#!/usr/bin/env python3
"""Exact rank-at-most-three base for raw two-corridor macro descent.

The base is evaluated only from endpoint-shortest strict corridors and their
surpluses. It does not read Bellman capacities, reset coaccessibility, global
macro-winning labels, or a stored winning policy.

For rank two, a negative strict corridor cannot be repaid: its endpoint already
has rank one. Hence the source is locally admissible exactly when it has a
nonnegative Type-I corridor to reset. For rank three, a Type-I corridor lands
at rank one or at an admissible rank-two source, while every Type-II block has
the forced rank pattern 3 -> 2 -> 1. These cases exhaust raw macro descent at
rank at most three.
"""
from __future__ import annotations

from typing import Any

from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, reachable_masses
from single_defect_macro_trap import _raw_type_i, _raw_type_ii


Mass = tuple[int, ...]
Letters = tuple[tuple[int, ...], ...]


def _mass_key(mass: Mass) -> tuple[int, Mass]:
    return mass_rank(mass), mass


def build_low_rank_base(letters: Letters, n: int) -> dict[str, Any]:
    """Build the exact local base classes P_1, P_2, and P_3."""
    frozen = tuple(tuple(letter) for letter in letters)
    masses = sorted(
        (mass for mass in reachable_masses(frozen, n) if mass_rank(mass) <= 3),
        key=_mass_key,
    )
    exit_cache: dict[Mass, list[dict[str, Any]]] = {}
    local_good: dict[Mass, bool] = {}
    witness: dict[Mass, dict[str, Any] | None] = {}
    rows = []

    def exits_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in exit_cache:
            exit_cache[mass] = endpoint_shortest_exits(mass, frozen, n)
        return exit_cache[mass]

    for mass in masses:
        rank = mass_rank(mass)
        if rank == 1:
            local_good[mass] = True
            witness[mass] = None
            rows.append({
                "mass": list(mass),
                "rank": rank,
                "in_low_rank_base": True,
                "type_i_count": 0,
                "type_ii_count": 0,
                "admissible_type_i_count": 0,
                "admissible_type_ii_count": 0,
                "witness": None,
            })
            continue

        exits = exits_for(mass)
        type_i = _raw_type_i(mass, exits, n)
        type_ii = _raw_type_ii(mass, exits, exits_for, n)
        admissible_i = [
            edge for edge in type_i if local_good.get(tuple(edge["target"]), False)
        ]
        admissible_ii = [
            edge for edge in type_ii if local_good.get(tuple(edge["target"]), False)
        ]
        candidates = sorted(
            admissible_i + admissible_ii,
            key=lambda edge: (
                edge["total_length"],
                -edge["total_surplus"],
                edge["type"],
                edge["target"],
                edge["intermediate"] or [],
            ),
        )
        local_good[mass] = bool(candidates)
        witness[mass] = candidates[0] if candidates else None

        if rank == 2:
            if type_ii:
                raise AssertionError("rank-two source unexpectedly has a Type-II block")
            if any(int(edge["rank_target"]) != 1 for edge in type_i):
                raise AssertionError("rank-two Type-I edge did not terminate at rank one")
        elif rank == 3:
            if any(
                (
                    int(edge["rank_source"]),
                    int(edge["rank_intermediate"]),
                    int(edge["rank_target"]),
                ) != (3, 2, 1)
                for edge in type_ii
            ):
                raise AssertionError("rank-three Type-II edge was not 3->2->1")

        rows.append({
            "mass": list(mass),
            "rank": rank,
            "in_low_rank_base": local_good[mass],
            "type_i_count": len(type_i),
            "type_ii_count": len(type_ii),
            "admissible_type_i_count": len(admissible_i),
            "admissible_type_ii_count": len(admissible_ii),
            "witness": witness[mass],
        })

    rank_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        rank = str(row["rank"])
        counts = rank_counts.setdefault(rank, {"states": 0, "base": 0})
        counts["states"] += 1
        counts["base"] += int(row["in_low_rank_base"])
    return {
        "n": n,
        "alphabet_size": len(frozen),
        "maximum_base_rank": 3,
        "rank_counts": rank_counts,
        "rows": rows,
        "base_masses": [row["mass"] for row in rows if row["in_low_rank_base"]],
        "semantics": {
            "rank_one": "terminal reset masses",
            "rank_two": "a nonnegative Type-I corridor to rank one",
            "rank_three": (
                "a Type-I corridor to the rank-one/two base, or a Type-II "
                "3->2->1 block"
            ),
            "forbidden_inputs": [
                "H_A",
                "global macro-winning labels",
                "ordinary reset coaccessibility",
                "stored winning policy",
            ],
        },
    }


__all__ = ["build_low_rank_base"]
