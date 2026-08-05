"""Render the typed Paper X pipeline and Registry figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "figures" / "paper10"
sys.path.insert(0, str(ROOT))

from figures.style import save_figure


BLUE = "#24567a"
TEAL = "#17725f"
ORANGE = "#c36f1f"
PURPLE = "#6e4b9e"
RED = "#b6423a"
INK = "#27333d"
MUTED = "#65727b"
GRID = "#cbd4d8"
LIGHT_BLUE = "#f3f8fc"
LIGHT_TEAL = "#f1faf6"
LIGHT_ORANGE = "#fff7ed"
LIGHT_PURPLE = "#f8f4fc"
LIGHT_RED = "#fff4f2"


def clean(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def box(ax, x, y, w, h, title, body="", *, edge=BLUE, face=LIGHT_BLUE,
        title_size=9.5, body_size=9.0):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1.5, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h - 0.030, title,
        ha="center", va="top", fontsize=title_size,
        fontweight="bold", color=edge,
    )
    if body:
        ax.text(
            x + w / 2, y + h / 2 - 0.012, body,
            ha="center", va="center", fontsize=body_size,
            color=INK, linespacing=1.28,
        )


def arrow(ax, start, end, *, color=MUTED, dashed=False, label=None, dy=0.025):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops={
            "arrowstyle": "-|>", "lw": 1.35, "color": color,
            "linestyle": "--" if dashed else "-",
            "shrinkA": 2, "shrinkB": 2,
        },
    )
    if label:
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + dy,
            label, ha="center", va="center", fontsize=8, color=MUTED,
        )


def heading(ax, title, subtitle):
    ax.text(.03, .95, title, fontsize=18, fontweight="bold", color=INK)
    ax.text(.03, .91, subtitle, fontsize=10.5, color=MUTED)


def figure_1():
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    clean(ax)
    heading(
        ax,
        "Capability-Sound Compiler v1 Emission",
        "Profiles select validated IR claims; they do not create evidence or cross carriers.",
    )
    stages = [
        (.035, "source + admission", "adapter output\nstrict or analogue", BLUE, LIGHT_BLUE),
        (.235, "Capability Manifest", "declared carriers\n+ conventions", ORANGE, LIGHT_ORANGE),
        (.435, "Typed SOF IR", "findings + claims\nevidence + derivations", PURPLE, LIGHT_PURPLE),
        (.635, "Report Profile", "module gates\nforbidden promotions", TEAL, LIGHT_TEAL),
        (.835, "compiler output", "claim items +\ndegradation items", BLUE, LIGHT_BLUE),
    ]
    for x, title, body, edge, face in stages:
        box(ax, x, .56, .15, .22, title, body, edge=edge, face=face,
            title_size=9.0, body_size=8.5)
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, (left[0] + .15, .67), (right[0], .67), color=MUTED)

    box(
        ax, .13, .22, .31, .16, "operator / route / word branch",
        r"$R_1[Y]$  |  $\mathrm{Route}_d[Y]$  |  $W_d[Y]$"
        "\n" r"$D_{\mathrm{route}}[Y]$  |  $D_{\mathrm{word}}[Y]$",
        edge=TEAL, face=LIGHT_TEAL, body_size=9.5,
    )
    box(
        ax, .56, .22, .31, .16, "independent Lie / Hall branch",
        r"$R_1^{\mathrm{Lie}}$  |  $R_2^{\mathrm{Lie}}$  |  $D_{\mathrm{Lie}}$"
        "\nadditional computation at each stage",
        edge=PURPLE, face=LIGHT_PURPLE, body_size=9.5,
    )
    arrow(ax, (.51, .55), (.30, .39), color=TEAL, dashed=True, label="typed carrier", dy=.012)
    arrow(ax, (.51, .55), (.72, .39), color=PURPLE, dashed=True, label="independent carrier", dy=.012)
    ax.text(
        .5, .09,
        "NOT_DECLARED, unresolved derivations, and forbidden promotions emit no affirmative claim.",
        ha="center", fontsize=11, color=RED, style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig1_capability_compilation")


def figure_2():
    fig, ax = plt.subplots(figsize=(13.5, 7.6))
    clean(ax)
    heading(
        ax,
        "Open SOF Registry",
        "Different sources enter a common evidence architecture without sharing a deformation law.",
    )
    box(
        ax, .37, .40, .26, .20, "Registry v2.0 entry",
        "admission + capabilities\ntyped findings\nevidence + boundaries",
        edge=TEAL, face=LIGHT_TEAL, title_size=11, body_size=9.5,
    )
    entries = [
        (.05, .66, "representation", "Rubik strict\nXu analogue", BLUE, LIGHT_BLUE),
        (.38, .70, "geometry", "spectral triple\nPDE", ORANGE, LIGHT_ORANGE),
        (.72, .66, "state / graph", "Markov / graph\nquantum gates", PURPLE, LIGHT_PURPLE),
        (.05, .18, "control / constraint", "Kalman\ncoloring", TEAL, LIGHT_TEAL),
        (.38, .10, "stochastic barrier", "barrier option", ORANGE, LIGHT_ORANGE),
        (.72, .18, "activation / filtration", "neural network\nYang-like", BLUE, LIGHT_BLUE),
    ]
    for x, y, title, body, edge, face in entries:
        box(ax, x, y, .23, .14, title, body, edge=edge, face=face,
            title_size=8.7, body_size=9.0)
        start = (x + .118, y + (.14 if y < .4 else 0))
        end = (.5, .4 if y < .4 else .6)
        arrow(ax, start, end, color=edge, dashed=True)
    ax.text(
        .5, .035,
        "15 strict realizations + 4 diagnostic analogues; no common dynamics asserted.",
        ha="center", fontsize=11, color=RED, style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig2_registry_wheel")


def figure_3():
    fig, ax = plt.subplots(figsize=(13.5, 7.6))
    clean(ax)
    heading(
        ax,
        "Capability-Aware Registry v2.0 Entry",
        "Admission and capabilities determine which findings may be registered.",
    )
    stages = [
        (.045, "1  Source", "domain data\n+ provenance", BLUE, LIGHT_BLUE),
        (.275, "2  Admission", "strict $(V,Q,Y)$\nor analogue map", ORANGE, LIGHT_ORANGE),
        (.505, "3  Capabilities", "carriers + semantics\npolicies + dynamics", PURPLE, LIGHT_PURPLE),
        (.735, "4  Findings", "values + claims\ncertificates + artifacts", TEAL, LIGHT_TEAL),
    ]
    for x, title, body, edge, face in stages:
        box(ax, x, .52, .19, .22, title, body, edge=edge, face=face,
            title_size=8.9, body_size=8.5)
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, (left[0] + .19, .63), (right[0], .63))

    box(
        ax, .13, .16, .74, .20, "result state + reader-facing claim status",
        "missing / unreached / observed / certified / established"
        "\nTheorem  |  Certificate  |  Observation  |  Research Program",
        edge=RED, face=LIGHT_RED, title_size=11, body_size=9.5,
    )
    arrow(ax, (.83, .51), (.65, .36), color=RED, dashed=True, label="separate axes", dy=.016)
    ax.text(
        .5, .08,
        "Manifest does not contain results. Findings do not create capabilities.",
        ha="center", fontsize=11, color=MUTED, style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig3_registry_layers")


def figure_4():
    fig, ax = plt.subplots(figsize=(13.5, 7.6))
    clean(ax)
    heading(
        ax,
        "Rate-Separation Evidence Has Different Claim Status",
        "Shared qualitative ordering does not identify carriers, mechanisms, or numerical scales.",
    )
    columns = [
        (.05, "Xu ridge analogue", r"$\theta_{\parallel}$ / $\theta_{\perp}$"
         "\nlocal contraction conversion\n"
         r"$749.6\times$", BLUE, LIGHT_BLUE, "Computational Observation"),
        (.365, "exact 3-sector path", r"$K_{\mathrm{dir}}(t)=t$"
         "\n" r"$K_{\mathrm{comm}}(t)=t^2$"
         "\n" r"$\tau_\eta:\ \eta<\sqrt{\eta}$", TEAL, LIGHT_TEAL, "Theorem"),
        (.68, "NN diagnostic analogue", r"$K_0<K_1<K_2$"
         "\ncontinuous proxies only\n$60<80<120$", PURPLE, LIGHT_PURPLE,
         "Computational Observation"),
    ]
    for x, title, body, edge, face, status in columns:
        box(ax, x, .42, .27, .32, title, body, edge=edge, face=face,
            title_size=11, body_size=9.6)
        ax.text(
            x + .135, .33, status, ha="center", va="center", fontsize=9.6,
            color=edge, fontweight="bold",
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white",
                  "edgecolor": edge, "linewidth": 1},
        )
    ax.text(
        .5, .18,
        r"No Registry v2.0 entry observes a full "
        r"$\tau(R_1^{\mathrm{Lie}})<\tau(R_2^{\mathrm{Lie}})"
        r"<\tau(D_{\mathrm{Lie}}^{(\leq d_{\max})})$ trajectory.",
        ha="center", fontsize=11, color=RED,
    )
    ax.text(
        .5, .09,
        "The full hierarchy remains a Research Program.",
        ha="center", fontsize=11, color=MUTED, style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig4_rate_hierarchy_evidence")


def figure_5():
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.set_title(
        "Calibrated Two-Channel Response Witness",
        loc="left", fontsize=17, fontweight="bold", color=INK, pad=18,
    )
    t = list(range(0, 1801, 30))
    gamma = 0.69314718056 / 30.0
    lam = 0.69314718056 / 1380.0
    grow = [1.0 - pow(2.718281828, -gamma * value) for value in t]
    slow_response = [1.0 - pow(2.718281828, -lam * value) for value in t]
    ax.plot(t, grow, color=TEAL, lw=2.2, label=r"fast growth $K_a(t)$")
    ax.plot(
        t, slow_response, color=ORANGE, lw=2.2,
        label=r"slow decay displacement $\widehat K_b(t)$",
    )
    ax.axhline(.5, color=GRID, ls="--", lw=1)
    ax.axvline(30, color=TEAL, ls=":", lw=1.4)
    ax.axvline(1380, color=ORANGE, ls=":", lw=1.4)
    ax.text(30, .10, r"$\tau_{1/2}=30$", ha="left", color=TEAL, fontsize=10)
    ax.text(1380, .56, r"$\tau_{1/2}=1380$", ha="center", color=ORANGE, fontsize=10)
    ax.set_xlabel("deformation time")
    ax.set_ylabel("normalized proxy response")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=.22)
    ax.legend(frameon=False, loc="lower right") #center right
    ax.text(
        .02, -.21,
        "One normalized-displacement policy; theorem for ordering, certificate for block realization.",
        transform=ax.transAxes, color=RED, fontsize=11, style="italic",
    )
    fig.tight_layout()
    save_figure(fig, FIGURE_DIR, "fig5_mechanism_separation")


def figure_6():
    fig, ax = plt.subplots(figsize=(13.5, 7.6))
    clean(ax)
    heading(
        ax,
        "Capability-Gated Compiler Output",
        "The typed compiler emits only modules supported by each admitted source.",
    )
    origins = [
        (.04, "representation", "joint spectrum"),
        (.235, "geometry", "Dirac / mesh blocks"),
        (.43, "state", "barrier / Markov"),
        (.625, "graph / control", "partition / flags"),
        (.82, "activation", "analogue descriptor"),
    ]
    for x, title, body in origins:
        box(ax, x, .68, .15, .13, title, body, edge=BLUE, face=LIGHT_BLUE,
            title_size=9.0, body_size=8.5)
        arrow(ax, (x + .075, .67), (.5, .565), color=BLUE, dashed=True)
    box(
        ax, .34, .42, .32, .14, "adapter + admission",
        "strict $(V,Q,Y)$  |  diagnostic analogue",
        edge=ORANGE, face=LIGHT_ORANGE, title_size=10.5, body_size=9.5,
    )
    box(
        ax, .10, .17, .34, .14, "enabled static modules",
        "operator / route / word / closure\nLie / Hall only when declared",
        edge=TEAL, face=LIGHT_TEAL, title_size=9.5, body_size=9.0,
    )
    box(
        ax, .56, .17, .34, .14, "enabled dynamic modules",
        "trajectory / wall / response\nonly with comparison + policies",
        edge=PURPLE, face=LIGHT_PURPLE, title_size=9.5, body_size=9.0,
    )
    arrow(ax, (.43, .41), (.28, .32), color=TEAL, label="static audit", dy=.012)
    arrow(ax, (.57, .41), (.72, .32), color=PURPLE, label="declared dynamics", dy=.012)
    ax.text(
        .5, .07,
        "Unavailable modules are omitted; no nearby carrier is substituted.",
        ha="center", fontsize=11, color=RED, style="italic",
    )
    save_figure(fig, FIGURE_DIR, "fig6_source_independent_observable_report")


def main():
    figure_1()
    figure_2()
    figure_3()
    figure_4()
    figure_5()
    figure_6()
    print(f"Paper X figures written to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
