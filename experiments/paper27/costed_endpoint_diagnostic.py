#!/usr/bin/env python3
"""Bellman diagnostic for the costed endpoint lift.

``C_A`` (the old endpoint-geodesic cut) is intentionally not reconstructed
here.  This module studies the distinct checkpoint-cost obstruction

    V_nu(mu) = tau(nu) - tau(mu) - ell_*(mu,nu) + H_A(nu)
    J_A(mu)  = max_nu V_nu(mu)

and the lifted coordinate ``Vhat = V - c``, where ``c`` is the transport cost
already paid in the current corridor.  On a geodesic edge labelled by a fixed
endpoint, ``V`` increases by one and ``Vhat`` is exactly conserved.

The calculation is finite and exact.  ``None`` is used for mathematical
``-infinity`` in JSON records (an endpoint whose lower-rank state is losing).
The resulting ``K_A`` is a Bellman-exact costed cut; it must not be confused
with the geometry-only ``C_A``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from .mass_maturity_legacy import (
        Letters,
        Mass,
        mass_rank,
        pushforward_mass,
        reachable_masses,
        simplified_deadline,
    )
except ImportError:
    from mass_maturity_legacy import (
        Letters,
        Mass,
        mass_rank,
        pushforward_mass,
        reachable_masses,
        simplified_deadline,
    )


def _mass_key(mass: Mass) -> tuple[int, Mass]:
    return mass_rank(mass), mass


def payload_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=list).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _j_negative(value: int | None) -> bool:
    """Return whether a JSON ``J`` value represents ``J<0``."""
    return value is None or value < 0


def _exit_rows(mass: Mass, letters: Letters, n: int) -> list[dict[str, Any]]:
    """Enumerate every lower-rank endpoint with its own shortest corridor.

    The older ``first_exit_corridors`` helper stops at the globally first rank
    drop.  ``ENDPOINT`` normalization is weaker: a corridor may choose a
    later lower-rank endpoint, provided its representative is shortest for
    that endpoint (as in the standard Cerny word).  This routine therefore
    explores the whole rank-preserving layer and coalesces each target by its
    endpoint-shortest distance.
    """
    source_tau = simplified_deadline(mass, n)
    source_rank = mass_rank(mass)
    seen: dict[Mass, int] = {mass: 0}
    parent: dict[Mass, tuple[Mass, int]] = {}
    queue = deque([mass])
    endpoints: dict[Mass, dict[str, Any]] = {}
    while queue:
        current = queue.popleft()
        depth = seen[current]
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(current, letter)
            target_rank = mass_rank(target)
            length = depth + 1
            if target_rank < source_rank:
                if target not in endpoints:
                    word = []
                    cursor = current
                    while cursor in parent:
                        cursor, previous_letter = parent[cursor]
                        word.append(previous_letter)
                    word = list(reversed(word)) + [letter_index]
                    endpoints[target] = {
                        "target": target,
                        "length": length,
                        "target_rank": target_rank,
                        "letter": letter_index,
                        "word": tuple(word),
                    }
                continue
            if target not in seen:
                seen[target] = length
                parent[target] = (current, letter_index)
                queue.append(target)
    rows = []
    for row in sorted(endpoints.values(), key=lambda item: (item["length"], item["target"], item["letter"])):
        target = tuple(row["target"])
        target_tau = simplified_deadline(target, n)
        rows.append({
            "target": target,
            "length": int(row["length"]),
            "target_rank": int(row["target_rank"]),
            "letter": int(row["letter"]),
            "word": tuple(row["word"]),
            "tau_target": target_tau,
            "surplus": target_tau - source_tau - int(row["length"]),
        })
    return rows


def endpoint_shortest_exits(mass: Mass, letters: Letters, n: int) -> list[dict[str, Any]]:
    """Public endpoint-normalized exit table for one mass placement.

    Unlike :func:`mass_maturity.first_exit_corridors`, this includes every
    lower-rank target that has a shortest rank-preserving representative.  A
    caller can therefore select a later endpoint without paying a nonminimal
    path to that same endpoint.
    """
    return _exit_rows(mass, letters, n)


def endpoint_shortest_exit_words(
    mass: Mass,
    letters: Letters,
    n: int,
) -> list[dict[str, Any]]:
    """Return every shortest word to every lower-rank mass endpoint.

    ``endpoint_shortest_exits`` intentionally chooses one BFS representative
    per mass endpoint. That is enough for scalar endpoint distances, but tied
    shortest words may realize different source-addressed fusion identities.
    This companion preserves the complete shortest-parent DAG without
    changing the legacy one-representative API.
    """
    source_tau = simplified_deadline(mass, n)
    source_rank = mass_rank(mass)
    distance: dict[Mass, int] = {mass: 0}
    parents: dict[Mass, list[tuple[Mass, int]]] = {mass: []}
    queue = deque([mass])
    endpoint_distance: dict[Mass, int] = {}
    endpoint_parents: dict[Mass, list[tuple[Mass, int]]] = {}

    while queue:
        current = queue.popleft()
        length = distance[current] + 1
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(current, letter)
            if mass_rank(target) < source_rank:
                known = endpoint_distance.get(target)
                if known is None or length < known:
                    endpoint_distance[target] = length
                    endpoint_parents[target] = [(current, letter_index)]
                elif length == known:
                    endpoint_parents[target].append((current, letter_index))
                continue
            known = distance.get(target)
            if known is None:
                distance[target] = length
                parents[target] = [(current, letter_index)]
                queue.append(target)
            elif length == known:
                parents[target].append((current, letter_index))

    @lru_cache(maxsize=None)
    def words_to(state: Mass) -> tuple[tuple[int, ...], ...]:
        if state == mass:
            return ((),)
        return tuple(
            word + (letter_index,)
            for parent, letter_index in parents[state]
            for word in words_to(parent)
        )

    rows = []
    for target in sorted(endpoint_distance):
        length = endpoint_distance[target]
        target_tau = simplified_deadline(target, n)
        words = {
            word + (letter_index,)
            for parent, letter_index in endpoint_parents[target]
            for word in words_to(parent)
        }
        for word in sorted(words):
            rows.append(
                {
                    "target": target,
                    "length": length,
                    "target_rank": mass_rank(target),
                    "letter": int(word[-1]),
                    "word": word,
                    "tau_target": target_tau,
                    "surplus": target_tau - source_tau - length,
                }
            )
    return rows


def endpoint_value(
    mass: Mass,
    endpoint: Mass,
    ell_star: int,
    h_endpoint: int | None,
    n: int,
) -> int | None:
    """Evaluate ``V_nu(mu)``; ``None`` represents ``-infinity``."""
    if h_endpoint is None:
        return None
    return simplified_deadline(endpoint, n) - simplified_deadline(mass, n) - ell_star + h_endpoint


def costed_endpoint_value(
    mass: Mass,
    endpoint: Mass,
    ell_star: int,
    h_endpoint: int | None,
    cost: int,
    n: int,
) -> int | None:
    """Evaluate ``Vhat_nu(mu,c)=V_nu(mu)-c``."""
    value = endpoint_value(mass, endpoint, ell_star, h_endpoint, n)
    return None if value is None else value - cost


def _capacity_for_mass(
    mass: Mass,
    exits: list[dict[str, Any]],
    capacities: dict[Mass, int | None],
) -> tuple[int | None, int | None, str]:
    """Return ``(H, J, status)`` after lower-rank capacities are known."""
    rank = mass_rank(mass)
    if rank == 1:
        # A reset is terminal: no pending debt may be carried beyond it.
        return 0, None, "RESET_NO_ENDPOINT"
    if not exits:
        return None, None, "DEAD_NO_ENDPOINT"

    values: list[int] = []
    for row in exits:
        target_h = capacities[row["target"]]
        if target_h is not None:
            values.append(row["surplus"] + target_h)
    j_value = max(values) if values else None
    if _j_negative(j_value):
        return None, j_value, "COSTED_ENDPOINT_CUT"

    # Pending debt must be paid by this next corridor.  Capacity in the
    # successor can certify the solvent h=0 branch, but cannot be borrowed to
    # defer a positive pending debt.
    positive_surpluses = [
        row["surplus"]
        for row in exits
        if capacities[row["target"]] is not None
        and row["surplus"] >= 0
    ]
    return max([0, *positive_surpluses]), j_value, "SOLVENT"


def _explicit_lift_capacity(
    exits: list[dict[str, Any]],
    capacities: dict[Mass, int | None],
    max_debt: int,
) -> int | None:
    """Independently evaluate the finite pending-debt lift.

    This is deliberately a state test rather than a call to ``J``.  It gives
    the diagnostic an independent Bellman check for the claimed compression
    ``H_A``.
    """
    winning: list[int] = []
    for debt in range(max_debt + 1):
        ok = False
        for row in exits:
            target_h = capacities[row["target"]]
            surplus = row["surplus"]
            if debt == 0:
                if target_h is not None and surplus + target_h >= 0:
                    ok = True
                    break
            elif target_h is not None and surplus >= debt:
                ok = True
                break
        if ok:
            winning.append(debt)
    if not winning:
        return None
    expected = list(range(winning[-1] + 1))
    if winning != expected:
        raise AssertionError("pending winning debts are not an integer initial segment")
    return winning[-1]


def _geodesic_rows(
    mass: Mass,
    exits: list[dict[str, Any]],
    capacities: dict[Mass, int | None],
    letters: Letters,
    n: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Check exact ``+1`` and costed conservation along representative cones."""
    rows: list[dict[str, Any]] = []
    counts = Counter()
    for exit_row in exits:
        endpoint = exit_row["target"]
        target_h = capacities[endpoint]
        if target_h is None:
            continue
        word = exit_row["word"]
        current = mass
        full_length = exit_row["length"]
        for step, letter_index in enumerate(word[:-1]):
            nxt = pushforward_mass(current, letters[letter_index])
            if mass_rank(nxt) != mass_rank(current):
                raise AssertionError("first-exit representative drops before its terminal letter")
            remaining = full_length - step
            current_v = simplified_deadline(endpoint, n) - simplified_deadline(current, n) - remaining + target_h
            next_v = simplified_deadline(endpoint, n) - simplified_deadline(nxt, n) - (remaining - 1) + target_h
            plus_one = next_v == current_v + 1
            conserved = (next_v - (step + 1)) == (current_v - step)
            counts["geodesic_edges"] += 1
            counts["v_plus_one_failures"] += not plus_one
            counts["vhat_conservation_failures"] += not conserved
            rows.append({
                "source": current,
                "target": nxt,
                "endpoint": endpoint,
                "step": step,
                "letter": letter_index,
                "remaining_distance_before": remaining,
                "v_before": current_v,
                "v_after": next_v,
                "vhat_before": current_v - step,
                "vhat_after": next_v - (step + 1),
                "v_plus_one": plus_one,
                "vhat_conserved": conserved,
            })
            current = nxt
        if word:
            terminal = pushforward_mass(current, letters[word[-1]])
            if terminal != endpoint:
                raise AssertionError("endpoint representative does not reach its endpoint")
    return rows, dict(counts)


