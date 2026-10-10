# Mechanism of Transient Separation

MTS-1 studies why the six unsafe coarse fibers identified by the held Paper
XVII draft separate after the registered initial transient, while five
disjoint non-singleton cohorts remain successor-compatible. It is a new
post-result mechanism registration. It does not modify the frozen Paper XVII
evidence surface or inherit its execution authority.

Current status: `POST_EXECUTION_FROZEN`.

Execution authority: `NONE_COMPLETED`.

The completed exact census contains 153 sources, 459 source-transition cache
records, and 6,975 pair-transition records. The exhaustive validator assigned
the frozen outcome `EXACT_TRANSITION_LAYER_LOCALIZATION`. At transitions
`2->3` and `3->4`, both
`CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL` and
`FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION` hold for every registered
transient-obstruction pair and for no registered persistent-safe pair in every
shared-stratum comparison cell. This is an exact finite-census statement, not
a prevalence estimate, hypothesis test, or causal attribution.

The frozen question is:

> Which exact transition-layer differences distinguish the 51 sources in the
> transient-obstruction fibers from the five persistent-safe cohorts, after
> controlling explicitly for transition time and initial anatomical stratum?

The registered model contains no world or external adjudicator. It uses a
fixed signed carrier, deterministic zero-input dynamics, and no stochastic
noise. MTS-1 may therefore support only an internal statement:

> The registered internal dynamics transforms microscopic distinctions into
> different coarse equivalence fates.

It may not describe this transformation as correction by the world.

The primary analysis unit is a source pair inside one registered fiber or
cohort, not an individual neuron treated as an independent biological sample.
The registered comparison follows the exact model pipeline

```text
microscopic state difference
  -> raw signed drive difference
  -> clipping-fate difference
  -> coarse successor difference
```

The equality `r_clip = 5 * delta_z_next` on an observation fiber is a required
identity replay, not a mechanism result. The highest registered outcome cannot
be awarded from that identity or from the already known successor label alone.
Likewise, the four exact `(r_raw, r_clip)` zero/nonzero quadrants are phenotype
labels, not four mechanism labels. Any interpretation must use an explicitly
registered conjunction involving `r_corr` or nontrivial state/raw-drive
geometry.

The Paper XVII sidecar stores exact coarse observations, not microscopic
states. The completed MTS-1 producer therefore replayed
each of the 153 selected sources once, validates every replayed observation
and state digest against the Paper XVII records, and caches 459
source-transition records. The 6,975 pair records are derived from that cache;
the pair stage has no operator interface.

The exhaustive result validator does not accept the producer's successor
residual as its historical certificate. For every pair transition it reads the
two canonical Paper XVII observation payloads at `t+1`, computes the exact
historical successor residual, and requires

```text
delta_z_next_historical = (4/5) delta_z_t + (1/5) r_clip.
```

On a current-observation fiber it additionally requires
`r_clip = 5 delta_z_next_historical`. The validator reconstructs the complete
pair universe from the cohort registry, redecodes the 459 source-cache
records, rederives all 6,975 pair records, and only then applies the frozen
seven-predicate and 15-cell classification. The producer has no scientific
outcome-writing authority.
The historical Paper XVII ASCII state hash is only an ancestry-compatibility
gate. New MTS-1 state identity is defined by the domain-tagged canonical binary
payload in [`exact_state_payload_v1.py`](exact_state_payload_v1.py); a digest
binds those bytes but does not replace exact payload semantics.

The registration preserves the six obstruction fibers separately and the five
persistent-safe cohorts separately. It does not pool them into two exchangeable
populations, run a hypothesis test, or claim a population prevalence.
Every unordered pair has one byte-level orientation: `source_a` is the smaller
source identifier, `source_b` is the larger, and every signed difference is
`value(source_a) - value(source_b)`. The clipping-fate table uses the same
`a -> b` orientation.

## Frozen objects

- 51 transient-obstruction sources in six `t=1` failure fibers;
- 570 unordered within-fiber pairs, all with different exact `t=2` coarse
  successors;
