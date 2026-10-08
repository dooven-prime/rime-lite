# Paper XXXVII Bounded Ordinary-Lane Control

**Release status:** paper-owned version 1.0 content package.
The [manuscript](../../papers/paper37/Paper%20XXXVII.md) owns the
complete data-independent proofs.

**Execution status:** runnable with Python 3.11 or later and the standard
library only for default verification. Local release validation is read-only,
includes finite replay, and statically checks the partial formalization.
Explicit Lean replay additionally requires the pinned compiler and Mathlib.

**Paper evidence:** bounded consistency controls, not all-$g$ proofs or
independent Computational Certificates. A
[partial Lean spine](lean/README.md) freezes selected logic and algebra.
The release manifest binds the reader PDF and theorem-facing closure;
the local receipt does not assert a Git tag or external deposit.

## Fixed Finite Scope

All cases use $n=5g$, $\Delta=g$, a full ordinary source lane $C_{\rm src}$,
all return labels, and no word-length budget.

| Domain | Branch policy | Branches | Source cases |
|---|---|---:|---:|
| $g=2$ | All 120 local $S_5$ restrictions; punctured identity | 120 | 120 |
| $g=3$ | 12 named mixed profiles, both lane permutations, four punctured restrictions | 96 | 192 |

The $g=2$ slice is exhaustive only with its declared punctured restriction.
The $g=3$ catalogue is selected, not exhaustive in the full stabilizer.
[audit_scope.py](audit_scope.py) fixes the exact catalogue and ordering.
The result file cannot redefine the scope. Every ordinary lane is used as
a source.

Matched $F_{20}/S_5$ and $A_5/S_5$ controls are separately replayed at
$g=2,3,4$. The first has the same unsigned labelled mobility, local parity,
and ten fused pairs but two versus six survivors per pair. The second has
different complete reachable injection sets but equal complete survivor sets.

## Checked Objects

The producer saturates actual raw guarded injections and independently
computes the five-position group. It checks confinement, actual relocation,
phase and local-generator words, complete reachable and terminal sets,
right-phase-coset counts, deterministic phase descent, complete survivor
maps, and kernel-swap projection multiplicity.

Nonnormalizing branches retain concrete reachable phase-equivalent
representatives and a common label with different output phase classes.
This does not negate the phase state-set bijection.

The JSON retains inputs, counts, concrete phase witnesses, and SHA-256
fingerprints of canonical complete sets instead of duplicating a large
reachable-state database. Complete sets are materialized and compared
during both runs.

The validator shares only the declarative catalogue with the producer.
Action, reachability, group closure, cosets, terminal events, and survivor
projection have separate implementations. This is not independent
scientific validation under a different owner.

## Owned Files

| File | Role |
|---|---|
| [audit_scope.py](audit_scope.py) | Fixed input catalogue and package contract |
| [ordinary_lane_audit.py](ordinary_lane_audit.py) | Standard-library producer |
| [results/ordinary_lane_audit_v1.json](results/ordinary_lane_audit_v1.json) | Bound summary and set fingerprints |
| [validation/validate_ordinary_lane_audit.py](validation/validate_ordinary_lane_audit.py) | Separately implemented finite replay |
| [validation/validate_source.py](validation/validate_source.py) | Source, citation, numbering, and boundary lint |
| [validation/test_contract.py](validation/test_contract.py) | Negative coverage, digest, and environment tests |
| [validation/validate_package.py](validation/validate_package.py) | Default closure and replay gate |
| [seal_manifest.py](seal_manifest.py) | Explicit authoring-time digest refresh |
| [development-manifest.json](development-manifest.json) | Exact-byte draft closure, not release identity |
| [release-environment.json](release-environment.json) | Declared build environment |
| [release-manifest.json](release-manifest.json) | Version 1.0 release-content inventory |
| [results/paper37_public_package_v1.validation-receipt.json](results/paper37_public_package_v1.validation-receipt.json) | Local closure verification receipt |
| [validation/validate_release.py](validation/validate_release.py) | Read-only release closure and replay gate |
| [lean/README.md](lean/README.md) | Lean coverage map and supplied-hypothesis boundary |
| [lean/formalization-manifest.json](lean/formalization-manifest.json) | Bound compiled partial formalization |
| [validation/validate_lean_formalization.py](validation/validate_lean_formalization.py) | Static checks or compiler and axiom replay |

## Commands

Default read-only release verification, including complete finite replay:

~~~powershell
python -B experiments/paper37/validation/validate_release.py
~~~

Nested development closure verification:

~~~powershell
python -B experiments/paper37/validation/validate_package.py
~~~

Static closure/source/fixed-coverage checks only, explicitly skipping replay:

~~~powershell
python -B experiments/paper37/validation/validate_package.py --static
~~~

Default verification plus explicit Lean compiler and axiom replay:

~~~powershell
python -B experiments/paper37/validation/validate_package.py --lean
~~~

The compiler replay checks 15 declarations and permits only standard
propext, Classical.choice, and Quot.sound dependencies. It does not prove
the concrete normalized geometry or copy the finite database into Lean.
The right-coset state set and deterministic normalizer iff remain separate
formal results. Concrete geometric inputs to generated controllability
are declared hypotheses, not hidden formalization claims.

Intentional authoring-time regeneration and digest refresh:

~~~powershell
python -B experiments/paper37/ordinary_lane_audit.py --output experiments/paper37/results/ordinary_lane_audit_v1.json
python -B experiments/paper37/seal_manifest.py
~~~

After intentionally changing formal sources, compile and audit before
refreshing both manifests:

~~~powershell
python -B experiments/paper37/validation/validate_lean_formalization.py --seal
python -B experiments/paper37/seal_manifest.py
~~~

Verification never regenerates results or repairs digests. Child processes
remove PYTHONOPTIMIZE, and mathematical checks use explicit exceptions rather
than optimization-sensitive assertions. Cache directories are pruned before
inventory traversal.

## Provenance and Separation

The broader exploratory note remains proof provenance, not a second
authority. Previously discussed scratch checks remain provisional; this
package is freshly recomputed rather than importing or relabelling them.

The old B0 controls remain separately paused under
experiments/exploratory/raw_to_typed_alignment/. The unnumbered forest
consumer is also separate. Default validation reads no exploratory tree,
old synchronizing sources, direction ledger, unnumbered draft, or upstream
experiment package. None is a hidden dependency of this closure.

## Known Nonclaims

Passing local closure verification does not establish an all-$g$ proof,
exhaustive $g=3$ coverage, universal minimality, partial-lane classification,
shortest or budgeted paths, typed transfer membership, authorization,
handoff, projectability, recursive return, settlement, or a reset bound.
The Lean subset is not a complete formalization of the geometric theorem
surface and does not resume the other two projects.
