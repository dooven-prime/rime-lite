"""Literal placed-partition and fusion-log model for the proper-arc controls.

The manuscript defines the mathematical object. This local implementation
retains complete parent blocks and ports in each fusion event, then projects
the first event creating F to its origin and filters later carrier events.
"""

from collections import deque

KERNEL = (0, 1)


def letters(n):
    """Return (p_map, d_map, kernel, collision_image)."""
    if n < 3:
        raise ValueError("the proper-arc controls require n >= 3")
    p_map = {q: (q + 1) % n for q in range(n)}
    d_map = {q: q for q in range(n)}
    d_map[KERNEL[1]] = KERNEL[0]
    return p_map, d_map, KERNEL, KERNEL[0]


def step(part, f_map, letter, n):
    """Apply one raw letter. Returns (new_partition, event_or_None).

    event = (letter, k0, k1, U0, V1, c, fresh)  with U0/V1/fresh as sorted tuples
    """
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
    """Canonical key for a partition."""
    return tuple(sorted((q, tuple(sorted(b))) for q, b in part.items()))


def from_pkey(pk):
    return {q: frozenset(b) for q, b in pk}


def bfs(n):
    """Enumerate generated placed partitions with their full fusion logs."""
    p_map, d_map, _kernel, _c = letters(n)
    seed = {i: frozenset([i]) for i in range(n)}
    start = (pkey(seed), ())
    seen = {start}
    dq = deque([start])
    while dq:
        pk, evs = dq.popleft()
        yield pk, evs
        part = from_pkey(pk)
        for letter, f_map in (("p", p_map), ("d", d_map)):
            np_, ev = step(part, f_map, letter, n)
            st = (pkey(np_), evs + (ev,) if ev else evs)
            if st not in seen:
                seen.add(st)
                dq.append(st)


def registration(evs, F):
    """Return (o_F, A_F) for invocation argument F, or None if not registered.

    F is a frozenset of atoms. A_F is the chronological tuple of later
    fusions whose U0 or V1 contains F, recorded in full.
    """
    F_t = tuple(sorted(F))
    for idx, ev in enumerate(evs):
        if ev[6] == F_t:
            # The origin is (d, (k0, U0), (k1, V1), c). The
            # event's fresh block is retained in the auxiliary log record,
            # but is derivable from U0 | V1 and is not part of Origin.
            o_F = (ev[0], (ev[1], ev[3]), (ev[2], ev[4]), ev[5])
            A_F = tuple(
                e for e in evs[idx + 1:]
                if F <= frozenset(e[3]) or F <= frozenset(e[4])
            )
            return o_F, A_F
    return None
