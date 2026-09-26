# P28.5n: Fresh-Consumption Hostile Selector

## Status

This is a source-local selector over the P28.5m feasibility surface. It runs
no exit oracle, reads no `Good_4` or `Good_5` field, and grants no rank-four or
rank-five section authority.

## Frozen selection rule

The selector is evaluated in the following order:

1. require consumption of the inherited distinguished packet;
2. hold `sigma5_length == 3` fixed;
3. prefer the `1+2` fusion family;
4. minimize structural Hamming distance to the third closed chain using only
   source/target partition, surplus, binary-kernel mass, and `F_4`-relative
   kernel offsets;
5. retain the complete primary tie, then minimize action-relative placement
   distance on the paired rooted rank-five/rank-four mass vectors;
6. retain any final tie rather than selecting by artifact order.

Neither stage reads low-rank base membership, lower-section membership,
winning labels, Bellman data, or a downstream success field.

## Exact result

The P28.5m hard class contains 74 cells and 1,224 contexts. Restricting to
`1+2` leaves 41 cells and 672 contexts. The structural minimization has a
unique minimizer at distance one, so the action-relative tie-break does not
discard an alternative cell. Its minimum placement distance is three.

The resulting pre-section carrier has 36 rooted contexts and signature

```text
family                         22111__12_TO_3211
rank-five partition            (2,2,1,1,1)
rank-four partition            (3,2,1,1)
fusion parents                 1+2
sigma5 length                  3
sigma5 surplus                 2
inherited fresh consumed       true
binary-kernel masses           [0,3]
F4-relative kernel offsets     [0,2]
```

Relative to the third closed chain, the selected carrier keeps the source and
target partitions, fusion masses, length, surplus, and kernel-mass multiset.
It flips inherited-fresh participation and changes the kernel-offset pattern
from `[0,6]` to `[0,2]`. It is therefore the nearest declared source-local
fresh-consumption control, not a success-selected carrier.

## Phase boundary

The artifact records

```text
evaluation_status       NOT_RUN
section_authority       NOT_GRANTED
winner_selected         false
```

The allowed next phase is to construct and freeze the rank-four abstract menu
and exact realization fibers for these 36 contexts. Only after that payload
has been digested may an independent evaluator compute `Good_4`.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_select_fresh_consumption_hostile.py
python experiments/synchronizing_automata/validation/validate_paper28_fresh_consumption_hostile.py
```

The artifact is
`results/paper28_fresh_consumption_hostile_selection_v1.json.gz`. Its SHA-256
digest is `01ee8936f3a733e26ea0f8094be25fc9ca9aea2d76ccebe632ef6a9eb5e4b969`.

## Claim boundary

P28.5n proves only the displayed source-local minimizer inside the frozen
41-cell `1+2`, fresh-consuming, length-three class. It proves no return,
maximality, canonicity, full-universe coverage, or all-rank statement. Fresh
avoidance remains an open necessity question until the staged menu/lift
construction and independent return evaluator are completed.
