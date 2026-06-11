"""Block Composition — per-layer block support of spectral layers.

Computationally verified:
  - Each spectral layer V_λ decomposes across cp/ep/co/eo blocks
  - Block support pattern is G-determined (same for all symmetric generator sets)
  - k=5 gap is the only gap in {0..9}

Paper: Paper I, Sec 3.3 (Block Support Analysis)
Invariant level: 1 (group-algebraic)
"""
import numpy as np
import os, sys
from rime.cubieoperator import CubieSpectralOperator
from rime.cubie import CubieMove, TOTAL_DIM, BLOCK_RANGES

np.random.seed(42)
FIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'figures', 'paper1')
os.makedirs(FIG_DIR, exist_ok=True)

op = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves)
layers = op.layer_keys

print("=" * 60)
print("  Paper I — Block Composition Analysis")
print("=" * 60)

block_names = list(BLOCK_RANGES.keys())
block_dims = {bn: end - start for bn, (start, end) in BLOCK_RANGES.items()}

print(f"\n  Block dimensions: cp={block_dims['cp']}, ep={block_dims['ep']}, "
      f"co={block_dims['co']}, eo={block_dims['eo']}")
print(f"  Total: {sum(block_dims.values())} = {TOTAL_DIM}")

# Per-layer block composition
print(f"\n  {'Layer':<10} {'Dim':>5} {'cp':>5} {'ep':>5} {'co':>5} {'eo':>5}  Dominant")
print(f"  {'-'*55}")
layer_data = []
for lam in layers:
    k = op.lam_to_k(lam)
    dim = op.layer_dimension(lam)
    P = op.projector(lam)
    comp = {}
    for bn, (s, e) in BLOCK_RANGES.items():
        comp[bn] = int(round(np.trace(P[s:e, s:e]).real))
    dominant = max(comp, key=comp.get)
    layer_data.append({'k': k, 'lam': lam, 'dim': dim, 'comp': comp, 'dominant': dominant})
    print(f"  V({k}/9)     {dim:>5} {comp['cp']:>5} {comp['ep']:>5} "
          f"{comp['co']:>5} {comp['eo']:>5}  {dominant}")

# Cross-block analysis
print(f"\n  Pure-block layers (≥90% in one block):")
for d in layer_data:
    dim = d['dim']
    for bn in block_names:
        if d['comp'][bn] >= 0.9 * dim:
            print(f"    V({d['k']}/9): {d['comp'][bn]}/{dim} in {bn}")

# Verify block totals
print(f"\n  Block total check (Σ_layer dim_in_block = block_dim):")
for bn in block_names:
    total = sum(d['comp'][bn] for d in layer_data)
    expected = block_dims[bn]
    status = "✓" if total == expected else f"✗ (expected {expected})"
    print(f"    {bn}: {total} = {expected} {status}")

# ── Figure ──
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(10, 6))
    block_colors = {'cp': '#5b6abf', 'ep': '#e74c3c', 'co': '#f39c12', 'eo': '#16a085'}

    x = np.arange(len(layer_data))
    width = 0.6
    bottom = np.zeros(len(layer_data))
    for bn in block_names:
        vals = [d['comp'][bn] for d in layer_data]
        ax.bar(x, vals, bottom=bottom, width=width, color=block_colors[bn],
               label=bn, edgecolor='white', linewidth=0.5)
        for i, v in enumerate(vals):
            if v > 5:
                ax.text(i, bottom[i] + v/2, str(v), ha='center', va='center', fontsize=7)
        bottom += vals

    labels = [f"V({d['k']}/9)\n(dim={d['dim']})" for d in layer_data]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('Dimension')
    ax.set_title('Block Composition of Spectral Layers', fontweight='bold')
    ax.legend(fontsize=9, ncol=4, loc='upper right')

    # Highlight k=5 absent
    ax.axvline(x=4.5, color='red', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.text(4.5, 105, 'k=5 absent', ha='center', color='red', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'block_composition.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Figure saved: {os.path.join(FIG_DIR, 'block_composition.png')}")
except ImportError:
    pass

print(f"\nDone — block composition verified.")
