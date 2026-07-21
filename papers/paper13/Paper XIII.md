# Comparison Geometry of SOF Reports

### Alignment, Fixed-Fiber Pseudometrics, and Word/Lie Transport Separation

**WuJun Chen**

Independent Researcher | RIME Project | 2026

*This paper is Part XIII of the RIME program. Paper VIII defines the static
Sectorized Observable Framework (SOF), Paper IX studies observable deformations,
Paper X introduces the Universal Observable Pipeline and the SOF Registry,
Paper XI classifies observable walls, and Paper XII formulates the SOF Diagnostic
Protocol for single-system SOF Reports. Paper XIII
introduces the local comparison geometry of SOF reports. It asks why comparison
is impossible before alignment, what geometry exists on a fixed fiber of
aligned structural representations, and which observable transport channels
must remain distinct.*

***

## Abstract

**Problem.** Paper XII defines a single-system SOF Report, but two reports are
not comparable merely because they conform to the same reporting protocol.
Statements such as "support decreased" remain undefined until sectors,
observables, thresholds, depth conventions, and parameter samples have been
aligned. Paper XIII asks what mathematical comparison object exists after
these choices are made explicit.

**Approach.** The alignment datum is

$$
\mathfrak A_{\mathrm{align}}
=
(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}).
$$

Here $\mathcal R^\star$ and $\widehat{\mathcal R}$ are the reference and
target reports and $\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}}$ align their
sectors and observables in common retained coordinates. The canonical SOF
comparison object is

$$
\mathfrak C_{\mathrm{cmp}}
=
(\mathfrak A_{\mathrm{align}},\Theta)
=
(\mathcal R^\star,\widehat{\mathcal R},
\Phi_{\mathrm{sec}},\Phi_{\mathrm{obs}};\Theta),
$$

where $\Theta$ fixes normalization, thresholds, depth semantics, path
synchronization, metrics, and aggregation. Comparison then induces

$$
\Delta_{\mathrm{audit}}
=
\operatorname{Compare}(\mathfrak C_{\mathrm{cmp}})
=
\operatorname{Compare}_{\Theta}(\mathfrak A_{\mathrm{align}}).
$$

The report pair alone is not comparable, the alignment datum alone does not
fix comparison semantics, and the audit signature is an output rather than the
comparison object. The machine-readable record retains
$\mathfrak C_{\mathrm{cmp}}$ and $\Delta_{\mathrm{audit}}$ separately.

**Results.** On each fixed fiber of aligned structural representations, the
structural signatures carry weighted Hamming pseudometrics; strictly positive weights
give a metric after quotienting by equality of the retained structural
signature. This is a local comparison geometry, not a metric on the full
eight-coordinate audit signature. An exact-support lemma places Lie-bridge
support inside the union of the two ordered length-two word supports, while a
single-generator $X^2$ witness proves that word accessibility can exist with
no Lie accessibility. Computational validation comprises 25 constructed
failure-mode comparisons across GridWorld, SIR, Traffic, Compiler IR, and the
additional Network Routing domain; the four main domains distinguish their five
declared controls by signature pattern. In the GridWorld F4 control, the Lie
channel changes on 8 ordered pairs while the word channel remains unchanged.
Three legitimate before/after transformations have nonzero raw signatures but
zero residual contract violations.

**Implications.** Paper XIII introduces the local comparison geometry of SOF
reports. Comparison is impossible before alignment; after alignment, report
differences become structured coordinates rather than aggregate scores. A
nonzero signature records change, not defect. Latent-model and black-box
comparison remain deployment regimes rather than evidence claims, and
cross-fiber transport remains open.

***

## Introduction

Papers VIII--XI establish the SOF object language, observable dynamics,
Universal Observable Pipeline, Registry, and wall-record taxonomy
\cite{paper8,paper9,paper10,paper11}. Paper XII then turns that language into a
single-system reporting protocol: a declared sectorization and observable
family produce a claim-status-aware `.sofreport` record \cite{paper12}.

Paper XIII changes the question from reporting to comparison. A single report
answers: *given this sectorization and these observables, what structure was
observed?* It cannot answer whether that structure agrees with a reference.
Correctness, conformance, and change are relational notions; two report files
are not yet a mathematical comparison object.

Before alignment, even a basic statement such as "the target has less support"
has no invariant meaning. The apparent difference may arise because:

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

Paper XIII makes four contributions:

1. It defines the SOF Report Alignment datum and the canonical comparison
   object $\mathfrak C_{\mathrm{cmp}}=(\mathfrak A_{\mathrm{align}},\Theta)$,
   making comparability explicit rather than hidden preprocessing.
2. It defines a fiber of aligned structural representations and equips it with
   a weighted structural pseudometric, giving a local comparison geometry.
3. It proves exact word/Lie support inclusion and a strict word-only witness,
   establishing that combinatorial and algebraic transport require separate
   signature channels.
4. It validates one comparison grammar across GridWorld, SIR, Traffic,
   Compiler IR, and an additional Network Routing control, including legitimate
   transformations whose nonzero differences are licensed by contract.

