# SOF Registry Snapshots

This directory stores frozen, versioned **Paper X SOF Registry release data**.
It is a first-class public data artifact, not an experiment directory, not the
Paper XII SOF Report collection, and not the future `sof-toolkit`
implementation.

## Current Snapshot

`paper10-release-v1.0.registry.json` freezes the 16-entry SOF Registry boundary
published with Paper X on 2026-07-10 (DOI `10.5281/zenodo.21288036`). It does
not include species introduced later by Papers XI--XII, including Qwen, MoE,
diffusion, dynamic maze, API-only LLM, and recommender reports.

The snapshot follows the five-layer contract:

```text
species
  -> SOF object
  -> observable ladder
  -> dynamics
  -> diagnostics
```

`claim_status`, evidence paths, report links, and qualification notes are
metadata. Wall behavior is recorded only when a deformation geometry exists;
it is not an automatic property of every Registry entry.

## Validation

From the repository root:

```bash
python registry/validate_snapshot.py
```

The validator checks the JSON Schema, unique entry IDs, declared entry count,
source/evidence/report paths, and the Paper X release boundary. New species
must be added in a new snapshot version rather than by mutating the frozen
Paper X file.
