# Observable Dynamics of Sectorized Observable Frameworks

### Deformations, Rate Separation, and Observable Dynamics

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part IX of the RIME program. Paper VIII establishes the static
object layer of Sectorized Observable Frameworks: SOFs, strict morphisms,
categories, and natural accessibility constructions. Paper IX studies
observable dynamics: how SOFs deform, how observable trajectories evolve, how
different time scales appear, and why different deformation spaces produce
different observable dynamics over the same observable architecture.*

***

## Abstract

**Problem.** Paper VIII identifies the Sectorized Observable Framework (SOF)
as the common observable architecture in which the RIME observables $R_1$, $R_2$, $D$, and
$\mathcal J_{\mathrm{acc}}$ arise naturally. The next question is dynamic:
how do these observables behave when the SOF itself varies? The difficulty is
that different systems deform different data. Rubik deforms generator weights;
Yang-like systems deform states; Markov systems deform transition operators;
graphs deform adjacency or Laplacian data; quantum systems deform Hamiltonians
or gate families.

**Approach.** We define a deformation of an SOF as a parameterized family

$$
\mathcal F_t=(V_t,\{Q_i(t)\},\mathcal X(t)),
\qquad t\in T,
$$

viewed as a path in the provisional deformation category
$\mathsf{SOF}_{\mathrm{def}}$.  The notation
$\Phi_t:\mathcal F\to\mathcal F_t$ is used only as shorthand for comparison
data that allows observable shadows to be tracked along this path.
Accessibility deformations induce trajectories

$$
R_1(t),\qquad R_2(t),\qquad D(t),\qquad
\mathcal J_{\mathrm{acc}}(t).
$$

Other SOF species induce their registered analogue shadows, such as plateau
functions, spectral gaps, communicating-class profiles, or proxy norms.

Walls are defined as loci in the deformation space where an observable shadow
fails to be locally constant.

**Results.** The main structural object is observable dynamics: the collection
of trajectories, time scales, plateaus, and wall loci attached to an SOF
deformation.  The first structural principle is the Observable Wall Pullback
Principle: for an admissible SOF deformation and a discrete observable shadow
$O$, the wall of $O$ is contained in, and under exact discriminant hypotheses
is realized as, the pullback of a rank, support, spectral, or filtration
discriminant of the corresponding continuous field:

$$
\Sigma_O\subseteq\mathcal J^{-1}(\Delta_O),
$$

with equality only when the chosen discriminant exactly captures the shadow
change.

This recovers the Paper VI hierarchy

$$
\Sigma_{\mathrm{access}}
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}
$$

as the accessibility-deformation instance. A second structural theme is
observable rate separation: different observable shadows may become visible on
different characteristic time scales. This separates RIME generator-weight
deformation from Yang-like state-mixing degeneration and from parameter-space
rate separation in ridge-regression grokking.

**Implications.** Paper IX provides the dynamic counterpart to Paper VIII's
static unity. The unifying object is the SOF architecture; the central subject is
observable dynamics. The same observable ladder may produce different time
scales, plateaus, repairs, and walls because different systems move in
different deformation spaces.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $\mathcal F$ | Sectorized Observable Framework |
| $\mathcal F_t$ | deformed SOF at parameter $t$ |
| $(\mathcal F_t)_{t\in T}$ | SOF deformation trajectory / path |
| $\mathsf{SOF}_{\mathrm{def}}$ | provisional deformation category for SOF paths |
| $T$ | deformation parameter space |
| $\Phi_t:\mathcal F\to\mathcal F_t$ | shorthand for comparison data along a deformation |
| $Q_i(t)$ | moving sector projector |
| $\mathcal X(t)$ | moving observable family |
| $R_1(t)$ | support-shadow trajectory |
| $R_2(t)$ | commutator-survival trajectory |
| $D(t)$ | first-depth trajectory |
| $\mathcal J_{\mathrm{acc}}(t)$ | accessibility-jet trajectory |
| $\Sigma_O$ | wall of observable shadow $O$ |
| $\Delta_O$ | target discriminant for $O$ |
| $\tau(O)$ | characteristic time scale of an observable trajectory |
| $\Sigma_{\mathrm{comm}}$ | commutativity locus |
| $\Sigma_{\mathrm{spec}}$ | normal spectral chart |
| $\Sigma_{\mathrm{access}}$ | accessibility discriminant |

***

## Introduction

