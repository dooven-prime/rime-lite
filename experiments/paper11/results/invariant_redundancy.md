# Paper XI Definition-Compatible Redundancy Audit

Snapshot configurations: **166**.

The matrix excludes codimension, cross-species wall density, and trajectory-only quantities.

## PCA Summary

- Components for 90% variance: **3**
- Components for 95% variance: **3**
- This is an empirical dimension estimate, not an invariant-basis theorem.

## High-Correlation Pairs

| Left | Right | Correlation |
|---|---|---:|
| direct_frozen_fraction | lie_terminal_fraction | +0.886 |
| direct_frozen_fraction | mean_word_depth | +0.932 |
| direct_frozen_fraction | max_word_depth | +0.923 |
| lie_terminal_fraction | mean_word_depth | +0.856 |
| mean_word_depth | max_word_depth | +0.938 |

## Trajectory Diagnostics

Trajectory quantities are reported separately; no trajectory PCA is performed.

| Control | Events | Changed-pair fraction | Event steps | Max event density |
|---|---:|---:|---:|---:|
| GridWorld obstacle path | 190 | 0.233 | 2 | 0.167 |
| SIR beta sweep | 4 | 0.667 | 1 | 0.667 |
| Graph edge-weight endpoint | 6 | 0.500 | 1 | 0.500 |
