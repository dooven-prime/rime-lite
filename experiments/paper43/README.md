# Paper XLIII Publication Evidence Index

This directory binds the numbered Paper XLIII reader edition to its
historical source commit, finite controls, and separately archived Lean
companion. It does not move or rewrite their proof-owning files.

| Manuscript result | Evidence level |
|---|---|
| Lemmas 3.1--3.2 and 4.1--4.3 | manuscript proofs; source-order and registered-placement interfaces in the Lean companion |
| Lemmas 5.2--5.3 and Corollary 5.5 | manuscript proofs of probe coalescence and separation; corresponding Lean proof layer |
| Theorems 6.1--6.2 | manuscript proofs; all-parameter Lean future-event classification and distinguishing bound |
| Section 7 counts and growth comparison | manuscript proofs; separate Lean full-summary and comparison layers |
| Finite controls | complete generated graphs for `n=3..5`, two finite right congruences, and all class-pair separator checks |

The frozen Lean theorem map links to the historical manuscript. The numbered
edition changes these printed labels, without changing their statements:

| Historical manuscript | Paper XLIII |
|---|---|
| Corollary 5.4 | Corollary 5.5 |
| Theorem 1 | Theorem 6.1 |
| Theorem 2 | Theorem 6.2 |
| Lemma 6.1 | Lemma 6.3 |

The historical submission identifier is `hal-05844771v1`. Its source is
bound by the reachable Git commit `5dd17636ba65060b0a84773fccacbf1505fa6a39`
and the individual file hashes in `evidence-map.v1.json`; there is no
historical source tag to assert. The Lean source is tagged
`future-event-lean-companion-v1.0` and archived at
[10.5281/zenodo.23914476](https://doi.org/10.5281/zenodo.23914476).
Neither identity is a DOI for Paper XLIII.

From the repository root, the numbered candidate gate is:

```text
python -B tools/release/validate_numbered_migration_commit_candidate.py 43 --write-receipt
```

This gate checks the numbered bytes, historical Git bytes, bounded finite
replay, Lean source-only closure, and theorem-to-source map. The source-only
checks do not recompile Lean; the companion's archived proof and acceptance
materials retain their own identity and limits. A local candidate receipt
does not claim an external publication or independent cross-host replay.
