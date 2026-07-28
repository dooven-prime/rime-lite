"""Paper VI v2: linearized constraints and pointwise typed support certificate.

The audit separates three claims:

1. the full complex commutator Jacobian has rank 11 and nullity 7;
2. adjoining the linearized QT/HT normality equations gives rank 14 and
   nullity 4 at the canonical point;
3. the combined kernel contains both exact class-scaling gauge directions and
   three inverse-pair-symmetric QT-axis directions with certified sample points.

Joint sectors are constructed only after commutativity, Hermiticity, and
normality checks pass. Operator support R1^op[rho] and Lie support R1^Lie[X]
are reported separately. No R2, word-depth, routed-depth, or Lie-depth wall is
claimed by this script.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import numpy as np

from rime.accessibility import compute_R1
from rime.cubie import CubieMove
from rime.spectral_utils import build_projectors, joint_diag_sectors


TOL = 1e-8
TOL_LINEAR = 1e-10
CANONICAL_DIMS = [1, 2, 8, 20, 26, 27, 39, 39, 66]
AXIS_DIMS = [1, 1, 1, 8, 9, 13, 13, 13, 13, 18, 20, 22, 26, 26, 44]


def _real_vector(matrix: np.ndarray) -> np.ndarray:
    return np.concatenate([matrix.real.ravel(), matrix.imag.ravel()])


def _matrix_rank(matrix: np.ndarray, tol: float = TOL_LINEAR) -> tuple[int, np.ndarray, np.ndarray]:
    _, singular_values, vt = np.linalg.svd(matrix, full_matrices=False)
    threshold = tol * max(float(singular_values[0]), 1.0)
    rank = int(np.sum(singular_values > threshold))
    return rank, singular_values, vt


def _rank_gap(singular_values: np.ndarray, rank: int) -> tuple[float, float, float]:
    retained = float(singular_values[rank - 1])
    discarded = float(singular_values[rank])
    ratio = retained / max(discarded, np.finfo(float).tiny)
    return retained, discarded, ratio


def _normality_derivative(operator: np.ndarray, derivative: np.ndarray) -> np.ndarray:
    return (
        derivative @ operator.conj().T
        + operator @ derivative.conj().T
        - derivative.conj().T @ operator
        - operator.conj().T @ derivative
    )


def _weighted_pair(
    weights: np.ndarray,
    rhos: list[np.ndarray],
    qt_indices: list[int],
    ht_indices: list[int],
) -> tuple[np.ndarray, np.ndarray]:
    qt_total = float(np.sum(weights[qt_indices]))
    ht_total = float(np.sum(weights[ht_indices]))
    qt = sum(weights[i] * rhos[i] for i in qt_indices) / qt_total
    ht = sum(weights[i] * rhos[i] for i in ht_indices) / ht_total
    return qt, ht


def _finite_order_principal_log(unitary: np.ndarray, order: int) -> np.ndarray:
    """Principal finite-order logarithm with arguments in (-pi, pi]."""
    identity = np.eye(unitary.shape[0], dtype=np.complex128)
    powers = [identity]
    for _ in range(1, order):
        powers.append(powers[-1] @ unitary)

    logarithm = np.zeros_like(unitary)
    for index in range(order):
        eigenvalue = np.exp(2j * np.pi * index / order)
        angle = float(np.angle(eigenvalue))
        if order % 2 == 0 and index == order // 2:
            angle = float(np.pi)
        projector = sum(
            eigenvalue ** (-power) * powers[power] for power in range(order)
        ) / order
        logarithm += 1j * angle * projector
    return (logarithm - logarithm.conj().T) / 2


def _projector_certificate(projectors: list[np.ndarray]) -> dict[str, float]:
    ambient_dim = projectors[0].shape[0]
    return {
        "idempotence": max(
            float(np.linalg.norm(projector @ projector - projector, "fro"))
            for projector in projectors
        ),
        "hermiticity": max(
            float(np.linalg.norm(projector - projector.conj().T, "fro"))
            for projector in projectors
        ),
        "orthogonality": max(
            float(np.linalg.norm(left @ right, "fro"))
            for i, left in enumerate(projectors)
            for j, right in enumerate(projectors)
            if i != j
        ),
        "completeness": float(
            np.linalg.norm(sum(projectors) - np.eye(ambient_dim), "fro")
        ),
    }


def _support_certificate(
    bases: list[np.ndarray], operators: list[np.ndarray]
) -> dict[str, float | int]:
    norms = [
        float(np.linalg.norm(left.conj().T @ operator @ right, "fro"))
        for operator in operators
        for left in bases
        for right in bases
    ]
    retained = [value for value in norms if value > TOL]
    discarded = [value for value in norms if value <= TOL]
    return {
        "count": len(retained),
        "minimum_retained_norm": min(retained, default=0.0),
        "maximum_discarded_norm": max(discarded, default=0.0),
    }


def _pair_certificate(qt: np.ndarray, ht: np.ndarray) -> dict[str, float]:
    return {
        "commutator": float(np.linalg.norm(qt @ ht - ht @ qt, "fro")),
        "qt_normality": float(
            np.linalg.norm(qt @ qt.conj().T - qt.conj().T @ qt, "fro")
        ),
        "ht_normality": float(
            np.linalg.norm(ht @ ht.conj().T - ht.conj().T @ ht, "fro")
        ),
        "qt_hermiticity": float(np.linalg.norm(qt - qt.conj().T, "fro")),
        "ht_hermiticity": float(np.linalg.norm(ht - ht.conj().T, "fro")),
    }


def _sector_record(
    label: str,
    weights: np.ndarray,
    rhos: list[np.ndarray],
    lie_generators: list[np.ndarray],
    qt_indices: list[int],
    ht_indices: list[int],
) -> dict:
    qt, ht = _weighted_pair(weights, rhos, qt_indices, ht_indices)
    pair = _pair_certificate(qt, ht)
    assert max(pair.values()) < TOL, (label, pair)

    sectors = joint_diag_sectors([qt, ht], tol=TOL)
    bases = [basis for _, basis in sectors]
    projectors = build_projectors(sectors, qt.shape[0])
    projector = _projector_certificate(projectors)
    assert max(projector.values()) < TOL, (label, projector)
    r1_op = _support_certificate(bases, rhos)
    r1_lie = _support_certificate(bases, lie_generators)
    assert r1_op["count"] == int(np.sum(compute_R1(bases, rhos, tol=TOL)))
    assert r1_lie["count"] == int(
        np.sum(compute_R1(bases, lie_generators, tol=TOL))
    )

    return {
        "label": label,
        "qt": qt,
        "ht": ht,
        "bases": bases,
        "projectors": projectors,
        "dimensions": sorted(basis.shape[1] for basis in bases),
        "pair": pair,
        "projector": projector,
        "r1_op": r1_op["count"],
        "r1_lie": r1_lie["count"],
        "r1_op_gap": r1_op,
        "r1_lie_gap": r1_lie,
    }


def main() -> None:
    keys = list(CubieMove.prim_moves.keys())
    rhos = [CubieMove.prim_moves[key].rho().astype(np.complex128) for key in keys]
    qt_indices = [i for i, key in enumerate(keys) if key[2] != 2]
    ht_indices = [i for i, key in enumerate(keys) if key[2] == 2]
    base_weights = np.ones(len(keys))
    qt0, ht0 = _weighted_pair(base_weights, rhos, qt_indices, ht_indices)

    commutator_columns = []
    joint_columns = []
    for index in range(len(keys)):
        if index in qt_indices:
            dqt = (rhos[index] - qt0) / len(qt_indices)
            dht = np.zeros_like(ht0)
        else:
            dqt = np.zeros_like(qt0)
            dht = (rhos[index] - ht0) / len(ht_indices)
        dcomm = dqt @ ht0 - ht0 @ dqt + qt0 @ dht - dht @ qt0
        dnormal_qt = _normality_derivative(qt0, dqt)
        dnormal_ht = _normality_derivative(ht0, dht)
        commutator_columns.append(_real_vector(dcomm))
        joint_columns.append(
            np.concatenate(
                [_real_vector(dcomm), _real_vector(dnormal_qt), _real_vector(dnormal_ht)]
            )
        )

    commutator_map = np.column_stack(commutator_columns)
    joint_map = np.column_stack(joint_columns)
    comm_rank, comm_singular, _ = _matrix_rank(commutator_map)
    joint_rank, joint_singular, joint_vt = _matrix_rank(joint_map)
    comm_gap = _rank_gap(comm_singular, comm_rank)
    joint_gap = _rank_gap(joint_singular, joint_rank)
    joint_kernel = joint_vt[joint_rank:, :]

    directions: dict[str, np.ndarray] = {}
    ht_gauge = np.zeros(len(keys))
    ht_gauge[ht_indices] = 1.0
    directions["uniform HT gauge"] = ht_gauge
    for axis in range(3):
        direction = np.zeros(len(keys))
        for index, key in enumerate(keys):
            if key[0] == axis and key[2] != 2:
                direction[index] = 1.0
        directions[f"QT axis {axis}"] = direction

    qt_gauge = sum(directions[f"QT axis {axis}"] for axis in range(3))

    direction_matrix = np.column_stack(list(directions.values()))
    assert np.linalg.matrix_rank(direction_matrix, tol=TOL_LINEAR) == 4
    direction_residuals = {}
    for label, direction in directions.items():
        unit = direction / np.linalg.norm(direction)
        projection = joint_kernel.T @ (joint_kernel @ unit)
        direction_residuals[label] = float(np.linalg.norm(unit - projection))

    lie_generators = [
        _finite_order_principal_log(rho, 2 if key[2] == 2 else 4)
        for rho, key in zip(rhos, keys)
    ]
    assert max(
        np.linalg.norm(generator + generator.conj().T, "fro")
        for generator in lie_generators
    ) < TOL

    canonical = _sector_record(
        "canonical", base_weights, rhos, lie_generators, qt_indices, ht_indices
    )
    axis_records = []
    for axis in range(3):
        weights = base_weights + 0.1 * directions[f"QT axis {axis}"]
        axis_records.append(
            _sector_record(
                f"QT axis {axis}, eps=0.1",
                weights,
                rhos,
                lie_generators,
                qt_indices,
                ht_indices,
            )
        )

    gauge_operator_drifts = {}
    for label, direction in {
        "uniform HT": directions["uniform HT gauge"],
        "uniform QT": qt_gauge,
    }.items():
        gauge_qt, gauge_ht = _weighted_pair(
            base_weights + 0.1 * direction,
            rhos,
            qt_indices,
            ht_indices,
        )
        gauge_operator_drifts[label] = max(
            float(np.linalg.norm(gauge_qt - qt0, "fro")),
            float(np.linalg.norm(gauge_ht - ht0, "fro")),
        )

    print("=" * 72)
    print("Paper VI v2: Linearized Constraints and Pointwise Typed R1 Audit")
    print("=" * 72)
    print(f"full commutator Jacobian: rank={comm_rank}, nullity={len(keys) - comm_rank}")
    print(f"commutator + normality map: rank={joint_rank}, nullity={len(keys) - joint_rank}")
    print(f"commutator singular values: {np.round(comm_singular, 6).tolist()}")
    print(f"combined singular values: {np.round(joint_singular, 6).tolist()}")
    print(
        "commutator rank gap: "
        f"retained={comm_gap[0]:.12e}, discarded={comm_gap[1]:.12e}, "
        f"ratio={comm_gap[2]:.3e}"
    )
    print(
        "combined rank gap: "
        f"retained={joint_gap[0]:.12e}, discarded={joint_gap[1]:.12e}, "
        f"ratio={joint_gap[2]:.3e}"
    )
    print("interpretable combined-kernel directions:")
    for label, residual in direction_residuals.items():
        print(f"  {label}: projection residual={residual:.3e}")
    for label, drift in gauge_operator_drifts.items():
        print(f"{label} gauge-family operator drift at eps=0.1: {drift:.3e}")
    print()
    print("validated sector records:")
    for record in [canonical, *axis_records]:
        pair = record["pair"]
        projector = record["projector"]
        print(
            f"  {record['label']}: sectors={len(record['bases'])}, "
            f"R1^op={record['r1_op']}, R1^Lie={record['r1_lie']}, "
            f"comm={pair['commutator']:.3e}, "
            f"normal=({pair['qt_normality']:.3e},{pair['ht_normality']:.3e}), "
            f"projector_max={max(projector.values()):.3e}"
        )
        print(f"    dimensions={record['dimensions']}")
        print(
            "    Lie-support gap: "
            f"retained={record['r1_lie_gap']['minimum_retained_norm']:.3e}, "
            f"discarded={record['r1_lie_gap']['maximum_discarded_norm']:.3e}"
        )

    assert comm_rank == 11
    assert joint_rank == 14
    assert comm_gap[0] > 1e-2 and comm_gap[1] < 1e-12
    assert joint_gap[0] > 1e-2 and joint_gap[1] < 1e-12
    assert max(direction_residuals.values()) < TOL_LINEAR
    assert max(gauge_operator_drifts.values()) < TOL
    assert canonical["dimensions"] == CANONICAL_DIMS
    assert canonical["r1_op"] == 438
    assert canonical["r1_lie"] == 408
    expected_lie_counts = [832, 832, 832]
    for record, expected_lie_count in zip(axis_records, expected_lie_counts):
        assert record["dimensions"] == AXIS_DIMS
        assert record["r1_op"] == 1006
        assert record["r1_lie"] == expected_lie_count
    assert canonical["r1_lie_gap"]["minimum_retained_norm"] > 1e-1
    assert max(
        record["r1_lie_gap"]["maximum_discarded_norm"]
        for record in [canonical, *axis_records]
    ) < 1e-10
    print("\n[snapshot OK: normality-gated sectors and typed R1 are separately certified]")


if __name__ == "__main__":
    main()
