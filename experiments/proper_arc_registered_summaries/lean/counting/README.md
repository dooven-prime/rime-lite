# Exact Actual-Summary Enumeration

This separate finite-combinatorial layer implements Theorem 6.1 of
`hal-05848115v1`. For every `c : ZMod n` and `2<=r<n`, put `m=n-r`.
The final statement retains the actual registered singleton-seed history
type on its left:

```lean
card_actual_registered_summaries c hr :
  Nat.card (ActualRegisteredSummaries c r) =
    (r-1)*n*((n+(n-r)-2).choose (n-r) +
      2*∑ b ∈ Finset.Icc 1 (n-r),
        3^(b-1)*(n+(n-r)-b-2).choose (n-r-b))
```

`hr : 2 <= r and r < n` implies `n>=3`. The type on the left is the
unchanged summary type from `summary/`: one complete chronological raw
`p,d` word from the singleton seed must produce all its literal fields.

## Four Interfaces

| Interface | Responsibility |
|---|---|
| C1 `card_summary_sigma` | Transport actual summaries through the frozen `actualRegisteredSummariesEquivParams`, then expand the two dependent sigma cardinalities. |
| C2 `card_codes_by_last_checkpoint` | Count one all-zero code, `2*3^(b-1)` codes at each `1<=b<=m`, and zero codes beyond m. |
| C3 `card_code_fibre_sum` | Weight those groups by the inherited actual-fibre cardinality and sum one origin component. |
| C4 `card_actual_registered_summaries` | Sum over `Fin (r-1)` to obtain the manuscript's exact formula (6.1). |

`sum_codes_by_last_checkpoint` is the common weighted grouping identity.
C2 follows by choosing an indicator weight; C3 uses the same identity
directly with the binomial fibre weight. Thus the enumeration does not
repeat the grouping argument or recompute any actual execution geometry.

`card_code_fibre` explicitly consumes the frozen actual placement-fibre
equivalence and `card_actualCodePlacements`. The endpoint `b=m` is kept:
`card_code_fibre_full` proves that each such code has n single-packet
phases. It does not substitute the positive-complement formula at k=0.

The shortest-complement regression is also all-parameter:

```lean
card_actual_registered_summaries_short_complement c hn :
  Nat.card (ActualRegisteredSummaries c (n-1)) = (n-2)*n*(n+1)
```

Here `hn : 3 <= n`. The empty chain and both one-event L/R codes are
included, even though the latter have the same full carrier source set.

## Replay And Local Freeze

From the parent Lean directory:

```powershell
python -B counting/validate_counting.py --check-upstream-git
python -B -m unittest discover -s counting/tests -p 'test_*.py' -v
```

The validator binds five new inputs in the
[local milestone manifest](milestones/summary-count-v1/manifest.json).
The [dependency report](milestones/summary-count-v1/dependency-audit.json)
records 13,382 declarations. The validator checks all seven previous
milestone manifests, their bound source bytes and reports unchanged;
recompiles the proof prerequisites and new modules; and audits 17 axiom
queries, 12 complete target signatures and their transitive dependencies.
The inherited summary-equivalence and fibre-cardinality declaration graphs
are compared exactly with their owning frozen reports. Only `propext`,
`Classical.choice` and `Quot.sound` are permitted axiom leaves.

The actual-summary definition, pure dependent parameter family, full-carrier
branch, formula and shortest-complement interface are checked explicitly.
Negative validator tests reject omitted dependencies, a formal-image
replacement for the actual domain, omitted k=0 phases, altered boundary
signatures and a fixed-pair total-count shortcut. The count imports no old
fixed-pair total-count theorem.

This local companion freeze is separate from the HAL v1 proof identity and
uses the pinned cached dependencies, not a fresh-machine cold replay.
Chain-length and rank refinements, fixed-pair specialization, generating
functions and asymptotic analysis remain separate later layers.
