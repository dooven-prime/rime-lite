"""Numerical Rubik registration against the exact Paper IV set P_9."""

from __future__ import annotations

import _bootstrap  # noqa: F401

import argparse
from fractions import Fraction
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.cubie import CubieMove, TOTAL_DIM
from rime.cubieoperator import CubieSpectralOperator
from experiments.observation import (
    check_experiment_observation,
    format_observation_check,
    utc_now,
    write_experiment_observation,
)
TOL = 1e-10
CLUSTER_TOLERANCES = (1e-6, 1e-8, 1e-10, 1e-12)
RESULT_PATH = Path(
    "experiments/paper4/results/rubik_joint_spectrum_registration.observation.json"
)
EXPECTED = (
    ("S1", 20, Fraction(1), Fraction(1), Fraction(1)),
    ("S2", 2, Fraction(5, 6), Fraction(1), Fraction(8, 9)),
    ("S3", 39, Fraction(5, 6), Fraction(2, 3), Fraction(7, 9)),
    ("S4", 26, Fraction(1, 2), Fraction(1), Fraction(2, 3)),
    ("S5", 1, Fraction(1, 3), Fraction(1), Fraction(5, 9)),
    ("S6", 39, Fraction(1, 2), Fraction(2, 3), Fraction(5, 9)),
    ("S7", 66, Fraction(2, 3), Fraction(1, 3), Fraction(5, 9)),
    ("S8", 8, Fraction(0), Fraction(1), Fraction(1, 3)),
    ("S9", 27, Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
)
EXPECTED_BY_LABEL = {row[0]: row for row in EXPECTED}
DECLARED_SOURCES = (
    "experiments/paper4/validation/rubik_joint_spectrum_registration.py",
    "experiments/observation.py",
    "rime/base.py",
    "rime/cube.py",
    "rime/cubie.py",
    "rime/cubieoperator.py",
    "rime/helpers.py",
    "rime/spectral_utils.py",
    "pyproject.toml",
)


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _frobenius(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, "fro"))


def _mean_rayleigh_scalar(basis: np.ndarray, operator: np.ndarray) -> float:
    compressed = basis.conj().T @ operator @ basis
    return float(np.trace(compressed).real / basis.shape[1])


def _cluster_slices(eigenvalues: np.ndarray, tolerance: float) -> list[slice]:
    """Partition sorted eigenvalues by distance from each cluster's first value."""
    slices = []
    start = 0
    while start < len(eigenvalues):
        stop = start + 1
        while (
            stop < len(eigenvalues)
            and abs(eigenvalues[stop] - eigenvalues[start]) < tolerance
        ):
            stop += 1
        slices.append(slice(start, stop))
        start = stop
    return slices


def _joint_bases(
    qt: np.ndarray,
    ht: np.ndarray,
    tolerance: float,
) -> list[np.ndarray]:
    """Diagonalize QT, then diagonalize HT inside each numerical QT cluster."""
    qt_eigenvalues, qt_eigenvectors = np.linalg.eigh(qt)
    bases = []
    for qt_slice in _cluster_slices(qt_eigenvalues, tolerance):
        qt_basis = qt_eigenvectors[:, qt_slice]
        restricted_ht = qt_basis.conj().T @ ht @ qt_basis
        ht_eigenvalues, ht_eigenvectors = np.linalg.eigh(restricted_ht)
        for ht_slice in _cluster_slices(ht_eigenvalues, tolerance):
            bases.append(qt_basis @ ht_eigenvectors[:, ht_slice])
    return bases


def _raw_clusters(
    qt: np.ndarray,
    ht: np.ndarray,
    a18: np.ndarray,
    tolerance: float,
) -> list[dict]:
    clusters = []
    for basis in _joint_bases(qt, ht, tolerance):
        projector = basis @ basis.conj().T
        clusters.append(
            {
                "rank": int(basis.shape[1]),
                "basis": basis,
                "projector": projector,
                "q": _mean_rayleigh_scalar(basis, qt),
                "h": _mean_rayleigh_scalar(basis, ht),
                "a18": _mean_rayleigh_scalar(basis, a18),
            }
        )
    return clusters


