"""Raw pushforward-union primitives for the bounded Fusion-log controls.

The four functions and KERNEL below are copied from the exploratory reference
implementation, without its selected-consumer or summary-enumeration layers.
They support arbitrary finite integer atom labels, not just site atoms.
"""

KERNEL = (0, 1)


def letters(n):
    """Return (p_map, d_map, kernel, collision_image)."""
    if n < 2:
        raise ValueError("the declared family requires n >= 2")
    p_map = {q: (q + 1) % n for q in range(n)}
    d_map = {q: q for q in range(n)}
    d_map[KERNEL[1]] = KERNEL[0]
    return p_map, d_map, KERNEL, KERNEL[0]


def step(part, f_map, letter, n):
    """Return the literal successor and complete effective event, if any."""
    new = {}
    for q, blk in part.items():
        t = f_map[q]
        new[t] = new.get(t, frozenset()) | blk
    new = {q: b for q, b in new.items() if b}
    k0, k1 = KERNEL
    if letter == "d" and k0 in part and k1 in part:
        U0 = tuple(sorted(part[k0]))
        V1 = tuple(sorted(part[k1]))
        fresh = tuple(sorted(part[k0] | part[k1]))
        return new, (letter, k0, k1, U0, V1, KERNEL[0], fresh)
    return new, None


def pkey(part):
    """Canonical key for a literal placed partition."""
    return tuple(sorted((q, tuple(sorted(b))) for q, b in part.items()))


def from_pkey(pk):
    return {q: frozenset(b) for q, b in pk}
