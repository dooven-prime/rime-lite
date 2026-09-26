#!/usr/bin/env python3
"""Validate the 165-context tagged fixed-scope mechanism cover."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import paper28_close_fixed_scope_mechanism_cover as producer

ARTIFACT = producer.DEFAULT_OUTPUT
RECEIPT = producer.default_receipt_path(ARTIFACT)
EXPECTED = {
    "source_count": 165,
    "completed_source_count": 165,
    "channel_count": 1051,
    "returning_channel_count": 1046,
    "nonreturning_channel_count": 5,
    "mixed_channel_count": 186,
    "mixed_source_count": 86,
    "exact_lift_count": 26995,
    "local_return_exact_lift_count": 23177,
    "nonreturning_exact_lift_count": 3818,
    "certified_target_context_count": 3162,
}


def _load_gzip(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    artifact = _load_gzip(ARTIFACT)
    rebuilt = producer.build_payload(
        gfpc_path=producer.DEFAULT_GFPC, pec_path=producer.DEFAULT_PEC
    )
    if artifact != rebuilt:
        raise AssertionError("mechanism-cover artifact differs from replay")
    if artifact["schema"] != producer.SCHEMA:
        raise AssertionError("mechanism-cover schema drift")
    if not artifact["theorem"]["holds"]:
        raise AssertionError("165-context cover theorem failed")

    cover = artifact["reduced_sufficient_cover"]
    if cover["schemas"] != ["GFPC", "PEC"]:
        raise AssertionError("reduced sufficient family drift")
    if cover["minimality_claimed"]:
        raise AssertionError("closure incorrectly claims minimality")
    if cover["historical_declared_family_preserved"] != [
        "OW",
        "FPC",
        "PEC",
        "GFPC",
    ]:
        raise AssertionError("declaration history was not preserved")
    rows = cover["G_red_fs"]
    if len(rows) != 165:
        raise AssertionError("reduced good relation size drift")
    if len(
        {
            (row["carrier_id"], row["context_id"], row["kappa_4_ISE_id"])
            for row in rows
        }
    ) != 165:
        raise AssertionError("reduced tagged provenance keys are not unique")
    if {
        row["carrier_id"]: row["mechanism"] for row in rows
    } != producer.ASSIGNMENT:
        raise AssertionError("carrier-to-mechanism assignment drift")

    aggregate = artifact["evaluation_summary"]["aggregate"]
    for key, value in EXPECTED.items():
        if aggregate[key] != value:
            raise AssertionError(f"aggregate drift for {key}")
    scope = artifact["scope"]
    if scope["new_oracle_opened"] or scope["component_evaluator_rerun"]:
        raise AssertionError("closure reran a component evaluator")
    if scope["winner_selected"] or scope["all_n_claim"]:
        raise AssertionError("closure crossed its quantifier/scope boundary")

    receipt = json.loads(RECEIPT.read_text(encoding="ascii"))
    if receipt["schema"] != producer.RECEIPT_SCHEMA:
        raise AssertionError("mechanism-cover receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("mechanism-cover receipt hash mismatch")
    if receipt["artifact"]["content_sha256"] != artifact["content_sha256"]:
        raise AssertionError("mechanism-cover receipt content mismatch")
    if receipt["artifact"]["frozen_closure_input_sha256"] != artifact[
        "frozen_closure_input_sha256"
    ]:
        raise AssertionError("mechanism-cover frozen-input binding drift")
    expected_receipt = producer.build_receipt(
        output=ARTIFACT,
        payload=artifact,
        input_paths=[producer.DEFAULT_GFPC, producer.DEFAULT_PEC],
    )
    if receipt != expected_receipt:
        raise AssertionError("mechanism-cover receipt closure drift")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                "frozen_closure_input_sha256": artifact[
                    "frozen_closure_input_sha256"
                ],
                "theorem_holds": True,
                "reduced_sufficient_cover": ["GFPC", "PEC"],
                "minimality_claimed": False,
                **EXPECTED,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
