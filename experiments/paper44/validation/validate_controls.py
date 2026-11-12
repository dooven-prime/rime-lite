"""Validate the retained Paper XLIV finite report against actual replay."""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CONTROLS = HERE.parent / "controls"
sys.path.insert(0, str(CONTROLS))

from prefix_observer_spectrum_control import algebra_controls, finite_control


EXPECTED = {
    3: (30, [12, 12]),
    4: (176, [69, 71, 71]),
    5: (920, [402, 410, 414, 414]),
    6: (4566, [2085, 2283, 2303, 2311, 2311]),
    7: (22134, [9965, 11803, 12363, 12411, 12427, 12427]),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate() -> None:
    report = json.loads((CONTROLS / "results/prefix_observer_spectrum.v1.json").read_text("utf-8"))
    require(report["status"] == "PASS_BOUNDED_PREFIX_OBSERVER_CONTROL", "saved status differs")
    require(report["evidence"] == "BOUNDED_CONSISTENCY_ONLY", "evidence boundary differs")
    require(report["kernel_formalization_claimed"] is False, "finite report overclaims Lean")
    require(report["algebra_recovery_range"] == [3, 100], "algebra range differs")
    rows = report["finite_models"]
    require([row["n"] for row in rows] == list(EXPECTED), "finite model range differs")
    algebra_controls()
    for row in rows:
        n = row["n"]
        states, counts = EXPECTED[n]
        require(row["reachable_consumer_states"] == states, f"state count differs: n={n}")
        require([entry["depth"] for entry in row["depths"]] == list(range(1, n)),
                f"depth range differs: n={n}")
        require([entry["classes"] for entry in row["depths"]] == counts,
                f"quotient counts differ: n={n}")
        require(all(entry["full_partition_matches"] is True for entry in row["depths"]),
                f"partition status differs: n={n}")
        require(finite_control(n) == row, f"saved finite replay differs: n={n}")
    print("PASS Paper XLIV bounded controls: 5 models, 20 depth partitions")


if __name__ == "__main__":
    try:
        validate()
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise SystemExit(f"FAIL Paper XLIV bounded controls: {error}") from error
