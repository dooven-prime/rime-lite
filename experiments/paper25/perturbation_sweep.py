"""Perturbation sweep for Rubik generator-resolved block diagnostics.

The sweep distinguishes additive operator perturbations E_a from projector
perturbations Delta_i.  Every block checks the declared Frobenius/operator-norm
stability bound before support margins are classified.
"""

from __future__ import annotations

import math
import platform

import numpy as np
import scipy

from rime.cubie import CubieMove
from rime.cubieoperator import CubieSpectralOperator

from experiments.paper25.rubik_transport import (
    EXPECTED_SECTOR_DIMENSIONS,
    _generator_label,
    _plane_rotation,
)


SCHEMA = "rime.paper25.rubik-perturbation-sweep.v1"
SUPPORT_THRESHOLD = 5e-2
SWEEP_LEVELS = (0.0, 1e-6, 1e-4, 1e-3, 1e-2, 5e-2)
BOUND_TOLERANCE = 2e-10


def _sector_slices(dimensions: list[int]) -> list[slice]:
    result = []
    start = 0
    for dimension in dimensions:
        result.append(slice(start, start + dimension))
        start += dimension
    return result


def _coordinate_plane_rotation(
    dimension: int, first: int, second: int, theta: float
) -> np.ndarray:
    transform = np.eye(dimension, dtype=complex)
    cosine = math.cos(theta)
    sine = math.sin(theta)
    transform[first, first] = cosine
    transform[second, second] = cosine
    transform[first, second] = -sine
    transform[second, first] = sine
    return transform


def _projector_delta_frobenius(
    perturbed_basis: np.ndarray, reference_basis: np.ndarray
) -> float:
    support = np.flatnonzero(
        np.maximum(
            np.max(np.abs(perturbed_basis), axis=1),
            np.max(np.abs(reference_basis), axis=1),
        )
        > 1e-14
    )
    perturbed_local = perturbed_basis[support, :]
    reference_local = reference_basis[support, :]
    difference = (
        perturbed_local @ perturbed_local.conj().T
        - reference_local @ reference_local.conj().T
    )
    return float(np.linalg.norm(difference, "fro"))


def _ambient_block_difference(
    perturbed_block: np.ndarray,
    reference_block: np.ndarray,
    perturbed_target_basis: np.ndarray,
    reference_target_basis: np.ndarray,
    perturbed_source_basis: np.ndarray,
    reference_source_basis: np.ndarray,
) -> float:
    target_support = np.flatnonzero(
        np.maximum(
            np.max(np.abs(perturbed_target_basis), axis=1),
            np.max(np.abs(reference_target_basis), axis=1),
        )
        > 1e-14
    )
    source_support = np.flatnonzero(
        np.maximum(
            np.max(np.abs(perturbed_source_basis), axis=1),
            np.max(np.abs(reference_source_basis), axis=1),
        )
        > 1e-14
    )
    perturbed_ambient = (
        perturbed_target_basis[target_support, :]
        @ perturbed_block
        @ perturbed_source_basis[source_support, :].conj().T
    )
    reference_ambient = (
        reference_target_basis[target_support, :]
        @ reference_block
        @ reference_source_basis[source_support, :].conj().T
    )
    return float(np.linalg.norm(perturbed_ambient - reference_ambient, "fro"))


def _margin_status(reference_norm: float, bound: float) -> str:
    if reference_norm - bound > SUPPORT_THRESHOLD:
        return "STABLE_ACTIVE"
    if reference_norm + bound <= SUPPORT_THRESHOLD:
        return "STABLE_INACTIVE"
    return "UNRESOLVED"


def _projector_difference_action_norm(
    perturbed_basis: np.ndarray,
    reference_basis: np.ndarray,
    vectors: np.ndarray,
) -> float:
    perturbed_projection = perturbed_basis @ (perturbed_basis.conj().T @ vectors)
    reference_projection = reference_basis @ (reference_basis.conj().T @ vectors)
    return float(np.linalg.norm(perturbed_projection - reference_projection, "fro"))


def _aggregate_margin_status(
    reference_norms: np.ndarray, bounds: np.ndarray
) -> str:
    lower = float(np.max(np.maximum(0.0, reference_norms - bounds)))
    upper = float(np.max(reference_norms + bounds))
    if lower > SUPPORT_THRESHOLD:
        return "STABLE_ACTIVE"
    if upper <= SUPPORT_THRESHOLD:
        return "STABLE_INACTIVE"
    return "UNRESOLVED"


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    return {
        status: statuses.count(status)
        for status in ("STABLE_ACTIVE", "STABLE_INACTIVE", "UNRESOLVED")
    }


