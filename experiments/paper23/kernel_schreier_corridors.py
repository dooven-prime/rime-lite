#!/usr/bin/env python3
"""Certificates for inverse-closed permutation-core kernel corridors.

The structural class studied here has a nonempty inverse-closed alphabet of
permutations and only defect-one nonpermutation letters.  Clean exit requires
every defect-one letter on a reachable unit Schreier orbit either to drop rank
or to fix the current image subset.  The weaker letterwise simulation gate
also permits a rank-preserving step when one permutation generator has the
same subset action.  Either gate normalizes the plateau to the permutation
Schreier orbit, where unit waiting is distance to its cover boundary plus one.
For a commuting-involution core the certificate records its elementary-
abelian rank and the resulting multi-generator diameter bound.
"""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from math import comb
from typing import Any

from pair_hitting import _rank_escape_witness
from registry import (
    Transition,
    compose_maps,
    rank,
    reachable_subset_automaton,
    shortest_subset_reset_word,
)


def inverse_permutation(letter: tuple[int, ...]) -> tuple[int, ...] | None:
    """Return the inverse map, or ``None`` when ``letter`` is not bijective."""
    if len(set(letter)) != len(letter):
        return None
    inverse = [0] * len(letter)
    for source, target in enumerate(letter):
        inverse[target] = source
    return tuple(inverse)


def _elementary_abelian_core_profile(
    generators: list[tuple[int, ...]],
    state_count: int,
) -> tuple[int, int]:
    """Return the F2-rank and order of a commuting involution core.

    The caller verifies that the distinct nonidentity generators commute and
    square to the identity.  Adding a generator outside the current subgroup
    then doubles its order, so the selected generators form an F2-basis.
    """
    identity = tuple(range(state_count))
    subgroup = {identity}
    basis_size = 0
    for generator in generators:
        if generator in subgroup:
            continue
        old_subgroup = tuple(subgroup)
        subgroup.update(
            compose_maps(element, generator)
            for element in old_subgroup
        )
        basis_size += 1
    return basis_size, len(subgroup)


