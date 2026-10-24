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
