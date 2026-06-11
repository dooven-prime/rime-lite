# Paper Scope

This file defines the current scope of the RIME trilogy. It is a navigation and boundary document: what each paper studies, which files support it, and which claims should not be moved across paper boundaries.

The trilogy is built around one pipeline:

```text
rho(g) -> A_18 -> spectral layers -> primitive sectors -> transport -> Lie/composition gap
```

## Paper I: Spectral Sector Decomposition

**Object.**

```text
A_18 = (1/18) sum_{s in S} rho(s)
```

where `S` is the standard 18 face-turn generator set.

**Question.** Why does the averaging operator have a rational six-layer spectrum despite noncommuting generators?

**In scope.**

- 228-dimensional cubie representation.
- Four physical blocks: `cp(64)`, `ep(144)`, `co(8)`, `eo(12)`.
- Six canonical spectral layers:

```text
{1, 8/9, 7/9, 2/3, 5/9, 1/3}.
```

- Rational spectral law `lambda = 1 - k/9`, with `k in {0,1,2,3,4,6}`.
- The missing `k=5` layer.
- Partition-integrality mechanism for rationality under the stated hypotheses.
- Block support of each spectral layer.
- Isotypic decomposition: 51 components, 50 multiplicity-free, 1 reservoir.
- Symmetry-breaking examples that leave the rational regime.

**Primary files.**

- `papers/paper1/Paper I.md`
- `experiments/paper1/spectral_ladder.py`
- `experiments/paper1/k_absence.py`
- `experiments/paper1/block_composition.py`
- `experiments/paper1/isotypic_decomposition.py`
- `experiments/paper1/symmetry_breaking.py`

## Paper II: Noncommutative Transport Topology

**Object.**

```text
K_{alpha,beta} = max_g || P_alpha rho(g) P_beta ||.
```

**Question.** Why does the nine-sector transport graph have its observed sparse structure?

**In scope.**

- Nine primitive sectors from `Center{A_18, QT_all, HT_all}`.
- Primitive sector terminology: minimal center-joint eigenspaces, not irreducible components.
- Transport tensor and `K` matrix between sectors.
- 10 undirected direct transport edges.
- Transport-active noncommutative block support `Supp_nc`.
- Type I edges: shared `Supp_nc` noncommutative transport.
- Type II edge: the CP commutative-permutation channel S8 <-> S9.
- Hub structure: S6 primary hub, S7 secondary hub, S1 isolated.
- EP algebra structure:

```text
A_EP ~= M_2(C)^4 + M_1(C)^4.
```

- Refinement obstruction and the role of noncommutative simple components.
- The boundary between representation-fixed, center-determined, and generator-conditioned structure.

**Primary files.**

- `papers/paper2/Paper II.md`
- `experiments/paper2/primitive_sectors.py`
- `experiments/paper2/transport_graph.py`
- `experiments/paper2/supp_nc.py`
- `experiments/paper2/ep_algebra.py`
- `experiments/paper2/generator_universality.py`

## Paper III: Accessibility Structure

**Object.**

```text
kappa_d = max || P_alpha C_d P_beta ||
```

where `C_d` ranges over depth-`d` Lie-generated expressions, and

```text
A_g = log rho(g).
```

**Question.** Why can discrete composition create accessibility channels that are invisible to Lie-generated accessibility?

**In scope.**

- Lie generators from matrix logarithms.
- Schur-locality and block-preserving Lie-generated support.
- `kappa_0` and `kappa_1` diagnostics.
- Formal distinction between:
  - direct transport,
  - Lie-generated accessibility,
  - compositional accessibility.
- Hybrid sectors and transport-active hybrid mediation.
- T7 morphisms:
  - `K = 0`,
  - `kappa_0 = 0`,
  - `kappa_1 = 0`,
  - length-2 compositional reachability through a hybrid sector,
  - higher-depth Lie obstruction from block support.
- Rubik `N=3`: 5 T7 morphisms, all cross-block.
- Pocket cube `N=2`: 0 T7 morphisms.
- Canonical `S_3` systems: 0 T7 morphisms, used as negative controls.
- Canonical witness selection for mediation statistics, kept separate from T7 pair detection.

**Primary files.**

- `papers/paper3/Paper III.md`
- `experiments/paper3/t7_detection.py`
- `experiments/paper3/kappa_depth.py`
- `experiments/paper3/transport_9sector.py`
- `experiments/paper3/transport_closure.py`
- `experiments/paper3/t7_refined.py`
- `experiments/paper3/t7_reg_reg.py`

## CCS: Computational Canonical Specification

**Object.** The CCS is the canonical numerical and methodological supplement for all three papers.

**In scope.**

- canonical numerical tables;
- experiment-to-claim mapping;
- stability checks;
- negative controls;
- figure registry;
- implementation notes;
- claim-status register.

**Primary file.**

- `ccs/canonical_specification.md`

## Cross-Cutting Controls and Boundaries

| Topic | Current scope |
|-------|---------------|
| `N=2` pocket cube | Negative control: 0 T7 morphisms |
| canonical `S_3` prototypes | Negative controls: 0 T7 morphisms under the canonical center |
| generator-family studies | Boundary and deformation evidence; do not state as universal invariance without qualification |
| threshold and seed sweeps | Numerical stability evidence |
| Dirac/spectral-triple probes | Structural probes, not a claim of full Connes spectral geometry |
| canonical mediation statistics | Derived from a witness-selection convention, not part of the T7 invariant itself |

## Out of Scope

This repository does not study:

- cube solving algorithms;
- Kociemba search, pruning tables, BFS, or IDA*;
- sticker-level rendering or game interfaces;
- neural-network solvers;
- unrelated historical modules removed from `rime-lite`;
- claims about all finite groups or all noncommutative representations unless explicitly marked as conjectural or open.

Avoid Phase-1 subgroup explanations for the spectral boundary. The corrected interpretation is the co-block support boundary described in Paper I and CCS, not Phase-1 invariance.

## Source-of-Truth Order

When documents disagree, use this order:

1. current paper markdown in `papers/paper*/`;
2. `ccs/canonical_specification.md`;
3. `papers/canonical_registry.json` and `papers/notation_registry.yaml`;
4. tests and experiment scripts;
5. overview and navigation documents such as this file.
