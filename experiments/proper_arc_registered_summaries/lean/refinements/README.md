# Absorption-Length And Placement-Rank Refinements

Two independent finite-combinatorial branches restrict the already frozen
actual-chain and actual-placement equivalences. The domain remains every
proper source arc `arc c r`, `c : ZMod n`, `2<=r<n`, from the identity
singleton seed under chronological raw `p,d` execution.

## Theorem 4.2: Number Of Selected Absorptions

For each complete origin cut `t : Fin (r-1)`, put `m=n-r`. The left side
below is a subtype of actual selected record lists, witnessed by existing
singleton-seed histories at that origin:

```lean
card_actualSelectedChains_length c hr t j :
  Nat.card {A : ActualSelectedChains c r (t.val+1) // A.val.length=j} =
    (n-r).choose j*2^j
```

[ChainLength.lean](ChainLength.lean) first identifies codes with j nonzero
positions with a j-element subset of `Fin m` and an independent Bool at
each selected position. `decodeChain_length` proves that the number of
complete ordered records is exactly that support cardinality. Restricting
the frozen `actualSelectedChainsEquivCode` transfers the pure subset/color
count to actual chains. The result holds for every natural j; the right
side is zero beyond m and is one at j=0. Both final two-packet L/R port
bindings remain different complete records through the inherited bijection.

## Theorem 5.2: Placement Rank

Fix an origin cut and a complete code v, and let
`k=outsideCount hr v`. The new `ActualRankCodePlacements` is only a
subtype of the existing actual placement fibre:

```lean
{P : ActualCodePlacements c hr t v // (placedBlocks P.val).card=s}
```

Here rank is read from the nonempty packet blocks of the literal generated
placement, not defined by a parameter index. For `k>0` and `2<=s<=k+1`,
[RankFibre.lean](RankFibre.lean) proves

```lean
Nat.card (ActualRankCodePlacements c hr t v s) =
  s*(k-1).choose (s-2)*n.choose s
```

`positiveFiberTarget_rank` proves the rank readback, including invariance
under the source-atom renaming. `rankParamsEquivSlice` identifies the
appropriate sigma slice with `RankFiberParams n k (s-1)`.
`actualRankCodePlacementsEquiv` then restricts the frozen actual positive
fibre equivalence. The final algebra uses the inherited pure theorem
`card_rankFiberParams_paper`, not an old fixed-pair actual count.

The k=0 case is separate. `actual_full_carrier_rank` proves that every
actual placement in that fibre has rank one. The independent equivalence
`actualFullRankCodePlacementsEquiv` identifies its rank-one subtype with
`ZMod n`, giving `card_actualFullRankCodePlacements = n`. The positive-k
formula is not applied at this boundary.

## Local Proof Closure

From the parent Lean directory:

```powershell
python -B refinements/validate_refinements.py --check-upstream-git
python -B -m unittest discover -s refinements/tests -p 'test_*.py' -v
```

The [new milestone](milestones/combinatorial-refinements-v1/manifest.json)
binds five new inputs. Its [audit](milestones/combinatorial-refinements-v1/dependency-audit.json)
records 16 complete target signatures, their type constants and 12,215
declaration nodes; 28 declaration/definition axiom queries are checked.
Only `propext`, `Classical.choice` and `Quot.sound` are permitted.

The two proof modules do not import each other. The validator checks this
independence in the declaration closures and rejects a total-summary-count
shortcut. It compares the inherited chain, positive fibre, full-carrier
and pure code-splitting declaration graphs with their frozen owner graphs.
It preserves all eight previous milestone manifests, bound source bytes and
reports. Replay recompiles the needed geometry prerequisites and new
proofs; the independent summary/total-count modules are byte-checked, not
used as mathematical inputs to either refinement.

Sixteen validator tests include omitted actual equivalences, truncated
readback dependencies, an artificial formal domain, a parameter-defined
rank, altered positive-rank bounds and a lost k=0 premise. The refinement
freeze is a local companion milestone, not a change to the HAL v1 proof
identity or a fresh-machine cold replay. Fixed-pair specialization,
generating functions and asymptotics remain later layers.
