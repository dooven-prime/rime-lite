"""
Paper II Figures: Transport Topology from Noncommutative Support

Post-ρ-fix (2026-05-13). Generates 5 figures:
  Fig 1: K Matrix Heatmap — 9×9 K_αβ, Type I/II transport taxonomy
  Fig 2: Transport Skeleton — connectivity geometry, hub structure, mechanism split
  Fig 3: Supp_nc Overlap — binary presence + per-block commutator strength
  Fig 4: Refinement Obstruction — commutative refinement → M₂ wall
  Fig 5: Structural Chain — A_EP → Supp_nc → K → Transport Topology

Visual philosophy: transport network geometry, overlap topology.
Entirely static — no dynamics, no Lie closure, no κ_d hierarchy.

Run: python test/_exp_paper2_figures.py
"""
import sys
import io
if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (ValueError, AttributeError):
        pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os, time

sys.path.insert(0, '.')
from rime.cubieoperator import CubieSpectralOperator
from rime.spectralstructure import block_projectors
from rime.trilogy_style.styles import apply_style
from rime.trilogy_style.colors import (
    SECTOR_COLORS, BLOCK_COLORS, SEMANTIC, CANVAS, layer_color
)
from rime.trilogy_style.elements import (
    NODE_MARKERS, NODE_SIZES, EDGE_STYLES, EDGE_COLORS,
    get_edge_style, styled_box, BORDER_WIDTH
)
from rime.base import DATA_DIR

apply_style('II')

TOL = 1e-10
TOL_K = 0.01  # threshold for K > 0

# ── Sector metadata (post-ρ-fix, 9-sector) ──────────────────────────────
SECTOR_NAMES = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']
SECTOR_LAYER = {
    'S1': 'V1', 'S2': 'V8/9', 'S3': 'V7/9', 'S4': 'V2/3',
    'S5': 'V5/9', 'S6': 'V5/9', 'S7': 'V5/9', 'S8': 'V1/3', 'S9': 'V1/3',
}
SECTOR_K = {'S1': 0, 'S2': 1, 'S3': 2, 'S4': 3, 'S5': 4, 'S6': 4, 'S7': 4, 'S8': 6, 'S9': 6}
SECTOR_BLOCK_SUPPORT = {
    'S1': ['cp', 'ep'],
    'S2': ['eo'],
    'S3': ['ep', 'eo'],
    'S4': ['ep', 'co'],
    'S5': ['eo'],
    'S6': ['ep', 'eo'],
    'S7': ['cp', 'ep', 'co', 'eo'],
    'S8': ['cp'],
    'S9': ['cp', 'co'],
}
SECTOR_SUPP_NC = {
    'S1': set(),
    'S2': {'eo'},
    'S3': {'ep', 'eo'},
    'S4': {'ep', 'co'},
    'S5': {'eo'},
    'S6': {'ep', 'eo'},
    'S7': {'ep', 'co', 'eo'},
    'S8': set(),
    'S9': {'co'},
}
SECTOR_HUB = {
    'S1': 'isolated', 'S2': 'leaf', 'S3': 'leaf', 'S4': 'leaf',
    'S5': 'leaf', 'S6': 'primary', 'S7': 'secondary', 'S8': 'leaf', 'S9': 'leaf',
}
# Known K matrix values (from paper_data.md §3.2, verified post-ρ-fix)
def _get_K_matrix():
    """Return 9×9 symmetric K matrix (post-ρ-fix, 9-sector resolution).

    Diagonal = self-coupling (‖P_i ρ(g) P_i‖ max over g).
    Off-diagonal < TOL_K → zero.
    """
    K = np.zeros((9, 9))
    # Diagonal (self-coupling)
    diag_vals = {'S1': 4.90, 'S2': 0.52, 'S3': 4.00, 'S4': 5.66,
                 'S5': 0.33, 'S6': 8.19, 'S7': 9.67, 'S8': 2.83, 'S9': 5.66}
    for i, s in enumerate(SECTOR_NAMES):
        K[i, i] = diag_vals[s]

    # Direct edges (Type I unless noted)
    edges = [
        (1, 4, 0.47, 'I'),   # S2-S5
        (1, 5, 0.58, 'I'),   # S2-S6
        (2, 5, 2.55, 'I'),   # S3-S6
        (2, 6, 3.61, 'I'),   # S3-S7
        (3, 5, 3.46, 'I'),   # S4-S6
        (3, 8, 1.00, 'I'),   # S4-S9
        (4, 5, 0.82, 'I'),   # S5-S6
        (5, 6, 3.61, 'I'),   # S6-S7
        (6, 8, 4.06, 'I'),   # S7-S9
        (7, 8, 2.83, 'II'),  # S8-S9 (Type II: CP permutation channel)
    ]
    for i, j, val, _ in edges:
        K[i, j] = val
        K[j, i] = val
    return K

