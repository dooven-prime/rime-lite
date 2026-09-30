# Paper XXXIII Lean Capacity Spine

**Status:** paper-owned partial formalization.

The development machine-checks the data-independent forward-invariance
argument underlying Paper XXXIII, Theorem 5.1.

## Formalized Surface

| Lean declaration | Manuscript role |
|---|---|
| Reach.preserve | a one-step invariant persists along a concrete finite path |
| output_ne_punctured | a rank-five output cannot occupy the capacity-four punctured lane |
| ordinaryNonedge_step | one enabled lane-shaped return preserves the ordinary nonedge family |
| ordinaryNonedge_reach | the hostile family is forward invariant |
| ordinaryNonedge_not_target | the family is disjoint from the edge target |
| ordinaryNonedge_not_safeHit | no state in the family reaches the target |
| strict_safeHit_gap | with the inherited Safe-Hit-to-SameLane implication, one hostile state witnesses strict containment |

## Assumption Boundary

The abstract CapacitySystem consumes the concrete facts proved in the
manuscript:

- the punctured lane has cardinality four;
- enabled outputs retain support cardinality five;
- every output is punctured-lane-shaped or ordinary-lane-shaped;
- transport between ordinary lanes preserves marked nonedges; and
- every declared target has an edge marked pair.

The Lean development does not construct the concrete branch \(a_g\), prove
the cyclic lane arithmetic for \(n=5g,\Delta=g\), or infer these hypotheses
from the finite JSON controls. Those are manuscript arguments.

It also does not formalize source-addressed orbit incidence, survivor
placement, typed transfer membership, projectability, recursive return,
settlement, or reset bounds.

## Build

~~~text
lake build
lake env lean Paper33.lean
~~~

The project pins Lean 4.33.0 and Mathlib commit
db584cd6d46c92f209a44c0f1c829460d327499d.
