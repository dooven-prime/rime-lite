"""
Local reference implementation of the fixed family studied in this directory.
Paper XL's manuscript remains normative for its definitions and claim scope.

Every experiment script imports from here. Earlier versions each carried their
own copy of the A_F logic, and those copies disagreed: one omitted the
carrier filter entirely, one applied the filter but stored only (k0, k1) per
fusion, which is lossy because the kernel ports are always (0, 1).

Model
-----
Q        = Z/nZ
atoms    Omega = Q (N = n), injective singleton seed iota = identity
p(q)     = q + 1 mod n
d        : rank-(n-1); d(k1) = k0, d(q) = q otherwise.
           kernel class {k0, k1} = {0, 1}; collision image c = k0 = 0
P        : placed partition, occupied position -> nonempty disjoint block
letter a : (f_{a#} P)(q') = union_{q : f_a(q) = q'} P(q)
fusion   : d with P[k0] and P[k1] both nonempty and d(k0) = d(k1) = c
           -> fresh = P[k0] | P[k1] at position c
           -> event o = (a, k0, k1, U0, V1, c, fresh)
F        : fixed nonempty invocation argument
           registered for h iff some actual fusion created exactly F
Gamma    : (P_h, F, o_F, A_F(h))

A_F, defined correctly
----------------------
Paper XL: "the later fusions involving the selected carrier, in chronological
order". A later fusion at index j involves F's carrier iff F's carrier sits at
one of the two kernel ports at that moment, i.e. iff F is a subset of that
fusion's U0 or of its V1. Atoms never split, so F stays inside one packet.

Each retained fusion is recorded in FULL: (a, k0, k1, U0, V1, c, fresh).
Recording only (k0, k1) is lossy and merges distinct Gamma.
"""

from collections import deque

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


def bfs(n, collect="all"):
    """Enumerate the whole log-state space.

    Yields (partition_key, events_tuple). collect is accepted for API symmetry
    with earlier scripts and ignored: callers filter afterwards.
    """
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
            # Paper XL's Origin is (d, (k0, U0), (k1, V1), c).  The
            # event's fresh block is retained in the auxiliary log record,
            # but is derivable from U0 | V1 and is not part of Origin.
            o_F = (ev[0], (ev[1], ev[3]), (ev[2], ev[4]), ev[5])
            A_F = tuple(
                e for e in evs[idx + 1:]
                if F <= frozenset(e[3]) or F <= frozenset(e[4])
            )
            return o_F, A_F
    return None


def collect_exact(n, Fs=None):
    """Per-size sums of |S_F|, using full structural equality.

    Returns {k: sum_{|F|=k} |S_F|}, optionally restricted to Fs.
    Python sets use hashing with equality checks, not truncated digest keys.
    Memory grows with the number of distinct Gamma; no runtime bound is claimed.
    """
    groups = {}
    for pk, evs in bfs(n):
        for ev in evs:
            F_t = ev[6]
            if Fs is not None and frozenset(F_t) not in Fs:
                continue
            reg = registration(evs, frozenset(F_t))
            if reg is None:
                continue
            o_F, A_F = reg
            k = len(F_t)
            s = groups.setdefault(k, set())
            s.add((pk, F_t, o_F, A_F))
    return {k: len(v) for k, v in groups.items()}


def collect_exact_one(n, F):
    """Exact |S_F| for a single F. Returns (count, n_log_states_seen)."""
    gammas = set()
    states = 0
    for pk, evs in bfs(n):
        states += 1
        reg = registration(evs, F)
        if reg is not None:
            o_F, A_F = reg
            gammas.add((pk, tuple(sorted(F)), o_F, A_F))
    return len(gammas), states


if __name__ == "__main__":
    import sys
    for n in range(3, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 6):
        r = collect_exact(n)
        line = "  ".join(f"k={k}: {r[k]}" for k in sorted(r))
        print(f"n={n}  {line}")
