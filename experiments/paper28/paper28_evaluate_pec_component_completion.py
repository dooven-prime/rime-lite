#!/usr/bin/env python3
"""Evaluate tagged fixed-scope PEC completion with generic LocalReturn.

The PEC declaration, B1 projectability fibers, and complete cand3/cand4/cand5
rank-four relations are frozen into one tagged completion-input digest before
the exact P_<=3 evaluator is opened.  Every exact lift is evaluated in its own
carrier relation.  No historical Good_4 artifact or rank-five return evaluator
is loaded, and no winner is selected.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from paper28_prepare_second_rank4_section_candidate import _cycle
from section_return_core import CompleteExitOracle, LowRankOracle


SCHEMA = "paper28-pec-component-completion-v1"
RECEIPT_SCHEMA = "paper28-pec-component-completion-receipt-v1"
DECLARATION_SCHEMA = "paper28-third-mechanism-schema-declaration-v1"
PROJECTABILITY_SCHEMA = "paper28-expanded-family-support-separation-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_DECLARATION = (
    RESULTS / "paper28_third_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_PROJECTABILITY = (
    RESULTS / "paper28_expanded_family_support_separation_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_pec_component_completion_v1.json.gz"

N = 7
CARRIER_SPECS = (
    {
        "id": "cand3",
        "tag": 3,
        "section": "Sec_4,cand3^(7)",
        "candidate_schema": "paper28-third-rank4-section-candidate-v1",
        "candidate": RESULTS / "paper28_third_rank4_section_candidate_v1.json.gz",
        "expected_sources": 36,
    },
    {
        "id": "cand4",
        "tag": 4,
        "section": "Sec_4,cand4^(7)",
        "candidate_schema": "paper28-fourth-rank4-section-candidate-v1",
        "candidate": RESULTS / "paper28_fourth_rank4_section_candidate_v1.json.gz",
        "expected_sources": 36,
    },
    {
        "id": "cand5",
        "tag": 5,
        "section": "Sec_4,cand5^(7)",
        "candidate_schema": "paper28-fifth-rank4-section-candidate-v1",
        "candidate": RESULTS / "paper28_fifth_rank4_section_candidate_v1.json.gz",
        "expected_sources": 10,
    },
)

FORBIDDEN_SUCCESS_REFINEMENTS = [
    "incoming distinguished pair must be fused",
    "incoming distinguished pair must be carried",
    "length equals 3 or 5",
    "surplus equals 0 or 2",
    "selected word has a fixed form",
    "fixed source placement or target offset profile",
    "selected winner",
]
FORBIDDEN_INPUTS = [
    "paper28_third_rank4_section_return_evaluation_v1.json.gz",
    "paper28_fourth_rank4_section_return_evaluation_v1.json.gz",
    "paper28_fifth_rank4_section_return_evaluation_v1.json.gz",
    "paper28_third_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fourth_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fifth_rank5_section_return_evaluation_v1.json.gz",
    "Good_4",
    "Good_5",
    "successful_channel",
    "winning",
    "bellman",
]


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(path: Path) -> Path:
    name = path.name
    if name.endswith(".json.gz"):
        name = name[: -len(".json.gz")]
    return path.with_name(f"{name}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="ascii",
    )


def _verify_content_digest(payload: Mapping[str, Any], label: str) -> None:
    candidate = dict(payload)
    stored = str(candidate.pop("content_sha256"))
    if _digest(candidate) != stored:
        raise AssertionError(f"{label} content digest mismatch")


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
    }


def _projectability_by_carrier(
    projectability: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        str(carrier["carrier_id"]): carrier
        for carrier in projectability["projectability"]["carriers"]
    }


def build_payload(
    *,
    declaration_path: Path,
    projectability_path: Path,
    carrier_specs: Sequence[Mapping[str, Any]] = CARRIER_SPECS,
) -> dict[str, Any]:
    declaration = _load(declaration_path)
    projectability = _load(projectability_path)
    if declaration.get("schema") != DECLARATION_SCHEMA:
        raise AssertionError("unexpected PEC declaration schema")
    if projectability.get("schema") != PROJECTABILITY_SCHEMA:
        raise AssertionError("unexpected B1 projectability schema")
    _verify_content_digest(declaration, "PEC declaration")
    _verify_content_digest(projectability, "B1 projectability")

    if declaration["scope"]["success_evaluator_loaded"]:
        raise AssertionError("PEC declaration was not frozen before completion")
    if declaration["declaration"]["expanded_family"] != ["OW", "FPC", "PEC"]:
        raise AssertionError("PEC declaration family drift")
    if declaration["summary"]["PEC_supported_provenances"] != 82:
        raise AssertionError("PEC support domain drift")
    if declaration["input"]["sha256"] != _sha256(projectability_path):
        raise AssertionError("PEC declaration is not bound to this B1 artifact")
    if projectability["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("B1 input loaded a rank-five evaluator")

    candidates: dict[str, dict[str, Any]] = {}
    candidate_inputs: dict[str, dict[str, Any]] = {}
    projectability_carriers = _projectability_by_carrier(projectability)
    expected_carrier_ids = {str(spec["id"]) for spec in carrier_specs}
    if set(projectability_carriers) != expected_carrier_ids:
        raise AssertionError("tagged projectability carrier domain drift")

    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        candidate_path = Path(spec["candidate"])
        candidate = _load(candidate_path)
        if candidate.get("schema") != spec["candidate_schema"]:
            raise AssertionError(f"unexpected {carrier_id} candidate schema")
        _verify_content_digest(candidate, f"{carrier_id} candidate")
        if candidate["scope"]["evaluation_status"] != "NOT_RUN":
            raise AssertionError(f"{carrier_id} relation is not pre-evaluation")
        if candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
            raise AssertionError(f"{carrier_id} candidate contains an evaluator")
        if _digest(candidate["construction"]) != candidate[
            "construction_payload_sha256"
        ]:
            raise AssertionError(f"{carrier_id} construction digest mismatch")

        binding = projectability["projectability_inputs"][carrier_id][
            "rank4_candidate"
        ]
        if binding["sha256"] != _sha256(candidate_path):
            raise AssertionError(f"{carrier_id} adapter file binding drift")
        if binding["content_sha256"] != candidate["content_sha256"]:
            raise AssertionError(f"{carrier_id} adapter content binding drift")
        candidates[carrier_id] = candidate
        candidate_inputs[carrier_id] = _input_record(candidate_path, candidate)

    declaration_support = {
        (
            str(row["carrier_id"]),
            str(row["context_id"]),
            str(row["kappa_4_ISE_id"]),
        ): row
        for row in declaration["declaration"]["support_rows"]
    }
    if len(declaration_support) != 82:
        raise AssertionError("PEC declaration support relation drift")
    if not all(row["supported"] for row in declaration_support.values()):
        raise AssertionError("completion input contains unsupported PEC provenance")

    frozen_carriers = []
    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        candidate = candidates[carrier_id]
        projection = projectability_carriers[carrier_id]
        rows = {
            str(row["context_id"]): row for row in projection["rows"]
        }
        menus = {
            str(row["source_context"]["context_id"]): row
            for row in candidate["construction"]["menus"]["contexts"]
        }
        if set(rows) != set(menus):
            raise AssertionError(f"{carrier_id} support/menu domain drift")
        if len(rows) != int(spec["expected_sources"]):
            raise AssertionError(f"{carrier_id} source count drift")

        provenance_keys = set()
        for context_id, row in rows.items():
            relation = row["return_certificate"]["Lambda_4"]
            if relation["construction_payload_sha256"] != candidate[
                "construction_payload_sha256"
            ]:
                raise AssertionError(f"{carrier_id} adapter relation drift")
            if relation["menu_sha256"] != _digest(menus[context_id]):
                raise AssertionError(f"{carrier_id} adapter menu binding drift")
            for provenance in row["provenance_fiber"]:
                key = (
                    carrier_id,
                    context_id,
                    str(provenance["kappa_4_ISE_id"]),
                )
                provenance_keys.add(key)
                if key not in declaration_support:
                    raise AssertionError(f"{carrier_id} provenance lacks PEC support")
        if provenance_keys != {
            key for key in declaration_support if key[0] == carrier_id
        }:
            raise AssertionError(f"{carrier_id} PEC support/provenance domain drift")

        frozen_carriers.append(
            {
                "carrier_id": carrier_id,
                "carrier_tag": int(spec["tag"]),
                "section": str(spec["section"]),
                "projectability_payload_sha256": _digest(projection),
                "rank4_construction_payload_sha256": candidate[
                    "construction_payload_sha256"
                ],
                "menu_payload_sha256": _digest(candidate["construction"]["menus"]),
                "exact_relation_payload_sha256": _digest(
                    candidate["construction"]["exact_lifts"]
                ),
                "PEC_support_rows_sha256": _digest(
                    [
                        declaration_support[key]
                        for key in sorted(provenance_keys)
                    ]
                ),
            }
        )

    frozen_completion_input = {
        "PEC_declaration_content_sha256": declaration["content_sha256"],
        "PEC_common_profile_payload_sha256": declaration[
            "unsupported_provenance_analysis"
        ]["common_profile_payload_sha256"],
        "B1_projectability_payload_sha256": projectability[
            "projectability_payload_sha256"
        ],
        "tagged_carriers": frozen_carriers,
    }
    frozen_completion_input_digest = _digest(frozen_completion_input)

    # No low-rank oracle exists before the tagged input above is frozen.
    low_rank_by_defect: dict[tuple[int, ...], LowRankOracle] = {}

    def local_return_receipt(
        record: Mapping[str, Any],
    ) -> tuple[bool, int, str]:
        target_context = record["exact"]["target_context"]
        defect = tuple(int(value) for value in target_context["defect"])
        oracle = low_rank_by_defect.get(defect)
        if oracle is None:
            oracle = LowRankOracle(CompleteExitOracle((_cycle(N), defect), N))
            low_rank_by_defect[defect] = oracle
        target = tuple(int(value) for value in record["exact"]["target_endpoint"])
        return (
            oracle.is_good(target),
            int(record["skeleton"]["target_rank"]),
            str(target_context["context_id"]),
        )

    carrier_evaluations = []
    pooled_good_provenances = []
    pooled_successful_lifts: set[tuple[str, str]] = set()
    pooled_unsuccessful_lifts: set[tuple[str, str]] = set()
    pooled_certified_targets: set[tuple[str, str]] = set()
    pooled_mixed_sources: set[tuple[str, str]] = set()

    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        carrier_tag = int(spec["tag"])
        candidate = candidates[carrier_id]
        projection = projectability_carriers[carrier_id]
        projectability_rows = {
            str(row["context_id"]): row for row in projection["rows"]
        }
        menu_rows = {
            str(row["source_context"]["context_id"]): row
            for row in candidate["construction"]["menus"]["contexts"]
        }
        receipts = candidate["construction"]["exact_lifts"]["receipts"]
        by_id = {str(row["receipt_id"]): row for row in receipts}
        if len(by_id) != len(receipts):
            raise AssertionError(f"{carrier_id} exact receipt ids are not unique")

        successful_ids: set[str] = set()
        unsuccessful_ids: set[str] = set()
        certified_target_ids: set[str] = set()
        mixed_source_ids: set[str] = set()
        successful_channel_count = 0
        failed_channel_count = 0
        mixed_channel_count = 0
        returning_channel_histogram: Counter[int] = Counter()
        context_rows = []
        good_provenance_rows = []

        for context_id in sorted(menu_rows):
            menu = menu_rows[context_id]
            projection_row = projectability_rows[context_id]
            supported_kappa_ids = sorted(
                str(provenance["kappa_4_ISE_id"])
                for provenance in projection_row["provenance_fiber"]
                if declaration_support[
                    (
                        carrier_id,
                        context_id,
                        str(provenance["kappa_4_ISE_id"]),
                    )
                ]["supported"]
            )
            if not supported_kappa_ids:
                raise AssertionError(f"{carrier_id} context lacks PEC support")

            channel_rows = []
            for channel in menu["channels"]:
                channel_successful = []
                channel_unsuccessful = []
                successful_targets = set()
                successful_ranks = set()
                for receipt_id_raw in channel["exact_lift_ids"]:
                    receipt_id = str(receipt_id_raw)
                    good, target_rank, target_id = local_return_receipt(
                        by_id[receipt_id]
                    )
                    tagged_receipt = (carrier_id, receipt_id)
                    if good:
                        channel_successful.append(receipt_id)
                        successful_ids.add(receipt_id)
                        pooled_successful_lifts.add(tagged_receipt)
                        successful_targets.add(target_id)
                        successful_ranks.add(target_rank)
                        certified_target_ids.add(target_id)
                        pooled_certified_targets.add((carrier_id, target_id))
                    else:
                        channel_unsuccessful.append(receipt_id)
                        unsuccessful_ids.add(receipt_id)
                        pooled_unsuccessful_lifts.add(tagged_receipt)
                channel_good = bool(channel_successful)
                if channel_good:
                    successful_channel_count += 1
                else:
                    failed_channel_count += 1
                if channel_successful and channel_unsuccessful:
                    mixed_channel_count += 1
                    mixed_source_ids.add(context_id)
                    pooled_mixed_sources.add((carrier_id, context_id))
                channel_rows.append(
                    {
                        "carrier_id": carrier_id,
                        "carrier_tag": carrier_tag,
                        "channel_id": str(channel["channel_id"]),
                        "exact_lift_count": len(channel["exact_lift_ids"]),
                        "has_local_return_exact_lift": channel_good,
                        "local_return_exact_lift_count": len(channel_successful),
                        "local_return_exact_lift_ids": sorted(channel_successful),
                        "nonreturning_exact_lift_count": len(
                            channel_unsuccessful
                        ),
                        "nonreturning_exact_lift_ids": sorted(
                            channel_unsuccessful
                        ),
                        "local_return_target_context_ids": sorted(
                            successful_targets
                        ),
                        "local_return_target_ranks": sorted(successful_ranks),
                    }
                )

            returning_channels = sum(
                1 for row in channel_rows if row["has_local_return_exact_lift"]
            )
            local_return = returning_channels > 0
            returning_channel_histogram[returning_channels] += 1
            good_kappa_ids = supported_kappa_ids if local_return else []
            for kappa_id in good_kappa_ids:
                tagged_good = {
                    "carrier_id": carrier_id,
                    "carrier_tag": carrier_tag,
                    "context_id": context_id,
                    "return_certificate_id": str(
                        projection_row["return_certificate_id"]
                    ),
                    "kappa_4_ISE_id": kappa_id,
                }
                good_provenance_rows.append(tagged_good)
                pooled_good_provenances.append(tagged_good)
            context_rows.append(
                {
                    "carrier_id": carrier_id,
                    "carrier_tag": carrier_tag,
                    "context_id": context_id,
                    "return_certificate_id": str(
                        projection_row["return_certificate_id"]
                    ),
                    "PEC_supported_kappa_4_ISE_ids": supported_kappa_ids,
                    "provenance_fiber_size": len(
                        projection_row["provenance_fiber"]
                    ),
                    "menu_size": int(menu["menu_size"]),
                    "returning_channel_count": returning_channels,
                    "nonreturning_channel_count": int(menu["menu_size"])
                    - returning_channels,
                    "LocalReturn_4_j_fs": local_return,
                    "G_PEC_j_fs_kappa_4_ISE_ids": good_kappa_ids,
                    "channels": channel_rows,
                }
            )

        exact_lift_ids = set(by_id)
        if successful_ids | unsuccessful_ids != exact_lift_ids:
            raise AssertionError(f"{carrier_id} evaluator missed exact lifts")
        if successful_ids & unsuccessful_ids:
            raise AssertionError(f"{carrier_id} lift received two statuses")
        menu_summary = candidate["construction"]["menus"]
        if successful_channel_count + failed_channel_count != int(
            menu_summary["channel_count"]
        ):
            raise AssertionError(f"{carrier_id} evaluator missed channels")
        if _digest(candidate["construction"]) != candidate[
            "construction_payload_sha256"
        ]:
            raise AssertionError(f"{carrier_id} evaluation mutated construction")

        completed_source_count = sum(
            1 for row in context_rows if row["G_PEC_j_fs_kappa_4_ISE_ids"]
        )
        carrier_evaluations.append(
            {
                "carrier_id": carrier_id,
                "carrier_tag": carrier_tag,
                "section": str(spec["section"]),
                "source_count": len(context_rows),
                "PEC_supported_source_count": sum(
                    1 for row in context_rows if row["PEC_supported_kappa_4_ISE_ids"]
                ),
                "completed_source_count": completed_source_count,
                "hostile_source_count": len(context_rows)
                - completed_source_count,
                "channel_count": int(menu_summary["channel_count"]),
                "returning_channel_count": successful_channel_count,
                "nonreturning_channel_count": failed_channel_count,
                "mixed_channel_count": mixed_channel_count,
                "mixed_source_count": len(mixed_source_ids),
                "mixed_source_context_ids": sorted(mixed_source_ids),
                "exact_lift_count": len(exact_lift_ids),
                "local_return_exact_lift_count": len(successful_ids),
                "nonreturning_exact_lift_count": len(unsuccessful_ids),
                "certified_target_context_count": len(certified_target_ids),
                "returning_channel_count_histogram": {
                    str(count): sources
                    for count, sources in sorted(returning_channel_histogram.items())
                },
                "contexts": context_rows,
                "G_PEC_j_fs": good_provenance_rows,
                "theorem_holds": completed_source_count == len(context_rows),
            }
        )

    total_sources = sum(row["source_count"] for row in carrier_evaluations)
    total_completed = sum(
        row["completed_source_count"] for row in carrier_evaluations
    )
    total_channels = sum(row["channel_count"] for row in carrier_evaluations)
    total_returning_channels = sum(
        row["returning_channel_count"] for row in carrier_evaluations
    )
    total_nonreturning_channels = sum(
        row["nonreturning_channel_count"] for row in carrier_evaluations
    )
    total_mixed_channels = sum(
        row["mixed_channel_count"] for row in carrier_evaluations
    )
    total_exact_lifts = sum(
        row["exact_lift_count"] for row in carrier_evaluations
    )
    all_hold = all(row["theorem_holds"] for row in carrier_evaluations)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "rank": 4,
            "sections": [str(spec["section"]) for spec in carrier_specs],
            "component": "PEC",
            "carrier_tagged_relations": True,
            "fixed_scope_return_certificate_adapters": True,
            "all_n_claim": False,
            "winner_selected": False,
            "menu_or_lift_rebuilt": False,
            "historical_Good4_artifacts_loaded": False,
            "rank5_return_evaluators_loaded": False,
            "new_census": False,
        },
        "phase_order": [
            "load_and_verify_frozen_PEC_support",
            "load_and_verify_cand3_cand4_cand5_complete_rank4_relations",
            "freeze_tagged_completion_input_digest",
            "define_generic_carrier_specific_LocalReturn_4_j_fs",
            "open_exact_P_le3_oracle",
            "evaluate_every_tagged_exact_lift_without_winner_selection",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            "PEC_declaration": _input_record(declaration_path, declaration),
            "projectability": _input_record(
                projectability_path, projectability
            ),
            "rank4_candidates": candidate_inputs,
        },
        "frozen_completion_input": frozen_completion_input,
        "frozen_completion_input_sha256": frozen_completion_input_digest,
        "definition": {
            "LocalReturn_4_j_fs": (
                "for carrier tag j, there exist a frozen candj menu channel m "
                "and exact lift x in Lift_4,candj^fs(C,m) whose theorem-facing "
                "target belongs to exact P_<=3^(7)"
            ),
            "G_PEC_j_fs": (
                "kappa belongs to the frozen carrier-j P_ISE fiber, satisfies "
                "the already frozen existential RelevantBranch_PEC^ISE relation, "
                "and satisfies generic LocalReturn_4,j^fs"
            ),
            "G_PEC_pool": (
                "tagged disjoint union over j in {3,4,5} of {j} times G_PEC_j^fs"
            ),
            "forbidden_success_refinements": FORBIDDEN_SUCCESS_REFINEMENTS,
        },
        "evaluation": {
            "carriers": carrier_evaluations,
            "pooled": {
                "source_count": total_sources,
                "PEC_supported_source_count": sum(
                    row["PEC_supported_source_count"]
                    for row in carrier_evaluations
                ),
                "completed_source_count": total_completed,
                "hostile_source_count": total_sources - total_completed,
                "channel_count": total_channels,
                "returning_channel_count": total_returning_channels,
                "nonreturning_channel_count": total_nonreturning_channels,
                "mixed_channel_count": total_mixed_channels,
                "mixed_source_count": len(pooled_mixed_sources),
                "exact_lift_count": total_exact_lifts,
                "local_return_exact_lift_count": len(pooled_successful_lifts),
                "nonreturning_exact_lift_count": len(
                    pooled_unsuccessful_lifts
                ),
                "certified_tagged_target_count": len(pooled_certified_targets),
                "G_PEC_pool": pooled_good_provenances,
            },
        },
        "theorem": {
            "name": "PEC-FS-Tagged-Completion",
            "carrier_statements": [
                (
                    f"for every C in {spec['section']}, PECSupp_7 implies "
                    f"G_PEC^fs,{spec['tag']} is nonempty"
                )
                for spec in carrier_specs
            ],
            "pooled_statement": (
                "the tagged disjoint union G_PEC^fs,pool is nonempty for every "
                "admitted source in the tagged cand3/cand4/cand5 union"
            ),
            "holds": all_hold and total_completed == total_sources,
        },
        "quantifier_audit": {
            "source_quantifier": (
                "universal separately over each admitted cand3, cand4, and cand5 source"
            ),
            "carrier_quantifier": "tagged disjoint union, not an unlabelled relation",
            "channel_quantifier": "existential within the source's carrier",
            "exact_lift_quantifier": "existential inside a supported channel",
            "failed_exact_lifts_retained": len(pooled_unsuccessful_lifts),
            "mixed_fibers_retained": total_mixed_channels,
            "winner_selected": False,
        },
        "claim_boundary": {
            "proved": [
                "tagged fixed-n=7 PEC component completion on cand3, cand4, and cand5",
                "generic carrier-specific LocalReturn_4,j^fs suffices for every PEC-supported source",
                "all unsuccessful exact lifts remain in their own complete frozen carrier relations",
            ],
            "not_proved": [
                "all-n PEC completion",
                "equality of any fixed-scope macro relation with Lambda_4^complete(C)",
                "an untagged identification of the three carrier relations",
                "a successful-path normal form for PEC",
                "universal channel or exact-lift success as a schema premise",
                "completeness of the mechanism family {OW,FPC,PEC}",
                "all-rank F5",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    input_paths: Sequence[Path],
) -> dict[str, Any]:
    source_paths = [
        Path(__file__).resolve(),
        HERE / "paper28_prepare_second_rank4_section_candidate.py",
        HERE / "section_return_core.py",
        HERE / "costed_endpoint_diagnostic.py",
        HERE / "single_defect_macro_trap.py",
        HERE / "mass_maturity_legacy.py",
        HERE / "validation" / "validate_paper28_pec_component_completion.py",
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "TAGGED_POST_DECLARATION_GENERIC_LOCAL_RETURN_EVALUATION",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "frozen_completion_input_sha256": payload[
                "frozen_completion_input_sha256"
            ],
        },
        "inputs": [
            {"name": path.name, "sha256": _sha256(path)} for path in input_paths
        ],
        "source_closure": [
            {"name": path.relative_to(HERE).as_posix(), "sha256": _sha256(path)}
            for path in source_paths
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declaration", type=Path, default=DEFAULT_DECLARATION)
    parser.add_argument(
        "--projectability", type=Path, default=DEFAULT_PROJECTABILITY
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        declaration_path=args.declaration,
        projectability_path=args.projectability,
        carrier_specs=CARRIER_SPECS,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    input_paths = [args.declaration, args.projectability] + [
        Path(spec["candidate"]) for spec in CARRIER_SPECS
    ]
    _write_receipt(
        receipt_path,
        build_receipt(output=args.out, payload=payload, input_paths=input_paths),
    )
    pooled = payload["evaluation"]["pooled"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "frozen_completion_input_sha256": payload[
                    "frozen_completion_input_sha256"
                ],
                "theorem_holds": payload["theorem"]["holds"],
                "by_carrier": {
                    row["carrier_id"]: {
                        key: row[key]
                        for key in (
                            "source_count",
                            "completed_source_count",
                            "returning_channel_count",
                            "nonreturning_channel_count",
                            "mixed_channel_count",
                            "exact_lift_count",
                            "local_return_exact_lift_count",
                            "nonreturning_exact_lift_count",
                        )
                    }
                    for row in payload["evaluation"]["carriers"]
                },
                **{
                    key: pooled[key]
                    for key in (
                        "source_count",
                        "PEC_supported_source_count",
                        "completed_source_count",
                        "returning_channel_count",
                        "nonreturning_channel_count",
                        "mixed_channel_count",
                        "exact_lift_count",
                        "local_return_exact_lift_count",
                        "nonreturning_exact_lift_count",
                    )
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
