# SOF Compiler Contracts

This directory contains the first three input contracts and the v1.0 emission
algorithm for a capability-aware SOF compiler. They define a thin interface
between domain adapters and the versioned reporting protocol; they do not
require every realization to implement every SOF enrichment.

## Contract Stack

```text
domain model
  -> Capability Manifest
  -> Typed SOF IR
  -> Report Profile
  -> Compiler Output v1.0
  -> downstream report protocol and serializers
```

The stack enforces a one-way discipline:

```text
The Manifest does not contain results.
The IR does not choose presentation.
The Profile does not create evidence.
Compiler Output is not itself a SOFRS report.
```

The output item type is the disjoint union

```text
CompilerItem_v1 = ClaimItem_v1 | DegradationItem_v1.
```

`compile_v1` returns an ordered collection of these items. A claim item carries
the emitting module, source IR claim, carrier references, claim status, result
state, and derivation references. A degradation item records an omitted module
or claim and the failed gate. Serialization, presentation, and report-level
epistemic metadata belong to the Paper XII reporting protocol.

`compiler-output-v1.0.schema.json` is the canonical machine-readable output
contract. `compile_output_v1` returns its complete envelope, while the legacy
`compile_v1` helper continues to return only the ordered item collection.
Downstream serializers must consume this compiler result rather than
reimplementing admission, evidence, derivation, or promotion checks.
Python consumers import these functions from `schemas.sofcompiler.api`; the
`validate_examples.py` module remains the CLI and regression implementation,
not the downstream import path.

### Capability Manifest v1.0

`capability-manifest-v1.0.schema.json` records:

- whether the record is a `strict_sof` or `diagnostic_analogue`;
- the source adapter and finite-space declaration;
- which typed carriers and closures are declared, not declared, or not
  applicable;
- which semantic conventions must be supplied by the IR;
- which run policies must be supplied by an audit.

It does not contain numerical results, certificates, or claim evidence.
Object-identity conventions and run-specific cutoff, threshold, norm, and
saturation values belong in separate IR collections.

For `strict_sof`, v2.0 requires a finite-dimensional complex space and forbids
declaring the whole record as a diagnostic analogue. A diagnostic sidecar may
still be registered through `proxy_diagnostic`.

Every capability is explicit. A missing Lie/Hall carrier is serialized as
`NOT_DECLARED`, not as a zero Lie channel. A static realization may mark a
deformation chart `NOT_APPLICABLE`.

### Typed SOF IR v1.0

`typed-sof-ir-v1.0.schema.json` is the normalized intermediate
representation. It records:

- typed objects and carriers;
- semantic conventions and run policies as separate collections;
- a top-level artifact registry with explicit digest algorithms;
- validator certificates that reference shared artifacts;
- structured findings for dimensions, ranks, depths, norms, residuals, walls,
  and response times;
- typed claims with hypotheses, scope, and negative boundaries;
- explicit derivation edges, versioned rule IDs, condition checks, and
  derivation state.

The two status axes remain separate:

| Axis | Values |
|------|--------|
| Result state | `DECLARED`, `ESTABLISHED`, `CERTIFIED`, `OBSERVED`, `UNREACHED_AT_CUTOFF`, `NOT_APPLICABLE`, `NOT_DECLARED` |
| Claim status | `Theorem`, `Computational Certificate`, `Computational Observation`, `Research Program`, or `null` where no claim is asserted |

The legal pairing is fixed: `ESTABLISHED` with `Theorem`, `CERTIFIED` with
`Computational Certificate`, `OBSERVED` with `Computational Observation`, and
`DECLARED` with `Research Program` or `null`. Unavailable states carry `null`.
`UNREACHED_AT_CUTOFF` requires a cutoff policy and never denotes exact
infinity. `NOT_DECLARED` and `NOT_APPLICABLE` carry no theorem or computational
claim status.

