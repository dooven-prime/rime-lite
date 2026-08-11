# SOF Registry

**Status:** public explanatory companion to Paper X version 2.0, published as DOI
[10.5281/zenodo.21768257](https://doi.org/10.5281/zenodo.21768257). Paper X
owns capability-aware compilation theory and Registry evidence. The Registry
is evidence architecture, not the compiler theorem, a species-classification
theorem, or a replacement for the static objects of Paper VIII.

## Versioned Snapshots

The immutable version-1 snapshot, published with DOI
`10.5281/zenodo.21288036`, is:

```text
registry/paper10-release-v1.0.registry.json
schemas/registry/v1.0.schema.json
```

It contains 16 release-local rows. Its old field names and applicability labels
retain their v1 meanings.

The frozen typed v2.0 snapshot published with Paper X version 2.0 is:

```text
registry/paper10-typed-v2.0.registry.json
schemas/registry/v2.0.schema.json
```

Registry v2.0 contains 19 rows:

| Coordinate | Count |
|------------|------:|
| strict SOF realizations | 15 |
| diagnostic analogues | 4 |
| route / word / Lie--Hall carrier declarations | `1 / 4 / 5` |
| proxy diagnostics / typed deformation charts | `7 / 2` |
| declared closure capabilities | 0 |
| structured findings | 28 |

The finding census contains 1 Theorem, 13 Computational Certificates, and 14
Computational Observations. These are Registry counts, not claims that every
row implements every carrier.

The v1 snapshot remains immutable. Regeneration of v2.0 always begins from the
v1 source plus explicit migration inputs:

```bash
python registry/migrate_v1_to_v2.py
```

## Compiler Interface

Registry v2.0 follows the Paper X interface:

```text
source
  -> strict-SOF or diagnostic-analogue admission
  -> capability declaration
  -> typed objects and carriers
  -> semantic conventions and run policies
  -> findings, claims, certificates, and checked derivations
```

The compiler contracts are versioned separately:

```text
Capability Manifest
Typed SOF IR
Report Profile
derivation-rule registry
```

The Registry instantiates compatible declarations and evidence routing; it
does not redefine these contracts. Registry v2.0 and Compiler v1.0 remain
parallel interfaces in this release: no versioned Registry-to-IR adapter is
implemented, and the row-level `capability_manifest` and `typed_sof_ir`
references remain null. Registry evidence therefore does not automatically
instantiate a Report Profile compilation.

`strict_sof` requires a validated finite complex

```text
(V, {Q_i}, Y)
```

realization. `diagnostic_analogue` requires source provenance, declared
descriptors, an analogue mapping, and a negative strict boundary. An analogue
row cannot instantiate a strict-SOF theorem.

## Sparse Capability Rule

A row declares only the carriers it actually supports. Absence of a
capability is not a zero result:

```text
NOT_DECLARED
!= zero
!= UNREACHED_AT_CUTOFF
!= NOT_APPLICABLE
!= mathematical nonexistence
```

In particular:

- a graph path cannot populate a routed-product field;
- a routed product cannot populate a full-word field without cancellation
  control;
- a positive-word algebra cannot be replaced by a star-closure;
- an operator system does not silently supply a Lie/Hall family;
- a continuous proxy cannot populate a discrete support or depth field without
  a proxy-to-shadow theorem.

Depth fields must distinguish exact and truncated values. Exact
`D_kappa in N union {infinity}` requires closure or saturation certification.
A finite audit records `D_kappa^(<=d_max)` and uses
`UNREACHED_AT_CUTOFF`, never infinity.

## Closure and Diagonal Scope

Registry v2.0 distinguishes:

```text
A_Y^+       positive associative word closure
A_Y^*       observable star-closure
A_QY^*      sector-enriched star-closure
```

These closures do not retain generator labels, routes, first-hit word length,
or Lie depth. All three unital closures have nonzero diagonal corners because

```text
Q_i I Q_i = Q_i.
```

Raw diagonal saturated Boolean support is therefore not a discriminating
finding. A closure finding must use off-diagonal pairs or declare a
scalar-reduced diagonal convention.

## Current Evidence Groups

The 19-row snapshot contains sparse evidence groups rather than one universal
result table:

- Rubik spectral, direct-support, cancellation, and incidence records retained
  at their owning papers' evidence levels;
- Paper IX-owned exact and calibrated response findings imported without
  re-owning their theorem or certificate status;
- strict Markov and path-graph positive-word registrations with exact finite
  word-depth certificates and no Lie/Hall carrier;
- finite spectral-triple, control, PDE, combinatorial, barrier-option, and
  quantum portability probes with carrier-specific boundaries;
- neural, graph-rewiring, and Yang-like continuous proxy observations that do
  not promote to discrete depth;
- diagnostic analogues for sources that do not supply a strict finite
  projector-and-alphabet realization.

The machine-readable snapshot is the authority for row membership, carrier
counts, finding values, and evidence references. Public companion prose should
not duplicate the full catalogue.

Historical Type III/IV language is not active Registry v2 vocabulary.
The historical filename
`experiments/paper10/rubik_wild_type34_audit.py` is retained for path
compatibility, while its current outputs are typed as commutator cancellation
and routed image--kernel incidence.

## Source-Addressed Evidence

Computational evidence uses:

```text
producer script
  -> versioned result artifact
  -> certificate or observation
  -> Registry finding
```

Artifacts carry identifiers, roles, digests, and producer links. Findings cite
the generated result artifact rather than relying only on a script path.
Archive files may support provenance but cannot support an active typed
finding.

Paper X evidence is built through:

```text
experiments/paper10/validation/build_results.py
  -> experiments/paper10/results/registry_evidence_v2.json
experiments/paper10/validation/build_legacy_certificate_imports.py
  -> experiments/paper10/results/legacy_certificate_imports_v2.json
  -> registry/migrate_v1_to_v2.py
  -> registry/paper10-typed-v2.0.registry.json
```

The legacy-import record is explicitly a migration certificate from the
immutable v1 snapshot, not a fresh scientific recomputation. Rubik joint
spectrum and direct-support certificates cite their existing Paper IV and
Paper II result JSON directly.

The detailed fixture and claim map is maintained in
[experiments/paper10/README.md](../experiments/paper10/README.md), not repeated
here.

## Repair and External Ratios

Repair is not one generic field. A finding must identify one of:

```text
static_filtration_repair
dynamic_shadow_repair
diagnostic_analogue_repair
```

and record its carrier, source and target layers, predicate, pair scope,
cutoff, denominator, temporal scope, and saturation status.

An externally sourced numerical ratio must state whether it is source-reported
or locally derived. Locally derived values record the source locator,
extraction formula, parameters, normalization, and response convention.

## Ownership and Artifact Chain

```text
Paper VIII  static typed SOF objects
Paper IX    typed dynamics and wall pullbacks
Paper X     compiler theory and Registry evidence
Paper XI    typed wall morphology, coordinate profiles, and taxonomy
Paper XII   .sofreport single-system protocol
Paper XIII  .sofaudit aligned comparison
Paper XIV   .sofaction context/policy interpretation and bounded candidates
```

After an explicit versioned Registry-to-IR adapter is supplied, the Registry
may supply typed findings to a report compiler. It does not perform report
alignment or choose an action. The artifact chain remains:

```text
typed objects and findings
  -> .sofreport
  -> .sofaudit
  -> .sofaction
```

Each downstream stage adds a new contract and cannot silently revise upstream
carrier semantics. `.sofaction` does not contain a selected plan,
authorization receipt, outcome observation, or action-effect certificate;
those remain separate future artifacts.

## Validation

Validate the immutable published v1 snapshot and frozen repository v2.0
snapshot:

```bash
python registry/validate_snapshot.py
```

Rebuild and validate the Paper X source record:

```bash
python experiments/paper10/validation/build_results.py
python experiments/paper10/validation/validate_results.py
```

The validator checks schema version, admission, capabilities, policies,
artifact digests, finding/evidence compatibility, promotion conditions,
census digest, and archive boundaries.
