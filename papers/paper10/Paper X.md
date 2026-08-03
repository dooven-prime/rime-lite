# Capability-Aware Compilation for Sectorized Observable Frameworks

### Typed Admission and Cross-Species Registry Evidence

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper is Paper X of the RIME program. It develops capability-aware
compilation and Registry evidence over the static and dynamic interfaces of
Papers VIII and IX, while keeping compiler soundness distinct from adapter
adequacy and automatic Registry ingestion.*

***

## Abstract

**Problem.** Paper VIII defines the static Sectorized Observable Framework
(SOF), and Paper IX develops its dynamic architecture. This paper asks which
conclusions a common interface may emit after a source adapter has declared
its admission kind, capabilities, carriers, policies, and evidence. The
challenge is to preserve these distinctions while compiling heterogeneous
records into capability-sound reports.

**Approach.** We formulate a capability-aware compilation interface:

$$
\begin{aligned}
\text{Capability Manifest}
&\longrightarrow \text{Typed SOF IR}\\
&\longrightarrow \text{Profile-Gated Compilation}
\longrightarrow \text{Capability-Sound Compiler Output}.
\end{aligned}
$$

Strict admission factors through Paper VIII; dynamic fields are inherited from
Paper IX. The Manifest declares availability; the IR records typed objects,
findings, evidence, and derivations; and the Profile specifies Boolean module
requirements and forbidden promotions.

**Results.** The Capability-Sound Compiler v1 Emission Theorem states that every
affirmative claim item emitted by the algorithm has an eligible typed IR source
and a valid derivation. Its claim-local carrier, convention, policy, evidence,
and promotion checks must pass.
Unavailable states, unresolved derivations, and forbidden promotions cannot
produce affirmative conclusions. Strict SOF and diagnostic-analogue admission
remain disjoint, and missing capability is not interpreted as zero. Registry
v2.0 separately provides a source-addressed evidence interface with sparse
capabilities and a reproducible census certificate.

**Boundary.** Compiler soundness does not establish scientific adequacy of an
adapter, identify different carriers, or prove common cross-species dynamics.
Compiler Output v1.0 is not yet a serialized SOFRS report.
Registry v2.0 and Compiler v1.0 remain parallel compatible interfaces until a
versioned Registry-to-IR adapter is supplied.

***

## Notation Table

| Symbol | Meaning |
|--------|---------|
| $\mathcal F=(V,Q,Y;X,\mathcal H)$ | typed Sectorized Observable Framework, with optional Lie/Hall filtration $\mathcal H=\{\mathcal H_d\}_{d\geq0}$ |
| $\mathcal R$ | SOF Registry |
| $\mathsf{Cap}(\mathcal E)$ | capability declaration of a Registry entry |
| strict SOF | finite complex $(V,Q,Y)$ realization satisfying structural admission |
| diagnostic analogue | source descriptor and analogue mapping without a strict SOF theorem instance |
| $R_1[Y]$, $\mathrm{Route}_d[Y]$, $W_d[Y]$ | operator, route, and word channels |
| $D_{\mathrm{route}}[Y]$, $D_{\mathrm{word}}[Y]$ | typed route and word depths |
| $R_1^{\mathrm{Lie}}$, $R_2^{\mathrm{Lie}}$, $D_{\mathrm{Lie}}$ | independently registered Lie/Hall channels |
| $K_0,K_1,K_2$ | raw norm proxies for direct, commutator, and nested-depth observables |

***

## Introduction

Papers VIII and IX establish the static SOF object language and its dynamic
trajectory layer, respectively \cite{paper8,paper9}. This paper addresses two
interface questions:

1. How can different source systems enter a single typed reporting interface
   without forcing them into the same carrier, diagnostic, or claim status?
2. Which conclusions may be emitted once admission, capabilities, policies,
   and evidence have been declared?

This compilation interface is not a new structural decomposition theorem.

Classical Wedderburn--Artin theory decomposes semisimple representations into
structural blocks \cite{curtisReiner1962,serre1977,lam2001}. This paper starts above that
layer and asks how sectorized observables, typed channels, dynamics, and
diagnostics are organized once a structural or native representation has been
chosen.

The guiding principle is:

different sources, explicit typed admission, capability-gated compilation,
and no unsupported promotion.

This paper treats capability-sound compiler emission as the theorem-level
object. The Registry is compatible evidence architecture: it records which
sources are admitted, which capabilities and carriers are declared, and which
findings are validated. Registry v2.0 and Compiler v1.0 are parallel
interfaces here. No versioned Registry-to-IR adapter is specified, so
a Registry row does not by itself enter a Report Profile compilation.

Registry admission is capability-sparse. A source enters the strict branch
only after satisfying the realization criteria. Sources that expose useful
structural descriptors without a complete finite-dimensional complex
realization $(V,Q,Y)$ may enter only as diagnostic analogues.

***

## Related Work and Novelty Boundary

**Program lineage.** This paper builds on the SOF object language of Paper VIII
\cite{paper8} and the observable-dynamics language of Paper IX \cite{paper9}.
Registry entries used here reuse the fixed spectral geometry of Paper IV
\cite{paper4}, the accessibility calculus of Paper V \cite{paper5}, the
normality-gated point registrations and linearized moving-field interface of
Paper VI \cite{paper6}, and the projected-composition incidence geometry,
rank-protection results, and promotion limits of Paper VII \cite{paper7}.