def _initial_endpoint_inequality_from_record(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the initial endpoint selector from one profile record.

    The initial deadline is zero, so each candidate is exactly the integer
    inequality ``ell_*(1, nu) <= tau(nu) + H_A(nu)``.  Keeping this evaluator
    separate makes the selector reusable without changing the recursive
    capacity calculation.
    """
    candidates = []
    for endpoint in record["endpoints"]:
        target_h = endpoint["H_target"]
        rhs = None if target_h is None else endpoint["tau_target"] + target_h
        margin = None if rhs is None else rhs - endpoint["length"]
        candidates.append({
            "endpoint": endpoint["target"],
            "ell_star": endpoint["length"],
            "tau_endpoint": endpoint["tau_target"],
            "H_endpoint": target_h,
            "right_hand_side": rhs,
            "margin": margin,
            "holds": margin is not None and margin >= 0,
        })
    witnesses = [row for row in candidates if row["holds"]]
    return {
        "formula": "ell_*(1,nu) <= tau(nu) + H_A(nu)",
        "candidates": candidates,
        "holds": bool(witnesses),
        "witness": witnesses[0] if witnesses else None,
        "equivalent_to_J_nonnegative": record["J_A"] is not None and record["J_A"] >= 0,
    }


def initial_uniform_endpoint_collapse(letters: Letters, n: int) -> dict[str, Any]:
    """Certify the initial uniform-mass endpoint collapse.

    The initial mass ``(1, ..., 1)`` is fixed by every rank-preserving letter:
    a map of an `
``-point set with image size `
`` is a permutation.  Thus
    every endpoint reachable by a rank-preserving prefix followed by its first
    strict drop is already the image of one rank-decreasing letter.  This
    helper records that finite check explicitly; the underlying implication is
    structural and does not depend on the explored automaton being synchronizing.
    """
    initial = (1,) * n
    rank_preserving_letters: list[int] = []
    rank_decreasing_letters: list[dict[str, Any]] = []
    for letter_index, letter in enumerate(letters):
        target = pushforward_mass(initial, letter)
        target_rank = mass_rank(target)
        if target_rank == n:
            if target != initial:
                raise AssertionError(
                    "a rank-preserving letter moved the uniform initial mass"
                )
            rank_preserving_letters.append(letter_index)
        elif target_rank < n:
            rank_decreasing_letters.append(
                {
                    "letter": letter_index,
                    "endpoint": target,
                    "target_rank": target_rank,
                }
            )
        else:
            raise AssertionError("mass rank cannot increase from the initial state")
    return {
        "initial": initial,
        "rank_preserving_letters": rank_preserving_letters,
        "rank_decreasing_letters": rank_decreasing_letters,
        "all_rank_preserving_fix_initial": True,
        "endpoint_length": 1 if rank_decreasing_letters else None,
    }


def first_fusion_selector(letters: Letters, n: int) -> dict[str, Any]:
    """Return the initial first-fusion selector certificate.

    At the uniform initial mass every endpoint-shortest first exit has length
    one.  Consequently the initial endpoint inequality is equivalent to the
    existence of a rank-decreasing letter whose immediate image has finite
    repayment capacity ``H_A >= 0``.  The full profile remains the source of
    truth for capacities and for the legacy IE compatibility query.
    """
    profile = costed_endpoint_profile(letters, n, include_edges=False)
    return _first_fusion_selector_from_profile(profile, letters, n)


def _first_fusion_selector_from_profile(
    profile: dict[str, Any], letters: Letters, n: int
) -> dict[str, Any]:
    """Build the selector view without recomputing the Bellman profile."""
    capacities = {
        tuple(row["mass"]): row["H_A"] for row in profile["profile"]
    }
    collapse = initial_uniform_endpoint_collapse(letters, n)
    candidates: list[dict[str, Any]] = []
    for row in collapse["rank_decreasing_letters"]:
        endpoint = tuple(row["endpoint"])
        h_value = capacities.get(endpoint)
        tau_value = simplified_deadline(endpoint, n)
        candidates.append(
            {
                "letter": row["letter"],
                "endpoint": endpoint,
                "target_rank": row["target_rank"],
                "ell_star": 1,
                "tau_endpoint": tau_value,
                "H_endpoint": h_value,
                "winning": h_value is not None and h_value >= 0,
            }
        )
    winning = [row for row in candidates if row["winning"]]
    d_letters = [row["letter"] for row in candidates]
    s_letters = [row["letter"] for row in winning]
    immediate_images = sorted({tuple(row["endpoint"]) for row in candidates})
    forced_applicable = len(d_letters) == 1
    ie = profile["initial"]["endpoint_inequality"]
    selector_holds = bool(winning)
    return {
        "formula": "exists rank-decreasing a: (a_*1,0) in W_A^(2C)",
        "initial_uniform_endpoint_collapse": collapse,
        "rank_decreasing_letters": candidates,
        "D_A": d_letters,
        "S_2C": s_letters,
        "I_A": immediate_images,
        "winning_first_letters": s_letters,
        "holds": selector_holds,
        "witness": winning[0] if winning else None,
        "forced_first_fusion": {
            "applicable": forced_applicable,
            "letter": d_letters[0] if forced_applicable else None,
            "image": candidates[0]["endpoint"] if forced_applicable else None,
            "image_winning": forced_applicable and candidates[0]["winning"],
        },
        "equivalent_to_IE": selector_holds == bool(ie["holds"]),
        "equivalent_to_initial_J_nonnegative": selector_holds
        == (profile["initial"]["J_A"] is not None and profile["initial"]["J_A"] >= 0),
    }


def costed_endpoint_profile(letters: Letters, n: int, *, include_edges: bool = True) -> dict[str, Any]:
    """Build the exact ``H_A/J_A/K_A`` profile for one automaton."""
    masses = sorted(reachable_masses(letters, n), key=_mass_key)
    capacities: dict[Mass, int | None] = {}
    profile: dict[Mass, dict[str, Any]] = {}
    all_geodesic_rows: list[dict[str, Any]] = []
    geodesic_counts = Counter()
    explicit_checks = 0
    explicit_failures = 0

    for mass in masses:
        exits = _exit_rows(mass, letters, n)
        h_value, j_value, status = _capacity_for_mass(mass, exits, capacities)
        if mass_rank(mass) == 1:
            # The rank-one endpoint is terminal and has no E(mu).
            exits = []
        if status != "RESET_NO_ENDPOINT":
            explicit = _explicit_lift_capacity(exits, capacities, (n - 1) ** 2)
            explicit_checks += 1
            if explicit != h_value:
                explicit_failures += 1
        endpoint_rows = []
        for row in exits:
            target_h = capacities[row["target"]]
            value = None if target_h is None else row["surplus"] + target_h
            endpoint_rows.append({
                "target": row["target"],
                "length": row["length"],
                "letter": row["letter"],
                "word": list(row["word"]),
                "tau_target": row["tau_target"],
                "surplus": row["surplus"],
                "H_target": target_h,
                "V_nu": value,
            })
        record: dict[str, Any] = {
            "mass": mass,
            "rank": mass_rank(mass),
            "tau": simplified_deadline(mass, n),
            "endpoints": endpoint_rows,
            "E_nonempty": bool(endpoint_rows),
            "H_A": h_value,
            "J_A": j_value,
            "status": status,
            "K_A": status == "COSTED_ENDPOINT_CUT",
            "bellman_equivalence": (
                status == "SOLVENT"
                or (status == "COSTED_ENDPOINT_CUT" and _j_negative(j_value))
                or (status == "DEAD_NO_ENDPOINT" and j_value is None)
                or status == "RESET_NO_ENDPOINT"
            ),
        }
        profile[mass] = record
        capacities[mass] = h_value

        if include_edges and status != "RESET_NO_ENDPOINT":
            edge_rows, edge_counts = _geodesic_rows(mass, exits, capacities, letters, n)
            all_geodesic_rows.extend(edge_rows)
            geodesic_counts.update(edge_counts)

    # A second pass records the visible J-only ``(-1,0)`` checkpoint crossing
    # distribution on rank-preserving edges.  These are not violations of T1:
    # the endpoint distance changes at the same time as the new checkpoint.
    j_crossings: list[dict[str, Any]] = []
    for mass in masses:
        record = profile[mass]
        if record["J_A"] is None:
            continue
        for letter_index, letter in enumerate(letters):
            target = pushforward_mass(mass, letter)
            if mass_rank(target) != mass_rank(mass) or target not in profile:
                continue
            target_j = profile[target]["J_A"]
            if record["J_A"] == -1 and target_j == 0:
                j_crossings.append({"source": mass, "target": target, "letter": letter_index, "J_source": -1, "J_target": 0})

    statuses = Counter(record["status"] for record in profile.values())
    k_states = [mass for mass, row in profile.items() if row["K_A"]]
    profile_by_mass = profile
    costed_crossings = []
    for row in all_geodesic_rows:
        source_j = profile_by_mass[row["source"]]["J_A"]
        target_j = profile_by_mass[row["target"]]["J_A"]
        if source_j == -1 and target_j == 0:
            costed_crossings.append({
                "source": row["source"],
                "target": row["target"],
                "endpoint": row["endpoint"],
                "letter": row["letter"],
                "step": row["step"],
                "vhat_before": row["vhat_before"],
                "vhat_after": row["vhat_after"],
                "J_source": source_j,
                "J_target": target_j,
                "costed_margin_conserved": row["vhat_before"] == row["vhat_after"],
            })
    initial = (1,) * n
    initial_row = profile[initial]
    initial_ie = _initial_endpoint_inequality_from_record(initial_row)
    ie_witnesses = [row for row in initial_ie["candidates"] if row["holds"]]
    return {
        "schema": "costed-endpoint-diagnostic-v1",
        "state_count": n,
        "alphabet_size": len(letters),
        "reachable_mass_count": len(masses),
        "profile": [profile[mass] for mass in masses],
        "H_A": {str(mass): profile[mass]["H_A"] for mass in masses},
        "J_A": {str(mass): profile[mass]["J_A"] for mass in masses},
        "counts": {
            "status": dict(sorted(statuses.items())),
            "K_A": len(k_states),
            "explicit_lift_checks": explicit_checks,
            "explicit_lift_failures": explicit_failures,
            "geodesic_edges": geodesic_counts.get("geodesic_edges", 0),
            "V_plus_one_failures": geodesic_counts.get("v_plus_one_failures", 0),
            "Vhat_conservation_failures": geodesic_counts.get("vhat_conservation_failures", 0),
            "J_minus_one_to_zero_crossings": len(j_crossings),
            "costed_minus_one_to_zero_rows": len(costed_crossings),
            "initial_status": initial_row["status"],
            "initial_H_A": initial_row["H_A"],
            "initial_J_A": initial_row["J_A"],
            "initial_IE_holds": bool(ie_witnesses),
            "initial_IE_J_equivalence_failure": (
                bool(ie_witnesses)
                != (initial_row["J_A"] is not None and initial_row["J_A"] >= 0)
            ),
        },
        "initial": {
            "mass": initial,
            "status": initial_row["status"],
            "H_A": initial_row["H_A"],
            "J_A": initial_row["J_A"],
            "K_A": initial_row["K_A"],
            "endpoint_inequality": initial_ie,
        },
        "geodesic_edge_rows": all_geodesic_rows if include_edges else None,
        "J_minus_one_to_zero_rows": j_crossings,
        "costed_minus_one_to_zero_rows": costed_crossings,
        "costed_cut_states": [list(mass) for mass in k_states],
        "claim_boundary": {
            "H_A": "Exact finite Bellman compression; None denotes -infinity.",
            "J_A": "Exact finite endpoint-cost diagnostic.",
            "K_A": "Costed endpoint cut; distinct from the geometry-only C_A.",
            "Vhat": "Exact conservation on the recorded endpoint-geodesic edges.",
            "general_Cerny": "Not claimed.",
        },
    }


def repayment_capacity(letters: Letters, n: int) -> dict[Mass, int | None]:
    """Return the exact Bellman capacity map ``H_A``."""
    profile = costed_endpoint_profile(letters, n, include_edges=False)
    return {tuple(row["mass"]): row["H_A"] for row in profile["profile"]}


def initial_endpoint_inequality(letters: Letters, n: int) -> dict[str, Any]:
    """Return the initial endpoint-selector certificate for an automaton.

    This is the minimal initial-state query, separated from the optional
    geodesic edge census.  It computes the recursive ``H_A`` values first and
    then evaluates every endpoint-shortest first exit from ``(1, ..., 1)``.
    The returned ``holds`` flag is equivalent to ``J_A((1, ..., 1)) >= 0``;
    ``witness`` identifies an endpoint that pays for its shortest transport.
    """
    profile = costed_endpoint_profile(letters, n, include_edges=False)
    return profile["initial"]["endpoint_inequality"]


def build_cerny_diagnostic(n: int = 4, *, include_edges: bool = True) -> dict[str, Any]:
    try:
        from .families import cerny_transition
    except ImportError:
        from families import cerny_transition
    return costed_endpoint_profile(tuple(cerny_transition(n)), n, include_edges=include_edges)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--no-edges", action="store_true")
    args = parser.parse_args()
    payload = build_cerny_diagnostic(args.states, include_edges=not args.no_edges)
    payload["content_sha256"] = payload_digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=list) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload["counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
