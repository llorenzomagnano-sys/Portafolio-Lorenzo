"""
Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba.

Fuente única para el ratio: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`
(hoja "Serie_Mensual"), recaudación administrada por la Dirección General de Rentas de
Córdoba. Se leen tres filas por su código:

  - `1`     Total (Recursos de Origen Provincial + Recursos de Origen Nacional). Es la
            proxy de "ingresos corrientes totales": excluye lo recaudado por otros
            organismos provinciales (p. ej., EPEC), según la nota al pie del archivo.
  - `1.1`   Recursos de Origen Provincial (recaudación propia).
  - `1.2.1` Coparticipación Federal de Impuestos: Ley 23.548 + compensación del
            Consenso Fiscal (Ley 27.429) + bono Consenso Fiscal.

RATIO (`ratio_coparticipacion_ingresos`) = fila 1.2.1 / fila 1: numerador y denominador
del mismo archivo, así el numerador es efectivamente parte del denominador. Da igual en
pesos nominales o reales (el deflactor se cancela).

CONTROL CONTRA LA SERIE NACIONAL: `coparticipacion_ron_pesos` es la coparticipación de
Córdoba según la serie RON de Hacienda (Núcleo 1) y `diferencia_ron_vs_provincia` su
diferencia relativa contra la fila 1.2.1. Coinciden en 2015-2017; desde 2018 la serie
nacional es entre 14% y 17% más alta. No identifiqué la causa (podría ser criterio de
registro o retenciones previas a la transferencia), así que no se usa para el ratio y se
deja visible como control.

COLUMNAS REALES (`*_real_base2016_pesos`): pesos constantes, base promedio 2016 = 100,
mismo IPC empalmado que el Núcleo 1 (`load_ipc_empalmado`):
`real = nominal × (ipc_2016 / ipc_año)`.

UNIDADES: el archivo rotula sus valores como "millones de pesos corrientes", pero están
en PESOS corrientes (la fila de coparticipación coincide en pesos con la serie RON en
2015-2017; ver docs/methodology.md).

ALCANCE: 2015-2025. El archivo arranca en enero de 2015; 2026 queda afuera por ser un
año incompleto.

Salida: data/processed/dependencia_fiscal_cordoba.csv
"""
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from coeficientes_ley23548 import COEFICIENTES_COPARTICIPACION  # noqa: E402
from simulator import simular_shock  # noqa: E402
from process_coparticipacion import load_ipc_empalmado  # noqa: E402

COPART_PATH = BASE_DIR / "data" / "processed" / "coparticipacion_real.csv"
INGRESOS_PATH = BASE_DIR / "data" / "raw" / "ingresos_cordoba" / "serie_recaudacion_provincial.xlsx"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "dependencia_fiscal_cordoba.csv"

SCOPE_START_YEAR = 2015
SCOPE_END_YEAR = 2025

MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


def _parse_fecha_columna(valor):
    """Convierte el encabezado de una columna de Serie_Mensual a (año, mes).

    La mayoría de las columnas traen un datetime real, pero al menos una
    (diciembre de 2023) viene como texto ("dic-23") -- se tolera ese formato
    en vez de asumir que todas las columnas son consistentes.
    """
    if hasattr(valor, "year"):
        return valor.year, valor.month
    texto = str(valor).strip().lower()
    mes_str, anio_str = texto.split("-")
    return 2000 + int(anio_str), MESES[mes_str]


FILAS_DGR = {
    "ingresos_totales_pesos": "1",
    "recursos_propios_pesos": "1.1",
    "coparticipacion_pesos": "1.2.1",
}


def load_series_dgr_anuales() -> pd.DataFrame:
    """Suma por año calendario completo las filas de FILAS_DGR de Serie_Mensual."""
    raw = pd.read_excel(INGRESOS_PATH, sheet_name="Serie_Mensual", header=None)
    codigos = raw[0].astype(str).str.strip()

    fila_fechas = 2  # fila 3 de la hoja
    columnas_datos = [c for c in raw.columns if c >= 2]

    series = {}
    meses_por_anio = {}
    for columna_salida, codigo in FILAS_DGR.items():
        filas = codigos[codigos == codigo].index
        if len(filas) != 1:
            raise SystemExit(
                f"Se esperaba una única fila con código {codigo} en Serie_Mensual, se "
                f"encontraron {len(filas)}. Revisar manualmente el archivo."
            )
        fila = int(filas[0])

        montos = {}
        meses = {}
        for c in columnas_datos:
            fecha_cruda = raw.iat[fila_fechas, c]
            if pd.isna(fecha_cruda):
                continue
            anio, _mes = _parse_fecha_columna(fecha_cruda)
            monto = raw.iat[fila, c]
            if pd.isna(monto):
                monto = 0.0
            montos[anio] = montos.get(anio, 0.0) + float(monto)
            meses[anio] = meses.get(anio, 0) + 1
        series[columna_salida] = montos
        meses_por_anio = meses

    anios_incompletos = sorted(a for a, m in meses_por_anio.items() if m < 12)
    if anios_incompletos:
        print(
            f"AVISO: años con menos de 12 meses de datos (se descartan, no se completan "
            f"con supuestos): {anios_incompletos}"
        )

    df = pd.DataFrame(series)
    df.index.name = "anio"
    df = df.reset_index()
    df = df[df["anio"].map(meses_por_anio) == 12]
    return df.sort_values("anio").reset_index(drop=True)


