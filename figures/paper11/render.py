"""Render the typed Paper XI wall-record, profile, and census figures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "figures" / "paper11"
CENSUS_PATH = ROOT / "experiments" / "paper11" / "results" / "wall_record_census_typed_v3.json"
CNOT_PATH = ROOT / "experiments" / "paper11" / "results" / "cnot_logarithm_boundary_v1.json"
sys.path.insert(0, str(ROOT))

from figures.style import save_figure


BLUE = "#24567a"
TEAL = "#17725f"
ORANGE = "#c36f1f"
PURPLE = "#6e4b9e"
RED = "#b6423a"
INK = "#27333d"
MUTED = "#65727b"
GRID = "#cbd4d8"
LIGHT_BLUE = "#f3f8fc"
LIGHT_TEAL = "#f1faf6"
LIGHT_ORANGE = "#fff7ed"
LIGHT_PURPLE = "#f8f4fc"
LIGHT_RED = "#fff4f2"


def load_current_records() -> tuple[dict, dict]:
    census = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
    cnot = json.loads(CNOT_PATH.read_text(encoding="utf-8"))

    expected = {
        "historical_record_count": 28,
        "active_record_count": 27,
        "retired_record_count": 1,
        "main_wall_spectrum_record_count": 5,
        "analogue_morphology_record_count": 2,
        "morphology_record_bundle_count": 7,
        "morphology_atom_count": 7,
        "registered_atom_field_entry_count": 10,
        "trajectory_change_entry_count": 8,
        "locus_germ_entry_count": 2,
        "active_tag_membership_count": 34,
    }
    for key, value in expected.items():
        if census.get(key) != value:
            raise ValueError(f"Paper XI census drift: {key}={census.get(key)!r}, expected {value}")

    if cnot.get("wall_admission") != "not_admitted":
        raise ValueError("Paper XI CNOT diagnostic was promoted unexpectedly")
    if cnot.get("affine_path", {}).get("singularity", {}).get("strength") != 0.5:
        raise ValueError("Paper XI CNOT singular coordinate has drifted")
    unitary = cnot.get("unitary_control", {})
    if not unitary.get("continuous_logarithm_branch_certified"):
        raise ValueError("Paper XI CNOT unitary control lacks a continuous logarithm")
    if unitary.get("sampled_internal_support_transition_detected") is not False:
        raise ValueError("Paper XI CNOT unitary control acquired an interior transition")
    return census, cnot


def clean(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def heading(ax, title, subtitle):
    ax.text(.03, .965, title, fontsize=18, fontweight="bold", color=INK)
    ax.text(.03, .925, subtitle, fontsize=10.5, color=MUTED)


def box(
    ax,
    x,
    y,
    w,
    h,
    title,
    body="",
    *,
    edge=BLUE,
    face=LIGHT_BLUE,
    title_size=9.5,
    body_size=8.5,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.010,rounding_size=0.010",
        linewidth=1.45,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h - .026,
        title,
        ha="center",
        va="top",
        fontsize=title_size,
        fontweight="bold",
        color=edge,
    )
    if body:
        ax.text(
            x + w / 2,
            y + h / 2 - .012,
            body,
            ha="center",
            va="center",
            fontsize=body_size,
            color=INK,
            linespacing=1.25,
        )


def arrow(ax, start, end, *, color=MUTED, dashed=False, label=None, dy=.018):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "lw": 1.3,
            "color": color,
            "linestyle": "--" if dashed else "-",
            "shrinkA": 2,
            "shrinkB": 2,
        },
    )
    if label:
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + dy,
            label,
            ha="center",
            va="center",
            fontsize=7.7,
            color=MUTED,
        )


def figure_1():
    fig, ax = plt.subplots(figsize=(13.5, 11.0))
    clean(ax)
    heading(
        ax,
        "Profile-Relative Wall Corpus",
        "Paper XI separates strict and analogue morphology bundles from non-wall context records.",
    )

    box(
        ax,
        .055,
        .77,
        .36,
        .12,
        "Paper IX: admissible wall datum",
        "chart + selected primary field\ndiscriminant + path/domain + policy",
        edge=BLUE,
        face=LIGHT_BLUE,
    )
    box(
        ax,
        .585,
        .77,
        .36,
        .12,
        "Paper X: validated evidence boundary",
        "realization kind + capabilities\nsource address + claim status",
        edge=PURPLE,
        face=LIGHT_PURPLE,
    )

    box(
        ax,
        .25,
        .60,
        .50,
        .11,
        "Paper XI corpus constructions",
        r"$\operatorname{RecordWall}_{P_W}(\mathfrak{D}_\kappa)\in\mathrm{StrictWallRecord}$"
        "\n"
        r"$\operatorname{RecordAnalogueMorphology}_{P_W}(s)\in\mathrm{AnalogueMorphologyRecord}$",
        edge=ORANGE,
        face=LIGHT_ORANGE,
        title_size=10.5,
        body_size=8.4,
    )
    arrow(ax, (.235, .76), (.40, .72), color=BLUE)
    arrow(ax, (.765, .76), (.60, .72), color=PURPLE)

    ax.text(
        .5,
        .548,
        "$\\mathrm{WallCorpusEntry}=\\mathrm{MorphologyRecordBundle}\\sqcup\\mathrm{WallContextRecord}$\n"
        "$\\mathrm{MorphologyRecordBundle}=\\mathrm{StrictWallRecord}\\sqcup\\mathrm{AnalogueMorphologyRecord}$",
        ha="center",
        fontsize=9.3,
        fontweight="bold",
        color=INK,
    )
    arrow(ax, (.44, .515), (.28, .50), color=TEAL)
    arrow(ax, (.56, .515), (.72, .50), color=PURPLE)

    box(
        ax,
        .055,
        .32,
        .40,
        .17,
        "TrajectoryEvent",
        "trajectory_ref + orientation\nevent interval + left/right sampling\n"
        r"$\delta_e^\gamma:q\mapsto(v_q^-,v_q^+,\mathrm{change}_q)$"
        "\npresent, typed, distinct primary endpoints",
        edge=TEAL,
        face=LIGHT_TEAL,
        title_size=10.5,
        body_size=9.0,
    )
    box(
        ax,
        .545,
        .32,
        .40,
        .17,
        "LocusSample",
        "domain context + event locus\nincident-stratum germ; no intrinsic order\n"
        r"$\delta_e^{\rm loc}:q\mapsto\{(C_\alpha,v_{q,\alpha})\}_\alpha$"
        "\nprobe order retained only when declared",
        edge=PURPLE,
        face=LIGHT_PURPLE,
        title_size=10.5,
        body_size=9.0,
    )

    box(
        ax,
        .19,
        .19,
        .62,
        .075,
        "one primary field + independently registered context fields",
        "context changes are co-observations; each retains applicable policies and evidence",
        edge=ORANGE,
        face=LIGHT_ORANGE,
        title_size=10,
        body_size=8.5,
    )
    arrow(ax, (.255, .31), (.39, .275), color=TEAL)
    arrow(ax, (.745, .31), (.61, .275), color=PURPLE)

    box(
        ax,
        .055,
        .045,
        .40,
        .075,
        "strict SOF wall spectrum",
        "upstream-admitted strict_sof atoms only",
        edge=BLUE,
        face=LIGHT_BLUE,
    )
    box(
        ax,
        .545,
        .045,
        .40,
        .075,
        "diagnostic analogue morphology",
        "included without upstream strict-wall admission",
        edge=RED,
        face=LIGHT_RED,
    )
    arrow(ax, (.43, .18), (.255, .13), color=BLUE)
    arrow(ax, (.57, .18), (.745, .13), color=RED)
    ax.text(
        .5,
        .155,
        "morphology signature, routed by upstream admission and corpus inclusion",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )

    save_figure(fig, FIGURE_DIR, "fig1_wall_record_pipeline")


def figure_2():
    fig, ax = plt.subplots(figsize=(13.5, 11))
    clean(ax)
    heading(
        ax,
        "Structured Wall Coordinates and Nonexclusive Curation",
        "Morphology identity, observation policy, and versioned curation remain separate typed objects.",
    )

    families = [
        ("Field families", "operator / route / word / Lie-Hall\nclosure / spectral / state / proxy", BLUE, LIGHT_BLUE),
        ("Event kinds", "support gain/loss / collision / repair\nfirst-hit change / terminalization / boundary hit", TEAL, LIGHT_TEAL),
        ("Regularity", "smooth / stratified / piecewise smooth\ndiscrete / stochastic / unknown", PURPLE, LIGHT_PURPLE),
        ("Persistence profile", "transient / persistent / oscillatory\nplateau / terminal / unresolved", ORANGE, LIGHT_ORANGE),
        ("Geometry", "location + crossing\n+ codimension status", BLUE, LIGHT_BLUE),
        ("Evidence", "Theorem / Computational Certificate\nComputational Observation / Research Program", RED, LIGHT_RED),
    ]
    for index, (title, body, edge, face) in enumerate(families):
        row, col = divmod(index, 2)
        box(
            ax,
            .035 + col * .29,
            .68 - row * .18,
            .255,
            .135,
            title,
            body,
            edge=edge,
            face=face,
            title_size=9.0,
            body_size=8.0,
        )

    box(
        ax,
        .63,
        .64,
        .335,
        .175,
        "Versioned curation assignment",
        "paper11-curation-tags-v1.0\n\nCOLLISION   REPAIR   TERMINAL\nPLATEAU_RATE\nNONSMOOTH_DISCRETE\nBRIDGE_INCIDENCE",
        edge=ORANGE,
        face=LIGHT_ORANGE,
        title_size=9.5,
        body_size=8.5,
    )
    box(
        ax,
        .63,
        .41,
        .335,
        .14,
        "Tags are not a partition",
        "one record may carry several tags\na tagged static witness may remain outside\nthe strict wall spectrum",
        edge=RED,
        face=LIGHT_RED,
        title_size=9.5,
        body_size=8.5,
    )
    arrow(ax, (.795, .63), (.795, .56), color=ORANGE)

    box(
        ax,
        .08,
        .13,
        .84,
        .11,
        r"$\operatorname{MorphSig}^{P_W}_W(e)$ and $\operatorname{CuratedSig}^{P_W,v}_W(e)$",
        "morphology: realization + role + atom kind + field/carrier + delta + profile\ncurated view: morphology signature + versioned assignment",
        edge=TEAL,
        face=LIGHT_TEAL,
        title_size=10.5,
        body_size=9.0,
    )
    for x in (.18, .47, .80):
        arrow(ax, (x, .31 if x < .6 else .40), (x, .25), color=MUTED, dashed=True)

    ax.text(
        .5,
        .065,
        r"Sampling, censoring, threshold, normalization, and cutoff remain policies in $P_W$; they are not morphology axes.",
        ha="center",
        fontsize=11,
        color=RED,
        style="italic",
    )

    save_figure(fig, FIGURE_DIR, "fig2_observable_wall_taxonomy")


def figure_3(census: dict, cnot: dict):
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.5))
    # heading(
    #     ax=axes[0],
    #     title="Typed Census and Sampled Lie/Hall Repair",
    #     subtitle="Current source-addressed records; no population prevalence or continuous threshold is inferred.",
    # )
    fig.suptitle(
        "Typed Census and CNOT Path-Admissibility Diagnostic",
        x=.03,
        ha="left",
        fontsize=17,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        .03,
        .91,
        "Current source-addressed records; no prevalence, wall bracket, or repair threshold is inferred.",
        fontsize=10.5,
        color=MUTED,
    )

    role_summary = census["record_role_summary"]
    roles = [
        ("pre-wall reference", role_summary["pre_wall_reference"]),
        ("static boundary witness", role_summary["static_boundary_witness"]),
        ("trajectory diagnostic", role_summary["trajectory_diagnostic"]),
        ("wall event", role_summary["wall_event"]),
        ("wall locus sample", role_summary["wall_locus_sample"]),
    ]
    labels = [label for label, _ in roles]
    values = [value for _, value in roles]
    colors = [GRID, MUTED, ORANGE, TEAL, BLUE]

    ax = axes[0]
    bars = ax.barh(labels, values, color=colors, height=.70)
    ax.invert_yaxis()
    ax.set_title("27 active typed records", fontsize=11, color=INK)
    ax.set_xlabel("record count")
    ax.set_xlim(0, 12.5)
    ax.set_xticks(range(0, 13, 2))
    ax.grid(axis="x", alpha=.22)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + .22, bar.get_y() + bar.get_height() / 2, str(value), va="center", color=INK)
    ax.text(
        .02,
        -.22,
        "5 strict wall bundles  |  2 analogue morphology bundles\n"
        "20 other active records  |  34 recomputed tag memberships",
        transform=ax.transAxes,
        fontsize=9.0,
        color=INK,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": LIGHT_BLUE, "edgecolor": BLUE},
    )

    affine_samples = cnot["affine_path"]["rows"]
    unitary_samples = cnot["unitary_control"]["rows"]
    strength = [sample["strength"] for sample in affine_samples]
    affine_hall = [
        float("nan")
        if sample["lie_reached_without_direct_support_pairs"] is None
        else sample["lie_reached_without_direct_support_pairs"]
        for sample in affine_samples
    ]
    unitary_hall = [
        sample["lie_reached_without_direct_support_pairs"]
        for sample in unitary_samples
    ]
    comparison = cnot["affine_path"]["sampled_side_comparison"]
    lower = comparison["left_sample"]["strength"]
    singular = cnot["affine_path"]["singularity"]["strength"]
    upper = comparison["right_sample"]["strength"]

    ax = axes[1]
    ax.plot(
        strength,
        affine_hall,
        color=PURPLE,
        lw=2.2,
        marker="o",
        ms=4,
        label="affine samplewise log",
    )
    ax.plot(
        strength,
        unitary_hall,
        color=TEAL,
        lw=2.2,
        ls="--",
        marker="s",
        ms=3.5,
        label="unitary continuous log",
    )
    ax.axvspan(lower, upper, color=ORANGE, alpha=.12)
    ax.axvline(singular, color=RED, ls="--", lw=1.7)
    ax.annotate(
        "s=0.50 singular\nno finite matrix logarithm",
        xy=(singular, 3),
        xytext=(.58, 2.55),
        arrowprops={"arrowstyle": "->", "color": ORANGE, "lw": 1.2},
        fontsize=9.0,
        color=ORANGE,
    )
    ax.annotate(
        "unitary control: 6/12\nfor every sampled s>0",
        xy=(.75, 6),
        xytext=(.57, 4.45),
        arrowprops={"arrowstyle": "->", "color": TEAL, "lw": 1.2},
        fontsize=9.0,
        color=TEAL,
    )
    ax.set_title("Affine failure versus unitary control", fontsize=11, color=INK)
    ax.set_xlabel("path parameter s")
    ax.set_ylabel("Lie-reached pairs without direct support (of 12)")
    ax.set_xlim(-.02, 1.02)
    ax.set_ylim(-.4, 6.8)
    ax.set_yticks([0, 2, 4, 6])
    ax.grid(alpha=.22)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5)
    ax.text(
        .5,
        -.22,
        "The affine side difference crosses an excluded singular point.\n"
        "The admissible control has no sampled interior repair threshold.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color=RED,
        style="italic",
    )

    fig.tight_layout(rect=(0, .12, 1, .95), w_pad=3.5)
    save_figure(fig, FIGURE_DIR, "fig3_census_and_cnot_log_domain")


def main():
    census, cnot = load_current_records()
    figure_1()
    figure_2()
    figure_3(census, cnot)
    print(f"Paper XI figures written to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