**External background.** The representation-theoretic structural layer is the
standard finite-dimensional semisimple/Wedderburn--Artin background
\cite{curtisReiner1962,serre1977,lam2001}; SOF adds an observable layer above
that decomposition. The rate-separation precedent is Xu--Vardi--Safran's
ridge-regression grokking model \cite{xuVardiSafran2026grokking}. Dynamic
precedents for plateaus and wall crossing belong to the Paper IX deformation
layer and are cited there \cite{paper9}; this paper uses only the resulting typed
findings and policies.

**Compiler and evidence interfaces.** Type and effect systems motivate the
separation of object identity, available operations, and checked effects
\cite{cardelli1996typesystems,lucassen1988effects}. Schema evolution work
clarifies why a change of required fields or meanings needs an explicit
version transition rather than silent reinterpretation
\cite{banerjee1987schema}. Scientific provenance provides the source,
transformation, and digest discipline used by the artifact graph
\cite{simmhan2005provenance,buneman2001provenance}. Model cards and datasheets
provide precedents for evidence-aware reporting and explicit scope boundaries
\cite{mitchell2019modelcards,gebru2021datasheets}. This work does not reproduce
those systems; it specializes their interface concerns to carrier-qualified
mathematical claims and proof- or certificate-sensitive promotion.

**Novelty boundary.** This paper does not redefine the static objects of Paper
VIII or the dynamic fields of Paper IX. Its contribution is the
capability-sound compilation layer and its Registry evidence architecture:
validated declarations, typed findings, evidence-qualified derivations, and
graceful degradation determine which claim items a compiler may emit.

***

## Capability-Aware Observable Compilation

### Pipeline Interface

The common structure behind the registered examples is not a shared native
coordinate system.  It is a shared pipeline:

$$
\begin{aligned}
\text{source system}
&\longrightarrow \text{adapter and admission}
\longrightarrow \text{Capability Manifest}\\
&\longrightarrow \text{Typed SOF IR}
\longrightarrow \text{Report Profile}
\longrightarrow \text{Compiler Output v1.0}.
\end{aligned}
$$

The common object is a compilation interface, not a shared result tuple. Strict
records factor through the static SOF core; diagnostic analogues use a separate
mapping and negative boundary. Both can use the evidence interface, but only
validated capabilities can enable report modules.

![Capability-sound observable compilation. Source adapters produce an
admission record, Capability Manifest, and Typed SOF IR. Compiler v1 emits only
claims selected by the Report Profile and supported by declared capabilities,
policies, and evidence.](../../figures/paper10/fig1_capability_compilation.png)

The compiler pipeline is implemented by the contract fixtures listed in
Appendix A. Although Registry v2.0 uses compatible typed fields, it is not an
input fixture for that implementation: its `capability_manifest` and
`typed_sof_ir` contract references remain intentionally null until a versioned
Registry-to-IR adapter is defined. The Registry census certificate and
compiler-contract certificate are therefore separate Computational
Certificates.

The compiler output is a typed collection of affirmative claim items and
degradation items. It is not yet a versioned SOFRS report artifact;
serialization, presentation, and report-level epistemic metadata belong to
Paper XII \cite{paper12}.

### Construction 1 (Strict Admission Factorization)

Let a source $\mathcal S$ supply:

1. a finite-dimensional complex Hilbert space $V$;
2. a complete labelled orthogonal sectorization $\{Q_i\}$;
3. a finite observable extraction rule producing a labelled operator family
   $Y$, together with any separately declared Lie/Hall registration
   $(X,\mathcal H)$, where
   $\mathcal H=\{\mathcal H_d\}_{d\geq0}$ is the declared formal-expression
   filtration and depth convention.

Relative to the declared choices, these data determine the typed SOF core

$$
\mathcal F_{\mathcal S}=(V,Q,Y;X,\mathcal H),
$$

and the static constructions supported by its declared enrichments. Here the
entries after the semicolon are omitted when no Lie/Hall enrichment is declared.
The definitions of the linear layers, closures, filtrations, and optional Lie/Hall
carrier belong to Paper VIII \cite{paper8}; they are not repeated here. This
factorization does not itself declare a route, word, Lie/Hall, deformation,
closure-certificate, or report capability.

### Compiler v1 Semantics

The compiler is bound to **Capability Manifest v1.0**, **Typed SOF IR v1.0**,
and **Report Profile v1.0**. Its output item type is the disjoint union

$$
\mathsf{CompilerItem}_{v1}
=
\mathsf{ClaimItem}_{v1}
\sqcup
\mathsf{DegradationItem}_{v1}.
$$

Thus

$$
\operatorname{Compile}_{v1}(M,I,P)
\in
\operatorname{List}(\mathsf{CompilerItem}_{v1}),
$$

with projections $\operatorname{AffirmativeClaims}$ and
$\operatorname{Degradations}$. Claim items retain the emitting module, source
IR claim, carrier references, result state, evidence level, and derivation
references. Degradation items retain the omitted module or claim and the gate
that failed.

For a typed IR source package $x$ and candidate claim $c$, write

$$
\operatorname{Eligible}_{M,P}(x,c)
$$

when the following checks pass: admission, module capability, carrier,
convention, claim-local policy, result state and evidence, and promotion
permission. This predicate does not assert that $c$ follows from $x$. Write

$$
I\vdash_{\mathrm{derive}}x\Rightarrow c
$$

