# Metodología

Este documento es la referencia técnica del proyecto: fuentes exactas, decisiones
metodológicas y limitaciones de cada núcleo de análisis. El resumen de hallazgos y las
instrucciones para correr el proyecto están en el [README](../README.md) — acá va el
detalle que sostiene cada número.

Está organizado en una sección por núcleo (Fuentes / Metodología / Supuestos y
limitaciones), más un apéndice con fuentes que se evaluaron y se descartaron.

## Cómo se obtuvieron los datos

Todos los archivos de `data/raw/` fueron incorporados manualmente por el autor y
subidos al repositorio: el entorno donde se desarrolló este proyecto no tiene acceso de
salida a internet hacia sitios externos (confirmado para `argentina.gob.ar`,
`indec.gob.ar`, Wikipedia, `justia.com`, `fred.stlouisfed.org`, y en general casi
cualquier dominio externo). Los scripts `scripts/download_coparticipacion.py` y
`scripts/download_ipc.py` existen para automatizar la descarga de esas dos fuentes en
un entorno con acceso a internet, pero no se probaron end-to-end. Detalle completo de
trazabilidad de cada archivo (de dónde, con qué alcance, por qué se usó o se descartó)
en [`data/raw/README.md`](../data/raw/README.md).

---

## Núcleo 1 — Serie histórica de coparticipación (2003-2025)

### Fuentes

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de
  Hacienda, Ministerio de Economía de la Nación.
  <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
  Archivo: `data/raw/coparticipacion/serie_ron_2003_2025.csv` (2003-2025).
- **IPC 2016-2025**: INDEC.
  <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>
  Archivo: `data/raw/ipc/serie_ipc_divisiones.csv` (mensual, desde dic-2016).
- **IPC 2003-2015**: Fundación Norte y Sur / Orlando J. Ferreres, provisto directamente
  por el autor (sin URL pública verificada). Archivo:
  `data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`, hoja `IPC `.

Fecha de incorporación: 20 de agosto de 2026 (rango original 2016-2025), ampliado a
2003-2025 el 12 de septiembre de 2026.

### Metodología

**Definición de "coparticipación" usada acá**: el archivo de RON desagrega los
recursos transferidos a cada provincia en ~20 conceptos (coparticipación Ley 23.548,
IVA, Ganancias, Bienes Personales, combustibles líquidos, régimen simplificado, etc.).
Se define "coparticipación" como la suma de:

1. El concepto que Hacienda reporta como **"coparticipación federal de impuestos Ley
   23.548"** o **"coparticipación federal de impuestos neta Ley 26.075"** según el año
   (mutuamente excluyentes: el nombre cambia según si se reporta el monto bruto o el
   neto de la detracción por Financiamiento Educativo, pero nunca aparecen ambos el
   mismo año para la misma provincia — se tratan como el mismo concepto).
2. **"Consenso Fiscal Ley 27.429 — compensación"**, vigente desde 2018.

No se incluyen los demás ~18 conceptos de RON: son regímenes de distribución
relacionados, pero distintos de la coparticipación Ley 23.548 en sentido estricto.

**Provincias excluidas**: el archivo fuente incluye filas que no son provincias
(`fdo.compensador`, `fondo a.t.n.`, `seguridad social`, `tesoro nacional`) — se
excluyen; el análisis trabaja con 23 provincias + CABA.

**Deflactación**:
- Fórmula: `monto_real = monto_nominal × (IPC_promedio_2016 / IPC_promedio_año)`.
- Base: promedio del año 2016 = 100. El archivo de IPC oficial arranca en diciembre de
  2016, así que el "promedio 2016" es en la práctica el valor de un solo mes — no
  afecta la comparabilidad entre provincias dentro del mismo año, pero 2016 no es un
  promedio anual en sentido estricto.
- Fuente del IPC 2016-2025: `serie_ipc_divisiones.csv`, filtrado a
  `Region == "Nacional"` y `Descripcion == "NIVEL GENERAL"`, promedio simple de los 12
  valores mensuales.

**Empalme del IPC 2003-2015** (`scripts/process_coparticipacion.py::load_ipc_empalmado`):
el archivo de Ferreres/Norte y Sur (hoja `IPC `) tiene dos tablas anuales relevantes:

