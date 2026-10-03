# Metodología

Estas son las notas técnicas del proyecto: de dónde sale cada dato, qué decisiones tomé al procesarlo y dónde el análisis tiene puntos flojos. El resumen de hallazgos y las instrucciones para correr todo están en el [README](../README.md) — acá va el detalle que sostiene cada número.

Va organizado en una sección por núcleo (fuentes, metodología, supuestos y limitaciones), más un apéndice al final con fuentes que evalué y descarté para el Núcleo 1.

## Cómo conseguí los datos

Todos los archivos de `data/raw/` los descargué o los conseguí a mano y los versioné tal cual, así el proyecto se reproduce sin acceso a internet. La trazabilidad de cada archivo (de dónde salió, qué alcance tiene, por qué lo usé o lo descarté) está en [`data/raw/README.md`](../data/raw/README.md).

---

## Núcleo 1 — Serie histórica de coparticipación (2003-2025)

### Fuentes

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de Hacienda, Ministerio de Economía de la Nación. <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>. Archivo: `data/raw/coparticipacion/serie_ron_2003_2025.csv` (2003-2025).
- **IPC 2016-2025**: INDEC. <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>. Archivo: `data/raw/ipc/serie_ipc_divisiones.csv` (mensual, desde dic-2016).
- **IPC 2003-2015**: Fundación Norte y Sur / Orlando J. Ferreres, conseguida en forma directa (sin URL pública verificada). Archivo: `data/raw/ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`, hoja `IPC `. Es la compilación histórica de series económicas de Argentina que hizo Ferreres para la Fundación Norte y Sur (conocido por *"Dos siglos de Economía Argentina"*) — la uso como insumo de análisis, sin reclamar autoría sobre la compilación.

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

Trabajo con las 24 jurisdicciones en un solo corte (no serie temporal). "Aporta" es el % del PBG de cada provincia sobre el PBG total del país en 2024, el año más reciente disponible (dato preliminar en la fuente). "Recibe" es la porción de cada provincia en lo que se reparte **entre provincias**: su coeficiente de Ley 23.548 (con el ajuste de CABA que explico abajo) dividido por la suma de los 24 coeficientes. La métrica es la diferencia en puntos porcentuales (recibe − aporta): positivo significa que la provincia recibe una porción del reparto mayor que su peso económico, negativo lo contrario.

Script: `scripts/build_coefficients_comparison.py`. Notebook: `notebooks/02_aporte_vs_recibo.ipynb`.

### Supuestos y limitaciones

El documento de coeficientes es de febrero de 2018, no la versión más actual: el valor de CABA ahí (3,75%) corresponde al Decreto 194/2016. Lo reemplacé por 1,4%, el coeficiente del régimen automático vigente desde la Ley 27.606 (2020); los otros 23 coeficientes no los toqué, porque son la tabla de la Ley 23.548 de 1988 y no cambiaron. Hay un detalle más: en diciembre de 2022 la Corte Suprema dictó una cautelar que obliga a Nación a transferirle a CABA un 1,55% adicional (2,95% en total), y en 2025 Nación y la Ciudad acordaron cómo cumplirla. Ese 1,55% se paga por fuera del régimen automático, así que mantengo el 1,4% para ser coherente con la serie de transferencias del Núcleo 1, y en el notebook muestro cómo cambia el resultado con 2,95% (la brecha de CABA pasa de −17,5 a −15,0 pp; la de Córdoba, de +0,01 a −0,2 pp). Tampoco modelé la excepción de Córdoba, Santa Fe y San Luis a la detracción del 15% para ANSES (es un descuento sobre la masa antes del reparto, no un coeficiente distinto).

Los 24 coeficientes suman ~0,59, no 1: el resto es lo que retienen Nación y el Fondo ATN. Por eso los renormalizo antes de compararlos con el PBG, que suma 100% entre provincias. En una primera versión los comparé sin renormalizar y el resultado era engañoso: como el coeficiente crudo es una fracción de un total más grande, todas las provincias grandes quedaban con brechas negativas por el solo hecho de ser grandes (Córdoba aparecía con −3,5 pp, cuando su porción del reparto, 8,58%, es prácticamente igual a su peso en el PBG, 8,56%). Renormalizado, el ranking mide cómo se reparte entre provincias, que es la pregunta del núcleo; cuánto se queda Nación es otra pregunta.

El PBG como proxy del aporte tributario tiene un problema conocido: mide dónde se *genera* la actividad económica, no dónde se *paga* el impuesto. Las empresas grandes con operaciones en todo el país suelen tener domicilio fiscal en CABA, así que en las estadísticas de recaudación por jurisdicción buena parte de lo generado en otras provincias figura como pagado en CABA. Si usara esa recaudación en vez del PBG, CABA aparecería aportando todavía más y provincias productivas como Córdoba, menos. El PBG está más cerca de dónde se genera la actividad, pero no es una medición directa de lo que tributa cada provincia.

---

## Núcleo 3 — Simulador de sensibilidad

