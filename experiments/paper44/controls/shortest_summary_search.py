"""Exact raw-word distances for one registered-summary consumer.

The alphabet is strictly ``{"p", "d"}``, with unit cost per letter.  A
search state is ``(P, origin, A_F)`` for a fixed source set ``F``.  Before
registration ``origin`` is ``None`` and ``A_F`` is empty; after registration
the state is exactly the complete consumer-relative summary, apart from the
fixed invocation argument F.  This is therefore a deterministic quotient of
the full history graph for the purpose of computing L_n(Gamma), not a search
on placed partitions alone.

This module is a bounded exact search tool.  It does not introduce inverse
rotations or macro letters.  A predecessor map is retained only when a caller
requests witness words.
"""

from collections import deque, defaultdict
import argparse
import json
from pathlib import Path

import core


RAW_LETTERS = ("p", "d")


def all_right_word(n):
    """Return the explicit all-R construction word W_n for n>=3.

    The product notation is expanded into the literal alphabet {p,d}; no
    inverse rotation or macro letter is introduced.
    """
    if type(n) is not int or n < 3:
        raise ValueError("the all-R construction requires integer n>=3")
    return ("d"
            + "".join("p" * (n - j) + "d" + "pd" * j
                      for j in range(1, n - 1))
            + "p" * (n - 1))


def stirling_second(n, k):
    """Return the Stirling number S(n,k) by its elementary recurrence."""
    if k < 0 or k > n:
        return 0
    row = [0] * (n + 1)
    row[0] = 1
    for size in range(1, n + 1):
        nxt = [0] * (n + 1)
        for blocks in range(1, size + 1):
            nxt[blocks] = row[blocks - 1] + blocks * row[blocks]
        row = nxt
    return row[k]


def falling_factorial(n, k):
    value = 1
    for offset in range(k):
        value *= n - offset
    return value


def placement_partition_count(n):
    """Count all placed partitions of n labelled atoms on n positions."""
    return sum(falling_factorial(n, blocks) * stirling_second(n, blocks)
               for blocks in range(1, n + 1))


def is_source_arc(n, F):
    F = frozenset(F)
    return any(F == frozenset((start + offset) % n for offset in range(len(F)))
               for start in range(n))


def consumer_metadata_upper_bound(n, F):
    """Overcount possible (origin, chain) metadata for one consumer."""
    F = frozenset(F)
    r = len(F)
    if r == n:
        return 1 + n * (n - 1)
    if 2 <= r < n:
        if not is_source_arc(n, F):
            return None
        return 1 + (r - 1) * 3 ** (n - r)
    return 1 if r == 1 else None


def consumer_state_upper_bound(n, F):
    """Finite all-parameter upper bound on retained consumer states."""
    metadata = consumer_metadata_upper_bound(n, F)
    return None if metadata is None else placement_partition_count(n) * metadata


def validate_input(n, F):
    if type(n) is not int or n < 2:
        raise ValueError("require integer n>=2")
    F = frozenset(F)
    if not F or not F <= frozenset(range(n)):
        raise ValueError("F must be a nonempty subset of Z/nZ")
    return F


def source_arc(n, start, size):
    return frozenset((start + offset) % n for offset in range(size))


def all_arc_census(n, *, max_states=None):
    """Exact D_{n,F} table for every proper registered arc and Omega."""
    if type(n) is not int or n < 2:
        raise ValueError("require integer n>=2")
    rows = []
    for size in range(2, n):
        for start in range(n):
            F = source_arc(n, start, size)
            report = registered_records(n, F, max_states=max_states,
                                        retain_predecessors=False)
            maximizers = [row for row in report["records"]
                          if row["distance"] == report["D"]]
            rows.append({
                "n": n, "size": size, "start": start,
                "states": report["states"], "registered": report["registered"],
                "D": report["D"], "maximizers": len(maximizers),
                "maximizer_ranks": sorted({row["rank"] for row in maximizers}),
                "maximizer_chain_lengths": sorted(
                    {row["chain_length"] for row in maximizers}),
            })
    F = frozenset(range(n))
    report = registered_records(n, F, max_states=max_states,
                                retain_predecessors=False)
    maximizers = [row for row in report["records"]
                  if row["distance"] == report["D"]]
    rows.append({
        "n": n, "size": n, "start": None,
        "states": report["states"], "registered": report["registered"],
        "D": report["D"], "maximizers": len(maximizers),
        "maximizer_ranks": sorted({row["rank"] for row in maximizers}),
        "maximizer_chain_lengths": sorted(
            {row["chain_length"] for row in maximizers}),
    })
    return rows


def seed_state(n):
    return (core.pkey({q: frozenset([q]) for q in range(n)}), None, ())


