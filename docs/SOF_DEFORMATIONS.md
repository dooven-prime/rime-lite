# SOF Deformations

**Status:** dynamic-layer routing note for Paper IX. This file records
deformation geometry, observable dynamics, rate separation, and wall behavior.
It preserves claim boundaries and does not replace the Paper IX manuscript.

Paper IX should be framed around:

```text
Observable Dynamics
```

Rate separation is one structural phenomenon inside observable dynamics, not
the whole subject.

## Dynamic Layer

Given an SOF

```text
F = (V, {Q_i}, X),
```

a deformation is a family

```text
F_t = (V_t, {Q_i(t)}, X(t)).
```

The primary dynamic object is the path or family `(F_t)_{t in I}` in
`SOF_def`, not merely an endpoint arrow `F_0 -> F_1`.  The endpoint notation
`Phi_t: F -> F_t` is shorthand for comparison data that lets observables be
tracked along this path.

An admissible deformation induces observable trajectories:

```text
R_1(t), R_2(t), D(t), J_acc(t), ...
```

Here admissible means:

- the path has comparison data for the diagnostic under discussion;
- the relevant sectors, or registered analogues, can be tracked on the domain
  being studied;
- the continuous field underlying the diagnostic is defined on that domain;
- the discrete shadow is locally constant away from the relevant rank,
  support, collision, filtration, or wall discriminant.

Admissibility is therefore attached to a chosen observable diagnostic; it is
not automatic for every formal deformation in `SOF_def`.

Formal status:

```text
Paper VIII: strict static category SOF_str
Paper IX:   provisional deformation category SOF_def
```

`SOF_def` is the weak dynamic container for deformation data.  Its arrows are
parameterized SOF families with enough comparison data to evaluate observable
trajectories.  They need not be isometric, need not preserve sector dimensions,
and need not preserve the full naturality statements of the strict category.
This closes the bookkeeping gap between the static object theory and the
dynamic notation `Phi_t: F -> F_t`, while leaving the full theory of weak SOF
morphisms for later work.

The central Paper IX question is:

```text
How do SOF observables evolve under a chosen deformation geometry?
```

## Observable Dynamics

Observable dynamics consists of:

- observable trajectories `O_i(t)`;
- plateaus and regimes;
- characteristic time scales `tau(O_i)`;
- discontinuity or discriminant loci;
- wall-crossing behavior.

The general principle is:

```text
same observable architecture,
different deformation geometry,
different observable dynamics.
```

SOF supplies the analysis paradigm. The deformation geometry supplies the
specific dynamics.

Current Paper IX diagnostics separate three deformation geometries:

| Diagnostic | Deformation geometry | Observable behavior |
|------------|----------------------|---------------------|
| State mixing on Rubik | state filter / density-style mixing | `P_d` flat for `epsilon=0..0.9`, jump only at `epsilon=1.0` |
| Generator-weight sweep | observable-family weight variation | plateau sequence oscillatory, not monotone |
| Training-coupled NN SOF | optimization dynamics with weight decay | raw proxies satisfy `tau(K0)<tau(K1)<tau(K2)` in the default run |
| Mechanism-separated SOF control | explicit fast-growth / slow-decay mechanisms | `tau(K0_grow)=30 << tau(K1_decay)=1380` |

The point is not that these are the same mechanism. The point is that SOF gives
a common observable architecture in which different deformation geometries can be
compared.

## Observable Rate Separation

A deformation is **observable rate-separated** if induced observable
trajectories have distinct characteristic time scales:

```text
tau(O_i) != tau(O_j)
```

for some observables `O_i`, `O_j`.

For RIME accessibility, a candidate hierarchy under a structured dynamical
perturbation model is:

```text
tau(R_1) < tau(R_2) < tau(D)
```

where direct support responds first, commutator survival responds next, and
first-depth repair becomes visible only through slower channels. This hierarchy
is not expected to hold under every static perturbation model.

This should be compared carefully with external examples:

```text
Xu/Vardi/Safran grokking:
  tau(theta_parallel) << tau(theta_perp)

RIME accessibility:
  tau(R_1) < tau(R_2) < tau(D)
```

The first is parameter-space rate separation. The second is observable-space
rate separation.

