"""Paper V support script: complement obstruction and support-level R2 repair.

Status: finite support/scalar model.

The model has five one-dimensional sectors. R1 records three independent
generator supports with a complement obstruction pattern. The projected
commutators create single-term bridges between the previously separated
intermediate sectors.

This is a support/scalar witness for Proposition 2: R1 fails structurally and
R2 is the first local repair layer under the centered-model hypotheses. It is
not a universal matrix-block nondegeneracy theorem.
"""

from __future__ import annotations

import numpy as np

from rime.accessibility import (
    compute_R1,
    compute_R2,
    compute_lie_depth_matrix,
    single_term_bridge_audit,
)


np.random.seed(42)
TOL = 1e-8
GENS = ["a", "b", "c"]


def _build_model() -> tuple[list[np.ndarray], list[np.ndarray], dict[str, int], dict[str, set[int]]]:
    n_sec = 5
    u = {"a": 2, "b": 3, "c": 4}
    B = {"a": {3, 4}, "b": {2, 4}, "c": {2, 3}}

    entries = {
        "a": {(0, 2): 2.0, (1, 3): 1.0, (1, 4): 3.0},
        "b": {(0, 3): 1.0, (1, 2): 2.0, (1, 4): 1.0},
        "c": {(0, 4): 3.0, (1, 2): 1.0, (1, 3): 2.0},
    }

    Xs = []
    for name in GENS:
        X = np.zeros((n_sec, n_sec), dtype=complex)
        for (i, j), value in entries[name].items():
            X[i, j] = value
            X[j, i] = value
        Xs.append(X)

    Vs = [np.eye(n_sec)[:, i : i + 1] for i in range(n_sec)]
    return Vs, Xs, u, B


def _fatal_bridge_count(bridges: list[dict], u: dict[str, int], B: dict[str, set[int]]) -> int:
    count = 0
    for bridge in bridges:
        v, w = bridge["i"], bridge["j"]
        for name in GENS:
            if v == u[name] and w in B[name]:
                count += 1
    return count


def main() -> None:
    Vs, Xs, u, B = _build_model()
    n_sec = len(Vs)

    R1 = compute_R1(Vs, Xs, tol=TOL)
    R2, R2_pairs = compute_R2(Vs, Xs, tol=TOL)
    D, _, _ = compute_lie_depth_matrix(Vs, Xs, max_depth=3, tol=TOL)
    bridges = single_term_bridge_audit(Vs, Xs, tol=TOL)
    fatal = _fatal_bridge_count(bridges, u, B)

    print("=" * 72)
    print("Paper V: Complement Obstruction Support Model")
    print("=" * 72)
    print("Sectors: 0=source, 1=sink, 2/3/4=intermediate vertices")
    print(f"Generator anchors u_g: {u}")
    print(f"Complement sink sets B_g: {B}")
    print()

    print("R1 support counts:")
    for idx, name in enumerate(GENS):
        print(f"  {name}: {int(R1[idx].sum())}")
    print(f"  total: {int(R1.sum())}")
    print()

    print("R2 commutator survival counts:")
    for idx, (g, h) in enumerate(R2_pairs):
        print(f"  [{GENS[g]},{GENS[h]}]: {int(R2[idx].sum())}")
    print(f"  total: {int(R2.sum())}")
    print()

    print("Single-term bridge sample:")
    for bridge in bridges[:8]:
        first, second = (
            (bridge["g"], bridge["h"])
            if bridge["orientation"] == "gh"
            else (bridge["h"], bridge["g"])
        )
        print(
            f"  S{bridge['i']} --[{GENS[first]},{GENS[second]}]--> S{bridge['j']} "
            f"via S{bridge['k']}: |AB|={bridge['prod_nrm']:.3g}"
        )
    print(f"Single-term bridges: {len(bridges)}")
    print(f"Fatal bridge impacts on complement diagonals: {fatal}")
    print()

    print("Depth matrix D:")
    for i in range(n_sec):
        labels = []
        for j in range(n_sec):
            value = D[i, j]
            labels.append("F" if value == 999 else str(int(value)))
        print(f"  S{i}: {' '.join(f'{x:>2}' for x in labels)}")

    assert n_sec == 5, f"expected 5 sectors, got {n_sec}"
    assert int(R1.sum()) == 18, f"expected 18 R1 bits, got {R1.sum()}"
    assert int(R2.sum()) > 0, "expected R2 to create at least one bridge"
    assert fatal > 0, "expected at least one fatal complement-bridge impact"
    print("\n[snapshot OK: complement model has R1 obstruction and support-level R2 repair]")


if __name__ == "__main__":
    main()
