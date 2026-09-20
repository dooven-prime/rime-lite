#!/usr/bin/env python3
"""Exact full-letter obstruction peeling for the sharp n=6 automata.

The local classes P_2 and P_3 certify executable maturity-bounded tails.  Their
complements F_2 and F_3 are not nonsynchronizing obstructions: a state may leave
the local bad region after additional plateau transport.  This producer keeps
exact automaton-relative mass placements and computes the greatest full-letter
closed subsets O_2 subset F_2 and O_3 subset F_3.

No macro-winning label, reset coaccessibility query, Bellman policy, or profile
quotient is used by the fixed-point computation.  Occupancy and merge-order
margins are serialized only as anatomy attached to the exact graph nodes.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable, Sequence

from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, pushforward_mass, reachable_masses
from single_defect_macro_trap import (
    _canonical_occupancy,
    _raw_type_i,
    _raw_type_ii,
    corridor_structural_profile,
)
from single_defect_low_rank_base import build_low_rank_base
from single_defect_transport import kernel_blocks, single_defect_alphabet_certificate


ROOT = Path(__file__).resolve().parents[2]
Mass = tuple[int, ...]
Letters = tuple[tuple[int, ...], ...]


def _digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _partition(mass: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted((int(value) for value in mass if value), reverse=True))


def _merged_masses(boundary_occupancy: list[dict[str, Any]]) -> tuple[int, int]:
    collisions = [
        row for row in boundary_occupancy if int(row["occupied_count"]) == 2
    ]
    if len(collisions) != 1:
        raise AssertionError("unit fusion must expose exactly one occupied pair")
    masses = tuple(
        sorted((int(value) for value in collisions[0]["masses"]), reverse=True)
    )
    if len(masses) != 2:
        raise AssertionError("unit-fusion collision did not retain two masses")
    return masses


def _tail_mass(partition: Sequence[int], merged: Sequence[int]) -> int:
    remaining = list(int(value) for value in partition)
    for value in merged:
        remaining.remove(int(value))
    if len(remaining) != 1:
        raise AssertionError("rank-three unit fusion did not leave one tail mass")
    return remaining[0]


def _raw_macro_closure(letters: Letters, n: int) -> set[Mass]:
    """Return the raw-block closure used by the preceding tail audit."""
    certificate = single_defect_alphabet_certificate(letters, n)
    defect = letters[int(certificate["defect_index"])]
    start = pushforward_mass((1,) * n, defect)
    exit_cache: dict[Mass, list[dict[str, Any]]] = {}
    block_cache: dict[Mass, list[dict[str, Any]]] = {}

    def exits_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in exit_cache:
            exit_cache[mass] = endpoint_shortest_exits(mass, letters, n)
        return exit_cache[mass]

    def blocks_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in block_cache:
            exits = exits_for(mass)
            rows = _raw_type_i(mass, exits, n)
            rows.extend(_raw_type_ii(mass, exits, exits_for, n))
            block_cache[mass] = rows
        return block_cache[mass]

    closure = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for edge in blocks_for(current):
            target = tuple(int(value) for value in edge["target"])
            if target not in closure:
                closure.add(target)
                queue.append(target)
    return closure


def _successors(mass: Mass, letters: Letters) -> tuple[tuple[int, Mass], ...]:
    return tuple(
        (index, pushforward_mass(mass, letter))
        for index, letter in enumerate(letters)
    )


def _rank_three_margin_table(
    source: Mass,
    letters: Letters,
    defect_index: int,
) -> dict[str, Any]:
    """Return exact merge-order R3-2C margins for one exact placement."""
    partition = _partition(source)
    if len(partition) != 3:
        raise ValueError("rank-three margin table requires rank three")
    exit_cache: dict[Mass, list[dict[str, Any]]] = {}

    def exits_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in exit_cache:
            exit_cache[mass] = endpoint_shortest_exits(mass, letters, len(mass))
        return exit_cache[mass]

    groups: dict[tuple[tuple[int, int], int], list[dict[str, Any]]] = {}
    direct_margins = []
    for first_row in exits_for(source):
        target_rank = int(first_row["target_rank"])
        first = corridor_structural_profile(
            source, first_row["word"], letters, defect_index
        )
        if target_rank == 1:
            direct_margins.append(int(first["surplus"]))
            continue
        if target_rank != 2:
            continue
        if int(first["q_d"]) != 1:
            raise AssertionError("rank-three first fusion was not a unit drop")
        intermediate = tuple(int(value) for value in first_row["target"])
        merged = _merged_masses(first["boundary_occupancy"])
        tail = _tail_mass(partition, merged)
        key = (merged, tail)
        for second_row in exits_for(intermediate):
            if int(second_row["target_rank"]) != 1:
                continue
            second = corridor_structural_profile(
                intermediate, second_row["word"], letters, defect_index
            )
            if int(second["q_d"]) != 1:
                raise AssertionError("rank-two second fusion was not a unit drop")
            s1 = int(first["surplus"])
            s2 = int(second["surplus"])
            margin = s2 - max(0, -s1)
            groups.setdefault(key, []).append({
                "intermediate": list(intermediate),
                "endpoint_costs": [
                    int(first["endpoint_distance"]),
                    int(second["endpoint_distance"]),
                ],
                "surpluses": [s1, s2],
                "margin": margin,
            })

    rows = []
    for (merged, tail), candidates in sorted(groups.items()):
        best = min(
            candidates,
            key=lambda row: (
                -int(row["margin"]),
                sum(int(value) for value in row["endpoint_costs"]),
                row["endpoint_costs"],
                row["intermediate"],
            ),
        )
        rows.append({
            "merged_masses": list(merged),
            "tail_mass": tail,
            "candidate_count": len(candidates),
            "maximum_margin": int(best["margin"]),
        })
    maximum = max(
        direct_margins + [int(row["maximum_margin"]) for row in rows],
        default=None,
    )
    return {
        "merge_orders": rows,
        "direct_q2_candidate_count": len(direct_margins),
        "maximum_direct_q2_margin": max(direct_margins, default=None),
        "maximum_local_margin": maximum,
        "in_P3_by_margin": maximum is not None and maximum >= 0,
    }


def _peel_rank_two(
    f2: set[Mass],
    p2: set[Mass],
    letters: Letters,
) -> tuple[set[Mass], dict[Mass, dict[str, Any]]]:
    """Compute O_2, the greatest full-letter closed subset of F_2."""
    current = set(f2)
    records: dict[Mass, dict[str, Any]] = {}
    round_index = 0
    while True:
        removals: dict[Mass, list[dict[str, Any]]] = {}
        for source in sorted(current):
            witnesses = []
            for letter_index, target in _successors(source, letters):
                target_rank = mass_rank(target)
                if target_rank == 1:
                    witnesses.append({
                        "kind": "STRICT_FUSION_TO_RANK_ONE",
                        "letter": letter_index,
                        "target": list(target),
                    })
                elif target_rank == 2 and target not in current:
                    witnesses.append({
                        "kind": (
                            "PLATEAU_TO_P2"
                            if target in p2
                            else "PLATEAU_TO_PEELED_F2"
                        ),
                        "letter": letter_index,
                        "target": list(target),
                    })
                elif target_rank > 2:
                    raise AssertionError("deterministic action increased mass rank")
            if witnesses:
                removals[source] = sorted(
                    witnesses,
                    key=lambda row: (row["kind"], row["letter"], row["target"]),
                )
        if not removals:
            break
        round_index += 1
        for source, witnesses in removals.items():
            records[source] = {
                "peel_round": round_index,
                "witnesses": witnesses,
            }
        current.difference_update(removals)
    return current, records


def _peel_rank_three(
    f3: set[Mass],
    p3: set[Mass],
    o2: set[Mass],
    p2: set[Mass],
    f2: set[Mass],
    letters: Letters,
) -> tuple[set[Mass], dict[Mass, dict[str, Any]]]:
    """Compute O_3 after the lower-rank obstruction O_2 is frozen."""
    current = set(f3)
    records: dict[Mass, dict[str, Any]] = {}
    round_index = 0
    while True:
        removals: dict[Mass, list[dict[str, Any]]] = {}
        for source in sorted(current):
            witnesses = []
            for letter_index, target in _successors(source, letters):
                target_rank = mass_rank(target)
                if target_rank == 3 and target not in current:
                    witnesses.append({
                        "kind": (
                            "PLATEAU_TO_P3"
                            if target in p3
                            else "PLATEAU_TO_PEELED_F3"
                        ),
                        "letter": letter_index,
                        "target": list(target),
                    })
                elif target_rank == 2 and target not in o2:
                    if target in p2:
                        target_class = "P2"
                    elif target in f2:
                        target_class = "PEELED_F2"
                    else:
                        target_class = "OUTSIDE_RANK2_SCOPE"
                    witnesses.append({
                        "kind": "FUSION_TO_O2_COMPLEMENT",
                        "letter": letter_index,
                        "target": list(target),
                        "target_class": target_class,
                    })
                elif target_rank == 1:
                    witnesses.append({
                        "kind": "STRICT_FUSION_TO_RANK_ONE",
                        "letter": letter_index,
                        "target": list(target),
                    })
                elif target_rank > 3:
                    raise AssertionError("deterministic action increased mass rank")
            if witnesses:
                removals[source] = sorted(
                    witnesses,
                    key=lambda row: (row["kind"], row["letter"], row["target"]),
                )
        if not removals:
            break
        round_index += 1
        for source, witnesses in removals.items():
            records[source] = {
                "peel_round": round_index,
                "witnesses": witnesses,
            }
        current.difference_update(removals)
    return current, records


def _rank_three_escape_distances(
    f3: set[Mass],
    p3: set[Mass],
    o2: set[Mass],
    letters: Letters,
) -> dict[Mass, dict[str, Any]]:
    """Find minimum plateau length to P_3 or a fusion outside O_2."""
    reverse: dict[Mass, list[tuple[Mass, int]]] = {mass: [] for mass in f3}
    distance: dict[Mass, int] = {}
    witness: dict[Mass, dict[str, Any]] = {}
    queue: list[tuple[int, Mass]] = []

    def admit(source: Mass, cost: int, row: dict[str, Any]) -> None:
        current = distance.get(source)
        order = (row["kind"], row["letter"], row["target"])
        existing = witness.get(source)
        existing_order = None if existing is None else (
            existing["kind"], existing["letter"], existing["target"]
        )
        if current is None or cost < current or (
            cost == current and existing_order is not None and order < existing_order
        ):
            distance[source] = cost
            witness[source] = row
            heapq.heappush(queue, (cost, source))

    for source in sorted(f3):
        for letter_index, target in _successors(source, letters):
            target_rank = mass_rank(target)
            if target_rank == 3:
                if target in f3:
                    reverse[target].append((source, letter_index))
                elif target in p3:
                    admit(source, 1, {
                        "kind": "PLATEAU_TO_P3",
                        "letter": letter_index,
                        "target": list(target),
                    })
            elif target_rank < 3 and target not in o2:
                admit(source, 0, {
                    "kind": "FUSION_TO_O2_COMPLEMENT",
                    "letter": letter_index,
                    "target": list(target),
                })

    while queue:
        cost, target = heapq.heappop(queue)
        if distance.get(target) != cost:
            continue
        for source, letter_index in reverse[target]:
            admit(source, cost + 1, {
                "kind": "PLATEAU_TO_F3_SUCCESSOR",
                "letter": letter_index,
                "target": list(target),
            })
    return {
        source: {
            "escape_depth": distance[source],
            "first_step": witness[source],
        }
        for source in distance
    }


def _source_automata(source: Path) -> list[dict[str, Any]]:
    payload = json.loads(source.read_text(encoding="utf-8", newline="\n"))
    if payload.get("schema") != "single-defect-n6-raw-macro-hostile-v1":
        raise AssertionError("unexpected hostile source schema")
    samples = payload.get("type_ii_samples", [])
    if len(samples) != int(payload["counts"].get("type_ii_steps", 0)):
        raise AssertionError("obstruction audit requires every Type-II sample")
    rows: dict[tuple[int, tuple[tuple[int, ...], ...]], dict[str, Any]] = {}
    for sample in samples:
        letters = tuple(tuple(int(value) for value in row) for row in sample["letters"])
        key = (int(sample["index"]), letters)
        rows[key] = {
            "automaton_index": key[0],
            "letters": letters,
        }
    return [rows[key] for key in sorted(rows)]


def _counter_rows(counter: Counter[Any], key_name: str) -> list[dict[str, Any]]:
    return [
        {key_name: key, "count": int(value)}
        for key, value in sorted(counter.items(), key=lambda item: item[0])
    ]


def analyze(source: Path) -> dict[str, Any]:
    automata = _source_automata(source)
    totals = Counter()
    peel_reason_counts = Counter()
    primary_peel_reason_counts = Counter()
    peel_round_counts = Counter()
    escape_depth_counts = Counter()
    raw_f3_escape_depth_counts = Counter()
    raw_f3_escape_kind_counts = Counter()
    rows = []
    raw_f3_registry = []

    for automaton in automata:
        automaton_index = int(automaton["automaton_index"])
        letters: Letters = automaton["letters"]
        n = len(letters[0])
        certificate = single_defect_alphabet_certificate(letters, n)
        defect_index = int(certificate["defect_index"])
        kernel = kernel_blocks(letters[defect_index], n)
        reachable = reachable_masses(letters, n)
        raw_closure = _raw_macro_closure(letters, n)
        low_rank = build_low_rank_base(letters, n)
        labels = {
            tuple(int(value) for value in row["mass"]): bool(row["in_low_rank_base"])
            for row in low_rank["rows"]
        }
        rank_two = {mass for mass in reachable if mass_rank(mass) == 2}
        rank_three = {mass for mass in reachable if mass_rank(mass) == 3}
        p2 = {mass for mass in rank_two if labels[mass]}
        f2 = rank_two - p2
        p3 = {mass for mass in rank_three if labels[mass]}
        f3 = rank_three - p3
        o2, peel2 = _peel_rank_two(f2, p2, letters)
        o3, peel3 = _peel_rank_three(f3, p3, o2, p2, f2, letters)
        escape3 = _rank_three_escape_distances(f3, p3, o2, letters)
        raw_f3 = {mass for mass in raw_closure if mass in f3}

        if set(peel2) | o2 != f2 or set(peel2) & o2:
            raise AssertionError("rank-two peeling did not partition F_2")
        if set(peel3) | o3 != f3 or set(peel3) & o3:
            raise AssertionError("rank-three peeling did not partition F_3")
        if set(escape3) != f3 - o3:
            raise AssertionError("escape-distance domain differs from peeled F_3")

        totals.update({
            "automata": 1,
            "rank_two_states": len(rank_two),
            "p2_states": len(p2),
            "f2_states": len(f2),
            "o2_states": len(o2),
            "rank_three_states": len(rank_three),
            "p3_states": len(p3),
            "f3_states": len(f3),
            "o3_states": len(o3),
            "raw_f3_states": len(raw_f3),
            "raw_f3_in_o3": len(raw_f3 & o3),
        })

        rank_three_rows = []
        for mass in sorted(rank_three):
            margin = _rank_three_margin_table(mass, letters, defect_index)
            if bool(margin["in_P3_by_margin"]) != (mass in p3):
                raise AssertionError("rank-three margin/P_3 parity failed")
            peel = peel3.get(mass)
            escape = escape3.get(mass)
            if peel:
                peel_round_counts[f"rank3:{int(peel['peel_round'])}"] += 1
                primary_peel_reason_counts[
                    f"rank3:{peel['witnesses'][0]['kind']}"
                ] += 1
                for witness_row in peel["witnesses"]:
                    peel_reason_counts[witness_row["kind"]] += 1
            if escape:
                escape_depth_counts[int(escape["escape_depth"])] += 1
            row = {
                "mass": list(mass),
                "partition": list(_partition(mass)),
                "kernel_occupancy": _canonical_occupancy(mass, kernel),
                "in_P3": mass in p3,
                "in_F3": mass in f3,
                "in_O3": mass in o3,
                "merge_order_margins": margin,
                "peeling": peel,
                "escape": escape,
            }
            rank_three_rows.append(row)
            if mass in raw_f3:
                if escape:
                    raw_f3_escape_depth_counts[int(escape["escape_depth"])] += 1
                    raw_f3_escape_kind_counts[
                        escape["first_step"]["kind"]
                    ] += 1
                raw_f3_registry.append({
                    "automaton_index": automaton_index,
                    **row,
                })

        rank_two_failure_rows = []
        for mass in sorted(f2):
            peel = peel2.get(mass)
            if peel:
                peel_round_counts[f"rank2:{int(peel['peel_round'])}"] += 1
                primary_peel_reason_counts[
                    f"rank2:{peel['witnesses'][0]['kind']}"
                ] += 1
                for witness_row in peel["witnesses"]:
                    peel_reason_counts[witness_row["kind"]] += 1
            rank_two_failure_rows.append({
                "mass": list(mass),
                "partition": list(_partition(mass)),
                "kernel_occupancy": _canonical_occupancy(mass, kernel),
                "in_O2": mass in o2,
                "peeling": peel,
            })

        rows.append({
            "automaton_index": automaton_index,
            "defect": list(letters[defect_index]),
            "counts": {
                "rank_two": len(rank_two),
                "P2": len(p2),
                "F2": len(f2),
                "O2": len(o2),
                "rank_three": len(rank_three),
                "P3": len(p3),
                "F3": len(f3),
                "O3": len(o3),
                "raw_F3": len(raw_f3),
                "raw_F3_in_O3": len(raw_f3 & o3),
            },
            "rank_two_failure_states": rank_two_failure_rows,
            "rank_three_states": rank_three_rows,
        })

    return {
        "schema": "single-defect-n6-low-rank-obstruction-peeling-v1",
        "source_result": str(source.relative_to(ROOT).as_posix()),
        "source_result_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scope": {
            "n": 6,
            "automata": len(automata),
            "automata_selection": (
                "the distinct automata carrying the 162 selected Type-II steps "
                "in the complete hostile source"
            ),
            "state_graph": (
                "all exact mass placements reachable from the all-ones mass "
                "under the full labelled letter action, computed per automaton"
            ),
        },
        "definitions": {
            "P2_P3": (
                "winning-label-free executable local base from "
                "single_defect_low_rank_base.build_low_rank_base"
            ),
            "F2_F3": "rank-wise complements of P2 and P3",
            "O2": (
                "greatest C subset F2 whose every letter successor stays at "
                "rank two in C"
            ),
            "O3": (
                "greatest C subset F3 whose rank-three successors stay in C "
                "and whose rank-two successors lie in O2"
            ),
            "escape_depth": (
                "minimum number of rank-preserving letter steps before entering "
                "P3 or taking a strict fusion outside O2"
            ),
        },
        "counts": dict(sorted(totals.items())),
        "peel_reason_counts": dict(sorted(peel_reason_counts.items())),
        "primary_peel_reason_counts": dict(
            sorted(primary_peel_reason_counts.items())
        ),
        "peel_round_counts": dict(sorted(peel_round_counts.items())),
        "escape_depth_counts": _counter_rows(
            escape_depth_counts, "escape_depth"
        ),
        "raw_f3_escape_depth_counts": _counter_rows(
            raw_f3_escape_depth_counts, "escape_depth"
        ),
        "raw_f3_escape_kind_counts": dict(
            sorted(raw_f3_escape_kind_counts.items())
        ),
        "automaton_rows": rows,
        "raw_f3_registry": raw_f3_registry,
        "claim_boundary": [
            "P_2/P_3 failure is local certificate failure, not nonsynchronization.",
            "A raw macro trap concerns the 2C block relation; O_2/O_3 instead use every labelled letter successor and therefore certify a reset-free full-action obstruction when nonempty.",
            "The fixed-point nodes are exact automaton-relative mass placements. Partitions, occupancies, and merge-order margins are annotations, not a dynamics quotient.",
            "The source automata inherit finite selection provenance from the deterministic Type-II hostile audit, but no selected policy or future label enters the local base, full-letter graph, peeling, or escape depth.",
            "An empty O_2/O_3 in this finite scope is a hostile control and structural anatomy record; it does not prove an all-n plateau escape theorem, Forced-FFS, General FFS, or Cerny.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(args.source.resolve())
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("single_defect_low_rank_base.py"),
        producer.with_name("single_defect_macro_trap.py"),
        producer.with_name("costed_endpoint_diagnostic.py"),
        producer.with_name("mass_maturity_legacy.py"),
        producer.with_name("single_defect_transport.py"),
    )
    payload["sources"] = {
        str(path.relative_to(ROOT).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in dependencies
    }
    payload["content_sha256"] = _digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "counts": payload["counts"],
        "escape_depth_counts": payload["escape_depth_counts"],
        "raw_f3_escape_depth_counts": payload["raw_f3_escape_depth_counts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
