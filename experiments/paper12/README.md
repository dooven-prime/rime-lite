# Paper XII Experiments

This directory contains the current SOFRS v2 migration, validation, and typed
report artifacts. Frozen SOFRS v1 results remain available under `archive/`
as source-addressed migration inputs; they are not the default result surface.

```text
paper12/
|-- *_sof.py / *_sweep.py          source experiment producers
|-- failure_cases.py               frozen boundary-fixture producer
|-- validation/                    migration and current validators
|-- results/                       current SOFRS v2 contract stack
|-- archive/results/               frozen SOFRS v1 reports and fixture
`-- (renderer)                     figures/paper12/render.py
```

Paper XII does not redefine the Paper X compiler contracts. It assembles one
SOFRS report from an exact `CompilerOutput` and preserves three boundaries:
Report Relativity, adapter adequacy, and versioned report serialization.
Every v2 report also carries an `external_basis_registry` of named basis
packages. Each claim binds its own `external_basis_refs` and
`external_constraint_ids`. The migration reports satisfy only the source-digest
package; they do not receive Object Certificates.

## Current Evidence

| Artifact | Role | Claim status |
|----------|------|--------------|
| `validation/migrate_sofrs_v1_to_v2.py` | maps nine frozen v1 envelopes into Manifest/IR/CompilerOutput/faithfully assembled SOFRS v2 stacks | migration and assembly producer |
| `validation/validate_sofrs_v2.py` | recomputes `Compile_v1` and `Assemble_v2`, checks item bijection, source mapping, cutoff provenance, admission boundaries, and artifact links | Computational Certificate validator |
| `results/migration-index.json` | source-addressed census of the nine migrations | Computational Certificate |
| `results/report-validation-receipts/paper12-v2/` | one deterministic validation receipt per v2 report plus a receipt index | validation evidence |
| `validation/validate_sofreport.py` | checks archived v1 envelopes and manuscript schema drift | historical compatibility validator |
| `validation/validate_protocol_admission.py` | applies the frozen v1 admission profile | historical compatibility validator |

The conservative migration classifies all nine reports as
`diagnostic_analogue`. Four receive `yes` under the controlled
`strict_reconstruction` assessment because their known obligations can be
enumerated, but the archived envelopes do not bind complete explicit `(V,Q,Y)`
artifacts and the assessment does not predict successful strict admission.
Each current report declares `source_mapping.status = migrated`. `heuristic`
is reserved for pre-admission adapter research and is not a valid SOFRS report
status.

Run the current pipeline from the repository root:

```bash
python experiments/paper12/validation/migrate_sofrs_v1_to_v2.py
python experiments/paper12/validation/validate_sofrs_v2.py
python tests/test_sofrs_v2.py
python figures/paper12/render.py
```

The validator emits v2 receipts only after the bound Manifest, IR, Paper X
Compiler Profile, CompilerOutput, Paper XII Assembly Profile, report assembly,
cutoff policies, and record-kind
boundary pass. A receipt certifies protocol validation of that exact artifact
closure. The external-basis statuses are checked independently; a satisfied
status must cite a digest-checked artifact. A receipt does not establish
adapter scientific adequacy, report alignment, or downstream interpretation.

The migration converts legacy integer `999` values to
`UNREACHED_AT_CUTOFF` under producer-bound maximum depths (Qwen 3,
recommender 8, transformer batch 4). General matrix commutators remain proxy
diagnostics, and changing-dimension or changing-sector aggregates remain
analogue records.

## Archive

`archive/results/` contains the nine frozen SOFRS v1 reports and the v1
boundary fixture. They are immutable migration provenance, not current report
outputs. Current commands read them explicitly and write only to `results/`.

The renderer is presentation-only: it reads current v2 report descriptors and
writes the retained Paper XII PNG/PDF assets under `figures/paper12/`.
