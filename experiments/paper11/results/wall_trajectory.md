# Paper XI Observable-Status Trajectory Controls

A wall event is counted only when an observable status changes between adjacent samples.

| Control | Steps | Ordered pairs | Events | Changed pairs | Event steps |
|---|---:|---:|---:|---:|---|
| GridWorld obstacle path | 3 | 600 | 190 | 140 | [1, 2] |
| SIR beta sweep | 21 | 6 | 4 | 4 | [1] |
| Graph edge-weight endpoint | 11 | 12 | 6 | 6 | [10] |

The event steps are sampled-path locations. They do not establish ambient codimension.
