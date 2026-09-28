# Gross Budget, Richness, and Scope Derivation

Status: `SCOPE_INSTANTIATED_AWAITING_RUNNER_AND_PREFLIGHT`

Execution authority: `NONE`

The next finite-history registration is derived in one direction only:

```text
gross resource budget
  -> minimum window and shift richness
  -> D0 admission
  -> mechanical H/T derivation
```

No second performance-engineering round is authorized. The completed
four-worker mmap/Cython audit is consumed only as an exact-equivalence and
resource prior.

## Candidate Source Universe

The complete same-line candidate universe consists of unit basis states on all
`Y_known_pm` source rows with positive known-sign outgoing absolute mass. The
source-universe audit identifies:

```text
carrier nodes                         211,577
admissible nonzero outgoing rows      163,439
excluded zero outgoing rows            48,138
nonempty superclass strata                 25
```

This audit does not admit `D0`. It fixes the complete source universe from
which either the full domain or a preregistered reduced domain may be admitted.

The four-source resource benchmark is not treated as representative of all
163,439 sources. In particular, the maximum-degree and maximum-outgoing-mass
sources are structurally extreme, but exact clipping leaves one active state
while each step still visits about 11,219 and 9,636 edge contributions.

## Gross Budget

The frozen gross budget binds:

```text
48 CPU core-hours
12-hour wall-clock safety cap
32 GiB peak process-tree RSS
100 GiB incremental run storage
4 workers maximum
20% resource-only calibration reserve
70% primary scientific computation
10% orchestration, serialization, and closure reserve
```

The three pools are nonfungible. Unused calibration or closure resources do
not extend the scientific run, and an incomplete run does not receive an
outcome-dependent budget increase. The primary scientific pool is exactly
`33.6` core-hours, with a nominal four-worker wall allowance of `8.4` hours.

The budget was fixed from available resources, not from a desired memory order
or closure outcome. It does not itself choose richness, a source domain, an
order, or a horizon.

## Richness

The frozen richness values are

\[
W_{\min}=2,\qquad S_{\min}=1,
\]

and therefore

\[
R=\max(W_{\min},S_{\min}+1)=2.
\]

Every candidate maximum order must use at least

\[
T-H\ge W_{\min},\qquad T-H-1\ge S_{\min}.
\]

At maximum order, this gives two history windows and one internal
history-to-history shift. It is the minimum nondegenerate iterable-state
surface; the values were not chosen from resource convenience or closure.

## D0 Admission

The preferred domain is the complete 163,439-source universe. The baseline new
order is fixed as `h=2`, so the baseline horizon is

\[
T_{\rm floor}=2+R=4.
\]

This baseline does not consume the depth-above-four calibration pool. Admit the
complete domain only if the preregistered resource-allocation envelope admits
an attempt at this baseline scope. The envelope is not a proved worst-case
runtime bound over all sources, and admission is not execution completion. If
an admitted run exceeds a frozen gross cap, its scientific state is
`UNRESOLVED`; `D0` is not resized after execution starts. Otherwise derive the
largest affordable source count and select it without behavioral or closure
access:

1. stratify by registered superclass, retaining `<missing>` explicitly;
2. allocate one source to every nonempty stratum;
3. allocate remaining seats proportionally by largest remainder;
4. rank sources within each stratum by SHA-256 of
   `RIME_DC_D0_V1|<node_index>`, breaking ties by node index.

If the budget cannot admit at least one source from every nonempty stratum, the
scope is `UNRESOLVED`. A reduced-domain result is always reported as such and
cannot borrow a full-domain minimality claim from Paper XVI.

More explicitly, let `N` be the admitted source count, `m` the number of
nonempty strata, and `n_i` the size of stratum `i`. After assigning one seat to
each stratum, set

\[
A=N-m,\qquad C=\sum_j(n_j-1),
\]

and compute

\[
a_i=\left\lfloor\frac{A(n_i-1)}{C}\right\rfloor,
\qquad
r_i=A(n_i-1)\bmod C.
\]

If `L=A-sum_i(a_i)`, the final quota is

\[
q_i=1+a_i+\mathbf 1\{i\text{ is among the }L\text{ largest }r_j\}.
\]

Equal remainders are ordered by the registered stratum label. All quotient and
remainder operations are integer operations. Hashes rank members only after
the quotas are fixed. A separate read-only validator recomputes the dual
resource gate, quotas, membership, and exact index artifact before any later
scope can consume the admitted domain.

The four cost-envelope fields are canonical decimal strings. Gross-budget
decimals are parsed directly into `Decimal`, and the admission capacities are

\[
N_{\rm core}=\left\lfloor
\frac{(C_{\rm primary}-C_{\rm fixed})3600}{c_{\rm source}}
\right\rfloor,
\]

\[
N_{\rm wall}=\left\lfloor
\frac{(T_{\rm primary}-T_{\rm fixed})3600W\eta}{c_{\rm source}}
\right\rfloor,
\qquad
|D_0|=\min(163439,N_{\rm core},N_{\rm wall}).
\]

No binary floating conversion enters these floors or the serialized predicted
resource totals.

## Mechanical H/T Rule

Once `D0` and any required resource-only depth calibration are frozen, define

\[
T(H)=H+R.
\]

Select the largest `H` for which the admitted `D0`, all exact trajectories, and
all audits at orders `0,...,H` fit the remaining scientific budget. Set
`T=T(H)`. No extra horizon beyond the richness minimum is added in this first
registration, and an incomplete larger rectangle cannot replace a complete
smaller one.

The existing benchmark directly measures depth only through four. Any derived
`T>4` requires a resource-only calibration paid from the already frozen
calibration reserve. That calibration cannot group histories, read closure
outcomes, or receive more resources after its measured costs are known.

Every admitted rectangle must satisfy both the primary `33.6` core-hour cap
and the monotonic wall-clock cap. Four workers are a concurrency ceiling, not
a linear-speedup theorem. If calibration is used, the primary wall allowance
is bounded by the gross 12-hour cap minus actual registered calibration wall
time and the reserved closure allowance. If `T=4`, the calibration pool is
unused and remains nontransferable.

## Instantiated First Scope

The frozen allocation model gives `N_core=993` and `N_wall=711`; therefore the
one-shot admitted domain is a 711-source
`REDUCED_STRATIFIED_HASH_D0`. It covers all 25 registered superclass strata.
With `R=2`, the first rectangle is

\[
H=2,\qquad T=4.
\]

No depth-above-four calibration was used. Core-hours and wall-clock are modeled
for admission. The 32 GiB RAM and 100 GiB incremental-storage limits remain
hard runtime caps and require a static runner preflight before execution
authority. Preflight failure yields `UNRESOLVED` without resizing `D0`.
