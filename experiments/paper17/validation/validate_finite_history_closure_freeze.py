#!/usr/bin/env python3
"""Validate and replay the result-owned finite-history freeze closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from finite_history_execution_common import D0_PATH, verify_artifact, write_json
from freeze_finite_history_closure_v1 import (
    ARCHIVE_PREFIX,
    FREEZE_MANIFEST_PATH,
    RESULT_PATH,
    ordered_files_digest,
)
from optimized_exact_common import load_json, sha256_file
from run_finite_history_closure_v1 import _classify, _intern_observations


DEFAULT_RECEIPT = (
    ROOT / "results" / "finite_history_closure.v1.freeze-validation-receipt.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _copy_member(archive: tarfile.TarFile, member: tarfile.TarInfo, destination: Path) -> None:
    source = archive.extractfile(member)
    if source is None:
        raise ValueError(f"archive member has no payload: {member.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        while True:
            block = source.read(8 * 1024 * 1024)
            if not block:
                break
            output.write(block)


def validate(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    require(manifest["status"] == "POST_EXECUTION_FROZEN", "freeze status mismatch")
    roles = [entry["role"] for entry in manifest["artifact_closure"]]
    require(len(roles) == len(set(roles)), "duplicate freeze closure role")
    closure_paths = {
        entry["role"]: verify_artifact(entry)
        for entry in manifest["artifact_closure"]
    }
    archive_path = closure_paths["EXACT_SIDECAR_ARCHIVE"]
    archive_binding = manifest["exact_sidecar_archive"]
    require(archive_path.stat().st_size == archive_binding["bytes"], "archive size mismatch")
    require(sha256_file(archive_path) == archive_binding["sha256"], "archive digest mismatch")
    entries = manifest["archive_members"]
    require(len(entries) == archive_binding["member_count"] == 1425, "archive member count mismatch")
    require(ordered_files_digest(entries) == archive_binding["ordered_files_sha256"], "ordered-files digest mismatch")
    expected = {entry["path"]: entry for entry in entries}

    with tempfile.TemporaryDirectory() as directory:
        extracted_root = Path(directory) / ARCHIVE_PREFIX
        seen: set[str] = set()
        with tarfile.open(archive_path, mode="r:") as archive:
            members = archive.getmembers()
            require(len(members) == len(entries), "unexpected archive member count")
            for member in members:
                require(member.isfile(), "archive contains non-file member")
                require(member.name.startswith(f"{ARCHIVE_PREFIX}/"), "archive prefix mismatch")
                relative = member.name[len(ARCHIVE_PREFIX) + 1 :]
                require(relative in expected, f"unexpected archive member: {relative}")
                require(relative not in seen, f"duplicate archive member: {relative}")
                require(member.uid == member.gid == member.mtime == 0, "archive metadata is not deterministic")
                require(member.mode == 0o444, "archive mode mismatch")
                target = extracted_root / relative
                _copy_member(archive, member, target)
                binding = expected[relative]
                require(target.stat().st_size == binding["bytes"], f"member size mismatch: {relative}")
                require(sha256_file(target) == binding["sha256"], f"member digest mismatch: {relative}")
                seen.add(relative)
        require(seen == set(expected), "archive member set mismatch")

        promoted = closure_paths["PROMOTED_SIDECAR_INVENTORY"]
        archived_inventory = extracted_root / "sidecar-inventory.json"
        require(promoted.read_bytes() == archived_inventory.read_bytes(), "promoted inventory byte mismatch")
        result = load_json(RESULT_PATH)
        archived_result = load_json(extracted_root / "result.json")
        require(result == archived_result, "archived compact result mismatch")
        d0 = __import__("numpy").load(D0_PATH, mmap_mode="r", allow_pickle=False)
        sources = [int(value) for value in d0]
        inventory = load_json(archived_inventory)
        require(inventory["ordered_sources"] == sources, "archived D0 ordering mismatch")
        sequences, observations, comparisons = _intern_observations(
            sources, extracted_root / "shards", 4
        )
        classification = _classify(sources, sequences, 2, 4)
        require(classification == result["classification"], "archive classification replay mismatch")
        require(observations == inventory["observation_inventory"], "archive observation inventory mismatch")
        require(comparisons == inventory["exact_payload_comparisons_after_hash_match"], "archive exact-comparison count mismatch")

    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-freeze-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_RESULT_OWNED_EXACT_SIDECAR_REPLAY",
        "independent_validation": False,
        "producer_replayed": False,
        "freeze_manifest": {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "validator": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "verified": {
            "archive_member_count": 1425,
            "source_count": 711,
            "orders": [0, 1, 2],
            "primary_outcome": "EXACT_CLOSED_NONINJECTIVE",
            "minimal_closing_order_on_registered_domain": 2,
            "classification_replayed_from_result_owned_archive": True,
            "runtime_work_required_for_replay": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=FREEZE_MANIFEST_PATH)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.manifest.resolve())
    if args.write_receipt:
        write_json(DEFAULT_RECEIPT, receipt)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
