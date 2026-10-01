# Terminal Orientation and Survivor Incidence in Five-Token Return Dynamics
### One-Lane Dihedral Classification and Pair-Level Non-Descent

**WuJun Chen**

Independent Researcher | RIME Program | 2026

**Paper XXXIV | Version 1.0**

*This paper (Paper XXXIV of the RIME program) studies intrinsic raw first-exit
incidence in normalized single-defect circular dynamics. It does not assert
typed transfer membership, projectability, recursive return, credit
settlement, or a reset bound.*

---

## Abstract

**Problem.** Spectator-safe reachability determines which pair of five source
lineages can occupy the terminal kernel pair. It does not record where the
other three source lineages land after the strict exit. A survivor statement
therefore requires more than a marked-pair Safe-Hit witness.

**Approach.** The construction retains the complete labelled injection and
terminal exponent.
For a normalized terminal witness $(\lambda,u)$, define

$$
 \beta_{\lambda,u}=\varepsilon_\Delta p^ua\lambda.
$$

This one map records both the fused source pair and the source-addressed
survivor placement. It transports the same witness back to the original raw
defect event. The classification then specializes to the one-lane dihedral
family $a\in\operatorname{Aut}(C_{n-1})$.

**Results.** Every dihedral branch has the same five hittable source pairs:
the consecutive pairs in the source cyclic order. The survivor spectrum,
however, depends on the orientation character. A rotation branch realizes
exactly the increasing survivor placements, while a reflection branch
realizes both the increasing and decreasing placements. For every hittable
pair the spectrum sizes are

$$
 \binom{n-2}{3}
 \qquad\text{and}\qquad
 2\binom{n-2}{3},
$$

respectively. Thus equal Safe-Hit and equal fused-pair data do not determine
survivor incidence: pair-level reachability forgets the attained terminal
orientation class.

**Boundary.** The orientation spectrum is exact for the one-lane dihedral
family. No claim is made that it is a minimal or sufficient survivor quotient
for arbitrary branches or multiple lanes. The results remain raw and do not
cross the typed transfer or projectability boundary.

**Keywords.** synchronizing automata; single-defect automata; packet
lineages; first-exit incidence; survivor placement; dihedral dynamics;
same-witness descent

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $Q=\mathbb Z/n\mathbb Z$ | labelled circular carrier |
| $p(q)=q+1$ | fixed full cycle |
| $K=\{0,\Delta\}$ | normalized kernel pair |
| $E=Q\setminus\{0\}$ | normalized branch carrier |
| $a\in\operatorname{Sym}(E)$ | branch permutation |
| $\varepsilon_\Delta$ | marked collapse $0\mapsto\Delta$ |
| $T_0$ | five source lineage labels |
| $\lambda:T_0\hookrightarrow E$ | labelled normalized state |
| $(\lambda,u)$ | terminal witness, including terminal rotation $u$ |
| $\beta_{\lambda,u}$ | complete normalized strict-exit incidence |
| $F$ | fused two-lineage source pair |
| $R_0=T_0\setminus F$ | three surviving source lineages |
| $\mathfrak F_a$ | fused-pair spectrum |
| $\mathfrak S_a(F)$ | source-addressed survivor spectrum over $F$ |
| $\psi$ | positive cycle on the one-lane carrier $E$ |
| $\chi(a)$ | dihedral orientation character |
| $\operatorname{OriSpec}_a(F)$ | attained terminal-orientation spectrum |

## Introduction

The first-exit problem for five packets has two distinct outputs. The first is
the unordered pair of source packets that fuses. The second is the placement
of the three packets that survive the strict exit. The first output is a
marked-pair reachability question. The second is a source-addressed incidence
question.

Paper XXIX retains all five packet lineages and classifies the complete raw
frontier for the canonical defect. Papers XXX and XXXI normalize a general
binary-kernel rank-$(n-1)$ defect into a marked collapse together with a free
branch permutation. Paper XXXII classifies single-lane Safe-Hit for every
branch permutation, while Paper XXXIII identifies the same-witness incidence
needed once deterministic orbit descent fails
[@paper29; @paper30; @paper31; @paper32; @paper33].

