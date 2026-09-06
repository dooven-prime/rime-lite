# Paper XXV Evidence Package

This directory registers the computational evidence for *Transformation Laws
and Localized Stability of Generator-Resolved Diagnostics*. Manuscript proofs
remain theorem authority.

## Evidence Layers

| Layer | Arithmetic | Zero and threshold semantics | Scope |
|---|---|---|---|
| `EXACT_INTEGER_FRACTION_CERTIFICATE` | Python integers and `fractions.Fraction`; no floating point | literal rational zero; exact rational comparisons | finite sharpness, minimax, equality, transport, and threshold fixtures |
| `BOUNDED_FLOAT64_OBSERVATION` | Python 3.13.0, NumPy 2.1.3, SciPy 1.18.0 for the Rubik runtime, float64/complex128 | fixture-specific thresholds and tolerances frozen in `release-manifest.json` | Rubik simultaneous-transport control and two-state Markov portability example |

The mixed source `transformation_laws_v1.json` is registered componentwise:
`exact_finite_certificate` belongs to the exact layer and
`bounded_numerical_observation` belongs to the bounded layer.

## Scope

| Claim group | Evidence role |
|---|---|
| typed transport and fixed-frame boundary | exact finite transport component plus bounded Rubik simultaneous-transport control |
| localized perturbation and aggregate margin | bounded Rubik orthogonal-specialization observation |
| sharpness, information lattice, additive completion, equality, unresolved interval | exact integer/Fraction certificate |
| two-state probability lift | bounded Markov portability and cross-layer observation |
| Supplementary Technical Note S1 | manuscript proofs plus an exact hostile-matrix replay and bounded proportional-family audit |
| partial Lean formalization | typed transport and scalar-margin declarations under a pinned Lean/Mathlib closure |

Rubik is not registered as a general perturbation distribution or Markov
example. Markov is not registered as support for a general stability theorem.

## Verification

Run the following commands from the repository root. Commands that write
receipts are explicit mutation operations; plain validation remains read-only.

Regenerate and validate the exact certificate:

```text
python experiments/paper25/sharpness_controls.py
python experiments/paper25/validation/validate_sharpness.py --write-receipt
```

Regenerate and validate the bounded-observation registry:

```text
python experiments/paper25/generate_observations.py
python experiments/paper25/register_bounded_observations.py
python experiments/paper25/validation/validate_bounded_observations.py --write-receipt
```

Validate claim alignment and the complete artifact closure:

```text
python experiments/paper25/validation/validate_claim_surface.py
python experiments/paper25/validation/validate_release.py
```

Validate Supplementary Technical Note S1 and its n-state audit:

```text
python experiments/paper25/notes/proportional_markov_semantic_lift/validate_note.py
python experiments/paper25/notes/proportional_markov_semantic_lift/validate_nstate_audit.py
```

Build the partial Lean formalization:

```text
cd experiments/paper25/lean
lake build
lake env lean Formalization.lean
```

Render the explanatory figure:

```text
python figures/paper25/render.py
```

The accepted reader PDF is retained at
`papers/paper25/paper25_arxiv.pdf`; the shared authoring TeX pipeline is not
part of this paper-owned evidence closure.

The receipts certify local replay and hash/status closure. They are not
independent validation or theorem proofs.

The package is paper-owned and self-contained. The main theorem spine registers
only the two-state Markov portability example. Supplementary Technical Note S1
adds one proportional-row n-state preservation contract and an explicit
absolute-gap negative boundary without enlarging the main theorem numbering.