![From SOF Reports to an audit signature. Two independently generated SOF
Reports, their explicit alignment, and the comparison specification form
$\mathfrak C_{\mathrm{cmp}}$. The induced $\Delta_{\mathrm{audit}}$ records
difference; interpretation and Action Semantics remain downstream.](../../figures/paper13/fig1_report_to_audit.png)

The theory developed here is local. The paper does not define comparison between
different alignment fibers, infer alignments automatically, prove a metric on
the full audit signature, or turn difference into defect or action. Single-report
production belongs to Paper XII, aligned comparison to Paper XIII, and
context-indexed interpretation and action semantics to Paper XIV.

The paper proceeds from the comparison object to the induced audit signature,
its fixed-fiber structural geometry, and word/Lie separation. It then presents the
controlled validations, portability analysis, and failure boundaries. The
appendices state the machine-readable alignment contract, reproducibility map,
and geometric boundary; broader alignment regimes are deferred to the Outlook.

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
explicit.

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
> reference report, a target report, a sector alignment, and an observable
> alignment into common retained coordinates. It is the minimal geometric datum
> required before a domain-independent report comparison can be specified.

The comparison specification is written schematically as

$$
\Theta
=
(\mathsf N,\mathsf M,\mathsf S_D,\tau,\mathsf P,\mathsf A),
$$

where $\mathsf N$ specifies normalization and scaling, $\mathsf M$ specifies the
comparison metric, $\mathsf S_D$ fixes depth semantics and frozen-value handling,
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
> It is **admissible** when the report references resolve, $\Phi$ induces
> shape-compatible common coordinates for every compared structural array,
> unmatched coordinates are declared, and $\Theta$ fixes the semantics of
> every non-null comparison coordinate. Path-dependent coordinates additionally
> require declared parameter synchronization.

Comparison is the operator

$$
\operatorname{Compare}
:
\mathsf{SOFComparison}
\longrightarrow
\mathsf{AuditSignature},
$$

which maps an admissible comparison object to its comparison signature:

$$
\boxed{
\Delta_{\mathrm{audit}}
=
\operatorname{Compare}(\mathfrak C_{\mathrm{cmp}})
=
\operatorname{Compare}_{\Theta}(\mathfrak A_{\mathrm{align}})
}.
$$

The second equality is the curried notation used when $\Theta$ is fixed. Thus
$\Delta_{\mathrm{audit}}$ is induced rather than primitive. Its serialized
record retains the comparison object and resulting signature as distinct
fields.

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

In the controlled validations below, both alignments are identity maps or
explicitly declared block/observable correspondences. Latent and behavioral
comparisons generally require non-trivial alignments.

### Notation

We distinguish SOF objects from SOF reports:

| Symbol | Meaning |
|--------|---------|
| $\mathcal{F}$ | A SOF object: the triple $(V, \{Q_i\}, \{X_k\})$ |
| $\mathcal{R}$ | A SOF Report: the diagnostic record produced from $\mathcal{F}$ |
| $\mathcal{R}^\star$ | Reference report |
| $\widehat{\mathcal{R}}$ | Target report |
| $\mathfrak A_{\mathrm{align}}$ | SOF Report Alignment datum |
| $\mathfrak C_{\mathrm{cmp}}$ | Admissible SOF comparison object $(\mathfrak A_{\mathrm{align}},\Theta)$ |
| $\Theta$ | Comparison specification: normalization, metric, depth semantics, thresholds, parameter synchronization, and aggregation |
| $\mathfrak F_{\Phi,\Theta}$ | Fiber of structural representations expressed under fixed $(\Phi,\Theta)$ |
| $\operatorname{Sig}^{\mathrm{str}}_{\Phi,\Theta}(\mathcal R^\epsilon)$ | Aligned structural representation of one side $\epsilon\in\{\mathrm{ref},\mathrm{tar}\}$ |
| $d_{\Phi,\Theta}$ | Fixed-fiber structural pseudometric |
| $\mathsf{SOFComparison}$ | Class of admissible SOF comparison objects |
| $\mathsf{AuditSignature}$ | Space of structured comparison signatures |
| $\Delta_{\mathrm{audit}}$ | Mathematical comparison signature induced by alignment and $\Theta$ |

This convention separates SOF objects from their report-level realizations.
The `.sofaudit` file serializes $\mathfrak C_{\mathrm{cmp}}$ together with its
induced $\Delta_{\mathrm{audit}}$ and factual claim boundary.

---

## Audit Signature and Fixed-Fiber Geometry

### Comparison Signature

Once $\Phi_{\mathrm{sec}}$ and $\Phi_{\mathrm{obs}}$ are fixed, the induced
comparison signature is an eight-coordinate structured comparison:

