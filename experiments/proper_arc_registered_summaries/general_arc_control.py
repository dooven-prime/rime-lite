"""Bounded full-log controls for the proper-arc manuscript.

The literal transition model in core.py compares generated summaries at
n=3..6 with the origin, chain, fiber, and total formulas. This is a finite
consistency control, not an all-n proof.
"""

import argparse
from collections import defaultdict
from math import comb

import core

MAX_N = 6


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def arc(n, start, length):
    return frozenset((start + i) % n for i in range(length))


def proper_arcs(n):
    for length in range(2, n):
        for start in range(n):
            yield arc(n, start, length)


def complement_in_source_order(n, F):
    """Return the complement after F's unique proper-arc start."""
    F = frozenset(F)
    for start in range(n):
        if arc(n, start, len(F)) == F:
            return [((start + len(F) + i) % n) for i in range(n - len(F))]
    raise AssertionError(f"not a cyclic arc: {sorted(F)}")


def decode_chain(n, F, code):
    """Decode a 0/L/R word into full selected absorption records."""
    F = frozenset(F)
    r = len(F)
    remaining = complement_in_source_order(n, F)
    carrier = F
    previous = 0
    events = []
    require(len(code) == n - r and set(code) <= set("0LR"),
            "invalid ternary code")
    for checkpoint, side in enumerate(code, 1):
        if side == "0":
            continue
        size = checkpoint - previous
        if side == "R":
            partner, remaining = frozenset(remaining[:size]), remaining[size:]
            u, v = carrier, partner
        else:
            partner, remaining = frozenset(remaining[-size:]), remaining[:-size]
            u, v = partner, carrier
        carrier = carrier | partner
        events.append(("d", 0, 1, tuple(sorted(u)), tuple(sorted(v)), 0,
                       tuple(sorted(carrier))))
        previous = checkpoint
    return tuple(events)


def encode_chain(n, F, chain):
    """Recover the unique ternary word from a full selected chain."""
    F = frozenset(F)
    r = len(F)
    remaining = complement_in_source_order(n, F)
    carrier = F
    previous = 0
    symbols = ["0"] * (n - r)
    for event in chain:
        require(len(event) == 7 and event[0:3] == ("d", 0, 1)
                and event[5] == 0, "unexpected selected event fields")
        u, v = frozenset(event[3]), frozenset(event[4])
        fresh = frozenset(event[6])
        if F <= u and F <= v:
            raise AssertionError("F cannot be contained in both selected parents")
        if F <= u:
            require(u == carrier, "carrier is not the first parent")
            side, partner = "R", v
        elif F <= v:
            require(v == carrier, "carrier is not the second parent")
            side, partner = "L", u
        else:
            raise AssertionError("selected event does not involve F carrier")
        checkpoint = len(fresh) - r
        require(previous < checkpoint <= n - r, "invalid checkpoints")
        size = checkpoint - previous
        if side == "R":
            require(frozenset(remaining[:size]) == partner,
                    "R partner is not the remaining prefix")
            remaining = remaining[size:]
        else:
            require(frozenset(remaining[-size:]) == partner,
                    "L partner is not the remaining suffix")
            remaining = remaining[:-size]
        symbols[checkpoint - 1] = side
        carrier = fresh
        previous = checkpoint
    code = "".join(symbols)
    require(decode_chain(n, F, code) == tuple(chain),
            "ternary decoder is not inverse to the observed chain")
    return code


def per_origin_expected(n, r):
    m = n - r
    return n * (
        comb(n + m - 2, m)
        + 2 * sum(3 ** (b - 1) * comb(n + m - b - 2, m - b)
                  for b in range(1, m + 1))
    )


def total_expected(n, r):
    return (r - 1) * per_origin_expected(n, r)


def fibre_expected(n, F, chain):
    """Return the exact fiber size for one fixed origin and chain."""
    if chain:
        carrier_size = len(chain[-1][6])
    else:
        carrier_size = len(F)
    k = n - carrier_size
    return n * comb(n + k - 2, k)


def collect(n):
    """Collect exact generated summary sets with one BFS."""
    summaries = defaultdict(set)
    state_count = 0
    for pk, events in core.bfs(n):
        state_count += 1
        for event in events:
            F = frozenset(event[6])
            if not 2 <= len(F) < n:
                continue
            registration = core.registration(events, F)
            require(registration is not None, "event-created F did not register")
            origin, chain = registration
            summaries[F].add((pk, origin, chain))
    return summaries, state_count


def check_n(n, verbose=True):
    require(3 <= n <= MAX_N, f"full-log controls are limited to n=3..{MAX_N}")
    summaries, state_count = collect(n)
    expected_F = set(proper_arcs(n))
    require(set(summaries) == expected_F,
            f"registered F mismatch: {set(summaries) ^ expected_F}")

    proper_rows = []
    for F in sorted((F for F in summaries if len(F) < n), key=lambda x: tuple(sorted(x))):
        r = len(F)
        by_origin = defaultdict(set)
        for pk, origin, chain in summaries[F]:
            by_origin[origin].add((pk, chain))
        require(len(by_origin) == r - 1, f"origin count mismatch for F={sorted(F)}")
        expected_chain_count = 3 ** (n - r)
        for origin, fibre_pairs in by_origin.items():
            chains = defaultdict(set)
            for pk, chain in fibre_pairs:
                chains[chain].add(pk)
                code = encode_chain(n, F, chain)
                require(decode_chain(n, F, code) == chain,
                        "observed chain failed code round trip")
            require(set(chains) == {
                decode_chain(n, F, "".join(code))
                for code in _ternary_words(n - r)
            }, f"chain set mismatch for F={sorted(F)}")
            require(len(chains) == expected_chain_count,
                    f"chain count mismatch for F={sorted(F)}")
            for chain, pks in chains.items():
                require(len(pks) == fibre_expected(n, F, chain),
                        f"fiber mismatch for F={sorted(F)} origin={origin}")
                carrier = frozenset(chain[-1][6]) if chain else F
                by_position = defaultdict(set)
                for pk in pks:
                    part = core.from_pkey(pk)
                    positions = [q for q, block in part.items()
                                 if block == carrier]
                    require(len(positions) == 1, "carrier is not uniquely placed")
                    by_position[positions[0]].add(pk)
                require(set(by_position) == set(range(n)),
                        "carrier positions are not all represented")
                expected_at_position = comb(n + n - len(carrier) - 2,
                                            n - len(carrier))
                require(all(len(pks_at_position) == expected_at_position
                             for pks_at_position in by_position.values()),
                        "fixed-position fiber mismatch")
        require(len(summaries[F]) == total_expected(n, r),
                f"total mismatch for F={sorted(F)}")
        proper_rows.append((r, len(summaries[F])))

    if verbose:
        print(f"PASS n={n}: {state_count} log states, "
              f"proper per-F={proper_rows}")
    return {
        "n": n,
        "log_states": state_count,
        "proper_per_F": [{"r": r, "summaries": count}
                         for r, count in proper_rows],
    }


def _ternary_words(length):
    if length == 0:
        yield ""
        return
    for prefix in _ternary_words(length - 1):
        for symbol in "0LR":
            yield prefix + symbol


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=MAX_N)
    args = parser.parse_args(argv)
    if not 3 <= args.max_n <= MAX_N:
        parser.error(f"--max-n must be between 3 and {MAX_N}")
    for n in range(3, args.max_n + 1):
        check_n(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