def _reference_data() -> dict:
    operator = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    decomposition = operator.center_decomposition()
    bases = [
        np.asarray(basis, dtype=complex)
        for basis in decomposition["sector_bases"]
    ]
    generators = [
        np.asarray(matrix, dtype=complex) for matrix in operator.rho_matrices()
    ]
    labels = [_generator_label(key) for key in operator.rho_moves.keys()]

    nominal_transform, _ = _plane_rotation(bases, theta=0.43)
    nominal_basis = np.hstack([nominal_transform @ basis for basis in bases])
    dimensions = [basis.shape[1] for basis in bases]
    slices = _sector_slices(dimensions)

    generator_coordinates = [
        nominal_basis.conj().T
        @ (nominal_transform @ generator @ nominal_transform.conj().T)
        @ nominal_basis
        for generator in generators
    ]
    return {
        "basis": nominal_basis,
        "dimensions": dimensions,
        "slices": slices,
        "generator_coordinates": generator_coordinates,
        "labels": labels,
    }


def _evaluate_point(reference: dict, epsilon: float, eta: float) -> dict:
    dimension = reference["basis"].shape[0]
    dimensions = reference["dimensions"]
    slices = reference["slices"]
    generators = reference["generator_coordinates"]

    first_coordinate = slices[0].start
    second_coordinate = slices[1].start
    sector_transform = _coordinate_plane_rotation(
        dimension, first_coordinate, second_coordinate, eta
    )
    perturbed_bases = [sector_transform[:, sector_slice] for sector_slice in slices]
    reference_bases = [np.eye(dimension, dtype=complex)[:, sector_slice] for sector_slice in slices]
    deltas = [
        _projector_delta_frobenius(perturbed, baseline)
        for perturbed, baseline in zip(perturbed_bases, reference_bases)
    ]

    rank_one = np.zeros((dimension, dimension), dtype=complex)
    rank_one[first_coordinate, second_coordinate] = 1.0

    actual_differences = np.zeros((len(generators), len(slices), len(slices)))
    global_bounds = np.zeros_like(actual_differences)
    localized_bounds = np.zeros_like(actual_differences)
    reference_norms = np.zeros_like(actual_differences)
    perturbed_norms = np.zeros_like(actual_differences)
    global_generator_statuses: list[str] = []
    localized_generator_statuses: list[str] = []
    global_status_violations = 0
    localized_status_violations = 0
    global_bound_violations = 0
    localized_bound_violations = 0

    for generator_index, generator in enumerate(generators):
        phase = 1.0 if generator_index % 2 == 0 else -1.0
        perturbation = phase * epsilon * rank_one
        perturbed_generator = generator + perturbation
        perturbed_images = [
            perturbed_generator @ basis for basis in perturbed_bases
        ]
        reference_adjoint_images = [
            generator.conj().T @ basis for basis in reference_bases
        ]
        for target, target_slice in enumerate(slices):
            target_basis = perturbed_bases[target]
            for source, source_slice in enumerate(slices):
                source_basis = perturbed_bases[source]
                reference_block = generator[target_slice, source_slice]
                perturbed_block = (
                    target_basis.conj().T @ perturbed_generator @ source_basis
                )
                global_bound = (
                    deltas[target] * (1.0 + epsilon)
                    + epsilon
                    + deltas[source]
                )
                left_local = (
                    _projector_difference_action_norm(
                        target_basis,
                        reference_bases[target],
                        perturbed_images[source],
                    )
                    if deltas[target] > 1e-15
                    else 0.0
                )
                middle_local = float(
                    np.linalg.norm(
                        reference_bases[target].conj().T
                        @ perturbation
                        @ source_basis,
                        "fro",
                    )
                ) if epsilon > 0.0 else 0.0
                right_local = (
                    _projector_difference_action_norm(
                        source_basis,
                        reference_bases[source],
                        reference_adjoint_images[target],
                    )
                    if deltas[source] > 1e-15
                    else 0.0
                )
                localized_bound = left_local + middle_local + right_local
                actual = (
                    _ambient_block_difference(
                        perturbed_block,
                        reference_block,
                        target_basis,
                        reference_bases[target],
                        source_basis,
                        reference_bases[source],
                    )
                    if localized_bound > 1e-15
                    else 0.0
                )
                reference_norm = float(np.linalg.norm(reference_block, "fro"))
                perturbed_norm = float(np.linalg.norm(perturbed_block, "fro"))

                actual_differences[generator_index, target, source] = actual
                global_bounds[generator_index, target, source] = global_bound
                localized_bounds[generator_index, target, source] = localized_bound
                reference_norms[generator_index, target, source] = reference_norm
                perturbed_norms[generator_index, target, source] = perturbed_norm
                if actual > global_bound + BOUND_TOLERANCE:
                    global_bound_violations += 1
                if actual > localized_bound + BOUND_TOLERANCE:
                    localized_bound_violations += 1

                if target != source:
                    global_status = _margin_status(reference_norm, global_bound)
                    localized_status = _margin_status(reference_norm, localized_bound)
                    global_generator_statuses.append(global_status)
                    localized_generator_statuses.append(localized_status)
                    if (
                        global_status == "STABLE_ACTIVE"
                        and perturbed_norm <= SUPPORT_THRESHOLD
                    ):
                        global_status_violations += 1
                    if (
                        global_status == "STABLE_INACTIVE"
                        and perturbed_norm > SUPPORT_THRESHOLD
                    ):
                        global_status_violations += 1
                    if (
                        localized_status == "STABLE_ACTIVE"
                        and perturbed_norm <= SUPPORT_THRESHOLD
                    ):
                        localized_status_violations += 1
                    if (
                        localized_status == "STABLE_INACTIVE"
                        and perturbed_norm > SUPPORT_THRESHOLD
                    ):
                        localized_status_violations += 1

    global_aggregate_statuses: list[str] = []
    localized_aggregate_statuses: list[str] = []
    global_aggregate_status_violations = 0
    localized_aggregate_status_violations = 0
    for left in range(len(slices)):
        for right in range(left + 1, len(slices)):
            coordinate_reference = np.concatenate(
                (reference_norms[:, left, right], reference_norms[:, right, left])
            )
            coordinate_global_bounds = np.concatenate(
                (global_bounds[:, left, right], global_bounds[:, right, left])
            )
            coordinate_localized_bounds = np.concatenate(
                (localized_bounds[:, left, right], localized_bounds[:, right, left])
            )
            coordinate_perturbed = np.concatenate(
                (perturbed_norms[:, left, right], perturbed_norms[:, right, left])
            )
            global_status = _aggregate_margin_status(
                coordinate_reference, coordinate_global_bounds
            )
            localized_status = _aggregate_margin_status(
                coordinate_reference, coordinate_localized_bounds
            )
            global_aggregate_statuses.append(global_status)
            localized_aggregate_statuses.append(localized_status)
            observed_active = float(np.max(coordinate_perturbed)) > SUPPORT_THRESHOLD
            if global_status == "STABLE_ACTIVE" and not observed_active:
                global_aggregate_status_violations += 1
            if global_status == "STABLE_INACTIVE" and observed_active:
                global_aggregate_status_violations += 1
            if localized_status == "STABLE_ACTIVE" and not observed_active:
                localized_aggregate_status_violations += 1
            if localized_status == "STABLE_INACTIVE" and observed_active:
                localized_aggregate_status_violations += 1

    positive_global_bounds = global_bounds[global_bounds > 0.0]
    positive_localized_bounds = localized_bounds[localized_bounds > 0.0]
    global_ratios = np.divide(
        actual_differences,
        global_bounds,
        out=np.zeros_like(actual_differences),
        where=global_bounds > 0.0,
    )
    localized_ratios = np.divide(
        actual_differences,
        localized_bounds,
        out=np.zeros_like(actual_differences),
        where=localized_bounds > 0.0,
    )
    localized_to_global = np.divide(
        localized_bounds,
        global_bounds,
        out=np.zeros_like(localized_bounds),
        where=global_bounds > 0.0,
    )
    localized_to_global_positive = localized_to_global[global_bounds > 0.0]
    return {
        "epsilon_operator_frobenius": epsilon,
        "epsilon_operator_norm": epsilon,
        "eta_sector_rotation_radians": eta,
        "projector_delta_frobenius": deltas,
        "maximum_projector_delta_frobenius": max(deltas),
        "maximum_actual_block_difference": float(np.max(actual_differences)),
        "maximum_declared_bound": float(np.max(global_bounds)),
        "minimum_positive_declared_bound": (
            float(np.min(positive_global_bounds))
            if positive_global_bounds.size
            else 0.0
        ),
        "maximum_actual_to_bound_ratio": float(np.max(global_ratios)),
        "bound_violation_count": global_bound_violations,
        "generator_coordinate_margin_counts": _count_statuses(
            global_generator_statuses
        ),
        "generator_coordinate_status_violation_count": global_status_violations,
        "aggregate_undirected_margin_counts": _count_statuses(
            global_aggregate_statuses
        ),
        "aggregate_status_violation_count": global_aggregate_status_violations,
        "localized_bound": {
            "maximum": float(np.max(localized_bounds)),
            "minimum_positive": (
                float(np.min(positive_localized_bounds))
                if positive_localized_bounds.size
                else 0.0
            ),
            "maximum_actual_to_bound_ratio": float(np.max(localized_ratios)),
            "bound_violation_count": localized_bound_violations,
            "generator_coordinate_margin_counts": _count_statuses(
                localized_generator_statuses
            ),
            "generator_coordinate_status_violation_count": localized_status_violations,
            "aggregate_undirected_margin_counts": _count_statuses(
                localized_aggregate_statuses
            ),
            "aggregate_status_violation_count": localized_aggregate_status_violations,
        },
        "localized_to_global_summary": {
            "positive_global_coordinate_count": int(positive_global_bounds.size),
            "zero_ratio_count": int(
                np.count_nonzero(
                    localized_to_global_positive <= BOUND_TOLERANCE
                )
            ),
            "minimum": (
                float(np.min(localized_to_global_positive))
                if localized_to_global_positive.size
                else 0.0
            ),
            "median": (
                float(np.median(localized_to_global_positive))
                if localized_to_global_positive.size
                else 0.0
            ),
            "mean": (
                float(np.mean(localized_to_global_positive))
                if localized_to_global_positive.size
                else 0.0
            ),
            "maximum": (
                float(np.max(localized_to_global_positive))
                if localized_to_global_positive.size
                else 0.0
            ),
            "zero_tolerance": BOUND_TOLERANCE,
        },
    }