$$
\Delta_{\mathrm{audit}} = (\,\Delta_{\mathrm{supp}},\;
\Delta_{\mathrm{brw}},\;
\Delta_{\mathrm{brl}},\;
\Delta_{\mathrm{dep}},\;
\Delta_{\mathrm{frz}},\;
\Delta_{\mathrm{cns}},\;
\Delta_{\mathrm{ctrl}},\;
\Delta_{\mathrm{wal}}\,)
$$

![The alignment-induced audit signature. The first five coordinate groups form
the structural sub-signature used by the fixed-fiber pseudometric. Constraint,
control-response, and wall-record coordinates retain directional or
path-dependent semantics. No metric on the full signature is
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
| **Wall-record mismatch** | $\Delta_{\mathrm{wal}}$ | Wall records along parameterized path | Failure to track environmental deformation |

### Why Eight, Not Seven

The comparison signature has eight coordinate groups.
$\Delta_{\mathrm{frz}}$ is one group with three coordinates
(`frozen_R1`, `frozen_D_word`, and `frozen_D_lie`), and
$\Delta_{\mathrm{wal}}$ is the eighth group. The wall record is a distinct
diagnostic object: a parameterized family of signatures rather than a
single-pair comparison.

The displayed coordinate $\Delta_{\mathrm{ctrl}}$ concerns native system
controls such as GridWorld moves, epidemiological rates, or traffic phases. It
does not denote a downstream intervention action. The v1.0 machine-readable
contract retains the field name `action_response_failure` as a compatibility
alias for this control-response coordinate.

### Aligned Structural Representation Fiber

Fix a comparison frame $(\Phi,\Theta)$, including the common retained sector
and observable index sets induced by $\Phi$. For either side
$\epsilon\in\{\mathrm{ref},\mathrm{tar}\}$ of an admissible comparison object,
with $\mathcal R^{\mathrm{ref}}=\mathcal R^\star$ and
$\mathcal R^{\mathrm{tar}}=\widehat{\mathcal R}$, let

$$
\operatorname{Sig}^{\mathrm{str}}_{\Phi,\Theta}
(\mathcal R^\epsilon)
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

Here every matrix has first been reindexed or aggregated into the common
coordinates declared by $\Phi$ according to $\Theta$. The first four
coordinates are aligned matrices. The final three are the canonical frozen
coordinates retained by $\Delta_{\mathrm{frz}}$. Write
$\operatorname{Adm}(\Phi,\Theta)$ for the report sides admissibly embedded in
this fixed comparison frame.

> **Definition (Aligned structural representation fiber).** The fixed fiber
> $\mathfrak F_{\Phi,\Theta}$ is the collection of aligned structural
> representations
> $$
> \mathfrak F_{\Phi,\Theta}
> =
> \left\{
> \operatorname{Sig}^{\mathrm{str}}_{\Phi,\Theta}(\mathcal R^\epsilon)
> :
> \mathcal R^\epsilon\in\operatorname{Adm}(\Phi,\Theta),\quad
> \epsilon\in\{\mathrm{ref},\mathrm{tar}\}
> \right\}.
> $$
> Its elements are aligned structural representations, not unaligned SOF
> Reports and not audit deltas. Representations expressed under different
> alignment or comparison specifications belong to different fibers.

For a matrix coordinate $c$, let $H_c$ be off-diagonal entrywise Hamming
distance; for a frozen-count coordinate, let $H_c$ be the discrete distance.
Given weights $w_c\geq0$ and $\sigma,\sigma'\in
\mathfrak F_{\Phi,\Theta}$, set

$$
d_{\Phi,\Theta}(\sigma,\sigma')
=
\sum_{c\in\mathcal C_{\mathrm{str}}}
w_c\,H_c(\sigma_c,\sigma'_c).
$$

> **Proposition (Fixed-fiber structural pseudometric).** The function
> $$
> d_{\Phi,\Theta}
> :
> \mathfrak F_{\Phi,\Theta}\times\mathfrak F_{\Phi,\Theta}
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
establish a metric on the full eight-coordinate $\Delta_{\mathrm{audit}}$:
constraint violations and control-response mismatches may be
reference-to-target directional, while wall comparison requires path
synchronization. Those coordinates require separate symmetrization,
normalization, and composition laws before a full-signature geometry can be
claimed.

The fixed-fiber theory is local. Each $\mathfrak F_{\Phi,\Theta}$ is a local
comparison domain in which coordinates and mismatch semantics have already
been fixed. No transition law between distinct fibers is defined; cross-fiber
geometry requires compatible pushforwards and coordinate-change laws.

![Alignment fibers and local comparison geometry. Each fiber fixes sector and
observable alignments together with the comparison semantics in $\Theta$.
The weighted structural pseudometric is defined within a local comparison
domain; the dashed cross-fiber relation is intentionally left
undefined.](../../figures/paper13/fig2_alignment_fiber.png)

### Word Bridge vs. Lie Bridge

Word bridges and Lie bridges capture different algebraic transport mechanisms.
The word channel is generated by products such as $X_aX_b$, while the Lie
channel is generated by commutators such as $[X_a,X_b]$. Their responses to the
same perturbation need not coincide, so neither channel should be inferred from
the other. They are therefore reported as separate coordinates of
$\mathsf{AuditSignature}$.

For the declared sectorization, write

$$
\operatorname{supp}_Q(Y)
=
\{(i,j):Q_iYQ_j\neq0,\ i\neq j\}.
$$

> **Lemma (Exact word/Lie support inclusion).** For every pair of observables,
> $$
> \operatorname{supp}_Q([X_a,X_b])
> \subseteq
> \operatorname{supp}_Q(X_aX_b)
> \cup
> \operatorname{supp}_Q(X_bX_a).
> $$

**Proof.** If both $Q_iX_aX_bQ_j$ and $Q_iX_bX_aQ_j$ vanish, then their
difference $Q_i[X_a,X_b]Q_j$ vanishes. Taking the contrapositive proves the
inclusion. $\square$

The lemma is an **exact-support** statement. At finite absolute threshold
$\tau$, one has only

$$
\|Q_i[X_a,X_b]Q_j\|_F
\leq
\|Q_iX_aX_bQ_j\|_F
+
\|Q_iX_bX_aQ_j\|_F.
$$

Consequently, Lie support detected at threshold $\tau$ guarantees that at
least one ordered word block exceeds $\tau/2$, not necessarily $\tau$.
Thresholded word/Lie comparisons therefore require compatible thresholds
inside $\Theta$.

The inclusion is strict. Let three one-dimensional sectors be connected by the
single skew-Hermitian generator

$$
X=E_{10}-E_{01}+E_{21}-E_{12}.
$$

Then

$$
Q_2X^2Q_0=E_{20}\neq0,
\qquad
[X,X]=0.
$$

Thus a length-two word channel connects sector $0$ to sector $2$ while the Lie
channel is absent. Word-depth accessibility can therefore exist without
Lie-channel accessibility, so the two channels cannot be merged into one
depth coordinate.

![Strict word/Lie separation witness. The single generator $X$ connects
successive sectors, so $Q_2X^2Q_0\neq0$, while the only self-commutator
$[X,X]$ vanishes. Word accessibility and Lie accessibility are therefore
distinct transport channels.](../../figures/paper13/fig4_word_lie_separation.png)

This separation is species-independent. It distinguishes two registry-level
transport mechanisms:

$$
\begin{aligned}
\text{combinatorial transport}
&\quad\leftrightarrow\quad
\text{word composition},\\
\text{algebraic transport}
&\quad\leftrightarrow\quad
\text{Lie commutators}.
\end{aligned}
$$

They may coexist in one realization, but neither is a surrogate for the other.
The distinction belongs to the SOF observable language rather than to
GridWorld, Compiler IR, or any other validation domain.

The controlled F4 example demonstrates this distinction. On the tested
skew-symmetrized generators, word products retain connectivity through
reverse-direction components while the commutator channel changes. Hence
$\Delta_{\mathrm{brw}}=0$ and $\Delta_{\mathrm{brl}}>0$ can occur in the same
comparison. This is evidence for separate reporting, not a universal sensitivity
ordering between word and Lie bridges.

### Machine-Readable Comparison Record

Paired comparisons are serialized as `.sofaudit` records, distinct from the
single-system `.sofreport` format of Paper XII. A `.sofaudit` record contains
the canonical comparison object
$\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
\Phi;\Theta)$, the induced signature $\Delta_{\mathrm{audit}}$, and its factual
claim boundary. It is a companion comparison contract rather than a revision
of SOFRS. The serialized field `comparison_object` identifies the input object;
`signature` identifies the output. Appendix A states the contract semantics;
the canonical JSON Schema is maintained separately.

### Downstream Interpretation Boundary

The comparison signature and its downstream interpretation are different
objects. For a declared context $\Gamma$, a downstream semantic layer may
interpret each coordinate through

$$
\operatorname{Sem}_{\Gamma,i}
:
\Delta_i
\longrightarrow
\mathcal I_i.
$$

Here $\mathcal I_i$ contains a context-relative interpretation label and may
carry declared severity or confidence annotations. It contains no repair
command, intervention candidate, or policy selection. Paper XIII records only
the factual alignment and signature; it does not define
$\operatorname{Sem}_{\Gamma,i}$ inside the comparison geometry.

Paper XIV owns the semantic and action layers:

$$
\Delta_i
\xmapsto{\operatorname{Sem}_{\Gamma,i}}
\mathcal I_i,
\qquad
(\Delta_{\mathrm{audit}},\operatorname{Sem}_{\Gamma})
\longmapsto
\mathcal A_{\Gamma}(\Delta_{\mathrm{audit}}).
$$

Any subsequent policy selection acts on the candidate Action Set and is further
downstream. Neither interpretation nor action may overwrite the recorded
$\Delta_{\mathrm{audit}}$.

### Legitimate Transformation Contracts

A nonzero comparison signature is descriptive, not condemnatory. For a declared
legitimate transformation, the paired comparison may additionally record a
transformation contract

$$
\mathcal T
=
(\text{intent},\text{allowed changes},\text{preserved invariants},
\text{required postconditions}).
$$

The raw $\Delta_{\mathrm{audit}}$ remains unchanged. A downstream contract
evaluation records only residual changes not licensed by $\mathcal T$. Thus a
large structural signature may still be conforming, while a small signature may
violate a required invariant. The `transformation_contract` and
`contract_evaluation` fields are optional `.sofaudit` metadata and do not alter
the intrinsic coordinates of $\Delta_{\mathrm{audit}}$.

---

## Controlled Validation: GridWorld

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

**F5 -- Obstacle Deformation.** Reference sweeps obstacle position
$(2,2)\to(2,1)\to(2,0)\to(1,0)\to(0,0)$. The target remains fixed at
obstacle=(2,1). The path records support, bridge, depth, and frozen-set changes;
equal net frozen counts at some steps still conceal different frozen pairs.

### GridWorld Signature Table

| Failure | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | $\Delta_{\mathrm{wal}}$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 action aliasing | 0 | 0 | 0 | 0 | (0, 0, 0) | 18 | 0 | -- |
| F2 persistence loss | 0 | 0 | 18 | 0 | (0, 0, -78) | 2 | 6 | -- |
| F3 forbidden edge | 2 | 6 | 6 | 48 | (-2, -48, -66) | 1 | 2 | -- |
| F4 bridge deletion | 0 | 0 | 8 | 0 | (0, 0, -52) | 0 | 10 | -- |
| F5 deformation | 12 | 30 | 16 | 108 | (0, 0, +20) | 6 | 24 | 5 steps |

The five controls have distinct coordinate-activation patterns. In particular,
F4 has $\Delta_{\mathrm{brw}}=0$ and $\Delta_{\mathrm{brl}}=8$, giving direct
evidence that word and Lie bridge channels must be reported separately. This
control does not imply a universal sensitivity ordering.

---

## Cross-Domain Controlled Validation

Each domain supplies its own sectorization, observable family, and alignment
contract while retaining the same comparison object and signature grammar.
No equivalence of the native dynamics or failure mechanisms is assumed.

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

**F5 -- Wall Record.** $\beta$ is swept from 0 to 0.5 in 11 steps; the target is fixed at $\beta=0.2$.
The frozen-set mismatch occurs only at the endpoint $\beta=0$; for all sampled
$\beta>0$, the reference and target have identical frozen sets.

#### SIR Signature Table

| Failure | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | $\Delta_{\mathrm{wal}}$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 rate equalization | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 4 | -- |
| F2 missing edge | 2 | 2 | 2 | 4 | (+2, +4, +4) | 0 | 2 | -- |
| F3 forbidden direct | 2 | 4 | 2 | 2 | (-2, 0, 0) | 1 | 2 | -- |
| F4 rate distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 2 | -- |
| F5 wall record | 0 | 0 | 0 | 0 | path-dependent* | 0 | 2 | 11 steps |

\* Along the wall path, the frozen-count delta is $(-2,-4,-4)$ at $\beta=0$ and
$(0,0,0)$ for every sampled $\beta>0$.

#### Two Walls in SIR Parameter Space

The SIR $\beta$-sweep reveals two walls of different SOF types:

- **$\beta=0$ (topological wall).** The $S\to I$ edge vanishes. $R_1$ loses the $S$--$I$ support pair.
  The direct and depth-frozen counts jump, producing a structural boundary.
- **$R_0=1$, i.e., $\beta=\gamma$ (response-order crossing).** $\|X_\beta\|/\|X_\gamma\|$
  crosses 1. No binary metric changes: $R_1$, $R_2$, and frozen sets are constant for all
  $\beta>0$. The crossing is visible only in the continuous response constants.

This distinction separates a support wall from a continuous response-order
crossing. In classical epidemiology, $R_0=1$ is already the critical epidemic
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
- **F5 wall record.** The reference sweeps $\rho$ from 0.01 to 100 while the
  target is fixed at $\rho=2$.

| Failure | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | $\Delta_{\mathrm{wal}}$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 phase aliasing | 4 | 4 | 0 | 8 | (+4, +8, +4) | 2 | 8 | -- |
| F2 missing phase | 4 | 4 | 0 | 8 | (+4, +8, +4) | 0 | 8 | -- |
| F3 forbidden diagonal | 2 | 8 | 4 | 2 | (-2, 0, -4) | 1 | 2 | -- |
| F4 timing distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 8 | -- |
| F5 wall record | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 8 | 21 steps |

Traffic F5 provides rate-order rather than binary wall evidence. The sampled
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
- **F5 pass-pipeline wall.** The reference follows
  $\mathrm{O0}\to\mathrm{mem2reg}\to\mathrm{simplifycfg}$, while the target remains fixed at the
  pre-simplifycfg snapshot.

| Failure | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | $\Delta_{\mathrm{wal}}$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 CFG/def-use aliasing | 2 | 10 | 12 | 4 | (+2, 0, +10) | 2 | 6 | -- |
| F2 dead branch loss | 4 | 8 | 8 | 8 | (+4, +8, +8) | 0 | 6 | -- |
| F3 spurious CFG edge | 2 | 2 | 4 | 2 | (-2, 0, 0) | 1 | 2 | -- |
| F4 lost def-use | 0 | 0 | 4 | 0 | (0, 0, 0) | 0 | 2 | -- |
| F5 pass-pipeline wall | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 0 | 3 steps |

F4 is the cleanest compiler-specific diagnostic: aggregate support and word
bridges remain unchanged, but the Lie bridge and per-channel response record
the broken data-flow observable. F5 shows the complementary path effect:
single-snapshot mismatch is zero, but the pass-path wall record detects that
the reference crosses the simplifycfg transition while the target remains
fixed at the pre-simplifycfg snapshot.

Compiler IR SOF Report Alignment is a structural comparison of control-flow and dependency
preservation under declared alignment. It does not replace semantic equivalence
checking or a verified compiler proof.

---

## Portability and Failure Boundaries

### Portability Criterion

A target domain follows the same construction when the required SOF
realization and alignment contract can be made explicit:

1. identify a domain-justified sectorization;
2. identify the observable family and its semantics;
3. construct or designate a reference report;
4. construct or observe a target report;
5. form the admissible comparison object
   $\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,
   \widehat{\mathcal R},\Phi;\Theta)$;
6. compute the induced
   $\Delta_{\mathrm{audit}}=\operatorname{Compare}(\mathfrak C_{\mathrm{cmp}})$;
   and
7. record the comparison and its claim boundary.

### Cross-Domain Synthesis

The four controlled domains isolate distinct roles for the same alignment
grammar:

| Domain | Sector origin | Observable family | Distinct alignment contribution |
|--------|---------------|-------------------|-----------------------------|
| **GridWorld** | Cell sectors in a finite transition system | Directional action operators | Spatial support mismatch, obstacle-wall deformation, and word/Lie bridge-channel contrast |
| **SIR** | Compartment sectors | Infection/recovery rate operators | Rate extinction wall versus smooth response-order crossing |
| **Traffic** | Intersection-node sectors | Directed signal-phase operators | Phase aliasing, timing distortion, and rate-order trajectory mismatch |
| **Compiler IR** | Basic-block sectors | CFG and def-use observables | Dual observable-family alignment and path-only pass-pipeline wall |

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

| Transformation | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | Res. |
|----------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Compiler $\mathrm{O0}$-like $\to$ $\mathrm{O2}$-like | 4 | 8 | 6 | 8 | (+4, +8, +8) | 0 | 8 | 0 |
| Traffic $\rho:0.5\to2.0$ | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 8 | 0 |
| GridWorld obstacle $(2,2)\to(0,0)$ | 12 | 26 | 10 | 102 | (-4, -6, +232) | 0 | 24 | 0 |

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

| Failure | $\Delta_{\mathrm{supp}}$ | $\Delta_{\mathrm{brw}}$ | $\Delta_{\mathrm{brl}}$ | $\Delta_{\mathrm{dep}}$ | $\Delta_{\mathrm{frz}}=(R_1,W,L)$ | $\Delta_{\mathrm{cns}}$ | $\Delta_{\mathrm{ctrl}}$ | $\Delta_{\mathrm{wal}}$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 route aliasing | 6 | 4 | 4 | 6 | (+6, +6, +6) | 3 | 12 | -- |
| F2 blocked prefix | 2 | 0 | 0 | 2 | (+2, 0, 0) | 0 | 2 | -- |
| F3 forbidden route | 0 | 2 | 4 | 0 | (0, 0, 0) | 1 | 2 | -- |
| F4 metric distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 6 | -- |
| F5 ACL policy wall | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 0 | 4 steps |

Two signatures are especially useful. F2 is a pure ACL edge-removal pattern:
direct support changes, but word and Lie bridge channels do not. F3 has no
direct-support mismatch, yet it produces word/Lie bridge mismatches plus a
constraint violation. This makes the appendix domain complementary to Compiler
IR rather than another traffic-shaped graph example.

### Failure Boundaries

Not all domain-model pairs produce informative alignments. The failure modes
documented in Paper XII's Failure Modes and Applicability section (single
sector, dense random, dim-1 sectors,
commuting observables, sector-observable mismatch) apply to paired comparisons
with additional constraints:

