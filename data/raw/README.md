# data/raw — trazabilidad de fuentes

Esta carpeta tiene los datos crudos, tal como los conseguí. Nunca se editan a mano. Cada subcarpeta corresponde a una fuente y tiene su propio `_metadata.json` con el origen exacto de cada archivo.

## Estado de las fuentes (Núcleo 1)

| Fuente | Carpeta | Estado |
|---|---|---|
| Coparticipación / RON — Secretaría de Hacienda | `data/raw/coparticipacion/` | **Datos reales incorporados** (ver detalle abajo) |
| IPC — INDEC | `data/raw/ipc/` | **Datos reales incorporados** (ver detalle abajo) |

### Cómo los conseguí

Escribí `scripts/download_coparticipacion.py` y `scripts/download_ipc.py`, pero no pude correrlos desde el entorno donde armé este proyecto: no tiene salida a internet hacia `argentina.gob.ar`, `indec.gob.ar` ni la mayoría de los dominios externos. Así que terminé descargando los archivos a mano desde mi propia máquina y copiándolos acá. Cada `_metadata.json` lo deja anotado (`obtenido_por`, `motivo`).

Si en algún momento corro este proyecto desde un entorno con acceso a internet, los scripts de descarga deberían poder reemplazar ese paso manual — pero no los probé de punta a punta, así que conviene revisar bien la salida la primera vez que se usen.

### Coparticipación federal / Recursos de Origen Nacional (RON)

- **Organismo**: Secretaría de Hacienda, Ministerio de Economía de la Nación.
- **URL de origen**: <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
- **Archivo usado**: `coparticipacion/serie_ron_2003_2025.csv` — 2003 a 2025, un registro por provincia/año/concepto (20 conceptos distintos de RON, no solo coparticipación Ley 23.548). Qué conceptos uso exactamente para este núcleo está detallado en `docs/methodology.md`.
- **Contexto normativo**: distribución automática y diaria bajo el régimen de la Ley 23.548 (1988) y modificaciones posteriores (por ejemplo, la compensación por el Consenso Fiscal desde 2018). El archivo agrega esa distribución diaria a nivel anual.

### Índice de Precios al Consumidor (IPC)

- **2016-2025 — INDEC**: `ipc/serie_ipc_divisiones.csv` — Region="Nacional", Nivel General, cobertura mensual desde diciembre de 2016. El IPC oficial de Argentina no tiene cobertura confiable antes de esa fecha con las fuentes a las que pude acceder directamente de INDEC (el detalle está en `docs/methodology.md`, en la parte sobre la confiabilidad del IPC oficial en 2007-2015).
- **2003-2015 — Fundación Norte y Sur / Orlando Ferreres**: `ipc/fundacion_norte_y_sur_orlando_ferreres.xlsx`, hoja `IPC `, que me pasaron directamente. La uso para empalmar el IPC hacia atrás desde 2016: el tramo 2004-2006 sale de la tabla "GBA (INDEC)" (pre-intervención, confiable), y el tramo 2007-2016 de la tabla "GBA (estimaciones privadas)" (reemplaza al IPC oficial de esos años, bastante desacreditado por la intervención del INDEC). El método exacto, y una limitación que no pude resolver sobre una nota del archivo ("Ver metodología" sin hoja de metodología adjunta), están en `docs/methodology.md`.
- Con este empalme, el Núcleo 1 pasó de cubrir 2016-2025 a cubrir 2003-2025. No llega a 1990 porque no encontré ninguna fuente de montos nominales de coparticipación anterior a 2003 (ver la sección de RON arriba).

### Ingresos corrientes de Córdoba (proxy, Núcleo 4)

- **Organismo**: Dirección General de Rentas de la Provincia de Córdoba (archivo que ya tenía armado de antes y usé acá).
- **Archivo usado**: `ingresos_cordoba/serie_recaudacion_provincial.xlsx`, hoja `Serie_Mensual` — recaudación mensual, enero 2015 a agosto 2026. Para el Núcleo 4 uso solo años calendario completos, 2015-2025.
- **El nombre del archivo no era el que esperaba**: pensaba que se iba a llamar `dgeyc_ingresos_cordoba.xlsx`, pero el archivo real se llama `Serie-recaudacion-provincial_Ene15-Ago26.xlsx` — confirmé que era la fuente correcta antes de usarla.
- **Limitación de alcance**: la fila "Total" que uso como proxy de "ingresos corrientes totales" excluye lo recaudado por otros organismos públicos provinciales (por ejemplo, EPEC), según la propia nota al pie del archivo. El detalle completo — incluida la corrección de unidades, porque el archivo dice "millones de pesos" pero en realidad son pesos — está en `docs/methodology.md`, sección del Núcleo 4.

## Otros archivos en esta carpeta (no usados en el Núcleo 1)

Los conservo como referencia para el futuro, o por si en algún momento quiero revisar la decisión de acotar el alcance temporal. Cada uno tiene documentado en su `_metadata.json` el motivo puntual por el que lo descarté — cobertura temporal insuficiente, o, en el caso de las series del Banco Mundial vía FRED, una inconsistencia económica que encontré en los propios datos, no un error mío al descargarlos.
