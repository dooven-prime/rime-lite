#!/usr/bin/env python3
"""Audit {OW,FPC} support on the cand3/cand4/cand5 frozen sections.

For each independently admitted rank-four carrier, this audit reconstructs
the complete fixed-scope ISE provenance fiber from the matching pre-Good_5
rank-five relation.  It freezes the per-carrier and pooled projectability
digests before loading the declared mechanism family.  Only then does it
evaluate the already frozen OW and FPC support predicates.

No rank-five return evaluator is loaded.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "paper28-expanded-family-support-separation-v1"
RECEIPT_SCHEMA = "paper28-expanded-family-support-separation-receipt-v1"
FAMILY_SCHEMA = "paper28-second-mechanism-schema-declaration-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_FAMILY_DECLARATION = (
    RESULTS / "paper28_second_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_expanded_family_support_separation_v1.json.gz"

DECLARED_FAMILY = ["OW", "FPC"]
OW_PARTITION_N7 = [4, 1, 1, 1]
FORBIDDEN_INPUTS = [
    "paper28_third_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fourth_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fifth_rank5_section_return_evaluation_v1.json.gz",
    "Good_5",
    "Good_5_consume",
    "Good_5^non3",
    "target_in_lower_section",
    "successful_channel",
    "successful_exact_lift",
    "winning",
    "bellman",
]

CARRIER_SPECS = (
    {
        "id": "cand3",
        "section": "Sec_4,cand3^(7)",
        "expected_contexts": 36,
        "rank4_candidate_schema": "paper28-third-rank4-section-candidate-v1",
        "rank4_authority_schema": (
            "paper28-third-rank4-section-return-evaluation-v1"
        ),
        "rank5_candidate_schema": "paper28-third-rank5-section-candidate-v1",
        "rank4_candidate": (
            RESULTS / "paper28_third_rank4_section_candidate_v1.json.gz"
        ),
        "rank4_authority": (
            RESULTS
            / "paper28_third_rank4_section_return_evaluation_v1.json.gz"
        ),
        "rank5_candidate": (
            RESULTS / "paper28_third_rank5_section_candidate_v1.json.gz"
        ),
    },
    {
        "id": "cand4",
        "section": "Sec_4,cand4^(7)",
        "expected_contexts": 36,
        "rank4_candidate_schema": "paper28-fourth-rank4-section-candidate-v1",
        "rank4_authority_schema": (
            "paper28-fourth-rank4-section-return-evaluation-v1"
        ),
        "rank5_candidate_schema": "paper28-fourth-rank5-section-candidate-v1",
        "rank4_candidate": (
            RESULTS / "paper28_fourth_rank4_section_candidate_v1.json.gz"
        ),
        "rank4_authority": (
            RESULTS
            / "paper28_fourth_rank4_section_return_evaluation_v1.json.gz"
        ),
        "rank5_candidate": (
            RESULTS / "paper28_fourth_rank5_section_candidate_v1.json.gz"
        ),
    },
    {
        "id": "cand5",
        "section": "Sec_4,cand5^(7)",
        "expected_contexts": 10,
        "rank4_candidate_schema": "paper28-fifth-rank4-section-candidate-v1",
        "rank4_authority_schema": (
            "paper28-fifth-rank4-section-return-evaluation-v1"
        ),
        "rank5_candidate_schema": "paper28-fifth-rank5-section-candidate-v1",
        "rank4_candidate": (
            RESULTS / "paper28_fifth_rank4_section_candidate_v1.json.gz"
        ),
        "rank4_authority": (
            RESULTS
            / "paper28_fifth_rank4_section_return_evaluation_v1.json.gz"
        ),
        "rank5_candidate": (
            RESULTS / "paper28_fifth_rank5_section_candidate_v1.json.gz"
        ),
    },
)


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


def _packet(packet: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(int(atom) for atom in packet))


def _mass_partition(context: Mapping[str, Any]) -> list[int]:
    return sorted(
        (int(packet["mass"]) for packet in context["packets"]), reverse=True
    )


def _boundary_partition(boundary: Mapping[str, Any]) -> list[int]:
    return sorted(
        (int(row["mass"]) for row in boundary["mass_rows"]), reverse=True
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


def _build_carrier_projectability(spec: Mapping[str, Any]) -> dict[str, Any]:
    carrier_id = str(spec["id"])
    rank4_candidate_path = Path(spec["rank4_candidate"])
    rank4_authority_path = Path(spec["rank4_authority"])
    rank5_candidate_path = Path(spec["rank5_candidate"])

    rank4_candidate = _load(rank4_candidate_path)
    rank4_authority = _load(rank4_authority_path)
    rank5_candidate = _load(rank5_candidate_path)
    expected_schemas = (
        (
            rank4_candidate,
            str(spec["rank4_candidate_schema"]),
            f"{carrier_id} rank-four candidate",
        ),
        (
            rank4_authority,
            str(spec["rank4_authority_schema"]),
            f"{carrier_id} rank-four authority",
        ),
        (
            rank5_candidate,
            str(spec["rank5_candidate_schema"]),
            f"{carrier_id} rank-five candidate",
        ),
    )
    for payload, schema, label in expected_schemas:
        if payload.get("schema") != schema:
            raise AssertionError(f"unexpected {label} schema")
        _verify_content_digest(payload, label)

    if rank4_candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError(f"{carrier_id} rank-four relation is not pre-evaluation")
    if rank5_candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError(f"{carrier_id} rank-five relation is not pre-Good_5")
    if rank5_candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError(f"{carrier_id} rank-five evaluator is not absent")
    for status_key, status in rank5_candidate["scope"].items():
        if status_key.endswith("evaluation_status") and status != "NOT_RUN":
            raise AssertionError(f"{carrier_id} hostile evaluator status drift")
    if _digest(rank4_candidate["construction"]) != rank4_candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError(f"{carrier_id} rank-four construction digest mismatch")
    if _digest(rank5_candidate["construction"]) != rank5_candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError(f"{carrier_id} rank-five construction digest mismatch")

    authority_input = rank4_authority["input"]
    if authority_input["sha256"] != _sha256(rank4_candidate_path):
        raise AssertionError(f"{carrier_id} rank-four authority input drift")
    if authority_input["content_sha256"] != rank4_candidate["content_sha256"]:
        raise AssertionError(f"{carrier_id} rank-four authority content drift")
    authority = rank4_authority["certified_lower_section"]
    if authority["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
        raise AssertionError(f"{carrier_id} rank-four authority is absent")
    if not rank4_authority["evaluation"]["all_sources_have_good_channel"]:
        raise AssertionError(f"{carrier_id} authority does not cover every source")

    lower_binding = rank5_candidate["lower_section_target"]
    if lower_binding["input_sha256"] != _sha256(rank4_authority_path):
        raise AssertionError(f"{carrier_id} rank-five lower authority binding drift")
    if lower_binding["input_content_sha256"] != rank4_authority["content_sha256"]:
        raise AssertionError(f"{carrier_id} lower authority content binding drift")

    admitted_contexts = {
        str(context["context_id"]): context for context in authority["contexts"]
    }
    expected_count = int(spec["expected_contexts"])
    if len(admitted_contexts) != expected_count:
        raise AssertionError(f"{carrier_id} admitted context count drift")
    menu_contexts = {
        str(row["source_context"]["context_id"]): row
        for row in rank4_candidate["construction"]["menus"]["contexts"]
    }
    if set(menu_contexts) != set(admitted_contexts):
        raise AssertionError(f"{carrier_id} frozen rank-four domain drift")
    lower_keys = {
        str(row["source_context_id"]): row
        for row in lower_binding["contexts"]
    }
    if set(lower_keys) != set(admitted_contexts):
        raise AssertionError(f"{carrier_id} lower-section key domain drift")

    rank4_receipts = rank4_candidate["construction"]["exact_lifts"]["receipts"]
    rank4_by_source = _group_by_source(rank4_receipts)
    if set(rank4_by_source) != set(admitted_contexts):
        raise AssertionError(f"{carrier_id} rank-four relation domain drift")

    source_rows = rank5_candidate["construction"]["source_section"]["contexts"]
    rank5_sources = {
        str(row["context"]["context_id"]): row for row in source_rows
    }
    if len(rank5_sources) != expected_count:
        raise AssertionError(f"{carrier_id} rank-five source count drift")
    rank5_receipts = rank5_candidate["construction"]["exact_lifts"]["receipts"]

    projectability_rows = []
    used_rank5_sources: set[str] = set()
    fiber_histogram: Counter[int] = Counter()
    for context_id in sorted(admitted_contexts):
        context = admitted_contexts[context_id]
        incoming = _selected_incoming_records(
            target_id=context_id,
            receipts=rank5_receipts,
            sources=rank5_sources,
        )
        if not incoming:
            raise AssertionError(f"{carrier_id} has no provenance into {context_id}")

        local_records = rank4_by_source[context_id]
        menu = menu_contexts[context_id]
        return_certificate = {
            "type": f"FIXED_SCOPE_{carrier_id.upper()}_RETURN_CERTIFICATE",
            "context_id": context_id,
            "b_4": lower_keys[context_id]["section_boundary_key"],
            "chi_4": {
                "distinguished_packet": context["distinguished_packet"],
                "incoming_transfer_updates": [
                    receipt["exact"]["ancestry_update"] for receipt in incoming
                ],
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
                "receipt_ids": [str(row["receipt_id"]) for row in local_records],
                "menu_sha256": _digest(menu),
            },
            "nu_4": {
                "handoff_type": "IDENTITY",
                "all_exact_targets_equal_admitted_context": all(
                    receipt["exact"]["target_context"] == context
                    for receipt in incoming
                ),
            },
            "authority": {
                "section": authority["name"],
                "authority_status": authority["authority_status"],
                "authority_content_sha256": rank4_authority["content_sha256"],
            },
        }
        if not return_certificate["nu_4"][
            "all_exact_targets_equal_admitted_context"
        ]:
            raise AssertionError(f"{carrier_id} handoff identity drift")
        return_certificate_id = f"kret4-{_digest(return_certificate)[:24]}"

        provenance_fiber = []
        for transfer in incoming:
            exact = transfer["exact"]
            source_id = str(exact["source_context_id"])
            source = rank5_sources[source_id]
            used_rank5_sources.add(source_id)
            if source["membership_uses_lower_section_success"]:
                raise AssertionError(f"{carrier_id} source selector reads success")
            if len(exact["fusion_packet_identities"]) != 1:
                raise AssertionError(f"{carrier_id} selected transfer fusion drift")
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
                "ancestry_update": exact["ancestry_update"],
                "sel": {
                    "membership_authority": source["membership_authority"],
                    "membership_uses_lower_section_success": False,
                    "selected_sigma5": source["selected_sigma5"],
                },
            }
            provenance_fiber.append(
                {
                    "kappa_4_ISE_id": f"kise4-{_digest(provenance)[:24]}",
                    "kappa_4_ISE": provenance,
                }
            )
        provenance_fiber.sort(key=lambda row: str(row["kappa_4_ISE_id"]))
        fiber_histogram[len(provenance_fiber)] += 1
        projectability_rows.append(
            {
                "carrier_id": carrier_id,
                "context_id": context_id,
                "return_certificate_id": return_certificate_id,
                "return_certificate": return_certificate,
                "provenance_fiber": provenance_fiber,
                "projectable": True,
                "projection_basis": (
                    "complete set of frozen future-free selected Sigma_5 transfer "
                    "receipts with exact typed handoff into the independently "
                    "admitted rank-four context"
                ),
            }
        )

    if used_rank5_sources != set(rank5_sources):
        raise AssertionError(f"{carrier_id} selected transfers do not use every source")

    projectability = {
        "carrier_id": carrier_id,
        "section": spec["section"],
        "definition": (
            "fixed-scope P_ISE reconstructed from the frozen pre-Good_5 transfer "
            "relation over independently admitted rank-four contexts"
        ),
        "context_count": len(projectability_rows),
        "projectable_context_count": len(projectability_rows),
        "fiber_size_histogram": {
            str(size): count for size, count in sorted(fiber_histogram.items())
        },
        "rows": projectability_rows,
    }
    projectability_digest = _digest(projectability)
    return {
        "carrier_id": carrier_id,
        "section": spec["section"],
        "inputs": {
            "rank4_candidate": _input_record(rank4_candidate_path, rank4_candidate),
            "rank4_authority": _input_record(rank4_authority_path, rank4_authority),
            "rank5_candidate": _input_record(rank5_candidate_path, rank5_candidate),
        },
        "projectability": projectability,
        "projectability_payload_sha256": projectability_digest,
    }


def _fpc_clause_audit(row: Mapping[str, Any], provenance: Mapping[str, Any]) -> dict[str, Any]:
    return_certificate = row["return_certificate"]
    context_up = provenance["C_up"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    f_entry = provenance["F_4"]
    fusion = f_entry["terminal_fusion"]
    ancestry = provenance["ancestry_update"]
    ambient_n = int(context_up["ambient_n"])

    up_packets = {_packet(packet["packet"]): packet for packet in pi_up}
    current_packets = {
        _packet(packet["packet"]): packet for packet in pi_current
    }
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    parent_union = tuple(sorted(atom for parent in parents for atom in parent))
    f_packet = _packet(f_entry["packet"])
    incoming = _packet(ancestry["incoming_distinguished_packet"])
    outgoing = _packet(ancestry["outgoing_distinguished_packet"])
    current_distinguished = _packet(
        return_certificate["chi_4"]["distinguished_packet"]
    )
    expected_current = (set(up_packets) - parent_set) | {f_packet}
    selected_word = [
        int(value) for value in provenance["sel"]["selected_sigma5"]["selected_word"]
    ]

    clauses = {
        "current_partition_is_n_minus_4_211": _mass_partition(
            {"packets": pi_current}
        )
        == [ambient_n - 4, 2, 1, 1],
        "source_partition_is_n_minus_4_1111": _mass_partition(
            {"packets": pi_up}
        )
        == [ambient_n - 4, 1, 1, 1, 1],
        "pi_up_equals_source_packets": pi_up == context_up["packets"],
        "incoming_distinguished_is_source_distinguished": incoming
        == _packet(context_up["distinguished_packet"]),
        "incoming_distinguished_has_mass_n_minus_4": len(incoming)
        == ambient_n - 4,
        "incoming_distinguished_survives_atomwise": incoming in current_packets,
        "incoming_distinguished_not_fused": incoming not in parent_set,
        "incoming_participation_is_none": ancestry["participation_type"] == "NONE",
        "terminal_parents_are_distinct_source_singletons": len(parent_set) == 2
        and all(parent in up_packets and len(parent) == 1 for parent in parents),
        "terminal_result_is_parent_union": f_packet == parent_union,
        "terminal_result_has_mass_two": int(f_entry["mass"])
        == len(f_packet)
        == 2,
        "terminal_result_is_outgoing_distinguished": f_packet == outgoing,
        "terminal_result_is_current_distinguished": f_packet
        == current_distinguished,
        "current_packet_partition_is_exact_replay": set(current_packets)
        == expected_current,
        "selected_word_is_exact_transfer_word": provenance["e"]["words"]
        == [selected_word],
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
        "handoff_certifies_role_transport": provenance["eta"][
            "target_context_id"
        ]
        == row["context_id"]
        and f_packet in current_packets,
    }
    return {
        "clauses": clauses,
        "failed_clauses": [key for key, value in clauses.items() if not value],
        "supported": all(clauses.values()),
        "source_partition": _mass_partition({"packets": pi_up}),
        "current_partition": _mass_partition({"packets": pi_current}),
        "terminal_parent_masses": sorted(len(parent) for parent in parents),
        "terminal_result_mass": len(f_packet),
        "incoming_participation_type": ancestry["participation_type"],
        "selected_length": int(
            provenance["sel"]["selected_sigma5"]["total_length"]
        ),
        "selected_surplus": int(
            provenance["sel"]["selected_sigma5"]["total_surplus"]
        ),
    }


def build_payload(
    *,
    carrier_specs: Sequence[Mapping[str, Any]] = CARRIER_SPECS,
    family_declaration_path: Path = DEFAULT_FAMILY_DECLARATION,
) -> dict[str, Any]:
    # Phase one deliberately does not load the mechanism declaration.
    carrier_projectability = [
        _build_carrier_projectability(spec) for spec in carrier_specs
    ]
    pooled_projectability = {
        "definition": (
            "tagged disjoint union of the cand3, cand4, and cand5 fixed-scope "
            "ISE projectability relations"
        ),
        "carrier_projectability_digests": {
            row["carrier_id"]: row["projectability_payload_sha256"]
            for row in carrier_projectability
        },
        "carriers": [row["projectability"] for row in carrier_projectability],
    }
    pooled_projectability_digest = _digest(pooled_projectability)

    # Phase two starts only after the complete projectability digest is frozen.
    family = _load(family_declaration_path)
    if family.get("schema") != FAMILY_SCHEMA:
        raise AssertionError("unexpected mechanism-family declaration schema")
    _verify_content_digest(family, "mechanism-family declaration")
    if family["declaration"]["expanded_family"] != DECLARED_FAMILY:
        raise AssertionError("declared mechanism family drift")
    if family["scope"]["success_evaluator_loaded"]:
        raise AssertionError("mechanism declaration loaded a success evaluator")

    support_carriers = []
    pooled_support_rows = []
    for carrier in carrier_projectability:
        support_rows = []
        failure_histogram: Counter[str] = Counter()
        for row in carrier["projectability"]["rows"]:
            boundary_partition = _boundary_partition(row["return_certificate"]["b_4"])
            ow_partition_gate = boundary_partition == OW_PARTITION_N7
            provenance_support = []
            for provenance_row in row["provenance_fiber"]:
                provenance = provenance_row["kappa_4_ISE"]
                fpc_audit = _fpc_clause_audit(row, provenance)
                for clause in fpc_audit["failed_clauses"]:
                    failure_histogram[clause] += 1
                supported = []
                if ow_partition_gate:
                    supported.append("OW")
                if fpc_audit["supported"]:
                    supported.append("FPC")
                provenance_support.append(
                    {
                        "kappa_4_ISE_id": provenance_row["kappa_4_ISE_id"],
                        "ow": {
                            "necessary_partition_gate": ow_partition_gate,
                            "required_partition": OW_PARTITION_N7,
                            "actual_partition": boundary_partition,
                            "remaining_clauses": (
                                "NOT_EVALUATED_BECAUSE_NECESSARY_GATE_FAILED"
                                if not ow_partition_gate
                                else "NOT_IN_SCOPE_OF_THIS_HOSTILE_AUDIT"
                            ),
                            "supported": False if not ow_partition_gate else None,
                        },
                        "fpc": fpc_audit,
                        "supported_mechanisms": supported,
                    }
                )
            supported_mechanisms = sorted(
                {
                    mechanism
                    for provenance_row in provenance_support
                    for mechanism in provenance_row["supported_mechanisms"]
                }
            )
            support_row = {
                "carrier_id": carrier["carrier_id"],
                "context_id": row["context_id"],
                "return_certificate_id": row["return_certificate_id"],
                "provenance_fiber_nonempty": bool(row["provenance_fiber"]),
                "provenance_support": provenance_support,
                "supported_mechanisms": supported_mechanisms,
                "expanded_family_support_relation_nonempty": bool(
                    supported_mechanisms
                ),
            }
            support_rows.append(support_row)
            pooled_support_rows.append(support_row)

        supported_contexts = sum(
            1
            for row in support_rows
            if row["expanded_family_support_relation_nonempty"]
        )
        support_carriers.append(
            {
                "carrier_id": carrier["carrier_id"],
                "section": carrier["section"],
                "context_count": len(support_rows),
                "supported_context_count": supported_contexts,
                "projectable_but_unsupported_context_count": (
                    len(support_rows) - supported_contexts
                ),
                "fpc_failed_clause_histogram": dict(sorted(failure_histogram.items())),
                "rows": support_rows,
            }
        )

    projectable_contexts = sum(
        row["projectability"]["projectable_context_count"]
        for row in carrier_projectability
    )
    supported_contexts = sum(
        1
        for row in pooled_support_rows
        if row["expanded_family_support_relation_nonempty"]
    )
    expected_total = sum(int(spec["expected_contexts"]) for spec in carrier_specs)
    if projectable_contexts != expected_total:
        raise AssertionError("pooled projectability count drift")
    if supported_contexts != 0:
        raise AssertionError("{OW,FPC} unexpectedly supports the hostile union")

    first_witnesses = {}
    for carrier in support_carriers:
        unsupported = [
            row
            for row in carrier["rows"]
            if row["provenance_fiber_nonempty"]
            and not row["expanded_family_support_relation_nonempty"]
        ]
        if not unsupported:
            raise AssertionError(f"{carrier['carrier_id']} lacks a support hostile")
        first_witnesses[carrier["carrier_id"]] = unsupported[0]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "sections": [str(spec["section"]) for spec in carrier_specs],
            "declared_mechanism_family": DECLARED_FAMILY,
            "new_census": False,
            "rank5_good_evaluator_loaded": False,
        },
        "phase_order": [
            "load_each_frozen_rank4_relation_and_independent_rank4_authority",
            "load_each_matching_frozen_pre_Good5_rank5_transfer_relation",
            "reconstruct_complete_fixed_scope_projectability_fibers",
            "freeze_per_carrier_projectability_digests",
            "freeze_pooled_projectability_digest",
            "load_frozen_OW_FPC_family_declaration",
            "evaluate_OW_and_FPC_support",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "projectability_inputs": {
            row["carrier_id"]: row["inputs"] for row in carrier_projectability
        },
        "family_declaration_input": _input_record(
            family_declaration_path, family
        ),
        "projectability": pooled_projectability,
        "projectability_payload_sha256": pooled_projectability_digest,
        "support_audit": {
            "evaluated_after_projectability_digest": True,
            "declared_family": DECLARED_FAMILY,
            "family_declaration_content_sha256": family["content_sha256"],
            "ow_support_rule": (
                "the frozen OW branch has necessary current partition "
                "(n-3,1,1,1); deeper clauses are not read after that gate fails"
            ),
            "fpc_support_rule": family["declaration"]["branch_formula"],
            "carriers": support_carriers,
        },
        "summary": {
            "admitted_contexts": expected_total,
            "projectable_contexts": projectable_contexts,
            "OW_supported_contexts": 0,
            "FPC_supported_contexts": 0,
            "expanded_family_supported_contexts": supported_contexts,
            "projectable_but_unsupported_contexts": (
                projectable_contexts - supported_contexts
            ),
            "by_carrier": {
                carrier["carrier_id"]: {
                    "admitted": carrier["context_count"],
                    "projectable": carrier["context_count"],
                    "supported_by_expanded_family": carrier[
                        "supported_context_count"
                    ],
                    "projectable_but_unsupported": carrier[
                        "projectable_but_unsupported_context_count"
                    ],
                }
                for carrier in support_carriers
            },
            "first_exact_witness_by_carrier": first_witnesses,
            "result": "EXPANDED_OW_FPC_FAMILY_INCOMPLETE_ON_CAND3_CAND4_CAND5",
        },
        "next_gate": {
            "name": "P28.6u-A2",
            "input_domain": (
                "tagged union of all exact projectable-but-unsupported cand3, "
                "cand4, and cand5 provenances"
            ),
            "order": [
                "pool_unsupported_projectable_provenances",
                "extract_cross_carrier_source_local_commonality",
                "freeze_future_free_RelevantBranch_g2",
                "only_then_name_g2",
            ],
            "candidate_commonality_not_yet_a_schema": (
                "exact 1+2 terminal fusion creates the current distinguished "
                "mass-three packet while another mass-two packet is transported"
            ),
        },
        "claim_boundary": {
            "proved": [
                "all 82 admitted fixed-scope sources have nonempty reconstructed ISE provenance fibers",
                "the frozen family {OW,FPC} supports none of those 82 sources",
                "each of cand3, cand4, and cand5 supplies an exact projectable-but-unsupported source",
                "the declared family is incomplete on the tagged union of these fixed scopes",
            ],
            "not_proved": [
                "failure of F5 on any source",
                "the identity, name, or completion theorem of a third mechanism schema",
                "all-n projectability or support cover",
                "all-n FPC component completion",
                "equality of the fixed-scope rank-four adapter with Lambda_4^complete(C)",
                "that fresh participation, length, surplus, or offset geometry belongs to the next branch key",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    carrier_specs: Sequence[Mapping[str, Any]],
    family_declaration_path: Path,
) -> dict[str, Any]:
    input_paths = []
    for spec in carrier_specs:
        input_paths.extend(
            [
                Path(spec["rank4_candidate"]),
                Path(spec["rank4_authority"]),
                Path(spec["rank5_candidate"]),
            ]
        )
    input_paths.append(family_declaration_path)
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
    parser.add_argument(
        "--family-declaration", type=Path, default=DEFAULT_FAMILY_DECLARATION
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        carrier_specs=CARRIER_SPECS,
        family_declaration_path=args.family_declaration,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            output=args.out,
            payload=payload,
            carrier_specs=CARRIER_SPECS,
            family_declaration_path=args.family_declaration,
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
