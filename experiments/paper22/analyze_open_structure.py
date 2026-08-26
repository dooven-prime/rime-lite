#!/usr/bin/env python3
"""Extract the Paper XXII precursor feature table from the Paper XXI replay.

This is an analysis layer over the published arbitrary-depth replay.  It does
not rerun the producer and does not promote any growth or uniformity pattern
to a theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "experiments" / "paper21" / "results" / "arbitrary_depth_semantic_v1.json"
DEFAULT_JSON = ROOT / "experiments" / "paper22" / "results" / "open_structure_feature_table_v1.json"
DEFAULT_MARKDOWN = ROOT / "experiments" / "paper22" / "results" / "open_structure_feature_table_v1.md"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def content_digest(payload: dict[str, Any]) -> str:
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def load_replay(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "paper.route-profiles.arbitrary-depth-semantic.v1":
        raise ValueError("input is not the Paper XXI arbitrary-depth replay")
    if payload.get("content_sha256") != content_digest(payload):
        raise ValueError("input content digest does not match")
    return payload


def profile_index(payload: dict[str, Any]) -> dict[int, dict[int, dict[str, int]]]:
    result: dict[int, dict[int, dict[str, int]]] = {}
    for record in payload["fixed_field_automata"]:
        prime = int(record["prime"])
        result[prime] = {int(row["depth"]): row for row in record["profiles"]}
    return result


def uniformity_table(payload: dict[str, Any], profiles: dict[int, dict[int, dict[str, int]]]) -> list[dict[str, Any]]:
    rows = []
    for record in payload["exceptional_characteristics"]:
        depth = int(record["depth"])
        generic = int(record["generic_zero_route_count"])
        exceptional = set(map(int, record["exceptional_characteristics"]))
        observed = []
        eligible = []
        mismatches = []
        for prime, by_depth in profiles.items():
            if depth not in by_depth:
                continue
            zero_count = int(by_depth[depth]["zero_count"])
            if prime > depth and prime not in exceptional:
                eligible.append(prime)
                if zero_count != generic:
                    mismatches.append({"prime": prime, "zero_count": zero_count})
            if zero_count == generic:
                observed.append(prime)
        rows.append(
            {
                "depth": depth,
                "generic_zero_count": generic,
                "exceptional_characteristics": sorted(exceptional),
                "eligible_sample_primes": sorted(eligible),
                "matching_sample_primes": sorted(observed),
                "eligible_mismatches": mismatches,
                "sample_status": "MATCHED" if not mismatches else "MISMATCH",
            }
        )
    return rows


def growth_table(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    previous: int | None = None
    for record in payload["exceptional_characteristics"]:
        depth = int(record["depth"])
        zero_count = int(record["generic_zero_route_count"])
        row: dict[str, Any] = {
            "depth": depth,
            "candidate_count": 0,
            "generic_zero_count": zero_count,
            "generic_nonzero_count": int(record["generic_nonzero_route_count"]),
            "zero_fraction_of_candidates": None,
            "successive_zero_ratio": None,
            "empirical_zero_root": None,
        }
        # Use the exact Boolean candidate formula, not a fitted growth model.
        row["candidate_count"] = (3**depth) * fibonacci(depth + 3)
        row["zero_fraction_of_candidates"] = zero_count / row["candidate_count"]
        if previous:
            row["successive_zero_ratio"] = zero_count / previous
        if zero_count:
            row["empirical_zero_root"] = zero_count ** (1.0 / depth)
        rows.append(row)
        previous = zero_count
    return rows


def fibonacci(index: int) -> int:
    left, right = 0, 1
    for _ in range(index):
        left, right = right, left + right
    return left


def arithmetic_table(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    seen: set[int] = set()
    for record in payload["exceptional_characteristics"]:
        exceptional = sorted(map(int, record["exceptional_characteristics"]))
        new_primes = sorted(set(exceptional) - seen)
        seen.update(exceptional)
        rows.append(
            {
                "depth": int(record["depth"]),
                "exceptional_characteristics": exceptional,
                "new_exceptional_characteristics": new_primes,
                "prefix_determinant_spectrum": record["prefix_determinant_spectrum"],
                "maximum_integral_matrix_entry": int(record["maximum_integral_matrix_entry"]),
                "distinct_prefix_pole_class_sum": int(record["distinct_prefix_pole_class_sum"]),
                "nonzero_determinants_factored": int(record["nonzero_determinants_factored"]),
            }
        )
    return rows


def automaton_table(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for record in payload["fixed_field_automata"]:
        prime = int(record["prime"])
        histogram = record.get("state_histogram", {})
        deficit_layers = {}
        for key, count in histogram.items():
            if not key.startswith("sector_1_card_"):
                continue
            card = int(key.rsplit("_", 1)[1])
            deficit_layers[str(prime - card)] = int(count)
        rows.append(
            {
            "prime": prime,
            "reachable_state_count": int(record["reachable_state_count"]),
            "ambient_state_bound": int(record["ambient_state_bound"]),
            "state_bound_fraction": int(record["reachable_state_count"]) / int(record["ambient_state_bound"]),
            "sector_1_deficit_layers": deficit_layers,
            }
        )
    return rows


def build_feature_table(payload: dict[str, Any]) -> dict[str, Any]:
    profiles = profile_index(payload)
    uniformity = uniformity_table(payload, profiles)
    growth = growth_table(payload)
    arithmetic = arithmetic_table(payload)
    automata = automaton_table(payload)
    return {
        "schema": "paper22.open-structure-feature-table.v1",
        "artifact_role": "COMPUTATIONAL_OBSERVATION_ANALYSIS_OF_PAPER21_PRECURSOR_REPLAY",
        "source_artifact": {
            "uri": "experiments/paper21/results/arbitrary_depth_semantic_v1.json",
            "content_sha256": payload["content_sha256"],
        },
        "claim_status": "computational_observation",
        "scope": {
            "depth_range": [row["depth"] for row in growth],
            "sample_primes": sorted(profiles),
            "purpose": "baseline for uniformity, growth, and arithmetic-structure research",
        },
        "uniformity": uniformity,
        "growth": growth,
        "arithmetic": arithmetic,
        "fixed_field_automata": automata,
        "interpretation_boundary": [
            "matching sampled profiles do not prove a field-independent law",
            "empirical roots and ratios do not establish an asymptotic growth constant",
            "exceptional-characteristic lists are finite-depth arithmetic observations",
            "automaton state counts are representation- and marking-relative",
        ],
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Paper XXII Open-Structure Feature Table",
        "",
        "Status: computational observation derived from the published Paper XXI arbitrary-depth replay.",
        "The table is a research baseline, not a new theorem or release receipt.",
        "",
        "## Uniformity",
        "",
        "| depth | generic zero | eligible primes | mismatches | status |",
        "|---:|---:|---|---:|---|",
    ]
    for row in payload["uniformity"]:
        lines.append(
            f"| {row['depth']} | {row['generic_zero_count']} | "
            f"{','.join(map(str, row['eligible_sample_primes'])) or '-'} | "
            f"{len(row['eligible_mismatches'])} | {row['sample_status']} |"
        )
    lines += [
        "",
        "## Growth",
        "",
        "| depth | candidates | generic zero | zero fraction | successive ratio | empirical root |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["growth"]:
        fmt = lambda value: "-" if value is None else f"{value:.8f}"
        lines.append(
            f"| {row['depth']} | {row['candidate_count']} | {row['generic_zero_count']} | "
            f"{fmt(row['zero_fraction_of_candidates'])} | {fmt(row['successive_zero_ratio'])} | "
            f"{fmt(row['empirical_zero_root'])} |"
        )
    lines += [
        "",
        "## Arithmetic Structure",
        "",
        "| depth | exceptional characteristics | determinant spectrum | max entry | pole-class sum |",
        "|---:|---|---|---:|---:|",
    ]
    for row in payload["arithmetic"]:
        lines.append(
            f"| {row['depth']} | {row['exceptional_characteristics'] or '-'} | "
            f"{row['prefix_determinant_spectrum']} | {row['maximum_integral_matrix_entry']} | "
            f"{row['distinct_prefix_pole_class_sum']} |"
        )
    lines += [
        "",
        "## Fixed-Field Automata",
        "",
        "| prime | reachable states | ambient bound | state-bound fraction |",
        "|---:|---:|---:|---:|",
    ]
    for row in payload["fixed_field_automata"]:
        lines.append(
            f"| {row['prime']} | {row['reachable_state_count']} | "
            f"{row['ambient_state_bound']} | {row['state_bound_fraction']:.8f} |"
        )
    lines += [
        "",
        "Deficit layers record the number of reachable sector-1 survivor subsets with "
        "`k = p - |S|`. Repeated tail values are a candidate uniformity signal only.",
        "",
        "| prime | deficit-layer counts (`k: count`) |",
        "|---:|---|",
    ]
    for row in payload["fixed_field_automata"]:
        layers = ", ".join(f"{k}:{v}" for k, v in sorted(row["sector_1_deficit_layers"].items(), key=lambda item: int(item[0])))
        lines.append(f"| {row['prime']} | {layers} |")
    lines += [
        "",
        "## Boundary",
        "",
        "- This is a deterministic feature extraction from an existing exact replay.",
        "- It does not prove uniformity beyond the listed sample primes.",
        "- It does not establish a scalar asymptotic, recurrence, or periodicity law.",
        "- The next theorem candidates are a generic profile recurrence, a uniform automaton quotient, or an arithmetic recurrence for `E_d`.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    feature_table = build_feature_table(load_replay(args.input))
    feature_table["content_sha256"] = content_digest(feature_table)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(feature_table, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.markdown_out.write_text(markdown(feature_table), encoding="utf-8", newline="\n")
    print(f"PASS {feature_table['schema']}: {len(feature_table['uniformity'])} depths")
    print(f"JSON {args.json_out}")
    print(f"MARKDOWN {args.markdown_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
