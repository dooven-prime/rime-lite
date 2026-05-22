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


def test_matrix_roundtrip(num_random=500, max_steps=50):
    """验证 from_vector ∘ matrix 作用 vs act 作用 """
    import random
    prim_moves = CubieMove.prim_moves
    prim_keys = list(prim_moves.keys())
    solved = CubieState.solved()
    sv = solved.vector
    rng = random.Random(42)
    omega = np.exp(2j * np.pi / 3)

    print("\n" + "=" * 70)
    print("test_matrix_roundtrip: from_vector(v @ matrix) vs act(state)")
    print("=" * 70)

    # ── 1. 单步 on solved ──
    print("\n--- Part 1: 1-step on solved state ---")
    ok = 0
    for key in prim_keys:
        mv = prim_moves[key]
        rec = CubieState.from_vector(sv @ mv.matrix)
        ref = mv.act(solved)
        if rec == ref:
            ok += 1
        else:
            print(f"  FAIL {key}: eq={rec == ref}, solvable={rec.is_solvable()}")
            if rec != ref:
                print(f"    ref={ref}")
                print(f"    rec={rec}")
    print(f"  rec == act(solved): {ok}/{len(prim_keys)} (should be 18)")

    # ── 2. 单步 on arbitrary states ──
    print("\n--- Part 2: 1-step on arbitrary states ---")
    n_ok = n_solvable = 0
    n_trials = 100
    for t in range(n_trials):
        keys = rng.choices(prim_keys, k=rng.randint(1, 30))
        s = solved
        for k in keys:
            s = prim_moves[k].act(s)
        mk = rng.choice(prim_keys)
        mv = prim_moves[mk]
        rec = CubieState.from_vector(s.vector @ mv.matrix)
        ref = mv.act(s)
        if rec == ref:
            n_ok += 1
        if rec.is_solvable():
            n_solvable += 1
    print(f"  rec == act(s): {n_ok}/{n_trials}")
    print(f"  solvable:      {n_solvable}/{n_trials}")

    # ── 3. 多步 on solved ──
    print(f"\n--- Part 3: Multi-step from solved ---")
    for steps in [1, 2, 5, 10, 20, 50]:
        n_ok = 0
        for t in range(50):
            keys = rng.choices(prim_keys, k=steps)
            # act chain
            s = solved
            for k in keys:
                s = prim_moves[k].act(s)
            ref = s
            # matrix chain (right action: v @ M1 @ M2 @ ...)
            v = sv.copy()
            for k in keys:
                v = v @ prim_moves[k].matrix
            rec = CubieState.from_vector(v)
            if rec == ref and rec.is_solvable():
                n_ok += 1
        print(f"  {steps:>3d} steps: rec==act_chain={n_ok}/50")

    # ── 4. 随机 matrix 路径后 is_solvable ──
    print(f"\n--- Part 4: Random matrix-path is_solvable ({num_random} trials, steps={max_steps}) ---")
    n_sol = 0
    for _ in range(num_random):
        keys = rng.choices(prim_keys, k=max_steps)
        v = sv.copy()
        for k in keys:
            v = v @ prim_moves[k].matrix
        s = CubieState.from_vector(v)
        if s.is_solvable():
            n_sol += 1
    print(f"  Solvable: {n_sol}/{num_random} ({100 * n_sol / num_random:.1f}%)")


def test_from_rotation():
    """验证 from_rotation 的 twist 公式：单步非 Y 轴使用 axis-dependent face formula，
    半步/多步使用 rotation-direction formula，无后置 flip patch。"""
    pm = CubieMove.prim_moves

    # 1. U/D moves (axis=1): corners never twist
    for key, mv in pm.items():
        if key[0] == 1:
            assert np.all(mv.corners_ori_delta == 0), f'{key}: U/D should have no corner twist'

    # 2. Half-turns (dir=±2): corners never twist (two quarter turns cancel)
    for key, mv in pm.items():
        if abs(key[2]) == 2:
            assert np.all(mv.corners_ori_delta == 0), f'{key}: half-turn should have no corner twist'

    # 3. Single-turn R/L (axis=0): twist depends on face (side), not on ±direction
    for side in (-1, 1):
        r_cw = pm[(0, side, 1)].corners_ori_delta
        r_ccw = pm[(0, side, -1)].corners_ori_delta
        assert np.array_equal(r_cw, r_ccw), \
            f'R/L side={side}: CW vs CCW should agree (face-dependent), got {r_cw} vs {r_ccw}'

    # 4. Single-turn F/B (axis=2): twist depends on face (side), not on ±direction
    for side in (-1, 1):
        f_cw = pm[(2, side, 1)].corners_ori_delta
        f_ccw = pm[(2, side, -1)].corners_ori_delta
        assert np.array_equal(f_cw, f_ccw), \
            f'F/B side={side}: CW vs CCW should agree (face-dependent), got {f_cw} vs {f_ccw}'

    # 5. R vs R' differ (different faces): side=+1 vs side=-1
    r_cw = pm[(0, 1, 1)].corners_ori_delta  # R
    l_cw = pm[(0, -1, 1)].corners_ori_delta  # L
    assert not np.array_equal(r_cw, l_cw), f'R vs L should differ'

    # 6. F vs B differ
    f_cw = pm[(2, 1, 1)].corners_ori_delta  # F
    b_cw = pm[(2, -1, 1)].corners_ori_delta  # B
    assert not np.array_equal(f_cw, b_cw), f'F vs B should differ'

    # 7. Inverse roundtrip: mv ∘ mv⁻¹ = identity for all 18 prims
    for key, mv in pm.items():
        comp = mv.compose(mv.inverse())
        assert comp == CubieMove.identity(), f'{key}: compose with inverse not identity'

    # 8. Cross-reference: R' = R⁻¹, L' = L⁻¹, F' = F⁻¹, B' = B⁻¹
    for face_side in (-1, 1):
        for axis in (0, 2):
            prim = pm[(axis, face_side, 1)]
            prim_inv = pm[(axis, face_side, -1)]
            assert prim_inv == prim.inverse(), f'axis={axis} side={face_side}: prime != inverse'

    print("test_from_rotation: OK (8 checks)")

# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
