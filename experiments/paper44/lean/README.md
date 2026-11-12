# Paper 44 Lean companion

This is a separately maintained Lean companion for
**Prefix Memory and the Growth Spectrum of Event Observers**. Its
[structure-and-counting milestone v1](FINITE_COMBINATORIAL_MILESTONE.md)
was locally frozen with an exact-byte manifest before the numbered candidate;
it is now included as source in this candidate, but has no separate archive
or independent cold replay. The concrete circular observer, its structural equivalence
criterion, terminal-sector quotient, actual proper-carrier label counts,
compatible placement fibres, and the full positive-depth quotient decomposition
are proved. The later asymptotic growth and critical-window claims remain
outside Lean coverage.

The milestone freezes the finite proof/source closure, toolchain locks and
86 explicit axiom-audit outputs, including the actual quotient equivalences
and both Theorem 3.3 cardinalities. Its 102 input hashes include imported
sibling proof modules. Read-only replay is available through
`python3 -B freeze_structure_count.py`; use `--check-only` for byte checks
without rebuilding. Cache reuse is recorded separately from independent
cold-start reproduction. Future analysis belongs in a separate layer.

## Reuse boundary

The companion reuses the abstract semantic layer from
`experiments/paper40/lean/PaperXL/PrefixObserver.lean`:

- deterministic per-letter traces;
- prefix labels with `short`/`saturated` phases;
- label-update preservation and append laws;
- future-trace plus current-label observer equivalence.

These are reuse and specialization results; Paper XLIV does not reestablish
an independent abstract observer theory. `PaperXL.FixedPrefixGrowth` remains
a later reuse point for cardinality envelopes and polynomial tag bounds.

The concrete layer reuses literal `Execution`, `step` and `run` from the
fixed-pair source closure in
`../../future_event_minimal_quotient/lean/upstream/`. Those upstream files
are pinned copies of the earlier companion (see its `upstream-manifest.json`).
It imports `FutureEvent.Events` and `FutureEvent.FutureClassification` from
that companion. Their complete ordered records, null slots and all-word
classification are used unchanged. Lake compiles only the imported modules
into this project's own build tree; neither source owner is modified.
The terminal range proof also imports the frozen fixed-pair
`RegisteredAbsorptionChains.OriginClassification` from that companion's
`full_summary/owner/` tree. Its `actual_registered_origin_unique` theorem
supplies the exact ordered registration record for `n >= 3`; its source is
not copied or edited here.

## Current coverage

| Module | Checked result | Boundary |
|---|---|---|
| `ObserverSemantics` | Paper XL observer/update API specialized to this paper's notation | Semantic reuse |
| `CircularPrefixInstance` | Genuine singleton-seed state subtype, raw `p/d` step, selected output, positive-depth prefix label, `label_step`, whole-word run/trace/label correspondence | All `n >= 3`, `j >= 1` |
| `CircularPrefixClassification` | Future normal-form condition plus current-label equality; preregistration placement equality; registered nonterminal placement-and-label equality; terminal label equality | Reuses the proved future-event classification on actual reachable states |
| `CircularPrefixCounting` | Finite terminal-prefix code cardinality in Lemma 3.2's binomial form | Parameter count; transferred to actual labels below |
| `TerminalPrefixEncoding` | Increasing checkpoint/Bool parameters equivalent to sparse codes, separately for saturated and short phases | Includes both final-event port bindings |
| `TerminalDecoder` | Exact record-list length, prefix truncation, one-event full-carrier completion and terminal-checkpoint criterion | Uses the frozen ordered-record decoder and actual chain realization |
| `TerminalLabelEquiv` | `terminalPrefixActualEquiv`, actual raw-history witnesses, both inverse identities and Lemma 3.2's actual terminal-label count | All `n >= 3`, `j >= 1`; terminal physical phase is absent |
| `TerminalObserverQuotient` | Actual terminal observer classes equivalent to actual labels, with both inverse identities and the exact terminal-sector minimal quotient count | Forgets terminal physical phase |
| `ProperCarrierCompletion` | A retained complete-record prefix extends to an exact prescribed proper frontier | Completion preserves every retained ordered record |
| `ProperCarrierLabels` | Recovery and actual realization of a full-chain representative for a fixed proper carrier and retained label | Actual generated-state image |
| `ProperCarrierPrefix` | Carrier-indexed saturated/short retained-label equivalences, actual reachability, inverse identities, and the zero-absorbed boundary | Labels are kept distinct by carrier; no cross-carrier quotienting |
| `ProperCarrierFibre` | Fixed-carrier/label placement equivalence and the exact placement-fibre cardinality | Fibre parameters count literal placements, not realizing histories |
| `ProperCarrierCounting` | Dependent carrier/label classification, Lemma 3.1's positive-`r` count, the `r=0` boundary and weighted actual placement-fibre counts | Supplies the proper sector to Theorem 3.3 |
| `CircularPrefixQuotient` | Four-sector actual normal form; full-domain and registered-domain observer quotients equivalent to their actual normal forms; both inverse identities | Equivalence is noncomputable; no raw-word uniqueness claim |
| `CircularPrefixTheorem33` | Dependent regrouping by absorbed size, finiteness and both exact Theorem 3.3 cardinalities | All `n >= 3`, `j >= 1`; analytic growth is separate |

