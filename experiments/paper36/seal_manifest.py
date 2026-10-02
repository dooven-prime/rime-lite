#!/usr/bin/env python3
"""Refresh the exact-byte Paper XXXVI draft closure after intentional edits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "experiments" / "paper36" / "development-manifest.json"
ARTIFACTS = (
    ("canonical-manuscript", "papers/paper36/Paper XXXVI.md"),
    ("paper-local-bibliography", "papers/paper36/references-v1.bib"),
    ("finite-producer", "experiments/paper36/signed_lane_audit.py"),
    ("bounded-result", "experiments/paper36/results/signed_lane_audit_v1.json"),
    ("manifest-sealer", "experiments/paper36/seal_manifest.py"),
    ("local-validator", "experiments/paper36/validation/validate_package.py"),
)


def main() -> None:
    rows = []
    for role, relative in ARTIFACTS:
        path = ROOT / relative
        rows.append({
            "role": role,
            "path": relative,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    payload = {
        "schema": "rime.paper36.development-manifest.v1",
        "paper_id": "PAPER36",
        "status": "DRAFT_PAPER_OWNED_CLOSURE",
        "release_identity_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "digest_policy": {
            "algorithm": "sha256",
            "scope": "exact_file_bytes",
            "path_resolution": "exact repository-relative path",
            "wildcards_allowed": False,
            "absolute_paths_allowed": False,
        },
        "artifacts": rows,
    }
    MANIFEST.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"PASS: sealed {len(rows)} draft artifacts")


if __name__ == "__main__":
    main()
