# MTS-1 Nontrivial Registered Contrast

## Status

Status: `NONTRIVIAL_CONTRAST_POLICY_FROZEN_AWAITING_PRODUCER_PREFLIGHT`.

Execution authority: `NONE`.

This package freezes the last scientific policy input before any 153-source
mechanism replay. It consumes only synthetic fixtures during validation. It
does not read raw-drive or clipping-fate data from a registered scientific
source.

## Exact predicate family

The primary family contains seven named conjunctions:

1. `CLIPPING_CREATES_COARSE_RESIDUAL`;
2. `CLIPPING_ELIMINATES_COARSE_RAW_RESIDUAL`;
3. `CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL`;
4. `RAW_RESIDUAL_PERSISTS_UNCHANGED`;
5. `RAW_DRIVE_DIFFERENCE_COARSE_ANNIHILATED`;
6. `MICROSCOPIC_DIFFERENCE_RAW_DRIVE_IDENTICAL`;
7. `FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION`.

Their exact machine definitions are frozen in
[`nontrivial_contrast_v1.py`](nontrivial_contrast_v1.py). None reads the pair
role, known successor label, defining-transition flag, or residual-quadrant
label. `REGISTERED_SAFE_FORGETTING_GEOMETRY` remains descriptive only and
cannot award the highest outcome.

## Finite-census comparison

Records are not pooled across transition or cohort. A comparison cell is one
transition and one transient/persistent cohort pair sharing the same initial
anatomical stratum. Each record receives the ordered seven-bit joint predicate
signature. Cell distributions are compared as exact normalized histograms by
integer cross multiplication; there is no floating tolerance, prevalence
cutoff, majority rule, hypothesis test, or significance threshold.

The census must contain exactly all canonical unordered source pairs rebuilt
from every frozen cohort membership on all three transitions. Matching only a
cohort pair count is insufficient.

`EXACT_TRANSITION_LAYER_LOCALIZATION` requires one named primary conjunction,
one transition, and one fixed direction such that the conjunction is true for
every pair on one role and no pair on the other role in every shared-stratum
cohort comparison cell at that transition.

If no such universal separator exists but at least one exact normalized joint
signature histogram differs, the outcome is
`PARTIAL_REGISTERED_FEATURE_CONTRAST`. If all registered comparison-cell
histograms agree, the outcome is
`NO_CONTRAST_IN_DECLARED_FEATURE_FAMILIES`. Incomplete census or validation is
`UNRESOLVED` at the execution layer and may not be converted into any of the
three completed outcomes.

## Append-only gate resolution

The earlier record-schema registration remains unchanged and correctly records
that three payload codecs were not implemented at its freeze time. The later
codec registration discharges those gates. This policy registration consumes
both artifacts append-only and discharges only
`NONTRIVIAL_CONTRAST_FINITE_CLASSIFICATION`. A future execution-authority
manifest must compute effective gate state from this ordered history rather
than rewriting an earlier artifact.

Three historical dependency paths were later retired when the unpublished
Paper XVII package was folded back into the exploratory dynamic-compression
line. The current registration resolves those paths only because the present
codec, sector-label, and transient-audit bytes exactly match the byte lengths
and SHA-256 digests frozen by the historical registrations. This is an
append-only path resolution, not a semantic rebinding.
