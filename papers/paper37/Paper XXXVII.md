# Lineage Permutation Groups and Complete Ordinary-Lane Survivor Frontiers
### Guarded Relocation and Phase-Coset Boundaries

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXVII | Version 1.0**

*This paper (Paper XXXVII of the RIME program) classifies intrinsic raw
reachability and survivor incidence for five source lineages filling an
ordinary lane. It makes no typed-transfer, projectability, settlement, or
reset-bound claim.*

## Abstract

**Problem.** A fused-pair spectrum does not determine where the three
surviving source lineages are placed. For branches that permute arithmetic
lanes, an abstract permutation group also does not by itself establish that
its elements are realizable by collision-free paths.

**Approach.** Fix normalized returns
$\phi_r^{(a)}=\varepsilon_\Delta p^r a$ with $n=5g$, $\Delta=g$, and $g\ge2$.
Five labelled lineages fill an ordinary five-point lane. The branch
stabilizes the lane partition but may act by arbitrary permutations within
ordinary lanes. All return labels are available, and paths have no length
budget. Actual guarded words realize pure lane relocation and every local
permutation generator.

**Results.** If $c$ is the five-position phase cycle and $\sigma_j$ are the
ordinary-lane restrictions, then
$K_a=\langle c,\sigma_1,\ldots,\sigma_{g-1}\rangle\le S_5$ gives exactly
the reachable injections: one copy of $K_a$ on each ordinary lane. The
phase state set is the lane set times the right-coset set
$H\backslash K_a=\{H\kappa\}$, where $H=\langle c\rangle$; deterministic
labelled phase descent requires a separate normalizer condition. Every
terminal placement comes from an element of the same $K_a$, and restricting
that element to the three survivors gives the complete frontier.
Symbolic matched families distinguish two losses of information:
$F_{20}$ and $S_5$ agree on unsigned labelled mobility, local parity, and
fused-pair coverage but have two versus six survivor placements per pair;
$A_5$ and $S_5$ have different reachable injection sets but identical
complete survivor spectra.

**Boundary.** The classification concerns full ordinary-lane occupancy and
unbudgeted raw paths. It does not classify partial occupancy, prove a
universal minimal quotient, or supply an existing-semantics typed bridge.

**Keywords.** circular automata; guarded returns; packet lineages;
permutation groups; phase cosets; survivor incidence

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/(5g)\mathbb Z$, $\Delta=g$ | circular carrier and lane spacing |
| $p(q)=q+1$ | fixed full cycle |
| $E=Q\setminus\{0\}$ | normalized section carrier |
| $\varepsilon_\Delta$ | collapse $0\mapsto\Delta$, fixing all other points |
| $K_\Delta=\{0,\Delta\}$ | terminal collision pair |
| $C_j$, $1\le j<g$ | ordinary five-point lanes |
| $C_\ast$, $\widehat C_\ast$ | punctured and full kernel lanes |
| $a$, $\pi$, $\sigma_j$ | branch, lane permutation, and local restrictions |
| $T_0=\{q_0,\ldots,q_4\}$ | source-lineage labels in positive source order |
| $c(t)=t+1$ on $\mathbb Z/5\mathbb Z$ | phase cycle |
| $K_a$ | five-position lineage permutation group |
| $\lambda_{j,\kappa}$ | placement $q_i\mapsto j+\kappa(i)\Delta$ |
| $\mathcal L_a(\lambda_0)$ | injections reachable by actual guarded paths |
| $H\backslash K_a$ | right cosets $H\kappa$, not a quotient group |
| $\mathcal M_a(\lambda_0)$ | actual pre-collapse terminal placements |
| $K_a(F)$ | terminal permutations sending the indices of $F$ to $\{0,1\}$ |
| $\mathfrak S_a(\lambda_0;F)$ | complete source-addressed survivor spectrum |
| $t_{01}=(0\ 1)$ | swap of the two terminal kernel indices |

## Introduction

A strict rank-five exit determines both a fused source pair and the
placements of the three remaining lineages. The latter data are not
recoverable from pair-level reachability alone. This paper asks for the
complete raw survivor frontier when five source lineages fill an ordinary
arithmetic lane and the branch restrictions are arbitrary permutations.

