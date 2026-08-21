"""Render Paper II direct-support figures from the frozen registered census."""

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
DATA = ROOT / "experiments" / "paper2" / "results" / "direct_transport.json"
OUT = HERE

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from schemas.release_snapshot import resolve_release_reference  # noqa: E402
from style import save_figure  # noqa: E402


def _load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        reference = {
            "uri": source["path"],
            "digest": {"algorithm": "sha256", "value": source["sha256"]},
        }
        resolved = resolve_release_reference(reference, repository_root=ROOT)
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale figure data: {source['path']}")
    degrees = [0] * data["sector_count"]
    for edge in data["edges"]:
        degrees[edge["source"] - 1] += 1
        degrees[edge["target"] - 1] += 1
    if degrees != data["degree_sequence"]:
        raise RuntimeError(f"figure data has inconsistent degrees: {degrees}")
    return data


def _matrix(data: dict) -> np.ndarray:
    matrix = np.zeros((data["sector_count"], data["sector_count"]))
    np.fill_diagonal(matrix, data["diagonal"])
    for edge in data["edges"]:
        i, j = edge["source"] - 1, edge["target"] - 1
        matrix[i, j] = matrix[j, i] = edge["weight"]
    return matrix


def heatmap(data: dict) -> None:
    matrix = _matrix(data)
    display = matrix.copy()
    np.fill_diagonal(display, np.nan)
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("#f2f2f2")

    fig, ax = plt.subplots(figsize=(8.8, 7.6))
    im = ax.imshow(display, cmap=cmap, vmin=0, vmax=max(edge["weight"] for edge in data["edges"]))
    labels = [f"S{i}" for i in range(1, data["sector_count"] + 1)]
    ax.set_xticks(range(9), labels)
    ax.set_yticks(range(9), labels)
    ax.xaxis.tick_top()
    for edge in data["edges"]:
        i, j = edge["source"] - 1, edge["target"] - 1
        color = "#7b3294" if edge["label"] == "Type II" else "#203746"
        for row, col in ((i, j), (j, i)):
            ax.text(col, row, f"{edge['weight']:.2f}", ha="center", va="center", color=color, fontweight="bold")
            if edge["label"] == "Type II":
                ax.add_patch(plt.Rectangle((col - 0.48, row - 0.48), 0.96, 0.96, fill=False, edgecolor=color, linewidth=2.0))
    for i in range(9):
        ax.text(i, i, "self", ha="center", va="center", color="#999999", fontsize=8)

    ax.set_title("Registered direct transport matrix", fontsize=17, fontweight="bold", pad=42)
    ax.set_xlabel("source sector")
    ax.set_ylabel("target sector")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(r"$K^S_{ij}$")
    fig.text(
        0.5,
        0.025,
        "Off-diagonal aggregate support at tau_K=0.05; diagonal self-blocks are omitted from the color scale.",
        ha="center",
        color="#555555",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, OUT, "fig1_k_heatmap")


def main() -> None:
    data = _load()
    heatmap(data)
    print(f"Rendered the Paper II heatmap from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
