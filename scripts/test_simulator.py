"""Tests de scripts/simulator.py. Correr con: pytest scripts/test_simulator.py"""
import pytest

from simulator import simular_shock


def test_monto_total_afectado_es_base_por_variacion():
    resultado = simular_shock(-0.10, 1_000_000, {"Córdoba": 0.05})
    assert resultado["monto_total_afectado"] == pytest.approx(-100_000)


def test_impacto_por_provincia_es_proporcional_al_coeficiente():
    resultado = simular_shock(-0.10, 1_000_000, {"Córdoba": 0.05, "Buenos Aires": 0.12})
    impactos = {p["provincia"]: p["impacto_pesos"] for p in resultado["por_provincia"]}
    assert impactos["Córdoba"] == pytest.approx(-100_000 * 0.05)
    assert impactos["Buenos Aires"] == pytest.approx(-100_000 * 0.12)


def test_shock_positivo_da_impacto_positivo():
    resultado = simular_shock(0.10, 1_000_000, {"Córdoba": 0.05})
    assert resultado["monto_total_afectado"] > 0
    assert resultado["por_provincia"][0]["impacto_pesos"] > 0


def test_shock_cero_no_tiene_impacto():
    resultado = simular_shock(0.0, 1_000_000, {"Córdoba": 0.05, "Buenos Aires": 0.12})
    assert resultado["monto_total_afectado"] == 0
    assert all(p["impacto_pesos"] == 0 for p in resultado["por_provincia"])


def test_total_impacto_provincias_es_suma_de_impactos_individuales():
    coef = {"Córdoba": 0.05, "Buenos Aires": 0.12, "Santa Fe": 0.05}
    resultado = simular_shock(-0.15, 2_000_000, coef)
    suma_manual = sum(p["impacto_pesos"] for p in resultado["por_provincia"])
    assert resultado["total_impacto_provincias"] == pytest.approx(suma_manual)


def test_recaudacion_base_no_positiva_lanza_error():
    with pytest.raises(ValueError):
        simular_shock(-0.10, 0, {"Córdoba": 0.05})
    with pytest.raises(ValueError):
        simular_shock(-0.10, -1_000_000, {"Córdoba": 0.05})


def test_coeficientes_vacios_lanza_error():
    with pytest.raises(ValueError):
        simular_shock(-0.10, 1_000_000, {})


def test_impacto_pct_de_su_coparticipacion_cuando_se_provee():
    coef = {"Córdoba": 0.05}
    actual = {"Córdoba": 50_000}
    resultado = simular_shock(-0.10, 1_000_000, coef, coparticipacion_actual_por_provincia=actual)
    impacto = resultado["por_provincia"][0]
    # impacto_pesos = 1_000_000 * -0.10 * 0.05 = -5_000; -5_000 / 50_000 = -0.10
    assert impacto["impacto_pct_de_su_coparticipacion"] == pytest.approx(-0.10)


def test_impacto_pct_es_none_si_no_se_provee_coparticipacion_actual():
    resultado = simular_shock(-0.10, 1_000_000, {"Córdoba": 0.05})
    assert resultado["por_provincia"][0]["impacto_pct_de_su_coparticipacion"] is None