The circular instance uses `x = (P,o,A)` and `F={0,1}`. Its prefix label is
literally `origin`, `take j chain`, and the short/saturated marker.
Registration initializes an empty absorption chain. One tagged output,
including null, is retained per raw letter. The event-tag conversion is
injective, and `circular_run_eq` identifies the abstract machine run with the
literal complete execution, not just its endpoint placement.

`circular_prefix_classification` specializes the established all-word
future-event normal forms and adds label equality. It does not assume a
finite history cutoff. In particular `circular_terminal_observerEq_iff_label`
proves that physical terminal phase is forgotten by this observer.

For `N=n-2 >= 1`, `j >= 1`, `TerminalPrefixCode N j` is the disjoint sum of
saturated and short checkpoint/binding parameters. The saturated summand has
`j` selected checkpoints and `j` independent Bool bindings. A short chain of
length `ell < j` has its last checkpoint fixed at `N`; only `ell-1` earlier
checkpoints are selected. `card_terminalPrefixCode_paper` proves

```text
card (TerminalPrefixCode N j)
  = 2^j * choose N j
    + sum (ell = 1 .. j-1), 2^ell * choose (N-1) (ell-1).
```

The parameter cardinality lemmas also admit formal zero-parameter values;
only `N >= 1`, `j >= 1` have the stated terminal interpretation. They contain
no terminal site factor: physical terminal phase is not part of a retained
label. The short/saturated prefix marker, in contrast, is retained.

## Actual terminal range equivalence

`ActualTerminalLabel n j` is the image of `circularLabel j` on actual
singleton-seed generated states that are registered and rank one. It is not
defined as the image of the combinatorial decoder or as all well-formed
syntactic labels. `terminalPrefixActualEquiv` proves

```text
TerminalPrefixCode (n-2) j ≃ ActualTerminalLabel n j.
```

The proof checks both directions:

- `terminalSparseLabel_reachable` realizes each code with a genuine terminal
  execution. A saturated prefix ending before checkpoint `N` is completed
  by one final absorption; the extra record lies beyond the retained prefix.
  Short codes already end at `N`. Both final ordered port bindings are legal.
- `actual_terminal_code` recovers the exact decoded chain and unique origin
  of every actual registered terminal state.
  `take_decodeChain_in_range` recovers a sparse code for its retained records;
  `terminalSparseLabel_covers` proves that no actual terminal label is omitted.
- `terminalSparseLabel_injective` uses equality of complete ordered records,
  the decoder's injectivity and the short/saturated marker. It does not
  compare only carrier sets or checkpoint cardinalities.
- `terminalPrefix_encode_decode` and `terminalPrefix_decode_encode` prove
  the two inverse identities. `terminalPrefixActualEquiv_value` fixes the
  forward map's literal label value, while `terminalPrefix_actual_history`
  exposes actual raw-word provenance.

These are mathematical, noncomputable equivalences using `Equiv.ofBijective`.
They do not extract a canonical executable inverse or claim uniqueness of
realizing raw words. The witnesses preserve the full origin and every retained
ordered record, not terminal physical phase.

`card_actualTerminalLabel_paper` now transfers Lemma 3.2's formula to the
actual terminal-label image. Together with the existing terminal observer
equivalence criterion, these labels classify the registered terminal sector.
The proper-carrier label count and compatible placement fibres are now proved
as dependent, carrier-indexed equivalences. `CircularPrefixQuotient` assembles
the four actual normal-form sectors, and `CircularPrefixTheorem33` proves the
exact finite quotient count. The growth spectrum, Gaussian critical window and
finite generated-domain minimization remain outside current coverage.

## Actual proper-carrier labels and fibres

`ActualProperLabelsAt r j` is a dependent sum over current proper carriers
with exactly `r` absorbed outside atoms. It does not deduplicate equal
saturated label values at different carriers. For `0 < r < n-2`,
`properCarrierCountEquiv` identifies this actual image with

```text
SaturatedCarrierParams r j + TerminalShort r j.
```

For the saturated branch, a sparse prefix ending at checkpoint `b` may be
completed to `r-b+1` different current carriers. The marker `q`, with
`b <= q <= r`, stores how much of that extension is on each side. Padding
and restricting the retained code, together with recovery of this marker
from the frontier, prove both directions of `saturatedCarrierEquiv`.
For the short branch, the code already ends at checkpoint `r` and uniquely
determines its carrier. `shortCarrierEquiv` reuses the fixed-final-checkpoint
encoding while preserving its last L/R binding. Actual reachability and
recovery enter through `properCarrierPrefixActualEquiv`, not a count-only
assumption. `properCarrierCount_encode_decode` and
`properCarrierCount_decode_encode` expose the two inverse identities.

