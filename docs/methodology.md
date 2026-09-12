# Metodología

## Fuentes de datos

Ver `data/raw/README.md` para el detalle completo de trazabilidad (qué archivo, de
dónde, con qué alcance temporal, y por qué se usó o se descartó cada uno).

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de
  Hacienda, Ministerio de Economía de la Nación.
  <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
  Archivo usado: `data/raw/coparticipacion/serie_ron_2003_2025.csv` (2003-2025). El
  Núcleo 1 usa el rango completo 2003-2025 — no llega a años anteriores porque no hay
  fuente de montos nominales de coparticipación para 1990-2002 (se buscó explícitamente
  y no se consiguió).
- **Índice de Precios al Consumidor (IPC), 2016-2025**: INDEC.
  <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>
  Archivo usado: `data/raw/ipc/serie_ipc_divisiones.csv` (mensual, desde dic-2016).
- **Índice de Precios al Consumidor, 2003-2015**: Fundación Norte y Sur / Orlando J.
  Ferreres, provisto directamente por el usuario. Archivo usado:
  `data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`, hoja `IPC ` — ver el
  detalle del empalme más abajo ("Empalme del IPC 2003-2015").
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
- **Ingresos corrientes de Córdoba (proxy), 2015-2025**: recaudación administrada por la
  Dirección General de Rentas de Córdoba, provista directamente por el usuario. Archivo
  usado: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx` (Núcleo 4) — ver
  limitación de alcance y corrección de unidades en la sección del Núcleo 4 más abajo.

Todos los archivos fueron descargados manualmente por el usuario y subidos al
repositorio, porque el entorno donde se desarrolló este proyecto no tiene acceso de
salida a internet hacia sitios externos (incluidos `argentina.gob.ar`, `indec.gob.ar`,
y en general casi cualquier dominio externo, confirmado también para Wikipedia,
justia.com, fred.stlouisfed.org). Los scripts `scripts/download_coparticipacion.py` y
`scripts/download_ipc.py` existen para automatizar la descarga de esas dos fuentes en
un entorno con acceso a internet, pero no se probaron end-to-end.

**Fecha de acceso / incorporación al repositorio**: 20 de agosto de 2026 (Núcleo 1),
24 de agosto de 2026 (Núcleo 2), 12 de septiembre de 2026 (ampliación del Núcleo 1 a
2003-2025).

## Supuestos y limitaciones

### Alcance temporal: 2003-2025 (ampliado desde 2016-2025 original)

El Núcleo 1 se acotó originalmente a 2016-2025 porque no se contaba con una fuente
confiable de IPC para años anteriores (ver más abajo, "Confiabilidad del IPC oficial en
el período 2007-2015", y el detalle de fuentes descartadas en esa sección). Al
incorporarse la base de Fundación Norte y Sur / Orlando Ferreres, se pudo extender el
IPC de forma confiable hasta 2003, así que el alcance pasó a **2003-2025**.

**No llega a 1990** (que era el pedido original de ampliación), pese a que el archivo de
Ferreres sí permitiría reconstruir el índice de precios desde mucho antes (ver más abajo).
El límite real es otro: **no existe, en ninguna fuente disponible para este proyecto,
un dato de montos nominales de coparticipación por provincia para 1990-2002** — el
archivo de RON (Secretaría de Hacienda) que se usa para los montos en pesos solo cubre
desde 2003. Sin esos montos no hay nada que deflactar, así que ampliar el índice de
precios más atrás no serviría de nada en este núcleo. Se confirmó explícitamente con el
usuario que no dispone de esa fuente, y se decidió avanzar con el rango 2003-2025 en vez
de dejar el núcleo bloqueado.

### Confiabilidad del IPC oficial en el período 2007-2015

Es un hecho ampliamente documentado (no solo una discusión política) que el IPC oficial
de INDEC entre aproximadamente 2007 y 2015 subestimó la inflación real, en el contexto
de lo que se conoce como la "intervención del INDEC". El FMI aplicó una censura formal a
la Argentina en 2013 por la calidad de estos datos, y el propio INDEC —bajo otra
gestión, desde fines de 2015— declaró la "emergencia estadística" y descontinuó esos
índices.

Al acotar el núcleo originalmente a 2016-2025, se habían evaluado y descartado además
estas fuentes (ya no relevantes para el rango actual, mantenidas acá como registro):

- **IPC INDEC "histórico" (`sh_ipc_12_16.xls`)**: pese al nombre, solo cubre abril-
  noviembre 2016, no aporta cobertura hacia atrás.
- **Series del Banco Mundial vía FRED (`DDOE01ARA086NWDB`, `DDOE02ARA086NWDB`)**: cubren
  1960-2014 y 1960-2015 respectivamente. El tramo 2003-2013 es internamente coherente,
  pero **2014 y 2015 muestran el índice bajando respecto de 2013** (134,7 → 105,5 →
  120,6), algo económicamente imposible dado que Argentina tuvo inflación alta y
  positiva esos años — indica un empalme mal hecho en el propio dataset del Banco
  Mundial, no un error de descarga, y coincide con el mismo período de descrédito del
  IPC oficial.
- **Serie FRED `FPCPITOTLZGARG`** (inflación anual %, Banco Mundial): solo cubre
  2018-2024, no aporta al hueco 2007-2015.

### Empalme del IPC 2003-2015 (Fundación Norte y Sur / Orlando Ferreres)

La base provista por el usuario (`data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`,
hoja `IPC `) contiene dos tablas anuales relevantes, ambas con base Diciembre 2016=100 o
Diciembre 2015=100 según la tabla:

- **Tabla A — "Índice de Precios al Consumidor GBA (INDEC)"**: serie continua desde
  ~1810 hasta 2025. Para 2007-2014 reproduce las mismas tasas de inflación **bajas y
  desacreditadas** que el IPC oficial de la época (8%-10% anual) — es decir, **no está
  corregida** para el período de intervención. Se usa acá solo para el tramo
  **2004-2006** (pre-intervención, sin motivo para desconfiar).
- **Tabla B — "Índice de Precios al Consumidor GBA (estimaciones privadas)"**: cubre
  2006-2025. Para 2007-2015 reporta tasas mucho más altas (14%-40% anual), consistentes
  con las estimaciones privadas/de consultoras contemporáneas al período de intervención
  del INDEC. Se usa acá para el tramo **2007-2016** (2016 solo para anclar el empalme al
  valor de 2016 ya publicado en este proyecto, no como dato final de ese año).

**Método de empalme** (`scripts/process_coparticipacion.py`, función
`load_ipc_empalmado`): partiendo del valor de `ipc_promedio_anual` de 2016 ya publicado
(100,0, por construcción — ver limitación de ese año en "Metodología de deflactación"),
se encadena **hacia atrás** año por año usando las tasas de variación % anual *tal como
figuran en el archivo fuente* (no se recalculan a partir de niveles, para no introducir
redondeos propios):

1. 2015 a 2007: `nivel[año-1] = nivel[año] / (1 + var_tabla_B[año])`.
2. 2006 a 2003: `nivel[año-1] = nivel[año] / (1 + var_tabla_A[año])`, continuando desde
   el nivel de 2006 obtenido en el paso anterior.

El resultado (índice promedio anual, base implícita = promedio 2016 de este proyecto):
2003→8,40, 2004→8,77, 2005→9,61, 2006→10,66, 2007→12,19, 2008→14,98, 2009→17,46,
2010→21,38, 2011→26,57, 2012→32,79, 2013→40,85, 2014→56,98, 2015→73,66, 2016→100,00 — una
suba acumulada de ~11,9 veces entre 2003 y 2016, consistente en orden de magnitud con la
inflación acumulada conocida de Argentina en ese período.

**Limitación no resuelta**: ambas tablas del archivo Ferreres marcan algunos años con un
asterisco (2015 y 2016 en la Tabla A) y una nota "* Ver metodología", pero el archivo
recibido **no incluye ninguna hoja de metodología** que explique qué ajuste implica ese
asterisco. No se pudo verificar su significado exacto ni la metodología completa de
construcción de la Tabla B (estimaciones privadas) más allá de lo que puede inferirse de
los propios números. Se documenta esta limitación de forma explícita en vez de asumir
una explicación.

**No se usó** el resto de la Tabla A (años anteriores a 2003, con datos hasta ~1810) ni
la hoja "IPC Nacional" del mismo archivo (que replica la serie oficial 2016-2025 ya
usada en el proyecto) — ver el motivo del corte en 2003 en la sección anterior.

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

`scripts/process_coparticipacion.py` verifica explícitamente que existan las 552
combinaciones esperadas (24 jurisdicciones × 23 años, 2003-2025) y también que haya IPC
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
- **Fuente del IPC**: 2016-2025, `data/raw/ipc/serie_ipc_divisiones.csv`, filtrado a
  `Region == "Nacional"` y `Descripcion == "NIVEL GENERAL"`; 2003-2015, empalmado desde
  `data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx` (ver "Empalme del IPC
  2003-2015" arriba).

## Metodología por núcleo

### Núcleo 1 — Serie histórica de coparticipación (2003-2025)

- Unidad de análisis: provincia × año.
- Fuente nominal: RON, filtrado a los conceptos de coparticipación definidos arriba
  (ver "Definición de 'coparticipación' usada en este análisis").
- Deflactado con IPC empalmado (INDEC 2016-2025 + Ferreres/Norte y Sur 2003-2015), base
  promedio 2016 = 100.
- Alcance temporal 2003-2025: no llega a 1990 por falta de una fuente de montos
  nominales de coparticipación anterior a 2003 (ver "Supuestos y limitaciones" arriba).
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

### Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba

- **Fuente de ingresos**: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`
  (hoja `Serie_Mensual`), un archivo que el usuario ya tenía construido. El nombre real
  del archivo no coincide con el que se había anticipado (`dgeyc_ingresos_cordoba.xlsx`)
  — se confirmó con el usuario que igualmente es la fuente que corresponde a este
  núcleo antes de integrarlo.
