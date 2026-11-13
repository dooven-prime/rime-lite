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

The [critical-window proof review](review/CRITICAL_WINDOW_REVIEW.md) binds
the current manuscript, bibliography and reader PDF by SHA-256 and records
the exact decomposition and local-limit argument. It supersedes the old
unnumbered C1 review's open-status statement only for this numbered edition.
The review belongs to the GitHub candidate evidence, not to the Zenodo
reader PDF. The first-publication [candidate manifest](release-manifest.json)
binds its bytes along with the edition and its read-only validators.

The Lean milestone was created before this candidate had a public commit.
Its source-hash inventory is the proof input identity, not the recorded HEAD.
The copied manifest is at `lean/milestones/structure-count-v1/manifest.json`,
the path required by its unchanged read-only validator. Source and toolchain
bytes pass `--check-only` in this worktree. The prior local build and axiom
audit are recorded in the milestone. The candidate workflow recompiles the
pinned same-source package and compares fresh axiom outputs; this is not
independent cold-start reproduction. No archive DOI is claimed by this
candidate.

## Read-only entry points

From the repository root, check the numbered manuscript, PDF, bibliography,
published XLI/XLIII inputs, source locks and candidate manifest:

```text
python -O -B experiments/paper44/validation/validate_candidate.py
python -B -m unittest discover -s experiments/paper44/validation -p test_candidate.py -v
python -O -B experiments/paper44/validation/validate_controls.py
```

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

The prospective fusion-log paper is Paper XLV, separate from this first
numbered Paper XLIV. No HAL migration identity is claimed for XLIV.
