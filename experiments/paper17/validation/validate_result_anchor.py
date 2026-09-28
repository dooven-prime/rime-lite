#!/usr/bin/env python3
"""Validate the Paper XVII result-owned anchor without producer replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "result-anchor.v1.json"
DEFAULT_RECEIPT = ROOT / "results" / "result-anchor.v1.validation-receipt.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    require(manifest["status"] == "RESULT_OWNED_ANCHOR_READY", "anchor status mismatch")
    artifacts = manifest["artifacts"]
    require(len(artifacts) == manifest["artifact_count"], "artifact count mismatch")
    paths = [entry["path"] for entry in artifacts]
    require(len(paths) == len(set(paths)), "duplicate artifact path")
    for entry in artifacts:
        target = (ROOT / entry["path"]).resolve()
        require(target.is_relative_to(ROOT.resolve()), "artifact escapes root")
        require(target.is_file(), f"missing artifact: {entry['path']}")
        require(target.stat().st_size == entry["bytes"], f"size mismatch: {entry['path']}")
        require(sha256_file(target) == entry["sha256"], f"digest mismatch: {entry['path']}")

    sidecar = ROOT / manifest["exact_sidecar"]["path"]
    require(sidecar.stat().st_size == manifest["exact_sidecar"]["bytes"], "sidecar size mismatch")
    require(sha256_file(sidecar) == manifest["exact_sidecar"]["sha256"], "sidecar digest mismatch")
    with tarfile.open(sidecar, mode="r:") as archive:
        members = archive.getmembers()
    require(len(members) == manifest["exact_sidecar"]["member_count"], "sidecar member count mismatch")

    common = load_json(ROOT / "results" / "finite_history_common_support_audit.v1.json")
    transient = load_json(ROOT / "results" / "finite_history_transient_fiber_audit.v1.json")
    claims = manifest["canonical_claims"]
    require(common["diagnosis"]["minimal_memory_order_identified"] is False, "minimal-memory boundary mismatch")
    require(
        common["common_support_audit"]["all_order_partitions_identical"] is True,
        "partition identity mismatch",
    )
    require(transient["transient_separation"]["offending_source_count"] == claims["t1_obstruction_source_count"], "obstruction source mismatch")
    require(transient["transient_separation"]["all_offending_sources_globally_singleton_at_t2"] is True, "transient separation mismatch")
    require(transient["persistent_safe_forgetting"]["cohort_sizes"] == claims["persistent_cohort_sizes"], "persistent cohort mismatch")
    require(transient["persistent_safe_forgetting"]["same_cohort_collection_at_t2_and_t3"] is True, "persistent membership mismatch")
    require(transient["diagnosis"]["mechanism_identified"] is False, "mechanism boundary mismatch")

    receipt = {
        "schema": "rime.paper17.result-anchor-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_RESULT_OWNED_EXACT_REPLAY_CLOSURE",
        "independent_validation": False,
        "producer_replayed": False,
        "manifest": {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "artifact_count": len(artifacts),
            "sidecar_member_count": len(members),
            "common_support_correction_bound": True,
            "transient_fiber_decomposition_bound": True,
            "minimal_memory_order_claimed": False,
            "mechanism_identified": False,
        },
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.manifest.resolve())
    if args.write_receipt:
        with DEFAULT_RECEIPT.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps(receipt, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
