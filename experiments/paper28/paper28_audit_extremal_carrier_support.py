#!/usr/bin/env python3
"""Audit {OW,FPC,PEC} support on the extremal n=7 rank-four section.

The projectability phase reads the independently admitted extremal rank-four
section and the frozen pre-Good_5 first rank-five transfer relation.  It binds
each exact target to the theorem-facing section context through a verified
atom bijection and freezes the complete projectability payload before loading
the declared mechanism family.

The historical rank-five Good evaluator is not loaded.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "paper28-extremal-carrier-support-separation-v1"
RECEIPT_SCHEMA = "paper28-extremal-carrier-support-separation-receipt-v1"
R4_AUTHORITY_SCHEMA = "paper28-section-return-menu-audit-v1"
R5_CANDIDATE_SCHEMA = "paper28-rank5-section-return-candidate-v1"
FAMILY_SCHEMA = "paper28-third-mechanism-schema-declaration-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_R4_AUTHORITY = RESULTS / "paper28_section_return_menu_audit_v1.json.gz"
DEFAULT_R5_CANDIDATE = RESULTS / "paper28_rank5_section_candidate_v1.json.gz"
DEFAULT_FAMILY_DECLARATION = (
    RESULTS / "paper28_third_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_extremal_carrier_support_separation_v1.json.gz"

DECLARED_FAMILY = ["OW", "FPC", "PEC"]
OW_PARTITION_N7 = [4, 1, 1, 1]
FORBIDDEN_INPUTS = [
    "paper28_rank5_section_return_evaluation_v1.json.gz",
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


def _packet(packet: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(int(atom) for atom in packet))


def _partition(packets: Sequence[Mapping[str, Any]]) -> list[int]:
    return sorted((int(row["mass"]) for row in packets), reverse=True)


def _boundary_partition(boundary: Mapping[str, Any]) -> list[int]:
    return sorted(
        (int(row["mass"]) for row in boundary["mass_rows"]), reverse=True
    )


def _boundary_key(context: Mapping[str, Any]) -> dict[str, Any]:
    distinguished = _packet(context["distinguished_packet"])
    distinguished_rows = [
        row for row in context["packets"] if _packet(row["packet"]) == distinguished
    ]
    if len(distinguished_rows) != 1:
        raise AssertionError("distinguished packet does not have one coordinate")
    distinguished_coordinate = int(distinguished_rows[0]["coordinate"])
    ambient_n = int(context["ambient_n"])
    mass_rows = [
        {
            "coordinate": int(row["coordinate"]),
            "mass": int(row["mass"]),
            "offset_from_distinguished": (
                int(row["coordinate"]) - distinguished_coordinate
            )
            % ambient_n,
            "is_distinguished": _packet(row["packet"]) == distinguished,
        }
        for row in context["packets"]
    ]
    mass_rows.sort(key=lambda row: row["coordinate"])
    return {
        "ambient_n": ambient_n,
        "defect": [int(value) for value in context["defect"]],
        "rank": len(context["packets"]),
        "distinguished_coordinate": distinguished_coordinate,
        "distinguished_mass": len(distinguished),
        "mass_rows": mass_rows,
    }


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
    }


def _group_receipts_by_boundary(
    receipts: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        key = receipt["exact"]["target_channel"]["section_boundary_key"]
        grouped[_digest(key)].append(receipt)
    for key in grouped:
        grouped[key].sort(key=lambda row: str(row["receipt_id"]))
    return grouped


def _exact_role_handoff(
    *, theorem_context: Mapping[str, Any], actual_context: Mapping[str, Any]
) -> dict[str, Any]:
    if theorem_context["defect"] != actual_context["defect"]:
        raise AssertionError("atom handoff changed the rooted action")
    theorem_by_coordinate = {
        int(row["coordinate"]): row for row in theorem_context["packets"]
    }
    actual_by_coordinate = {
        int(row["coordinate"]): row for row in actual_context["packets"]
    }
    if set(theorem_by_coordinate) != set(actual_by_coordinate):
        raise AssertionError("atom handoff changed occupied coordinates")

    theorem_to_actual: dict[int, int] = {}
    role_rows = []
    for coordinate in sorted(theorem_by_coordinate):
        theorem_packet = sorted(
            int(value) for value in theorem_by_coordinate[coordinate]["packet"]
        )
        actual_packet = sorted(
            int(value) for value in actual_by_coordinate[coordinate]["packet"]
        )
        if len(theorem_packet) != len(actual_packet):
            raise AssertionError("atom handoff changed a packet mass")
        for theorem_atom, actual_atom in zip(
            theorem_packet, actual_packet, strict=True
        ):
            theorem_to_actual[theorem_atom] = actual_atom
        role_rows.append(
            {
                "coordinate": coordinate,
                "theorem_packet": theorem_packet,
                "actual_packet": actual_packet,
                "mass": len(theorem_packet),
                "is_distinguished": _packet(
                    theorem_by_coordinate[coordinate]["packet"]
                )
                == _packet(theorem_context["distinguished_packet"]),
            }
        )
    ambient_n = int(theorem_context["ambient_n"])
    if set(theorem_to_actual) != set(range(ambient_n)):
        raise AssertionError("theorem-side handoff atoms are not complete")
    if set(theorem_to_actual.values()) != set(range(ambient_n)):
        raise AssertionError("actual-side handoff atoms are not bijective")
    actual_to_theorem = {
        actual: theorem for theorem, actual in theorem_to_actual.items()
    }
    mapped_distinguished = sorted(
        theorem_to_actual[int(value)]
        for value in theorem_context["distinguished_packet"]
    )
    if mapped_distinguished != sorted(actual_context["distinguished_packet"]):
        raise AssertionError("atom handoff changed distinguished ancestry")
    is_identity = all(source == target for source, target in theorem_to_actual.items())
    return {
        "type": "ATOM_BIJECTION",
        "theorem_context_id": str(theorem_context["context_id"]),
        "actual_target_context_id": str(actual_context["context_id"]),
        "theorem_to_actual_atom_bijection": [
            {"theorem_atom": source, "actual_atom": target}
            for source, target in sorted(theorem_to_actual.items())
        ],
        "actual_to_theorem_atom_bijection": [
            {"actual_atom": source, "theorem_atom": target}
            for source, target in sorted(actual_to_theorem.items())
        ],
        "role_packet_correspondence": role_rows,
        "distinguished_packet_preserved": True,
        "literal_atom_identity": is_identity,
    }


def _actual_to_theorem_packet(
    packet: Sequence[int], eta: Mapping[str, Any]
) -> tuple[int, ...]:
    atom_map = {
        int(row["actual_atom"]): int(row["theorem_atom"])
        for row in eta["actual_to_theorem_atom_bijection"]
    }
    return tuple(sorted(atom_map[int(atom)] for atom in packet))


def _build_projectability(
    *, rank4_authority_path: Path, rank5_candidate_path: Path
) -> dict[str, Any]:
    rank4_authority = _load(rank4_authority_path)
    rank5_candidate = _load(rank5_candidate_path)
    if rank4_authority.get("schema") != R4_AUTHORITY_SCHEMA:
        raise AssertionError("unexpected extremal rank-four authority schema")
    if rank5_candidate.get("schema") != R5_CANDIDATE_SCHEMA:
        raise AssertionError("unexpected first rank-five candidate schema")
    _verify_content_digest(rank4_authority, "extremal rank-four authority")
    _verify_content_digest(rank5_candidate, "first rank-five candidate")

    authority = rank4_authority["success_certification"]
    if not authority["all_declared_sources_have_successful_channel"]:
        raise AssertionError("extremal rank-four authority is absent")
    if rank4_authority["scope"]["declared_section_context_count"] != 35:
        raise AssertionError("extremal authority context count drift")
    if rank5_candidate["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("first rank-five relation is not pre-Good_5")
    if rank5_candidate["evaluator"]["status"] != "ABSENT_BY_DESIGN":
        raise AssertionError("first rank-five evaluator is not absent")
    if _digest(rank5_candidate["construction"]) != rank5_candidate[
        "construction_payload_sha256"
    ]:
        raise AssertionError("first rank-five construction digest mismatch")

    menu = rank4_authority["future_free_menu"]
    if _digest(menu) != rank4_authority["future_free_menu_content_sha256"]:
        raise AssertionError("extremal rank-four menu digest mismatch")
    menu_contexts = {
        str(row["source_context"]["context_id"]): row
        for row in menu["contexts"]
    }
    if len(menu_contexts) != 35:
        raise AssertionError("extremal rank-four menu domain drift")

    lower_rows = rank5_candidate["lower_section_target"]["contexts"]
    lower_by_key = {
        _digest(row["section_boundary_key"]): row for row in lower_rows
    }
    if len(lower_by_key) != 35:
        raise AssertionError("extremal lower-section key domain drift")
    if rank5_candidate["lower_section_target"]["section_keys_sha256"] != _digest(
        [row["section_boundary_key"] for row in lower_rows]
    ):
        raise AssertionError("extremal lower-section key digest drift")

    theorem_context_by_key: dict[str, Mapping[str, Any]] = {}
    menu_by_key: dict[str, Mapping[str, Any]] = {}
    for menu_row in menu_contexts.values():
        context = menu_row["source_context"]
        key_digest = _digest(_boundary_key(context))
        if key_digest not in lower_by_key:
            raise AssertionError("rank-four authority context lacks section key")
        if key_digest in theorem_context_by_key:
            raise AssertionError("rank-four section key is not unique")
        theorem_context_by_key[key_digest] = context
        menu_by_key[key_digest] = menu_row
    if set(theorem_context_by_key) != set(lower_by_key):
        raise AssertionError("authority and lower-section key domains differ")

    source_rows = rank5_candidate["construction"]["source_section"]["contexts"]
    rank5_sources = {
        str(row["context"]["context_id"]): row for row in source_rows
    }
    receipts = rank5_candidate["construction"]["exact_lifts"]["receipts"]
    receipts_by_boundary = _group_receipts_by_boundary(receipts)

    rows = []
    fiber_histogram: Counter[int] = Counter()
    handoff_histogram: Counter[str] = Counter()
    used_receipts: set[str] = set()
    used_sources: set[str] = set()
    for key_digest in sorted(theorem_context_by_key):
        theorem_context = theorem_context_by_key[key_digest]
        menu_row = menu_by_key[key_digest]
        incoming = receipts_by_boundary.get(key_digest, [])
        if not incoming:
            raise AssertionError("admitted ext context has no exact provenance")

        return_certificate = {
            "type": "FIXED_SCOPE_EXT_RETURN_CERTIFICATE",
            "context_id": str(theorem_context["context_id"]),
            "b_4": _boundary_key(theorem_context),
            "chi_4": {
                "distinguished_packet": theorem_context["distinguished_packet"],
                "incoming_transfer_update_count": len(incoming),
            },
            "Lambda_4": {
                "relation_kind": (
                    "frozen future-free extremal skeleton menu with exact-lift IDs"
                ),
                "future_free_menu_content_sha256": rank4_authority[
                    "future_free_menu_content_sha256"
                ],
                "source_menu_sha256": _digest(menu_row),
                "menu_size": int(menu_row["menu_size"]),
                "channel_ids": [
                    str(channel["channel_id"]) for channel in menu_row["channels"]
                ],
                "exact_lift_ids": sorted(
                    str(receipt_id)
                    for channel in menu_row["channels"]
                    for receipt_id in channel["exact_lift_ids"]
                ),
            },
            "nu_4": {
                "handoff_type": "ATOM_BIJECTION",
                "section_boundary_key_sha256": key_digest,
            },
            "authority": {
                "section": "Sec_4,ext^(7)",
                "authority_status": "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION",
                "authority_content_sha256": rank4_authority["content_sha256"],
            },
        }
        return_certificate_id = f"kret4-{_digest(return_certificate)[:24]}"

        provenance_fiber = []
        for transfer in incoming:
            exact = transfer["exact"]
            source_id = str(exact["source_context_id"])
            source = rank5_sources[source_id]
            if source["excluded"]:
                raise AssertionError("excluded rank-five source entered provenance")
            if len(exact["fusion_packet_identities"]) != 1:
                raise AssertionError("ext transfer fusion count drift")
            actual_context = exact["target_context"]
            eta = _exact_role_handoff(
                theorem_context=theorem_context,
                actual_context=actual_context,
            )
            handoff_histogram[eta["type"]] += 1
            if eta["literal_atom_identity"]:
                raise AssertionError("ext handoff unexpectedly became literal identity")
            outgoing_actual = exact["ancestry_update"][
                "outgoing_distinguished_packet"
            ]
            outgoing_theorem = _actual_to_theorem_packet(outgoing_actual, eta)
            if outgoing_theorem != _packet(theorem_context["distinguished_packet"]):
                raise AssertionError("handoff does not transport outgoing ancestry")

            corridor = transfer["accounting"]["corridors"]
            if len(corridor) != 1:
                raise AssertionError("ext transfer corridor count drift")
            provenance = {
                "C_up": source["context"],
                "e": {
                    "receipt_id": str(transfer["receipt_id"]),
                    "receipt_sha256": _digest(transfer),
                    "words": exact["words"],
                },
                "Pi_up": source["context"]["packets"],
                "Pi_target_actual": actual_context["packets"],
                "Pi_C": theorem_context["packets"],
                "F_4": {
                    "actual_packet": outgoing_actual,
                    "theorem_facing_packet": list(outgoing_theorem),
                    "mass": len(outgoing_actual),
                    "terminal_fusion": exact["fusion_packet_identities"][0],
                },
                "eta": eta,
                "ancestry_update": exact["ancestry_update"],
                "sel": {
                    "membership_authority": (
                        "future-free rank-five action-local carrier plus exact "
                        "typed-boundary projectability"
                    ),
                    "membership_uses_lower_section_success": False,
                    "projectability_uses_rank5_good_evaluator": False,
                    "sigma6_selection_rule": source["sigma6_selection_rule"],
                    "sigma6_selected_word": source["sigma6_selected_word"],
                    "selected_sigma5": {
                        "selected_word": exact["words"][0],
                        "total_length": int(corridor[0]["length"]),
                        "total_surplus": int(corridor[0]["surplus"]),
                        "selection_basis": (
                            "complete pre-Good_5 exact receipt fiber with target "
                            "typed boundary equal to the admitted section key"
                        ),
                    },
                },
            }
            provenance_fiber.append(
                {
                    "kappa_4_ISE_id": f"kise4-{_digest(provenance)[:24]}",
                    "kappa_4_ISE": provenance,
                }
            )
            used_receipts.add(str(transfer["receipt_id"]))
            used_sources.add(source_id)
        provenance_fiber.sort(key=lambda row: str(row["kappa_4_ISE_id"]))
        fiber_histogram[len(provenance_fiber)] += 1
        rows.append(
            {
                "carrier_id": "ext",
                "context_id": str(theorem_context["context_id"]),
                "return_certificate_id": return_certificate_id,
                "return_certificate": return_certificate,
                "provenance_fiber": provenance_fiber,
                "projectable": True,
                "projection_basis": (
                    "complete pre-Good_5 exact transfer receipts matched by the "
                    "released section boundary key with verified atom-bijection "
                    "handoff to the theorem-facing context"
                ),
            }
        )

    if len(used_receipts) != 35 or len(used_sources) != 35:
        raise AssertionError("ext projectability does not use 35 transfers/sources")
    projectability = {
        "carrier_id": "ext",
        "section": "Sec_4,ext^(7)",
        "definition": (
            "fixed-scope P_ISE reconstructed from the frozen pre-Good_5 first "
            "rank-five transfer relation and atom-bijection handoff into the "
            "independently admitted extremal rank-four section"
        ),
        "context_count": len(rows),
        "projectable_context_count": len(rows),
        "fiber_size_histogram": {
            str(size): count for size, count in sorted(fiber_histogram.items())
        },
        "handoff_type_histogram": dict(sorted(handoff_histogram.items())),
        "rows": sorted(rows, key=lambda row: str(row["context_id"])),
    }
    return {
        "inputs": {
            "rank4_authority": _input_record(rank4_authority_path, rank4_authority),
            "rank5_candidate": _input_record(rank5_candidate_path, rank5_candidate),
        },
        "projectability": projectability,
        "projectability_payload_sha256": _digest(projectability),
    }


def _map_actual_packets(
    packets: Sequence[Mapping[str, Any]], eta: Mapping[str, Any]
) -> set[tuple[int, ...]]:
    return {_actual_to_theorem_packet(row["packet"], eta) for row in packets}


def _fpc_clause_audit(
    row: Mapping[str, Any], provenance: Mapping[str, Any]
) -> dict[str, Any]:
    context_up = provenance["C_up"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    f_entry = provenance["F_4"]
    fusion = f_entry["terminal_fusion"]
    eta = provenance["eta"]
    ancestry = provenance["ancestry_update"]
    ambient_n = int(context_up["ambient_n"])

    up_packets = {_packet(packet["packet"]) for packet in pi_up}
    current_packets = {_packet(packet["packet"]) for packet in pi_current}
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    result_actual = _packet(f_entry["actual_packet"])
    result_theorem = _packet(f_entry["theorem_facing_packet"])
    incoming = _packet(ancestry["incoming_distinguished_packet"])
    incoming_theorem = _actual_to_theorem_packet(incoming, eta)
    current_distinguished = _packet(
        row["return_certificate"]["chi_4"]["distinguished_packet"]
    )
    mapped_target_packets = _map_actual_packets(provenance["Pi_target_actual"], eta)

    clauses = {
        "current_partition_is_n_minus_4_211": _partition(pi_current)
        == [ambient_n - 4, 2, 1, 1],
        "source_partition_is_n_minus_4_1111": _partition(pi_up)
        == [ambient_n - 4, 1, 1, 1, 1],
        "incoming_distinguished_has_mass_n_minus_4": len(incoming)
        == ambient_n - 4,
        "incoming_distinguished_not_fused": incoming not in parent_set,
        "incoming_distinguished_survives_under_handoff": incoming_theorem
        in current_packets,
        "incoming_participation_is_none": ancestry["participation_type"] == "NONE",
        "terminal_parents_are_distinct_source_singletons": len(parent_set) == 2
        and all(parent in up_packets and len(parent) == 1 for parent in parents),
        "terminal_result_has_mass_two": len(result_actual) == 2,
        "terminal_result_maps_to_current_distinguished": result_theorem
        == current_distinguished,
        "handoff_maps_exact_target_to_theorem_context": mapped_target_packets
        == current_packets,
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
    }
    return {
        "clauses": clauses,
        "failed_clauses": [key for key, value in clauses.items() if not value],
        "supported": all(clauses.values()),
    }


def _pec_clause_audit(
    row: Mapping[str, Any], provenance: Mapping[str, Any]
) -> dict[str, Any]:
    context_up = provenance["C_up"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    f_entry = provenance["F_4"]
    fusion = f_entry["terminal_fusion"]
    eta = provenance["eta"]
    ancestry = provenance["ancestry_update"]

    up_packets = {_packet(packet["packet"]) for packet in pi_up}
    current_packets = {_packet(packet["packet"]) for packet in pi_current}
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    result_actual = _packet(f_entry["actual_packet"])
    result_theorem = _packet(f_entry["theorem_facing_packet"])
    current_distinguished = _packet(
        row["return_certificate"]["chi_4"]["distinguished_packet"]
    )
    carried_pairs = sorted(
        packet for packet in up_packets - parent_set if len(packet) == 2
    )
    incoming = _packet(ancestry["incoming_distinguished_packet"])
    incoming_role = (
        "FUSED_PAIR"
        if incoming in parent_set and len(incoming) == 2
        else "CARRIED_PAIR"
        if incoming in carried_pairs
        else "OTHER"
    )
    mapped_target_packets = _map_actual_packets(provenance["Pi_target_actual"], eta)

    clauses = {
        "source_has_rank_five": len(pi_up) == 5,
        "current_has_rank_four": len(pi_current) == 4,
        "terminal_parents_are_one_singleton_and_one_pair": sorted(
            len(parent) for parent in parents
        )
        == [1, 2]
        and len(parent_set) == 2,
        "terminal_parents_are_source_packets": all(
            parent in up_packets for parent in parents
        ),
        "terminal_result_has_mass_three": len(result_actual) == 3,
        "terminal_result_maps_to_current_distinguished": result_theorem
        == current_distinguished,
        "exactly_one_complementary_source_pair": len(carried_pairs) == 1,
        "complementary_pair_survives_under_handoff": bool(carried_pairs)
        and _actual_to_theorem_packet(carried_pairs[0], eta) in current_packets,
        "incoming_distinguished_is_one_of_two_pair_roles": incoming_role
        in {"FUSED_PAIR", "CARRIED_PAIR"},
        "handoff_maps_exact_target_to_theorem_context": mapped_target_packets
        == current_packets,
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
    }
    return {
        "clauses": clauses,
        "failed_clauses": [key for key, value in clauses.items() if not value],
        "supported": all(clauses.values()),
    }


def build_payload(
    *,
    rank4_authority_path: Path = DEFAULT_R4_AUTHORITY,
    rank5_candidate_path: Path = DEFAULT_R5_CANDIDATE,
    family_declaration_path: Path = DEFAULT_FAMILY_DECLARATION,
) -> dict[str, Any]:
    # Phase one completes before the mechanism declaration is opened.
    frozen = _build_projectability(
        rank4_authority_path=rank4_authority_path,
        rank5_candidate_path=rank5_candidate_path,
    )
    projectability = frozen["projectability"]
    projectability_digest = frozen["projectability_payload_sha256"]

    # Phase two begins only after projectability has a frozen digest.
    family = _load(family_declaration_path)
    if family.get("schema") != FAMILY_SCHEMA:
        raise AssertionError("unexpected mechanism-family declaration schema")
    _verify_content_digest(family, "mechanism-family declaration")
    if family["declaration"]["expanded_family"] != DECLARED_FAMILY:
        raise AssertionError("declared mechanism family drift")
    if family["scope"]["success_evaluator_loaded"]:
        raise AssertionError("mechanism declaration loaded a success evaluator")

    support_rows = []
    fpc_failures: Counter[str] = Counter()
    pec_failures: Counter[str] = Counter()
    for row in projectability["rows"]:
        current_partition = _boundary_partition(row["return_certificate"]["b_4"])
        ow_gate = current_partition == OW_PARTITION_N7
        provenance_support = []
        for provenance_row in row["provenance_fiber"]:
            provenance = provenance_row["kappa_4_ISE"]
            fpc = _fpc_clause_audit(row, provenance)
            pec = _pec_clause_audit(row, provenance)
            for clause in fpc["failed_clauses"]:
                fpc_failures[clause] += 1
            for clause in pec["failed_clauses"]:
                pec_failures[clause] += 1
            supported = []
            if ow_gate:
                supported.append("OW")
            if fpc["supported"]:
                supported.append("FPC")
            if pec["supported"]:
                supported.append("PEC")
            provenance_support.append(
                {
                    "kappa_4_ISE_id": provenance_row["kappa_4_ISE_id"],
                    "ow": {
                        "necessary_partition_gate": ow_gate,
                        "required_partition": OW_PARTITION_N7,
                        "actual_partition": current_partition,
                        "remaining_clauses": (
                            "NOT_EVALUATED_BECAUSE_NECESSARY_GATE_FAILED"
                            if not ow_gate
                            else "NOT_IN_SCOPE_OF_THIS_HOSTILE_AUDIT"
                        ),
                        "supported": False if not ow_gate else None,
                    },
                    "fpc": fpc,
                    "pec": pec,
                    "supported_mechanisms": supported,
                }
            )
        supported_mechanisms = sorted(
            {
                mechanism
                for item in provenance_support
                for mechanism in item["supported_mechanisms"]
            }
        )
        support_rows.append(
            {
                "carrier_id": "ext",
                "context_id": row["context_id"],
                "return_certificate_id": row["return_certificate_id"],
                "provenance_fiber_nonempty": bool(row["provenance_fiber"]),
                "provenance_support": provenance_support,
                "supported_mechanisms": supported_mechanisms,
                "expanded_family_support_relation_nonempty": bool(
                    supported_mechanisms
                ),
            }
        )

    supported_count = sum(
        int(row["expanded_family_support_relation_nonempty"])
        for row in support_rows
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "section": "Sec_4,ext^(7)",
            "declared_mechanism_family": DECLARED_FAMILY,
            "rank5_good_evaluator_loaded": False,
            "new_census": False,
        },
        "phase_order": [
            "reconstruct_ext_projectability_from_rank4_authority_and_pre_Good5_transfer_relation",
            "freeze_projectability_digest",
            "load_frozen_OW_FPC_PEC_declaration",
            "evaluate_support_without_return_evaluation",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            **frozen["inputs"],
            "family_declaration": _input_record(family_declaration_path, family),
        },
        "projectability_payload_sha256": projectability_digest,
        "projectability": projectability,
        "support_audit": {
            "declared_family": DECLARED_FAMILY,
            "definition": (
                "support is evaluated on every provenance only after the complete "
                "ext projectability relation is frozen"
            ),
            "context_count": len(support_rows),
            "supported_context_count": supported_count,
            "projectable_but_unsupported_context_count": (
                len(support_rows) - supported_count
            ),
            "fpc_failed_clause_histogram": dict(sorted(fpc_failures.items())),
            "pec_failed_clause_histogram": dict(sorted(pec_failures.items())),
            "rows": support_rows,
        },
        "summary": {
            "admitted_contexts": len(support_rows),
            "projectable_contexts": projectability["projectable_context_count"],
            "OW_supported_contexts": sum(
                int("OW" in row["supported_mechanisms"]) for row in support_rows
            ),
            "FPC_supported_contexts": sum(
                int("FPC" in row["supported_mechanisms"])
                for row in support_rows
            ),
            "PEC_supported_contexts": sum(
                int("PEC" in row["supported_mechanisms"])
                for row in support_rows
            ),
            "expanded_family_supported_contexts": supported_count,
            "projectable_but_unsupported_contexts": len(support_rows)
            - supported_count,
            "result": (
                "OW_FPC_PEC_FAMILY_INCOMPLETE_ON_EXT"
                if supported_count < len(support_rows)
                else "OW_FPC_PEC_FAMILY_SUPPORTS_EXT"
            ),
        },
        "claim_boundary": {
            "proved": (
                "fixed-n=7 ext projectability/support separation for the frozen "
                "mechanism family {OW,FPC,PEC}"
            ),
            "not_claimed": [
                "failure of F5",
                "the identity of a fourth mechanism",
                "a generalized fresh-pair carry schema",
                "all-n projectability or support cover",
                "equality with Lambda_4^complete(C)",
                "uniform functionality of Proj_ISE",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    rank4_authority_path: Path,
    rank5_candidate_path: Path,
    family_declaration_path: Path,
) -> dict[str, Any]:
    validator = HERE / "validation" / "validate_paper28_extremal_family_support.py"
    source_closure = [HERE / Path(__file__).name, validator]
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
            {
                "name": path.name,
                "sha256": _sha256(path),
            }
            for path in (
                rank4_authority_path,
                rank5_candidate_path,
                family_declaration_path,
            )
        ],
        "source_closure": [
            {
                "name": path.relative_to(HERE).as_posix(),
                "sha256": _sha256(path),
            }
            for path in source_closure
        ],
        "verification_mode": (
            "PROJECTABILITY_FREEZE_THEN_POST_DECLARATION_SUPPORT_EVALUATION"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rank4-authority", type=Path, default=DEFAULT_R4_AUTHORITY)
    parser.add_argument("--rank5-candidate", type=Path, default=DEFAULT_R5_CANDIDATE)
    parser.add_argument(
        "--family-declaration", type=Path, default=DEFAULT_FAMILY_DECLARATION
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_payload(
        rank4_authority_path=args.rank4_authority,
        rank5_candidate_path=args.rank5_candidate,
        family_declaration_path=args.family_declaration,
    )
    _write(args.output, payload)
    receipt = build_receipt(
        output=args.output,
        payload=payload,
        rank4_authority_path=args.rank4_authority,
        rank5_candidate_path=args.rank5_candidate,
        family_declaration_path=args.family_declaration,
    )
    _write_receipt(default_receipt_path(args.output), receipt)
    print(
        json.dumps(
            {
                "artifact": args.output.as_posix(),
                "artifact_sha256": _sha256(args.output),
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
