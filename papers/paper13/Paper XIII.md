# Typed Alignment and Audit Signatures

### Realization-Relative Comparison for SOF Reports

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper (Paper XIII of the RIME program) consumes versioned SOF Reports from
Paper XII and owns explicit semantic alignment, partial comparability, typed
Audit Signatures, and fixed-frame structural pseudodistance. A report pair is
input evidence until alignment and comparison semantics are fixed.*

***

## Abstract

**Problem.** Paper XII defines a family of realization- and profile-relative
single-system report views
$\mathcal R^{\mathrm{view}}_{\sigma,\eta,P_X,P_A,v_N,v_A}$, not a canonical map from a source
system to one report. Two reports are therefore not comparable merely because
they conform to the same reporting protocol. Statements such as "support
decreased" remain undefined until record kinds, declared capabilities, sectors,
observables, thresholds, depth conventions, and parameter samples have been
admitted and aligned. This paper asks when two coordinates in a common typed
language actually have shared semantics, when comparison must remain partial,
and when it is formally incomparable.

**Approach.** This paper inherits carrier, policy, evidence, record-kind, and
promotion guards from the Paper X compiler contracts. Its new alignment datum is

$$
\mathfrak A_{\mathrm{align}}
=
(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}).
$$

Here $\mathcal R^\star$ and $\widehat{\mathcal R}$ are realization-relative
reference and target reports. The inherited guards first retain only fields
whose carriers, conventions, policies, evidence, and record-kind permissions
are jointly eligible; a missing capability is not serialized as a zero.
$\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}$ then align admitted sectors and
observables in common retained coordinates. The resulting alignment-relative
SOF comparison object is

$$
\mathfrak C_{\mathrm{cmp}}
=
(\mathfrak A_{\mathrm{align}},\Theta)
=
(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}};\Theta),
$$

where $\Theta$ fixes normalization, thresholds, depth semantics, path
synchronization, metrics, and aggregation. For an Audit Profile
$P_{\mathrm{audit}}$, comparison then induces the sparse typed map

$$
\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}
=
\{\Delta_\kappa\}_{\kappa\in
\operatorname{AlignCap}(\mathcal R^\star,\widehat{\mathcal R};
\Phi,\Theta,P_{\mathrm{audit}})}.
$$

The report pair alone is not comparable, the alignment datum alone does not
fix comparison semantics, and the audit map is an output rather than the
comparison object. Each requested coordinate carries a typed aligned,
mismatched, unavailable, incomparable, or unresolved state.

**Results.** The **No Comparison Without Alignment** proposition shows that a
report pair does not induce an Audit Signature until alignment evidence $\Phi$
and comparison semantics $\Theta$ are fixed. The
**Alignment-Relative Audit Faithfulness** invariant preserves report-item
bindings, carriers, policies, evidence, and provenance, or records an explicit
unavailable, incomparable, or unresolved state. On a fixed comparison frame,
the retained structural signatures carry weighted Hamming pseudometrics. The
finite controls include one native GridWorld F4 audit whose selected support,
word, and Lie coordinates are `ALIGNED`, `ALIGNED`, and `MISMATCH`, with counts
$0,0,8$.

**Implications.** This paper introduces alignment-relative Audit Signatures,
not a generic report-diff protocol. Comparison is undefined before inherited
guards, explicit alignment evidence, and comparison semantics; after all
three, report differences become structured coordinates rather than aggregate
scores. A nonzero signature records change, not defect. Diagnostic analogues
remain descriptor-level unless an explicit comparison map is declared.
Interpretation and policy-relative disposition belong to Paper XIV, and
cross-frame transport remains open. SOFAUDIT establishes aligned difference,
not diagnostic interpretation, defect attribution, or causal attribution,
without a separately supplied causal or intervention model.

***

## Introduction

Papers VIII--X establish the static typed object language, typed dynamic
fields, and capability-aware compilation theory; Paper XI supplies sparse
within-event wall records and morphology profiles \cite{paper8,paper9,paper10,paper11}. Paper XII
then instantiates the Paper X compiler contracts as a versioned single-system
reporting protocol \cite{paper12}. Its report view is relative to a frozen
source snapshot $\sigma$, an admitted adapter $\eta$, a Paper X Compiler
Profile $P_X$, a Paper XII Assembly Profile $P_A$, and normative and assembly
version closures $v_N,v_A$:

$$
S
\longrightarrow
\operatorname{Adapter}_{\eta}
\longrightarrow
(M_\eta,I_\eta)
\xrightarrow{\operatorname{Compile}_{v1}(\cdot,P_X)}
\mathcal O_{\eta,P_X}
\xrightarrow{\operatorname{Assemble}_{v2}(\cdot,P_A)}
\mathcal R^{\mathrm{view}}_{\sigma,\eta,P_X,P_A,v_N,v_A}(S).
$$

This paper shifts the focus from single-system reporting to cross-report
comparison. A single report answers: *under this admitted adapter, capability
declaration, policy set, and profile, what structure was reported?* Paper XII
establishes that a single-system report is realization-relative and is not, by
itself, a comparative correctness certificate. Two report files are therefore
not yet a mathematical comparison object.

### From Report Relativity to Report Alignment

Let the reference and target reports be

$$
\mathcal R^\star
=
\mathcal R^{\mathrm{view}}_{\sigma^\star,\eta^\star,
P_X^\star,P_A^\star,v_N^\star,v_A^\star}(S^\star),
\qquad
\widehat{\mathcal R}
=
\mathcal R^{\mathrm{view}}_{\widehat\sigma,\widehat\eta,
\widehat P_X,\widehat P_A,\widehat v_N,\widehat v_A}(\widehat S).
$$

When no ambiguity arises, the report indices are suppressed after this
definition. In particular, this paper never folds $P_A$ back into
$\operatorname{Compile}_{v1}$.

A literal report difference may arise from the source systems, from the
adapters, from the enabled capabilities, from the selected profiles, or from
several of these at once. This paper does not infer which source-level cause
produced a report difference. Instead, it requires the referenced reports to
retain their respective provenance and requires the comparison object to
declare which report-level fields are eligible and how they are aligned.
Thus a localized report difference is a statement about retained coordinates
under the declared observation and comparison semantics, not an identified
source mechanism. The sampled location or first observed mismatch time does
not by itself identify what produced the underlying change.

Report relativity does not make comparison impossible. It identifies the
additional data that comparison must not hide. In particular, alignment cannot
repair an undeclared carrier, reinterpret `NOT_DECLARED` as zero, turn
`UNREACHED_AT_CUTOFF` into infinity, or promote a diagnostic analogue into a
strict SOF theorem instance.

### Inherited Compiler Guards

This paper does not define a third admission system. It inherits record kinds,
carrier declarations, policy and evidence requirements, unavailable-state
semantics, and promotion rules from Paper X and the SOFRS v2.1 reports of Paper
XII. Its new datum is the explicit pairwise alignment
$\Phi=(\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}})$ together with the comparison
specification $\Theta$.

Only compatible strict fields are compared. Analogue fields remain at the
descriptor level. A comparison containing one strict and one analogue report
requires an explicitly declared common shadow. This does not convert the
analogue into a strict carrier or define a new record kind. The `.sofaudit` v2
validator checks inherited carrier, policy, evidence, record-kind, and
promotion conditions before emitting any coordinate.

Before alignment, even a basic statement such as "the target has less support"
has no invariant meaning. The apparent difference may arise because:

- the reports have incompatible record kinds or capability declarations;
- the two reports use different sectors;
- their observable families are not in correspondence;
- their thresholds or depth semantics differ;
- their parameter samples or trajectory samples are not synchronized.

The pair $(\mathcal R^\star,\widehat{\mathcal R})$ is therefore insufficient.
The alignment datum

$$
\mathfrak A_{\mathrm{align}}
=
\bigl(
\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}
\bigr)
$$

places the reports in common retained coordinates. The additional specification
$\Theta$ fixes how those coordinates are compared. Together they form the SOF
comparison object

$$
\mathfrak C_{\mathrm{cmp}}
=
(\mathfrak A_{\mathrm{align}},\Theta).
$$

> **SOF Report Alignment Principle.** Compare a target report
> $\widehat{\mathcal R}$ against a reference report $\mathcal R^\star$ only
> after sector and observable alignments $\Phi_{\mathrm{sec}}$ and
> $\Phi_{\mathrm{obs}}$ are explicit. The admissible comparison object is
> $(\mathfrak A_{\mathrm{align}},\Theta)$; $\Delta_{\mathrm{audit}}$ is its
> induced comparison signature.

**Proposition 1 (No Comparison Without Alignment).** Within the present
object language there is no admissible map

$$
(\mathcal R_1,\mathcal R_2)\longmapsto\Delta_{\mathrm{audit}}
$$

from a bare report pair. An Audit Signature is defined only after explicit
$\Phi$ identifies common retained semantic coordinates and $\Theta$ fixes the
comparison policies on those coordinates.

