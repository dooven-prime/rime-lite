# Uniform Finite-Field Route Profiles
### Pole-Preimage Classification and Characteristic-Aware Stability in Marked Modular Carriers

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*Paper XXI of the RIME program. An independently scoped theorem paper on
finite marked carriers and routed composition.*

---

## Abstract

**Problem.** Boolean support of each one-step sector block does not determine
whether the corresponding labelled routed product is nonzero. For the marked
projective carrier over a finite field, the missing information is encoded by
the collision pattern of prefix poles.

**Approach.** For the declared projective action on
$X_F=\mathbf P^1(F)$, with marked sectors $C_0=\{\infty\}$ and $C_1=F$ and
labelled alphabet $(S,R,R^{-1})$, preimages of $\infty$ under word prefixes
classify each supported route. The same prefix data define fixed-field
survivor automata and fixed-depth generic profiles.

**Results.** Depth two has 45 supported labelled candidates and exactly 14
zero routes for every finite field with at least three elements. Depth three
has 216 candidates and

$$
|Z_3(F)|=115+\mathbf 1_{\operatorname{char}F=2}
 +19\mathbf 1_{|F|=2}+\mathbf 1_{|F|=3}.
$$

At every positive depth, survivor sets admit an exact prefix-pole
classification. It yields the candidate count $3^dF_{d+3}$, fixed-field
rational transfer series, and stabilization of the complete labelled
depth-$d$ zero-route set whenever $|F|>d$ and
$\operatorname{char}F\notin E_d$.

**Boundary.** Every result is relative to the declared action, labelled
alphabet, marked partition, order convention, and route semantics. The
fixed-field automaton and reduced rational function may depend on the field.
No field-independent automaton, all-depth scalar zero-count formula,
presentation invariance, Hecke or modular-form interpretation, RG
universality, or spectral zero-mode claim is made.

**Keywords:** finite fields; projective line; routed products; prefix poles;
finite automata; rational generating functions; characteristic stability.

## Notation Table {.unnumbered}

| Symbol | Meaning |
|---|---|
| $F$, $q$ | finite field and its cardinality |
| $X_F=\mathbf P^1(F)$ | marked projective carrier $F\cup\{\infty\}$ |
| $C_0,C_1$ | singleton and finite marked sectors |
| $A=(S,R,R^{-1})$ | ordered labelled projective alphabet |
| $Q_s$ | projector onto sector $C_s$ |
| $G_k$ | composition of the first $k$ word letters |
| $\widetilde G_k$ | declared integral lift of the $k$th prefix |
| $v_k(w)=(d_k,-c_k)$ | primitive homogeneous vector for the $k$th prefix pole |
| $z_k(w)=G_k^{-1}(\infty)$ | prefix pole of word $w$ at position $k$ |
| $\operatorname{Surv}_F(w,s)$ | initial states surviving the complete route |
| $B_d(F),N_d(F),Z_d(F)$ | supported, nonzero, and zero-route sets or counts at depth $d$ |
| $Z_d^{\mathrm{gen}}$ | fixed-depth generic zero-route profile |
| $D_d,E_d$ | prefix determinant spectrum and exceptional characteristics |

## Introduction

This paper studies when a Boolean-supported sector route on a finite
projective carrier survives ordered composition. The complete object is

$$
(X_F,\rho,A,(C_0,C_1),\prec,\mathsf{Route}),
$$

where $\rho$ is the declared permutation action, $A$ retains its labels,
$\prec$ fixes composition order, and $\mathsf{Route}$ fixes the sector-path
semantics. None of these components is inferred from the others.

The central theorem classifies a route by the equality and exclusion pattern
of its prefix poles. Two consequences follow in different directions:

$$
\text{prefix-pole semantics}
\Longrightarrow
\begin{cases}
\text{fixed-field survivor automata and rational series},\\
\text{fixed-depth generic profiles and exceptional characteristics}.
\end{cases}
$$

