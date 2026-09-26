# Paper XXVIII Lean Spine

This supplementary Lean 4 development checks the data-independent logic and
algebra used by Paper XXVIII. It does not import finite JSON records or prove
the computational certificates.

## Correspondence

| Lean declaration | Manuscript surface | Exact scope |
|---|---|---|
| `credit_of_surplus` | Proposition 4.1, (4.2) | Derives budget credit from the stipulated endpoint surplus equation. |
| `credit_of_composite` | Proposition 4.1, (4.3) | Proves credit composition for an already existing, compatible composite with additive length and surplus. |
| `existential_return_compose` | Theorem 5.1, (5.1) to (5.2) | Composes two supplied existential return relations through the *same* certified rank-four target. |
| `separate_exists_not_same_witness` | Same-witness firewall | Concrete countermodel to fusing two unrelated existential witnesses. |
| `alignment_return_transport`, `existential_alignment_return_transport` | Theorem 6.2 transport step | Preserves LocalReturn when an adapter path has a canonical image with equal theorem-facing observables. |
| `alignment_not_relation_equality_control` | Theorem 6.2 boundary | An injective image can be nonsurjective; alignment is not relation equality. |

`TypedLifts` carries source-addressed menu and lift relations, source typing,
and a typed handoff relation. This is an abstract interface, not an
implementation of F1--F4. In particular, the type signature has no lower
success parameter, but Lean does not prove that a concrete constructor is
future-free. It also does not derive exact replay, ancestry, normalization,
or handoff soundness. `ReturnChain` keeps the upper lift and its handoff on
the same word and feeds that exact middle target to the lower lift.

The alignment `Observable` parameter stands for the complete theorem-facing
read set, including provenance when the consumer needs it. Its preservation
field is a premise; the 26,995 finite image checks are not repeated in Lean.

## Build

From this directory:

```text
lake build
lake env lean Paper28.lean
```

The project pins Lean 4.33.0 and uses only Lean's standard library. No
Mathlib package, generated finite database, `sorry`, or custom axiom is used.

Successful elaboration validates these conditional implications only. The
five finite return surfaces, 11,252 receipts, 26,995 macro lifts, coverage,
Projectable-Origin Supply, and any all-\(n\) statement remain outside the
Lean claim surface. The finite results retain their separate exact
computational certificates and receipts.

## Release Closure

The supplementary formalization has its own source-addressed closure and does
not enter the historical finite-mirror manifest. From the repository root,
validate the retained receipt with:

```text
python experiments/paper28/validation/validate_lean_formalization.py --replay
```

The retained receipt is
`results/paper28_lean_formalization_v1.receipt.json`. It binds the manifest,
README, toolchain, Lake files, Lean sources, and validator, while excluding
the receipt itself. This is local closure verification, not independent
formal validation or a replay of the finite JSON certificates.
