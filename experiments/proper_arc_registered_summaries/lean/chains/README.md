# Proper-Arc Ternary Chains: Constructive Layer

This layer starts Theorem 4.2 of `hal-05848115v1`. For every proper source
arc `F=arc c r`, `2<=r<n`, and every legal internal origin cut, it provides
the ternary decoder, its injectivity, and actual clean witnesses:

```lean
codeEmbeddingActualSelectedChains c hr t :
  Code (n-r) ↪ ActualSelectedChains c r (t.val+1)
```

The codomain consists of complete selected-record lists realized by raw
singleton-seed histories at the specified origin. It is not a decoder range.
The proved map is an embedding; its surjectivity is the next separate task.

## Proof Responsibilities

| Source | Contract |
|---|---|
| `Decoder.lean` | Start the source frontier at `lo=r, hi=n`. Code position i denotes cumulative proper-arc absorption i+1; a nonzero position emits one record for the whole intervening batch. |
| `DecoderInjective.lean` | Recover cumulative size `result.card-r` and the carrier port from each ordered record; distinct codes have distinct canonical chains. |
| `SourceTranslation.lean` | Atom renaming commutes with actual registration guards, selected-event guards and every `p,d` update. Alignment transports the canonical seed to arbitrary source offset c. |
| `CleanRealization.lean` | Iterate the inherited generic multi-atom R/L checkpoint constructors from the actual origin word. One common word preserves the chosen origin, decoded chain, and present clean carrier. |
| `ActualChains.lean` | Recover source-addressed keys after translation, prove all-c decoder injectivity, and embed codes into the real-history fixed-origin chain type. |

The inherited coordinate frontier counts `|C|-2`; this decoder shifts that
quantity by `r-2`. It does not reuse the fixed-pair actual-code realization.
Physical sites and source identities remain distinct: `recordKeyAt` tests
the source atom c in the left parent, not whether physical port zero is
contained in a source set.

For every code the final witness retains a packet equal to `decodedCarrier`,
contains F in that packet, and leaves every other packet singleton. The
`CleanOutside` predicate includes actual presence of that complete packet,
not merely a constraint on outside atoms. Zero symbols produce no selected
event; a checkpoint absorbing ell atoms uses outside assembly followed by
one selected event, not ell selected singleton absorptions. The generic
checkpoint theorem also covers the last two-packet L/R choices.

## Replay

From the parent Lean directory:

```powershell
python -B chains/validate_chains.py --check-upstream-git
python -B -m unittest discover -s chains/tests -p 'test_*.py' -v
```

The validator compiles this layer independently, audits its declarations and
complete target dependency graphs, and checks the exact bytes of all three
prior origin milestones before and after replay. Its axiom leaves are
restricted to `propext`, `Classical.choice`, and `Quot.sound`. The dependency
report includes the real-history codomain definition and the complete public
signatures. `--source-only` checks bytes without replaying the kernel.
This remains a local companion milestone, separate from the HAL v1 identity.

The [construction manifest](milestones/chain-construction-v1/manifest.json)
binds eight new inputs, 34 axiom checks and 11 complete target signatures.
The [dependency report](milestones/chain-construction-v1/dependency-audit.json)
contains 9,420 declaration nodes. Its inherited target graphs are compared
with the frozen origin-classification report, including direct dependency
edges rather than merely checking that old theorem names occur.

## Converse Completion

The arbitrary-actual-history direction is now proved in the separate
[converse layer](../converse/README.md):

```text
registered reachable s at origin o_t
  => exists v : Code (n-r), s.chain = decodeChain c hr v.
```

That layer follows source order and the actual carrier across arbitrary
outside fusions, with no `CleanOutside` premise. It gives an explicit
encoder, the fixed-origin selected-chain equivalence and total `3^(n-r)`
count. These are additional converse results, not retroactive changes to
this constructive layer's eight frozen inputs or its original scope.
