#!/usr/bin/env python3
"""Validate the finite Farey/Catalan/Fibonacci theorem certificate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PAPER_DIR = Path(__file__).resolve().parents[1]
if str(PAPER_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER_DIR))

from exact_rational_low_deficit import ROOT, content_digest, file_digest
from farey_catalan_structure import DEFAULT_OUTPUT, build


DEFAULT_RECEIPT = DEFAULT_OUTPUT.with_name(
    "farey_catalan_fibonacci_k10_v1.validation-receipt.json"
)
MANIFEST = PAPER_DIR / "evidence-manifest.json"


def relative_uri(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "paper.route-profiles.farey-catalan-fibonacci-certificate.v1":
        raise ValueError("unexpected Farey/Catalan/Fibonacci schema")
    if payload.get("content_sha256") != content_digest(payload):
        raise ValueError("Farey/Catalan/Fibonacci content digest mismatch")
    return payload


def artifact_reference(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"missing closure artifact: {path}")
    return {"uri": relative_uri(path), "sha256": file_digest(path)}


def validate_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = {
        "schema": "paper.route-profiles.farey-catalan-paper22-evidence-manifest.v1",
        "evidence_id": "PAPER22-FAREY-CATALAN-EVIDENCE-V1",
        "status": "PAPER22_RELEASE_EVIDENCE",
        "ownership": "PAPER22_INDEPENDENT_THEOREM_PACKAGE",
        "max_deficit": 10,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"evidence manifest constant changed: {key}")
    boundary = manifest.get("generation_boundary", {})
    if boundary.get("membership_logic_shared") is not False:
        raise ValueError("independent membership-generation boundary was weakened")
    artifacts = manifest.get("artifacts", [])
    roles = [row.get("role") for row in artifacts]
    paths = [row.get("path") for row in artifacts]
    if len(roles) != len(set(roles)) or len(paths) != len(set(paths)):
        raise ValueError("manifest roles and paths must be unique")
    required = {
        "theorem-manuscript",
        "reader-pdf",
        "bibliography-slice",
        "build-environment",
        "farey-catalan-producer",
        "shared-rational-transition-core",
        "exact-rational-result",
        "hostile-reduction-result",
        "exact-rational-validator",
        "farey-catalan-result",
        "farey-catalan-validator",
    }
    if set(roles) != required:
        raise ValueError("manifest artifact roles changed")
    closure = [
        {"role": row["role"], "artifact": artifact_reference(ROOT / row["path"])}
        for row in artifacts
    ]
    closure.append({"role": "evidence-manifest", "artifact": artifact_reference(MANIFEST)})
    if any(row["artifact"]["uri"].endswith("validation-receipt.json") for row in closure):
        raise ValueError("validation receipt entered its own closure")
    return manifest, closure


def validate(path: Path) -> tuple[dict[str, Any], list[str]]:
    manifest, closure = validate_manifest()
    payload = load(path)
    if payload.get("artifact_role") != (
        "FINITE_EXACT_CERTIFICATE_FOR_FAREY_CATALAN_AND_FIBONACCI_THEOREMS"
    ):
        raise ValueError("Farey/Catalan/Fibonacci artifact role changed")
    if payload.get("claim_status") != (
        "computational_certificate_supporting_manuscript_theorems"
    ):
        raise ValueError("Farey/Catalan/Fibonacci claim status changed")
    theorem_boundary = payload.get("theorem_boundary", [])
    required_boundary = {
        "the all-k anchored Farey classification is a manuscript proof, not a consequence of this finite replay",
        "the all-k Catalan enumeration is a manuscript corollary, not a sequence-fit claim",
        "the all-k Fibonacci envelope is a manuscript theorem, not a consequence of this finite replay",
    }
    if not required_boundary <= set(theorem_boundary):
        raise ValueError("manuscript-versus-certificate boundary changed")
    generated_boundary = payload.get("independent_generation_boundary", {})
    for key in ("transition_path", "anchored_boundary_path", "shared_primitives", "membership_logic_shared"):
        if generated_boundary.get(key) != manifest["generation_boundary"].get(key):
            raise ValueError(f"generated independence boundary differs from manifest: {key}")
    replayed = build(int(payload["max_deficit"]))
    if replayed != payload:
        raise ValueError("Farey/Catalan/Fibonacci certificate does not match exact replay")
    checks = ["complete exact replay through the declared maximum deficit"]

    if payload["max_deficit"] != 10:
        raise ValueError("unexpected maximum deficit")
    if [row["reachable_state_count"] for row in payload["rows"]] != [
        1,
        2,
        3,
        7,
        19,
        56,
        174,
        561,
        1859,
        6292,
        21658,
    ]:
        raise ValueError("unexpected reachable-state sequence")
    checks.append("adjacent-Catalan state sequence through deficit ten")

    for row in payload["rows"]:
        if not all(row["checks"].values()):
            raise ValueError(f"failed finite structural check at deficit {row['deficit']}")
        if row["reachable_registry_sha256"] != row["independent_candidate_registry_sha256"]:
            raise ValueError(f"registry digest mismatch at deficit {row['deficit']}")
    checks.extend(
        [
            "independently generated anchored-Farey state-set equality",
            "cyclic Farey boundary and anchor invariants",
            "three Catalan category counts",
            "Fibonacci coordinate and determinant extrema",
            "typed global and guard registry decompositions",
            "explicit Fibonacci equality witnesses",
        ]
    )

    final = payload["rows"][-1]
    if final["category_counts"] != {
        "both_anchors": 11934,
        "empty": 0,
        "negative_one_only": 4862,
        "zero_only": 4862,
    }:
        raise ValueError("unexpected deficit-ten anchor partition")
    if final["observed_extrema"] != {
        "exact_layer_max_primitive_coordinate": 89,
        "global_state_registry_max_abs_determinant": 6765,
        "max_configuration_internal_abs_determinant": 55,
        "transition_guard_registry_max_abs_determinant": 10946,
    }:
        raise ValueError("unexpected deficit-ten extremal profile")
    checks.append("deficit-ten category and extremal witness profile")

    if payload["rows"][5]["same_level_component_sizes"] != [8, 12, 12, 24]:
        raise ValueError("unexpected deficit-five same-level component profile")
    if payload["rows"][6]["same_level_component_sizes"] != [29, 29, 29, 29, 29, 29]:
        raise ValueError("unexpected deficit-six same-level component profile")
    checks.append("oriented-patch same-level component hostile profiles")
    typed = payload.get("typed_continuant_envelope_replay", {})
    if typed.get("max_depth") != 7 or not typed.get("all_checks_passed"):
        raise ValueError("typed continuant envelope replay failed")
    if len(typed.get("records", [])) != 36:
        raise ValueError("typed continuant envelope replay grid changed")
    checks.append("typed continuant envelope grid through path depth seven")
    checks.extend(
        [
            "Paper XXII-owned evidence manifest and byte closure",
            "independent transition-versus-anchored-membership generation boundary",
        ]
    )

    receipt: dict[str, Any] = {
        "schema": "paper.route-profiles.farey-catalan-fibonacci-validation-receipt.v1",
        "artifact_id": "ROUTE-PROFILES-FAREY-CATALAN-FIBONACCI-K10-REPLAY-V1",
        "receipt_kind": "LOCAL_EXACT_REPLAY_AND_SOURCE_CLOSURE_RECEIPT",
        "status": "PASS",
        "evidence_manifest": artifact_reference(MANIFEST),
        "artifact_closure": closure,
        "generation_boundary": manifest["generation_boundary"],
        "validated_artifact": {
            "uri": relative_uri(path),
            "artifact_id": payload["artifact_id"],
            "content_sha256": payload["content_sha256"],
            "file_sha256": file_digest(path),
        },
        "validator": {
            "uri": relative_uri(Path(__file__)),
            "sha256": file_digest(Path(__file__)),
        },
        "checks": checks,
        "validation_boundary": [
            "PASS proves exact finite replay agreement through deficit ten",
            "PASS does not independently prove the manuscript all-deficit Farey classification",
            "PASS does not independently prove the manuscript all-deficit Fibonacci envelope",
            "PASS is not independent validation of the validator implementation",
        ],
    }
    return receipt, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    try:
        receipt, checks = validate(args.artifact)
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
