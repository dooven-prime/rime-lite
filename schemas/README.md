# Versioned SOF Data Contracts

This directory is the canonical source for machine-readable SOF contracts in
`rime-lite`.

```text
schemas/
  sofrs/v1.0.schema.json      one concrete SOF diagnostic run
  sofrs/paper12-protocol-profile-v1.0.json Paper XII admission rules
  sofaudit/v1.0.schema.json   one aligned reference/target SOF comparison
  sofaction/v1.0.schema.json  one contextual SOF action-semantics artifact
  sofdecision/v1.0.schema.json one legacy policy-relative decision record
  registry/v1.0.schema.json   one frozen five-layer Registry snapshot
```

The contracts are deliberately separate:

- **SOFRS envelope validation** checks the frozen v1.0 JSON shape of a
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
- **SOF Alignment Schema** validates a `.sofaudit` artifact comparing two
  aligned SOFRS reports. Its `alignment` field records the sector and
  observable alignment, and its `signature` field serializes the
  alignment-induced comparison signature $\Delta_{\mathrm{audit}}$. It is a
  companion contract, not a new SOFRS version. The v1.0 field named
  `candidate` is retained for compatibility; Paper XIII treats it as the
  target report. The v1.0 `normalization` field serializes the artifact-level
  part of the comparison specification $\Theta$; schema-version defaults may
  supply components not repeated in every artifact. Legitimate before/after controls may additionally declare
  `comparison_role`, `transformation_contract`, and `contract_evaluation`;
  the contract residual never replaces the raw comparison signature. These
  fields remain optional at the JSON-Schema level for v1.0 compatibility, but
  `validate_sofaudit.py` treats all three as conditionally required for a
  `legitimate_transformation_control`.
- **SOF Action Semantics Schema** validates a `.sofaction` artifact containing
  versioned coordinate interpretations, their derived candidate Action Set, and
  optional downstream policy selection. The core principle is that a nonzero
  signature records difference rather than defect; conforming transformations
  use `licensed_change`. Candidate actions remain distinct from execution
  authorization or optimality claims.
- **SOF Decision Schema** validates the legacy `.sofdecision` policy-control
  artifact. It is retained for compatibility and policy experiments, not as the
  primary Paper XIV mathematical object.
- **SOF Registry Schema** validates a versioned collection of species entries.
  Each entry records the five Paper X layers: species, SOF object, observable
  ladder, dynamics, and diagnostics. Claim status remains metadata.

Published schema versions are immutable. A change to required fields,
controlled vocabularies, or field meaning requires a new versioned file.
