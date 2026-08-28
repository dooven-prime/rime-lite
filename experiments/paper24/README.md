# Paper XXIV Evidence Companion

This directory owns the Lean companion and exact hostile-fixture replay for
Paper XXIV, *Finite Typed Context Descent*. Paper XIII is a motivating
application source, not a formal premise of this evidence package.

The self-contained project pins Lean and Mathlib. Build it from the repository
root with:

```text
cd experiments/paper24/lean
lake env lean FiniteTypedContextDescent.lean
```

## Formalized Surface

The current Lean development proves the free finite-signature core:

- coverage and separatedness;
- free gluing for compatible local signatures;
- the exact finite `AB`/`BC`/`AC` witness.

It does not formalize the manuscript's exact visible-package equalizer,
universal scope-visibility characterization, typed relational admissible
descent, or comparison-reconstruction theorem. Those remain manuscript proofs
unless separately promoted into the Lean closure. The relational acyclicity
characterization is imported from the classical database literature and is
not presented as a Paper XXIV Lean result.

## Exact Hostile Fixtures

The paper-owned Python replay checks the two finite controls whose object types
must remain separate:

```text
python experiments/paper24/validation/validate_descent_fixtures.py
```

It validates:

- `UNSEEN_SCOPE`: matching singleton-coordinate sections glue uniquely, while
  the unseen ternary parity predicate rejects the global section;
- `CYCLIC_CONTEXT_CORE`: the Boolean relations `A=B`, `B=C`, and `A!=C` have
  matching unary projections and empty natural join.

The committed result is
`experiments/paper24/results/descent_hostile_fixtures_v1.json`. This replay does
not prove the general Beeri--Fagin--Maier--Yannakakis acyclicity theorem and
does not generate counterexamples for arbitrary GYO residual cores.

## Release Closure

The paper-owned release gate validates the manuscript, reader PDF,
bibliography, declared Lean/Mathlib closure, Lean compilation gate, and exact
hostile fixtures. Generate the source-addressed receipt with:

```text
python experiments/paper24/validation/validate_release.py --write-receipt
```

Thereafter, validate the committed receipt without rewriting it:

```text
python experiments/paper24/validation/validate_release.py
```

The receipt is
`experiments/paper24/results/paper24_release_receipt_v1.json`. It is a local
closure-verification receipt: it does not independently validate its own
implementation, supply external peer review, or extend Lean coverage beyond
the formalized surface listed above.