- **Alignment failure.** If $\Phi_{\mathrm{sec}}$ or $\Phi_{\mathrm{obs}}$
  cannot be specified (incommensurable sectorizations or observable families),
  the paired comparison reduces to two independent single-system reports.
- **Coverage asymmetry.** If the reference covers state-space regions the
  target cannot represent (or vice versa), $\Delta_{\mathrm{frz}}$ is
  dominated by coverage mismatch rather than structural error.
- **Rate-resolution floor.** $\Delta_{\mathrm{ctrl}}$ requires per-control
  response constants above the tolerance floor. Models with near-zero rates
  produce $\Delta_{\mathrm{ctrl}}$ indistinguishable from noise.
- **Threshold dependence.** The validation controls verify matrix-level sector
  permutation equivariance and conditional rescaling stability away from
  $\tau$, but a multi-scale control changes structural support three times as
  $\tau$ crosses declared block magnitudes. Threshold stability is local, not
  universal.
- **Refinement boundary.** Coarse/fine sector comparison is not covered by the
  fixed-fiber proposition. It requires a pushforward law for structural
  signatures and remains open.
- **Cross-domain discrimination boundary.** Across the 25 failure-mode
  comparisons analyzed here, the normalized seven-coordinate structural vectors have
  same-label and different-label mean distances $1.0915$ and $1.3991$, a
  separation ratio of $1.2818$. This is weak, domain-dominated separation.
  There is only one comparison per failure label within each domain, so no
  within-domain replication or clustering claim is made.

