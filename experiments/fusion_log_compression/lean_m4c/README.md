# M4-C: Arbitrary-initial-packet interpretation

Local Lean development extending the frozen M4-B actual-word compression
theorem. This is a separate Lake project; no M4-B source or published
archive byte is changed.

## Result and Domain

For every `n >= 3`, atom type `alpha` with decidable equality, initial
set-valued placement with at least one occupied site, and actual `p,d` word,
`arbitrary_initial_log_endpoint_budget` constructs an interpreted routing
certificate. Its actual word has the same complete ordered effective-fusion
log and literal endpoint, and meets the unchanged B/K/M bounds. In particular
it applies to every eligible finite partition into nonempty initial packets.

The raw theorem is slightly more general: it needs nonempty occupied support,
not an atom partition, clean state, singleton-seed history, pre-existing source
lift, or finiteness of the ambient atom type. Each packet is a `Finset`.
`named_initial_log_endpoint_representative` specializes to the existing
`LegalNamedPlacement n r alpha` interface and uses initial rank exactly `r`.

The rank in the arbitrary-type theorem is the cardinality of occupied sites.
`named_occupied_rank` relates it to the number of distinct named packets.
On the canonical side it equals M4-B's packet-set cardinality by the frozen
SourceOrdered rank theorem.

## How the Bridge Works

1. `expandBlock labels I` takes the union of the initial packet labels in `I`.
   It preserves union. Option-level expansion preserves occupied versus empty
   physical sites, so it commutes with rotations and actual defect steps.
2. For nonempty occupied support `S`, the integer map
   `max_{q in S} [q.val + floor((x-q.val)/n)*n]` is monotone, degree-one periodic,
   lands in `S` modulo `n`, and fixes every occupied site. Its fibres supply a
   SourceOrdered placement on the fixed `ZMod n` index alphabet.
3. An occupied index carries its initial packet; a hole index has empty label.
   Expanding the canonical fibres gives the original placement exactly. These
   auxiliary indices add no physical packets or preparatory execution word.
4. M4-B supplies its actual replay plan. Every M2 stage is enabled at the actual
   representative reached by the preceding literal stages. The M3 suffix is
   transported to a genuine `BatchPlacementPlan` over the original atom type,
   with exactly the same word, nonempty-batch count and transfer count.
5. The old bounds are rewritten through equal occupied-site ranks. No new
   cost estimate or free inverse/phase operation is introduced.

An existing actual log prefix is retained literally. It is not assumed to be
recoverable from the current initial-packet alphabet. The target `F` and the
selected `origin/chain` policy need not agree with the auxiliary index run:
their fields do not affect raw placement or complete-event output. The final
contract compares the complete log and placement, not the whole selected
execution record or an existing typed-transfer interface.

## Reproduce

From the parent experiment directory:

```text
python -B validation/replay_m4c.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m4c.py
python -B validation/replay_m4c.py --report results/my-m4c-replay.json
```

For a fresh external-dependency setup, add `--cache`. Lean is pinned to
`leanprover/lean4:v4.33.0` (commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`); Mathlib is pinned to
`db584cd6d46c92f209a44c0f1c829460d327499d`.
The launcher verifies both ancestor source closures, the M4-C inventory,
runtime identity, build and 29 transitive axiom targets. Reports are never
overwritten. The local run uses the installed pinned toolchain and shared
external dependency caches, not an independent cold setup.

[M4C_THEOREM_MAP.md](../M4C_THEOREM_MAP.md) records the interfaces and exact
ancestor pin. The result is an existence/interpretation theorem, not an
exported executable normalizer. Independent formal-schedule/compatible-target
classification, joint counts and shortest-word results remain separate.
