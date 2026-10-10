# Persistent Effective-Drive Boundary

**Evidence status:** bound supplementary documentation for Paper XVII
publication candidate-2, Computational Certificate 7.3. The manuscript owns
the claim. This note does not replace the manuscript or modify MTS-1 outcomes.

The [exact readout](persistent_safe_effective_drive.v1.json) and
[read-only replay](../validation/audit_persistent_safe_effective_drive_v1.py)
are byte-identical mirrors of the integration-worktree audit. They consume
the previously frozen MTS-1 inventory and caches, not a new operator run.

## Complete Noninjective Coverage

All five persistent cohorts have sizes 51,25,19,4,3. The audit covers every
one of their 102 sources at the saved current times 1,2,3: 306 records.
Every raw drive is nonzero and coordinatewise nonpositive, and every clipped
drive is zero. The registered update at each of these saved states is thus

$$
F_Y(x_t)=\frac45x_t.
$$

On the declared common support 2,3, the ten non-singleton fibers contain
204 source-time points and account for all 194 redundant windows. Common
linear leakage is a sufficient explanation of their one-step coarse
equality. The microscopic differences need not vanish.

## Replay and Scope

The default publication gate checks the exact JSON and implementation
bindings, fixed cohort/time coverage, parent inventory identities, and
aggregate consistency. It does not replay all source payloads.

With the exact MTS-1 sidecar materialized, the optional `--check` command
hashes and decodes all selected state, raw-drive and clipped-drive payloads,
recomputes coordinatewise clipping, checks cohort observation equality, and
compares the entire regenerated readout with the saved JSON. It does not
recompute the operator action or independently replicate the experiment.

The time-1 records concern the same cohort sources, not closure of every
time-1 fiber. This is not a pure-leak classification of all 711 sources,
an extension of the finite common coarse image, a long-horizon execution,
or evidence of active compensation or learned correction.

Only total-drive signs are checked. This result does not establish
nonpositivity of each source-block contribution or arbitrary block-subset
robustness for all 102 sources. Earlier 76-source blockwise and 565/567
transient-intervention readouts remain separate research records outside
this publication closure.
