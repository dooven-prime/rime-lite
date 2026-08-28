#!/usr/bin/env python3
"""Layer controls separating escape wait from terminal fiber incidence.

For each reachable rank r, this module records

    Omega_r       = worst shortest rank-drop escape length,
    epsilon_r     = worst-state best terminal excess among shortest escapes,
    kappa_r       = Omega_r / epsilon_r.

The exact incidence potential satisfies theta_r <= kappa_r.  Consequently the
tail-max construction from ``fiber_incidence_potential`` gives a certified
upper envelope for Phi_FI.  This is useful only when epsilon_r exceeds one;
otherwise it deliberately reduces to the existing Omega_r control.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

from fiber_incidence_potential import fiber_incidence_potential
from path_potential import cerny_transition
from registry import (
    Transition,
    fiber_excess,
    payload_digest,
    reachable_subset_automaton,
    shortest_subset_reset_word,
)


def capacity_profile_bound(
    state_count: int,
    lower_profile: dict[int, int],
    active_ranks: set[int] | None = None,
) -> dict[str, Any]:
    """Return the Pin--Frankl bound induced by a capacity lower profile.

    ``lower_profile[r]=h_{n,r}`` means that every relevant terminal escape in
    rank ``r`` has fiber excess at least ``h_{n,r}``.  The theorem then uses
    ``Omega_r <= binom(n-r+2,2)`` and charges each unit drop by the ratio
    ``binom(n-r+2,2)/h_{n,r}``.  Missing inactive ranks contribute zero.
    """
    if state_count < 2:
        raise ValueError("state_count must be at least two")
    ranks = set(range(2, state_count + 1)) if active_ranks is None else set(active_ranks)
    if any(rank_value < 2 or rank_value > state_count for rank_value in ranks):
        raise ValueError("active ranks must lie in [2,state_count]")
    if any(rank_value not in lower_profile for rank_value in ranks):
        missing = sorted(ranks.difference(lower_profile))
        raise ValueError(f"capacity profile missing ranks: {missing}")
    ratios: dict[int, Fraction] = {}
    for rank_value in sorted(ranks):
        capacity = lower_profile[rank_value]
        if capacity < 1:
            raise ValueError("capacity lower bounds must be positive")
        ratios[rank_value] = Fraction(
            comb(state_count - rank_value + 2, 2), capacity
        )
    tail: Fraction | None = None
    tail_profile: dict[int, Fraction] = {}
    for index in range(state_count, 1, -1):
        if index in ratios and (tail is None or ratios[index] > tail):
            tail = ratios[index]
        if tail is not None:
            tail_profile[index] = tail
    bound = sum(tail_profile.values(), Fraction(0))
    return {
        "state_count": state_count,
        "active_ranks": sorted(ranks),
        "lower_profile": {str(rank_value): lower_profile[rank_value] for rank_value in sorted(ranks)},
        "pin_frankl_ratio_by_rank": {
            str(rank_value): {"numerator": value.numerator, "denominator": value.denominator}
            for rank_value, value in sorted(ratios.items())
        },
        "tail_ratio_by_index": {
            str(index): {"numerator": value.numerator, "denominator": value.denominator}
            for index, value in sorted(tail_profile.items())
        },
        "bound": {"numerator": bound.numerator, "denominator": bound.denominator},
        "claim_status": "Theorem from imported Pin--Frankl layer bound plus capacity profile",
    }


def layer_incidence_controls(transition: Transition) -> dict[int, dict[str, Any]]:
    """Return exact Omega/epsilon/kappa controls for reachable rank layers."""
    _distance, _words, edges = reachable_subset_automaton(transition)
    by_rank: dict[int, list[tuple[int, ...]]] = {}
    for subset in edges:
        by_rank.setdefault(len(subset), []).append(subset)
    controls: dict[int, dict[str, Any]] = {}
    for rank_value, nodes in sorted(by_rank.items()):
        if rank_value == 1:
            continue
        node_rows = []
        for start in sorted(nodes):
            distance = {start: 0}
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for target in edges[current]:
                    if len(target) == rank_value and target not in distance:
                        distance[target] = distance[current] + 1
                        queue.append(target)
            exits = []
            for source, path_length in distance.items():
                for letter, target in enumerate(edges[source]):
                    if len(target) >= rank_value:
                        continue
                    excess = fiber_excess(transition[letter], source)
                    assert excess > 0
                    exits.append({
                        "segment_length": path_length + 1,
                        "fiber_excess": excess,
                        "source": list(source),
                        "letter": letter,
                        "target": list(target),
                    })
            if not exits:
                continue
            shortest = min(row["segment_length"] for row in exits)
            shortest_exits = [row for row in exits if row["segment_length"] == shortest]
            node_rows.append({
                "subset": list(start),
                "shortest_escape_length": shortest,
                "best_shortest_escape_excess": max(
                    row["fiber_excess"] for row in shortest_exits
                ),
                "minimum_boundary_excess": min(
                    row["fiber_excess"] for row in exits
                ),
                "boundary_edge_count": len(exits),
            })
        if len(node_rows) != len(nodes):
            controls[rank_value] = {
                "status": "INFINITE_LAYER_ESCAPE",
                "reachable_subset_count": len(nodes),
                "node_rows": node_rows,
            }
            continue
        omega = max(row["shortest_escape_length"] for row in node_rows)
        epsilon = min(row["best_shortest_escape_excess"] for row in node_rows)
        unit_state_rows = [
            row for row in node_rows
            if row["best_shortest_escape_excess"] == 1
        ]
        high_state_rows = [
            row for row in node_rows
            if row["best_shortest_escape_excess"] > 1
        ]
        statewise_ratios = [
            Fraction(
                row["shortest_escape_length"],
                row["best_shortest_escape_excess"],
            )
            for row in node_rows
        ]
        chi = max(statewise_ratios)
        unit_wait = max(
            (row["shortest_escape_length"] for row in unit_state_rows),
            default=None,
        )
        high_ratio = max(
            (
                Fraction(
                    row["shortest_escape_length"],
                    row["best_shortest_escape_excess"],
                )
                for row in high_state_rows
            ),
            default=None,
        )
        u_value = 0 if unit_wait is None else unit_wait
        h_value = Fraction(0) if high_ratio is None else high_ratio
        boundary_capacity = min(row["minimum_boundary_excess"] for row in node_rows)
        unit_boundary_count = sum(
            row["minimum_boundary_excess"] == 1 for row in node_rows
        )
        kappa = Fraction(omega, epsilon)
        controls[rank_value] = {
            "status": "FINITE_LAYER_ESCAPE",
            "reachable_subset_count": len(nodes),
            "Omega_r": omega,
            "epsilon_r": epsilon,
            "statewise_ratio_chi_r": {
                "numerator": chi.numerator,
                "denominator": chi.denominator,
            },
            "unit_shortest_escape_state_count": len(unit_state_rows),
            "high_capacity_shortest_escape_state_count": len(high_state_rows),
            "Omega_r_unit_states": unit_wait,
            "u_r": u_value,
            "high_capacity_ratio_r": (
                None if high_ratio is None else {
                    "numerator": high_ratio.numerator,
                    "denominator": high_ratio.denominator,
                }
            ),
            "h_r": {
                "numerator": h_value.numerator,
                "denominator": h_value.denominator,
            },
            "empty_branch_maximum_convention": 0,
            "statewise_branch_identity_holds": chi == max(
                Fraction(u_value), h_value
            ),
            "boundary_capacity_r": boundary_capacity,
            "unit_defect_boundary_state_count": unit_boundary_count,
            "two_thick_boundary": boundary_capacity >= 2,
            "kappa_r": {
                "numerator": kappa.numerator,
                "denominator": kappa.denominator,
            },
            "chi_at_most_kappa": chi <= kappa,
            "chi_strictly_improves_kappa": chi < kappa,
            "improves_Omega": epsilon > 1,
            "node_rows": node_rows,
        }
    return controls


def boundary_thickness_profile(
    controls: dict[int, dict[str, Any]],
    threshold: int = 2,
) -> dict[str, Any]:
    """Classify reachable layers by a declared q-thick boundary condition.

    A rank is ``q``-thick when every reachable subset in that layer has no
    positive-incidence boundary edge below ``q``.  This is stronger than the
    epsilon statistic, which only inspects shortest exits.
    """
    if threshold < 1:
        raise ValueError("threshold must be positive")
    finite = {
        rank_value: row
        for rank_value, row in controls.items()
        if row.get("status") == "FINITE_LAYER_ESCAPE"
    }
    thick = sorted(
        rank_value for rank_value, row in finite.items()
        if row.get("boundary_capacity_r", 0) >= threshold
    )
    unit = sorted(
        rank_value for rank_value, row in finite.items()
        if row.get("boundary_capacity_r", 0) == 1
    )
    return {
        "threshold": threshold,
        "q_thick_ranks": thick,
        "unit_capacity_ranks": unit,
        "finite_rank_count": len(finite),
        "class_condition": (
            "for every reachable rank-r subset T and generator a, "
            "Exc_a(T)>0 implies Exc_a(T)>=q"
        ),
        "claim_status": "Exact finite class certificate",
    }


def incidence_control_certificate(transition: Transition) -> dict[str, Any]:
    """Compare exact Phi_FI with its Omega/epsilon upper envelope."""
    controls = layer_incidence_controls(transition)
    n = len(transition[0])
    infinite_active_ranks = sorted(
        rank_value for rank_value, row in controls.items()
        if row.get("status") == "INFINITE_LAYER_ESCAPE"
    )
    global_finite_bound_available = not infinite_active_ranks
    kappa: dict[int, Fraction] = {}
    chi: dict[int, Fraction] = {}
    unit_wait: dict[int, Fraction] = {}
    high_ratio: dict[int, Fraction] = {}
    for rank_value, row in controls.items():
        if row["status"] == "FINITE_LAYER_ESCAPE":
            kappa[rank_value] = Fraction(
                row["kappa_r"]["numerator"], row["kappa_r"]["denominator"]
            )
            chi[rank_value] = Fraction(
                row["statewise_ratio_chi_r"]["numerator"],
                row["statewise_ratio_chi_r"]["denominator"],
            )
            unit_wait[rank_value] = Fraction(row["u_r"])
            high_ratio[rank_value] = Fraction(
                row["h_r"]["numerator"], row["h_r"]["denominator"]
            )
    tail: Fraction | None = None
    lambda_upper: dict[int, Fraction] = {}
    for index in range(n, 1, -1):
        if index in kappa and (tail is None or kappa[index] > tail):
            tail = kappa[index]
        if tail is not None:
            lambda_upper[index] = tail
    phi_upper_by_rank: dict[int, Fraction] = {1: Fraction(0)}
    running = Fraction(0)
    for rank_value in range(2, n + 1):
        running += lambda_upper.get(rank_value, Fraction(0))
        phi_upper_by_rank[rank_value] = running
    statewise_tail: Fraction | None = None
    statewise_lambda_upper: dict[int, Fraction] = {}
    for index in range(n, 1, -1):
        if index in chi and (
            statewise_tail is None or chi[index] > statewise_tail
        ):
            statewise_tail = chi[index]
        if statewise_tail is not None:
            statewise_lambda_upper[index] = statewise_tail
    unit_tail = Fraction(0)
    high_tail = Fraction(0)
    unit_tail_by_index: dict[int, Fraction] = {}
    high_tail_by_index: dict[int, Fraction] = {}
    combined_tail_by_index: dict[int, Fraction] = {}
    for index in range(n, 1, -1):
        unit_tail = max(unit_tail, unit_wait.get(index, Fraction(0)))
        high_tail = max(high_tail, high_ratio.get(index, Fraction(0)))
        unit_tail_by_index[index] = unit_tail
        high_tail_by_index[index] = high_tail
        combined_tail_by_index[index] = max(unit_tail, high_tail)
        if combined_tail_by_index[index] != statewise_lambda_upper.get(
            index, Fraction(0)
        ):
            raise AssertionError(f"unit/high tail identity failed at index {index}")
    phi_statewise_upper_by_rank: dict[int, Fraction] = {1: Fraction(0)}
    statewise_running = Fraction(0)
    for rank_value in range(2, n + 1):
        statewise_running += statewise_lambda_upper.get(
            rank_value, Fraction(0)
        )
        phi_statewise_upper_by_rank[rank_value] = statewise_running
    combined_statewise_bound = sum(
        combined_tail_by_index.values(), Fraction(0)
    )
    if combined_statewise_bound != phi_statewise_upper_by_rank.get(
        n, Fraction(0)
    ):
        raise AssertionError("combined unit/high bound differs from chi tail sum")
    exact = fiber_incidence_potential(transition)
    exact_phi = (
        None if exact["initial_potential"] is None
        else Fraction(
            exact["initial_potential"]["numerator"],
            exact["initial_potential"]["denominator"],
        )
    )
    reset = shortest_subset_reset_word(transition)
    reset_depth = None if reset is None else len(reset)
    upper = phi_upper_by_rank.get(n)
    statewise_upper = phi_statewise_upper_by_rank.get(n)
    if exact_phi is not None and upper is not None and exact_phi > upper:
        raise AssertionError("Omega/epsilon envelope is below exact Phi_FI")
    if reset_depth is not None and upper is not None and reset_depth > upper:
        raise AssertionError("Omega/epsilon potential failed to bound reset depth")
    if exact_phi is not None and statewise_upper is not None:
        if exact_phi > statewise_upper:
            raise AssertionError("statewise ratio envelope is below exact Phi_FI")
        if upper is not None and statewise_upper > upper:
            raise AssertionError("statewise ratio envelope exceeds Omega/epsilon")
    for rank_value, value in chi.items():
        theta = exact["theta_by_rank"].get(str(rank_value))
        if theta is not None and Fraction(
            theta["numerator"], theta["denominator"]
        ) > value:
            raise AssertionError(f"theta exceeds chi at rank {rank_value}")
    return {
        "carrier": "fiber_incidence_layer_controls",
        "controls": {str(rank_value): row for rank_value, row in controls.items()},
        "lambda_upper": {
            str(index): {"numerator": value.numerator, "denominator": value.denominator}
            for index, value in sorted(lambda_upper.items())
        },
        "statewise_ratio_chi_by_rank": {
            str(rank_value): {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for rank_value, value in sorted(chi.items())
        },
        "unit_wait_u_by_rank": {
            str(rank_value): int(value)
            for rank_value, value in sorted(unit_wait.items())
        },
        "high_capacity_h_by_rank": {
            str(rank_value): {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for rank_value, value in sorted(high_ratio.items())
        },
        "statewise_lambda_upper": {
            str(index): {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for index, value in sorted(statewise_lambda_upper.items())
        },
        "statewise_branch_tail_profile": {
            str(index): {
                "unit_tail_u_bar_j": int(unit_tail_by_index[index]),
                "high_tail_h_bar_j": {
                    "numerator": high_tail_by_index[index].numerator,
                    "denominator": high_tail_by_index[index].denominator,
                },
                "chi_tail": {
                    "numerator": combined_tail_by_index[index].numerator,
                    "denominator": combined_tail_by_index[index].denominator,
                },
                "tail_identity_holds": combined_tail_by_index[index]
                == max(unit_tail_by_index[index], high_tail_by_index[index]),
            }
            for index in sorted(combined_tail_by_index)
        },
        "combined_statewise_bound_initial": {
            "numerator": combined_statewise_bound.numerator,
            "denominator": combined_statewise_bound.denominator,
        } if global_finite_bound_available else None,
        "partial_finite_rank_statewise_sum": {
            "numerator": combined_statewise_bound.numerator,
            "denominator": combined_statewise_bound.denominator,
        },
        "phi_statewise_upper_by_rank": {
            str(rank_value): {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for rank_value, value in sorted(phi_statewise_upper_by_rank.items())
        },
        "phi_upper_by_rank": {
            str(rank_value): {"numerator": value.numerator, "denominator": value.denominator}
            for rank_value, value in sorted(phi_upper_by_rank.items())
        },
        "exact_phi_fi": None if exact_phi is None else {
            "numerator": exact_phi.numerator, "denominator": exact_phi.denominator
        },
        "shortest_reset_depth": reset_depth,
        "upper_slack": None if reset_depth is None or upper is None else {
            "numerator": (upper - reset_depth).numerator,
            "denominator": (upper - reset_depth).denominator,
        },
        "statewise_upper_slack": (
            None if reset_depth is None or statewise_upper is None else {
                "numerator": (statewise_upper - reset_depth).numerator,
                "denominator": (statewise_upper - reset_depth).denominator,
            }
        ),
        "claim_boundary": (
            "exact finite-escape Omega/epsilon and statewise unit/high control; "
            "no universal bound on its initial value is claimed"
        ),
        "escape_semantics": {
            "finite_escape_active_ranks": sorted(chi),
            "infinite_escape_active_ranks": infinite_active_ranks,
            "empty_branch_maximum": 0,
            "ratio_domain": "finite-escape active ranks only",
            "global_finite_bound_status": (
                "AVAILABLE"
                if global_finite_bound_available
                else "UNAVAILABLE_INFINITE_ESCAPE_ACTIVE_RANK"
            ),
        },
    }


def waiting_capacity_tradeoff_certificate(
    transition: Transition,
    declared_lower_profile: dict[int, int] | None = None,
) -> dict[str, Any]:
    """Assemble the waiting/capacity tradeoff and its class-bound interface.

    When no profile is supplied, the exact ``epsilon_r`` values are used.  A
    supplied profile is treated as a declared class hypothesis and is checked
    against the finite carrier before the Pin--Frankl profile bound is emitted.
    """
    controls = layer_incidence_controls(transition)
    n = len(transition[0])
    finite_controls = {
        rank_value: row
        for rank_value, row in controls.items()
        if row.get("status") == "FINITE_LAYER_ESCAPE"
    }
    exact_profile = {
        rank_value: row["epsilon_r"]
        for rank_value, row in finite_controls.items()
    }
    lower_profile = (
        exact_profile if declared_lower_profile is None else declared_lower_profile
    )
    profile_errors = [
        f"rank {rank_value}: declared capacity {lower_profile.get(rank_value)} "
        f"> exact epsilon {exact_profile.get(rank_value)}"
        for rank_value in sorted(finite_controls)
        if rank_value not in lower_profile
        or lower_profile[rank_value] > exact_profile[rank_value]
    ]
    if profile_errors:
        raise ValueError("invalid capacity profile: " + "; ".join(profile_errors))
    bound = capacity_profile_bound(
        n,
        lower_profile,
        active_ranks=set(finite_controls),
    )
    exact = incidence_control_certificate(transition)
    global_finite_bound_available = (
        exact["escape_semantics"]["global_finite_bound_status"] == "AVAILABLE"
    )
    thickness = boundary_thickness_profile(controls, threshold=2)
    high_capacity = sorted(
        rank_value for rank_value, row in finite_controls.items()
        if row["epsilon_r"] > 1
    )
    unit_capacity = sorted(
        rank_value for rank_value, row in finite_controls.items()
        if row["epsilon_r"] == 1
    )
    return {
        "carrier": "waiting_capacity_tradeoff",
        "Omega_epsilon_kappa": {
            str(rank_value): {
                "Omega_r": row["Omega_r"],
                "epsilon_r": row["epsilon_r"],
                "kappa_r": row["kappa_r"],
                "statewise_ratio_chi_r": row["statewise_ratio_chi_r"],
                "unit_shortest_escape_state_count": (
                    row["unit_shortest_escape_state_count"]
                ),
                "high_capacity_shortest_escape_state_count": (
                    row["high_capacity_shortest_escape_state_count"]
                ),
                "Omega_r_unit_states": row["Omega_r_unit_states"],
                "u_r": row["u_r"],
                "high_capacity_ratio_r": row["high_capacity_ratio_r"],
                "h_r": row["h_r"],
                "boundary_capacity_r": row["boundary_capacity_r"],
            }
            for rank_value, row in sorted(finite_controls.items())
        },
        "high_capacity_ranks_H": high_capacity,
        "unit_capacity_ranks_U": unit_capacity,
        "boundary_thickness_q2": thickness,
        "exact_tradeoff_envelope": {
            "lambda_upper": exact["lambda_upper"],
            "phi_kappa_initial": (
                exact["phi_upper_by_rank"].get(str(n))
                if global_finite_bound_available else None
            ),
            "statewise_lambda_upper": exact["statewise_lambda_upper"],
            "statewise_branch_tail_profile": exact[
                "statewise_branch_tail_profile"
            ],
            "phi_statewise_initial": (
                exact["phi_statewise_upper_by_rank"].get(str(n))
                if global_finite_bound_available else None
            ),
            "combined_statewise_bound_initial": exact[
                "combined_statewise_bound_initial"
            ],
            "global_finite_bound_status": exact[
                "escape_semantics"
            ]["global_finite_bound_status"],
        },
        "declared_capacity_profile": {
            "profile": {str(rank_value): value for rank_value, value in sorted(lower_profile.items())},
            "is_exact_epsilon_profile": declared_lower_profile is None,
            "pin_frankl_capacity_bound": bound,
        },
        "shortest_reset_depth": exact["shortest_reset_depth"],
        "bound_slack": (
            None if exact["shortest_reset_depth"] is None
            else {
                "numerator": (
                    Fraction(
                        bound["bound"]["numerator"],
                        bound["bound"]["denominator"],
                    ) - exact["shortest_reset_depth"]
                ).numerator,
                "denominator": (
                    Fraction(
                        bound["bound"]["numerator"],
                        bound["bound"]["denominator"],
                    ) - exact["shortest_reset_depth"]
                ).denominator,
            }
        ),
        "claim_boundary": {
            "waiting_capacity_tradeoff": "Exact finite theorem",
            "statewise_branch_refinement": "Exact finite theorem",
            "unit_high_tail_decomposition": "Exact finite theorem",
            "capacity_profile_bound": "Theorem under declared lower profile",
            "quadratic_or_linear_rank_bound": "Open; not inferred from finite data",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = incidence_control_certificate(cerny_transition(args.states))
    payload = {
        "schema": "rime.synchronizing-automata.fiber-incidence-controls.v1",
        "transition_family": "Cerny",
        "result": result,
    }
    payload["content_sha256"] = payload_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "states": args.states,
        "exact_phi_fi": result["exact_phi_fi"],
        "phi_upper": result["phi_upper_by_rank"].get(str(args.states)),
        "reset_depth": result["shortest_reset_depth"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
