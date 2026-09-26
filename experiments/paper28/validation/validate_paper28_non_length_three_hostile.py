#!/usr/bin/env python3
"""Replay the P28.5s non-length-three hostile selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_select_non_length_three_hostile import (
    DEFAULT_FEASIBILITY,
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_REFERENCE_RETURN,
    DEFAULT_REFERENCE_SELECTION,
    RECEIPT_SCHEMA,
    SCHEMA,
    _digest,
    _load,
    _sha256,
    build_payload,
    build_receipt,
    default_receipt_path,
)

EXPECTED = {
    "selection_status": "UNIQUE_SOURCE_LOCAL_MINIMIZER",
    "eligible_cell_count": 142,
    "eligible_context_count": 5032,
    "preferred_cell_count": 66,
    "preferred_context_count": 723,
    "minimum_geometry_distance": 1,
    "geometry_minimizer_count": 1,
    "minimum_gross_gain_distance": 0,
    "accounting_minimizer_count": 1,
    "minimum_placement_distance": 4,
    "finalist_count": 1,
    "context_count": 10,
}

EXPECTED_SIGNATURE = {
    "binary_kernel_mass_multiset": [0, 3],
    "cyclic_offsets_F4_to_kernel": [0, 6],
    "family": "22111__12_TO_3211",
    "fusion_contains_inherited_fresh": True,
    "fusion_parent_sizes": [1, 2],
    "rank4_partition": [3, 2, 1, 1],
    "rank5_partition": [2, 2, 1, 1, 1],
    "sigma5_length": 5,
    "sigma5_surplus": 0,
}


def _assert_payload(payload: dict) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected P28.5s schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("P28.5s content digest mismatch")
    scope = payload["scope"]
    if scope["evaluation_status"] != "NOT_RUN":
        raise AssertionError("P28.5s contains a return evaluation")
    if scope["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("P28.5s granted section authority")
    if scope["winner_selected"]:
        raise AssertionError("P28.5s selected a winner")

    candidate = payload["candidate"]
    observed = {
        "selection_status": candidate["selection_status"],
        "eligible_cell_count": candidate["eligible_signature_cell_count"],
        "eligible_context_count": candidate["eligible_context_count"],
        "preferred_cell_count": candidate["preferred_signature_cell_count"],
        "preferred_context_count": candidate["preferred_context_count"],
        "minimum_geometry_distance": candidate["minimum_geometry_distance"],
        "geometry_minimizer_count": candidate["geometry_minimizer_count"],
        "minimum_gross_gain_distance": candidate["minimum_gross_gain_distance"],
        "accounting_minimizer_count": candidate["accounting_minimizer_count"],
        "minimum_placement_distance": candidate[
            "minimum_action_relative_placement_distance"
        ],
        "finalist_count": candidate["finalist_count"],
        "context_count": candidate["context_count"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"P28.5s selection drift: {observed!r}")
    if candidate["accounting_control"]["surplus_compared_independently"]:
        raise AssertionError("P28.5s incorrectly treats surplus independently")
    if candidate["finalists"][0]["signature"] != EXPECTED_SIGNATURE:
        raise AssertionError("P28.5s finalist signature drift")
    if candidate["finalists"][0]["gross_maturity_gain"] != 5:
        raise AssertionError("P28.5s finalist gross maturity gain drift")
    for finalist in candidate["finalists"]:
        signature = finalist["signature"]
        if signature["fusion_contains_inherited_fresh"] is not True:
            raise AssertionError("P28.5s finalist avoids inherited ancestry")
        if signature["sigma5_length"] == 3:
            raise AssertionError("P28.5s finalist did not break length three")
        if signature["fusion_parent_sizes"] != [1, 2]:
            raise AssertionError("P28.5s finalist left the preferred 1+2 family")
        if finalist["gross_maturity_gain"] != (
            signature["sigma5_length"] + signature["sigma5_surplus"]
        ):
            raise AssertionError("P28.5s gross-gain calculation drift")
    if payload["candidate_payload_sha256"] != _digest(candidate):
        raise AssertionError("P28.5s candidate digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--feasibility", type=Path, default=DEFAULT_FEASIBILITY)
    parser.add_argument(
        "--reference-selection", type=Path, default=DEFAULT_REFERENCE_SELECTION
    )
    parser.add_argument(
        "--reference-return", type=Path, default=DEFAULT_REFERENCE_RETURN
    )
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    stored = _load(args.artifact)
    recomputed = build_payload(
        args.input,
        args.feasibility,
        args.reference_selection,
        args.reference_return,
    )
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored P28.5s artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected P28.5s receipt schema")
    expected_receipt = build_receipt(
        input_path=args.input,
        feasibility_path=args.feasibility,
        reference_selection_path=args.reference_selection,
        reference_return_path=args.reference_return,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored P28.5s receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                **EXPECTED,
                "evaluation_status": "NOT_RUN",
                "section_authority": "NOT_GRANTED",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