for the separate derivation relation generated by identity emission and valid
v1.0 rule-registry derivations whose hypotheses and condition checks are
satisfied. Open rules and unresolved derivations do not belong to this
relation. Finally, write $I\models_{\mathrm{scope}}c$ when the typed IR and a
sound registered derivation support $c$ with its declared carrier, scope,
hypotheses, and evidence level. For a Computational Observation, this denotes
bounded evidential support rather than theorem status.

The executable $\operatorname{Compile}_{v1}$ validates the contract triple,
traverses profile modules in declared order, emits a degradation item for a
blocked module or ineligible selected claim, and emits a claim item only after
both $\operatorname{Eligible}_{M,P}(x,c)$ and
$I\vdash_{\mathrm{derive}}x\Rightarrow c$ succeed.

### Theorem 1 (Capability-Sound Compiler v1 Emission)

Let $M$ be a schema-valid Capability Manifest v1.0, let $I$ be a Typed SOF IR
v1.0 whose references and result-state/evidence pairs validate against $M$,
and let $P$ be a Report Profile v1.0 applicable to the admission kind of $M$.
Assume that every theorem-status rule used by
$\vdash_{\mathrm{derive}}$ is sound within its registered scope. If

$$
c\in\operatorname{AffirmativeClaims}
\bigl(\operatorname{Compile}_{v1}(M,I,P)\bigr),
$$

then there is a typed IR source package $x$ such that

$$
\operatorname{Eligible}_{M,P}(x,c)
\quad\text{and}\quad
I\vdash_{\mathrm{derive}}x\Rightarrow c.
$$

Consequently $I\models_{\mathrm{scope}}c$. In particular, a `NOT_DECLARED` or
`NOT_APPLICABLE` state, an unchecked or failed derivation condition, or a
forbidden promotion cannot generate an affirmative claim item. A diagnostic
analogue cannot instantiate a strict-SOF theorem claim.

### Proof

Proceed by induction over the ordered module-emission rules of
$\operatorname{Compile}_{v1}$. If record-kind applicability or a module's
Boolean capability, object, convention, or run-policy expression fails, the
corresponding rule emits only a degradation item, so it contributes no element
to $\operatorname{AffirmativeClaims}$.

Consider an enabled module. The candidate-selection rule first filters by
carrier kind, result state, and claim status. It then re-evaluates the module
expressions using only the capability, object, convention, and run-policy
references carried by the candidate and its typed finding dependencies. A
globally present threshold or certificate therefore cannot satisfy an omitted
claim-local reference. The evidence rule requires a proof reference for a
Theorem, a passing certificate for a Computational Certificate, and a source
artifact for a Computational Observation. The promotion rule rejects every
forbidden promotion ID. These checks establish
$\operatorname{Eligible}_{M,P}(x,c)$.

For identity emission, $I\vdash_{\mathrm{derive}}x\Rightarrow c$ holds
directly. For a derived claim, the emission rule requires a non-open registered
rule, a `VALID` derivation state, and satisfied proof- or certificate-backed
conditions. The induction hypothesis applies to its source packages, and the
assumed scoped soundness of the registered rule establishes the target claim.
Therefore every claim-emission branch supplies both the eligibility witness
and the derivation witness. No degradation branch emits an affirmative claim,
which proves the statement. $\square$

For an exact finite depth claim $D_\kappa=d$,
$\operatorname{Eligible}_{M,P}(x,c)$ requires a first-hit certificate: a
level-$d$ witness together with verified non-hits at all levels
$1,\ldots,d-1$. A level-$d$ witness without that minimality audit supports only
$D_\kappa\leq d$, or the finding that a hit was observed by level $d$.
Non-attainment through a finite cutoff remains the distinct state
`UNREACHED_AT_CUTOFF`. Likewise, trajectory non-crossing on a bounded
observation interval is response censoring carried by its sampling or
trajectory policy; it is not this filtration state.

The theorem applies only to the v1.0 semantics of the three named input
contracts and the v1.0 emission algorithm. The schemas, rule registry,
validator, compiler-output fixture, and boundary regressions in Appendix A
(A1--A5) provide a Computational Certificate that the implementation realizes
these emission rules; that certificate does not replace the proof. A future
major contract version requires the algorithm and soundness theorem to be
restated or reproved.

### Claim Spine

This paper separates role and ownership from the four reader-facing claim
statuses.

| Item | Role / ownership | Claim status | Content |
|------|------------------|--------------|---------|
| Strict Admission Factorization | inherited construction from Paper VIII | not an independent Paper X claim | finite complex $(V,Q,Y)$ data determine a typed SOF core relative to declared choices |
| Capability-Sound Compiler v1 Emission | owned result | Theorem | the algorithm emits only claim items with eligible IR sources and valid derivations |
| Registry v2.0 census | owned finite evidence | Computational Certificate | snapshot counts are bound to the Registry content digest, schema, and validator |

### Registry Probes and Open Dynamic Directions

The cross-species evidence motivates the following rate-hierarchy target but
does not place it in the compiler claim spine:

$$
\tau(R_1^{\mathrm{Lie}})
<
\tau(R_2^{\mathrm{Lie}})
<
\tau(D_{\mathrm{Lie}}^{(\leq d_{\max})}).
$$

An exact-depth version with $D_{\mathrm{Lie}}$ is a stronger future target and
requires a closure or saturation certificate. This is a Paper IX-compatible
dynamic Research Program recorded as a Registry probe, not an owned compiler
result.

