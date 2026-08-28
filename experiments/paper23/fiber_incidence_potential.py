#!/usr/bin/env python3
"""Fiber-incidence amortized potential for rank-collapse dynamics.

For a reachable rank-r subset S, a rank-preserving path ending at T and a
letter a with U=delta(T,a) of rank r-e has incidence e=Exc_a(T).  The ratio

    (path length + 1) / e

is the cost per unit rank drop of that escape.  Taking the worst reachable
subset and then a tail maximum over ranks yields an analytic rank potential:

    theta_r = max_S min_escape cost/incidence,
    lambda_j = max_{t >= j} theta_t,
    Phi_FI(S) = sum_{j=2}^{|S|} lambda_j.

The tail maximum is the small monotonicity device that makes multi-fiber
drops path-compatible.  This is an exact finite theorem about the declared
rank-layer graph; it is not a universal numerical bound in n and m.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Any

from path_potential import cerny_transition, rank_drop_dynamic_potential
from registry import (
    Transition,
    fiber_excess,
    payload_digest,
    reachable_subset_automaton,
    shortest_subset_reset_word,
)


def _fraction_json(value: Fraction | None) -> dict[str, int] | None:
    if value is None:
        return None
    return {"numerator": value.numerator, "denominator": value.denominator}


def _rank_theta(
    transition: Transition,
    nodes: list[tuple[int, ...]],
    edges: dict[tuple[int, ...], tuple[tuple[int, ...], ...]],
) -> tuple[Fraction | None, dict[tuple[int, ...], Fraction | None], list[dict]]:
    """Compute theta(S), theta_r, and exact terminal incidence options."""
    rank_value = len(nodes[0])
    boundary_options = []
    for source in nodes:
        for letter_index, target in enumerate(edges[source]):
            if len(target) >= rank_value:
                continue
            incidence = fiber_excess(transition[letter_index], source)
            assert incidence > 0
            boundary_options.append((source, letter_index, target, incidence))

    theta_by_subset: dict[tuple[int, ...], Fraction | None] = {}
    option_rows: list[dict] = []
    for start in nodes:
        distance = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for target in edges[current]:
                if len(target) == rank_value and target not in distance:
                    distance[target] = distance[current] + 1
                    queue.append(target)
        choices = []
        for source, letter_index, target, incidence in boundary_options:
            if source not in distance:
                continue
            segment_length = distance[source] + 1
            choices.append((
                Fraction(segment_length, incidence),
                segment_length,
                incidence,
                source,
                letter_index,
                target,
            ))
        if not choices:
            theta_by_subset[start] = None
            continue
        choices.sort(key=lambda item: (item[0], item[1], -item[2], item[3], item[4], item[5]))
        best = choices[0]
        theta_by_subset[start] = best[0]
        option_rows.append({
            "subset": list(start),
            "rank": rank_value,
            "theta": _fraction_json(best[0]),
            "segment_length": best[1],
            "fiber_excess": best[2],
            "boundary_source": list(best[3]),
            "letter": best[4],
            "target": list(best[5]),
        })
    finite = [value for value in theta_by_subset.values() if value is not None]
    theta_rank = max(finite) if len(finite) == len(nodes) else None
    return theta_rank, theta_by_subset, option_rows


def fiber_incidence_potential(transition: Transition) -> dict[str, Any]:
    """Compute the exact fiber-incidence potential and local descent checks."""
    distance, _words, edges = reachable_subset_automaton(transition)
    nodes_by_rank: dict[int, list[tuple[int, ...]]] = {}
    for subset in distance:
        nodes_by_rank.setdefault(len(subset), []).append(subset)

    theta_by_rank: dict[int, Fraction | None] = {}
    theta_by_subset: dict[tuple[int, ...], Fraction | None] = {}
    options_by_rank: dict[int, list[dict]] = {}
    for rank_value, nodes in sorted(nodes_by_rank.items()):
        if rank_value == 1:
            continue
        theta, subset_values, options = _rank_theta(transition, sorted(nodes), edges)
        theta_by_rank[rank_value] = theta
        theta_by_subset.update(subset_values)
        options_by_rank[rank_value] = options

    # Tail maxima make a drop of e ranks pay for e copies of the current
    # per-incidence cost, even when several intermediate ranks are skipped.
    n = len(transition[0])
    lambda_by_index: dict[int, Fraction] = {}
    tail: Fraction | None = None
    for index in range(n, 1, -1):
        theta = theta_by_rank.get(index)
        if theta is not None and (tail is None or theta > tail):
            tail = theta
        if tail is not None:
            lambda_by_index[index] = tail

    phi_by_rank: dict[int, Fraction] = {1: Fraction(0)}
    running = Fraction(0)
    for rank_value in range(2, n + 1):
        running += lambda_by_index.get(rank_value, Fraction(0))
        phi_by_rank[rank_value] = running

    local_checks: list[bool] = []
    local_rows: list[dict] = []
    for rank_value, options in options_by_rank.items():
        for option in options:
            source_rank = rank_value
            target_rank = len(option["target"])
            incidence = option["fiber_excess"]
            segment = option["segment_length"]
            difference = phi_by_rank[source_rank] - phi_by_rank[target_rank]
            holds = Fraction(segment) <= difference
            local_checks.append(holds)
            local_rows.append({
                "source": option["subset"],
                "target": option["target"],
                "rank_before": source_rank,
                "rank_after": target_rank,
                "segment_length": segment,
                "fiber_excess": incidence,
                "potential_difference": _fraction_json(difference),
                "local_descent_holds": holds,
            })

    full = tuple(range(n))
    reset_word = shortest_subset_reset_word(transition)
    reset_depth = None if reset_word is None else len(reset_word)
    psi = rank_drop_dynamic_potential(transition)
    initial_phi = phi_by_rank.get(n)
    if reset_depth is not None and psi["initial_potential"] != reset_depth:
        raise AssertionError("Psi and reset depth disagree")
    if reset_depth is not None and initial_phi is not None and Fraction(reset_depth) > initial_phi:
        raise AssertionError("fiber-incidence potential bound failed")
    return {
        "carrier": "fiber_incidence_amortized_potential",
        "potential_formula": (
            "theta_r=max_S min_escape((dist_r(S,T)+1)/Exc_a(T)); "
            "lambda_j=max_{t>=j} theta_t; "
            "Phi_FI(S)=sum_{j=2}^{|S|} lambda_j"
        ),
        "reachable_subset_count": len(distance),
        "theta_by_rank": {
            str(rank_value): _fraction_json(value)
            for rank_value, value in sorted(theta_by_rank.items())
        },
        "lambda_by_index": {
            str(index): _fraction_json(value)
            for index, value in sorted(lambda_by_index.items())
        },
        "phi_by_rank": {
            str(rank_value): _fraction_json(value)
            for rank_value, value in sorted(phi_by_rank.items())
        },
        "subset_theta_options": [
            option for rank_value in sorted(options_by_rank)
            for option in options_by_rank[rank_value]
        ],
        "local_descent_rows": local_rows,
        "local_descent_certificate": {
            "all_checks_passed": all(local_checks) if local_checks else True,
            "check_count": len(local_checks),
            "meaning": "segment length is paid by tail-max incidence potential drop",
        },
        "initial_potential": _fraction_json(initial_phi),
        "shortest_reset_depth": reset_depth,
        "shortest_reset_word": None if reset_word is None else list(reset_word),
        "bound_slack": (
            None if reset_depth is None or initial_phi is None
            else _fraction_json(initial_phi - reset_depth)
        ),
        "claim_boundary": (
            "exact finite fiber-incidence potential theorem; no universal "
            "quadratic estimate for Phi_FI is claimed"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = fiber_incidence_potential(cerny_transition(args.states))
    payload = {
        "schema": "rime.synchronizing-automata.fiber-incidence-potential.v1",
        "transition_family": "Cerny",
        "result": result,
    }
    payload["content_sha256"] = payload_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "states": args.states,
        "initial_potential": result["initial_potential"],
        "reset_depth": result["shortest_reset_depth"],
        "checks": result["local_descent_certificate"]["check_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
