# Paper XIII Experiments

Paper XIII owns pairwise alignment and capability-aware comparison. The
single-system report protocol belongs to Paper XII, and interpretation or
policy-relative disposition belongs to Paper XIV.

```text
paper13/
|-- *_sof.py / before_after_alignment.py  frozen domain-control producers
|-- validation/                           migrations and current validators
|-- results/                              current migrated and native-v2 artifacts
|-- archive/                              v1 table check and frozen v1 corpus
`-- (renderer)                            figures/paper13/render.py
```

## Current Contract

The published SOFAUDIT v2.0 corpus remains the immutable migration source.
The published v2.1 release uses:

```text
two SOFRS v2 alignment-ready reports
  -> validated source-report receipts
  -> inherited Paper X guard checks
  -> typed sector and observable alignment Phi
  -> controlled comparison specification Theta
  -> comparison-role and external comparison basis
  -> regime-bound Audit Profile
  -> sparse typed coordinates
```

No factual Audit Signature exists for a bare report pair. The alignment
evidence and comparison specification define the typed comparison domain;
equal field names alone do not establish shared semantics.

The versioned Standard Regime-A profile requests:

```text
support, word_bridge, lie_bridge, depth,
frozen_summary, constraint, response, wall_record
```

These are profile coordinates, not universal requirements. Missing or
incompatible fields use `NOT_DECLARED`, `NOT_APPLICABLE`, `INCOMPARABLE`, or
`UNRESOLVED`; they are never filled with zero.

The profile is the source of truth at
`schemas/sofaudit/paper13-standard-regime-a-profile-v2.0.json`; coordinate
family/value semantics are sourced from
`schemas/sofaudit/coordinate-semantics-registry-v1.0.json`. Producers and the
semantic validator load those inputs rather than maintaining a private channel
list. Every current audit also carries both files as digest-checked
`audit-profile` and `coordinate-semantics-registry` source artifacts; the
embedded profile must equal its bound source profile. Every admitted Audit
Profile must list both roles in `required_evidence_roles`; omitting either
normative input is a validation error.

The `wall_record` coordinate has an additional ownership gate. Both sides must
bind source-addressed Paper XI wall records and signatures, and the comparison
must declare compatible trajectory/domain context, synchronization or stratum
alignment, orientation, and field-alignment semantics before `ALIGNED` or
`MISMATCH` is legal. The five
frozen v1 F5 path payloads lack those bindings. V2 retains them as hashed
compatibility observations with `UNRESOLVED` wall coordinates; it does not
infer Paper IX admission or Paper XI morphology from a path difference.

## Versioned Artifacts

- `archive/results/` and `schemas/sofaudit/v1.0.schema.json` are frozen
  provenance and migration inputs, not the default result surface.
- `validation/migrate_sofrs_v1_to_v2.py` first converts the 36 retained Paper XIII source
  reports into CompilerOutput-bound SOFRS v2 reports and v2 validation receipts.
- `validation/migrate_sofaudit_v1_to_v2.py` emits 28 source-addressed records
  under `results/audits/` and writes `results/migration-index.json`.
- `validation/emit_migration_audit_receipts.py` validates those 28 current
  migrated records and emits their SOFAUDIT v2 validation receipts under
  `results/receipts/`. Paper XIV consumes the audit and receipt together.
- The 28 records consume 36 deduplicated SOFRS v2 report-validation receipts;
  a source report digest without a matching `PASS` receipt is insufficient.
- `validation/validate_sofaudit_v2.py` performs semantic validation after schema
  validation. It recomputes source roles and regime, profile-coordinate closure,
  alignment coverage and map properties, inherited guard state, comparison-basis
  completeness, claim/certificate compatibility, and artifact identity/digest
  closure. An external-object claim additionally requires a digest-bound
  independent oracle that did not reuse producer cache.
- `validation/contextual_descent_control.py --write` emits the one promoted
  finite AB/BC/AC control under `results/controls/`; its independent validator
  is `validation/validate_contextual_descent_control.py`. This is the only
  Paper XIII promotion from `experiments/exploratory/comparison_geometry/`.
- `release-snapshots/rime-lite-v2.0/` preserves the exact historical bytes
  required by the published v2.0 closure when a checkout normalizes text
  files. It is an explicit historical input, not a regenerated result or a
  fallback that permits report/input digest drift.
- The census is 20 F1-F4 source payloads + 5 F5 compatibility payloads + 3
  transformation controls = 28 legacy/control cases, plus one separate native
  GridWorld F4 factual audit, giving 29 current SOFAUDIT v2 artifacts.
- The 28 migrated records are Migration/Assembly Certificates. They establish
  preservation under the declared v1-to-v2 mapping, not facts about the source
  mathematical objects.
- The 201 coordinates with legacy v1 payloads migrate to `UNRESOLVED`, while 23
  absent coordinates remain `NOT_DECLARED`. The source payloads remain frozen
  and digest-addressed; migration does not invent the report-level alignment and
  item bindings needed for factual v2 `ALIGNED` or `MISMATCH` states.
- `validation/gridworld_f4_native_v2.py` builds a separate native factual chain
  under `results/native/gridworld-f4/`: two sparse source snapshots, two strict
  SOFRS v2 source-report stacks and receipts, explicit sector/observable
  alignment, complete comparison semantics, item bindings, one factual native
  `.sofaudit`, and a SOFAUDIT validation receipt. This artifact is not a
  twenty-ninth migration record.
- `validation/gridworld_f4_object_certificate.py` independently reconstructs
  the finite GridWorld F4 matrices from the frozen sparse sources, recomputes
  the support coordinates, checks direct support against a graph-incidence
  baseline, and compares its result with the native producer output.
  Its certified mismatch counts are direct support `0`, ordered length-two
  word support `0`, and simple-commutator support `8`. The native audit binds
  this oracle and emits factual `ALIGNED`, `ALIGNED`, and `MISMATCH` states. The
  validator also confirms that the migrated v2 coordinates remain unresolved;
  it does not upgrade the migration artifact.
- `schemas/sofaudit/validation-receipt-v2.0.schema.json` defines the current
  audit receipt for native and migrated v2 artifacts. The receipt proves
  protocol conformance and digest closure,
  not object truth; the independent recomputation carries the Object
  Certificate.
- Legacy `999` policy sentinels migrate to `UNREACHED_AT_CUTOFF` with an
  explicit cutoff.
- Legacy F5 path payloads remain source-addressed but are not promoted to wall
  comparisons without retained Paper XI inputs.
- `validation/migrate_sofaudit_v2_to_v2_1.py` migrates all 29 v2.0 audits and
  their 38 deduplicated source-report stacks into the v2.1 boundary contract.
- `validation/validate_sofaudit_v2_1.py` checks the exact v2.0 projection,
  report and audit receipt closure, and the required no-attribution boundary.
- `results/v2.1/` contains 29 SOFAUDIT v2.1 artifacts, 29 comparison-only
  validation receipts, and the bound SOFRS v2.1 source-report closures.

SOFAUDIT v2.1 may localize differences only in aligned report coordinates.
Its fixed `attribution_boundary` keeps diagnostic interpretation downstream,
places defect and causal attribution out of scope, and keeps the reference as
a comparison role rather than ground truth, a control group, or a causal
baseline. A future causal artifact must consume a separate model and evidence;
it cannot promote `SOFAUDIT.causal_status` in place.

The v2.1 schema and validator also admit native audits with a bound generation
implementation and nonempty input closure. The current 29-artifact candidate
corpus uses the explicit migration branch; native generation receives a
different receipt provenance and exact check set.

Run:

```bash
python tools/validate_release_snapshot.py release-snapshots/rime-lite-v2.0/manifest.json
python experiments/paper13/validation/validate_sofaudit_v2.py
python experiments/paper13/validation/migrate_sofaudit_v2_to_v2_1.py
python experiments/paper13/validation/validate_sofaudit_v2_1.py --write-receipts
python tests/test_sofaudit_v2.py
```

The omitted v1-to-v2 migrators, receipt emitter, and native GridWorld `--write`
commands are historical v2.0 producers. They are not routine validation
commands and must not be used to refresh the immutable published corpus in the
current worktree. The v2.1 producer and receipt writer use `results/v2.1/`.

JSON Schema establishes shape only. The semantic validator executes the
cross-field invariants above and the hostile fixtures mutate each boundary to
confirm rejection. Even that validation issues only protocol-conformance or
comparison-audit evidence. A schema-valid alignment cannot receive an Object
Certificate unless a declared domain baseline or first-principles independent
recomputation tests its object-level content.

The domain scripts and `validation/validate_sofaudit_v1.py` remain historical
reproducibility inputs for the controlled GridWorld, SIR, Traffic, Compiler IR,
Network Routing, and before/after comparisons. Rerunning those producers writes
only to `archive/results/`; active migration and validation write to `results/`.
`archive/regenerate_tables_v1.py` checks the frozen signature table only against
the retained v1 manuscript and does not constrain the active Paper XIII text.

The presentation-only renderer follows the repository figure contract:

```bash
python figures/paper13/render.py
```

It reads no scientific result as a certificate and writes only the retained
PNG/PDF assets under `figures/paper13/`.
