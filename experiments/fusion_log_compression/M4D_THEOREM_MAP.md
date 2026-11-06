# M4-D theorem-to-source map

## Ownership and Identity

This local milestone proves the abstract-schedule/compatible-endpoint
classification of Fusion-log Theorem 4.1, with its specific `B(n,t,s)` bound.
The mathematical owner is the frozen manuscript at
`fusion-log-compression-source-v1.0`, commit
`41cf746a095ecd06d85cb3d1184d58e7bfdd5979`. The new Lean proof owner is
`lean_m4d/FusionLogSchedule/`; it is not part of that HAL deposit's proof
identity.

Direct ancestor: `m4c-development-manifest.v1.json`, SHA-256
`606e08c94497e48098d8f7c78ad9572ebc6b4614d5c7552f9254743b35d9660d`.
Its verifier recursively checks the frozen M4-B and M1-M3 inputs. M4-B's
public archive remains `10.5281/zenodo.23976349`.

Lean: `leanprover/lean4:v4.33.0`, commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`.
Mathlib: `db584cd6d46c92f209a44c0f1c829460d327499d`.
The new exact input identity is `m4d-development-manifest.v1.json`; no
companion Git tag, DOI or independent cold-replay identity is assigned here.

## Theorem Surface

All names in this table have namespace `FusionLogSchedule`.

| Paper role | Declaration | Owning source |
| --- | --- | --- |
| Pure admissible contractions; unique terminal partition | `AbstractTrace`, `AbstractTrace.last_unique` | `AbstractTrace.lean` |
| Next abstract event has an actual route from the current representative | `abstract_step_realizable` | `CanonicalRealization.lean` |
| Same-witness induction over the whole abstract log | `AbstractTrace.realize` | `CanonicalRealization.lean` |
| Necessary cyclic-neighbour condition for every actual word | `actual_trace_admissible` | `CanonicalRealization.lean` |
| Exact canonical endpoint restoration | `realize_index_joint`, `index_joint_iff` | `CanonicalRealization.lean` |
| Static endpoint condition equals common positive named-cycle compatibility | `index_compatible_iff_named_cycle` | `OrderInterface.lean` |
| Generic-atom actual execution supplies a finite abstract certificate | `actual_joint_certificate` | `JointClassification.lean` |
| Abstract certificate and endpoint give a real bounded word | `realize_admissible_schedule` | `JointClassification.lean` |
| Literal log uniquely recovers source-addressed records | `AdmissibleSchedule.indexEvents_recover`, `indexEvents_unique` | `PacketAddresses.lean` |
| Literal log determines the abstract terminal partition | `AdmissibleSchedule.last_eq_finalPackets` | `LiteralClassification.lean` |
| Theorem 4.1, necessity and sufficiency as a conjunction | `abstract_schedule_endpoint_iff` | `LiteralClassification.lean` |
| Theorem 4.1, converse with `B(n,t,s)` | `abstract_schedule_bounded_realization` | `LiteralClassification.lean` |
| Equivalent bounded-word classification | `abstract_schedule_endpoint_iff_bounded` | `LiteralClassification.lean` |
| Existing eligible named placements satisfy the packet-partition premise | `packetPartition_of_named` | `LiteralClassification.lean` |

Paths in the last column are relative to `lean_m4d/FusionLogSchedule/`.

## Exact Main Interface

The common parameters are `n : Nat`, `[NeZero n]`, `alpha : Type*`,
`[DecidableEq alpha]`, `F : Finset alpha`, `source : Execution n alpha`,
`events : List (FusionRecord alpha)` and `target : Placement n (Finset alpha)`.
The hypotheses are `hn : 3 <= n`, nonempty occupied support of
`source.placed`, and `valid : PacketPartition source.placed`.

```text
JointlyAttainable F source events target <->
  IsAdmissibleSchedule source.placed nonempty events /\
  CompatibleForLog source.placed nonempty events target
```

`JointlyAttainable` is exactly an actual word with the complete ordered
event trace and the literal endpoint. Under the right side, the stronger
theorem returns:

```text
exists word : List Letter,
  eventTrace F source word = events /\
  (run F source word).placed = target /\
  word.length <= normalFormBudget n
    (occupiedSites source.placed).card (occupiedSites target).card
```

`Signatures.lean` prints the complete elaborated signatures into the replay
receipt. The new definitions of schedule and compatibility are static:
neither asks for a real word. The recovered abstract partition prevents
combining independently chosen log and endpoint witnesses.

## Transitive Proof Dependencies

```text
pure AbstractTrace
 -> source-neighbour M2 route on the current actual injection
 -> exact packet-set update + exactly one ordered event
 -> AbstractTrace.realize
 -> M3 fusion-free endpoint restoration
 -> actual generic-atom log/endpoint interpretation (M4-C)
 -> M4-C compression of that same realized joint object
 -> B(n,t,s) from the original source

actual word
 -> source-order preservation + actual fusion adjacency
 -> actual_trace_admissible
 -> canonical endpoint source-order + literal interpretation
 -> actual_joint_certificate

initial packet disjointness + nonemptiness
 -> restore_expandBlock on saturated source fibres
 -> unique literal-log source addresses
 -> unique abstract terminal partition
 -> independent admissibility / compatibility conjunction
```

The budget depends on M4-C's frozen M4-B replay and rank/hole ledger; the
abstract converse does not reprove or weaken that cost theorem. The
classification does not import any counting or all-R optimality result.

## Audit and Reproduction

From this experiment directory:

```text
python -B validation/replay_m4d.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m4d.py
python -B validation/replay_m4d.py --report results/my-m4d-replay.json
```

`AxiomAudit.lean` prints axioms for 27 named declarations. The validator
requires exactly that inventory and accepts only `propext`, `Classical.choice`
and `Quot.sound`; it rejects placeholders, additional axiom names, altered
inputs and ancestor drift. These are transitive axiom sets, not an independent
mathematical review or a declaration-dependency graph. The saved local result
is `results/m4d-abstract-schedule.v1.json`.

The rank-one, empty-log and final-two-packet cases remain in the same all-
parameter proof. Counts of joint objects, forgetful fibres and all-R exact
optimality/uniqueness remain outside this milestone.