**Argument.** Each report is indexed by its own realization, carrier labels,
policies, and evidence. Before $\Phi$, equal field names do not establish a
common comparison object; before $\Theta$, even aligned values lack fixed
normalization, cutoff, orientation, and mismatch semantics. Therefore a bare
pair can support only a request for alignment, not a factual Audit Signature.
This is an object-domain restriction, not merely a program branch that refuses
to run. $\square$

**Protocol Invariant 1 (Alignment-Relative Audit Faithfulness).** Relative to
a declared alignment contract $(\Phi,\Theta)$, every emitted Audit Signature
coordinate must bind the contributing reference and target report items, retain
their carrier, policy, evidence, and provenance qualifications, or record an
explicit unmatched, incomparable, or unresolved state. Assembly must not
manufacture a missing value, treat the reference role as truth status, or
promote an unavailable coordinate to numerical zero.

This invariant is protocol-level. It does not establish that $\Phi$ is the
scientifically best alignment or that either report is correct about its source.

This paper makes four contributions:

1. It defines the SOF Report Alignment datum and
   the typed alignment-relative comparison object
   $\mathfrak C_{\mathrm{cmp}}=(\mathfrak A_{\mathrm{align}},\Theta)$, making
   comparability explicit rather than hidden preprocessing.
2. It defines capability-aware Audit Profiles and sparse typed comparison maps;
   unavailable coordinates remain explicit states rather than numerical zeros.
3. It defines a common retained comparison frame and equips representations
   embedded in that frame with a weighted structural pseudometric.
4. It separates protocol and migration conformance from a selected
    first-principles Object Certificate. A native-v2.0 GridWorld F4 audit and
    its v2.1 boundary-preserving revision close
   the object-to-report-to-comparison chain, while the remaining F1--F4
   payloads in GridWorld, SIR, Traffic, Compiler IR, and Network Routing remain
   bounded source observations. The corpus also includes
   legitimate transformations whose nonzero differences are licensed by
   contract, and supplies a versioned `.sofaudit` migration certificate that
   preserves five legacy F5 paths without promoting them to wall comparisons.

![From SOF Reports to an audit signature. Two independently generated SOF
Reports, their explicit alignment, and the comparison specification form
$\mathfrak C_{\mathrm{cmp}}$. The induced $\Delta_{\mathrm{audit}}$ records
difference; interpretation and Action Semantics remain downstream.](../../figures/paper13/fig1_report_to_audit.png)

The theory developed here is local. The paper does not define comparison
between different retained frames, infer alignments automatically, prove a
metric on a universal audit map, or turn difference into defect or action.
Single-report production belongs to Paper XII, aligned comparison to Paper
XIII, and context-indexed interpretation and action semantics to Paper XIV.

The paper proceeds from the comparison object to the induced audit signature,
its fixed-frame structural pseudodistance, word/Lie separation, native object
control, bounded observations, and failure boundaries. Broader alignment
regimes remain in the Outlook.

---

## Related Work and Novelty Boundary

**Program lineage.** Paper VIII supplies the SOF object layer; Paper IX supplies
typed dynamic fields; Paper X supplies capability-sound compiler contracts and
Registry evidence; Paper XI supplies typed one-wall records; and Paper XII
supplies the versioned single-report protocol and alignment-ready provenance
consumed here \cite{paper8,paper9,paper10,paper11,paper12}. Cross-paper
consumption does not transfer ownership: this paper owns aligned pairwise
differences, not either input's admission, morphology, or report semantics.

**Reporting and audit precedents.** Model cards and end-to-end algorithmic
audit frameworks provide precedents for structured records with explicit
scope and failure boundaries \cite{mitchell2019modelcards,raji2020accountability}.
This paper differs by treating sector and observable alignment as the
mathematical prerequisite for a comparison signature.

**Schema and ontology alignment.** Database schema matching and ontology
matching construct correspondences between fields, entities, and semantic
relations \cite{rahm2001survey,euzenat2013ontology}. SOF Report Alignment has a
different comparison unit: sector correspondences and observable
correspondences must be declared together with threshold, depth, trajectory,
and claim-status semantics before a comparison signature exists.

**Representation matching.** Orthogonal Procrustes alignment and modern
representation-similarity methods compare coordinate representations or
learned feature spaces \cite{schonemann1966procrustes,kornblith2019similarity}.
This paper does not compare raw embeddings. It aligns declared observable
structures and then compares their support, bridge, depth, frozen, response,
constraint, and admitted wall-record coordinates.

**Structured metrics.** Hamming distance and graph edit distance provide
standard precedents for discrete structural comparison
\cite{hamming1950codes,gao2010graphedit}. The fixed-frame pseudometric here is
more restricted than a general report distance: it is defined only on aligned
structural representations under fixed $(\Phi,\Theta)$, and no metric is
claimed on the full directional and path-dependent audit signature.

**World-model comparison context.** Latent-state world models and executable
consequence benchmarks motivate the Regime B/C comparison problem
\cite{lecun2022ami,hafner2025dreamerv3,cai2026whatifworld,lin2026scratchworld}.
They are comparison contexts, not evidence for the fixed-frame proposition or
the GridWorld F4 observation.

---

## SOF Report Alignment

### Alignment Datum and Comparison Object

For a report $\mathcal R$, write $I(\mathcal R)$ for its retained sector-label
set and $G(\mathcal R)$ for its retained observable-label set. An alignment
places the two reports in common retained coordinate sets $I_\Phi$ and
$G_\Phi$. Schematically, its sector component is the span

$$
I(\mathcal R^\star)_{\mathrm{ret}}
\xrightarrow{\phi^\star_{\mathrm{sec}}}
I_\Phi
\xleftarrow{\widehat\phi_{\mathrm{sec}}}
I(\widehat{\mathcal R})_{\mathrm{ret}},
$$

and its observable component is defined analogously over $G_\Phi$. The legs
may be identities, relabellings, or declared aggregations. They need not be
total or bijective, but unmatched coordinates and any aggregation rule must be
explicit. A declared aggregation is a typed alignment operation with a
family-specific law recorded in $\Theta$; it is not thereby a canonical
presheaf restriction or an untyped coarse-graining default.

The SOF Report Alignment datum is

$$
\mathfrak A_{\mathrm{align}}
=
(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}),
\qquad
\Phi=(\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}).
$$

> **Definition (SOF Report Alignment).** A SOF Report Alignment consists of a
> reference report, a target report, a typed sector alignment, and a typed
> observable alignment into common retained coordinates. Each alignment declares
> its map kind, matched and unmatched identifiers, totality/injectivity/
> surjectivity properties, semantic basis, evidence, and negative boundary.
> The reference role is not a truth claim: its role basis must state whether it
> is a formal specification, exact recomputation, certified measurement,
> consensus standard, or declared baseline only. It is the minimal geometric
> datum required before a domain-independent report comparison can be specified.

The reference role is a comparison role only. Even when its basis is a formal
specification, exact recomputation, certified measurement, consensus standard,
or declared baseline, it is not thereby a ground-truth oracle, a control group,
or a causal baseline for the target system.

The comparison specification is written schematically as

$$
\Theta
=
(\mathsf N,\mathsf M,\mathsf S_D,\tau,\mathsf P,\mathsf A),
$$

where $\mathsf N$ specifies normalization and scaling, $\mathsf M$ specifies the
comparison metric and its coordinate weights, $\mathsf S_D$ fixes depth semantics and frozen-value handling,
$\tau$ records thresholds and tolerances, $\mathsf P$ synchronizes parameterized
paths, and $\mathsf A$ specifies aggregation. Components fixed by a schema version
or protocol default need not be repeated in every record, but they remain part
of the declared comparison semantics.

> **Definition (SOF comparison object).** A SOF comparison object is
> $$
> \mathfrak C_{\mathrm{cmp}}
> =
> (\mathfrak A_{\mathrm{align}},\Theta)
> =
> (\mathcal R^\star,\widehat{\mathcal R},
> \Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}};\Theta).
> $$
> It is **admissible** when the inherited Paper X record-kind, carrier, policy,
> evidence, and promotion guards are satisfied; the report references resolve; $\Phi$ induces
> shape-compatible common coordinates for every compared structural array,
> unmatched coordinates are declared, and the controlled components of $\Theta$
> fix normalization, metric, missing-value, depth, threshold, parameter, and
> aggregation semantics for every non-null comparison coordinate. Path-dependent
> coordinates additionally require declared parameter synchronization. An
> Object Certificate requires a separate comparison basis with raw source,
> independent recomputation, oracle result, and audit result artifacts.

Let $\operatorname{Cap}(\mathcal R)$ denote the typed fields licensed by a
report's Capability Manifest, IR, evidence, and profile. For a comparison
profile $P_{\mathrm{audit}}$, define

$$
\operatorname{AlignCap}
(\mathcal R^\star,\widehat{\mathcal R};
\Phi,\Theta,P_{\mathrm{audit}})
=
\operatorname{Cap}(\mathcal R^\star)
\cap_{\Phi,\Theta}
\operatorname{Cap}(\widehat{\mathcal R})
\cap
\operatorname{Req}(P_{\mathrm{audit}}).
$$

