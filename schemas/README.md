# Versioned SOF Data Contracts

This directory is the canonical source for machine-readable SOF contracts in
`rime-lite`.

```text
schemas/
  sofcompiler/capability-manifest-v1.0.schema.json
                               application capability declaration
  sofcompiler/typed-sof-ir-v1.0.schema.json
                               typed objects, conventions, findings, and claims
  sofcompiler/report-profile-v1.0.schema.json
                               capability-gated report composition
  sofcompiler/compiler-output-v1.0.schema.json
                               typed claim/degradation compiler output
  sofcompiler/rule-registry-v1.0.json
                               versioned derivation-rule vocabulary
  sofrs/v1.0.schema.json      one concrete SOF diagnostic run
  sofrs/paper12-protocol-profile-v1.0.json Paper XII admission rules
  sofrs/v2.0.schema.json      capability-gated compiled SOF report
  sofrs/report-validation-receipt-v1.0.schema.json
                              receipt for one frozen strict SOFRS v1 artifact
  sofrs/paper12-strict-report-profile-v2.0.json
                               strict SOF report modules
  sofrs/paper12-analogue-report-profile-v2.0.json
                               diagnostic-analogue report module
  sofaudit/v1.0.schema.json   one aligned reference/target SOF comparison
  sofaudit/v2.0.schema.json   capability-aligned profile-selected comparison
  registry/v1.0.schema.json   one frozen five-layer Registry snapshot
  registry/v2.0.schema.json   typed Registry snapshot contract
```

The contracts are deliberately separate:

- **Shared contract mechanics** live in `schemas/contract_api.py`. Paper-local
  validators reuse its JSON Schema error format, digest verification,
  repository-bounded artifact resolution, and result-state/claim-status
  matrix. These mechanics do not own paper-specific admission, morphology,
  reporting, comparison, or action semantics.

- **SOF compiler contracts** define a new three-stage interface:
  Capability Manifest, Typed SOF IR, and Report Profile. The manifest declares
  available carriers and convention/run-policy requirements; the IR records
  separate conventions and run policies, artifacts, findings, certificates,
  typed claims, and audited derivation edges; the profile enables only report
  modules supported by Boolean capability/object/policy expressions. Compiler
  Output records the resulting `ClaimItem_v1 | DegradationItem_v1` collection;
  it is not a SOFRS report. Result state is distinct from the four
  reader-facing claim levels. Run
  `python schemas/sofcompiler/validate_examples.py` for schema and
  cross-contract semantic validation. The rule registry is controlled support
  data, not a fourth report contract. Claim selection is claim-local: a claim
  cannot borrow a capability, convention, run policy, or finding dependency
  merely because it exists elsewhere in the IR. These contracts do not mutate
  SOFRS or Registry snapshots.
- **SOFRS v1.0 envelope validation** checks the frozen JSON shape of a
  `.sofreport` artifact. It does not by itself establish Paper XII protocol
  admission. The envelope validator also rejects Paper XIII/XIV top-level
  fields such as `alignment`, `signature`, `action_semantics`, and `action_set`;
  a report describes one system or run rather than comparing or acting on two
  reports.
- **Paper XII protocol admission** is a separate profile layered over the
  frozen envelope. It requires named-system metadata, a failure boundary, and
  conditional evaluator provenance for Level III behavioral reports. Run
  `python experiments/paper12/validate_protocol_admission.py`. Multi-system
  validator fixtures may be envelope-valid while remaining explicitly excluded
  from protocol admission.
- **SOFRS v2.0 reporting** binds the exact Paper X Compiler Output produced
  from a Capability Manifest, Typed SOF IR, Report Profile, and rule registry.
  The validator recomputes that output before checking report modules. SOFRS
  does not
  require one universal support/bridge/repair/wall grammar. Strict reports
  require finite complex `(V,Q,Y)` data and structural admission; analogue
  reports carry descriptor provenance, an analogue mapping, and a negative SOF
  boundary and cannot instantiate SOF theorems. The reference migration
  preserves all nine v1 reports by digest, emits four strict records and five
  analogues under `experiments/paper12/results/v2/`, and converts legacy `999`
  values to `UNREACHED_AT_CUTOFF`. Every v2 report also carries
  alignment-ready adapter/profile, sector/observable, carrier, convention,
  policy, comparison-key, and digest metadata without constructing a pairwise
  alignment. Run
  `python experiments/paper12/validate_sofrs_v2.py`.
- **SOFRS report validation receipts** bind one exact report artifact to the
  Paper XII validator and schema that checked it. The v1.0 receipt contract is
  limited to frozen strict SOFRS v1 compatibility inputs; native v2 validation
  uses a future versioned receipt contract. A receipt records validation
  evidence; it is neither a report result state nor a Paper XIII comparison
  state. Consumers must verify the receipt and its report linkage rather than
  trusting a self-declared `PASS` field.
- **SOFAUDIT v2.0** validates a `.sofaudit` artifact comparing two aligned
  SOFRS reports with validated source-report receipts. A report digest alone
  is insufficient. SOFAUDIT inherits record-kind, carrier, policy, evidence, and
  promotion guards from the Paper X compiler contracts. The fields
  `source_reports`, `alignment`, and `comparison_specification` serialize the
  canonical comparison object
  $\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
  \Phi;\Theta)$. `audit_profile` selects requested coordinates and
  `coordinates` stores the sparse typed output. Unavailable coordinates are
  `NOT_DECLARED`, `NOT_APPLICABLE`, `INCOMPARABLE`, or `UNRESOLVED`, never
  numerical zero. The frozen v1 schema and 28 source records remain immutable;
  the v2 migration normalizes legacy `999` policy sentinels to
  `UNREACHED_AT_CUTOFF` with explicit cutoffs. Run
  `python experiments/paper13/migrate_sofaudit_v1_to_v2.py` and
  `python experiments/paper13/validate_sofaudit_v2.py`.
- **SOF Registry Schema** validates a versioned collection of evidence entries.
  v1 retains the frozen five-layer Paper X release shape. v2.0 instead declares
  strict-SOF or diagnostic-analogue admission, capabilities, typed objects and
  carriers, semantic conventions, run policies, structured findings and
  claims, artifacts, certificates, and checked derivations. Strict rows require
  finite complex `(V,Q,Y)` data; analogue rows cannot instantiate SOF theorems.
  A v2.0 census certificate binds its counts to a canonical Registry content
  digest, schema artifact, validator version, and query version. Repair
  findings are typed as static-filtration, dynamic-shadow, or
  diagnostic-analogue records rather than one generic repair field. Locally
  derived external ratios carry their extraction formula, source locator,
  parameters, and response convention.
  Raw diagonal saturated Boolean support is excluded because every unital
  closure contains `Q_i` in its `i,i` corner. A finite `depth_cutoff`
  denotes a truncated field with `unreached` beyond the cutoff, never exact
  infinity. Claim status remains distinct from result state. Registry v2.0 is
  semantically compatible with the compiler contracts but is not yet
  translated into Manifest/IR records by a versioned adapter.

Published schema versions are immutable. A change to required fields,
controlled vocabularies, or field meaning requires a new versioned file.
Contracts for unreleased downstream stages are intentionally excluded from this
public schema index.
