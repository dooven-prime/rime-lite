# Paper XXII Lean Companion

This is a small, boundary-scoped Lean 4 companion for Paper XXII,
“Anchored Farey Classification and Catalan-Fibonacci Envelopes for Rational
Defect Dynamics.” It is a post-release follow-up, outside the Paper XXII v1
evidence manifest and retained validation receipts. It checks two reusable
interfaces:

- `Paper22.Arithmetic.continuant_le_fib`: the positive-run continuant is
  bounded by the Fibonacci number indexed by the total run length;
- `Paper22.TypedBridges.typedBridgeTableCorrect`: the finite integer matrix
  bridge table, determinant-one facts, identity action, and bilinear
  determinant formulas used by the typed endpoint calculation.

The entry point `Paper22.lean` re-exports the all-parameter arithmetic
envelope as `continuant_fibonacci_envelope`. The matrix theorem remains
available under its module-qualified name.

## Scope boundary

This companion does **not** formalize the anchored-Farey geometric
classification, the finite registry generators, the Catalan enumeration, or
the manuscript's full Theorem 4. Those claims retain their paper-owned
Python validators and evidence receipts. The Lean development checks the
data-independent arithmetic and finite algebraic interfaces on which parts of
that argument are based; it is not a replacement for the computational
certificates.

The companion uses Mathlib only for standard natural-number and integer
arithmetic. It contains no generated finite database, `sorry`, or custom
axiom. The dependency revision is recorded in `lake-manifest.json`.

## Reproduction

From this directory, using Lean `4.33.0`:

```text
lake build
lake env lean Paper22.lean
```

The expected successful build covers the root module and both supporting
modules. Build caches are local and are not part of the paper evidence
package.
