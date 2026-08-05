# Legacy Paper XI Configuration Redundancy Audit

**Status:** excluded from the v2 wall spectrum and typed census.

Snapshot configurations: **166**.

The matrix excludes codimension, cross-species wall density, and trajectory-only quantities.

## PCA Summary

- Components for 90% variance: **3**
- Components for 95% variance: **3**
- This is an empirical dimension estimate, not an invariant-basis theorem.

## High-Correlation Pairs

| Left | Right | Correlation |
|---|---|---:|
| direct_unsupported_fraction | lie_unreached_fraction | +0.886 |
| direct_unsupported_fraction | mean_word_depth | +0.932 |
| direct_unsupported_fraction | max_word_depth | +0.923 |
| lie_unreached_fraction | mean_word_depth | +0.856 |
| mean_word_depth | max_word_depth | +0.938 |

## Trajectory Diagnostics

Trajectory quantities are reported separately; no trajectory PCA is performed.

| Control | Pair events | Field changes | Changed-pair fraction | Event steps | Max pair-event density |
|---|---:|---:|---:|---:|---:|
| GridWorld obstacle path | 236 | 314 | 0.290 | 2 | 0.220 |
| SIR beta sweep | 4 | 10 | 0.667 | 1 | 0.667 |
| Graph edge-weight endpoint | 6 | 12 | 0.500 | 1 | 0.500 |
