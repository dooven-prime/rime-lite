# BCH Composition Promotion Note

**Status:** exploratory interface note, not a normative SOF contract.

## Ownership Chain

The proposed future chain is:

```text
declared Lie/Hall carrier and ordered composition semantics
  -> replayable BCHSignature plus evidence
  -> optional Paper XII report module retaining that signature
  -> optional Paper XIII Audit Profile coordinate
  -> aligned BCH comparison state
```

Paper XIII must not derive BCH coefficients from raw generators while
assembling an audit. It may compare only signatures retained by two validated
reports, with explicit carrier, generator, Hall-basis, quotient, order,
truncation, and scope alignment.

The frozen control registers `X` and `Y` as operative input generators and
records `Z=[X,Y]` as an induced Hall-basis coordinate. A structured alignment
therefore binds the operative generator bijection and its bracket-preserving
extension to retained Hall coordinates; it does not promote every Hall basis
element to an operative generator.

## Candidate Report Payload

A future Paper XII module would retain, without recomputing:

```text
module_id
capability_id = bch_composition_signature
value_schema_id
carrier_definition_ref
implementation_ref
generator_registration
composition_convention
hall_basis
quotient_relation
truncation_order
completion_status
signature_ref
evidence_refs
```

The report module would state only that a validated upstream signature and its
evidence were retained. Scientific adequacy of the carrier and implementation
would remain external to SOFRS assembly. Cross-report `generator_alignment`
is intentionally absent from this payload. It belongs to the Paper XIII
comparison input and binds the two retained registrations; equal label strings
never imply alignment.

## Candidate Audit Coordinate

A future optional Audit Profile could request:

```text
coordinate_family = bch_composition
comparison_scope = full_bch | through_degree
required_capability = bch_composition_signature
required_alignment = carrier + structured generator alignment + Hall basis + quotient + order
```

The coordinate-local `bch_status` remains separate from Paper XIII's global
`comparison_state`. In particular, `TRUNCATED_MATCH` projects to `ALIGNED`
only when the retained coordinate is explicitly scoped through a finite
degree. The corresponding full-BCH state remains `UNRESOLVED`.

## Runtime Destination

After a normative extension contract is accepted, `sof-runtime` should own:

- the evaluator implementation registry and implementation digest;
- report-item and evidence binding;
- signature replay in an isolated evaluator invocation;
- SOFAUDIT coordinate production and validation replay;
- receipt closure and hostile cross-language conformance tests.

The current Python package is a mathematical and protocol-development control.
It is not that runtime closure.

## Promotion Gates

Promotion requires all of the following:

1. a versioned BCH signature value schema;
2. a language-neutral structured generator-alignment schema;
3. a Paper XII optional report-module contract;
4. a Paper XIII optional coordinate/profile extension;
5. a digest-registered `sof-runtime` evaluator and independent replay;
6. hostile tests for carrier spoofing, stale and coordinated digest tampering,
   coefficient/sequence inconsistency, truncation escalation, unavailable
   capability, and unregistered implementations.

Until those gates are met, this package remains outside the Paper XIII v2.1
main contract and Standard Regime-A profile.
