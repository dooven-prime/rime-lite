# Finite-History Closure Design

Status: `DESIGN_FROZEN_NOT_REGISTERED`

Execution authority: `NONE`

## Question

Let `X` be the microscopic state space, `F` the frozen deterministic update,
and `O` the registered coarse observation. Write

\[
z_t(x)=O(F^t x)
\]

and define the order-`h` history representation

\[
\Psi_h(x)=(z_h(x),z_{h-1}(x),\ldots,z_0(x)).
\]

The primary question is whether there is a map `G_h` on a registered
orbit-window history image such that the same update applies across sources
and times.

For a frozen microscopic source domain `D_0` and horizon `T`, define

\[
\Omega_{h,T}=\{(x,t):x\in D_0,\ h\le t<T\},
\]

\[
H_h(x,t)=(z_t(x),z_{t-1}(x),\ldots,z_{t-h}(x)),
\qquad
S_h(x,t)=z_{t+1}(x).
\]

The exact closure criterion is

\[
H_h(x,t)=H_h(y,s)\Longrightarrow S_h(x,t)=S_h(y,s)
\]

for every `(x,t),(y,s)` in `Omega_(h,T)`. Thus cross-source and cross-time
comparisons are part of the primary definition, not optional validator checks.
When the criterion holds, it defines `G_h` on the registered history image by

\[
G_h(H_h(x,t))=S_h(x,t).
\]

The historical prefix question

\[
\Psi_h(x)=\Psi_h(y)\Longrightarrow z_{h+1}(x)=z_{h+1}(y)
\]

remains a read-only comparison surface. It is not the primary criterion of
this line.

The optimization variable is only the memory order `h`. History, moments,
spectral modes, Koopman coordinates, and learned predictive states are not
mixed into one search family.

## Prefix Factorization Is Not Yet an Iterable State

Paper XVI tests initial trajectory prefixes. Such a test proves or refutes a
factorization on its declared prefix domain, but a successful prefix test alone
does not make the history representation an iterable dynamic state.

An iterable-state claim requires a separately registered orbit-window domain.
For trajectories generated from a frozen initial set `D_0`, define windows

\[
\Psi_{h,t}(x)=(z_t(x),z_{t-1}(x),\ldots,z_{t-h}(x)),
\qquad h\le t<T.
\]

The same time-homogeneous `G_h` must factor every registered window, including
comparisons across different sources and times. The registered history image
must also be closed under the induced shift wherever a next window is claimed.
Only that stronger result may be called a closed finite-history state.

The primary criterion is frozen as:

- `ORBIT_WINDOW_CLOSURE`, including all cross-source and cross-time fibers in
  `Omega_(h,T)`.

`PREFIX_FACTORIZATION` and `ORBIT_WINDOW_CLOSURE` must not be merged.

## Horizon-Bounded Shift

Histories are ordered newest first. If

\[
u=(z_t,z_{t-1},\ldots,z_{t-h}),
\]

then the induced shift is

\[
\sigma_h(u)=(G_h(u),z_t,\ldots,z_{t-h+1}).
\]

Let `H_(h,T)^-` contain only registered histories with another history window
inside the registered horizon. The shift obligation is

\[
\sigma_h(H_{h,T}^{-})\subseteq H_{h,T}.
\]

This supports a time-homogeneous update only over the registered orbit-window
image and registered shifts. It does not establish indefinite forward
invariance.

## Exact Equality and Defect

History membership is an exact fiber question. Floating-point closeness must
not create or merge a history fiber. A producer must use a canonical exact
representation of the registered rational dynamics, or fail closed before
classification. Floating-point trajectories may be retained only as
cross-checks.

Every rational is represented in reduced form `p/q`, with `q > 0` and
`gcd(|p|,q)=1`. Zero and sign are determined by `p`; clipped-ReLU comparisons
use exact integer cross multiplication. Hashes and modular fingerprints may
index candidate payloads, but they cannot certify mathematical equality. A
hash match must be followed by canonical rational payload comparison before
two windows enter the same fiber.

For an exact history fiber `C`, define the successor defect

\[
\Delta_h(C)=\max_{x,y\in C}\lVert z_{h+1}(x)-z_{h+1}(y)\rVert.
\]

Exact deterministic closure requires every successor difference to vanish.
An approximate criterion such as `Delta_h <= epsilon` is a separate future
contract with its own norm and tolerance; it cannot be inferred from this
design.

## Complexity and Compression

Within this family,

\[
\Psi_{h_1}\preceq\Psi_{h_2}\quad\text{means only}\quad h_1\le h_2.
\]

No parameter count, bit complexity, mode count, or learned-model complexity is
part of this order.

For each tested order, the result must report

\[
N_h=|\Omega_{h,T}|,\qquad
K_h=|\operatorname{im}H_h|,\qquad
M_h=\max_C |C|,\qquad
N_h-K_h.
\]

The derived descriptive ratio

\[
\rho_h=\frac{K_h}{N_h}
\]

may be reported for visualization. It is not an admission criterion or a
quality score. Values below one expose non-singleton history fibers; their
successors still determine whether the representation closes or fails.

These distinguish genuine compression from a finite-domain injective code. A
closure result is classified as:

