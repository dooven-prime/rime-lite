#!/usr/bin/env python3
"""Freeze fourth rank-four menus and exact lifts before Good_4 evaluation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from paper28_audit_fourth_rank4_section_overlap import SCHEMA as OVERLAP_SCHEMA
from paper28_mechanism_schema import exact_receipt_sha256, validate_receipt
from paper28_prepare_second_rank4_section_candidate import (
    _context_from_selection as _second_context_from_selection,
)
from paper28_prepare_third_rank4_section_candidate import (
    FORBIDDEN_CONSTRUCTION_FIELDS,
    _construction_core,
    _cycle,
    _factorization_summary,
)
from paper28_prepare_third_rank4_section_candidate import (
    _build_menus as _build_third_menus,
)
from paper28_prepare_third_rank4_section_candidate import (
    _record_from_edge as _third_record_from_edge,
)
from paper28_project_seed_mechanisms import Context
from paper28_select_fresh_consumption_hostile import SCHEMA as SELECTION_SCHEMA
from section_return_core import CompleteExitOracle

SCHEMA = "paper28-fourth-rank4-section-candidate-v1"
RECEIPT_SCHEMA = "paper28-fourth-rank4-section-candidate-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_fresh_consumption_hostile_selection_v1.json.gz"
)
DEFAULT_OVERLAP = (
    HERE / "results" / "paper28_fourth_rank4_section_overlap_audit_v1.json"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_fourth_rank4_section_candidate_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_prepare_fourth_rank4_section_candidate.py",
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_audit_fourth_rank4_section_overlap.py",
    "paper28_prepare_third_rank4_section_candidate.py",
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "validation/validate_paper28_fourth_rank4_section_candidate.py",
)
N = 7


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
    return output.with_name(f"{output.name.removesuffix('.json.gz')}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _context_from_selection(row: Mapping[str, Any]) -> Context:
    base = _second_context_from_selection(row)
    return replace(
        base,
        origin=f"n7-fourth-rank4-candidate-{row['index']}-{row['defect']}",
        seed_surface="N7_FOURTH_RANK4_CANDIDATE_36",
        is_seed=True,
    )


def _record_from_edge(context: Context, edge: Mapping[str, Any]) -> dict[str, Any]:
    record = _third_record_from_edge(context, edge)
    record["seed_surface"] = context.seed_surface
    record["relation_role"] = "RANK4_FOURTH_SECTION_CANDIDATE"
    record["origin"] = context.origin
    record["receipt_id"] = "pending"
    record["receipt_id"] = f"r4c4-{exact_receipt_sha256(record)[:24]}"
    validate_receipt(record)
    return record


def _build_menus(
    contexts: list[Context], records: list[Mapping[str, Any]]
) -> dict[str, Any]:
    menus = _build_third_menus(contexts, records)
    for context in menus["contexts"]:
        for channel in context["channels"]:
            channel["channel_id"] = str(channel["channel_id"]).replace(
                "r4c3m-", "r4c4m-", 1
            )
            for accounting in channel["accounting_refinements"]:
                accounting["accounting_id"] = str(accounting["accounting_id"]).replace(
                    "r4c3a-", "r4c4a-", 1
                )
    return menus


def build_payload(selection_path: Path, overlap_path: Path) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected fourth-candidate selection schema")
    if selection["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("selection input already contains success evaluation")
    if selection["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("selection input already claims section authority")

    overlap = _load(overlap_path)
    if overlap.get("schema") != OVERLAP_SCHEMA:
        raise AssertionError("unexpected fourth-section overlap schema")
    if overlap["inputs"]["fourth_candidate"]["sha256"] != _sha256(selection_path):
        raise AssertionError("overlap audit is not bound to this selection")
    if overlap["overlap"]["certified_union_intersection_count"] != 0:
        raise AssertionError("fourth carrier overlaps certified section authority")
    if overlap["scope"]["candidate_membership_mutated"]:
        raise AssertionError("overlap audit mutated candidate membership")

    selected_rows = selection["candidate"]["contexts"]
    contexts = [_context_from_selection(row) for row in selected_rows]
    if len(contexts) != 36 or len({context.context_id for context in contexts}) != 36:
        raise AssertionError("fourth rank-four carrier is not 36 distinct contexts")

    records = []
    factorizations = []
    for context in contexts:
        oracle = CompleteExitOracle((_cycle(N), context.defect), N)
        edges = list(oracle.macro_edges(context.mass))
        if not edges:
            raise AssertionError("fourth rank-four candidate has no macro exits")
        for edge in edges:
            record = _record_from_edge(context, edge)
            records.append(record)
            factorizations.append(_factorization_summary(record))
    records.sort(key=lambda row: str(row["receipt_id"]))
    factorizations.sort(key=lambda row: str(row["receipt_id"]))
    if len({row["receipt_id"] for row in records}) != len(records):
        raise AssertionError("fourth exact receipt ids are not unique")

    menus = _build_menus(contexts, records)
    factor_state_ids = {
        str(operation[side]["state_id"])
        for row in factorizations
        for operation in row["operation_occurrences"]
        for side in ("exact_source", "exact_target")
    }
    endpoint_state_ids = {str(row["source_state_id"]) for row in factorizations} | {
        str(row["target_state_id"]) for row in factorizations
    }
    operation_kinds = sorted(
        {str(kind) for row in factorizations for kind in row["operation_kind_path"]}
    )
    if not set(operation_kinds).issubset({"TRANSPORT", "RETURN", "FUSION"}):
        raise AssertionError("fourth carrier requires an undeclared generator kind")

    construction = {
        "source_carrier": {
            "name": "C_4,cand4^(7)",
            "recursive_authority": "NONE_PRE_EVALUATION",
            "selection_artifact": selection_path.name,
            "selection_artifact_sha256": _sha256(selection_path),
            "selection_content_sha256": selection["content_sha256"],
            "selection_candidate_payload_sha256": selection["candidate_payload_sha256"],
            "overlap_audit": overlap_path.name,
            "overlap_audit_sha256": _sha256(overlap_path),
            "overlap_content_sha256": overlap["content_sha256"],
            "certified_section_intersection_count": overlap["overlap"][
                "certified_union_intersection_count"
            ],
            "context_count": len(contexts),
            "context_ids": sorted(context.context_id for context in contexts),
        },
        "menus": menus,
        "exact_lifts": {
            "definition": (
                "complete source-addressed rank-four macro receipts factored "
                "through exact TRANSPORT/RETURN/FUSION operation paths"
            ),
            "receipt_count": len(records),
            "receipts": records,
            "factorizations": factorizations,
            "operation_kinds": operation_kinds,
        },
        "checkpoint_type_audit": {
            "menu_source_context_count": len(contexts),
            "exported_recursive_target_count": 0,
            "replay_state_count": len(factor_state_ids),
            "receipt_endpoint_state_count": len(endpoint_state_ids),
            "internal_only_state_count": len(factor_state_ids - endpoint_state_ids),
            "internal_only_exported_as_checkpoint": 0,
        },
    }
    encoded = json.dumps(
        _construction_core(construction),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field in encoded:
            raise AssertionError(
                f"future-success field leaked into construction: {field}"
            )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "source_rank": 4,
            "source": "36-context P28.5n fresh-consuming pre-section carrier",
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "nonclaim": (
                "this artifact freezes menus and exact lifts but does not evaluate "
                "Good_4 or certify return to P_<=3"
            ),
        },
        "phase_order": [
            "read_frozen_candidate_selection",
            "bind_read_only_typed_overlap_audit",
            "reconstruct_typed_rank4_sources",
            "enumerate_complete_future_free_macro_relation",
            "factor_exact_lifts_and_construct_menus",
            "freeze_construction_payload_and_digest",
            "low_rank_evaluator_absent",
        ],
        "inputs": {
            "selection": {
                "name": selection_path.name,
                "schema": selection["schema"],
                "sha256": _sha256(selection_path),
                "content_sha256": selection["content_sha256"],
            },
            "overlap_audit": {
                "name": overlap_path.name,
                "schema": overlap["schema"],
                "sha256": _sha256(overlap_path),
                "content_sha256": overlap["content_sha256"],
                "intersection_count": overlap["overlap"][
                    "certified_union_intersection_count"
                ],
            },
        },
        "construction": construction,
        "evaluator": {
            "status": "ABSENT_BY_DESIGN",
            "good_predicate_defined_for_later_phase": (
                "Good_4(C,m) iff an exact lift in Lift_4(C,m) has target in "
                "the exact P_<=3^(7) base"
            ),
            "evaluated_source_count": 0,
            "evaluated_channel_count": 0,
        },
    }
    payload["construction_payload_sha256"] = _digest(construction)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    selection_path: Path,
    overlap_path: Path,
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_SELECTION_AND_OVERLAP",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "construction_payload_sha256": payload["construction_payload_sha256"],
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
    parser.add_argument("--overlap", type=Path, default=DEFAULT_OVERLAP)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.selection, args.overlap)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            selection_path=args.selection,
            overlap_path=args.overlap,
            output=args.out,
            payload=payload,
        ),
    )
    menus = payload["construction"]["menus"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "construction_payload_sha256": payload["construction_payload_sha256"],
                "source_contexts": menus["context_count"],
                "menu_channels": menus["channel_count"],
                "accounting_refinements": menus["accounting_refinement_count"],
                "exact_lifts": menus["exact_lift_count"],
                "max_menu_size": menus["max_menu_size"],
                "operation_kinds": payload["construction"]["exact_lifts"][
                    "operation_kinds"
                ],
                "certified_section_intersection": 0,
                "good_4_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
