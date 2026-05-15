"""Theorem verification:
  - SpectralStructure construction from 18 generators
  - k-set prediction matches Spec(A) = {1 - k/9 | k ∈ {0,1,2,3,4,6}}
  - Eigenvalue count prediction (6 distinct)
  - Block structure: cp/ep/co/eo dimensions
  - Integrality: class-sum coefficients rational
  - Partition integrality: block-level trace structure
  - Galois stability: spectral field is Q (rational)
  - Block projectors / block_of_index consistency

Paper: Paper I, Sec 3 (Spectral decomposition via Bose-Mesner)
Invariant level: 1 (group algebra)
"""

import numpy as np
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES, BLOCK_DIMS
from rime.spectralstructure import SpectralStructure, block_projectors, block_of_index

TOL = 1e-10
ss = SpectralStructure(CubieMove.prim_moves)


def test_construction():
    """SpectralStructure builds without error from 18 generators."""
    assert ss.n == 18, f'n={ss.n}'
    assert ss.m == 9, f'm={ss.m}, expected 9'
    assert len(ss.class_generators) == 6, f'n_classes={len(ss.class_generators)}, expected 6'
    print('test_construction: OK')


def test_k_set():
    """k-set prediction: {0, 1, 2, 3, 4, 6} — k=5 is genuinely absent."""
    k_total = ss._k_sets["total"]
    expected = {0, 1, 2, 3, 4, 6}
    assert k_total == expected, f'k-set={k_total}, expected {expected}'
    # k=5 must NOT be in the set
    assert 5 not in k_total, 'k=5 should be absent'
    print(f'test_k_set: OK  (k-set = {sorted(k_total)})')


def test_eigenvalues():
    """Predicted eigenvalues: λ = 1 - k/9 for each k in k-set."""
    evals = ss._eigenvalues
    expected = {
        0: 1.0,        # V₁
        1: 8/9,        # V₈/₉
        2: 7/9,        # V₇/₉
        3: 2/3,        # V₂/₃
        4: 5/9,        # V₅/₉
        6: 1/3,        # V₁/₃
    }
    assert len(evals) == 6, f'expected 6 eigenvalues, got {len(evals)}'
    for k, lam in expected.items():
        assert k in evals, f'missing k={k}'
        assert abs(evals[k] - lam) < TOL, f'λ(k={k})={evals[k]}, expected {lam}'
    print(f'test_eigenvalues: OK  ({len(evals)} eigenvalues)')


def test_eigenvalue_count():
    """predict_n_eigenvalues() returns 6."""
    assert ss.predict_n_eigenvalues() == 6
    print('test_eigenvalue_count: OK')


def test_slow_dimension():
    """predict_slow_dimension returns positive value (λ >= 2/3 subspace)."""
    dim_slow = ss.predict_slow_dimension(threshold=2/3)
    assert dim_slow > 0, f'slow dim = {dim_slow}'
    print(f'test_slow_dimension: OK  (slow_dim={dim_slow})')


def test_block_structure():
    """Block dimensions match BLOCK_DIMS from cubie.py."""
    assert ss.block_dims == BLOCK_DIMS
    assert ss.block_ranges == BLOCK_RANGES

    bd = ss.block_dims
    assert bd['cp'] == 64 and bd['ep'] == 144
    assert bd['co'] == 8 and bd['eo'] == 12
    print('test_block_structure: OK')


def test_block_projectors():
    """Block projectors partition [0, 228) correctly."""
    projs = block_projectors()
    assert set(projs.keys()) == {'cp', 'ep', 'co', 'eo'}

    # Each projector is diagonal
    for name, P in projs.items():
        off_diag = P - np.diag(np.diag(P))
        assert np.allclose(off_diag, 0, atol=TOL), f'{name} not diagonal'

    # Sum to identity
    P_sum = sum(projs.values())
    assert np.allclose(P_sum, np.eye(TOTAL_DIM), atol=TOL), 'ΣP_block ≠ I'

    # Trace = block dimension
    for name, P in projs.items():
        assert int(round(np.trace(P))) == BLOCK_DIMS[name], \
            f'{name} trace={np.trace(P)} ≠ dim={BLOCK_DIMS[name]}'
    print('test_block_projectors: OK')


def test_block_of_index():
    """block_of_index maps every index to correct block."""
    for start, end, name in [
        (0, 64, 'cp'), (64, 208, 'ep'), (208, 216, 'co'), (216, 228, 'eo')
    ]:
        for i in range(start, end):
            assert block_of_index(i) == name, f'block_of_index({i}) = {block_of_index(i)}, expected {name}'

    # Out of range raises
    try:
        block_of_index(-1)
        assert False, 'should raise on -1'
    except ValueError:
        pass
    try:
        block_of_index(228)
        assert False, 'should raise on 228'
    except ValueError:
        pass
    print('test_block_of_index: OK')


def test_integrality():
    """verify_integrality: class-sum coefficients are integral."""
    result = ss.verify_integrality()
    assert result['all_integer'], f'integrality: not all integer'
    print(f'test_integrality: OK  (all_integer={result["all_integer"]})')


def test_partition_integrality():
    """verify_partition_integrality: block-level trace structure."""
    result = ss.verify_partition_integrality()
    assert result['all_integer'], f'partition integrality: not all integer'
    print(f'test_partition_integrality: OK  (all_integer={result["all_integer"]})')


def test_galois_stability():
    """verify_galois_stability: spectral field is Q (rational)."""
    result = ss.verify_galois_stability()
    assert result['is_stable'], f'galois stability: not stable'
    assert result['field'] == 'Q', f'spectral field not Q: {result["field"]}'
    print(f'test_galois_stability: OK  (stable={result["is_stable"]}, field={result["field"]})')


def test_spectral_field():
    """predict_spectral_field returns rational field description."""
    field = ss.predict_spectral_field()
    assert 'rational' in str(field).lower() or 'Q' in str(field), \
        f'spectral field = {field}'
    print(f'test_spectral_field: OK  ({field})')


if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
