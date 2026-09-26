#!/usr/bin/env python3
"""Replay the P28.5g cross-realization invariant audit."""

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

from paper28_cross_realization_invariant_audit import (
    DEFAULT_OUTPUT,
    RECEIPT_SCHEMA,
    SCHEMA,
    _paths_from_args,
    add_input_arguments,
    build_payload,
    build_receipt,
    default_receipt_path,
)


EXPECTED = {
    "first_rank4_menu_max": 8,
    "second_rank4_menu_max": 11,
    "first_rank4_channels": [169, 4],
    "second_rank4_channels": [401, 0],
    "first_rank5_channels": [35, 52],
    "second_rank5_channels": [48, 48],
    "first_rank5_lifts": [35, 179],
    "second_rank5_lifts": [48, 147],
    "first_handoff": {"ATOM_BIJECTION": 35},
    "second_handoff": {"IDENTITY": 48},
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
        raise AssertionError("unexpected P28.5g schema")
    content = dict(payload)
    observed_digest = content.pop("content_sha256")
    if observed_digest != _digest(content):
        raise AssertionError("P28.5g content digest mismatch")
    if payload["scope"]["new_oracle_evaluation"]:
        raise AssertionError("P28.5g unexpectedly ran a new oracle")
    if payload["scope"]["third_candidate_selected"]:
        raise AssertionError("P28.5g unexpectedly selected a third candidate")

    first = payload["realizations"]["first"]
    second = payload["realizations"]["second"]
    observed = {
        "first_rank4_menu_max": first["rank4"]["menu_max"],
        "second_rank4_menu_max": second["rank4"]["menu_max"],
        "first_rank4_channels": [
            first["rank4"]["successful_channel_count"],
            first["rank4"]["failed_channel_count"],
        ],
        "second_rank4_channels": [
            second["rank4"]["successful_channel_count"],
            second["rank4"]["failed_channel_count"],
        ],
        "first_rank5_channels": [
            first["rank5"]["successful_channel_count"],
            first["rank5"]["failed_channel_count"],
        ],
        "second_rank5_channels": [
            second["rank5"]["successful_channel_count"],
            second["rank5"]["failed_channel_count"],
        ],
        "first_rank5_lifts": [
            first["rank5"]["successful_exact_lift_count"],
            first["rank5"]["failed_exact_lift_count"],
        ],
        "second_rank5_lifts": [
            second["rank5"]["successful_exact_lift_count"],
            second["rank5"]["failed_exact_lift_count"],
        ],
        "first_handoff": first["rank5"]["handoff_type_histogram"],
        "second_handoff": second["rank5"]["handoff_type_histogram"],
    }
    if observed != EXPECTED:
        raise AssertionError(f"P28.5g frozen facts drifted: {observed!r}")
    if not all(payload["contract_audit"].values()):
        raise AssertionError("a common F1--F5 discipline check failed")
    conclusions = payload["derived_conclusions"]
    if conclusions["menu_size_le_8_survives"]:
        raise AssertionError("P28.5g failed to reject menu size <= 8")
    if conclusions["nonidentity_handoff_is_universal"]:
        raise AssertionError("P28.5g incorrectly promoted nonidentity handoff")
    if conclusions["add_F6_handoff_contract"]:
        raise AssertionError("P28.5g incorrectly added F6")
    if not conclusions["typed_observable_preservation_required"]:
        raise AssertionError("P28.5g lost typed observable preservation")
    if payload["F3_refinement"]["schema_change"] != "NONE_KEEP_WITHIN_F3":
        raise AssertionError("P28.5g F3/F6 decision drift")


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
        raise AssertionError("stored P28.5g artifact differs from replay")

    receipt_path = args.receipt or default_receipt_path(args.artifact)
    stored_receipt = _load(receipt_path)
    if stored_receipt.get("schema") != RECEIPT_SCHEMA:
        raise AssertionError("unexpected P28.5g receipt schema")
    expected_receipt = build_receipt(
        paths=paths,
        output=args.artifact,
        payload=stored,
    )
    if stored_receipt != expected_receipt:
        raise AssertionError("stored P28.5g receipt is stale")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.artifact.as_posix(),
                "artifact_sha256": _sha256(args.artifact),
                "receipt": receipt_path.as_posix(),
                "receipt_binding": "PASS",
                "menu_size_le_8_survives": False,
                "common_generator_vocabulary": (
                    stored["realizations"]["first"]["rank5"][
                        "generator_vocabulary"
                    ]
                ),
                "first_handoff": EXPECTED["first_handoff"],
                "second_handoff": EXPECTED["second_handoff"],
                "F3_decision": stored["F3_refinement"]["schema_change"],
                "third_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
