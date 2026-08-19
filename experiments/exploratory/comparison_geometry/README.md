# Comparison Geometry Exploratory Programs

**Research status:** typed comparison research programs with exact finite
controls.

**Execution status:** runnable with the repository Python environment using
the commands below.

**Paper evidence:** none by package placement. Paper XIII may register one
exact source-addressed control without promoting the package as a whole.

This directory contains two distinct comparison programs. The contextual
descent package studies how typed SOF data restricts to smaller observation
contexts, enters a common retained comparison context, and passes or fails
finite gluing controls. The BCH package freezes one exact composition
signature and tests how two already retained signatures could be compared
under an explicit generator alignment. Neither program is a continuation of
Paper IX deformation theory, and neither consumes Paper XIV `ActionContext`
or policy objects.

The `cross_fiber_compare.py` filename is retained for source compatibility;
that earlier control remains the source-level bridge-energy aggregation
example. Its active object language is **contextual comparison and descent**.

## Candidate Objects

The first-stage context category contains finite `ObservationContext` objects.
Its arrows are only canonical restrictions:

```text
u: C_local -> C_ambient
F(u): F(C_ambient) -> F(C_local).
```

An arrow may retain sector, observable, and parameter subsets or apply an
injective semantics-preserving relabelling. It must preserve carrier,
realization kind, and conventions. In particular, it cannot silently map word
data to Lie data or strict data to analogue data.

`ResolutionRefinement` and `AggregationPushforward` are separate witness
types. A split such as `A -> {A1,A2}` does not define a canonical lift of a
coarse signature, and an aggregation has no pushforward until a
family-specific law is supplied.

The prototype supplies:

- [`FORMAL_NOTE.md`](FORMAL_NOTE.md): definitions, local propositions, and
  candidate-relative claim boundaries;
- `context_objects.py`: finite observation contexts and typed coordinates;
- `typed_morphisms.py`: identity, composition, and the restriction/refinement
  boundary;
- `presheaf_signatures.py`: carrier-preserving signature restriction;
- `common_context.py`: explicit common retained contexts and same-frame
  comparison in the same-realization canonical-restriction subcase;
- `finite_descent.py`: finite candidate-space gluing classification;
- `canonical_minimal_example.py`: the canonical `AB`/`BC`/`AC`
  separatedness counterexample and strengthened cover;
- `separating_cover_theorem.py`: finite difference-support separation and
  constraint-scope controls used by the AB/BC/AC comparison case;
- `aggregation_pushforward.py`: rejection of uncontracted pushforwards;
- `gluing_hostile_cases.py`: executable positive and hostile controls.
- [`bch_composition/`](bch_composition/): a separately frozen Heisenberg BCH
  carrier, structured generator alignment, exact signature replay, and hostile
  comparison controls.

## BCH Composition Candidate

The BCH package consumes a declared Paper VIII-style Lie/Hall carrier to
produce a replayable local signature. A future Paper XII optional report
module may retain that signature and its evidence. Only then may a Paper XIII
optional Audit Profile compare two retained coordinates under a separately
declared generator alignment. Paper XIII does not recompute BCH coefficients
from raw generators.

The current implementation is deliberately narrow: exact rational arithmetic
on the class-two Heisenberg carrier. It proves the finite ordered control
`BCH(X,Y) != BCH(Y,X)` at degree two in that carrier, but it is not yet a
SOFRS module, SOFAUDIT coordinate, or registered runtime evaluator. The
eventual evaluator registry and receipt replay closure belong in
`sof-runtime`.

## Finite Descent Control

The gluing control deliberately tests existence and uniqueness separately.
Two local contexts retaining sectors `AB` and `BC` agree on their overlap but
do not observe the cross-context relation `A-C`. Two global sections that
differ only on `A-C` therefore have the same local restrictions, yielding
`GLUED_NONUNIQUE`. This is the finite-candidate analogue of a separatedness
failure: the restriction map is not injective on the compatible locus. Adding
an `AC` context distinguishes them and yields `GLUED_UNIQUE` in the declared
finite candidate set.

The formal note proves, for the declared finite typed partial-map assignment,
that `F_sig` is a contravariant functor on the canonical-restriction context
category. It also proves the descent classifier sound and complete relative to
its digest-bound finite candidate set `G`. Neither proposition supplies a
natural cover topology or a sheaf theorem.

The common retained-context span is intentionally narrower than Paper XIII's
full alignment contract. A `strict_sof` report and a `diagnostic_analogue`
report may be explicitly aligned by Paper XIII, but they cannot be joined by
two ordinary restriction legs in this prototype. Alignment is not silently
reclassified as restriction.

The controlled result states are:

```text
GLUED_UNIQUE
GLUED_NONUNIQUE
NO_GLOBAL_SECTION
INCOMPATIBLE_OVERLAP
NO_MORPHISM
UNSUPPORTED_PUSHFORWARD
UNRESOLVED
```

`NO_GLOBAL_SECTION` means no declared global candidate realizes compatible
local data. Its interpretation is candidate-relative unless the attached
`DescentBasis` declares an independently evidenced exhaustive candidate
space. `UNRESOLVED` means that no candidate space was supplied. The two states
are not interchangeable.

Each finite search is bound to a `DescentBasis` containing the candidate-space
identifier, completeness status, enumerator, validator, and SHA-256 digest.

## Run

Run from the repository root:

```bash
python experiments/exploratory/comparison_geometry/canonical_minimal_example.py
python experiments/exploratory/comparison_geometry/separating_cover_theorem.py
python experiments/exploratory/comparison_geometry/gluing_hostile_cases.py
python experiments/exploratory/comparison_geometry/cross_fiber_compare.py
python experiments/exploratory/comparison_geometry/bch_composition/bch_signature.py --out experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.json --markdown experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.md
python experiments/exploratory/comparison_geometry/bch_composition/validate_bch_signature.py experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.json
python experiments/exploratory/comparison_geometry/bch_composition/hostile_cases.py
```

## Known Nonclaims

These scripts check finite data structures, candidate-space examples, and one
frozen BCH carrier. They do not establish a Grothendieck topology, a sheaf or
descent theorem for SOF, a general BCH theorem, a cross-frame metric, a
connection, transport, curvature, or any topos-level structural result. The
contextual package remains a `Research Program` item until a natural cover
class, its closure properties, and presheaf-specific descent conditions are
independently defined and validated. A Paper XII or XIII release may consume a
specific control only through an explicit source-addressed reference; that
does not promote either exploratory package as a whole.
