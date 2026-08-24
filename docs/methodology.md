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
- **Producto Bruto Geográfico (PBG) por provincia**: CEPAL, sobre metodología base de
  INDEC (año base 2004). Archivo usado:
  `data/raw/pbg/Jurisdiccion_52sectores.xlsx` (hoja `VABpb`), 2004-2024. No es la
  publicación directa de INDEC (que solo llega a 2017 en su archivo público) — es una
  actualización de CEPAL, usada por ser la fuente más reciente disponible.
- **Coeficientes de coparticipación (Ley 23.548)**: documento tipo Secretaría de
  Hacienda / BNA, "Índices de Distribución de la Coparticipación Federal de Impuestos y
  Regímenes Especiales de Distribución". Archivo usado:
  `data/raw/coeficientes/indices_copa_2018.pdf`, creado el 2 de febrero de 2018 (según
  metadata del archivo) — ver limitaciones abajo sobre el ajuste aplicado.

Todos los archivos fueron descargados manualmente por el usuario y subidos al
repositorio, porque el entorno donde se desarrolló este proyecto no tiene acceso de
salida a internet hacia sitios externos (incluidos `argentina.gob.ar`, `indec.gob.ar`,
y en general casi cualquier dominio externo, confirmado también para Wikipedia,
justia.com, fred.stlouisfed.org). Los scripts `scripts/download_coparticipacion.py` y
`scripts/download_ipc.py` existen para automatizar la descarga de esas dos fuentes en
un entorno con acceso a internet, pero no se probaron end-to-end.

**Fecha de acceso / incorporación al repositorio**: 20 de agosto de 2026 (Núcleo 1),
24 de agosto de 2026 (Núcleo 2).

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

### Núcleo 2 — vintage de los coeficientes de coparticipación y ajuste de CABA

El documento fuente de los coeficientes (`indices_copa_2018.pdf`) es de febrero de
2018, no la versión más actual. Se detectó porque el valor de CABA ahí (3,75%)
corresponde al Decreto 194/2016, mientras que el valor vigente desde 2020 es 1,4%.

**Decisión tomada**: se corrigió manualmente solo el coeficiente de CABA a 1,4%. El
resto de los 23 coeficientes provinciales **no se modificaron**, porque corresponden a
la tabla de la Ley 23.548 (1988), que no cambió desde entonces — la única excepción
material conocida en ese período es justamente la de CABA. El valor de 1,4% se tomó de
una búsqueda web (no se pudo verificar por acceso directo a una fuente primaria desde
este entorno).

**No se modelaron dos ajustes adicionales**, documentados acá para que quede explícito
que fueron evaluados y no aplicados en el Núcleo 2 (si vuelven a ser relevantes,
conviene revisarlos en el Núcleo 3, el simulador):
- La excepción de Córdoba, Santa Fe y San Luis a la detracción del 15% de la masa
  coparticipable para financiar ANSES (por el fallo de la Corte Suprema de 2015). No es
  un coeficiente distinto en la tabla de distribución — es un descuento aplicado sobre
  la masa coparticipable *antes* de repartir según los coeficientes, así que no afecta
  el número que se usa en este núcleo (el % que cada provincia recibe de la masa ya
  neta de esa detracción es aproximadamente el mismo coeficiente, salvo por ese
  descuento adicional que no sufren esas 3 provincias).
- La adición de Tierra del Fuego (1991): ya está incluida en la tabla fuente con su
  propio coeficiente (0,7%), no requirió ajuste.

### Núcleo 2 — por qué no se renormalizan los coeficientes de coparticipación

