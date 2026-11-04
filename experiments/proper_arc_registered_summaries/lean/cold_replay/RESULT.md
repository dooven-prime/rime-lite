# Proper-Arc Isolated Cold Replay

Completed on 2026-11-04. The final run status is
`PASS_ISOLATED_COLD_REPLAY_WITH_FRESH_OFFICIAL_MATHLIB_CACHE`.

## Result

All nine owning validators recomputed their complete target signatures,
axiom sets and declaration graphs and matched their frozen reports.

| Layer | Axiom Queries | Report Targets | Graph Nodes | Replay |
|---|---:|---:|---:|---|
| M1: origin construction | 26 | 4 | 5,329 | PASS |
| M2: origin interfaces | 5 | 4 | 5,334 | PASS |
| M3: exhaustive origin classification | 23 | 9 | 8,268 | PASS |
| M4: constructive ternary chains | 34 | 11 | 9,420 | PASS |
| M5: actual chain equivalence | 34 | 15 | 11,160 | PASS |
| M6: actual placement fibres | 32 | 15 | 12,761 | PASS |
| M7: dependent actual summaries | 30 | 15 | 10,501 | PASS |
| M8: exact summary counts | 17 | 12 | 13,382 | PASS |
| M9: combinatorial refinements | 28 | 16 | 12,215 | PASS |

The 229 queries and 101 report targets overlap across layers. Only
`propext`, `Classical.choice` and `Quot.sound` occur as axiom leaves.
All ten test suites passed, totaling 94 tests. The final theorem-map check
covered the 17 selected theorem entries and the 13,621-node union graph.
The union graph counts all audited declarations in the nine frozen reports,
not merely the union of the 17 selected theorem closures.

Union graph SHA-256:
`ef8b4326ceb91811346672ae41fd577cb089bf0829bb7027464a7d86a85d55da`.

## Bound Environment

- Manuscript worktree base: `2a30449b9dc37a36b25b277ebc006515c2addb59`.
- Lean 4.33.0: `d8b18978322de05a8f3dba51ef03cf5461676c17`.
- Mathlib: `db584cd6d46c92f209a44c0f1c829460d327499d`.
- Unchanged Lake lock SHA-256: `1a40688690ef2b536dc9297406625a36b4989fafa5b6e5b1b76390b9a60532ec`.
- 99 unique frozen inputs, delivered in a 125-file source/evidence overlay.

The detached worktree was pristine before the overlay. No previous project
build, package junction, local Mathlib compiled cache or installed Lean
toolchain was copied. The toolchain was downloaded anew; its ZIP CRC,
archive SHA-256 and executable version were checked. All locked dependency
revisions and tracked source cleanliness were checked before and after
replay. The official cache tool downloaded 2,990 dependency artifacts;
the project proofs were compiled in the cold directory.

Mathlib source acquisition required a recorded recovery after Git transport
failures. Official API data reconstructed the exact pinned commit and every
tree object; all 9,032 archive blobs matched that tree. The successful
bootstrap is `mathlib-archive-bootstrap.v3.json`. Earlier transport and
bootstrap failures are retained, not converted into successful attempts.

This was a separate environment on the same Windows host, using the official
Mathlib compiled cache rather than a full Mathlib source rebuild. The source
overlay has local SHA-256 identity, not a new public companion commit or tag.
The original nine manifests/reports and HAL v1 proof identity are unchanged.
The Lean README's new result link is downstream documentation; the copied
README bytes at replay time remain bound in the source snapshot.

## Evidence and Recheck

The [evidence manifest](results/isolated-windows-v1/evidence-manifest.v1.json)
binds the final receipt, source snapshots, acquisition records and all 77
command logs. The [final receipt](results/isolated-windows-v1/cold-replay.v1.json)
records exact commands, durations, log hashes, dependency revisions and the
matched graph digest. Downloaded archives and build binaries are not included
in this compact evidence bundle.

From the owning Lean directory:

```powershell
python -B cold_replay/verify_result.py --evidence cold_replay/results/isolated-windows-v1
```

This checks evidence closure without executing Lean again. The
[replay instructions](README.md) describe a new acquisition and kernel run.
The [theorem-to-source map](../THEOREM_TO_SOURCE_MAP.md) remains the theorem
ownership and source-location entry.

Fixed-pair actual-type specialization and the generating-function/asymptotic
layer were not started by this replay.
