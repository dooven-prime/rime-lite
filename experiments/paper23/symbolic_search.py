#!/usr/bin/env python3
"""Search auditable upper-bound expressions over synchronizing-census features."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean
from typing import Callable

from registry import CARRIER_CONTRACT, file_digest, payload_digest


def rows_from(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_digest = payload.get("content_sha256")
    if expected_digest is not None:
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        if payload_digest(unsigned) != expected_digest:
            raise ValueError(f"content digest mismatch: {path}")
    schema = payload["schema"]
    if schema == "rime.synchronizing-automata.v2":
        n = payload["scope"]["state_count"]
        return [{**row, "state_count": row.get("state_count", n)} for row in payload["analysis"]["feature_rows"]]
    if schema == "rime.synchronizing-automata.census-summary.v2":
        return payload["feature_rows"]
    if schema == "rime.synchronizing-automata.family-suite.v1":
        return [record["symbolic_feature_row"] for record in payload["records"]]
    raise ValueError(f"unsupported schema: {schema}")


def expression_library() -> dict[str, Callable[[dict], int]]:
    return {
        "(n - 1)^2": lambda row: (row["state_count"] - 1) ** 2,
        "n * (n - 1)": lambda row: row["state_count"] * (row["state_count"] - 1),
        "monoid_size - 1": lambda row: row["transition_monoid_size"] - 1,
        "nonconstant_monoid_elements": lambda row: row["nonconstant_monoid_elements"],
        "(n - 1) * minimum_letter_rank": lambda row: (row["state_count"] - 1) * row["minimum_letter_rank"],
        "minimum_letter_rank^2": lambda row: row["minimum_letter_rank"] ** 2,
        "n * maximum_letter_rank_drop": lambda row: row["state_count"] * row["maximum_letter_rank_drop"],
        "n + rank_drop_incidence_count": lambda row: row["state_count"] + row["rank_drop_incidence_count"],
        "n * (nontrivial_congruence_quotient_count + 1)": lambda row: row["state_count"] * (row["nontrivial_congruence_quotient_count"] + 1),
    }


def upper_bound_search(rows: list[dict]) -> list[dict]:
    results = []
    for expression, evaluate in expression_library().items():
        eligible = []
        for row in rows:
            try:
                value = evaluate(row)
            except KeyError:
                continue
            eligible.append((row, value - row["reset_length"]))
        assert eligible, f"no eligible rows for expression: {expression}"
        gaps = [gap for _row, gap in eligible]
        failures = [row["automaton_id"] for row, gap in eligible if gap < 0]
        family_holdout = [
            (row, gap)
            for row, gap in eligible
            if row.get("cohort") == "known_slow_family"
        ]
        results.append({
            "expression": expression,
            "holds_on_registered_rows": not failures,
            "failure_count": len(failures),
            "first_counterexamples": failures[:10],
            "eligible_row_count": len(eligible),
            "excluded_missing_feature_count": len(rows) - len(eligible),
            "minimum_slack": min(gaps),
            "mean_slack": mean(gaps),
            "equality_count": sum(gap == 0 for gap in gaps),
            "known_slow_family_holdout": {
                "eligible_row_count": len(family_holdout),
                "failure_count": sum(gap < 0 for _row, gap in family_holdout),
                "minimum_slack": (
                    min(gap for _row, gap in family_holdout)
                    if family_holdout
                    else None
                ),
            },
            "claim_status": "Research Program" if expression == "(n - 1)^2" else "Computational Observation",
        })
    return sorted(results, key=lambda item: (not item["holds_on_registered_rows"], item["mean_slack"], item["expression"]))


def affine_symbolic_search(rows: list[dict], limit: int = 25) -> dict:
    """Enumerate a small interpretable grammar around the Cerny baseline."""
    required = {
        "state_count",
        "reset_length",
        "maximum_letter_rank_drop",
        "nontrivial_congruence_quotient_count",
        "rank_drop_incidence_count",
    }
    eligible_rows = [row for row in rows if required <= row.keys()]
    assert eligible_rows, "no rows carry the full affine-search feature set"
    survivors = []
    rejected = []
    for drop_coefficient in range(-6, 3):
        for quotient_coefficient in range(-6, 3):
            for incidence_coefficient in range(-4, 3):
                for constant in range(0, 5):
                    def evaluate(row: dict) -> int:
                        baseline = (row["state_count"] - 1) ** 2
                        drop = row["maximum_letter_rank_drop"] - 1
                        quotient = int(row["nontrivial_congruence_quotient_count"] > 0)
                        incidence = row["rank_drop_incidence_count"] - 1
                        return baseline + drop_coefficient * drop + quotient_coefficient * quotient + incidence_coefficient * incidence + constant

                    gaps = [evaluate(row) - row["reset_length"] for row in eligible_rows]
                    failures = [row["automaton_id"] for row, gap in zip(eligible_rows, gaps) if gap < 0]
                    record = {
                        "expression": f"(n-1)^2 {drop_coefficient:+d}*(letter_rank_drop-1) {quotient_coefficient:+d}*has_nontrivial_quotient {incidence_coefficient:+d}*(incidence_count-1) {constant:+d}",
                        "coefficients": {"letter_rank_drop_minus_one": drop_coefficient, "has_nontrivial_quotient": quotient_coefficient, "incidence_count_minus_one": incidence_coefficient, "constant": constant},
                        "failure_count": len(failures),
                        "first_counterexamples": failures[:10],
                        "minimum_slack": min(gaps),
                        "mean_slack": mean(gaps),
                        "equality_count": sum(gap == 0 for gap in gaps),
                        "complexity": abs(drop_coefficient) + abs(quotient_coefficient) + abs(incidence_coefficient) + constant,
                        "claim_status": "Computational Observation",
                    }
                    if failures:
                        rejected.append(record)
                    else:
                        survivors.append(record)
    survivors.sort(key=lambda item: (item["mean_slack"], item["complexity"], -item["equality_count"], item["expression"]))
    rejected.sort(key=lambda item: (item["failure_count"], -item["minimum_slack"], item["mean_slack"], item["complexity"]))
    return {
        "grammar": "(n-1)^2 + a*(letter_rank_drop-1) + b*has_nontrivial_quotient + c*(incidence_count-1) + d",
        "coefficient_ranges": {"a": [-6, 2], "b": [-6, 2], "c": [-4, 2], "d": [0, 4]},
        "evaluated_expression_count": 9 * 9 * 7 * 5,
        "eligible_row_count": len(eligible_rows),
        "excluded_missing_feature_count": len(rows) - len(eligible_rows),
        "surviving_expression_count": len(survivors),
        "best_survivors": survivors[:limit],
        "best_near_misses": rejected[:limit],
    }


def conditional_envelopes(rows: list[dict]) -> dict[str, list[dict]]:
    features = [
        "maximum_letter_rank_drop",
        "rank_drop_incidence_count",
        "nontrivial_congruence_quotient_count",
        "minimum_nontrivial_quotient_size",
        "selected_witness_strict_rank_drop_count",
        "selected_witness_max_wait",
        "selected_witness_max_plateau",
        "maximum_rank_layer_escape_distance",
        "sum_rank_layer_escape_bound",
        "compatible_escape_budget",
        "largest_rank_preserving_scc_size",
    ]
    result = {}
    for feature in features:
        groups: dict[str, list[int]] = {}
        for row in rows:
            if feature not in row:
                continue
            key = str(row[feature])
            groups.setdefault(key, []).append(row["reset_length"])
        result[feature] = [{"value": key, "count": len(values), "maximum_reset_length": max(values), "mean_reset_length": mean(values)} for key, values in sorted(groups.items(), key=lambda item: item[0])]
    return result


def quotient_lift_audit(rows: list[dict]) -> dict:
    def audit(field: str) -> dict:
        applicable = [row for row in rows if row.get(field) is not None]
        failures = [
            row["automaton_id"]
            for row in applicable
            if row["reset_length"] > row[field]
        ]
        gaps = [row[field] - row["reset_length"] for row in applicable]
        return {
            "bound_field": field,
            "applicability": (
                "at least one nontrivial congruence with finite internal term"
            ),
            "applicable_row_count": len(applicable),
            "failure_count": len(failures),
            "first_counterexamples": failures[:10],
            "minimum_slack": min(gaps) if gaps else None,
            "mean_slack": mean(gaps) if gaps else None,
            "equality_count": sum(gap == 0 for gap in gaps),
            "claim_status": "Computational Certificate",
        }

    return {
        "best_uniform_bound_over_nontrivial_congruences": audit(
            "best_nontrivial_congruence_uniform_bound"
        ),
        "best_target_specific_bound_over_nontrivial_congruences": audit(
            "best_nontrivial_congruence_target_specific_bound"
        ),
        "best_selected_shortest_witness_bound_over_nontrivial_congruences": audit(
            "best_nontrivial_congruence_shortest_witness_bound"
        ),
        "target_specific_interpretation": (
            "The unrestricted target-specific minimum equals D_sync whenever "
            "applicable because every full reset word is a quotient-reset "
            "candidate with singleton internal depth zero."
        ),
    }


def hard_core_audit(rows: list[dict]) -> dict:
    selected = [row for row in rows if row.get("simple_hard_core_candidate")]
    by_state_count = []
    for state_count in sorted({row["state_count"] for row in selected}):
        group = [row for row in selected if row["state_count"] == state_count]
        maximum = max(row["reset_length"] for row in group)
        by_state_count.append({
            "state_count": state_count,
            "row_count": len(group),
            "maximum_reset_length": maximum,
            "extremal_automaton_ids": [
                row["automaton_id"]
                for row in group
                if row["reset_length"] == maximum
            ],
            "maximum_rank_preserving_scc_size": max(
                row["largest_rank_preserving_scc_size"] for row in group
            ),
        })
    return {
        "selection": "strongly connected; no nontrivial congruence (excluding equality and universal congruences); minimum letter rank n-1; maximum one-letter rank drop 1",
        "row_count": len(selected),
        "by_state_count": by_state_count,
        "claim_status": "Computational Observation",
    }


def build_payload(inputs: list[Path]) -> dict:
    input_payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in inputs
    ]
    assert all(
        payload["carrier_contract"] == CARRIER_CONTRACT
        for payload in input_payloads
    ), "all symbolic-search inputs must use the frozen carrier contract"
    rows = [row for path in inputs for row in rows_from(path)]
    assert rows, "no synchronizing feature rows"
    repository_root = Path(__file__).resolve().parents[2]

    def source_path(path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(repository_root).as_posix()
        except ValueError:
            return resolved.as_posix()

    payload = {
        "schema": "rime.synchronizing-automata.symbolic-search.v2",
        "carrier_contract": CARRIER_CONTRACT,
        "inputs": [
            {
                "path": source_path(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in inputs
        ],
        "row_count": len(rows),
        "upper_bound_search": upper_bound_search(rows),
        "affine_symbolic_search": affine_symbolic_search(rows),
        "conditional_envelopes": conditional_envelopes(rows),
        "quotient_lift_bound_audit": quotient_lift_audit(rows),
        "simple_hard_core_audit": hard_core_audit(rows),
        "producer": {
            "script": "experiments/paper23/symbolic_search.py",
            "script_sha256": file_digest(Path(__file__)),
        },
        "claim_boundary": "Expression-library search over finite feature rows. Surviving expressions are finite patterns or named conjecture candidates, not proofs.",
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.inputs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": payload["row_count"], "surviving": sum(item["holds_on_registered_rows"] for item in payload["upper_bound_search"])}, indent=2))


if __name__ == "__main__":
    main()
