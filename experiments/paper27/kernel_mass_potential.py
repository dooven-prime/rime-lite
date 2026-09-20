#!/usr/bin/env python3
"""Exact kernel-mass diagnostics for finite synchronizing automata.

The implementation is deliberately integer-only.  A transformation is a
tuple ``t`` with ``t[q]`` the image of state ``q``.  Words act on the right,
so appending a letter ``a`` replaces ``t`` by ``a after t``.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from math import comb
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

Transformation = tuple[int, ...]
Subset = frozenset[int]


def apply_subset(subset: Subset, transformation: Transformation) -> Subset:
    return frozenset(transformation[q] for q in subset)


def compose_transformation(
    transformation: Transformation, letter: Transformation
) -> Transformation:
    """Return ``letter after transformation`` for right-acted words."""
    return tuple(letter[image] for image in transformation)


def kernel_partition(transformation: Transformation) -> tuple[tuple[int, ...], ...]:
    fibres: dict[int, list[int]] = defaultdict(list)
    for source, image in enumerate(transformation):
        fibres[image].append(source)
    return tuple(sorted((tuple(block) for block in fibres.values()), key=lambda b: b[0]))


def kernel_mass(kernel: Sequence[Sequence[int]]) -> int:
    return sum(comb(len(block), 2) for block in kernel)


def kernel_potential(kernel: Sequence[Sequence[int]], n: int) -> int:
    """V(K)=2*(unmerged source pairs)-(|K|-1)."""
    return 2 * (comb(n, 2) - kernel_mass(kernel)) - (len(kernel) - 1)


def rank_debt(rank: int, n: int) -> int:
    """Cerny rank debt D_n(r), with zero debt at the two endpoints."""
    if not 1 <= rank <= n:
        raise ValueError("rank must lie between 1 and n")
    return 0 if rank == n else (n - rank - 1) * (rank - 1)


def rank_debt_potential(kernel: Sequence[Sequence[int]], n: int) -> int:
    """W(K)=V(K)-D_n(|K|)."""
    return kernel_potential(kernel, n) - rank_debt(len(kernel), n)


def cerny_letters(n: int) -> tuple[Transformation, Transformation]:
    """The standard C_n pair: a is an n-cycle and b merges 0 into 1."""
    if n < 2:
        raise ValueError("n must be at least 2")
    cycle = tuple((q + 1) % n for q in range(n))
    defect = tuple(1 if q == 0 else q for q in range(n))
    return cycle, defect


def all_nonempty_subsets(n: int) -> list[Subset]:
    return [
        frozenset(q for q in range(n) if mask & (1 << q))
        for mask in range(1, 1 << n)
    ]


def distance_to_singleton(
    letters: Sequence[Transformation], n: int
) -> dict[Subset, int]:
    """Reverse BFS distance to the nearest singleton in the subset graph."""
    subsets = all_nonempty_subsets(n)
    reverse: dict[Subset, list[Subset]] = defaultdict(list)
    for subset in subsets:
        for letter in letters:
            reverse[apply_subset(subset, letter)].append(subset)
    distance = {subset: 0 for subset in subsets if len(subset) == 1}
    queue = deque(distance)
    while queue:
        target = queue.popleft()
        for source in reverse[target]:
            if source not in distance:
                distance[source] = distance[target] + 1
                queue.append(source)
    return distance


def shortest_reset_words(
    letters: Sequence[Transformation], n: int, max_paths: int | None = None
) -> tuple[int | None, list[tuple[int, ...]]]:
    """Enumerate shortest reset words, with an optional defensive cap."""
    distance = distance_to_singleton(letters, n)
    start = frozenset(range(n))
    if start not in distance:
        return None, []
    shortest = distance[start]
    words: list[tuple[int, ...]] = []

    def visit(subset: Subset, remaining: int, word: tuple[int, ...]) -> None:
        if max_paths is not None and len(words) >= max_paths:
            return
        if remaining == 0:
            words.append(word)
            return
        for index, letter in enumerate(letters):
            target = apply_subset(subset, letter)
            if distance.get(target) == remaining - 1:
                visit(target, remaining - 1, word + (index,))

    visit(start, shortest, tuple())
    return shortest, words


def reachable_subsets(
    letters: Sequence[Transformation], n: int
) -> set[Subset]:
    """Return the subset states reachable from the full state set."""
    start = frozenset(range(n))
    reached = {start}
    queue = deque([start])
    while queue:
        subset = queue.popleft()
        for letter in letters:
            target = apply_subset(subset, letter)
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def reachable_transformations(
    letters: Sequence[Transformation], n: int
) -> set[Transformation]:
    """Return transformations reachable from the identity transformation."""
    identity = tuple(range(n))
    reached = {identity}
    queue = deque([identity])
    while queue:
        transformation = queue.popleft()
        for letter in letters:
            target = compose_transformation(transformation, letter)
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def transport_decomposition(
    transformation: Transformation,
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...], tuple[int, ...]]:
    """Return (kernel partition, image subset, quotient-to-image labelling)."""
    kernel = kernel_partition(transformation)
    image = tuple(sorted(set(transformation)))
    # Blocks are canonically ordered by least source.  Their first images give
    # the induced bijection Q/K -> Im(t); this is lambda_t.
    transport = tuple(transformation[block[0]] for block in kernel)
    if set(transport) != set(image) or len(transport) != len(image):
        raise AssertionError("transport decomposition is not bijective")
    return kernel, image, transport


def fiber_mass_vector(transformation: Transformation) -> tuple[int, ...]:
    """Return mu_t(x)=|t^{-1}(x)| in ambient-state order."""
    mass = [0] * len(transformation)
    for image in transformation:
        mass[image] += 1
    return tuple(mass)


def pushforward_mass(
    mass: Sequence[int], letter: Transformation
) -> tuple[int, ...]:
    """Return a_* mu, so (a_*mu)(y)=sum_{a(x)=y}mu(x)."""
    if len(mass) != len(letter):
        raise ValueError("mass vector and letter have different state counts")
    pushed = [0] * len(mass)
    for source, value in enumerate(mass):
        pushed[letter[source]] += value
    return tuple(pushed)


def mass_kernel_mass(mass: Sequence[int]) -> int:
    return sum(comb(value, 2) for value in mass)


def mass_rank(mass: Sequence[int]) -> int:
    return sum(value > 0 for value in mass)


def mass_partition(mass: Sequence[int]) -> tuple[int, ...]:
    """Return the positive mass multiset as a decreasing integer partition.

    The ambient coordinates are deliberately forgotten here.  They remain
    part of the mass placement, while this partition records only the scalar
    credit layer.
    """
    if any(value < 0 for value in mass):
        raise ValueError("mass entries must be nonnegative")
    total = sum(mass)
    if total <= 0:
        raise ValueError("mass must have positive total")
    return tuple(sorted((value for value in mass if value), reverse=True))


def mass_fiber_partition_witness(
    mass: Sequence[int], letter: Transformation
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Return target fibers witnessing partition transport/coarsening.

    Each row is ``(target, sources)`` for an occupied source fiber of the
    letter.  Its target mass equals the sum of the listed source masses.  If
    support rank is preserved, every source fiber is a singleton and the
    positive-mass partition is unchanged; otherwise these are the explicit
    merges witnessing a coarsening of that partition.
    """
    if len(mass) != len(letter):
        raise ValueError("mass and letter must have the same state count")
    fibers: dict[int, list[int]] = defaultdict(list)
    for source, value in enumerate(mass):
        if value:
            fibers[letter[source]].append(source)
    rows = tuple(
        (target, tuple(sources))
        for target, sources in sorted(fibers.items())
    )
    target_mass = pushforward_mass(mass, letter)
    for target, sources in rows:
        if target_mass[target] != sum(mass[source] for source in sources):
            raise AssertionError("fiber witness does not recover target mass")
    return rows


