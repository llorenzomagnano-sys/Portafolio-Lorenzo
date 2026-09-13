# Metodología

Estas son las notas técnicas del proyecto: de dónde sale cada dato, qué decisiones tomé al procesarlo y dónde el análisis tiene puntos flojos. El resumen de hallazgos y las instrucciones para correr todo están en el [README](../README.md) — acá va el detalle que sostiene cada número.

Va organizado en una sección por núcleo (fuentes, metodología, supuestos y limitaciones), más un apéndice al final con fuentes que evalué y descarté para el Núcleo 1.

## Cómo conseguí los datos

Todos los archivos de `data/raw/` los subí yo a mano: el entorno donde armé este proyecto no tiene salida a internet hacia sitios externos (lo confirmé para `argentina.gob.ar`, `indec.gob.ar`, Wikipedia, `justia.com`, `fred.stlouisfed.org`, y en general casi cualquier dominio externo). Dejé escritos `scripts/download_coparticipacion.py` y `scripts/download_ipc.py` para automatizar la descarga de esas dos fuentes en un entorno con acceso a internet, pero no llegué a probarlos de punta a punta. El detalle de trazabilidad de cada archivo — de dónde salió, qué alcance tiene, por qué lo usé o lo descarté — está en [`data/raw/README.md`](../data/raw/README.md).

---

## Núcleo 1 — Serie histórica de coparticipación (2003-2025)

### Fuentes

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de Hacienda, Ministerio de Economía de la Nación. <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>. Archivo: `data/raw/coparticipacion/serie_ron_2003_2025.csv` (2003-2025).
- **IPC 2016-2025**: INDEC. <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>. Archivo: `data/raw/ipc/serie_ipc_divisiones.csv` (mensual, desde dic-2016).
- **IPC 2003-2015**: Fundación Norte y Sur / Orlando J. Ferreres, que me pasaron directamente (sin URL pública verificada). Archivo: `data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`, hoja `IPC `. Es la compilación histórica de series económicas de Argentina que hizo Ferreres para la Fundación Norte y Sur (conocido por *"Dos siglos de Economía Argentina"*) — la uso como insumo de análisis, sin reclamar autoría sobre la compilación.

Incorporé estos datos el 20 de agosto de 2026 (con el rango original acotado a 2016-2025), y amplié a 2003-2025 el 12 de septiembre.

### Metodología

El archivo de RON desagrega lo transferido a cada provincia en unos 20 conceptos (coparticipación Ley 23.548, IVA, Ganancias, Bienes Personales, combustibles líquidos, régimen simplificado, etc.). Definí "coparticipación" como la suma de dos de esos conceptos: el que Hacienda reporta como "coparticipación federal de impuestos Ley 23.548" o "coparticipación federal de impuestos neta Ley 26.075" según el año (son mutuamente excluyentes — el nombre cambia según si se reporta el monto bruto o neto de la detracción por Financiamiento Educativo, pero nunca aparecen los dos el mismo año para la misma provincia, así que los trato como el mismo concepto), más "Consenso Fiscal Ley 27.429 — compensación", vigente desde 2018. Dejé afuera los otros ~18 conceptos de RON: son regímenes de distribución relacionados, pero distintos de la coparticipación Ley 23.548 en sentido estricto.

El archivo fuente también trae filas que no son provincias (`fdo.compensador`, `fondo a.t.n.`, `seguridad social`, `tesoro nacional`) — las excluí, así que el análisis queda en 23 provincias + CABA.

Para deflactar uso `monto_real = monto_nominal × (IPC_promedio_2016 / IPC_promedio_año)`, con base en el promedio del año 2016 = 100. El IPC oficial arranca en diciembre de 2016, así que ese "promedio 2016" en la práctica es el valor de un solo mes — no afecta la comparación entre provincias dentro de un mismo año, pero 2016 no es un promedio anual en sentido estricto. Para 2016-2025 uso `serie_ipc_divisiones.csv` filtrado a `Region == "Nacional"` y `Descripcion == "NIVEL GENERAL"`, promediando los 12 valores mensuales.

