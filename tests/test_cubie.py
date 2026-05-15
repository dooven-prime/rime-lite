"""CubieMove / CubieState group-theoretic self-consistency tests.

Adapted from rime/test/test_cubie.py — standalone tests with no solver/sticker dependency.
"""

import numpy as np
from rime.cubie import CubieState, CubieMove, TOTAL_DIM

TOL = 1e-6


# ═══════════════════════════════════════════════════════════════════════════════
# Group axioms
# ═══════════════════════════════════════════════════════════════════════════════

def test_group_axioms():
    """逆元、恒等元、结合律 — identity, inverse, composition."""
    s = CubieState.solved()
    M = CubieMove.from_rotation(1, 1, 1)   # U
    M2 = CubieMove.from_rotation(1, 1, 2)  # U2
    M_ = CubieMove.from_rotation(1, 1, -1) # U'
    I = CubieMove.identity()

    # identity
    assert M.compose(I) == M
    assert I.compose(M) == M

    # inverse
    assert M.compose(M.inverse()) == I
    assert M.inverse().compose(M) == I
    assert M.compose(M_) == I
    assert M.inverse() == M_

    # composition
    assert M.compose(M) == M2
    assert M_.compose(M_) == M2

    # action identity
    assert I.act(s) == s

    print('test_group_axioms: OK')


# ═══════════════════════════════════════════════════════════════════════════════
# Representation ρ(g)
# ═══════════════════════════════════════════════════════════════════════════════

def test_representation():
    """ρ 酉性、同态、trace — unitarity, homomorphism, state vector."""
    s = CubieState.solved()
    M = CubieMove.from_rotation(1, 1, 1)
    I = CubieMove.identity()

    # state vector roundtrip
    Sv = s.vector
    assert Sv.dtype == np.complex64
    assert CubieState.from_vector(Sv) == s

    # ρ(identity) = I
    assert np.allclose(I.rho(), np.eye(TOTAL_DIM), atol=TOL)

    # ρ(gh) = ρ(g) @ ρ(h)
    assert np.allclose(I.compose(M).rho(), I.rho() @ M.rho(), atol=TOL)

    # unitarity: ρ(g) @ ρ(g)^H = I
    assert np.allclose(M.rho() @ M.rho().T.conj(), np.eye(TOTAL_DIM), atol=TOL)

    # inverse: ρ(g⁻¹) = ρ(g)^*
    assert np.allclose(M.inverse().rho(), M.rho().T.conj(), atol=TOL)

    # state vector action: v @ ρ(g) = act(s).vector
    assert np.allclose(Sv @ M.matrix, M.act(s).vector, atol=TOL)

    # norm preservation
    assert abs(np.linalg.norm(Sv @ M.rho()) - np.linalg.norm(Sv)) < TOL

    print('test_representation: OK')


# ═══════════════════════════════════════════════════════════════════════════════
# Per-generator group properties
# ═══════════════════════════════════════════════════════════════════════════════

