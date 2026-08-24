"""
Simulador de sensibilidad — Núcleo 3.

Dado un shock porcentual en la recaudación tributaria nacional coparticipable,
calcula el impacto resultante en pesos (y en términos relativos) para cada provincia,
usando los coeficientes de distribución de la Ley 23.548 relevados en el Núcleo 2.

SUPUESTOS (documentados acá y en docs/methodology.md):

1. `recaudacion_base` es la MASA COPARTICIPABLE TOTAL de referencia, en pesos -- el
   monto sujeto a distribución por la Ley 23.548 ANTES de aplicar los coeficientes
   (incluye la porción que retiene la Nación y el Fondo ATN, no solo lo que reciben
   las provincias). No es la recaudación tributaria nacional total, que incluye
   impuestos no coparticipables (p. ej., derechos de exportación).

2. El simulador usa ÚNICAMENTE los coeficientes de la Ley 23.548 (los mismos del
   Núcleo 2, con CABA ajustada a 1,4%). NO incluye la compensación del Consenso Fiscal
   (Ley 27.429): es un monto que históricamente se fijó en pesos, no una proporción de
   la recaudación corriente, así que no tiene sentido que responda proporcionalmente a
   un shock de recaudación. Esto genera una diferencia intencional con la definición de
   "coparticipación" del Núcleo 1 (que sí suma Consenso Fiscal) -- documentado acá y en
   methodology.md.

3. Los adelantos/anticipos de coparticipación (p. ej., los otorgados por Decreto
   219/2026) son una PARTIDA APARTE: son anticipos a cuenta de coparticipación futura,
   no un cambio en el coeficiente de reparto de cada provincia. El simulador no los
   modela -- un shock de recaudación no cambia cuánto le corresponde a cada provincia
   según su coeficiente, aunque el momento en que efectivamente cobra ese dinero pueda
   variar por este tipo de mecanismos de adelanto.

4. El shock se aplica de forma proporcional y simultánea a toda la masa coparticipable
   -- no distingue por tipo de impuesto (IVA, Ganancias, Bienes Personales, etc.),
   aunque en la práctica una caída de recaudación puede afectar de forma desigual a los
   distintos impuestos que componen la masa coparticipable.
"""
from typing import Optional


def simular_shock(
    variacion_pct_recaudacion: float,
    recaudacion_base: float,
    coeficientes_por_provincia: dict[str, float],
    coparticipacion_actual_por_provincia: Optional[dict[str, float]] = None,
) -> dict:
    """Calcula el impacto en pesos de un shock de recaudación para cada provincia.

    Parámetros
    ----------
    variacion_pct_recaudacion : float
        Variación porcentual de la recaudación coparticipable, como fracción
        (ej.: -0.10 para una caída del 10%; +0.05 para un aumento del 5%).
    recaudacion_base : float
        Masa coparticipable total de referencia, en pesos, ANTES de aplicar los
        coeficientes (ver supuesto 1 en el docstring del módulo). Debe ser positiva.
    coeficientes_por_provincia : dict[str, float]
        Mapa provincia -> coeficiente de coparticipación (Ley 23.548). No hace falta
        que sumen 1 (representan % de la masa coparticipable total, no solo de lo que
        reciben las provincias entre sí).
    coparticipacion_actual_por_provincia : dict[str, float], opcional
        Mapa provincia -> monto de coparticipación que recibe hoy, en pesos. Si se
        provee, se calcula además el impacto como % de lo que cada provincia recibe
        actualmente. Si no, ese campo queda en `None` para cada provincia.

    Devuelve
    -------
    dict con:
        - "variacion_pct_recaudacion", "recaudacion_base": los parámetros de entrada.
        - "monto_total_afectado": variación en pesos de la masa coparticipable total
          (recaudacion_base * variacion_pct_recaudacion).
        - "por_provincia": lista de dicts con
          {provincia, coeficiente, impacto_pesos, impacto_pct_de_su_coparticipacion}.
        - "total_impacto_provincias": suma de impacto_pesos de todas las provincias
          (será menor en valor absoluto que monto_total_afectado, porque los
          coeficientes de provincias no suman 1 -- el resto es Nación y ATN).

    Excepciones
    -----------
    ValueError si `recaudacion_base` no es positiva o si `coeficientes_por_provincia`
    está vacío.
    """
    if recaudacion_base <= 0:
        raise ValueError("recaudacion_base debe ser positiva.")
    if not coeficientes_por_provincia:
        raise ValueError("coeficientes_por_provincia no puede estar vacío.")

    monto_total_afectado = recaudacion_base * variacion_pct_recaudacion

    por_provincia = []
    for provincia, coeficiente in coeficientes_por_provincia.items():
        impacto_pesos = monto_total_afectado * coeficiente

        impacto_pct_actual = None
        if coparticipacion_actual_por_provincia is not None:
            monto_actual = coparticipacion_actual_por_provincia.get(provincia)
            if monto_actual:
                impacto_pct_actual = impacto_pesos / monto_actual

        por_provincia.append(
            {
                "provincia": provincia,
                "coeficiente": coeficiente,
                "impacto_pesos": impacto_pesos,
                "impacto_pct_de_su_coparticipacion": impacto_pct_actual,
            }
        )

    total_impacto_provincias = sum(p["impacto_pesos"] for p in por_provincia)

    return {
        "variacion_pct_recaudacion": variacion_pct_recaudacion,
        "recaudacion_base": recaudacion_base,
        "monto_total_afectado": monto_total_afectado,
        "por_provincia": por_provincia,
        "total_impacto_provincias": total_impacto_provincias,
    }


if __name__ == "__main__":
    coef_ejemplo = {"Córdoba": 0.05039652, "Buenos Aires": 0.12463838}
    resultado = simular_shock(-0.10, 1_000_000, coef_ejemplo)
    print(resultado)
