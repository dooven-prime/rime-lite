# P28.5u: Fifth Rank-Four Section Return

## Status

An independent evaluator has applied exact low-rank membership to the frozen
P28.5t relation. It did not rebuild menus or lifts and did not select a
winning channel.

## Exact result

```text
source contexts                    10
successful sources                 10
hostile sources                     0

abstract channels                  53
channels with a successful lift    53
failed channels                     0

exact lifts                     1,476
successful exact lifts          1,205
unsuccessful exact lifts          271
mixed success/failure channels     18
certified target contexts         174
```

The good-channel histogram is `4:1, 5:5, 6:4`, equal to the menu-size
histogram: every abstract channel has at least one successful exact lift. The
271 unsuccessful lifts and 18 mixed fibers remain explicit controls against a
deterministic channel interpretation.

Thus

\[
 \forall C\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand5}},\qquad
 \exists m\in\mathfrak M_4(C),\quad
 \exists x\in\operatorname{Lift}_4(C,m):
 \partial^+x\in P^{(7)}_{\le3}.
\]

The evaluation grants fixed-scope authority to `Sec_4,cand5^(7)` on these ten
typed contexts. Internal boundaries remain excluded from checkpoint authority.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_fifth_rank4_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_fifth_rank4_section_return.py
```

The artifact is
`results/paper28_fifth_rank4_section_return_evaluation_v1.json.gz`, with
SHA-256 `23961258aff1ebf976ad67c148229b4506852a56fffb3bb1035eca6079e246de`.

## Claim boundary

This closes only the fifth rank-four section-to-base theorem. It does not yet
construct the matching rank-five relation and therefore does not evaluate
ordinary `Good_5` or `Good_5^non3`. Length-three necessity remains open.
