#!/usr/bin/env python3
"""Enumerate and audit small complete deterministic synchronizing automata."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import deque
from pathlib import Path
from typing import Iterable, Sequence

Transition = tuple[tuple[int, ...], ...]
Word = tuple[int, ...]


CARRIER_CONTRACT = {
    "contract": "rime.rank-collapse-carrier.v1",
    "base_sets": "Q and alphabet A are finite and nonempty",
    "evaluation": {
        "word_action": "left_to_right",
        "operator_composition": "Eval_Y(uv) = Eval_Y(v) Eval_Y(u)",
        "typing": "anti_homomorphism_to_End(V); homomorphism_to_End(V)^op",
    },
    "depth_domain": "N_0",
    "theorem_spine": [
        "dfa_rank_one_equivalence",
        "kernel_image_monotonicity",
        "fiber_excess_identity",
        "plateau_escape_representation",
        "quotient_internal_composition_bound",
    ],
    "exact_propositions": [
        "transformation_kernel_linear_kernel_bridge",
        "generator_presentation_separation",
        "deterministic_coordinate_support_collapse",
    ],
    "wait_coordinates": [
        "selected_witness_max_wait",
        "selected_witness_max_plateau",
        "structural_next_drop_distance",
        "rank_layer_max_escape_distance",
    ],
    "path_compatible_fields": [
        "compatible_escape_budget",
        "potential_certificate",
    ],
    "classical_benchmark": {
        "name": "Pin-Frankl compression bound",
        "rank_layer_bound": "Omega_r <= binom(n-r+2,2)",
        "cubic_bound": "D_sync <= (n^3-n)/6",
        "ownership": "imported mathematics",
        "source": (
            "https://www.mathnet.ru/php/archive.phtml?"
            "jrnid=rm&option_lang=eng&paperid=10005&wshow=paper"
        ),
    },
    "research_target": (
        "path-compatible potential for transformation-kernel-preserving, "
        "possibly changing image-subset plateaus"
    ),
}


def payload_digest(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compose_maps(first: tuple[int, ...], second: tuple[int, ...]) -> tuple[int, ...]:
    """Return ``second after first`` for state transformations."""
    return tuple(second[first[state]] for state in range(len(first)))


def apply_word(word: Word, transition: Transition, states: Iterable[int]) -> tuple[int, ...]:
    current = tuple(states)
    for letter_index in word:
        current = tuple(transition[letter_index][state] for state in current)
    return current


def transformation_for_word(word: Word, transition: Transition, n: int) -> tuple[int, ...]:
    return apply_word(word, transition, range(n))


def transformation_kernel_partition(
    transformation: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    """Return the fiber partition of a finite-set transformation."""
    fibers: dict[int, list[int]] = {}
    for source, target in enumerate(transformation):
        fibers.setdefault(target, []).append(source)
    return tuple(sorted(tuple(block) for block in fibers.values()))


def rank(transformation: tuple[int, ...]) -> int:
    return len(set(transformation))


def image_subset(transformation: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(set(transformation)))


def reachable_subset_automaton(
    transition: Transition,
    initial: Iterable[int] | None = None,
) -> tuple[
    dict[tuple[int, ...], int],
    dict[tuple[int, ...], Word],
    dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
]:
    """Return the reachable subset orbit, shortest words, and labelled edges."""
    n = len(transition[0])
    start = tuple(range(n)) if initial is None else tuple(sorted(set(initial)))
    distance = {start: 0}
    shortest_words: dict[tuple[int, ...], Word] = {start: tuple()}
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        successors = tuple(
            tuple(sorted({letter[state] for state in current}))
            for letter in transition
        )
        edges[current] = successors
        for letter_index, nxt in enumerate(successors):
            if nxt not in distance:
                distance[nxt] = distance[current] + 1
                shortest_words[nxt] = shortest_words[current] + (letter_index,)
                queue.append(nxt)
    return distance, shortest_words, edges


def subset_rank_carrier(transition: Transition, max_depth: int) -> dict:
    """Exact image-family layers and first-hit depths for rank thresholds."""
    n = len(transition[0])
    full = tuple(range(n))
    distance, shortest_words, _edges = reachable_subset_automaton(transition)

    exact_layers = []
    frontier = {full}
    for depth in range(max_depth + 1):
        exact_layers.append({
            "depth": depth,
            "images": [list(image) for image in sorted(frontier)],
            "minimum_rank": min(map(len, frontier)),
        })
        frontier = {
            tuple(sorted({letter[state] for state in image}))
            for image in frontier
            for letter in transition
        }

    first_hits = []
    for threshold in range(1, n + 1):
        hits = [depth for image, depth in distance.items() if len(image) <= threshold]
        first_hits.append({
            "rank_threshold": threshold,
            "status": "EXACT_FIRST_HIT" if hits else "UNREACHABLE_IN_SUBSET_ORBIT",
            "depth": min(hits) if hits else None,
        })
    return {
        "carrier": "image_rank_collapse",
        "notation": "Img_d[Y]",
        "depth_domain": "N_0",
        "exact_depth_reachable_image_subsets": exact_layers,
        "reachable_subset_orbit": [
            {
                "subset": list(image),
                "minimal_depth": distance[image],
                "shortest_word": list(shortest_words[image]),
            }
            for image in sorted(distance)
        ],
        "reachable_subset_orbit_size": len(distance),
        "first_hit_depth_by_rank_threshold": first_hits,
        "subset_orbit_exhausted": True,
    }


def subset_collapse_depth(transition: Transition, initial: Iterable[int]) -> int | None:
    distance, _shortest_words, _edges = reachable_subset_automaton(
        transition,
        initial,
    )
    hits = [depth for subset, depth in distance.items() if len(subset) == 1]
    return min(hits) if hits else None


def shortest_subset_reset_word(
    transition: Transition,
    initial: Iterable[int] | None = None,
) -> Word | None:
    distance, shortest_words, _edges = reachable_subset_automaton(
        transition,
        initial,
    )
    hits = [subset for subset in distance if len(subset) == 1]
    if not hits:
        return None
    target = min(hits, key=lambda subset: (distance[subset], shortest_words[subset]))
    return shortest_words[target]


def fiber_excess(letter: tuple[int, ...], states: Iterable[int]) -> int:
    state_set = set(states)
    return sum(
        max(len(state_set.intersection(block)) - 1, 0)
        for block in transformation_kernel_partition(letter)
    )


def kernel_refines(
    finer: Sequence[Sequence[int]],
    coarser: Sequence[Sequence[int]],
) -> bool:
    coarse_sets = [set(block) for block in coarser]
    return all(any(set(block) <= coarse for coarse in coarse_sets) for block in finer)


def strongly_connected_components(
    nodes: Sequence[tuple[int, ...]],
    adjacency: dict[tuple[int, ...], set[tuple[int, ...]]],
) -> list[list[tuple[int, ...]]]:
    """Return Kosaraju components in deterministic order."""
    visited: set[tuple[int, ...]] = set()
    finish_order: list[tuple[int, ...]] = []

    def visit(node: tuple[int, ...]) -> None:
        visited.add(node)
        for successor in sorted(adjacency[node]):
            if successor not in visited:
                visit(successor)
        finish_order.append(node)

    for node in sorted(nodes):
        if node not in visited:
            visit(node)

    reverse = {node: set() for node in nodes}
    for node in nodes:
        for successor in adjacency[node]:
            reverse[successor].add(node)

    components = []
    visited.clear()

    def collect(node: tuple[int, ...], component: list[tuple[int, ...]]) -> None:
        visited.add(node)
        component.append(node)
        for predecessor in sorted(reverse[node]):
            if predecessor not in visited:
                collect(predecessor, component)

    for node in reversed(finish_order):
        if node not in visited:
            component: list[tuple[int, ...]] = []
            collect(node, component)
            components.append(sorted(component))
    return sorted(components, key=lambda component: (-len(component), component))


def state_graph_strongly_connected(transition: Transition) -> bool:
    n = len(transition[0])
    for start in range(n):
        reached = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for letter in transition:
                nxt = letter[current]
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append(nxt)
        if len(reached) != n:
            return False
    return True


def collision_pair_set(letter: tuple[int, ...]) -> list[list[int]]:
    return [
        [left, right]
        for left in range(len(letter))
        for right in range(left + 1, len(letter))
        if letter[left] == letter[right]
    ]


def pair_merge_distances(transition: Transition) -> dict[tuple[int, int], int | None]:
    """Return exact directed pair-automaton merge distances."""
    n = len(transition[0])
    result: dict[tuple[int, int], int | None] = {}
    for left in range(n):
        for right in range(left + 1, n):
            start = (left, right)
            distance = {start: 0}
            queue = deque([start])
            merged_at: int | None = None
            while queue and merged_at is None:
                current = queue.popleft()
                for letter in transition:
                    targets = (letter[current[0]], letter[current[1]])
                    if targets[0] == targets[1]:
                        merged_at = distance[current] + 1
                        break
                    successor = tuple(sorted(targets))
                    if successor not in distance:
                        distance[successor] = distance[current] + 1
                        queue.append(successor)
            result[start] = merged_at
    return result


def pair_collision_profile(transition: Transition) -> dict:
    distances = pair_merge_distances(transition)
    return {
        "carrier": "unordered_state_pair_merge",
        "collision_pair_sets": [
            {
                "letter": letter_index,
                "pairs": collision_pair_set(letter),
            }
            for letter_index, letter in enumerate(transition)
        ],
        "pair_merge_distances": [
            {
                "pair": list(pair),
                "distance": distance,
                "mathematical_value": (
                    distance if distance is not None else "infinity"
                ),
            }
            for pair, distance in sorted(distances.items())
        ],
    }


def rank_preserving_escape_profile(transition: Transition) -> dict:
    """Compute intrinsic escape distances in each reachable rank layer."""
    n = len(transition[0])
    distance, _shortest_words, edges = reachable_subset_automaton(transition)
    pair_distances = pair_merge_distances(transition)
    layers = []
    all_finite = True
    for current_rank in range(2, n + 1):
        nodes = sorted(subset for subset in distance if len(subset) == current_rank)
        if not nodes:
            continue
        boundary = {
            subset
            for subset in nodes
            if any(len(successor) < current_rank for successor in edges[subset])
        }
        reverse_edges = {subset: set() for subset in nodes}
        preserving_adjacency = {subset: set() for subset in nodes}
        for subset in nodes:
            for successor in edges[subset]:
                if len(successor) == current_rank:
                    preserving_adjacency[subset].add(successor)
                    reverse_edges[successor].add(subset)
        components = strongly_connected_components(nodes, preserving_adjacency)
        boundary_distance = {subset: 0 for subset in boundary}
        queue = deque(sorted(boundary))
        while queue:
            current = queue.popleft()
            for predecessor in sorted(reverse_edges[current]):
                if predecessor not in boundary_distance:
                    boundary_distance[predecessor] = boundary_distance[current] + 1
                    queue.append(predecessor)
        records = []
        for subset in nodes:
            finite = subset in boundary_distance
            all_finite = all_finite and finite
            escape_word: list[int] | None = None
            escape_target: list[int] | None = None
            if finite:
                current = subset
                escape_word = []
                while boundary_distance[current] > 0:
                    letter_index, successor = min(
                        (
                            (letter_index, successor)
                            for letter_index, successor in enumerate(edges[current])
                            if len(successor) == current_rank
                            and boundary_distance.get(successor)
                            == boundary_distance[current] - 1
                        ),
                        key=lambda item: (item[0], item[1]),
                    )
                    escape_word.append(letter_index)
                    current = successor
                letter_index, successor = min(
                    (
                        (letter_index, successor)
                        for letter_index, successor in enumerate(edges[current])
                        if len(successor) < current_rank
                    ),
                    key=lambda item: (item[0], item[1]),
                )
                escape_word.append(letter_index)
                escape_target = list(successor)
            finite_pair_distances = [
                pair_distances[tuple(sorted((left, right)))]
                for left, right in itertools.combinations(subset, 2)
                if pair_distances[tuple(sorted((left, right)))] is not None
            ]
            minimum_pair_distance = (
                min(finite_pair_distances) if finite_pair_distances else None
            )
            omega = boundary_distance[subset] + 1 if finite else None
            records.append({
                "subset": list(subset),
                "boundary_distance": boundary_distance.get(subset),
                "directed_distance_convention": (
                    "shortest directed path in the rank-preserving graph"
                ),
                "structural_next_drop_distance": omega,
                "mathematical_value": omega if finite else "infinity",
                "shortest_rank_drop_word": escape_word,
                "rank_drop_target_subset": escape_target,
                "minimum_pair_merge_distance": minimum_pair_distance,
                "pair_merge_upper_bound_holds": (
                    finite
                    and minimum_pair_distance is not None
                    and omega <= minimum_pair_distance
                ),
                "omega_symbol": "omega(S)",
                "status": (
                    "EXACT_ESCAPE_DISTANCE"
                    if finite
                    else "EXACT_INFINITY_NO_REACHABLE_STRICT_DROP"
                ),
            })
        finite_omegas = [
            record["structural_next_drop_distance"]
            for record in records
            if record["structural_next_drop_distance"] is not None
        ]
        rank_layer_max = (
            max(finite_omegas) if len(finite_omegas) == len(nodes) else None
        )
        pin_frankl_bound = math.comb(n - current_rank + 2, 2)
        layers.append({
            "rank": current_rank,
            "reachable_subsets": [list(subset) for subset in nodes],
            "rank_preserving_edges": [
                {
                    "source": list(subset),
                    "letter": letter_index,
                    "target": list(successor),
                }
                for subset in nodes
                for letter_index, successor in enumerate(edges[subset])
                if len(successor) == current_rank
            ],
            "collision_exits": [
                {
                    "source": list(subset),
                    "letter": letter_index,
                    "target": list(successor),
                    "fiber_excess": fiber_excess(
                        transition[letter_index],
                        subset,
                    ),
                    "collision_fibers": [
                        sorted(set(subset).intersection(block))
                        for block in transformation_kernel_partition(
                            transition[letter_index]
                        )
                        if len(set(subset).intersection(block)) > 1
                    ],
                }
                for subset in nodes
                for letter_index, successor in enumerate(edges[subset])
                if len(successor) < current_rank
            ],
            "collision_boundary": [list(subset) for subset in sorted(boundary)],
            "rank_preserving_sccs": [
                [list(subset) for subset in component]
                for component in components
            ],
            "largest_rank_preserving_scc_size": max(map(len, components)),
            "escape_records": records,
            "rank_layer_max_escape_distance": rank_layer_max,
            "Omega_r_symbol": f"Omega_{current_rank}",
            "pin_frankl_compression_benchmark": pin_frankl_bound,
            "pin_frankl_benchmark_holds": (
                rank_layer_max is not None
                and rank_layer_max <= pin_frankl_bound
            ),
        })
    synchronizing = any(len(subset) == 1 for subset in distance)
    omega_values = [layer["rank_layer_max_escape_distance"] for layer in layers]
    bound_available = synchronizing and all_finite and all(value is not None for value in omega_values)
    potential_verified = False
    if bound_available:
        omega_by_rank = {
            layer["rank"]: layer["rank_layer_max_escape_distance"]
            for layer in layers
        }

        def potential(subset_rank: int) -> int:
            return sum(
                value
                for layer_rank, value in omega_by_rank.items()
                if layer_rank <= subset_rank
            )

        checks = []
        for layer in layers:
            for record in layer["escape_records"]:
                target = record["rank_drop_target_subset"]
                assert target is not None
                before = potential(layer["rank"])
                after = potential(len(target))
                lhs = record["structural_next_drop_distance"] + after
                record["rank_layer_potential_before"] = before
                record["rank_layer_potential_after"] = after
                record["local_potential_lhs"] = lhs
                record["local_potential_inequality_holds"] = lhs <= before
                checks.append(lhs <= before)
        potential_verified = all(checks)
    coarse_bound = sum(omega_values) if bound_available else None
    pin_frankl_cubic_bound = (n ** 3 - n) // 6
    return {
        "carrier": "rank_preserving_subset_escape",
        "subset_action": "M_Y acts on 2^Q by S . w = delta(S,w)",
        "layers": layers,
        "sync_upper_bound_sum_Omega_r": coarse_bound,
        "compatible_escape_budget": {
            "construction": "rank_layer_max_potential_baseline",
            "value": coarse_bound,
            "path_compatible": potential_verified,
            "not_equivalent_to_cerny_target": True,
        },
        "potential_certificate": {
            "formula": "Phi(S)=sum_{2<=r<=|S|} Omega_r over reachable ranks",
            "local_descent_inequalities_verified": potential_verified,
            "claim_status": "Theorem",
        },
        "classical_compression_benchmark": {
            "owner": "Pin-Frankl compression argument",
            "rank_layer_formula": "Omega_r <= binom(n-r+2,2)",
            "cubic_reset_bound": pin_frankl_cubic_bound,
            "registered_layer_checks_hold": all(
                layer["pin_frankl_benchmark_holds"] for layer in layers
            ) if synchronizing else None,
            "claim_status": "Imported Theorem",
        },
        "bound_status": (
            "EXACT_FINITE_REDUCTION"
            if bound_available
            else "NO_GLOBAL_FINITE_ESCAPE_CERTIFICATE"
        ),
    }


def structural_next_drop_distance(
    transition: Transition,
    initial: Iterable[int],
) -> int | None:
    """Return the intrinsic shortest rank-preserving wait plus one drop."""
    start = tuple(sorted(set(initial)))
    initial_rank = len(start)
    distance = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for letter in transition:
            successor = tuple(sorted({letter[state] for state in current}))
            if len(successor) < initial_rank:
                return distance[current] + 1
            if successor not in distance:
                distance[successor] = distance[current] + 1
                queue.append(successor)
    return None


def prefix_rank_drop_filtration(transition: Transition, word: Word) -> list[dict]:
    """Record strict drops and plateaus along one declared word."""
    n = len(transition[0])
    current = tuple(range(n))
    result = []
    for depth, letter_index in enumerate(word, start=1):
        before_image = image_subset(current)
        before_kernel = transformation_kernel_partition(current)
        letter = transition[letter_index]
        fibers: dict[int, list[int]] = {}
        for state in before_image:
            fibers.setdefault(letter[state], []).append(state)
        nxt = compose_maps(current, letter)
        after_image = image_subset(nxt)
        after_kernel = transformation_kernel_partition(nxt)
        excess = fiber_excess(letter, before_image)
        assert len(before_image) - len(after_image) == excess
        assert kernel_refines(before_kernel, after_kernel)
        assert (before_kernel == after_kernel) == (excess == 0)
        result.append({
            "depth": depth,
            "letter": letter_index,
            "rank_before": len(before_image),
            "rank_after": len(after_image),
            "image_subset_before": list(before_image),
            "image_subset_after": list(after_image),
            "transformation_kernel_partition_before": [
                list(block) for block in before_kernel
            ],
            "transformation_kernel_partition_after": [
                list(block) for block in after_kernel
            ],
            "kernel_coarsening": before_kernel != after_kernel,
            "kernel_unchanged": before_kernel == after_kernel,
            "strict_drop": excess > 0,
            "drop_size": excess,
            "fiber_excess": excess,
            "collision_fibers_on_current_image": [states for states in fibers.values() if len(states) > 1],
        })
        current = nxt
    return result


def shortest_reset_word(transition: Transition) -> Word | None:
    n = len(transition[0])
    identity = tuple(range(n))
    queue: deque[tuple[int, ...]] = deque([identity])
    predecessor: dict[tuple[int, ...], tuple[tuple[int, ...] | None, int | None]] = {identity: (None, None)}
    while queue:
        current = queue.popleft()
        if rank(current) == 1:
            word: list[int] = []
            while predecessor[current][0] is not None:
                parent, letter = predecessor[current]
                assert parent is not None and letter is not None
                word.append(letter)
                current = parent
            return tuple(reversed(word))
        for letter_index, letter in enumerate(transition):
            nxt = compose_maps(current, letter)
            if nxt not in predecessor:
                predecessor[nxt] = (current, letter_index)
                queue.append(nxt)
    return None


def transition_monoid_with_words(transition: Transition) -> dict[tuple[int, ...], Word]:
    n = len(transition[0])
    identity = tuple(range(n))
    monoid = {identity: tuple()}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for letter_index, letter in enumerate(transition):
            nxt = compose_maps(current, letter)
            if nxt not in monoid:
                monoid[nxt] = monoid[current] + (letter_index,)
                queue.append(nxt)
    return monoid


def positive_word_support(
    transition: Transition,
    max_depth: int,
    partition: Sequence[Sequence[int]],
) -> list[list[list[int]]]:
    """Compute the exact-depth full positive-word shadow ``W_d[Y]``."""
    block_of = {state: block for block, states in enumerate(partition) for state in states}
    n = len(transition[0])
    n_blocks = len(partition)
    frontier = {tuple(range(n))}
    levels = []
    for _depth in range(1, max_depth + 1):
        frontier = {compose_maps(current, letter) for current in frontier for letter in transition}
        support = [[0 for _ in range(n_blocks)] for _ in range(n_blocks)]
        for transformation in frontier:
            for source, target in enumerate(transformation):
                support[block_of[target]][block_of[source]] = 1
        levels.append(support)
    return levels


def set_partitions(states: tuple[int, ...]) -> Iterable[tuple[tuple[int, ...], ...]]:
    if not states:
        yield tuple()
        return
    first, *rest = states
    for partition in set_partitions(tuple(rest)):
        yield ((first,),) + partition
        for index in range(len(partition)):
            block = tuple(sorted((first,) + partition[index]))
            yield partition[:index] + (block,) + partition[index + 1 :]


def is_congruence(transition: Transition, partition: Sequence[Sequence[int]]) -> bool:
    block_of = {state: block for block, states in enumerate(partition) for state in states}
    return all(
        len({block_of[letter[state]] for state in block}) == 1
        for letter in transition
        for block in partition
    )


def quotient_profiles(transition: Transition) -> list[dict]:
    n = len(transition[0])
    transition_monoid = transition_monoid_with_words(transition)
    profiles = []
    for partition in set_partitions(tuple(range(n))):
        if not is_congruence(transition, partition):
            continue
        block_of = {state: block for block, states in enumerate(partition) for state in states}
        quotient = tuple(
            tuple(block_of[letter[block[0]]] for block in partition)
            for letter in transition
        )
        quotient_reset = shortest_reset_word(quotient)
        internal_depths = [subset_collapse_depth(transition, block) for block in partition]
        uniform_internal_depth = max(internal_depths) if all(depth is not None for depth in internal_depths) else None
        reached_subset = (
            None
            if quotient_reset is None
            else image_subset(
                transformation_for_word(quotient_reset, transition, n)
            )
        )
        target_block = (
            None
            if reached_subset is None
            else next(
                block
                for block in partition
                if set(reached_subset) <= set(block)
            )
        )
        reached_subset_internal_depth = (
            None
            if reached_subset is None
            else subset_collapse_depth(transition, reached_subset)
        )
        target_candidates = []
        for transformation, word in transition_monoid.items():
            quotient_transformation = tuple(
                block_of[transformation[block[0]]]
                for block in partition
            )
            if len(set(quotient_transformation)) != 1:
                continue
            candidate_subset = image_subset(transformation)
            candidate_internal_depth = subset_collapse_depth(
                transition,
                candidate_subset,
            )
            if candidate_internal_depth is None:
                continue
            target_candidates.append({
                "bound": len(word) + candidate_internal_depth,
                "quotient_reset_word": list(word),
                "quotient_reset_depth": len(word),
                "reached_subset": list(candidate_subset),
                "reached_subset_internal_depth": candidate_internal_depth,
            })
        best_target = min(
            target_candidates,
            key=lambda item: (
                item["bound"],
                item["quotient_reset_depth"],
                item["quotient_reset_word"],
                item["reached_subset"],
            ),
            default=None,
        )
        fixed_uniform_bound = (
            None
            if quotient_reset is None or uniform_internal_depth is None
            else len(quotient_reset) + uniform_internal_depth
        )
        profiles.append({
            "partition": [list(block) for block in partition],
            "state_count": len(partition),
            "transition": [list(letter) for letter in quotient],
            "selected_shortest_quotient_reset_depth": None if quotient_reset is None else len(quotient_reset),
            "selected_shortest_quotient_reset_word": None if quotient_reset is None else list(quotient_reset),
            "selected_reached_subset": None if reached_subset is None else list(reached_subset),
            "selected_target_class": None if target_block is None else list(target_block),
            "selected_reached_subset_internal_depth": reached_subset_internal_depth,
            "selected_shortest_witness_composition_bound": (
                None
                if quotient_reset is None or reached_subset_internal_depth is None
                else len(quotient_reset) + reached_subset_internal_depth
            ),
            "internal_compression_depths": [
                {"block": list(block), "depth": depth, "status": "EXACT_FIRST_HIT" if depth is not None else "UNREACHABLE_IN_SUBSET_ORBIT"}
                for block, depth in zip(partition, internal_depths)
            ],
            "uniform_internal_compression_depth": uniform_internal_depth,
            "fixed_congruence_uniform_bound": fixed_uniform_bound,
            "fixed_congruence_target_specific_bound": (
                None if best_target is None else best_target["bound"]
            ),
            "target_specific_bound_semantics": (
                "exact but self-referential unless the quotient-reset witness "
                "class is restricted; a full reset word is always eligible"
            ),
            "target_specific_optimizing_witness": best_target,
        })
    return sorted(profiles, key=lambda profile: (profile["state_count"], profile["partition"]))


def incidence_profile(transition: Transition) -> list[dict]:
    profile = []
    for first_index, first in enumerate(transition):
        for second_index, second in enumerate(transition):
            product = compose_maps(first, second)
            excess = fiber_excess(second, image_subset(first))
            assert rank(first) - rank(product) == excess
            profile.append({
                "word": [first_index, second_index],
                "input_rank": rank(first),
                "product_rank": rank(product),
                "fiber_excess": excess,
                "strict_rank_drop": excess > 0,
            })
    return profile


def direct_support(transition: Transition, partition: Sequence[Sequence[int]]) -> list[list[list[int]]]:
    block_of = {state: block for block, states in enumerate(partition) for state in states}
    result: list[list[list[int]]] = []
    for letter in transition:
        matrix = [[0 for _ in partition] for _ in partition]
        for source, target in enumerate(letter):
            matrix[block_of[target]][block_of[source]] = 1
        result.append(matrix)
    return result


def operator_blocks(transition: Transition, partition: Sequence[Sequence[int]]) -> list[list[list[list[list[int]]]]]:
    result = []
    for letter in transition:
        letter_blocks = []
        for target_states in partition:
            target_index = {state: row for row, state in enumerate(target_states)}
            row_blocks = []
            for source_states in partition:
                block = [[0 for _ in source_states] for _ in target_states]
                for column, source in enumerate(source_states):
                    target = letter[source]
                    if target in target_index:
                        block[target_index[target]][column] = 1
                row_blocks.append(block)
            letter_blocks.append(row_blocks)
        result.append(letter_blocks)
    return result


def block_support_path(
    transition: Transition,
    max_depth: int,
    partition: Sequence[Sequence[int]],
) -> list[list[list[int]]]:
    """Compute exact-length Boolean paths in the aggregated direct graph.

    This is ``Path_d(R_1[Y])``. It is not routed projected-product support and
    can strictly overestimate that support for nonsingleton sectors.
    """
    block_of = {state: block for block, states in enumerate(partition) for state in states}
    n_blocks = len(partition)
    direct = [[False for _ in range(n_blocks)] for _ in range(n_blocks)]
    for letter in transition:
        for source, target in enumerate(letter):
            direct[block_of[target]][block_of[source]] = True
    paths = direct
    levels = [[[int(value) for value in row] for row in paths]]
    for _depth in range(2, max_depth + 1):
        nxt = [[False for _ in range(n_blocks)] for _ in range(n_blocks)]
        for target in range(n_blocks):
            for source in range(n_blocks):
                nxt[target][source] = any(
                    direct[target][mid] and paths[mid][source]
                    for mid in range(n_blocks)
                )
        paths = nxt
        levels.append([[int(value) for value in row] for row in paths])
    return levels


def routed_support(
    transition: Transition,
    max_depth: int,
    partition: Sequence[Sequence[int]],
) -> list[list[list[int]]]:
    """Compute the exact-depth routed-product shadow ``Route_d[Y]``.

    A deterministic state map gives each basis state a unique intermediate
    sector at every letter. Tracking actual state trajectories therefore
    computes routed support without replacing projected products by graph
    powers. After aggregation over all routes, this shadow agrees with full
    positive-word support for this declared deterministic realization.
    """
    block_of = {
        state: block
        for block, states in enumerate(partition)
        for state in states
    }
    n_blocks = len(partition)
    frontier = {(state, state) for state in range(len(transition[0]))}
    levels = []
    for _depth in range(1, max_depth + 1):
        frontier = {
            (source, letter[current])
            for source, current in frontier
            for letter in transition
        }
        support = [[0 for _ in range(n_blocks)] for _ in range(n_blocks)]
        for source, target in frontier:
            support[block_of[target]][block_of[source]] = 1
        levels.append(support)
    return levels


def canonical_transition(transition: Transition) -> Transition:
    n = len(transition[0])
    best: Transition | None = None
    for permutation in itertools.permutations(range(n)):
        inverse = {old: new for new, old in enumerate(permutation)}
        relabelled = tuple(
            tuple(inverse[letter[permutation[old]]] for old in range(n))
            for letter in transition
        )
        if best is None or relabelled < best:
            best = relabelled
    assert best is not None
    return best


def enumerate_isomorphism_classes(n: int, alphabet: int) -> list[Transition]:
    seen: set[Transition] = set()
    for flat in itertools.product(range(n), repeat=n * alphabet):
        transition = tuple(tuple(flat[letter * n : (letter + 1) * n]) for letter in range(alphabet))
        seen.add(canonical_transition(transition))
    return sorted(seen)


def audit_automaton(
    transition: Transition,
    max_word_depth: int = 4,
    partition: Sequence[Sequence[int]] | None = None,
) -> dict:
    if max_word_depth < 1:
        raise ValueError("max_word_depth must be at least one")
    n = len(transition[0])
    if partition is None:
        partition = tuple((state,) for state in range(n))
    monoid = transition_monoid_with_words(transition)
    reset_word = shortest_reset_word(transition)
    witness = None
    if reset_word is not None:
        transformation = transformation_for_word(reset_word, transition, n)
        witness = {
            "word": list(reset_word),
            "map": list(transformation),
            "image_subset": list(image_subset(transformation)),
            "transformation_kernel_partition": [
                list(block)
                for block in transformation_kernel_partition(transformation)
            ],
            "rank": rank(transformation),
        }
    paths = block_support_path(transition, max_word_depth, partition)
    routed = routed_support(transition, max_word_depth, partition)
    words = positive_word_support(transition, max_word_depth, partition)
    singleton_coordinate_partition = all(len(block) == 1 for block in partition)
    return {
        "transition": [list(letter) for letter in transition],
        "state_count": n,
        "alphabet_size": len(transition),
        "partition": [list(block) for block in partition],
        "operator_blocks": operator_blocks(transition, partition),
        "direct_support": direct_support(transition, partition),
        "block_support_path": paths,
        "routed_support": routed,
        "positive_word_support": words,
        "deterministic_route_word_agreement": routed == words,
        "deterministic_coordinate_support_collapse": {
            "applicable": singleton_coordinate_partition,
            "path_route_word_equal": (
                paths == routed == words
                if singleton_coordinate_partition
                else None
            ),
        },
        "kernel_type_bridge": {
            "finite_set_object": "KerPart(t_w)",
            "linear_object": "ker_C(Y_w)",
            "linear_kernel_span": "span_C{e_x-e_y : x~_w y}",
            "rank_identity": (
                "rank(Y_w)=#KerPart(t_w)=|im(t_w)|"
            ),
        },
        "transition_monoid_size": len(monoid),
        "transition_monoid": [
            {
                "shortest_word": list(word),
                "minimal_depth": len(word),
                "map": list(transformation),
                "image_subset": list(image_subset(transformation)),
                "transformation_kernel_partition": [
                    list(block)
                    for block in transformation_kernel_partition(transformation)
                ],
                "rank": rank(transformation),
            }
            for transformation, word in sorted(monoid.items(), key=lambda item: (len(item[1]), item[1]))
        ],
        "transition_monoid_rank_histogram": {str(r): sum(rank(element) == r for element in monoid) for r in range(1, n + 1) if any(rank(element) == r for element in monoid)},
        "sector_quotients": quotient_profiles(transition),
        "rank_incidence_profile": incidence_profile(transition),
        "pair_collision_profile": pair_collision_profile(transition),
        "rank_collapse": subset_rank_carrier(transition, max_word_depth),
        "rank_preserving_escape": rank_preserving_escape_profile(transition),
        "reset": {"is_synchronizing": reset_word is not None, "shortest_word": None if reset_word is None else list(reset_word), "shortest_length": None if reset_word is None else len(reset_word)},
        "witness_transformation": witness,
        "reset_rank_drop_filtration": None if reset_word is None else prefix_rank_drop_filtration(transition, reset_word),
    }


def feature_row(record: dict, n: int) -> dict:
    histogram = record["transition_monoid_rank_histogram"]
    letter_ranks = [rank(tuple(letter)) for letter in record["transition"]]
    proper_quotients = [q for q in record["sector_quotients"] if 1 < q["state_count"] < n]
    uniform_quotient_bounds = [
        q["fixed_congruence_uniform_bound"]
        for q in proper_quotients
        if q["fixed_congruence_uniform_bound"] is not None
    ]
    target_quotient_bounds = [
        q["fixed_congruence_target_specific_bound"]
        for q in proper_quotients
        if q["fixed_congruence_target_specific_bound"] is not None
    ]
    shortest_witness_bounds = [
        q["selected_shortest_witness_composition_bound"]
        for q in proper_quotients
        if q["selected_shortest_witness_composition_bound"] is not None
    ]
    quotient_depths = [
        q["selected_shortest_quotient_reset_depth"]
        for q in proper_quotients
        if q["selected_shortest_quotient_reset_depth"] is not None
    ]
    filtration = record["reset_rank_drop_filtration"] or []
    strict_depths = [step["depth"] for step in filtration if step["strict_drop"]]
    previous = 0
    rank_drop_waits = []
    for depth in strict_depths:
        rank_drop_waits.append(depth - previous)
        previous = depth
    largest_rank_scc = max(
        (
            layer["largest_rank_preserving_scc_size"]
            for layer in record["rank_preserving_escape"]["layers"]
        ),
        default=0,
    )
    strongly_connected = state_graph_strongly_connected(
        tuple(tuple(letter) for letter in record["transition"])
    )
    hard_core_candidate = (
        strongly_connected
        and not proper_quotients
        and min(letter_ranks) == n - 1
        and n - min(letter_ranks) == 1
    )
    return {
        "automaton_id": record["id"],
        "state_count": n,
        "alphabet_size": len(record["transition"]),
        "reset_length": record["reset"]["shortest_length"],
        "transition_monoid_size": record["transition_monoid_size"],
        "nonconstant_monoid_elements": sum(count for value, count in histogram.items() if int(value) > 1),
        "minimum_letter_rank": min(letter_ranks),
        "maximum_letter_rank_drop": n - min(letter_ranks),
        "rank_drop_incidence_count": sum(item["fiber_excess"] > 0 for item in record["rank_incidence_profile"]),
        "nontrivial_congruence_quotient_count": len(proper_quotients),
        "minimum_nontrivial_quotient_size": min(
            (q["state_count"] for q in proper_quotients),
            default=None,
        ),
        "minimum_quotient_reset_depth": min(quotient_depths, default=None),
        "best_nontrivial_congruence_uniform_bound": min(
            uniform_quotient_bounds,
            default=None,
        ),
        "best_nontrivial_congruence_target_specific_bound": min(
            target_quotient_bounds,
            default=None,
        ),
        "best_nontrivial_congruence_shortest_witness_bound": min(
            shortest_witness_bounds,
            default=None,
        ),
        "selected_witness_strict_rank_drop_count": len(strict_depths),
        "selected_witness_strict_rank_drop_depths": strict_depths,
        "selected_witness_first_rank_drop_depth": strict_depths[0] if strict_depths else None,
        "selected_witness_max_wait": max(rank_drop_waits, default=None),
        "selected_witness_max_plateau": max(
            (wait - 1 for wait in rank_drop_waits),
            default=None,
        ),
        "rank_layer_max_escape_distance": {
            str(layer["rank"]): layer["rank_layer_max_escape_distance"]
            for layer in record["rank_preserving_escape"]["layers"]
        },
        "maximum_rank_layer_escape_distance": max(
            (
                layer["rank_layer_max_escape_distance"]
                for layer in record["rank_preserving_escape"]["layers"]
                if layer["rank_layer_max_escape_distance"] is not None
            ),
            default=None,
        ),
        "sum_rank_layer_escape_bound": record["rank_preserving_escape"]["sync_upper_bound_sum_Omega_r"],
        "compatible_escape_budget": record["rank_preserving_escape"][
            "compatible_escape_budget"
        ]["value"],
        "potential_certificate_verified": record["rank_preserving_escape"][
            "potential_certificate"
        ]["local_descent_inequalities_verified"],
        "largest_rank_preserving_scc_size": largest_rank_scc,
        "state_graph_strongly_connected": strongly_connected,
        "simple_hard_core_candidate": hard_core_candidate,
    }


def build_registry(n: int, alphabet: int, max_word_depth: int) -> dict:
    records = []
    for index, transition in enumerate(enumerate_isomorphism_classes(n, alphabet)):
        records.append({"id": f"dfa-n{n}-k{alphabet}-{index:05d}", **audit_automaton(transition, max_word_depth)})
    synchronizing = [r for r in records if r["reset"]["is_synchronizing"]]
    feature_rows = [feature_row(record, n) for record in synchronizing]
    candidates = [
        {
            "statement": "reset_length <= (n-1)^2",
            "holds_for_all_registered_synchronizing_automata": all(row["reset_length"] <= (n - 1) ** 2 for row in feature_rows),
            "equality_case_count": sum(row["reset_length"] == (n - 1) ** 2 for row in feature_rows),
            "claim_status": "Research Program",
            "candidate_kind": "conjecture",
        },
        {
            "statement": "reset_length <= number_of_nonconstant_transition_monoid_elements",
            "holds_for_all_registered_synchronizing_automata": all(row["reset_length"] <= row["nonconstant_monoid_elements"] for row in feature_rows),
            "equality_case_count": sum(row["reset_length"] == row["nonconstant_monoid_elements"] for row in feature_rows),
            "claim_status": "Research Program",
            "candidate_kind": "proof_target",
        },
    ]
    payload = {
        "schema": "rime.synchronizing-automata.v2",
        "carrier_contract": CARRIER_CONTRACT,
        "scope": {
            "state_count": n,
            "alphabet_size": alphabet,
            "max_word_depth": max_word_depth,
            "isomorphism": "state relabelling; letter labels fixed",
        },
        "enumeration": {
            "labelled_tables": n ** (n * alphabet),
            "isomorphism_classes": len(records),
            "synchronizing_classes": len(synchronizing),
        },
        "records": records,
        "analysis": {
            "feature_rows": feature_rows,
            "candidate_inequalities": candidates,
        },
        "producer": {
            "script": "experiments/paper23/registry.py",
            "script_sha256": file_digest(Path(__file__)),
        },
        "claim_boundary": "Finite complete enumeration and exact BFS/monoid certificates for registered DFAs; candidate inequalities are Research Program items, not general theorems, and no general Cerny theorem is claimed.",
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, default=3)
    parser.add_argument("--alphabet", type=int, default=2)
    parser.add_argument("--max-word-depth", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.states < 1 or args.alphabet < 1 or args.max_word_depth < 1:
        raise SystemExit(
            "states, alphabet, and max-word-depth must be positive"
        )
    payload = build_registry(args.states, args.alphabet, args.max_word_depth)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"classes": payload["enumeration"]["isomorphism_classes"], "synchronizing": sum(r["reset"]["is_synchronizing"] for r in payload["records"])}, indent=2))


if __name__ == "__main__":
    main()
