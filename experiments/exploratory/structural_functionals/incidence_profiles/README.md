# Routed-Incidence Profiles Under Generator Restriction and Frame Change

**Research status:** exploratory fixed-frame structural-functional package
with local theorem candidates, exact finite certificates, and bounded
Computational Observations.

**Execution status:** runnable with the repository Python environment using
the commands below.

**Paper evidence:** none by package placement. Paper VII v2.1 separately
registers only the fixed canonical-frame family index, fixed-frame summary,
canonical carrier-zero certificate, and axis-rotation control through
`experiments/paper7/validation/register_fixed_frame_profiles.py`. Every other
artifact remains exploratory even though the package is public.

This package studies one routed composition

```text
A = Q_i X_g Q_k,  B = Q_k X_h Q_j,  AB = Q_i X_g Q_k X_h Q_j
```

for restricted inverse-closed Rubik generator families. It separates the
fixed-frame and endogenous-frame questions that earlier exploratory scripts
mixed together.

## Typed Object

The registered operator data are:

```text
F_op = (V, {Q_i}, Y),
Y = {X_g = (rho(g)-rho(g)^*)/2}.
```

The primary object is the finite routed-incidence profile of supported factor
pairs under this declared anti-Hermitian operator alphabet. It belongs to the
Paper VIII operator/routed branch and consumes the Paper VII one-route
image--kernel and rank-protection boundary. No Lie/Hall carrier is registered.

Two protocols are kept distinct:

1. `fixed_full`: retain the canonical 18-generator joint QT/HT frame and
   restrict only the operative generator family;
2. `endogenous`: recompute the spectral frame from the restricted family and
   serialize projector-overlap alignment back to the canonical frame.

An endogenous frame is not called a refinement unless the computed
containment relation proves refinement. Most reported frame pairs overlap
without either refining the other.

The finite family index quotients the declared axis-balanced family space by
the 24 orientation-preserving cube rotations. It is not the Paper X SOF
Registry.

## Recorded Quantities

For every supported routed factor pair, the census records the five Paper VII
rank-protection classes and reports both

```text
unprotected_zero / all_supported_routes
unprotected_zero / all_unprotected_routes.
```

These denominators answer different questions and are never merged.

For endogenous frames, the alignment entries are

```text
M_ij = tr(P_full_i P_family_j)
     = ||V_full_i^* V_family_j||_F^2.
```

Row and column mass residuals check numerically that the overlap table covers
both decompositions. Sector indices have no cross-frame identity without this
alignment object. Overlap maxima and containment minima are serialized as
tie-aware sector-index sets under the declared alignment tolerance; no
scientific claim depends on an arbitrary single-index `argmax` or `argmin`.

## Carrier Admission

The ambient Rubik realization has exact physical carriers `cp`, `ep`, `co`,
and `eo`. The numerical census distinguishes:

- `physical_carrier_forced`: no registered carrier supports both factor legs;
- `within_carrier_image_kernel`: a carrier supports both legs, but every
  carrier-local product is numerically zero;
- `numerical_cancellation_or_threshold_conflict`: a total product is below its
  threshold while a carrier-local product exceeds its local threshold.

The carrier-forced theorem requires both sector projectors and operative
matrices to preserve the registered carrier decomposition. Sector-projector
reduction alone is insufficient. Exact promotion additionally requires exact
carrier masks. The canonical certificate checks these conditions over
`Z[zeta_3]`, checks all nine joint spectral projectors, and records a
conservative preoperation `int64` bound for every identity construction,
addition, subtraction, integer scale, adjoint, matrix multiplication, and
trace. Trace accumulation uses Python integers. Thus `all_operations_safe`
covers the full fixed-width arithmetic path rather than matrix multiplication
alone.

## Commands

Run from the package directory:

```powershell
cd experiments/exploratory/structural_functionals/incidence_profiles
```

Focused tests and exact certificates:

```powershell
python test_incidence_profiles.py
python make_exact_certificates.py
python exact_n8_spectrum.py
python exact_canonical_carriers.py
```

Generate the finite family index and both complete censuses:

```powershell
python enumerate_families.py
python enumerate_families.py --run --protocol fixed_full
python enumerate_families.py --run --protocol endogenous
```

Build summaries, the finite conjecture audit, and the conditional route
certificate:

```powershell
python summarize_census.py results/axis_balanced_fixed `
  --output results/axis_balanced_fixed_summary.json
python summarize_census.py results/axis_balanced_endogenous `
  --output results/axis_balanced_endogenous_summary.json
python search_conjectures.py
python run_census.py --families axes02_qt --protocols fixed_full
python exact_route_certificate.py results/named/axes02_qt__fixed_full.json `
  --output results/exact_certificates/axes02_qt_fixed_full_routes.json
python validate_results.py
```

The one-time migration comparison against a retained local historical snapshot
is optional and is not part of normal package execution:

```powershell
python compare_historical.py <historical-results-directory>
```

Its output stores historical file digests and comparison results, not the
external absolute path. Normal validation verifies the retained certificate's
structure and current-artifact closure; it cannot independently rerun the
historical comparison without the separately retained historical bytes. The
migration certificate has no Paper VII promotion authority.

Use `--start` and `--stop` to shard the complete family census. Existing
profile files are left untouched so interrupted runs can resume. After an
implementation or backend change, use `--overwrite` explicitly to regenerate
the affected profiles and their source-artifact closure.

## Promotion Boundary

`THEOREMS.md` records reusable local propositions and their assumptions. Exact
finite JSON outputs use the reader-facing status `Computational Certificate`;
the separate `certificate_kind` field says whether the check is exact finite,
exact combinatorial, or conditional exact. Numerical profiles use
`Computational Observation`.

The observed fixed-frame `2/9` rate remains a finite numerical census. The
canonical certificate proves every registered carrier-forced zero in its
numerator, but does not prove exact nonvanishing of every remaining supported
route.

## Known Nonclaims

- The package as a whole does not amend or supersede Paper VII; Paper VII v2.1
  owns only the four explicitly registered fixed-frame source artifacts.
- A support path is not promoted to a routed product.
- A routed product is not promoted to a full ordered word or route sum.
- No associative product here is a commutator or Lie/Hall depth certificate.
- Projector overlap is not a complete invariant of frame pairs.
- An endogenous frame is not automatically a refinement of the canonical
  frame.
- Free matrix-pair codimension does not determine represented pullback
  incidence geometry.
- The finite `2/9` pattern is not a universal generator-family law.
- The package is not a Paper X Registry entry, Paper XII report, Paper XIII
  audit, or Paper XIV interpretation object.
