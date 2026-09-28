# Paper XVII Result Anchor

**Status:** `RESULT_OWNED_ANCHOR_READY`

**Execution authority:** `NONE_COMPLETED`

This package is the paper-owned result anchor for the Paper XVII candidate,
*Exact Post-Transient Coarse-State Closure in a Reduced Male Drosophila CNS
Model*. It imports a selected exact-byte closure from the exploratory MaleCNS
dynamic-compression line. Directory placement does not publish the paper or
promote the result beyond the boundaries below.

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
   same exact noninjective closed partition;
2. all 51 sources in the six `t=1` obstruction fibers have globally singleton
   coarse observations at `t=2`;
3. the remaining noninjectivity is carried by five disjoint cohorts of sizes
   `51, 25, 19, 4, 3`, with identical membership at `t=2` and `t=3` and
   successor-consistent registered evolution.

The central safe statement is:

> The transient does not repair the original ambiguous fibers. It eliminates
> them. Exact noninjective state descent is then carried by a disjoint family
> of persistent successor-consistent fibers.

Here "eliminates" means that the original unsafe equivalence classes are
absent from the later registered reached-set slices because their members are
coarsely separated. It does not mean that microscopic states converge or are
destroyed.

## Validation

The package contains the deterministic USTAR sidecar used for exact replay.
From this directory, run:

```powershell
$py = 'python'
& $py validation/validate_result_anchor.py
& $py validation/validate_finite_history_closure_freeze.py
& $py validation/validate_finite_history_common_support_audit.py
& $py validation/validate_finite_history_transient_fiber_audit.py
```

These checks replay classification and the two corrective audits from the
result-owned exact sidecar. They do not rerun the microscopic orbit producer
and are not independent replication.

## Claim Boundary

- The domain is the preregistered reduced `D0=711`, not the full source
  universe.
- The horizon is finite (`T=4`); no indefinite forward invariance is claimed.
- The result is exact on the registered finite domain, not a population-level
  neuroscience theorem.
- No clipping, convergence, recurrent-input, slow-mode, or biological causal
  mechanism is identified.
- The original runtime and compiled producer closure is recorded but is not
  represented as clean-clone producer replay.
- Local exact replay is not independent validation.

The broader exploratory MaleCNS tree is not part of this paper-owned anchor.