The distinction between group generation and actual paths is central.
Knowing that several permutations generate a subgroup does not show that
each generator, its inverse, and their composites satisfy the guards of
the dynamical system. Conversely, knowing an existential coarse edge at
each stage does not identify a single representative that can traverse the
whole path. Source-addressed incidence is needed when such representative
control is unavailable [@paper33].

In the regime considered here, full ordinary-lane occupancy supplies
uniform guards. The punctured lane has four positions and cannot receive
five distinct lineages. A positive word realizes the inverse of the
globally enabled branch return. Combining that word with a return label
gives pure relocation between any two ordinary lanes. Relocation then
turns each local branch restriction into an actual guarded loop at any
current lane. These constructions realize every element of a single
five-position permutation group, without changing representatives between
independently chosen edge witnesses.

Paper XXXVI treats locally dihedral restrictions by retaining the lane and
source-relative orientation [@paper36]. Here orientation is replaced by a
full permutation parameter. The resulting phase-coset set specializes to
one cyclic state or two dihedral states per lane. For arbitrary local
permutations, however, that state-set parameterization need not support
deterministic labelled updates. The exact normalizer condition is stated
separately.

The main results proceed in three steps.

1. Actual relocation and local loops give the complete reachable-injection
   classification, including a constructive reverse inclusion.
2. The same group gives exactly the actual terminal placements; its
   restriction to the three survivors gives the complete frontier and
   projection multiplicity.
3. Two symbolic matched families show that coarse mobility data can lose
   survivor information, while full reachable-state information can retain
   distinctions that survivor projection forgets.

The branch-normalized return law is inherited from Papers XXX and XXXI
[@paper30; @paper31]. All full-lane path constructions and terminal
converses used below are proved here. No finite census is a premise of the
classification.

### Related Work and Novelty Boundary

Monotonic and cyclic-order-preserving automata have an established
synchronization theory [@eppstein1990]. The present setting allows
ordinary-lane restrictions that need not preserve cyclic order. Its
question is not a shortest reset sequence but the exact source-labelled
boundary of a guarded five-lineage execution.

Almost-group automata with one defect-one letter and permutation letters
are a close ambient class. Casas Torres studies conditions for complete
reachability, including the case of transitive imprimitive permutation
groups [@casasTorres2024]. The invariant here retains individual source
lineages and requires injectivity on their complete support throughout the
internal path. Support-image reachability and complete survivor incidence
are different observables.

Dynamic-constraint synchronization concerns restrictions on the order in
which a word traverses states [@wolf2020]. The guard here is injectivity on a
specified five-point placement at every internal return, followed by an
actual terminal collision. The results below do not give a general
algorithm or complexity classification for constrained synchronization.

Within the raw frontier line, Paper XXXV classifies arbitrary-branch
one-lane survivor incidence by reachable cyclic orders and terminal-phase
collapse [@paper35]. Paper XXXVI supplies a signed mobility quotient and
survivor theorem for multiple full ordinary lanes under locally dihedral
restrictions [@paper36]. This paper removes that local restriction in the
same full-lane regime, proves actual relocation and local generator
realization, and identifies the terminal restriction map for arbitrary
ordinary-lane permutations.

Permutation-group generation, coset sets, and orbit-stabilizer counting are
standard background, not novelty claims. The contribution is their exact
realization by the declared guarded words and the resulting same-witness
terminal classification. The related-work comparison is selective; no
exhaustive priority or universal minimality assertion is made.

## Normalized Full-Lane Dynamics

### Carrier, Branch, and Source

Throughout,

$$
 n=5g,\qquad \Delta=g,\qquad g\ge2,\qquad
 Q=\mathbb Z/n\mathbb Z,\qquad E=Q\setminus\{0\}.
 \tag{2.1}
$$

Let $p(q)=q+1$ and define

$$
 \varepsilon_\Delta(q)=
 \begin{cases}
 \Delta,&q=0,\\
 q,&q\ne0.
 \end{cases}
 \qquad K_\Delta=\{0,\Delta\}.
 \tag{2.2}
$$

The lane partition of $E$ consists of

$$
 \begin{aligned}
 C_j&=\{j+t\Delta:t\in\mathbb Z/5\mathbb Z\},
       &&1\le j<g,\\
 C_\ast&=\{\Delta,2\Delta,3\Delta,4\Delta\}.
 \end{aligned}
 \tag{2.3}
$$

Its full kernel lane in $Q$ is
$\widehat C_\ast=C_\ast\cup\{0\}$.
Assume

