"""Render the Paper XXV transport-decomposition and information-lattice figure."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import (  # noqa: E402
    BLUE,
    BLUE_DARK,
    GREEN,
    ORANGE,
    arrow,
    box,
    clean,
    setup,
    title,
)


HERE = Path(__file__).resolve().parent


def transport_information_lattice() -> None:
    fig, ax = setup((13.8, 8.0))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Aligned Change Separates Before It Is Bounded",
        "Three typed perturbation terms feed an information-refinement lattice",
    )

    box(
        ax,
        0.035,
        0.70,
        0.27,
        0.11,
        "Left-carrier motion",
        r"$\Delta_i\bar Y_aQ'_j$",
        edge=BLUE,
        fill="#eef5fa",
    )
    box(
        ax,
        0.365,
        0.70,
        0.27,
        0.11,
        "Additive operator error",
        r"$Q'_iE_aQ'_j$",
        edge=ORANGE,
        fill="#fff6e8",
    )
    box(
        ax,
        0.695,
        0.70,
        0.27,
        0.11,
        "Right-carrier motion",
        r"$\bar Q_i\bar Y_a\Delta_j$",
        edge=BLUE,
        fill="#eef5fa",
    )
    box(
        ax,
        0.365,
        0.52,
        0.27,
        0.10,
        "Exact block difference",
        r"$D_a(i,j)=T_L+T_E+T_R$",
        edge=BLUE_DARK,
        fill="#f5f9fc",
    )
    for x in (0.17, 0.50, 0.83):
        arrow(ax, x, 0.70, 0.50, 0.62, color=BLUE_DARK)

    ax.text(
        0.50,
        0.45,
        r"$\|D_a(i,j)\|_F\leq b_{\rm loc}\leq b_{\rm glob}$",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=BLUE_DARK,
    )

    box(ax, 0.44, 0.33, 0.12, 0.06, "Local", r"$I_{\rm loc}$", edge=GREEN, fill="#eef8f1", body_size=8.8)
    box(ax, 0.44, 0.23, 0.12, 0.06, "Two-sided", r"$I_{LR}$", edge=GREEN, fill="#eef8f1", body_size=8.8)
    box(ax, 0.25, 0.13, 0.12, 0.06, "Left", r"$I_L$", edge=ORANGE, fill="#fff6e8", body_size=8.8)
    box(ax, 0.63, 0.13, 0.12, 0.06, "Right", r"$I_R$", edge=ORANGE, fill="#fff6e8", body_size=8.8)
    box(ax, 0.44, 0.04, 0.12, 0.06, "Global", r"$I_G$", edge=BLUE_DARK, fill="#f5f9fc", body_size=8.8)
    arrow(ax, 0.50, 0.33, 0.50, 0.28, color=GREEN)
    arrow(ax, 0.48, 0.22, 0.34, 0.19, color=ORANGE)
    arrow(ax, 0.52, 0.22, 0.66, 0.19, color=ORANGE)
    arrow(ax, 0.31, 0.12, 0.47, 0.10, color=BLUE_DARK)
    arrow(ax, 0.69, 0.12, 0.53, 0.10, color=BLUE_DARK)

    fig.savefig(
        HERE / "fig1_transport_information_lattice.png",
        bbox_inches="tight",
        dpi=180,
    )
    fig.savefig(
        HERE / "fig1_transport_information_lattice.pdf",
        bbox_inches="tight",
    )


if __name__ == "__main__":
    transport_information_lattice()
    print(f"Wrote Paper XXV figure to {HERE}")
