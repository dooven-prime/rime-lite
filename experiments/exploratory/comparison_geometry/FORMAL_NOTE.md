# Formal Note: Contextual Comparison and Descent

**Status:** mathematically defined presheaf/descent exploratory program with
exact finite results.

This note freezes the first formal prototype. It does not claim a sheaf theory
of SOF, a Grothendieck topology, a descent theorem, or a topos-level result.
Its purpose is to separate canonical restriction from resolution refinement
and aggregation, and to make finite gluing results epistemically typed.

## 1. The Canonical-Restriction Context Category

**Definition 1 (Observation Context).** An observation context is a finite
record

$$
C=(S_C,Y_C,P_C,\kappa_C,r_C,\theta_C),
$$

where $S_C$ is a finite retained sector-label set, $Y_C$ is a finite retained
observable-label set, $P_C$ is an optional finite parameter-label set,
$\kappa_C$ is a carrier, $r_C$ is a realization kind, and $\theta_C$ is a
convention package. The first prototype uses exact convention preservation.

The active carriers are `operator`, `word`, `lie`, `observable`, and `record`.
The active realization kinds are `strict_sof` and `diagnostic_analogue`. These
labels are data, not conclusions inferred from section values.

All sector, observable, parameter, carrier, realization-kind, family, and
convention-package labels are drawn from fixed set-sized registries. The
finite records and morphism triples therefore form a small first-stage
category; no proper-class-sized context universe is used.

**Definition 2 (Canonical Observation Restriction).** For contexts $C'$ and
$C$, a morphism $u:C'\to C$ is a triple of injective maps

