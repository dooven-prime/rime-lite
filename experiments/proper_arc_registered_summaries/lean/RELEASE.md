# Source Release Handoff

Prepared version: **1.0**. Proposed tag:
`proper-arc-lean-companion-v1.0`. Source-commit, tag, push and Zenodo
publication are separate actions and have not been performed by preparation.

The release branch starts at verified `origin/master` commit
`b2c64443b61ef63879704308b5062ab7df6066c3`. Its only selected content is this
Lean companion. The published proper-arc paper and its bounded controls are
not revised.

## Final Acceptance

`source-manifest.v1.json` binds
`cold_replay/results/isolated-windows-v1/cold-replay.v1.json` and
`evidence-manifest.v1.json` by SHA-256 as **final acceptance evidence**.
The receipt certifies the completed same-host isolated replay: all nine
owners and 94 tests passed. Its 99 frozen inputs, target signatures, axiom
sets and graph digest match this package. Packaging adds documentation and
byte inventories; it adds no theorem or theorem-audit layer.

The nine original freeze manifests/reports, source snapshots and cold logs
must not be rebound to later bytes. Keep the candidate source manifest
unchanged after its content commit; record publication facts downstream.

## Build the Narrow Archive

From the Lean directory:

```powershell
python -B package_source.py --output-dir <outside-source-directory> --write-manifest
```

The utility uses the existing theorem-map and evidence checks, writes the
file inventory and makes a deterministic ZIP. The inventory excludes itself
to avoid a self-hash; `SHA256SUMS.txt` binds both the ZIP and manifest.
`.gitattributes` preserves every frozen byte, including historical log line
endings. No `.lake/`, private config, toolchain ZIP or dependency build is
included. A subsequent run without `--write-manifest` requires the same
inventory and does not overwrite existing output files.

## Source Commit and Tag

After approval, select only this directory from the clean release worktree.
Check that Git's staged blobs preserve the manifest bytes, then create the
independent content commit. Create the proposed tag at that exact commit
and push the branch and tag. Do not use a branch name as the immutable source
identity. No change to the 99 proof inputs is needed.

## Zenodo

Prepare a separate **software** record using `.zenodo.json`. Upload the
narrow source ZIP, its `source-manifest.v1.json`, and `SHA256SUMS.txt`, rather
than treating a whole-repository GitHub archive as this closure. The HAL
paper is related by `isSupplementTo`; the companion has its own version and
eventual DOI. `.zenodo.json` omits a publication date and DOI until those
facts exist. It follows the [Zenodo deposit metadata documentation](https://developers.zenodo.org/#deposit-metadata).

Before publishing, record the resolved source tag and content commit in the
deposit description. After publication, download the deposited files and
compare exact size and SHA-256 with the prepared outputs. Record the actual
tag/commit/DOI/file binding in a downstream metadata anchor. Neither the
candidate manifest nor the accepted cold record is rewritten to appear
already published.
