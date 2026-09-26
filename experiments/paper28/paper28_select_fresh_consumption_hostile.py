#!/usr/bin/env python3
"""Select a fresh-consuming length-three hostile carrier without success data."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_select_second_rank5_return_candidate import (
    FORBIDDEN_OUTPUT_FIELDS,
    INPUT_SCHEMA,
    N,
    _context_projection,
    _future_free_signature,
    _hamming_distance,
)
from paper28_select_third_rank5_return_candidate import (
    SCHEMA as THIRD_SELECTION_SCHEMA,
)

SCHEMA = "paper28-fresh-consumption-hostile-selection-v1"
RECEIPT_SCHEMA = "paper28-fresh-consumption-hostile-selection-receipt-v1"
RULE_SCHEMA = "paper28-remaining-anatomy-feasibility-audit-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    HERE / "results" / "single_defect_n7_inherited_section_pilot_complete_v1.json"
)
DEFAULT_RULE = HERE / "results" / "paper28_remaining_anatomy_feasibility_audit_v1.json"
DEFAULT_REFERENCE = (
    HERE / "results" / "paper28_third_rank5_return_candidate_selection_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_fresh_consumption_hostile_selection_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_select_third_rank5_return_candidate.py",
    "section_return_core.py",
    "single_defect_transport.py",
    "validation/validate_paper28_fresh_consumption_hostile.py",
)
STRUCTURAL_DISTANCE_FIELDS = (
    "rank5_partition",
    "rank4_partition",
    "sigma5_surplus",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)
PREFERRED_FUSION = [1, 2]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _signature_key(signature: Mapping[str, Any]) -> str:
    return json.dumps(
        signature,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def _placement(row: Mapping[str, Any]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (
        tuple(int(value) for value in row["rank5_context"]["mass"]),
        tuple(int(value) for value in row["rank4_context"]["mass"]),
    )


def _placement_json(
    placement: tuple[tuple[int, ...], tuple[int, ...]],
) -> dict[str, list[int]]:
    return {
        "rank5_mass": list(placement[0]),
        "rank4_mass": list(placement[1]),
    }


def _placement_distance(
    left: tuple[tuple[int, ...], tuple[int, ...]],
    right: tuple[tuple[int, ...], tuple[int, ...]],
) -> int:
    return sum(a != b for a, b in zip(left[0], right[0], strict=True)) + sum(
        a != b for a, b in zip(left[1], right[1], strict=True)
    )


def _minimum_placement_distance(
    candidate: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
    reference: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
) -> tuple[int, list[dict[str, Any]]]:
    rows = [
        (_placement_distance(left, right), left, right)
        for left in candidate
        for right in reference
    ]
    minimum = min(row[0] for row in rows)
    witnesses = [
        {
            "candidate": _placement_json(left),
            "reference": _placement_json(right),
        }
        for distance, left, right in rows
        if distance == minimum
    ]
    witnesses.sort(
        key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))
    )
    return minimum, witnesses


def _assert_rule(rule: Mapping[str, Any]) -> None:
    if rule.get("schema") != RULE_SCHEMA:
        raise AssertionError("unexpected P28.5m rule schema")
    gate = rule["next_stage_gate"]
    if gate["status"] != "HOSTILE_CLASS_FEASIBLE_CARRIER_NOT_SELECTED":
        raise AssertionError("P28.5m has not opened the fresh-consumption class")
    if gate["hard_constraint"] != "fusion_contains_inherited_fresh == true":
        raise AssertionError("P28.5m fresh-consumption hard constraint drift")
    if gate["preferred_control"] != "sigma5_length == 3":
        raise AssertionError("P28.5m length control drift")
    if gate["fourth_candidate_selected"]:
        raise AssertionError("P28.5m unexpectedly preselected a carrier")


def build_payload(
    input_path: Path,
    rule_path: Path,
    reference_path: Path,
) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected inherited pilot schema")
    if len(source["rows"]) != 15120:
        raise AssertionError("P28.5n requires the complete rooted scope")

    rule = json.loads(rule_path.read_text(encoding="ascii"))
    _assert_rule(rule)
    reference = _load(reference_path)
    if reference.get("schema") != THIRD_SELECTION_SCHEMA:
        raise AssertionError("unexpected third-chain reference schema")
    reference_candidate = reference["candidate"]
    reference_signature = reference_candidate["selected_signature"]
    reference_placements = sorted(
        {_placement(row) for row in reference_candidate["contexts"]}
    )
    if len(reference_placements) != 18:
        raise AssertionError("third-chain action-relative placement spectrum drift")

    groups: dict[str, list[tuple[Mapping[str, Any], dict[str, Any]]]] = defaultdict(
        list
    )
    for row in source["rows"]:
        signature = _future_free_signature(row)
        groups[_signature_key(signature)].append((row, signature))
    if len(groups) != 562:
        raise AssertionError("future-free carrier no longer has 562 cells")

    fresh_length_three = []
    for members in groups.values():
        signature = members[0][1]
        if not signature["fusion_contains_inherited_fresh"]:
            continue
        if int(signature["sigma5_length"]) != 3:
            continue
        fresh_length_three.append(members)
    if len(fresh_length_three) != 74:
        raise AssertionError("P28.5m 74-cell hostile class drift")

    preferred = [
        members
        for members in fresh_length_three
        if members[0][1]["fusion_parent_sizes"] == PREFERRED_FUSION
    ]
    if len(preferred) != 41:
        raise AssertionError("P28.5m 41-cell 1+2 preference drift")
    if sum(len(members) for members in preferred) != 672:
        raise AssertionError("P28.5m 1+2 preferred context count drift")

    candidate_rows = []
    for members in preferred:
        signature = members[0][1]
        placements = sorted({_placement(row) for row, _ in members})
        placement_distance, placement_witnesses = _minimum_placement_distance(
            placements, reference_placements
        )
        candidate_rows.append(
            {
                "signature": dict(signature),
                "context_count": len(members),
                "action_relative_placement_count": len(placements),
                "structural_distance": _hamming_distance(
                    signature,
                    reference_signature,
                    STRUCTURAL_DISTANCE_FIELDS,
                ),
                "minimum_action_relative_placement_distance": placement_distance,
                "minimum_placement_witnesses": placement_witnesses,
            }
        )
    candidate_rows.sort(key=lambda row: _signature_key(row["signature"]))

    minimum_structural = min(row["structural_distance"] for row in candidate_rows)
    primary = [
        row
        for row in candidate_rows
        if row["structural_distance"] == minimum_structural
    ]
    minimum_placement = min(
        row["minimum_action_relative_placement_distance"] for row in primary
    )
    finalists = [
        row
        for row in primary
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
    candidate_projection = {
        "name": "fresh-consuming length-three fourth pre-section carrier",
        "recursive_authority": "NONE",
        "selection_status": status,
        "selection_rule": (
            "require inherited-fresh consumption and length three, prefer 1+2, "
            "minimize structural Hamming distance to the third closed chain, "
            "retain the complete primary tie, then minimize action-relative "
            "rank-five/rank-four mass-placement Hamming distance"
        ),
        "hard_constraints": {
            "fusion_contains_inherited_fresh": True,
            "sigma5_length": 3,
        },
        "preferred_fusion": PREFERRED_FUSION,
        "structural_distance_fields": list(STRUCTURAL_DISTANCE_FIELDS),
        "placement_distance_definition": (
            "minimum coordinate Hamming distance on the concatenated rooted "
            "rank-five and rank-four mass placements"
        ),
        "eligible_signature_cell_count": len(fresh_length_three),
        "preferred_signature_cell_count": len(preferred),
        "preferred_context_count": sum(len(members) for members in preferred),
        "minimum_structural_distance": minimum_structural,
        "primary_minimizer_count": len(primary),
        "primary_minimizers": primary,
        "minimum_action_relative_placement_distance": minimum_placement,
        "finalist_count": len(finalists),
        "finalists": finalists,
        "context_count": len(contexts),
        "contexts": contexts,
    }
    encoded = json.dumps(
        candidate_projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_OUTPUT_FIELDS:
        if field in encoded:
            raise AssertionError(
                f"downstream-success field leaked into selector: {field}"
            )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "winner_selected": False,
            "nonclaim": (
                "this artifact freezes only a source-local hostile carrier or "
                "complete finalist tie; it does not evaluate a return"
            ),
        },
        "phase_order": [
            "bind_P28_5m_feasibility_rule",
            "project_complete_inherited_rows_to_562_future_free_cells",
            "require_fresh_consumption_and_length_three",
            "prefer_1_plus_2_fusion",
            "minimize_structural_distance_to_third_closed_chain",
            "retain_complete_primary_tie",
            "minimize_action_relative_placement_distance",
            "retain_complete_final_tie_or_unique_minimizer",
            "freeze_candidate_payload_before_any_return_evaluation",
        ],
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "schema": source["schema"],
                "sha256": _sha256(input_path),
                "rows_digest": source["rows_digest"],
            },
            "P28_5m_rule": {
                "name": rule_path.name,
                "schema": rule["schema"],
                "sha256": _sha256(rule_path),
                "content_sha256": rule["content_sha256"],
            },
            "third_closed_chain_reference": {
                "name": reference_path.name,
                "schema": reference["schema"],
                "sha256": _sha256(reference_path),
                "content_sha256": reference["content_sha256"],
                "candidate_payload_sha256": reference["candidate_payload_sha256"],
            },
        },
        "selection_audit": {
            "future_free_signature_cell_count": len(groups),
            "fresh_consumed_length_three_cell_count": len(fresh_length_three),
            "fresh_consumed_length_three_context_count": sum(
                len(members) for members in fresh_length_three
            ),
            "preferred_1_plus_2_cell_count": len(preferred),
            "preferred_1_plus_2_context_count": sum(
                len(members) for members in preferred
            ),
            "structural_distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    Counter(
                        row["structural_distance"] for row in candidate_rows
                    ).items()
                )
            },
            "primary_placement_distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    Counter(
                        row["minimum_action_relative_placement_distance"]
                        for row in primary
                    ).items()
                )
            },
        },
        "candidate": candidate_projection,
        "next_phase_gate": {
            "allowed_next": (
                "if the finalist is unique, construct and freeze its rank-four "
                "menu/exact-lift relation before any independent evaluator"
                if len(finalists) == 1
                else "define a new source-local secondary rule without success data"
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
                "inside the 41-cell 1+2 fresh-consuming length-three class"
            ),
            "not_claimed": [
                "rank-four or rank-five section authority",
                "return success",
                "maximality or canonicity",
                "coverage of the full inherited universe",
                "an all-rank return theorem",
            ],
        },
    }
    payload["candidate_payload_sha256"] = _digest(candidate_projection)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    input_path: Path,
    rule_path: Path,
    reference_path: Path,
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "SOURCE_LOCAL_HOSTILE_SELECTION_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "candidate_payload_sha256": payload["candidate_payload_sha256"],
        },
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "sha256": _sha256(input_path),
                "rows_digest": payload["inputs"]["inherited_pilot"]["rows_digest"],
            },
            "P28_5m_rule": {
                "name": rule_path.name,
                "sha256": _sha256(rule_path),
                "content_sha256": payload["inputs"]["P28_5m_rule"]["content_sha256"],
            },
            "third_closed_chain_reference": {
                "name": reference_path.name,
                "sha256": _sha256(reference_path),
                "candidate_payload_sha256": payload["inputs"][
                    "third_closed_chain_reference"
                ]["candidate_payload_sha256"],
            },
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
    parser.add_argument("--rule", type=Path, default=DEFAULT_RULE)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.input, args.rule, args.reference)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            input_path=args.input,
            rule_path=args.rule,
            reference_path=args.reference,
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
                "primary_minimizers": candidate["primary_minimizer_count"],
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