- **Definición de "ingresos corrientes totales" usada (decisión documentada, no la
  única posible)**: la fila "Total" del archivo = Recursos de Origen Provincial +
  Recursos de Origen Nacional, administrados por la Dirección General de Rentas de
  Córdoba. La propia nota al pie del archivo aclara que **excluye** lo recaudado por
  otros organismos públicos provinciales (p. ej., el Fondo para el Desarrollo
  Energético Provincial recaudado por EPEC). Es decir, **no** es el ingreso corriente
  total del sector público provincial en sentido estricto de ejecución presupuestaria
  (cuenta ahorro-inversión-financiamiento), sino la mejor proxy disponible — se usa así
  tras confirmarlo explícitamente con el usuario.
- **Unidades del archivo fuente, corregidas**: el encabezado de las hojas dice
  "Millones de pesos corrientes", pero es incorrecto — los valores de celda están en
  PESOS corrientes. Se verificó cruzando la fila "Coparticipación Federal de Impuestos
  (CFI)" del archivo: la suma de los 12 meses de 2015 da $23.709.952.851, contra
  $23.673.039.600 (23.673,04 millones) del `monto_nominal` de Córdoba 2015 ya calculado
  en el Núcleo 1 a partir de una fuente independiente (Secretaría de Hacienda) —
  diferencia de apenas 0,16%. Esto confirma la unidad real (pesos) y de paso valida
  cruzadamente el propio Núcleo 1 con una fuente distinta.
