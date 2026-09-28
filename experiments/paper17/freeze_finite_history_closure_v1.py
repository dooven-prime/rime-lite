#!/usr/bin/env python3
"""Promote the completed finite-history sidecar into a result-owned closure."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from pathlib import Path
from typing import Any

from finite_history_execution_common import (
    D0_PATH,
    PREFLIGHT_PATH,
    PREFLIGHT_RECEIPT_PATH,
    REGISTRATION_PATH,
    REGISTRATION_RECEIPT_PATH,
    ROOT,
    RUNTIME_ROOT,
    artifact,
    write_json,
)
from optimized_exact_common import load_json, sha256_file


RUN_ID = "finite-history-v1"
RUN_ROOT = RUNTIME_ROOT / RUN_ID
RESULT_PATH = ROOT / "results" / "finite_history_closure.v1.json"
RESULT_RECEIPT_PATH = (
    ROOT / "results" / "finite_history_closure.v1.validation-receipt.json"
)
PROMOTED_INVENTORY_PATH = (
    ROOT / "results" / "finite_history_closure.v1.sidecar-inventory.json"
)
ARCHIVE_PATH = ROOT / "results" / "finite_history_closure.v1.sidecar.tar"
FREEZE_MANIFEST_PATH = (
    ROOT / "results" / "finite_history_closure.v1.freeze-manifest.json"
)
ARCHIVE_PREFIX = RUN_ID


def required_member_paths() -> list[str]:
    members = ["checkpoint.json", "result.json", "sidecar-inventory.json"]
    for source in sorted(
        int(path.stem) for path in (RUN_ROOT / "shards").glob("*.bin")
    ):
        members.append(f"shards/{source}.bin")
        members.append(f"source-metadata/{source}.json")
    return sorted(members)


def ordered_files_digest(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(
            f"{entry['path']}\t{entry['bytes']}\t{entry['sha256']}\n".encode("ascii")
        )
    return digest.hexdigest()


def build_archive(member_paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    temporary = ARCHIVE_PATH.with_suffix(ARCHIVE_PATH.suffix + ".tmp")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(temporary, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for relative in member_paths:
            source = RUN_ROOT / relative
            if not source.is_file():
                raise FileNotFoundError(f"missing sidecar member: {relative}")
            entry = {
                "path": relative,
                "bytes": source.stat().st_size,
                "sha256": sha256_file(source),
            }
            entries.append(entry)
            info = tarfile.TarInfo(name=f"{ARCHIVE_PREFIX}/{relative}")
            info.size = int(entry["bytes"])
            info.mode = 0o444
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with source.open("rb") as handle:
                archive.addfile(info, handle)
    temporary.replace(ARCHIVE_PATH)
    archive_entry = {
        "path": ARCHIVE_PATH.relative_to(ROOT).as_posix(),
        "bytes": ARCHIVE_PATH.stat().st_size,
        "sha256": sha256_file(ARCHIVE_PATH),
        "format": "USTAR",
        "member_prefix": ARCHIVE_PREFIX,
        "member_count": len(entries),
        "ordered_files_sha256": ordered_files_digest(entries),
    }
    return entries, archive_entry


def build_freeze() -> dict[str, Any]:
    result = load_json(RESULT_PATH)
    receipt = load_json(RESULT_RECEIPT_PATH)
    if result["status"] != "COMPLETED":
        raise ValueError("finite-history result is not complete")
    if receipt["status"] != "PASS":
        raise ValueError("finite-history result validation did not pass")
    if receipt["result"]["sha256"] != sha256_file(RESULT_PATH):
        raise ValueError("result receipt binding mismatch")
    inventory_source = RUN_ROOT / "sidecar-inventory.json"
    if sha256_file(inventory_source) != result["sidecar_inventory"]["sha256"]:
        raise ValueError("runtime sidecar inventory binding mismatch")
    PROMOTED_INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inventory_source, PROMOTED_INVENTORY_PATH)
    member_entries, archive_entry = build_archive(required_member_paths())

    closure = [
        artifact(RESULT_PATH, "COMPACT_RESULT"),
        artifact(RESULT_RECEIPT_PATH, "RESULT_VALIDATION_RECEIPT"),
        artifact(REGISTRATION_PATH, "EXECUTION_REGISTRATION"),
        artifact(REGISTRATION_RECEIPT_PATH, "REGISTRATION_VALIDATION_RECEIPT"),
        artifact(PREFLIGHT_PATH, "STATIC_PREFLIGHT"),
        artifact(PREFLIGHT_RECEIPT_PATH, "STATIC_PREFLIGHT_RECEIPT"),
        artifact(D0_PATH, "D0_INDEX"),
        artifact(
            ROOT / "results" / "finite_history_D0_admission.v1.json",
            "D0_ADMISSION",
        ),
        artifact(
            ROOT / "results" / "finite_history_D0_admission.v1.validation-receipt.json",
            "D0_ADMISSION_RECEIPT",
        ),
        artifact(PROMOTED_INVENTORY_PATH, "PROMOTED_SIDECAR_INVENTORY"),
        artifact(ARCHIVE_PATH, "EXACT_SIDECAR_ARCHIVE"),
        artifact(ROOT / "run_finite_history_closure_v1.py", "EXPERIMENT_RUNNER"),
        artifact(
            ROOT / "validation" / "validate_finite_history_closure_v1.py",
            "ORIGINAL_RESULT_VALIDATOR",
        ),
        artifact(Path(__file__).resolve(), "FREEZE_PRODUCER"),
        artifact(
            ROOT / "validation" / "validate_finite_history_closure_freeze.py",
            "FREEZE_VALIDATOR",
        ),
    ]
    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-freeze-manifest.v1",
        "status": "POST_EXECUTION_FROZEN",
        "evidence_level": "Computational Certificate",
        "validation_mode": "LOCAL_EXACT_SIDECAR_CLASSIFICATION_REPLAY",
        "independent_validation": False,
        "producer_replayed_during_freeze": False,
        "run_id": RUN_ID,
        "primary_result": {
            "outcome": result["classification"]["primary_outcome_at_H"],
            "minimal_closing_order_on_registered_domain": result["classification"][
                "minimal_closing_order_on_registered_domain"
            ],
            "domain": "REGISTERED_REDUCED_D0",
            "source_count": 711,
            "H": 2,
            "T": 4,
        },
        "exact_sidecar_archive": archive_entry,
        "archive_members": member_entries,
        "artifact_closure": closure,
        "claim_boundary": {
            "registered_reduced_domain_only": True,
            "full_domain_claimed": False,
            "indefinite_forward_invariance_claimed": False,
            "independent_validation_claimed": False,
            "archive_is_storage_projection_not_scientific_recomputation": True,
            "runtime_work_may_be_removed_only_after_freeze_validation_and_durable_anchor": True,
        },
    }


def main() -> int:
    manifest = build_freeze()
    write_json(FREEZE_MANIFEST_PATH, manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "outcome": manifest["primary_result"]["outcome"],
                "archive": manifest["exact_sidecar_archive"],
                "manifest": str(FREEZE_MANIFEST_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
