# Fusion-log Lean companion: development after HAL v1

The mathematical reader is frozen at source tag
`fusion-log-compression-source-v1.0`, commit
`41cf746a095ecd06d85cb3d1184d58e7bfdd5979`. This development work does
not modify that snapshot, its controls or its PDF. The HAL submission
identity is recorded separately in the downstream repository metadata.

## M1-M3 baseline

The 76-file local M3 package was imported byte-for-byte from its existing
proof manifest and upstream pin. It has its own 51-source upstream mirror,
Lean/Mathlib locks, theorem map and saved receipt. The copied
`proof-manifest.v1.json` and its inputs are unchanged; the original
exploratory files are also untouched.

From this directory:

```text
python -B validation/replay.py --verify-inputs-only
python -B validation/replay.py
```

The latter replays the build and 18 targeted transitive axiom checks.
The saved v1 receipt is retained unchanged rather than rewritten to
pretend it came from this worktree.

## M4 extension

`lean_m4/` is a separate Lake project requiring `../lean`. Thus adding
M4 modules does not change the M3 source inventory or aggregate imports.
It uses the same execution semantics and the same complete-log wrapper,
not a replacement state model.

The new stage follows this chain:

```text
actual event trace and first-fusion split
 -> fusion-free packet-partition invariance
 -> actual first-event route retaining its gap and matching successor partition
 -> actual rank-drop / evolving-hole ledger
 -> budgeted complete-event replay on source-ordered states
 -> M3 alignment of the literal endpoint, retaining its batch plan
 -> one joint certificate satisfying B(n,t,s), K and M.
```

Its precise interfaces and remaining M4 obligations are in
[`lean_m4/README.md`](lean_m4/README.md). This is a companion development
stage, not a new machine-proof claim for the deposited paper.

The active extension is bound by `m4-development-manifest.v2.json` and its
budgeted replay receipt. The previous v1 sources, manifests and receipt
are preserved byte-for-byte under `milestones/m4-source-ordered-v1/`;
the root-level v1 manifest is historical and no longer describes active
M4 sources. The package-level README and M3 theorem map remain unchanged
members of the frozen M3 closure; use this page for extension status.

The new result is all-parameter on the existing `SourceOrdered` / `ZMod n`
domain, not yet the arbitrary-atom / arbitrary-initial-packet bridge.
It does not extend the independent admissible-schedule converse, fibre
counting or all-R optimality formalization. No public companion version
identity or independent cold replay is claimed by this local milestone.
