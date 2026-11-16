"""Linear antipodal-partition construction over the unchanged RSR-2 executor.

The all-parameter argument is in ANTIPODAL_PARTITION_LINEAR_COST.md. Replay
checks here are bounded controls, not a proof of optimal length or diameter.
"""

from __future__ import annotations

from rsr2_model import Event, Layer, Packet, Word, replay, seed


def antipodal_partition(m: int) -> tuple[Packet, ...]:
    if m < 1:
        raise ValueError("antipodal pairs require m >= 1")
    return tuple((i, i + m) for i in range(m))


def antipodal_linear_word(m: int) -> Word:
    """Use spaced upper storage, then a second pass through the lower ring."""
    antipodal_partition(m)
    p0, p1, v, d1 = ("p", 0), ("p", 1), ("v", None), ("d", 1)
    return ((v,)
            + (p0, p1, p1, v) * (m - 1)
            + (p0, p1, p1, p1, v, d1)
            + (p0, p1, p1, v, d1) * (m - 1))


def antipodal_spaced_endpoint(m: int) -> tuple[Layer, Layer]:
    """Literal representative: pair i is at upper site 2*((i-1) mod m)."""
    target = antipodal_partition(m)
    n = 2 * m
    upper: list[Packet] = [()] * n
    for i, block in enumerate(target):
        upper[2 * ((i - 1) % m)] = block
    return ((),) * n, tuple(upper)


def audit_antipodal_linear_word(m: int) -> dict[str, int]:
    n = 2 * m
    target = antipodal_partition(m)
    word = antipodal_linear_word(m)
    final = replay(seed(n), word)
    if final.layers != antipodal_spaced_endpoint(m) or final.partition != target:
        raise AssertionError("antipodal construction missed the literal endpoint")

    # Structural equality of complete event tuples, not a serialized byte test.
    events = [Event("vertical", None, ((-j) % n,)) for j in range(m)]
    for j in range(m):
        incoming, stored = m - j, (-j) % n
        events.append(Event("vertical", None, (incoming,)))
        events.append(Event("fusion", 1, tuple(sorted((incoming, stored))),
                            (incoming,), (stored,)))
    if final.events != tuple(events):
        raise AssertionError("unexpected fusion or transfer event")

    counts = {"p0": word.count(("p", 0)), "p1": word.count(("p", 1)),
              "d0": word.count(("d", 0)), "d1": word.count(("d", 1)),
              "v": word.count(("v", None))}
    expected = {"p0": 2 * m - 1, "p1": 4 * m - 1,
                "d0": 0, "d1": m, "v": 2 * m}
    if counts != expected or len(word) != 9 * m - 2:
        raise AssertionError("raw-letter counts disagree with the construction")
    return {"m": m, "n": n, "raw_length": len(word), **counts}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-m", type=int, default=32)
    args = parser.parse_args()
    if args.max_m < 1:
        parser.error("--max-m must be at least 1")
    receipts = [audit_antipodal_linear_word(m) for m in range(1, args.max_m + 1)]
    print(json.dumps({"checked_m": [1, args.max_m], "last": receipts[-1]}, indent=2))