def mass_partition_transition(
    mass: Sequence[int], letter: Transformation
) -> dict[str, object]:
    """Classify one mass edge as transport or a partition coarsening."""
    source = tuple(mass)
    target = pushforward_mass(source, letter)
    source_rank = mass_rank(source)
    target_rank = mass_rank(target)
    witness = mass_fiber_partition_witness(source, letter)
    singleton_fibers = all(len(sources) == 1 for _, sources in witness)
    source_partition = mass_partition(source)
    target_partition = mass_partition(target)
    fiber_partition = tuple(
        sorted(
            (sum(source[source_index] for source_index in sources)
             for _, sources in witness),
            reverse=True,
        )
    )
    if fiber_partition != target_partition:
        raise AssertionError("fiber witness does not recover target partition")
    if target_rank == source_rank:
        if not singleton_fibers:
            raise AssertionError("rank-preserving edge has a noninjective support fiber")
        if source_partition != target_partition:
            raise AssertionError("rank-preserving edge changed mass partition")
        kind = "transport"
        coarsening = source_partition == target_partition
    elif target_rank < source_rank:
        if singleton_fibers:
            raise AssertionError("strict support drop has no merged support fiber")
        kind = "fusion"
        coarsening = True
    else:
        raise AssertionError("mass pushforward increased support rank")
    return {
        "source": source,
        "target": target,
        "source_partition": source_partition,
        "target_partition": target_partition,
        "source_rank": source_rank,
        "target_rank": target_rank,
        "kind": kind,
        "partition_coarsening": coarsening,
        "fiber_witness": witness,
    }


def mass_fusion_data(
    mass: Sequence[int], letter: Transformation
) -> dict[str, int | tuple[int, ...]]:
    """Compute a terminal fusion credit directly from occupied letter fibres."""
    occupied_fibres: dict[int, list[int]] = defaultdict(list)
    for source, value in enumerate(mass):
        if value:
            occupied_fibres[letter[source]].append(source)
    delta_m = 0
    q = 0
    for sources in occupied_fibres.values():
        q += len(sources) - 1
        delta_m += sum(
            mass[left] * mass[right]
            for left_index, left in enumerate(sources)
            for right in sources[left_index + 1 :]
        )
    target = pushforward_mass(mass, letter)
    if delta_m != mass_kernel_mass(target) - mass_kernel_mass(mass):
        raise AssertionError("occupied-fibre formula disagrees with mass increment")
    if q != mass_rank(mass) - mass_rank(target):
        raise AssertionError("occupied-fibre formula disagrees with rank drop")
    return {
        "target": target,
        "delta_m": delta_m,
        "q": q,
        "budget": 2 * delta_m - q,
    }


