# SOF Objects

**Status:** public object-layer companion to Paper VIII, published as
version 2.0 under DOI
[10.5281/zenodo.21700863](https://doi.org/10.5281/zenodo.21700863). Paper VIII
remains the canonical source for its release-local definition. This companion
summarizes the carrier-qualified static objects, strict categories, matched
closure isomorphisms, and support-preservation and depth-monotonicity
theorems of that release.

SOF means **Sectorized Observable Framework**. The purpose of SOF is to provide
a sectorization-based observable architecture for cross-species comparison of
sectorized observables. Many RIME examples are representation-derived, but the
SOF object begins after a compatible sectorization and observable family have
been supplied. It is not a new physical model.

## Core Object

A finite operator SOF core is specified by

```text
F_op = (V, {Q_i}, Y)
```

where:

- `V` is a finite-dimensional complex Hilbert space;
- `{Q_i}` is a distinguished sector projector family;
- `Y={Y_a}` is a declared labelled operator alphabet.

Representations, graphs, Markov chains, controls, meshes, and other source
systems enter through adapters that realize these three strict objects. The
source object itself is not substituted for `V`.

The operator alphabet may consist of generators, averaged operators, transfer
operators, rate operators, adjacency/Laplacian operators, or filtration
observables. Its label map, multiplicities, adjoint convention, and word
alphabet are part of the typed realization.

The associated static layers are kept separate:

```text
D_Q        = span_C{Q_i}                    marked sector algebra
E_Y        = span_C{I,Y_a,Y_a^*}            observable operator system
S_QY       = D_Q + E_Y                      sector-enriched operator system

A_Y^+      = alg_C(I,Y)                     positive associative word algebra
A_Y^*      = C^*(Y)                         observable star-closure
A_QY^*     = C^*(D_Q union Y)               sector-enriched star-closure
```

An optional Lie/Hall enrichment is independently registered as `(X,H_Hall)`.
It does not follow automatically from `Y`, `E_Y`, or any generated closure.

The distinction is structural:

```text
closure     answers what is generated after saturation
filtration  records how, along which routes, and at what first length it is generated
```

Passing from the labelled alphabet to an operator system or generated algebra
forgets generator labels and first-hit word length. Adding `D_Q` to the
star-closure additionally permits sector projectors as internal route
separators. Thus positive-word, star-word, and sector-enriched routed
saturation are not interchangeable.

## Sectorization Interface

The program separates three layers:

```text
source system
  -> admissibility or realization gate
  -> compatible sectorization
  -> registered observable families
  -> typed observable shadows
```

Sectorization is the interface that turns source data into SOF data. Its origin
may be representation-theoretic, geometric, filtration-based, graph/coloring
based, activation-based, control/PDE-based, or externally chosen. It determines
the language in which spectral geometry, accessibility geometry, and genericity
can be compared.

## Sectorization Necessity

The hidden reason for the sectorization step is:

```text
no sectors -> no sector shadows
```

A source system may have global observables without a sectorization.  But
the RIME observables are projected shadows.  They are built from blocks

```text
Q_i X_a Q_j.
```

Without the projectors `{Q_i}`, the following objects are not defined:

- sector-to-sector support;
- bridge products through intermediate sectors;
- frozen pairs;
- repair;
- routed, word, or Lie first-depth matrices;
- accessibility walls as changes of sector shadows.

With the trivial one-sector decomposition `{I}`, global observables remain but
the cross-sector shadows collapse.  This is the **Sectorization Necessity
Principle**, or equivalently the **No-Sector No-Shadow Principle**.

## Active Typed Middle Skeleton

The active SOF object architecture is:

```text
spectral admissibility gates, when sectors are spectrally derived
  -> typed sector fields
  -> operator / routed-composition / full-word branch
     and a separate Lie / Hall branch
  -> branch-specific promotion or comparison certificates
```

For a spectrally derived moving sectorization, the admissibility chain is

```text
Sigma_spec subseteq Sigma_normal subseteq Sigma_comm subseteq M
  -> {Q_i(w)}.
```

Here `Sigma_spec` is a normal spectral chart with coherent projector labels,
constant ranks, and the separation or contour data needed for the regularity
being claimed. Commutativity alone is not enough. Externally fixed,
graph-derived, control-derived, or otherwise non-spectral sectorizations begin
with declared projector fields on their own admissibility domain and do not
acquire fictitious spectral gates.

Once sectors exist, two carrier types are kept separate:

```text
operator field:  (Q, Y), with Y={Y_a} a registered operator family
Lie/Hall field:  (Q, X, H), with X={X_g} a registered Lie family
                              and H a declared filtration
```

The operator branch contains:

```text
R_1[Y]          direct projected-block support
Route_d[Y]      support of routed projected products
W_d[Y]          support of full ordered words
D_route[Y]      first routed-composition depth
D_word[Y]       first full-word depth
```

For complete sectorizations, the exact support relations satisfy

```text
W_d[Y] subseteq Route_d[Y] subseteq Path_d(R_1[Y]).
```

Here `Path_d(R_1[Y])(i,j)` means an aggregate directed support path of exactly
`d` steps from `j` to `i`. It forgets generator labels and does not require
label compatibility across adjacent edges. Repeated vertices are allowed, and
a self-loop step is allowed only when the corresponding aggregate diagonal
support is nonzero. These conventions keep the path shadow broad enough to
contain routed products with diagonal intermediate steps. Off-diagonal
accessibility still uses endpoint pairs `i != j`.

Neither reverse promotion is automatic: graph paths can die by image--kernel
incidence, and nonzero routed terms can cancel in the full word sum.
`C_d[Y]` remains a compatibility symbol for the frozen Papers III and VII
interfaces; active SOF writing uses `Route_d[Y]`.

The three saturated corner families are

```text
A_ij^+    = Q_i A_Y^+ Q_j
A_ij^*    = Q_i A_Y^* Q_j
A_ij^Q,*  = Q_i A_QY^* Q_j
```

All three are automatically nonzero on the diagonal because their defining
unital algebras contain `I`, so `Q_i I Q_i = Q_i`. Saturated Boolean support is
therefore informative without qualification primarily for `i != j`. A
nontrivial diagonal audit must use a scalar-reduced corner, for example the
Hilbert--Schmidt complement

```text
A_ii^bullet intersect (C Q_i)^(perp_HS)
```

or the corresponding vector-space quotient by `C Q_i`. Registry and wall
records must state whether saturated support is off-diagonal or
scalar-reduced diagonal support.

The Lie/Hall branch contains:

```text
R_1^Lie         direct support of the registered X_g
R_2^Lie         simple-commutator support
D_Lie           first depth in the declared Hall/Lie filtration
```

The two branches are not identified. In particular,
`R_1^op != R_1^Lie`, `W_d^X != R_d^Lie`, and
`D_word != D_Lie` without an additional theorem and compatible registrations.
An exact finite first-hit value at depth `d` requires both a level-`d` witness
and verified non-hits at every lower level; the witness alone gives only an
upper bound. Before a closure certificate exists, an unseen numerical pair is
recorded as `unreached` at a declared cutoff, never as mathematical infinity.

Promotion certificates are therefore branch-specific. Examples include:

- graph path to routed product: image--kernel nondegeneracy;
- routed products to a full word: control of cancellation among routes;
- operator family to Lie family: an explicit branch, normalization, and
  registration bridge;
- low-order Lie support to Lie depth: a declared closure or richness theorem;
- continuous proxy to discrete shadow: a threshold- and margin-stable
  proxy/shadow theorem.

A smooth family may package typed jets such as `J_op`, `J_comp`, `J_word`, and
`J_Lie`. The old name `J_acc` is retained only when its typed components are
listed. Likewise, `Sigma_access` denotes only a declared union or package of
typed discriminants, not one primitive universal wall.

## Claim-Status Boundary

Examples in Paper VIII are illustrative rather than new numerical evidence.
Its theorem layer is structural and functorial:

```text
declared SOF data
  -> well-defined typed constructions
  -> support preservation and target-depth monotonicity under strict morphisms
```

Deformation behavior, rate hierarchy, and observable dynamics belong to Paper
IX.

## Report Admission Boundary

Paper VIII owns the strict finite object

```text
F_op = (V, {Q_i}, Y).
```

Paper XII v2.0 uses two mutually exclusive report kinds. `strict_sof` requires
this finite complex object and structural validation. `diagnostic_analogue`
records provenance-bound descriptors and an analogue mapping without claiming
membership in the strict category. Source-map status (`native`,
`adapter-derived`, or `migrated`) is independent of record kind, and evidence
status is independent of both.

Different strict realizations of the same source need not be equivalent.
Different analogue mappings need not be comparable. Neither record kind
determines claim strength, and an analogue does not become strict by
accumulating observations.

## Paper VIII Boundary

Published Paper VIII version 2 owns its release-local static definition:

- the marked sector algebra and labelled operator alphabet;
- the operator-system and saturated-algebra layers;
- separate routed-product and full-word filtrations;
- an optional independently registered Lie/Hall enrichment;
- strict carrier-qualified morphisms;
- separate operator/word and Lie/Hall functoriality theorems.

Paper VIII does not own:

- deformation geometry;
- observable dynamics and wall behavior;
- universal comparison between unrelated SOFs;
- unconditional promotion from low-order Lie support to `D_Lie`, or from any
  operator/word branch to a Lie-depth object.

The later deformation, Registry, wall-classification, diagnostic-reporting,
and aligned-comparison layers are assigned in
[PROGRAM_MAP.md](PROGRAM_MAP.md) rather than duplicated here.
