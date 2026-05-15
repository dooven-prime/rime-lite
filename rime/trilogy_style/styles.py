"""
Trilogy Style Sheets — per-paper matplotlib rcParams.

Three visual philosophies:
  Paper I:  "spectral decomposition atlas"  — clean, symmetric, algebraic
  Paper II: "transport network"             — graph-heavy, edge-weight visual
  Paper III:"accessibility obstruction"     — hierarchy, freezing, forbidden

Each paper gets a self-contained style sheet. Use via:
  import matplotlib.pyplot as plt
  from rime.trilogy_style.styles import apply_style
  apply_style('I')   # or 'II' or 'III'
"""

import matplotlib as mpl
from .colors import CANVAS, PAPER_COLORS

# ── Base settings (shared across trilogy) ─────────────────────────────

_BASE = {
    'figure.dpi': 200,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.grid': False,
    'axes.axisbelow': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '#cccccc',
    'mathtext.fontset': 'dejavusans',
}

# ── Paper I: Spectral Decomposition Atlas ──────────────────────────────
# Clean, symmetric, algebraic. No dynamics arrows. Lattice, partition,
# spectrum ladder, refinement trees.

PAPER_I = {
    **_BASE,
    # Canvas
    'figure.facecolor': CANVAS['white'],
    'axes.facecolor': CANVAS['white'],
    # Typography — serif for algebraic/structural feel
    'font.family': 'serif',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    # Lines — thin, clean
    'axes.linewidth': 0.6,
    'grid.linewidth': 0.3,
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
    # Ticks
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    # Spine visibility — minimal
    'axes.spines.top': False,
    'axes.spines.right': False,
}

# ── Paper II: Transport Network ────────────────────────────────────────
# Graph-heavy, edge-weight visual, support overlap heatmaps.
# Bold, high-data-density, network-theoretic.

PAPER_II = {
    **_BASE,
    # Canvas
    'figure.facecolor': CANVAS['white'],
    'axes.facecolor': CANVAS['light'],
    # Typography — sans-serif for modern network viz
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    # Lines — heavier for edge-weight encoding
    'axes.linewidth': 0.8,
    'lines.linewidth': 2.0,
    'lines.markersize': 8,
    # Ticks
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    # Spine visibility — full for graphs
    'axes.spines.top': True,
    'axes.spines.right': True,
    # Colorbar defaults
    'image.cmap': 'viridis',
}

# ── Paper III: Accessibility Obstruction ────────────────────────────────
# Hierarchy, freezing, curvature emergence, forbidden arrows.
# Dark mode — the "wall" that continuous dynamics cannot cross.

PAPER_III = {
    **_BASE,
    # Canvas — dark for obstruction theme
    'figure.facecolor': CANVAS['dark'],
    'axes.facecolor': CANVAS['dark'],
    # Typography — clean sans-serif, white on dark
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    # Text colors for dark bg
    'text.color': '#e6e6e6',
    'axes.labelcolor': '#cccccc',
    'xtick.color': '#999999',
    'ytick.color': '#999999',
    # Lines — high contrast
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#444444',
    'grid.linewidth': 0.3,
    'grid.color': '#333333',
    'lines.linewidth': 2.0,
    'lines.markersize': 7,
    # Ticks
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    # Spine — minimal
    'axes.spines.top': False,
    'axes.spines.right': False,
    # Legend
    'legend.facecolor': '#1a1a2e',
    'legend.edgecolor': '#444444',
    'legend.labelcolor': '#cccccc',
}

# ── Public API ─────────────────────────────────────────────────────────

STYLES = {
    'I':   PAPER_I,
    'II':  PAPER_II,
    'III': PAPER_III,
    'base': _BASE,
}


def apply_style(paper, extra_rc=None):
    """Apply the canonical trilogy style for a given paper.

    Args:
        paper: 'I', 'II', or 'III'
        extra_rc: optional dict of extra rcParams to override/add
    """
    style = STYLES.get(paper, _BASE)
    mpl.rcParams.update(style)
    if extra_rc:
        mpl.rcParams.update(extra_rc)


def reset_style():
    """Reset to matplotlib defaults."""
    mpl.rcdefaults()
