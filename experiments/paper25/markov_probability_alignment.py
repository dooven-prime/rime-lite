"""Cross-layer alignment of Markov block bounds and probability diagnostics.

Probability lifting is admitted only for the coordinate singleton partition.
For rotated Hilbert frames, state-level probability observations remain valid,
but the operator blocks are not interpreted as transition probabilities.
"""

from __future__ import annotations

import json
from pathlib import Path
import platform

import numpy as np

from experiments.paper25.markov_stability import (
    BLOCK_ACTIVITY_THRESHOLD,
    MARKOV_POSITIVE_SUPPORT_THRESHOLD,
    _stationary_eigenvalue_separation,
)
from experiments.paper25.markov_helpers import (
    eventual_hit_probability,
)
from experiments.paper25.markov_helpers import (
    expected_hitting_time,
    stationary_distribution,
    support_reachable,
)


SCHEMA = "rime.paper25.markov-probability-alignment.v1"
STABILITY_RESULT = Path(__file__).resolve().parent / "results" / "nonnormal_markov_stability_v1.json"
ALIGNMENT_TOLERANCE = 2e-12


def _probability_values(transition: np.ndarray) -> dict:
    stationary = stationary_distribution(transition)
    return {
        "stationary_distribution": None if stationary is None else stationary.tolist(),
        "positive_support_reachable_state_0_to_state_1": support_reachable(
            transition, 0, {1}
        ),
        "eventual_hit_probability_state_0_to_state_1": eventual_hit_probability(
            transition, 0, {1}
        ),
        "expected_hitting_time_state_0_to_state_1": expected_hitting_time(
            transition, 0, {1}
        ),
        "stationary_eigenvalue_separation": _stationary_eigenvalue_separation(
            transition
        ),
    }


def _interval_lift(reference_probability: float, reverse_probability: float, bound: float) -> dict:
    lower = max(0.0, reference_probability - bound)
    upper = min(1.0, reference_probability + bound)
    support_certified = lower > 0.0
    target_mass_lower = lower / (lower + reverse_probability) if lower > 0.0 else 0.0
    target_mass_upper = upper / (upper + reverse_probability)
    return {
        "transition_probability_interval": [lower, upper],
        "positive_edge_persistence": (
            "CERTIFIED" if support_certified else "UNRESOLVED"
        ),
        "eventual_hit_probability_one": (
            "CERTIFIED_FOR_DECLARED_TWO_STATE_FAMILY"
            if support_certified
            else "UNRESOLVED"
        ),
        "expected_hitting_time_interval": [
            1.0 / upper,
            1.0 / lower if support_certified else None,
        ],
        "stationary_target_mass_interval": [target_mass_lower, target_mass_upper],
        "stationary_eigenvalue_separation_interval": [
            reverse_probability + lower,
            reverse_probability + upper,
        ],
    }


def _contains(interval: list[float | None], value: float, tolerance: float = ALIGNMENT_TOLERANCE) -> bool:
    lower, upper = interval
    if lower is not None and value < lower - tolerance:
        return False
    if upper is not None and value > upper + tolerance:
        return False
    return True


def _aligned_record(parent: dict, transition: np.ndarray) -> dict:
    directed = {
        (row["source_sector"], row["target_sector"]): row
        for row in parent["directed_offdiagonal_blocks"]
    }
    forward = directed[(0, 1)]
    forward_probability = float(transition[0, 1])
    reverse_probability = float(transition[1, 0])
    probability = _probability_values(transition)
    global_lift = _interval_lift(0.1, reverse_probability, forward["global_bound"])
    localized_lift = _interval_lift(
        0.1, reverse_probability, forward["localized_bound"]
    )
    expected_time = float(probability["expected_hitting_time_state_0_to_state_1"])
    target_mass = float(probability["stationary_distribution"][1])
    separation = float(probability["stationary_eigenvalue_separation"])
    for lift in (global_lift, localized_lift):
        lift["actual_probability_contained"] = _contains(
            lift["transition_probability_interval"], forward_probability
        )
        lift["actual_expected_hitting_time_contained"] = _contains(
            lift["expected_hitting_time_interval"], expected_time
        )
        lift["actual_stationary_target_mass_contained"] = _contains(
            lift["stationary_target_mass_interval"], target_mass
        )
        lift["actual_stationary_eigenvalue_separation_contained"] = _contains(
            lift["stationary_eigenvalue_separation_interval"], separation
        )
    return {
        "alignment_status": "ALIGNED_SINGLETON_STATE_PARTITION",
        "probability_lift_status": "ADMITTED",
        "forward_coordinate": {
            "source_state": 0,
            "target_state": 1,
            "transition_probability": forward_probability,
            "operator_block_frobenius": forward["perturbed_block_frobenius"],
            "block_probability_equality_residual": abs(
                forward_probability - forward["perturbed_block_frobenius"]
            ),
            "markov_positive_support": (
                forward_probability > MARKOV_POSITIVE_SUPPORT_THRESHOLD
            ),
            "block_activity_above_threshold": (
                forward["perturbed_block_frobenius"] > BLOCK_ACTIVITY_THRESHOLD
            ),
            "positive_support_equals_block_activity": (
                (forward_probability > MARKOV_POSITIVE_SUPPORT_THRESHOLD)
                == (forward["perturbed_block_frobenius"] > BLOCK_ACTIVITY_THRESHOLD)
            ),
        },
        "probability_observations": probability,
        "global_probability_lift": global_lift,
        "localized_probability_lift": localized_lift,
    }


