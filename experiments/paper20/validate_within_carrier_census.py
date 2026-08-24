"""Validate the exact Paper XX shared-carrier obstruction census."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.paper20.within_carrier_census import (  # noqa: E402
    ARTIFACT_ID,
    DEFAULT_OUTPUT,
    SCHEMA,
    build_payload,
    canonical_json,
    content_digest,
)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA or payload.get("artifact_id") != ARTIFACT_ID:
        errors.append("schema or artifact identity mismatch")
    if payload.get("content_sha256") != content_digest(payload):
        errors.append("content digest mismatch")
    if payload.get("claim_status") != "Computational Certificate":
        errors.append("claim status mismatch")
    if payload.get("arithmetic") != "exact_integer_permutation_and_projector_matrices":
        errors.append("arithmetic boundary mismatch")

    model = payload.get("model", {})
    if model.get("carrier_count") != 1:
        errors.append("model must have exactly one carrier")
    if model.get("sector_carrier_supports") != [["b"], ["b"], ["b"]]:
        errors.append("every sector must share the sole carrier")

    enumeration = payload.get("enumeration", {})
    if enumeration.get("total_labelled_route_count") != 108:
        errors.append("complete labelled route count mismatch")
    candidate_count = enumeration.get("support_candidate_count")
    active_count = enumeration.get("active_product_count")
    obstruction_count = enumeration.get("strict_within_carrier_obstruction_count")
    if not isinstance(candidate_count, int) or not isinstance(active_count, int):
        errors.append("candidate or active count is not an integer")
    elif candidate_count != active_count + obstruction_count:
        errors.append("candidate partition mismatch")
    if not isinstance(obstruction_count, int) or obstruction_count < 1:
        errors.append("strict within-carrier obstruction census is empty")
    if enumeration.get("disjoint_endpoint_carrier_obstruction_count") != 0:
        errors.append("shared-carrier census was contaminated by disjoint supports")

    obstructions = enumeration.get("obstructions", [])
    if len(obstructions) != obstruction_count:
        errors.append("obstruction ledger length mismatch")
    for row in obstructions:
        if row.get("endpoint_carrier_intersection") != ["b"]:
            errors.append("obstruction lacks shared endpoint carrier support")
        if row.get("incoming_rank", 0) < 1 or row.get("outgoing_rank", 0) < 1:
            errors.append("obstruction contains a zero adjacent factor")
        if row.get("product_rank") != 0:
            errors.append("obstruction product is not exactly zero")
        if row.get("mechanism") != "STRICT_WITHIN_CARRIER_IMAGE_KERNEL_CONTAINMENT":
            errors.append("obstruction mechanism mismatch")

    witness = {
        "source": 0,
        "middle": 1,
        "target": 2,
        "first_label": "g01",
        "second_label": "h23",
    }
    if witness not in [row.get("route") for row in obstructions]:
        errors.append("declared strict shared-carrier witness is missing")

    try:
        rebuilt = build_payload()
    except Exception as exc:  # fail closed at the validator boundary
        errors.append(f"producer replay failed: {exc}")
    else:
        if canonical_json(rebuilt) != canonical_json(payload):
            errors.append("full exact producer replay mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    errors = validate(args.artifact)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    payload = json.loads(args.artifact.read_text(encoding="utf-8"))
    count = payload["enumeration"]["strict_within_carrier_obstruction_count"]
    print(f"PASS {payload['artifact_id']}: {count} exact shared-carrier obstructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
