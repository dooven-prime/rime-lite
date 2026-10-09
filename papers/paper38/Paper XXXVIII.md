# Exact Return Layers and Budgeted Survivor Frontiers
### Source-Relative Return Counts in Full Ordinary-Lane Dynamics

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXVIII | Version 1.0**

*This paper is Paper XXXVIII of the RIME program. It studies source-labelled
raw first-exit incidence, charging each normalized return including the
terminal occurrence. It makes no typed-transfer, recursive-settlement, or
reset-bound claim.*

## Abstract

**Problem.** An unbudgeted lineage group determines which terminal
placements are reachable, but need not determine their return-count layers.

**Approach.** We study five source lineages filling an ordinary lane in
normalized circular dynamics with $n=5g$, $\Delta=g$, and $g\ge2$, allowing
arbitrary lane-stabilizing branch restrictions and every return label.
Each normalized return, including the terminal one, has unit cost.

**Results.** For $N\ge1$, an exact correspondence with actual guarded paths gives
$\Theta_{=N}=\mathcal A_a^{N-1}B_s$ and
$\Theta_N=\bigcup_{\ell=0}^{N-1}\mathcal A_a^\ell B_s$, where
$B_s=H\sigma_s$ is the forced source factor. Each product is realized
without uncharged phase alignment or representative replacement.
Cumulative layers cannot stall before covering $K_a$, so every
attainable terminal placement and survivor map has a witness using at
most $|K_a|/5\le24$ returns. An all-$g\ge3$ matched family has the
same group, aggregate factor set, and complete unbudgeted frontier
but different one-return survivor maps of equal cardinality; both
frontiers coincide at two returns.

**Boundary.** The full-lane source is supplied, not asserted to be the complete
current image reached from the initial $Q$. First exits and budgets are
relative to these five lineages. The original-letter consequence requires a supplied
normalization realization and excludes source-entry cost. No sharp constant,
minimal invariant, or deterministic coset transition congruence is claimed.

**Keywords.** circular automata; guarded returns; source-relative budgets;
positive product layers; survivor incidence

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q,E,\Delta$ | circular carrier, normalized carrier, and lane spacing |
| $C_j,C_\ast$ | ordinary five-point lanes and punctured four-point lane |
| $\lambda_{j,\kappa}$ | actual placement of the five source labels |
| $s$ | fixed ordinary source lane |
| $\pi,\sigma_j$ | lane permutation and within-lane branch restrictions |
| $c,H=\langle c\rangle$ | five-position phase cycle and phase subgroup |
| $K_a$ | generated five-position lineage group |
| $\mathcal A_a=\bigcup_jH\sigma_j$ | aggregate factor set |
| $B_s=H\sigma_s$ | forced initial right coset |
| $\Theta_{=N},\Theta_N$ | exact and at-most terminal return-count layers |
| $\mu_\eta$ | pre-collapse terminal placement of one permutation |
| $\mathfrak S_a^{\le N}(\lambda_0;F)$ | source-addressed survivor maps within budget |

## Introduction

Closure and bounded reachability read different information. In the full
ordinary-lane setting, the unbudgeted reachable injections and terminal
placements are classified by an embedded group $K_a\le S_5$
[@paper37]. A return budget asks a different question: which of those
terminal permutations can be realized from a fixed source within a given
number of actual returns, with injectivity preserved before the terminal
collision?

The first return necessarily applies the restriction of the source lane.
Later restrictions can be selected by choosing the target of the preceding
return. All labels are available, so the same label also selects the current
phase. The resulting products retain a source-dependent initial coset
$B_s$ as well as the aggregate factors $\mathcal A_a$; passing to their
generated group alone forgets this information.

Theorem 3.1 is the central result. It identifies both exact and cumulative
terminal layers with ordered products and constructs one actual guarded
injection sequence for each claimed placement. Theorem 4.4 then gives a
uniform finite return budget by counting right cosets. Theorem 5.1 shows
that the initial coset is not dispensable: fixing even the aggregate set
and full unbudgeted frontier does not fix the first budget layer.

The inherited uniform edge law and unbudgeted incidence classification
are attributed to Paper XXXVII [@paper37]. The new object is the
return-count terminal layer and its complete survivor restriction.
The local home-lane controls are recorded in Appendix A; they are not
needed for the central exact layer formula or its 24-return consequence.