Those results answer increasingly broad versions of

$$
 \text{which pair can fuse?}
 \tag{1.1}
$$

They do not by themselves answer

$$
 \text{where do the other three source lineages land?}
 \tag{1.2}
$$

A terminal endpoint cannot be reconstructed by choosing one witness for
(1.1) and another for (1.2). The pair and survivor placement must come from
the same labelled path and the same terminal event.

This paper introduces the normalized incidence map

$$
 \beta_{\lambda,u}=\varepsilon_\Delta p^ua\lambda.
 \tag{1.3}
$$

Its unique two-element fiber is the fused pair; its restriction to the other
three labels is the survivor placement. The terminal exponent $u$ remains
part of the witness.

The main classification concerns the one-lane regime $\Delta=1$. Put
$L=n-1$ and let $a$ be a cycle-graph automorphism of the punctured lane. All
such branches have the same complete Safe-Hit predicate, but their survivor
spectra split according to the orientation character

$$
 \chi(a)\in\{+1,-1\}.
 \tag{1.4}
$$

Rotation branches retain only positive terminal orientation. Reflection
branches attain both orientations. The fused-pair projection forgets exactly
this distinction in the classified family.

The proof has one important converse. A formally allowed terminal placement
is not treated as a witness. Because five occupied points in an $n\ge6$
carrier leave a hole, a terminal rotation can move a hole to the deleted
coordinate and reconstruct an actual reachable section injection.
This binds fused pair, survivor placement, and terminal exponent to one row.

The theorem spine is:

1. Section 2 defines normalized strict-exit incidence and proves same-witness
   transport to the original raw event.
2. Section 3 classifies the reachable labelled orientation fibers of every
   one-lane dihedral branch.
3. Section 4 proves the complete dihedral survivor-spectrum theorem.
4. Section 5 isolates terminal orientation as the information forgotten by
   pair-level reachability.
5. Section 6 records the computational controls and the boundary to wider
   branch and typed theories.

### Related Work and Novelty Boundary

The Černý conjecture and the general theory of synchronizing automata concern
short reset words [@cerny1964; @volkov2008; @volkov2022survey]. Circular,
almost-group, and completely reachable automata provide neighboring
structural settings [@dubuc1998; @berlinkovNicaud2020; @casasTorres2024;
@don2016; @gonzeJungers2018; @ferensSzykula2026]. This paper proves neither a
reset bound nor a complete-reachability characterization.

Subset synchronization, monotonicity, and dynamic word constraints study
related partial and order-sensitive reachability questions
[@eppstein1990; @ryzhikovShemyakov2018; @wolf2020]. Here one guarded path must
keep five source-labelled lineages injective until one declared strict event,
and the output retains the incidence of every source label.

Within the RIME synchronizing-automata line, Paper XXIX proves the canonical
source-addressed frontier, Papers XXX--XXXII expose and classify normalized
branch dynamics, and Paper XXXIII formalizes source-addressed orbit incidence
[@paper29; @paper30; @paper31; @paper32; @paper33]. The new claims here are an
exact normalized strict-exit incidence transport, a complete one-lane
dihedral survivor-spectrum classification, and a symbolic proof that the
pair-level Safe-Hit surface does not determine survivor incidence.

## Normalized Strict-Exit Incidence

### The inherited branch system

Fix

$$
 Q=\mathbb Z/n\mathbb Z,
 \qquad
 K=\{0,\Delta\},
 \qquad
 E=Q\setminus\{0\},
 \tag{2.1}
$$

with $n\ge6$. Let

$$
 \varepsilon_\Delta(0)=\Delta,
 \qquad
 \varepsilon_\Delta(q)=q\quad(q\ne0),
 \tag{2.2}
$$

and let $a\in\operatorname{Sym}(E)$. Paper XXXI's branch normalization gives
the partial point maps

$$
 \phi_r=\varepsilon_\Delta p^ra:E\longrightarrow E,
 \qquad
 r\in\mathbb Z/n\mathbb Z.
 \tag{2.3}
$$

Let $T_0$ be a five-element set of source lineage labels. A normalized state
is an injection

$$
 \lambda:T_0\hookrightarrow E.
 \tag{2.4}
