"""Cross-domain structural-signature discrimination boundary for Paper XIII.

There is one artifact per domain/failure label, so within-domain replication
is unavailable. This script reports only the cross-domain boundary result.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
DOMAINS = ("gridworld", "sir", "traffic", "compiler", "network")
FAILURE_TYPES = ("f1", "f2", "f3", "f4", "f5")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _opportunity_count(artifact: dict) -> int:
    reference_path = RESULTS / artifact["reference"]["artifact"]
    reference = _load(reference_path)
    matrix = reference["support_matrix"]["matrix"]
    n = len(matrix)
    if n < 2 or any(len(row) != n for row in matrix):
        raise ValueError(f"invalid reference support matrix in {reference_path}")
    return n * (n - 1)


def extract_structural_vector(artifact: dict) -> np.ndarray:
    """Return seven normalized structural coordinates."""

    opportunities = _opportunity_count(artifact)
    signature = artifact["signature"]
    frozen = signature["frozen_disagreement"]
    return np.array(
        [
            signature["support_mismatch"]["total_mismatch"],
            signature["bridge_word_mismatch"]["total_mismatch"],
            signature["bridge_lie_mismatch"]["total_mismatch"],
            signature["depth_distortion"]["total_mismatch"],
            abs(frozen["frozen_R1"]["delta"]),
            abs(frozen["frozen_D_word"]["delta"]),
            abs(frozen["frozen_D_lie"]["delta"]),
        ],
        dtype=float,
    ) / opportunities


def structural_l1(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sum(np.abs(left - right)))


def analyze() -> dict[str, float | int | str]:
    vectors: dict[str, np.ndarray] = {}
    for domain in DOMAINS:
        for failure in FAILURE_TYPES:
            stem = f"{domain}_{failure}"
            path = RESULTS / f"{stem}.sofaudit"
            if path.is_file():
                vectors[stem] = extract_structural_vector(_load(path))

    same_label: list[float] = []
    different_label: list[float] = []
    stems = sorted(vectors)
    for index, left in enumerate(stems):
        for right in stems[index + 1 :]:
            distance = structural_l1(vectors[left], vectors[right])
            left_label = left.rsplit("_", 1)[1]
            right_label = right.rsplit("_", 1)[1]
            if left_label == right_label:
                same_label.append(distance)
            else:
                different_label.append(distance)

    same_mean = float(np.mean(same_label))
    different_mean = float(np.mean(different_label))
    ratio = different_mean / same_mean if same_mean else np.inf
    return {
        "artifacts": len(vectors),
        "same_label_cross_domain_mean": same_mean,
        "different_label_cross_domain_mean": different_mean,
        "separation_ratio": ratio,
        "claim_status": "boundary",
        "within_domain_replication": "unavailable",
    }


def main() -> None:
    result = analyze()
    print("Paper XIII cross-domain discrimination boundary")
    for name, value in result.items():
        if isinstance(value, float):
            print(f"  {name}: {value:.4f}")
        else:
            print(f"  {name}: {value}")
    print("Boundary: shared failure labels do not establish domain-independent classes.")


if __name__ == "__main__":
    main()
