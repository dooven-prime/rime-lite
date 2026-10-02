# Signed Lane-Exit Graphs and Complete Survivor Frontiers
### Phase Descent in Full Ordinary-Lane Five-Token Dynamics

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXVI | Version 1.0**

*This paper (Paper XXXVI of the RIME program) studies intrinsic raw survivor
incidence in a declared multi-lane regime. It does not assert typed transfer
membership, projectability, recursive compatibility, credit settlement, or a
reset bound.*

---

## Abstract

**Problem.** A spectator-safe fused-pair witness does not determine the
placements of the three surviving source lineages. In multiple arithmetic
lanes, a compressed mobility graph must also support a single concrete
guarded path through its internal transitions and terminal exit.

**Approach.** The analysis uses normalized returns
$\phi_r^{(a)}=\varepsilon_\Delta p^r a$ with $n=5g$, $\Delta=g$, and $g\ge2$.
The source fills an ordinary five-point lane. The branch stabilizes the lane
partition and restricts to a cycle-graph isomorphism between ordinary lanes;
its action on the four-point punctured lane is unrestricted. Full ordinary
lanes are invariant under guarded returns. Their edge guards are uniform
over all source-labelled representatives, and globally enabled return blocks
realize every within-lane phase.

**Results.** Quotienting reachable injections by phase gives exactly the
reachable internal vertices of a signed lane graph. Its state is a lane
together with source-relative orientation. Each boundary edge can be
realized, on a genuinely reachable phase representative, with any prescribed
source-consecutive pair at the terminal kernel. Consequently, a consecutive
pair has precisely one survivor injection for each reachable exit sign:
the three survivors occupy $(2\Delta,3\Delta,4\Delta)$ in source order for
positive sign, and $(4\Delta,3\Delta,2\Delta)$ for negative sign.
Nonconsecutive pairs have no strict-exit witness. An all-$g$ matched family
has identical unsigned labelled lane graphs and fused-pair spectra but
different survivor spectra.

**Boundary.** Phase can be removed from the unbudgeted reachability state,
whereas unsigned lane data cannot determine the complete raw frontier.
This is a scoped sufficiency and non-descent theorem, not a classification
of the full lane stabilizer or a universal minimality assertion.

**Keywords.** circular automata; single-defect dynamics; packet lineages;
signed graphs; phase quotient; guarded reachability; survivor incidence

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/(5g)\mathbb Z$, $\Delta=g$ | labelled circular carrier and lane spacing |
| $p(q)=q+1$ | fixed full cycle |
| $E=Q\setminus\{0\}$ | normalized section carrier |
| $\varepsilon_\Delta$ | collapse $0\mapsto\Delta$, fixing every other point |
| $K_\Delta=\{0,\Delta\}$ | terminal collision pair |
| $C_\ast$ | four-point punctured lane |
| $C^{(j)}$, $\mathcal C_\Delta^{(5)}$ | ordinary lanes and their collection |
| $\widehat C_\ast$ | full five-point pre-collapse kernel lane |
| $\rho_C$ | positive $\Delta$-rotation of a five-point lane |
| $a$ | lane-stabilizing branch, locally dihedral on ordinary lanes |
| $\phi_r^{(a)}$ | normalized guarded return of label $r$ |
| $T_0=\{q_0,\ldots,q_4\}$ | fixed source-lineage labels in positive source order |
| $\lambda_0$, $C_{\rm src}$ | source injection and its ordinary lane |
| $\mathcal L_a(\lambda_0)$ | injections reachable by actual guarded paths |
| $\sim_{\rm ph}$ | equivalence by within-lane phase rotation |
| $\widetilde\Gamma_a^{\rm ori}$ | signed lift of the lane-exit graph |
| $\operatorname{ExitOri}_a(C_{\rm src})$ | reachable boundary signs |
| $\mathcal W_a(\lambda_0;F,\mu)$ | terminal witness fiber |
| $\mathfrak S_a(\lambda_0;F)$ | source-addressed survivor spectrum |

## Introduction

A raw strict exit records more than the pair that fuses. It also records the
coordinates of every surviving source lineage. Forgetting those placements
can make distinct strict-exit frontiers indistinguishable at the fused-pair
level. Paper XXXIV establishes this separation in a one-lane dihedral
family [@paper34].