Paper VIII answers the static question:

What is a Sectorized Observable Framework?

Paper IX answers the dynamic question:

How does a Sectorized Observable Framework evolve?

The guiding principle is:

same observable architecture, different deformation geometry,
different observable dynamics.

This distinction is necessary because SOF is an observable architecture, not a
universal dynamics or wall theory. It records sectors, observables, projected
blocks, support, commutators, depth, and jets. A trajectory or wall appears only
after a deformation space has been chosen.

The central observation is that the same observable ladder can behave very
differently depending on what is allowed to vary:

| System | Deformation variable | Expected dynamics |
|--------|----------------------|-------------------|
| Rubik / RIME | generator weights or observable family | accessibility walls, fragmentation, nonmonotone plateaus |
| Yang-like filtration | state or density matrix | monotone filtration degeneration |
| Markov | transition or rate operator | communicating-class and transport changes |
| Graph | adjacency or Laplacian | rewiring, spectral jumps, transport changes |
| Quantum | Hamiltonian or gate family | circuit accessibility and spectral response |

Paper IX therefore provides **Dynamic Unity**: different deformation spaces
generate different observable dynamics over a common observable architecture.

***

## Related Work: Observable Dynamics Precedents

This paper uses related work as precedent for observable dynamics, not as
theorem support for SOF. The three most relevant external frameworks occupy
different roles.

### Rate Separation in Parameter Space

Xu, Vardi, and Safran's ridge-regression analysis of grokking
\cite{xuVardiSafran2026grokking} proves a clean rate separation between two
parameter-space directions:

$$
\theta=\theta_{\parallel}+\theta_{\perp}.
$$

The data-visible component $\theta_{\parallel}$ evolves quickly under the
empirical loss, while $\theta_{\perp}$ is controlled only by weight decay and
therefore evolves slowly. This is not an SOF theorem and not an accessibility
statement. Its relevance is structural: it shows that different directions of
a deformation may become visible on different time scales.

Paper IX studies the analogous question in observable space:

$$
O_1(t),\ldots,O_k(t)
\quad\leadsto\quad
\tau(O_1),\ldots,\tau(O_k).
$$

Neural-network activations give a concrete source of observable-space
predictions.  Changing the activation changes both the induced sectorization
and the effective observable family: a trivial linear activation gives one
sector, ReLU gives hard activation sectors, GeLU gives soft response sectors,
and Top-k activations give rank-jump sectors.  Thus the same weight matrices
may produce different $R_1/R_2$ profiles, and potentially different depth
profiles once a training filtration is specified, when viewed through different
activation-induced SOFs.  The corresponding Paper IX prediction is that
activation families can systematically change observable time-scale ratios
once the sectorized observables are coupled to training dynamics.

A small training-coupled diagnostic supports the basic rate hierarchy for raw
observable proxies: for both ReLU and GeLU, the measured half-response times
satisfy

$$
\tau(K_0)<\tau(K_1)<\tau(K_2),
$$

where $K_0$, $K_1$, and $K_2$ are raw block-norm proxies for direct support,
commutator survival, and nested-commutator depth. The computational footnote
in Section 6.6 records the default diagnostic run. This is evidence for the
observable-dynamics framing, not a theorem about all neural networks or all
activation functions.

The conceptual point is that structures classified statically in Paper V become
rate-bearing only after a dynamical process has been chosen.  The small NN
audit realizes only the proxy part of this program: direct support,
commutator-like survival, and nested-depth proxies become measurable as
continuous time scales.  It is not a test of the discrete first-depth invariant
$D$ itself.

The same diagnostic also separates continuous and binary effects.  The
$K_0/K_1/K_2$ hierarchy is a continuous norm-growth phenomenon, while
$D$-repair is a binary event in which a frozen pair becomes accessible.  In the
small NN SOF diagnostic, $D_{\mathrm{repaired}}$ remains zero because the
sector pairs are already connected at the binary support level; observing
training-time $D$-repair requires more sectors, a higher binary threshold, or a
system with genuine initial frozen pairs.

Thus the available evidence supports
$\tau(K_0)<\tau(K_1)<\tau(K_2)$ for continuous proxy observables, not an
observed $\tau(D)$ for the discrete first-depth shadow. A direct $\tau(D)$
audit requires a system with genuine binary accessibility repair, such as a
structured quantum gate deformation or a Rubik continuous deformation where
frozen sector pairs become accessible along the path.

