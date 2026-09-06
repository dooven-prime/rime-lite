"""Rubik QH-sector transport controls for numerical diagnostics.

This module consumes the existing canonical 18-generator representation and
the registered nine QH sector bases. It does not rebuild or reinterpret the
Paper I/II objects.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform

import numpy as np
import scipy

from rime.cubie import CubieMove
from rime.cubieoperator import CubieSpectralOperator


SCHEMA = "rime.paper25.rubik-transport.v1"
PROFILE_DIGEST_DECIMALS = 12
SUPPORT_THRESHOLDS = (1e-10, 1e-6, 5e-2)
EXPECTED_SECTOR_DIMENSIONS = [20, 2, 39, 26, 1, 39, 66, 8, 27]


def _generator_label(key: tuple[int, int, int]) -> str:
    axis, side, direction = key
    return f"axis{axis}:side{side:+d}:turn{direction:+d}"


def _profile_digest(profile: np.ndarray) -> str:
    rounded = np.round(profile, PROFILE_DIGEST_DECIMALS)
    rounded[np.abs(rounded) < 0.5 * 10 ** (-PROFILE_DIGEST_DECIMALS)] = 0.0
    encoded = json.dumps(
        rounded.tolist(),
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _generator_block_profiles(
    operators: list[np.ndarray], bases: list[np.ndarray]
) -> np.ndarray:
    profile = np.zeros((len(operators), len(bases), len(bases)), dtype=float)
    for generator_index, operator in enumerate(operators):
        images = [operator @ basis for basis in bases]
        for target, left in enumerate(bases):
            left_adjoint = left.conj().T
            for source, image in enumerate(images):
                profile[generator_index, target, source] = np.linalg.norm(
                    left_adjoint @ image, "fro"
                )
    return profile


def _transported_block_profiles(
    operators: list[np.ndarray], bases: list[np.ndarray], transform: np.ndarray
) -> np.ndarray:
    """Evaluate blocks of U Y U* in the transported bases U B_i."""

    transported_bases = [transform @ basis for basis in bases]
    profile = np.zeros((len(operators), len(bases), len(bases)), dtype=float)
    for generator_index, operator in enumerate(operators):
        transported_images = [transform @ (operator @ basis) for basis in bases]
        for target, left in enumerate(transported_bases):
            left_adjoint = left.conj().T
            for source, image in enumerate(transported_images):
                profile[generator_index, target, source] = np.linalg.norm(
                    left_adjoint @ image, "fro"
                )
    return profile


def _aggregate(profile: np.ndarray) -> np.ndarray:
    return np.max(profile, axis=0)


def _undirected_edges(matrix: np.ndarray, threshold: float) -> list[list[int]]:
    return [
        [left + 1, right + 1]
        for left in range(matrix.shape[0])
        for right in range(left + 1, matrix.shape[1])
        if max(matrix[left, right], matrix[right, left]) > threshold
    ]


def _edge_census(
    baseline: np.ndarray, transported: np.ndarray, fixed_frame: np.ndarray
) -> list[dict]:
    rows = []
    for threshold in SUPPORT_THRESHOLDS:
        base_edges = _undirected_edges(baseline, threshold)
        transported_edges = _undirected_edges(transported, threshold)
        fixed_edges = _undirected_edges(fixed_frame, threshold)
        base_set = {tuple(edge) for edge in base_edges}
        fixed_set = {tuple(edge) for edge in fixed_edges}
        rows.append(
            {
                "threshold": threshold,
                "status_semantics": "ACTIVE_OR_INACTIVE_UNDER_DECLARED_THRESHOLD",
                "baseline_edges": base_edges,
                "transported_edges": transported_edges,
                "fixed_frame_edges": fixed_edges,
                "transported_equal_to_baseline": transported_edges == base_edges,
                "fixed_frame_equal_to_baseline": fixed_edges == base_edges,
                "fixed_frame_added_edges": [
                    list(edge) for edge in sorted(fixed_set - base_set)
                ],
                "fixed_frame_removed_edges": [
                    list(edge) for edge in sorted(base_set - fixed_set)
                ],
            }
        )
    return rows


def _cross_sector_norms(operator: np.ndarray, bases: list[np.ndarray]) -> dict:
    values = [
        float(np.linalg.norm(left.conj().T @ operator @ right, "fro"))
        for target, left in enumerate(bases)
        for source, right in enumerate(bases)
        if target != source
    ]
    return {
        "maximum": max(values),
        "joint_frobenius": float(math.sqrt(sum(value * value for value in values))),
    }


def _plane_rotation(
    bases: list[np.ndarray], theta: float
) -> tuple[np.ndarray, dict]:
    first = bases[0][:, 0]
    second = bases[1][:, 0]
    cosine = math.cos(theta)
    sine = math.sin(theta)
    dimension = first.shape[0]
    transform = np.eye(dimension, dtype=complex)
    transform += (cosine - 1.0) * (
        np.outer(first, first.conj()) + np.outer(second, second.conj())
    )
    transform += sine * (
        np.outer(second, first.conj()) - np.outer(first, second.conj())
    )
    return transform, {
        "kind": "two_plane_unitary_rotation",
        "theta_radians": theta,
        "source_vectors": ["S1:basis-vector-0", "S2:basis-vector-0"],
    }


def _profile_rows(
    labels: list[str],
    baseline: np.ndarray,
    transported: np.ndarray,
    fixed_frame: np.ndarray,
) -> list[dict]:
    rows = []
    for index, label in enumerate(labels):
        rows.append(
            {
                "generator_label": label,
                "baseline_block_norms": baseline[index].tolist(),
                "transported_block_norms": transported[index].tolist(),
                "fixed_frame_block_norms": fixed_frame[index].tolist(),
                "transported_max_abs_difference": float(
                    np.max(np.abs(transported[index] - baseline[index]))
                ),
                "fixed_frame_max_abs_difference": float(
                    np.max(np.abs(fixed_frame[index] - baseline[index]))
                ),
            }
        )
    return rows


def build_payload() -> dict:
    operator = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    decomposition = operator.center_decomposition()
    bases = [
        np.asarray(basis, dtype=complex)
        for basis in decomposition["sector_bases"]
    ]
    generators = [
        np.asarray(matrix, dtype=complex) for matrix in operator.rho_matrices()
    ]
    generator_keys = list(operator.rho_moves.keys())
    labels = [_generator_label(key) for key in generator_keys]

    transform, transform_declaration = _plane_rotation(bases, theta=0.43)
    transported_bases = [transform @ basis for basis in bases]
    fixed_frame_equivalent_bases = [transform.conj().T @ basis for basis in bases]
    # B_i^* (U Y U*) B_j = (U* B_i)^* Y (U* B_j).

    baseline_profile = _generator_block_profiles(generators, bases)
    transported_profile = _transported_block_profiles(generators, bases, transform)
    fixed_frame_profile = _generator_block_profiles(
        generators, fixed_frame_equivalent_bases
    )

    baseline_aggregate = _aggregate(baseline_profile)
    transported_aggregate = _aggregate(transported_profile)
    fixed_frame_aggregate = _aggregate(fixed_frame_profile)

    qh_basis = np.hstack(bases)
    transported_qh_basis = np.hstack(transported_bases)
    identity = np.eye(qh_basis.shape[0])
    transported_average = transform @ operator.A @ transform.conj().T

    baseline_average_cross = _cross_sector_norms(operator.A, bases)
    transported_average_cross = _cross_sector_norms(
        transported_average, transported_bases
    )
    fixed_frame_average_cross = _cross_sector_norms(transported_average, bases)

    per_generator = _profile_rows(
        labels, baseline_profile, transported_profile, fixed_frame_profile
    )
    edge_census = _edge_census(
        baseline_aggregate, transported_aggregate, fixed_frame_aggregate
    )

    return {
        "schema": SCHEMA,
        "bundle_id": "numerical-representation-diagnostics.rubik-qh-transport.v1",
        "artifact_role": "PAPER25_RUBIK_TRANSPORT_EVIDENCE",
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
            "dimension": qh_basis.shape[0],
            "generator_count": len(generators),
            "generator_labels": labels,
            "generator_keys": [list(key) for key in generator_keys],
            "sectorization_id": "registered_QH_joint_sectors",
            "sector_count": len(bases),
            "sector_dimensions": [basis.shape[1] for basis in bases],
        },
        "transform": {
            **transform_declaration,
            "unitarity_residual_frobenius": float(
                np.linalg.norm(transform.conj().T @ transform - identity, "fro")
            ),
            "baseline_basis_unitarity_residual_frobenius": float(
                np.linalg.norm(qh_basis.conj().T @ qh_basis - identity, "fro")
            ),
            "transported_basis_unitarity_residual_frobenius": float(
                np.linalg.norm(
                    transported_qh_basis.conj().T @ transported_qh_basis - identity,
                    "fro",
                )
            ),
        },
        "generator_resolved_profiles": {
            "norm": "Frobenius",
            "profile_shape": list(baseline_profile.shape),
            "digest_rounding_decimals": PROFILE_DIGEST_DECIMALS,
            "baseline_digest": _profile_digest(baseline_profile),
            "transported_digest": _profile_digest(transported_profile),
            "fixed_frame_digest": _profile_digest(fixed_frame_profile),
            "transported_max_abs_difference": float(
                np.max(np.abs(transported_profile - baseline_profile))
            ),
            "fixed_frame_max_abs_difference": float(
                np.max(np.abs(fixed_frame_profile - baseline_profile))
            ),
            "per_generator": per_generator,
        },
        "aggregate_support_profiles": {
            "aggregation": "maximum over the 18 declared labelled generators",
            "baseline": baseline_aggregate.tolist(),
            "transported": transported_aggregate.tolist(),
            "fixed_frame": fixed_frame_aggregate.tolist(),
            "transported_max_abs_difference": float(
                np.max(np.abs(transported_aggregate - baseline_aggregate))
            ),
            "fixed_frame_max_abs_difference": float(
                np.max(np.abs(fixed_frame_aggregate - baseline_aggregate))
            ),
            "baseline_asymmetry_max_abs": float(
                np.max(np.abs(baseline_aggregate - baseline_aggregate.T))
            ),
            "threshold_census": edge_census,
        },
        "uniform_generator_average": {
            "measure": "uniform_on_declared_18_labels",
            "baseline_cross_sector_norms": baseline_average_cross,
            "transported_frame_cross_sector_norms": transported_average_cross,
            "fixed_frame_cross_sector_norms": fixed_frame_average_cross,
        },
        "interpretation": {
            "transported_frame": (
                "representation operators and labelled QH projectors are transported together"
            ),
            "fixed_frame": (
                "representation operators are transported while the original QH projectors remain fixed"
            ),
            "strongest_observation": (
                "the full transported generator-resolved profile agrees within float64 residual, "
                "while the fixed-frame profile and thresholded block-activity graph change"
            ),
        },
        "negative_boundaries": [
            "QH projectors are numerical registrations, so inactive threshold coordinates are not exact zero certificates.",
            "The fixed-frame difference is not a failure of representation equivalence; it records a changed marked sectorization relation.",
            "The profile is not a complete representation fingerprint or tomography theorem.",
            "No historical Paper I or Paper II artifact is modified or promoted by this bounded observation.",
        ],
    }
