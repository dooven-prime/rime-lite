# Paper Scope

This file defines the public scope of the RIME paper series. It is a navigation
and boundary document: what each paper studies, which files support it, and
which claims should not be moved across paper boundaries.

Current public release: Papers I--XIII, with CCS v2 retained as an optional
non-paper archive. Paper XIV remains a development horizon. Publication
identities belong to the root release table; repository manuscripts may carry
explicitly labelled later-version candidates without mutating those releases.

The repository typed stack uses the frozen Registry v2.0 snapshot together
with SOFRS v2.0 and SOFAUDIT v2.0 versioned migrations. Their v1 artifacts
remain immutable.
Paper XII owns single-report protocol semantics, Paper XIII owns pairwise
alignment and sparse comparison, and Paper XIV owns downstream interpretation
and action semantics.

The active repository versions of Papers I--VII are frozen in maintenance
mode. Admissible changes are limited to explicit errata, build or certificate
repairs, and scope-narrowing boundary clarifications unless a paper is
explicitly reopened as a new version.

For the full narrative architecture, see `docs/PROGRAM_MAP.md`. For the
canonical Rubik numerical invariants used across the early papers, see
`docs/CORE_INVARIANTS.md`.

## Public Scope Matrix

| Paper | Object | Question |
|-------|--------|----------|
| Paper I | `A_18` and its spectral layers | What is the blockwise canonical spectrum, and which conditional arithmetic criteria apply? |
| Paper II | QT/HT sectors and transport tensor `K` | Why does the resolved sector graph have its observed structure? |
| Paper III | direct support graph and projected matrix composition | Why can graph reachability fail to compose at operator level? |
| Paper IV | fixed finite collision arrangements and conditional operator registration | How do affine-branch collisions form quotient layers, and when does an operator realization inherit that quotient? |
| Paper V | direct support, projected products, commutator support, and cutoff Lie depth | Why does Boolean support fail to determine commutator accessibility? |
| Paper VI | linearized commutativity/normality constraints and pointwise typed registrations | Which tangent directions preserve the declared constraints, and which samples pass the spectral gates? |
| Paper VII | incidence geometry, rank protection, and promotion limits | When do nonzero projected factors compose? |
| Paper VIII | marked static SOF objects, typed filtrations, and strict morphisms | What is the sectorized observable object, and what is preserved under strict morphisms? |
| Paper IX | typed dynamic fields, deformation charts, and observable trajectories | Which typed SOF fields can be compared continuously, and where can their walls occur? |
| Paper X | capability-aware compilation theory and SOF Registry evidence | Under which contracts can typed claims be compiled without manufacturing evidence or crossing carrier boundaries? |
| Paper XI | typed wall records, profile-relative coordinates, multi-label taxonomy, and local-model eligibility | How can admitted wall data be organized without redefining walls or assigning an intrinsic type to the source system? |
| Paper XII | versioned reporting protocol and epistemic boundary (SOFRS v2.0) | What does a compiled report represent, what remains the adapter's responsibility, and how are strict and analogue reports migrated with alignment-ready provenance? |
| Paper XIII | Audit Profiles, SOF Report Alignment, sparse typed comparison maps, and fixed-frame pseudometrics | How can two SOF Reports be aligned and compared without manufacturing unavailable coordinates? |

Development horizon:

| Paper | Object | Question |
|-------|--------|----------|
| Paper XIV | `SOFActionObject = (Delta_audit, K_ctx, Pi_policy, I_interp, A_cand)` | Under which admitted `ActionContext` and `PolicyProfile` can an audit difference be interpreted, and which bounded candidates are supported? |

The artifact chain is:

```text
typed SOF objects and findings
  -> .sofreport
  -> .sofaudit
  -> .sofaction
```

The first artifact describes one declared realization, the second compares two
aligned reports, and the third interprets the immutable audit under an admitted
`ActionContext` and the single normative `PolicyProfile`. A `.sofaction`
artifact stops at bounded candidates; selection, authorization, observation,
and effect belong to separate downstream contracts. No downstream artifact may
be imported backward into the preceding layer.

