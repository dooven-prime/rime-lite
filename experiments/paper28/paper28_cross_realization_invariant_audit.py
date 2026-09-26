#!/usr/bin/env python3
"""Compare the two frozen P28.5 composed section-return realizations."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SCHEMA = "paper28-cross-realization-invariant-audit-v1"
RECEIPT_SCHEMA = "paper28-cross-realization-invariant-audit-receipt-v1"
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_FIRST_RANK4 = RESULTS / "paper28_section_return_menu_audit_v1.json.gz"
DEFAULT_FIRST_RANK5_CANDIDATE = (
    RESULTS / "paper28_rank5_section_candidate_v1.json.gz"
)
DEFAULT_FIRST_RANK5_EVALUATION = (
    RESULTS / "paper28_rank5_section_return_evaluation_v1.json.gz"
)
DEFAULT_SECOND_SELECTION = (
    RESULTS / "paper28_second_rank5_return_candidate_selection_v1.json.gz"
)
DEFAULT_SECOND_RANK4_CANDIDATE = (
    RESULTS / "paper28_second_rank4_section_candidate_v1.json.gz"
)
DEFAULT_SECOND_RANK4_EVALUATION = (
    RESULTS / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_SECOND_RANK5_CANDIDATE = (
    RESULTS / "paper28_second_rank5_section_candidate_v1.json.gz"
)
DEFAULT_SECOND_RANK5_EVALUATION = (
    RESULTS / "paper28_second_rank5_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_cross_realization_invariant_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_cross_realization_invariant_audit.py",
    "validation/validate_paper28_cross_realization_invariant_audit.py",
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


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="ascii",
        newline="\n",
    )


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}.receipt.json")


def _words(values: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        list(word)
        for word in sorted({tuple(int(value) for value in word) for word in values})
    ]


def _successful_ids_first(evaluation: Mapping[str, Any]) -> list[str]:
    return sorted(
        str(lift["receipt_id"])
        for source in evaluation["sources"]
        for channel in source["channels"]
        for lift in channel["successful_exact_lifts"]
    )


def _successful_ids_second(evaluation: Mapping[str, Any]) -> list[str]:
    return sorted(
        str(row["receipt_id"])
        for row in evaluation["evaluation"]["lift_evaluations"]
        if row["target_in_lower_section"]
    )


def _handoff_mode_first(evaluation: Mapping[str, Any]) -> dict[str, int]:
    histogram: Counter[str] = Counter()
    for source in evaluation["sources"]:
        for channel in source["channels"]:
            for lift in channel["successful_exact_lifts"]:
                handoff = lift["exact_role_handoff"]
                identity_map = all(
                    int(row["canonical_atom"]) == int(row["actual_atom"])
                    for row in handoff["canonical_to_actual_atom_bijection"]
                )
                identity_id = (
                    str(handoff["canonical_source_context_id"])
                    == str(handoff["actual_target_context_id"])
                )
                histogram[
                    "IDENTITY" if identity_map and identity_id else "ATOM_BIJECTION"
                ] += 1
    return dict(sorted(histogram.items()))


def _rank5_anatomy(
    candidate: Mapping[str, Any],
    successful_ids: Sequence[str],
    *,
    first_realization: bool,
) -> dict[str, Any]:
    construction = candidate["construction"]
    records = {
        str(record["receipt_id"]): record
        for record in construction["exact_lifts"]["receipts"]
    }
    selected = [records[receipt_id] for receipt_id in successful_ids]
    if len(selected) != len(successful_ids):
        raise AssertionError("successful receipt id missing from candidate")
    source_rows = construction["source_section"]["contexts"]
    if first_realization:
        upstream_words = [
            row["sigma6_selected_word"] for row in source_rows
        ]
    else:
        upstream_words = [row["sigma6"]["selected_word"] for row in source_rows]
    operation_kinds = sorted(
        {
            str(kind)
            for row in construction["exact_lifts"]["factorizations"]
            for kind in row["operation_kind_path"]
        }
    )
    return {
        "source_partition_set": sorted(
            {
                tuple(int(value) for value in row["skeleton"]["source_partition"])
                for row in selected
            }
        ),
        "target_partition_set": sorted(
            {
                tuple(int(value) for value in row["skeleton"]["target_partition"])
                for row in selected
            }
        ),
        "upstream_sigma6_words": _words(upstream_words),
        "successful_rank5_words": _words(
            row["exact"]["words"][0] for row in selected
        ),
        "successful_fusion_parent_masses": sorted(
            {
                tuple(
                    int(value)
                    for value in row["skeleton"]["fusion_chain"][0][
                        "parent_masses"
                    ]
                )
                for row in selected
            }
        ),
        "successful_lengths": sorted(
            {
                tuple(int(value) for value in row["observables"]["corridor_lengths"])
                for row in selected
            }
        ),
        "successful_total_surpluses": sorted(
            {int(row["observables"]["total_surplus"]) for row in selected}
        ),
        "incoming_distinguished_participation": sorted(
            {str(row["skeleton"]["ancestry_update_type"]) for row in selected}
        ),
        "generator_vocabulary": operation_kinds,
        "internal_boundaries_exported_as_checkpoints": int(
            construction["checkpoint_type_audit"][
                "internal_only_exported_as_checkpoint"
            ]
        ),
        "construction_evaluation_status": str(
            candidate["scope"]["evaluation_status"]
        ),
    }


def _input_row(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload.get("content_sha256"),
    }


def build_payload(paths: Mapping[str, Path]) -> dict[str, Any]:
    data = {name: _load(path) for name, path in paths.items()}
    expected_schemas = {
        "first_rank4": "paper28-section-return-menu-audit-v1",
        "first_rank5_candidate": "paper28-rank5-section-return-candidate-v1",
        "first_rank5_evaluation": "paper28-rank5-section-return-evaluation-v1",
        "second_selection": "paper28-second-rank5-return-candidate-selection-v1",
        "second_rank4_candidate": "paper28-second-rank4-section-candidate-v1",
        "second_rank4_evaluation": (
            "paper28-second-rank4-section-return-evaluation-v1"
        ),
        "second_rank5_candidate": "paper28-second-rank5-section-candidate-v1",
        "second_rank5_evaluation": (
            "paper28-second-rank5-section-return-evaluation-v1"
        ),
    }
    for name, schema in expected_schemas.items():
        if data[name].get("schema") != schema:
            raise AssertionError(f"unexpected schema for {name}")

    first_rank5_good = _successful_ids_first(data["first_rank5_evaluation"])
    second_rank5_good = _successful_ids_second(data["second_rank5_evaluation"])
    first_anatomy = _rank5_anatomy(
        data["first_rank5_candidate"],
        first_rank5_good,
        first_realization=True,
    )
    second_anatomy = _rank5_anatomy(
        data["second_rank5_candidate"],
        second_rank5_good,
        first_realization=False,
    )

    first_rank4_menu = data["first_rank4"]["future_free_menu"]
    first_rank4_success = data["first_rank4"]["success_certification"]
    second_rank4_candidate = data["second_rank4_candidate"]["construction"]
    second_rank4_success = data["second_rank4_evaluation"]["evaluation"]
    first_rank5_summary = data["first_rank5_evaluation"]["summary"]
    second_rank5_summary = data["second_rank5_evaluation"]["evaluation"]
    first_handoff = _handoff_mode_first(data["first_rank5_evaluation"])
    second_handoff = dict(
        data["second_rank5_evaluation"]["evaluation"]["handoff_type_histogram"]
    )

    first = {
        "name": "extremal_35_context_chain",
        "rank4": {
            "source_count": int(first_rank4_menu["context_count"]),
            "menu_max": int(first_rank4_menu["max_menu_size"]),
            "channel_count": int(first_rank4_menu["channel_count"]),
            "successful_channel_count": int(
                first_rank4_success["successful_channel_count"]
            ),
            "failed_channel_count": int(first_rank4_success["failed_channel_count"]),
            "successful_exact_lift_count": int(
                first_rank4_success["successful_exact_lift_count"]
            ),
            "failed_exact_lift_count": int(
                first_rank4_success["failed_exact_lift_count"]
            ),
        },
        "rank5": {
            **first_anatomy,
            "source_count": int(first_rank5_summary["source_context_count"]),
            "channel_count": int(first_rank5_summary["channel_count"]),
            "successful_channel_count": int(
                first_rank5_summary["successful_channel_count"]
            ),
            "failed_channel_count": int(
                first_rank5_summary["failed_channel_count"]
            ),
            "successful_exact_lift_count": int(
                first_rank5_summary["successful_exact_lift_count"]
            ),
            "failed_exact_lift_count": int(
                first_rank5_summary["unsuccessful_exact_lift_count"]
            ),
            "all_sources_have_good_channel": bool(
                first_rank5_summary["all_sources_have_good_channel"]
            ),
            "handoff_type_histogram": first_handoff,
            "winner_selected": bool(first_rank5_summary["winner_selected"]),
        },
    }
    second = {
        "name": "second_48_context_chain",
        "rank4": {
            "source_count": int(
                second_rank4_candidate["source_context_count"]
                if "source_context_count" in second_rank4_candidate
                else second_rank4_candidate["menus"]["context_count"]
            ),
            "menu_max": int(second_rank4_candidate["menus"]["max_menu_size"]),
            "channel_count": int(second_rank4_success["channel_count"]),
            "successful_channel_count": int(
                second_rank4_success["successful_channel_count"]
            ),
            "failed_channel_count": int(
                second_rank4_success["failed_channel_count"]
            ),
            "successful_exact_lift_count": int(
                second_rank4_success["successful_exact_lift_count"]
            ),
            "failed_exact_lift_count": int(
                second_rank4_success["unsuccessful_exact_lift_count"]
            ),
        },
        "rank5": {
            **second_anatomy,
            "source_count": int(second_rank5_summary["successful_source_count"]),
            "channel_count": int(second_rank5_summary["channel_count"]),
            "successful_channel_count": int(
                second_rank5_summary["successful_channel_count"]
            ),
            "failed_channel_count": int(
                second_rank5_summary["failed_channel_count"]
            ),
            "successful_exact_lift_count": int(
                second_rank5_summary["successful_exact_lift_count"]
            ),
            "failed_exact_lift_count": int(
                second_rank5_summary["unsuccessful_exact_lift_count"]
            ),
            "all_sources_have_good_channel": bool(
                second_rank5_summary["all_sources_have_good_channel"]
            ),
            "handoff_type_histogram": second_handoff,
            "winner_selected": bool(data["second_rank5_evaluation"]["scope"][
                "winner_selected"
            ]),
        },
    }

    if first["rank4"]["menu_max"] >= second["rank4"]["menu_max"]:
        raise AssertionError("second realization did not falsify menu <= 8")
    common_generator_vocabulary = (
        first["rank5"]["generator_vocabulary"]
        == second["rank5"]["generator_vocabulary"]
        == ["FUSION", "RETURN", "TRANSPORT"]
    )
    common_fusion = (
        first["rank5"]["successful_fusion_parent_masses"]
        == second["rank5"]["successful_fusion_parent_masses"]
        == [(1, 1)]
    )
    common_length_surplus = (
        first["rank5"]["successful_lengths"]
        == second["rank5"]["successful_lengths"]
        == [(3,)]
        and first["rank5"]["successful_total_surpluses"]
        == second["rank5"]["successful_total_surpluses"]
        == [0]
    )
    common_unused_incoming = (
        first["rank5"]["incoming_distinguished_participation"]
        == second["rank5"]["incoming_distinguished_participation"]
        == ["NONE"]
    )
    f1_f5 = {
        "future_free_construction": (
            first["rank5"]["construction_evaluation_status"] == "NOT_RUN"
            and second["rank5"]["construction_evaluation_status"] == "NOT_RUN"
        ),
        "exact_lift_fibers_retained": (
            first["rank5"]["successful_exact_lift_count"]
            + first["rank5"]["failed_exact_lift_count"]
            == 214
            and second["rank5"]["successful_exact_lift_count"]
            + second["rank5"]["failed_exact_lift_count"]
            == 195
        ),
        "internal_boundaries_excluded": (
            first["rank5"]["internal_boundaries_exported_as_checkpoints"] == 0
            and second["rank5"]["internal_boundaries_exported_as_checkpoints"]
            == 0
        ),
        "existential_return": (
            first["rank5"]["all_sources_have_good_channel"]
            and second["rank5"]["all_sources_have_good_channel"]
        ),
        "winner_selection_absent": (
            not first["rank5"]["winner_selected"]
            and not second["rank5"]["winner_selected"]
        ),
        "exact_compatible_accounting_present": all(
            "accounting" in record
            for name in ("first_rank5_candidate", "second_rank5_candidate")
            for record in data[name]["construction"]["exact_lifts"]["receipts"]
        ),
    }
    if not all(f1_f5.values()):
        raise AssertionError(f"cross-realization contract drift: {f1_f5!r}")

    matrix = [
        {
            "surface": "rank5_source_partition",
            "first": first["rank5"]["source_partition_set"],
            "second": second["rank5"]["source_partition_set"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "rank4_section_partition",
            "first": first["rank5"]["target_partition_set"],
            "second": second["rank5"]["target_partition_set"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "upstream_Sigma6_word",
            "first": first["rank5"]["upstream_sigma6_words"],
            "second": second["rank5"]["upstream_sigma6_words"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "successful_rank5_word",
            "first": first["rank5"]["successful_rank5_words"],
            "second": second["rank5"]["successful_rank5_words"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "handoff_mode",
            "first": first_handoff,
            "second": second_handoff,
            "status": "IMPLEMENTATION_DEPENDENT",
        },
        {
            "surface": "rank4_menu_max",
            "first": first["rank4"]["menu_max"],
            "second": second["rank4"]["menu_max"],
            "status": "NO_STABLE_NUMERICAL_BOUND",
        },
        {
            "surface": "rank4_all_channels_good",
            "first": first["rank4"]["failed_channel_count"] == 0,
            "second": second["rank4"]["failed_channel_count"] == 0,
            "status": "NOT_STRUCTURAL",
        },
        {
            "surface": "rank5_existential_return",
            "first": first["rank5"]["all_sources_have_good_channel"],
            "second": second["rank5"]["all_sources_have_good_channel"],
            "status": "SURVIVES_BOTH",
        },
        {
            "surface": "generator_vocabulary",
            "first": first["rank5"]["generator_vocabulary"],
            "second": second["rank5"]["generator_vocabulary"],
            "status": "SURVIVES_BOTH",
        },
        {
            "surface": "rank5_fusion_parent_masses",
            "first": first["rank5"]["successful_fusion_parent_masses"],
            "second": second["rank5"]["successful_fusion_parent_masses"],
            "status": "COMMON_UNTESTED_ACCIDENTAL",
        },
        {
            "surface": "rank5_length_surplus",
            "first": {
                "lengths": first["rank5"]["successful_lengths"],
                "surpluses": first["rank5"]["successful_total_surpluses"],
            },
            "second": {
                "lengths": second["rank5"]["successful_lengths"],
                "surpluses": second["rank5"]["successful_total_surpluses"],
            },
            "status": "COMMON_UNTESTED_ACCIDENTAL",
        },
        {
            "surface": "incoming_distinguished_consumed",
            "first": first["rank5"]["incoming_distinguished_participation"],
            "second": second["rank5"]["incoming_distinguished_participation"],
            "status": "COMMON_STRUCTURAL_CANDIDATE_NOT_PROVED",
        },
        {
            "surface": "F1_F5_discipline",
            "first": True,
            "second": True,
            "status": "SURVIVES_BOTH",
        },
    ]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "realization_count": 2,
            "new_oracle_evaluation": False,
            "third_candidate_selected": False,
        },
        "inputs": {
            name: _input_row(paths[name], data[name])
            for name in sorted(paths)
        },
        "realizations": {
            "first": first,
            "second": second,
        },
        "invariant_matrix": matrix,
        "contract_audit": f1_f5,
        "derived_conclusions": {
            "menu_size_le_8_survives": False,
            "generator_vocabulary_survives": common_generator_vocabulary,
            "fusion_1_plus_1_common_but_unproved": common_fusion,
            "length_3_surplus_0_common_but_unproved": common_length_surplus,
            "incoming_distinguished_unused_common_but_unproved": (
                common_unused_incoming
            ),
            "nonidentity_handoff_is_universal": False,
            "typed_observable_preservation_required": True,
            "add_F6_handoff_contract": False,
        },
        "F3_refinement": {
            "statement": (
                "exact-lift soundness certifies a target view preserving every "
                "typed observable used by the lower theorem"
            ),
            "allowed_realizations": ["IDENTITY", "ATOM_BIJECTION"],
            "preserved_observables": [
                "rooted action",
                "occupied coordinates",
                "packet masses and roles",
                "distinguished ancestry",
                "normalization semantics",
                "accounting semantics",
            ],
            "schema_change": "NONE_KEEP_WITHIN_F3",
        },
        "next_hostile_selection": {
            "status": "PREREGISTERED_NOT_RUN",
            "ambient_n": 7,
            "carrier": "future-free 562-cell space",
            "hard_constraint": "fusion_parent_type != 1+1",
            "preferred_type": "1+2",
            "secondary_objective": (
                "minimize distance from the closed realizations on fresh "
                "participation, length, surplus, kernel mass, and "
                "F4-relative offsets"
            ),
            "evaluation_forbidden_during_selection": [
                "Good_4",
                "Good_5",
                "lower-section success",
                "winning or Bellman labels",
            ],
        },
        "claim_boundary": {
            "proved": (
                "the displayed comparison and F3 decision on the two frozen "
                "fixed-n=7 composed chains"
            ),
            "not_claimed": [
                "the common 1+1 length-three zero-surplus anatomy is structural",
                "a rank-controlled or uniform menu bound",
                "a third return realization",
                "an all-rank return theorem",
            ],
        },
    }
    # Normalize tuples produced by set-based audits to their canonical JSON
    # representation before hashing and replay comparison.
    payload = json.loads(
        json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            default=list,
        )
    )
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    paths: Mapping[str, Path],
    output: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "CROSS_ARTIFACT_INVARIANT_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            name: {
                "name": path.name,
                "sha256": _sha256(path),
            }
            for name, path in sorted(paths.items())
        },
        "source_closure": [
            {
                "path": (HERE / relative).relative_to(repo_root).as_posix(),
                "sha256": _sha256(HERE / relative),
            }
            for relative in SOURCE_CLOSURE
        ],
    }


def _paths_from_args(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "first_rank4": args.first_rank4,
        "first_rank5_candidate": args.first_rank5_candidate,
        "first_rank5_evaluation": args.first_rank5_evaluation,
        "second_selection": args.second_selection,
        "second_rank4_candidate": args.second_rank4_candidate,
        "second_rank4_evaluation": args.second_rank4_evaluation,
        "second_rank5_candidate": args.second_rank5_candidate,
        "second_rank5_evaluation": args.second_rank5_evaluation,
    }


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--first-rank4", type=Path, default=DEFAULT_FIRST_RANK4)
    parser.add_argument(
        "--first-rank5-candidate",
        type=Path,
        default=DEFAULT_FIRST_RANK5_CANDIDATE,
    )
    parser.add_argument(
        "--first-rank5-evaluation",
        type=Path,
        default=DEFAULT_FIRST_RANK5_EVALUATION,
    )
    parser.add_argument(
        "--second-selection",
        type=Path,
        default=DEFAULT_SECOND_SELECTION,
    )
    parser.add_argument(
        "--second-rank4-candidate",
        type=Path,
        default=DEFAULT_SECOND_RANK4_CANDIDATE,
    )
    parser.add_argument(
        "--second-rank4-evaluation",
        type=Path,
        default=DEFAULT_SECOND_RANK4_EVALUATION,
    )
    parser.add_argument(
        "--second-rank5-candidate",
        type=Path,
        default=DEFAULT_SECOND_RANK5_CANDIDATE,
    )
    parser.add_argument(
        "--second-rank5-evaluation",
        type=Path,
        default=DEFAULT_SECOND_RANK5_EVALUATION,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_input_arguments(parser)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    paths = _paths_from_args(args)
    payload = build_payload(paths)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write(
        receipt_path,
        build_receipt(paths=paths, output=args.out, payload=payload),
    )
    conclusions = payload["derived_conclusions"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "menu_size_le_8_survives": conclusions[
                    "menu_size_le_8_survives"
                ],
                "generator_vocabulary_survives": conclusions[
                    "generator_vocabulary_survives"
                ],
                "nonidentity_handoff_is_universal": conclusions[
                    "nonidentity_handoff_is_universal"
                ],
                "add_F6_handoff_contract": conclusions[
                    "add_F6_handoff_contract"
                ],
                "third_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