def _match_to_p9(clusters: list[dict]) -> dict[str, dict]:
    if len(clusters) != len(EXPECTED):
        raise AssertionError(f"expected 9 numerical clusters, got {len(clusters)}")

    cost = np.empty((len(clusters), len(EXPECTED)), dtype=float)
    for i, cluster in enumerate(clusters):
        for j, (_, _, q_exact, h_exact, _) in enumerate(EXPECTED):
            cost[i, j] = max(
                abs(cluster["q"] - float(q_exact)),
                abs(cluster["h"] - float(h_exact)),
            )

    cluster_indices, expected_indices = linear_sum_assignment(cost)
    matched = {}
    for cluster_index, expected_index in zip(cluster_indices, expected_indices):
        label = EXPECTED[expected_index][0]
        record = dict(clusters[cluster_index])
        record["coordinate_match_linf"] = float(cost[cluster_index, expected_index])
        matched[label] = record
    return matched


def _tolerance_stability(
    matched_by_tolerance: dict[float, dict[str, dict]],
) -> dict[str, dict]:
    reference = matched_by_tolerance[TOL]
    census = {}
    for tolerance, matched in matched_by_tolerance.items():
        max_coordinate_drift = 0.0
        max_projector_drift = 0.0
        minimum_normalized_overlap = 1.0
        maximum_principal_angle = 0.0
        label_rank_stable = True

        for label, expected in EXPECTED_BY_LABEL.items():
            current = matched[label]
            baseline = reference[label]
            label_rank_stable &= current["rank"] == expected[1]
            max_coordinate_drift = max(
                max_coordinate_drift,
                abs(current["q"] - baseline["q"]),
                abs(current["h"] - baseline["h"]),
            )
            max_projector_drift = max(
                max_projector_drift,
                _frobenius(current["projector"] - baseline["projector"]),
            )
            overlap = float(
                np.trace(baseline["projector"] @ current["projector"]).real
                / expected[1]
            )
            minimum_normalized_overlap = min(minimum_normalized_overlap, overlap)
            singular_values = np.linalg.svd(
                baseline["basis"].conj().T @ current["basis"],
                compute_uv=False,
            )
            minimum_cosine = float(np.clip(np.min(singular_values), -1.0, 1.0))
            maximum_principal_angle = max(
                maximum_principal_angle,
                float(np.arccos(minimum_cosine)),
            )

        census[f"{tolerance:.0e}"] = {
            "cluster_count": len(matched),
            "label_rank_stable": bool(label_rank_stable),
            "label_rank_pairs": {
                label: matched[label]["rank"] for label, *_ in EXPECTED
            },
            "maximum_match_to_p9_linf": max(
                record["coordinate_match_linf"] for record in matched.values()
            ),
            "maximum_coordinate_drift_from_1e-10_linf": max_coordinate_drift,
            "maximum_projector_drift_from_1e-10_frobenius": max_projector_drift,
            "minimum_normalized_projector_overlap": minimum_normalized_overlap,
            "maximum_principal_angle_radians": maximum_principal_angle,
        }
    return census