- **Tabla A — "GBA (INDEC)"**: serie continua desde ~1810. Para 2007-2014 reproduce las
  mismas tasas bajas y desacreditadas del IPC oficial de la época — no está corregida
  para el período de intervención. Se usa solo para **2004-2006** (pre-intervención).
- **Tabla B — "GBA (estimaciones privadas)"**: cubre 2006-2025, con tasas mucho más
  altas para 2007-2015, consistentes con estimaciones privadas contemporáneas a la
  intervención del INDEC. Se usa para **2007-2016** (2016 solo para anclar el empalme
  al valor de 2016 ya calculado, no como dato final de ese año).

Método: partiendo del `ipc_promedio_anual` de 2016 ya calculado (100,0), se encadena
hacia atrás año por año con las tasas de variación % anual *tal como figuran en el
archivo* (no se recalculan desde niveles, para no introducir redondeos propios):
1. 2015 a 2007: `nivel[año-1] = nivel[año] / (1 + var_tabla_B[año])`.
2. 2006 a 2003: `nivel[año-1] = nivel[año] / (1 + var_tabla_A[año])`.

Resultado (índice, base implícita = promedio 2016 de este proyecto): 2003→8,40,
2004→8,77, 2005→9,61, 2006→10,66, 2007→12,19, 2008→14,98, 2009→17,46, 2010→21,38,
2011→26,57, 2012→32,79, 2013→40,85, 2014→56,98, 2015→73,66, 2016→100,00 — una suba
acumulada de ~11,9 veces entre 2003 y 2016, consistente en orden de magnitud con la
inflación acumulada conocida de Argentina en ese período.

### Supuestos y limitaciones

- **No llega a 1990** (el alcance original pedido): no existe, en ninguna fuente
  disponible, un dato de montos nominales de coparticipación por provincia para
  1990-2002 — el archivo de RON solo cubre desde 2003. El índice de precios sí podría
  reconstruirse desde antes (la Tabla A de Ferreres llega a ~1810), pero sin montos
  nominales que deflactar no serviría de nada. Se confirmó explícitamente con el autor
  que no dispone de esa fuente.
- **Confiabilidad del IPC oficial 2007-2015**: es un hecho ampliamente documentado (no
  solo una discusión política) que el IPC oficial de INDEC en ese período subestimó la
  inflación real — la "intervención del INDEC". El FMI censuró formalmente a Argentina
  en 2013 por la calidad de estos datos, y el propio INDEC, bajo otra gestión desde
  fines de 2015, declaró la "emergencia estadística" y descontinuó esos índices.
- **Limitación sin resolver del archivo Ferreres**: ambas tablas marcan algunos años
  con asterisco (2015 y 2016 en la Tabla A) y una nota "Ver metodología", pero el
  archivo recibido no incluye ninguna hoja de metodología que explique ese ajuste. No
  se pudo verificar su significado exacto — se documenta la limitación en vez de
  asumir una explicación.
- **Valores faltantes**: `scripts/process_coparticipacion.py` verifica explícitamente
  que existan las 552 combinaciones esperadas (24 jurisdicciones × 23 años) y que haya
  IPC para cada año antes de deflactar. Al momento de escribir esto, no faltó ninguna
  — si en el futuro faltara alguna, el script corta la ejecución con un aviso explícito
  en vez de completarla silenciosamente.
- Script de procesamiento: `scripts/process_coparticipacion.py`. Notebook:
  `notebooks/01_serie_historica.ipynb`.

---

## Núcleo 2 — Aporte vs. recibo por provincia

### Fuentes

- **Producto Bruto Geográfico (PBG) por provincia**: CEPAL, sobre metodología base de
  INDEC (año base 2004). Archivo: `data/raw/pbg/Jurisdiccion_52sectores.xlsx` (hoja
  `VABpb`), 2004-2024. No es la publicación directa de INDEC (que solo llega a 2017 en
  su archivo público) — es una actualización de CEPAL, usada por ser la más reciente
  disponible.
- **Coeficientes de coparticipación (Ley 23.548)**: documento tipo Secretaría de
  Hacienda / BNA, "Índices de Distribución de la Coparticipación Federal de Impuestos y
  Regímenes Especiales de Distribución". Archivo: `data/raw/coeficientes/indices_copa_2018.pdf`,
  creado el 2 de febrero de 2018 (según metadata del archivo).

