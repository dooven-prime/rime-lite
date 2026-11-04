# Proper-Arc Lean Theorem-To-Source Map

This map connects the proper-arc paper's closed finite classification and
enumeration statements to their owning Lean declarations and frozen audit
closures. Mathematical ownership remains with
[hal-05848115v1](https://hal.science/hal-05848115v1);
the companion supplies the separate formal proof artifacts below.

## Scope And Proof Spine

The domain is `c : ZMod n`, `2<=r<n` (hence n>=3), the identity singleton
seed, the fixed proper source arc `arc c r`, and chronological actual `p,d`
words with no length cutoff. Write `m=n-r` and let k be the decoded number
of outside source atoms. Origins and selected chains retain ordered source
parent blocks; placements are literal generated packet placements.

$$
\boxed{\begin{gathered}
\text{Actual origin classification}\\
\Downarrow\\
\text{Actual chain equivalence}\\
\Downarrow\\
\text{Actual placement fibres}\\
\Downarrow\\
\text{Actual summary equivalence}\\
\Downarrow\\
\text{Exact and refined counts}
\end{gathered}}
$$

This is the assembly sequence, not an assertion that every preceding
interface is a proof dependency of every later one. In particular, the
fixed-origin chain construction consumes the explicit origin construction;
origin exhaustiveness is separately needed to recover the origin component
of arbitrary actual summaries. The declaration dependencies below are read
from the frozen proof graphs, not inferred from file imports.

## Theorem-To-Source Table

Each row is kernel-checked in its owning local freeze. The actual-history
types are not replaced by formal decoder images in the counting statements.

| ID | Paper statement and closed contract | Owning Lean source | Freeze |
|---|---|---|---|
| O1 | Proposition 3.1, constructive direction. Each legal internal cut has an explicit actual word, its complete origin and the cut-independent boundary placement. | [`ProperArc.run_originWord`](ProperArc/OriginBoundary.lean#L192) | M1 |
| O2 | Proposition 3.1, exhaustive direction. Every actual registered history has exactly one legal internal origin cut; no clean-state premise. | [`ProperArc.actual_registered_origin_unique`](classification/OriginExhaustive.lean#L69) | M3 |
| O3 | Proposition 3.1, actual origin equivalence. Actual registration origins are equivalent to Fin (r-1). | [`ProperArc.actualRegistrationOriginsEquivCuts`](classification/OriginExhaustive.lean#L113) | M3 |
| C1 | Lemma 4.1 / Theorem 4.2, construction. Every code at every origin has one actual clean word realizing the full selected records. | [`ProperArc.Chains.realize_clean_code`](chains/CleanRealization.lean#L83) | M4 |
| C2 | Theorem 4.2, actual chain equivalence. Actual fixed-origin selected chains are equivalent to Code (n-r), including arbitrary nonclean histories. | [`ProperArc.Chains.actualSelectedChainsEquivCode`](converse/ActualChainConverse.lean#L116) | M5 |
| C3 | Theorem 4.2, total chain count. The actual fixed-origin selected-chain set has cardinality 3^(n-r). | [`ProperArc.Chains.card_actualSelectedChains`](converse/ActualChainConverse.lean#L137) | M5 |
| F1 | Theorem 5.2, positive-complement fibre. Native cut/site parameters and actual fixed-origin/code placements are equivalent for k>0. | [`ProperArc.Chains.positivePlacementFibreEquiv`](fibres/PlacementEquivalence.lean#L57) | M6 |
| F0 | Theorem 5.2, full-carrier fibre. For k=0 the actual fixed-origin/code placement fibre is independently equivalent to ZMod n. | [`ProperArc.Chains.fullPlacementFibreEquiv`](fibres/PlacementEquivalence.lean#L80) | M6 |
| F2 | Theorem 5.2, uniform fibre interface. CodeFiberParams uses a separate full-carrier branch and is equivalent to actual placements. | [`ProperArc.Chains.codePlacementFibreEquiv`](fibres/PlacementEquivalence.lean#L108) | M6 |
| F3 | Theorem 5.2, exact fibre cardinality. The actual fixed-origin/code placement count is n * choose(n+k-2,k), including k=0. | [`ProperArc.Chains.card_actualCodePlacements`](fibres/PlacementEquivalence.lean#L116) | M6 |
| S1 | Theorem 5.3, dependent equivalence. Actual registered summaries are equivalent to the pure dependent origin/code/fibre parameter sum. | [`ProperArc.Chains.actualRegisteredSummariesEquivParams`](summary/SummaryEquivalence.lean#L56) | M7 |
| S2 | Theorem 5.3, same-word certificate. One actual singleton-seed word jointly realizes the decoded origin, full chain and literal placement. | [`ProperArc.Chains.decodeSummary_same_word`](summary/SummaryEquivalence.lean#L80) | M7 |
| N1 | Theorem 6.1 / equation (6.1). The exact binomial total counts ActualRegisteredSummaries c r, not an assumed formal image. | [`ProperArc.Chains.card_actual_registered_summaries`](counting/SummaryCardinality.lean#L74) | M8 |
| N2 | Section 6, shortest-complement boundary. For n>=3 and r=n-1 the actual summary count is (n-2)*n*(n+1). | [`ProperArc.Chains.card_actual_registered_summaries_short_complement`](counting/SummaryCardinality.lean#L86) | M8 |
| R1 | Theorem 4.2, absorption-length refinement. Actual fixed-origin chains with j records are counted by choose(n-r,j)*2^j for every natural j. | [`ProperArc.Chains.card_actualSelectedChains_length`](refinements/ChainLength.lean#L113) | M9 |
| R2 | Theorem 5.2 / equation (5.4), rank refinement. Actual rank-s placements number s*choose(k-1,s-2)*choose(n,s) for k>0 and 2<=s<=k+1. | [`ProperArc.Chains.card_actualRankCodePlacements`](refinements/RankFibre.lean#L83) | M9 |
| R0 | Theorem 5.2, rank-one boundary. The k=0 actual rank-one placement fibre has exactly n phases. | [`ProperArc.Chains.card_actualFullRankCodePlacements`](refinements/RankFibre.lean#L125) | M9 |

M2 is a thin named-interface freeze rather than another classification
theorem. M4's clean witnesses are used for construction; the converse
classifications and actual-set equivalences do not assume cleanliness.

## Actual Declaration Dependencies

A table edge omits intervening helpers but is verified by the complete
transitive declaration closure. Nearest mapped inputs are the transitive
reduction among the selected rows, not the raw direct Lean dependencies.

| Target | Nearest mapped inputs | Closure nodes | Actual axiom leaves |
|---|---|---:|---|
| O1 | (no other mapped target) | 5,323 | `propext`, `Classical.choice`, `Quot.sound` |
| O2 | (no other mapped target) | 6,022 | `propext`, `Classical.choice`, `Quot.sound` |
| O3 | O1 | 6,501 | `propext`, `Classical.choice`, `Quot.sound` |
| C1 | O1 | 9,185 | `propext`, `Classical.choice`, `Quot.sound` |
| C2 | C1 | 9,649 | `propext`, `Classical.choice`, `Quot.sound` |
| C3 | C2 | 11,092 | `propext`, `Classical.choice`, `Quot.sound` |
| F1 | O1 | 10,349 | `propext`, `Classical.choice`, `Quot.sound` |
| F0 | C1 | 9,673 | `propext`, `Classical.choice`, `Quot.sound` |
| F2 | F1, F0 | 10,408 | `propext`, `Classical.choice`, `Quot.sound` |
| F3 | F2 | 12,721 | `propext`, `Classical.choice`, `Quot.sound` |
| S1 | O2, F2 | 10,496 | `propext`, `Classical.choice`, `Quot.sound` |
| S2 | F2 | 10,418 | `propext`, `Classical.choice`, `Quot.sound` |
| N1 | F3, S1 | 13,345 | `propext`, `Classical.choice`, `Quot.sound` |
| N2 | N1 | 13,359 | `propext`, `Classical.choice`, `Quot.sound` |
| R1 | C2 | 11,364 | `propext`, `Classical.choice`, `Quot.sound` |
| R2 | F1 | 11,799 | `propext`, `Classical.choice`, `Quot.sound` |
| R0 | F0 | 10,976 | `propext`, `Classical.choice`, `Quot.sound` |

A later stage can use the underlying converse/helper interface without
using the earlier packaged equivalence as a declaration. For example, S1
uses `actual_chain_decode_encode` through its summary-code readback, while
the F1 inverse uses `actual_fiber_params`. Their full helper dependencies
remain in the owning reports even when C2 is absent from a mapped-input row.

The two M9 refinements are independent of one another and of N1.
R1 restricts the actual chain equivalence by literal record length; R2
restricts the positive fibre equivalence by the literal placement's packet
count. R0 uses the independent full-carrier phase equivalence. The k=0
fibre is not replaced by the empty positive-complement sigma type.

Full dependency-name lists and per-theorem closure graph hashes are in
[`theorem-to-source-map.v1.json`](theorem-to-source-map.v1.json). Each
owning report stores every node's kind and direct declaration dependencies.
The graph hashes cover canonical sorted node records; exact Lean source
bytes are separately bound by the source hashes. A graph hash alone is not
a hash of a compiled proof term.

## Frozen Versions And Audit Results

- Lean executable: `Lean (version 4.33.0, x86_64-w64-windows-gnu, commit d8b18978322de05a8f3dba51ef03cf5461676c17, Release)`.
- Mathlib commit: `db584cd6d46c92f209a44c0f1c829460d327499d`.
- Paper source tag: `proper-arc-summaries-source-v1.0`.
- Paper content commit: `2a30449b9dc37a36b25b277ebc006515c2addb59`.
- [Pinned manuscript](reference/proper-arc-hal-v1.md) SHA-256: `057beff05b4a5fb94f3e857298e23b0f5119b3d33fc1e4e6b4dedeb0c08eda48`.
- Generic `RegisteredAbsorptionChains` source: `547848ce2305daf54f0e2df049a9d5372ffdcbdc`;
  underlying fixed-pair source: `050cf8ec11e3db263830b46ea95e4062b8e08869`.
  These are owners of reused interpreter, source-order, placement and pure
  parameter machinery, not substitutes for the proper-arc actual-set proofs.

| Freeze | Scope | Bound inputs | Axiom queries | Targets | Graph nodes |
|---|---|---:|---:|---:|---:|
| [M1](milestones/origin-realization-v1/manifest.json) | Origin construction | 52 | 26 | 4 | 5,329 |
| [M2](interfaces/milestones/origin-interfaces-v1/manifest.json) | Named origin interfaces | 4 | 5 | 4 | 5,334 |
| [M3](classification/milestones/origin-classification-v1/manifest.json) | Exhaustive origin classification | 6 | 23 | 9 | 8,268 |
| [M4](chains/milestones/chain-construction-v1/manifest.json) | Actual clean chain construction | 8 | 34 | 11 | 9,420 |
| [M5](converse/milestones/actual-chain-equivalence-v1/manifest.json) | Actual chain equivalence | 7 | 34 | 15 | 11,160 |
| [M6](fibres/milestones/placement-fibre-v1/manifest.json) | Actual placement fibres | 7 | 32 | 15 | 12,761 |
| [M7](summary/milestones/dependent-summary-v1/manifest.json) | Actual dependent summaries | 5 | 30 | 15 | 10,501 |
| [M8](counting/milestones/summary-count-v1/manifest.json) | Exact actual-summary count | 5 | 17 | 12 | 13,382 |
| [M9](refinements/milestones/combinatorial-refinements-v1/manifest.json) | Independent combinatorial refinements | 5 | 28 | 16 | 12,215 |

| Freeze | Manifest SHA-256 | Dependency report SHA-256 |
|---|---|---|
| M1 | `56769c0fa07686e5431de1f2b667eea8bd46619c979d1fe5d4e308e7c6d00c96` | [`05713260569b9f95eb4d68922633c4680417953b47b751ec69a1912335ac3bc1`](milestones/origin-realization-v1/dependency-audit.json) |
| M2 | `c3725a2407c2af450ad9c095abcbca89ba5cad13f1331d008c05e7134a2202f8` | [`b106edddeb9e6b98a8139a743f727f4c1ff8779a089335633f0056bae5134add`](interfaces/milestones/origin-interfaces-v1/dependency-audit.json) |
| M3 | `cf0bc343a73e7466b870c36843e072472159779373ad3e85964d17e69acea2d0` | [`dac7179c99634005d50019e73730c8fee62346d4b69c98bd24e4ee57b5bd479a`](classification/milestones/origin-classification-v1/dependency-audit.json) |
| M4 | `5979c315a7a8f534efeb29948cb0f4f8ed151c99a7e06cd6059f3bf58aa9e5fd` | [`f237046fb6eef5fde362efb825a435f3ac48e1bd88007a958ff8d090b7444d94`](chains/milestones/chain-construction-v1/dependency-audit.json) |
| M5 | `3dac55c745d644ebb80565fdeb749b411f0ca7e18e0a9c35d4d7b1fc2ee3a731` | [`0e8dfdd89a0bbc3f187477a7060be52663fae5e686a1285ac4bb1446c407b571`](converse/milestones/actual-chain-equivalence-v1/dependency-audit.json) |
| M6 | `7d85df042a583508908a028e98499b52e7e8d7507d23d5c70f6e210faa21658d` | [`e9b56f6fb1cbe661dc0f8da7fdd0412f8063d063b44fe1479921f47ba72f269a`](fibres/milestones/placement-fibre-v1/dependency-audit.json) |
| M7 | `aef536f33efdd1b114e87f9b96ffdce1ddceec94c9a41d10b572f092a38b95a6` | [`6643c334c4bf6f70b7d02ea47ba19be6ffd34eafc77c5e770ea0aadca7fc42e1`](summary/milestones/dependent-summary-v1/dependency-audit.json) |
| M8 | `6535bd701625f294302f4ecadbb686a1a04cd22e9a6c110fe4d050619aa531ba` | [`df38f0a016ca2f0191d84f37f76b9030a6c390b5583fe3ad073ce1f579372454`](counting/milestones/summary-count-v1/dependency-audit.json) |
| M9 | `54ac894b75ab88a1eb66058f5bdb6b90d6ced237b3d8c104099777188d1febec` | [`9a039472f4f2cb29ce687359569b98c09be31c3cbb1700c7c7f79ed8d97abb13`](refinements/milestones/combinatorial-refinements-v1/dependency-audit.json) |

Together these freezes bind 99 distinct input files.
Their compatible declaration graphs have 13,621 distinct nodes.
The union graph counts all audited declarations in the nine frozen reports, not merely the union of the 17 selected theorem closures.
Per-freeze query and node counts overlap and must not be added as independent
proof totals. Every recorded target closure was checked for missing nodes
and axiom leaves; only `propext`, `Classical.choice` and `Quot.sound` occur.

These are local companion freeze identities. No separate public companion
tag or deposit is assigned by this map, and the paper's HAL v1 proof identity
is unchanged. The upstream archive URL is provenance metadata; downloaded
archive file bytes were not verified here. The recorded kernel replays use
pinned cached dependencies, not a fresh-machine cold replay.

## Reproduction

From this Lean directory, the following read-only command checks all nine
manifest/report identities, every bound source, all reported target closures
and axiom sets, and the deterministic map outputs:

```powershell
python -B theorem_map.py --check-upstream-git
python -B -m unittest discover -s map_tests -p 'test_*.py' -v
```

It checks frozen evidence; it does not execute the Lean kernel anew. A
standalone source copy can omit `--check-upstream-git`; that option additionally
compares reused inputs and the manuscript with local historical Git objects.

For a fresh local kernel replay use the pinned Lean/Mathlib versions and
the owning validator for the desired freeze (no `--freeze` option):

```powershell
python -B validate_companion.py
python -B interfaces/validate_interfaces.py
python -B classification/validate_classification.py
python -B chains/validate_chains.py
python -B converse/validate_converse.py
python -B fibres/validate_fibres.py
python -B summary/validate_summary.py
python -B counting/validate_counting.py
python -B refinements/validate_refinements.py
```

`RIME_LAKE_EXE` may select the pinned `lake.exe`; `lake --no-cache build`
alone retains the original origin target. The later validators compile
their named modules and audit their complete target closures. The bootstrap
entry is [`bootstrap_inputs.py`](bootstrap_inputs.py); the dependency lock
and [`upstream-manifest.json`](upstream-manifest.json) specify the reused
versions. A portable snapshot must include the bound inputs, manifests,
reports and validators, not a machine-specific `.lake/packages` junction.

## Separate Later Formalization

The pinned paper already contains proofs of the following results. They
are not kernel-verified conclusions of this companion snapshot:

| Paper owner | Remaining Lean obligation |
|---|---|
| Proposition 7.1 | Identify the actual r=2,c=0 proper-arc summary type with the fixed-pair owner type, then transport its equivalences. |
| Propositions 8.1 and 8.2; Corollary 8.3 | Fixed-n, diagonal fixed-r and unscaled summary-count generating functions, with their distinct coefficient domains. |
| Theorem 8.4 | Fixed-r 9/2 growth, leading coefficient and explicit tail/error estimates for the proper-arc count. |

In particular, the exact finite counts are closed here; a Lean proof
of their generating functions or fixed-r 9/2 growth requires a separate
analytic/formal-series layer. Numerically specializing the closed proper-arc
formula at r=2 is not the pending cross-owner actual-type identification.

## Frozen Target Signatures

These are verbatim signatures from the owning kernel audit reports. The
paper contracts and source links above disambiguate older pretty-printer
outputs that suppress inferred subtype binder types. M9 additionally records
the constants in each target's type to pin its actual-history domain.

### O1: `ProperArc.run_originWord`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) (r t : ℕ),
  r < n →
    1 ≤ t →
      t < r →
        RegisteredAbsorptionChains.run (ProperArc.arc c r) (RegisteredAbsorptionChains.singletonExecution n)
            (ProperArc.originWord c r t) =
          { placed := ProperArc.boundaryPlacement c r, origin := some (ProperArc.originRecord c r t), chain := [] }
```

### O2: `ProperArc.actual_registered_origin_unique`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) (r : ℕ) (s : RegisteredAbsorptionChains.Execution n (ZMod n)),
  2 ≤ r ∧ r < n →
    RegisteredAbsorptionChains.ReachableExecution (ProperArc.arc c r) s →
      s.origin ≠ none → ∃! i, s.origin = some (ProperArc.originRecord c r (↑i + 1))
```

### O3: `ProperArc.actualRegistrationOriginsEquivCuts`

```lean
{n : ℕ} →
  [inst : NeZero n] → (c : ZMod n) → (r : ℕ) → 2 ≤ r ∧ r < n → ProperArc.ActualRegistrationOrigins c r ≃ Fin (r - 1)
```

### C1: `ProperArc.Chains.realize_clean_code`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) (v : RegisteredAbsorptionChains.Code (n - r))
  (t : ℕ),
  1 ≤ t ∧ t < r →
    ∃ w,
      have s := RegisteredAbsorptionChains.run (ProperArc.arc c r) (RegisteredAbsorptionChains.singletonExecution n) w;
      s.origin = some (ProperArc.originRecord c r t) ∧
        s.chain = ProperArc.Chains.decodeChain c ⋯ v ∧
          RegisteredAbsorptionChains.CleanOutside (ProperArc.Chains.decodedCarrier c ⋯ v) s ∧
            ProperArc.arc c r ⊆ ProperArc.Chains.decodedCarrier c ⋯ v
```

### C2: `ProperArc.Chains.actualSelectedChainsEquivCode`

```lean
{n : ℕ} →
  [inst : NeZero n] →
    (c : ZMod n) →
      {r : ℕ} →
        2 ≤ r ∧ r < n →
          (t : Fin (r - 1)) →
            ProperArc.Chains.ActualSelectedChains c r (↑t + 1) ≃ RegisteredAbsorptionChains.Code (n - r)
```

### C3: `ProperArc.Chains.card_actualSelectedChains`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ},
  2 ≤ r ∧ r < n → ∀ (t : Fin (r - 1)), Nat.card (ProperArc.Chains.ActualSelectedChains c r (↑t + 1)) = 3 ^ (n - r)
```

### F1: `ProperArc.Chains.positivePlacementFibreEquiv`

```lean
{n : ℕ} →
  [inst : NeZero n] →
    (c : ZMod n) →
      {r : ℕ} →
        (hr : 2 ≤ r ∧ r < n) →
          (t : Fin (r - 1)) →
            (v : RegisteredAbsorptionChains.Code (n - r)) →
              0 < ProperArc.Chains.outsideCount ⋯ v →
                RegisteredAbsorptionChains.FiberParams n (ProperArc.Chains.outsideCount ⋯ v) ≃
                  ProperArc.Chains.ActualCodePlacements c hr t v
```

### F0: `ProperArc.Chains.fullPlacementFibreEquiv`

```lean
{n : ℕ} →
  [inst : NeZero n] →
    (c : ZMod n) →
      {r : ℕ} →
        (hr : 2 ≤ r ∧ r < n) →
          (t : Fin (r - 1)) →
            (v : RegisteredAbsorptionChains.Code (n - r)) →
              ProperArc.Chains.outsideCount ⋯ v = 0 → ZMod n ≃ ProperArc.Chains.ActualCodePlacements c hr t v
```

### F2: `ProperArc.Chains.codePlacementFibreEquiv`

```lean
{n : ℕ} →
  [inst : NeZero n] →
    (c : ZMod n) →
      {r : ℕ} →
        (hr : 2 ≤ r ∧ r < n) →
          (t : Fin (r - 1)) →
            (v : RegisteredAbsorptionChains.Code (n - r)) →
              ProperArc.Chains.CodeFiberParams ⋯ v ≃ ProperArc.Chains.ActualCodePlacements c hr t v
```

### F3: `ProperArc.Chains.card_actualCodePlacements`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) (t : Fin (r - 1))
  (v : RegisteredAbsorptionChains.Code (n - r)),
  Nat.card (ProperArc.Chains.ActualCodePlacements c hr t v) =
    n * (n + ProperArc.Chains.outsideCount ⋯ v - 2).choose (ProperArc.Chains.outsideCount ⋯ v)
```

### S1: `ProperArc.Chains.actualRegisteredSummariesEquivParams`

```lean
{n : ℕ} →
  [inst : NeZero n] →
    (c : ZMod n) →
      {r : ℕ} → (hr : 2 ≤ r ∧ r < n) → ProperArc.Chains.ActualRegisteredSummaries c r ≃ ProperArc.Chains.SummaryParams ⋯
```

### S2: `ProperArc.Chains.decodeSummary_same_word`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) (p : ProperArc.Chains.SummaryParams ⋯),
  ∃ word,
    have s := RegisteredAbsorptionChains.run (ProperArc.arc c r) (RegisteredAbsorptionChains.singletonExecution n) word;
    s = ↑(ProperArc.Chains.decodeSummary c hr p) ∧
      s.origin = some (ProperArc.originRecord c r (↑p.fst + 1)) ∧
        s.chain = ProperArc.Chains.decodeChain c ⋯ p.snd.fst ∧
          s.placed = ↑((ProperArc.Chains.codePlacementFibreEquiv c hr p.fst p.snd.fst) p.snd.snd)
```

### N1: `ProperArc.Chains.card_actual_registered_summaries`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ},
  2 ≤ r ∧ r < n →
    Nat.card (ProperArc.Chains.ActualRegisteredSummaries c r) =
      (r - 1) * n *
        ((n + (n - r) - 2).choose (n - r) +
          2 * ∑ b ∈ Finset.Icc 1 (n - r), 3 ^ (b - 1) * (n + (n - r) - b - 2).choose (n - r - b))
```

### N2: `ProperArc.Chains.card_actual_registered_summaries_short_complement`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n),
  3 ≤ n → Nat.card (ProperArc.Chains.ActualRegisteredSummaries c (n - 1)) = (n - 2) * n * (n + 1)
```

### R1: `ProperArc.Chains.card_actualSelectedChains_length`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ},
  2 ≤ r ∧ r < n →
    ∀ (t : Fin (r - 1)) (j : ℕ),
      Nat.card { A : ProperArc.Chains.ActualSelectedChains c r (↑t + 1) // (↑A).length = j } = (n - r).choose j * 2 ^ j
```

### R2: `ProperArc.Chains.card_actualRankCodePlacements`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) (t : Fin (r - 1))
  (v : RegisteredAbsorptionChains.Code (n - r)),
  0 < ProperArc.Chains.outsideCount ⋯ v →
    ∀ (s : ℕ),
      2 ≤ s ∧ s ≤ ProperArc.Chains.outsideCount ⋯ v + 1 →
        Nat.card (ProperArc.Chains.ActualRankCodePlacements c hr t v s) =
          s * (ProperArc.Chains.outsideCount ⋯ v - 1).choose (s - 2) * n.choose s
```

### R0: `ProperArc.Chains.card_actualFullRankCodePlacements`

```lean
∀ {n : ℕ} [inst : NeZero n] (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) (t : Fin (r - 1))
  (v : RegisteredAbsorptionChains.Code (n - r)),
  ProperArc.Chains.outsideCount ⋯ v = 0 → Nat.card (ProperArc.Chains.ActualRankCodePlacements c hr t v 1) = n
```
