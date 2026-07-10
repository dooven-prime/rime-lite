"""
Generator-Set Universality Test — Paper II

Tests whether the core structural phenomena (star topology, V2/3 freezing,
Lie incompleteness) are Rubik's cube specific or universal across generator sets.

Generator sets tested:
  - n=18: all face turns (baseline)
  - n=16: no R2/L2 (edge case)
  - n=12: quarter-turn only (CW/CCW, no half-turns)
  - n=10: face-balanced subset
  - n=9:  positive-face only (R/U/F)
  - n=8:  no axis-1, no half-turn (symmetry-breaking)
  - n=6:  half-turn only (180° turns)
  - n=4:  R/L quarter-turn only
  - n=3:  R face only

For each set, checks:
  1. Spectral eigenvalues and block structure
  2. Transport topology (star? hub?)
  3. Infinitesimal transport κ_ij matrix
  4. Discrete-continuous singular pairs

Key question: do κ_ij = 0 pairs persist across all symmetric generator sets?

Run: python experiments/paper2/generator_universality.py
"""
import sys
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, time

from rime.cubieoperator import CubieSpectralOperator
from rime.base import DATA_DIR

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ── Configuration ───────────────────────────────────────────────────────────────
GENERATOR_CONFIGS = {
    '18-full':     {'n': 18, 'label': 'All face turns', 'color': '#2980b9'},
    '16-noR2L2':   {'n': 16, 'label': 'No R2/L2', 'color': '#c0392b'},
    '12-quarter':  {'n': 12, 'label': 'Quarter-turn only', 'color': '#e67e22'},
    '10-balanced': {'n': 10, 'label': 'Face-balanced', 'color': '#8e44ad'},
    '9-posface':   {'n': 9,  'label': 'Positive-face only', 'color': '#16a085'},
    '8-symbreak':  {'n': 8,  'label': 'No axis-1, no HT', 'color': '#d35400'},
    '6-half':      {'n': 6,  'label': 'Half-turn only', 'color': '#27ae60'},
    '4-RL':        {'n': 4,  'label': 'R/L QT only', 'color': '#7f8c8d'},
    '3-Rface':     {'n': 3,  'label': 'R face only', 'color': '#2c3e50'},
}

FIG_DIR = os.path.join(DATA_DIR, 'paper_figures')
LAM_LABELS = ['V1', 'V7/9', 'V2/3', 'V5/9', 'V1/3']
LAYER_COLORS = ['#5b6abf', '#3498db', '#2ecc71', '#e74c3c', '#f39c12']