No tiene fuentes propias: reutiliza los coeficientes de coparticipación del Núcleo 2 (`scripts/coeficientes_ley23548.py`) y, para calibrar el escenario de referencia, la coparticipación nominal 2025 del Núcleo 1.

### Metodología

El corazón es `simular_shock(variacion_pct_recaudacion, recaudacion_base, coeficientes_por_provincia)`, en `scripts/simulator.py`, con 9 tests automáticos en `scripts/test_simulator.py` (`pytest scripts/test_simulator.py`). `recaudacion_base` es la masa coparticipable TOTAL de referencia (incluye lo que retiene Nación y el Fondo ATN, no solo lo que reciben las provincias); no es la recaudación tributaria nacional total, que incluye impuestos no coparticipables.

Es un modelo deliberadamente simple: el impacto en cada provincia es el shock multiplicado por la masa y por su coeficiente. Una consecuencia directa es que, en porcentaje de lo que le corresponde por coeficiente, todas las provincias pierden exactamente lo mismo. En una primera versión mostré además el impacto como % de lo que cada provincia efectivamente cobró en 2025, y aparecían diferencias (entre 8,0% y 8,9%, y 11,5% para CABA) que presenté como resultado. Las saqué: no reflejan exposición distinta, solo que lo cobrado en 2025 no sigue exactamente los coeficientes legales (la compensación del Consenso Fiscal se reparte con otro criterio, CABA tiene su propio régimen). Lo que sí diferencia la gravedad del golpe entre provincias es cuánto depende cada una de la coparticipación, que es el Núcleo 4.

El simulador usa únicamente los coeficientes de Ley 23.548: no incluye la compensación del Consenso Fiscal (Ley 27.429) porque es un monto fijado en pesos, no una proporción de la recaudación corriente. Tampoco modela los adelantos de coparticipación (como el Decreto 219/2026), que son anticipos a cuenta y no cambian el coeficiente de nadie. Y el shock se aplica de forma proporcional a toda la masa coparticipable, sin distinguir por impuesto (IVA, Ganancias, etc.), aunque en la práctica una caída de recaudación puede pegarle distinto a cada uno.

La interfaz interactiva del notebook es un slider de `ipywidgets`, para que todo siga siendo reproducible desde los notebooks sin un servidor aparte. Para poder usarlo sin instalar nada armé además una página estática (`docs/simulador/index.html`, publicada con GitHub Pages) que reimplementa la misma fórmula en JavaScript. Usa la misma calibración que el indicador de sensibilidad del Núcleo 4 (masa coparticipable 2025 calibrada con la coparticipación que registra el archivo provincial) y muestra el impacto en pesos y como % de los ingresos totales de Córdoba de 2025. Sus constantes son una foto de los datos 2025 de este repositorio: si incorporo años nuevos hay que recalcularlas a mano. El GIF del README (`scripts/build_demo_gif.py`, fuera del pipeline de datos) usa la misma calibración.

Notebook: `notebooks/03_simulador_sensibilidad.ipynb`.

### Supuestos y limitaciones

Para tener un escenario de referencia usé una cifra pública de comienzos de 2026: la caída de recaudación del primer cuatrimestre que reportó IARAF ($5,1 billones de caída total, $1,4 billones menos de coparticipación). No encontré una cifra oficial de masa coparticipable para ese período, así que estimé una `recaudacion_base` de un cuatrimestre con datos propios (la coparticipación nominal 2025 del Núcleo 1, dividida por 3 y dividida por la suma de los 24 coeficientes, 0,5876, para llegar a la masa total) y calculé qué variación % reproduce exactamente los $1,4 billones: −8,6%.

Eso es una calibración, no una validación. El único chequeo que no viene forzado por el cálculo es que la masa coparticipable afectada representa ~46,7% de la caída total de recaudación, dentro del rango que suele citarse para la parte coparticipable de la recaudación nacional (~40-50%). Es una señal de consistencia, no una comparación contra una fuente independiente. Para ese escenario, el impacto en Córdoba es de unos $120.100 millones en el cuatrimestre.

---

## Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba

### Fuentes

- **Recaudación de Córdoba, 2015-2025**: recaudación administrada por la Dirección General de Rentas de Córdoba (probablemente republicada por la Dirección General de Estadística y Censos; no encontré una URL pública estable del archivo). Archivo: `data/raw/ingresos_cordoba/serie_recaudacion_provincial.xlsx`, hoja `Serie_Mensual`, mensual desde enero de 2015.
- Para control, la coparticipación de Córdoba de la serie RON del Núcleo 1. También reutiliza el simulador del Núcleo 3.

### Metodología

Todo el ratio sale de un solo archivo. Leo tres filas por su código: el **Total** (1, recursos de origen provincial + recursos de origen nacional), que uso como proxy de ingresos corrientes totales; los **Recursos de Origen Provincial** (1.1), que son la recaudación propia; y la **Coparticipación Federal de Impuestos** (1.2.1: Ley 23.548 + compensación y bono del Consenso Fiscal). El ratio de dependencia es 1.2.1 / 1.

