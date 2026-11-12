"""Compare a fresh Lean axiom-audit output with the frozen finite milestone."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


LEAN = Path(__file__).resolve().parents[1] / "lean"
sys.path.insert(0, str(LEAN))

from freeze_structure_count import audit_axioms, source_inventory


def validate(output_path: Path) -> None:
    manifest = json.loads((LEAN / "milestones/structure-count-v1/manifest.json").read_text("utf-8"))
    if source_inventory() != manifest["source_sha256"]:
        raise ValueError("Lean proof input bytes differ from frozen milestone")
    actual = audit_axioms(output_path.read_text("utf-8"))
    if actual != manifest["axiom_audit"]:
        raise ValueError("Lean axiom outputs differ from frozen milestone")
    print(f"PASS Paper XLIV finite Lean axiom audit: {len(actual)} declarations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        validate(args.output)
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise SystemExit(f"FAIL Paper XLIV finite Lean axiom audit: {error}") from error
