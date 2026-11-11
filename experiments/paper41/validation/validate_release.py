#!/usr/bin/env python3
"""Validate the Paper XLI candidate without changing inherited evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper41"
MANIFEST = PACKAGE / "release-manifest.json"
EVIDENCE_MAP = PACKAGE / "evidence-map.v1.json"
RECEIPT = PACKAGE / "results/paper41_release_candidate.validation-receipt.json"
SOURCE_COMMIT = "050cf8ec11e3db263830b46ea95e4062b8e08869"
HISTORICAL = {
    "papers/unnumbered/circular_coalescence_counts/MANUSCRIPT.md":
        "4fac6e3a1edb4038c4be8e6f39ed2c20197a31547a01a1afd5baa9edbb5723e9",
    "papers/unnumbered/circular_coalescence_counts/references.bib":
        "22759041ce7aab8797025048c876c56121d2d4f48fbc9e9b00e69b8ba3a02f3c",
    "papers/unnumbered/circular_coalescence_counts/hal-v1/Chen_Registered_Absorption_Chains_HAL_preprint.pdf":
        "e1458521b652c6dab20ffcf0454370356abe8760e0cb89dc2b3d22d1ec9b3cb4",
    "experiments/registered_absorption_chains/replay-lock.v1.json":
        "1c12bedb480a031968260200ce53867c00a414bee112ccff0baa09f98462d43e",
    "experiments/registered_absorption_chains/results/independent_bfs_n2_n7.v1.json":
        "d6d140baaccdb2274856cff7ed2cee1cf9ec069c8127730bc35e805a31437cc0",
    "experiments/registered_absorption_chains/lean/formalization-manifest.v1.json":
        "2ecdac2a895ba158f1b938647bd5ca002df9dadc9dcaab76e0eac390e71c0dbb",
}
ARTIFACTS = {
    "manuscript": "papers/paper41/Paper XLI.md",
    "reader-pdf": "papers/paper41/paper41_arxiv.pdf",
    "bibliography": "papers/paper41/references-v1.bib",
    "paper-index": "papers/paper41/README.md",
    "evidence-map": "experiments/paper41/evidence-map.v1.json",
    "experiment-index": "experiments/paper41/README.md",
    "release-environment": "experiments/paper41/release-environment.json",
    "candidate-validator": "experiments/paper41/validation/validate_release.py",
    "candidate-validator-tests": "experiments/paper41/validation/test_release.py",
    "candidate-ci-workflow": ".github/workflows/paper41-candidate.yml",
    "checkout-line-ending-policy": ".gitattributes",
    "reader-build-entrypoint": "papers/tex/build.py",
    "reader-build-driver": "papers/tex/_build.py",
    "reader-build-postprocessor": "papers/tex/_postprocess.py",
    "reader-build-hrule-cleaner": "papers/tex/_clean_hrule.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def data(path: str) -> bytes:
    target = (ROOT / path).resolve()
    require(target.is_relative_to(ROOT.resolve()), f"path escapes repository: {path}")
    require(target.is_file(), f"missing file: {path}")
    return target.read_bytes()


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=True
    )
    return result.stdout


def check_historical() -> None:
    evidence = json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))
    require(evidence["schema"] == "rime.paper41.evidence-map.v1", "evidence schema")
    require(evidence["paper_id"] == "PAPER41" and evidence["release_version"] == "1.0",
            "evidence edition identity")
    historical = evidence["historical_submission"]
    require(historical["identifier"] == "hal-05837829v1", "HAL identifier drift")
    require(historical["status"] == "SUBMITTED_MODERATION_NOT_ASSERTED_ACCEPTED",
            "HAL status overpromoted")
    require(historical["source_commit"] == SOURCE_COMMIT, "historical commit drift")
    companion = evidence["inherited_companion"]
    require(companion["source_commit"] == SOURCE_COMMIT, "companion commit drift")
    require(companion["proof_owner"] == "experiments/registered_absorption_chains/",
            "proof owner drift")
    recorded = historical["source_files"] + companion["files"]
    require(len(recorded) == len(HISTORICAL), "historical file count drift")
    require({row["path"]: row["sha256"] for row in recorded} == HISTORICAL,
            "historical byte map drift")
    require(evidence["numbered_edition"]["publication_status"] == "RELEASE_CANDIDATE",
            "edition status overpromoted")
    require(evidence["numbered_edition"]["release_identity_claimed"] is False,
            "edition release identity claimed early")
    require(evidence["numbered_edition"]["external_anchor_claimed"] is False,
            "external anchor claimed early")
    git_bytes("cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}")
    for path, expected in HISTORICAL.items():
        require(sha256(data(path)) == expected, f"local historical byte drift: {path}")
        require(sha256(git_bytes("show", f"{SOURCE_COMMIT}:{path}")) == expected,
                f"historical Git object drift: {path}")

    lean_root = ROOT / "experiments/registered_absorption_chains/lean"
    lean = json.loads(
        (lean_root / "formalization-manifest.v1.json").read_text(encoding="utf-8")
    )
    require(lean["build"]["lean"] == "4.33.0", "Lean toolchain drift")
    require(len(lean["source_sha256"]) == 56, "Lean source inventory drift")
    for path, expected in lean["source_sha256"].items():
        require(sha256((lean_root / path).read_bytes()) == expected,
                f"Lean source byte drift: {path}")


def check_citations() -> None:
    manuscript = data(ARTIFACTS["manuscript"]).decode("utf-8")
    bibliography = data(ARTIFACTS["bibliography"]).decode("utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,]+),", bibliography))
    cited = set(re.findall(r"(?<!\w)@([A-Za-z][A-Za-z0-9_:-]*)", manuscript))
    require(cited <= keys, f"unresolved citation keys: {sorted(cited - keys)}")
    require("Paper XLI (version 1.0)" in manuscript, "visible edition missing")
    require("hal-05837829v1" not in manuscript, "historical submission in reader prose")
    require(data(ARTIFACTS["reader-pdf"]).startswith(b"%PDF-"), "reader PDF invalid")


def candidate_manifest() -> dict[str, object]:
    return {
        "schema": "rime.paper41.release-manifest.v1",
        "paper_id": "PAPER41",
        "release_version": "1.0",
        "intended_release_tag": "paper41-v1.0",
        "status": "RELEASE_CANDIDATE",
        "release_identity_claimed": False,
        "external_anchor_claimed": False,
        "historical_evidence_map": ARTIFACTS["evidence-map"],
        "receipt_self_exclusion": True,
        "artifacts": [
            {
                "role": role,
                "path": path,
                "sha256": sha256(data(path)),
                "size": len(data(path)),
            }
            for role, path in ARTIFACTS.items()
        ],
    }


def check_manifest() -> tuple[int, str]:
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(manifest["schema"] == "rime.paper41.release-manifest.v1",
            "manifest schema")
    for field, expected in (
        ("paper_id", "PAPER41"),
        ("release_version", "1.0"),
        ("intended_release_tag", "paper41-v1.0"),
        ("status", "RELEASE_CANDIDATE"),
        ("release_identity_claimed", False),
        ("external_anchor_claimed", False),
        ("receipt_self_exclusion", True),
        ("historical_evidence_map", ARTIFACTS["evidence-map"]),
    ):
        require(manifest[field] == expected, f"manifest {field} drift")
    rows = manifest["artifacts"]
    require(len(rows) == len(ARTIFACTS), "artifact count drift")
    require({row["role"]: row["path"] for row in rows} == ARTIFACTS,
            "artifact role/path drift")
    require(len({row["role"] for row in rows}) == len(rows), "duplicate artifact role")
    require(len({row["path"] for row in rows}) == len(rows), "duplicate artifact path")
    for row in rows:
        payload = data(row["path"])
        require(row["sha256"] == sha256(payload), f"digest drift: {row['path']}")
        require(row["size"] == len(payload), f"size drift: {row['path']}")
    return len(rows), sha256(manifest_bytes)


def replay() -> None:
    bfs = subprocess.run(
        [
            sys.executable, "-O", "-B",
            "experiments/registered_absorption_chains/independent_bfs_check.py",
            "--check-result",
            "experiments/registered_absorption_chains/results/independent_bfs_n2_n7.v1.json",
        ],
        cwd=ROOT, check=True, text=True, capture_output=True
    )
    require(bfs.stdout.count("PASS") == 6, "bounded BFS replay incomplete")
    lean = subprocess.run(
        [sys.executable, "-B", "validate_lean_package.py"],
        cwd=ROOT / "experiments/registered_absorption_chains/lean",
        check=True, text=True, capture_output=True, env=os.environ.copy()
    )
    require("PASS partial Lean package: 56 bound files; 262 axiom audits" in lean.stdout,
            "Lean replay incomplete")
    print(bfs.stdout, end="")
    print(lean.stdout, end="")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true",
                        help="write candidate manifest from current exact bytes")
    parser.add_argument("--replay", action="store_true",
                        help="rerun inherited BFS and Lean validators")
    parser.add_argument("--write-receipt", action="store_true",
                        help="replay and write a local candidate receipt")
    args = parser.parse_args()
    try:
        check_historical()
        check_citations()
        if args.freeze:
            require(not args.write_receipt, "freeze and receipt are separate steps")
            MANIFEST.write_text(
                json.dumps(candidate_manifest(), indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        count, manifest_sha = check_manifest()
        if args.replay or args.write_receipt:
            replay()
        if args.write_receipt:
            RECEIPT.parent.mkdir(parents=True, exist_ok=True)
            receipt = {
                "schema": "rime.paper41.candidate-validation-receipt.v1",
                "status": "PASS_LOCAL_CANDIDATE_CLOSURE",
                "paper_id": "PAPER41",
                "release_identity_claimed": False,
                "external_anchor_claimed": False,
                "manifest_sha256": manifest_sha,
                "artifact_count": count,
                "historical_byte_bindings": len(HISTORICAL),
                "lean_source_files": 56,
                "bounded_bfs_n": [2, 3, 4, 5, 6, 7],
                "lean_axiom_audits": 262,
                "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "limits": [
                    "Local same-source replay, not independent replication",
                    "No Zenodo deposit, release tag, or external anchor claimed",
                    "Corollary 5.2 asymptotic estimate is manuscript-only",
                ],
            }
            RECEIPT.write_text(
                json.dumps(receipt, indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(f"PASS Paper XLI candidate: {count} artifacts; manifest {manifest_sha}")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"FAIL Paper XLI candidate: {exc}") from exc


if __name__ == "__main__":
    main()