Para 2003-2015 tuve que empalmar dos series del archivo de Ferreres/Norte y Sur (función `load_ipc_empalmado` en `scripts/process_coparticipacion.py`), porque ninguna de las dos tablas del archivo sirve sola para todo el período: la tabla "GBA (INDEC)" es una serie continua desde ~1810, pero para 2007-2014 reproduce las mismas tasas bajas y desacreditadas del IPC oficial de la época — no está corregida para el período de intervención, así que solo la uso para 2004-2006. La tabla "GBA (estimaciones privadas)" cubre 2006-2025 con tasas mucho más altas para 2007-2015, consistentes con lo que estimaban las consultoras privadas en ese momento — la uso para 2007-2016 (2016 solo para anclar el empalme al valor que ya tenía calculado, no como dato final de ese año).

El método es simple: parto del `ipc_promedio_anual` de 2016 que ya tenía (100,0) y encadeno hacia atrás, año por año, con las tasas de variación % anual tal como figuran en el archivo (no las recalculo desde niveles, para no meter redondeos propios): de 2015 a 2007 con la tabla de estimaciones privadas, de 2006 a 2003 con la tabla del INDEC. El resultado (índice, misma base implícita) queda: 2003→8,40, 2004→8,77, 2005→9,61, 2006→10,66, 2007→12,19, 2008→14,98, 2009→17,46, 2010→21,38, 2011→26,57, 2012→32,79, 2013→40,85, 2014→56,98, 2015→73,66, 2016→100,00 — una suba acumulada de ~11,9 veces entre 2003 y 2016, que está en línea con la inflación acumulada que efectivamente tuvo Argentina en ese período.

### Supuestos y limitaciones

No llega a 1990, que era la idea original: no encontré, en ninguna fuente, montos nominales de coparticipación por provincia para 1990-2002 — el archivo de RON arranca en 2003. El índice de precios en sí podría reconstruirse desde antes (la tabla de Ferreres llega a ~1810), pero sin montos nominales que deflactar no serviría de mucho. Confirmé con la fuente que no hay ese dato disponible.

Sobre el IPC oficial de 2007-2015: que subestimó la inflación real en ese período no es una discusión de opinión, es un hecho bastante documentado — la llamada "intervención del INDEC". El FMI censuró formalmente a Argentina en 2013 por la calidad de esos datos, y el propio INDEC, ya con otra gestión desde fines de 2015, declaró la "emergencia estadística" y discontinuó esos índices.

Una limitación que no pude resolver: las dos tablas del archivo de Ferreres marcan algunos años con asterisco (2015 y 2016 en la tabla del INDEC) y una nota "Ver metodología", pero el archivo que tengo no incluye ninguna hoja de metodología que explique ese ajuste. No sé qué significa exactamente, así que lo dejo anotado acá en vez de inventar una explicación.

`scripts/process_coparticipacion.py` chequea que existan las 552 combinaciones esperadas (24 jurisdicciones × 23 años) y que haya IPC para cada año antes de deflactar. Hasta ahora no faltó ninguna; si en algún momento faltara alguna, el script corta la ejecución con un aviso en vez de completar el hueco por su cuenta.

También agregué una lectura en términos relativos: además del gráfico en niveles absolutos (donde Buenos Aires domina el gráfico solo por su tamaño), indexé cada provincia a su propio valor de 2003 (=100). Ahí las cuatro provincias de referencia quedan casi indistinguibles (335-357 puntos en 2025) — confirma que el salto de la serie responde a la dinámica agregada del régimen, no a que a Córdoba le haya ido mejor o peor que al resto. Sin este gráfico, el de niveles absolutos por sí solo podría sugerir, incorrectamente, que a Buenos Aires "le va mejor" en el régimen, cuando en realidad solo es más grande en nivel.

Script: `scripts/process_coparticipacion.py`. Notebook: `notebooks/01_serie_historica.ipynb`.

---

## Núcleo 2 — Aporte vs. recibo por provincia

### Fuentes

- **Producto Bruto Geográfico (PBG) por provincia**: CEPAL, sobre metodología base de INDEC (año base 2004). Archivo: `data/raw/pbg/Jurisdiccion_52sectores.xlsx` (hoja `VABpb`), 2004-2024. No es la publicación directa de INDEC (que en su archivo público solo llega a 2017) — es una actualización de CEPAL, la más reciente que encontré.
- **Coeficientes de coparticipación (Ley 23.548)**: documento tipo Secretaría de Hacienda / BNA, "Índices de Distribución de la Coparticipación Federal de Impuestos y Regímenes Especiales de Distribución". Archivo: `data/raw/coeficientes/indices_copa_2018.pdf`, creado el 2 de febrero de 2018 según la metadata del archivo.

### Metodología

