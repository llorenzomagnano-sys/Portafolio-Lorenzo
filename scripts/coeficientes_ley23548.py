"""
Coeficientes de coparticipación (Ley 23.548) compartidos entre scripts del proyecto.

Extraídos manualmente de data/raw/coeficientes/indices_copa_2018.pdf, página 2,
columna "Coparticipación Federal (Ley 23548)". El valor de CABA se ajustó de 0,0375
(Decreto 194/2016, vigente cuando se hizo el documento) a 0,014 (régimen automático
desde la Ley 27.606, 2020). El 1,55% adicional que Nación le transfiere a CABA desde la
cautelar de la Corte Suprema (dic-2022) se paga por fuera de este coeficiente y no se
incluye. Detalle en docs/methodology.md.

No suman 1: representan el % de cada provincia sobre la masa coparticipable TOTAL
(que incluye la porción que retiene la Nación y el Fondo ATN). Para comparar entre
provincias hay que renormalizarlos (ver build_coefficients_comparison.py).
"""

COEFICIENTES_COPARTICIPACION = {
    "Buenos Aires": 0.12463838,
    "CABA": 0.014,  # ajustado manualmente (original del PDF: 0.03750000)
    "Catamarca": 0.01563276,
    "Córdoba": 0.05039652,
    "Corrientes": 0.02109876,
    "Chaco": 0.02831388,
    "Chubut": 0.00897608,
    "Entre Ríos": 0.02771262,
    "Formosa": 0.02066148,
    "Jujuy": 0.01612470,
    "La Pampa": 0.01065870,
    "La Rioja": 0.01175190,
    "Mendoza": 0.02366778,
    "Misiones": 0.01874838,
    "Neuquén": 0.00985064,
    "Río Negro": 0.01432092,
    "Salta": 0.02175468,
    "San Juan": 0.01918566,
    "San Luis": 0.01295442,
    "Santa Cruz": 0.00897608,
    "Santa Fe": 0.05072448,
    "Santiago del Estero": 0.02344914,
    "Tucumán": 0.02700204,
    "Tierra del Fuego": 0.00700000,
}
