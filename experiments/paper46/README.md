# Paper XLVI: RSR-2 Development Package

This package owns the candidate's guarded two-ring implementation, bounded
controls and Lean companion. The [manuscript](../../papers/paper46/Paper%20XLVI.md)
owns its mathematical claims; the [source map](FORMALIZATION_MAP.md)
identifies the checked declarations. This is a development extraction, not
a release archive.

## Model and Proof Scope

The five unit-cost letters are lower/upper rotation, lower/upper adjacent
collapse, and the guarded upward elevator. Its source must be occupied and
receiver empty. There is no downward transfer or cross-layer fusion.
Python retains an event list for replay; the all-parameter Lean placement
theorems concern the declared atom-to-location guarded executor. The
concrete four-site Lean certificate also checks its event log.

The completed surface covers Bell realization, exact retention iff and
minimum transferred atom mass, packet/port ledgers, the specified linear
and quadratic literal optima, and linear antipodal partition bounds. The
general partition diameter is not classified.

## Reproduce

From the repository root, using Python 3.10 or newer:

```text
python -B experiments/paper46/validation/replay.py
python -B experiments/paper46/validation/replay.py --lean --report experiments/paper46/results/local-replay.json
```

The first command checks candidate input bytes and runs the bounded tests.
The second also builds the pinned Lean package and checks all 223 explicit
axiom targets. `--lake PATH` selects a specific toolchain executable. No
Python third-party library, Mathlib cache, other paper source or exploratory
directory is required. The official pinned Lean toolchain must already be
installed.

Direct commands remain available:

```text
python -B -m unittest discover -s experiments/paper46 -p "test_*.py"
python -B experiments/paper46/layer_allocation_geometry.py
python -B experiments/paper46/antipodal_partition_cost.py --max-m 100
```

| Control | Finite scope |
| --- | --- |
| Bell/interleaved construction | Every partition through `n=7`; permutation loading through `n=6` |
| Retention and mass | Full physical reachability graphs through `n=4`, with additional constructive allocation tests |
| Singleton optimal schedules | Separately implemented exact search through `n=7`, including the four `n=2` words |
| Antipodal witnesses | Literal endpoints, events and costs through `m=32`, plus `m=50,100`; small target-pure graph checks |

The standard-library controls are implementation checks, not all-parameter
proofs or a certified Python-to-Lean semantic equivalence.

## Provenance and Candidate Identity

`extraction-provenance.json` records byte-preserving copies from
`experiments/exploratory/stacked_rings_rsr2`. That directory remains research
provenance, not a runtime dependency. `development-manifest.json` binds the
paper's canonical sources and this package, excluding build products and
generated replay results. It is mutable before release; it does not assert
a public commit, tag, DOI or independently reproduced environment.

The replay receipt records the manifest hash, commands, outputs and audit
results. A fresh package build using an already installed local toolchain
is not an independently acquired cold replay. Existing proof linter
warnings are retained; the extraction does not refactor proved modules.

The [candidate CI](../../.github/workflows/paper46-candidate.yml) runs the
same byte check, bounded controls, Lean build, and axiom audit on a hosted
runner. Its generated receipt is retained only after a successful run;
it is not an independent cold-replay certificate or a release qualification.
