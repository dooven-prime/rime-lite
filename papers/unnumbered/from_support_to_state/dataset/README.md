# Published predictive-profile Dataset

The authoritative Dataset v1.0 is at
[Zenodo DOI 10.5281/zenodo.23555888](https://doi.org/10.5281/zenodo.23555888).
Its deposited `malecns_predictive_refinement_v1.0.zip` has SHA-256
`6bf11532ed405ab5bc0a74b78ed1360931454124da954c35e74cc72c8e016f3d`
and contains the derived carrier, exact result, source, figures, manifest,
and verifier. [SHA256SUMS.txt](SHA256SUMS.txt) identifies the four deposited
files. [ATTRIBUTION.md](ATTRIBUTION.md) records the upstream data and license.

This repository mirrors the archive's small [manifest](manifest.json),
[verifier source](verify_dataset.py),
[result JSON](../evidence/profile_heterogeneity_census.v1.json),
[producer and focused test](../evidence/), and [figures](../figures/).
It intentionally omits the two large carrier files. The manifest describes
the **extracted Zenodo archive**, not this partial Git checkout; running the
verifier in this directory must not be reported as a full-package check.

For verification, download and extract the ZIP, enter its single top-level
directory, then run:

```text
python -B verify_dataset.py
python -m pip install -r requirements.txt
python -B verify_dataset.py --replay
```

The first command verifies the complete file inventory and byte digests;
expected status is `LOCAL_BYTE_CLOSURE_PASS`. The second verification
recomputes the declared census from the included derived carrier and runs
the focused controls; expected status is `SOURCE_REPLAY_PASS`. It does not
regenerate that carrier from the original upstream connectome tables or
constitute independent replication.