def reachable_mass_states(
    letters: Sequence[Transformation], n: int
) -> set[tuple[int, ...]]:
    initial = (1,) * n
    reached = {initial}
    queue = deque([initial])
    while queue:
        mass = queue.popleft()
        for letter in letters:
            target = pushforward_mass(mass, letter)
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def mass_first_exit_frontier(
    mass: tuple[int, ...], letters: Sequence[Transformation]
) -> dict:
    """First support-drop frontier in the exact mass-transport graph."""
    rank = mass_rank(mass)
    if rank <= 1:
        return {"omega": 0, "exits": [], "frontier": []}
    start_mass = mass_kernel_mass(mass)
    seen = {mass: 0}
    queue = deque([mass])
    shortest: int | None = None
    exits: dict[tuple[int, ...], dict] = {}
    while queue:
        current = queue.popleft()
        depth = seen[current]
        if shortest is not None and depth >= shortest:
            continue
        for index, letter in enumerate(letters):
            fusion = mass_fusion_data(current, letter)
            target = fusion["target"]
            if not isinstance(target, tuple):
                raise AssertionError("mass fusion target is not a mass vector")
            target_rank = mass_rank(target)
            length = depth + 1
            if target_rank < rank:
                if shortest is None:
                    shortest = length
                if length != shortest:
                    continue
                delta_m = int(fusion["delta_m"])
                if delta_m != mass_kernel_mass(target) - start_mass:
                    raise AssertionError("rank-preserving prefix changed kernel mass")
                q = rank - target_rank
                if q != fusion["q"]:
                    raise AssertionError("fusion q disagrees with support drop")
                exits[target] = {
                    "length": length,
                    "delta_m": delta_m,
                    "q": q,
                    "budget": 2 * delta_m - q,
                    "target_rank": target_rank,
                    "letter": index,
                }
            elif target not in seen:
                seen[target] = length
                queue.append(target)
    if shortest is None:
        raise ValueError("non-reset mass state has no support-decreasing exit")
    exit_records = sorted(exits.values(), key=lambda item: tuple(item.values()))
    return {
        "omega": shortest,
        "exits": exit_records,
        "frontier": pareto_frontier(exit_records),
    }


def mass_phase_census(
    letters: Sequence[Transformation], n: int
) -> dict:
    """Audit the exact quotient t -> mu_t and the residual (K,T) ambiguity."""
    transformations = reachable_transformations(letters, n)
    mass_states = reachable_mass_states(letters, n)
    mu_groups: dict[tuple[int, ...], list[Transformation]] = defaultdict(list)
    kt_masses: dict[tuple, set[tuple[int, ...]]] = defaultdict(set)
    pushforward_checks = 0
    pushforward_failures = 0
    for transformation in transformations:
        kernel, image, _ = transport_decomposition(transformation)
        mass = fiber_mass_vector(transformation)
        mu_groups[mass].append(transformation)
        kt_masses[(kernel, image)].add(mass)
        if sum(mass) != n or tuple(index for index, value in enumerate(mass) if value) != image:
            raise AssertionError("mass support does not equal transformation image")
        if mass_kernel_mass(mass) != kernel_mass(kernel):
            raise AssertionError("mass vector does not recover kernel mass")
        for letter in letters:
            pushforward_checks += 1
            target = compose_transformation(transformation, letter)
            if fiber_mass_vector(target) != pushforward_mass(mass, letter):
                pushforward_failures += 1

    frontier_cache = {
        mass: mass_first_exit_frontier(mass, letters)
        for mass in mass_states
        if mass_rank(mass) > 1
    }
    multi_mu_kt = 0
    varying_kt = 0
    first_example = None
    for (kernel, image), masses in kt_masses.items():
        if len(masses) <= 1:
            continue
        multi_mu_kt += 1
        signatures = {
            mass: tuple(
                (entry["length"], entry["delta_m"], entry["q"], entry["budget"], entry["target_rank"])
                for entry in frontier_cache[mass]["frontier"]
            )
            for mass in masses
            if mass_rank(mass) > 1
        }
        if len(set(signatures.values())) <= 1:
            continue
        varying_kt += 1
        if first_example is None:
            first_example = {
                "kernel": [list(block) for block in kernel],
                "image": list(image),
                "mass_frontiers": [
                    {
                        "mass": list(mass),
                        "frontier": [list(record) for record in signature],
                    }
                    for mass, signature in sorted(signatures.items())
                ],
            }
    return {
        "reachable_transformations": len(transformations),
        "reachable_mass_states": len(mass_states),
        "ambient_mass_state_bound": comb(2 * n - 1, n - 1),
        "mass_fibers": len(mu_groups),
        "multi_transformation_mass_fibers": sum(len(group) > 1 for group in mu_groups.values()),
        "pushforward_checks": pushforward_checks,
        "pushforward_failures": pushforward_failures,
        "same_mass_is_transition_congruence": pushforward_failures == 0,
        "kt_fibers_with_multiple_masses": multi_mu_kt,
        "kt_fibers_with_frontier_variation": varying_kt,
        "mass_frontier_example": first_example,
    }


def first_exit_frontier(
    transformation: Transformation,
    letters: Sequence[Transformation],
    n: int,
    omega: int | None = None,
) -> dict:
    """Enumerate kernel-changing exits at the first image-rank escape depth."""
    rank = len(set(transformation))
    if rank <= 1:
        return {"omega": 0, "exits": []}
    if omega is None:
        omega, _ = shortest_escape_profile(frozenset(set(transformation)), letters)
    seen = {transformation: 0}
    queue = deque([transformation])
    exits: dict[Transformation, dict] = {}
    while queue:
        current = queue.popleft()
        depth = seen[current]
        if depth >= omega:
            continue
        current_kernel = kernel_partition(current)
        current_mass = kernel_mass(current_kernel)
        for index, letter in enumerate(letters):
            target = compose_transformation(current, letter)
            target_rank = len(set(target))
            length = depth + 1
            if target_rank < rank:
                if length != omega:
                    continue
                target_kernel = kernel_partition(target)
                delta_m = kernel_mass(target_kernel) - current_mass
                q = len(current_kernel) - len(target_kernel)
                exits[target] = {
                    "length": length,
                    "delta_m": delta_m,
                    "q": q,
                    "budget": 2 * delta_m - q,
                    "target_rank": target_rank,
                    "letter": index,
                }
            elif target not in seen:
                seen[target] = length
                queue.append(target)
    return {"omega": omega, "exits": sorted(exits.values(), key=lambda x: tuple(x.values()))}


