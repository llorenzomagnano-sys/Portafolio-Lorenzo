# Portafolio-Lorenzo

Análisis del régimen de coparticipación federal de impuestos en Argentina, con foco en la provincia de Córdoba.

## Objetivo del proyecto

Este repositorio existe como pieza de portfolio técnico para postular a consultoras de análisis fiscal (perfil IERAL, IARAF). El proyecto aborda el problema económico de la distribución de recursos tributarios entre Nación y provincias bajo el régimen de coparticipación federal, evaluando su evolución histórica, su impacto en las cuentas provinciales y su sensibilidad ante cambios en las reglas de reparto, con aplicación concreta al caso de Córdoba.

## Núcleos de análisis

| Núcleo | Descripción | Estado |
|---|---|---|
| 1 | Serie histórica de coparticipación | completo |
| 2 | Aporte vs. recibo por provincia | completo |
| 3 | Simulador de sensibilidad | completo |
| 4 | Peso de la coparticipación en las cuentas de Córdoba | pendiente |

### Núcleo 1 — Serie histórica de coparticipación (2016-2025)

Muestra la evolución de la coparticipación federal recibida por Córdoba en pesos
constantes, y la compara contra Buenos Aires, Santa Fe y Mendoza. El análisis está
acotado a 2016-2025 por disponibilidad de datos de inflación confiables (ver
[`docs/methodology.md`](docs/methodology.md) para el detalle). Notebook:
[`notebooks/01_serie_historica.ipynb`](notebooks/01_serie_historica.ipynb).

![Coparticipación real recibida por Córdoba, 2016-2025](output/figures/cordoba_evolucion_real_2016_2025.png)

### Núcleo 2 — Aporte vs. recibo por provincia

Compara el peso económico de cada provincia (PBG, 2024) contra lo que recibe por
coparticipación (coeficiente Ley 23.548). Córdoba aporta 8,6% del PBG nacional pero
recibe solo 5,0% de la coparticipación — una brecha de -3,5 puntos porcentuales, la
tercera peor del país después de Buenos Aires y CABA. El análisis documenta
explícitamente la limitación del PBG como proxy del aporte tributario real (ver
[`docs/methodology.md`](docs/methodology.md)). Notebook:
[`notebooks/02_aporte_vs_recibo.ipynb`](notebooks/02_aporte_vs_recibo.ipynb).

![Coparticipación recibida vs. PBG aportado, por provincia](output/figures/aporte_vs_recibo_ranking.png)

### Núcleo 3 — Simulador de sensibilidad

Un simulador (`scripts/simulator.py`, con tests automáticos) que calcula cómo se
reparte entre provincias un shock de recaudación tributaria nacional coparticipable.
Se validó contra la caída de recaudación real del primer cuatrimestre de 2026
reportada por IARAF ($5,1 billones de caída total, $1,4 billones menos de
coparticipación): la variación real implícita (~-8,6%) y la tasa de "coparticipabilidad"
implícita (~46,7%) resultan consistentes con lo esperable, aunque —documentado
explícitamente— es un chequeo de consistencia interna y no una validación contra una
fuente independiente de recaudación coparticipable de 2026. Para ese shock, Córdoba
pierde del orden de $120 mil millones de pesos. Incluye un simulador interactivo
(slider de `ipywidgets`) para explorar otros escenarios. Notebook:
[`notebooks/03_simulador_sensibilidad.ipynb`](notebooks/03_simulador_sensibilidad.ipynb).

![Impacto de la caída de recaudación del primer cuatrimestre de 2026, por provincia](output/figures/simulador_validacion_1cuatrimestre2026.png)

## Estructura del repositorio

```
data/raw/          # Datos descargados sin procesar. Nunca se editan a mano.
data/processed/    # Datos limpios, listos para análisis.
scripts/           # Código reutilizable: descarga, limpieza, cálculo.
notebooks/         # Notebooks exploratorios, uno por núcleo temático.
docs/              # Metodología, supuestos, fuentes.
output/figures/    # Gráficos exportados.
```

## Fuentes de datos

- **Secretaría de Hacienda / Ministerio de Economía de la Nación** — coparticipación /
  Recursos de Origen Nacional por provincia (usada en el Núcleo 1).
- **INDEC** — Índice de Precios al Consumidor, usado como deflactor (Núcleo 1).
- **CEPAL** (metodología base INDEC) — Producto Bruto Geográfico por provincia (Núcleo 2).
- Documento tipo Secretaría de Hacienda / BNA — coeficientes de coparticipación Ley 23.548 (Núcleo 2).
- datos.gob.ar (en construcción)
- DGEyC Córdoba (Dirección General de Estadística y Censos de la Provincia de Córdoba) — (en construcción)

Detalle completo de trazabilidad de cada fuente en [`data/raw/README.md`](data/raw/README.md).

## Cómo correr el proyecto

```bash
# Clonar el repositorio
git clone https://github.com/llorenzomagnano-sys/Portafolio-Lorenzo.git
cd Portafolio-Lorenzo

# Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar Jupyter para explorar los notebooks
jupyter notebook

# Correr los tests del simulador (Núcleo 3)
pytest scripts/test_simulator.py
```

## Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## Autor

**[Lorenzo Magnano]**
[LinkedIn: Lorenzo Magnano]
