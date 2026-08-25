# Tests — Mathematical Invariant Verification

## Philosophy

The mathematical tests are **not** general software QA tests. They do not test
arbitrary edge cases or application behavior. Explicit infrastructure
exceptions protect experiment provenance and the versioned compiler, report,
and audit contracts.

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
| `test_cubieoperator.py` | Canonical engine: spectral-calculus checks, polynomial span, k-set registration | Paper I |
| `test_spectrum.py` | Six-layer numerical registration, k=5 census absence, multiplicities | Paper I |
| `test_sectors.py` | 9 QH joint sectors, layer splitting, S6 hub, S1 isolation | Paper II, Sec 4 |
| `test_commutant.py` | QH-family commutativity, Supp_nc localization | Paper II, Sec 5 |
| `test_transport.py` | Direct graph, sector non-invariance, and graph/operator composition obstruction | Paper II / revised Paper III |
| `test_experiment_observation.py` | Cached-observation manifest integrity and stale-source detection | Reproducibility infrastructure |
| `test_verification_state.py` | Tracked-tree mutation detection and Zenodo record-ID parsing | Release verification infrastructure |
| `../experiments/paper20/validation/validate_hostile_controls.py` | active carrier-path, default-discovery, evidence-boundary, and shared-carrier controls | Paper XX post-release maintenance |
| `test_contract_api.py` | Shared digest, repository-bound artifact, status-axis, and CompilerOutput schema mechanics | Cross-paper contract infrastructure |
| `test_accessibility_engine.py` | Typed direct/routed/word/Lie separation, incidence, rank protection, cutoff semantics | General API / Papers III, V, VII |
| `test_registry_v2.py` | Registry v2.0 schema, evidence, depth, repair, and promotion guards | Paper X Registry contract |
| `test_registry_migration.py` | Immutable-v1 digest and reproducible frozen-v2 migration | Paper X Appendix A11 |
| `test_sofcompiler_contracts.py` | Manifest/IR/Profile schemas, claim-local gates, and typed `Compile_v1` output regression | Paper X compiler theorem implementation |
| `test_sofrs_v2.py` | Capability-gated migration, exact CompilerOutput binding, and single-report validation | Paper XII SOFRS v2 contract |
| `test_sofaudit_v2.py` | Validated source-report receipts, source-addressed alignment, sparse comparison states, wall-input ownership, and shared status guards | Paper XIII SOFAUDIT v2 contract |
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
- **Run active tests**: `python tests/run_all_tests.py verify` (~1-2 min)
- **Run slow tests**: `python tests/run_slow_tests.py` (~5-10 min, requires CubieSpectralOperator)

## Repository-Non-Intervening Verification

The active runner copies the current tracked and non-ignored working files to
a temporary directory and runs every test there. Before and after the run it
records the source checkout's `HEAD`, tracked status, tracked diff digest, and
tracked-content digest. Any source-tree delta produces
`VERIFICATION_SIDE_EFFECT` and fails the harness, even if all mathematical or
protocol assertions passed.

The generative Paper XII and XIII regressions also self-isolate when launched
as individual scripts. Importing either regression outside verification
scratch is rejected before its migration or receipt-writing steps begin.

The versioned `verification-baseline.json` distinguishes new failures,
existing baseline failures, and resolved baseline failures. Baseline failures
remain unresolved evidence; verification never repairs, regenerates, or
re-signs their historical artifacts. Exit codes are `0` for `PASS`, `1` for
`FAIL`, and `2` for `UNRESOLVED`.

Release verification has three explicit stages:

1. `VERIFY` captures and checks the tracked release state.
2. `BUILD/REPLAY IN ISOLATION` writes generated output only inside scratch or
   an explicit candidate staging location.
3. `ANCHOR CHECK` downloads an actual deposited file and compares its bytes
   with one local release artifact.

Promotion is outside those verification stages. Only a paper-owned, explicit
`PROMOTE` operation may update tracked release paths; validator identity alone
does not confer mutation authority.

For a Zenodo file-byte check, run:

```bash
python tools/release/verify_zenodo_anchor.py \
  --doi 10.5281/zenodo.RECORD_ID \
  --local path/to/release-artifact.pdf \
  --remote-name deposited-file.pdf
```

An anchor check establishes equality of those two files only. It does not
validate the producer, validator, complete evidence closure, or scientific
claims.

Slow tests (each constructs a full CubieSpectralOperator):
  `test_cubieoperator.py` -- canonical engine: spectral-calculus checks, polynomial span, k-set registration
  `test_transport.py` -- direct graph and projected-composition obstruction

## Author-Side Release Gates

Paper-version release gates, migration checks, hostile fixtures, and internal
publication-surface audits are intentionally excluded from the public test
inventory. Their local results are engineering and release-control evidence;
the owning paper, accepted release manifest, and published record remain the
authority for public scientific claims. Reusable read-only release checks are
documented under [`tools/`](../tools/README.md).

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
