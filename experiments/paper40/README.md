# Paper XL: Q2 Snapshot and Bounded Replay

**Status:** Paper XL v1.0 release content with a paper-owned evidence subclosure. The
[manuscript](../../papers/paper40/Paper%20XL.md) owns the proofs.

**Execution:** Python 3.11+ and the standard library. Default validation extracts
the bound snapshot to a temporary directory and replays it without Git, network,
either development checkout, installed SOF, or an external checking tool.

**Evidence:** bounded consistency controls and `LOCAL_CLOSURE_VERIFICATION`,
not independent validation, a Computational Certificate or a machine proof.
The local receipt does not check any public tag or deposit. The
[release manifest](release-manifest.json) binds the canonical
manuscript, [reader PDF](../../papers/paper40/paper40_arxiv.pdf), bibliography,
source, results and validators. Its local receipt is not an external download
check. A local `PASS` is not a public-reproducibility claim.

## Reader Commands

From a RIME source archive or checkout containing this package:

```text
python -B experiments/paper40/validation/validate_release.py
```

This checks the release manifest and receipt, reruns the retained result from
a fresh extracted source, and runs nine package-boundary tests. It does not
modify bound files. For the development subclosure alone, run
`python -B experiments/paper40/validation/validate_package.py`. Its `--static`
mode checks integrity only; its optional `--receipt` writes outside the bound
package. The release receipt is excluded from its own closure.

For the standalone tool, extract [q2-source-v1.zip](source/q2-source-v1.zip)
and run from the extracted directory:

```text
python -B run_evidence.py
python -B q2_cli.py check examples/origin_read_failure.json
```

The archive README also gives a check-to-replay pipeline. The first command
runs all 30 application tests with no skips, the nine typed requests and the
earlier fixed operator controls. It emits JSON to stdout; optional output and
environment files must be outside the extracted source tree. No pip install
or other project is needed. The complete typed input language is included.

## Complete Typed Request Example

The manuscript's short request in Section 4 has the following `ECC_SYN_V1`
encoding. It is also supplied as `examples/origin_read_failure.json` inside
the source snapshot. The empty command menu isolates R; the read failure
also occurs with the Track commands in Section 5.2.

```json
{
  "language": "ECC_SYN_V1",
  "environment": {"defect": [0, 2, 0], "seed": [0, 1, 2]},
  "selected": [0, 1, 2],
  "program": {
    "q": {
      "kind": "pair",
      "left": {"kind": "query", "name": "CurrentPartition"},
      "right": {"kind": "query", "name": "SelectedBlock"}
    },
    "reports": [{
      "label": "origin_port0",
      "expr": {
        "kind": "snd",
        "value": {
          "kind": "fst",
          "value": {
            "kind": "field", "name": "parents",
            "value": {"kind": "query", "name": "OriginSnapshot"}
          }
        }
      }
    }],
    "commands": []
  }
}
```

`parents` is an ordered pair of `(position, block)` entries, so
`snd(fst(parents))` reads the block at the first kernel port. From the
extracted source root, PowerShell can send the result directly to replay:

```powershell
python -B q2_cli.py check examples/origin_read_failure.json |
    python -B q2_cli.py verify examples/origin_read_failure.json --result -
```

In a POSIX shell the same pipeline can be written on one line. The check
returns `FAIL_READ` with `dd` and `pdd`, equal q-values and report blocks
`{0,2}` and `{1,2}`. Replay returns `VALID_REJECTION_WITNESS`; it verifies the
separation, not complete domain exploration. Full syntax and type conventions
are in the snapshot's `Q2_LANGUAGE.md`; `q2_cli.py` is the check/verify entry,
`q2/model.py` supplies generated-domain exploration, and `q2/engine.py` and
`q2/replay.py` implement the decision and separate history replay.

## Source Ownership and Snapshot

The maintained implementation is in
`dooven-prime/sof-runtime`, `applications/event_causal_consumers/`.
The exported files and license are read from exact runtime content commit
`a4b3e48bd119908494c6d4de8619bffc01c1ecb9`; the exporter does not
substitute uncommitted working-tree bytes.
The ZIP is an immutable evidence mirror of the selected sources, not another
editable implementation. Its inner manifest lists each file and origin.
The [outer binding](source/snapshot.v1.json) records both the archive hash and
the inner manifest hash. The archive is deterministic: fixed member order,
timestamps and permissions, stored rather than version-dependent compression.
Runtime text is exported as UTF-8 LF; inherited release blobs retain exact bytes.