def build_payload() -> dict:
    reference = _reference_data()
    sweep_axes = {
        "OPERATOR_ONLY": [(level, 0.0) for level in SWEEP_LEVELS],
        "SECTORIZATION_ONLY": [(0.0, level) for level in SWEEP_LEVELS],
        "COUPLED": [(level, level) for level in SWEEP_LEVELS],
    }
    records = []
    for axis, points in sweep_axes.items():
        for level_index, (epsilon, eta) in enumerate(points):
            records.append(
                {
                    "sweep_axis": axis,
                    "level_index": level_index,
                    **_evaluate_point(reference, epsilon=epsilon, eta=eta),
                }
            )

    return {
        "schema": SCHEMA,
        "bundle_id": "numerical-representation-diagnostics.rubik-perturbation-sweep.v1",
        "artifact_role": "PAPER25_PERTURBATION_STABILITY_EVIDENCE",
        "claim_status": "BOUNDED_NUMERICAL_OBSERVATION",
        "paper_evidence_status": "REGISTERED_SUPPORT_NOT_THEOREM_PROOF",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "arithmetic": "complex128/float64",
        },
        "carrier": {
            "carrier_id": "canonical_cubie_representation_228d",
            "generator_count": len(reference["labels"]),
            "generator_labels": reference["labels"],
            "sector_dimensions": reference["dimensions"],
            "nominal_transport": "rubik_qh_transport_v1 two-plane rotation at theta=0.43",
        },
        "perturbation_model": {
            "operator": (
                "E_a = sign(a) epsilon |S1:0><S2:0| in nominal transported coordinates"
            ),
            "sectorization": (
                "Q'_i = W_eta Q_i W_eta* with W_eta rotating S1:0 and S2:0"
            ),
            "operator_norms": "||E_a||_2 = ||E_a||_F = epsilon",
            "projector_delta": "Delta_i = Q'_i - Q_i; recorded in Frobenius norm",
        },
        "stability_bound": {
            "global_block_difference": (
                "||Q'_i Y'_a Q'_j - Q_i Y_a Q_j||_F <= "
                "||Delta_i||_F (1 + epsilon_a) + epsilon_a + ||Delta_j||_F"
            ),
            "carrier_localized_block_difference": (
                "||Q'_i Y'_a Q'_j - Q_i Y_a Q_j||_F <= "
                "||Delta_i Y'_a Q'_j||_F + ||Q_i E_a Q'_j||_F + "
                "||Q_i Y_a Delta_j||_F"
            ),
            "premises": [
                "Y_a is unitary, hence ||Y_a||_2 = 1",
                "Q_i and Q'_i are orthogonal projectors",
                "||E_a||_2 = ||E_a||_F = epsilon_a",
            ],
            "localized_data_requirement": (
                "carrier-localized perturbation actions must be available; "
                "the localized bound is not inferred from global norms alone"
            ),
            "comparison_tolerance": BOUND_TOLERANCE,
        },
        "support_margin_policy": {
            "threshold": SUPPORT_THRESHOLD,
            "stable_active": "reference_norm - bound > threshold",
            "stable_inactive": "reference_norm + bound <= threshold",
            "unresolved": "otherwise",
            "inactive_is_exact_zero": False,
            "comparison": (
                "the same policy is evaluated with global and carrier-localized bounds"
            ),
        },
        "sweep_levels": list(SWEEP_LEVELS),
        "records": records,
        "negative_boundaries": [
            "The sweep validates the stated bound on a declared finite perturbation family; it is not a universal optimality theorem.",
            "UNRESOLVED is a margin status, not evidence that a block is zero or nonzero.",
            "Additive E_a operators need not form a group representation or preserve unitarity.",
            "No Paper I/II support edge or exact-zero claim is revised by this bounded sweep.",
        ],
    }
