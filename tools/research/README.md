# Research Method Tools

This directory supports the non-protocol research workflow

```text
Explore -> Exactify -> Prove -> Formalize
```

The tools do not infer theorem truth or promote claims. They compare explicitly
declared research surfaces and fail when their source-addressed bindings drift.

`validate_claim_surface.py` checks:

- preservation of declared historical observation and certificate bytes;
- claim IDs and statuses in a paper-owned promotion certificate;
- manuscript markers named by an explicit surface map;
- exact Lean source digests from the paper-owned formalization manifest;
- declared manuscript-theorem to Lean-declaration alignment;
- complete mapping of the promoted claim surface.

Example:

```text
python tools/research/validate_claim_surface.py \
  experiments/paper21/claim-surface-map.json
```

Finite counterexample search, exceptional-regime partition, and exact
certificate production remain mathematical, paper-owned operations. This
generic layer validates their declared lifecycle; it does not replace them.
