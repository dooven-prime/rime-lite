# Versioned SOF Data Contracts

This directory is the canonical source for machine-readable SOF contracts in
`rime-lite`.

```text
schemas/
  sofrs/v1.0.schema.json      one concrete SOF diagnostic run
  sofaudit/v1.0.schema.json  one aligned reference/candidate SOF audit
  registry/v1.0.schema.json  one frozen five-layer Registry snapshot
```

The contracts are deliberately separate:

- **SOFRS** validates a `.sofreport` artifact produced by one experiment or
  named system.
- **SOF Audit Schema** validates a `.sofaudit` artifact comparing two aligned
  SOFRS reports. Its `signature` field serializes the mathematical output
  $\Delta_{\mathrm{audit}}$. It is a companion contract, not a new SOFRS
  version.
- **SOF Registry Schema** validates a versioned collection of species entries.
  Each entry records the five Paper X layers: species, SOF object, observable
  ladder, dynamics, and diagnostics. Claim status remains metadata.

Published schema versions are immutable. A change to required fields,
controlled vocabularies, or field meaning requires a new versioned file.
