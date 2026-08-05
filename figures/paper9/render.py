"""Render the typed Paper IX dynamics figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "figures" / "paper9"
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
GRID = "#cbd4d8"


def box(ax, x, y, w, h, title, body, edge=BLUE, face=LIGHT_BLUE, size=10):
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1.5, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h - 0.035, title, ha="center", va="top",
            fontsize=9, fontweight="bold", color=edge)
    ax.text(x + w / 2, y + h / 2 - 0.008, body, ha="center", va="center",
            fontsize=size, color=INK, linespacing=1.3)


def arrow(ax, start, end, color=MUTED, dashed=False, label=None, dy=0.025):
    ax.annotate("", xy=end, xytext=start, arrowprops={
        "arrowstyle": "-|>", "lw": 1.35, "color": color,
        "linestyle": "--" if dashed else "-", "shrinkA": 2, "shrinkB": 2,
    })
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + dy,
                label, ha="center", va="center", fontsize=8, color=MUTED)


def clean(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def figure_1():
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    clean(ax)
    ax.text(.03, .95, "Typed Observable Trajectory", fontsize=18,
            fontweight="bold", color=INK)
    ax.text(.03, .91, "A typed chart makes fibres comparable; a selected path then defines a trajectory.",
            fontsize=11, color=MUTED)
    box(ax, .04, .61, .26, .18, "typed chart on U",
        r"$\mathcal{V}\to U;\ I,A,G_0$"
        "\nfixed word / Hall rules", BLUE, LIGHT_BLUE, 9.5)
    box(ax, .37, .61, .26, .18, "comparison field",
        r"$J_{\kappa}=\Theta_{\kappa}(\mathrm{fibre\ data})$"
        "\n" r"$U\to\mathcal{E}_{\kappa}$", ORANGE, LIGHT_ORANGE, 9.5)
    box(ax, .70, .61, .26, .18, "selected trajectory",
        r"$\gamma:I_{\gamma}\to U$"
        "\n" r"$O_{\kappa,\gamma}=\widehat O_{\kappa}J_{\kappa}\gamma$",
        TEAL, LIGHT_TEAL, 9.5)
    arrow(ax, (.31, .70), (.36, .70), BLUE, label="extract")
    arrow(ax, (.64, .70), (.69, .70), TEAL, label="select path")
    box(ax, .12, .24, .31, .20, "operator / word",
        r"$R_1[Y]\quad|\quad \mathrm{Route}_d[Y]\quad|\quad W_d[Y]$"
        "\n" r"$D_{\mathrm{route}}^{(\leq d_{\max})}\quad|\quad D_{\mathrm{word}}^{(\leq d_{\max})}$",
        TEAL, LIGHT_TEAL, 9.5)
    box(ax, .56, .24, .31, .20, "Lie / Hall",
        r"$R_1^{\mathrm{Lie}}\quad|\quad R_2^{\mathrm{Lie}}\quad|\quad D_{\mathrm{Lie}}^{(\leq d_{\max})}$"
        "\n" "independently registered", PURPLE, LIGHT_PURPLE, 9.5)
    arrow(ax, (.82, .595), (.30, .45), TEAL, dashed=True, label="selected carrier", dy=.015)
    arrow(ax, (.82, .595), (.72, .45), PURPLE, dashed=True, label="selected carrier", dy=.015)
    ax.text(.5, .10, "construction / audit order; no cross-branch implication is drawn",
            ha="center", fontsize=11, color=RED, style="italic")
    save_figure(fig, FIGURE_DIR, "fig1_observable_trajectory")


def figure_2():
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    clean(ax)
    ax.text(.03, .95, "Typed Wall Pullback", fontsize=18, fontweight="bold", color=INK)
    ax.text(.03, .91, "A chart field pulls a target discriminant back; a path crossing is a separate test.",
            fontsize=11, color=MUTED)
    box(ax, .05, .58, .24, .20, "typed chart U", "fixed labels + rules\ncomparison map\nadmissibility gates",
        BLUE, LIGHT_BLUE, 10)
    box(ax, .38, .58, .24, .20, "typed field", r"$J_{\kappa}:U\longrightarrow\mathcal{E}_{\kappa}$"
        "\nblock / rank / support data", TEAL, LIGHT_TEAL, 10)
    box(ax, .71, .58, .24, .20, "discriminant", r"$\Delta_{\kappa}\subset\mathcal{E}_{\kappa}$"
        "\nexact only when declared", ORANGE, LIGHT_ORANGE, 10)
    arrow(ax, (.30, .68), (.37, .68), BLUE, label="evaluate")
    arrow(ax, (.63, .68), (.70, .68), ORANGE, label="compare")
    ax.text(.5, .43, r"$\Sigma_{O_{\kappa}}\subseteq J_{\kappa}^{-1}(\Delta_{\kappa})$",
            ha="center", fontsize=15, color=INK)
    ax.text(.5, .34, "equality requires pullback-exactness for the selected shadow",
            ha="center", fontsize=10, color=RED)
    box(ax, .13, .145, .22, .135, "typed wall", r"$\Sigma_{R_1[Y]}$",
        TEAL, LIGHT_TEAL, 10)
    box(ax, .39, .145, .22, .135, "typed wall", r"$\Sigma_{R_2^{\mathrm{Lie}}}$",
        PURPLE, LIGHT_PURPLE, 10)
    box(ax, .65, .145, .22, .135, "typed wall", r"$\Sigma_{D_{\mathrm{word}}^{(\leq d_{\max})}}$",
        ORANGE, LIGHT_ORANGE, 10)
    ax.text(.5, .07, r"The package $\Sigma_{\mathrm{access}}$ is shorthand only after its typed members are enumerated.",
            ha="center", fontsize=10, color=MUTED, style="italic")
    save_figure(fig, FIGURE_DIR, "fig2_wall_pullback")


def figure_3():
    fig, ax = plt.subplots(figsize=(12.6, 7.2))
    ax.set_title("Training-Coupled NN: Continuous Proxy Response", loc="left",
                 fontsize=17, fontweight="bold", color=INK, pad=18)
    t = [0, 30, 60, 80, 120, 160]
    k0 = [0.02, .34, .52, .67, .82, .93]
    k1 = [0.01, .10, .24, .50, .75, .90]
    k2 = [0.00, .04, .10, .20, .50, .78]
    ax.plot(t, k0, "-o", color=TEAL, label=r"$K_0$ direct-block proxy")
    ax.plot(t, k1, "-o", color=BLUE, label=r"$K_1$ commutator proxy")
    ax.plot(t, k2, "-o", color=PURPLE, label=r"$K_2$ nested proxy")
    ax.axvline(60, color=TEAL, ls="--", lw=1)
    ax.axvline(80, color=BLUE, ls="--", lw=1)
    ax.axvline(120, color=PURPLE, ls="--", lw=1)
    ax.text(60, 1.01, r"$\tau_{50}=60$", ha="center", color=TEAL, fontsize=10)
    ax.text(80, .94, r"$80$", ha="center", color=BLUE, fontsize=10)
    ax.text(120, .87, r"$120$", ha="center", color=PURPLE, fontsize=10)
    ax.set_xlabel("training step")
    ax.set_ylabel("normalized continuous proxy")
    ax.set_ylim(0, 1.08)
    ax.grid(alpha=.25)
    ax.legend(frameon=False, loc="lower right")
    ax.text(.02, -.15, "Proxy-only observation: no binary D-repair and no K_i -> D_Lie bridge.",
            transform=ax.transAxes, color=RED, fontsize=11, style="italic")
    fig.tight_layout()
    save_figure(fig, FIGURE_DIR, "fig3_nn_rate_hierarchy")


def figure_5():
    fig, ax = plt.subplots(figsize=(13.2, 6.8))
    clean(ax)
    ax.text(.03, .95, "Parameter Precedent and Observable-Space Question",
            fontsize=17, fontweight="bold", color=INK)
    box(ax, .06, .54, .32, .25, "Xu--Vardi--Safran", r"$\theta_{\parallel}$"
        "\nloss-driven / fast\n"
        r"$\theta_{\perp}$" "\nweight-decay / slow", BLUE, LIGHT_BLUE, 10)
    box(ax, .62, .54, .32, .25, "SOF question", "selected typed field\n"
        r"$R_1^{\mathrm{Lie}},R_2^{\mathrm{Lie}},D_{\mathrm{Lie}}^{(\leq d_{\max})}$" "\n"
        "mechanism-separated?", TEAL, LIGHT_TEAL, 10)
    arrow(ax, (.40, .66), (.60, .66), ORANGE, dashed=True,
          label="analogy, not identification")
    ax.text(.5, .39, r"$\tau(\theta_{\parallel})\ll\tau(\theta_{\perp})$",
            ha="center", fontsize=14, color=BLUE)
    ax.text(.5, .29, r"$\tau(R_1^{\mathrm{Lie}})<\tau(R_2^{\mathrm{Lie}})<\tau(D_{\mathrm{Lie}}^{(\leq d_{\max})})$",
            ha="center", fontsize=14, color=TEAL)
    ax.text(.5, .16, "The right-hand hierarchy remains a structured-dynamics target.",
            ha="center", fontsize=11, color=RED)
    save_figure(fig, FIGURE_DIR, "fig5_xu_parameter_observable_bridge")


def figure_6():
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    clean(ax)
    ax.text(.03, .95, "SOF Deformation-Record Interface", fontsize=18,
            fontweight="bold", color=INK)
    ax.text(.03, .91, "Typed charts and comparison data support carrier-specific dynamic diagnostics.",
            fontsize=11, color=MUTED)
    box(ax, .06, .59, .22, .24, "strict static SOF", "isometric / labelled\n"
        "carrier-preserving", BLUE, LIGHT_BLUE, 10)
    box(ax, .37, .59, .26, .24, r"$\mathsf{SOF}_{\mathrm{def}}$", "typed charts\n"
        "paths + endpoints\nschema transitions", ORANGE, LIGHT_ORANGE, 10)
    box(ax, .70, .59, .24, .24, "typed diagnostic", "trajectory / wall / rate\n"
        "for one carrier", TEAL, LIGHT_TEAL, 10)
    arrow(ax, (.29, .70), (.36, .70), BLUE, dashed=True, label="weakens")
    arrow(ax, (.64, .70), (.69, .70), TEAL, label="evaluates")
    ax.text(.5, .45, "Research Program", ha="center", fontsize=10, color=RED)
    box(ax, .16, .20, .20, .12, "weak morphism theory", "open", PURPLE, LIGHT_PURPLE, 9.5)
    box(ax, .39, .20, .20, .12, "wall crossing law", "open", PURPLE, LIGHT_PURPLE, 9.5)
    box(ax, .62, .20, .20, .12, "proxy-shadow bridge", "open", PURPLE, LIGHT_PURPLE, 9.5)
    ax.text(.5, .08, "This is a record interface, not a completed deformation category.",
            ha="center", fontsize=11, color=MUTED, style="italic")
    save_figure(fig, FIGURE_DIR, "fig6_sof_def_category")


def main():
    figure_1()
    figure_2()
    figure_3()
    figure_5()
    figure_6()
    print(f"Paper IX figures written to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
