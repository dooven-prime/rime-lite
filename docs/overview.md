# RIME Program Overview

## One-Page Project Summary

**Public release scope.** This overview refers to the current public RIME
release: Papers I--VII plus the Computational Canonical Specification (CCS).
The original three-paper trilogy remains the Rubik-centered foundation; Papers
IV--VII extend it into the broader RIME program.

RIME studies how spectral, transport, accessibility, and deformation structures
arise from finite-dimensional represented systems. The Rubik cube is used as a
finite, explicit, highly noncommutative laboratory, not as a puzzle-solving
object.

The program invariant is:

```text
Spectral geometry determines the objects.
Accessibility geometry determines their behavior.
Genericity determines why the behavior is stable.
```

## Seven-Paper Arc

| Paper | Role | Main question |
|-------|------|---------------|
| Paper I | spectral formation | Why does the canonical Rubik spectrum have six rational layers? |
| Paper II | transport topology | Why does the resolved sector graph have its observed structure? |
| Paper III | accessibility separation | Why can composition see channels Lie generation misses? |
| Paper IV | collision geometry | Why are the six spectral layers a collision quotient? |
| Paper V | repair calculus | What repairs binary support after path-commutator cancellation? |
| Paper VI | deformation geometry | Why do sectors and accessibility walls move under generator variation? |
| Paper VII | generic completion | Why is accessibility generically stable? |

The dependency chain is:

```text
Arithmetic
  -> Transport
  -> Lie/composition separation
  -> Collision geometry
  -> Accessibility repair
  -> Generator-set deformation
  -> Generic completion
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

## Sectorized Observable Language

The common organizational language after Paper V is the Sectorized Observable
Framework (SOF). In the current papers this is used only as neutral terminology
for data of the form

```text
(V, {Q_i}, X),
```

where `V` is a finite-dimensional representation space, `{Q_i}` is a sector
projector family, and `X` is a chosen observable family. The observables
`R_1`, `R_2`, and `D` are defined relative to this data, not to the Rubik
representation alone.

A full SOF registry and axiomatization is future work. The current theorem
layers remain paper-specific and claim-status gated.

## Repository Entry Points

- `papers/paper1/`--`papers/paper7/` contain the manuscript sources.
- `ccs/canonical_specification.md` records the canonical computational data for
  the trilogy and bridge notes.
- `docs/PROGRAM_MAP.md` gives the detailed Papers I--VII architecture.
- `docs/PROGRAM_PHILOSOPHY.md` records the Rubik-as-laboratory philosophy.
- `docs/TRILOGY_OVERVIEW.md` preserves the original trilogy-focused overview.
- `experiments/README.md` maps support scripts to paper claims.

## Scope

RIME is not a cube-solving project. It does not study solving algorithms,
scramble search, neural solvers, sticker rendering, or game mechanics. The cube
is used as a finite representation-theoretic laboratory for spectral
accessibility.
