"""Commutant gap verification.

Level-1 (mathematical invariants — must never break):
  Δ_comm = dim(Comm(A)) − dim(Comm(ρ)) ≥ 0
  Per-layer 0 ≤ comm_dim ≤ d²

Level-2 (canonical snapshot — regression detection):
  Frozen at post-ρ-fix revision r2. Update when representation changes.

See docs/paper_data.md §8.3.
"""
import numpy as np
from rime.cubieoperator import CubieSpectralOperator

# Post-ρ-fix canonical snapshot (revision r2).
# Update these when the representation definition changes.
CANONICAL = {
    "comm_A": 804,
    "comm_rho": 610,
    "delta": 194,
}

# Shared operator — expensive to construct, reuse across all tests.
_op: CubieSpectralOperator | None = None


def _get_op() -> CubieSpectralOperator:
    global _op
    if _op is None:
        _op = CubieSpectralOperator()
    return _op


def test_commutant_gap_invariant():
    """Level-1: Δ_comm = dim(Comm(A)) − dim(Comm(ρ)) ≥ 0."""
    op = _get_op()

    ca = op.commutant_algebra()
    dim_comm_A = ca['dim_total']
    full_basis, dim_comm_rho = op.full_commutant_combinatorial()

    assert dim_comm_A > 0
    assert dim_comm_rho > 0
    assert dim_comm_A >= dim_comm_rho  # projected commutant ≥ true commutant
    delta = dim_comm_A - dim_comm_rho
    assert delta >= 0

    print(f"test_commutant_gap_invariant: OK  "
          f"(Comm(A)={dim_comm_A}, Comm(ρ)={dim_comm_rho}, Δ={delta})")


def test_commutant_per_layer_invariant():
    """Level-1: each layer's commutant satisfies 0 ≤ comm_dim ≤ d²."""
    op = _get_op()
    ca = op.commutant_algebra()
    layers = op.layer_keys

    for lam in layers:
        b = ca['blocks'][lam]
        d = b['dim']
        c = b['commutant_dim']
        assert 0 <= c <= d * d, f"λ={lam:.6f}: comm={c} not in [0, {d*d}]"

    print(f"test_commutant_per_layer_invariant: OK  ({len(layers)} layers)")


def test_commutant_gap_snapshot():
    """Level-2: canonical snapshot regression check."""
    op = _get_op()

    ca = op.commutant_algebra()
    dim_comm_A = ca['dim_total']
    full_basis, dim_comm_rho = op.full_commutant_combinatorial()
    delta = dim_comm_A - dim_comm_rho

    assert dim_comm_A == CANONICAL["comm_A"], \
        f"dim(Comm(A)) = {dim_comm_A}, canonical = {CANONICAL['comm_A']}"
    assert dim_comm_rho == CANONICAL["comm_rho"], \
        f"dim(Comm(ρ)) = {dim_comm_rho}, canonical = {CANONICAL['comm_rho']}"
    assert delta == CANONICAL["delta"], \
        f"Δ_comm = {delta}, canonical = {CANONICAL['delta']}"

    print(f"test_commutant_gap_snapshot: OK  "
          f"(matches post-ρ-fix r2)")


def test_transport_commutant_relation():
    """Level-1: transport-commutant relation invariants.

    Transport sums are not frozen — they depend on projector normalization,
    generator weighting, and basis conventions. Assert only invariants.
    """
    op = _get_op()
    tol = 1e-6

    ca = op.commutant_algebra()
    dim_comm_A = ca['dim_total']
    full_basis, dim_comm_rho = op.full_commutant_combinatorial()
    delta = dim_comm_A - dim_comm_rho

    # Layer-level transport sum
    T = op.transport_tensor()
    layers = op.layer_keys
    n = len(layers)
    T_sum_sq = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            tij = max(T[(layers[i], layers[j])]['max'],
                      T[(layers[j], layers[i])]['max'])
            T_sum_sq += tij ** 2
    transport_2sum = 2 * T_sum_sq

    # Sector-level transport sum
    secs = op.center_decomposition()
    n_sec = secs['n_sectors']
    K_sec = np.zeros((n_sec, n_sec))
    for a in range(n_sec):
        Pa = secs['projectors'][a]
        for b_val in range(n_sec):
            Pb = secs['projectors'][b_val]
            norms = [float(np.linalg.norm(Pa @ rho @ Pb, 'fro'))
                     for rho in op.rho_matrices()]
            K_sec[a, b_val] = max(norms)

    T_sum_sq_sec = 0.0
    for a in range(n_sec):
        for b_val in range(a + 1, n_sec):
            T_sum_sq_sec += max(K_sec[a, b_val], K_sec[b_val, a]) ** 2
    transport_2sum_sec = 2 * T_sum_sq_sec

    # Level-1 invariants
    assert transport_2sum > 0, "transport sum must be positive"
    assert np.isfinite(transport_2sum)
    assert transport_2sum_sec > 0, "sector transport sum must be positive"
    assert transport_2sum_sec >= transport_2sum, \
        "sector resolution captures ≥ layer resolution transport"

    # Δ_comm and transport are both positive (no equality asserted)
    assert delta > 0


    print(f"test_transport_commutant_relation: OK")
    print(f"  Δ_comm                    = {delta}")
    print(f"  2 Σ ‖T‖² (layer)         = {transport_2sum:.2f}")
    print(f"  2 Σ ‖T‖² (sector)        = {transport_2sum_sec:.2f}")


if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