def _incomparable_record(parent: dict, transition: np.ndarray) -> dict:
    return {
        "alignment_status": "INCOMPARABLE_ROTATED_HILBERT_FRAME",
        "probability_lift_status": "NOT_ADMITTED",
        "reason": (
            "the rotated orthogonal projectors are not a set-valued partition "
            "of the Markov states"
        ),
        "probability_observations": _probability_values(transition),
        "global_probability_lift": None,
        "localized_probability_lift": None,
    }


def build_payload(stability_payload: dict | None = None) -> dict:
    if stability_payload is None:
        stability_payload = json.loads(STABILITY_RESULT.read_text(encoding="utf-8"))
    records = []
    for parent in stability_payload["records"]:
        transition = np.asarray(parent["state_level_transition_matrix"], dtype=float)
        cross_layer = (
            _aligned_record(parent, transition)
            if parent["sector_semantics"] == "COORDINATE_STATE_PARTITION"
            else _incomparable_record(parent, transition)
        )
        records.append(
            {
                "sweep_axis": parent["sweep_axis"],
                "level_index": parent["level_index"],
                "epsilon_operator_norm": parent["epsilon_operator_norm"],
                "eta_sector_rotation_radians": parent[
                    "eta_sector_rotation_radians"
                ],
                **cross_layer,
            }
        )

    return {
        "schema": SCHEMA,
        "bundle_id": "numerical-representation-diagnostics.markov-probability-alignment.v1",
        "artifact_role": "PAPER25_MARKOV_ALIGNMENT_EVIDENCE",
        "claim_status": "BOUNDED_NUMERICAL_OBSERVATION",
        "paper_evidence_status": "REGISTERED_SUPPORT_NOT_THEOREM_PROOF",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "arithmetic": "float64",
        },
        "parent_bundle": {
            "bundle_id": stability_payload["bundle_id"],
            "schema": stability_payload["schema"],
        },
        "typed_alignment_rule": (
            "For coordinate singleton sectors, ||Q_i P Q_j||_F = P[i,j] "
            "because P[i,j] is nonnegative. Rotated Hilbert frames do not "
            "admit this Markov probability interpretation."
        ),
        "two_state_probability_model": {
            "form": "P=[[1-a,a],[b,1-b]]",
            "fixed_reverse_probability_b": 0.2,
            "identities": {
                "expected_hitting_time_0_to_1": "1/a for a>0",
                "stationary_target_mass": "a/(a+b)",
                "stationary_eigenvalue_separation": "sep_1=|1-lambda_2|=a+b",
                "eventual_hit_probability_0_to_1": "1 for a>0",
            },
        },
        "records": records,
        "negative_boundaries": [
            "Positive Markov support is not the same as thresholded block activity.",
            "Support reachability alone does not imply almost-sure hitting for an arbitrary Markov chain.",
            "The probability lift uses the declared two-state family and singleton state partition.",
            "No probability lift is admitted from a rotated Hilbert sector frame.",
            "A block perturbation bound does not generally bound stationary or hitting diagnostics without additional model structure.",
            "The stationary-eigenvalue separation interval is not a general nonnormal spectral-stability theorem.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(build_payload(), indent=2))
