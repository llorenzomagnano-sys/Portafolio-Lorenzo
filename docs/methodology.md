# Metodología

## Fuentes de datos

**Estado: parcialmente documentado — pendiente de verificación de estructura real.**
Ver `data/raw/README.md` para el detalle de trazabilidad (URL exacta, fecha de acceso
por corrida, estado de verificación) de cada fuente.

- **Coparticipación federal / Recursos de Origen Nacional (RON)**: Secretaría de
  Hacienda, Ministerio de Economía de la Nación.
  <https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron>
- **Índice de Precios al Consumidor (IPC)**: INDEC.
  <https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv> (metodología
  vigente desde dic-2016) y `sh_ipc_12_16.xls` (serie histórica hasta dic-2016).

Estas URLs se identificaron por búsqueda web, no por acceso directo verificado, porque
el entorno donde se escribieron los scripts de descarga no tiene salida de red hacia
`argentina.gob.ar` ni `indec.gob.ar`. Falta confirmar que la estructura real de los
archivos coincide con lo esperado antes de dar esta sección por cerrada.

## Supuestos y limitaciones

- La coparticipación se distribuye a las provincias de forma automática y diaria bajo
  el régimen de la Ley 23.548 (1988), con modificaciones posteriores (p. ej.,
  compensación por el Consenso Fiscal desde 2018). El análisis no reconstruye el
  cálculo de reparto, solo trabaja con los montos ya distribuidos y publicados.
- (pendiente de completar una vez procesados los datos reales: tratamiento de valores
  faltantes, provincias con cambios de nombre/código a lo largo de la serie, etc.)

## Metodología de deflactación

**Pendiente.** Se va a documentar acá, antes de generar `data/processed/coparticipacion_real.csv`:
- Año/mes base elegido para la serie real.
- Cómo se resuelve el empalme metodológico del IPC nacional entre el tramo histórico
  (hasta dic-2016) y el vigente (desde dic-2016), dada la discontinuidad conocida del
  índice oficial en el período 2007-2015.
- Fórmula exacta usada para deflactar (monto_real = monto_nominal × IPC_base / IPC_período).

## Metodología por núcleo

(en construcción)
