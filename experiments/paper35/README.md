# Paper XXXV: Order-Phase Evidence

The [manuscript](../../papers/paper35/Paper%20XXXV.md),
[reader PDF](../../papers/paper35/paper35_arxiv.pdf), and
[Zenodo deposit](https://doi.org/10.5281/zenodo.23085408) identify Paper XXXV
v1.0. The manuscript proves the all-\(n\) one-lane results. This directory
retains a supplementary proof note, a partial Lean formalization, and an
exhaustive finite consistency control; none replaces the manuscript proof.

The GitHub content package remains a release candidate until committed and
tagged. The local receipt does not claim an external publication anchor.

## Verify

From the repository root:

~~~powershell
python -B experiments/paper35/validation/validate_release.py
~~~

The default check is read-only. It verifies exact package bytes, replays the
120-branch six-point control, and compiles the declared Lean spine. It also
checks the upstream inheritance gate against the exact published Paper XXXII
and XXXIV tag identities. A missing or changed bound file fails the check.

## Package Map

| Path | Role |
|---|---|
| [ONE_LANE_ORDER_PHASE_SURVIVOR_THEOREM.md](ONE_LANE_ORDER_PHASE_SURVIVOR_THEOREM.md) | supplementary proof provenance |
| [lean/](lean/) | bounded formalization and its pinned source closure |
| [order_phase_audit.py](order_phase_audit.py) | exact finite producer |
| [results/order_phase_n6_v2.json](results/order_phase_n6_v2.json) | retained 120-branch result |
| [development-manifest.json](development-manifest.json) | nested source inventory; no release identity |
| [release-manifest.json](release-manifest.json) | selected release and package-byte inventory |
| [results/paper35_public_package_v1.validation-receipt.json](results/paper35_public_package_v1.validation-receipt.json) | local closure verification record |

The release receipt is excluded from its own closure. The finite audit checks
the six-point no-internal-hole fiber only as a bounded consistency control; it
does not prove the all-$n$ theorem. Lean checks phase logic, the
left-coset type boundary, survivor-product counting, and a conditional
forward-invariance consequence; it does not formalize the complete guarded
geometry proof. The inheritance gate verifies upstream packages without
extending their theorem scopes. None of these checks establishes typed
transfer, projectability, recursive return, or a reset bound.
