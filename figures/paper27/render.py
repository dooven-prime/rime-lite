"""Render the Paper XXVII proof-state interface figure."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import BLUE, BLUE_DARK, GREEN, GRAY_1, GRAY_2, ORANGE  # noqa: E402


HERE = Path(__file__).resolve().parent


def _box(ax, x, y, w, h, heading, body, edge, fill="#ffffff"):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=1.5, edgecolor=edge, facecolor=fill))
    ax.text(
        x + 0.025,
        y + h - 0.035,
        heading,
        ha="left",
        va="top",
        fontsize=10.8,
        fontweight="bold",
        color=edge,
    )
    ax.text(
        x + 0.025,
        y + h * 0.31,
        body,
        ha="left",
        va="center",
        fontsize=8.3,
        color=GRAY_1,
        linespacing=1.18,
    )


def _arrow(ax, x1, y1, x2, y2, color=GRAY_2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.5,
            color=color,
            shrinkA=3,
            shrinkB=3,
        )
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
    fig, ax = plt.subplots(figsize=(12.2, 6.3))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.965,
        "From Checkpoint Selection to Relation-Valued Descent",
        ha="center",
        va="top",
        fontsize=16,
        fontweight="bold",
        color=BLUE_DARK,
    )
    ax.text(
        0.5,
        0.91,
        "Two fixed-scope interfaces repair two distinct information losses",
        ha="center",
        va="top",
        fontsize=10.2,
        color=GRAY_2,
    )

    ax.plot([0.5, 0.5], [0.18, 0.86], color="#d7dde2", linewidth=1.2)
    ax.text(0.255, 0.845, "n = 6  |  legitimate checkpoint", ha="center", fontsize=11.5,
            fontweight="bold", color=BLUE_DARK)
    ax.text(0.745, 0.845, "n = 7  |  sufficient relation", ha="center", fontsize=11.5,
            fontweight="bold", color=BLUE_DARK)

    _box(ax, 0.055, 0.63, 0.39, 0.15, "Mass state", "Reachable rank-four endpoint\nwithout recursive legitimacy", ORANGE, "#fff8ef")
    _box(ax, 0.055, 0.42, 0.39, 0.15, "Typed activation", "Restores ancestry, but does not\nchoose a descending representative", BLUE, "#f3f8fc")
    _box(ax, 0.055, 0.21, 0.39, 0.15, "Intrinsic entry section", "1,704 rooted defects\n1,700 Type-I + 4 Type-II-only", GREEN, "#f1f8f4")
    _arrow(ax, 0.25, 0.63, 0.25, 0.57)
    _arrow(ax, 0.25, 0.42, 0.25, 0.36)

    _box(ax, 0.555, 0.63, 0.39, 0.15, "Mass endpoint quotient", "Tied shortest words can erase\nsource-addressed packet transport", ORANGE, "#fff8ef")
    _box(ax, 0.555, 0.42, 0.39, 0.15, "Moved-slot relation menu", "Future-free and source-addressed;\nno representative is selected in advance", BLUE, "#f3f8fc")
    _box(ax, 0.555, 0.21, 0.39, 0.15, "Finite descent interface", "17 typed states, 8 admitted returns,\n5 exit relations, Low Transport", GREEN, "#f1f8f4")
    _arrow(ax, 0.75, 0.63, 0.75, 0.57)
    _arrow(ax, 0.75, 0.42, 0.75, 0.36)

    ax.add_patch(Rectangle((0.055, 0.075), 0.89, 0.08, linewidth=1.0,
                           edgecolor="#9da8b0", facecolor="#f7f8f9"))
    ax.text(
        0.5,
        0.115,
        "Boundary: construction and proof dependencies in the declared n = 6 and n = 7 scopes; no all-n recursion or reset-bound claim.",
        ha="center",
        va="center",
        fontsize=9.1,
        color=GRAY_1,
    )

    fig.tight_layout(pad=0.7)
    fig.savefig(HERE / "fig1_entry_relation_interface.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    render()
    print(f"Wrote {HERE / 'fig1_entry_relation_interface.png'}")