$$

The transition $\lambda\xrightarrow{r}\phi_r\lambda$ is defined exactly when
$\phi_r$ is injective on $\lambda(T_0)$. For a fixed source $\lambda_0$, let

$$
 \mathcal L_{n,\Delta,a}(\lambda_0)
 \tag{2.5}
$$

be the complete set of injections reachable by guarded transitions.

The normalized system is intrinsic. Transport back to an original labelled
defect additionally assumes the branch-normalization data of Paper XXXI: a
rank-$(n-1)$ defect $d$ with missing image $m$,
$D=Q\setminus\{m\}$, a bijection

$$
 b=d|_E:E\overset\sim\longrightarrow D,
 \qquad
 p^{t_0}(m)=0,
 \qquad
 a=p^{t_0}b.
$$

These data are not reconstructed from $a$. Conclusions internal to
$\beta_{\lambda,u}$ need only the normalized system; conclusions about the
original raw event are conditional on this supplied realization.

### Terminal witnesses

Fix $F\subset T_0$, $|F|=2$, and put $R_0=T_0\setminus F$. A terminal witness
for $F$ is a pair $(\lambda,u)$ satisfying

$$
 \lambda\in\mathcal L_{n,\Delta,a}(\lambda_0),
 \qquad
 p^ua\lambda(F)=\{0,\Delta\}.
 \tag{2.6}
$$

Define

$$
 \boxed{
 \beta_{\lambda,u}
 =\varepsilon_\Delta p^ua\lambda:T_0\longrightarrow E.}
 \tag{2.7}
$$

Since $p^ua\lambda$ is injective, (2.7) is equivalently

$$
 \beta_{\lambda,u}(q)
 =
 \begin{cases}
  \Delta,&q\in F,\\
  p^ua(\lambda(q)),&q\in R_0.
 \end{cases}
 \tag{2.8}
$$

**Proposition 2.1 (normalized strict-exit incidence transport).** For every
terminal witness $(\lambda,u)$, conclusions 1--2 below hold intrinsically.
When the normalized system is supplied with the original branch-realization
data above, conclusions 3--4 also hold:

1. $\beta_{\lambda,u}$ has the unique two-element fiber $F$ over $\Delta$;
2. $\beta_{\lambda,u}|_{R_0}$ is an injection into
   $E\setminus\{\Delta\}$;
3. the one normalized witness transports, without replacement, to the raw
   witness $(b\lambda,t_0+u)$ for the original strict defect event;
   and
4. replacing lineage labels by their fixed source packets recovers the raw
   rank-four endpoint exactly.

**Proof.** The only nonsingleton fiber of $\varepsilon_\Delta$ is
$\{0,\Delta\}$. Equation (2.6) says that precisely the two lineages in $F$
occupy that fiber. The other three images are distinct and avoid both kernel
coordinates, proving the first two claims.

Let $b:E\overset\sim\longrightarrow D$ and $t_0$ be the branch-normalization
data of Paper XXXI. The identities

$$
 b^{-1}d=\varepsilon_\Delta,
 \qquad
 a=p^{t_0}b
 \tag{2.9}
$$

give

$$
 \boxed{
 d\,p^{t_0+u}b\lambda=b\,\beta_{\lambda,u}.}
 \tag{2.10}
$$

Thus (2.10) carries this one normalized witness to its prescribed raw
coordinates $(b\lambda,t_0+u)$; no second witness is chosen. Finally, the
fixed source packets are nonempty and disjoint.
The output packet at a coordinate is therefore the union of exactly the
source packets whose lineage labels occupy that fiber, as in Paper XXIX's
lineage decoder. $\square$

### Incidence spectra and the same-witness firewall

Let $\mathcal W_a(\lambda_0;F)$ be the set of terminal witnesses satisfying
(2.6). Define

$$
 \mathfrak B_a(\lambda_0;F)
 =\{\beta_{\lambda,u}:(\lambda,u)\in\mathcal W_a(\lambda_0;F)\},
 \tag{2.11}
$$

and

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)
 =\{\beta_{\lambda,u}|_{R_0}:
   (\lambda,u)\in\mathcal W_a(\lambda_0;F)\}.}
 \tag{2.12}
