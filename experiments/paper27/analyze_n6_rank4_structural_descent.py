#!/usr/bin/env python3
"""Mine exact rank-four descent into the nonrecursive P_1/P_2/P_3 base.

The 24 selected 4->3->2 Type-II rows provide a sharp starting slice.  This
producer erases their future labels, reconstructs every semigroup-reachable
rank-four exact mass placement in the same automata, and asks whether a raw
Type-I/Type-II block lands in the already frozen low-rank base.

The resulting edge-existence label is an exploration target, not a definition
of Q_4.  Partition and fixed-kernel occupancy signatures are audited for mixed
success/failure classes so that a lossy source profile is not silently treated
as a dynamics quotient.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_n6_low_rank_obstruction_peeling import (
    _digest,
    _partition,
    _raw_macro_closure,
)
from costed_endpoint_diagnostic import endpoint_shortest_exits
from mass_maturity_legacy import mass_rank, reachable_masses
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


def _source_rows(source: Path) -> list[dict[str, Any]]:
    payload = json.loads(source.read_text(encoding="utf-8", newline="\n"))
    if payload.get("schema") != "single-defect-n6-raw-macro-hostile-v1":
        raise AssertionError("unexpected hostile source schema")
    rows = []
    for sample in payload["type_ii_samples"]:
        if len(sample["profile"]["source_partition"]) != 4:
            continue
        rows.append({
            "automaton_index": int(sample["index"]),
            "letters": tuple(
                tuple(int(value) for value in row) for row in sample["letters"]
            ),
            "selected_profile": sample["profile"],
        })
    keys = {(row["automaton_index"], row["letters"]) for row in rows}
    if len(rows) != 24 or len(keys) != 24:
        raise AssertionError("rank-four source does not contain 24 distinct automata")
    return sorted(rows, key=lambda row: row["automaton_index"])


def _edge_profile(
    edge: dict[str, Any],
    letters: Letters,
    defect_index: int,
    base_labels: dict[Mass, bool],
) -> dict[str, Any]:
    source = tuple(int(value) for value in edge["source"])
    first = corridor_structural_profile(
        source, edge["first_word"], letters, defect_index
    )
    second = None
    if edge["type"] == "II":
        intermediate = tuple(int(value) for value in edge["intermediate"])
        second = corridor_structural_profile(
            intermediate, edge["second_word"], letters, defect_index
        )
    target = tuple(int(value) for value in edge["target"])
    target_rank = mass_rank(target)
    if target_rank > 3:
        raise AssertionError("rank-four local descent did not reach low rank")
    if not base_labels.get(target, False):
        raise AssertionError("serialized local descent target is outside base")
    return {
        "type": edge["type"],
        "target": list(target),
        "target_rank": target_rank,
        "target_base": f"P{target_rank}",
        "intermediate": edge["intermediate"],
        "intermediate_rank": edge["rank_intermediate"],
        "total_length": int(edge["total_length"]),
        "total_surplus": int(edge["total_surplus"]),
        "first": {
            "q_d": int(first["q_d"]),
            "delta_m_d": int(first["delta_m_d"]),
            "endpoint_distance": int(first["endpoint_distance"]),
            "transport_distance": int(first["transport_distance"]),
            "surplus": int(first["surplus"]),
            "boundary_occupancy": first["boundary_occupancy"],
        },
        "second": None if second is None else {
            "q_d": int(second["q_d"]),
            "delta_m_d": int(second["delta_m_d"]),
            "endpoint_distance": int(second["endpoint_distance"]),
            "transport_distance": int(second["transport_distance"]),
            "surplus": int(second["surplus"]),
            "boundary_occupancy": second["boundary_occupancy"],
        },
    }


def _rank_four_row(
    source: Mass,
    letters: Letters,
    defect_index: int,
    base_labels: dict[Mass, bool],
    exits_cache: dict[Mass, list[dict[str, Any]]],
) -> dict[str, Any]:
    n = len(source)

    def exits_for(mass: Mass) -> list[dict[str, Any]]:
        if mass not in exits_cache:
            exits_cache[mass] = endpoint_shortest_exits(mass, letters, n)
        return exits_cache[mass]

    exits = exits_for(source)
    edges = _raw_type_i(source, exits, n)
    edges.extend(_raw_type_ii(source, exits, exits_for, n))
    local = [
        edge
        for edge in edges
        if mass_rank(tuple(int(value) for value in edge["target"])) <= 3
        and base_labels.get(
            tuple(int(value) for value in edge["target"]), False
        )
    ]
    local.sort(
        key=lambda edge: (
            int(edge["total_length"]),
            -int(edge["total_surplus"]),
            edge["type"],
            edge["target"],
            edge["intermediate"] or [],
        )
    )
    best = None
    if local:
        best = _edge_profile(local[0], letters, defect_index, base_labels)
    return {
        "mass": list(source),
        "partition": list(_partition(source)),
        "local_descent_edge_count": len(local),
        "has_local_descent_to_P_le_3": bool(local),
        "best_local_descent": best,
    }


def _signature(partition: list[int], occupancy: list[dict[str, Any]]) -> str:
    return json.dumps(
        {"partition": partition, "occupancy": occupancy},
        sort_keys=True,
        separators=(",", ":"),
    )


def analyze(source: Path) -> dict[str, Any]:
    selected = _source_rows(source)
    totals = Counter()
    selected_controls = Counter()
    target_base_counts = Counter()
    edge_type_counts = Counter()
    signature_stats: dict[str, Counter[str]] = {}
    automaton_rows = []
    selected_rows = []

    for item in selected:
        automaton_index = int(item["automaton_index"])
        letters: Letters = item["letters"]
        n = len(letters[0])
        certificate = single_defect_alphabet_certificate(letters, n)
        defect_index = int(certificate["defect_index"])
        kernel = kernel_blocks(letters[defect_index], n)
        reachable = reachable_masses(letters, n)
        raw_closure = _raw_macro_closure(letters, n)
        low_rank = build_low_rank_base(letters, n)
        base_labels = {
            tuple(int(value) for value in row["mass"]): bool(
                row["in_low_rank_base"]
            )
            for row in low_rank["rows"]
        }
        rank_four = sorted(mass for mass in reachable if mass_rank(mass) == 4)
        raw_rank_four = {mass for mass in raw_closure if mass_rank(mass) == 4}
        exits_cache: dict[Mass, list[dict[str, Any]]] = {}
        rows = []
        for mass in rank_four:
            row = _rank_four_row(
                mass, letters, defect_index, base_labels, exits_cache
            )
            occupancy = _canonical_occupancy(mass, kernel)
            in_raw = mass in raw_rank_four
            row.update({
                "kernel_occupancy": occupancy,
                "in_raw_macro_closure": in_raw,
            })
            rows.append(row)
            totals["semigroup_rank_four_states"] += 1
            totals["semigroup_rank_four_with_local_descent"] += int(
                row["has_local_descent_to_P_le_3"]
            )
            totals["raw_rank_four_states"] += int(in_raw)
            totals["raw_rank_four_with_local_descent"] += int(
                in_raw and row["has_local_descent_to_P_le_3"]
            )
            if row["best_local_descent"] is not None:
                best = row["best_local_descent"]
                edge_type_counts[best["type"]] += 1
                target_base_counts[best["target_base"]] += 1
            signature = _signature(row["partition"], occupancy)
            stats = signature_stats.setdefault(signature, Counter())
            stats["occurrences"] += 1
            stats["raw_occurrences"] += int(in_raw)
            stats["local_descent"] += int(row["has_local_descent_to_P_le_3"])

        selected_profile = item["selected_profile"]
        selected_source = tuple(
            int(value) for value in selected_profile["source"]
        )
        selected_target = tuple(
            int(value) for value in selected_profile["target"]
        )
        selected_row = next(
            row for row in rows if tuple(row["mass"]) == selected_source
        )
        selected_controls["source_in_raw_rank_four"] += int(
            selected_source in raw_rank_four
        )
        selected_controls["source_has_local_descent"] += int(
            selected_row["has_local_descent_to_P_le_3"]
        )
        selected_controls["selected_target_in_low_rank_base"] += int(
            base_labels.get(selected_target, False)
        )
        selected_controls["selected_target_rank_two"] += int(
            mass_rank(selected_target) == 2
        )
        signature = _signature(
            selected_row["partition"], selected_row["kernel_occupancy"]
        )
        signature_stats[signature]["selected_occurrences"] += 1
        selected_rows.append({
            "automaton_index": automaton_index,
            "source": list(selected_source),
            "source_partition": list(_partition(selected_source)),
            "source_occupancy": selected_row["kernel_occupancy"],
            "selected_intermediate": selected_profile["intermediate"],
            "selected_target": list(selected_target),
            "selected_target_base": f"P{mass_rank(selected_target)}",
            "selected_surpluses": [
                int(selected_profile["first"]["surplus"]),
                int(selected_profile["second"]["surplus"]),
            ],
            "selected_q": [
                int(selected_profile["first"]["q_d"]),
                int(selected_profile["second"]["q_d"]),
            ],
            "selected_delta_m": [
                int(selected_profile["first"]["delta_m_d"]),
                int(selected_profile["second"]["delta_m_d"]),
            ],
            "local_descent_edge_count": int(
                selected_row["local_descent_edge_count"]
            ),
            "best_local_descent": selected_row["best_local_descent"],
        })
        automaton_rows.append({
            "automaton_index": automaton_index,
            "defect": list(letters[defect_index]),
            "counts": {
                "semigroup_rank_four": len(rows),
                "semigroup_rank_four_with_local_descent": sum(
                    row["has_local_descent_to_P_le_3"] for row in rows
                ),
                "raw_rank_four": len(raw_rank_four),
                "raw_rank_four_with_local_descent": sum(
                    row["has_local_descent_to_P_le_3"]
                    for row in rows
                    if row["in_raw_macro_closure"]
                ),
            },
            "rank_four_states": rows,
        })

    signature_rows = []
    signature_classes = Counter()
    for encoded, stats in sorted(signature_stats.items()):
        decoded = json.loads(encoded)
        occurrences = int(stats["occurrences"])
        successes = int(stats["local_descent"])
        if successes == 0:
            classification = "ALL_FAILURE"
        elif successes == occurrences:
            classification = "ALL_SUCCESS"
        else:
            classification = "MIXED"
        signature_classes[classification] += 1
        signature_rows.append({
            **decoded,
            **dict(sorted(stats.items())),
            "failure": occurrences - successes,
            "classification": classification,
        })

    selected_count = len(selected_rows)
    return {
        "schema": "single-defect-n6-rank4-structural-descent-audit-v1",
        "source_result": str(source.relative_to(ROOT).as_posix()),
        "source_result_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scope": {
            "n": 6,
            "selected_rank4_type_ii_automata": selected_count,
            "selected_transition": "4->3->2",
            "state_scope": (
                "all exact semigroup-reachable rank-four placements in the "
                "24 selected automata, with raw-macro membership marked"
            ),
        },
        "selected_controls": {
            name: {
                "passing": int(value),
                "total": selected_count,
                "all_hold": int(value) == selected_count,
            }
            for name, value in sorted(selected_controls.items())
        },
        "counts": dict(sorted(totals.items())),
        "best_edge_type_counts": dict(sorted(edge_type_counts.items())),
        "best_target_base_counts": dict(sorted(target_base_counts.items())),
        "occupancy_signature_class_counts": dict(
            sorted(signature_classes.items())
        ),
        "occupancy_signature_rows": signature_rows,
        "selected_rank4_rows": selected_rows,
        "automaton_rows": automaton_rows,
        "candidate_boundary": {
            "target": (
                "find a source-local Q4(mu) implying a raw Type-I/Type-II "
                "block into P1 union P2 union P3"
            ),
            "not_a_candidate_definition": (
                "has_local_descent_to_P_le_3 is the exact edge-existence label "
                "being explained; using it as Q4 would be tautological"
            ),
            "allowed_source_fields": [
                "exact mass placement",
                "fixed K_d occupancy",
                "mass partition as an annotation",
                "q_d and DeltaM_d at locally declared boundaries",
                "endpoint-shortest local hitting distances",
            ],
            "forbidden_inputs": [
                "Bellman policy",
                "global macro-winning label",
                "ordinary reset coaccessibility",
                "full-letter O_r peeling label",
            ],
        },
        "claim_boundary": [
            "The 24 selected rows retain deterministic-witness selection provenance, but every reconstructed edge and low-rank target certificate is local and exact.",
            "The semigroup/raw sweeps are finite n=6 anatomy, not a rank-four Structural Entry or Escape theorem.",
            "Partition plus occupancy is audited as a potentially lossy signature; mixed classes prohibit treating it as a dynamics quotient or complete Q4 predicate.",
            "This producer does not prove Forced-FFS, General FFS, or Cerny.",
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
        producer.with_name("analyze_n6_low_rank_obstruction_peeling.py"),
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
        "scope": payload["scope"],
        "counts": payload["counts"],
        "selected_controls": payload["selected_controls"],
        "occupancy_signature_class_counts": payload[
            "occupancy_signature_class_counts"
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