The decorated intersection means that a field survives only when its carrier,
semantic convention, run policy, evidence status, and alignment are compatible
under $(\Phi,\Theta)$. Comparison is therefore profile-indexed:

$$
\boxed{
\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}
=
\operatorname{Compare}_{\Theta,P_{\mathrm{audit}}}
(\mathfrak A_{\mathrm{align}})
=
\{\Delta_\kappa\}_{\kappa\in\operatorname{AlignCap}}
}.
$$

Thus $\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}$ is a sparse typed map,
not a universal fixed-length vector. A requested coordinate may be `ALIGNED`,
`MISMATCH`, `NOT_DECLARED`, `NOT_APPLICABLE`, `INCOMPARABLE`, or `UNRESOLVED`.
Here `ALIGNED` means that comparability has been established and the retained
values are equal or within the declared tolerance; `MISMATCH` means that
comparability has been established and the values are unequal or outside that
tolerance. Thus these two states lie on one result axis.
Unavailable states carry no numerical zero and no affirmative claim status.
The serialized record retains the comparison object, Audit Profile, inherited
guard checks, and coordinate results as distinct fields.

**Remark (Comparison-object non-uniqueness).** Alignment is not unique in general.
Different admissible choices of $\Phi_{\mathrm{sec}}$ or
$\Phi_{\mathrm{obs}}$ may produce different comparison signatures under the
same $\Theta$. Different admissible choices of $\Theta$ may also change the
signature under the same alignment. Both $\Phi$ and $\Theta$ therefore remain
inside the `.sofaudit` comparison object rather than hidden preprocessing.

### The Alignment Contract

Without $\Phi_{\mathrm{sec}}$ and $\Phi_{\mathrm{obs}}$, two reports are merely
two unrelated descriptions. The alignment contract establishes comparability:

- **Sector alignment** $\Phi_{\mathrm{sec}}$: In the simplest case (same ambient
  space, same sector partition), this is the identity. When sector counts differ
  or sectorizations are produced by different pipelines (e.g., reference from
  simulation, target from clustering), $\Phi_{\mathrm{sec}}$ must specify which
  reference sector each target sector corresponds to, or declare pairs
  incomparable.
- **Observable alignment** $\Phi_{\mathrm{obs}}$: When observable families differ
  in cardinality or semantics (e.g., reference has 4 directional controls, target
  has 4 but in a different order), $\Phi_{\mathrm{obs}}$ specifies the
  correspondence. When observables are incommensurable (reference: physical forces;
  target: neural network activations), alignment is defined at the sector-block
  support level rather than the operator level.

In the controlled source observations below, both alignments are identity maps or
explicitly declared block/observable correspondences. Latent and behavioral
comparisons generally require non-trivial alignments.

## Notation Table

Paper XII distinguishes a realized object, compiled report, and serialized
artifact. This paper inherits that distinction and adds the aligned comparison
object and its serialization:

| Symbol | Meaning |
|--------|---------|
| $\mathcal{F}_\eta$ | Realized typed object $(V,\{Q_i\},Y;X,\mathcal H_{\mathrm{Hall}})$, with the Lie/Hall enrichment optional and independently declared |
| $\mathcal O_{\eta,P_X}$ | Paper X `CompilerOutput` produced by $\operatorname{Compile}_{v1}(M_\eta,I_\eta,P_X)$ |
| $\mathcal R^{\mathrm{norm}}_{\sigma,\eta,P_X,v_N}$ | Normative single-system report core |
| $\mathcal R^{\mathrm{view}}_{\sigma,\eta,P_X,P_A,v_N,v_A}$ | Paper XII assembled report view |
| $\mathcal A_{\sigma,\eta,P_X,P_A,v_N,v_A,v_S}$ | Serialized `.sofreport` artifact |
| $\mathcal{R}^\star$ | Reference report |
| $\widehat{\mathcal{R}}$ | Target report |
| $\mathfrak A_{\mathrm{align}}$ | SOF Report Alignment datum |
| $\mathfrak C_{\mathrm{cmp}}$ | Admissible SOF comparison object $(\mathfrak A_{\mathrm{align}},\Theta)$ |
| $\Theta$ | Comparison specification: normalization, metric, depth semantics, thresholds, parameter synchronization, and aggregation |
| $P_{\mathrm{audit}}$ | Audit Profile selecting requested comparison coordinates |
| $\mathfrak B=(I_B,G_B,\Theta)$ | Common retained comparison frame |
| $\mathfrak F_B$ | Structural representations admissibly embedded into $\mathfrak B$ |
| $\sigma_B(\mathcal R)$ | Aligned structural representation of one report in $\mathfrak B$ |
| $d_B$ | Fixed-frame structural pseudometric |
| $\Delta_{\mathrm{audit}}^P$ | Sparse typed comparison map induced by alignment, $\Theta$, and the Audit Profile |

The `.sofaudit` file serializes $\mathfrak C_{\mathrm{cmp}}$, the Audit
Profile, inherited guard checks, the induced sparse comparison map, and its
factual claim boundary.

---

## Audit Profiles and Fixed-Frame Geometry

### Capability-Aware Audit Object

The general comparison output is the sparse map
$\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}$. It contains only coordinates
requested by the Audit Profile and resolved through the aligned capabilities
of both reports. The profile does not manufacture a missing word, Lie,
deformation, or proxy carrier.

The controlled corpus uses the **Standard Regime-A Audit Profile**
$P_{\mathrm{A8}}$. It requests eight coordinate groups:

$$
\Delta_{\mathrm{audit}}^{P_{\mathrm{A8}}}
= (\,\Delta_{\mathrm{supp}},\;
\Delta_{\mathrm{brw}},\;
\Delta_{\mathrm{brl}},\;
\Delta_{\mathrm{dep}},\;
\Delta_{\mathrm{frz}},\;
\Delta_{\mathrm{cns}},\;
\Delta_{\mathrm{ctrl}},\;
\Delta_{\mathrm{wal}}\,)
$$

![The Standard Regime-A Audit Profile. The first five requested coordinate
groups form the structural sub-signature used by the fixed-frame pseudometric.
Constraint, response, and wall-record coordinates retain directional or
path-dependent semantics. No universal Audit Profile metric is
claimed.](../../figures/paper13/fig3_audit_signature.png)

| Dimension | Symbol | What is compared | What it detects |
|-----------|--------|-----------------|-----------------|
| **Support mismatch** | $\Delta_{\mathrm{supp}}$ | $R_1^{\star}$ vs. $\widehat{R}_1$ | Missing or hallucinated direct transitions |
| **Bridge mismatch (word)** | $\Delta_{\mathrm{brw}}$ | $R_{2,\mathrm{word}}^{\star}$ vs. $\widehat{R}_{2,\mathrm{word}}$ | Lost or spurious 2-step word paths |
| **Bridge mismatch (Lie)** | $\Delta_{\mathrm{brl}}$ | $R_{2,\mathrm{Lie}}^{\star}$ vs. $\widehat{R}_{2,\mathrm{Lie}}$ | Commutator-structure changes |
| **Depth distortion** | $\Delta_{\mathrm{dep}}$ | $D_{\mathrm{word}}^{\star}$ vs. $\widehat{D}_{\mathrm{word}}$ | Path-length errors and pairwise frozen/reachable misclassification |
| **Frozen disagreement** | $\Delta_{\mathrm{frz}}$ | $(f_{R_1},f_{D,\mathrm{word}},f_{D,\mathrm{Lie}})^{\star}$ vs. target counts | Net over/under-estimation of direct, word-depth, and Lie-depth reachability (three coordinates) |
| **Constraint violations** | $\Delta_{\mathrm{cns}}$ | Raw $T^{\star}$ vs. target $T$ | Target transitions absent from the reference |
| **Control-response mismatch** | $\Delta_{\mathrm{ctrl}}$ | Per-control $c_a^{\star}(i,j)$ vs. $\widehat{c}_a(i,j)$ | Rate errors, native-control aliasing, response collapse |
| **Wall-record mismatch** | $\Delta_{\mathrm{wal}}$ | Two retained Paper XI wall signatures in a compatible trajectory or domain context | Difference between aligned one-wall records |

### Standard Eight-Channel Regime-A Profile

The standard controlled profile has eight coordinate groups.
$\Delta_{\mathrm{frz}}$ is one group with three coordinates
(`frozen_R1`, `frozen_D_word`, and `frozen_D_lie`), and
$\Delta_{\mathrm{wal}}$ is the eighth group. This coordinate is available only
when both reports retain independently admitted one-wall records and Paper XI
signatures.

### Wall-Record Comparison Gate

Let $e^\star$ and $\widehat e$ be wall atoms already admitted upstream by
Paper IX and recorded by Paper XI. This paper consumes, but does not redefine,
their one-record signatures

$$
s^\star=\operatorname{MorphSig}_{W}^{P_W}(e^\star),
\qquad
\widehat s=\operatorname{MorphSig}_{W}^{\widehat P_W}(\widehat e).
$$

The default comparison is curation-independent. Curated signatures may be
compared only when the curation rulebook version, assignment semantics, and
any override policy are also explicitly aligned; a shared tag spelling alone
does not identify wall morphology.

