# Entry Sections and Relation-Valued Descent
## In Single-Defect Circular Automata

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXVII**

*This paper (Paper XXVII of the RIME program) develops fixed-scope entry-section
and relation-valued descent interfaces for single-defect circular automata.*

---

## Abstract

**Problem.** In the fixed `n=6` and `n=7` single-defect circular settings
considered here, local rank descent is not determined by the mass state alone.
Already at rank four, reachable states in these fixed scopes need not admit the
desired local escape, and selecting one shortest word per mass endpoint can
erase source-addressed packet information needed by the proof.

**Approach.** We replace a universal checkpoint predicate by an intrinsic entry
section and replace a deterministic continuation witness by a future-free,
relation-valued completion interface. The resulting proof objects retain typed
ancestry only to the level at which the required source-addressed relation is
proved to descend.

**Results.** In the fixed `n=6` single-defect cycle family, an intrinsic section
selects one legitimate rank-four checkpoint for each of the 1,704
synchronizing rooted rank-five defects. A computer-assisted classification,
validated against the bound source closure, gives 1,700 Type-I-admitting
instances and four genuinely Type-II-only instances, the latter forming two
explicit repayment mechanisms. For the inherited extremal `n=7` carrier, we
prove a Low-Transport theorem by finite symbolic exhaustion. Its canonical
finite elimination consists of one empty shallow cell, 17 typed
post-tag states, 40 kinematic returns reduced to eight admitted returns, and
five rank-three exit relations containing 17 admissible heavy-pair exits.

**Boundary.** These are fixed-scope structural theorems. We do not prove the
Černý conjecture, a general First-Fusion Selector theorem, or an all-`n`
uniform bound on relation-menu size.

**Keywords.** synchronizing automata; Černý conjecture; mass quotient; entry
section; typed ancestry; relation-valued descent; finite proof; provenance

---

## Notation Table {.unnumbered}