def analyze_generator_set(name, cfg):
    """Full structural analysis for a single generator set."""
    print(f"\n{'='*70}")
    print(f"  {name} ({cfg['label']}) — n={cfg['n']}")
    print(f"{'='*70}")

    t0 = time.time()
    cso = CubieSpectralOperator(n=cfg['n'])
    print(f"  Init: {time.time() - t0:.1f}s")

    layers = cso.layer_keys
    n_layers = len(layers)
    dims = [cso.layer_dimension(lam) for lam in layers]

    # 1. Spectral eigenvalues
    print(f"\n  Spectral layers ({n_layers}):")
    for lam in layers:
        print(f"    λ={lam:.6f}  dim={cso.layer_dimension(lam):3d}")

    # 2. Transport tensor — check star topology
    tg = cso.transport_graph()
    print(f"\n  Transport graph:")
    print(f"    Is star: {tg['is_star']}")
    print(f"    Hub: {tg['hub']:.6f}" if tg['hub'] else "    Hub: None")
    print(f"    Isolated: {[f'{lam:.6f}' for lam in tg['isolated']]}")

    # Transport coupling matrix
    T = cso.transport_tensor()
    adj = tg['adjacency']

    # Build short labels from layer eigenvalues (adaptive to generator set)
    def _label(lam):
        """Short label: canonical name if matches, else λ rounded."""
        for canon_val, canon_name in [(1.0, 'V1'), (8/9, 'V8/9'), (7/9, 'V7/9'),
                                       (2/3, 'V2/3'), (5/9, 'V5/9'), (1/3, 'V1/3')]:
            if abs(lam - canon_val) < 1e-4:
                return canon_name
        return f'λ={lam:.4f}'

    lam_labels = [_label(lam) for lam in layers]
    n_show = min(n_layers, 7)  # show up to 7 layers

    # Check if canonical V7/9-V2/3 decoupling persists
    lam_keys = cso.layer_keys
    v79_idx = next((i for i, k in enumerate(lam_keys) if abs(k - 7/9) < 1e-4), None)
    v23_idx = next((i for i, k in enumerate(lam_keys) if abs(k - 2/3) < 1e-4), None)
    if v79_idx is not None and v23_idx is not None:
        v79_lam = lam_keys[v79_idx]
        v23_lam = lam_keys[v23_idx]
        t_79_23 = T[(v79_lam, v23_lam)]['max']
        t_23_79 = T[(v23_lam, v79_lam)]['max']
        print(f"    T[V7/9, V2/3] = {t_79_23:.2e}  T[V2/3, V7/9] = {t_23_79:.2e}")
        print(f"    V7/9-V2/3 decoupled: {t_79_23 < 1e-8}")

    # 3. Infinitesimal transport — κ_ij matrix
    print(f"\n  Infinitesimal transport κ_ij = max_g ||P_i A_g P_j||_F:")
    it = cso.infinitesimal_transport()
    km = it['kappa_matrix']

    # Print κ matrix
    label_w = max(8, max(len(lbl) for lbl in lam_labels[:n_show]) + 2)
    header = " " * label_w + "".join(f"{lam_labels[i]:>{label_w}s}" for i in range(n_show))
    print(header)
    for i in range(n_show):
        row = f"  {lam_labels[i]:>{label_w-2}s} "
        for j in range(n_show):
            row += f"  {km[i,j]:{label_w-2}.2e}"
        print(row)

    # 4. Compare discrete (K) vs continuous (κ) transport
    print(f"\n  Discrete transport K_ij = max_g ||P_i ρ(g) P_j||_F:")
    K_adj = adj  # adjacency matrix from transport graph
    header = " " * label_w + "".join(f"{lam_labels[i]:>{label_w}s}" for i in range(n_show))
    print(header)
    for i in range(n_show):
        row = f"  {lam_labels[i]:>{label_w-2}s} "
        for j in range(n_show):
            row += f"  {K_adj[i,j]:{label_w-2}.2e}"
        print(row)

    # Check directed asymmetry: max |K_ij - K_ji| and |κ_ij - κ_ji|
    max_k_asym = max(abs(K_adj[i,j] - K_adj[j,i]) for i in range(n_show)
                     for j in range(n_show))
    max_kappa_asym = max(abs(km[i,j] - km[j,i]) for i in range(n_show)
                         for j in range(n_show))
    print(f"\n  Directed asymmetry: max|K_ij-K_ji| = {max_k_asym:.2e},  max|κ_ij-κ_ji| = {max_kappa_asym:.2e}")

    # Identify pairs with strong discrete but weak continuous coupling
    print(f"\n  K/κ ratio (pairs with K>0.1):")
    for i in range(n_show):
        for j in range(n_show):
            if i != j and K_adj[i,j] > 0.1:
                ratio = K_adj[i,j] / max(km[i,j], 1e-15)
                if ratio > 10:
                    print(f"    {lam_labels[i]}→{lam_labels[j]}: K={K_adj[i,j]:.2f}, κ={km[i,j]:.2e}, ratio={ratio:.1e}")

    result = {
        'name': name,
        'label': cfg['label'],
        'n': cfg['n'],
        'n_layers': n_layers,
        'layers': layers,
        'dims': dims,
        'is_star': tg['is_star'],
        'hub': tg['hub'],
        'adjacency': adj,
        'kappa_matrix': km,
        'max_k_asym': max_k_asym,
        'max_kappa_asym': max_kappa_asym,
        'labels': lam_labels,
    }
    return result


def plot_universality(results):
    """Visual summary of universality across generator sets."""
    n_sets = len(results)
    fig = plt.figure(figsize=(18, 3 + 3 * n_sets))
    fig.patch.set_facecolor('#0d1117')

    # Panel A: κ_ij heatmaps side by side
    for idx, (name, res) in enumerate(results.items()):
        ax = fig.add_subplot(n_sets, 3, 3 * idx + 1)
        ax.set_facecolor('#0d1117')
        km = res['kappa_matrix']
        labels = res['labels']
        n_l = min(res['n_layers'], 5)
        im = ax.imshow(km[:n_l, :n_l], cmap='YlOrRd', aspect='auto',
                       vmin=0, vmax=max(km.max(), 1e-10))
        ax.set_title(f'{name} — κ_ij', color='white', fontsize=10, fontweight='bold')
        ax.set_xticks(range(n_l))
        ax.set_xticklabels(labels[:n_l], color='#cccccc', fontsize=7)
        ax.set_yticks(range(n_l))
        ax.set_yticklabels(labels[:n_l], color='#cccccc', fontsize=7)
        plt.colorbar(im, ax=ax)
        for i in range(n_l):
            for j in range(n_l):
                color = 'white' if km[i, j] > 1 else 'black'
                ax.text(j, i, f'{km[i,j]:.1e}', ha='center', va='center',
                       fontsize=6, color=color)

    # Panel B: transport comparison summary
    for idx, (name, res) in enumerate(results.items()):
        ax = fig.add_subplot(n_sets, 3, 3 * idx + 2)
        ax.set_facecolor('#0d1117')
        ax.text(0.5, 0.65, f'Star: {res["is_star"]}, Hub: {res["hub"]:.4f}' if res['hub'] else f'Star: {res["is_star"]}, Hub: None',
                fontsize=11, color='#3498db',
                ha='center', transform=ax.transAxes, fontweight='bold')
        ax.text(0.5, 0.45, f'K asymmetry: {res["max_k_asym"]:.2e}',
                fontsize=9, color='#aaaaaa', ha='center', transform=ax.transAxes)
        ax.text(0.5, 0.30, f'κ asymmetry: {res["max_kappa_asym"]:.2e}',
                fontsize=9, color='#aaaaaa', ha='center', transform=ax.transAxes)
        ax.text(0.5, 0.15, f'{res["n_layers"]} layers, Σ dim={sum(res["dims"])}',
                fontsize=8, color='#888888', ha='center', transform=ax.transAxes)
        ax.set_title(f'{name}', color='white', fontsize=11, fontweight='bold')
        ax.axis('off')

    # Panel C: adjacency comparison
    for idx, (name, res) in enumerate(results.items()):
        ax = fig.add_subplot(n_sets, 3, 3 * idx + 3)
        ax.set_facecolor('#0d1117')
        adj = res['adjacency']
        labels = res['labels']
        n_l = min(res['n_layers'], 5)
        im = ax.imshow(adj[:n_l, :n_l], cmap='Blues', aspect='auto')
        ax.set_title(f'{name} — K_ij', color='white', fontsize=10, fontweight='bold')
        ax.set_xticks(range(n_l))
        ax.set_xticklabels(labels[:n_l], color='#cccccc', fontsize=7)
        ax.set_yticks(range(n_l))
        ax.set_yticklabels(labels[:n_l], color='#cccccc', fontsize=7)
        plt.colorbar(im, ax=ax)
        for i in range(n_l):
            for j in range(n_l):
                color = 'white' if adj[i, j] > 2 else 'black'
                ax.text(j, i, f'{adj[i,j]:.2f}', ha='center', va='center',
                       fontsize=6, color=color)

    fig.suptitle('Generator-Set Universality: Transport Structure & Barrier Stability',
                 fontsize=15, fontweight='bold', color='white', y=0.99)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, 'universality_transport_barrier.png')
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='#0d1117')
    plt.close()
    print(f"\nSaved: {out}")


