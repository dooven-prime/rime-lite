"""Perturbation stability control for the retained nonnormal Markov carrier.

The transition convention is P[source, target].  Block-activity margins are
operator diagnostics and are kept separate from positive Markov support.
"""

from __future__ import annotations

import math
import platform

import numpy as np

from experiments.paper25.perturbation_sweep import (
    _ambient_block_difference,
    _coordinate_plane_rotation,
    _projector_delta_frobenius,
    _projector_difference_action_norm,
)
from experiments.paper25.markov_helpers import (
    eventual_hit_probability,
    expected_hitting_time,
    stationary_distribution,
    validate_transition,
)


SCHEMA = "rime.paper25.nonnormal-markov-stability.v1"
SWEEP_LEVELS = (0.0, 0.001, 0.01, 0.03, 0.05, 0.08, 0.1)
BLOCK_ACTIVITY_THRESHOLD = 0.15
MARKOV_POSITIVE_SUPPORT_THRESHOLD = 1e-12
BOUND_TOLERANCE = 2e-12


def _margin_status(reference_norm: float, bound: float) -> str:
    if reference_norm - bound > BLOCK_ACTIVITY_THRESHOLD:
        return "STABLE_ACTIVE"
    if reference_norm + bound <= BLOCK_ACTIVITY_THRESHOLD:
        return "STABLE_INACTIVE"
    return "UNRESOLVED"


def _aggregate_margin_status(reference_norms: np.ndarray, bounds: np.ndarray) -> str:
    lower = float(np.max(np.maximum(0.0, reference_norms - bounds)))
    upper = float(np.max(reference_norms + bounds))
    if lower > BLOCK_ACTIVITY_THRESHOLD:
        return "STABLE_ACTIVE"
    if upper <= BLOCK_ACTIVITY_THRESHOLD:
        return "STABLE_INACTIVE"
    return "UNRESOLVED"


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    return {
        status: statuses.count(status)
        for status in ("STABLE_ACTIVE", "STABLE_INACTIVE", "UNRESOLVED")
    }


def _reference_data() -> dict:
    transition = np.array([[0.9, 0.1], [0.2, 0.8]], dtype=float)
    projectors = [
        np.diag([1.0, 0.0]).astype(complex),
        np.diag([0.0, 1.0]).astype(complex),
    ]
    bases = []
    for projector in projectors:
        values, vectors = np.linalg.eigh(projector)
        basis = vectors[:, values > 0.5]
        if basis.shape[1] != 1:
            raise ValueError("the retained Markov control must have rank-one sectors")
        bases.append(basis)
    validate_transition(transition)
    return {
        "case_id": "non_normal_markov",
        "description": "positive row-stochastic Markov operator with coordinate sectors",
        "transition": transition,
        "bases": bases,
        "operator_norm": float(np.linalg.norm(transition, 2)),
    }


def _operator_perturbation(epsilon: float) -> np.ndarray:
    # Unit Frobenius/operator norm and zero row sums.
    return epsilon * np.array([[-1.0, 1.0], [0.0, 0.0]]) / math.sqrt(2.0)


def _normality_residual(operator: np.ndarray) -> float:
    adjoint = operator.conj().T
    return float(np.linalg.norm(adjoint @ operator - operator @ adjoint, "fro"))


def _stationary_eigenvalue_separation(operator: np.ndarray) -> float:
    values = list(np.linalg.eigvals(operator))
    stationary_index = min(
        range(len(values)), key=lambda index: abs(values[index] - 1.0)
    )
    nonstationary = [
        value for index, value in enumerate(values) if index != stationary_index
    ]
    if not nonstationary:
        return 0.0
    return float(min(abs(1.0 - value) for value in nonstationary))


def _status_violation(status: str, observed_norm: float) -> int:
    if status == "STABLE_ACTIVE" and observed_norm <= BLOCK_ACTIVITY_THRESHOLD:
        return 1
    if status == "STABLE_INACTIVE" and observed_norm > BLOCK_ACTIVITY_THRESHOLD:
        return 1
    return 0