### Prethermalization and Long Plateaus

Many-body prethermalization provides a second precedent. Abanin, De Roeck,
Ho, and Huveneers' rigorous theory of many-body prethermalization
\cite{abaninDeRoeckHoHuveneers2017prethermalization} shows that, in
high-frequency driven quantum systems, fast microscopic dynamics can coexist
with a long-lived effective Hamiltonian and a delayed heating time. This is
closer to the Paper IX viewpoint than a monotone degeneration example: it has
a fast observable regime, a long plateau, and a slow mode that becomes visible
only after a large time scale.

The SOF use is again conceptual. Prethermalization suggests that observable
plateaus and delayed wall visibility may admit quantitative time-scale bounds
in favorable deformation geometries.

### Wall-Crossing Without a Formula

Kontsevich--Soibelman wall-crossing
\cite{kontsevichSoibelman2008stability} demonstrates that, in some settings,
invariants jumping across walls admit exact transformation laws. The SOF
framework developed here has wall loci and observable shadows, but no
wall-crossing formula.

Thus KS wall-crossing belongs in discussion, not in the theorem layer:

| Framework | Wall data |
|-----------|-----------|
| KS | wall plus exact transformation formula |
| SOF | wall plus observable shadow; transformation formula open |

An exact transformation law across $\Sigma_O$ is therefore an additional
structure to be proved for a restricted SOF class, not part of the present
framework.

***

## SOF Deformations

### SOF Deformation Definition

Let

$$
\mathcal F=(V,\{Q_i\}_{i\in I},\mathcal X)
$$

be an SOF. A **deformation** of $\mathcal F$ over a parameter space $T$ is a
family

$$
\mathcal F_t=(V_t,\{Q_i(t)\}_{i\in I_t},\mathcal X(t)),
\qquad t\in T,
$$

together with comparison data identifying the objects along the family on the
parameter region where such identification is meaningful.

The primary dynamic object is the path or family

$$
(\mathcal F_t)_{t\in T}
$$

in the provisional deformation category $\mathsf{SOF}_{\mathrm{def}}$, not
merely an endpoint arrow $\mathcal F_{t_0}\to\mathcal F_{t_1}$.  Observable
trajectories are paths in $\mathsf{SOF}_{\mathrm{def}}$ after the relevant
comparison data have been specified.

![Observable trajectory. Paper IX treats observable dynamics as paths
$(\mathcal F_t)_{t\in T}$ whose shadows $R_1(t)$, $R_2(t)$, $D(t)$, and
$\mathcal J_{\mathrm{acc}}(t)$ are tracked only where the corresponding
comparison data are admissible.](../../figures/paper9/fig1_observable_trajectory.png)

In the simplest fixed-space case,

$$
V_t=V,\qquad
\mathcal F_t=(V,\{Q_i(t)\},\mathcal X(t)).
$$

In a fixed-sector deformation,

$$
Q_i(t)=Q_i,\qquad
\mathcal X(t)\text{ varies}.
$$

In a moving-sector deformation, both $\{Q_i(t)\}$ and $\mathcal X(t)$ may
vary.

### Deformation Map

For a fixed base object, a deformation can be written schematically as

$$
\Phi_t:\mathcal F\longrightarrow\mathcal F_t.
$$

This notation does not mean that $\Phi_t$ is necessarily a strict SOF
morphism. In Paper IX, $\Phi_t$ records the comparison data used to track
observable shadows along the path $(\mathcal F_t)_{t\in T}$. Strict morphisms
belong to the static category of Paper VIII.

### Working Deformation Category

For the purposes of Paper IX, the ambient dynamic category is the provisional
category

$$
\mathsf{SOF}_{\mathrm{def}}.
$$

Its objects are finite SOFs. A morphism

$$
\mathcal F\rightsquigarrow \mathcal G
$$

is a deformation datum consisting of:

1. a parameter space $T$ with marked endpoints $t_0,t_1$;
2. a family of SOFs $\{\mathcal F_t\}_{t\in T}$;
3. endpoint identifications $\mathcal F_{t_0}\simeq \mathcal F$ and
   $\mathcal F_{t_1}\simeq \mathcal G$ in whatever weak sense is sufficient for
   the chosen diagnostic;
4. comparison data along $T$ allowing the relevant observable shadows
   $R_1(t),R_2(t),D(t),\mathcal J_{\mathrm{acc}}(t)$, or their analogues, to be
   evaluated consistently.