The commonality developed here is therefore not common dynamics. It is a
capability-sound compilation interface.
Different species may possess completely different deformation geometries.
What is shared is the typed passage from a domain source through strict or
analogue admission and capability declarations to validated findings.
Observable dynamics remain species-dependent.

There is also an explicitly programmatic direction: the **Observable
Sufficiency Program**.  Its question is whether an expanding class of registered
species can be compared using aligned typed fields, including operator/word
and Lie/Hall branches when independently registered. This is a research
program for future alignment work, not a theorem established here or part of
the compiler spine.

### Inherited Sector Boundary

This paper uses the Paper VIII No-Sector No-Shadow boundary
\cite{paper8}: sector-indexed findings require declared projectors, while
global observables may exist without them. A source lacking the required marked
sectorization cannot validate as a strict-SOF Manifest. If that source is
otherwise admitted under another record kind, sector-indexed modules degrade
rather than emit claims. The compiler does not infer that every useful
observable theory must be sectorized.

### Capability-Aware SOF Registry

**Definition 1 (SOF Registry).**

A **SOF Registry** is a finite or open-ended collection

$$
\mathcal R=\{\mathcal E_s\}_{s\in S}
$$

of typed evidence entries. Each entry $\mathcal E_s$ first declares one of two
admission kinds:

1. a **strict SOF realization**, with a finite complex space, a complete marked
   sectorization, and a labelled operative alphabet $(V_s,Q_s,Y_s)$;
2. a **diagnostic analogue**, with source descriptors, an explicit analogue
   mapping, provenance, and a negative boundary excluding strict SOF theorem
   instantiation.

The entry then supplies a capability declaration
$\mathsf{Cap}(\mathcal E_s)$, typed objects and carriers, semantic conventions,
run policies, channels, structured findings, claims, certificates, artifacts,
and audited derivation edges. Dynamics are optional and must identify their
comparison and trajectory data when required by the selected diagnostic.

The Registry is therefore a compatible evidence interface, not a fixed result
tuple or an already compiled Manifest/IR pair. A row
need not supply route, word, closure, Lie/Hall, deformation, wall, or response
data unless those capabilities are declared. Conversely, declaring one
carrier does not authorize a nearby one: a graph path cannot fill a routed
product, a star closure cannot fill a positive-word depth field, and a proxy
cannot fill a discrete Lie shadow.

Sector origin is retained as provenance rather than redefined here.
Representation-, control-, mesh-, graph-, and Dirac-derived coordinates may
instantiate the Paper VIII realization interface when the strict structural
admission conditions are satisfied. Stochastic-barrier, activation-derived,
and other source coordinates may instead supply diagnostic-analogue mappings.
Sector origin is retained as provenance in both branches, but only strict
entries instantiate a Paper VIII SOF. Evidence level records support for a
finding; it does not determine the admission kind.

Every sector-pair channel also records its pair scope. In particular, a
saturated-corner channel must be either off-diagonal or scalar-reduced on the
diagonal. Indeed, because all three generated algebras are unital,

$$
Q_i
\in
Q_iA_Y^+Q_i
\cap
Q_iA_Y^*Q_i
\cap
Q_iA_{Q,Y}^*Q_i.
$$

Raw diagonal saturated Boolean support is therefore identically true and is
not an informative Registry coordinate. A nontrivial diagonal channel must
remove $\mathbb C Q_i$, for example by the Hilbert--Schmidt orthogonal
complement, and declare that reduction in its channel semantics.

Registry records are capability-sparse. A missing capability, a computed zero,
a cutoff-unreached state, a validation failure, and mathematical nonexistence
are distinct states. A compiler may omit an unsupported module or report it as
unavailable, but it may not manufacture the missing field.

Thus the Registry is the evidence architecture developed here. The theorem-level
object is sound compilation through the interface; the Registry records
instances, controls, and boundary cases.

![Registry wheel. Strict realizations and diagnostic analogues enter through
different source maps, including representation, gate action, state
partitions, control or mesh geometry, Dirac blocks, stopping regions,
activation descriptors, and filtrations. The wheel records admission and
evidence roles; it does not assert common dynamics.](../../figures/paper10/fig2_registry_wheel.png)

### Diagnostic Vocabulary

The shared diagnostic vocabulary is:

| Diagnostic | Meaning |
|------------|---------|
| $\tau(O)$ | characteristic time scale |
| $\operatorname{wall}_{\mathrm{ref}}(O;\mathcal C,P_W)$ | imported typed-wall reference under declared context and policy |
| $\mathrm{Repair}_{\mathrm{filt}}^{\kappa,(\leq d_{\max})}$ | static finite-filtration recovery in carrier $\kappa$ under a declared cutoff and pair scope |
| $\mathrm{Repair}_{\mathrm{dyn}}^\kappa$ | time- or parameter-indexed shadow transition in carrier $\kappa$ under a declared chart and trajectory |
| $\mathrm{Repair}_{\mathrm{an}}^\kappa$ | carrier-qualified diagnostic-analogue repair descriptor with no strict SOF theorem instantiation |
| $\operatorname{plateau}_{\mathrm{diag}}(O;\gamma,P_\tau)$ | trajectory-relative stable-regime diagnostic |