---

## Conclusion

Paper XIII fixes the SOF comparison object
$\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
\Phi;\Theta)$. Alignment supplies common retained coordinates, $\Theta$ fixes
their comparison semantics, and
$\Delta_{\mathrm{audit}}=\operatorname{Compare}(\mathfrak C_{\mathrm{cmp}})$
is the induced output. On each fixed $(\Phi,\Theta)$ fiber, the structural
sub-signature carries a weighted pseudometric, while exact support inclusion
and the single-generator $X^2$ witness separate word transport from Lie
transport.

GridWorld, SIR, Traffic, Compiler IR, Network Routing, and the legitimate
transformation controls demonstrate portability of the comparison grammar.
They do not extend the pseudometric to the full signature or define comparison
between fibers. Those extensions require normalization, symmetrization, and
compatible pushforward laws.

Within the RIME program, Paper XII establishes reporting, Paper XIII establishes
local aligned comparison geometry, and Paper XIV interprets nonzero comparison
coordinates through context-indexed action semantics. This separation keeps
difference, defect, and action as distinct objects.

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
World-model proposals and executable-consequence benchmarks provide relevant
contexts \cite{hafner2025dreamerv3,cai2026whatifworld,lin2026scratchworld}, but
they do not supply evidence for the structural results proved here.

