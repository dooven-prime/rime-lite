"""Render the Paper XXVI deterministic--stochastic separation figure."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import BLUE, BLUE_DARK, GRAY_2, ORANGE  # noqa: E402


HERE = Path(__file__).resolve().parent


def deterministic_stochastic_separation() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12.5,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "figure.dpi": 120,
            "savefig.dpi": 240,
        }
    )

    n = np.arange(3, 17, dtype=float)
    cerny_reset = (n - 1) ** 2
    cerny_absorption = n**3 - 1.5 * n**2 + (n.astype(int) % 2) / 2
    rare_reset = n - 1
    rare_absorption = 2**n - 2

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.5), sharex=True, sharey=True)
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "Deterministic and Random Synchronization Scales Separate",
        fontsize=16,
        fontweight="bold",
        color=BLUE_DARK,
        y=0.98,
    )
    fig.text(
        0.5,
        0.92,
        "Shortest-word control is min-plus; pair absorption averages the labelled transition carrier",
        ha="center",
        color=GRAY_2,
        fontsize=10,
    )

    panels = (
        (axes[0], cerny_reset, cerny_absorption, "Černý family", r"$rt=(n-1)^2$", r"$H_2=\Theta(n^3)$"),
        (axes[1], rare_reset, rare_absorption, "Advance/reset family", r"$rt=n-1$", r"$H_2=2^n-2$"),
    )
    for ax, reset, absorption, panel_title, reset_label, absorption_label in panels:
        ax.set_facecolor("#fbfcfd")
        ax.plot(
            n,
            reset,
            color=BLUE,
            linewidth=2.4,
            marker="o",
            markersize=4.2,
            label=f"deterministic  {reset_label}",
        )
        ax.plot(
            n,
            absorption,
            color=ORANGE,
            linewidth=2.4,
            marker="s",
            markersize=4.0,
            label=f"random pair  {absorption_label}",
        )
        ax.set_yscale("log")
        ax.set_xlim(3, 16)
        ax.set_ylim(1, 1.2e5)
        ax.set_xticks([3, 6, 9, 12, 15])
        ax.grid(True, which="major", color="#d9e1e7", linewidth=0.8)
        ax.grid(True, which="minor", axis="y", color="#eef1f3", linewidth=0.5)
        ax.set_title(panel_title, fontweight="bold", color=BLUE_DARK, pad=10)
        ax.set_xlabel("state count  n")
        ax.legend(loc="upper left", frameon=False, fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#9aa7b0")
        ax.spines["bottom"].set_color("#9aa7b0")

    axes[0].set_ylabel("time scale (logarithmic axis)")
    fig.text(
        0.5,
        0.025,
        "The family with the shorter reset threshold can have the larger random absorption time.",
        ha="center",
        color=BLUE_DARK,
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0.035, 0.07, 0.985, 0.95), w_pad=2.4)
    fig.savefig(HERE / "fig1_deterministic_stochastic_separation.png", bbox_inches="tight")
    fig.savefig(HERE / "fig1_deterministic_stochastic_separation.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    deterministic_stochastic_separation()
    print(f"Wrote Paper XXVI figure to {HERE}")
