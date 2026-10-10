#!/usr/bin/env python3
"""Read-only publication gate; compact audit checks are not full cache replay."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from build_publication_candidate_v2 import (
    AUDIT, DRIVE, MANIFEST, RECEIPT, REPLACED, SNAPSHOT, TABLE,
    build_manifest, build_table, read, ref, sha256_file,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_ref(entry: dict, base: Path) -> None:
    relative = entry["path"]
    require(not Path(relative).is_absolute() and "*" not in relative and "?" not in relative, "nonportable artifact path")
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()) and path.is_file(), f"missing or escaping artifact: {relative}")
    require(path.stat().st_size == entry["bytes"] and sha256_file(path) == entry["sha256"], f"artifact byte drift: {relative}")


def validate_drive() -> dict:
    record = read(REPO / DRIVE)
    require(record["schema"] == "rime.paper17.post-result-persistent-safe-effective-drive-audit.v1" and record["status"] == "PASS", "drive audit schema/status drift")
    require(record["validation_mode"] == "LOCAL_BOUND_PAYLOAD_REPLAY_NO_OPERATOR_TRAVERSAL", "drive replay boundary drift")
    require(record["independent_validation"] is False and record["microscopic_producer_replayed"] is False, "drive replay overclaim")
    expected_inputs = {
        "results/finite_history_transient_fiber_audit.v1.json",
        "results/finite_history_common_support_audit.v1.json",
        "mechanism/results/mechanism_cohort_registry.v1.json",
        "mechanism/results/mts1-v1.freeze-manifest.json",
        "mechanism/results/mts1-v1/inventory.json",
        "mechanism/results/mts1-v1/validation/mechanism_validation.v1.receipt.json",
    }
    require(len(record["inputs"]) == 6 and {entry["path"] for entry in record["inputs"]} == expected_inputs, "drive parent read-set drift")
    for entry in record["inputs"]:
        check_ref(entry, ROOT)
    check_ref(record["audit_script"], ROOT)
    require(record["audit_script"]["path"] == AUDIT.removeprefix("experiments/paper17/"), "drive implementation identity drift")
    require(record["coverage"] == {
        "cohorts": 5, "distinct_sources": 102, "source_time_records": 306,
        "times": [1, 2, 3], "paper17_common_support_times": [2, 3],
        "within_cohort_pairs_across_cached_times": 5265,
    }, "drive coverage narrowed or changed")
    require(record["summary"] == {
        "raw_drive_sign_counts": {"NONZERO_NONPOSITIVE": 306},
        "nonzero_clipped_drive_source_times": 0,
        "nonzero_clipped_drive_fiber_exists": False,
        "all_selected_updates_are_pure_leak": True,
    }, "drive aggregate result drift")
    registry = read(ROOT / "mechanism/results/mechanism_cohort_registry.v1.json")
    cohorts = registry["persistent_safe"]["cohorts"]
    sizes = [cohort["source_count"] for cohort in cohorts]
    require(sizes == [51, 25, 19, 4, 3], "persistent cohort sizes drift")
    expected = {(cohort["cohort_id"], time): cohort for cohort in cohorts for time in (1, 2, 3)}
    rows = record["by_cohort_time"]
    require(len(rows) == 15 and {(row["cohort_id"], row["time"]) for row in rows} == set(expected), "cohort-time record set drift")
    for row in rows:
        cohort = expected[row["cohort_id"], row["time"]]
        count = cohort["source_count"]
        require(row["source_count"] == count and row["pair_count"] == comb(count, 2), "cohort cardinality drift")
        require(row["pair_modes"] == {"BOTH_DRIVES_ZERO": comb(count, 2)}, "cohort effective-drive interpretation drift")
        require(row["raw_drive_sign_counts"] == {"NONZERO_NONPOSITIVE": count} and row["nonzero_clipped_drive_sources"] == 0, "cohort signs drift")
    require(sum(sizes) * 2 == 204 and sum(size - 1 for size in sizes) * 2 == 194, "noninjective coverage arithmetic drift")
    freeze = read(ROOT / "mechanism/results/mts1-v1.freeze-manifest.json")
    roles = {entry["role"]: entry for entry in freeze["artifact_closure"]}
    for role, path in (
        ("EXACT_SIDECAR_INVENTORY", "mechanism/results/mts1-v1/inventory.json"),
        ("EXHAUSTIVE_VALIDATION_RECEIPT", "mechanism/results/mts1-v1/validation/mechanism_validation.v1.receipt.json"),
    ):
        parent = roles[role]
        target = ROOT / path
        require(parent["bytes"] == target.stat().st_size and parent["sha256"] == sha256_file(target), "frozen MTS-1 parent binding drift")
    return {"status": "PASS", "source_times": 306, "common_support_points": 204, "redundant_windows": 194, "source_payloads_replayed": False, "operator_action_recomputed": False}


def validate_source() -> None:
    source = (REPO / "papers/paper17/Paper XVII.md").read_text(encoding="utf-8")
    require("Computational Certificate 7.3" in source and "### 7.4 Effective-Drive Boundary" in source, "effective-drive claim missing from manuscript")
    require("do not extend the" in source and "all 711 sources" in source, "drive domain firewall missing")
    require(not any(ord(char) < 32 and char not in "\n\r\t" for char in source), "control character in manuscript")
    require(not re.search(r"(?<!\\)\b(?:qquad|quad)\b|(?<!\\)\bleft\(|(?<!\\)\bright\)", source), "bare TeX command in source")
    bib = (REPO / "papers/paper17/references-v1.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib))
    citations = {key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", source) for key in group.split(",")}
    require(citations <= keys, f"missing bibliography entries: {citations - keys}")
    tags = re.findall(r"\\tag\{([^}]+)\}", source)
    require(len(tags) == len(set(tags)), "duplicate equation tag")


def run(relative: str, env: dict) -> dict:
    process = subprocess.run([sys.executable, str(ROOT / relative)], cwd=REPO, env=env, capture_output=True, text=True, check=False)
    require(process.returncode == 0, f"check failed: {relative}\n{process.stdout[-3000:]}\n{process.stderr[-3000:]}")
    return json.loads(process.stdout)


def validate() -> dict:
    manifest = read(MANIFEST)
    require(manifest == build_manifest(), "candidate-2 manifest differs from declared artifact surface")
    require(read(TABLE) == build_table(), "candidate-2 evidence table differs from declared promotion")
    require(manifest["status"] == "RELEASE_CANDIDATE" and manifest["release_identity_claimed"] is False, "premature publication identity")
    require(manifest["receipt_path"] == RECEIPT and RECEIPT not in {entry["path"] for entry in manifest["artifacts"]}, "receipt self-binding")
    require(not any(manifest["claim_boundaries"].values()), "forbidden scientific promotion")
    for entry in manifest["artifacts"]:
        check_ref(entry, REPO)
    previous = manifest["prior_candidate"]
    require(previous["replaced_artifacts"] == {path: f"{SNAPSHOT}/{path}" for path in REPLACED}, "prior-reader replacement map drift")
    old_manifest = read(ROOT / "release-manifest.v1.json")
    old_receipt = read(ROOT / "results/release.v1.validation-receipt.json")
    require(old_receipt["status"] == "PASS" and old_receipt["manifest"] == previous["manifest"], "candidate-1 receipt binding drift")
    require(old_receipt["verified"]["ordered_closure_sha256"] == old_manifest["release_identity"]["ordered_closure_sha256"], "candidate-1 identity drift")
    require(old_receipt["validator"]["sha256"] == sha256_file(ROOT / "validation/validate_release.py"), "candidate-1 validator bytes drift")
    validate_source()
    drive = validate_drive()
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    public = run("validation/validate_public_package.py", env)
    interface = run("validation/validate_mts1_evidence_interface_v1.py", env)
    tests = subprocess.run([sys.executable, str(ROOT / "validation/test_publication_candidate_v2.py")], cwd=REPO, env=env, capture_output=True, text=True, check=False)
    require(tests.returncode == 0, f"compact-gate hostile tests failed:\n{tests.stdout}\n{tests.stderr}")
    require(public["status"] == "PASS" and public["check_count"] == 9, "legacy exact public checks drift")
    require(interface["status"] == "PASS" and interface["sidecar_pair_shards_replayed"] is False, "compact MTS-1 replay boundary drift")
    return {
        "schema": "rime.paper17.release-validation-receipt.v2",
        "status": "PASS", "validation_mode": "LOCAL_CLOSURE_VERIFICATION_WITH_COMPACT_DRIVE_AUDIT",
        "independent_validation": False, "producer_replayed": False,
        "manifest": ref("experiments/paper17/release-manifest.v2.json"),
        "validator": ref("experiments/paper17/validation/validate_release_v2.py"),
        "verified": {
            "artifact_count": manifest["artifact_count"],
            "release_identity_artifact_count": manifest["release_identity"]["ordered_artifact_count"],
            "ordered_closure_sha256": manifest["release_identity"]["ordered_closure_sha256"],
            "previous_candidate_artifacts_preserved": len(old_manifest["artifacts"]),
            "public_package_checks": public["check_count"],
            "compact_gate_hostile_tests": 5,
            "mts1_compact_evidence_interface_verified": True,
            "persistent_drive": drive,
            "coarse_endomap_verified": False,
            "clean_clone_microscopic_generation_verified": False,
            "remote_sidecar_bytes_downloaded": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-candidate-2-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    receipt = REPO / RECEIPT
    if args.write_candidate_2_receipt:
        receipt.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    else:
        require(receipt.is_file() and read(receipt) == result, "candidate-2 receipt missing or different")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