Composition is concatenation of deformation data when the endpoint comparison
data are compatible; the identity arrow is the constant deformation. This is
not the strict category $\mathsf{SOF}_{\mathrm{str}}$ of Paper VIII. A
deformation morphism may be non-isometric, may change sector dimensions, and
may preserve only support, rank, norm, plateau, or rate diagnostics. Its role
is to make observable trajectories well-defined, not to preserve all natural
SOF constructions strictly.

The full theory of weak SOF morphisms is left open. Paper IX only uses the
minimal deformation-category language needed to locate $\Phi_t$ formally and
to separate dynamic comparison from strict static naturality.

For the observable claims below, **admissible** means:

1. the path $\{\mathcal F_t\}_{t\in T}$ is equipped with comparison data for
   the diagnostic under discussion;
2. the relevant sectors, or their registered analogues, can be tracked along
   the path on the domain being studied;
3. the continuous field underlying the diagnostic is defined along that
   domain;
4. the discrete shadow is locally constant away from the corresponding
   rank, support, collision, filtration, or wall discriminant.

Thus admissibility is not automatic for every formal deformation in
$\mathsf{SOF}_{\mathrm{def}}$. It is a hypothesis attached to the chosen
observable diagnostic.

### Observable Trajectories

An admissible accessibility deformation induces trajectories of the
accessibility shadows:

$$
R_1(t),\qquad
R_2(t),\qquad
D(t),\qquad
\mathcal J_{\mathrm{acc}}(t).
$$

Other SOF species induce the shadows registered for that branch:

| Branch | Additional shadow |
|--------|-------------------|
| Spectral SOF | joint spectral arrangement, collision quotient |
| Accessibility SOF | accessibility jet, wall hierarchy |
| Filtration SOF | plateau functions $P_d(t)$ |
| Markov SOF | communicating-class or transport profile |
| Graph SOF | spectral gap, connectedness, Laplacian rank |

***

## Walls as Observable Discontinuities

### Wall Definition

Let $O$ be an observable shadow defined along a deformation
$\mathcal F_t$. The **wall** of $O$ is the locus

$$
\Sigma_O
=
\{t\in T:O(\mathcal F_t)\text{ is not locally constant at }t\}.
$$

If $O$ is continuous rather than discrete, the wall is replaced by the
discriminant where its rank, support, stratification type, or qualitative
regime changes.

### Examples

For accessibility:

$$
\Sigma_{R_1},\qquad
\Sigma_{R_2},\qquad
\Sigma_D
$$

record changes in support, commutator survival, and first-depth accessibility.

For spectral geometry:

$$
\Sigma_{\mathrm{spec}}
$$

records the domain where joint spectral projectors vary coherently, while
internal spectral walls record collisions, field changes, or arrangement
changes.

For filtration geometry, a plateau wall is a locus where

$$
P_d(t)=\#\{(i,j):D_t(i,j)\le d\}
$$

changes qualitative behavior.

***

## Observable Wall Pullback

### Principle 1 (Observable Wall Pullback)

Let $\mathcal F_t$ be an admissible SOF deformation and let $O$ be a discrete
observable shadow obtained from a continuous block, commutator, spectral, jet,
or filtration field

$$
\mathcal J:T\to\mathcal E.
$$

Suppose $O$ is locally constant on the complement of a discriminant
$\Delta_O\subseteq\mathcal E$. Then the wall of $O$ is contained in the
pullback

$$
\Sigma_O\subseteq \mathcal J^{-1}(\Delta_O).
$$

If the admissibility hypotheses are strengthened so that $\Delta_O$ exactly
captures the rank, support, collision, or filtration changes defining $O$,
then

$$
\Sigma_O= \mathcal J^{-1}(\Delta_O).
$$

![Wall pullback principle. Observable walls are contained in pullbacks of
rank, support, spectral, or filtration discriminants along admissible
observable fields. Equality is asserted only under exact discriminant
hypotheses.](../../figures/paper9/fig2_wall_pullback.png)

### Justification

By assumption, $O$ is locally constant whenever $\mathcal J(t)$ remains in a
single stratum of $\mathcal E\setminus\Delta_O$. Therefore a failure of local
constancy can occur only when $\mathcal J(t)$ meets the discriminant. This
gives the inclusion. If the discriminant is defined to be exactly the locus
where the relevant rank, support, collision, or filtration type changes, then
every point in the pullback is a wall point for $O$, giving equality.

