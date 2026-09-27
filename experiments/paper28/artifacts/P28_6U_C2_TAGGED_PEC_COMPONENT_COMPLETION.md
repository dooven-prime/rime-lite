# P28.6u-C2: Tagged Fixed-Scope PEC Component Completion

## Status

The fixed-scope Pair-Extension Carry component is complete on each of the
three independently frozen carriers

\[
 j\in\{3,4,5\},\qquad
 \operatorname{Sec}_{4,\mathrm{cand}j}^{(7)}.
\]

The evaluation does not identify their rank-four relations. Every source,
channel, lift, target, and good-provenance record retains its carrier tag.

## Explicit PEC witness binding

Before completion, the PEC branch syntax was hardened to

\[
\boxed{
 \operatorname{RelevantBranch}^{\rm ISE}_{\rm PEC}(C,d,\kappa)
 \iff
 \exists P,Q,x\in\Pi^\uparrow:
 \operatorname{PECWitness}(C,d,\kappa;P,Q,x).}
\tag{C2-PECWitness}
\]

No uniqueness of the role decomposition is assumed. The current frozen fibers
happen to provide one exact witness each, but the support predicate remains
existential and relation-valued.

## Carrier-specific return relations

For each carrier tag define

\[
\boxed{
\begin{aligned}
 \operatorname{LocalReturn}_{4,j}^{\rm fs}(C,d,\kappa)
 \iff \exists m,x:\;&
 x\in\operatorname{Lift}_{4,\mathrm{cand}j}^{\rm fs}(C,m)\\
 &\land
 \widehat{\partial^+x}\in P_{\le3}^{(7)}.
\end{aligned}}
\tag{C2-LocalReturn}
\]

The derived good-provenance relation is

\[
 \mathcal G_{\rm PEC}^{\rm fs,j}
 =\left\{\kappa\in\mathcal P_{\rm ISE}^{j}:
 \operatorname{RelevantBranch}^{\rm ISE}_{\rm PEC}(\kappa)
 \land
 \operatorname{LocalReturn}_{4,j}^{\rm fs}(\kappa)\right\}.
\]

The pooled object is only the tagged disjoint union

\[
 \boxed{
 \mathcal G_{\rm PEC}^{\rm fs,pool}
 =\bigsqcup_{j\in\{3,4,5\}}
 \{j\}\times\mathcal G_{\rm PEC}^{\rm fs,j}.}
\tag{C2-TaggedUnion}
\]

## Phase order

The evaluator enforces

\[
\boxed{
\begin{aligned}
 &\text{freeze PEC support}\\
 &\to\text{freeze the three complete rank-four relations}\\
 &\to\text{freeze a tagged completion-input digest}\\
 &\to\text{define carrier-specific generic LocalReturn}\\
 &\to\text{open exact }P_{\le3}^{(7)}\\
 &\to\text{evaluate every tagged exact lift without selecting a winner.}
\end{aligned}}
\tag{C2-Order}
\]

The tagged completion-input digest is

```text
1b0604cca68070e046b0eb6b0f0cdd17609b450edbe950fb46d15fc9cde2aa13
```

The evaluator does not load any historical `Good_4` artifact or rank-five
return evaluator. Historical counts are compared only by the validator after
the new artifact has been deterministically reconstructed and receipt closure
has passed.

## Completion theorem

For every `j in {3,4,5}`,

\[
\boxed{
 \forall C\in\operatorname{Sec}_{4,\mathrm{cand}j}^{(7)},\qquad
 \operatorname{PECSupp}_7(C)
 \Longrightarrow
 \mathcal G_{\rm PEC}^{\rm fs,j}(C)\ne\varnothing.}
\tag{PEC-FS-Tagged-Completion}
\]

The exact audit is

| carrier | sources completed | channels returning | channels failed | mixed channels | exact lifts returning | exact lifts failed |
|---|---:|---:|---:|---:|---:|---:|
| `cand3` | 36/36 | 171 | 1 | 63 | 4,208 | 1,031 |
| `cand4` | 36/36 | 252 | 0 | 38 | 5,937 | 561 |
| `cand5` | 10/10 | 53 | 0 | 18 | 1,205 | 271 |
| **tagged pool** | **82/82** | **476** | **1** | **119** | **11,350** | **1,863** |

The three complete relations contain 13,213 exact lifts in 477 channels.
There are 1,566 certified tagged target contexts and 50 tagged sources with a
mixed channel. The one fully failed channel belongs to cand3 and is retained.

Thus completion is existential at both channel and exact-lift level. The
11,350 returning lifts are not collapsed to a selected witness, and the 1,863
failed lifts remain part of the theorem object.

## Regression firewall

After the C2 artifact is frozen, the validator compares its per-carrier source,
channel, lift, and certified-target counts with the three historical
fixed-scope `Good_4` artifacts. All three checks pass. Those artifacts are not
listed as evaluator inputs and do not affect PEC support, the completion-input
digest, or `LocalReturn` evaluation.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_pec_component_completion.py
python experiments/synchronizing_automata/validation/validate_paper28_pec_component_completion.py
```

The artifact is `results/paper28_pec_component_completion_v1.json.gz`. Its
SHA-256 digest is
`3f6e4bc7758f518a956b3bc07021202b049af3f34a4132f8cb71f45b6edf48fd`.

## Claim boundary

This theorem proves tagged fixed-`n=7` PEC component completion on cand3,
cand4, and cand5. It does not identify their adapters with one another or with
`Lambda_4^complete(C)`, prove all-`n` PEC completion, impose a successful-path
normal form, prove universal channel or lift success, establish completeness
of `{OW,FPC,PEC}`, or prove all-rank F5.