Trabajo con las 24 jurisdicciones en un solo corte (no serie temporal). "Aporta" es el % del PBG de cada provincia sobre el PBG total del país en 2024, el año más reciente disponible (dato preliminar en la fuente). "Recibe" es el coeficiente de coparticipación Ley 23.548 de cada provincia (con el ajuste de CABA que explico abajo), sin renormalizar — también explico por qué más abajo. La métrica que uso para compararlos es la diferencia en puntos porcentuales (recibe − aporta): positivo significa que la provincia recibe proporcionalmente más de lo que su peso económico sugeriría, negativo lo contrario.

Script: `scripts/build_coefficients_comparison.py`. Notebook: `notebooks/02_aporte_vs_recibo.ipynb`.

### Supuestos y limitaciones

El documento de coeficientes es de febrero de 2018, no la versión más actual — me di cuenta porque el valor de CABA ahí (3,75%) corresponde al Decreto 194/2016, mientras que el vigente desde 2020 es 1,4%. Corregí a mano solo ese valor; los otros 23 coeficientes no los toqué, porque son la tabla de la Ley 23.548 de 1988 y no cambiaron desde entonces. El 1,4% de CABA lo saqué de una búsqueda web, sin poder verificarlo contra una fuente primaria directa desde este entorno. No modelé acá dos ajustes adicionales que sí importan para el Núcleo 3: la excepción de Córdoba/Santa Fe/San Luis a la detracción del 15% para ANSES (es un descuento sobre la masa coparticipable antes del reparto, no un coeficiente distinto) y Tierra del Fuego (ya viene incluida en la tabla fuente con su propio 0,7%).

Los 24 coeficientes suman ~0,6086, no 1 — es lo esperable, porque el resto (~37,89% Nación + ~1% Fondo ATN) es la porción que no se distribuye a ninguna provincia. Decidí no renormalizar: el coeficiente, tal cual se publica, ya representa el % de la masa coparticipable *total* que recibe cada provincia, conceptualmente equivalente a "% del PBG total del país" (las dos son fracciones de un total nacional, no de un subconjunto). Renormalizar cambiaría la pregunta que responde la comparación — pasaría de "qué % de la masa total le corresponde" a "qué % de lo que efectivamente se reparte entre provincias" — y no es lo que quería medir. Como consecuencia, "% PBG" y "% coparticipación" no son la misma torta: son fracciones de dos totales nacionales distintos, así que la diferencia sirve como indicador comparativo de orden de magnitud (útil para el ranking), no como una relación exacta uno a uno.

El PBG como proxy del aporte tributario tiene un problema conocido: mide dónde se *genera* la actividad económica, no dónde se *paga* el impuesto. Las empresas grandes con operaciones en todo el país suelen tener domicilio fiscal en CABA, así que buena parte de lo generado en otras provincias termina contabilizado como si fuera de CABA. Esto probablemente infla el aporte "real" de CABA y subestima el de provincias productivas como Córdoba — lo dejo señalado también en el notebook.

---

## Núcleo 3 — Simulador de sensibilidad

No tiene fuentes propias: reutiliza los coeficientes de coparticipación del Núcleo 2 (`scripts/coeficientes_ley23548.py`) y, para el caso de validación, la coparticipación nominal 2025 ya calculada en el Núcleo 1.

### Metodología

El corazón es `simular_shock(variacion_pct_recaudacion, recaudacion_base, coeficientes_por_provincia)`, en `scripts/simulator.py`, con 9 tests automáticos en `scripts/test_simulator.py` (`pytest scripts/test_simulator.py`). `recaudacion_base` es la masa coparticipable TOTAL de referencia (incluye lo que retiene Nación y el Fondo ATN, no solo lo que reciben las provincias) — no es la recaudación tributaria nacional total, que incluye impuestos no coparticipables.

El simulador usa únicamente los coeficientes de Ley 23.548: no incluye la compensación del Consenso Fiscal (Ley 27.429) porque es un monto fijado en pesos, no una proporción de la recaudación corriente, así que no tiene sentido que responda a un shock porcentual. Esto genera una diferencia intencional con la definición de "coparticipación" del Núcleo 1, que sí suma Consenso Fiscal. Tampoco modela los adelantos de coparticipación (como el Decreto 219/2026): son anticipos a cuenta de coparticipación futura, no cambian el coeficiente de reparto de nadie. Y el shock se aplica de forma proporcional y simultánea a toda la masa coparticipable — no distingue por tipo de impuesto (IVA, Ganancias, etc.), aunque en la práctica una caída de recaudación puede pegarle distinto a cada uno.

