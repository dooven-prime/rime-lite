#!/usr/bin/env python3
"""Validate the A1 exact signed-route result and its byte closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


FOLLOWUPS = Path(__file__).resolve().parents[1]
DESIGN = FOLLOWUPS / "y_known_pm_route_audit.design-v1.json"
REGISTRATION = FOLLOWUPS / "y_known_pm_route_audit.registration-v1.2.json"
RESULT = FOLLOWUPS / "results" / "y_known_pm_route_audit.v1.json"
RECEIPT = FOLLOWUPS / "results" / "y_known_pm_route_audit.v1.validation-receipt.json"


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
    failures: list[str] = []
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    if result.get("status") != "COMPLETED":
        failures.append("result is not complete")
    if result.get("outcome") not in design.get("outcomes", []):
        failures.append("result outcome is outside the design ontology")
    if result.get("design", {}).get("sha256") != sha256_file(DESIGN):
        failures.append("result design binding mismatch")
    if result.get("registration", {}).get("sha256") != sha256_file(REGISTRATION):
        failures.append("result registration binding mismatch")
    producer_path = FOLLOWUPS / registration.get("producer", {}).get("path", "")
    if not producer_path.is_file() or sha256_file(producer_path) != registration.get(
        "producer", {}
    ).get("sha256"):
        failures.append("registered producer binding mismatch")
    validator_path = Path(__file__).resolve()
    if registration.get("validator", {}).get("sha256") != sha256_file(validator_path):
        failures.append("registered validator binding mismatch")

    content = dict(result)
    declared_content = content.pop("result_content_sha256", None)
    if declared_content != canonical_sha256(content):
        failures.append("result canonical content digest mismatch")
    if result.get("exact_arithmetic", {}).get("floating_nonzero_tolerance_used") is not False:
        failures.append("result admits a floating nonzero threshold")
    if set(result.get("fields", {})) != set(design.get("sector_fields", [])):
        failures.append("result does not cover every registered sector field")

    for field in design.get("sector_fields", []):
        field_result = result.get("fields", {}).get(field, {})
        for depth in design.get("depths", []):
            depth_result = field_result.get("depths", {}).get(str(depth), {})
            records = depth_result.get("records", [])
            counts = depth_result.get("classification_counts", {})
            if len(records) != depth_result.get("macro_word_count"):
                failures.append(f"{field} depth {depth} record count mismatch")
            for status in design["classification"]["statuses"]:
                actual = sum(record.get("status") == status for record in records)
                if counts.get(status) != actual:
                    failures.append(f"{field} depth {depth} status count mismatch: {status}")
            for record in records:
                if record.get("status") == "EXACT_NONZERO_PROJECTED_PRODUCT":
                    certificate = record.get("modular_certificate", {})
                    if not certificate.get("residue"):
                        failures.append(f"{field} depth {depth} lacks nonzero exact residue")

    closure = [
        {"role": "DESIGN", "path": DESIGN.name, "sha256": sha256_file(DESIGN)},
        {
            "role": "REGISTRATION",
            "path": REGISTRATION.name,
            "sha256": sha256_file(REGISTRATION),
        },
        {
            "role": "PRODUCER",
            "path": producer_path.name,
            "sha256": sha256_file(producer_path),
        },
        {
            "role": "VALIDATOR",
            "path": f"validation/{validator_path.name}",
            "sha256": sha256_file(validator_path),
        },
        {
            "role": "RESULT",
            "path": "results/y_known_pm_route_audit.v1.json",
            "sha256": sha256_file(RESULT),
        },
    ]
    receipt = {
        "schema": "rime.exploratory.malecns-y-known-pm-route-audit-validation.v1",
        "status": "PASS" if not failures else "FAIL",
        "validation_mode": "LOCAL_CLOSURE_AND_CERTIFICATE_STRUCTURE_VERIFICATION",
        "independent_validation": False,
        "producer_replay_performed": False,
        "experiment_executed_by_validator": False,
        "outcome": result.get("outcome"),
        "ordered_closure": closure,
        "closure_sha256": canonical_sha256(closure),
        "receipt_in_own_closure": False,
        "failures": failures,
        "claim_boundary": "exact result/closure validation; not independent mathematical validation and not a biological claim",
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