Three code files and the license from XXXIX commit
`b032b47ec47f28c8b2f65844abbe30dc3b38fef8` are carried inside the archive.
Their code hashes are checked again by the frozen-source loader. They are
bounded differential inputs, not a live dependency on the RIME checkout.
The archive contains MIT license notices for both source repositories.

## Fixed Replay Scope

| Positions | Defect | Selected F | Log states | Causal states |
|---:|---|---|---:|---:|
| 2 | (0,0) | {0,1} | 6 | 4 |
| 3 | (0,2,0) | {0,1,2} | 39 | 18 |
| 4 | (0,0,1,2) | {0,1} | 292 | 72 |

The nine typed controls yield five positives, two read failures, one guard
failure and one successor failure. All four rejections undergo separate
history replay. The retained [record](results/q2-controls.v1.json) includes
the requests, decisions, full rejection payloads, replay results, test IDs
and the earlier fixed controls. The latter retain the 84-to-72 forest/causal
comparison, its fiber counts, and one seven-position continuation. That
continuation is not an exhausted seven-position domain. No new census is added.

The 30 application tests and nine package tests have different roles. The
latter reject archive drift, missing/duplicate members, payload changes,
narrowed controls/counts, skipped tests and out-of-closure document links;
they do not add mathematical
coverage to the application theorem. `artifact_scope.py` fixes inventories
and expected controls independently of result records, so a result cannot
shrink its own claimed domain.

The replay verifier shares the grammar/type interpreter with the checker.
It reconstructs actual histories without calling producer updates, but is
not an external independent implementation of the whole language. Acceptance
needs complete exploration; replaying a negative pair alone proves no such
completeness. The retained environment describes the generating run, not a
requirement that future users reproduce that operating system.

## Evidence Order

```text
pinned sof-runtime commit + exact XXXIX blobs
  -> source archive + inner manifest
  -> source binding
  -> bounded result + observed environment
  -> development subclosure manifest
  -> release manifest (manuscript, PDF and evidence)
  -> local release validation receipt
  -> future public release anchor
```

The [development manifest](development-manifest.json) binds the manuscript,
bibliography, documentation, archive, results and source validators. It excludes
unnumbered working notes, live source trees, the reader PDF and the receipt.
The release manifest binds the additional PDF and release-checking inputs.
No result depends on a receipt or public anchor that follows it.

## Explicit Regeneration

Only maintainers need checkouts containing the two pinned source commits:

```text
python -B experiments/paper40/build_snapshot.py --runtime-root ../sof-runtime
```

Extract that newly built ZIP outside the repositories and run its
`run_evidence.py --output` with an absolute path to the candidate
`results/q2-controls.v1.json`, and `--environment` with an absolute path to
`environment.v1.json`. Then explicitly rebind:

```text
python -B experiments/paper40/freeze_closure.py --write
python -B experiments/paper40/validation/validate_package.py
python -B experiments/paper40/validation/validate_release.py --write-manifest
python -B experiments/paper40/validation/validate_release.py --write-receipt
python -B experiments/paper40/validation/validate_release.py
```

Verification never invokes export or rebind. Changing the implementation,
scope or paper bytes requires deliberate regeneration and review, not an
automatic repair of hash mismatches.

## Publication Gate and Nonclaims

At publication, distribute this exact ZIP and binding with the accepted paper
package at an immutable tag/commit or deposit. Replace the pending anchor
only after it exists, download the public bytes and check their hashes, and
replay from that download before claiming public reproducibility. A mutable
`master`/`main` link or an unpushed local tag is not that check. There is no
public source URL or DOI invented by this candidate package.

This is not a minimal-state synthesizer, a new generic equivalence algorithm,
a comparative benchmark, an efficiency claim, or evidence of broad utility.
It does not add SOFRS/Registry authority, a strict SOF morphism, adjoint or
spectral descent, old B0 compatibility, or a reset-bound result. The source
snapshot and local receipt alone establish none of these.
