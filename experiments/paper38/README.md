# Paper XXXVIII Return-Budget Control

**Status:** Paper XXXVIII version 1.0 paper-owned evidence package. The
[manuscript](../../papers/paper38/Paper%20XXXVIII.md) owns the
data-independent proofs. The development manifest remains a nested evidence
inventory; the release manifest and validation receipt bind the versioned
package separately.

**Execution status:** Python 3.11+; standard library only. Default validation
is read-only and includes separately implemented bounded replay.

**Paper evidence:** bounded consistency controls, not all-$g$ proofs or
independent Computational Certificates. A
[partial Lean algebraic spine](lean/README.md) checks selected product,
saturation, and initial-layer statements; it is not a complete formalization
of the all-$g$ geometry. No Paper XXXVII Lean source is imported.

## Fixed Scope

All cases have $n=5g$, $\Delta=g$, five source lineages filling an ordinary
lane, arbitrary declared local permutations, and all return labels. Each
terminal occurrence is charged one return. All earlier returns must be
injective. Exact counts $N=1,\ldots,26$ are checked separately from at-most
counts. The producer and result cannot redefine this range.

| Domain | Branch catalogue | Branches | Sources |
|---|---|---:|---:|
| $g=2$ | Every local $S_5$ restriction; punctured identity | 120 | 120 |
| $g=3$ | Six named profiles, two lane/puncture variants | 12 | 24 |
| $g=4$ | Same six profiles and two variants | 12 | 36 |

The six profiles and ordering are fixed in [audit_scope.py](audit_scope.py).
Every ordinary source lane is used. The $g=3,4$ catalogue is selected, not
exhaustive. The matched reflection-location family is separately checked
at $g=3,4,5$, always from source lane one.

These are newly produced controls. Previously reported scratch checks are
not copied, relabelled, or counted as additional evidence. The catalogue is
a consistency test, not a new subgroup census or sharp-constant search.

## Objects Checked

The producer constructs positive product layers retaining the first factor
$H\sigma_s$. For every terminal permutation it saves one actual label word
within the coset bound and checks all intermediate raw coordinate updates.

The validator imports only the declarative scope, not the producer. It
enumerates raw injection layers by explicit branch/rotation/collapse
actions. An internal successor is carried forward; a strict successor is
recorded only as terminal, never expanded. Exact layers permit revisiting
a state at different depths and do not stop when a cumulative layer fills.

The retained result uses canonical compact JSON rather than a raw-state
database. For each of the 26 counts, the complete terminal-permutation sets and the
ten complete source-addressed survivor sets are compared through canonical
fingerprints. All retained witness words are replayed on the same concrete
injection. Counts alone are not accepted as set equality. The cumulative
bound is checked without claiming that an exact layer contains the group.

The matched controls check identical group, aggregate, complete reachable
injections, and unbudgeted frontier; distinct first-layer survivor maps of
equal cardinality; and second-layer recovery. The first-layer distinction
is not a count separation.

## Inventory

| Path | Role |
|---|---|
| [audit_scope.py](audit_scope.py) | Fixed inputs, budget range, and closure allowlist |
| [return_budget_audit.py](return_budget_audit.py) | Algebraic producer and concrete witness constructor |
| [results/return_budget_audit_v1.json](results/return_budget_audit_v1.json) | Layer fingerprints and actual bounded label words |
| [validation/validate_return_budget.py](validation/validate_return_budget.py) | Separately implemented coordinate replay |
| [validation/validate_source.py](validation/validate_source.py) | Source, bibliography, cross-reference, and firewall lint |
| [validation/test_contract.py](validation/test_contract.py) | Negative scope, layer, witness, and environment tests |
| [validation/validate_package.py](validation/validate_package.py) | Read-only closure and default replay gate |
| [seal_manifest.py](seal_manifest.py) | Explicit mutation-authorized digest refresh |
| [development-manifest.json](development-manifest.json) | Selected exact-byte finite evidence closure |
| [release-manifest.json](release-manifest.json) | Candidate manuscript, PDF, build, and evidence identity |
| [release-environment.json](release-environment.json) | Recorded build and replay environment |
| [validation/validate_release.py](validation/validate_release.py) | Read-only release package and receipt check |
| [results/paper38_public_package_v1.validation-receipt.json](results/paper38_public_package_v1.validation-receipt.json) | Downstream local closure verification |
| [upstream-provenance.json](upstream-provenance.json) | Published XXXVII theorem source binding |
| [lean/README.md](lean/README.md) | Explicit partial-formalization coverage |
| [lean/formalization-manifest.json](lean/formalization-manifest.json) | Compiled sources and axiom footprint |
| [validation/validate_lean_formalization.py](validation/validate_lean_formalization.py) | Static formal closure or explicit compiler replay |

