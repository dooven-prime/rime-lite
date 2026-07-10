# Experiments - Reproducibility Map

This directory contains deterministic support scripts and diagnostics for the
RIME program. The public-facing directory has four separate responsibilities:

1. `experiments/paperN/` contains paper-facing computations and claim support.
2. `experiments/quantum/` contains quantum-gate SOF portability diagnostics.
3. `experiments/cross_ref/` contains related-work positioning diagnostics.
4. Top-level figure scripts are local figure-production tools; manuscripts use
   frozen figure artifacts under `figures/`.

Tests under `tests/` verify package invariants and are not part of this
directory.

Public release scope: Papers I--X plus CCS. Paper XI--XII scripts, when
present, are horizon diagnostics and are not part of the current public release
claim set.

All public support scripts use fixed seeds where randomness is present
(`np.random.seed(42)` unless otherwise stated).

## Directory Map

```text
experiments/
|-- paper1/                 Paper I: spectral origin
|-- paper2/                 Paper II: transport topology and QT/HT sectors
|-- paper3/                 Paper III: Lie/composition accessibility
|-- paper4/                 Paper IV: fixed collision geometry
|-- paper5/                 Paper V: static accessibility repair calculus
|-- paper6/                 Paper VI: generator-set moduli and wall structure
|   `-- archive/            historical provenance scripts only
|-- paper7/                 Paper VII: generic completion and SOF diagnostics
|-- paper9/                 Paper IX: observable dynamics diagnostics
|-- paper10/                Paper X: registry evidence and SOF portability
|-- quantum/                quantum-gate SOF diagnostics
|-- cross_ref/              related-work diagnostics, not theorem sources
`-- trilogy_style/          shared styling utilities used by local figure scripts
```

The tables below keep these roles separate. A script listed under one role
should not be treated as evidence for another role unless the manuscript
explicitly says so.

## Paper I - Spectral Origin

| Script | Verifies |
|--------|----------|
| `experiments/paper1/spectral_ladder.py` | six-layer spectrum, dimensions, block support |
| `experiments/paper1/k_absence.py` | absence of the `k=5` spectral layer |
| `experiments/paper1/block_composition.py` | per-layer block support |
| `experiments/paper1/projector_algebra.py` | projector idempotence, orthogonality, trace dimensions |
| `experiments/paper1/co_eo_analytic_spectrum.py` | CO/EO analytic spectrum and face-symmetric block law |
| `experiments/paper1/isotypic_decomposition.py` | 51 isotypic components and the multiplicity reservoir |
| `experiments/paper1/symmetry_breaking.py` | verified broken-face irrational families |

## Paper II - Transport Topology

| Script | Verifies |
|--------|----------|
| `experiments/paper2/joint_spectral_geometry.py` | nine rational QT/HT joint-spectrum points and the `A_18` collision quotient |
| `experiments/paper2/collision_geometry.py` | affine-branch collision classification, no shadow collisions, unique maximal collapse |
| `experiments/paper2/primitive_sectors.py` | nine sectors from `Center{A, QT_all, HT_all}` |
| `experiments/paper2/transport_graph.py` | transport matrix, symmetry, and graph edges |
| `experiments/paper2/supp_nc.py` | per-block noncommutativity localization |
| `experiments/paper2/ep_algebra.py` | EP block algebra structure |
| `experiments/paper2/commutant_pi_map.py` | commutant restriction map audit |
| `experiments/paper2/generator_universality.py` | generator-family transport-topology comparison |

## Paper III - Lie Accessibility

| Script | Verifies |
|--------|----------|
| `experiments/paper3/t7_detection.py` | T7 morphisms and two-step compositional reachability |
| `experiments/paper3/kappa_depth.py` | gradient/curvature accessibility hierarchy |
| `experiments/paper3/transport_9sector.py` | nine-sector transport tensor and accessibility hierarchy |
| `experiments/paper3/t7_refined.py` | `S3 nat+reg` prototype comparison |
| `experiments/paper3/t7_necessity.py` | shared-irrep necessity check |
| `experiments/paper3/transport_closure.py` | Lie accessibility hierarchy audit |
| `experiments/paper3/kappa_hierarchy_search.py` | kappa hierarchy as a search diagnostic |
| `experiments/paper3/t7_reg_reg.py` | `S3 reg+reg` structural contrast |

## Paper IV - Collision Geometry

| Script | Verifies |
|--------|----------|
| `experiments/paper4/rubik_collision_quotient.py` | exact finite-point collision quotient, no shadow collisions, unique maximal collapse at `alpha=2/3` |
| `experiments/paper4/v59_collision_vs_transport.py` | `V_5/9` collision triangle versus direct transport chain `S5-S6-S7` |

## Paper V - Minimal Accessibility Data

| Script | Verifies |
|--------|----------|
| `experiments/paper5/s4_r1_r2_depth.py` | S4-3gen-B `R1`/`R2`/depth example |
| `experiments/paper5/path_commutator_cancellation.py` | binary-support counterexample with path-commutator cancellation |
| `experiments/paper5/complement_explosion.py` | support/scalar complement obstruction model and `R2` bridge repair |
| `experiments/paper5/noncomplement_obstruction_enumeration.py` | finite support-level non-complement obstruction families |
| `experiments/paper5/matrix_nondegeneracy.py` | single-term bridge matrix audit and rank-protection check |

## Paper VI - Commutativity Walls and Spectral Phase Transitions

