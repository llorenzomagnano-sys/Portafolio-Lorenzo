"""Chequeos de consistencia del procesamiento de datos (Núcleos 1, 2 y 4).

Leen los datos versionados en data/raw/ y data/processed/. Correr con:
    pytest scripts/test_procesamiento.py
"""
import pandas as pd
import pytest

from build_coefficients_comparison import OUTPUT_PATH as APORTE_PATH
from build_dependencia_fiscal import build_ratio, calcular_sensibilidad
from process_coparticipacion import (
    OUTPUT_PATH as COPART_PATH,
    load_ipc_empalmado,
    load_ipc_ferreres_var_pct,
    load_ipc_promedio_anual,
)


@pytest.fixture(scope="module")
def ipc():
    return load_ipc_empalmado().set_index("anio")["ipc_promedio_anual"]


@pytest.fixture(scope="module")
def dependencia():
    return build_ratio().set_index("anio")


def test_ipc_cubre_2003_2025_y_crece_todos_los_anios(ipc):
    assert list(ipc.index) == list(range(2003, 2026))
    assert (ipc.diff().dropna() > 0).all()


def test_ipc_2016_es_un_promedio_y_no_el_valor_de_diciembre(ipc):
    # El IPC oficial solo trae diciembre de 2016; usarlo como promedio sesga ~10%.
    diciembre_2016 = load_ipc_promedio_anual().set_index("anio").loc[2016, "ipc_promedio_anual"]
    assert ipc[2016] < diciembre_2016 * 0.95


def test_ipc_2016_reproduce_la_variacion_2017_de_la_fuente(ipc):
    _, var_tabla_b = load_ipc_ferreres_var_pct()
    assert ipc[2017] / ipc[2016] - 1 == pytest.approx(var_tabla_b[2017])


def test_serie_de_coparticipacion_tiene_24_jurisdicciones_por_23_anios():
    df = pd.read_csv(COPART_PATH)
    assert len(df) == 24 * 23
    assert df["monto_real_base2016"].notna().all()


def test_aporte_vs_recibo_compara_participaciones_que_suman_uno():
    df = pd.read_csv(APORTE_PATH)
    assert df["pct_coparticipacion_entre_provincias"].sum() == pytest.approx(1.0)
    # El PBG trae además una fila "No distribuido", por eso no suma exactamente 1.
    assert df["pct_pbg_aporte"].sum() == pytest.approx(1.0, abs=0.01)


def test_ratio_de_dependencia_usa_partes_del_mismo_total(dependencia):
    d = dependencia
    assert ((d["ratio_coparticipacion_ingresos"] > 0) & (d["ratio_coparticipacion_ingresos"] < 1)).all()
    assert (d["coparticipacion_pesos"] + d["recursos_propios_pesos"] <= d["ingresos_totales_pesos"]).all()


def test_archivo_provincial_esta_en_pesos_y_coincide_con_nacion_en_2015_2017(dependencia):
    # Si el archivo estuviera en millones, la diferencia sería de seis órdenes de magnitud.
    diferencias = dependencia.loc[2015:2017, "diferencia_ron_vs_provincia"]
    assert (diferencias.abs() < 0.01).all()


def test_sensibilidad_es_el_shock_por_el_ratio_de_dependencia(dependencia):
    sens = calcular_sensibilidad(2025, [-0.10]).iloc[0]
    esperado = -0.10 * dependencia.loc[2025, "ratio_coparticipacion_ingresos"]
    assert sens["impacto_pct_ingresos_totales_cordoba"] == pytest.approx(esperado)
