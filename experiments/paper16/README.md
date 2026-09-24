# Paper XVI computational artifacts

This directory owns the self-contained publication closure for Paper XVI,
*From Support to State: Auditing Structural and Dynamic Descent in the Male
Drosophila CNS*. `source/` contains the exact research subset consumed by the
paper. The larger exploratory lineage is deliberately excluded and is not a
release dependency. Exact paths, byte digests, portable artifacts, and replay
receipts bind the paper to the selected source and upstream inputs.

The release closure binds:

- the static depth-two/depth-three liftability audits and sector comparison;
- clean scratch replay of all six static audit artifacts with exact-byte
  comparison against the canonical results;
- the signed operator admission, dynamics, and observation-resolution records;
- D2.1--D2.3 and their exact producers;
- the A1 same-carrier signed route audit and A2 named-sector follow-up;
- clean scratch replay of the corrected A1/A2 exact producers with exact-byte
  comparison against the canonical results;
- regenerated portable JSON artifacts whose locator fields are relative to
  the paper-owned source root;
- the exact upstream MaleCNS input URLs, byte identities, and CC-BY-4.0 source
  license;
- a paper-owned clean-clone replay closure for the three carrier outputs,
  without importing E0.3, E1, or unrelated Digital Fly sidecars.

`release-manifest.v1.json` binds the canonical Paper XVI manuscript,
paper-local bibliography, reader PDF, figure sources, and theorem-facing
computational closure. The release-content commit and external anchor remain
unset until publication. The local validation receipt is closure verification
only; it is not independent mathematical validation.

From the repository root, replay the two decisive exact producers with:

```text
python experiments/paper16/validation/replay_exact_followups.py --write-receipt
```

Replay the six static LP2/LP3 and sectorization artifacts under the locked
Python 3.12 environment without modifying the canonical result directory:

```text
python experiments/paper16/validation/replay_static_audits.py \
  --external-input-root <download-directory> \
  --scratch-root <scratch-directory>
```

After the carrier arrays have been reconstructed, replay the six v0.1-v0.2
dynamic-descent artifacts in scratch with the same locked Python 3.12
environment:

```text
python experiments/paper16/validation/replay_dynamic_descent.py \
  --scratch-root <scratch-directory>
```

This command expects the three registered carrier outputs under
`experiments/paper16/source/digital_fly_v0/results/`. After downloading the
three tables listed in `upstream-provenance.v1.json`, reconstruct and verify
them with the Python 3.12 environment locked by `source/requirements/static.txt`:

```text
python experiments/paper16/source/replay/replay_large_artifacts.py --replay \
  --external-input-root <download-directory> \
  --scratch-root <scratch-directory> \
  --materialize-output-root experiments/paper16/source \
  --receipt <carrier-replay-receipt.json>
```

Materialization occurs only after all three scratch outputs match the declared
sizes and SHA-256 digests. The generated NPZ/Parquet files and upstream data
directory are ignored by Git. Run the A1/A2 replay with the Python 3.13
environment locked by `source/requirements/followups.txt`.

Refresh the deterministic release manifest and closure receipt with:

```text
python experiments/paper16/validation/validate_release_closure.py --refresh
```

Run the same command without `--refresh` for a read-only verification.
