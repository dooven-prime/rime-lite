# Paper XXXVI: Bounded Signed-Lane Control

The [manuscript](../../papers/paper36/Paper%20XXXVI.md),
[reader PDF](../../papers/paper36/paper36_arxiv.pdf), and
[Zenodo deposit](https://doi.org/10.5281/zenodo.23093673) identify Paper XXXVI
v1.0. This directory contains its bounded consistency control. The manuscript
proofs, not the finite scan, establish the all-$g$ results.

The content manifest identifies the exact repository package. The local
receipt does not attest the Git tag or Zenodo deposit; those are checked by a
separate post-release anchor.

## Verify

From the repository root, run:

~~~powershell
python -B experiments/paper36/validation/validate_release.py
~~~

The default check is read-only. It verifies the release inventory and receipt,
then replays the declared finite control with a separate implementation. A
passing result reports 5,040 branches and 9,840 source cases; a missing or
changed bound file fails the check.

## Object and Scope

The control uses the normalized return
$\phi_r^{(a)}=\varepsilon_\Delta p^r a$ for
$n=5g$, $\Delta=g$, and $g\in\{2,3\}$. Each source injection fills one
ordinary lane $C_{\rm src}$ with five labels in positive cyclic order.
All ordinary-lane permutations, independent local signs and phases, and
all four-point punctured-lane permutations are included. There is no
word-length budget.

The retained scope is exhaustive within these two finite domains:

| $g$ | Branches | Source cases |
|---:|---:|---:|
| 2 | 240 | 240 |
| 3 | 4,800 | 9,600 |

For each source case, the producer checks the complete guarded
injection-reachability set, the signed phase classes, full-support guards,
and the source-addressed survivor spectrum. The identity/reflection
matched control separately checks equality of all unsigned labelled
internal edges and boundary exponents, and the differing survivor counts.

## Package Map

| File | Role |
|---|---|
| [signed_lane_audit.py](signed_lane_audit.py) | standard-library exact producer |
| [results/signed_lane_audit_v1.json](results/signed_lane_audit_v1.json) | retained bounded result |
| [development-manifest.json](development-manifest.json) | exact-byte nested source inventory; no release identity |
| [validation/validate_package.py](validation/validate_package.py) | source audit and separately implemented finite replay |
| [release-manifest.json](release-manifest.json) | selected manuscript and package-byte inventory |
| [results/paper36_public_package_v1.validation-receipt.json](results/paper36_public_package_v1.validation-receipt.json) | downstream local closure verification record |

The receipt is excluded from its own closure. Its `PASS` status records
declared file integrity and finite replay, not independent mathematical
validation. The direction ledger and broader exploratory tree are outside
this package.

## Claim Boundary

The result does not prove Theorems 3.3, 4.3, or 5.1 for arbitrary $g$.
It does not check partial-lane sources or the full lane stabilizer, and
it supplies no typed transfer, projectability, recursive-return,
settlement, or reset-bound conclusion. It is not a second theorem
authority or a computational certificate for a universal theorem.