def pareto_frontier(exits: Sequence[dict]) -> list[dict]:
    """Keep exits not dominated by shorter length and larger KC budget."""
    frontier = []
    for candidate in exits:
        dominated = any(
            other["length"] <= candidate["length"]
            and other["budget"] >= candidate["budget"]
            and (
                other["length"] < candidate["length"]
                or other["budget"] > candidate["budget"]
            )
            for other in exits
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda x: (x["length"], -x["budget"], x["delta_m"], x["q"]))


def phase_necessity_census(
    letters: Sequence[Transformation], n: int
) -> dict:
    """Compare different lambda_t values inside common (K,T) fibres."""
    groups: dict[tuple, list[Transformation]] = defaultdict(list)
    transformations = reachable_transformations(letters, n)
    omega_by_image: dict[tuple[int, ...], tuple[int, int]] = {}
    for transformation in transformations:
        kernel, image, transport = transport_decomposition(transformation)
        groups[(kernel, image)].append(transformation)
        if image not in omega_by_image:
            omega_by_image[image] = (
                shortest_escape_profile(frozenset(image), letters)
                if len(image) > 1
                else (0, 0)
            )
    multi_groups = 0
    omega_variation = 0
    frontier_variation = 0
    first_example = None
    for (kernel, image), members in groups.items():
        transports = {}
        frontiers = {}
        for transformation in members:
            _, _, transport = transport_decomposition(transformation)
            transports[transport] = transformation
            omega, _ = omega_by_image[image]
            exits = first_exit_frontier(transformation, letters, n, omega)["exits"]
            signature = tuple(
                (item["length"], item["delta_m"], item["q"], item["budget"], item["target_rank"])
                for item in pareto_frontier(exits)
            )
            frontiers[transport] = signature
        if len(transports) <= 1:
            continue
        multi_groups += 1
        if len({omega_by_image[image][0] for _ in transports}) > 1:
            omega_variation += 1
        if len(set(frontiers.values())) > 1:
            frontier_variation += 1
            if first_example is None:
                first_example = {
                    "kernel": [list(block) for block in kernel],
                    "image": list(image),
                    "omega": omega_by_image[image][0],
                    "lambda_frontiers": [
                        {
                            "lambda": list(transport),
                            "frontier": [list(record) for record in signature],
                        }
                        for transport, signature in sorted(frontiers.items())
                    ],
                }
    return {
        "reachable_transformations": len(transformations),
        "kt_fibers": len(groups),
        "multi_lambda_fibers": multi_groups,
        "omega_variation_fibers": omega_variation,
        "frontier_variation_fibers": frontier_variation,
        "omega_is_image_invariant": omega_variation == 0,
        "lambda_frontier_example": first_example,
    }


def shortest_escape_profile(
    subset: Subset, letters: Sequence[Transformation]
) -> tuple[int, int]:
    """Return omega(T) and the best excess among shortest strict escapes."""
    rank = len(subset)
    seen = {subset}
    queue = deque([(subset, 0)])
    shortest: int | None = None
    excesses: list[int] = []
    while queue:
        current, depth = queue.popleft()
        if shortest is not None and depth >= shortest:
            continue
        for letter in letters:
            target = apply_subset(current, letter)
            if len(target) < rank:
                escape_length = depth + 1
                if shortest is None:
                    shortest = escape_length
                if escape_length == shortest:
                    excesses.append(rank - len(target))
            elif target not in seen:
                seen.add(target)
                queue.append((target, depth + 1))
    if shortest is None:
        raise ValueError("reachable subset has no strict escape")
    return shortest, max(excesses)