Paper XXXV goes further within one lane: for arbitrary branch permutations,
reachable cyclic orders determine the complete raw survivor frontier and
terminal phases [@paper35]. The present paper instead addresses mobility
between ordinary lanes, where phase compression must preserve a single
concrete witness along the entire path.

The multi-lane problem adds a witness issue. An existential transition
between two coarse classes cannot generally be composed with another such
transition: the outgoing edge may require a representative different from
the one actually reached. Paper XXXIII therefore retains source-addressed
intermediate incidence rather than an unrestricted Boolean composition of
orbit edges [@paper33]. A positive compression theorem must discharge this
representative mismatch, not merely hide it.

This paper gives such a theorem in a capacity-isolated regime. Fix
$n=5g$, $\Delta=g$, and a source occupying an entire ordinary five-point
lane. The punctured lane has only four points, so it cannot receive the
complete source under an injective return. Assume that each ordinary-lane
restriction of the branch is a rotation or reflection. Then every internal
lane edge is enabled on its entire representative fiber, and its orientation
law is uniform. A finite-order return block supplies all five phases by
actual guarded paths.

The correct compressed state is not the lane alone, but the lane together
with source-relative orientation. The paper proves three statements.

1. Reachable injections modulo phase are exactly reachable signed lane
   vertices, with uniform edgewise lifting from the same representative.
2. Reachable boundary signs determine the complete source-addressed survivor
   frontier, including the converse construction of every claimed incidence.
3. Unsigned labelled graphs do not suffice: an explicit all-$g$ pair of
   branches has the same unsigned graph and pair spectrum, but one versus
   two survivor injections for every consecutive source pair.

The argument is data-independent. The normalized action law is inherited
from the branch-coordinate framework [@paper30; @paper31], but all geometric
and witness-lifting statements used here are proved below.

### Related Work and Novelty Boundary

Order-preserving automata and their synchronization algorithms are classical.
Eppstein studies reset sequences for automata whose transitions respect a
cyclic ordering [@eppstein1990]. Circular automata also belong to the
established reset-bound literature [@dubuc1998]. The question here is instead
the unbudgeted first-exit incidence of five fixed source lineages: every
internal step remains injective on their complete support, and the terminal
event identifies exactly a prescribed source pair.

Almost-group automata with one defect-one letter and permutation letters
are a closely related ambient class. Casas Torres studies complete
reachability, including transitive imprimitive permutation groups
[@casasTorres2024]. Complete reachability concerns support images; the
present theorem retains source-labelled orientation and all three survivor
coordinates on one guarded witness. No complete-reachability characterization
is claimed.

Synchronization under dynamic constraints studies constraints on the order
in which words traverse states [@wolf2020]. Here the constraint is injectivity
on the five-point occupied support at every internal return, followed by a
specified source-marked collision. The signed graph is an exact quotient
proved for this declared full-lane regime, not a general reduction for
constrained synchronization.

Within the RIME line, Paper XXX supplies universal section symmetries;
Paper XXXI normalizes partial returns; Paper XXXIII identifies a
four-versus-five capacity obstruction; Paper XXXIV separates pair and
survivor observables; and Paper XXXV completes the arbitrary-branch one-lane
raw frontier through cyclic-order reachability and terminal-phase collapse
[@paper30; @paper31; @paper33; @paper34; @paper35]. The contribution here is
the multi-lane local-dihedral signed quotient, uniform same-witness path
lifting, a complete survivor theorem, and a matched symbolic obstruction to
unsigned descent. The proofs do not assume a typed recursive-return theorem.

## Normalized System and Full-Lane Regime

### Action and Reachability

Throughout,

$$
 n=5g,\qquad \Delta=g,\qquad g\ge2,\qquad
 Q=\mathbb Z/n\mathbb Z,\qquad E=Q\setminus\{0\}.
 \tag{2.1}
$$

Set $p(q)=q+1$ and

$$
 \varepsilon_\Delta(q)=
 \begin{cases}
 \Delta,&q=0,\\
 q,&q\ne0.
 \end{cases}
 \qquad K_\Delta=\{0,\Delta\}.
 \tag{2.2}
$$

The $\Delta$-lane partition of $E$ consists of

