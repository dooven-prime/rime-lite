# P28.5k: Third Rank-Five Section Return

## Status

The matching rank-five construction and independent `Good_5` evaluator are
complete. They establish the third fixed-scope chain

```text
Sec_5,cand3^(7) -> Sec_4,cand3^(7) -> P_<=3^(7).
```

## Pre-evaluation construction

The constructor reads the frozen P28.5h source carrier and the independently
certified lower authority, but it constructs and digests every source, menu,
and exact lift before opening the lower-section evaluator.

```text
rank-five sources            36
future-free channels         70
exact lifts                 209
maximum menu size             2
menu histogram       1:2, 2:34
internal-only states        585
exported internal states      0
Good_5 status           NOT_RUN
```

The frozen inherited `1+2`, length-three, surplus-two `Sigma_5` receipt is
present in the corresponding exact lift fiber for every source. No channel is
chosen by lower-section membership.

## Independent Good_5 evaluation

The post-freeze evaluator finds:

```text
successful sources          36 / 36
successful channels         36 / 70
failed channels             34 / 70
successful exact lifts      36 / 209
failed exact lifts         173 / 209
good channels per source     exactly 1
successful handoffs          36 identity
winner selected              false
```

All failed channels and lifts remain in the relation. The result therefore
has the required existential quantifier and does not serialize a preferred
winner.

## Typed handoff

Every successful target is literally identical to its canonical
`Sec_4,cand3^(7)` context. The evaluator nevertheless uses the same typed
handoff check as the preceding realizations and verifies the rooted action,
occupied coordinates, packet masses, and distinguished ancestry. Identity is
an observed realization fact, not a theorem premise.

Together with the first atom-bijection chain and the second identity chain,
this continues to support the current schema decision: certified preservation
of lower-theorem observables belongs to F3 exact-lift soundness; a separate F6
handoff axiom is not promoted.

## Structural consequence

This chain breaks the shared `1+1`, zero-surplus, and kernel-mass `[0,2]`
anatomy of the first two positive-rank returns while preserving length three:

```text
(2,2,1,1,1) --[1+2, length 3, surplus 2]--> (3,2,1,1).
```

Hence `1+1` fusion, zero surplus, and kernel mass `[0,2]` are not necessary
features of fixed-`n=7` positive-rank section return on the three declared
realizations. Length three and nonconsumption of the incoming distinguished
packet remain common realization facts, not promoted assumptions.

## Claim boundary

The result applies only to the frozen 36-context source-local carrier. It does
not cover the full inherited rank-five universe, prove a canonical or maximal
section, establish B1/B2 menu bounds, or imply an all-rank return theorem.

## Artifacts

- `results/paper28_third_rank5_section_candidate_v1.json.gz`
- `results/paper28_third_rank5_section_return_evaluation_v1.json.gz`
- their replay receipts and validators