- **Problema de formato detectado**: la columna de diciembre de 2023 en `Serie_Mensual`
  está guardada como texto ("dic-23") en vez de fecha, a diferencia de todas las demás
  columnas. `scripts/build_dependencia_fiscal.py` la parsea aparte en vez de asumir que
  todas las columnas tienen el mismo formato.
- **Numerador del ratio**: `monto_nominal` (no `monto_real_base2016`) de Córdoba, del
  Núcleo 1. Para un ratio "% de los ingresos que es coparticipación" hace falta
  comparar magnitudes del mismo tipo (nominal sobre nominal, del mismo año) — usar la
  serie deflactada en el numerador contra un denominador nominal distorsionaría el
  ratio con el efecto de la inflación, sin ningún motivo válido para hacerlo.
- **Alcance**: 2015-2025 (11 años) — intersección entre lo que cubre el archivo de
  ingresos (desde enero de 2015) y el Núcleo 1 (hasta 2025). 2026 queda afuera del
  ratio anual por ser un año calendario incompleto en ambas fuentes.
- **Indicador de sensibilidad**: reutiliza `scripts/simulator.py::simular_shock` del
  Núcleo 3. La masa coparticipable base para 2025 se estima igual que en la validación
  del Núcleo 3 (`recaudacion_base` = coparticipación nominal recibida por las 24
  jurisdicciones en 2025, dividida por la suma de sus 24 coeficientes, para
  "gross-upear" a la masa coparticipable total). El impacto en pesos resultante para
  Córdoba se divide por sus ingresos corrientes totales de 2025 para obtener el
  impacto en % del ingreso provincial total. Es una simplificación de primera ronda: no
  modela respuestas de política provincial (ajuste de gasto, recaudación propia
  adicional, endeudamiento) ante la caída de ingresos.
- Script: `scripts/build_dependencia_fiscal.py`.
- Notebook: `notebooks/04_dependencia_fiscal_cordoba.ipynb`.
