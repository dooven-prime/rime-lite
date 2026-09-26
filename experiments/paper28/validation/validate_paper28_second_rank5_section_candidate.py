#!/usr/bin/env python3
"""Replay the pre-evaluation second rank-five section candidate."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_prepare_second_rank5_section_candidate import (
    DEFAULT_LOWER_SECTION,
    DEFAULT_OUTPUT,
    DEFAULT_SELECTION,
    FORBIDDEN_CONSTRUCTION_FIELDS,
    RECEIPT_SCHEMA,
    SCHEMA,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED_SOURCE_CONTEXTS = 48


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
        raise AssertionError("unexpected second rank-five candidate schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5 evaluation")
    if payload["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("candidate evaluator is not absent")
    if payload["construction_payload_sha256"] != _digest(
        payload["construction"]
    ):
        raise AssertionError("construction payload digest mismatch")
    content = dict(payload)
    observed_content_digest = content.pop("content_sha256")
    if observed_content_digest != _digest(content):
        raise AssertionError("candidate content digest mismatch")

    construction = payload["construction"]
    source = construction["source_section"]
    menus = construction["menus"]
    lifts = construction["exact_lifts"]
    if source["context_count"] != EXPECTED_SOURCE_CONTEXTS:
        raise AssertionError("second rank-five source count drift")
    if menus["context_count"] != EXPECTED_SOURCE_CONTEXTS:
        raise AssertionError("second rank-five menu context count drift")
    if payload["lower_section_target"]["context_count"] != 48:
        raise AssertionError("lower section authority count drift")
    if construction["checkpoint_type_audit"][
        "internal_only_exported_as_checkpoint"
    ]:
        raise AssertionError("internal boundary exported as checkpoint")
    if construction["checkpoint_type_audit"]["exported_recursive_target_count"]:
        raise AssertionError("pre-evaluation candidate exported a recursive target")

    source_ids = {
        str(row["context"]["context_id"]) for row in source["contexts"]
    }
    menu_source_ids = {
        str(row["source_context_id"]) for row in menus["contexts"]
    }
    if source_ids != menu_source_ids or len(source_ids) != EXPECTED_SOURCE_CONTEXTS:
        raise AssertionError("source/menu typing drift")

    receipts = lifts["receipts"]
    receipt_ids = [str(row["receipt_id"]) for row in receipts]
    if len(receipt_ids) != len(set(receipt_ids)):
        raise AssertionError("exact receipt ids are not unique")
    if len(receipt_ids) != lifts["receipt_count"]:
        raise AssertionError("exact receipt count drift")
    menu_lift_ids = [
        str(receipt_id)
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    ]
    if Counter(menu_lift_ids) != Counter(receipt_ids):
        raise AssertionError("menu fibers do not partition exact receipts")
    factorization_ids = [
        str(row["receipt_id"]) for row in lifts["factorizations"]
    ]
    if Counter(factorization_ids) != Counter(receipt_ids):
        raise AssertionError("factorizations do not cover exact receipts")
    operation_kinds = {
        str(kind)
        for row in lifts["factorizations"]
        for kind in row["operation_kind_path"]
    }
    if not operation_kinds.issubset({"TRANSPORT", "RETURN", "FUSION"}):
        raise AssertionError(f"unexpected generator kind: {operation_kinds!r}")

    theorem_data = json.dumps(
        {
            "source_contexts": source["contexts"],
            "menu_contexts": menus["contexts"],
            "exact_lifts": receipts,
            "factorizations": lifts["factorizations"],
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field.lower() in theorem_data:
            raise AssertionError(
                f"construction contains forbidden success field: {field}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument(
        "--lower-section",
        type=Path,
        default=DEFAULT_LOWER_SECTION,
    )
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.selection, args.lower_section)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored second rank-five candidate differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected second rank-five receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        lower_section_path=args.lower_section,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored receipt is stale or closure binding drifted")

    construction = stored["construction"]
    kinds = sorted(
        {
            str(kind)
            for row in construction["exact_lifts"]["factorizations"]
            for kind in row["operation_kind_path"]
        }
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "source_contexts": construction["source_section"][
                    "context_count"
                ],
                "menu_channels": construction["menus"]["channel_count"],
                "max_menu_size": construction["menus"]["max_menu_size"],
                "exact_lifts": construction["exact_lifts"]["receipt_count"],
                "operation_kinds": kinds,
                "good_5_evaluation": "NOT_RUN",
                "lower_section": stored["lower_section_target"]["name"],
                "internal_boundaries_exported_as_checkpoints": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
