#!/usr/bin/env python3
"""Replay and validate the pre-evaluation P28.5a section candidate."""

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

from paper28_prepare_rank5_section_candidate import (
    DEFAULT_OUTPUT,
    FORBIDDEN_CONSTRUCTION_FIELDS,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)

EXPECTED = {
    "action_local_carrier_count": 36,
    "source_context_count": 35,
    "menu_channel_count": 87,
    "max_menu_size": 3,
    "exact_lift_count": 214,
    "lower_section_context_count": 35,
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


def _construction_core(construction: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_contexts": construction["source_section"]["contexts"],
        "menu_contexts": construction["menus"]["contexts"],
        "exact_lifts": construction["exact_lifts"]["receipts"],
    }


def _assert_candidate(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected rank-five candidate schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("pre-evaluation artifact evaluated downstream success")
    if payload["construction_phase_order"] != [
        "source_section",
        "future_free_menus_and_exact_lifts",
        "construction_payload_digest",
        "independent_lower_section_projection",
        "future_hostile_evaluator_not_run",
    ]:
        raise AssertionError("construction phase order drift")

    construction = payload["construction"]
    source = construction["source_section"]
    menus = construction["menus"]
    lifts = construction["exact_lifts"]
    target = payload["lower_section_target"]
    observed = {
        "action_local_carrier_count": source["action_local_carrier_count"],
        "source_context_count": source["context_count"],
        "menu_channel_count": menus["channel_count"],
        "max_menu_size": menus["max_menu_size"],
        "exact_lift_count": lifts["receipt_count"],
        "lower_section_context_count": target["context_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"candidate checksum drift: {observed!r}")

    excluded = source["excluded_sources"]
    if len(excluded) != 1 or excluded[0]["defect"] != "0123450":
        raise AssertionError("source-local predecessor exclusion drift")
    if any(row["defect"] == "0123450" for row in source["contexts"]):
        raise AssertionError("excluded predecessor entered the source section")

    source_ids = {
        row["context"]["context_id"] for row in source["contexts"]
    }
    menu_ids = {row["source_context_id"] for row in menus["contexts"]}
    receipt_source_ids = {
        row["exact"]["source_context_id"] for row in lifts["receipts"]
    }
    if source_ids != menu_ids or source_ids != receipt_source_ids:
        raise AssertionError("source, menu, and exact-lift domains disagree")
    if any(row["menu_size"] != len(row["channels"]) for row in menus["contexts"]):
        raise AssertionError("menu-size serialization drift")

    audit = construction["checkpoint_type_audit"]
    if audit["menu_source_context_count"] != len(source_ids):
        raise AssertionError("menu source typing drift")
    if audit["exported_recursive_target_count"] != 0:
        raise AssertionError("a target was exported before Good_5 evaluation")
    if audit["internal_only_exported_as_checkpoint"] != 0:
        raise AssertionError("an internal boundary gained checkpoint authority")

    evaluator = payload["evaluator"]
    if evaluator != {
        "status": "ABSENT_BY_DESIGN",
        "good_predicate_defined_for_later_phase": (
            "Good_5(C,m) iff an exact lift in Lift_5(C,m) has target "
            "in Sec_4,ext^(7)"
        ),
        "evaluated_source_count": 0,
        "evaluated_channel_count": 0,
    }:
        raise AssertionError("hostile evaluator is not absent by design")

    encoded = json.dumps(
        _construction_core(construction),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field.lower() in encoded:
            raise AssertionError(
                f"future-success field leaked into construction: {field}"
            )

    if payload["construction_payload_sha256"] != _digest(construction):
        raise AssertionError("construction payload digest mismatch")
    content = dict(payload)
    observed_content_digest = content.pop("content_sha256")
    if observed_content_digest != _digest(content):
        raise AssertionError("artifact content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n7-extremal-input", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.n7_extremal_input)
    _assert_candidate(stored)
    _assert_candidate(recomputed)
    if stored != recomputed:
        raise AssertionError("stored candidate artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected rank-five candidate receipt schema")
    expected_receipt = build_receipt(output=args.artifact, payload=stored)
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or closure binding drifted")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "construction_payload_sha256": stored[
                    "construction_payload_sha256"
                ],
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "source_contexts": EXPECTED["source_context_count"],
                "menu_channels": EXPECTED["menu_channel_count"],
                "exact_lifts": EXPECTED["exact_lift_count"],
                "good_5_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
