# Hosted Lean acceptance: M4-C, M4-D and M5

The job `M4-C/M4-D/M5 proof and frozen ancestors` in
`.github/workflows/fusion-log-lean.yml` builds three independently configured
Lake roots on GitHub-hosted Ubuntu, then runs their source-bound replay
validators and 29/27/64 transitive axiom audits. The workflow also runs the
11 ancestor/C, five D and eight M5 validation-gate tests. Finite mathematical
enumeration is not part of this job. Current proved scope is indexed in
[CURRENT_STATUS.md](CURRENT_STATUS.md); the root README stays byte-frozen.

## Source and Dependency Contract

`lean_m5` requires `lean_m4d`, which requires `lean_m4c`, which requires `lean_m4`, which
requires `lean`. The latter includes the fixed source mirror under
`lean/upstream`; it does not require another worktree or local Git object.
All roots retain the pinned Lean toolchain and Mathlib revision.

`validation/verify_ci_ancestors.py` resolves the annotated HAL source tag
to its fixed commit and checks the 21 declared source bytes at that tag.
The live M1-M3/M4-B/M4-C proof inputs must match their owning manifests.
M4-D verifies its own frozen inventory and exact M4-C ancestor.
M5 additionally resolves `fusion-log-m4d-source-v1.0` to its exact tag object
and content commit, reads its manifest and all 16 declared inputs at that
tag, and checks the separate live M5 inventory.

All Lean action invocations are commit-pinned. They download the official
Mathlib compiled cache, with GitHub project-build caching disabled. The
downstream roots share only the first root's external dependency directory on
this runner through a runner-created relative symlink. No `.lake`, local
absolute path, compiled project proof or machine junction is committed.

The package-local `.gitattributes` retains exact JSON bytes, including
historical Windows receipts. The proof files themselves remain the
manifest-bound source bytes; no theorem, old manifest or old receipt is
rewritten to claim a hosted run.

## Acceptance Receipts

`validation/collect_ci_receipts.py` cross-checks the actual replay reports,
Lean runtime commit, live Mathlib checkouts, ancestor manifests and axiom
inventories. It records both the PR source commit and actual checkout
commit, requiring the owned trees to agree, then writes the runner context
and SHA-256 of each receipt. `collect_ci_m5_receipts.py` separately checks
the M5 report, its 64-target axiom inventory, actual Mathlib checkout and
exact M4-D ancestry, then binds the unchanged C/D context. The collectors require a Linux
GitHub Actions environment; a local source-gate pass is not a hosted run.

The artifact `fusion-log-proof-receipts-<run_id>-<attempt>` retains
the C/D receipts and `runner-context.json`, plus `m5-ancestor.json`,
`m5-replay.json` and `m5-runner-context.json` for 90 days. Successful acceptance requires
the complete job and receipt cross-check to succeed. Incomplete artifacts
from failed attempts are diagnostic, not acceptance evidence. Download and
archive the successful receipts before their GitHub retention expires.

The M4-D source identity is fixed independently of this M5 extension.
A green M5 job binds its actual run and source commit; it
does not create a release tag or merge the PR. Public M5 identity is
fixed only after review and merge. Section 5 belongs to M5; all-R optimality
and shortest-word uniqueness remain later proof stages. PR and master-push
triggers avoid duplicate branch-push/PR jobs for the same candidate.

## Local Commands

Run from this experiment directory, with the pinned Lean toolchain installed:

```text
python -B validation/verify_ci_ancestors.py
python -B validation/replay_m4c.py --cache --report results/my-m4c-replay.json
python -B validation/replay_m4d.py --cache --report results/my-m4d-replay.json
python -B validation/replay_m5.py --cache --report results/my-m5-replay.json
```

Do not overwrite existing reports. Local commands do not set hosted-run
status. No branch protection or automatic merge is configured here; a
path-filtered workflow must not become required without an always-present
status policy for unrelated changes. No publication action is performed.