These repair kinds are not interchangeable. Every repair finding records its
carrier, source and target layers, temporal scope, predicate, cutoff, pair
scope, count denominator, and saturation status. Not every diagnostic is
defined for every species; absence is recorded rather than hidden.
The wall and plateau entries import Paper IX admissibility and Paper XI
morphology rather than defining generic wall or plateau objects here.

### Registry v2.0 Interface

Registry v2.0 uses the following entry-assembly order:

$$
\begin{aligned}
\text{source}
&\longrightarrow \text{admission and capabilities}\\
&\longrightarrow \text{typed objects, carriers, and policies}\\
&\longrightarrow \text{findings and evidence}.
\end{aligned}
$$

![Capability-aware Registry entry. A source is admitted either as a strict SOF
realization or as a diagnostic analogue. Declared capabilities gate typed
carriers and reportable findings; evidence and negative boundaries prevent
unsupported promotion.](../../figures/paper10/fig3_registry_layers.png)

This is the observable layer added above classical structural decomposition.
Wedderburn--Artin theory explains how semisimple representations decompose
into structural blocks \cite{curtisReiner1962,serre1977,lam2001}. The SOF
Registry begins after this decomposition stage: it records how sectorized
observables, typed transport channels, deformation geometries, and diagnostics
are built on the represented or finite system. The
sectorization-origin field records where the coarse coordinate system comes
from; it is Registry metadata, not an additional SOF axiom.

The complete registry is intentionally larger than the main argument. To keep
the discussion centered on the pipeline rather than on a catalogue, the main
text uses a compressed capability view. Appendix A (A6--A8) identifies the
immutable v1.0 snapshot, the typed Registry v2.0 snapshot, and its schema and
validator.

### Registry Census Certificate

The following counts have status **Computational Certificate**, not Theorem.
The snapshot stores a `census_certificate` containing its snapshot ID, a
SHA-256 digest of the canonical Registry payload excluding the certificate
itself, schema version and digest, validator ID and version, validation status,
query version, and recomputable summary. The validator rejects a stale digest,
count mismatch, schema mismatch, or validator-version mismatch. Appendix A
(A9--A11) identifies the generated evidence record, its producer and
validator, and the migration regression.

| Registry v2.0 coordinate | Count | Meaning |
|--------------------------|------:|---------|
| rows | 19 | versioned evidence entries |
| strict SOF realizations | 15 | complete finite complex $(V,Q,Y)$ admission |
| diagnostic analogues | 4 | mapped descriptors without strict theorem instantiation |
| route / word / Lie--Hall carriers | $1/4/5$ | optional finite-filtration capabilities |
| proxy diagnostics / typed deformation charts | $7/2$ | proxy capability is broader than deformation admissibility |
| declared closure capabilities | 0 | no closure conclusion is inferred from finite-depth data |
| findings by evidence level | 1 Theorem, 13 Computational Certificates, 14 Computational Observations | 28 structured findings in total |

This compressed table is the reader view of that certificate. It is evidence
that the interface admits multiple species without forcing them into the same
carrier or evidence level; it is not the compiler-soundness theorem.

The finite spectral-triple entry plays a distinct logical role.  It is
conceptually different from the representation-based examples: its
sectorization is induced by a block-diagonal Dirac operator rather than by
irreducible representation theory or Wedderburn--Artin block decomposition.
Nevertheless, the same observable pipeline yields bridge-level accessibility
diagnostics. This suggests that the SOF pipeline depends primarily on the
existence of a compatible sectorization, rather than on the algebraic origin of
that sectorization.

***

## Registry Evidence: Cross-Species Capability Probes

### Markov and Graph: Static Positive-Word Registrations

Two foundational strict rows use coordinate sectors and a single declared
operative letter. The Markov row uses a three-state column-stochastic lazy
directed cycle with alphabet $\{P\}$; the graph row uses the path graph $P_6$
with vertex sectors and adjacency alphabet $\{A\}$. Both declare operator and
positive-word carriers, but no Lie/Hall carrier.

The exact finite audit gives

| Registration | $R_1[Y]$ | $W_2[Y]$ | $\max D_{\mathrm{word}}[Y]$ |
|--------------|----------:|----------:|----------------------------:|
| Markov lazy cycle | $3/6$ | $6/6$ | $2$ |
| path graph $P_6$ | $10/30$ | $8/30$ | $5$ |

The denominators count ordered off-diagonal sector pairs. Every such pair is
eventually reached in both registrations. Because each example has one
entrywise nonnegative operative matrix, a positive matrix entry in a power
cannot be removed by route-sum cancellation. Word support therefore agrees
with support-graph walks for these two declared matrices, and finite
shortest-path comparison certifies the displayed exact depths. This is a
realization-specific certificate, not a general promotion from graph paths to
operator words.

The graph row also carries a separate rewiring $K_0/K_1$ proxy observation,
discussed below. That dynamic proxy neither defines nor alters the static
$R_1[Y]$, $W_2[Y]$, or $D_{\mathrm{word}}[Y]$ certificates.

### Xu--Vardi--Safran Grokking: Rate-Separation Probe

Xu--Vardi--Safran's ridge-regression analysis
\cite{xuVardiSafran2026grokking} separates a parameter vector into row-space
and null-space components:

$$
\theta=\theta_{\parallel}+\theta_{\perp}.
$$

The row-space component is driven by the empirical loss and evolves quickly;
the null-space component is controlled by weight decay and evolves slowly.
This is not an SOF theorem. Registry v2.0 admits it as an external diagnostic
analogue: the source theorem remains external, while the Registry records only
the mapped rate descriptor and its negative strict-SOF boundary.

