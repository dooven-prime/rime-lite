#!/usr/bin/env python3
"""Replay the pre-evaluation fourth rank-five relation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_prepare_fourth_rank5_section_candidate import (
    DEFAULT_LOWER_SECTION,
    DEFAULT_OUTPUT,
    DEFAULT_SELECTION,
    FORBIDDEN_CONSTRUCTION_FIELDS,
    RECEIPT_SCHEMA,
    SCHEMA,
    _digest,
    _load,
    build_payload,
    build_receipt,
    default_receipt_path,
)

EXPECTED = {
    "source_context_count": 36,
    "channel_count": 107,
    "max_menu_size": 4,
    "exact_lift_count": 252,
    "selected_sigma5_receipt_count": 36,
    "participation_histogram": {"FIRST_ONLY": 179, "NONE": 73},
    "replay_state_count": 838,
    "receipt_endpoint_state_count": 287,
    "internal_only_state_count": 551,
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fourth rank-five candidate schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5 evaluation")
    if payload["scope"]["hostile_evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5_consume evaluation")
    evaluator = payload["evaluator"]
    if evaluator["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("candidate evaluator is not absent")
    if evaluator["ordinary_good_5_status"] != "NOT_RUN":
        raise AssertionError("ordinary Good_5 ran before freeze")
    if evaluator["hostile_good_5_consume_status"] != "NOT_RUN":
        raise AssertionError("hostile Good_5_consume ran before freeze")
    if payload["construction_payload_sha256"] != _digest(payload["construction"]):
        raise AssertionError("construction payload digest mismatch")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("candidate content digest mismatch")

    construction = payload["construction"]
    source = construction["source_section"]
    menus = construction["menus"]
    lifts = construction["exact_lifts"]
    audit = construction["checkpoint_type_audit"]
    observed = {
        "source_context_count": source["context_count"],
        "channel_count": menus["channel_count"],
        "max_menu_size": menus["max_menu_size"],
        "exact_lift_count": lifts["receipt_count"],
        "selected_sigma5_receipt_count": lifts["selected_sigma5_receipt_count"],
        "participation_histogram": lifts["ancestry_participation_histogram"],
        "replay_state_count": audit["replay_state_count"],
        "receipt_endpoint_state_count": audit["receipt_endpoint_state_count"],
        "internal_only_state_count": audit["internal_only_state_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fourth rank-five finite equalities drift: {observed!r}")
    if (
        menus["context_count"] != 36
        or payload["lower_section_target"]["context_count"] != 36
    ):
        raise AssertionError("fourth rank-five source/lower count drift")
    if (
        audit["internal_only_exported_as_checkpoint"]
        or audit["exported_recursive_target_count"]
    ):
        raise AssertionError("pre-evaluation rank-five relation exported checkpoint")

    source_ids = {str(row["context"]["context_id"]) for row in source["contexts"]}
    menu_source_ids = {str(row["source_context_id"]) for row in menus["contexts"]}
    if source_ids != menu_source_ids or len(source_ids) != 36:
        raise AssertionError("fourth rank-five source/menu typing drift")
    receipts = lifts["receipts"]
    receipt_ids = [str(row["receipt_id"]) for row in receipts]
    if (
        len(receipt_ids) != len(set(receipt_ids))
        or len(receipt_ids) != lifts["receipt_count"]
    ):
        raise AssertionError("fourth exact receipt identity/count drift")
    menu_lift_ids = [
        str(receipt_id)
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    ]
    if Counter(menu_lift_ids) != Counter(receipt_ids):
        raise AssertionError("fourth menu fibers do not partition exact receipts")
    factorization_ids = [str(row["receipt_id"]) for row in lifts["factorizations"]]
    if Counter(factorization_ids) != Counter(receipt_ids):
        raise AssertionError("fourth factorizations do not cover exact receipts")
    operation_kinds = {
        str(kind)
        for row in lifts["factorizations"]
        for kind in row["operation_kind_path"]
    }
    if not operation_kinds.issubset({"TRANSPORT", "RETURN", "FUSION"}):
        raise AssertionError(f"unexpected generator kind: {operation_kinds!r}")

    selected_ids = set(lifts["selected_sigma5_receipt_ids"])
    if len(selected_ids) < 36 or not selected_ids <= set(receipt_ids):
        raise AssertionError("selected fresh-consuming receipts are incomplete")
    for row in source["contexts"]:
        if not row["selected_sigma5_exact_lift_ids"]:
            raise AssertionError("source lacks its selected Sigma_5 lift")
        if not row["selected_sigma5_consumes_incoming_distinguished"]:
            raise AssertionError("selected Sigma_5 lift lost fresh consumption")
    by_id = {str(row["receipt_id"]): row for row in receipts}
    for receipt_id in selected_ids:
        if (
            by_id[receipt_id]["exact"]["ancestry_update"]["participation_type"]
            == "NONE"
        ):
            raise AssertionError("selected Sigma_5 lift avoids incoming ancestry")
    for record in receipts:
        source_context = next(
            row
            for row in source["contexts"]
            if row["context"]["context_id"] == record["exact"]["source_context_id"]
        )
        if (
            record["exact"]["ancestry_update"]["incoming_distinguished_packet"]
            != source_context["incoming_distinguished_packet"]
        ):
            raise AssertionError("exact lift lost incoming distinguished identity")

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
            raise AssertionError(f"construction contains forbidden field: {field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--lower-section", type=Path, default=DEFAULT_LOWER_SECTION)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.selection, args.lower_section)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fourth rank-five candidate differs from replay")
    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fourth rank-five receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        lower_section_path=args.lower_section,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fourth rank-five receipt is stale")
    construction = stored["construction"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "source_contexts": construction["source_section"]["context_count"],
                "menu_channels": construction["menus"]["channel_count"],
                "max_menu_size": construction["menus"]["max_menu_size"],
                "exact_lifts": construction["exact_lifts"]["receipt_count"],
                "selected_fresh_consuming_receipts": construction["exact_lifts"][
                    "selected_sigma5_receipt_count"
                ],
                "good_5_evaluation": "NOT_RUN",
                "good_5_consume_evaluation": "NOT_RUN",
                "internal_boundaries_exported_as_checkpoints": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
