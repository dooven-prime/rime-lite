#!/usr/bin/env python3
"""Evaluate tagged fixed-scope GFPC completion with generic LocalReturn.

The GFPC declaration, cand2/ext provenance fibers, and both complete rank-four
relations are frozen before the exact P_<=3 oracle is opened.  The two carrier
relations remain tagged and disjoint.  No prior component completion or
historical Good evaluator is a proof input, and no winner is selected.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_prepare_second_rank4_section_candidate import _cycle
from section_return_core import CompleteExitOracle, LowRankOracle

SCHEMA = "paper28-gfpc-component-completion-v1"
RECEIPT_SCHEMA = "paper28-gfpc-component-completion-receipt-v1"
DECLARATION_SCHEMA = "paper28-fourth-mechanism-schema-declaration-v1"
CAND2_PROJECTABILITY_SCHEMA = (
    "paper28-fixed-scope-projectability-support-separation-v1"
)
EXT_PROJECTABILITY_SCHEMA = "paper28-extremal-carrier-support-separation-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_DECLARATION = (
    RESULTS / "paper28_fourth_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_CAND2_PROJECTABILITY = (
    RESULTS / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)
DEFAULT_EXT_PROJECTABILITY = (
    RESULTS / "paper28_extremal_carrier_support_separation_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_gfpc_component_completion_v1.json.gz"

N = 7
CARRIER_SPECS = (
    {
        "id": "cand2",
        "tag": "cand2",
        "section": "Sec_4,cand2^(7)",
        "candidate_schema": "paper28-second-rank4-section-candidate-v1",
        "candidate": RESULTS / "paper28_second_rank4_section_candidate_v1.json.gz",
        "projectability": DEFAULT_CAND2_PROJECTABILITY,
        "projectability_schema": CAND2_PROJECTABILITY_SCHEMA,
        "expected_sources": 48,
    },
    {
        "id": "ext",
        "tag": "ext",
        "section": "Sec_4,ext^(7)",
        "candidate_schema": "paper28-ext-rank4-section-candidate-v1",
        "candidate": RESULTS / "paper28_ext_rank4_section_candidate_v1.json.gz",
        "projectability": DEFAULT_EXT_PROJECTABILITY,
        "projectability_schema": EXT_PROJECTABILITY_SCHEMA,
        "expected_sources": 35,
    },
)

FORBIDDEN_SUCCESS_REFINEMENTS = [
    "F_ent must participate in a later fusion",
    "incoming distinguished packet must be carried or consumed",
    "fixed background masses or current partition",
    "literal-identity handoff",
    "fixed corridor length, surplus, word, or offset profile",
    "selected winner",
]
FORBIDDEN_INPUTS = [
    "paper28_fpc_component_completion_v1.json.gz",
    "paper28_section_return_menu_audit_v1.json.gz",
    "paper28_second_rank4_section_return_evaluation_v1.json.gz",
    "paper28_rank5_section_return_evaluation_v1.json.gz",
    "paper28_second_rank5_section_return_evaluation_v1.json.gz",
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
    return path.with_name(
        f"{path.name.removesuffix('.json.gz')}.receipt.json"
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


def _projectability_rows(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return list(payload["projectability"]["rows"])


def build_payload(
    *,
    declaration_path: Path,
    carrier_specs: Sequence[Mapping[str, Any]] = CARRIER_SPECS,
) -> dict[str, Any]:
    declaration = _load(declaration_path)
    if declaration.get("schema") != DECLARATION_SCHEMA:
        raise AssertionError("unexpected GFPC declaration schema")
    _verify_content_digest(declaration, "GFPC declaration")
    if declaration["scope"]["success_evaluator_loaded"]:
        raise AssertionError("GFPC declaration was not frozen before completion")
    if declaration["declaration"]["expanded_family"] != [
        "OW",
        "FPC",
        "PEC",
        "GFPC",
    ]:
        raise AssertionError("GFPC declaration family drift")
    if declaration["summary"]["GFPC_supported_provenances"] != 83:
        raise AssertionError("GFPC support domain drift")

    declaration_support = {
        (
            str(row["carrier_id"]),
            str(row["context_id"]),
            str(row["kappa_4_ISE_id"]),
        ): row
        for row in declaration["declaration"]["support_rows"]
    }
    if len(declaration_support) != 83 or not all(
        row["supported"] for row in declaration_support.values()
    ):
        raise AssertionError("GFPC support relation is not the frozen 83-row domain")

    candidates: dict[str, dict[str, Any]] = {}
    projections: dict[str, dict[str, Any]] = {}
    candidate_inputs: dict[str, dict[str, Any]] = {}
    projectability_inputs: dict[str, dict[str, Any]] = {}
    frozen_carriers = []

    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        candidate_path = Path(spec["candidate"])
        projectability_path = Path(spec["projectability"])
        candidate = _load(candidate_path)
        projectability = _load(projectability_path)
        if candidate.get("schema") != spec["candidate_schema"]:
            raise AssertionError(f"unexpected {carrier_id} candidate schema")
        if projectability.get("schema") != spec["projectability_schema"]:
            raise AssertionError(f"unexpected {carrier_id} projectability schema")
        _verify_content_digest(candidate, f"{carrier_id} candidate")
        _verify_content_digest(projectability, f"{carrier_id} projectability")
        if candidate["scope"]["evaluation_status"] != "NOT_RUN":
            raise AssertionError(f"{carrier_id} relation is not pre-evaluation")
        if candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
            raise AssertionError(f"{carrier_id} candidate contains an evaluator")
        if _digest(candidate["construction"]) != candidate[
            "construction_payload_sha256"
        ]:
            raise AssertionError(f"{carrier_id} construction digest mismatch")

        declaration_binding = declaration["inputs"][
            "cand2_projectability"
            if carrier_id == "cand2"
            else "ext_support_separation"
        ]
        if declaration_binding["sha256"] != _sha256(projectability_path):
            raise AssertionError(f"{carrier_id} declaration binding drift")

        rows = {
            str(row["context_id"]): row
            for row in _projectability_rows(projectability)
        }
        menus = {
            str(row["source_context"]["context_id"]): row
            for row in candidate["construction"]["menus"]["contexts"]
        }
        if set(rows) != set(menus):
            raise AssertionError(f"{carrier_id} projectability/menu domain drift")
        if len(rows) != int(spec["expected_sources"]):
            raise AssertionError(f"{carrier_id} source count drift")

        if carrier_id == "cand2":
            bound = projectability["inputs"]["rank4_candidate"]
            if bound["sha256"] != _sha256(candidate_path):
                raise AssertionError("cand2 adapter file binding drift")
            if bound["content_sha256"] != candidate["content_sha256"]:
                raise AssertionError("cand2 adapter content binding drift")

        provenance_keys = set()
        for context_id, row in rows.items():
            relation = row["return_certificate"]["Lambda_4"]
            if carrier_id == "cand2":
                if relation["construction_payload_sha256"] != candidate[
                    "construction_payload_sha256"
                ]:
                    raise AssertionError("cand2 relation binding drift")
                expected_menu_digest = relation["menu_sha256"]
            else:
                if relation["future_free_menu_content_sha256"] != _digest(
                    candidate["construction"]["menus"]
                ):
                    raise AssertionError("ext complete-menu binding drift")
                expected_menu_digest = relation["source_menu_sha256"]
                relation_ids = set(map(str, relation["exact_lift_ids"]))
                candidate_ids = {
                    str(receipt_id)
                    for channel in menus[context_id]["channels"]
                    for receipt_id in channel["exact_lift_ids"]
                }
                if relation_ids != candidate_ids:
                    raise AssertionError("ext source exact-lift binding drift")
            if expected_menu_digest != _digest(menus[context_id]):
                raise AssertionError(f"{carrier_id} source menu binding drift")
            for provenance in row["provenance_fiber"]:
                key = (
                    carrier_id,
                    context_id,
                    str(provenance["kappa_4_ISE_id"]),
                )
                provenance_keys.add(key)
                if key not in declaration_support:
                    raise AssertionError(
                        f"{carrier_id} projectable provenance lacks GFPC support"
                    )
        if len(provenance_keys) != len(rows):
            raise AssertionError(f"{carrier_id} expected singleton provenance fibers")

        candidates[carrier_id] = candidate
        projections[carrier_id] = projectability
        candidate_inputs[carrier_id] = _input_record(candidate_path, candidate)
        projectability_inputs[carrier_id] = _input_record(
            projectability_path, projectability
        )
        frozen_carriers.append(
            {
                "carrier_id": carrier_id,
                "carrier_tag": str(spec["tag"]),
                "section": str(spec["section"]),
                "projectability_payload_sha256": projectability[
                    "projectability_payload_sha256"
                ],
                "rank4_construction_payload_sha256": candidate[
                    "construction_payload_sha256"
                ],
                "menus_sha256": _digest(candidate["construction"]["menus"]),
                "exact_relation_sha256": _digest(
                    candidate["construction"]["exact_lifts"]["receipts"]
                ),
            }
        )

    frozen_completion_input = {
        "GFPC_declaration_content_sha256": declaration["content_sha256"],
        "GFPC_anonymous_profile_payload_sha256": declaration[
            "anonymous_role_analysis"
        ]["anonymous_profile_payload_sha256"],
        "support_rows_sha256": _digest(
            declaration["declaration"]["support_rows"]
        ),
        "tagged_carriers": frozen_carriers,
    }
    frozen_completion_input_digest = _digest(frozen_completion_input)

    # The exact low-rank oracle is opened only after the complete tagged input
    # relation and its digest have been fixed above.
    low_rank_by_defect: dict[tuple[int, ...], LowRankOracle] = {}
    carrier_evaluations = []
    pooled_good = []
    pooled_successful_lifts: set[tuple[str, str]] = set()
    pooled_unsuccessful_lifts: set[tuple[str, str]] = set()
    pooled_certified_targets: set[tuple[str, str]] = set()
    pooled_mixed_sources: set[tuple[str, str]] = set()

    for spec in carrier_specs:
        carrier_id = str(spec["id"])
        carrier_tag = str(spec["tag"])
        candidate = candidates[carrier_id]
        projectability_rows = {
            str(row["context_id"]): row
            for row in _projectability_rows(projections[carrier_id])
        }
        menu_rows = {
            str(row["source_context"]["context_id"]): row
            for row in candidate["construction"]["menus"]["contexts"]
        }
        receipts = candidate["construction"]["exact_lifts"]["receipts"]
        receipts_by_id = {str(row["receipt_id"]): row for row in receipts}
        if len(receipts_by_id) != len(receipts):
            raise AssertionError(f"{carrier_id} receipt ids are not unique")

        def local_return(
            receipt_id: str,
            *,
            bound_receipts: Mapping[str, Mapping[str, Any]] = receipts_by_id,
        ) -> tuple[bool, int, str]:
            record = bound_receipts[receipt_id]
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

        successful_ids: set[str] = set()
        unsuccessful_ids: set[str] = set()
        certified_target_ids: set[str] = set()
        successful_channel_count = 0
        failed_channel_count = 0
        mixed_channel_count = 0
        mixed_source_ids: set[str] = set()
        returning_histogram: Counter[int] = Counter()
        context_rows = []
        good_rows = []

        for context_id in sorted(menu_rows):
            menu = menu_rows[context_id]
            projection = projectability_rows[context_id]
            supported_kappas = sorted(
                str(provenance["kappa_4_ISE_id"])
                for provenance in projection["provenance_fiber"]
                if declaration_support[
                    (
                        carrier_id,
                        context_id,
                        str(provenance["kappa_4_ISE_id"]),
                    )
                ]["supported"]
            )
            if not supported_kappas:
                raise AssertionError(f"{carrier_id} source lacks GFPC support")

            channel_rows = []
            for channel in menu["channels"]:
                successful = []
                unsuccessful = []
                targets = set()
                ranks = set()
                for raw_receipt_id in channel["exact_lift_ids"]:
                    receipt_id = str(raw_receipt_id)
                    good, target_rank, target_id = local_return(receipt_id)
                    if good:
                        successful.append(receipt_id)
                        successful_ids.add(receipt_id)
                        pooled_successful_lifts.add((carrier_id, receipt_id))
                        targets.add(target_id)
                        ranks.add(target_rank)
                        certified_target_ids.add(target_id)
                        pooled_certified_targets.add((carrier_id, target_id))
                    else:
                        unsuccessful.append(receipt_id)
                        unsuccessful_ids.add(receipt_id)
                        pooled_unsuccessful_lifts.add((carrier_id, receipt_id))
                if successful:
                    successful_channel_count += 1
                else:
                    failed_channel_count += 1
                if successful and unsuccessful:
                    mixed_channel_count += 1
                    mixed_source_ids.add(context_id)
                    pooled_mixed_sources.add((carrier_id, context_id))
                channel_rows.append(
                    {
                        "carrier_id": carrier_id,
                        "carrier_tag": carrier_tag,
                        "channel_id": str(channel["channel_id"]),
                        "exact_lift_count": len(channel["exact_lift_ids"]),
                        "has_local_return_exact_lift": bool(successful),
                        "local_return_exact_lift_count": len(successful),
                        "local_return_exact_lift_ids": sorted(successful),
                        "nonreturning_exact_lift_count": len(unsuccessful),
                        "nonreturning_exact_lift_ids": sorted(unsuccessful),
                        "local_return_target_context_ids": sorted(targets),
                        "local_return_target_ranks": sorted(ranks),
                    }
                )

            returning_channels = sum(
                int(row["has_local_return_exact_lift"]) for row in channel_rows
            )
            returning_histogram[returning_channels] += 1
            source_returns = returning_channels > 0
            good_kappas = supported_kappas if source_returns else []
            for kappa_id in good_kappas:
                tagged = {
                    "carrier_id": carrier_id,
                    "carrier_tag": carrier_tag,
                    "context_id": context_id,
                    "return_certificate_id": str(
                        projection["return_certificate_id"]
                    ),
                    "kappa_4_ISE_id": kappa_id,
                }
                good_rows.append(tagged)
                pooled_good.append(tagged)
            context_rows.append(
                {
                    "carrier_id": carrier_id,
                    "carrier_tag": carrier_tag,
                    "context_id": context_id,
                    "return_certificate_id": str(
                        projection["return_certificate_id"]
                    ),
                    "GFPC_supported_kappa_4_ISE_ids": supported_kappas,
                    "provenance_fiber_size": len(projection["provenance_fiber"]),
                    "menu_size": int(menu["menu_size"]),
                    "returning_channel_count": returning_channels,
                    "nonreturning_channel_count": int(menu["menu_size"])
                    - returning_channels,
                    "LocalReturn_4_j_fs": source_returns,
                    "G_GFPC_j_fs_kappa_4_ISE_ids": good_kappas,
                    "channels": channel_rows,
                }
            )

        exact_ids = set(receipts_by_id)
        if successful_ids | unsuccessful_ids != exact_ids:
            raise AssertionError(f"{carrier_id} evaluator missed exact lifts")
        if successful_ids & unsuccessful_ids:
            raise AssertionError(f"{carrier_id} lift received two statuses")
        menus_summary = candidate["construction"]["menus"]
        if successful_channel_count + failed_channel_count != int(
            menus_summary["channel_count"]
        ):
            raise AssertionError(f"{carrier_id} evaluator missed channels")

        completed = sum(
            int(bool(row["G_GFPC_j_fs_kappa_4_ISE_ids"]))
            for row in context_rows
        )
        carrier_evaluations.append(
            {
                "carrier_id": carrier_id,
                "carrier_tag": carrier_tag,
                "section": str(spec["section"]),
                "source_count": len(context_rows),
                "GFPC_supported_source_count": sum(
                    int(bool(row["GFPC_supported_kappa_4_ISE_ids"]))
                    for row in context_rows
                ),
                "completed_source_count": completed,
                "hostile_source_count": len(context_rows) - completed,
                "channel_count": int(menus_summary["channel_count"]),
                "returning_channel_count": successful_channel_count,
                "nonreturning_channel_count": failed_channel_count,
                "mixed_channel_count": mixed_channel_count,
                "mixed_source_count": len(mixed_source_ids),
                "mixed_source_context_ids": sorted(mixed_source_ids),
                "exact_lift_count": len(exact_ids),
                "local_return_exact_lift_count": len(successful_ids),
                "nonreturning_exact_lift_count": len(unsuccessful_ids),
                "certified_target_context_count": len(certified_target_ids),
                "returning_channel_count_histogram": {
                    str(count): sources
                    for count, sources in sorted(returning_histogram.items())
                },
                "contexts": context_rows,
                "G_GFPC_j_fs": good_rows,
                "theorem_holds": completed == len(context_rows),
            }
        )

    total_sources = sum(row["source_count"] for row in carrier_evaluations)
    total_completed = sum(
        row["completed_source_count"] for row in carrier_evaluations
    )
    total_mixed_channels = sum(
        row["mixed_channel_count"] for row in carrier_evaluations
    )
    all_hold = all(row["theorem_holds"] for row in carrier_evaluations)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "rank": 4,
            "sections": [str(spec["section"]) for spec in carrier_specs],
            "component": "GFPC",
            "carrier_tagged_relations": True,
            "fixed_scope_return_certificate_adapters": True,
            "all_n_claim": False,
            "winner_selected": False,
            "historical_FPC_completion_loaded": False,
            "historical_Good4_artifacts_loaded": False,
            "rank5_return_evaluators_loaded": False,
            "new_census": False,
        },
        "phase_order": [
            "load_and_verify_frozen_GFPC_support",
            "load_and_verify_cand2_ext_complete_rank4_relations",
            "freeze_tagged_completion_input_digest",
            "define_generic_carrier_specific_LocalReturn_4_j_fs",
            "open_exact_P_le3_oracle",
            "evaluate_every_tagged_exact_lift_without_winner_selection",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            "GFPC_declaration": _input_record(declaration_path, declaration),
            "projectability": projectability_inputs,
            "rank4_candidates": candidate_inputs,
        },
        "frozen_completion_input": frozen_completion_input,
        "frozen_completion_input_sha256": frozen_completion_input_digest,
        "definition": {
            "LocalReturn_4_j_fs": (
                "for carrier tag j, there exist a frozen menu channel m and "
                "exact lift x in Lift_4,j^fs(C,m) whose theorem-facing target "
                "belongs to exact P_<=3^(7)"
            ),
            "G_GFPC_j_fs": (
                "kappa belongs to the frozen carrier-j P_ISE fiber, satisfies "
                "the already frozen existential RelevantBranch_GFPC^ISE, and "
                "satisfies generic LocalReturn_4,j^fs"
            ),
            "G_GFPC_pool": (
                "tagged disjoint union of cand2 and ext GFPC good-provenance relations"
            ),
            "forbidden_success_refinements": FORBIDDEN_SUCCESS_REFINEMENTS,
        },
        "evaluation": {
            "carriers": carrier_evaluations,
            "pooled": {
                "source_count": total_sources,
                "GFPC_supported_source_count": sum(
                    row["GFPC_supported_source_count"]
                    for row in carrier_evaluations
                ),
                "completed_source_count": total_completed,
                "hostile_source_count": total_sources - total_completed,
                "channel_count": sum(
                    row["channel_count"] for row in carrier_evaluations
                ),
                "returning_channel_count": sum(
                    row["returning_channel_count"]
                    for row in carrier_evaluations
                ),
                "nonreturning_channel_count": sum(
                    row["nonreturning_channel_count"]
                    for row in carrier_evaluations
                ),
                "mixed_channel_count": total_mixed_channels,
                "mixed_source_count": len(pooled_mixed_sources),
                "exact_lift_count": sum(
                    row["exact_lift_count"] for row in carrier_evaluations
                ),
                "local_return_exact_lift_count": len(
                    pooled_successful_lifts
                ),
                "nonreturning_exact_lift_count": len(
                    pooled_unsuccessful_lifts
                ),
                "certified_tagged_target_count": len(
                    pooled_certified_targets
                ),
                "G_GFPC_pool": pooled_good,
            },
        },
        "theorem": {
            "name": "GFPC-FS-Tagged-Completion",
            "carrier_statements": [
                (
                    f"for every C in {spec['section']}, GFPCSupp_7 implies "
                    f"G_GFPC^fs,{spec['tag']} is nonempty"
                )
                for spec in carrier_specs
            ],
            "pooled_statement": (
                "the tagged disjoint union G_GFPC^fs,pool is nonempty for "
                "every admitted source in the tagged cand2/ext union"
            ),
            "holds": all_hold and total_completed == total_sources,
        },
        "quantifier_audit": {
            "source_quantifier": (
                "universal separately over each admitted cand2 and ext source"
            ),
            "carrier_quantifier": "tagged disjoint union, never unlabelled",
            "channel_quantifier": "existential within the source's carrier",
            "exact_lift_quantifier": "existential inside a supported channel",
            "failed_exact_lifts_retained": len(pooled_unsuccessful_lifts),
            "mixed_fibers_retained": total_mixed_channels,
            "winner_selected": False,
        },
        "claim_boundary": {
            "proved": [
                "tagged fixed-n=7 GFPC component completion on cand2 and ext",
                "the same generic carrier-specific LocalReturn semantics suffices on both carriers",
                "all unsuccessful exact lifts remain in their complete frozen carrier relations",
            ],
            "not_proved": [
                "inheritance of FPC completion by schema subsumption",
                "all-n GFPC completion",
                "equality of either fixed-scope relation with Lambda_4^complete(C)",
                "an untagged identification of cand2 and ext relations",
                "a GFPC successful-path normal form",
                "minimality of {GFPC,PEC}",
                "all-rank F5",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, output: Path, payload: Mapping[str, Any], input_paths: Sequence[Path]
) -> dict[str, Any]:
    source_paths = [
        Path(__file__).resolve(),
        HERE / "paper28_prepare_ext_rank4_section_candidate.py",
        HERE / "paper28_prepare_second_rank4_section_candidate.py",
        HERE / "section_return_core.py",
        HERE / "costed_endpoint_diagnostic.py",
        HERE / "single_defect_macro_trap.py",
        HERE / "mass_maturity_legacy.py",
        HERE / "validation" / "validate_paper28_gfpc_component_completion.py",
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
            {"name": path.name, "sha256": _sha256(path)}
            for path in input_paths
        ],
        "source_closure": [
            {
                "name": path.relative_to(HERE).as_posix(),
                "sha256": _sha256(path),
            }
            for path in source_paths
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declaration", type=Path, default=DEFAULT_DECLARATION)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        declaration_path=args.declaration, carrier_specs=CARRIER_SPECS
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    input_paths = [args.declaration]
    for spec in CARRIER_SPECS:
        input_paths.extend([Path(spec["projectability"]), Path(spec["candidate"])])
    receipt = build_receipt(
        output=args.out, payload=payload, input_paths=input_paths
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
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
                "pooled": {
                    key: payload["evaluation"]["pooled"][key]
                    for key in (
                        "source_count",
                        "GFPC_supported_source_count",
                        "completed_source_count",
                        "channel_count",
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