$$
 a\in\operatorname{Stab}
       \bigl(\{C_\ast,C_1,\ldots,C_{g-1}\}\bigr)
       \le\operatorname{Sym}(E).
 \tag{2.4}
$$

The unique four-point lane is fixed setwise. There are a permutation $\pi$
of $\{1,\ldots,g-1\}$ and arbitrary $\sigma_j\in S_5$ such that

$$
 a(j+t\Delta)=\pi(j)+\sigma_j(t)\Delta.
 \tag{2.5}
$$

Here $S_5=\operatorname{Sym}(\mathbb Z/5\mathbb Z)$ acts on the five
within-lane indices. No condition is imposed on $a|_{C_\ast}$.

Fix distinct source labels $T_0=\{q_0,\ldots,q_4\}$ and one ordinary source
lane $C_{\rm src}=C_{j_{\rm src}}$. Set

$$
 \lambda_0(q_i)=j_{\rm src}+i\Delta,\qquad
 \lambda_{j,\kappa}(q_i)=j+\kappa(i)\Delta
       \quad(\kappa\in S_5).
 \tag{2.6}
$$

The initial enumeration gives the positive cyclic order of the source
lineages. A lineage may denote any fixed nonempty source packet. Distinct
source packets remain distinct labels before the strict exit; their atom
counts are not read by the dynamics studied here.

### Guarded Paths and Terminal Witnesses

For each $r\in Q$, the normalized return is

$$
 \phi_r^{(a)}=\varepsilon_\Delta\circ p^r\circ a.
 \tag{2.7}
$$

Composition is right-to-left. A word lists its return labels in execution
order, and acts on a placement by postcomposition of its coordinate map.
For an injection $\lambda:T_0\hookrightarrow E$, a return is enabled exactly
when

$$
 K_\Delta\nsubseteq p^r a\lambda(T_0).
 \tag{2.8}
$$

The unique nonsingleton fiber of $\varepsilon_\Delta$ is $K_\Delta$, so
(2.8) is equivalent to injectivity of $\phi_r^{(a)}\lambda$.
Let $\mathcal L_a(\lambda_0)$ be the injections obtained by actual finite
words whose every internal return is enabled, including the empty word.
All labels are available, and no word-length budget is imposed.

A terminal witness consists of a reachable injection $\lambda$ and a label
$u$ with
$K_\Delta\subseteq p^u a\lambda(T_0)$. Its pre-collapse placement and strict
incidence are

$$
 \mu=p^u a\lambda,\qquad
 \beta=\varepsilon_\Delta\mu.
 \tag{2.9}
$$

Write $\mathcal M_a(\lambda_0)$ for the actual pre-collapse terminal
placements. For $F\subset T_0$, $|F|=2$, put $R_0=T_0\setminus F$ and define

$$
 \mathfrak S_a(\lambda_0;F)=
 \left\{\beta|_{R_0}:
 \begin{array}{l}
 \mu=p^u a\lambda\in\mathcal M_a(\lambda_0),\\
 \mu(F)=K_\Delta
 \end{array}\right\}.
 \tag{2.10}
$$

This is a set of source-addressed injections, not a count or mass profile.
On $R_0$, $\beta$ agrees with $\mu$. On $F$, both values of $\beta$ equal
$\Delta$. Thus a survivor map together with the fixed $F$ reconstructs the
complete terminal incidence. Returning lineage labels to their fixed source
packet blocks reconstructs the raw packet endpoint.

### The Lineage Permutation Group

Let $c(t)=t+1$ on $\mathbb Z/5\mathbb Z$ and define

$$
 K_a=\langle c,\sigma_1,\ldots,\sigma_{g-1}\rangle\le S_5,
 \qquad H=\langle c\rangle\cong C_5.
 \tag{2.11}
$$

$K_a$ acts on within-lane indices, identified with the source labels through
(2.6). It is not Paper XXX's physical return group on the normalized
carrier, nor a group of typed transfer objects. Actual guarded realization
of its elements is proved next, rather than assumed from this definition.

## Actual Guarded Relocation and Local Generation

### Lemma 3.1. Uniform full-lane edge law

Every enabled return from a full ordinary lane ends in a full ordinary
lane. If

$$
 \pi(j)+r=h+k\Delta\pmod n,\qquad 1\le h<g,
 \tag{3.1}
$$

