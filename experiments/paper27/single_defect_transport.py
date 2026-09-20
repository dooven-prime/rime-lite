#!/usr/bin/env python3
"""Fixed-kernel diagnostics for the single rank-decreasing-letter slice.

This module is an exploration-layer reduction for the ``|D_A|=1`` case.  It
does not alter the canonical mass or Bellman engines.  If ``d`` is the unique
rank-decreasing letter, every strict rank drop is caused by the fixed kernel
partition ``K_d``; at a lower-rank mass state the same letter is allowed as a
transport edge exactly when the current support is a partial transversal of
``K_d``.

The transport graph is the mass graph restricted to rank-preserving edges.  A
directed shortest path from a source to the boundary where ``d`` becomes
strictly rank-decreasing, followed by ``d``, is a first-exit word of the form
``u d``.  The graph is finite because a mass vector has total mass `
``.

The noninitial maturity identity is recorded exactly as

    tau(d_*mu) - tau(mu)
      = 2*DeltaM_d(mu) + q_d(mu)*(2*r-q_d(mu)-n-1).

The initial state has the separately defined deadline ``tau(1)=0``; its
one-letter endpoint must therefore use the actual deadline difference rather
than the noninitial formula.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Iterable, Sequence

try:
    from .kernel_mass_potential import (
        Transformation,
        kernel_partition,
        mass_kernel_mass,
        mass_partition,
        mass_rank,
        pushforward_mass,
    )
    from .mass_rank_debt_n6 import mass_deadline
except ImportError:
    from kernel_mass_potential import (
        Transformation,
        kernel_partition,
        mass_kernel_mass,
        mass_partition,
        mass_rank,
        pushforward_mass,
    )
    from mass_rank_debt_n6 import mass_deadline


Mass = tuple[int, ...]
Kernel = tuple[tuple[int, ...], ...]


def support(mass: Sequence[int]) -> tuple[int, ...]:
    """Return the occupied coordinates in increasing order."""
    if any(value < 0 for value in mass):
        raise ValueError("mass entries must be nonnegative")
    return tuple(index for index, value in enumerate(mass) if value)


def validate_mass(mass: Sequence[int], n: int) -> Mass:
    """Validate and freeze a total-mass `
`` vector."""
    frozen = tuple(int(value) for value in mass)
    if len(frozen) != n:
        raise ValueError("mass vector must have n coordinates")
    if any(value < 0 for value in frozen):
        raise ValueError("mass entries must be nonnegative")
    if sum(frozen) != n:
        raise ValueError("mass vector must have total mass n")
    if not support(frozen):
        raise ValueError("mass vector must have nonempty support")
    return frozen


def validate_transformation(transformation: Sequence[int], n: int) -> Transformation:
    """Validate a deterministic transformation on ``range(n)``."""
    frozen = tuple(int(value) for value in transformation)
    if len(frozen) != n or any(value < 0 or value >= n for value in frozen):
        raise ValueError("transformation must map range(n) to range(n)")
    return frozen


def transformation_rank(transformation: Sequence[int]) -> int:
    return len(set(transformation))


def kernel_blocks(defect: Sequence[int], n: int | None = None) -> Kernel:
    """Return the fixed input kernel partition ``K_d``."""
    if n is None:
        n = len(defect)
    return kernel_partition(validate_transformation(defect, n))


def is_partial_transversal(
    occupied_support: Iterable[int], kernel: Kernel
) -> bool:
    """Whether a support meets every kernel block in at most one point."""
    occupied = set(occupied_support)
    return all(sum(index in occupied for index in block) <= 1 for block in kernel)


def kernel_occupancy(
    mass: Sequence[int], kernel: Kernel
) -> tuple[dict[str, Any], ...]:
    """Return fixed-kernel support/mass occupancy, including singleton blocks."""
    occupied = set(support(mass))
    rows = []
    for block in kernel:
        block_support = tuple(index for index in block if index in occupied)
        rows.append(
            {
                "block": list(block),
                "occupied_support": list(block_support),
                "occupied_count": len(block_support),
                "excess": max(len(block_support) - 1, 0),
                "mass": [int(mass[index]) for index in block_support],
            }
        )
    return tuple(rows)


def fixed_kernel_fusion_data(
    mass: Sequence[int], defect: Sequence[int]
) -> dict[str, Any]:
    """Compute ``q_d``, ``DeltaM_d`` and the explicit fusion surplus.

    ``surplus_formula`` is the stated maturity increment minus one.  It is an
    exact deadline surplus for noninitial sources (``r<n``).  At the uniform
    initial source, ``mass_deadline`` uses the terminal initial convention
    ``tau(1)=0``; ``actual_deadline_surplus`` records that boundary value.
    """
    n = len(mass)
    source = validate_mass(mass, n)
    d = validate_transformation(defect, n)
    kernel = kernel_blocks(d, n)
    occupied = set(support(source))
    target = pushforward_mass(source, d)
    rank_before = mass_rank(source)
    rank_after = mass_rank(target)
    occupancy = kernel_occupancy(source, kernel)
    q = sum(row["excess"] for row in occupancy)
    delta_m = sum(
        source[left] * source[right]
        for row in occupancy
        for offset, left in enumerate(row["occupied_support"])
        for right in row["occupied_support"][offset + 1 :]
    )
    if q != rank_before - rank_after:
        raise AssertionError("fixed-kernel occupancy does not recover rank drop")
    if delta_m != mass_kernel_mass(target) - mass_kernel_mass(source):
        raise AssertionError("fixed-kernel occupancy does not recover DeltaM")
    if rank_before <= 1:
        raise ValueError("fusion data requires a non-reset source rank")

    formula_increment = 2 * delta_m + q * (
        2 * rank_before - q - n - 1
    )
    formula_surplus = formula_increment - 1
    source_tau = mass_deadline(source, n, True)
    target_tau = mass_deadline(target, n, True)
    actual_increment = target_tau - source_tau
    actual_surplus = actual_increment - 1
    formula_applies = rank_before < n
    if formula_applies and actual_increment != formula_increment:
        raise AssertionError("noninitial fixed-kernel maturity identity failed")
    return {
        "source": source,
        "target": target,
        "kernel": [list(block) for block in kernel],
        "source_support": list(support(source)),
        "target_support": list(support(target)),
        "source_partition": list(mass_partition(source)),
        "target_partition": list(mass_partition(target)),
        "rank_before": rank_before,
        "rank_after": rank_after,
        "rank_drop": q,
        "q_d": q,
        "delta_m_d": delta_m,
        "occupancy": list(occupancy),
        "surplus_formula": formula_surplus,
        "formula_increment": formula_increment,
        "formula_applies_to_deadline": formula_applies,
        "source_tau": source_tau,
        "target_tau": target_tau,
        "actual_deadline_increment": actual_increment,
        "actual_deadline_surplus": actual_surplus,
        "maturity_identity_holds": (not formula_applies)
        or actual_increment == formula_increment,
        "partial_transversal_before": is_partial_transversal(occupied, kernel),
        "strict_drop": rank_after < rank_before,
    }


def unique_rank_decreasing_letter(
    letters: Sequence[Transformation], n: int
) -> tuple[int, Transformation]:
    """Return the unique globally rank-decreasing letter, or raise."""
    frozen = tuple(validate_transformation(letter, n) for letter in letters)
    decreasing = [
        (index, letter)
        for index, letter in enumerate(frozen)
        if transformation_rank(letter) < n
    ]
    if len(decreasing) != 1:
        raise ValueError(
            "single-defect slice requires exactly one globally rank-decreasing letter"
        )
    return decreasing[0]


def single_defect_alphabet_certificate(
    letters: Sequence[Transformation], n: int
) -> dict[str, Any]:
    """Certify the structural assumptions used by the transport reduction."""
    frozen = tuple(validate_transformation(letter, n) for letter in letters)
    defect_index, defect = unique_rank_decreasing_letter(frozen, n)
    permutation_indices = [
        index for index, letter in enumerate(frozen) if index != defect_index
    ]
    if any(transformation_rank(frozen[index]) != n for index in permutation_indices):
        raise AssertionError("non-defect letter is not rank preserving")
    return {
        "alphabet_size": len(frozen),
        "state_count": n,
        "defect_index": defect_index,
        "defect": list(defect),
        "defect_rank": transformation_rank(defect),
        "kernel": [list(block) for block in kernel_blocks(defect, n)],
        "permutation_indices": permutation_indices,
        "all_nondefect_letters_are_permutations": True,
        "single_global_defect": True,
    }


def _rank_preserving_successors(
    mass: Mass,
    letters: Sequence[Transformation],
    n: int,
) -> list[dict[str, Any]]:
    source_rank = mass_rank(mass)
    rows = []
    for letter_index, letter in enumerate(letters):
        target = pushforward_mass(mass, letter)
        target_rank = mass_rank(target)
        if target_rank == source_rank:
            rows.append(
                {
                    "letter": letter_index,
                    "target": tuple(target),
                    "target_rank": target_rank,
                    "kind": "transport",
                }
            )
    return rows


def fixed_kernel_transport_graph(
    source_mass: Sequence[int],
    letters: Sequence[Transformation],
    n: int,
    *,
    defect_index: int | None = None,
) -> dict[str, Any]:
    """Build the reachable rank-preserving graph at ``rank(source_mass)``.

    Boundary vertices are rank-``r`` masses whose support is not a partial
    transversal of ``K_d``.  From such a vertex the defect letter is a strict
    exit, but it is not included as a transport edge when it lowers rank.
    Other letters are retained whenever they preserve rank.  Distances are
    directed and measured from the source to boundary vertices.
    """
    source = validate_mass(source_mass, n)
    if mass_rank(source) <= 1:
        raise ValueError("transport graph requires source rank greater than one")
    frozen_letters = tuple(validate_transformation(letter, n) for letter in letters)
    actual_defect_index, actual_defect = unique_rank_decreasing_letter(
        frozen_letters, n
    )
    if defect_index is None:
        defect_index, defect = actual_defect_index, actual_defect
    else:
        if defect_index != actual_defect_index:
            raise ValueError("defect_index does not identify the unique defect")
        defect = actual_defect
    kernel = kernel_blocks(defect, n)
    rank = mass_rank(source)
    distances: dict[Mass, int] = {source: 0}
    words: dict[Mass, tuple[int, ...]] = {source: tuple()}
    edges: list[dict[str, Any]] = []
    queue = deque([source])
    while queue:
        current = queue.popleft()
        current_distance = distances[current]
        current_word = words[current]
        current_boundary = not is_partial_transversal(support(current), kernel)
        for row in _rank_preserving_successors(current, frozen_letters, n):
            target = tuple(row["target"])
            edge = {
                "source": list(current),
                "target": list(target),
                "letter": row["letter"],
                "kind": row["kind"],
                "source_boundary": current_boundary,
                "target_boundary": not is_partial_transversal(
                    support(target), kernel
                ),
            }
            edges.append(edge)
            if target not in distances:
                distances[target] = current_distance + 1
                words[target] = current_word + (row["letter"],)
                queue.append(target)

    boundary = [
        mass for mass in distances if not is_partial_transversal(support(mass), kernel)
    ]
    boundary.sort(key=lambda mass: (distances[mass], mass))
    distance = min((distances[mass] for mass in boundary), default=None)
    representative = None
    first_exit = None
    exit_data = None
    if distance is not None:
        boundary_mass = next(mass for mass in boundary if distances[mass] == distance)
        transport_word = words[boundary_mass]
        representative = {
            "boundary_mass": list(boundary_mass),
            "transport_word": list(transport_word),
            "distance_to_boundary": distance,
            "first_exit_word": list(transport_word + (defect_index,)),
        }
        first_exit = pushforward_mass(boundary_mass, defect)
        exit_data = fixed_kernel_fusion_data(boundary_mass, defect)
        if mass_rank(first_exit) >= rank:
            raise AssertionError("boundary representative did not strictly exit")
    return {
        "source_mass": list(source),
        "source_rank": rank,
        "defect_index": defect_index,
        "defect": list(defect),
        "kernel": [list(block) for block in kernel],
        "state_count": len(distances),
        "edge_count": len(edges),
        "states": [list(mass) for mass in sorted(distances, key=lambda m: (distances[m], m))],
        "distances": {str(list(mass)): distances[mass] for mass in distances},
        "edges": edges,
        "boundary_states": [list(mass) for mass in boundary],
        "boundary_distance": distance,
        "omega_d": None if distance is None else distance + 1,
        "representative": representative,
        "representative_exit_target": None
        if first_exit is None
        else list(first_exit),
        "representative_exit_data": exit_data,
        "first_exit_form": "u d" if distance is not None else None,
        "normal_form_holds": (
            distance is None
            or (
                representative is not None
                and representative["first_exit_word"][-1] == defect_index
                and mass_rank(tuple(first_exit)) < rank
            )
        ),
        "directed_distance_convention": "shortest directed rank-preserving path to fixed-kernel boundary",
    }


def endpoint_conditioned_boundaries(
    source_mass: Sequence[int],
    letters: Sequence[Transformation],
    n: int,
    *,
    defect_index: int | None = None,
) -> dict[str, Any]:
    """Group fixed-kernel boundary vertices by their terminal endpoint.

    For each lower-rank endpoint `
