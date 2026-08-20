"""
Descarga la página oficial de Recursos de Origen Nacional (RON) / coparticipación
federal de la Secretaría de Hacienda (Ministerio de Economía de la Nación) y guarda
los archivos descargables (xlsx/xls/csv/zip) que encuentre en ella, junto con la
página HTML de origen y metadata de trazabilidad.

Fuente candidata (confirmada por búsqueda, NO por acceso directo -- ver nota abajo):
    https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron

NOTA IMPORTANTE: este script fue escrito sin poder acceder a argentina.gob.ar desde
el entorno de desarrollo (el proxy de red de esa sesión bloquea el dominio). No se
verificó la estructura real de la página ni de los archivos que publica. Por eso:
  - No asume nombres de archivo fijos: rastrea la página en busca de enlaces a
    archivos (.xls, .xlsx, .csv, .zip) y los descarga tal cual los encuentra.
  - Si SOURCE_URL cambió o la página no tiene los enlaces esperados, el script debe
    fallar de forma explícita (no debe inventar ni completar datos).
  - Guarda el HTML de la página fuente para poder revisarlo manualmente si el
    scraping no encuentra lo esperado.

Al correrlo, revisar la salida de consola y el contenido descargado en
data/raw/coparticipacion/ antes de usarlo en el procesamiento.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.argentina.gob.ar/economia/sechacienda/asuntosprovinciales/ron"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "coparticipacion"
FILE_EXTENSIONS = (".xls", ".xlsx", ".csv", ".zip")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Portafolio-Lorenzo/1.0)"}


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    return response.text


def find_data_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().split("?")[0].endswith(FILE_EXTENSIONS):
            links.add(urljoin(base_url, href))
    return sorted(links)


def download_file(url: str, dest_dir: Path) -> Path:
    filename = url.split("/")[-1].split("?")[0]
    dest_path = dest_dir / filename
    response = requests.get(url, timeout=60, headers=HEADERS)
    response.raise_for_status()
    dest_path.write_bytes(response.content)
    return dest_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    access_time = datetime.now(timezone.utc).isoformat()

    print(f"Descargando página de origen: {SOURCE_URL}")
    html = fetch_page(SOURCE_URL)
    (OUTPUT_DIR / "_source_page.html").write_text(html, encoding="utf-8")

    links = find_data_links(html, SOURCE_URL)
    if not links:
        raise SystemExit(
            "No se encontraron enlaces a archivos (.xls/.xlsx/.csv/.zip) en la "
            "página. La estructura del sitio puede haber cambiado. Revisar "
            f"manualmente {SOURCE_URL} y el HTML guardado en "
            f"{OUTPUT_DIR / '_source_page.html'}, y actualizar SOURCE_URL o el "
            "filtro de enlaces en este script antes de continuar."
        )

    print(f"Se encontraron {len(links)} archivo(s) candidato(s):")
    downloaded = []
    for link in links:
        print(f"  - {link}")
        try:
            path = download_file(link, OUTPUT_DIR)
            downloaded.append(
                {"source_url": link, "local_path": str(path.relative_to(OUTPUT_DIR.parent.parent.parent))}
            )
            print(f"    descargado -> {path}")
        except requests.RequestException as exc:
            print(f"    ERROR al descargar {link}: {exc}")

    if not downloaded:
        raise SystemExit("Se encontraron enlaces pero ninguna descarga tuvo éxito. Ver errores arriba.")

    metadata = {
        "source_page": SOURCE_URL,
        "access_datetime_utc": access_time,
        "downloaded_files": downloaded,
        "note": (
            "Descarga automática por scraping de enlaces en la página fuente. "
            "Revisar manualmente que los archivos correspondan a la serie de "
            "distribución de RON/coparticipación por provincia esperada -- el "
            "script no valida el contenido, solo lo descarga."
        ),
    }
    metadata_path = OUTPUT_DIR / "_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nMetadata guardada en {metadata_path}")
    print(
        "\nIMPORTANTE: revisar manualmente los archivos descargados en "
        f"{OUTPUT_DIR} antes de procesarlos con scripts/process_coparticipacion.py."
    )


if __name__ == "__main__":
    main()
