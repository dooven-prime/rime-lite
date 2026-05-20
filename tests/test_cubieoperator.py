"""Theorem verification — CubieSpectralOperator: the canonical spectral engine.

CubieSpectralOperator is the SINGLE source of truth for spectral decomposition.
SpectralStructure is only a theorem façade — it predicts/explains/names what CSO
computes numerically. All spectral claims MUST be verified against CSO output.

These tests require CubieSpectralOperator (~2-3 min total). Slow test suite.

Invariant levels:
  Level 1 — Spectral theorem:  eigenvalues, projectors, orthogonality, minimal
                                polynomial, trace consistency
  Level 2 — Bose-Mesner:       polynomial closure, adjacency algebra dimension,
                                k-set reconstruction (numerical confirmation)
  Level 3 — Dynamical prep:    slow-fast splitting, generator symmetry
"""

import numpy as np
from rime.cubie import CubieMove,TOTAL_DIM
from rime.cubieoperator import CubieSpectralOperator

TOL = 1e-10

# ═══════════════════════════════════════════════════════════════════════════
# Level 1 — Spectral theorem invariants
# ═══════════════════════════════════════════════════════════════════════════

def test_minimal_polynomial():
    """‖p(A)‖ = 0 where p(x) = ∏_{λ∈Spec(A)} (x − λ).

    The degree-6 polynomial annihilates A — this is the fundamental
    closure property: the spectral decomposition is algebraically complete.
    """
    op = CubieSpectralOperator()
    A = op.A
    # Build p(x) = ∏ (x − λ_i)
    p_A = np.eye(TOTAL_DIM, dtype=complex)
    for lam in op.layer_keys:
        p_A = p_A @ (A - lam * np.eye(TOTAL_DIM))
    residual = float(np.linalg.norm(p_A, 'fro'))

    assert residual < 1e-6, f'‖p(A)‖ = {residual:.2e}, expected < 1e-6'
    print(f'test_minimal_polynomial: OK  (‖p(A)‖ = {residual:.1e})')


def test_multiplicity_consistency():
    """Σ dim(V_λ) = 228 and trace(A) = Σ λ·dim(V_λ).

    Character-level consistency — fundamental identity of spectral decomposition.
    """
    op = CubieSpectralOperator()

    # Sum of dimensions
    total_dim = sum(op.layer_dimension(lam) for lam in op.layer_keys)
    assert total_dim == 228, f'Σ dim = {total_dim}, expected 228'

    # Trace identity: Tr(A) = Σ λ_i · dim_i
    trace_A = float(np.trace(op.A).real)
    trace_sum = sum(
        lam * op.layer_dimension(lam) for lam in op.layer_keys
    )
    assert abs(trace_A - trace_sum) < 1e-3, \
        f'Tr(A) = {trace_A:.6f}, Σ λ·dim = {trace_sum:.6f}'

    print(f'test_multiplicity_consistency: OK  (Σ dim=228, Tr(A)={trace_A:.6f})')


def test_spectral_projector_theorem():
    """P_i P_j = δ_ij P_i, Σ P_i = I, A = Σ λ_i P_i.

    This is the full spectral theorem — stronger than eigenvalue count alone.
    """
    op = CubieSpectralOperator()
    layers = op.layer_keys
    n = len(layers)

    # Idempotence: P_i² = P_i
    for lam in layers:
        P = op.layer_projector(lam)
        assert np.allclose(P @ P, P, atol=1e-10), \
            f'P_{lam:.6f} not idempotent'

    # Orthogonality: P_i P_j = 0 for i ≠ j
    for i in range(n):
        Pi = op.layer_projector(layers[i])
        for j in range(i + 1, n):
            Pj = op.layer_projector(layers[j])
            prod = float(np.linalg.norm(Pi @ Pj, 'fro'))
            assert prod < 1e-10, \
                f'P_{layers[i]:.6f}·P_{layers[j]:.6f} = {prod:.1e}, expected 0'

    # Completeness: Σ P_i = I
    P_sum = sum(op.layer_projector(lam) for lam in layers)
    assert np.allclose(P_sum, np.eye(TOTAL_DIM), atol=5e-10), \
        f'‖Σ P_i − I‖ = {np.linalg.norm(P_sum - np.eye(TOTAL_DIM)):.1e}'

    # Spectral reconstruction: A = Σ λ_i P_i
    A_recon = sum(lam * op.layer_projector(lam) for lam in layers)
    assert np.allclose(A_recon, op.A, atol=1e-3), \
        f'‖A − Σ λ_i P_i‖ = {np.linalg.norm(A_recon - op.A):.1e}'

    print(f'test_spectral_projector_theorem: OK  ({n} layers)')