### Related Work and Novelty Boundary

**Group word lengths and positive products.**

Word length depends on the generating set and the convention for
inverses, not only on the generated group. Babai, Hetyei, Kantor,
Lubotzky, and Seress discuss finite-group diameter with generators and
their inverses [@babaiEtAl1990]. Bradford uses positive-word balls and
directed Cayley graphs, explicitly distinguishing them from the
inverse-closed convention [@bradford2017].
The present products also use positive factors; inverse steps are not
free returns. No new general Cayley-diameter method is claimed.

Finite positive-generation and cardinality arguments supply the
elementary saturation proof in Section 4. The contribution is not the
abstract notation of product powers or the observation that a generating
closure forgets lengths. It is the exact correspondence of those
products, including the forced source coset, with the guarded first-exit
witnesses of the declared raw system.

**Almost-group and constrained synchronization.**

Casas Torres studies complete reachability for automata with one defect-one
letter and permutation letters, focusing on a transitive imprimitive
permutation group [@casasTorres2024]. That problem concerns images of the
whole state set. Here five fixed source lineages remain distinct through
every internal return and are read individually at their first strict exit.

Wolf studies synchronization under constraints on how a word traverses
states [@wolf2020]. Our guard instead maintains injectivity on the complete
five-point placement until a terminal collision, and our cost counts
normalized returns. We do not provide a general constrained-synchronization
algorithm or a classification of shortest original-letter words.

**Inherited geometry and scoped new claims.**

Paper XXXVII supplies the uniform full-lane edge law, constructive
unbudgeted reachability, and terminal survivor restriction [@paper37].
Those results remain inherited inputs, not claims newly owned here.
Theorem 3.1 supplies the return-count description with actual witnesses;
its uniform bound and Theorem 5.1's symbolic source-initial-layer
separation concern that new bounded observable.

The comparison is selective and does not establish exhaustive priority.
Different tasks alone are not an expressivity separation or a claim of
strict superiority. Likewise, $(\mathcal A_a,B_s)$ is a proved sufficient
description of the layers, not a claimed minimal invariant. The claims are
confined to the declared unit-cost return model; neither sharpness nor a
typed-transfer bridge is asserted.

## Raw System and Return-Count Convention

Retain the raw setup of Paper XXXVII version 1.0 [@paper37]. Fix

$$
 n=5g,\qquad \Delta=g,\qquad g\ge2,\qquad
 Q=\mathbb Z/n\mathbb Z,\qquad E=Q\setminus\{0\},
 \tag{2.1}
$$

with $p(q)=q+1$ and
$\varepsilon_\Delta(0)=\Delta$,
$\varepsilon_\Delta(q)=q$ for $q\ne0$.
Its unique collision pair is $K_\Delta=\{0,\Delta\}$.
The ordinary lanes and punctured lane are

$$
 \begin{aligned}
 C_j&=\{j+t\Delta:t\in\mathbb Z/5\mathbb Z\},
       &&1\le j<g,\\
 C_\ast&=\{\Delta,2\Delta,3\Delta,4\Delta\}.
 \end{aligned}
 \tag{2.2}
$$

The branch $a\in\operatorname{Sym}(E)$ stabilizes this lane partition.
There are a permutation $\pi$ of the ordinary lane indices and arbitrary
$\sigma_j\in S_5=\operatorname{Sym}(\mathbb Z/5\mathbb Z)$ such that

$$
 a(j+t\Delta)=\pi(j)+\sigma_j(t)\Delta.
 \tag{2.3}
$$

The restriction to $C_\ast$ is arbitrary. Fix source labels
$T_0=\{q_0,\ldots,q_4\}$, a source lane $s=j_{\rm src}$, and

$$
 \lambda_0=\lambda_{s,{\rm id}},\qquad
 \lambda_{j,\kappa}(q_i)=j+\kappa(i)\Delta.
 \tag{2.4}
$$

These five labelled lineages form a supplied local configuration. They are
not asserted to be all current packets descended from the full initial
carrier $Q$; first exit below is relative to this configuration.

Source indices are read modulo five. Set

$$
 c(t)=t+1,\qquad H=\langle c\rangle,\qquad
 K_a=\langle c,\sigma_1,\ldots,\sigma_{g-1}\rangle\le S_5.
 \tag{2.5}
