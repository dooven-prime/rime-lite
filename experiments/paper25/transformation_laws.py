"""Finite controls for typed transformation laws of representation diagnostics.

The exact fixture uses only Python integers and ``Fraction`` arithmetic.  The
dense orthogonal fixture is a bounded floating observation and is kept
separate from the exact certificate surface.
"""

from __future__ import annotations

from fractions import Fraction
import math
from typing import Iterable

import numpy as np


SCHEMA = "rime.paper25.transformation-laws.v1"
NUMERICAL_TOLERANCE = 1e-10


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _exact_rank(rows: Iterable[Iterable[int]]) -> int:
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    row_count = len(matrix)
    column_count = len(matrix[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                left - scale * right
                for left, right in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def exact_commutant_dimension(generators: Iterable[np.ndarray]) -> int:
    """Dimension of the simultaneous commutant over Q for integer matrices."""

    family = [np.asarray(generator, dtype=object) for generator in generators]
    if not family:
        raise ValueError("at least one declared generator is required")
    dimension = family[0].shape[0]
    if any(generator.shape != (dimension, dimension) for generator in family):
        raise ValueError("generator carrier mismatch")
    equations: list[list[int]] = []
    for generator in family:
        for row in range(dimension):
            for column in range(dimension):
                equation = [0] * (dimension * dimension)
                for inner in range(dimension):
                    equation[inner * dimension + column] += int(generator[row, inner])
                    equation[row * dimension + inner] -= int(generator[inner, column])
                equations.append(equation)
    return dimension * dimension - _exact_rank(equations)


def _coordinate_projectors(dimension: int) -> list[np.ndarray]:
    projectors = []
    for index in range(dimension):
        projector = np.zeros((dimension, dimension), dtype=np.int64)
        projector[index, index] = 1
        projectors.append(projector)
    return projectors


def _block_profile(
    family: dict[str, np.ndarray], projectors: list[np.ndarray]
) -> list[dict]:
    profile = []
    for label, operator in family.items():
        for target, left in enumerate(projectors):
            for source, right in enumerate(projectors):
                block = left @ operator @ right
                squared_norm = int(np.sum(np.asarray(block, dtype=object) ** 2))
                profile.append(
                    {
                        "generator_label": label,
                        "target_sector": target,
                        "source_sector": source,
                        "frobenius_norm_squared": squared_norm,
                        "exact_support": squared_norm != 0,
                    }
                )
    return profile


def _weighted_numerator(
    family: dict[str, np.ndarray], weights: dict[str, int]
) -> tuple[np.ndarray, int]:
    if set(family) != set(weights):
        raise ValueError("weights must bind every and only declared generator label")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weight mass must be positive")
    numerator = sum(
        (weights[label] * np.asarray(operator, dtype=np.int64) for label, operator in family.items()),
        start=np.zeros_like(next(iter(family.values())), dtype=np.int64),
    )
    return numerator, total


def _normalized_trace_moments(
    family: dict[str, np.ndarray], weights: dict[str, int], max_power: int = 4
) -> list[str]:
    numerator, total = _weighted_numerator(family, weights)
    return [
        _fraction_text(
            Fraction(int(np.trace(np.linalg.matrix_power(numerator, power))), total**power)
        )
        for power in range(1, max_power + 1)
    ]


def _transport(
    family: dict[str, np.ndarray], transform: np.ndarray
) -> dict[str, np.ndarray]:
    adjoint = transform.conj().T
    return {
        label: transform @ operator @ adjoint for label, operator in family.items()
    }


def _dense_orthogonal_transform() -> np.ndarray:
    first = 0.37
    second = -0.61
    transform = np.zeros((4, 4), dtype=float)
    transform[:2, :2] = [
        [math.cos(first), -math.sin(first)],
        [math.sin(first), math.cos(first)],
    ]
    transform[2:, 2:] = [
        [math.cos(second), -math.sin(second)],
        [math.sin(second), math.cos(second)],
    ]
    return transform


def _floating_block_norms(
    family: dict[str, np.ndarray], projectors: list[np.ndarray]
) -> list[float]:
    return [
        float(np.linalg.norm(left @ operator @ right, "fro"))
        for operator in family.values()
        for left in projectors
        for right in projectors
    ]


def _classify_numeric_nonzero(value: float, declared_error_bound: float) -> str:
    if declared_error_bound < 0:
        raise ValueError("error bound must be nonnegative")
    return (
        "BOUNDED_NONZERO_UNDER_DECLARED_BOUND"
        if abs(value) > declared_error_bound
        else "UNRESOLVED"
    )


def build_payload() -> dict:
    cycle = np.array(
        [[0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        dtype=np.int64,
    )
    representation = {"r": cycle, "r_inv": cycle.T}
    projectors = _coordinate_projectors(4)

    exact_transform = np.array(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.int64,
    )
    transported_representation = _transport(representation, exact_transform)
    transported_projectors = [
        exact_transform @ projector @ exact_transform.T for projector in projectors
    ]
    base_profile = _block_profile(representation, projectors)
    transported_profile = _block_profile(
        transported_representation, transported_projectors
    )
    fixed_frame_profile = _block_profile(transported_representation, projectors)

    declared_weights = {"r": 2, "r_inv": 1}
    alternate_weights = {"r": 1, "r_inv": 1}
    average_numerator, _ = _weighted_numerator(representation, declared_weights)
    transported_average_numerator, _ = _weighted_numerator(
        transported_representation, declared_weights
    )

    dense_transform = _dense_orthogonal_transform()
    dense_representation = _transport(representation, dense_transform)
    dense_projectors = [
        dense_transform @ projector @ dense_transform.T for projector in projectors
    ]
    dense_conjugation_residual = max(
        float(
            np.linalg.norm(
                dense_representation[label]
                - dense_transform @ representation[label] @ dense_transform.T,
                "fro",
            )
        )
        for label in representation
    )
    base_norms = _floating_block_norms(representation, projectors)
    dense_norms = _floating_block_norms(dense_representation, dense_projectors)

    exact_commutant = exact_commutant_dimension(representation.values())
    transported_commutant = exact_commutant_dimension(
        transported_representation.values()
    )
    declared_moments = _normalized_trace_moments(representation, declared_weights)
    transported_moments = _normalized_trace_moments(
        transported_representation, declared_weights
    )
    alternate_moments = _normalized_trace_moments(representation, alternate_weights)

    shear = np.array(
        [[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.int64,
    )
    shear_inverse = np.array(
        [[1, -1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.int64,
    )
    similar_representation = {
        label: shear @ operator @ shear_inverse
        for label, operator in representation.items()
    }
    similar_projectors = [
        shear @ projector @ shear_inverse for projector in projectors
    ]
    similar_average_numerator, _ = _weighted_numerator(
        similar_representation, declared_weights
    )
    similar_profile = _block_profile(similar_representation, similar_projectors)

    exact_transport = {
        "fixture": "C4_regular_labelled_generators_with_coordinate_sectorization",
        "arithmetic": "Python integer matrices and Fraction trace moments",
        "generator_completeness_witness": "label r generates the represented C4 action",
        "commutant_dimension": {
            "base": exact_commutant,
            "transported": transported_commutant,
            "invariant": exact_commutant == transported_commutant,
        },
        "fixed_measure_average": {
            "weights": declared_weights,
            "exact_conjugation_residual_max_abs": int(
                np.max(
                    np.abs(
                        transported_average_numerator
                        - exact_transform @ average_numerator @ exact_transform.T
                    )
                )
            ),
            "base_normalized_trace_moments_1_to_4": declared_moments,
            "transported_normalized_trace_moments_1_to_4": transported_moments,
        },
        "changed_measure_control": {
            "alternate_weights": alternate_weights,
            "alternate_normalized_trace_moments_1_to_4": alternate_moments,
            "differs_from_declared_measure": alternate_moments != declared_moments,
        },
        "transported_sectorization": {
            "block_profile_equal": base_profile == transported_profile,
            "exact_support_graph_equal": [
                row for row in base_profile if row["exact_support"]
            ]
            == [row for row in transported_profile if row["exact_support"]],
        },
        "untransported_sectorization_hostile_control": {
            "block_profile_equal": base_profile == fixed_frame_profile,
            "exact_support_graph_equal": [
                row for row in base_profile if row["exact_support"]
            ]
            == [row for row in fixed_frame_profile if row["exact_support"]],
        },
        "nonunitary_similarity_boundary": {
            "transform_kind": "invertible_unimodular_shear",
            "commutant_dimension": exact_commutant_dimension(
                similar_representation.values()
            ),
            "fixed_measure_average_similarity_residual_max_abs": int(
                np.max(
                    np.abs(
                        similar_average_numerator
                        - shear @ average_numerator @ shear_inverse
                    )
                )
            ),
            "transported_idempotents_remain_idempotent": all(
                np.array_equal(projector @ projector, projector)
                for projector in similar_projectors
            ),
            "transported_idempotents_remain_self_adjoint": all(
                np.array_equal(projector.T, projector)
                for projector in similar_projectors
            ),
            "frobenius_block_profile_equal": base_profile == similar_profile,
            "boundary": (
                "general similarity preserves the algebraic transport law but "
                "does not preserve orthogonal sectorization or Frobenius block norms"
            ),
        },
    }

    numerical_transport = {
        "fixture": "dense_continuous_orthogonal_change_of_basis",
        "arithmetic": "float64 bounded observation",
        "declared_tolerance": NUMERICAL_TOLERANCE,
        "orthogonality_residual_frobenius": float(
            np.linalg.norm(dense_transform.T @ dense_transform - np.eye(4), "fro")
        ),
        "generator_conjugation_residual_frobenius_max": dense_conjugation_residual,
        "transported_block_norm_difference_max": max(
            abs(left - right) for left, right in zip(base_norms, dense_norms)
        ),
        "near_zero_policy_control": {
            "declared_error_bound": 1e-9,
            "error_bound_status": "INPUT_REQUIRING_OWN_CERTIFICATION",
            "small_value": 5e-10,
            "small_value_status": _classify_numeric_nonzero(5e-10, 1e-9),
            "resolved_value": 2e-8,
            "resolved_value_status": _classify_numeric_nonzero(2e-8, 1e-9),
            "exact_zero_status_reserved_for_exact_arithmetic": True,
        },
    }

    return {
        "schema": SCHEMA,
        "bundle_id": "numerical-representation-diagnostics.transformation-laws.v1",
        "artifact_role": "PAPER25_TRANSFORMATION_LAW_EVIDENCE",
        "claim_status": "EXACT_FINITE_CERTIFICATE_AND_BOUNDED_NUMERICAL_OBSERVATION",
        "paper_evidence_status": "REGISTERED_SUPPORT_NOT_THEOREM_PROOF",
        "diagnostic_registry": [
            {
                "diagnostic": "commutant_dimension",
                "ownership": "REPRESENTATION_INTRINSIC",
                "required_bindings": [
                    "representation_carrier",
                    "represented_action_or_generator_completeness_witness",
                ],
                "law": "invariant under representation equivalence",
            },
            {
                "diagnostic": "weighted_generator_average_similarity_class",
                "ownership": "GENERATOR_MEASURE_RELATIVE",
                "required_bindings": [
                    "labelled_generator_family",
                    "label_alignment",
                    "weight_measure",
                ],
                "law": "equivariant under simultaneous labelled transport with fixed measure",
            },
            {
                "diagnostic": "generator_resolved_block_norms",
                "ownership": "SECTORIZATION_RELATIVE",
                "required_bindings": [
                    "labelled_generator_family",
                    "labelled_projectors",
                    "unitary_transport",
                    "norm",
                ],
                "law": "invariant only under simultaneous unitary transport of operators and projectors",
            },
            {
                "diagnostic": "support_or_activity_graph",
                "ownership": "SECTORIZATION_AND_ZERO_POLICY_RELATIVE",
                "required_bindings": [
                    "labelled_generator_family",
                    "labelled_projectors",
                    "zero_or_error_policy",
                ],
                "law": "transported only with the sectorization and declared exact-zero or threshold policy",
            },
        ],
        "exact_finite_certificate": exact_transport,
        "bounded_numerical_observation": numerical_transport,
        "negative_boundaries": [
            "No concatenated diagnostic vector is declared a representation invariant.",
            "No reconstruction, tomography, identifiability, or representation-equivalence completeness claim is made.",
            "A spectral layer is not treated as a subrepresentation without a full-action invariance witness.",
            "Numerical near-zero blocks remain unresolved unless a separately justified error bound proves nonzero or exact arithmetic proves zero.",
            "Finite discretization diagnostics do not establish convergence to or reconstruction of an underlying continuous object.",
        ],
    }