The finite-state translation is field-relative and does not imply a uniform
automaton. The generic profile is depth-relative and does not imply one
all-depth scalar law. Depth-two and depth-three formulas are exact instances
of the same semantic construction rather than the source of the arbitrary-
depth theorem.

![A supported labelled route is reduced to prefix-pole equality and exclusion
constraints. Fixing the field yields a finite survivor automaton, while fixing
the depth yields a generic profile with exceptional characteristics. Neither
branch implies a field-independent automaton or an all-depth scalar
law.](../../figures/paper21/fig1_prefix_pole_semantics.png)

The governing distinctions are

$$
\begin{aligned}
\text{abstract presentation}&\ne\text{permutation action},\\
\text{permutation action}&\ne\text{marked partition},\\
\text{Boolean support}&\ne\text{ordered routed product},\\
\text{zero route}&\ne\text{spectral zero mode},\\
\text{fixed-depth profile equality}&\ne\text{full semigroup equality}.
\end{aligned}
$$

## Related Work and Novelty Boundary {.unnumbered}

Finite-field and projective-line arithmetic are standard background
\cite{lidlNiederreiter1997}. Finite automata, recognizable series, and their
rational representations are likewise classical \cite{berstelReutenauer2011}.
This paper does not claim those theories. Its contribution is the exact
translation from the declared marked modular route semantics to prefix-pole
constraints, together with characteristic-aware finite-depth classifications,
the induced survivor automata, and source-addressed exact evidence.

Paper XX \cite{paper20} and this paper belong to the same carrier/route
research line, but the results below do not invoke Paper XX's all-depth
carrier-accessibility theorem. No nontrivial direct-sum carrier decomposition
or Paper XX carrier-preservation certificate is registered for the marked
modular family. The classifications instead follow from the explicit
projective maps, their poles, and finite-field preimage arithmetic. Thematic
succession therefore does not establish theorem dependence.

The same exploratory Schreier source family previously supplied selected
finite actions for the exact static realization package of Paper VIII
\cite{paper8}. That promotion certifies a marked finite-permutation SOF
realization; it does not classify routed products by prefix poles. The present
route-profile evidence is promoted under a separate claim map and receipt
closure. Shared source provenance therefore does not transfer theorem
ownership or validation scope between the two papers.

A bridge to Paper XX would require a declared $(B,\{V_b\},\{\Pi_b\})$ and a
proof that every labelled generator and marked sector projector preserves
every carrier. Without that bridge, this paper is not a corollary,
specialization, or application of Paper XX.

---

## Marked Modular Carrier

Let $F$ be a finite field and let

$$
X_F=\mathbf P^1(F)=F\cup\{\infty\},
\qquad C_0=\{\infty\},\quad C_1=F.
$$

Use the labelled projective maps

$$
S(x)=-x^{-1},
\qquad R(x)=-(x+1)^{-1},
\qquad R^{-1}(x)=-1-x^{-1},
$$

with the fixed integral lifts

$$
\widetilde S=
\begin{pmatrix}0&-1\\1&0\end{pmatrix},
\qquad
\widetilde R=
\begin{pmatrix}0&-1\\1&1\end{pmatrix},
\qquad
\widetilde {R^{-1}}=
\begin{pmatrix}-1&-1\\1&0\end{pmatrix}
\in \operatorname{SL}_2(\mathbf Z).
$$

For the induced prefix lift

$$
\widetilde G_k(w)=
\begin{pmatrix}\alpha_k&\beta_k\\c_k&d_k\end{pmatrix},
$$

fix the primitive pole vector

$$
v_k(w)=(d_k,-c_k),
$$

under the usual projective identification up to sign. Then

$$
z_i(w)=z_j(w)
\iff
\det\bigl(v_i(w),v_j(w)\bigr)=0.
$$

Unimodularity makes every $v_k(w)$ primitive, so reduction modulo a prime
never sends it to the zero vector.

Their values at infinity are

$$
S(\infty)=0,
\qquad R(\infty)=0,
\qquad R^{-1}(\infty)=-1.
$$

Their poles are

$$
\pi_S=0,
\qquad \pi_R=-1,
\qquad \pi_{R^{-1}}=0.
$$