![Alignment regimes and evidence boundary. Regime A supplies the controlled
validation used in this paper. Regimes B and C share the comparison-object
type but
require increasingly strong latent-sector or semantic-probe justification;
they remain application regimes rather than evidence for the fixed-fiber
results.](../../figures/paper13/fig6_alignment_regimes.png)

### Comparison Tooling

A software implementation should preserve the mathematical order of
operations: declare the report pair, record $\Phi$ and $\Theta$, compute the
signature, and only then apply domain-specific interpretation. Automatic
alignment inference must remain distinguishable from a declared alignment,
and trajectory comparison must retain parameter synchronization explicitly.

### Open Problems

1. **Cross-fiber transport.** Define pushforward and transition laws that make
   structural signatures comparable across sector refinement and changing
   observable families.
2. **Alignment inference and stability.** Determine when
   $\Phi_{\mathrm{sec}}$ and $\Phi_{\mathrm{obs}}$ can be inferred, and how
   latent clustering or quantization uncertainty propagates to
   $\Delta_{\mathrm{audit}}$.
3. **Full-signature geometry.** Extend the fixed-fiber pseudometric, if
   possible, to directional constraints, response coordinates, and
   synchronized wall records, with normalization across sector counts.
4. **Observable sufficiency.** Characterize minimal observable families that
   preserve diagnostically relevant distinctions and support causal
   attribution of response mismatches.
