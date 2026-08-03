# Pre-SOF Interface Map

This companion records the public interface roles of Papers I--VII. It keeps
their technical boundaries out of the one-page [RIME Program Map](PROGRAM_MAP.md)
while avoiding a new source of release status or numerical values.

The papers are neighboring, self-contained interfaces. Their ordering is
thematic, not a theorem dependency chain.

## 1. Two Input Families

### Spectral and sector interfaces

This family asks how represented source structure supplies operators, spectral
layers, compatible sectors, collision data, and admissible spectral samples.

```text
represented operator family
  -> block or joint spectral data
  -> compatible sectorization
  -> fixed collision arrangement or gated spectral sample
```

The final arrow is not automatic. Collision quotients and moving spectral
registrations require their own hypotheses.

### Transport and accessibility interfaces

This family asks what labelled generators do between declared sectors and what
additional conditions allow direct support to promote to composition or
higher-depth witnesses.

```text
labelled generator blocks
  -> direct support
  -> projected products or full words
  -> commutator or Lie/Hall witnesses when separately registered
```

Each arrow is an audit order. Boolean paths, nonzero projected products, full
words, commutators, and finite-depth Lie witnesses are distinct objects.

## 2. Paper Roles

| Paper | Interface owned | Primary boundary |
|-------|-----------------|------------------|
| I | block spectral decomposition and conditional arithmetic criteria | blockwise numerical or algebraic structure does not become a universal arithmetic theorem |
| II | compatible QT/HT sectors, labelled projected blocks, and direct support | direct support records nonzero blocks, not routed composition or Lie depth |
| III | comparison of support-graph paths with projected matrix products | a graph path may fail through image--kernel incidence or cancellation |
| IV | fixed affine-branch collision arrangement and quotient structure | the abstract arrangement is exact; a represented Rubik interpretation is conditional on registration |
| V | separation of direct support, routed products, full words, commutators, and cutoff depth | one carrier cannot fill another carrier's field |
| VI | linearized commutativity/normality constraints and normality-gated point registrations | pointwise certificates do not provide coherent moving projectors or a wall theorem |
| VII | fixed-rank image--kernel incidence, rank protection, and promotion limits | finite examples or atlas coverage do not prove generic completion |

## 3. Spectral Interfaces

### Paper I: represented spectral layers

Paper I starts with a declared represented averaging operator and studies its
block spectral structure. Arithmetic conclusions remain conditional on the
stated hypotheses. Spectral decomposition does not by itself choose every
later sectorization, observable alphabet, or accessibility carrier.

### Paper IV: fixed collision arrangements

Paper IV treats a fixed finite affine-branch arrangement. Equality of declared
branch values produces collision relations and quotient layers inside that
arrangement. A numerical operator family inherits this structure only through
a separately checked registration. Paper IV does not own moving charts or wall
pullbacks.

### Paper VI: admissibility before motion

Paper VI enforces the order

```text
Sigma_comm -> Sigma_normal -> Sigma_spec -> pointwise spectral registration.
```

Its Jacobian audits are linearized Computational Certificates. They do not
establish nonlinear manifold dimensions. Its accepted samples are pointwise
registrations. They do not establish coherent label continuation or a complete
deformation category; those dynamic objects belong to Paper IX.

## 4. Transport and Accessibility Interfaces

### Paper II: labelled direct transport

Paper II records the labelled tensor of projected generator blocks and its
aggregate direct support. The labels are part of the data. Replacing the
family by an aggregate graph loses which generator realizes a channel and
cannot recover routed products, word length, or commutator structure.

### Paper III: support is not composition

Paper III isolates the gap between graph reachability and nonzero projected
matrix composition. Even when adjacent blocks are nonzero, their product may
vanish because the image of one factor lies in the kernel of the next. This is
the image--kernel obstruction.

### Paper V: carrier separation

Paper V keeps the following registrations distinct:

```text
direct operator support
routed projected products
full associative words
simple commutator support
cutoff Lie depth
```

The distinction is semantic, not merely notational. `compute_length_two_support`
is word support when it computes associative words; it is not commutator
support. Associative products of Lie generators are diagnostics unless a Lie
or Hall rule explicitly registers them.

### Paper VII: promotion conditions

Paper VII studies fixed-rank incidence conditions that control whether nonzero
projected factors compose. Rank protection, image--kernel nonincidence,
cancellation control, and saturation are examples of promotion hypotheses.
They are not consequences of Boolean reachability.

Its finite atlas and counterexamples delimit the promotion problem. They do
not establish a universal or represented generic-completion theorem.

## 5. Interface into Paper VIII

Paper VIII provides the static SOF object language into which compatible
pre-SOF data may be registered:

```text
F_op = (V, {Q_i}, Y)
```

The sector projectors and labelled observable family remain part of the data.
An optional Lie/Hall carrier is registered independently. Papers I--VII may
supply examples, source structure, or promotion certificates, but no one
paper automatically supplies every field of the static SOF object.

## 6. Promotion Checklist

Before promoting a pre-SOF record, identify:

1. the owning carrier and labelled family;
2. the marked sectorization and its provenance;
3. the composition, word, commutator, or Hall convention;
4. the cutoff and whether depth is exact or truncated;
5. the nonincidence, cancellation, saturation, or comparison hypothesis;
6. the evidence level and source-addressed artifact.

If any item is absent, retain the narrower source claim.

## 7. Numerical Authority

This companion intentionally omits certificate payloads such as ranks,
nullities, singular values, support counts, residuals, and census totals. Those
values belong to the owning manuscript, result record, and validator. See
[experiments/README.md](../experiments/README.md) for artifact routing.
