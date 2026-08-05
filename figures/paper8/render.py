"""Render the typed Paper VIII definition figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "figures" / "paper8"
sys.path.insert(0, str(ROOT))

from figures.style import save_figure


BLUE = "#24567a"
TEAL = "#17725f"
ORANGE = "#c36f1f"
PURPLE = "#6e4b9e"
RED = "#b6423a"
INK = "#27333d"
MUTED = "#65727b"
LIGHT_BLUE = "#f3f8fc"
LIGHT_TEAL = "#f1faf6"
LIGHT_ORANGE = "#fff7ed"
LIGHT_PURPLE = "#f8f4fc"
LIGHT_RED = "#fff4f2"
LIGHT_GRAY = "#f7f8f8"
GRID = "#cbd4d8"


def clean_axes(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def rounded_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    heading: str,
    body: str,
    *,
    edge: str = BLUE,
    face: str = LIGHT_BLUE,
    body_size: float = 9.0,
    heading_size: float = 11.0,
    heading_color: str | None = None,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1.5,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h - 0.035,
        heading,
        ha="center",
        va="top",
        fontsize=heading_size,
        fontweight="bold",
        color=heading_color or edge,
    )
    ax.text(
        x + w / 2,
        y + h / 2 - 0.008,
        body,
        ha="center",
        va="center",
        fontsize=body_size,
        color=INK,
        linespacing=1.25,
    )


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = MUTED,
    dashed: bool = False,
    label: str | None = None,
    label_offset: tuple[float, float] = (0.0, 0.0),
) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "lw": 1.35,
            "color": color,
            "linestyle": "--" if dashed else "-",
            "shrinkA": 2,
            "shrinkB": 2,
        },
    )
    if label:
        x = (start[0] + end[0]) / 2 + label_offset[0]
        y = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(x, y, label, ha="center", va="center", fontsize=7.4, color=MUTED)


def figure_1() -> None:
    fig, ax = plt.subplots(figsize=(14.2, 8.6))
    clean_axes(ax)
    ax.text(0.03, 0.96, "Typed SOF Object Language", fontsize=18, fontweight="bold", color=INK)
    ax.text(
        0.03,
        0.925,
        "Static data, typed finite filtrations, and saturated closures are distinct objects.",
        fontsize=10.5,
        color=MUTED,
    )

    rounded_box(
        ax,
        0.04,
        0.785,
        0.92,
        0.12,
        "spectral gates for spectrally derived moving sectors only",
        r"$M \supset \Sigma_{\mathrm{comm}} \supset \Sigma_{\mathrm{normal}} "
        r"\supset \Sigma_{\mathrm{spec}}^{(\nu)} \longrightarrow \{Q_i(w)\}$",
        edge=GRID,
        face=LIGHT_GRAY,
        body_size=9,
        heading_size=10,
        heading_color=INK,
    )
    ax.text(
        0.5,
        0.75,
        "carrier declaration; construction/audit order, not implication",
        ha="center",
        fontsize=11,
        color=MUTED,
        style="italic",
    )

    columns = [(0.04, 0.28), (0.355, 0.28), (0.67, 0.28)]
    rounded_box(
        ax,
        columns[0][0],
        0.17,
        columns[0][1],
        0.56,
        "marked static data",
        r"$D_Q=\mathrm{span}_{\mathbf{C}}\{Q_i\}$" "\n\n"
        r"labelled alphabet $Y=\{Y_a\}$" "\n\n"
        r"$E_Y=\mathrm{span}\{I,Y_a,Y_a^*\}$" "\n\n"
        r"$S_{Q,Y}=D_Q+E_Y$" "\n\n"
        r"optional $(X,H_{\mathrm{Hall}})$",
        edge=BLUE,
        face=LIGHT_BLUE,
        body_size=10,
    )
    rounded_box(
        ax,
        columns[1][0],
        0.17,
        columns[1][1],
        0.56,
        "typed finite filtrations",
        r"$B_{ij}^{a}=Q_iY_aQ_j$" "\n"
        r"$R_1[Y]$" "\n\n"
        r"$\mathrm{Route}_d[Y]\quad|\quad W_d[Y]$" "\n"
        r"$D_{\mathrm{route}}[Y]\quad|\quad D_{\mathrm{word}}[Y]$" "\n\n"
        r"$R_1^{\mathrm{Lie}}\quad|\quad R_2^{\mathrm{Lie}}$" "\n"
        r"$D_{\mathrm{Lie}}$ (independent carrier)",
        edge=TEAL,
        face=LIGHT_TEAL,
        body_size=10,
    )
    rounded_box(
        ax,
        columns[2][0],
        0.17,
        columns[2][1],
        0.56,
        "three saturated closures",
        r"$A_Y^+=\mathrm{alg}_{\mathbf{C}}(I,Y)$" "\n\n"
        r"$A_Y^*=C^*(Y)$" "\n\n"
        r"$A_{Q,Y}^*=C^*(D_Q\cup Y)$" "\n\n"
        r"closure, not first-hit depth",
        edge=PURPLE,
        face=LIGHT_PURPLE,
        body_size=10,
    )

    arrow(ax, (0.335, 0.46), (0.35, 0.46), color=GRID)
    arrow(ax, (0.65, 0.46), (0.665, 0.46), color=GRID)
    ax.text(
        0.5,
        0.105,
        "Dashed promotion gates require additional computation; labels and word length flow from "
        r"$Y$, not from $E_Y$ or a saturated closure.",
        ha="center",
        fontsize=9.5,
        color=RED,
    )
    ax.text(
        0.5,
        0.065,
        "Operator/word and Lie/Hall branches are not equivalent without carrier alignment and a bridge theorem.",
        ha="center",
        fontsize=9.5,
        color=MUTED,
        style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig1_sof_definition")


def figure_2() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 7.6))
    clean_axes(ax)
    ax.text(0.03, 0.955, "Sectorization Necessity", fontsize=18, fontweight="bold", color=INK)
    ax.text(
        0.03,
        0.915,
        "The SOF shadows are sector-indexed; a global observable family alone does not define them.",
        fontsize=11,
        color=MUTED,
    )

    rounded_box(
        ax,
        0.07,
        0.57,
        0.34,
        0.19,
        "without a declared sectorization",
        r"$V,\ Y$ only",
        edge=RED,
        face=LIGHT_RED,
        body_size=12,
    )
    rounded_box(
        ax,
        0.59,
        0.57,
        0.34,
        0.19,
        "with a compatible sectorization",
        r"$V,\ \{Q_i\},\ Y$",
        edge=TEAL,
        face=LIGHT_TEAL,
        body_size=12,
    )
    ax.plot([0.5, 0.5], [0.16, 0.79], color=GRID, lw=1.2)

    ax.text(
        0.24,
        0.40,
        "no sector labels\nno corner blocks\nno route separators\nno sector-indexed shadow",
        ha="center",
        va="center",
        fontsize=11,
        color=INK,
        linespacing=1.5,
    )
    ax.text(
        0.76,
        0.40,
        r"$B_{ij}^{a}=Q_iY_aQ_j$" "\n"
        r"$R_1[Y]$ and $\mathrm{Route}_d[Y]$" "\n"
        r"$W_d[Y]$ and typed depths" "\n"
        "wall records only after a deformation is declared",
        ha="center",
        va="center",
        fontsize=10.4,
        color=INK,
        linespacing=1.45,
    )
    rounded_box(
        ax,
        0.10,
        0.14,
        0.28,
        0.15,
        "global diagnostics may exist",
        "but they are not sector shadows",
        edge=RED,
        face=LIGHT_RED,
        body_size=8.8,
    )
    rounded_box(
        ax,
        0.62,
        0.14,
        0.28,
        0.15,
        "typed SOF diagnostics",
        "become defined after realization",
        edge=TEAL,
        face=LIGHT_TEAL,
        body_size=8.8,
    )
    ax.text(
        0.5,
        0.065,
        "No-Sector No-Shadow is a definitional necessity principle, not a classification theorem.",
        ha="center",
        fontsize=10,
        color=MUTED,
        style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig2_no_sector_no_shadow")


def figure_3() -> None:
    fig, ax = plt.subplots(figsize=(14.0, 8.0))
    clean_axes(ax)
    ax.text(0.03, 0.955, "Strict SOF Morphism", fontsize=18, fontweight="bold", color=INK)
    ax.text(
        0.03,
        0.915,
        "A static strict morphism preserves marked sectors and labelled carriers on a reducing image.",
        fontsize=11,
        color=MUTED,
    )

    rounded_box(
        ax,
        0.05,
        0.67,
        0.28,
        0.15,
        r"$\mathrm{F}$",
        r"$(V,\{Q_i\},Y;X,\mathrm{H})$",
        edge=BLUE,
        face=LIGHT_BLUE,
        body_size=11,
    )
    rounded_box(
        ax,
        0.67,
        0.67,
        0.28,
        0.15,
        r"$\mathrm{F}'$",
        r"$(V',\{Q'_{i'}\},Y';X',\mathrm{H}')$",
        edge=BLUE,
        face=LIGHT_BLUE,
        body_size=11,
    )
    arrow(
        ax,
        (0.35, 0.745),
        (0.65, 0.745),
        color=BLUE,
        label=r"$\Phi=(U,f,\phi,\psi)$",
        label_offset=(0.0, 0.035),
    )

    rounded_box(
        ax,
        0.07,
        0.42,
        0.25,
        0.13,
        "sector map",
        r"$UQ_iU^*=Q'_{f(i)}$",
        edge=TEAL,
        face=LIGHT_TEAL,
        body_size=8.8,
    )
    rounded_box(
        ax,
        0.375,
        0.42,
        0.25,
        0.13,
        "operator carrier",
        r"$UY_aU^*=P_fY'_{\phi(a)}P_f$",
        edge=ORANGE,
        face=LIGHT_ORANGE,
        body_size=8.8,
    )
    rounded_box(
        ax,
        0.68,
        0.42,
        0.25,
        0.13,
        "optional Lie/Hall carrier",
        r"$UX_gU^*=P_fX'_{\psi(g)}P_f$",
        edge=PURPLE,
        face=LIGHT_PURPLE,
        body_size=8.8,
    )
    ax.text(0.5, 0.595, "intertwining conditions", ha="center", fontsize=9, color=MUTED, style="italic")

    rounded_box(
        ax,
        0.08,
        0.13,
        0.39,
        0.16,
        "operator/word functoriality",
        r"$R_1[Y],\ \mathrm{Route}_d[Y],\ W_d[Y]$"
        "\n"
        "source witnesses map forward; target depths do not increase",
        edge=TEAL,
        face=LIGHT_TEAL,
        body_size=9,
    )
    rounded_box(
        ax,
        0.53,
        0.13,
        0.39,
        0.16,
        "Lie/Hall functoriality",
        r"$R_1^{\mathrm{Lie}},\ R_2^{\mathrm{Lie}},\ D_{\mathrm{Lie}}$"
        "\n"
        "requires a registered carrier; target depth does not increase",
        edge=PURPLE,
        face=LIGHT_PURPLE,
        body_size=9,
    )
    arrow(
        ax,
        (0.50, 0.40),
        (0.28, 0.29),
        color=TEAL,
        dashed=True,
        label="construction/audit order",
        label_offset=(0.0, 0.035),
    )
    arrow(
        ax,
        (0.50, 0.40),
        (0.72, 0.29),
        color=PURPLE,
        dashed=True,
        label="construction/audit order",
        label_offset=(0.0, 0.035),
    )
    ax.text(
        0.5,
        0.085,
        "Strict static category; deformation arrows and weak comparisons belong to Paper IX.",
        ha="center",
        fontsize=10,
        color=RED,
        style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig3_strict_morphism")


def main() -> None:
    figure_1()
    figure_2()
    figure_3()
    print(f"Paper VIII figures written to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