def successor(n, F, state, letter):
    """Apply one raw letter to a consumer-relative search state."""
    if letter not in RAW_LETTERS:
        raise ValueError("only raw letters p and d are allowed")
    pk, origin, chain = state
    maps = core.letters(n)
    f_map = maps[0 if letter == "p" else 1]
    part, event = core.step(core.from_pkey(pk), f_map, letter, n)
    if event is not None:
        fresh = frozenset(event[6])
        if origin is None:
            if fresh == F:
                origin = (event[0], (event[1], event[3]),
                          (event[2], event[4]), event[5])
        elif F <= frozenset(event[3]) or F <= frozenset(event[4]):
            chain = chain + (event,)
    return core.pkey(part), origin, chain


def bfs_distances(n, F, *, max_states=None, retain_predecessors=False):
    """Return exact distances in the complete retained-summary graph.

    The returned dictionary contains registered and pre-registration states.
    ``parent`` is ``None`` unless requested; then it maps every non-start state
    to ``(previous_state, raw_letter)`` along a shortest path.
    """
    F = validate_input(n, F)
    start = seed_state(n)
    distances = {start: 0}
    parent = {} if retain_predecessors else None
    queue = deque([start])
    while queue:
        state = queue.popleft()
        next_distance = distances[state] + 1
        for letter in RAW_LETTERS:
            nxt = successor(n, F, state, letter)
            if nxt in distances:
                continue
            if max_states is not None and len(distances) >= max_states:
                raise RuntimeError("UNRESOLVED_LIMIT: retained-state cap reached")
            distances[nxt] = next_distance
            if parent is not None:
                parent[nxt] = (state, letter)
            queue.append(nxt)
    return distances, parent


def reconstruct_word(state, parent):
    """Reconstruct a shortest raw word from a predecessor map."""
    letters = []
    while state in parent:
        state, letter = parent[state]
        letters.append(letter)
    return "".join(reversed(letters))


def registered_records(n, F, *, max_states=None, retain_predecessors=True):
    """Compute exact registered-summary distances and grouped statistics."""
    F = validate_input(n, F)
    distances, parent = bfs_distances(
        n, F, max_states=max_states, retain_predecessors=retain_predecessors)
    registered = {state: distance for state, distance in distances.items()
                  if state[1] is not None}
    if not registered:
        return {
            "n": n, "F": sorted(F), "states": len(distances),
            "state_upper_bound": consumer_state_upper_bound(n, F),
            "registered": 0, "D": None, "records": [],
            "by_rank": {}, "by_chain_length": {}, "distances": distances,
            "parent": parent,
        }

    records = []
    for state, distance in registered.items():
        pk, origin, chain = state
        records.append({
            "distance": distance,
            "rank": len(pk),
            "fusion_count": n - len(pk),
            "chain_length": len(chain),
            "origin": origin,
            "chain": chain,
            "word": reconstruct_word(state, parent) if parent is not None else None,
            "state": state,
        })
    records.sort(key=lambda row: (row["distance"], row["rank"],
                                  row["chain_length"], repr(row["state"])))
    by_rank = defaultdict(list)
    by_chain_length = defaultdict(list)
    for row in records:
        by_rank[row["rank"]].append(row["distance"])
        by_chain_length[row["chain_length"]].append(row["distance"])

    def summary(rows):
        return {"count": len(rows), "min": min(rows), "max": max(rows)}

    return {
        "n": n,
        "F": sorted(F),
        "states": len(distances),
        "state_upper_bound": consumer_state_upper_bound(n, F),
        "registered": len(registered),
        "D": max(row["distance"] for row in records),
        "records": records,
        "by_rank": {str(rank): summary(rows)
                     for rank, rows in sorted(by_rank.items())},
        "by_chain_length": {str(length): summary(rows)
                             for length, rows in sorted(by_chain_length.items())},
        "distances": distances,
        "parent": parent,
    }


def jsonable_report(report, include_records=True):
    """Drop internal tuple-keyed graph objects and return a JSON report."""
    result = {key: value for key, value in report.items()
              if key not in {"distances", "parent", "records"}}
    if include_records:
        result["records"] = [
            {key: value for key, value in row.items() if key != "state"}
            for row in report["records"]
        ]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--F", nargs="+", type=int,
                        help="source atoms in the fixed consumer F")
    parser.add_argument("--all-arcs", action="store_true",
                        help="compute D_{n,F} for every proper source arc and Omega")
    parser.add_argument("--max-states", type=int, default=None)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-records", action="store_true",
                        help="omit individual summaries from JSON output")
    args = parser.parse_args(argv)
    if args.all_arcs == (args.F is not None):
        parser.error("choose exactly one of --F or --all-arcs")
    if args.all_arcs:
        output_obj = {"n": args.n,
                      "cost_model": "raw alphabet {p,d}, unit letter cost",
                      "rows": all_arc_census(args.n, max_states=args.max_states)}
    else:
        report = registered_records(args.n, frozenset(args.F),
                                    max_states=args.max_states,
                                    retain_predecessors=not args.no_records)
        output_obj = jsonable_report(report, not args.no_records)
    output = json.dumps(output_obj, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
