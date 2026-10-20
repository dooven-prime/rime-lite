"""Explicitly bind the Paper XL development subclosure; verification never repairs it."""

import hashlib
import json
from pathlib import Path

from artifact_scope import ARTIFACTS, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def manifest_data():
    artifacts = []
    for relative in ARTIFACTS:
        data = (ROOT / relative).read_bytes()
        if not relative.endswith(".zip"):
            data.decode("utf-8")
            require(b"\r" not in data, "non-LF candidate text: " + relative)
        artifacts.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})
    return {"schema": "rime.paper40.development-manifest.v1", "paper_id": "PAPER40",
            "status": "DRAFT_PAPER_OWNED_CLOSURE", "release_identity_claimed": False,
            "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
            "proof_ownership": "Manuscript owns the theorems; code and bounded controls are supplementary.",
            "excluded_dependencies": ["unnumbered working notes", "live sof-runtime checkout",
                                      "Git history during replay", "network", "external checking tools",
                                      "reader PDF", "validation receipt itself"],
            "artifacts": artifacts}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    (HERE / "development-manifest.json").write_text(
        json.dumps(manifest_data(), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("Development subclosure bound; release/publication identity is separate.")
