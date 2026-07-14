# SOF Objects

**Status:** object-layer routing note for Paper VIII and later SOF work. This
file records what belongs to the static object theory and preserves claim
boundaries; it does not replace the Paper VIII manuscript proofs.

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
observables. The origin of the family is not part of the SOF definition.

## Sectorization Interface

The program separates three layers:

```text
source system
  -> compatible sectorization
  -> SOF
  -> observable shadows
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
- first-depth matrix `D(i,j)`;
- accessibility walls as changes of sector shadows.

With the trivial one-sector decomposition `{I}`, global observables remain but
the cross-sector shadows collapse.  This is the **Sectorization Necessity
Principle**, or equivalently the **No-Sector No-Shadow Principle**.

## Natural Shadows

The main RIME shadows are:

```text
R_1        support / direct transport shadow
R_2        commutator-survival shadow
D          first-depth accessibility shadow
J_acc      accessibility jet in smooth SOF families
Sigma_spec spectral-chart domain for moving projectors
Sigma_access accessibility discriminant
```

These are natural constructions once the SOF and the relevant filtration or
smooth family have been specified. They are not universal completeness
theorems by themselves.

## Claim-Status Boundary

Paper VIII may use examples, but it should not use them as new numerical
evidence. Its theorem layer is definitional and structural:

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

Paper VIII should own:

- SOF definition;
- compatible-sectorization realization / Sectorized Realization Theorem;
- strict SOF morphisms;
- the strict category `SOF_str`;
- natural constructions on SOF data;
- naturality of accessibility observables under strict equivalence.

Paper VIII should not own:

- deformation geometry;
- observable dynamics and wall behavior;
- universal comparison between unrelated SOFs;
- unconditional `(R_1,R_2) -> D` completeness.

Those belong to Papers IX and X.