An exact finite first-hit depth requires a certificate containing both a
level-$d$ witness and verified non-hits at every lower level. A witness at
level $d$ alone supports only an upper bound. The v1.0 result-state vocabulary
does not use `UNREACHED_ON_DECLARED_INTERVAL`: bounded non-crossing for a
`response_time` finding is encoded with `result_state=OBSERVED`, `value=null`,
and right-censoring details in its referenced `sampling_grid` or
`trajectory_parameterization` policy. Dedicated censoring result states would
require a future major contract version.

### Report Profile v1.0

`report-profile-v1.0.schema.json` records composable report modules. Each
module declares:

- Boolean `all_of`, `any_of`, and `none_of` requirements for capabilities,
  object kinds, semantic conventions, and run policies;
- accepted result and claim statuses;
- accepted carrier kinds;
- evidence requirements for each claim status;
- machine-readable forbidden promotion IDs, with human-readable notes;
- output sections.

The profile also declares graceful-degradation behavior. A missing capability
may omit a module or emit an unavailable statement, but it cannot be replaced
by a nearby carrier. `any_of` expresses cases such as route **or** word
support, or any one of the three closure types.

The `outputs` array declares requested downstream serialization targets. It
does not change the `Compile_v1` return type and does not authorize Paper X to
construct a SOFRS report, PDF, Registry snapshot, or API response directly.

The initial module vocabulary is:

| Module | Minimum capability |
|--------|--------------------|
| SOF Basic | marked sectorization and labelled operator carrier |
| Associative | route and/or word carrier with declared finite-audit policy |
| Closure | one explicitly typed positive, observable-star, or sector-enriched closure |
| Lie/Hall | independently declared Lie family and Hall convention |
| Dynamic | typed deformation chart, comparison map, trajectory, selected trajectory observable, and parameterization policy |

These names are reusable profile components, not mandatory sections. A profile
may select any compatible subset.

For example, a response-time Dynamic module can require
`deformation_chart` at the capability level; `deformation_chart`,
`comparison_map`, `trajectory`, and `trajectory_observable` at the object
level; and `trajectory_parameterization`, `threshold`, and `norm` at the run
policy level. A chart alone is therefore insufficient to enable that module.

## Layered Validation

JSON Schema checks envelope shape and controlled vocabularies. The companion
validator adds semantic and cross-contract checks:

```bash
python schemas/sofcompiler/validate_examples.py
```

It verifies:

- required configuration for every declared capability;
- manifest/adapter/record-kind alignment;
- object, carrier, convention, policy, artifact, certificate, finding, claim,
  and derivation references;
- artifact digest and manifest identity consistency;
- the result-state/claim-status legality matrix;
- cutoff policy for `UNREACHED_AT_CUTOFF`;
- evidence policy for theorem, certificate, observation, and no-claim states;
- versioned derivation rule IDs and condition checks;
- Boolean profile admission and forbidden-promotion checks.

The same executable contains `compile_v1`, which applies the checked module
emission rules and produces typed claim/degradation items. The committed
`examples/strict-associative-compiler-output-v1.0.json` fixture is a regression
record for that algorithm. It is output evidence, not a fourth input contract.

The examples intentionally describe a strict static realization with operator,
route, word, and three closure carriers, but no Lie/Hall or deformation
carrier. The selected report profile therefore assembles only Basic,
Associative, and Closure modules. The closure module is admitted by its
`any_of` expression even though a future realization could provide only one
closure.

Module admission and claim emission are separate gates. After a module passes
its global Boolean requirements, each candidate claim is checked again using
only its own capability, object, semantic-convention, and run-policy
references. A claim also inherits every typed dependency of each finding it
cites. An unresolved derivation, globally available threshold, or unrelated
certificate cannot make that claim eligible.

The companion `rule-registry-v1.0.json` is a controlled vocabulary for
derivation rules. It is not a fourth report contract; it is versioned support
data consumed by the IR validator.

## Version Boundary

These v1.0 contracts are a new working compiler interface. They do not modify or
replace:

- frozen SOFRS v1.0 artifacts;
- the Paper XII protocol-admission profile;
- Registry v1 or Registry v2 snapshots.

Future adapters may translate those formats into this IR only through an
explicit, versioned mapping. Once these contracts are released, their
published versions are immutable.
