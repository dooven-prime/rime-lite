#!/usr/bin/env python3
"""Resolve the Paper XVII evidence table against its immutable Git anchor."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
TABLE = ROOT / "manuscript-evidence-table.v1.json"
DEFAULT_RECEIPT = ROOT / "results" / "manuscript-evidence-table.v1.validation-receipt.json"
ALLOWED_LEVELS = {
    "Theorem",
    "Computational Certificate",
    "Computational Observation",
    "Research Program",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_bytes(commit: str, path: str) -> bytes:
    process = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode:
        raise ValueError(process.stderr.decode("utf-8", errors="replace"))
    return process.stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> dict[str, Any]:
    table = load_json(path)
    require(table["status"] == "FROZEN_FOR_RELEASE_CANDIDATE", "table status mismatch")
    commit = table["evidence_anchor"]["commit"]
    resolved = subprocess.run(
        ["git", "rev-parse", commit],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    require(resolved.returncode == 0, "anchor commit does not resolve")
    require(resolved.stdout.strip() == commit, "anchor commit resolution mismatch")

    references: dict[str, dict[str, Any]] = {}
    for name in ("anchor_manifest", "anchor_receipt"):
        entry = table["evidence_anchor"][name]
        references[entry["path"]] = entry
    claim_ids: set[str] = set()
    for claim in table["claims"]:
        require(claim["id"] not in claim_ids, "duplicate claim id")
        claim_ids.add(claim["id"])
        require(claim["reader_facing_status"] in ALLOWED_LEVELS, "invalid evidence level")
        for entry in claim["evidence"]:
            existing = references.setdefault(entry["path"], entry)
            require(existing == entry, f"inconsistent binding: {entry['path']}")

    historical_count = 0
    current_count = 0
    for relative, entry in references.items():
        mode = entry.get("resolution_mode", "historical_git_anchor")
        if mode == "historical_git_anchor":
            payload = git_bytes(commit, relative)
            historical_count += 1
        elif mode == "current_paper_owned":
            target = REPO_ROOT / relative
            require(target.is_file(), f"missing current artifact: {relative}")
            payload = target.read_bytes()
            current_count += 1
        else:
            raise ValueError(f"unsupported resolution mode: {mode}")
        require(len(payload) == entry["bytes"], f"artifact size mismatch: {relative}")
        require(sha256_bytes(payload) == entry["sha256"], f"artifact digest mismatch: {relative}")

    require(claim_ids == {"P17-C1", "P17-C2", "P17-C3", "P17-C4", "P17-C5", "P17-C6", "P17-C7", "P17-C8", "P17-C9", "P17-O1"}, "claim surface mismatch")
    mechanism_claim = next(claim for claim in table["claims"] if claim["id"] == "P17-C9")
    mechanism_paths = {entry["path"] for entry in mechanism_claim["evidence"]}
    require(
        {
            "experiments/paper17/mechanism/results/mts1-v1.global-pair-tally.v1.json",
            "experiments/paper17/mechanism/results/mts1-v1.global-pair-tally.v1.validation-receipt.json",
            "experiments/paper17/mechanism/results/mts1-v1.zenodo-anchor.v1.json",
        } <= mechanism_paths,
        "mechanism evidence interface incomplete",
    )
    boundaries = table["global_boundaries"]
    require(not any(boundaries.values()), "one or more forbidden promotions are enabled")
    concept = table["canonical_wording"]["concept_sentence"]
    require("does not repair" in concept and "It eliminates them" in concept, "concept sentence mismatch")

    return {
        "schema": "rime.paper17.manuscript-evidence-table-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "HISTORICAL_GIT_ANCHOR_RESOLUTION",
        "independent_validation": False,
        "producer_replayed": False,
        "table": {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "anchor_commit": commit,
        "verified": {
            "claim_count": len(claim_ids),
            "historical_artifact_count": historical_count,
            "current_paper_owned_artifact_count": current_count,
            "minimal_memory_order_claimed": False,
            "exact_post_separation_transition_layer_contrast_bound": True,
            "initial_separation_trigger_identified": False,
            "causal_mechanism_identified": False,
            "coarse_endomap_verified": False,
            "current_head_substitution_used": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", type=Path, default=TABLE)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(args.table.resolve())
    if args.write_receipt:
        with DEFAULT_RECEIPT.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps(receipt, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
