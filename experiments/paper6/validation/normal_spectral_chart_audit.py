"""Paper VI v2.1: linearized certificates and normality-gated registrations.

The audit separates three claims:

1. the full complex commutator Jacobian has rank 11 and nullity 7;
2. adjoining the linearized QT/HT normality equations gives rank 14 and
   nullity 4 at the canonical point;
3. the combined kernel contains both exact class-scaling gauge directions and
   three inverse-pair-symmetric QT-axis directions with certified sample points;
4. admission is fail-closed before projector construction, with one explicit
   nonnormal single-generator negative control.

Joint sectors are constructed only after commutativity, Hermiticity, and
normality checks pass. Operator support R1^op[rho] and Lie support R1^Lie[X]
are reported separately. No R2, word-depth, routed-depth, or Lie-depth wall is
claimed by this script.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from rime.accessibility import compute_R1
from rime.cubie import CubieMove
from rime.spectral_utils import build_projectors, joint_diag_sectors


TOL = 1e-8
TOL_LINEAR = 1e-10
CANONICAL_DIMS = [1, 2, 8, 20, 26, 27, 39, 39, 66]
AXIS_DIMS = [1, 1, 1, 8, 9, 13, 13, 13, 13, 18, 20, 22, 26, 26, 44]
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = ROOT / "experiments" / "paper6" / "results" / "normality_gated_admission_v2_1.json"
FIGURE_DATA_PATH = ROOT / "experiments" / "paper6" / "results" / "figure_data.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Paper VI v2.1 linearized and admission certificates."
    )
    parser.add_argument(
        "--write-results",
        action="store_true",
        help="Rewrite the versioned result record and figure-data projection.",
    )
    return parser.parse_args()


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
        "status": "ADMITTED",
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


def _rejected_record(
    label: str,
    weights: np.ndarray,
    rhos: list[np.ndarray],
    qt_indices: list[int],
    ht_indices: list[int],
) -> dict:
    qt, ht = _weighted_pair(weights, rhos, qt_indices, ht_indices)
    pair = _pair_certificate(qt, ht)
    failed = [name for name, value in pair.items() if value >= TOL]
    assert failed, (label, pair)
    return {
        "label": label,
        "status": "REJECTED",
        "qt": qt,
        "ht": ht,
        "bases": None,
        "projectors": None,
        "dimensions": None,
        "pair": pair,
        "projector": None,
        "r1_op": None,
        "r1_lie": None,
        "r1_op_gap": None,
        "r1_lie_gap": None,
        "failed_gates": failed,
    }


def _public_admission_record(record: dict, perturbation: dict) -> dict:
    projector = record["projector"]
    public = {
        "sample_id": perturbation["sample_id"],
        "label": record["label"],
        "weight_perturbation": perturbation,
        "status": record["status"],
        "pair_residuals": record["pair"],
        "projector_residuals": projector,
        "projector_residual_max": (
            max(projector.values()) if projector is not None else None
        ),
        "sector_count": (
            len(record["bases"]) if record["bases"] is not None else None
        ),
        "sector_dimensions": record["dimensions"],
        "r1_op": record["r1_op"],
        "r1_lie": record["r1_lie"],
        "r1_op_gap": record["r1_op_gap"],
        "r1_lie_gap": record["r1_lie_gap"],
    }
    if record["status"] == "REJECTED":
        public["failed_gates"] = record["failed_gates"]
        public["post_admission_fields"] = "NOT_COMPUTED"
    return public


def _linearized_record(
    label: str,
    singular_values: np.ndarray,
    rank: int,
    gap: tuple[float, float, float],
) -> dict:
    return {
        "label": label,
        "rank": rank,
        "nullity": int(len(singular_values) - rank),
        "rank_threshold_policy": {
            "multiplier": TOL_LINEAR,
            "reference_scale": "max(largest_singular_value, 1.0)",
            "effective_threshold": TOL_LINEAR
            * max(float(singular_values[0]), 1.0),
        },
        "singular_values": [float(value) for value in singular_values],
        "smallest_retained": gap[0],
        "largest_discarded": gap[1],
        "retained_discarded_ratio": gap[2],
    }


def _build_result(
    *,
    keys: list[tuple[int, int, int]],
    commutator_map: dict,
    combined_map: dict,
    direction_residuals: dict[str, float],
    gauge_operator_drifts: dict[str, float],
    admission_records: list[dict],
) -> dict:
    script_path = Path(__file__).resolve()
    return {
        "schema": "paper6.normality-gated-admission.v2.1",
        "paper_version": "2.1",
        "claim_scope": (
            "linearized numerical certificates and pointwise normality-gated "
            "registrations; no nonlinear chart, continuation, or moving-field theorem"
        ),
        "implementation": {
            "path": script_path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(script_path),
        },
        "realization": {
            "dtype": "complex128",
            "ambient_dimension": 228,
            "generator_count": len(keys),
            "generator_keys": [list(key) for key in keys],
        },
        "numerical_policy": {
            "matrix_norm": "frobenius",
            "admission_tolerance": TOL,
            "support_threshold": TOL,
            "sector_clustering_threshold": TOL,
            "rank_threshold_multiplier": TOL_LINEAR,
            "rank_reference_scale": "max(largest_singular_value, 1.0)",
        },
        "claim_levels": {
            "linearized_maps": "Computational Certificate",
            "admission_residuals": "Computational Certificate",
            "projector_residuals": "Computational Certificate",
            "sector_and_typed_support_counts": "Computational Observation",
        },
        "linearized_maps": [commutator_map, combined_map],
        "combined_kernel_direction_residuals": direction_residuals,
        "exact_gauge_family_operator_drifts": gauge_operator_drifts,
        "admission_rule": {
            "pre_projector_required_fields": [
                "commutator",
                "qt_normality",
                "ht_normality",
                "qt_hermiticity",
                "ht_hermiticity",
            ],
            "pre_projector_rule": "all residuals < admission_tolerance",
            "post_projector_rule": "all projector residuals < admission_tolerance",
            "failure_behavior": (
                "REJECTED; projector, sector, and typed-support fields are not computed"
            ),
        },
        "admission_records": admission_records,
        "archive_correction_ledger": [
            {
                "legacy_result": "9 -> 24--35 sectors",
                "failure_reason": (
                    "nonnormal samples were processed with a Hermitian eigensolver"
                ),
                "current_status": "REJECTED",
            },
            {
                "legacy_result": "438 -> 6334 raw support",
                "failure_reason": (
                    "raw rho(g) support was not declared as operator- or Lie-typed support"
                ),
                "current_status": "PROVENANCE_ONLY",
            },
            {
                "legacy_result": "legacy R2 and D claims",
                "failure_reason": (
                    "no typed routed-product, word, commutator, or closure certificate"
                ),
                "current_status": "WITHDRAWN",
            },
        ],
    }


def _build_figure_data(result: dict, result_digest: str) -> dict:
    return {
        "schema": "paper6.figure-data.v2.1",
        "claim_scope": result["claim_scope"],
        "provenance": {
            "sources": [
                result["implementation"],
                {
                    "path": RESULT_PATH.relative_to(ROOT).as_posix(),
                    "sha256": result_digest,
                },
            ]
        },
        "numerical_policy": result["numerical_policy"],
        "linearized_maps": result["linearized_maps"],
        "admission_records": result["admission_records"],
    }


def _assert_match(expected, actual, path: str = "root") -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict), path
        assert set(expected) == set(actual), path
        for key in expected:
            _assert_match(expected[key], actual[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        assert isinstance(actual, list), path
        assert len(expected) == len(actual), path
        for index, (left, right) in enumerate(zip(expected, actual)):
            _assert_match(left, right, f"{path}[{index}]")
        return
    if isinstance(expected, float):
        assert isinstance(actual, (int, float)), path
        assert np.isclose(expected, actual, rtol=1e-9, atol=1e-12), (
            path,
            expected,
            actual,
        )
        return
    assert expected == actual, (path, expected, actual)


def main() -> None:
    args = _parse_args()
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

    rejected_index = qt_indices[0]
    rejected_weights = base_weights.copy()
    rejected_weights[rejected_index] += 0.1
    rejected_control = _rejected_record(
        f"single QT {CubieMove.move_label(keys[rejected_index])}, eps=0.1",
        rejected_weights,
        rhos,
        qt_indices,
        ht_indices,
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

    perturbations = [
        {
            "sample_id": "canonical",
            "kind": "none",
            "epsilon": 0.0,
        },
        *[
            {
                "sample_id": f"qt_axis_{axis}_eps_0_1",
                "kind": "qt_axis_symmetric",
                "axis": axis,
                "epsilon": 0.1,
            }
            for axis in range(3)
        ],
        {
            "sample_id": "single_qt_generator_eps_0_1_negative_control",
            "kind": "single_generator",
            "generator_key": list(keys[rejected_index]),
            "generator_label": CubieMove.move_label(keys[rejected_index]),
            "epsilon": 0.1,
        },
    ]
    all_records = [canonical, *axis_records, rejected_control]
    admission_records = [
        _public_admission_record(record, perturbation)
        for record, perturbation in zip(all_records, perturbations)
    ]
    result = _build_result(
        keys=keys,
        commutator_map=_linearized_record(
            "commutativity", comm_singular, comm_rank, comm_gap
        ),
        combined_map=_linearized_record(
            "commutativity + normality", joint_singular, joint_rank, joint_gap
        ),
        direction_residuals=direction_residuals,
        gauge_operator_drifts=gauge_operator_drifts,
        admission_records=admission_records,
    )

    print("=" * 72)
    print("Paper VI v2.1: Linearized Certificates and Gated Registrations")
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
    print("admission records:")
    for record in all_records:
        pair = record["pair"]
        projector = record["projector"]
        if record["status"] == "REJECTED":
            print(
                f"  {record['label']}: status=REJECTED, "
                f"comm={pair['commutator']:.3e}, "
                f"normal=({pair['qt_normality']:.3e},{pair['ht_normality']:.3e}), "
                f"hermitian=({pair['qt_hermiticity']:.3e},"
                f"{pair['ht_hermiticity']:.3e}), "
                f"failed={record['failed_gates']}"
            )
            continue
        print(
            f"  {record['label']}: status=ADMITTED, sectors={len(record['bases'])}, "
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
        assert record["status"] == "ADMITTED"
        assert record["dimensions"] == AXIS_DIMS
        assert record["r1_op"] == 1006
        assert record["r1_lie"] == expected_lie_count
    assert canonical["status"] == "ADMITTED"
    assert rejected_control["status"] == "REJECTED"
    assert rejected_control["projector"] is None
    assert rejected_control["r1_op"] is None
    assert set(rejected_control["failed_gates"]) == {
        "commutator",
        "qt_normality",
        "qt_hermiticity",
    }
    assert canonical["r1_lie_gap"]["minimum_retained_norm"] > 1e-1
    assert max(
        record["r1_lie_gap"]["maximum_discarded_norm"]
        for record in [canonical, *axis_records]
    ) < 1e-10

    if args.write_results:
        _write_json(RESULT_PATH, result)
        figure_data = _build_figure_data(result, _sha256(RESULT_PATH))
        _write_json(FIGURE_DATA_PATH, figure_data)
        print(f"wrote {RESULT_PATH.relative_to(ROOT)}")
        print(f"wrote {FIGURE_DATA_PATH.relative_to(ROOT)}")
    else:
        committed_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        _assert_match(result, committed_result)
        expected_figure_data = _build_figure_data(
            committed_result, _sha256(RESULT_PATH)
        )
        committed_figure_data = json.loads(
            FIGURE_DATA_PATH.read_text(encoding="utf-8")
        )
        _assert_match(expected_figure_data, committed_figure_data)
        print("validated committed v2.1 result and figure-data projection")

    print("\n[snapshot OK: admission gates and post-admission fields are separated]")


if __name__ == "__main__":
    main()