### Paper VI as an Instance

In Paper VI, the admissible deformation space is the generator-set moduli
space restricted to normal spectral charts:

$$
\Sigma_{\mathrm{spec}}\subseteq\Sigma_{\mathrm{comm}}.
$$

The accessibility jet

$$
\mathcal J_{\mathrm{acc}}
=
(J_{\mathrm{block}},J_{\mathrm{comm}},J_{\mathrm{depth}})
$$

is the continuous field. When $\Delta_{\mathrm{access}}$ is taken as the exact
accessibility discriminant, the accessibility wall is the pullback of the
rank/support discriminant:

$$
\Sigma_{\mathrm{access}}
=
\mathcal J_{\mathrm{acc}}^{-1}(\Delta_{\mathrm{access}}),
$$

with

$$
\Sigma_{\mathrm{access}}
\subseteq
\Sigma_{\mathrm{spec}}
\subseteq
\Sigma_{\mathrm{comm}}.
$$

This is the prototype for the Paper IX framework.

***

## Deformation Species

### Generator Deformation

In RIME generator deformation, the sectorized observable family changes by
varying generator weights or observable weights:

$$
X_g\mapsto X_g(w).
$$

This deformation redistributes transport. Its wall behavior can include
sector fragmentation, $R_1/R_2/D$ jumps, stable plateaus, oscillation, or
temporary accessibility improvement.

### State-Mixing Deformation

In Yang-like filtration systems, the natural deformation is state mixing:

$$
\rho(\varepsilon)
=
(1-\varepsilon)\rho_0+\varepsilon\sigma.
$$

This tends to be entropy-increasing and naturally supports monotone plateau
degradation:

$$
1-P(\varepsilon)\sim C\varepsilon^\alpha.
$$

This is a different geometry from generator-weight deformation.

### Markov Deformation

For Markov systems, one may deform a transition or rate operator:

$$
P\mapsto P(\varepsilon),
\qquad
L_M\mapsto L_M(\varepsilon).
$$

Walls may correspond to changes in communicating classes, absorbing
components, stationary structure, or transport support.

### Graph Deformation

For graph systems, one may deform adjacency or Laplacian data:

$$
A\mapsto A(\varepsilon),
\qquad
L\mapsto L(\varepsilon).
$$

Walls may correspond to edge rewiring, connectedness changes, spectral
collisions, Laplacian rank changes, or transport-profile changes.

### Quantum Deformation

For quantum systems, one may deform Hamiltonians, gate families, or circuit
generators:

$$
H\mapsto H(\varepsilon),
\qquad
U_g\mapsto U_g(\varepsilon).
$$

Walls may correspond to spectral transitions, controllability changes,
entangling-channel changes, or accessibility-channel changes relative to a
chosen sectorization.

### Computational Footnote: Training-Coupled NN Deformation

A small neural-network SOF gives a concrete diagnostic for observable
rate-separation under a specified training dynamics.  The sectorization is
activation-induced, the observable family is derived from trainable weight
operators, and the measured quantities are raw off-diagonal block-norm proxies

$$
K_0(t),\qquad K_1(t),\qquad K_2(t),
$$

for direct support, commutator survival, and nested-commutator depth.  These
continuous proxies retain scale information, unlike the normalized binary
depth matrix.

In the default run of
`experiments/paper9/nn_training_sof_tau.py`, both ReLU and GeLU satisfy

$$
\tau_{50}(K_0)<\tau_{50}(K_1)<\tau_{50}(K_2).
$$

| Activation | $\tau_{50}(K_0)$ | $\tau_{50}(K_1)$ | $\tau_{50}(K_2)$ | final binary audit |
|------------|------------------|------------------|------------------|--------------------|
| ReLU | 60 | 80 | 120 | $R_1=4$, $R_2=2$, $D_{\mathrm{repaired}}=0$ |
| GeLU | 60 | 80 | 120 | $R_1=12$, $R_2=6$, $D_{\mathrm{repaired}}=0$ |

![Training-coupled NN proxy rate hierarchy. In the default diagnostic,
$K_0$, $K_1$, and $K_2$ exhibit ordered half-response times
$60<80<120$. This is proxy-rate evidence only; it does not identify
$\tau(K_2)$ with a binary $\tau(D)$ event.](../../figures/paper9/fig3_nn_rate_hierarchy.png)

