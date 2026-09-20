#!/usr/bin/env python3
"""Audit rank-four checkpoint ancestry and a local exposure-section candidate.

The producer treats ``Q_4`` as a predicate evaluated only at macro endpoints.
It reconstructs the unique first-macro ancestry of every declared ``E_4``
checkpoint, tracks the packet freshly created by the last strict fusion, and
tests a small order-statistic gate on the three mixed ``(3,1,1,1)`` classes.

No plateau-closure, reset-coaccessibility, Bellman, or macro-winning label is
used by either the packet reconstruction or the exposure gate.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

from analyze_n6_low_rank_obstruction_peeling import _digest
from analyze_n6_rank4_matched_exposure import _grouped_exposure_signature
from analyze_n6_rank4_structural_descent import _source_rows
from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, pushforward_mass
from single_defect_low_rank_base import build_low_rank_base
from single_defect_macro_trap import _raw_type_i, _raw_type_ii
from single_defect_transport import single_defect_alphabet_certificate


ROOT = Path(__file__).resolve().parents[2]
Mass = tuple[int, ...]
Letters = tuple[tuple[int, ...], ...]
Packet = frozenset[int]
PacketState = dict[int, Packet]


def _partition(mass: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted((int(value) for value in mass if value), reverse=True))


def _push_packets(state: PacketState, letter: Sequence[int]) -> PacketState:
    target: dict[int, set[int]] = {}
    for coordinate, packet in state.items():
        target.setdefault(int(letter[coordinate]), set()).update(packet)
    return {
        coordinate: frozenset(labels)
        for coordinate, labels in target.items()
    }


def _packet_mass(state: PacketState, n: int) -> Mass:
    return tuple(len(state.get(index, ())) for index in range(n))


def _trace_packets(
    state: PacketState, word: Sequence[int], letters: Letters
) -> PacketState:
    current = state
    for letter_index in word:
        current = _push_packets(current, letters[int(letter_index)])
    return current


def _fusion_witness(
    state: PacketState, word: Sequence[int], letters: Letters
) -> tuple[PacketState, dict[str, Any]]:
    if not word:
        raise AssertionError("strict packet corridor is empty")
    boundary = _trace_packets(state, word[:-1], letters)
    final_letter = letters[int(word[-1])]
    grouped: dict[int, list[tuple[int, Packet]]] = defaultdict(list)
    for coordinate, packet in boundary.items():
        grouped[int(final_letter[coordinate])].append((coordinate, packet))
    collisions = [
        (target, packets)
        for target, packets in grouped.items()
        if len(packets) > 1
    ]
    if len(collisions) != 1 or len(collisions[0][1]) != 2:
        raise AssertionError("corridor does not have one binary strict fusion")
    target_coordinate, parents = collisions[0]
    parent_packets = tuple(packet for _, packet in parents)
    fresh = frozenset().union(*parent_packets)
    target = _push_packets(boundary, final_letter)
    if len(target) != len(state) - 1:
        raise AssertionError("packet corridor is not a unit rank drop")
    return target, {
        "boundary_parent_coordinates": [
            int(coordinate) for coordinate, _ in parents
        ],
        "target_coordinate": int(target_coordinate),
        "parent_packets": [sorted(packet) for packet in parent_packets],
        "parent_sizes": sorted(len(packet) for packet in parent_packets),
        "fresh_packet": sorted(fresh),
        "fresh_size": len(fresh),
    }


def _serialize_packet_state(state: PacketState) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": int(coordinate),
            "packet": sorted(packet),
            "mass": len(packet),
        }
        for coordinate, packet in sorted(state.items())
    ]


def _edge_key(edge: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(edge["total_length"]),
        -int(edge["total_surplus"]),
        edge["type"],
        edge["target"],
        edge["intermediate"] or [],
    )


def _edge_summary(
    edge: dict[str, Any],
    checkpoint_packets: PacketState,
    fresh_packet: Packet,
    letters: Letters,
) -> dict[str, Any]:
    _, fusion = _fusion_witness(
        checkpoint_packets, edge["first_word"], letters
    )
    fused_packets = [frozenset(row) for row in fusion["parent_packets"]]
    return {
        "type": edge["type"],
        "first_word": list(edge["first_word"]),
        "second_word": list(edge["second_word"]),
        "intermediate": edge["intermediate"],
        "target": list(edge["target"]),
        "target_rank": int(edge["rank_target"]),
        "total_length": int(edge["total_length"]),
        "surplus_first": int(edge["surplus_first"]),
        "surplus_second": int(edge["surplus_second"]),
        "total_surplus": int(edge["total_surplus"]),
        "first_fusion": fusion,
        "first_fusion_contains_fresh_packet": fresh_packet in fused_packets,
    }


def _slack_data(record: dict[str, Any]) -> dict[str, Any]:
    signature = dict(
        _grouped_exposure_signature(record, "full_plateau_exposure")
    )
    h11 = tuple(sorted(int(value) for value in signature[(1, 1)]))
    h31 = tuple(sorted(int(value) for value in signature[(1, 3)]))
    r11 = tuple(sorted((1 - value for value in h11), reverse=True))
    r31 = tuple(sorted((5 - value for value in h31), reverse=True))
    return {
        "h11_ordered": list(h11),
        "h31_ordered": list(h31),
        "R11_ordered": list(r11),
        "R31_ordered": list(r31),
        "checkpoint_exposure_gate": h11[0] <= 3 and h31[1] <= 6,
    }


def _order_features(record: dict[str, Any]) -> dict[str, int]:
    slack = _slack_data(record)
    r11 = tuple(int(value) for value in slack["R11_ordered"])
    r31 = tuple(int(value) for value in slack["R31_ordered"])
    rall = tuple(sorted(r11 + r31, reverse=True))
    features: dict[str, int] = {}
    for name, values in (("R11", r11), ("R31", r31), ("Rall", rall)):
        for index, value in enumerate(values, 1):
            features[f"{name}_{index}"] = value
        for index in range(2, len(values) + 1):
            features[f"{name}_top{index}_sum"] = sum(values[:index])
    return features


def _literal_holds(
    features: dict[str, int], literal: tuple[str, str, int]
) -> bool:
    name, operation, threshold = literal
    if operation == ">=":
        return features[name] >= threshold
    if operation == "<=":
        return features[name] <= threshold
    raise AssertionError("unknown order-statistic operation")


def _literal_row(
    literal: tuple[str, str, int], contamination: int
) -> dict[str, Any]:
    name, operation, threshold = literal
    return {
        "feature": name,
        "operation": operation,
        "threshold": threshold,
        "counterexample_count": contamination,
    }


def _literal_spec(literal: tuple[str, str, int]) -> dict[str, Any]:
    name, operation, threshold = literal
    return {
        "feature": name,
        "operation": operation,
        "threshold": threshold,
    }


def _order_search(
    entries: list[dict[str, int]],
    failures: list[dict[str, int]],
    successes: list[dict[str, int]],
) -> dict[str, Any]:
    feature_names = sorted(entries[0])

    entry_literals: list[tuple[int, tuple[str, str, int]]] = []
    for name in feature_names:
        candidates = (
            (name, ">=", min(row[name] for row in entries)),
            (name, "<=", max(row[name] for row in entries)),
        )
        for literal in candidates:
            contamination = sum(
                _literal_holds(row, literal) for row in failures
            )
            entry_literals.append((contamination, literal))
    entry_pairs = []
    for left, right in itertools.combinations(entry_literals, 2):
        contamination = sum(
            _literal_holds(row, left[1]) and _literal_holds(row, right[1])
            for row in failures
        )
        entry_pairs.append((contamination, left[1], right[1]))

    failure_literals: list[tuple[int, tuple[str, str, int]]] = []
    for name in feature_names:
        candidates = (
            (name, "<=", max(row[name] for row in failures)),
            (name, ">=", min(row[name] for row in failures)),
        )
        for literal in candidates:
            contamination = sum(
                _literal_holds(row, literal) for row in successes
            )
            failure_literals.append((contamination, literal))
    failure_pairs = []
    for left, right in itertools.combinations(failure_literals, 2):
        contamination = sum(
            _literal_holds(row, left[1]) and _literal_holds(row, right[1])
            for row in successes
        )
        failure_pairs.append((contamination, left[1], right[1]))

    best_entry_literal = min(entry_literals)
    best_entry_pair = min(entry_pairs)
    best_failure_literal = min(failure_literals)
    best_failure_pair = min(failure_pairs)
    zero_entry_pairs = sum(row[0] == 0 for row in entry_pairs)
    zero_failure_pairs = sum(row[0] == 0 for row in failure_pairs)
    return {
        "feature_family": {
            "features": feature_names,
            "feature_count": len(feature_names),
            "literal_count_per_quantifier": 2 * len(feature_names),
            "description": (
                "ordered R11/R31/combined slacks and nontrivial prefix sums"
            ),
        },
        "entry_quantifier": {
            "best_single": _literal_row(
                best_entry_literal[1], best_entry_literal[0]
            ),
            "best_pair": {
                "literals": [
                    _literal_spec(best_entry_pair[1]),
                    _literal_spec(best_entry_pair[2]),
                ],
                "counterexample_count": best_entry_pair[0],
            },
            "zero_counterexample_pair_count": zero_entry_pairs,
        },
        "failure_blacklist_quantifier": {
            "best_single": _literal_row(
                best_failure_literal[1], best_failure_literal[0]
            ),
            "best_pair": {
                "literals": [
                    _literal_spec(best_failure_pair[1]),
                    _literal_spec(best_failure_pair[2]),
                ],
                "counterexample_count": best_failure_pair[0],
            },
            "zero_counterexample_pair_count": zero_failure_pairs,
        },
    }


def analyze(rank_four_result: Path, exposure_result: Path) -> dict[str, Any]:
    rank_four = json.loads(rank_four_result.read_text(encoding="utf-8", newline="\n"))
    exposure = json.loads(exposure_result.read_text(encoding="utf-8", newline="\n"))
    if rank_four.get("schema") != "single-defect-n6-rank4-structural-descent-audit-v1":
        raise AssertionError("unexpected rank-four structural schema")
    if exposure.get("schema") != "single-defect-n6-rank4-matched-exposure-audit-v1":
        raise AssertionError("unexpected rank-four exposure schema")
    if ROOT / exposure["rank_four_result"] != rank_four_result:
        raise AssertionError("checkpoint audit inputs do not share rank-four source")

    hostile_path = ROOT / rank_four["source_result"]
    hostile = json.loads(hostile_path.read_text(encoding="utf-8", newline="\n"))
    source_rows = _source_rows(hostile_path)
    selected_by_index = {
        int(sample["index"]): sample["profile"]
        for sample in hostile["type_ii_samples"]
        if len(sample["profile"]["source_partition"]) == 4
    }
    structural_by_index = {
        int(row["automaton_index"]): row for row in rank_four["automaton_rows"]
    }
    exposure_records = {
        (int(record["automaton_index"]), tuple(int(value) for value in record["mass"])): record
        for class_row in exposure["class_rows"]
        for record in class_row["records"]
    }

    counts = Counter()
    partition_counts = Counter()
    fresh_best_type_counts = Counter()
    selected_counts = Counter()
    entry_rows = []
    for source_row in source_rows:
        automaton_index = int(source_row["automaton_index"])
        letters: Letters = source_row["letters"]
        n = len(letters[0])
        defect_index = int(
            single_defect_alphabet_certificate(letters, n)["defect_index"]
        )
        defect = letters[defect_index]
        singleton_packets = {
            index: frozenset((index,)) for index in range(n)
        }
        mu_packets = _push_packets(singleton_packets, defect)
        mu_d = _packet_mass(mu_packets, n)
        exit_cache: dict[Mass, list[dict[str, Any]]] = {}

        def exits_for(mass: Mass) -> list[dict[str, Any]]:
            if mass not in exit_cache:
                exit_cache[mass] = endpoint_shortest_exits(mass, letters, n)
            return exit_cache[mass]

        initial_edges = _raw_type_i(mu_d, exits_for(mu_d), n)
        initial_edges.extend(
            _raw_type_ii(mu_d, exits_for(mu_d), exits_for, n)
        )
        entry_edges = [
            edge for edge in initial_edges if int(edge["rank_target"]) == 4
        ]
        entry_by_target = {
            tuple(int(value) for value in edge["target"]): edge
            for edge in entry_edges
        }
        if len(entry_by_target) != len(entry_edges):
            raise AssertionError("rank-four endpoint has nonunique initial ancestry")
        structural = structural_by_index[automaton_index]
        raw = {
            tuple(int(value) for value in row["mass"])
            for row in structural["rank_four_states"]
            if row["in_raw_macro_closure"]
        }
        if set(entry_by_target) != raw:
            raise AssertionError("initial ancestry endpoints do not equal E4")

        base = build_low_rank_base(letters, n)
        base_labels = {
            tuple(int(value) for value in row["mass"]): bool(
                row["in_low_rank_base"]
            )
            for row in base["rows"]
        }
        selected = selected_by_index[automaton_index]
        for checkpoint, entry_edge in sorted(entry_by_target.items()):
            checkpoint_packets, ancestry = _fusion_witness(
                mu_packets, entry_edge["first_word"], letters
            )
            if _packet_mass(checkpoint_packets, n) != checkpoint:
                raise AssertionError("packet ancestry does not reconstruct checkpoint")
            fresh_packet = frozenset(ancestry["fresh_packet"])
            fresh_coordinates = [
                coordinate
                for coordinate, packet in checkpoint_packets.items()
                if packet == fresh_packet
            ]
            if fresh_coordinates != [ancestry["target_coordinate"]]:
                raise AssertionError("fresh packet location drift")
            part = _partition(checkpoint)
            counts["entry_checkpoints"] += 1
            partition_counts[str(part)] += 1
            counts[f"fresh_size:{len(fresh_packet)}"] += 1
            counts[
                "parent_sizes:" + str(tuple(ancestry["parent_sizes"]))
            ] += 1

            local_edges = _raw_type_i(checkpoint, exits_for(checkpoint), n)
            local_edges.extend(
                _raw_type_ii(
                    checkpoint, exits_for(checkpoint), exits_for, n
                )
            )
            local_edges = [
                edge
                for edge in local_edges
                if int(edge["rank_target"]) <= 3
                and base_labels.get(tuple(int(value) for value in edge["target"]), False)
            ]
            local_edges.sort(key=_edge_key)
            summaries = [
                _edge_summary(
                    edge, checkpoint_packets, fresh_packet, letters
                )
                for edge in local_edges
            ]
            fresh_edges = [
                (edge, summary)
                for edge, summary in zip(local_edges, summaries)
                if summary["first_fusion_contains_fresh_packet"]
            ]
            if not fresh_edges:
                raise AssertionError("E4 checkpoint has no fresh-packet descent")
            best_fresh_edge, best_fresh_summary = min(
                fresh_edges, key=lambda row: _edge_key(row[0])
            )
            counts["local_descent_edges"] += len(local_edges)
            counts["fresh_packet_local_descent_edges"] += len(fresh_edges)
            counts["entry_with_fresh_packet_descent"] += 1
            counts["best_edge_contains_fresh_packet"] += int(
                summaries[0]["first_fusion_contains_fresh_packet"]
            )
            fresh_best_type_counts[
                f"{part}:{best_fresh_edge['type']}"
            ] += 1

            selected_summary = None
            if tuple(int(value) for value in selected["source"]) == checkpoint:
                selected_edge = next(
                    edge
                    for edge in local_edges
                    if list(edge["first_word"]) == list(selected["first"]["word"])
                    and list(edge["second_word"]) == list(selected["second"]["word"])
                    and list(edge["target"]) == list(selected["target"])
                )
                selected_summary = _edge_summary(
                    selected_edge, checkpoint_packets, fresh_packet, letters
                )
                selected_counts["selected_rows"] += 1
                selected_counts[
                    "selected_first_fusion_contains_fresh_packet"
                ] += int(
                    selected_summary["first_fusion_contains_fresh_packet"]
                )
                selected_counts[
                    f"{part}:selected_rows"
                ] += 1
                selected_counts[
                    f"{part}:selected_contains_fresh"
                ] += int(
                    selected_summary["first_fusion_contains_fresh_packet"]
                )

            slack = None
            if part == (3, 1, 1, 1):
                record = exposure_records[(automaton_index, checkpoint)]
                if not record["in_raw_macro_closure"]:
                    raise AssertionError("mixed-class entry lost raw provenance")
                slack = _slack_data(record)
                if not slack["checkpoint_exposure_gate"]:
                    raise AssertionError("E4 checkpoint violates exposure gate")
                counts["partition_3111_entries_passing_exposure_gate"] += 1

            entry_rows.append({
                "automaton_index": automaton_index,
                "checkpoint": list(checkpoint),
                "partition": list(part),
                "entry_edge": {
                    "type": entry_edge["type"],
                    "first_word": list(entry_edge["first_word"]),
                    "surplus": int(entry_edge["surplus_first"]),
                    "total_length": int(entry_edge["total_length"]),
                },
                "ancestry": ancestry,
                "checkpoint_packets": _serialize_packet_state(
                    checkpoint_packets
                ),
                "local_descent_edge_count": len(local_edges),
                "fresh_packet_local_descent_edge_count": len(fresh_edges),
                "best_overall_edge_contains_fresh_packet": summaries[0][
                    "first_fusion_contains_fresh_packet"
                ],
                "best_fresh_packet_edge": best_fresh_summary,
                "selected_sharp_edge": selected_summary,
                "slack_order_statistics": slack,
            })

    mixed_records = [
        record
        for class_row in exposure["class_rows"]
        for record in class_row["records"]
    ]
    roles = Counter()
    gate_roles = Counter()
    entry_features = []
    failure_features = []
    success_features = []
    h_pair_counts: dict[str, Counter[tuple[int, int]]] = {
        "entry": Counter(),
        "failure": Counter(),
    }
    failure_rows = []
    for record in mixed_records:
        if record["in_raw_macro_closure"]:
            role = "entry"
        elif not record["has_local_descent"]:
            role = "failure"
        else:
            role = "other_success"
        slack = _slack_data(record)
        roles[role] += 1
        gate_roles[f"{role}:{slack['checkpoint_exposure_gate']}"] += 1
        features = _order_features(record)
        if role == "entry":
            entry_features.append(features)
            h_pair_counts["entry"][
                (slack["h11_ordered"][0], slack["h31_ordered"][1])
            ] += 1
        if role == "failure":
            failure_features.append(features)
            h_pair_counts["failure"][
                (slack["h11_ordered"][0], slack["h31_ordered"][1])
            ] += 1
            mass = tuple(int(value) for value in record["mass"])
            heavy = [index for index, value in enumerate(mass) if value == 3]
            if len(heavy) != 1:
                raise AssertionError("failure lacks unique syntactic fresh tag")
            failure_rows.append({
                "automaton_index": int(record["automaton_index"]),
                "mass": list(mass),
                "state_compatible_minimal_fresh_tag": {
                    "fresh_coordinate": heavy[0],
                    "fresh_size": 3,
                    "parent_sizes": [1, 2],
                },
                "has_local_descent": False,
                "passes_checkpoint_exposure_gate": slack[
                    "checkpoint_exposure_gate"
                ],
                "slack_order_statistics": slack,
            })
        if record["has_local_descent"]:
            success_features.append(features)

    if roles != Counter({"entry": 48, "failure": 30, "other_success": 978}):
        raise AssertionError("mixed-class role count drift")
    order_search = _order_search(
        entry_features, failure_features, success_features
    )
    chosen_gate = {
        "name": "N6_PARTITION_3111_CHECKPOINT_EXPOSURE_GATE",
        "definition": "h11_(1)<=3 and h31_(2)<=6",
        "slack_form": "R11_(1)>=-2 and R31_(2)>=-1",
        "entry_coverage": int(gate_roles["entry:True"]),
        "entry_misses": int(gate_roles["entry:False"]),
        "failure_false_positives": int(gate_roles["failure:True"]),
        "other_success_coverage": int(gate_roles["other_success:True"]),
        "total_coverage": sum(
            value
            for key, value in gate_roles.items()
            if key.endswith(":True")
        ),
    }

    return {
        "schema": "single-defect-n6-rank4-checkpoint-section-audit-v1",
        "rank_four_result": str(rank_four_result.relative_to(ROOT).as_posix()),
        "rank_four_result_sha256": hashlib.sha256(
            rank_four_result.read_bytes()
        ).hexdigest(),
        "exposure_result": str(exposure_result.relative_to(ROOT).as_posix()),
        "exposure_result_sha256": hashlib.sha256(
            exposure_result.read_bytes()
        ).hexdigest(),
        "hostile_result": rank_four["source_result"],
        "hostile_result_sha256": rank_four["source_result_sha256"],
        "scope": {
            "n": 6,
            "automata": len(source_rows),
            "checkpoint_semantics": (
                "rank-four endpoints of admissible first raw macro blocks from mu_d"
            ),
            "checkpoint_closure_requirement": "MACRO_ENDPOINT_ONLY",
        },
        "ancestry_counts": dict(sorted(counts.items())),
        "entry_partition_counts": dict(sorted(partition_counts.items())),
        "fresh_best_edge_type_counts": dict(
            sorted(fresh_best_type_counts.items())
        ),
        "selected_sharp_counts": dict(sorted(selected_counts.items())),
        "entry_rows": entry_rows,
        "mixed_class_roles": dict(sorted(roles.items())),
        "mixed_class_gate_roles": dict(sorted(gate_roles.items())),
        "entry_failure_h_pair_counts": {
            role: [
                {"h11_first": pair[0], "h31_second": pair[1], "count": count}
                for pair, count in sorted(rows.items())
            ]
            for role, rows in h_pair_counts.items()
        },
        "chosen_exposure_gate": chosen_gate,
        "order_statistic_search": order_search,
        "failure_false_tag_control": {
            "failures": len(failure_rows),
            "state_compatible_minimal_tag_count": len(failure_rows),
            "tag_fields": ["fresh_coordinate", "fresh_size", "parent_sizes"],
            "interpretation": (
                "chi1/chi2 can be attached syntactically to every (3,1,1,1) "
                "failure; a valid ancestry basis cannot be inferred from mass bytes"
            ),
            "rows": failure_rows,
        },
        "claim_boundary": [
            "Checkpoint predicates are required to be stable only under declared macro return maps, not under rank-preserving plateau action.",
            "The fresh-packet witness is generated by a source-addressed first macro edge; it is not reconstructed from mass bytes alone.",
            "The chosen exposure gate is exact finite n=6 evidence, not an all-n Entry or Escape theorem.",
            "The gate does not contain P2/P3 membership, winning, reset coaccessibility, or raw-membership labels.",
            "Fresh involvement proves existence of an alternative local descent in this sample; it does not describe the deterministic selected edge.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rank_four_result", type=Path)
    parser.add_argument("exposure_result", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(
        args.rank_four_result.resolve(), args.exposure_result.resolve()
    )
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("analyze_n6_rank4_structural_descent.py"),
        producer.with_name("analyze_n6_rank4_matched_exposure.py"),
        producer.with_name("single_defect_macro_trap.py"),
        producer.with_name("single_defect_low_rank_base.py"),
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
        "ancestry_counts": payload["ancestry_counts"],
        "chosen_exposure_gate": payload["chosen_exposure_gate"],
        "mixed_class_gate_roles": payload["mixed_class_gate_roles"],
        "selected_sharp_counts": payload["selected_sharp_counts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