def run_registration() -> dict:
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    operators, _ = op.build_per_axis_ops()
    qt = operators["QT_all"]
    ht = operators["HT_all"]
    a18 = operators["A_18"]

    matched_by_tolerance = {
        tolerance: _match_to_p9(_raw_clusters(qt, ht, a18, tolerance))
        for tolerance in CLUSTER_TOLERANCES
    }
    matched = matched_by_tolerance[TOL]
    projectors = [matched[label]["projector"] for label, *_ in EXPECTED]

    operator_residuals = {
        "qt_hermiticity": _frobenius(qt - qt.conj().T),
        "ht_hermiticity": _frobenius(ht - ht.conj().T),
        "qt_normality": _frobenius(qt @ qt.conj().T - qt.conj().T @ qt),
        "ht_normality": _frobenius(ht @ ht.conj().T - ht.conj().T @ ht),
        "qh_commutator": _frobenius(qt @ ht - ht @ qt),
        "a18_reconstruction": _frobenius(a18 - (2 * qt + ht) / 3),
    }

    identity = np.eye(TOTAL_DIM, dtype=np.complex128)
    projector_residuals = {
        "idempotence": max(_frobenius(P @ P - P) for P in projectors),
        "hermiticity": max(_frobenius(P - P.conj().T) for P in projectors),
        "orthogonality": max(
            _frobenius(projectors[i] @ projectors[j])
            for i in range(len(projectors))
            for j in range(i + 1, len(projectors))
        ),
        "completeness": _frobenius(sum(projectors) - identity),
        "rank_trace_error": max(
            abs(float(np.trace(P).real) - expected[1])
            for P, expected in zip(projectors, EXPECTED)
        ),
    }

    rows = []
    table_discrepancies = []
    qt_joint_residuals = []
    ht_joint_residuals = []
    a18_joint_residuals = []
    for expected in EXPECTED:
        label, expected_dim, q_exact, h_exact, a_exact = expected
        cluster = matched[label]
        projector = cluster["projector"]
        basis = cluster["basis"]
        dim = cluster["rank"]
        if dim != expected_dim:
            raise AssertionError(f"rank mismatch for {label}: {dim}")

        q_raw = cluster["q"]
        h_raw = cluster["h"]
        a_raw = cluster["a18"]
        q_error = abs(q_raw - float(q_exact))
        h_error = abs(h_raw - float(h_exact))
        a_error = abs(a_raw - float(a_exact))
        table_discrepancies.extend((q_error, h_error, a_error))

        q_residual = _frobenius(qt @ basis - q_raw * basis)
        h_residual = _frobenius(ht @ basis - h_raw * basis)
        a_residual = _frobenius(a18 @ basis - a_raw * basis)
        qt_joint_residuals.append(q_residual)
        ht_joint_residuals.append(h_residual)
        a18_joint_residuals.append(a_residual)

        rows.append(
            {
                "label": label,
                "rank": dim,
                "raw": {"q": q_raw, "h": h_raw, "a18": a_raw},
                "registered": {
                    "q": _fraction_text(q_exact),
                    "h": _fraction_text(h_exact),
                    "a18": _fraction_text(a_exact),
                },
                "table_discrepancy": {"q": q_error, "h": h_error, "a18": a_error},
                "coordinate_match_to_p9_linf": cluster["coordinate_match_linf"],
                "joint_eigen_residual": {
                    "qt": q_residual,
                    "ht": h_residual,
                    "a18": a_residual,
                },
            }
        )

    registered_points = np.array(
        [(float(q), float(h)) for _, _, q, h, _ in EXPECTED], dtype=float
    )
    joint_gaps_linf = [
        float(np.max(np.abs(registered_points[i] - registered_points[j])))
        for i in range(len(registered_points))
        for j in range(i + 1, len(registered_points))
    ]
    tolerance_census = _tolerance_stability(matched_by_tolerance)

    if any(value >= TOL for value in operator_residuals.values()):
        raise AssertionError(f"operator residual exceeded {TOL}")
    if any(value >= TOL for value in projector_residuals.values()):
        raise AssertionError(f"projector residual exceeded {TOL}")
    if max(table_discrepancies) >= TOL:
        raise AssertionError(f"table discrepancy exceeded {TOL}")
    if max(qt_joint_residuals + ht_joint_residuals + a18_joint_residuals) >= TOL:
        raise AssertionError(f"joint-eigen residual exceeded {TOL}")
    for tolerance, audit in tolerance_census.items():
        if not audit["label_rank_stable"]:
            raise AssertionError(f"label-rank pairs changed at tolerance {tolerance}")
        if audit["maximum_match_to_p9_linf"] >= TOL:
            raise AssertionError(f"coordinate registration failed at {tolerance}")
        if audit["maximum_coordinate_drift_from_1e-10_linf"] >= TOL:
            raise AssertionError(f"coordinate drift exceeded {TOL} at {tolerance}")
        if audit["maximum_projector_drift_from_1e-10_frobenius"] >= TOL:
            raise AssertionError(f"projector drift exceeded {TOL} at {tolerance}")
        if 1.0 - audit["minimum_normalized_projector_overlap"] >= TOL:
            raise AssertionError(f"projector overlap changed at {tolerance}")

    print("Paper IV Rubik joint-spectrum registration")
    print("  claim status: computational certificate")
    print(f"  clusters: {len(rows)}; ranks: {[row['rank'] for row in rows]}")
    for key, value in operator_residuals.items():
        print(f"  {key}: {value:.3e}")
    for key, value in projector_residuals.items():
        print(f"  projector_{key}: {value:.3e}")
    print(f"  max raw-to-P_9 table discrepancy: {max(table_discrepancies):.3e}")
    print(
        "  max joint-eigen residual: "
        f"{max(qt_joint_residuals + ht_joint_residuals + a18_joint_residuals):.3e}"
    )
    print(f"  minimum P_9 joint-point L-infinity gap: {min(joint_gaps_linf):.6f}")
    for tolerance, audit in tolerance_census.items():
        print(
            f"  clustering tol={tolerance}: n={audit['cluster_count']} "
            f"label-rank={audit['label_rank_stable']} "
            f"coord-drift={audit['maximum_coordinate_drift_from_1e-10_linf']:.3e} "
            f"projector-drift={audit['maximum_projector_drift_from_1e-10_frobenius']:.3e} "
            f"min-overlap={audit['minimum_normalized_projector_overlap']:.16f}"
        )
    print("REGISTRATION PASSED: numerical clusters match the declared set P_9")

    return {
        "summary": {
            "passed": True,
            "claim_status": "computational_certificate",
            "cluster_count": len(rows),
            "ambient_dimension": TOTAL_DIM,
            "maximum_raw_to_p9_table_discrepancy": max(table_discrepancies),
            "maximum_joint_eigen_residual": max(
                qt_joint_residuals + ht_joint_residuals + a18_joint_residuals
            ),
            "minimum_p9_joint_point_linf_gap": min(joint_gaps_linf),
        },
        "operator_residuals": operator_residuals,
        "projector_residuals": projector_residuals,
        "clustering_tolerance_census": tolerance_census,
        "registered_clusters": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-result", action="store_true")
    mode.add_argument("--no-write-result", action="store_true")
    args = parser.parse_args()

    result_path = args.result if args.result.is_absolute() else ROOT / args.result
    if args.check_result:
        check = check_experiment_observation(result_path, root=ROOT)
        print(format_observation_check(args.result, check))
        return 0 if check.reusable else 1

    started_at = utc_now()
    start = perf_counter()
    observations = run_registration()
    elapsed = perf_counter() - start
    print(f"  elapsed: {elapsed:.3f}s")

    if not args.no_write_result:
        write_experiment_observation(
            result_path,
            root=ROOT,
            experiment_id="paper4-rubik-joint-spectrum-registration",
            paper="Paper IV",
            command=[
                "python",
                "experiments/paper4/validation/rubik_joint_spectrum_registration.py",
            ],
            sources=DECLARED_SOURCES,
            parameters={
                "residual_threshold": TOL,
                "clustering_tolerances": list(CLUSTER_TOLERANCES),
                "dtype": "complex128",
                "matching_metric": "L-infinity on raw (q,h) coordinates",
                "reference_tolerance": TOL,
                "joint_diagonalization": (
                    "Diagonalize QT, cluster its eigenvalues by absolute gap < tau, "
                    "then diagonalize HT within each retained QT cluster."
                ),
                "cluster_representative": "normalized trace / mean Rayleigh scalar",
                "rank_definition": "number of orthonormal basis columns",
                "rational_reconstruction": "none; compare to the predeclared set P_9",
                "declared_coordinate_denominators": {"q_h": 6, "a18": 9},
            },
            observations=observations,
            claim_status="computational_certificate",
            claim_scope=(
                "Numerical registration of nine QT/HT joint clusters against "
                "the independent exact rational set P_9 used by Paper IV."
            ),
            limitations=[
                "Machine-zero residuals do not prove exact QT/HT commutation.",
                "Small raw-to-table discrepancies do not prove exact rational eigenvalues.",
                "The actual Rubik collision-quotient statement remains conditional on exact registration.",
            ],
            started_at_utc=started_at,
            elapsed_seconds=elapsed,
            distributions=("numpy", "scipy", "rime"),
        )
        print(f"WROTE OBSERVATION: {args.result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
