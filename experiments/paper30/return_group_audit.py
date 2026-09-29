#!/usr/bin/env python3
"""Bounded consistency controls for the Paper XXX return-group theorem spine.

The checker uses only Python's standard library. It exhausts the branch
completion parameter on a small fixed range and checks the manuscript's
definitions and consequences directly. The retained output is a bounded
development consistency control, not the proof of an all-n statement.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import permutations
from math import factorial, gcd
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence, TypeAlias


Perm: TypeAlias = dict[int, int]
Partition: TypeAlias = tuple[tuple[int, ...], ...]

SCHEMA = "rime.paper30.general-defect-return-group-audit.v1"
STATUS = "FINITE_SANITY_CHECK_NOT_ALL_N_PROOF"


def compose(left: Mapping[int, int], right: Mapping[int, int]) -> Perm:
    """Return left o right."""

    return {x: left[right[x]] for x in right}


def inverse(perm: Mapping[int, int]) -> Perm:
    result = {value: key for key, value in perm.items()}
    if len(result) != len(perm):
        raise AssertionError("map is not a permutation")
    return result


def cycle_partition(perm: Mapping[int, int]) -> tuple[frozenset[int], ...]:
    unseen = set(perm)
    cycles: list[frozenset[int]] = []
    while unseen:
        start = min(unseen)
        cycle: set[int] = set()
        current = start
        while current not in cycle:
            cycle.add(current)
            unseen.remove(current)
            current = perm[current]
        if current != start:
            raise AssertionError("permutation traversal did not close at its start")
        cycles.append(frozenset(cycle))
    return tuple(sorted(cycles, key=lambda block: (min(block), len(block))))


def orbit_partition(
    carrier: Iterable[int], generators: Sequence[Mapping[int, int]]
) -> tuple[frozenset[int], ...]:
    points = set(carrier)
    moves = list(generators) + [inverse(generator) for generator in generators]
    unseen = set(points)
    orbits: list[frozenset[int]] = []
    while unseen:
        start = min(unseen)
        orbit = {start}
        queue = deque((start,))
        while queue:
            point = queue.popleft()
            for move in moves:
                successor = move[point]
                if successor not in points:
                    raise AssertionError("generator left its declared carrier")
                if successor not in orbit:
                    orbit.add(successor)
                    queue.append(successor)
        unseen -= orbit
        orbits.append(frozenset(orbit))
    return tuple(sorted(orbits, key=lambda block: (min(block), len(block))))


def canonical_partition(blocks: Iterable[Iterable[int]]) -> Partition:
    normalized = [tuple(sorted(block)) for block in blocks]
    return tuple(sorted(normalized, key=lambda block: (block[0], len(block), block)))


def set_partitions(items: Sequence[int]) -> Iterator[Partition]:
    """Generate each set partition once in canonical block order."""

    if not items:
        yield ()
        return
    first = items[0]
    for tail in set_partitions(items[1:]):
        yield canonical_partition(((first,), *tail))
        for index in range(len(tail)):
            blocks = [list(block) for block in tail]
            blocks[index].append(first)
            yield canonical_partition(blocks)


def graph_components(vertex_count: int, edges: Iterable[tuple[int, int]]) -> Partition:
    adjacency = {vertex: set() for vertex in range(vertex_count)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(adjacency)
    components: list[set[int]] = []
    while unseen:
        start = min(unseen)
        component = {start}
        queue = deque((start,))
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in component:
                    component.add(neighbor)
                    queue.append(neighbor)
        unseen -= component
        components.append(component)
    return canonical_partition(components)


def point_partition_as_cycle_partition(
    point_orbits: Iterable[frozenset[int]],
    cycle_index: Mapping[int, int],
) -> Partition:
    blocks = []
    for orbit in point_orbits:
        cycle_ids = {cycle_index[point] for point in orbit}
        blocks.append(cycle_ids)
    return canonical_partition(blocks)


def predicted_cycle_type(n: int, delta: int) -> tuple[int, ...]:
    divisor = gcd(n, delta)
    length = n // divisor
    return tuple(sorted((length - 1, *(length for _ in range(divisor - 1)))))


def punctured_rotation(n: int, delta: int) -> Perm:
    """The punctured rotation psi_Delta on E0 = Q minus {0}."""

    result: Perm = {}
    for point in range(1, n):
        rotated = (point + delta) % n
        result[point] = delta if rotated == 0 else rotated
    if set(result.values()) != set(result):
        raise AssertionError("punctured rotation is not a permutation")
    return result


def branch_defect(n: int, delta: int, values: Sequence[int]) -> dict[str, object]:
    """Construct the defect attached to one branch-completion permutation."""

    q = tuple(range(n))
    k0 = 0
    k1 = delta
    missing = n - 1
    e0 = tuple(point for point in q if point != k0)
    image = tuple(point for point in q if point != missing)
    if sorted(values) != list(e0):
        raise ValueError("branch parameter is not a permutation of E0")
    a = dict(zip(e0, values, strict=True))
    t0 = (k0 - missing) % n
    t1 = (k1 - missing) % n
    b0 = {point: (a[point] - t0) % n for point in e0}
    d = dict(b0)
    d[k0] = b0[k1]

    fibers: dict[int, set[int]] = {}
    for source, target in d.items():
        fibers.setdefault(target, set()).add(source)
    nontrivial = [fiber for fiber in fibers.values() if len(fiber) > 1]
    if set(d.values()) != set(image):
        raise AssertionError("constructed defect has the wrong missing image")
    if nontrivial != [{k0, k1}]:
        raise AssertionError("constructed defect has the wrong binary kernel")

    returns: list[Perm] = []
    for exponent in (t0, t1):
        return_map = {
            point: d[(point + exponent) % n]
            for point in image
        }
        if set(return_map.values()) != set(image):
            raise AssertionError("universal return is not a permutation of D")
        returns.append(return_map)
    g0, g1 = returns
    h = compose(g1, inverse(g0))
    b0_inverse = inverse(b0)
    conjugated_g0 = compose(b0_inverse, compose(g0, b0))
    conjugated_h = compose(b0_inverse, compose(h, b0))
    psi = punctured_rotation(n, delta)
    if conjugated_g0 != a:
        raise AssertionError("branch return did not recover a")
    if conjugated_h != psi:
        raise AssertionError("relative return is not the punctured rotation")

    collision = d[k0]
    collision_coordinate = (collision + t0) % n
    if collision_coordinate != a[k1]:
        raise AssertionError("fixed-collision point condition failed")

    return {
        "a": a,
        "b0": b0,
        "d": d,
        "g0": g0,
        "g1": g1,
        "psi": psi,
        "collision_coordinate": collision_coordinate,
        "e0": e0,
        "image": image,
    }


def gluing_partition(a: Mapping[int, int], psi: Mapping[int, int]) -> Partition:
    cycles = cycle_partition(psi)
    cycle_index = {
        point: index for index, cycle in enumerate(cycles) for point in cycle
    }
    edges = {
        (cycle_index[source], cycle_index[target])
        for source, target in a.items()
        if cycle_index[source] != cycle_index[target]
    }
    return graph_components(len(cycles), edges)


def allowed_fixed_collision_partitions(
    psi: Mapping[int, int], source: int, target: int
) -> set[Partition]:
    cycles = cycle_partition(psi)
    cycle_index = {
        point: index for index, cycle in enumerate(cycles) for point in cycle
    }
    source_cycle = cycle_index[source]
    target_cycle = cycle_index[target]
    source_is_singleton = cycles[source_cycle] == frozenset((source,))
    allowed: set[Partition] = set()
    for partition in set_partitions(tuple(range(len(cycles)))):
        containing_source = next(block for block in partition if source_cycle in block)
        if source_cycle != target_cycle and target_cycle not in containing_source:
            continue
        if target == source and source_is_singleton and containing_source != (source_cycle,):
            continue
        allowed.add(partition)
    return allowed


def audit_delta(n: int, delta: int) -> dict[str, object]:
    e0 = tuple(range(1, n))
    psi = punctured_rotation(n, delta)
    cycles = cycle_partition(psi)
    actual_cycle_type = tuple(sorted(len(cycle) for cycle in cycles))
    expected_cycle_type = predicted_cycle_type(n, delta)
    if actual_cycle_type != expected_cycle_type:
        raise AssertionError("punctured-rotation cycle type mismatch")

    cycle_index = {
        point: index for index, cycle in enumerate(cycles) for point in cycle
    }
    realized_by_target: dict[int, set[Partition]] = {
        target: set() for target in e0
    }
    case_count = 0
    all_partitions: set[Partition] = set()

    for values in permutations(e0):
        case_count += 1
        data = branch_defect(n, delta, values)
        a = data["a"]
        g0 = data["g0"]
        g1 = data["g1"]
        b0 = data["b0"]
        image = data["image"]
        if not isinstance(a, dict):
            raise TypeError("branch parameter must be a permutation dictionary")
        if not isinstance(g0, dict) or not isinstance(g1, dict):
            raise TypeError("universal returns must be permutation dictionaries")
        if not isinstance(b0, dict):
            raise TypeError("inverse branch must be a permutation dictionary")
        if not isinstance(image, tuple):
            raise TypeError("defect image must be an immutable tuple")

        generated_orbits = orbit_partition(e0, (a, psi))
        partition_from_points = point_partition_as_cycle_partition(
            generated_orbits, cycle_index
        )
        partition_from_graph = gluing_partition(a, psi)
        if partition_from_points != partition_from_graph:
            raise AssertionError("cycle gluing does not equal point orbits")

        direct_orbits = orbit_partition(image, (g0, g1))
        b0_inverse = inverse(b0)
        transported = orbit_partition(
            (b0_inverse[point] for point in image),
            (a, psi),
        )
        mapped_direct = tuple(
            sorted(
                (frozenset(b0_inverse[point] for point in orbit) for orbit in direct_orbits),
                key=lambda block: (min(block), len(block)),
            )
        )
        if mapped_direct != transported:
            raise AssertionError("direct return-group orbits disagree after conjugacy")

        target = int(data["collision_coordinate"])
        realized_by_target[target].add(partition_from_graph)
        all_partitions.add(partition_from_graph)

    expected_all = set(set_partitions(tuple(range(len(cycles)))))
    if all_partitions != expected_all:
        raise AssertionError("unrestricted branch fiber missed a cycle partition")

    fixed_partition_counts: dict[str, int] = {}
    for target in e0:
        expected = allowed_fixed_collision_partitions(psi, delta, target)
        actual = realized_by_target[target]
        if actual != expected:
            raise AssertionError(
                f"fixed-collision partition criterion failed at n={n}, "
                f"delta={delta}, target={target}"
            )
        fiber_count = sum(
            1 for values in permutations(e0) if values[e0.index(delta)] == target
        )
        if fiber_count != factorial(n - 2):
            raise AssertionError("fixed-collision fiber cardinality mismatch")
        fixed_partition_counts[str(target)] = len(actual)

    return {
        "delta": delta,
        "gcd": gcd(n, delta),
        "punctured_cycle_type": list(actual_cycle_type),
        "branch_permutations": case_count,
        "cycle_partition_count": len(all_partitions),
        "fixed_collision_fibers": len(e0),
        "fixed_collision_fiber_size": factorial(n - 2),
        "fixed_collision_partition_counts": fixed_partition_counts,
        "branch_completion_exact": True,
        "relative_return_exact": True,
        "cycle_gluing_exact": True,
        "fixed_collision_exact": True,
    }


def build_result(min_n: int, max_n: int) -> dict[str, object]:
    if min_n < 6 or max_n < min_n:
        raise ValueError("expected 6 <= min_n <= max_n")
    records = []
    total_cases = 0
    total_fixed_fibers = 0
    for n in range(min_n, max_n + 1):
        deltas = [audit_delta(n, delta) for delta in range(1, n)]
        total_cases += sum(int(record["branch_permutations"]) for record in deltas)
        total_fixed_fibers += sum(
            int(record["fixed_collision_fibers"]) for record in deltas
        )
        records.append({"n": n, "deltas": deltas})
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {"min_n": min_n, "max_n": max_n},
        "totals": {
            "branch_completion_cases": total_cases,
            "fixed_collision_fibers": total_fixed_fibers,
        },
        "records": records,
        "claim_boundary": [
            "finite replay is not the all-n proof",
            "point orbits on D are not coloring orbits on the section",
            "return-group reachability does not imply Safe-Hit or typed projectability",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=6)
    parser.add_argument("--max-n", type=int, default=8)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_result(args.min_n, args.max_n)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(
            "wrote Paper XXX bounded consistency audit: "
            f"n={args.min_n}..{args.max_n}, "
            f"{result['totals']['branch_completion_cases']} branch cases"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
