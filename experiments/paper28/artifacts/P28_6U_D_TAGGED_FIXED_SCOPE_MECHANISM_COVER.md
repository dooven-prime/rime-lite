# P28.6u-D: Tagged Fixed-Scope Mechanism-Cover Closure

## Status

The five declared fixed-`n=7` admitted rank-four carriers now have a closed
tagged mechanism cover. Define

\[
\begin{aligned}
 \mathcal D_4^{(7)}={}&
 \operatorname{Sec}_{4,\mathrm{ext}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand2}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand3}}^{(7)}\\
 &\sqcup\operatorname{Sec}_{4,\mathrm{cand4}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand5}}^{(7)}.
\end{aligned}
\]

It contains

\[
 35+48+36+36+10=165
\]

tagged admitted contexts.

## Reduced sufficient cover

The frozen carrier assignment is

| carrier | completed schema |
|---|---|
| `ext`, `cand2` | GFPC |
| `cand3`, `cand4`, `cand5` | PEC |

The resulting good-provenance relation is the tagged disjoint union

\[
\boxed{
 \mathcal G_{\rm red}^{\rm fs}
 =
 \bigl(\{\operatorname{GFPC}\}\times
 \mathcal G_{\rm GFPC}^{\rm fs}\bigr)
 \sqcup
 \bigl(\{\operatorname{PEC}\}\times
 \mathcal G_{\rm PEC}^{\rm fs}\bigr).}
\tag{D-ReducedCover}
\]

This is a **reduced sufficient cover**, not a minimal-family theorem. The
declaration history

\[
 \mathfrak G_4^{(3)}
 =\{\operatorname{OW},\operatorname{FPC},
 \operatorname{PEC},\operatorname{GFPC}\}
\]

is preserved. Nothing excludes a future schema that subsumes both GFPC and
PEC.

## Theorem composition only

The closure artifact loads the frozen C3 GFPC and C2 PEC component theorems,
freezes their carrier-to-mechanism assignment, and forms the tagged union. It
does not open a low-rank oracle, rerun a component evaluator, inspect a
historical `Good` artifact, or select a winner.

Thus the proof is exactly

\[
\boxed{
 \text{projectability}
 +\text{support classification}
 +\text{component completion}
 \Longrightarrow
 \text{fixed-}n=7\text{ multi-carrier F5 on }\mathcal D_4^{(7)}.}
\tag{D-Composition}
\]

## Exact audit

\[
\boxed{
 \forall(j,C)\in\mathcal D_4^{(7)},\qquad
 \mathcal G_{\rm red}^{\rm fs}(j,C)\ne\varnothing.}
\tag{D-Cover}
\]

The aggregate relation retains the full finite controls:

| quantity | count |
|---|---:|
| tagged admitted/completed sources | 165/165 |
| channels | 1,051 |
| returning channels | 1,046 |
| failed channels retained | 5 |
| mixed channels retained | 186 |
| exact lifts | 26,995 |
| returning exact lifts | 23,177 |
| failed exact lifts retained | 3,818 |
| certified tagged targets | 3,162 |

The theorem is existential over mechanisms, provenances, channels, and exact
lifts. Failed sibling mechanisms or relation rows do not refute the return.

The frozen closure-input digest is

```text
596cf08bba67416b76b46e519c09331069350d78500ab039841d63375e3c0ebf
```

## Replay

```powershell
python experiments/synchronizing_automata/paper28_close_fixed_scope_mechanism_cover.py
python experiments/synchronizing_automata/validation/validate_paper28_fixed_scope_mechanism_cover.py
```

The artifact is
`results/paper28_fixed_scope_mechanism_cover_closure_v1.json.gz`; its SHA-256
digest is
`20073b8c096be4085ef28d6199ebe009d3333cd75078e029c003a1b670edb46f`.

## Claim boundary

This closes only the declared fixed-`n=7`, rank-four, five-carrier universe.
It does not prove minimality of \(\{\mathrm{GFPC},\mathrm{PEC}\}\), an
all-`n` projectability theorem, equality of any adapter with
\(\Lambda_4^{\rm complete}(C)\), all-`n` component completion, or all-rank F5.
This D-stage composition itself makes no such identification. P28.6v later
proves fixed-scope one/two-segment canonical path alignment for every adapter
macro lift, not equality with the single first-exit relation, while retaining
the all-`n` projectability and origin theorems as separate open obligations.
