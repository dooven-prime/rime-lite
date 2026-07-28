# RIME Program Overview

RIME (Representation-Induced Mechanics and Evolution) studies how spectral,
transport, accessibility, and deformation structures arise in
finite-dimensional represented systems. The Rubik cube provides a concrete,
reproducible, and highly noncommutative laboratory. It is used as a
representation-theoretic testbed, not as a puzzle-solving problem.

The public program currently contains Papers I--XIII. Papers I--VII are
independent version-2 papers, and Papers VIII--XIII retain their published
release-local semantics unless explicitly reopened. The canonical publication
list is the root [Public Release table](../README.md#public-release).

## Central Architecture

RIME asks what information survives each passage from a represented system to
observable behavior:

```text
represented system
  -> compatible sectorization
  -> registered observable family
  -> typed support and composition data
  -> deformation or comparison diagnostics
```

When the sectors vary with parameters, the spectral carrier must first pass
the admissibility gates

```text
Sigma_comm -> Sigma_normal -> Sigma_spec -> {Q_i(w)}.
```

Commutativity alone does not supply orthogonal sectors, and pointwise
diagonalization alone does not supply coherent projector fields.

After sectorization, the operator and Lie constructions form separate
branches:

```text
operator branch:
  R_1[Y] -> routed products C_d[Y] -> full words W_d[Y]
         -> D_route[Y], D_word[Y]

Lie branch:
  R_1^Lie -> R_2^Lie -> D_Lie
```

These arrows indicate construction order, not automatic promotion. Boolean
paths, projected products, word sums, commutators, and Lie depth are distinct
objects. Each promotion requires its own nondegeneracy, cancellation,
saturation, or comparison certificate.

## Program Arc

### Papers I--III: Rubik-Centered Foundations

- **Paper I** studies block spectral structure and conditional arithmetic
  criteria for averaging operators.
- **Paper II** studies sector non-invariance, projected generator blocks, and
  the registered direct transport graph.
- **Paper III** separates support-graph reachability from projected matrix
  composition through the image--kernel obstruction.

These papers are self-contained. Their compatible interfaces do not form a
Paper I -> Paper II -> Paper III theorem chain.

### Papers IV--VII: Geometry and Promotion Limits

- **Paper IV** studies collision quotients of a fixed finite affine-branch
  arrangement and gives only a conditional exact Rubik interpretation.
- **Paper V** separates direct support, routed products, full words,
  commutator support, and Lie depth on a fixed sectorized system.
- **Paper VI** gives linearized commutativity/normality certificates and
  normality-gated pointwise registrations, not a moving-wall theorem.
- **Paper VII** studies fixed-rank image--kernel incidence, rank protection,
  and the limits of graph-to-route and low-order-to-depth promotion.

These are neighboring self-contained interfaces. Paper IV keeps its
arrangement fixed; Paper VI treats moving spectral fields only as a gated
research target; Paper VII does not assert a generic completion theorem.

### Papers VIII--XIII: Sectorized Observable Framework

- **Paper VIII** introduces the static SOF object language and strict
  morphisms.
- **Paper IX** studies observable trajectories, deformation geometry, and
  wall diagnostics.
- **Paper X** formulates the Universal Observable Pipeline and maintains
  Registry evidence.
- **Paper XI** organizes observable wall records and classification
  boundaries.
- **Paper XII** defines the SOF Report protocol and its machine-readable
  single-system contract.
- **Paper XIII** defines aligned report comparison and factual audit
  signatures.

The current published terms in Papers VIII--XIII are release facts. Migrating
them to the branched typed architecture requires versioned paper, artifact,
figure, and Registry updates. The frozen Paper X Registry v1 snapshot is not
silently rewritten.

## Claim Discipline

RIME keeps four reader-facing claim levels separate:

| Level | Meaning |
|-------|---------|
| Theorem | exact statement proved from declared hypotheses |
| Computational Certificate | reproducible finite computation tied to declared inputs |
| Computational Observation | bounded numerical pattern without theorem promotion |
| Research Program | proposed extension, conjectural bridge, or open problem |

Numerical residuals do not prove exact arithmetic identities. A finite atlas
does not prove a generic completion theorem. A proxy trajectory does not prove
a binary support or depth transition without an explicit proxy-to-shadow
bridge.

## Rubik and General Theory

Rubik-specific records include the 228-dimensional cubie realization, the
standard 18 face-turn family, six registered averaging layers, nine registered
QT/HT sectors, and the sparse direct transport graph. These records provide a
finite calibration laboratory.

The general objects are averaging operators, compatible sectorizations,
collision arrangements, projected compositions, word and commutator support,
incidence varieties, normal spectral charts, observable deformations, and
aligned report comparisons. A Rubik computation becomes a general theorem only
when the abstract hypotheses and the promotion step are stated and proved.

## Reading Further

- [Public documentation index](README.md)
- [Detailed program map](PROGRAM_MAP.md)
- [Paper ownership and scope](PAPER_SCOPE.md)
- [Rubik-as-laboratory philosophy](PROGRAM_PHILOSOPHY.md)
- [Experiment and reproducibility map](../experiments/README.md)
