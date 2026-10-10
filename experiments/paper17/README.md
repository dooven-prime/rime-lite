# Paper XVII Computational Artifacts

**Status:** `FROZEN_FOR_RELEASE_CANDIDATE`

**Execution authority:** `NONE_COMPLETED`

This package is the paper-owned evidence surface for the Paper XVII candidate,
*Exact Post-Transient Coarse Factorization in a Reduced Male Drosophila CNS
Model*. It combines the reached-set factorization result with a separately
registered exact transition-layer census. Directory placement does not publish
the paper or promote either result beyond the boundaries below.

## Evidence Surface

The registered run used a reduced domain of 711 sources, exact rational
dynamics, and the finite horizon `T=4`. The original order-specific result is
retained unchanged as historical primary output:

```text
h=0  FAILED_EXACT_CLOSURE
h=1  FAILED_EXACT_CLOSURE
h=2  EXACT_CLOSED_NONINJECTIVE
```

Those rows use different left boundaries and therefore do not establish a
minimal memory order. The theorem-facing correction surface is instead:

1. on the common support `t in {2,3}`, orders zero, one, and two induce the
   same exact noninjective successor-compatible partition;
2. all 51 sources in the six `t=1` obstruction fibers have globally singleton
   coarse observations at `t=2`;
3. the remaining noninjectivity is carried by five disjoint cohorts of sizes
   `51, 25, 19, 4, 3`, with identical membership at `t=2` and `t=3` and
   successor-consistent registered evolution;
4. all 614 terminal `t=4` observations lie outside the verified common coarse
   image, so the certificate contains one internal shift but no coarse
   endomap.

The mechanism census replays 153 source states into 459 exact source-transition
cache records and derives 6,975 pair-transition records. All 15 registered
comparison cells have different normalized seven-predicate signature
histograms. Two exact predicates separate every transient-obstruction pair
from every persistent-safe pair at both `2 -> 3` and `3 -> 4`:

```text
CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL
FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION
```

Both have direction `TRANSIENT_ALL__PERSISTENT_NONE`. No registered primary
predicate is an all-versus-none separator at `1 -> 2`. The mechanism result
therefore establishes a stable exact post-separation layer contrast, not the
cause of the initial separation.

The central safe statement is:

> The transient does not repair the original ambiguous fibers. It eliminates
> them. Exact noninjective coarse factorization is then carried by a disjoint family
> of persistent successor-consistent fibers.

Here "eliminates" means that the original unsafe equivalence classes are
absent from the later registered reached-set slices because their members are
coarsely separated. It does not mean that microscopic states converge or are
destroyed.

## Validation Setup

Use CPython 3.12.6 and install the pinned dependencies:

```powershell
python -m pip install -r requirements-exact-optimized-v1.txt
python validation/validate_public_package.py
```

The unified entry point checks the pinned runtime, artifact bindings, frozen
classification, common-support correction, transient-fiber decomposition,
terminal-image boundary, compact mechanism freeze, and manuscript evidence
table. It is read-only and does not replay the 4.5 GiB mechanism sidecar.

The release-candidate closure is recorded in `release-manifest.v1.json`; its
local verification receipt is
`results/release.v1.validation-receipt.json`. The receipt is excluded from its
own closure.

## Exact Anchors

The result-owned sidecar contains 1,425 files and has SHA-256
`5ed5853b43901d927fb43d2ff1926f6bcb79343d95e15e62df8f770259c52ad9`.
The paper-owned anchor first entered Git history at commit
`99e2ac5a57afed27e5f213f658ddd5c3e6e93932`. Historical evidence-table
entries are resolved from that commit rather than substituted from current
HEAD. Later terminal-image and manuscript-boundary records are resolved from
their explicitly bound paper-owned bytes.

The registration record, completed result, and exact sidecar first entered
that immutable history together. The anchor therefore does not independently
establish that registration preceded execution.

The D0-admission and primary-run receipts are retained as historical bound
bytes. The default public gate begins at the frozen result-owned sidecar and
compares each downstream replayable receipt with the validator's canonical
output; it does not claim to recreate the historical executable environment.

These checks begin from the result-owned exact sidecar. They do not rerun the
microscopic orbit producer, establish clean-clone generation closure, or
provide independent replication. `build_result_anchor.py` likewise consumes
paper-owned bytes by default. Its optional `--compare-exploratory-source`
gate compares the historical import source when that tree is locally present;
the comparison is not a default release dependency.

The design, registration, budget, preflight, and execution records retained in
this directory are package-only historical production context. They do not
enter the theorem-facing release identity merely because they are present.

The MTS-1 exact sidecar contains 2,481 artifacts totaling 4,837,598,145 bytes.
It is represented publicly by `mechanism/results/mts1-v1/inventory.json`, the
ordered sidecar closure digest
`ea6725ad7acdb493ca2ccbe629b477e902f62563b00d25953735961237d86096`,
the exhaustive local validation receipt, and the compact post-execution freeze.
The sidecar is not tracked in Git and currently has no external immutable
anchor. Loss of those local bytes would remove exact-byte sidecar verification;
the compact closure must not be described as a clean-clone producer replay.

## Claim Boundary

- The domain is the reduced `D0=711` frozen by the declared pre-execution
  registration record, not the full source universe. The release closure does
  not independently authenticate that record's temporal precedence.
- The horizon is finite (`T=4`); no indefinite forward invariance is claimed.
- The verified factor is not an endomap on one coarse image; the terminal
  successor image lies outside the common `t in {2,3}` image.
- The result is exact on the registered finite domain, not a population-level
  neuroscience theorem.
- The exact post-separation clipping/fate contrast is verified only on the
  registered cohorts and transitions. No universal registered separator exists
  at `1 -> 2`, so the initial trigger remains unidentified and may be
  heterogeneous or compositional.
- No biological causal attribution, external-world effect, convergence,
  recurrent-input explanation, or slow-mode mechanism is identified.
- The original runtime and compiled producer closure is recorded but is not
  represented as clean-clone producer replay.
- Local exact replay is not independent validation.

The broader exploratory MaleCNS tree is not part of this paper-owned anchor.
