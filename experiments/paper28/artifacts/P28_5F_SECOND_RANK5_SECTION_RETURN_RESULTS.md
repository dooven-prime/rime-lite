# P28.5f: Second Rank-Five Section Return

## Status

The second fixed-`n=7` realization now supplies the composed chain

\[
 \operatorname{Sec}^{(7)}_{5,\mathrm{cand2}}
 \longrightarrow
 \operatorname{Sec}^{(7)}_{4,\mathrm{cand2}}
 \longrightarrow
 P_{\le3}^{(7)}.
\]

The rank-five arrow was constructed and evaluated in two separate phases. The
source, future-free menu, and exact lift fibers were frozen before the newly
certified lower section was opened for `Good_5` evaluation.

## Phase A: pre-evaluation construction

The source authority is inherited from the frozen P28.5d future-free
`31111__11_TO_3211` selection. Its 48 exact rank-five contexts have partition
`(3,1,1,1,1)`. Membership does not read lower-section success.

For each source, the constructor retains all tied endpoint-shortest
rank-five-to-four receipts and quotients them only by interaction skeleton.
The frozen relation contains:

```text
source contexts               48
future-free channels          96
exact lifts                  195
menu size                      2 for every source
operation kinds               TRANSPORT / RETURN / FUSION
```

The construction-payload digest is
`b79c23f988e00f67f4aa24819948b3a0acff67f19c0c50054bdcf24ffab6d481`.
The complete pre-evaluation artifact digest is
`106f87b804f4a07b647e17a8d6a9c3d82bd711c076a20146cdb3ce817a8b5e0e`.

The lower `Sec_4,cand2^(7)` authority is bound only after this construction
digest has been computed. `Good_5`, target membership, successful-channel
labels, and winner selection are absent from the construction payload.

## Phase B: typed handoff evaluation

The post-freeze evaluator reads the 195 exact lifts and the independently
certified `Sec_4,cand2^(7)` authority. It neither rebuilds the relation nor
selects a best channel. It proves

\[
 \forall C\in\operatorname{Sec}^{(7)}_{5,\mathrm{cand2}},\qquad
 \exists m\in\mathfrak M_5(C),\qquad
 \exists x\in\operatorname{Lift}_5(C,m):
 \partial^+x\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand2}}.
\]

The exact result is:

```text
successful sources            48 / 48
successful channels           48 / 96
unsuccessful channels         48 / 96
successful exact lifts        48 / 195
unsuccessful exact lifts     147 / 195
good channels per source       1
```

Thus every source has exactly one good channel and one failed channel. The
failed half of the frozen menu remains part of the theorem object and prevents
the existential return statement from collapsing into a deterministic
selector.

## Successful realization anatomy

The 48 successful lifts reproduce the selected future-free `Sigma_5` receipts:

```text
word p d^2                  24
word p^2 d                  24
corridor length              3
surplus                       0
fusion masses               1+1
source partition            (3,1,1,1,1)
target partition            (3,2,1,1)
incoming distinguished use   none
```

This is a uniform realization normal form on this carrier only. It is not a
general rank-five return normal form.

## Handoff outcome

Every successful target is literally the corresponding exact lower-section
context. The handoff histogram is

```text
IDENTITY       48
ATOM_BIJECTION  0
```

This answers the P28.5d handoff hostile test negatively: the second
realization does not independently require a non-identity typed handoff.
Consequently, the P28.5c promotion gate is not met. Typed equivalence remains
permitted inside exact-lift soundness F3, but it is not promoted to a sixth
abstract section-return contract on the present evidence.

The two realizations therefore show different serialization behavior:

- the extremal 35-context chain requires an atom-bijection handoff;
- the second 48-context chain closes by identity handoff.

What survives both is preservation of the lower theorem's typed observables,
not a requirement that the handoff be nontrivial.

## Preregistered questions

| question | result on the second realization |
| --- | --- |
| H1: is non-identity typed handoff again required? | no; all 48 successful handoffs are identity |
| H2: does the normalized action-relative boundary support liftability? | yes on the declared 48-context scope |
| H3: do `TRANSPORT`, `RETURN`, and `FUSION` cover exact lifts? | yes; no fourth primitive occurs |
| H4: does `forall C exists m exists x` survive? | yes; 48/48 sources, with 48 failed channels retained |

## Claim boundary

This is a fixed-scope second realization. It does not prove:

- a return theorem for every inherited rank-five context;
- maximality or canonicity of `Sec_5,cand2^(7)`;
- a rank-controlled or uniform menu bound;
- that every channel or lift succeeds;
- an all-rank return theorem or Forced FFS.

The higher arrow partly reflects the frozen source-local `Sigma_5` carrier
selection. Its value is the clean separation of source authority, menu/lift
construction, lower-section certification, and post-freeze typed handoff
evaluation.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_prepare_second_rank5_section_candidate.py
python experiments/synchronizing_automata/validation/validate_paper28_second_rank5_section_candidate.py
python experiments/synchronizing_automata/paper28_evaluate_second_rank5_section_return.py
python experiments/synchronizing_automata/validation/validate_paper28_second_rank5_section_return.py
```

The evaluation artifact is
`results/paper28_second_rank5_section_return_evaluation_v1.json.gz`. Its digest
is `e2990ba262a09e9d985e2f968ee9c0af76f8192d8b1f5d93cd8db0ec9876ec56`.
The JSON receipt binds the frozen candidate, the lower authority, and the local
source closure.

## Next research step

Do not enlarge to `n=8` or the full 15,120 inherited scope yet. First extract
the common and divergent assumptions of the 35-context and 48-context composed
chains. In particular, separate:

- typed-observable preservation, which both chains use;
- non-identity handoff, which only the first chain uses;
- selected-entry identity, which is special to the second chain;
- the common existential menu/lift quantifier and exact-compatible accounting.