### Metodología

- Unidad de análisis: provincia (24 jurisdicciones, un solo corte, no serie temporal).
- **"Aporta"**: % del PBG de cada provincia sobre el PBG total del país, año 2024 (el
  más reciente disponible, dato preliminar en la fuente).
- **"Recibe"**: coeficiente de coparticipación Ley 23.548 por provincia (ver ajuste de
  CABA abajo). No renormalizado — ver por qué en "Supuestos y limitaciones".
- **Métrica**: diferencia en puntos porcentuales (recibe − aporta). Positivo = la
  provincia recibe proporcionalmente más de lo que su peso económico (PBG) sugeriría;
  negativo, lo contrario.
- Script: `scripts/build_coefficients_comparison.py`. Notebook:
  `notebooks/02_aporte_vs_recibo.ipynb`.

### Supuestos y limitaciones

- **Vintage de los coeficientes y ajuste de CABA**: el documento fuente es de febrero
  de 2018, no la versión más actual — se detectó porque el valor de CABA ahí (3,75%)
  corresponde al Decreto 194/2016, mientras que el vigente desde 2020 es 1,4%. Se
  corrigió manualmente solo ese valor; los otros 23 coeficientes no se modificaron,
  porque corresponden a la tabla de la Ley 23.548 (1988), sin cambios desde entonces.
  El 1,4% de CABA se tomó de una búsqueda web, sin poder verificarlo por acceso directo
  a una fuente primaria desde este entorno.
  - No se modelaron dos ajustes adicionales, evaluados y descartados para este núcleo
    (relevantes en cambio para el Núcleo 3): la excepción de Córdoba/Santa Fe/San Luis
    a la detracción del 15% para ANSES (es un descuento sobre la masa coparticipable
    antes del reparto, no un coeficiente distinto) y la adición de Tierra del Fuego
    (ya incluida en la tabla fuente con su propio 0,7%).
