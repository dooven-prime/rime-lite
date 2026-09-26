#!/usr/bin/env python3
"""Audit typed overlap of the third carrier with the certified second section.

This audit is read-only with respect to candidate membership.  It compares
canonical typed context identities only after the 36-source P28.5h carrier has
been frozen.  It does not construct menus or evaluate Good_4.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_prepare_second_rank4_section_candidate import _context_from_selection
from paper28_select_third_rank5_return_candidate import SCHEMA as SELECTION_SCHEMA


SCHEMA = "paper28-third-rank4-section-overlap-audit-v1"
RECEIPT_SCHEMA = "paper28-third-rank4-section-overlap-audit-receipt-v1"
SECOND_AUTHORITY_SCHEMA = "paper28-second-rank4-section-return-evaluation-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_third_rank5_return_candidate_selection_v1.json.gz"
)
DEFAULT_AUTHORITY = (
    HERE / "results" / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_third_rank4_section_overlap_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_audit_third_rank4_section_overlap.py",
    "paper28_select_third_rank5_return_candidate.py",
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "validation/validate_paper28_third_rank4_section_overlap.py",
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


def build_payload(selection_path: Path, authority_path: Path) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected third candidate-selection schema")
    if selection["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("third candidate was not frozen before overlap audit")
    if selection["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("third candidate already claims section authority")

    authority = _load(authority_path)
    if authority.get("schema") != SECOND_AUTHORITY_SCHEMA:
        raise AssertionError("unexpected second-section authority schema")
    certified = authority["certified_lower_section"]
    if certified["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
        raise AssertionError("second rank-four section lacks certified authority")

    third_contexts = [
        _context_from_selection(row).payload for row in selection["candidate"]["contexts"]
    ]
    second_contexts = list(certified["contexts"])
    third_by_id = {str(row["context_id"]): row for row in third_contexts}
    second_by_id = {str(row["context_id"]): row for row in second_contexts}
    if len(third_by_id) != 36 or len(second_by_id) != 48:
        raise AssertionError("typed overlap scope drift")

    intersection = sorted(set(third_by_id) & set(second_by_id))
    for context_id in intersection:
        if third_by_id[context_id] != second_by_id[context_id]:
            raise AssertionError("context id collision with unequal typed payload")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "candidate_membership_mutated": False,
            "menu_constructed": False,
            "good_4_evaluated": False,
        },
        "inputs": {
            "third_candidate": {
                "name": selection_path.name,
                "schema": selection["schema"],
                "sha256": _sha256(selection_path),
                "content_sha256": selection["content_sha256"],
                "candidate_payload_sha256": selection["candidate_payload_sha256"],
            },
            "second_section_authority": {
                "name": authority_path.name,
                "schema": authority["schema"],
                "sha256": _sha256(authority_path),
                "content_sha256": authority["content_sha256"],
                "authority_status": certified["authority_status"],
            },
        },
        "typed_identity": (
            "canonical context id computed from ambient n, rooted action, labelled "
            "packet placement, and distinguished packet"
        ),
        "overlap": {
            "third_candidate_context_count": len(third_by_id),
            "second_section_context_count": len(second_by_id),
            "intersection_count": len(intersection),
            "intersection_context_ids": intersection,
            "third_only_count": len(set(third_by_id) - set(second_by_id)),
            "second_only_count": len(set(second_by_id) - set(third_by_id)),
            "classification": (
                "DISJOINT_TYPED_CONTEXTS" if not intersection else "PARTIAL_TYPED_OVERLAP"
            ),
        },
        "claim_boundary": {
            "proved": "exact typed identity overlap of the two frozen rank-four surfaces",
            "not_claimed": [
                "third carrier section authority",
                "Good_4 success for the third carrier",
                "absence of a coarser typed isomorphism",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, selection_path: Path, authority_path: Path, output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    closure = []
    for relative in SOURCE_CLOSURE:
        path = HERE / relative
        closure.append(
            {"path": path.relative_to(repo_root).as_posix(), "sha256": _sha256(path)}
        )
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "READ_ONLY_TYPED_SECTION_OVERLAP",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            "third_candidate": {
                "name": selection_path.name,
                "sha256": _sha256(selection_path),
                "content_sha256": payload["inputs"]["third_candidate"]["content_sha256"],
            },
            "second_section_authority": {
                "name": authority_path.name,
                "sha256": _sha256(authority_path),
                "content_sha256": payload["inputs"]["second_section_authority"]["content_sha256"],
            },
        },
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.selection, args.authority)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write(
        receipt_path,
        build_receipt(
            selection_path=args.selection,
            authority_path=args.authority,
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
                "third_contexts": payload["overlap"]["third_candidate_context_count"],
                "second_authority_contexts": payload["overlap"]["second_section_context_count"],
                "intersection": payload["overlap"]["intersection_count"],
                "classification": payload["overlap"]["classification"],
                "candidate_membership_mutated": False,
                "good_4_evaluated": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
