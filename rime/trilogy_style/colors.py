"""
Trilogy Color System — single source of truth for all figure colors.

Semantic principle:
  Blue tones   = commutative, pure, structural
  Red tones    = noncommutative, hybrid, dynamical
  Gray dashed  = forbidden, Lie-frozen, inaccessible
  Bold edge    = composition-enabled
  Double node  = hub

Block identity:
  CP: indigo/slate   (exactly commutative, Q3 Hamming scheme)
  EP: crimson/brick  (noncommutative dynamical core, 94%)
  CO: amber/gold     (Z3 phase, corner orientation)
  EO: teal           (Z2 phase, edge orientation)

Paper identity:
  Paper I:   blue    (spectral ontology)
  Paper II:  purple  (transport topology)
  Paper III: orange  (Lie accessibility)
"""

# ── Spectral Layers (6, post-ρ-fix, k=0,1,2,3,4,6) ──────────────────────
# Ordered from largest λ to smallest.

LAYER_COLORS = {
    'V1':   '#1a3a5c',   # k=0, λ=1     — isolated, trivial, commutative core (deep navy)
    'V8/9': '#16a085',   # k=1, λ=8/9   — newly discovered, small (teal)
    'V7/9': '#2980b9',   # k=2, λ=7/9   — transport-active (medium blue)
    'V2/3': '#27ae60',   # k=3, λ=2/3   — co-block boundary (green)
    'V5/9': '#c0392b',   # k=4, λ=5/9   — primary hub (warm red)
    'V1/3': '#e67e22',   # k=6, λ=1/3   — CP-dominated, outer layer (orange)
}

# Aliases keyed by k-value
LAYER_COLORS_BY_K = {
    0: '#1a3a5c',   # V1
    1: '#16a085',   # V8/9
    2: '#2980b9',   # V7/9
    3: '#27ae60',   # V2/3
    4: '#c0392b',   # V5/9
    6: '#e67e22',   # V1/3
}

# Lighter tint variants for filled areas / translucent elements
LAYER_COLORS_LIGHT = {
    'V1':   '#d6e4f0',
    'V8/9': '#d1f2eb',
    'V7/9': '#d4e6f1',
    'V2/3': '#d5f5e3',
    'V5/9': '#f5b7b1',
    'V1/3': '#fdebd0',
}

# ── Primitive Sectors (9, post-ρ-fix) ──────────────────────────────────
# Inherit hue from parent spectral layer, vary saturation/lightness.

SECTOR_COLORS = {
    'S1': '#1a3a5c',   # V1     cp+ep  — ISOLATED
    'S2': '#1abc9c',   # V8/9   eo     — small, connective
    'S3': '#3498db',   # V7/9   ep+eo
    'S4': '#2ecc71',   # V2/3   ep+co
    'S5': '#e74c3c',   # V5/9   eo
    'S6': '#c0392b',   # V5/9   ep+eo  — PRIMARY HUB
    'S7': '#e67e22',   # V5/9   cp+ep+co+eo — SECONDARY HUB
    'S8': '#f39c12',   # V1/3   cp
    'S9': '#d35400',   # V1/3   cp+co
}

SECTOR_LABELS = {
    'S1': 'S₁ (V₁, cp+ep)',
    'S2': 'S₂ (V₈/₉, eo)',
    'S3': 'S₃ (V₇/₉, ep+eo)',
    'S4': 'S₄ (V₂/₃, ep+co)',
    'S5': 'S₅ (V₅/₉, eo)',
    'S6': 'S₆ (V₅/₉, ep+eo) — HUB',
    'S7': 'S₇ (V₅/₉, cp+ep+co+eo) — HUB',
    'S8': 'S₈ (V₁/₃, cp)',
    'S9': 'S₉ (V₁/₃, cp+co)',
}

# ── Blocks ─────────────────────────────────────────────────────────────

BLOCK_COLORS = {
    'cp': '#5b6abf',   # corner permutation — commutative, Q3 Hamming
    'ep': '#e74c3c',   # edge permutation — noncommutative dynamical core (94%)
    'co': '#f39c12',   # corner orientation — Z3 phase, amber
    'eo': '#16a085',   # edge orientation — Z2 phase, teal
}

BLOCK_LABELS = {
    'cp': 'CP (corner perm, 64D)',
    'ep': 'EP (edge perm, 144D)',
    'co': 'CO (corner ori, 8D)',
    'eo': 'EO (edge ori, 12D)',
}

# ── Semantic Mappings ──────────────────────────────────────────────────
# These are the *meaning* → *color* mappings, not tied to any specific object.

SEMANTIC = {
    'commutative':    '#2980b9',   # blue — pure, structural
    'noncommutative': '#e74c3c',   # red — hybrid, dynamical
    'hybrid':         '#e74c3c',   # red — mixed block support
    'forbidden':      '#95a5a6',   # gray — inaccessible, Lie-frozen
    'curvature':      '#8e44ad',   # purple — Lie curvature channels
    'composition':    '#2c3e50',   # dark — discrete composition path
    'hub_primary':    '#c0392b',   # deep red — primary hub
    'hub_secondary':  '#e67e22',   # orange — secondary hub
}

# ── Paper Identity ─────────────────────────────────────────────────────

PAPER_COLORS = {
    'I':   '#2980b9',   # Spectral Ontology — blue
    'II':  '#8e44ad',   # Transport Topology — purple
    'III': '#e67e22',   # Lie Accessibility — orange
}

PAPER_LABELS = {
    'I':   'Paper I: Spectral Ontology',
    'II':  'Paper II: Transport Topology',
    'III': 'Paper III: Lie Accessibility',
}

# ── Generator Sets ─────────────────────────────────────────────────────

GENSET_COLORS = {
    '18-full':     '#2980b9',   # face-symmetric, rational
    '12-quarter':  '#3498db',
    '6-half':      '#5b6abf',
    'abelian':     '#27ae60',   # abelian axis — commutative
    'n=8':         '#e74c3c',   # symmetry-broken → Q(√5)
    'n=10':        '#f39c12',
    'n=16':        '#c0392b',   # symmetry-broken → Q(√5)
    'n=21':        '#16a085',   # extended face-symmetric
}

# ── Background / Canvas ────────────────────────────────────────────────

CANVAS = {
    'white': '#ffffff',
    'light': '#f8f9fa',
    'dark':  '#0d1117',
}

# ── Utility ────────────────────────────────────────────────────────────

def layer_color(lam=None, k=None):
    """Return the canonical color for a spectral layer.

    Accepts either lambda value ('V1', 'V7/9', ...) or k-value (0,1,2,3,4,6).
    """
    if k is not None:
        return LAYER_COLORS_BY_K.get(k, '#333333')
    if lam is not None:
        return LAYER_COLORS.get(str(lam), '#333333')
    return '#333333'

def sector_color(sector_name):
    """Return the canonical color for a primitive sector (S1–S9)."""
    return SECTOR_COLORS.get(sector_name, '#333333')

def block_color(block_name):
    """Return the canonical color for a block (cp/ep/co/eo)."""
    return BLOCK_COLORS.get(block_name, '#333333')

def paper_color(paper):
    """Return the canonical color for a paper (I/II/III)."""
    return PAPER_COLORS.get(paper, '#333333')
