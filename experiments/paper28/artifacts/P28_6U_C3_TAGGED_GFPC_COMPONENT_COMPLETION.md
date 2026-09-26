# P28.6u-C3: Tagged Fixed-Scope GFPC Component Completion

## Status

Generalized Fresh-Pair Carry is complete on the two independently frozen
fixed-`n=7` carriers

\[
 \operatorname{Sec}_{4,\mathrm{cand2}}^{(7)},
 \qquad
 \operatorname{Sec}_{4,\mathrm{ext}}^{(7)}.
\]

The relations remain carrier tagged. C3 does not identify the cand2 and ext
adapters, and it does not inherit completion from the older FPC theorem.

## Success-free ext adapter

The historical extremal menu audit stored the future-free menu and the later
`Good_4` certification in one artifact. Before C3, a separate adapter was
therefore frozen from the bound seed catalog and generator factorization:

```text
paper28_ext_rank4_section_candidate_v1.json.gz
```

Its output contains 35 sources, 173 channels, and 4,182 exact lifts. Every
`observables` field is removed, `Good_4=NOT_RUN`, and the evaluator is absent.
The complete-menu digest and all 35 source-menu digests agree with the ext B2
return certificates.

## Generic return semantics

For carrier tag \(j\in\{\mathrm{cand2},\mathrm{ext}\}\), define

\[
\boxed{
\begin{aligned}
 \operatorname{LocalReturn}_{4,j}^{\rm fs}(C,d,\kappa)
 \iff \exists m,x:\;&
 x\in\operatorname{Lift}_{4,j}^{\rm fs}(C,m)\\
 &\land \widehat{\partial^+x}\in P_{\le3}^{(7)}.
\end{aligned}}
\tag{C3-LocalReturn}
\]

No GFPC-specific continuation condition is added. In particular, completion
does not require fixed background masses, a fixed handoff mode, later use of
the fresh packet, a fixed word, length, surplus, debt, or offset profile.

The derived relation is

\[
 \mathcal G_{\rm GFPC}^{\rm fs,j}
 =\left\{\kappa\in\mathcal P_{\rm ISE}^{j}:
 \operatorname{RelevantBranch}_{\rm GFPC}^{\rm ISE}(\kappa)
 \land
 \operatorname{LocalReturn}_{4,j}^{\rm fs}(\kappa)\right\}.
\]

The pooled object is only the tagged disjoint union

\[
\boxed{
 \mathcal G_{\rm GFPC}^{\rm fs,pool}
 =
 \{\mathrm{cand2}\}\times\mathcal G_{\rm GFPC}^{\rm fs,cand2}
 \sqcup
 \{\mathrm{ext}\}\times\mathcal G_{\rm GFPC}^{\rm fs,ext}.}
\tag{C3-TaggedUnion}
\]

## Phase order

The evaluator enforces

\[
\boxed{
\begin{aligned}
 &\text{freeze GFPC support}\\
 &\to\text{freeze the cand2 and success-free ext relations}\\
 &\to\text{freeze the tagged completion-input digest}\\
 &\to\text{define generic carrier-specific LocalReturn}\\
 &\to\text{open exact }P_{\le3}^{(7)}\\
 &\to\text{evaluate every exact lift without selecting a winner.}
\end{aligned}}
\tag{C3-Order}
\]

The frozen completion-input digest is

```text
cb81c756dc176102bce7a40dca26c7e792a7d940712faf3d5e73ff0024e4665e
```

The older FPC completion, historical `Good_4` outputs, and rank-five return
evaluators are forbidden proof inputs. Historical counts are opened by the
validator only after deterministic reconstruction and receipt closure pass.

## Completion theorem

The two carrier-tagged statements are

\[
\boxed{
 \forall C\in\operatorname{Sec}_{4,\mathrm{cand2}}^{(7)},\quad
 \operatorname{GFPCSupp}_7(C)
 \Longrightarrow
 \mathcal G_{\rm GFPC}^{\rm fs,cand2}(C)\ne\varnothing,}
\]

and

\[
\boxed{
 \forall C\in\operatorname{Sec}_{4,\mathrm{ext}}^{(7)},\quad
 \operatorname{GFPCSupp}_7(C)
 \Longrightarrow
 \mathcal G_{\rm GFPC}^{\rm fs,ext}(C)\ne\varnothing.}
\tag{GFPC-FS-Tagged-Completion}
\]

The exact audit is

| carrier | sources completed | channels returning | channels failed | mixed channels | exact lifts returning | exact lifts failed |
|---|---:|---:|---:|---:|---:|---:|
| `cand2` | 48/48 | 401 | 0 | 8 | 9,498 | 102 |
| `ext` | 35/35 | 169 | 4 | 59 | 2,329 | 1,853 |
| **tagged pool** | **83/83** | **570** | **4** | **67** | **11,827** | **1,955** |

The two complete relations contain 13,782 exact lifts in 574 channels and
reach 1,596 certified tagged targets. Thirty-six tagged sources contain a
mixed channel. All four fully failed channels and all 1,955 failed lifts remain
in the theorem object.

Thus schema subsumption and completion are now cleanly separated:

\[
 \operatorname{FPC}\preceq\operatorname{GFPC}
 \quad\text{was proved in A3, while C3 independently proves}\quad
 \operatorname{GFPC}\text{ completion on cand2/ext}.
\]

## Replay

```powershell
python experiments/synchronizing_automata/paper28_prepare_ext_rank4_section_candidate.py
python experiments/synchronizing_automata/validation/validate_paper28_ext_rank4_section_candidate.py
python experiments/synchronizing_automata/paper28_evaluate_gfpc_component_completion.py
python experiments/synchronizing_automata/validation/validate_paper28_gfpc_component_completion.py
```

The C3 artifact is
`results/paper28_gfpc_component_completion_v1.json.gz`; its SHA-256 digest is
`59de702c5285d7739a70eac3f3f0bdcfafc7a72e14517b39454bea49bb5ab3af`.

## Multi-carrier closure

P28.6u-D now closes the tagged fixed-`n=7` multi-carrier theorem on

\[
 \mathcal D_4^{(7)}
 =\operatorname{Sec}_{4,\mathrm{ext}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand2}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand3}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand4}}^{(7)}
 \sqcup\operatorname{Sec}_{4,\mathrm{cand5}}^{(7)},
\]

using GFPC for ext/cand2 and PEC for cand3/cand4/cand5. All 165 tagged sources
are covered. This is a **reduced sufficient cover**, not a minimal-family
claim. See
[`P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md`](P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md).

## Claim boundary

C3 proves tagged fixed-`n=7` GFPC component completion on cand2 and ext. It
does not prove completion inheritance, all-`n` GFPC, equality with
\(\Lambda_4^{\rm complete}(C)\), an untagged relation, a successful-path
normal form, minimality of \(\{\mathrm{GFPC},\mathrm{PEC}\}\), or all-rank F5.
