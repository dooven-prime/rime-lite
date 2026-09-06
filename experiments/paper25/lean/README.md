# Paper XXV Typed Transport and Scalar-Margin Formalization

**Status:** paper-owned partial formalization admitted to the Paper XXV draft
release manifest. Its receipt records local closure verification, not
independent validation of the manuscript.

This paper-owned partial formalization covers the typed transport and scalar
margin core of Paper XXV.

## Formalized Surface

- exact three-factor block covariance under `uStar * u = 1`;
- finite-sum covariance;
- an explicit conjugation-invariant metric interface and threshold/activity
  preservation;
- stable-active and stable-inactive margin implications;
- the unresolved interval equivalence and its inactive/active scalar
  witnesses.

The manuscript correspondence is deliberately narrower than whole-result
coverage:

| Lean declarations | Manuscript surface |
|---|---|
| `transported_block_eq`, `transported_block_measure_eq`, `transported_block_active_iff` | algebraic and abstract-diagnostic core of Theorem 2.1 |
| `finite_aggregate_conjugate` | finite-sum covariance only; not the full Boolean aggregation statement of Corollary 2.2 |
| `stable_active_of_error`, `stable_inactive_of_error`, `margin_trichotomy` | scalar order core of Corollary 4.1 |
| `unresolved_iff_interval`, `unresolved_has_inactive_and_active` | scalar interval part of Theorem 4.2; not its operator-realization clause |

## Formalization Boundary

The metric interface is intentionally abstract: it assumes that the declared
scalar diagnostic is invariant under the transport. It does not formalize a
concrete Frobenius norm or derive metric invariance from unitarity. The
unresolved-interval witnesses are scalar values, not operator or matrix
realizations. The carrier-localized perturbation theorem, minimax sharpness,
oblique-carrier extension, Rubik and Markov realizations, numerical artifacts,
and the Paper XXV companion note remain outside this Lean surface.

Successful elaboration establishes only that these named Lean declarations
type-check under the pinned environment. It does not independently validate
the manuscript, numerical evidence, or release closure.

## Build

Build from this directory with:

```text
lake build
lake env lean Formalization.lean
```

The source uses Lean 4.33.0 and the pinned Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d`.