K_MATRIX = _get_K_matrix()
BLOCKS = ['cp', 'ep', 'co', 'eo']
# Block commutator norms ‖[QT⁰, QT¹]‖_b (post-ρ-fix)
BLOCK_COMM_NORM = {'cp': 0.0, 'ep': 2.74, 'co': 0.61, 'eo': 0.79}

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')
os.makedirs(FIG_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 1: K Matrix Heatmap
# ═══════════════════════════════════════════════════════════════════════════════

def plot_fig1_k_heatmap(output_path):
    """9×9 K_αβ heatmap. Type I edges in circle markers, Type II (S8↔S9) in
    purple border. Zero entries in light gray. Diagonal in dark gray.
    """
    fig, ax = plt.subplots(1, 1, figsize=(9.5, 8))
    fig.patch.set_facecolor(CANVAS['white'])
    ax.set_facecolor(CANVAS['white'])

    n = 9
    labels = SECTOR_NAMES
    K = K_MATRIX

    cmap = plt.cm.YlOrRd
    norm = plt.Normalize(vmin=0, vmax=np.max(K) * 1.05)
    im = ax.imshow(K, cmap=cmap, norm=norm, aspect='equal')

    # Annotate each cell
    for i in range(n):
        for j in range(n):
            val = K[i, j]
            if i == j:
                txt = f'{val:.2f}'
                clr = '#444444'
                wt, fs = 'normal', 8
            elif val < TOL_K:
                txt = '0'
                clr = '#cccccc'
                wt, fs = 'normal', 8
            else:
                txt = f'{val:.2f}'
                clr = 'white' if val > np.max(K) * 0.4 else '#333333'
                wt, fs = 'bold', 9
            ax.text(j, i, txt, ha='center', va='center', fontsize=fs,
                    color=clr, fontweight=wt)

    # CP channel S8↔S9 — purple border
    for (r, c) in [(7, 8), (8, 7)]:
        rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                             edgecolor=SEMANTIC['curvature'], linewidth=3.0,
                             linestyle='-', zorder=10)
        ax.add_patch(rect)

    # Type I edges — circle markers
    type1_pairs = [(1,4),(1,5),(2,5),(2,6),(3,5),(3,8),(4,5),(5,6),(6,8)]
    for (r, c) in type1_pairs:
        ax.plot(c, r, 'o', markersize=4.5, markerfacecolor='none',
                markeredgecolor='#2c3e50', markeredgewidth=1.0, alpha=0.55)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold')
    # Simpler axis labels
    ax.set_xlabel(r'$\beta$', fontsize=12, fontweight='bold', labelpad=4)
    ax.set_ylabel(r'$\alpha$', fontsize=12, fontweight='bold', labelpad=4)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()

    # Colorbar — compact
    cbar = plt.colorbar(im, ax=ax, shrink=0.82, pad=0.02)
    cbar.set_label(r'$K_{\alpha\beta}$', fontsize=10, fontweight='bold')

    # Title — single line
    ax.set_title(r'Transport Matrix $K_{\alpha\beta}$ (9 sectors)',
                 fontsize=13, fontweight='bold', pad=18)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='none', edgecolor='#2c3e50', linewidth=1.5,
                       label='Noncommutative (9 edges)'),
        mpatches.Patch(facecolor='none', edgecolor=SEMANTIC['curvature'], linewidth=3,
                       label='Comm. permutation (S8↔S9)'),
        mpatches.Patch(facecolor='#f0f0f0', edgecolor='#cccccc', linewidth=1,
                       label='Disconnected'),
    ]
    ax.legend(handles=legend_elements, loc='upper center',
              bbox_to_anchor=(0.5, -0.12), fontsize=8,
              framealpha=0.9, ncol=3, borderpad=0.6, handlelength=1.5)

    plt.tight_layout(pad=0.8)
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"Fig 1 (K heatmap) → {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 2: Transport Graph
# ═══════════════════════════════════════════════════════════════════════════════

