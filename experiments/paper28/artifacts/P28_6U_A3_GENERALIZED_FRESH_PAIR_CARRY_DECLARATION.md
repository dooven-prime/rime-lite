# P28.6u-A3: Generalized Fresh-Pair Carry Declaration

## Status

The fourth theorem-facing rank-four mechanism schema is declared from the
tagged disjoint union

\[
 48\ \text{cand2 FPC provenances}
 \ \sqcup\
 35\ \text{ext unsupported provenances}.
\]

The exact pooled domain has 83 rows. No component-completion artifact,
Good evaluator, lower-section membership, successful receipt, or winner is
loaded.

## Phase order

\[
\begin{aligned}
 &\text{load the 48 frozen FPC-supported cand2 provenances}\\
 &\quad\sqcup\text{ the 35 frozen projectable-but-unsupported ext provenances}\\
 &\longrightarrow \text{derive anonymous exact role profiles}\\
 &\longrightarrow \text{freeze the anonymous-profile digest}\\
 &\longrightarrow \text{freeze the future-free branch formula}\\
 &\longrightarrow \text{assign the identifier GFPC}\\
 &\longrightarrow \text{record schema subsumption.}
\end{aligned}
\tag{A3-Order}
\]

The frozen anonymous-profile digest is

    0ab1d2993b9770938d13fcdd9c04abdc98be59c001311c18399f7cbb0627d094

## Anonymous role equation

For a projectable provenance \(\kappa_4^{\rm ISE}\), the pooled rows share
exactly the following source-addressed relation:

\[
\boxed{
\begin{aligned}
 &|\Pi^\uparrow|=5,\qquad |\Pi_C|=4,\\
 &\exists x\ne y\in\Pi^\uparrow,\qquad |x|=|y|=1,\\
 &e\text{ has terminal strict fusion }x\sqcup y=F_{\rm ent},\\
 &|F_{\rm ent}|=2,\qquad
 \eta(F_{\rm ent})=\operatorname{Dist}(\chi_4),\\
 &\text{all three packets in }\Pi^\uparrow\setminus\{x,y\}
 \text{ carry atomwise under }\eta,\\
 &\operatorname{Dist}(\chi^\uparrow)
 \in\Pi^\uparrow\setminus\{x,y\}
 \text{ and carries atomwise},\\
 &\Pi_C=
 \eta\!\left((\Pi^\uparrow\setminus\{x,y\})\cup\{F_{\rm ent}\}\right).
\end{aligned}}
\tag{GFPC-Anonymous}
\]

The existential role witnesses are retained. No uniqueness of the
\((x,y)\) decomposition is assumed.

The implementation verifies the packet equation twice: first on the exact
actual target packets, then after applying the F3-certified handoff to the
theorem-facing \(\Pi_C\). This matters on the extremal carrier, where all 35
handoffs are non-identity atom bijections.

## Hostile variation survived

All 83 rows satisfy (GFPC-Anonymous):

| tagged source | input rows | anonymous equation passes |
|---|---:|---:|
| cand2 FPC | 48 | 48 |
| ext unsupported | 35 | 35 |
| **pooled** | **83** | **83** |

The two surfaces deliberately disagree on the following anatomy:

| field | cand2 | ext |
|---|---|---|
| source partition | \((3,1,1,1,1)\) | \((2,2,1,1,1)\) |
| current partition | \((3,2,1,1)\) | \((2,2,2,1)\) |
| background masses | \((3,1,1)\) | \((2,2,1)\) |
| incoming distinguished mass | 3 | 2 |
| handoff | identity | atom bijection |

Therefore none of those fields belongs to the new branch key. This omission
is a schema abstraction, not an existence theorem for arbitrary background
masses:

\[
 \boxed{
 \text{branch key ignores background masses}
 \ \not\Longrightarrow\
 \text{all background masses are realizable or projectable}.}
\tag{GFPC-RealizabilityFirewall}
\]

## Declared schema

Only after the anonymous profile is frozen do we assign the name
**Generalized Fresh-Pair Carry** (GFPC):

\[
\boxed{
\operatorname{RelevantBranch}_{\rm GFPC}^{\rm ISE}
(C,d,\kappa_4^{\rm ISE})
\iff
\text{the clauses of }(\mathrm{GFPC\mbox{-}Anonymous})\text{ hold}.}
\tag{GFPC-Branch}
\]

