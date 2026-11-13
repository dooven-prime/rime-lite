#!/usr/bin/env python3
"""Compare fresh All-R axiom output with the declared 69-target inventory."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/fusion_log_compression/lean_all_r/FusionLogAllR/AxiomAudit.lean"
sys.path.insert(0, str(ROOT / "experiments/fusion_log_compression/validation"))
from replay import parse_axiom_audit  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_all_r_audit.py AUDIT_OUTPUT")
    targets = re.findall(r"(?m)^#print axioms\s+(\S+)\s*$", SOURCE.read_text(encoding="utf-8"))
    if len(targets) != 69 or len(set(targets)) != 69:
        raise SystemExit("All-R audit source must name 69 distinct targets")
    output = Path(sys.argv[1]).read_text(encoding="utf-8")
    if re.search(r"\bsorryAx\b|declaration uses 'sorry'", output):
        raise SystemExit("placeholder in All-R axiom output")
    try:
        observations = parse_axiom_audit(output, targets)
    except RuntimeError as error:
        raise SystemExit(f"FAIL All-R axiom audit: {error}") from error
    print(f"PASS All-R axiom audit: {len(observations)} targets; only allowed axioms")


if __name__ == "__main__":
    main()
