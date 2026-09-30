# Paper XXXI: Partial-Return Hostile Controls and Lean Spine

This directory is the paper-owned development package for
[Paper XXXI](../../papers/paper31/Paper%20XXXI.md). It is self-contained and
does not read the broader exploratory source tree.

**Status:** paper-owned release-candidate package. The nested development
manifest remains a non-publication evidence closure; the outer release
manifest and receipt bind the Version 1.0 reader package. Neither is an
independent mathematical validation of the manuscript.

## Evidence Layers

| Layer | Owned files | Scope |
|---|---|---|
| All-`n` mathematics | the manuscript | Branch normalization, cyclic-branch elimination, multi-lane Safe-Hit classification, and the bounded normalizer extension |
| Bounded hostile controls | `partial_return_audit.py`, `results/`, and `validation/` | Exhaustive replay of the retained finite domains |
| Lean spine | `lean/` and `validation/validate_lean_formalization.py` | Data-independent path, quotient, skew-transport, and claim-boundary implications |

The finite result has status `FINITE_SANITY_CHECK_NOT_ALL_N_PROOF`. It is a
development control, not an all-`n` proof or an independent Computational
Certificate. Lean elaboration checks only the declarations mapped in
[`lean/README.md`](lean/README.md); it does not formalize the lane arithmetic
or constructive hole-slide.

## Bounded Hostile Audit

The standard-library-only checker uses the normalized carrier
`E = Q \ {0}` and directly constructs every marked-pair plus
three-spectator state. It checks:

- for every `6 <= n <= 12` and every nonzero kernel separation, exact
  Safe-Hit reachability equals lane adjacency;
- lane adjacency is invariant on every enabled identity-branch edge;
- for `6 <= n <= 8`, every branch permutation is scanned and every
  normalizer is retained;
- the skew quotient edge and target equations;
- exact quotient reachability;
- identity-branch simulation and the normalizer sandwich; and
- the `u = +/-1` orientation-compatible classification.

The retained totals are:

| Domain | Retained total |
|---|---:|
| Cyclic-branch state cases | 93,720 |
| Enabled cyclic-branch labelled edges | 870,540 |
| Normalizer branches | 456 |
| Normalizer start-state cases | 70,560 |
| Orientation-compatible state cases | 36,760 |
| Normalizer quotient edges | 175,216 |

Replay the retained result from the repository root:

```powershell
python experiments/paper31/validation/validate_partial_return_audit.py
```

Regenerate it explicitly with:

```powershell
python experiments/paper31/partial_return_audit.py `
  --cyclic-min-n 6 --cyclic-max-n 12 --normalizer-max-n 8 `
  --output experiments/paper31/results/partial_return_hostile_audit_v1.json
```

## Lean Spine

```powershell
cd experiments/paper31/lean
lake build
cd ../../..
python experiments/paper31/validation/validate_lean_formalization.py --replay
```

The project pins Lean 4.33.0 and Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d`. The `.lake/` directory is local
build state and is excluded from the development closure.

## Development Closure

`development-manifest.json` binds the manuscript, bibliography, finite
producer and result, Lean sources and lock files, documentation, and
validators by SHA-256. It intentionally claims no release identity.
Research ledgers and historical drafts are intentionally excluded from this
closure and from the reader release.

```powershell
python experiments/paper31/validation/validate_package.py
python experiments/paper31/validation/validate_package.py --replay
```

## Claim Boundary

The package proves no additional all-`n` mathematics. In particular, it does
not classify normalizer multipliers outside `u = +/-1`, the broader
cycle-partition-preserving regime, survivor placement, typed transfer
membership, projectability, recursive return, settlement, or reset bounds.

## Release Validation

The public package validator binds the canonical manuscript, reader PDF,
paper-local bibliography, nested development closure, build environment, and
validator implementation. The receipt is excluded from its own closure.

```powershell
python experiments/paper31/validation/validate_public_package.py
python experiments/paper31/validation/validate_public_package.py --replay
```

`LOCAL_CLOSURE_VERIFICATION` records exact-byte and replay consistency. It is
not independent validation of the mathematical proofs.