then it is enabled on every injection filling $C_j$, and

$$
 \lambda_{j,\kappa}\xrightarrow{r}
 \lambda_{h,c^k\sigma_j\kappa}.
 \tag{3.2}
$$

If $\pi(j)+r\equiv0\pmod g$, the return is strict rather than enabled.

**Proof.** The set $a(C_j)$ is $C_{\pi(j)}$. Rotation by $p^r$ takes it
to the full residue lane with residue $\pi(j)+r$ modulo $g$. If that residue
is zero, the image is $\widehat C_\ast$ and contains both kernel points.
Otherwise it is an ordinary lane $C_h$, which contains neither kernel
point; $\varepsilon_\Delta$ fixes it. This decision depends on the support,
not on its lineage ordering. Applying (2.5) coordinatewise gives (3.2).
$\square$

### Lemma 3.2. Actual relocation and phase words

For any ordinary lanes $C_j,C_h$, an actual guarded word
$T_{j\to h}$ sends

$$
 j+t\Delta\longmapsto h+t\Delta
 \tag{3.3}
$$

on every representative filling $C_j$. Actual guarded loops also realize
every phase $c^t$ on every ordinary lane.

**Proof.** Let $m=\operatorname{ord}(a)$. Since $a(E)=E$,
$\phi_0^{(a)}=a$ is globally enabled. The word consisting of $m-1$ zero
labels implements $a^{-1}$; when $m=1$, this block is empty.
Following it by the label $r=h-j$ gives

$$
 \begin{aligned}
 \phi_{h-j}^{(a)}(\phi_0^{(a)})^{m-1}\big|_{C_j}
   &=\varepsilon_\Delta p^{h-j}\big|_{C_j}\\
   &=p^{h-j}\big|_{C_j}.
 \end{aligned}
 \tag{3.4}
$$

Every zero step sends a full ordinary lane to a full ordinary lane.
The last step sends the representative back to $C_h$ and is uniformly
enabled by Lemma 3.1. Thus this is a word on the actual representative,
not merely equality of formal coordinate maps.

The same inverse block followed by label $\Delta$ realizes
$\varepsilon_\Delta p^\Delta$; on an ordinary lane it is the cycle $c$.
Repeating this loop supplies all five phases, including inverse phases by
positive powers. $\square$

### Lemma 3.3. Actual local-generator loops

Every $\kappa\in K_a$ is realized by a guarded loop at any ordinary lane.

**Proof.** At the current lane $C_h$, use the word

$$
 T_{h\to j}\ ;\ 0\ ;\ T_{\pi(j)\to h}.
 \tag{3.5}
$$

The semicolons denote execution order. Relocation first preserves the
within-lane indices; the zero return then applies $\sigma_j$ and moves to
$C_{\pi(j)}$; the final relocation restores $C_h$ without changing the
new indices. Hence the loop realizes $\sigma_j$ on every injection filling
$C_h$. All three blocks are enabled on the actual predecessor produced by
the previous block.

The loop returns to the same lane, so repetition realizes
$\sigma_j^{-1}$ by a positive power of its finite order. Lemma 3.2 supplies
$c$ and $c^{-1}$ in the same way. Any expression for $\kappa$ in these
generators and inverses can therefore be executed as one concatenated
guarded loop. $\square$

## Complete Reachable Injections and Phase States

### Theorem 4.1. Complete reachable-injection classification

Under the hypotheses of Section 2,

$$
 \boxed{
 \mathcal L_a(\lambda_0)=
 \{\lambda_{j,\kappa}:1\le j<g,\ \kappa\in K_a\}.}
 \tag{4.1}
$$

In particular,
$|\mathcal L_a(\lambda_0)|=(g-1)|K_a|$.

**Proof.** Initially $\lambda_0=\lambda_{j_{\rm src},{\rm id}}$.
Lemma 3.1 shows that every enabled successor of $\lambda_{j,\kappa}$
is $\lambda_{h,c^k\sigma_j\kappa}$. If $\kappa\in K_a$, its successor
permutation also belongs to $K_a$. Induction on the actual word gives the
forward inclusion.

For the reverse inclusion, first use $T_{j_{\rm src}\to j}$ to reach
$\lambda_{j,{\rm id}}$. Lemma 3.3 then realizes any desired
$\kappa\in K_a$ at that lane. The resulting placement is
$\lambda_{j,\kappa}$, and each step is enabled on its actual predecessor.
Distinct $(j,\kappa)$ give distinct injections. $\square$

