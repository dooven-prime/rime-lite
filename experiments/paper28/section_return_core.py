#!/usr/bin/env python3
"""Future-free local machinery for activated section-return experiments."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from collections.abc import Sequence
from typing import Any

from costed_endpoint_diagnostic import (
    endpoint_shortest_exits,
    endpoint_shortest_exit_words,
)
from mass_maturity_legacy import mass_rank, pushforward_mass
from single_defect_macro_trap import _raw_type_i, _raw_type_ii

Mass = tuple[int, ...]
Transformation = tuple[int, ...]
Letters = tuple[Transformation, ...]
Packet = frozenset[int]
PacketState = dict[int, Packet]


def digest_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=list
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def mass_partition(mass: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted((int(value) for value in mass if value), reverse=True))


def push_packets(state: PacketState, letter: Sequence[int]) -> PacketState:
    target: dict[int, set[int]] = {}
    for coordinate, packet in state.items():
        target.setdefault(int(letter[coordinate]), set()).update(packet)
    return {coordinate: frozenset(labels) for coordinate, labels in target.items()}


def packet_mass(state: PacketState, n: int) -> Mass:
    return tuple(len(state.get(index, ())) for index in range(n))


def trace_packets(
    state: PacketState, word: Sequence[int], letters: Letters
) -> PacketState:
    current = state
    for letter_index in word:
        current = push_packets(current, letters[int(letter_index)])
    return current


def fusion_witness(
    state: PacketState, word: Sequence[int], letters: Letters
) -> tuple[PacketState, dict[str, Any]]:
    if not word:
        raise AssertionError("strict packet corridor is empty")
    boundary = trace_packets(state, word[:-1], letters)
    final_letter = letters[int(word[-1])]
    grouped: dict[int, list[tuple[int, Packet]]] = {}
    for coordinate, packet in boundary.items():
        grouped.setdefault(int(final_letter[coordinate]), []).append(
            (coordinate, packet)
        )
    collisions = [
        (target, packets) for target, packets in grouped.items() if len(packets) > 1
    ]
    if len(collisions) != 1 or len(collisions[0][1]) != 2:
        raise AssertionError("corridor does not have one binary strict fusion")
    target_coordinate, parents = collisions[0]
    parent_packets = tuple(packet for _, packet in parents)
    fresh = frozenset().union(*parent_packets)
    target = push_packets(boundary, final_letter)
    if len(target) != len(state) - 1:
        raise AssertionError("packet corridor is not a unit rank drop")
    return target, {
        "boundary_parent_coordinates": [int(coordinate) for coordinate, _ in parents],
        "target_coordinate": int(target_coordinate),
        "parent_packets": [sorted(packet) for packet in parent_packets],
        "parent_sizes": sorted(len(packet) for packet in parent_packets),
        "fresh_packet": sorted(fresh),
        "fresh_size": len(fresh),
    }


def serialize_packet_state(state: PacketState) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": int(coordinate),
            "packet": sorted(packet),
            "mass": len(packet),
        }
        for coordinate, packet in sorted(state.items())
    ]


def deserialize_packet_state(rows: Sequence[dict[str, Any]]) -> PacketState:
    return {
        int(row["coordinate"]): frozenset(int(value) for value in row["packet"])
        for row in rows
    }


class ExitOracle:
    """Cache endpoint-normalized strict corridors for one fixed action."""

    def __init__(self, letters: Letters, n: int) -> None:
        self.letters = letters
        self.n = n
        self.cache: dict[Mass, list[dict[str, Any]]] = {}

    def exits(self, mass: Mass) -> list[dict[str, Any]]:
        if mass not in self.cache:
            self.cache[mass] = endpoint_shortest_exits(mass, self.letters, self.n)
        return self.cache[mass]

    def macro_edges(self, mass: Mass) -> list[dict[str, Any]]:
        rows = _raw_type_i(mass, self.exits(mass), self.n)
        rows.extend(_raw_type_ii(mass, self.exits(mass), self.exits, self.n))
        return sorted(rows, key=macro_edge_key)


class CompleteExitOracle(ExitOracle):
    """Cache every tied endpoint-shortest word for packet-relation work."""

    def exits(self, mass: Mass) -> list[dict[str, Any]]:
        if mass not in self.cache:
            self.cache[mass] = endpoint_shortest_exit_words(
                mass,
                self.letters,
                self.n,
            )
        return self.cache[mass]


class LowRankOracle:
    """Lazy exact ``P_1/P_2/P_3`` evaluator for one fixed action."""

    def __init__(self, exits: ExitOracle) -> None:
        self.exits = exits
        self.good_cache: dict[Mass, bool] = {}
        self.witness_cache: dict[Mass, dict[str, Any] | None] = {}

    def is_good(self, mass: Mass) -> bool:
        if mass in self.good_cache:
            return self.good_cache[mass]
        rank = mass_rank(mass)
        if rank == 1:
            self.good_cache[mass] = True
            self.witness_cache[mass] = None
            return True
        if rank not in (2, 3):
            raise ValueError("low-rank oracle only accepts ranks one to three")
        candidates = [
            edge
            for edge in self.exits.macro_edges(mass)
            if self.is_good(tuple(int(value) for value in edge["target"]))
        ]
        self.good_cache[mass] = bool(candidates)
        self.witness_cache[mass] = candidates[0] if candidates else None
        return self.good_cache[mass]

    def witness(self, mass: Mass) -> dict[str, Any] | None:
        self.is_good(mass)
        return self.witness_cache[mass]


def macro_edge_key(edge: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(edge["total_length"]),
        1 if edge["type"] == "I" else 2,
        tuple(int(value) for value in edge["first_word"]),
        tuple(int(value) for value in edge["second_word"]),
        tuple(int(value) for value in edge["target"]),
        tuple(int(value) for value in edge["intermediate"] or ()),
    )


def edge_summary(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": str(edge["type"]),
        "first_word": [int(value) for value in edge["first_word"]],
        "second_word": [int(value) for value in edge["second_word"]],
        "intermediate": (
            None
            if edge["intermediate"] is None
            else [int(value) for value in edge["intermediate"]]
        ),
        "target": [int(value) for value in edge["target"]],
        "rank_target": int(edge["rank_target"]),
        "length_first": int(edge["length_first"]),
        "length_second": int(edge["length_second"]),
        "total_length": int(edge["total_length"]),
        "surplus_first": int(edge["surplus_first"]),
        "surplus_second": int(edge["surplus_second"]),
        "total_surplus": int(edge["total_surplus"]),
        "debt_required": int(edge["debt_required"]),
    }


def activated_edge_summary(
    edge: dict[str, Any],
    packets: PacketState,
    letters: Letters,
    n: int,
    *,
    include_target_packets: bool = True,
) -> tuple[dict[str, Any], PacketState]:
    intermediate_packets, first_fusion = fusion_witness(
        packets, edge["first_word"], letters
    )
    second_fusion = None
    target_packets = intermediate_packets
    if edge["type"] == "II":
        target_packets, second_fusion = fusion_witness(
            intermediate_packets, edge["second_word"], letters
        )
    if packet_mass(target_packets, n) != tuple(int(value) for value in edge["target"]):
        raise AssertionError("activated block packets miss the mass endpoint")
    row = edge_summary(edge)
    row["first_fusion"] = first_fusion
    row["second_fusion"] = second_fusion
    if include_target_packets:
        row["target_packets"] = serialize_packet_state(target_packets)
    return row, target_packets


def activated_choice_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(row["total_length"]),
        1 if row["type"] == "I" else 2,
        tuple(int(value) for value in row["first_word"]),
        tuple(int(value) for value in row["second_word"]),
        tuple(
            int(value) for value in row["first_fusion"]["boundary_parent_coordinates"]
        ),
        tuple(int(value) for value in row["target"]),
    )


def is_synchronizing_mass_action(letters: Letters, n: int) -> bool:
    initial = (1,) * n
    reached = {initial}
    queue = deque([initial])
    while queue:
        mass = queue.popleft()
        for letter in letters:
            target = pushforward_mass(mass, letter)
            if mass_rank(target) == 1:
                return True
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return False


__all__ = [
    "ExitOracle",
    "Letters",
    "LowRankOracle",
    "Mass",
    "PacketState",
    "Transformation",
    "activated_choice_key",
    "activated_edge_summary",
    "deserialize_packet_state",
    "digest_payload",
    "edge_summary",
    "fusion_witness",
    "is_synchronizing_mass_action",
    "macro_edge_key",
    "mass_partition",
    "packet_mass",
    "push_packets",
    "serialize_packet_state",
    "trace_packets",
]