The branch formula explicitly does not read:

- background packet masses or either packet partition;
- incoming distinguished mass;
- literal identity of the handoff;
- selected word, length, surplus, debt, cyclic placement, or kernel offsets;
- Good, LocalReturn, lower-section membership, a successful endpoint, or a
  winner;
- a historical mechanism label.

The declared historical family is now

\[
\boxed{
 \mathfrak G_4^{(3)}
 =\{\operatorname{OW},\operatorname{FPC},
 \operatorname{PEC},\operatorname{GFPC}\}.}
\tag{GFPC-Family3}
\]

FPC remains a frozen historical theorem object. It is not retroactively
broadened.

## Mechanism-schema subsumption

For branch schemas define

\[
 g\preceq h
 \iff
 \forall(C,d,\kappa),\quad
 \operatorname{RelevantBranch}_g^{\rm ISE}(C,d,\kappa)
 \Longrightarrow
 \operatorname{RelevantBranch}_h^{\rm ISE}(C,d,\kappa).
\tag{Schema-Subsumption}
\]

The FPC clauses imply the GFPC clauses by weakening the fixed background
partition and incoming-heavy requirements while retaining the exact
singleton-pair fusion, current distinguished role, three-packet carry, and
typed handoff. Hence

\[
 \boxed{\operatorname{FPC}\preceq\operatorname{GFPC}.}
\tag{FPC-GFPC}
\]

The inclusion is strict on the declared fixed scopes: all 48 old FPC rows
support GFPC, while the 35 ext rows support GFPC and fail FPC.

Schema subsumption is only branch-domain inclusion. It does not inherit
component completion:

\[
 \boxed{
 \operatorname{FPC}\preceq\operatorname{GFPC}
 \ \not\Longrightarrow\
 \text{FPC completion proves GFPC completion}.}
\tag{Subsumption-CompletionFirewall}
\]

The reduced view

\[
 \{\operatorname{OW},\operatorname{GFPC},\operatorname{PEC}\}
\]

is recorded only as a candidate compression. No minimal-family theorem is
claimed, and the historical family (GFPC-Family3) is preserved.

## Component completion

P28.6u-C3 now independently evaluates generic carrier-specific LocalReturn
on the cand2 and ext frozen adapters. It obtains 48/48 and 35/35 completed
sources, respectively, and combines them only as a tagged disjoint union.
The old FPC completion is not a proof input; its cand2 counts are used only as
a post-freeze regression checksum.

The pooled relation retains 1,955 failed exact lifts, four fully failed
channels, and 67 mixed channels. Hence GFPC completion remains existential and
does not add a successful-path normal form to the branch declaration. See
[`P28_6U_C3_TAGGED_GFPC_COMPONENT_COMPLETION.md`](P28_6U_C3_TAGGED_GFPC_COMPONENT_COMPLETION.md).

P28.6u-D now closes the 165-context tagged fixed-`n=7` multi-carrier theorem
using GFPC on ext/cand2 and PEC on cand3/cand4/cand5. This is a reduced
sufficient cover, not a minimal-family theorem. See
[`P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md`](P28_6U_D_TAGGED_FIXED_SCOPE_MECHANISM_COVER.md).

## Replay

    python experiments/synchronizing_automata/paper28_declare_fourth_mechanism_schema.py
    python experiments/synchronizing_automata/validation/validate_paper28_fourth_mechanism_schema.py

The artifact is
results/paper28_fourth_mechanism_schema_declaration_v1.json.gz. Its SHA-256
digest is
6c2cc844832d8285c64a4380a77234d4f6788d6e8779c20f4c6a4adc3e7704c1.

## Claim boundary

This declaration proves fixed-\(n=7\) support of the 83-row pooled domain and
the branch-domain subsumption \(\operatorname{FPC}\preceq\operatorname{GFPC}\).
The separate C3 theorem now proves tagged fixed-scope GFPC completion. Neither
result proves completion inheritance, minimality of a reduced family,
realizability of arbitrary background masses, all-\(n\) projectability or
support cover, equality with \(\Lambda_4^{\rm complete}(C)\), or F5.
