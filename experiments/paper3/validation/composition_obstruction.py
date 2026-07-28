"""Canonical support-graph versus matrix-composition certificate for Paper III."""

from __future__ import annotations

import _bootstrap  # noqa: F401

import argparse
from pathlib import Path
import sys
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.cubie import BLOCK_RANGES, CubieMove
from rime.cubieoperator import CubieSpectralOperator
from experiments.observation import (
    check_experiment_observation,
    format_observation_check,
    git_provenance,
    package_versions,
    utc_now,
    write_experiment_observation,
)
from rime.spectral_utils import (
    block_set,
    find_graph_only_two_step_pairs,
    joint_diag_sectors,
    max_two_step_composition,
    sector_bases_from_projectors,
    select_canonical_intermediate,
)


TOL_EDGE = 0.05
TOL_COMPOSITION = 1e-10
BLOCK_SUPPORT_THRESHOLD = 0.01
CLUSTER_TOLERANCES = (1e-6, 1e-8, 1e-10, 1e-12)
EXPECTED_DIMS = [1, 2, 8, 20, 26, 27, 39, 39, 66]
EXPECTED = {
    (1, 3, 5),  # S2--S4 via S6
    (2, 8, 6),  # S3--S9 via S7
    (3, 4, 5),  # S4--S5 via S6
    (3, 7, 8),  # S4--S8 via S9
    (5, 8, 6),  # S6--S9 via S7
}
RESULT_PATH = Path("experiments/paper3/results/composition_obstruction.observation.json")
DECLARED_SOURCES = (
    "experiments/paper3/validation/composition_obstruction.py",
    "experiments/observation.py",
    "rime/base.py",
    "rime/cube.py",
    "rime/cubie.py",
    "rime/cubieoperator.py",
    "rime/helpers.py",
    "rime/spectral_utils.py",
    "pyproject.toml",
)


def direct_support_matrix(rho_matrices, bases):
    """Compute maximum direct transport norms in reduced sector bases."""
    n = len(bases)
    K = np.zeros((n, n), dtype=float)
    for rho in rho_matrices:
        dense = rho.toarray() if hasattr(rho, "toarray") else np.asarray(rho)
        rho_bases = [dense @ basis for basis in bases]
        for i, Bi in enumerate(bases):
            for j, rho_Bj in enumerate(rho_bases):
                K[i, j] = max(
                    K[i, j],
                    np.linalg.norm(Bi.conj().T @ rho_Bj, "fro"),
                )
    return K


def maximum_cross_block_projector_norm(projectors):
    """Return the largest off-physical-block projector norm."""
    ranges = list(BLOCK_RANGES.values())
    maximum = 0.0
    for projector in projectors:
        for a, (start_a, end_a) in enumerate(ranges):
            for b, (start_b, end_b) in enumerate(ranges):
                if a == b:
                    continue
                block = projector[start_a:end_a, start_b:end_b]
                maximum = max(maximum, np.linalg.norm(block, "fro"))
    return maximum


def qh_registration_certificate(op, projectors):
    """Return numerical validity and tolerance-stability data for QH sectors."""
    operators, _ = op.build_per_axis_ops()
    qh_operators = [
        operators["A_18"],
        operators["QT_all"],
        operators["HT_all"],
    ]
    identity = np.eye(qh_operators[0].shape[0], dtype=np.complex128)
    pairwise_commutator = max(
        np.linalg.norm(left @ right - right @ left, "fro")
        for index, left in enumerate(qh_operators)
        for right in qh_operators[index + 1 :]
    )
    idempotence = max(np.linalg.norm(P @ P - P, "fro") for P in projectors)
    hermiticity = max(np.linalg.norm(P - P.conj().T, "fro") for P in projectors)
    orthogonality = max(
        np.linalg.norm(projectors[i] @ projectors[j], "fro")
        for i in range(len(projectors))
        for j in range(len(projectors))
        if i != j
    )
    completeness = np.linalg.norm(sum(projectors) - identity, "fro")
    joint_invariance = max(
        np.linalg.norm(P @ operator - operator @ P, "fro")
        for P in projectors
        for operator in qh_operators
    )
    block_diagonality = maximum_cross_block_projector_norm(projectors)
    tolerance_census = {}
    for tolerance in CLUSTER_TOLERANCES:
        sectors = joint_diag_sectors(qh_operators, tol=tolerance)
        tolerance_census[tolerance] = sorted(V.shape[1] for _, V in sectors)

    return {
        "pairwise_commutator": pairwise_commutator,
        "idempotence": idempotence,
        "hermiticity": hermiticity,
        "orthogonality": orthogonality,
        "completeness": completeness,
        "joint_invariance": joint_invariance,
        "block_diagonality": block_diagonality,
        "tolerance_census": tolerance_census,
    }


