"""
Paper III Figures: Lie Accessibility and the Discrete/Continuous Split

Visual language: obstruction geometry, accessibility hierarchy.
Theme: "continuous dynamics cannot cross this wall" — frozen, blocked,
inaccessible, tangent confinement, curvature emergence, detour, bypass.

Generates six publication-quality figures:
  Fig 0: Accessibility Hierarchy Collapse — Lie World vs Compositional World
  Fig 1: Four-Level Accessibility Hierarchy (collapse + resurrection)
  Fig 2: Lie Barrier / Frozen Accessibility (wall diagram)
  Fig 3: Curvature Emergence (geometric mechanism)
  Fig 4: S₃ Minimal Prototype (9-dim, T7 without curvature)
  Fig 5: Hybrid Bridge Topology (block-colored, cross-block via hybrids)

Run: python test/_exp_paper3_figures.py
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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Wedge
from matplotlib.patches import ConnectionPatch
import numpy as np
import os

sys.path.insert(0, '.')
from rime.base import DATA_DIR
from rime.trilogy_style import (
    apply_style,
    PAPER_COLORS, BLOCK_COLORS, SECTOR_COLORS, LAYER_COLORS,
    SEMANTIC,
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')

# ── Paper III visual identity ────────────────────────────────────────────
C_BG      = '#0d1117'
C_P1      = PAPER_COLORS['I']        # #2980b9 blue
C_P2      = PAPER_COLORS['II']       # #8e44ad purple
C_P3      = PAPER_COLORS['III']      # #e67e22 orange
C_LIE     = '#5b6abf'   # continuous / Lie  — cool blue-gray
C_FROZEN  = '#95a5a6'   # frozen / blocked  — gray
C_WALL    = '#6c5b7b'   # Lie barrier wall  — muted purple
C_ESCAPE  = '#e74c3c'   # composition escape — red
C_CURV    = '#8e44ad'   # curvature emergence — purple
C_HYBRID  = '#f39c12'   # hybrid bridge — amber
C_TEXT    = '#ffffff'
C_SUBTEXT = '#aaaaaa'
C_MUTED   = '#777777'

# Block colors
C_CP = BLOCK_COLORS['cp']   # #5b6abf
C_EP = BLOCK_COLORS['ep']   # #e74c3c
C_CO = BLOCK_COLORS['co']   # #f39c12
C_EO = BLOCK_COLORS['eo']   # #16a085


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 0: Accessibility Hierarchy Collapse — Lie World vs Compositional World
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig0_pipeline(output_path):
    """Three-panel narrative diagram: Lie world (left, cold, arrows hit wall)
    → spectral decomposition (center, hybrid cracks in wall) → compositional world
    (right, warm, bypass through hybrid bridge, T7).

    Visual story: Continuous dynamics freezes at the block boundary;
    composition bypasses it.
    """
    fig = plt.figure(figsize=(22, 10))
    fig.patch.set_facecolor(C_BG)

    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 0.7, 1.0], wspace=0.06,
                          left=0.02, right=0.98, top=0.87, bottom=0.2)

    ax_l = fig.add_subplot(gs[0])
    ax_c = fig.add_subplot(gs[1])
    ax_r = fig.add_subplot(gs[2])

    for ax in [ax_l, ax_c, ax_r]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_facecolor(C_BG)

    # ── Color palette ──
    C_BLOCK_A  = '#3a5070'    # cold steel blue (block A, left of wall)
    C_BLOCK_B  = '#2d3f5e'    # darker cold blue (block B, right of wall)
    C_WALL     = '#8899aa'    # barrier wall
    C_WALL_COLD = '#6b7b8e'   # wall in Lie panel (dark, solid)
    C_WALL_WARM = '#8a7a7e'   # wall in composition panel (faded)
    C_LIE_ARR  = '#6b8bb0'    # Lie arrows — cold blue
    C_COMP_ARR = '#e74c3c'    # composition arrow — red
    C_COMP_GLO = '#ff5544'    # composition glow
    C_HYBRID_NODE = '#f39c12' # hybrid sector — amber
    C_PURE_A   = '#5b8cb8'    # pure sector in block A
    C_PURE_B   = '#4a7a9e'    # pure sector in block B
    C_STOP     = '#95a5a6'    # × marks
    C_TEXT2    = '#e0e0e0'

    # ── Block geometry (BLOCKS SIDE-BY-SIDE, VERTICAL WALL BETWEEN) ──
    block_bot   = 0.8
    block_top   = 9.2
    block_left  = 0.5
    wall_left   = 3.8
    wall_right  = 6.2
    block_right = 9.5

    def draw_block(ax, x0, x1, y0, y1, color, edgecolor, label, label_x, label_y, alpha=0.55):
        """Draw a rounded block rectangle."""
        rect = FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                              boxstyle="round,pad=0.25",
                              facecolor=color, edgecolor=edgecolor,
                              linewidth=1.5, alpha=alpha)
        ax.add_patch(rect)
        ax.text(label_x, label_y, label, fontsize=11, fontweight='bold',
                color=C_TEXT2, ha='center', va='center')

    def draw_wall(ax, x0, x1, y0, y1, color, edgecolor, alpha=0.7, lw=1.8):
        """Draw the vertical wall between blocks."""
        wall = FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                              boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor=edgecolor,
                              linewidth=lw, alpha=alpha)
        ax.add_patch(wall)

    def draw_curvature_arrow(ax, cx, cy, radius, angle, color, lw=2.5):
        """Curved arrow showing commutator mixing within a block."""
        arc = Arc((cx, cy), 2*radius, 2*radius, angle=angle,
                  theta1=25, theta2=335, color=color, lw=lw, alpha=0.7)
        ax.add_patch(arc)
        theta_end = np.radians(angle + 335)
        axh_x = cx + radius * np.cos(theta_end)
        axh_y = cy + radius * np.sin(theta_end)
        ax.plot(axh_x, axh_y, '>', color=color, markersize=7, alpha=0.7)

    # ═══════════════════════════════════════════════════════════
    # LEFT PANEL: Lie / Continuous World (cold, frozen)
    # ═══════════════════════════════════════════════════════════

    ax_l.text(5, 9.8, 'Lie / Continuous World', fontsize=14, fontweight='bold',
              color=C_LIE, ha='center', va='center')
    ax_l.text(5, 9.3,
              r'infinitesimal  $\cdot$  tangent-generated  $\cdot$  block-preserving',
              fontsize=8, color=C_MUTED, ha='center', va='center')

    draw_block(ax_l, block_left, wall_left, block_bot, block_top,
               C_BLOCK_A, '#5a7a9a', r'$V_A$', 2.15, 8.5)
    draw_block(ax_l, wall_right, block_right, block_bot, block_top,
               C_BLOCK_B, '#4a6a8a', r'$V_B$', 7.85, 8.5)
    draw_wall(ax_l, wall_left, wall_right, block_bot, block_top,
              C_WALL_COLD, '#99aabb', alpha=0.75, lw=2.0)
    ax_l.text(5.0, 5.0, 'BLOCK\nBOUNDARY', fontsize=8, fontweight='bold',
              color='#1a1a2e', ha='center', va='center', rotation=90, linespacing=1.4)

    # ── Curvature arrows rotating WITHIN each block ──
    draw_curvature_arrow(ax_l, 2.2, 6.8, 0.7, 20, C_LIE_ARR)
    draw_curvature_arrow(ax_l, 2.8, 3.2, 0.55, 160, C_LIE_ARR)
    draw_curvature_arrow(ax_l, 7.8, 7.2, 0.6, 340, C_LIE_ARR)
    draw_curvature_arrow(ax_l, 7.2, 2.8, 0.65, 200, C_LIE_ARR)

    ax_l.text(2.2, 7.9, r'$[A_g,A_h]$', fontsize=7.5, color=C_LIE_ARR, ha='center')
    ax_l.text(7.8, 8.1, r'$\kappa_1$', fontsize=7.5, color=C_LIE_ARR, ha='center')

    # ── Arrows hitting wall and stopping (× marks) ──
    wall_stops_left  = [(2.0, 7.5), (3.0, 5.5), (1.8, 3.0), (2.8, 1.5)]
    wall_stops_right = [(8.0, 7.0), (7.2, 4.5), (8.0, 3.5), (7.0, 1.8)]

    for x1, y1 in wall_stops_left:
        ax_l.annotate('', xy=(wall_left, y1), xytext=(x1, y1),
                      arrowprops=dict(arrowstyle='->', color=C_LIE_ARR,
                                     lw=1.6, alpha=0.45))
        ax_l.plot(wall_left, y1, 'X', color=C_STOP, markersize=7,
                  markeredgewidth=1.5, alpha=0.8)

    for x1, y1 in wall_stops_right:
        ax_l.annotate('', xy=(wall_right, y1), xytext=(x1, y1),
                      arrowprops=dict(arrowstyle='->', color=C_LIE_ARR,
                                     lw=1.6, alpha=0.45))
        ax_l.plot(wall_right, y1, 'X', color=C_STOP, markersize=7,
                  markeredgewidth=1.5, alpha=0.8)

    ax_l.text(5.0, 9.55, r'$\kappa_d(\alpha,\beta) = 0$ for ALL $d$ (cross-block)',
              fontsize=7.5, color=C_STOP, ha='center', style='italic')

    # ═══════════════════════════════════════════════════════════
    # CENTER PANEL: Spectral Decomposition — hybrid cracks
    # ═══════════════════════════════════════════════════════════

    ax_c.text(5, 9.8, 'Spectral Decomposition', fontsize=14, fontweight='bold',
              color='#c0c0d0', ha='center', va='center')
    ax_c.text(5, 9.3,
              'pure sectors  +  hybrid sectors on the boundary',
              fontsize=8, color=C_MUTED, ha='center', va='center')

    draw_block(ax_c, block_left, wall_left, block_bot, block_top,
               '#3d4058', '#6a6a8a', r'$V_A$', 2.15, 8.5, alpha=0.45)
    draw_block(ax_c, wall_right, block_right, block_bot, block_top,
               '#35384a', '#5a5a7a', r'$V_B$', 7.85, 8.5, alpha=0.45)
    draw_wall(ax_c, wall_left, wall_right, block_bot, block_top,
              '#6b7b8e', '#888899', alpha=0.4, lw=1.0)

    # ── Pure sector nodes ──
    pure_a = [(1.3, 7.8), (2.0, 6.5), (1.5, 5.2), (3.0, 7.2), (2.4, 4.0),
              (3.2, 2.8), (1.8, 2.0), (2.8, 1.2)]
    pure_b = [(8.7, 7.8), (8.0, 6.5), (8.5, 5.2), (7.0, 7.2), (7.6, 4.0),
              (6.8, 2.8), (8.2, 2.0), (7.2, 1.2)]
    for px, py in pure_a:
        ax_c.add_patch(plt.Circle((px, py), 0.18, facecolor=C_PURE_A,
                                  edgecolor='#8899bb', linewidth=0.8, alpha=0.85))
    for px, py in pure_b:
        ax_c.add_patch(plt.Circle((px, py), 0.18, facecolor=C_PURE_B,
                                  edgecolor='#7788aa', linewidth=0.8, alpha=0.85))

    # ── Hybrid sectors ON the wall — diamonds with glow ──
    hybrid_positions = [7.5, 5.0, 2.5]
    for hy in hybrid_positions:
        glow = plt.Circle((5.0, hy), 0.55, facecolor=C_HYBRID_NODE,
                          edgecolor='none', alpha=0.14)
        ax_c.add_patch(glow)
        diamond = plt.Polygon([
            (5.0, hy + 0.38), (5.5, hy), (5.0, hy - 0.38), (4.5, hy),
        ], facecolor=C_HYBRID_NODE, edgecolor='#ffcc44', linewidth=1.5, alpha=0.9)
        ax_c.add_patch(diamond)

    # Crack lines from hybrids spreading into wall
    for hy in hybrid_positions:
        ax_c.plot([5.1, 4.5, 4.1], [hy + 0.3, hy + 0.9, hy + 1.4],
                 color='#667788', lw=1.0, alpha=0.45)
        ax_c.plot([4.9, 5.5, 5.9], [hy - 0.3, hy - 0.9, hy - 1.4],
                 color='#667788', lw=1.0, alpha=0.45)

    ax_c.text(5.0, 8.8, 'hybrid sectors\n(cracks / tunneling\n/ junction states)',
              fontsize=7.5, color=C_HYBRID_NODE, ha='center', va='center',
              fontweight='bold', linespacing=1.3)
    ax_c.text(2.15, 1.0, 'pure sectors', fontsize=7, color=C_MUTED, ha='center')
    ax_c.text(7.85, 1.0, 'pure sectors', fontsize=7, color=C_MUTED, ha='center')

    # ═══════════════════════════════════════════════════════════
    # RIGHT PANEL: Compositional World (warm, bypass, T7)
    # ═══════════════════════════════════════════════════════════

    ax_r.text(5, 9.8, 'Compositional World', fontsize=14, fontweight='bold',
              color=C_ESCAPE, ha='center', va='center')
    ax_r.text(5, 9.3,
              r'finite composition  $\cdot$  projector-mediated  $\cdot$  T7',
              fontsize=8, color=C_MUTED, ha='center', va='center')

    draw_block(ax_r, block_left, wall_left, block_bot, block_top,
               '#4a3540', '#8a6a7a', r'$V_A$', 2.15, 8.5, alpha=0.5)
    draw_block(ax_r, wall_right, block_right, block_bot, block_top,
               '#3d2835', '#7a5a6a', r'$V_B$', 7.85, 8.5, alpha=0.5)
    draw_wall(ax_r, wall_left, wall_right, block_bot, block_top,
              C_WALL_WARM, '#776677', alpha=0.25, lw=0.8)

    # ── Hybrid bridge node (breach point) ──
    hy_y = 5.0
    for r_scale, a in [(1.0, 0.1), (0.6, 0.18), (0.35, 0.3)]:
        ax_r.add_patch(plt.Circle((5.0, hy_y), 0.7 * r_scale,
                                  facecolor=C_HYBRID_NODE, edgecolor='none', alpha=a))
    diamond_r = plt.Polygon([
        (5.0, hy_y + 0.45), (5.6, hy_y), (5.0, hy_y - 0.45), (4.4, hy_y),
    ], facecolor=C_HYBRID_NODE, edgecolor='#ffdd66', linewidth=2.2, alpha=0.95)
    ax_r.add_patch(diamond_r)
    ax_r.text(5.0, hy_y, r'$P_\gamma$', fontsize=8.5, fontweight='bold',
              color='#1a1a2e', ha='center', va='center')

    # ── Composition bypass path ──
    # Enter from right (block B): arrow from (8.0, 3.0) → toward hybrid
    # Exit into left (block A): arrow from hybrid → (2.5, 7.5)

    # Glow layers
    for lw, a in [(9.0, 0.1), (6.0, 0.18)]:
        ax_r.annotate('', xy=(5.5, hy_y - 0.5), xytext=(8.0, 2.5),
                      arrowprops=dict(arrowstyle='->', color=C_COMP_GLO,
                                     lw=lw, alpha=a, connectionstyle='arc3,rad=0.35'))
        ax_r.annotate('', xy=(2.5, 7.5), xytext=(4.5, hy_y + 0.5),
                      arrowprops=dict(arrowstyle='->', color=C_COMP_GLO,
                                     lw=lw, alpha=a, connectionstyle='arc3,rad=-0.35'))

    # Core arrows
    ax_r.annotate('', xy=(5.5, hy_y - 0.5), xytext=(8.0, 2.5),
                  arrowprops=dict(arrowstyle='->', color=C_COMP_ARR,
                                 lw=3.8, alpha=0.85, connectionstyle='arc3,rad=0.35'))
    ax_r.annotate('', xy=(2.5, 7.5), xytext=(4.5, hy_y + 0.5),
                  arrowprops=dict(arrowstyle='->', color=C_COMP_ARR,
                                 lw=3.8, alpha=0.85, connectionstyle='arc3,rad=-0.35'))

    # ── Labels ──
    ax_r.text(8.5, 3.5, r'$\rho(g_1)P_\gamma\rho(g_2)$',
              fontsize=9.5, fontweight='bold', color=C_COMP_ARR, ha='center')
    ax_r.text(8.5, 2.8, 'composition bypasses\nblock boundary',
              fontsize=7.5, color=C_MUTED, ha='center', linespacing=1.3)
    ax_r.text(1.8, 6.0, 'T7', fontsize=11, fontweight='bold',
              color=C_ESCAPE, ha='center', va='center')
    ax_r.text(1.8, 5.3, 'composition-\nonly morphism', fontsize=7, color=C_ESCAPE,
              ha='center', va='center', linespacing=1.3)

    # Breach marks in wall near hybrid
    ax_r.plot([4.3, 4.5, 4.7, 5.3, 5.5, 5.7],
             [hy_y + 0.8, hy_y + 0.5, hy_y + 0.7, hy_y + 0.7, hy_y + 0.5, hy_y + 0.8],
             color=C_HYBRID_NODE, lw=1.2, alpha=0.5)
    ax_r.plot([4.3, 4.5, 4.7, 5.3, 5.5, 5.7],
             [hy_y - 0.8, hy_y - 0.5, hy_y - 0.7, hy_y - 0.7, hy_y - 0.5, hy_y - 0.8],
             color=C_HYBRID_NODE, lw=1.2, alpha=0.5)

    # ═══════════════════════════════════════════════════════════
    # GLOBAL: Titles and slogan
    # ═══════════════════════════════════════════════════════════

    fig.suptitle('Accessibility Hierarchy Collapse',
                 fontsize=18, fontweight='bold', color=C_TEXT, y=0.95)

    fig.text(0.5, 0.895,
             r'$\mathrm{Lie\ Accessibility} \;\subsetneq\; \mathrm{Compositional\ Accessibility}$',
             fontsize=12, color=C_MUTED, ha='center', va='center')

    fig.text(0.5, 0.105,
             'Continuous dynamics freezes at the block boundary; composition bypasses it.',
             fontsize=14, fontweight='bold', color=C_TEXT, ha='center', va='center')

    fig.text(0.5, 0.048,
             r'(a) Lie generators $\{A_g\}$ and all commutators are block-diagonal (Lemma 1) — every arrow stops at the wall.  '
             r'(b) Hybrid sectors sit on the boundary — cracks, tunneling nodes, junction states bridging both blocks.  '
             r'(c) Finite composition $\rho(g_1) P_\gamma \rho(g_2)$ routes through a hybrid bridge — bypassing the wall (T7).',
             fontsize=7.5, color=C_MUTED, ha='center', va='center')

    for i, (ax, label) in enumerate([(ax_l, 'a'), (ax_c, 'b'), (ax_r, 'c')]):
        ax.text(0.3, 9.75, f'({label})', fontsize=12, fontweight='bold',
                color=C_TEXT, ha='left', va='center')

    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 0 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 1: Four-Level Accessibility Hierarchy
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig1_hierarchy(output_path):
    """Four-level pyramid: accessibility narrows through Lie levels,
    then composition resurrects cross-block reachability.

    Visual story: the continuous hierarchy collapses (pyramid narrows)
    → discrete path resurrects accessibility at the bottom.
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 15.5)
    ax.axis('off')
    fig.patch.set_facecolor(C_BG)

    cx = 8.0

    # ── Level definitions ──
    levels = [
        {
            'y': 11.0, 'width': 12.0, 'label': 'Level 0 — Direct Transport',
            'math': r'$K_{\alpha\beta} = \max_g \|P_\alpha \rho(g) P_\beta\|_F > 0$',
            'desc': 'Single-generator amplitude transfer',
            'block': 'Within-block only  (Lemma 0: shared Supp_nc required)',
            'color': C_LIE, 'edge_color': '#7b8fd4',
        },
        {
            'y': 8.3, 'width': 10.5, 'label': 'Level 1 — Gradient Accessibility',
            'math': r'$\kappa_0(\alpha,\beta) = \max_g \|P_\alpha A_g P_\beta\|_F > 0$',
            'desc': 'Individual Lie generator A_g = log ρ(g)',
            'block': 'Within-block only  (A_g is block-diagonal)',
            'color': '#4a6db5', 'edge_color': '#6b8fd4',
        },
        {
            'y': 5.6, 'width': 9.0, 'label': 'Level 2 — Curvature Accessibility',
            'math': r'$\kappa_1(\alpha,\beta) = \max \|P_\alpha [A_g, A_h] P_\beta\|_F > 0$',
            'desc': 'Commutator transport — Lie curvature',
            'block': 'Within-block only  (commutators are block-diagonal)',
            'color': '#3d5a9e', 'edge_color': '#5b7fc4',
        },
        {
            'y': 2.9, 'width': 7.5, 'label': 'Level ∞ — Lie Closure',
            'math': r'$\exists d \geq 0 : \kappa_d(\alpha,\beta) > 0$',
            'desc': 'All finite-depth Lie monomials',
            'block': 'Within-block only  (Lemma 1: all Lie monomials block-diagonal)',
            'color': '#2a4580', 'edge_color': '#4b6fb4',
        },
    ]

    box_h = 1.8

    # Draw Lie levels (trapezoid: narrowing downward)
    for lv in levels:
        y = lv['y']
        half_w = lv['width'] / 2
        x0 = cx - half_w

        # Filled box
        rect = FancyBboxPatch((x0, y), lv['width'], box_h,
                              boxstyle="round,pad=0.1",
                              facecolor=lv['color'], edgecolor=lv['edge_color'],
                              linewidth=1.8, alpha=0.85)
        ax.add_patch(rect)

        # Label
        ax.text(cx, y + box_h - 0.4, lv['label'],
                fontsize=12, fontweight='bold', color=C_TEXT, ha='center', va='center')
        ax.text(cx, y + box_h - 1.0, lv['math'],
                fontsize=9.5, color=C_SUBTEXT, ha='center', va='center')
        ax.text(cx, y + box_h - 1.45, lv['desc'] + '  |  ' + lv['block'],
                fontsize=8, color=C_MUTED, ha='center', va='center')

    # ── Arrow between Lie levels ──
    for i in range(len(levels) - 1):
        y_top = levels[i]['y']
        y_bot = levels[i+1]['y'] + box_h
        ax.annotate('', xy=(cx, y_bot + 0.05), xytext=(cx, y_top - 0.05),
                   arrowprops=dict(arrowstyle='->', color=C_FROZEN, lw=2.0, alpha=0.7))

    # ── WALL / Barrier line ──
    wall_y = 2.5
    ax.plot([1.5, 14.5], [wall_y, wall_y], color=C_WALL, linewidth=3, linestyle='-', alpha=0.8)
    # Wall texture (diagonal hatching suggestion)
    for wx in np.linspace(2, 14, 13):
        ax.plot([wx, wx + 0.4], [wall_y, wall_y + 0.15], color=C_WALL, linewidth=1, alpha=0.3)
    ax.text(cx, wall_y + 0.25, r'Lie Barrier  --  $\kappa_d = 0 \; \forall d$  --  Block-Preserving Wall',
            fontsize=10, color=C_WALL, ha='center', va='bottom', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG, edgecolor=C_WALL, alpha=0.8))

    # ── Composition resurrection ──
    comp_y = 0.6
    comp_w = 13.0
    rect = FancyBboxPatch((cx - comp_w/2, comp_y), comp_w, box_h,
                          boxstyle="round,pad=0.1",
                          facecolor='#3a1a1a', edgecolor=C_ESCAPE,
                          linewidth=3.0, alpha=0.9)
    ax.add_patch(rect)

    # "Resurrection" arrow from wall to composition
    ax.annotate('', xy=(cx, comp_y + box_h + 0.05), xytext=(cx, wall_y - 0.05),
               arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=3.5, alpha=0.9))

    ax.text(cx, comp_y + box_h - 0.4, 'Beyond — Composition Accessibility (T7)',
            fontsize=13, fontweight='bold', color=C_ESCAPE, ha='center', va='center')
    ax.text(cx, comp_y + box_h - 1.0,
            r'$P_\alpha \rho(g_1) P_{\gamma_1} \cdots P_{\gamma_n} \rho(g_{n+1}) P_\beta \neq 0$',
            fontsize=10, color=C_TEXT, ha='center', va='center')
    ax.text(cx, comp_y + box_h - 1.5,
            r'Discrete paths via hybrid sectors  |  Cross-block enabled  |  Composition $\supsetneq$ Lie',
            fontsize=8.5, color=C_HYBRID, ha='center', va='center', fontweight='bold')

    # ── Side annotations ──
    # Left: "accessibility narrows"
    ax.annotate('Accessibility\nnarrows',
                xy=(2.5, 9.0), fontsize=9, color=C_FROZEN, ha='center',
                style='italic')
    ax.annotate('', xy=(3.2, 7.5), xytext=(2.8, 10.5),
               arrowprops=dict(arrowstyle='->', color=C_FROZEN, lw=1.5, alpha=0.5))

    # Right: "continuous hierarchy collapses"
    ax.annotate('Continuous\nhierarchy\ncollapses',
                xy=(13.5, 9.0), fontsize=9, color=C_FROZEN, ha='center',
                style='italic')

    # Right: resurrection
    ax.annotate('Discrete path\nresurrects\naccessibility',
                xy=(13.5, 1.8), fontsize=9, color=C_ESCAPE, ha='center',
                style='italic', fontweight='bold')

    # ── Formal statement ──
    ax.text(cx, 14.8,
            'Four-Level Accessibility Hierarchy',
            fontsize=17, fontweight='bold', color=C_TEXT, ha='center', va='center')
    ax.text(cx, 14.0,
            r'$\mathrm{Direct} \subset \mathrm{Gradient} \subset \mathrm{Curvature} \subset \mathrm{Lie\ Closure} \subsetneq \mathrm{Composition}$',
            fontsize=10.5, color=C_SUBTEXT, ha='center', va='center')
    ax.text(cx, 13.3,
            'Cross-block transport lives ONLY in the composition layer.',
            fontsize=9.5, color=C_ESCAPE, ha='center', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 1 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 2: Lie Barrier / Frozen Accessibility — Wall Diagram
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig2_lie_barrier(output_path):
    """The signature visual of Paper III: continuous Lie flow hits a wall;
    discrete composition detours around it through hybrid sectors.

    Left panel:  Continuous Lie flow  A --X--> B  (blocked by wall)
    Right panel: Discrete composition  A → H1 → H2 → B  (hybrid bridge)
    """
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(18, 9))
    fig.patch.set_facecolor(C_BG)

    for ax in [axL, axR]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_facecolor(C_BG)

    # ── Left: Continuous Lie flow blocked ──
    axL.set_title('Continuous Lie Accessibility', fontsize=14, fontweight='bold',
                  color=C_LIE, pad=15)

    # Block A (left)
    rect_a = FancyBboxPatch((0.5, 3.5), 2.5, 3.0, boxstyle="round,pad=0.15",
                            facecolor='#1a2a3c', edgecolor=C_P1, linewidth=2.5, alpha=0.7)
    axL.add_patch(rect_a)
    axL.text(1.75, 5.0, 'Block A\n(pure sectors)', fontsize=11, fontweight='bold',
             color=C_TEXT, ha='center', va='center')
    axL.text(1.75, 4.2, r'$\alpha$', fontsize=18, color=C_P1, ha='center', va='center',
             fontweight='bold')

    # Block B (right)
    rect_b = FancyBboxPatch((7.0, 3.5), 2.5, 3.0, boxstyle="round,pad=0.15",
                            facecolor='#2a1a2c', edgecolor=C_P2, linewidth=2.5, alpha=0.7)
    axL.add_patch(rect_b)
    axL.text(8.25, 5.0, 'Block B\n(pure sectors)', fontsize=11, fontweight='bold',
             color=C_TEXT, ha='center', va='center')
    axL.text(8.25, 4.2, r'$\beta$', fontsize=18, color=C_P2, ha='center', va='center',
             fontweight='bold')

    # Wall between blocks
    wall_rect = FancyBboxPatch((3.8, 1.5), 2.4, 7.0, boxstyle="round,pad=0.1",
                               facecolor='#2a1a2a', edgecolor=C_WALL, linewidth=3.0, alpha=0.6)
    axL.add_patch(wall_rect)
    axL.text(5.0, 6.5, 'LIE\nBARRIER', fontsize=14, fontweight='bold',
             color=C_WALL, ha='center', va='center')
    axL.text(5.0, 5.2, r'$\kappa_d = 0$', fontsize=12, color=C_FROZEN, ha='center', va='center')
    axL.text(5.0, 4.5, r'$\forall d \geq 0$', fontsize=10, color=C_FROZEN, ha='center', va='center')
    axL.text(5.0, 3.5, 'Lemma 1:\nall Lie monomials\nblock-diagonal', fontsize=8,
             color=C_MUTED, ha='center', va='center')

    # Attempted Lie arrows (hit wall)
    for y_offset in [5.5, 5.0, 4.5]:
        # Arrow from A to wall
        axL.annotate('', xy=(4.2, y_offset), xytext=(3.2, y_offset),
                    arrowprops=dict(arrowstyle='->', color=C_LIE, lw=2.0, alpha=0.7))
        # X mark at wall
        axL.text(4.6, y_offset, 'X', fontsize=14, color=C_ESCAPE, ha='center', va='center',
                fontweight='bold')

    # Lie generators label
    axL.text(2.0, 7.5, r'$A_g = \log\rho(g)$', fontsize=10, color=C_LIE, ha='center')
    axL.text(2.0, 7.0, r'$[A_g, A_h]$', fontsize=9, color=C_LIE, ha='center')
    axL.text(2.0, 6.5, '... all depths', fontsize=8, color=C_MUTED, ha='center')

    # Annotations
    axL.text(5.0, 1.0, 'Lie algebra is structurally blind\nto cross-block transport.',
             fontsize=10, color=C_FROZEN, ha='center', style='italic')
    axL.text(5.0, 0.4, 'FROZEN — inaccessible at all Lie depths',
             fontsize=9, color=C_ESCAPE, ha='center', fontweight='bold')

    # ── Right: Discrete composition escape ──
    axR.set_title('Discrete Composition Escape (T7)', fontsize=14, fontweight='bold',
                  color=C_ESCAPE, pad=15)

    # Block A
    rect_a2 = FancyBboxPatch((0.3, 3.0), 2.2, 4.0, boxstyle="round,pad=0.15",
                             facecolor='#1a2a3c', edgecolor=C_P1, linewidth=2.5, alpha=0.7)
    axR.add_patch(rect_a2)
    axR.text(1.4, 5.0, 'Block A', fontsize=11, fontweight='bold', color=C_TEXT, ha='center')

    # Block B
    rect_b2 = FancyBboxPatch((7.5, 3.0), 2.2, 4.0, boxstyle="round,pad=0.15",
                             facecolor='#2a1a2c', edgecolor=C_P2, linewidth=2.5, alpha=0.7)
    axR.add_patch(rect_b2)
    axR.text(8.6, 5.0, 'Block B', fontsize=11, fontweight='bold', color=C_TEXT, ha='center')

    # Hybrid bridge zone
    hybrid_zone = FancyBboxPatch((3.2, 2.5), 3.6, 5.0, boxstyle="round,pad=0.1",
                                 facecolor='#3a2a1a', edgecolor=C_HYBRID, linewidth=2.5,
                                 alpha=0.4, linestyle='--')
    axR.add_patch(hybrid_zone)
    axR.text(5.0, 7.0, 'HYBRID\nBRIDGE', fontsize=12, fontweight='bold',
             color=C_HYBRID, ha='center', va='center')

    # Hybrid sectors
    h1_y, h2_y = 5.5, 3.5
    for hy, hname in [(h1_y, 'H1'), (h2_y, 'H2')]:
        h_rect = FancyBboxPatch((4.0, hy - 0.4), 2.0, 0.8, boxstyle="round,pad=0.08",
                                facecolor='#5a3a1a', edgecolor=C_HYBRID, linewidth=2.0, alpha=0.9)
        axR.add_patch(h_rect)
        axR.text(5.0, hy, hname, fontsize=11, fontweight='bold', color=C_HYBRID,
                 ha='center', va='center')

    # Composition path: α → H1 → H2 → β
    # α→H1
    axR.annotate('', xy=(4.0, h1_y), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=3.0,
                              connectionstyle='arc3,rad=0.2'))
    # H1→H2
    axR.annotate('', xy=(5.0, h2_y + 0.4), xytext=(5.0, h1_y - 0.4),
                arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=3.0))
    # H2→β
    axR.annotate('', xy=(7.5, 4.5), xytext=(6.0, h2_y),
                arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=3.0,
                              connectionstyle='arc3,rad=-0.2'))

    # Source and target labels
    axR.text(1.4, 3.8, r'$\alpha$', fontsize=18, color=C_P1, ha='center', fontweight='bold')
    axR.text(8.6, 3.8, r'$\beta$', fontsize=18, color=C_P2, ha='center', fontweight='bold')

    # ρ(g) labels on edges
    axR.text(3.2, 5.8, r'$\rho(g)$', fontsize=9, color=C_ESCAPE, ha='center')
    axR.text(5.5, 5.8, r'$\rho(h)$', fontsize=9, color=C_ESCAPE, ha='center')
    axR.text(6.8, 5.0, r'$\rho(k)$', fontsize=9, color=C_ESCAPE, ha='center')

    # Annotation
    axR.text(5.0, 1.8, r'$P_\alpha \rho(g) P_{H1} \rho(h) P_{H2} \rho(k) P_\beta \neq 0$',
             fontsize=10, color=C_ESCAPE, ha='center', fontweight='bold')
    axR.text(5.0, 1.2, 'Composition path bypasses Lie barrier.\nHybrid sectors bridge blocks.',
             fontsize=9, color=C_SUBTEXT, ha='center')
    axR.text(5.0, 0.5, 'ESCAPE — reachable only via discrete composition',
             fontsize=9, color=C_ESCAPE, ha='center', fontweight='bold')

    # ── Overall title ──
    fig.suptitle('Lie Barrier & Discrete Escape: The Central Visual Metaphor',
                 fontsize=17, fontweight='bold', color=C_TEXT, y=1.02)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 2 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 3: Curvature Emergence — Geometric Diagram
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig3_curvature_emergence(output_path):
    """Geometric visualization of κ₀=0, κ₁>0 — first-order frozen, second-order
    commutator bends trajectory to create accessibility.

    Shows: tangent cone = 0 at first order, commutator bends into connection.
    """
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.patch.set_facecolor(C_BG)

    titles = [
        'Direct Transport (K = 0)',
        r'Gradient Accessibility ($\kappa_0 = 0$)',
        r'Curvature Accessibility ($\kappa_1 > 0$)',
    ]
    colors = [C_FROZEN, C_LIE, C_CURV]

    for idx, (ax, title, color) in enumerate(zip(axes, titles, colors)):
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor(C_BG)
        ax.set_title(title, fontsize=13, fontweight='bold', color=color, pad=12)

        # Two sectors as shaded circles
        circle_a = plt.Circle((-1.8, 0), 0.6, facecolor='#1a2a3c', edgecolor=C_P1,
                              linewidth=2.5, alpha=0.7)
        circle_b = plt.Circle((1.8, 0), 0.6, facecolor='#2a1a2c', edgecolor=C_P2,
                              linewidth=2.5, alpha=0.7)
        ax.add_patch(circle_a)
        ax.add_patch(circle_b)
        ax.text(-1.8, 0, r'$\alpha$', fontsize=14, color=C_P1, ha='center', va='center',
                fontweight='bold')
        ax.text(1.8, 0, r'$\beta$', fontsize=14, color=C_P2, ha='center', va='center',
                fontweight='bold')
        ax.text(-1.8, -0.8, 'Block A', fontsize=8, color=C_MUTED, ha='center')
        ax.text(1.8, -0.8, 'Block B', fontsize=8, color=C_MUTED, ha='center')

    # ── Panel 1: Direct — no connection at all ──
    ax = axes[0]
    # Gray dashed arrows that don't reach
    ax.annotate('', xy=(-0.8, 0.3), xytext=(-1.3, 0.3),
               arrowprops=dict(arrowstyle='->', color=C_FROZEN, lw=1.5, linestyle='dashed'))
    ax.annotate('', xy=(0.8, -0.3), xytext=(1.3, -0.3),
               arrowprops=dict(arrowstyle='->', color=C_FROZEN, lw=1.5, linestyle='dashed'))
    ax.text(0, -1.5, r'$K_{\alpha\beta} = 0$', fontsize=11, color=C_FROZEN, ha='center',
            fontweight='bold')
    ax.text(0, -2.0, 'No shared Supp_nc\nZero direct coupling', fontsize=8.5,
            color=C_MUTED, ha='center')

    # ── Panel 2: Gradient — tangent cone = 0 (frozen) ──
    ax = axes[1]
    # Tangent vectors fanning out from α but stopping (frozen)
    angles = np.linspace(-0.6, 0.6, 5)
    for ang in angles:
        end_x = -1.8 + 0.8 * np.cos(ang)
        end_y = 0.8 * np.sin(ang)
        ax.annotate('', xy=(end_x, end_y), xytext=(-1.3, 0),
                   arrowprops=dict(arrowstyle='->', color=C_LIE, lw=1.2, alpha=0.5))
    # X mark in the gap
    ax.text(0, 0, r'$\times$', fontsize=24, color=C_FROZEN, ha='center', va='center', alpha=0.7)
    ax.text(0, -1.5, r'$\kappa_0(\alpha,\beta) = 0$', fontsize=11, color=C_FROZEN, ha='center',
            fontweight='bold')
    ax.text(0, -2.0, r'$A_g$ is block-diagonal' + '\nTangent cone empty', fontsize=8.5,
            color=C_MUTED, ha='center')

    # ── Panel 3: Curvature — commutator bends trajectory ──
    ax = axes[2]
    # A curved path from α to β via commutator "bending"
    t = np.linspace(0, 1, 100)
    # Cubic Bezier-like curve going up and over
    x_curve = -1.8 + 3.6 * t
    y_curve = 1.5 * np.sin(np.pi * t)  # arc upward
    ax.plot(x_curve, y_curve, color=C_CURV, linewidth=3.5, alpha=0.9)
    # Arrowhead
    ax.annotate('', xy=(1.7, y_curve[-10]), xytext=(1.5, y_curve[-25]),
               arrowprops=dict(arrowstyle='->', color=C_CURV, lw=3.5))

    # Commutator annotation
    ax.text(0, 1.8, r'$[A_g, A_h]$', fontsize=11, color=C_CURV, ha='center', fontweight='bold')
    ax.text(0, 1.3, 'commutator bends\ninto connection', fontsize=8.5, color=C_CURV, ha='center',
            style='italic')
    ax.text(0, -1.5, r'$\kappa_1(\alpha,\beta) > 0$', fontsize=11, color=C_CURV, ha='center',
            fontweight='bold')
    ax.text(0, -2.0, 'Curvature creates channel\nFirst-order frozen, second-order reachable',
            fontsize=8.5, color=C_MUTED, ha='center')

    # Enhancement annotation
    ax.text(0, -2.5, r'Enhancement $\kappa_1/\kappa_0 \sim 10^{14}$',
            fontsize=9, color=C_CURV, ha='center', fontweight='bold')

    # ── Overall ──
    fig.suptitle('Curvature Emergence: First-Order Frozen, Second-Order Accessible',
                 fontsize=17, fontweight='bold', color=C_TEXT, y=1.02)

    # Bottom caption
    fig.text(0.5, 0.02, 'Curvature channels are all within-block. Cross-block transport requires composition (T7).',
             fontsize=10, color=C_MUTED, ha='center', style='italic')

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 3 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 4: S₃ Minimal Prototype
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig4_s3_prototype(output_path):
    """S₃ nat⊕reg — 9-dim minimal T7 prototype. Small graph with 5 sectors,
    dual-color hybrid S5, 3 T7 pairs (dashed red). Zero curvature channels.

    This figure proves: T7 exists without M₂ curvature — they are independent.
    """
    fig, (ax_graph, ax_legend) = plt.subplots(1, 2, figsize=(18, 8),
                                               gridspec_kw={'width_ratios': [2.5, 1]})
    fig.patch.set_facecolor(C_BG)
    ax_graph.set_facecolor(C_BG)
    ax_legend.set_facecolor(C_BG)
    ax_legend.axis('off')

    # ── Node positions ──
    pos = {
        'S1': (-2.5, 1.5),    # pure-reg
        'S2': (-2.5, -1.5),   # pure-reg
        'S4': (2.5, -1.5),    # pure-reg
        'S3': (2.5, 1.5),     # pure-nat
        'S5': (0, 0),         # HYBRID (nat+reg) — bridge
    }

    # Node specs: (label, color, size, is_hybrid)
    nodes = [
        ('S1', C_P1, 800, False),
        ('S2', C_P1, 600, False),
        ('S4', C_P1, 600, False),
        ('S3', C_ESCAPE, 600, False),
        ('S5', C_HYBRID, 1400, True),  # hybrid — larger, dual-colored
    ]

    # Block regions
    rect_nat = FancyBboxPatch((1.2, 0.5), 2.5, 2.5, boxstyle="round,pad=0.1",
                              facecolor='#2a1a2c', edgecolor=C_P2, linewidth=1.5,
                              alpha=0.3, linestyle='--')
    ax_graph.add_patch(rect_nat)
    ax_graph.text(2.45, 2.7, 'nat\n(3D)', fontsize=9, color=C_P2, ha='center', alpha=0.6)

    rect_reg1 = FancyBboxPatch((-3.5, 0.5), 2.5, 2.5, boxstyle="round,pad=0.1",
                               facecolor='#1a2a3c', edgecolor=C_P1, linewidth=1.5,
                               alpha=0.3, linestyle='--')
    ax_graph.add_patch(rect_reg1)
    rect_reg2 = FancyBboxPatch((-3.5, -2.5), 2.5, 2.5, boxstyle="round,pad=0.1",
                               facecolor='#1a2a3c', edgecolor=C_P1, linewidth=1.5,
                               alpha=0.3, linestyle='--')
    ax_graph.text(-2.25, 2.7, 'reg\n(6D)', fontsize=9, color=C_P1, ha='center', alpha=0.6)

    # ── Draw edges ──
    # Direct edges (solid, colored)
    direct_edges = [
        ('S1', 'S5'), ('S2', 'S5'), ('S3', 'S5'), ('S4', 'S5'),
        ('S1', 'S4'),
    ]
    for a, b in direct_edges:
        xa, ya = pos[a]
        xb, yb = pos[b]
        ax_graph.annotate('', xy=(xb, yb), xytext=(xa, ya),
                         arrowprops=dict(arrowstyle='->', color=C_LIE, lw=1.8, alpha=0.5))

    # T7 pairs (dashed red — composition-only)
    t7_pairs = [('S1', 'S3'), ('S2', 'S3'), ('S3', 'S4')]
    for a, b in t7_pairs:
        xa, ya = pos[a]
        xb, yb = pos[b]
        mid_x, mid_y = (xa + xb)/2, (ya + yb)/2
        # Offset midpoint to arc around S5
        offset_x = -mid_x * 0.6
        offset_y = -mid_y * 0.6
        # Draw as curved dashed path
        ax_graph.annotate('', xy=(xb, yb), xytext=(xa, ya),
                         arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=2.5,
                                        linestyle='dashed', alpha=0.8,
                                        connectionstyle=f'arc3,rad={0.3 if b == "S3" else -0.3}'))

    # ── Draw nodes ──
    for label, color, size, is_hybrid in nodes:
        x, y = pos[label]
        if is_hybrid:
            # Dual-color: split circle (left half reg-blue, right half nat-purple)
            wedge_l = Wedge((x, y), 0.35, 90, 270, facecolor=C_P1, edgecolor='white',
                           linewidth=1.5, alpha=0.9)
            wedge_r = Wedge((x, y), 0.35, -90, 90, facecolor=C_P2, edgecolor='white',
                           linewidth=1.5, alpha=0.9)
            ax_graph.add_patch(wedge_l)
            ax_graph.add_patch(wedge_r)
        else:
            ax_graph.scatter(x, y, s=size, c=color, alpha=0.85, edgecolors='white',
                           linewidth=1.5, zorder=10)
        # Label
        offset = 20 if not is_hybrid else 25
        ax_graph.annotate(label, (x, y), textcoords="offset points",
                         xytext=(0, -offset), ha='center', fontsize=11,
                         fontweight='bold', color=C_TEXT)

    # ── Annotation: T7 paths ──
    ax_graph.annotate('T7 pairs\n(composition-only)',
                     xy=(-0.5, 1.8), fontsize=9, color=C_ESCAPE, ha='center',
                     style='italic',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG,
                              edgecolor=C_ESCAPE, alpha=0.8))
    ax_graph.annotate('Hybrid\nBridge',
                     xy=(0, 0.6), fontsize=8, color=C_HYBRID, ha='center',
                     fontweight='bold')

    ax_graph.set_xlim(-4.5, 4.5)
    ax_graph.set_ylim(-3.5, 3.5)
    ax_graph.axis('off')
    ax_graph.set_title(r'S$_3$ nat$\oplus$reg -- 9-dim Minimal T7 Prototype',
                      fontsize=14, fontweight='bold', color=C_TEXT, pad=12)

    # ── Right panel: data table ──
    ax_legend.text(0, 0.95, 'System Properties', fontsize=13, fontweight='bold',
                   color=C_TEXT, ha='left', va='top')
    props = [
        ('Group', r'$S_3$ (order 6)'),
        ('Representation', r'$\rho_{\mathrm{nat}} \oplus \rho_{\mathrm{reg}}$'),
        ('Dimension', '9 (3 + 6)'),
        ('Blocks', '2 (nat, reg)'),
        ('Sectors', '5 (4 pure + 1 hybrid)'),
        ('Direct edges', '14 (all pure--pure or pure--hybrid)'),
        ('Curvature pairs', r'$\mathbf{0}$ — no M₂ in this system'),
        ('T7 pairs', r'$\mathbf{3}$ -- all cross-block nat--reg'),
        ('T7 mediation', 'All through S5 (hybrid)'),
        ('C1 (shared irrep)', r'S$_3$ standard 2-dim: nat(x1), reg(x2) $\checkmark$'),
        ('C2 (hybrid)', r'S5 carries standard irrep from both blocks $\checkmark$'),
        ('C3 (block-diag)', r'$\rho$ block-diagonal by construction $\checkmark$'),
        ('Key fact', r'$\kappa_1 = 0$ everywhere → T7 exists without curvature'),
    ]
    for i, (key, val) in enumerate(props):
        y = 0.88 - i * 0.072
        is_key = (key == 'Key fact')
        c = C_ESCAPE if is_key else C_MUTED
        sz = 9.5 if is_key else 8.5
        fw = 'bold' if is_key else 'normal'
        ax_legend.text(0.05, y, f'{key}:', fontsize=8.5, color=C_SUBTEXT, ha='left', va='top')
        ax_legend.text(0.5, y, val, fontsize=sz, color=c, ha='left', va='top', fontweight=fw)

    # Independence box — placed at figure bottom to avoid table overlap
    fig.text(0.5, 0.02, r'T7 and M$_2$ are logically independent.  $\;$ S$_3$ nat$\oplus$reg: T7 without M$_2$.  $\;$ S$_3$ reg$\oplus$reg: both present.  $\;$ Rubik: both present.',
             fontsize=10, color=C_TEXT, ha='center', va='bottom',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a2a3c',
                      edgecolor=C_HYBRID, alpha=0.85))

    fig.suptitle(r'S$_3$ Minimal Prototype -- T7 Exists Without Curvature, Proving Independence from M$_2$',
                fontsize=15, fontweight='bold', color=C_TEXT, y=1.01)
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 4 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Fig 5: Hybrid Bridge Topology — Obstruction Figure
# ══════════════════════════════════════════════════════════════════════════════════

