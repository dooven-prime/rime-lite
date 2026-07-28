"""Paper V support script: path-commutator cancellation in S4-3gen-B.

Status: representation-derived computational counterexample to binary support.

The binary R1 graph records whether generator blocks Q_i X_g Q_j are nonzero.
For a pair of generators (g,h), a length-2 R1 witness means that at least one
intermediate sector k supports a path

    Q_i X_g Q_k X_h Q_j

or the reversed color ordering. This is only a support-level candidate. The
projected commutator is the signed difference of the two orderings, and it can
vanish even when both products are nonzero.

In the S4-3gen-B system, two ordered sector pairs have exactly this behavior:
R1 predicts a depth-1 commutator candidate, the projected commutator cancels,
and the first nonzero Lie block appears at depth 2.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import numpy as np

from rime.accessibility import compute_lie_accessibility_audit
from rime.rep_utils import build_system_from_perms, symmetric_group


np.random.seed(42)
TOL = 1e-8

GEN_NAMES = ["a", "b", "c"]
GEN_PERMS = [
    (1, 0, 2, 3),  # a = (12)
    (2, 0, 1, 3),  # b = (134)
    (1, 2, 3, 0),  # c = (1234)
]


def _block_norm(Vs: list[np.ndarray], X: np.ndarray, i: int, j: int) -> float:
    return float(np.linalg.norm(Vs[i].conj().T @ X @ Vs[j], "fro"))


def _length2_witnesses(R1: np.ndarray, pairs: list[tuple[int, int]], i: int, j: int) -> list[tuple[int, int, int]]:
    """Return (g,h,k) witnesses for a length-2 R1 commutator candidate."""
    witnesses: list[tuple[int, int, int]] = []
    n_sec = R1.shape[1]
    for g, h in pairs:
        for k in range(n_sec):
            if (R1[g, i, k] and R1[h, k, j]) or (R1[h, i, k] and R1[g, k, j]):
                witnesses.append((g, h, k))
    return witnesses


def main() -> None:
    system = build_system_from_perms(symmetric_group(4), GEN_PERMS)
    Vs, Xs = system["Vs"], system["Xs"]
    result = compute_lie_accessibility_audit(Vs, Xs, max_depth=4, tol=TOL)
    R1 = result["R1_Lie"]
    R2 = result["R2_Lie"]
    pairs = result["R2_pairs"]
    D = result["D_Lie_cutoff"]
    census = result["lie_depth_census"]
    signature = tuple(
        census["by_depth"].get(depth, 0) for depth in range(3)
    ) + (census["unreached"],)

    direct = []
    r2_surviving = []
    gaps = []
    no_candidate = []

    for i in range(len(Vs)):
        for j in range(len(Vs)):
            if i == j:
                continue
            witnesses = _length2_witnesses(R1, pairs, i, j)
            if np.any(R1[:, i, j]):
                direct.append((i, j))
            elif witnesses and np.any(R2[:, i, j]):
                r2_surviving.append((i, j))
            elif witnesses:
                gaps.append((i, j))
            else:
                no_candidate.append((i, j))

    print("=" * 72)
    print("Paper V: Path-Commutator Cancellation in S4-3gen-B")
    print("=" * 72)
    print(f"Sectors: {len(Vs)}")
    print(f"Cutoff census (A0,A1,A2,Aunreached): {signature}")
    print()
    print("R1 length-2 classification of ordered off-diagonal pairs:")
    print(f"  direct R1 edges: {len(direct)}")
    print(f"  R2-surviving candidates: {len(r2_surviving)}")
    print(f"  cancellation gaps: {len(gaps)}")
    print(f"  no length-2 candidate: {len(no_candidate)}")
    print()

    print("Cancellation gap details:")
    for i, j in gaps:
        witnesses = _length2_witnesses(R1, pairs, i, j)
        print(f"  S{j}->S{i}: D={int(D[i, j])}, witnesses={witnesses}")
        for g, h, k in witnesses:
            term_gh = Vs[i].conj().T @ Xs[g] @ Vs[k] @ Vs[k].conj().T @ Xs[h] @ Vs[j]
            term_hg = Vs[i].conj().T @ Xs[h] @ Vs[k] @ Vs[k].conj().T @ Xs[g] @ Vs[j]
            comm = Xs[g] @ Xs[h] - Xs[h] @ Xs[g]
            comm_norm = _block_norm(Vs, comm, i, j)
            diff_norm = float(np.linalg.norm(term_gh - term_hg, "fro"))
            print(
                f"    [{GEN_NAMES[g]},{GEN_NAMES[h]}] via S{k}: "
                f"|gh|={np.linalg.norm(term_gh, 'fro'):.6g}, "
                f"|hg|={np.linalg.norm(term_hg, 'fro'):.6g}, "
                f"|gh-hg|={diff_norm:.3e}, |comm|={comm_norm:.3e}"
            )
            assert comm_norm < TOL
            assert diff_norm < TOL
            assert np.linalg.norm(term_gh, "fro") > TOL
            assert np.linalg.norm(term_hg, "fro") > TOL
    print()

    print("R2-surviving candidate details:")
    for i, j in r2_surviving:
        active = [pairs[idx] for idx in range(R2.shape[0]) if R2[idx, i, j]]
        print(f"  S{j}->S{i}: D={int(D[i, j])}, active commutators={active}")
        assert int(D[i, j]) == 1

    assert len(Vs) == 10
    assert signature == (10, 2, 2, 76)
    assert len(direct) == 10
    assert sorted(r2_surviving) == [(5, 6), (6, 5)]
    assert sorted(gaps) == [(3, 4), (4, 3)]
    assert len(no_candidate) == 76
    print("\n[snapshot OK: two R1 candidates cancel at R2 and first appear at depth 2]")


if __name__ == "__main__":
    main()