Static additive noise is a poor model for this hierarchy. It perturbs
generators, commutators, and nested commutators simultaneously, so the Lie-depth
observable `D` can acquire accidental new directions before `R_1` or `R_2`
cross their intended thresholds. A useful diagnostic result is:

```text
near-threshold additive-noise system:
  tau(R_1) = 5.89e-9 < tau(R_2) = 6.37e-8
  tau(D)   = 1.00e-10  (scrambled by simultaneous Lie-filtration perturbation)
```

This supports `tau(R_1)<tau(R_2)` for engineered near-threshold systems, but it
also shows that `tau(D)` requires a perturbation model that separates
first-order support, commutator survival, and higher Lie-depth effects.
Xu--Vardi--Safran's gradient-descent plus weight-decay model is the right kind
of precedent: one channel is gradient-driven while the hidden channel is driven
only by regularization. Paper IX should therefore treat observable rate
hierarchy as a property of **dynamical deformation models**, not of arbitrary
static additive noise.

Paper X now has a SOF-internal H3 positive control:

```text
experiments/paper10/mechanism_separation_theorem.py

tau(K0_grow)  = 30
tau(K1_decay) = 1380
```

This closes the old H3 gap at the proxy layer.  The causal statement is:

```text
mechanism separation + ordered response constants -> proxy-rate separation
```

It still does not prove `K_i -> R_i/D` and does not measure `tau(D)`.

Current evidence gap:

```text
observed:
  tau(R_1) < tau(R_2)              in engineered near-threshold accessibility
  tau(K0) < tau(K1) < tau(K2)      in training-coupled NN SOF
  D_repaired = 6                  in static Clifford+CNOT quantum audit

not yet observed:
  tau(R_1) < tau(R_2) < tau(D)
  together with D_repaired > 0 along one structured deformation
```

Here `K2` is a continuous nested-commutator proxy, not the discrete
first-depth observable `D`.  A valid `tau(D)` audit needs a species with
initial frozen pairs that become accessible during a structured deformation.
The NN audit should remain proxy-only; the natural `tau(D)` targets are
structured quantum gate deformations or Rubik continuous deformations.

Open bridge:

```text
continuous proxies        K0, K1, K2
discrete shadows          R_1, R_2, D
missing bridge            Observable Proxy Shadow Principle
```

The Observable Proxy Shadow Principle is the future theorem target saying when
a continuous proxy determines, approximates, or predicts its discrete shadow.
It should require at least threshold calibration, margin stability,
sectorization stability, and compatibility between proxy order and discrete
filtration order. Until such a theorem exists, `K0/K1/K2` diagnostics remain
proxy evidence only.

Cross-domain rate-separation comparison:

| Domain | Fast channel | Slow channel | Ratio |
|--------|--------------|--------------|-------|
| Ridge regression | `theta_parallel` | `theta_perp` | about `6.7e4--6.8e4x` |
| RIME near-threshold | `R_1` | `R_2` | about `11x` |

The magnitudes are domain-dependent. The shared pattern is hierarchical
visibility: a fast channel responds first, while a slow channel becomes visible
later under the chosen deformation dynamics.

Current diagnostic status:

```text
experiments/paper9/rate_hierarchy.py
```

The Rubik local perturbation sweep is presently a flat-region negative control:
for tested perturbations near the canonical point, `R_1`, `R_2`, and `D` may
remain unchanged, so no finite threshold hierarchy is observed. This does not
disprove observable rate separation; it says the tested Rubik region is locally
stable and that rate hierarchy should be measured either across actual walls,
under larger perturbations, or in smaller SOF test systems where full depth
sweeps are tractable.

The same diagnostic also records two useful guardrails:

- one-sector SOFs collapse all cross-sector rate questions;
- changing sectorization while keeping generators fixed changes the observable
  shadows, confirming that SOF is an interface and sectorization is input data.

The richer sectorization-sensitivity run gives:

| Sectorization | Sectors | R1% | R2% | D_max | D_rep |
|---------------|---------|-----|-----|-------|-------|
| QT-only | 39 | 15.3 | 7.2 | 999 | 36 |
| HT-only | 16 | 10.0 | 3.9 | 999 | 60 |
| Mixed | 9 | 7.4 | 3.5 | 999 | 32 |

Thus sectorization changes not only support density but also the distribution
of higher-depth repair. In particular, the HT-only sectorization repairs more
frozen pairs than the mixed canonical sectorization in this diagnostic.

