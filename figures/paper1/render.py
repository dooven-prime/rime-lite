"""Render the three claim-status-aware Paper I figures from frozen display data."""

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
DATA = ROOT / "experiments" / "paper1" / "results" / "figure_data.json"
OUT = HERE

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from schemas.release_snapshot import resolve_release_reference  # noqa: E402
from style import PAPER_BLOCK_COLORS as BLOCK_COLORS, save_figure  # noqa: E402


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
    layers = data["canonical_layers"]
    if any(sum(row["blocks"].values()) != row["dimension"] for row in layers):
        raise RuntimeError("figure data has an inconsistent layer dimension")
    block_totals = {block: sum(row["blocks"][block] for row in layers) for block in BLOCK_COLORS}
    if block_totals != {"cp": 64, "ep": 144, "co": 8, "eo": 12}:
        raise RuntimeError(f"figure data has inconsistent block totals: {block_totals}")
    return data


def spectral_census(data: dict) -> None:
    layers = sorted(data["canonical_layers"], key=lambda row: row["lambda"])
    x = np.array([row["lambda"] for row in layers])
    width = 0.055

    fig, ax = plt.subplots(figsize=(12, 6.2))
    bottom = np.zeros(len(layers))
    for block in ("cp", "ep", "co", "eo"):
        values = np.array([row["blocks"][block] for row in layers])
        ax.bar(
            x,
            values,
            width=width,
            bottom=bottom,
            color=BLOCK_COLORS[block],
            edgecolor="white",
            linewidth=0.7,
            label=block.upper(),
        )
        bottom += values

    for xi, row in zip(x, layers):
        ax.text(xi, row["dimension"] + 3, str(row["dimension"]), ha="center", fontweight="bold")
        ax.text(xi, -8, f"k={row['k']}", ha="center", color="#555555", fontsize=9)

    missing = 4 / 9
    ax.axvline(missing, color="#999999", linestyle="--", linewidth=1.2)
    ax.text(missing, 120, "registered k=5 vacancy", ha="center", color="#777777", fontsize=9)
    ax.annotate(
        "all four blocks contribute",
        xy=(5 / 9, 106),
        xytext=(0.70, 112),
        arrowprops={"arrowstyle": "->", "color": "#777777"},
        color="#555555",
        ha="center",
    )

    ticks = [1 / 3, 4 / 9, 5 / 9, 2 / 3, 7 / 9, 8 / 9, 1]
    labels = ["1/3", "4/9", "5/9", "2/3", "7/9", "8/9", "1"]
    ax.set_xticks(ticks, labels)
    ax.set_xlim(0.28, 1.04)
    ax.set_ylim(-13, 132)
    ax.set_xlabel("registered eigenvalue label")
    ax.set_ylabel("multiplicity")
    ax.set_title("Canonical blockwise spectral census", fontsize=17, fontweight="bold", pad=12)
    ax.text(
        0.5,
        1.01,
        "six numerical clusters registered against the displayed values",
        transform=ax.transAxes,
        ha="center",
        color="#666666",
        fontsize=10,
    )
    ax.legend(frameon=False, ncol=4, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eeeeee", linewidth=0.7)
    save_figure(fig, OUT, "fig1_spectral_collapse")


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
        ax.scatter(root.real, root.imag, s=520, color=color, edgecolor="white", linewidth=2, zorder=3)
        dx = 0.18 if root.real > 0 else -0.20
        dy = 0.17 if root.imag >= 0 else -0.19
        ax.text(root.real + dx, root.imag + dy, label, color=color, fontsize=18, fontweight="bold")

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
    ax.set_title("Complete-face phase cancellation", fontsize=17, fontweight="bold", pad=12)
    ax.set_aspect("equal")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.42, 1.28)
    ax.axis("off")
    save_figure(fig, OUT, "fig3_phase_cancellation")


def broken_face_contrast(data: dict) -> None:
    groups = data["broken_face_control"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4), sharey=True)

    for ax, key, title in zip(
        axes,
        ("canonical", "eight_generator"),
        ("18-generator canonical family", "8-generator broken-face control"),
    ):
        rows = groups[key]
        for row in rows:
            candidate = row.get("recognition") == "Q(sqrt(5)) candidate"
            color = "#b33b2e" if candidate else "#2b6f91"
            ax.hlines(row["lambda"], 0, row["dimension"], color="#c9c9c9", linewidth=1.0)
            ax.scatter(
                row["dimension"],
                row["lambda"],
                s=70 + 2.2 * row["dimension"],
                color="white" if candidate else color,
                edgecolor=color,
                linewidth=2 if candidate else 1,
                zorder=3,
            )
            ax.text(row["dimension"] + 4, row["lambda"], row["label"], va="center", fontsize=9, color=color)

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
        "The contrast records two finite computations; it is not an exact field-classification theorem.",
        ha="center",
        color="#555555",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    save_figure(fig, OUT, "fig4_symmetry_breaking")


def main() -> None:
    data = _load()
    spectral_census(data)
    phase_identity()
    broken_face_contrast(data)
    print(f"Rendered three Paper I figures from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
