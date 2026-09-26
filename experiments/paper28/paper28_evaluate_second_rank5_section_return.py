#!/usr/bin/env python3
"""Evaluate Good_5 on the frozen second rank-five candidate."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_prepare_rank5_section_candidate import _boundary_key
from paper28_prepare_second_rank5_section_candidate import (
    DEFAULT_LOWER_SECTION,
    DEFAULT_OUTPUT as DEFAULT_CANDIDATE,
    SCHEMA as CANDIDATE_SCHEMA,
    _project_lower_section,
)


SCHEMA = "paper28-second-rank5-section-return-evaluation-v1"
RECEIPT_SCHEMA = "paper28-second-rank5-section-return-evaluation-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_second_rank5_section_return_evaluation_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_evaluate_second_rank5_section_return.py",
    "paper28_prepare_second_rank5_section_candidate.py",
    "paper28_evaluate_second_rank4_section_return.py",
    "paper28_prepare_rank5_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_second_rank5_section_return.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name.removesuffix('.json.gz')}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _packet_map(context: Mapping[str, Any]) -> dict[int, list[int]]:
    return {
        int(row["coordinate"]): sorted(int(value) for value in row["packet"])
        for row in context["packets"]
    }


def _typed_handoff(
    receipt: Mapping[str, Any],
    canonical_context: Mapping[str, Any],
) -> dict[str, Any]:
    actual = receipt["exact"]["target_context"]
    if [int(value) for value in actual["defect"]] != [
        int(value) for value in canonical_context["defect"]
    ]:
        raise AssertionError("typed handoff changed the rooted action")
    actual_packets = _packet_map(actual)
    canonical_packets = _packet_map(canonical_context)
    if set(actual_packets) != set(canonical_packets):
        raise AssertionError("typed handoff changed occupied coordinates")

    canonical_to_actual: dict[int, int] = {}
    role_rows = []
    for coordinate in sorted(canonical_packets):
        canonical_packet = canonical_packets[coordinate]
        actual_packet = actual_packets[coordinate]
        if len(canonical_packet) != len(actual_packet):
            raise AssertionError("typed handoff changed packet mass")
        for source, target in zip(
            canonical_packet,
            actual_packet,
            strict=True,
        ):
            canonical_to_actual[source] = target
        role_rows.append(
            {
                "coordinate": coordinate,
                "mass": len(canonical_packet),
                "canonical_packet": canonical_packet,
                "actual_packet": actual_packet,
                "is_distinguished": canonical_packet
                == sorted(canonical_context["distinguished_packet"]),
            }
        )
    if set(canonical_to_actual) != set(range(7)):
        raise AssertionError("typed handoff canonical atoms are incomplete")
    if set(canonical_to_actual.values()) != set(range(7)):
        raise AssertionError("typed handoff actual atoms are incomplete")
    mapped_distinguished = sorted(
        canonical_to_actual[int(value)]
        for value in canonical_context["distinguished_packet"]
    )
    if mapped_distinguished != sorted(actual["distinguished_packet"]):
        raise AssertionError("typed handoff changed distinguished ancestry")

    actual_to_canonical = {
        target: source for source, target in canonical_to_actual.items()
    }
    identity = (
        str(actual["context_id"]) == str(canonical_context["context_id"])
        and all(source == target for source, target in canonical_to_actual.items())
    )
    return {
        "handoff_type": "IDENTITY" if identity else "ATOM_BIJECTION",
        "actual_target_context_id": str(actual["context_id"]),
        "canonical_lower_context_id": str(canonical_context["context_id"]),
        "canonical_to_actual_atom_bijection": [
            {"canonical_atom": source, "actual_atom": target}
            for source, target in sorted(canonical_to_actual.items())
        ],
        "actual_to_canonical_atom_bijection": [
            {"actual_atom": source, "canonical_atom": target}
            for source, target in sorted(actual_to_canonical.items())
        ],
        "packet_correspondence": role_rows,
        "rooted_action_preserved": True,
        "packet_masses_preserved": True,
        "distinguished_packet_preserved": True,
    }


def _load_lower_authority(
    path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = _load(path)
    projection = _project_lower_section(path)
    contexts = payload["certified_lower_section"]["contexts"]
    by_boundary: dict[str, dict[str, Any]] = {}
    for context in contexts:
        packet_map = {
            int(row["coordinate"]): frozenset(
                int(value) for value in row["packet"]
            )
            for row in context["packets"]
        }
        boundary = _boundary_key(
            defect=context["defect"],
            packets=packet_map,
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
        raise AssertionError("unexpected second rank-five candidate schema")
    if candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("candidate is not the frozen pre-evaluation object")
    if candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("candidate already contains an evaluator")
    if candidate["construction_payload_sha256"] != _digest(
        candidate["construction"]
    ):
        raise AssertionError("candidate construction digest mismatch")
    content = dict(candidate)
    observed = content.pop("content_sha256")
    if observed != _digest(content):
        raise AssertionError("candidate content digest mismatch")


def build_payload(
    candidate_path: Path,
    lower_section_path: Path,
) -> dict[str, Any]:
    candidate = _load(candidate_path)
    _validate_candidate(candidate)
    lower_projection, lower_by_boundary = _load_lower_authority(
        lower_section_path
    )
    if lower_projection != candidate["lower_section_target"]:
        raise AssertionError(
            "lower authority differs from frozen candidate projection"
        )

    construction = candidate["construction"]
    records = construction["exact_lifts"]["receipts"]
    by_id = {str(record["receipt_id"]): record for record in records}
    if len(by_id) != len(records):
        raise AssertionError("candidate exact receipt ids are not unique")

    lift_evaluations: dict[str, dict[str, Any]] = {}
    handoff_histogram: Counter[str] = Counter()
    successful_receipt_ids: set[str] = set()
    failed_receipt_ids: set[str] = set()
    for receipt_id, record in by_id.items():
        boundary = record["exact"]["target_channel"]["section_boundary_key"]
        key = _digest(boundary)
        canonical = lower_by_boundary.get(key)
        if canonical is None:
            failed_receipt_ids.add(receipt_id)
            lift_evaluations[receipt_id] = {
                "receipt_id": receipt_id,
                "target_boundary_sha256": key,
                "target_in_lower_section": False,
                "typed_handoff": None,
            }
            continue
        handoff = _typed_handoff(record, canonical)
        successful_receipt_ids.add(receipt_id)
        handoff_histogram[handoff["handoff_type"]] += 1
        lift_evaluations[receipt_id] = {
            "receipt_id": receipt_id,
            "target_boundary_sha256": key,
            "target_in_lower_section": True,
            "target_section_context_id": str(canonical["context_id"]),
            "exact_ancestry_update": record["exact"]["ancestry_update"],
            "typed_handoff": handoff,
        }

    context_rows = []
    successful_channel_count = 0
    failed_channel_count = 0
    hostile_source_ids = []
    good_histogram: Counter[int] = Counter()
    for context in construction["menus"]["contexts"]:
        channels = []
        for channel in context["channels"]:
            success_ids = [
                str(receipt_id)
                for receipt_id in channel["exact_lift_ids"]
                if str(receipt_id) in successful_receipt_ids
            ]
            failure_ids = [
                str(receipt_id)
                for receipt_id in channel["exact_lift_ids"]
                if str(receipt_id) in failed_receipt_ids
            ]
            if success_ids:
                successful_channel_count += 1
            else:
                failed_channel_count += 1
            channels.append(
                {
                    "channel_id": str(channel["channel_id"]),
                    "exact_lift_count": len(channel["exact_lift_ids"]),
                    "has_successful_exact_lift": bool(success_ids),
                    "successful_exact_lift_count": len(success_ids),
                    "successful_exact_lift_ids": sorted(success_ids),
                    "unsuccessful_exact_lift_count": len(failure_ids),
                    "unsuccessful_exact_lift_ids": sorted(failure_ids),
                }
            )
        good_count = sum(
            bool(channel["has_successful_exact_lift"]) for channel in channels
        )
        source_id = str(context["source_context_id"])
        if not good_count:
            hostile_source_ids.append(source_id)
        good_histogram[good_count] += 1
        context_rows.append(
            {
                "source_context_id": source_id,
                "menu_size": int(context["menu_size"]),
                "successful_channel_count": good_count,
                "failed_channel_count": int(context["menu_size"]) - good_count,
                "channels": channels,
            }
        )

    all_sources_good = not hostile_source_ids
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
            "construction_payload_sha256": candidate[
                "construction_payload_sha256"
            ],
            "lower_section_name": lower_section_path.name,
            "lower_section_sha256": _sha256(lower_section_path),
            "lower_section_content_sha256": _load(lower_section_path)[
                "content_sha256"
            ],
        },
        "scope": {
            "ambient_n": 7,
            "source_rank": 5,
            "target_rank": 4,
            "source_context_count": construction["source_section"][
                "context_count"
            ],
            "winner_selected": False,
            "menu_or_lift_rebuilt": False,
        },
        "definition": (
            "Good_5(C,m) iff an exact lift in the frozen channel admits a "
            "verified typed handoff to Sec_4,cand2^(7)"
        ),
        "evaluation": {
            "all_sources_have_good_channel": all_sources_good,
            "successful_source_count": int(
                construction["source_section"]["context_count"]
            )
            - len(hostile_source_ids),
            "hostile_source_count": len(hostile_source_ids),
            "hostile_source_context_ids": sorted(hostile_source_ids),
            "channel_count": int(construction["menus"]["channel_count"]),
            "successful_channel_count": successful_channel_count,
            "failed_channel_count": failed_channel_count,
            "exact_lift_count": int(
                construction["exact_lifts"]["receipt_count"]
            ),
            "successful_exact_lift_count": len(successful_receipt_ids),
            "unsuccessful_exact_lift_count": len(failed_receipt_ids),
            "good_channel_count_histogram": {
                str(count): sources
                for count, sources in sorted(good_histogram.items())
            },
            "handoff_type_histogram": dict(sorted(handoff_histogram.items())),
            "contexts": context_rows,
            "lift_evaluations": [
                lift_evaluations[receipt_id]
                for receipt_id in sorted(lift_evaluations)
            ],
        },
        "certified_source_section": {
            "name": "Sec_5,cand2^(7)",
            "return_authority_status": (
                "GRANTED_BY_FIXED_SCOPE_GOOD5_EVALUATION"
                if all_sources_good
                else "NOT_GRANTED_HOSTILE_SOURCES_PRESENT"
            ),
            "context_count": len(source_contexts) if all_sources_good else 0,
            "contexts": source_contexts if all_sources_good else [],
        },
        "typed_handoff_audit": {
            "lower_section": "Sec_4,cand2^(7)",
            "literal_context_identity_required": False,
            "verified_handoff_types": sorted(handoff_histogram),
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
            "proved_if_all_sources_good": (
                "every source in the frozen 48-context rank-five candidate has "
                "a future-free channel with an exact typed lift to "
                "Sec_4,cand2^(7)"
            ),
            "not_claimed": [
                "every menu channel succeeds",
                "every exact lift succeeds",
                "the source section is maximal or canonical",
                "the full inherited 15120-context scope is covered",
                "an all-rank return theorem",
            ],
        },
    }
    if successful_receipt_ids | failed_receipt_ids != set(by_id):
        raise AssertionError("Good_5 did not partition exact lifts")
    if successful_channel_count + failed_channel_count != int(
        construction["menus"]["channel_count"]
    ):
        raise AssertionError("Good_5 did not partition channels")
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
    closure = []
    for relative in SOURCE_CLOSURE:
        path = HERE / relative
        closure.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "sha256": _sha256(path),
            }
        )
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "POST_FREEZE_TYPED_HANDOFF_EVALUATION",
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
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument(
        "--lower-section",
        type=Path,
        default=DEFAULT_LOWER_SECTION,
    )
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
                "all_sources_have_good_channel": evaluation[
                    "all_sources_have_good_channel"
                ],
                "successful_sources": evaluation["successful_source_count"],
                "hostile_sources": evaluation["hostile_source_count"],
                "successful_channels": evaluation["successful_channel_count"],
                "failed_channels": evaluation["failed_channel_count"],
                "successful_exact_lifts": evaluation[
                    "successful_exact_lift_count"
                ],
                "unsuccessful_exact_lifts": evaluation[
                    "unsuccessful_exact_lift_count"
                ],
                "handoff_types": evaluation["handoff_type_histogram"],
                "source_return_authority": payload[
                    "certified_source_section"
                ]["return_authority_status"],
                "winner_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
