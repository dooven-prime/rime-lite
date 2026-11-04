# Dependent Generated-Summary Equivalence

This layer proves Theorem 5.3 of `hal-05848115v1` for arbitrary source
start `c : ZMod n` and `2<=r<n`:

```lean
actualRegisteredSummariesEquivParams c hr :
  ActualRegisteredSummaries c r ≃ SummaryParams ⟨hr.1,hr.2.le⟩

SummaryParams hr =
  (_ : Fin (r-1)) × (v : Code (n-r)) × CodeFiberParams hr v
```

The right side is the manuscript's dependent parameter space: an internal
origin cut, a ternary selected-chain code and its placement-fibre parameter.
The actual type on the left contains an existing `Execution` exactly when
one chronological singleton-seed word produces that whole value with a
registered origin. F is fixed by the type index `arc c r`; its other fields
are the literal placement, complete origin record and full ordered chain.
No new operational state fields or admission rules are introduced.

## Maps And Inverses

| Interface | Meaning |
|---|---|
| `summaryOriginIndex_spec` | Recover the unique actual origin cut using the frozen exhaustive origin classification. |
| `summaryCode_spec` | Recover the code directly from the actual full selected records using the frozen record encoder and its actual-history converse. |
| `summaryPlacementInFibre` | Use the same actual history as a member of the recovered origin/code placement fibre. |
| `encodeSummary` | Apply the inverse placement-fibre equivalence in that recovered dependent component. |
| `decodeSummary` | Use the forward fibre equivalence to realize the tuple and retain its complete origin, chain and literal placement together. |

`decodeSummary_encodeSummary` restores every actual summary field.
`encodeSummary_decodeSummary` restores the complete dependent tuple.
The latter uses `decodeSummary_injective`: origin equality identifies the
cut, full-chain equality identifies the code, and literal placement equality
identifies the parameter in that same fibre. `actualSummary_unique_params`
packages the uniqueness statement for each actual summary.

The three `decodeSummary_origin`, `decodeSummary_chain` and
`decodeSummary_placed` projection lemmas pin the meanings of the decoded
fields. `decodeSummary_same_word` certifies one actual word realizing all
three fields and the entire decoded execution simultaneously. Both k>0
and k=0 use the already frozen placement-fibre equivalence.

## Replay

From the parent Lean directory:

```powershell
python -B summary/validate_summary.py --check-upstream-git
python -B -m unittest discover -s summary/tests -p 'test_*.py' -v
```

The validator preserves all six earlier milestone manifests, sources and
reports. It audits the new declarations and complete dependency graphs,
including the owning origin-classification graph and the chain/fibre
graphs. It checks the actual seed-history domain, the pure dependent
parameter family and the joint word certificate. Allowed axiom leaves are
`propext`, `Classical.choice` and `Quot.sound`.

This is a local companion milestone, separate from the HAL v1 proof
identity. It proves the generated-summary equivalence, not yet Theorem
6.1's binomial enumeration or the later analytic formulas. The maps are
mathematical encoders/decoders; no executable or performance claim is made.

The [dependent-summary manifest](milestones/dependent-summary-v1/manifest.json)
binds five new inputs and 30 declaration/definition axiom checks. The
[dependency report](milestones/dependent-summary-v1/dependency-audit.json)
contains 15 complete target signatures and 10,501 declaration nodes.
The owning origin and fibre proof graphs are compared exactly with their
earlier frozen graphs, including direct declaration dependencies.