The expanded sections keep the objects and claim boundaries of Papers I--VII
separate. Their shared computational realization does not create a formal
dependency chain. Connections are typed interfaces: a neighboring output may
be reused only after the receiving paper redeclares its object, hypotheses,
realization, and claim status. In particular, spectral layers, registered QH
sectors, direct support, routed composition, words, commutators, and Lie depth
are not stages of one automatically promoted object.

## Paper I: Spectral Sector Decomposition

**Object.**

```text
A_18 = (1/18) sum_{s in S} rho(s)
```

where `S` is the standard 18 face-turn generator set.

**Question.** What is the canonical averaging operator's blockwise spectral
census, and which conditional arithmetic criteria apply to it?

**In scope.**

- 228-dimensional cubie representation.
- Four physical blocks: `cp(64)`, `ep(144)`, `co(8)`, `eo(12)`.
- Six canonical spectral layers:

```text
{1, 8/9, 7/9, 2/3, 5/9, 1/3}.
```

- Registered rational parametrization `lambda = 1 - k/9`, with
  `k in {0,1,2,3,4,6}`.
- The registered missing `k=5` layer.
- Exact Hamming-scheme and face-incidence reductions for the two permutation
  blocks.
- Explicitly computational corner- and edge-orientation block spectra.
- Compression-trace rationality equivalence and partition integrality as a
  sufficient certificate format; the canonical face partition fails that
  certificate.
- Block support of each spectral layer.
- A registered generator-family arithmetic contrast, without exact
  minimal-polynomial promotion.

**Primary files.**

- `papers/paper1/Paper I.md`
- `experiments/paper1/validation/spectral_ladder.py`
- `experiments/paper1/validation/k_absence.py`
- `experiments/paper1/validation/block_composition.py`
- `experiments/paper1/validation/symmetry_breaking.py`

## Paper II: Noncommutative Transport Topology

**Object.**

```text
K_{alpha,beta} = max_g || P_alpha rho(g) P_beta ||.
```

**Question.** Why does the nine-sector transport graph have its observed sparse structure?

**In scope.**

- Nine QT/HT joint-spectral sectors from `Center{A_18, QT_all, HT_all}`.
- Sector terminology: minimal QT/HT joint eigenspaces, not irreducible components.
- Numerically registered QT/HT joint clusters near 9 rational `(q,h)` points.
- Exact finite arithmetic for the explicitly declared rational nine-point
  arrangement, separate from promotion to an exact Rubik joint spectrum.
- Conditional collision quotient: if the registered table is the exact QT/HT
  joint spectrum with the stated projectors and ranks, then
  `A_18 = (2/3)QT_all + (1/3)HT_all` gives the six canonical layers as its
  `alpha=2/3` quotient.
- Exact affine-branch collision geometry for the declared arrangement, with
  `alpha=2/3` as its unique maximal interior collapse.
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
- `experiments/paper2/validation/joint_spectral_geometry.py`
- `experiments/paper2/validation/collision_geometry.py`
- `experiments/paper2/validation/primitive_sectors.py`
- `experiments/paper2/validation/transport_graph.py`
- `experiments/paper2/validation/supp_nc.py`
- `experiments/paper2/validation/ep_algebra.py`
- `experiments/paper2/validation/generator_universality.py`

## Paper III: Support Graph vs Matrix Composition

**Object.**

```text
T_ikj(g2,g1) = Q_i rho(g2) Q_k rho(g1) Q_j.
```

**Question.** When does a two-step path in the direct support graph represent a
nonzero projected matrix composition, and what obstructs that promotion?

**In scope.**

- Direct generator-support graph on the nine QH sectors.
- Projected two-step composition operators.
- The theorem that support-graph paths do not imply nonzero matrix products.
- Image-kernel and physical-block obstructions to composition.
- Five canonical graph-only triples whose adjacent support blocks are nonzero
  while every tested projected two-generator product vanishes.
- Conditions under which graph reachability can be promoted to operator
  composition remain open.

