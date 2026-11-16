"""RSR-2-C layer-allocation controls; reuse the unchanged guarded executor.

The subset search optimizes transferred atom mass, not raw-word length.
These bounded controls do not certify the all-parameter mathematical proofs.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable

from rsr2_model import (
    Packet, State, Word, _normalize_partition, adjacent_fusion_word,
    replay, seed, set_partitions, step,
)


def cyclic_runs(values: Iterable[int]) -> tuple[int, ...]:
    runs: list[int] = []
    for value in values:
        if not runs or runs[-1] != value:
            runs.append(value)
    if len(runs) > 1 and runs[-1] == runs[0]:
        runs.pop()
    return tuple(runs)


def lower_source_order_holds(state: State) -> bool:
    """Check packet intervals AND their physical cyclic order after deletions."""
    owner = {atom: site for site, packet in enumerate(state.layers[0])
             for atom in packet}
    source_order = cyclic_runs(owner[atom] for atom in sorted(owner))
    physical_order = tuple(site for site, packet in enumerate(state.layers[0])
                           if packet)
    if len(source_order) != len(physical_order):
        return False
    if not source_order:
        return True
    return any(source_order == physical_order[cut:] + physical_order[:cut]
               for cut in range(len(physical_order)))


def retention_admissible(target: tuple[Packet, ...], retained: frozenset[int]) -> bool:
    """Whether retained target blocks are intervals in their restricted source cycle.

    target must be a valid partition; indices refer to its supplied block order.
    """
    if not retained.issubset(range(len(target))):
        raise ValueError("retained indices must name target blocks")
    source_labels = sorted((atom, index) for index in retained
                           for atom in target[index])
    runs = cyclic_runs(index for _, index in source_labels)
    return len(runs) == len(retained)


def minimum_transferred_mass(target: tuple[Packet, ...]) -> tuple[int, frozenset[int]]:
    """Exact subset search for the proved mass formula; potentially exponential."""
    best_mass, best_retained = 0, frozenset()
    for mask in range(1 << len(target)):
        retained = frozenset(i for i in range(len(target)) if mask & (1 << i))
        if retention_admissible(target, retained):
            mass = sum(len(target[i]) for i in retained)
            if mass > best_mass:
                best_mass, best_retained = mass, retained
    return sum(map(len, target)) - best_mass, best_retained


def construct_layer_allocation(
    n: int, blocks: Iterable[Iterable[int]], retained: frozenset[int]
) -> tuple[State, Word]:
    """Realize an admissible layer allocation, not a specified literal placement.

    Indices refer to the canonically normalized target partition. Upper blocks
    use partial interleaved singleton loading; lower blocks are fused only
    after all upper atoms have left. No minimum raw-length claim is made.
    """
    target = _normalize_partition(n, blocks)
    if not retention_admissible(target, retained):
        raise ValueError("retained blocks are not restricted-cycle intervals")
    state = seed(n)
    word = []
    loaded = 0
    upper_blocks = tuple(block for i, block in enumerate(target) if i not in retained)
    for block in reversed(upper_blocks):
        suffix: Packet = ()
        for atom in reversed(block):
            route = [("p", 1)] if loaded else []
            site = state.layers[0].index((atom,))
            route += [("p", 0)] * ((-site) % n) + [("v", None)]
            if suffix:
                route.append(("d", 1))
            state = replay(state, route)
            word.extend(route)
            loaded += 1
            suffix = tuple(sorted((atom, *suffix)))
            if state.layers[1][0] != suffix or any(state.layers[1][loaded:]):
                raise AssertionError("partial upper packing invariant failed")

    target_of = {atom: i for i, block in enumerate(target) for atom in block}
    while True:
        packets = tuple(packet for packet in state.layers[0] if packet)
        if len(packets) == len(retained):
            break
        for i, left in enumerate(packets):
            right = packets[(i + 1) % len(packets)]
            if target_of[left[0]] == target_of[right[0]]:
                route = adjacent_fusion_word(state, 0, left, right)
                state = replay(state, route)
                word.extend(route)
                break
        else:
            raise AssertionError("admissible lower refinement has no mergeable pair")

    expected_lower = {target[i] for i in retained}
    if (state.partition != target
            or {packet for packet in state.layers[0] if packet} != expected_lower
            or {packet for packet in state.layers[1] if packet} != set(upper_blocks)):
        raise AssertionError("layer-allocation construction missed its endpoint")
    return state, tuple(word)


def audit_reachable_geometry(n: int) -> dict[str, int]:
    """Exhaust the physical state graph, forgetting logs but retaining all actions.

    Every guarded transition uses rsr2_model.step. This checks arbitrary
    prefusions, whole-packet transfers, and endpoints on both layers.
    """
    actions = (("p", 0), ("p", 1), ("d", 0), ("d", 1), ("v", None))
    initial = seed(n).layers
    seen = {initial}
    queue = deque([initial])
    allocations = set()
    min_mass: dict[tuple[Packet, ...], int] = {}
    edges = 0
    while queue:
        state = State(n, queue.popleft())
        if not lower_source_order_holds(state):
            raise AssertionError("reachable state violates lower source order")
        lower_blocks = frozenset(packet for packet in state.layers[0] if packet)
        allocations.add((state.partition, lower_blocks))
        mass = sum(len(packet) for packet in state.layers[1])
        min_mass[state.partition] = min(mass, min_mass.get(state.partition, n))
        for action in actions:
            if action == ("v", None) and (
                    not state.layers[0][0] or state.layers[1][0]):
                continue
            result = step(state, action)
            edges += 1
            if result.layers not in seen:
                seen.add(result.layers)
                queue.append(result.layers)

    expected_allocations = 0
    for target in set_partitions(n):
        predicted_mass, _ = minimum_transferred_mass(target)
        if min_mass.get(target) != predicted_mass:
            raise AssertionError("mass formula disagrees with exhaustive reachability")
        for mask in range(1 << len(target)):
            retained = frozenset(i for i in range(len(target)) if mask & (1 << i))
            lower_blocks = frozenset(target[i] for i in retained)
            admissible = retention_admissible(target, retained)
            if ((target, lower_blocks) in allocations) != admissible:
                raise AssertionError("allocation criterion disagrees with reachability")
            expected_allocations += int(admissible)
    if expected_allocations != len(allocations):
        raise AssertionError("unaccounted endpoint layer allocation")
    return {"n": n, "physical_states": len(seen), "legal_edges": edges,
            "partitions": len(min_mass), "layer_allocations": len(allocations)}


if __name__ == "__main__":
    import json

    print(json.dumps([audit_reachable_geometry(n) for n in range(2, 5)], indent=2))
