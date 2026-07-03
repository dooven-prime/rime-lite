"""Paper V support script: matrix nondegeneracy in S4-3gen-B.

Status: representation-derived computational verification.

Support-level single-term bridges become matrix products A B in systems with
sector dimensions greater than one. Nonzero support of A and B does not by
itself imply A B != 0. This script checks the S4-3gen-B example used in Paper V:

    48/48 single-term bridge products are nonzero.
    48/48 satisfy the implemented rank-protection predicate.

This is an example-level verification and a regression guard for
docs/MATRIX_NONDEGENERACY.md, not a universal nondegeneracy theorem.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from rime.accessibility import matrix_nondeg_audit, single_term_bridge_audit
from rime.rep_utils import build_system_from_perms, symmetric_group


np.random.seed(42)
TOL = 1e-8

GEN_PERMS = {
    "a": (1, 0, 2, 3),  # (12)
    "b": (2, 0, 1, 3),  # (134)
    "c": (1, 2, 3, 0),  # (1234)
}


def _perturbation_check(Vs: list[np.ndarray], Xs: list[np.ndarray], bridges: list[dict]) -> int:
    """Return the number of trials where a sampled bridge product becomes zero."""
    zero_trials = 0
    for trial in range(100):
        rng = np.random.default_rng(trial * 7919 + 1)
        Xs_pert = []
        for X in Xs:
            pert = rng.normal(0, 1e-6, X.shape) + 1j * rng.normal(0, 1e-6, X.shape)
            pert = (pert - pert.conj().T) / 2
            Xs_pert.append(X + pert)

        for bridge in bridges[:3]:
            if bridge["orientation"] == "gh":
                left, right = bridge["g"], bridge["h"]
            else:
                left, right = bridge["h"], bridge["g"]
            A = Vs[bridge["i"]].conj().T @ Xs_pert[left] @ Vs[bridge["k"]]
            B = Vs[bridge["k"]].conj().T @ Xs_pert[right] @ Vs[bridge["j"]]
            if np.linalg.norm(A @ B, "fro") <= TOL * 10:
                zero_trials += 1
                break
    return zero_trials


def main() -> None:
    gen_perms = list(GEN_PERMS.values())
    system = build_system_from_perms(symmetric_group(4), gen_perms)
    Vs, Xs = system["Vs"], system["Xs"]
    n_sec, dims = system["n_sec"], system["dims"]

    bridges = matrix_nondeg_audit(single_term_bridge_audit(Vs, Xs, tol=TOL), tol=TOL)
    ab_zero = [bridge for bridge in bridges if bridge["product_zero"]]
    structural = [bridge for bridge in bridges if bridge["structural"]]

    by_dk = defaultdict(lambda: {"count": 0, "zero": 0, "min_rank": 999})
    for bridge in bridges:
        dk = bridge["d_k"]
        by_dk[dk]["count"] += 1
        by_dk[dk]["zero"] += int(bridge["product_zero"])
        by_dk[dk]["min_rank"] = min(
            by_dk[dk]["min_rank"],
            int(np.linalg.matrix_rank(bridge["prod"], tol=TOL)),
        )

    zero_trials = _perturbation_check(Vs, Xs, bridges)

    print("=" * 72)
    print("Paper V: S4-3gen-B Matrix Nondegeneracy")
    print("=" * 72)
    print(f"Sectors: {n_sec}")
    print(f"Sector dimensions: {dims}")
    print(f"Single-term bridges: {len(bridges)}")
    print(f"AB=0 cases: {len(ab_zero)}")
    print(f"Rank-protected bridges: {len(structural)}")
    print(f"Perturbation trials with sampled AB=0: {zero_trials}/100")
    print()

    print("Summary by intermediate dimension d_k:")
    for dk in sorted(by_dk):
        info = by_dk[dk]
        print(
            f"  d_k={dk}: count={info['count']}, "
            f"min product rank={info['min_rank']}, AB=0={info['zero']}"
        )
    print()

    print("First five single-term bridges:")
    for bridge in bridges[:5]:
        if bridge["orientation"] == "gh":
            left, right = bridge["g"], bridge["h"]
        else:
            left, right = bridge["h"], bridge["g"]
        print(
            f"  S{bridge['i']} --[X{left},X{right}]--> S{bridge['j']} via S{bridge['k']}: "
            f"|A|={bridge['a_nrm']:.3g}, |B|={bridge['b_nrm']:.3g}, "
            f"|AB|={bridge['prod_nrm']:.3g}, "
            f"ranks=({bridge['rank_A']},{bridge['rank_B']})"
        )

    assert len(bridges) == 48, f"expected 48 bridges, got {len(bridges)}"
    assert len(ab_zero) == 0, f"expected no AB=0 cases, got {len(ab_zero)}"
    assert len(structural) == 48, f"expected 48 rank-protected bridges, got {len(structural)}"
    assert zero_trials == 0, f"expected no perturbation AB=0 trials, got {zero_trials}"
    print("\n[snapshot OK: 48/48 nonzero and rank-protected]")


if __name__ == "__main__":
    main()
