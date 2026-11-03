# Wallis Ratio: Separate Analytic Companion

This layer proves the future-event count's real ratio limit. It consumes the
finite combinatorial milestone without changing any of its 81 frozen inputs.
It is separate from the HAL v1 proof identity and has its own source and
dependency audit.

## Three main statements

`tendsto_scaled_central_binomial` proves

\[
\lim_{m\to\infty}\frac{\sqrt m\binom{2m}{m}}{4^m}
=\frac1{\sqrt\pi}.
\]

`tendsto_normalized_remainder` proves

\[
\lim_{m\to\infty}
\frac{1-(m+2)(m+1)}{\sqrt{m+2}\,4^{m+2}}=0.
\]

Both statements are in `WallisAsymptotics.lean`, which imports only Mathlib.
Their declaration-level dependency closures contain neither the finite model
nor a Stirling input.
The short elementary normalization proof has its upstream code attribution
recorded in [NOTICE.md](NOTICE.md).

`tendsto_futureQuotient_normalized` proves

\[
\lim_{m\to\infty}
\frac{|\operatorname{FutureQuotient}(m+3)|}
{\sqrt{m+3}\,4^{m+3}}=\frac5{16\sqrt\pi}.
\]

Here `futureCardReal m` is the real coercion of the cardinality of the actual
all-word quotient at horizon `n=m+3`. Every legal horizon `n>=3` occurs in
this cofinal parametrization. There is no artificial value at `n=0`, no
formal-binomial count substituted for an unproved actual cardinality, and
no word-length truncation.

## Proof interfaces

For `B_m=binom(2m,m)`, the pinned Mathlib Wallis formula gives

\[
W_m=\frac{16^m}{(2m+1)B_m^2}\to\frac\pi2.
\]

The proof first establishes the literal squared identity and then uses
nonnegativity to take the positive square root:

\[
\frac{\sqrt m B_m}{4^m}
=\sqrt{\frac{m/(2m+1)}{W_m}}\to\frac1{\sqrt\pi}.
\]

The remainder numerator is `-(m^2+3m+1)`. Polynomial-over-geometric decay
and the reciprocal square-root limit prove its normalized limit directly.

Only the final bridge imports `FutureEvent.ClosedQuotientCount`. It uses
`card_futureQuotient_additive` to justify the natural subtraction before
casting `card_futureQuotient_closed` to the reals. The exact identity is

\[
Q_{m+2}=\left(5m+3-\frac1{m+1}\right)B_m-(m+2)(m+1)+1.
\]

The exact normalization retains the factor `4^(m+2)=16*4^m`. The three
leading factors tend to `5`, `1` and `1/sqrt(pi)`; the remainder tends to
zero. The concluding theorem refers to the actual quotient cardinality,
not just to the algebraic expression.

## Build and audit

Use the parent package's pinned Lean `4.33.0` and Mathlib
`db584cd6d46c92f209a44c0f1c829460d327499d`. From the parent Lean directory:

```powershell
python -B analysis/validate_analysis.py
python -B -m unittest discover -s analysis/tests -p 'test_*.py' -v
```

`RIME_LAKE_EXE` can select the pinned `lake.exe`. The validator checks all
81 frozen finite inputs, builds the finite root, compiles the two analytic
modules, and runs the analytic audit. No finite source or Lake configuration
is edited; generated analytic `.olean` files stay under `.lake/`.

The audit separately checks all twelve analytic/helper theorems. For the
three main statements it also records full signatures, transitive
declaration dependencies and axiom leaves, using the frozen finite
milestone's declaration-graph walker. It rejects a missing actual-count
bridge, a model dependency in the first two statements, a Stirling input,
or any axiom outside `propext`, `Classical.choice`, `Quot.sound`.

The exact local record is in `milestones/wallis-ratio-v1/manifest.json` and
`dependency-audit.json`. `--freeze` creates an absent record once; ordinary
replay compares exact source hashes and the complete dependency report.
The five analytic source inputs and the finite milestone are bound
separately. Replay uses local pinned dependency caches; it is not a
fresh-machine cold-replay claim.

This layer covers only the future-event count's asymptotic ratio. The
full-summary observer, an executable minimizer and algorithmic resource
bounds are different interfaces.
