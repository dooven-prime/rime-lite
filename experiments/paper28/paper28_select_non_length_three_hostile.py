#!/usr/bin/env python3
"""Select a non-length-three hostile carrier without candidate success data."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_select_fresh_consumption_hostile import (
    _digest,
    _load,
    _minimum_placement_distance,
    _placement,
    _sha256,
    _signature_key,
    _write,
    _write_receipt,
    default_receipt_path,
)
from paper28_select_second_rank5_return_candidate import (
    FORBIDDEN_OUTPUT_FIELDS,
    INPUT_SCHEMA,
    N,
    _context_projection,
    _future_free_signature,
    _hamming_distance,
)

SCHEMA = "paper28-non-length-three-hostile-selection-v1"
RECEIPT_SCHEMA = "paper28-non-length-three-hostile-selection-receipt-v1"
FEASIBILITY_SCHEMA = "paper28-remaining-anatomy-feasibility-audit-v1"
REFERENCE_SELECTION_SCHEMA = "paper28-fresh-consumption-hostile-selection-v1"
REFERENCE_RETURN_SCHEMA = "paper28-fourth-rank5-section-return-evaluation-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    HERE / "results" / "single_defect_n7_inherited_section_pilot_complete_v1.json"
)
DEFAULT_FEASIBILITY = (
    HERE / "results" / "paper28_remaining_anatomy_feasibility_audit_v1.json"
)
DEFAULT_REFERENCE_SELECTION = (
    HERE / "results" / "paper28_fresh_consumption_hostile_selection_v1.json.gz"
)
DEFAULT_REFERENCE_RETURN = (
    HERE / "results" / "paper28_fourth_rank5_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_non_length_three_hostile_selection_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_select_non_length_three_hostile.py",
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_select_third_rank5_return_candidate.py",
    "section_return_core.py",
    "single_defect_transport.py",
    "validation/validate_paper28_non_length_three_hostile.py",
)
PREFERRED_FUSION = [1, 2]
GEOMETRY_DISTANCE_FIELDS = (
    "rank5_partition",
    "rank4_partition",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)


def _gross_gain(signature: Mapping[str, Any]) -> int:
    return int(signature["sigma5_length"]) + int(signature["sigma5_surplus"])


def _assert_feasibility(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != FEASIBILITY_SCHEMA:
        raise AssertionError("unexpected P28.5m feasibility schema")
    rows = {
        row["quadrant"]: (row["signature_cell_count"], row["context_count"])
        for row in payload["quadrants"]
    }
    if rows.get("length_not_3__fresh_consumed") != (142, 5032):
        raise AssertionError("P28.5m non-length-three consumed quadrant drift")
    forbidden = payload["next_stage_gate"]["forbidden_selection_inputs"]
    if "Good_4" not in forbidden or "Good_5" not in forbidden:
        raise AssertionError("P28.5m future-free gate drift")


def _reference_signature(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if payload.get("schema") != REFERENCE_SELECTION_SCHEMA:
        raise AssertionError("unexpected fourth-chain selection schema")
    candidate = payload["candidate"]
    if candidate["finalist_count"] != 1:
        raise AssertionError("fourth-chain reference is not unique")
    return candidate["finalists"][0]["signature"]


def _assert_reference_return(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != REFERENCE_RETURN_SCHEMA:
        raise AssertionError("unexpected fourth-chain return schema")
    authority = payload["certified_source_section"]
    if (
        authority["ordinary_return_authority_status"]
        != "GRANTED_BY_FIXED_SCOPE_GOOD5_EVALUATION"
    ):
        raise AssertionError("fourth-chain reference lacks ordinary authority")
    if authority["fresh_consumption_claim_status"] != "PROVED_ON_FIXED_SCOPE":
        raise AssertionError("fourth-chain reference lacks hostile authority")


def build_payload(
    input_path: Path,
    feasibility_path: Path,
    reference_selection_path: Path,
    reference_return_path: Path,
) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != INPUT_SCHEMA or len(source["rows"]) != 15120:
        raise AssertionError("P28.5s requires the complete inherited pilot")

    feasibility = json.loads(feasibility_path.read_text(encoding="ascii"))
    _assert_feasibility(feasibility)
    reference_selection = _load(reference_selection_path)
    reference_signature = _reference_signature(reference_selection)
    reference_return = _load(reference_return_path)
    _assert_reference_return(reference_return)
    reference_contexts = reference_selection["candidate"]["contexts"]
    reference_placements = sorted({_placement(row) for row in reference_contexts})
    reference_gain = _gross_gain(reference_signature)

    groups: dict[str, list[tuple[Mapping[str, Any], dict[str, Any]]]] = defaultdict(
        list
    )
    for row in source["rows"]:
        signature = _future_free_signature(row)
        groups[_signature_key(signature)].append((row, signature))
    if len(groups) != 562:
        raise AssertionError("future-free carrier no longer has 562 cells")

    eligible = []
    for members in groups.values():
        signature = members[0][1]
        if not signature["fusion_contains_inherited_fresh"]:
            continue
        if int(signature["sigma5_length"]) == 3:
            continue
        eligible.append(members)
    if len(eligible) != 142 or sum(map(len, eligible)) != 5032:
        raise AssertionError("non-length-three consumed class drift")

    preferred = [
        members
        for members in eligible
        if members[0][1]["fusion_parent_sizes"] == PREFERRED_FUSION
    ]
    if not preferred:
        raise AssertionError("non-length-three class has no 1+2 family")

    rows = []
    for members in preferred:
        signature = members[0][1]
        placements = sorted({_placement(row) for row, _ in members})
        placement_distance, placement_witnesses = _minimum_placement_distance(
            placements, reference_placements
        )
        gross_gain = _gross_gain(signature)
        rows.append(
            {
                "signature": dict(signature),
                "context_count": len(members),
                "action_relative_placement_count": len(placements),
                "geometry_distance": _hamming_distance(
                    signature,
                    reference_signature,
                    GEOMETRY_DISTANCE_FIELDS,
                ),
                "gross_maturity_gain": gross_gain,
                "gross_gain_distance": abs(gross_gain - reference_gain),
                "minimum_action_relative_placement_distance": placement_distance,
                "minimum_placement_witnesses": placement_witnesses,
            }
        )
    rows.sort(key=lambda row: _signature_key(row["signature"]))

    minimum_geometry = min(row["geometry_distance"] for row in rows)
    geometry_minimizers = [
        row for row in rows if row["geometry_distance"] == minimum_geometry
    ]
    minimum_gain_distance = min(
        row["gross_gain_distance"] for row in geometry_minimizers
    )
    accounting_minimizers = [
        row
        for row in geometry_minimizers
        if row["gross_gain_distance"] == minimum_gain_distance
    ]
    minimum_placement = min(
        row["minimum_action_relative_placement_distance"]
        for row in accounting_minimizers
    )
    finalists = [
        row
        for row in accounting_minimizers
        if row["minimum_action_relative_placement_distance"] == minimum_placement
    ]
    finalist_keys = {_signature_key(row["signature"]) for row in finalists}
    selected_members = [
        member
        for members in preferred
        if _signature_key(members[0][1]) in finalist_keys
        for member in members
    ]
    contexts = sorted(
        (_context_projection(row, signature) for row, signature in selected_members),
        key=lambda row: (row["defect"], row["index"]),
    )
    status = (
        "UNIQUE_SOURCE_LOCAL_MINIMIZER"
        if len(finalists) == 1
        else "TIE_RETAINED_NEEDS_NEW_SOURCE_LOCAL_RULE"
    )

    candidate = {
        "name": "non-length-three fifth pre-section carrier",
        "recursive_authority": "NONE",
        "selection_status": status,
        "selection_rule": (
            "require inherited-fresh consumption and length not equal to three; "
            "prefer 1+2 fusion; minimize partition/kernel/offset geometry "
            "distance to the fourth closed chain; then minimize absolute gross "
            "maturity-gain distance using G=length+surplus; then minimize "
            "action-relative rank-five/rank-four placement distance"
        ),
        "hard_constraints": {
            "fusion_contains_inherited_fresh": True,
            "sigma5_length_not_equal": 3,
        },
        "preferred_fusion": PREFERRED_FUSION,
        "geometry_distance_fields": list(GEOMETRY_DISTANCE_FIELDS),
        "accounting_control": {
            "definition": "gross_maturity_gain = sigma5_length + sigma5_surplus",
            "reference_value": reference_gain,
            "surplus_compared_independently": False,
        },
        "placement_distance_definition": (
            "minimum coordinate Hamming distance on the concatenated rooted "
            "rank-five and rank-four mass placements"
        ),
        "eligible_signature_cell_count": len(eligible),
        "eligible_context_count": sum(map(len, eligible)),
        "preferred_signature_cell_count": len(preferred),
        "preferred_context_count": sum(map(len, preferred)),
        "minimum_geometry_distance": minimum_geometry,
        "geometry_minimizer_count": len(geometry_minimizers),
        "geometry_minimizers": geometry_minimizers,
        "minimum_gross_gain_distance": minimum_gain_distance,
        "accounting_minimizer_count": len(accounting_minimizers),
        "accounting_minimizers": accounting_minimizers,
        "minimum_action_relative_placement_distance": minimum_placement,
        "finalist_count": len(finalists),
        "finalists": finalists,
        "context_count": len(contexts),
        "contexts": contexts,
    }
    encoded = json.dumps(
        candidate, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).lower()
    for field in FORBIDDEN_OUTPUT_FIELDS:
        if field in encoded:
            raise AssertionError(f"downstream-success field leaked: {field}")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "winner_selected": False,
            "nonclaim": (
                "this artifact freezes only a source-local non-length-three "
                "carrier or complete finalist tie"
            ),
        },
        "phase_order": [
            "bind_complete_P28_5m_feasibility_partition",
            "bind_closed_fourth_chain_as_geometry_reference",
            "require_fresh_consumption_and_length_not_equal_to_three",
            "prefer_1_plus_2_fusion",
            "minimize_partition_kernel_offset_geometry_distance",
            "minimize_gross_gain_distance_without_independent_surplus_control",
            "minimize_action_relative_placement_distance",
            "freeze_complete_finalist_tie_or_unique_minimizer",
            "defer_Good4_Good5_and_Good5_non_length_three",
        ],
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "schema": source["schema"],
                "sha256": _sha256(input_path),
                "rows_digest": source["rows_digest"],
            },
            "P28_5m_feasibility": {
                "name": feasibility_path.name,
                "schema": feasibility["schema"],
                "sha256": _sha256(feasibility_path),
                "content_sha256": feasibility["content_sha256"],
            },
            "fourth_chain_selection": {
                "name": reference_selection_path.name,
                "schema": reference_selection["schema"],
                "sha256": _sha256(reference_selection_path),
                "content_sha256": reference_selection["content_sha256"],
            },
            "fourth_chain_return": {
                "name": reference_return_path.name,
                "schema": reference_return["schema"],
                "sha256": _sha256(reference_return_path),
                "content_sha256": reference_return["content_sha256"],
            },
        },
        "selection_audit": {
            "future_free_signature_cell_count": len(groups),
            "non_length_three_fresh_consumed_cell_count": len(eligible),
            "non_length_three_fresh_consumed_context_count": sum(map(len, eligible)),
            "preferred_1_plus_2_cell_count": len(preferred),
            "preferred_1_plus_2_context_count": sum(map(len, preferred)),
            "preferred_length_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        int(members[0][1]["sigma5_length"]) for members in preferred
                    ).items()
                )
            },
            "preferred_gross_gain_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(_gross_gain(members[0][1]) for members in preferred).items()
                )
            },
            "geometry_distance_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(row["geometry_distance"] for row in rows).items()
                )
            },
            "geometry_minimizer_gross_gain_distance_distribution": {
                str(value): count
                for value, count in sorted(
                    Counter(
                        row["gross_gain_distance"] for row in geometry_minimizers
                    ).items()
                )
            },
        },
        "candidate": candidate,
        "next_phase_gate": {
            "allowed_next": (
                "if unique, freeze rank-four menu/exact lifts; later rank-five "
                "freeze must report selected corridor length against the full "
                "exact-fiber corridor-length spectrum before independent "
                "Good_5 and Good_5^non3 evaluation"
                if len(finalists) == 1
                else "define a new source-local secondary rule without success data"
            ),
            "preregistered_hostile_predicate": (
                "Good_5^non3(C,m) iff an exact lift reaches the certified lower "
                "section and has corridor length not equal to three"
            ),
            "forbidden_now": [
                "rank-four or rank-five return evaluation",
                "exact low-rank base membership",
                "lower-section membership",
                "winner-selected channel menus",
            ],
        },
        "claim_boundary": {
            "proved": (
                "the declared source-local minimizer or complete finalist tie "
                "inside the 1+2 fresh-consuming non-length-three class"
            ),
            "not_claimed": [
                "rank-four or rank-five section authority",
                "ordinary or non-length-three return success",
                "maximality or canonicity",
                "coverage of the full inherited universe",
                "an all-rank return theorem",
            ],
        },
    }
    payload["candidate_payload_sha256"] = _digest(candidate)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    input_path: Path,
    feasibility_path: Path,
    reference_selection_path: Path,
    reference_return_path: Path,
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "SOURCE_LOCAL_NON_LENGTH_THREE_SELECTION_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "candidate_payload_sha256": payload["candidate_payload_sha256"],
        },
        "inputs": {
            key: {
                "name": row["name"],
                "sha256": row["sha256"],
                **(
                    {"content_sha256": row["content_sha256"]}
                    if "content_sha256" in row
                    else {"rows_digest": row["rows_digest"]}
                ),
            }
            for key, row in payload["inputs"].items()
        },
        "source_closure": [
            {
                "path": (HERE / relative).relative_to(repo_root).as_posix(),
                "sha256": _sha256(HERE / relative),
            }
            for relative in SOURCE_CLOSURE
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--feasibility", type=Path, default=DEFAULT_FEASIBILITY)
    parser.add_argument(
        "--reference-selection", type=Path, default=DEFAULT_REFERENCE_SELECTION
    )
    parser.add_argument(
        "--reference-return", type=Path, default=DEFAULT_REFERENCE_RETURN
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        args.input,
        args.feasibility,
        args.reference_selection,
        args.reference_return,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            input_path=args.input,
            feasibility_path=args.feasibility,
            reference_selection_path=args.reference_selection,
            reference_return_path=args.reference_return,
            output=args.out,
            payload=payload,
        ),
    )
    candidate = payload["candidate"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "selection_status": candidate["selection_status"],
                "eligible_cells": candidate["eligible_signature_cell_count"],
                "preferred_1_plus_2_cells": candidate["preferred_signature_cell_count"],
                "geometry_minimizers": candidate["geometry_minimizer_count"],
                "accounting_minimizers": candidate["accounting_minimizer_count"],
                "finalists": candidate["finalist_count"],
                "candidate_contexts": candidate["context_count"],
                "evaluation_status": "NOT_RUN",
                "section_authority": "NOT_GRANTED",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
