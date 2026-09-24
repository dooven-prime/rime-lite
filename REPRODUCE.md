# Reproduce

This file is a non-normative human navigation layer. It does not define a
claim, contract, release identity, or evidence closure. The tagged manuscript,
paper-owned manifest, and receipts remain authoritative.

## Paper XVI v1.0: shortest audit path

From a current checkout with release tags available, run:

```text
python tools/release/audit_paper16_v1_materialization.py
```

The expected status is:

```text
status: HISTORICAL_MATERIALIZATION_EXPLAINED
ordered_closure_entries: 56
materialization_exceptions: 21
all_exception_json_semantics_equal: true
```

Paper XVI v1.0 was frozen with 21 JSON digests taken from historical Windows
CRLF or mixed-EOL materializations. Git stores and checks out those paths as
LF. Consequently, the original closure validator returns `FAIL` in a clean
checkout of `paper16-v1.0`. The audit above is locked to the published tag,
release commit, manifest blob, and exact affected paths. It verifies that the
registered bytes are deterministic historical materializations of the same
JSON objects. It does not rewrite the tag, repair the receipt, or turn the
original clean-checkout result into `PASS`.

## What to open

| Question | Start here |
|---|---|
| What does the paper claim? | `papers/paper16/Paper XVI.md` |
| What was uploaded for readers? | `papers/paper16/paper16_arxiv.pdf` |
| What is in the machine closure? | `experiments/paper16/release-manifest.v1.json` |
| What did the original local validator record? | `experiments/paper16/results/release-closure.v1.validation-receipt.json` |
| Why does a clean tag checkout now fail? | `tools/release/audit_paper16_v1_materialization.py` |
| Which external MaleCNS bytes are required? | `experiments/paper16/upstream-provenance.v1.json` |
| Which command owns each replay? | `experiments/paper16/README.md` |

The public result line is:

```text
three exact upstream tables
  -> paper-owned producers
  -> static and dynamic artifacts
  -> replay receipts
  -> release manifest
  -> paper16-v1.0 and Zenodo DOI 10.5281/zenodo.22931881
```

## Fresh producer replay

Use this path only when the existing closure check is insufficient and fresh
recomputation is required.

### 1. Obtain the three inputs

Download the exact files listed in
`experiments/paper16/upstream-provenance.v1.json` into one directory. Preserve
their filenames and exact bytes. The largest table is approximately 1 GB.

### 2. Create the locked environments

Carrier, static, and dynamic replay require Python 3.12 and the exact packages
in:

```text
experiments/paper16/source/requirements/static.txt
```

The A1/A2 exact follow-ups require Python 3.13 and:

```text
experiments/paper16/source/requirements/followups.txt
```

Do not bypass a Python or package-version mismatch. It is a replay failure,
not a warning.

### 3. Reconstruct the ignored carrier files

Run under the locked Python 3.12 environment:

```text
python experiments/paper16/source/replay/replay_large_artifacts.py --replay \
  --external-input-root <inputs> \
  --scratch-root <scratch>/carrier \
  --materialize-output-root experiments/paper16/source \
  --receipt <scratch>/carrier-replay.json
```

The materialized NPZ and Parquet files are ignored generated inputs. They are
copied into place only after their sizes and SHA-256 digests match.

### 4. Replay the static and dynamic records

Still under Python 3.12:

```text
python experiments/paper16/validation/replay_static_audits.py \
  --external-input-root <inputs> \
  --scratch-root <scratch>/static \
  --receipt <scratch>/static-replay.json

python experiments/paper16/validation/replay_dynamic_descent.py \
  --scratch-root <scratch>/dynamic \
  --receipt <scratch>/dynamic-replay.json
```

Both commands regenerate into scratch and compare exact bytes with the
committed artifacts. Success requires `status: PASS` and
`all_replayed_bytes_equal: true`.

### 5. Replay the two exact follow-ups

Switch to the locked Python 3.13 environment:

```text
python experiments/paper16/validation/replay_exact_followups.py \
  > <scratch>/a1-a2-replay.json
```

Success requires `status: PASS`, two replay records, and
`all_replayed_bytes_equal: true`.

Finally rerun the historical materialization audit from the shortest path.
Fresh replay results remain separate from the frozen v1.0 closure result.

## Common failures

| Failure | Meaning |
|---|---|
| missing upstream file | The three official MaleCNS tables are not all present under `<inputs>`. |
| upstream digest mismatch | The downloaded release or file bytes differ from the registered inputs. |
| Python/package mismatch | The wrong replay environment is active. |
| missing carrier NPZ/Parquet | Step 3 has not completed successfully. |
| replay bytes differ | A producer, dependency, input, or serialization result has drifted. |
| v1.0 direct validator reports JSON byte mismatches | The frozen manifest records historical Windows text materializations while Git materializes LF; use the release-specific audit above. |
| materialization audit is `UNRESOLVED` | The tag, manifest, exception set, or an affected JSON object differs from the frozen v1.0 profile. |

On a historical tag, do not use `--refresh`, `--write-receipt`, or a default
receipt output path. Those are maintainer operations that can rewrite
candidate metadata. Reproduction should write only to `<scratch>` and ignored
generated carrier paths.

## Boundary

The Paper XVI v1.0 audit explains a historical byte-materialization mismatch;
it is not local closure verification and does not establish a clean-checkout
closure `PASS`. A successful producer replay separately establishes the
properties declared by that replay receipt. Neither result is independent
scientific validation, physiological validation, or a causal claim.
