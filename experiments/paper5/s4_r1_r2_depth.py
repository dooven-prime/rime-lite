"""Paper V support script: S4 R1/R2/depth example.

Status: representation-derived computational example.

This script constructs the S4-3gen-B regular-representation system used in
Paper V and records the three layers:

    R1: generator support Q_i X_g Q_j != 0
    R2: commutator survival Q_i [X_g, X_h] Q_j != 0
    D: first Lie-depth matrix

The example is intentionally modest: it records that R1 and R2 are distinct
finite data layers and provides a regression guard for the S4
signature. It does not prove the global (R1,R2)->D theorem program.
"""

from __future__ import annotations

import numpy as np

from rime.accessibility import accessibility_signature
from rime.rep_utils import build_system_from_perms, symmetric_group


np.random.seed(42)
TOL = 1e-8

GEN_PERMS = {
    "a": (1, 0, 2, 3),  # (12)
    "b": (2, 0, 1, 3),  # (134)
    "c": (1, 2, 3, 0),  # (1234)
}


def _depth_label(value: int) -> str:
    if value == 999:
        return "F"
    return str(int(value))


def main() -> None:
    gen_names = list(GEN_PERMS)
    gen_perms = list(GEN_PERMS.values())

    system = build_system_from_perms(symmetric_group(4), gen_perms)
    Vs, Xs = system["Vs"], system["Xs"]
    n_sec, dims = system["n_sec"], system["dims"]

    result = accessibility_signature(Vs, Xs, max_depth=4, tol=TOL)
    R1 = result["R1"]
    R2 = result["R2"]
    R2_pairs = result["R2_pairs"]
    D = result["D"]
    sig = result["sig"]

    print("=" * 72)
    print("Paper V: S4-3gen-B R1/R2/Depth Example")
    print("=" * 72)
    print("System: S4 regular representation, generators a=(12), b=(134), c=(1234)")
    print(f"Sectors: {n_sec}")
    print(f"Sector dimensions: {dims}")
    print(f"Accessibility signature (A0,A1,A2,Ainf): {sig}")
    print()

    print("R1 generator support counts:")
    for g_idx, name in enumerate(gen_names):
        print(f"  {name}: {int(R1[g_idx].sum())}")
    print(f"  total: {int(R1.sum())}")
    print()

    print("R2 projected commutator survival counts:")
    for idx, (g, h) in enumerate(R2_pairs):
        print(f"  [{gen_names[g]},{gen_names[h]}]: {int(R2[idx].sum())}")
    print(f"  total: {int(R2.sum())}")
    print()

    print("Depth matrix D (0=direct, 1=commutator, 2=nested, F=frozen):")
    header = "      " + " ".join(f"S{j:02d}" for j in range(n_sec))
    print(header)
    for i in range(n_sec):
        row = " ".join(f"{_depth_label(D[i, j]):>3}" for j in range(n_sec))
        print(f"  S{i:02d} {row}")
    print()

    depth_counts = {
        "direct": int(np.sum(D == 0)) - n_sec,
        "commutator": int(np.sum(D == 1)),
        "nested": int(np.sum(D == 2)),
        "frozen": int(np.sum(D == 999)),
    }
    print("Depth counts excluding the diagonal:")
    for key, value in depth_counts.items():
        print(f"  {key}: {value}")

    assert n_sec == 10, f"expected 10 sectors, got {n_sec}"
    assert sig == (10, 2, 2, 76), f"expected signature (10,2,2,76), got {sig}"
    print("\n[snapshot OK: n_sec=10, sig=(10,2,2,76)]")


if __name__ == "__main__":
    main()
