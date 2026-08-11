"""Shared figure helpers for SOF-stage papers VIII--X."""

from __future__ import annotations

import os
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


BLUE = "#2471a3"
BLUE_DARK = "#1b4f72"
GREEN = "#2e8b57"
RED = "#a93226"
ORANGE = "#b9770e"
PURPLE = "#6c3483"
GRAY_0 = "#111111"
GRAY_1 = "#333333"
GRAY_2 = "#666666"
GRAY_3 = "#999999"
GRAY_4 = "#d9d9d9"
GRAY_5 = "#f4f6f7"


def setup(figsize: tuple[float, float] = (12.5, 7.2)):
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 17,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    return fig, ax


def clean(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def title(ax, main: str, sub: str | None = None) -> None:
    ax.text(0.5, 0.965, main, ha="center", va="top", fontsize=18, fontweight="bold")
    if sub:
        ax.text(0.5, 0.918, sub, ha="center", va="top", fontsize=10.5, color=GRAY_2)


def box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    head: str,
    body: str = "",
    edge: str = BLUE,
    fill: str = "white",
    head_color: str | None = None,
    body_size: float = 9.5,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.4,
        edgecolor=edge,
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.64, head, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=head_color or edge)
    if body:
        ax.text(x + w / 2, y + h * 0.34, body, ha="center", va="center",
                fontsize=body_size, color=GRAY_1, linespacing=1.18)


def arrow(ax, x1: float, y1: float, x2: float, y2: float, color: str = GRAY_2, lw: float = 1.8) -> None:
    arr = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=lw,
        color=color,
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arr)


def save(fig, out_dir: str, name: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, f"{name}.png"), bbox_inches="tight")
    fig.savefig(os.path.join(out_dir, f"{name}.pdf"), bbox_inches="tight")
    plt.close(fig)


def draw_matrix(ax, data: np.ndarray, row_labels: Iterable[str], col_labels: Iterable[str], cmap="Blues") -> None:
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_xticklabels(list(col_labels), rotation=28, ha="right")
    ax.set_yticklabels(list(row_labels))
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            ax.text(j, i, f"{val:.0f}" if val in (0, 1) else f"{val:.1f}",
                    ha="center", va="center", fontsize=8.5,
                    color="white" if val > 0.55 else GRAY_0)
    return im
