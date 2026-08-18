"""Render the current claim-aware CCS figure set from source-addressed data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PAPER1_DATA = ROOT / "experiments" / "paper1" / "results" / "figure_data.json"
PAPER2_DATA = ROOT / "experiments" / "paper2" / "results" / "direct_transport.json"

sys.path.insert(0, str(HERE.parent))
from style import PAPER_BLOCK_COLORS as BLOCK_COLORS, save_figure  # noqa: E402


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        source_path = ROOT / source["path"]
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale figure data: {source['path']}")
    return data


def _validate(paper1: dict, paper2: dict) -> None:
    layers = paper1["canonical_layers"]
    if sum(row["dimension"] for row in layers) != 228:
        raise RuntimeError("Paper I figure data does not sum to dimension 228")
    totals = {
        block: sum(row["blocks"][block] for row in layers)
        for block in BLOCK_COLORS
    }
    if totals != {"cp": 64, "ep": 144, "co": 8, "eo": 12}:
        raise RuntimeError(f"Paper I block totals are inconsistent: {totals}")

    degrees = [0] * paper2["sector_count"]
    for edge in paper2["edges"]:
        degrees[edge["source"] - 1] += 1
        degrees[edge["target"] - 1] += 1
    if degrees != paper2["degree_sequence"]:
        raise RuntimeError(f"Paper II degree sequence is inconsistent: {degrees}")
    if paper2["threshold"] != 0.05 or len(paper2["edges"]) != 10:
        raise RuntimeError("Paper II display data does not use the registered census")


def spectral_census(data: dict) -> None:
    layers = sorted(data["canonical_layers"], key=lambda row: row["lambda"])
    x = np.array([row["lambda"] for row in layers])
    bottom = np.zeros(len(layers))

    fig, ax = plt.subplots(figsize=(12, 6.2))
    for block in ("cp", "ep", "co", "eo"):
        values = np.array([row["blocks"][block] for row in layers])
        ax.bar(
            x,
            values,
            width=0.055,
            bottom=bottom,
            color=BLOCK_COLORS[block],
            edgecolor="white",
            linewidth=0.7,
            label=block.upper(),
        )
        bottom += values

    for xi, row in zip(x, layers):
        ax.text(
            xi,
            row["dimension"] + 3,
            str(row["dimension"]),
            ha="center",
            fontweight="bold",
        )
        ax.text(xi, -8, f"k={row['k']}", ha="center", color="#555555", fontsize=9)

    ax.axvline(4 / 9, color="#999999", linestyle="--", linewidth=1.2)
    ax.text(
        4 / 9,
        120,
        "registered k=5 vacancy",
        ha="center",
        color="#777777",
        fontsize=9,
    )
    ax.annotate(
        "all four carrier blocks contribute",
        xy=(5 / 9, 106),
        xytext=(0.70, 112),
        arrowprops={"arrowstyle": "->", "color": "#777777"},
        color="#555555",
        ha="center",
    )
    ax.set_xticks(
        [1 / 3, 4 / 9, 5 / 9, 2 / 3, 7 / 9, 8 / 9, 1],
        ["1/3", "4/9", "5/9", "2/3", "7/9", "8/9", "1"],
    )
    ax.set_xlim(0.28, 1.04)
    ax.set_ylim(-13, 132)
    ax.set_xlabel("registered eigenvalue label")
    ax.set_ylabel("multiplicity")
    ax.set_title(
        "Canonical blockwise spectral census",
        fontsize=17,
        fontweight="bold",
        y=1.08,
    )
    ax.text(
        0.5,
        1.02,
        "six numerical clusters registered against the displayed values",
        transform=ax.transAxes,
        ha="center",
        color="#666666",
        fontsize=10,
    )
    ax.legend(frameon=False, ncol=4, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eeeeee", linewidth=0.7)
    save_figure(fig, HERE, "fig_c1_canonical_spectrum")


def phase_identity() -> None:
    roots = np.exp(2j * np.pi * np.arange(3) / 3)
    labels = ["1", r"$\omega$", r"$\omega^2$"]
    colors = ["#2b83ba", "#d39b17", "#b77a00"]

    fig, ax = plt.subplots(figsize=(8.4, 6.5))
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color="#d4d4d4", linewidth=1.2)
    ax.axhline(0, color="#e6e6e6", linewidth=0.8)
    ax.axvline(0, color="#e6e6e6", linewidth=0.8)
    polygon = np.r_[roots, roots[:1]]
    ax.plot(polygon.real, polygon.imag, color="#79add1", linewidth=2.6)
    for root, label, color in zip(roots, labels, colors):
        ax.scatter(
            root.real,
            root.imag,
            s=520,
            color=color,
            edgecolor="white",
            linewidth=2,
            zorder=3,
        )
        dx = 0.18 if root.real > 0 else -0.20
        dy = 0.17 if root.imag >= 0 else -0.19
        ax.text(
            root.real + dx,
            root.imag + dy,
            label,
            color=color,
            fontsize=18,
            fontweight="bold",
        )

    ax.text(0, 0.08, r"$1+\omega+\omega^2=0$", ha="center", fontsize=22, fontweight="bold")
    ax.text(
        0,
        -1.26,
        "Local exact identity for complete-face phase sums\n"
        "It is not a certificate for the full averaging spectrum.",
        ha="center",
        color="#555555",
        fontsize=10,
        linespacing=1.4,
    )
    ax.set_title("Complete-face phase cancellation", fontsize=17, fontweight="bold")
    ax.set_aspect("equal")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.42, 1.28)
    ax.axis("off")
    save_figure(fig, HERE, "fig_c10_phase_cancellation")


def arithmetic_contrast(data: dict) -> None:
    groups = data["broken_face_control"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4), sharey=True)

    for ax, key, title in zip(
        axes,
        ("canonical", "eight_generator"),
        ("18-generator canonical family", "8-generator broken-face control"),
    ):
        for row in groups[key]:
            candidate = row.get("recognition") == "Q(sqrt(5)) candidate"
            color = "#b33b2e" if candidate else "#2b6f91"
            ax.hlines(row["lambda"], 0, row["dimension"], color="#c9c9c9")
            ax.scatter(
                row["dimension"],
                row["lambda"],
                s=70 + 2.2 * row["dimension"],
                color="white" if candidate else color,
                edgecolor=color,
                linewidth=2 if candidate else 1,
                zorder=3,
            )
            ax.text(
                row["dimension"] + 4,
                row["lambda"],
                row["label"],
                va="center",
                fontsize=9,
                color=color,
            )
        ax.set_xlim(0, 126)
        ax.set_xlabel("registered multiplicity")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.grid(axis="y", color="#eeeeee", linewidth=0.7)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("registered eigenvalue")
    axes[1].text(
        0.57,
        0.07,
        "red rings: numerical recognition\nagainst Q(sqrt(5)) candidates",
        transform=axes[1].transAxes,
        color="#b33b2e",
        fontsize=9,
        ha="center",
    )
    fig.suptitle("Registered generator-family arithmetic contrast", fontsize=17, fontweight="bold")
    fig.text(
        0.5,
        0.015,
        "Two finite computations; not an exact field-classification theorem.",
        ha="center",
        color="#555555",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    save_figure(fig, HERE, "fig_c20_arithmetic_contrast")


def _transport_matrix(data: dict) -> np.ndarray:
    matrix = np.zeros((data["sector_count"], data["sector_count"]))
    np.fill_diagonal(matrix, data["diagonal"])
    for edge in data["edges"]:
        i, j = edge["source"] - 1, edge["target"] - 1
        matrix[i, j] = matrix[j, i] = edge["weight"]
    return matrix


def transport_heatmap(data: dict) -> None:
    display = _transport_matrix(data)
    np.fill_diagonal(display, np.nan)
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("#f2f2f2")

    fig, ax = plt.subplots(figsize=(8.8, 7.6))
    im = ax.imshow(
        display,
        cmap=cmap,
        vmin=0,
        vmax=max(edge["weight"] for edge in data["edges"]),
    )
    labels = [f"S{i}" for i in range(1, data["sector_count"] + 1)]
    ax.set_xticks(range(9), labels)
    ax.set_yticks(range(9), labels)
    ax.xaxis.tick_top()
    for edge in data["edges"]:
        i, j = edge["source"] - 1, edge["target"] - 1
        text_color = "white" if edge["weight"] >= 2 else "#203746"
        for row, col in ((i, j), (j, i)):
            ax.text(
                col,
                row,
                f"{edge['weight']:.2f}",
                ha="center",
                va="center",
                color=text_color,
                fontweight="bold",
            )
            if edge["label"] == "Type II":
                ax.add_patch(
                    plt.Rectangle(
                        (col - 0.48, row - 0.48),
                        0.96,
                        0.96,
                        fill=False,
                        edgecolor="#7b3294",
                        linewidth=2,
                    )
                )
    for i in range(9):
        ax.text(i, i, "self", ha="center", va="center", color="#999999", fontsize=8)

    ax.set_title("Registered direct transport matrix", fontsize=17, fontweight="bold", pad=42)
    ax.set_xlabel("source sector")
    ax.set_ylabel("target sector")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label(r"$K^S_{ij}$")
    fig.text(
        0.5,
        0.025,
        "Aggregate support at tau_K=0.05; diagonal self-blocks are omitted from the color scale.",
        ha="center",
        color="#555555",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, HERE, "fig_c2_transport_heatmap")


def direct_support_graph(data: dict) -> None:
    positions = {
        1: (-1.85, 1.35),
        2: (-1.35, 0.25),
        3: (-0.85, -0.90),
        4: (0.20, -1.15),
        5: (-0.45, 0.90),
        6: (0.20, 0.10),
        7: (1.05, -0.35),
        8: (1.85, 0.95),
        9: (1.45, 0.25),
    }
    degrees = data["degree_sequence"]
    fig, ax = plt.subplots(figsize=(10.2, 6.3))

    for edge in data["edges"]:
        x1, y1 = positions[edge["source"]]
        x2, y2 = positions[edge["target"]]
        type_two = edge["label"] == "Type II"
        ax.plot(
            [x1, x2],
            [y1, y2],
            color="#7b3294" if type_two else "#46788c",
            linestyle="--" if type_two else "-",
            linewidth=1.3 + 0.45 * edge["weight"],
            alpha=0.9,
            zorder=1,
        )

    for sector, (x, y) in positions.items():
        degree = degrees[sector - 1]
        if sector == 6:
            color, size = "#c44e3b", 780
        elif degree == 0:
            color, size = "#6f7f86", 420
        else:
            color, size = "#f4a340", 390 + 45 * degree
        ax.scatter(x, y, s=size, color=color, edgecolor="white", linewidth=2, zorder=3)
        ax.text(x, y, f"S{sector}", ha="center", va="center", color="white", fontweight="bold")
        ax.text(x, y - 0.22, f"deg {degree}", ha="center", va="top", color="#555555", fontsize=8)

    ax.annotate(
        "isolated registered sector",
        xy=positions[1],
        xytext=(-1.15, 1.66),
        arrowprops={"arrowstyle": "->", "color": "#888888"},
        color="#666666",
    )
    ax.annotate(
        "unique degree-five hub",
        xy=positions[6],
        xytext=(0.48, 1.47),
        arrowprops={"arrowstyle": "->", "color": "#888888"},
        color="#666666",
    )
    ax.legend(
        handles=[
            Line2D([0], [0], color="#46788c", linewidth=2, label="nine Type I labelled edges"),
            Line2D(
                [0],
                [0],
                color="#7b3294",
                linewidth=2,
                linestyle="--",
                label="S8--S9 Type II labelled edge",
            ),
        ],
        loc="lower left",
        frameon=False,
    )
    ax.set_title("Ten-edge aggregate direct-support graph", fontsize=17, fontweight="bold")
    ax.text(
        0.5,
        0.985,
        "labels are assigned after block certification",
        transform=ax.transAxes,
        ha="center",
        color="#666666",
        fontsize=9,
    )
    ax.set_xlim(-2.2, 2.25)
    ax.set_ylim(-1.55, 1.8)
    ax.set_aspect("equal")
    ax.axis("off")
    save_figure(fig, HERE, "fig_c19_direct_support_graph")


def main() -> None:
    paper1 = _load(PAPER1_DATA)
    paper2 = _load(PAPER2_DATA)
    _validate(paper1, paper2)
    spectral_census(paper1)
    phase_identity()
    arithmetic_contrast(paper1)
    transport_heatmap(paper2)
    direct_support_graph(paper2)
    print("Rendered five current CCS figures from Paper I and Paper II result records")


if __name__ == "__main__":
    main()