# ═══════════════════════════════════════════════════════════════════════════
# Level 2 — Bose-Mesner / algebraic structure
# ═══════════════════════════════════════════════════════════════════════════

def test_bose_mesner_dimension():
    """dim span{I, A, A², …, A^(d−1)} = 6 where d = |Spec(A)|.

    The adjacency algebra closes at degree equal to the number of distinct
    eigenvalues — the defining property of a Bose-Mesner / association scheme.
    """
    op = CubieSpectralOperator()
    A = op.A
    n_eigs = len(op.layer_keys)

    # Build Krylov sequence {I, A, A², …, A^(n_eigs)}
    powers = [np.eye(TOTAL_DIM, dtype=complex)]
    Ak = np.eye(TOTAL_DIM, dtype=complex)
    for _k in range(1, n_eigs + 1):
        Ak = Ak @ A
        powers.append(Ak.copy())

    # Stack as vectors and compute rank
    stacked = np.array([p.ravel() for p in powers])  # (n_eigs+1, 228²)
    _, s, _ = np.linalg.svd(stacked, full_matrices=False)
    rank = int(np.sum(s > 1e-8))

    assert rank == 6, \
        f'dim span{{I,A,…,A^{n_eigs}}} = {rank}, expected {n_eigs}'
    print(f'test_bose_mesner_dimension: OK  (rank = {rank})')


def test_rational_projector_reconstruction():
    """P_i = ∏_{j≠i} (A − λ_j I) / (λ_i − λ_j) matches eigenspace projector.

    The Lagrange interpolation formula reconstructs spectral projectors as
    rational polynomials in A — proving projectors lie in ℚ[A], not just ℂ.
    """
    op = CubieSpectralOperator()
    A = op.A
    layers = op.layer_keys

    for i, lam_i in enumerate(layers):
        Pi_numerical = op.layer_projector(lam_i)

        # Lagrange: P_i = ∏_{j≠i} (A − λ_j) / (λ_i − λ_j)
        Pi_lagrange = np.eye(TOTAL_DIM, dtype=complex)
        for j, lam_j in enumerate(layers):
            if i != j:
                Pi_lagrange = Pi_lagrange @ (
                    (A - lam_j * np.eye(TOTAL_DIM)) / (lam_i - lam_j)
                )

        error = float(np.linalg.norm(Pi_lagrange - Pi_numerical, 'fro'))
        assert error < 1e-3, \
            f'P_{lam_i:.6f}: ‖Lagrange − eigenspace‖ = {error:.1e}'

    print(f'test_rational_projector_reconstruction: OK  ({len(layers)} layers)')


