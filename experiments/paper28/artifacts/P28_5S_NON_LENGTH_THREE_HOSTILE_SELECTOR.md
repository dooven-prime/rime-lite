# P28.5s: Non-Length-Three Hostile Selector

## Status

A unique 10-context source-local minimizer is frozen for the fifth hostile
return experiment. No `Good_4`, ordinary `Good_5`, or `Good_5^non3`
evaluation has run, and no section authority is granted.

## Preregistered rule

The selector uses the complete 562-cell future-free carrier and applies the
following lexicographic rule:

1. require inherited-fresh consumption;
2. require `sigma5_length != 3`;
3. prefer the `1+2` fusion family;
4. minimize source/target partition, kernel-mass, and kernel-offset distance
   to the fourth closed chain;
5. minimize gross maturity-gain distance using
   `G = sigma5_length + sigma5_surplus`;
6. only then minimize action-relative rank-five/rank-four placement distance.

Surplus is not compared as an independent control variable. Candidate
membership reads no return success, low-rank base membership, lower-section
membership, or winning label.

## Exact selection

```text
complete future-free cells                         562
fresh-consuming, non-length-three cells            142
corresponding rooted contexts                     5,032
preferred 1+2 cells                                  66
preferred 1+2 rooted contexts                       723
geometry minimizers                                   1
gross-gain minimizers                                 1
finalists                                             1
selected contexts                                    10
```

All 66 preferred `1+2` cells have gross maturity gain `G=5`. Their length
distribution is `2:25, 4:23, 5:18`. The unique geometry minimizer has

```text
(2,2,1,1,1) --[1+2, length 5, surplus 0]--> (3,2,1,1)
fresh consumed, kernel masses [0,3], F4-relative offsets [0,6]
```

Thus the fifth carrier keeps the fourth chain's source and target partitions,
fusion parents, inherited-fresh participation, kernel masses, and gross gain
`G=5`, while changing `(length,surplus)` from `(3,2)` to `(5,0)`. On the
declared geometry fields the sole difference is the kernel-offset pair
`[0,2] -> [0,6]`.

This is therefore the nearest available non-length-three control, not a
literal one-variable matched control. The interpretation is asymmetric:

- if a complete fifth chain succeeds through `L != 3` lifts, length three is
  not necessary on the declared fixed-`n=7` surface;
- if it fails, the failure cannot be attributed to length alone, because the
  relative kernel-offset geometry also changed.

A failure would justify a search for a more tightly offset-matched
non-length-three carrier; it would not prove that length-five return is
impossible.

The minimum action-relative placement distance is four, attained by a unique
placement witness after the structural and accounting filters have already
selected the unique cell.

## Next gate

The next legal stage is a separately frozen rank-four menu/exact-lift
relation. If that lower section gains authority, the matching rank-five freeze
must report the selected corridor length against the complete exact-fiber
length spectrum before either success predicate is run.

The hostile predicate is preregistered as

\[
 \operatorname{Good}^{\ne3}_5(C,m)
 \iff
 \exists x\in\operatorname{Lift}_5(C,m):
 \widehat{\partial^+x}\in\operatorname{Sec}^{(7)}_{4,\mathrm{cand5}}
 \quad\text{and}\quad L(x)\ne3.
\]

Ordinary `Good_5` and `Good_5^non3` must be evaluated only after the complete
rank-five relation is frozen.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_select_non_length_three_hostile.py
python experiments/synchronizing_automata/validation/validate_paper28_non_length_three_hostile.py
```

The artifact is
`results/paper28_non_length_three_hostile_selection_v1.json.gz`, with SHA-256
`4dafb1644b1f2c4f7fb519d01c513fd995caa93a548ee23d4f74ac813f58c5f4`.
Its candidate payload digest is
`124a14abce155fa91c576839524707890c363e9000097b774cbf0a345f26daae`.

## Claim boundary

This stage proves only the future-free selector equality and replay binding.
It does not prove rank-four or rank-five return, does not refute length-three
necessity, and does not establish an all-rank normal form.
