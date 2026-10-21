"""Hostile controls for the downstream Paper XL fixed-controls audit."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.release.verify_paper40_fixed_controls import (
    tagged_bytes,
    validate_fixed_controls,
)


def tagged_inputs() -> tuple[dict, bytes]:
    record = json.loads(tagged_bytes(ROOT, "experiments/paper40/results/q2-controls.v1.json"))
    archive = tagged_bytes(ROOT, "experiments/paper40/source/q2-source-v1.zip")
    return record, archive


def test_fixed_controls_in_tag_pass() -> None:
    validate_fixed_controls(*tagged_inputs())


def test_current_v1_package_keeps_fixed_controls() -> None:
    package = ROOT / "experiments/paper40"
    record = json.loads((package / "results/q2-controls.v1.json").read_bytes())
    archive = (package / "source/q2-source-v1.zip").read_bytes()
    validate_fixed_controls(record, archive)


def test_fixed_controls_reject_narrowed_claims() -> None:
    original, archive = tagged_inputs()
    for mutation in (
        "duplicate_cases", "missing_scope", "changed_fiber_count", "changed_matched",
        "changed_continuation", "changed_producer_binding",
    ):
        record = copy.deepcopy(original)
        fixed = record["fixed_controls"]
        if mutation == "duplicate_cases":
            fixed["cases"] = [fixed["cases"][0]] * 9
        elif mutation == "missing_scope":
            del fixed["scope"]
        elif mutation == "changed_fiber_count":
            fixed["cases"][5]["operator"]["fibers"] = 84
        elif mutation == "changed_matched":
            fixed["matched"] = []
        elif mutation == "changed_continuation":
            fixed["same_invocation"]["trace"][-1] = [4, 4, 0, 0]
        elif mutation == "changed_producer_binding":
            fixed["upstream_commit"] = "0" * 40
        try:
            validate_fixed_controls(record, archive)
        except (KeyError, ValueError):
            pass
        else:
            raise AssertionError(f"fixed-control mutation accepted: {mutation}")


if __name__ == "__main__":
    test_fixed_controls_in_tag_pass()
    test_current_v1_package_keeps_fixed_controls()
    test_fixed_controls_reject_narrowed_claims()
    print("test_paper40_post_release_audit.py: OK")