The conceptual bridge to SOF is the transition from parameter-space rate
separation to an observable-space rate question. The Registry evidence audit
reports:

| Domain | Fast channel | Slow channel | Ratio | Evidence type |
|--------|--------------|--------------|-------|---------------|
| Ridge regression | $\theta_{\parallel}$ | $\theta_{\perp}$ | $749.6\times$ | locally derived contraction-deficit ratio from an external-theorem diagnostic analogue |
| Exact three-sector trajectory | selected direct block norm | selected simple-commutator block norm | $\eta^{-1/2}$ at common threshold $0<\eta<1$ | Inherited Paper IX Theorem relative to the declared trajectory and policy |
| NN training diagnostic analogue | $K_0$ | $K_2$ | ordered half-response $60<80<120$ | Computational Observation |

This evidence is structural; it does not assert numerical equality of the
ratios. Different domains produce different magnitudes, and the three-sector
ratio varies with the declared threshold. Response times are compared only
relative to a stated trajectory parameterization, observable normalization,
norm, and policy.

The ridge value is not source-reported and is not a half-response-time ratio.
It is locally derived by the registered seeded diagnostic as

$$
\frac{\eta(\lambda_{\min}^{+}+\lambda)}{\eta\lambda}=749.6,
$$

using $m=400$, $n=50$, $\eta=0.2$, $\lambda=10^{-4}$, and seed $42$.
Registry v2.0 records the source locator, extraction formula, parameter values,
response convention, and `locally_derived` status. The external paper supplies
the theoretical precedent; it does not directly report this Registry number.

![Rate-hierarchy evidence. Xu ridge dynamics, NN proxy diagnostics, and an
exact three-sector threshold construction provide three evidence levels for
hierarchical visibility. Their claim status and parameter semantics
differ.](../../figures/paper10/fig4_rate_hierarchy_evidence.png)

### Yang-Like State Mixing: Proxy Boundary

The active Yang-like row studies a declared state-mixing path

$$
\rho(\varepsilon)=(1-\varepsilon)\rho_0+\varepsilon\sigma.
$$

and evaluates two continuous block-norm proxies. Their half-response audit is
degenerate rather than ordered. Registry v2.0 therefore admits this row as a
diagnostic analogue and proxy boundary, not as a strict deformation chart or
typed wall. The earlier plateau/oscillation script is retired historical
provenance and supplies no active Registry v2.0 finding.

The registry lesson is:

common evidence interface, different deformation geometry, different proxy
behavior.

### Quantum Clifford/CNOT: Non-Rubik Accessibility Probe

Quantum gate systems provide a non-Rubik accessibility probe.  In small
computational-basis sectorizations, this certificate uses the unique Registry
carrier `quantum.gates.principal-log-skew.hall-v1`. Its two-qubit generator
list is $\{H,S,\mathrm{CNOT}\}$, with $H$ and $S$ acting on the first qubit.
For each embedded gate $U$, the registration applies the SciPy principal
matrix logarithm and then the skew-Hermitian projection
$X=(\log U-(\log U)^*)/2$, with no additional normalization. The source code
declares direct skew extraction $(U-U^*)/2$ only as an exception fallback.
The diagnostic observations are:

1. entangling generators such as CNOT reduce frozen pairs and open additional
   transport channels;
2. the $T$ gate does not enrich the tested low-order
   $R_1^{\mathrm{Lie}}/R_2^{\mathrm{Lie}}$ support beyond
   the corresponding Clifford+CNOT gate set;
3. the same typed Lie/Hall audit can be applied outside Rubik.

This entry uses a **static filtration repair** count, not a dynamic transition.
For ordered off-diagonal sector pairs define

$$
\mathrm{Repair}_{\mathrm{filt}}^{\mathrm{Lie},(\leq4)}(i,j)
=
\mathbf 1\!\left[
R_1^{\mathrm{Lie}}(i,j)=0,
\quad
D_{\mathrm{Lie}}^{(\leq4)}(i,j)\neq\mathrm{unreached}
\right].
$$

The registered predicate imposes no $R_2^{\mathrm{Lie}}=0$ condition. The
Hall filtration places generators at depth $0$, simple commutators at depth
$1$, and generator brackets with the preceding layer at later depths, modulo
the cumulative real-linear span. The registered cutoff field $4$ denotes the
four tested levels with engine indices $0,1,2,3$; the absolute zero tolerance
is $10^{-6}$. The two-qubit computational basis gives $12$ ordered
off-diagonal pairs, with

$$
N_{\mathrm{repair,filt}}^{\mathrm{Lie},(\leq4)}(\text{Pauli})=0/12,
\qquad
N_{\mathrm{repair,filt}}^{\mathrm{Lie},(\leq4)}
(\text{Clifford+CNOT})=6/12.
$$

Thus, the value $6$ is a static pair count, not a depth. The registration is
truncated-only and asserts neither saturation nor a time-dependent repair
event. Artifact A9b records the carrier ID, generator extraction,
normalization, Hall convention, cutoff indexing, tolerance, and pair scope; no
alternative gate-generator registration belongs to this certificate.

This is not a claim that quantum systems obey Rubik wall theory. It is a
registry claim: quantum systems can expose a typed Lie/Hall channel under a
different species geometry.

***

## Imported Dynamic Evidence

