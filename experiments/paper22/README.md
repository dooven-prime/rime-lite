# Paper XXII Evidence Package

This directory owns the finite computational evidence for Paper XXII,
"Anchored Farey Classification and Catalan-Fibonacci Envelopes for Rational
Defect Dynamics." Paper XXI supplies motivation only; its v1.0 release closure
is not modified or revalidated here.

## Accepted Release Evidence

| role | path | status |
|---|---|---|
| exact rational producer | `exact_rational_low_deficit.py` | release evidence |
| Farey/Catalan producer | `farey_catalan_structure.py` | release evidence |
| rational certificate | `results/exact_rational_low_deficit_k8_v1.json` | Computational Certificate |
| reduction hostile control | `results/p23_global_registry_hostile_v1.json` | Computational Certificate |
| Farey/Catalan certificate | `results/farey_catalan_fibonacci_k10_v1.json` | Computational Certificate |
| exact rational validator | `validation/validate_exact_rational_low_deficit.py` | local exact replay |
| Farey/Catalan validator | `validation/validate_farey_catalan_structure.py` | local exact replay and release-closure verification |
| exact rational receipt | `results/exact_rational_low_deficit_k8_v1.validation-receipt.json` | recorded local verification |
| integrated release receipt | `results/farey_catalan_fibonacci_k10_v1.validation-receipt.json` | recorded local verification |
| evidence manifest | `evidence-manifest.json` | release artifact index |

The integrated release closure also binds the canonical manuscript, accepted
reader PDF, paper-local bibliography slice, and declared build environment
under `papers/paper22/`.

## Generation Boundary

The two accepted producers use distinct membership-generation paths:

- `exact_rational_low_deficit.py::enumerate_states` constructs transition
  closure;
- `farey_catalan_structure.py::anchored_farey_candidates` constructs anchored
  Farey boundaries independently of the reachable-state list.

They share canonical cusp encoding, integral Mobius action, and determinant
arithmetic, but not the membership predicate. Equality of their complete
registries is checked through deficit ten. The exact rational certificate
separately records 2,682 cumulative states through deficit eight and the
hostile reduction collision at characteristic 23.

The finite records support the manuscript theorems but do not replace their
all-deficit proofs. The determinant threshold is sufficient, not claimed
sharp. Each receipt excludes itself from its closure, and local closure
verification is not independent mathematical validation.

## Read-Only Verification

Run from the repository root:

```text
python experiments/paper22/validation/validate_exact_rational_low_deficit.py
python experiments/paper22/validation/validate_farey_catalan_structure.py
```

Both commands replay the accepted results and compare the reconstructed
receipt with the recorded receipt without modifying the repository.
Regeneration and receipt writing require the explicit producer commands and
`--write-receipt`; they are promotion operations, not verification.

## Exploratory Records

`analyze_open_structure.py`, `low_deficit_census.py`, `stable_deficit.py`, and
their corresponding result files retain bounded exploratory provenance. They
are outside `evidence-manifest.json` and do not define the Paper XXII theorem
or release identity. The auxiliary derivation ledger under `validation/` is
also non-authoritative; theorem statements and numbering belong to the
manuscript.
