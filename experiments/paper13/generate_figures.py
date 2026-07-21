"""Generate the eight canonical figures for Paper XIII.

The figures use one visual grammar throughout: reports/alignment are blue,
fixed-fiber geometry is teal, and interpretation or open boundaries are orange.
Both vector PDF and review PNG outputs are written to figures/paper13/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "figures" / "paper13"

NAVY = "#173B57"
BLUE = "#2F6F9F"
BLUE_LIGHT = "#DDECF5"
TEAL = "#2A7F78"
TEAL_LIGHT = "#DDEFEA"
ORANGE = "#C56B2D"
ORANGE_LIGHT = "#F5E6D8"
GRAY = "#66727A"
GRAY_LIGHT = "#EDF0F2"
INK = "#172126"
WHITE = "#FFFFFF"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "mathtext.fontset": "dejavusans",
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "savefig.facecolor": WHITE,
    }
)


def canvas(width: float = 12.0, height: float = 6.2):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    subtitle: str = "",
    *,
    face: str = WHITE,
    edge: str = NAVY,
    linestyle: str = "-",
    linewidth: float = 1.7,
    title_size: float = 12,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=face,
        edgecolor=edge,
        linewidth=linewidth,
        linestyle=linestyle,
    )
    ax.add_patch(patch)
    cy = y + h / 2
    ax.text(
        x + w / 2,
        cy + (0.035 if subtitle else 0),
        title,
        ha="center",
        va="center",
        color=INK,
        fontsize=title_size,
        fontweight="bold",
    )
    if subtitle:
        ax.text(
            x + w / 2,
            cy - 0.045,
            subtitle,
            ha="center",
            va="center",
            color=GRAY,
            fontsize=9.5,
            linespacing=1.25,
        )
    return patch


def arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = NAVY,
    style: str = "-",
    width: float = 1.8,
    head: float = 15,
    connectionstyle: str = "arc3",
):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=head,
        linewidth=width,
        linestyle=style,
        color=color,
        connectionstyle=connectionstyle,
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(patch)
    return patch


def label(ax, x: float, y: float, text: str, *, color: str = GRAY, size: float = 10):
    ax.text(x, y, text, ha="center", va="center", color=color, fontsize=size)


def save(fig, stem: str):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(
        OUTPUT / f"{stem}.png",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(fig)


def figure_1_graphical_abstract():
    fig, ax = canvas(12.5, 6.0)
    ax.set_title("From SOF Reports to an Aligned Audit", color=NAVY, pad=12)

    box(ax, 0.03, 0.61, 0.15, 0.17, "System A", "source realization", face=GRAY_LIGHT)
    box(ax, 0.03, 0.22, 0.15, 0.17, "System B", "source realization", face=GRAY_LIGHT)
    box(ax, 0.24, 0.61, 0.17, 0.17, "SOF Report", r"$\mathcal R^\star$", face=BLUE_LIGHT, edge=BLUE)
    box(ax, 0.24, 0.22, 0.17, 0.17, "SOF Report", r"$\widehat{\mathcal R}$", face=BLUE_LIGHT, edge=BLUE)
    box(
        ax,
        0.47,
        0.39,
        0.18,
        0.22,
        "Alignment",
        r"$\Phi_{\rm sec},\;\Phi_{\rm obs},\;\Theta$",
        face=TEAL_LIGHT,
        edge=TEAL,
    )
    box(
        ax,
        0.71,
        0.39,
        0.14,
        0.22,
        "SOF Audit",
        r"$\Delta_{\rm audit}$",
        face=BLUE_LIGHT,
        edge=BLUE,
    )
    box(
        ax,
        0.89,
        0.39,
        0.09,
        0.22,
        "Interpretation",
        "downstream",
        face=ORANGE_LIGHT,
        edge=ORANGE,
        title_size=10.5,
    )

    arrow(ax, (0.18, 0.695), (0.24, 0.695), color=GRAY)
    arrow(ax, (0.18, 0.305), (0.24, 0.305), color=GRAY)
    arrow(ax, (0.41, 0.695), (0.47, 0.55), color=BLUE)
    arrow(ax, (0.41, 0.305), (0.47, 0.45), color=BLUE)
    arrow(ax, (0.65, 0.50), (0.71, 0.50), color=TEAL)
    arrow(ax, (0.85, 0.50), (0.89, 0.50), color=ORANGE, style="--")

    label(ax, 0.50, 0.14, "Reporting", color=BLUE, size=11)
    arrow(ax, (0.56, 0.14), (0.62, 0.14), color=GRAY, head=11)
    label(ax, 0.69, 0.14, "Alignment", color=TEAL, size=11)
    arrow(ax, (0.75, 0.14), (0.81, 0.14), color=GRAY, head=11)
    label(ax, 0.86, 0.14, "Audit", color=BLUE, size=11)
    ax.text(
        0.935,
        0.30,
        "difference first,\nmeaning later",
        ha="center",
        va="center",
        fontsize=9,
        color=ORANGE,
    )
    save(fig, "fig1_report_to_audit")


def figure_2_alignment_fiber():
    fig, ax = canvas(12.2, 6.4)
    ax.set_title("Local Comparison Geometry on an Alignment Fiber", color=NAVY, pad=12)

    ellipse_t = np.linspace(0, 2 * np.pi, 300)
    ax.fill(
        0.50 + 0.39 * np.cos(ellipse_t),
        0.49 + 0.35 * np.sin(ellipse_t),
        color=GRAY_LIGHT,
        alpha=0.65,
        zorder=0,
    )
    ax.plot(
        0.50 + 0.39 * np.cos(ellipse_t),
        0.49 + 0.35 * np.sin(ellipse_t),
        color=GRAY,
        linewidth=1.2,
    )
    ax.text(0.18, 0.81, "report space", color=GRAY, fontsize=11, fontweight="bold")

    fiber = FancyBboxPatch(
        (0.29, 0.24),
        0.44,
        0.48,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor=TEAL_LIGHT,
        edgecolor=TEAL,
        linewidth=2.1,
    )
    ax.add_patch(fiber)
    ax.text(
        0.51,
        0.68,
        r"fixed fiber $\mathfrak F_{\Phi,\Theta}$",
        ha="center",
        color=TEAL,
        fontsize=12,
        fontweight="bold",
    )

    points = {
        r"$\mathcal R_1$": (0.37, 0.49),
        r"$\mathcal R_2$": (0.52, 0.35),
        r"$\mathcal R_3$": (0.64, 0.52),
    }
    for name, (x, y) in points.items():
        ax.add_patch(Circle((x, y), 0.018, facecolor=BLUE, edgecolor=NAVY, linewidth=1.0))
        ax.text(x, y + 0.045, name, ha="center", color=INK, fontsize=10)
    ax.plot([0.37, 0.52], [0.49, 0.35], color=TEAL, linewidth=2.2)
    ax.text(0.445, 0.39, r"$d_{\Phi,\Theta}$", color=TEAL, fontsize=11, fontweight="bold")

    ax.add_patch(Circle((0.80, 0.67), 0.018, facecolor=ORANGE, edgecolor=ORANGE, linewidth=1.0))
    ax.text(0.82, 0.71, r"$\mathcal R'$", color=INK, fontsize=10)
    arrow(ax, (0.72, 0.62), (0.79, 0.67), color=ORANGE, style="--")
    ax.text(
        0.84,
        0.56,
        "different alignment\nor comparison semantics",
        ha="center",
        color=ORANGE,
        fontsize=9.5,
    )
    ax.text(
        0.51,
        0.18,
        "Pseudometric comparisons are defined inside a fixed fiber;\ncross-fiber transport is not defined in Paper XIII.",
        ha="center",
        va="top",
        color=INK,
        fontsize=10.5,
    )
    save(fig, "fig2_alignment_fiber")


def figure_3_audit_signature():
    fig, ax = canvas(13.0, 6.0)
    ax.set_title("The Eight-Coordinate Audit Signature", color=NAVY, pad=12)
    names = [
        ("Support", r"$\Delta_{\rm supp}$"),
        ("Word bridge", r"$\Delta_{\rm brw}$"),
        ("Lie bridge", r"$\Delta_{\rm brl}$"),
        ("Depth", r"$\Delta_{\rm dep}$"),
        ("Frozen", r"$\Delta_{\rm frz}$"),
        ("Constraint", r"$\Delta_{\rm cns}$"),
        ("Response", r"$\Delta_{\rm act}$"),
        ("Wall record", r"$\Delta_{\rm wal}$"),
    ]
    x0, total_w, gap = 0.035, 0.93, 0.008
    w = (total_w - 7 * gap) / 8
    for i, (name, symbol) in enumerate(names):
        x = x0 + i * (w + gap)
        face = TEAL_LIGHT if i < 5 else (ORANGE_LIGHT if i >= 5 else BLUE_LIGHT)
        edge = TEAL if i < 5 else ORANGE
        box(ax, x, 0.38, w, 0.25, name, symbol, face=face, edge=edge, title_size=9.8)
        ax.text(x + w / 2, 0.31, str(i + 1), ha="center", color=edge, fontsize=10, fontweight="bold")

    ax.text(0.31, 0.73, "structural sub-signature", ha="center", color=TEAL, fontsize=11, fontweight="bold")
    ax.plot([0.04, 0.59], [0.70, 0.70], color=TEAL, linewidth=2)
    ax.text(0.79, 0.73, "directional / path-dependent coordinates", ha="center", color=ORANGE, fontsize=11, fontweight="bold")
    ax.plot([0.61, 0.965], [0.70, 0.70], color=ORANGE, linewidth=2)

    box(
        ax,
        0.11,
        0.12,
        0.34,
        0.11,
        "Fixed-fiber pseudometric",
        "proved for retained structural coordinates",
        face=TEAL_LIGHT,
        edge=TEAL,
        title_size=10.5,
    )
    box(
        ax,
        0.55,
        0.12,
        0.34,
        0.11,
        "Full-signature geometry",
        "requires additional laws",
        face=ORANGE_LIGHT,
        edge=ORANGE,
        linestyle="--",
        title_size=10.5,
    )
    save(fig, "fig3_audit_signature")


def figure_4_word_lie():
    fig, ax = canvas(12.2, 6.1)
    ax.set_title("Word and Lie Transport Are Distinct Channels", color=NAVY, pad=12)

    for panel_x, panel_title, panel_color in [
        (0.06, "Word channel", TEAL),
        (0.55, "Lie channel", ORANGE),
    ]:
        ax.text(panel_x + 0.19, 0.79, panel_title, ha="center", color=panel_color, fontsize=13, fontweight="bold")
        for idx, x in enumerate([panel_x + 0.05, panel_x + 0.19, panel_x + 0.33]):
            ax.add_patch(Circle((x, 0.51), 0.043, facecolor=WHITE, edgecolor=NAVY, linewidth=2))
            ax.text(x, 0.51, str(idx), ha="center", va="center", color=INK, fontsize=12, fontweight="bold")
        arrow(ax, (panel_x + 0.095, 0.51), (panel_x + 0.145, 0.51), color=BLUE, head=13)
        arrow(ax, (panel_x + 0.235, 0.51), (panel_x + 0.285, 0.51), color=BLUE, head=13)

    curved = FancyArrowPatch(
        (0.11, 0.57),
        (0.39, 0.57),
        arrowstyle="-|>",
        connectionstyle="arc3,rad=-0.38",
        mutation_scale=16,
        linewidth=2.5,
        color=TEAL,
    )
    ax.add_patch(curved)
    ax.text(0.25, 0.69, r"$Q_2X^2Q_0\neq0$", ha="center", color=TEAL, fontsize=12, fontweight="bold")

    ax.plot([0.60, 0.88], [0.64, 0.38], color=ORANGE, linewidth=2.5)
    ax.plot([0.60, 0.88], [0.38, 0.64], color=ORANGE, linewidth=2.5)
    ax.text(0.74, 0.69, r"$[X,X]=0$", ha="center", color=ORANGE, fontsize=12, fontweight="bold")
    ax.text(0.74, 0.27, "no Lie repair", ha="center", color=ORANGE, fontsize=10.5)

    ax.text(
        0.50,
        0.10,
        "The same sectorization supports length-two word accessibility without Lie accessibility.",
        ha="center",
        color=INK,
        fontsize=11,
    )
    save(fig, "fig4_word_lie_separation")


def figure_5_portability():
    fig, ax = canvas(12.8, 6.4)
    ax.set_title("Protocol Portability Across Controlled Domains", color=NAVY, pad=12)

    domains = [
        ("GridWorld", "cells / actions"),
        ("SIR", "compartments / rates"),
        ("Traffic", "nodes / phases"),
        ("Compiler IR", "blocks / CFG + def-use"),
    ]
    ys = [0.76, 0.59, 0.42, 0.25]
    for (name, sub), y in zip(domains, ys):
        box(ax, 0.035, y - 0.055, 0.20, 0.11, name, sub, face=GRAY_LIGHT, edge=GRAY, title_size=10.5)
        box(ax, 0.29, y - 0.055, 0.19, 0.11, "Report pair", r"$\mathcal R^\star,\widehat{\mathcal R}$", face=BLUE_LIGHT, edge=BLUE, title_size=10.5)
        arrow(ax, (0.235, y), (0.29, y), color=GRAY, head=12)
        arrow(ax, (0.48, y), (0.56, 0.505), color=BLUE, head=12)

    box(
        ax,
        0.56,
        0.38,
        0.18,
        0.25,
        "Alignment map",
        r"$\operatorname{Compare}_{\Theta}$",
        face=TEAL_LIGHT,
        edge=TEAL,
    )
    box(
        ax,
        0.80,
        0.38,
        0.16,
        0.25,
        "Typed signature",
        "support / bridges /\ndepth / response / walls",
        face=BLUE_LIGHT,
        edge=BLUE,
        title_size=10.8,
    )
    arrow(ax, (0.74, 0.505), (0.80, 0.505), color=TEAL)
    ax.text(
        0.65,
        0.18,
        "Same comparison grammar; domain-specific sectors, observables, and signatures.",
        ha="center",
        color=INK,
        fontsize=11,
    )
    save(fig, "fig5_protocol_portability")


def figure_6_regimes():
    fig, ax = canvas(12.6, 6.2)
    ax.set_title("Alignment Regimes and Evidence Boundary", color=NAVY, pad=12)
    regimes = [
        (0.055, "A", "Controlled reference", "explicit sectors and observables", "validated here", BLUE_LIGHT, BLUE),
        (0.37, "B", "Aligned latent model", "latent-to-reference correspondence", "future application", TEAL_LIGHT, TEAL),
        (0.685, "C", "Black-box behavioral", "semantic probe correspondence", "future application", ORANGE_LIGHT, ORANGE),
    ]
    for x, code, title, requirement, status, face, edge in regimes:
        box(ax, x, 0.34, 0.26, 0.34, title, requirement, face=face, edge=edge, title_size=11.5)
        ax.add_patch(Circle((x + 0.04, 0.72), 0.027, facecolor=edge, edgecolor=edge))
        ax.text(x + 0.04, 0.72, code, ha="center", va="center", color=WHITE, fontweight="bold")
        ax.text(x + 0.13, 0.28, status, ha="center", color=edge, fontsize=10, fontweight="bold")

    arrow(ax, (0.29, 0.51), (0.36, 0.51), color=GRAY, head=13)
    arrow(ax, (0.605, 0.51), (0.675, 0.51), color=GRAY, head=13)
    ax.text(0.50, 0.16, "increasing uncertainty in the alignment object", ha="center", color=GRAY, fontsize=11)
    ax.plot([0.16, 0.84], [0.12, 0.12], color=GRAY, linewidth=1.2)
    ax.text(0.16, 0.08, "declared finite alignment", ha="center", color=GRAY, fontsize=9.5)
    ax.text(0.84, 0.08, "semantic alignment only", ha="center", color=GRAY, fontsize=9.5)
    save(fig, "fig6_alignment_regimes")


def figure_7_stability_boundary():
    fig, ax = canvas(13.0, 6.3)
    ax.set_title("Stability Controls and Their Boundary", color=NAVY, pad=12)

    panels = [
        (0.03, "Permutation", "equivariant after\ndeclared relabeling", TEAL_LIGHT, TEAL),
        (0.27, "Rescaling", "stable while blocks\nremain away from $\tau$", TEAL_LIGHT, TEAL),
        (0.51, "Threshold crossing", "support changes when\nblock magnitudes cross $\tau$", ORANGE_LIGHT, ORANGE),
        (0.75, "Refinement", "coarse/fine pushforward\nnot defined", WHITE, ORANGE),
    ]
    for x, title, sub, face, edge in panels:
        box(
            ax,
            x,
            0.34,
            0.21,
            0.30,
            title,
            sub,
            face=face,
            edge=edge,
            linestyle="--" if title == "Refinement" else "-",
            title_size=11,
        )

    for x in [0.235, 0.475, 0.715]:
        arrow(ax, (x, 0.49), (x + 0.025, 0.49), color=GRAY, head=11)
    ax.text(0.36, 0.75, "fixed-fiber controls", ha="center", color=TEAL, fontsize=11, fontweight="bold")
    ax.plot([0.05, 0.48], [0.71, 0.71], color=TEAL, linewidth=2)
    ax.text(0.73, 0.75, "boundary cases", ha="center", color=ORANGE, fontsize=11, fontweight="bold")
    ax.plot([0.52, 0.95], [0.71, 0.71], color=ORANGE, linewidth=2)
    ax.text(
        0.50,
        0.20,
        "Stability is conditional on the declared fiber and threshold semantics.",
        ha="center",
        color=INK,
        fontsize=11,
    )
    save(fig, "fig7_stability_boundary")


def figure_8_geometry_outlook():
    fig, ax = canvas(12.6, 6.3)
    ax.set_title("Comparison Geometry Beyond a Single Fiber", color=NAVY, pad=12)

    fibers = [
        (0.07, 0.42, r"$\mathfrak F_{\Phi_1,\Theta_1}$"),
        (0.39, 0.57, r"$\mathfrak F_{\Phi_2,\Theta_2}$"),
        (0.71, 0.34, r"$\mathfrak F_{\Phi_3,\Theta_3}$"),
    ]
    for x, y, name in fibers:
        patch = FancyBboxPatch(
            (x, y),
            0.22,
            0.24,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=TEAL_LIGHT,
            edgecolor=TEAL,
            linewidth=2,
        )
        ax.add_patch(patch)
        ax.text(x + 0.11, y + 0.205, name, ha="center", color=TEAL, fontsize=11, fontweight="bold")
        for dx, dy in [(0.06, 0.08), (0.11, 0.13), (0.16, 0.075)]:
            ax.add_patch(Circle((x + dx, y + dy), 0.012, facecolor=BLUE, edgecolor=NAVY, linewidth=0.8))
        ax.plot([x + 0.06, x + 0.11, x + 0.16], [y + 0.08, y + 0.13, y + 0.075], color=TEAL, linewidth=1.6)

    arrow(ax, (0.29, 0.58), (0.39, 0.64), color=ORANGE, style="--")
    arrow(ax, (0.61, 0.60), (0.71, 0.51), color=ORANGE, style="--")
    ax.text(0.35, 0.72, "pushforward?", ha="center", color=ORANGE, fontsize=10, fontweight="bold")
    ax.text(0.68, 0.63, "transition law?", ha="center", color=ORANGE, fontsize=10, fontweight="bold")

    box(
        ax,
        0.29,
        0.13,
        0.42,
        0.13,
        "Open comparison geometry",
        "refinement maps / changing observables / path synchronization",
        face=ORANGE_LIGHT,
        edge=ORANGE,
        linestyle="--",
        title_size=11,
    )
    ax.text(
        0.50,
        0.86,
        "Paper XIII proves local geometry inside each fiber.",
        ha="center",
        color=INK,
        fontsize=11,
    )
    save(fig, "fig8_comparison_geometry_outlook")


def main():
    figure_1_graphical_abstract()
    figure_2_alignment_fiber()
    figure_3_audit_signature()
    figure_4_word_lie()
    figure_5_portability()
    figure_6_regimes()
    figure_7_stability_boundary()
    figure_8_geometry_outlook()
    print(f"wrote 8 figures to {OUTPUT}")


if __name__ == "__main__":
    main()