$$
u_S:S_{C'}\hookrightarrow S_C,
\qquad
u_Y:Y_{C'}\hookrightarrow Y_C,
\qquad
u_P:P_{C'}\hookrightarrow P_C,
$$

together with the obligations

$$
\kappa_{C'}=\kappa_C,
\qquad
r_{C'}=r_C,
\qquad
\theta_{C'}=\theta_C.
$$

The injections are declared semantics-preserving inclusions or relabellings.
They are not arbitrary comparison maps. The current implementation verifies
totality on local labels, injectivity, ambient-label membership, and the three
typing equalities above.

**Definition 3 (The category $\mathcal C_{\mathrm{obs}}$).** Objects are the
finite Observation Contexts. Morphisms are Canonical Observation Restrictions.
The identity has identity label maps. Composition is componentwise function
composition.

**Proposition 1 (Context Category).** The objects and morphisms above form a
category.

**Proof.** Identity maps are injective and preserve all typed fields. A
composite of injective label maps is injective, and equality of carrier,
realization kind, and conventions is transitive. Associativity and the left
and right identity laws follow componentwise from the corresponding laws for
functions. $\square$

**Corollary 1 (Typed Full Subcategories).** There are no morphisms between
contexts with different carrier, realization-kind, or convention-package
labels. With exact convention identity, the category decomposes as

$$
\mathcal C_{\mathrm{obs}}
=
\bigsqcup_{\kappa,r,\theta}\mathcal C_{\kappa,r,\theta}.
$$

Equivalently, indexing only by $(\kappa,r)$ gives full typed subcategories,
each of which may further decompose by convention package. No connectedness
claim is made. In particular, a word-to-Lie, strict-to-analogue, or
convention-changing promotion is not a false morphism; it is not a morphism
in this category.

## 2. The Structural-Signature Presheaf

Fix for each carrier $\kappa$ a registered family-label set $A_\kappa$ and a
scalar payload set

$$
V_{\mathrm{scalar}}
=\mathbf{Bool}\sqcup\mathbf{Int}\sqcup\mathbf{Real}\sqcup\mathbf{String}.
$$

For $C$, let $K_{\mathrm{sig}}(C)$ be the carrier-qualified coordinate set

$$
K_{\mathrm{sig}}(C)
\subseteq
A_{\kappa_C}\times S_C\times S_C\times Y_C
\times(P_C\sqcup\{\bot\}),
$$

where family-specific admissibility may select a subset of the displayed
product. The prototype coordinate is

$$
(\alpha,\kappa_C,i,j,y,p).
$$

**Definition 4 (Structural Signature Section).** Define

$$
F_{\mathrm{sig}}(C)
$$

to be the set of finite typed partial maps

$$
s:D_s\longrightarrow V_{\mathrm{scalar}},
\qquad
D_s\subseteq K_{\mathrm{sig}}(C).
$$

Partiality is intentional: unavailable or unrequested coordinates need not be
manufactured.

For $u:C'\to C$, define $F_{\mathrm{sig}}(u)$ by retaining exactly those
coordinates whose sector, observable, and parameter labels lie in the images
of $u_S,u_Y,u_P$, then relabelling them with the corresponding inverse maps on
those images. Thus

$$
F_{\mathrm{sig}}(u):F_{\mathrm{sig}}(C)
\longrightarrow F_{\mathrm{sig}}(C').
$$

**Proposition 2 (Presheaf Functoriality).** The assignment

$$
F_{\mathrm{sig}}:\mathcal C_{\mathrm{obs}}^{\mathrm{op}}
\longrightarrow\mathbf{Set}
$$

is a contravariant functor. Explicitly,

$$
F_{\mathrm{sig}}(\operatorname{id}_C)
=\operatorname{id}_{F_{\mathrm{sig}}(C)},
$$

and for $C''\xrightarrow{f}C'\xrightarrow{g}C$,

$$
F_{\mathrm{sig}}(g\circ f)
=F_{\mathrm{sig}}(f)\circ F_{\mathrm{sig}}(g).
$$

**Proof.** For the identity, every coordinate is retained and each inverse
label map is the identity, so every section is unchanged. For composition, a
coordinate of $C$ survives restriction along $g\circ f$ exactly when each of
its labels lies first in the image of $g$ and then, after inverse relabelling,
in the image of $f$. This is exactly the condition for surviving restriction
along $g$ followed by $f$. On every surviving label,
$(g\circ f)^{-1}=f^{-1}\circ g^{-1}$ on the relevant images. The payload is
unchanged in both constructions, so the resulting partial maps agree
coordinatewise. $\square$

**Proposition 3 (Typed Preservation).** Restriction maps remain inside one
$\mathcal C_{\kappa,r,\theta}$ subcategory and preserve every coordinate
carrier.

**Proof.** The equality $\kappa_{C'}=\kappa_C$ is a morphism obligation, and
coordinate validation requires the coordinate carrier to equal its context
carrier. Realization kind and convention package are also preserved by the
defining morphism obligations. $\square$

## 3. Common Retained Context

**Definition 5 (Same-Realization Common Retained Context).** In the
same-carrier, same-realization-kind, and same-convention subcase, a common
retained context for $C_{\mathrm{ref}}$ and $C_{\mathrm{tar}}$ is an explicitly
declared span

$$
u_{\mathrm{ref}}:C^*\to C_{\mathrm{ref}},
\qquad
u_{\mathrm{tar}}:C^*\to C_{\mathrm{tar}}
$$

of Canonical Observation Restrictions. For sections $s_{\mathrm{ref}}$ and
$s_{\mathrm{tar}}$, same-frame comparison is

$$
\operatorname{Compare}_{C^*}
\left(
F_{\mathrm{sig}}(u_{\mathrm{ref}})(s_{\mathrm{ref}}),
F_{\mathrm{sig}}(u_{\mathrm{tar}})(s_{\mathrm{tar}})
\right).
$$

This is the canonical-restriction realization of the
same-realization-kind subcase of the Paper XIII alignment boundary:

> No same-frame comparison without a common retained context and two admitted
> restriction legs.

No pullback, pushout, or universal property is claimed for $C^*$. It is not
assumed to be a lattice-theoretic common refinement.

Paper XIII also admits strict-vs-analogue comparison through an explicit
alignment contract. Such a pair cannot admit the span above because $C^*$
cannot simultaneously have both realization-kind labels. A future typed
bridge may have the form

$$
T:F_{\mathrm{strict}}(C_s)
\dashrightarrow F_{\mathrm{analogue}}(C_a),
$$

but $T$ would not be a morphism of $\mathcal C_{\mathrm{obs}}$ and not an
$F_{\mathrm{sig}}$ restriction map. Thus alignment maps and restriction maps
remain distinct objects.

## 4. Finite Covers and Matching Families

**Definition 6 (Declared Finite Cover).** A declared finite cover of $U$ is a
finite family of Canonical Observation Restrictions

$$
\mathcal U=\{u_i:U_i\to U\}_{i=1}^m.
$$

This is not yet a Grothendieck cover. Different coverage predicates are kept
explicit. It is a sector-label cover when

$$
S_U=\bigcup_i u_{i,S}(S_{U_i}),
$$

and it covers a required interaction set $E_{\mathrm{req}}\subseteq
K_{\mathrm{sig}}(U)$ when

$$
E_{\mathrm{req}}
\subseteq
\bigcup_i (u_i)_\#(K_{\mathrm{sig}}(U_i)).
$$

Coverage of sector labels therefore need not imply coverage of pairwise or
higher-order relation coordinates.

**Definition 7 (Coordinate Embedding and Matching Family).** Every restriction
$u_i:U_i\to U$ induces an injective coordinate embedding

$$
(u_i)_\#:K_{\mathrm{sig}}(U_i)\hookrightarrow K_{\mathrm{sig}}(U)
$$

by forward relabelling. Define the coordinate overlap

$$
K_{ij}
=
(u_i)_\#K_{\mathrm{sig}}(U_i)
\cap
(u_j)_\#K_{\mathrm{sig}}(U_j).
$$

A family $s_i\in F_{\mathrm{sig}}(U_i)$ is matching when its ambient-coordinate
images satisfy

$$
(u_i)_\#s_i\big|_{K_{ij}}
=
(u_j)_\#s_j\big|_{K_{ij}}
$$

for every $i,j$, on coordinates where the partial sections are both defined.
This image-intersection formulation is used because the prototype does not
assume categorical pullbacks $U_i\times_U U_j$. Here $(u_i)_\#s_i$ only
reindexes the unchanged local payload along an injective coordinate embedding;
it is not an aggregation pushforward $q_!$.

## 5. Candidate-Space Descent Algorithm

Let

$$
G\subseteq F_{\mathrm{sig}}(U)
$$

be a declared finite candidate space. A `DescentBasis` binds its identifier,
completeness status, enumerator, validator, SHA-256 digest, and optional
completeness-evidence identifier. Its completeness status is `bounded`,
`exhaustive`, or `unspecified`. An exhaustive label requires an external
completeness-evidence reference; the reference itself is not self-proving.
The digest is computed from a duplicate-free finite set of section payloads
and is independent of their input order.

For a matching family $(s_i)$, the classifier computes exactly

$$
G_{\mathrm{match}}
=
\left\{
s\in G:
F_{\mathrm{sig}}(u_i)(s)=s_i
\text{ for every }i
\right\}.
$$

Its core algorithm is:

```text
validate the cover, matching family, DescentBasis, and candidate digest
G_match := empty list
for s in G:
    if Restrict(s, u_i) = s_i for every i:
        append s to G_match
if |G_match| = 0: return NO_GLOBAL_SECTION
if |G_match| = 1: return GLUED_UNIQUE
if |G_match| > 1: return GLUED_NONUNIQUE
```

Malformed cover legs, incompatible overlaps, absent candidate spaces, and
unsupported pushforwards terminate in separate typed states before this core
classification.

**Theorem 1 (Finite Classifier Soundness and Completeness Relative to $G$).**
For a valid declared finite cover, matching family, digest-closed finite
candidate space $G$, and corresponding `DescentBasis`, the classifier satisfies

$$
|G_{\mathrm{match}}|=1
\iff \texttt{GLUED\_UNIQUE},
$$

$$
|G_{\mathrm{match}}|>1
\iff \texttt{GLUED\_NONUNIQUE},
$$

and

$$
|G_{\mathrm{match}}|=0
\iff \texttt{NO\_GLOBAL\_SECTION},
$$

all relative to the declared $G$.

**Proof.** The enumeration loop visits every element of the finite set $G$
once. It appends $s$ if and only if all declared restriction equalities hold,
so the resulting list is exactly $G_{\mathrm{match}}$; this gives both
soundness and completeness of enumeration relative to $G$. The final branch
is an exhaustive and mutually exclusive partition of the nonnegative integer
$|G_{\mathrm{match}}|$ into zero, one, and greater than one. $\square$

The machine state `NO_GLOBAL_SECTION` is therefore candidate-relative. With a
bounded basis it means only that no matching element was found in $G$. It may
be read as nonexistence in $F_{\mathrm{sig}}(U)$ only when $G$ has been
independently certified exhaustive or an external obstruction theorem is
bound. `UNRESOLVED` means that no candidate space was supplied.

## 6. Canonical Three-Sector Minimal Example

Let the required global interaction coordinates be

$$
E_{\mathrm{req}}=\{AB,BC,AC\}.
$$

Take two global candidates

$$
s_0=(AB=1,BC=1,AC=0),
\qquad
s_1=(AB=1,BC=1,AC=1).
$$

The local contexts $U_{AB}$ and $U_{BC}$ cover the sector labels
$\{A,B,C\}$, but their induced interaction coordinates do not cover $AC$.
Hence

$$
F(u_{AB})(s_0)=F(u_{AB})(s_1),
\qquad
F(u_{BC})(s_0)=F(u_{BC})(s_1),
$$

while $s_0\neq s_1$. Therefore the observation map

$$
\rho_{\mathcal U}:G\longrightarrow
F(U_{AB})\times F(U_{BC})
$$

is not injective for $G=\{s_0,s_1\}$. The classifier returns
`GLUED_NONUNIQUE`. This is the canonical finite-candidate separatedness
counterexample.

Adding $U_{AC}$ and the local datum $AC=0$ separates the two candidates. The
matching set becomes $\{s_0\}$, so the classifier returns `GLUED_UNIQUE`
relative to $G$.

**Proposition 4 (Minimality Within the Pairwise Missing-Interaction Pattern).**
The example is minimal among pairwise signatures that exhibit two observed
relations sharing a sector label and one unobserved relation between the two
remaining endpoints.

**Proof.** With at most two sector labels there is at most one unordered
off-diagonal pair, so two observed relations with a third missing endpoint
pair cannot occur. Three labels admit exactly the pattern $AB,BC,AC$.
Nonuniqueness requires at least two distinct global candidates, and the two
candidates above suffice. The claim is only for this pairwise pattern; it is
not a universal minimality result over all presheaves or cover notions.
$\square$

The essential conclusion is

$$
\text{coverage of labels}
\not\Rightarrow
\text{coverage of interaction coordinates}.
$$

More generally, uniqueness relative to an admissible global space $G$ is
equivalent to injectivity of the restriction-observation map on $G$. For
pairwise signatures this turns cover sufficiency into a finite interaction-
graph problem; for higher-order signatures it suggests the corresponding
interaction-hypergraph problem.

## 7. Next Mathematical Program

The next step is not to choose a topology that makes a preferred presheaf a
sheaf. Candidate covers should first arise from Observation Context structure:

- sector-subset families that jointly cover $S_U$;
- observable subfamilies that jointly cover $Y_U$;
- parameter subdomains that jointly cover the declared parameter domain.

Their identity, pullback-stability, and transitivity properties must then be
tested before they define a candidate Grothendieck topology.

Different typed presheaves may have different descent behavior on the same
cover. In particular, a future raw-observable presheaf $F_{\mathrm{obs}}$ may
retain matrix-block data sufficient for unique gluing, while the derived
summary presheaf $F_{\mathrm{sig}}$ can fail separatedness because it omits
cross-context interactions. Establishing such a contrast would show exactly
which representation layer loses globally identifying information.

Resolution refinement and aggregation remain outside the first category. A
split such as $A\rightsquigarrow A_1\sqcup A_2$ does not canonically lift a
coarse section to fine sections. A fine-to-coarse map may admit an additional
family-specific pushforward

$$
q_!:F(C_{\mathrm{fine}})\longrightarrow F(C_{\mathrm{coarse}}),
$$

but existence and functoriality of $q_!$ must be proved separately for each
typed quantity. Additive bridge energy, Boolean support, word depth, Lie
depth, wall morphology, and analogue descriptors are not presumed to share
one aggregation law.

## 8. Controlled Claim Spine

| Object | Status | Boundary |
|---|---|---|
| $\mathcal C_{\mathrm{obs}}$ and canonical restrictions | Definition plus Proposition | first-stage typed category only |
| $F_{\mathrm{sig}}$ presheaf functoriality | Theorem | finite typed partial-map assignment |
| finite classifier equivalences | Theorem | sound and complete only relative to declared $G$ |
| `GLUED_NONUNIQUE` minimal witness | Computational Certificate | declared candidate space and cover |
| `NO_GLOBAL_SECTION` with bounded basis | Computational Certificate at finite scope | no absolute nonexistence claim |
| `NO_GLOBAL_SECTION` with exhaustive basis | Computational Certificate at declared exhaustive scope | completeness evidence remains external |
| natural cover class or Grothendieck topology | Research Program | not defined |
| general sheaf/descent/topos result | Research Program | not claimed |
