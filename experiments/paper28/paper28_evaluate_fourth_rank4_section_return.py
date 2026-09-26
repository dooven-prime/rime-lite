#!/usr/bin/env python3
"""Evaluate the frozen fourth rank-four relation against exact P_<=3."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_prepare_fourth_rank4_section_candidate import (
    SCHEMA as CANDIDATE_SCHEMA,
)
from paper28_prepare_fourth_rank4_section_candidate import (
    _cycle,
    _digest,
    _load,
    _sha256,
    _write,
)
from section_return_core import CompleteExitOracle, LowRankOracle

SCHEMA = "paper28-fourth-rank4-section-return-evaluation-v1"
RECEIPT_SCHEMA = "paper28-fourth-rank4-section-return-evaluation-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_CANDIDATE = (
    HERE / "results" / "paper28_fourth_rank4_section_candidate_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_fourth_rank4_section_return_evaluation_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_evaluate_fourth_rank4_section_return.py",
    "paper28_prepare_fourth_rank4_section_candidate.py",
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_audit_fourth_rank4_section_overlap.py",
    "paper28_prepare_third_rank4_section_candidate.py",
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "validation/validate_paper28_fourth_rank4_section_return.py",
)
N = 7


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name.removesuffix('.json.gz')}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_payload(candidate_path: Path) -> dict[str, Any]:
    candidate = _load(candidate_path)
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise AssertionError("unexpected fourth rank-four candidate schema")
    if candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate is not the frozen pre-evaluation artifact")
    construction_digest = _digest(candidate["construction"])
    if construction_digest != candidate["construction_payload_sha256"]:
        raise AssertionError("candidate construction digest is invalid")

    construction = candidate["construction"]
    menus = construction["menus"]
    records = construction["exact_lifts"]["receipts"]
    by_id = {str(record["receipt_id"]): record for record in records}
    if len(by_id) != len(records):
        raise AssertionError("candidate exact receipt ids are not unique")

    low_rank_by_defect: dict[tuple[int, ...], LowRankOracle] = {}

    def is_good(receipt_id: str) -> bool:
        record = by_id[receipt_id]
        defect = tuple(
            int(value) for value in record["exact"]["target_context"]["defect"]
        )
        low_rank = low_rank_by_defect.get(defect)
        if low_rank is None:
            low_rank = LowRankOracle(CompleteExitOracle((_cycle(N), defect), N))
            low_rank_by_defect[defect] = low_rank
        target = tuple(int(value) for value in record["exact"]["target_endpoint"])
        return low_rank.is_good(target)

    context_rows = []
    successful_receipt_ids: set[str] = set()
    failed_receipt_ids: set[str] = set()
    successful_channel_count = 0
    failed_channel_count = 0
    certified_target_ids: set[str] = set()
    good_histogram: Counter[int] = Counter()
    hostile_source_ids = []

    for context in menus["contexts"]:
        channel_rows = []
        for channel in context["channels"]:
            success_ids = []
            failure_ids = []
            target_ids = set()
            target_ranks = set()
            for receipt_id in channel["exact_lift_ids"]:
                record = by_id[receipt_id]
                if is_good(receipt_id):
                    success_ids.append(receipt_id)
                    successful_receipt_ids.add(receipt_id)
                    target_id = str(record["exact"]["target_context"]["context_id"])
                    target_ids.add(target_id)
                    certified_target_ids.add(target_id)
                    target_ranks.add(int(record["skeleton"]["target_rank"]))
                else:
                    failure_ids.append(receipt_id)
                    failed_receipt_ids.add(receipt_id)
            if target_ranks - {2, 3}:
                raise AssertionError("Good_4 exported a target outside rank <= 3")
            if success_ids:
                successful_channel_count += 1
            else:
                failed_channel_count += 1
            channel_rows.append(
                {
                    "channel_id": channel["channel_id"],
                    "exact_lift_count": len(channel["exact_lift_ids"]),
                    "has_successful_exact_lift": bool(success_ids),
                    "successful_exact_lift_count": len(success_ids),
                    "successful_exact_lift_ids": sorted(success_ids),
                    "unsuccessful_exact_lift_count": len(failure_ids),
                    "unsuccessful_exact_lift_ids": sorted(failure_ids),
                    "certified_target_context_ids": sorted(target_ids),
                    "certified_target_ranks": sorted(target_ranks),
                }
            )
        good_count = sum(row["has_successful_exact_lift"] for row in channel_rows)
        good_histogram[good_count] += 1
        source_id = str(context["source_context"]["context_id"])
        if not good_count:
            hostile_source_ids.append(source_id)
        context_rows.append(
            {
                "source_context_id": source_id,
                "menu_size": int(context["menu_size"]),
                "successful_channel_count": good_count,
                "failed_channel_count": int(context["menu_size"]) - good_count,
                "channels": channel_rows,
            }
        )

    all_sources_good = not hostile_source_ids
    source_contexts = [row["source_context"] for row in menus["contexts"]]
    certified_section = {
        "name": "Sec_4,cand4^(7)",
        "authority_status": (
            "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION"
            if all_sources_good
            else "NOT_GRANTED_HOSTILE_SOURCES_PRESENT"
        ),
        "context_count": len(source_contexts) if all_sources_good else 0,
        "contexts": source_contexts if all_sources_good else [],
        "context_ids_sha256": (
            _digest(sorted(row["context_id"] for row in source_contexts))
            if all_sources_good
            else None
        ),
    }
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "input": {
            "name": candidate_path.name,
            "schema": candidate["schema"],
            "sha256": _sha256(candidate_path),
            "content_sha256": candidate["content_sha256"],
            "construction_payload_sha256": candidate["construction_payload_sha256"],
        },
        "scope": {
            "ambient_n": N,
            "source_rank": 4,
            "source_context_count": menus["context_count"],
            "target": "exact_P_le3^(7)",
            "winner_selected": False,
            "menu_or_lift_rebuilt": False,
        },
        "definition": (
            "Good_4(C,m) iff an exact lift in the frozen channel has target in "
            "the exact P_<=3^(7) base"
        ),
        "evaluation": {
            "all_sources_have_good_channel": all_sources_good,
            "successful_source_count": int(menus["context_count"])
            - len(hostile_source_ids),
            "hostile_source_count": len(hostile_source_ids),
            "hostile_source_context_ids": sorted(hostile_source_ids),
            "channel_count": int(menus["channel_count"]),
            "successful_channel_count": successful_channel_count,
            "failed_channel_count": failed_channel_count,
            "exact_lift_count": int(menus["exact_lift_count"]),
            "successful_exact_lift_count": len(successful_receipt_ids),
            "unsuccessful_exact_lift_count": len(failed_receipt_ids),
            "good_channel_count_histogram": {
                str(count): sources for count, sources in sorted(good_histogram.items())
            },
            "certified_target_context_count": len(certified_target_ids),
            "contexts": context_rows,
        },
        "certified_lower_section": certified_section,
        "checkpoint_type_audit": {
            "menu_sources_equal_frozen_candidate_sources": True,
            "recursive_targets_are_only_exact_P_le3_contexts": True,
            "internal_boundaries_exported_as_checkpoints": 0,
            "winner_selected": False,
        },
        "claim_boundary": {
            "proved_if_all_sources_good": (
                "every context in the frozen 36-context fresh-consuming carrier "
                "has at least one future-free channel with an exact lift to "
                "P_<=3^(7)"
            ),
            "not_claimed": [
                "every menu channel or exact lift succeeds",
                "the candidate is maximal or canonical",
                "the corresponding rank-five return succeeds",
                "the full inherited 15120-context scope is covered",
                "an all-rank return theorem",
            ],
        },
    }
    if successful_receipt_ids | failed_receipt_ids != set(by_id):
        raise AssertionError("Good_4 evaluation did not partition exact lifts")
    if successful_channel_count + failed_channel_count != int(menus["channel_count"]):
        raise AssertionError("Good_4 evaluation did not partition channels")
    if construction_digest != _digest(candidate["construction"]):
        raise AssertionError("Good_4 evaluation mutated frozen construction")
    result["content_sha256"] = _digest(result)
    return result


def build_receipt(
    *, candidate_path: Path, output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "POST_FREEZE_EXACT_LOW_RANK_EVALUATION",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "input": {
            "name": candidate_path.name,
            "schema": payload["input"]["schema"],
            "sha256": payload["input"]["sha256"],
            "content_sha256": payload["input"]["content_sha256"],
            "construction_payload_sha256": payload["input"][
                "construction_payload_sha256"
            ],
        },
        "source_closure": [
            {
                "path": (HERE / relative).relative_to(repo_root).as_posix(),
                "sha256": _sha256(HERE / relative),
            }
            for relative in SOURCE_CLOSURE
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.candidate)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(candidate_path=args.candidate, output=args.out, payload=payload),
    )
    evaluation = payload["evaluation"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "all_sources_have_good_channel": evaluation[
                    "all_sources_have_good_channel"
                ],
                "successful_sources": evaluation["successful_source_count"],
                "hostile_sources": evaluation["hostile_source_count"],
                "successful_channels": evaluation["successful_channel_count"],
                "failed_channels": evaluation["failed_channel_count"],
                "successful_exact_lifts": evaluation["successful_exact_lift_count"],
                "unsuccessful_exact_lifts": evaluation["unsuccessful_exact_lift_count"],
                "certified_target_contexts": evaluation[
                    "certified_target_context_count"
                ],
                "section_authority": payload["certified_lower_section"][
                    "authority_status"
                ],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
