# Two Observer Growth Rates

This separate Lean companion compares two observation contracts on the same
singleton-seed-generated `p,d` dynamics. It consumes the frozen finite
future-event classification, the Wallis asymptotic companion, and the
full-summary observer/count bridge without changing their source bytes.

## Results

On the cofinal horizons `n=m+3`, `fullCardReal` and
`FutureEventAnalysis.futureCardReal` are casts of the cardinalities of the
actual all-word observer quotients. The final theorems prove

\[
\lim_{n\to\infty}\frac{Q_n^{\rm full}}{n(9/2)^n}=\frac4{81},
\qquad
\lim_{n\to\infty}
\frac{Q_n^{\rm full}/Q_n^{\rm future}}{\sqrt n(9/8)^n}
=\frac{64\sqrt\pi}{405}.
\]

The ratio also tends to positive infinity. The already-frozen future-event
limit is `Q_future/(sqrt(n)*4^n) -> 5/(16*sqrt(pi))`.

`SummarySeries.lean` is independent of both models. It rewrites the exact
fixed-pair bracket as a truncated negative-binomial series and proves

\[
0\le 1-\frac{B_{m+1}}{(9/2)^{m+1}}\le(8/9)^{m+1}.
\]

`ObserverGrowth.lean` applies that estimate to the actual full-summary
quotient through `FullSummary.card_fullQuotient_closed`, proves that its
unregistered summands are negligible, and combines the result with the
frozen future-event Wallis limit. The comparison is relative to these two
observation contracts, not a reset-word or general memory lower bound.

## Replay

From the parent Lean directory, using the pinned Lean 4.33.0 toolchain:

```powershell
python -B comparison/validate_comparison.py
python -B -m unittest discover -s comparison/tests -p 'test_*.py' -v
```

`--source-only` checks hashes without claiming a kernel replay. The default
rebuilds the pinned finite library, eight owner-count modules, both prior
extension proof layers, and this companion before checking the dependency
report. It rejects missing actual-count inputs, altered theorem signatures,
incomplete declaration graphs, and axioms outside `propext`,
`Classical.choice`, and `Quot.sound`.

The [local milestone](milestones/observer-growth-v1/manifest.json) binds
five new source inputs, four explicit target signatures, the complete
dependency graph and all 16 new theorem axiom checks. Its three prerequisite
manifest hashes identify the separate frozen closures. The recorded Lean
executable and Mathlib commit are checked during replay. This local
companion does not change the deposited HAL v1 proof identity.
