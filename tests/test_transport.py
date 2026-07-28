"""Regression checks for direct support and projected matrix composition.

Paper II owns the direct transport graph. Paper III distinguishes two-step
support paths from nonzero projected composition operators.
"""

from collections import Counter
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rime.cubie import BLOCK_RANGES, CubieMove
from rime.cubieoperator import CubieSpectralOperator
from rime.spectral_utils import (
    find_graph_only_two_step_pairs,
    max_two_step_composition,
    sector_bases_from_projectors,
    select_canonical_intermediate,
)


TOL = 1e-10
TOL_K = 0.05
EXPECTED = {
    (1, 3, 5),  # S2--S4 via S6
    (2, 8, 6),  # S3--S9 via S7
    (3, 4, 5),  # S4--S5 via S6
    (3, 7, 8),  # S4--S8 via S9
    (5, 8, 6),  # S6--S9 via S7
}


def check(condition, message):
    assert condition, message


def direct_support_matrix(rho_matrices, bases):
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


op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
sectors = op.center_decomposition()
projectors = sectors["projectors"]
bases = sector_bases_from_projectors(projectors)
rho_matrices = list(op.rho_matrices())
K = direct_support_matrix(rho_matrices, bases)
block_sets = op.sector_block_support(projectors)

print("Test 1: direct support symmetry ...")
asymmetry = np.max(np.abs(K - K.T))
check(asymmetry < TOL, f"K asymmetry too large: {asymmetry:.2e}")
print(f"  OK: max |K-K^T| = {asymmetry:.2e}")

print("Test 2: canonical direct graph ...")
edges = [(i, j) for i in range(len(projectors))
         for j in range(i + 1, len(projectors)) if K[i, j] > TOL_K]
check(len(edges) == 10, f"expected 10 direct edges, got {len(edges)}")
s6_degree = int(np.sum(K[5, :] > TOL_K)) - 1
s1_degree = int(np.sum(K[0, 1:] > TOL_K))
check(s6_degree == 5, f"expected S6 degree 5, got {s6_degree}")
check(s1_degree == 0, f"expected isolated S1, got degree {s1_degree}")
print("  OK: 10 edges, S6 degree 5, S1 isolated")

print("Test 3: graph-only two-step pairs ...")
graph_pairs = find_graph_only_two_step_pairs(K, block_sets, TOL_K)
canonical = {
    (i, j, select_canonical_intermediate(candidates, K, TOL_K))
    for i, j, candidates in graph_pairs
}
check(canonical == EXPECTED, f"unexpected graph-only triples: {sorted(canonical)}")
hub_counts = Counter(k + 1 for _, _, k in canonical)
check(hub_counts == Counter({6: 2, 7: 2, 9: 1}),
      f"unexpected intermediates: {dict(hub_counts)}")
print("  OK: five support paths with canonical intermediates S6/S7/S9")

print("Test 4: projected composition obstruction ...")
for i, j, k in sorted(canonical):
    result = max_two_step_composition(rho_matrices, bases, i, k, j)
    check(result["left_max"] > TOL_K and result["right_max"] > TOL_K,
          f"missing support factor for S{i + 1}--S{j + 1} via S{k + 1}")
    check(result["composition_max"] < TOL,
          f"composition active for S{i + 1}--S{j + 1} via S{k + 1}: "
          f"{result['composition_max']:.3e}")
    print(
        f"  S{i + 1}--S{j + 1} via S{k + 1}: "
        f"factors=({result['left_max']:.6f}, {result['right_max']:.6f}), "
        f"product={result['composition_max']:.3e}"
    )

print("Test 5: QH projectors respect physical blocks ...")
maximum_cross_block = 0.0
ranges = list(BLOCK_RANGES.values())
for projector in projectors:
    for a, (start_a, end_a) in enumerate(ranges):
        for b, (start_b, end_b) in enumerate(ranges):
            if a == b:
                continue
            block = projector[start_a:end_a, start_b:end_b]
            maximum_cross_block = max(
                maximum_cross_block,
                np.linalg.norm(block, "fro"),
            )
check(maximum_cross_block < TOL,
      f"QH projector cross-block residual too large: {maximum_cross_block:.3e}")
print(f"  OK: max cross-block projector norm = {maximum_cross_block:.3e}")

print("\nAll transport/composition tests passed.")
