# Paper XI Sparse Typed-State Trajectory Controls

A pair event is counted only when at least one declared typed field changes between adjacent samples.

| Control | Steps | Ordered pairs | Pair events | Field changes | Changed pairs | Event steps |
|---|---:|---:|---:|---:|---:|---|
| GridWorld obstacle path | 3 | 600 | 236 | 314 | 174 | [1, 2] |
| SIR beta sweep | 21 | 6 | 4 | 10 | 4 | [1] |
| Graph edge-weight endpoint | 11 | 12 | 6 | 12 | 6 | [10] |

The event steps are sampled-path locations. They do not establish ambient codimension.
