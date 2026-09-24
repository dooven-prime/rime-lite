#!/usr/bin/env python3
"""Validate the additive A2 named-sector follow-up closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FOLLOWUPS = Path(__file__).resolve().parents[1]
DESIGN = FOLLOWUPS / "d2_2_named_sector_followup.design-v1.json"
REGISTRATION = FOLLOWUPS / "d2_2_named_sector_followup.registration-v1.1.json"
RESULT = FOLLOWUPS / "results" / "d2_2_named_sector_followup.v1.json"
RECEIPT = FOLLOWUPS / "results" / "d2_2_named_sector_followup.v1.validation-receipt.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate() -> tuple[dict, bool]:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    failures: list[str] = []
    if result.get("status") != "COMPLETED":
        failures.append("result is not complete")
    if result.get("design", {}).get("sha256") != sha256_file(DESIGN):
        failures.append("design binding mismatch")
    if result.get("registration", {}).get("sha256") != sha256_file(REGISTRATION):
        failures.append("registration binding mismatch")
    producer = FOLLOWUPS / registration.get("producer", {}).get("path", "")
    if not producer.is_file() or sha256_file(producer) != registration.get(
        "producer", {}
    ).get("sha256"):
        failures.append("producer binding mismatch")
    if registration.get("validator", {}).get("sha256") != sha256_file(Path(__file__)):
        failures.append("validator binding mismatch")
    content = dict(result)
    declared = content.pop("result_content_sha256", None)
    if declared != canonical_sha256(content):
        failures.append("canonical result digest mismatch")

    named = result.get("typed_named", {})
    if named.get("outcome") not in design["outcomes"]["typed_named"]:
        failures.append("named outcome is outside the registered ontology")
    witness = named.get("witness")
    if named.get("outcome") == "EXACT_NAMED_SECTOR_WITNESS_FOUND":
        if not witness or witness.get("sector") == "<missing>":
            failures.append("named outcome lacks a named-sector witness")
        if not witness.get("exact_future_separation"):
            failures.append("named witness lacks exact future separation")
    missing = result.get("missing_bucket", {})
    if missing.get("outcome") != "FROZEN_CONTROL_WITNESS_RECONFIRMED":
        failures.append("frozen missing-bucket control was not reconfirmed")
    if result.get("exact_dynamics", {}).get(
        "floating_future_separation_tolerance_used"
    ) is not False:
        failures.append("follow-up uses a floating future-separation tolerance")

    closure = [
        {"role": "DESIGN", "path": DESIGN.name, "sha256": sha256_file(DESIGN)},
        {
            "role": "REGISTRATION",
            "path": REGISTRATION.name,
            "sha256": sha256_file(REGISTRATION),
        },
        {"role": "PRODUCER", "path": producer.name, "sha256": sha256_file(producer)},
        {
            "role": "VALIDATOR",
            "path": f"validation/{Path(__file__).name}",
            "sha256": sha256_file(Path(__file__)),
        },
        {
            "role": "RESULT",
            "path": "results/d2_2_named_sector_followup.v1.json",
            "sha256": sha256_file(RESULT),
        },
    ]
    receipt = {
        "schema": "rime.exploratory.digital-fly-d2-2-named-sector-followup-validation.v1",
        "status": "PASS" if not failures else "FAIL",
        "validation_mode": "LOCAL_CLOSURE_AND_CERTIFICATE_STRUCTURE_VERIFICATION",
        "independent_validation": False,
        "producer_replay_performed": False,
        "experiment_executed_by_validator": False,
        "typed_named_outcome": named.get("outcome"),
        "missing_bucket_outcome": missing.get("outcome"),
        "ordered_closure": closure,
        "closure_sha256": canonical_sha256(closure),
        "receipt_in_own_closure": False,
        "failures": failures,
        "claim_boundary": design["claim_boundary"],
    }
    return receipt, not failures


def main() -> None:
    receipt, passed = validate()
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
