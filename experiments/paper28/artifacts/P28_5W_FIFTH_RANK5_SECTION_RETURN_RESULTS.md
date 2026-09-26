# P28.5w: Fifth Rank-Five Section Return

## Status

An independent evaluator has applied the frozen `Sec_4,cand5^(7)` authority to
the complete P28.5v rank-five relation. It did not rebuild sources, menus, or
lifts and did not select a winning channel.

Before loading lower-section membership, the evaluator rechecks the
pre-evaluation relation equality

\[
 \operatorname{Lift}_5(C,m)\cap\{L=3\}=\varnothing
\]

for every source and every channel. Hence on this frozen relation

\[
 \operatorname{Good}^{\ne3}_5(C,m)
 \iff
 \operatorname{Good}_5(C,m)
\]

independently of the subsequent success values.

## Exact result

```text
source contexts                         10
ordinary successful sources             10
non-length-three successful sources     10

abstract channels                       28
ordinary successful channels            10
non-length-three successful channels    10
failed channels                         18

exact lifts                             62
ordinary successful exact lifts         10
non-length-three successful lifts       10
unsuccessful exact lifts                 52
selected Sigma_5 successful lifts       10
```

Every source has exactly one successful channel. All ten successful handoffs
are literal identity handoffs to `Sec_4,cand5^(7)`.

The exact-lift length/success table is

```text
L    target in Sec_4,cand5    target outside
5             10                    10
6              0                     6
7              0                     9
8              0                     9
9              0                    18
```

Thus all successful lifts have length five. The longer exact alternatives are
retained but do not enter the lower section. More importantly for the hostile
claim, the complete exact relation contains no length-three lift at all.

The fixed-scope theorem is therefore

\[
 \forall C\in\operatorname{Sec}^{(7)}_{5,\mathrm{cand5}},\qquad
 \exists m\in\mathfrak M_5(C),\quad
 \exists x\in\operatorname{Lift}_5(C,m):
 \widehat{\partial^+x}\in
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand5}}
 \quad\text{and}\quad L(x)\ne3.
\]

Together with P28.5u this closes

\[
 \operatorname{Sec}^{(7)}_{5,\mathrm{cand5}}
 \xrightarrow{L\ne3}
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand5}}
 \longrightarrow P^{(7)}_{\le3}.
\]

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_fifth_rank5_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_fifth_rank5_section_return.py
```

The artifact is
`results/paper28_fifth_rank5_section_return_evaluation_v1.json.gz`, with
SHA-256 `b357ab66892124ec2a29840529a7e61b0d0e68495bc5bf168f67e9b2522367a2`.

## Claim boundary

This proves on the five declared fixed-`n=7` composed-return surfaces that
length three is not necessary for positive-rank section return. It does not
prove that every non-length-three carrier succeeds, isolate length as the
cause of any future failure, cover the full inherited 15,120-context scope,
or establish an all-rank return theorem. The fifth selector also changed the
relative kernel offsets from `[0,2]` to `[0,6]`; that matters to the
interpretation of a hypothetical failure, although the present realization
succeeds.

The declared fixed-`n=7` anatomy-hostile program stops here. Its next task is
all-rank F5 sufficient-hypothesis extraction, not selection of a sixth local
carrier.
