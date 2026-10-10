# Paper XVII: Start Here

**Status:** unpublished release candidate. **Execution authority:** none;
the registered primary and MTS-1 computations have completed. This is the
current navigation page. The root `README.md` and `mechanism/README.md` are
byte-bound historical snapshots, not current package summaries. Their
no-external-anchor statements describe the state at the earlier anchor. Do
not edit them or rerun their one-time registration producers to tidy prose.

## Shortest Paths

| Need | Open |
|---|---|
| Read the claim and its limits | [Manuscript](../../papers/paper17/Paper%20XVII.md), [reader PDF](../../papers/paper17/paper17_arxiv.pdf) |
| Map manuscript claims to exact records | [Evidence table](manuscript-evidence-table.v1.json) |
| Check reduced-domain admission and the frozen primary output | [D0 admission](results/finite_history_D0_admission.v1.json), [primary output](results/finite_history_closure.v1.json) |
| Check the common-support correction and two fiber fates | [Common support](results/finite_history_common_support_audit.v1.json), [fiber decomposition](results/finite_history_transient_fiber_audit.v1.json) |
| Check the terminal-image limit | [Terminal-image audit](results/finite_history_terminal_image_audit.v1.json) |
| Check the MTS-1 finite classification and global pair quantifier | [Classification](mechanism/results/mts1-v1/validation/mechanism_classification.v1.json), [global tally](mechanism/results/mts1-v1.global-pair-tally.v1.json) |
| Check the external data deposit binding | [Zenodo sidecar anchor](mechanism/results/mts1-v1.zenodo-anchor.v1.json) |
| Check exact package membership and validation status | [Release manifest](release-manifest.v1.json), [local receipt](results/release.v1.validation-receipt.json) |

The paper-owned public gate is read-only. From the repository root, run with
the Python 3.12.6 environment and dependency versions in
`requirements-exact-optimized-v1.txt`:

```powershell
$py = $env:RIME_PY312
if (-not $py) { throw 'Set RIME_PY312 to the pinned Python 3.12 executable.' }
& $py experiments/paper17/validation/validate_public_package.py
& $py experiments/paper17/validation/validate_release.py
```

The first command checks nine retained local receipts and tests. The second
also checks every artifact explicitly listed in the release manifest. Neither
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
- `mechanism/MTS1_1_INITIAL_TRANSITION_DECOMPOSITION.md` and its registration
  describe a later, unexecuted question. They are not in this release
  manifest and contribute no Paper XVII result.
- `.runtime-work/`, `__pycache__/`, compiled kernels, and scratch output are
  local caches, not release artifacts.

The current release manifest separates theorem-facing and validation identity
from package-only historical records. Do not infer claim authority from a
file's presence in this directory. The MTS-1 sidecar is externally anchored
as described below, but clean-clone microscopic generation, independent
validation, and independently authenticated pre-execution chronology remain
unclaimed.

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
