# Paper VII Experiments

Paper VII v2 is a static incidence-geometry paper on fixed sectorizations.
Its active evidence layer has three scripts:

| Script | Claim scope |
|--------|-------------|
| `validation/incidence_variety_codim.py` | exact integer evaluation of fixed-rank and fixed-double-rank dimension formulas |
| `validation/rank_protected_bridge_audit.py` | numerical routed-product census with corrected left/right rank protection, six-zero Rubik operator registration, and image--kernel witness metrics |
| `validation/atlas_r2_boundary.py` | finite full-array comparison of typed low-order Lie support, per-depth support, complete depth arrays, and generator--basis closure residuals |

Generated records live under `results/`. They are versioned computational
observations and reproducibility artifacts. They do not promote routed products
to words or commutators, and they do not prove low-order-to-depth completion.

Historical Type-IV searches, the old completion atlas, and the former
cross-species Markov/graph appendix script live under `archive/`. They are not
current claim authority. The Markov and graph examples were re-registered with
native positive-word semantics under `experiments/paper10/markov_graph_sof.py`;
the archived Paper VII script remains provenance only.

`figures/paper7/render.py` reads the current `incidence_geometry.json` and
`projected_composition_audit.json` records directly. It renders the ambient
codimension and Rubik incidence-census figures without using the retired
generic-completion or Type-IV figure program.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
