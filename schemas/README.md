# Versioned SOF Data Contracts

This directory is the canonical source for machine-readable SOF contracts in
`rime-lite`.

```text
schemas/
  common/digest-v1.schema.json
                              canonical lowercase SHA-256 digest
  common/artifact-reference-v1.schema.json
                              source-addressed artifact reference
  common/validation-receipt-reference-v1.schema.json
                              source-addressed validation receipt reference
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
  sofrs/v2.1.schema.json      report non-intervention semantic revision
  sofrs/report-validation-receipt-v1.0.schema.json
                              receipt for one frozen strict SOFRS v1 artifact
  sofrs/report-validation-receipt-v2.0.schema.json
                              receipt for one SOFRS v2 report closure
  sofrs/report-validation-receipt-v2.1.schema.json
                              conformance-only receipt for SOFRS v2.1
  sofrs/paper12-strict-compiler-profile-v1.0.json
                               Paper X compiler-profile instance for strict SOF
  sofrs/paper12-analogue-compiler-profile-v1.0.json
                               Paper X compiler-profile instance for analogues
  sofrs/assembly-profile-v2.0.schema.json
                               Paper XII faithful-assembly profile contract
  sofrs/paper12-strict-assembly-profile-v2.0.json
                               strict SOFRS assembly instance
  sofrs/paper12-analogue-assembly-profile-v2.0.json
                               analogue SOFRS assembly instance
  sofaudit/v1.0.schema.json   one aligned reference/target SOF comparison
  sofaudit/v2.0.schema.json   capability-aligned profile-selected comparison
  sofaudit/validation-receipt-v2.0.schema.json
                               digest-bound SOFAUDIT protocol receipt
  sofaudit/v2.1.schema.json   non-intervention and attribution-boundary revision
  sofaudit/validation-receipt-v2.1.schema.json
                               conformance-only SOFAUDIT v2.1 receipt
  sofaudit/*profile-v2.0.json versioned Paper XIII Audit Profile inputs
  sofaudit/coordinate-semantics-registry-v1.0.json
                               coordinate family/value semantics registry
  sofaction/v2.0.schema.json   policy-relative interpretation and bounded candidates
  sofaction/validation-receipt-v2.0.schema.json
                               digest-bound SOFAction protocol receipt
  sofaction/v2.1.schema.json   non-intervention action-semantics revision
  sofaction/validation-receipt-v2.1.schema.json
                               conformance-only SOFAction v2.1 receipt
  registry/v1.0.schema.json   one frozen five-layer Registry snapshot
  registry/v2.0.schema.json   typed Registry snapshot contract
  registry/v2.1.schema.json   separate Registry v2.1 candidate contract
```

The contracts are deliberately separate:

- **Shared digest and reference fragments** are canonicalized under
  `schemas/common/`. The v2 SOFRS, SOFAUDIT, SOFAction, and validation-receipt
  schemas contain self-contained generated copies so direct JSON Schema consumers do not need
  a filesystem reference registry. Regenerate and check them with
  `python schemas/common/generate_shared_contract_fragments.py --check`; the generator
  is the only supported update path for these repeated definitions. All three
  contracts use the same lowercase SHA-256 digest pattern and receipt-reference
  shape. SOFAction's
  role-bearing artifact reference is a typed superset whose digest component is
  generated from the same shared fragment.

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
  `python experiments/paper12/validation/validate_protocol_admission.py`. Multi-system
  validator fixtures may be envelope-valid while remaining explicitly excluded
  from protocol admission.
- **SOFRS v2.0 reporting** binds the exact Paper X Compiler Output produced
  from a Capability Manifest, Typed SOF IR, Compiler Report Profile, and rule registry.
  Paper XII then applies a separately typed Assembly Profile. The validator
  recomputes the compiler output and complete assembly, checks object equality,
  and verifies a typed identity bijection between `CompilerOutput.items` and
  report claim/degradation items. SOFRS
  does not
  require one universal support/bridge/repair/wall grammar. Strict reports
  require finite complex `(V,Q,Y)` data and structural admission; analogue
  reports carry descriptor provenance, an analogue mapping, and a negative SOF
  boundary and cannot instantiate SOF theorems. The reference migration
  preserves all nine archived v1 reports by digest, emits nine analogue
  reports under `experiments/paper12/results/`, records four controlled
  strict-reconstruction assessments with status `yes`, and converts legacy `999`
  values to `UNREACHED_AT_CUTOFF`. Every v2 report also carries
  alignment-ready adapter/profile, sector/observable, carrier, convention,
  policy, comparison-key, and digest metadata without constructing a pairwise
  alignment. It also carries `external_basis_registry` and claim-level basis
  references, separating source identity, object-level recomputation,
  realization/structure validation, and domain semantic adequacy. A schema-valid report may leave the latter levels
  unresolved; an Object Certificate requires a satisfied object-level basis
  with digest-checked evidence. Run
  `python experiments/paper12/validation/validate_sofrs_v2.py`.
- **SOFRS report validation receipts** bind one exact report artifact to the
  Paper XII validator and schema that checked it. The v1.0 receipt contract is
  limited to frozen strict SOFRS v1 compatibility inputs. The v2.0 receipt
  contract binds the report, Manifest, IR, Compiler Profile, CompilerOutput,
  Assembly Profile, assembly implementation, validator implementation, and
  receipt schema as one digest-checked closure.
  A receipt records validation
  evidence; it is neither a report result state nor a Paper XIII comparison
  state. Consumers must verify the receipt and its report linkage rather than
  trusting a self-declared `PASS` field.
