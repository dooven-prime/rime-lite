#!/usr/bin/env python3
"""Replay ordinary and fresh-consuming Good_5 for the fourth relation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_evaluate_fourth_rank5_section_return import (
    DEFAULT_CANDIDATE,
    DEFAULT_LOWER_SECTION,
    DEFAULT_OUTPUT,
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
    "exact_lift_count": 252,
    "ordinary_successful_source_count": 36,
    "ordinary_hostile_source_count": 0,
    "consume_successful_source_count": 36,
    "consume_hostile_source_count": 0,
    "ordinary_successful_channel_count": 36,
    "ordinary_failed_channel_count": 71,
    "consume_successful_channel_count": 36,
    "consume_failed_channel_count": 71,
    "ordinary_successful_exact_lift_count": 36,
    "ordinary_unsuccessful_exact_lift_count": 216,
    "fresh_consuming_successful_exact_lift_count": 36,
    "fresh_avoiding_successful_exact_lift_count": 0,
    "selected_sigma5_ordinary_success_count": 36,
    "selected_sigma5_consume_success_count": 36,
    "ordinary_histogram": {"1": 36},
    "consume_histogram": {"1": 36},
    "handoff_histogram": {"IDENTITY": 36},
    "consume_handoff_histogram": {"IDENTITY": 36},
    "cross_table": {
        "fresh_avoided": {
            "target_in_lower_section": 0,
            "target_outside_lower_section": 73,
        },
        "fresh_consumed": {
            "target_in_lower_section": 36,
            "target_outside_lower_section": 143,
        },
    },
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected fourth rank-five evaluation schema")
    scope = payload["scope"]
    evaluation = payload["evaluation"]
    observed = {
        "source_context_count": scope["source_context_count"],
        "channel_count": evaluation["channel_count"],
        "exact_lift_count": evaluation["exact_lift_count"],
        "ordinary_successful_source_count": evaluation[
            "ordinary_successful_source_count"
        ],
        "ordinary_hostile_source_count": evaluation["ordinary_hostile_source_count"],
        "consume_successful_source_count": evaluation[
            "consume_successful_source_count"
        ],
        "consume_hostile_source_count": evaluation["consume_hostile_source_count"],
        "ordinary_successful_channel_count": evaluation[
            "ordinary_successful_channel_count"
        ],
        "ordinary_failed_channel_count": evaluation["ordinary_failed_channel_count"],
        "consume_successful_channel_count": evaluation[
            "consume_successful_channel_count"
        ],
        "consume_failed_channel_count": evaluation["consume_failed_channel_count"],
        "ordinary_successful_exact_lift_count": evaluation[
            "ordinary_successful_exact_lift_count"
        ],
        "ordinary_unsuccessful_exact_lift_count": evaluation[
            "ordinary_unsuccessful_exact_lift_count"
        ],
        "fresh_consuming_successful_exact_lift_count": evaluation[
            "fresh_consuming_successful_exact_lift_count"
        ],
        "fresh_avoiding_successful_exact_lift_count": evaluation[
            "fresh_avoiding_successful_exact_lift_count"
        ],
        "selected_sigma5_ordinary_success_count": evaluation[
            "selected_sigma5_ordinary_success_count"
        ],
        "selected_sigma5_consume_success_count": evaluation[
            "selected_sigma5_consume_success_count"
        ],
        "ordinary_histogram": evaluation["ordinary_good_channel_count_histogram"],
        "consume_histogram": evaluation["consume_good_channel_count_histogram"],
        "handoff_histogram": evaluation["handoff_type_histogram"],
        "consume_handoff_histogram": evaluation["consume_handoff_type_histogram"],
        "cross_table": evaluation["exact_lift_cross_table"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"fourth rank-five evaluation drift: {observed!r}")
    if scope["winner_selected"] or scope["menu_or_lift_rebuilt"]:
        raise AssertionError("evaluator changed the frozen quantifier boundary")
    if (
        evaluation["ordinary_successful_source_count"]
        + evaluation["ordinary_hostile_source_count"]
        != 36
    ):
        raise AssertionError("ordinary source partition drift")
    if (
        evaluation["consume_successful_source_count"]
        + evaluation["consume_hostile_source_count"]
        != 36
    ):
        raise AssertionError("consume source partition drift")
    if (
        evaluation["ordinary_successful_channel_count"]
        + evaluation["ordinary_failed_channel_count"]
        != evaluation["channel_count"]
    ):
        raise AssertionError("ordinary channel partition drift")
    if (
        evaluation["consume_successful_channel_count"]
        + evaluation["consume_failed_channel_count"]
        != evaluation["channel_count"]
    ):
        raise AssertionError("consume channel partition drift")
    if (
        evaluation["ordinary_successful_exact_lift_count"]
        + evaluation["ordinary_unsuccessful_exact_lift_count"]
        != evaluation["exact_lift_count"]
    ):
        raise AssertionError("ordinary exact-lift partition drift")
    if (
        evaluation["fresh_consuming_successful_exact_lift_count"]
        + evaluation["fresh_avoiding_successful_exact_lift_count"]
        != evaluation["ordinary_successful_exact_lift_count"]
    ):
        raise AssertionError("successful fresh-participation split drift")
    if (
        sum(sum(row.values()) for row in evaluation["exact_lift_cross_table"].values())
        != evaluation["exact_lift_count"]
    ):
        raise AssertionError("cross table does not cover exact lifts")
    if evaluation["all_sources_have_ordinary_good_channel"] != (
        evaluation["ordinary_hostile_source_count"] == 0
    ):
        raise AssertionError("ordinary all-sources flag drift")
    if evaluation["all_sources_have_consume_good_channel"] != (
        evaluation["consume_hostile_source_count"] == 0
    ):
        raise AssertionError("consume all-sources flag drift")

    authority = payload["certified_source_section"]
    if evaluation["all_sources_have_ordinary_good_channel"]:
        if (
            authority["ordinary_return_authority_status"]
            != "GRANTED_BY_FIXED_SCOPE_GOOD5_EVALUATION"
        ):
            raise AssertionError("ordinary F5 success did not grant return authority")
        if authority["context_count"] != 36 or len(authority["contexts"]) != 36:
            raise AssertionError("certified fourth source section count drift")
    if evaluation["all_sources_have_consume_good_channel"]:
        if authority["fresh_consumption_claim_status"] != "PROVED_ON_FIXED_SCOPE":
            raise AssertionError("consume-hostile success was not recorded")
    else:
        if authority["fresh_consumption_claim_status"] != "FAILED_ON_HOSTILE_SOURCES":
            raise AssertionError("consume-hostile failure was not recorded")
    if payload["checkpoint_type_audit"]["internal_boundaries_exported_as_checkpoints"]:
        raise AssertionError("internal boundary exported as checkpoint")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("evaluation content digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--lower-section", type=Path, default=DEFAULT_LOWER_SECTION)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(args.candidate, args.lower_section)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored fourth rank-five evaluation differs from replay")
    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected fourth rank-five evaluation receipt schema")
    expected_receipt = build_receipt(
        candidate_path=args.candidate,
        lower_section_path=args.lower_section,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored fourth rank-five evaluation receipt is stale")
    evaluation = stored["evaluation"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "ordinary_all_sources_good": evaluation[
                    "all_sources_have_ordinary_good_channel"
                ],
                "consume_all_sources_good": evaluation[
                    "all_sources_have_consume_good_channel"
                ],
                "ordinary_successful_sources": evaluation[
                    "ordinary_successful_source_count"
                ],
                "consume_successful_sources": evaluation[
                    "consume_successful_source_count"
                ],
                "ordinary_successful_channels": evaluation[
                    "ordinary_successful_channel_count"
                ],
                "consume_successful_channels": evaluation[
                    "consume_successful_channel_count"
                ],
                "fresh_consuming_successful_lifts": evaluation[
                    "fresh_consuming_successful_exact_lift_count"
                ],
                "fresh_consumption_claim": stored["certified_source_section"][
                    "fresh_consumption_claim_status"
                ],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
