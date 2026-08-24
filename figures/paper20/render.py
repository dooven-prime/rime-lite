"""Render the Paper XX carrier-support and survivor-test diagram."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import (  # noqa: E402
    BLUE,
    BLUE_DARK,
    GRAY_2,
    GREEN,
    ORANGE,
    RED,
    arrow,
    box,
    clean,
    save,
    setup,
    title,
)


HERE = Path(__file__).resolve().parent


def carrier_survivor_gate() -> None:
    fig, ax = setup((13.8, 7.6))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Carrier Support Admits; the Survivor Test Decides",
        "Boolean support remains a candidate layer, not a routed-composition witness",
    )

    box(
        ax,
        0.34,
        0.73,
        0.32,
        0.12,
        "Declared routed product",
        r"$T_{i\leftarrow j}(\mathbf{g};\mathbf{k})$",
        edge=BLUE_DARK,
        fill="#eef5fa",
    )
    box(
        ax,
        0.34,
        0.52,
        0.32,
        0.12,
        "Endpoint carrier gate",
        r"$\operatorname{Supp}_B(i)\cap\operatorname{Supp}_B(j)$",
        edge=BLUE,
        fill="#f5f9fc",
    )
    arrow(ax, 0.50, 0.73, 0.50, 0.64, color=BLUE_DARK)

    box(
        ax,
        0.055,
        0.30,
        0.32,
        0.13,
        "Disjoint endpoint carriers",
        r"intersection $=\varnothing$",
        edge=RED,
        fill="#fbefed",
    )
    box(
        ax,
        0.625,
        0.30,
        0.32,
        0.13,
        "Common endpoint carriers",
        r"intersection $\ne\varnothing$",
        edge=ORANGE,
        fill="#fff6e8",
    )
    arrow(ax, 0.40, 0.52, 0.22, 0.43, color=RED)
    arrow(ax, 0.60, 0.52, 0.78, 0.43, color=ORANGE)

    box(
        ax,
        0.055,
        0.095,
        0.32,
        0.12,
        "Exact all-depth obstruction",
        r"$T=0$ at every finite depth",
        edge=RED,
        fill="#fbefed",
    )
    box(
        ax,
        0.625,
        0.095,
        0.32,
        0.12,
        "Exact carrier-local decision",
        r"survivor recursion / $\operatorname{im}B_r^{(b)}\subseteq\ker A_r^{(b)}$",
        edge=GREEN,
        fill="#eef8f1",
        body_size=9.0,
    )
    arrow(ax, 0.215, 0.30, 0.215, 0.215, color=RED)
    arrow(ax, 0.785, 0.30, 0.785, 0.215, color=GREEN)

    ax.text(
        0.50,
        0.025,
        "Carrier overlap is an admission condition, not a nonzero conclusion.",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color=GRAY_2,
    )
    save(fig, str(HERE), "fig1_carrier_survivor_gate")


if __name__ == "__main__":
    carrier_survivor_gate()
    print(f"Wrote Paper XX figures to {HERE}")
