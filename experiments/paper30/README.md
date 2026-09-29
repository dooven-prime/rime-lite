# Paper XXX: General-Defect Return-Group Controls

This directory is the paper-owned development package for
[Paper XXX](../../papers/paper30/Paper%20XXX.md). It has no dependency on the
private exploratory synchronizing-automata tree.

**Status:** paper-owned release-candidate package. The nested development
manifest remains a non-publication evidence closure; the outer release
manifest and receipt bind the Version 1.0 reader package. Neither is an
independent mathematical validation of the manuscript.

## Evidence Layers

| Layer | Owned files | Scope |
|---|---|---|
| All-$n$ mathematics | the manuscript | Universal returns, exact orbit reduction, punctured rotation, branch completion, and cycle gluing |
| Bounded consistency control | `return_group_audit.py`, `results/`, and `validation/validate_return_group_audit.py` | Exhaustive replay for $6\le n\le8$ |
| Lean spine | `lean/` and `validation/validate_lean_formalization.py` | Data-independent quotient, gluing, and fixed-fiber implications |

The finite result is marked `FINITE_SANITY_CHECK_NOT_ALL_N_PROOF`. The finite
audits are bounded consistency controls bound into the development closure.
They are not proofs of the all-$n$ theorems and are not promoted as independent
Computational Certificates. Lean elaboration checks only the declarations
listed in `lean/README.md`; it does not formalize the punctured-rotation number
theory or the manuscript's constructive permutation realizations.

## Finite Return-Group Audit

The standard-library-only checker fixes coordinates

$$
k_0=0,\qquad k_1=\Delta,\qquad m=n-1,
$$

and exhausts every branch-completion permutation $a\in\operatorname{Sym}(E_0)$
for $6\le n\le8$ and every nonzero separation $\Delta$. It checks:

- exact reconstruction of a binary-kernel rank-$(n-1)$ defect;
- the universal return permutations and the conjugacy
  $b_0^{-1}h_db_0=\psi_\Delta$;
- the predicted punctured-rotation cycle type;
- equality between point orbits and cycle-gluing components;
- realization of every unrestricted cycle partition; and
- the fixed-collision fiber size and exact forced-join/isolation criterion.

Run the retained replay from the repository root:

```powershell
python experiments/paper30/validation/validate_return_group_audit.py
```

Regenerate the retained result explicitly with:

```powershell
python experiments/paper30/return_group_audit.py `
  --min-n 6 --max-n 8 `
  --output experiments/paper30/results/general_defect_return_group_audit_v1.json
```

## Lean Spine

```powershell
cd experiments/paper30/lean
lake build
cd ../../..
python experiments/paper30/validation/validate_lean_formalization.py --replay
```

The Lean project pins Lean 4.33.0 and Mathlib revision
`db584cd6d46c92f209a44c0f1c829460d327499d`. See
[`lean/README.md`](lean/README.md) for the declaration-to-manuscript map and
the explicit noncoverage boundary.

## Claim Boundary

Nothing in this package proves a general coloring-orbit classification,
Safe-Hit criterion, survivor-incidence frontier, typed transfer membership,
projectability, recursive return, credit settlement, or reset bound. The
paper remains the authority for the all-$n$ mathematics.

## Release Validation

The public package validator binds the canonical manuscript, reader PDF,
paper-local bibliography, nested development closure, build environment, and
validator implementation. The receipt is excluded from its own closure.

```powershell
python experiments/paper30/validation/validate_public_package.py
python experiments/paper30/validation/validate_public_package.py --replay
```

`LOCAL_CLOSURE_VERIFICATION` records exact-byte and replay consistency. It is
not independent validation of the mathematical proofs.
