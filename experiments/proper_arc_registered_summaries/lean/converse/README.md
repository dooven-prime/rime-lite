# Actual Proper-Arc Selected Chains

This layer completes the chain-bijection and total-chain-count parts of
Theorem 4.2 in `hal-05848115v1`. For arbitrary `c : ZMod n`, `2<=r<n`
and `t : Fin (r-1)`:

```lean
actualSelectedChainsEquivCode c hr t :
  ActualSelectedChains c r (t.val+1) ≃ Code (n-r)

card_actualSelectedChains c hr t :
  Nat.card (ActualSelectedChains c r (t.val+1)) = 3^(n-r)
```

The codomain is the unchanged actual-history type from the frozen
`chains/ActualChains.lean`, not a decoder range or a clean-state subtype.

## Converse Interfaces

| Interface | Contract |
|---|---|
| `actual_chain_checkpoint_strict` | Along any registered actual history, `result.card-r` is strictly increasing and lies in `1,...,n-r`. |
| `actual_partner_is_end_interval` | In aligned source coordinates, the actual partner is a nonempty prefix or suffix. The same conclusion retains its port binding and this proper arc's exact record append and successor. |
| `actual_chain_decode_encode` | The explicit record-based encoder decodes to the entire actual ordered record list, including both parents and their result. |

The encoder reads result size relative to r and the source anchor c in the
left parent. The carrier contains c and the outside partner does not, so
this reads its actual parent-to-port binding. Even if the final prefix and
suffix sets coincide, `checkpoint_port_bindings_distinct` proves their two
ordered records are different.

## Proof Map

| Source | Responsibility |
|---|---|
| `DecoderInsertion.lean` | Skip zero positions and insert one later checkpoint with the exact frontier and record update. |
| `ActualPartner.lean` | Strict local growth and source-end interval geometry; prove the actual proper-arc F-update independently of the inherited pair-update output. |
| `ActualTrace.lean` | Maintain a sparse code and present recorded carrier through arbitrary real letters and outside-only fusions. Transport the converse to arbitrary c by actual alignment and source renaming. |
| `ActualChainConverse.lean` | Explicit encoder, both round-trips, strict chronological checkpoints, unique code, actual equivalence and total count. |

The reverse invariant `ActualChainTrace` has no `CleanOutside` field.
Registration initializes carrier F and an empty selected chain. Selected
steps append the actual complete `checkpointRecord`; unselected steps keep
the carrier and records while still performing the entire placement update.
The local size lemma supplies strict growth before sparse insertion; the
global strict-list theorem is then assembled from the actual classification.
There is no dependence in the opposite direction.

The full equivalence combines this arbitrary-history converse with the
frozen clean per-code construction. The converse itself does not use clean
witnesses or the fixed-pair actual chain-classification theorem. The aligned
geometric helper is transported to arbitrary source offsets in
`actual_chain_in_decode_range` and all final actual-history statements.

## Replay

From the parent Lean directory:

```powershell
python -B converse/validate_converse.py --check-upstream-git
python -B -m unittest discover -s converse/tests -p 'test_*.py' -v
```

The validator preserves all four previous milestone manifests, source bytes
and reports. It audits every new theorem, the encoder, reverse invariant
and equivalence, plus explicit inherited target closures. Only `propext`,
`Classical.choice` and `Quot.sound` are allowed as axiom leaves. It checks
the absence of clean premises and clean proof dependencies in the converse,
the actual seed-history domain, and the exact inherited declaration graphs.

The [local manifest](milestones/actual-chain-equivalence-v1/manifest.json)
binds seven new inputs and 34 declaration/definition axiom checks. The
[dependency report](milestones/actual-chain-equivalence-v1/dependency-audit.json)
records 15 complete target signatures and 11,160 declaration nodes,
including exact comparisons with the inherited construction graphs.
This companion does not change
the HAL v1 proof identity. Refined counting by absorption length, actual
placement fibres, dependent summary equivalence and analysis remain separate.
