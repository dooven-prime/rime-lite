# P28.6u-A2: Pair-Extension Carry Declaration

## Status

The third theorem-facing rank-four mechanism schema is declared. It is earned
from the tagged union of all 82 exact projectable-but-unsupported cand3,
cand4, and cand5 provenances isolated by P28.6u-B1.

The construction order is

\[
\boxed{
\text{pooled unsupported provenance}
\longrightarrow
\text{anonymous cross-carrier role profile}
\longrightarrow
\text{profile digest}
\longrightarrow
\text{branch formula}
\longrightarrow
\text{name }\operatorname{PEC}.}
\tag{PEC-Order}
\]

The resulting declared family is

\[
 \boxed{
 \mathfrak G_4^{(2)}
 =\{\operatorname{OW},\operatorname{FPC},\operatorname{PEC}\},}
 \tag{PEC-Family2}
\]

where `PEC` means **Pair-Extension Carry**.

## Cross-carrier role equation

Let

\[
 \kappa_4^{\rm ISE}
 =(C^\uparrow,e,\Pi^\uparrow,\Pi_C,F_4,\eta,\mathsf{sel})
\]

be a provenance record in the complete frozen projectability fiber. On this
branch write `F_ent:=F_4`. The provenance-sensitive predicate is

\[
\boxed{
\begin{aligned}
 &\operatorname{RelevantBranch}^{\rm ISE}_{\operatorname{PEC}}
 (C,d,\kappa_4^{\rm ISE}) :\iff{}\\
 &\quad \exists P,Q,x\in\Pi^\uparrow\text{ distinct such that}\\
 &\quad |\Pi^\uparrow|=5,\qquad |\Pi_C|=4\\
 &\quad\land
 |P|=|Q|=2,\quad |x|=1,\quad P,Q,x\text{ distinct}\\
 &\quad\land
 e\text{ is an exact selected entry whose terminal strict fusion is }
 P\sqcup x=F_{\rm ent}\\
 &\quad\land |F_{\rm ent}|=3,\qquad
 \eta(F_{\rm ent})=\operatorname{Dist}(\chi_4)\\
 &\quad\land
 Q\text{ is not fused by }e\text{ and survives atomwise}\\
 &\quad\land
 \Pi_C=\eta\!\left((\Pi^\uparrow\setminus\{P,x\})
 \cup\{F_{\rm ent}\}\right)\\
 &\quad\land
 \operatorname{Dist}(\chi^\uparrow)\in\{P,Q\},
 \text{ with its consumed-or-carried update certified exactly}\\
 &\quad\land
 \eta\text{ certifies preservation of the }F_{\rm ent},Q,
 \text{ and spectator typed roles.}
\end{aligned}}
\tag{PEC-Branch}
\]

The role decomposition is existential and relation-valued. No uniqueness of
`P,Q,x` is assumed. On the present fixed scopes the exact terminal fusion and
the complementary-pair condition produce one witness, but that is a replay
fact rather than part of the branch syntax.

Thus the mechanism extends one source-addressed mass-two packet by a singleton
to create the current distinguished mass-three packet, while carrying a
different mass-two packet into the rank-four context.

The incoming distinguished packet may be either the fused pair `P` or the
carried pair `Q`. The exact ancestry update records which case occurs; the
polarity is not a branch clause.

## Future-free field ownership

The branch reads only:

| field | owner |
|---|---|
| current distinguished packet and rank-four context | typed source `C` |
| upstream packets and selected exact entry | `kappa_4^ISE` |
| fusion parents, packet atoms, and ancestry update | exact replay in `kappa_4^ISE` |
| preservation of entry, carried-pair, and spectator roles | F3-certified handoff `eta` |

It does not read:

- fresh-consumption polarity as a required value;
- the selected word;
- corridor length;
- surplus, debt, or tail budget;
- coordinates or kernel-offset profiles;
- literal identity of the handoff;
- `Good`, `LocalReturn`, lower-section membership, a successful endpoint, or
  a winner;
- a historical mechanism label.

The common-profile payload is frozen before `PEC` is assigned. Its digest is

```text
51b360229d9be2a83a261f024c380b9aa445608241f266f06e5326af8024b541
```

## Hostile variation audit

The 82 supporting provenances retain the deliberately varied anatomy:

| observable | histogram |
|---|---|
| incoming pair role | carried `36`, fused `46` |
| ancestry participation | none `36`, first-only `46` |
| selected length | `3:72`, `5:10` |
| selected surplus | `2:72`, `0:10` |
| selected word | `001:72`, `01001:10` |

They also contain 15 source role-placement profiles and 32 target offset
profiles. The declaration therefore uses the exact pair-extension/carry
equation rather than one carrier's serialization anatomy.

## Fixed-scope support result

Define

\[
\begin{aligned}
 &\operatorname{PECSupp}_n(C,\kappa_4^{\rm ret};d):\iff{}\\
 &\quad \exists\kappa_4^{\rm ISE}
 \in\mathcal P_{\rm ISE}(C,\kappa_4^{\rm ret}):
 \operatorname{RelevantBranch}^{\rm ISE}_{\operatorname{PEC}}
 (C,d,\kappa_4^{\rm ISE}).
\end{aligned}
\tag{PEC-Support}
\]

The post-profile support audit gives

```text
cand3  36 / 36 PEC-supported
cand4  36 / 36 PEC-supported
cand5  10 / 10 PEC-supported
pooled 82 / 82 PEC-supported
```

Hence `mathfrak G_4^(2)` closes the exact support gap exposed by P28.6u-B1.
This is support classification only. No rank-four return evaluator is loaded,
and no PEC component-completion theorem is inferred from the already known
fixed-scope return results.

## Next theorem layer

The separate component target is

\[
\boxed{
 (C,\kappa_4^{\rm ret})\in\operatorname{Sec}_4
 \land \operatorname{PECSupp}_n(C,\kappa_4^{\rm ret};d)
 \Longrightarrow
 \mathcal G_{\operatorname{PEC}}(C,\kappa_4^{\rm ret};d)
 \ne\varnothing.}
\tag{PEC-Completion}
\]

Any fixed-scope completion audit must reuse generic `LocalReturn_4` semantics
and remain separate from this declaration.

That separate tagged audit is now complete in
[`P28_6U_C2_TAGGED_PEC_COMPONENT_COMPLETION.md`](P28_6U_C2_TAGGED_PEC_COMPONENT_COMPLETION.md).
It proves generic fixed-scope PEC completion independently on cand3, cand4,
and cand5 while retaining all carrier tags and failed exact lifts. This does
not change the support declaration or promote it to all `n`.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_declare_third_mechanism_schema.py
python experiments/synchronizing_automata/validation/validate_paper28_third_mechanism_schema.py
```

The artifact is
`results/paper28_third_mechanism_schema_declaration_v1.json.gz`. Its SHA-256
digest is
`888708418730727d2ce32468db53c1d1fb952b8dbca7bd41e4e78550496f56dc`.

## Claim boundary

This declaration proves a future-free provenance-sensitive support schema and
fixed-`n=7` support on cand3/cand4/cand5. It does not prove PEC completion,
all-`n` projectability, all-`n` support cover, completeness of
`{OW,FPC,PEC}`, identification with a historical mechanism, equality of the
fixed-scope adapter with `Lambda_4^complete(C)`, or F5. Fixed-scope PEC
completion is a separate downstream theorem in P28.6u-C2.
