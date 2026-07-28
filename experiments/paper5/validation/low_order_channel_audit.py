"""Paper V support script: separate R1, products, R2, and cutoff depth.

Status: representation-derived computational case study.

The audit starts from ordered off-diagonal target pairs with aggregate R1=0.
It then separates bracket-emergent channels, product-supported cancellation
channels, image-kernel incidence candidates, and pairs with no tested two-step
product. Product support is computed independently from commutator support.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import numpy as np

from rime.accessibility import compute_R1, compute_R2
from rime.rep_utils import build_system_from_perms, symmetric_group


TOL = 1e-8
GEN_PERMS = [
    (1, 0, 2, 3),
    (2, 0, 1, 3),
    (1, 2, 3, 0),
]


def _block(Vs: list[np.ndarray], X: np.ndarray, i: int, j: int) -> np.ndarray:
    return Vs[i].conj().T @ X @ Vs[j]


def main() -> None:
    system = build_system_from_perms(symmetric_group(4), GEN_PERMS)
    Vs, Xs = system["Vs"], system["Xs"]
    n_sec = len(Vs)

    R1_tensor = compute_R1(Vs, Xs, tol=TOL)
    R2_tensor, _ = compute_R2(Vs, Xs, tol=TOL)
    R1 = np.any(R1_tensor, axis=0)
    R2 = np.any(R2_tensor, axis=0)
    C2 = np.zeros((n_sec, n_sec), dtype=bool)
    W2 = np.zeros((n_sec, n_sec), dtype=bool)
    incidence_records = []

    for i in range(n_sec):
        for j in range(n_sec):
            if i == j:
                continue
            for g, Xg in enumerate(Xs):
                for h, Xh in enumerate(Xs):
                    word = _block(Vs, Xg @ Xh, i, j)
                    W2[i, j] |= np.linalg.norm(word, "fro") > TOL
                    for k in range(n_sec):
                        A = _block(Vs, Xg, i, k)
                        B = _block(Vs, Xh, k, j)
                        product = A @ B
                        a_nonzero = np.linalg.norm(A, "fro") > TOL
                        b_nonzero = np.linalg.norm(B, "fro") > TOL
                        product_nonzero = np.linalg.norm(product, "fro") > TOL
                        C2[i, j] |= product_nonzero
                        if (
                            not R1[i, j]
                            and a_nonzero
                            and b_nonzero
                            and not product_nonzero
                        ):
                            incidence_records.append((j, i, g, h, k))

    offdiag = ~np.eye(n_sec, dtype=bool)
    r1_zero = offdiag & ~R1
    bracket_emergent = r1_zero & R2
    routed_only = r1_zero & ~R2 & C2 & ~W2
    word_supported = r1_zero & ~R2 & W2
    product_supported = routed_only | word_supported
    unresolved = r1_zero & ~R2 & ~C2 & ~W2

    print("=" * 72)
    print("Paper V: S4 Low-Order Channel Separation")
    print("=" * 72)
    print(f"support threshold: {TOL:.0e}")
    print(f"ordered off-diagonal pairs: {int(np.sum(offdiag))}")
    print(f"direct R1 pairs: {int(np.sum(offdiag & R1))}")
    print(f"R1-zero pairs: {int(np.sum(r1_zero))}")
    print(f"  bracket-emergent R2 pairs: {int(np.sum(bracket_emergent))}")
    print(f"  routed-product C2^X-supported, R2-zero pairs: {int(np.sum(r1_zero & ~R2 & C2))}")
    print(f"    full-word W2^X-supported pairs: {int(np.sum(word_supported))}")
    print(f"    C2^X=1, W2^X=0 pairs: {int(np.sum(routed_only))}")
    print(f"  unresolved pairs: {int(np.sum(unresolved))}")
    print(f"  image-kernel incidence records: {len(incidence_records)}")
    print()

    print("Bracket-emergent channels (source -> target):")
    for i, j in zip(*np.where(bracket_emergent)):
        print(f"  S{j} -> S{i}")
    print("Product-supported cancellation channels (source -> target):")
    for i, j in zip(*np.where(product_supported)):
        print(
            f"  S{j} -> S{i}: C2^X={int(C2[i, j])}, "
            f"W2^X={int(W2[i, j])}, R2^Lie={int(R2[i, j])}"
        )

    assert int(np.sum(offdiag & R1)) == 10
    assert int(np.sum(r1_zero)) == 80
    assert int(np.sum(bracket_emergent)) == 2
    assert np.all(~W2 | C2), "full-word support must imply routed-term support"
    assert int(np.sum(r1_zero & ~R2 & C2)) == 2
    assert int(np.sum(word_supported)) == 2
    assert int(np.sum(routed_only)) == 0
    assert int(np.sum(product_supported)) == 2
    assert int(np.sum(unresolved)) == 76
    assert not incidence_records
    assert sorted(zip(*np.where(bracket_emergent))) == [(5, 6), (6, 5)]
    assert sorted(zip(*np.where(product_supported))) == [(3, 4), (4, 3)]
    print("\n[snapshot OK: R1, products, and R2 are separately classified]")


if __name__ == "__main__":
    main()
