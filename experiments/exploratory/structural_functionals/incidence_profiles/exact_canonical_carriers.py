#!/usr/bin/env python
"""Exact canonical-sector carrier masks and fixed-frame AB=0 certificates.

The canonical sectors are joint eigenspaces of the exact QT and HT sums. Their
projectors are constructed as Lagrange polynomials over Z[zeta_3], up to a
known nonzero integer denominator. Exact carrier masks then certify all four
canonical zero triples by the carrier-forced incidence theorem.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from exact_n8_spectrum import (
    DIMENSION,
    exact_rho,
    pair_zero,
    pair_identity as raw_pair_identity,
    pair_matmul as raw_pair_matmul,
)
from incidence_profiles import BLOCK_RANGES, REPO_ROOT, named_family, source_artifact, write_json


QT_EIGENVALUES = (0, 4, 6, 8, 10, 12)
HT_EIGENVALUES = (2, 4, 6)
SECTOR_LABELS = (
    (12, 6),
    (10, 6),
    (10, 4),
    (6, 6),
    (4, 6),
    (6, 4),
    (8, 2),
    (0, 6),
    (4, 2),
)
EXPECTED_CARRIERS = (
    ("cp", "ep"),
    ("eo",),
    ("ep", "eo"),
    ("ep", "co"),
    ("eo",),
    ("ep", "eo"),
    ("cp", "ep", "co", "eo"),
    ("cp",),
    ("cp", "co"),
)
CANONICAL_ZERO_TRIPLES = ((2, 6, 8), (5, 6, 8), (8, 6, 2), (8, 6, 5))
INT64_MAX = int(np.iinfo(np.int64).max)


def pair_is_zero(pair) -> bool:
    return not np.any(pair[0]) and not np.any(pair[1])


def pair_max_abs(pair) -> tuple[int, int]:
    int64_min = np.iinfo(np.int64).min

    def component_max_abs(component) -> int:
        if np.any(component == int64_min):
            return 2**63
        return int(np.max(np.abs(component), initial=0))

    return (
        component_max_abs(pair[0]),
        component_max_abs(pair[1]),
    )


def record_preoperation_bound(
    audit: list[dict],
    operation: str,
    operation_kind: str,
    bound: int,
) -> None:
    record = {
        "operation": operation,
        "operation_kind": operation_kind,
        "conservative_max_abs_output_bound": int(bound),
        "int64_safe": int(bound) <= INT64_MAX,
    }
    audit.append(record)
    if not record["int64_safe"]:
        raise OverflowError(
            f"int64 safety bound exceeded before {operation}: {bound}"
        )


def audited_pair_identity(scale: int, audit: list[dict], operation: str):
    record_preoperation_bound(audit, operation, "identity", abs(int(scale)))
    return raw_pair_identity(scale)


def audited_pair_add(left, right, audit: list[dict], operation: str):
    left_real, left_zeta = pair_max_abs(left)
    right_real, right_zeta = pair_max_abs(right)
    bound = max(left_real + right_real, left_zeta + right_zeta)
    record_preoperation_bound(audit, operation, "add", bound)
    return left[0] + right[0], left[1] + right[1]


def audited_pair_sub(left, right, audit: list[dict], operation: str):
    left_real, left_zeta = pair_max_abs(left)
    right_real, right_zeta = pair_max_abs(right)
    bound = max(left_real + right_real, left_zeta + right_zeta)
    record_preoperation_bound(audit, operation, "subtract", bound)
    return left[0] - right[0], left[1] - right[1]


def audited_pair_scale(pair, scalar: int, audit: list[dict], operation: str):
    max_real, max_zeta = pair_max_abs(pair)
    bound = max(max_real, max_zeta) * abs(int(scalar))
    record_preoperation_bound(audit, operation, "scale", bound)
    return pair[0] * scalar, pair[1] * scalar


def audited_pair_adjoint(pair, audit: list[dict], operation: str):
    max_real, max_zeta = pair_max_abs(pair)
    bound = max(max_real + max_zeta, max_zeta)
    record_preoperation_bound(audit, operation, "adjoint", bound)
    # conjugate(a + b*zeta_3) = (a-b) - b*zeta_3
    return (pair[0] - pair[1]).T, (-pair[1]).T


def audited_pair_trace(pair, audit: list[dict], operation: str) -> tuple[int, int]:
    max_real, max_zeta = pair_max_abs(pair)
    diagonal_count = min(pair[0].shape)
    bound = diagonal_count * max(max_real, max_zeta)
    record_preoperation_bound(audit, operation, "trace", bound)
    # Python integers make the scalar accumulation independently overflow-free.
    trace_real = sum(int(value) for value in np.diag(pair[0]))
    trace_zeta = sum(int(value) for value in np.diag(pair[1]))
    return trace_real, trace_zeta


def conservative_pair_matmul_bound(left, right) -> int:
    """Bound every output coefficient before an int64 pair multiplication."""
    if left[0].shape[1] != right[0].shape[0]:
        raise ValueError("incompatible pair-matrix dimensions")
    inner = left[0].shape[1]
    max_a, max_b = pair_max_abs(left)
    max_c, max_d = pair_max_abs(right)
    real_bound = inner * (max_a * max_c + max_b * max_d)
    zeta_bound = inner * (
        max_a * max_d + max_b * max_c + max_b * max_d
    )
    return max(real_bound, zeta_bound)


def audited_pair_matmul(left, right, audit: list[dict], operation: str):
    bound = conservative_pair_matmul_bound(left, right)
    record_preoperation_bound(audit, operation, "matmul", bound)
    return raw_pair_matmul(left, right)


def pair_preserves_block_decomposition(pair, block_ranges=BLOCK_RANGES) -> bool:
    blocks = tuple(block_ranges.values())
    for left_index, (left_start, left_stop) in enumerate(blocks):
        for right_index, (right_start, right_stop) in enumerate(blocks):
            if left_index == right_index:
                continue
            if np.any(pair[0][left_start:left_stop, right_start:right_stop]):
                return False
            if np.any(pair[1][left_start:left_stop, right_start:right_stop]):
                return False
    return True


def polynomial_numerator(operator, target: int, spectrum, audit=None, label="polynomial"):
    audit = [] if audit is None else audit
    result = audited_pair_identity(1, audit, f"{label}:identity")
    denominator = 1
    maxima = []
    for other in spectrum:
        if other == target:
            continue
        shifted = audited_pair_sub(
            operator,
            audited_pair_identity(other, audit, f"{label}:identity-{other}"),
            audit,
            f"{label}:shift-{other}",
        )
        result = audited_pair_matmul(
            result,
            shifted,
            audit,
            f"{label}:factor-{other}",
        )
        denominator *= target - other
        maxima.append(max(pair_max_abs(result)))
    return result, denominator, maxima


def carrier_mask(pair):
    mask = []
    for carrier, (start, stop) in BLOCK_RANGES.items():
        real = pair[0][start:stop, start:stop]
        zeta = pair[1][start:stop, start:stop]
        if np.any(real) or np.any(zeta):
            mask.append(carrier)
    return tuple(mask)


def main():
    arithmetic_audit = []
    qt_sum = pair_zero()
    ht_sum = pair_zero()
    generator_carrier_checks = []
    for key in named_family("full"):
        matrix = exact_rho(key)
        adjoint = audited_pair_adjoint(
            matrix, arithmetic_audit, f"generator-{key}:adjoint"
        )
        skew_numerator = audited_pair_sub(
            matrix, adjoint, arithmetic_audit, f"generator-{key}:skew-numerator"
        )
        generator_carrier_checks.append(
            {
                "generator": list(key),
                "represented_operator_preserves_registered_carriers": (
                    pair_preserves_block_decomposition(matrix)
                ),
                "adjoint_preserves_registered_carriers": (
                    pair_preserves_block_decomposition(adjoint)
                ),
                "anti_hermitian_numerator_preserves_registered_carriers": (
                    pair_preserves_block_decomposition(skew_numerator)
                ),
            }
        )
        if key[2] == 2:
            ht_sum = audited_pair_add(
                ht_sum, matrix, arithmetic_audit, f"ht-sum:add-{key}"
            )
        else:
            qt_sum = audited_pair_add(
                qt_sum, matrix, arithmetic_audit, f"qt-sum:add-{key}"
            )

    commutator = audited_pair_sub(
        audited_pair_matmul(
            qt_sum, ht_sum, arithmetic_audit, "qt-ht-commutator:left"
        ),
        audited_pair_matmul(
            ht_sum, qt_sum, arithmetic_audit, "qt-ht-commutator:right"
        ),
        arithmetic_audit,
        "qt-ht-commutator:subtract",
    )
    qt_sum_self_adjoint = pair_is_zero(
        audited_pair_sub(
            qt_sum,
            audited_pair_adjoint(qt_sum, arithmetic_audit, "qt-sum:adjoint"),
            arithmetic_audit,
            "qt-sum:self-adjoint-residual",
        )
    )
    ht_sum_self_adjoint = pair_is_zero(
        audited_pair_sub(
            ht_sum,
            audited_pair_adjoint(ht_sum, arithmetic_audit, "ht-sum:adjoint"),
            arithmetic_audit,
            "ht-sum:self-adjoint-residual",
        )
    )
    qt_projectors = {
        eigenvalue: polynomial_numerator(
            qt_sum,
            eigenvalue,
            QT_EIGENVALUES,
            arithmetic_audit,
            f"qt-projector-{eigenvalue}",
        )
        for eigenvalue in QT_EIGENVALUES
    }
    ht_projectors = {
        eigenvalue: polynomial_numerator(
            ht_sum,
            eigenvalue,
            HT_EIGENVALUES,
            arithmetic_audit,
            f"ht-projector-{eigenvalue}",
        )
        for eigenvalue in HT_EIGENVALUES
    }

    sectors = []
    exact_projectors = []
    exact_masks = []
    max_coefficient = 0
    for index, ((qt_value, ht_value), expected) in enumerate(
        zip(SECTOR_LABELS, EXPECTED_CARRIERS)
    ):
        qt_numerator, qt_denominator, qt_maxima = qt_projectors[qt_value]
        ht_numerator, ht_denominator, ht_maxima = ht_projectors[ht_value]
        numerator = audited_pair_matmul(
            qt_numerator,
            ht_numerator,
            arithmetic_audit,
            f"joint-projector-{index}",
        )
        denominator = qt_denominator * ht_denominator
        exact_projectors.append((numerator, denominator))
        mask = carrier_mask(numerator)
        exact_masks.append(mask)
        idempotence = audited_pair_sub(
            audited_pair_matmul(
                numerator,
                numerator,
                arithmetic_audit,
                f"joint-projector-{index}:idempotence",
            ),
            audited_pair_scale(
                numerator,
                denominator,
                arithmetic_audit,
                f"joint-projector-{index}:denominator-scale",
            ),
            arithmetic_audit,
            f"joint-projector-{index}:idempotence-residual",
        )
        self_adjoint = audited_pair_sub(
            numerator,
            audited_pair_adjoint(
                numerator,
                arithmetic_audit,
                f"joint-projector-{index}:adjoint",
            ),
            arithmetic_audit,
            f"joint-projector-{index}:self-adjoint-residual",
        )
        qt_eigen_residual = audited_pair_sub(
            audited_pair_matmul(
                qt_sum,
                numerator,
                arithmetic_audit,
                f"joint-projector-{index}:qt-eigenvalue",
            ),
            audited_pair_scale(
                numerator,
                qt_value,
                arithmetic_audit,
                f"joint-projector-{index}:qt-scale",
            ),
            arithmetic_audit,
            f"joint-projector-{index}:qt-eigen-residual",
        )
        ht_eigen_residual = audited_pair_sub(
            audited_pair_matmul(
                ht_sum,
                numerator,
                arithmetic_audit,
                f"joint-projector-{index}:ht-eigenvalue",
            ),
            audited_pair_scale(
                numerator,
                ht_value,
                arithmetic_audit,
                f"joint-projector-{index}:ht-scale",
            ),
            arithmetic_audit,
            f"joint-projector-{index}:ht-eigen-residual",
        )
        trace_real, trace_zeta = audited_pair_trace(
            numerator, arithmetic_audit, f"joint-projector-{index}:trace"
        )
        dimension = trace_real // denominator if trace_zeta == 0 and trace_real % denominator == 0 else None
        max_coefficient = max(
            max_coefficient,
            *(qt_maxima or [0]),
            *(ht_maxima or [0]),
            *pair_max_abs(numerator),
        )
        sectors.append(
            {
                "sector": index,
                "qt_sum_eigenvalue": qt_value,
                "ht_sum_eigenvalue": ht_value,
                "projector_denominator": denominator,
                "projector_idempotence_verified": pair_is_zero(idempotence),
                "projector_self_adjoint_verified": pair_is_zero(self_adjoint),
                "qt_joint_eigenvalue_verified": pair_is_zero(qt_eigen_residual),
                "ht_joint_eigenvalue_verified": pair_is_zero(ht_eigen_residual),
                "projector_preserves_registered_carriers": pair_preserves_block_decomposition(numerator),
                "exact_dimension": dimension,
                "exact_carrier_mask": list(mask),
                "expected_carrier_mask": list(expected),
                "carrier_mask_verified": mask == expected,
            }
        )

    pairwise_orthogonality_verified = True
    pairwise_orthogonality_checks = 0
    for left_index, (left, _) in enumerate(exact_projectors):
        for right_index, (right, _) in enumerate(exact_projectors):
            if left_index == right_index:
                continue
            product = audited_pair_matmul(
                left,
                right,
                arithmetic_audit,
                f"orthogonality-{left_index}-{right_index}",
            )
            pairwise_orthogonality_checks += 1
            pairwise_orthogonality_verified &= pair_is_zero(product)

    common_denominator = math.lcm(
        *(abs(denominator) for _, denominator in exact_projectors)
    )
    projector_sum = pair_zero()
    for index, (numerator, denominator) in enumerate(exact_projectors):
        scaled = audited_pair_scale(
            numerator,
            common_denominator // denominator,
            arithmetic_audit,
            f"completeness-{index}:scale",
        )
        projector_sum = audited_pair_add(
            projector_sum,
            scaled,
            arithmetic_audit,
            f"completeness-{index}:add",
        )
    completeness_residual = audited_pair_sub(
        projector_sum,
        audited_pair_identity(
            common_denominator, arithmetic_audit, "completeness:identity"
        ),
        arithmetic_audit,
        "completeness:residual",
    )
    exact_dimension_sum = sum(row["exact_dimension"] or 0 for row in sectors)

    triple_certificates = []
    for target, intermediate, source in CANONICAL_ZERO_TRIPLES:
        overlap = sorted(set(exact_masks[target]) & set(exact_masks[source]))
        triple_certificates.append(
            {
                "triple": [target, intermediate, source],
                "target_carriers": list(exact_masks[target]),
                "source_carriers": list(exact_masks[source]),
                "carrier_intersection": overlap,
                "all_generator_pairs_have_exact_zero_product": not overlap,
            }
        )

    fixed_profiles = Path("results/axis_balanced_fixed")
    orbit_certificates = []
    for path in sorted(fixed_profiles.glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        observed_triples = {
            tuple(row["triple"]) for row in profile["zero_profile"]["triple_counts"]
        }
        zero_count = profile["counts"]["unprotected_zero"]
        mechanisms = profile["counts"]["zero_mechanism_counts"]
        covered = observed_triples <= set(CANONICAL_ZERO_TRIPLES)
        orbit_certificates.append(
            {
                "orbit_id": profile["family"].get("orbit_id"),
                "operator_count": profile["family"]["operator_count"],
                "observed_zero_count": zero_count,
                "observed_zero_triples": [list(item) for item in sorted(observed_triples)],
                "only_carrier_forced_mechanism": mechanisms.get("physical_carrier_forced", 0) == zero_count,
                "all_observed_zero_routes_exactly_certified": covered
                and mechanisms.get("physical_carrier_forced", 0) == zero_count,
            }
        )

    certificate = {
        "schema": "rime.exact-canonical-carrier-certificate.v2",
        "claim_status": "Computational Certificate",
        "certificate_kind": "exact_finite_algebraic",
        "coefficient_ring": "Z[zeta_3], zeta_3^2 + zeta_3 + 1 = 0",
        "arithmetic_backend": (
            "numpy.int64 coefficient arrays guarded by conservative "
            "preoperation bounds for every arithmetic operation; trace "
            "accumulation uses Python integers"
        ),
        "qt_ht_commutator_verified_entrywise": pair_is_zero(commutator),
        "qt_sum_self_adjoint_verified": qt_sum_self_adjoint,
        "ht_sum_self_adjoint_verified": ht_sum_self_adjoint,
        "operative_generator_carrier_checks": generator_carrier_checks,
        "all_operative_generators_preserve_registered_carriers": all(
            row["represented_operator_preserves_registered_carriers"]
            and row["adjoint_preserves_registered_carriers"]
            and row["anti_hermitian_numerator_preserves_registered_carriers"]
            for row in generator_carrier_checks
        ),
        "operative_family": "anti-Hermitian numerators rho(g)-rho(g)^*; division by 2 omitted",
        "projector_construction": (
            "P_(q,h) = product_{q'!=q}(S_QT-q'I)/(q-q') "
            "product_{h'!=h}(S_HT-h'I)/(h-h')"
        ),
        "maximum_intermediate_integer_coefficient": max_coefficient,
        "int64_preoperation_audit": {
            "coverage": [
                "identity",
                "add",
                "subtract",
                "scale",
                "adjoint",
                "matmul",
                "trace",
            ],
            "operation_count": len(arithmetic_audit),
            "operation_kind_counts": dict(
                sorted(Counter(row["operation_kind"] for row in arithmetic_audit).items())
            ),
            "maximum_conservative_output_bound": max(
                row["conservative_max_abs_output_bound"] for row in arithmetic_audit
            ),
            "int64_limit": INT64_MAX,
            "all_operations_safe": all(
                row["int64_safe"] for row in arithmetic_audit
            ),
            "operations": arithmetic_audit,
        },
        "int64_pair_matmul_safety_verified": all(
            row["int64_safe"]
            for row in arithmetic_audit
            if row["operation_kind"] == "matmul"
        ),
        "int64_all_arithmetic_safety_verified": all(
            row["int64_safe"] for row in arithmetic_audit
        ),
        "projector_family": {
            "candidate_count": len(exact_projectors),
            "pairwise_orthogonality_check_count": pairwise_orthogonality_checks,
            "pairwise_orthogonality_verified": pairwise_orthogonality_verified,
            "common_denominator": common_denominator,
            "completeness_verified": pair_is_zero(completeness_residual),
            "exact_dimension_sum": exact_dimension_sum,
            "ambient_dimension": DIMENSION,
            "dimension_sum_verified": exact_dimension_sum == DIMENSION,
        },
        "provenance": {
            "source_artifacts": [
                source_artifact(Path(__file__)),
                source_artifact(Path(__file__).with_name("exact_n8_spectrum.py")),
                source_artifact(Path(__file__).with_name("incidence_profiles.py")),
                source_artifact(REPO_ROOT / "rime" / "base.py"),
                source_artifact(REPO_ROOT / "rime" / "cube.py"),
                source_artifact(REPO_ROOT / "rime" / "cubie.py"),
                source_artifact(REPO_ROOT / "rime" / "cubieoperator.py"),
                source_artifact(REPO_ROOT / "rime" / "helpers.py"),
                source_artifact(REPO_ROOT / "rime" / "spectral_utils.py"),
                *(source_artifact(path) for path in sorted(fixed_profiles.glob("*.json"))),
            ]
        },
        "sectors": sectors,
        "canonical_zero_triples": triple_certificates,
        "fixed_frame_orbit_certificates": orbit_certificates,
        "theorem": "Carrier-Forced Routed Incidence (THEOREMS.md, Theorem 1)",
        "conclusion": (
            "The exact canonical sector projectors reduce the four physical carriers. "
            "The endpoint carrier masks of each canonical zero triple are disjoint; "
            "the represented Rubik operators, their adjoints, and the anti-Hermitian "
            "operative numerators preserve those carriers; therefore AB=0 exactly "
            "for every registered operative pair on those triples."
        ),
    }
    assert certificate["qt_ht_commutator_verified_entrywise"]
    assert certificate["qt_sum_self_adjoint_verified"]
    assert certificate["ht_sum_self_adjoint_verified"]
    assert certificate["all_operative_generators_preserve_registered_carriers"]
    assert certificate["int64_pair_matmul_safety_verified"]
    assert certificate["int64_all_arithmetic_safety_verified"]
    assert set(certificate["int64_preoperation_audit"]["operation_kind_counts"]) == set(
        certificate["int64_preoperation_audit"]["coverage"]
    )
    assert all(row["projector_idempotence_verified"] for row in sectors)
    assert all(row["projector_self_adjoint_verified"] for row in sectors)
    assert all(row["qt_joint_eigenvalue_verified"] for row in sectors)
    assert all(row["ht_joint_eigenvalue_verified"] for row in sectors)
    assert all((row["exact_dimension"] or 0) > 0 for row in sectors)
    assert all(row["projector_preserves_registered_carriers"] for row in sectors)
    assert all(row["carrier_mask_verified"] for row in sectors)
    assert certificate["projector_family"]["pairwise_orthogonality_verified"]
    assert certificate["projector_family"]["completeness_verified"]
    assert certificate["projector_family"]["dimension_sum_verified"]
    assert all(row["all_generator_pairs_have_exact_zero_product"] for row in triple_certificates)
    assert all(row["all_observed_zero_routes_exactly_certified"] for row in orbit_certificates)
    write_json(Path("results/exact_certificates/canonical_carrier_zero_products.json"), certificate)
    print(
        f"exact canonical carrier masks certified; {len(orbit_certificates)} fixed-frame orbit profiles covered"
    )


if __name__ == "__main__":
    main()