Labels remain distinct data even when represented maps coincide. A word
$[a_1,\ldots,a_d]$ acts left to right on states, so its operator product is
$P_{a_d}\cdots P_{a_1}$.

### Definition 2.1: Boolean-Supported Route

For a word $[a_1,\ldots,a_d]$ and source-to-target sector path
$(s_0,\ldots,s_d)$, the route is Boolean-supported when

$$
a_k(C_{s_{k-1}})\cap C_{s_k}\ne\varnothing
$$

for every $k$. It is a zero route when it is supported but

$$
Q_{s_d}P_{a_d}\cdots P_{a_1}Q_{s_0}=0.
$$

Equivalently, no carrier state follows the entire declared sector path.

---

## Depth-Two Classification

### Proposition 3.1: Support Shape Exhaustion

Every label has the common direct-support matrix, with target rows and source
columns,

$$
\begin{array}{c|cc}
 & C_0&C_1\\\hline
C_0&0&1\\
C_1&1&1
\end{array}
$$

Thus each ordered pair $[a,b]$ has exactly five supported shapes:

$$
(1,0,1),\ (0,1,0),\ (1,1,0),\ (0,1,1),\ (1,1,1).
$$

With nine ordered labelled pairs, the candidate count is $9\cdot5=45$.

*Proof.*

The displayed matrix is common to all three maps. The supported binary paths
of length two are exactly the five listed shapes.

### Theorem 3.2: Uniform Modular Zero-Route Classification

For every finite field $F$ with $|F|\ge3$, the declared carrier has exactly 14
zero routes among 45 supported labelled candidates. Hence

$$
\frac{|Z_2(F)|}{|B_2(F)|}=\frac{14}{45}.
$$

The shape decomposition is

$$
(0,1,0):4,
\qquad (1,1,0):5,
\qquad (0,1,1):5.
$$

*Proof.*

At infinity the first label gives $0$, $0$, or $-1$ for $S$, $R$,
or $R^{-1}$. From the intermediate value $0$, the second labels
$(S,R,R^{-1})$ give $(\infty,-1,\infty)$; from $-1$, they give
$(1,\infty,0)$.

The table supplies four zero routes of shape $(0,1,0)$ and five of shape
$(1,1,0)$, because the actual two-step value lands in the wrong target
sector. For shape $(0,1,1)$, the five remaining label pairs require, after
pole exclusions,

$$
S(x)=0,\quad S(x)=0,\quad R(x)=0,\quad R(x)=0,
\quad R^{-1}(x)=-1.
$$

These reduce to the impossible finite-field equation $x^{-1}=0$. The other
four source-finite cases have witnesses $1$, $0$, $-1$, and $-1$.

For $(1,0,1)$, the first-letter pole supplies a witness. For $(1,1,1)$, at
most two finite inputs are excluded by the two prefix poles. Since $|F|\ge3$,
one finite witness remains. The five shapes exhaust all candidates, giving
$4+5+5=14$.

### Corollary 3.3: Odd-Prime Form

For every odd prime $p$, the modular action on $\mathbf P^1(\mathbf F_p)$ has exactly 14 zero
routes among 45 candidates under this alphabet, partition, and route contract.
The prime assumption is stronger than needed: the theorem is finite-field
relative and includes extension fields of cardinality at least three.

---

## Depth-Three Classification

For $[a,b,c]$, write

$$
v_a=a(\infty),
\qquad \pi_a=a^{-1}(\infty),
\qquad e_{ab}=b(v_a).
$$

The eight supported sector shapes are

$$
0101,\ 0110,\ 0111,\ 1010,\ 1011,\ 1101,\ 1110,\ 1111.
$$

### Theorem 4.1: Depth-Three Shape Criteria

The route is nonzero exactly under the following shape-relative criteria:

