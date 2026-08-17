#!/usr/bin/env python3
"""Exact finite carriers for Fuchsian-quotient Schreier actions.

The module contains no surface Laplacian, Hecke, moduli, or reporting layer.
All certificate arithmetic uses Python integers or ``fractions.Fraction``.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


Permutation = tuple[int, ...]
Word = tuple[int, ...]
Matrix = list[list[int]]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def content_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_prime(value: int) -> bool:
    if isinstance(value, bool) or not isinstance(value, int) or value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def validate_permutation(permutation: Permutation) -> None:
    if tuple(sorted(permutation)) != tuple(range(len(permutation))):
        raise ValueError("value is not a permutation of its state set")


def compose_maps(first: Permutation, second: Permutation) -> Permutation:
    """Return ``second after first`` for left-to-right word evaluation."""

    if len(first) != len(second):
        raise ValueError("permutations must have the same degree")
    return tuple(second[first[state]] for state in range(len(first)))


def inverse_permutation(permutation: Permutation) -> Permutation:
    validate_permutation(permutation)
    inverse = [0] * len(permutation)
    for source, target in enumerate(permutation):
        inverse[target] = source
    return tuple(inverse)


def permutation_power(permutation: Permutation, exponent: int) -> Permutation:
    if exponent < 0:
        return permutation_power(inverse_permutation(permutation), -exponent)
    result = tuple(range(len(permutation)))
    factor = permutation
    while exponent:
        if exponent & 1:
            result = compose_maps(result, factor)
        factor = compose_maps(factor, factor)
        exponent //= 2
    return result


def permutation_order(permutation: Permutation) -> int:
    validate_permutation(permutation)
    seen = [False] * len(permutation)
    order = 1
    for start in range(len(permutation)):
        if seen[start]:
            continue
        length = 0
        current = start
        while not seen[current]:
            seen[current] = True
            length += 1
            current = permutation[current]
        order = math.lcm(order, length)
    return order


def permutation_matrix(permutation: Permutation) -> Matrix:
    validate_permutation(permutation)
    matrix = [[0 for _ in permutation] for _ in permutation]
    for source, target in enumerate(permutation):
        matrix[target][source] = 1
    return matrix


def matrix_sum(matrices: Sequence[Matrix]) -> Matrix:
    if not matrices:
        raise ValueError("at least one matrix is required")
    size = len(matrices[0])
    if any(len(matrix) != size or any(len(row) != size for row in matrix) for matrix in matrices):
        raise ValueError("matrices must be square and have a common size")
    return [
        [sum(matrix[row][column] for matrix in matrices) for column in range(size)]
        for row in range(size)
    ]


def graph_laplacian(permutations: Sequence[Permutation]) -> tuple[Matrix, Matrix]:
    matrices = [permutation_matrix(permutation) for permutation in permutations]
    adjacency = matrix_sum(matrices)
    size = len(adjacency)
    laplacian = [
        [len(permutations) * int(row == column) - adjacency[row][column] for column in range(size)]
        for row in range(size)
    ]
    return adjacency, laplacian


def matrix_digest(matrix: Matrix) -> str:
    return content_digest(matrix)


def rational_rank(matrix: Matrix) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    column_count = len(rows[0]) if rows else 0
    for column in range(column_count):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank or not rows[index][column]:
                continue
            factor = rows[index][column]
            rows[index] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(rows[index], rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def bareiss_determinant(matrix: Matrix) -> int:
    values = [row[:] for row in matrix]
    size = len(values)
    if any(len(row) != size for row in values):
        raise ValueError("determinant requires a square matrix")
    if size == 0:
        return 1
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        if values[pivot_index][pivot_index] == 0:
            swap = next(
                (
                    row
                    for row in range(pivot_index + 1, size)
                    if values[row][pivot_index]
                ),
                None,
            )
            if swap is None:
                return 0
            values[pivot_index], values[swap] = values[swap], values[pivot_index]
            sign *= -1
        pivot = values[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = (
                    values[row][column] * pivot
                    - values[row][pivot_index] * values[pivot_index][column]
                )
                if numerator % previous:
                    raise ArithmeticError("Bareiss division was not exact")
                values[row][column] = numerator // previous
        previous = pivot
        for row in range(pivot_index + 1, size):
            values[row][pivot_index] = 0
    return sign * values[-1][-1]


def characteristic_polynomial(matrix: Matrix) -> list[int]:
    """Return descending monic coefficients using exact Newton identities."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("characteristic polynomial requires a square matrix")

    def multiply(left: Matrix, right: Matrix) -> Matrix:
        return [
            [
                sum(left[row][index] * right[index][column] for index in range(size))
                for column in range(size)
            ]
            for row in range(size)
        ]

    identity = [
        [int(row == column) for column in range(size)] for row in range(size)
    ]
    current = identity
    traces = []
    for _ in range(size):
        current = multiply(current, matrix)
        traces.append(sum(current[index][index] for index in range(size)))
    coefficients = [1]
    for degree in range(1, size + 1):
        numerator = -sum(
            coefficients[degree - power] * traces[power - 1]
            for power in range(1, degree + 1)
        )
        if numerator % degree:
            raise ArithmeticError("Newton identity did not divide exactly")
        coefficients.append(numerator // degree)
    return coefficients


def exact_laplacian_certificate(permutations: Sequence[Permutation]) -> dict:
    adjacency, laplacian = graph_laplacian(permutations)
    size = len(laplacian)
    rank = rational_rank(laplacian)
    cofactor = [row[:-1] for row in laplacian[:-1]]
    return {
        "definition": "L=sum_a(I-P_a) for the declared symmetric labelled alphabet",
        "arithmetic": "Python integer matrices, Fraction rank, Bareiss determinant, exact Newton identities",
        "adjacency_sha256": matrix_digest(adjacency),
        "laplacian_sha256": matrix_digest(laplacian),
        "symmetric": adjacency == [list(row) for row in zip(*adjacency)],
        "zero_row_sums": all(sum(row) == 0 for row in laplacian),
        "exact_rational_rank": rank,
        "zero_eigenvalue_multiplicity": size - rank,
        "spanning_tree_count": bareiss_determinant(cofactor),
        "characteristic_polynomial_coefficients_descending": characteristic_polynomial(
            laplacian
        ),
    }


def mobius_permutation(p: int, matrix: tuple[int, int, int, int]) -> Permutation:
    if not is_prime(p):
        raise ValueError("p must be prime")
    a, b, c, d = (entry % p for entry in matrix)
    if (a * d - b * c) % p == 0:
        raise ValueError("Mobius matrix must be invertible modulo p")
    infinity = p
    targets = []
    for state in range(p + 1):
        if state == infinity:
            targets.append(infinity if c == 0 else a * pow(c, -1, p) % p)
            continue
        numerator = (a * state + b) % p
        denominator = (c * state + d) % p
        targets.append(
            infinity
            if denominator == 0
            else numerator * pow(denominator, -1, p) % p
        )
    permutation = tuple(targets)
    validate_permutation(permutation)
    return permutation


def modular_generators(p: int) -> dict[str, Permutation]:
    s = mobius_permutation(p, (0, -1, 1, 0))
    t = mobius_permutation(p, (1, 1, 0, 1))
    r = compose_maps(t, s)
    generators = {"S": s, "R": r, "R_inv": inverse_permutation(r), "T": t}
    identity = tuple(range(p + 1))
    if permutation_power(s, 2) != identity or permutation_power(r, 3) != identity:
        raise AssertionError("modular presentation relation failed")
    if compose_maps(r, s) != t:
        raise AssertionError("declared T relation failed")
    return generators


def permutation_orbits(permutation: Permutation) -> tuple[tuple[int, ...], ...]:
    validate_permutation(permutation)
    unseen = set(range(len(permutation)))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = []
        current = start
        while current not in orbit:
            orbit.append(current)
            unseen.discard(current)
            current = permutation[current]
        orbits.append(tuple(sorted(orbit)))
    return tuple(sorted(orbits, key=lambda orbit: (len(orbit), orbit)))


def validate_sectors(sectors: Sequence[Sequence[int]], state_count: int) -> None:
    flattened = [state for sector in sectors for state in sector]
    if sorted(flattened) != list(range(state_count)):
        raise ValueError("sectors must be a disjoint complete state partition")
    if any(not sector for sector in sectors):
        raise ValueError("sectors must be nonempty")


def sector_index(sectors: Sequence[Sequence[int]], state_count: int) -> dict[int, int]:
    validate_sectors(sectors, state_count)
    return {
        state: index for index, sector in enumerate(sectors) for state in sector
    }


def block_rank_matrix(
    permutation: Permutation, sectors: Sequence[Sequence[int]]
) -> list[list[int]]:
    labels = sector_index(sectors, len(permutation))
    ranks = [[0 for _ in sectors] for _ in sectors]
    for source, target in enumerate(permutation):
        ranks[labels[target]][labels[source]] += 1
    return ranks


def support_matrix(
    transformations: Iterable[Permutation], sectors: Sequence[Sequence[int]]
) -> list[list[int]]:
    transformations = tuple(transformations)
    if not transformations:
        raise ValueError("at least one transformation is required")
    labels = sector_index(sectors, len(transformations[0]))
    support = [[0 for _ in sectors] for _ in sectors]
    for transformation in transformations:
        validate_permutation(transformation)
        for source, target in enumerate(transformation):
            support[labels[target]][labels[source]] = 1
    return support


def labelled_direct_support(
    named_generators: Sequence[tuple[str, Permutation]],
    sectors: Sequence[Sequence[int]],
) -> dict:
    return {
        name: {
            "support_target_by_source": support_matrix((permutation,), sectors),
            "block_rank_target_by_source": block_rank_matrix(permutation, sectors),
        }
        for name, permutation in named_generators
    }


def boolean_path_layers(
    direct: Sequence[Sequence[int]], max_depth: int
) -> list[dict]:
    if max_depth < 1:
        raise ValueError("max_depth must be positive")
    base = [[bool(value) for value in row] for row in direct]
    current = [row[:] for row in base]
    layers = []
    for depth in range(1, max_depth + 1):
        layers.append(
            {
                "depth": depth,
                "support_target_by_source": [
                    [int(value) for value in row] for row in current
                ],
            }
        )
        current = [
            [
                any(
                    base[target][middle] and current[middle][source]
                    for middle in range(len(base))
                )
                for source in range(len(base))
            ]
            for target in range(len(base))
        ]
    return layers


def exact_word_layers(
    generators: Sequence[Permutation],
    sectors: Sequence[Sequence[int]],
    max_depth: int,
) -> list[dict]:
    if not generators:
        raise ValueError("a word alphabet is required")
    frontier = {tuple(range(len(generators[0])))}
    layers = []
    for depth in range(1, max_depth + 1):
        frontier = {
            compose_maps(transformation, generator)
            for transformation in frontier
            for generator in generators
        }
        layers.append(
            {
                "depth": depth,
                "distinct_transformations": len(frontier),
                "support_target_by_source": support_matrix(frontier, sectors),
            }
        )
    return layers


def generated_group(
    generators: Sequence[Permutation],
) -> dict[Permutation, Word]:
    if not generators:
        raise ValueError("a generating alphabet is required")
    identity = tuple(range(len(generators[0])))
    shortest_words = {identity: tuple()}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for index, generator in enumerate(generators):
            nxt = compose_maps(current, generator)
            if nxt not in shortest_words:
                shortest_words[nxt] = shortest_words[current] + (index,)
                queue.append(nxt)
    return shortest_words


def generated_group_positive_words(
    generators: Sequence[Permutation],
) -> dict[Permutation, Word]:
    """Return shortest nonempty positive words for every image element."""

    if not generators:
        raise ValueError("a generating alphabet is required")
    shortest_words: dict[Permutation, Word] = {}
    queue: deque[Permutation] = deque()
    for index, generator in enumerate(generators):
        if generator not in shortest_words:
            shortest_words[generator] = (index,)
            queue.append(generator)
    while queue:
        current = queue.popleft()
        for index, generator in enumerate(generators):
            nxt = compose_maps(current, generator)
            if nxt not in shortest_words:
                shortest_words[nxt] = shortest_words[current] + (index,)
                queue.append(nxt)
    identity = tuple(range(len(generators[0])))
    if identity not in shortest_words:
        raise AssertionError("finite permutation image lacks a positive identity word")
    return shortest_words


def exact_word_depth(
    named_generators: Sequence[tuple[str, Permutation]],
    sectors: Sequence[Sequence[int]],
) -> dict:
    generators = tuple(permutation for _, permutation in named_generators)
    closure = generated_group_positive_words(generators)
    ordered = sorted(closure.items(), key=lambda item: (len(item[1]), item[1]))
    labels = sector_index(sectors, len(generators[0]))
    depths: list[list[int | None]] = [
        [None for _ in sectors] for _ in sectors
    ]
    witnesses = []
    for transformation, word in ordered:
        for source, target in enumerate(transformation):
            source_sector = labels[source]
            target_sector = labels[target]
            if depths[target_sector][source_sector] is not None:
                continue
            depths[target_sector][source_sector] = len(word)
            witnesses.append(
                {
                    "target_sector": target_sector,
                    "source_sector": source_sector,
                    "depth": len(word),
                    "word_left_to_right": [
                        named_generators[index][0] for index in word
                    ],
                    "source_state": source,
                    "target_state": target,
                }
            )
    return {
        "depth_convention": "minimum positive-word length d>=1 over the declared labelled alphabet; the empty word is excluded",
        "evaluation_convention": "a1...ad acts left-to-right, so the matrix product is P_ad...P_a1",
        "depth_matrix_target_by_source": depths,
        "first_hit_witnesses": sorted(
            witnesses,
            key=lambda item: (item["target_sector"], item["source_sector"]),
        ),
        "saturation": {
            "status": "EXACT_FINITE_GROUP_CLOSURE",
            "transformation_count": len(closure),
            "shortest_nonempty_identity_word_length": len(
                closure[tuple(range(len(generators[0])))]
            ),
        },
    }


def route_length_two_profile(
    named_generators: Sequence[tuple[str, Permutation]],
    sectors: Sequence[Sequence[int]],
) -> dict:
    state_count = len(named_generators[0][1])
    validate_sectors(sectors, state_count)
    sector_sets = [set(sector) for sector in sectors]
    pair_profiles = []
    total_candidates = 0
    total_nonzero = 0
    for first_name, first in named_generators:
        for second_name, second in named_generators:
            candidates = []
            nonzero = []
            for target_index, target in enumerate(sector_sets):
                for middle_index, middle in enumerate(sector_sets):
                    for source_index, source in enumerate(sector_sets):
                        first_block = any(first[state] in middle for state in source)
                        second_block = any(
                            second[state] in target for state in middle
                        )
                        if not (first_block and second_block):
                            continue
                        route = [target_index, middle_index, source_index]
                        candidates.append(route)
                        if any(
                            first[state] in middle
                            and second[first[state]] in target
                            for state in source
                        ):
                            nonzero.append(route)
            zero = [route for route in candidates if route not in nonzero]
            pair_profiles.append(
                {
                    "word_left_to_right": [first_name, second_name],
                    "operator_product": f"P_{second_name} P_{first_name}",
                    "candidate_routes_target_middle_source": candidates,
                    "nonzero_routes_target_middle_source": nonzero,
                    "zero_routes_target_middle_source": zero,
                }
            )
            total_candidates += len(candidates)
            total_nonzero += len(nonzero)
    return {
        "route_semantics": "Q_target P_second Q_middle P_first Q_source for the displayed left-to-right word [first,second]",
        "ordered_letter_pair_profiles": pair_profiles,
        "supported_route_candidate_count": total_candidates,
        "nonzero_routed_product_count": total_nonzero,
        "zero_routed_product_count": total_candidates - total_nonzero,
    }


def simple_support_graph_metrics(permutations: Sequence[Permutation]) -> dict:
    state_count = len(permutations[0])
    neighbors = [set() for _ in range(state_count)]
    for permutation in permutations:
        for source, target in enumerate(permutation):
            if source != target:
                neighbors[source].add(target)
                neighbors[target].add(source)
    all_distances = []
    for start in range(state_count):
        distances = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for target in sorted(neighbors[current]):
                if target not in distances:
                    distances[target] = distances[current] + 1
                    queue.append(target)
        if len(distances) != state_count:
            return {
                "connected": False,
                "diameter": None,
                "girth": None,
                "edge_count": sum(map(len, neighbors)) // 2,
            }
        all_distances.extend(distances.values())
    girth = None
    for start in range(state_count):
        distances = {start: 0}
        parents: dict[int, int | None] = {start: None}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for target in neighbors[current]:
                if target not in distances:
                    distances[target] = distances[current] + 1
                    parents[target] = current
                    queue.append(target)
                elif parents[current] != target:
                    candidate = distances[current] + distances[target] + 1
                    girth = candidate if girth is None else min(girth, candidate)
    return {
        "connected": True,
        "diameter": max(all_distances),
        "girth": girth,
        "edge_count": sum(map(len, neighbors)) // 2,
    }


def carrier_observables(
    named_generators: Sequence[tuple[str, Permutation]],
    sectors: Sequence[Sequence[int]],
    max_word_depth: int,
) -> dict:
    generators = tuple(permutation for _, permutation in named_generators)
    direct_by_letter = labelled_direct_support(named_generators, sectors)
    direct = support_matrix(generators, sectors)
    return {
        "labelled_direct_support": direct_by_letter,
        "aggregate_direct_support_target_by_source": direct,
        "boolean_path_layers": boolean_path_layers(direct, max_word_depth),
        "route_length_two": route_length_two_profile(named_generators, sectors),
        "positive_word_layers": exact_word_layers(
            generators, sectors, max_word_depth
        ),
        "exact_first_hit_word_depth": exact_word_depth(
            named_generators, sectors
        ),
    }
