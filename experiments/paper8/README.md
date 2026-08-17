# Paper VIII v2.1 Evidence Boundary

**Candidate revision:** Marked Finite-Realization and Word-Filtration Revision.

Paper VIII remains a static object-language paper. Its category,
functoriality, marked finite-realization, route/word, and finite-saturation
results are proved from declared finite-dimensional hypotheses. The promoted
computational material is an exact conformance witness, not a premise for
those proofs.

## Owned Evidence Chain

```text
exploratory finite-action bundles
  -> exact upstream replay
  -> Paper VIII promotion producer
  -> P8V2.1-CONFORMANCE
  -> Paper VIII replay validator
  -> P8V2.1-REPLAY
  -> manuscript Computational Certificate claims
```

The exploratory source artifacts retain their original provenance and
`NOT_PROMOTED` status. Paper VIII owns the promotion decision, reduced claim
surface, conformance certificate, and replay receipt.

## Public Upstream Package

The reviewed public source package is
`experiments/exploratory/carrier_realizations/fuchsian_schreier/`. Its
executable package closure includes the finite carrier core, modular and
triangle census producers, exact JSON bundles, replay validator, Markdown
projections, and hostile control.

Paper VIII imports only the two JSON bundles listed below. Public package
documentation, projections, hostile controls, and internal migration lineage
are not additional Paper VIII evidence.

## Active Artifacts

| Artifact ID | Path | Role |
|---|---|---|
| `P8V2.1-CONFORMANCE` | `experiments/paper8/results/v2.1/marked_finite_realization_conformance_v2_1.json` | paper-owned promoted certificate |
| `P8V2.1-REPLAY` | `experiments/paper8/results/v2.1/marked_finite_realization_conformance_v2_1.validation-receipt.json` | validation receipt |
| summary | `experiments/paper8/results/v2.1/marked_finite_realization_conformance_v2_1.md` | human-readable projection |
| producer | `experiments/paper8/validation/promote_marked_finite_realizations_v2_1.py` | source-addressed promotion and saturation replay |
| validator | `experiments/paper8/validation/validate_marked_finite_realizations_v2_1.py` | fail-closed certificate replay |

Upstream provenance inputs:

- `experiments/exploratory/carrier_realizations/fuchsian_schreier/results/modular_p1_census_v2.json`;
- `experiments/exploratory/carrier_realizations/fuchsian_schreier/results/triangle_low_index_census_v2.json`.

## Claim Matrix

| Claim ID | Claim class | Statement | Carrier/object | Status | Source | Validator | Manuscript location |
|---|---|---|---|---|---|---|---|
| `P8V2.1-T04` | local theorem | labelled finite action plus marked partition defines an exact operator SOF | finite permutation realization | Theorem | proof | n/a | Marked Finite Permutation Realization |
| `P8V2.1-T05` | local theorem | routed and full-word Boolean support coincide for coordinate-sector permutation carriers | operator/word branch | Theorem | proof | n/a | Permutation Route/Word Coincidence |
| `P8V2.1-T06` | local theorem | finite represented positive closure decides exact first-hit word depth | finite permutation closure | Theorem | proof | n/a | Exact Finite Positive-Word Saturation |
| `P8V2.1-T07` | local theorem | the four-state witness has `W_2=Route_2` strictly contained in `Path_2` | exact marked two-sector carrier | Theorem | proof | n/a | Boolean Path Overestimate |
| `P8V2.1-CERT-01` | local computational claim | six modular and seventeen triangle actions instantiate exact marked finite cores | 57 marked realizations | Computational Certificate | `P8V2.1-CONFORMANCE` | paper8 replay validator | Promoted Conformance Certificate |
| `P8V2.1-CERT-02` | local computational claim | three distinct label pairs retain equal represented operators without label deduplication | labelled triangle carriers | Computational Certificate | `P8V2.1-CONFORMANCE` | paper8 replay validator | Promoted Conformance Certificate |
| `P8V2.1-CERT-03` | local computational claim | the exact four-state matrices replay the strict Path/Route/W relation | hostile finite carrier | Computational Certificate | `P8V2.1-CONFORMANCE` | paper8 replay validator | Proposition 7 and certificate section |
| `P8V2.1-CERT-04` | local computational claim | all 57 first-hit records are bound to complete represented-image saturation receipts | positive-word filtration | Computational Certificate | `P8V2.1-CONFORMANCE` | paper8 replay validator | Promoted Conformance Certificate |

## Rebuild and Validate

From the repository root:

```bash
python experiments/paper8/validation/promote_marked_finite_realizations_v2_1.py
python experiments/paper8/validation/validate_marked_finite_realizations_v2_1.py --write-receipt
python papers/tex/build.py paper8
```

The validator performs full upstream replay, installed-source digest checks,
Paper VIII certificate reconstruction, exact hostile-witness checks, finite
right-closure checks, and coordinated result/digest tamper rejection.

## Promoted Scope

- six modular actions on `P^1(F_p)` for `p=3,5,7,11,13,17`;
- seventeen bounded triangle-group actions for signatures `(2,3,7)`,
  `(2,4,5)`, and `(3,3,4)` through index seven;
- fifty-one triangle cycle-sector realizations and six modular orbit-sector
  realizations;
- three equal-operator/distinct-label witnesses;
- one exact four-state `Path_2` overestimate witness;
- fifty-seven complete finite positive-closure saturation receipts.

## Negative Boundary

- A finite representation does not canonically select a SOF sectorization.
- The labelled map is not replaced by its represented image set.
- No Lie/Hall carrier, commutator support, or Lie depth is promoted.
- No generic strict separation of positive and star closures is claimed.
- No graph-Laplacian, spanning-tree, surface, Hecke, moduli, Selberg, or
  automorphic field enters the manuscript claim surface.
- No exploratory source artifact becomes paper evidence without the paper-owned
  promotion record and receipt.

The representation, geometry, Markov, graph, activation, and external-sector
examples elsewhere in the manuscript remain illustrative realization classes.
Their scientific findings remain with the papers or applications that own the
corresponding static audit, deformation, Registry record, report, or
comparison.
