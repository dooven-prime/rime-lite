"""Render Paper VII figures from current exact and numerical result records."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INCIDENCE = ROOT / "experiments" / "paper7" / "results" / "incidence_geometry.json"
AUDIT = ROOT / "experiments" / "paper7" / "results" / "projected_composition_audit.json"
STRUCTURED = ROOT / "experiments" / "paper7" / "results" / "structured_incidence_geometry_v2_1.json"
FIXED_PROFILE = ROOT / "experiments" / "paper7" / "results" / "fixed_frame_incidence_profiles_v2_1.json"
EXPECTED = {
    "experiments/paper7/results/incidence_geometry.json": "b139746bfc75f00084b2750328500db0429fed12f58c732f932cb08c0db0da99",
    "experiments/paper7/results/projected_composition_audit.json": "ba329db6659ff35d190a8b5ee9e4d0bf98e34d44f2e38e827eb733a98431fa0c",
    "experiments/paper7/results/structured_incidence_geometry_v2_1.json": "42d8a0cedcb2721a581eec16eebfc4d56df3108361fe65259f06059a1ae45fd2",
    "experiments/paper7/results/fixed_frame_incidence_profiles_v2_1.json": "5740a4bf33f83ba7ce20582918320edb450ffa086819b02aec15d8d972fe6e3d",
}

sys.path.insert(0, str(HERE.parent))
from style import save_figure  # noqa: E402


def _load() -> tuple[dict, dict, dict, dict]:
    for path, expected in EXPECTED.items():
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if digest != expected:
            raise RuntimeError(f"stale result: {path}")
    incidence = json.loads(INCIDENCE.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    structured = json.loads(STRUCTURED.read_text(encoding="utf-8"))
    fixed_profile = json.loads(FIXED_PROFILE.read_text(encoding="utf-8"))
    if incidence["formulas"]["fixed_double_rank_relative_codimension"] != "rs":
        raise RuntimeError("unexpected incidence formula")
    if structured["formulas"]["fixed_double_rank_relative_codimension"] != "sum_b r_b s_b":
        raise RuntimeError("unexpected structured incidence formula")
    if fixed_profile["fixed_frame_census"]["observed_rate"] != "2/9":
        raise RuntimeError("unexpected fixed-frame profile rate")
    return incidence, audit, structured, fixed_profile


def codimension_growth(incidence: dict) -> None:
    squares = {
        int(row["n"]): row
        for row in incidence["configurations"]
        if row["label"].startswith("square_d_")
    }
    dimensions = sorted(squares)
    ambient = np.array([squares[d]["ambient_dimension"] for d in dimensions])
    codim = np.array([squares[d]["type_iv_codimension"] for d in dimensions])
    asymptotic = 0.75 * np.square(dimensions)
    x = np.arange(len(dimensions))

    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    width = 0.34
    ax.bar(x - width / 2, ambient, width=width, color="#d9d9d9", edgecolor="#888888", label=r"ambient $2d^2$")
    ax.bar(x + width / 2, codim, width=width, color="#2b6f91", label="minimum fixed-rank codimension")
    ax.plot(x, asymptotic, color="#b33b2e", linestyle="--", linewidth=2.0, marker="o", label=r"$3d^2/4$")
    for xi, value, total in zip(x, codim, ambient):
        ax.text(xi + width / 2, value + 1.2, f"{100 * value / total:.1f}%", ha="center", color="#555555", fontsize=9)
    ax.set_xticks(x, [str(d) for d in dimensions])
    ax.set_xlabel(r"square intermediate dimension $d$")
    ax.set_ylabel("complex dimension / codimension")
    ax.set_title("Ambient fixed-rank incidence codimension", fontsize=17, fontweight="bold", pad=12)
    ax.text(
        0.5,
        1.00,
        r"$\operatorname{codim}I_r=(d-r)^2+dr$ is minimized near $r=d/2$",
        transform=ax.transAxes,
        ha="center",
        color="#666666",
        fontsize=10,
    )
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, HERE, "fig1_incidence_codimension")


def rubik_incidence_census(audit: dict) -> None:
    rubik = next(row for row in audit["systems"] if row["name"] == "rubik")
    registration = rubik["operator_registration"]
    counts = Counter((row["i"], row["k"], row["j"]) for row in rubik["zero_witnesses"])
    expected = {(2, 6, 8): 144, (5, 6, 8): 144, (8, 6, 2): 144, (8, 6, 5): 144}
    if dict(counts) != expected:
        raise RuntimeError(f"unexpected Rubik zero-witness census: {counts}")

    fig, (left, right) = plt.subplots(1, 2, figsize=(12.0, 5.8), gridspec_kw={"width_ratios": [0.78, 1.35]})
    left.bar(
        ["nonzero\nquarter turns", "zero\nhalf turns"],
        [registration["nonzero_operator_count"], registration["zero_operator_count"]],
        color=["#2b7a78", "#b9c0c5"],
        width=0.62,
    )
    left.set_ylim(0, 14)
    left.set_ylabel("registered operators")
    left.set_title(r"$X_g=(\rho(g)-\rho(g)^*)/2$", fontsize=14, fontweight="bold", pad=28)
    left.text(0, 12.35, "12", ha="center", fontweight="bold")
    left.text(1, 6.35, "6", ha="center", fontweight="bold")
    left.text(0.5, 1.01, "18 declared generators", transform=left.transAxes, ha="center", color="#666666", fontsize=10)
    left.spines[["top", "right"]].set_visible(False)
    left.grid(axis="y", color="#eeeeee", linewidth=0.8)

    triples = list(expected)
    labels = [f"({i},{k},{j})" for i, k, j in triples]
    values = [counts[triple] for triple in triples]
    bars = right.bar(labels, values, color="#b33b2e", width=0.62)
    for bar, value in zip(bars, values):
        right.text(bar.get_x() + bar.get_width() / 2, value + 4, str(value), ha="center", fontweight="bold")
    right.set_ylim(0, 165)
    right.set_ylabel("ordered nonzero-factor records with zero product")
    right.set_xlabel(r"sector triple $(i,k,j)$")
    right.set_title("Four registered image--kernel concentrations", fontsize=14, fontweight="bold", pad=28)
    right.text(
        0.5,
        1.01,
        r"$144=12^2$ per triple; total $576/2592$ audited products",
        transform=right.transAxes,
        ha="center",
        color="#b33b2e",
        fontsize=10,
    )
    right.spines[["top", "right"]].set_visible(False)
    right.grid(axis="y", color="#eeeeee", linewidth=0.8)

    fig.suptitle("Declared Rubik routed-product incidence census", fontsize=17, fontweight="bold")
    fig.text(
        0.5,
        0.015,
        "This is a finite numerical registration; it does not identify a represented pullback codimension.",
        ha="center",
        color="#555555",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    save_figure(fig, HERE, "fig2_rubik_incidence_census")


def structured_incidence_layers(structured: dict, fixed_profile: dict) -> None:
    diagonal = structured["diagonal_ambient"]["rows"]
    d4 = next(row for row in diagonal if row["d"] == 4)
    census = fixed_profile["fixed_frame_census"]

    fig, ax = plt.subplots(figsize=(12.2, 5.4))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    panel_x = (0.35, 4.35, 8.35)
    colors = ("#2b6f91", "#2b7a78", "#b35c2e")
    titles = ("Free matrix-pair ambient", "Common-carrier ambient", "Represented pullback")
    subtitles = (
        r"$Z=\{(A,B):AB=0\}$",
        r"$Z_{\mathcal{B}}=\prod_\beta Z_\beta$",
        r"$\Phi^{-1}(Z_{\mathcal{B}})\subseteq\Theta$",
    )

    for x, color, title, subtitle in zip(panel_x, colors, titles, subtitles):
        ax.add_patch(Rectangle((x, 1.15), 3.15, 3.45, fill=False, linewidth=2.0, edgecolor=color))
        ax.text(x + 1.575, 4.22, title, ha="center", va="center", fontsize=13, fontweight="bold", color=color)
        ax.text(x + 1.575, 3.78, subtitle, ha="center", va="center", fontsize=12, color="#333333")

    # Free dense pair.
    for row in range(4):
        for col in range(4):
            ax.add_patch(Rectangle((0.78 + col * 0.28, 2.05 + row * 0.28), 0.22, 0.22, color="#a9c9d8"))
            ax.add_patch(Rectangle((2.03 + col * 0.28, 2.05 + row * 0.28), 0.22, 0.22, color="#d8e7ee"))
    ax.text(1.89, 1.62, r"relative codim $rs$", ha="center", fontsize=11, color="#444444")

    # Structured diagonal blocks.
    block_specs = ((4.70, 2.12, 0.62), (5.50, 2.12, 0.48), (6.14, 2.12, 0.36))
    for index, (x, y, size) in enumerate(block_specs):
        ax.add_patch(Rectangle((x, y), size, size, facecolor="#b8dbd8", edgecolor="#2b7a78", linewidth=1.2))
        ax.text(x + size / 2, y + size / 2, rf"$\beta_{index + 1}$", ha="center", va="center", fontsize=10)
    ax.text(5.92, 1.72, r"relative codim $\sum_\beta r_\beta s_\beta$", ha="center", fontsize=11, color="#444444")
    ax.text(5.92, 1.38, f"diagonal $d=4$: codim {d4['zero_product_locus_codimension']}", ha="center", fontsize=9.5, color="#666666")

    # Represented family inside a declared parameter space.
    theta = np.linspace(0, 1, 100)
    curve_x = 8.92 + 2.05 * theta
    curve_y = 2.15 + 0.50 * np.sin(np.pi * theta)
    ax.plot(curve_x, curve_y, color="#b35c2e", linewidth=3.0)
    ax.plot([8.92, 10.97], [2.15, 2.15], color="#e2b299", linewidth=9.0, alpha=0.55)
    ax.text(9.94, 3.17, "pullback codimension can be 0", ha="center", fontsize=11, color="#444444")
    ax.text(
        9.94,
        1.66,
        f"fixed frame: {census['orbit_rows_with_supported_routes']}/19 active; 2/9 observed",
        ha="center",
        fontsize=9.5,
        color="#666666",
    )

    for left, right in ((3.56, 4.23), (7.56, 8.23)):
        ax.add_patch(
            FancyArrowPatch(
                (left, 2.88),
                (right, 2.88),
                arrowstyle="-|>",
                mutation_scale=16,
                linewidth=1.5,
                color="#777777",
            )
        )

    ax.text(
        6.1,
        0.55,
        "Codimension is ambient-relative; equal aggregate profiles do not identify the labelled family.",
        ha="center",
        fontsize=11,
        color="#444444",
    )
    fig.suptitle("Three levels of routed-incidence geometry", fontsize=17, fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(fig, HERE, "fig3_structured_incidence_layers")


def main() -> None:
    incidence, audit, structured, fixed_profile = _load()
    codimension_growth(incidence)
    rubik_incidence_census(audit)
    structured_incidence_layers(structured, fixed_profile)
    print(f"Rendered Paper VII figures from {INCIDENCE.relative_to(ROOT)} and {AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
