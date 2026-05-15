"""
Trilogy Visual Elements — node/edge shapes, markers, and semantic conventions.

Visual grammar (consistent across all three papers):
  ┌─────────────────────────────────────────────────────────┐
  │  Element          │  Shape/Style          │  Meaning    │
  ├─────────────────────────────────────────────────────────┤
  │  Spectral layer   │  Rounded rect (round)  │  coarse     │
  │  Primitive sector │  Square (sharp)        │  fine       │
  │  Hub              │  Double circle ○◎      │  primary    │
  │  Block            │  Hexagon               │  invariant  │
  │  Commutative      │  Blue fill             │  pure       │
  │  Noncommutative   │  Red fill              │  hybrid     │
  │  Forbidden edge   │  Gray dashed           │  frozen     │
  │  Composition edge │  Bold solid            │  enabled    │
  │  Curvature edge   │  Purple dotted         │  Lie-only   │
  │  Cross-block      │  Double line           │  mediated   │
  └─────────────────────────────────────────────────────────┘
"""

# ── Node Shapes ────────────────────────────────────────────────────────
# Each shape carries semantic meaning. Use consistently across trilogy.

import matplotlib.patches as mpatches

# Box styles for FancyBboxPatch
BOX_STYLES = {
    'layer':   'round',          # rounded rect — spectral layer (coarse resolution)
    'sector':  'square',         # sharp rect   — primitive sector (fine resolution)
    'block':   'round',          # rounded      — invariant subspace block
    'hub':     'round',          # round + double border — transport hub
}

# Box padding (points)
BOX_PADDING = {
    'layer':   12,
    'sector':  10,
    'block':   14,
    'hub':     16,
}

# Border widths
BORDER_WIDTH = {
    'layer':   2.0,
    'sector':  2.2,
    'block':   1.8,
    'hub':     3.0,   # double-border effect via thicker stroke
    'normal':  1.5,
}

# ── Node Markers (for scatter/network plots) ───────────────────────────

NODE_MARKERS = {
    'layer':         's',      # square
    'sector':        's',      # square
    'hub_primary':   'D',      # diamond
    'hub_secondary': 's',      # square
    'isolated':      'o',      # circle — no outgoing edges
    'block_cp':      'H',      # hexagon
    'block_ep':      'H',      # hexagon
    'block_co':      'h',      # hexagon (flat top)
    'block_eo':      'h',      # hexagon (flat top)
}

NODE_SIZES = {
    'layer':          120,
    'sector':         100,
    'hub_primary':    180,
    'hub_secondary':  150,
    'isolated':        80,
    'block':          140,
    'default':        100,
}

# ── Edge Styles ─────────────────────────────────────────────────────────

EDGE_STYLES = {
    'direct':         {'linestyle': '-',     'linewidth': 2.5,  'alpha': 0.9},
    'composition':    {'linestyle': '-',     'linewidth': 2.5,  'alpha': 0.9},
    'curvature':      {'linestyle': ':',     'linewidth': 1.8,  'alpha': 0.7},
    'forbidden':      {'linestyle': '--',    'linewidth': 1.2,  'alpha': 0.4},
    'cross_block':    {'linestyle': '-',     'linewidth': 1.5,  'alpha': 0.5},
    'self_loop':      {'linestyle': '-',     'linewidth': 1.0,  'alpha': 0.6},
    'Lie_frozen':     {'linestyle': '--',    'linewidth': 1.0,  'alpha': 0.3},
    'mediated':       {'linestyle': '-.',    'linewidth': 1.5,  'alpha': 0.6},
}

# Edge color — keyed by edge type semantic meaning
EDGE_COLORS = {
    'direct':         '#2c3e50',   # dark — composition-enabled
    'composition':    '#2c3e50',
    'curvature':      '#8e44ad',   # purple — Lie curvature
    'forbidden':      '#95a5a6',   # gray — inaccessible
    'Lie_frozen':     '#95a5a6',
    'cross_block':    '#7f8c8d',
    'mediated':       '#bdc3c7',
}

# ── Figure Layout ──────────────────────────────────────────────────────

# Canonical figure sizes (inches)
FIGURE_SIZES = {
    'single':       (8, 5),       # single panel
    'double':       (12, 6),      # two panels side-by-side
    'triple':       (16, 6),      # three panels
    'full_width':   (14, 8),      # full-width explanatory figure
    'heatmap':      (10, 8),      # square-ish for matrices
    'graph':        (12, 10),     # transport graph / network
    'hierarchy':    (10, 8),      # hierarchy / lattice / tree
    'ladder':       (6, 10),      # spectrum ladder
    'pipeline':     (8, 14),      # vertical pipeline (e.g., trilogy master figure)
}

# ── Font Specifications ─────────────────────────────────────────────────

TITLE_FONTS = {
    'I':   {'family': 'serif',      'size': 14, 'weight': 'normal'},
    'II':  {'family': 'sans-serif', 'size': 13, 'weight': 'bold'},
    'III': {'family': 'sans-serif', 'size': 14, 'weight': 'bold'},
}

LABEL_FONTS = {
    'I':   {'family': 'serif',      'size': 12},
    'II':  {'family': 'sans-serif', 'size': 11},
    'III': {'family': 'sans-serif', 'size': 12},
}

ANNOTATION_FONTS = {
    'I':   {'family': 'serif',      'size': 10, 'style': 'italic'},
    'II':  {'family': 'sans-serif', 'size': 9},
    'III': {'family': 'sans-serif', 'size': 10},
}

# ── Helper Functions ───────────────────────────────────────────────────

def get_node_style(element_type):
    """Return (marker, size, edgecolor, edgewidth) tuple for a node type."""
    marker = NODE_MARKERS.get(element_type, 'o')
    size = NODE_SIZES.get(element_type, NODE_SIZES['default'])
    return marker, size


def get_edge_style(edge_type):
    """Return a dict of line properties for an edge type."""
    style = EDGE_STYLES.get(edge_type, EDGE_STYLES['direct']).copy()
    style['color'] = EDGE_COLORS.get(edge_type, '#2c3e50')
    return style


def styled_box(ax, x, y, width, height, box_type='layer',
               facecolor='#ffffff', edgecolor='#333333', **kwargs):
    """Place a styled FancyBboxPatch on the given axes.

    Args:
        ax: matplotlib Axes
        x, y: bottom-left corner
        width, height: box dimensions
        box_type: 'layer', 'sector', 'block', 'hub'
        facecolor, edgecolor: fill and stroke colors
        **kwargs: passed to FancyBboxPatch
    """
    box_style = mpatches.BoxStyle(
        BOX_STYLES.get(box_type, 'round'),
        pad=BOX_PADDING.get(box_type, 10)
    )
    lw = BORDER_WIDTH.get(box_type, 1.5)

    # Double border for hubs
    if box_type == 'hub':
        lw = BORDER_WIDTH['hub']

    patch = mpatches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle=box_style,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        **kwargs
    )
    ax.add_patch(patch)
    return patch