5. **Directed comparison costs.** Determine whether normalized channel
   strengths define canonical sector-pair costs without model-dependent
   weighting choices.

---

## Appendix A: Alignment Artifact and Schema Validation

The canonical machine-readable contract is
`schemas/sofaudit/v1.0.schema.json`. A conforming `.sofaudit` record encodes
an aligned comparison, not a second single-system SOF Report.

| Contract component | Required content |
|--------------------|------------------|
| Identity | contract version, artifact type, comparison-object type, audit identifier, and named system |
| Claim boundary | controlled claim status, nonempty qualification, regime, and failure modes |
| Report pair | reference and target report identifiers |
| Alignment | explicit sector and observable alignments |
| Comparison specification | normalization, thresholds, depth semantics, aggregation, and path synchronization when present |
| Audit signature | support, word bridge, Lie bridge, depth, frozen, constraint, response, and wall-record coordinates |
| Legitimate transformation | optional comparison role, transformation contract, and residual evaluation |
| Action boundary | no semantic interpretation, candidate action, risk, expected effect, or policy-selection fields |

The fields `reference`, `target`, `alignment`, and `comparison_specification`
serialize $\mathfrak C_{\mathrm{cmp}}$; the field `signature` serializes
$\Delta_{\mathrm{audit}}$. The contract does not use the single-report key
`sofrs_version`, and a nonzero coordinate does not imply defect. Legitimate
transformation controls retain their raw signature and record contract
residuals separately. The contract rejects
`decision`, `action_semantics`, `action_set`, and `selection`; these belong to
the downstream `.sofaction` layer. Its top-level vocabulary is closed; the
optional `domain` and `wall_note` fields are declared factual qualifications,
not semantic or action outputs.