def run_audit():
    versions = package_versions(("numpy", "scipy", "rime"))
    git = git_provenance(ROOT)
    op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
    sectors = op.center_decomposition()
    projectors = sectors["projectors"]
    rho_matrices = list(op.rho_matrices())
    bases = sector_bases_from_projectors(projectors)
    K = direct_support_matrix(rho_matrices, bases)
    block_sets = [
        block_set(projector, BLOCK_RANGES, BLOCK_SUPPORT_THRESHOLD)
        for projector in projectors
    ]

    graph_pairs = find_graph_only_two_step_pairs(K, block_sets, TOL_EDGE)
    canonical = {
        (i, j, select_canonical_intermediate(candidates, K, TOL_EDGE))
        for i, j, candidates in graph_pairs
    }
    if canonical != EXPECTED:
        raise AssertionError(
            f"canonical graph-only triples changed: {sorted(canonical)}"
        )

    registration = qh_registration_certificate(op, projectors)
    projector_cross_block = registration["block_diagonality"]
    direct_edges = [
        (i, j)
        for i in range(len(projectors))
        for j in range(i + 1, len(projectors))
        if K[i, j] > TOL_EDGE
    ]
    if len(direct_edges) != 10:
        raise AssertionError(f"expected 10 direct edges, got {len(direct_edges)}")

    print("Paper III composition-obstruction audit")
    print(
        "  environment: "
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, "
        f"NumPy {versions['numpy']}, SciPy {versions['scipy']}, "
        f"rime {versions['rime']}"
    )
    print(f"  git: {git['commit']} ({git['tracked_worktree']})")
    print(f"  sectors: {len(projectors)}")
    print(f"  generators: {len(rho_matrices)}")
    print("  QH registration residuals:")
    for key in (
        "pairwise_commutator",
        "idempotence",
        "hermiticity",
        "orthogonality",
        "completeness",
        "joint_invariance",
        "block_diagonality",
    ):
        print(f"    {key}: {registration[key]:.3e}")
    print("  clustering tolerance census:")
    for tolerance, dimensions in registration["tolerance_census"].items():
        print(f"    tol={tolerance:.0e}: n=9 dims={dimensions}")
    print(f"  max projector cross-block norm: {projector_cross_block:.3e}")

    residual_keys = (
        "pairwise_commutator",
        "idempotence",
        "hermiticity",
        "orthogonality",
        "completeness",
        "joint_invariance",
        "block_diagonality",
    )
    if max(registration[key] for key in residual_keys) >= TOL_COMPOSITION:
        raise AssertionError(f"QH registration residual exceeded {TOL_COMPOSITION}")
    if any(
        dimensions != EXPECTED_DIMS
        for dimensions in registration["tolerance_census"].values()
    ):
        raise AssertionError("QH nine-sector census is not tolerance-stable")

    witnesses = []
    for i, j, k in sorted(canonical):
        result = max_two_step_composition(rho_matrices, bases, i, k, j)
        if result["left_max"] <= TOL_EDGE or result["right_max"] <= TOL_EDGE:
            raise AssertionError(f"missing support edge for S{i + 1}--S{j + 1} via S{k + 1}")
        if result["composition_max"] >= TOL_COMPOSITION:
            raise AssertionError(
                f"composition unexpectedly active for S{i + 1}--S{j + 1} "
                f"via S{k + 1}: {result['composition_max']:.3e}"
            )
        witnesses.append(
            {
                "endpoint_a": i + 1,
                "endpoint_b": j + 1,
                "intermediate": k + 1,
                "max_left_edge_norm": result["left_max"],
                "max_right_edge_norm": result["right_max"],
                "max_ordered_product_norm": result["composition_max"],
                "ordered_product_argmax": list(result["composition_argmax"]),
            }
        )
        print(
            f"  S{i + 1}--S{j + 1} via S{k + 1}: "
            f"edge_maxima=({result['left_max']:.6f}, "
            f"{result['right_max']:.6f}) "
            f"product={result['composition_max']:.3e}"
        )

    if projector_cross_block >= TOL_COMPOSITION:
        raise AssertionError(
            f"sector projectors do not respect physical blocks: {projector_cross_block:.3e}"
        )

    print("AUDIT PASSED: five support paths, five image--kernel obstructions")
    return {
        "summary": {
            "passed": True,
            "sector_count": len(projectors),
            "generator_count": len(rho_matrices),
            "direct_edge_count": len(direct_edges),
            "graph_only_witness_count": len(witnesses),
        },
        "sector_dimensions": [int(basis.shape[1]) for basis in bases],
        "sector_physical_block_support": [sorted(blocks) for blocks in block_sets],
        "registration_residuals": {
            key: float(registration[key]) for key in residual_keys
        },
        "clustering_tolerance_census": {
            f"{tolerance:.0e}": dimensions
            for tolerance, dimensions in registration["tolerance_census"].items()
        },
        "direct_support": {
            "maximum_asymmetry": float(np.max(np.abs(K - K.T))),
            "edges": [[i + 1, j + 1] for i, j in direct_edges],
            "matrix": K.tolist(),
        },
        "generator_index_base": 0,
        "graph_only_obstruction_witnesses": witnesses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result",
        type=Path,
        default=RESULT_PATH,
        help="observation artifact path relative to the repository root",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check-result",
        action="store_true",
        help="check the cached observation and declared source hashes without rerunning",
    )
    mode.add_argument(
        "--no-write-result",
        action="store_true",
        help="run the full audit without updating the cached observation",
    )
    args = parser.parse_args()

    result_path = args.result if args.result.is_absolute() else ROOT / args.result
    if args.check_result:
        check = check_experiment_observation(result_path, root=ROOT)
        print(format_observation_check(args.result, check))
        return 0 if check.reusable else 1

    started_at = utc_now()
    start = perf_counter()
    observations = run_audit()
    elapsed = perf_counter() - start
    print(f"  elapsed: {elapsed:.3f}s")

    if not args.no_write_result:
        write_experiment_observation(
            result_path,
            root=ROOT,
            experiment_id="paper3-composition-obstruction",
            paper="Paper III",
            command=[
                "python",
                "experiments/paper3/validation/composition_obstruction.py",
            ],
            sources=DECLARED_SOURCES,
            parameters={
                "direct_edge_threshold": TOL_EDGE,
                "composition_zero_threshold": TOL_COMPOSITION,
                "physical_block_support_fraction_threshold": BLOCK_SUPPORT_THRESHOLD,
                "clustering_tolerances": list(CLUSTER_TOLERANCES),
                "generator_count": 18,
                "dtype": "complex128",
            },
            observations=observations,
            claim_status="computational_certificate",
            claim_scope=(
                "Canonical 228-dimensional Rubik realization: QH registration, "
                "ten-edge support graph, and five graph-only ordered-product audits."
            ),
            limitations=[
                "Machine-zero residuals are numerical observations, not exact vanishing proofs.",
                "Exact vanishing additionally uses the manuscript's block-preserving construction.",
                "Only explicitly declared source files participate in stale detection.",
            ],
            started_at_utc=started_at,
            elapsed_seconds=elapsed,
            distributions=("numpy", "scipy", "rime"),
        )
        print(f"WROTE OBSERVATION: {args.result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
