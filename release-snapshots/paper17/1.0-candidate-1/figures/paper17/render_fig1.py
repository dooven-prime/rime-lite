#!/usr/bin/env python3
"""Render the Paper XVII transient-separation figure from exact audit records."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "experiments" / "paper17" / "results"
OUTPUT = Path(__file__).with_name("fig1_transient_separation_and_safe_forgetting.png")

RED = "#B33A3A"
RED_LIGHT = "#F2D9D5"
TEAL = "#167D78"
TEAL_LIGHT = "#D7ECE9"
BLUE = "#2D5F8B"
BLUE_LIGHT = "#DDE8F2"
INK = "#20252B"
MUTED = "#606A73"
LINE = "#9AA4AD"


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def arrow(ax, start, end, color, *, style="-|>", width=1.6, mutation=13):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=mutation,
            linewidth=width,
            color=color,
            transform=ax.transAxes,
            shrinkA=2,
            shrinkB=2,
        )
    )


def main() -> int:
    common = load("finite_history_common_support_audit.v1.json")
    transient = load("finite_history_transient_fiber_audit.v1.json")
    terminal = load("finite_history_terminal_image_audit.v1.json")

    failure_sizes = [item["member_count"] for item in transient["transient_separation"]["failure_fibers"]]
    cohort_sizes = transient["persistent_safe_forgetting"]["cohort_sizes"]
    profile = next(
        item for item in common["common_support_audit"]["profiles"] if item["h"] == 0
    )
    image = terminal["exact_image_profile"]

    assert failure_sizes == [9, 33, 2, 2, 2, 3]
    assert sum(failure_sizes) == 51
    assert cohort_sizes == [51, 25, 19, 4, 3]
    assert profile["N_h"] == 1422
    assert profile["K_h"] == 1228
    assert profile["failure_fiber_count"] == 0
    assert terminal["classification"]["registered_internal_shift_count"] == 1
    assert image["t4_intersection_with_common_image_size"] == 0

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
        }
    )
    fig = plt.figure(figsize=(8.2, 10.2), facecolor="white")
    grid = fig.add_gridspec(3, 1, height_ratios=[1.05, 1.12, 1.0], hspace=0.26,
                            left=0.07, right=0.95, top=0.89, bottom=0.04)
    ax_left = fig.add_subplot(grid[0, 0])
    ax_right = fig.add_subplot(grid[1, 0])
    ax_bottom = fig.add_subplot(grid[2, 0])

    for ax in (ax_left, ax_right, ax_bottom):
        ax.set_axis_off()

    ax_left.set_title("A  Transient separation", loc="left", color=INK, pad=8)
    ax_left.text(0.03, 0.88, r"$t=1$: six unsafe coarse fibers", color=RED, weight="bold", transform=ax_left.transAxes)
    x_positions = [0.10, 0.26, 0.42, 0.58, 0.74, 0.90]
    max_size = max(failure_sizes)
    for x, size in zip(x_positions, failure_sizes):
        radius = 0.039 + 0.042 * (size / max_size) ** 0.5
        circle = plt.Circle((x, 0.68), radius, transform=ax_left.transAxes, facecolor=RED_LIGHT, edgecolor=RED, linewidth=1.5)
        ax_left.add_patch(circle)
        ax_left.text(x, 0.68, str(size), ha="center", va="center", color=INK, weight="bold", transform=ax_left.transAxes)
    ax_left.text(0.5, 0.53, "51 sources share unsafe histories", ha="center", color=MUTED, transform=ax_left.transAxes)
    arrow(ax_left, (0.5, 0.48), (0.5, 0.31), RED)
    ax_left.text(0.5, 0.23, r"$t=2$: 51 globally singleton observations", ha="center", color=RED, weight="bold", transform=ax_left.transAxes)
    for i in range(17):
        for j in range(3):
            ax_left.plot(0.16 + i * 0.042, 0.075 + j * 0.028, marker="o", markersize=3.4, color=RED, transform=ax_left.transAxes)

    ax_right.set_title("B  Persistent safe forgetting", loc="left", color=INK, pad=8)
    ax_right.text(0.27, 0.88, r"$t=2$ cohorts", ha="center", color=TEAL, weight="bold", transform=ax_right.transAxes)
    ax_right.text(0.73, 0.88, r"$t=3$ same members", ha="center", color=TEAL, weight="bold", transform=ax_right.transAxes)
    y_positions = [0.73, 0.59, 0.45, 0.31, 0.17]
    max_cohort = max(cohort_sizes)
    for y, size in zip(y_positions, cohort_sizes):
        width = 0.19 + 0.12 * size / max_cohort
        left_x = 0.27 - width / 2
        right_x = 0.73 - width / 2
        for x in (left_x, right_x):
            rect = Rectangle((x, y - 0.043), width, 0.086, transform=ax_right.transAxes, facecolor=TEAL_LIGHT, edgecolor=TEAL, linewidth=1.4)
            ax_right.add_patch(rect)
            ax_right.text(x + width / 2, y, str(size), ha="center", va="center", color=INK, weight="bold", transform=ax_right.transAxes)
        arrow(ax_right, (left_x + width + 0.015, y), (right_x - 0.015, y), TEAL, width=1.35, mutation=11)
    ax_right.text(0.5, 0.035, "Five disjoint cohorts remain successor-consistent", ha="center", color=INK, transform=ax_right.transAxes)

    ax_bottom.set_title("C  Common-support factorization and terminal-image boundary", loc="left", color=INK, pad=8)
    ax_bottom.add_patch(Rectangle((0.02, 0.56), 0.96, 0.29, transform=ax_bottom.transAxes, facecolor=BLUE_LIGHT, edgecolor=BLUE, linewidth=1.4))
    ax_bottom.text(0.5, 0.76, r"Common support $t\in\{2,3\}$: $\Pi_0=\Pi_1=\Pi_2$", ha="center", color=BLUE, weight="bold", transform=ax_bottom.transAxes)
    ax_bottom.text(0.5, 0.64, r"$N=1422,\ K=1228$; ten non-singleton fibers; no conflicts", ha="center", color=INK, transform=ax_bottom.transAxes)
    ax_bottom.add_patch(Rectangle((0.02, 0.13), 0.39, 0.30, transform=ax_bottom.transAxes, facecolor="#F1F3F5", edgecolor=LINE, linewidth=1.4))
    ax_bottom.add_patch(Rectangle((0.59, 0.13), 0.39, 0.30, transform=ax_bottom.transAxes, facecolor="#F8E9E7", edgecolor=RED, linewidth=1.4))
    ax_bottom.text(0.215, 0.35, r"$\mathcal{Z}_{2,3}$: 1,228 values", ha="center", color=BLUE, weight="bold", transform=ax_bottom.transAxes)
    ax_bottom.text(0.215, 0.22, r"one internal $t=2\to3$ shift", ha="center", color=INK, transform=ax_bottom.transAxes)
    ax_bottom.text(0.785, 0.35, r"terminal $t=4$: 614 values", ha="center", color=RED, weight="bold", transform=ax_bottom.transAxes)
    ax_bottom.text(0.785, 0.22, r"disjoint from $\mathcal{Z}_{2,3}$", ha="center", color=INK, transform=ax_bottom.transAxes)
    arrow(ax_bottom, (0.43, 0.28), (0.57, 0.28), RED, width=1.7, mutation=15)
    ax_bottom.text(0.5, 0.02, "No endomap on the verified common coarse image", ha="center", color=RED, weight="bold", transform=ax_bottom.transAxes)

    fig.suptitle("Exact finite fiber evolution", x=0.07, y=0.975, ha="left", color=INK, fontsize=17, weight="bold")
    fig.text(0.07, 0.939, "Registered 711-source domain | unsafe fibers separate; disjoint cohorts remain safely noninjective", color=MUTED, fontsize=11)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
