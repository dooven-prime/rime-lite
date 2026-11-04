# Actual Proper-Arc Placement Fibres

For each proper source arc, internal origin cut and ternary code, this layer
proves the actual placement-fibre equivalence and total fibre cardinality
in Theorem 5.2 of `hal-05848115v1`:

```lean
codePlacementFibreEquiv c hr t v :
  CodeFiberParams ⟨hr.1,hr.2.le⟩ v ≃ ActualCodePlacements c hr t v

card_actualCodePlacements c hr t v :
  Nat.card (ActualCodePlacements c hr t v) = n * (n+k-2).choose k
```

Here k is the decoded remaining interval length. `outsideCount_eq` proves
that it is also `n-r-lastCheckpoint v`, exactly the manuscript's `m-b(v)`.
The domain is arbitrary `c : ZMod n`, `2<=r<n`, every origin cut and every
code. The actual subtype requires one singleton-seed raw word realizing
the specified complete origin, selected chain and literal placement.

## Parameters And Their Actual Meaning

For k>0 the native finite type is

```text
FiberParams n k = (i : Fin k) × RankFiberParams n k (i.val+1)
RankFiberParams n k u = Fin n × Select (k-1) (u-1) × Select (n-1) u
```

The choices are the number u of outside blocks, the carrier site, the
internal source cuts, and the occupied offsets clockwise from that site.
They encode the cut/occupied-set/carrier-site triples of equation (5.2).
The inherited `ValidFiberPlacement` decoder fixes their positive source and
physical orders. Its pure inverse and literal-placement uniqueness are
reused; no reachability premise is put into these parameter types.

For k=0 the parameter type is independently `ZMod n`. Its map is literally
`q ↦ fullCarrierPlacement univ q`, as certified by
`fullPlacementFibreEquiv_val`. Every such phase has a real word at the same
origin and chain, not merely a conditional one-block classification.

## Proof Map

| Source | Responsibility |
|---|---|
| `Carrier.lean` | Identify the decoded carrier as an actually present packet, including arbitrary outside-fusion histories; transport to any c and identify the full-carrier boundary. |
| `NormalForm.lean` | Recover ordered outside intervals and actual physical sites, form a `ValidFiberPlacement`, and bound its outside-block rank. |
| `Realization.lean` | Start from the actual clean code witness, assemble each outside cut and adjust its placement while retaining origin and chain in the same run; realize the independent full-carrier phases. |
| `PlacementEquivalence.lean` | Prove parameter injectivity and arbitrary-history reverse existence, build both branch equivalences and their union, then transfer finite cardinality and Vandermonde. |

The forward cut construction reuses `allCut_realize_target`, which accepts
an arbitrary selected F. It starts from the specially constructed clean
witness, not an arbitrary already-coarsened state with the same chain.
Its counted assembly has k-u true outside fusions, followed by fusion-free
placement control; that count is not a raw-word-length bound.

The reverse normal form has no clean-state premise or clean-construction
dependency. It uses the actual carrier, source order and the remaining
source interval. It recovers the same literal placement, rather than only
its block sizes or a placement up to rotation. Source translation changes
atom labels while preserving the actual chronological update equations.

## Replay

From the parent Lean directory:

```powershell
python -B fibres/validate_fibres.py --check-upstream-git
python -B -m unittest discover -s fibres/tests -p 'test_*.py' -v
```

The validator preserves the five prior milestone manifests, source files
and reports. It checks the new theorem/definition axioms and full target
dependency graphs, including actual cut construction, inverse normal form,
both k branches and exact comparison with inherited proof graphs. It
rejects a parameter type that assumes reachability, a domain replaced by
formal targets, a clean restriction on the converse, or substitution of the
fixed-pair actual fibre theorem. Allowed axiom leaves remain `propext`,
`Classical.choice` and `Quot.sound`.

This is a local Lean companion milestone, separate from the HAL v1 proof
identity. The full dependent-summary equivalence and total-summary count,
the rank-refined fibre count, refined chain count and analytic layer remain
separate subsequent obligations.

The [placement-fibre manifest](milestones/placement-fibre-v1/manifest.json)
binds seven new inputs and 32 declaration/definition axiom checks. Its
[dependency report](milestones/placement-fibre-v1/dependency-audit.json)
contains 15 complete target signatures and 12,761 declaration nodes.
Inherited declaration graphs are compared exactly with their prior freeze.