**Primary files.**

- `papers/paper3/Paper III.md`
- `experiments/paper3/validation/composition_obstruction.py`
- `tests/test_transport.py`

## Paper IV: Collision Geometry of Joint Spectra

**Object.** A fixed finite arrangement
`P={(q_i,h_i)} subset R^2` observed through
`L_alpha(q,h)=alpha*q+(1-alpha)*h`.

**Claim layers.**

- General collision and spectral-quotient results are exact theorems under
  their stated finite-point or commuting-Hermitian hypotheses.
- The census of the displayed rational arrangement `P_9` is exact finite
  arithmetic and is complete on `alpha in [0,1]`.
- Matching the Rubik QT/HT computation to `P_9` is computational evidence,
  supported by commutator, projector, joint-eigen, raw-to-table, and
  coordinate-matched tolerance diagnostics.
- The exact Rubik collision-quotient statement is conditional on exact
  registration; machine-zero residuals do not establish that promotion.
- Moving arrangements, normal spectral charts, and Sigma hierarchies are a
  research program owned by Paper VI, not results of Paper IV.

**Primary files.**

- `papers/paper4/Paper IV.md`
- `experiments/paper4/validation/rubik_collision_quotient.py`
- `experiments/paper4/validation/rubik_joint_spectrum_registration.py`
- `experiments/paper4/validation/v59_collision_vs_transport.py`

## CCS v2: Computational Companion and Status Archive

**Object.** CCS v2 is optional human-readable archive material for Papers
I--II and the historical first combined release. It is not a paper, theorem
source, semantic authority, executable certificate, or prerequisite for
Papers I--III.

**In scope.**

- canonical numerical tables;
- experiment-to-claim mapping;
- stability checks;
- negative controls;
- figure registry;
- implementation notes;
- archive-status register;
- open problems and explicitly labelled historical records.

**Primary file.**

- `ccs/canonical_specification.md`

## Cross-Cutting Controls and Boundaries

| Topic | Current scope |
|-------|---------------|
| `N=2` pocket cube | Archived first-version graph/kappa control; not a current compositional-morphism certificate |
| canonical `S_3` prototypes | Historical controls; not current Paper III composition evidence |
| generator-family studies | Boundary and deformation evidence; do not state as universal invariance without qualification |
| threshold and seed sweeps | Numerical stability evidence |
| Dirac/spectral-triple probes | Archived first-version interpretation; not current Paper III claim support |
| canonical mediation statistics | Historical support-graph witness convention; not an operator-composition invariant |

## Out of Scope

This repository does not study:

- cube solving algorithms;
- Kociemba search, pruning tables, BFS, or IDA*;
- sticker-level rendering or game interfaces;
- neural-network solvers;
- unrelated historical modules removed from `rime-lite`;
- claims about all finite groups or all noncommutative representations unless explicitly marked as conjectural or open.

Avoid Phase-1 subgroup explanations for the spectral boundary. The corrected interpretation is the co-block support boundary described in Paper I and CCS, not Phase-1 invariance.

## Authority Boundaries

Authority is typed rather than represented by one universal precedence list:

- **Semantic authority:** the owning versioned manuscript determines
  definitions, hypotheses, theorem statements, ownership, and claim
  boundaries. Public interface documents summarize those meanings; planning
  and archive notes do not replace them.
- **Evidence authority:** declared source inputs, the owning versioned result
  record, and its passing validator determine public numerical values,
  censuses, digests, and computational certificates. Manuscript prose states
  the meaning and scope of those claims but does not override a conflicting
  result record.
- **Release-identity authority:** a published Zenodo record fixes the title,
  authorship, version, files, DOI, and date of that historical release. The
  root release table indexes those identities; a repository candidate does not
  mutate them.

A disagreement between manuscript prose and its owning evidence blocks a new
release rather than being resolved by prose precedence.
`ccs/canonical_specification.md` remains an optional Paper I--II computation
and history index. `HISTORY.md` records why a historical statement was
superseded; neither file proves a replacement theorem.