def plot_fig5_hybrid_bridge(output_path):
    """Obstruction figure: block ambient fields, forbidden wall, thin direct edges,
    thick glowing T7 arcs, prominent hubs, disconnect inset.

    Visual thesis: continuous dynamics CANNOT cross this wall.
    Remove S6/S7 → graph splits into disconnected components.
    """
    fig = plt.figure(figsize=(20, 16), facecolor=C_BG)
    # Main axes
    ax = fig.add_axes([0.02, 0.05, 0.72, 0.90])
    ax.set_facecolor(C_BG)

    # ── Node positions ──
    pos = {
        'S1': (-3.8, 3.0),    # cp+ep isolated — far left
        'S2': (-1.0, 5.2),    # eo — top center
        'S3': (-2.5, 2.0),    # ep+eo — left
        'S4': (2.5, -2.0),    # ep+co — right-center
        'S5': (1.0, 4.8),     # eo — top right
        'S6': (-1.5, 1.0),    # ep+eo — PRIMARY HUB (center-left)
        'S7': (1.0, 0.5),     # cp+ep+co+eo — SECONDARY HUB (center)
        'S8': (4.2, 2.5),     # cp — right
        'S9': (3.0, 0.0),     # cp+co — right center
    }

    sectors = [
        ('S1', ['cp', 'ep'], True, False, True),
        ('S2', ['eo'], False, False, False),
        ('S3', ['ep', 'eo'], True, False, False),
        ('S4', ['ep', 'co'], True, False, False),
        ('S5', ['eo'], False, False, False),
        ('S6', ['ep', 'eo'], True, True, False),
        ('S7', ['cp', 'ep', 'co', 'eo'], True, True, False),
        ('S8', ['cp'], False, False, False),
        ('S9', ['cp', 'co'], True, False, False),
    ]

    # ── 1. Ambient block "fields" (radial glows, not boxes) ──
    field_specs = [
        (-3.0, 2.0, 5.5, C_EP, 'EP'),        # EP: left, red glow
        (3.5, 1.0, 4.5, C_CP, 'CP'),          # CP: right, indigo glow
        (0.0, 5.0, 3.5, C_EO, 'EO'),          # EO: top, teal glow
        (2.8, -2.0, 3.0, C_CO, 'CO'),         # CO: bottom-right, amber glow
    ]
    for cx_f, cy_f, radius, color, label in field_specs:
        # Concentric circles for soft radial glow
        for r_scale, alpha in [(1.0, 0.04), (0.7, 0.06), (0.45, 0.09)]:
            circle = plt.Circle((cx_f, cy_f), radius * r_scale,
                               facecolor=color, edgecolor='none',
                               alpha=alpha, transform=ax.transData)
            ax.add_patch(circle)
        # Label at field center
        ax.text(cx_f, cy_f, label, fontsize=16, color=color,
                ha='center', va='center', alpha=0.18, fontweight='bold')

    # ── 2. Forbidden wall / barrier curtain (between EP and CP zones) ──
    wall_x = 0.0
    wall_ymin, wall_ymax = -5.5, 5.8
    # Gradient curtain via overlapping semi-transparent bands
    for i, (x_offset, alpha) in enumerate([
        (-0.2, 0.06), (0.0, 0.10), (0.2, 0.06),
        (-0.5, 0.03), (0.5, 0.03),
    ]):
        rect = FancyBboxPatch((wall_x + x_offset - 0.12, wall_ymin), 0.24,
                              wall_ymax - wall_ymin,
                              boxstyle="round,pad=0.05",
                              facecolor=C_WALL, edgecolor='none',
                              alpha=alpha)
        ax.add_patch(rect)
    # Wall label
    ax.text(wall_x, wall_ymax + 0.3, 'LIE BARRIER',
            fontsize=13, color=C_WALL, ha='center', va='bottom',
            fontweight='bold', alpha=0.75)
    ax.text(wall_x, wall_ymax - 0.2, r'$\kappa_d = 0 \;\forall d$',
            fontsize=9, color=C_FROZEN, ha='center', va='top', alpha=0.7)

    # ── 3. Direct edges — thin, cool, sparse (keep ~40% = structurally essential) ──
    direct_edges = [
        # Hub S6 connections (primary hub, degree 5)
        ('S2', 'S6'), ('S3', 'S6'), ('S4', 'S6'), ('S5', 'S6'),
        # Hub S7 connections (secondary hub, degree 4)
        ('S6', 'S7'), ('S3', 'S7'), ('S7', 'S8'), ('S7', 'S9'),
        # Within-block essential
        ('S8', 'S9'),          # CP-mediated channel
        ('S2', 'S3'),          # both EO
        ('S2', 'S5'),          # both EO
        ('S4', 'S9'),          # both CO
    ]
    drawn = set()
    for a, b in direct_edges:
        if (a, b) in drawn or (b, a) in drawn:
            continue
        drawn.add((a, b))
        xa, ya = pos[a]
        xb, yb = pos[b]
        ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                   arrowprops=dict(arrowstyle='->', color='#5b7a9f', lw=1.0,
                                  alpha=0.30))

    # ── 4. T7 edges — thick, bright, glowing (composition escape) ──
    t7_pairs = [
        ('S2', 'S4'), ('S3', 'S9'), ('S4', 'S5'), ('S4', 'S8'), ('S6', 'S9'),
    ]
    for a, b in t7_pairs:
        xa, ya = pos[a]
        xb, yb = pos[b]
        # Glow layer (thick, low alpha)
        ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                   arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=7.0,
                                  alpha=0.18,
                                  connectionstyle='arc3,rad=0.3'))
        # Core layer (thinner, bright)
        ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                   arrowprops=dict(arrowstyle='->', color=C_ESCAPE, lw=3.5,
                                  alpha=0.9,
                                  connectionstyle='arc3,rad=0.3'))

    # ── 5. Draw nodes ──
    for label, blocks, is_hybrid, is_hub, is_isolated in sectors:
        x, y = pos[label]
        n_blocks = len(blocks)

        if is_isolated:
            # S1: frozen, dim, dashed outline — G-invariant subrepresentation
            circle = plt.Circle((x, y), 0.5, facecolor='#151520', edgecolor=C_FROZEN,
                               linewidth=2.5, alpha=0.5, linestyle='--')
            ax.add_patch(circle)
            ax.text(x, y, 'S1', fontsize=11, color=C_FROZEN, ha='center', va='center',
                   fontweight='bold')
            ax.text(x, y - 0.9, 'FROZEN', fontsize=8, color=C_FROZEN, ha='center',
                   style='italic', alpha=0.7)
        elif is_hub:
            # Large pie for hubs
            hub_r = 0.65 if label == 'S6' else 0.55
            block_colors = [BLOCK_COLORS[b] for b in blocks]
            for bi, b_color in enumerate(block_colors):
                start_angle = 90 + bi * 360 / n_blocks
                end_angle = 90 + (bi + 1) * 360 / n_blocks
                wedge = Wedge((x, y), hub_r, start_angle, end_angle,
                             facecolor=b_color, edgecolor='white',
                             linewidth=2.5, alpha=0.95)
                ax.add_patch(wedge)
            # Outer glow ring
            glow_ring = plt.Circle((x, y), hub_r + 0.15, facecolor='none',
                                  edgecolor=C_HYBRID, linewidth=4.0, alpha=0.35)
            ax.add_patch(glow_ring)
            ring = plt.Circle((x, y), hub_r + 0.08, facecolor='none',
                             edgecolor=C_HYBRID, linewidth=2.5, alpha=0.85)
            ax.add_patch(ring)
            # Label
            ax.annotate(label, (x, y), textcoords="offset points",
                       xytext=(0, -32), ha='center', fontsize=14,
                       fontweight='bold', color=C_TEXT)
        elif is_hybrid and n_blocks >= 2:
            block_colors = [BLOCK_COLORS[b] for b in blocks]
            for bi, b_color in enumerate(block_colors):
                start_angle = 90 + bi * 360 / n_blocks
                end_angle = 90 + (bi + 1) * 360 / n_blocks
                wedge = Wedge((x, y), 0.35, start_angle, end_angle,
                             facecolor=b_color, edgecolor='white',
                             linewidth=1.0, alpha=0.85)
                ax.add_patch(wedge)
            ax.annotate(label, (x, y), textcoords="offset points",
                       xytext=(0, -20), ha='center', fontsize=11,
                       fontweight='normal', color=C_TEXT)
        else:
            color = BLOCK_COLORS[blocks[0]]
            circle = plt.Circle((x, y), 0.32, facecolor=color, edgecolor='white',
                               linewidth=1.0, alpha=0.85)
            ax.add_patch(circle)
            ax.annotate(label, (x, y), textcoords="offset points",
                       xytext=(0, -20), ha='center', fontsize=11,
                       fontweight='normal', color=C_TEXT)

    # ── 6. S6/S7 annotation ──
    ax.annotate('PRIMARY\nHUB', xy=pos['S6'], xytext=(-4.0, -1.5),
               fontsize=11, color=C_HYBRID, ha='center', fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=C_HYBRID, lw=1.5))
    ax.annotate('SECONDARY\nHUB', xy=pos['S7'], xytext=(4.5, -1.5),
               fontsize=11, color=C_HYBRID, ha='center', fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=C_HYBRID, lw=1.5))

    # ── Legend ──
    legend_y = -4.8
    legend_items = [
        ('#5b7a9f', 'Direct edge (K > 0)', 1.0, 'solid'),
        (C_ESCAPE, 'T7 pair (composition-only)', 3.5, 'solid'),
        (C_HYBRID, 'Transport-active hybrid (hub)', 2.5, 'ring'),
        (C_FROZEN, 'Isolated / Lie-frozen (S1)', 2.5, 'dotted'),
    ]
    for i, (color, label, lw, style) in enumerate(legend_items):
        y_pos = legend_y - i * 0.65
        if style == 'ring':
            ring = plt.Circle((-4.5, y_pos), 0.15, facecolor='none', edgecolor=color,
                             linewidth=lw, alpha=0.85)
            ax.add_patch(ring)
        else:
            ax.plot([-5.0, -3.8], [y_pos, y_pos], color=color, linewidth=lw,
                    linestyle=style, alpha=0.85)
        ax.text(-3.5, y_pos, label, fontsize=11, color=C_TEXT, ha='left', va='center')

    # Block color legend
    for i, (block, color) in enumerate([('cp', C_CP), ('ep', C_EP), ('co', C_CO), ('eo', C_EO)]):
        x_pos = 2.5 + i * 1.8
        rect = FancyBboxPatch((x_pos, legend_y - 0.3), 0.5, 0.35, boxstyle="round,pad=0.04",
                              facecolor=color, edgecolor='white', linewidth=1.0, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x_pos + 0.25, legend_y - 0.12, block.upper(), fontsize=10, color=C_TEXT,
                ha='center', va='center', fontweight='bold')

    ax.set_xlim(-6.0, 6.0)
    ax.set_ylim(-6.0, 6.5)
    ax.axis('off')

    # ── 7. Disconnect INSET: "WITHOUT HYBRIDS" ──
    inset_ax = fig.add_axes([0.76, 0.40, 0.22, 0.42])
    inset_ax.set_facecolor('#0a0a14')
    inset_ax.set_xlim(-3, 3)
    inset_ax.set_ylim(-3, 3.5)
    inset_ax.axis('off')
    # Title
    inset_ax.text(0, 3.3, 'WITHOUT HYBRIDS', fontsize=13, color=C_ESCAPE,
                 ha='center', fontweight='bold')
    inset_ax.text(0, 2.9, '(S6 & S7 removed)', fontsize=9, color=C_MUTED,
                 ha='center')

    # Disconnected components
    # Component 1: EP+EO cluster (left)
    comp1_nodes = {'S2': (-1.5, 1.8), 'S3': (-1.8, 0.8), 'S5': (-0.5, 1.8)}
    # Component 2: CP+CO cluster (right)
    comp2_nodes = {'S4': (1.5, -0.5), 'S8': (2.0, 0.8), 'S9': (1.5, 0.0)}
    # Component 3: S1 alone (isolated)
    comp3_node = ('S1', -2.5, -0.5)

    # Draw component 1 edges
    for a, b in [('S2', 'S3'), ('S2', 'S5')]:
        xa, ya = comp1_nodes[a]
        xb, yb = comp1_nodes[b]
        inset_ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                         arrowprops=dict(arrowstyle='->', color='#5b7a9f', lw=1.0, alpha=0.5))
    # Draw component 2 edges
    for a, b in [('S8', 'S9'), ('S4', 'S9')]:
        xa, ya = comp2_nodes[a]
        xb, yb = comp2_nodes[b]
        inset_ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                         arrowprops=dict(arrowstyle='->', color='#5b7a9f', lw=1.0, alpha=0.5))

    # Draw nodes for components
    for label, (x, y) in comp1_nodes.items():
        inset_ax.scatter(x, y, s=180, c='#445566', edgecolors='#666666', linewidth=1, alpha=0.7)
        inset_ax.text(x, y - 0.3, label, fontsize=9, color='#888888', ha='center')
    for label, (x, y) in comp2_nodes.items():
        inset_ax.scatter(x, y, s=180, c='#445566', edgecolors='#666666', linewidth=1, alpha=0.7)
        inset_ax.text(x, y - 0.3, label, fontsize=9, color='#888888', ha='center')
    # S1 alone
    x, y = comp3_node[1], comp3_node[2]
    inset_ax.scatter(x, y, s=120, c='#151520', edgecolors=C_FROZEN, linewidth=2, alpha=0.5,
                    linestyle='--')
    inset_ax.text(x, y - 0.3, 'S1', fontsize=9, color=C_FROZEN, ha='center')

    # Gray out cross-block T7 paths
    for a, b in [('S2', 'S4'), ('S3', 'S9'), ('S4', 'S5'), ('S4', 'S8'), ('S6', 'S9')]:
        # Just draw faint gray dashes
        pass  # T7 edges don't exist without hybrids — nothing to draw
    inset_ax.text(0, -1.8, 'All cross-block paths GONE.',
                 fontsize=10, color=C_ESCAPE, ha='center', fontweight='bold')
    inset_ax.text(0, -2.2, 'Graph splits into\n3 disconnected components.',
                 fontsize=9, color=C_MUTED, ha='center')

    # Inset border
    inset_border = FancyBboxPatch((-3.2, -2.6), 6.4, 6.2,
                                  boxstyle="round,pad=0.1",
                                  facecolor='none', edgecolor='#333355',
                                  linewidth=1.5, alpha=0.6)
    inset_ax.add_patch(inset_border)

    # ── Main title ──
    fig.text(0.38, 0.97, 'Hybrid Bridge Topology — Cross-Block Accessibility Exists ONLY Through Hybrids',
             fontsize=17, fontweight='bold', color=C_TEXT, ha='center')

    # Key takeaway
    fig.text(0.38, 0.03, 'Remove S6 and S7  →  cross-block graph disconnects into 3 isolated components.  Hybrid sectors are the sole bridges between blocks.',
             fontsize=12, color=C_HYBRID, ha='center', style='italic')

    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"Fig 5 saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════════

