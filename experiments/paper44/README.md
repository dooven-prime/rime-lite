# Paper XLIV Evidence Index

Status: numbered release candidate, not yet published. This directory is the
new publication-facing proof and control entry for Paper XLIV. It does not
give the earlier local draft a retroactive Git or HAL identity.

## Evidence ownership

| Result | Evidence | Boundary |
|---|---|---|
| Actual circular chains and fixed-chain placement fibres | Published Paper XLI v1.0, DOI `10.5281/zenodo.24137725` | Imported theorem, not reproved here |
| Future-event equivalence and distinguishing words | Published Paper XLIII v1.0, DOI `10.5281/zenodo.24148747` | Imported theorem, not a prefix count |
| Concrete prefix observer, actual normal forms, and Theorem 3.3 finite counts | [Lean structure/count milestone](lean/FINITE_COMBINATORIAL_MILESTONE.md) | All `n>=3`, `j>=1`; 102 bound inputs, 86 axiom-audit outputs |
| Fixed-depth and uniform growth, supercritical ratio, Gaussian window | [Paper XLIV manuscript](../../papers/paper44/Paper%20XLIV.md) | Paper proofs; not in the Lean milestone |
| Finite generated-domain minimization and arithmetic identities | [Bounded controls](controls/README.md) | `n=3..7`, 20 depth cases; not a proof of all-parameter claims |

The Lean milestone was created before this candidate had a public commit.
Its source-hash inventory is the proof input identity, not the recorded HEAD.
The copied manifest is at `lean/milestones/structure-count-v1/manifest.json`,
the path required by its unchanged read-only validator. Source and toolchain
bytes pass `--check-only` in this worktree. The prior local build and axiom
audit are recorded in the milestone, but this edition has not yet obtained a
separate clean-host replay or archive DOI.

## Read-only entry points

From `experiments/paper44/lean`:

```text
python -B freeze_structure_count.py --check-only
```

From `experiments/paper44/controls`:

```text
python -B -m unittest test_prefix_label_update test_prefix_observer_supercritical -v
python -B prefix_observer_spectrum_control.py --max-n 7
```

The candidate sequence remains: review the numbered mathematics and PDF,
run the Lean and control gates on a fixed source commit, freeze the content
tag, then deposit the tagged PDF and add downstream DOI metadata. None of
those later identities is asserted by this index.