$$
\begin{array}{c|l}
0101 & v_a=\pi_b\\
0110 & v_a\ne\pi_b\ \text{ and }\ e_{ab}=\pi_c\\
0111 & v_a\ne\pi_b\ \text{ and }\ e_{ab}\ne\pi_c\\
1010 & v_b=\pi_c\\
1011 & v_b\ne\pi_c\\
1101 & v_a\ne\pi_b\\
1110 & v_b\ne\pi_c\ \text{ and }\ e_{ab}\ne\pi_c\\
1111 & \text{some finite }x\text{ avoids all three prefix poles}
\end{array}
$$

*Proof.*

The first seven rows trace the unique singleton-sector state. A
finite-to-infinity step forces the preceding state to the corresponding pole;
a finite-to-finite step excludes that pole. The all-finite row requires
$x\ne\pi_a$, $a(x)\ne\pi_b$, and $b(a(x))\ne\pi_c$.

Its forbidden set is the union of at most three finite prefix preimages.

### Theorem 4.2: Characteristic-Aware Count

For every finite field $F$, with $q=|F|$,

$$
|Z_3(F)|=115+\mathbf 1_{\operatorname{char}F=2}
+19\mathbf 1_{q=2}+\mathbf 1_{q=3}.
$$

There are always 216 supported candidates.

*Proof.*

The first seven criteria reduce to equalities among $0$, $1$, $-1$,
and infinity. The relevant collapse is $1=-1$ in characteristic two. For
$1111$, at most three finite inputs are forbidden. Thus no zero occurs for
cardinality at least four in characteristic two or at least five in odd
characteristic. In $\mathbf F_3$, $[R^{-1},S,R]$ has three forbidden inputs
and gives the unique all-finite zero. In $\mathbf F_2$, exactly eight of the
27 words retain a finite witness, yielding 19 all-finite zeros. Summing the
shape contributions gives the formula.

**Exact shape decomposition.** The corresponding zero-route histograms are:

| regime | 0101 | 0110 | 0111 | 1010 | 1011 | 1101 | 1110 | 1111 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $\mathbf F_2$ | 12 | 22 | 20 | 12 | 15 | 15 | 20 | 19 | 135 |
| $\mathbf F_3$ | 12 | 23 | 19 | 12 | 15 | 15 | 19 | 1 | 116 |
| characteristic 2, $q\ge4$ | 12 | 22 | 20 | 12 | 15 | 15 | 20 | 0 | 116 |
| odd characteristic, $q\ge5$ | 12 | 23 | 19 | 12 | 15 | 15 | 19 | 0 | 115 |

The scalar total is not the complete invariant: $\mathbf F_3$ and characteristic-two
fields of cardinality at least four both have total 116 but different shape
histograms.

---

## Arbitrary-Depth Semantic Theory

For a word $w=[a_1,\ldots,a_d]$, put

$$
G_0=\operatorname{id},
\qquad G_k=a_k\cdots a_1,
\qquad z_k(w)=G_k^{-1}(\infty).
$$

Thus $z_k(w)$ is the initial point whose $k$th prefix image is infinity. For a
sector path $s=(s_0,\ldots,s_d)$, define

$$
I_0(s)=\{k:s_k=0\},
\qquad I_1(s)=\{k:s_k=1\},
$$

and

$$
\operatorname{Surv}_F(w,s)
=\{x:G_k(x)\in C_{s_k}\text{ for every }k\}.
$$

### Theorem 5.1: Arbitrary-Depth Prefix-Pole Classification

For every finite field, every positive depth, every labelled word, and every
sector path,

$$
\operatorname{Surv}_F(w,s)
=\bigcap_{k\in I_0(s)}\{z_k(w)\}
\cap
\bigcap_{k\in I_1(s)}\bigl(X_F\setminus\{z_k(w)\}\bigr).
$$

Consequently:

1. If $I_0(s)$ is empty, then

   $$
   \operatorname{Surv}_F(w,s)
   =X_F\setminus\{z_0(w),\ldots,z_d(w)\}.
   $$

2. If $I_0(s)$ is nonempty, the survivor set is a singleton exactly when all
   forced poles $z_k$, $k\in I_0(s)$, are equal to one point $z$ and no
   forbidden pole $z_j$, $j\in I_1(s)$, equals $z$. Otherwise it is empty.

