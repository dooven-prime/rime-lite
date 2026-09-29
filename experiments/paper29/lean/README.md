# Paper XXIX Lean Spine

**Status:** paper-owned partial formalization for a manuscript draft. The
development freezes data-independent implications; it does not replace the
all-$n$ geometric proofs or the finite canonical audit.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| `incidence_ext_of_fused_and_survivors` | Extensional core of the fused-pair/survivor decomposition used in Theorems 4.1 and 6.2 |
| `FusedFiber`, `fusedFiber_ext` | Reading the fused fiber from a boundary incidence map |
| `projectConfig_comp`, `projectConfig_congr` | Same-lineage quotient naturality behind Theorem 4.2; pair and spectators cannot use different witnesses |
| `FrontierClassification`, `frontier_card_of_classification` | The product-count consequence of Theorem 6.2 after the geometric classification equivalence and factor counts are supplied |
| `endpointEquivOfCommonIncidence` | Incidence-level source-block independence in Corollary 6.3 |
| `no_unconditional_raw_to_typed` | Section 7's logical boundary: raw nonemptiness alone cannot create arbitrary typed data |
| `typed_origin_of_explicit_bridge` | An explicit bridge is sufficient to transport a raw witness to typed existence |

## Excluded Scope

The development does not formalize:

- the canonical defect dynamics or defect factorization;
- safe-hit reachability, the missing-image section, or hole slides;
- the all-$n$ fused-pair and survivor classifications themselves;
- the finite graph audit or its retained JSON;
- declared transfer fibers, authorization, typed handoff, projectability,
  recursive return, settlement, or reset bounds.

In particular, `frontier_card_of_classification` is conditional on an exact
classification equivalence. It does not manufacture that equivalence from
finite observations.

## Build

```text
lake build
lake env lean Paper29.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.

