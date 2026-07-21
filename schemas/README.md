# Versioned SOF Data Contracts

This directory is the canonical source for machine-readable SOF contracts in
`rime-lite`.

```text
schemas/
  sofrs/v1.0.schema.json      one concrete SOF diagnostic run
  sofrs/paper12-protocol-profile-v1.0.json Paper XII admission rules
  sofaudit/v1.0.schema.json   one aligned reference/target SOF comparison
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
- **SOF Comparison Schema** validates a `.sofaudit` artifact comparing two
  aligned SOFRS reports. The fields `reference`, `target`, `alignment`, and
  `comparison_specification` serialize the canonical comparison object
  $\mathfrak C_{\mathrm{cmp}}=(\mathcal R^\star,\widehat{\mathcal R},
  \Phi;\Theta)$. Its `signature` field separately serializes the induced output
  $\Delta_{\mathrm{audit}}$. It is a companion contract, not a new SOFRS
  version. Legitimate before/after controls may additionally declare
  `comparison_role`, `transformation_contract`, and `contract_evaluation`;
  the contract residual never replaces the raw comparison signature. These
  fields remain optional at the JSON-Schema level for v1.0 compatibility, but
  `validate_sofaudit.py` treats all three as conditionally required for a
  `legitimate_transformation_control`.
- **SOF Registry Schema** validates a versioned collection of species entries.
  Each entry records the five Paper X layers: species, SOF object, observable
  ladder, dynamics, and diagnostics. Claim status remains metadata.

Published schema versions are immutable. A change to required fields,
controlled vocabularies, or field meaning requires a new versioned file.
Contracts for unreleased downstream stages are intentionally excluded from this
public schema index.
