# Paper XXXIV Lean Incidence Spine

**Status:** paper-owned partial formalization.

This project machine-checks the data-independent incidence, counting, and
non-descent consequences used by Paper XXXIV. It deliberately does not copy
the finite survivor database or formalize the guarded all-$n$ geometry.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| `markedCollapse_eq_root_iff` | the normalized collapse has exactly the two marked preimages of the collision root |
| `TerminalWitness.incidence_eq_root_iff` | the complete terminal witness identifies the fused source pair |
| `TerminalWitness.incidence_injOn_survivors` | the same incidence is injective on the three surviving lineages |
| `TerminalWitness.root_fiber_card` | the fused fiber has cardinality two |
| `exists_missing_coordinate` | the finite-cardinality core of the missing-hole converse |
| `DihedralSpectrum.reflection_card` | one negative orientation copy doubles the positive survivor count |
| `no_descent_of_equal_view_ne_output` | equal coarse data with unequal outputs forbids functional descent |
| `no_pair_level_survivor_descent` | the rotation/reflection survivor view does not descend through pair data |

## Assumption Boundary

`TerminalWitness` consumes one injective pre-collapse placement whose two
distinguished lineages occupy the marked-collapse coordinates. The Lean
development proves the fiber and survivor consequences of that supplied
witness. It does not construct guarded paths or infer terminal membership.

`DihedralSpectrum` consumes the disjoint positive and negative survivor
families and their equal cardinality. Those are the geometric conclusions of
the manuscript classification. Lean checks their counting and non-descent
consequences; it does not prove the all-$n$ reachability classification.

The development also does not formalize the branch conjugacy back to an
original defect, finite JSON controls, arbitrary-branch or multi-lane
survivor theory, typed transfer membership, projectability, recursive return,
settlement, or reset bounds.

## Build

```text
lake build
lake env lean Paper34.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.