def _subset_image(
    subset: tuple[int, ...],
    letter: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(sorted({letter[state] for state in subset}))


def _binary_wait_normal_form(
    transition: Transition,
    reset_word: tuple[int, ...],
    permutation_letter: int,
    defect_one_letter: int,
) -> dict[str, Any]:
    """Normalize a shortest binary escape and expose its wait number."""
    n = len(transition[0])
    current = tuple(range(n))
    normalized: list[int] = []
    for letter_index in reset_word:
        target = _subset_image(current, transition[letter_index])
        replacement: tuple[int, ...]
        if (
            letter_index == defect_one_letter
            and len(target) == len(current)
        ):
            permutation_target = _subset_image(
                current,
                transition[permutation_letter],
            )
            if target == current:
                replacement = tuple()
            elif target == permutation_target:
                replacement = (permutation_letter,)
            else:
                raise AssertionError(
                    "binary wait normalization used outside its simulation gate"
                )
        else:
            replacement = (letter_index,)
        for replacement_letter in replacement:
            normalized.append(replacement_letter)
            current = _subset_image(
                current,
                transition[replacement_letter],
            )
        if current != target:
            raise AssertionError("local Schreier replacement changed the subset")

    eta_by_rank: dict[str, int] = {}
    cursor = 0
    current = tuple(range(n))
    drop_count = 0
    shape_verified = True
    for rank_value in range(n, 1, -1):
        eta = 0
        if (
            rank_value < n
            and cursor < len(normalized)
            and normalized[cursor] == permutation_letter
        ):
            eta = 1
            current = _subset_image(
                current,
                transition[permutation_letter],
            )
            cursor += 1
        if rank_value < n:
            eta_by_rank[str(rank_value)] = eta
        if (
            cursor >= len(normalized)
            or normalized[cursor] != defect_one_letter
        ):
            shape_verified = False
            break
        target = _subset_image(current, transition[defect_one_letter])
        if len(current) != rank_value or len(target) != rank_value - 1:
            shape_verified = False
            break
        current = target
        cursor += 1
        drop_count += 1
    shape_verified = (
        shape_verified
        and cursor == len(normalized)
        and len(current) == 1
    )
    wait_number = sum(eta_by_rank.values())
    identity_holds = (
        shape_verified
        and len(normalized) == len(reset_word)
        and len(reset_word) == n - 1 + wait_number
    )
    return {
        "normalized_shortest_word": normalized,
        "eta_by_source_rank": eta_by_rank,
        "genuine_permutation_wait_number": wait_number,
        "defect_one_drop_count": drop_count,
        "normal_form_shape_verified": shape_verified,
        "reset_depth_identity_holds": identity_holds,
        "at_most_one_wait": wait_number <= 1,
    }


def _defect_one_functional_graph_profile(
    letter: tuple[int, ...],
) -> dict[str, Any]:
    """Return the unique tail/cycle decomposition of a defect-one map."""
    n = len(letter)
    fibers: dict[int, list[int]] = {state: [] for state in range(n)}
    for source, target in enumerate(letter):
        fibers[target].append(source)
    missing = [state for state, preimage in fibers.items() if not preimage]
    branching = [
        (state, preimage)
        for state, preimage in fibers.items()
        if len(preimage) == 2
    ]
    if len(missing) != 1 or len(branching) != 1:
        raise AssertionError("expected one missing state and one double fiber")
    collision_target, collision_pair = branching[0]
    path: list[int] = []
    position: dict[int, int] = {}
    current = missing[0]
    while current not in position:
        position[current] = len(path)
        path.append(current)
        current = letter[current]
    cycle_start = position[current]
    tail = path[:cycle_start]
    distinguished_cycle = path[cycle_start:]
    if not tail or current != collision_target:
        raise AssertionError("defect-one tail does not enter at the double fiber")
    cycle_vertices = sorted(set(range(n)).difference(tail))
    return {
        "missing_state": missing[0],
        "collision_target": collision_target,
        "collision_pair": sorted(collision_pair),
        "tail": tail,
        "tail_endpoint": tail[-1],
        "distinguished_cycle": distinguished_cycle,
        "cycle_vertices": cycle_vertices,
        "tail_size": len(tail),
        "cycle_vertex_count": len(cycle_vertices),
    }


def _word_subset_trace(
    transition: Transition,
    word: list[int],
) -> list[dict[str, Any]]:
    n = len(transition[0])
    current = tuple(range(n))
    rows = []
    for depth, letter_index in enumerate(word, start=1):
        target = _subset_image(current, transition[letter_index])
        rows.append({
            "depth": depth,
            "letter": letter_index,
            "source_subset": list(current),
            "target_subset": list(target),
            "source_holes": sorted(set(range(n)).difference(current)),
            "target_holes": sorted(set(range(n)).difference(target)),
            "strict_rank_drop": len(target) == len(current) - 1,
        })
        current = target
    return rows


def _permutation_path_to_boundary(
    start: tuple[int, ...],
    rank_value: int,
    permutation_letters: list[int],
    defect_one_letters: list[int],
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
) -> tuple[list[int], int, tuple[int, ...]] | None:
    distance = {start: 0}
    words = {start: tuple()}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        exits = [
            letter
            for letter in defect_one_letters
            if len(edges[current][letter]) < rank_value
        ]
        if exits:
            terminal = min(exits)
            return list(words[current]), terminal, current
        for letter in permutation_letters:
            target = edges[current][letter]
            if target not in distance:
                distance[target] = distance[current] + 1
                words[target] = words[current] + (letter,)
                queue.append(target)
    return None


def _permutation_orbit(
    start: tuple[int, ...],
    permutation_letters: list[int],
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
) -> tuple[tuple[int, ...], ...]:
    orbit = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for letter in permutation_letters:
            target = edges[current][letter]
            if target not in orbit:
                orbit.add(target)
                queue.append(target)
    return tuple(sorted(orbit))


def _orbit_profile(
    orbit: tuple[tuple[int, ...], ...],
    rank_value: int,
    permutation_letters: list[int],
    defect_one_letters: list[int],
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
) -> dict[str, Any]:
    boundary = {
        subset: [
            letter
            for letter in defect_one_letters
            if len(edges[subset][letter]) < rank_value
        ]
        for subset in orbit
    }
    boundary = {subset: letters for subset, letters in boundary.items() if letters}
    clean_failures = []
    schreier_simulation_failures = []
    cover_failures = []
    for subset in orbit:
        one_step_schreier_targets = {
            subset,
            *(edges[subset][letter] for letter in permutation_letters),
        }
        for letter in defect_one_letters:
            target = edges[subset][letter]
            if len(target) == rank_value and target != subset:
                clean_failures.append({
                    "subset": list(subset),
                    "letter": letter,
                    "target": list(target),
                })
            if (
                len(target) == rank_value
                and target not in one_step_schreier_targets
            ):
                schreier_simulation_failures.append({
                    "subset": list(subset),
                    "letter": letter,
                    "target": list(target),
                })
            if len(target) < rank_value and len(target) != rank_value - 1:
                cover_failures.append({
                    "subset": list(subset),
                    "letter": letter,
                    "target": list(target),
                })
    distances = []
    for subset in orbit:
        witness = _permutation_path_to_boundary(
            subset,
            rank_value,
            permutation_letters,
            defect_one_letters,
            edges,
        )
        distances.append(None if witness is None else len(witness[0]))
    return {
        "rank": rank_value,
        "orbit": [list(subset) for subset in orbit],
        "orbit_size": len(orbit),
        "cover_boundary": [
            {"subset": list(subset), "defect_one_letters": letters}
            for subset, letters in sorted(boundary.items())
        ],
        "cover_boundary_size": len(boundary),
        "clean_exit_on_orbit": not clean_failures,
        "clean_exit_failures": clean_failures,
        "letterwise_schreier_simulation_on_orbit": (
            not schreier_simulation_failures
        ),
        "schreier_simulation_failures": schreier_simulation_failures,
        "cover_only_exit_verified": not cover_failures,
        "cover_exit_failures": cover_failures,
        "directed_distance_to_cover_boundary": [
            {
                "subset": list(subset),
                "distance": distance,
            }
            for subset, distance in zip(orbit, distances)
        ],
        "directed_cover_radius": (
            None if any(value is None for value in distances)
            else max(distances, default=0)
        ),
    }


def kernel_schreier_corridor_certificate(
    transition: Transition,
) -> dict[str, Any]:
    """Return the exact permutation-core/cover-boundary class certificate."""
    n = len(transition[0])
    letter_ranks = [rank(letter) for letter in transition]
    permutation_letters = [
        index for index, value in enumerate(letter_ranks) if value == n
    ]
    defect_one_letters = [
        index for index, value in enumerate(letter_ranks) if value == n - 1
    ]
    higher_defect_letters = [
        index for index, value in enumerate(letter_ranks) if value < n - 1
    ]
    inverse_indices: dict[str, int | None] = {}
    for index in permutation_letters:
        inverse = inverse_permutation(transition[index])
        inverse_indices[str(index)] = next(
            (
                candidate
                for candidate in permutation_letters
                if transition[candidate] == inverse
            ),
            None,
        )
    inverse_closed = all(value is not None for value in inverse_indices.values())
    permutation_core_nonempty = bool(permutation_letters)
    nonpermutation_letters = [
        index for index, value in enumerate(letter_ranks) if value < n
    ]
    all_nonpermutation_defect_one = (
        bool(nonpermutation_letters)
        and not higher_defect_letters
        and set(nonpermutation_letters) == set(defect_one_letters)
    )
    distinct_nonidentity_permutations = sorted({
        transition[index]
        for index in permutation_letters
        if transition[index] != tuple(range(n))
    })
    permutation_core_all_involutions = all(
        compose_maps(letter, letter) == tuple(range(n))
        for letter in distinct_nonidentity_permutations
    )
    permutation_core_pairwise_commuting = all(
        compose_maps(left, right) == compose_maps(right, left)
        for left in distinct_nonidentity_permutations
        for right in distinct_nonidentity_permutations
    )
    if (
        permutation_core_all_involutions
        and permutation_core_pairwise_commuting
    ):
        elementary_abelian_rank, elementary_abelian_order = (
            _elementary_abelian_core_profile(
                distinct_nonidentity_permutations,
                n,
            )
        )
    else:
        elementary_abelian_rank = None
        elementary_abelian_order = None

    _distance, _reaching_words, edges = reachable_subset_automaton(transition)
    orbit_cache: dict[tuple[tuple[int, ...], ...], dict[str, Any]] = {}
    state_rows = []
    finite_escape_all = True
    for subset in sorted(edges, key=lambda value: (len(value), value)):
        if len(subset) <= 1:
            continue
        escape = _rank_escape_witness(transition, edges, subset)
        if escape is None:
            finite_escape_all = False
            continue
        if escape["best_shortest_escape_excess"] != 1:
            continue
        orbit = _permutation_orbit(subset, permutation_letters, edges)
        if orbit not in orbit_cache:
            orbit_cache[orbit] = _orbit_profile(
                orbit,
                len(subset),
                permutation_letters,
                defect_one_letters,
                edges,
            )
            if elementary_abelian_rank is not None:
                orbit_size = orbit_cache[orbit]["orbit_size"]
                if orbit_size & (orbit_size - 1):
                    raise AssertionError(
                        "elementary-abelian orbit size is not a power of two"
                    )
                quotient_rank = orbit_size.bit_length() - 1
                subset_count_rank_bound = (
                    comb(n, len(subset)).bit_length() - 1
                )
                orbit_cache[orbit]["schreier_quotient_rank"] = quotient_rank
                orbit_cache[orbit]["schreier_quotient_rank_upper_bound"] = min(
                    elementary_abelian_rank,
                    subset_count_rank_bound,
                )
                orbit_cache[orbit]["quotient_rank_size_bound_holds"] = (
                    quotient_rank <= elementary_abelian_rank
                    and quotient_rank <= subset_count_rank_bound
                )
                cover_radius = orbit_cache[orbit]["directed_cover_radius"]
                orbit_cache[orbit]["quotient_rank_radius_bound_holds"] = (
                    None if cover_radius is None
                    else cover_radius <= quotient_rank
                )
            else:
                orbit_cache[orbit]["schreier_quotient_rank"] = None
                orbit_cache[orbit]["schreier_quotient_rank_upper_bound"] = None
                orbit_cache[orbit]["quotient_rank_size_bound_holds"] = None
                orbit_cache[orbit]["quotient_rank_radius_bound_holds"] = None
        orbit_profile = orbit_cache[orbit]
        core_witness = _permutation_path_to_boundary(
            subset,
            len(subset),
            permutation_letters,
            defect_one_letters,
            edges,
        )
        core_escape_length = (
            None if core_witness is None else len(core_witness[0]) + 1
        )
        state_rows.append({
            "subset": list(subset),
            "rank": len(subset),
            "omega": escape["segment_length"],
            "e_star": escape["best_shortest_escape_excess"],
            "permutation_orbit_size": orbit_profile["orbit_size"],
            "schreier_quotient_rank": orbit_profile[
                "schreier_quotient_rank"
            ],
            "schreier_quotient_rank_upper_bound": orbit_profile[
                "schreier_quotient_rank_upper_bound"
            ],
            "cover_boundary_size": orbit_profile["cover_boundary_size"],
            "directed_cover_radius": orbit_profile["directed_cover_radius"],
            "clean_exit_on_orbit": orbit_profile["clean_exit_on_orbit"],
            "letterwise_schreier_simulation_on_orbit": orbit_profile[
                "letterwise_schreier_simulation_on_orbit"
            ],
            "core_escape_length": core_escape_length,
            "shortest_core_normal_form_holds": (
                core_escape_length == escape["segment_length"]
            ),
            "core_witness": (
                None if core_witness is None else {
                    "permutation_prefix": core_witness[0],
                    "terminal_defect_one_letter": core_witness[1],
                    "terminal_source": list(core_witness[2]),
                }
            ),
        })

    structural_base = (
        permutation_core_nonempty
        and inverse_closed
        and all_nonpermutation_defect_one
    )
    clean_exit = all(row["clean_exit_on_orbit"] for row in state_rows)
    schreier_simulable = all(
        orbit["letterwise_schreier_simulation_on_orbit"]
        for orbit in orbit_cache.values()
    )
    normal_form = all(
        row["shortest_core_normal_form_holds"] for row in state_rows
    )
    clean_class = structural_base and finite_escape_all and clean_exit
    schreier_simulable_class = (
        structural_base and finite_escape_all and schreier_simulable
    )
    normal_form_class = structural_base and finite_escape_all and normal_form
    clean_theorem_failures = [
        row
        for row in state_rows
        if row["clean_exit_on_orbit"]
        and not row["shortest_core_normal_form_holds"]
    ]
    schreier_simulation_theorem_failures = [
        row
        for row in state_rows
        if row["letterwise_schreier_simulation_on_orbit"]
        and not row["shortest_core_normal_form_holds"]
    ]

    u_by_rank = {
        rank_value: max(
            (
                row["omega"]
                for row in state_rows
                if row["rank"] == rank_value
            ),
            default=0,
        )
        for rank_value in range(2, n + 1)
    }
    unit_tail = {}
    running = 0
    for index in range(n, 1, -1):
        running = max(running, u_by_rank[index])
        unit_tail[index] = running
    ratios = {
        index: Fraction(unit_tail[index], n - index + 1)
        for index in unit_tail
    }
    maximum_ratio = max(ratios.values(), default=Fraction(0))
    reset = shortest_subset_reset_word(transition)
    reset_depth = None if reset is None else len(reset)
    binary_involutive_class = (
        schreier_simulable_class
        and len(transition) == 2
        and len(permutation_letters) == 1
        and len(defect_one_letters) == 1
    )
    binary_tail_bound = {
        index: 1 if index == n else 2
        for index in range(2, n + 1)
    }
    binary_tail_checks = {
        index: unit_tail[index] <= binary_tail_bound[index]
        for index in unit_tail
    }
    binary_reset_bound = 2 * n - 3
    binary_wait_normal_form = (
        None if not binary_involutive_class or reset is None else
        _binary_wait_normal_form(
            transition,
            reset,
            permutation_letters[0],
            defect_one_letters[0],
        )
    )
    if binary_involutive_class:
        binary_defect_profile = _defect_one_functional_graph_profile(
            transition[defect_one_letters[0]]
        )
    else:
        binary_defect_profile = None
    binary_clean_one_wait_class = binary_involutive_class and clean_class
    if binary_clean_one_wait_class and binary_defect_profile is not None:
        tail_size = binary_defect_profile["tail_size"]
        cycle_vertex_count = binary_defect_profile["cycle_vertex_count"]
        predicted_wait_number = int(cycle_vertex_count > 1)
        greedy_word = (
            [defect_one_letters[0]] * tail_size
            + [permutation_letters[0]] * predicted_wait_number
            + [defect_one_letters[0]] * (cycle_vertex_count - 1)
        )
        greedy_trace = _word_subset_trace(transition, greedy_word)
        greedy_resets = (
            bool(greedy_trace)
            and len(greedy_trace[-1]["target_subset"]) == 1
        )
        predicted_reset_depth = n - 1 + predicted_wait_number
        certified_wait_number = (
            None if binary_wait_normal_form is None else
            binary_wait_normal_form["genuine_permutation_wait_number"]
        )
        binary_clean_one_wait_theorem = {
            "applicable": True,
            "defect_one_functional_graph": binary_defect_profile,
            "greedy_one_wait_word": greedy_word,
            "greedy_subset_hole_trace": greedy_trace,
            "predicted_wait_number": predicted_wait_number,
            "predicted_reset_depth": predicted_reset_depth,
            "greedy_word_resets": greedy_resets,
            "certified_wait_number_matches_prediction": (
                certified_wait_number == predicted_wait_number
            ),
            "shortest_reset_depth_matches_prediction": (
                reset_depth == predicted_reset_depth
            ),
            "one_wait_bound_holds": (
                certified_wait_number is not None
                and certified_wait_number <= 1
            ),
            "reset_depth_at_most_n": (
                reset_depth is not None and reset_depth <= n
            ),
        }
    else:
        binary_clean_one_wait_theorem = {
            "applicable": False,
            "defect_one_functional_graph": binary_defect_profile,
            "greedy_one_wait_word": None,
            "greedy_subset_hole_trace": None,
            "predicted_wait_number": None,
            "predicted_reset_depth": None,
            "greedy_word_resets": None,
            "certified_wait_number_matches_prediction": None,
            "shortest_reset_depth_matches_prediction": None,
            "one_wait_bound_holds": None,
            "reset_depth_at_most_n": None,
        }
    commuting_involutive_class = (
        schreier_simulable_class
        and permutation_core_all_involutions
        and permutation_core_pairwise_commuting
    )
    commuting_generator_count = len(distinct_nonidentity_permutations)
    commuting_schreier_rank = (
        elementary_abelian_rank
        if elementary_abelian_rank is not None else 0
    )
    commuting_tail_bound = {
        index: 1 if index == n else commuting_schreier_rank + 1
        for index in range(2, n + 1)
    }
    commuting_tail_checks = {
        index: unit_tail[index] <= commuting_tail_bound[index]
        for index in unit_tail
    }
    commuting_reset_bound = 1 + (n - 2) * (commuting_schreier_rank + 1)
    commuting_linear_constant = max(
        Fraction(1), Fraction(commuting_schreier_rank + 1, 2)
    )
    faithful_rank_upper_bound = n // 2
    faithful_rank_bound_holds = (
        None if elementary_abelian_rank is None else
        elementary_abelian_rank <= faithful_rank_upper_bound
    )
    parameter_free_reset_bound = (
        1 + (n - 2) * (faithful_rank_upper_bound + 1)
    )
    cerny_bound = (n - 1) ** 2
    sigma_by_rank = {
        rank_value: max(
            (
                row["schreier_quotient_rank"]
                for row in state_rows
                if row["rank"] == rank_value
                and row["schreier_quotient_rank"] is not None
            ),
            default=0,
        )
        for rank_value in range(2, n + 1)
    }
    statewise_reset_bound = 1 + sum(
        1 + sigma_by_rank[rank_value]
        for rank_value in range(2, n)
    )
    statewise_quotient_rank_checks_passed = all(
        profile["quotient_rank_size_bound_holds"]
        and profile["quotient_rank_radius_bound_holds"]
        for profile in orbit_cache.values()
    )
    return {
        "carrier": "inverse_closed_permutation_core_kernel_corridor",
        "state_count": n,
        "alphabet_size": len(transition),
        "letter_ranks": letter_ranks,
        "permutation_letters": permutation_letters,
        "permutation_inverse_letter": inverse_indices,
        "permutation_core_nonempty": permutation_core_nonempty,
        "inverse_closed_permutation_core": inverse_closed,
        "distinct_nonidentity_permutation_generator_count": (
            commuting_generator_count
        ),
        "permutation_core_all_involutions": (
            permutation_core_all_involutions
        ),
        "permutation_core_pairwise_commuting": (
            permutation_core_pairwise_commuting
        ),
        "elementary_abelian_core_rank": elementary_abelian_rank,
        "elementary_abelian_core_order": elementary_abelian_order,
        "faithful_elementary_abelian_rank_upper_bound": (
            faithful_rank_upper_bound
        ),
        "faithful_elementary_abelian_rank_bound_holds": (
            faithful_rank_bound_holds
        ),
        "defect_one_letters": defect_one_letters,
        "higher_defect_letters": higher_defect_letters,
        "all_nonpermutation_letters_defect_one": (
            all_nonpermutation_defect_one
        ),
        "finite_escape_all_reachable_nonsingletons": finite_escape_all,
        "reachable_unit_state_count": len(state_rows),
        "clean_exit_on_all_unit_orbits": clean_exit,
        "letterwise_schreier_simulation_on_all_unit_orbits": (
            schreier_simulable
        ),
        "all_unit_shortest_exits_have_core_normal_form": normal_form,
        "inverse_closed_defect_one_clean_exit_class": clean_class,
        "inverse_closed_defect_one_schreier_simulable_class": (
            schreier_simulable_class
        ),
        "inverse_closed_defect_one_normal_form_class": normal_form_class,
        "clean_exit_theorem_failure_count": len(clean_theorem_failures),
        "schreier_simulation_theorem_failure_count": len(
            schreier_simulation_theorem_failures
        ),
        "state_rows": state_rows,
        "orbit_profiles": list(orbit_cache.values()),
        "u_r_by_rank": {
            str(rank_value): value
            for rank_value, value in sorted(u_by_rank.items())
        },
        "unit_wait_tail_by_index": {
            str(index): value for index, value in sorted(unit_tail.items())
        },
        "linear_codimension_ratio_by_index": {
            str(index): {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for index, value in sorted(ratios.items())
        },
        "maximum_linear_codimension_ratio": {
            "numerator": maximum_ratio.numerator,
            "denominator": maximum_ratio.denominator,
        },
        "unit_tail_sum": sum(unit_tail.values()),
        "shortest_reset_depth": reset_depth,
        "binary_involutive_core_corollary": {
            "applicable": binary_involutive_class,
            "unit_tail_upper_bound_by_index": {
                str(index): value
                for index, value in sorted(binary_tail_bound.items())
            },
            "all_unit_tail_checks_passed": (
                None if not binary_involutive_class
                else all(binary_tail_checks.values())
            ),
            "linear_codimension_constant_C": (
                1 if binary_involutive_class else None
            ),
            "reset_depth_upper_bound": (
                binary_reset_bound if binary_involutive_class else None
            ),
            "reset_bound_holds": (
                None if not binary_involutive_class
                else reset_depth is not None and reset_depth <= binary_reset_bound
            ),
            "wait_number_normal_form": binary_wait_normal_form,
            "clean_one_wait_theorem": binary_clean_one_wait_theorem,
        },
        "commuting_involutive_core_theorem": {
            "applicable": commuting_involutive_class,
            "distinct_nonidentity_generator_count": (
                commuting_generator_count
            ),
            "elementary_abelian_core_rank": (
                elementary_abelian_rank
                if commuting_involutive_class else None
            ),
            "elementary_abelian_core_order": (
                elementary_abelian_order
                if commuting_involutive_class else None
            ),
            "schreier_diameter_upper_bound": (
                commuting_schreier_rank
                if commuting_involutive_class else None
            ),
            "maximum_schreier_quotient_rank_by_subset_rank": (
                None if not commuting_involutive_class else {
                    str(rank_value): value
                    for rank_value, value in sorted(sigma_by_rank.items())
                }
            ),
            "statewise_quotient_rank_reset_depth_upper_bound": (
                statewise_reset_bound if commuting_involutive_class else None
            ),
            "statewise_quotient_rank_bound_holds": (
                None if not commuting_involutive_class
                else reset_depth is not None
                and reset_depth <= statewise_reset_bound
            ),
            "all_statewise_quotient_rank_checks_passed": (
                statewise_quotient_rank_checks_passed
                if commuting_involutive_class else None
            ),
            "unit_tail_upper_bound_by_index": {
                str(index): value
                for index, value in sorted(commuting_tail_bound.items())
            },
            "all_unit_tail_checks_passed": (
                None if not commuting_involutive_class
                else all(commuting_tail_checks.values())
            ),
            "linear_codimension_constant_C": (
                None if not commuting_involutive_class else {
                    "numerator": commuting_linear_constant.numerator,
                    "denominator": commuting_linear_constant.denominator,
                }
            ),
            "reset_depth_upper_bound": (
                commuting_reset_bound if commuting_involutive_class else None
            ),
            "reset_bound_holds": (
                None if not commuting_involutive_class
                else reset_depth is not None
                and reset_depth <= commuting_reset_bound
            ),
            "faithful_rank_upper_bound": (
                faithful_rank_upper_bound
                if commuting_involutive_class else None
            ),
            "faithful_rank_bound_holds": (
                faithful_rank_bound_holds
                if commuting_involutive_class else None
            ),
            "parameter_free_reset_depth_upper_bound": (
                parameter_free_reset_bound
                if commuting_involutive_class else None
            ),
            "parameter_free_bound_holds": (
                None if not commuting_involutive_class
                else reset_depth is not None
                and reset_depth <= parameter_free_reset_bound
            ),
            "cerny_reset_depth_upper_bound": (
                cerny_bound if commuting_involutive_class else None
            ),
            "parameter_free_bound_at_most_cerny": (
                None if not commuting_involutive_class
                else parameter_free_reset_bound <= cerny_bound
            ),
        },
        "theorem_interface": {
            "clean_exit_identity": (
                "For the declared clean class, omega(T) equals one plus "
                "directed permutation-Schreier distance to the defect-one "
                "cover boundary."
            ),
            "diameter_corollary": (
                "A directed cover-radius bound Delta_r gives u_r<=Delta_r+1."
            ),
            "cayley_quotient_bound": (
                "For an inverse-closed permutation core, every subset "
                "Schreier graph is a quotient of the core Cayley graph, so "
                "its cover radius is at most the Cayley diameter whenever "
                "the cover boundary is nonempty."
            ),
            "commuting_involution_bound": (
                "If the core is generated by commuting involutions and has "
                "F2-rank s, each Schreier diameter is at most s; hence "
                "u_n=1 and u_r<=s+1 below full rank."
            ),
            "faithful_rank_bound": (
                "A faithful elementary-abelian permutation group on n "
                "points has F2-rank s<=floor(n/2), giving a parameter-free "
                "bound no larger than (n-1)^2."
            ),
            "binary_wait_number_identity": (
                "In the binary letterwise-simulation class, a shortest "
                "normalized reset word has n-1 defect-one drops and nu(A) "
                "genuine permutation waits, so D_sync=n-1+nu(A)."
            ),
            "binary_clean_one_wait_theorem": (
                "For a synchronizing binary clean automaton, the hole "
                "recurrence admits at most one genuine permutation wait; "
                "therefore D_sync is n-1 or n."
            ),
        },
        "claim_boundary": {
            "letter_classification": "Exact finite theorem",
            "clean_exit_schreier_conjugacy": "Exact class theorem",
            "letterwise_schreier_simulation": "Exact class theorem",
            "binary_involutive_core_linear_bound": "Exact class theorem",
            "commuting_involutive_core_bound": "Exact class theorem",
            "elementary_abelian_faithful_rank_bound": "Exact group theorem",
            "parameter_free_cerny_corollary": "Exact class theorem",
            "binary_wait_number_normal_form": "Exact class theorem",
            "binary_clean_one_wait_bound": "Exact class theorem",
            "binary_clean_extremal_depth_n": "Exact class theorem",
            "shortest_core_normal_form": "Exact finite certificate",
            "linear_codimension_bound": "Computational Observation only",
            "uniform_class_constant": "Open",
            "global_quadratic_synchronization_bound": "Open",
        },
    }
