#!/usr/bin/env python3
"""Validate inverse-closed permutation-core corridor audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import resolve_repository_reference
from audit_kernel_schreier_corridors import build_audit
from registry import payload_digest


def validate(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if payload.get("schema") != (
        "rime.synchronizing-automata.kernel-schreier-corridor-audit.v1"
    ):
        errors.append("schema mismatch")
    unsigned = dict(payload)
    digest = unsigned.pop("content_sha256", None)
    if digest != payload_digest(unsigned):
        errors.append("content digest mismatch")
    paths = [
        resolve_repository_reference(item["path"])
        for item in payload.get("source_artifacts", [])
    ]
    missing = [str(source) for source in paths if not source.is_file()]
    if missing:
        errors.append("missing source artifacts: " + ", ".join(missing))
    else:
        expected = build_audit(paths)
        if expected != payload:
            errors.append("audit replay mismatch")
    for row in payload.get("rows", []):
        identifier = row.get("id")
        if row.get("clean_exit_class"):
            if not row.get("structural_base_class"):
                errors.append(f"clean class lacks structural base at {identifier}")
            if row.get("clean_exit_theorem_failure_count"):
                errors.append(f"clean theorem failure at {identifier}")
            if row.get("normal_form_failure_count"):
                errors.append(f"clean class lacks core normal form at {identifier}")
        if row.get("normal_form_class") and row.get("normal_form_failure_count"):
            errors.append(f"normal-form class failure at {identifier}")
        if row.get("schreier_simulable_class"):
            if row.get("schreier_simulation_theorem_failure_count"):
                errors.append(f"Schreier simulation failure at {identifier}")
            if row.get("normal_form_failure_count"):
                errors.append(
                    f"Schreier-simulable class lacks normal form at {identifier}"
                )
        binary = row.get("binary_involutive_core_corollary", {})
        if row.get("binary_involutive_core_class"):
            if not row.get("schreier_simulable_class"):
                errors.append(
                    f"binary class lacks Schreier simulation at {identifier}"
                )
            if not binary.get("all_unit_tail_checks_passed"):
                errors.append(f"binary tail bound failure at {identifier}")
            if not binary.get("reset_bound_holds"):
                errors.append(f"binary reset bound failure at {identifier}")
            if binary.get("linear_codimension_constant_C") != 1:
                errors.append(f"binary class constant mismatch at {identifier}")
            wait_form = binary.get("wait_number_normal_form") or {}
            if not wait_form.get("normal_form_shape_verified"):
                errors.append(f"binary wait shape failure at {identifier}")
            if not wait_form.get("reset_depth_identity_holds"):
                errors.append(f"binary wait identity failure at {identifier}")
            if wait_form.get("defect_one_drop_count") != row["state_count"] - 1:
                errors.append(f"binary drop count failure at {identifier}")
            one_wait = binary.get("clean_one_wait_theorem", {})
            if row.get("clean_exit_class"):
                if not one_wait.get("applicable"):
                    errors.append(
                        f"clean binary one-wait theorem not applied at {identifier}"
                    )
                for field in (
                    "greedy_word_resets",
                    "certified_wait_number_matches_prediction",
                    "shortest_reset_depth_matches_prediction",
                    "one_wait_bound_holds",
                    "reset_depth_at_most_n",
                ):
                    if not one_wait.get(field):
                        errors.append(
                            f"clean binary {field} failure at {identifier}"
                        )
            elif one_wait.get("applicable"):
                errors.append(
                    f"one-wait theorem escaped clean scope at {identifier}"
                )
        commuting = row.get("commuting_involutive_core_theorem", {})
        if row.get("commuting_involutive_core_class"):
            if not row.get("schreier_simulable_class"):
                errors.append(
                    f"commuting class lacks Schreier simulation at {identifier}"
                )
            if not commuting.get("all_unit_tail_checks_passed"):
                errors.append(f"commuting tail bound failure at {identifier}")
            if not commuting.get("reset_bound_holds"):
                errors.append(f"commuting reset bound failure at {identifier}")
            generator_count = commuting.get(
                "distinct_nonidentity_generator_count"
            )
            core_rank = commuting.get("elementary_abelian_core_rank")
            core_order = commuting.get("elementary_abelian_core_order")
            if not (
                isinstance(generator_count, int)
                and isinstance(core_rank, int)
                and 0 <= core_rank <= generator_count
            ):
                errors.append(
                    f"invalid elementary-abelian rank at {identifier}"
                )
            elif core_order != 2 ** core_rank:
                errors.append(
                    f"invalid elementary-abelian order at {identifier}"
                )
            if commuting.get("schreier_diameter_upper_bound") != core_rank:
                errors.append(
                    f"Schreier rank bound mismatch at {identifier}"
                )
            if not commuting.get("statewise_quotient_rank_bound_holds"):
                errors.append(
                    f"statewise quotient-rank bound failure at {identifier}"
                )
            if not commuting.get(
                "all_statewise_quotient_rank_checks_passed"
            ):
                errors.append(
                    f"statewise quotient-rank check failure at {identifier}"
                )
            if not commuting.get("faithful_rank_bound_holds"):
                errors.append(
                    f"faithful elementary-abelian rank failure at {identifier}"
                )
            if not commuting.get("parameter_free_bound_holds"):
                errors.append(
                    f"parameter-free reset bound failure at {identifier}"
                )
            if not commuting.get("parameter_free_bound_at_most_cerny"):
                errors.append(
                    f"parameter-free Cerny comparison failure at {identifier}"
                )
    for summary in payload.get("summaries", []):
        if summary.get("clean_exit_theorem_failure_count"):
            errors.append(
                f"clean theorem summary failure at n={summary.get('state_count')}"
            )
        if summary.get("normal_form_failure_count"):
            errors.append(
                f"normal-form summary failure at n={summary.get('state_count')}"
            )
        if summary.get("schreier_simulation_theorem_failure_count"):
            errors.append(
                f"Schreier simulation summary failure at n={summary.get('state_count')}"
            )
        if summary.get("binary_corollary_failure_count"):
            errors.append(
                f"binary corollary summary failure at n={summary.get('state_count')}"
            )
        if summary.get("binary_clean_one_wait_failure_count"):
            errors.append(
                "binary clean one-wait summary failure at "
                f"n={summary.get('state_count')}"
            )
        if summary.get("commuting_involutive_core_failure_count"):
            errors.append(
                f"commuting-core summary failure at n={summary.get('state_count')}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    errors = validate(args.artifact)
    if errors:
        print(f"FAIL {args.artifact}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS KERNEL-SCHREIER-CORRIDOR: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
