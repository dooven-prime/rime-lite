#!/usr/bin/env python3
"""Audit pair-hitting identities over existing finite automaton records."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from _bootstrap import repository_relative_reference
from pair_hitting import pair_hitting_certificate
from registry import file_digest, payload_digest


def _records(paths: list[Path]):
    for path in paths:
        shards = sorted(path.glob("shard_*.json")) if path.is_dir() else [path]
        for shard in shards:
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for record in payload.get("records", []):
                yield shard, record


def build_audit(paths: list[Path]) -> dict:
    rows: list[dict] = []
    source_digests: dict[str, str] = {}
    for source, record in _records(paths):
        source_key = repository_relative_reference(source)
        source_digests[source_key] = file_digest(source)
        transition = tuple(tuple(letter) for letter in record["transition"])
        result = pair_hitting_certificate(transition)
        kernel_corridor_failure_count = sum(
            not corridor.get("reached_subset_verified")
            or not corridor.get("selected_prefix_plateau_verified")
            or (
                corridor.get("all_shortest_exits_unit")
                and not corridor.get("unit_first_exit_cover_verified")
            )
            for corridor in (
                row.get("kernel_corridor", {})
                for row in result["identity_rows"]
            )
        )
        packing_inversion_failure_count = sum(
            not row.get("inversion_holds")
            for row in result["unit_reachable_packing_profile"].get(
                "packing_inversion_rows", []
            )
        )
        packing_area_identity_failure_count = int(
            not result["unit_reachable_packing_profile"].get(
                "packing_area_identity_holds", False
            )
        )
        rows.append({
            "id": record.get("id", record.get("family")),
            "source": source_key,
            "state_count": len(transition[0]),
            "alphabet_size": len(transition),
            "synchronizing": result["shortest_reset_depth"] is not None,
            "reachable_nonsingleton_subset_count": result["identity_row_count"],
            "infinite_identity_row_count": result["infinite_identity_row_count"],
            "identity_failure_count": len(result["identity_failures"]),
            "kernel_corridor_failure_count": kernel_corridor_failure_count,
            "packing_inversion_failure_count": (
                packing_inversion_failure_count
            ),
            "packing_area_identity_failure_count": (
                packing_area_identity_failure_count
            ),
            "rank_profile": result["rank_profile"],
            "packing_profile": result["packing_profile"],
            "unit_reachable_packing_profile": result[
                "unit_reachable_packing_profile"
            ],
            "statewise_waiting_capacity_profile": result[
                "statewise_waiting_capacity_profile"
            ],
            "H": result["high_capacity_ranks_H"],
            "U": result["unit_capacity_ranks_U"],
        })

    cohorts: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        cohorts[row["state_count"]].append(row)
    summaries = []
    for state_count, cohort in sorted(cohorts.items()):
        synchronizing = [row for row in cohort if row["synchronizing"]]
        maximum_threshold = state_count * (state_count - 1) // 2
        maximum_profiles = []
        for threshold in range(maximum_threshold + 1):
            unrestricted_values = []
            unit_values = []
            for row in synchronizing:
                packing_row = next(
                    (
                        item for item in row["packing_profile"]["rows"]
                        if item["L"] == threshold
                    ),
                    None,
                )
                unrestricted_values.append(
                    row["packing_profile"]["eventual_infinite_pair_packing"]
                    if packing_row is None else packing_row["P_A_L"]
                )
                unit_row = next(
                    (
                        item
                        for item in row["unit_reachable_packing_profile"]["rows"]
                        if item["L"] == threshold
                    ),
                    None,
                )
                unit_values.append(
                    0 if unit_row is None else unit_row["P_A_U_reachable_L"]
                )
            maximum_profiles.append({
                "L": threshold,
                "maximum_P_A_L": max(unrestricted_values, default=0),
                "maximum_P_A_U_reachable_L": max(unit_values, default=0),
            })
        mixed_layers = 0
        strict_chi_layers = 0
        for row in synchronizing:
            for control in row["statewise_waiting_capacity_profile"].values():
                if (
                    control["unit_shortest_escape_state_count"] > 0
                    and control["high_capacity_shortest_escape_state_count"] > 0
                ):
                    mixed_layers += 1
                chi = control["statewise_ratio_chi_r"]
                kappa = control["kappa_r"]
                if (
                    chi["numerator"] * kappa["denominator"]
                    < kappa["numerator"] * chi["denominator"]
                ):
                    strict_chi_layers += 1
        summaries.append({
            "state_count": state_count,
            "record_count": len(cohort),
            "synchronizing_count": len(synchronizing),
            "reachable_nonsingleton_subset_count": sum(
                row["reachable_nonsingleton_subset_count"] for row in cohort
            ),
            "synchronizing_reachable_nonsingleton_subset_count": sum(
                row["reachable_nonsingleton_subset_count"]
                for row in synchronizing
            ),
            "infinite_identity_row_count": sum(
                row["infinite_identity_row_count"] for row in cohort
            ),
            "identity_failure_count": sum(
                row["identity_failure_count"] for row in cohort
            ),
            "kernel_corridor_failure_count": sum(
                row["kernel_corridor_failure_count"] for row in cohort
            ),
            "packing_inversion_failure_count": sum(
                row["packing_inversion_failure_count"] for row in cohort
            ),
            "packing_area_identity_failure_count": sum(
                row["packing_area_identity_failure_count"] for row in cohort
            ),
            "unit_capacity_rank_union": sorted({
                rank_value for row in cohort for rank_value in row["U"]
            }),
            "high_capacity_rank_union": sorted({
                rank_value for row in cohort for rank_value in row["H"]
            }),
            "mixed_statewise_rank_layer_count": mixed_layers,
            "strict_chi_improvement_rank_layer_count": strict_chi_layers,
            "maximum_synchronizing_packing_profiles": maximum_profiles,
        })

    payload = {
        "schema": "rime.synchronizing-automata.pair-hitting-audit.v1",
        "carrier": "pair_hitting_representation_and_automaton_specific_packing",
        "source_artifacts": [
            {"path": path, "raw_blob_sha256": digest}
            for path, digest in sorted(source_digests.items())
        ],
        "rows": rows,
        "summaries": summaries,
        "claim_boundary": {
            "pair_hitting_identity": "Exact theorem; replayed on every listed subset",
            "same_kernel_suffix_corridor": (
                "Exact theorem; selected corridor and unit cover replayed"
            ),
            "reachable_unit_packing_inversion": (
                "Exact theorem; replayed at every tail index"
            ),
            "reachable_unit_packing_area": (
                "Exact theorem; replayed by the finite layer-cake identity"
            ),
            "automaton_specific_packing": "Exact finite certificate",
            "census_patterns": "Computational Observation",
            "universal_or_class_level_packing_bound": "Open",
            "quadratic_synchronization_bound": "Open",
        },
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    payload = build_audit(args.paths)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "rows": len(payload["rows"]),
        "reachable_nonsingleton_subsets": sum(
            summary["reachable_nonsingleton_subset_count"]
            for summary in payload["summaries"]
        ),
        "identity_failures": sum(
            summary["identity_failure_count"] for summary in payload["summaries"]
        ),
        "kernel_corridor_failures": sum(
            summary["kernel_corridor_failure_count"]
            for summary in payload["summaries"]
        ),
        "packing_inversion_failures": sum(
            summary["packing_inversion_failure_count"]
            for summary in payload["summaries"]
        ),
        "packing_area_identity_failures": sum(
            summary["packing_area_identity_failure_count"]
            for summary in payload["summaries"]
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
