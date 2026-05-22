# RIME

**Representation-theoretic Investigation of Mathematical Emergence** — a trilogy proving that discrete group composition is structurally richer than the continuous Lie limit.

---

<p align="center">
  <img src="figures/trilogy_overview.png" width="100%">
</p>

<p align="center">
  <em>The RIME cascade: rational spectrum → transport topology → composition-only transport (T7)</em>
</p>

---

## What Is This?

The 228-dimensional representation of the Rubik's Cube group has a spectral structure that no one predicted and no one has explained — until now.

The averaging operator $A = \frac{1}{|S|}\sum \rho(s)$ over 18 face-turn generators has exactly **six rational eigenvalues** despite the generators failing to commute. The representation decomposes into **nine primitive sectors** connected by **ten transport edges**, all block-preserving. And there exist **five sector pairs** that no depth of Lie commutator can reach — yet a single discrete composition step can.

This trilogy explains why.

## The Three Papers

| Paper | Object | Question | Answer |
|-------|--------|----------|--------|
| **I. Spectral Rationality** | $A = \frac{1}{\|S\|}\sum\rho(s)$ | Why is the spectrum rational? | Partition integrality: face completeness forces integer traces via $\omega + \omega^2 + 1 = 0$ |
| **II. Transport Topology** | $K_{\alpha\beta} = \max_g \|P_\alpha\rho(g)P_\beta\|$ | Why does the transport graph have its observed structure? | The $M_2(\mathbb{C})^4$ components of $A_{\text{EP}}$ drive hub formation and cap refinement at 9 sectors |
| **III. Lie Accessibility** | $\kappa_d = \max\|P_\alpha C_d P_\beta\|$ | Why can discrete composition beat the continuous limit? | All Lie monomials are block-diagonal (Lemma 1); composition through hybrid sectors bridges blocks (T7 Theorem) |

The three papers form a logical chain: **spectral origin → transport topology → Lie accessibility**. Each paper's conclusions are the next paper's starting point. No circular dependency.

## Main Structural Picture

### The 228-dimensional Rubik cube representation

```
V = V_cp (64) ⊕ V_ep (144) ⊕ V_co (8) ⊕ V_eo (12)
          │              │           │          │
      Q₃ Hamming    face-incidence  Z₃ phase   Z₂ phase
          │              │           │          │
          └──────────────┴───────────┴──────────┘
                         │
              A = (1/18) Σ ρ(s)  →  6 rational layers
                         │
              Center{A, QT, HT}   →  9 primitive sectors
```

### The key numbers

| Quantity | Value | Why it matters |
|----------|-------|----------------|
| Spectral layers | 6 (not 10) | 10 block idempotents collapse via eigenvalue coincidence |
| Absent eigenvalue | $k=5$ ($\lambda=4/9$) | No block produces it — structural vacancy |
| Transport edges | 10 | All block-preserving; zero cross-block direct edges |
| Primary hub | S6 (degree 5) | Unique sector intersecting all three active $M_2$ components |
| T7 pairs | 5 (cross-block) | Zero Lie transport at any depth; 2-step composition reaches them |
| $N=2$ control | 0 T7, 0 hybrid | Edge-permutation block ($M_2$) is necessary for both phenomena |

### The governing principles

- **M₂ Principle** — Noncommutative simple components ($n_i \geq 2$) are observed to be the sole carriers of refinement obstruction, transport mediation, and Lie curvature
- **T7 Principle** — In the Rubik and $S_3$ prototype systems, discrete composition is strictly more powerful than Lie accessibility

## Repository Structure

