# M5: Exact Counts and Literal Endpoint Log Fibres

M5 formalizes Section 5 of the Fusion-log manuscript over actual chronological
`p,d` executions. It extends the frozen M4-D joint-realization theorem without
changing its sources, manifests or historical receipts.

## Results

Fix a legal positively ordered literal rank-`t` initial placement, with
`n >= 3` and `1 <= s <= t`. The proved interfaces give:

| Object counted | Exact cardinality | Main declaration |
| --- | --- | --- |
| Complete admissible ordered logs, terminal rank `s` | `t! / s!` | `card_admissibleLogs_rank` |
| Actual literal endpoints for one fixed log | `s * choose n s` | `card_actualLiteralEndpointFiber` |
| Actual complete-log/literal-endpoint pairs of rank `s` | `(t! / s!) * (s * choose n s)` | `card_rawJoint` |
| Complete actual logs over one reachable literal endpoint, `s >= 2` | `(t-s)!` | `card_rawActualLogFiber` |
| Complete actual logs over one reachable rank-one endpoint | `t!` | `card_rawActualLogFiber_rankOne` |
| Distinct reachable literal endpoints, `s >= 2` | `choose t s * (s * choose n s)` | `card_rawLiteralEndpoints` |
| Distinct reachable rank-one endpoints | `n` | `card_rawLiteralEndpoints_rankOne` |

The schedule/boundary-deletion equivalence retains the two different ordered
parent bindings of the last rank-two fusion. At rank one the literal target
has no visible last surviving boundary; those choices belong to its `t!`
log fibre, not to an extra endpoint coordinate. Zero-event schedules and
`t=s=1` are included.

## Actual Objects

`RawActualLogFiber F start target` stores only complete structured event
lists with an actual joint realization to that exact literal placement.
It assumes neither a preselected schedule family nor an event count.
`card_rawActualLogFiber_of_reachable` states its full piecewise count using
the physical rank of any reachable target.

`RawJoint F start d` stores only an event list and a literal target with
actual joint reachability. It indexes by log length `d`;
`jointlyAttainable_length_add_rank` proves `d + packetRank target = t`.
Thus `d=t-s` is precisely the rank-`s` joint object in the manuscript.
Execution words and realization proofs are witnesses, not counted data.

The proof chain is:

```text
ordered-boundary deletion bijection
 -> independent forward and reverse M4-D log admission
 -> exact fixed-log literal endpoint equivalence
 -> visible-survivor recovery and its converse
 -> rank-one same-phase compatibility
 -> unrestricted actual literal-endpoint log fibres
 -> dependent actual joint equivalence and exact counts
```

`LiteralPacketStart` supplies the legal named initial placement, its positive
order and its identification with the marked circle. In particular it uses
the existing nonempty/disjoint/coverage fields of `LegalNamedPlacement`;
no raw-word witness is added to this initial-data interface. The actual
realization theorems use `n >= 3`; the static admission layer does not.

## Reproduce

From the parent experiment directory:

```text
python -B validation/replay_m5.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay_m5.py
python -B validation/replay_m5.py --report results/my-m5-replay.json
```

For new external dependencies add `--cache`. Lean is
`leanprover/lean4:v4.33.0`; Mathlib is pinned to
`db584cd6d46c92f209a44c0f1c829460d327499d`.
The replay gate checks the complete ancestor/source inventories, the actual
toolchain, `lake build`, 64 transitive axiom targets, and final elaborated
signatures. It accepts only `propext`, `Classical.choice` and `Quot.sound`.
New reports never overwrite saved ones.

The minimal direct commands from this Lake root are:

```text
lake build
lake env lean FusionLogEnumeration/AxiomAudit.lean
lake env lean FusionLogEnumeration/Signatures.lean
```

[M5_THEOREM_MAP.md](../M5_THEOREM_MAP.md) records proof ownership and the
manuscript correspondence. [PROOF_GUIDE.md](PROOF_GUIDE.md) preserves the
detailed interface-by-interface explanation. Current stage navigation is in
[CURRENT_STATUS.md](../CURRENT_STATUS.md), outside the frozen M3 README.

## Evidence Boundary

These are all-parameter Lean proofs of the declared Section 5 interfaces.
The manifest and saved receipts distinguish a local replay from a hosted
Ubuntu run; public source identity is fixed separately after acceptance.
No shortest-word optimum or all-R uniqueness result is included.
