# Lean proof package

This directory is self-contained apart from its locked external Mathlib
dependencies. Its `RegisteredAbsorptionChains` library reads only the
vendored `upstream/` sources identified in the parent provenance file.
No path dependency points into `experiments/exploratory/`.

## Commands

From this directory, with the pinned toolchain selected:

```text
lake exe cache get
lake build
lake env lean FusionLogCompression/AxiomAudit.lean
```

The recommended parent-level replay launcher additionally checks SHA-256
input identity, the Lean runtime commit and all printed axiom sets. See
[../REPRODUCING.md](../REPRODUCING.md).

## Module Owners

| Module | Responsibility |
| --- | --- |
| `M1Batch` | Explicit hole-crossing word; exact endpoint, fusion-freedom and `2*n+f` cost |
| `M2AdjacentFusion` | Ordered-port routing followed by exactly one effective fusion |
| `SourceAdjacentGap` | Source-order boundary to physical hole certificate |
| `FullFusionLog` | Complete-log wrapper, fusion-free preservation and one-event append |
| `M3BatchPlacement` | Plans indexed by actual successor states; word, cost and phase composition |
| `M3GapFlow` | Normalized cyclic flow, zero edge, conservation and bounded mass |
| `M3GapBatch` | One positive flow edge as an actual compressed batch |
| `M3LinearSchedule` | Donor capacities and zero-cut arithmetic induction |
| `M3CyclicSchedule` | Cyclic reindexing and bounded actual-plan construction |
| `M3Placement` | Exact target phase, rank-one branch and final M3 theorems |
| `AxiomAudit` | Public signatures and transitive axiom checks for 18 targets |

The aggregate `FusionLogCompression.lean` imports the completed M1-M3
proofs. The audit imports that aggregate and is invoked separately, avoiding
a circular import. Build warnings are existing linter suggestions, not
proof placeholders.

M4 complete-log replay and shortest-word results are outside this package's
checked milestone. M3 does not depend on their completion.
