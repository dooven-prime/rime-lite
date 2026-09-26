# P28.4 Future-Free Section-to-Base Menu

## Status

This note records the first fixed-scope connection between the Paper XXVII
proof interface and the Paper XXVIII boundary-generator relation. The scope is
the 35 released extremal rank-four `n=7` section contexts. It is not the full
15,120-context inherited scope and not a return theorem above rank four.

The reusable theorem contract extracted from this audit is frozen in
[`P28_4A_FUTURE_FREE_SECTION_RETURN_SCHEMA.md`](P28_4A_FUTURE_FREE_SECTION_RETURN_SCHEMA.md).
The separation between structural assumptions and finite-carrier facts is
recorded in
[`P28_4B_ASSUMPTION_EXTRACTION.md`](P28_4B_ASSUMPTION_EXTRACTION.md).

The finite result is:

\[
\boxed{
\forall C\in\operatorname{Sec}^{(7)}_{4,\mathrm{ext}},\quad
\exists m\in\mathfrak M(C),\quad
\exists \widetilde m\in\operatorname{Lift}(C,m):
\partial^+\widetilde m\in P_{\le3}^{(7)}.}
\]

Menu construction is future-free. Exact low-rank success is evaluated only
after the menu payload and its digest have been frozen.

Equivalently, with success defined as the derived predicate

\[
\operatorname{Good}_4(C,m)
\iff
\exists x\in\operatorname{Lift}(C,m):
\partial^+x\in P_{\le3}^{(7)},
\]

the theorem is `\forall C\,\exists m:\operatorname{Good}_4(C,m)`. The
predicate `Good_4` is not present in the menu key or constructor.

## Three typed levels

The audit keeps three objects separate.

1. **Section context.** A declared recursive proof state from the released
   35-context extremal carrier.
2. **Abstract generator-path channel.** A future-free interaction skeleton,
   together with its relation-valued accounting refinements.
3. **Exact lift.** A tied endpoint-shortest source-addressed receipt whose
   word factors through the P28.3 typed generator graph.

The abstract path channel is not selected by checking whether its target lies
in `P_{<=3}`. A channel may have both successful and unsuccessful exact lifts,
and an entire channel may fail. The theorem needs only one successful channel
per section source.

## Future-free menu

For every declared source context `C`, the constructor:

- enumerates all admissible tied endpoint-shortest local receipts;
- projects them to the future-free interaction skeleton;
- retains the accounting refinements as a set-valued relation;
- binds each channel to its exact generator-path realization fiber.

It does not read `target_in_exact_P_le3`, winning labels, Bellman values, reset
coaccessibility, or producer-selected preferred witnesses.

The frozen menu has:

| object | count |
| --- | ---: |
| declared section sources | 35 |
| abstract generator-path channels | 173 |
| accounting refinements | 864 |
| exact lifted receipts | 4,182 |
| maximum channels at one source | 8 |

The per-source menu-size distribution is

\[
1\times2,\quad6\times3,\quad5\times4,\quad12\times5,
\quad6\times6,\quad3\times7,\quad2\times8.
\]

This is a fixed-scope B0 statement only. It proves neither a rank-controlled
B1 bound nor a uniform B2 bound.

## Post-construction success certification

After freezing the menu, the exact low-rank evaluator gives:

| certification object | count |
| --- | ---: |
| channels with at least one successful exact lift | 169 |
| channels with no successful exact lift | 4 |
| successful exact lifts | 2,329 |
| unsuccessful exact lifts | 1,853 |
| distinct certified low-rank targets | 303 |

All 35 source contexts have at least one successful channel. The four failed
channels are retained as hostile controls. They are `(6,1)` heavy-target
schemas in four source contexts; their presence shows that the result is
existential rather than universal over menu members.

## Internal boundary exclusion

The 4,182 exact lifts traverse `8,438` replay-certified local typed states.
Of these, `8,020` occur only internally rather than as stored receipt
endpoints. The type audit verifies:

\[
\texttt{menu\_source}\subseteq
\operatorname{Sec}^{(7)}_{4,\mathrm{ext}},
\]

\[
\texttt{recursive\_target}\subseteq P_{\le3}^{(7)},
\]

and

\[
\boxed{
\#\{\text{internal-only states exported as recursive checkpoints}\}=0.}
\]

Internal boundaries remain available only inside exact lifted paths. Exact
replay does not confer recursive checkpoint authority.

## Relation to the historical mechanism names

The menu is not branched by `repayment`, `heavy comb`, `bridge`, `B2`, or
`fallback` names. Those are predicates on generator paths and accounting:

\[
\operatorname{Repay}(m)
\iff S_1<0\ \text{ and }\ S_1+S_2\ge0,
\]

while `HeavyChain(m)` records whether the second fusion consumes the fresh
packet created by the first. P28.3's ten repayment/non-heavy hostile receipts
show why these predicates must remain distinct.

## Replay

Produce the deterministic artifact and receipt:

```powershell
python experiments/synchronizing_automata/paper28_audit_section_return_menu.py
```

Fully recompute the menu, generator lifts, post-construction certification,
internal-boundary exclusion, and receipt binding:

```powershell
python experiments/synchronizing_automata/validation/validate_paper28_section_return_menu.py
```

## Claim boundary

This result proves a future-free section-to-**base** return on the declared
35-context extremal scope. It does not prove:

- success of every menu member;
- the full 15,120-context inherited theorem in this generator language;
- a section-to-section return above rank four;
- an all-rank constructor;
- B1 or B2 boundedness;
- Forced FFS.
