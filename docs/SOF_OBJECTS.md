# SOF Objects

**Status:** public object-layer companion to Paper VIII, published as
DOI [10.5281/zenodo.21287278](https://doi.org/10.5281/zenodo.21287278). Paper
VIII remains the canonical source for the published v1 definition and
naturality theorem. This companion also records the active typed-object
migration; that migration does not retroactively strengthen the published
theorem or alter frozen artifacts.

SOF means **Sectorized Observable Framework**. The purpose of SOF is to provide
a sectorization-based observable architecture for cross-species comparison of
sectorized observables. Many RIME examples are representation-derived, but the
SOF object begins after a compatible sectorization and observable family have
been supplied. It is not a new physical model.

## Core Object

A finite SOF is specified by

```text
F = (V, {Q_i}, X)
```

where:

- `V` is a finite-dimensional representation, state, Hilbert, graph, control,
  mesh, or other finite source space;
- `{Q_i}` is a distinguished sector projector family;
- `X` is a chosen observable family.

The observable family may consist of generators, averaged operators, transfer
operators, rate operators, adjacency/Laplacian operators, or filtration
observables. The origin of the family is not part of the published SOF
definition. In the active typed architecture, however, its registration type
is part of the realization: a general operator family and a Lie/Hall family do
not induce the same higher constructions merely because both are denoted by
operators.

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
C_d[Y]          support of routed projected products
W_d[Y]          support of full ordered words
D_route[Y]      first routed-composition depth
D_word[Y]       first full-word depth
```

For complete sectorizations, the exact support relations satisfy

```text
W_d[Y] subseteq C_d[Y] subseteq Path_d(R_1[Y]).
```

Neither reverse promotion is automatic: graph paths can die by image--kernel
incidence, and nonzero routed terms can cancel in the full word sum.

The Lie/Hall branch contains:

```text
R_1^Lie         direct support of the registered X_g
R_2^Lie         simple-commutator support
D_Lie           first depth in the declared Hall/Lie filtration
```

The two branches are not identified. In particular,
`R_1^op != R_1^Lie`, `W_d^X != R_d^Lie`, and
`D_word != D_Lie` without an additional theorem and compatible registrations.
Before a closure certificate exists, an unseen numerical pair is recorded as
`unreached` at a declared cutoff, never as mathematical infinity.

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
Its theorem layer is definitional and structural:

```text
SOF data -> natural observable constructions.
```

Deformation behavior, rate hierarchy, and observable dynamics belong to Paper
IX.

## Applicability Boundary

Paper VIII owns the formal core of the SOF Applicability Hierarchy:

```text
Level I  Definitional applicability
         explicit finite SOF object satisfying the axioms

Level II Realizational applicability
         reproducible source system -> SOF construction
```

Realizational applicability must identify the finite space, sectorization
origin, observable extraction, truncation, and any non-uniqueness. Different
realizations of the same source system need not be equivalent; equivalence
requires a separate strict or weak comparison argument. Neither
level determines claim strength: a valid object may support a theorem,
evidence, a diagnostic, or only a boundary statement. Diagnostic and
analogical applicability are Paper XII methodology levels rather than objects
of the strict category.

## Paper VIII Boundary

Published Paper VIII owns:

- SOF definition;
- compatible-sectorization realization / Sectorized Realization Theorem;
- strict SOF morphisms;
- the strict category `SOF_str`;
- its release-local natural constructions on SOF data;
- its release-local naturality theorem under strict equivalence.

A future typed revision must state separate carrier-qualified functors and
their filtration or saturation hypotheses. The v1 proof strategy may be
reusable, but the old unqualified `R_1/R_2/D` ladder is not the active
cross-paper object architecture.

Paper VIII does not own:

- deformation geometry;
- observable dynamics and wall behavior;
- universal comparison between unrelated SOFs;
- unconditional promotion from low-order Lie support to `D_Lie`, or from any
  operator/word branch to a Lie-depth object.

The later deformation, Registry, wall-classification, diagnostic-reporting,
and aligned-comparison layers are assigned in
[PROGRAM_MAP.md](PROGRAM_MAP.md) rather than duplicated here.
