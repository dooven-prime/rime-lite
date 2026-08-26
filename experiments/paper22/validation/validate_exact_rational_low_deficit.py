#!/usr/bin/env python3
"""Validate and exactly replay the rational low-deficit certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PAPER_DIR = Path(__file__).resolve().parents[1]
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from exact_rational_low_deficit import (
    DEFAULT_HOSTILE_OUTPUT,
    DEFAULT_OUTPUT,
    ROOT,
    build_exact_certificate,
    build_p23_hostile_fixture,
    canonical_json,
    content_digest,
    file_digest,
)


DEFAULT_RECEIPT = DEFAULT_OUTPUT.with_name(
    "exact_rational_low_deficit_k8_v1.validation-receipt.json"
)


def load_checked(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != schema:
        raise ValueError(f"unexpected schema for {path}")
    if payload.get("content_sha256") != content_digest(payload):
        raise ValueError(f"content digest mismatch for {path}")
    return payload


def relative_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def validate(certificate_path: Path, hostile_path: Path) -> tuple[dict[str, Any], list[str]]:
    certificate = load_checked(
        certificate_path, "paper.route-profiles.exact-rational-low-deficit.v1"
    )
    hostile = load_checked(
        hostile_path, "paper.route-profiles.p23-global-registry-hostile.v1"
    )
    checks: list[str] = []

    max_deficit = int(certificate["max_deficit"])
    replayed_certificate = build_exact_certificate(max_deficit)
    if replayed_certificate != certificate:
        raise ValueError("exact rational certificate does not match replay")
    checks.append("exact rational state and transition replay")

    replayed_hostile = build_p23_hostile_fixture(replayed_certificate, max_deficit)
    if replayed_hostile != hostile:
        raise ValueError("p=23 hostile fixture does not match replay")
    checks.append("p=23 reduction and finite-field BFS replay")

    expected_layers = [1, 2, 3, 7, 19, 56, 174, 561, 1859]
    actual_layers = [
        int(certificate["layer_counts"][str(level)])
        for level in range(max_deficit + 1)
    ]
    if max_deficit != 8 or actual_layers != expected_layers:
        raise ValueError("unexpected rational low-deficit layer sequence")
    checks.append("declared C_0 through C_8 cardinalities")

    if certificate["transition_closure"] != {
        "in_range_transition_count": 6759,
        "monotonicity_check": True,
        "outside_transition_count": 1287,
        "status": "CLOSED_THROUGH_MAX_DEFICIT",
    }:
        raise ValueError("unexpected transition closure summary")
    checks.append("deficit monotonicity and transition closure")

    state_registry = certificate["global_determinant_registry"]
    guard_registry = certificate["transition_guard_determinant_registry"]
    if (state_registry["cusp_count"], state_registry["max_abs_determinant"]) != (
        320,
        987,
    ):
        raise ValueError("unexpected global state determinant registry")
    if (guard_registry["cusp_count"], guard_registry["max_abs_determinant"]) != (
        448,
        1597,
    ):
        raise ValueError("unexpected transition-guard determinant registry")
    checks.append("global state and one-step guard determinant registries")

    if not hostile["reduced_rational_layer_equals_finite_bfs_layer"]:
        raise ValueError("reduced rational layer differs from p=23 BFS layer")
    if (
        hostile["rational_exact_layer_state_count"],
        hostile["distinct_reduced_rational_state_count"],
        hostile["finite_field_bfs_exact_layer_state_count"],
    ) != (1859, 1723, 1723):
        raise ValueError("unexpected p=23 hostile layer counts")
    checks.append("p=23 1859-to-1723 global state collision")

    local = hostile["configuration_local_bound"]
    global_bound = hostile["global_registry_bound"]
    if local != {
        "conclusion": "INSUFFICIENT_FOR_CROSS_STATE_INJECTIVITY",
        "max_abs_determinant": 21,
        "prime_exceeds_bound": True,
    }:
        raise ValueError("configuration-local hostile condition changed")
    if global_bound["prime_exceeds_bound"] or global_bound["max_abs_determinant"] != 987:
        raise ValueError("global registry no longer rejects p=23")
    checks.append("configuration-local versus global-registry hostile boundary")

    collisions = hostile["witness"]["cross_state_cusp_collisions"]
    if not collisions or not all(
        row["determinant_divisible_by_23"] and row["determinant"] % 23 == 0
        for row in collisions
    ):
        raise ValueError("missing cross-state determinant collision witness")
    checks.append("explicit cross-state determinant divisibility witness")

    return {
        "schema": "paper.route-profiles.exact-rational-low-deficit-validation-receipt.v1",
        "artifact_id": "ROUTE-PROFILES-EXACT-RATIONAL-C-LE-8-REPLAY-V1",
        "receipt_kind": "LOCAL_EXACT_REPLAY_AND_SOURCE_CLOSURE_RECEIPT",
        "status": "PASS",
        "validated_artifacts": [
            {
                "uri": relative_uri(certificate_path),
                "artifact_id": certificate["artifact_id"],
                "content_sha256": certificate["content_sha256"],
                "file_sha256": file_digest(certificate_path),
            },
            {
                "uri": relative_uri(hostile_path),
                "artifact_id": hostile["artifact_id"],
                "content_sha256": hostile["content_sha256"],
                "file_sha256": file_digest(hostile_path),
            },
        ],
        "validator": {
            "uri": relative_uri(Path(__file__)),
            "sha256": file_digest(Path(__file__)),
        },
        "checks": checks,
        "validation_boundary": [
            "PASS proves exact replay agreement under the declared local source closure",
            "PASS is not an independent validation of the validator implementation",
            "the finite k<=8 certificate does not replace the general manuscript finiteness proof",
            "the sufficient determinant threshold is not claimed to be sharp",
        ],
    }, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hostile", type=Path, default=DEFAULT_HOSTILE_OUTPUT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    try:
        receipt, checks = validate(args.artifact, args.hostile)
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    receipt["content_sha256"] = content_digest(receipt)
    if args.write_receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    elif args.receipt.is_file():
        committed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if committed != receipt:
            print(f"FAIL: committed receipt drift: {args.receipt}")
            return 1
    else:
        print(f"FAIL: missing committed receipt: {args.receipt}")
        return 1
    print(f"PASS {receipt['artifact_id']}: {len(checks)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
