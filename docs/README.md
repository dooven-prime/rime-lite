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
| Trace Papers I--VII interfaces and promotion limits | [PRE_SOF_INTERFACE_MAP.md](PRE_SOF_INTERFACE_MAP.md) |
| Check controlled cross-paper terminology | [PROGRAM_VOCABULARY.md](PROGRAM_VOCABULARY.md) |
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
| [SOF_PROTOCOL_STACK.md](SOF_PROTOCOL_STACK.md) | compiler-to-report-to-audit-to-interpretation contracts and authority boundaries |

The companion documents explain the public SOF arc. They do not silently
promote release-local `R1`/`R2`/`D` terminology into a universal ladder.
Operator support, routed composition, full-word support, commutator support,
and Lie depth remain typed separately.

## Reproducibility and Contracts

| Resource | Role |
|----------|------|
| [experiments/README.md](../experiments/README.md) | paper-owned scripts, result artifacts, and claim boundaries |
| [figures/README.md](../figures/README.md) | presentation renderers and manuscript image assets |
| [schemas/README.md](../schemas/README.md) | published compiler, SOFRS, SOFAUDIT, SOFAction, and Registry contracts |
| [registry/](../registry/) | immutable Registry releases and the separately versioned v2.1 candidate |
| [release-snapshots/](../release-snapshots/) | exact-byte historical inputs used by version-aware validators |
| [tools/README.md](../tools/README.md) | read-only snapshot, evidence-graph, release-manifest, and external-anchor checks |
| [CCS v2.1](../ccs/canonical_specification.md) | optional computational companion archive |

Presentation renderers are not scientific certificates. Cached observations
are not proofs. CCS v2.1 is optional archive material rather than a premise,
definition source, or claim authority for the independent papers.

## Source Authority

Authority depends on the kind of statement:

- The owning versioned manuscript determines definitions, hypotheses,
  theorem statements, ownership, and claim boundaries.
- Declared source inputs, versioned result records, and passing validators
  determine project-specific numerical values, censuses, digests, and
  computational certificates.
- Published Zenodo records determine release identity. The root release table
  indexes those immutable identities without promoting repository candidates
  to published versions.
- These public companions summarize the owning sources. CCS v2.1 supplies
  optional reproducibility records and historical context only.

A manuscript/evidence disagreement blocks release; prose precedence does not
resolve a numerical mismatch.

Cross-paper citations identify compatible objects; they do not import
hypotheses or promote support to composition, words, commutators, Lie depth,
moving fields, or represented genericity.

## Repository Boundary

The public documentation covers the published Papers I--XV architecture and
the independently scoped Papers XX--XXIII mathematical lines. Author-side planning,
exploratory research routing,
release migration status, and historical working notes are outside this public
documentation index.