### Corollary 4.2. Lane-by-phase-coset state set

Two reachable injections are phase equivalent when they occupy the same
lane and differ by a positive $\Delta$-rotation. Then

$$
 \begin{aligned}
 \mathcal L_a(\lambda_0)/{\sim_{\rm ph}}
   &\cong \{1,\ldots,g-1\}\times H\backslash K_a,\\
 [\lambda_{j,\kappa}]_{\rm ph}
   &\longmapsto (j,H\kappa).
 \end{aligned}
 \tag{4.2}
$$

Here $H\backslash K_a$ denotes the right-coset set
$\{H\kappa:\kappa\in K_a\}$, not a quotient group. Its contribution to the
state count is $|K_a|/5$.

**Proof.** A phase acts by
$\lambda_{j,\kappa}\mapsto\lambda_{j,c^t\kappa}$.
Thus equivalence is exactly equality of $j$ and $H\kappa$. Theorem 4.1
supplies every $(j,\kappa)$, and Lemma 3.2 supplies every representative of
its phase class by an actual loop. This proves the bijection and count.
$\square$

### Proposition 4.3. Deterministic labelled phase descent

Fix an enabled label from a source lane $C_j$. Its output phase class is
independent of the input representative of each phase class if and only if

$$
 \sigma_jH\sigma_j^{-1}=H.
 \tag{4.3}
$$

Consequently all internal labelled updates descend deterministically
precisely when every ordinary-lane restriction normalizes $H$.

**Proof.** The target lane and exponent $k$ in (3.1) do not depend on the
representative. The phase representatives $c^t\kappa$ have output classes

$$
 Hc^k\sigma_jc^t\kappa=H\sigma_jc^t\kappa.
 \tag{4.4}
$$

These all equal $H\sigma_j\kappa$ exactly when
$\sigma_jc^t\sigma_j^{-1}\in H$ for every $t$. This is inclusion of
$\sigma_jH\sigma_j^{-1}$ in $H$, hence equality since both groups have
order five. Each source lane has enabled labels to ordinary lanes, so the
condition applies at every source. $\square$

Corollary 4.2 is therefore an exact compression of the reachable state
set, not an unconditional deterministic transition congruence. When
(4.3) fails, a quotient transition must retain representative incidence
or be relation-valued; its existence cannot be inferred from the
state-set bijection alone.

### Corollary 4.4. Cyclic and dihedral specialization

If every ordinary restriction is locally dihedral, then $K_a=C_5$ when
all restrictions preserve orientation and $K_a=D_{10}$ when at least one
reverses it. There are respectively one and two phase states per lane.

**Proof.** Rotations are powers of $c$. Any reflection together with $c$
generates the dihedral group of the five-cycle, and all local restrictions
belong to that group. The coset counts are $5/5$ and $10/5$. The two
dihedral classes record source-relative positive and negative orientation.
$\square$

Thus the signed state of Paper XXXVI is a specialization of the
lane-by-phase-coset state, rather than a proposed minimal quotient for
arbitrary local permutations.

## Actual Terminal Placements and Complete Survivor Projection

### Theorem 5.1. Complete terminal-placement spectrum

For $\eta\in S_5$, define $\mu_\eta(q_i)=\eta(i)\Delta$. Then

$$
 \boxed{
 \mathcal M_a(\lambda_0)=\{\mu_\eta:\eta\in K_a\}.}
 \tag{5.1}
$$

Every placement on the right is produced by one actual guarded prefix and
one terminal occurrence.

**Proof.** By Theorem 4.1, a terminal source has the form
$\lambda_{j,\kappa}$ with $\kappa\in K_a$. A terminal label $u$ satisfies
$\pi(j)+u\equiv0\pmod g$. Write
$\pi(j)+u=k\Delta\pmod n$. Coordinatewise,

$$
 p^u a\lambda_{j,\kappa}(q_i)
     =(c^k\sigma_j\kappa)(i)\Delta.
 \tag{5.2}
$$

Since $c^k\sigma_j\kappa\in K_a$, this gives the forward inclusion.