def build_ratio() -> pd.DataFrame:
    df = load_series_dgr_anuales()
    df = df[(df["anio"] >= SCOPE_START_YEAR) & (df["anio"] <= SCOPE_END_YEAR)].copy()

    faltantes = set(range(SCOPE_START_YEAR, SCOPE_END_YEAR + 1)) - set(df["anio"])
    if faltantes:
        print(
            f"AVISO: faltan {len(faltantes)} años en 2015-2025 (quedan ausentes en la "
            f"salida): {sorted(faltantes)}"
        )

    df["ratio_coparticipacion_ingresos"] = df["coparticipacion_pesos"] / df["ingresos_totales_pesos"]
    df["participacion_recursos_propios"] = df["recursos_propios_pesos"] / df["ingresos_totales_pesos"]

    ipc = load_ipc_empalmado()
    ipc_2016 = float(ipc.loc[ipc["anio"] == 2016, "ipc_promedio_anual"].iloc[0])
    df = df.merge(ipc, on="anio", how="left")
    if df["ipc_promedio_anual"].isna().any():
        raise SystemExit("Falta IPC para algún año del alcance; no se deflacta con supuestos.")
    for col in ["ingresos_totales_pesos", "recursos_propios_pesos", "coparticipacion_pesos"]:
        df[col.replace("_pesos", "_real_base2016_pesos")] = df[col] * ipc_2016 / df["ipc_promedio_anual"]
    df = df.drop(columns=["ipc_promedio_anual"])

    copart_ron = pd.read_csv(COPART_PATH)
    copart_ron = copart_ron[copart_ron["provincia"] == "Córdoba"][["anio", "monto_nominal"]]
    copart_ron["coparticipacion_ron_pesos"] = copart_ron["monto_nominal"] * 1e6
    df = df.merge(copart_ron.drop(columns="monto_nominal"), on="anio", how="left")
    df["diferencia_ron_vs_provincia"] = df["coparticipacion_ron_pesos"] / df["coparticipacion_pesos"] - 1

    return df.sort_values("anio").reset_index(drop=True)


def base_calibrada_cordoba(anio_referencia: int) -> tuple[float, float, float]:
    """Masa coparticipable total implícita, coparticipación e ingresos totales de Córdoba.

    La masa se calibra para que el coeficiente de Córdoba aplicado sobre ella reproduzca
    exactamente la coparticipación que registra el archivo provincial en
    `anio_referencia`. Así, el impacto en pesos que devuelve `simular_shock` y el
    denominador (ingresos totales) salen de la misma fuente.
    """
    ratio_df = build_ratio()
    fila = ratio_df.loc[ratio_df["anio"] == anio_referencia].iloc[0]
    coparticipacion = float(fila["coparticipacion_pesos"])
    ingresos_totales = float(fila["ingresos_totales_pesos"])
    recaudacion_base = coparticipacion / COEFICIENTES_COPARTICIPACION["Córdoba"]
    return recaudacion_base, coparticipacion, ingresos_totales


def calcular_sensibilidad(anio_referencia: int, escenarios: list[float]) -> pd.DataFrame:
    """Traduce shocks de recaudación coparticipable (Núcleo 3) en impacto % sobre el
    ingreso provincial total de Córdoba en `anio_referencia`."""
    recaudacion_base, _copart, ingresos_totales = base_calibrada_cordoba(anio_referencia)

    filas = []
    for variacion in escenarios:
        resultado = simular_shock(variacion, recaudacion_base, COEFICIENTES_COPARTICIPACION)
        impacto_cordoba = next(
            p["impacto_pesos"] for p in resultado["por_provincia"] if p["provincia"] == "Córdoba"
        )
        filas.append(
            {
                "variacion_pct_recaudacion": variacion,
                "impacto_copart_cordoba_pesos": impacto_cordoba,
                "impacto_pct_ingresos_totales_cordoba": impacto_cordoba / ingresos_totales,
            }
        )
    return pd.DataFrame(filas)


def main() -> None:
    ratio_df = build_ratio()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ratio_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Guardado: {OUTPUT_PATH} ({len(ratio_df)} filas)")
    print(ratio_df.to_string(index=False))

    anio_referencia = int(ratio_df["anio"].max())
    print(f"\nSensibilidad, año de referencia {anio_referencia}:")
    sensibilidad = calcular_sensibilidad(anio_referencia, [-0.05, -0.10])
    print(sensibilidad.to_string(index=False))


if __name__ == "__main__":
    main()
