# Paper XXX Lean Spine

**Status:** paper-owned partial formalization for a manuscript draft. The
development checks data-independent logical implications; it does not replace
the manuscript's all-$n$ permutation constructions.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| `exact_quotient_reachability` | Theorem 4.1: existential quotient edges preserve and reflect reachability when every fiber is internally controllable |
| `exact_cycle_gluing_reachability` | Theorem 6.2: point reachability descends exactly to relative-return cycles |
| `cycleStep_iff_eq_or_gluing` | The cycle quotient consists precisely of internal loops and undirected branch-gluing edges |
| `restrictEquivToFiber` | Corollary 6.4: the broad branch-completion equivalence restricts to the fixed-collision fiber |
| `fixed_arrow_forces_gluing` | The fixed collision arrow forces the source and target relative cycles to join |
| `fixed_singleton_cycle_isolated` | The singleton fixed-point exception in Corollary 6.4 |
| `no_unconditional_point_to_coloring_promotion` | Point-orbit classification does not silently promote to coloring-orbit existence |

## Excluded Scope

The development does not formalize:

- construction of the universal returns from a labelled defect;
- the punctured-rotation conjugacy or its gcd-dependent cycle type;
- free branch completion as a concrete equivalence of defect maps;
- the factorial cardinality of the fixed-collision fiber;
- constructive realization of every admissible cycle partition;
- coloring-orbit classification, guarded quotient edges, Safe-Hit, survivor
  incidence, typed transfer/projectability, recursive return, settlement, or
  reset bounds; or
- the finite Python audit and retained JSON.

In particular, `restrictEquivToFiber` consumes an already supplied broad
equivalence. It does not manufacture Theorem 6.1.

## Build

```text
lake build
lake env lean Paper30.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.
