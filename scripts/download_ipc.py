"""
Descarga las series del Índice de Precios al Consumidor (IPC) publicadas por
INDEC, para usarlas como deflactor de la serie de coparticipación.

Fuentes candidatas (confirmadas por búsqueda, NO por acceso directo -- ver nota
en scripts/download_coparticipacion.py sobre la restricción de red del entorno
de desarrollo):
  - Serie IPC por división de consumo, metodología vigente desde dic-2016:
    https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv
  - Serie IPC por apertura, metodología vigente desde dic-2016:
    https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_aperturas.csv
  - Serie histórica IPC hasta dic-2016 (metodología anterior):
    https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_12_16.xls

NOTA METODOLÓGICA: la serie de IPC nacional de Argentina tiene una discontinuidad
conocida entre 2007 y 2015 (período de intervención del INDEC, con cuestionamientos
sobre la fiabilidad del índice oficial de esos años). Este script solo descarga los
archivos crudos tal como los publica INDEC -- el empalme y las decisiones
metodológicas para construir una serie deflactora se documentan y resuelven en
scripts/process_coparticipacion.py y en docs/methodology.md, no acá.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

SOURCES = {
    "ipc_divisiones_2016_actual.csv": "https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv",
    "ipc_aperturas_2016_actual.csv": "https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_aperturas.csv",
    "ipc_serie_historica_hasta_2016.xls": "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_12_16.xls",
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "ipc"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Portafolio-Lorenzo/1.0)"}


def download_file(url: str, dest_path: Path) -> None:
    response = requests.get(url, timeout=60, headers=HEADERS)
    response.raise_for_status()
    dest_path.write_bytes(response.content)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    access_time = datetime.now(timezone.utc).isoformat()

    downloaded = []
    for filename, url in SOURCES.items():
        dest_path = OUTPUT_DIR / filename
        print(f"Descargando {url}")
        try:
            download_file(url, dest_path)
            downloaded.append(
                {"source_url": url, "local_path": str(dest_path.relative_to(OUTPUT_DIR.parent.parent.parent))}
            )
            print(f"  -> {dest_path}")
        except requests.RequestException as exc:
            print(f"  ERROR al descargar {url}: {exc}")
            print("  Revisar manualmente si la URL sigue vigente en indec.gob.ar.")

    if not downloaded:
        raise SystemExit("No se pudo descargar ningún archivo de IPC. Ver errores arriba.")

    metadata = {
        "access_datetime_utc": access_time,
        "downloaded_files": downloaded,
        "note": (
            "La serie nacional de IPC tiene una discontinuidad metodológica entre "
            "2007 y 2015/2016 (intervención del INDEC). El empalme entre tramos se "
            "resuelve en scripts/process_coparticipacion.py y se documenta en "
            "docs/methodology.md, no en esta descarga."
        ),
    }
    metadata_path = OUTPUT_DIR / "_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nMetadata guardada en {metadata_path}")


if __name__ == "__main__":
    main()