## Commands

Default closure verification with finite replay:

~~~powershell
python -B experiments/paper38/validation/validate_package.py
~~~

Source, closure, and fixed coverage only; explicitly skips mathematical replay:

~~~powershell
python -B experiments/paper38/validation/validate_package.py --static
~~~

Optional exact-byte comparison with the published upstream tag:

~~~powershell
python -B experiments/paper38/validation/validate_package.py --compare-upstream-tag
~~~

Default validation plus explicit Lean compiler and 30-declaration axiom replay:

~~~powershell
python -B experiments/paper38/validation/validate_package.py --lean
~~~

Default and `--static` modes verify the exact formal source/manifest closure
without requiring Lean, Mathlib, Git, or a dependency cache. Only `--lean`
performs a new compiler replay; it requires the pinned runtime. Generated
`.lake` files are ignored and do not belong to the paper closure.

Intentional authoring-time regeneration, then digest sealing:

~~~powershell
python -B experiments/paper38/return_budget_audit.py
python -B experiments/paper38/seal_manifest.py
~~~

After intentional Lean changes, run the formal validator with `--seal`
before sealing the outer development manifest. The formal sealer compiles
and audits before recording a compiled status; verification never seals.

Verification never regenerates the result or repairs a digest. It removes
`PYTHONOPTIMIZE` in subprocesses, uses explicit exceptions for mathematical
checks, prunes cache directories, and compares closure bytes before and
after verification. The manifest excludes itself from its artifact list.

## Upstream and Release Boundary

The inherited uniform edge law and unbudgeted classification belong to the
exact published Paper XXXVII tag named in the provenance record. No finite
upstream artifact is imported as budget evidence. Default verification
requires neither Git nor an upstream workspace: only the selected paper38
files. The optional comparison resolves the exact tag bytes and fails
closed without a tag; it never substitutes current HEAD. That comparison
is a byte-identity check, not a replay or proof of the upstream theorem.

The related-work audit and broader exploratory source tree are not release
dependencies. The reader PDF at `papers/paper38/paper38_arxiv.pdf`
belongs to the release manifest, not to the nested development manifest.
The receipt records local closure verification and finite replay; it neither
authenticates its own validator nor claims independent mathematical validation.
External deposit integrity is checked separately after publication.

## Known Nonclaims

The source is a supplied five-lineage full-lane configuration, not a whole
image asserted to be reachable from the initial Q. The lane-stabilizing
returns preserve the number of occupied residue classes modulo g, so the
entire normalized carrier E cannot enter one full ordinary lane. Neither
the finite replay nor the partial Lean spine certifies whole-image entry.

No sharp bound, exact-24 padding, deterministic right-coset transition,
minimal invariant, partial occupancy, restricted label menu, shortest raw
word, typed source supply, authorization, transfer, handoff, POS, recursive
compatibility, settlement, or reset theorem is established by these checks.
The conditional $24n$ raw-letter consequence needs its fixed blockwise
realization and excludes entry cost; this package does not supply that
realization for an unspecified source.
