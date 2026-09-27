# P28.5d: Second Rank-Five Return Candidate

## Status

This note freezes the choice of a second fixed-`n=7` higher-rank return model.
It does **not** grant section authority and does not evaluate `Good_4` or
`Good_5`.

The choice is made entirely on the future-free 562-cell carrier inherited from
the Paper XXVII audits. Completion success, low-rank membership, winning
labels, and lower-section membership are not inputs.

## Selection rule

The released extremal reference cell has signature

```text
family                              22111__11_TO_2221
fusion parent sizes                 1+1
fusion contains inherited fresh     false
Sigma_5 length / surplus            3 / 0
binary-kernel mass multiset         [0,2]
F4-relative kernel offsets          [0,6]
```

Exclude that mass-transition family. Among all remaining future-free cells,
minimize Hamming distance on the six non-partition continuity fields displayed
above. There is a unique distance-zero cell:

```text
family                              31111__11_TO_3211
rank-five source partition          (3,1,1,1,1)
rank-four target partition          (3,2,1,1)
fusion parent sizes                 1+1
fusion contains inherited fresh     false
Sigma_5 length / surplus            3 / 0
binary-kernel mass multiset         [0,2]
F4-relative kernel offsets          [0,6]
contexts                            48
```

Thus the candidate keeps the local `Sigma_5` fusion/accounting and
kernel-relative boundary fixed while changing the upper entry geometry and the
rank-four partition. On these 48 rows, `Sigma_6` is uniformly `d`, while the
two tied `Sigma_5` words `p^2d` and `p d^2` occur 24 times each.

This is a pre-section carrier, denoted provisionally by

\[
 \mathcal C^{(7)}_{4,\mathrm{cand2}}.
\]

The notation `Sec` is deliberately withheld until an independent
section-to-base theorem is proved.

## Why this candidate

The candidate is not chosen because it is known to succeed. It is the unique
non-extremal carrier cell that changes the source/target partition family while
preserving every declared continuity field of the first realization.

It attacks three facts that were accidental in P28.5:

1. the rank-five source partition changes from `(2,2,1,1,1)` to
   `(3,1,1,1,1)`;
2. the lower target partition changes from `(2,2,2,1)` to `(3,2,1,1)`;
3. the upstream `Sigma_6` realization changes from `p^2d` to `d`.

At the same time it does not introduce a new ambient size, kernel type, or
interaction vocabulary.

## Preregistered hostile questions

The second realization is intended to falsify, not merely confirm, the first
one.

1. **H1 -- handoff.** Does section return again require a non-identity typed
   handoff?
2. **H2 -- boundary.** Does the normalized action-relative boundary still
   support exact liftability?
3. **H3 -- generators.** Do `TRANSPORT`, `RETURN`, and `FUSION` still cover
   every exact lift?
4. **H4 -- quantifier.** Does the future-free
   `forall C exists m exists x` return statement still hold?

None of these questions is evaluated by the selection artifact.

## Required two-stage continuation

The experiment must proceed in this order.

1. Construct future-free menus and exact lifts from the frozen 48-context
   rank-four carrier. Freeze and digest them before evaluating `Good_4` against
   the independently defined exact low-rank base.
2. Only if the first stage certifies
   `Sec_4,cand2^(7) -> P_<=3^(7)`, define and freeze the corresponding
   rank-five source/menu/lift data. Evaluate `Good_5` against the new lower
   authority only after that second freeze.

The desired independent chain is therefore

\[
 \operatorname{Sec}^{(7)}_{5,\mathrm{cand2}}
 \longrightarrow
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand2}}
 \longrightarrow
 P_{\le3}^{(7)},
\]

but no arrow in this display is claimed by the present artifact.

## Frozen boundaries

- The 562 carrier keys are future-free; their historical successful-cover
  menus are not imported.
- No best completion or winning channel is selected.
- Internal operation boundaries have no checkpoint authority.
- A second non-identity handoff would satisfy the promotion gate for adding
  typed handoff to the general return schema; one example alone did not.
- Failure of this candidate reopens mechanism or section selection, not the
  Paper XXVII interface, unless a theorem-relevant observable itself fails to
  descend.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_select_second_rank5_return_candidate.py
python experiments/synchronizing_automata/validation/validate_paper28_second_rank5_return_candidate.py
```

The artifact is
`results/paper28_second_rank5_return_candidate_selection_v1.json.gz`. Its JSON
receipt binds the complete inherited pilot input and the local source closure.
