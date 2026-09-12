"""
Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba.

Cruza la coparticipación nominal de Córdoba (Núcleo 1) con una proxy de sus ingresos
corrientes totales (archivo de recaudación provincial, ver más abajo), calcula el ratio
coparticipación / ingresos totales por año, y usa el simulador del Núcleo 3 para
traducir un shock de recaudación coparticipable en un impacto sobre el ingreso
provincial total.

DEFINICIÓN DE "INGRESOS CORRIENTES TOTALES" USADA ACÁ (decisión documentada, confirmada
con el usuario -- no es la única posible):

Se usa la fila "Total" de `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`
(hoja "Serie_Mensual"): Recursos de Origen Provincial + Recursos de Origen Nacional,
administrados por la Dirección General de Rentas de Córdoba. Esto **excluye** lo
recaudado por otros organismos públicos provinciales (p. ej., EPEC), según la propia
nota al pie del archivo fuente -- por lo tanto NO es el ingreso corriente total del
sector público provincial en sentido estricto de ejecución presupuestaria, sino la
mejor proxy disponible. Ver docs/methodology.md para el detalle completo.

UNIDADES: el archivo fuente rotula sus valores como "millones de pesos corrientes",
pero son en realidad PESOS corrientes (verificado cruzando la fila de coparticipación
del archivo contra el Núcleo 1 -- ver docs/methodology.md).

NUMERADOR: se usa `monto_nominal` (no `monto_real_base2016`) de
`data/processed/coparticipacion_real.csv` para Córdoba. El ratio "% de los ingresos que
es coparticipación" debe calcularse con magnitudes del mismo tipo (nominal sobre
nominal) -- usar la serie deflactada en el numerador contra un denominador nominal
distorsionaría el ratio sin ningún motivo válido.

ALCANCE: 2015-2025 (11 años), intersección entre lo que cubre el archivo de recaudación
provincial (desde ene-2015) y el Núcleo 1 (hasta 2025). 2026 queda afuera del ratio
anual por ser un año calendario incompleto en ambas fuentes.

Entradas:
  - data/processed/coparticipacion_real.csv (Núcleo 1)
  - data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx (hoja Serie_Mensual)

Salida:
  - data/processed/dependencia_fiscal_cordoba.csv
    columnas: anio, coparticipacion_nominal_pesos, ingresos_totales_pesos,
    ratio_coparticipacion_ingresos
"""
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from coeficientes_ley23548 import COEFICIENTES_COPARTICIPACION  # noqa: E402
from simulator import simular_shock  # noqa: E402

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


def load_ingresos_totales_anuales() -> pd.DataFrame:
    """Suma la fila "Total" de Serie_Mensual a nivel de año calendario completo."""
    raw = pd.read_excel(INGRESOS_PATH, sheet_name="Serie_Mensual", header=None)

    fila_total = raw[raw[1].astype(str).str.strip() == "Total"].index
    if len(fila_total) != 1:
        raise SystemExit(
            f"Se esperaba una única fila 'Total' en Serie_Mensual, se encontraron "
            f"{len(fila_total)}. Revisar manualmente el archivo."
        )
    fila_total = int(fila_total[0])

    fila_fechas = 2  # fila 3 de la hoja (0-indexed = 2)
    columnas_datos = [c for c in raw.columns if c >= 2]

    montos_por_anio = {}
    meses_por_anio = {}
    for c in columnas_datos:
        fecha_cruda = raw.iat[fila_fechas, c]
        if fecha_cruda is None:
            continue
        anio, _mes = _parse_fecha_columna(fecha_cruda)
        monto = raw.iat[fila_total, c]
        if monto is None:
            continue
        montos_por_anio[anio] = montos_por_anio.get(anio, 0.0) + float(monto)
        meses_por_anio[anio] = meses_por_anio.get(anio, 0) + 1

    anios_incompletos = [a for a, m in meses_por_anio.items() if m < 12]
    if anios_incompletos:
        print(
            f"AVISO: años con menos de 12 meses de datos (se descartan del ratio anual, "
            f"no se completan con supuestos): {sorted(anios_incompletos)}"
        )

    filas = [
        {"anio": anio, "ingresos_totales_pesos": monto}
        for anio, monto in montos_por_anio.items()
        if meses_por_anio[anio] == 12
    ]
    return pd.DataFrame(filas).sort_values("anio").reset_index(drop=True)


def build_ratio() -> pd.DataFrame:
    copart = pd.read_csv(COPART_PATH)
    copart_cordoba = copart[copart["provincia"] == "Córdoba"][["anio", "monto_nominal"]].copy()
    copart_cordoba["coparticipacion_nominal_pesos"] = copart_cordoba["monto_nominal"] * 1e6
    copart_cordoba = copart_cordoba.drop(columns=["monto_nominal"])

    ingresos = load_ingresos_totales_anuales()

    combinado = copart_cordoba.merge(ingresos, on="anio", how="inner")
    combinado = combinado[
        (combinado["anio"] >= SCOPE_START_YEAR) & (combinado["anio"] <= SCOPE_END_YEAR)
    ]

    anios_esperados = set(range(SCOPE_START_YEAR, SCOPE_END_YEAR + 1))
    anios_presentes = set(combinado["anio"])
    faltantes = anios_esperados - anios_presentes
    if faltantes:
        print(
            f"AVISO: faltan {len(faltantes)} años en el cruce 2015-2025 (no se completan "
            f"con supuestos, quedan ausentes en la salida): {sorted(faltantes)}"
        )

    combinado["ratio_coparticipacion_ingresos"] = (
        combinado["coparticipacion_nominal_pesos"] / combinado["ingresos_totales_pesos"]
    )
    return combinado.sort_values("anio").reset_index(drop=True)


def calcular_sensibilidad(anio_referencia: int, escenarios: list[float]) -> pd.DataFrame:
    """Traduce shocks de recaudación coparticipable (Núcleo 3) en impacto % sobre el
    ingreso provincial total de Córdoba, usando el año de referencia indicado.

    La masa coparticipable base se estima igual que en el Núcleo 3 (notebook de
    validación IARAF): "gross-up" de la coparticipación nominal efectivamente recibida
    por las 24 jurisdicciones en `anio_referencia`, dividiendo por la suma de sus 24
    coeficientes (porque esos coeficientes representan solo la porción de la masa total
    que va a las provincias, el resto es Nación + Fondo ATN).
    """
    copart = pd.read_csv(COPART_PATH)
    total_recibido_provincias = copart[copart["anio"] == anio_referencia]["monto_nominal"].sum() * 1e6
    suma_coeficientes = sum(COEFICIENTES_COPARTICIPACION.values())
    recaudacion_base = total_recibido_provincias / suma_coeficientes

    ratio_df = build_ratio()
    ingresos_totales_referencia = float(
        ratio_df.loc[ratio_df["anio"] == anio_referencia, "ingresos_totales_pesos"].iloc[0]
    )

    filas = []
    for variacion in escenarios:
        resultado = simular_shock(variacion, recaudacion_base, COEFICIENTES_COPARTICIPACION)
        impacto_cordoba = next(
            p["impacto_pesos"] for p in resultado["por_provincia"] if p["provincia"] == "Córdoba"
        )
        impacto_pct_ingresos_totales = impacto_cordoba / ingresos_totales_referencia
        filas.append(
            {
                "variacion_pct_recaudacion": variacion,
                "impacto_copart_cordoba_pesos": impacto_cordoba,
                "impacto_pct_ingresos_totales_cordoba": impacto_pct_ingresos_totales,
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