- **Por qué no se renormalizan los coeficientes**: los 24 coeficientes suman ~0,6086,
  no 1 — correcto y esperado, porque el resto (~37,89% Nación + ~1% Fondo ATN) es la
  porción que no se distribuye a ninguna provincia. Se decidió no renormalizar: el
  coeficiente ya representa, tal cual se publica, el % de la masa coparticipable
  *total* que recibe cada provincia, conceptualmente equivalente a "% del PBG total del
  país" (ambas son fracciones de un total nacional, no de un subconjunto).
  Renormalizar cambiaría la pregunta que responde la comparación ("qué % de la masa
  total le corresponde" pasaría a ser "qué % de lo que efectivamente se reparte entre
  provincias"), que no fue lo pedido. Esto también implica que "% PBG" y "%
  coparticipación" no son la "misma torta" — son fracciones de dos totales nacionales
  distintos, así que la diferencia es un indicador comparativo de orden de magnitud
  (útil para el ranking de provincias), no una relación exacta 1 a 1.
- **PBG como proxy del aporte tributario real**: el PBG mide dónde se *genera* la
  actividad económica, no dónde se *paga* el impuesto. Las grandes empresas con
  operaciones en todo el país suelen tener domicilio fiscal en CABA, así que buena
  parte de la recaudación generada en otras provincias queda contabilizada como si se
  hubiera generado en CABA. Esto probablemente infla el aporte tributario "real"
  atribuible a CABA y subestima el de provincias productivas como Córdoba. Documentado
  también, de forma visible, en el notebook.

---

## Núcleo 3 — Simulador de sensibilidad

### Fuentes

No usa una fuente propia: reutiliza los coeficientes de coparticipación del Núcleo 2
(`scripts/coeficientes_ley23548.py`) y, para el caso de validación, la coparticipación
nominal 2025 ya calculada en el Núcleo 1.

### Metodología

- Función núcleo: `simular_shock(variacion_pct_recaudacion, recaudacion_base,
  coeficientes_por_provincia)` en `scripts/simulator.py`, con 9 tests automáticos en
  `scripts/test_simulator.py` (`pytest scripts/test_simulator.py`).
- **`recaudacion_base`** = masa coparticipable TOTAL de referencia (incluye Nación y
  Fondo ATN, no solo lo que reciben las provincias). No es la recaudación tributaria
  nacional total (que incluye impuestos no coparticipables).
- **Consenso Fiscal excluido**: el simulador usa únicamente los coeficientes de Ley
  23.548. La compensación del Consenso Fiscal (Ley 27.429) no se incluye porque es un
  monto fijado en pesos, no una proporción de la recaudación corriente — no tiene
  sentido que responda a un shock porcentual. Esto genera una diferencia intencional
  con la definición de "coparticipación" del Núcleo 1 (que sí suma Consenso Fiscal).
- **Adelantos de coparticipación** (p. ej., Decreto 219/2026): se documentan como una
  partida aparte (anticipos a cuenta de coparticipación futura). No cambian el
  coeficiente de reparto de ninguna provincia, así que el simulador no los modela.
- **Shock uniforme**: se aplica de forma proporcional y simultánea a toda la masa
  coparticipable — no distingue por tipo de impuesto (IVA, Ganancias, etc.), aunque en
  la práctica una caída de recaudación puede afectar de forma desigual a los distintos
  impuestos que la componen.
- **Interfaz interactiva**: un slider de `ipywidgets` dentro del notebook, en vez de
  una app Streamlit aparte — mantiene todo el proyecto reproducible desde notebooks,
  sin depender de un proceso servidor adicional.
- Notebook: `notebooks/03_simulador_sensibilidad.ipynb`.

### Supuestos y limitaciones

**Caso de validación**: la caída de recaudación del primer cuatrimestre de 2026
reportada por IARAF ($5,1 billones de caída total, $1,4 billones menos de
coparticipación). No se consiguió una cifra oficial de masa coparticipable de
referencia para ese período (misma restricción de acceso a internet del entorno), así
que la validación se construyó así:

1. Se estimó una `recaudacion_base` para un cuatrimestre a partir de datos propios: la
   coparticipación nominal 2025 del Núcleo 1 (÷3 para aproximar 4 meses), "grosseada"
   dividiendo por la suma de los 24 coeficientes de provincias (0,5876) para llegar a
   la masa coparticipable total.
2. Se calculó qué variación % de recaudación, aplicada a esa base, reproduce
   exactamente el impacto de $1,4 billones que reportó IARAF: **-8,6%**.
3. Como chequeo de consistencia independiente (no forzado por la calibración
   anterior), se calculó qué fracción de la caída *total* de recaudación ($5,1
   billones) representa la masa coparticipable afectada: **~46,7%**, dentro del rango
   que suele citarse para la proporción de la recaudación nacional que es
   coparticipable en Argentina (~40-50%) — una señal razonable de que la
   `recaudacion_base` estimada y la cifra de IARAF son mutuamente consistentes.
4. **Esto es una calibración/chequeo de consistencia, no una predicción validada
   contra una tercera fuente independiente** de recaudación coparticipable real del
   primer cuatrimestre de 2026 — esa fuente no se consiguió. Se documenta esta
   limitación explícitamente en vez de presentar el resultado como una validación más
   fuerte de lo que en realidad es. Para ese escenario, el impacto estimado en Córdoba
   es de -$120.073 millones.

---

## Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba

### Fuentes

- **Ingresos corrientes de Córdoba (proxy), 2015-2025**: recaudación administrada por
  la Dirección General de Rentas de Córdoba, provista directamente por el autor
  (probablemente republicada por DGEyC Córdoba, sin URL pública verificada desde este
  entorno). Archivo: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`,
  hoja `Serie_Mensual`. El nombre real del archivo no coincidía con el anticipado
  (`dgeyc_ingresos_cordoba.xlsx`) — se confirmó con el autor que es la fuente correcta
  antes de integrarla.
- Reutiliza además la coparticipación nominal de Córdoba del Núcleo 1 y el simulador
  del Núcleo 3.

### Metodología

- **Definición de "ingresos corrientes totales" usada (no la única posible)**: la fila
  "Total" del archivo = Recursos de Origen Provincial + Recursos de Origen Nacional,
  administrados por la Dirección General de Rentas. Ver limitación de alcance abajo.
- **Numerador del ratio**: `monto_nominal` (no `monto_real_base2016`) de Córdoba, del
  Núcleo 1 — un ratio "% de los ingresos que es coparticipación" necesita magnitudes
  del mismo tipo (nominal sobre nominal, mismo año); usar la serie deflactada contra un
  denominador nominal distorsionaría el ratio con el efecto de la inflación, sin
  ningún motivo válido.
- **Alcance**: 2015-2025 (11 años) — intersección entre lo que cubre el archivo de
  ingresos (desde enero de 2015) y el Núcleo 1 (hasta 2025). 2026 queda afuera del
  ratio anual por ser un año calendario incompleto en ambas fuentes.
- **Indicador de sensibilidad**: reutiliza `scripts/simulator.py::simular_shock`. La
  masa coparticipable base para 2025 se estima igual que en la validación del Núcleo 3
  (coparticipación nominal recibida por las 24 jurisdicciones en 2025, dividida por la
  suma de sus 24 coeficientes). El impacto en pesos resultante para Córdoba se divide
  por sus ingresos corrientes totales de 2025 para obtener el impacto en % del ingreso
  provincial total.
- Script: `scripts/build_dependencia_fiscal.py`. Notebook:
  `notebooks/04_dependencia_fiscal_cordoba.ipynb`.

### Supuestos y limitaciones

- **Limitación de alcance de "ingresos corrientes totales"**: la propia nota al pie
  del archivo fuente aclara que la fila "Total" excluye lo recaudado por otros
  organismos públicos provinciales (p. ej., el Fondo para el Desarrollo Energético
  Provincial recaudado por EPEC). Es decir, **no** es el ingreso corriente total del
  sector público provincial en sentido estricto de ejecución presupuestaria, sino la
  mejor proxy disponible — se usó así tras confirmarlo explícitamente con el autor.
- **Unidades del archivo fuente, corregidas**: el encabezado de las hojas dice
  "Millones de pesos corrientes", pero es incorrecto — los valores de celda están en
  PESOS corrientes. Se verificó cruzando la fila "Coparticipación Federal de Impuestos
  (CFI)" del archivo: la suma de los 12 meses de 2015 da $23.709.952.851, contra
  $23.673.039.600 del `monto_nominal` de Córdoba 2015 ya calculado en el Núcleo 1 a
  partir de una fuente independiente (Secretaría de Hacienda) — diferencia de apenas
  0,16%, lo que confirma la unidad real y de paso valida cruzadamente el Núcleo 1 con
  una fuente distinta. Esa validación cruzada solo se hizo para 2015 — no se verificó
  que las dos fuentes sigan coincidiendo en los 10 años restantes.
- **Problema de formato detectado**: la columna de diciembre de 2023 en
  `Serie_Mensual` está guardada como texto ("dic-23") en vez de fecha, a diferencia de
  todas las demás columnas — `scripts/build_dependencia_fiscal.py` la parsea aparte.
- **Simplificación de primera ronda**: el indicador de sensibilidad no modela
  respuestas de política provincial (ajuste de gasto, recaudación propia adicional,
  endeudamiento) ante una caída de ingresos.

---

## Apéndice: fuentes evaluadas y descartadas para el Núcleo 1

Al acotar originalmente el Núcleo 1 a 2016-2025 (antes de conseguir la base de
Ferreres/Norte y Sur), se evaluaron y descartaron estas fuentes para cubrir 2003-2015 —
se mantienen acá como registro, ya no son relevantes para el alcance actual:

- **IPC INDEC "histórico" (`sh_ipc_12_16.xls`)**: pese al nombre, solo cubre
  abril-noviembre 2016, no aporta cobertura hacia atrás.
- **Series del Banco Mundial vía FRED (`DDOE01ARA086NWDB`, `DDOE02ARA086NWDB`)**:
  cubren 1960-2014 y 1960-2015. El tramo 2003-2013 es internamente coherente, pero 2014
  y 2015 muestran el índice bajando respecto de 2013 (134,7 → 105,5 → 120,6), algo
  económicamente imposible dado que Argentina tuvo inflación alta y positiva esos años
  — indica un empalme mal hecho en el propio dataset del Banco Mundial, no un error de
  descarga, y coincide con el mismo período de descrédito del IPC oficial.
- **Serie FRED `FPCPITOTLZGARG`** (inflación anual %, Banco Mundial): solo cubre
  2018-2024, no aporta al hueco 2007-2015.
