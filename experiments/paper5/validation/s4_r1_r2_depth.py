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

import _bootstrap  # noqa: F401

import numpy as np

from rime.accessibility import (
    assert_accessibility_inputs,
    audit_lie_closure,
    compute_lie_accessibility_audit,
)
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
        return "U"
    return str(int(value))


def _sector_certificate(projs: list[np.ndarray]) -> dict:
    ambient_dim = projs[0].shape[0]
    idempotence = max(np.linalg.norm(Q @ Q - Q, "fro") for Q in projs)
    hermiticity = max(np.linalg.norm(Q - Q.conj().T, "fro") for Q in projs)
    orthogonality = max(
        np.linalg.norm(Qi @ Qj, "fro")
        for i, Qi in enumerate(projs)
        for j, Qj in enumerate(projs)
        if i != j
    )
    completeness = np.linalg.norm(sum(projs) - np.eye(ambient_dim), "fro")
    return {
        "ranks": [int(np.linalg.matrix_rank(Q, tol=TOL)) for Q in projs],
        "maximum_idempotence_residual": float(idempotence),
        "maximum_hermiticity_residual": float(hermiticity),
        "maximum_orthogonality_residual": float(orthogonality),
        "completeness_residual": float(completeness),
    }


def main() -> None:
    gen_names = list(GEN_PERMS)
    gen_perms = list(GEN_PERMS.values())

    system = build_system_from_perms(symmetric_group(4), gen_perms)
    Vs, Xs, projs = system["Vs"], system["Xs"], system["projs"]
    sector_registration = system["sector_registration"]
    n_sec, dims = system["n_sec"], system["dims"]
    sectors = _sector_certificate(projs)

    input_report = assert_accessibility_inputs(
        Vs,
        Xs,
        tol=TOL,
        require_complete=True,
        require_skew_hermitian=True,
    )
    result = compute_lie_accessibility_audit(Vs, Xs, max_depth=4, tol=TOL)
    closure_result = compute_lie_accessibility_audit(
        Vs, Xs, max_depth=6, tol=TOL
    )
    closure = audit_lie_closure(
        Xs, closure_result["cumulative_basis"][-1], tol=TOL
    )
    R1 = result["R1_Lie"]
    R2 = result["R2_Lie"]
    R2_pairs = result["R2_pairs"]
    D = result["D_Lie_cutoff"]
    census = result["lie_depth_census"]
    sig = tuple(census["by_depth"].get(depth, 0) for depth in range(3)) + (
        census["unreached"],
    )

    print("=" * 72)
    print("Paper V: S4-3gen-B R1/R2/Depth Example")
    print("=" * 72)
    print("System: S4 regular representation, generators a=(12), b=(134), c=(1234)")
    print(f"Sectors: {n_sec}")
    print(f"Sector dimensions: {dims}")
    print(
        "Sector construction: ordered compression by class sums followed by "
        "generator-derived Hermitian operators"
    )
    print(f"Compression clustering and rank threshold: {TOL:.0e}")
    print(
        "Registration family maximum commutator norm: "
        f"{sector_registration['maximum_pairwise_commutator_norm']:.6g}"
    )
    print(f"Numerical dtypes: projectors={projs[0].dtype}, generators={Xs[0].dtype}")
    print(f"Projector rank census: {sectors['ranks']}")
    print(
        "Maximum projector residuals: "
        f"idempotence={sectors['maximum_idempotence_residual']:.3e}, "
        f"Hermiticity={sectors['maximum_hermiticity_residual']:.3e}, "
        f"orthogonality={sectors['maximum_orthogonality_residual']:.3e}"
    )
    print(f"Projector completeness residual: {sectors['completeness_residual']:.3e}")
    print(f"Cutoff census (A0,A1,A2,Aunreached): {sig}")
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

    print("Depth matrix D^(3) (0=direct, 1=commutator, 2=nested, U=unreached):")
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
        "unreached_through_depth_3": int(np.sum(D == 999)),
    }
    print("Depth counts excluding the diagonal:")
    for key, value in depth_counts.items():
        print(f"  {key}: {value}")
    print()
    per_depth_dims = [
        len(layer) for layer in closure_result["per_depth_basis"]
    ]
    cumulative_dims = [
        len(layer) for layer in closure_result["cumulative_basis"]
    ]
    print(f"Numerical Lie layer dimensions: {per_depth_dims}")
    print(f"Numerical cumulative dimensions: {cumulative_dims}")
    print(f"Closure span dimension: {closure['dimension']}")
    print(f"Augmented closure-matrix rank: {closure['augmented_rank']}")
    print(f"Closure rank threshold: {closure['rank_threshold']:.0e}")
    print(f"Minimum retained singular value: {closure['minimum_retained_singular_value']:.6g}")
    print(f"Maximum discarded singular value: {closure['maximum_discarded_singular_value']:.3e}")
    print(f"Basis Gram residual: {closure['basis_gram_error']:.3e}")
    print(
        "Maximum [X,L] closure residual: "
        f"{closure['maximum_generator_closure_residual']:.3e}"
    )
    print(f"Sector coverage rank: {input_report['coverage_rank']}")

    assert n_sec == 10, f"expected 10 sectors, got {n_sec}"
    assert sig == (10, 2, 2, 76), f"expected signature (10,2,2,76), got {sig}"
    assert per_depth_dims == [3, 3, 7, 8, 0, 0]
    assert cumulative_dims == [3, 6, 13, 21, 21, 21]
    assert sectors["ranks"] == dims
    assert sectors["maximum_idempotence_residual"] < TOL
    assert sectors["maximum_hermiticity_residual"] < TOL
    assert sectors["maximum_orthogonality_residual"] < TOL
    assert sectors["completeness_residual"] < TOL
    assert projs[0].dtype == np.complex128
    assert Xs[0].dtype == np.complex128
    assert sector_registration["order_dependent"]
    assert not sector_registration["joint_spectral_claim"]
    assert closure["augmented_rank"] == closure["dimension"]
    assert closure["minimum_retained_singular_value"] > TOL
    assert closure["maximum_discarded_singular_value"] < TOL
    assert closure["maximum_generator_closure_residual"] < TOL
    assert closure["basis_gram_error"] < TOL
    assert closure["saturated"]
    print("\n[snapshot OK: cutoff census and numerical Lie-closure certificate]")


if __name__ == "__main__":
    main()
