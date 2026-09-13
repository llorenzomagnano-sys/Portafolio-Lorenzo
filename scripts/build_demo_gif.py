"""
Genera un GIF animado que muestra el simulador interactivo del Núcleo 3
(`notebooks/03_simulador_sensibilidad.ipynb`) recorriendo varios escenarios de shock,
para tener una demo visual en el README sin depender de que alguien corra el notebook.

No es parte del pipeline de datos (run_all.py no lo llama) -- es un asset de
presentación. Se puede regenerar corriendo este script directamente:

    python scripts/build_demo_gif.py

Salida:
  - output/figures/simulador_interactivo_demo.gif
"""
import io
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from simulator import simular_shock  # noqa: E402
from coeficientes_ley23548 import COEFICIENTES_COPARTICIPACION  # noqa: E402
from process_coparticipacion import load_ron_nominal  # noqa: E402

OUTPUT_PATH = BASE_DIR / "output" / "figures" / "simulador_interactivo_demo.gif"

COLOR_NEGATIVO = "#e34948"
COLOR_POSITIVO = "#2a78d6"
INK_PRIMARY = "#0b0b0b"
GRID_COLOR = "#e1e0d9"
SURFACE = "#fcfcfb"

ESCENARIOS_PCT = [0, -5, -10, -15, -10, -5]  # recorrido de ida y vuelta, termina en un valor negativo


def recaudacion_base_2025() -> float:
    nominal = load_ron_nominal()
    total_2025 = nominal[nominal["anio"] == 2025]["monto_nominal"].sum() * 1e6
    return total_2025 / sum(COEFICIENTES_COPARTICIPACION.values())


def render_frame(variacion_pct: float, recaudacion_base: float) -> Image.Image:
    variacion = variacion_pct / 100
    resultado = simular_shock(variacion, recaudacion_base, COEFICIENTES_COPARTICIPACION)
    cordoba = next(p for p in resultado["por_provincia"] if p["provincia"] == "Córdoba")
    impacto_miles_m = cordoba["impacto_pesos"] / 1e9

    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=120)
    color = COLOR_NEGATIVO if cordoba["impacto_pesos"] < 0 else COLOR_POSITIVO
    ax.barh(["Córdoba"], [impacto_miles_m], color=color, height=0.5)
    ax.axvline(0, color=GRID_COLOR, linewidth=1)
    ax.set_xlim(-70, 70)
    ax.set_xlabel("Miles de millones de pesos")
    ax.set_title(
        f"Variación de recaudación: {variacion:+.0%}   |   Impacto en Córdoba: {impacto_miles_m:,.1f} mil M",
        fontsize=10.5, color=INK_PRIMARY,
    )
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="both", length=0)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=SURFACE)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def main() -> None:
    recaudacion_base = recaudacion_base_2025()
    frames = [render_frame(pct, recaudacion_base) for pct in ESCENARIOS_PCT]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=900,
        loop=0,
    )
    print(f"Guardado: {OUTPUT_PATH} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
