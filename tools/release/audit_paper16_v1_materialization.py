#!/usr/bin/env python3
"""Explain the frozen Paper XVI v1.0 JSON materialization mismatch.

This is a release- and path-specific historical audit. It does not rewrite the
published tag, regenerate a receipt, or turn the original clean-checkout
closure result into PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RELEASE_REF = "paper16-v1.0"
RELEASE_COMMIT = "970125ae0c38dd28b2ab6b536e3043acdc497459"
MANIFEST_URI = "experiments/paper16/release-manifest.v1.json"
MANIFEST_GIT_BLOB_SHA256 = (
    "0839c69a5d8ec66f7cbba073347290008ba2204599b1166368a13b3e574efba0"
)
DECLARED_CLOSURE_SHA256 = (
    "9077abae3effc7230c107c491cad5d496a57e3983fcd4e4c3b4e7529197357c8"
)

CRLF_TEXT = "CRLF_TEXT"
MIXED_EXECUTION_LINE = "CRLF_TEXT_WITH_EXECUTION_LINE_LF"

# These are the complete and only historical byte-materialization exceptions.
# Keys include the manifest path base so similarly named files cannot collide.
MATERIALIZATION_PROFILE = {
    "PAPER16_SOURCE_ROOT:digital_fly_v0/results/carrier_v0_manifest.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:replay/results/large_artifact_replay.v1.receipt.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:followups/results/d2_2_named_sector_followup.v1.validation-receipt.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:followups/results/y_known_pm_route_audit.v1.validation-receipt.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_1/results/o1_observation_resolution_v0_1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_1/results/sd1_dynamics_v0_1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_1/results/sd1_operator_admission_v0_1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_2/results/d2_1_markov_closure_v0_2.json": CRLF_TEXT,
    "REPOSITORY_ROOT:experiments/paper16/results/a1-a2-exact-replay.v1.receipt.json": CRLF_TEXT,
    "REPOSITORY_ROOT:experiments/paper16/results/dynamic-descent-replay.v1.receipt.json": CRLF_TEXT,
    "REPOSITORY_ROOT:experiments/paper16/results/static-audits-replay.v1.receipt.json": MIXED_EXECUTION_LINE,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:followups/results/d2_2_named_sector_followup.v1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:followups/results/y_known_pm_route_audit.v1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/path_lifting_audit_full_v3.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/path_lifting_audit_full_v3_somaSide.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/path_lifting_depth3_audit_full_somaSide_v1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/path_lifting_depth3_audit_full_v1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/sectorization_comparison_v1.json": CRLF_TEXT,
    "PAPER16_SOURCE_ROOT:results/sectorization_field_audit_v1.json": CRLF_TEXT,
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def safe_uri(uri: str) -> str:
    path = PurePosixPath(uri)
    if (
        not uri
        or "\\" in uri
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError(f"invalid repository URI: {uri!r}")
    return uri


def git_output(*args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout


def git_blob(uri: str) -> bytes:
    return git_output("show", f"{RELEASE_REF}:{safe_uri(uri)}")


def repository_uri(entry: dict[str, Any]) -> str:
    path = safe_uri(entry["path"])
    base = entry.get("path_base")
    if base == "REPOSITORY_ROOT":
        return path
    if base == "PAPER16_SOURCE_ROOT":
        return f"experiments/paper16/source/{path}"
    raise ValueError(f"unsupported Paper XVI path base: {base!r}")


def profile_key(entry: dict[str, Any]) -> str:
    return f"{entry.get('path_base')}:{entry['path']}"


def normalized_lf(payload: bytes) -> bytes:
    normalized = payload.replace(b"\r\n", b"\n")
    if b"\r" in normalized or b"\x00" in normalized:
        raise ValueError("historical text materialization received non-LF text")
    return normalized


def historical_materialization(payload: bytes, mode: str) -> bytes:
    normalized = normalized_lf(payload)
    materialized = normalized.replace(b"\n", b"\r\n")
    if mode == CRLF_TEXT:
        return materialized
    if mode == MIXED_EXECUTION_LINE:
        marker_lf = b'"executable": "<EXECUTION_PYTHON>/python.exe",\n'
        marker_crlf = b'"executable": "<EXECUTION_PYTHON>/python.exe",\r\n'
        if materialized.count(marker_crlf) != 1:
            raise ValueError("mixed-EOL marker is absent or ambiguous")
        return materialized.replace(marker_crlf, marker_lf, 1)
    raise ValueError(f"unsupported historical materialization mode: {mode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Explain the frozen Paper XVI v1.0 LF/CRLF materialization "
            "mismatch without rewriting the release."
        )
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="include the 21 path-level materialization records",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resolved_commit = git_output(
        "rev-parse", "--verify", f"{RELEASE_REF}^{{commit}}"
    ).decode("ascii").strip()
    if resolved_commit != RELEASE_COMMIT:
        raise ValueError(
            f"{RELEASE_REF} resolves to {resolved_commit}, expected {RELEASE_COMMIT}"
        )

    manifest_bytes = git_blob(MANIFEST_URI)
    if sha256_bytes(manifest_bytes) != MANIFEST_GIT_BLOB_SHA256:
        raise ValueError("Paper XVI v1.0 manifest Git blob changed")
    manifest = json.loads(manifest_bytes)
    if manifest.get("closure_sha256") != DECLARED_CLOSURE_SHA256:
        raise ValueError("Paper XVI v1.0 declared closure digest changed")

    entries = manifest.get("ordered_closure")
    if not isinstance(entries, list) or len(entries) != 56:
        raise ValueError("Paper XVI v1.0 ordered closure is not the frozen 56-entry set")

    explained: list[dict[str, Any]] = []
    unexpected: list[str] = []
    direct_matches = 0
    used_profiles: set[str] = set()

    for entry in entries:
        payload = git_blob(repository_uri(entry))
        actual_digest = sha256_bytes(payload)
        if actual_digest == entry["sha256"] and len(payload) == entry["size"]:
            direct_matches += 1
            continue

        key = profile_key(entry)
        mode = MATERIALIZATION_PROFILE.get(key)
        if mode is None:
            unexpected.append(key)
            continue

        reconstructed = historical_materialization(payload, mode)
        if (
            sha256_bytes(reconstructed) != entry["sha256"]
            or len(reconstructed) != entry["size"]
        ):
            unexpected.append(key)
            continue
        if json.loads(payload) != json.loads(reconstructed):
            unexpected.append(key)
            continue

        used_profiles.add(key)
        explained.append(
            {
                "path": entry["path"],
                "path_base": entry["path_base"],
                "materialization": mode,
                "git_blob_sha256": actual_digest,
                "registered_sha256": entry["sha256"],
                "semantic_json_equal": True,
            }
        )

    unused_profiles = sorted(set(MATERIALIZATION_PROFILE) - used_profiles)
    result = {
        "schema": "rime.paper16.historical-materialization-audit.v1",
        "status": (
            "HISTORICAL_MATERIALIZATION_EXPLAINED"
            if not unexpected and not unused_profiles
            else "UNRESOLVED"
        ),
        "release_ref": RELEASE_REF,
        "release_commit": resolved_commit,
        "manifest_git_blob_sha256": sha256_bytes(manifest_bytes),
        "declared_closure_sha256": manifest["closure_sha256"],
        "ordered_closure_entries": len(entries),
        "direct_git_blob_matches": direct_matches,
        "materialization_exceptions": len(explained),
        "all_exception_json_semantics_equal": all(
            item["semantic_json_equal"] for item in explained
        ),
        "unexpected_mismatches": unexpected,
        "unused_profiles": unused_profiles,
        "materialization_modes": {
            CRLF_TEXT: sum(
                item["materialization"] == CRLF_TEXT for item in explained
            ),
            MIXED_EXECUTION_LINE: sum(
                item["materialization"] == MIXED_EXECUTION_LINE
                for item in explained
            ),
        },
        "boundary": {
            "frozen_release_rewritten": False,
            "direct_clean_checkout_closure_pass": False,
            "original_receipt_resigned": False,
            "local_closure_verification": False,
            "independent_validation": False,
            "meaning": (
                "The frozen manifest digests identify historical Windows text "
                "materializations of the same JSON objects. This audit explains "
                "the mismatch; it does not repair or revalidate the v1.0 closure."
            ),
        },
    }
    if args.verbose:
        result["exceptions"] = explained
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "HISTORICAL_MATERIALIZATION_EXPLAINED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
