"""Shared, presentation-only helpers for RIME figure renderers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


PAPER_BLOCK_COLORS = {
    "cp": "#24567a",
    "ep": "#c7473a",
    "co": "#d39b17",
    "eo": "#17725f",
}


def save_figure(
    fig: plt.Figure,
    output_dir: Path,
    stem: str,
    *,
    dpi: int = 240,
) -> None:
    """Write matching raster and vector assets without changing the plot."""

    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_dir / f"{stem}.png",
        dpi=dpi,
        bbox_inches="tight",
        facecolor="white",
    )
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