This paper does not re-prove response-time results. From Paper IX, it imports the
calibrated exponential theorem and its three-sector Computational Certificate
with half-response times $30<1380$, together with the direct/commutator
threshold construction and NN proxy observations \cite{paper9}. The Registry
preserves their distinct theorem, certificate, and observation statuses.
Here, import means registration in the Paper X evidence interface; it does not
make the Paper IX artifacts Compiler v1 input fixtures or implement a
Registry-to-IR adapter.

The compiler-level boundary is that none of these findings may be promoted to
a Boolean support time, dynamic-shadow repair time, or Lie depth without the
missing proxy-to-shadow conditions identified in Paper IX. The static
Clifford+CNOT repair count remains a separate Registry certificate and cannot
fill that dynamic field.

![Imported calibrated response fixture. Paper IX owns the response theorem and
block-realization certificate; this paper preserves their typed status in the
Registry.](../../figures/paper10/fig5_mechanism_separation.png)

### Evidence Stratification

| Evidence layer | Status | Interpretation |
|----------------|--------|----------------|
| Calibrated exponential response model | Inherited Paper IX Theorem | exact result under one normalized-displacement policy |
| Three-sector block-norm realization | Inherited Paper IX Computational Certificate: $30<1380$ | registered typed dynamic finding, not yet compiled through a Registry-to-IR adapter and not a cross-species causal law |
| Exact three-sector threshold construction | Inherited Paper IX Theorem: $\tau_\eta(K_{\mathrm{dir}})=\eta$ and $\tau_\eta(K_{\mathrm{comm}})=\sqrt{\eta}$ for $0<\eta<1$ | first- versus second-order norm scaling under the declared trajectory and policy; not an intrinsic rate invariant, Boolean support, or Lie depth |
| NN training diagnostic analogue | Computational Observation: $60<80<120$ | endpoint-normalized sampled proxy response hierarchy; no strict SOF theorem instance |
| Markov and graph strict SOFs | Computational Certificates | direct and length-two positive-word support plus exact first word depth for two declared entrywise nonnegative matrices; no Lie/Hall carrier |
| Finite spectral-triple strict SOF | Computational Certificate plus Computational Observation | central distance obstruction and two ordered bridge instances remain separate |
| Quantum strict SOF | Computational Certificate: static filtration-repair count $6/12$ within cutoff | ordered-pair count, not depth 6 or a response trajectory |
| Paper VI Rubik registration | Computational Observation: pointwise $R_1^{\mathrm{Lie}}$ only | no $R_2^{\mathrm{Lie}}$, $D_{\mathrm{Lie}}$, or moving-field positive instance is imported |
| Xu ridge diagnostic analogue | Computational Observation: locally derived contraction-deficit ratio $749.6\times$ | external theorem is precedent; the registered number is not source-reported or a response-time ratio |
| Graph-rewiring / Yang-like proxy boundaries | Computational Observations | edge rewiring and state mixing are degenerate or unordered under their declared policies |
| Proxy-to-shadow bridge | Research Program | Observable Proxy Shadow Principle not yet proved |
| Dynamic truncated-$D_{\mathrm{Lie}}$ repair trajectory | Research Program | Clifford+CNOT gives a static filtration-repair count $6/12$, but no dynamic-shadow repair or structured $\tau(D_{\mathrm{Lie}}^{(\leq d_{\max})})$ audit |

The inherited response proposition is an exact calibrated model, not a blanket
causal theorem. Its realization certificate uses one strict proxy-capable
deformation chart. The NN, Xu, and Yang-like rows are diagnostic analogues; the
quantum row is a static Lie/Hall audit; and the graph row contains separate
static positive-word certificates and a rewiring proxy boundary. These roles
are not interchangeable. A response comparison is meaningful only after its
parameterization, normalization, norm, and response policy are fixed.

***

## Claim-Status Boundary

This paper claims:

1. Capability-Sound Compiler v1 Emission is the central theorem-level object;
2. strict admission factors through the Paper VIII SOF core rather than
   constituting a new realization theorem;
3. the SOF Registry is capability-aware evidence architecture with separate
   strict-SOF and diagnostic-analogue admission;
4. the compilation interface inherits the Paper VIII No-Sector No-Shadow
   boundary;
5. registered rows may be compared only through aligned fields with compatible
   carriers, conventions, policies, and evidence levels;
6. the Registry Census Certificate records 19 rows, including 15 strict
   realizations and 4 diagnostic analogues, with a recomputable digest and
   schema/validator binding.

This paper does not claim:

1. every mathematical system is naturally an SOF;
2. every SOF has a canonical nontrivial deformation;
3. a diagnostic analogue is a strict SOF theorem instance;
4. a missing capability is equivalent to zero, cutoff-unreached, failed
   validation, or mathematical nonexistence;
5. every row supplies route, word, closure, Lie/Hall, deformation, wall, and
   response-time fields;
6. all SOFs obey
   $\tau(R_1^{\mathrm{Lie}})<\tau(R_2^{\mathrm{Lie}})
   <\tau(D_{\mathrm{Lie}}^{(\leq d_{\max})})$;
7. Registry v2.0 contains a dynamic-shadow repair-rate
   trajectory or that its static filtration-repair count is a depth value;
8. the continuous proxy family $K_0/K_1/K_2$ already determines the discrete
   Lie shadows $R_1^{\mathrm{Lie}}$, $R_2^{\mathrm{Lie}}$, and
   $D_{\mathrm{Lie}}^{(\leq d_{\max})}$;
