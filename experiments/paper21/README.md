# Uniform Finite-Field Route Profiles

**Pole-Preimage Classification and Characteristic-Aware Stability in Marked
Modular Carriers**

Paper XXI is an independently scoped theorem paper on finite marked carriers
and routed composition.

It shares a carrier/route research line with Paper XX, but does not depend on
its theorems. The finite-field classifications use explicit
projective pole/preimage arithmetic. No Paper XX carrier decomposition or
carrier-preservation certificate is registered in this package.

The source directory also supplied selected finite-action bundles to Paper
VIII v2.1. Paper XXI consumes different route-profile producers and results,
then promotes them under its own claim map and receipts. Directory provenance
does not make the Paper VIII conformance certificate part of this closure.

## Ownership

This package owns the finite marked modular carrier, labelled routed products,
depth-two and depth-three zero-route classifications, the arbitrary-depth
prefix-pole semantics, the fixed-field survivor automaton and rationality
theorem, the generic profile `Z_d^gen`, prefix determinant spectra `D_d`,
fixed-depth large-field stabilization, the Boolean candidate count, and the
fixed-depth route-profile interface.

The source experiments remain under
`experiments/exploratory/carrier_realizations/fuchsian_schreier/`. Their
existing result files remain exploratory source artifacts. Promotion must
create paper-owned results and fresh replay receipts rather than rewriting
those files in place.

## Claim Levels

- **Exact theorem:** depth-two uniform classification for finite fields with
  at least three elements.
- **Exact theorem:** depth-three characteristic/cardinality classification.
- **Exact theorem:** `B_d = 3^d F_(d+3)` for supported candidates at every
  positive depth.
- **Exact theorem:** arbitrary-depth route survivor sets are classified by
  forced and forbidden prefix poles.
- **Exact theorem:** the generic depth-`d` profile is determined by the
  integral prefix-pole equality relation and the pole-class count identity.
- **Exact theorem:** for each fixed finite field, the survivor language has a
  finite reachable-subset automaton and rational transfer series.
- **Exact theorem:** at fixed depth `d`, the labelled zero-route set stabilizes
  for `|F| > d` outside a finite exceptional characteristic set `E_d`.
- **Exact theorem:** `D_d` and `E_d` are monotone under depth extension.
- **Computational certificate:** sampled higher-depth route profiles and
  finite word-image layers.

The phrase *zero route* is used throughout. It is not an operator-kernel or
spectral *zero mode* statement.

## Finite-Field Branch Boundary

| Surface | Current status |
|---|---|
| `d = 2` semantic zero-route classification | closed and formalized |
| `d = 3` characteristic-aware zero-route classification | closed and formalized |
| `B_d = 3^d F_(d+3)` supported-candidate count | closed and formalized for every positive depth |
| arbitrary-depth prefix-pole classification | closed in manuscript; exact paper-owned replay |
| generic profile `Z_d^gen` and determinant spectrum `D_d` | defined for every depth; replay through depth ten |
| fixed-field automaton and rationality | closed in manuscript; exact paper-owned construction |
| fixed-depth stabilization outside `E_d` | closed for `|F| > d`; `E_d` replay through depth ten |
| monotonicity `D_d subseteq D_(d+1)` and `E_d subseteq E_(d+1)` | closed in manuscript |
| Lean closure of the arbitrary-depth prefix-pole package | open |
| all-depth scalar zero-count formula or growth law | open |

The arbitrary-depth semantic classification reduces the generic scalar count
to prefix-pole equivalence classes, but does not yet give a closed form. The
fixed-field automata may grow with the field and the reduced rational functions
may differ. Recurrences for `D_d`, a universal state bound, one rational
function for all fields, and a stable depth-asymptotic growth law remain open.

## Verification Sources

- `uniform_modular_zero_route_classification.py`
- `depth_three_zero_route_classification.py`
- `uniform_finite_field_route_profile.py`
- `results/uniform_modular_zero_route_classification_v1.json`
- `results/depth_three_zero_route_classification_v1.json`
- `results/uniform_finite_field_route_profile_v1.json`

Paper-owned validation and formalization:

- `validation/promote_route_profiles.py`
- `validation/validate_route_profiles.py`
- `arbitrary_depth_semantic.py`
- `validation/validate_arbitrary_depth_semantic.py`
- `results/arbitrary_depth_semantic_v1.json`
- `claim-surface-map.json`
- `results/arbitrary_depth_semantic_v1.validation-receipt.json`
- `results/route_profile_promotion_v1.json`
- `results/route_profile_promotion_v1.validation-receipt.json`
- `lean/FiniteFieldRouteProfiles.lean`
- `lean/README.md`

The self-contained Lake project under `lean/` vendors the two imported theorem
modules and pins Lean and Mathlib. The Lean entry point covers the complete
depth-two semantic theorem, the
arbitrary-depth Boolean candidate count, all eight depth-three shape criteria,
the all-finite witness theorem for fields of cardinality at least four, the
`F2`/`F3` finite exceptional enumerations, and the complete characteristic-
aware depth-three histogram/count theorem. Sampled higher-depth profiles
remain computational certificates only. The arbitrary-depth prefix-pole,
generic profile/determinant spectrum, automaton, rationality, and stabilization
theorems remain manuscript theorems with exact paper-owned replay, not
part of the Lean proof surface.

Run the portable formalization check from the repository root:

```text
python experiments/paper21/validation/validate_lean_formalization.py \
  --receipt build/verification/paper21-lean-receipt.json
```

The committed receipt is release evidence. Routine verification writes to
scratch and compares against it; only an explicit promotion step may replace
the tracked receipt.

Receipt scopes are distinct. The promotion receipt binds the promoted route
profile certificate and its declared source replay. The arbitrary-depth
receipt binds the exact semantic replay. The Lean compilation receipt binds
only the formalized theorem surface listed in the manuscript status table; it
does not certify Theorem 5.1, Corollaries 5.2--5.3 and 5.6, or Theorem 5.5.
Proposition 5.4 is part of the formalized surface. The release receipt binds
these records to the manuscript, PDF, figure, validators, formal sources, and
hostile regression without including itself.

The methodology surface can be checked independently with:

```text
python tools/research/validate_claim_surface.py \
  experiments/paper21/claim-surface-map.json
```

This check aligns declared claim IDs, manuscript markers, promotion status,
and Lean declarations. It does not infer that a matching declaration proves a
manuscript claim; the explicit map is the reviewed assertion being checked.

## Release Closure

Run the nonmutating release check from the repository root:

```text
python experiments/paper21/validation/validate_release.py
```

Receipt generation is a promotion operation and requires explicit replay:

```text
python experiments/paper21/validation/validate_release.py \
  --write-receipt --recompute-components --recompute-lean
```

The release receipt records local closure verification. It is not independent
validation, does not prove the manuscript theorems, and does not extend the
declared Lean proof surface.

<!-- paper21-release-receipt-index:start -->
## Exact Release Receipt Index

- Receipt: `experiments/paper21/results/route_profiles_v1.release-receipt.json`
- Exact-file SHA-256: `9b4362fa53266de63e51280290a6c992d466c150f78e102975ac4ea6c90c0d49`
- Receipt content SHA-256: `fa9186ee943ba601d723e59a0ef319101cac839b38c9aac02927fb5755942ca4`
- Artifact closure SHA-256: `55fc30e7b12aa34a9fe3078320c3c40617489ca71b86e28473b3ce2d6e5ecbc8`
- Validation mode: `LOCAL_CLOSURE_VERIFICATION`
- Independent validation: `false`
- Receipt included in its own closure: `false`
<!-- paper21-release-receipt-index:end -->
