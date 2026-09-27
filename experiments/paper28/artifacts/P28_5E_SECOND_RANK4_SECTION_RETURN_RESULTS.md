# P28.5e: Second Rank-Four Section-to-Base Return

## Status

The 48-context `31111__11_TO_3211` carrier now has an independently staged
fixed-scope section-to-base theorem:

\[
 \forall C\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand2}},\qquad
 \exists m\in\mathfrak M_4(C),\qquad
 \exists x\in\operatorname{Lift}_4(C,m):
 \partial^+x\in P_{\le3}^{(7)}.
\]

The result grants the name `Sec_4,cand2^(7)` to the previously frozen
pre-section carrier. It does not yet construct or evaluate the corresponding
rank-five return.

## Phase A: future-free construction

The constructor reads only the frozen P28.5d selection artifact. It rebuilds
the 48 exact typed rank-four source contexts and enumerates the complete tied
endpoint-shortest Type-I/II macro relation. `Good_4`, exact low-rank success,
winning labels, Bellman data, and reset coaccessibility are absent from the
construction payload.

The frozen construction contains:

```text
source contexts               48
abstract skeleton channels   401
accounting refinements      3,769
source-addressed exact lifts 9,600
menu size                     6--11
operation kinds               TRANSPORT / RETURN / FUSION
```

Its construction-payload digest is
`6aa660c94d72c32739b959d227da8c0eb5124a34e0f208614dbe773d8af4dfcf`.
The complete artifact digest is
`0fad98bbedbd54403b7e64acf05d61e0f8d6e3d6909ad109ed945b1f4a774b9f`.

## Phase B: post-freeze evaluation

The evaluator reads the frozen Phase-A artifact, verifies its construction
digest, and evaluates every exact target against the independent exact
`P_<=3^(7)` base. It does not regenerate a source, channel, or lift, and it
does not select a preferred successful channel.

The result is:

```text
successful sources                 48 / 48
successful channels               401 / 401
successful exact lifts          9,498 / 9,600
unsuccessful exact lifts              102
distinct certified target contexts  1,293
```

All 401 channels have at least one successful exact lift. This does not make
the exact fibers deterministic: eight channels in four source contexts contain
both successful and unsuccessful lifts. The 102 unsuccessful lifts are kept
in the relation and provide a hostile control for the existential channel
semantics.

The 48 menu sizes, equivalently the successful-channel counts, have histogram

```text
6:2, 7:5, 8:23, 9:11, 10:6, 11:1.
```

Of the 401 successful channels, 295 certify rank-two targets and 106 certify
rank-three targets.

## Section authority and typing

Because every frozen source has a good channel, the evaluator grants
fixed-scope authority to

\[
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand2}}.
\]

The authority is attached only to the 48 original exact source contexts.
No internal operation boundary is exported as a recursive checkpoint. The
recursive targets are exact rank-two or rank-three contexts only.

This stage is section-to-base, so it does not test the P28.5c typed-handoff
promotion gate. That question belongs to the later rank-five-to-four return,
where an exact target must be compared with this newly certified section.

## Claim boundary

The result proves F5 only on the declared 48-context fixed-`n=7` carrier. It
does not claim:

- that every exact lift succeeds;
- that the carrier is canonical or maximal;
- that the matching rank-five return succeeds;
- that the full inherited 15,120-context scope is covered;
- an all-rank return theorem or a uniform menu bound.

The stronger fixed-scope fact that every channel is good is reported as a
derived result, not used as the general theorem quantifier.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_prepare_second_rank4_section_candidate.py
python experiments/synchronizing_automata/validation/validate_paper28_second_rank4_section_candidate.py
python experiments/synchronizing_automata/paper28_evaluate_second_rank4_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_second_rank4_section_return.py
```

The post-freeze evaluation artifact is
`results/paper28_second_rank4_section_return_evaluation_v1.json.gz`. Its
artifact digest is
`a82c3ba7719995ecbc6ec44178836ffdd1c406ac145803a852252db5016377f9`;
the JSON receipt binds the frozen construction artifact and the local source
closure.

## Next permitted step

Define the corresponding rank-five source, future-free menu, exact lift
fibers, and typed handoff without reading this section's success labels. Freeze
and digest that construction first. Only then evaluate `Good_5` against
`Sec_4,cand2^(7)`.

This step has subsequently been completed under that order; see
[`P28_5F_SECOND_RANK5_SECTION_RETURN_RESULTS.md`](P28_5F_SECOND_RANK5_SECTION_RETURN_RESULTS.md).