def as_fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def from_fraction(record: dict[str, int]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def fi_profile(letters: Sequence[Transformation], n: int) -> dict:
    """Compute exact rankwise FI tails, retaining the unit/high split."""
    chi: dict[int, Fraction] = {}
    unit: dict[int, Fraction] = {}
    high: dict[int, Fraction] = {}
    state_count = 0
    unit_state_count = 0
    for subset in reachable_subsets(letters, n):
        if len(subset) == 1:
            continue
        omega, e_star = shortest_escape_profile(subset, letters)
        ratio = Fraction(omega, e_star)
        rank = len(subset)
        chi[rank] = max(chi.get(rank, Fraction(0)), ratio)
        branch = unit if e_star == 1 else high
        branch[rank] = max(branch.get(rank, Fraction(0)), ratio)
        state_count += 1
        unit_state_count += e_star == 1
    unit_tail: dict[int, Fraction] = {}
    high_tail: dict[int, Fraction] = {}
    chi_tail: dict[int, Fraction] = {}
    for j in range(2, n + 1):
        unit_tail[j] = max(
            (value for rank, value in unit.items() if rank >= j), default=Fraction(0)
        )
        high_tail[j] = max(
            (value for rank, value in high.items() if rank >= j), default=Fraction(0)
        )
        chi_tail[j] = max(unit_tail[j], high_tail[j])
    phi = sum(chi_tail.values(), Fraction(0))
    unit_area = sum(unit_tail.values(), Fraction(0))
    high_correction = sum(
        (chi_tail[j] - unit_tail[j] for j in range(2, n + 1)), Fraction(0)
    )
    return {
        "phi_fi": as_fraction(phi),
        "unit_area": as_fraction(unit_area),
        "high_capacity_correction": as_fraction(high_correction),
        "unit_only": state_count == unit_state_count,
        "state_count": state_count,
        "unit_state_count": unit_state_count,
        "chi_by_rank": {str(rank): as_fraction(value) for rank, value in sorted(chi.items())},
        "unit_tail": {str(rank): as_fraction(value) for rank, value in unit_tail.items()},
        "high_tail": {str(rank): as_fraction(value) for rank, value in high_tail.items()},
    }


@dataclass(frozen=True)
class Corridor:
    length: int
    delta_m: int
    q: int
    budget: int
    bank: int
    start_rank: int
    end_rank: int
    image_excess: int
    escape_omega: int
    escape_e_star: int
    debt_delta: int
    debt_budget: int
    debt_bank: int

    def as_dict(self) -> dict[str, int]:
        return {
            "length": self.length,
            "delta_m": self.delta_m,
            "q": self.q,
            "budget": self.budget,
            "bank": self.bank,
            "start_rank": self.start_rank,
            "end_rank": self.end_rank,
            "image_excess": self.image_excess,
            "escape_omega": self.escape_omega,
            "escape_e_star": self.escape_e_star,
            "debt_delta": self.debt_delta,
            "debt_budget": self.debt_budget,
            "debt_bank": self.debt_bank,
        }


def corridor_profile(
    word: Sequence[int], letters: Sequence[Transformation], n: int
) -> list[Corridor]:
    """Split a word at kernel changes and compute exact KC ledgers."""
    transformation = tuple(range(n))
    old_kernel = kernel_partition(transformation)
    old_mass = kernel_mass(old_kernel)
    subset = frozenset(range(n))
    corridor_start_subset = subset
    length = 0
    profile: list[Corridor] = []
    for index in word:
        image = apply_subset(subset, letters[index])
        image_excess = len(subset) - len(image)
        transformation = compose_transformation(transformation, letters[index])
        length += 1
        new_kernel = kernel_partition(transformation)
        subset = image
        if new_kernel == old_kernel:
            continue
        new_mass = kernel_mass(new_kernel)
        delta_m = new_mass - old_mass
        q = len(old_kernel) - len(new_kernel)
        budget = 2 * delta_m - q
        debt_delta = rank_debt(len(old_kernel), n) - rank_debt(len(new_kernel), n)
        escape_omega, escape_e_star = shortest_escape_profile(corridor_start_subset, letters)
        profile.append(
            Corridor(
                length=length,
                delta_m=delta_m,
                q=q,
                budget=budget,
                bank=budget - length,
                start_rank=len(old_kernel),
                end_rank=len(new_kernel),
                image_excess=image_excess,
                escape_omega=escape_omega,
                escape_e_star=escape_e_star,
                debt_delta=debt_delta,
                debt_budget=budget - debt_delta,
                debt_bank=budget - debt_delta - length,
            )
        )
        old_kernel, old_mass, length = new_kernel, new_mass, 0
        corridor_start_subset = image
    # A rank-one reset ends exactly at a kernel change.  For a non-reset word,
    # retaining a nonempty corridor would make the profile incomplete.
    if length:
        raise ValueError("word ended inside an unchanged kernel corridor")
    return profile


def path_summary(
    words: Sequence[Sequence[int]], letters: Sequence[Transformation], n: int
) -> dict:
    profiles = [corridor_profile(word, letters, n) for word in words]
    banks = [min((c.bank for c in profile), default=0) for profile in profiles]
    admissible = [all(c.bank >= 0 for c in profile) for profile in profiles]
    local_w_admissible = [all(c.debt_bank >= 0 for c in profile) for profile in profiles]
    telescope_values = [sum(c.budget for c in profile) for profile in profiles]
    prefix_ledgers = [prefix_bank_ledger(profile, n) for profile in profiles]
    return {
        "shortest_path_count": len(words),
        "bank_admissible_path_count": sum(admissible),
        "has_bank_admissible_path": any(admissible),
        "minimum_local_bank": min(banks, default=0),
        "minimum_bank_by_path": banks,
        "local_w_admissible_path_count": sum(local_w_admissible),
        "has_local_w_admissible_path": any(local_w_admissible),
        "banked_v_admissible_path_count": sum(
            ledger["banked_v_admissible"] for ledger in prefix_ledgers
        ),
        "has_banked_v_admissible_path": any(
            ledger["banked_v_admissible"] for ledger in prefix_ledgers
        ),
        "banked_w_admissible_path_count": sum(
            ledger["banked_w_admissible"] for ledger in prefix_ledgers
        ),
        "has_banked_w_admissible_path": any(
            ledger["banked_w_admissible"] for ledger in prefix_ledgers
        ),
        "prefix_bank_ledgers": prefix_ledgers,
        "global_budget_telescope_values": telescope_values,
        "global_budget_telescope_constant": len(set(telescope_values)) <= 1,
        "profiles": [
            [corridor.as_dict() for corridor in profile] for profile in profiles
        ],
    }


def prefix_bank_ledger(profile: Sequence[Corridor], n: int) -> dict:
    """Return LOCAL/BANKED V/W data and the exact rank-debt prefix identity."""
    banked_v = 0
    banked_w = 0
    prefixes = []
    for index, corridor in enumerate(profile, start=1):
        local_v = corridor.budget - corridor.length
        local_w = corridor.debt_budget - corridor.length
        banked_v += local_v
        banked_w += local_w
        debt = rank_debt(corridor.end_rank, n)
        prefixes.append(
            {
                "corridor": index,
                "rank": corridor.end_rank,
                "local_v": local_v,
                "local_w": local_w,
                "banked_v": banked_v,
                "banked_w": banked_w,
                "rank_debt": debt,
                "banked_difference": banked_w - banked_v,
                "identity_holds": banked_w - banked_v == debt,
            }
        )
    return {
        "prefixes": prefixes,
        "all_prefix_identities_hold": all(row["identity_holds"] for row in prefixes),
        "local_v_admissible": all(row["local_v"] >= 0 for row in prefixes),
        "local_w_admissible": all(row["local_w"] >= 0 for row in prefixes),
        "banked_v_admissible": all(row["banked_v"] >= 0 for row in prefixes),
        "banked_w_admissible": all(row["banked_w"] >= 0 for row in prefixes),
        "banked_v_implies_banked_w": not all(
            row["banked_v"] >= 0 for row in prefixes
        )
        or all(row["banked_w"] >= 0 for row in prefixes),
    }


def first_exit_budget_search(
    letters: Sequence[Transformation], n: int, use_rank_debt: bool = False
) -> dict:
    """Search the full marked-kernel graph with LOCAL_V or LOCAL_W payment.

    A node is a reachable transformation together with the shortest current
    corridor length at that transformation.  Kernel-preserving edges increase
    this length.  A kernel-changing edge is retained only when its length is at
    most ``2*Delta M-q`` and then resets the corridor counter to zero.  Keeping
    the least corridor length for each transformation is a dominance rule: the
    same suffix is no harder to traverse from a shorter marked-kernel prefix.
    """
    identity = tuple(range(n))
    best_length: dict[Transformation, int] = {identity: 0}
    paths: dict[Transformation, tuple[int, ...]] = {identity: tuple()}
    queue = deque([identity])
    explored_edges = 0
    while queue:
        transformation = queue.popleft()
        corridor_length = best_length[transformation]
        if len(set(transformation)) == 1:
            word = paths[transformation]
            profile = corridor_profile(word, letters, n)
            bank_field = "debt_bank" if use_rank_debt else "bank"
            return {
                "found": True,
                "semantics": "LOCAL_W" if use_rank_debt else "LOCAL_V",
                "word": list(word),
                "word_length": len(word),
                "minimum_bank": min(
                    (getattr(corridor, bank_field) for corridor in profile), default=0
                ),
                "profile": [corridor.as_dict() for corridor in profile],
                "explored_transformations": len(best_length),
                "explored_edges": explored_edges,
            }
        old_kernel = kernel_partition(transformation)
        old_mass = kernel_mass(old_kernel)
        for index, letter in enumerate(letters):
            explored_edges += 1
            target = compose_transformation(transformation, letter)
            new_kernel = kernel_partition(target)
            if new_kernel == old_kernel:
                next_length = corridor_length + 1
            else:
                delta_m = kernel_mass(new_kernel) - old_mass
                q = len(old_kernel) - len(new_kernel)
                budget = 2 * delta_m - q
                if use_rank_debt:
                    budget -= rank_debt(len(old_kernel), n) - rank_debt(
                        len(new_kernel), n
                    )
                if corridor_length + 1 > budget:
                    continue
                next_length = 0
            if next_length < best_length.get(target, 10**9):
                best_length[target] = next_length
                paths[target] = paths[transformation] + (index,)
                queue.append(target)
    return {
        "found": False,
        "semantics": "LOCAL_W" if use_rank_debt else "LOCAL_V",
        "word": None,
        "word_length": None,
        "minimum_bank": None,
        "profile": None,
        "explored_transformations": len(best_length),
        "explored_edges": explored_edges,
    }


def banked_first_exit_search(
    letters: Sequence[Transformation], n: int, use_rank_debt: bool = False
) -> dict:
    """Search with cumulative credit, allowing credit to move across corridors.

    At a transformation inside a kernel corridor, ``resource`` equals the bank
    accumulated at prior kernel exits minus the length already spent in the
    current corridor.  A rank-preserving edge costs one.  A kernel-changing
    edge costs one, adds its V/W credit, and is admissible exactly when the new
    cumulative bank is nonnegative.  Larger resource dominates smaller
    resource at the same transformation.
    """
    identity = tuple(range(n))
    best_resource: dict[Transformation, int] = {identity: 0}
    paths: dict[Transformation, tuple[int, ...]] = {identity: tuple()}
    queue = deque([identity])
    explored_edges = 0
    while queue:
        transformation = queue.popleft()
        resource = best_resource[transformation]
        if len(set(transformation)) == 1:
            word = paths[transformation]
            profile = corridor_profile(word, letters, n)
            ledger = prefix_bank_ledger(profile, n)
            admissible_field = (
                "banked_w_admissible" if use_rank_debt else "banked_v_admissible"
            )
            if not ledger[admissible_field]:
                raise AssertionError("banked search returned an inadmissible path")
            return {
                "found": True,
                "semantics": "BANKED_W" if use_rank_debt else "BANKED_V",
                "word": list(word),
                "word_length": len(word),
                "final_bank": resource,
                "prefix_ledger": ledger,
                "profile": [corridor.as_dict() for corridor in profile],
                "explored_transformations": len(best_resource),
                "explored_edges": explored_edges,
            }
        old_kernel = kernel_partition(transformation)
        old_mass = kernel_mass(old_kernel)
        for index, letter in enumerate(letters):
            explored_edges += 1
            target = compose_transformation(transformation, letter)
            new_kernel = kernel_partition(target)
            if new_kernel == old_kernel:
                next_resource = resource - 1
            else:
                delta_m = kernel_mass(new_kernel) - old_mass
                q = len(old_kernel) - len(new_kernel)
                credit = 2 * delta_m - q
                if use_rank_debt:
                    credit += rank_debt(len(new_kernel), n) - rank_debt(
                        len(old_kernel), n
                    )
                next_resource = resource - 1 + credit
                if next_resource < 0:
                    continue
            if next_resource > best_resource.get(target, -10**9):
                best_resource[target] = next_resource
                paths[target] = paths[transformation] + (index,)
                queue.append(target)
    return {
        "found": False,
        "semantics": "BANKED_W" if use_rank_debt else "BANKED_V",
        "word": None,
        "word_length": None,
        "final_bank": None,
        "prefix_ledger": None,
        "profile": None,
        "explored_transformations": len(best_resource),
        "explored_edges": explored_edges,
    }


def audit_cerny(
    n: int, include_phase: bool = False, include_mass: bool = False
) -> dict:
    letters = cerny_letters(n)
    distance, words = shortest_reset_words(letters, n)
    if distance is None:
        raise AssertionError("C_n should synchronize")
    summary = path_summary(words, letters, n)
    canonical = summary["profiles"][0]
    fi = fi_profile(letters, n)
    debt_banks = [c["debt_bank"] for c in canonical]
    return {
        "family": "Cerny",
        "n": n,
        "alphabet": ["a", "b"],
        "letters": [list(letter) for letter in letters],
        "reset_length": distance,
        "expected_cerny_length": (n - 1) ** 2,
        "shortest": summary,
        "canonical_corridor_lengths": [c["length"] for c in canonical],
        "canonical_budgets": [c["budget"] for c in canonical],
        "canonical_banks": [c["bank"] for c in canonical],
        "local_kc_all_equal": all(c["bank"] == 0 for c in canonical),
        "global_potential_telescope": sum(c["budget"] for c in canonical),
        "upstream_unit_excess_corridors": sum(
            c["escape_e_star"] == 1 and c["delta_m"] > 1 for c in canonical
        ),
        "fi": fi,
        "rank_debt_banks": debt_banks,
        "rank_debt_local_all_pass": all(bank >= 0 for bank in debt_banks),
        "rank_debt_local_all_equal": all(bank == 0 for bank in debt_banks),
        "phase_necessity": (
            phase_necessity_census(letters, n)
            if include_phase
            else {"status": "skipped", "reason": "release phase census disabled"}
        ),
        "mass_phase": (
            mass_phase_census(letters, n)
            if include_mass
            else {"status": "skipped", "reason": "release mass census disabled"}
        ),
    }


def audit_fixed_cycle(
    n: int,
    max_paths: int | None = None,
    include_phase: bool = False,
    include_mass: bool = False,
) -> dict:
    """Exhaust the n^n second-letter slice with a fixed n-cycle first letter."""
    cycle = cerny_letters(n)[0]
    rows = []
    synchronizing = 0
    total_paths = 0
    bank_paths = 0
    automata_with_bank_path = 0
    no_bank_indices: list[int] = []
    first_counterexample: dict | None = None
    upstream_corridors = 0
    upstream_automata = 0
    full_budget_paths = 0
    full_budget_automata = 0
    full_budget_fail_indices: list[int] = []
    full_debt_budget_automata = 0
    full_debt_budget_fail_indices: list[int] = []
    banked_v_automata = 0
    banked_v_fail_indices: list[int] = []
    banked_w_automata = 0
    banked_w_fail_indices: list[int] = []
    hostile_rows: list[dict] = []
    phase_multi_lambda = 0
    phase_frontier_variation = 0
    debt_pass_automata = 0
    debt_equal_automata = 0
    shortest_banked_v_automata = 0
    shortest_banked_w_automata = 0
    prefix_identity_failures = 0
    mass_transition_failures = 0
    mass_kt_variation = 0
    for index, defect in enumerate(itertools.product(range(n), repeat=n)):
        letters = (cycle, defect)
        distance, words = shortest_reset_words(letters, n, max_paths=max_paths)
        if distance is None:
            rows.append({"index": index, "defect": list(defect), "synchronizing": False})
            continue
        synchronizing += 1
        total_paths += len(words)
        summary = path_summary(words, letters, n)
        fi = fi_profile(letters, n)
        phi_fi = from_fraction(fi["phi_fi"])
        phase = phase_necessity_census(letters, n) if include_phase else {
            "status": "skipped",
            "reason": "release phase census disabled",
        }
        mass_phase = mass_phase_census(letters, n) if include_mass else {
            "status": "skipped",
            "reason": "release mass census disabled",
        }
        bank_paths += summary["bank_admissible_path_count"]
        if summary["has_bank_admissible_path"]:
            automata_with_bank_path += 1
        else:
            no_bank_indices.append(index)
        debt_pass = any(
            all(corridor["debt_bank"] >= 0 for corridor in profile)
            for profile in summary["profiles"]
        )
        debt_equal = any(
            all(corridor["debt_bank"] == 0 for corridor in profile)
            for profile in summary["profiles"]
        )
        debt_pass_automata += debt_pass
        debt_equal_automata += debt_equal
        shortest_banked_v_automata += summary["has_banked_v_admissible_path"]
        shortest_banked_w_automata += summary["has_banked_w_admissible_path"]
        prefix_identity_failures += sum(
            not ledger["all_prefix_identities_hold"]
            for ledger in summary["prefix_bank_ledgers"]
        )
        phase_multi_lambda += phase.get("multi_lambda_fibers", 0)
        phase_frontier_variation += phase.get("frontier_variation_fibers", 0)
        mass_transition_failures += mass_phase.get("pushforward_failures", 0)
        mass_kt_variation += mass_phase.get("kt_fibers_with_frontier_variation", 0)
        upstream = sum(
            1
            for profile in summary["profiles"]
            for corridor in profile
            if corridor["escape_e_star"] == 1 and corridor["delta_m"] > 1
        )
        if upstream:
            upstream_automata += 1
            upstream_corridors += upstream
        upstream_credits = [
            sum(
                2 * max(corridor["delta_m"] - corridor["image_excess"], 0)
                for corridor in profile
            )
            for profile in summary["profiles"]
        ]
        full = first_exit_budget_search(letters, n)
        if full["found"]:
            full_budget_automata += 1
            full_budget_paths += 1
        else:
            full_budget_fail_indices.append(index)
        full_debt = first_exit_budget_search(letters, n, use_rank_debt=True)
        if full_debt["found"]:
            full_debt_budget_automata += 1
        else:
            full_debt_budget_fail_indices.append(index)
        banked_v = banked_first_exit_search(letters, n)
        if banked_v["found"]:
            banked_v_automata += 1
        else:
            banked_v_fail_indices.append(index)
        banked_w = banked_first_exit_search(letters, n, use_rank_debt=True)
        if banked_w["found"]:
            banked_w_automata += 1
        else:
            banked_w_fail_indices.append(index)
        row = {
            "index": index,
            "defect": list(defect),
            "synchronizing": True,
            "reset_length": distance,
            "shortest": summary,
            "upstream_unit_corridor_count": upstream,
            "upstream_mass_credit_by_shortest_path": upstream_credits,
            "full_first_exit_budget_search": full,
            "full_rank_debt_budget_search": full_debt,
            "banked_v_search": banked_v,
            "banked_w_search": banked_w,
            "fi": fi,
            "phase_necessity": phase,
            "mass_phase": mass_phase,
            "rank_debt_local_pass": debt_pass,
            "rank_debt_local_equal": debt_equal,
        }
        rows.append(row)
        threshold = (n - 1) ** 2
        if phi_fi > threshold:
            hostile_rows.append(
                {
                    "index": index,
                    "defect": list(defect),
                    "reset_length": distance,
                    "phi_fi": as_fraction(phi_fi),
                    "fi_excess_over_cerny": as_fraction(phi_fi - threshold),
                    "unit_only": fi["unit_only"],
                    "high_capacity_correction": fi["high_capacity_correction"],
                    "minimum_upstream_mass_credit": min(upstream_credits),
                    "maximum_upstream_mass_credit": max(upstream_credits),
                    "full_budget_search_found": full["found"],
                }
            )
        if not summary["has_bank_admissible_path"] and first_counterexample is None:
            first_counterexample = row
    return {
        "family": "fixed-cycle-second-letter-exhaustion",
        "n": n,
        "labelled_transformations": n**n,
        "synchronizing_automata": synchronizing,
        "total_shortest_paths": total_paths,
        "bank_admissible_shortest_paths": bank_paths,
        "automata_with_bank_admissible_path": automata_with_bank_path,
        "automata_without_bank_admissible_path": synchronizing - automata_with_bank_path,
        "upstream_unit_corridor_total": upstream_corridors,
        "upstream_unit_automata": upstream_automata,
        "full_budget_admissible_automata": full_budget_automata,
        "full_budget_inadmissible_automata": synchronizing - full_budget_automata,
        "full_budget_fail_indices": full_budget_fail_indices,
        "full_rank_debt_budget_admissible_automata": full_debt_budget_automata,
        "full_rank_debt_budget_inadmissible_automata": synchronizing - full_debt_budget_automata,
        "full_rank_debt_budget_fail_indices": full_debt_budget_fail_indices,
        "local_v_admissible_automata": full_budget_automata,
        "local_v_fail_indices": full_budget_fail_indices,
        "local_w_admissible_automata": full_debt_budget_automata,
        "local_w_fail_indices": full_debt_budget_fail_indices,
        "banked_v_admissible_automata": banked_v_automata,
        "banked_v_fail_indices": banked_v_fail_indices,
        "banked_w_admissible_automata": banked_w_automata,
        "banked_w_fail_indices": banked_w_fail_indices,
        "banked_v_failure_subset_of_banked_w": set(banked_w_fail_indices)
        <= set(banked_v_fail_indices),
        "phi_fi_hostile_threshold": (n - 1) ** 2,
        "phi_fi_hostile_count": len(hostile_rows),
        "phi_fi_hostile_rows": hostile_rows,
        "rank_debt_local_pass_automata": debt_pass_automata,
        "rank_debt_local_equal_automata": debt_equal_automata,
        "shortest_banked_v_admissible_automata": shortest_banked_v_automata,
        "shortest_banked_w_admissible_automata": shortest_banked_w_automata,
        "prefix_rank_debt_identity_failures": prefix_identity_failures,
        "phase_multi_lambda_fiber_total": phase_multi_lambda,
        "phase_frontier_variation_fiber_total": phase_frontier_variation,
        "mass_pushforward_failure_total": mass_transition_failures,
        "mass_kt_frontier_variation_fiber_total": mass_kt_variation,
        "first_bank_counterexample": first_counterexample,
        "rows": rows,
    }


def build_report(include_phase: bool = False, include_mass: bool = False) -> dict:
    cerny = [
        audit_cerny(
            n,
            include_phase=include_phase and n <= 8,
            include_mass=include_mass and n <= 8,
        )
        for n in range(3, 11)
    ]
    fixed = audit_fixed_cycle(
        5, include_phase=include_phase, include_mass=include_mass
    )
    return {"cerny": cerny, "fixed_cycle_n5": fixed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fixed-cycle-n", type=int, default=5)
    parser.add_argument("--phase", action="store_true")
    parser.add_argument("--mass-phase", action="store_true")
    args = parser.parse_args()
    payload = {
        "cerny": [
            audit_cerny(
                n,
                include_phase=args.phase and n <= 8,
                include_mass=args.mass_phase and n <= 8,
            )
            for n in range(3, 11)
        ]
    }
    if args.fixed_cycle_n:
        payload["fixed_cycle"] = audit_fixed_cycle(
            args.fixed_cycle_n,
            include_phase=args.phase,
            include_mass=args.mass_phase,
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "cerny_n": [row["n"] for row in payload["cerny"]],
        "fixed_cycle": payload.get("fixed_cycle", {}).get("synchronizing_automata"),
    }))


if __name__ == "__main__":
    main()