Conversely, fix $\eta\in K_a$ and any ordinary lane $C_j$.
The permutation $\kappa=\sigma_j^{-1}\eta$ belongs to $K_a$, so
Theorem 4.1 supplies an actual path to $\lambda_{j,\kappa}$. Take the
terminal label $u=-\pi(j)\pmod n$. Then $k=0$ in (5.2), and the
pre-collapse placement is exactly $\mu_\eta$.
It fills $\widehat C_\ast$, so the occurrence is a strict exit.
Also

$$
 p^{-u}\mu_\eta(T_0)=C_{\pi(j)}\subset E,
 \tag{5.3}
$$

which verifies the section pullback on the same witness. No separate
formal terminal placement is substituted for the one produced by the
prefix. $\square$

### Theorem 5.2. Complete survivor frontier

For $F\subset T_0$, $|F|=2$, let
$I_F=\{i:q_i\in F\}$ and define

$$
 K_a(F)=\{\eta\in K_a:\eta(I_F)=\{0,1\}\}.
 \tag{5.4}
$$

Then

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)=
 \left\{
 q_i\mapsto\eta(i)\Delta\ \ (q_i\in R_0):
 \eta\in K_a(F)
 \right\}.}
 \tag{5.5}
$$

In particular, $F$ is hittable if and only if $K_a(F)\ne\varnothing$.

**Proof.** Every actual terminal placement is $\mu_\eta$ for an
$\eta\in K_a$ by Theorem 5.1. It fuses $F$ exactly when
$\eta(I_F)=\{0,1\}$. On all three survivors the collapse fixes the
pre-collapse coordinates, which are
$2\Delta,3\Delta,4\Delta$. Thus every actual survivor map belongs to the
right-hand side.

For any $\eta\in K_a(F)$, use the prefix and terminal label constructed
in the reverse inclusion of Theorem 5.1. That same occurrence both fuses
$F$ and places each survivor as in (5.5). Hence every displayed restriction
is actual. Nonemptiness is equivalent to existence of such an occurrence.
$\square$

The theorem classifies sets of maps. It does not replace one terminal
witness by independent choices for the fused pair and the survivors.
The resulting full incidence has value $\Delta$ on $F$ and the displayed
restriction on $R_0$.

### Corollary 5.3. Exact projection multiplicity

If $K_a(F)\ne\varnothing$, then

$$
 \begin{aligned}
 |\mathfrak S_a(\lambda_0;F)|
   &=\frac{|K_a(F)|}{1+\mathbf 1_{\{t_{01}\in K_a\}}}\\
   &=\frac{|K_a|}
    {|\operatorname{Orb}_{K_a}(I_F)|
      \bigl(1+\mathbf 1_{\{t_{01}\in K_a\}}\bigr)}.
 \end{aligned}
 \tag{5.6}
$$

**Proof.** Two permutations sending $I_F$ to $\{0,1\}$ and agreeing on
the other three indices are either equal or differ by left multiplication
by $t_{01}$. If $t_{01}\notin K_a$, the restriction map is injective.
If $t_{01}\in K_a$, each fiber is the two-element set
$\{\eta,t_{01}\eta\}$. This action is free and stays inside $K_a(F)$.

Since $\{0,1\}$ lies in the orbit of $I_F$ when $K_a(F)$ is nonempty,
the set of permutations sending $I_F$ to that pair is a coset of its
setwise stabilizer. Orbit-stabilizer gives
$|K_a(F)|=|K_a|/|\operatorname{Orb}_{K_a}(I_F)|$.
$\square$

For the cyclic and dihedral specializations, the hittable pairs are
exactly the five source-consecutive pairs. Their survivor counts are one
and two, respectively. The dihedral group contains no single
transposition of two points: every reflection of a five-cycle exchanges
two pairs of points. These cases recover the orientation distinction
without extending it to arbitrary local branches.

## Two Complementary Losses of Information

Fix $\pi={\rm id}$, let $a$ be the identity on $C_\ast$ and on every
ordinary lane except $C_1$, and vary only $\sigma_1$. These branches exist
for every $g\ge2$. The source can be any full ordinary lane.

### Proposition 6.1. Elementary generation controls

The following restrictions give the displayed lineage groups and survivor
counts for each of the ten source pairs.

| $\sigma_1$ | $K_a$ | $|K_a|$ | Survivors per pair |
|---|---|---:|---:|
| $t\mapsto2t$ | $F_{20}\cong C_5\rtimes C_4\cong\operatorname{AGL}(1,5)$ | 20 | 2 |
| $(0\ 1\ 2)$ | $A_5$ | 60 | 6 |
| $(0\ 1)$ | $S_5$ | 120 | 6 |

