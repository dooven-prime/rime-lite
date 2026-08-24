"""Render the Paper XXI prefix-pole semantics diagram."""

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
    arrow,
    box,
    clean,
    save,
    setup,
    title,
)


HERE = Path(__file__).resolve().parent


def prefix_pole_semantics() -> None:
    fig, ax = setup((13.8, 7.7))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Prefix Poles Decide Route Survival",
        "One semantic classification yields field-relative and depth-relative consequences",
    )

    box(
        ax,
        0.33,
        0.74,
        0.34,
        0.12,
        "Declared labelled route",
        r"word $w$ + sector path $s$",
        edge=BLUE_DARK,
        fill="#eef5fa",
    )
    box(
        ax,
        0.33,
        0.53,
        0.34,
        0.13,
        "Prefix-pole constraints",
        r"$s_k=0$: force $x=z_k$;  $s_k=1$: exclude $x=z_k$",
        edge=BLUE,
        fill="#f5f9fc",
        body_size=9.2,
    )
    arrow(ax, 0.50, 0.74, 0.50, 0.66, color=BLUE_DARK)

    box(
        ax,
        0.055,
        0.29,
        0.36,
        0.14,
        "Fix the finite field",
        "reachable survivor subsets",
        edge=GREEN,
        fill="#eef8f1",
    )
    box(
        ax,
        0.585,
        0.29,
        0.36,
        0.14,
        "Fix the route depth",
        "integral pole equalities + exceptional characteristics",
        edge=ORANGE,
        fill="#fff6e8",
        body_size=8.9,
    )
    arrow(ax, 0.40, 0.53, 0.235, 0.43, color=GREEN)
    arrow(ax, 0.60, 0.53, 0.765, 0.43, color=ORANGE)

    box(
        ax,
        0.055,
        0.08,
        0.36,
        0.12,
        "Finite automaton",
        "field-relative rational transfer series",
        edge=GREEN,
        fill="#eef8f1",
    )
    box(
        ax,
        0.585,
        0.08,
        0.36,
        0.12,
        "Generic depth profile",
        r"$Z_d(F)=Z_d^{\mathrm{gen}}$ outside $E_d$",
        edge=ORANGE,
        fill="#fff6e8",
    )
    arrow(ax, 0.235, 0.29, 0.235, 0.20, color=GREEN)
    arrow(ax, 0.765, 0.29, 0.765, 0.20, color=ORANGE)

    ax.text(
        0.50,
        0.015,
        "Neither branch supplies one field-independent automaton or one all-depth scalar law.",
        ha="center",
        va="bottom",
        fontsize=10.8,
        fontweight="bold",
        color=GRAY_2,
    )
    save(fig, str(HERE), "fig1_prefix_pole_semantics")


if __name__ == "__main__":
    prefix_pole_semantics()
    print(f"Wrote Paper XXI figures to {HERE}")
