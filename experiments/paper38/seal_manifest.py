#!/usr/bin/env python3
"""Explicit authoring-time sealing; never invoked by read-only verification."""

import hashlib
import json
from pathlib import Path

from audit_scope import ARTIFACTS


ROOT = Path(__file__).resolve().parents[2]


def main():
    inventory = []
    for role, relative in ARTIFACTS:
        raw = (ROOT / relative).read_bytes()
        if b"\r" in raw:
            raise ValueError(f"non-LF artifact: {relative}")
        raw.decode("utf-8")
        inventory.append({"path": relative, "role": role, "size": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
    record = {
        "schema": "rime.paper38.development-manifest.v1", "paper_id": "PAPER38",
        "status": "DRAFT_PAPER_OWNED_CLOSURE", "release_identity_claimed": False,
        "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
        "formalization_claimed": "PARTIAL_ALGEBRAIC_SPINE",
        "digest_policy": {"algorithm": "sha256", "scope": "exact_file_bytes", "text_eol": "LF"},
        "proof_ownership": "The manuscript owns the data-independent theorems; finite controls are supplementary.",
        "excluded_dependencies": ["experiments/exploratory/", "experiments/synchronizing_automata/",
                                  "papers/unnumbered/", "upstream experiment workspaces"],
        "artifacts": inventory,
    }
    path = ROOT / "experiments/paper38/development-manifest.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: sealed {len(inventory)} Paper XXXVIII development artifacts; no release identity")


if __name__ == "__main__":
    main()
