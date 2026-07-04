# RIME Trilogy + CCS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21108197.svg)](https://doi.org/10.5281/zenodo.21108197)

This directory is the reader-facing entry point for the original three-paper
RIME trilogy and its Computational Canonical Specification (CCS).

The trilogy studies spectral, transport, and accessibility structures in the
228-dimensional Rubik cubie representation. The Rubik cube is not treated as a
solving problem; it is used as a finite, explicit, highly noncommutative
representation-theoretic laboratory.

The archived trilogy + CCS release is:

[The RIME Trilogy: Spectral, Transport, and Accessibility Structures in Finite Group Representations](https://doi.org/10.5281/zenodo.21108197)

## Reading Path

| Component | PDF | Source | Main question |
|-----------|-----|--------|---------------|
| Paper I | [paper1_arxiv.pdf](../papers/paper1/paper1_arxiv.pdf) | [Paper I.md](../papers/paper1/Paper%20I.md) | Why does the averaging operator have a rational six-layer spectrum? |
| Paper II | [paper2_arxiv.pdf](../papers/paper2/paper2_arxiv.pdf) | [Paper II.md](../papers/paper2/Paper%20II.md) | Why does the nine-sector transport graph have its observed sparse structure? |
| Paper III | [paper3_arxiv.pdf](../papers/paper3/paper3_arxiv.pdf) | [Paper III.md](../papers/paper3/Paper%20III.md) | Why can discrete composition create channels invisible to Lie-generated accessibility? |
| CCS | [ccs_arxiv.pdf](ccs_arxiv.pdf) | [canonical_specification.md](canonical_specification.md) | Which numerical objects, figures, stability checks, and claim dependencies are canonical? |

## Trilogy Arc

```text
Paper I      spectral sector decomposition
    ->
Paper II     noncommutative transport topology
    ->
Paper III    Lie-generated vs compositional accessibility
    ->
CCS          canonical numerical specification
```

Paper I constructs the six-layer rational spectrum of the Rubik averaging
operator. Paper II refines the spectral layers into nine QT/HT joint-spectral
sectors and studies generator transport between them. Paper III compares
Lie-generated accessibility with discrete compositional accessibility and
isolates the T7 phenomenon.

The CCS is the canonical lookup document for the trilogy. It records the
numerical invariants, figure directory, verification tables, tolerance policy,
and claim-status map used by Papers I--III.

## One-Screen Summary

<p align="center">
  <img src="../figures/trilogy_overview.png" width="100%">
</p>

<p align="center">
  <em>The trilogy cascade: spectral layers, transport topology, and composition-only accessibility.</em>
</p>

## Core Objects

The central representation is

```text
rho : G -> U(228),
```

where `G` is the Rubik cube group acting on the cubie representation. The
canonical generator average is

```text
A = (1 / |S|) sum_{s in S} rho(s),
```

with `S` the standard 18 face-turn generator set.

The canonical spectral layers are

```text
Spec(A) = {1, 8/9, 7/9, 2/3, 5/9, 1/3}.
```

The QT/HT joint decomposition gives nine sectors `S1`--`S9`. Paper II studies
transport between these sectors via

```text
K_{alpha,beta} = max_g || P_alpha rho(g) P_beta ||.
```

Paper III studies Lie accessibility using logarithmic generators

```text
A_g = log rho(g).
```

The trilogy's common structural theme is:

```text
spectral projector geometry is not contained in Lie tangent geometry.
```

## Canonical Values

| Quantity | Canonical value |
|----------|-----------------|
| representation dimension | 228 |
| physical blocks | `cp`, `ep`, `co`, `eo` |
| spectral layers | 6 |
| QT/HT joint-spectral sectors | 9 |
| direct transport edges, undirected | 10 |
| T7 morphisms in Rubik `N=3` | 5 |
| T7 morphisms in pocket cube `N=2` | 0 |
| isotypic components | 51 |
| multiplicity reservoir | one component |

## Reproducibility Entry Points

Run from the repository root:

```bash
python tests/run_all_tests.py
python tests/run_slow_tests.py
python papers/validate_registry.py
```

Representative trilogy support scripts:

```bash
python experiments/paper1/spectral_ladder.py
python experiments/paper2/primitive_sectors.py
python experiments/paper2/transport_graph.py
python experiments/paper3/t7_detection.py
```

The full CCS source is [canonical_specification.md](canonical_specification.md).

## Scope

This is not a cube-solving project. It does not study solving algorithms,
search heuristics, pruning tables, sticker rendering, or neural solvers. The
cube is used only as a finite representation-theoretic testbed.

For the broader RIME program beyond the trilogy, use the repository root
[README](../README.md).

## Citation

```bibtex
@misc{chen_rime_trilogy_2026,
  author       = {Chen, WuJun},
  title        = {The RIME Trilogy: Spectral, Transport, and Accessibility
                  Structures in Finite Group Representations},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.21108197},
  url          = {https://doi.org/10.5281/zenodo.21108197}
}
```