Rubik sectorization sensitivity can be expensive when many sectors are
generated. The exploratory script therefore skips large sectorizations by
default; increase `--max-sectors` only when full reproduction is needed. The
QT/HT alternatives in that script are random spectral-probe sectorizations, not
theorem-level joint-sector constructions.

## Wall Pullback

The current Paper IX statement should be a principle, not a theorem, unless the
admissibility hypotheses and the target discriminant are fully specified:

```text
Sigma_O subset J^{-1}(Delta_O)
```

where `O` is a discrete observable shadow and `J` is the corresponding
continuous field. Equality requires the discriminant to exactly capture the
rank, support, collision, or filtration change defining `O`.

## Deformation Species

| Species | Deformation variable | Typical dynamics |
|---------|----------------------|------------------|
| Paper IV spectral | affine projection | collision geometry |
| Paper VI accessibility | generator weights | accessibility walls |
| Yang-like filtration | state mixing | monotone degeneration |
| Neural-network SOF | activation family and training dynamics | activation-dependent sectorization and observable time-scale ratios |
| Quantum circuits | gate-set or Hamiltonian variation | channel and controllability changes |
| Markov systems | rate or transition perturbation | mixing and communicating-class changes |
| Graph systems | edge rewiring or Laplacian weighting | connectivity and spectral changes |

The intake question for any new direction is:

```text
What is changing?
```

## Neural-Network Activation SOFs

Neural networks give a concrete Paper IX prediction class:

```text
activation function = sectorization + observable-family design knob
```

Examples:

| Activation | SOF reading |
|------------|-------------|
| None | one-sector trivial SOF |
| ReLU | hard activation-frequency sectors |
| GeLU | soft response-strength sectors |
| Top-k | rank-jump winner/rest sectors |

For hidden-layer weights, one can define projected observables:

```text
R_1: Q_i W_l Q_j != 0
R_2: Q_i [W_a, W_b] Q_j != 0
D:   minimal effective composition / Lie-depth path
```

The current diagnostic is:

```text
experiments/paper9/nn_activation_sof.py
experiments/paper9/nn_training_sof_tau.py
```

The first script tests fixed weights and activation-induced sectorizations. The
second script couples a small training loop to SOF observables and measures raw
norm proxies:

```text
K0(t): R_1 support proxy
K1(t): R_2 commutator-survival proxy
K2(t): nested-depth proxy
```

The conclusion is not a training theorem: different activations produce
different sector counts and `R_1/R_2/frozen` profiles, and the training-coupled
audit is an exploratory test of `tau(K0) < tau(K1) < tau(K2)`.

Default training-coupled diagnostic:

| Activation | tau(K0) | tau(K1) | tau(K2) | Result |
|------------|---------|---------|---------|--------|
| ReLU | 60 | 80 | 120 | `K0 < K1 < K2` |
| GeLU | 60 | 80 | 120 | `K0 < K1 < K2` |

Here `K0`, `K1`, and `K2` are raw off-diagonal block-norm proxies for direct
support, commutator survival, and nested-commutator depth. They retain scale
information during training. This is why they are better suited to time-scale
measurement than the normalized binary `D` matrix.

The final binary audits remain connected at the `D` level:

| Activation | final R1 | final R2 | final D_repaired | final D_frozen |
|------------|----------|----------|------------------|----------------|
| ReLU | 4 | 2 | 0 | 0 |
| GeLU | 12 | 6 | 0 | 0 |

This also separates two effects:

```text
continuous rate hierarchy:
  K0/K1/K2 norms grow on different time scales

binary accessibility repair:
  D_repaired > 0 only when a frozen pair becomes accessible
```

In the default small NN SOF, `D_repaired` remains zero because all off-diagonal
sector pairs are already connected at the binary support level from the first
audit step. This is not a failure of the rate hierarchy. It shows that
continuous time-scale separation and binary frozen-to-accessible repair are
different observables. To see training-time D-repair, one needs more sectors,
a higher binary threshold, or an SOF with genuine initial frozen pairs.

Therefore `tau(K2)` should not be reported as `tau(D)`.  The current NN audit
supports continuous observable rate separation only.  Do not force NN to carry
the binary `D` claim; use it for proxy rates and reserve `tau(D)` for quantum
or Rubik deformation audits.

Do not write `K_i -> R_i` as an established implication.  That arrow is exactly
the open Proxy Shadow problem.

