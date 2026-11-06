# Fusion-log compression: independent Lean development package

Status: **M1-M3 checked locally** (2026-11-05). This is a development
companion, not a published release or a proof of the full compression paper.

The exploratory directory was copied here and left unchanged. This package
has its own source inventory, dependency lock and replay gate; it no longer
depends on a sibling exploratory checkout.

## Completed Interface

For `n >= 3`, two eligible placements of the same `r >= 1` named,
nonempty, disjoint packets in the same positive cyclic order admit one
actual chronological `p,d` word with:

- no effective fusion at any intermediate step;
- exact literal endpoint placement;
- unchanged registration, selected chain and complete fusion log;
- at most `(3*n-r)*(r-1) + (n-1)` unit-cost raw letters.

The main declarations are `sameOrderPlacement_short` and
`sameOrderPlacement_logged` in
[lean/FusionLogCompression/M3Placement.lean](lean/FusionLogCompression/M3Placement.lean).
They are generic in the atom type; eligible named placements supply the
finite packet partition. Rank one uses only a phase rotation. Full rank
has no positive gap flow.

[M3_THEOREM_MAP.md](M3_THEOREM_MAP.md) records the exact interfaces,
owners, proof chain and correspondence with manuscript Proposition 3.3.

## Reproduce

From this directory, using Python 3.10+ and the installed pinned Lean:

```text
python -B validation/replay.py --verify-inputs-only
python -B -m unittest discover -s validation -p test_replay.py
python -B validation/replay.py --cache
```

The first command checks source identity only. The last command builds the
package and audits 18 named declarations and their transitive axiom sets.
[REPRODUCING.md](REPRODUCING.md) gives dependency acquisition, explicit
toolchain selection and optional report commands.

## Dependencies and Evidence

- Lean `leanprover/lean4:v4.33.0`, runtime commit
  `d8b18978322de05a8f3dba51ef03cf5461676c17`.
- Mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`, with transitive
  dependencies pinned by `lean/lake-manifest.json`.
- 51 upstream Lean sources from RIME commit
  `050cf8ec11e3db263830b46ea95e4062b8e08869`, vendored unchanged under
  `lean/upstream/`; exact provenance and hashes are in
  [upstream-pin.v1.json](upstream-pin.v1.json).
- [proof-manifest.v1.json](proof-manifest.v1.json) binds the local proof
  sources, audit, launcher and lock. The saved local replay is
  [results/m3-replay.v1.json](results/m3-replay.v1.json).

The local replay used a copy of already available Mathlib build artifacts;
it is not an independent cold replay. All 18 audited targets allow only
`propext`, `Classical.choice` and `Quot.sound`.

## Next Boundary

M4, the induction replaying an entire admissible effective fusion log,
remains open here. M2's source-boundary extraction currently uses
`ZMod n` atoms; a generic arbitrary-start initialization/order bridge is
separate. No shortest-word optimum or full-paper formalization is attached
to M3. The frozen upstream and manuscript candidate bytes are unchanged.
