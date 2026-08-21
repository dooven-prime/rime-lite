"""Render the Paper III obstruction figure from the source-addressed observation."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "experiments" / "paper3" / "results" / "composition_obstruction.observation.json"
OUT = HERE

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from schemas.release_snapshot import resolve_release_reference  # noqa: E402
from style import save_figure  # noqa: E402


def _declared_source_path(source: dict[str, str]) -> Path:
    reference = {
        "uri": source["path"],
        "digest": {"algorithm": "sha256", "value": source["sha256"]},
    }
    return resolve_release_reference(reference, repository_root=ROOT)


def composition_obstruction(data: dict) -> None:
    witnesses = data["observations"]["graph_only_obstruction_witnesses"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.5, 5.8), gridspec_kw={"width_ratios": [1.0, 1.35]})

    left.axis("off")
    box = {"boxstyle": "round,pad=0.45", "facecolor": "#f4f6f7", "edgecolor": "#657b83", "linewidth": 1.4}
    left.text(0.13, 0.62, r"$E_j$", fontsize=18, ha="center", va="center", bbox=box)
    left.text(0.50, 0.62, r"$E_k$", fontsize=18, ha="center", va="center", bbox=box)
    left.text(0.87, 0.62, r"$E_i$", fontsize=18, ha="center", va="center", bbox=box)
    left.annotate("", xy=(0.41, 0.62), xytext=(0.22, 0.62), arrowprops={"arrowstyle": "->", "linewidth": 2.2, "color": "#2b7a78"})
    left.annotate("", xy=(0.78, 0.62), xytext=(0.59, 0.62), arrowprops={"arrowstyle": "->", "linewidth": 2.2, "color": "#b2473e"})
    left.text(0.315, 0.68, r"$B\ne0$", ha="center", color="#2b7a78", fontsize=13)
    left.text(0.685, 0.68, r"$A\ne0$", ha="center", color="#b2473e", fontsize=13)
    left.text(0.50, 0.42, r"$\operatorname{im}B\subseteq\ker A$", ha="center", fontsize=17, fontweight="bold")
    left.text(0.50, 0.29, r"$AB=0$", ha="center", fontsize=21, color="#b2473e", fontweight="bold")
    left.text(0.50, 0.10, "Two nonzero support factors\nneed not compose.", ha="center", color="#555555", fontsize=11, linespacing=1.4)
    left.set_title("Exact local obstruction", fontsize=15, fontweight="bold")

    names = [f"S{w['endpoint_a']}--S{w['endpoint_b']}\nvia S{w['intermediate']}" for w in witnesses]
    x = np.arange(len(witnesses))
    left_norms = np.array([w["max_left_edge_norm"] for w in witnesses])
    right_norms = np.array([w["max_right_edge_norm"] for w in witnesses])
    products = np.array([w["max_ordered_product_norm"] for w in witnesses])
    right.scatter(x - 0.10, left_norms, marker="o", s=60, color="#2b7a78", label="left edge maximum")
    right.scatter(x + 0.10, right_norms, marker="s", s=55, color="#4c78a8", label="right edge maximum")
    right.scatter(x, products, marker="x", s=75, linewidth=2.0, color="#b2473e", label="maximum routed product")
    for index, value in enumerate(products):
        right.text(index, value * 1.8, f"{value:.1e}", ha="center", color="#b2473e", fontsize=8)
    right.axhline(1e-10, color="#888888", linestyle="--", linewidth=1.0, label="declared zero threshold")
    right.set_yscale("log")
    right.set_ylim(3e-17, 12)
    right.set_xticks(x, names, fontsize=8)
    right.set_ylabel("Frobenius norm")
    right.set_title("Five registered graph-only witnesses", fontsize=15, fontweight="bold")
    right.grid(axis="y", which="both", color="#eeeeee", linewidth=0.7)
    right.spines[["top", "right"]].set_visible(False)
    right.legend(frameon=False, loc="center right", fontsize=8)
    right.text(
        0.5,
        -0.23,
        "Factor columns are independently maximized; products are exhaustive over 18 x 18 ordered pairs.",
        transform=right.transAxes,
        ha="center",
        color="#555555",
        fontsize=8.5,
    )

    fig.suptitle("Support paths versus projected matrix composition", fontsize=17, fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    save_figure(fig, OUT, "fig1_composition_obstruction")


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        digest = hashlib.sha256(_declared_source_path(source).read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale observation: {source['path']}")
    if not data["observations"]["summary"]["passed"]:
        raise RuntimeError("observation did not pass")
    if len(data["observations"]["graph_only_obstruction_witnesses"]) != 5:
        raise RuntimeError("unexpected graph-only witness count")
    composition_obstruction(data)
    print(f"Rendered Paper III figure from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
