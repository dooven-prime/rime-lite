"""Render Paper V figures from source-addressed exact and finite records."""

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
DATA = ROOT / "experiments" / "paper5" / "results" / "figure_data.json"

sys.path.insert(0, str(HERE.parent))
from style import save_figure  # noqa: E402


def _load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale figure data: {source['path']}")
    census = data["s4_low_order_census"]
    if census["bracket_emergent_pairs"] + census["product_supported_r2_zero_pairs"] + census["unresolved_within_tested_order"] != census["r1_zero_pairs"]:
        raise RuntimeError("inconsistent S4 low-order partition")
    return data


def same_support_counterexample(data: dict) -> None:
    record = data["exact_counterexample"]
    x = np.array(record["x"])
    y0 = np.array(record["y_cancelling"])
    y1 = np.array(record["y_emergent"])

    fig = plt.figure(figsize=(12.0, 6.5))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.72], hspace=0.34, wspace=0.28)
    axes = [fig.add_subplot(grid[0, index]) for index in range(3)]
    matrices = [x, y0, y1]
    titles = [r"$X$", r"$Y_0=2X$", r"$Y_1$"]
    for ax, matrix, title in zip(axes, matrices, titles):
        ax.imshow(matrix != 0, cmap=matplotlib.colors.ListedColormap(["#f2f2f2", "#2b6f91"]), vmin=0, vmax=1)
        for row in range(3):
            for col in range(3):
                ax.text(col, row, str(matrix[row, col]), ha="center", va="center", color="white" if matrix[row, col] else "#777777", fontweight="bold")
        ax.set_xticks(range(3), ["1", "2", "3"])
        ax.set_yticks(range(3), ["1", "2", "3"])
        ax.set_title(title, fontsize=15, fontweight="bold")
        ax.tick_params(length=0)

    ax0 = fig.add_subplot(grid[1, 0:1])
    ax1 = fig.add_subplot(grid[1, 1:3])
    for ax in (ax0, ax1):
        ax.axis("off")

    ax0.text(
        0.5,
        0.62,
        "Generator-indexed direct support\nis identical in both systems",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.55", "facecolor": "#eef5f8", "edgecolor": "#2b6f91"},
    )
    ax1.text(0.20, 0.70, r"$Y_0$:  $2-2=0$", ha="center", fontsize=17, color="#666666", fontweight="bold")
    ax1.text(0.20, 0.32, r"$Q_1[X,Y_0]Q_3=0$", ha="center", fontsize=13, color="#666666")
    ax1.annotate("", xy=(0.52, 0.50), xytext=(0.40, 0.50), arrowprops={"arrowstyle": "->", "linewidth": 2, "color": "#888888"})
    ax1.text(0.78, 0.70, r"$Y_1$:  $3-2=1$", ha="center", fontsize=17, color="#b33b2e", fontweight="bold")
    ax1.text(0.78, 0.32, r"$Q_1[X,Y_1]Q_3\ne0$", ha="center", fontsize=13, color="#b33b2e")

    fig.suptitle("Exact same-support commutator counterexample", fontsize=17, fontweight="bold")
    fig.text(
        0.5,
        0.015,
        "Boolean direct support does not determine signed commutator survival or exact channel depth.",
        ha="center",
        color="#555555",
        fontsize=11,
    )
    save_figure(fig, HERE, "fig1_same_support_counterexample")


def low_order_partition(data: dict) -> None:
    census = data["s4_low_order_census"]
    labels = [
        r"$R_2^{\mathrm{Lie}}=1$",
        r"$C_2^X=W_2^X=1,\ R_2^{\mathrm{Lie}}=0$",
        "unresolved at tested order",
    ]
    values = [
        census["bracket_emergent_pairs"],
        census["product_supported_r2_zero_pairs"],
        census["unresolved_within_tested_order"],
    ]
    colors = ["#2b7a78", "#d39b17", "#b9c0c5"]

    fig, (top, ax) = plt.subplots(2, 1, figsize=(10.8, 6.6), gridspec_kw={"height_ratios": [0.55, 1.0]})
    top.axis("off")
    objects = [
        ("direct support", r"$R_1$"),
        ("routed products", r"$C_2^X$"),
        ("full words", r"$W_2^X$"),
        ("commutators", r"$R_2^{\mathrm{Lie}}$"),
        ("cutoff depth", r"$D_{\mathrm{Lie}}^{(\leq L)}$"),
    ]
    xs = np.linspace(0.08, 0.92, len(objects))
    for index, (name, symbol) in enumerate(objects):
        top.text(
            xs[index],
            0.52,
            f"{symbol}\n{name}",
            ha="center",
            va="center",
            fontsize=11,
            bbox={"boxstyle": "round,pad=0.42", "facecolor": "#f7f7f7", "edgecolor": "#7d8b93"},
        )
        if index < len(objects) - 1:
            top.annotate("", xy=(xs[index + 1] - 0.09, 0.52), xytext=(xs[index] + 0.09, 0.52), arrowprops={"arrowstyle": "->", "color": "#999999"})
    top.text(0.5, 0.08, "audit order only; no arrow denotes functional determination", ha="center", color="#666666", fontsize=11)

    y = np.arange(len(labels))
    ax.barh(y, values, color=colors, edgecolor="white", height=0.62)
    for yi, value in zip(y, values):
        ax.text(value + 1.0, yi, str(value), va="center", fontweight="bold")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 82)
    ax.set_xlabel("ordered sector pairs among the 80 aggregate-R1-zero targets")
    ax.set_title("Finite S4 low-order channel separation", fontsize=15, fontweight="bold", pad=10)
    ax.grid(axis="x", color="#eeeeee", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.text(
        0.5,
        0.012,
        r"Threshold $10^{-8}$; this finite census is not a low-order-to-depth completion theorem.",
        ha="center",
        color="#555555",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save_figure(fig, HERE, "fig2_low_order_channel_separation")


def main() -> None:
    data = _load()
    same_support_counterexample(data)
    low_order_partition(data)
    print(f"Rendered two Paper V figures from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