The claim status is computational diagnostic only. The result supports
observable time-scale separation under this training-coupled deformation, but
it does not claim binary $D$-repair: in this small SOF all sector pairs are
already connected at the binary depth level throughout the audit.

Consequently, neural-network SOFs are used here only for proxy-rate
diagnostics. A positive control for $\tau(D)$ requires a species with genuine
binary repair, for example a structured entangling-gate deformation or a Rubik
continuous deformation.

### Open Bridge: The Proxy Shadow Principle

The preceding diagnostic exposes a formal gap between two observable layers:

the continuous proxy layer $K_0(t),K_1(t),K_2(t)$ and the discrete shadow
layer $R_1(t),R_2(t),D(t)$.

There is no theorem in this paper identifying $K_i$ with the corresponding
discrete shadow. In particular,

$$
K_2(t)\quad\not\Rightarrow\quad D(t)
$$

without an additional bridge theorem controlling thresholds, margins, and
shadow stability.

We refer to the missing bridge as the **Observable Proxy Shadow Principle**.
In a future theorem-level form, such a principle would specify hypotheses under
which a continuous observable proxy $K_i(t)$ determines, approximates, or
predicts the corresponding discrete shadow $R_i(t)$ or $D(t)$. At minimum, one
expects conditions such as:

1. a fixed threshold or calibration rule from proxy norms to binary shadows;
2. a margin condition excluding near-threshold ambiguity;
3. stability of the sectorization along the measured interval;
4. compatibility between proxy order and the discrete filtration order.

Paper IX does not assume this principle.  Until such a bridge is proved,
$K_0/K_1/K_2$ audits are proxy diagnostics only. They support the broader
observable-dynamics viewpoint, but they do not prove rate separation for
$R_1/R_2/D$.

### Example Claim-Status Stratification

The examples in this paper are deliberately separated by claim status. Their
role is not to accumulate many unrelated systems, but to show which kinds of
evidence support observable dynamics and which kinds mark boundary cases.

| Class | Examples used here | Supports | Does not support |
|-------|--------------------|----------|------------------|
| Positive dynamics | Paper VI generator-weight deformation on normal spectral charts; Rubik generator-weight plateau/oscillation diagnostics; engineered near-threshold accessibility with $\tau(R_1)<\tau(R_2)$ | observable trajectories and species-dependent wall behavior | a universal wall law or a full $\tau(R_1)<\tau(R_2)<\tau(D)$ theorem |
| Negative or degenerate boundary | Yang-like state mixing; static additive noise that perturbs Lie layers simultaneously; discrete graph rewiring or unstructured quantum interpolation when no smooth mechanism-separated dynamics is specified | deformation geometry matters; the same observable architecture can produce different or degenerate wall behavior | failure of SOF itself |
| Proxy-only diagnostics | training-coupled NN audits of $K_0/K_1/K_2$; Xu--Vardi--Safran ridge dynamics as parameter-space precedent | continuous observable or parameter rate separation | binary $D$-repair, $\tau(D)$, or a proved $K_i\to R_i/D$ bridge |

Static positive witnesses, such as Clifford+CNOT giving non-Rubik
$D_{\mathrm{repaired}}>0$, are important for the registry but are not yet
dynamic $\tau(D)$ audits. Paper IX therefore treats them as static repair
witnesses rather than as completed rate-hierarchy evidence.

***

## Rubik and Yang: A Diagnostic Contrast

The Rubik/Yang comparison illustrates why Paper IX is needed.

Both systems can be described by the same observable architecture. Both can
produce plateau functions. But they deform different data.

Yang-like deformation changes the state:

$$
\rho(\varepsilon)=(1-\varepsilon)\rho_0+\varepsilon\sigma.
$$

This is a degeneration geometry. It naturally suggests laws such as

$$
1-P(\varepsilon)\sim C\varepsilon^\alpha.
$$

RIME deformation changes observables or generator weights:

$$
X_g\mapsto X_g(w).
$$

This is a transport-redistribution geometry. The plateau functions

$$
P_d(w)
$$

need not degrade. They may remain constant, oscillate, or improve.

The diagnostics make this distinction concrete.  Under a Rubik
state-mixing probe, the plateau functions remain flat for
$\varepsilon=0,\ldots,0.9$ and jump only at the extreme endpoint
$\varepsilon=1$.  Under generator-weight deformation, the observed plateau
sequence is oscillatory:

