#!/usr/bin/env python3
"""Explicit authoring step: seal exact bytes, without claiming a release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from audit_scope import ARTIFACTS


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "experiments/paper37/development-manifest.json"


def main() -> None:
    rows = []
    for role, relative in ARTIFACTS:
        raw = (ROOT / relative).read_bytes()
        if b"\r" in raw:
            raise ValueError(f"non-LF file: {relative}")
        raw.decode("utf-8")
        rows.append({"path": relative, "role": role,
                     "sha256": hashlib.sha256(raw).hexdigest()})
    record = {
        "schema": "rime.paper37.development-manifest.v1",
        "paper_id": "PAPER37",
        "status": "DRAFT_PAPER_OWNED_CLOSURE",
        "release_identity_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "digest_policy": {
            "algorithm": "sha256", "scope": "exact_file_bytes",
            "path_resolution": "exact repository-relative path",
            "wildcards_allowed": False, "absolute_paths_allowed": False,
        },
        "evidence_boundary": "Bounded consistency controls and a partial Lean spine; manuscript owns the all-g proofs.",
        "excluded_dependencies": [
            "experiments/exploratory/",
            "experiments/synchronizing_automata/",
            "papers/unnumbered/",
            "published paper-owned experiment packages",
        ],
        "artifacts": rows,
    }
    MANIFEST.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8", newline="\n")
    print(f"PASS: sealed {len(rows)} development artifacts; no release identity")


if __name__ == "__main__":
    main()
