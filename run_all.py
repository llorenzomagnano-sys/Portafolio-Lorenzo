#!/usr/bin/env python3
"""
Corre el pipeline completo del proyecto de punta a punta, con un solo comando:

    python run_all.py

Pasos:
  1. Descarga de datos crudos -- NO se ejecuta automáticamente (ver nota abajo).
  2. Procesamiento (Núcleo 1, 2 y 4): genera los CSV de data/processed/.
  3. Tests automáticos del simulador (Núcleo 3).
  4. Regeneración de los 4 notebooks (ejecuta cada uno de punta a punta con
     `jupyter nbconvert`, lo que a su vez regenera todas las figuras de
     output/figures/).

Nota sobre la descarga: `scripts/download_coparticipacion.py` y
`scripts/download_ipc.py` existen pero no se probaron end-to-end -- el entorno donde
se desarrolló este proyecto no tiene acceso de salida a internet, así que todos los
archivos de `data/raw/` fueron incorporados manualmente (ver docs/methodology.md y
data/raw/README.md para la trazabilidad completa de cada fuente). Este script asume
que `data/raw/` ya está poblada (viene versionada en el repositorio) y arranca desde
el procesamiento. Si en algún momento se corre este proyecto desde un entorno con
acceso a internet y se quiere probar la descarga automática, correr esos dos scripts
por separado antes de este.

Requiere las dependencias de requirements.txt instaladas (`pip install -r
requirements.txt`).
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

PASOS_PROCESAMIENTO = [
    ("Núcleo 1 — procesar y deflactar la serie de coparticipación", "process_coparticipacion.py"),
    ("Núcleo 2 — comparar aporte (PBG) vs. recibo (coparticipación)", "build_coefficients_comparison.py"),
    ("Núcleo 4 — ratio de dependencia fiscal de Córdoba", "build_dependencia_fiscal.py"),
]

NOTEBOOKS = [
    "01_serie_historica.ipynb",
    "02_aporte_vs_recibo.ipynb",
    "03_simulador_sensibilidad.ipynb",
    "04_dependencia_fiscal_cordoba.ipynb",
]


def run(descripcion: str, cmd: list[str], cwd: Path) -> None:
    print(f"\n{'=' * 70}\n{descripcion}\n{'=' * 70}")
    resultado = subprocess.run(cmd, cwd=cwd)
    if resultado.returncode != 0:
        sys.exit(
            f"\nFalló: {descripcion!r} (comando: {' '.join(cmd)}). "
            "Se corta el pipeline acá -- revisar el error de arriba antes de reintentar."
        )


def main() -> None:
    print(
        "Pipeline del proyecto Portafolio-Lorenzo.\n"
        "La descarga automática de data/raw/ NO se ejecuta (ver docstring de este "
        "archivo) -- se asume que data/raw/ ya está poblada, como viene en el "
        "repositorio."
    )

    for descripcion, script in PASOS_PROCESAMIENTO:
        run(descripcion, [sys.executable, script], cwd=SCRIPTS_DIR)

    run(
        "Núcleo 3 — tests automáticos del simulador",
        [sys.executable, "-m", "pytest", "test_simulator.py", "-v"],
        cwd=SCRIPTS_DIR,
    )

    for notebook in NOTEBOOKS:
        run(
            f"Regenerar notebook: {notebook}",
            ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", notebook],
            cwd=NOTEBOOKS_DIR,
        )

    print(f"\n{'=' * 70}\nPipeline completo. Salidas actualizadas en data/processed/, "
          f"output/figures/ y notebooks/.\n{'=' * 70}")


if __name__ == "__main__":
    main()
