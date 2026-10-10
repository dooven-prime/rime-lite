#!/usr/bin/env python3
"""Render the Paper XVII registered transition-layer contrast figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


REPO = Path(__file__).resolve().parents[2]
CLASSIFICATION = (
    REPO
    / "experiments"
    / "paper17"
    / "mechanism"
    / "results"
    / "mts1-v1"
    / "validation"
    / "mechanism_classification.v1.json"
)
OUTPUT = Path(__file__).with_name("fig2_internal_transition_layer_contrast.png")

RED = "#B33A3A"
RED_LIGHT = "#F2D9D5"
TEAL = "#167D78"
TEAL_LIGHT = "#D7ECE9"
AMBER = "#A46A16"
AMBER_LIGHT = "#F5E8CE"
BLUE = "#2D5F8B"
BLUE_LIGHT = "#DDE8F2"
INK = "#20252B"
MUTED = "#606A73"
LINE = "#9AA4AD"


def arrow(ax, start, end, color, *, width=1.6, mutation=13):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=mutation,
            linewidth=width,
            color=color,
            transform=ax.transAxes,
            shrinkA=2,
            shrinkB=2,
        )
    )


def box(ax, xy, width, height, face, edge, title, detail):
    x, y = xy
    ax.add_patch(
        Rectangle(
            (x, y),
            width,
            height,
            transform=ax.transAxes,
            facecolor=face,
            edgecolor=edge,
            linewidth=1.5,
        )
    )
    ax.text(
        x + width / 2,
        y + height * 0.67,
        title,
        ha="center",
        va="center",
        color=edge,
        weight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        x + width / 2,
        y + height * 0.29,
        detail,
        ha="center",
        va="center",
        color=INK,
        fontsize=12,
        transform=ax.transAxes,
    )


def main() -> int:
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    result = data["classification"]
    separators = result["exact_separators"]

    assert data["status"] == "PASS"
    assert result["outcome"] == "EXACT_TRANSITION_LAYER_LOCALIZATION"
    assert result["record_count"] == 6975
    assert result["comparison_cell_count"] == 15
    assert result["differing_comparison_cell_count"] == 15
    assert len(separators) == 4
    assert {entry["transition"] for entry in separators} == {"2_TO_3", "3_TO_4"}
    assert {entry["predicate"] for entry in separators} == {
        "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL",
        "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION",
    }
    assert all(
        entry["direction"] == "TRANSIENT_ALL__PERSISTENT_NONE"
        for entry in separators
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 13,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
        }
    )
    fig = plt.figure(figsize=(8.2, 9.8), facecolor="white")
    grid = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.3], hspace=0.25,
                            left=0.07, right=0.96, top=0.87, bottom=0.06)
    ax_top = fig.add_subplot(grid[0, 0])
    ax_bottom = fig.add_subplot(grid[1, 0])
    for ax in (ax_top, ax_bottom):
        ax.set_axis_off()

    ax_top.set_title("A  Time-resolved interpretation boundary", loc="left", color=INK, pad=8)
    box(
        ax_top,
        (0.01, 0.20),
        0.29,
        0.56,
        AMBER_LIGHT,
        AMBER,
        "$1\\to2$ defining split",
        "Histograms differ; no\nuniversal separator",
    )
    box(
        ax_top,
        (0.355, 0.20),
        0.29,
        0.56,
        BLUE_LIGHT,
        BLUE,
        "$2\\to3$ later layer",
        "Two exact all-versus-\nnone predicates",
    )
    box(
        ax_top,
        (0.70, 0.20),
        0.29,
        0.56,
        BLUE_LIGHT,
        BLUE,
        "$3\\to4$ later layer",
        "The same two exact\npredicates",
    )
    arrow(ax_top, (0.305, 0.48), (0.35, 0.48), LINE)
    arrow(ax_top, (0.65, 0.48), (0.695, 0.48), LINE)
    ax_top.text(
        0.5,
        0.02,
        "Later signatures do not establish the cause of the initial split",
        ha="center",
        color=RED,
        weight="bold",
        transform=ax_top.transAxes,
    )

    ax_bottom.set_title("B  Exact registered separator matrix", loc="left", color=INK, pad=8)
    ax_bottom.text(0.44, 0.9, r"$2\to3$", ha="center", color=BLUE, weight="bold", fontsize=14, transform=ax_bottom.transAxes)
    ax_bottom.text(0.76, 0.9, r"$3\to4$", ha="center", color=BLUE, weight="bold", fontsize=14, transform=ax_bottom.transAxes)
    ax_bottom.text(0.02, 0.69, "Clipping modifies\ncoarse residual", color=INK, weight="bold", transform=ax_bottom.transAxes)
    ax_bottom.text(0.02, 0.36, "Fate disagreement +\nclip correction", color=INK, weight="bold", transform=ax_bottom.transAxes)

    for y in (0.62, 0.29):
        for x in (0.34, 0.66):
            ax_bottom.add_patch(Rectangle((x, y), 0.13, 0.16, transform=ax_bottom.transAxes, facecolor=RED_LIGHT, edgecolor=RED, linewidth=1.4))
            ax_bottom.add_patch(Rectangle((x + 0.14, y), 0.13, 0.16, transform=ax_bottom.transAxes, facecolor=TEAL_LIGHT, edgecolor=TEAL, linewidth=1.4))
            ax_bottom.text(x + 0.065, y + 0.105, "TO", ha="center", color=RED, weight="bold", transform=ax_bottom.transAxes)
            ax_bottom.text(x + 0.065, y + 0.045, "ALL", ha="center", color=INK, weight="bold", transform=ax_bottom.transAxes)
            ax_bottom.text(x + 0.205, y + 0.105, "PS", ha="center", color=TEAL, weight="bold", transform=ax_bottom.transAxes)
            ax_bottom.text(x + 0.205, y + 0.045, "NONE", ha="center", color=INK, weight="bold", transform=ax_bottom.transAxes)

    ax_bottom.add_patch(Rectangle((0.02, 0.015), 0.94, 0.14, transform=ax_bottom.transAxes, facecolor="#F1F3F5", edgecolor=LINE, linewidth=1.2))
    ax_bottom.text(0.49, 0.105, "Complete exact finite census", ha="center", color=INK, weight="bold", transform=ax_bottom.transAxes)
    ax_bottom.text(0.49, 0.05, "153 sources | 459 transitions | 6,975 pair records | 15/15 histograms differ", ha="center", color=MUTED, fontsize=11.5, transform=ax_bottom.transAxes)

    fig.suptitle(
        "Stable internal transition-layer contrast after transient separation",
        x=0.04,
        y=0.985,
        ha="left",
        color=INK,
        fontsize=16,
        weight="bold",
    )
    fig.text(
        0.04,
        0.935,
        "TO = transient-obstruction pairs; PS = persistent-safe pairs. Exact finite-census comparison.",
        color=MUTED,
        fontsize=12,
    )
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