$$

Every label $r\in Q$ is available. The normalized return is
$\phi_r^{(a)}=\varepsilon_\Delta p^r a$.
Composition is right-to-left; a word lists labels in execution order.
The inherited edge law, Paper XXXVII Lemma 3.1 / equation (3.2), is

$$
 \begin{gathered}
 \pi(j)+r=h+k\Delta\pmod n,\qquad 1\le h<g,\\
 \lambda_{j,\kappa}\xrightarrow{r}
       \lambda_{h,c^k\sigma_j\kappa}.
 \end{gathered}
 \tag{2.6}
$$

This edge is uniformly enabled on every injection filling $C_j$.
If $\pi(j)+r\equiv0\pmod g$, the corresponding occurrence is strict:
its pre-collapse support is
$\widehat C_\ast=\{0,\Delta,2\Delta,3\Delta,4\Delta\}$.
The punctured lane cannot receive five distinct lineages internally.

A terminal witness has an actual guarded prefix followed by one strict
return. Its return count $N_{\rm ret}$ includes that last occurrence.
Thus an $N$-return witness has $N-1$ internal returns and one terminal
return. An empty internal prefix is allowed; zero returns cannot realize
a terminal event.

Write

$$
 \mu_\eta(q_i)=\eta(i)\Delta,\qquad \eta\in K_a.
 \tag{2.7}
$$

Paper XXXVII, Theorem 5.1 [@paper37], identifies these with all actual unbudgeted
pre-collapse terminal placements. Define $\Theta_{=N}(a,s)$ by actual
witnesses using exactly $N$ returns, and define $\Theta_N(a,s)$ by actual
witnesses using at most $N$ returns:

$$
 \begin{aligned}
 \Theta_{=N}
   &=\{\eta\in K_a:\mu_\eta\text{ has an actual }N\text{-return witness}\},\\
 \Theta_N&=\bigcup_{t=1}^{N}\Theta_{=t},\qquad N\ge1.
 \end{aligned}
 \tag{2.8}
$$

The prefix must remain injective at every internal return. The final
return is therefore the first strict rank drop.

For subsets of a group, $XY=\{xy:x\in X,\ y\in Y\}$,
$X^0=\{1\}$, and $X^{\ell+1}=XX^\ell$.
No inverse is treated as a free generator or a free return.

## Exact Return Layers and Same-Witness Realization

Define the existing aggregate factor set and forced source coset by

$$
 \mathcal A_a=\bigcup_{1\le j<g}H\sigma_j,\qquad B_s=H\sigma_s.
 \tag{3.1}
$$

### Theorem 3.1. Exact and cumulative terminal-layer formulas

For every $N\ge1$,

$$
 \boxed{
 \begin{aligned}
 \Theta_{=N}(a,s)&=\mathcal A_a^{N-1}B_s,\\
 \Theta_N(a,s)&=\bigcup_{\ell=0}^{N-1}\mathcal A_a^\ell B_s.
 \end{aligned}}
 \tag{3.2}
$$

For every element, the construction produces one actual witness with the
stated return count, retaining the same concrete representative from step
to step.

**Proof: actual paths imply products.** Consider an actual $N$-return
witness. Put $j_0=s$ and $\kappa_0={\rm id}$.
For internal step $t$, let its ordinary target be $C_{j_t}$ and write
its phase choice as $k_t\in\mathbb Z/5\mathbb Z$. Equation (2.6) gives

$$
 \kappa_t=c^{k_t}\sigma_{j_{t-1}}\kappa_{t-1}.
 \tag{3.3}
$$

The last step produces
$\eta=c^{k_N}\sigma_{j_{N-1}}\kappa_{N-1}$.
Consequently,

$$
 \eta=
 (c^{k_N}\sigma_{j_{N-1}})\cdots
 (c^{k_2}\sigma_{j_1})(c^{k_1}\sigma_s).
 \tag{3.4}
$$

The first chronological factor, on the right, belongs to $B_s$.
Each later factor belongs to $\mathcal A_a$. This proves the forward
inclusion for the exact layer.

**Proof: products imply actual paths.** Conversely, choose a product
as in (3.4), with $j_0=s$, ordinary $j_1,\ldots,j_{N-1}$, and phases
$k_1,\ldots,k_N$. For $1\le t<N$, choose

