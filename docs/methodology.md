# Metodología

## Fuentes de datos

Ver `data/raw/README.md` para el detalle completo de trazabilidad (qué archivo, de
dónde, con qué alcance temporal, y por qué se usó o se descartó cada uno).

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de
  Hacienda, Ministerio de Economía de la Nación.
  <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
  Archivo usado: `data/raw/coparticipacion/serie_ron_2003_2025.csv` (2003-2025, aunque
  el Núcleo 1 solo usa 2016-2025 — ver más abajo).
- **Índice de Precios al Consumidor (IPC)**: INDEC.
  <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>
  Archivo usado: `data/raw/ipc/serie_ipc_divisiones.csv` (mensual, desde dic-2016).

Ambos archivos fueron descargados manualmente por el usuario y subidos al repositorio,
porque el entorno donde se desarrolló este núcleo no tiene acceso de salida a internet
hacia sitios externos (incluidos `argentina.gob.ar` e `indec.gob.ar`). Los scripts
`scripts/download_coparticipacion.py` y `scripts/download_ipc.py` existen para
automatizar esto en un entorno con acceso a internet, pero no se probaron end-to-end.

**Fecha de acceso / incorporación al repositorio**: 20 de agosto de 2026.

## Supuestos y limitaciones

### Alcance temporal acotado a 2016-2025

El archivo de RON cubre 2003-2025, pero el Núcleo 1 **solo procesa 2016-2025**. Motivo:
no se consiguió una serie de IPC nacional confiable para 2003-2015. En el camino se
evaluaron y descartaron explícitamente:

- **IPC INDEC "histórico" (`sh_ipc_12_16.xls`)**: pese al nombre, solo cubre abril-
  noviembre 2016, no aporta cobertura hacia atrás.
- **Series del Banco Mundial vía FRED (`DDOE01ARA086NWDB`, `DDOE02ARA086NWDB`)**: cubren
  1960-2014 y 1960-2015 respectivamente, y el tramo 2003-2013 es internamente coherente
  (se nota la hiperinflación de 1989-90, la Convertibilidad 1991-2001, la crisis de
  2002). Pero **2014 y 2015 muestran el índice bajando respecto de 2013** (134,7 → 105,5
  → 120,6), algo económicamente imposible dado que Argentina tuvo inflación alta y
  positiva esos años. Esto indica un empalme mal hecho entre fuentes en el propio
  dataset del Banco Mundial en ese punto de corte, no un error de descarga — coincide
  con el período de mayor descrédito del IPC oficial de INDEC (ver nota abajo), que
  aparentemente tampoco pudo resolverse limpiamente en compilaciones internacionales.
- **Serie FRED `FPCPITOTLZGARG`** (inflación anual %, Banco Mundial): solo cubre
  2018-2024, no aporta al hueco 2014-2015.

Ante la falta de una fuente confiable para ese tramo específico, se decidió **no
inventar un valor** (ni interpolar, ni usar el dato roto con una advertencia) y en
cambio **acotar el alcance del núcleo a 2016-2025**, donde el IPC oficial de INDEC es
sólido y de frecuencia mensual. La coparticipación nominal 2003-2015 queda disponible en
los datos crudos por si se retoma este análisis en el futuro con una fuente de precios
mejor para ese tramo.

### Confiabilidad del IPC oficial en el período 2007-2015

Es un hecho ampliamente documentado (no solo una discusión política) que el IPC oficial
de INDEC entre aproximadamente 2007 y 2015 subestimó la inflación real, en el contexto
de lo que se conoce como la "intervención del INDEC". El FMI aplicó una censura formal a
la Argentina en 2013 por la calidad de estos datos, y el propio INDEC —bajo otra
gestión, desde fines de 2015— declaró la "emergencia estadística" y descontinuó esos
índices. Esto refuerza la decisión de no usar ese tramo ni siquiera como aproximación:
además de no encontrarse una fuente empalmada de forma confiable, la fuente oficial de
ese período específico es de por sí cuestionable.

### Definición de "coparticipación" usada en este análisis

El archivo de RON desagrega los recursos transferidos a cada provincia en ~20 conceptos
distintos (coparticipación Ley 23.548, IVA, impuesto a las Ganancias, Bienes Personales,
combustibles líquidos, régimen simplificado, etc.). Para este núcleo, "coparticipación"
se define como la suma de:

1. El concepto que Hacienda reporta como **"coparticipación federal de impuestos Ley
   23.548"** o **"coparticipación federal de impuestos neta Ley 26.075"** según el año
   (son mutuamente excluyentes: el nombre cambia según si se reporta el monto bruto o el
   neto de la detracción por Financiamiento Educativo Ley 26.075, pero nunca aparecen
   ambos el mismo año para la misma provincia — se tratan como el mismo concepto
   subyacente).
2. **"Consenso Fiscal Ley 27.429 — compensación"**, vigente desde 2018, tal como se
   describió en el pedido original de este núcleo.

No se incluyen los demás ~18 conceptos de RON (IVA, Ganancias, Bienes Personales, etc.):
son regímenes de distribución de recursos de origen nacional relacionados, pero
distintos de la coparticipación Ley 23.548 en sentido estricto. Podrían incorporarse en
un análisis futuro de "RON total" si se considera relevante.

### Provincias excluidas

El archivo fuente incluye filas que no son provincias: `fdo.compensador`,
`fondo a.t.n.` (Aportes del Tesoro Nacional), `seguridad social` y `tesoro nacional`. Se
excluyen del análisis, que trabaja únicamente con las 23 provincias + CABA.

### Valores faltantes

`scripts/process_coparticipacion.py` verifica explícitamente que existan las 240
combinaciones esperadas (24 jurisdicciones × 10 años, 2016-2025) y también que haya IPC
disponible para cada año antes de deflactar. Al momento de escribir esto, **no faltó
ninguna combinación** — si en el futuro se detectara alguna, el script corta la
ejecución con un aviso explícito en vez de completarla silenciosamente.

## Metodología de deflactación

- **Base de la serie real**: promedio del año 2016 = 100. Nota: el archivo de IPC
  arranca en diciembre de 2016, así que el "promedio 2016" en la práctica es el valor de
  un solo mes (diciembre). Es una limitación menor y queda documentada acá; no afecta la
  comparabilidad entre provincias dentro del mismo año, solo hace que 2016 no sea un
  promedio anual en sentido estricto.
- **Fórmula**: `monto_real = monto_nominal × (IPC_promedio_2016 / IPC_promedio_año)`,
  donde `IPC_promedio_año` es el promedio simple de los 12 valores mensuales del IPC
  Nacional, Nivel General, de ese año.
- **Fuente del IPC**: `data/raw/ipc/serie_ipc_divisiones.csv`, filtrado a
  `Region == "Nacional"` y `Descripcion == "NIVEL GENERAL"`.

## Metodología por núcleo

### Núcleo 1 — Serie histórica de coparticipación (2016-2025)

- Unidad de análisis: provincia × año.
- Fuente nominal: RON, filtrado a los conceptos de coparticipación definidos arriba
  (ver "Definición de 'coparticipación' usada en este análisis").
- Deflactado con IPC Nacional Nivel General, base promedio 2016 = 100.
- Alcance temporal acotado a 2016-2025 por disponibilidad de datos (ver "Supuestos y
  limitaciones" arriba).
- Script de procesamiento: `scripts/process_coparticipacion.py`.
- Notebook: `notebooks/01_serie_historica.ipynb`.
