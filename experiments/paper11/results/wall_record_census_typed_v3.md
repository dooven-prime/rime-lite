# Paper XI Typed Wall-Profile Census

- Historical rows preserved: **28**
- Active typed records: **27**
- Retired rows: **1**
- Strict main wall-spectrum records: **5**
- Analogue morphology records: **2**
- Morphology record bundles: **7**
- Morphology atoms: **7**
- Registered atom-field entries: **10**
- Trajectory-change entries: **8**
- Locus-germ entries: **2**
- Pair-scoped entries: **4**
- Active multi-label memberships: **34**
- Morphology bundles contain atoms from the trajectory-event/locus-sample union.
- Tags are nonexclusive curation labels, not classification classes.
- Imported evidence retains its source-paper ownership.

## Record roles

| Role | Records |
|---|---:|
| pre_wall_reference | 2 |
| retired_provenance | 1 |
| static_boundary_witness | 5 |
| trajectory_diagnostic | 13 |
| wall_event | 5 |
| wall_locus_sample | 2 |

## Realization kinds

| Realization kind | Records |
|---|---:|
| diagnostic_analogue | 9 |
| strict_sof | 19 |

## Curation tags

| Tag | Active records | Main-wall records | Species | Deformations |
|---|---:|---:|---:|---:|
| COLLISION | 4 | 3 | 2 | 3 |
| REPAIR | 9 | 0 | 0 | 0 |
| TERMINAL | 3 | 0 | 0 | 0 |
| PLATEAU_RATE | 4 | 0 | 0 | 0 |
| NONSMOOTH_DISCRETE | 7 | 1 | 1 | 1 |
| BRIDGE_INCIDENCE | 7 | 1 | 1 | 1 |

## Morphology record bundles

| Partition | Record | Role | Field family | Primary field | Evidence |
|---|---|---|---|---|---|
| strict_main | `rubik-collision-quotient` | wall_locus_sample | spectral | `spectral.joint_sector_count` | `experiments/paper11/results/rubik_collision_quotient_result_v1.json` |
| strict_main | `rubik-endpoint-pair-closures` | wall_event | spectral | `spectral.adjacent_gap` | `experiments/paper11/results/rubik_spectral_endpoint_v1.json` |
| strict_main | `constructed-route-incidence` | wall_locus_sample | route | `route.support[Y,d=2]` | `experiments/paper11/results/route_incidence_result_v1.json` |
| strict_main | `graph-edge-removal` | wall_event | operator | `operator.direct_support[Y]` | `experiments/paper11/results/wall_trajectory.json` |
| strict_main | `constructed-goe-endpoint` | wall_event | spectral | `spectral.adjacent_gap` | `experiments/paper11/results/constructed_goe_endpoint_v1.json` |
| analogue_morphology | `maze-door-wall` | wall_event | graph | `graph.component_count` | `experiments/paper12/results/v2/ir/maze.ir.json` |
| analogue_morphology | `grn-terminal-basin-loss` | wall_event | state | `state.terminal_component_count` | `experiments/paper11/results/grn_terminal_basin_loss_v1.json` |

## Active records