$$

The fused-pair spectrum is

$$
 \mathfrak F_a(\lambda_0)
 =\{F:\mathcal W_a(\lambda_0;F)\ne\varnothing\}.
 \tag{2.13}
$$

The attained boundary has the exact decomposition

$$
 \mathfrak B_a(\lambda_0)
 \cong
 \bigsqcup_{F\in\mathfrak F_a(\lambda_0)}
 \{F\}\times\mathfrak S_a(\lambda_0;F).
 \tag{2.14}
$$

This is a decomposition of attained incidences, not a claim that every formal
survivor injection occurs. In particular,

$$
 \begin{aligned}
 &\bigl[\exists(\lambda,u)\text{ hitting }F\bigr]\\
 &\qquad\land
 \bigl[\exists(\lambda',u')\text{ with the desired survivor pattern}\bigr]\\
 &\not\Longrightarrow
 \exists(\widehat\lambda,\widehat u)\text{ realizing both properties}.
 \end{aligned}
 \tag{2.15}
$$

## The One-Lane Dihedral System

Set $\Delta=1$ and $L=n-1$. On

$$
 E=\{1,\ldots,n-1\},
 \tag{3.1}
$$

let $\psi$ be the positive $L$-cycle. Let

$$
 \operatorname{Aut}(C_L)=\langle\psi,\rho\rangle,
 \tag{3.2}
$$

where $\rho$ fixes $1$ and reverses the cycle. Define

$$
 \chi(a)=
 \begin{cases}
  +1,&a\in\langle\psi\rangle,\\
  -1,&a\in\langle\psi\rangle\rho.
 \end{cases}
 \tag{3.3}
$$

Give $T_0$ a positive cyclic order and assume that
$\lambda_0:T_0\hookrightarrow E$ preserves it. An injection is called
positive or negative according to whether it preserves or reverses this
oriented cyclic order.

**Lemma 3.1 (identity-path simulation).** For every
$a\in\operatorname{Sym}(E)$, every guarded identity-branch path has a guarded
branch-$a$ realization with the same source and target injections.

**Proof.** The label-zero branch return is $a_\#$ and is globally enabled.
Since $a$ is a finite permutation, positive powers of this return realize
$a^{-1}_\#$. Before an identity transition

$$
 x\longmapsto(\varepsilon_1p^r)_\#x,
$$

first reach $a^{-1}_\#x$ by label-zero returns and then apply the label-$r$
branch return. Its output is

$$
 (\varepsilon_1p^ra)_\#(a^{-1}_\#x)
 =(\varepsilon_1p^r)_\#x.
$$

Iterating this construction simulates the whole path. $\square$

**Lemma 3.2 (reachable orientation fiber).** If
$a\in\operatorname{Aut}(C_L)$, then

$$
 \mathcal L_a(\lambda_0)
 =
 \begin{cases}
  \{\text{positive injections}\},&\chi(a)=+1,\\
  \{\text{positive injections}\}\sqcup
  \{\text{negative injections}\},&\chi(a)=-1.
 \end{cases}
 \tag{3.4}
$$

**Proof.** By Paper XXXI's lane-order preservation theorem, on every guarded
support $\varepsilon_1p^r$ preserves the hole-deleted cyclic order
[@paper31]. A branch step therefore preserves orientation for a rotation
branch and reverses it for a reflection branch. This proves the forward
inclusions.

Paper XXIX's labelled order-fiber theorem says that the identity branch
reaches every positive injection [@paper29]. Lemma 3.1 imports those paths
into every branch-$a$ system. If $a$ is a reflection and $\mu$ is negative,
$a^{-1}\mu$ is positive. Reach $a^{-1}\mu$ and apply the globally enabled
label-zero return once to reach $\mu$. $\square$

The next lemma is the step that prevents formal terminal coordinates from
being promoted silently to actual witnesses.

**Lemma 3.3 (missing-hole terminal realization).** Let
$a\in\operatorname{Aut}(C_L)$. Suppose that an injective placement
$\mu:T_0\hookrightarrow Q$ is positive when $\chi(a)=+1$, and is either
positive or negative when $\chi(a)=-1$. Assume also that

