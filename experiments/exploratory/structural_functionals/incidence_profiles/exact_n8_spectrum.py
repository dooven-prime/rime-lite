#!/usr/bin/env python
"""Exact n=8 spectrum certificate over Z[zeta_3] and Q(sqrt(5),zeta_3).

An element ``a + b*zeta`` is stored as a pair of integer matrices, using
``zeta^2 + zeta + 1 = 0``. No floating-point matrix enters this certificate.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import numpy as np

from incidence_profiles import (
    REPO_ROOT,
    Qsqrt5,
    lagrange_projector_certificate,
    named_family,
    source_artifact,
    write_json,
)
from rime.cubie import CubieMove


DIMENSION = 228
INT64_MAX = int(np.iinfo(np.int64).max)
PAIR_MATMUL_PREOPERATION_BOUNDS: list[int] = []


def pair_zero():
    return np.zeros((DIMENSION, DIMENSION), dtype=np.int64), np.zeros(
        (DIMENSION, DIMENSION), dtype=np.int64
    )


def pair_identity(scale: int = 1):
    return np.eye(DIMENSION, dtype=np.int64) * scale, np.zeros(
        (DIMENSION, DIMENSION), dtype=np.int64
    )


def pair_add(left, right):
    return left[0] + right[0], left[1] + right[1]


def pair_sub(left, right):
    return left[0] - right[0], left[1] - right[1]


def _pair_max_abs(pair) -> tuple[int, int]:
    int64_min = np.iinfo(np.int64).min

    def component_max_abs(component) -> int:
        if np.any(component == int64_min):
            return 2**63
        return int(np.max(np.abs(component), initial=0))

    return (
        component_max_abs(pair[0]),
        component_max_abs(pair[1]),
    )


def pair_matmul_preoperation_bound(left, right) -> int:
    """Conservatively bound each output coefficient before multiplication."""
    if left[0].shape[1] != right[0].shape[0]:
        raise ValueError("incompatible pair-matrix dimensions")
    inner = left[0].shape[1]
    max_a, max_b = _pair_max_abs(left)
    max_c, max_d = _pair_max_abs(right)
    real_bound = inner * (max_a * max_c + max_b * max_d)
    zeta_bound = inner * (
        max_a * max_d + max_b * max_c + max_b * max_d
    )
    return max(real_bound, zeta_bound)


def pair_matmul(left, right):
    # (a+bz)(c+dz) = (ac-bd) + (ad+bc-bd)z, z^2=-1-z.
    bound = pair_matmul_preoperation_bound(left, right)
    PAIR_MATMUL_PREOPERATION_BOUNDS.append(bound)
    if bound > INT64_MAX:
        raise OverflowError(
            f"int64 safety bound exceeded before pair multiplication: {bound}"
        )
    a, b = left
    c, d = right
    ac = a @ c
    bd = b @ d
    return ac - bd, a @ d + b @ c - bd


def exact_rho(key):
    move = CubieMove.prim_moves[key]
    real, zeta = pair_zero()

    for position, destination in enumerate(move.corners_perm):
        destination = int(destination)
        for copy in range(8):
            real[8 * destination + copy, 8 * position + copy] = 1

    ep_offset = 64
    for position, destination in enumerate(move.edges_perm):
        destination = int(destination)
        for copy in range(12):
            real[ep_offset + 12 * destination + copy, ep_offset + 12 * position + copy] = 1

    co_offset = 208
    for position, destination in enumerate(move.corners_perm):
        destination = int(destination)
        exponent = int(move.corners_ori_delta[position]) % 3
        row, column = co_offset + destination, co_offset + position
        if exponent == 0:
            real[row, column] = 1
        elif exponent == 1:
            zeta[row, column] = 1
        else:
            real[row, column] = -1
            zeta[row, column] = -1

    eo_offset = 216
    for position, destination in enumerate(move.edges_perm):
        destination = int(destination)
        real[eo_offset + destination, eo_offset + position] = (
            -1 if int(move.edges_ori_delta[position]) % 2 else 1
        )
    return real, zeta


def pair_adjoint(pair):
    # conjugate(a + b*zeta_3) = (a-b) - b*zeta_3
    return (pair[0] - pair[1]).T, (-pair[1]).T


def polynomial_product(factors):
    result = pair_identity()
    maxima = []
    for factor in factors:
        result = pair_matmul(result, factor)
        maxima.append(max(int(np.max(np.abs(result[0]))), int(np.max(np.abs(result[1])))))
    return result, maxima


def qsqrt5_traces_of_projectors(eigenvalues, power_traces):
    interpolation = lagrange_projector_certificate(eigenvalues)
    traces = []
    for projector in interpolation["projector_polynomials"]:
        value_a = Qsqrt5()
        value_b = Qsqrt5()
        for power, coefficient_json in enumerate(
            projector["polynomial_coefficients_low_to_high"]
        ):
            coefficient = Qsqrt5(
                Fraction(coefficient_json["rational"]),
                Fraction(coefficient_json["sqrt5"]),
            )
            trace_a, trace_b = power_traces[power]
            value_a = value_a + coefficient * trace_a
            value_b = value_b + coefficient * trace_b
        traces.append((value_a, value_b))
    return interpolation, traces


def main():
    PAIR_MATMUL_PREOPERATION_BOUNDS.clear()
    family = named_family("axes02_qt")
    inverse_closed = all((key[0], key[1], -key[2]) in family for key in family)
    exact_generators = [exact_rho(key) for key in family]
    generator_checks = []
    identity = pair_identity()
    for key, matrix in zip(family, exact_generators):
        inverse_key = (key[0], key[1], -key[2])
        inverse = exact_rho(inverse_key)
        residual = pair_sub(pair_matmul(matrix, inverse), identity)
        generator_checks.append(
            {
                "generator": list(key),
                "inverse": list(inverse_key),
                "inverse_identity_verified": not np.any(residual[0]) and not np.any(residual[1]),
            }
        )

    operator_sum = pair_zero()
    for matrix in exact_generators:
        operator_sum = pair_add(operator_sum, matrix)
    operator_sum_self_adjoint = not any(
        np.any(component)
        for component in pair_sub(operator_sum, pair_adjoint(operator_sum))
    )
    identity = pair_identity()
    shifted = lambda integer: pair_sub(operator_sum, pair_identity(integer))
    quadratic = pair_sub(pair_matmul(shifted(5), shifted(5)), pair_identity(5))
    annihilator, intermediate_maxima = polynomial_product(
        [operator_sum, shifted(2), shifted(4), shifted(6), shifted(8), quadratic]
    )
    annihilator_verified = not np.any(annihilator[0]) and not np.any(annihilator[1])

    eigenvalues_s = [
        Qsqrt5(0),
        Qsqrt5(2),
        Qsqrt5(4),
        Qsqrt5(5, 1),
        Qsqrt5(5, -1),
        Qsqrt5(6),
        Qsqrt5(8),
    ]
    powers = [identity]
    for _ in range(1, len(eigenvalues_s)):
        powers.append(pair_matmul(powers[-1], operator_sum))
    power_traces = [
        (Qsqrt5(int(np.trace(real))), Qsqrt5(int(np.trace(zeta))))
        for real, zeta in powers
    ]
    interpolation, projector_traces = qsqrt5_traces_of_projectors(
        eigenvalues_s, power_traces
    )
    multiplicities = []
    traces_verified = True
    for eigenvalue, (trace_a, trace_b) in zip(eigenvalues_s, projector_traces):
        is_integer = trace_a.radical == 0 and trace_b == Qsqrt5() and trace_a.rational.denominator == 1
        traces_verified = traces_verified and is_integer and trace_a.rational > 0
        multiplicities.append(
            {
                "eigenvalue_of_S": eigenvalue.to_json(),
                "eigenvalue_of_A_equals_S_over_8": (eigenvalue / 8).to_json(),
                "trace_zeta_basis": [trace_a.to_json(), trace_b.to_json()],
                "multiplicity": int(trace_a.rational) if is_integer else None,
            }
        )

    certificate = {
        "schema": "rime.exact-spectrum-certificate.v1",
        "claim_status": "Computational Certificate",
        "certificate_kind": "exact_finite_algebraic",
        "family": "axes02_qt",
        "generator_keys": [list(key) for key in family],
        "generator_family_inverse_closed": inverse_closed,
        "operator_sum_self_adjoint_verified": operator_sum_self_adjoint,
        "coefficient_ring": "Z[zeta_3], zeta_3^2 + zeta_3 + 1 = 0",
        "ambient_dimension": DIMENSION,
        "generator_inverse_checks": generator_checks,
        "annihilating_polynomial": "x(x-2)(x-4)(x-6)(x-8)((x-5)^2-5)",
        "annihilator_verified_entrywise": annihilator_verified,
        "intermediate_max_abs_integer_coefficient": intermediate_maxima,
        "int64_preoperation_audit": {
            "operation_count": len(PAIR_MATMUL_PREOPERATION_BOUNDS),
            "maximum_conservative_output_bound": max(
                PAIR_MATMUL_PREOPERATION_BOUNDS, default=0
            ),
            "int64_limit": INT64_MAX,
            "all_operations_safe": all(
                bound <= INT64_MAX for bound in PAIR_MATMUL_PREOPERATION_BOUNDS
            ),
        },
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                source_artifact(Path(__file__).with_name("incidence_profiles.py")),
                source_artifact(REPO_ROOT / "rime" / "base.py"),
                source_artifact(REPO_ROOT / "rime" / "cube.py"),
                source_artifact(REPO_ROOT / "rime" / "cubie.py"),
            ]
        },
        "projector_interpolation_verified": interpolation["verified_interpolation_identity"],
        "projector_traces_verified_positive_integers": traces_verified,
        "multiplicities": multiplicities,
        "multiplicity_sum": sum(item["multiplicity"] or 0 for item in multiplicities),
        "conclusion": (
            "Because S is Hermitian (the family is inverse closed), the square-free "
            "annihilator and positive exact projector traces certify the complete exact "
            "spectrum and multiplicities. The Lagrange polynomials therefore define the "
            "exact spectral projectors over Q(sqrt(5), zeta_3)."
        ),
    }
    assert all(row["inverse_identity_verified"] for row in generator_checks)
    assert inverse_closed
    assert operator_sum_self_adjoint
    assert annihilator_verified
    assert traces_verified
    assert certificate["int64_preoperation_audit"]["all_operations_safe"]
    assert certificate["multiplicity_sum"] == DIMENSION
    write_json(Path("results/exact_certificates/n8_exact_spectrum.json"), certificate)
    print(
        "exact n=8 spectrum certified; multiplicities =",
        [item["multiplicity"] for item in multiplicities],
    )


if __name__ == "__main__":
    main()