def print_summary(results):
    """Print a comparison table across generator sets."""
    print(f"\n{'='*90}")
    print("UNIVERSALITY SUMMARY")
    print(f"{'='*90}")

    header = f"{'Generator set':<18s} {'n':>3s} {'Layers':>6s} {'Star':>6s} "
    header += f"{'Hub':>8s} {'K_asym':>10s} {'κ_asym':>10s} {'Σ dim':>6s}"
    print(header)
    print("-" * 90)

    for name, res in results.items():
        hub_str = f"{res['hub']:.4f}" if res['hub'] else "None"
        line = f"{res['label']:<18s} {res['n']:3d} {res['n_layers']:6d} "
        line += f"{str(res['is_star']):>6s} {hub_str:>8s} "
        line += f"{res['max_k_asym']:10.2e} {res['max_kappa_asym']:10.2e} "
        line += f"{sum(res['dims']):6d}"
        print(line)

    # Key invariants
    print(f"\n── Structural Invariants Across Generator Sets ──")
    all_star = all(r['is_star'] for r in results.values())
    print(f"  Star topology preserved: {all_star}")

    # Check if same hub λ value appears
    hubs = set()
    for r in results.values():
        if r['hub'] is not None:
            hubs.add(round(r['hub'], 4))
    print(f"  Hub λ values: {hubs}")

    # Transport asymmetry summary
    print(f"\n  Directed transport asymmetry across sets:")
    for name, r in results.items():
        print(f"    {name}: K_asym={r['max_k_asym']:.2e}, κ_asym={r['max_kappa_asym']:.2e}")

    # Transport-geometry duality — check decoupling of non-communicating layers
    print(f"\n  Transport-decoupled pairs (where K_ij=K_ji=0) across sets:")
    for name, r in results.items():
        t = r['adjacency']
        layers = r['layers']
        zero_pairs = []
        for i in range(len(layers)):
            for j in range(i + 1, len(layers)):
                if t[i, j] < 1e-8:
                    zero_pairs.append((layers[i], layers[j]))
        if zero_pairs:
            pair_str = ', '.join(f'({a:.4f},{b:.4f})' for a, b in zero_pairs[:3])
            if len(zero_pairs) > 3:
                pair_str += f' +{len(zero_pairs)-3} more'
            print(f"    {name}: {len(zero_pairs)} pairs [{pair_str}]")
        else:
            print(f"    {name}: 0 decoupled pairs (fully connected)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 90)
    print("Generator-Set Universality Test")
    print("Tests structural stability of star topology, freezing, Lie incompleteness")
    print("=" * 90)

    results = {}
    for name, cfg in GENERATOR_CONFIGS.items():
        try:
            results[name] = analyze_generator_set(name, cfg)
        except Exception as e:
            print(f"\n  ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()

    if len(results) >= 2:
        print_summary(results)
        os.makedirs(FIG_DIR, exist_ok=True)
        plot_universality(results)

    print(f"\n{'='*90}")
    print("Done.")
    print(f"{'='*90}")


if __name__ == '__main__':
    main()