def test_k_set_reconstruction():
    """λ_predicted = 1 − k/9 matches numerical Spec(A) exactly.

    Not just "k=5 absent" but: the full k-set reconstruction succeeds.
    Both eigenvalues AND multiplicities must match.
    """
    from rime.spectralstructure import SpectralStructure
    ss = SpectralStructure(CubieMove.prim_moves)
    m = ss.m  # denominator: λ_k = 1 − k/m
    op = CubieSpectralOperator()

    # Predicted: λ_k = 1 − k/m for k ∈ k_set
    k_set = ss.k_set_total()
    predicted = {1 - k / m: k for k in k_set}

    # Numerical: eigenvalues with multiplicities
    for lam_float in op.layer_keys:
        # Match to nearest predicted lambda
        best_k = None
        best_diff = float('inf')
        for pred_lam, k in predicted.items():
            diff = abs(lam_float - pred_lam)
            if diff < best_diff:
                best_diff = diff
                best_k = k
        assert best_diff < 5e-6, \
            f'λ={lam_float:.8f} has no k-match (nearest k={best_k}, diff={best_diff:.1e})'

        # Multiplicity must match prediction
        dim = op.layer_dimension(lam_float)
        layers_pred = ss.eigenvalue_layers()  # [(lam, mult, blocks, label), ...]
        pred_mult = None
        for p_lam, p_mult, _p_blocks, _label in layers_pred:
            if abs(p_lam - lam_float) < 5e-6:
                pred_mult = p_mult
                break
        assert pred_mult is not None, f'no predicted multiplicity for λ={lam_float}'
        assert dim == pred_mult, \
            f'λ(k={best_k}): dim={dim}, predicted={pred_mult}'

    print(f'test_k_set_reconstruction: OK  (k-set → {len(k_set)} eigenvalues)')

    # Verify k=5 genuinely absent at the reconstruction level
    assert 5 not in k_set, 'k=5 should be absent from k-set'


# ═══════════════════════════════════════════════════════════════════════════
# Level 3 — Dynamical preparation (Paper II bridge)
# ═══════════════════════════════════════════════════════════════════════════

def test_slow_fast_orthogonality():
    """P_slow P_fast = 0 and P_slow + P_fast = I.

    The slow/fast splitting is a proper orthogonal decomposition —
    foundation for the transport narrative in Paper II.
    """
    op = CubieSpectralOperator()

    mask_slow, mask_fast = op.slow_fast_split(threshold=2 / 3)
    V_slow = op.V[:, mask_slow]
    V_fast = op.V[:, mask_fast]
    P_slow = V_slow @ V_slow.T.conj()
    P_fast = V_fast @ V_fast.T.conj()

    # Orthogonality
    cross = float(np.linalg.norm(P_slow @ P_fast, 'fro'))
    assert cross < 1e-10, f'‖P_slow P_fast‖ = {cross:.1e}'

    # Completeness
    P_sum = P_slow + P_fast
    assert np.allclose(P_sum, np.eye(TOTAL_DIM), atol=1e-10), \
        'P_slow + P_fast ≠ I'

    # Dimension consistency
    slow_dim = int(round(np.trace(P_slow).real))
    fast_dim = int(round(np.trace(P_fast).real))
    assert slow_dim + fast_dim == 228, \
        f'dim_slow + dim_fast = {slow_dim + fast_dim}'

    print(f'test_slow_fast_orthogonality: OK  (slow={slow_dim}, fast={fast_dim})')


def test_generator_symmetry():
    """Spec(A) is invariant under relabeling of generators.

    A = (1/|S|) Σ ρ(s) is a symmetric sum — the spectrum does not depend on
    generator ordering. Verifies the averaging construction is well-defined.
    """
    import random

    # Canonical order
    op1 = CubieSpectralOperator()
    w1 = np.sort(op1.w)

    # Shuffled: build with same generators in different order
    gens_list = list(op1.rho_moves.items())
    random.seed(42)
    random.shuffle(gens_list)
    gens_shuffled = dict(gens_list)

    op2 = CubieSpectralOperator(generators=gens_shuffled)
    w2 = np.sort(op2.w)

    assert np.allclose(w1, w2, atol=1e-10), \
        f'max|Spec(shuffled) − Spec(canonical)| = {np.max(np.abs(w1 - w2)):.1e}'

    print(f'test_generator_symmetry: OK  (Spec invariant under shuffle)')


if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
