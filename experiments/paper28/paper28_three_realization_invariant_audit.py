#!/usr/bin/env python3
"""Audit invariants across the three frozen P28.5 section-return chains."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SCHEMA = "paper28-three-realization-invariant-audit-v1"
RECEIPT_SCHEMA = "paper28-three-realization-invariant-audit-receipt-v1"
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_TWO_CHAIN_AUDIT = RESULTS / "paper28_cross_realization_invariant_audit_v1.json"
DEFAULT_THIRD_SELECTION = RESULTS / "paper28_third_rank5_return_candidate_selection_v1.json.gz"
DEFAULT_THIRD_OVERLAP = RESULTS / "paper28_third_rank4_section_overlap_audit_v1.json"
DEFAULT_THIRD_RANK4_CANDIDATE = RESULTS / "paper28_third_rank4_section_candidate_v1.json.gz"
DEFAULT_THIRD_RANK4_EVALUATION = RESULTS / "paper28_third_rank4_section_return_evaluation_v1.json.gz"
DEFAULT_THIRD_RANK5_CANDIDATE = RESULTS / "paper28_third_rank5_section_candidate_v1.json.gz"
DEFAULT_THIRD_RANK5_EVALUATION = RESULTS / "paper28_third_rank5_section_return_evaluation_v1.json.gz"
DEFAULT_OUTPUT = RESULTS / "paper28_three_realization_invariant_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_three_realization_invariant_audit.py",
    "validation/validate_paper28_three_realization_invariant_audit.py",
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


def _input_row(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload.get("content_sha256"),
    }


def _successful_ids(evaluation: Mapping[str, Any]) -> list[str]:
    return sorted(
        str(row["receipt_id"])
        for row in evaluation["evaluation"]["lift_evaluations"]
        if row["target_in_lower_section"]
    )


def _words(values: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        list(word)
        for word in sorted({tuple(int(value) for value in word) for word in values})
    ]


def _third_rank5_anatomy(
    candidate: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> dict[str, Any]:
    successful_ids = _successful_ids(evaluation)
    construction = candidate["construction"]
    records = {
        str(record["receipt_id"]): record
        for record in construction["exact_lifts"]["receipts"]
    }
    selected = [records[receipt_id] for receipt_id in successful_ids]
    if len(selected) != len(successful_ids):
        raise AssertionError("third successful receipt id missing from candidate")
    source_rows = construction["source_section"]["contexts"]
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
        "upstream_sigma6_words": _words(
            row["sigma6"]["selected_word"] for row in source_rows
        ),
        "successful_rank5_words": _words(
            row["exact"]["words"][0] for row in selected
        ),
        "successful_fusion_parent_masses": sorted(
            {
                tuple(
                    int(value)
                    for value in row["skeleton"]["fusion_chain"][0]["parent_masses"]
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
        "generator_vocabulary": sorted(
            {
                str(kind)
                for row in construction["exact_lifts"]["factorizations"]
                for kind in row["operation_kind_path"]
            }
        ),
        "source_count": int(evaluation["scope"]["source_context_count"]),
        "channel_count": int(evaluation["evaluation"]["channel_count"]),
        "successful_channel_count": int(
            evaluation["evaluation"]["successful_channel_count"]
        ),
        "failed_channel_count": int(evaluation["evaluation"]["failed_channel_count"]),
        "successful_exact_lift_count": int(
            evaluation["evaluation"]["successful_exact_lift_count"]
        ),
        "failed_exact_lift_count": int(
            evaluation["evaluation"]["unsuccessful_exact_lift_count"]
        ),
        "all_sources_have_good_channel": bool(
            evaluation["evaluation"]["all_sources_have_good_channel"]
        ),
        "handoff_type_histogram": dict(
            evaluation["evaluation"]["handoff_type_histogram"]
        ),
        "winner_selected": bool(evaluation["scope"]["winner_selected"]),
        "construction_evaluation_status": str(candidate["scope"]["evaluation_status"]),
        "internal_boundaries_exported_as_checkpoints": int(
            construction["checkpoint_type_audit"][
                "internal_only_exported_as_checkpoint"
            ]
        ),
    }


def _paths_from_args(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "two_chain_audit": args.two_chain_audit,
        "third_selection": args.third_selection,
        "third_overlap": args.third_overlap,
        "third_rank4_candidate": args.third_rank4_candidate,
        "third_rank4_evaluation": args.third_rank4_evaluation,
        "third_rank5_candidate": args.third_rank5_candidate,
        "third_rank5_evaluation": args.third_rank5_evaluation,
    }


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--two-chain-audit", type=Path, default=DEFAULT_TWO_CHAIN_AUDIT)
    parser.add_argument("--third-selection", type=Path, default=DEFAULT_THIRD_SELECTION)
    parser.add_argument("--third-overlap", type=Path, default=DEFAULT_THIRD_OVERLAP)
    parser.add_argument(
        "--third-rank4-candidate", type=Path, default=DEFAULT_THIRD_RANK4_CANDIDATE
    )
    parser.add_argument(
        "--third-rank4-evaluation", type=Path, default=DEFAULT_THIRD_RANK4_EVALUATION
    )
    parser.add_argument(
        "--third-rank5-candidate", type=Path, default=DEFAULT_THIRD_RANK5_CANDIDATE
    )
    parser.add_argument(
        "--third-rank5-evaluation", type=Path, default=DEFAULT_THIRD_RANK5_EVALUATION
    )


def build_payload(paths: Mapping[str, Path]) -> dict[str, Any]:
    data = {name: _load(path) for name, path in paths.items()}
    expected_schemas = {
        "two_chain_audit": "paper28-cross-realization-invariant-audit-v1",
        "third_selection": "paper28-third-rank5-return-candidate-selection-v1",
        "third_overlap": "paper28-third-rank4-section-overlap-audit-v1",
        "third_rank4_candidate": "paper28-third-rank4-section-candidate-v1",
        "third_rank4_evaluation": "paper28-third-rank4-section-return-evaluation-v1",
        "third_rank5_candidate": "paper28-third-rank5-section-candidate-v1",
        "third_rank5_evaluation": "paper28-third-rank5-section-return-evaluation-v1",
    }
    for name, schema in expected_schemas.items():
        if data[name].get("schema") != schema:
            raise AssertionError(f"unexpected schema for {name}")

    prior = data["two_chain_audit"]
    if prior["scope"]["realization_count"] != 2:
        raise AssertionError("P28.5g no longer supplies exactly two realizations")
    if data["third_overlap"]["overlap"]["intersection_count"] != 0:
        raise AssertionError("third lower section is not typed-disjoint from the second")

    third_rank5 = _third_rank5_anatomy(
        data["third_rank5_candidate"], data["third_rank5_evaluation"]
    )
    third_rank4_construction = data["third_rank4_candidate"]["construction"]
    third_rank4_evaluation = data["third_rank4_evaluation"]["evaluation"]
    third = {
        "name": "third_36_context_chain",
        "rank4": {
            "source_count": int(third_rank4_evaluation["successful_source_count"]),
            "menu_max": int(third_rank4_construction["menus"]["max_menu_size"]),
            "channel_count": int(third_rank4_evaluation["channel_count"]),
            "successful_channel_count": int(
                third_rank4_evaluation["successful_channel_count"]
            ),
            "failed_channel_count": int(third_rank4_evaluation["failed_channel_count"]),
            "successful_exact_lift_count": int(
                third_rank4_evaluation["successful_exact_lift_count"]
            ),
            "failed_exact_lift_count": int(
                third_rank4_evaluation["unsuccessful_exact_lift_count"]
            ),
            "typed_overlap_with_second": 0,
        },
        "rank5": third_rank5,
    }

    first = prior["realizations"]["first"]
    second = prior["realizations"]["second"]
    realizations = [first, second, third]
    selection = data["third_selection"]
    references = selection["candidate"]["closed_reference_signatures"]
    selected_signature = selection["candidate"]["selected_signature"]
    kernel_mass_rows = [
        references[0]["binary_kernel_mass_multiset"],
        references[1]["binary_kernel_mass_multiset"],
        selected_signature["binary_kernel_mass_multiset"],
    ]

    common_vocabulary = all(
        row["rank5"]["generator_vocabulary"] == ["FUSION", "RETURN", "TRANSPORT"]
        for row in realizations
    )
    all_length_three = all(
        {
            tuple(int(value) for value in length)
            for length in row["rank5"]["successful_lengths"]
        }
        == {(3,)}
        for row in realizations
    )
    all_incoming_unused = all(
        row["rank5"]["incoming_distinguished_participation"] == ["NONE"]
        for row in realizations
    )
    f1_f5 = {
        "future_free_construction": (
            bool(prior["contract_audit"]["future_free_construction"])
            and data["third_rank4_candidate"]["scope"]["evaluation_status"] == "NOT_RUN"
            and third_rank5["construction_evaluation_status"] == "NOT_RUN"
        ),
        "exact_lift_fibers_retained": (
            third["rank4"]["successful_exact_lift_count"]
            + third["rank4"]["failed_exact_lift_count"]
            == int(third_rank4_evaluation["exact_lift_count"])
            and third_rank5["successful_exact_lift_count"]
            + third_rank5["failed_exact_lift_count"]
            == int(data["third_rank5_evaluation"]["evaluation"]["exact_lift_count"])
        ),
        "internal_boundaries_excluded": (
            third_rank4_construction["checkpoint_type_audit"][
                "internal_only_exported_as_checkpoint"
            ]
            == 0
            and third_rank5["internal_boundaries_exported_as_checkpoints"] == 0
        ),
        "existential_return": all(
            row["rank5"]["all_sources_have_good_channel"] for row in realizations
        )
        and bool(third_rank4_evaluation["all_sources_have_good_channel"]),
        "winner_selection_absent": (
            all(not row["rank5"]["winner_selected"] for row in realizations)
            and not data["third_rank4_evaluation"]["scope"]["winner_selected"]
        ),
        "exact_compatible_accounting_present": all(
            "accounting" in record
            for record in data["third_rank5_candidate"]["construction"]["exact_lifts"]["receipts"]
        ),
        "typed_lower_observables_preserved": all(
            bool(data["third_rank5_evaluation"]["typed_handoff_audit"][field])
            for field in (
                "rooted_action_preserved",
                "packet_masses_preserved",
                "distinguished_packet_preserved",
            )
        ),
    }
    if not all(f1_f5.values()):
        raise AssertionError(f"three-realization contract drift: {f1_f5!r}")

    matrix = [
        {
            "surface": "rank5_source_partition",
            "first": first["rank5"]["source_partition_set"],
            "second": second["rank5"]["source_partition_set"],
            "third": third_rank5["source_partition_set"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "rank4_section_partition",
            "first": first["rank5"]["target_partition_set"],
            "second": second["rank5"]["target_partition_set"],
            "third": third_rank5["target_partition_set"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "successful_rank5_word",
            "first": first["rank5"]["successful_rank5_words"],
            "second": second["rank5"]["successful_rank5_words"],
            "third": third_rank5["successful_rank5_words"],
            "status": "ACCIDENTAL",
        },
        {
            "surface": "handoff_mode",
            "first": first["rank5"]["handoff_type_histogram"],
            "second": second["rank5"]["handoff_type_histogram"],
            "third": third_rank5["handoff_type_histogram"],
            "status": "IMPLEMENTATION_DEPENDENT",
        },
        {
            "surface": "rank4_menu_max",
            "first": first["rank4"]["menu_max"],
            "second": second["rank4"]["menu_max"],
            "third": third["rank4"]["menu_max"],
            "status": "NO_STABLE_NUMERICAL_BOUND",
        },
        {
            "surface": "rank4_all_channels_good",
            "first": first["rank4"]["failed_channel_count"] == 0,
            "second": second["rank4"]["failed_channel_count"] == 0,
            "third": third["rank4"]["failed_channel_count"] == 0,
            "status": "NOT_STRUCTURAL",
        },
        {
            "surface": "rank5_fusion_parent_masses",
            "first": first["rank5"]["successful_fusion_parent_masses"],
            "second": second["rank5"]["successful_fusion_parent_masses"],
            "third": third_rank5["successful_fusion_parent_masses"],
            "status": "ONE_PLUS_ONE_NOT_NECESSARY",
        },
        {
            "surface": "rank5_length",
            "first": first["rank5"]["successful_lengths"],
            "second": second["rank5"]["successful_lengths"],
            "third": third_rank5["successful_lengths"],
            "status": "COMMON_UNTESTED_ACCIDENTAL",
        },
        {
            "surface": "rank5_total_surplus",
            "first": first["rank5"]["successful_total_surpluses"],
            "second": second["rank5"]["successful_total_surpluses"],
            "third": third_rank5["successful_total_surpluses"],
            "status": "ZERO_SURPLUS_NOT_NECESSARY",
        },
        {
            "surface": "binary_kernel_mass_multiset",
            "first": kernel_mass_rows[0],
            "second": kernel_mass_rows[1],
            "third": kernel_mass_rows[2],
            "status": "ZERO_TWO_NOT_NECESSARY",
        },
        {
            "surface": "incoming_distinguished_consumed",
            "first": first["rank5"]["incoming_distinguished_participation"],
            "second": second["rank5"]["incoming_distinguished_participation"],
            "third": third_rank5["incoming_distinguished_participation"],
            "status": "COMMON_STRUCTURAL_CANDIDATE_NOT_PROVED",
        },
        {
            "surface": "generator_vocabulary",
            "first": first["rank5"]["generator_vocabulary"],
            "second": second["rank5"]["generator_vocabulary"],
            "third": third_rank5["generator_vocabulary"],
            "status": "SURVIVES_ALL_THREE",
        },
        {
            "surface": "F1_F5_discipline",
            "first": True,
            "second": True,
            "third": True,
            "status": "SURVIVES_ALL_THREE",
        },
    ]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "realization_count": 3,
            "new_oracle_evaluation": False,
            "fourth_candidate_selected": False,
        },
        "inputs": {
            name: _input_row(paths[name], data[name]) for name in sorted(paths)
        },
        "realizations": {"first": first, "second": second, "third": third},
        "invariant_matrix": matrix,
        "contract_audit": f1_f5,
        "derived_conclusions": {
            "generator_vocabulary_survives_all_three": common_vocabulary,
            "fusion_1_plus_1_is_necessary": False,
            "zero_surplus_is_necessary": False,
            "kernel_mass_0_2_is_necessary": False,
            "length_three_common_but_unproved": all_length_three,
            "incoming_distinguished_unused_common_but_unproved": all_incoming_unused,
            "nonidentity_handoff_is_universal": False,
            "typed_observable_preservation_required": True,
            "add_F6_handoff_contract": False,
            "menu_size_bound_claimed": False,
        },
        "F3_decision": {
            "schema_change": "NONE_KEEP_WITHIN_F3",
            "observed_handoffs": ["IDENTITY", "ATOM_BIJECTION"],
            "statement": (
                "exact-lift soundness certifies preservation of every typed "
                "observable used by the lower theorem"
            ),
        },
        "remaining_hostile_targets": {
            "common_unproved_anatomy": [
                "successful rank-five length equals 3",
                "incoming distinguished packet is not consumed",
            ],
            "fourth_candidate_status": "NOT_SELECTED",
            "selection_rule_status": "NOT_PREREGISTERED_BY_THIS_AUDIT",
        },
        "claim_boundary": {
            "proved": (
                "the displayed comparison and contract audit on the three "
                "frozen fixed-n=7 composed chains"
            ),
            "not_claimed": [
                "length three or distinguished-packet avoidance is structural",
                "T/R/F is all-rank complete",
                "a rank-controlled or uniform menu bound",
                "a fourth return realization",
                "an all-rank return theorem",
            ],
        },
    }
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
    *, paths: Mapping[str, Path], output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "THREE_REALIZATION_CROSS_ARTIFACT_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": {
            name: {"name": path.name, "sha256": _sha256(path)}
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
    _write(receipt_path, build_receipt(paths=paths, output=args.out, payload=payload))
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "realizations": payload["scope"]["realization_count"],
                "one_plus_one_necessary": False,
                "zero_surplus_necessary": False,
                "kernel_mass_0_2_necessary": False,
                "remaining_common_anatomy": payload["remaining_hostile_targets"][
                    "common_unproved_anatomy"
                ],
                "fourth_candidate_selected": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
