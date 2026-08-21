"""Render the Paper XV epistemic-revision boundary figure."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
from matplotlib.patches import FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import (
    BLUE,
    BLUE_DARK,
    GRAY_2,
    GRAY_4,
    ORANGE,
    arrow,
    box,
    clean,
    save,
    setup,
    title,
)


FIGURE_DIR = Path(__file__).resolve().parent
TEAL = "#168c8c"
TEAL_DARK = "#116b6b"
BLUE_FILL = "#eef5fa"
TEAL_FILL = "#edf8f7"
ORANGE_FILL = "#fff6e8"


def render_revision_boundary() -> None:
    fig, ax = setup((14.5, 7.2))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Acyclic Epistemic Revision",
        "Object change remains external; currentness requires validation and activation",
    )

    ax.text(0.04, 0.82, "External object path", fontsize=11, fontweight="bold", color=ORANGE)
    box(ax, 0.04, 0.61, 0.14, 0.14, "Object state", r"$X_t$", edge=ORANGE, fill=ORANGE_FILL)
    box(ax, 0.27, 0.61, 0.20, 0.14, "External transition", "dynamics or intervention", edge=ORANGE, fill=ORANGE_FILL)
    box(ax, 0.56, 0.61, 0.14, 0.14, "Object state", r"$X_{t+1}$", edge=ORANGE, fill=ORANGE_FILL)
    box(ax, 0.79, 0.61, 0.17, 0.14, "Observation", "candidate evidence", edge=BLUE, fill=BLUE_FILL)
    arrow(ax, 0.185, 0.68, 0.27, 0.68, color=ORANGE)
    arrow(ax, 0.475, 0.68, 0.56, 0.68, color=ORANGE)
    arrow(ax, 0.71, 0.68, 0.79, 0.68, color=BLUE)

    ax.plot([0.04, 0.96], [0.53, 0.53], color=GRAY_4, linewidth=1.0)
    ax.text(0.04, 0.47, "Owned epistemic path", fontsize=11, fontweight="bold", color=TEAL_DARK)
    box(ax, 0.04, 0.22, 0.20, 0.17, "Admitted input", r"$E_t,\ \widehat e,\ \Pi_{\rm rev}$", edge=BLUE_DARK, fill=BLUE_FILL)
    box(ax, 0.31, 0.22, 0.20, 0.17, "Revision proposal", r"$\widetilde E_{t+1},\rho,\Sigma,V$", edge=TEAL, fill=TEAL_FILL)
    box(ax, 0.59, 0.22, 0.15, 0.17, "Conformance", r"receipt $r_{\rm conf}$", edge=TEAL_DARK, fill=TEAL_FILL)
    box(ax, 0.82, 0.22, 0.14, 0.17, "Current state", r"$E_{t+1}$", edge=TEAL_DARK, fill=TEAL_FILL)
    arrow(ax, 0.245, 0.305, 0.31, 0.305, color=BLUE_DARK)
    arrow(ax, 0.515, 0.305, 0.59, 0.305, color=TEAL)
    arrow(ax, 0.745, 0.305, 0.82, 0.305, color=TEAL_DARK)

    ax.plot(
        [0.875, 0.875, 0.14],
        [0.61, 0.445, 0.445],
        color=GRAY_2,
        linewidth=1.4,
        linestyle="--",
    )
    evidence_arrow = FancyArrowPatch(
        (0.14, 0.445),
        (0.14, 0.39),
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.4,
        linestyle="--",
        color=GRAY_2,
    )
    ax.add_patch(evidence_arrow)
    ax.text(0.78, 0.13, r"activation also requires $b_{\rm act}$", ha="center", fontsize=10.5, color=TEAL_DARK)
    ax.text(0.50, 0.065, "No revision artifact authorizes the external object transition.", ha="center", fontsize=12, fontweight="bold", color=ORANGE)

    save(fig, str(FIGURE_DIR), "fig1_revision_boundary")


if __name__ == "__main__":
    render_revision_boundary()