An aligned wall-comparison input consists of the two source-addressed record
and signature references together with a comparison context

$$
\mathfrak A_{\mathrm{wall}}
=
(s^\star,\widehat s;
\Psi_{\mathrm{context}},\Psi_{\mathrm{field}}).
$$

The context alignment declares whether the inputs are trajectory events or
domain-level locus samples. For trajectories it also fixes parameter
synchronization and orientation alignment; for locus samples it aligns the
domain and incident-stratum semantics without imposing an intrinsic
before/after order. The field alignment identifies the primary and retained
context fields being compared. Only then may the Audit Profile emit

$$
\Delta_{\mathrm{wall}}
=
\operatorname{CompareWall}_{\Theta}
(s^\star,\widehat s;
\Psi_{\mathrm{context}},\Psi_{\mathrm{field}}).
$$

This is a between-report difference. It is not either input's within-event
$\delta_e^\gamma$ or within-locus $\delta_e^{\mathrm{loc}}$, and it cannot
establish that either input was a wall. A path payload without two retained
wall signatures is therefore `UNRESOLVED`, even when its sampled values differ.

The displayed coordinate $\Delta_{\mathrm{ctrl}}$ concerns native system
controls such as GridWorld moves, epidemiological rates, or traffic phases. It
does not denote a downstream intervention action. SOFAUDIT v2.1 serializes it as
the descriptive coordinate `response`; the frozen v1 records retain
`action_response_failure` only as historical provenance.

The eight-channel profile is not universal. A report without a Lie/Hall
carrier does not acquire a Lie-bridge value, and a static report does not
acquire a wall record. Incompatible conventions and unresolved checks also
remain nonnumeric typed states. None is numerical zero.

For the controlled tables below, $P_{\mathrm{audit}}=P_{\mathrm{A8}}$ is
fixed and the superscript is suppressed. Every displayed dash in a wall column
means `NOT_DECLARED`, not zero; `UNRESOLVED` marks a declared legacy path
observation that lacks the wall-input binding required above. The dense tables
abbreviate this state as `unres.`.

### Fixed-Frame Structural Pseudodistance

Fix a common comparison frame

$$
\mathfrak B=(I_B,G_B,\Theta),
$$

The **fixed comparison frame** is the primary object. It is determined by the
retained alignment and comparison specification and may be viewed locally as
one fiber only in an informal sense; no global bundle or
transition law between frames is claimed. Here $I_B$ and $G_B$ are
the retained sector and observable index sets and $\Theta$ fixes their
comparison semantics. Each admissible report carries a
declared embedding $\phi_{\mathcal R}:\mathcal R\to\mathfrak B$. A pairwise
alignment $(\Phi,\Theta)$ is one way to construct such a frame by supplying
the reference and target embeddings; it need not be the only pair that can be
expressed in that frame. For an admissibly embedded report $\mathcal R$, let

$$
\sigma_B(\mathcal R)
=
\bigl(
R_1,\,
R_{2,\mathrm{word}},\,
R_{2,\mathrm{Lie}},\,
D_{\mathrm{word}},\,
f_{R_1},\,
f_{D,\mathrm{word}},\,
f_{D,\mathrm{Lie}}
\bigr).
$$

This structural tuple is defined only on the Standard Regime-A profile
subdomain where all listed operator, word, Lie/Hall, depth, and frozen-summary
fields are jointly admitted. It is not synthesized for capability-sparse
comparisons.

Here every matrix has first been reindexed or aggregated into the common
coordinates of $\mathfrak B$ according to $\phi_{\mathcal R}$ and $\Theta$. The first four
coordinates are aligned matrices. The final three are the canonical frozen
coordinates retained by $\Delta_{\mathrm{frz}}$. Write
$\operatorname{Adm}(\mathfrak B)$ for all reports with validated embeddings
into this fixed frame.

> **Definition (Fixed-frame structural representation set).** The set
> $\mathfrak F_B$ is the collection of aligned structural
> representations
> $$
> \mathfrak F_B
> =
> \left\{
> \sigma_B(\mathcal R)
> :
> \mathcal R\in\operatorname{Adm}(\mathfrak B)
> \right\}.
> $$
> Its elements are aligned structural representations, not unaligned SOF
> Reports and not audit deltas. Representations expressed under different
> retained frames belong to different sets. In a single pairwise audit,
> $\mathfrak F_B$ may contain only the reference and target representations;
> no larger population or manifold is implied.

For a matrix coordinate $c$, let $H_c$ be off-diagonal entrywise Hamming
distance; for a frozen-count coordinate, let $H_c$ be the discrete distance.
The weights $w_c\geq0$ are the coordinate weights declared by $\Theta$ (part of
$\mathsf M$), not additional data introduced by the proposition. For
$\sigma,\sigma'\in
\mathfrak F_B$, set

