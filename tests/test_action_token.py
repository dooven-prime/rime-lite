"""ActionToken parser self-consistency tests — roundtrip invariants, cubie key mapping."""

from rime.cube import ActionToken,CubeBase
from rime.cubie import CubieMove

N = 3
gens = CubieMove.prim_moves()
ALL_FACES = [f + s for f in 'RULDFB' for s in ['', "'", '2']]
ALL_SLICES = [f + s for f in 'MES' for s in ['', "'", '2']]


def test_action_token_roundtrip():
    """ActionToken.transform(s).__str__() == s for all standard moves."""
    for s in ALL_FACES + ALL_SLICES:
        assert str(ActionToken.transform(s, n=N)) == s, f'roundtrip fail: {s}'
    print('test_action_token_roundtrip: OK')


def test_action_token_cubie_roundtrip():
    """ActionToken.from_cubie_move <-> to_cubie_move roundtrip for all 18."""
    for key in gens:
        token = ActionToken.from_cubie_move(*key, n=N)
        assert token.to_cubie_move(n=N) == key, f'cubie roundtrip fail: {key}'
    print('test_action_token_cubie_roundtrip: OK')


def test_action_token_key_independence():
    """Different (axis, side, direction) produce 18 distinct keys."""
    keys = set()
    for key in gens:
        token = ActionToken.from_cubie_move(*key, n=N)
        keys.add(token.key)
    assert len(keys) == 18, f'expected 18 distinct keys, got {len(keys)}'
    print('test_action_token_key_independence: OK')


def test_corner_coords():
    """Verify corner_coords correctness for N=3..7 validity."""
    expected_names = ['URF', 'UFL', 'ULB', 'UBR', 'DFR', 'DLF', 'DBL', 'DRB']
    for n in [3, 4, 5, 6, 7]:
        coords = CubeBase.corner_coords(n)
        assert len(coords) == 8, f'N={n}: expected 8 corners, got {len(coords)}'
        names = [''.join(CubeBase.FACES[f] for f, r, c in corner) for corner in coords]
        assert names == expected_names, f'N={n}: expected {expected_names}, got {names}'
        for i, corner in enumerate(coords):
            assert len(corner) == 3, f'N={n} corner {i}: expected 3 stickers'
            faces = [f for f, r, c in corner]
            assert len(set(faces)) == 3, f'N={n} corner {i}: duplicate faces {faces}'
            for f, r, c in corner:
                assert r in (0, n - 1), f'N={n} corner {i}: r={r} out of bounds'
                assert c in (0, n - 1), f'N={n} corner {i}: c={c} out of bounds'
    print('test_corner_coords: OK')


def test_edge_coords():
    """Verify edge_coords correctness for N=3..7 validity."""
    expected_names = ['UR', 'UF', 'UL', 'UB', 'FR', 'FL', 'BL', 'BR', 'DR', 'DF', 'DL', 'DB']
    for n in [3, 4, 5, 6, 7]:
        coords = CubeBase.edge_coords(n)
        assert len(coords) == 12, f'N={n}: expected 12 edges, got {len(coords)}'
        names = [''.join(CubeBase.FACES[f] for f, r, c in edge) for edge in coords]
        assert names == expected_names, f'N={n}: expected {expected_names}, got {names}'
        for i, edge in enumerate(coords):
            assert len(edge) == 2, f'N={n} edge {i}: expected 2 stickers'
            faces = [f for f, r, c in edge]
            assert len(set(faces)) == 2, f'N={n} edge {i}: duplicate faces {faces}'
            for f, r, c in edge:
                assert 0 <= r < n, f'N={n} edge {i}: r={r} out of bounds'
                assert 0 <= c < n, f'N={n} edge {i}: c={c} out of bounds'
                # edge sticker must be on the border (r or c at 0 or n-1, but not both)
                is_border = (r in (0, n - 1)) ^ (c in (0, n - 1))
                assert is_border, f'N={n} edge {i}: ({r},{c}) not an edge position'
    print('test_edge_coords: OK')


def test_center_coords():
    """Verify center_coords / get_centers / SOLVED_CENTERS_MAP for N=3..7."""
    import numpy as np
    for n in [3, 4, 5, 6, 7]:
        coords = CubeBase.center_coords(n)
        expected = 6 * (n - 2) ** 2
        assert len(coords) == expected, f'N={n}: expected {expected} centers, got {len(coords)}'
        for f, r, c in coords:
            assert 0 <= f < 6, f'N={n}: face={f}'
            assert 1 <= r < n - 1, f'N={n}: r={r} on border'
            assert 1 <= c < n - 1, f'N={n}: c={c} on border'
        faces = {f for f, r, c in coords}
        assert faces == set(range(6)), f'N={n}: missing faces'

        # get_centers consistency
        state = np.arange(6 * n * n).reshape(6, n, n)
        centers = CubeBase.get_centers(state)
        for i, (f, r, c) in enumerate(coords):
            assert centers[i] == state[f, r, c], f'N={n}: get_centers mismatch at {i}'

    print('test_center_coords: OK')

if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