def test_prim_moves_group_props():
    """逐 prim_move 验证：群乘法、逆元、酉性、向量/矩阵一致性."""
    s = CubieState.solved()
    I = CubieMove.identity()
    prim = CubieMove.prim_moves()

    for k, mv in prim.items():
        # -- basic act --
        s1 = mv.act(s)
        assert I.act(s) == s
        assert mv.convert().convert() == mv
        assert mv.convert().inverse() == mv.inverse().convert()

        # act / act_left consistency via convert
        s2 = mv.act_left(s)
        assert mv.convert().act(s) == s2
        assert mv.act(s) == mv.convert().act_left(s)

        # -- identity --
        assert mv.compose(I) == mv
        assert I.compose(mv) == mv

        # -- inverse cancellation --
        assert mv.inverse().act(s1) == s
        assert mv.act(mv.inverse().act(s)) == s
        assert mv.compose(mv.inverse()) == I
        assert mv.inverse().compose(mv) == I

        # -- associativity (spot check) --
        assert mv.inverse().act(mv.act(s)) == I.act(s)

        # -- orientation sum invariants --
        assert mv.corners_ori_delta.sum() % 3 == 0, f'corner ori sum fail: {k}'
        assert mv.edges_ori_delta.sum() % 2 == 0, f'edge ori sum fail: {k}'

        # -- solvability preservation --
        assert mv.act(s).is_solvable(), f'not solvable: {k}'

        # -- ρ unitarity --
        Ms = mv.rho()
        assert np.allclose(Ms @ Ms.T.conj(), np.eye(TOTAL_DIM), atol=TOL), \
            f'ρ not unitary: {k}'
        assert np.allclose(Ms.T.conj() @ Ms, np.eye(TOTAL_DIM), atol=TOL), \
            f'ρ^H ρ ≠ I: {k}'

        # -- ρ homomorphism --
        assert np.allclose(I.rho() @ Ms, I.compose(mv).rho(), atol=TOL), \
            f'ρ homomorphism fail: {k}'

        # -- state vector roundtrip --
        assert CubieState.from_vector(s1.vector) == s1, f'vector roundtrip: {k}'

        # -- v @ matrix == act(s).vector --
        Sv = s.vector
        assert np.allclose(Sv @ mv.matrix, s1.vector, atol=TOL), \
            f'matrix/vector mismatch: {k}'

        # -- inverse matrix == ρ^H --
        assert np.allclose(mv.inverse().matrix, mv.matrix.T.conj(), atol=TOL), \
            f'inverse matrix ≠ ρ^H: {k}'

        # -- compose with U, check trace invariance under conjugation --
        M = CubieMove.from_rotation(1, 1, 1)
        lhs = M.compose(mv).compose(M.inverse()).matrix
        rhs = mv.matrix
        assert abs(np.trace(lhs) - np.trace(rhs)) < TOL * 10, \
            f'trace not conjugacy-invariant: {k}'

    # ρ = I ⇒ move = I
    for mv in prim.values():
        if np.allclose(mv.rho(), np.eye(TOTAL_DIM), atol=TOL):
            assert mv == I, f'ρ=I but move ≠ I'

    print(f'test_prim_moves_group_props: OK  ({len(prim)} generators)')


# ═══════════════════════════════════════════════════════════════════════════════
# Action consistency
# ═══════════════════════════════════════════════════════════════════════════════

def test_action_consistency():
    """identity / inverse / build / compose-act 一致性."""
    I = CubieMove.identity()
    s = CubieState.solved()
    prim = CubieMove.prim_moves()

    # identity
    assert I.act(s) == s

    # inverse cancellation
    for m in prim.values():
        assert m.compose(m.inverse()) == I

    # CubieMove.build: can reconstruct a move from (s0, s1)
    for k, m in prim.items():
        s1 = m.act(s)
        built = CubieMove.build(s, s1)
        assert built == m, f'build mismatch: {k}'

    # compose-act consistency: (m1 @ m2).act(s) == m2.act(m1.act(s))
    items = list(prim.values())
    for m1 in items[:6]:  # one per face, avoid 18×18 explosion
        for m2 in items:
            assert m1.compose(m2).act(s) == m2.act(m1.act(s)), \
                f'compose/act mismatch'

    print(f'test_action_consistency: OK')


# ═══════════════════════════════════════════════════════════════════════════════
# Slice moves self-consistency
# ═══════════════════════════════════════════════════════════════════════════════

def test_slice_moves():
    """Slice moves M/E/S are well-defined and solvability-preserving."""
    s = CubieState.solved()
    slices = CubieMove.slice_moves()

    for k, m in slices.items():
        s1 = m.act(s)
        assert s1.is_solvable(), f'slice not solvable: {k}'
        # inverse returns to solved
        assert m.inverse().act(s1) == s, f'slice inverse fail: {k}'
        # unitarity
        assert np.allclose(m.rho() @ m.rho().T.conj(), np.eye(TOTAL_DIM), atol=TOL), \
            f'slice ρ not unitary: {k}'
        # slice moves are NOT in prim_moves (they are a separate set)
        assert not m.is_primitive(), f'slice should not be primitive: {k}'

    print(f'test_slice_moves: OK  ({len(slices)} slices)')


# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
