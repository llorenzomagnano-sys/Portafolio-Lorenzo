# Portafolio-Lorenzo

Análisis del régimen de coparticipación federal de impuestos en Argentina, con foco en la provincia de Córdoba.

## Objetivo del proyecto

Este repositorio existe como pieza de portfolio técnico para postular a consultoras de análisis fiscal (perfil IERAL, IARAF). El proyecto aborda el problema económico de la distribución de recursos tributarios entre Nación y provincias bajo el régimen de coparticipación federal, evaluando su evolución histórica, su impacto en las cuentas provinciales y su sensibilidad ante cambios en las reglas de reparto, con aplicación concreta al caso de Córdoba.

## Núcleos de análisis

| Núcleo | Descripción | Estado |
|---|---|---|
| 1 | Serie histórica de coparticipación | pendiente |
| 2 | Aporte vs. recibo por provincia | pendiente |
| 3 | Simulador de sensibilidad | pendiente |
| 4 | Peso de la coparticipación en las cuentas de Córdoba | pendiente |

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

(en construcción)

- Secretaría de Hacienda / Ministerio de Economía de la Nación
- datos.gob.ar
- INDEC
- DGEyC Córdoba (Dirección General de Estadística y Censos de la Provincia de Córdoba)

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
```

## Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## Autor

**[Nombre completo]**
[LinkedIn / contacto]
