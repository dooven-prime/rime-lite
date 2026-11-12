# Paper XLII Publication Evidence Index

This directory binds the numbered Paper XLII edition to the historical
proper-arc source, finite controls, and independently archived Lean
companion. It does not move or rewrite their proof-owning files.

| Manuscript result | Evidence level |
|---|---|
| Proposition 3.1 and Theorem 4.2 | manuscript proof; Lean origin and chain layer |
| Theorems 5.2 and 5.3 | manuscript proof; Lean placement-fibre and dependent-summary layer |
| Theorem 6.1 | manuscript proof; Lean exact-count layer; complete finite controls for $n=3..6$ |
| Proposition 7.1 | manuscript proof comparing Paper XLI; outside the Lean companion |
| Propositions 8.1--8.2, Corollary 8.3, Theorem 8.4 | manuscript proofs; outside the Lean companion |

The historical submission identifier is `hal-05848115v1`; the source
snapshot is `proper-arc-summaries-source-v1.0`. The separately published
Lean source is `proper-arc-lean-companion-v1.0`, archived at
[10.5281/zenodo.23941878](https://doi.org/10.5281/zenodo.23941878).
These are provenance and proof identities, not a DOI for Paper XLII.

The candidate validator checks the edition and historical bytes. The
bounded finite replay and source-only Lean closure can be run from the
repository root with:

```text
python -B experiments/proper_arc_registered_summaries/validate_controls.py
python -B experiments/proper_arc_registered_summaries/lean/validate_companion.py --source-only --check-upstream-git
```

The accepted isolated cold Lean replay belongs to the companion archive.
Its original environment and limits are preserved there; this index does
not claim a new independent replay.
