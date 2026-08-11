"""Render current Paper XIV v2 presentation figures."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sof_figure_utils import (
    BLUE,
    BLUE_DARK,
    GRAY_1,
    GRAY_2,
    GRAY_4,
    ORANGE,
    arrow,
    box,
    clean,
    save,
    setup,
    title,
)


FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parent.parent
RESULTS = ROOT / "experiments" / "paper14" / "results"
OUT = str(FIGURE_DIR)
TEAL = "#168c8c"
TEAL_DARK = "#116b6b"
BLUE_FILL = "#eef5fa"
TEAL_FILL = "#edf8f7"
ORANGE_FILL = "#fff6e8"


def fig1_factorization() -> None:
    fig, ax = setup((14.5, 7.2))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(ax, "SOFActionObject Factorization", "Context and policy precede bounded candidate actions")
    box(ax, 0.04, 0.45, 0.18, 0.18, "Audit Projection", r"$\Delta_{\rm audit}$", edge=BLUE, fill=BLUE_FILL)
    box(ax, 0.31, 0.68, 0.18, 0.18, "Action Context", "$K_{\\rm ctx}$\n(admitted input)", edge=BLUE_DARK)
    box(ax, 0.31, 0.22, 0.18, 0.18, "Policy Profile", "$\\Pi_{\\rm policy}$\n(admitted input)", edge=BLUE_DARK)
    box(ax, 0.58, 0.42, 0.18, 0.24, "Interpretation", "$I_{\\rm interp}$\nthree-input", edge=TEAL, fill=TEAL_FILL)
    box(ax, 0.82, 0.45, 0.15, 0.18, "Candidate Set", r"$A_{\rm cand}$", edge=TEAL_DARK, fill=TEAL_FILL)
    arrow(ax, 0.225, 0.54, 0.58, 0.54, color=BLUE)
    arrow(ax, 0.50, 0.77, 0.58, 0.60, color=BLUE_DARK)
    arrow(ax, 0.50, 0.31, 0.58, 0.48, color=BLUE_DARK)
    arrow(ax, 0.765, 0.54, 0.82, 0.54, color=TEAL)
    ax.text(0.895, 0.22, "selection / authorization\nremain downstream", ha="center", va="center", fontsize=11, color=ORANGE)
    arrow(ax, 0.895, 0.45, 0.895, 0.30, color=ORANGE)
    ax.text(0.5, 0.08, "The audit projection is preserved; candidates are not commands.", ha="center", fontsize=12, fontweight="bold", color=TEAL_DARK)
    save(fig, OUT, "fig1_semantic_factorization")


def fig2_interpretation_relativity() -> None:
    fig, ax = setup((13.6, 7.2))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(ax, "Interpretation Relativity", "The same factual difference can have different policy-relative meanings")
    box(ax, 0.05, 0.42, 0.18, 0.18, "Same audit", r"$\Delta_{\rm audit}$", edge=BLUE, fill=BLUE_FILL)
    box(ax, 0.35, 0.62, 0.27, 0.17, "Failure context + review policy", "defect candidate", edge=BLUE_DARK, fill=BLUE_FILL)
    box(ax, 0.35, 0.20, 0.27, 0.17, "Licensed context + conforming policy", "licensed change", edge=TEAL, fill=TEAL_FILL)
    arrow(ax, 0.23, 0.51, 0.35, 0.70, color=BLUE)
    arrow(ax, 0.23, 0.51, 0.35, 0.29, color=TEAL)
    box(ax, 0.73, 0.62, 0.20, 0.17, "Candidate result", "Investigate /\nRequestEvidence", edge=BLUE_DARK)
    box(ax, 0.73, 0.20, 0.20, 0.17, "Candidate result", "NoAction /\nInvestigate", edge=TEAL, fill=TEAL_FILL)
    arrow(ax, 0.625, 0.705, 0.73, 0.705, color=BLUE)
    arrow(ax, 0.625, 0.285, 0.73, 0.285, color=TEAL)
    ax.text(0.5, 0.075, r"$I_{K_1,\Pi_1}(\Delta)\neq I_{K_2,\Pi_2}(\Delta)$", ha="center", fontsize=14, fontweight="bold", color=GRAY_1)
    save(fig, OUT, "fig2_context_nonidentifiability")


def fig4_channel_semantics() -> None:
    fig, ax = setup((14.5, 8.0))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(ax, "Typed Coordinates Preserve Distinct Action Semantics", "Candidate dispositions remain tied to the retained coordinate family")
    rows = [
        ("Direct support", "coordinate state", "Investigate", BLUE),
        ("Word bridge", "coordinate state", "RequestEvidence", TEAL),
        ("Lie bridge", "policy assessment", "Investigate", TEAL_DARK),
        ("Frozen depth", "uncertainty state", "Unresolved state", BLUE_DARK),
        ("Wall record", "source boundary", "RequestEvidence", ORANGE),
    ]
    for i, (channel, meaning, disposition, color) in enumerate(rows):
        y = 0.72 - 0.125 * i
        box(ax, 0.055, y, 0.20, 0.085, channel, edge=color, body_size=9)
        box(ax, 0.36, y, 0.24, 0.085, meaning, edge=color, fill=GRAY_4, body_size=9)
        box(ax, 0.71, y, 0.23, 0.085, disposition, edge=color, body_size=9)
        arrow(ax, 0.26, y + 0.042, 0.36, y + 0.042, color=color)
        arrow(ax, 0.605, y + 0.042, 0.71, y + 0.042, color=color)
    ax.text(0.5, 0.075, "A candidate never substitutes one SOF carrier for another.", ha="center", fontsize=12, fontweight="bold", color=TEAL_DARK)
    save(fig, OUT, "fig4_channel_semantics")


def fig5_workbench() -> None:
    summary = json.loads((RESULTS / "action_summary.json").read_text(encoding="utf-8"))
    for reference in summary["source_artifacts"]:
        path = ROOT / reference["uri"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != reference["digest"]["value"]:
            raise ValueError(f"action summary source digest mismatch: {path}")
    rows = summary["records"]
    domains = ["gridworld", "sir", "traffic", "compiler", "network", "before_after"]
    labels = ["GridWorld", "SIR", "Traffic", "Compiler", "Routing", "Before/After"]
    dispositions = ["Investigate", "RequestEvidence", "Mitigate", "Rollback"]
    counts = np.zeros((len(domains), len(dispositions)), dtype=int)
    for row in rows:
        prefix = next(domain for domain in domains if row["case"].startswith(domain))
        for disposition in row["dispositions"]:
            if disposition in dispositions:
                counts[domains.index(prefix), dispositions.index(disposition)] += 1
    fig, ax = plt.subplots(figsize=(13.6, 7.2))
    fig.patch.set_facecolor("white")
    x = np.arange(len(labels))
    width = 0.18
    colors = [BLUE, TEAL, ORANGE, BLUE_DARK]
    for i, disposition in enumerate(dispositions):
        ax.bar(x + (i - 1.5) * width, counts[:, i], width, label=disposition, color=colors[i])
    ax.set_xticks(x, labels)
    ax.set_ylabel("cases producing candidate disposition")
    ax.set_title("Paper XIV v2 Action Workbench", fontsize=18, fontweight="bold", pad=16)
    ax.text(0.5, 1.00, "28 migrated unresolved records plus one native factual audit; counts are not severity", transform=ax.transAxes, ha="center", fontsize=10, color=GRAY_2)
    ax.legend(frameon=False, ncol=4, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRAY_4, linewidth=0.7)
    save(fig, OUT, "fig5_controlled_workbench")


def fig6_boundary() -> None:
    fig, ax = setup((14.0, 7.2))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(ax, "Admission, Empty Sets, and the Policy Boundary", "Missing context or evidence does not create a default intervention")
    cases = [
        (0.05, "Missing context or policy", "inconclusive", "empty interpretations\nempty Candidate Set", ORANGE),
        (0.365, "Migrated audit", "UNRESOLVED", "preserved projection\nno affirmative candidate", BLUE),
        (0.68, "Native factual audit", "MISMATCH", "policy-relative interpretation\nreview candidates", TEAL),
    ]
    for x, head, mid, bottom, color in cases:
        box(ax, x, 0.30, 0.265, 0.43, head, f"{mid}\n\n{bottom}", edge=color, body_size=10)
    ax.text(0.5, 0.18, "No retain / deploy / rollback command is generated.", ha="center", fontsize=12, fontweight="bold", color=ORANGE)
    ax.text(0.5, 0.105, "Post-action facts require a new Paper XIII audit.", ha="center", fontsize=11, color=GRAY_2)
    save(fig, OUT, "fig6_admission_boundary")


def main() -> None:
    fig1_factorization()
    fig2_interpretation_relativity()
    fig4_channel_semantics()
    fig5_workbench()
    fig6_boundary()
    print(f"Wrote Paper XIV figures to {OUT}")


if __name__ == "__main__":
    main()