def plot_fig2_transport_skeleton(output_path):
    """Transport Skeleton — pure connectivity geometry.
    S6 as dominant hub (center, huge diamond, deep red).
    Noncommutative core cluster: S2,S3,S4,S5,S7,S9 — connected via red edges.
    S8–S9 detached pair on right — curved purple arc (separate mechanism).
    S1 isolated gray dot top-left (invariant sector).
    NO edge weights, NO algebraic detail. Pure topology.
    """
    fig, ax = plt.subplots(1, 1, figsize=(13, 10))
    fig.patch.set_facecolor(CANVAS['white'])
    ax.set_facecolor(CANVAS['white'])
    ax.set_xlim(-7, 7)
    ax.set_ylim(-6.5, 7)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── Node positions — force-directed feel with fixed anchors ──
    pos = {
        'S6': (0.0, 0.0),        # CENTER — primary hub
        # Noncommutative core — roughly radial around S6
        'S7': (0.6, -1.8),       # secondary hub, close to center
        'S3': (-2.8, -1.5),      # left side of core
        'S4': (2.5, -2.0),       # right side of core
        'S2': (-3.0, 1.0),       # upper left
        'S5': (-1.8, 2.5),       # upper
        'S9': (2.8, 0.0),        # middle right — bridge to S8
        # CP detached pair — right side, visually separate
        'S8': (5.2, 1.5),
        # S1 isolated — far top-left
        'S1': (-5.5, 5.0),
    }

    # ── Edges — Type I (red, straight) + Type II (purple, curved arc) ──
    edges_type1 = [
        ('S2', 'S5'), ('S2', 'S6'), ('S3', 'S6'), ('S3', 'S7'),
        ('S4', 'S6'), ('S4', 'S9'), ('S5', 'S6'), ('S6', 'S7'), ('S7', 'S9'),
    ]
    # Draw Type I edges — center-outward alpha gradient via layering
    for si, sj in edges_type1:
        xi, yi = pos[si]
        xj, yj = pos[sj]
        # Compute distance from center for alpha: closer to center = more opaque
        dist_from_center = min(np.sqrt(xi**2 + yi**2), np.sqrt(xj**2 + yj**2))
        alpha = max(0.35, 1.0 - dist_from_center / 6.0)
        ax.plot([xi, xj], [yi, yj], linestyle='-', color=SEMANTIC['noncommutative'],
                linewidth=2.0, alpha=alpha, zorder=1, solid_capstyle='round')

    # Type II: S8–S9 — curved arc, visually distinct
    x8, y8 = pos['S8']
    x9, y9 = pos['S9']
    # Draw a curved arc between S9 and S8
    mid_x, mid_y = (x8 + x9) / 2, (y8 + y9) / 2
    # Control point offset perpendicular to the line
    dx, dy = x8 - x9, y8 - y9
    cp_x = mid_x - dy * 0.5
    cp_y = mid_y + dx * 0.5
    # Quadratic bezier via parametric
    from matplotlib.patches import FancyArrowPatch
    import matplotlib.path as mpath
    Path = mpath.Path
    verts = [(x9, y9), (cp_x, cp_y), (x8, y8)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = mpath.Path(verts, codes)
    patch = FancyArrowPatch(path=path, color=SEMANTIC['curvature'],
                            linewidth=2.5, alpha=0.75, zorder=1,
                            arrowstyle='-', linestyle=(0, (5, 3)))
    ax.add_patch(patch)

    # ── Subtle background for CP detached pair ──
    cp_center_x = (pos['S8'][0] + pos['S9'][0]) / 2
    cp_center_y = (pos['S8'][1] + pos['S9'][1]) / 2
    cp_bg = FancyBboxPatch((cp_center_x - 2.2, cp_center_y - 1.4), 4.4, 2.8,
                           boxstyle="round,pad=0.3",
                           facecolor=SEMANTIC['curvature'], edgecolor='none',
                           linewidth=0, alpha=0.05, zorder=0)
    ax.add_patch(cp_bg)
    ax.text(cp_center_x, cp_center_y + 1.2, 'CP Channel',
            fontsize=9, color=SEMANTIC['curvature'], ha='center', va='center',
            fontweight='bold', style='italic', alpha=0.7)

    # ── Draw nodes ──
    for sname in SECTOR_NAMES:
        x, y = pos[sname]
        hub_type = SECTOR_HUB[sname]
        color = SECTOR_COLORS[sname]

        if hub_type == 'primary':
            # S6: HUGE diamond, dominant presence
            sz = 520
            marker = 'D'
            edgecolor = '#8b0000'
            lw = 3.0
        elif hub_type == 'secondary':
            sz = 220
            marker = 's'
            edgecolor = SEMANTIC['hub_secondary']
            lw = 2.0
        elif hub_type == 'isolated':
            sz = 100
            marker = 'o'
            edgecolor = '#cccccc'
            lw = 1.5
        elif sname == 'S8':
            # S8 — distinct from core, part of CP pair
            sz = 160
            marker = 'o'
            edgecolor = SEMANTIC['curvature']
            lw = 2.0
        elif sname == 'S9':
            # S9 — bridge node, connects core to CP
            sz = 180
            marker = 's'
            edgecolor = '#666666'
            lw = 1.8
        else:
            sz = 160
            marker = 'o'
            edgecolor = '#555555'
            lw = 1.5

        ax.scatter(x, y, s=sz, c=color, marker=marker, edgecolors=edgecolor,
                   linewidth=lw, zorder=5, alpha=0.9)

        # Label — sector name only, no metadata
        label_offset_y = -0.55 if sname in ('S6', 'S5') else 0.45
        label_offset_y = -0.55 if sname == 'S7' else label_offset_y
        ax.text(x, y + label_offset_y, sname, fontsize=9,
                ha='center', va='center', color='white', fontweight='bold', zorder=6)

    # ── Minimal annotations ──
    # S1 — invariant sector
    ax.annotate('invariant sector',
                xy=pos['S1'], xytext=(-6.8, 6.2),
                fontsize=9, ha='center', color='#aaaaaa',
                fontweight='bold', style='italic',
                arrowprops=dict(arrowstyle='->', color='#cccccc', lw=1.2))

    # S6 — visual dominance alone signals hub role; no text annotation needed

    # ── Title ──
    ax.set_title('Transport Skeleton\n'
                 'Type I: noncommutative core (red)    |    '
                 'Type II: commutative permutation channel (purple)',
                 fontsize=13, fontweight='bold', pad=12, linespacing=1.4)

    # ── Legend — minimal ──
    legend_elements = [
        plt.Line2D([0], [0], color=SEMANTIC['noncommutative'], linewidth=2.5,
                   label='Type I: noncommutative mixing'),
        plt.Line2D([0], [0], color=SEMANTIC['curvature'], linewidth=2.5,
                   linestyle=(0, (5, 3)), label='Type II: CP permutation'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=SECTOR_COLORS['S6'],
                   markersize=12, markeredgecolor='#8b0000', markeredgewidth=2,
                   label='Primary hub'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=8.5,
              framealpha=0.9, borderpad=0.6, handlelength=2.0)

    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"Fig 2 (Transport Skeleton) → {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 3: Supp_nc Overlap — Binary + Continuous Strength
# ═══════════════════════════════════════════════════════════════════════════════

def plot_fig3_supp_nc_overlap(output_path):
    """Dual-layer display:
    Primary (color): Supp_nc presence/absence per sector per block
    Secondary (text): per-block commutator norm ‖[QT⁰, QT¹]‖_b
    Shows that overlap is binary BUT noncommutativity is graded.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.patch.set_facecolor(CANVAS['white'])
    ax.set_facecolor(CANVAS['white'])

    n_sectors = 9
    n_blocks = 4
    blocks = BLOCKS
    sector_names = SECTOR_NAMES

    # Build the overlap matrix: 1 if block in Supp_nc, 0 otherwise
    overlap = np.zeros((n_sectors, n_blocks))
    for i, s in enumerate(sector_names):
        for j, b in enumerate(blocks):
            if b in SECTOR_SUPP_NC[s]:
                overlap[i, j] = 1

    # Block commutator norms for header annotation
    block_norms = [BLOCK_COMM_NORM[b] for b in blocks]

    # Draw the grid
    for i in range(n_sectors):
        for j in range(n_blocks):
            b = blocks[j]
            if overlap[i, j]:
                # Noncommutative block — color by block identity
                facecolor = BLOCK_COLORS[b]
                alpha = 0.7
                txt_color = 'white'
                txt = f'{block_norms[j]:.2f}'
                fontweight = 'bold'
            else:
                # No Supp_nc — light gray
                facecolor = '#f0f0f0'
                alpha = 0.5
                txt_color = '#cccccc'
                txt = '·'
                fontweight = 'normal'

            rect = plt.Rectangle((j - 0.45, i - 0.45), 0.9, 0.9,
                                 facecolor=facecolor, edgecolor='white',
                                 linewidth=1.5, alpha=alpha)
            ax.add_patch(rect)
            ax.text(j, i, txt, ha='center', va='center', fontsize=11,
                    color=txt_color, fontweight=fontweight)

    # Also annotate sector Supp_nc cardinality on the right
    for i, s in enumerate(sector_names):
        nc_size = len(SECTOR_SUPP_NC[s])
        hub_type = SECTOR_HUB[s]
        if hub_type == 'primary':
            marker = ' ★'
            mcolor = SEMANTIC['hub_primary']
        elif hub_type == 'secondary':
            marker = ' ☆'
            mcolor = SEMANTIC['hub_secondary']
        elif hub_type == 'isolated':
            marker = ' ⊗'
            mcolor = SEMANTIC['forbidden']
        else:
            marker = ''
            mcolor = '#555555'
        ax.text(n_blocks + 0.3, i, f'|Supp_nc| = {nc_size}{marker}',
                ha='left', va='center', fontsize=9, color=mcolor,
                fontweight='bold')

    # Block header — compact
    for j, b in enumerate(blocks):
        norm_val = block_norms[j]
        if norm_val == 0:
            status = 'comm.'
            header_color = SEMANTIC['commutative']
        elif norm_val > 2:
            status = 'dominant'
            header_color = SEMANTIC['noncommutative']
        else:
            status = 'sideband'
            header_color = SEMANTIC['forbidden']
        ax.text(j, -0.7, f'{b.upper()}\n‖[QT]‖={norm_val:.2f}\n({status})',
                ha='center', va='top', fontsize=8, fontweight='bold',
                color=header_color, linespacing=1.1)

    # Sector labels — cleaner
    for i, s in enumerate(sector_names):
        ax.text(-0.4, i, s, ha='right', va='center',
                fontsize=9, color='#333333', fontweight='bold')

    ax.set_xlim(-0.7, n_blocks + 1.6)
    ax.set_ylim(n_sectors - 0.3, -1.0)
    ax.set_aspect('equal')
    ax.axis('off')

    # Title — single line
    ax.set_title('Noncommutative Support (colored = Supp_nc present, number = ‖[QT⁰,QT¹]‖_b)',
                 fontsize=12, fontweight='bold', pad=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"Fig 3 (Supp_nc Overlap) → {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 4: Refinement Obstruction — The Philosophical Climax
# ═══════════════════════════════════════════════════════════════════════════════

def plot_fig4_refinement_obstruction(output_path):
    """Refinement obstruction: the commutative Center resolves to 9 sectors.
    Further refinement requires operators outside the Center — M₂ noncommutativity
    obstructs simultaneous diagonalization. The M₂ components are the minimal
    obstruction units.

    Left: Center diagonalization → 9 sectors (achieved).
    Right: attempt to split M₂-coupled sectors → appears obstructed.
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 8))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS['white'])

    # ── Title ──
    ax.text(7.5, 8.1, 'Refinement Obstruction',
            fontsize=16, fontweight='bold', color='#222222', ha='center', va='center')
    ax.text(7.5, 7.65, 'M₂ overlap obstructs further commutative refinement',
            fontsize=10, color='#777777', ha='center', va='center', style='italic')

    # ── LEFT SIDE: Commutative refinement chain ──
    left_cx = 3.5
    left_w = 4.8
    box_h = 1.1

    steps = [
        (r'$A_{18}$', '6 spectral layers', 6.3),
        (r'$A_{18}$ + QT$_{\rm all}$', 'finer eigenspaces', 5.0),
        (r'Center$\{A, \mathrm{QT}, \mathrm{HT}\}$', 'maximal abelian resolution', 3.7),
    ]

    for idx, (label, desc, y) in enumerate(steps):
        styled_box(ax, left_cx - left_w/2, y, left_w, box_h, box_type='layer',
                   facecolor='white', edgecolor=SEMANTIC['commutative'])
        ax.text(left_cx, y + box_h - 0.3, label,
                fontsize=12, fontweight='bold', color='#222222', ha='center', va='center')
        ax.text(left_cx, y + 0.28, desc,
                fontsize=8.5, color='#555555', ha='center', va='center')
        if idx < 2:
            ax.annotate('', xy=(left_cx, y - 0.08),
                       xytext=(left_cx, y + box_h + 0.08),
                       arrowprops=dict(arrowstyle='->', color=SEMANTIC['commutative'], lw=2.2))

    # Final: 9 sectors
    result_y = 2.3
    styled_box(ax, left_cx - left_w/2, result_y, left_w, box_h,
               box_type='sector', facecolor='#f0f4ff', edgecolor=SEMANTIC['commutative'])
    ax.text(left_cx, result_y + box_h/2,
            '9 Primitive Sectors',
            fontsize=12, fontweight='bold', color=SEMANTIC['commutative'],
            ha='center', va='center')
    ax.annotate('', xy=(left_cx, result_y + box_h),
               xytext=(left_cx, 3.62),
               arrowprops=dict(arrowstyle='->', color=SEMANTIC['commutative'], lw=2.2))

    # Left side label
    ax.text(left_cx, 7.1, 'COMMUTATIVE CENTER',
            fontsize=11, fontweight='bold', color=SEMANTIC['commutative'],
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=SEMANTIC['commutative'], linewidth=1.2))

    # ── RIGHT SIDE: Obstruction ──
    right_cx = 10.8
    right_w = 5.5

    # M₂ components top
    m2_y = 6.5
    ax.text(right_cx, 7.1, 'M₂ COMPONENTS IN A_EP',
            fontsize=10, fontweight='bold', color=SEMANTIC['noncommutative'],
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                      edgecolor=SEMANTIC['noncommutative'], linewidth=1.2))

    for mi, mlabel in enumerate(['M₂⁽¹⁾', 'M₂⁽²⁾', 'M₂⁽³⁾', 'M₁']):
        mx = right_cx - 1.9 + mi * 1.25
        is_active = mi < 3
        fc = SEMANTIC['noncommutative'] if is_active else SEMANTIC['forbidden']
        ec = SEMANTIC['noncommutative'] if is_active else '#cccccc'
        alpha = 0.25 if is_active else 0.10
        rect = FancyBboxPatch((mx, m2_y), 1.05, 0.48, boxstyle="round,pad=0.04",
                              facecolor=fc, edgecolor=ec, linewidth=1.2, alpha=alpha)
        ax.add_patch(rect)
        ax.text(mx + 0.525, m2_y + 0.24, mlabel, fontsize=8, ha='center',
                va='center', fontweight='bold',
                color='#444444' if is_active else '#aaaaaa')

    ax.text(right_cx, m2_y + 0.62,
            '$A_{\\rm EP} \\cong M_2(\\mathbb{C})^4 \\oplus M_1(\\mathbb{C})^4$',
            fontsize=8.5, color='#444444', ha='center', va='bottom', fontweight='bold')

    # Cross-over arrow
    ax.annotate('', xy=(right_cx, 5.2),
               xytext=(left_cx + left_w/2 + 0.3, 2.9),
               arrowprops=dict(arrowstyle='->', color='#999999', lw=1.8,
                              connectionstyle='arc3,rad=0.35'))
    ax.text(right_cx - 1.2, 4.3, 'resolve\nM₂?', fontsize=8, color='#999999',
            ha='center', va='center', style='italic')

    # Attempt box
    styled_box(ax, right_cx - right_w/2, 3.6, right_w, 1.3, box_type='sector',
               facecolor='#fff8f8', edgecolor=SEMANTIC['noncommutative'])
    ax.text(right_cx, 4.45,
            'All observed refinement attempts\n'
            'require operators outside the commutative center',
            fontsize=9.5, color=SEMANTIC['noncommutative'], ha='center', va='center',
            fontweight='bold', linespacing=1.3)

    ax.annotate('', xy=(right_cx, 3.52),
               xytext=(right_cx, 3.72),
               arrowprops=dict(arrowstyle='->', color=SEMANTIC['noncommutative'], lw=2.2))

    # Obstruction wall
    wall_y = 2.0
    wall = FancyBboxPatch((right_cx - right_w/2 + 0.4, wall_y), right_w - 0.8, 1.2,
                          boxstyle="round,pad=0.12",
                          facecolor='#fff0f0', edgecolor=SEMANTIC['noncommutative'],
                          linewidth=3.0, linestyle='-')
    ax.add_patch(wall)
    ax.text(right_cx, wall_y + 0.6,
            'M₂ OVERLAP OBSTRUCTION\n'
            'no further commutative refinement found',
            fontsize=11, fontweight='bold', color=SEMANTIC['noncommutative'],
            ha='center', va='center', linespacing=1.3)

    # One-line explanation — keeps figure light
    ax.text(right_cx, wall_y - 0.1,
            'Non-central operators in $A_{\\rm EP}$ fail to commute with the Center',
            fontsize=8.5, color='#666666', ha='center', va='top', style='italic')

    # Bottom
    ax.text(7.5, 0.3, 'Center diagonalization: 9 sectors achieved     |     '
            'M₂-coupled splitting: appears obstructed',
            fontsize=10, fontweight='bold', color='#333333', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#fafafa',
                      edgecolor='#cccccc', linewidth=1.0))

    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"Fig 4 (Refinement Obstruction) → {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 5: M₂ → Transport Chain
