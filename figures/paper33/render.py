"""Render the Paper XXXIII source-addressed incidence figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


HERE = Path(__file__).resolve().parent

BLUE = "#24567a"
BLUE_DARK = "#173b55"
GREEN = "#17725f"
ORANGE = "#c96516"
RED = "#b2473e"
GRAY = "#58646d"
LIGHT = "#f5f7f8"


def _box(ax, x, heading, body, *, edge, fill, width=0.16) -> None:
    y, height = 0.43, 0.24
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            linewidth=1.6,
            edgecolor=edge,
            facecolor=fill,
        )
    )
    ax.text(
        x + width / 2,
        y + height * 0.67,
        heading,
        ha="center",
        va="center",
        fontsize=11.0,
        fontweight="bold",
        color=edge,
    )
    ax.text(
        x + width / 2,
        y + height * 0.29,
        body,
        ha="center",
        va="center",
        fontsize=9.0,
        color=GRAY,
        linespacing=1.2,
    )


def _arrow(ax, x1, x2, label) -> None:
    y = 0.55
    ax.add_patch(
        FancyArrowPatch(
            (x1, y),
            (x2, y),
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.5,
            color="#7b8790",
            shrinkA=3,
            shrinkB=3,
        )
    )
    ax.text(
        (x1 + x2) / 2,
        y - 0.19,
        label,
        ha="center",
        va="top",
        fontsize=8.4,
        color=GRAY,
    )


def render() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.dpi": 120,
            "savefig.dpi": 260,
            "axes.unicode_minus": False,
        }
    )
    fig, ax = plt.subplots(figsize=(12.4, 5.0))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.93,
        "Source-Addressed Orbit Incidence",
        ha="center",
        va="top",
        fontsize=16,
        fontweight="bold",
        color=BLUE_DARK,
    )
    ax.text(
        0.5,
        0.855,
        "A valid factorization retains one concrete intermediate witness",
        ha="center",
        va="top",
        fontsize=10.3,
        color=GRAY,
    )

    starts = [0.025, 0.225, 0.425, 0.625, 0.825]
    _box(ax, starts[0], r"Source orbit $O$", r"$x\in O$", edge=BLUE, fill="#f1f6fa")
    _box(
        ax,
        starts[1],
        r"Branch image $a_\#(O)$",
        r"concrete image states",
        edge=BLUE,
        fill="#f1f6fa",
    )
    _box(
        ax,
        starts[2],
        r"Shared witness $y$",
        r"$y\in\mathcal{I}_a(O,O_1)$" "\n" r"$y\in\mathrm{Dom}(F_r^{(0)})$",
        edge=ORANGE,
        fill="#fff7ec",
    )
    _box(
        ax,
        starts[3],
        r"Identity return",
        r"$F_r^{(0)}(y)$",
        edge=GREEN,
        fill="#eff8f4",
    )
    _box(
        ax,
        starts[4],
        r"Target orbit $O'$",
        r"$F_r^{(0)}(y)\in O'$",
        edge=GREEN,
        fill="#eff8f4",
    )

    _arrow(ax, 0.185, 0.225, r"$a_\#$")
    _arrow(ax, 0.385, 0.425, r"intersect with $O_1$")
    _arrow(ax, 0.585, 0.625, r"guarded $F_r^{(0)}$")
    _arrow(ax, 0.785, 0.825, r"orbit membership")

    ax.add_patch(
        FancyBboxPatch(
            (0.11, 0.13),
            0.78,
            0.13,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            linewidth=1.2,
            edgecolor=RED,
            facecolor="#fff4f2",
        )
    )
    ax.text(
        0.5,
        0.195,
        r"Non-composable shortcut: $\mathcal{I}_a(O,O_1)\ne\varnothing$ and "
        r"$O_1$ has a return do not suffice when they use different states.",
        ha="center",
        va="center",
        fontsize=9.7,
        color=RED,
    )

    fig.tight_layout(pad=0.6)
    HERE.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        HERE / "fig1_source_addressed_incidence.png",
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


if __name__ == "__main__":
    render()
    print(f"Wrote {HERE / 'fig1_source_addressed_incidence.png'}")
