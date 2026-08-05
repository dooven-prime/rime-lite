"""Independently validate the Paper XI Rubik collision result."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = Path(__file__).parent / "inputs" / "rubik_collision_points_v1.json"
RESULT_PATH = ROOT / "experiments" / "paper11" / "results" / "rubik_collision_quotient_result_v1.json"
CERT_PATH = ROOT / "experiments" / "paper11" / "results" / "rubik_collision_quotient_validation_v1.json"
PRODUCER_PATH = Path(__file__).parent / "produce_collision_quotient_result.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    points = source["points"]
    counts = {key: 0 for key in ("parallel", "interior", "endpoint", "exterior")}
    critical = set()

    for left, right in combinations(points, 2):
        slope_left = Fraction(left["q"]) - Fraction(left["h"])
        slope_right = Fraction(right["q"]) - Fraction(right["h"])
        if slope_left == slope_right:
            counts["parallel"] += 1
            continue
        alpha = (Fraction(right["h"]) - Fraction(left["h"])) / (
            slope_left - slope_right
        )
        kind = "interior" if 0 < alpha < 1 else "endpoint" if alpha in {0, 1} else "exterior"
        counts[kind] += 1
        if kind == "interior":
            critical.add(alpha)

    layers = {}
    classes_at_two_thirds = {}
    for alpha in critical:
        values = {}
        for point in points:
            value = Fraction(point["h"]) + alpha * (
                Fraction(point["q"]) - Fraction(point["h"])
            )
            values.setdefault(value, []).append(point["id"])
        layers[str(alpha)] = len(values)
        if alpha == Fraction(2, 3):
            classes_at_two_thirds = {
                str(value): ids for value, ids in values.items() if len(ids) > 1
            }

    summary = result["summary"]
    assert result["canonical_input"]["sha256"] == sha256(INPUT_PATH)
    assert summary["pair_classification"] == counts
    assert summary["interior_layer_counts"] == dict(sorted(layers.items(), key=lambda item: Fraction(item[0])))
    assert summary["maximal_interior_collision_parameter"] == "2/3"
    assert summary["maximal_interior_layer_count"] == 6
    assert summary["maximal_interior_drop"] == 3
    assert sorted(classes_at_two_thirds.values()) == sorted(summary["maximal_collision_classes"])

    certificate = {
        "schema": "paper11-validation-certificate-v1.0",
        "claim_status": "Computational Certificate",
        "validator": "experiments/paper11/validation/validate_collision_quotient_result.py",
        "validator_version": "1.0",
        "validator_independence": {
            "implementation_relation": "separate_algorithm",
            "language_relation": "same_language",
            "runtime_relation": "separate_process",
            "input_source": "canonical_input_and_frozen_result",
            "producer_cache_used": False,
        },
        "canonical_input_sha256": sha256(INPUT_PATH),
        "producer_sha256": sha256(PRODUCER_PATH),
        "result_sha256": sha256(RESULT_PATH),
        "validator_sha256": sha256(Path(__file__)),
        "recomputed_summary": {
            "pair_classification": counts,
            "interior_layer_counts": dict(sorted(layers.items(), key=lambda item: Fraction(item[0]))),
            "maximal_collision_classes": sorted(classes_at_two_thirds.values()),
        },
        "claim_scope": result["claim_scope"],
        "validation_status": "passed",
    }
    CERT_PATH.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    print(f"wrote {CERT_PATH}")


if __name__ == "__main__":
    main()
