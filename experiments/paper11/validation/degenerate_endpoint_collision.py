"""Post-release Paper XI candidate: constructed spectral endpoint collisions.

Claim status: constructed Class A witness.

The family H(t) = D + t V starts at a deliberately degenerate diagonal matrix
D and uses a GOE draw only for the splitting direction V.  It has two isolated
double eigenvalues at t=0.  The audit verifies that both pair gaps open linearly,
with the first-order coefficient predicted by degenerate perturbation theory.

This is not a generic one-parameter GOE crossing: a double eigenvalue has
codimension two in the real-symmetric ambient space.  Perturbing the endpoint D
off the discriminant removes both collisions.  Direction perturbations test
transversality conditional on retaining the constructed endpoint; they do not
establish unrestricted structural stability.  "A1-type" is used only in Paper
XI's pair-gap endpoint convention, not as a full Arnold classification theorem.

The script is not part of the frozen Paper XI v1.0 census.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIMENSION = 6
ENDPOINT_DIAGONAL = np.array([1.0, 1.0, 2.0, 3.0, 4.0, 4.0])
TARGET_PAIRS = [(0, 1), (4, 5)]
LOCAL_T = np.logspace(-8, -3, 13)
ISOLATION_T = np.linspace(0.0, 0.05, 51)
TOL = 1e-10


def goe_matrix(n: int, rng: np.random.RandomState) -> np.ndarray:
    matrix = rng.randn(n, n) / np.sqrt(n)
    return (matrix + matrix.T) / 2.0


def eigenvalues_at(t: float, direction: np.ndarray) -> np.ndarray:
    return np.linalg.eigvalsh(np.diag(ENDPOINT_DIAGONAL) + t * direction)


def first_order_coefficient(direction: np.ndarray, pair: tuple[int, int]) -> dict:
    block = direction[np.ix_(pair, pair)]
    coefficient = float(np.ptp(np.linalg.eigvalsh(block)))
    x = float((block[0, 0] - block[1, 1]) / 2.0)
    y = float(block[0, 1])
    conical_coefficient = float(2.0 * np.sqrt(x * x + y * y))
    return {
        "restricted_block": block.tolist(),
        "coefficient": coefficient,
        "conical_coefficient": conical_coefficient,
        "normal_coordinates": [x, y],
        "normal_form_residual": abs(coefficient - conical_coefficient),
    }


def local_gap_audit(direction: np.ndarray, pair: tuple[int, int]) -> dict:
    gaps = np.array(
        [eigenvalues_at(float(t), direction)[pair[1]] - eigenvalues_at(float(t), direction)[pair[0]]
         for t in LOCAL_T],
        dtype=float,
    )
    if np.any(gaps <= 0):
        raise AssertionError(f"target pair {pair} did not split on the local positive ray")
    fitted_order, log_prefactor = np.polyfit(np.log(LOCAL_T), np.log(gaps), 1)
    first_order = first_order_coefficient(direction, pair)
    relative_error = abs(gaps[0] / LOCAL_T[0] - first_order["coefficient"]) / max(
        first_order["coefficient"],
        TOL,
    )
    return {
        "pair": list(pair),
        "endpoint_gap": 0.0,
        "first_positive_parameter": float(LOCAL_T[0]),
        "first_positive_gap": float(gaps[0]),
        "fitted_order": float(fitted_order),
        "fitted_prefactor": float(np.exp(log_prefactor)),
        "gap_over_t_min": float(np.min(gaps / LOCAL_T)),
        "gap_over_t_max": float(np.max(gaps / LOCAL_T)),
        "first_order": first_order,
        "smallest_t_relative_error": float(relative_error),
    }


def non_target_isolation(direction: np.ndarray) -> float:
    non_target_indices = [1, 2, 3]
    minimum = np.inf
    for t in ISOLATION_T:
        gaps = np.diff(eigenvalues_at(float(t), direction))
        minimum = min(minimum, *(float(gaps[index]) for index in non_target_indices))
    return float(minimum)


def direction_robustness(draws: int, seed: int) -> dict:
    coefficients = {pair: [] for pair in TARGET_PAIRS}
    for offset in range(draws):
        direction = goe_matrix(DIMENSION, np.random.RandomState(seed + offset))
        for pair in TARGET_PAIRS:
            coefficients[pair].append(first_order_coefficient(direction, pair)["coefficient"])
    return {
        f"pair_{pair[0]}_{pair[1]}": {
            "minimum_coefficient": float(np.min(values)),
            "median_coefficient": float(np.median(values)),
            "nontransverse_draws": int(np.count_nonzero(np.array(values) <= TOL)),
        }
        for pair, values in coefficients.items()
    }


def endpoint_lifting_control() -> list[dict]:
    controls = []
    for epsilon in (1e-6, 1e-4, 1e-2):
        perturbed = ENDPOINT_DIAGONAL.copy()
        perturbed[1] += epsilon
        perturbed[5] += 2.0 * epsilon
        gaps = np.diff(np.linalg.eigvalsh(np.diag(perturbed)))
        controls.append(
            {
                "epsilon": epsilon,
                "pair_0_1_gap": float(gaps[0]),
                "pair_4_5_gap": float(gaps[4]),
                "collisions_retained": bool(gaps[0] <= TOL or gaps[4] <= TOL),
            }
        )
    return controls


def run_audit(seed: int = 42, robustness_draws: int = 32) -> dict:
    direction = goe_matrix(DIMENSION, np.random.RandomState(seed))
    endpoint_gaps = np.diff(np.linalg.eigvalsh(np.diag(ENDPOINT_DIAGONAL)))
    if not all(endpoint_gaps[left] <= TOL for left, _right in TARGET_PAIRS):
        raise AssertionError("constructed endpoint does not contain the declared double levels")

    collisions = [local_gap_audit(direction, pair) for pair in TARGET_PAIRS]
    for collision in collisions:
        if abs(collision["fitted_order"] - 1.0) > 0.02:
            raise AssertionError("target pair does not have a linear local gap opening")
        if collision["first_order"]["normal_form_residual"] > 1e-12:
            raise AssertionError("2x2 conical normal-form coefficient mismatch")

    isolation = non_target_isolation(direction)
    if isolation <= 0.5:
        raise AssertionError("target double levels are not isolated on the tested local interval")

    robustness = direction_robustness(robustness_draws, seed + 1000)
    if any(item["nontransverse_draws"] for item in robustness.values()):
        raise AssertionError("sampled endpoint-preserving direction failed transversality")

    lifting = endpoint_lifting_control()
    if any(item["collisions_retained"] for item in lifting):
        raise AssertionError("endpoint-lifting negative control did not remove both collisions")

    return {
        "record_version": "paper11-constructed-goe-endpoint-v1.0",
        "claim_status": "constructed_witness",
        "paper_xi_release_status": "post_v1_candidate",
        "taxonomy_candidates": ["A"],
        "species": "finite real-symmetric random-matrix family",
        "family": "H(t)=D+tV with constructed degenerate D and GOE direction V",
        "ambient_collision_codimension": 2,
        "collision_count": len(collisions),
        "collisions": collisions,
        "minimum_non_target_gap_on_local_interval": isolation,
        "direction_robustness": robustness,
        "endpoint_lifting_negative_control": lifting,
        "claim_boundary": (
            "constructed pair-gap endpoint witness; not a generic GOE crossing, "
            "unrestricted stability theorem, or full ADE classification"
        ),
        "trajectory_event": {
            "orientation": "endpoint_to_positive_parameter",
            "parameter_bracket": [0.0, float(LOCAL_T[0])],
            "before_state": {
                "adjacent_gaps": [
                    collision["endpoint_gap"] for collision in collisions
                ]
            },
            "after_state": {
                "adjacent_gaps": [
                    collision["first_positive_gap"] for collision in collisions
                ]
            },
            "raw_numeric_direction": "increase",
            "event_semantics": "collision_exit",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--robustness-draws", type=int, default=32)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_audit(seed=args.seed, robustness_draws=args.robustness_draws)
    print("=" * 72)
    print("  Paper XI candidate: constructed spectral endpoint collisions")
    print("=" * 72)
    for collision in result["collisions"]:
        first_order = collision["first_order"]
        print(
            f"pair {tuple(collision['pair'])}: order={collision['fitted_order']:.6f}, "
            f"first-order coefficient={first_order['coefficient']:.6f}, "
            f"gap/t=[{collision['gap_over_t_min']:.6f}, "
            f"{collision['gap_over_t_max']:.6f}]"
        )
    print(
        "Minimum non-target gap on t in [0, 0.05]: "
        f"{result['minimum_non_target_gap_on_local_interval']:.6f}"
    )
    for pair, audit in result["direction_robustness"].items():
        print(
            f"{pair}, endpoint-preserving directions: min coefficient="
            f"{audit['minimum_coefficient']:.6f}, "
            f"nontransverse={audit['nontransverse_draws']}"
        )
    print("Endpoint-lifting control: both constructed collisions removed at every epsilon")
    print("Claim boundary: " + result["claim_boundary"] + ".")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