$$
d_B(\sigma,\sigma')
=
\sum_{c\in\mathcal C_{\mathrm{str}}}
w_c\,H_c(\sigma_c,\sigma'_c).
$$

> **Proposition (Fixed-frame structural pseudometric).** The function
> $$
> d_B
> :
> \mathfrak F_B\times\mathfrak F_B
> \longrightarrow\mathbb R_{\geq0}
> $$
> is a pseudometric. If every $w_c>0$, it is a metric on the retained aligned
> structural signature tuples, or equivalently on richer aligned
> representations quotiented by equality of those tuples. Omitted diagonal
> entries are part of the declared equivalence.

**Proof.** Every $H_c$ is nonnegative and symmetric. Pointwise mismatch obeys

$$
\mathbf 1[x\neq z]
\leq
\mathbf 1[x\neq y]+\mathbf 1[y\neq z],
$$

so each matrix Hamming coordinate satisfies the triangle inequality; the
discrete frozen-count coordinates do as well. A nonnegative weighted sum
preserves these properties. Zero-weight coordinates may identify distinct
signatures, giving a pseudometric. If all weights are positive, zero distance
is equivalent to equality of every retained structural coordinate. $\square$

This proposition applies only to the **structural sub-signature**. It does not
establish a metric on the full Standard Regime-A audit map, still less on an
arbitrary Audit Profile:
constraint violations and control-response mismatches may be
reference-to-target directional, while wall comparison requires a compatible
trajectory or domain context. Those coordinates require separate symmetrization,
normalization, and composition laws before a full-signature geometry can be
claimed.

The fixed-frame statement is local. Each $\mathfrak F_B$ is a comparison
domain in which retained coordinates and mismatch semantics have already been
fixed. No transition law between distinct frames is defined; cross-frame
geometry requires compatible pushforwards and coordinate-change laws.

![Alignment frames and local structural pseudodistance. Each frame fixes
retained sector and observable coordinates together with the comparison
semantics in $\Theta$. The weighted structural pseudometric is defined within
one comparison domain; the dashed cross-frame relation is intentionally left
undefined.](../../figures/paper13/fig2_alignment_fiber.png)

### Word Bridge vs. Lie Bridge

Paper VIII already establishes that positive word products and Lie/Hall
commutators belong to different typed carriers. This paper does not reprove
that static distinction. It requires the two coordinates to be aligned and
compared separately.

For a matched pair of declared generators, the elementary identity

$$
\|Q_i[X_a,X_b]Q_j\|_F
\leq
\|Q_iX_aX_bQ_j\|_F
+
\|Q_iX_bX_aQ_j\|_F
$$

shows why $\Theta$ must align threshold conventions as well as labels: a
thresholded commutator witness need not coincide with either ordered
word-support shadow at the same absolute threshold. No coordinate is inferred
from the other.

The native GridWorld F4 comparison is the paper-specific object-level
control. On the tested
skew-symmetrized generators, word products retain connectivity through
reverse-direction components while the commutator channel changes. Hence
$\Delta_{\mathrm{brw}}=0$ while $\Delta_{\mathrm{brl}}$ changes on eight
ordered pairs. This is evidence for separate aligned coordinates, not a
universal sensitivity ordering between word and Lie bridges.

### First-Principles Object Control

The migrated `.sofaudit` cannot certify this matrix fact by schema validation
or digest closure. The GridWorld F4 Object Certificate therefore starts from
the two frozen native source snapshots, independently reconstructs
the skew generator matrices, recomputes direct support, all ordered length-two
products, and all simple commutators, and compares those results with both the
native producer output and the frozen source payload. A graph-support baseline independently checks the direct
transition incidence. Agreement among the source construction, matrix
recomputation, and graph baseline is the object-level evidence. The certificate
also checks that the migrated v2 audit leaves those coordinates `UNRESOLVED`
rather than borrowing the source-level result. The separate native audit binds
the oracle and may therefore emit factual coordinates; its SOFAUDIT validation
receipt records protocol conformance separately.

The certificate is finite and scope-bounded. It establishes the selected F4
support/word/Lie counts and pair sets under the declared threshold and
normalization. It does not establish that GridWorld is a scientifically
adequate model of an external learned system or that the same sensitivity
ordering holds in another realization.

### Machine-Readable Comparison Record

Paired comparisons are serialized as `.sofaudit` records, distinct from the
single-system `.sofreport` format of Paper XII. A `.sofaudit` record contains
the declared alignment-relative comparison object
$\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
\Phi;\Theta)$, inherited Paper X guard checks, an Audit Profile, the induced
sparse `coordinates` map, and its factual claim boundary. It is a companion
comparison contract rather than a revision of SOFRS. Appendix A states the
contract boundary; earlier artifacts remain provenance.

Each positive coordinate carries an evidence strength and epistemic target.
Certificate classes distinguish object evidence, comparison-audit evidence,
protocol conformance, and migration/assembly preservation. Comparison-audit
evidence establishes faithful calculation relative to $\Phi$ and $\Theta$;
schema validation and digest closure do not establish external-object truth.
Object-level evidence additionally requires a bound comparison basis linking
raw sources, independent recomputation, an oracle result, and the audit result.

### Difference and Attribution Boundary

> **Proposition (No Attribution Without a Causal Model).** Given validated
> reports, explicit alignment $\Phi$, comparison semantics $\Theta$, and an
> Audit Profile, SOFAUDIT may establish an aligned difference relation. In the
> absence of a separately supplied causal or intervention model, that relation
> does not identify the process, mechanism, component, or intervention that
> produced an underlying source-level difference.

**Argument.** The comparison object has inputs

$$
(\mathcal R^\star,\widehat{\mathcal R},\Phi,\Theta,P_{\mathrm{audit}})
$$

and an audit-signature codomain. None of these inputs specifies an object-level
dynamics, intervention assignment, or identification criterion. Distinct
source processes, adapters, observation maps, or profile choices can induce
the same retained aligned relation. Attribution is therefore not identified by
the audit map. $\square$

In particular,

$$
\begin{aligned}
\text{aligned difference}
&\not\Rightarrow \text{diagnostic interpretation},\\
\text{diagnostic interpretation}
&\not\Rightarrow \text{defect attribution},\\
\text{defect attribution}
&\not\Rightarrow \text{causal attribution}.
\end{aligned}
$$

Coordinate localization is not attribution. An audit may state that a retained
coordinate mismatches, or that a mismatch is first registered between two
declared samples, without identifying a component or mechanism as its cause.

### Downstream Interpretation Boundary

The audit map records aligned disagreement. It does not assign severity,
correctness, defect, or an intervention. Policy-relative interpretation and
bounded candidate disposition belong to the downstream Paper XIV
interpretation/action-semantics layer and cannot overwrite the recorded Paper
XIII coordinates.

### Legitimate Transformation Evidence

A nonzero comparison signature is descriptive, not condemnatory. For a declared
legitimate transformation, an external source-addressed artifact may specify a
transformation contract

$$
\mathcal T
=
(\text{intent},\text{allowed changes},\text{preserved invariants},
\text{required postconditions}).
$$

The raw $\Delta_{\mathrm{audit}}$ remains unchanged. A separately typed contract
evaluation may record residual changes not licensed by $\mathcal T$. Thus a
large structural signature may still be conforming, while a small signature may
violate a required invariant. SOFAUDIT v2.1 does not provide free-form
`transformation_contract` or `contract_evaluation` escape fields; such evidence
must be bound through a versioned external artifact and an admitted coordinate
or future extension contract.

---

## Controlled Source Observations: GridWorld

### GridWorld Setup

The reference is a deterministic $5\times5$ grid with 25 one-hot cell sectors
and an absorbing obstacle at $(2,2)$. Moves originating at the obstacle
self-loop, while neighboring moves into it are blocked. The observable family
consists of the four skew-symmetrized directional transition matrices
$\{N,S,E,W\}$. Five target perturbations test distinct comparison channels.

### GridWorld Failure Modes

**F1 -- Action Aliasing (N = S).** The target model's S transition matrix is
replaced by N. Because the response constants retain block norms rather than
orientation or sign, the support, bridge, depth, frozen, and response channels
do not detect this opposite-action aliasing; only the raw transition-constraint
channel responds. This exposes a boundary of the chosen observable family.

**F2 -- Persistence Loss.** E from (1,1) is smeared across three targets
(0.5, 0.3, 0.2 weights). The new edges lie on already-supported sector pairs,
so direct and word support remain fixed while commutator paths change.

**F3 -- Forbidden Edge.** S from (1,2) hallucinates a transition into the
absorbing obstacle sector (2,2). This adds direct support, creates word and Lie
bridges, shortens word depth, and violates the reference transition constraint.

**F4 -- Rare Bridge Deletion.** E removed from all column-0 cells
(0, 5, 10, 15, 20). Reverse-oriented skew components preserve the registered
word paths, while the commutator channel and Lie-depth shadow change.

**F5 -- Obstacle-Path Compatibility Record.** The frozen v1 payload sweeps obstacle position
$(2,2)\to(2,1)\to(2,0)\to(1,0)\to(0,0)$. The target remains fixed at
obstacle=(2,1). The path records support, bridge, depth, and frozen-set changes;
equal net frozen counts at some steps still conceal different frozen pairs.
The payload does not bind two Paper XI wall signatures and declares no usable
parameter synchronization, so SOFAUDIT v2.1 retains it as an unresolved path
observation rather than a wall-record mismatch.

### GridWorld Legacy Source-Payload Observations

The frozen F1--F5 vectors remain source-addressed in the legacy results indexed
by `experiments/paper13/README.md`; they are not factual SOFAUDIT v2.1
coordinates. Migrated source-present values are `UNRESOLVED`, and absent values
are `NOT_DECLARED`, until native report alignment and item bindings are
supplied.

The five frozen controls have distinct source-payload activation patterns. In
particular, the F4 payload records $\Delta_{\mathrm{brw}}=0$ and
$\Delta_{\mathrm{brl}}=8$. This bounded observation motivates separate word
and Lie channels but does not itself recertify a v2 comparison or imply a
universal sensitivity ordering.

### Native v2.0 End-to-End GridWorld F4 Validation and v2.1 Boundary Migration

The native F4 control is a separate execution path, not an upgrade of the
migrated record. It freezes two sparse GridWorld source snapshots, constructs
two strict native SOFRS v2.0 reports with validation receipts, declares identity
sector and observable alignments, fixes the complete comparison specification
$\Theta$, and binds each factual coordinate to report items. An independent
validator reconstructs the matrices from the frozen sparse sources, computes
direct generator support, ordered length-two word support, and simple
commutator support without consuming producer caches, and checks direct support
against the corresponding graph-incidence baseline.

The resulting native `.sofaudit` has `comparison_basis=COMPLETE` and binds the
independent oracle. Its three requested factual coordinates are:

| Native coordinate | State | Mismatch count |
|-------------------|-------|:--------------:|
| operator support | `ALIGNED` | 0 |
| ordered length-two word support | `ALIGNED` | 0 |
| simple-commutator support | `MISMATCH` | 8 |

Thus the object-level result, the SOFAUDIT v2.0 factual comparison, and its
projection-preserving v2.1 revision form a digest-bound chain. The old migrated
F4 artifact deliberately remains an
`UNRESOLVED` preservation artifact; migration never borrows the new oracle.
The native audit validation receipt certifies protocol conformance of the
artifact closure, while the separately bound independent recomputation carries
the Object Certificate.

---

## Cross-Domain Controlled Source Observations

Each frozen domain producer supplies its own sectorization, observable family,
and legacy comparison payload while retaining the same source-table grammar.
No equivalence of the native dynamics or failure mechanisms is assumed. Except
for the native GridWorld F4 chain above, these payloads remain bounded
observations pending object-level revalidation and native-v2.0 item bindings.

### SIR Compartmental Model

#### SIR Realization

The reference SIR system has three one-hot compartment sectors, Susceptible,
Infectious, and Recovered, with rate observables $\beta$ for $S\to I$ and
$\gamma$ for $I\to R$. The reference parameters are $\beta=0.3$ and
$\gamma=0.1$, so $R_0=3$. The directed chain is
$S\xrightarrow{\beta}I\xrightarrow{\gamma}R$. Under the skew-symmetrized rate
generators:

- **$R_1$**: $S\leftrightarrow I$ and $I\leftrightarrow R$ each contribute 2 ordered off-diagonal pairs,
  yielding $R_1^{\mathrm{offdiag}} = 4$. The skew part records antisymmetric
  support: $X_{\beta}[I,S] = \beta/2$ and $X_{\beta}[S,I] = -\beta/2$
  together encode the $S$--$I$ support channel. This is a proxy for the directed
  epidemiological $S\to I$ semantic, not a direct encoding.
- **$R_{2,\mathrm{word}}$**: $S\leftrightarrow R$ via the 2-step word bridge $X_\gamma X_\beta$.
  $R_{2,\mathrm{word}}^{\mathrm{offdiag}} = 2$.
- **$D_{\mathrm{word}}$**: $D(S,I)=1$, $D(I,R)=1$, and $D(S,R)=2$, with symmetric reverse entries.
- $f_{R_1}=2$ for the directly frozen $S$--$R$ ordered pairs, while
  $f_{D,\mathrm{word}}=f_{D,\mathrm{Lie}}=0$.
- **$R_{2,\mathrm{Lie}}$**: $[X_\beta, X_\gamma]$ has a non-zero $S$--$R$ block.
  $R_{2,\mathrm{Lie}}^{\mathrm{offdiag}} = 2$.

This is a minimal three-sector realization with a nontrivial two-step bridge.

#### SIR Failure Modes

**F1 -- Rate Equalization ($\beta=\gamma$).** Binary structure is unchanged and only
$\Delta_{\mathrm{ctrl}}$ responds. The infection and recovery operators remain
distinct because they occupy different support blocks.

**F2 -- Missing Edge ($\beta=0$).** The $S\to I$ channel vanishes, changing
direct support, both bridge channels, depth, and all three frozen coordinates.

**F3 -- Forbidden Direct ($S\to R$).** A spurious direct edge is added to the
$\beta$ observable, producing extra support and bridge paths together with one
reference-constraint violation.

**F4 -- Rate Distortion ($\beta=0.001$).** Structure is preserved ($\beta>0$ so edges
exist), but the $S\to I$ response is 300 times weaker. Only the continuous
control-response coordinate changes.

**F5 -- Beta-Trajectory Compatibility Record.** $\beta$ is swept from 0 to
0.5 in 11 steps; the target is fixed at $\beta=0.2$. The frozen payload records
sampled support and response changes but does not retain Paper XI wall
signatures for both sides.
The frozen-set mismatch occurs only at the endpoint $\beta=0$; for all sampled
$\beta>0$, the reference and target have identical frozen sets.

#### SIR Legacy Source-Payload Observations

The complete frozen vectors remain in the source-addressed legacy results. The
distinguishing bounded pattern is that binary coordinates change at
$\beta=0$, whereas for every sampled $\beta>0$ the frozen-count delta is zero
and rate changes remain continuous-response observations. These are not
factual SOFAUDIT v2.1 coordinates.

#### Candidate Support Boundary and Response Crossing

The sampled SIR $\beta$-sweep displays one candidate source-side support
boundary and one continuous response-order crossing:

- **$\beta=0$ (candidate support boundary).** The $S\to I$ edge vanishes.
  $R_1$ loses the $S$--$I$ support pair. The direct and depth-frozen counts
  jump. This paper records this sampled diagnostic but does not supply Paper IX
  wall admission or a Paper XI one-wall signature.
- **$R_0=1$, i.e., $\beta=\gamma$ (response-order crossing).** $\|X_\beta\|/\|X_\gamma\|$
  crosses 1. No binary metric changes: $R_1$, $R_2$, and frozen sets are constant for all
  $\beta>0$. The crossing is visible only in the continuous response constants.

In classical epidemiology, $R_0=1$ is already the critical epidemic
threshold. SOF does not replace that interpretation; it re-expresses the same
threshold as a crossing of registered response magnitudes rather than a change
in compartmental support.

### Traffic Intersection

The traffic-intersection control adds a third Regime A domain. The reference is
a directed 2x2 intersection grid with four one-hot sectors
$(\mathrm{NW},\mathrm{NE},\mathrm{SW},\mathrm{SE})$ and two signal-phase
observables. Phase A records N-S green movement through southbound edges
$\mathrm{NW}\to\mathrm{SW}$ and $\mathrm{NE}\to\mathrm{SE}$. Phase B records E--W green movement through westbound edges
$\mathrm{NE}\to\mathrm{NW}$ and $\mathrm{SE}\to\mathrm{SW}$. Reverse directions are represented by the
skew-symmetric transpose, as in the other finite SOF controls.

The deformation parameter is the green-time ratio $\rho=t_A/t_B$. The
reference is $\rho=1$. Five constructed variants are compared:

- **F1 phase aliasing.** Phase B is replaced by Phase A, losing the horizontal
  response while making the two signal phases indistinguishable.
- **F2 missing phase.** $\rho=0$, so Phase A is removed and vertical movement
  freezes.
- **F3 forbidden diagonal.** Phase A hallucinates an $\mathrm{NW}\to\mathrm{SE}$ diagonal edge.
- **F4 timing distortion.** $\rho=0.01$, so binary support is preserved while
  control-response magnitudes collapse.
- **F5 rate-order trajectory.** The reference sweeps $\rho$ from 0.01 to 100
  while the target is fixed at $\rho=2$.

#### Traffic Legacy Source-Payload Observations

The complete frozen vectors remain in the source-addressed legacy results and
are not factual SOFAUDIT v2.1 coordinates. They separate phase aliasing, missing
phase, forbidden-edge, and timing-response patterns without promoting the F5
path to a wall comparison.

Traffic F5 provides a rate-order trajectory diagnostic rather than binary wall
evidence. The sampled
interval $\rho\in[0.01,100]$ excludes the limit points
$\rho\to0$ and $\rho\to\infty$, so frozen-count deltas remain $(0,0,0)$ under
the declared tolerance. The record is therefore a trajectory-mismatch path,
not a binary wall-crossing observation.

### Compiler IR

The compiler-IR control uses two distinct observable families on five one-hot
basic-block sectors:

$$
(B_{0,\mathrm{entry}}, B_1, B_2,
B_{3,\mathrm{side}}, B_{4,\mathrm{exit}}).
$$
The observable family contains:

- $X_{\mathrm{cfg}}$, recording control-flow edges;
- $X_{\mathrm{defuse}}$, recording cross-block def-use chains.

The reference is an O2-like five-block IR where the side block B3 is reachable
and the $\mathrm{B3}\to\mathrm{B4}$ data dependence is intact. Alignment is compiler-native:
basic-block names, SSA provenance, CFG node correspondence, dominance
metadata, or debug/source-span metadata can provide the comparison contract.
The experiment uses identity alignment.

Five constructed variants are compared:

- **F1 CFG/def-use aliasing.** $X_{\mathrm{defuse}}$ is replaced by
  $X_{\mathrm{cfg}}$, making data-flow structure indistinguishable from control
  flow.
- **F2 dead branch loss.** B3 is isolated by removing both CFG and def-use
  edges.
- **F3 spurious CFG edge.** A hallucinated $\mathrm{B0}\to\mathrm{B4}$ jump bypasses the normal
  path.
- **F4 lost def-use.** The $\mathrm{B3}\to\mathrm{B4}$ data edge is removed while the CFG edge is
  preserved.
- **F5 pass-pipeline path.** The reference follows
  $\mathrm{O0}\to\mathrm{mem2reg}\to\mathrm{simplifycfg}$, while the target remains fixed at the
  pre-simplifycfg snapshot.

#### Compiler IR Legacy Source-Payload Observations

The complete frozen vectors remain in the source-addressed legacy results and
are not factual SOFAUDIT v2.1 coordinates. They retain separate CFG and def-use
channels and keep the F5 pass-pipeline path unresolved as a wall comparison.

F4 is the cleanest compiler-specific diagnostic: aggregate support and word
bridges remain unchanged, but the Lie bridge and per-channel response record
the broken data-flow observable. F5 supplies a complementary legacy path
observation: the reference crosses the `simplifycfg` transition while the
target remains fixed at the pre-`simplifycfg` snapshot. Because neither side is
bound to a Paper XI wall signature, this path difference is not emitted as a
wall-record mismatch.

Compiler IR SOF Report Alignment is a structural comparison of control-flow and dependency
preservation under declared alignment. It does not replace semantic equivalence
checking or a verified compiler proof.

---

## Portability and Failure Boundaries

### Portability Criterion

A target domain follows the same construction when it supplies a
domain-justified sectorization, a declared observable family, reference and
target reports, and an admissible comparison object
$\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},\Phi;\Theta)$
whose sparse output and claim boundary are retained.

