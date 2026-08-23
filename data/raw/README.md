# data/raw — trazabilidad de fuentes

Esta carpeta contiene datos descargados sin procesar. **Nunca se editan a mano.** Cada
subcarpeta corresponde a una fuente y tiene su propio `_metadata.json` con el origen
exacto de cada archivo.

## Estado de las fuentes (Núcleo 1)

| Fuente | Carpeta | Estado |
|---|---|---|
| Coparticipación / RON — Secretaría de Hacienda | `data/raw/coparticipacion/` | **Datos reales incorporados** (ver detalle abajo) |
| IPC — INDEC | `data/raw/ipc/` | **Datos reales incorporados** (ver detalle abajo) |

### Cómo se obtuvieron

`scripts/download_coparticipacion.py` y `scripts/download_ipc.py` existen y están
documentados, pero **no pudieron correrse desde el entorno de desarrollo**: no tiene
acceso de salida (egress) a `argentina.gob.ar`, `indec.gob.ar` ni a la mayoría de los
dominios externos (política de red de la sesión). En su lugar, el usuario descargó los
archivos manualmente desde su propio navegador y los subió al chat, desde donde se
copiaron a esta carpeta. Cada `_metadata.json` documenta esto explícitamente
(`obtenido_por`, `motivo`).

Si en el futuro se corre este proyecto desde un entorno con acceso a internet, los
scripts de descarga deberían poder reemplazar este paso manual — pero no se probaron
end-to-end todavía, así que conviene revisar su salida la primera vez que se usen.

### Coparticipación federal / Recursos de Origen Nacional (RON)

- **Organismo**: Secretaría de Hacienda, Ministerio de Economía de la Nación.
- **URL de origen**: <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
- **Archivo usado**: `coparticipacion/serie_ron_2003_2025.csv` — 2003 a 2025, un registro
  por provincia/año/concepto (20 conceptos distintos de RON, no solo coparticipación
  Ley 23.548). El detalle de qué conceptos se usan para este núcleo está en
  `docs/methodology.md`.
- **Contexto normativo**: distribución automática y diaria bajo el régimen de la Ley
  23.548 (1988) y modificaciones posteriores (p. ej., compensación por el Consenso
  Fiscal desde 2018). El archivo agrega esa distribución diaria a nivel anual.

### Índice de Precios al Consumidor (IPC)

- **Organismo**: INDEC.
- **Archivo usado**: `ipc/serie_ipc_divisiones.csv` — Region="Nacional", Nivel General,
  cobertura mensual diciembre 2016 en adelante.
- **Nota importante**: el IPC nacional oficial de Argentina **no tiene cobertura
  confiable antes de diciembre 2016** con las fuentes que se pudieron conseguir (ver
  `docs/methodology.md`, sección "Supuestos y limitaciones", para el detalle de por qué
  se descartaron varias fuentes alternativas). Por eso el Núcleo 1 se acotó a
  **2016-2025**.

## Otros archivos en esta carpeta (no usados en el Núcleo 1)

Se conservan como referencia para núcleos futuros o para revisar la decisión de acotar
el alcance temporal. Cada uno está documentado en el `_metadata.json` de su carpeta con
el motivo puntual por el que se descartó (insuficiente cobertura temporal, o -- en el
caso de las series del Banco Mundial vía FRED -- una inconsistencia económica detectada
en los propios datos, no un error de descarga).
