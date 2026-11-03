# Theorem-to-Source Review Map

The declared main proof line is closed: actual behavior, exact parameter
equivalences and counts, full-summary observation, and the two growth laws
with exponential quotient-size separation. This map identifies the owning
paper statements and frozen companion proofs separately.

**Domain:** `n>=3`, singleton-seed chronological `p,d` histories, selected
source pair `{0,1}`, complete declared outputs, unrestricted future words.

**Identity:** the four proof milestones have exact local source identities.
A publicly retrievable version of this complete companion is still pending;
the HAL paper identifiers below do not identify these later Lean files.

## Paper-to-Source Table

| Paper statement | Frozen Lean source | Correspondence |
|---|---|---|
| [Lemma 5.3: exact coalescence and strict gap](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L456) | [FutureEvent.gapProbe_coalesces_iff_holeMove](../FutureEvent/ProbeCoalescence.lean#L316)<br>[FutureEvent.probe_coalescence_strict_gap](../FutureEvent/ProbeCoalescence.lean#L367) | Formalization of the stated result |
| [Theorem 1 / (6.1): actual future-equivalence classes](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L557) | [FutureEvent.futureEquivalent_iff_normalForm](../FutureEvent/FutureClassification.lean#L62)<br>[FutureEvent.futureQuotientEquivNormalForms](../FutureEvent/FutureQuotient.lean#L178) | Formalization of the stated result |
| [Theorem 2: distinguishing depth 6n-10](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L593) | [FutureEvent.future_inequivalence_uniform_separation](../FutureEvent/FutureClassification.lean#L73)<br>[FutureEvent.bounded_traces_iff_futureEquivalent](../FutureEvent/FutureClassification.lean#L82) | Formalization of the stated result |
| [Proposition 3.3: actual placement parameters and counts](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L212) | [FutureEvent.registerablePlacementParamsEquiv](../FutureEvent/RegisterablePlacementEquiv.lean#L133)<br>[FutureEvent.registeredPlacementParamsEquiv](../FutureEvent/RegisteredPlacementEquiv.lean#L134)<br>[FutureEvent.card_actual_registerable_placements](../FutureEvent/ClosedQuotientCount.lean#L12)<br>[FutureEvent.card_actual_registered_placements_closed](../FutureEvent/ClosedQuotientCount.lean#L52) | Formalization of the stated result |
| [Equation (7.1): exact future quotient count](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L646) | [FutureEvent.card_futureQuotient_closed](../FutureEvent/ClosedQuotientCount.lean#L68) | Formalization of the stated result |
| [Equation (7.2): actual future quotient asymptotic](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L672) | [FutureEventAnalysis.tendsto_futureQuotient_normalized](../analysis/FutureCountAsymptotics.lean#L100) | Same ratio limit; Lean uses the pinned Wallis input |
| [Lemma 6.1 and (6.2): full-summary quotient and count](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L605) | [FullSummary.event_to_summary_prefix_detection](../full_summary/Observation.lean#L77)<br>[FullSummary.fullQuotientEquivSummaries](../full_summary/CountBridge.lean#L20)<br>[FullSummary.card_fullQuotient_closed](../full_summary/CountBridge.lean#L39) | Formalization of the stated result |
| [Theorem 5.1: inherited actual complete-summary count](https://github.com/dooven-prime/rime-lite/blob/050cf8ec11e3db263830b46ea95e4062b8e08869/papers/unnumbered/circular_coalescence_counts/MANUSCRIPT.md#L515) | [RegisteredAbsorptionChains.card_actualRegisteredSummaries_closed](../full_summary/owner/RegisteredAbsorptionChains/TotalCountFormula.lean#L64) | Inherited from the pinned fixed-pair companion; used in future-paper (7.3) |
| [Auxiliary bound for (7.3b); fixed-pair Corollary 5.2](https://github.com/dooven-prime/rime-lite/blob/050cf8ec11e3db263830b46ea95e4062b8e08869/papers/unnumbered/circular_coalescence_counts/MANUSCRIPT.md#L544) | [ObserverComparison.summaryBracket_error](../comparison/SummarySeries.lean#L143) | Companion strengthening: signed error bound, not a verbatim HAL-v1 lemma |
| [Equations (6.2), (7.3b), preceding (7.4): full growth](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L711) | [ObserverComparison.tendsto_fullQuotient_normalized](../comparison/ObserverGrowth.lean#L75) | Same full-quotient limit; negative-binomial tail replaces singularity analysis |
| [Equation (7.4): exponential quotient-size separation](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L723) | [ObserverComparison.tendsto_full_div_future_normalized](../comparison/ObserverGrowth.lean#L102) | Formalization of the stated result |
| [Consequence of (7.4): quotient-size ratio tends to infinity](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md#L723) | [ObserverComparison.tendsto_full_div_future_atTop](../comparison/ObserverGrowth.lean#L116) | Explicit formal corollary; not a separately numbered theorem in HAL v1 |

The fixed-pair count is inherited, including its registered-origin
classification and actual dependent fibre construction. The full-summary
bridge identifies literal executions and seed provenance, not just numbers.

## Four Final Target Signatures

These are the complete elaborated signatures copied from the frozen Lean
dependency report, not hand-transcribed restatements. `fullCardReal m` is
`Nat.card (FullSummary.FullQuotient (m+3))` cast to reals, and
`futureCardReal m` reads the analogous actual future-event quotient.
The cofinal parameter `n=m+3` covers every legal horizon.

### summaryBracket_error

```lean
∀ (m : ℕ),
  0 ≤ 1 - ObserverComparison.summaryBracket (m + 1) / (9 / 2) ^ (m + 1) ∧
    1 - ObserverComparison.summaryBracket (m + 1) / (9 / 2) ^ (m + 1) ≤ (8 / 9) ^ (m + 1)
```

Source: [ObserverComparison.summaryBracket_error](../comparison/SummarySeries.lean#L143); SHA-256 `e939dbf2f3a991c7eff09d69a0dee69c304a7b1ce7c323283cf6f0eeff2b4ec4`.

Paper relation: Companion strengthening: signed error bound, not a verbatim HAL-v1 lemma.

Dependency closure: 16,510 declarations; axioms: `propext, Classical.choice, Quot.sound`. The full node list and direct edges are at [`comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/0`](../comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/0).

### tendsto_fullQuotient_normalized

```lean
Filter.Tendsto (fun m => ObserverComparison.fullCardReal m / ((↑m + 3) * (9 / 2) ^ (m + 3))) Filter.atTop
  (nhds (4 / 81))
```

Source: [ObserverComparison.tendsto_fullQuotient_normalized](../comparison/ObserverGrowth.lean#L75); SHA-256 `dde719f25d4fa7700264956de4118b809dc7381ac2e60a7d852fb2272e0c83f5`.

Paper relation: Same full-quotient limit; negative-binomial tail replaces singularity analysis.

Dependency closure: 22,271 declarations; axioms: `propext, Classical.choice, Quot.sound`. The full node list and direct edges are at [`comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/1`](../comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/1).

### tendsto_full_div_future_normalized

```lean
Filter.Tendsto
  (fun m => ObserverComparison.fullCardReal m / FutureEventAnalysis.futureCardReal m / (√(↑m + 3) * (9 / 8) ^ (m + 3)))
  Filter.atTop (nhds (64 * √Real.pi / 405))
```

Source: [ObserverComparison.tendsto_full_div_future_normalized](../comparison/ObserverGrowth.lean#L102); SHA-256 `dde719f25d4fa7700264956de4118b809dc7381ac2e60a7d852fb2272e0c83f5`.

Paper relation: Formalization of the stated result.

Dependency closure: 44,071 declarations; axioms: `propext, Classical.choice, Quot.sound`. The full node list and direct edges are at [`comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/2`](../comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/2).

### tendsto_full_div_future_atTop

```lean
Filter.Tendsto (fun m => ObserverComparison.fullCardReal m / FutureEventAnalysis.futureCardReal m) Filter.atTop
  Filter.atTop
```

Source: [ObserverComparison.tendsto_full_div_future_atTop](../comparison/ObserverGrowth.lean#L116); SHA-256 `dde719f25d4fa7700264956de4118b809dc7381ac2e60a7d852fb2272e0c83f5`.

Paper relation: Explicit formal corollary; not a separately numbered theorem in HAL v1.

Dependency closure: 44,075 declarations; axioms: `propext, Classical.choice, Quot.sound`. The full node list and direct edges are at [`comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/3`](../comparison/milestones/observer-growth-v1/dependency-audit.json#/targets/3).

## Frozen Layers

| Layer | Inputs / targets / graph nodes | Manifest | Dependency report |
|---|---|---|---|
| finite | 81 / 5 / 13,538 | [manifest](../milestones/finite-combinatorial-v1/manifest.json)<br>`f4f2d444828362f2cb95387a8852f5317bc1057f5be71df2351f9d656369576c` | [graph](../milestones/finite-combinatorial-v1/dependency-audit.json)<br>`9421a53b3d0fb1fc914d90d793f65a31ea22a34a88aad50b59864584dce1c729` |
| wallis | 5 / 3 / 43,759 | [manifest](../analysis/milestones/wallis-ratio-v1/manifest.json)<br>`273e87e97bd2f5b779898b1f41c6361efa1debcaeed44fbd5f383f37d3419232` | [graph](../analysis/milestones/wallis-ratio-v1/dependency-audit.json)<br>`eee38fd15e99f9437b767e1925b3c44a9fdd4d60da046a4b55275d1dd3db8c74` |
| full | 17 / 5 / 13,615 | [manifest](../full_summary/milestones/full-summary-v1/manifest.json)<br>`1bac05ed4a743dff4ce4f07c32237a38207bd2182e404b56c4de29f0b47899aa` | [graph](../full_summary/milestones/full-summary-v1/dependency-audit.json)<br>`84f4649d2c029c2bd9628779fc982b2e4f75b940705c2b5bcba1c176912c8bcd` |
| comparison | 5 / 4 / 44,075 | [manifest](../comparison/milestones/observer-growth-v1/manifest.json)<br>`5154f2a7d11c7434a7af29c9160965ecc105210b95c33ae118ec4815df9b4fc8` | [graph](../comparison/milestones/observer-growth-v1/dependency-audit.json)<br>`337df320752120b7b850c15802467370d161b99585255c9f080e38881e482cef` |

Input and graph-node counts are per layer; dependency closures overlap and
must not be added as independent proofs. Each graph records declaration types,
proof bodies, direct dependencies, target closures and axiom leaves.

The mathematical dependency spine is:

```text
actual p,d execution + source order + same-word probes
  -> all-word future-equivalence classification
  -> pure placement parameters <-> actual reachable placements
  -> exact future count -> Wallis -> future growth
actual Moore output + event-to-summary bridge
  -> full quotient <-> null + registerable placements + actual summaries
  -> pinned fixed-pair exact summary count -> negative-binomial tail
  -> full growth -> full/future ratio limit -> divergence
```

This spine covers the declared classification, count and growth conclusions.
The separate probe-graph enumeration/distribution in (7.6)-(7.7a) and the
formal power-series identity (7.3a) are not claimed as Lean coverage here.

## Build and Audit

Lean: `Lean (version 4.33.0, x86_64-w64-windows-gnu, commit d8b18978322de05a8f3dba51ef03cf5461676c17, Release)`.

Mathlib: `db584cd6d46c92f209a44c0f1c829460d327499d`. The package `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json` fix the toolchain and dependency revisions.

From `experiments/future_event_minimal_quotient/lean`, first obtain the pinned
Lean toolchain and Lake dependencies (including the Mathlib cache). Then:

```powershell
lake --no-cache build
python -B validate_companion.py
python -B freeze_finite_milestone.py
python -B analysis/validate_analysis.py
python -B full_summary/validate_bridge.py
python -B comparison/validate_comparison.py
python -B review/build_theorem_map.py
```

Each layer's ordinary replay rebuilds and audits; it does not rewrite its
freeze. The comparison replay also rebuilds the bound owner and extension
modules, so stale extension `.olean` files are not accepted as evidence.
`--source-only` on the proof validators checks bytes only. These records
document local kernel replay with cached pinned dependencies, not a completed
fresh-machine cold replay.

Run the recorded negative controls and finite-control tests separately:

```powershell
python -B -m unittest discover -s tests -p 'test_*.py' -v
python -B -m unittest discover -s analysis/tests -p 'test_*.py' -v
python -B -m unittest discover -s full_summary/tests -p 'test_*.py' -v
python -B -m unittest discover -s comparison/tests -p 'test_*.py' -v
python -B -m unittest discover -s review/tests -p 'test_*.py' -v
```

The parent Python control package is independently versioned and is not a
premise of these all-parameter Lean proofs.

## Manuscript and Public Snapshot Identities

- Paper: [hal-05844771v1](https://hal.science/hal-05844771v1); [pinned source](https://github.com/dooven-prime/rime-lite/blob/baaded50b61a6a9315a6002ece2dfa9b2c9e16a2/papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md); [read-only reference copy](manuscripts/future-event-hal-v1.md). Source commit `baaded50b61a6a9315a6002ece2dfa9b2c9e16a2`; SHA-256 `5e0adba3542361c4b8227f96507bca40f71a76012389a6d97811cf7658d5dad6`.
- Paper: [hal-05837829v1](https://hal.science/hal-05837829v1); [pinned source](https://github.com/dooven-prime/rime-lite/blob/050cf8ec11e3db263830b46ea95e4062b8e08869/papers/unnumbered/circular_coalescence_counts/MANUSCRIPT.md); [read-only reference copy](manuscripts/fixed-pair-source.md). Source commit `050cf8ec11e3db263830b46ea95e4062b8e08869`; SHA-256 `4fac6e3a1edb4038c4be8e6f39ed2c20197a31547a01a1afd5baa9edbb5723e9`.

The reference copies retain exact historical bytes; they do not replace
the owning manuscripts or claim that HAL deposited the later formalization.

The independently obtainable **companion** identity remains `PENDING`.
Before advertising public replay, select and commit this complete companion
closure, fix a source tag/commit, and archive an obtainable source bundle
with its checksum and persistent record identifier. Include all four
manifests, reports, their bound sources, the two read-only manuscript copies,
build locks, attribution/license files, this map and its checker. `.lake/`
build products are not the source identity. A normal source archive must
preserve the recorded bytes, rather than applying checkout newline conversion.

Record that retrieval identity in a downstream public-source anchor, outside
the four frozen closures. Verify its commit and archived bytes; do not edit
old manifests to turn their truthful local status into a published claim.

Machine-readable map: [`theorem-map.v1.json`](theorem-map.v1.json), SHA-256 `e901404b456e33700bce30debc24c1595f38f093fc343034274a4dea419d462f`.

The map checker validates source/report hashes, exact declaration locations,
paper anchors and the four target signatures. It does not re-run the kernel;
the separate proof replay commands above perform that work.
