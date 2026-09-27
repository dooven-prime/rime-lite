#!/usr/bin/env python3
"""Replay the P28.5l three-realization invariant audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from paper28_three_realization_invariant_audit import (
    DEFAULT_OUTPUT,
    RECEIPT_SCHEMA,
    SCHEMA,
    _paths_from_args,
    add_input_arguments,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED_THIRD = {
    "rank4_menu_max": 7,
    "rank4_channels": [171, 1],
    "rank4_lifts": [4208, 1031],
    "rank5_channels": [36, 34],
    "rank5_lifts": [36, 173],
    "handoff": {"IDENTITY": 36},
    "fusion": [[1, 2]],
    "length": [[3]],
    "surplus": [2],
    "incoming_participation": ["NONE"],
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
    return json.loads(path.read_text(encoding="ascii"))


def _assert_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected P28.5l schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("P28.5l content digest mismatch")
    if payload["scope"] != {
        "ambient_n": 7,
        "realization_count": 3,
        "new_oracle_evaluation": False,
        "fourth_candidate_selected": False,
    }:
        raise AssertionError("P28.5l scope drift")

    third = payload["realizations"]["third"]
    observed = {
        "rank4_menu_max": third["rank4"]["menu_max"],
        "rank4_channels": [
            third["rank4"]["successful_channel_count"],
            third["rank4"]["failed_channel_count"],
        ],
        "rank4_lifts": [
            third["rank4"]["successful_exact_lift_count"],
            third["rank4"]["failed_exact_lift_count"],
        ],
        "rank5_channels": [
            third["rank5"]["successful_channel_count"],
            third["rank5"]["failed_channel_count"],
        ],
        "rank5_lifts": [
            third["rank5"]["successful_exact_lift_count"],
            third["rank5"]["failed_exact_lift_count"],
        ],
        "handoff": third["rank5"]["handoff_type_histogram"],
        "fusion": third["rank5"]["successful_fusion_parent_masses"],
        "length": third["rank5"]["successful_lengths"],
        "surplus": third["rank5"]["successful_total_surpluses"],
        "incoming_participation": third["rank5"][
            "incoming_distinguished_participation"
        ],
    }
    if observed != EXPECTED_THIRD:
        raise AssertionError(f"P28.5l third realization drift: {observed!r}")
    if not all(payload["contract_audit"].values()):
        raise AssertionError("P28.5l common contract audit failed")

    conclusions = payload["derived_conclusions"]
    for field in (
        "fusion_1_plus_1_is_necessary",
        "zero_surplus_is_necessary",
        "kernel_mass_0_2_is_necessary",
        "nonidentity_handoff_is_universal",
        "add_F6_handoff_contract",
        "menu_size_bound_claimed",
    ):
        if conclusions[field]:
            raise AssertionError(f"P28.5l incorrectly promoted {field}")
    for field in (
        "generator_vocabulary_survives_all_three",
        "length_three_common_but_unproved",
        "incoming_distinguished_unused_common_but_unproved",
        "typed_observable_preservation_required",
    ):
        if not conclusions[field]:
            raise AssertionError(f"P28.5l lost frozen conclusion {field}")
    if payload["F3_decision"]["schema_change"] != "NONE_KEEP_WITHIN_F3":
        raise AssertionError("P28.5l F3/F6 decision drift")
    if payload["remaining_hostile_targets"]["fourth_candidate_status"] != "NOT_SELECTED":
        raise AssertionError("P28.5l unexpectedly selected a fourth carrier")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_input_arguments(parser)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    paths = _paths_from_args(args)

    stored = _load(args.artifact)
    recomputed = build_payload(paths)
    _assert_payload(stored)
    _assert_payload(recomputed)
    if stored != recomputed:
        raise AssertionError("stored P28.5l artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = _load(receipt_path)
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected P28.5l receipt schema")
    expected_receipt = build_receipt(paths=paths, output=args.artifact, payload=stored)
    if stored_receipt != expected_receipt:
        raise AssertionError("stored P28.5l receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "realizations": 3,
                "one_plus_one_necessary": False,
                "zero_surplus_necessary": False,
                "kernel_mass_0_2_necessary": False,
                "remaining_common_anatomy": stored["remaining_hostile_targets"][
                    "common_unproved_anatomy"
                ],
                "fourth_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
