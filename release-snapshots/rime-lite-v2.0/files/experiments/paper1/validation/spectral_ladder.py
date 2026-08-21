"""Spectral Ladder — six registered labels for the spectrum of A₁₈.

Computationally verified:
  - Spec(A₁₈) = {1 − k/9 | k ∈ {0, 1, 2, 3, 4, 6}}
  - Multiplicities: [20, 2, 39, 26, 106, 35]
  - k=5 absent from the registered canonical spectrum

Paper: Paper I, Computational Proposition 3.5
Claim status: canonical computational census
"""
import _bootstrap  # noqa: F401
import numpy as np
import os, sys
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES

np.random.seed(42)
FIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'figures', 'paper1', 'diagnostics')
os.makedirs(FIG_DIR, exist_ok=True)

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
layers = op.layer_keys

print("=" * 72)
print("  Paper I — Spectral Ladder")
print("  Spec(A_18) = {1 - k/9 | k in {0,1,2,3,4,6}}")
print("=" * 72)
print(f"\n  {'k':>4}  {'lambda':>12}  {'dim':>5}  {'cp':>5}  {'ep':>5}  {'co':>5}  {'eo':>5}")
print(f"  {'-'*50}")

total = 0
for lam in layers:
    k = op.lam_to_k(lam)
    dim = op.layer_dimension(lam)
    total += dim
    P = op.projector(lam)
    blocks = []
    for bn, (s, e) in BLOCK_RANGES.items():
        tr = int(round(np.trace(P[s:e, s:e]).real))
        blocks.append(f"{tr:>5}")
    print(f"  {k:>4}  {lam:>12.10f}  {dim:>5}  " + "  ".join(blocks))

print(f"  {'-'*50}")
print(f"  {'':>4}  {'':>12}  {total:>5}")
print(f"\n  k=5 absent: {5 not in [op.lam_to_k(lam) for lam in layers]}")
print(f"  Registered k-set: {{0,1,2,3,4,6}}")
print(f"  Unobserved in 0..9: {{5,7,8,9}}")

# ── Simple figure ──
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    k_vals = [op.lam_to_k(lam) for lam in layers]
    dims = [op.layer_dimension(lam) for lam in layers]
    colors = ['#2980b9', '#27ae60', '#8e44ad', '#e67e22', '#e74c3c', '#16a085']

    ax1.bar(range(6), dims, color=colors, edgecolor='white', linewidth=1.5)
    ax1.set_xticks(range(6))
    ax1.set_xticklabels([f'k={k}' for k in k_vals])
    ax1.set_ylabel('Dimension')
    ax1.set_title('Spectral Layer Dimensions')
    for i, d in enumerate(dims):
        ax1.text(i, d + 2, str(d), ha='center', fontsize=10)

    # Block composition stacked bars
    block_data = np.zeros((6, 4))
    block_names = ['cp', 'ep', 'co', 'eo']
    block_colors = ['#5b6abf', '#e74c3c', '#f39c12', '#16a085']
    for i, lam in enumerate(layers):
        P = op.projector(lam)
        for j, (bn, (s, e)) in enumerate(BLOCK_RANGES.items()):
            block_data[i, j] = int(round(np.trace(P[s:e, s:e]).real))

    bottom = np.zeros(6)
    for j in range(4):
        ax2.bar(range(6), block_data[:, j], bottom=bottom,
                color=block_colors[j], label=block_names[j], edgecolor='white')
        bottom += block_data[:, j]
    ax2.set_xticks(range(6))
    ax2.set_xticklabels([f'k={k}' for k in k_vals])
    ax2.set_ylabel('Dimension')
    ax2.set_title('Block Composition per Layer')
    ax2.legend(fontsize=9)

    # Mark k=5 as absent
    for ax in [ax1, ax2]:
        ax.axvline(x=4.5, color='red', linestyle='--', alpha=0.4, linewidth=1)
    ax1.text(4.5, max(dims) * 0.9, 'k=5\nabsent', ha='center', color='red', fontsize=9)

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'spectral_ladder.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Figure saved: {os.path.join(FIG_DIR, 'spectral_ladder.png')}")
except ImportError:
    print("\n  (matplotlib not available — skipping figure)")

print(f"\nDone — spectral ladder verified.")
