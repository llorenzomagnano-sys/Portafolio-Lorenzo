# Coparticipación federal: el caso de Córdoba

[![CI](https://github.com/llorenzomagnano-sys/Portafolio-Lorenzo/actions/workflows/ci.yml/badge.svg)](https://github.com/llorenzomagnano-sys/Portafolio-Lorenzo/actions/workflows/ci.yml)

Análisis de datos del régimen de coparticipación federal de impuestos en Argentina, con foco en la provincia de Córdoba.

## Sobre este proyecto

La coparticipación federal es uno de esos temas que aparecen todo el tiempo en la agenda económica argentina — un gobernador reclamando por su provincia, un cambio de coeficientes generando discusión — pero que casi nunca se explican con números concretos y trazables. Armé este repositorio para entender mejor cómo funciona el reparto de la Ley 23.548 en la práctica, tomando a Córdoba como caso de estudio en vez de quedarme en generalidades sobre todo el país.

Lo organicé en cuatro preguntas que se van encadenando: cómo evolucionó en el tiempo la coparticipación real que recibe Córdoba, si la provincia recibe en proporción a lo que aporta, qué tan sensible es ese reparto a un shock de recaudación, y qué tan dependiente es el presupuesto provincial de esa plata. De dónde sale cada dato, qué supuestos tomé y dónde flaquean queda documentado a la vista en vez de escondido en un anexo — es la parte del trabajo que más tiempo me llevó.

## Principales hallazgos

- **Serie histórica (2003-2025)**: la coparticipación real recibida por Córdoba (pesos constantes de 2016) pasó de $13.421 millones en 2003 a un máximo de $49.955 millones en 2022, y cerró 2025 en $42.205 millones, 3,1 veces el nivel de 2003. En términos relativos (indexado a 2003=100), sin embargo, Córdoba creció prácticamente igual que Buenos Aires, Santa Fe y Mendoza (entre 306 y 325 puntos en 2025): el salto responde a la dinámica agregada del régimen, no a algo particular de cada provincia.
- **Aporte vs. recibo por provincia**: comparando la porción de cada provincia en lo que se reparte entre provincias con su peso en el PBG, Córdoba queda prácticamente empatada: recibe el 8,58% del reparto y representa el 8,56% del PBG. Las que quedan claramente por debajo son CABA (−17,5 pp), Buenos Aires (−10,6 pp) y Neuquén (−2,7 pp); las que más reciben en relación a su PBG, Chaco, Formosa y Tucumán (cerca de +3 pp cada una).
- **Simulador de sensibilidad**: calibrado con la caída de recaudación de comienzos de 2026 que dio a conocer IARAF, una baja de ~8,6% en la recaudación nacional coparticipable le cuesta a Córdoba unos $120.100 millones en un cuatrimestre. Como el reparto es proporcional, todas las provincias pierden el mismo porcentaje de lo que les corresponde; lo que cambia la gravedad del golpe es cuánto depende cada una de la coparticipación (Núcleo 4).
- **Dependencia fiscal de Córdoba (2015-2025)**: la coparticipación pasó de explicar el 36,0% de los ingresos de Córdoba en 2015 a un máximo de 45,2% en 2023-2024, y bajó a 40,4% en 2025. En pesos constantes, la suba se explica sobre todo por la recaudación propia, que cayó un 20% entre 2017 y 2020 y se mantuvo cerca de ese piso hasta 2024, mientras la coparticipación seguía creciendo. Con la dependencia de 2025, una caída del 10% en la recaudación nacional coparticipable reduce los ingresos totales de la provincia en un 4,0%.

## Núcleos de análisis

| Núcleo | Descripción | Notebook |
|---|---|---|
| 1 | Serie histórica de coparticipación (2003-2025) | [`01_serie_historica.ipynb`](notebooks/01_serie_historica.ipynb) |
| 2 | Aporte vs. recibo por provincia | [`02_aporte_vs_recibo.ipynb`](notebooks/02_aporte_vs_recibo.ipynb) |
| 3 | Simulador de sensibilidad | [`03_simulador_sensibilidad.ipynb`](notebooks/03_simulador_sensibilidad.ipynb) |
| 4 | Peso de la coparticipación en las cuentas de Córdoba | [`04_dependencia_fiscal_cordoba.ipynb`](notebooks/04_dependencia_fiscal_cordoba.ipynb) |

La metodología completa — fuentes, supuestos y limitaciones de cada núcleo — está en [`docs/methodology.md`](docs/methodology.md).

### Núcleo 1 — Serie histórica de coparticipación

![Coparticipación real recibida por Córdoba, 2003-2025](output/figures/cordoba_evolucion_real_2003_2025.png)

En niveles absolutos Buenos Aires tapa todo por su tamaño, así que agregué también la misma serie indexada a 2003=100:

![Coparticipación real por provincia, indexada a 2003=100](output/figures/comparativo_provincias_indexado_2003_2025.png)

### Núcleo 2 — Aporte vs. recibo por provincia

![Coparticipación recibida vs. PBG aportado, por provincia](output/figures/aporte_vs_recibo_ranking.png)

### Núcleo 3 — Simulador de sensibilidad

Impacto en pesos del escenario de comienzos de 2026. En porcentaje, todas las provincias pierden lo mismo, porque el reparto es proporcional al coeficiente:

![Impacto de la caída de recaudación del primer cuatrimestre de 2026, por provincia](output/figures/simulador_impacto_1cuatrimestre2026.png)

Demo del simulador recorriendo distintos escenarios de shock, con el impacto como % de los ingresos totales de Córdoba (generada con `scripts/build_demo_gif.py`):

![Demo del simulador mostrando el impacto como % de los ingresos totales de Córdoba](output/figures/simulador_interactivo_demo.gif)

**[Probar el simulador en el navegador →](https://llorenzomagnano-sys.github.io/Portafolio-Lorenzo/simulador/)**: misma fórmula de `simular_shock`, reimplementada en JavaScript en una página estática (`docs/simulador/index.html`). Usa los datos de 2025 de este repositorio; el detalle con las 24 jurisdicciones está en el notebook.

### Núcleo 4 — Peso de la coparticipación en las cuentas de Córdoba

![Coparticipación como % de los ingresos corrientes de Córdoba, 2015-2025](output/figures/dependencia_fiscal_cordoba.png)

El ratio da igual en pesos nominales o reales; para ver por qué se movió hay que mirar los niveles en pesos constantes. La recaudación propia se estancó justo cuando la coparticipación crecía:

![Recaudación propia y coparticipación de Córdoba, en pesos constantes base 2016](output/figures/dependencia_fiscal_cordoba_real.png)

## Simulador interactivo

El Núcleo 3 tiene un simulador interactivo (slider de `ipywidgets`) dentro de `notebooks/03_simulador_sensibilidad.ipynb`, más la versión web linkeada arriba. Elegí `ipywidgets` en vez de una app Streamlit para que todo el proyecto se pudiera reproducir desde los notebooks sin depender de un servidor; la lógica (`scripts/simulator.py`) está separada y sin dependencias de notebook, así que la versión web es solo esa misma fórmula en JavaScript.

## Estructura del repositorio

```
data/raw/          # Datos crudos, tal como se obtuvieron. Nunca se editan a mano.
data/processed/    # Datos limpios, generados por los scripts de scripts/.
scripts/           # Procesamiento de cada núcleo, simulador y tests (simulador + consistencia de datos).
notebooks/         # Un notebook por núcleo temático, con los gráficos e interpretación.
docs/              # Metodología, y el simulador web (docs/simulador/, publicado con GitHub Pages).
output/figures/    # Gráficos exportados (PNG), embebidos en este README y en los notebooks.
run_all.py         # Corre todo el pipeline de procesamiento + notebooks con un solo comando.
```

## Fuentes de datos

| Fuente | Organismo | Núcleo(s) |
|---|---|---|
| [Coparticipación / Recursos de Origen Nacional (RON)](https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron) | Secretaría de Hacienda, Ministerio de Economía de la Nación | 1, 3, 4 |
| [Índice de Precios al Consumidor, 2016-2025](https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv) | INDEC | 1 |
| Índice de Precios al Consumidor, 2003-2015 (archivo propio, sin URL pública verificada) | Fundación Norte y Sur / Orlando J. Ferreres | 1 |
| Producto Bruto Geográfico por provincia (`Jurisdiccion_52sectores.xlsx`, archivo propio) | CEPAL, sobre metodología base de INDEC | 2 |
| Índices de distribución de la coparticipación federal (`indices_copa_2018.pdf`, archivo propio) | Documento tipo Secretaría de Hacienda / BNA | 2, 3, 4 |
| Recaudación provincial (`serie_recaudacion_provincial.xlsx`, archivo propio) | Dirección General de Rentas de Córdoba | 4 |

Ninguna de estas fuentes tiene una licencia restrictiva conocida para este tipo de análisis (son estadísticas públicas o compilaciones a las que ya tenía acceso), pero no todas tienen una URL pública verificada de origen. El detalle de cómo conseguí cada archivo, con qué alcance temporal y qué limitaciones tiene, está en [`data/raw/README.md`](data/raw/README.md) y en [`docs/methodology.md`](docs/methodology.md).

**Atribución**: la serie de precios 2003-2015 usada en el Núcleo 1 se basa en la compilación histórica de series económicas de Argentina realizada por **Orlando J. Ferreres** para la **Fundación Norte y Sur**, conocido por su obra de referencia *"Dos siglos de Economía Argentina"*. La uso acá solo como insumo — un índice de precios empalmado con fuentes oficiales, con el detalle en la metodología — y no reclamo ninguna autoría sobre la compilación original.

## Cómo correr el proyecto de punta a punta

```bash
# Clonar el repositorio
git clone https://github.com/llorenzomagnano-sys/Portafolio-Lorenzo.git
cd Portafolio-Lorenzo

# Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Correr todo el pipeline: procesamiento de los 4 núcleos + tests + regeneración
# de los 4 notebooks (con sus gráficos). data/raw/ ya viene poblada en el repo.
python run_all.py
```

Para explorar de forma interactiva en vez de solo regenerar: `jupyter notebook` y abrir cualquiera de los notebooks de `notebooks/`. Para correr solo los tests (simulador y chequeos de consistencia de los datos procesados): `pytest scripts/`.

## Limitaciones metodológicas (resumen)

Cada una de estas se documenta en detalle, con la decisión tomada y su razón, en [`docs/methodology.md`](docs/methodology.md):

- **Núcleo 1** no llega a 1990 (la idea original) porque no existe una fuente de montos nominales de coparticipación por provincia para 1990-2002; el rango quedó en 2003-2025. El tramo 2003-2016 depende de un IPC empalmado con una fuente privada (Ferreres/Norte y Sur), porque el IPC oficial de 2007-2015 quedó desacreditado por la intervención del INDEC y el actual recién arranca en diciembre de 2016. Además, la serie de Hacienda que uso refleja lo que Nación informa haber transferido: desde 2018 supera en 14-17% a la coparticipación que registra la propia Córdoba (ver Núcleo 4).
- **Núcleo 2** usa el PBG como proxy del aporte tributario real, que tiene un problema de atribución geográfica conocido: las empresas suelen tributar donde tienen sede fiscal, no donde generan la actividad económica. Eso probablemente infla el aporte de CABA y subestima el de provincias productivas como Córdoba.
- **Núcleo 3** es un modelo lineal y proporcional, calibrado con una sola cifra pública (un cuatrimestre de recaudación). Es una calculadora de escenarios, no un modelo validado contra una serie independiente.
- **Núcleo 4** usa como proxy de "ingresos corrientes totales" de Córdoba la recaudación administrada por la Dirección General de Rentas, que excluye lo recaudado por otros organismos provinciales como EPEC. Desde 2018, además, la coparticipación que informa Nación para Córdoba supera en 14-17% a la que registra la provincia, y no identifiqué por qué; el ratio usa solo la fuente provincial. El indicador de sensibilidad es una simplificación de primera ronda: no modela ninguna respuesta de política provincial ante una caída de ingresos.

## Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles. Los datos de `data/raw/` conservan la licencia/términos de sus fuentes originales (estadísticas públicas u organismos oficiales); no se redistribuyen bajo la licencia MIT del código.

## Autor

**Lorenzo Magnano**

El código lo escribí con asistencia de herramientas de IA. Las preguntas, la elección y el control de las fuentes y los criterios metodológicos son míos.
