# Registered Absorption Chains: Bounded Replay

This is the small GitHub companion to *Registered Absorption Chains and
Placement Fibers for a Circular Action with an Adjacent Idempotent*, deposited
by the author as [HAL preprint hal-05837829v1](https://hal.science/hal-05837829v1).
The HAL manuscript and this later GitHub companion have separate file sets;
this directory does not assert that the code was included in the HAL v1 deposit.
It is not a numbered RIME paper release, a proof certificate, or an independent
external replication.

## Scope

For each `2 <= n <= 7`, the script explores reachable states by breadth-first
search from the identity-placed singleton seed on `Z/nZ`. The letters are
`p(q) = q + 1 mod n` and the idempotent `d(1) = 0`, with `d(q) = q` otherwise.
Registration occurs when an actual fusion first creates the selected block
`F = {0,1}`; earlier unrelated fusions are allowed. Fusion ports are ordered
`(0,1)`. The state retains the complete placed partition, origin
record, and selected absorption chain. There is no word-length cutoff.

The raw-action implementation does not import the local chain decoder or an
earlier enumeration result. It compares its complete reachable summary set
with the all-`n` formulas and the saved record. Agreement is a bounded
consistency control, not a proof of the manuscript's all-`n` theorems.

The separate [Lean 4 combinatorial spine](lean/README.md) checks symbolic
checkpoint bijections, formal parameter counts, terminating net gap
accounting, fusion-free execution of supplied hole walks, structural
faithfulness of phase-aware frames, and actual-word realization of each net
gap transfer through adjacent crossings. Given an explicitly named, cyclically
ordered legal placement, it constructs an exact frame and an actual word to
any other such placement with the same named blocks, and checks every defect
letter for a nonfusion kernel configuration. This completes Lemma 2.2 on its
stated two-placement premise; the single-block case is a pure rotation. A
separate source-order invariant now proves that every actual execution from
the singleton seed is represented by a monotone degree-one integer lift, and
that an actual two-port fusion has no intervening third lifted output fiber.
Two source-ordered placements with the same nonempty atom blocks now admit a
common source-key naming and a fusion-free actual word between them. A target
placement built from native `RankFiberParams` cuts, carrier phase, and
occupied-site offsets now obtains legal positive order without assumed
reachability. The chosen clean code witness supplies its decoded carrier arc;
the all-cut boundary-deletion theorem constructs a matching outside-merge
schedule from every valid positive-complement cut. The Lean stage theorem permits real
noncarrier fusions while retaining origin and selected chain; only the final
placement adjustment is fusion-free. The `k=0` branch now has a code-specific
actual full-carrier witness and the exact `n`-phase fixed-record fiber.
The outside schedule and final target adjustment compose into one actual word;
only the final suffix is fusion-free. A separate theorem
counts the `n` distinct placements of one fixed full carrier and realizes each
by rotation. The all-cut theorem constructs the schedule for `k>0`; reverse
fiber normalization and rank-parameter uniqueness are formalized separately.
The Lean code-prefix induction now selects a clean actual chain witness with
singleton outside atoms for every ternary code. Only that chosen witness can
support a later quantification over target cuts: an arbitrary witness of the
same selected chain may already have irreversible outside fusions. The Lean
no-splitting theorem checks this
boundary for every actual continuation word, and the refinement theorem
requires each current outside packet to lie wholly within a target cut block.
The literal registration step supplies a clean base witness. A conditional
singleton induction step uses a supplied same-order legal kernel placement.
The newer batch checkpoint theorem accepts an actual outside-assembly
schedule, a weak partner-subpacket invariant, and a legal placement in either
port direction; it derives the strong assembled shape, composes one actual
word with a final `d`, appends exactly one ordered selected record, and
restores singleton outside packets. Adjacent named outside blocks now admit
an exact `r`-to-`r-1` re-naming whose placement is the actual fused successor.
For a supplied named prefix or suffix of `ell` outside blocks, fixed R/L
recursion constructs one continuous assembly schedule by successively merging
the first or last adjacent pair, with a typed count of exactly `ell-1`
genuine outside fusions. Its endpoint retains a legal positive-cycle naming
whose placement is the actual successor and whose first or last outside block
is the assembled partner. Fusion-free routing letters are not counted.
Given an assembled first or last outside partner, the R or L terminal
kernel-port placement is also constructed without changing cyclic order.
The source-interval checkpoint arithmetic now identifies the R/L partner,
its size and carrier update. Actual reachability and cleanliness determine
the complete block set and canonical source-key naming, so the required
prefix/suffix no longer needs a separately supplied alignment certificate.
From a clean state whose carrier equals the decoded frontier, the counted
assembly and R/L port construction compose into one actual word, append
exactly one selected record, and restore the next frontier's clean state.
`CleanCodeInduction.lean` now decodes every ternary prefix into a source
frontier and exact ordered records, then constructs one actual clean word
whose origin, carrier and chain match that same decoder. Multi-atom
checkpoints are executed in one selected absorption rather than split into
singleton absorptions. `CleanOutside` literally supplies a physical site
holding the decoded carrier. The record result size and ordered left parent
recover each nonzero code position and its R/L side; consequently distinct
codes have distinct decoded chains. `ActualChainRange.lean` now proves every
actual registered selected chain lies in this decoder image and has a unique
code. Its equivalence uses the subtype of genuinely reachable chains, not all
record lists. `chainEquiv` alone only relates symbolic checkpoint data. The
cut-to-schedule bridge now starts from that chosen clean witness, deletes
exactly `k-t` non-target boundaries by actual outside fusions, and reaches
every valid `k>0` cut/phase/offset target without changing its origin or
selected chain. The reverse direction now extracts a valid target from every
actual registered endpoint of that chain. The finite rank encoder and decoder
are inverse, and the resulting rank parameters are unique across all positive
outside ranks for a fixed carrier arc.
The actual-state frontier theorem does not use cleanliness: the latest
selected record (or the origin before any selected absorption) names the
actual carrier in every registered singleton-seed history. Its complement is
one source interval. The next real selected merger takes a nonempty prefix
or suffix of that interval, uses the carrier at the corresponding kernel
port, appends the exact source-addressed record, and strictly increases the
checkpoint. The global reverse induction is now checked over literal `p,d`
words without assuming clean outside packets along arbitrary histories.
On the generated domain, a full carrier at one site already implies a genuine
one-packet placement by the Lean source-order invariant. Every full-carrier
code now has a generated clean witness, making its fixed-origin/fixed-chain
phase fiber unconditionally equal to the `n` physical rotations.
Conditional on one actually reachable full-carrier history, the Lean companion
also classifies the complete fixed-origin/fixed-chain full-carrier fiber and
proves it has exactly `n` states. Every actual registered chain now has a
unique code. For `k>0`, literal fixed-chain placements are equivalent to
positive-rank cut/phase/offset parameters. The later Lean companion now proves
registration-origin uniqueness for `n>=3`, packages the full-carrier phase
fiber as an actual placement equivalence, and assembles the complete generated
summaries into a finite code-indexed parameter sum. Lean also proves the
last-checkpoint regrouping and the closed actual-summary count for `n>=3`.
An independent six-state execution closure classifies the `n=2` case: two
pre-registration phases and four registered origin/phase states. The resulting
actual-summary count is `4`, and the combined count covers every `n>=2`.
The [end-to-end formalization milestone](FORMALIZATION_MILESTONE.md) records
the exact local Lean/Mathlib versions, 56-file SHA-256 closure, final theorem
signature, origin-sensitive dependency chain, and reproducible axiom audit.

## Replay

Python 3.13.0 and the standard library were used to generate and check the
retained record. From the repository root, run:

```text
python -O -B experiments/registered_absorption_chains/independent_bfs_check.py --check-result experiments/registered_absorption_chains/results/independent_bfs_n2_n7.v1.json
```

The command is read-only and exits nonzero if the saved JSON differs from a
fresh complete replay. `-O` checks that the validation does not depend on
Python assertions; `-B` avoids bytecode output. The expected registered-summary
counts for `n = 2,3,4,5,6,7` are `4,12,72,410,2244,11928`, respectively.
The `registered_summary_set_sha256` in each row is a digest of the sorted,
canonical JSON encoding of the complete registered-summary set. The record
does not contain that full set or the generating execution words.

[`replay-lock.v1.json`](replay-lock.v1.json) lists the exact source and result
bytes retained in this companion. Its digests are byte-integrity bindings,
not independent validation of the mathematics. The immutable Git commit
containing this directory is the public source snapshot; the HAL identifier
addresses the manuscript rather than retroactively anchoring these code bytes.
