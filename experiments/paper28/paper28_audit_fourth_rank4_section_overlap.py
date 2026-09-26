#!/usr/bin/env python3
"""Audit the fourth carrier against the two certified rank-four sections."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_prepare_second_rank4_section_candidate import _context_from_selection
from paper28_select_fresh_consumption_hostile import SCHEMA as SELECTION_SCHEMA

SCHEMA = "paper28-fourth-rank4-section-overlap-audit-v1"
RECEIPT_SCHEMA = "paper28-fourth-rank4-section-overlap-audit-receipt-v1"
SECOND_AUTHORITY_SCHEMA = "paper28-second-rank4-section-return-evaluation-v1"
THIRD_AUTHORITY_SCHEMA = "paper28-third-rank4-section-return-evaluation-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_fresh_consumption_hostile_selection_v1.json.gz"
)
DEFAULT_SECOND_AUTHORITY = (
    HERE / "results" / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_THIRD_AUTHORITY = (
    HERE / "results" / "paper28_third_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_fourth_rank4_section_overlap_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_audit_fourth_rank4_section_overlap.py",
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "validation/validate_paper28_fourth_rank4_section_overlap.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="ascii",
        newline="\n",
    )


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name.removesuffix('.json')}.receipt.json")


def _certified_contexts(
    payload: Mapping[str, Any], expected_schema: str, label: str
) -> dict[str, Mapping[str, Any]]:
    if payload.get("schema") != expected_schema:
        raise AssertionError(f"unexpected {label} authority schema")
    certified = payload["certified_lower_section"]
    if certified["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
        raise AssertionError(f"{label} rank-four section lacks authority")
    return {str(row["context_id"]): row for row in certified["contexts"]}


def build_payload(
    selection_path: Path,
    second_authority_path: Path,
    third_authority_path: Path,
) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected fourth candidate-selection schema")
    if selection["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("fourth candidate was not frozen before overlap audit")
    if selection["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("fourth candidate already claims section authority")

    second = _load(second_authority_path)
    third = _load(third_authority_path)
    second_by_id = _certified_contexts(second, SECOND_AUTHORITY_SCHEMA, "second")
    third_by_id = _certified_contexts(third, THIRD_AUTHORITY_SCHEMA, "third")
    fourth_rows = [
        _context_from_selection(row).payload
        for row in selection["candidate"]["contexts"]
    ]
    fourth_by_id = {str(row["context_id"]): row for row in fourth_rows}
    if len(fourth_by_id) != 36 or len(second_by_id) != 48 or len(third_by_id) != 36:
        raise AssertionError("fourth overlap scope drift")

    second_intersection = sorted(set(fourth_by_id) & set(second_by_id))
    third_intersection = sorted(set(fourth_by_id) & set(third_by_id))
    for context_id in second_intersection:
        if fourth_by_id[context_id] != second_by_id[context_id]:
            raise AssertionError("second context id collision with unequal payload")
    for context_id in third_intersection:
        if fourth_by_id[context_id] != third_by_id[context_id]:
            raise AssertionError("third context id collision with unequal payload")
    union_ids = set(second_by_id) | set(third_by_id)
    union_intersection = sorted(set(fourth_by_id) & union_ids)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "candidate_membership_mutated": False,
            "menu_constructed": False,
            "good_4_evaluated": False,
        },
        "inputs": {
            "fourth_candidate": {
                "name": selection_path.name,
                "schema": selection["schema"],
                "sha256": _sha256(selection_path),
                "content_sha256": selection["content_sha256"],
                "candidate_payload_sha256": selection["candidate_payload_sha256"],
            },
            "second_section_authority": {
                "name": second_authority_path.name,
                "schema": second["schema"],
                "sha256": _sha256(second_authority_path),
                "content_sha256": second["content_sha256"],
            },
            "third_section_authority": {
                "name": third_authority_path.name,
                "schema": third["schema"],
                "sha256": _sha256(third_authority_path),
                "content_sha256": third["content_sha256"],
            },
        },
        "typed_identity": (
            "canonical context id computed from ambient n, rooted action, labelled "
            "packet placement, and distinguished packet"
        ),
        "overlap": {
            "fourth_candidate_context_count": len(fourth_by_id),
            "second_section_context_count": len(second_by_id),
            "third_section_context_count": len(third_by_id),
            "second_intersection_count": len(second_intersection),
            "second_intersection_context_ids": second_intersection,
            "third_intersection_count": len(third_intersection),
            "third_intersection_context_ids": third_intersection,
            "certified_union_intersection_count": len(union_intersection),
            "certified_union_intersection_context_ids": union_intersection,
            "fourth_only_count": len(set(fourth_by_id) - union_ids),
            "classification": (
                "DISJOINT_FROM_CERTIFIED_RANK4_SECTIONS"
                if not union_intersection
                else "PARTIAL_TYPED_OVERLAP"
            ),
        },
        "claim_boundary": {
            "proved": (
                "exact typed identity overlap of the fourth frozen carrier with "
                "the certified second and third rank-four sections"
            ),
            "not_claimed": [
                "fourth carrier section authority",
                "Good_4 success for the fourth carrier",
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.selection, args.second_authority, args.third_authority)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write(
        receipt_path,
        build_receipt(
            selection_path=args.selection,
            second_authority_path=args.second_authority,
            third_authority_path=args.third_authority,
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
                "fourth_contexts": overlap["fourth_candidate_context_count"],
                "second_intersection": overlap["second_intersection_count"],
                "third_intersection": overlap["third_intersection_count"],
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