Interpretation:

```text
Paper V:  static R_1/R_2/D structures are exposed.
Paper IX: dynamic SOF processes make their rates measurable.
```

The training-coupled design choice makes the hierarchy observable: direct
support responds first, commutator survival responds later, and nested-depth
proxies respond latest in the default diagnostic. This is the intended bridge
from static accessibility classification to rate-hierarchy dynamics.

Current fixed-weight diagnostic:

| Activation | Sectors | Dims | R1 | R2 | R1 offdiag | R2 offdiag | Frozen |
|------------|---------|------|----|----|------------|------------|--------|
| None | 1 | `[24]` | 2 | 1 | 0 | 0 | 0 |
| ReLU | 2 | `[12, 12]` | 8 | 4 | 4 | 2 | 0 |
| GeLU | 3 | `[8, 8, 8]` | 18 | 9 | 12 | 6 | 0 |
| Top-2 | 2 | `[23, 1]` | 6 | 3 | 4 | 2 | 0 |

This table supports the interface claim: changing the activation changes the
sectorization and therefore the measured observable profile even with fixed
weights and fixed batch.

Paper IX prediction:

```text
changing activation families should systematically change observable
time-scale ratios tau(O_i) once weights, training, and sectorization are
coupled.
```

## External vs Internal Moduli

RIME Papers V--VII mainly study external observable moduli:

```text
generator weights -> sector arrangement / accessibility data
```

Yang-style filtration probes emphasize internal state/coherence moduli:

```text
state or coherence variation inside a fixed sector arrangement
```

These are separate deformation axes and should not be forced into a single wall
model.

## Yang-Like Filtration Boundary

Yang-style filtration probes suggest a future degeneration diagnostic:

```text
P_d(epsilon) = fraction of sector pairs with D(i,j) <= d
1 - P_d(epsilon) ~ C epsilon^alpha
```

The current RIME comparison indicates that the deformation space matters more
than the exponent. Yang-like systems deform states along a mixing path, so
entropy tends to rise and filtration plateaus may monotonically decay. RIME
accessibility deforms operator weights, so accessibility plateaus may stay
flat, oscillate, or improve.

Current decision:

- treat Yang-like systems as future Filtration SOF examples;
- do not force them into the Paper VI accessibility-wall template;
- fit exponents only after a monotone degeneration regime has been identified.

Rubik state mixing is currently a contrast case:

```text
P_d(epsilon) flat for epsilon=0..0.9
jump only at epsilon=1.0
```

Thus Rubik QT/HT sector structure resists this state-mixing deformation until
the extreme endpoint. This confirms that Yang-like state mixing and RIME
generator/accessibility deformation are different deformation geometries.

The QT generator-weight plateau diagnostic belongs to this same Paper IX
deformation layer. It computes and postprocesses

```text
P_d(epsilon) = fraction of off-diagonal sector pairs with D(i,j) <= d
```

under QT-weight perturbations, and tests whether a monotone Yang-like decay
law is meaningful for RIME accessibility data.

The support script is:

```text
experiments/paper9/plateau_under_qt_perturbation.py
```

## Oscillation Diagnostics

Generator-weight plateau data can be nonmonotone. The current exploratory FFT
diagnostic uses the sequence

```text
P_2 = [0.111, 0.111, 0.111, 0.111, 0.111, 0.111, 0.139, 0.111, 0.264]
```

and obtains:

```text
zero crossings = 3/8
oscillation score = 0.38
```

A synthetic monotone comparison has only one detrended sign crossing. The
diagnostic supports the distinction:

```text
generator-weight deformation -> oscillatory plateau dynamics
state-mixing deformation     -> flat/monotone plateau dynamics in the tested probe
```

The support script is:

```text
experiments/paper9/state_mixing_fft.py
```

## Accessibility Transfer Operators

This is linked to the horizon direction in `docs/RESEARCH_DIRECTIONS.md`.
The disciplined sequence is:

```text
SOF class
  -> canonical accessibility transfer operator T_A
  -> determinant zeta Z_A(s)=det(I-sT_A)^(-1)
  -> trace identity
  -> possible primitive-cycle expansion
```

Do not promote zeta, trace-formula, Selberg, or RH-like language into current
papers until `T_A` is a canonical construction with nontrivial examples and
clear failure modes.