$$
 \mu(F)=\{0,1\}.
 \tag{3.5}
$$

Then there is an actual terminal witness $(\lambda,u)$ with
$p^ua\lambda=\mu$.

**Proof.** The placement occupies five points in an $n\ge6$ carrier, so it
omits some coordinate $h$. Choose $u$ so that $p^{-u}\mu$ omits $0$, and set

$$
 \boxed{\lambda=a^{-1}p^{-u}\mu:T_0\hookrightarrow E.}
 \tag{3.6}
$$

If $a$ is a rotation, the allowed $\mu$ is positive and hence so is
$\lambda$. If $a$ is a reflection, Lemma 3.2 contains both orientation
classes. Thus $\lambda$ belongs to the reachable fiber in either case, and
$p^ua\lambda=\mu$. $\square$

## Complete Dihedral Survivor Classification

For a consecutive source pair $F$, orient the source order as

$$
 (f_0,f_1,r_1,r_2,r_3),
 \qquad
 F=\{f_0,f_1\}.
 \tag{4.1}
$$

Define

$$
 \mathfrak S^+(F)
 =\left\{
 s:R_0\hookrightarrow E\setminus\{1\}:
 2\le s(r_1)<s(r_2)<s(r_3)\le n-1
 \right\},
 \tag{4.2}
$$

and

$$
 \mathfrak S^-(F)
 =\left\{
 s:R_0\hookrightarrow E\setminus\{1\}:
 2\le s(r_3)<s(r_2)<s(r_1)\le n-1
 \right\}.
 \tag{4.3}
$$

**Theorem 4.1 (one-lane dihedral survivor-spectrum classification).** For
every $a\in\operatorname{Aut}(C_L)$,

$$
 \boxed{
 \mathfrak F_a(\lambda_0)
 =\{\text{the five consecutive pairs in the source cyclic order}\}.}
 \tag{4.4}
$$

For every such pair $F$,

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)
 =
 \begin{cases}
  \mathfrak S^+(F),&\chi(a)=+1,\\[1mm]
  \mathfrak S^+(F)\mathbin{\sqcup}\mathfrak S^-(F),&\chi(a)=-1.
 \end{cases}}
 \tag{4.5}
$$

Consequently,

$$
 \boxed{
 |\mathfrak S_a(\lambda_0;F)|
 =
 \begin{cases}
  \binom{n-2}{3},&\chi(a)=+1,\\[1mm]
  2\binom{n-2}{3},&\chi(a)=-1.
 \end{cases}}
 \tag{4.6}
$$

**Proof.** By Lemma 3.2, the possible pre-collapse terminal placements are
positive only for a rotation branch and have both orientations for a
reflection branch. An unordered source pair can occupy the adjacent kernel
coordinates $\{0,1\}$ in either orientation exactly when its members are
consecutive in the source cyclic order. Lemma 3.3 supplies an actual terminal
witness for every such formal placement, proving (4.4).

For a positive terminal placement, (4.1) forces

$$
 f_0\mapsto0,
 \qquad
 f_1\mapsto1,
 \qquad
 2\le r_1<r_2<r_3\le n-1.
 \tag{4.7}
$$

For a negative terminal placement it forces

$$
 f_1\mapsto0,
 \qquad
 f_0\mapsto1,
 \qquad
 2\le r_3<r_2<r_1\le n-1.
 \tag{4.8}
$$

The strict collapse sends both fused lineages to $1$ and fixes every survivor
coordinate. Equations (4.7)--(4.8) therefore give (4.5). The two survivor
families are disjoint because their coordinates are distinct, and each is
indexed by a three-subset of the $n-2$ coordinates $\{2,\ldots,n-1\}$.
This proves (4.6). $\square$

The identity branch is the positive-orientation specialization and recovers
Paper XXIX's canonical survivor spectrum after undoing branch coordinates.
The reflection branches add one complete negative-orientation copy; they do
not change which source pairs can fuse.

## Terminal Orientation and Pair-Level Non-Descent

For a hittable pair $F$, define