$$
 r_t=j_t-\pi(j_{t-1})+k_t\Delta\pmod n.
 \tag{3.5}
$$

Starting at $\lambda_0$, this one return both applies the desired factor
and places the resulting injection in the ordinary lane needed for the
next factor. It is uniformly enabled by (2.6). The actual successor
determines the next concrete input; no representative is exchanged in
a decoder fiber.

For the last occurrence choose

$$
 u=-\pi(j_{N-1})+k_N\Delta\pmod n.
 \tag{3.6}
$$

It gives the pre-collapse placement $\mu_\eta$ and has support
$\widehat C_\ast$, hence is strict. The preceding $N-1$ returns were
injective, so this is the first rank drop. When $N=1$, the construction
has no internal step and uses $j_0=s$ directly.

Taking the union over $1\le t\le N$ proves the cumulative formula.
The phase choice in each factor is supplied by that return's label;
no separate phase path or uncharged relocation has been inserted.
$\square$

In particular,

$$
 \Theta_1=B_s=H\sigma_s.
 \tag{3.7}
$$

The forced source factor cannot be replaced by $H$ or discarded.
The result preserves the fixed source and desired terminal placement,
not an independently preassigned terminal exponent, prefix, or
historical witness.

For a source pair $F$, let $I_F=\{i:q_i\in F\}$ and
$R_0=T_0\setminus F$. Define
$\mathfrak S_a^{\le N}(\lambda_0;F)$ from actual terminal witnesses
whose return count is at most $N$, just as the unbudgeted frontier
is defined in Paper XXXVII.

### Proposition 3.2. Exact budgeted survivor restriction

$$
 \boxed{
 \mathfrak S_a^{\le N}(\lambda_0;F)=
 \left\{q_i\mapsto\eta(i)\Delta\ \ (q_i\in R_0):
 \eta\in\Theta_N,\quad \eta(I_F)=\{0,1\}\right\}.}
 \tag{3.8}
$$

The same statement for exactly $N$ returns uses $\Theta_{=N}$.

**Proof.** Every actual budgeted terminal placement has permutation
$\eta\in\Theta_N$ by Theorem 3.1. It fuses $F$ precisely when
$\eta(I_F)=\{0,1\}$. Its three survivor reads are the indicated
restriction. Conversely, Theorem 3.1 constructs one actual witness for
every such $\eta$, within the stated budget. That same witness supplies
both the fused pair and its survivor map. $\square$

Thus $(\mathcal A_a,B_s)$ determines the return-count terminal layers.
For fixed $n,\Delta$, and source labels, equal aggregate sets and
initial cosets determine equal budgeted survivor frontiers. This is a
sufficiency statement, not minimality, a converse, or equality of labelled
path languages. The lane permutation is still used to construct the
actual labels in (3.5)--(3.6).

## Uniform Finite Return-Budget Realization

### Lemma 4.1. Positive aggregate generation

The group and the positive monoid generated by $\mathcal A_a$ both equal
$K_a$.

**Proof.** Every element of $\mathcal A_a$ belongs to $K_a$.
For each $j$, the aggregate contains both $\sigma_j$ and
$c\sigma_j$. Its generated group therefore contains all $\sigma_j$ and
$c=(c\sigma_j)\sigma_j^{-1}$, hence equals $K_a$.
Each inverse of an aggregate element is a nonnegative power of that
element because the group is finite. Positive generation consequently
has the same closure. This is an algebraic closure argument, not a
permission to execute a free inverse return. $\square$

### Lemma 4.2. Cumulative recurrence and right-coset closure

For $N\ge1$,

$$
 \Theta_{N+1}=\Theta_N\cup\mathcal A_a\Theta_N,\qquad
 H\Theta_N=\Theta_N.
 \tag{4.1}
$$

Each $\Theta_N$ is a nonempty union of five-element right cosets $H\kappa$.

**Proof.** The recurrence follows by distributing set multiplication
over the finite union in (3.2). The initial coset is left $H$-invariant,
as is $\mathcal A_a=\bigcup_jH\sigma_j$. Each term in that union is
therefore left $H$-invariant. Since $H$ has order five, its left action
on the group is free and its orbits are the five-element right cosets
$H\kappa$. The initial layer has five elements and every cumulative
layer contains it. $\square$