Hence a supported route is zero exactly when the corresponding condition
above has empty survivor set.

*Proof.*

For every initial point $x$, one has $G_k(x)\in C_0$ exactly when
$x=z_k(w)$, and $G_k(x)\in C_1$ exactly when $x\ne z_k(w)$.

Intersecting these conditions over all prefix positions gives the displayed
identity. The two cases exhaust the possible sector paths.

**Scope.** This is an all-depth semantic classification, not an all-depth scalar count.
The number and collision pattern of the prefix poles can still vary with the
word, depth, and field.

### Generic Depth-$d$ Profile

Evaluate the fixed integral lifts over $\mathbf Q$. For a word $w$, declare prefix
indices equivalent when their rational projective poles agree:

$$
i\sim_w j
\iff
\det\bigl(v_i(w),v_j(w)\bigr)=0.
$$

Let $Z_d^{\mathrm{gen}}$ be the supported labelled routes that are zero under this
integral prefix-pole equality pattern. This definition is combinatorial: it
uses the finite word/sector-path indexing and the rational pole-collision
relation, not a selected finite field.

No declared letter fixes infinity. Hence consecutive prefix poles are
distinct, so no pole-equivalence class contains consecutive indices. Each
class therefore defines a Boolean-supported itinerary whose zero sectors are
exactly the indices in that class.

If $c(w)$ is the number of equivalence classes among the $d+1$ prefix poles,
then the generic nonzero itineraries for $w$ are exactly:

1. one itinerary for each prefix-pole class, with zeros at that class; and
2. the all-finite itinerary, represented by every rational point outside the
   finite prefix-pole set.

Therefore

$$
|Z_d^{\mathrm{gen}}|
=3^dF_{d+3}-\sum_{w\in A^d}\bigl(c(w)+1\bigr).
$$

This is the distinguished scalar sequence for future growth questions. It is
not yet supplied with a closed form or asymptotic law.

### Corollary 5.2: Fixed-Field Survivor Automaton

Fix a finite field $F$. A survivor state is a pair $(s,A)$ with
$A\subseteq C_s$. Begin in either $(0,C_0)$ or $(1,C_1)$. For a label $a$ and
an admitted target sector $t$, define

$$
\tau_{a,t}(s,A)=\bigl(t,a(A)\cap C_t\bigr),
$$

where the common support template admits every sector transition except
$0\to0$. Let $S_F$ be the states reachable from the two initial states. Then
$S_F$ is finite, with the elementary bound

$$
|S_F|\le 2+2^{|F|}.
$$

Empty-survivor states are retained rather than pruned. A Boolean-supported
route may become semantically dead before its terminal step and must still
contribute to $B_d(F)$ and $Z_d(F)$.

Moreover the second component after reading a route prefix is exactly its
current-image survivor set. Therefore the route is nonzero exactly when its
terminal survivor component is nonempty.

*Proof.*

The transition identity follows directly by applying the next
permutation and then imposing the next sector projector. Induction on prefix
length proves the survivor assertion. There are two subsets of the singleton
sector and $2^{|F|}$ subsets of the finite sector, so the reachable state set is
finite with the stated bound.

**Transfer setup.** Let $M_F$ be the nonnegative integer transition matrix of this automaton,
counting labelled $(a,t)$ transitions. Let $u_F$ select the two initial states,
$\mathbf 1$ be the all-state column, and $n_F$ indicate states with nonempty
survivor component.

### Corollary 5.3: Transfer Counts and Rational Generating Functions

For every $d\ge0$,

$$
B_d(F)=u_FM_F^d\mathbf 1,
\qquad
N_d(F)=u_FM_F^dn_F,
\qquad
Z_d(F)=B_d(F)-N_d(F).
$$

In particular,

$$
B_F(z)=u_F(I-zM_F)^{-1}\mathbf 1,
\qquad
N_F(z)=u_F(I-zM_F)^{-1}n_F,
$$

and $Z_F(z)=B_F(z)-N_F(z)$