### Cross-Domain Synthesis

The four controlled domains isolate distinct roles for the same alignment
grammar:

| Domain | Sector origin | Observable family | Distinct alignment contribution |
|--------|---------------|-------------------|-----------------------------|
| **GridWorld** | Cell sectors in a finite transition system | Directional action operators | Spatial support mismatch, obstacle-path diagnostics, and word/Lie bridge-channel contrast |
| **SIR** | Compartment sectors | Infection/recovery rate operators | Sampled support boundary versus smooth response-order crossing |
| **Traffic** | Intersection-node sectors | Directed signal-phase operators | Phase aliasing, timing distortion, and rate-order trajectory mismatch |
| **Compiler IR** | Basic-block sectors | CFG and def-use observables | Dual observable-family alignment and pass-pipeline path diagnostics |

Their common comparison map is

$$
\mathfrak C_{\mathrm{cmp}}
=
(\mathcal R^\star,\widehat{\mathcal R},\Phi;\Theta)
\longmapsto
\Delta_{\mathrm{audit}}
\longmapsto
\text{typed diagnostic coordinates}.
$$

The domains differ in sector origin and observable semantics, but the
comparison-object type remains the same. The controlled comparisons therefore establish
portability of the alignment grammar without identifying the underlying
failure mechanisms across domains.

![Protocol portability across controlled domains. GridWorld, SIR, Traffic, and
Compiler IR use different sectors and observables, but each produces an
explicit $\mathfrak C_{\mathrm{cmp}}$ consumed by the same comparison map. The
figure asserts portability of the comparison-object grammar, not equivalence of
native dynamics.](../../figures/paper13/fig5_protocol_portability.png)

