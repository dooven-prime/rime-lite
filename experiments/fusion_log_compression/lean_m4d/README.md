# M4-D: Abstract schedules and compatible endpoints

An independent Lean milestone for the joint classification in manuscript
Theorem 4.1, above the unchanged M4-C interpretation layer.

## Contract

For `n >= 3`, any atom type with decidable equality, and any nonempty initial
placement of nonempty pairwise disjoint packets, the following are equivalent:

1. A real chronological `p,d` word has the prescribed complete ordered
   effective-fusion log and the prescribed literal endpoint.
2. The log is an admissible abstract schedule and the endpoint is compatible
   with its terminal cyclic partition.

When these conditions hold there is one actual word with length at most
`normalFormBudget n t s`, where `t` and `s` are the occupied-site ranks of
the initial and target placements. This is the manuscript's specific
`B(n,t,s)` upper bound, not a shortest-word assertion.

The main declarations are:

```text
FusionLogSchedule.abstract_schedule_endpoint_iff
FusionLogSchedule.abstract_schedule_bounded_realization
FusionLogSchedule.abstract_schedule_endpoint_iff_bounded
```

`PacketPartition` expresses nonempty packets and pairwise disjointness.
`packetPartition_of_named` admits the existing `LegalNamedPlacement` interface.
The ambient atom type need not be finite; each packet is a `Finset`.

## Abstract Definitions

`AbstractTrace` is a finite sequence of contractions of distinct whole
source-neighbour packets. Each record keeps the ordered parents and their
union. Its constructors contain no execution word. On two remaining packets,
both port directions are retained; an empty trace includes the zero-fusion
case.

The fixed M4-C cyclic source fibres encode initial packets, including gaps,
without adding a physical packet or an entry word. `AdmissibleSchedule`
interprets an abstract trace on these fibres as literal atom-set records.
For a genuine packet partition, `indexEvents_recover` recovers the unique
index trace from the literal log. Therefore `finalPackets` computes its
terminal partition without choosing an admissibility witness.

`CompatibleForLog` asks for a static degree-one source-order placement of
that partition which expands to the literal target. It contains no actual
execution. `index_compatible_iff_named_cycle` identifies the canonical
endpoint condition with the existing common positive named-cycle interface.
The admissibility and compatibility predicates consequently refer to the
same terminal partition even when written as a conjunction.

## Proof Route

`AbstractTrace.realize` applies M2 to the current actual representative,
appending exactly one full record at each step. M3 then aligns the endpoint
without adding a fusion. The resulting joint object supplies the real
reference word required by the frozen M4-C compression theorem, which gives
the sharp budget from the original initial placement. No reference-word
cost is charged or silently prefixed to the short word.

Necessity is a separate induction on the actual word, including rotations,
fusion-free defect moves, and effective adjacent fusions. Endpoint
source-order is transported by the same run. Rank-one and zero-fusion cases
use the inherited one-packet/empty-replay branches.

## Reproduce

Run from the parent experiment directory:

```text
python -B validation/replay_m4d.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m4d.py
python -B validation/replay_m4d.py --report results/my-m4d-replay.json
```

For fresh external dependencies add `--cache`. Lean is pinned to
`leanprover/lean4:v4.33.0`; Mathlib to
`db584cd6d46c92f209a44c0f1c829460d327499d`.
The validator checks ancestor closures, this source inventory, the runtime,
the build, 27 transitive axiom declarations, and the printed final signatures.
Reports are new files, never overwrites. The recorded local replay uses the
installed pinned toolchain and shared dependency caches.

[`M4D_THEOREM_MAP.md`](../M4D_THEOREM_MAP.md) owns the theorem/source mapping.
The M4-B archive, M4-C manifest and HAL reader remain unchanged. Joint-object
counts, forgetful endpoint fibres and all-R optimality are later milestones.
The minimal CI workflow currently replays M4-C, not M4-D.