The recurrence concerns sets of attainable terminal permutations.
It does not append an internal step to a completed strict exit.
To realize a new product, Theorem 3.1 constructs a new path, choosing
ordinary targets for all factors except the last. In particular, it
can retarget what would have been a shorter witness's final factor.

Nor does right-coset closure make left multiplication by each aggregate
element a deterministic map on right cosets. The normalizer condition
for that different assertion remains the one in Paper XXXVII.

### Lemma 4.3. No premature stall

If $\Theta_{N+1}=\Theta_N$, then $\Theta_N=K_a$. Consequently,

$$
 \Theta_N\ne K_a
 \quad\Longrightarrow\quad
 |\Theta_{N+1}|\ge|\Theta_N|+5.
 \tag{4.2}
$$

**Proof.** Equality and (4.1) imply $x\Theta_N\subseteq\Theta_N$ for
every $x\in\mathcal A_a$. Left multiplication is a bijection of the
finite group, so $|x\Theta_N|=|\Theta_N|$ and the inclusion is equality.
It follows that $\Theta_N$ is invariant under each such left
multiplication and its inverse, and hence under the generated group
$K_a$.

Choose $y\in\Theta_N$. For every $z\in K_a$, the element $zy^{-1}$
belongs to $K_a$, so invariance gives $z=(zy^{-1})y\in\Theta_N$.
The reverse inclusion already holds, proving $\Theta_N=K_a$.

If the cumulative layer is proper, it must therefore grow strictly.
Both layers are unions of five-element right cosets, so strict growth
adds at least five elements. $\square$

### Theorem 4.4. Uniform 24-return realization

Put $q=|K_a|/5$, an integer because $H\le K_a$. Then

$$
 \boxed{\Theta_q=K_a,\qquad q\le24.}
 \tag{4.3}
$$

Every actual attainable terminal placement has one guarded witness
whose first strict return is terminal and whose total return count
is at most $q$.

**Proof.** $K_a$ has exactly $q$ right cosets of $H$. The initial
layer contains one of them. By Lemma 4.3, each successive cumulative
layer either has already reached $K_a$ or adds at least one new coset.
After at most $q-1$ expansions, the layer is full. This includes $q=1$,
where the initial coset is already all of $K_a$.
Finally, $|K_a|\le120$ gives $q\le24$.

Every $\eta\in K_a$ belongs to the cumulative layer $\Theta_q$.
Theorem 3.1 supplies the actual guarded prefix and terminal occurrence
realizing $\mu_\eta$ within this budget. Paper XXXVII's terminal
classification identifies these with all unbudgeted attainable
placements. $\square$

By Proposition 3.2, the same bound realizes every unbudgeted survivor
map, with its fused pair read from the same terminal permutation.
Equivalently,

$$
 \mathfrak S_a^{\le q}(\lambda_0;F)
       =\mathfrak S_a(\lambda_0;F)
       \qquad\text{for every source pair }F.
 \tag{4.4}
$$

The bound concerns cumulative layers, not $\Theta_{=q}$.
Exact layers need not be monotone: if every local restriction is odd,
all aggregate elements are odd because a five-cycle is even, and
every exact $N$-return terminal permutation has parity $(-1)^N$.
No assertion that every placement can be padded to exactly 24 returns,
or that 24 is a sharp constant, is made.

## An All-g Budget-Frontier Non-Descent Family

### Theorem 5.1. First-layer separation and second-layer recovery

Fix $g\ge3$, the same source
$\lambda_0(q_i)=1+i\Delta$, $\pi={\rm id}$, and identity on the
punctured lane. Let $\tau(t)=-t\pmod5$ and define

$$
 \begin{aligned}
 a^{(2)}:&\quad \sigma_2=\tau,\quad \sigma_j={\rm id}\ (j\ne2),\\
 a^{(1)}:&\quad \sigma_1=\tau,\quad \sigma_j={\rm id}\ (j\ne1).
 \end{aligned}
 \tag{5.1}
$$

Both branches have the same $K_a=D_{10}$, complete reachable injection
set, terminal-placement set, and unbudgeted survivor frontier. They
also have the same unsigned labelled lane-exit graph.
For each consecutive source pair $F_i=\{q_i,q_{i+1}\}$,