def _evaluate_point(reference: dict, epsilon: float, eta: float) -> dict:
    transition = reference["transition"]
    reference_bases = reference["bases"]
    operator_norm = reference["operator_norm"]

    sector_transform = _coordinate_plane_rotation(2, 0, 1, eta)
    perturbed_bases = [sector_transform @ basis for basis in reference_bases]
    projector_deltas = [
        _projector_delta_frobenius(perturbed, nominal)
        for perturbed, nominal in zip(perturbed_bases, reference_bases)
    ]

    perturbation = _operator_perturbation(epsilon)
    perturbed_transition = transition + perturbation
    validate_transition(perturbed_transition)

    directed_rows = []
    global_statuses: list[str] = []
    localized_statuses: list[str] = []
    reference_norms = []
    perturbed_norms = []
    global_bounds = []
    localized_bounds = []
    global_bound_violations = 0
    localized_bound_violations = 0
    global_status_violations = 0
    localized_status_violations = 0

    for source_sector in range(2):
        for target_sector in range(2):
            if source_sector == target_sector:
                continue
            source_basis = reference_bases[source_sector]
            target_basis = reference_bases[target_sector]
            perturbed_source_basis = perturbed_bases[source_sector]
            perturbed_target_basis = perturbed_bases[target_sector]

            reference_block = source_basis.conj().T @ transition @ target_basis
            perturbed_block = (
                perturbed_source_basis.conj().T
                @ perturbed_transition
                @ perturbed_target_basis
            )
            global_bound = operator_norm * (
                projector_deltas[source_sector]
                + projector_deltas[target_sector]
            ) + epsilon
            left_local = _projector_difference_action_norm(
                perturbed_source_basis,
                source_basis,
                transition @ perturbed_target_basis,
            )
            middle_local = float(
                np.linalg.norm(
                    perturbed_source_basis.conj().T
                    @ perturbation
                    @ perturbed_target_basis,
                    "fro",
                )
            )
            right_local = _projector_difference_action_norm(
                perturbed_target_basis,
                target_basis,
                transition.conj().T @ source_basis,
            )
            localized_bound = left_local + middle_local + right_local
            actual_difference = _ambient_block_difference(
                perturbed_block,
                reference_block,
                perturbed_source_basis,
                source_basis,
                perturbed_target_basis,
                target_basis,
            )
            reference_norm = float(np.linalg.norm(reference_block, "fro"))
            perturbed_norm = float(np.linalg.norm(perturbed_block, "fro"))
            global_status = _margin_status(reference_norm, global_bound)
            localized_status = _margin_status(reference_norm, localized_bound)

            global_bound_violations += int(
                actual_difference > global_bound + BOUND_TOLERANCE
            )
            localized_bound_violations += int(
                actual_difference > localized_bound + BOUND_TOLERANCE
            )
            global_status_violations += _status_violation(
                global_status, perturbed_norm
            )
            localized_status_violations += _status_violation(
                localized_status, perturbed_norm
            )
            global_statuses.append(global_status)
            localized_statuses.append(localized_status)
            reference_norms.append(reference_norm)
            perturbed_norms.append(perturbed_norm)
            global_bounds.append(global_bound)
            localized_bounds.append(localized_bound)
            directed_rows.append(
                {
                    "source_sector": source_sector,
                    "target_sector": target_sector,
                    "reference_block_frobenius": reference_norm,
                    "perturbed_block_frobenius": perturbed_norm,
                    "actual_ambient_block_difference": actual_difference,
                    "global_bound": global_bound,
                    "localized_bound": localized_bound,
                    "global_margin_status": global_status,
                    "localized_margin_status": localized_status,
                }
            )

    reference_array = np.asarray(reference_norms)
    perturbed_array = np.asarray(perturbed_norms)
    global_array = np.asarray(global_bounds)
    localized_array = np.asarray(localized_bounds)
    global_aggregate = _aggregate_margin_status(reference_array, global_array)
    localized_aggregate = _aggregate_margin_status(reference_array, localized_array)
    observed_aggregate_active = (
        float(np.max(perturbed_array)) > BLOCK_ACTIVITY_THRESHOLD
    )

    def aggregate_violation(status: str) -> int:
        if status == "STABLE_ACTIVE" and not observed_aggregate_active:
            return 1
        if status == "STABLE_INACTIVE" and observed_aggregate_active:
            return 1
        return 0

    actual_array = np.asarray(
        [row["actual_ambient_block_difference"] for row in directed_rows]
    )
    global_ratios = np.divide(
        actual_array,
        global_array,
        out=np.zeros_like(actual_array),
        where=global_array > 0.0,
    )
    localized_ratios = np.divide(
        actual_array,
        localized_array,
        out=np.zeros_like(actual_array),
        where=localized_array > 0.0,
    )

    transition_real = np.asarray(perturbed_transition, dtype=float)
    stationary = stationary_distribution(transition_real)
    row_residual = float(np.max(np.abs(transition_real.sum(axis=1) - 1.0)))
    minimum_entry = float(np.min(transition_real))
    normality_residual = _normality_residual(perturbed_transition)
    return {
        "epsilon_operator_norm": epsilon,
        "epsilon_operator_frobenius": epsilon,
        "eta_sector_rotation_radians": eta,
        "state_level_transition_matrix": transition_real.tolist(),
        "projector_delta_frobenius": projector_deltas,
        "sector_semantics": (
            "COORDINATE_STATE_PARTITION"
            if eta == 0.0
            else "HILBERT_FRAME_ONLY_NOT_STATE_PARTITION"
        ),
        "kernel_checks": {
            "row_stochastic_residual_max_abs": row_residual,
            "minimum_entry": minimum_entry,
            "nonnegative": minimum_entry >= -MARKOV_POSITIVE_SUPPORT_THRESHOLD,
            "positive_support_edge_count": int(
                np.sum(transition_real > MARKOV_POSITIVE_SUPPORT_THRESHOLD)
            ),
            "normality_residual_frobenius": normality_residual,
            "normality_status": (
                "PASS" if normality_residual <= MARKOV_POSITIVE_SUPPORT_THRESHOLD else "FAIL"
            ),
        },
        "probability_observations": {
            "claim_status": "BOUNDED_COMPUTATIONAL_OBSERVATION",
            "state_level_only": True,
            "stationary_distribution": None if stationary is None else stationary.tolist(),
            "stationary_eigenvalue_separation": _stationary_eigenvalue_separation(
                transition_real
            ),
            "eventual_hit_probability_state_0_to_state_1": eventual_hit_probability(
                transition_real, 0, {1}
            ),
            "expected_hitting_time_state_0_to_state_1": expected_hitting_time(
                transition_real, 0, {1}
            ),
        },
        "directed_offdiagonal_blocks": directed_rows,
        "global_bound": {
            "maximum": float(np.max(global_array)),
            "maximum_actual_to_bound_ratio": float(np.max(global_ratios)),
            "bound_violation_count": global_bound_violations,
            "directed_margin_counts": _count_statuses(global_statuses),
            "directed_status_violation_count": global_status_violations,
            "aggregate_undirected_status": global_aggregate,
            "aggregate_status_violation_count": aggregate_violation(global_aggregate),
        },
        "localized_bound": {
            "maximum": float(np.max(localized_array)),
            "maximum_actual_to_bound_ratio": float(np.max(localized_ratios)),
            "bound_violation_count": localized_bound_violations,
            "directed_margin_counts": _count_statuses(localized_statuses),
            "directed_status_violation_count": localized_status_violations,
            "aggregate_undirected_status": localized_aggregate,
            "aggregate_status_violation_count": aggregate_violation(
                localized_aggregate
            ),
        },
    }


