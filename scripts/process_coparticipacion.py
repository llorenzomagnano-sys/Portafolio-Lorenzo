"""
Procesa y deflacta la serie de coparticipación federal por provincia (Núcleo 1).

Alcance definido tras evaluar la disponibilidad real de datos (ver
docs/methodology.md): **2016-2025 únicamente**. El archivo fuente de RON cubre
2003-2025, pero el IPC nacional oficial confiable solo cubre desde diciembre de
2016 -- no se encontró una fuente de inflación creíble para 2014-2015 (las
series alternativas evaluadas mostraban un empalme roto en ese tramo, con el
índice bajando de un año a otro pese a la inflación real). En vez de inventar
un supuesto para tapar ese hueco, se acotó el alcance temporal.

Definición de "coparticipación" usada acá (decisión documentada, no es la única
posible): suma de los conceptos que Hacienda reporta bajo
  - "coparticipacion federal de impuestos ley 23548", o
  - "coparticipacion federal de impuestos neta ley 26075"
  (mutuamente excluyentes según el año -- se coalescen como el mismo concepto)
más
  - "consenso fiscal ley 27429 compensacion" (desde 2018)

Entradas:
  - data/raw/coparticipacion/serie_ron_2003_2025.csv
  - data/raw/ipc/serie_ipc_divisiones.csv

Salida:
  - data/processed/coparticipacion_real.csv
    columnas: provincia, anio, monto_nominal, ipc_promedio_anual, monto_real_base2016
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RON_PATH = BASE_DIR / "data" / "raw" / "coparticipacion" / "serie_ron_2003_2025.csv"
IPC_PATH = BASE_DIR / "data" / "raw" / "ipc" / "serie_ipc_divisiones.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "coparticipacion_real.csv"

SCOPE_START_YEAR = 2016
SCOPE_END_YEAR = 2025
BASE_YEAR = 2016  # serie real en pesos constantes, base = promedio del año 2016

CONCEPTOS_COPARTICIPACION = {
    "coparticipacion federal de impuestos ley 23548",
    "coparticipacion federal de impuestos neta ley 26075",
    "consenso fiscal ley 27429 compensacion",
}

RECIPIENTES_NO_PROVINCIALES = {
    "fdo.compensador",
    "fondo a.t.n.",
    "seguridad social",
    "tesoro nacional",
}

# Normalización de nombres tal como aparecen en el CSV fuente -> nombre canónico.
PROVINCIA_CANONICA = {
    "buenos aires": "Buenos Aires",
    "c.a.b.a": "CABA",
    "catamarca": "Catamarca",
    "chaco": "Chaco",
    "chubut": "Chubut",
    "cordoba": "Córdoba",
    "corrientes": "Corrientes",
    "entre rios": "Entre Ríos",
    "formosa": "Formosa",
    "jujuy": "Jujuy",
    "la pampa": "La Pampa",
    "la rioja": "La Rioja",
    "mendoza": "Mendoza",
    "misiones": "Misiones",
    "neuquen": "Neuquén",
    "rio negro": "Río Negro",
    "salta": "Salta",
    "san juan": "San Juan",
    "san luis": "San Luis",
    "santa cruz": "Santa Cruz",
    "santa fe": "Santa Fe",
    "sgo. del estero": "Santiago del Estero",
    "tierra del fuego": "Tierra del Fuego",
    "tucuman": "Tucumán",
}


def load_ron_nominal() -> pd.DataFrame:
    df = pd.read_csv(RON_PATH, sep=";", encoding="latin-1")
    df.columns = [c.strip().lower() for c in df.columns]
    df["monto"] = df["monto"].astype(str).str.replace(",", ".", regex=False).astype(float)
    df["provincia"] = df["provincia"].str.strip().str.lower()
    df["impuesto"] = df["impuesto"].str.strip().str.lower()

    df = df[(df["ano"] >= SCOPE_START_YEAR) & (df["ano"] <= SCOPE_END_YEAR)]
    df = df[~df["provincia"].isin(RECIPIENTES_NO_PROVINCIALES)]
    df = df[df["impuesto"].isin(CONCEPTOS_COPARTICIPACION)]

    provincias_sin_mapear = set(df["provincia"]) - set(PROVINCIA_CANONICA)
    if provincias_sin_mapear:
        raise SystemExit(
            f"Provincias sin mapeo a nombre canónico: {sorted(provincias_sin_mapear)}. "
            "Agregar al diccionario PROVINCIA_CANONICA antes de continuar -- no se "
            "descartan silenciosamente."
        )
    df["provincia"] = df["provincia"].map(PROVINCIA_CANONICA)

    nominal = df.groupby(["provincia", "ano"], as_index=False)["monto"].sum()
    nominal = nominal.rename(columns={"ano": "anio", "monto": "monto_nominal"})

    provincias_esperadas = set(PROVINCIA_CANONICA.values())
    anios_esperados = set(range(SCOPE_START_YEAR, SCOPE_END_YEAR + 1))
    combinaciones_esperadas = {(p, a) for p in provincias_esperadas for a in anios_esperados}
    combinaciones_presentes = set(zip(nominal["provincia"], nominal["anio"]))
    faltantes = combinaciones_esperadas - combinaciones_presentes
    if faltantes:
        print(
            f"AVISO: faltan {len(faltantes)} combinaciones provincia-año en la fuente "
            "(no se completan con supuestos, quedan ausentes en la salida):"
        )
        for provincia, anio in sorted(faltantes):
            print(f"  - {provincia}, {anio}")

    return nominal


def load_ipc_promedio_anual() -> pd.DataFrame:
    df = pd.read_csv(IPC_PATH, sep=";", encoding="latin-1")
    df.columns = [c.strip() for c in df.columns]

    nivel_general = df[
        (df["Region"].str.strip().str.lower() == "nacional")
        & (df["Descripcion"].str.strip().str.lower() == "nivel general")
    ].copy()
    nivel_general["Indice_IPC"] = (
        nivel_general["Indice_IPC"].astype(str).str.replace(",", ".", regex=False).astype(float)
    )
    if nivel_general.empty:
        raise SystemExit(
            "No se encontraron filas con Region='Nacional' y Descripcion='NIVEL GENERAL' "
            f"en {IPC_PATH}. Revisar manualmente los valores reales de esas columnas."
        )

    nivel_general["anio"] = nivel_general["Periodo"].astype(str).str[:4].astype(int)
    nivel_general = nivel_general[
        (nivel_general["anio"] >= SCOPE_START_YEAR) & (nivel_general["anio"] <= SCOPE_END_YEAR)
    ]

    meses_por_anio = nivel_general.groupby("anio")["Periodo"].count()
    for anio, meses in meses_por_anio.items():
        if meses < 12:
            print(
                f"AVISO: el año {anio} tiene solo {meses} mes(es) de IPC disponibles "
                "(promedio calculado igual, documentado en methodology.md)."
            )

    promedio = nivel_general.groupby("anio", as_index=False)["Indice_IPC"].mean()
    promedio = promedio.rename(columns={"Indice_IPC": "ipc_promedio_anual"})
    return promedio


def main() -> None:
    nominal = load_ron_nominal()
    ipc = load_ipc_promedio_anual()

    if BASE_YEAR not in set(ipc["anio"]):
        raise SystemExit(f"No hay IPC disponible para el año base {BASE_YEAR}.")
    ipc_base = float(ipc.loc[ipc["anio"] == BASE_YEAR, "ipc_promedio_anual"].iloc[0])

    combinado = nominal.merge(ipc, on="anio", how="left")
    faltantes_ipc = combinado[combinado["ipc_promedio_anual"].isna()]
    if not faltantes_ipc.empty:
        anios_sin_ipc = sorted(faltantes_ipc["anio"].unique())
        print(f"AVISO: sin IPC para los años {anios_sin_ipc}; monto_real queda vacío para esos años.")

    combinado["monto_real_base2016"] = combinado["monto_nominal"] * (
        ipc_base / combinado["ipc_promedio_anual"]
    )

    combinado = combinado.sort_values(["provincia", "anio"]).reset_index(drop=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combinado.to_csv(OUTPUT_PATH, index=False)
    print(f"\nGuardado: {OUTPUT_PATH} ({len(combinado)} filas)")
    print(f"Base de la serie real: promedio {BASE_YEAR} = 100 (IPC_base = {ipc_base:.4f})")


if __name__ == "__main__":
    main()
