# RIME Public Documentation

This directory contains the public explanatory and reference documents for the
RIME program. It complements the paper manuscripts but does not replace their
theorems, hypotheses, claim status, or computational artifacts.

Publication identities and DOIs are maintained only in the root
[Public Release table](../README.md#public-release).

## Start Here

| Reader goal | Document |
|-------------|----------|
| Read a concise research overview | [overview.md](overview.md) |
| Understand the full paper architecture and typed interfaces | [PROGRAM_MAP.md](PROGRAM_MAP.md) |
| See which paper owns each object and claim | [PAPER_SCOPE.md](PAPER_SCOPE.md) |
| Understand why Rubik is used as a finite laboratory | [PROGRAM_PHILOSOPHY.md](PROGRAM_PHILOSOPHY.md) |

## Foundational References

| Document | Role |
|----------|------|
| [CORE_INVARIANTS.md](CORE_INVARIANTS.md) | stable Rubik calibration data and numerical boundaries |
| [conventions.md](conventions.md) | coordinates, move encoding, composition conventions, and tolerances |

## SOF Companions

| Document | Role |
|----------|------|
| [SOF_OBJECTS.md](SOF_OBJECTS.md) | static Sectorized Observable Framework object layer |
| [SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md) | deformation geometry, trajectories, and wall diagnostics |
| [SOF_REGISTRY.md](SOF_REGISTRY.md) | Registry evidence architecture and cross-species routing |

The companion documents explain the public SOF arc. They do not silently
promote release-local `R1`/`R2`/`D` terminology into a universal ladder.
Operator support, routed composition, full-word support, commutator support,
and Lie depth remain typed separately.

## Reproducibility and Contracts

| Resource | Role |
|----------|------|
| [experiments/README.md](../experiments/README.md) | paper-owned scripts, result artifacts, and claim boundaries |
| [figures/README.md](../figures/README.md) | presentation renderers and manuscript image assets |
| [schemas/README.md](../schemas/README.md) | published SOFRS, SOFAudit, and Registry contracts |
| [registry/](../registry/) | frozen versioned Registry snapshots |
| [CCS v2](../ccs/canonical_specification.md) | optional computational companion archive |

Presentation renderers are not scientific certificates. Cached observations
are not proofs. CCS v2 is optional archive material rather than a premise,
definition source, or claim authority for the independent papers.

## Source Authority

Use the following order when statements appear to differ:

1. The owning paper's current manuscript and declared version boundary.
2. The paper-owned validation artifact or canonical machine-readable schema.
3. The public scope, program-map, and companion documentation in this
   directory.
4. CCS v2 for optional reproducibility records and historical context.

Cross-paper citations identify compatible objects; they do not import
hypotheses or promote support to composition, words, commutators, Lie depth,
moving fields, or represented genericity.

## Repository Boundary

The public documentation covers Papers I--XIII and their released support
contracts. Author-side planning, exploratory research routing, and historical
working notes are outside this public documentation index.
