# Exact somaSide two-source witness v1.0

This small supporting package accompanies *A Path Is Not a State*. It checks
the exact one-step obstruction for the two previously registered L-sector
sources (body IDs 10002 and 10006). It is separate from the full-domain
predictive-profile Dataset and is not another RIME numbered release.

## First check

Extract the ZIP and enter its single top-level directory. Run:

```text
python -B verify_witness.py
```

The standard-library verifier checks the entire unpacked file inventory,
sizes, SHA-256 digests, source bindings, the saved rational arithmetic, and
six focused controls. Expected status: `COMPACT_WITNESS_PASS`. The exact
M-coordinate difference (first source minus second) is `-661/84521472`;
the cross product is `-36355`.

## Source extraction

The certificate's full source check additionally needs the **two carrier
files from the separate predictive-profile Dataset**. Unzip that Dataset,
then run from this witness package's top-level directory:

```text
python -m pip install -r requirements.txt
python -B verify_witness.py --replay --carrier-dir PATH_TO_DATASET/data/carrier
```

Use the actual extracted Dataset directory in place of `PATH_TO_DATASET`.
Expected status: `SOURCE_EXTRACTION_PASS`. The verifier checks both carrier
SHA-256 digests before invoking the original source extractor; the extractor
also checks the three included Paper XVI metadata records and reconstructs
both complete source rows. No unpublished exploratory path is required.
This step is same-implementation replay, not independent replication or a
rebuild from the original upstream Feather tables.

The package manifest excludes itself but binds every other file. Only
`__pycache__` directories containing `.pyc` files are permitted outside
that inventory. The included verifier is not an external trust anchor;
the deposited ZIP SHA-256 and repository record establish the versioned
byte identity. MaleCNS source attribution is recorded in `ATTRIBUTION.md`.
