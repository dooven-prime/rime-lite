# Paper XXVII Evidence Package

This directory is the paper-owned computational companion for *Entry Sections
and Relation-Valued Descent in Single-Defect Circular Automata*.

The package is independent of the historical discovery workspace at
`experiments/synchronizing_automata`.  Public commands, embedded source
closures, and paper links resolve only through `experiments/paper27`.

## Theorem Surface

- Fixed `n=6`: the intrinsic Entry section is evaluated on all `1800` rooted
  binary defects.  Its synchronizing indexed graph has `1704` instances,
  split into `1700` Type-I-admitting and `4` Type-II-only instances.
- Fixed `n=7`: the declared inherited scope contains `15120` selected rank-four
  checkpoint instances.  The source-rank-five selector uses only one-drop
  blocks; subsequent Type-I/Type-II labels belong to the rank-four completion
  relation.  The theorem-facing Low-Transport closure is the five-cell finite
  symbolic elimination recorded in `N7_LOW_TRANSPORT_PAPER_TABLES.md` and
  `single_defect_n7_extremal_negative_cell_exhaustion_v1.json`.
- The `n=7` theorem chain starts from the paper-owned 35-context extremal
  carrier input. Its admission record binds the exact pre-release discovery
  artifact from which the ordered context projection was taken; the larger
  discovery census is not part of the public package.

## Layout

- the directory root contains paper-owned producers, shared mathematical
  modules, and the theorem-facing table ledger;
- `results/` contains the admitted theorem input and bound JSON artifacts;
- `validation/` contains read-only artifact validators and the package-level
  release validator;
- `release-manifest.json`, `release-environment.json`, and
  `claim-surface-map.json` bind the public package.

## Closure Tiers

The package manifest separates three closures:

- **normative manuscript/build**: the canonical manuscript and paper-local
  bibliography;
- **theorem-facing computational**: code, results, notes, and validators used
  to validate the declared finite theorem surfaces;
- **public package documentation**: this evidence guide and its validation
  boundary.

Only the first two classes define the release identity. The validation receipt
binds each class separately and also binds the complete package inventory.
Historical drafts, discovery censuses, author audits, and review notes are not
part of the public package.

## Validation

Run the local closure validator from the repository root:

```powershell
python experiments/paper27/validation/validate_public_package.py
```

To write a self-excluded validation receipt after a successful check:

```powershell
python experiments/paper27/validation/validate_public_package.py --write-receipt
```

Mutation-authorized reconstruction is separate from validation:

```powershell
python experiments/paper27/reproduce.py
python experiments/paper27/reproduce.py --rebuild-n6-base --workers 8
```

The default command rebuilds the derived `n=6` artifacts and the `n=7`
theorem-facing chain from the admitted 35-context carrier input. The optional
flag first rebuilds the complete `n=6` base enumeration. The public package
does not claim to replay the excluded `n=7` discovery census.

## Claim Boundary

This package certifies fixed `n=6` and `n=7` statements only.  It does not
claim the Černý conjecture, Forced FFS, General FFS, an all-rank Entry-section
theorem, or a uniform all-`n` completion-menu bound.

The paper proves the displayed mathematical equalities. Bound artifacts check
their transcription and source provenance; replay status is recorded
separately, and the current receipt records no producer replay. The artifacts
are not substitutes for the paper proofs.

## Canonical Evidence Map

The manuscript owns the proofs and claim boundaries. The computational
closure retains only:

- the complete `n=6` base enumeration and its two theorem projections;
- the admitted `n=7` 35-context carrier input;
- the five derived `n=7` theorem artifacts;
- `N7_LOW_TRANSPORT_PAPER_TABLES.md`, which is parsed by the final fixed-scope
  validator.

Broader common-witness, inherited-section, and interface-design analyses are
discovery records rather than release artifacts.

## Provenance Rule

Equality of mathematical output does not by itself certify an old artifact
after its source closure changes:

```text
same output does not imply the same certified artifact
```

Canonical JSON uses repository-relative POSIX paths and LF line endings. The
default validator checks the existing receipt; `--write-receipt` is the
explicit refresh operation after successful closure validation.
