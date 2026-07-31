# SOF Registry Snapshots

This directory stores frozen, versioned **Paper X SOF Registry snapshots**. It
is a first-class public data artifact, not an experiment directory, not the
Paper XII SOF Report collection, and not the future `sof-toolkit`
implementation.

## Current Snapshot

`paper10-release-v1.0.registry.json` freezes the 16-entry SOF Registry boundary
published with Paper X on 2026-07-10 (DOI `10.5281/zenodo.21288036`). It does
not include species introduced later by Papers XI--XII, including Qwen, MoE,
diffusion, dynamic maze, API-only LLM, and recommender reports.

`paper10-typed-v2.0.registry.json` is the frozen capability-aware v2.0
repository snapshot. It has 19 entries: 15 strict SOF realizations and 4
diagnostic analogues. Each row declares admission kind, source-map and evidence
role, capabilities, typed objects and carriers, semantic conventions, run
policies, channels, structured findings and claims, artifacts, certificates,
and audited derivations. The v1 snapshot remains immutable.

The typed snapshot includes strict static Markov and path-graph registrations
with native transition/adjacency alphabets, positive-word carriers, and exact
finite depth certificates. Neither row acquires a Lie/Hall carrier. The graph
row's edge-rewiring proxy remains a separate finding.

The snapshot also carries a Registry Census Certificate. It binds the row,
admission, capability, and finding counts to a canonical content digest, the
v2.0 schema artifact, the validator version, and a recomputable query version.
The validator rejects stale content digests or count mismatches.

Registry v2.0 follows a compiler-style interface:

```text
source
  -> strict-SOF or diagnostic-analogue admission
  -> capability declaration
  -> typed objects, carriers, conventions, and policies
  -> findings, claims, and source-addressed evidence
```

The Registry and Compiler v1.0 contracts are parallel, semantically compatible
interfaces in this release. Registry rows do not yet carry a versioned
Registry-to-IR adapter; their `capability_manifest` and `typed_sof_ir`
references remain null. A row therefore does not automatically instantiate a
compiler fixture or Report Profile run.

Capabilities are sparse. A row does not acquire route, word, closure,
Lie/Hall, deformation, proxy, or wall semantics from a nearby carrier. Missing
capability, zero, cutoff-unreached, failed validation, and nonexistence remain
distinct. Raw diagonal saturated Boolean support is excluded because unital
closures always contain `Q_i` in the `i,i` corner; a nontrivial diagonal
channel must declare a scalar-reduced convention. A finite cutoff records a
truncated depth field, and `unreached` never means exact infinity.

Repair is not one generic field. A finding must identify
`static_filtration_repair`, `dynamic_shadow_repair`, or
`diagnostic_analogue_repair` and record its source and target layers, temporal
scope, predicate, cutoff, pair scope, count denominator, and saturation status.
External numerical conversions also record whether they are source-reported or
locally derived, together with their formula, parameters, and response
convention.

Generated experiment evidence uses a two-step provenance chain. The producer
script is registered with role `script`; its versioned JSON output is
registered with role `source-data` and names the producer through
`generated_by_artifact_ids`. Findings and computational certificates cite the
result artifact, not merely the executable script. For result records that
declare `schema` and `runtime.script_sha256`, the validator checks both values
against the artifact registration and producer digest. Files under `archive/`
remain eligible only as historical provenance.

Two legacy certificates without standalone historical result files use
`experiments/paper10/results/legacy_certificate_imports_v2.json`. That record
is explicitly a source-addressed migration from immutable Registry v1.0, not a
fresh scientific recomputation. Its source snapshot and script digests are
validated.

## Validation

From the repository root:

```bash
python registry/validate_snapshot.py
```

The default command validates both the immutable published v1 snapshot and the
frozen repository v2.0 snapshot.

The validator checks schema, admission and capability consistency, references,
depth and response policies, evidence status, promotion conditions, artifact
digests, archive boundaries, and the Paper X release boundary.

To regenerate the typed v2.0 snapshot from the immutable v1 input:

```bash
python registry/migrate_v1_to_v2.py
```