| Script | Verifies |
|--------|----------|
| `experiments/paper6/tangent_commutator_map.py` | computational local tangent model at the canonical point |
| `experiments/paper6/fragmentation_walls.py` | fragmentation, gauge direction, `R1` jumps, Wall Origin Principle |
| `experiments/paper6/generator_moduli_space.py` | global generator-set moduli tables and bifurcation snapshots |
| `experiments/paper6/phase_utils.py` | shared utilities for Paper VI phase tables |
| `experiments/paper6/wall_crossing_summary.py` | compact theorem-support table for accessibility wall crossings |
| `experiments/paper6/archive/` | historical provenance scripts; not part of canonical reproducibility |

## Paper VII - Generic Accessibility Completion

| Script | Status |
|--------|--------|
| `experiments/paper7/atlas_r2_boundary.py` | completion-boundary atlas and exact `(R1,R2)->D` hash audit |
| `experiments/paper7/incidence_variety_codim.py` | incidence-variety codimension computation |
| `experiments/paper7/rank_protected_bridge_audit.py` | rank-protected bridge audit for generic completion evidence |
| `experiments/paper7/markov_graph_sof.py` | Markov and graph SOF portability diagnostic for Appendix C |

Paper VII scripts support the published generic-completion and incidence
boundary paper. Exploratory or historical variants live under
`experiments/paper7/archive/`.

## Quantum SOF Diagnostics

| Script | Status |
|--------|--------|
| `experiments/quantum/quantum_accessibility_universality.py` | Pauli/Clifford/Universal gate-set R1/R2/D sanity check |

This script supports Sectorized Observable Framework portability checks. It is a
cross-species diagnostic and appendix-level sanity check, not a standalone
theorem source.

## Cross-Reference Diagnostics

| Script | Status |
|--------|--------|
| `experiments/cross_ref/emlp_morphosymm_character_diagnostic.py` | related-work diagnostic for commutant, character-idempotent, and symmetry-adapted coordinate comparisons |
| `experiments/cross_ref/grokking_rate_separation.py` | related-work diagnostic for ridge-regression row/null-space rate separation and Paper IX deformation dynamics |

These scripts support related-work positioning. They are not theorem sources
unless a manuscript explicitly cites them as claim support.

## Paper VIII - Sectorized Observable Framework

Paper VIII is primarily object-theoretic. Its public reproducibility layer is
the manuscript proof layer plus figure assets. The top-level
`experiments/paper8_figures.py` script regenerates the schematic figures, but
it is a figure-production tool rather than numerical theorem support.

## Paper IX - Observable Dynamics

| Script | Status |
|--------|--------|
| `experiments/paper9/nn_activation_sof.py` | activation-induced sectorization and fixed-weight R1/R2/frozen diagnostic |
| `experiments/paper9/nn_training_sof_tau.py` | training-coupled K0/K1/K2 time-scale diagnostic |
| `experiments/paper9/rate_hierarchy.py` | rate hierarchy, rate collapse, and sectorization-sensitivity diagnostic |
| `experiments/paper9/state_mixing_fft.py` | state-mixing, oscillation, and cross-domain rate-separation summary |
| `experiments/paper9/plateau_under_qt_perturbation.py` | QT generator-weight plateau diagnostic; default mode postprocesses cached data |

Paper IX scripts are diagnostics for observable dynamics. They are the current
home for rate hierarchy, wall dynamics, and deformation-species experiments;
claim status is recorded script by script.

## Paper X - Universal Observable Pipeline and SOF Registry

| Script | Status |
|--------|--------|
| `experiments/paper10/mechanism_separation_theorem.py` | constructive H3 positive control: mechanism separation gives proxy-rate separation, `30 << 1380` |
| `experiments/paper10/control_pde_combinatorial_sof.py` | control/PDE/combinatorial SOF portability probe: Kalman ranks, Laplacian subdomain transport, and graph-coloring diagnostics |
| `experiments/paper10/ncg_spectral_triple_sof.py` | finite NCG-inspired spectral-triple SOF probe: central Connes-distance obstruction and two ordered T7-style bridges |
| `experiments/paper10/rubik_wild_type34_audit.py` | Rubik QT/HT wild Type III/IV audit: `288` Type III cancellations and `528` Type IV bridge-level incidence products |
| `experiments/paper10/registry_evidence.py` | registry evidence summary: mechanism-separated control, Xu/RIME/NN rates, Yang/RIME plateau contrast, and quantum Clifford non-Rubik D-repair |
| `experiments/paper10/tau_quantum_graph_yang.py` | negative/boundary tau probes for quantum interpolation, graph rewiring, and Yang-like state mixing |

Paper X scripts are registry evidence. They support the SOF Registry as a
cross-species comparison object. Mechanism separation is constructive
proxy-layer support; proxy-to-shadow and `tau(D)` bridges remain open.

## Figure Production Scripts

Top-level scripts such as `experiments/paper*_figures.py`,
`experiments/ccs_figures.py`, and `experiments/trilogy_overview.py` are local
production tools for figure assets. They are not part of the public
reproducibility index unless a paper explicitly cites them as support scripts.
Manuscripts reference frozen figures under `figures/`; public support scripts
do not regenerate them.

## Usage

Run single support scripts from the repository root:

```bash
python experiments/paper4/rubik_collision_quotient.py
python experiments/paper6/tangent_commutator_map.py
python experiments/paper7/rank_protected_bridge_audit.py
python experiments/paper7/markov_graph_sof.py
python experiments/paper9/rate_hierarchy.py
python experiments/paper10/registry_evidence.py
```

Run the quantum SOF diagnostic from the repository root:

```bash
python experiments/quantum/quantum_accessibility_universality.py
```

Run package invariants:

```bash
python tests/run_all_tests.py
```

## Reproducibility Notes

- Experiments are deterministic unless explicitly documented otherwise.
- Manuscripts consume frozen figure files under `figures/`; support scripts do
  not regenerate figures.
- Historical scripts in `archive/` directories are provenance records, not
  canonical claim support.
