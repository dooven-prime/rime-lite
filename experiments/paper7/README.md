# Paper VII Experiments

Paper VII v2.1 is a static incidence-geometry paper on fixed sectorizations.
It extends the free matrix-pair calculation to common carrier-block
structures and registers one fixed-frame represented profile. Its active
evidence layer has five scripts:

| Script | Claim scope |
|--------|-------------|
| `validation/incidence_variety_codim.py` | exact integer evaluation of fixed-rank and fixed-double-rank dimension formulas |
| `validation/structured_incidence_geometry.py` | exact evaluation of carrier-rank-vector formulas, the diagonal-ambient correction, and a complementary-support pullback control |
| `validation/rank_protected_bridge_audit.py` | numerical routed-product census with corrected left/right rank protection, six-zero Rubik operator registration, and image--kernel witness metrics |
| `validation/atlas_r2_boundary.py` | finite full-array comparison of typed low-order Lie support, per-depth support, complete depth arrays, and generator--basis closure residuals |
| `validation/register_fixed_frame_profiles.py` | source-addressed promotion of the 19-orbit fixed canonical-frame census and exact carrier-zero certificate |

Generated records live under `results/`. They are versioned computational
observations and reproducibility artifacts. They do not promote routed products
to words or commutators, and they do not prove low-order-to-depth completion.

The v2.1 fixed-frame registration consumes only the canonical-frame outputs
under `experiments/exploratory/structural_functionals/incidence_profiles/`.
It excludes endogenous-frame profiles, the n=8 spectrum, cross-frame
alignment, and the proposed universal `2/9` law. The exact carrier certificate
establishes the zero status of the registered numerator; nonvanishing of all
remaining supported routes, and therefore the displayed `2/9` rate, remains a
finite Computational Observation.

The promoted exact certificate audits every fixed-width arithmetic operation,
not only matrix multiplication. Its source record carries conservative bounds
for identity, add, subtract, scale, adjoint, matrix multiplication, and trace,
with Python-integer trace accumulation.

Historical Type-IV searches, the old completion atlas, and the former
cross-species Markov/graph appendix script live under `archive/`. They are not
current claim authority. The Markov and graph examples were re-registered with
native positive-word semantics under `experiments/paper10/markov_graph_sof.py`;
the archived Paper VII script remains provenance only.

`figures/paper7/render.py` reads the current `incidence_geometry.json` and
`projected_composition_audit.json` records directly, together with the v2.1
structured and fixed-frame records. It renders free, structured, and
represented-incidence boundaries without using the retired generic-completion
or Type-IV figure program.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.

The two v2.1 structured producers are read-only by default: they recompute and
compare exact JSON/text output with the committed candidate artifacts. Use
`--write-results` only while intentionally refreshing the v2.1 candidate;
ordinary validation must omit it.

```bash
python experiments/paper7/validation/structured_incidence_geometry.py
python experiments/paper7/validation/register_fixed_frame_profiles.py
```
