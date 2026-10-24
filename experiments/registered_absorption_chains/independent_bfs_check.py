#!/usr/bin/env python3
"""Bounded raw-action check of registered summaries; no chain decoder imports."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
from json import dumps
from math import comb
from pathlib import Path


State = tuple[tuple[int, ...], tuple[int, int] | None, tuple[tuple[int, int, int], ...]]
F = 0b11


def successors(state: State) -> tuple[State, State]:
    placed, origin, chain = state
    n = len(placed)
    rotated = (placed[-1],) + placed[:-1]
    after = list(placed)
    left, right = after[0], after[1]
    after[0] = left | right
    after[1] = 0
    if left and right:
        if origin is None and left | right == F:
            origin = (left, right)
        elif origin is not None and ((left & F) == F or (right & F) == F):
            chain = chain + ((left, right, left | right),)
    return (rotated, state[1], state[2]), (tuple(after), origin, chain)


def raw_states(n: int) -> set[State]:
    seed: State = (tuple(1 << q for q in range(n)), None, ())
    seen = {seed}
    pending = deque([seed])
    while pending:
        for next_state in successors(pending.popleft()):
            if next_state not in seen:
                seen.add(next_state)
                pending.append(next_state)
    return seen


def expected_total(n: int) -> int:
    if n == 2:
        return 4
    m = n - 2
    return n * (comb(2 * m, m) + 2 * sum(
        3 ** (b - 1) * comb(2 * m - b, m - b) for b in range(1, m + 1)
    ))


def check_n(n: int) -> dict[str, object]:
    states = raw_states(n)
    registered = sorted(state for state in states if state[1] is not None)
    fibers: dict[tuple[tuple[int, int, int], ...], list[State]] = defaultdict(list)
    for state in registered:
        fibers[state[2]].append(state)
    if len(fibers) != 3 ** (n - 2):
        raise ValueError(f"n={n}: chain count mismatch")
    if len(registered) != expected_total(n):
        raise ValueError(f"n={n}: total mismatch")
    if n == 2:
        if len(fibers[()]) != 4 or {state[1] for state in registered} != {(1, 2), (2, 1)}:
            raise ValueError("n=2: origin exception mismatch")
    else:
        for chain, fiber in fibers.items():
            carrier = chain[-1][2] if chain else F
            k = n - carrier.bit_count()
            expected = n * comb(n + k - 2, k)
            if len(fiber) != expected:
                raise ValueError(f"n={n}: fixed-chain fiber mismatch: {chain}")
            if {state[1] for state in fiber} != {(1, 2)}:
                raise ValueError(f"n={n}: origin mismatch")
    chain_lengths = Counter(len(chain) for chain in fibers)
    fiber_weights = Counter((n - (chain[-1][2] if chain else F).bit_count(), len(fiber))
                            for chain, fiber in fibers.items())
    canonical = [
        [list(placed), list(origin), [list(event) for event in chain]]
        for placed, origin, chain in registered
    ]
    digest = sha256(dumps(canonical, separators=(",", ":")).encode("ascii")).hexdigest()
    return {
        "n": n,
        "reachable_states": len(states),
        "registered_summaries": len(registered),
        "expected_total": expected_total(n),
        "selected_chains": len(fibers),
        "chain_length_counts": {str(length): count for length, count in sorted(chain_lengths.items())},
        "fiber_groups": [
            {"outside_atoms": k, "weight_per_chain": weight, "chains": count}
            for (k, weight), count in sorted(fiber_weights.items())
        ],
        "registered_summary_set_sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=7)
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check-result", type=Path)
    args = parser.parse_args()
    if not 2 <= args.max_n <= 7:
        parser.error("--max-n must lie in 2..7 for this bounded control")
    rows = [check_n(n) for n in range(2, args.max_n + 1)]
    result = {
        "schema": "rime.circular-adjacent-collapse.raw-bfs.v1",
        "status": "BOUNDED_COMPUTATIONAL_CONSISTENCY_NOT_PROOF",
        "model": "identity singleton seed; p(q)=q+1 mod n; d(1)=0, d(q)=q otherwise; F={0,1}",
        "method": "BFS of literal placed partitions and ordered registration/absorption records",
        "scope": f"2<=n<={args.max_n}",
        "rows": rows,
    }
    payload = dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    if args.check_result:
        if args.check_result.read_text(encoding="utf-8") != payload:
            raise ValueError(f"saved result differs from raw BFS: {args.check_result}")
    for row in rows:
        print(f"n={row['n']}: {row['selected_chains']} chains, "
              f"{row['registered_summaries']} registered summaries, PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