La interfaz interactiva es un slider de `ipywidgets` dentro del notebook, en vez de una app Streamlit aparte, para que todo el proyecto siga siendo reproducible desde los notebooks sin depender de un servidor corriendo aparte. También armé una versión standalone en JavaScript (sin ninguna dependencia de Python) para poder moverla desde el navegador sin abrir Jupyter — reproduce exactamente el mismo cálculo que la sección de validación de acá abajo: misma `recaudacion_base` y coparticipación actual de Córdoba, ambas escaladas a un cuatrimestre, con el impacto expresado como % de lo que Córdoba recibe hoy. Las constantes que usa esa página son una foto de los datos 2025 ya procesados en este repositorio al momento de publicarla — si en algún momento incorporo años posteriores, hay que recalcularlas y republicar la página a mano, no se actualizan solas.

Además del gráfico en pesos absolutos (donde Buenos Aires domina solo por tener el coeficiente más grande), agregué una vista con el parámetro `coparticipacion_actual_por_provincia` de `simular_shock` — antes sin usar en este notebook — que muestra el impacto como % de lo que cada provincia recibe hoy. Ahí 23 de las 24 jurisdicciones caen en una banda angosta (~8,0%-8,9%), muy cerca de la variación % del shock, porque el reparto es proporcional al coeficiente de cada una. La excepción es CABA (~11,5%), y no es un supuesto raro del simulador: es un eco de que su coeficiente lo corregí a mano en el Núcleo 2 (1,4% en vez del 3,75% del documento fuente), así que ya no guarda con lo que CABA recibió en 2025 la misma proporción que sí mantienen las demás provincias.

También armé un GIF de demo (`scripts/build_demo_gif.py`, no forma parte del pipeline de datos) para el README, mostrando el simulador recorriendo distintos escenarios, con el impacto expresado como % de los ingresos corrientes totales de Córdoba (Núcleo 4) — la lectura relativa, no la absoluta en pesos.

Notebook: `notebooks/03_simulador_sensibilidad.ipynb`.

### Supuestos y limitaciones

Para tener algún punto de referencia externo, contrasté el modelo contra una cifra pública que circuló a comienzos de 2026: una caída de recaudación del primer cuatrimestre reportada por IARAF ($5,1 billones de caída total, $1,4 billones menos de coparticipación). No conseguí una cifra oficial de masa coparticipable de referencia para ese período específico (misma restricción de acceso a internet del entorno), así que armé el contraste así: estimé una `recaudacion_base` para un cuatrimestre a partir de datos propios (la coparticipación nominal 2025 del Núcleo 1, dividida por 3 para aproximar 4 meses, y "grosseada" dividiendo por la suma de los 24 coeficientes de provincias, 0,5876, para llegar a la masa coparticipable total); después calculé qué variación % de recaudación, aplicada a esa base, reproduce exactamente el impacto de $1,4 billones reportado: -8,6%.

Como chequeo de consistencia — no forzado por el cálculo anterior — miré qué fracción de la caída *total* de recaudación ($5,1 billones) representa la masa coparticipable afectada: ~46,7%, dentro del rango que se suele citar para la proporción de la recaudación nacional que es coparticipable en Argentina (~40-50%). Es una señal razonable de que la `recaudacion_base` que estimé y la cifra pública son consistentes entre sí, pero quiero ser preciso sobre qué es esto: es una calibración y un chequeo de consistencia interna, no una predicción contrastada contra una tercera fuente independiente de recaudación coparticipable real de ese período — esa fuente no la conseguí. Para este escenario, el impacto estimado en Córdoba es de -$120.073 millones.

---

## Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba

### Fuentes

