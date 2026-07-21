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

Public release scope: Papers I--XIII plus CCS. Unreleased paper-stage
experiments are intentionally omitted from this public reproducibility map
until their manuscripts and artifact contracts are frozen.

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
|-- paper11/                Paper XI: observable wall records and taxonomy
|-- paper12/                Paper XII: SOF diagnostic protocol and reports
|-- paper13/                Paper XIII: SOF Report Alignment and comparison geometry
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
| `experiments/quantum/quantum_gateset_t_blind_control.py` | computational-basis gate-log negative control: Clifford and Universal T/S variants have identical support, bridge, and depth shadows |
| `experiments/quantum/quantum_state_trajectory_sof.py` | trajectory-induced STAB/MAGIC coarse graining: T-sensitive transition observable changes from absent to complete two-state off-diagonal support |

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


## Paper XI - Observable Classification Theory

| Script | Status |
|--------|--------|
| `experiments/paper11/cross_species_wall_audit.py` | cross-species wall diagnostics for the observable taxonomy; no ADE classification theorem is claimed |
| `experiments/paper11/spectral_ade_collision.py` | Rubik smooth spectral local-model audit: 16 pairwise A1-type closures plus sampling-dependent simultaneous pair-gap responses |
| `experiments/paper11/discriminant_bifurcation_map.py` | auxiliary 2D commutativity-discriminant slice; one hit on the chosen `20 x 20` evaluation grid |
| `experiments/paper11/wall_density_registry.py` | wall-density table for the frozen 15-entry v1 taxonomy sample |
| `experiments/paper11/wall_record_census.py` | frozen v1 24-record multi-label coverage audit; Class A remains the original sampling gap |
| `experiments/paper11/invariant_redundancy.py` | definition-compatible 166-configuration redundancy audit; three PCA components explain both 90% and 95% for the tested ensemble, without claiming an invariant basis |
| `experiments/paper11/an_adjacency.py` | Appendix A boundary audit: block-restricted eigenbranch continuation finds no A2-to-two-A1 split candidate on the tested slices |
| `experiments/paper11/wall_trajectory.py` | Appendix B boundary audit: sampled observable-status trajectories for GridWorld, SIR, and weighted graph controls; counts status changes rather than static frozen pairs |
| `experiments/paper11/repair_persistence_quantum.py` | CNOT-strength interpolation audit: repair threshold `0.55`, persistence `p_W=0.45`, and post-activation stability |
| `experiments/paper11/piecewise_smooth_activation_wall.py` | activation-wall boundary audit: ReLU kink, GeLU control, and top-k rank-selection diagnostic |
| `experiments/paper11/validation/degenerate_endpoint_collision.py` | v1.1 smooth endpoint witness with two transverse A1-type spectral closures |
| `experiments/paper11/validation/percolation_wall.py` | v1.1 nested-threshold percolation witness for a discrete monotone repair wall |
| `experiments/paper11/validation/kuramoto_wall.py` | v1.1 matched-frequency control for a smooth negative-orientation freezing wall |
| `experiments/paper11/validation/grn_toggle_wall.py` | v1.1 knockout structure-wall witness; the earlier low-volume CLE noise-wall interpretation is explicitly withdrawn after SSA control |
| `experiments/paper11/validation/wall_robustness_audit.py` | unified robustness checks for the four added wall profiles |
| `experiments/paper11/validation/wall_record_census_v2.py` | independently generated v1.1 census: 28 records, 19 eligible records, and 38 class memberships |
| `experiments/paper11_figures.py` | generates Figure 1 wall-record pipeline, Figure 2 six-class taxonomy, and Figure 3 wall-density/repair-persistence evidence |

Paper XI scripts are taxonomy evidence and boundary audits. The v1.1 extension
meets the predeclared finite-sample coverage target for Classes A--F, but this is
coverage closure rather than taxonomy completeness. ADE remains only a
candidate local model for smooth discriminant branches; graph, Markov,
activation, and degenerate rate probes require non-ADE, stratified, or
species-specific wall languages.

## Paper XII - SOF Diagnostic Protocol

