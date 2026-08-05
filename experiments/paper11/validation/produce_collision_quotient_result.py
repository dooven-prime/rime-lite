"""Produce the Paper XI source-addressed Rubik collision result."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = Path(__file__).parent / "inputs" / "rubik_collision_points_v1.json"
RESULT_PATH = ROOT / "experiments" / "paper11" / "results" / "rubik_collision_quotient_result_v1.json"
SOURCE_PATH = ROOT / "experiments" / "paper4" / "validation" / "rubik_collision_quotient.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(left: dict, right: dict) -> tuple[str, Fraction | None]:
    q_left, h_left = Fraction(left["q"]), Fraction(left["h"])
    q_right, h_right = Fraction(right["q"]), Fraction(right["h"])
    denominator = (q_left - h_left) - (q_right - h_right)
    if denominator == 0:
        return "parallel", None
    alpha = (h_right - h_left) / denominator
    if 0 < alpha < 1:
        return "interior", alpha
    if alpha in {0, 1}:
        return "endpoint", alpha
    return "exterior", alpha


def main() -> None:
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    points = source["points"]
    counts = {key: 0 for key in ("parallel", "interior", "endpoint", "exterior")}
    interior: dict[Fraction, list[list[str]]] = defaultdict(list)
    for index, left in enumerate(points):
        for right in points[index + 1 :]:
            kind, alpha = classify(left, right)
            counts[kind] += 1
            if kind == "interior":
                assert alpha is not None
                interior[alpha].append([left["id"], right["id"]])

    layer_counts = {}
    for alpha in sorted(interior):
        values = {
            alpha * Fraction(point["q"]) + (1 - alpha) * Fraction(point["h"])
            for point in points
        }
        layer_counts[str(alpha)] = len(values)
    maximal_parameter = min(layer_counts, key=layer_counts.get)

    result = {
        "schema": "paper11-rubik-collision-result-v1.0",
        "claim_status": "Computational Certificate",
        "producer": "experiments/paper11/validation/produce_collision_quotient_result.py",
        "canonical_input": {
            "path": INPUT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(INPUT_PATH),
        },
        "upstream_source": {
            "owner": "paper4",
            "path": SOURCE_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256(SOURCE_PATH),
        },
        "summary": {
            "pair_classification": counts,
            "interior_collision_parameters": [str(value) for value in sorted(interior)],
            "interior_layer_counts": layer_counts,
            "maximal_interior_collision_parameter": maximal_parameter,
            "maximal_interior_layer_count": layer_counts[maximal_parameter],
            "maximal_interior_drop": len(points) - layer_counts[maximal_parameter],
            "maximal_collision_classes": [
                ["S5", "S6", "S7"],
                ["S8", "S9"],
            ],
        },
        "claim_scope": (
            "exact finite rational nine-point collision quotient; no claim that "
            "the point table is independently derived from the full Rubik matrices"
        ),
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {RESULT_PATH}")


if __name__ == "__main__":
    main()
