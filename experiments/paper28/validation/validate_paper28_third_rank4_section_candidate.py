#!/usr/bin/env python3
"""Replay the pre-evaluation P28.5i third rank-four relation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_prepare_third_rank4_section_candidate import (
    DEFAULT_OUTPUT,
    DEFAULT_OVERLAP,
    DEFAULT_SELECTION,
    FORBIDDEN_CONSTRUCTION_FIELDS,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED = {
    "context_count": 36,
    "channel_count": 172,
    "accounting_refinement_count": 1503,
    "exact_lift_count": 5239,
    "max_menu_size": 7,
    "menu_size_histogram": {"3": 2, "4": 11, "5": 17, "6": 5, "7": 1},
    "replay_state_count": 13997,
    "receipt_endpoint_state_count": 749,
    "internal_only_state_count": 13248,
}


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


def _assert_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected third rank-four candidate schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("pre-evaluation artifact contains Good_4 output")
    if payload["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("pre-evaluation carrier gained section authority")

    construction = payload["construction"]
    source = construction["source_carrier"]
    menus = construction["menus"]
    lifts = construction["exact_lifts"]
    if source["context_count"] != 36 or menus["context_count"] != 36:
        raise AssertionError("third rank-four source count drift")
    if source["recursive_authority"] != "NONE_PRE_EVALUATION":
        raise AssertionError("third source carrier authority drift")
    if source["old_section_intersection_count"] != 0:
        raise AssertionError("third source overlaps old section authority")
    if menus["exact_lift_count"] != lifts["receipt_count"]:
        raise AssertionError("menu and third exact relation disagree")
    observed_counts = {
        "context_count": menus["context_count"],
        "channel_count": menus["channel_count"],
        "accounting_refinement_count": menus["accounting_refinement_count"],
        "exact_lift_count": menus["exact_lift_count"],
        "max_menu_size": menus["max_menu_size"],
        "menu_size_histogram": menus["menu_size_histogram"],
        "replay_state_count": construction["checkpoint_type_audit"]["replay_state_count"],
        "receipt_endpoint_state_count": construction["checkpoint_type_audit"][
            "receipt_endpoint_state_count"
        ],
        "internal_only_state_count": construction["checkpoint_type_audit"][
            "internal_only_state_count"
        ],
    }
    if observed_counts != EXPECTED:
        raise AssertionError(f"third construction finite equalities drift: {observed_counts!r}")
    if set(lifts["operation_kinds"]) - {"TRANSPORT", "RETURN", "FUSION"}:
        raise AssertionError("undeclared generator operation entered third relation")

    source_ids = set(source["context_ids"])
    menu_ids = {row["source_context"]["context_id"] for row in menus["contexts"]}
    receipt_ids = {str(row["receipt_id"]) for row in lifts["receipts"]}
    receipt_source_ids = {row["exact"]["source_context_id"] for row in lifts["receipts"]}
    factor_ids = {str(row["receipt_id"]) for row in lifts["factorizations"]}
    if source_ids != menu_ids or source_ids != receipt_source_ids:
        raise AssertionError("third source/menu/exact-lift domains disagree")
    if receipt_ids != factor_ids:
        raise AssertionError("third exact relation and factorization disagree")
    menu_lift_ids = {
        receipt_id
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    }
    if menu_lift_ids != receipt_ids:
        raise AssertionError("third menu channels do not partition exact relation")

    audit = construction["checkpoint_type_audit"]
    if audit["exported_recursive_target_count"] != 0:
        raise AssertionError("third target exported before Good_4 evaluation")
    if audit["internal_only_exported_as_checkpoint"] != 0:
        raise AssertionError("third internal boundary gained checkpoint authority")
    if payload["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("third low-rank evaluator is not absent")

    encoded = json.dumps(
        {
            "source_context_ids": source["context_ids"],
            "menu_contexts": menus["contexts"],
            "exact_receipts": lifts["receipts"],
            "factorizations": lifts["factorizations"],
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field in encoded:
            raise AssertionError(f"future-success field leaked into construction: {field}")

    if payload["construction_payload_sha256"] != _digest(construction):
        raise AssertionError("third construction payload digest mismatch")
    content = dict(payload)
    observed = content.pop("content_sha256")
    if observed != _digest(content):
        raise AssertionError("third artifact content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--overlap", type=Path, default=DEFAULT_OVERLAP)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.selection, args.overlap)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored third rank-four construction differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected third rank-four receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        overlap_path=args.overlap,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("third rank-four receipt is stale")

    menus = stored["construction"]["menus"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "source_contexts": menus["context_count"],
                "menu_channels": menus["channel_count"],
                "accounting_refinements": menus["accounting_refinement_count"],
                "exact_lifts": menus["exact_lift_count"],
                "max_menu_size": menus["max_menu_size"],
                "good_4_evaluation": "NOT_RUN",
                "section_authority": "NOT_GRANTED",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