### Legitimate Transformation Controls

The failure-mode controls ask whether a target departs from a declared reference.
The before/after controls ask a different question: what observable structure
changes under a transformation already declared legitimate? Each control stores
the full raw signature and a separate contract residual.

#### Legacy Source-Payload Transformation Observations

The source-addressed vectors cover a Compiler $\mathrm{O0}$-like to
$\mathrm{O2}$-like transformation, Traffic $\rho:0.5\to2.0$, and a GridWorld
obstacle relocation. All three have zero declared contract residual despite
nonzero raw differences; the complete legacy vectors remain outside the
factual SOFAUDIT v2.1 coordinate surface.

The Compiler control uses a common five-block ambient realization with B3 marked
as a retired target sector; its sector alignment is therefore explicit rather
than silently treated as an unchanged active partition. Traffic preserves all
binary topology while reversing the phase-response order. GridWorld changes
support, bridges, depths, and frozen counts substantially, but every changed raw
transition is incident to the declared old or new obstacle sector. In all three
cases, nonzero $\Delta_{\mathrm{audit}}$ means **changed**, while the zero contract
residual means **no undeclared change was detected**.

### Additional Validation Domain: Network Routing

Network Routing is included as an appendix validation domain rather than as a
fifth member of the main synthesis table. It is useful because it isolates an
ACL/policy-removal comparison role: the ACL acts as a constraint that removes edges
from $X_{\mathrm{external}}$, rather than an additive observable family like
Compiler IR's CFG/def-use pair.

The reference has four prefix sectors
$(P0_{\mathrm{local}},P1_{\mathrm{dmz}},P2_{\mathrm{internal}},
P3_{\mathrm{external}})$ and two observables:
$X_{\mathrm{internal}}$ for trusted-zone routes and
$X_{\mathrm{external}}$ for gateway routes.

#### Network Routing Legacy Source-Payload Observations

The complete frozen vectors remain in the source-addressed legacy results and
are not factual SOFAUDIT v2.1 coordinates. The retained qualitative contrast is
between F2 edge removal and F3 bridge/constraint activation.

Two signatures are especially useful. F2 is a pure ACL edge-removal pattern:
direct support changes, but word and Lie bridge channels do not. F3 has no
direct-support mismatch, yet it produces word/Lie bridge mismatches plus a
constraint violation. This makes the appendix domain complementary to Compiler
IR rather than another traffic-shaped graph example.

### Failure Boundaries

Paper XII owns the single-report applicability boundaries. Paper XIII adds
three paired-comparison boundaries:

- **Alignment failure.** If $\Phi_{\mathrm{sec}}$ or $\Phi_{\mathrm{obs}}$
  cannot be specified (incommensurable sectorizations or observable families),
  the paired comparison reduces to two independent single-system reports.
  Undeclared coarse/fine refinement is an alignment failure. A refinement may
  be used inside one comparison object only when both legs into a common
  retained frame and the associated aggregation or pushforward rule are
  explicitly supplied in $\Phi$ and $\Theta$. Transport between independently
  defined refinement frames remains open.
- **Coverage asymmetry.** If the reference covers state-space regions the
  target cannot represent (or vice versa), $\Delta_{\mathrm{frz}}$ is
  dominated by coverage mismatch rather than a common-coordinate structural
  difference.
- **Comparison-resolution floor.** Thresholds, tolerances, sampling grids, and
  finite cutoffs bound the resolution of a coordinate. Near-zero rates may be
  indistinguishable from noise, threshold crossings may change discrete
  support, and unresolved finite depth remains `UNREACHED_AT_CUTOFF`.

### Failure Controls

Positive comparisons do not establish non-fabrication. The boundary controls
reject missing $\Phi$ or $\Theta$, incompatible carrier or policy guards,
receipt drift, analogue-to-strict promotion, unavailable-to-zero promotion,
unbound coordinates, incomplete alignment, and external-object claims without
an independent comparison basis. Partial evidence remains unmatched,
incomparable, or unresolved.

A receipt does not authenticate its own validator, and a conformance `PASS`
does not establish object-level truth. A schema-valid but scientifically
misleading alignment therefore requires an independent domain baseline or
first-principles recomputation before Object Certificate status is available.
A declared reference remains a comparison role unless its role basis supplies
stronger authority.

The cross-domain distance study is a separate computational boundary, not a
fourth alignment failure class. It is a legacy source-payload diagnostic, not
a factual SOFAUDIT v2.1 coordinate study. Across the 25 failure-mode comparisons, the
normalized seven-coordinate structural vectors have same-label and
different-label mean distances $1.0915$ and $1.3991$, a separation ratio of
$1.2818$. This is weak, domain-dominated separation. There is only one
comparison per failure label within each domain, so no within-domain
replication or clustering claim is made. This diagnostic uses only its declared
shared fields; it does not promote the five F5 compatibility payloads to wall
coordinates.

---

## Claim Spine

Evidence strength and claim target are orthogonal. Definitions and protocol
invariants are not promoted into external scientific results.

| Claim or object | Formal role and claim target | Reader-facing status |
|-----------------|------------------------------|----------------------|
| SOF comparison object $(\mathfrak A_{\mathrm{align}},\Theta)$ and Audit Profile | owned typed definitions; representation interface | not an independent evidence claim |
| No Comparison Without Alignment | domain-of-definition proposition; representation interface | Theorem |
| No Attribution Without a Causal Model | aligned-difference boundary; no source-mechanism identification without an external model | Theorem |
| Alignment-Relative Audit Faithfulness | executable invariant; implementation checked by a Comparison Audit Certificate | not an independent evidence claim |
| Fixed-frame structural pseudometric | mathematical proposition under one retained frame and weights fixed by $\Theta$ | Theorem |
| GridWorld F4 first-principles oracle and native SOFAUDIT | finite end-to-end comparison; external-object target and Object Certificate | Computational Certificate |
| versioned boundary-preserving migration | finite preservation audit; Migration/Assembly Certificate | Computational Certificate |
| finite AB/BC/AC contextual-descent control | promoted bounded candidate-space witness only | Computational Certificate |
| remaining controlled F1--F4 legacy source payloads | source-payload diagnostics pending object-level revalidation; not factual v2.1 coordinates | Computational Observation |
| cross-frame transport, generalized descent, and inferred semantic alignment | open targets; no certificate is claimed here | Research Program |

The `.sofaudit` validation receipt is a Protocol Conformance Certificate only.
It is not evidence that either source report is scientifically adequate, that
the declared alignment is uniquely correct, or that a nonzero coordinate is a
defect.

---

## Conclusion

This paper fixes the SOF comparison object
$\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
\Phi;\Theta)$. Alignment supplies common retained coordinates, $\Theta$ fixes
their comparison semantics, and an Audit Profile selects the sparse typed
output $\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}$. In each fixed retained
frame where the Standard Regime-A structural fields are jointly admitted, the
structural sub-signature carries a weighted pseudometric.

The native GridWorld F4 chain demonstrates factual end-to-end comparison. The
remaining GridWorld, SIR, Traffic, Compiler IR, Network Routing, and legitimate
transformation payloads provide bounded cross-domain exercises of the
comparison grammar. They do not extend the pseudometric to the full signature or define
comparison between frames. Those extensions require normalization,
symmetrization, and compatible pushforward laws.

Within the RIME program, Paper XII owns reporting. Paper XIII owns
alignment-relative comparison and fixed-frame pseudodistance. Paper XIV owns
context-indexed interpretation and policy-relative disposition. Their objects
remain distinct: difference, interpretation, and bounded candidate generation.
An aligned difference may localize a retained coordinate or declared sample
window, but it does not identify the source mechanism that produced it.

---

## Outlook

### Alignment Regimes

The SOF comparison object applies to three reference-target regimes:

| Regime | Reference | Target | Alignment status |
|--------|-----------|--------|------------------|
| **A: controlled reference** | explicit dynamics or structure | constructed variant or declared transformation | validated here |
| **B: aligned latent model** | environment or analytic reference | latent-state dynamics model | requires a justified latent-sector correspondence |
| **C: black-box behavioral** | grounded observations | API-, trajectory-, or video-level model | requires semantic probe alignment |

These regimes classify the relation between the two reports; they are
independent of the SOF Applicability Hierarchy, which classifies the quality of
each source-to-report realization. Regimes B and C remain future applications.
World-model proposals and executable consequence benchmarks provide relevant
contexts \cite{hafner2025dreamerv3,cai2026whatifworld,lin2026scratchworld}, but
they do not supply evidence for the structural results proved here.

![Alignment regimes and evidence boundary. Regime A supplies the controlled
validation used in this paper. Regimes B and C share the comparison-object
type but
require increasingly strong latent-sector or semantic-probe justification;
they remain application regimes rather than evidence for the fixed-frame
results.](../../figures/paper13/fig6_alignment_regimes.png)

### Comparison Tooling

Implementations must distinguish declared alignment from inferred alignment
and retain parameter synchronization for trajectory comparisons. Interpretation
is downstream of the audit signature.

