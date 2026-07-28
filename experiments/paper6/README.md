# Paper VI Computational Support

Paper VI v2 separates linearized constraint geometry from pointwise,
normality-gated spectral registrations.

## Current Entry Points

- `validation/tangent_commutator_map.py`: full complex-real commutator Jacobian and the
  rank-11/nullity-7 linearized-kernel certificate.
- `validation/normal_spectral_chart_audit.py`: combined commutativity-normality derivative,
  pointwise projector checks, and typed direct-support registrations on the
  declared certified samples.
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

`results/figure_data.json` is the source-addressed display summary of the
current Jacobian and pointwise-registration audit.
`figures/paper6/render.py` uses it to render the two manuscript figures; it
does not infer a nonlinear chart, projector continuation, or moving field.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