are rational functions in $\mathbf Q(z)$ admitting numerator and denominator
polynomials in $\mathbf Z[z]$. This is fixed-field rationality:
$S_F$, $M_F$, and the reduced rational functions may change with $F$.

### Proposition 5.4: Boolean Candidate Count

For every positive depth $d$, the supported labelled route count is

$$
B_d=3^dF_{d+3},
$$

where $F_1=F_2=1$.

*Proof.*

There are $3^d$ ordered words. A sector path is supported exactly
when it has no consecutive zero sectors. The number of binary strings of
length $d+1$ without consecutive zeros is $F_{d+3}$.

**Generating function.** For $d\ge0$, the corresponding candidate generating function is

$$
B(z)=\frac{2+3z}{1-3z-9z^2}.
$$

### Theorem 5.5: Fixed-Depth Large-Field Stabilization

Use the fixed integral lifts above. For every word of length $d$, the induced
prefix matrix $\widetilde G_k(w)$ lies in $\operatorname{SL}_2(\mathbf Z)$,
and its primitive pole vector is $v_k(w)=(d_k,-c_k)$. Define the prefix
determinant spectrum

$$
D_d=
\left\{
\left|\det\bigl(v_i(w),v_j(w)\bigr)\right|:
w\in A^d,\ 0\le i<j\le d,\
\det\bigl(v_i(w),v_j(w)\bigr)\ne0
\right\}.
$$

Define $E_d$ as its prime support:

$$
E_d=\{\ell\text{ prime}:\ell\mid\Delta
\text{ for some }\Delta\in D_d\}.
$$

Both sets are finite. If a finite field $F$ satisfies

$$
|F|>d,
\qquad
\operatorname{char}F\notin E_d,
$$

then its complete labelled depth-$d$ zero-route set is the generic profile:

$$
Z_d(F)=Z_d^{\mathrm{gen}}.
$$

In particular, any two fields satisfying these conditions have identical
labelled depth-$d$ zero-route sets.

*Proof.*

Every prefix matrix is unimodular, so its integral pole vector is
primitive and remains a nonzero projective vector after reduction in every
characteristic. Outside $E_d$, reduction therefore preserves every equality
and inequality among the finitely many prefix-pole vectors: a projective
equality holds after reduction exactly when its integral determinant is zero.
By Theorem 5.1 this settles every path containing a zero sector. For the
all-finite path, at most $d+1$ prefix poles are forbidden, while
$|\mathbf P^1(F)|=|F|+1>d+1$; hence a survivor exists. The same argument
applies to every field satisfying the displayed conditions.

### Corollary 5.6: Monotonicity of Exceptional Characteristics

For every positive depth,

$$
D_d\subseteq D_{d+1},
\qquad
E_d\subseteq E_{d+1}.
$$

*Proof.*

Append any declared letter to a length-$d$ word. Its first $d+1$
prefix matrices and pole vectors are unchanged, so every determinant in
$D_d$ also occurs at depth $d+1$. Taking prime support gives the second
inclusion.

**Exact finite diagnostics.** The exact computational artifact gives the following arithmetic diagnostics:

| depth $d$ | $D_d$ | $E_d$ |
|---:|---|---|
| 1--2 | $\{1\}$ | empty |
| 3--4 | $\{1,2\}$ | $\{2\}$ |
| 5--6 | $\{1,2,3\}$ | $\{2,3\}$ |
| 7--8 | $\{1,2,3,4,5\}$ | $\{2,3,5\}$ |
| 9--10 | $\{1,2,3,4,5,7,8\}$ | $\{2,3,5,7\}$ |

This explains, rather than merely records, why characteristic five first
separates from the generic profile at depth seven: a nonzero prefix
determinant of absolute value five first enters $D_7$. The table is an exact
finite certificate for the displayed depths; Theorem 5.5 is the general
mathematical statement. No closed form for $D_d$ or $E_d$ is inferred from the
displayed pattern.

### Definition 5.7: Fixed-Depth Route Profile

