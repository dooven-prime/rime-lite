"""Generate the three active Paper XII v2 figures."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "figures"
if str(FIGURES) not in sys.path:
    sys.path.insert(0, str(FIGURES))

from sof_figure_utils import (  # noqa: E402
    BLUE,
    GREEN,
    GRAY_1,
    GRAY_2,
    GRAY_4,
    ORANGE,
    PURPLE,
    arrow,
    box,
    clean,
    save,
    setup,
    title,
)


OUT = FIGURES / "paper12"


def fig1_compile_assemble_protocol_stack() -> None:
    fig, ax = setup((15.2, 8.2))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "SOFRS v2 Compile and Assembly Stack",
        "Paper X owns normative item compilation; Paper XII owns faithful report assembly",
    )

    box(
        ax,
        0.025,
        0.54,
        0.14,
        0.18,
        "Source + Adapter",
        "$S_\\sigma, \\eta$\nsource-addressed realization",
        edge=GRAY_2,
        fill="#f7f7f7",
        body_size=8.8,
    )
    box(
        ax,
        0.205,
        0.54,
        0.16,
        0.18,
        "Paper X Inputs",
        "$M_\\eta, I_\\eta, P_X$\ncapabilities + typed IR",
        edge=BLUE,
        fill="#f2f7fb",
        body_size=8.8,
    )
    box(
        ax,
        0.405,
        0.54,
        0.14,
        0.18,
        r"$\mathrm{Compile}_{v1}$",
        "capability and\npromotion gates",
        edge=BLUE,
        fill="#eef5fa",
        body_size=8.8,
    )
    box(
        ax,
        0.585,
        0.54,
        0.15,
        0.18,
        "CompilerOutput",
        "ordered normative items\n+ degradation items",
        edge=GREEN,
        fill="#f0f8f3",
        body_size=8.8,
    )
    box(
        ax,
        0.775,
        0.54,
        0.10,
        0.18,
        r"$P_A$",
        "Assembly\nProfile v2",
        edge=PURPLE,
        fill="#faf5fc",
        body_size=8.8,
    )
    box(
        ax,
        0.905,
        0.54,
        0.075,
        0.18,
        "SOFRS",
        "v2 report",
        edge=ORANGE,
        fill="#fff8ed",
        body_size=8.8,
    )

    arrow(ax, 0.165, 0.63, 0.205, 0.63, color=GRAY_2)
    arrow(ax, 0.365, 0.63, 0.405, 0.63, color=BLUE)
    arrow(ax, 0.545, 0.63, 0.585, 0.63, color=BLUE)
    arrow(ax, 0.735, 0.63, 0.775, 0.63, color=GREEN)
    arrow(ax, 0.875, 0.63, 0.905, 0.63, color=PURPLE)

    ax.text(
        0.47,
        0.79,
        "Paper X compilation boundary",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=BLUE,
    )
    ax.plot([0.20, 0.75], [0.76, 0.76], color=BLUE, linewidth=2)
    ax.text(
        0.86,
        0.79,
        "Paper XII assembly boundary",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=PURPLE,
    )
    ax.plot([0.77, 0.98], [0.76, 0.76], color=PURPLE, linewidth=2)

    box(
        ax,
        0.09,
        0.19,
        0.24,
        0.16,
        "Assembly Faithfulness",
        "one ordered compiler item\nfor one report claim or degradation item",
        edge=GREEN,
        fill="#f0f8f3",
        body_size=9.0,
    )
    box(
        ax,
        0.38,
        0.19,
        0.24,
        0.16,
        "Permitted Additions",
        "envelope, provenance, alignment-ready\nand presentation metadata",
        edge=PURPLE,
        fill="#faf5fc",
        body_size=9.0,
    )
    box(
        ax,
        0.67,
        0.19,
        0.24,
        0.16,
        "Forbidden Assembly Moves",
        "no normative item addition, deletion,\nduplication, or semantic alteration",
        edge=ORANGE,
        fill="#fff8ed",
        body_size=9.0,
    )
    arrow(ax, 0.66, 0.53, 0.50, 0.35, color=GREEN)
    ax.text(
        0.5,
        0.075,
        "The validation receipt binds the exact source, compiler, assembly, validator, and contract closure.",
        ha="center",
        fontsize=11.5,
        fontweight="bold",
        color=GRAY_1,
    )
    save(fig, OUT, "fig1_compile_assemble_protocol_stack")


def fig2_claim_scoped_epistemic_boundary() -> None:
    fig, ax = setup((14.8, 8.4))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Claim-Scoped External Basis",
        "Protocol conformance and external scientific support remain separately typed",
    )

    packages = [
        (0.035, "Source identity", "snapshot and producer\ndigest binding", BLUE, "#eef5fa"),
        (0.275, "Object recomputation", "independent finite\nobject evidence", GREEN, "#f0f8f3"),
        (0.515, "Structure validation", "realization and carrier\nadmission evidence", PURPLE, "#faf5fc"),
        (0.755, "Domain adequacy", "semantic fitness for the\nexternal question", ORANGE, "#fff8ed"),
    ]
    for x, head, body, edge, fill in packages:
        box(ax, x, 0.60, 0.20, 0.17, head, body, edge=edge, fill=fill, body_size=8.8)
    ax.text(
        0.5,
        0.82,
        "Package status vocabulary: SATISFIED / PARTIAL / NOT_ASSESSED / NOT_APPLICABLE",
        ha="center",
        fontsize=9.5,
        color=GRAY_2,
        fontweight="bold",
    )

    box(
        ax,
        0.18,
        0.30,
        0.25,
        0.15,
        "Claim A",
        "external_basis_refs = {source, object}\nconstraint IDs are explicit",
        edge=GREEN,
        fill="#f0f8f3",
        body_size=8.8,
    )
    box(
        ax,
        0.57,
        0.30,
        0.25,
        0.15,
        "Claim B",
        "external_basis_refs = {source}\nno inherited object evidence",
        edge=BLUE,
        fill="#eef5fa",
        body_size=8.8,
    )
    arrow(ax, 0.135, 0.595, 0.27, 0.45, color=BLUE)
    arrow(ax, 0.375, 0.595, 0.34, 0.45, color=GREEN)
    arrow(ax, 0.135, 0.595, 0.65, 0.45, color=BLUE)

    box(
        ax,
        0.07,
        0.08,
        0.25,
        0.11,
        "Protocol-valid report",
        "schema and closure admitted",
        edge=GRAY_2,
        fill="#f7f7f7",
        body_size=8.8,
    )
    box(
        ax,
        0.375,
        0.08,
        0.25,
        0.11,
        "Object Certificate",
        "requires satisfied object-level basis",
        edge=GREEN,
        fill="#f0f8f3",
        body_size=8.8,
    )
    box(
        ax,
        0.68,
        0.08,
        0.25,
        0.11,
        "Scientific adequacy",
        "not implied by protocol conformance",
        edge=ORANGE,
        fill="#fff8ed",
        body_size=8.8,
    )
    ax.plot([0.04, 0.96], [0.245, 0.245], color=GRAY_4, linewidth=1.2)
    save(fig, OUT, "fig2_claim_scoped_epistemic_boundary")


def fig3_report_relativity_alignment() -> None:
    fig, ax = setup((14.2, 8.4))
    clean(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title(
        ax,
        "Report Relativity and Alignment",
        "Reports are derived from declared realizations, not directly from the source system",
    )

    box(
        ax,
        0.39,
        0.76,
        0.22,
        0.11,
        r"Source system $S$",
        "physical, algebraic, computational,\nor behavioral source",
        edge=GRAY_2,
        body_size=9.6,
    )

    box(
        ax,
        0.07,
        0.53,
        0.30,
        0.16,
        r"Realization $\eta_1$",
        r"finite space $V_1$"
        "\n"
        r"sectors $\{Q_i^{(1)}\}$"
        "\n"
        r"observables $\mathcal{X}_1$; specification $\Theta_1$",
        edge=BLUE,
        fill="#f7fbfd",
        body_size=9.6,
    )
    box(
        ax,
        0.63,
        0.53,
        0.30,
        0.16,
        r"Realization $\eta_2$",
        r"finite space $V_2$"
        "\n"
        r"sectors $\{Q_i^{(2)}\}$"
        "\n"
        r"observables $\mathcal{X}_2$; specification $\Theta_2$",
        edge=ORANGE,
        fill="#fffaf3",
        body_size=9.6,
    )
    arrow(ax, 0.46, 0.75, 0.24, 0.70, color=BLUE, lw=2.0)
    arrow(ax, 0.54, 0.75, 0.76, 0.70, color=ORANGE, lw=2.0)

    box(
        ax,
        0.12,
        0.34,
        0.20,
        0.10,
        r"Report $\mathcal{R}_1$",
        "versioned SOFRS artifact",
        edge=BLUE,
        body_size=9.2,
    )
    box(
        ax,
        0.68,
        0.34,
        0.20,
        0.10,
        r"Report $\mathcal{R}_2$",
        "versioned SOFRS artifact",
        edge=ORANGE,
        body_size=9.2,
    )
    arrow(ax, 0.22, 0.525, 0.22, 0.44, color=BLUE, lw=2.0)
    arrow(ax, 0.78, 0.525, 0.78, 0.44, color=ORANGE, lw=2.0)

    ax.text(
        0.5,
        0.39,
        r"$\mathcal{R}_1 \ne \mathcal{R}_2$ may reflect realization choices",
        ha="center",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color=GRAY_1,
    )

    box(
        ax,
        0.33,
        0.17,
        0.34,
        0.11,
        "Explicit alignment",
        r"$\Phi_{\mathrm{sec}},\ \Phi_{\mathrm{obs}},\ \Theta_{\mathrm{cmp}}$",
        edge=PURPLE,
        fill="#fbf8fc",
        body_size=11.0,
    )
    arrow(ax, 0.22, 0.33, 0.40, 0.29, color=BLUE, lw=2.0)
    arrow(ax, 0.78, 0.33, 0.60, 0.29, color=ORANGE, lw=2.0)

    box(
        ax,
        0.39,
        0.035,
        0.22,
        0.075,
        r"Audit signature $\Delta_{\mathrm{audit}}$",
        "aligned comparison output",
        edge=GREEN,
        fill="#f7fbf8",
        body_size=9.2,
    )
    arrow(ax, 0.50, 0.165, 0.50, 0.115, color=GREEN, lw=2.0)

    save(fig, OUT, "fig3_report_relativity_alignment")


def main() -> None:
    fig1_compile_assemble_protocol_stack()
    fig2_claim_scoped_epistemic_boundary()
    fig3_report_relativity_alignment()
    print(f"Wrote 3 active Paper XII figures to {OUT}")


if __name__ == "__main__":
    main()
