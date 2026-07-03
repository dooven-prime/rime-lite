# Experiments — One-Click Paper Reproduction

Each file is a self-contained experiment producing one result that directly supports a claim in the trilogy. All experiments are deterministic (`np.random.seed(42)`).

## Directory Map

```
experiments/
├── README.md                     ← this file
│
├── paper1/                       ← Paper I: Spectral Origin (A)
│   ├── spectral_ladder.py        ← 6-layer spectrum: λ=1−k/9, dims, block support
│   ├── k_absence.py              ← k=5 genuinely absent (not numerical)
│   ├── block_composition.py      ← Per-layer block support breakdown
│   └── projector_algebra.py      ← P_i·P_j=δ_ij P_i, ΣP_i=I, Tr(P_i)=dim_i
│
├── paper2/                       ← Paper II: Transport Topology (K_αβ)
│   ├── primitive_sectors.py      ← 9 sectors from Center{A, QT_all, HT_all}
│   ├── transport_graph.py        ← K matrix, symmetry, graph edges
│   ├── supp_nc.py                ← Noncommutativity per block (cp=0, ep=93.9%)
│   └── ep_algebra.py             ← EP block: M₂⁴ ⊕ M₁⁴ (semisimple, center, Killing)
│
├── paper3/                       ← Paper III: Lie Accessibility (κ_d)
│   ├── t7_detection.py           ← T7 pairs: 5 cross-block, K=κ₀=κ₁=0, 2-step reachable
│   ├── kappa_depth.py            ← κ₀ (gradient) + κ₁ (curvature) hierarchy
│   ├── t7_refined.py             ← S₃ nat⊕reg: canonical + refined, C0 negative control, 0 T7
│   ├── t7_reg_reg.py             ← S₃ reg⊕reg: canonical, C0 negative control, 0 T7
│   └── t7_necessity.py           ← C1 necessity: shared irrep test (abelian + S₃ disjoint)
│
├── paper2_figures.py             ← Paper II figure generation batch
├── paper3_figures.py             ← Paper III figure generation batch
├── ccs_figures.py                ← CCS canonical figures (→ figures/ccs/)
├── persistence_bridge.py         ← CCS-r2 Parts II.12-II.15: spectral persistence, transition atlas
├── trilogy_overview.py           ← Trilogy cascade overview (→ figures/trilogy_overview.png)
└── trilogy_master_figure.py      ← Unified trilogy master figure
```

## Invariant Level

## Paper II v2 additions

- `experiments/paper2/joint_spectral_geometry.py` verifies the 9 rational QT/HT joint-spectrum points and the `A_18` collision quotient.
- `experiments/paper2/collision_geometry.py` verifies the exact affine-branch collision classification, no shadow collisions, and the unique maximal collapse at `alpha=2/3`.

## Paper IV support scripts

- `experiments/paper4/rubik_collision_quotient.py` verifies the exact finite-point collision quotient: `36 = 2 + 10 + 15 + 9`, no shadow collisions, and unique maximal collapse at `alpha=2/3`.
- `experiments/paper4/v59_collision_vs_transport.py` verifies that the `V_5/9` collision component is a triangle while direct transport is the chain `S5-S6-S7`.

## Paper V support scripts

- `experiments/paper5/s4_r1_r2_depth.py` verifies the S4-3gen-B `R1`/`R2`/depth example with signature `(10,2,2,76)`.
- `experiments/paper5/path_commutator_cancellation.py` verifies the S4-3gen-B binary-support counterexample: two length-2 `R1` candidates cancel at projected commutator depth and first appear at depth `2`.
- `experiments/paper5/complement_explosion.py` records the support/scalar complement obstruction model and its nonzero `R2` bridge repair.
- `experiments/paper5/noncomplement_obstruction_enumeration.py` enumerates finite support-level obstruction patterns and records non-complement families.
- `experiments/paper5/matrix_nondegeneracy.py` verifies the S4-3gen-B single-term bridge matrix audit: `48/48` products nonzero and rank-protected.

## Cross-reference support scripts

- `experiments/cross_ref/emlp_morphosymm_character_diagnostic.py` cleans the old EMLP/W33/MorphoSymm cross-reference prototypes into a claim-status-gated diagnostic: exact S3 commutant and character-idempotent checks, Rubik `A_18` spectral coordinates, QT/HT sector-basis `Q`, `decompose_signal()`, and sampled sector trace fingerprints. This is related-work support, not a theorem source.

| Level | Meaning | Papers |
|-------|---------|--------|
| 0 | Categorical | Block structure exists |
| 1 | Group-algebraic | Spectral law, isotypic decomposition |
| 2 | Generator-conditioned | Transport strengths, T7 count |

Paper I: levels 1-2. Paper II: level 2. Paper III: level 2.

## Usage

```bash
# Single experiment
python experiments/paper1/spectral_ladder.py

# All Paper I experiments
for f in experiments/paper1/*.py; do python "$f"; done

# Run everything
python tests/run_all_tests.py          # invariant verification (assert-style)
```

## Seed & Reproducibility

All experiments use `np.random.seed(42)`. Center decomposition uses fixed seed internally. Figures are auto-saved to `experiments/paperN/figures/`.
