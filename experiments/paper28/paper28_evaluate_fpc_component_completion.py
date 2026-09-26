#!/usr/bin/env python3
"""Evaluate fixed-scope FPC completion with generic LocalReturn semantics.

The FPC branch declaration and complete cand2 rank-four relation are frozen
before the exact P_<=3 evaluator is opened.  The evaluator does not add any
FPC-specific continuation condition and does not read the historical Good_4
artifact or any rank-five return evaluation.
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


SCHEMA = "paper28-fpc-component-completion-v1"
RECEIPT_SCHEMA = "paper28-fpc-component-completion-receipt-v1"
DECLARATION_SCHEMA = "paper28-second-mechanism-schema-declaration-v1"
PROJECTABILITY_SCHEMA = "paper28-fixed-scope-projectability-support-separation-v1"
CANDIDATE_SCHEMA = "paper28-second-rank4-section-candidate-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_DECLARATION = (
    HERE / "results" / "paper28_second_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_PROJECTABILITY = (
    HERE
    / "results"
    / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)
DEFAULT_CANDIDATE = (
    HERE / "results" / "paper28_second_rank4_section_candidate_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_fpc_component_completion_v1.json.gz"
)

N = 7
FORBIDDEN_SUCCESS_REFINEMENTS = [
    "F_ent must participate in the next fusion",
    "H must avoid the next fusion",
    "length equals 3",
    "surplus equals 0",
    "word is p^2 d or p d^2",
    "fixed cyclic offset profile",
    "selected winner",
]
FORBIDDEN_INPUTS = [
    "paper28_second_rank4_section_return_evaluation_v1.json.gz",
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


def build_payload(
    *, declaration_path: Path, projectability_path: Path, candidate_path: Path
) -> dict[str, Any]:
    declaration = _load(declaration_path)
    projectability = _load(projectability_path)
    candidate = _load(candidate_path)

    expected = (
        (declaration, DECLARATION_SCHEMA, "FPC declaration"),
        (projectability, PROJECTABILITY_SCHEMA, "projectability"),
        (candidate, CANDIDATE_SCHEMA, "rank-four candidate"),
    )
    for payload, schema, label in expected:
        if payload.get("schema") != schema:
            raise AssertionError(f"unexpected {label} schema")
        _verify_content_digest(payload, label)

    if declaration["scope"]["success_evaluator_loaded"]:
        raise AssertionError("FPC declaration was not frozen before completion")
    if declaration["declaration"]["expanded_family"] != ["OW", "FPC"]:
        raise AssertionError("FPC declaration family drift")
    if declaration["summary"]["FPC_supported_provenances"] != 48:
        raise AssertionError("FPC support domain drift")
    if declaration["input"]["sha256"] != _sha256(projectability_path):
        raise AssertionError("FPC declaration is not bound to this projectability input")
    if projectability["inputs"]["rank4_candidate"]["sha256"] != _sha256(
        candidate_path
    ):
        raise AssertionError("projectability adapter is not bound to this relation")
    if projectability["inputs"]["rank4_candidate"][
        "content_sha256"
    ] != candidate["content_sha256"]:
        raise AssertionError("rank-four candidate content binding drift")
    if candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("rank-four relation is not the frozen pre-evaluation input")
    if candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("rank-four candidate already contains an evaluator")
    if _digest(candidate["construction"]) != candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError("rank-four construction digest mismatch")

    declaration_support = {
        str(row["context_id"]): row
        for row in declaration["declaration"]["support_rows"]
    }
    if set(declaration_support) != {
        str(row["context_id"])
        for row in projectability["projectability"]["rows"]
    }:
        raise AssertionError("FPC support and projectability domains differ")
    if not all(row["supported"] for row in declaration_support.values()):
        raise AssertionError("completion input contains an unsupported FPC provenance")

    projectability_rows = {
        str(row["context_id"]): row
        for row in projectability["projectability"]["rows"]
    }
    menu_rows = {
        str(row["source_context"]["context_id"]): row
        for row in candidate["construction"]["menus"]["contexts"]
    }
    if set(menu_rows) != set(projectability_rows):
        raise AssertionError("FPC support and frozen rank-four menu domains differ")

    for context_id, row in projectability_rows.items():
        if len(row["provenance_fiber"]) != 1:
            raise AssertionError("fixed-scope FPC completion expects singleton fibers")
        relation = row["return_certificate"]["Lambda_4"]
        if relation["construction_payload_sha256"] != candidate[
            "construction_payload_sha256"
        ]:
            raise AssertionError("fixed-scope return adapter relation drift")
        if relation["menu_sha256"] != _digest(menu_rows[context_id]):
            raise AssertionError("fixed-scope return adapter menu binding drift")

    frozen_completion_input = {
        "FPC_declaration_content_sha256": declaration["content_sha256"],
        "FPC_common_profile_payload_sha256": declaration[
            "unsupported_provenance_analysis"
        ]["common_profile_payload_sha256"],
        "projectability_payload_sha256": projectability[
            "projectability_payload_sha256"
        ],
        "rank4_construction_payload_sha256": candidate[
            "construction_payload_sha256"
        ],
        "support_rows_sha256": _digest(
            declaration["declaration"]["support_rows"]
        ),
    }
    frozen_completion_input_digest = _digest(frozen_completion_input)

    receipts = candidate["construction"]["exact_lifts"]["receipts"]
    by_id = {str(row["receipt_id"]): row for row in receipts}
    if len(by_id) != len(receipts):
        raise AssertionError("rank-four exact receipt ids are not unique")

    low_rank_by_defect: dict[tuple[int, ...], LowRankOracle] = {}

    def local_return_receipt(receipt_id: str) -> tuple[bool, int, str]:
        record = by_id[receipt_id]
        target_context = record["exact"]["target_context"]
        defect = tuple(int(value) for value in target_context["defect"])
        oracle = low_rank_by_defect.get(defect)
        if oracle is None:
            oracle = LowRankOracle(CompleteExitOracle((_cycle(N), defect), N))
            low_rank_by_defect[defect] = oracle
        target = tuple(int(value) for value in record["exact"]["target_endpoint"])
        good = oracle.is_good(target)
        return good, int(record["skeleton"]["target_rank"]), str(
            target_context["context_id"]
        )

    context_rows = []
    good_provenance_rows = []
    successful_receipt_ids: set[str] = set()
    unsuccessful_receipt_ids: set[str] = set()
    certified_target_ids: set[str] = set()
    successful_channel_count = 0
    failed_channel_count = 0
    mixed_channel_count = 0
    mixed_source_ids: set[str] = set()
    local_return_histogram: Counter[int] = Counter()

    for context_id in sorted(menu_rows):
        menu = menu_rows[context_id]
        support = declaration_support[context_id]
        projection = projectability_rows[context_id]
        provenance_row = projection["provenance_fiber"][0]
        kappa_id = str(provenance_row["kappa_4_ISE_id"])
        if kappa_id != support["kappa_4_ISE_id"]:
            raise AssertionError("FPC support provenance binding drift")

        channel_rows = []
        for channel in menu["channels"]:
            successful_ids = []
            unsuccessful_ids = []
            successful_target_ids = set()
            successful_target_ranks = set()
            for receipt_id in channel["exact_lift_ids"]:
                receipt_id = str(receipt_id)
                good, target_rank, target_id = local_return_receipt(receipt_id)
                if good:
                    successful_ids.append(receipt_id)
                    successful_receipt_ids.add(receipt_id)
                    successful_target_ids.add(target_id)
                    successful_target_ranks.add(target_rank)
                    certified_target_ids.add(target_id)
                else:
                    unsuccessful_ids.append(receipt_id)
                    unsuccessful_receipt_ids.add(receipt_id)
            channel_good = bool(successful_ids)
            if channel_good:
                successful_channel_count += 1
            else:
                failed_channel_count += 1
            if successful_ids and unsuccessful_ids:
                mixed_channel_count += 1
                mixed_source_ids.add(context_id)
            channel_rows.append(
                {
                    "channel_id": str(channel["channel_id"]),
                    "exact_lift_count": len(channel["exact_lift_ids"]),
                    "has_local_return_exact_lift": channel_good,
                    "local_return_exact_lift_count": len(successful_ids),
                    "local_return_exact_lift_ids": sorted(successful_ids),
                    "nonreturning_exact_lift_count": len(unsuccessful_ids),
                    "nonreturning_exact_lift_ids": sorted(unsuccessful_ids),
                    "local_return_target_context_ids": sorted(
                        successful_target_ids
                    ),
                    "local_return_target_ranks": sorted(successful_target_ranks),
                }
            )

        returning_channels = sum(
            1 for row in channel_rows if row["has_local_return_exact_lift"]
        )
        local_return = returning_channels > 0
        local_return_histogram[returning_channels] += 1
        good_ids = [kappa_id] if support["supported"] and local_return else []
        if good_ids:
            good_provenance_rows.append(
                {
                    "context_id": context_id,
                    "return_certificate_id": str(
                        projection["return_certificate_id"]
                    ),
                    "kappa_4_ISE_id": kappa_id,
                }
            )
        context_rows.append(
            {
                "context_id": context_id,
                "return_certificate_id": str(projection["return_certificate_id"]),
                "FPC_supported": bool(support["supported"]),
                "provenance_fiber_size": len(projection["provenance_fiber"]),
                "menu_size": int(menu["menu_size"]),
                "returning_channel_count": returning_channels,
                "nonreturning_channel_count": int(menu["menu_size"])
                - returning_channels,
                "LocalReturn_4_fs": local_return,
                "G_FPC_fs_kappa_4_ISE_ids": good_ids,
                "channels": channel_rows,
            }
        )

    exact_lift_ids = set(by_id)
    if successful_receipt_ids | unsuccessful_receipt_ids != exact_lift_ids:
        raise AssertionError("completion evaluator did not partition exact lifts")
    if successful_receipt_ids & unsuccessful_receipt_ids:
        raise AssertionError("completion evaluator assigned two statuses to a lift")
    menu_summary = candidate["construction"]["menus"]
    if successful_channel_count + failed_channel_count != int(
        menu_summary["channel_count"]
    ):
        raise AssertionError("completion evaluator did not partition channels")
    if _digest(candidate["construction"]) != candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError("completion evaluation mutated frozen construction")

    completed_source_count = sum(
        1 for row in context_rows if row["G_FPC_fs_kappa_4_ISE_ids"]
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "rank": 4,
            "section": "Sec_4,cand2^(7)",
            "component": "FPC",
            "fixed_scope_return_certificate_adapter": True,
            "all_n_claim": False,
            "winner_selected": False,
            "menu_or_lift_rebuilt": False,
            "new_census": False,
        },
        "phase_order": [
            "load_and_verify_frozen_FPC_support",
            "load_and_verify_frozen_rank4_exact_relation",
            "freeze_completion_input_digest",
            "define_generic_LocalReturn_4_fs_evaluator",
            "open_exact_P_le3_oracle",
            "evaluate_every_exact_lift_without_winner_selection",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            "FPC_declaration": _input_record(declaration_path, declaration),
            "projectability": _input_record(
                projectability_path, projectability
            ),
            "rank4_candidate": _input_record(candidate_path, candidate),
        },
        "frozen_completion_input": frozen_completion_input,
        "frozen_completion_input_sha256": frozen_completion_input_digest,
        "definition": {
            "LocalReturn_4_fs": (
                "there exist a frozen cand2 menu channel m and exact lift x in "
                "Lift_4,cand2^fs(C,m) whose theorem-facing exact target belongs "
                "to exact P_<=3^(7)"
            ),
            "G_FPC_fs": (
                "kappa belongs to the frozen P_ISE fiber, satisfies the already "
                "frozen RelevantBranch_FPC^ISE predicate, and satisfies generic "
                "LocalReturn_4^fs"
            ),
            "forbidden_success_refinements": FORBIDDEN_SUCCESS_REFINEMENTS,
        },
        "evaluation": {
            "source_count": len(context_rows),
            "FPC_supported_source_count": sum(
                1 for row in context_rows if row["FPC_supported"]
            ),
            "completed_source_count": completed_source_count,
            "hostile_source_count": len(context_rows) - completed_source_count,
            "channel_count": int(menu_summary["channel_count"]),
            "returning_channel_count": successful_channel_count,
            "nonreturning_channel_count": failed_channel_count,
            "mixed_channel_count": mixed_channel_count,
            "mixed_source_count": len(mixed_source_ids),
            "mixed_source_context_ids": sorted(mixed_source_ids),
            "exact_lift_count": len(exact_lift_ids),
            "local_return_exact_lift_count": len(successful_receipt_ids),
            "nonreturning_exact_lift_count": len(unsuccessful_receipt_ids),
            "certified_target_context_count": len(certified_target_ids),
            "returning_channel_count_histogram": {
                str(count): sources
                for count, sources in sorted(local_return_histogram.items())
            },
            "contexts": context_rows,
            "G_FPC_fs": good_provenance_rows,
        },
        "theorem": {
            "name": "FPC-FS-Completion",
            "statement": (
                "for every C in Sec_4,cand2^(7), FPCSupp_7 implies the fixed-"
                "scope good-provenance relation G_FPC^fs is nonempty"
            ),
            "holds": completed_source_count == len(context_rows),
        },
        "quantifier_audit": {
            "source_quantifier": "universal over 48 admitted cand2 sources",
            "channel_quantifier": "existential",
            "exact_lift_quantifier": "existential inside a supported channel",
            "failed_exact_lifts_retained": len(unsuccessful_receipt_ids),
            "mixed_fibers_retained": mixed_channel_count,
            "winner_selected": False,
        },
        "claim_boundary": {
            "proved": [
                "fixed-n=7 FPC component completion on Sec_4,cand2^(7)",
                "generic LocalReturn_4^fs suffices for every FPC-supported cand2 source",
                "unsuccessful exact lifts remain in the complete frozen relation",
            ],
            "not_proved": [
                "all-n FPC completion",
                "equality of the fixed-scope macro relation with Lambda_4^complete(C)",
                "a successful-path normal form for FPC",
                "universal channel or exact-lift success as a schema premise",
                "completeness of the mechanism family {OW,FPC}",
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
        HERE / "validation" / "validate_paper28_fpc_component_completion.py",
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "POST_DECLARATION_GENERIC_LOCAL_RETURN_EVALUATION",
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
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        declaration_path=args.declaration,
        projectability_path=args.projectability,
        candidate_path=args.candidate,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            output=args.out,
            payload=payload,
            input_paths=[args.declaration, args.projectability, args.candidate],
        ),
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
                **{
                    key: payload["evaluation"][key]
                    for key in (
                        "source_count",
                        "FPC_supported_source_count",
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