9. the registry is closed or complete.

The stable formulation is:

Strict admission is an inherited construction. Capability-sound compiler
emission is the theorem-level result. Registry census and concrete realizations are
certificates or observations at their declared levels. Paper IX owns the
ordered-calibration theorem and response certificate; this paper preserves their
typed evidence status. Mechanism-based cross-species causality, the Lie/Hall
rate hierarchy, and observable sufficiency remain external or downstream
Research Programs rather than compiler claims.

The interface therefore supports cross-species reporting only through
carrier-qualified typed fields. Depending on declared capabilities, these may
include operator, route, word, independently registered Lie/Hall, trajectory,
wall, rate, repair, and plateau records.

![Capability-gated compiler output. Strict sectorization may come from
representation theory, geometry, stochastic barriers, or control flags;
diagnostic analogues enter through a separate mapping. The compiler output includes
only modules supported by the admitted input's declared capabilities and
evidence.](../../figures/paper10/fig6_source_independent_observable_report.png)

***

## Conclusion

This paper establishes capability-aware compilation and Registry evidence. Strict
admission factors through the static object language of Paper VIII, while
deformation fields and response results are inherited from Paper IX. Under the
versioned Manifest, IR, Profile, rule registry, and emission algorithm,
capability-sound compilation emits only claims whose carrier, convention,
policy, evidence, and derivation checks pass. The Registry demonstrates this interface with
sparse strict and analogue records; it is evidence architecture, not the
soundness theorem itself.

The result is a common compiler interface rather than a common mathematical
dynamics. Its output is not a completed SOFRS report. Paper XI owns wall-record
classification, Paper XII the versioned single-report protocol \cite{paper12},
Paper XIII aligned sparse comparison, and Paper XIV policy-relative decision
semantics.

***

## Outlook

The next compiler questions are:

1. define versioned domain and Registry-to-IR adapters together with
   scientifically testable adequacy obligations;
2. identify carrier-specific proxy-to-shadow rules with explicit margin,
   stability, and promotion hypotheses;
3. extend compilation across nontrivial fibre bundles and schema transitions
   without treating incomparable fields as missing values;
4. enlarge the derivation-rule registry only when theorem hypotheses,
   certificate requirements, and negative boundaries can be checked
   mechanically.

Papers XI--XIV consume the resulting typed records through wall, report,
alignment, and decision contracts. Those downstream layers do not revise the
compiler theorem or supply missing upstream evidence.

***

## Appendix A: Computational Artifacts

The following repository artifacts implement the compiler contracts, Registry
migration, and source-addressed evidence checks used above.

### A.1 Compiler Contracts

The default directory is `schemas/sofcompiler/`. All short paths below are
relative to that directory.

| Artifact | Role | Short path |
|----------|------|------------|
| A1 | Capability Manifest schema | \path{capability-manifest-v1.0.schema.json} |
| A2 | Typed SOF IR schema | \path{typed-sof-ir-v1.0.schema.json} |
| A3 | Report Profile schema | \path{report-profile-v1.0.schema.json} |
| A4 | versioned derivation-rule registry | \path{rule-registry-v1.0.json} |
| A5 | compiler examples, typed output regression, and validator | \path{examples/}; \path{examples/strict-associative-compiler-output-v1.0.json}; \path{validate_examples.py} |

### A.2 Registry and Evidence

The short paths in this table are relative to the base directory shown in the
second column.

| Artifact | Base directory | Role | Short path |
|----------|----------------|------|------------|
| A6 | `registry/` | immutable Registry v1.0 snapshot | \path{paper10-release-v1.0.registry.json} |
| A7 | `registry/` | typed Registry v2.0 snapshot | \path{paper10-typed-v2.0.registry.json} |
| A8 | `schemas/registry/` and `registry/` | Registry schema and snapshot validator | \path{v2.0.schema.json}; \path{validate_snapshot.py} |
| A9a | `experiments/paper10/` | generated cross-species evidence record | \path{results/registry_evidence_v2.json} |
| A9b | `experiments/paper10/` | legacy certificate-import record | \path{results/legacy_certificate_imports_v2.json} |
| A10a | `experiments/paper10/` | cross-species evidence producer | \path{validation/build_results.py} |
| A10b | `experiments/paper10/` | legacy-import producer | \path{validation/build_legacy_certificate_imports.py} |
| A10c | `experiments/paper10/` | result validator | \path{validation/validate_results.py} |
| A11 | `registry/` and `tests/` | v1-to-v2 migrator and migration regression | \path{migrate_v1_to_v2.py}; \path{test_registry_migration.py} |

A5 checks the contract examples, including claim-local capability, convention,
policy, finding-dependency, derivation, and typed emission gates. A8 validates both Registry snapshots by
default. A10a--A10c build the two evidence records and validate the main
cross-species record. A11 regenerates the v2.0 snapshot from the immutable v1.0
source and checks the migration and legacy-import invariants. The snapshots store
artifact identifiers and digests so that findings, certificates, and producer
paths remain source-addressed. These executable checks certify the declared
implementations and finite records; they do not replace the compiler theorem
proof. All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite).

Artifact A9b is explicitly a migration certificate for two finite values
retained from the immutable v1 snapshot; it does not represent a fresh
scientific recomputation. The Rubik joint-spectrum and direct-support
certificates instead cite their existing Paper IV and Paper II result JSON
directly.
