#!/usr/bin/env python3
"""Audit source-local feasibility of the two remaining P28.5 anatomies."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_select_second_rank5_return_candidate import (
    INPUT_SCHEMA,
    KEY_FIELDS,
    _future_free_signature,
)


SCHEMA = "paper28-remaining-anatomy-feasibility-audit-v1"
RECEIPT_SCHEMA = "paper28-remaining-anatomy-feasibility-audit-receipt-v1"
RULE_SCHEMA = "paper28-three-realization-invariant-audit-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "results" / "single_defect_n7_inherited_section_pilot_complete_v1.json"
DEFAULT_RULE = HERE / "results" / "paper28_three_realization_invariant_audit_v1.json"
DEFAULT_OUTPUT = HERE / "results" / "paper28_remaining_anatomy_feasibility_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_remaining_anatomy_feasibility_audit.py",
    "paper28_select_second_rank5_return_candidate.py",
    "section_return_core.py",
    "single_defect_transport.py",
    "validation/validate_paper28_remaining_anatomy_feasibility_audit.py",
)
FEATURE_FIELDS = (
    "family",
    "rank5_partition",
    "rank4_partition",
    "fusion_parent_sizes",
    "sigma5_length",
    "sigma5_surplus",
    "binary_kernel_mass_multiset",
    "cyclic_offsets_F4_to_kernel",
)


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


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="ascii",
        newline="\n",
    )


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.receipt.json")


def _signature_key(signature: Mapping[str, Any]) -> str:
    return json.dumps(
        signature,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def _value_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _distribution(
    cells: Sequence[Mapping[str, Any]], field: str
) -> list[dict[str, Any]]:
    cell_counts: Counter[str] = Counter()
    context_counts: Counter[str] = Counter()
    values: dict[str, Any] = {}
    for cell in cells:
        value = cell["signature"][field]
        key = _value_key(value)
        values[key] = value
        cell_counts[key] += 1
        context_counts[key] += int(cell["context_count"])
    return [
        {
            "value": values[key],
            "signature_cell_count": int(cell_counts[key]),
            "context_count": int(context_counts[key]),
        }
        for key in sorted(values)
    ]


def _quadrant_key(*, length_three: bool, fresh_consumed: bool) -> str:
    length = "length_3" if length_three else "length_not_3"
    fresh = "fresh_consumed" if fresh_consumed else "fresh_not_consumed"
    return f"{length}__{fresh}"


def _quadrant_row(
    *, key: str, cells: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "quadrant": key,
        "nonempty": bool(cells),
        "signature_cell_count": len(cells),
        "context_count": sum(int(cell["context_count"]) for cell in cells),
        "source_local_distributions": {
            field: _distribution(cells, field) for field in FEATURE_FIELDS
        },
    }


def build_payload(input_path: Path, rule_path: Path) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected inherited pilot schema")
    if len(source["rows"]) != 15120:
        raise AssertionError("feasibility audit requires the complete rooted scope")

    rule = json.loads(rule_path.read_text(encoding="ascii"))
    if rule.get("schema") != RULE_SCHEMA:
        raise AssertionError("unexpected P28.5l rule schema")
    remaining = rule["remaining_hostile_targets"]
    if remaining["fourth_candidate_status"] != "NOT_SELECTED":
        raise AssertionError("P28.5l unexpectedly selected a fourth carrier")
    expected_anatomy = {
        "successful rank-five length equals 3",
        "incoming distinguished packet is not consumed",
    }
    if set(remaining["common_unproved_anatomy"]) != expected_anatomy:
        raise AssertionError("P28.5l remaining-anatomy boundary drift")

    groups: dict[str, dict[str, Any]] = {}
    for row in source["rows"]:
        signature = _future_free_signature(row)
        key = _signature_key(signature)
        entry = groups.setdefault(
            key,
            {"signature": signature, "context_count": 0},
        )
        entry["context_count"] += 1
    if len(groups) != 562:
        raise AssertionError("future-free carrier no longer has 562 cells")

    quadrants: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in groups.values():
        signature = cell["signature"]
        key = _quadrant_key(
            length_three=int(signature["sigma5_length"]) == 3,
            fresh_consumed=bool(signature["fusion_contains_inherited_fresh"]),
        )
        quadrants[key].append(cell)

    ordered_keys = (
        "length_3__fresh_consumed",
        "length_3__fresh_not_consumed",
        "length_not_3__fresh_consumed",
        "length_not_3__fresh_not_consumed",
    )
    rows = [
        _quadrant_row(
            key=key,
            cells=sorted(
                quadrants.get(key, []),
                key=lambda cell: _signature_key(cell["signature"]),
            ),
        )
        for key in ordered_keys
    ]
    if sum(row["signature_cell_count"] for row in rows) != 562:
        raise AssertionError("quadrants do not partition signature cells")
    if sum(row["context_count"] for row in rows) != 15120:
        raise AssertionError("quadrants do not partition rooted contexts")

    fresh_consumed_contexts = sum(
        row["context_count"]
        for row in rows
        if row["quadrant"].endswith("fresh_consumed")
    )
    fresh_not_consumed_contexts = 15120 - fresh_consumed_contexts
    if [fresh_consumed_contexts, fresh_not_consumed_contexts] != [6256, 8864]:
        raise AssertionError("inherited fresh-participation checksum drift")

    by_key = {row["quadrant"]: row for row in rows}
    preferred = by_key["length_3__fresh_consumed"]
    preferred_feasible = bool(preferred["nonempty"])
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rooted_context_count": 15120,
            "future_free_signature_cell_count": 562,
            "new_oracle_evaluation": False,
            "good_or_success_field_read": False,
            "fourth_candidate_selected": False,
        },
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "schema": source["schema"],
                "sha256": _sha256(input_path),
                "rows_digest": source["rows_digest"],
            },
            "P28_5l_rule": {
                "name": rule_path.name,
                "schema": rule["schema"],
                "sha256": _sha256(rule_path),
                "content_sha256": rule["content_sha256"],
            },
        },
        "projection": {
            "key_fields": list(KEY_FIELDS),
            "quadrant_axes": {
                "length": ["sigma5_length == 3", "sigma5_length != 3"],
                "fresh_participation": [
                    "fusion_contains_inherited_fresh == true",
                    "fusion_contains_inherited_fresh == false",
                ],
            },
            "feature_distributions": list(FEATURE_FIELDS),
            "selection_or_success_fields_used": [],
        },
        "fresh_participation_checksum": {
            "consumed_context_count": fresh_consumed_contexts,
            "not_consumed_context_count": fresh_not_consumed_contexts,
        },
        "quadrants": rows,
        "derived_feasibility": {
            "length_3_fresh_consumed_nonempty": preferred_feasible,
            "length_3_fresh_consumed_signature_cell_count": preferred[
                "signature_cell_count"
            ],
            "length_3_fresh_consumed_context_count": preferred["context_count"],
            "recommended_next_attack": (
                "hold sigma5_length == 3 and require "
                "fusion_contains_inherited_fresh == true"
                if preferred_feasible
                else "attack sigma5_length != 3 before fresh participation"
            ),
        },
        "next_stage_gate": {
            "status": (
                "HOSTILE_CLASS_FEASIBLE_CARRIER_NOT_SELECTED"
                if preferred_feasible
                else "PREFERRED_HOSTILE_CLASS_EMPTY"
            ),
            "hard_constraint": "fusion_contains_inherited_fresh == true",
            "preferred_control": "sigma5_length == 3",
            "permitted_distance_fields": [
                "rank5_partition",
                "rank4_partition",
                "fusion_parent_sizes",
                "sigma5_surplus",
                "binary_kernel_mass_multiset",
                "cyclic_offsets_F4_to_kernel",
                "action_relative_mass_placement",
            ],
            "forbidden_selection_inputs": [
                "Good_4",
                "Good_5",
                "exact low-rank base membership",
                "lower-section membership",
                "winning or Bellman labels",
            ],
            "fourth_candidate_selected": False,
        },
        "claim_boundary": {
            "proved": (
                "the exact two-by-two source-local feasibility partition of "
                "the existing 562-cell fixed-n=7 carrier"
            ),
            "not_claimed": [
                "any quadrant has section authority",
                "the preferred hostile class has a successful return",
                "a fourth carrier has been selected",
                "length or fresh participation is all-rank structural",
                "an all-rank return theorem",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, input_path: Path, rule_path: Path, output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "SOURCE_LOCAL_FEASIBILITY_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            "inherited_pilot": {
                "name": input_path.name,
                "sha256": _sha256(input_path),
                "rows_digest": payload["inputs"]["inherited_pilot"]["rows_digest"],
            },
            "P28_5l_rule": {
                "name": rule_path.name,
                "sha256": _sha256(rule_path),
                "content_sha256": payload["inputs"]["P28_5l_rule"][
                    "content_sha256"
                ],
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.input, args.rule)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write(
        receipt_path,
        build_receipt(
            input_path=args.input,
            rule_path=args.rule,
            output=args.out,
            payload=payload,
        ),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "fresh_consumed_contexts": payload["fresh_participation_checksum"][
                    "consumed_context_count"
                ],
                "fresh_not_consumed_contexts": payload[
                    "fresh_participation_checksum"
                ]["not_consumed_context_count"],
                "quadrants": {
                    row["quadrant"]: {
                        "signature_cells": row["signature_cell_count"],
                        "contexts": row["context_count"],
                    }
                    for row in payload["quadrants"]
                },
                "next_stage": payload["next_stage_gate"]["status"],
                "fourth_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
