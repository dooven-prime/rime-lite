"""Render Paper VI figures from the normality-gated v2.1 audit record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "experiments" / "paper6" / "results" / "figure_data.json"

sys.path.insert(0, str(HERE.parent))
from style import save_figure  # noqa: E402


def _load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale figure data: {source['path']}")
    maps = data["linearized_maps"]
    if [(row["rank"], row["nullity"]) for row in maps] != [(11, 7), (14, 4)]:
        raise RuntimeError("unexpected linearized rank census")
    records = data["admission_records"]
    if [row["status"] for row in records] != [
        "ADMITTED",
        "ADMITTED",
        "ADMITTED",
        "ADMITTED",
        "REJECTED",
    ]:
        raise RuntimeError("unexpected admission status census")
    return data


def linearized_gates(data: dict) -> None:
    maps = data["linearized_maps"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.0, 6.0), gridspec_kw={"width_ratios": [0.85, 1.35]})

    labels = ["commutativity", "commutativity\n+ normality"]
    ranks = [row["rank"] for row in maps]
    nullities = [row["nullity"] for row in maps]
    x = np.arange(2)
    left.bar(x, ranks, color="#2b6f91", label="rank")
    left.bar(x, nullities, bottom=ranks, color="#d6dde1", label="nullity")
    for index, (rank, nullity) in enumerate(zip(ranks, nullities)):
        left.text(index, rank / 2, str(rank), ha="center", va="center", color="white", fontsize=14, fontweight="bold")
        left.text(index, rank + nullity / 2, str(nullity), ha="center", va="center", color="#444444", fontsize=13, fontweight="bold")
    left.set_xticks(x, labels)
    left.set_ylim(0, 20)
    left.set_ylabel("weight-space dimension")
    left.set_title("Rank / nullity", fontsize=14, fontweight="bold")
    left.legend(frameon=False, ncol=2, loc="upper center")
    left.spines[["top", "right"]].set_visible(False)

    for index, row in enumerate(maps):
        singular = np.array(row["singular_values"])
        positions = np.arange(1, len(singular) + 1)
        retained = singular > 1e-10
        color = "#2b6f91" if index == 0 else "#2b7a78"
        right.scatter(positions[retained], singular[retained], s=43, color=color, label=labels[index].replace("\n", " "))
        right.scatter(positions[~retained], np.full(np.sum(~retained), 1e-15), s=32, facecolor="white", edgecolor=color)
    right.axhline(1e-10, color="#999999", linestyle="--", linewidth=1.0, label="rank threshold scale")
    right.set_yscale("log")
    right.set_ylim(3e-16, 1.2)
    right.set_xlabel("ordered singular-value index")
    right.set_ylabel("singular value")
    right.set_title("Full complex-real Jacobian spectra", fontsize=14, fontweight="bold")
    right.grid(axis="y", which="both", color="#eeeeee", linewidth=0.7)
    right.spines[["top", "right"]].set_visible(False)
    right.legend(frameon=False, fontsize=8, loc="lower left")

    fig.suptitle("Linearized commutativity and normality gates", fontsize=17, fontweight="bold")
    fig.text(
        0.5,
        0.015,
        "The rank certificates are pointwise and linearized; they do not prove nonlinear integrability or a moving spectral chart.",
        ha="center",
        color="#555555",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    save_figure(fig, HERE, "fig1_linearized_normality_gate")


def pointwise_registrations(data: dict) -> None:
    rows = data["admission_records"]
    short_labels = ["canonical", "axis 0", "axis 1", "axis 2", "single QT"]
    x_all = np.arange(len(rows))
    admitted = [row for row in rows if row["status"] == "ADMITTED"]
    x_admitted = np.arange(len(admitted))

    fig, (gate, sectors_ax, support_ax) = plt.subplots(
        1,
        3,
        figsize=(14.2, 5.8),
        gridspec_kw={"width_ratios": [1.15, 0.8, 1.15]},
    )

    gate_residuals = [max(row["pair_residuals"].values()) for row in rows]
    colors = ["#2b7a78" if row["status"] == "ADMITTED" else "#b33b2e" for row in rows]
    gate.scatter(x_all, gate_residuals, s=68, color=colors, zorder=3)
    gate.axhline(
        data["numerical_policy"]["admission_tolerance"],
        color="#777777",
        linestyle="--",
        linewidth=1.1,
        label=r"admission tolerance $10^{-8}$",
    )
    gate.set_yscale("log")
    gate.set_ylim(1e-18, 1)
    gate.set_xticks(x_all, short_labels, rotation=20, ha="right")
    gate.set_ylabel("maximum pre-projector residual")
    gate.set_title("Fail-closed admission gate", fontsize=13, fontweight="bold")
    gate.grid(axis="y", which="both", color="#eeeeee", linewidth=0.7)
    gate.spines[["top", "right"]].set_visible(False)
    gate.legend(frameon=False, fontsize=8, loc="upper left")

    sectors = [row["sector_count"] for row in admitted]
    bars = sectors_ax.bar(
        x_admitted,
        sectors,
        color=["#2b6f91", "#2b7a78", "#2b7a78", "#2b7a78"],
        width=0.64,
    )
    for bar, value in zip(bars, sectors):
        sectors_ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.35,
            str(value),
            ha="center",
            fontweight="bold",
        )
    sectors_ax.set_xticks(x_admitted, short_labels[:4], rotation=20, ha="right")
    sectors_ax.set_ylim(0, 17)
    sectors_ax.set_ylabel("registered sectors")
    sectors_ax.set_title("Post-admission sectors", fontsize=13, fontweight="bold")
    sectors_ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
    sectors_ax.spines[["top", "right"]].set_visible(False)

    width = 0.34
    op = [row["r1_op"] for row in admitted]
    lie = [row["r1_lie"] for row in admitted]
    support_ax.bar(
        x_admitted - width / 2,
        op,
        width=width,
        color="#d39b17",
        label=r"$R_1^{\mathrm{op}}$",
    )
    support_ax.bar(
        x_admitted + width / 2,
        lie,
        width=width,
        color="#b33b2e",
        label=r"$R_1^{\mathrm{Lie}}$",
    )
    support_ax.set_xticks(x_admitted, short_labels[:4], rotation=20, ha="right")
    support_ax.set_ylabel("directed support blocks")
    support_ax.set_title("Post-admission typed support", fontsize=13, fontweight="bold")
    support_ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
    support_ax.spines[["top", "right"]].set_visible(False)
    support_ax.legend(frameon=False)

    fig.suptitle(
        r"Normality-gated registrations at $\varepsilon=0.1$",
        fontsize=17,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.015,
        "The single-QT control is rejected before projector construction; only admitted samples receive sector and typed-support fields.",
        ha="center",
        color="#555555",
        fontsize=10.5,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    save_figure(fig, HERE, "fig2_pointwise_typed_registrations")


def main() -> None:
    data = _load()
    linearized_gates(data)
    pointwise_registrations(data)
    print(f"Rendered two Paper VI figures from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