**Proof.** Translation $c$ and multiplication by $2$ generate exactly
the affine maps $t\mapsto\alpha t+b$ over $\mathbb F_5$:
$2$ generates $\mathbb F_5^\times$, and the translations give every $b$.
These twenty maps act transitively on ordered distinct pairs and hence on
the ten unordered pairs. No transposition belongs to this group.
A nonidentity translation has no fixed point, and any affine map with
$\alpha\ne1$ has exactly one fixed point; a transposition has three.

The group generated by $c$ and $(0\ 1\ 2)$ lies in $A_5$.
It contains $(1\ 2\ 3)$ by conjugation with $c$.
Those two three-cycles fix $4$ and generate a transitive subgroup on the
other four points whose stabilizer of $0$ contains $(1\ 2\ 3)$.
Its order is at least $4\cdot3=12$, and at most $12$ by evenness.
Thus the full generated group has a point stabilizer of order at least
$12$; it is transitive by $c$, so its order is at least $60$.
It is therefore $A_5$.

Conjugating $(0\ 1)$ by powers of $c$ gives all successive
transpositions of the five-cycle. In particular, the adjacent
transpositions along the path $0,1,2,3,4$ generate $S_5$.
Both $A_5$ and $S_5$ are transitive on unordered pairs: any permutation
mapping one pair to another can have its parity corrected by swapping
two points outside the target pair.

Theorem 5.2 and Corollary 5.3 now give the counts.
The pair stabilizers have orders $20/10=2$, $60/10=6$, and
$120/10=12$. The kernel swap is absent from the first two groups and
present in the third. $\square$

### Theorem 6.2. Unsigned mobility, parity, and fused pairs do not suffice

For every $g\ge2$, the branches with
$\sigma_1(t)=2t$ and $\sigma_1=(0\ 1)$ have the same unsigned
labelled lane-exit graph, the same local parity at every lane, and the
same ten hittable source pairs. Nevertheless they have respectively two
and six survivor maps for each pair.

**Proof.** Lemma 3.1 makes the unsigned internal graph depend only on
$\pi$ and the lane partition: label $r$ is enabled at $C_j$ precisely
when $\pi(j)+r\not\equiv0\pmod g$, and its target lane is the unique
ordinary residue lane with that residue. The terminal labels are exactly
the complementary residues, again independent of $\sigma_j$.
Both branches have $\pi={\rm id}$, so these labelled graphs agree.

Multiplication by $2$ fixes $0$ and cycles the four nonzero indices;
it is odd, as is $(0\ 1)$. All other local restrictions in both branches
are identity, so the local parities agree lane by lane.
Proposition 6.1 gives all ten hittable pairs and the two distinct
survivor counts. Therefore this combined coarse summary does not determine
the complete survivor frontier. $\square$

### Theorem 6.3. Different reachable injections, equal survivor frontiers

For every $g\ge2$, the branches with
$\sigma_1=(0\ 1\ 2)$ and $\sigma_1=(0\ 1)$ have respectively
$60(g-1)$ and $120(g-1)$ reachable injections. For every source pair $F$,
their complete survivor sets nevertheless coincide: each is the set of
all six bijections

$$
 R_0\overset{\sim}{\longrightarrow}
       \{2\Delta,3\Delta,4\Delta\}.
 \tag{6.1}
$$

**Proof.** Proposition 6.1 identifies the groups as $A_5$ and $S_5$,
and Theorem 4.1 gives the injection counts. Fix any one of the six
survivor bijections. It has exactly two extensions to a permutation
sending $I_F$ to $\{0,1\}$, obtained by the two choices of kernel
ordering. They differ by $t_{01}$ and have opposite parity.
Exactly one lies in $A_5$, while both lie in $S_5$.
Theorem 5.2 realizes those extensions by actual terminal witnesses and
forgets their kernel ordering on restriction. Hence both groups give
every displayed survivor map and no others. $\square$

The two theorems express different directions of information loss.
The first rejects a specific coarse summary. The second shows that the
complete reachable injection set retains distinctions not visible in the
survivor frontier. Neither identifies a universally minimal sufficient
observable.

## Scope and Open Boundaries

