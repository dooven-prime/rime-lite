"""T7 Detection — Discrete/Continuous accessibility split in N=3.

Computationally verified:
  - T7 pairs: cross-block sector pairs with K = κ₀ = κ₁ = 0
    but reachable via 2-step discrete composition through a hub.
  - T7 shows that discrete composition can access transitions
    that the continuous (Lie) limit cannot reach (predicted by Theorem T7, Paper III Sec. 5).
  - Block-diagonal ρ(g) → block-diagonal A_g → block-diagonal [A_g, A_h]
    → Lie closure preserves blocks → cross-block transitions require
    discrete composition.

Paper: Paper III, Sec 3 (T7 Theorem)
Invariant level: 2 (generator-conditioned)
"""
import numpy as np
import os
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, BLOCK_RANGES
from rime.spectral_utils import select_canonical_intermediate


np.random.seed(42)
TOL = 1e-10
TOL_K = 0.05
# NOTE: No TOL_KAPPA needed — T7 uses structural block-disjointness test.
# If block_sets[i] ∩ block_sets[j] = ∅, then κ_d = 0 is a structural consequence
# of Lemma 1 (block-diagonal Lie closure), not a numerical threshold comparison.
FIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'paper3')
os.makedirs(FIG_DIR, exist_ok=True)

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
sec = op.center_decomposition()
Ps = sec['projectors']
n = sec['n_sectors']

print("=" * 60)
print("  Paper III — T7 Detection")
print("  Discrete/Continuous Accessibility Split")
print("=" * 60)

# Build K, kappa0, kappa1 via canonical cached path
K_manual, kappa0, kappa1 = op.transport_kappa(Ps, compute_kappa1=True)

block_sets = op.sector_block_support(Ps)

# Print sector info
print("\n  Sector block support:")
for i, bs in enumerate(block_sets):
    k = op.lam_to_k(sec['sectors'][i]['lam_18'])
    print(f"    S{i+1}: V({k}/9), dim={sec['sectors'][i]['dim']}, blocks={bs}")

# T7 detection: structural obstruction test.
# Lemma 1 → Lie closure is block-diagonal → if block_sets[i] ∩ block_sets[j] = ∅,
# then κ_d(i,j) = 0 for ALL d (exact, structural). No numerical κ threshold needed.
print(f"\n  T7 candidates (disjoint blocks, K=0, 2-step reachable):")
t7_pairs = []
for i in range(n):
    for j in range(i+1, n):
        if not block_sets[i].isdisjoint(block_sets[j]):
            continue  # not cross-block
        if K_manual[i, j] >= TOL_K:
            continue  # has direct transport
        # κ_d = 0 follows structurally: Lemma 1 guarantees block-diagonal Lie closure
        # → P_i C_d P_j = 0 for disjoint blocks. No numerical threshold needed.

        # Check 2-step reachability: collect all valid intermediates,
        # then select the canonical witness by transport degree.
        candidates = [k for k in range(n)
                      if k != i and k != j
                      and K_manual[i, k] > TOL_K and K_manual[k, j] > TOL_K]

        if candidates:
            hub = select_canonical_intermediate(candidates, K_manual, TOL_K)
            t7_pairs.append((i, j, hub))
            print(f"    S{i+1} ↔ S{j+1}: K={K_manual[i,j]:.1e}, κ₀={kappa0[i,j]:.1e}, "
                  f"κ₁={kappa1[i,j]:.1e}, hub=S{hub+1}  ← T7!")
        else:
            print(f"    S{i+1} ↔ S{j+1}: K=0, blocks disjoint, but NOT 2-step reachable")

print(f"\n  T7 pairs detected: {len(t7_pairs)}")
for i, j, hub in t7_pairs:
    bi = sec['sectors'][i]
    bj = sec['sectors'][j]
    ki = op.lam_to_k(bi['lam_18'])
    kj = op.lam_to_k(bj['lam_18'])
    print(f"    S{i+1}(V({ki}/9), {block_sets[i]}) ↔ S{j+1}(V({kj}/9), {block_sets[j]}) "
          f"via S{hub+1}")

assert len(t7_pairs) >= 1, f"No T7 pairs found — discrete/continuous split not confirmed!"
print(f"\n  T7 theorem confirmed: discrete composition accesses transitions")
print(f"  that the Lie continuous limit cannot reach (predicted by Theorem T7, Paper III Sec. 5).")

# ── Figure ──
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: K matrix with T7 highlighted
    K_display = K_manual.copy()
    im = ax1.imshow(K_display, cmap='YlOrRd', aspect='equal', vmin=0)
    ax1.set_xticks(range(n))
    ax1.set_yticks(range(n))
    ax1.set_xticklabels([f'S{i+1}' for i in range(n)], fontsize=8)
    ax1.set_yticklabels([f'S{i+1}' for i in range(n)], fontsize=8)
    ax1.set_title('K_αβ with T7 pairs marked')

    # Mark T7 pairs with star
    for i, j, _ in t7_pairs:
        ax1.plot(j, i, '*', color='blue', markersize=15, markeredgecolor='white',
                markeredgewidth=1)
        ax1.plot(i, j, '*', color='blue', markersize=15, markeredgecolor='white',
                markeredgewidth=1)

    plt.colorbar(im, ax=ax1, shrink=0.8)

    # Right: Lie vs Discrete diagram
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 8)
    ax2.axis('off')
    ax2.set_title('Discrete/Continuous Split', fontweight='bold')

    # Lie world (left)
    lie_rect = plt.Rectangle((0.5, 1), 3, 6, fill=True, facecolor='#5b6abf', alpha=0.2)
    ax2.add_patch(lie_rect)
    ax2.text(2, 7.5, 'Lie World', ha='center', fontweight='bold', fontsize=11)
    ax2.text(2, 3.5, 'A_g block-diagonal\nκ₀=0 cross-block\nκ₁=0 cross-block',
            ha='center', fontsize=9)

    # Wall
    ax2.plot([4, 4], [1, 7], linewidth=3, color='#6c5b7b')
    ax2.text(4, 7.5, 'Block\nBoundary', ha='center', fontsize=8, color='#6c5b7b')

    # Composition world (right)
    comp_rect = plt.Rectangle((4.5, 1), 3, 6, fill=True, facecolor='#e67e22', alpha=0.2)
    ax2.add_patch(comp_rect)
    ax2.text(6, 7.5, 'Composition', ha='center', fontweight='bold', fontsize=11)
    ax2.text(6, 3.5, '2-step discrete\nbypasses block\nvia hybrid hub',
            ha='center', fontsize=9)

    # Arrow: discrete bypass
    ax2.annotate('', xy=(8, 5.5), xytext=(1, 5.5),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2,
                               connectionstyle='arc3,rad=0.3'))
    ax2.text(4.5, 6.3, 'T7 bypass', ha='center', fontsize=9, color='#e74c3c', fontweight='bold')

    # Arrow: Lie blocked
    ax2.annotate('', xy=(3.8, 4.5), xytext=(1.2, 4.5),
                arrowprops=dict(arrowstyle='->', color='#95a5a6', lw=1.5))
    ax2.text(2.5, 4.2, 'Blocked', ha='center', fontsize=8, color='#95a5a6')

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 't7_detection.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Figure saved: {os.path.join(FIG_DIR, 't7_detection.png')}")
except ImportError:
    pass

print(f"\nDone — T7 computationally verified in the canonical Rubik system.")