En la primera versión del núcleo usé como numerador la coparticipación de la serie nacional (Núcleo 1) y como denominador el total de este archivo. Fue un error: las dos fuentes coinciden en 2015-2017, pero desde 2018 la serie nacional registra entre un 14% y un 17% más que el archivo provincial, así que el numerador dejaba de ser parte del denominador y el ratio quedaba inflado unos 6 puntos (llegaba a 51,6% cuando con una sola fuente el máximo es 45,2%). La comparación entre las dos queda como columna de control en el CSV (`coparticipacion_ron_pesos`, `diferencia_ron_vs_provincia`) y como sección propia en el notebook. No identifiqué la causa de la diferencia; puede ser un criterio de registro distinto o montos que Nación informa como transferidos pero que se retienen o compensan antes de llegar a la provincia.

El ratio da lo mismo en pesos nominales o reales, porque el deflactor se cancela en la división. Para ver por qué se mueve, en cambio, hacen falta los niveles en pesos constantes (base 2016, mismo IPC empalmado que el Núcleo 1, `load_ipc_empalmado`; `real = nominal × (ipc_2016 / ipc_año)`) del total, de la recaudación propia y de la coparticipación. Entre 2015 y 2025 la coparticipación creció un 25,0% real y la recaudación propia un 16,8%, pero la recaudación propia cayó un 20% entre 2017 y 2020 y no recuperó ese nivel hasta 2025. Eso, más que el crecimiento de la coparticipación, es lo que llevó el ratio de 36,0% (2015) a 45,2% (2023-2024); en 2025 la recaudación propia se recuperó y el ratio bajó a 40,4%.

Para el indicador de sensibilidad reutilizo `scripts/simulator.py::simular_shock`. La masa coparticipable de referencia la calibro para que el coeficiente de Córdoba reproduzca la coparticipación que registra el archivo provincial en 2025 (`base_calibrada_cordoba`), y divido el impacto en pesos por los ingresos totales de 2025. Así impacto y denominador salen de la misma fuente, y el resultado es, por construcción, el shock multiplicado por el ratio de 2025: una caída del 10% en la recaudación coparticipable reduce los ingresos totales de Córdoba en un 4,0%. Queda en pesos nominales de 2025 porque es un escenario puntual, no una serie.

Script: `scripts/build_dependencia_fiscal.py`. Notebook: `notebooks/04_dependencia_fiscal_cordoba.ipynb`.

### Supuestos y limitaciones

La nota al pie del archivo aclara que el Total excluye lo recaudado por otros organismos públicos provinciales, por ejemplo el Fondo para el Desarrollo Energético Provincial que recauda EPEC. No es el ingreso corriente total del sector público provincial en sentido estricto de ejecución presupuestaria, sino la mejor proxy que tengo; con esa recaudación incluida, el ratio sería algo menor.

El encabezado de las hojas dice "Millones de pesos corrientes", pero los valores están en pesos corrientes. Lo verifiqué con la fila de coparticipación: en 2015-2017 coincide con la serie de Hacienda del Núcleo 1, expresada en pesos, con diferencias menores al 0,2%.

La columna de diciembre de 2023 en `Serie_Mensual` está guardada como texto ("dic-23") en vez de fecha, a diferencia de las demás; el script la parsea aparte.

Y, como en el Núcleo 3, el indicador de sensibilidad es una simplificación de primera ronda: no modela respuestas de política provincial (ajuste de gasto, recaudación propia adicional, endeudamiento) ante una caída de ingresos.

---

## Apéndice: fuentes evaluadas y descartadas para el Núcleo 1

Cuando el Núcleo 1 todavía estaba acotado a 2016-2025 (antes de conseguir la base de Ferreres/Norte y Sur), evalué y descarté estas fuentes para cubrir 2003-2015. Las series del Banco Mundial no se conservan en el repositorio; las dejo acá como registro, aunque ya no son relevantes para el alcance actual:

- **IPC INDEC "histórico" (`sh_ipc_12_16.xls`)**: pese al nombre, solo cubre abril-noviembre 2016 — no suma cobertura hacia atrás.
- **Series del Banco Mundial vía FRED (`DDOE01ARA086NWDB`, `DDOE02ARA086NWDB`)**: cubren 1960-2014 y 1960-2015. El tramo 2003-2013 es internamente coherente, pero 2014 y 2015 muestran el índice bajando respecto de 2013 (134,7 → 105,5 → 120,6), algo económicamente imposible dado que Argentina tuvo inflación alta y positiva esos años — parece un empalme mal hecho en el propio dataset del Banco Mundial, no un error mío al descargarlo, y coincide justo con el período de descrédito del IPC oficial.
- **Serie FRED `FPCPITOTLZGARG`** (inflación anual %, Banco Mundial): solo cubre 2018-2024, no aporta al hueco 2007-2015.