- 102 persistent-safe sources in five cohorts of sizes `51, 25, 19, 4, 3`;
- 1,755 unordered within-cohort pairs with equal exact observations at
  `t=2`, `t=3`, and `t=4`;
- a common transition grid `1->2`, `2->3`, and `3->4` for both source roles.

The exact membership and ordered-pair digests are in
[`results/mechanism_cohort_registry.v1.json`](results/mechanism_cohort_registry.v1.json).
The scientific and negative boundaries are in
[`MECHANISM_OF_TRANSIENT_SEPARATION.md`](MECHANISM_OF_TRANSIENT_SEPARATION.md).
The first execution-semantic refinement is frozen separately in
[`MTS1_SCOPED_EXECUTION_AMENDMENT.md`](MTS1_SCOPED_EXECUTION_AMENDMENT.md).

## Validation

Use the pinned Python 3.12 environment recorded by the Paper XVII runtime
receipt. Set its path outside the release closure:

```powershell
$py = $env:RIME_PY312
if (-not $py) { throw 'Set RIME_PY312 to the pinned Python 3.12 executable.' }
& $py validation\validate_mechanism_of_transient_separation_registration.py
& $py validation\test_exact_state_payload_v1.py
& $py validation\validate_mechanism_execution_amendment_v1.py
& $py validation\test_source_addressed_mechanism_producer_v1.py
& $py validation\validate_source_addressed_producer_registration_v1.py
& $py validation\test_mechanism_result_validation_v1.py
& $py validation\test_mts1_capped_runner_v1.py
& $py validation\validate_mechanism_validation_resource_gate_v1.py
```

These checks replay cohort membership and exact observation-payload relations,
compile and hostile-test the new exact transition kernel in a temporary
directory, exercise the producer only on synthetic states, validate the
historical-successor hostile control, and check the capped execution wrapper.
The static/synthetic resource preflight is bound in
[`mechanism_resource_contract.v1.json`](mechanism_resource_contract.v1.json)
and
[`results/mechanism_resource_preflight.v1.json`](results/mechanism_resource_preflight.v1.json).
It assumes one sequential source worker and freezes caps of 12 CPU core-hours,
12 monotonic wall hours, 32 GiB process-tree RSS, and 100 GiB incremental
result storage. Cap violation yields `UNRESOLVED`; source, cohort, or pair
dropping and a smaller-surface retry are forbidden.

The pre-execution checks above do not run the 153-source microscopic replay or
classify an outcome. That single-use execution has now completed under the
bound authority and resource caps. The result-owned inventory is
[`results/mts1-v1/inventory.json`](results/mts1-v1/inventory.json), the
validator-derived classification is
[`results/mts1-v1/validation/mechanism_classification.v1.json`](results/mts1-v1/validation/mechanism_classification.v1.json),
and the exhaustive validation receipt is
[`results/mts1-v1/validation/mechanism_validation.v1.receipt.json`](results/mts1-v1/validation/mechanism_validation.v1.receipt.json).
The compact post-execution closure is bound by
[`results/mts1-v1.freeze-manifest.json`](results/mts1-v1.freeze-manifest.json)
and its validation receipt. Validation is local exhaustive exact rederivation,
not independent replication; the producer was not replayed by the validator.

The exact payload and pair-record sidecar is approximately 4.5 GiB. It is
excluded from Git while its complete ordered byte inventory and closure digest
remain bound by the compact freeze. No external immutable sidecar anchor is
claimed yet.

## Boundary

The existing metadata already expose state-support and clipping-count
summaries. This registration therefore cannot certify that its broad interest
in clipping or support geometry was chosen without seeing those summaries.
It instead freezes the exact equations, pair universes, time controls, and
allowed feature families before any new pair-resolved drive or clipping
decomposition is produced.

A future `MTS-2: External Adjudication of Equivalence` would compare matched
autonomous and externally driven systems. It is not registered and has no
execution authority.
