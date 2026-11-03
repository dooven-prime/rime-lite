# Actual Full-Summary Observer Bridge

This separate finite layer defines the paper's full-summary Moore contract,
classifies its actual all-word quotient and connects it to the fixed-pair
actual-summary count. It preserves the 81 frozen future-event proof inputs
and the five frozen Wallis-ratio inputs.

## Observation contract

For the fixed raw environment and selected pair `F={0,1}`, `output s` is
`none` before registration and `some s` afterwards. An `Execution` contains
the literal placement, complete origin record and ordered selected chain;
`F`, the defect letter and its ports are fixed by the environment. Thus this
is exactly the displayed `(P,F,o,A)` contract, not a projection to placement
or to future events.

`Equivalent F s t` compares outputs after every common chronological raw
word, including `[]`. It is not defined by the intended normal forms.

`event_to_summary_prefix_detection` supplies a decomposition `pre++suffix=w`
of the same word whenever its event traces differ, with unequal Moore
outputs after `pre`. Adjacent current/successor outputs determine the
selected event of that actual step. Induction composes these facts without
changing representatives. This lemma also holds on ambient executions;
the classification and count are restricted to the actual generated domain.

## Actual minimal quotient

For `n>=3`, `equivalent_iff_normalForm` proves

\[
x\equiv_{\rm full}y
\iff
\bigl(x,y\text{ are permanently unregistered}\bigr)\ \lor\ x=y.
\]

Here equality of registered executions retains every summary field, even at
rank one. Before registration, actual provenance implies an empty old chain;
distinct registerable placements are separated by the inherited actual
probe words and the event-to-summary bridge.

The null class has an explicit actual witness: rotate source atoms `1,2`
to ports `0,1` and execute `d`. The resulting `{1,2}` packet prevents any
later registration of exactly `{0,1}` by no-splitting. This witnesses the
single null class without merging any registered terminal state into it.

`fullQuotientEquivSummaries` proves

\[
\operatorname{FullQuotient}(n)\simeq
\mathbf1\ \sqcup\ \mathcal R_n\ \sqcup\
\operatorname{ActualRegisteredSummaries}(n).
\]

The quotient on the left is of actual singleton-seed generated states under
the all-word Moore equivalence. The registered summand is identified with
the count owner's type by retaining the identical execution and identical
actual seed provenance, not by equating numerical formulas.

## Exact count and observation refinement

The count bridge derives

\[
Q_n^{\rm full}=1+R_n+s_n,\qquad R_n=n\binom{2n-4}{n-3},
\]

with the inherited all-parameter registered-summary formula, `m=n-2`,

\[
s_n=n\left[\binom{2m}{m}
+2\sum_{b=0}^{m-1}3^b\binom{2m-b-1}{m-b-1}\right].
\]

`forgetToFuture` is a surjection from the actual full-summary quotient to
the actual future-event quotient. It commutes with every raw continuation;
the finite cardinality inequality follows. It is generally not injective.

## Inherited owner and proof boundary

The eight modules in `owner/RegisteredAbsorptionChains/` are exact source
copies from commit `050cf8ec11e3db263830b46ea95e4062b8e08869`. They extend,
without changing, the 38 execution/fibre modules in the frozen finite
companion. `owner-manifest.json` binds their bytes and compilation order.
This is the fixed-pair preprint's later Lean companion snapshot, not a
retroactive alteration of its HAL proof identity.

The count audit requires the actual-summary dependent equivalence and
`actual_registered_origin_unique` in the count's dependency closure. Thus
the registration origin is not omitted when passing from placement fibres
to complete registered summaries. The domain is `n>=3`; the two-origin
`n=2` boundary is not imported into this theorem.

This layer proves the observer bridge and exact finite count. The
full-summary `9/2` asymptotic and full/future quotient-ratio asymptotic
remain separate analytic obligations. The old future-event Wallis theorem
is preserved but is not used as an input to this finite bridge.

## Replay

From the parent Lean package directory, using its pinned Lean `4.33.0` and
Mathlib revision:

```powershell
python -B full_summary/validate_bridge.py --check-owner-git
python -B -m unittest discover -s full_summary/tests -p 'test_*.py' -v
```

`RIME_LAKE_EXE` can select the exact `lake.exe`. The validator verifies both
prior frozen source sets, the eight owner modules, and the local bridge
sources. It builds the finite root and the extension without changing the
finite Lake configuration. Generated `.olean` files remain under `.lake/`.
`--check-owner-git` compares the new owner bytes with `git show` at their
declared historical commit when that Git history is available.

The local milestone is in `milestones/full-summary-v1/manifest.json` with a
complete declaration-dependency report. Its five main targets include the
actual-summary quotient equivalence definition. All bridge theorems and
four semantic equivalence/projection definitions have explicit axiom
checks. The audit rejects a missing Moore contract, missing origin
classification, discarded registered terminal states, analytic inputs or
nonstandard axiom assumptions.

`--freeze` creates an absent local milestone once; ordinary replay is
read-only apart from build products. This uses pinned local dependency
caches, not a claimed fresh-machine cold replay. Normal-form equivalences
remain mathematical noncomputable objects, not an extracted minimizer.