$$
 \begin{aligned}
 C_\ast&=\{\Delta,2\Delta,3\Delta,4\Delta\},\\
 C^{(j)}&=\{j+t\Delta:t\in\mathbb Z/5\mathbb Z\},
               &&1\le j\le g-1,\\
 \mathcal C_\Delta^{(5)}&=\{C^{(1)},\ldots,C^{(g-1)}\},\\
 \widehat C_\ast&=\{0,\Delta,2\Delta,3\Delta,4\Delta\}.
 \end{aligned}
 \tag{2.3}
$$

On every ordinary lane and on $\widehat C_\ast$, positive rotation is
$\rho_C(q)=q+\Delta$.

Fix a permutation $a$ of $E$ stabilizing this partition. For each ordinary
lane, require

$$
 a(C)=C',\qquad
 a\rho_C=\rho_{C'}^{\,\chi_C}a\quad\hbox{on }C,\qquad
 \chi_C\in\{+1,-1\}.
 \tag{2.4}
$$

Thus $a|_C$ is a five-cycle graph isomorphism. Its restriction to $C_\ast$
is arbitrary. This is the **full ordinary-lane local-dihedral regime**;
neither normalizer membership nor a common multiplier is assumed.

The return of label $r\in Q$ is

$$
 \phi_r^{(a)}=\varepsilon_\Delta\circ p^r\circ a.
 \tag{2.5}
$$

Composition is right-to-left: a label first applies $a$, then $p^r$, then
$\varepsilon_\Delta$. A path with labels $r_1,\ldots,r_k$ applies them in
that listed order. Labels are normalized return labels, not individual
original-automaton letters.

Let $T_0$ be five fixed source labels, and fix an injection
$\lambda_0:T_0\hookrightarrow E$ whose image is an ordinary lane
$C_{\rm src}$. Write $q_0,\ldots,q_4$ in the positive cyclic order induced
by $\lambda_0$; source subscripts are modulo $5$.

A return from $\lambda$ is enabled exactly when $\phi_r^{(a)}$ is injective
on $\lambda(T_0)$. Equivalently,

$$
 K_\Delta\nsubseteq p^r a(\lambda(T_0)).
 \tag{2.6}
$$

Write $\mathcal L_a(\lambda_0)$ for the injections reachable by finite
enabled paths, including the empty path. No length budget is imposed.

### Terminal Witnesses

Fix $F\subset T_0$ of size two and $R_0=T_0\setminus F$. A formal
pre-collapse placement is an injection $\mu:T_0\hookrightarrow Q$ with
$\mu(F)=K_\Delta$. Define

$$
 \mathcal W_a(\lambda_0;F,\mu)=
 \left\{(u,\lambda):
 \begin{array}{l}
 u\in Q\setminus\mu(T_0),\\
 \lambda\in\mathcal L_a(\lambda_0),\\
 \lambda=a^{-1}p^{-u}\mu
 \end{array}\right\}.
 \tag{2.7}
$$

The hole condition makes the pullback well typed in $E$. Its projection
onto $u$ is the phase fiber $\Phi_a(\lambda_0;F,\mu)$.

**Proposition 2.1 (exact terminal pullback).** A formal placement $\mu$ is
attainable by a guarded prefix and one terminal strict return if and only if
$\mathcal W_a(\lambda_0;F,\mu)\ne\varnothing$. For fixed $\mu$, projection
onto $u$ is a bijection from $\mathcal W_a$ to $\Phi_a$.

**Proof.** An actual terminal call has
$\mu=p^u a\lambda$ with $\lambda$ reachable. Since
$p^{-u}\mu(T_0)=a(\lambda(T_0))\subseteq E$, its terminal hole satisfies
$u\notin\mu(T_0)$. Inverting the two bijections gives the pullback in
(2.7). Conversely, every pair in (2.7) gives $\mu=p^u a\lambda$ after an
actual guarded prefix. The injection $\mu$ puts precisely the two labels
of $F$ at $0,\Delta$, so the final collapse has rank four. The pullback is
unique for fixed $(\mu,u)$, proving the projection assertion. $\square$

The resulting strict incidence is

$$
 \beta_\mu(q)=
 \begin{cases}
 \Delta,&q\in F,\\
 \mu(q),&q\in R_0.
 \end{cases}
 \tag{2.8}
$$

Define

$$
 \begin{aligned}
 \mathfrak S_a(\lambda_0;F)
 &=\{\mu|_{R_0}:\mu(F)=K_\Delta,\
                 \mathcal W_a(\lambda_0;F,\mu)\ne\varnothing\},\\
 \mathfrak F_a(\lambda_0)
 &=\{F:|F|=2,\ \mathfrak S_a(\lambda_0;F)\ne\varnothing\}.
 \end{aligned}
 \tag{2.9}
$$

If fixed nonempty disjoint source blocks are supplied, (2.8) reconstructs
the packet endpoint by placing each surviving block at its own coordinate
and the union of the two fused blocks at $\Delta$. No block mass, role, or
ancestry field enters the present dynamics.

## Signed Phase Descent

### Uniform Edge Laws and Actual Phase Control

**Lemma 3.1 (full-lane invariance and uniform lifting).** Suppose
$a(C^{(j)})=C^{(j')}$ and let $h\equiv j'+r\pmod g$, with
$0\le h\le g-1$. The label $r$ is disabled on every injection filling
$C^{(j)}$ when $h=0$. When $h\ne0$, it is enabled on every such injection,
maps it onto $C^{(h)}$, and has sign $\chi_{C^{(j)}}$.

For the enabled restriction $f:C\to C'$, every phase $k$ satisfies

$$
 f\rho_C^k=\rho_{C'}^{\,\chi_C k}f.
 \tag{3.1}
$$

**Proof.** If $h=0$, the full set $p^r a(C^{(j)})$ is
$\widehat C_\ast$. It contains the two collision points, so the collapse
is not injective. If $h\ne0$, this full set is $C^{(h)}$, which avoids
$0$. The collapse is the identity there, and the restriction is
$p^r a|_{C^{(j)}}$. Translation preserves positive $\Delta$-orientation,
so (2.4) gives its sign and (3.1). The guard reads only the full support,
not the representative filling it. Composition with any bijection
$T_0\to C$ therefore gives a legal injection onto $C'$. $\square$

In particular, every reachable source state still fills an ordinary lane.
The four-point punctured lane is never an internal destination.

**Lemma 3.2 (actual phase saturation).** If $\lambda$ is reachable and fills
$C$, every $\rho_C^k\lambda$ is reachable.

**Proof.** Let $m=\operatorname{ord}(a)$ and put
$\psi_\Delta=\varepsilon_\Delta p^\Delta|_E$. This is a permutation of
$E$: $p^\Delta(E)$ omits $\Delta$, and the collapse replaces its point
$0$ by that missing point. Thus

$$
 \phi_0^{(a)}=a,\qquad
 \phi_\Delta^{(a)}=\psi_\Delta a
 \tag{3.2}
$$

are globally enabled on injections into $E$. The actual label block
consisting of $m-1$ zeros followed by $\Delta$ implements

$$
 \phi_\Delta^{(a)}(\phi_0^{(a)})^{m-1}
       =\psi_\Delta a^m=\psi_\Delta.
 \tag{3.3}
$$

Every intermediate step is enabled. On an ordinary lane,
$\psi_\Delta|_C=\rho_C$. Repeating this block realizes all five phases.
This proves saturation by actual paths, not by a formal symmetry
identification. $\square$

### The Signed Graph

The base graph $\Gamma_a^{\rm ori}$ has ordinary-lane vertices and a
boundary vertex $\partial$. Its internal and boundary edges are

$$
 \begin{aligned}
 C\xrightarrow{\,r,\chi\,}C'
 &\quad\Longleftrightarrow\quad
   \phi_r^{(a)}|_C:C\to C'\text{ is bijective of sign }\chi,\\
 C\xrightarrow{\,u,\chi_\partial\,}\partial
 &\quad\Longleftrightarrow\quad
   p^u a(C)=\widehat C_\ast
   \text{ with pre-collapse sign }\chi_\partial.
 \end{aligned}
 \tag{3.4}
$$

These are different edge types: a boundary exponent ends the path with a
strict collision, not another enabled internal return.

The **signed lift** $\widetilde\Gamma_a^{\rm ori}$ has internal vertices
$(C,\sigma)$ and boundary vertices $(\partial,\sigma)$, with
$\sigma\in\{+1,-1\}$. It lifts the edges as

$$
 \begin{aligned}
 (C,\sigma)&\xrightarrow{\,r\,}(C',\sigma\chi),\\
 (C,\sigma)&\xrightarrow{\,u\,}(\partial,\sigma\chi_\partial).
 \end{aligned}
 \tag{3.5}
$$

Set

$$
 \operatorname{ExitOri}_a(C_{\rm src})
 =\{\chi:(C_{\rm src},+1)\leadsto(\partial,\chi)
                  \text{ in }\widetilde\Gamma_a^{\rm ori}\}.
 \tag{3.6}
$$

The source-relative orientation of a reachable injection is positive when
its cyclic label order is $(q_0,\ldots,q_4)$, and negative when that order is
reversed. Lemma 3.1 shows that these are the only two possible orders.
For a fixed base point $c_C\in C$, such an injection has the form

$$
 \lambda(q_i)=\rho_C^{\,b+\sigma i}(c_C),
 \qquad b\in\mathbb Z/5\mathbb Z,\quad \sigma\in\{+1,-1\}.
 \tag{3.7}
$$

Define $\lambda\sim_{\rm ph}\lambda'$ when they have the same lane and
$\lambda'=\rho_C^k\lambda$ for some $k$.

**Theorem 3.3 (signed phase descent).** The map

$$
 [\lambda]_{\rm ph}\longmapsto
       \bigl(\lambda(T_0),\operatorname{sgn}_{\lambda_0}(\lambda)\bigr)
 \tag{3.8}
$$

is a bijection

$$
 \mathcal L_a(\lambda_0)/{\sim_{\rm ph}}
 \ \cong\
 \operatorname{Reach}^{\rm int}_{\widetilde\Gamma_a^{\rm ori}}
                  (C_{\rm src},+1).
 \tag{3.9}
$$

It is an isomorphism of the reachable phase-quotient transition graph with
the reachable internal signed graph, including return labels and disabled
labels. Every finite internal signed path lifts, edge by edge, from the same
concrete initial representative.

**Proof.** Project an actual guarded path. Lemma 3.1 keeps its support in
ordinary lanes and updates its source sign exactly as (3.5). This gives a
signed path and proves that the map in (3.8) takes values in the right-hand
side.

Conversely, let a signed path have labels $r_1,\ldots,r_k$. Starting with
the given $\lambda_0$, define recursively
$\lambda_i=\phi_{r_i}^{(a)}\lambda_{i-1}$. Each edge is enabled on every
injection filling its incoming lane by Lemma 3.1. In particular it is
enabled on the representative just produced by the previous edge.
Induction supplies one actual path with the required support and sign.
This proves surjectivity without choosing independent edge witnesses.

Two reachable injections with the same lane and sign have the same cyclic
label order and differ only by $b$ in (3.7), hence are phase equivalent.
Opposite signs cannot be phase equivalent for five distinct labels.
Lemma 3.2 supplies every representative of each reachable phase class.
Finally, enabledness is support-dependent, and (3.1) makes the output phase
class independent of the incoming representative. These facts prove the
transition-graph assertion. $\square$

The quotient has at most $2(g-1)$ internal vertices and the reachable
injection set has at most $10(g-1)$ elements. This does not preserve the
cost of reaching a particular phase: phase control may insert the blocks
in (3.3). No shortest-word or fixed-endpoint word claim follows.

## Boundary Realization and Complete Survivor Frontier

### Phase-Complete Boundary Lifting

**Lemma 4.1 (prescribed-pair boundary realization).** Let $(C,\sigma)$ be
reachable, let $b=p^u a|_C:C\to\widehat C_\ast$ be a fixed boundary edge of
sign $\chi_\partial$, and fix a source-consecutive pair
$F=\{q_i,q_{i+1}\}$. Within any reachable incoming phase fiber, exactly one
phase puts $F$ at $K_\Delta$ through this same exponent $u$. The resulting
terminal witness has sign $\sigma\chi_\partial$.

**Proof.** Choose a reachable incoming $\lambda$ from Theorem 3.3. Every
$\lambda^{(k)}=\rho_C^k\lambda$ is reachable by Lemma 3.2. Writing
$\widehat\rho(q)=q+\Delta$ on $\widehat C_\ast$, we have

$$
 \mu^{(k)}=b\lambda^{(k)}
       =\widehat\rho^{\,\chi_\partial k}(b\lambda).
 \tag{4.1}
$$

All five placements have the same sign $\sigma\chi_\partial$. The image
of a source-consecutive pair is an edge of the target five-cycle.
Its five rotations are distinct and exhaust the target edges. Exactly
one is $K_\Delta$, which selects a unique $k_F$.

Put $\lambda_F=\lambda^{(k_F)}$ and $\mu_F=p^u a\lambda_F$.
The same placement verifies the fused pair, orientation, and all survivor
coordinates. Moreover,
$p^{-u}\mu_F(T_0)=a(C)\subseteq E$, so
$u\notin\mu_F(T_0)$. Hence $(u,\lambda_F)$ belongs to the witness fiber
(2.7). Concatenating the actual incoming path, the phase-control block,
and the terminal return gives a single complete witness. $\square$

This uniqueness is for the chosen phase fiber and chosen boundary exponent;
it does not assert uniqueness of all paths or all terminal witnesses.

### Terminal Rigidity

For a sign $\chi$, let $\mathfrak S_\Delta^\chi(F)$ be the survivor
restrictions of bijections
$\mu:T_0\to\widehat C_\ast$ such that
$\mu(F)=K_\Delta$ and $\mu$ has source-relative sign $\chi$.

**Lemma 4.2 (terminal rigidity).** A nonconsecutive pair has no such
placement. For $F=\{q_i,q_{i+1}\}$ there is exactly one placement of each
sign:

$$
 \begin{aligned}
 \mu_F^+(q_{i+t})&=t\Delta,\\
 \mu_F^-(q_{i+t})&=(1-t)\Delta,
                    &&t\in\mathbb Z/5\mathbb Z.
 \end{aligned}
 \tag{4.2}
$$

Consequently, on the ordered survivor labels
$(q_{i+2},q_{i+3},q_{i+4})$,

$$
 s_F^+=(2\Delta,3\Delta,4\Delta),\qquad
 s_F^-=(4\Delta,3\Delta,2\Delta).
 \tag{4.3}
$$

In particular, the two survivor injections are distinct.

**Proof.** Preserving or reversing the source order makes $\mu$ a
five-cycle graph isomorphism. The preimage of the target edge
$\{0,\Delta\}$ is therefore a source edge. For a consecutive $F$,
positive sign forces $q_i\mapsto0$, $q_{i+1}\mapsto\Delta$;
negative sign forces the reverse assignment. The rest of the cycle then
forces (4.2). Restricting gives (4.3), whose first coordinates differ.
$\square$

### Completion Theorem

**Theorem 4.3 (complete survivor frontier).** In the declared regime,

$$
 \mathfrak S_a(\lambda_0;F)=
 \begin{cases}
 \displaystyle\bigsqcup_{\chi\in\operatorname{ExitOri}_a(C_{\rm src})}
                   \mathfrak S_\Delta^\chi(F),
                   &F\text{ source-consecutive},\\
 \varnothing,      &F\text{ nonconsecutive}.
 \end{cases}
 \tag{4.4}
$$

The union is a disjoint union of actual survivor injections, not merely
of witnesses carrying different sign labels.

**Proof.** For the forward inclusion, choose an actual terminal witness
$(u,\lambda)$ and put $\mu=p^u a\lambda$. The reachable injection fills
an ordinary lane $C$ by Lemma 3.1. Its translated image is a full residue
class modulo $g$. Since $\mu(F)$ contains $0$, that class is
$\widehat C_\ast$. Thus $u$ defines a boundary edge from $C$.

The actual prefix projects by Theorem 3.3 to a signed path ending at
$(C,\sigma)$. Appending this boundary edge gives exit sign
$\chi=\sigma\chi_\partial$. The very same $\mu$ has this sign, puts $F$
at the kernel, and supplies the survivor restriction. Lemma 4.2 forces
$F$ to be consecutive and places its survivors in
$\mathfrak S_\Delta^\chi(F)$.

For the reverse inclusion, choose
$\chi\in\operatorname{ExitOri}_a(C_{\rm src})$ and a formal placement
$\mu$ contributing to $\mathfrak S_\Delta^\chi(F)$. Take a signed path
to this boundary vertex. Lift its internal part using Theorem 3.3,
and retain its fixed final boundary exponent $u$. Lemma 4.1 then gives
an actual reachable phase representative and a placement $\nu$ with
the prescribed pair and sign $\chi$. Both $\nu$ and $\mu$ fill
$\widehat C_\ast$ and have that same pair and sign. Lemma 4.2 implies
$\nu=\mu$. Thus the claimed survivor injection has an actual witness,
not only a formal terminal shape. Finally, (4.3) proves disjointness.
$\square$

**Corollary 4.4 (explicit incidence spectrum).** The fused-pair spectrum is
exactly

$$
 \mathfrak F_a(\lambda_0)=
       \{\{q_i,q_{i+1}\}:i\in\mathbb Z/5\mathbb Z\}.
 \tag{4.5}
$$

For each such $F$, its survivor spectrum consists of $s_F^+$ if positive
exit sign is reachable, $s_F^-$ if negative exit sign is reachable, and
both if both are reachable. In particular,

$$
 |\mathfrak S_a(\lambda_0;F)|
       =|\operatorname{ExitOri}_a(C_{\rm src})|\in\{1,2\}.
 \tag{4.6}
$$

**Proof.** A boundary exponent exists directly from $C_{\rm src}$:
translate its image under $a$ to residue zero modulo $g$.
Hence the exit-sign set is nonempty. Apply Theorem 4.3 and Lemma 4.2.
$\square$

Writing $\beta_F^\chi=\varepsilon_\Delta\mu_F^\chi$, the complete
strict-incidence spectrum is

$$
 \begin{aligned}
 \mathfrak B_a(\lambda_0)
 &=\{\beta_F^\chi:F\text{ consecutive},\
              \chi\in\operatorname{ExitOri}_a(C_{\rm src})\},\\
 |\mathfrak B_a(\lambda_0)|
 &=5|\operatorname{ExitOri}_a(C_{\rm src})|\in\{5,10\}.
 \end{aligned}
 \tag{4.7}
$$

Indeed, $\beta^{-1}(\Delta)$ recovers its fused source pair and (4.3)
distinguishes the two signs for that pair. All incidences have output
support $\{\Delta,2\Delta,3\Delta,4\Delta\}$. Their source-addressed
differences are not visible from that common support.

## Unsigned Lane Data Do Not Descend

The unsigned graph retains lanes, internal return labels and guards,
boundary exponents, and the source lane, but forgets every orientation sign.
The following obstruction preserves this full unsigned data, not merely
unlabelled connectivity.

**Theorem 5.1 (all-$g$ unsigned non-descent).** For every $g\ge2$, there are
two branches in the declared regime which, for the same source injection,
have identical unsigned labelled lane-exit graphs and identical fused-pair
spectra, but different survivor spectra for every consecutive source pair.

**Proof.** Let $a_+=\operatorname{id}_E$. Define $a_-$ to fix $C_\ast$
pointwise and reflect every ordinary lane:

$$
 a_-(j+t\Delta)=j-t\Delta,
 \qquad 1\le j\le g-1,\quad t\in\mathbb Z/5\mathbb Z.
 \tag{5.1}
$$

Both branches fix each lane setwise. Lemma 3.1 gives their common unsigned
internal rule:

$$
 \begin{aligned}
 C^{(j)}\xrightarrow{\,r\,}C^{(h)}
 &\quad\Longleftrightarrow\quad
 h\equiv j+r\pmod g,\quad h\ne0,\\
 C^{(j)}\xrightarrow{\,u\,}\partial
 &\quad\Longleftrightarrow\quad
 j+u\equiv0\pmod g.
 \end{aligned}
 \tag{5.2}
$$

Thus every enabled label, disabled label, target lane, and boundary
exponent agrees. For $a_+$ every edge sign is positive, so its exit-sign
set is $\{+1\}$. For $a_-$ every ordinary-lane internal and boundary
edge is negative. A direct boundary edge from the source gives negative
exit sign. The globally enabled label-zero return $a_-$, followed by
the same boundary exponent, gives positive exit sign. These are actual
paths from the same source, so

$$
 \operatorname{ExitOri}_{a_+}(C_{\rm src})=\{+1\},\qquad
 \operatorname{ExitOri}_{a_-}(C_{\rm src})=\{+1,-1\}.
 \tag{5.3}
$$

Theorem 4.3 supplies the prescribed-pair witnesses, giving

$$
 \begin{aligned}
 \mathfrak S_{a_+}(\lambda_0;F)&=\{s_F^+\},\\
 \mathfrak S_{a_-}(\lambda_0;F)&=\{s_F^+,s_F^-\}
                   &&(F\text{ consecutive}).
 \end{aligned}
 \tag{5.4}
$$

Both pair spectra are the five source edges by Corollary 4.4, whereas
the two survivor injections in (5.4) are distinct. This proves the
matched all-$g$ obstruction. $\square$

Thus no rule depending only on this unsigned labelled graph and source
pair data can reconstruct the survivor frontier throughout the declared
regime. The theorem establishes insufficiency of the unsigned observable;
it does not claim that a sign bit is a universally minimal invariant.

## Scope and Open Boundaries

The proofs use two specific hypotheses. First, the source fills a five-point
ordinary lane, while the punctured lane has capacity four. Without complete
lane occupancy, the uniform support guard and capacity isolation no longer
give the present graph. Second, ordinary-lane branch restrictions preserve
or reverse cycle order. General stabilizer restrictions can produce cyclic
orders other than the two carried by the signed lift.

The declared theorem does not classify those larger state spaces. Nor does
it classify the terminal phase fiber for arbitrary formal placements:
phase saturation within an ordinary lane is not an all-hole phase-collapse
theorem across lanes. The terminal construction here retains the actual
boundary exponent and its selected reachable representative.

There is also a length boundary. Realizing a phase may use multiple
globally enabled returns. The signed graph determines unbudgeted raw
reachability and survivor incidence, not shortest words, a credit inequality,
or an admissible settlement schedule.

Finally, normalized raw incidence is not typed transfer membership.
Authorization, ancestry, fixed transfer bindings, and typed handoffs are
not fields of the present injection system. Any raw-to-typed bridge must
supply its own same-witness theorem under existing semantics. Neither the
positive frontier theorem nor the unsigned obstruction resolves
Projectable-Origin Supply, recursive compatibility, or reset bounds.

## Computational Artifacts

The evidence package is under `experiments/paper36/` in the
[RIME repository](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper36).
Paths below are relative to this directory.

| Surface | Location | Role |
|---|---|---|
| Control | `signed_lane_audit.py` | exhaustive $g=2,3$ branch and source-case checks |
| Result | [audit JSON](https://github.com/dooven-prime/rime-lite/blob/master/experiments/paper36/results/signed_lane_audit_v1.json) | bounded source-addressed survivor controls |
| Validation | `validation/validate_package.py` | source binding and separately implemented finite replay |

These finite controls check consistency in the declared domains; they do not
prove the all-$g$ theorems. The theorem statements and proofs in this
manuscript remain authoritative.

## Claim Status and Boundary

| Claim | Status |
|---|---|
| Proposition 2.1: exact terminal pullback | algebraic proof for the declared witness type |
| Lemmas 3.1--3.2: uniform guard and phase saturation | data-independent proofs for all $g\ge2$ |
| Theorem 3.3: signed phase descent | exact reachable transition quotient in the full ordinary-lane local-dihedral regime |
| Lemmas 4.1--4.2: boundary lifting and rigidity | actual prescribed-pair witness and unique incidence per sign |
| Theorem 4.3 / Corollary 4.4: complete survivor frontier | both inclusions, disjointness, and pair spectrum proved |
| Theorem 5.1: unsigned non-descent | explicit matched family for every $g\ge2$ |
| Full stabilizer, partial lane occupancy, length budgets | not classified |
| Typed transfer, projectability, recursion, settlement | outside the theorem surface |

## Conclusion

In the declared full ordinary-lane regime, a reachable injection can be
compressed to its lane and source-relative orientation. Uniform edge guards
permit an entire graph path to lift from one concrete representative, and
actual phase control realizes every prescribed consecutive pair at a fixed
boundary edge. The reachable exit signs then determine the placements of
all three survivors.

The matched reflection family shows why the unsigned graph is too coarse:
it preserves all labelled lane mobility and pair-hitting data but changes
the complete survivor frontier. Phase can be removed from the compressed
reachability state; orientation cannot be discarded from this observable
without losing incidence information. These conclusions remain raw,
multi-lane, hypothesis-explicit, and independent of recursive or reset-bound
claims.

## References {.unnumbered}