- `rubik-collision-quotient`: Rubik QT/HT | spectral | spectral.joint_sector_count | Computational Certificate | wall_locus_sample | strict_sof | field_family=spectral | owner=paper11
- `rubik-endpoint-pair-closures`: Rubik QT/HT | spectral | spectral.adjacent_gap | Computational Certificate | wall_event | strict_sof | field_family=spectral | owner=paper11
- `rubik-simultaneous-pair-gap-response`: Rubik QT/HT | spectral | spectral.pair_gap_response | Computational Observation | pre_wall_reference | strict_sof | field_family=spectral | owner=paper11
- `rubik-r2-repair`: Rubik accessibility | lie_hall | lie.direct_support[X], lie.simple_commutator_support[X] | Computational Certificate | static_boundary_witness | strict_sof | field_family=lie_hall | owner=paper5
- `rubik-commutator-cancellation`: Rubik anti-Hermitian low-order audit | lie_hall | lie.simple_commutator_support[X] | Computational Certificate | static_boundary_witness | strict_sof | field_family=lie_hall | owner=paper10
- `constructed-route-incidence`: Constructed routed-product incidence | operator_route | route.support[Y,d=2] | Computational Certificate | wall_locus_sample | strict_sof | field_family=route | owner=paper11
- `constructed-commutator-repair`: Constructed commutator-cancellation control | lie_hall | lie.direct_support[X], lie.simple_commutator_support[X] | Computational Certificate | static_boundary_witness | strict_sof | field_family=lie_hall | owner=paper5
- `quantum-cnot-path-admissibility`: Quantum Clifford+CNOT path control | cnot_path_admissibility_diagnostic | diagnostic.path_logarithm_admissibility | Computational Observation | trajectory_diagnostic | strict_sof | field_family=diagnostic | owner=paper11
- `control-kalman-chain`: Control Kalman | operator_word | word.depth_truncated[Y,cutoff=3] | Computational Observation | static_boundary_witness | strict_sof | field_family=word | owner=paper10
- `transformer-matrix-commutator-repair`: NN Transformer activation | matrix_commutator_diagnostic | diagnostic.matrix_commutator_repair_pair_count[cutoff=3] | Computational Observation | trajectory_diagnostic | diagnostic_analogue | field_family=diagnostic | owner=paper12
- `moe-bias-repair`: Mixture-of-Experts routing | routing | routing.active_private_experts | Computational Certificate | trajectory_diagnostic | diagnostic_analogue | field_family=state | owner=paper12
- `diffusion-denoising-repair`: Diffusion / denoising | state_partition | state.sector_count, state.direct_support | Computational Observation | trajectory_diagnostic | diagnostic_analogue | field_family=state | owner=paper12
- `maze-door-wall`: Dynamic maze connectivity | graph_connectivity | graph.component_count, graph.unreachable_pair_count | Computational Observation | wall_event | diagnostic_analogue | field_family=graph | owner=paper12
- `recommender-targeted-bridge`: Recommender structural coverage | bipartite_coverage | coverage.unreachable_pair_count | Computational Observation | trajectory_diagnostic | strict_sof | field_family=graph | owner=paper12
- `markov-absorbing-endpoint`: Markov absorbing | markov_communication | markov.terminal_unreachable_pair_count | Computational Observation | pre_wall_reference | strict_sof | field_family=state | owner=paper11
- `barrier-stopping-boundary`: Barrier option GBM | stochastic_stopping | stochastic.first_hit_boundary | Computational Observation | trajectory_diagnostic | strict_sof | field_family=stochastic | owner=paper10
- `exact-three-sector-rate-separation`: Exact three-sector skew family | continuous_lie_block_norms | lie_norm.K_direct, lie_norm.K_simple_commutator | Theorem | trajectory_diagnostic | strict_sof | field_family=proxy | owner=paper9
- `mechanism-separated-rates`: Mechanism-separated SOF | observable_proxy | proxy.K0_growth_time, proxy.K1_response_time | Computational Certificate | trajectory_diagnostic | strict_sof | field_family=proxy | owner=paper10
- `nn-proxy-rate-ordering`: Training-coupled NN SOF | observable_proxy | proxy.K0_direct_norm, proxy.K1_simple_commutator_norm, proxy.K2_nested_commutator_norm | Computational Observation | trajectory_diagnostic | diagnostic_analogue | field_family=proxy | owner=paper9
- `graph-edge-removal`: Graph P3/C4 | operator_word | operator.direct_support[Y], word.depth_truncated[Y,cutoff=6] | Computational Certificate | wall_event | strict_sof | field_family=operator | owner=paper11
- `relu-kink`: NN Transformer activation | activation | activation.response_slope | Computational Certificate | trajectory_diagnostic | diagnostic_analogue | field_family=state | owner=paper11
- `topk-rank-selection`: NN Transformer activation | activation | activation.topk_active_count | Computational Observation | trajectory_diagnostic | diagnostic_analogue | field_family=state | owner=paper11
- `ncg-t7-bridge`: Finite spectral triple | operator_route | route.support[Y,d=2] | Computational Observation | static_boundary_witness | strict_sof | field_family=route | owner=paper10
- `constructed-goe-endpoint`: Constructed real-symmetric spectral family | spectral | spectral.adjacent_gap | Computational Certificate | wall_event | strict_sof | field_family=spectral | owner=paper11
- `nested-percolation-opening`: Erdos-Renyi percolation ensemble | operator_word | operator.direct_support[Y], word.unreached_pair_count_at_cutoff[Y,cutoff=6,aggregation=ensemble_mean,ensemble_policy=seeded_nested_32] | Computational Observation | trajectory_diagnostic | strict_sof | field_family=word | owner=paper11
- `kuramoto-freezing-crossover`: Kuramoto oscillator ensemble | operator_word | word.depth_truncated[Y,cutoff=3], dynamics.order_parameter_occupancy | Computational Observation | trajectory_diagnostic | diagnostic_analogue | field_family=word | owner=paper11
- `grn-terminal-basin-loss`: GRN toggle-switch flow | terminal_structure | state.terminal_component_count, state.terminal_sector_identity | Computational Observation | wall_event | diagnostic_analogue | field_family=state | owner=paper11

## Retired provenance

- `rubik-generator-weight-plateau`: retired nonnormal generator-weight fragmentation/oscillation diagnostic; not admitted to the typed moving-wall census