def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    print("=" * 60)
    print("Paper III Figures: Lie Accessibility & Discrete/Continuous Split")
    print("=" * 60)
    print("(Figs 0–3: conceptual, no CSO needed)")

    print("\n── Fig 0: Accessibility Hierarchy Collapse ──")
    plot_fig0_pipeline(os.path.join(FIG_DIR, 'fig0_pipeline.png'))

    print("\n── Fig 1: Four-Level Accessibility Hierarchy ──")
    plot_fig1_hierarchy(os.path.join(FIG_DIR, 'fig1_hierarchy.png'))

    print("\n── Fig 2: Lie Barrier / Frozen Accessibility ──")
    plot_fig2_lie_barrier(os.path.join(FIG_DIR, 'fig2_lie_barrier.png'))

    print("\n── Fig 3: Curvature Emergence ──")
    plot_fig3_curvature_emergence(os.path.join(FIG_DIR, 'fig3_curvature_emergence.png'))

    print("\n── Fig 4: S₃ Minimal Prototype ──")
    plot_fig4_s3_prototype(os.path.join(FIG_DIR, 'fig4_s3_prototype.png'))

    print("\n── Fig 5: Hybrid Bridge Topology ──")
    plot_fig5_hybrid_bridge(os.path.join(FIG_DIR, 'fig5_hybrid_bridge.png'))

    print(f"\nAll 6 figures saved to {FIG_DIR}/")
    print("Done.")


if __name__ == '__main__':
    main()