Los 24 coeficientes de coparticipación (23 provincias + CABA ajustada) suman
aproximadamente 0,6086, no 1. Esto es correcto y esperado: el resto (~37,89% Nación +
1% Fondo ATN, aproximadamente) es la porción de la masa coparticipable que no se
distribuye a ninguna provincia. **Se decidió no renormalizar estos 24 valores para que
sumen 1 entre sí.** Motivo: el coeficiente de Ley 23.548 ya representa, tal cual se
publica, el % de la masa coparticipable *total* que recibe cada provincia — que es
conceptualmente equivalente a "% del PBG total del país" que aporta cada provincia
(ambas son fracciones de un total nacional, no fracciones de un subconjunto). Si se
renormalizara, la comparación dejaría de responder la pregunta "qué proporción de la
recaudación coparticipable/PBG nacional le corresponde a esta provincia" y pasaría a
responder una pregunta distinta ("qué proporción de lo que efectivamente se reparte
entre provincias"), que no fue lo pedido.

**Importante**: esto significa que "% PBG" y "% coparticipación" no son estrictamente
la "misma torta" — son dos fracciones de dos totales nacionales distintos (PBG país vs.
masa coparticipable total). La diferencia entre ambas columnas es un indicador
comparativo de orden de magnitud, útil para el ranking de provincias "ganadoras" y
"perdedoras", pero no debe leerse como "esta provincia se está quedando con X puntos
porcentuales de un pozo común".

### Núcleo 2 — PBG como proxy del aporte tributario: limitación de atribución geográfica

El PBG mide dónde se **genera** la actividad económica, no dónde se **paga** el
impuesto. Las grandes empresas con operaciones en todo el país suelen tener domicilio
fiscal en CABA, así que buena parte de la recaudación de impuestos nacionales
coparticipables generada en otras provincias queda contabilizada, a efectos de
recaudación, como si se hubiera generado en CABA. Esto probablemente **infla el aporte
tributario "real" atribuible a CABA** más allá de lo que su propio PBG ya sugiere (que
de por sí es alto, por concentrar sedes corporativas y servicios), y por el mismo
motivo podría estar **subestimando el aporte tributario real de provincias productivas
como Córdoba**. Esta limitación se documenta también, de forma visible, en
`notebooks/02_aporte_vs_recibo.ipynb`.

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

### Núcleo 2 — Aporte vs. recibo por provincia

- Unidad de análisis: provincia (24 jurisdicciones, un solo corte, no serie temporal).
- "Aporta": % del PBG de cada provincia sobre el PBG total del país, año 2024 (el más
  reciente disponible, dato preliminar en la fuente).
- "Recibe": coeficiente de coparticipación Ley 23.548 por provincia, con el ajuste de
  CABA a 1,4% (ver "Supuestos y limitaciones" arriba). No renormalizado.
- Métrica: diferencia en puntos porcentuales (recibe − aporta). Positivo = la provincia
  recibe proporcionalmente más de lo que su peso económico (PBG) sugeriría; negativo =
  lo contrario.
- Limitación central: el PBG es un proxy del aporte tributario real, con un problema de
  atribución geográfica conocido (sede fiscal vs. lugar de generación de la actividad
  económica), documentado en detalle arriba y en el notebook.
- Script: `scripts/build_coefficients_comparison.py`.
- Notebook: `notebooks/02_aporte_vs_recibo.ipynb`.

### Núcleo 3 — Simulador de sensibilidad

- Función núcleo: `simular_shock(variacion_pct_recaudacion, recaudacion_base,
  coeficientes_por_provincia)` en `scripts/simulator.py`, con 9 tests automáticos en
  `scripts/test_simulator.py` (`pytest scripts/test_simulator.py`).
- **`recaudacion_base`** = masa coparticipable TOTAL de referencia (incluye Nación y
  Fondo ATN, no solo lo que reciben las provincias). No es la recaudación tributaria
  nacional total (que incluye impuestos no coparticipables).
- **Consenso Fiscal excluido**: el simulador usa únicamente los coeficientes de Ley
  23.548 (los mismos del Núcleo 2). La compensación del Consenso Fiscal (Ley 27.429) no
  se incluye porque es un monto que se fija en pesos, no una proporción de la
  recaudación corriente — no tiene sentido que responda a un shock porcentual. Esto
  genera una diferencia intencional con la definición de "coparticipación" del Núcleo 1
  (que sí suma Consenso Fiscal).
- **Adelantos de coparticipación** (p. ej., Decreto 219/2026): se documentan como una
  partida aparte (anticipos a cuenta de coparticipación futura). No cambian el
  coeficiente de reparto de ninguna provincia, así que el simulador no los modela.
- **Caso de validación**: la caída de recaudación del primer cuatrimestre de 2026
  reportada por IARAF ($5,1 billones de caída total, $1,4 billones menos de
  coparticipación). No se consiguió una cifra oficial de masa coparticipable de
  referencia para ese período (misma restricción de acceso a internet del entorno de
  desarrollo), así que la validación se construyó así:
  1. Se estimó una `recaudacion_base` para un cuatrimestre a partir de datos reales
     propios: la coparticipación nominal 2025 del Núcleo 1 (÷3 para aproximar 4 meses),
     "grosseada" dividiendo por la suma de los 24 coeficientes de provincias (0,5876)
     para llegar a la masa coparticipable total (no solo la parte que reciben las
     provincias).
  2. Se calculó qué variación % de recaudación, aplicada a esa base, reproduce
     exactamente el impacto de $1,4 billones que reportó IARAF: **-8,6%**.
  3. Como chequeo de consistencia independiente (no forzado por la calibración
     anterior), se calculó qué fracción de la caída *total* de recaudación ($5,1
     billones) representa la masa coparticipable afectada: **~46,7%**. Este número cae
     dentro del rango que suele citarse para la proporción de la recaudación nacional
     total que es coparticipable en Argentina (aproximadamente 40-50%), lo cual es una
     señal razonable de que la `recaudacion_base` estimada y la cifra de IARAF son
     mutuamente consistentes.
  4. **Esto es una calibración/chequeo de consistencia, no una predicción validada
     contra una tercera fuente independiente** de recaudación coparticipable real del
     primer cuatrimestre de 2026 — esa fuente no se consiguió. Se documenta esta
     limitación explícitamente en vez de presentar el resultado como una validación más
     fuerte de lo que en realidad es.
- **Interfaz interactiva**: se eligió un slider con `ipywidgets` dentro del notebook
  (en vez de una app Streamlit aparte), para mantener consistencia con el resto del
  proyecto (todo basado en notebooks) y porque no requiere levantar un proceso servidor
  aparte para que el análisis sea reproducible.
- Notebook: `notebooks/03_simulador_sensibilidad.ipynb`.
