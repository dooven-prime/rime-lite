# Source-Addressed Stabilizer Descent in Five-Token Return Dynamics
### Orbit Incidence and Capacity-Isolated Order Breaking

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXIII | Version 1.0**

*This paper (Paper XXXIII of the RIME program) studies intrinsic raw
spectator-safe return dynamics in the full lane-partition stabilizer. It
imports the normalized partial-return system and lane-stabilizer boundary of
Paper XXXII, but no typed transfer, projectability, recursive-return,
credit-settlement, or reset-bound conclusion.*

---

## Abstract

**Problem.** Paper XXXII proves that every permutation preserving the
arithmetic-lane partition satisfies

$$
\operatorname{LaneAdj}_{\Delta}
\Longrightarrow
\operatorname{SafeHit}_{a}
\Longrightarrow
\operatorname{SameLane}_{\Delta}.
$$

Outside the normalizer of the universal return cycle, however, the branch
permutation does not induce a deterministic map on return orbits. Separate
existential orbit edges also cannot be composed without retaining the same
intermediate state.

**Approach.** For universal-return orbits \(O,O'\), we introduce the
source-addressed incidence

$$
\mathcal I_a(O,O')=a_\#(O)\cap O'.
$$

This set of concrete states gives an exact factorization of every stabilizer
return. Choosing one representative per orbit further compresses the
incidence to a finite cyclic phase set while preserving the intermediate
witness.

**Results.** The source-addressed factorization is exact for every branch
permutation. The paper then disproves the natural full-stabilizer promotion
claim

$$
\operatorname{Break}_{\Delta}(a)\ne\varnothing
\Longrightarrow
\operatorname{SafeHit}_{a}
=
\operatorname{SameLane}_{\Delta}.
$$

For every \(g\ge2\), take \(n=5g\) and \(\Delta=g\). The punctured lane has
capacity four and every ordinary lane has capacity five. A branch may break
cyclic order only on the punctured lane while fixing every ordinary lane.
A complete five-token context on an ordinary lane cannot enter the breaking
lane through any guarded return. The same-lane nonedge contexts on ordinary
lanes therefore form a forward-invariant, target-disjoint family.

**Boundary.** The obstruction does not prove that the break set itself fails
to determine Safe-Hit; that stronger non-descent claim requires matched
branches with equal retained summaries and different hit predicates. The
remaining positive problem is a same-witness, lane-type-sensitive mobility
theorem.

**Keywords.** synchronizing automata; single-defect automata; partial
dynamics; orbit incidence; same-witness descent; lane stabilizers; guarded
reachability

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| \(Q=\mathbb Z/n\mathbb Z\) | labelled circular carrier |
| \(p(q)=q+1\) | fixed full cycle |
| \(\Delta\) | oriented kernel separation |
| \(g=\gcd(n,\Delta)\) | number of arithmetic lanes before puncturing |
| \(\ell=n/g\) | full lane length |
| \(E=Q\setminus\{0\}\) | normalized branch carrier |
| \(\widehat\Sigma=\operatorname{Conf}_{2,3}(E)\) | two marked tokens and three spectators |
| \(\psi_\Delta\) | punctured rotation on \(E\) |
| \(H_\Delta=\langle\psi_\Delta\rangle\) | globally enabled cyclic return subgroup |
| \(\mathcal Z_\Delta=\widehat\Sigma/H_\Delta\) | universal-return orbit space |
| \(F_r^{(0)}\) | identity-branch partial return with label \(r\) |
| \(F_r^{(a)}\) | branch-\(a\) partial return |
| \(\mathcal C_\Delta\) | arithmetic-lane partition of \(E\) |
| \(\operatorname{Stab}(\mathcal C_\Delta)\) | full lane-partition stabilizer |
| \(\mathcal I_a(O,O')\) | concrete incidence \(a_\#(O)\cap O'\) |
| \(\Theta_a(O,O')\) | cyclic phases realizing that incidence |
| \(\operatorname{Break}_\Delta(a)\) | lanes on which \(a\) is not a cycle-graph isomorphism |

## Introduction

Papers XXIX--XXXII successively replace a historical transfer interface by
an intrinsic rank-five raw dynamical system. Paper XXIX identifies the exact
spectator-safe quotient and classifies the canonical frontier. Paper XXX
extracts the universal return group of a general binary-kernel defect. Paper
XXXI normalizes all partial returns into branch coordinates. Paper XXXII
classifies the complete single-lane branch space and isolates the full
lane-partition stabilizer as the maximal remaining lane-based regime
[@paper29; @paper30; @paper31; @paper32].

The inherited raw system has state space

$$
\widehat\Sigma
=
\operatorname{Conf}_{2,3}(E),
\tag{1.1}
$$

where two tokens are marked, three are spectators, and every other point is a
hole. The globally enabled punctured rotation

$$
\psi_\Delta
\tag{1.2}
$$

generates a cyclic group

$$
H_\Delta=\langle\psi_\Delta\rangle
\tag{1.3}
$$

on this state space.

For a normalizer branch \(a\), the action \(a_\#\) descends to a deterministic
permutation of

$$
\mathcal Z_\Delta=\widehat\Sigma/H_\Delta.
\tag{1.4}
$$

The normalized dynamics is then a deterministic orbit twist followed by an
identity-branch relation. The full stabilizer removes exactly this
convenience. A branch may carry every arithmetic lane to a lane while failing

$$
aH_\Delta a^{-1}=H_\Delta.
\tag{1.5}
$$

There is then no branch map on \(\mathcal Z_\Delta\).

The first task of this paper is to identify the exact replacement. The
replacement cannot be only a Boolean relation between orbits. If one
existential witness establishes that the branch reaches an intermediate
orbit and another establishes that an identity return leaves that orbit, the
two statements need not compose. The intermediate state must be shared.

This leads to the source-addressed incidence

$$
\mathcal I_a(O,O')=a_\#(O)\cap O'.
\tag{1.6}
$$

The object is small enough to be parameterized by one cyclic phase and rich
enough to preserve the same witness.

![Source-addressed orbit incidence retains one concrete intermediate witness
through the branch image and guarded identity return. Separate existential
orbit edges do not compose when they use different states.](../../figures/paper33/fig1_source_addressed_incidence.png){width=96%}

The second task is to determine whether one order-breaking lane already
promotes every same-lane context. It does not. The obstruction is geometric,
not merely algebraic: a breaking lane may be too short to receive the full
five-token context. This yields an all-\(g\) family with a nonempty break set
but a proper intermediate Safe-Hit set.

The theorem spine is:

1. Section 2 freezes the normalized branch system and the stabilizer
   sandwich inherited from Paper XXXII.
2. Section 3 proves exact source-addressed orbit descent.
3. Section 4 compresses concrete incidence to cyclic phase data.
4. Section 5 constructs the all-\(g\) capacity-isolation obstruction.
5. Section 6 states the refined same-witness mobility problem.

The work remains intrinsic and raw. It neither rebuilds typed transfer
authority nor imports downstream success into the return system.

### Related Work and Novelty Boundary

The Černý conjecture and the wider theory of synchronizing automata concern
short reset words [@cerny1964; @volkov2008; @volkov2022survey]. Circular,
almost-group, and completely reachable automata provide adjacent structural
settings [@dubuc1998; @berlinkovNicaud2020; @casasTorres2024;
@don2016; @gonzeJungers2018; @ferensSzykula2026]. This paper proves no reset
bound and no complete-reachability characterization.

Subset synchronization, careful synchronization, monotonicity, and dynamic
word constraints study related partial or order-sensitive behavior
[@eppstein1990; @ryzhikovShemyakov2018; @wolf2020]. The present state carries
a source-marked pair and three source-marked spectators. One guarded path must
keep all five lineages injective until the declared terminal incidence.

Within the RIME line, Papers XXIX--XXXII establish the raw rank-five frontier,
the universal return group, branch-normalized partial returns, and the
single-lane permutation dichotomy [@paper29; @paper30; @paper31; @paper32].
The new claims here are an exact same-witness descent object for the full
lane stabilizer and an all-\(g\) obstruction to promotion by break-set
nonemptiness.

## The Inherited Stabilizer System

Fix

$$
n\ge6,
\qquad
1\le\Delta\le n-1,
\qquad
g=\gcd(n,\Delta),
\qquad
\ell=\frac ng.
\tag{2.1}
$$

Put

$$
E=\mathbb Z/n\mathbb Z\setminus\{0\}.
\tag{2.2}
$$

The punctured rotation \(\psi_\Delta\) has one distinguished cycle
\(C_\ast\) and \(g-1\) ordinary cycles:

$$
\mathcal C_\Delta
=
\{C_\ast,C_1,\ldots,C_{g-1}\},
\tag{2.3}
$$

with

$$
|C_\ast|=\ell-1,
\qquad
|C_j|=\ell.
\tag{2.4}
$$

Let

$$
a\in\operatorname{Sym}(E)
\tag{2.5}
$$

be an arbitrary branch permutation.

For each label \(r\in\mathbb Z/n\mathbb Z\), Paper XXXI defines the
identity-branch partial point map

$$
\phi_r^{(0)}=\varepsilon_\Delta p^r,
\tag{2.6}
$$

and Paper XXXII extends it to the branch map

$$
\phi_r^{(a)}=\varepsilon_\Delta p^r a.
\tag{2.7}
$$

Push-forward to five-token states gives partial maps

$$
F_r^{(0)}
\quad\text{and}\quad
F_r^{(a)}
=
F_r^{(0)}\circ a_\#.
\tag{2.8}
$$

The domain guard is injectivity on the complete five-point support. The
target is the inherited branch-normalized marked-pair target. Safe-Hit means
reachability of that target through the declared partial maps.

Sections 3 and 4 retain the full scope \(a\in\operatorname{Sym}(E)\). Beginning
in Section 5, the paper restricts to

$$
a\in\operatorname{Stab}(\mathcal C_\Delta).
$$

Such a branch fixes the unique short lane setwise and permutes the ordinary
lanes, with arbitrary internal permutations. On this restricted scope, Paper
XXXII proves the full-stabilizer sandwich

$$
\boxed{
\operatorname{LaneAdj}_\Delta(x)
\Longrightarrow
\operatorname{SafeHit}_{a}(x)
\Longrightarrow
\operatorname{SameLane}_\Delta(x).
}
\tag{2.9}
$$

The restriction used for the obstruction theorem does not narrow the
algebraic factorization proved in Sections 3 and 4.

## Source-Addressed Orbit Descent

Let

$$
\pi_H:\widehat\Sigma\longrightarrow
\mathcal Z_\Delta
=
\widehat\Sigma/H_\Delta
\tag{3.1}
$$

be the universal-return orbit map. For orbits \(O,O'\), define

$$
\boxed{
\mathcal I_a(O,O')
:=
a_\#(O)\cap O'.
}
\tag{3.2}
$$

The values of \(\mathcal I_a\) are concrete normalized five-token states.

Define the direct branch edge by

$$
O\xrightarrow{r,a}O'
\tag{3.3}
$$

when there exists \(x\in O\) such that

$$
x\in\operatorname{Dom}(F_r^{(a)})
\quad\text{and}\quad
F_r^{(a)}(x)\in O'.
\tag{3.4}
$$

**Proposition 3.1 (exact source-addressed stabilizer descent).** For every
branch permutation \(a\), label \(r\), and orbits \(O,O'\),

$$
\boxed{
O\xrightarrow{r,a}O'
\iff
\exists O_1\in\mathcal Z_\Delta\;
\exists y\in
\mathcal I_a(O,O_1)\cap\operatorname{Dom}(F_r^{(0)}):
\quad
F_r^{(0)}(y)\in O'.
}
\tag{3.5}
$$

**Proof.** Suppose \(x\in O\) realizes the direct branch edge. Set

$$
y=a_\#x
\tag{3.6}
$$

and let \(O_1=\pi_H(y)\). Then

$$
y\in a_\#(O)\cap O_1
=
\mathcal I_a(O,O_1).
\tag{3.7}
$$

By (2.8),

$$
F_r^{(0)}(y)
=
F_r^{(a)}(x)
\in O'.
\tag{3.8}
$$

Conversely, let \(y\) satisfy the right side. Incidence supplies
\(x\in O\) with \(y=a_\#x\). The domain and image clauses then give
(3.4) by (2.8). \(\square\)

The concrete state \(y\) is essential. In general,

$$
\mathcal I_a(O,O_1)\ne\varnothing
\tag{3.9}
$$

and

$$
\exists z\in O_1\cap\operatorname{Dom}(F_r^{(0)}):
\quad F_r^{(0)}(z)\in O'
\tag{3.10}
$$

do not imply (3.5), because the incidence witness and the return witness may
be different.

## Cyclic Phase Compression

Let

$$
M=\operatorname{ord}(\psi_\Delta).
\tag{4.1}
$$

Choose one representative \(x_O\) for every \(O\in\mathcal Z_\Delta\).
Define the phase-incidence set

$$
\Theta_a(O,O_1)
=
\left\{
t\in\mathbb Z/M\mathbb Z:
\pi_H\!\left(
a_\#\psi_{\Delta,\#}^{\,t}x_O
\right)=O_1
\right\}.
\tag{4.2}
$$

**Corollary 4.1 (cyclic phase incidence).** For every \(O,O_1\),

$$
\mathcal I_a(O,O_1)
=
\left\{
a_\#\psi_{\Delta,\#}^{\,t}x_O:
t\in\Theta_a(O,O_1)
\right\}.
\tag{4.3}
$$

Moreover,

$$
\boxed{
O\xrightarrow{r,a}O'
\iff
\exists t\in\mathbb Z/M\mathbb Z:
\begin{cases}
a_\#\psi_{\Delta,\#}^{\,t}x_O
\in\operatorname{Dom}(F_r^{(0)}),\\[1mm]
\pi_H\!\left(
F_r^{(0)}
(a_\#\psi_{\Delta,\#}^{\,t}x_O)
\right)=O'.
\end{cases}
}
\tag{4.4}
$$

**Proof.** Every point of \(O\) has the form
\(\psi_{\Delta,\#}^{\,t}x_O\). Applying \(a_\#\) gives (4.3), and
substitution into Proposition 3.1 gives (4.4). \(\square\)

Replacing \(x_O\) by another representative translates the phase coordinate
\(t\). The concrete relation represented by (4.4) is unchanged.

Corollary 4.1 is a finite parametrization of source-addressed incidence. It
is not a deterministic action of \(a\) on orbit space and not a Safe-Hit
classification.

## Capacity-Isolated Order Breaking

For a lane \(C\in\mathcal C_\Delta\), say that \(a\) breaks \(C\) if

$$
a|_C:C\longrightarrow a(C)
\tag{5.1}
$$

is not a cycle-graph isomorphism. Put

$$
\operatorname{Break}_\Delta(a)
=
\{C\in\mathcal C_\Delta:a\text{ breaks }C\}.
\tag{5.2}
$$

The stabilizer sandwich suggests the possible strengthening

$$
\operatorname{Break}_\Delta(a)\ne\varnothing
\stackrel{?}{\Longrightarrow}
\operatorname{SafeHit}_a
=
\operatorname{SameLane}_\Delta.
\tag{5.3}
$$

The next theorem disproves (5.3) uniformly.

**Theorem 5.1 (capacity-isolated break obstruction).** For every integer
\(g\ge2\), set

$$
n=5g,
\qquad
\Delta=g.
\tag{5.4}
$$

There is a branch

$$
a_g\in\operatorname{Stab}(\mathcal C_\Delta)
\tag{5.5}
$$

such that

$$
\operatorname{Break}_\Delta(a_g)=\{C_\ast\}
\tag{5.6}
$$

but

$$
\operatorname{SafeHit}_{a_g}
\subsetneq
\operatorname{SameLane}_\Delta.
\tag{5.7}
$$

For every ordinary lane \(C_j\), each state occupying all five points of
\(C_j\) with a marked nonedge belongs to

$$
\operatorname{SameLane}_\Delta
\setminus
\operatorname{SafeHit}_{a_g}.
\tag{5.8}
$$

**Proof.** Under (5.4), the punctured lane has length

$$
|C_\ast|=\ell-1=4,
\tag{5.9}
$$

and every ordinary lane has length

$$
|C_j|=\ell=5.
\tag{5.10}
$$

Choose \(a_g\) to be an adjacent transposition on the punctured four-cycle
and the identity on all ordinary lanes. An adjacent transposition is not a
cycle-graph automorphism of a four-cycle, so (5.6) holds.

Let \(\mathcal U\) be the set of states whose five occupied points fill one
ordinary lane and whose marked pair is a cycle nonedge in that lane. Every
state in \(\mathcal U\) is same-lane.

Consider an enabled return from \(x\in\mathcal U\). Since \(a_g\) is the
identity on the supporting ordinary lane, the branch step leaves the complete
five-point support there. A rotation can carry that full lane either to
another ordinary lane or to the five-point unpunctured lane through
\(0,\Delta,2\Delta,3\Delta,4\Delta\).

The second case is not guarded: the rotated support contains both collision
coordinates \(0\) and \(\Delta\). Equivalently, the four-point punctured lane
cannot receive a complete five-token context. Hence every enabled return
carries \(x\) bijectively to a complete ordinary lane.

On ordinary lanes the branch is identity, and the rotational transport is a
cycle-graph isomorphism. It therefore preserves marked nonedges. Thus

$$
\mathcal U
\quad\text{is forward invariant.}
\tag{5.11}
$$

The normalized branch target on an ordinary lane requires the marked pair to
be a \(\Delta\)-edge of that lane. No state of \(\mathcal U\) is a target.
Therefore \(\mathcal U\) is target-disjoint, and every state in
\(\mathcal U\) fails Safe-Hit. This proves (5.7) and (5.8). \(\square\)

**Corollary 5.2 (break nonemptiness is insufficient).** In the full
lane-partition stabilizer,

$$
\boxed{
\operatorname{Break}_\Delta(a)\ne\varnothing
\not\Longrightarrow
\operatorname{SafeHit}_a
=
\operatorname{SameLane}_\Delta.
}
\tag{5.12}
$$

The failure is a same-witness mobility failure: the complete context cannot
enter the only lane on which the branch can change its cyclic order.

Corollary 5.2 does not prove that the map

$$
a\longmapsto\operatorname{Break}_\Delta(a)
\tag{5.13}
$$

is too coarse to determine Safe-Hit. Such a quotient non-descent theorem
requires two branches with equal break sets and different Safe-Hit
predicates.

## The Remaining Mobility Problem

The obstruction identifies the missing positive hypothesis. It is not enough
that some lane be order breaking; one concrete five-token context must reach
a usable breaking placement.

**Definition 6.1 (mobility to a breaking witness).** Write

$$
\operatorname{MobToBreak}_a(x)
\tag{6.1}
$$

if an actual guarded identity-branch path carries \(x\) to a concrete state
\(y\) in a lane \(C\) such that:

1. the marked pair of \(y\) is nonadjacent in \(C\);
2. \(a|_C\) sends that concrete pair to an adjacent pair;
3. the same state \(a_\#y\) admits the declared continuation to the target.

**Proposition 6.2 (mobility-to-break sufficiency).** For every branch \(a\),

$$
\operatorname{MobToBreak}_a(x)
\Longrightarrow
\operatorname{SafeHit}_a(x).
\tag{6.2}
$$

**Proof.** Concatenate the guarded identity path in Definition 6.1, its
pathwise branch-\(a\) simulation inherited from Paper XXXII, the globally
enabled label-zero \(a_\#\) step at \(y\), and the declared continuation from
the same state \(a_\#y\). This branch step is not an additional guarded
ordinary return. Every clause uses the witnesses supplied by the definition.
\(\square\)

The proposition is intentionally conditional. The substantive open problem
is to characterize when the cyclic phase-incidence fibers of Corollary 4.1
contain a usable breaking witness.

### Open Problem 6.3 (minimal stabilizer incidence)

Find a quotient of the phase-incidence data that:

1. determines the return guard;
2. retains the concrete intermediate witness needed by Proposition 3.1;
3. detects mobility to a usable breaking placement; and
4. is strictly smaller than the raw five-token state relation.

Candidate summaries include the break set, the lane permutation, restriction
cycle types, and relative phase data. None is promoted here as sufficient.

## Computational Artifacts

The paper-owned evidence package is available under
[`experiments/paper33/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper33)
in the RIME repository. It has no dependency on the broader exploratory
source tree.

| Surface | Paper-owned path | Role |
|---|---|---|
| Bounded finite controls | `stabilizer_hostile_audit.py` and `results/` | Replays the retained full-stabilizer and capacity-isolation domains |
| Partial formalization | `lean/` | Checks the abstract capacity-obstruction implication spine |
| Development validation | `development-manifest.json` and `validation/` | Binds the 19-artifact paper-owned evidence closure |
| Release validation | `release-manifest.json` and the public receipt under `results/` | Binds the manuscript, reader PDF, bibliography, figure, nested development closure, environment, and validators |

For all eight multi-lane domains with \(6\le n\le9\), the producer exhausts
656 full stabilizer branches and verifies 656 instances of Proposition 3.1.
No failure of (5.3) occurs in that bounded range.

For

$$
(n,\Delta)=(10,2),
\tag{7.1}
$$

the complete 2,880-branch scan records

$$
80\ \mathsf{ADJ},
\qquad
160\ \mathsf{INTERMEDIATE},
\qquad
2640\ \mathsf{SAME}.
\tag{7.2}
$$

The first intermediate branch is the \(g=2\) instance of Theorem 5.1. Its
state counts are

$$
|\operatorname{Adj}|=505,
\qquad
|\operatorname{SafeHit}|=555,
\qquad
|\operatorname{SameLane}|=560.
\tag{7.3}
$$

The package also checks the forward-invariant family used in Theorem 5.1 for
\(2\le g\le12\).

These calculations are bounded consistency controls. They are not proofs of
Proposition 3.1 or Theorem 5.1, and the absence of a retained matched hostile
pair is not a quotient-descent result.

A paper-owned Lean development machine-checks the data-independent
capacity-obstruction spine of Theorem 5.1: a rank-five output cannot occupy a
capacity-four lane; the declared ordinary-lane nonedge family is preserved by
one step and hence by finite reachability; and that family is disjoint from
the edge target. The formalization consumes, rather than constructs, the
concrete branch family, cyclic lane arithmetic, lane-shape dichotomy, and
ordinary-lane nonedge preservation proved above. It does not formalize the
finite databases or promote them to all-\(g\) evidence.

The public receipt records performed replay and local closure verification,
is excluded from its own closure, and is not an independent mathematical
validation.

## Claim Status and Boundary

| Claim | Status | Scope |
|---|---|---|
| Exact source-addressed stabilizer descent | Proposition 3.1 | Every branch permutation and pair of universal-return orbits |
| Cyclic phase parametrization | Corollary 4.1 | Every source, intermediate, and target orbit in the declared cyclic action |
| Capacity-isolated break obstruction | Theorem 5.1 | The family \(n=5g,\Delta=g\), every integer \(g\ge2\) |
| Break nonemptiness is insufficient | Corollary 5.2 | Full lane-partition stabilizer in the same all-\(g\) family |
| Mobility-to-break sufficiency | Proposition 6.2 | Conditional on one concrete same-witness guarded path |
| Capacity-obstruction implication spine | Machine-checked partial Lean formalization | Abstract finite reachability system under the declared invariance and target-disjointness hypotheses |
| Retained finite scans | Bounded consistency control | All multi-lane domains \(6\le n\le9\), the complete \((10,2)\) domain, and \(2\le g\le12\) family controls |
| Break-set quotient non-descent | Open | Requires matched branches with equal retained break data and different Safe-Hit predicates |
| Minimal sufficient incidence quotient | Open | Must preserve guards, same-witness composition, and usable breaking placement |
| General positive mobility-to-break theorem | Open | No all-stabilizer mobility criterion is claimed |
| Complete survivor incidence | Not claimed | Marked-pair return does not determine all spectator placements |
| Raw-to-typed transfer bridge | Not claimed | Raw reachability supplies no typed authority |
| Projectable-origin supply | Not claimed | Outside the intrinsic raw system |
| Recursive return and credit settlement | Not claimed | No reset-bound consequence |

The finite controls do not enlarge the theorem domain. Raw reachability does
not supply typed authority.

## Conclusion

The full lane stabilizer changes the nature of return descent. A normalizer
branch acts deterministically on universal-return orbits; a general
stabilizer branch does not. The exact replacement is source-addressed orbit
incidence, and its cyclic phase parametrization preserves the intermediate
witness needed by the next partial return.

In this sense the full stabilizer is a natural endpoint of lane-only descent:
the lane partition remains visible, but it no longer determines which
concrete phase witness can pass the next guard.

Order breaking alone is nevertheless insufficient. In the family
\(n=5g,\Delta=g\), the only breaking lane has capacity four while the
candidate context occupies five points. Complete ordinary-lane contexts
cannot enter the breaking lane, so same-lane nonedges survive as a
forward-invariant obstruction.

The remaining classification problem is therefore no longer whether a branch
breaks cyclic order somewhere. It is whether one concrete guarded context can
reach a breaking placement and continue from that same witness.

## References {.unnumbered}

::: {#refs}
:::
