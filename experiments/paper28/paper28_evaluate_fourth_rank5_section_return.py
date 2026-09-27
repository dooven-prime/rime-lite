#!/usr/bin/env python3
"""Evaluate ordinary and fresh-consuming Good_5 on the frozen fourth relation."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_evaluate_third_rank5_section_return import _typed_handoff
from paper28_prepare_fourth_rank5_section_candidate import (
    DEFAULT_LOWER_SECTION,
    _digest,
    _load,
    _project_lower_section,
    _sha256,
    _write,
)
from paper28_prepare_fourth_rank5_section_candidate import (
    DEFAULT_OUTPUT as DEFAULT_CANDIDATE,
)
from paper28_prepare_fourth_rank5_section_candidate import (
    SCHEMA as CANDIDATE_SCHEMA,
)
from paper28_prepare_rank5_section_candidate import _boundary_key

SCHEMA = "paper28-fourth-rank5-section-return-evaluation-v1"
RECEIPT_SCHEMA = "paper28-fourth-rank5-section-return-evaluation-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_fourth_rank5_section_return_evaluation_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_evaluate_fourth_rank5_section_return.py",
    "paper28_prepare_fourth_rank5_section_candidate.py",
    "paper28_evaluate_fourth_rank4_section_return.py",
    "paper28_evaluate_third_rank5_section_return.py",
    "paper28_prepare_rank5_section_candidate.py",
    "paper28_select_fresh_consumption_hostile.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_fourth_rank5_section_return.py",
)


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name.removesuffix('.json.gz')}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _packet_map(context: Mapping[str, Any]) -> dict[int, frozenset[int]]:
    return {
        int(row["coordinate"]): frozenset(int(value) for value in row["packet"])
        for row in context["packets"]
    }


def _load_lower_authority(
    path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = _load(path)
    projection = _project_lower_section(path)
    contexts = payload["certified_lower_section"]["contexts"]
    by_boundary: dict[str, dict[str, Any]] = {}
    for context in contexts:
        boundary = _boundary_key(
            defect=context["defect"],
            packets=_packet_map(context),
            distinguished=frozenset(
                int(value) for value in context["distinguished_packet"]
            ),
        )
        key = _digest(boundary)
        if key in by_boundary:
            raise AssertionError("lower authority boundary key is not unique")
        by_boundary[key] = context
    if len(by_boundary) != int(projection["context_count"]):
        raise AssertionError("lower authority projection/context mismatch")
    return projection, by_boundary


def _validate_candidate(candidate: Mapping[str, Any]) -> None:
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise AssertionError("unexpected fourth rank-five candidate schema")
    if candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5 evaluation")
    if candidate["scope"]["hostile_evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate already contains Good_5_consume evaluation")
    evaluator = candidate["evaluator"]
    if evaluator["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("candidate evaluator is not absent")
    if candidate["construction_payload_sha256"] != _digest(candidate["construction"]):
        raise AssertionError("candidate construction digest mismatch")
    content = dict(candidate)
    observed = content.pop("content_sha256")
    if observed != _digest(content):
        raise AssertionError("candidate content digest mismatch")


def _consumes_incoming_distinguished(record: Mapping[str, Any]) -> bool:
    participation = str(record["exact"]["ancestry_update"]["participation_type"])
    if participation not in {"NONE", "FIRST_ONLY", "SECOND_ONLY", "BOTH"}:
        raise AssertionError(f"unknown ancestry participation type: {participation}")
    return participation != "NONE"


def build_payload(candidate_path: Path, lower_section_path: Path) -> dict[str, Any]:
    candidate = _load(candidate_path)
    _validate_candidate(candidate)
    lower_projection, lower_by_boundary = _load_lower_authority(lower_section_path)
    if lower_projection != candidate["lower_section_target"]:
        raise AssertionError("lower authority differs from frozen candidate projection")

    construction = candidate["construction"]
    records = construction["exact_lifts"]["receipts"]
    by_id = {str(record["receipt_id"]): record for record in records}
    if len(by_id) != len(records):
        raise AssertionError("candidate exact receipt ids are not unique")
    selected_ids = set(construction["exact_lifts"]["selected_sigma5_receipt_ids"])

    lift_evaluations: dict[str, dict[str, Any]] = {}
    ordinary_success_ids: set[str] = set()
    ordinary_failure_ids: set[str] = set()
    consume_success_ids: set[str] = set()
    handoff_histogram: Counter[str] = Counter()
    consume_handoff_histogram: Counter[str] = Counter()
    cross = {
        "fresh_consumed": {
            "target_in_lower_section": 0,
            "target_outside_lower_section": 0,
        },
        "fresh_avoided": {
            "target_in_lower_section": 0,
            "target_outside_lower_section": 0,
        },
    }

    for receipt_id, record in by_id.items():
        consumed = _consumes_incoming_distinguished(record)
        boundary = record["exact"]["target_channel"]["section_boundary_key"]
        key = _digest(boundary)
        canonical = lower_by_boundary.get(key)
        target_in = canonical is not None
        row_key = "fresh_consumed" if consumed else "fresh_avoided"
        col_key = (
            "target_in_lower_section" if target_in else "target_outside_lower_section"
        )
        cross[row_key][col_key] += 1
        if not target_in:
            ordinary_failure_ids.add(receipt_id)
            lift_evaluations[receipt_id] = {
                "receipt_id": receipt_id,
                "consumes_incoming_distinguished": consumed,
                "target_boundary_sha256": key,
                "target_in_lower_section": False,
                "ordinary_good_5": False,
                "hostile_good_5_consume": False,
                "typed_handoff": None,
            }
            continue
        handoff = _typed_handoff(record, canonical)
        ordinary_success_ids.add(receipt_id)
        handoff_histogram[handoff["handoff_type"]] += 1
        if consumed:
            consume_success_ids.add(receipt_id)
            consume_handoff_histogram[handoff["handoff_type"]] += 1
        lift_evaluations[receipt_id] = {
            "receipt_id": receipt_id,
            "consumes_incoming_distinguished": consumed,
            "target_boundary_sha256": key,
            "target_in_lower_section": True,
            "ordinary_good_5": True,
            "hostile_good_5_consume": consumed,
            "target_section_context_id": str(canonical["context_id"]),
            "exact_ancestry_update": record["exact"]["ancestry_update"],
            "typed_handoff": handoff,
        }

    context_rows = []
    ordinary_successful_channel_count = 0
    consume_successful_channel_count = 0
    ordinary_hostile_source_ids = []
    consume_hostile_source_ids = []
    ordinary_histogram: Counter[int] = Counter()
    consume_histogram: Counter[int] = Counter()
    for context in construction["menus"]["contexts"]:
        channel_rows = []
        for channel in context["channels"]:
            exact_ids = [str(value) for value in channel["exact_lift_ids"]]
            ordinary_ids = sorted(set(exact_ids) & ordinary_success_ids)
            consume_ids = sorted(set(exact_ids) & consume_success_ids)
            failure_ids = sorted(set(exact_ids) & ordinary_failure_ids)
            avoided_success_ids = sorted(set(ordinary_ids) - set(consume_ids))
            if ordinary_ids:
                ordinary_successful_channel_count += 1
            if consume_ids:
                consume_successful_channel_count += 1
            channel_rows.append(
                {
                    "channel_id": str(channel["channel_id"]),
                    "exact_lift_count": len(exact_ids),
                    "ordinary_good_5": bool(ordinary_ids),
                    "hostile_good_5_consume": bool(consume_ids),
                    "ordinary_successful_exact_lift_ids": ordinary_ids,
                    "fresh_consuming_successful_exact_lift_ids": consume_ids,
                    "fresh_avoiding_successful_exact_lift_ids": avoided_success_ids,
                    "target_outside_exact_lift_ids": failure_ids,
                }
            )
        ordinary_count = sum(row["ordinary_good_5"] for row in channel_rows)
        consume_count = sum(row["hostile_good_5_consume"] for row in channel_rows)
        source_id = str(context["source_context_id"])
        if not ordinary_count:
            ordinary_hostile_source_ids.append(source_id)
        if not consume_count:
            consume_hostile_source_ids.append(source_id)
        ordinary_histogram[ordinary_count] += 1
        consume_histogram[consume_count] += 1
        context_rows.append(
            {
                "source_context_id": source_id,
                "menu_size": int(context["menu_size"]),
                "ordinary_successful_channel_count": ordinary_count,
                "consume_successful_channel_count": consume_count,
                "channels": channel_rows,
            }
        )

    all_sources_good = not ordinary_hostile_source_ids
    all_sources_consume_good = not consume_hostile_source_ids
    selected_success_ids = selected_ids & ordinary_success_ids
    selected_consume_success_ids = selected_ids & consume_success_ids
    source_contexts = [
        row["context"] for row in construction["source_section"]["contexts"]
    ]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "input": {
            "candidate_name": candidate_path.name,
            "candidate_schema": candidate["schema"],
            "candidate_sha256": _sha256(candidate_path),
            "candidate_content_sha256": candidate["content_sha256"],
            "construction_payload_sha256": candidate["construction_payload_sha256"],
            "lower_section_name": lower_section_path.name,
            "lower_section_sha256": _sha256(lower_section_path),
            "lower_section_content_sha256": _load(lower_section_path)["content_sha256"],
        },
        "scope": {
            "ambient_n": 7,
            "source_rank": 5,
            "target_rank": 4,
            "source_context_count": construction["source_section"]["context_count"],
            "winner_selected": False,
            "menu_or_lift_rebuilt": False,
        },
        "definitions": {
            "ordinary_good_5": (
                "an exact lift in the frozen channel admits a verified typed "
                "handoff to Sec_4,cand4^(7)"
            ),
            "hostile_good_5_consume": (
                "an ordinary-successful exact lift also consumes the incoming "
                "distinguished packet"
            ),
        },
        "evaluation": {
            "all_sources_have_ordinary_good_channel": all_sources_good,
            "all_sources_have_consume_good_channel": all_sources_consume_good,
            "ordinary_successful_source_count": 36 - len(ordinary_hostile_source_ids),
            "ordinary_hostile_source_count": len(ordinary_hostile_source_ids),
            "ordinary_hostile_source_context_ids": sorted(ordinary_hostile_source_ids),
            "consume_successful_source_count": 36 - len(consume_hostile_source_ids),
            "consume_hostile_source_count": len(consume_hostile_source_ids),
            "consume_hostile_source_context_ids": sorted(consume_hostile_source_ids),
            "channel_count": int(construction["menus"]["channel_count"]),
            "ordinary_successful_channel_count": ordinary_successful_channel_count,
            "ordinary_failed_channel_count": int(construction["menus"]["channel_count"])
            - ordinary_successful_channel_count,
            "consume_successful_channel_count": consume_successful_channel_count,
            "consume_failed_channel_count": int(construction["menus"]["channel_count"])
            - consume_successful_channel_count,
            "exact_lift_count": int(construction["exact_lifts"]["receipt_count"]),
            "ordinary_successful_exact_lift_count": len(ordinary_success_ids),
            "ordinary_unsuccessful_exact_lift_count": len(ordinary_failure_ids),
            "fresh_consuming_successful_exact_lift_count": len(consume_success_ids),
            "fresh_avoiding_successful_exact_lift_count": len(
                ordinary_success_ids - consume_success_ids
            ),
            "selected_sigma5_exact_lift_count": len(selected_ids),
            "selected_sigma5_ordinary_success_count": len(selected_success_ids),
            "selected_sigma5_consume_success_count": len(selected_consume_success_ids),
            "ordinary_good_channel_count_histogram": {
                str(count): sources
                for count, sources in sorted(ordinary_histogram.items())
            },
            "consume_good_channel_count_histogram": {
                str(count): sources
                for count, sources in sorted(consume_histogram.items())
            },
            "handoff_type_histogram": dict(sorted(handoff_histogram.items())),
            "consume_handoff_type_histogram": dict(
                sorted(consume_handoff_histogram.items())
            ),
            "exact_lift_cross_table": cross,
            "contexts": context_rows,
            "lift_evaluations": [
                lift_evaluations[receipt_id] for receipt_id in sorted(lift_evaluations)
            ],
        },
        "certified_source_section": {
            "name": "Sec_5,cand4^(7)",
            "ordinary_return_authority_status": (
                "GRANTED_BY_FIXED_SCOPE_GOOD5_EVALUATION"
                if all_sources_good
                else "NOT_GRANTED_HOSTILE_SOURCES_PRESENT"
            ),
            "fresh_consumption_claim_status": (
                "PROVED_ON_FIXED_SCOPE"
                if all_sources_consume_good
                else "FAILED_ON_HOSTILE_SOURCES"
            ),
            "context_count": len(source_contexts) if all_sources_good else 0,
            "contexts": source_contexts if all_sources_good else [],
        },
        "typed_handoff_audit": {
            "lower_section": "Sec_4,cand4^(7)",
            "literal_context_identity_required": False,
            "verified_handoff_types": sorted(handoff_histogram),
            "consume_verified_handoff_types": sorted(consume_handoff_histogram),
            "rooted_action_preserved": True,
            "packet_masses_preserved": True,
            "distinguished_packet_preserved": True,
        },
        "checkpoint_type_audit": {
            "menu_sources_equal_frozen_candidate_sources": True,
            "recursive_targets_are_only_certified_lower_section_contexts": True,
            "internal_boundaries_exported_as_checkpoints": 0,
            "winner_selected": False,
        },
        "claim_boundary": {
            "ordinary_claim": (
                "every source has a future-free channel with an exact typed lift "
                "to Sec_4,cand4^(7)"
                if all_sources_good
                else "ordinary F5 fails on the listed hostile sources"
            ),
            "fresh_consumption_claim": (
                "every source has such a lift that consumes incoming ancestry"
                if all_sources_consume_good
                else "fresh-consumption hostile claim fails on the listed sources"
            ),
            "not_claimed": [
                "every menu channel succeeds",
                "every exact lift succeeds",
                "the source section is maximal or canonical",
                "the full inherited 15120-context scope is covered",
                "a non-length-three return",
                "an all-rank return theorem",
            ],
        },
    }
    if ordinary_success_ids | ordinary_failure_ids != set(by_id):
        raise AssertionError("ordinary Good_5 did not partition exact lifts")
    if not consume_success_ids <= ordinary_success_ids:
        raise AssertionError("consume-good lift is not ordinary-good")
    if sum(sum(row.values()) for row in cross.values()) != len(by_id):
        raise AssertionError("exact-lift cross table is incomplete")
    if _digest(construction) != candidate["construction_payload_sha256"]:
        raise AssertionError("Good_5 evaluation mutated frozen construction")
    result["content_sha256"] = _digest(result)
    return result


def build_receipt(
    *,
    candidate_path: Path,
    lower_section_path: Path,
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "POST_FREEZE_ORDINARY_AND_CONSUME_GOOD5_EVALUATION",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            "candidate": {
                "name": candidate_path.name,
                "sha256": _sha256(candidate_path),
                "construction_payload_sha256": payload["input"][
                    "construction_payload_sha256"
                ],
            },
            "lower_section": {
                "name": lower_section_path.name,
                "sha256": _sha256(lower_section_path),
            },
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
    parser.add_argument("--lower-section", type=Path, default=DEFAULT_LOWER_SECTION)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.candidate, args.lower_section)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            candidate_path=args.candidate,
            lower_section_path=args.lower_section,
            output=args.out,
            payload=payload,
        ),
    )
    evaluation = payload["evaluation"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "ordinary_all_sources_good": evaluation[
                    "all_sources_have_ordinary_good_channel"
                ],
                "consume_all_sources_good": evaluation[
                    "all_sources_have_consume_good_channel"
                ],
                "ordinary_successful_sources": evaluation[
                    "ordinary_successful_source_count"
                ],
                "consume_successful_sources": evaluation[
                    "consume_successful_source_count"
                ],
                "ordinary_successful_channels": evaluation[
                    "ordinary_successful_channel_count"
                ],
                "consume_successful_channels": evaluation[
                    "consume_successful_channel_count"
                ],
                "ordinary_successful_lifts": evaluation[
                    "ordinary_successful_exact_lift_count"
                ],
                "fresh_consuming_successful_lifts": evaluation[
                    "fresh_consuming_successful_exact_lift_count"
                ],
                "cross_table": evaluation["exact_lift_cross_table"],
                "ordinary_authority": payload["certified_source_section"][
                    "ordinary_return_authority_status"
                ],
                "fresh_consumption_claim": payload["certified_source_section"][
                    "fresh_consumption_claim_status"
                ],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
