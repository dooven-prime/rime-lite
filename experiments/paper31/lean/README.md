# Paper XXXI Lean Spine

**Status:** paper-owned partial formalization for Paper XXXI Version 1.0. The
development checks reusable data-independent implications. It does not
replace the manuscript's arithmetic lane and constructive hole-slide proofs.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| `exact_labelled_path_transport` | Theorem 2.1(5): an exact one-edge partial-system conjugacy transports and reflects one common labelled path |
| `safeHit_iff_quotient` | Generic exact relation-valued orbit reduction under internal fiber controllability |
| `safeHit_of_same_exact_quotient` | Theorem 3.1: equal exact quotient edges and targets imply equal Safe-Hit truth |
| `skew_quotient_edge` | Theorem 5.1 edge formula: deterministic twist followed by the base existential relation |
| `skew_quotient_target` | Theorem 5.1 target-orbit transport |
| `safeHit_sandwich` | Corollary 6.4 implication spine |
| `separate_witnesses_do_not_combine` | The same-witness firewall in the normalized Safe-Hit definition |

## Excluded Scope

The development does not formalize:

- construction of the branch bijection from a concrete labelled defect;
- the concrete identity `phi_r = epsilon_Delta p^r a` or its collision guard;
- punctured-rotation arithmetic, lane decomposition, or affine normalizer
  coordinates;
- lane-order preservation or the constructive decreasing hole slide;
- the all-`n` proof that Safe-Hit is equivalent to lane adjacency;
- the finite Python audit or retained JSON;
- survivor incidence, typed transfer membership, projectability, recursive
  return, settlement, or reset bounds.

The Lean theorems consume the edge, target, internal-controllability, or
invariance hypotheses that the manuscript proves in its concrete setting.
They do not manufacture those hypotheses.

## Build

```text
lake build
lake env lean Paper31.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.
