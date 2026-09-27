# P28.5h: Third Return Candidate

## Status

This note freezes a third fixed-`n=7` source-local hostile model. It constructs
no completion menu, grants no section authority, and does not evaluate
`Good_4` or `Good_5`.

The selection remains inside the existing future-free 562-cell carrier. It is
the first candidate deliberately chosen to attack the shared `1+1`,
length-three, zero-surplus anatomy: the selected minimizer breaks `1+1` and
zero surplus while holding length three fixed.

## Imported rule

P28.5g preregistered the following primary rule:

1. require fusion-parent type different from `1+1`;
2. prefer a `1+2` family;
3. minimize source-local distance from the two closed realizations on fresh
   participation, length, surplus, binary-kernel mass, and `F_4`-relative
   offsets;
4. do not read completion success, lower-section authority, winning labels,
   or Bellman data.

The selector binds the P28.5g artifact before projecting the inherited pilot.

## Primary tie

The primary rule is not single-valued. The finite projection gives

```text
562 carrier cells
  -> 381 non-1+1 cells
  -> 272 preferred 1+2 cells
  -> 12 minimum-distance cells
```

The twelve cells contain 157 rooted contexts. Their primary Hamming distance
from the closed realizations is two. This complete tie is serialized in the
artifact; no JSON order or historical success label is used to select one of
its members.

## Source-local tie-break

Before any success evaluator is opened, the following controlled tie-break is
frozen:

1. among the twelve primary minimizers, prefer nonzero `Sigma_5` surplus;
2. among those cells, minimize refined binary-kernel boundary distance;
3. define that distance as sorted kernel-mass `L^1` distance plus minimum
   cyclic matching distance between the two `F_4`-relative kernel offsets.

Ten primary minimizers, containing 139 contexts, have nonzero surplus. Their
refined boundary-distance distribution is

```text
distance 1: 1 cell
distance 2: 1 cell
distance 3: 3 cells
distance 4: 3 cells
distance 5: 2 cells
```

Thus the secondary rule has a unique minimizer. This refinement is explicitly
later than the P28.5g primary preregistration, but remains source-local and is
frozen before `Good_4`, `Good_5`, or any lower-section evaluation.

## Selected pre-section carrier

The unique candidate signature is

```text
family                              22111__12_TO_3211
rank-five source partition          (2,2,1,1,1)
rank-four target partition          (3,2,1,1)
fusion parent sizes                 1+2
fusion contains inherited fresh     false
Sigma_5 length / surplus            3 / 2
binary-kernel mass multiset         [0,3]
F4-relative kernel offsets          [0,6]
contexts                            36
```

On all 36 contexts, both the upstream `Sigma_6` word and the selected
rank-five-to-four word are `p^2d`. There are six source mass placements and
twelve target mass placements.

Relative to the two completed chains, the candidate attacks three facts:

```text
fusion masses          1+1 -> 1+2
surplus                0   -> 2
kernel mass multiset   [0,2] -> [0,3]
```

It controls the remaining local anatomy:

```text
length                              3
inherited fresh consumed?           no
F4-relative kernel offsets          [0,6]
```

The carrier is denoted provisionally by

\[
 \mathcal C^{(7)}_{4,\mathrm{cand3}}.
\]

The notation `Sec` is withheld. In particular, this result does not prove

\[
 \mathcal C^{(7)}_{4,\mathrm{cand3}}\longrightarrow P_{\le3}^{(7)}
\]

or a matching rank-five section return.

## Next phase gate

The next authorized operation is only:

1. construct future-free rank-four menus and complete exact lift fibers for
   the frozen 36-context carrier;
2. freeze and digest that relation;
3. only then run an independent `Good_4` evaluator against the exact low-rank
   base.

No `n=8` or full-15,120 return evaluation is authorized. Failure reopens the
mechanism or candidate-section layer, not the Paper XXVII interface, unless a
theorem-relevant observable itself fails to descend.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_select_third_rank5_return_candidate.py
python experiments/synchronizing_automata/validation/validate_paper28_third_rank5_return_candidate.py
```

The artifact is
`results/paper28_third_rank5_return_candidate_selection_v1.json.gz`. Its
SHA-256 digest is
`a4349259f0deca744dc2ff54657851e909b973537a345e2f2295fdb73d20e6c5`.
The receipt binds the inherited pilot, the P28.5g preregistration artifact, and
the five-file local source closure.

## Claim boundary

This result proves only the displayed source-local selection equality on the
fixed 562-cell carrier. It does not prove that the selected carrier succeeds,
that `1+2` is a primitive all-rank mechanism, that positive surplus is
structural, or that any B1/B2 menu bound exists.
