#!/usr/bin/env python3
"""Audit inverse-closed permutation-core kernel corridors."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from _bootstrap import repository_relative_reference
from kernel_schreier_corridors import kernel_schreier_corridor_certificate
from registry import file_digest, payload_digest


def _records(paths: list[Path]):
    for path in paths:
        shards = sorted(path.glob("shard_*.json")) if path.is_dir() else [path]
        for shard in shards:
            payload = json.loads(shard.read_text(encoding="utf-8"))
            for record in payload.get("records", []):
                yield shard, record


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def build_audit(paths: list[Path]) -> dict:
    rows = []
    source_digests: dict[str, str] = {}
    for source, record in _records(paths):
        source_key = repository_relative_reference(source)
        source_digests[source_key] = file_digest(source)
        transition = tuple(tuple(letter) for letter in record["transition"])
        result = kernel_schreier_corridor_certificate(transition)
        structural_base = (
            result["permutation_core_nonempty"]
            and result["inverse_closed_permutation_core"]
            and result["all_nonpermutation_letters_defect_one"]
        )
        rows.append({
            "id": record.get("id", record.get("family")),
            "family": record.get("family"),
            "source": source_key,
            "state_count": result["state_count"],
            "alphabet_size": result["alphabet_size"],
            "synchronizing": result["shortest_reset_depth"] is not None,
            "shortest_reset_depth": result["shortest_reset_depth"],
            "permutation_letter_count": len(result["permutation_letters"]),
            "defect_one_letter_count": len(result["defect_one_letters"]),
            "higher_defect_letter_count": len(result["higher_defect_letters"]),
            "permutation_core_nonempty": result[
                "permutation_core_nonempty"
            ],
            "inverse_closed_permutation_core": result[
                "inverse_closed_permutation_core"
            ],
            "all_nonpermutation_letters_defect_one": result[
                "all_nonpermutation_letters_defect_one"
            ],
            "structural_base_class": structural_base,
            "finite_escape_all_reachable_nonsingletons": result[
                "finite_escape_all_reachable_nonsingletons"
            ],
            "reachable_unit_state_count": result[
                "reachable_unit_state_count"
            ],
            "clean_exit_on_all_unit_orbits": result[
                "clean_exit_on_all_unit_orbits"
            ],
            "letterwise_schreier_simulation_on_all_unit_orbits": result[
                "letterwise_schreier_simulation_on_all_unit_orbits"
            ],
            "all_unit_shortest_exits_have_core_normal_form": result[
                "all_unit_shortest_exits_have_core_normal_form"
            ],
            "clean_exit_class": result[
                "inverse_closed_defect_one_clean_exit_class"
            ],
            "schreier_simulable_class": result[
                "inverse_closed_defect_one_schreier_simulable_class"
            ],
            "normal_form_class": result[
                "inverse_closed_defect_one_normal_form_class"
            ],
            "binary_involutive_core_class": result[
                "binary_involutive_core_corollary"
            ]["applicable"],
            "binary_involutive_core_corollary": result[
                "binary_involutive_core_corollary"
            ],
            "commuting_involutive_core_class": result[
                "commuting_involutive_core_theorem"
            ]["applicable"],
            "commuting_involutive_core_theorem": result[
                "commuting_involutive_core_theorem"
            ],
            "clean_exit_theorem_failure_count": result[
                "clean_exit_theorem_failure_count"
            ],
            "schreier_simulation_theorem_failure_count": result[
                "schreier_simulation_theorem_failure_count"
            ],
            "normal_form_failure_count": sum(
                not row["shortest_core_normal_form_holds"]
                for row in result["state_rows"]
            ),
            "clean_exit_state_failure_count": sum(
                not row["clean_exit_on_orbit"]
                for row in result["state_rows"]
            ),
            "u_r_by_rank": result["u_r_by_rank"],
            "unit_wait_tail_by_index": result[
                "unit_wait_tail_by_index"
            ],
            "maximum_linear_codimension_ratio": result[
                "maximum_linear_codimension_ratio"
            ],
            "unit_tail_sum": result["unit_tail_sum"],
            "maximum_directed_cover_radius": max(
                (
                    profile["directed_cover_radius"]
                    for profile in result["orbit_profiles"]
                    if profile["directed_cover_radius"] is not None
                ),
                default=None,
            ),
        })

    cohorts: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        cohorts[row["state_count"]].append(row)
    summaries = []
    for state_count, cohort in sorted(cohorts.items()):
        synchronizing = [row for row in cohort if row["synchronizing"]]
        clean = [row for row in synchronizing if row["clean_exit_class"]]
        normal = [row for row in synchronizing if row["normal_form_class"]]
        simulable = [
            row for row in synchronizing if row["schreier_simulable_class"]
        ]
        binary = [
            row for row in synchronizing
            if row["binary_involutive_core_class"]
        ]
        summaries.append({
            "state_count": state_count,
            "record_count": len(cohort),
            "synchronizing_count": len(synchronizing),
            "structural_base_count": sum(
                row["structural_base_class"] for row in synchronizing
            ),
            "clean_exit_class_count": len(clean),
            "normal_form_class_count": len(normal),
            "schreier_simulable_class_count": len(simulable),
            "binary_involutive_core_class_count": len(binary),
            "clean_exit_theorem_failure_count": sum(
                row["clean_exit_theorem_failure_count"] for row in clean
            ),
            "normal_form_failure_count": sum(
                row["normal_form_failure_count"] for row in normal
            ),
            "schreier_simulation_theorem_failure_count": sum(
                row["schreier_simulation_theorem_failure_count"]
                for row in simulable
            ),
            "binary_corollary_failure_count": sum(
                not row["binary_involutive_core_corollary"][
                    "all_unit_tail_checks_passed"
                ]
                or not row["binary_involutive_core_corollary"][
                    "reset_bound_holds"
                ]
                or not row["binary_involutive_core_corollary"][
                    "wait_number_normal_form"
                ]["reset_depth_identity_holds"]
                for row in binary
            ),
            "binary_clean_one_wait_failure_count": sum(
                not row["binary_involutive_core_corollary"][
                    "clean_one_wait_theorem"
                ]["greedy_word_resets"]
                or not row["binary_involutive_core_corollary"][
                    "clean_one_wait_theorem"
                ]["shortest_reset_depth_matches_prediction"]
                or not row["binary_involutive_core_corollary"][
                    "clean_one_wait_theorem"
                ]["one_wait_bound_holds"]
                for row in binary
                if row["clean_exit_class"]
            ),
            "commuting_involutive_core_class_count": sum(
                row["commuting_involutive_core_class"]
                for row in synchronizing
            ),
            "commuting_involutive_core_failure_count": sum(
                not row["commuting_involutive_core_theorem"][
                    "all_unit_tail_checks_passed"
                ]
                or not row["commuting_involutive_core_theorem"][
                    "reset_bound_holds"
                ]
                or not row["commuting_involutive_core_theorem"][
                    "statewise_quotient_rank_bound_holds"
                ]
                or not row["commuting_involutive_core_theorem"][
                    "faithful_rank_bound_holds"
                ]
                or not row["commuting_involutive_core_theorem"][
                    "parameter_free_bound_at_most_cerny"
                ]
                for row in synchronizing
                if row["commuting_involutive_core_class"]
            ),
            "maximum_clean_class_linear_ratio": (
                None if not clean else _as_fraction_object(max(
                    _fraction(row["maximum_linear_codimension_ratio"])
                    for row in clean
                ))
            ),
            "maximum_normal_class_linear_ratio": (
                None if not normal else _as_fraction_object(max(
                    _fraction(row["maximum_linear_codimension_ratio"])
                    for row in normal
                ))
            ),
            "maximum_clean_class_unit_tail_sum": max(
                (row["unit_tail_sum"] for row in clean),
                default=None,
            ),
            "maximum_normal_class_unit_tail_sum": max(
                (row["unit_tail_sum"] for row in normal),
                default=None,
            ),
            "maximum_clean_class_reset_depth": max(
                (row["shortest_reset_depth"] for row in clean),
                default=None,
            ),
            "maximum_normal_class_reset_depth": max(
                (row["shortest_reset_depth"] for row in normal),
                default=None,
            ),
        })
    payload = {
        "schema": "rime.synchronizing-automata.kernel-schreier-corridor-audit.v1",
        "carrier": "inverse_closed_permutation_core_and_defect_one_cover_exits",
        "source_artifacts": [
            {"path": path, "raw_blob_sha256": digest}
            for path, digest in sorted(source_digests.items())
        ],
        "rows": rows,
        "summaries": summaries,
        "claim_boundary": {
            "clean_exit_schreier_identity": "Exact class theorem",
            "letterwise_schreier_simulation": "Exact class theorem",
            "binary_involutive_core_linear_bound": "Exact class theorem",
            "binary_wait_number_normal_form": "Exact class theorem",
            "binary_clean_one_wait_bound": "Exact class theorem",
            "binary_clean_extremal_depth_n": "Exact class theorem",
            "commuting_involutive_core_bound": "Exact class theorem",
            "faithful_elementary_abelian_rank_bound": "Exact group theorem",
            "parameter_free_cerny_corollary": "Exact class theorem",
            "statewise_schreier_quotient_rank_bound": "Exact class theorem",
            "normal_form_rows": "Exact finite certificate",
            "n3_n4_linear_constant": "Computational Observation",
            "uniform_linear_codimension_bound": "Open",
            "global_quadratic_synchronization_bound": "Open",
        },
    }
    payload["content_sha256"] = payload_digest(payload)
    return payload


def _as_fraction_object(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


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
        "summaries": payload["summaries"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