| symbol | meaning |
| --- | --- |
| $Q=\mathbb Z/n\mathbb Z$ | finite state set in the declared circular scope |
| $p$ | fixed cyclic permutation letter |
| $d$ | collision-rooted rank-$(n-1)$ defect letter |
| $A=(Q,\{p,d\})$ | rooted single-defect circular action |
| $\mu_t=t_*\mathbf 1$ | image-fiber mass of a transformation $t$ |
| $M(\mu)$, $\tau(\mu)$ | collision mass and maturity potential |
| $S(\mu\to\mu')$ | endpoint-normalized corridor surplus |
| $P_{\le3}$ | exact nonrecursive terminal base $P_1\cup P_2\cup P_3$ |
| $C_r=(A,d,\mu_r,\chi_r)$ | typed source-rank-$r$ context |
| $\Sigma_r^{(n)}$ | future-free selector from source rank $r$ in ambient size $n$ |
| $\mathcal E_6^{\rm entry},\pi_6,\widetilde\sigma_6$ | admissible-entry relation, its action projection, and the chosen right inverse |
| $\kappa(B)$ | intrinsic ordering key for an admissible macro block $B$ |
| $\operatorname{Im}^{\rm idx}(\Sigma)$ | selector image retaining its source index |
| $\mathcal R_4^{(7)}(X)$ | complete source-addressed completion relation at checkpoint $X$ |
| $s_4^{(7)}(X)$ | deterministic serialization of that relation |
| $\mathcal E(Y)$ | admitted endpoint-shortest heavy-pair exit words from $Y$ |
| $\Gamma(Y,t)$ | passive image of $\mathcal E(Y)$ under $t$ |
| $\mathsf N,\mathsf A$ | endpoint-normalization and accounting admission predicates |

---

## 1. Introduction

Let $p$ be a fixed cycle and $d$ a rank-$(n-1)$ defect letter with one binary
kernel. The mass quotient records how transformation fibers merge, while
corridor compression records the rank-preserving transport required before a
strict fusion. This framework converts a reset route into a sequence of local
fusion corridors with exact length accounting.

The first obstruction is semantic. Already in the fixed single-defect cycle
scopes studied here, a rank-four mass state may be reachable in the semigroup
without being a legitimate checkpoint for the recursive proof. Even activated
ancestry does not make every rank-four checkpoint locally escapable. The fixed
`n=6` solution is therefore not another state predicate: it is a section that
chooses one legitimate activated checkpoint from each synchronizing rooted
action.

The second obstruction is representational. At `n=7`, two tied shortest words
can reach the same mass endpoint while transporting different labelled packet
identities. A quotient that retains only the endpoint is therefore too coarse
for a moved-slot relation. At the opposite extreme, retaining the complete
action-resolved digest audited here merely re-encodes the finite context. The
useful interface lies between these extremes: a finite, future-free relation
menu with an existentially certified descending member.

The two fixed-rank results support one organizing sentence:

> **$n=6$ chooses a legitimate checkpoint; $n=7$ determines the relation
> structure it must retain.**

### 1.1 From Mechanism Classification to Proof-State Architecture

A mechanism-first organization would classify balanced and exceptional
repayment patterns, prove descent into $P_{\le3}$, and then seek a higher-rank
return. The finite obstructions below show that this classification is
downstream of a prior semantic question: which proof state makes local descent
well-defined?

The mass state is too coarse to certify a legitimate recursive checkpoint.
Typed activation restores ancestry but still does not choose a descending
representative, which forces the intrinsic entry section of Section 3. After
that choice has been made, a second quotient failure occurs: tied
endpoint-shortest words can carry different source-addressed packet
transports. Retaining the particular complete action-resolved digest audited
here, however, merely re-encodes the finite context. The resulting progression
of proof objects is therefore

$$
 \boxed{
 \begin{gathered}
 \text{legitimate checkpoint choice}
 \longrightarrow \text{endpoint-quotient failure}\\[-2pt]
 \longrightarrow \text{source-addressed relation}
 \longrightarrow \text{sufficient finite descent interface}
 \end{gathered}.}
 \tag{1.1}
$$

This is a conceptual progression, not a logical dependency between the
fixed-`n=6` and fixed-`n=7` theorems. Local descent mechanisms remain necessary
realizations inside the interface, but their taxonomy and recursive
composition remain outside the present theorem spine.

> **Terminology boundary.** *Relation-valued descent* here means a finite,
> source-addressed completion relation attached to one typed proof context.
> Paper XXIV instead studies patch-indexed relation families, natural-join
> reconstruction, and the $\alpha$-acyclicity obstruction [@paper24]. The two
> papers share a descent philosophy, not a mathematical object or theorem.

![The fixed-`n=6` section chooses a legitimate checkpoint; the fixed-`n=7`
relation interface preserves the source-addressed transport needed for
descent. Each arrow denotes a within-scope construction dependency; the
diagram asserts neither an implication from the `n=6` theorem to the `n=7`
theorem nor an all-`n` recursion.](../../figures/paper27/fig1_entry_relation_interface.png)

### 1.2 Contributions

This paper makes four fixed-scope contributions.

1. **Legitimate checkpoint selection.** It defines an intrinsic `n=6` entry
   section and proves that state gates, typed activation, and section choice
   have different logical roles.
2. **Quotient failure and source addressing.** It shows that tied
   endpoint-shortest representatives may carry different packet-addressed
   transports, so the required relation does not descend through the mass
   endpoint quotient.
3. **A sufficient proof interface.** It isolates the fixed-scope contract
   used here: bounded, future-free, relation-valued, and descent-certified,
   with provenance closure imposed separately as a publication requirement.
4. **Fixed-scope realizations.** The `n=6` indexed section graph has 1,700
   Type-I-admitting and four Type-II-only instances, while the inherited
   extremal `n=7` carrier satisfies Low Transport through a complete finite
   symbolic elimination.

### 1.3 Nonclaims

No statement below asserts any of the following:

- that every rank-four mass state admits local descent;
- that activation alone guarantees descent;
- that every member of a relation menu succeeds;
- that a successful member is unique;
- that the observed fixed-scope menu bounds are uniform in `n` or rank;
- that the fixed `n=6,7` results prove Forced FFS, General FFS, or the Černý
  conjecture.

The design objective is to reduce the retained proof state without
re-encoding the full context; no mathematical minimality claim is made.

---

## 2. Mass, Corridors, and Two-Corridor Accounting

Words act from left to right. Thus, for a mass state $\mu$ and a letter $a$,

$$
 \mu_{ta}=a_*\mu_t.
$$

For a transformation $t:Q\to Q$, define its image-fiber mass by

$$
 \mu_t(y)=|t^{-1}(y)|.
$$

Its rank and collision mass are

$$
 r(\mu)=|\operatorname{supp}(\mu)|,
 \qquad
 M(\mu)=\sum_y\binom{\mu(y)}2.
$$

For a nonuniform mass state of rank `r`, define the maturity potential

$$
 \tau(\mu)=\|\mu\|_2^2+(r-1)(n-r)-2n+1,
$$

with the separate convention $\tau(\mathbf1)=0$ at the uniform initial mass.

A corridor from rank $r$ to rank $r-q$ has endpoint-normalized length $\ell$.
Writing $\Delta M=M(\mu')-M(\mu)$, its surplus is

$$
 S(\mu\to\mu')
 =\tau(\mu')-\tau(\mu)-\ell
 =2\Delta M+q(2r-q-n-1)-\ell.
 \tag{2.1}
$$

Along a reset route the surpluses telescope:

$$
 \sum S=(n-1)^2-\text{total word length}.
 \tag{2.2}
$$

The two-corridor rule permits exactly two macro types.

- **Type-I:** one corridor with `S>=0`.
- **Type-II:** two corridors with $S_1<0$ and $S_1+S_2\ge0$.

The exact low-rank sets $P_1,P_2,P_3$ form the terminal base used here; this
base is not defined recursively. We write

$$
 P_{\le3}=P_1\cup P_2\cup P_3.
$$

The distinction between a mass endpoint and a source-addressed corridor is
essential. Endpoint normalization is imposed on complete words for a fixed
endpoint; it does not authorize quotienting tied shortest representatives
when their packet-addressed transports differ.

---

## 3. Fixed `n=6`: An Intrinsic Entry Section

Let

$$
 Q=\mathbb Z/6\mathbb Z,
 \qquad p(i)=i+1.
$$

Let $d$ be a collision-rooted rank-five defect with binary kernel $K_d$ and
collision image $0$. Let $m$ be the unique coordinate omitted from
$\operatorname{im}(d)$. The kernel-image mass $\mu_d=d_*\mathbf1$ has mass two
at $0$, mass zero at $m$, and mass one elsewhere.

Define

$$
 a(d)=\min\{a\in\{0,1,2\}:p^a(m)\notin K_d\}.
 \tag{3.1}
$$

The minimum exists because $m,p(m),p^2(m)$ are distinct while $K_d$ has two
points.

### Lemma 3.1 (short-entry normal form)

Every endpoint-shortest strict block from $\mu_d$ has the form

$$
 p^{a(d)}d,
 \qquad a(d)\in\{0,1,2\}.
$$

**Proof.** If the current rank-five support is $Q\setminus\{x\}$ with
$x\in K_d$, then a non-strict application of $d$ satisfies

$$
 d(Q\setminus\{x\})=\operatorname{im}(d)=Q\setminus\{m\}.
 \tag{3.2}
$$

Thus every non-strict `d` resets the support to the same canonical support.
In a strict word

$$
 p^{a_0}d\,p^{a_1}d\cdots p^{a_k}d,
$$

all non-strict initial segments can be deleted while preserving strictness of
the final segment. A shortest strict word therefore contains one copy of `d`,
and (3.1) gives `a<=2`. QED.

Every such short entry is activated and Type-I: at rank five its length is at
most three and its first fusion has nonnegative surplus.

### Definition 3.2 (predecessor idempotent)

Set

$$
 \operatorname{PredIdem}(d)
 \iff d^2=d
 \quad\text{and}\quad
 K_d=\{0,p^{-1}(0)\}.
$$

Define the intrinsic section

$$
 \sigma_6(d)=
 \begin{cases}
 p^5d,&\operatorname{PredIdem}(d),\\
 p^{a(d)}d,&\text{otherwise}.
 \end{cases}
 \tag{3.3}
$$

The exceptional clause recognizes predecessor-collapse geometry; it does not
recognize an action string or query future escape.

### Proposition 3.3 (rooted scope classification)

The 1,800 collision-rooted binary rank-five defects split exactly into

$$
 24\ \mathcal A\text{-preserving}
 \;\sqcup\;
 72\ \mathcal E\text{-preserving}
 \;\sqcup\;
 1\ \operatorname{PredIdem}
 \;\sqcup\;
 1703\ \text{generic defects},
 \tag{3.4}
$$

where

$$
 \mathcal A=\{\{0,3\},\{1,4\},\{2,5\}\},
 \qquad
 \mathcal E=\{\{0,2,4\},\{1,3,5\}\}.
$$

The first two classes preserve a nontrivial quotient and are not
synchronizing. In this exact fixed scope, the remaining 1,704 defects are
synchronizing. The converse direction in this sentence is a finite
classification, not an all-`n` block-system theorem.

Let $\mathcal S_6$ denote these 1,704 synchronizing rooted defects. Counts for
the section are taken in its indexed graph

$$
 \operatorname{Im}^{\rm idx}(\sigma_6)
 =\{(d,\operatorname{end}(\sigma_6(d))):d\in\mathcal S_6\}.
$$

Thus the action index is retained even when two actions have the same mass
endpoint. The ordinary endpoint projection of this graph is not what is
counted below.

To make the word *section* literal, define the admissible-entry relation

$$
 \mathcal E_6^{\rm entry}
 =\{(d,w):d\in\mathcal S_6,\;
     w\text{ is an admissible activated }5\to4\text{ entry for }d\},
 \qquad
 \pi_6(d,w)=d.
 \tag{3.4a}
$$

The selected lift

$$
 \widetilde\sigma_6(d)=(d,\sigma_6(d)),
 \qquad
 \pi_6\circ\widetilde\sigma_6
 =\operatorname{id}_{\mathcal S_6}
 \tag{3.4b}
$$

is therefore a choice section of $\pi_6$. It is unrelated to the
`Option`-valued signature sections of Paper XXIV [@paper24].

### Lemma 3.4 (predecessor zero-surplus comb at n=6)

For the predecessor idempotent, repeated use of $p^5d$ produces

$$
 (2,1,1,1,1,0)
 \xrightarrow{p^5d}(3,1,1,1,0,0)
 \xrightarrow{p^5d}(4,1,1,0,0,0)
 \xrightarrow{p^5d}(5,1,0,0,0,0)
 \xrightarrow{p^5d}(6,0,0,0,0,0),
$$

with zero surplus in every block. The endpoint-shortest $p^2d$ entry is an
activated hostile control, but

$$
 (d,\operatorname{end}(p^2d))
 \notin\operatorname{Im}^{\rm idx}(\sigma_6).
$$

### Theorem 3.5 (fixed-n=6 entry-section descent)

For every synchronizing collision-rooted binary rank-five defect $d$, the word
$\sigma_6(d)$ is an activated rank-five-to-rank-four entry, and its endpoint
admits a local Type-I or Type-II macro descent into $P_{\le3}$.

Partition the indexed graph into its Type-I-admitting and genuinely
Type-II-only parts. More precisely,

$$
 \operatorname{Im}^{\rm idx}(\sigma_6)
 =\operatorname{Im}^{\rm idx}_{I}(\sigma_6)
 \sqcup
 \operatorname{Im}^{\rm idx}_{II\setminus I}(\sigma_6),
 \qquad
 \left(
 |\operatorname{Im}^{\rm idx}_{I}(\sigma_6)|,
 |\operatorname{Im}^{\rm idx}_{II\setminus I}(\sigma_6)|
 \right)=(1700,4).
 \tag{3.5}
$$

The four Type-II-only indexed instances form two mechanisms, each occurring
twice:

$$
\begin{array}{c|c|c}
\text{source partition}&\text{first fusion}&\text{repayment fusion}\\
\hline
(2,2,1,1)&1+2\to3&3+2\to5\\
(3,1,1,1)&1+1\to2&3+2\to5.
\end{array}
 \tag{3.6}
$$

Both terminate at partition $(5,1)$ in the exact set $P_2$. Their total
surpluses are respectively

$$
 14-(\ell_1+\ell_2)
 \qquad\text{and}\qquad
 12-(\ell_1+\ell_2).
$$

The theorem quantifier is existential over legal receipts. It does not require
the canonically serialized receipt to have the displayed common form.

The executable enumeration establishes the finite classification and the
`1700+4` indexed-graph decomposition. The bound certificate records its
theorem-facing output, while the release validator checks source binding and
closure. The symbolic equalities supplied in the proof remain mathematical
premises rather than conclusions inferred from the certificate files.

### Remark 3.6 (what the section repairs)

The fixed-scope hierarchy is strict:

$$
 \text{state gate}
 <\text{typed activation}
 <\text{typed section choice}.
 \tag{3.7}
$$

State-local rank-four escape has genuine counterexamples. Activation removes
counterfactual placements but still leaves activated endpoints without local
descent. The intrinsic section succeeds on all 1,704 synchronizing rooted
actions. Thus activation is necessary for semantic legitimacy; in this
complete fixed scope it is not sufficient for descent, whereas the section
choice is.

---

## 4. From Deterministic Witnesses to Relation-Valued Proof Objects

### Definition 4.1 (source-rank convention and inherited section chain)

For ambient size `n`, a typed source-rank-`r` context is written

$$
 C_r=(A,d,\mu_r,\chi_r),
$$

where $A=(Q,\{p,d\})$ is the rooted action, $\mu_r$ has rank $r$, and $\chi_r$
records the labelled packet placement, activation ancestry, and source roles
needed by the local admissible relation. The subscript of
$\Sigma_r^{(n)}$ is always the **source rank**, while the superscript is the
ambient cardinality. Thus a selected block

$$
 B=\Sigma_r^{(n)}(C_r)
$$

has rank-`r-1` endpoint, and the endpoint context
$\operatorname{End}(C_r,B)$ inherits the endpoint mass, labelled packets, and
the fresh/parent packet data of the selected fusion. In particular,

$$
 \Sigma_5^{(6)}=\sigma_6,
 \qquad
 \Sigma_6^{(7)}:6\to5,
 \qquad
 \Sigma_5^{(7)}:5\to4.
$$

For an admissible source-addressed macro block `B`, let

$$
 \kappa(B)=
 (\ell(B),\operatorname{type}(B),w_1(B),w_2(B),
   \rho(B),\mu_{\operatorname{end}B})
$$

in lexicographic order, where Type I precedes Type II and `rho(B)` is the
ordered boundary-parent coordinate tuple of the first fusion. This is an
intrinsic serialization of the local relation, not a downstream success key.

For a rooted synchronizing defect at $n=7$, start with

$$
 C_6(d)=(A_d,d,\mu_d,\chi_6(d)),
 \qquad \mu_d=d_*\mathbf1,
$$

where $\chi_6(d)$ is the labelled kernel-image packet placement. The two
future-free selectors are defined as follows.

1. **Rank-six selector.** $\Sigma_6^{(7)}$ forms all activated,
   endpoint-normalized Type-I blocks from $\mu_d$ to rank five and selects the
   $\kappa$-least block. For the intrinsic predecessor idempotent only, it
   selects the declared oriented return $p^6d$.
2. **Rank-five selector.** First form

   $$
   C_5(d)=\operatorname{End}
   \bigl(C_6(d),\Sigma_6^{(7)}(C_6(d))\bigr).
   $$

   Then $\Sigma_5^{(7)}$ forms the complete endpoint-normalized admissible
   macro relation, restricts it to blocks ending at rank four, and selects its
   $\kappa$-least member. Every block in this restricted relation is Type I:
   a Type-II block contains two strict drops and bypasses rank four.

Thus the inherited chain is

$$
 C_6(d)
 \xrightarrow{\ \Sigma_6^{(7)}\ }
 C_5(d)
 \xrightarrow{\ \Sigma_5^{(7)}\ }
 C_4(d).
$$

Both choices read only the rooted action, current mass, typed ancestry, and
the current local admissible relation. Neither selector reads

$$
 \begin{gathered}
 L_4^{(7)},\quad P_{\le3}\text{ membership},\quad
 \text{target winning},\quad W^{2C},\\
 \text{reset coaccessibility},\quad\text{or a Bellman policy}.
 \end{gathered}
$$

The predecessor correction occurs only in $\Sigma_6^{(7)}$.

Let $\mathcal C_5^{(7)}$ be the complete finite set of inherited contexts
$C_5(d)$ generated by this first selector in the declared $n=7$ scope. The second
selector defines the indexed graph

$$
 \operatorname{Im}^{\rm idx}(\Sigma_5^{(7)})
 =\{(C,\operatorname{end}(\Sigma_5^{(7)}(C))):
       C\in\mathcal C_5^{(7)}\}.
$$

The selector is defined on all 15,120 context-indexed instances;
projected rank-four endpoints are not asserted to be distinct. This graph is
the image of the checkpoint selector only; all of its selected blocks have one
strict drop and are Type I in the source-rank sense above.

For an indexed checkpoint

$$
 X=(C,C_4)\in\operatorname{Im}^{\rm idx}(\Sigma_5^{(7)}),
$$

let $\mathcal R_4^{(7)}(X)$ be the complete source-addressed relation of legal
Type-I and Type-II completion receipts from $C_4$ into $P_{\le3}$. The source
index $C$ is retained, so equal projected rank-four mass endpoints are not
silently identified. The declared deterministic serialization is

$$
 s_4^{(7)}(X)=\operatorname{Serialize}
 \bigl(\mathcal R_4^{(7)}(X)\bigr).
$$

It is a shortest-witness view of the relation, not a selector in the inherited
section chain or the theorem quantifier. Across the 15,120 indexed checkpoints,
this serialization chooses 14,936 Type-I receipts and 184 Type-II receipts.

The quantifier-correct existential split is instead induced by the complete
completion relation. Define

$$
 \begin{aligned}
 \mathcal G_I^{(7)}
 &=\{X:\mathcal R_4^{(7)}(X)\text{ contains a Type-I receipt}\},\\
 \mathcal G_{II\setminus I}^{(7)}
 &=\{X:\mathcal R_4^{(7)}(X)\text{ contains no Type-I receipt but contains a
 Type-II receipt}\}.
 \end{aligned}
$$

Then

$$
 \operatorname{Im}^{\rm idx}(\Sigma_5^{(7)})
 =\mathcal G_I^{(7)}\sqcup\mathcal G_{II\setminus I}^{(7)},
 \qquad
 (|\mathcal G_I^{(7)}|,|\mathcal G_{II\setminus I}^{(7)}|)
 =(15093,27).
 \tag{4.1}
$$

This discrepancy is not cosmetic. A selected witness is a serialization
choice; the theorem object is the complete legal receipt relation.

We use *completion relation* for the complete legal receipt relation and
*relation menu* for the finite, theorem-facing family of future-free role
channels exposed to a descent argument. A role channel may contain more than
one concrete receipt; the existential descent statement ranges over the
receipts represented by the menu.

Common-witness audits support an intermediate representation. Coarse
signatures do not determine one completion template, while the particular
complete local-relation digest used in the audit is injective on all 15,120
contexts and therefore supplies no compression on this scope. Intermediate
labelled classes nevertheless admit finite observed covers. Those broader
counts are pre-release discovery records, not theorem claims, definitions, or
members of the public release identity.

The extremal carrier of Sections 5--8 is not an independently sampled
rank-four census. It is the 35-instance cell of the indexed checkpoint graph
in which both selected section blocks are $p^2d$, the inherited rank-five
partition is $(2,2,1,1,1)$, $\Sigma_5^{(7)}$ fuses $1+1$ with length three and
surplus zero, and the resulting rank-four partition is $(2,2,2,1)$ with the
declared $F_4/K_d$ carrier incidence. Sections 5--8 study
$\mathcal R_4^{(7)}$ on this cell; Section 5 first reconstructs the carrier
intrinsically.

### Definition 4.2 (proof-interface contract)

The relation $\mathcal R_r(C)$ below is context-local: it is attached to one
typed proof context $C$ and ranges over source-addressed completion receipts.
It is neither a patch family nor a natural-join object, and no
$\alpha$-acyclicity theorem is invoked. Those objects belong to the distinct
typed-context descent problem of Paper XXIV [@paper24].

A fixed-scope completion interface assigns each typed rank-$r$ context $C$ a
finite relation menu. Write $\mathcal R_r(C)$ for its realized completion
relation: the set of all concrete receipts represented by the menu. The
interface is required to be:

| property | mathematical contract |
| --- | --- |
| **Bounded** | each declared context has a finite menu; no all-`n` uniform constant is asserted |
| **Future-free** | construction reads no downstream success, winning, Bellman, or reset-coaccessibility label |
| **Relation-valued** | tied representatives and packet identities are retained whenever the observable does not descend to a quotient |
| **Descent-certified** | at least one admissible menu member descends |

Provenance closure is a separate publication contract: implementation, bound
artifacts, and source closure must agree. Any performed producer replay must
also agree, and replay status is recorded explicitly.

The descent condition is deliberately existential:

$$
 \exists B\in\mathcal R_r(C):
 B\text{ is admissible and descends}.
 \tag{4.2}
$$

It neither requires every menu member to succeed nor chooses a unique winning
channel.

### Remark 4.3 (lossy endpoint quotient)

Let $W_{\min}$ be the complete fixed-endpoint shortest-word relation and let

$$
 q:W_{\min}\to\mathcal E
$$

forget the word while retaining its mass endpoint. For a source-addressed
observable `R`, the implication

$$
 q(w_1)=q(w_2)\Longrightarrow R(w_1)=R(w_2)
 \tag{4.3}
$$

is false in the `n=7` carrier. Tied shortest words can reach the same mass
endpoint while fusing different packet identities. The correct theorem object
is therefore the fixed-endpoint shortest-word relation, not one BFS
representative per endpoint.

This correction simplifies the canonical relation profile to

$$
 72=61_{\rm direct}+5_{\rm one\text{-}return}+1_{\rm OC}+5_{\rm bad}.
 \tag{4.4}
$$

The numbers in (4.4) are verification data, not the Low-Transport theorem.

---

## 5. The Extremal `n=7` Carrier

Let

$$
 Q=\mathbb Z/7\mathbb Z,
 \qquad p(i)=i+1,
 \qquad K_d=\{0,6\},
$$

and write

$$
 d=(0,\pi(1),\ldots,\pi(5),0),
 \qquad \pi\in S_5.
$$

Consider the inherited extremal rank-four carrier of partition `(2,2,2,1)`
created by two `p^2d` returns. Its local action is parameterized by

$$
 (h,\alpha,\beta)\in\{3,4,5\}\times S_3\times S_2.
 \tag{5.1}
$$

Set

$$
 \lambda(1)=1,
 \qquad \lambda(2)=2,
 \qquad \lambda(3)=h,
 \qquad \alpha(j)=\pi(\lambda(j)).
$$

### Lemma 5.1 (carrier reconstruction)

The triple $(h,\alpha,\beta)$ uniquely determines $\pi$. Explicitly,

$$
 \pi(1)=\alpha(1),
 \qquad
 \pi(2)=\alpha(2),
 \qquad
 \pi(h)=\alpha(3).
 \tag{5.2}
$$

If $\{u,v\}=\{3,4,5\}\setminus\{h\}$ with $u<v$, then

$$
 \begin{array}{ll}
 \beta=I:&(\pi(u),\pi(v))=(4,5),\\
 \beta=S:&(\pi(u),\pi(v))=(5,4).
 \end{array}
 \tag{5.3}
$$

The ambient 36 carrier actions are therefore exactly

$$
 \mathcal C_{\rm amb}^{(7)}
 =\{3,4,5\}\times S_3\times S_2.
$$

Define the predecessor boundary and selected extremal carrier by

$$
 \mathcal C_{\rm pred}^{(7)}=\{(3,e,I)\},
 \qquad
 \mathcal C_{\rm sel}^{(7)}
 =\mathcal C_{\rm amb}^{(7)}\setminus\mathcal C_{\rm pred}^{(7)}.
 \tag{5.4}
$$

Thus the 36 oriented parameter cells are the disjoint union of the
35-context selected carrier and one predecessor section exception. Sections
6--8 analyze $\mathcal C_{\rm sel}^{(7)}$; the excluded predecessor cell is
retained only as an adjacent boundary case.

### Lemma 5.2 (packet recursion)

Let `F_4` be the packet created by the selected rank-five-to-rank-four return,
let $D_1,D_2$ be the other mass-two packets, and let $s$ be the singleton.
Their rooted coordinates are

$$
 \boxed{
 F_4=0,
 \qquad D_1=\alpha(2),
 \qquad D_2=\pi(\alpha(2)+2),
 \qquad s=\pi(\alpha(3)+2).
 }
 \tag{K}
$$

All coordinates are taken modulo seven.

### Definition 5.3 (moved-slot relation)

For $j\in\operatorname{Mov}(\alpha)$, let $W_j(C)$ be the complete relation of
role-compatible, endpoint-normalized heavy-comb associations in which the
incoming mass-two packet traverses the tagged edge

$$
 \lambda(j)\xrightarrow{d}\alpha(j)
$$

during its own fusion corridor. Define `Land_1(W_j)` to be the subrelation
whose final singleton offset is one. The definition is future-free and retains
all tied endpoint-shortest representatives.

---

## 6. Canonical Five-Cell Elimination

The Low-Transport proof uses positive constructor soundness everywhere and
complete relation exhaustion only at the five parameter cells where a
universal negative statement is required. This section packages that finite
elimination as five theorem-facing equalities.

### 6.1 Typed shallow states

A post-tag state is

$$
 \widehat X=(X_{\rm place},c,\text{incoming role},k,\delta,
 \text{labelled corridor source}),
 \tag{6.1}
$$

where $c$ is the corridor index, $k$ is the marked-prefix length, and $\delta$
is the accounting state needed by later admission. Prefixes may be quotiented
only after they induce the same typed state and the same normalization and
accounting semantics.

The five menu-bad parameter cells are

$$
 \mathfrak B=
 \{(132,2,3,I),(213,2,3,I),(213,2,3,S),
   (213,2,4,I),(321,3,3,I)\}.
 \tag{6.2}
$$

Here $\alpha$ is written in one-line notation on the three low slots.

### Lemma 6.1 (empty shallow cell)

For direct and one-return germs, equivalently post-tag depth $r\in\{0,1\}$,

$$
 \boxed{\mathcal X^{\rm sh}_3(321;h=3,\beta=I)=\varnothing.}
 \tag{6.3}
$$

The two corridor roles fail for different reasons. A first-corridor mark makes
every candidate violate the two-corridor accounting bound
$\ell_1+\ell_2\le20$; a second-corridor mark violates fixed-endpoint
minimality. No landing test is used.

The superscript `sh` is essential. The full tagged relation is nonempty and
contains a depth-two endpoint-shortest representative. Thus (6.3) is an
empty canonical shallow-menu relation, not an empty full relation.

### Lemma 6.2 (back-solving exhaustion)

For the four nonempty cells in (6.2), solving the typed reverse constraints
gives

$$
 \boxed{
 \bigsqcup_b\operatorname{Sol}_{BT}(b)
 =\{\widehat X_1,\ldots,\widehat X_{17}\}.
 }
 \tag{6.4}
$$

The reverse calculation starts from the terminal fusion roles, uses unique
reverse rotations, and branches under `d^{-1}` only at the collision image.
Every rejected branch has one of four declared reasons:

$$
 \begin{aligned}
 E&=\text{early fusion}, & R&=\text{role violation},\\
 N&=\text{fixed-endpoint nonminimality}, &
 A&=\text{debt or length violation}.
 \end{aligned}
$$

Exactly one displayed state, $\widehat X_5$, has two tied provenances; they
may be identified because they induce identical typed placement and gate
semantics. This is a valid quotient, in contrast to (4.3). The marked-prefix
count is retained in Appendix B as an exhaustion checksum rather than a
theorem object.

### Lemma 6.3 (return admission)

For a typed state $\widehat X$, let $Q^{\rm kin}(\widehat X)$ be the rotations
satisfying the rank-preserving and role-preserving kinematic equations. Let
$N(\widehat X,q)$ and $A(\widehat X,q)$ denote fixed-endpoint normalization and
accounting admission.
Then, row by row,

$$
 \boxed{
 Q(\widehat X_i)
 =\{q\in Q^{\rm kin}(\widehat X_i):
       N(\widehat X_i,q)=A(\widehat X_i,q)=1\}.
 }
 \tag{6.5}
$$

On this five-cell surface, normalization and accounting are the complete
admission interface. The displayed rows contain both accounting-only and
normalization-only rejections, so neither gate is implied by the other. The
aggregate rejection counts are recorded in Appendix B as transcription
checks. Equality (6.5), not those counts, is the theorem.

### Lemma 6.4 (heavy-pair exit exhaustion)

The first-corridor branches in (6.4)-(6.5) produce five typed rank-three
states $Y_k$. Define

$$
 \mathcal E(Y_k)
 =\{w:w\text{ is an admissible endpoint-normalized strict
 heavy-pair exit from }Y_k\}.
 \tag{6.6}
$$

Then $\mathcal E(Y_k)$ equals the complete displayed word set in the finite exit table.
The shortest-parent DAG first exhausts fixed-endpoint shortest words, after
which the heavy-pair role and debt filters are applied. Appendix B records the
complete admitted/over-debt/wrong-pair partition as a completeness checksum; the
word-set equality (6.6) is the theorem-facing statement.

For a passive singleton at coordinate `t`, define the image relation

$$
 \boxed{
 \Gamma(Y_k,t)=\{w(t):w\in\mathcal E(Y_k)\}.
 }
 \tag{6.7}
$$

The five exact images are

$$
\begin{aligned}
 \Gamma(Y_1,4)&=\{2,4,5\},\\
 \Gamma(Y_2,5)&=\{2,4,5\},\\
 \Gamma(Y_3,5)&=\{3,4,5\},\\
 \Gamma(Y_4,5)&=\{2,3,5\},\\
 \Gamma(Y_5,5)&=\{3,5\}.
\end{aligned}
 \tag{6.8}
$$

No singleton image is used to choose an exit word; (6.8) is the passive
image of the already exhausted relation (6.6).

### Corollary 6.5 (five negative spectra)

The complete direct and one-return landing spectra at the cells in
$\mathfrak B$ are

| cell | direct spectrum | one-return spectrum |
| --- | --- | --- |
| `132/2,(3,I)` | `{2,4,5}` | `{2,4,5}` |
| `213/2,(3,I)` | `{3,4,5}` | `{4}` |
| `213/2,(3,S)` | `{4}` | empty |
| `213/2,(4,I)` | `{2,3,4,5}` | `{3,5}` |
| `321/3,(3,I)` | empty | empty |

Offset one is absent in every row, and the independent Orbit-Closure germ is
inapplicable at all five parameter cells. The corollary is a set-image
consequence of Lemmas 6.1-6.4; it bears no independent search or completeness
burden.

Appendix B displays the complete 17-row back-solving table, the rowwise
40-to-8 admission table, and the five complete heavy-pair word sets. Their
equality proofs, not the counts alone, are the mathematical premises.

---

## 7. Low Transport

Call a moved direction `j` menu-good if a sound direct, one-return, or
Orbit-Closure constructor supplies a member of `W_j(C)` landing at offset one.
Constructor soundness gives only the implication needed below:

$$
 \operatorname{MenuGood}_j
 \Longrightarrow
 \operatorname{Land}_1(W_j)\ne\varnothing.
 \tag{7.1}
$$

No converse or normal-form theorem for all deep successful germs is used.

### Lemma 7.1 (transposition landing)

The five-cell elimination yields

$$
\begin{aligned}
 B_2(132)&\iff h=3\land\beta=I,
 &B_3(132)&\iff\bot,\\
 B_1(213)&\iff\bot,
 &B_2(213)&\iff h=3\lor(h=4\land\beta=I),\\
 B_1(321)&\iff\bot,
 &B_3(321)&\iff h=3\land\beta=I.
\end{aligned}
 \tag{7.2}
$$

Thus every transposition has at least one good moved direction:

$$
 \alpha\text{ a transposition}
 \Longrightarrow
 \exists j\in\operatorname{Mov}(\alpha):
 \operatorname{Land}_1(W_j)\ne\varnothing.
 \tag{7.3}
$$

The existential quantifier is sharp: five transposition contexts have only
one good direction.

### Lemma 7.2 (three-cycle landing)

If $\alpha=231$, every moved direction has a direct offset-one constructor. The
same holds for $\alpha=312$ except at $(h,\beta,j)=(5,S,2)$, where the explicit
Orbit-Closure germ supplies the relation. Hence

$$
 \alpha\text{ a three-cycle}
 \Longrightarrow
 \forall j\in\{1,2,3\},
 \quad \operatorname{Land}_1(W_j)\ne\varnothing.
 \tag{7.4}
$$

The Orbit-Closure word closes the tagged packet's four-cycle before the final
strict fusion. A separate Root-Shift Exchange identity remains valid but is
not a dependency of the canonical proof after tied-shortest correction.

### Theorem 7.3 (Low-Transport Lemma)

Let $C$ be a non-predecessor extremal carrier context. If $\alpha$ is
nonidentity, then

$$
 \boxed{
 \exists j\in\operatorname{Mov}(\alpha),
 \quad
 \exists B\in W_j(C):
 \operatorname{Land}(B)=1.
 }
 \tag{7.5}
$$

Equivalently, $\alpha\ne e$ implies $1\in R_4(C)$.

**Proof.** Every nonidentity element of $S_3$ is a transposition or a
three-cycle. Apply Lemma 7.1 or Lemma 7.2. QED.

---

## 8. The Identity Boundary and Credit Reallocation

When $\alpha=e$, the moved-slot menu is empty. The ambient 36-cell table has
six such cells: five belong to $\mathcal C_{\rm sel}^{(7)}$, while the
predecessor cell belongs to $\mathcal C_{\rm pred}^{(7)}$.

| $h$ | $\beta$ | $\pi$ | selected outcome or boundary status |
| ---: | --- | --- | --- |
| 3 | $I$ | $e$ | adjacent boundary: predecessor section exception |
| 3 | `S` | `(4 5)` | offset-one heavy comb |
| 4 | `I` | `(3 4)` | offset-two heavy-comb bridge |
| 4 | `S` | `(3 5 4)` | offset-one heavy comb |
| 5 | `I` | `(3 4 5)` | offset-one heavy comb |
| 5 | `S` | `(3 5)` | rank-two `(5,2)` fallback |

The predecessor cell is outside the selected carrier and uses the independent
$p^6d$ section. The $(3\ 4)$ cell
uses an explicit $p^3dp^2d$ bridge. The $(3\ 5)$ cell uses the rank-two $(5,2)$
fallback.

For the source partition `(2,2,2,1)`,

$$
 \tau(2,2,2,1)=9,
 \qquad
 \tau(7)=36.
$$

Thus the total maturity credit is 27. The heavy-comb and fallback channels
allocate it as

$$
 \boxed{
 20+B_2(6,1)=20+7=27,
 \qquad
 12+B_2(5,2)=12+15=27.
 }
 \tag{8.1}
$$

The `(5,2)` fallback does not create credit. It spends eight fewer units in
the rank-four prefix and leaves eight additional units for the rank-two tail.

### Theorem 8.1 (extremal carrier completion at n=7)

Every context in the 35-context selected carrier
$\mathcal C_{\rm sel}^{(7)}$ admits a local completion into the exact low-rank
base. Its 30 cells with $\alpha\ne e$ are covered by Theorem 7.3. Its five
non-predecessor cells with $\alpha=e$ are covered by three direct heavy-comb
channels, one bridge, and one $(5,2)$ fallback. Equation (8.1) closes the two
possible terminal credit allocations.

The predecessor cell $\mathcal C_{\rm pred}^{(7)}$ is outside the theorem
domain. It is recorded in the ambient boundary table and handled independently
by the $p^6d$ section.

This theorem is a human-auditable finite proof with source-bound computational
verification. It is not an all-`n` return theorem.

---

## 9. Sufficient Proof Interfaces

The fixed-rank results supply a sufficient proof-interface contract and
suggest the following proof-design principle:

> **Proof-interface principle.** A quotient is admissible only after the
> theorem-relevant observable is shown to descend through it.

Equivalently, compress proof-relevant information only through quotients on
which the required relation is proved to descend. The design objective is to
reduce the retained proof state without re-encoding the full context; no
mathematical minimality claim is made.

At `n=6`, the mass state is too coarse to choose a legitimate checkpoint;
typed activation and an intrinsic section are needed. At `n=7`, one shortest
word per mass endpoint is too coarse for packet-addressed transport, while the
particular full action-resolved digest audited here is injective and therefore
too fine to compress this scope. The theorem uses typed states and set-valued
relations at the intermediate level.

Schematically, on the audited fixed scopes,

$$
 \boxed{
 \text{too-coarse endpoint quotient}
 \quad\big|\quad
 \text{sufficient interface}
 \quad\big|\quad
 \text{injective full digest}.}
 \tag{9.1}
$$

This display juxtaposes two proved counterexamples to overcompression with one
observed noncompressing full digest. It defines no order on representations
and makes no minimality claim for the middle interface.

The contrast between two quotients is instructive.

- The endpoint quotient is forbidden because the moved-slot relation does not
  descend through it.
- The two-prefix quotient at $\widehat X_5$ is allowed because both provenances
  induce the same typed state and all later gate semantics agree.

Thus *lossless* is always relative to the theorem observable. The goal is not
to retain every available field, nor to force a deterministic outcome, but to
retain exactly enough structure to prove an existential descent channel.

### 9.1 Audited proof-state refinements

The interface was not selected for notational convenience. Each refinement
below is forced by a declared hostile audit.

| hostile audit | failed proof object | information retained | canonical replacement |
| --- | --- | --- | --- |
| reachable rank-four failures | mass state | typed ancestry | activated checkpoint |
| activated rank-four failures | activated checkpoint | legitimate source choice | intrinsic entry section |
| tied-shortest failure | mass-endpoint quotient | source-addressed packet transport | fixed-endpoint shortest-word relation |
| full-digest over-resolution | the particular complete action-resolved digest audited here | theorem-relevant channels only | finite future-free relation menu |

Thus every enlargement of the proof state is paid for by a counterexample to
the preceding quotient. The last row has a deliberately narrower status: the
full digest is injective on the declared finite context population and hence
offers no useful compression there. It does not prove that every lossless
local encoding must be injective or uninformative.

### 9.2 Mechanisms are realizations, not interfaces

Balanced repayments, two-corridor fallbacks, bridges, heavy combs, and orbit
closures remain necessary ingredients of the finite proofs. They describe how
a selected local channel succeeds, and may vary with the local realization.
Checkpoint legitimacy and descent of the source-addressed relation instead
control whether such mechanisms can be composed without changing the proof's
meaning. The present paper therefore treats local mechanisms as realizations
inside a sufficient proof interface, not as the interface itself.

The all-rank candidate is a finite-valued section correspondence

$$
 \Sigma_r(C_r)
 =\{\mathcal C_1(C_r),\ldots,\mathcal C_m(C_r)\},
$$

constructed without future success information and satisfying

$$
 \exists j:
 \operatorname{end}(\mathcal C_j(C_r))
 \in\operatorname{Sec}_{r-1}.
 \tag{9.2}
$$

Neither a uniform bound on `m` nor an all-rank definition of
`Sec_{r-1}` is proved here.

---

## 10. Related Work and Novelty Boundary

This section separates inherited class results, adjacent proof methods, and
the fixed-scope interface claimed here. The comparison is by hypotheses,
mathematical object, and proof mechanism; shared generator format alone does
not identify the present theorem surface.

### 10.1 Circular and one-cluster automata

The automata studied here contain a letter acting as a full cycle. They
therefore lie inside the classical circular-automaton setting, for which the
Černý bound is already known by Dubuc [@dubuc1998]. The numerical reset bound is not a
novelty claim of this paper. Prime-cycle one-cluster automata were treated by
Steinberg [@steinberg2011onecluster], and Zhu's recent annular-spectral preprint
proves the Černý bound for one-cluster automata in its stated positive-level
setting [@zhu2026onecluster]. Those
works establish reset-length results by extension or linear-algebraic methods;
they do not supply the fixed-rank entry-section and source-addressed relation
interfaces proved here.

### 10.2 Defect-one actions, groups, and reachable subsets

Automata generated by permutation letters together with a rank-`n-1` merging
letter are a recognized structural and computational class. Catalano and
Jungers study randomized generation and slowly synchronizing families in this
format [@catalanoJungers2018]. Casas Torres studies complete reachability for almost group
automata with exactly one defect-one letter and a set of permutation letters
[@casasTorres2024]. Rystsov proves the Černý and rank conjectures for the narrower
Černý-type setting generated by a simple idempotent and a regular permutation
group [@rystsov2025]. Synchronizing-group and transformation-monoid methods provide a
broader algebraic setting for permutation actions combined with singular maps
[@araujoCameronSteinberg2017; @steinberg2008representation]. The present work
overlaps those sources at the alphabet and semigroup
level, but its fixed cyclic action, rooted packet ancestry, endpoint-normalized
corridors, and two-corridor accounting are additional hypotheses and proof
objects.

Complete reachability asks whether every nonempty subset is the image of the
whole state set [@bondarVolkov2016; @ferensSzykula2026]. The Ferens--Szykuła journal version gives a
quadratic decision algorithm and a quadratic reaching bound, while Zhu gives
binary counterexamples to Don's proposed reaching bound and a near-bound for
standardized automata [@ferensSzykula2026; @zhu2024don]. That theory is adjacent because it organizes
defect words and subset-image transport. We neither assume nor prove complete
reachability. Our sections choose one proof-relevant checkpoint, and the
relation menus retain only the source-addressed local channels needed for the
declared descent.

### 10.3 Extension methods and relation-valued witnesses

Subset extension and preimage growth are central tools in synchronization.
Kisielewicz and Szykuła exhibit subsets whose shortest extending words are
quadratic and explain why a naive uniformly short extension principle cannot
generally improve the cubic method [@kisielewiczSzykula2016]. This paper makes no universal
short-extension claim. Its relation-valued interface instead preserves all
tied shortest representatives when the moved-slot observable fails to descend
through the mass-endpoint quotient.

Rodaro and Venturi study a different quotient question: lifting the Černý
property from quotient automata via congruence and transition-monoid ideal
structure [@rodaroVenturi2026]. Their automaton-quotient problem is distinct from the present
proof-data question of whether a source-addressed observable descends through
a proposed information quotient.

Recent surveys record the surrounding class results and open questions about
compression, subset synchronization, and linear algebra
[@volkov2026results; @szykula2026open]. Within the
cited comparison set, we did not locate an
equivalent formulation of the combined interface

$$
 \text{intrinsic entry section}
 \quad+\quad
 \text{future-free source-addressed completion relation}.
$$

This is a bounded attribution statement, not an exhaustive novelty
certificate.

### 10.4 Overlap, disjoint scope, and claimed contribution

| comparison surface | overlap | disjoint scope | claim retained here |
| --- | --- | --- | --- |
| circular automata [@dubuc1998] | a full-cycle letter | prior reset-bound theorem is global; our results are fixed-rank interface theorems | no numerical Černý-bound novelty |
| one-cluster and linear extension [@steinberg2011onecluster; @zhu2026onecluster] | cyclic transport and subset growth | different hypotheses, carrier, and proof mechanism | entry and relation interfaces only |
| permutation plus one rank-`n-1` letter [@catalanoJungers2018; @casasTorres2024; @rystsov2025] | raw generator format | randomized, complete-reachability, or reset/rank-conjecture objectives | rooted indexed section-graph classification |
| completely reachable automata [@bondarVolkov2016; @ferensSzykula2026; @casasTorres2024; @zhu2024don] | defect words and subset images | complete reachability is neither assumed nor concluded | selected proof checkpoint and local menu |
| synchronizing groups [@araujoCameronSteinberg2017; @steinberg2008representation] | permutation action with a singular map | group-wide synchronization properties | fixed cyclic, source-addressed transport |
| extension and quotient methods [@kisielewiczSzykula2016; @rodaroVenturi2026] | short words, preimage transport, and quotient structure | no universal extension bound or automaton-quotient lifting theorem is asserted | theorem-relative preservation of tied witnesses |
| finite typed-context descent [@paper24] | descent language and relation-valued data | patch families, natural joins, and $\alpha$-acyclicity | one-context completion relation with an existential witness |

The contribution is therefore an interface architecture, not a new numerical
reset-threshold theorem:

$$
 \boxed{
 \text{state predicate}
 \longrightarrow
 \text{entry section}
 \longrightarrow
 \text{relation-valued descent interface}.}
$$

---

## 11. Evidence Status and Provenance

For the finite-symbolic equalities in Appendix B, the paper and artifacts have
different jobs:

$$
 \boxed{
 \begin{aligned}
 &\text{the paper proves the Appendix B equalities;}\\
 &\text{bound artifacts check transcription and provenance closure;}\\
 &\text{replay status is recorded separately.}
 \end{aligned}
 }
 \tag{11.1}
$$

Theorem 3.5 has a different status: executable enumeration establishes its
complete fixed-`n=6` classification, and the bound certificate records the
theorem-facing output. The release validator checks source binding and closure.
The manuscript supplies the definitions, local identities, and claim boundary
for that computer-assisted theorem.

We use three epistemic labels throughout:

| label | meaning in this paper |
| --- | --- |
| **symbolic** | a general formula or local identity is derived in the text without finite-scope machine exhaustion |
| **finite symbolic exhaustion** | a declared finite parameter set is exhausted by explicit equations and complete paper tables |
| **computer-assisted classification** | a complete fixed scope is classified by executable enumeration whose recorded output is checked against a bound source closure |

Accordingly, Theorem 3.5 is a computer-assisted fixed-scope classification;
carrier reconstruction and Theorem 7.3 use finite symbolic exhaustion; the
credit identity and the explicit closed-germ identities are symbolic. The
15,120-context statistics are computational evidence and are not theorem
premises.

The theorem-facing equalities are:

$$
\begin{aligned}
 &\mathcal X^{\rm sh}_3(321;3,I)=\varnothing,\\
 &\bigsqcup_b\operatorname{Sol}_{BT}(b)
   =\{\widehat X_1,\ldots,\widehat X_{17}\},\\
 &Q(\widehat X_i)
   =\{q\in Q^{\rm kin}(\widehat X_i):N=A=1\},\\
 &\mathcal E(Y_k)=\{\text{all displayed admissible exits}\},\\
 &\Gamma(Y_k,t)=\operatorname{eval}_t\mathcal E(Y_k).
\end{aligned}
 \tag{11.2}
$$

Counts such as 129 complete representatives, 184 canonically serialized Type-II
receipts, or relation-cover statistics are discovery diagnostics. They do not
replace the equalities in (11.2) and are not required by the public release
closure.

---

## 12. Open Problems

The present work leaves the following questions open.

1. Determine whether relation-menu size admits a useful all-`n` bound.
2. Find an intermediate representation that is lossless for the required
   observable without becoming injective on the full context space.
3. Characterize the class of theorem observables for which a source-addressed
   local relation admits a noninjective sufficient quotient.

Mechanism taxonomy, parameterized repayment families, credit accounting, and
future-free return between sections remain outside the present theorem spine.
In particular, no `n=8`,
Forced FFS, B2-generalization, or all-rank mechanism result is part of Paper
XXVII.

Any enlargement of the present interface requires an additional typed state,
an admitted return hidden by a third gate, an omitted strict exit, another
failed quotient, or a performed replay that changes a theorem-facing relation.

---

## 13. Conclusion

The two fixed-rank analyses answer successive proof-interface questions:

$$
 \boxed{
 \begin{aligned}
 n=6&\text{ chooses a legitimate checkpoint;}\\
 n=7&\text{ determines the relation structure it must retain}.
 \end{aligned}}
$$

At `n=6`, the correct object is an intrinsic entry section rather than a
universal rank-four predicate. At `n=7`, the correct local object is a
source-addressed, relation-valued completion interface rather than one chosen
shortest representative or the particular injective full digest audited here.
The resulting finite proofs separate theorem-facing equalities from bound
computational evidence and provenance records.

Mechanism classification remains outside the present theorem spine.

These conclusions do not supply an all-rank section, a uniform bound on menu
size, Forced FFS, General FFS, or a new proof of the Černý conjecture. Their
role is narrower: they identify and verify a proof architecture on the two
finite scopes studied here, where checkpoint choice and inherited relation
structure can be observed together.

---

## Appendix A: Claim Status

| claim | status |
| --- | --- |
| mass/corridor/two-corridor accounting | exact framework input |
| fixed-`n=6` rooted scope and section classification | computer-assisted classification |
| fixed-`n=6` `1700+4` indexed section-graph theorem | computer-assisted classification |
| extremal `n=7` carrier reconstruction | symbolic formulas plus finite parameterization |
| five-cell canonical elimination | finite symbolic exhaustion, closed at declared scope |
| Theorem 7.3 (Low-Transport) | finite symbolic consequence of the closed elimination |
| identity boundary and 27-credit closure | symbolic finite completion |
| all-`n` bounded relation menu | open |
| Forced FFS / General FFS | open |
| Černý conjecture | not claimed |

---

## Appendix B: Complete Five-Cell Elimination

This appendix records the complete theorem-facing finite equalities used in
Section 6. It is included for human auditability. The bound artifacts check
their transcription and provenance closure; any producer replay is recorded
separately and is not assumed here. The artifacts are not premises for the
completeness claims.

### B.1 Empty Shallow Cell

The fifth negative parameter cell is separate. Here the post-tag relation is
explicitly the **shallow** relation

$$
 \mathcal X_j^{\rm sh}(C)
 =\{\widehat X:\widehat X\text{ arises from a role-compatible marked }
 C_4\text{ association with }r\in\{0,1\}\}.
$$

No landing test occurs in this definition. The claim to prove is

$$
 \boxed{\mathcal X_3^{\rm sh}(321;h=3,\beta=I)=\varnothing.}
 \tag{Empty-X}
$$

Carrier reconstruction gives

$$
 d=(0,3,2,1,4,5,0),
 \qquad
 (F_4,s,D_1,D_2)=(0,1,2,4),
$$

and the marked moved edge is $3\to1$. Put $H=F_4+D_2$ after the first
heavy-comb fusion. For corridor lengths $\ell_1,\ell_2$, the two surpluses are

$$
 S_1=7-\ell_1,
 \qquad
 S_2=13-\ell_2.
$$

Thus a Type-II heavy comb requires

$$
 \ell_1\ge8,
 \qquad
 \ell_1+\ell_2\le20.                            \tag{EX-A}
$$

The finite back-solving used below is entirely local. Reverse rotation is
unique, and the inverse fibres of the defect are

$$
 d^{-1}(0)=\{0,6\},\quad d^{-1}(1)=\{3\},\quad
 d^{-1}(3)=\{1\},\quad d^{-1}(i)=\{i\} (i=2,4,5).
 \tag{EX-B}
$$

Starting from the prescribed terminal fusion roles, iterate `(EX-B)` through
rank-preserving predecessors. Mark a predecessor exactly when the incoming
mass-two packet occupies coordinate `3`, and retain only marks with at most
one later nonterminal `d`. Endpoint nonminimal branches and branches violating
`(EX-A)` are discarded. This gives the following two exhaustive calculations.

#### A first-corridor mark cannot be repaid

Solving the first-corridor equations for both choices of incoming mass-two
packet leaves exactly the five marked words below. Digits use $0=p,1=d$; the
bracketed `1` is the marked occurrence. Every surviving row fuses `F4` with
`D2`.

| id | marked first word | $r$ | rank-three endpoint |
| --- | --- | ---: | --- |
| `F1` | `000101[1]01000001` | 1 | `0:H,3:D1,5:s` |
| `F2` | `1000000[1]0100001` | 1 | `0:H,3:D1,5:s` |
| `F3` | `10000010[1]0100001` | 1 | `0:H,2:s,3:D1` |
| `F4` | `1000000[1]0000001` | 0 | `0:H,2:D1,3:s` |
| `F5` | `000101[1]000001` | 0 | `0:H,1:s,5:D1` |

Their accounting data are:

| id | $\ell_1$ | minimum possible $\ell_2$ | total | exclusion |
| --- | ---: | ---: | ---: | --- |
| `F1` | 15 | 6 | 21 | $A$ |
| `F2` | 15 | 6 | 21 | $A$ |
| `F3` | 16 | 6 | 22 | $A$ |
| `F4` | 15 | 12 | 27 | $A$ |
| `F5` | 13 | 8 | 21 | $A$ |

The minimum possible $\ell_2$ is the shortest strict second exit fusing $H$
with $D_1$, over all exact rank-two endpoints. Consequently every row violates
$\ell_1+\ell_2\le20$; no first-corridor mark defines a member of
$\mathcal X_3^{\rm sh}$.

#### A second-corridor mark is nonminimal

The same back-solving without a mark gives exactly five first corridors that
can satisfy the repayment bound:

| id | complete first word | rank-three source $Z$ | $\ell_1$ | maximum $\ell_2$ |
| --- | --- | --- | ---: | ---: |
| `Z1` | `000010001` | `0:H,1:D1,3:s` | 9 | 11 |
| `Z2` | `0000101001` | `0:H,2:s,5:D1` | 10 | 10 |
| `Z3` | `00001011001` | `0:H,1:D1,2:s` | 11 | 9 |
| `Z4` | `00010000001` | `0:H,1:s,4:D1` | 11 | 9 |
| `Z5` | `00010100001` | `0:H,2:s,4:D1` | 11 | 9 |

For a final singleton coordinate `t`, let

$$
 L_{\rm sh}(Z,t)
$$

be the minimum length, within the displayed repayment bound, of a strict
$H+D_1$ exit containing a shallow marked $3\to1$ edge. Let
$L_{\min}(Z,t)$ be the unrestricted fixed-endpoint minimum. Solving the labelled
pair-exit equations gives all finite shallow values:

| source | `t : L_sh(Z,t) > L_min(Z,t)` |
| --- | --- |
| `Z1` | `1: 9>8`, `2: 9>7`, `3: 9>7`, `5: 10>7` |
| `Z2` | `5: 10>8` |
| `Z3` | `2: 9>8`, `3: 9>7`, `5: 9>7` |
| `Z4` | none |
| `Z5` | none |

Every omitted coordinate has no shallow marked solution within the repayment
bound. Every displayed solution is strictly longer than another word to the
same mass endpoint, so fixed-endpoint normalization rejects it. This proves
`(Empty-X)` before any return or rank-three continuation calculation.

The superscript `sh` is essential. The full tagged relation is not empty:
from $Z_1$, the endpoint-shortest word `00[1]01100001` contains the marked edge
and has two later rank-preserving $d$ letters $(r=2)$. It is outside the
canonical direct/one-return menu and is retained as a hostile control against
the stronger, false untyped claim.

### B.2 Back-Solving Exhaustion

An accounting triple is $(S_{\rm in},k,b)$: surplus entering the marked corridor,
marked-prefix length, and running balance after the tagged occurrence.

The four nonempty carrier inputs, derived from Lemma 5.1 and (K), are:

| cell | rooted defect | rank-four source | marked edge |
| --- | --- | --- | --- |
| `132/2,(3,I)` | `0132450` | `0:F4,3:D1,4:s,5:D2` | `2 -> 3` |
| `213/2,(3,I)` | `0213450` | `0:F4,1:D1,3:D2,5:s` | `2 -> 1` |
| `213/2,(3,S)` | `0213540` | `0:F4,1:D1,3:D2,4:s` | `2 -> 1` |
| `213/2,(4,I)` | `0214350` | `0:F4,1:D1,4:D2,5:s` | `2 -> 1` |

For a corridor source `Z`, incoming role `R`, and moved slot `j`, a
back-solving solution is a marked prefix `u=u' d` such that:

1. every `d` in `u` is rank-preserving;
2. `R` occupies `lambda(j)` immediately before the final, marked `d` in `u`;
3. the resulting post-tag state admits a direct or one-return suffix of the
   prescribed fusion corridor;
4. the full corridor is shortest for its exact mass endpoint and satisfies
   the two-corridor accounting gate.

For corridor one, `Z` is the displayed rank-four source. For corridor two,
`Z` ranges over the rank-three endpoints of admissible first corridors. The
inverse step is explicit:

$$
 p^{-1}(i)=i-1\pmod 7,
 \qquad
 d^{-1}(0)=\{0,6\},
 \qquad
 d^{-1}(i)=\{\pi^{-1}(i)\}\quad(i\ne0).
 \tag{BT-inverse}
$$

Back-solving the terminal roles with `(BT-inverse)` and discarding a branch at
its first `E`, `R`, `N`, or `A` violation is a finite inverse recurrence.  More
explicitly, for each cell `b`, corridor `c`, and incoming role `R`, start from
the two prescribed terminal fusion parents.  Reverse rotations uniquely.
Whenever a reversed `d`-edge has image zero, branch over the two preimages
`{0,6}`; every other nonzero coordinate has a unique predecessor.  Stop a
branch when it reaches the marked equation

$$
 R@\lambda(j)\xrightarrow d R@\alpha(j),       \tag{BT-mark}
$$

or at its first `E/R/N/A` violation.  Fixed-endpoint distance and the remaining
debt budget bound the marked-prefix depth.  Subtracting the shortest admissible
post-tag suffix from those bounds gives the channel caps in the next table.

> **Inverse-Tree Termination and Completeness Lemma.** For every declared cell
> and channel, the recurrence above terminates and enumerates every admissible
> marked prefix within its stated depth cap. Reverse rotations are unique;
> under `d^{-1}` a nonzero image has one predecessor and the collision image
> zero has exactly the two predecessors `{0,6}`. Hence each reverse level lists
> the full predecessor set. The fixed-endpoint and remaining-accounting bounds
> give the finite depth cap. Moreover, an `E/R/N/A` exclusion is permanent
> under further reverse extension: an early fusion cannot be undone, a role
> violation contradicts the prescribed labelled trace, a shorter word to the
> fixed endpoint remains shorter, and added prefix length cannot repair an
> exceeded debt/length bound. Induction on reverse depth therefore proves both
> termination and exhaustion; no unlisted admissible leaf exists.

> **Back-Solving Exhaustion Lemma.** The inverse recurrence above has exactly
> the source-addressed surviving leaves displayed below.  Every other inverse
> leaf ends at its first `E`, `R`, `N`, or `A` exclusion.  A repeated word in
> two rows denotes two different labelled corridor sources, not a quotient.

| cell | `c/role` | cap | surviving prefixes |
| --- | --- | ---: | --- |
| `132/2,(3,I)` | `2/D1` | 3 | `011 -> X1` |
| `132/2,(3,I)` | `1/D2` | 5 | `00001 -> X2` |
| `132/2,(3,I)` | `2/D2` | 6 | `00001 -> X3`; `00001 -> X4`; `000101 -> X5`; `101001 -> X5`; `010101 -> X6` |
| `213/2,(3,I)` | `1/D1` | 2 | `01 -> X8` |
| `213/2,(3,I)` | `2/D2` | 2 | `1 -> X7`; `01 -> X9` |
| `213/2,(3,S)` | `2/D2` | 2 | `01 -> X10` |
| `213/2,(4,I)` | `1/D1` | 4 | `01 -> X13`; `0101 -> X17` |
| `213/2,(4,I)` | `2/D1` | 3 | `1 -> X11`; `1 -> X12`; `01 -> X15`; `101 -> X16` |
| `213/2,(4,I)` | `2/D2` | 2 | `01 -> X14` |

All omitted `c/role` combinations have empty survivor sets under the same
recurrence.  The cellwise checksum is

$$
 (7\to6)+(3\to3)+(1\to1)+(7\to7)=18\to17,     \tag{BT-count}
$$

where only `X5` identifies two leaves.  That identification is legal because
the two prefixes induce the same typed post-tag placement and the same full
normalization/accounting gate semantics.  In contrast, no mass-endpoint
quotient is used here.

Expanding the 17 typed leaves gives the following prefix-solution table. The
prefix set is part of the equality: two prefixes may be identified only when
they induce the same displayed typed state and the same
normalization/accounting semantics.

The state identities and prefix data are:

| id | negative cell | `c/role` | marked-prefix set | `k` |
| --- | --- | --- | --- | ---: |
| `X1` | `132/2,(3,I)` | `2/D1` | `{011}` | 3 |
| `X2` | `132/2,(3,I)` | `1/D2` | `{00001}` | 5 |
| `X3` | `132/2,(3,I)` | `2/D2` | `{00001}` | 5 |
| `X4` | `132/2,(3,I)` | `2/D2` | `{00001}` | 5 |
| `X5` | `132/2,(3,I)` | `2/D2` | `{000101,101001}` | 6 |
| `X6` | `132/2,(3,I)` | `2/D2` | `{010101}` | 6 |
| `X7` | `213/2,(3,I)` | `2/D2` | `{1}` | 1 |
| `X8` | `213/2,(3,I)` | `1/D1` | `{01}` | 2 |
| `X9` | `213/2,(3,I)` | `2/D2` | `{01}` | 2 |
| `X10` | `213/2,(3,S)` | `2/D2` | `{01}` | 2 |
| `X11` | `213/2,(4,I)` | `2/D1` | `{1}` | 1 |
| `X12` | `213/2,(4,I)` | `2/D1` | `{1}` | 1 |
| `X13` | `213/2,(4,I)` | `1/D1` | `{01}` | 2 |
| `X14` | `213/2,(4,I)` | `2/D2` | `{01}` | 2 |
| `X15` | `213/2,(4,I)` | `2/D1` | `{01}` | 2 |
| `X16` | `213/2,(4,I)` | `2/D1` | `{101}` | 3 |
| `X17` | `213/2,(4,I)` | `1/D1` | `{0101}` | 4 |

The corresponding typed payloads are:

| id | post-tag placement | accounting | corridor source |
| --- | --- | --- | --- |
| `X1` | `0:s,1:D2+F4,3:D1` | `(-3,3,-6)` | `0:D2+F4,2:D1,5:s` |
| `X2` | `0:D1,1:s,3:D2,4:F4` | `(0,5,-5)` | `0:F4,3:D1,4:s,5:D2` |
| `X3` | `0:s,3:D2,4:D1+F4` | `(-2,5,-7)` | `0:D1+F4,2:s,5:D2` |
| `X4` | `1:s,3:D2,4:D1+F4` | `(-3,5,-8)` | `0:D1+F4,4:s,5:D2` |
| `X5` | `0:s,2:D1+F4,3:D2` | `(-2,6,-8)` | `0:D1+F4,2:s,5:D2` |
| `X6` | `2:s,3:D2,4:D1+F4` | `(-2,6,-8)` | `0:D1+F4,2:s,5:D2` |
| `X7` | `0:D1+F4,1:D2,4:s` | `(-1,1,-2)` | `0:D1+F4,2:D2,4:s` |
| `X8` | `0:s,1:D1,2:F4,4:D2` | `(0,2,-2)` | `0:F4,1:D1,3:D2,5:s` |
| `X9` | `0:s,1:D2,2:D1+F4` | `(-1,2,-3)` | `0:D1+F4,1:D2,5:s` |
| `X10` | `0:s,1:D2,2:D1+F4` | `(-1,2,-3)` | `0:D1+F4,1:D2,5:s` |
| `X11` | `0:D2+F4,1:D1,4:s` | `(-1,1,-2)` | `0:D2+F4,2:D1,3:s` |
| `X12` | `0:D2+F4,1:D1,5:s` | `(-2,1,-3)` | `0:D2+F4,2:D1,5:s` |
| `X13` | `0:s,1:D1,2:F4,5:D2` | `(0,2,-2)` | `0:F4,1:D1,4:D2,5:s` |
| `X14` | `1:D2,2:D1+F4,3:s` | `(-1,2,-3)` | `0:D1+F4,1:D2,3:s` |
| `X15` | `0:s,1:D1,2:D2+F4` | `(-3,2,-5)` | `0:D2+F4,1:D1,5:s` |
| `X16` | `0:s,1:D1,2:D2+F4` | `(-2,3,-5)` | `0:D2+F4,2:D1,5:s` |
| `X17` | `0:D2,1:D1,2:s,4:F4` | `(0,4,-4)` | `0:F4,1:D1,4:D2,5:s` |

Let

$$
 \mathfrak B_{\ne\varnothing}
 =\{132/2,(3,I);\ 213/2,(3,I);\ 213/2,(3,S);\ 213/2,(4,I)\}.
$$

The theorem-facing equality is the disjoint-union statement

$$
 \bigsqcup_{b\in\mathfrak B_{\ne\varnothing}}
 \operatorname{Sol}_{\rm BT}(b)
 =\{\widehat X_1,\ldots,\widehat X_{17}\}
$$

over the four nonempty negative cells, together with `(Empty-X)` for the fifth.
There are 18 marked-prefix solutions because `X5` has two tied provenances,
but exactly 17 typed states. No landing value is used in this elimination.

### B.3 Return Admission

For each $q\in Q^{\rm kin}(\widehat X)$, let $A_q(\widehat X)$ be the uniquely determined shallow
candidate obtained after terminal-rotation elimination. Define

$$
 \mathsf N(\widehat X,q)=1
 \iff A_q(\widehat X)\text{ has fixed-endpoint minimum length},
$$

and

$$
 \mathsf A(\widehat X,q)=1
 \iff A_q(\widehat X)\text{ satisfies the applicable corridor balance and
 debt bound}.
$$

Rank preservation and the prescribed packet roles are already part of
$Q^{\rm kin}$. The admitted relation is therefore

$$
 Q(\widehat X)=
 \{q\in Q^{\rm kin}(\widehat X):
   \mathsf N(\widehat X,q)=\mathsf A(\widehat X,q)=1\}.       \tag{Admission}
$$

If the marked prefix has length `k`, a one-return suffix has the forced form

$$
 p^q d\,p^{a_q}d,
 \qquad
 L_q=k+q+a_q+2,                              \tag{RA-word}
$$

where adjacency uniquely determines `a_q`.  A direct suffix has the form
$p^{a_D}d$ and length $L_D=k+a_D+1$. Write $L_*$ for the shortest length to
the same exact mass endpoint.  Then

$$
 \mathsf N=1\iff L=L_*.
$$

For a second-corridor candidate, its surplus is $S_2=13-L$; the typed state
supplies $S_{\rm in}<0$, and

$$
 \mathsf A=1\iff S_{\rm in}+S_2\ge0.          \tag{RA-2}
$$

For a first-corridor candidate, $S_1=7-L<0$. Its accounting entry below is
`S1; r/m`, where $m$ is the number of role-compatible normalized second
corridors and $r$ is the number that repay $-S_1$; here

$$
 \mathsf A=1\iff r>0.                          \tag{RA-1}
$$

Mass endpoints are displayed as seven-coordinate strings. The following is
the complete one-return elimination. In the accounting column, an expression
$x+y=z$ means $S_{\rm in}+S_2=S_{\rm total}$. The decision column encodes the
two gates: `in Q` or `direct` means $(N,A)=(1,1)$, `N` means $(0,1)$, `A`
means $(1,0)$, and `N+A` means $(0,0)$.

| `X` | `c` | `q` | `a_q` | endpoint | `L/L_*` | accounting | decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `X1` | 2 | 0 | 5 | `6000010` | 10/8 | `-3+3=0` | `N` |
| `X1` | 2 | 1 | 3 | `6000100` | 9/9 | `-3+4=1` | `in Q` |
| `X1` | 2 | 5 | 6 | `6000100` | 16/9 | `-3-3=-6` | `N+A` |
| `X2` | 1 | 1 | 2 | `4020010` | 10/10 | `S1=-3; 4/12` | `in Q` |
| `X2` | 1 | 4 | 6 | `4020100` | 17/9 | `S1=-10; 0/8` | `N+A` |
| `X3` | 2 | 1 | 2 | `6010000` | 10/9 | `-2+3=1` | `N` |
| `X3` | 2 | 4 | 6 | `6010000` | 17/9 | `-2-4=-6` | `N+A` |
| `X3` | 2 | 6 | 4 | `6000100` | 17/11 | `-2-4=-6` | `N+A` |
| `X4` | 2 | 1 | 2 | `6000010` | 10/10 | `-3+3=0` | `in Q` |
| `X4` | 2 | 4 | 6 | `6000100` | 17/9 | `-3-4=-7` | `N+A` |
| `X4` | 2 | 6 | 4 | `6000100` | 17/9 | `-3-4=-7` | `N+A` |
| `X5` | 2 | 0 | 4 | `6000100` | 12/11 | `-2+1=-1` | `N+A` |
| `X5` | 2 | 2 | 2 | `6000010` | 12/10 | `-2+1=-1` | `N+A` |
| `X5` | 2 | 5 | 6 | `6000100` | 19/11 | `-2-6=-8` | `N+A` |
| `X6` | 2 | 1 | 2 | `6000100` | 11/11 | `-2+2=0` | `in Q` |
| `X6` | 2 | 6 | 4 | `6000010` | 18/10 | `-2-5=-7` | `N+A` |
| `X7` | 2 | 1 | 5 | `6001000` | 9/8 | `-1+4=3` | `N` |
| `X7` | 2 | 3 | 3 | `6001000` | 9/8 | `-1+4=3` | `N` |
| `X7` | 2 | 4 | 2 | `6000100` | 9/9 | `-1+4=3` | `in Q` |
| `X8` | 1 | 0 | 5 | `4200010` | 9/8 | `S1=-2; 4/9` | `N` |
| `X8` | 1 | 2 | 3 | `4002100` | 9/9 | `S1=-2; 0/7` | `A` |
| `X8` | 1 | 3 | 2 | `4200010` | 9/8 | `S1=-2; 4/9` | `N` |
| `X9` | 2 | 0 | 5 | `6000010` | 9/8 | `-1+4=3` | `N` |
| `X9` | 2 | 2 | 3 | `6000100` | 9/7 | `-1+4=3` | `N` |
| `X9` | 2 | 3 | 2 | `6000010` | 9/8 | `-1+4=3` | `N` |
| `X10` | 2 | 0 | 5 | `6000100` | 9/8 | `-1+4=3` | `N` |
| `X10` | 2 | 3 | 2 | `6000100` | 9/8 | `-1+4=3` | `N` |
| `X11` | 2 | 1 | 5 | `6000100` | 9/8 | `-1+4=3` | `N` |
| `X11` | 2 | 3 | 3 | `6000100` | 9/8 | `-1+4=3` | `N` |
| `X12` | 2 | 1 | 5 | `6000010` | 9/9 | `-2+4=2` | `in Q` |
| `X12` | 2 | 3 | 3 | `6000010` | 9/9 | `-2+4=2` | `in Q` |
| `X13` | 1 | 0 | 5 | `4000210` | 9/8 | `S1=-2; 2/6` | `N` |
| `X13` | 1 | 2 | 3 | `4001200` | 9/7 | `S1=-2; 7/10` | `N` |
| `X14` | 2 | 0 | 5 | `6100000` | 9/7 | `-1+4=3` | `N` |
| `X14` | 2 | 2 | 3 | `6010000` | 9/8 | `-1+4=3` | `N` |
| `X15` | 2 | 0 | 5 | `6000010` | 9/8 | `-3+4=1` | `N` |
| `X15` | 2 | 2 | 3 | `6001000` | 9/7 | `-3+4=1` | `N` |
| `X16` | 2 | 0 | 5 | `6000010` | 10/9 | `-2+3=1` | `N` |
| `X16` | 2 | 2 | 3 | `6001000` | 10/7 | `-2+3=1` | `N` |
| `X17` | 1 | 0 | 4 | `4002010` | 10/10 | `S1=-3; 2/6` | `in Q` |

The direct candidates are exhausted by the same formulas with no return
exponent:

| `X` | `c` | `a_D` | endpoint | `L/L_*` | accounting | decision |
| --- | --- | --- | --- | --- | --- | --- |
| `X2` | 1 | 3 | `4020100` | 9/9 | `S1=-2; 3/8` | direct |
| `X3` | 2 | 3 | `6010000` | 9/9 | `-2+4=2` | direct |
| `X4` | 2 | 3 | `6000100` | 9/9 | `-3+4=1` | direct |
| `X5` | 2 | 4 | `6000100` | 11/11 | `-2+2=0` | direct |
| `X6` | 2 | 3 | `6000010` | 10/10 | `-2+3=1` | direct |
| `X7` | 2 | 6 | `6001000` | 8/8 | `-1+5=4` | direct |
| `X8` | 1 | 5 | `4200010` | 8/8 | `S1=-1; 4/9` | direct |
| `X9` | 2 | 5 | `6000010` | 8/8 | `-1+5=4` | direct |
| `X10` | 2 | 5 | `6000100` | 8/8 | `-1+5=4` | direct |
| `X11` | 2 | 6 | `6000100` | 8/8 | `-1+5=4` | direct |
| `X12` | 2 | 6 | `6001000` | 8/7 | `-2+5=3` | `N` |
| `X13` | 1 | 5 | `4000210` | 8/8 | `S1=-1; 4/6` | direct |
| `X14` | 2 | 5 | `6010000` | 8/8 | `-1+5=4` | direct |
| `X15` | 2 | 5 | `6000010` | 8/8 | `-3+5=2` | direct |
| `X16` | 2 | 5 | `6000010` | 9/9 | `-2+4=2` | direct |

Thus the rowwise equality `(Admission)` gives

| id | `Q^kin(X)` | admitted `Q(X)` | direct |
| --- | --- | --- | --- |
| `X1` | `{0,1,5}` | `{1}` | none |
| `X2` | `{1,4}` | `{1}` | admitted |
| `X3` | `{1,4,6}` | empty | admitted |
| `X4` | `{1,4,6}` | `{1}` | admitted |
| `X5` | `{0,2,5}` | empty | admitted |
| `X6` | `{1,6}` | `{1}` | admitted |
| `X7` | `{1,3,4}` | `{4}` | admitted |
| `X8` | `{0,2,3}` | empty | admitted |
| `X9` | `{0,2,3}` | empty | admitted |
| `X10` | `{0,3}` | empty | admitted |
| `X11` | `{1,3}` | empty | admitted |
| `X12` | `{1,3}` | `{1,3}` | rejected by `N` |
| `X13` | `{0,2}` | empty | admitted |
| `X14` | `{0,2}` | empty | admitted |
| `X15` | `{0,2}` | empty | admitted |
| `X16` | `{0,2}` | empty | admitted |
| `X17` | `{0}` | `{0}` | none |

Summing the rows gives

$$
 40=8_{\rm admitted}+21_{N}+1_A+10_{N+A},       \tag{Q-count}
$$

and the direct candidates give

$$
 15=14_{\rm admitted}+1_N.                      \tag{D-count}
$$

No return candidate passes both $N$ and $A$ while remaining outside $Q(\widehat X)$.
No direct candidate passes its declared gate while remaining outside the
direct relation. Thus endpoint normalization and accounting are the complete
admission interface **on this five-cell surface**. This statement is not
promoted to other ranks or ambient sizes.

### B.4 Heavy-Pair Exit Exhaustion

For a typed rank-three state `Y`, define

$$
 \mathcal E(Y)=\{w:w\text{ is an admissible endpoint-normalized strict
 heavy-pair exit from }Y\},
$$

and

$$
 \Gamma(Y,t)=\{w(t):w\in\mathcal E(Y)\}.        \tag{Gamma-image}
$$

Words use $0=p,1=d$ and act left to right. Completeness is obtained before
the singleton is evaluated. On the finite rank-three mass graph, let
$\delta_Y(M)$ be the shortest rank-preserving distance from the mass placement
of $Y$ to $M$. Retain a parent edge $M\xrightarrow{a}M'$ exactly when

$$
 \delta_Y(M)+1=\delta_Y(M'),                    \tag{Exit-DAG}
$$

and retain a strict terminal edge to `Z` exactly at the minimum distance to
that exact endpoint `Z`.  Backtracking this shortest-parent DAG gives every
tied endpoint-shortest exit word.  A terminal parent-role check then selects
the exits fusing the two heavy packet identities.  Finally, the displayed
debt bound discards the overlength exits.  No singleton landing is read in
any of these three operations.

The resulting equalities are below. An accepted entry records
$(\text{word},\text{length},\text{target},t,S_2)$; its last two fields are
obtained only by passive evaluation. The over-debt relation lists every other
endpoint-shortest exit that fuses the correct heavy pair, together with its
length and target.

The admitted relation and its passive images are:

| id | defect / typed `Y` | debt / max `ell_2` | complete `E(Y)` | `Gamma(Y,t)` |
| --- | --- | --- | --- | --- |
| `Y1` | `0132450`; `0:D2+F4,2:D1,4:s` | `2 / 11` | `0010001 [7,6010000,2,6]`; `010100001 [9,6000100,4,4]`; `0101001001 [10,6000010,5,3]` | `{2,4,5}` |
| `Y2` | `0132450`; `0:D2+F4,2:D1,5:s` | `3 / 10` | `0010001 [7,6010000,2,6]`; `010001001 [9,6000100,4,4]`; `011010001 [9,6000100,4,4]`; `01000001 [8,6000010,5,5]` | `{2,4,5}` |
| `Y3` | `0213450`; `0:D1+F4,1:D2,5:s` | `1 / 12` | `00001001 [8,6001000,3,5]`; `0000001 [7,6000100,4,6]`; `00010001 [8,6000010,5,5]`; `01000001 [8,6000010,5,5]` | `{3,4,5}` |
| `Y4` | `0214350`; `0:D1+F4,4:D2,5:s` | `1 / 12` | `011000100001 [12,6010000,2,1]`; `011010000001 [12,6010000,2,1]`; `10100001 [8,6001000,3,5]`; `101010001 [9,6000010,5,4]` | `{2,3,5}` |
| `Y5` | `0214350`; `0:D1+F4,3:D2,5:s` | `3 / 10` | `0100001 [7,6001000,3,6]`; `01010001 [8,6000010,5,5]` | `{3,5}` |

For the checksum below, write

$$
 (a,o,w)=(\text{admitted},\text{over-debt},\text{wrong-pair}).
$$

The rejected correct-pair exits and complete endpoint-shortest checksums are:

| id | split $(a,o,w)$ |
| --- | --- |
| $Y_1$ | $(3,5,16)$ |
| $Y_2$ | $(4,8,13)$ |
| $Y_3$ | $(4,5,15)$ |
| $Y_4$ | $(4,2,17)$ |
| $Y_5$ | $(2,4,16)$ |

The complete over-debt relation is:

| id | word | length | endpoint |
| --- | --- | ---: | --- |
| $Y_1$ | `00000010000001` | 14 | `6100000` |
| $Y_1$ | `000000100001001` | 15 | `6001000` |
| $Y_1$ | `000000110000001` | 15 | `6001000` |
| $Y_1$ | `00010101000001` | 14 | `6100000` |
| $Y_1$ | `000101010001001` | 15 | `6001000` |
| $Y_2$ | `0001010010001` | 13 | `6100000` |
| $Y_2$ | `00010100101001` | 14 | `6001000` |
| $Y_2$ | `00010101000001` | 14 | `6001000` |
| $Y_2$ | `1000101000001` | 13 | `6100000` |
| $Y_2$ | `10001010001001` | 14 | `6001000` |
| $Y_2$ | `1010010010001` | 13 | `6100000` |
| $Y_2$ | `10100100101001` | 14 | `6001000` |
| $Y_2$ | `10100101000001` | 14 | `6001000` |
| $Y_3$ | `000001010100001` | 15 | `6100000` |
| $Y_3$ | `0000101000100001` | 16 | `6010000` |
| $Y_3$ | `100000010100001` | 15 | `6100000` |
| $Y_3$ | `100101010000001` | 15 | `6100000` |
| $Y_3$ | `1001010110100001` | 16 | `6010000` |
| $Y_4$ | `0110101000001` | 13 | `6100000` |
| $Y_4$ | `0110110101001` | 13 | `6000100` |
| $Y_5$ | `001000100001` | 12 | `6010000` |
| $Y_5$ | `001010000001` | 12 | `6010000` |
| $Y_5$ | `0010101000001` | 13 | `6100000` |
| $Y_5$ | `0010110101001` | 13 | `6000100` |

Thus each row proves a word-set equality, not merely the existence of enough
witnesses.  Across the five rows the complete rank-three relation contains
17 admitted heavy-pair exits, 24 correct-pair exits rejected only by the debt
bound, and 77 tied endpoint-shortest exits rejected by the terminal packet
roles.  The singleton images in `Gamma` are derived images of the admitted
word sets.

### B.5 Derived Negative Spectra

Composing the first-corridor images with `Gamma` and adjoining the local
second-corridor images gives:

| cell | direct spectrum | one-return spectrum |
| --- | --- | --- |
| `132/2,(3,I)` | `{2,4,5}` | `{2,4,5}` |
| `213/2,(3,I)` | `{3,4,5}` | `{4}` |
| `213/2,(3,S)` | `{4}` | empty |
| `213/2,(4,I)` | `{2,3,4,5}` | `{3,5}` |
| `321/3,(3,I)` | empty by `(Empty-X)` | empty by `(Empty-X)` |

No displayed spectrum contains offset one. This final table is a set-image
calculation; all universal work is confined to Back-Solving, Return Admission,
and Heavy-Pair Exit Exhaustion above.

---

## Appendix C: Computational Artifacts

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite) under
`experiments/paper27/`; short paths are relative to that directory.

| artifact surface | role | short path |
| --- | --- | --- |
| theorem-facing records | fixed-scope classifications and symbolic tables | `results/` |
| producers | entry-section, relation, return, and exit enumeration | `*.py` |
| validators | formula checks, source binding, and closure checks | `validation/` |
| release manifest | ordered exact-byte closure and closure-class policy | `release-manifest.json` |
| validation receipt | local closure verification, excluded from its own closure | `results/*validation-receipt.json` |

The release identity contains only the canonical manuscript and theorem-facing
closure. Package-only, historical, and receipt artifacts do not alter theorem
identity.

The receipt records local closure verification, not independent mathematical
validation. Replay flags state which producers were re-executed for that
receipt; a bound artifact digest does not by itself establish theorem truth.