| Script | Status |
|--------|--------|
| `schemas/sofrs/v1.0.schema.json` | canonical JSON Schema for the versioned eight-field SOF Report Specification (SOFRS) v1.0 |
| `schemas/sofrs/paper12-protocol-profile-v1.0.json` | independent admission profile layered over the frozen envelope schema |
| `experiments/paper12/validate_sofreport.py` | frozen SOFRS v1.0 envelope and Appendix schema-drift validator |
| `experiments/paper12/validate_protocol_admission.py` | stronger Paper XII admission-profile validator for named-system and Level III provenance requirements |
| `experiments/paper12/transformer_activation_sof.py` | transformer-style activation SOF diagnostic and reproducible report |
| `experiments/paper12_figures.py` | generates the diagnostic-protocol and four-level applicability-hierarchy figures |
| `experiments/paper12/qwen_attention_sof.py` | revision-pinned Qwen attention-head SOF diagnostic with parameterized cache/device/dtype and recorded runtime provenance; Head 6 gives four natural sectors |
| `experiments/paper12/transformer_batch_sweep.py` | transformer token-partition sweep; canonical `5 x 50` row has `frozen_R1=14`, `D_repaired=6`, and one permanently frozen sector |
| `experiments/paper12/moe_expert_sof.py` | MoE routing SOF Report: all six expert-pair sectors, `80%` direct support, six two-step repairs, and no terminally frozen pair |
| `experiments/paper12/moe_bias_repair_sof.py` | DeepSeek-style MoE routing-repair control: `10/12` initially frozen private experts reactivate under load-bias updates; shared baseline is excluded from private freeze counts |
| `experiments/paper12/diffusion_denoising_sof.py` | diffusion-time SOF deformation diagnostic; forward noise creates a sector split at `t=11`, reverse denoising is the repair direction |
| `experiments/paper12/maze_wall_crossing.py` | dynamic connectivity wall demo: `24` split crossings and `24` reverse merge/repair crossings on a `5 x 5` maze |
| `experiments/paper12/blackbox_llm_sof.py` | API-level SOF Report for an API-only LLM / black-box language model: protocol/task probe sectors, Structural/Behavioral/Failure observables, and repair transitions; weak comparison only |
| `experiments/paper12/results/nvidia_llama31_8b_20260711.sofreport` | first versioned real API-level report: NVIDIA NIM `meta/llama-3.1-8b-instruct`, `18/18` successful protocol--task requests |
| `experiments/paper12/results/transformer.sofreport` | SOFRS v1.0 transformer activation report |
| `experiments/paper12/results/diffusion.sofreport` | SOFRS v1.0 diffusion-time wall and reverse-repair report |
| `experiments/paper12/results/maze.sofreport` | SOFRS v1.0 connectivity split/merge wall record |
| `experiments/paper12/results/moe.sofreport` | SOFRS v1.0 expert-routing support and two-step repair report |
| `experiments/paper12/results/qwen.sofreport` | SOFRS v1.0 revision-pinned pretrained-Qwen attention-head report on the strict 40-token retained subspace |
| `experiments/paper12/results/recommender.sofreport` | SOFRS v1.0 recommender coverage and targeted dead-zone repair report |
| `experiments/paper12/results/moe_bias_repair.sofreport` | SOFRS v1.0 private-expert load and bias-driven routing-repair trajectory |
| `experiments/paper12/results/transformer_batch.sofreport` | SOFRS v1.0 token-bin sector-count robustness sweep |
| `experiments/paper12/results/failure_cases.fixture.json` | envelope-valid multi-system validator fixture; intentionally excluded from ordinary protocol admission |
| `experiments/paper12/recommender_sof.py` | recommender structural-coverage report: `12/16` user/item cluster pairs are unreachable in the default disconnected benchmark; not an A/B-test replacement |
| `experiments/paper12/failure_cases.py` | generates the multi-system validator fixture for single-sector, all-to-all, over-refined, commuting, and sector-observable mismatch cases |

Paper XII scripts support the published diagnostic methodology and its
reference SOFRS artifacts. They do not retroactively enlarge the claim sets of
Papers I--XI. The current repository manuscript is an explicit new-version
candidate; it retains the same SOFRS v1.0 schema, artifact paths, and nine
admitted reference reports.

## Paper XIII - Comparison Geometry of SOF Reports

| Script | Status |
|--------|--------|
| `schemas/sofaudit/v1.0.schema.json` | canonical factual-only contract for aligned reference/target comparisons and induced audit signatures |
| `experiments/paper13/validate_sofaudit.py` | validates the canonical schema, linked SOFRS reports, legitimate-transformation semantics, and all published `.sofaudit` artifacts |
| `experiments/paper13/gridworld_reference_sof.py` | controlled GridWorld reference and five comparison signatures, including word/Lie channel separation |
| `experiments/paper13/sir_compartment_sof.py` | SIR rate, support, response-order, and wall-record comparisons |
| `experiments/paper13/traffic_intersection_sof.py` | traffic phase, timing, and trajectory-mismatch comparisons |
| `experiments/paper13/compiler_ir_sof.py` | compiler-IR CFG/def-use alignment and pass-pipeline controls |
| `experiments/paper13/network_routing_sof.py` | appendix routing domain with ACL removal and higher-order bridge diagnostics |
| `experiments/paper13/before_after_alignment.py` | three legitimate transformations with nonzero raw signatures and zero contract residuals |
| `experiments/paper13/signature_metric.py` | fixed-fiber weighted structural pseudometric control |
| `experiments/paper13/word_lie_controlled.py` | exact-support word/Lie inclusion and strict word-only witness |
| `experiments/paper13/regenerate_tables.py` | regenerates the published signature tables from canonical artifacts |

Paper XIII scripts support the published alignment and comparison methodology.
They establish local fixed-fiber comparison geometry and controlled portability;
they do not infer alignments automatically, define cross-fiber transport, or
interpret nonzero signatures as defects or actions. Paper XIV action semantics
remain outside this public experiment index until that release boundary is fixed.

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