$$
 \begin{aligned}
 \mathfrak S_{a^{(2)}}^{\le1}(\lambda_0;F_i)&=\{s_i^+\},\\
 \mathfrak S_{a^{(1)}}^{\le1}(\lambda_0;F_i)&=\{s_i^-\},
 \end{aligned}
 \qquad s_i^+\ne s_i^-,
 \tag{5.2}
$$

where, in the ordered survivor labels
$(q_{i+2},q_{i+3},q_{i+4})$,

$$
 s_i^+=(2\Delta,3\Delta,4\Delta),\qquad
 s_i^-=(4\Delta,3\Delta,2\Delta).
 \tag{5.3}
$$

Both one-return sets have cardinality one. At two returns the
complete sets agree:

$$
 \mathfrak S_{a^{(2)}}^{\le2}(\lambda_0;F_i)
 =\mathfrak S_{a^{(1)}}^{\le2}(\lambda_0;F_i)
 =\{s_i^+,s_i^-\}.
 \tag{5.4}
$$

**Proof.** Both branches contain an identity restriction and a
reflection restriction, so

$$
 K_a=\langle c,\tau\rangle=H\sqcup H\tau=D_{10},
 \qquad \mathcal A_a=D_{10}.
 \tag{5.5}
$$

Paper XXXVII, Theorems 4.1, 5.1, and 5.2, now gives identical
unbudgeted injections, terminal placements, and survivor sets.
The unsigned labelled graph depends on $\pi$ and the lane partition,
not on the local restrictions, so it agrees as well.

The source is $C_1$. By (3.7), its forced first layers are

$$
 \Theta_1(a^{(2)},1)=H,\qquad
 \Theta_1(a^{(1)},1)=H\tau.
 \tag{5.6}
$$

For $F_i$, the unique rotation sending its two indices to $\{0,1\}$
is $\eta_i^+(t)=t-i$. The unique reflection doing so is
$\eta_i^-(t)=i+1-t$. Their restrictions to the three ordered survivor
labels give exactly (5.3). Proposition 3.2 supplies actual single-return
witnesses for both. The coordinates $2\Delta$ and $4\Delta$ are
distinct in $Q$, so the survivor maps differ even though their counts
are equal.

For either branch, $\mathcal A_a=D_{10}$ and $\Theta_1$ is a nonempty
coset in that group. Thus
$\mathcal A_a\Theta_1=D_{10}$ and (4.1) gives
$\Theta_2=D_{10}$. Restriction yields (5.4).
Nonconsecutive pairs have empty survivor sets throughout, since
dihedral permutations preserve five-cycle adjacency. $\square$

The family keeps even the aggregate factor set fixed. What differs is
the forced initial coset $B_s$. Therefore

$$
 \boxed{
 \begin{gathered}
 \text{same }K_a,\ \text{same complete reachable injections},\\
 \text{same unbudgeted terminal and survivor sets}\\
 \not\Longrightarrow\text{same return-budgeted survivor frontier}.
 \end{gathered}}
 \tag{5.7}
$$

This is a full source-addressed set separation, not a count separation,
a search failure, or a universal minimality statement.

## Conditional Original-Letter Consequence

### Corollary 6.1. Conditional 24n bound from the corresponding section source

Suppose an existing normalization realization binds the fixed normalized
source to a concrete raw section source. Fix its parameter $t_0\in Q$
and suppose it represents label $r$ by the chronological original block

$$
 p^{[t_0+r]_n}d,\qquad 0\le[t_0+r]_n<n.
 \tag{6.1}
$$

Assume this same fixed realization covers the internal states and terminal
occurrences of the witnesses constructed in Theorem 4.4, transporting their
guards and strict events on the corresponding source-labelled raw invocation.
Then every normalized attainable terminal placement has a corresponding
raw strict-exit witness, from that fixed section source, with

$$
 |w_{\rm raw}|\le n\,|K_a|/5\le24n.
 \tag{6.2}
$$

**Proof.** Theorem 4.4 supplies at most $|K_a|/5$ returns on one
actual witness. Expand those returns through the supplied blockwise
realization. Each block has at most $n$ original letters.
The assumed guard/event transport makes every nonterminal block
rank-preserving and the last block strict. The pure $p$ prefixes
preserve rank, so no earlier strict drop is introduced. Concatenating
these same-source blocks gives (6.2). $\square$

