"""Render Paper IV figures from the exact, source-addressed P_9 census."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
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
DATA = ROOT / "experiments" / "paper4" / "results" / "figure_data.json"

sys.path.insert(0, str(HERE.parent))
from style import save_figure  # noqa: E402


COLORS = {
    "S1": "#244f73",
    "S2": "#158f80",
    "S3": "#3a8ec1",
    "S4": "#2c9b63",
    "S5": "#c7473a",
    "S6": "#a83b32",
    "S7": "#e37b20",
    "S8": "#e79a16",
    "S9": "#c96516",
}


def _load() -> tuple[dict, list[dict]]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["provenance"]["sources"]:
        digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise RuntimeError(f"stale figure data: {source['path']}")
    points = [
        {
            **row,
            "qf": Fraction(row["q"]),
            "hf": Fraction(row["h"]),
        }
        for row in data["points"]
    ]
    if len(points) != 9 or sum(row["dimension"] for row in points) != 228:
        raise RuntimeError("unexpected P_9 census")
    return data, points


def _lambda(point: dict, alpha: Fraction | float) -> float:
    return float(alpha * point["qf"] + (1 - alpha) * point["hf"])


def _fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return rf"$\frac{{{value.numerator}}}{{{value.denominator}}}$"


def joint_points(points: list[dict]) -> None:
    alpha = Fraction(2, 3)
    groups: dict[Fraction, list[dict]] = defaultdict(list)
    for point in points:
        groups[alpha * point["qf"] + (1 - alpha) * point["hf"]].append(point)

    fig, ax = plt.subplots(figsize=(9.2, 6.5))
    for members in groups.values():
        if len(members) > 1:
            ordered = sorted(members, key=lambda row: float(row["qf"]))
            ax.plot(
                [float(row["qf"]) for row in ordered],
                [float(row["hf"]) for row in ordered],
                color="#aeb8bf",
                linestyle="--",
                linewidth=1.4,
                zorder=1,
            )

    offsets = {
        "S1": (-0.045, 0.028),
        "S2": (0.022, 0.028),
        "S3": (0.022, -0.040),
        "S4": (0.022, 0.028),
        "S5": (0.022, 0.028),
        "S6": (0.022, -0.040),
        "S7": (0.022, 0.028),
        "S8": (0.022, 0.028),
        "S9": (0.022, -0.040),
    }
    for point in points:
        x, y = float(point["qf"]), float(point["hf"])
        ax.scatter(
            x,
            y,
            s=95 + 10 * np.sqrt(point["dimension"]),
            color=COLORS[point["label"]],
            edgecolor="white",
            linewidth=1.4,
            zorder=3,
        )
        dx, dy = offsets[point["label"]]
        ax.text(x + dx, y + dy, point["label"], fontsize=11, fontweight="bold")

    ax.set_xticks(
        [0, 1 / 3, 1 / 2, 2 / 3, 5 / 6, 1],
        ["0", "1/3", "1/2", "2/3", "5/6", "1"],
    )
    ax.set_yticks([1 / 3, 2 / 3, 1], ["1/3", "2/3", "1"])
    ax.set_xlim(-0.06, 1.08)
    ax.set_ylim(0.26, 1.08)
    ax.set_xlabel(r"$q$ coordinate")
    ax.set_ylabel(r"$h$ coordinate")
    ax.set_title(r"Exact nine-point arrangement $P_9$", fontsize=17, fontweight="bold", pad=12)
    ax.text(
        0.5,
        1.01,
        r"Dashed chords join nontrivial $L_{2/3}$ quotient classes",
        transform=ax.transAxes,
        ha="center",
        color="#666666",
        fontsize=10,
    )
    ax.grid(color="#eeeeee", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, HERE, "fig1_joint_spectral_points")


def affine_branches(data: dict, points: list[dict]) -> None:
    criticals = [Fraction(value) for value in data["critical_parameters"]]
    collisions = {
        Fraction(alpha): edges for alpha, edges in data["interior_collisions"].items()
    }
    alphas = np.linspace(0, 1, 500)
    fig, ax = plt.subplots(figsize=(11.8, 6.4))

    for point in points:
        values = [float(a * point["qf"] + (1 - a) * point["hf"]) for a in alphas]
        ax.plot(alphas, values, color=COLORS[point["label"]], linewidth=2.0)

    for alpha in criticals:
        main = alpha == Fraction(2, 3)
        ax.axvline(
            float(alpha),
            color="#b33b2e" if main else "#b9b9b9",
            linewidth=2.2 if main else 1.0,
            linestyle="-" if main else "--",
        )
        ax.text(
            float(alpha),
            1.025,
            _fraction(alpha),
            ha="center",
            color="#b33b2e" if main else "#666666",
            fontweight="bold" if main else "normal",
            fontsize=10,
        )
        for left, _ in collisions[alpha]:
            point = next(row for row in points if row["label"] == left)
            ax.scatter(
                float(alpha),
                _lambda(point, alpha),
                s=62 if main else 34,
                color="#b33b2e" if main else "white",
                edgecolor="#b33b2e" if main else "#666666",
                linewidth=1.1,
                zorder=4,
            )

    ax.annotate(
        r"unique maximal interior drop: $9\to6$",
        xy=(2 / 3, 5 / 9),
        xytext=(0.72, 0.68),
        arrowprops={"arrowstyle": "->", "color": "#b33b2e"},
        color="#b33b2e",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xticks(
        [0, *map(float, criticals), 1],
        ["0", *[_fraction(value) for value in criticals], "1"],
    )
    ax.set_yticks(
        [0, 1 / 3, 5 / 9, 2 / 3, 7 / 9, 8 / 9, 1],
        ["0", "1/3", "5/9", "2/3", "7/9", "8/9", "1"],
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.03, 1.06)
    ax.set_xlabel(r"interpolation parameter $\alpha$")
    ax.set_ylabel(r"branch value $\lambda_i(\alpha)$")
    ax.set_title(r"Affine branch arrangement of $P_9$", fontsize=17, fontweight="bold", pad=12)
    ax.grid(color="#eeeeee", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, HERE, "fig2_affine_branch_arrangement")


def collision_graph(data: dict, points: list[dict]) -> None:
    positions = {
        "S1": (0.50, 0.88),
        "S2": (0.19, 0.72),
        "S3": (0.34, 0.53),
        "S4": (0.14, 0.30),
        "S5": (0.51, 0.35),
        "S6": (0.69, 0.51),
        "S7": (0.70, 0.24),
        "S8": (0.34, 0.09),
        "S9": (0.88, 0.10),
    }
    dims = {row["label"]: row["dimension"] for row in points}
    fig, ax = plt.subplots(figsize=(9.2, 7.0))
    ax.axis("off")

    for alpha_text, edges in data["interior_collisions"].items():
        main = alpha_text == "2/3"
        for left, right in edges:
            x1, y1 = positions[left]
            x2, y2 = positions[right]
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="#b33b2e" if main else "#aeb8bf",
                linewidth=3.0 if main else 1.2,
                linestyle="-" if main else "--",
                zorder=1,
            )
            if not main:
                ax.text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2 + 0.022,
                    alpha_text,
                    ha="center",
                    fontsize=8,
                    color="#666666",
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.5},
                )

    for label, (x, y) in positions.items():
        main = label in {"S5", "S6", "S7", "S8", "S9"}
        size = 700 + 18 * np.sqrt(dims[label])
        ax.scatter(
            x,
            y,
            s=size,
            color=COLORS[label] if main else "white",
            edgecolor=COLORS[label],
            linewidth=2.0,
            zorder=3,
        )
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            color="white" if main else "#222222",
            fontweight="bold",
            zorder=4,
        )

    ax.text(0.5, 0.98, r"Interior collision graph of $P_9$", ha="center", fontsize=17, fontweight="bold")
    ax.text(
        0.5,
        0.93,
        r"Red edges occur at $\alpha=2/3$; gray edges mark the other interior collisions",
        ha="center",
        color="#666666",
        fontsize=10,
    )
    ax.set_xlim(0.03, 0.97)
    ax.set_ylim(0.00, 1.02)
    save_figure(fig, HERE, "fig3_collision_graph")


def main() -> None:
    data, points = _load()
    joint_points(points)
    affine_branches(data, points)
    collision_graph(data, points)
    print(f"Rendered three Paper IV figures from {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
