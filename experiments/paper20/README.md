# Paper XX Computational Artifacts

This directory owns the computational companion and release closure for
Paper XX, *All-Depth Carrier Accessibility for Routed Composition*. The routed
factorization, survivor recursion, and cutwise statements are proved in the
manuscript. The exact shared-carrier census is a finite Computational
Certificate; the numerical censuses remain bounded companions.

This is the paper-owned package for the post-protocol carrier/route line. Its
mathematical antecedents are Paper III's all-length disjoint-block obstruction
and Paper VII's carrier-resolved incidence geometry. Its retained results do
not depend on earlier experiment archives or numerical logarithm diagnostics.
The package also does not certify Paper XXI or make that paper a corollary; a
cross-paper bridge would require an explicit Paper XX carrier-hypothesis
registration for the marked finite-field family.

The engine records:

- direct support norms and support-edge count;
- explicit routed products at each enumerated depth;
- carrier support of every sector;
- active-route counts and first active depth within the declared search bound.
- carrier-restricted path pairs, exposing the sandwich
  `composition <= carrier-path <= support-path`.

The computational engine requires a complete orthogonal sectorization. It
stores orthonormal sector bases and multiplies the corresponding rectangular
transport blocks; these are basis representations of the same routed
operators, not Boolean substitutes.

Endpoint pairs and `source->target` keys use source-first order. The stored
direct-support matrix follows the operator convention
`matrix[target][source] = max_g ||Q_target R_g Q_source||_F`.

The current adapters are:

- `z2_double_regular_engine()`: a 4-dimensional regular-plus-regular Z2 model
  with exactly representable 0/1 input matrices, a pure--hybrid--pure graph
  path, and a mathematically exact all-depth carrier obstruction;
- `s3_natural_regular_engine()`: a 9-dimensional natural-plus-regular S3
  control model with an A-only endpoint, an A+B hybrid intermediate, and
  B-only endpoints;
- `rubik_engine()`: the canonical 228-dimensional Rubik realization.

## Retained Bounded Results

| Model | Carrier dimensions | Sectors | Final depth | Support / carrier-path / composition pairs |
|---|---:|---:|---:|---:|
| Z2 regular + regular | 2 + 2 | 3 | 3 | 9 / 7 / 7 |
| S3 natural + regular | 3 + 6 | 6 | 2 | 36 / 28 / 28 |
| Rubik canonical | 64 + 144 + 8 + 12 | 9 | 2 | 53 / 43 / 43 |

Counts are for ordered endpoint pairs and include diagonal pairs when present.
In these bounded runs every strict support/composition difference is explained
by cross-carrier stitching. This is not a general claim that shared-carrier
image--kernel obstructions cannot occur; the exact strict control below gives
eight such obstructions in one carrier.

The strict shared-carrier control is separate from the thresholded adapters.
It uses one carrier, integer permutation/projector matrices, and a complete
depth-two route enumeration:

```text
python experiments/paper20/within_carrier_census.py
python experiments/paper20/validate_within_carrier_census.py
```

The retained result contains 24 supported labelled candidates, 16 active
products, and eight exact within-carrier image--kernel obstructions. No
disjoint endpoint carrier support occurs in this model.

The manuscript's carrier-support decision diagram is presentation-only and is
rebuilt from its renderer without consuming a scientific result record:

```text
python figures/paper20/render.py
```

Run the small control census:

```text
python experiments/paper20/census.py --model z2 --max-depth 3
python experiments/paper20/census.py --model s3 --max-depth 2
```

Validate the retained census artifacts and their declared source digests:

```text
python experiments/paper20/validate_results.py
```

Add `--recompute` to replay every retained artifact from its registered
producer closure. The Rubik depth-2 replay is intentionally slower.

The Rubik adapter is intentionally bounded:

```text
python experiments/paper20/census.py --model rubik --max-depth 1
```

Increasing the depth enumerates actual routes and can grow exponentially.
Every output declares its depth bound, tolerances, and `computational_observation`
status. It does not claim an all-depth classification from finite enumeration.
`minimum_active_depth_within_bound: null` means only that no active route was
observed through `max_depth_enumerated`; the theorem supplies an all-depth
conclusion only when its carrier-disjointness hypotheses apply. In particular,
the 12 Rubik pairs with overlapping carrier support that are null through
depth 2 are not decided by endpoint carrier support alone. Their separate
image--kernel audit closes the bounded depth-two mechanism as factor-zero
obstruction while leaving exact all-depth status unestablished:

```text
python experiments/paper20/image_kernel_census.py
python experiments/paper20/validate_image_kernel.py --recompute
```

The audit exhausts `12 * 9 * 18^2 = 34,992` depth-two route indices. It
classifies 19,008 routes with both projected factors below tolerance, 7,992
with only the prefix below tolerance, and 7,992 with only the suffix below
tolerance; it observes no route with two active factors and a zero product and
no active product. A carrier-restricted replay covers 40,824 route/carrier
indices with the same qualitative result. Index-space coverage is exact, but
factor and product norm classifications are bounded numerical observations.
Exact projected-factor zero, exact absence of nontrivial image--kernel
cancellation, and exact all-depth vanishing are not established. Exact pair
and route records remain in the registered result JSON files.

The retained census is computed in `complex128`, including the Z2 control.
For Z2, exactness of the all-depth conclusion comes from the theorem and its
0/1 construction, not from treating a floating-point validator PASS as an
exact-arithmetic certificate.

## Paper-Owned Release Closure

Lean formalization is optional and is not a release prerequisite for this
elementary block-factorization paper. The release receipt binds the manuscript,
declared environment, implementation, retained results, Rubik source closure,
the exhaustive depth-two image--kernel audit, and hostile regression tests.

Generate the receipt only after replaying all three producers:

```text
python experiments/paper20/validation/validate_release.py \
  --write-receipt --recompute-results
```

Validate frozen bytes without rerunning the slower Rubik census:

```text
python experiments/paper20/validation/validate_release.py
```

Receipt `PASS` establishes the declared local release closure and conformance
only. It is not a machine proof of the manuscript, an independent validator of
its own implementation, or an exact-arithmetic certificate for the
`complex128` census.

The README is a downstream navigation and digest index, not an artifact in the
receipt's ordered closure. This permits it to bind the exact receipt bytes
without creating a receipt-to-README-to-receipt cycle. The release manifest is
upstream of validation and likewise does not contain the receipt digest.

<!-- paper20-release-receipt-index:start -->
## Exact Release Receipt Index

- Receipt: `experiments/paper20/results/carrier_accessibility_v1.release-receipt.json`
- Exact-file SHA-256: `befaee58cd9d8561faa08ff4de870cb23939d52f2373911a377125940055604b`
- Receipt content SHA-256: `ad746f6ff7626b0e6a3a2b74d08f31bf50be952dfed354dd35c7dbabbb54ba7d`
- Artifact closure SHA-256: `eecca10fe115d9a12be2b250021aa3ba9aba6c82c7124ea9db21fdebc57aee1b`
- Validation mode: `LOCAL_CLOSURE_VERIFICATION`
- Independent validation: `false`
- Receipt included in its own closure: `false`
<!-- paper20-release-receipt-index:end -->