The validator entry point is:

```
python experiments/paper13/validate_sofaudit.py
```

## Appendix B: Experimental Reproduction

The following scripts and outputs constitute the reproducibility layer. Paths
are relative to `experiments/paper13/`; generated reports and comparison
records are stored in `results/`.

### Controlled Domain Audits

- **GridWorld:** `gridworld_reference_sof.py` constructs the 25-sector
  reference and F1--F5 controls, producing six `.sofreport` and five
  `.sofaudit` records.
- **SIR:** `sir_compartment_sof.py` constructs the three-sector reference and
  F1--F5 controls, producing six `.sofreport` and five `.sofaudit` records.
- **Traffic:** `traffic_intersection_sof.py` constructs the four-sector
  reference and F1--F5 controls, producing six `.sofreport` and five
  `.sofaudit` records.
- **Compiler IR:** `compiler_ir_sof.py` constructs the five-sector reference
  and F1--F5 controls, producing six `.sofreport` and five `.sofaudit` records.
- **Network Routing:** `network_routing_sof.py` constructs the additional
  routing reference and F1--F5 controls, producing six `.sofreport` and five
  `.sofaudit` records.
- **Legitimate transformations:** `before_after_alignment.py` constructs three
  before/after controls, producing six `.sofreport` and three `.sofaudit`
  records.

### Mathematical and Validation Controls

- `signature_metric.py` checks the fixed-fiber structural pseudometric and its
  stated boundary.
- `word_lie_controlled.py` checks the exact-support inequality, finite-threshold
  caveat, strict word-only witness, and GridWorld F4 record.
- `validation/stability_controlled.py` checks permutation equivariance,
  conditional rescaling, and threshold transitions.
- `validation/discrimination_controlled.py` checks coupled coordinates,
  legitimate transformations, and channel-specific controls.
- `validation/discrimination_analysis.py` provides the cross-domain boundary
  analysis over 25 comparisons; it does not support a within-domain replication
  claim.
- `validation/distance_profile.py` computes a declared-channel cost diagnostic
  that is excluded from the report metric.
- `validate_sofaudit.py` validates the canonical schema and all `.sofaudit`
  records.
- `regenerate_tables.py` regenerates `results/signature_tables.md`.

## Appendix C: Geometric Boundary and Outlook

The computational controls establish fixed-fiber and declared-threshold
properties only. Sector permutations and conditional rescalings can be tested
inside a declared fiber, while threshold crossings can change the discrete
signature and changes of alignment data move the representation to a different
comparison domain.

![Stability boundary of the alignment protocol. Sector permutation and
conditional rescaling are controlled within a fixed fiber, while threshold
crossings can change discrete support. Sector refinement or observable
replacement changes the comparison fiber and has no transition law in the
present theory.](../../figures/paper13/fig7_stability_boundary.png)

The resulting local domains do not yet form a global comparison geometry.
Transition maps and pushforward laws must be defined before bundle, connection,
transport, or curvature language can be promoted from outlook to theorem.

![Comparison geometry beyond a fixed fiber. Each alignment fiber carries its
own local structural pseudometric. Transition maps, pushforwards, connections,
transport, and curvature between fibers are displayed as open constructions,
not as results of Paper XIII.](../../figures/paper13/fig8_comparison_geometry_outlook.png)

---

## References

**Program lineage.** Paper VIII supplies the SOF object layer; Paper IX supplies
observable trajectories; Paper X supplies the Universal Observable Pipeline
and Registry; Paper XI supplies wall records; and Paper XII supplies the
single-report protocol consumed here \cite{paper8,paper9,paper10,paper11,paper12}.

**Reporting and audit precedents.** Model cards and end-to-end algorithmic
audit frameworks provide precedents for structured records with explicit
scope and failure boundaries \cite{mitchell2019modelcards,raji2020accountability}.
Paper XIII differs by treating sector and observable alignment as the
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
Paper XIII does not compare raw embeddings. It aligns declared observable
structures and then compares their support, bridge, depth, frozen, response,
constraint, and wall-record shadows.

**Structured metrics.** Hamming distance and graph edit distance provide
standard precedents for discrete structural comparison
\cite{hamming1950codes,gao2010graphedit}. The fixed-fiber pseudometric here is
more restricted than a general report distance: it is defined only on aligned
structural representations under fixed $(\Phi,\Theta)$, and no metric is
claimed on the full directional and path-dependent audit signature.

**World-model deployment context.** Latent-state world models and executable
consequence benchmarks motivate the Regime B/C comparison problem
\cite{lecun2022ami,hafner2025dreamerv3,cai2026whatifworld,lin2026scratchworld}.
They are deployment contexts, not evidence for the fixed-fiber proposition or
the word/Lie separation lemma.