u``, this returns the directed distance
    from ``source_mass`` to the nearest reachable rank-preserving placement
    ``eta`` with ``d_*eta=nu``. Thus ``ell_d^*(mu,nu)=distance+1``. Taking the
    minimum over endpoint groups recovers ``omega_d(mu)``; choosing one group
    does not require choosing the globally nearest boundary.
    """
    graph = fixed_kernel_transport_graph(
        source_mass, letters, n, defect_index=defect_index
    )
    defect_index = int(graph["defect_index"])
    defect = tuple(graph["defect"])
    source = tuple(graph["source_mass"])
    rank = int(graph["source_rank"])

    distances: dict[Mass, int] = {source: 0}
    words: dict[Mass, tuple[int, ...]] = {source: tuple()}
    queue = deque([source])
    frozen_letters = tuple(validate_transformation(letter, n) for letter in letters)
    while queue:
        current = queue.popleft()
        for row in _rank_preserving_successors(current, frozen_letters, n):
            target = tuple(row["target"])
            if target not in distances:
                distances[target] = distances[current] + 1
                words[target] = words[current] + (int(row["letter"]),)
                queue.append(target)

    endpoint_rows: dict[Mass, dict[str, Any]] = {}
    for boundary_row in graph["boundary_states"]:
        boundary = tuple(boundary_row)
        endpoint = pushforward_mass(boundary, defect)
        if mass_rank(endpoint) >= rank:
            raise AssertionError("fixed-kernel boundary did not strictly drop rank")
        row = {
            "endpoint": list(endpoint),
            "endpoint_rank": mass_rank(endpoint),
            "boundary_mass": list(boundary),
            "boundary_distance": distances[boundary],
            "ell_d_star": distances[boundary] + 1,
            "transport_word": list(words[boundary]),
            "first_exit_word": list(words[boundary] + (defect_index,)),
        }
        previous = endpoint_rows.get(endpoint)
        if previous is None or (
            row["ell_d_star"], row["boundary_mass"], row["transport_word"]
        ) < (
            previous["ell_d_star"],
            previous["boundary_mass"],
            previous["transport_word"],
        ):
            endpoint_rows[endpoint] = row
    rows = sorted(
        endpoint_rows.values(),
        key=lambda row: (
            row["ell_d_star"],
            row["endpoint"],
            row["boundary_mass"],
        ),
    )
    minimum = min((row["ell_d_star"] for row in rows), default=None)
    if minimum != graph["omega_d"]:
        raise AssertionError("endpoint-conditioned minima do not recover omega_d")
    return {
        "source_mass": list(source),
        "source_rank": rank,
        "defect_index": defect_index,
        "kernel": graph["kernel"],
        "endpoints": rows,
        "endpoint_count": len(rows),
        "minimum_ell_d_star": minimum,
        "omega_d": graph["omega_d"],
        "minimum_identity_holds": minimum == graph["omega_d"],
    }


def rewarded_boundary_frontier(
    source_mass: Sequence[int],
    letters: Sequence[Transformation],
    n: int,
    capacities: dict[Mass, int | None],
    *,
    defect_index: int | None = None,
) -> dict[str, Any]:
    """Return all reachable fusion boundaries and their reward-cost frontier.

    Unlike :func:`endpoint_conditioned_boundaries`, this retains every
    reachable boundary placement. A farther placement with the same endpoint
    can carry greater fixed-kernel collision credit and must not be discarded
    before comparing ``reward - distance``.
    """
    graph = fixed_kernel_transport_graph(
        source_mass, letters, n, defect_index=defect_index
    )
    source = tuple(graph["source_mass"])
    defect_index = int(graph["defect_index"])
    defect = tuple(graph["defect"])
    frozen_letters = tuple(validate_transformation(letter, n) for letter in letters)
    distances: dict[Mass, int] = {source: 0}
    words: dict[Mass, tuple[int, ...]] = {source: tuple()}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for edge in _rank_preserving_successors(current, frozen_letters, n):
            target = tuple(edge["target"])
            if target not in distances:
                distances[target] = distances[current] + 1
                words[target] = words[current] + (int(edge["letter"]),)
                queue.append(target)

    if mass_rank(source) >= n:
        raise ValueError("rewarded boundary compression requires a noninitial source rank")
    rows = []
    for raw_boundary in graph["boundary_states"]:
        boundary = tuple(raw_boundary)
        fusion = fixed_kernel_fusion_data(boundary, defect)
        endpoint = tuple(fusion["target"])
        capacity = capacities.get(endpoint)
        distance = distances[boundary]
        credit = int(fusion["formula_increment"])
        surplus = credit - distance - 1
        total_reward = None if capacity is None else credit + int(capacity)
        psi_value = None if total_reward is None else total_reward - distance - 1
        rows.append({
            "boundary_mass": list(boundary),
            "endpoint": list(endpoint),
            "endpoint_rank": mass_rank(endpoint),
            "transport_distance": distance,
            "corridor_length": distance + 1,
            "transport_word": list(words[boundary]),
            "first_exit_word": list(words[boundary] + (defect_index,)),
            "q_d": fusion["q_d"],
            "delta_m_d": fusion["delta_m_d"],
            "fusion_credit": credit,
            "surplus": surplus,
            "H_endpoint": capacity,
            "total_reward": total_reward,
            "psi_value": psi_value,
        })

    viable = [row for row in rows if row["H_endpoint"] is not None]
    for row in rows:
        reward = row["total_reward"]
        row["pareto_dominated"] = reward is None or any(
            other is not row
            and other["total_reward"] is not None
            and other["transport_distance"] <= row["transport_distance"]
            and other["total_reward"] >= reward
            and (
                other["transport_distance"] < row["transport_distance"]
                or other["total_reward"] > reward
            )
            for other in rows
        )
    frontier = [row for row in rows if not row["pareto_dominated"]]
    endpoint_best: dict[Mass, dict[str, Any]] = {}
    endpoint_credit_failures = 0
    for row in viable:
        endpoint = tuple(row["endpoint"])
        expected_credit = mass_deadline(endpoint, n, True) - mass_deadline(source, n, True)
        if row["fusion_credit"] != expected_credit:
            endpoint_credit_failures += 1
        previous = endpoint_best.get(endpoint)
        if previous is None or (
            row["transport_distance"], row["boundary_mass"]
        ) < (
            previous["transport_distance"], previous["boundary_mass"]
        ):
            endpoint_best[endpoint] = row
    endpoint_rows = []
    for endpoint, boundary_row in endpoint_best.items():
        ell_star = int(boundary_row["transport_distance"]) + 1
        reward = (
            mass_deadline(endpoint, n, True)
            - mass_deadline(source, n, True)
            + int(boundary_row["H_endpoint"])
        )
        endpoint_rows.append({
            "endpoint": list(endpoint),
            "ell_d_star": ell_star,
            "reward": reward,
            "value": reward - ell_star,
            "H_endpoint": boundary_row["H_endpoint"],
            "tau_endpoint": mass_deadline(endpoint, n, True),
            "representative_boundary": boundary_row["boundary_mass"],
        })
    for row in endpoint_rows:
        row["pareto_dominated"] = any(
            other is not row
            and other["ell_d_star"] <= row["ell_d_star"]
            and other["reward"] >= row["reward"]
            and (
                other["ell_d_star"] < row["ell_d_star"]
                or other["reward"] > row["reward"]
            )
            for other in endpoint_rows
        )
    endpoint_frontier = [row for row in endpoint_rows if not row["pareto_dominated"]]
    gamma = max((row["surplus"] for row in viable), default=None)
    psi = max((row["psi_value"] for row in viable), default=None)
    endpoint_value = max((row["value"] for row in endpoint_rows), default=None)
    if endpoint_value != psi:
        raise AssertionError("fixed-endpoint compression changed Psi_d")
    return {
        "source_mass": list(source),
        "source_rank": mass_rank(source),
        "defect_index": defect_index,
        "boundary_count": len(rows),
        "viable_boundary_count": len(viable),
        "frontier_count": len(frontier),
        "endpoint_count": len(endpoint_rows),
        "endpoint_frontier_count": len(endpoint_frontier),
        "endpoint_credit_failures": endpoint_credit_failures,
        "Gamma_d": gamma,
        "Psi_d": psi,
        "boundaries": sorted(rows, key=lambda row: (
            row["transport_distance"],
            -(row["total_reward"] if row["total_reward"] is not None else -10**9),
            row["boundary_mass"],
        )),
        "pareto_frontier": sorted(frontier, key=lambda row: (
            row["transport_distance"], -row["total_reward"], row["boundary_mass"]
        )),
        "endpoint_candidates": sorted(endpoint_rows, key=lambda row: (
            row["ell_d_star"], -row["reward"], row["endpoint"]
        )),
        "endpoint_pareto_frontier": sorted(endpoint_frontier, key=lambda row: (
            row["ell_d_star"], -row["reward"], row["endpoint"]
        )),
        "endpoint_compression_holds": endpoint_value == psi
        and endpoint_credit_failures == 0,
        "solvent": psi is not None and psi >= 0,
    }


def first_exit_normal_form(
    source_mass: Sequence[int],
    letters: Sequence[Transformation],
    n: int,
    *,
    defect_index: int | None = None,
) -> dict[str, Any]:
    """Return the single-defect first-exit certificate for one source mass."""
    certificate = single_defect_alphabet_certificate(letters, n)
    if defect_index is None:
        defect_index = certificate["defect_index"]
    graph = fixed_kernel_transport_graph(
        source_mass, letters, n, defect_index=defect_index
    )
    return {
        "alphabet": certificate,
        "transport": graph,
        "strict_exit_only_letter": defect_index,
        "strict_first_exit_normal_form": graph["first_exit_form"] == "u d",
        "omega_d": graph["omega_d"],
    }


__all__ = [
    "Kernel",
    "Mass",
    "Transformation",
    "fixed_kernel_fusion_data",
    "fixed_kernel_transport_graph",
    "endpoint_conditioned_boundaries",
    "rewarded_boundary_frontier",
    "first_exit_normal_form",
    "is_partial_transversal",
    "kernel_blocks",
    "kernel_occupancy",
    "single_defect_alphabet_certificate",
    "support",
    "transformation_rank",
    "unique_rank_decreasing_letter",
    "validate_mass",
    "validate_transformation",
]