Full occupancy is a theorem hypothesis. The support of every reachable
injection is an entire ordinary lane, so guard decisions are uniform and
the punctured lane is inaccessible internally. With partial occupancy,
holes can enable returns into the kernel residue lane, and the relocation
and confinement proofs above no longer supply a classification.

All words are unbudgeted. The inverse branch block and repeated generator
loops establish existence, not shortest paths or preservation of a length
or credit allowance. A budgeted variant requires its own proof.

The general survivor theorem is parameterized by the embedded group
$K_a\le S_5$ and its restriction map. The paper does not assert an
exhaustive five-stratum classification of subgroups containing $H$.
The cyclic, dihedral, affine, alternating, and symmetric specializations
are used only where their generation and restrictions have been justified.
Group orders alone are not survivor-frontier data.

The raw classification supplies neither a complete typed source nor
target-blind authorization, selector identity, declared transfer
membership, or typed handoff. Those are separate compatibility obligations
under existing semantics. No new forest semantics is a premise of the
results here, and no projectable-origin or recursive-settlement conclusion
is inferred.

## Computational Artifacts

The paper-owned evidence package is under `experiments/paper37/` in the
[RIME repository](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper37).
Paths below are relative to this directory.

The control includes all 120 ordinary-lane restrictions at $g=2$ with
punctured identity, and 96 explicitly selected branches with 192 source
cases at $g=3$. Matched controls are separately replayed at $g=2,3,4$.
These are bounded consistency controls, not proofs of the all-$g$ theorems.

| Surface | Location | Role |
|---|---|---|
| Control | `ordinary_lane_audit.py`, `results/ordinary_lane_audit_v1.json` | bounded source-addressed replay |
| Lean | `lean/Paper37.lean`, `lean/formalization-manifest.json` | partial implication spine |
| Validation | `validation/validate_release.py` | source binding and finite replay |
| Evidence | `development-manifest.json` | exact 22-artifact nested closure |
| Release | `release-manifest.json` | PDF, source, and environment binding |
| Receipt | `results/` | downstream local closure check |

The partial Lean spine formalizes word composition, conditional control
reduction, phase-state equivalence and normalization, survivor restriction
multiplicity, and the algebraic $A_5/S_5$ projection equality. The concrete
guard, confinement, relocation words, and terminal-placement converse remain
manuscript proofs and explicit inputs to the formal reduction.

The receipt records local closure verification and finite replay, not a
fresh Lean compilation or independent mathematical validation.

## Claim Status and Boundary

| Claim | Status |
|---|---|
| Lemmas 3.1--3.3: uniform edges and actual relocation/generator words | proved for full ordinary lanes |
| Theorem 4.1: complete reachable injections | proved for all $g\ge2$ in the declared regime |
| Corollary 4.2: lane-by-phase-coset state set | proved as a set bijection; no quotient-group claim |
| Proposition 4.3: deterministic labelled phase condition | proved under the exact local normalizer condition |
| Corollary 4.4: cyclic/dihedral recovery | proved specialization |
| Theorems 5.1--5.2 and Corollary 5.3: terminal and survivor classification | proved with actual witnesses and exact restriction multiplicity |
| Proposition 6.1 and Theorems 6.2--6.3: matched symbolic controls | proved for all $g\ge2$; not finite certificates |
| Fixed $g=2$ slice, selected $g=3$ catalogue, and matched $g=2,3,4$ replay | bounded consistency controls; not all-$g$ proofs |
| Lean word/control, phase, and restriction spine | partial formalization; geometric inputs remain explicit |
| Partial occupancy and budgeted paths | open; not classified |
| Exhaustive subgroup taxonomy | not claimed |
| Existing-semantics typed alignment, projectability, settlement, reset bounds | outside the theorem surface |

## Conclusion

In the full ordinary-lane regime, actual guarded relocation words turn
arbitrary local branch restrictions into controllable generators at every
ordinary lane. Their group gives exactly the reachable source-labelled
injections and the actual terminal placements. Restriction of a single
terminal permutation then gives the complete survivor frontier.

Phase may be removed at the level of the reachable state set, but
deterministic labelled phase descent requires normalization of the phase
group by each local restriction. Survivor projection has its own loss of
information: unsigned mobility, parity, and pair coverage can be too coarse,
whereas different complete reachable state spaces can still have identical
survivor frontiers. These are scoped raw statements, not typed recursive
compatibility or reset estimates.

## References {.unnumbered}
