# data/raw — trazabilidad de fuentes

Esta carpeta contiene datos descargados sin procesar. **Nunca se editan a mano.** Cada
subcarpeta corresponde a una fuente y se genera con el script de descarga
correspondiente (ver `scripts/`), que además escribe un `_metadata.json` con la URL de
origen exacta y la fecha/hora de acceso (UTC) de esa corrida.

## Estado de las fuentes (Núcleo 1)

| Fuente | Script | Carpeta | Estado |
|---|---|---|---|
| Coparticipación / RON — Secretaría de Hacienda | `scripts/download_coparticipacion.py` | `data/raw/coparticipacion/` | **Pendiente de verificación** — ver nota abajo |
| IPC — INDEC | `scripts/download_ipc.py` | `data/raw/ipc/` | **Pendiente de verificación** — ver nota abajo |

### Nota sobre el estado "pendiente de verificación"

Los scripts de descarga se escribieron con URLs identificadas por búsqueda, pero el
entorno de desarrollo donde se escribieron **no tiene acceso de salida a los dominios
`argentina.gob.ar` e `indec.gob.ar`** (bloqueado por política de red de esa sesión), así
que no se pudo confirmar directamente la estructura real de la página ni de los
archivos antes de escribir el código. Los scripts están hechos para fallar de forma
explícita si la estructura esperada no está (no inventan datos), y guardan evidencia
(HTML de origen, metadata) para poder ajustarlos si hace falta.

**Antes de usar estos datos en el procesamiento, hay que:**
1. Correr `python scripts/download_coparticipacion.py` y `python scripts/download_ipc.py`
   desde un entorno con acceso a internet.
2. Revisar manualmente los archivos descargados (¿son realmente series de distribución
   de RON por provincia? ¿el IPC tiene una columna de nivel general nacional?).
3. Si algo no coincide con lo esperado, avisar antes de seguir con
   `scripts/process_coparticipacion.py` — ese script todavía no está escrito porque
   depende de conocer la estructura real de los archivos.

## Fuentes candidatas identificadas

### Coparticipación federal / Recursos de Origen Nacional (RON)

- **Organismo**: Secretaría de Hacienda, Ministerio de Economía de la Nación (Argentina).
- **URL**: <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
- **Contexto normativo**: distribución automática y diaria bajo el régimen de la Ley
  23.548 (1988) y modificaciones posteriores (p. ej., compensación por el Consenso
  Fiscal desde 2018).
- **Verificación**: identificada por búsqueda web (no se pudo acceder al contenido
  real desde el entorno de desarrollo). El script rastrea la página buscando enlaces a
  archivos `.xls`/`.xlsx`/`.csv`/`.zip` en vez de asumir un nombre de archivo fijo.

### Índice de Precios al Consumidor (IPC)

- **Organismo**: INDEC (Instituto Nacional de Estadística y Censos).
- **URLs**:
  - Serie por división de consumo (metodología vigente desde dic-2016):
    <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv>
  - Serie por apertura (metodología vigente desde dic-2016):
    <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_aperturas.csv>
  - Serie histórica hasta dic-2016 (metodología anterior):
    <https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_12_16.xls>
- **Nota metodológica pendiente**: el IPC nacional argentino tiene una discontinuidad
  conocida entre 2007 y 2015 (intervención del INDEC en ese período). El criterio de
  empalme entre tramos se define en `docs/methodology.md` una vez confirmada la
  estructura real de los archivos.
- **Verificación**: identificada por búsqueda web, misma limitación de acceso que arriba.

## Metadata dinámica

Después de correr los scripts de descarga, cada subcarpeta va a tener su propio
`_metadata.json` con la URL exacta y el timestamp de la corrida real — esa es la fuente
de verdad sobre cuándo y de dónde se descargó cada archivo, este README documenta el
contexto y las fuentes candidatas.
