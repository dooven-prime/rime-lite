# SOF Registry

**Status:** public explanatory companion to Paper X, published as
DOI [10.5281/zenodo.21288036](https://doi.org/10.5281/zenodo.21288036). The
Registry is evidence architecture, not a classification theorem or a
replacement for Paper VIII and [SOF_OBJECTS.md](SOF_OBJECTS.md).

SOF means **Sectorized Observable Framework** and supplies a sectorized
observable architecture and analysis paradigm. Paper X
uses the Universal Observable Pipeline as the theorem-level structure:

```text
species
  -> finite space V
  -> sectorization {Q_i}
  -> observable family X
  -> observable shadows
  -> observable diagnostics
```

The registry records examples where this pipeline has been realized and where
sector data, observable families, and derived shadows have been tested or
identified.  The registry is evidence architecture, not the theorem itself.
Wall behavior is not part of the registry entry itself; it appears only after
a deformation geometry is specified.

## Machine-Readable Snapshot

The frozen Paper X release snapshot is
`registry/paper10-release-v1.0.registry.json`. It contains the 16 entries in
the Paper X publication boundary and validates against
`schemas/registry/v1.0.schema.json`.

This document is the public explanatory layer. The JSON file is immutable
release data. Species introduced by Papers XI--XII are not
backfilled into that snapshot; they require a later version. Validate it with:

```bash
python registry/validate_snapshot.py
```

## Registry Rule

Each entry should identify five layers:

```text
species
  -> SOF object
  -> observable ladder
  -> dynamics
  -> diagnostics
```

Applicability and claim status are metadata attached to each entry, not
additional registry layers.

The SOF object layer records the realized triple:

```text
F_s = (V_s, {Q_i^(s)}, X_s)
```

The observable ladder records shadows such as spectra, collision data,
`R_1/R_2/D`, jets, filtration plateaus, or rate proxies.  The dynamics layer
records the deformation variable when present.  The diagnostics layer records
measured or proved quantities such as `tau`, `wall`, `repair`, and `plateau`.

This makes the registry a five-layer taxonomy rather than a flat evidence
table.

## Registry Applicability Index

The following compact index is a reader-facing view of the active registry.
Applicability classifies the justification used by the registered analysis,
not the species permanently. Claim status is an independent epistemic label:
Level I does not imply a theorem, and Level III does not imply a strict
internal realization. Level IV analogies are excluded because they cannot
enter the Registry as realized species or produce conforming SOFRS artifacts.

This index does not modify the frozen Paper X v1.0 snapshot or its schema. A
machine-readable `applicability_level` field remains reserved for a future
Registry contract version.

| Species | Applicability | Claim Status |
|---------|---------------|--------------|
| Rubik QT/HT | Level I: Definitional | `evidence` |
| Rubik Type III/IV wild mechanisms | Level I: Definitional | `evidence` |
| Synthetic Type III/IV | Level I: Definitional | `negative_control` |
| Xu ridge model | Level II: Realizational | `theorem` (external rate precedent) |
| Mechanism-separated SOF control | Level I: Definitional | `evidence` |
| Engineered near-threshold accessibility | Level I: Definitional | `diagnostic` |
| Finite spectral triple | Level I: Definitional | `evidence` |
| Control systems | Level I: Definitional | `diagnostic` |
| PDE discretization | Level I: Definitional | `diagnostic` |
| Combinatorial optimization | Level I: Definitional | `diagnostic` |
| Barrier-option stochastic finance | Level II: Realizational | `diagnostic` |
| Quantum gates | Level I: Definitional | `evidence` |
| Markov / absorbing Markov | Level I: Definitional | `boundary` |
| Graph systems | Level I: Definitional | `boundary` |
| Yang-like photonic systems | Level II: Realizational | `boundary` |
| Neural-network / transformer SOFs | Level II: Realizational | `proxy_only` (Paper IX); `diagnostic` (Paper XII) |
| Mixture-of-Experts routing | Level II: Realizational | `diagnostic` |
| Diffusion / denoising SOFs | Level II: Realizational | `diagnostic` |
| API-only LLM / black-box language model | Level III: Diagnostic | `diagnostic` |
| Dynamic maze connectivity | Level I: Definitional | `diagnostic` |
| Recommender structural coverage | Level II: Realizational | `diagnostic` |
| Rubik deformation probes | Level I: Definitional | `diagnostic` |

## Current Five-Layer Entries

| Species | Sectorization origin | SOF object | Observable ladder | Dynamics | Diagnostics / status |
|---------|----------------------|------------|-------------------|----------|----------------------|
| Rubik QT/HT | representation / joint spectral geometry | cube-representation SOF with nine QT/HT sectors and face-turn/QT/HT observables | spectra, collision quotient, `R_1/R_2/D`, `J_acc` | affine projection, generator weights, normal spectral charts | core RIME laboratory |
| Rubik Type III/IV wild mechanisms | representation / joint spectral geometry | QT/HT sectorized Rubik SOF | cancellation and incidence mechanism audit | static bridge-product audit on natural sectors | naturally occurring instances: `288` Type III cancellations and `528` Type IV bridge-level incidence candidates |
| Synthetic Type III/IV | constructed sector model | constructed block-sector SOFs | cancellation, repair, incidence, completion boundaries | static and perturbative mechanism tests | constructed boundary references |
| Xu ridge model | external row/null decomposition | row/null external observable-dynamics species | fast/slow parameter-observable channels | gradient versus regularization dynamics | theorem-proven external rate-separation precedent |
| Mechanism-separated SOF control | constructed sector model | constructed three-sector SOF | `K0_grow/K1_decay` proxy ladder | gradient-driven growth versus regularization-only decay | constructive H3 positive control, `30 << 1380` |
| Engineered near-threshold accessibility | constructed near-threshold sectors | synthetic near-threshold accessibility SOF | `R_1/R_2` threshold shadows | near-threshold perturbation | engineered `tau(R_1)<tau(R_2)` diagnostic |
| Finite spectral triple | geometry / Dirac blocks | finite Hilbert-space SOF with block projectors from a block-diagonal Dirac operator `D` and algebra/one-form observables | central Connes-distance obstruction and T7-style bridge shadows | static NCG-inspired registry probe | non-group portability example: `max norm([D,p_i])_F=0`, cross-block central distance infinite, `2` ordered T7-style bridges |
| Control systems | controllability flag | Kalman-chain SOF with sectors from controllability-flag increments | direct support, length-two word support, first word-depth | static controllability diagnostic | Kalman ranks `1,2,3`; terminal word-depth `2` |
| PDE discretization | discretization geometry / mesh partition | finite-difference Laplacian SOF with subdomain/interface mesh sectors | direct coupling, length-two support, first word-depth | static mesh-transport diagnostic | left-to-right word-depth `2` through interface sector |
| Combinatorial optimization | constraint / color partition | graph-coloring SOF with color-class projectors and adjacency observable | inter-color support and same-color conflict diagnostics | static coloring diagnostic | `4` inter-color directed support edges; `2` same-color conflicts |
| Barrier-option stochastic finance | stopping/barrier region | finite log-price grid SOF with below-barrier / above-barrier projectors and GBM finite-difference observables | cross-barrier support and stochastic first-hitting-time diagnostic | log-price diffusion / barrier hitting | independent stochastic-process species: `R1=75.0%`, `R2=0.0%`, `D_repaired=0`, mean first-hit time `6.5915` in the default audit |
| Quantum gates | computational-basis or spectral sectors | computational-basis or spectral sector SOF with gate logs/Hamiltonians | `R_1/R_2/D` accessibility ladder | gate-set expansion and Hamiltonian/gate deformation | non-Rubik D-repair sanity checks |
| Markov / absorbing Markov | state / absorbing-class partition | state-sector SOFs with transition or rate operators | `R_1/R_2/D`, frozen-pair audit | transition perturbation, absorbing boundaries | portability and degenerate-frozen diagnostics |
| Graph systems | vertex or spectral graph partition | vertex or spectral sector SOFs with adjacency/Laplacian/walk operators | graph transport shadows and `R_1/R_2/D` audit | rewiring, weighting, spectral perturbation | connected controls and frozen-pair degeneracies |
| Yang-like photonic systems | state / filtration sectors | filtration-sector SOF with state/coherence observables | plateau functions and filtration-depth shadows | state mixing / coherence degeneration | future comparison branch |
| Neural-network / transformer SOFs | activation-induced regions, attention partitions, expert-routing partitions | activation- or attention-sector SOFs with weight/token-derived operators | raw `K0/K1/K2` proxy ladder, auxiliary `R_1/R_2/frozen` audits, transformer activation, Qwen attention-head, and batch-sweep reports | activation choice, attention-head diversity, training dynamics, token-space influence | Paper IX proxy-rate diagnostics plus Paper XII transformer diagnostics (`R1=58.3%`, `R2=66.7%`, `D_repaired=2`; Qwen Head 6 gives four natural sectors; batch sweep `frozen_R1=14`, `D_repaired=6`) |
| Mixture-of-Experts routing | router-derived expert-pair partitions and private expert activity sectors | token-space SOF with identical top-2 route sectors, private load sectors, routing overlap, and a separate shared baseline | direct routing support, generic word-depth closure, frozen-expert trajectories, and bias-driven repair | router weights, top-k policy, token population, capacity/dropout changes, and load-bias updates | Paper XII white-box diagnostics: dense four-expert control realizes all six route sectors with `24/30` direct ordered support pairs; DeepSeek-style sparse control starts with `10/12` private experts frozen and repairs `10/10` from step `18`, while a shared baseline remains separate; routing analogues, not Lie-depth `D` |
| Diffusion / denoising SOFs | time-indexed noise-sector proposal | finite feature-space SOF with PCA-sign probe sectors and feature/noise observables | sector-count trajectory and support edges along diffusion time | forward noise schedule and reverse denoising path | Paper XII toy diagnostic: forward noise creates a sector split at `t=11`, reverse denoising is the repair direction |
| API-only LLM / black-box language model | prompt protocols / task classes used as probe sectors | no strict projector-based SOF object; API-only behavioral comparison | Structural, Behavioral, and Failure observable families; repair recorded as protocol transitions | prompt/schema/few-shot/tool protocol changes | API-level SOF Report under the Black-Box SOF Diagnostic Principle; first versioned NVIDIA NIM audit completes `18/18` requests with task completion `61.1%`, instruction following `72.2%`, schema repair `2`, valid tool repair `1`, and visible off-task tool misuse; endpoint-scoped evidence, not an internal-mechanism or `D`-repair claim |
| Dynamic maze connectivity | graph connected components induced by door state | finite cell-space graph SOF with time-dependent component sectors | component count, frozen ordered cell-pair count, split/merge wall record | door closure followed by reverse reopening | Paper XII visual wall diagnostic: `24` component splits and `24` reverse merges, `0 -> 600 -> 0` frozen ordered cell pairs; connectivity repair, not fixed-sector `D` |
| Recommender structural coverage | user/item cluster partition | bipartite user-item SOF with interaction observable | direct support, generic propagation depth, unreachable cluster-pair audit | targeted interaction or coverage interventions | Paper XII synthetic offline diagnostic: `12/16` user/item cluster pairs unreachable initially, reduced to `10/16` by one targeted bridge; not a ranking or A/B-test claim |
| Rubik deformation probes | representation / joint spectral geometry | QT/HT sector SOFs with state-filtered or generator-weighted observables | plateau functions `P_d` | state mixing or generator-weight deformation | Yang/RIME contrast and oscillation diagnostics |

## Deformation Geometries

| Branch | Deformation variable | Geometry | Current status |
|--------|----------------------|----------|----------------|
| Spectral SOF | affine or spectral projection parameter | collision geometry / spectral walls | Paper IV and spectral side of Paper VI |
| Accessibility SOF | generator weights or observable-family deformation | accessibility walls | Papers V--VII |
| Filtration SOF | state mixing or coherence variation | filtration degeneration | future comparison branch |
| Observable-dynamics SOF | training or optimization trajectory | observable time-scale hierarchy | Paper IX diagnostic layer |
| Neural-network SOF | activation family and training dynamics | activation-dependent sectorization and proxy tau ratios | cross-reference diagnostic |
| Quantum circuit SOF | gate-set expansion or gate-family deformation | circuit accessibility channels | diagnostic only |
| Markov SOF | rate or transition perturbation | communicating-class / transport changes | diagnostic only |
| Graph SOF | edge rewiring or Laplacian perturbation | graph transport changes | diagnostic only |
| Stochastic-finance SOF | log-price diffusion and barrier/stopping level | first-hitting and barrier-crossing diagnostics | diagnostic only |

## Support Scripts

Current support and diagnostic scripts:

```text
experiments/paper7/atlas_r2_boundary.py
experiments/paper7/incidence_variety_codim.py
experiments/paper7/rank_protected_bridge_audit.py
experiments/paper7/markov_graph_sof.py
experiments/quantum/quantum_accessibility_universality.py
experiments/cross_ref/grokking_rate_separation.py
experiments/paper9/nn_activation_sof.py
experiments/paper9/nn_training_sof_tau.py
experiments/paper12/transformer_activation_sof.py
experiments/paper12/qwen_attention_sof.py
experiments/paper12/transformer_batch_sweep.py
experiments/paper12/diffusion_denoising_sof.py
experiments/paper12/failure_cases.py
experiments/paper12/blackbox_llm_sof.py
experiments/paper12/results/nvidia_llama31_8b_20260711.sofreport
experiments/paper12/moe_expert_sof.py
experiments/paper12/moe_bias_repair_sof.py
experiments/paper12/maze_wall_crossing.py
experiments/paper12/recommender_sof.py
experiments/paper9/rate_hierarchy.py
experiments/paper9/state_mixing_fft.py
experiments/paper9/plateau_under_qt_perturbation.py
experiments/paper10/mechanism_separation_theorem.py
experiments/paper10/control_pde_combinatorial_sof.py
experiments/paper10/ncg_spectral_triple_sof.py
experiments/paper10/rubik_wild_type34_audit.py
experiments/paper10/barrier_option_sof.py
experiments/paper10/registry_evidence.py
experiments/paper10/tau_quantum_graph_yang.py
```

## Implementation Interface

The current reusable audit interface is:

```text
AccessibilityEngine(Vs, Xs)
  -> R_1 support
  -> R_2 commutator survival
  -> D first Lie-depth matrix
  -> frozen_R1 / frozen_D / D_repaired diagnostics
```

This is an implementation interface, not a mathematical equivalence theorem.
Once an example provides sector bases `Vs` and operator generators `Xs`, the
same audit computes the accessibility shadows.

Metric convention:

```text
R1_tensor_pct, R2_tensor_pct:
  full block tensor density, including diagonal blocks

R1_pct, R2_pct:
  off-diagonal accessibility density; aliases of R1_offdiag_pct/R2_offdiag_pct
```

Frozen-pair diagnostics are off-diagonal sector-pair diagnostics.

For observable-dynamics diagnostics, raw norm proxies are also used:

```text
K0(t): direct support / R_1 proxy
K1(t): commutator survival / R_2 proxy
K2(t): nested-commutator depth proxy
```

These retain scale information during a dynamical process. They are therefore
better suited to measuring characteristic times `tau(O)` than the normalized
binary `D` matrix.

## Current Takeaways

- `R_1/R_2/D` are sectorized observables, not Rubik-specific quantities.
- SOF abstracts coarse-grained information accessibility. A compatible
  sectorization is a system-recognized coarse coordinate system; once one asks
  how information, influence, or transport crosses those sectors, support,
  bridge, depth, repair, and wall shadows are the natural diagnostics.
- Stable slogan: sectorization is source-dependent; the observable pipeline is
  source-independent.
- Sectorization is required before these shadows exist: no sector projectors
  means no support, bridge, repair, or wall shadows. This is the No-Sector
  No-Shadow principle.
- The Paper X registry evidence currently includes a mechanism-separated SOF
  control (`tau(K0_grow)=30`, `tau(K1_decay)=1380`), Rubik wild Type III/IV
  instances (`288` Type III cancellations and `528` Type IV bridge-level
  incidence candidates), Xu ridge separation (`~68553x`), RIME near-threshold
  separation (`~10.8x`), Yang/RIME plateau contrast (`1/5` vs `3/8` zero
  crossings), and quantum Clifford D-repair (`6` vs Pauli `0`).
- The Rubik Type IV count should be read in Paper VII's bridge-level sense:
  incidence candidates, not certified Type IV accessibility obstructions.
- Quantum CNOT examples show non-Rubik higher-depth repair in the tested
  computational-basis sectorization.
- The finite spectral-triple probe shows SOF portability outside group/Lie
  origins: block projectors from a Dirac operator give sectorization, central
  Connes-distance obstruction appears at the metric layer, and T7-style bridge
  shadows appear at the observable-composition layer.
- This entry is the first registry species in which sectorization is induced by
  geometry rather than representation-theoretic decomposition. It suggests that
  SOF depends on compatible sectorization, not on the specific algebraic origin
  of the sectors.
- Control, PDE, and combinatorial probes extend this sector-origin independence:
  sectors may come from a Kalman flag, a mesh/interface partition, or a coloring
  constraint. These are word-depth portability diagnostics, not Paper V
  commutator-repair theorems.
- Barrier-option stochastic finance extends the registry to a mathematically
  independent stochastic-process setting. Here sectorization comes from a
  stopping/barrier region in a log-price diffusion. The first-hitting time is
  a stochastic diagnostic attached to the SOF entry; it is not identified with
  the discrete accessibility depth `D`.
- Markov and graph examples test portability of the audit interface; they do
  not prove cross-species D-repair or generic completion.
- Yang-like filtration probes should be treated as a different deformation
  geometry, not as the Paper VI accessibility-wall template.
- Neural-network and transformer diagnostics show that activation choice,
  token activation clusters, attention partitions, and related model-internal
  decompositions can induce SOF sectorizations. The Paper XII transformer
  diagnostic gives three activation-count sectors with `R1=58.3%`,
  `R2=66.7%`, and `D_repaired=2`.
- Training-coupled NN diagnostics give exploratory evidence for
  `tau(K0)<tau(K1)<tau(K2)` under a specified optimization dynamics; this is
  proxy-only evidence, not a `tau(D)` claim.
- The registry does not yet include a proved `K_i -> R_i/D` bridge. This open
  bridge is the Observable Proxy Shadow Principle: when do continuous proxies
  determine or predict discrete shadows?
- The registry does not yet contain a single structured deformation with both
  `tau(R_1)<tau(R_2)<tau(D)` and `D_repaired>0`; static Clifford+CNOT gives
  non-Rubik D-repair, but not a measured `tau(D)` trajectory. The natural
  future targets are structured quantum gate deformations and Rubik continuous
  deformations.
- Paper X tau-boundary probes show that quantum linear interpolation, graph
  rewiring, and Yang-like state mixing fail or degenerate; H3 structured
  dynamics is decisive.
- Gap 3 is closed at the proxy layer: the SOF category now has a constructive
  H3 positive control.  Gap 4 remains conditional on a proxy-to-shadow bridge
  and a genuine `tau(D)` audit.
- In the default small NN SOF, `D_repaired=0` throughout because all sector
  pairs are already connected at the binary level; this separates continuous
  rate hierarchy from binary frozen-to-accessible repair.
- Rubik state-mixing and generator-weight probes show different observable dynamics:
  state mixing is flat until an extreme endpoint, while generator-weight
  plateau data can be oscillatory.

## Promotion Rule

A registry entry can become paper-level evidence only when it has:

1. a named SOF species;
2. an explicit sectorization;
3. an explicit observable family;
4. a named derived shadow or diagnostic;
5. a support script or proof mechanism;
6. a claim-status metadata label.

Without these six items, the entry remains a horizon note.
