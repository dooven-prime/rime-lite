# Tests — Mathematical Invariant Verification

## Philosophy

These tests are **not** software QA tests. They do not test edge cases, error handling, or API contracts.

They are **mathematical invariant verification tests** corresponding directly to claims in the trilogy papers. Each test file verifies one class of invariants from the invariant hierarchy.

## Invariant Hierarchy

| Level | Description | Example |
|-------|-------------|---------|
| 0 | Categorical / structural | Block decomposition exists |
| 1 | Group-algebraic | Spectral decomposition, isotypic decomposition |
| 2 | Generator-conditioned | Transport strengths, hub degree, T7 pairs |

Level-0 and level-1 claims hold for **any** symmetric generator set. Level-2 claims hold for the Rubik's cube 18-generator system.

## Test → Paper Mapping

| Test File | Theorem Verified | Paper & Section |
|-----------|-----------------|-----------------|
| `test_action_token.py` | Parser roundtrip, cubie key mapping | All papers (conventions) |
| `test_cubie.py` | Group axioms, inverse, build, compose-act consistency | Paper I, Sec 2 |
| `test_representation.py` | Group homomorphism, unitary, block decomposition | Paper I, Sec 2 |
| `test_spectralstructure.py` | k-set prediction, integrality, Galois stability, rational field | Paper I, Sec 3 |
| `test_spectrum.py` | Rational spectral law, k=5 absent, multiplicities | Paper I, Sec 3 |
| `test_sectors.py` | 9 primitive sectors, layer splitting, S6 hub, S1 isolation | Paper II, Sec 4 |
| `test_commutant.py` | Center commutativity, Supp_nc localization | Paper II, Sec 5 |
| `test_commutant_gap.py` | Δ_comm = dim(Comm(A)) − dim(Comm(ρ)), transport-commutant relation | Paper II, Sec 8.3 |
| `test_transport.py` | K symmetry, S6 transport hub, T7 theorem, N=2 control | Paper II Sec 6 / Paper III |
| `test_f3.py` | Isotypic decomposition, Schur's lemma, multiplicity reservoir | Paper I App B / Paper II |

## Reproducibility

- **Deterministic**: All tests use `seed=42` where randomness is involved.
- **No randomness in results**: center decomposition, irrep detection, and transport computation are deterministic after seed.
- **Assert-only style**: Plain Python `assert` via a local `check()` helper. No pytest, no unittest, no test framework.
- **Run individually**: `python tests/test_spectrum.py`
- **Run fast tests**: `python tests/run_all_tests.py` (~10s)
- **Run slow tests**: `python tests/run_slow_tests.py` (~5-10 min, requires CubieSpectralOperator)

Slow tests (each constructs a full CubieSpectralOperator):
  `test_commutant_gap.py` — Δ_comm, transport invariants (Paper II §8.3)
  `test_transport.py` — K symmetry, T7 pairs, N=2 control (Paper II §6 / Paper III)
  `test_f3.py` — isotypic decomposition, multiplicity reservoir (Paper I App B / Paper II)

## Tolerances

| Context | Tolerance | Reason |
|---------|-----------|--------|
| Homomorphism, unitary | `1e-7` | float64 accumulation in 228×228 matrix multiplication |
| Block-diagonality | `1e-12` | Exact by construction (permutation + phase) |
| Spectral, sector, commutant | `1e-10` | Eigensolver at float64 precision |
| Transport (K threshold) | `0.05` | Discriminates "zero" from "nonzero" transport |
| Hybrid classification | `0.01 × dim` | Fraction of sector norm in a block |