`card_actualProperLabelsAt_all` proves Lemma 3.1 for `n >= 3`, `j >= 1`,
`0 <= r < n-2`, using `properCarrierPrefixCount r j` for the coefficient:

```text
c(0,j) = 1
c(r,j) = 2^j * choose (r+1) (j+1)
         + sum (ell = 1 .. j-1), 2^ell * choose (r-1) (ell-1)   (r > 0).
```

`properPrefixPlacementEquiv` identifies each fixed compatible carrier/label
fibre with the upstream actual fixed-chain placement fibre. Its forward map
is the literal placement identity, so choices of realizing history are not
counted. `card_actualProperPlacements_paper` proves the common fibre weight
`n * choose (2*(n-2)-r) (n-2-r)`. Finally,
`card_actualProperFibreAt_all` counts carrier/label/placement triples as
`c(r,j)` times this weight, including the separate zero-absorption boundary.
Identifying their union with the full observer quotient, and adding the
unregistered and terminal sectors, is closed by the normal-form equivalence in
`CircularPrefixQuotient` and the cardinality theorem in
`CircularPrefixTheorem33`.

## Theorem 3.3: actual minimal quotient

`PrefixObserverQuotient` is the quotient of actual singleton-seed generated
states by the concrete machine's all-word `ObserverEq`. Its relation is not
defined by the proposed counting keys. `prefixObserverNormalEquiv` proves
that its classes are exactly the following disjoint actual normal forms:

- one permanently unregistrable, unregistered class;
- an actual registerable placement;
- an actually attained registered terminal prefix label;
- a proper carrier, compatible actual label and literal placement.

`unregistered_dead_state` supplies the real word `[p,d]` for the first
sector. `properObservation_covers` recovers a proper frontier from every
actual registered nonterminal history. `properCarrier_unique_of_placement`
ensures that equal placements cannot be counted again under different
carrier indices. `prefixNormalSignature_injective`, reachability and coverage
establish the normal-form equivalence, with named encode/decode identities.
The registered quotient restricts the same observer to actual registered
states and retains only the last two sectors.

`properObservationSizeEquiv` regroups the proper observations by absorbed
size, preserving all carrier, label and placement fields. Composing its
cardinality with the actual label/fibre and terminal counts gives
`paperTheorem33`:

```text
N = n-2
A = n * sum (r = 0 .. N-1), c(r,j) * choose (2*N-r) (N-r)
card PrefixObserverQuotient           = 1 + R_n + T_(N,j) + A
card RegisteredPrefixObserverQuotient = T_(N,j) + A
```

`card_prefixObserverQuotient_paper` and
`card_registeredPrefixObserverQuotient_paper` expose the two formulas
separately; `paperTheorem33_formula` expands the first in binomial notation.
These are all-parameter finite mathematical proofs for `n >= 3`, `j >= 1`.
The normal-form inverses use classical choice and do not extract an executable
minimizer. No asymptotic, spectrum or Gaussian-window result follows merely
from compiling these finite formulas.

## Checks

The project pins Lean 4.33.0 and Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d` in its Lake files. It needs the
sibling Paper XL and future-event sources from this checkout. From this
directory:

```text
lake --no-cache build
lake env lean Checks.lean
lake env lean AxiomAudit.lean
```

With an existing compatible local dependency cache, validate its pins using
`rime-lean-cache .` (and `--link` only for missing links) before building, as
described in the root `AGENTS.md`. Cache reuse is not a cold-start replay;
build output and dependency links stay under ignored `.lake/`.

`Checks.lean` includes concrete registration/empty-chain checks, null-preserving
trace length, `N=1` and above-maximum-depth actual label counts, early saturated
prefix completion, distinct final-event bindings, dependent inverse interfaces,
zero/positive-absorption counts, weighted placement-fibre counts, both total
quotient formulas and inverse identities. Concrete controls include `n=3`,
`n=5,j=2` (410 total / 334 registered) and `n=5,j=4` (414 total), where
above-maximum-depth memory still forgets terminal physical phase.
These controls supplement the all-parameter proofs; they are not an independent
transition implementation or a new exhaustive enumerator. `AxiomAudit.lean`
covers the instance, structural classification, sparse encoding, terminal-sector
quotient, actual range equivalences, full and registered quotient equivalences,
their inverse statements, and both Theorem 3.3 formulas.
Its allowed dependencies are Lean's standard `propext`,
`Classical.choice` and `Quot.sound`; no custom axioms or `sorry` declarations
are introduced. The checks do not establish the analytic growth or
critical-window claims.