$$
 \begin{aligned}
 \operatorname{OriSpec}_a(F)
 =\{\epsilon\in\{+,-\}:{}&
   \exists(\lambda,u)\in\mathcal W_a(\lambda_0;F),\\[-1mm]
  &p^ua\lambda\text{ has orientation }\epsilon\}.
 \end{aligned}
 \tag{5.1}
$$

**Corollary 5.1 (orientation-spectrum factorization).** Within the one-lane
dihedral family,

$$
 \operatorname{OriSpec}_a(F)
 =
 \begin{cases}
  \{+\},&\chi(a)=+1,\\
  \{+,-\},&\chi(a)=-1,
 \end{cases}
 \tag{5.2}
$$

and

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)
 =
 \bigsqcup_{\epsilon\in\operatorname{OriSpec}_a(F)}
 \mathfrak S^\epsilon(F).}
 \tag{5.3}
$$

**Proof.** This is Theorem 4.1 with the terminal orientation retained instead
of counted. $\square$

The factorization is exact for the classified family. It does not assert that
$\operatorname{OriSpec}$ is minimal or sufficient for arbitrary branches.

**Corollary 5.2 (pair-level non-descent).** Let $a_+$ be any rotation and
$a_-$ any reflection in $\operatorname{Aut}(C_L)$. Then

$$
 \mathfrak F_{a_+}(\lambda_0)
 =\mathfrak F_{a_-}(\lambda_0),
 \tag{5.4}
$$

and the two branches have the same complete marked-pair Safe-Hit predicate,
but for every hittable pair $F$,

$$
 \boxed{
 \mathfrak S_{a_+}(\lambda_0;F)
 \ne
 \mathfrak S_{a_-}(\lambda_0;F).}
 \tag{5.5}
$$

Hence fused-pair reachability does not determine survivor incidence.

**Proof.** Equation (5.4) follows from (4.4). Paper XXXII proves that every
cycle-graph automorphism has Safe-Hit exactly on the adjacent marked-pair
class [@paper32]. Equations (4.5)--(4.6) show that $a_+$ realizes only
$\mathfrak S^+(F)$, while $a_-$ also realizes the nonempty disjoint family
$\mathfrak S^-(F)$. $\square$

Corollary 5.2 is a quotient non-descent statement. The pair-level observable
forgets terminal orientation. It is stronger than exhibiting two distinct raw
endpoints for one fused pair, because the two branch families agree on the
entire marked-pair reachability predicate.

## Controls, Scope, and Open Boundary

### Bounded finite controls

The paper-owned finite control under `experiments/paper34/` retains complete
lineage labels and terminal exponents. Its six-point run exhausts all
$5!=120$ branch permutations. It also checks every rotation and reflection of
the one-lane cycle for $6\le n\le9$.

For each dihedral branch and each consecutive fused pair, the control compares
the complete attained survivor set, not only its cardinality, against (4.5).
The per-pair counts are

| $n$ | rotation branch | reflection branch |
|---:|---:|---:|
| 6 | 4 | 8 |
| 7 | 10 | 20 |
| 8 | 20 | 40 |
| 9 | 35 | 70 |

These bounded computations are consistency controls. They are not the proof
of Theorem 4.1 or Corollary 5.2.

### Wider raw branch theory

For a non-dihedral one-lane branch, Paper XXXII shows that every marked-pair
orbit is Safe-Hit [@paper32]. That theorem still does not classify the
survivor spectrum. An arbitrary branch can alter terminal cyclic order more
substantially than the two classes in (5.2). In multiple lanes, lane type,
phase incidence, and same-witness mobility may all affect survivor placement.

The next raw problem is therefore not another proof of pair reachability. It
is to determine which terminal-order or phase-incidence data classify
$\mathfrak S_a(F)$ beyond the dihedral family.

### Boundary to typed transfer and recursion

Proposition 2.1 and Theorem 4.1 classify raw incidence. They do not establish
that any endpoint belongs to a separately declared transfer fiber. In
particular,

$$
 \text{raw survivor incidence}
 \not\Rightarrow
 \text{typed transfer membership}
 \not\Rightarrow
 \text{same-witness projectability}.
 \tag{6.1}
$$

No role, ancestry, residual, authorization, or handoff field is inferred from
the raw map $\beta_{\lambda,u}$. No new semantic field is introduced to force
such a bridge.

