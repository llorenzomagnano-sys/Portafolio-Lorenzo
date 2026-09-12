"""
Procesa y deflacta la serie de coparticipación federal por provincia (Núcleo 1).

Alcance: **2003-2025**. El archivo fuente de RON (montos nominales por provincia)
solo cubre desde 2003 -- no hay fuente de montos nominales de coparticipación
para 1990-2002 (se buscó explícitamente y el usuario confirmó no tenerla), así
que la serie en pesos no puede arrancar antes de 2003 aunque el índice de
precios sí podría reconstruirse más atrás.

El IPC nacional oficial confiable (serie_ipc_divisiones.csv) solo cubre desde
diciembre de 2016. Para 2007-2015 el IPC oficial de la época está ampliamente
desacreditado (intervención del INDEC, ver docs/methodology.md). Para llegar a
2003 con un deflactor confiable se empalma un IPC de tres tramos, usando la
base de Fundación Norte y Sur / Orlando Ferreres para 2003-2015:
  - 2003-2006: tabla "GBA (INDEC)" del archivo Ferreres (tramo pre-intervención,
    confiable).
  - 2007-2015: tabla "GBA (estimaciones privadas)" del mismo archivo (sustituye
    al IPC oficial desacreditado de ese tramo).
  - 2016-2025: IPC oficial nacional ya usado (serie_ipc_divisiones.csv), sin
    modificar.
El empalme se ancla exactamente al valor ya publicado de 2016 (ver
load_ipc_empalmado() y docs/methodology.md para el detalle y las tasas usadas).

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
  - data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx

Salida:
  - data/processed/coparticipacion_real.csv
    columnas: provincia, anio, monto_nominal, ipc_promedio_anual, monto_real_base2016
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RON_PATH = BASE_DIR / "data" / "raw" / "coparticipacion" / "serie_ron_2003_2025.csv"
IPC_PATH = BASE_DIR / "data" / "raw" / "ipc" / "serie_ipc_divisiones.csv"
IPC_FERRERES_PATH = BASE_DIR / "data" / "raw" / "ipc" / "fundacion_norte_y_sur_orlando_ferreres.xlsx"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "coparticipacion_real.csv"

SCOPE_START_YEAR = 2003
SCOPE_END_YEAR = 2025
BASE_YEAR = 2016  # serie real en pesos constantes, base = promedio del año 2016

# Hoja del archivo Ferreres que contiene las tasas de variación anual (var. %
# anual) usadas para el empalme. Se leen directamente tal como están en la
# fuente (no se recalculan a partir de los niveles, para no introducir
# redondeos distintos a los de la fuente).
IPC_FERRERES_SHEET = "IPC "

# Años cuya variación % anual se toma de cada tabla del archivo Ferreres:
#   - tabla A ("GBA (INDEC)"): tramo 2004-2006, pre-intervención, confiable.
#     Se usa para encadenar hacia atrás desde 2006 hasta 2003.
#   - tabla B ("GBA (estimaciones privadas)"): tramo 2007-2016. Se usa para
#     encadenar hacia atrás desde el valor de 2016 ya publicado hasta 2006,
#     porque para 2007-2015 el IPC oficial de la época está desacreditado
#     (ver docs/methodology.md). El año 2016 se incluye solo para anclar el
#     empalme al dato ya existente, no se usa como valor final de 2016.
IPC_FERRERES_ANIOS_TABLA_A = [2004, 2005, 2006]
IPC_FERRERES_ANIOS_TABLA_B = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]

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


def _parse_anio_ferreres(valor) -> int | None:
    """Convierte 'Año' de la hoja Ferreres a int, tolerando el asterisco usado
    en algunas filas (p. ej. '2015*') para marcar años ajustados por la fuente."""
    if valor is None:
        return None
    texto = str(valor).strip().rstrip("*")
    try:
        return int(float(texto))
    except ValueError:
        return None


def load_ipc_ferreres_var_pct() -> tuple[dict, dict]:
    """Lee la hoja "IPC " del archivo Ferreres y devuelve (var_tabla_a,
    var_tabla_b): año -> variación % anual, una por cada una de las dos tablas
    anuales de esa hoja (columna A = Año, columna C = var. % anual del
    promedio)."""
    raw = pd.read_excel(IPC_FERRERES_PATH, sheet_name=IPC_FERRERES_SHEET, header=None)

    filas_tabla_a = raw[raw[1].astype(str).str.contains("GBA \\(INDEC\\)", na=False)].index
    filas_tabla_b = raw[raw[1].astype(str).str.contains("estimaciones privadas", na=False)].index
    if len(filas_tabla_a) != 1 or len(filas_tabla_b) != 1:
        raise SystemExit(
            "No se encontraron (o se encontró más de una vez) los encabezados "
            "'GBA (INDEC)' / 'estimaciones privadas' en la hoja "
            f"'{IPC_FERRERES_SHEET}' de {IPC_FERRERES_PATH}. Revisar manualmente."
        )
    inicio_a, inicio_b = int(filas_tabla_a[0]), int(filas_tabla_b[0])

    def parse_tabla(fila_inicio: int, fila_fin: int) -> dict:
        var_por_anio = {}
        for i in range(fila_inicio, fila_fin):
            anio = _parse_anio_ferreres(raw.iat[i, 0])
            var = raw.iat[i, 2]
            if anio is not None and isinstance(var, (int, float)):
                var_por_anio[anio] = float(var)
        return var_por_anio

    var_tabla_a = parse_tabla(inicio_a + 2, inicio_b)
    var_tabla_b = parse_tabla(inicio_b + 2, len(raw))
    return var_tabla_a, var_tabla_b


def load_ipc_empalmado() -> pd.DataFrame:
    """Construye ipc_promedio_anual para 2003-2025 empalmando tres fuentes
    (ver docstring del módulo y docs/methodology.md):
      - 2016-2025: IPC oficial nacional ya usado (sin modificar).
      - 2007-2015: encadenado hacia atrás desde el valor de 2016 usando las
        tasas de la tabla "estimaciones privadas" de Ferreres.
      - 2003-2006: encadenado hacia atrás desde el valor resultante de 2006
        usando las tasas de la tabla "GBA (INDEC)" de Ferreres.
    El empalme queda anclado exactamente al valor de 2016 ya publicado; no se
    recalculan ni modifican los años 2016-2025.
    """
    ipc_oficial = load_ipc_promedio_anual()
    if 2016 not in set(ipc_oficial["anio"]):
        raise SystemExit("No hay IPC oficial para 2016; no se puede anclar el empalme.")
    nivel = {2016: float(ipc_oficial.loc[ipc_oficial["anio"] == 2016, "ipc_promedio_anual"].iloc[0])}

    var_tabla_a, var_tabla_b = load_ipc_ferreres_var_pct()

    faltantes_b = [a for a in IPC_FERRERES_ANIOS_TABLA_B if a not in var_tabla_b]
    faltantes_a = [a for a in IPC_FERRERES_ANIOS_TABLA_A if a not in var_tabla_a]
    if faltantes_b or faltantes_a:
        raise SystemExit(
            f"Faltan tasas de variación anual en el archivo Ferreres: tabla A {faltantes_a}, "
            f"tabla B {faltantes_b}. No se completan con supuestos."
        )

    for anio in sorted(IPC_FERRERES_ANIOS_TABLA_B, reverse=True):
        nivel[anio - 1] = nivel[anio] / (1 + var_tabla_b[anio])
    for anio in sorted(IPC_FERRERES_ANIOS_TABLA_A, reverse=True):
        nivel[anio - 1] = nivel[anio] / (1 + var_tabla_a[anio])

    empalmado = pd.DataFrame(
        {"anio": list(nivel.keys()), "ipc_promedio_anual": list(nivel.values())}
    )
    empalmado = empalmado[
        (empalmado["anio"] >= SCOPE_START_YEAR) & (empalmado["anio"] < 2016)
    ]
    return pd.concat([empalmado, ipc_oficial], ignore_index=True).sort_values("anio")


def main() -> None:
    nominal = load_ron_nominal()
    ipc = load_ipc_empalmado()

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
