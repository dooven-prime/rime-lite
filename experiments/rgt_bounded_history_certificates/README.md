# R/G/T bounded history certificates

Supporting library of the Paper XL C1/RGT companion, not a separate paper
and not part of the frozen Paper XL release closure. This package quantifies the actual-history rejection statement in
Paper XL, Theorem 4.1, using finite complete auxiliary states. It does not
change Paper XL or claim a new general finite-automaton theorem.

The first milestone is Lean-checked:

- every reachable complete state has a history of length at most `N - 1`,
  where a list of length `N` covers all reachable complete states;
- each failed R, G, or T clause has two such bounded prehistories;
- a T certificate appends the same commonly enabled raw letter, giving
  successor histories of length at most `N`;
- a recoverable complete-log encoding gives the explicit bound
  `B(n,m) = n^m * sum(j=0..m-1, 3^(m*j))`.
- a separate observation-factorization interface transports any
  complete-log/endpoint-preserving compression bound `B(n)` to R/G
  counterexample histories of length `B(n)` and T successor histories of
  length `B(n)+1`.

The last statement is conditional on an explicit semantic encoding and recovery
interface. The code-list count and interface implication are proved here. A
separate Paper XL Lean companion now supplies an instance for its declared
circular placement-plus-complete-log model; this is not a claim that the
frozen Python raw-log implementation or archived bytes have been formalized.
No lossy summary or minimal quotient count is substituted for `N`.

## Files

| File | Role |
|------|------|
| [RGT_BOUNDED_HISTORY_CERTIFICATES.md](RGT_BOUNDED_HISTORY_CERTIFICATES.md) | precise hypotheses, proofs, model/runtime boundary, and remaining correspondence question |
| [lean/README.md](lean/README.md) | toolchain, declarations, verification commands, and axiom boundary |
| [FiniteHistory.lean](lean/RGTBoundedHistory/FiniteHistory.lean) | endpoint-preserving loop erasure and finite-cover bounds |
| [Certificates.lean](lean/RGTBoundedHistory/Certificates.lean) | R/G/T rejection equivalences and the one-letter T extension |
| [LogEncoding.lean](lean/RGTBoundedHistory/LogEncoding.lean) | complete-log code count, recoverability interface, and counted certificate bounds |
| [ObservationCompression.lean](lean/RGTBoundedHistory/ObservationCompression.lean) | observation-preserving bounded replacement and conditional R/G/T certificate transport |
| [ObservationCompressionChecks.lean](lean/ObservationCompressionChecks.lean) | concrete check of the conditional read-certificate transport |
| [Checks.lean](lean/Checks.lean) | kernel-checked boundary examples; not an independent runtime implementation |
| [AxiomAudit.lean](lean/AxiomAudit.lean) | explicit public-theorem dependency queries |

## Validation

From this repository's root, with the pinned Lean toolchain available:

```bash
cd experiments/rgt_bounded_history_certificates/lean
lake build
lake env lean Checks.lean
lake env lean AxiomAudit.lean
```

Lean 4.33.0 and its bundled `Std` are the only dependencies. No Mathlib or
network download is required once that toolchain is installed. Build output
stays in the ignored `.lake/` directory. All three commands passed locally on
2026-11-04. The queried dependencies were only `propext`, `Classical.choice`,
and `Quot.sound` (some declarations use a subset or none).

## Nonclaims and next interface

These are bounds on **two past histories**, not on a future distinguishing
suffix. In particular, a candidate's T failure need not distinguish the
consumer's report/guard behavior. This package neither extends the specialized
`6n - 10` probe bound to general defects nor proves POS, typed authorization,
same-witness projectability, or a quadratic history bound.

The declared circular Lean model's `CompleteLogEncoding`, exact consumer
factorization through `(ordered event list, terminal atom-site map)`, and
finite-bound R/G/T wrappers are in [the Paper XL Lean companion](../paper40/lean/README.md).
For the C1-compatible fragment (`n ≥ 3`, `2 ≤ m ≤ n`),
`PaperXL.C1QuadraticRGT` now instantiates the quadratic complete-state
compressor and transports its bound to R/G/T certificates, including lossy
candidate maps defined on that complete state. Correspondence to independently
defined lossy runtime state models and frozen Python bytes remains open.
Proper-arc Lean and Fusion-log M2--M4 are not dependencies of the present
package.