def build_payload() -> dict:
    reference = _reference_data()
    axes = {
        "OPERATOR_ONLY": [(level, 0.0) for level in SWEEP_LEVELS],
        "SECTORIZATION_ONLY": [(0.0, level) for level in SWEEP_LEVELS],
        "COUPLED": [(level, level) for level in SWEEP_LEVELS],
    }
    records = []
    for axis, points in axes.items():
        for level_index, (epsilon, eta) in enumerate(points):
            records.append(
                {
                    "sweep_axis": axis,
                    "level_index": level_index,
                    **_evaluate_point(reference, epsilon, eta),
                }
            )

    return {
        "schema": SCHEMA,
        "bundle_id": "numerical-representation-diagnostics.nonnormal-markov-stability.v1",
        "artifact_role": "PAPER25_NONNORMAL_MARKOV_STABILITY_EVIDENCE",
        "claim_status": "BOUNDED_NUMERICAL_OBSERVATION",
        "paper_evidence_status": "REGISTERED_SUPPORT_NOT_THEOREM_PROOF",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "arithmetic": "float64/complex128",
        },
        "carrier": {
            "source_case_id": reference["case_id"],
            "description": reference["description"],
            "dimension": 2,
            "transition_convention": "P[source,target] is row-stochastic",
            "nominal_transition": reference["transition"].tolist(),
            "nominal_operator_norm": reference["operator_norm"],
            "nominal_sectorization": "coordinate singleton state partition {{0},{1}}",
        },
        "perturbation_model": {
            "operator": "E = epsilon [[-1,1],[0,0]]/sqrt(2)",
            "operator_constraints": [
                "||E||_2 = ||E||_F = epsilon",
                "every row sum of E is zero",
                "P+E remains nonnegative on the retained sweep",
            ],
            "sectorization": "Q'_i = W_eta Q_i W_eta*",
        },
        "stability_bound": {
            "global": (
                "||Q'_i P' Q'_j-Q_i P Q_j||_F <= ||Delta_i||_F "
                "||P||_2+||E||_F+||P||_2||Delta_j||_F"
            ),
            "localized": (
                "||Q'_i P' Q'_j-Q_i P Q_j||_F <= "
                "||Delta_i P Q'_j||_F+||Q'_i E Q'_j||_F+"
                "||Q_i P Delta_j||_F"
            ),
            "unitarity_assumed": False,
            "comparison_tolerance": BOUND_TOLERANCE,
        },
        "block_activity_policy": {
            "threshold": BLOCK_ACTIVITY_THRESHOLD,
            "meaning": "operator block-strength diagnostic, not Markov positive support",
            "stable_active": "reference_norm - bound > threshold",
            "stable_inactive": "reference_norm + bound <= threshold",
            "unresolved": "otherwise",
        },
        "markov_positive_support_policy": {
            "threshold": MARKOV_POSITIVE_SUPPORT_THRESHOLD,
            "meaning": "strictly positive transition entries above numerical tolerance",
        },
        "sweep_levels": list(SWEEP_LEVELS),
        "records": records,
        "negative_boundaries": [
            "The block-activity threshold is not the Markov positive-support threshold.",
            "A rotated Hilbert sector frame is not a set-valued Markov state partition.",
            "The probability diagnostics concern the state-level kernel only.",
            "Block stability does not imply spectral or pseudospectral stability for a nonnormal operator.",
            "UNRESOLVED is a margin status, not an exact-zero or exact-nonzero claim.",
            "This finite sweep is not a universal Markov robustness theorem.",
        ],
    }
