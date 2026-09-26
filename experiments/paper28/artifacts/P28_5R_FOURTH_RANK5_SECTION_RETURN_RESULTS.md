# P28.5r: Fourth Rank-Five Section Return

## Status

An independent evaluator has applied the released `Sec_4,cand4^(7)` authority
to the frozen P28.5q relation. It did not rebuild the source set, menu, or
exact lifts and did not select a winning channel.

Two post-freeze predicates are evaluated separately:

\[
 \operatorname{Good}_5(C,m)
 \iff
 \exists x\in\operatorname{Lift}_5(C,m):
 \widehat{\partial^+x}\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand4}},
\]

and

\[
 \operatorname{Good}^{\mathrm{consume}}_5(C,m)
 \iff
 \operatorname{Good}_5(C,m)
 \text{ has a lift consuming the incoming distinguished packet}.
\]

## Exact result

```text
source contexts                              36
ordinary successful sources                  36
fresh-consuming successful sources           36
hostile sources                                0

abstract channels                           107
ordinary successful channels                 36
fresh-consuming successful channels          36
failed channels                              71

exact lifts                                 252
ordinary successful exact lifts              36
ordinary unsuccessful exact lifts           216
fresh-consuming successful exact lifts       36
fresh-avoiding successful exact lifts          0
selected Sigma_5 successful receipts          36
```

Every source has exactly one ordinary good channel, and that same channel is
fresh-consuming. All 36 successful typed handoffs are literal identity.

The exact-lift cross table is

| | target in `Sec_4,cand4^(7)` | target outside |
| --- | ---: | ---: |
| fresh consumed | 36 | 143 |
| fresh avoided | 0 | 73 |

Thus the fresh-avoiding subrelation is not merely unnecessary for the proof:
on this frozen surface it contains no successful lift at all.

## Fixed-scope theorem

The ordinary F5 return and the stronger hostile statement both hold:

\[
 \forall C\in\operatorname{Sec}^{(7)}_{5,\mathrm{cand4}},\qquad
 \exists m\in\mathfrak M_5(C),\quad
 \exists x\in\operatorname{Lift}_5(C,m):
 \widehat{\partial^+x}\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand4}}
\]

with `x` consuming the incoming distinguished packet. Together with P28.5p,
this closes the fourth composed chain

\[
 \operatorname{Sec}^{(7)}_{5,\mathrm{cand4}}
 \xrightarrow{\text{fresh consumed}}
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand4}}
 \longrightarrow P^{(7)}_{\le3}.
\]

Consequently, avoidance of inherited distinguished ancestry is not necessary
for positive-rank section return on the declared fixed-`n=7` surfaces.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_fourth_rank5_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_fourth_rank5_section_return.py
```

The evaluation artifact is
`results/paper28_fourth_rank5_section_return_evaluation_v1.json.gz`, with
SHA-256 `09e4221506a442c447300c0fdf716ab9f1dd3eee49eb0d9254571b1da7d5087a`.
The receipt binding and deterministic replay both pass.

## Claim boundary

This is a fixed-`n=7`, 36-source hostile realization. It does not prove that
fresh consumption is always available, does not establish a general
rank-five normal form, and does not address non-length-three return. The
remaining controlled anatomy test is `length != 3`.