```
rime-lite/
├── rime/                          # Core computation
│   ├── cubieoperator.py           # CubieSpectralOperator — eigendecomposition, projectors, transport, commutant
│   ├── cubie.py                   # CubieState, CubieMove, BLOCK_RANGES
│   ├── spectralstructure.py       # Pre-spectral prediction: k-sets, eigenvalues
│   ├── spectral_utils.py          # joint_diag_sectors, find_t7_pairs
│   └── helpers.py                 # poly_rank, is_rational_form
│
├── experiments/                   # Verification + figures
│   ├── paper1/                    # Paper I experiments (spectral ladder, k-absence, block composition)
│   ├── paper2/                    # Paper II experiments (sectors, transport, supp_nc, EP algebra)
│   ├── paper3/                    # Paper III experiments (T7 detection, N=2 control, κ hierarchy)
│   ├── paper1_figures.py          # → figures/paper1/ (6 figures)
│   ├── paper2_figures.py          # → figures/paper2/ (11 figures)
│   ├── paper3_figures.py          # → figures/paper3/ (13 figures)
│   ├── ccs_figures.py             # → figures/ccs/ (12 figures)
│   ├── trilogy_overview.py        # → figures/trilogy_overview.png (this README's figure)
│   └── trilogy_style/             # Shared visual language for all figures
│
├── examples/
│   ├── paper1/Paper I - 260522.md # Paper I manuscript (canonical)
│   ├── paper2/Paper II - 260522.md
│   ├── paper3/Paper III - 260522.md
│   └── canonical_specification.md # CCS — unified numerical constitution
│
├── tests/                         # Invariant verification (no pytest)
│   ├── run_all_tests.py           # Fast tests (~5s, 8 suites)
│   └── run_slow_tests.py          # Slow tests (~5-10 min, 5 suites)
│
├── docs/
│   ├── CORE_INVARIANTS.md         # The 6 invariants
│   ├── PAPER_SCOPE.md             # What each paper studies
│   └── logs/                      # Audit and repair logs
│
└── figures/                       # Frozen output — never recomputed by paper build
    ├── paper1/
    ├── paper2/
    ├── paper3/
    ├── ccs/
    └── trilogy_overview.png
```

## Reproducibility

Every numerical claim in the trilogy is verified by code. No data files, no precomputed caches — all values are recomputed from first principles.

```bash
pip install -e .
python tests/run_all_tests.py            # Fast invariant tests (~5s)
python tests/run_slow_tests.py           # Full verification (~5-10 min)
python experiments/paper1_figures.py     # Paper I figures
python experiments/ccs_figures.py        # CCS figures
python experiments/trilogy_overview.py   # This README's figure
```

The test suite directly asserts the structural invariants:

| Test suite | Verifies |
|------------|----------|
| `test_spectrum.py` | 6 layers, rational λ, projector algebra |
| `test_sectors.py` | 9 sectors, S6 hub, S1 isolation |
| `test_transport.py` | K symmetry, 10 edges, 5 T7 pairs |
| `test_commutant_gap.py` | Comm(ρ)=610, Δ_comm=194 |
| `test_f3.py` | 51 isotypic components, multiplicity reservoir |
| `test_kappa_hierarchy.py` | κ₀ → 2-cycle, κ₁ → 3-cycle, T7 → breaks Lie sheet |

All experiments use `np.random.seed(42)`. All numerical assertions use `TOL = 1e-10`; transport detection uses `TOL_K = 0.05`.

## Quick Start

```bash
# The smallest self-contained T7 demonstration (Paper III core result)
python experiments/paper3/t7_minimal.py

# Why the spectrum has exactly 6 rational layers
python experiments/paper1/spectral_ladder.py

# The 9-sector transport topology
python experiments/paper2/primitive_sectors.py
```

Requires Python ≥ 3.10, numpy, scipy, matplotlib. Joblib optional (pickle fallback).

## Citation

```bibtex
@article{rime-trilogy,
  title   = {The {RIME} Trilogy: Spectral Rationality, Transport Topology,
             and Composition-Only Transport in the {Rubik}'s Cube Representation},
  author  = {Chen, WuJun},
  year    = {2026},
  note    = {Three-paper series with unified computational supplement}
}
```

Paper I: *Spectral Sector Decomposition in the Rubik's Cube Representation: Rational Spectral Collapse, Primitive Idempotents, and Block Spectral Factorization.*

Paper II: *Noncommutative Transport Topology in the Rubik's Cube Representation: Hybrid Sectors, Permutation Channels, and Refinement Obstructions.*

Paper III: *Accessibility Beyond Lie Closure in Finite Group Representations: Hybrid Projector Geometry and Composition-Only Transport.*

## Status

| Component | Status |
|-----------|--------|
| Core computation | Stable — all 8 fast tests + 5 slow tests pass |
| Paper I manuscript | Draft complete, Phase 0–5 repairs applied |
| Paper II manuscript | Draft complete, Phase 0–5 repairs applied |
| Paper III manuscript | Draft complete, Phase 0–5 repairs applied |
| CCS (computational supplement) | Frozen — canonical numerical constitution |
| Specification theorems | S2, S5, S6 proven; S1, S3, S4 verified (open) |
| Semantic label migration | Deferred to pre-submission |

---

*Maintained by Rime (WuJun Chen)*
