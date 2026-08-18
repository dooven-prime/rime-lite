# Paper IX Experiments

This directory supports the finite examples and computational observations in
Paper IX. It does not prove a universal deformation law or a proxy-to-shadow
bridge.

## Current Evidence

| Artifact | Role | Claim status |
|----------|------|--------------|
| `rate_hierarchy.py` | validates the exact three-sector first-order/direct versus second-order/commutator threshold construction | theorem validation |
| `calibrated_response.py` | realizes the normalized two-channel exponential response model with half-response times `30 < 1380` | Computational Certificate; the analytic inequality is proved in Paper IX |
| `nn_training_sof_tau.py` | reproduces the default `K0/K1/K2` endpoint-normalized sampled half-response ordering | Computational Observation |
| `nn_activation_sof.py` | records a fixed-weight activation/sectorization sensitivity audit | Computational Observation |
| `validation/validate_results.py` | checks the versioned JSON records and their claim-facing invariants | release validator |
| `validation/migrate_deformation_records_v2_1.py` | classifies retained dynamic records under the v2.1 object/record type split without inferring dynamics or causes | semantic-type migration validator |
| `results/deformation-record-migration-v2.1.json` | source-addressed `ObjectDeformation` / ordered-path `ObjectTrajectory` / `SOFObservationRecord` / `DeformationRecord` migration ledger | migration evidence |

Read-only release verification from the repository root is:

```bash
python experiments/paper9/validation/validate_results.py
python experiments/paper9/validation/migrate_deformation_records_v2_1.py
```

The four experiment scripts above are rebuild commands: each writes a result
under `results/` (the NN training script may also append a diagnostic log).
Run them only in a scratch copy or staging area, then compare and explicitly
promote candidate bytes. A release verification must not invoke them in the
tracked worktree. Generated public records are stored in `results/`. The NN binary rows are
pointwise cutoff-relative audits. Because the diagnostic does not coherently
continue sector labels across training time, they are not temporal repair
events.

Both three-sector records are relative to their declared trajectory
parameterization, observable normalization, Frobenius norm, and response
policy. Neither is an intrinsic rate invariant of the static SOF.

The v2.1 ledger treats the three retained sampled trajectories as legacy
deformation records. Because their frozen artifacts do not independently bind
an underlying transition model, they remain `LEGACY_RECORD_ONLY` with
`object_transition_model = NOT_DECLARED` and
`causal_mechanism_status = NOT_ESTABLISHED`. The static activation audit is
not migrated as a deformation record.

## Archive

`archive/` preserves the v1 Rubik generator-weight, plateau, and hard-coded
state-mixing summaries. Those scripts are historical provenance only and are
not current evidence for Paper IX v2.
