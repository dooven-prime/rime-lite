"""
Trilogy Style — shared visual language for Papers I, II, III.

Usage:
    from rime.trilogy_style import apply_style, COLORS, ELEMENTS
    apply_style('I')  # set matplotlib rcParams for Paper I

    # Color access
    COLORS['layer']['V5/9']  # → '#c0392b'
    COLORS.layer_color(k=4)   # → '#c0392b'

    # Element access
    ELEMENTS.get_edge_style('forbidden')  # → {linestyle: '--', ...}
"""

from .colors import (
    LAYER_COLORS, LAYER_COLORS_BY_K, LAYER_COLORS_LIGHT,
    SECTOR_COLORS, SECTOR_LABELS,
    BLOCK_COLORS, BLOCK_LABELS,
    SEMANTIC,
    PAPER_COLORS, PAPER_LABELS,
    GENSET_COLORS,
    CANVAS,
    layer_color, sector_color, block_color, paper_color,
)

from .styles import (
    STYLES, PAPER_I, PAPER_II, PAPER_III, _BASE,
    apply_style, reset_style,
)

from .elements import (
    BOX_STYLES, BOX_PADDING, BORDER_WIDTH,
    NODE_MARKERS, NODE_SIZES,
    EDGE_STYLES, EDGE_COLORS,
    FIGURE_SIZES,
    TITLE_FONTS, LABEL_FONTS, ANNOTATION_FONTS,
    get_node_style, get_edge_style, styled_box,
)

__version__ = '1.0.0'
