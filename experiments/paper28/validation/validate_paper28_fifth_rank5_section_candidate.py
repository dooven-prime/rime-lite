#!/usr/bin/env python3
"""Replay the pre-evaluation fifth rank-five relation."""

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

from paper28_prepare_fifth_rank5_section_candidate import (
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
    "source_context_count": 10,
    "channel_count": 28,
    "max_menu_size": 3,
    "exact_lift_count": 62,
    "selected_sigma5_receipt_count": 10,
    "selected_sigma5_length_histogram": {"5": 10},
    "exact_fiber_length_histogram": {"5": 20, "6": 6, "7": 9, "8": 9, "9": 18},
    "length_three_exact_lift_count": 0,
    "non_length_three_exact_lift_count": 62,
    "participation_histogram": {"FIRST_ONLY": 52, "NONE": 10},
    "replay_state_count": 254,
    "receipt_endpoint_state_count": 72,
    "internal_only_state_count": 182,
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fifth rank-five candidate schema")
    if payload["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5 evaluation")
    if payload["scope"]["hostile_evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5^non3 evaluation")
    evaluator = payload["evaluator"]
    if evaluator["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("candidate evaluator is not absent")
    if evaluator["ordinary_good_5_status"] != "NOT_RUN":
        raise AssertionError("ordinary Good_5 ran before freeze")
    if evaluator["hostile_good_5_non3_status"] != "NOT_RUN":
        raise AssertionError("hostile Good_5^non3 ran before freeze")
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
        "selected_sigma5_length_histogram": lifts[
            "selected_sigma5_length_histogram"
        ],
        "exact_fiber_length_histogram": lifts["exact_fiber_length_histogram"],
        "length_three_exact_lift_count": lifts[
            "length_three_exact_lift_count"
        ],
        "non_length_three_exact_lift_count": lifts[
            "non_length_three_exact_lift_count"
        ],
        "participation_histogram": lifts["ancestry_participation_histogram"],
        "replay_state_count": audit["replay_state_count"],
        "receipt_endpoint_state_count": audit["receipt_endpoint_state_count"],
        "internal_only_state_count": audit["internal_only_state_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fifth rank-five finite equalities drift: {observed!r}")
    if (
        menus["context_count"] != 10
        or payload["lower_section_target"]["context_count"] != 10
    ):
        raise AssertionError("fifth rank-five source/lower count drift")
    if (
        audit["internal_only_exported_as_checkpoint"]
        or audit["exported_recursive_target_count"]
    ):
        raise AssertionError("pre-evaluation rank-five relation exported checkpoint")

    source_ids = {str(row["context"]["context_id"]) for row in source["contexts"]}
    menu_source_ids = {str(row["source_context_id"]) for row in menus["contexts"]}
    if source_ids != menu_source_ids or len(source_ids) != 10:
        raise AssertionError("fifth rank-five source/menu typing drift")
    receipts = lifts["receipts"]
    receipt_ids = [str(row["receipt_id"]) for row in receipts]
    if (
        len(receipt_ids) != len(set(receipt_ids))
        or len(receipt_ids) != lifts["receipt_count"]
    ):
        raise AssertionError("fifth exact receipt identity/count drift")
    menu_lift_ids = [
        str(receipt_id)
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    ]
    if Counter(menu_lift_ids) != Counter(receipt_ids):
        raise AssertionError("fifth menu fibers do not partition exact receipts")
    factorization_ids = [str(row["receipt_id"]) for row in lifts["factorizations"]]
    if Counter(factorization_ids) != Counter(receipt_ids):
        raise AssertionError("fifth factorizations do not cover exact receipts")
    operation_kinds = {
        str(kind)
        for row in lifts["factorizations"]
        for kind in row["operation_kind_path"]
    }
    if not operation_kinds.issubset({"TRANSPORT", "RETURN", "FUSION"}):
        raise AssertionError(f"unexpected generator kind: {operation_kinds!r}")

    selected_ids = set(lifts["selected_sigma5_receipt_ids"])
    if len(selected_ids) < 10 or not selected_ids <= set(receipt_ids):
        raise AssertionError("selected non-length-three receipts are incomplete")
    for row in source["contexts"]:
        if not row["selected_sigma5_exact_lift_ids"]:
            raise AssertionError("source lacks its selected Sigma_5 lift")
        if not row["selected_sigma5_consumes_incoming_distinguished"]:
            raise AssertionError("selected Sigma_5 lift lost fresh consumption")
    by_id = {str(row["receipt_id"]): row for row in receipts}
    exact_lengths = {
        receipt_id: int(record["accounting"]["corridors"][0]["length"])
        for receipt_id, record in by_id.items()
    }
    exact_histogram = {
        str(length): count
        for length, count in sorted(Counter(exact_lengths.values()).items())
    }
    if exact_histogram != lifts["exact_fiber_length_histogram"]:
        raise AssertionError("global exact-fiber length spectrum drift")
    length_three_count = sum(length == 3 for length in exact_lengths.values())
    if length_three_count != lifts["length_three_exact_lift_count"]:
        raise AssertionError("global length-three count drift")
    if len(receipts) - length_three_count != lifts["non_length_three_exact_lift_count"]:
        raise AssertionError("global non-length-three count drift")
    if lifts["length_spectrum_role"] != (
        "success-free projection of the complete exact relation; not an "
        "admission, channel, or receipt filter"
    ):
        raise AssertionError("length spectrum acquired an admission role")

    selected_histogram = {
        str(length): count
        for length, count in sorted(
            Counter(exact_lengths[receipt_id] for receipt_id in selected_ids).items()
        )
    }
    if selected_histogram != lifts["selected_sigma5_length_histogram"]:
        raise AssertionError("selected Sigma_5 length spectrum drift")
    for receipt_id in selected_ids:
        if (
            by_id[receipt_id]["exact"]["ancestry_update"]["participation_type"]
            == "NONE"
        ):
            raise AssertionError("selected Sigma_5 lift avoids incoming ancestry")
        if by_id[receipt_id]["accounting"]["corridors"][0]["length"] == 3:
            raise AssertionError("selected Sigma_5 lift has length three")
    source_by_id = {
        str(row["context"]["context_id"]): row for row in source["contexts"]
    }
    source_receipt_ids: dict[str, list[str]] = {
        source_id: [] for source_id in source_by_id
    }
    for receipt_id, record in by_id.items():
        source_receipt_ids[str(record["exact"]["source_context_id"])].append(receipt_id)
    for source_id, row in source_by_id.items():
        ids = source_receipt_ids[source_id]
        histogram = {
            str(length): count
            for length, count in sorted(
                Counter(exact_lengths[receipt_id] for receipt_id in ids).items()
            )
        }
        if histogram != row["exact_fiber_length_histogram"]:
            raise AssertionError("per-source exact-fiber length spectrum drift")
        l3_count = sum(exact_lengths[receipt_id] == 3 for receipt_id in ids)
        if l3_count != row["exact_fiber_length_three_count"]:
            raise AssertionError("per-source length-three count drift")
        if len(ids) - l3_count != row["exact_fiber_non_length_three_count"]:
            raise AssertionError("per-source non-length-three count drift")
        if int(row["selected_sigma5_length"]) == 3:
            raise AssertionError("selected source receipt has length three")
    for context in menus["contexts"]:
        for channel in context["channels"]:
            ids = [str(value) for value in channel["exact_lift_ids"]]
            histogram = {
                str(length): count
                for length, count in sorted(
                    Counter(exact_lengths[receipt_id] for receipt_id in ids).items()
                )
            }
            if histogram != channel["exact_lift_length_histogram"]:
                raise AssertionError("per-channel exact-fiber length spectrum drift")
            l3_count = sum(exact_lengths[receipt_id] == 3 for receipt_id in ids)
            if l3_count != channel["length_three_exact_lift_count"]:
                raise AssertionError("per-channel length-three count drift")
            if len(ids) - l3_count != channel["non_length_three_exact_lift_count"]:
                raise AssertionError("per-channel non-length-three count drift")
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
        raise AssertionError("stored fifth rank-five candidate differs from replay")
    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fifth rank-five receipt schema")
    expected_receipt = build_receipt(
        selection_path=args.selection,
        lower_section_path=args.lower_section,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fifth rank-five receipt is stale")
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
                "selected_non_length_three_receipts": construction["exact_lifts"][
                    "selected_sigma5_receipt_count"
                ],
                "selected_sigma5_length_histogram": construction["exact_lifts"][
                    "selected_sigma5_length_histogram"
                ],
                "exact_fiber_length_histogram": construction["exact_lifts"][
                    "exact_fiber_length_histogram"
                ],
                "good_5_evaluation": "NOT_RUN",
                "good_5_non3_evaluation": "NOT_RUN",
                "internal_boundaries_exported_as_checkpoints": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
