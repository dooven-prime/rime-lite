# Tests — Mathematical Invariant Verification

## Philosophy

The mathematical tests are **not** general software QA tests. They do not test
arbitrary edge cases or application behavior. The one explicit infrastructure
exception is `test_experiment_observation.py`, which protects the provenance
and stale-detection contract used by cached computational observations.

They are **mathematical invariant verification tests** corresponding to claims
in independent RIME papers. Each test file verifies one declared class of
invariants; no test creates a cross-paper theorem dependency.

## Invariant Hierarchy

| Level | Description | Example |
|-------|-------------|---------|
| 0 | Categorical / structural | Block decomposition exists |
| 1 | Group-algebraic | Representation and spectral decomposition |
| 2 | Generator-conditioned | Transport strengths, hub degree, graph/composition obstructions |

These levels organize the test inventory; they do not imply that every test
generalizes to every symmetric generator family. Each module states its own
input family, arithmetic mode, and claim status.

## Test → Paper Mapping

| Test File | Claim or Contract Exercised | Paper & Section |
|-----------|-----------------|-----------------|
| `test_action_token.py` | Parser roundtrip, cubie key mapping | All papers (conventions) |
| `test_cubie.py` | Group axioms, inverse, build, compose-act consistency | Paper I, Sec 2 |
| `test_representation.py` | Group homomorphism, unitary, block decomposition | Paper I, Sec 2 |
| `test_spectralstructure.py` | k-set registration, certificate boundaries, failed face-partition hypothesis | Paper I |
| `test_spectral_utils_api.py` | Commuting-Hermitian and orthogonal-projector registration gates | General spectral API |
| `claim_contract_tests.py` | Executable claim-status boundaries: arithmetic, semisimplicity, S4 H1, graph shape, cutoff, normality gates, observation metadata, and public-output routing | Papers I--VII |
| `test_cubieoperator.py` | Canonical engine: spectral-calculus checks, polynomial span, k-set registration | Paper I |
| `test_spectrum.py` | Six-layer numerical registration, k=5 census absence, multiplicities | Paper I |
| `test_sectors.py` | 9 QH joint sectors, layer splitting, S6 hub, S1 isolation | Paper II, Sec 4 |
| `test_commutant.py` | QH-family commutativity, Supp_nc localization | Paper II, Sec 5 |
| `test_transport.py` | Direct graph, sector non-invariance, and graph/operator composition obstruction | Paper II / revised Paper III |
| `test_experiment_observation.py` | Cached-observation manifest integrity and stale-source detection | Reproducibility infrastructure |
| `test_accessibility_engine.py` | Typed direct/routed/word/Lie separation, incidence, rank protection, cutoff semantics | General API / Papers III, V, VII |
| `test_paper13_methodology.py` | Comparison-layer methodology controls | Paper XIII |
| `archive/test_commutant_gap.py` | First-version candidate commutant dimensions | Provenance only |
| `archive/test_f3.py` | First-version compressed-centralizer computation | Withdrawn interpretation; provenance only |
| `archive/test_generator_families.py` | First-version generator-family T7 counts | Graph-square provenance only |
| `archive/test_hybrid_sectors.py` | First-version hybrid/T7 mediation labels | Graph-incidence provenance only |

## Reproducibility

- **Deterministic**: All tests use `seed=42` where randomness is involved.
- **No randomness in results**: center decomposition, irrep detection, and transport computation are deterministic after seed.
- **Assert-only style**: Plain Python `assert` via a local `check()` helper. No pytest, no unittest, no test framework.
- **Run individually (PowerShell)**: set
  `$env:PYTHONPATH=(Resolve-Path '.').Path`, then run
  `python tests/test_spectrum.py`.
- **Run individually (POSIX)**: `PYTHONPATH=. python tests/test_spectrum.py`
- **Run active tests**: `python tests/run_all_tests.py` (~1-2 min)
- **Run slow tests**: `python tests/run_slow_tests.py` (~5-10 min, requires CubieSpectralOperator)

Slow tests (each constructs a full CubieSpectralOperator):
  `test_cubieoperator.py` -- canonical engine: spectral-calculus checks, polynomial span, k-set registration
  `test_transport.py` -- direct graph and projected-composition obstruction

Withdrawn claim-path tests live under `tests/archive/` and are never executed
by the default fast or slow runners.

## Tolerances

| Context | Tolerance | Reason |
|---------|-----------|--------|
| Homomorphism, unitary | `1e-7` | float64 accumulation in 228×228 matrix multiplication |
| Block-diagonality | `1e-12` | Exact by construction (permutation + phase) |
| Spectral, sector, commutant | `1e-10` | Eigensolver at float64 precision |
| Transport (K threshold) | `0.05` | Discriminates "zero" from "nonzero" transport |
| Hybrid classification | `0.01 × dim` | Fraction of sector norm in a block |
