#!/usr/bin/env python3
"""Audit fixed-scope ISE projectability before singleton OW support.

The audit reuses only frozen P28.5 cand2 artifacts. It reconstructs one
source-authorized rank-five-to-four provenance record over each admitted
rank-four context, freezes that projectability payload, and only then evaluates
support by the declared singleton mechanism family {OW}.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "paper28-fixed-scope-projectability-support-separation-v1"
RECEIPT_SCHEMA = (
    "paper28-fixed-scope-projectability-support-separation-receipt-v1"
)
R4_CANDIDATE_SCHEMA = "paper28-second-rank4-section-candidate-v1"
R4_AUTHORITY_SCHEMA = "paper28-second-rank4-section-return-evaluation-v1"
R5_CANDIDATE_SCHEMA = "paper28-second-rank5-section-candidate-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_R4_CANDIDATE = (
    HERE / "results" / "paper28_second_rank4_section_candidate_v1.json.gz"
)
DEFAULT_R4_AUTHORITY = (
    HERE
    / "results"
    / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_R5_CANDIDATE = (
    HERE / "results" / "paper28_second_rank5_section_candidate_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE
    / "results"
    / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)

OW_PARTITION_N7 = [4, 1, 1, 1]
DECLARED_FAMILY = ["OW"]
FORBIDDEN_INPUTS = [
    "paper28_second_rank5_section_return_evaluation_v1.json.gz",
    "Good_5",
    "target_in_lower_section",
    "successful_channel",
    "successful_exact_lift",
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


def _mass_partition(context: Mapping[str, Any]) -> list[int]:
    return sorted(
        (int(packet["mass"]) for packet in context["packets"]), reverse=True
    )


def _group_by_source(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["exact"]["source_context_id"])].append(record)
    for source_id in grouped:
        grouped[source_id].sort(key=lambda row: str(row["receipt_id"]))
    return grouped


def _selected_incoming_records(
    *,
    target_id: str,
    receipts: Sequence[Mapping[str, Any]],
    sources: Mapping[str, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    matches = []
    for receipt in receipts:
        exact = receipt["exact"]
        if str(exact["target_context"]["context_id"]) != target_id:
            continue
        source_id = str(exact["source_context_id"])
        source = sources[source_id]
        selected_word = [
            int(value) for value in source["selected_sigma5"]["selected_word"]
        ]
        if exact["words"] != [selected_word]:
            continue
        matches.append(receipt)
    return sorted(matches, key=lambda row: str(row["receipt_id"]))


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
    }


def build_payload(
    *,
    rank4_candidate_path: Path,
    rank4_authority_path: Path,
    rank5_candidate_path: Path,
) -> dict[str, Any]:
    rank4_candidate = _load(rank4_candidate_path)
    rank4_authority = _load(rank4_authority_path)
    rank5_candidate = _load(rank5_candidate_path)

    expected_schemas = (
        (rank4_candidate, R4_CANDIDATE_SCHEMA, "rank-four candidate"),
        (rank4_authority, R4_AUTHORITY_SCHEMA, "rank-four authority"),
        (rank5_candidate, R5_CANDIDATE_SCHEMA, "rank-five candidate"),
    )
    for payload, schema, label in expected_schemas:
        if payload.get("schema") != schema:
            raise AssertionError(f"unexpected {label} schema")
        _verify_content_digest(payload, label)

    if rank4_candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("rank-four relation is not the frozen pre-evaluation input")
    if rank5_candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("rank-five relation is not the frozen pre-evaluation input")
    if rank5_candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("rank-five Good evaluator was not absent")
    if _digest(rank4_candidate["construction"]) != rank4_candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError("rank-four construction digest mismatch")
    if _digest(rank5_candidate["construction"]) != rank5_candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError("rank-five construction digest mismatch")

    authority = rank4_authority["certified_lower_section"]
    if authority["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
        raise AssertionError("rank-four section authority is absent")
    if not rank4_authority["evaluation"]["all_sources_have_good_channel"]:
        raise AssertionError("rank-four authority does not cover every source")

    lower_binding = rank5_candidate["lower_section_target"]
    if lower_binding["input_sha256"] != _sha256(rank4_authority_path):
        raise AssertionError("rank-five construction is not bound to this authority")
    if lower_binding["input_content_sha256"] != rank4_authority["content_sha256"]:
        raise AssertionError("rank-five lower-authority content binding drift")

    admitted_contexts = {
        str(context["context_id"]): context for context in authority["contexts"]
    }
    if len(admitted_contexts) != 48:
        raise AssertionError("cand2 admitted rank-four context count drift")
    menu_contexts = {
        str(row["source_context"]["context_id"]): row
        for row in rank4_candidate["construction"]["menus"]["contexts"]
    }
    if set(menu_contexts) != set(admitted_contexts):
        raise AssertionError("rank-four authority and frozen relation domains differ")

    lower_keys = {
        str(row["source_context_id"]): row
        for row in lower_binding["contexts"]
    }
    if set(lower_keys) != set(admitted_contexts):
        raise AssertionError("lower-section boundary binding domain drift")

    rank4_receipts = rank4_candidate["construction"]["exact_lifts"]["receipts"]
    rank4_by_source = _group_by_source(rank4_receipts)
    if set(rank4_by_source) != set(admitted_contexts):
        raise AssertionError("rank-four local relation domain drift")

    source_rows = rank5_candidate["construction"]["source_section"]["contexts"]
    rank5_sources = {
        str(row["context"]["context_id"]): row for row in source_rows
    }
    if len(rank5_sources) != 48:
        raise AssertionError("cand2 rank-five source count drift")
    rank5_receipts = rank5_candidate["construction"]["exact_lifts"]["receipts"]

    projectability_rows = []
    used_rank5_sources: set[str] = set()
    for context_id in sorted(admitted_contexts):
        context = admitted_contexts[context_id]
        incoming = _selected_incoming_records(
            target_id=context_id,
            receipts=rank5_receipts,
            sources=rank5_sources,
        )
        if len(incoming) != 1:
            raise AssertionError(
                f"expected one source-authorized transfer into {context_id}, "
                f"found {len(incoming)}"
            )
        transfer = incoming[0]
        exact = transfer["exact"]
        source_id = str(exact["source_context_id"])
        source = rank5_sources[source_id]
        used_rank5_sources.add(source_id)

        if exact["target_context"] != context:
            raise AssertionError("cand2 handoff is not literal typed identity")
        if _mass_partition(context) != [3, 2, 1, 1]:
            raise AssertionError("cand2 rank-four partition drift")
        if source["membership_uses_lower_section_success"]:
            raise AssertionError("source selector reads lower-section success")
        if len(exact["fusion_packet_identities"]) != 1:
            raise AssertionError("selected cand2 transfer lost its single fusion")

        local_records = rank4_by_source[context_id]
        local_receipt_ids = [str(row["receipt_id"]) for row in local_records]
        menu = menu_contexts[context_id]
        return_certificate = {
            "type": "FIXED_SCOPE_CAND2_RETURN_CERTIFICATE",
            "context_id": context_id,
            "b_4": lower_keys[context_id]["section_boundary_key"],
            "chi_4": {
                "distinguished_packet": context["distinguished_packet"],
                "incoming_transfer_update": exact["ancestry_update"],
            },
            "Lambda_4": {
                "relation_kind": (
                    "frozen complete tied endpoint-shortest Type-I/II macro relation"
                ),
                "construction_payload_sha256": rank4_candidate[
                    "construction_payload_sha256"
                ],
                "source_relation_sha256": _digest(local_records),
                "receipt_count": len(local_records),
                "receipt_ids": local_receipt_ids,
                "menu_sha256": _digest(menu),
            },
            "nu_4": {
                "handoff_type": "IDENTITY",
                "exact_target_context_equals_admitted_context": True,
            },
            "authority": {
                "section": authority["name"],
                "authority_status": authority["authority_status"],
                "authority_content_sha256": rank4_authority["content_sha256"],
            },
        }
        return_certificate_id = f"kret4-{_digest(return_certificate)[:24]}"

        f4_packet = exact["ancestry_update"]["outgoing_distinguished_packet"]
        provenance = {
            "C_up": source["context"],
            "e": {
                "receipt_id": transfer["receipt_id"],
                "receipt_sha256": _digest(transfer),
                "words": exact["words"],
            },
            "Pi_up": source["context"]["packets"],
            "Pi_C": context["packets"],
            "F_4": {
                "packet": f4_packet,
                "mass": len(f4_packet),
                "terminal_fusion": exact["fusion_packet_identities"][0],
            },
            "eta": {
                "type": "IDENTITY",
                "target_context_id": context_id,
            },
            "sel": {
                "membership_authority": source["membership_authority"],
                "membership_uses_lower_section_success": False,
                "selected_sigma5": source["selected_sigma5"],
            },
        }
        provenance_id = f"kise4-{_digest(provenance)[:24]}"
        projectability_rows.append(
            {
                "context_id": context_id,
                "return_certificate_id": return_certificate_id,
                "return_certificate": return_certificate,
                "provenance_fiber": [
                    {
                        "kappa_4_ISE_id": provenance_id,
                        "kappa_4_ISE": provenance,
                    }
                ],
                "projectable": True,
                "projection_basis": (
                    "one frozen future-free selected Sigma_5 transfer receipt "
                    "with exact identity handoff into the independently admitted "
                    "rank-four context"
                ),
            }
        )

    if used_rank5_sources != set(rank5_sources):
        raise AssertionError("selected transfers do not use every frozen rank-five source")

    projectability = {
        "definition": (
            "fixed-scope instantiation of P_ISE over the independently admitted "
            "Sec_4,cand2^(7) contexts"
        ),
        "return_certificate_adapter": (
            "b_4 and chi_4 from the exact admitted context and incoming transfer; "
            "Lambda_4 from the frozen complete rank-four macro relation; nu_4 "
            "from the exact identity handoff"
        ),
        "context_count": len(projectability_rows),
        "projectable_context_count": sum(
            1 for row in projectability_rows if row["projectable"]
        ),
        "fiber_size_histogram": {"1": len(projectability_rows)},
        "rows": projectability_rows,
    }
    projectability_digest = _digest(projectability)

    support_rows = []
    for row in projectability_rows:
        context = row["return_certificate"]["b_4"]
        actual_partition = sorted(
            (int(item["mass"]) for item in context["mass_rows"]), reverse=True
        )
        ow_supported = actual_partition == OW_PARTITION_N7
        support_rows.append(
            {
                "context_id": row["context_id"],
                "return_certificate_id": row["return_certificate_id"],
                "provenance_fiber_nonempty": bool(row["provenance_fiber"]),
                "actual_partition": actual_partition,
                "ow_required_partition": OW_PARTITION_N7,
                "ow_partition_gate": ow_supported,
                "supported_mechanisms": ["OW"] if ow_supported else [],
                "singleton_support_relation_nonempty": ow_supported,
            }
        )

    projectable_unsupported = [
        row
        for row in support_rows
        if row["provenance_fiber_nonempty"]
        and not row["singleton_support_relation_nonempty"]
    ]
    if len(projectable_unsupported) != 48:
        raise AssertionError("cand2 did not produce the expected support separation")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "section": "Sec_4,cand2^(7)",
            "declared_mechanism_family": DECLARED_FAMILY,
            "new_census": False,
            "rank5_good_evaluator_loaded": False,
        },
        "phase_order": [
            "load_frozen_rank4_relation",
            "load_independent_rank4_authority",
            "load_frozen_pre_Good5_rank5_transfer_relation",
            "reconstruct_complete_fixed_scope_projectability_fibers",
            "freeze_projectability_payload_digest",
            "evaluate_singleton_OW_support",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            "rank4_candidate": _input_record(
                rank4_candidate_path, rank4_candidate
            ),
            "rank4_authority": _input_record(
                rank4_authority_path, rank4_authority
            ),
            "rank5_candidate": _input_record(
                rank5_candidate_path, rank5_candidate
            ),
        },
        "projectability": projectability,
        "projectability_payload_sha256": projectability_digest,
        "support_audit": {
            "evaluated_after_projectability_digest": True,
            "declared_family": DECLARED_FAMILY,
            "ow_support_reads": [
                "current rank-four packet partition",
                "frozen provenance-level OW branch definition",
            ],
            "rows": support_rows,
        },
        "summary": {
            "admitted_contexts": 48,
            "projectable_contexts": 48,
            "singleton_supported_contexts": 0,
            "projectable_but_unsupported_contexts": 48,
            "first_exact_witness": projectable_unsupported[0],
            "result": "SINGLETON_OW_FAMILY_INCOMPLETE_ON_CAND2",
        },
        "claim_boundary": {
            "proved": [
                "the fixed-scope cand2 provenance fiber is nonempty for every admitted source",
                "the declared singleton OW support relation is empty for every cand2 source",
                "there exists an exact projectable-but-unsupported admitted source",
            ],
            "not_proved": [
                "all-n projectability",
                "projectability for every released rank-four section",
                "failure of F5",
                "the identity or name of a second mechanism schema",
                "completeness of any enlarged mechanism family",
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
    return {
        "schema": RECEIPT_SCHEMA,
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "projectability_payload_sha256": payload[
                "projectability_payload_sha256"
            ],
        },
        "inputs": [
            {"name": path.name, "sha256": _sha256(path)} for path in input_paths
        ],
        "source_closure": {
            "script": {
                "name": Path(__file__).name,
                "sha256": _sha256(Path(__file__).resolve()),
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rank4-candidate", type=Path, default=DEFAULT_R4_CANDIDATE)
    parser.add_argument("--rank4-authority", type=Path, default=DEFAULT_R4_AUTHORITY)
    parser.add_argument("--rank5-candidate", type=Path, default=DEFAULT_R5_CANDIDATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        rank4_candidate_path=args.rank4_candidate,
        rank4_authority_path=args.rank4_authority,
        rank5_candidate_path=args.rank5_candidate,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            output=args.out,
            payload=payload,
            input_paths=[
                args.rank4_candidate,
                args.rank4_authority,
                args.rank5_candidate,
            ],
        ),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "projectability_payload_sha256": payload[
                    "projectability_payload_sha256"
                ],
                **payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