- **SOFRS v2.1 reporting** is the published non-intervention semantic revision.
  A v2.0 report does not validate directly as v2.1. Explicit migration preserves
  its normative projection, adds the fixed `object_transition_boundary`, and
  binds the source v2.0 receipt, migration implementation, v2.1 contracts,
  validator, and boundary helper in a new conformance-only receipt. Native
  generation is a separate provenance branch requiring a digest-bound producer
  and nonempty input closure. Report and receipt conformance does not establish
  implementation purity, adapter adequacy, an object-state transition, outcome,
  or causal effect. Run
  `python experiments/paper12/validation/validate_sofrs_v2_1.py`.
- **SOFAUDIT v2.0** validates a `.sofaudit` artifact comparing two aligned
  SOFRS v2 reports with validated v2 source-report receipts. A report digest alone
  is insufficient. SOFAUDIT inherits record-kind, carrier, policy, evidence, and
  promotion guards from the Paper X compiler contracts. The fields
  `source_reports`, typed `alignment`, and controlled `comparison_specification` serialize the
  canonical comparison object
  $\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
  \Phi;\Theta)$. `comparison_basis` records reference-role authority,
  alignment evidence, policy compatibility, and any independent object oracle.
  `audit_profile` selects namespaced coordinate instances and `coordinates`
  stores typed reference/target values and relations under a controlled
  `value_schema_id`. Unavailable coordinates are
  `NOT_DECLARED`, `NOT_APPLICABLE`, `INCOMPARABLE`, or `UNRESOLVED`, never
  numerical zero. Certificate classes distinguish object recomputation,
  alignment-relative comparison audit, protocol conformance, and migration or
  assembly preservation. Native generation and v1 migration use disjoint
  provenance variants.

  JSON Schema checks shape; the Paper XIII semantic validator executes the
  cross-field contract. It recomputes reference/target roles, record-kind
  regime, profile-coordinate closure, alignment coverage and
  total/injective/surjective properties, inherited guard state, comparison-basis
  completeness, claim/result/certificate compatibility, and artifact
  identity/role/digest closure. It also requires an external-object claim to
  bind a satisfied independent oracle over raw source, independent
  recomputation, oracle result, and audit result artifacts. Hostile fixtures
  exercise each rejection boundary.

  The frozen v1 schema and 28 source records remain immutable. Their v2
  Migration/Assembly Certificates preserve source identity and normalize legacy
  `999` sentinels to `UNREACHED_AT_CUTOFF`; they do not recertify legacy
  comparisons. Because the migrated SOFRS v2 analogue reports do not provide
  the required report-level alignments and item bindings, 201 legacy-present
  coordinates are `UNRESOLVED` and 23 absent coordinates are `NOT_DECLARED`.
  Separately, the native GridWorld F4 chain binds two native SOFRS v2 reports,
  explicit alignments and comparison semantics, report-item bindings, and an
  independent object oracle. It emits factual `ALIGNED`, `ALIGNED`, and
  `MISMATCH` coordinates with mismatch counts `0`, `0`, and `8`; it is not part
  of the 28-record migration census. The SOFAUDIT validation receipt binds the
  audit, validator, source-report receipts, and referenced artifacts as a
  protocol-conformance closure. It does not replace the independent Object
  Certificate.
  Run
  `python experiments/paper13/validation/migrate_sofrs_v1_to_v2.py`,
  `python experiments/paper13/validation/migrate_sofaudit_v1_to_v2.py`, and
  `python experiments/paper13/validation/validate_sofaudit_v2.py`.
- **SOFAUDIT v2.1** adds the fixed attribution boundary and separates explicit
  v2.0 migration from native v2.1 generation. Migration preserves the
  comparison projection and binds the frozen source audit and receipt; native
  generation binds its own producer and input closure. Neither branch promotes
  an aligned difference into defect, causal attribution, or intervention.
  Run `python experiments/paper13/validation/validate_sofaudit_v2_1.py`.
- **SOFAction v2.0** validates a `.sofaction` artifact that binds an immutable
  SOFAUDIT projection and its receipt to an independently supplied
  `ActionContext` and the sole normative `PolicyProfile`. Policy Predicate
  Language v1.0 is a closed AST; its controlled uncertainty policy preserves
  unresolved and unavailable states rather than coercing them to false or
  zero. The semantic validator independently replays admission, predicate
  evaluation, rule precedence, interpretation records, disposition closure,
  and the bounded `CandidateActionSet`.

  The published workbench contains 28 migration-relative inputs and one native
  GridWorld F4 factual audit, producing 29 source-addressed SOFAction objects
  and validation receipts. The current record classes are
  `policy_conformance_certificate` and `decision_trace_certificate`. Neither
  class selects, recommends, authorizes, executes, observes, or certifies the
  effect of an action. Run `python experiments/paper14/action_workbench.py` and
  `python experiments/paper14/validate_sofaction.py`.
- **SOFAction v2.1** adds a fixed execution boundary and distinct migration and
  native-generation provenance. Its 29 validation receipts bind the active
  v2.1 closure; historical v2.0 receipts remain immutable and use their own
  version-aware validation path. Run
  `python experiments/paper14/validate_sofaction_v2_1.py`.
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
  translated into Manifest/IR records by a versioned adapter. Registry v2.1
  preserves the v2.0 object shape in a separate candidate schema and binds the
  frozen v2.0 predecessor, current evidence result, producer, migrator, and
  validator without rewriting either published predecessor.

Published schema versions are immutable. A change to required fields,
controlled vocabularies, or field meaning requires a new versioned file.
Published contracts end at SOFAction's bounded candidates. The numbered SOF
protocol line allocates no `.sofplan`, `.sofauth`, `.sofexec`, `.sofoutcome`,
or `.sofeffect` wire contract.