- **Ingresos corrientes de Córdoba (proxy), 2015-2025**: recaudación administrada por la Dirección General de Rentas de Córdoba, que me pasaron directamente (probablemente republicada por DGEyC Córdoba, sin URL pública que haya podido verificar desde este entorno). Archivo: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`, hoja `Serie_Mensual`. El nombre real del archivo no coincidía con el que esperaba (`dgeyc_ingresos_cordoba.xlsx`) — confirmé que era la fuente correcta antes de usarlo.
- También reutiliza la coparticipación nominal de Córdoba del Núcleo 1 y el simulador del Núcleo 3.

### Metodología

Uso como "ingresos corrientes totales" la fila "Total" del archivo (Recursos de Origen Provincial + Recursos de Origen Nacional, administrados por la Dirección General de Rentas) — no es la única definición posible, ver la limitación de alcance más abajo. Para el numerador del ratio uso `monto_nominal` (no `monto_real_base2016`) de Córdoba del Núcleo 1: un ratio de "% de los ingresos que es coparticipación" necesita magnitudes del mismo tipo, nominal sobre nominal y del mismo año — usar la serie deflactada contra un denominador nominal metería el efecto de la inflación en el ratio sin ningún motivo.

El rango queda en 2015-2025 (11 años), la intersección entre lo que cubre el archivo de ingresos (desde enero de 2015) y el Núcleo 1 (hasta 2025); 2026 queda afuera del ratio anual por ser un año calendario incompleto en ambas fuentes. Para el indicador de sensibilidad reutilizo `scripts/simulator.py::simular_shock`: estimo la masa coparticipable base de 2025 igual que en la validación del Núcleo 3 (coparticipación nominal recibida por las 24 jurisdicciones en 2025, dividida por la suma de sus 24 coeficientes), y divido el impacto en pesos resultante para Córdoba por sus ingresos corrientes totales de 2025 para obtener el impacto en % del ingreso provincial total.

Script: `scripts/build_dependencia_fiscal.py`. Notebook: `notebooks/04_dependencia_fiscal_cordoba.ipynb`.

### Supuestos y limitaciones

La propia nota al pie del archivo fuente aclara que la fila "Total" excluye lo recaudado por otros organismos públicos provinciales — por ejemplo, el Fondo para el Desarrollo Energético Provincial que recauda EPEC. Así que esto no es el ingreso corriente total del sector público provincial en sentido estricto de ejecución presupuestaria, sino la mejor proxy que tengo disponible; lo usé así después de confirmarlo con la fuente.

El encabezado de las hojas del archivo dice "Millones de pesos corrientes", pero está mal: los valores de celda están en pesos corrientes, no en millones. Lo verifiqué cruzando la fila "Coparticipación Federal de Impuestos (CFI)" del archivo: la suma de los 12 meses de 2015 da $23.709.952.851, contra $23.673.039.600 del `monto_nominal` de Córdoba 2015 que ya había calculado en el Núcleo 1 a partir de una fuente independiente (Secretaría de Hacienda) — una diferencia de apenas 0,16%, que confirma la unidad real y de paso valida cruzadamente el Núcleo 1 con una fuente distinta. Esa validación cruzada solo la hice para 2015; no verifiqué que las dos fuentes sigan coincidiendo en los 10 años restantes.

También encontré un problema de formato menor: la columna de diciembre de 2023 en `Serie_Mensual` está guardada como texto ("dic-23") en vez de fecha, a diferencia de todas las demás columnas — `scripts/build_dependencia_fiscal.py` la parsea aparte.

Y, como en el Núcleo 3, el indicador de sensibilidad es una simplificación de primera ronda: no modela ninguna respuesta de política provincial (ajuste de gasto, recaudación propia adicional, endeudamiento) ante una caída de ingresos.

---

## Apéndice: fuentes evaluadas y descartadas para el Núcleo 1

Cuando el Núcleo 1 todavía estaba acotado a 2016-2025 (antes de conseguir la base de Ferreres/Norte y Sur), evalué y descarté estas fuentes para cubrir 2003-2015. Las dejo acá como registro, aunque ya no son relevantes para el alcance actual:

- **IPC INDEC "histórico" (`sh_ipc_12_16.xls`)**: pese al nombre, solo cubre abril-noviembre 2016 — no suma cobertura hacia atrás.
- **Series del Banco Mundial vía FRED (`DDOE01ARA086NWDB`, `DDOE02ARA086NWDB`)**: cubren 1960-2014 y 1960-2015. El tramo 2003-2013 es internamente coherente, pero 2014 y 2015 muestran el índice bajando respecto de 2013 (134,7 → 105,5 → 120,6), algo económicamente imposible dado que Argentina tuvo inflación alta y positiva esos años — parece un empalme mal hecho en el propio dataset del Banco Mundial, no un error mío al descargarlo, y coincide justo con el período de descrédito del IPC oficial.
- **Serie FRED `FPCPITOTLZGARG`** (inflación anual %, Banco Mundial): solo cubre 2018-2024, no aporta al hueco 2007-2015.