# ═══════════════════════════════════════════════════════════════════════════════

def plot_fig5_m2_chain(output_path):
    """Flow schematic: A_EP → Supp_nc → K → Transport Graph.
    Shows the structural chain from algebraic origin to transport topology.
    Observations B and C as annotations between nodes.
    Bottom: Type I/II taxonomy mini-table.
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 6.5))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor(CANVAS['white'])

    # ── Title ──
    ax.text(7.5, 6.2, 'From M₂ Algebra to Transport Topology',
            fontsize=16, fontweight='bold', color='#222222', ha='center', va='center')
    ax.text(7.5, 5.8, 'Algebraic origin → structural invariant → transport criterion → topology',
            fontsize=9, color='#777777', ha='center', va='center', style='italic')

    # ── Four nodes ──
    node_w = 2.8
    node_h = 2.1
    node_y = 2.8
    x_positions = [0.3, 4.0, 7.7, 11.4]
    titles = [
        'M₂ OBSTRUCTION',
        'NONCOMMUTATIVE\nSUPPORT',
        'TRANSPORT\nCRITERION',
        'TRANSPORT\nTOPOLOGY',
    ]
    subtitles = [
        '$A_{\\rm EP} \\cong M_2^4 \\oplus M_1^4$\n3 active M₂',
        'Supp_nc(α)\n{ep, eo, co} blocks',
        'Type I: Supp_nc shared\nType II: CP permutation',
        'S6 hub (deg 5)\nS1 isolated',
    ]
    colors = [
        SECTOR_COLORS['S6'],
        SEMANTIC['noncommutative'],
        SEMANTIC['curvature'],
        SEMANTIC['hub_primary'],
    ]

    for idx, (x, title, subtitle, color) in enumerate(
        zip(x_positions, titles, subtitles, colors)):
        styled_box(ax, x, node_y, node_w, node_h, box_type='hub' if idx == 3 else 'sector',
                   facecolor='white', edgecolor=color)

        # Title bar
        bar = FancyBboxPatch((x + 0.06, node_y + 0.08), 0.06, node_h - 0.16,
                             boxstyle="round,pad=0.01", facecolor=color, edgecolor='none')
        ax.add_patch(bar)

        ax.text(x + 0.45, node_y + node_h - 0.3, title,
                fontsize=9, fontweight='bold', color='#222222', ha='left', va='top',
                linespacing=1.1)
        ax.text(x + 0.45, node_y + 0.3, subtitle,
                fontsize=8, color='#555555', ha='left', va='bottom', linespacing=1.3)

    # ── Annotations between nodes ──
    ax.annotate('Observation B\nHub Necessity\nM₂ overlap →\nunique hub S6',
                xy=(x_positions[1] + node_w/2, node_y + node_h + 0.25),
                fontsize=7.5, ha='center', va='bottom', color=SEMANTIC['hub_primary'],
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#fff8f8',
                          edgecolor=SEMANTIC['hub_primary'], linewidth=0.8))

    ax.annotate('Observation C\nRefinement Obstruction\nM₂ blocks further\ncommutative splitting',
                xy=(x_positions[2] + node_w/2, node_y + node_h + 0.25),
                fontsize=7.5, ha='center', va='bottom', color=SEMANTIC['noncommutative'],
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#fff5f5',
                          edgecolor=SEMANTIC['noncommutative'], linewidth=0.8))

    # ── Arrows ──
    for idx in range(3):
        x_from = x_positions[idx] + node_w
        x_to = x_positions[idx + 1]
        y_center = node_y + node_h / 2
        ax.annotate('', xy=(x_to + 0.05, y_center),
                   xytext=(x_from + 0.05, y_center),
                   arrowprops=dict(arrowstyle='->', color=colors[idx + 1],
                                  lw=2.8, connectionstyle='arc3,rad=0'))
        arrow_labels = ['creates', 'determines', 'shapes']
        ax.text((x_from + x_to) / 2 + 0.05, y_center + 0.28,
                arrow_labels[idx], fontsize=7.5, color=colors[idx + 1],
                ha='center', va='center', fontweight='bold', style='italic')

    # ── Bottom: Type I/II mini-table ──
    table_y = 1.2
    ax.text(7.5, table_y + 0.35, 'Two Transport Mechanisms',
            fontsize=9, fontweight='bold', color='#333333', ha='center', va='center')

    col_x = [1.8, 5.8, 9.0, 12.2]
    col_w = [3.5, 2.6, 2.6, 2.5]
    headers = ['Type', 'Origin', 'Criterion', 'Example']
    row_data = [
        ['Type I: Noncommutative', 'M₂ in A_EP', 'Supp_nc shared', 'S3↔S6, S4↔S6 (9 edges)'],
        ['Type II: Commutative perm', 'CP adjacency', 'CP block + ρ(g)≠id', 'S8↔S9 (1 edge)'],
    ]

    for j, hdr in enumerate(headers):
        ax.text(col_x[j] + col_w[j]/2, table_y, hdr, fontsize=7.5,
                fontweight='bold', color='#555555', ha='center', va='center')

    for ri, row in enumerate(row_data):
        row_y = table_y - 0.35 - ri * 0.45
        for cj, cell in enumerate(row):
            ec = SEMANTIC['noncommutative'] if ri == 0 else SEMANTIC['curvature']
            rect = FancyBboxPatch((col_x[cj], row_y - 0.18), col_w[cj], 0.38,
                                  boxstyle="round,pad=0.03",
                                  facecolor='white', edgecolor=ec, linewidth=0.8,
                                  alpha=0.5)
            ax.add_patch(rect)
            ax.text(col_x[cj] + col_w[cj]/2, row_y, cell, fontsize=7,
                    color='#333333', ha='center', va='center')

    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.replace('.png', '.pdf'), bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"Fig 5 (M₂ → Transport Chain) → {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 70)
    print("Paper II Figures: Transport Topology from Noncommutative Support")
    print("=" * 70)
    print("Post-ρ-fix (2026-05-13), 9-sector resolution, 5 figures.")
    print("Visual philosophy: transport network geometry, overlap topology.")
    print("Entirely static — no dynamics, no Lie closure, no κ_d hierarchy.")
    print()

    # Fig 1: K Matrix Heatmap
    print("── Fig 1: K Matrix Heatmap ──")
    plot_fig1_k_heatmap(os.path.join(FIG_DIR, 'paper2_fig1_k_heatmap.png'))

    # Fig 2: Transport Skeleton
    print("\n── Fig 2: Transport Skeleton ──")
    plot_fig2_transport_skeleton(os.path.join(FIG_DIR, 'paper2_fig2_transport_skeleton.png'))

    # Fig 3: Supp_nc Overlap
    print("\n── Fig 3: Supp_nc Overlap ──")
    plot_fig3_supp_nc_overlap(os.path.join(FIG_DIR, 'paper2_fig3_supp_nc_overlap.png'))

    # Fig 4: Refinement Obstruction
    print("\n── Fig 4: Refinement Obstruction ──")
    plot_fig4_refinement_obstruction(os.path.join(FIG_DIR, 'paper2_fig4_refinement_obstruction.png'))

    # Fig 5: Structural Chain
    print("\n── Fig 5: Structural Chain ──")
    plot_fig5_m2_chain(os.path.join(FIG_DIR, 'paper2_fig5_m2_chain.png'))

    print(f"\nAll 5 figures saved to {FIG_DIR}/")
    print("Done.")
