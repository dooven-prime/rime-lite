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

Run the current release audit from the repository root:

```bash
python experiments/paper9/rate_hierarchy.py
python experiments/paper9/calibrated_response.py
python experiments/paper9/nn_training_sof_tau.py
python experiments/paper9/nn_activation_sof.py
python experiments/paper9/validation/validate_results.py
```

Generated public records are stored in `results/`. The NN binary rows are
pointwise cutoff-relative audits. Because the diagnostic does not coherently
continue sector labels across training time, they are not temporal repair
events.

Both three-sector records are relative to their declared trajectory
parameterization, observable normalization, Frobenius norm, and response
policy. Neither is an intrinsic rate invariant of the static SOF.

## Archive

`archive/` preserves the v1 Rubik generator-weight, plateau, and hard-coded
state-mixing summaries. Those scripts are historical provenance only and are
not current evidence for Paper IX v2.