- `EXACT_CLOSED_NONINJECTIVE` when closure holds and at least one history
  fiber contains more than one registered microscopic source;
- `EXACT_CLOSED_BY_INJECTIVITY` when closure holds only after every registered
  history fiber becomes a singleton;
- `FAILED_EXACT_CLOSURE` when an exact same-history/different-successor witness
  exists;
- `UNRESOLVED` when exact generation or exhaustive classification fails.

`EXACT_CLOSED_BY_INJECTIVITY` is a valid finite-domain factorization result but
not evidence of nontrivial dynamic compression.

A minimal closing order `h_star` may be reported only when every lower tested
order has an exact obstruction and order `h_star` passes an exhaustive exact
classification on the same domain. A minimal compressed-state order requires
the stronger `EXACT_CLOSED_NONINJECTIVE` outcome.

If every registered order through `H` fails, the only admissible statement is:

> No exact closure was found through history order `H` on the registered
> domain.

This does not imply infinite memory.

## Inherited Boundary

Paper XVI and its source-addressed artifacts establish bounded failures at
orders zero and one on historical prefix domains. They are read-only prior
evidence. They cannot prove minimality under `ORBIT_WINDOW_CLOSURE`. Before a
future result can report a minimal closing order, orders zero and one and every
other lower order must be classified again on the same `D_0`, `T`, exact
encoding, and window universe.

The new line must not rewrite Paper XVI, reuse Digital Fly E1 candidate or
vault schemas, or treat predictive accuracy as exact factorization.

## Source Universe and Shared Orbits

The preferred `D_0` is the complete source universe of the corresponding
Paper XVI closure line. This is required for a same-domain minimal-order
statement. If exact resource limits require a reduced domain, the reduction
rule must depend only on frozen structure or indices and be registered before
orbit generation. The strongest admissible conclusion is then explicitly
restricted to the registered reduced domain.

All orders `h=0,...,H` share one exact orbit generation:

```text
x in D_0
  -> (x_0,z_0),...,(x_T,z_T)
  -> immutable exact-observation orbit receipt
  -> derived window audits h=0,...,H
```

The microscopic state may be streamed. Once the next exact state and its
observation have been bound, the prior microscopic payload need not be kept
for fiber grouping. The persistent theorem-facing surface consists of exact
observations, source/time identities, required state digests or checkpoints,
and replay provenance. Each order then has

\[
N_h=|D_0|(T-h).
\]

No order may regenerate a different orbit or use a different source subset.

## Window and Shift Richness

At maximum order `H`, each source supplies

\[
W_{\rm windows}=T-H
\]

registered windows. Only

\[
W_{\rm shift}=T-H-1
\]

have a next history window inside the horizon. Registration therefore freezes
two independent gates,

\[
T-H\ge W_{\min},\qquad T-H-1\ge S_{\min}.
\]

This prevents an iterable-state claim from resting on a terminal successor
with no meaningful registered shift surface.

## Execution Backend Boundary

Exact rational orbit generation remains normative. GPU or modular arithmetic
may accelerate structural preprocessing, support propagation, or candidate
prefiltering, but cannot replace reduced-rational payload comparison. A modular
mismatch may reject equality; modular agreement cannot certify it. Any
accelerator must bind its backend and preserve a CPU exact replay path for
theorem-facing equality.

## Registration Blockers

The primary criterion is already frozen as `ORBIT_WINDOW_CLOSURE`. Before the
main experiment receives execution authority, freeze:

1. exact initial/source domain and time horizon `T`;
2. maximum registered history order `H`;
3. minimum window and shift richness values `W_min` and `S_min`;
4. canonical exact state and history encoding;
5. exhaustive grouping and successor-comparison algorithm;
6. resource budget, output schema, producer, validator, and receipt contract;
7. whether a no-obstruction result is complete enough to certify finite-domain
   closure;
8. failure behavior for arithmetic overflow, unsupported exact operations,
   incomplete enumeration, or nonfinite numerical cross-checks.

Before fixing `H` or `T`, run only the independently registered exact-arithmetic
resource benchmark. It may measure exact step cost, bit growth, support growth,
observation encoding, memory, and throughput. It may not group fibers, compare
successors, classify closure, or recommend an order from observed outcomes.

After the benchmark, freeze a gross compute allowance and an overhead reserve.
Only then may registration select the largest complete rectangular scope
`(D_0,H,T)` satisfying both richness gates and exhaustive classification of
every order `0,...,H`. A larger incomplete scope must not replace a smaller
complete one.

Let

\[
R=\max(W_{\min},S_{\min}+1).
\]

Then both richness gates require `T >= H+R`. The completed resource benchmark
measures exact growth only through depth four. It cannot support a cost model
for `T > 4`. A registration must therefore either require `T <= 4` or reserve,
before inspecting deeper arithmetic, a fixed resource-only depth-growth
calibration budget. Calibration may measure steps five and six but may not
group fibers, read closure outcomes, or expand its allocation after observing
costs.

Gross budget is a tuple, not wall time alone. It binds CPU core-hours,
wall-clock safety cap, peak RAM, disk allowance, and maximum workers. Changing
worker count does not change the scientific evaluation count, but it does
change resource consumption and must remain within the same frozen tuple.

Until these fields are registered, no trajectory generation or closure search
is authorized.
