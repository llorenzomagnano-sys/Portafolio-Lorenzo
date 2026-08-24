"""
Núcleo 2 — Compara, para cada provincia, cuánto "aporta" (proxy: % de su PBG sobre el
PBG total del país) contra cuánto "recibe" (% de la masa coparticipable total según el
coeficiente de distribución de la Ley 23.548).

IMPORTANTE (ver docs/methodology.md para el detalle completo):
- Los coeficientes de coparticipación son los de la Ley 23.548 (1988), tal como figuran
  en data/raw/coeficientes/indices_copa_2018.pdf, con UN solo ajuste manual: el valor de
  CABA se reemplazó por 1,4% (vigente desde 2020), en vez del 3,75% que tenía ese
  documento de 2018.
- Esos 24 coeficientes NO se renormalizan para sumar 1 -- se usan tal cual, como
  fracción de la masa coparticipable TOTAL (que incluye lo que retiene la Nación y el
  Fondo ATN). El % de PBG también es una fracción de un total nacional (el PBG país).
  Ambas columnas son fracciones de "totales nacionales" distintos, no partes de un
  mismo pastel -- la comparación es de orden de magnitud, no una relación exacta 1 a 1.
- El PBG usado es el de 2024 (el año más reciente disponible en la fuente), marcado
  como dato preliminar en el archivo original.
- Esto usa el PBG como PROXY del aporte tributario real -- tiene una limitación
  metodológica conocida y documentada: las grandes empresas suelen tributar donde
  tienen sede fiscal (muchas veces CABA), no necesariamente donde generan la actividad
  económica. Ver la sección de limitaciones en el notebook y en methodology.md.
"""
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
from coeficientes_ley23548 import COEFICIENTES_COPARTICIPACION  # noqa: E402

PBG_PATH = BASE_DIR / "data" / "raw" / "pbg" / "Jurisdiccion_52sectores.xlsx"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "aporte_vs_recibo.csv"

PBG_YEAR = 2024

# Nombres tal como aparecen en la hoja VABpb -> nombre canónico usado en el proyecto.
PROVINCIA_CANONICA = {
    "Ciudad de Buenos Aires": "CABA",
    "Buenos Aires": "Buenos Aires",
    "Catamarca": "Catamarca",
    "Córdoba": "Córdoba",
    "Corrientes": "Corrientes",
    "Chaco": "Chaco",
    "Chubut": "Chubut",
    "Entre Ríos": "Entre Ríos",
    "Formosa": "Formosa",
    "Jujuy": "Jujuy",
    "La Pampa": "La Pampa",
    "La Rioja": "La Rioja",
    "Mendoza": "Mendoza",
    "Misiones": "Misiones",
    "Neuquén": "Neuquén",
    "Río Negro": "Río Negro",
    "Salta": "Salta",
    "San Juan": "San Juan",
    "San Luis": "San Luis",
    "Santa Cruz": "Santa Cruz",
    "Santa Fe": "Santa Fe",
    "Santiago del Estero": "Santiago del Estero",
    "Tucumán": "Tucumán",
    "Tierra del Fuego": "Tierra del Fuego",
}


def load_pbg_pct(year: int) -> pd.DataFrame:
    raw = pd.read_excel(PBG_PATH, sheet_name="VABpb", header=None)

    header_row = raw[raw[1] == "JURISDICCIÓN"].index[0]
    years_row = raw.iloc[header_row]
    year_columns = {}
    for col in raw.columns[2:]:
        value = years_row[col]
        if pd.isna(value):
            continue
        year_int = int(str(value).split()[0].split(".")[0])
        year_columns[year_int] = col

    if year not in year_columns:
        raise SystemExit(f"No se encontró la columna del año {year} en {PBG_PATH}.")
    col = year_columns[year]

    data = raw.iloc[header_row + 1 :, [1, col]].copy()
    data.columns = ["jurisdiccion", "pbg"]
    data = data.dropna(subset=["jurisdiccion"])
    data["jurisdiccion"] = data["jurisdiccion"].astype(str).str.strip()

    total_row = data[data["jurisdiccion"] == "Total"]
    if total_row.empty:
        raise SystemExit(f"No se encontró la fila 'Total' en {PBG_PATH}.")
    total_pbg = float(total_row["pbg"].iloc[0])

    data = data[data["jurisdiccion"].isin(PROVINCIA_CANONICA)]
    provincias_sin_mapear = set(data["jurisdiccion"]) - set(PROVINCIA_CANONICA)
    if provincias_sin_mapear:
        raise SystemExit(f"Jurisdicciones sin mapeo: {sorted(provincias_sin_mapear)}")

    data["provincia"] = data["jurisdiccion"].map(PROVINCIA_CANONICA)
    data["pct_pbg_aporte"] = data["pbg"].astype(float) / total_pbg

    return data[["provincia", "pct_pbg_aporte"]]


def main() -> None:
    pbg = load_pbg_pct(PBG_YEAR)

    coef = pd.DataFrame(
        {
            "provincia": list(COEFICIENTES_COPARTICIPACION.keys()),
            "pct_coparticipacion_recibe": list(COEFICIENTES_COPARTICIPACION.values()),
        }
    )

    combinado = pbg.merge(coef, on="provincia", how="outer", indicator=True)
    solo_un_lado = combinado[combinado["_merge"] != "both"]
    if not solo_un_lado.empty:
        raise SystemExit(
            "Hay provincias que aparecen en una fuente pero no en la otra -- revisar "
            f"mapeo de nombres antes de continuar:\n{solo_un_lado}"
        )
    combinado = combinado.drop(columns="_merge")

    combinado["diferencia_pp"] = (
        combinado["pct_coparticipacion_recibe"] - combinado["pct_pbg_aporte"]
    ) * 100

    combinado = combinado.sort_values("diferencia_pp", ascending=False).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combinado.to_csv(OUTPUT_PATH, index=False)
    print(f"Guardado: {OUTPUT_PATH} ({len(combinado)} filas)")
    print(f"PBG usado: año {PBG_YEAR}")
    print("\nCórdoba:")
    print(combinado[combinado["provincia"] == "Córdoba"].to_string(index=False))


if __name__ == "__main__":
    main()
