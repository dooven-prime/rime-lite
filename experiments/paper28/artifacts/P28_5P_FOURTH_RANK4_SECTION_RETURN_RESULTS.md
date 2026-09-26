# P28.5p: Fourth Rank-Four Section Return

## Status

An independent evaluator has applied exact low-rank membership to the frozen
P28.5o menu and exact-lift relation. It did not rebuild menus or lifts and did
not select a winning channel.

## Exact result

```text
source contexts                    36
successful sources                 36
hostile sources                     0

abstract channels                 252
channels with a successful lift   252
failed channels                     0

exact lifts                     6,498
successful exact lifts          5,937
unsuccessful exact lifts          561
mixed success/failure channels     38
certified target contexts         768
```

Thus

\[
 \forall C\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand4}},\qquad
 \exists m\in\mathfrak M_4(C),\quad
 \exists x\in\operatorname{Lift}_4(C,m):
 \partial^+x\in P_{\le3}^{(7)}.
\]

All 252 abstract channels have at least one successful lift, but 561 exact
lifts fail and 38 channels contain both successful and unsuccessful
realizations. Channel success therefore does not collapse the exact fiber to
a deterministic witness.

## Authority and next gate

The evaluation grants fixed-scope authority to
`Sec_4,cand4^(7)` on these 36 typed contexts. Internal operation boundaries
remain excluded from recursive checkpoint authority.

This is not yet a fourth positive-rank composed chain. The matching rank-five
source menu and exact lifts must be frozen before this new lower-section
authority is used to evaluate `Good_5`. Consequently the claim that successful
positive-rank return can consume inherited distinguished ancestry remains open
until that second stage closes.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_fourth_rank4_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_fourth_rank4_section_return.py
```

The evaluation artifact is
`results/paper28_fourth_rank4_section_return_evaluation_v1.json.gz`, with
SHA-256 `ed330003880427ebaf252d6dccb8e42c76dae3e9661340641f0c7c4054744ef7`.

## Claim boundary

The result is an exact fixed-scope section-to-base theorem for the frozen
36-context fresh-consuming carrier. It does not prove the matching rank-five
return, maximality, full inherited-scope coverage, a non-length-three return,
or an all-rank theorem.
