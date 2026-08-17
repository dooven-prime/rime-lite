# Paper VI Computational Support

Paper VI v2.1 is a certificate and admission-boundary revision. It separates
linearized constraint geometry from pointwise, normality-gated spectral
registrations and rejects inadmissible samples before projector construction.

## Current Entry Points

- `validation/tangent_commutator_map.py`: full complex-real commutator Jacobian and the
  rank-11/nullity-7 linearized-kernel certificate.
- `validation/normal_spectral_chart_audit.py`: combined
  commutativity-normality derivative, fail-closed admission, pointwise
  projector checks, and typed direct-support registrations. Run with
  `--write-results` to refresh the versioned result and figure-data projection;
  run without that flag to recompute and validate both committed artifacts.
- `validation/generator_moduli_space.py`: contextual ambient-moduli probes. It is not a
  spectral-chart or moving-wall certificate.
- `phase_utils.py`: shared implementation helper, not an independent claim
  source.

## Results And Archive

New generated JSON, observation, hash, and run-summary artifacts belong under
`results/`. Long deterministic runs should use
`experiments.observation`; cached observations remain review aids rather
than theorem sources.

First-version fragmentation and untyped wall scripts live under `archive/`.
They are historical provenance and must not be used to admit nonnormal samples
to spectral registration or to infer moving typed accessibility fields.

`results/normality_gated_admission_v2_1.json` is the full versioned result
record. It binds the validator implementation, numerical policies, singular
spectra, admission residuals, projector checks, typed support counts, and the
archive correction ledger.

Its admission ledger contains four `ADMITTED` records and one `REJECTED`
single-QT negative control. Rejected records carry no projector, sector, or
typed-support values; missing post-admission fields are not numerical zero.

`results/figure_data.json` is the source-addressed display projection of that
result record.
`figures/paper6/render.py` uses it to render the two manuscript figures; it
does not infer a nonlinear chart, projector continuation, or moving field.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
