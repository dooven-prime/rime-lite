"""Paper XI wall-record coverage census.

This audit separates two statistics that must not be conflated:

1. species prevalence: fraction of the 15-species taxonomy sample carrying a
   class at least once;
2. wall-record coverage: number and diversity of independently registered
   observable/deformation records assigned to each class.

A record is first-pass eligible when it has an explicit deformation, an
explicit change locus, a measured signature, and an existing evidence file.
Eligibility is a coverage rule for this census, not a theorem criterion.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from wall_density_registry import SPECIES, WALL_TYPES, compute_density


ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
PAPER_PATH = ROOT / "papers" / "paper11" / "Paper XI - v1.md"
TARGET_RECORDS = 3
TARGET_SPECIES = 2
TARGET_DEFORMATIONS = 2


def record(
    record_id: str,
    species: str,
    classes: list[str],
    observable: str,
    deformation_origin: str,
    change_locus: str,
    evidence: str,
    claim_status: str,
    *,
    explicit_deformation: bool,
    explicit_locus: bool,
    measured_signature: bool,
    note: str = "",
) -> dict:
    return {
        "record_id": record_id,
        "species": species,
        "classes": classes,
        "observable": observable,
        "deformation_origin": deformation_origin,
        "change_locus": change_locus,
        "evidence": evidence,
        "claim_status": claim_status,
        "explicit_deformation": explicit_deformation,
        "explicit_locus": explicit_locus,
        "measured_signature": measured_signature,
        "note": note,
    }


WALL_RECORDS = [
    record(
        "A-rubik-collision-quotient",
        "Rubik QT/HT",
        ["A"],
        "finite QT/HT joint spectrum",
        "affine projection parameter",
        "unique maximal collision at alpha=2/3",
        "experiments/paper4/validation/rubik_collision_quotient.py",
        "theorem",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "A-rubik-endpoint-pair-closures",
        "Rubik QT/HT",
        ["A"],
        "Hermitian spectral probe eigenvalue gaps",
        "single QT generator weight",
        "16 pairwise closures at the canonical endpoint",
        "experiments/paper11/spectral_ade_collision.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "A-rubik-simultaneous-pair-gap-response",
        "Rubik QT/HT",
        ["A"],
        "two independently indexed spectral gaps",
        "two-weight diagonal QT path",
        "one to three common half-closure responses across tested sampling resolutions",
        "experiments/paper11/spectral_ade_collision.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=False,
        measured_signature=True,
        note="Pair-gap response only; count is sampling-resolution dependent; no eigenbranch continuation or A2 identification.",
    ),
    record(
        "BF-rubik-r2-repair",
        "Rubik accessibility",
        ["B", "F"],
        "R1/R2 accessibility support",
        "fixed generator family",
        "path-commutator cancellation repaired at R2",
        "experiments/paper5/validation/path_commutator_cancellation.py",
        "evidence",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
        note="Static repair mechanism, not yet a deformation wall record.",
    ),
    record(
        "F-rubik-type-iii-cancellation",
        "Rubik Type III/IV wild",
        ["F"],
        "projected bridge products",
        "static natural-sector audit",
        "Type III cancellation instances",
        "experiments/paper10/rubik_wild_type34_audit.py",
        "evidence",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
    ),
    record(
        "F-rubik-type-iv-incidence",
        "Rubik Type III/IV wild",
        ["F"],
        "bridge-product incidence",
        "algebraic bridge perturbation",
        "rank/incidence variety for AB=0",
        "experiments/paper7/validation/incidence_variety_codim.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="Bridge-level incidence evidence, not a universal Type IV theorem.",
    ),
    record(
        "BF-synthetic-complement-repair",
        "Synthetic Type III/IV",
        ["B", "F"],
        "support/scalar complement bridge",
        "constructed obstruction control",
        "nonzero R2 bridge across an R1 obstruction",
        "experiments/paper5/validation/complement_explosion.py",
        "evidence",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
    ),
    record(
        "BCF-quantum-cnot-threshold",
        "Quantum Clifford+CNOT",
        ["B", "C", "F"],
        "computational-basis accessibility",
        "CNOT-strength matrix interpolation",
        "repair threshold at strength 0.55",
        "experiments/paper11/repair_persistence_quantum.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="Terminal pre-threshold side, bridge repair, and persistent repaired side.",
    ),
    record(
        "BF-control-kalman-chain",
        "Control Kalman",
        ["B", "F"],
        "controllability-flag word depth",
        "static chain realization",
        "terminal sector reached at word depth 2",
        "experiments/paper10/control_pde_combinatorial_sof.py",
        "diagnostic",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
    ),
    record(
        "B-transformer-lie-depth-repair",
        "NN Transformer activation",
        ["B"],
        "activation-sector accessibility",
        "single synthetic transformer realization",
        "2 frozen-R1 pairs repaired at Lie depth",
        "experiments/paper12/transformer_activation_sof.py",
        "diagnostic",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
    ),
    record(
        "BC-moe-bias-repair",
        "Mixture-of-Experts routing",
        ["B", "C"],
        "private-expert activity",
        "load-bias update trajectory",
        "10 dead experts repair from step 18",
        "experiments/paper12/moe_bias_repair_sof.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="Routing repair, not Lie-depth D-repair.",
    ),
    record(
        "B-diffusion-denoising-repair",
        "Diffusion / denoising",
        ["B"],
        "PCA-sign sector count and support",
        "forward diffusion and reverse denoising time",
        "sector split at t=11 and reverse repair",
        "experiments/paper12/diffusion_denoising_sof.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "BE-maze-door-wall",
        "Dynamic maze connectivity",
        ["B", "E"],
        "component and frozen-pair counts",
        "discrete door closure/reopening path",
        "24 splits followed by 24 reverse merges",
        "experiments/paper12/maze_wall_crossing.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="Connectivity repair, not fixed-sector D-repair.",
    ),
    record(
        "BF-recommender-targeted-bridge",
        "Recommender structural coverage",
        ["B", "F"],
        "user-item cluster coverage",
        "targeted interaction intervention",
        "unreachable pairs reduced from 12/16 to 10/16",
        "experiments/paper12/recommender_sof.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "C-markov-absorbing-endpoint",
        "Markov absorbing",
        ["C"],
        "communicating/frozen-pair accessibility",
        "endpoint contrast across transition systems",
        "absorbing example has 2 terminal frozen pairs",
        "experiments/paper11/cross_species_wall_audit.py",
        "diagnostic",
        explicit_deformation=False,
        explicit_locus=True,
        measured_signature=True,
        note="Endpoint contrast; a parameterized absorbing-limit path remains to be added.",
    ),
    record(
        "C-barrier-stopping-boundary",
        "Barrier option GBM",
        ["C"],
        "cross-barrier support and first-hit time",
        "log-price diffusion",
        "absorbing barrier/stopping boundary",
        "experiments/paper10/barrier_option_sof.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="First hitting is not identified with SOF depth.",
    ),
    record(
        "D-xu-ridge-rate-hierarchy",
        "Xu ridge model",
        ["D"],
        "parallel/null parameter rates",
        "optimization time",
        "slow/fast rate ratio about 68553x",
        "experiments/paper9/state_mixing_fft.py",
        "proxy_only",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "D-mechanism-separated-rates",
        "Mechanism-separated SOF",
        ["D"],
        "K0 growth and K1 decay proxies",
        "gradient/regularization response time",
        "tau(K0)=30 and tau(K1)=1380",
        "experiments/paper9/calibrated_response.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
        note="Proxy-rate evidence; no K-to-R/D bridge.",
    ),
    record(
        "D-yang-state-mixing-plateau",
        "Yang-like photonic",
        ["D"],
        "filtration plateau profile",
        "state-mixing parameter",
        "monotone/flat plateau degeneration with 1/5 zero crossings",
        "experiments/paper9/state_mixing_fft.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "D-rubik-generator-weight-plateau",
        "Rubik deformation probes",
        ["D"],
        "depth plateau P3",
        "QT generator-weight deformation",
        "oscillatory plateau profile with 3/8 zero crossings",
        "experiments/paper9/state_mixing_fft.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "E-graph-edge-removal",
        "Graph P3/C4",
        ["E"],
        "Laplacian spectral gap",
        "discrete edge removal",
        "nonzero gap jump after rewiring",
        "experiments/paper11/cross_species_wall_audit.py",
        "diagnostic",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "E-relu-kink",
        "NN Transformer activation",
        ["E"],
        "mean absolute activation response",
        "activation bias",
        "slope jump at ReLU bias 0",
        "experiments/paper11/piecewise_smooth_activation_wall.py",
        "evidence",
        explicit_deformation=True,
        explicit_locus=True,
        measured_signature=True,
    ),
    record(
        "E-topk-rank-selection",
        "NN Transformer activation",
        ["E"],
        "top-k active-entry count",
        "activation bias samples",
        "rank-selection boundary not crossed on the tested grid",
        "experiments/paper11/piecewise_smooth_activation_wall.py",
        "boundary",
        explicit_deformation=True,
        explicit_locus=False,
        measured_signature=True,
        note="Negative boundary record; no top-k wall event observed.",
    ),
    record(
        "F-ncg-t7-bridge",
        "Finite spectral triple",
        ["F"],
        "Dirac-block and one-form bridge support",
        "static finite spectral-triple realization",
        "2 ordered T7-style bridges",
        "experiments/paper10/ncg_spectral_triple_sof.py",
        "diagnostic",
        explicit_deformation=False,
        explicit_locus=False,
        measured_signature=True,
    ),
]


def validate_records(records: list[dict]) -> None:
    ids = [item["record_id"] for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("wall-record ids must be unique")
    valid_classes = set(WALL_TYPES)
    for item in records:
        unknown = set(item["classes"]) - valid_classes
        if unknown:
            raise ValueError(f"{item['record_id']}: unknown classes {sorted(unknown)}")


def enrich_record(item: dict) -> dict:
    evidence_exists = (ROOT / item["evidence"]).is_file()
    eligible = all(
        [
            item["explicit_deformation"],
            item["explicit_locus"],
            item["measured_signature"],
            evidence_exists,
        ]
    )
    return {**item, "evidence_exists": evidence_exists, "eligible": eligible}


def compute_census(records: list[dict] = WALL_RECORDS) -> dict:
    validate_records(records)
    enriched = [enrich_record(item) for item in records]
    class_rows = {}
    membership_count = sum(len(item["classes"]) for item in enriched)
    for wall_class, class_name in WALL_TYPES.items():
        members = [item for item in enriched if wall_class in item["classes"]]
        eligible = [item for item in members if item["eligible"]]
        species = sorted({item["species"] for item in eligible})
        deformations = sorted({item["deformation_origin"] for item in eligible})
        target_checks = {
            "records": len(eligible) >= TARGET_RECORDS,
            "species": len(species) >= TARGET_SPECIES,
            "deformations": len(deformations) >= TARGET_DEFORMATIONS,
        }
        class_rows[wall_class] = {
            "name": class_name,
            "registered_records": len(members),
            "membership_share": len(members) / membership_count,
            "eligible_records": len(eligible),
            "unique_eligible_species": len(species),
            "unique_eligible_deformations": len(deformations),
            "eligible_species": species,
            "eligible_deformations": deformations,
            "target_checks": target_checks,
            "coverage_status": "pass" if all(target_checks.values()) else "gap",
        }

    species_density = compute_density(SPECIES)
    return {
        "record_count": len(enriched),
        "eligible_record_count": sum(item["eligible"] for item in enriched),
        "class_membership_count": membership_count,
        "targets": {
            "eligible_records_per_class": TARGET_RECORDS,
            "unique_species_per_class": TARGET_SPECIES,
            "deformation_origins_per_class": TARGET_DEFORMATIONS,
        },
        "class_coverage": class_rows,
        "species_prevalence": species_density,
        "records": enriched,
    }


def markdown_report(census: dict) -> str:
    lines = [
        "# Paper XI Wall-Record Coverage Census",
        "",
        f"- Registered wall records: **{census['record_count']}**",
        f"- First-pass eligible records: **{census['eligible_record_count']}**",
        f"- Class memberships: **{census['class_membership_count']}** (multi-label records allowed)",
        "- Coverage target: at least 3 eligible records, 2 species, and 2 deformation origins per class.",
        "",
        "## Class Coverage",
        "",
        "| Class | Registered | Membership share | Eligible | Species | Deformations | Status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for wall_class, row in census["class_coverage"].items():
        lines.append(
            f"| {wall_class} {row['name']} | {row['registered_records']} | "
            f"{row['membership_share']:.1%} | {row['eligible_records']} | {row['unique_eligible_species']} | "
            f"{row['unique_eligible_deformations']} | **{row['coverage_status']}** |"
        )

    lines.extend(
        [
            "",
            "## Species Prevalence",
            "",
            "This retains the original 15-species denominator and does not count repeated records as new species.",
            "",
            "| Class | Species count | Prevalence |",
            "|---|---:|---:|",
        ]
    )
    for wall_class, row in census["species_prevalence"].items():
        lines.append(
            f"| {wall_class} {row['name']} | {row['count']} | {row['density']:.1%} |"
        )

    lines.extend(
        [
            "",
            "## Coverage Gaps",
            "",
        ]
    )
    gaps = [
        (wall_class, row)
        for wall_class, row in census["class_coverage"].items()
        if row["coverage_status"] == "gap"
    ]
    if not gaps:
        lines.append("All classes meet the first-pass coverage target.")
    else:
        for wall_class, row in gaps:
            failed = [name for name, passed in row["target_checks"].items() if not passed]
            lines.append(f"- **{wall_class} {row['name']}**: missing {', '.join(failed)} coverage.")

    lines.extend(
        [
            "",
            "## Record Inventory",
            "",
            "| Record | Classes | Species | Deformation | Eligible | Evidence |",
            "|---|---|---|---|:---:|---|",
        ]
    )
    for item in census["records"]:
        eligible = "yes" if item["eligible"] else "no"
        lines.append(
            f"| `{item['record_id']}` | {','.join(item['classes'])} | {item['species']} | "
            f"{item['deformation_origin']} | {eligible} | `{item['evidence']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def print_report(census: dict) -> None:
    print("Paper XI wall-record coverage census")
    print(f"  records: {census['record_count']}")
    print(f"  eligible: {census['eligible_record_count']}")
    print(f"  class memberships: {census['class_membership_count']}")
    print()
    print(f"  {'Class':<6s} {'Registered':>10s} {'Eligible':>9s} {'Species':>8s} {'Deform':>8s}  Status")
    for wall_class, row in census["class_coverage"].items():
        print(
            f"  {wall_class + ' ' + row['name']:<28s} "
            f"{row['registered_records']:>10d} {row['eligible_records']:>9d} "
            f"{row['unique_eligible_species']:>8d} "
            f"{row['unique_eligible_deformations']:>8d}  {row['coverage_status']}"
        )


def verify_paper_table(census: dict) -> None:
    paper = PAPER_PATH.read_text(encoding="utf-8")
    missing = []
    for wall_class, row in census["class_coverage"].items():
        expected = (
            f"| {wall_class} {row['name'].lower()} | {row['registered_records']} | "
            f"{row['eligible_records']} | {row['unique_eligible_species']} | "
            f"{row['unique_eligible_deformations']} | {row['coverage_status']} |"
        )
        if expected not in paper:
            missing.append(expected)
    if missing:
        raise RuntimeError(
            "Paper XI wall-record coverage table is out of sync:\n"
            + "\n".join(missing)
        )


def main() -> None:
    census = compute_census()
    verify_paper_table(census)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "wall_record_census.json"
    md_path = RESULTS_DIR / "wall_record_census.md"
    json_path.write_text(json.dumps(census, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown_report(census), encoding="utf-8")
    print_report(census)
    print(f"PASS {PAPER_PATH} contains the generated class-coverage rows")
    print()
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