## Computational Artifacts

The paper-owned evidence package is available under
[`experiments/paper34/`](https://github.com/dooven-prime/rime-lite/tree/master/experiments/paper34)
in the RIME repository. It has no dependency on the broader exploratory
source tree.

| Surface | Location | Purpose |
|---|---|---|
| Finite control | `survivor_incidence_audit.py`, `results/` | bounded same-witness replay |
| Theorem note | [classification note](https://github.com/dooven-prime/rime-lite/blob/master/experiments/paper34/ONE_LANE_DIHEDRAL_SURVIVOR_CLASSIFICATION.md) | supporting all-$n$ proof provenance |
| Lean spine | `lean/` | incidence and non-descent implications |
| Validation | `validation/` | source and evidence gates |
| Source closure | `development-manifest.json` | exact 18-artifact paper-owned closure |

The finite result is not promoted as proof of the all-$n$ claims. The formal
note is supporting proof provenance; the owning theorem statements and claim
boundaries are those in this manuscript.

A paper-owned Lean formalization machine-checks the data-independent part of
the argument. From one supplied injective terminal placement it derives the
unique two-lineage collision fiber, survivor injectivity, and collision-root
avoidance. It also checks the missing-coordinate cardinality lemma, the
orientation-spectrum count, and the logical non-descent from equal pair data
to unequal survivor spectra. The formalization consumes rather than proves
the guarded all-$n$ reachability and dihedral orientation classification in
Sections 3--4. It does not formalize the finite database or the conditional
transport back through a concrete branch conjugacy.

The source closure is verified locally against exact file bytes. Any release
receipt remains downstream of those bytes and records its declared validation
mode and replay status. It is not an independent mathematical validation.

## Claim Status and Boundary

| Claim surface | Status | Scope |
|---|---|---|
| Normalized strict-exit incidence | Proposition 2.1(1)--(2) | every normalized branch and every complete terminal witness |
| Transport to the original raw event | Proposition 2.1(3)--(4) | every supplied Paper XXXI branch realization of that normalized witness |
| Reachable orientation fiber | Lemma 3.2 | one-lane dihedral branches, all $n\ge6$ |
| Missing-hole terminal realization | Lemma 3.3 | allowed terminal orientations, all $n\ge6$ |
| Complete dihedral survivor spectrum | Theorem 4.1 | every $a\in\operatorname{Aut}(C_{n-1})$, all $n\ge6$ |
| Orientation-spectrum factorization | Corollary 5.1 | one-lane dihedral family |
| Pair-level survivor non-descent | Corollary 5.2 | any rotation branch matched with any reflection branch |
| Incidence/counting/non-descent implication spine | Machine-checked partial Lean formalization | abstract complete terminal witnesses and supplied positive/negative survivor families |
| Arbitrary-branch survivor classification | Open | pair Safe-Hit alone is insufficient |
| Multiple-lane survivor classification | Open | phase incidence and lane mobility retained |
| Typed transfer and projectability bridge | Open interface theorem | not decided by raw incidence |

The paper claims no shortest terminal word, path-length bound, reset threshold,
credit settlement, uniform recursive menu, or all-rank descent theorem.

## Conclusion

The first strict exit carries more information than the identity of the fused
pair. Retaining the complete terminal witness produces one normalized
incidence map whose unique double fiber records the pair and whose singleton
fibers record the three survivors. This map transports exactly to the
original raw event.

In the one-lane dihedral family, the missing information is terminal
orientation. All rotations and reflections have the same five hittable source
pairs and the same marked-pair Safe-Hit predicate. Rotation branches realize
one orientation class of survivor placements; reflection branches realize
both. Pair-level reachability therefore forgets a genuine source-addressed
boundary observable.

This establishes survivor incidence as a new mathematical layer rather than
an endpoint count appended to Safe-Hit. Beyond the dihedral family, the task
is to identify the phase and orientation data that remain visible at the
terminal event while preserving the same witness. Only after that raw problem
is solved does the separate typed bridge to transfer membership and
projectability become relevant.

## References {.unnumbered}

::: {#refs}
:::
