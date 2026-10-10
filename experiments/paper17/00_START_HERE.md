# Paper XVII: Start Here

**Status:** unpublished publication candidate-2. **Execution authority:** none;
the registered primary and MTS-1 computations have completed. This is the
current navigation page. The root `README.md` and `mechanism/README.md` are
byte-bound historical snapshots, not current package summaries. Their
no-external-anchor statements describe the state at the earlier anchor. Do
not edit them or rerun their one-time registration producers to tidy prose.

## Shortest Paths

| Need | Open |
|---|---|
| Read the claim and its limits | [Manuscript](../../papers/paper17/Paper%20XVII.md), [reader PDF](../../papers/paper17/paper17_arxiv.pdf) |
| Map manuscript claims to exact records | [Evidence table v2](manuscript-evidence-table.v2.json) |
| Check reduced-domain admission and the frozen primary output | [D0 admission](results/finite_history_D0_admission.v1.json), [primary output](results/finite_history_closure.v1.json) |
| Check the common-support correction and two fiber fates | [Common support](results/finite_history_common_support_audit.v1.json), [fiber decomposition](results/finite_history_transient_fiber_audit.v1.json) |
| Check the terminal-image limit | [Terminal-image audit](results/finite_history_terminal_image_audit.v1.json) |
| Check the MTS-1 finite classification and global pair quantifier | [Classification](mechanism/results/mts1-v1/validation/mechanism_classification.v1.json), [global tally](mechanism/results/mts1-v1.global-pair-tally.v1.json) |
| Check the external data deposit binding | [Zenodo sidecar anchor](mechanism/results/mts1-v1.zenodo-anchor.v1.json) |
| Check the complete persistent effective-drive boundary | [Readout](mechanism/post_result_audits/EFFECTIVE_DRIVE_BOUNDARY.md), [exact cache audit](mechanism/post_result_audits/persistent_safe_effective_drive.v1.json) |
| Check current package membership and validation status | [Manifest v2](release-manifest.v2.json), [local receipt v2](results/release.v2.validation-receipt.json) |

The paper-owned public gate is read-only. From the repository root, run with
the Python 3.12.6 environment and dependency versions in
`requirements-exact-optimized-v1.txt`:

```powershell
$py = $env:RIME_PY312
if (-not $py) { throw 'Set RIME_PY312 to the pinned Python 3.12 executable.' }
& $py experiments/paper17/validation/validate_public_package.py
& $py experiments/paper17/validation/validate_release_v2.py
```

The first command checks nine retained local receipts and tests. The second
also checks the current manifest, the compact drive-audit bindings and
coverage, and preservation of the prior candidate's replaced artifacts. Neither
command reruns microscopic producers or independently replicates the result. Full
MTS-1 pair-shard replay is a separate, optional local check requiring the
approximately 4.84 GB exact sidecar:

```powershell
& $py experiments/paper17/mechanism/audit_global_pair_tally_v1.py
```

## What Belongs Where

- `results/` holds the frozen finite-history result and its later exact audits.
- `mechanism/results/` holds the completed MTS-1 census, global pair tally,
  compact inventory, and external deposit binding. The deep `mts1-v1/`
  layout follows the frozen source-cache/pair-record sidecar identity; it is
  not a second paper.
- `validation/` and `mechanism/validation/` contain the paper-local checks.
- Root registration, cost, and preflight files and the older READMEs are
  historical production context. Their status labels are not the current
  release-candidate status.
- MTS-1.1 and MTS-1.2 are separate, completed integration-worktree research
  records. Their intervention and initial-transition results are not in this
  publication closure and contribute no Paper XVII claim.
- `.runtime-work/`, `__pycache__/`, compiled kernels, and scratch output are
  local caches, not release artifacts.

The current release manifest separates theorem-facing and validation identity
from package-only historical records. Do not infer claim authority from a
file's presence in this directory. The MTS-1 sidecar is externally anchored
as described below, but clean-clone microscopic generation, independent
validation, and independently authenticated pre-execution chronology remain
unclaimed.

## Candidate-2 Promotion Boundary

Certificate 7.3 explicitly promotes one later cache audit: all five persistent
cohorts, 102 sources and 306 saved records at times 1,2,3. On the declared
common support 2,3, all 204 members of the ten non-singleton fibers have zero
clipped drive. Those fibers account for all 194 redundant windows; common
linear leakage therefore suffices to preserve their one-step equality.
The time-1 readout does not enlarge the common-support factorization.

The existing scientific results, registrations, inventory, external data
anchor, and candidate-1 receipts remain unchanged. `release-manifest.v1.json`
is historical; it is not the gate for the revised reader artifacts. Its seven
replaced artifacts are preserved byte-for-byte under
`release-snapshots/paper17/1.0-candidate-1/`, with an explicit map in manifest
v2. They are provenance, not a second claim authority. Manifest v2 and its
new downstream receipt bind the current candidate without re-signing old
scientific outcomes. The manuscript owns Certificate 7.3; its readout note
is supplementary documentation.

Default validation checks compact bindings and aggregate consistency, not
all exact source payloads. After materializing the frozen MTS-1 sidecar at
the inventory-declared paths, the optional full drive replay is:

```powershell
& $py experiments/paper17/mechanism/validation/audit_persistent_safe_effective_drive_v1.py --check
```

This command decodes the saved exact caches and recomputes clipping. It does
not traverse the signed operator or regenerate microscopic trajectories.

## Post-Freeze Evidence Bindings

### Global Pair Quantifier

The frozen MTS-1 classifier proves four all-versus-none separators within 15
shared-initial-stratum comparison cells. Those cells do not include TO-06
(three transient pairs) or PS-03 through PS-05 (180 persistent pairs). The
append-only `mechanism/results/mts1-v1.global-pair-tally.v1.json` replays all
33 exact pair shards, checks their SHA-256 against the frozen sidecar inventory,
reconstructs canonical pair membership, and evaluates the same seven frozen
predicates. At both `2_TO_3` and `3_TO_4`, the two decisive predicates each
have counts 570/570 transient and 0/1755 persistent.

With the exact sidecar present,
`& $py experiments/paper17/mechanism/audit_global_pair_tally_v1.py` performs a
read-only full tally replay.
The retained tally receipt binds that replay result and its code. Without the
sidecar, `& $py experiments/paper17/validation/validate_mts1_evidence_interface_v1.py` checks
only the compact bindings, aggregate arithmetic, and frozen-cell agreement;
it does not claim to replay pair shards.

### External Data Anchor

The MTS-1 exact sidecar is a split data deposit at
[Zenodo DOI 10.5281/zenodo.23234143](https://doi.org/10.5281/zenodo.23234143).
`mechanism/results/mts1-v1.zenodo-anchor.v1.json` binds the frozen inventory
to the 17 published files, their published sizes and MD5 metadata, locally
computed part SHA-256 values, and the locally reconstructed archive SHA-256.
The remote files were not downloaded in full for independent SHA-256 replay.
The DOI identifies the data deposit, not the manuscript. Neither this anchor
nor the tally establishes a clean-clone producer replay, independent
validation, or independently authenticated registration chronology.
