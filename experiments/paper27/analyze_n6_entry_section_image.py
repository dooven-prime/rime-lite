#!/usr/bin/env python3
"""Decompose the indexed image of the fixed-n=6 activated Entry section.

The input Entry sweep has already selected one activated rank-four checkpoint
per synchronizing rooted binary defect.  This producer classifies only those
selected endpoints.  In particular, it does not promote a universal
checkpoint predicate, import the historical Route-F envelope, or infer an
edge type from a deterministic best-edge tie break: Type-I and Type-II
existence are read separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_n6_low_rank_obstruction_peeling import _digest

ROOT = Path(__file__).resolve().parents[2]
ENTRY_SCHEMA = "single-defect-n6-rank4-activated-entry-exhaustiveness-v1"
OUTPUT_SCHEMA = "single-defect-n6-entry-section-image-v1"

BALANCED = "BALANCED_LEMMA_A"
TYPE_I_OUTSIDE_G4 = "EASY_UNBALANCED_TYPE_I_OUTSIDE_G4"
TYPE_I_OPEN_WEDGE = "EASY_UNBALANCED_TYPE_I_G4_OPEN_WEDGE"
TYPE_I_CLOSED_TRIANGLE = "EASY_UNBALANCED_TYPE_I_G4_CLOSED_TRIANGLE"
RESIDUAL_TYPE_II = "RESIDUAL_UNBALANCED_TYPE_II"

EXPECTED_RESIDUAL_FORMS = {
    "d102503__H0_x5_y2_z1",
    "d403205__H0_x2_y5_z4",
}


def _load(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8", newline="\n"))
    if payload.get("schema") != schema:
        raise AssertionError(f"unexpected input schema: {path}")
    return payload


def _intrinsic_form_label(defect: str, labels: list[int]) -> str:
    if len(labels) != 4:
        raise AssertionError("open-wedge source lost its Hxyz labels")
    h, x, y, z = (int(value) for value in labels)
    return f"d{defect}__H{h}_x{x}_y{y}_z{z}"


def _stratum(choice: dict[str, Any]) -> str:
    partition = tuple(int(value) for value in choice["partition"])
    type_i = int(choice["local_type_i_descent_count"])
    type_ii = int(choice["local_type_ii_descent_count"])
    if partition == (2, 2, 1, 1):
        return BALANCED
    if partition != (3, 1, 1, 1):
        raise AssertionError("selected section left the two rank-four partitions")
    if type_i:
        if not choice["G4"]:
            return TYPE_I_OUTSIDE_G4
        incidence = choice["G4_incidence"]
        if incidence == "OPEN_WEDGE":
            return TYPE_I_OPEN_WEDGE
        if incidence == "CLOSED_TRIANGLE":
            return TYPE_I_CLOSED_TRIANGLE
        raise AssertionError("G4 Type-I endpoint lost its incidence type")
    if type_ii and choice["G4_incidence"] == "OPEN_WEDGE":
        return RESIDUAL_TYPE_II
    raise AssertionError("selected unbalanced endpoint has no declared stratum")


def analyze(entry_path: Path) -> dict[str, Any]:
    entry = _load(entry_path, ENTRY_SCHEMA)
    if not entry["scope"]["complete_scope"]:
        raise AssertionError("Entry input is not the complete rooted n=6 sweep")

    counts = Counter()
    selected_rows = []
    residual_rows = []
    for action in entry["synchronizing_action_rows"]:
        defect = str(action["defect"])
        audit = action["entry_choice_audit"]
        choice = audit["section_choice"]
        if not choice["has_local_descent"]:
            raise AssertionError("Entry section selected a non-descending endpoint")
        if bool(choice["local_type_i_descent_count"]) != (
            choice["best_local_type_i_descent"] is not None
        ):
            raise AssertionError("Type-I existence and receipt disagree")
        if bool(choice["local_type_ii_descent_count"]) != (
            choice["best_local_type_ii_descent"] is not None
        ):
            raise AssertionError("Type-II existence and receipt disagree")

        stratum = _stratum(choice)
        counts["selected_section_actions"] += 1
        counts[f"stratum:{stratum}"] += 1
        if choice["local_type_i_descent_count"]:
            counts["selected_section_with_type_i"] += 1
        else:
            counts["selected_section_type_ii_only"] += 1
        partition = tuple(int(value) for value in choice["partition"])
        counts[
            "balanced_section_endpoints"
            if partition == (2, 2, 1, 1)
            else "unbalanced_section_endpoints"
        ] += 1
        if partition == (2, 2, 1, 1):
            counts[
                "balanced_with_type_i"
                if choice["local_type_i_descent_count"]
                else "balanced_type_ii_only"
            ] += 1
        if partition == (3, 1, 1, 1) and choice["local_type_i_descent_count"]:
            counts["easy_unbalanced_type_i"] += 1

        basis = choice["activated_basis"]
        row = {
            "defect": defect,
            "selector_case": audit["selector_case"],
            "checkpoint": choice["checkpoint"],
            "partition": choice["partition"],
            "entry_edge": choice["entry_edge"],
            "activated_basis_sha256": _digest(basis),
            "stratum": stratum,
            "local_type_i_descent_count": int(choice["local_type_i_descent_count"]),
            "local_type_ii_descent_count": int(choice["local_type_ii_descent_count"]),
            "local_descent_receipt": (
                choice["best_local_type_i_descent"]
                if choice["best_local_type_i_descent"] is not None
                else choice["best_local_type_ii_descent"]
            ),
            "G4": bool(choice["G4"]),
            "G4_incidence": choice["G4_incidence"],
            "G4_labels_Hxyz": choice["G4_labels_Hxyz"],
        }

        if stratum == RESIDUAL_TYPE_II:
            labels = [int(value) for value in choice["G4_labels_Hxyz"]]
            label = _intrinsic_form_label(defect, labels)
            residual = {
                **row,
                "activated_basis": basis,
                "intrinsic_source_form": label,
            }
            residual_rows.append(residual)
            row["intrinsic_source_form"] = label
        selected_rows.append(row)

    residual_forms = {row["intrinsic_source_form"] for row in residual_rows}
    if residual_forms != EXPECTED_RESIDUAL_FORMS:
        raise AssertionError("selected section residual form closure drift")
    residual_actions = {row["defect"] for row in residual_rows}
    counts["residual_unbalanced_type_ii"] = len(residual_rows)
    counts["residual_action_types"] = len(residual_actions)
    counts["residual_intrinsic_source_forms"] = len(residual_forms)

    return {
        "schema": OUTPUT_SCHEMA,
        "scope": {
            "n": 6,
            "domain": "the indexed image of ROOTED_N6_ENTRY_SECTION_V1",
            "section_semantics": (
                "one source-addressed activated rank-four checkpoint is "
                "chosen for each synchronizing rooted binary defect"
            ),
            "easy_semantics": (
                "an explicit endpoint-normalized local Type-I certificate "
                "lands in exact P_1/P_2/P_3"
            ),
            "residual_semantics": (
                "the selected unbalanced endpoint has no local Type-I "
                "certificate but has a local Type-II certificate"
            ),
        },
        "inputs": {
            str(entry_path.relative_to(ROOT).as_posix()): hashlib.sha256(
                entry_path.read_bytes()
            ).hexdigest(),
        },
        "counts": dict(sorted(counts.items())),
        "decomposition": {
            "statement": (
                "the indexed graph of sigma_6 is the disjoint union of 995 "
                "balanced, 707 easy unbalanced Type-I, and 2 residual "
                "unbalanced Type-II section instances"
            ),
            "balanced_stratum": BALANCED,
            "easy_unbalanced_strata": [
                TYPE_I_OUTSIDE_G4,
                TYPE_I_OPEN_WEDGE,
                TYPE_I_CLOSED_TRIANGLE,
            ],
            "residual_stratum": RESIDUAL_TYPE_II,
        },
        "selected_section_rows": selected_rows,
        "residual_rows": residual_rows,
        "theorem_boundary": {
            "fixed_n6_section_image_decomposition_holds": True,
            "selected_section_has_local_descent": True,
            "interpretation": (
                "activation supplies semantic legitimacy; the intrinsic "
                "section choice supplies the descending representative"
            ),
        },
        "nonclaims": [
            "This is a complete fixed-n=6 rooted computation, not an all-n theorem.",
            "The historical four-action/eight-form Route-F surface is not an input to this paper-owned section-image artifact.",
            "The artifact records Type-I existence and does not identify a shortest representative with a pair-level existential witness.",
            "The generic 1703-action Entry complement still has a finite symbolic receipt closure rather than a non-enumerative proof.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entry",
        type=Path,
        default=ROOT / "experiments/paper27/results/"
        "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(args.entry)
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("analyze_n6_low_rank_obstruction_peeling.py"),
    )
    payload["sources"] = {
        str(path.relative_to(ROOT).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in dependencies
    }
    payload["content_sha256"] = _digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "counts": payload["counts"],
                "residual_forms": sorted(EXPECTED_RESIDUAL_FORMS),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
