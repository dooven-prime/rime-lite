"""Render Paper XVI figures from the frozen reader-facing result surface."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


HERE = Path(__file__).resolve().parent


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(HERE / f"{stem}.png", dpi=240, bbox_inches="tight")
    fig.savefig(HERE / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def descent_stack() -> None:
    labels = [
        ("Quotient support", "Adjacent sector blocks are nonzero."),
        ("Routed composition", "The full projected product is nonzero."),
        ("Signed operator", "Weights and transmitter-proxy signs are fixed."),
        ("Microscopic dynamics", "The registered update F_Y is fixed."),
        ("Observation", "A declared coarse map O is applied."),
        ("Dynamic closure", "Observed successors are constant on each fiber."),
    ]
    colors = ["#dceaf7", "#d8eee5", "#f5e7c8", "#eadff1", "#f2dedb", "#e2e5e9"]
    fig, ax = plt.subplots(figsize=(9.4, 7.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.2)
    ax.axis("off")
    ax.text(
        5,
        9.75,
        "Each arrow requires an explicit descent certificate; no arrow is automatic.",
        ha="center",
        va="center",
        fontsize=11,
        color="#263238",
        weight="bold",
    )
    for idx, ((title, subtitle), color) in enumerate(zip(labels, colors)):
        y = 8.55 - idx * 1.38
        box = FancyBboxPatch(
            (0.65, y),
            8.7,
            0.92,
            boxstyle="round,pad=0.035,rounding_size=0.05",
            facecolor=color,
            edgecolor="#24313a",
            linewidth=1.0,
        )
        ax.add_patch(box)
        ax.text(
            1.08,
            y + 0.46,
            str(idx + 1),
            ha="center",
            va="center",
            fontsize=10.5,
            weight="bold",
            color="#24313a",
        )
        ax.text(
            1.55,
            y + 0.46,
            title,
            ha="left",
            va="center",
            fontsize=11.2,
            weight="bold",
        )
        ax.text(
            4.55,
            y + 0.46,
            subtitle,
            ha="left",
            va="center",
            fontsize=9.5,
            color="#33434d",
        )
        if idx < len(labels) - 1:
            ax.annotate(
                "",
                xy=(5, y - 0.42),
                xytext=(5, y - 0.05),
                arrowprops={"arrowstyle": "->", "lw": 1.15, "color": "#37474f"},
            )
    save(fig, "fig1_descent_stack")


def registered_contrasts() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.1))
    fig.subplots_adjust(wspace=0.34, hspace=0.45)

    ax = axes[0, 0]
    labels = ["relay-strict\naddition", "coverage-inclusive\naddition"]
    vals = [781 / 782, 374 / 812]
    bars = ax.bar(labels, vals, color=["#287271", "#d98c4a"], width=0.62)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("conditional liftability")
    ax.set_title("A. Nested support additions")
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{100*value:.2f}%", ha="center", fontsize=9)

    ax = axes[0, 1]
    gammas = [0.9, 1.0, 1.1]
    sign = [0.84668, 0.87846, 0.90458]
    coverage = [0.00416, 0.00598, 0.00770]
    ax.plot(gammas, sign, marker="o", linewidth=2, color="#7b2d26", label="matched-support sign")
    ax.plot(gammas, coverage, marker="s", linewidth=2, color="#457b9d", label="coverage reference")
    ax.set_ylim(0, 1.0)
    ax.set_xlabel(r"$\gamma$")
    ax.set_ylabel("cosine distance")
    ax.set_title("B. Registered dynamic contrast")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    strata = ["small", "medium", "large"]
    rms = [8.7141, 7.0140, 8.7840]
    q95 = [2.0207, 1.5190, 2.2083]
    local = [24.0335, 3.8780, 36.4267]
    x = range(len(strata))
    width = 0.23
    ax.bar([v - width for v in x], rms, width=width, label="RMS / mean", color="#4c78a8")
    ax.bar(list(x), q95, width=width, label="q95 / mean", color="#72b7b2")
    ax.bar([v + width for v in x], local, width=width, label="local / mean", color="#f58518")
    ax.set_xticks(list(x), strata)
    ax.set_ylabel("visibility ratio")
    ax.set_title("C. Observation resolution")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    labels = ["LP2", "LP3", "first-order\nclosure"]
    values = [1.0, 1.0, 0.0]
    colors = ["#2a9d8f", "#2a9d8f", "#c14953"]
    bars = ax.bar(labels, values, color=colors, width=0.58)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 1], ["failed", "complete"])
    ax.set_title("D. Same-carrier somaSide audit")
    ax.text(bars[0].get_x() + bars[0].get_width() / 2, 1.035, "64/64", ha="center", fontsize=9)
    ax.text(bars[1].get_x() + bars[1].get_width() / 2, 1.035, "256/256", ha="center", fontsize=9)
    ax.text(bars[2].get_x() + bars[2].get_width() / 2, 0.04, "fiber witness", ha="center", fontsize=8, color="white", rotation=90)

    for ax in axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color="#d8dde1", linewidth=0.6, alpha=0.75)
        ax.set_axisbelow(True)

    fig.suptitle("Frozen MaleCNS representation-loss contrasts", fontsize=14, weight="bold", y=1.01)
    save(fig, "fig2_registered_contrasts")


if __name__ == "__main__":
    descent_stack()
    registered_contrasts()
