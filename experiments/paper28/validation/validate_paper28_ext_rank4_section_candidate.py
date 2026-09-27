#!/usr/bin/env python3
"""Validate the success-free extremal rank-four relation adapter."""

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

import paper28_prepare_ext_rank4_section_candidate as producer

ARTIFACT = producer.DEFAULT_OUTPUT
RECEIPT = producer.default_receipt_path(ARTIFACT)


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
        catalog_path=producer.DEFAULT_CATALOG,
        factorization_path=producer.DEFAULT_FACTORIZATION,
    )
    if artifact != rebuilt:
        raise AssertionError("ext adapter differs from deterministic replay")
    if artifact["schema"] != producer.SCHEMA:
        raise AssertionError("ext adapter schema drift")
    if artifact["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("ext adapter contains a Good_4 evaluation")
    if artifact["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("ext evaluator is not absent")

    construction = artifact["construction"]
    menus = construction["menus"]
    lifts = construction["exact_lifts"]
    expected = {
        "context_count": 35,
        "channel_count": 173,
        "exact_lift_count": 4182,
        "max_menu_size": 8,
    }
    for key, value in expected.items():
        if menus[key] != value:
            raise AssertionError(f"ext menu drift for {key}")
    if lifts["receipt_count"] != 4182:
        raise AssertionError("ext exact relation size drift")
    if any("observables" in row for row in lifts["receipts"]):
        raise AssertionError("outcome observables leaked into ext relation")

    receipt_ids = {str(row["receipt_id"]) for row in lifts["receipts"]}
    menu_ids = {
        str(receipt_id)
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    }
    if receipt_ids != menu_ids:
        raise AssertionError("ext menu/exact-lift identity drift")
    if producer._digest(construction) != artifact[
        "construction_payload_sha256"
    ]:
        raise AssertionError("ext construction digest mismatch")

    receipt = json.loads(RECEIPT.read_text(encoding="ascii"))
    if receipt["schema"] != producer.RECEIPT_SCHEMA:
        raise AssertionError("ext adapter receipt schema drift")
    if receipt["artifact"]["sha256"] != _sha256(ARTIFACT):
        raise AssertionError("ext adapter receipt artifact hash mismatch")
    expected_receipt = producer.build_receipt(
        output=ARTIFACT,
        payload=artifact,
        input_paths=[
            producer.DEFAULT_CATALOG,
            producer.DEFAULT_FACTORIZATION,
        ],
    )
    if receipt != expected_receipt:
        raise AssertionError("ext adapter receipt closure drift")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT.as_posix(),
                "artifact_sha256": _sha256(ARTIFACT),
                **expected,
                "outcome_observables_in_relation": 0,
                "good_4_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
