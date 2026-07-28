"""
Claim-qualified structural and computational checks:
    - SpectralStructure construction from 18 generators 
    - registered k-set matches {0,1,2,3,4,6}
    - Eigenvalue count prediction (6 distinct) 
    - Block structure: cp/ep/co/eo dimensions 
    - Integrality certificate boundary: CO/EO remain unresolved
    - Canonical face-partition audit: the integer hypothesis fails
    - Numerical field registration is not an exact arithmetic proof
    - Block projectors / block_of_index consistency 

Paper: Paper I (block structure and registered finite census)
Claim status: mixed theorem support and computational certificate
"""


import numpy as np
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES, BLOCK_DIMS
from rime.spectralstructure import SpectralStructure, block_projectors, block_of_index

TOL = 1e-10
ss = SpectralStructure(CubieMove.prim_moves)
m = ss.m  # denominator: λ_k = 1 − k/m


def test_construction():
    """SpectralStructure builds without error from 18 generators."""
    assert ss.n == 18, f'n={ss.n}'
    assert ss.m == 9, f'm={ss.m}, expected 9'
    assert len(ss.class_generators) == 6, f'n_classes={len(ss.class_generators)}, expected 6'
    print('test_construction: OK')


def test_k_set():
    """Registered k-set is {0, 1, 2, 3, 4, 6}; k=5 is absent."""
    k_total = ss._k_sets["total"]
    expected = {0, 1, 2, 3, 4, 6}
    assert k_total == expected, f'k-set={k_total}, expected {expected}'
    # k=5 must NOT be in the set
    assert 5 not in k_total, 'k=5 should be absent'
    print(f'test_k_set: OK  (k-set = {sorted(k_total)})')


def test_eigenvalues():
    """Registered eigenvalues match 1 - k/9 for each k in the census."""
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
    """registered_eigenvalue_count() returns 6."""
    assert ss.registered_eigenvalue_count() == 6
    print('test_eigenvalue_count: OK')


def test_slow_dimension():
    """registered_slow_dimension returns the finite census value."""
    dim_slow = ss.registered_slow_dimension(threshold=2/3)
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
    """Block certificates do not silently promote unresolved CO/EO data."""
    result = ss.verify_integrality()
    assert not result['all_integer']
    assert result['certified_blocks'] == ['cp', 'ep']
    assert result['unresolved_blocks'] == ['co', 'eo']
    assert all(info['is_integer'] is None for info in result['co'].values())
    assert all(info['is_integer'] is None for info in result['eo'].values())
    print('test_integrality: OK  (CO/EO unresolved)')


def test_partition_integrality():
    """The canonical face partition fails the integer certificate."""
    result = ss.audit_partition_integrality()
    assert not result['all_integer']
    dims = tuple(int(info['dim']) for _, info in sorted(
        result['mechanism'].items(), reverse=True
    ))
    assert dims == (20, 2, 39, 26, 106, 35), dims
    noninteger = [
        face['trace']
        for info in result['mechanism'].values()
        for face in info['face_traces'].values()
        if not face['is_integer']
    ]
    assert any(abs(value - 16 / 3) < 1e-6 for value in noninteger)
    assert any(abs(value - 530 / 3) < 1e-6 for value in noninteger)
    conclusion = result['rationality_conclusion']
    assert not conclusion['hypothesis_satisfied']
    assert not conclusion['certifies_rationality']
    print(f'test_partition_integrality: OK  (dims={dims}, hypothesis fails)')


def test_spectral_field_registration():
    """Field recognition remains a computational observation."""
    result = ss.register_spectral_field()
    assert result['is_stable'], 'registered labels are not stable'
    assert result['field'] == 'Q', f'unexpected registered label: {result["field"]}'
    assert result['claim_status'] == 'computational_observation'
    print(
        'test_spectral_field_registration: OK  '
        f'(label={result["field"]}, status={result["claim_status"]})'
    )


def test_spectral_field():
    """Class symmetry alone does not certify the exact spectral field."""
    field = ss.structural_spectral_field_status()
    assert field == 'not_certified', f'spectral field status = {field}'
    print(f'test_spectral_field: OK  ({field})')


def test_retired_false_predictors_are_absent():
    """Circular feasibility and arbitrary-family predictors are removed."""
    assert not hasattr(ss, 'diophantine_feasibility')
    assert not hasattr(ss, 'predict_q3_krawtchouk')


if __name__ == "__main__":
    for name in sorted(k for k in globals() if k.startswith('test_')):
        globals()[name]()
    print('\n=== ALL TESTS PASSED ===')
