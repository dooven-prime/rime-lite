# Future-Event Quotient: Separate Lean Companion

This development companion targets the definitions and proofs of
[hal-05844771v1](https://hal.science/hal-05844771v1). It is separate from
the HAL v1 proof identity and from the frozen Python control package in the
parent directory. It does not modify either deposit or its fixed bytes.

The [theorem-to-source review map](review/THEOREM_TO_SOURCE.md) connects the
paper statements to four frozen proof layers, gives the four final target
signatures, and records source hashes, dependency graphs and replay commands.
Its [machine-readable map](review/theorem-map.v1.json) is checked with
`python -B review/build_theorem_map.py`. A public version identity for the
complete companion remains pending, separately from both HAL paper identities.

## Reused execution semantics

The thirty-eight modules in `upstream/RegisteredAbsorptionChains/` are exact copies
from commit `050cf8ec11e3db263830b46ea95e4062b8e08869`, a later Lean companion
to the fixed-pair counting preprint. Their hashes and original paths are
recorded in `upstream-manifest.json`. They are not newly proved results of
this companion.

| Reusable layer | Use here |
|---|---|
| `Letter`, `Execution`, `step`, `run` | Literal chronological raw `p,d` execution, origin and selected-chain updates. |
| `placementOfMap`, `forwardMapRun`, `run_placementOfMap` | Actual atomwise execution, including collisions. |
| Source-order lift and no-splitting | Source-order and persistent atom equality for later probe admission. |
| Fusion-free routing and phase control | Actual hole moves, outside assembly and final placement adjustment. |
| Clean code witnesses and fixed-chain placement classification | Reused for the registered-placement parameter equivalence, independently of the completed behavioral classification. |
| Old total-summary counting theorems | Not imported into the frozen future-event root; its region counts use their own parameter equivalences. The separate full-summary extension below imports the pinned count owner. |

The fixed raw environment supplies the letter `d`, ordered ports `(0,1)`
and target `0`; a `FusionRecord` stores its ordered parent blocks and their
union. No variable port or event-coordinate field is being forgotten.

The interpreter, atomwise action, source-order lemmas and registered
same-placement trace theorem accept an arbitrary selected finite set `F`.
The gap-registration theorem here specializes to `F={0,1}`. A later
proper-arc companion can reuse the former layer, but its origin cuts,
chain decoder and dependent counting equivalence require their own proofs;
the fixed-pair counting classification is not imported by changing `F`.

## Current proof scope

- `Atomwise.lean` connects the inherited actual interpreter to a chronological
  site word and proves that its final atom sites determine the literal placed
  partition, also through fused steps (Lemma 5.1). Final injectivity on the
  initially occupied sites rules out every intermediate new fusion.
- `Events.lean` defines new registration/absorption outputs independently of
  the retained old chain, proves trace concatenation and right congruence,
  and proves that registered states with the same placement have identical
  future event traces. Registered placement separation is proved separately
  in the sweep modules below.
- `GapProbe.lean` computes the actual `dp`-block site map and the pre-final
  gap-probe map, including its singleton port-zero fiber, interval port-one
  fiber, and injectivity away from port one.
- `GapRegistration.lean` uses the initial singleton-fiber and empty-open-gap
  premises to prove that one actual probe has null output before its last
  letter, then creates exactly the ordered singleton registration. The same
  prefix is fusion-free at every intermediate predecessor. Its raw length is
  at most `3*n-6` when `n>=3` and `1<=g<=n-2`.
- `RegistrationDomain.lean` defines `PairGenerated` by an actual singleton-seed
  history and `PairRegisterable` by the existence of a future word that sets
  the previously absent origin. A genuine registration has singleton parents;
  no-splitting pulls that necessary condition backwards through any prefix.
- `GapAdmission.lean` proves the converse on the generated domain and derives
  the probe's admission premises from source order. It proves the unregistered
  source criterion of Lemma 3.2 and supplies Lemma 5.2's actual first-registration
  word for every generated registerable state, including its fusion-free prefix
  and the `3*n-6` suffix-length bound.
- `HoleMove.lean` realizes every `x^(h)` by the literal descending local words.
  Each step sees an actual hole and reaches the exact next atom map, with
  origin and chain unchanged. Every intermediate letter is fusion-free.
- `ProbeCoalescence.lean` proves Lemma 5.3 on actual generated registerable
  states, with a unique parameter `1<=h<=g`. The complete terminal event
  recovers both ordered singleton parents; the nonzero probe fibers recover
  each outside atom, including atoms already sharing an outside packet.
- `SweepSites.lean` computes the actual `pd` and sweep site maps. Before
  the defect in pair `k+1`, port zero has the single initial-site preimage
  `-(k+1)` for `k+2<n`, even when earlier selected events occurred. A full
  aligned sweep sends every initial site to zero; `|W_q|<=3*n-4`.
- `SweepReconstruction.lean` reverses an actual defect from its selected
  output and endpoint when its carrier port is known. It covers empty ports,
  including the null-output move from port one into an empty port zero.
  Induction then proves aligned sweep injectivity (Lemma 4.1).
- `RegisteredDomain.lean` proves that registration in an actual generated
  state puts source atoms `0,1` in the same current packet. The sweep callers
  do not assume this property merely from an arbitrary `isSome` field.
- `SweepSeparation.lean` proves the orientation/slot decoders, outside-anchored
  phase recovery and registered placement separation (Lemmas 4.2--4.3 and
  Corollary 4.4). The outside-anchor premise belongs only to the first state;
  the comparison state need not have the same packet, or any packet, there.
- `TwoProbeSeparation.lean` combines the smaller-gap probe with a sweep of
  the actual registered successors, proving a `6*n-10` distinguishing bound
  for two distinct generated registerable states.
- `SilentRegion.lean` proves that unregistered states unable to register and
  registered one-packet states emit null on every future word. The latter
  remain one-packet states under every actual continuation. It also proves
  that an already registered state never emits a new registration tag.
- `CrossRegionSeparation.lean` supplies nonnull actual probes for both active
  regions and distinguishes each pair of different regions. It proves that
  the structural silent region is exactly the all-future-null region, and
  gives its equivalent current-source-fiber test on generated states.
- `FutureClassification.lean` proves equation (6.1)'s complete behavioral
  classification, right congruence of its normal forms, the all-region
  `6*n-10` distinguishing bound, and the corresponding finite-length test
  for equivalence.
- `FutureQuotient.lean` forms the all-word future-equivalence quotient of
  actual generated states and proves its equivalence to the finite tagged
  normal-form space. Actual raw continuations descend to this quotient and
  preserve chronological concatenation. An explicit seed sweep realizes
  its silent key.
- `QuotientCardinality.lean` proves that actual registerable states and their
  literal placements are in bijection, then derives the structural count
  `Q_future = 1 + R + A` with the paper's state/placement conventions.
- `PlacementParameters.lean` defines the two finite combinatorial input
  types, without any reachability fields. `PlacementSums.lean` proves their
  Vandermonde and weighted hockey-stick evaluations.
- `RegisterablePlacementEquiv.lean` identifies registerable parameters with
  actual generated registerable placements. `IntervalAssembly.lean` and
  `ZeroCarrierAssembly.lean` supply literal outside-assembly words and
  fusion-free final adjustment; the singleton normal-form modules recover
  source cuts and physical sites in the reverse direction.
- `RegisteredPlacementEquiv.lean` independently identifies the carrier-choice
  and fibre parameters with actual registered nonterminal placements. Its
  forward construction reuses actual clean-code/fibre words, and its reverse
  construction recovers the actual carrier and unique rank parameters.
- `ClosedQuotientCount.lean` transfers both parameter cardinalities to the
  actual regions and hence to the all-word future-equivalence quotient.

The domain criterion is not defined by the desired source shape:

```text
PairGenerated(s)    := exists history, run(seed, history) = s
PairRegisterable(s) := origin(s) = none and exists w, origin(run(s,w)).isSome
```

For `n>=3`, an actual unregistered generated state is `PairRegisterable` if
and only if the source fibers containing atoms `0` and `1` are singletons.
The monotone degree-one source lift then proves that their forward physical
gap is empty and has length between `1` and `n-2`. Consequently callers of
`generated_registerable_probe` do not supply separate singleton or gap
assumptions. Outside packets may already be fused; no `CleanOutside` premise
is used. The suffix bound starts at this current state, not at the seed.

## Exact coalescence surface

`ProbeCoalesce x y word` means equality of the complete selected-event
traces AND equality of the literal terminal placements under that SAME word.
For `n>=3`, two generated semantically registerable states, and atom maps
encoding their actual placements, `gapProbe_coalesces_iff_holeMove` proves:

```text
ProbeCoalesce(x,y,V_x) <-> exists unique h,
  1 <= h <= g(x) and y = holeMoveExecution(x,h).
```

`holeMoveExecution` changes only the site of source singleton `{1}`, to
`site_x(0)+h`. It retains all other atom sites and the original origin/chain.
Its actual witness is `backShiftWord b (g-h)`, recursively appending
`localLetters (b-(k+1))`; all coordinates are in `ZMod n`, including wraps
across zero. `holeMove_actual_word`, `holeMove_generated` and
`holeMove_registerable` prove that every parameter gives a real comparison
state in the same generated registerable domain, not merely a formal map.

The converse construction proves equality of the full terminal executions
(`holeMove_probe_same_run`), stronger than the endpoint-placement clause.
`h=g` is exactly the identity state and uses the empty move word. For distinct
coalescing states, `probe_coalescence_strict_gap` proves `g(y)<g(x)` from this
same classification.

## Registered sweep and two-probe surface

For `n>=3`, `registered_sweep_separation` separates different literal
placements of actual generated registered states, provided the first state
has an outside atom. It returns one common actual `W_q` and the bound
`|W_q|<=3*n-4`. The comparison state is not required to have a matching
outside anchor. The lower-level aligned theorem also accepts arbitrary
selected `F` with an explicit common carrier site.

The phase decoder is slightly stronger than the required first-event
implication: any selected output with atom `0` as a left parent at the
specified later defect determines its initial site from the singleton
port-zero fiber. It does not assume that earlier outputs were null.

`registerable_pair_separation` proves, for two DISTINCT generated
semantically registerable states, that a common suffix of length at most
`6*n-10` distinguishes their traces. The construction uses the smaller-gap
state's `V` probe. If probe traces agree, strict gap descent excludes equal
terminal placements. Both actual endpoints are registered and the first is
nonterminal, so registered separation supplies the final `W` sweep.

## Complete future-event behavioral classification

For `n>=3` and `PairGenerated x`, `PairGenerated y`,
`futureEquivalent_iff_normalForm` proves exactly these alternatives:

```text
FutureEquivalent(x,y) <->
  (SilentRegion(x) and SilentRegion(y)) or
  (PairRegisterable(x) and PairRegisterable(y) and x.placed = y.placed) or
  (RegisteredNonterminal(x) and RegisteredNonterminal(y) and x.placed = y.placed).
```

`RankOnePlacement` means that the literal placement is the source-fiber
placement of a constant atom map: all source atoms form one packet at one
site. `RegisteredNonterminal` means a registered origin and a non-rank-one
placement. The semantic registerability definition is unchanged.
`silentRegion_iff_currentShape` makes the silent test local on the generated
domain: an unregistered state is silent exactly when the two selected atoms
are not separate singleton fibers; a registered state is silent exactly
when its atom map is constant.

`future_inequivalence_uniform_separation` extends the distinguishing bound
to EVERY inequivalent generated pair, including comparisons across regions.
`bounded_traces_iff_futureEquivalent` proves that agreement on all words of
length at most `6*n-10` is equivalent to agreement on all future words.
No word-length cutoff is used to define the generated domain or to prove
the classification.

This completes the behavioral classification in Theorem 1 and the uniform
length statement in Theorem 2. The following equivalence and structural count
also formalize Theorem 1's `1+R+A` consequence. The parameter equivalences
and closed binomial count below complete its numerical evaluation. The
full-summary observation contract, prefix-detection bridge and exact count
are provided by the separate full-summary companion below. The future-event
asymptotic ratio is provided by the separate analytic companion. Full-summary
and full/future-ratio asymptotics remain distinct analytic obligations.

## Actual quotient and structural count

`GeneratedState n` is the subtype of full executions with an actual
singleton-seed history. `FutureQuotient n` is its quotient by equality of
ALL future selected-event traces, not a quotient defined by the proposed
normal forms. `futureQuotientEquivNormalForms` proves, for `n>=3`,

\[
  \mathrm{FutureQuotient}(n)\simeq
  \mathbf 1\;\sqcup\;
  \mathrm{RegisterablePlacements}(n)\;\sqcup\;
  \mathrm{RegisteredNonterminalPlacements}(n).
\]

Both placement types retain an existential actual-history witness in their
defining subtype. They are not arbitrary ambient placed partitions.
Surjectivity onto the silent summand is justified by `seed_sweep_silent`:
the actual word `sweepCore (n-2)` from the seed reaches a one-packet silent
state. Thus the single silent class is nonempty, not merely a formal tag.

`finite_futureQuotient` proves finiteness via this equivalence and the
finite ambient placement type. It does not assume a history cutoff or
need a finiteness theorem about the whole raw execution space.
`quotientRun_mk`, `quotientRun_append` and `quotientNormalKey_run_mk` keep
the quotient continuation attached to the actual chronological `run`.

For the paper's `R_n`, which counts actual registerable states,
`registerableStatesEquivPlacements` proves that forgetting to placement is
a bijection: every generated unregistered execution has no origin and an
empty old selected chain. In contrast, `A_n` deliberately counts literal
registered nonterminal placements, not distinct registered histories.
`card_futureQuotient_actual_regions` consequently proves

\[
  |\mathrm{FutureQuotient}(n)|=
  1+|\mathrm{RegisterableGeneratedStates}(n)|+
    |\mathrm{RegisteredNonterminalPlacements}(n)|.
\]

## Actual placement parameter equivalences and closed count

For `n>=3`, `registerablePlacementParamsEquiv` proves

\[
\mathcal R_n\simeq\bigsqcup_{t=1}^{n-2}
\bigl(\operatorname{Fin}(n)\times
\operatorname{Select}(n-3,t-1)\times
\operatorname{Select}(n-1,t+1)\bigr).
\]

The first two source atoms remain distinct singleton packets. The other
atoms are cut into nonempty consecutive blocks. Actual outside-only words
assemble those blocks from the singleton seed; actual fusion-free routing
then realizes every phase and occupied-site choice. The inverse is obtained
from the source-key naming of the actual placed partition. The intermediate
`InitialCutSelect` encoding simply fixes the cut separating singleton `{1}`
from the remaining outside blocks; `initialCutEquiv` removes that forced cut.

Independently, `registeredPlacementParamsEquiv` proves

\[
\mathcal A_n\simeq\bigsqcup_{k=1}^{n-2}
\bigl(\operatorname{Fin}(n-1-k)\times\operatorname{FiberParams}(n,k)\bigr).
\]

The carrier index fixes its literal source arc, not just its size. The
forward direction constructs a code with those boundaries and invokes its
actual fixed-chain placement witness. The reverse direction extracts an
actual chain code and the inherited fixed-chain normal form. Recovering
carrier boundaries, source cuts and physical sites proves injectivity.
Different origins and old chains are intentionally not counted in this
placement type.

The parameter counts and binomial identities give

\[
R_n=n\binom{2n-4}{n-3},\qquad
A_n=n\sum_{k=1}^{n-2}(n-1-k)\binom{n+k-2}{k}
=2(2n-3)\binom{2n-4}{n-2}-n(n-1).
\]

`card_futureQuotient_closed` consequently proves, for the quotient defined
by agreement on all future event traces of actual generated states,

\[
|\operatorname{FutureQuotient}(n)|=
1+n\binom{2n-4}{n-3}
+2(2n-3)\binom{2n-4}{n-2}-n(n-1).
\]

The corresponding additive theorem proves the subtraction is legitimate
over natural numbers. These are all-parameter Lean proofs, not conclusions
from the finite control tables. The finite root does not import the analytic
companion.

`futureNormalKey` and the parameter equivalences use classical choice and
are noncomputable mathematical equivalences. They are not an extracted
efficient normalization or minimization algorithm. Paper XL's executable
checker instead checks a supplied candidate against a consumer's R/G/T
requirements; this companion proves the particular coarsest behavioral
quotient for the declared future-event observation contract.

## Separate analytic milestone

The [Wallis analytic companion](analysis/README.md) proves the central-binomial
limit and normalized remainder independently of the finite model. Its final
bridge consumes the closed cardinality and proves

\[
\lim_{m\to\infty}
\frac{|\operatorname{FutureQuotient}(m+3)|}
{\sqrt{m+3}\,4^{m+3}}=\frac5{16\sqrt\pi}.
\]

The shift `n=m+3` ranges over every legal horizon and introduces no artificial
zero-size count. The analytic milestone binds five additional source inputs
and the existing finite milestone separately; none of the 81 frozen finite
inputs is changed or widened. Run its own validation entry point:

```powershell
python -B analysis/validate_analysis.py
```

## Full-summary observer bridge

The separate [full-summary companion](full_summary/README.md) defines the
Moore output as absent before registration and the complete execution
summary afterwards, including at rank one. Equality is tested after every
common word, including the empty word. It proves the actual quotient
equivalence

\[
\operatorname{FullQuotient}(n)\simeq
\mathbf1\sqcup\operatorname{RegisterablePlacements}(n)
\sqcup\operatorname{ActualRegisteredSummaries}(n)
\]

and the exact count `Q_full=1+R_n+s_n` for `n>=3`. An identity-on-executions
bridge connects the registered summand to the pinned fixed-pair count owner;
origin classification remains in that count's dependency closure.

The canonical surjection to `FutureQuotient` commutes with actual raw-word
continuations. The permanently unregistered class has an explicit actual
wrong-pair-fusion witness and does not include registered terminal states.

Eight additional pinned owner modules and the observer/count proofs are
owned by this extension, not added to either earlier frozen milestone.
Its independent replay entry point is

```powershell
python -B full_summary/validate_bridge.py --check-owner-git
```

Neither the full-summary `9/2` growth nor the quotient-size ratio is claimed
by this finite bridge.

## Observer-growth comparison

The separate [comparison companion](comparison/README.md) consumes those
three frozen layers. It proves the negative-binomial tail bound for the
fixed-pair summary count and then the limits for the two actual quotients:

\[
\frac{Q_n^{\rm full}}{n(9/2)^n}\longrightarrow\frac4{81},
\qquad
\frac{Q_n^{\rm full}/Q_n^{\rm future}}{\sqrt n(9/8)^n}
\longrightarrow\frac{64\sqrt\pi}{405}.
\]

The quotient-size ratio tends to positive infinity. The comparison has its
own source manifest, dependency graph, theorem audit and replay command:

```powershell
python -B comparison/validate_comparison.py
```

It leaves the finite, Wallis and full-summary bridge milestones unchanged
and does not change the HAL v1 proof identity.

## Semantic anchors

The finite classification and closed-count spine has a separate
[exact-byte milestone](FINITE_COMBINATORIAL_MILESTONE.md). Its five explicit
target audits include the two equivalence definitions, in addition to the
package-wide theorem audit. The frozen record excludes the analytic
asymptotic layer and can be replayed with `python -B freeze_finite_milestone.py`.

The source hashes for `RegistrationDomain.lean` (`PairGenerated` and
`PairRegisterable`) and `Events.lean` (`selectedOutput` and `eventTrace`) are
unchanged from the exact-coalescence milestone. The manifest binds those
whole files, as well as the interpreter's pinned upstream `Execution.lean`.
All finite-spine theorems are separately listed in `AxiomAudit.lean`; in
particular it retains `generated_registerable_iff_singletons`,
`holeMove_actual_word`, `gapProbe_coalesces_iff_holeMove` and
`probe_coalescence_strict_gap`. Changing the semantics requires an explicit
source rebind, not merely rebuilding the downstream theorem names.

## Build and audit

Use the exact Lean toolchain in `lean-toolchain` (Lean 4.33.0); `lakefile.toml`
and `lake-manifest.json` pin Mathlib and its dependencies. From this directory:

```powershell
lake --no-cache build
lake env lean FutureEvent/AxiomAudit.lean
python -B validate_companion.py
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

`--no-cache` avoids Lake's optional package build-archive download; it does
not bypass Lean elaboration or the normal dependency cache. A fresh machine
must still obtain the pinned Mathlib dependencies and their compiled cache.
The `.lake/` tree is local build data and is not part of the source closure.

The validator is read-only: it verifies the mirrored owner bytes and the
development source inventory, then builds and audits the listed declarations.
`--check-upstream-git` additionally checks the mirror against `git show` at
the pinned owner commit when that Git history is available locally.
Source token lint masks nested comments and strings; kernel-axiom checks
independently reject unfinished proofs or nonstandard theorem dependencies.