The fixed normalization realization is an additional hypothesis. No
source-specific realization theorem is invoked here to discharge it;
the abstract normalized model alone does not supply that binding. Thus
(6.2) is a proved conditional consequence, not an independent original-letter
length result.

This paper does not supply an original normalization realization for an
unspecified source. This conditional bound excludes entry cost, does
not preserve a chosen old word or exponent, and is not a shortest-word
classification. Labels with different $[t_0+r]_n$ have different raw
costs, although every phase choice costs one normalized return.

## Scope and Open Boundaries

The central result is the exact return-count layer formula with its
actual guarded realization. Uniform finite-budget saturation and the
symbolic initial-layer separation are its quantitative and negative
consequences; neither requires a subgroup census or a shortest-word
classification.

The source assumption is not an entry-supply conclusion. Under the frozen
lane-stabilizing actions, reduction modulo $g$ intertwines each return with
a permutation of residue classes: $a$ permutes lanes, $p^r$ translates
residues, and $\varepsilon_g$ preserves them. Thus a support occupying more
than one residue class cannot enter a single full ordinary lane under these
returns. In particular, the full normalized carrier $E$ cannot supply this
entrance. This does not change the source-relative first-exit or budget results.

The all-$g$ statements are proved under the inherited raw full-lane
assumptions. Bounded replay checks only their declared finite instances.
The partial Lean spine covers selected algebraic steps, not the concrete
guarded realization, and does not import Paper XXXVII's formalization.

The three notions remain distinct:

$$
 \boxed{
 \begin{gathered}
 \text{exact return-count terminal layers}\\
 \ne\text{shortest original-word classification}\\
 \ne\text{recursive credit budget or settlement}.
 \end{gathered}}
 \tag{7.1}
$$

Partial occupancy, restricted return-label menus, typed source supply,
target-blind authorization, selector identity, transfer membership,
handoff, POS, recursive compatibility, and reset bounds are not supplied.
These results concern the declared full-lane return-count observable only;
the unbudgeted classification is an inherited input, not a budget theorem
attributed to the earlier published version.

## Computational Artifacts

The paper-owned evidence package is under `experiments/paper38/` in the
[RIME repository](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper38).
Paths below are relative to this directory.

| Surface | Location | Role |
|---|---|---|
| Scope | `audit_scope.py` | fixed finite catalogue and budget range |
| Control | `return_budget_audit.py`, `results/` | return layers and actual witness checks |
| Lean | `lean/` | partial algebraic spine and source-addressed coverage |
| Validation | `validation/` | separately implemented coordinate replay and source binding |
| Evidence | `development-manifest.json` | exact selected source closure |
| Release | `release-manifest.json` | manuscript, PDF, and environment binding |
| Receipt | `results/` | downstream local closure verification |

The controls exhaust all 120 local restrictions at $g=2$ with the declared
punctured identity, and use a selected catalogue at $g=3,4$. Every ordinary
source lane and exact return counts $1,\ldots,26$ are checked. The symbolic
matched family is additionally replayed at $g=3,4,5$. These are bounded
consistency controls, not proofs of the all-$g$ results or independent
Computational Certificates. The validator reconstructs the full labelled
injection layers and survivor maps rather than trusting stored counts.

The partial Lean algebraic spine checks positive product layers, cumulative
phase-block growth and saturation, the algebraic 24-factor consequence,
and the finite $D_{10}$ initial-layer control. It is not a complete
formalization of the all-$g$ geometric results: concrete guards, actual
label-word realization, physical survivor embedding, and the original-letter
corollary remain outside its checked scope.

## Claim Status and Boundary

| Claim | Status |
|---|---|
| Theorem 3.1 and Proposition 3.2: exact layers and survivor restriction | proved with same-witness realization |
| Lemmas 4.1--4.3 and Theorem 4.4: cumulative saturation | proved; at most 24 normalized returns |
| Theorem 5.1: matched initial-layer separation | proved for all $g\ge3$ in the declared family |
| Corollary 6.1: original-letter bound | Proved conditional corollary; the fixed normalization realization is not established here |
| Lemma A.1 and Proposition A.2: home-lane controls | Proved auxiliary lemma and proposition; not premises of Theorem 3.1 or 4.4 |
| Retained finite replay | Bounded consistency control on the declared finite catalogue; not an all-$g$ proof |
| Lean algebraic spine | Partial formalization; concrete guards and survivor realization remain unformalized |

