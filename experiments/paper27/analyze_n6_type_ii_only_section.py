#!/usr/bin/env python3
"""Normalize the four Type-II-only endpoints in the fixed-n=6 Entry section."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_n6_low_rank_obstruction_peeling import _digest
from costed_endpoint_diagnostic import endpoint_shortest_exits
from single_defect_low_rank_base import build_low_rank_base
from single_defect_macro_trap import _raw_type_ii, corridor_structural_profile

ROOT = Path(__file__).resolve().parents[2]
ENTRY_SCHEMA = "single-defect-n6-rank4-activated-entry-exhaustiveness-v1"
OUTPUT_SCHEMA = "single-defect-n6-type-ii-only-section-v1"
N = 6
CYCLE = tuple((index + 1) % N for index in range(N))

BALANCED_MECHANISM = "BALANCED_12_THEN_32_REPAYMENT"
UNBALANCED_MECHANISM = "UNBALANCED_11_THEN_32_REPAYMENT"


def _partition(mass: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted((int(value) for value in mass if value), reverse=True))


def _load(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8", newline="\n"))
    if payload.get("schema") != schema:
        raise AssertionError(f"unexpected input schema: {path}")
    return payload


def _fused_masses(profile: dict[str, Any]) -> list[int]:
    rows = [
        row for row in profile["boundary_occupancy"] if int(row["occupied_count"]) > 1
    ]
    if len(rows) != 1 or int(rows[0]["occupied_count"]) != 2:
        raise AssertionError("Type-II corridor lost its unit binary fusion")
    masses = [int(value) for value in rows[0]["masses"]]
    if len(masses) != 2:
        raise AssertionError("unit fusion did not expose two masses")
    return masses


def _mechanism(
    source_partition: tuple[int, ...],
    first_masses: list[int],
    second_masses: list[int],
) -> str:
    if (
        source_partition == (2, 2, 1, 1)
        and first_masses == [2, 1]
        and second_masses == [3, 2]
    ):
        return BALANCED_MECHANISM
    if (
        source_partition == (3, 1, 1, 1)
        and first_masses == [1, 1]
        and second_masses == [3, 2]
    ):
        return UNBALANCED_MECHANISM
    raise AssertionError(
        "Type-II-only endpoint left the proposed repayment mechanisms: "
        f"{source_partition}, {first_masses}, {second_masses}"
    )


def analyze(entry_path: Path) -> dict[str, Any]:
    entry = _load(entry_path, ENTRY_SCHEMA)

    rows = []
    counts = Counter()
    for action in entry["synchronizing_action_rows"]:
        choice = action["entry_choice_audit"]["section_choice"]
        if int(choice["local_type_i_descent_count"]) != 0:
            continue
        if int(choice["local_type_ii_descent_count"]) <= 0:
            raise AssertionError("Type-I-free section endpoint lacks Type-II")
        defect_text = str(action["defect"])

        defect = tuple(int(value) for value in defect_text)
        letters = (CYCLE, defect)
        source = tuple(int(value) for value in choice["checkpoint"])
        parent_best = choice["best_local_type_ii_descent"]
        base = build_low_rank_base(letters, N)
        base_labels = {
            tuple(int(value) for value in row["mass"]): bool(
                row["in_low_rank_base"]
            )
            for row in base["rows"]
        }
        exit_cache: dict[tuple[int, ...], list[dict[str, Any]]] = {}

        def exits_for(
            mass: tuple[int, ...],
            *,
            _cache: dict[tuple[int, ...], list[dict[str, Any]]] = exit_cache,
            _letters: tuple[tuple[int, ...], tuple[int, ...]] = letters,
        ) -> list[dict[str, Any]]:
            if mass not in _cache:
                _cache[mass] = endpoint_shortest_exits(mass, _letters, N)
            return _cache[mass]

        local_type_ii = [
            edge
            for edge in _raw_type_ii(source, exits_for(source), exits_for, N)
            if base_labels.get(tuple(int(value) for value in edge["target"]), False)
        ]
        if len(local_type_ii) != int(choice["local_type_ii_descent_count"]):
            raise AssertionError("section-local Type-II relation count drift")
        source_partition = _partition(source)
        desired_first = [2, 1] if source_partition == (2, 2, 1, 1) else [1, 1]
        common_receipts = []
        for edge in local_type_ii:
            first_profile = corridor_structural_profile(
                source,
                tuple(int(value) for value in edge["first_word"]),
                letters,
                1,
            )
            intermediate_profile = tuple(
                int(value) for value in first_profile["target"]
            )
            second_profile = corridor_structural_profile(
                intermediate_profile,
                tuple(int(value) for value in edge["second_word"]),
                letters,
                1,
            )
            if (
                _fused_masses(first_profile) == desired_first
                and _fused_masses(second_profile) == [3, 2]
            ):
                common_receipts.append(edge)
        if not common_receipts:
            raise AssertionError("Type-II-only endpoint lost its common mechanism")
        selected = min(
            common_receipts,
            key=lambda edge: (
                int(edge["total_length"]),
                -int(edge["total_surplus"]),
                tuple(int(value) for value in edge["first_word"]),
                tuple(int(value) for value in edge["second_word"]),
                tuple(int(value) for value in edge["target"]),
            ),
        )
        receipt = {
            "type": "II",
            "first_word": selected["first_word"],
            "second_word": selected["second_word"],
            "target": selected["target"],
            "total_length": int(selected["total_length"]),
            "total_surplus": int(selected["total_surplus"]),
        }
        receipt_selection = "MINIMUM_SECTION_LOCAL_COMMON_MECHANISM"
        first = corridor_structural_profile(
            source,
            tuple(int(value) for value in receipt["first_word"]),
            letters,
            1,
        )
        intermediate = tuple(int(value) for value in first["target"])
        second = corridor_structural_profile(
            intermediate,
            tuple(int(value) for value in receipt["second_word"]),
            letters,
            1,
        )
        if second["target"] != receipt["target"]:
            raise AssertionError("Type-II replay misses its declared endpoint")
        if int(first["q_d"]) != 1 or int(second["q_d"]) != 1:
            raise AssertionError("Type-II-only section edge is not two unit drops")
        if int(first["surplus"]) >= 0:
            raise AssertionError("Type-II first corridor carries no debt")
        if int(second["surplus"]) < -int(first["surplus"]):
            raise AssertionError("Type-II second corridor does not repay debt")

        target = tuple(int(value) for value in second["target"])
        if not base_labels.get(target, False):
            raise AssertionError("Type-II-only endpoint misses exact P_<=3")

        first_masses = _fused_masses(first)
        second_masses = _fused_masses(second)
        mechanism = _mechanism(source_partition, first_masses, second_masses)
        counts["type_ii_only_section_endpoints"] += 1
        counts[f"mechanism:{mechanism}"] += 1
        counts[f"source_partition:{source_partition}"] += 1
        counts["symbolic_receipt_differs_from_parent_best"] += int(
            receipt != parent_best
        )

        rows.append(
            {
                "defect": defect_text,
                "selector_case": action["entry_choice_audit"]["selector_case"],
                "entry_word": choice["entry_edge"]["first_word"],
                "source": list(source),
                "source_partition": list(source_partition),
                "mechanism": mechanism,
                "available_type_ii_receipts": int(
                    choice["local_type_ii_descent_count"]
                ),
                "receipt_selection": receipt_selection,
                "parent_best_type_ii_receipt": parent_best,
                "selected_symbolic_type_ii_receipt": receipt,
                "first_corridor": {
                    "word": first["word"],
                    "q_d": int(first["q_d"]),
                    "delta_m_d": int(first["delta_m_d"]),
                    "length": int(first["endpoint_distance"]),
                    "surplus": int(first["surplus"]),
                    "fused_masses": first_masses,
                    "target": first["target"],
                    "target_partition": first["target_partition"],
                },
                "second_corridor": {
                    "word": second["word"],
                    "q_d": int(second["q_d"]),
                    "delta_m_d": int(second["delta_m_d"]),
                    "length": int(second["endpoint_distance"]),
                    "surplus": int(second["surplus"]),
                    "fused_masses": second_masses,
                    "target": second["target"],
                    "target_partition": second["target_partition"],
                },
                "debt_required": -int(first["surplus"]),
                "combined_surplus": int(first["surplus"]) + int(second["surplus"]),
                "target_in_exact_P_leq3": True,
                "entry_activation_basis_sha256": _digest(choice["activated_basis"]),
            }
        )

    rows.sort(key=lambda row: (row["mechanism"], row["defect"], row["source"]))
    if len(rows) != 4:
        raise AssertionError("Type-II-only section closure is not four")
    if Counter(row["mechanism"] for row in rows) != Counter(
        {BALANCED_MECHANISM: 2, UNBALANCED_MECHANISM: 2}
    ):
        raise AssertionError("Type-II-only mechanism closure drift")

    return {
        "schema": OUTPUT_SCHEMA,
        "scope": {
            "n": N,
            "domain": (
                "selected ROOTED_N6_ENTRY_SECTION_V1 endpoints with no "
                "local Type-I descent"
            ),
            "selection_semantics": (
                "a Type-II receipt is chosen only after the complete Type-I "
                "existence test is empty; the producer then chooses the "
                "shortest section-local receipt in the declared common mechanism"
            ),
            "forbidden_inputs": [
                "Bellman or winning labels",
                "ordinary reset coaccessibility",
                "raw macro reachability as a state predicate",
            ],
        },
        "inputs": {
            str(entry_path.relative_to(ROOT).as_posix()): hashlib.sha256(
                entry_path.read_bytes()
            ).hexdigest(),
        },
        "counts": dict(sorted(counts.items())),
        "mechanism_summary": [
            {
                "mechanism": BALANCED_MECHANISM,
                "source_partition": [2, 2, 1, 1],
                "first_fusion_masses": [2, 1],
                "second_fusion_masses": [3, 2],
                "count": 2,
            },
            {
                "mechanism": UNBALANCED_MECHANISM,
                "source_partition": [3, 1, 1, 1],
                "first_fusion_masses": [1, 1],
                "second_fusion_masses": [3, 2],
                "count": 2,
            },
        ],
        "rows": rows,
        "theorem_boundary": {
            "fixed_n6_section_image_is_type_i_or_two_type_ii_mechanisms": True,
            "type_i_section_endpoints": 1700,
            "type_ii_only_section_endpoints": 4,
            "interpretation": (
                "the shortest fixed-n=6 proof has a 1700-endpoint Type-I "
                "branch and four explicitly replayed Type-II-only endpoints"
            ),
        },
        "nonclaims": [
            "The two mechanisms classify the fixed-n=6 selected section only.",
            "They do not prove the wider balanced or open-wedge structural lemmas.",
            "They do not replace the all-n Entry-section or macro-return problems.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entry",
        type=Path,
        default=ROOT / "experiments/paper27/results/"
        "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json",
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(args.entry)
    producer = Path(__file__).resolve()
    dependencies = (
        producer,
        producer.with_name("analyze_n6_low_rank_obstruction_peeling.py"),
        producer.with_name("costed_endpoint_diagnostic.py"),
        producer.with_name("mass_maturity_legacy.py"),
        producer.with_name("single_defect_low_rank_base.py"),
        producer.with_name("single_defect_macro_trap.py"),
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
    print(
        json.dumps(
            {
                "counts": payload["counts"],
                "mechanisms": payload["mechanism_summary"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