### Presheaf and Descent Outlook

The fixed-frame boundary suggests a more structured Research Program. Let
$\mathcal C_{\mathrm{obs}}$ be a candidate category of observation contexts,
where a first-stage morphism

$$
u:C'\longrightarrow C
$$

is restricted to localization, retained-sector or retained-observable
restriction, parameter-domain restriction, or semantics-preserving
relabelling for which a canonical restriction map exists. The exploratory
formal prototype defines the finite typed partial-signature assignment

$$
F_{\mathrm{sig}}:\mathcal C_{\mathrm{obs}}^{\mathrm{op}}
\longrightarrow \mathbf{Set}.
$$

All labels and convention packages in this prototype are drawn from fixed
set-sized registries, so the first-stage context category is small.

Within the finite exploratory prototype, identity and composition are verified
directly from the definition of coordinate restriction. This is an exact
formal result internal to that prototype, not a general SOF presheaf theorem or
a certificate claim of this paper. Presheaves of raw observables, full
realizations, and comparison-ready records remain candidate extensions rather
than results of this paper.

The carrier index is essential: restriction may preserve word data or
Lie/Hall data, but it does not convert one carrier into the other. Likewise,
a resolution refinement that splits a coarse sector does not automatically
define a presheaf restriction, because a coarse relation need not determine
its values on the finer sectors. Aggregation is instead a separate candidate
pushforward and is available only when a family-specific law has been
declared.

In the same-carrier, same-realization-kind, and same-convention subcase, a
comparison defined here can factor through an explicit common retained context
$C^*$ with admissible canonical-restriction legs

$$
C^*\longrightarrow C_{\mathrm{ref}},
\qquad
C^*\longrightarrow C_{\mathrm{tar}},
$$

so that both sections can be restricted to $F_{\mathrm{sig}}(C^*)$ before
comparison. The
term *common retained context* is intentional: $C^*$ is not assumed to be a
lattice-theoretic common refinement.

This span does not cover the full alignment contract defined here. In
particular, a strict-vs-analogue comparison may be admitted by explicit
$\Phi_{\mathrm{sec}}$, $\Phi_{\mathrm{obs}}$, and $\Theta$, but it cannot be
represented by two ordinary restriction legs because realization kind is
preserved by every morphism of the first-stage context category. An alignment
bridge is not thereby promoted to a presheaf restriction.

Finite gluing tests can then ask separately whether compatible local sections
have a global extension and whether that extension is unique. The exploratory
controls show why this is nontrivial for relation-valued signatures: sector
subsets may cover all sector labels while failing to cover cross-subset
relations, leaving multiple global extensions. This is a finite-candidate
analogue of a separatedness failure, not a general separatedness theorem.
Conversely, a bounded search can establish only that no global candidate was
found in the declared candidate space; it cannot establish nonexistence in an
unbounded presheaf. No Grothendieck topology,
sheaf theorem, descent theorem, or topos-level structural result is claimed in
this paper. The finite prototype remains non-evidentiary Research Program
material; only the separately registered AB/BC/AC control in Appendix B is on
the paper's evidence surface.

### Open Problems

1. **Context category and descent.** Generalize the finite
   canonical-restriction prototype to a structurally natural
   observation-context category; determine which carrier-typed assignments
   remain functorial, identify natural covers, test their closure properties,
   and study existence and uniqueness of gluing.
2. **Cross-frame transport.** Define family-specific pushforward and transition
   laws for resolution refinement, aggregation, and changing observable
   families without treating them as automatic restrictions.
3. **Alignment inference and stability.** Determine when
   $\Phi_{\mathrm{sec}}$ and $\Phi_{\mathrm{obs}}$ can be inferred, and how
   latent clustering or quantization uncertainty propagates to
   $\Delta_{\mathrm{audit}}$.
4. **Full-signature geometry.** Extend the fixed-frame pseudometric, if
   possible, to directional constraints, response coordinates, and
   synchronized wall records, with normalization across sector counts.
5. **Observable sufficiency.** Characterize minimal observable families that
   preserve diagnostically relevant distinctions and support causal
   attribution of response mismatches.
6. **Directed comparison costs.** Determine whether normalized channel
   strengths define canonical sector-pair costs without model-dependent
   weighting choices.

---

## Appendix A: Alignment Artifact and Schema Validation

The canonical machine-readable contract is
`schemas/sofaudit/v2.1.schema.json`. A conforming `.sofaudit` record encodes
an aligned comparison, not a second single-system SOF Report and not a
deployment decision. The separate
`schemas/sofaudit/validation-receipt-v2.1.schema.json` binds one audit to the
validator and digest-closed artifacts that were checked; the receipt is a
Protocol Conformance Certificate, not object-level evidence.

The contract's conceptual closure is the comparison object, its explicit
alignment and comparison specification, a versioned Audit Profile, sparse
typed coordinates, comparison-basis evidence, and a negative action boundary.
The full field inventory and shared reference types are defined by the
source-addressed schema and common contracts, not copied into this appendix.
In particular, `source_reports`, `alignment`, and
`comparison_specification` serialize $\mathfrak C_{\mathrm{cmp}}$;
`audit_profile` and `coordinates` serialize
$\Delta_{\mathrm{audit}}^{P_{\mathrm{audit}}}$. A nonzero mismatch does not
imply defect. `NOT_DECLARED`, `NOT_APPLICABLE`, `INCOMPARABLE`, and
`UNRESOLVED` coordinates have null values and cannot be replaced by zero.
Interpretation and action fields belong to Paper XIV.

The `attribution_boundary` is fixed as follows:

| Field | Required value |
|---|---|
| `localization_scope` | `ALIGNED_REPORT_COORDINATES` |
| `interpretation_status` | `DOWNSTREAM` |
| `defect_attribution_status` | `OUT_OF_SCOPE_FOR_SOFAUDIT` |
| `causal_status` | `OUT_OF_SCOPE_FOR_SOFAUDIT` |
| `reference_role` | `COMPARISON_ROLE_ONLY` |
| `reference_causal_role` | `NOT_A_CAUSAL_BASELINE` |

The corresponding receipt fixes
`receipt_kind = SOFAUDIT_VALIDATION_RECEIPT` and
`receipt_scope = SOFAUDIT_PROTOCOL_CONFORMANCE_ONLY`. Its `PASS` status does
not establish interpretation, defect attribution, causal attribution, or a
causal baseline.

The schema fixes object shapes; the semantic validator checks the role, regime,
profile, alignment, guard, coordinate, comparison-basis, claim-status, and
artifact-closure relations. An external-object claim requires an independent
object oracle over raw source, recomputation, oracle result, and audit result.
These are semantic checks beyond JSON Schema shape validation.

The frozen v1/v2.0 records remain immutable provenance. Migration preserves
their projections and unavailable states; it does not manufacture factual
coordinates or transfer the native Object Certificate to migrated records.
The detailed census, digests, and receipt index are maintained with the paper's
experiment record.

## Appendix B: Computational Artifacts

The following source-addressed artifacts implement the v2.1 comparison
contract and finite controls. Full inventories, digests, and generated outputs
remain indexed in `experiments/paper13/README.md` rather than duplicated here.

| Artifact | Role | Source-addressed path |
|----------|------|-----------------------|
| B1 | SOFAUDIT v2.1 schemas | `schemas/sofaudit/` |
| B2 | coordinate registry and Standard Regime-A profile | `schemas/sofaudit/` |
| B3 | semantic validator and receipt checks | `experiments/paper13/validation/` |
| B4 | v1-to-v2 migration and index | `experiments/paper13/` |
| B5 | native GridWorld F4 audit chain | `experiments/paper13/results/native/` |
| B6 | independent GridWorld F4 object control | `experiments/paper13/results/object-certificates/` |
| B7 | promoted finite AB/BC/AC control | `experiments/paper13/results/controls/` |
| B8 | focused protocol regression | `tests/test_sofaudit_v2.py` |
| B9 | v2.0-to-v2.1 audit migration | `experiments/paper13/validation/` |
| B10 | v2.1 semantic and receipt validator | `experiments/paper13/validation/` |
| B11 | v2.1 audit and source-report closure | `experiments/paper13/results/v2.1/` |

The artifact census is 20 F1--F4 source payloads, five F5 compatibility
payloads, and three transformation controls, giving 28 migrated records, plus
one separate native GridWorld F4 audit. This count is a corpus definition, not
a generalization claim.

B1--B11 establish only their declared finite targets. Migrated records are not
factual v2.1 comparisons, and the AB/BC/AC control is not a general descent
theorem. The full artifact map is maintained with the paper's experiment
record.

## Appendix C: Geometric Boundary and Outlook

The computational controls establish fixed-frame and declared-threshold
properties only. Sector permutations and conditional rescalings can be tested
inside a declared frame, while threshold crossings can change the discrete
signature and changes of alignment data move the representation to a different
comparison domain.

The resulting local domains do not yet form a global comparison geometry.
Transition maps and pushforward laws must be defined before bundle, connection,
transport, or curvature language can be promoted from outlook to theorem.
