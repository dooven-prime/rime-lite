#!/usr/bin/env python3
"""Validate the exact Paper XVII release-candidate closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MANIFEST = ROOT / "release-manifest.v1.json"
RECEIPT = ROOT / "results" / "release.v1.validation-receipt.json"
IDENTITY_CLASSES = {
    "theorem-facing-manuscript",
    "theorem-facing-presentation",
    "theorem-facing-computational",
    "release-validation",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def closure_digest(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(entry["bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(manifest["status"] == "RELEASE_CANDIDATE", "release status mismatch")
    require(manifest["release_identity_claimed"] is False, "premature release identity")
    require(manifest["receipt_self_exclusion"] is True, "receipt self-exclusion mismatch")
    require(manifest["receipt_path"] not in {entry["path"] for entry in manifest["artifacts"]}, "receipt included in own closure")
    policy = manifest["digest_policy"]
    require(policy["wildcards_allowed"] is False, "wildcards must be forbidden")
    require(policy["absolute_paths_allowed"] is False, "absolute paths must be forbidden")

    artifacts = manifest["artifacts"]
    require(len(artifacts) == manifest["artifact_count"], "artifact count mismatch")
    paths: set[str] = set()
    counts: Counter[str] = Counter()
    for entry in artifacts:
        relative = entry["path"]
        require(relative not in paths, f"duplicate artifact: {relative}")
        paths.add(relative)
        require("*" not in relative and "?" not in relative, f"wildcard path: {relative}")
        require(not Path(relative).is_absolute(), f"absolute path: {relative}")
        target = (REPO / relative).resolve()
        require(target.is_relative_to(REPO.resolve()), f"path escapes repository: {relative}")
        require(target.is_file(), f"missing artifact: {relative}")
        require(target.stat().st_size == entry["bytes"], f"size mismatch: {relative}")
        require(sha256_file(target) == entry["sha256"], f"digest mismatch: {relative}")
        counts[entry["closure_class"]] += 1
    require(dict(sorted(counts.items())) == manifest["artifact_count_by_closure_class"], "closure-class counts mismatch")

    identity = [entry for entry in artifacts if entry["closure_class"] in IDENTITY_CLASSES]
    declared_identity = manifest["release_identity"]
    require(len(identity) == declared_identity["ordered_artifact_count"], "identity count mismatch")
    require(closure_digest(identity) == declared_identity["ordered_closure_sha256"], "identity closure digest mismatch")

    generation = manifest["generation_closure"]
    require(generation["status"] == "INCOMPLETE_NOT_CLAIMED", "generation closure boundary mismatch")
    require(generation["microscopic_producer_replayed"] is False, "producer replay overclaim")
    require(generation["clean_clone_generation_verified"] is False, "clean-clone overclaim")
    require(len(generation["missing_historical_execution_dependencies"]) == 5, "missing dependency surface mismatch")
    mechanism_production = generation["mechanism_production"]
    require(
        mechanism_production["status"] == "LOCAL_EXECUTION_COMPLETED_COMPACT_CLOSURE_ONLY",
        "mechanism production status mismatch",
    )
    require(mechanism_production["execution_authority"] == "NONE_COMPLETED", "mechanism authority mismatch")
    require(mechanism_production["source_producer_executed"] is True, "mechanism execution not recorded")
    require(mechanism_production["exhaustive_validator_completed"] is True, "mechanism validation not recorded")
    require(mechanism_production["clean_clone_producer_replay_verified"] is False, "mechanism replay overclaim")
    require(mechanism_production["exact_sidecar_tracked_in_git"] is False, "mechanism sidecar tracking mismatch")
    require(
        mechanism_production["exact_sidecar_external_immutable_anchor"] == {
            "doi": "10.5281/zenodo.23234143",
            "binding": "experiments/paper17/mechanism/results/mts1-v1.zenodo-anchor.v1.json",
            "binding_mode": "POST_FREEZE_PUBLIC_SPLIT_DEPOSIT",
        },
        "mechanism sidecar deposit binding mismatch",
    )
    require(manifest["registration_timing_boundary"]["independently_anchored_before_execution"] is False, "timing overclaim")
    require(not any(manifest["claim_boundaries"].values()), "one or more forbidden promotions enabled")
    verified_claims = manifest["verified_claims"]
    require(verified_claims["post_separation_transition_layer_contrast"] is True, "mechanism contrast claim mismatch")
    require(verified_claims["mechanism_source_count"] == 153, "mechanism source count mismatch")
    require(verified_claims["mechanism_source_transition_cache_record_count"] == 459, "mechanism cache count mismatch")
    require(verified_claims["mechanism_pair_transition_record_count"] == 6975, "mechanism pair-record count mismatch")
    require(verified_claims["mechanism_comparison_cell_count"] == 15, "mechanism comparison-cell count mismatch")
    require(verified_claims["mechanism_differing_comparison_cell_count"] == 15, "mechanism differing-cell count mismatch")
    require(verified_claims["mechanism_exact_separator_count"] == 4, "mechanism separator count mismatch")
    require(verified_claims["mechanism_global_post_separation_pair_tally_bound"] is True, "global tally binding missing")
    require(verified_claims["mechanism_universal_separator_at_1_to_2"] is False, "initial trigger overclaim")

    public_validation = subprocess.run(
        [sys.executable, str(ROOT / "validation" / "validate_public_package.py")],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        public_validation.returncode == 0,
        f"public-package validation failed:\n{public_validation.stdout[-4000:]}\n{public_validation.stderr[-4000:]}",
    )
    public_result = json.loads(public_validation.stdout)
    require(public_result["status"] == "PASS", "public-package status mismatch")
    evidence_validation = subprocess.run(
        [sys.executable, str(ROOT / "validation" / "validate_mts1_evidence_interface_v1.py")],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        evidence_validation.returncode == 0,
        f"MTS-1 evidence-interface validation failed:\n"
        f"{evidence_validation.stdout[-4000:]}\n{evidence_validation.stderr[-4000:]}",
    )
    evidence_result = json.loads(evidence_validation.stdout)
    require(evidence_result["status"] == "PASS", "MTS-1 evidence-interface status mismatch")
    require(evidence_result["sidecar_pair_shards_replayed"] is False, "compact replay overclaim")

    return {
        "schema": "rime.paper17.release-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "independent_validation": False,
        "producer_replayed": False,
        "manifest": {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(REPO).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "artifact_count": len(artifacts),
            "release_identity_artifact_count": len(identity),
            "ordered_closure_sha256": declared_identity["ordered_closure_sha256"],
            "public_package_checks": public_result["check_count"],
            "mts1_compact_evidence_interface_verified": True,
            "receipt_excluded_from_own_closure": True,
            "coarse_endomap_verified": False,
            "post_separation_transition_layer_contrast_verified": True,
            "initial_separation_trigger_identified": False,
            "mechanism_exact_sidecar_external_anchor": True,
            "clean_clone_microscopic_generation_verified": False,
            "preexecution_temporal_order_independently_anchored": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.manifest.resolve())
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    else:
        require(RECEIPT.is_file(), "retained release receipt is missing")
        retained = json.loads(RECEIPT.read_text(encoding="utf-8"))
        require(retained == receipt, "retained release receipt does not match validation replay")
    print(json.dumps(receipt, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
