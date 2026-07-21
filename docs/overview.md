# RIME Program Overview

## One-Page Project Summary

**Public release scope.** This overview refers to the current public RIME
release: Papers I--XIII plus the Computational Canonical Specification (CCS).
The original three-paper trilogy remains the Rubik-centered foundation; Papers
IV--XIII extend it into the broader RIME program.

Published DOI records are immutable release snapshots. The repository may
carry explicitly labeled later manuscript candidates; the current Paper XII
repository copy is such a candidate and does not alter the published SOFRS
v1.0 contract.

RIME studies how spectral, transport, accessibility, and deformation structures
arise from finite-dimensional represented systems. The Rubik cube is used as a
finite, explicit, highly noncommutative laboratory, not as a puzzle-solving
object.

The program invariant is:

```text
Spectral geometry determines the objects.
Compatible sectorization is the interface.
Observable geometry is the invariant.
Accessibility geometry determines their behavior.
Genericity determines why the behavior is stable.
```

## Thirteen-Paper Arc

| Paper | Role | Main question |
|-------|------|---------------|
| Paper I | spectral formation | Why does the canonical Rubik spectrum have six rational layers? |
| Paper II | transport topology | Why does the resolved sector graph have its observed structure? |
| Paper III | accessibility separation | Why can composition see channels Lie generation misses? |
| Paper IV | collision geometry | Why are the six spectral layers a collision quotient? |
| Paper V | repair calculus | What repairs binary support after path-commutator cancellation? |
| Paper VI | deformation geometry | Why do sectors and accessibility walls move under generator variation? |
| Paper VII | generic completion | Why is accessibility generically stable? |
| Paper VIII | SOF object theory | What is the sectorized observable object? |
| Paper IX | observable dynamics | How do SOF observables evolve under deformation? |
| Paper X | observable pipeline | Why do different species share one observable pipeline? |
| Paper XI | observable classification | Which wall records and signatures belong to common observable classes? |
| Paper XII | diagnostic protocol | How does SOF produce reusable, claim-status-aware SOF Reports? |
| Paper XIII | comparison geometry | How can two SOF Reports be aligned and compared without conflating difference with defect? |

The dependency chain is:

```text
Arithmetic
  -> Transport
  -> Lie/composition separation
  -> Collision geometry
  -> Accessibility repair
  -> Generator-set deformation
  -> Generic completion
  -> SOF object theory
  -> Observable dynamics
  -> Universal observable pipeline
  -> Observable wall classification
  -> SOF diagnostic reporting
  -> SOF Report Alignment and comparison geometry
```

## Main Objects

The trilogy begins with the Rubik cubie representation and the generator
average

```text
A = (1 / |S|) sum_{s in S} rho(s).
```

The canonical spectrum collapses to six rational layers:

```text
Spec(A) = {1, 8/9, 7/9, 2/3, 5/9, 1/3}.
```

The QT/HT joint-sector decomposition refines this into nine sectors. Papers
II--III study transport and accessibility on these sectors. Papers IV--VII
then separate the post-trilogy geometry into four layers:

```text
fixed projection geometry      -> Paper IV
static accessibility calculus  -> Paper V
moving sector/wall geometry    -> Paper VI
generic completion theory      -> Paper VII
```

## Sectorized Observable Architecture

The common organizational architecture after Paper V is the Sectorized Observable
Framework (SOF). In the current papers this is used only as neutral terminology
for data of the form

```text
(V, {Q_i}, X),
```

where `V` is a finite-dimensional space, `{Q_i}` is a sector
projector family, and `X` is a chosen observable family. The observables
`R_1`, `R_2`, and `D` are defined relative to this data, not to the Rubik
representation alone.

SOF is a sectorized observable architecture. It does not prescribe a universal wall
theory; deformation geometry is chosen separately in each branch.

The lightweight registry lives in [SOF_REGISTRY.md](SOF_REGISTRY.md). The post-VII SOF
material is split by role:

- [SOF_OBJECTS.md](SOF_OBJECTS.md) for the static object layer;
- [SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md) for observable dynamics and walls;
- [SOF_REGISTRY.md](SOF_REGISTRY.md) for cross-species evidence, application routing, and
  claim-status boundaries.

Detailed applications, comparison controls, and external precedents are
documented in Papers X--XIII and their References sections. Internal
research-routing notes are intentionally not part of the public documentation
contract.

Further SOF theorem upgrades remain future work. The current theorem layers
remain paper-specific and claim-status gated.

## Repository Entry Points

| Resource | Public role |
|----------|-------------|
| `papers/paper1/`--`papers/paper13/` | canonical public manuscript sources and explicit revision candidates |
| `ccs/canonical_specification.md` | canonical trilogy computation and claim dependencies |
| [PROGRAM_MAP.md](PROGRAM_MAP.md) | program architecture, layer vocabulary, and Rubik/general boundary |
| [PAPER_SCOPE.md](PAPER_SCOPE.md) | per-paper ownership and source-of-truth order |
| [PROGRAM_PHILOSOPHY.md](PROGRAM_PHILOSOPHY.md) | Rubik-as-laboratory rationale |
| [CORE_INVARIANTS.md](CORE_INVARIANTS.md) | stable Rubik calibration data |
| [conventions.md](conventions.md) | coordinates, move encoding, composition, and tolerances |
| [SOF_OBJECTS.md](SOF_OBJECTS.md) | Paper VIII object-layer companion |
| [SOF_DEFORMATIONS.md](SOF_DEFORMATIONS.md) | Paper IX dynamic-layer companion |
| [SOF_REGISTRY.md](SOF_REGISTRY.md) | Paper X Registry companion and evidence map |
| [TRILOGY_OVERVIEW.md](TRILOGY_OVERVIEW.md) | trilogy-only introduction |
| `experiments/README.md` | support-script and claim map |
| `schemas/README.md` | published SOFRS, SOFAudit, and Registry contract map |

## Scope

RIME is not a cube-solving project. It does not study solving algorithms,
scramble search, neural solvers, sticker rendering, or game mechanics. The cube
is used as a finite representation-theoretic laboratory for spectral
accessibility.
