# Lean Proof Layer

**Status:** compiled under the pinned release closure.

The library target imports:

- `Formalization/PairHitting.lean`, which formalizes the full pair-hitting
  identity over `WithTop Nat`;
- `Formalization/ParameterFreeArithmetic.lean`, which formalizes only the
  conditional arithmetic implication used in manuscript Theorem 5.4;
- `Formalization/AxiomAudit.lean`, which reports the axioms used by those two
  named targets.

The pinned environment is Lean 4.33.0 with Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`. The successful build, placeholder
scan, axiom audit, and source hashes are recorded in
`formalization_receipt.json`.

Replay with:

```bash
lake build
rg -n "\\b(sorry|admit)\\b|^\\s*axiom\\b" -g "*.lean" .
lake env lean Formalization/AxiomAudit.lean
```

The receipt proves elaboration under the pinned closure. It is not an
independent proof checker for the validator, and it does not extend Lean
coverage to the rest of the manuscript.
