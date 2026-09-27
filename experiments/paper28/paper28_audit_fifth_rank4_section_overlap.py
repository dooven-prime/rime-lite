#!/usr/bin/env python3
"""Audit the fifth carrier against three certified rank-four sections."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_audit_fourth_rank4_section_overlap import (
    _certified_contexts,
    _digest,
    _load,
    _sha256,
    _write,
    default_receipt_path,
)
from paper28_prepare_second_rank4_section_candidate import _context_from_selection
from paper28_select_non_length_three_hostile import SCHEMA as SELECTION_SCHEMA

SCHEMA = "paper28-fifth-rank4-section-overlap-audit-v1"
RECEIPT_SCHEMA = "paper28-fifth-rank4-section-overlap-audit-receipt-v1"
AUTHORITY_SCHEMAS = {
    "second": "paper28-second-rank4-section-return-evaluation-v1",
    "third": "paper28-third-rank4-section-return-evaluation-v1",
    "fourth": "paper28-fourth-rank4-section-return-evaluation-v1",
}
HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_non_length_three_hostile_selection_v1.json.gz"
)
DEFAULT_SECOND_AUTHORITY = (
    HERE / "results" / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_THIRD_AUTHORITY = (
    HERE / "results" / "paper28_third_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_FOURTH_AUTHORITY = (
    HERE / "results" / "paper28_fourth_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_fifth_rank4_section_overlap_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_audit_fifth_rank4_section_overlap.py",
    "paper28_select_non_length_three_hostile.py",
    "paper28_audit_fourth_rank4_section_overlap.py",
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "validation/validate_paper28_fifth_rank4_section_overlap.py",
)


def build_payload(
    selection_path: Path,
    second_authority_path: Path,
    third_authority_path: Path,
    fourth_authority_path: Path,
) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected fifth candidate-selection schema")
    scope = selection["scope"]
    if scope["evaluation_status"] != "NOT_RUN":
        raise AssertionError("fifth candidate was not frozen before overlap audit")
    if scope["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("fifth candidate already claims section authority")

    authority_paths = {
        "second": second_authority_path,
        "third": third_authority_path,
        "fourth": fourth_authority_path,
    }
    authority_payloads = {label: _load(path) for label, path in authority_paths.items()}
    authority_contexts = {
        label: _certified_contexts(
            authority_payloads[label], AUTHORITY_SCHEMAS[label], label
        )
        for label in authority_paths
    }
    candidate_rows = [
        _context_from_selection(row).payload
        for row in selection["candidate"]["contexts"]
    ]
    candidate_by_id = {str(row["context_id"]): row for row in candidate_rows}
    if len(candidate_by_id) != 10:
        raise AssertionError("fifth overlap scope is not ten distinct contexts")

    intersections = {}
    certified_union: set[str] = set()
    for label, contexts in authority_contexts.items():
        certified_union.update(contexts)
        ids = sorted(set(candidate_by_id) & set(contexts))
        for context_id in ids:
            if candidate_by_id[context_id] != contexts[context_id]:
                raise AssertionError(
                    f"{label} context id collision with unequal payload"
                )
        intersections[label] = {
            "section_context_count": len(contexts),
            "intersection_count": len(ids),
            "intersection_context_ids": ids,
        }
    union_ids = sorted(set(candidate_by_id) & certified_union)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "candidate_membership_mutated": False,
            "menu_constructed": False,
            "good_4_evaluated": False,
        },
        "inputs": {
            "fifth_candidate": {
                "name": selection_path.name,
                "schema": selection["schema"],
                "sha256": _sha256(selection_path),
                "content_sha256": selection["content_sha256"],
                "candidate_payload_sha256": selection["candidate_payload_sha256"],
            },
            **{
                f"{label}_section_authority": {
                    "name": authority_paths[label].name,
                    "schema": authority_payloads[label]["schema"],
                    "sha256": _sha256(authority_paths[label]),
                    "content_sha256": authority_payloads[label]["content_sha256"],
                }
                for label in authority_paths
            },
        },
        "typed_identity": (
            "canonical context id computed from ambient n, rooted action, labelled "
            "packet placement, and distinguished packet"
        ),
        "overlap": {
            "fifth_candidate_context_count": len(candidate_by_id),
            "sections": intersections,
            "certified_union_intersection_count": len(union_ids),
            "certified_union_intersection_context_ids": union_ids,
            "fifth_only_count": len(set(candidate_by_id) - certified_union),
            "classification": (
                "DISJOINT_FROM_CERTIFIED_RANK4_SECTIONS"
                if not union_ids
                else (
                    "FULL_TYPED_OVERLAP"
                    if len(union_ids) == len(candidate_by_id)
                    else "PARTIAL_TYPED_OVERLAP"
                )
            ),
        },
        "claim_boundary": {
            "proved": (
                "exact typed identity overlap of the fifth frozen carrier with "
                "the certified second, third, and fourth rank-four sections"
            ),
            "not_claimed": [
                "fifth carrier section authority",
                "Good_4 success for the fifth carrier",
                "absence of a coarser typed isomorphism",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    selection_path: Path,
    second_authority_path: Path,
    third_authority_path: Path,
    fourth_authority_path: Path,
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "READ_ONLY_TYPED_SECTION_OVERLAP",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            key: {
                "name": row["name"],
                "sha256": row["sha256"],
                "content_sha256": row["content_sha256"],
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
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument(
        "--second-authority", type=Path, default=DEFAULT_SECOND_AUTHORITY
    )
    parser.add_argument("--third-authority", type=Path, default=DEFAULT_THIRD_AUTHORITY)
    parser.add_argument(
        "--fourth-authority", type=Path, default=DEFAULT_FOURTH_AUTHORITY
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        args.selection,
        args.second_authority,
        args.third_authority,
        args.fourth_authority,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write(
        receipt_path,
        build_receipt(
            selection_path=args.selection,
            second_authority_path=args.second_authority,
            third_authority_path=args.third_authority,
            fourth_authority_path=args.fourth_authority,
            output=args.out,
            payload=payload,
        ),
    )
    overlap = payload["overlap"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "fifth_contexts": overlap["fifth_candidate_context_count"],
                "section_intersections": {
                    label: row["intersection_count"]
                    for label, row in overlap["sections"].items()
                },
                "union_intersection": overlap["certified_union_intersection_count"],
                "classification": overlap["classification"],
                "candidate_membership_mutated": False,
                "good_4_evaluated": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
