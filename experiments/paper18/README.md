# Paper XVIII research-report evidence index

The canonical report is [Paper XVIII](../../papers/paper18/Paper%20XVIII.md);
its [Technical Notes](../../papers/paper18/TECHNICAL_NOTES.md) retain finite
tables and replay boundaries. This directory is an evidence index, not a
new computation or a claim that the original MaleCNS producer has been
reconstructed from a clean checkout.

| Claim or input | Versioned source | Evidence level |
|---|---|---|
| Earlier structural route counts and first-reference scan | [Paper XVI v1.0](https://github.com/dooven-prime/rime-lite/tree/paper16-v1.0/experiments/paper16) | Published paper-owned finite record |
| Reached-set factorization and image escape | [Paper XVII v1.0](https://github.com/dooven-prime/rime-lite/blob/paper17-v1.0/experiments/paper17/00_START_HERE.md) | Published exact-orbit sidecar replay |
| 163,439-source profile census and coordinate counts | [Dataset v1.0](https://doi.org/10.5281/zenodo.23555888) | Exact integer census; derived-carrier source replay |
| Two-source rational inequality | [Compact witness ZIP at fixed commit](https://github.com/dooven-prime/rime-lite/blob/4d7595936e9fb2271a870ec560e77c021a64fdb9/papers/unnumbered/from_support_to_state/witness/malecns_two_source_witness_v1.0.zip) and [instructions](https://github.com/dooven-prime/rime-lite/blob/4d7595936e9fb2271a870ec560e77c021a64fdb9/papers/unnumbered/from_support_to_state/witness/README.md) | Exact arithmetic check; optional source-row extraction using the Dataset carrier |

The deposited Dataset ZIP has SHA-256
6bf11532ed405ab5bc0a74b78ed1360931454124da954c35e74cc72c8e016f3d.
The repository mirrors only its small
[result](../../papers/unnumbered/from_support_to_state/evidence/profile_heterogeneity_census.v1.json),
[producer](../../papers/unnumbered/from_support_to_state/evidence/profile_heterogeneity_census.py),
and [verification guide](../../papers/unnumbered/from_support_to_state/dataset/README.md);
the large derived carrier is in the deposited archive. The mirrored result
has SHA-256
f199ca218039cc5c49ce2e8dbea66d171f3623d84dcf2889682dfc554f7aef32.

The separate compact witness ZIP is tracked under the link above and has
SHA-256
6ff8175d62b893f2f71c357ae51419727edc58aed160365fe8fb86a52feea2c9.
Its mirrored [certificate](../../papers/unnumbered/from_support_to_state/evidence/somaside_exact_witness.v1.json)
has SHA-256
f57a4702387809899fca2e2cfc46b2fa7adb2481154b95c703aa9ce6384425e1.
The Dataset DOI does **not** identify this compact ZIP.

## Release-content check

From the repository root, run:

```text
python -B experiments/paper18/validation/validate_release.py
```

The [release manifest](release-manifest.json) binds the report,
accepted PDFs, figures, build sources, and this index. Its historical-evidence
closure checks all 33 files in the prior JCN submission against Git commit
`4d7595936e9fb2271a870ec560e77c021a64fdb9` and the current checkout's
exact bytes. The gate reruns focused finite controls and the compact witness's
default checker. The [local receipt](results/paper18_local_release.validation-receipt.json)
excludes itself from its own digest. This does not download or replay the
large deposited Dataset carrier or establish a Zenodo DOI. After the tag is
created, `python -B experiments/paper18/validation/validate_release.py --check-tag`
also checks that the exact `paper18-v1.0` annotated tag contains the bound
release content.

This [index at the release tag](https://github.com/dooven-prime/rime-lite/blob/paper18-v1.0/experiments/paper18/README.md)
is the report's public fixed-version entry point once the tag is pushed. The
witness ZIP has a separate fixed historical Git URL above.

The [JCN author-submission snapshot](../../papers/unnumbered/from_support_to_state/README.md)
is retained unchanged as a prior version. Paper XVIII re-edits its prose
and figure placement; it does not retroactively change those submitted
bytes or the independent published identities of Papers XVI and XVII.