The depth-$d$ profile records supported, nonzero, and zero counts; zero
histograms by sector path; per-word local counts; an exact zero-route-set
digest; and the exact positive-word image layer at depth $d$. The word-image
layer is separate: profile equality does not imply equality of word images or
full semigroup closures.

### Computational Certificate 5.8: Sampled Profiles

The exact certificate samples $p=2,3,5,7,11,13$ through depth five:

| depth | candidates | $p=2$ | $p=3$ | $p\ge5$ in sample |
|---:|---:|---:|---:|---:|
| 1 | 9 | 0 | 0 | 0 |
| 2 | 45 | 18 | 14 | 14 |
| 3 | 216 | 135 | 116 | 115 |
| 4 | 1053 | 810 | 742 | 732 |
| 5 | 5103 | 4374 | 4152 | 4094 |

An extended exact probe separates $p=5$ from $p\ge7$ at depths seven and
eight, consistently with $5\in E_7$. These tables remain fixed-depth
certificates; they do not supply an all-depth scalar formula or a limiting
growth law.

---

## Computational Evidence

The retained evidence uses exact finite permutations, finite-field arithmetic,
integral matrix lifts, and Python integers. No floating-point eigensolver or
thresholded zero test enters the recorded classifications.

The depth-three controls cover $\mathbf F_2,\mathbf F_3,\mathbf F_4,
\mathbf F_5,\mathbf F_7,\mathbf F_8$, and $\mathbf F_9$. The arbitrary-depth
replay checks the prefix-pole classification through depth five over
$\mathbf F_2,\mathbf F_3,\mathbf F_5$, and $\mathbf F_7$, constructs the
complete reachable automata for the declared sample fields, verifies transfer
counts through depth ten, and computes $E_d$ through depth ten. These finite
checks are Computational Certificates for the registered inputs; they do not
replace the manuscript proofs of Theorem 5.1, Corollaries 5.2--5.3 and 5.6,
or Theorem 5.5.

The compiled Lean surface covers Theorem 3.2, the complete depth-three shape
and count package, and Proposition 5.4. It does not cover the arbitrary-depth
prefix-pole theorem, fixed-field automata and rationality, the generic profile,
or fixed-depth stabilization and determinant-spectrum monotonicity. Lean type
checking and exact Python replay are distinct evidence paths; neither is
claimed to derive the other.

The source experiments retain their exploratory artifact identities.
Promotion forms new source-addressed evidence objects without rewriting those
sources in place.

---

## Interpretation Boundaries

These are finite marked-carrier theorems, not invariants of the abstract
presentation alone:

$$
\text{same presentation}\ne\text{same permutation action},
$$

and the same action with a different marked partition need not have the same
route profile.

A route zero is a projector-resolved labelled block vanishing. It is not a
Hecke eigenvalue, operator-kernel dimension, or modular-form zero. A future
Hecke connection would require an explicit double-coset correspondence,
averaging semantics, and an equivariance theorem. Cross-field stability is
likewise not an RG fixed point; RG language would require a coarse-graining
map, a contract state space, and a declared flow.

---

## Claim Status and Boundary

The reader-facing evidence levels are:

| Surface | Evidence level | Formalization status |
|---|---|---|
| Proposition 3.1, Theorem 3.2, and Corollary 3.3 | Theorem | compiled Lean source closure |
| Theorems 4.1--4.2 | Theorem | compiled Lean source closure |
| Theorem 5.1 | Theorem | manuscript proof with exact replay; Lean extension open |
| Corollaries 5.2--5.3 | Theorem | manuscript proof with exact construction; Lean extension open |
| Proposition 5.4 | Theorem | compiled Lean source closure |
| Theorem 5.5 and Corollary 5.6 | Theorem | manuscript proof with exact replay; Lean extension open |
| $D_d$, $E_d$, and sampled route-profile tables | Computational Certificate | source-addressed exact replay |
| unresolved uniform and asymptotic questions | Research Program | open |

No Computational Observation is promoted by this paper: every retained table
uses exact finite arithmetic. Formalization status is separate from the
reader-facing evidence level; a manuscript theorem does not become a
Computational Certificate merely because its proof is not yet in Lean.

