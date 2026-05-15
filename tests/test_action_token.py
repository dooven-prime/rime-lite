"""ActionToken parser self-consistency tests — roundtrip invariants, cubie key mapping."""

from rime.cube import ActionToken
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


if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
