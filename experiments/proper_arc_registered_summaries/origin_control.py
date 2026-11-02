"""Replay the manuscript's explicit proper-arc origin words."""

import hashlib
import json

import core


def origin_word(n, c, r, t):
    if not (3 <= n and 0 <= c < n and 2 <= r < n and 1 <= t < r):
        raise ValueError("require n>=3, 0<=c<n, 2<=r<n, 1<=t<r")

    def slide(j):
        return "p" * ((-j) % n) + "d" + "p" * j

    word = "p" * ((-c) % n)
    for j in range(t - 2, -1, -1):
        word += slide(j)
    for j in range(r - 2, t - 1, -1):
        word += slide(j)
    for j in range(t - 1, 0, -1):
        word += slide(j)
    return word + "d"


def check_origin(n, c, r, t):
    word = origin_word(n, c, r, t)
    p_map, d_map, _kernel, _image = core.letters(n)
    part = {i: frozenset((i,)) for i in range(n)}
    events = []
    F = frozenset((c + i) % n for i in range(r))

    for index, letter in enumerate(word):
        part, event = core.step(part, p_map if letter == "p" else d_map,
                                letter, n)
        blocks = list(part.values())
        if set().union(*blocks) != set(range(n)):
            raise AssertionError("raw step lost a source atom")
        if sum(map(len, blocks)) != n:
            raise AssertionError("raw step duplicated a source atom")
        if event is not None:
            events.append((index, event))
            if index < len(word) - 1 and frozenset(event[6]) == F:
                raise AssertionError("F was registered before the last letter")

    left = tuple(sorted((c + i) % n for i in range(t)))
    right = tuple(sorted((c + i) % n for i in range(t, r)))
    expected_event = ("d", 0, 1, left, right, 0, tuple(sorted(F)))
    expected_part = {0: F}
    expected_part.update({i: frozenset(((c + i) % n,))
                          for i in range(r, n)})
    if len(events) != r - 1 or events[-1] != (len(word) - 1, expected_event):
        raise AssertionError("origin fusion count or final record mismatch")
    if core.pkey(part) != core.pkey(expected_part):
        raise AssertionError("origin word missed the common boundary placement")
    return word


def audit_n(n):
    records = []
    for r in range(2, n):
        for c in range(n):
            for t in range(1, r):
                records.append([c, r, t, check_origin(n, c, r, t)])
    payload = json.dumps(records, separators=(",", ":"), ensure_ascii=True)
    return {
        "n": n,
        "origin_cases": len(records),
        "origin_word_sha256": hashlib.sha256(payload.encode("ascii")).hexdigest(),
    }
