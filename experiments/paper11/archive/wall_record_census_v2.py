"""Paper XI v2-prep wall-record coverage census.

The v2 census extends, but does not mutate, the frozen 24-record v1 census.
Four post-v1 profile records are admitted with explicit deformation,
change locus, measured signature, evidence file, and claim boundary.

Coverage is a predeclared finite-sample curation rule, not a classification theorem. The
15-species prevalence sample from v1 remains a separate statistic and is not
silently expanded by these wall-record additions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER11_DIR = SCRIPT_DIR.parent
ROOT = PAPER11_DIR.parents[1]
sys.path.insert(0, str(PAPER11_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

import wall_record_census as v1


RESULTS_DIR = SCRIPT_DIR / "results"
PAPER_PATH = ROOT / "papers" / "paper11" / "Paper XI - v1.1.md"


V2_ADDITIONS = [
    v1.record(
        "A-constructed-goe-endpoint",
        "Constructed real-symmetric spectral family",
        ["A"],
        "two isolated adjacent eigenvalue gaps",
        "degenerate endpoint with GOE splitting direction",
        "two order-one pair-gap closures at t=0",
        "experiments/paper11/validation/degenerate_endpoint_collision.py",
        "constructed_witness",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note=(
            "Constructed non-Rubik Class A witness. The double-level endpoint "
            "has ambient codimension two; endpoint perturbation removes both "
            "collisions. Not a generic one-parameter GOE crossing."
        ),
    ),
    v1.record(
        "BE-nested-percolation-opening",
        "Erdos-Renyi percolation ensemble",
        ["B", "E"],
        "direct support and bounded word-depth reachability",
        "nested edge-threshold probability path",
        "monotone repair window near p=0.08--0.10",
        "experiments/paper11/validation/percolation_wall.py",
        "candidate_evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note=(
            "Pathwise edge addition is discrete and monotone; the ensemble "
            "mean and fluctuation profile define the transition window."
        ),
    ),
    v1.record(
        "DE-kuramoto-freezing-crossover",
        "Kuramoto oscillator ensemble",
        ["D", "E"],
        "order-parameter occupancy and bounded word-depth freezing",
        "matched coupling-strength sweep",
        "freezing crossover near K=1.6--1.8",
        "experiments/paper11/validation/kuramoto_wall.py",
        "candidate_evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note=(
            "Smooth phase dynamics induce a thresholded finite-sector shadow. "
            "The freezing direction is stable across the tested matched ensembles."
        ),
    ),
    v1.record(
        "C-grn-terminal-basin-loss",
        "GRN toggle-switch flow",
        ["C"],
        "terminal attractor count and terminal-sector identity",
        "continuous regulatory-edge weakening",
        "two-to-one basin loss in lambda bracket 0.520--0.525",
        "experiments/paper11/validation/grn_toggle_wall.py",
        "candidate_evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note=(
            "Class C terminal-structure witness. The discrete edge-deletion "
            "endpoint has an E-coordinate, but the primary wall mechanism is "
            "continuous deterministic basin loss. The CLE/SSA noise wall is withdrawn."
        ),
    ),
]


WALL_RECORDS_V2 = [*v1.WALL_RECORDS, *V2_ADDITIONS]


def compute_census_v2() -> dict:
    census = v1.compute_census(WALL_RECORDS_V2)
    census["class_coverage"]["C"]["name"] = "Terminal-structure"
    census["species_prevalence"]["C"]["name"] = "Terminal-structure"
    return {
        **census,
        "version": "paper11-v2-prep",
        "base_version": "paper11-v1.0-frozen",
        "base_record_count": len(v1.WALL_RECORDS),
        "added_record_count": len(V2_ADDITIONS),
        "coverage_interpretation": (
            "predeclared finite-sample record, species, and deformation coverage; "
            "not completeness of the wall taxonomy"
        ),
        "class_a_boundary": (
            "coverage closes through a constructed non-Rubik witness; "
            "naturally occurring non-Rubik Class A breadth remains open"
        ),
    }


def markdown_report_v2(census: dict) -> str:
    preamble = [
        "# Paper XI v2 Wall-Record Coverage Census",
        "",
        f"- Frozen v1 records retained: **{census['base_record_count']}**",
        f"- Post-v1 records added: **{census['added_record_count']}**",
        f"- v2 registered wall records: **{census['record_count']}**",
        f"- v2 first-pass eligible records: **{census['eligible_record_count']}**",
        "- Coverage target: at least 3 eligible records, 2 species, and 2 deformation origins per class.",
        "- Coverage means predeclared finite-sample curation coverage, not taxonomy completeness.",
        "- Class A closes through a constructed witness; natural non-Rubik breadth remains open.",
        "",
    ]
    base_lines = v1.markdown_report(census).splitlines()
    if base_lines and base_lines[0].startswith("# "):
        base_lines = base_lines[2:]
    return "\n".join([*preamble, *base_lines]) + "\n"


def verify_paper_table_v2(census: dict) -> None:
    if not PAPER_PATH.is_file():
        return
    paper = PAPER_PATH.read_text(encoding="utf-8")
    missing = []
    for wall_class, row in census["class_coverage"].items():
        expected = (
            f"| {wall_class} | {row['registered_records']} | "
            f"{row['eligible_records']} | {row['unique_eligible_species']} | "
            f"{row['unique_eligible_deformations']} | {row['coverage_status']} |"
        )
        if expected not in paper:
            missing.append(expected)
    if missing:
        raise RuntimeError(
            "Paper XI v2 coverage table is out of sync:\n" + "\n".join(missing)
        )


def main() -> None:
    census = compute_census_v2()
    failed = [
        wall_class
        for wall_class, row in census["class_coverage"].items()
        if row["coverage_status"] != "pass"
    ]
    if failed:
        raise SystemExit(f"v2 predeclared coverage remains open for: {failed}")
    verify_paper_table_v2(census)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "wall_record_census_v2.json"
    md_path = RESULTS_DIR / "wall_record_census_v2.md"
    json_path.write_text(json.dumps(census, indent=2), encoding="utf-8")
    md_path.write_text(markdown_report_v2(census), encoding="utf-8")

    print("=" * 72)
    print("  Paper XI v2 wall-record coverage census")
    print("=" * 72)
    print(
        f"records={census['record_count']}, eligible={census['eligible_record_count']}, "
        f"memberships={census['class_membership_count']}"
    )
    for wall_class, row in census["class_coverage"].items():
        print(
            f"{wall_class}: eligible={row['eligible_records']}, "
            f"species={row['unique_eligible_species']}, "
            f"deformations={row['unique_eligible_deformations']}, "
            f"status={row['coverage_status']}"
        )
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
