"""Bounded regression checks for costs, endpoint fibres and the all-R optimum."""

from collections import defaultdict, deque
from math import comb, factorial
from pathlib import Path
import argparse
import json

import core
from fusion_log_arbitrary_start_control import Builder, states_from


def bound(n, t, s):
    d = t - s
    return (3 * n * d + (n - t) * d + comb(d, 2)
            + (3 * n - s) * (s - 1) + n - 1)


def cost_identities(max_n=80):
    count = 0
    for n in range(3, max_n + 1):
        q = lambda s: bound(n, n, s)
        assert 2 * q(1) == 7 * n * (n - 1)
        for s in range(1, n + 1):
            if s < n:
                assert q(s + 1) - q(s) == -(n + s - 1)
            for t in range(s, n + 1):
                h = n - t
                assert q(s) - bound(n, t, s) == 3 * n * h + comb(h, 2)
                assert 2 * bound(n, t, s) <= 7 * n * (n - 1)
                count += 1
    return {"max_n": max_n, "valid_triples_checked": count}


def all_right_log(n):
    return tuple(("d", 0, 1, tuple(range(i)), (i,), 0, tuple(range(i + 1)))
                 for i in range(1, n))


def all_right_word(n):
    return "d" + "".join("p" * (n - j) + "d" + "pd" * j
                         for j in range(1, n - 1)) + "p" * (n - 1)


def shortest(n, expected_log):
    """Unit-cost BFS, rejecting any fusion outside the specified prefix.

    expected_log=None forgets history. It changes the target contract, not
    the raw alphabet or costs. Path counts detect shortest-word uniqueness.
    """
    maps = dict(zip(("p", "d"), core.letters(n)[:2]))
    seed = core.pkey({q: frozenset((q,)) for q in range(n)})
    target = core.pkey({n - 1: frozenset(range(n))})
    start = (seed, 0)
    goal = (target, 0 if expected_log is None else len(expected_log))
    queue = deque([start])
    distance, ways, parent = {start: 0}, {start: 1}, {}
    while queue:
        state = queue.popleft()
        if state == goal:
            word = []
            cursor = goal
            while cursor != start:
                cursor, letter = parent[cursor]
                word.append(letter)
            return {"length": distance[goal], "shortest_word_count": ways[goal],
                    "word": "".join(reversed(word)), "states_discovered": len(distance)}
        placement, index = state
        for letter in ("p", "d"):
            part, event = core.step(core.from_pkey(placement), maps[letter], letter, n)
            next_index = index
            if expected_log is not None and event is not None:
                if index == len(expected_log) or event != expected_log[index]:
                    continue
                next_index += 1
            successor = (core.pkey(part), next_index)
            next_distance = distance[state] + 1
            if successor not in distance:
                distance[successor], ways[successor] = next_distance, ways[state]
                parent[successor] = state, letter
                queue.append(successor)
            elif distance[successor] == next_distance:
                ways[successor] += ways[state]
    raise AssertionError("target not found")


def ledger(n, word):
    part = {q: frozenset((q,)) for q in range(n)}
    maps = dict(zip(("p", "d"), core.letters(n)[:2]))
    expected, events = all_right_log(n), []
    rotations = slides = unchanged = 0
    backslides = defaultdict(int)
    for letter in word:
        successor, event = core.step(part, maps[letter], letter, n)
        if letter == "p":
            rotations += 1
        elif event is not None:
            events.append(event)
        elif part == successor:
            unchanged += 1
        else:
            assert 1 in part and 0 not in part
            if frozenset((0, 1)) <= part[1]:
                backslides[len(part) - 1] += 1
            else:
                slides += 1
        part = successor
    assert tuple(events) == expected
    assert part == {n - 1: frozenset(range(n))}
    B = sum(backslides.values())
    T = (n - 1) * (n - 2) // 2
    Pmin = n * (n - 1) - 1
    R = rotations - Pmin - B
    assert R >= 0
    assert slides == T + sum(m * b for m, b in backslides.items())
    minimum = 3 * n * (n - 1) // 2 - 1
    assert len(word) - minimum == R + sum((m + 2) * b for m, b in backslides.items()) + unchanged
    return {"rotations": rotations, "external_slides": slides,
            "backslides_by_remaining_outside": dict(sorted(backslides.items())),
            "unchanged_defects": unchanged, "rotation_excess": R}


def detour_checks(n):
    cases = []
    canonical = all_right_word(n)
    for label, word in [("canonical", canonical), ("rotation_excess", canonical + "p" * n),
                        ("unchanged_defect", canonical + "d")]:
        cases.append({"case": label, "ledger": ledger(n, word)})
    for remaining in range(n - 1):
        builder = Builder(n, {q: frozenset((q,)) for q in range(n)})
        for event in all_right_log(n):
            builder.fuse(event)
            if len(builder.part) - 1 == remaining:
                carrier = next(block for block in builder.part.values() if {0, 1} <= block)
                outside = sorted((block for block in builder.part.values() if block != carrier),
                                 key=lambda block: min(block))
                builder.place({0: carrier, **{i + 1: block for i, block in enumerate(outside)}})
                builder.emit("pd")
        builder.place({n - 1: frozenset(range(n))})
        result = ledger(n, "".join(builder.word))
        assert result["backslides_by_remaining_outside"].get(remaining, 0) >= 1
        cases.append({"case": f"backslide_with_{remaining}_outside", "ledger": result})
    return cases


def audit(n):
    seed = {q: frozenset((q,)) for q in range(n)}
    endpoint_logs = defaultdict(set)
    log_endpoints = defaultdict(set)
    for placement, log in states_from(n, seed):
        endpoint_logs[placement].add(log)
        log_endpoints[log].add(placement)
    for placement, logs in endpoint_logs.items():
        rank = len(placement)
        assert len(logs) == (factorial(n) if rank == 1 else factorial(n - rank))
    for log, placements in log_endpoints.items():
        rank = n - len(log)
        assert len(placements) == rank * comb(n, rank)
    for rank in range(1, n + 1):
        expected = n if rank == 1 else rank * comb(n, rank) * comb(n, rank)
        assert sum(len(placement) == rank for placement in endpoint_logs) == expected
    exact = shortest(n, all_right_log(n))
    assert exact["word"] == all_right_word(n)
    assert exact["length"] == 3 * n * (n - 1) // 2 - 1
    assert exact["shortest_word_count"] == 1
    endpoint = shortest(n, None)
    assert n - 1 <= endpoint["length"] <= 3 * n - 4
    return {"n": n, "joint_objects": sum(map(len, endpoint_logs.values())),
            "literal_endpoints": len(endpoint_logs), "complete_logs": len(log_endpoints),
            "all_log_and_endpoint_fibres_match": True,
            "all_right_optimum": exact, "history_forgotten_endpoint": endpoint,
            "cost_excess_cases": detour_checks(n)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)
    result = {"status": "PASS_BOUNDED_MATHEMATICAL_CONTROLS",
              "evidence": "BOUNDED_CONSISTENCY_ONLY", "costs": cost_identities(),
              "cases": [audit(n) for n in range(3, 7)],
              "shared_raw_step_implementation": "controls/core.py",
              "kernel_formalization_claimed": False}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "singleton_sizes": len(result["cases"]),
                      "cost_triples": result["costs"]["valid_triples_checked"]}))


if __name__ == "__main__":
    main()
