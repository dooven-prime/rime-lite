# Paper XXXV Lean Order-Phase Spine

**Status:** paper-owned partial formalization.

This project machine-checks the data-independent logical and finite-product
consequences used by Paper XXXV. It does not copy the 120-branch audit or
formalize the concrete guarded order graph.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| `reachable_symm_iff` | the globally enabled branch equivalence transports reachability backward as well as forward |
| `PhaseModel.mem_phaseFiber_iff` | one concrete hole is a phase witness exactly when its terminal cyclic order is reachable |
| `PhaseModel.phaseFiber_eq_holes_of_reachableOrder` | Theorem B: every hole is a phase witness for a reachable terminal order |
| `PhaseModel.phaseFiber_eq_empty_of_unreachableOrder` | Theorem B: an unreachable terminal order has no phase witness |
| `PhaseModel.attainable_iff_of_holes_nonempty` | the exact terminal criterion once a missing coordinate is supplied |
| `LeftCosetSpace` | Theorem A's `K_a^{ord}/C_5` is a left-coset space without a normality assumption |
| `leftCosetClass_eq_iff` | equality in that space is left-coset equivalence |
| `survivorFrontier_card_of_available_card` | Theorem C's `m_a(F) * choose (n - 2) 3` count |
| `FrontierModel.frontier_eq_of_signature_eq` | Corollary 5.3: equal signatures determine equal frontiers |

## Assumption Boundary

`PhaseModel` consumes the manuscript's order-fiber saturation and the fact
that every well-typed hole pullback has the terminal cyclic order. Lean checks
the all-or-none phase conclusion and its same-witness quantifiers; it does not
prove those concrete guarded-geometry inputs.

`LeftCosetSpace` freezes the notation boundary only. The development does
not prove the eight-pattern double-coset reconstruction or the concrete
generated-subgroup reachability theorem.

The survivor module represents the proved frontier product by
`allowedOrders × coordinateTriples`. It checks membership, cardinality, and
the forward complete-invariant implication. It makes no minimality statement
and proves no converse.

The development also does not formalize the finite JSON control, multi-lane
mobility, shortest witnesses, typed transfer membership, projectability,
recursive return, settlement, or reset bounds.

## Build

```text
lake build
lake env lean Paper35.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.
