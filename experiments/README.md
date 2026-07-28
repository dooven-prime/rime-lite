# Experiments

This directory contains deterministic validation, computational certificates,
bounded observations, and portability diagnostics for the RIME program.
Script-level roles, parameters, expected outputs, and claim boundaries belong
in the owning `experiments/paperN/README.md`.

This top-level page is only a routing and maintenance index.

## Directory Contract

New or version-reopened paper directories use:

```text
experiments/paperN/
|-- README.md       paper-local artifact and claim map
|-- validation/     current citable validation
|-- results/        generated records, observations, and run summaries
`-- archive/        retired experiments and historical provenance
```

Directories need not contain every subdirectory. Immutable releases may retain
older fixed paths until a versioned reopening.

Paper-facing computations write generated records under the owning
`results/` directory. They do not write public artifacts to repository-level
`data/`. Presentation renderers and manuscript images belong under

## Paper Routing

| Paper | Experiment entry point | Scope |
|-------|------------------------|-------|
| I | [paper1/README.md](paper1/README.md) | block spectral census and arithmetic controls |
| II | [paper2/README.md](paper2/README.md) | registered sectors and direct transport |
| III | [paper3/README.md](paper3/README.md) | support graph versus projected composition |
| IV | [paper4/README.md](paper4/README.md) | fixed collision geometry and numerical registration |
| V | [paper5/README.md](paper5/README.md) | support, products, words, commutators, and Lie depth |
| VI | [paper6/README.md](paper6/README.md) | linearized commutativity/normality and point registrations |
| VII | [paper7/README.md](paper7/README.md) | incidence geometry, rank protection, and finite Lie atlas |
| IX | [paper9/](paper9/) | observable-deformation diagnostics |
| X | [paper10/](paper10/) | pipeline and Registry evidence |
| XI | [paper11/README.md](paper11/README.md) | wall records, taxonomy, and boundary audits |
| XII | [paper12/README.md](paper12/README.md) | SOF Report validation and diagnostic probes |
| XIII | [paper13/](paper13/) | aligned report comparison and controlled examples |

Where a paper-local README is not yet present, the owning manuscript and
script docstrings define the release-local scope. A future versioned reopening
should add the standard local README before changing artifact semantics.

Papers VIII--XIII retain their published or release-local terminology. Bare
`R1`/`R2`/`D`, ladder, repair, and wall labels in those artifacts must not be
read as a completed migration to the separate operator, routed-composition,
full-word, commutator, and Lie-depth branches. The frozen Paper X Registry v1
snapshot is not backfilled during later migration.

## Shared Diagnostics

| Directory | Role |
|-----------|------|
| [quantum/](quantum/) | quantum-gate and trajectory portability diagnostics |
| [cross_ref/](cross_ref/) | related-work positioning diagnostics |

These directories provide bounded comparisons and controls. They are not
standalone theorem sources.

## Cached Observations

Long deterministic computations may store a versioned
`*.observation.json` under the owning paper's `results/` directory through
`experiments.observation`. An observation records parameters, runtime
provenance, Git state, claim scope, limitations, and declared source hashes.

Check a cached record from the repository root with:

```bash
python -m experiments.observation path/to/result.observation.json --root .
```

A current hash check can avoid unnecessary recomputation during drafting. It
does not replace the executable certificate or the final release run.

## Maintenance Rules

- Run commands from the repository root unless the paper-local README states
  otherwise.
- Keep randomness deterministic and record the seed.
- Treat absolute support tolerances and observable scaling as part of the
  declared realization.
- Keep `validation/`, `results/`, and `archive/` roles separate.
- Do not cite archived scripts as current claim support.
- Do not infer theorem status from a cached result, figure, or passing
  numerical residual.
- Keep operator, routed-product, full-word, commutator, and Lie-depth outputs
  typed separately.

Repository-wide regression tests use:

```bash
python tests/run_all_tests.py
```

The owning paper README remains the source for any additional slow,
environment-specific, or release-validation command.
