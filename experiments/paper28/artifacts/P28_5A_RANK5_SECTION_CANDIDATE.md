# P28.5a Extremal Rank-Five Section Return Candidate

## Status

The pre-evaluation objects are frozen. This note defines a source-local
rank-five section candidate, a future-free mechanism menu, its exact lift
fibers, and the independently released lower section. It does **not** evaluate
`Good_5` and therefore does not claim a rank-five-to-four return theorem.

The intended later statement is

```text
for every C in Sec_5,cand^(7),
there exists m in M_5(C) with Good_5(C,m).
```

That existential assertion is outside the present artifact.

## 1. Source Section Candidate

Write a rooted defect as

```text
d = (0, pi(1), ..., pi(5), 0),   pi in S_5.
```

The source-local carrier condition is

```text
{4,5} subset pi({3,4,5}).
```

It selects 36 actions before any lower-section data is loaded. Apply the
intrinsic `Sigma_6^(7)` rule to the rank-six kernel image. The unique
predecessor idempotent `0123450` uses the oriented entry `p^6 d` and is
excluded. Every other row uses the endpoint-shortest activated entry `p^2 d`.
This leaves

```text
|Sec_5,cand^(7)| = 35.
```

Every source has partition `(2,2,1,1,1)`, with the fresh mass-two packet at
the root. The second mass-two packet remains action-addressed; the 35 sources
realize six coordinate mass placements. No rank-four section membership,
`Good_5`, winning label, or low-rank success label enters source membership.

## 2. Future-Free Menus and Exact Lifts

For each source context `C`, the producer enumerates all tied
endpoint-shortest one-corridor rank-five-to-four receipts. It first groups
them only by the future-free interaction skeleton and retains accounting
refinements and exact lifts as relations inside each channel:

```text
M_5(C) = interaction-skeleton channels,
Lift_5(C,m) = source-addressed exact receipts in channel m.
```

An exact lift retains:

- the complete word and corridor boundary;
- source and fusion packet identities;
- exact target placement and distinguished packet;
- ancestry update;
- length, surplus, debt profile, and residual target budget;
- exact `TRANSPORT` / `RETURN` / `FUSION` factorization.

The frozen construction has the following replay checksums:

| object | count |
| --- | ---: |
| source contexts | 35 |
| abstract channels | 87 |
| exact lifts | 214 |
| replay boundary states | 752 |
| internal-only boundary states | 505 |

The menu-size distribution is

```text
3 contexts with size 1,
12 contexts with size 2,
20 contexts with size 3.
```

These are fixed-scope checksums, not all-rank bounds.

## 3. Construction Order and Target Authority

The producer enforces the order

```text
source section
  -> future-free menus and exact lifts
  -> construction-payload digest
  -> independent lower-section projection
  -> hostile evaluator absent.
```

Only after the construction digest is frozen does it read the released Paper
XXVII target authority `Sec_4,ext^(7)`. The target is imported as 35 typed
section boundary keys. No source or menu membership is changed after that
import, and no target intersection is computed.

The later predicate is reserved as

```text
Good_5(C,m)
iff some x in Lift_5(C,m) has target in Sec_4,ext^(7).
```

The current artifact records zero evaluated sources and zero evaluated
channels. Its evaluator status is `ABSENT_BY_DESIGN`.

## 4. Type Boundary

Local operation boundaries are replay states, not recursive proof states.
The current artifact exports no recursive target and grants no section
authority to any internal-only boundary. A later evaluator may certify only
exact receipt endpoints against the independently declared lower section.

## 5. Claims and Nonclaims

The present result establishes only that the four P28.5a objects are
independently defined and replayable:

```text
Sec_5,cand^(7),  M_5(C),  Lift_5(C,m),  Sec_4,ext^(7).
```

It does not claim:

- that every source has a good channel;
- that the 87 channels or the menu-size bound are stable in rank or `n`;
- that the source candidate is maximal or canonical beyond this declared
  source-local rule;
- that an internal boundary can serve as a section checkpoint;
- that the full 15,120 inherited scope or `n=8` has been tested.

## 6. Replay

From the repository root, with the released Paper XXVII target artifact:

```powershell
python experiments/synchronizing_automata/paper28_prepare_rank5_section_candidate.py `
  --n7-extremal-input <paper27-release>/experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json

python experiments/synchronizing_automata/validation/validate_paper28_rank5_section_candidate.py `
  --n7-extremal-input <paper27-release>/experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json
```

The validator recomputes the complete payload, checks the forbidden-field and
checkpoint-type invariants, and verifies the source-closure receipt.