$$
P_2=(0.111,0.111,0.111,0.111,0.111,0.111,0.139,0.111,0.264),
$$

with three detrended sign changes out of eight intervals and oscillation score
$0.38$. Thus state mixing and generator-weight deformation produce different
observable dynamics even when they are described in the same sectorized
language.

![Yang-like state mixing versus RIME generator weights. Both diagnostics use
plateau-style observable architecture, but state mixing produces endpoint
degeneration while generator-weight deformation produces oscillatory,
nonmonotone behavior.](../../figures/paper9/fig4_yang_vs_rime.png)

The diagnostic scripts separate these two roles: the QT perturbation audit
computes plateau functions under generator-weight deformation, while the
state-mixing/FFT audit summarizes endpoint stability and oscillation.

Therefore the distinction is not the observable architecture. The distinction is
the deformation geometry.

### Observable Rate-Separation Dynamics

The natural object in RIME is not a parameter vector but an observable
trajectory.  Thus the relevant abstraction is **observable time-scale
separation**.

Let

$$
O_1(t),\ldots,O_k(t)
$$

be observable shadows or continuous fields induced by an SOF deformation.  If
one can assign characteristic time scales

$$
\tau(O_1),\ldots,\tau(O_k)
$$

and at least two of them are separated, then the deformation is called
**observable rate-separated**.

For accessibility deformations, a candidate hierarchy under structured
dynamical perturbations is

$$
\tau(R_1)<\tau(R_2)<\tau(D)
$$

whenever direct support changes first, commutator survival changes next, and
depth repair is visible only after slower channels enter the observable
shadow.  This is the accessibility analogue of a fast/intermediate/slow
observable hierarchy, but it is not a claim about arbitrary static additive
noise.

At present this remains a target hierarchy, not a completed empirical theorem:
the available diagnostics show $\tau(R_1)<\tau(R_2)$ in an engineered
near-threshold system and $\tau(K_0)<\tau(K_1)<\tau(K_2)$ in a
training-coupled NN SOF, while the available runs do not simultaneously observe
$\tau(R_1)<\tau(R_2)<\tau(D)$ together with
$D_{\mathrm{repaired}}>0$. The quantum Clifford+CNOT audit provides a static
non-Rubik example with $D_{\mathrm{repaired}}=6$, but it does not yet provide a
structured deformation from which $\tau(D)$ can be measured. Thus NN supplies
proxy-rate evidence, while quantum or Rubik deformations remain the natural
candidates for the first genuine $\tau(D)$ audit.

A related diagnostic appears in Xu, Vardi, and Safran's ridge-regression
analysis of grokking \cite{xuVardiSafran2026grokking}. Their model separates
the parameter vector into a row-space component and an orthogonal component:

$$
\theta=\theta_{\parallel}+\theta_{\perp}.
$$

The row-space component is driven directly by empirical loss and converges
quickly. The orthogonal component is invisible to the training data and is
controlled only by weight decay, producing a delayed generalization transition.

This is not the same observable as RIME accessibility. Their theorem proves a
rate separation in parameter space; Paper IX uses it as a comparison point for
rate separation in observable space.  The common higher-level phenomenon is
that different directions of a deformation may become visible on different
time scales.

In the SOF architecture, the template is:

visible channel $\to$ fast observable change, while hidden channel $\to$ slow
deformation-controlled repair.

Ridge regression has

$$
\tau(\theta_{\parallel})\ll \tau(\theta_{\perp}),
$$

while a RIME accessibility deformation may have

$$
\tau(R_1)<\tau(R_2)<\tau(D).
$$

The objects are different, but both are rate hierarchies.  Wall crossing is
observable only when the slow modes become visible to the chosen observable
shadow.

![Xu-style parameter-to-observable bridge. Ridge-regression rate separation
is theorem-level evidence in parameter space. Paper IX uses it only as a
bridge precedent for observable-space rate separation; the proxy-shadow bridge
from $K_i(t)$ to $R_i(t)$ or $D(t)$ remains open.](../../figures/paper9/fig5_xu_parameter_observable_bridge.png)

This distinction matters.  In engineered near-threshold accessibility systems,
one may observe

$$
\tau(R_1)<\tau(R_2),
$$