No claim is made of arbitrary generator or partition invariance,
presentation-only universality, a field-independent finite automaton or state
bound, one rational function valid for every field, an all-depth closed scalar
formula, profile convergence, Hecke or modular-form content, Selberg or
Teichmuller content, RG content, or a spectral interpretation of *zero route*.

The remaining questions concern uniformity and minimization, not existence of
fixed-field automata, fixed-field rational series, or fixed-depth
stabilization.

## Conclusion

For the declared marked modular carrier, route survival at every positive
depth is controlled exactly by prefix-pole equality and exclusion. This gives
uniform depth-two and characteristic-aware depth-three classifications, an
all-depth semantic criterion, fixed-field survivor automata and rational
series, and fixed-depth large-field stabilization whenever $|F|>d$ and
$\operatorname{char}F\notin E_d$. The exact finite computations and the
compiled Lean subset support distinct parts of that theorem surface without
enlarging it.

The result is representation- and marking-relative. It does not promote
Boolean support to composition, a fixed-depth profile to a semigroup
invariant, or field-relative rationality to one uniform automaton. The next
mathematical problem is the arbitrary-depth structure of the generic route
language, not another fixed-depth classification.

## Outlook

The research order is:

1. **Generic route language.** Study the graded family
   $\mathcal Z^{\mathrm{gen}}=\bigsqcup_{d\ge0}Z_d^{\mathrm{gen}}$ and its
   scalar sequence $z_d^{\mathrm{gen}}=|Z_d^{\mathrm{gen}}|$.
2. **Prefix determinant algebra.** Determine recurrences, closure properties,
   or growth laws for $D_d$, $E_d$, and the pole-class sum
   $\sum_w c(w)$.
3. **Automaton quotient and minimization.** Replace raw survivor subsets by
   the coarsest state equivalence that preserves every future route decision.
   Fixed-field rationality alone does not imply a uniform automaton.
4. **Generic generating function.** Determine whether
   $G_{\mathrm{gen}}(t)=\sum_{d\ge0}z_d^{\mathrm{gen}}t^d$ is rational,
   algebraic, D-finite, or lies outside those classes.
5. **Asymptotic growth.** Only after the preceding structure is available,
   study the asymptotic quantity

   $$
   \limsup_{d\to\infty}(z_d^{\mathrm{gen}})^{1/d}
   $$

   and finer asymptotics.

Alphabet/partition comparison and any separate coarse-graining theory remain
independently scoped questions.

---

## Appendix A: Computational Artifacts {.unnumbered}

The computational package is available under `experiments/paper21/` in the
[RIME repository](https://github.com/dooven-prime/rime-lite). Paths in this
table are relative to that directory.

| Role | Public entry points |
|---|---|
| arbitrary-depth exact replay | `arbitrary_depth_semantic.py`; `validation/validate_arbitrary_depth_semantic.py` |
| source-addressed promotion | `validation/promote_route_profiles.py`; `validation/validate_route_profiles.py` |
| compiled Lean subset | `lean/`; `validation/validate_lean_formalization.py` |
| claim/evidence alignment | `claim-surface-map.json` |
| release closure | `release-manifest.json`; `validation/validate_release.py` |
| release receipt | `results/route_profiles_v1.release-receipt.json` |

The promotion, arbitrary-depth, and Lean receipts have distinct scopes. The
release receipt binds those records, the manuscript, PDF, producers,
validators, imported Lean sources, pinned dependency manifest, and hostile
tests. A receipt is excluded from its own ordered closure. Verification by the
same paper-owned validator is local closure verification, not independent
validation and not a proof of validator trust. The experiment README records
the exact receipt and closure digests together with the verification entry
points.

The Lean receipt binds only the formalized surface listed in Section 8. It
does not certify Theorem 5.1, Corollaries 5.2--5.3 and 5.6, or Theorem 5.5.
This paper publishes mathematical results and exact evidence; it is not a
protocol contract or a claim of independent validation.