The proved mathematical statements have theorem-level evidence under their
declared hypotheses. Partial formalization describes proof coverage, not a
separate evidence level or an enlargement of those hypotheses.

## Conclusion

The fixed source enters the terminal layer law through $B_s=H\sigma_s$.
All later factors come from $\mathcal A_a$, and choosing the next lane and
phase within each return realizes the products on one actual guarded
sequence. The cumulative layers saturate within $|K_a|/5\le24$ returns
without a normalizer assumption or a deterministic coset update.

The matched family fixes $\mathcal A_a$, $K_a$, and all unbudgeted
incidence sets while changing the first-layer survivor maps. Its second
layer recovers the common complete frontier. Thus the generating closure
is adequate for unbudgeted existence but omits an initial condition that
can matter for return-budgeted incidence. The conditional original-letter
bound does not identify a shortest-word metric or a recursive settlement
law.

## Appendix A: Local Home-Lane Controls

### Lemma A.1. Six-return control and thirteen-return generator loops

Let $\alpha_j=j-\pi(j)\pmod n$ and
$m_j=\operatorname{ord}(\sigma_j)$.
Actual uniformly guarded words realize phase and pure relocation with
at most six returns. At any ordinary home lane, an actual loop realizes
any $\sigma_j$ with at most thirteen returns.

**Proof.** By the cycle types of a permutation on five points,
$m_j\in\{1,2,3,4,5,6\}$. Label $\alpha_j$ is an internal self-return on
$C_j$ and applies $\sigma_j$ to its current permutation. The word

$$
 \underbrace{\alpha_j;\ldots;\alpha_j}_{m_j-1\ {\rm returns}};
          (\alpha_j+\Delta)
 \tag{A.1}
$$

acts as $(c\sigma_j)\sigma_j^{m_j-1}=c$, staying in $C_j$.
Replacing its final label by $h-\pi(j)$ gives

$$
 T_{j\to h}=
 \underbrace{\alpha_j;\ldots;\alpha_j}_{m_j-1\ {\rm returns}};
          (h-\pi(j)).
 \tag{A.2}
$$

The total within-lane permutation is
$\sigma_j\sigma_j^{m_j-1}={\rm id}$, and the final support is $C_h$.
Both words have length $m_j\le6$; when $m_j=1$, the repeated block is
empty. All intermediate steps stay in an ordinary lane, and the last
step has the explicitly chosen ordinary target. Equation (2.6) proves
legality on the same representative throughout.

At a home lane $C_h$, execute

$$
 T_{h\to j};\ 0;\ T_{\pi(j)\to h}.
 \tag{A.3}
$$

The first and last blocks preserve indices. The zero return applies
$\sigma_j$ while moving $C_j$ to $C_{\pi(j)}$.
The loop therefore applies $\sigma_j$ at $C_h$ at cost at most
$6+1+6=13$. $\square$

### Proposition A.2. Conservative fixed-home-lane terminal bound

Every $\eta\in K_a$ has an actual terminal witness with

$$
 N_{\rm ret}\le13(|K_a|-1)+7\le1554.
 \tag{A.4}
$$

**Proof.** In a finite group, the positive monoid generated by
$S=\{c,\sigma_1,\ldots,\sigma_{g-1}\}$ is the group it generates:
an inverse of each generator is a nonnegative power of that generator.
Thus every element of $K_a$ is reachable from the identity in the
positive Cayley graph. A shortest such path repeats no vertex and has
at most $|K_a|-1$ edges.

Choose an ordinary incoming lane $C_j$. Relocate there at cost at most
six. Use Lemma A.1 to realize a positive expression for
$\kappa=\sigma_j^{-1}\eta$ at that home lane, at cost at most
$13(|K_a|-1)$. Finally take $u=-\pi(j)$.
The inherited terminal law gives
$p^u a\lambda_{j,\kappa}=\mu_\eta$, on this same actual prefix and
terminal occurrence. Adding the last return gives (A.4), since
$|K_a|\le|S_5|=120$. $\square$

This construction controls permutations at a prescribed home lane
without using the global order of $a$. It is not used to prove the exact
layer formula or Theorem 4.4.

## References {.unnumbered}