while static additive noise can make $D$ change earlier by injecting accidental
directions into higher Lie-filtration layers.  Thus $\tau(D)$ is meaningful
only after the deformation model specifies how first-order support,
commutator-survival, and nested Lie-depth effects are coupled.  Paper IX
therefore treats rate hierarchy as a property of observable dynamics under a
specified deformation model, not as a universal consequence of adding noise to
generators.

![Provisional deformation category. The dynamic layer uses
$\mathsf{SOF}_{\mathrm{def}}$ as a weak home for paths equipped with endpoint
identification, sector tracking, observable tracking, and diagnostic
admissibility. This is deliberately weaker than the strict SOF morphisms of
Paper VIII.](../../figures/paper9/fig6_sof_def_category.png)

The diagnostic values are:

| Domain | Fast channel | Slow channel | Ratio |
|--------|--------------|--------------|-------|
| Ridge regression | $\theta_{\parallel}$ | $\theta_{\perp}$ | $68553\times$ |
| RIME near-threshold | $R_1$ | $R_2$ | about $10.8$ |
| NN training-coupled SOF | $K_0$ | $K_2$ proxy | ordered proxy half-response $60<80<120$ |

The ratios are not meant to be numerically comparable across domains. The
shared structure is hierarchical visibility under a specified deformation.

***

## Outlook

Paper IX establishes the dynamic layer:

$$
\begin{aligned}
\mathrm{SOF}
&\longrightarrow \text{deformation space}
\longrightarrow \text{observable trajectories}\\
&\longrightarrow \text{wall discriminants}.
\end{aligned}
$$

Paper X then turns these trajectories into registry evidence:

$$
\begin{aligned}
\mathrm{SOF\ Registry}
&\longrightarrow \text{registered species}
\longrightarrow \text{observable diagnostics}\\
&\longrightarrow \text{pipeline-level comparison principles}.
\end{aligned}
$$

The comparison question for Paper X is not whether these systems are strictly
isomorphic as SOFs. In general they are not. The question is whether
observable phenomena persist across admissible registry entries:

Which wall invariants, plateau laws, accessibility repairs, or completion
principles survive across different SOF species?

***

## What This Paper Does Not Claim

Paper IX does not claim:

1. a universal observable dynamics or wall geometry for all SOF deformations;
2. that Yang-like filtration degeneration and RIME accessibility walls are the
   same object;
3. that monotone exponent laws apply to generator-weight deformation;
4. that parameter-space rate separation and observable-space rate separation
   are identical;
5. that every deformation is smooth or has a single discriminant type;
6. that the NN diagnostics in this paper exhibit binary $D$-repair;
7. that the program has already observed a full
   $\tau(R_1)<\tau(R_2)<\tau(D)$ trajectory with
   $D_{\mathrm{repaired}}>0$;
8. that the Observable Proxy Shadow Principle has been proved;
9. unconditional generic completion.

The stable claim is:

SOF provides the common observable architecture; deformation geometry determines
the observable dynamics.

***

## References

**Program lineage.** Paper VIII supplies the static SOF object layer and the
naturality theorem for accessibility observables \cite{paper8}. Paper IX
studies deformation geometry over that object layer. Paper VI is the main RIME
accessibility-deformation prototype \cite{paper6}; Paper V supplies the
length-2 repair calculus \cite{paper5}; and Paper VII supplies the generic
completion boundary that later deformation theory must respect \cite{paper7}.

**Related observable-dynamics precedents.** Xu, Vardi, and Safran, "To Grok
Grokking: Provable Grokking in Ridge Regression," arXiv:2601.19791
\cite{xuVardiSafran2026grokking}, provides a clean parameter-space example
where different directions evolve on different time scales. Abanin, De Roeck,
Ho, and Huveneers, "A Rigorous Theory of Many-Body Prethermalization for
Periodically Driven and Closed Quantum Systems," Communications in
Mathematical Physics 354 (2017), 809--827, arXiv:1509.05386
\cite{abaninDeRoeckHoHuveneers2017prethermalization}, provides a many-body
example of fast dynamics, long plateaus, and delayed slow-mode visibility.
Kontsevich and Soibelman, "Stability structures, motivic Donaldson--Thomas
invariants and cluster transformations," arXiv:0811.2435
\cite{kontsevichSoibelman2008stability}, provides a precedent for exact
transformation laws across walls; the SOF framework in this paper has wall
loci and observable shadows, not such a formula.
