#!/usr/bin/env python3
"""Declare the third rank-four mechanism from the pooled B1 support gap.

The input is the frozen P28.6u-B1 projectability/support-separation artifact.
This script first extracts and digests the exact source-local role profile of
all cand3/cand4/cand5 projectable-but-unsupported provenances.  It then freezes
the branch formula and only afterwards assigns the identifier PEC
(Pair-Extension Carry).

No return evaluator, lower-target membership, successful receipt, or winner
is read.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "paper28-third-mechanism-schema-declaration-v1"
RECEIPT_SCHEMA = "paper28-third-mechanism-schema-declaration-receipt-v1"
INPUT_SCHEMA = "paper28-expanded-family-support-separation-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    HERE / "results" / "paper28_expanded_family_support_separation_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_third_mechanism_schema_declaration_v1.json.gz"
)

PRIOR_FAMILY = ["OW", "FPC"]
SCHEMA_ID = "PEC"
SCHEMA_NAME = "Pair-Extension Carry"
EXPANDED_FAMILY = ["OW", "FPC", SCHEMA_ID]
FORBIDDEN_INPUTS = [
    "paper28_third_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fourth_rank5_section_return_evaluation_v1.json.gz",
    "paper28_fifth_rank5_section_return_evaluation_v1.json.gz",
    "Good_4",
    "Good_5",
    "LocalReturn",
    "target_in_lower_section",
    "successful_channel",
    "successful_exact_lift",
    "winning",
    "bellman",
    "historical_mechanism_label",
]


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _canonical_text(value: Any) -> str:
    return _canonical_bytes(value).decode("ascii")


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


def _verify_content_digest(payload: Mapping[str, Any]) -> None:
    candidate = dict(payload)
    stored = str(candidate.pop("content_sha256"))
    if _digest(candidate) != stored:
        raise AssertionError("input content digest mismatch")


def _packet(packet: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(int(atom) for atom in packet))


def _partition(packets: Sequence[Mapping[str, Any]]) -> list[int]:
    return sorted((int(row["mass"]) for row in packets), reverse=True)


def _word_key(word: Sequence[int]) -> str:
    return "".join(str(int(letter)) for letter in word)


def _counter(values: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _role_profile(
    *, carrier_id: str, row: Mapping[str, Any], provenance_row: Mapping[str, Any]
) -> dict[str, Any]:
    provenance = provenance_row["kappa_4_ISE"]
    return_certificate = row["return_certificate"]
    context_up = provenance["C_up"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    f3_record = provenance["F_4"]
    fusion = f3_record["terminal_fusion"]
    ancestry = provenance["ancestry_update"]

    up_packets = {_packet(packet["packet"]): packet for packet in pi_up}
    current_packets = {
        _packet(packet["packet"]): packet for packet in pi_current
    }
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    parent_union = tuple(sorted(atom for parent in parents for atom in parent))
    parent_by_mass = {len(parent): parent for parent in parents}
    fused_pair = parent_by_mass.get(2)
    fused_singleton = parent_by_mass.get(1)
    f3 = _packet(f3_record["packet"])
    incoming = _packet(ancestry["incoming_distinguished_packet"])
    outgoing = _packet(ancestry["outgoing_distinguished_packet"])
    current_distinguished = _packet(
        return_certificate["chi_4"]["distinguished_packet"]
    )
    carried_pairs = [
        packet for packet in up_packets if len(packet) == 2 and packet not in parent_set
    ]
    carried_pair = carried_pairs[0] if len(carried_pairs) == 1 else None
    spectators = set(up_packets) - parent_set
    expected_current = spectators | {f3}
    selected_sigma5 = provenance["sel"]["selected_sigma5"]
    selected_word = [int(value) for value in selected_sigma5["selected_word"]]

    if incoming == fused_pair:
        incoming_role = "FUSED_PAIR"
    elif incoming == carried_pair:
        incoming_role = "CARRIED_PAIR"
    else:
        incoming_role = "OTHER"

    checks = {
        "source_has_rank_five": len(pi_up) == 5,
        "current_has_rank_four": len(pi_current) == 4,
        "pi_up_equals_source_packets": pi_up == context_up["packets"],
        "terminal_parents_are_one_singleton_and_one_pair": sorted(
            len(parent) for parent in parents
        )
        == [1, 2]
        and len(parent_set) == 2,
        "terminal_parents_are_source_packets": all(
            parent in up_packets for parent in parents
        ),
        "terminal_result_is_parent_union": f3 == parent_union,
        "terminal_result_has_mass_three": int(f3_record["mass"])
        == len(f3)
        == 3,
        "terminal_result_is_outgoing_distinguished": f3 == outgoing,
        "terminal_result_is_current_distinguished": f3
        == current_distinguished,
        "exactly_one_complementary_source_pair": len(carried_pairs) == 1,
        "complementary_pair_survives_atomwise": carried_pair in current_packets,
        "all_nonparent_packets_survive_atomwise": spectators.issubset(
            set(current_packets)
        ),
        "current_packet_partition_is_exact_replay": set(current_packets)
        == expected_current,
        "incoming_distinguished_is_source_distinguished": incoming
        == _packet(context_up["distinguished_packet"]),
        "incoming_distinguished_is_one_of_the_two_pair_roles": incoming_role
        in {"FUSED_PAIR", "CARRIED_PAIR"},
        "selected_word_is_exact_transfer_word": provenance["e"]["words"]
        == [selected_word],
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
        "handoff_certifies_role_transport": provenance["eta"][
            "target_context_id"
        ]
        == row["context_id"]
        and f3 in current_packets
        and carried_pair in current_packets,
    }

    source_role_placement = [
        {
            "mass": int(packet["mass"]),
            "coordinate": int(packet["coordinate"]),
            "role": (
                "FUSED_PAIR"
                if _packet(packet["packet"]) == fused_pair
                else "FUSED_SINGLETON"
                if _packet(packet["packet"]) == fused_singleton
                else "CARRIED_PAIR"
                if _packet(packet["packet"]) == carried_pair
                else "SPECTATOR"
            ),
            "incoming_distinguished": _packet(packet["packet"]) == incoming,
        }
        for packet in pi_up
    ]
    target_offset_profile = [
        {
            "mass": int(item["mass"]),
            "offset": int(item["offset_from_distinguished"]),
            "distinguished": bool(item["is_distinguished"]),
        }
        for item in return_certificate["b_4"]["mass_rows"]
    ]

    return {
        "carrier_id": carrier_id,
        "context_id": str(row["context_id"]),
        "return_certificate_id": str(row["return_certificate_id"]),
        "kappa_4_ISE_id": str(provenance_row["kappa_4_ISE_id"]),
        "source_partition": _partition(pi_up),
        "current_partition": _partition(pi_current),
        "terminal_parent_masses": sorted(len(parent) for parent in parents),
        "terminal_result_mass": len(f3),
        "complementary_pair_mass": len(carried_pair) if carried_pair else None,
        "incoming_pair_role": incoming_role,
        "checks": checks,
        "realization_anatomy": {
            "selected_word": selected_word,
            "length": int(selected_sigma5["total_length"]),
            "surplus": int(selected_sigma5["total_surplus"]),
            "incoming_participation_type": str(ancestry["participation_type"]),
            "handoff_type": str(provenance["eta"]["type"]),
            "source_role_placement": source_role_placement,
            "target_offset_profile": target_offset_profile,
        },
    }


def build_payload(*, input_path: Path) -> dict[str, Any]:
    source = _load(input_path)
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected expanded-family support input schema")
    _verify_content_digest(source)
    if source["scope"]["declared_mechanism_family"] != PRIOR_FAMILY:
        raise AssertionError("input family is not {OW,FPC}")
    if source["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("input unexpectedly loaded a rank-five evaluator")
    if source["summary"]["projectable_but_unsupported_contexts"] != 82:
        raise AssertionError("pooled support-gap domain drift")

    support_by_key = {}
    for carrier in source["support_audit"]["carriers"]:
        for row in carrier["rows"]:
            support_by_key[(str(row["carrier_id"]), str(row["context_id"]))] = row

    exact_rows = []
    for carrier in source["projectability"]["carriers"]:
        carrier_id = str(carrier["carrier_id"])
        for row in carrier["rows"]:
            key = (carrier_id, str(row["context_id"]))
            support = support_by_key[key]
            if not row["projectable"] or not row["provenance_fiber"]:
                continue
            if support["expanded_family_support_relation_nonempty"]:
                continue
            for provenance_row in row["provenance_fiber"]:
                exact_rows.append((carrier_id, row, provenance_row))
    exact_rows.sort(
        key=lambda item: (
            item[0],
            str(item[1]["context_id"]),
            str(item[2]["kappa_4_ISE_id"]),
        )
    )
    if len(exact_rows) != 82:
        raise AssertionError("expected 82 exact unsupported provenances")

    # The anonymous profile is frozen before a schema identifier is assigned.
    profiles = [
        _role_profile(carrier_id=carrier_id, row=row, provenance_row=provenance)
        for carrier_id, row, provenance in exact_rows
    ]
    failed_checks = [
        {
            "carrier_id": profile["carrier_id"],
            "context_id": profile["context_id"],
            "failed": [key for key, value in profile["checks"].items() if not value],
        }
        for profile in profiles
        if not all(profile["checks"].values())
    ]
    if failed_checks:
        raise AssertionError(f"pair-extension checks failed: {failed_checks[:3]}")

    common_profile = {
        "source_rank": 5,
        "current_rank": 4,
        "entry_role": (
            "the exact selected terminal entry fuses a source-addressed mass-two "
            "packet P with a source singleton x"
        ),
        "outgoing_distinguished_role": (
            "F_ent=P disjoint-union x has mass three and is transported to the "
            "current distinguished packet"
        ),
        "carry_role": (
            "a distinct source-addressed mass-two packet Q is not fused and "
            "survives atomwise"
        ),
        "current_packet_equation": (
            "Pi_C=(Pi_up minus {P,x}) union {F_ent} with every nonparent packet "
            "preserved by exact replay"
        ),
        "ancestry_role": (
            "the incoming distinguished packet is either P or Q; exact ancestry "
            "update certifies consumption or carry without fixing the polarity"
        ),
        "handoff_obligation": (
            "the F3-certified handoff preserves F_ent, Q, and all spectator roles"
        ),
    }
    anonymous_profile_payload = {
        "common_profile": common_profile,
        "profiles": profiles,
    }
    common_profile_digest = _digest(anonymous_profile_payload)

    word_histogram = _counter(
        [
            _word_key(profile["realization_anatomy"]["selected_word"])
            for profile in profiles
        ]
    )
    length_histogram = _counter(
        [str(profile["realization_anatomy"]["length"]) for profile in profiles]
    )
    surplus_histogram = _counter(
        [str(profile["realization_anatomy"]["surplus"]) for profile in profiles]
    )
    incoming_role_histogram = _counter(
        [profile["incoming_pair_role"] for profile in profiles]
    )
    participation_histogram = _counter(
        [
            profile["realization_anatomy"]["incoming_participation_type"]
            for profile in profiles
        ]
    )
    source_placement_profiles = {
        _canonical_text(profile["realization_anatomy"]["source_role_placement"])
        for profile in profiles
    }
    target_offset_profiles = {
        _canonical_text(profile["realization_anatomy"]["target_offset_profile"])
        for profile in profiles
    }

    branch_formula = {
        "provenance_record": "kappa_4^ISE in the complete frozen P_ISE fiber",
        "clauses": [
            "there exist distinct source packets P,Q,x in Pi_up satisfying the following role equations",
            "Pi_up has rank five and Pi_C has rank four",
            "the exact selected terminal entry fuses a source mass-two packet P and singleton x",
            "F_ent:=F_4=P disjoint-union x has mass three and is transported to the current distinguished packet",
            "a distinct source mass-two packet Q survives atomwise",
            "the incoming distinguished packet is one of P,Q and the exact update certifies its consumed-or-carried role",
            "Pi_C=(Pi_up minus {P,x}) union {F_ent} with every nonparent packet preserved",
            "the F3-certified handoff preserves the F_ent,Q,and spectator typed roles",
        ],
        "explicitly_not_read": [
            "fresh-consumption polarity",
            "selected word",
            "corridor length",
            "surplus or debt",
            "literal coordinate placement",
            "kernel-offset profile",
            "literal identity of the handoff",
            "Good or LocalReturn",
            "lower-section membership",
            "successful endpoint or winner",
            "historical mechanism label",
        ],
    }

    # The identifier is assigned only after the profile and formula above exist.
    support_rows = []
    for profile in profiles:
        supported = all(profile["checks"].values())
        support_rows.append(
            {
                "carrier_id": profile["carrier_id"],
                "context_id": profile["context_id"],
                "return_certificate_id": profile["return_certificate_id"],
                "kappa_4_ISE_id": profile["kappa_4_ISE_id"],
                "schema_id": SCHEMA_ID,
                "supported": supported,
                "support_basis": (
                    "exact mass-two-plus-singleton extension and complementary-pair carry"
                ),
            }
        )
    supported_count = sum(1 for row in support_rows if row["supported"])
    if supported_count != 82:
        raise AssertionError("the declared PEC branch does not cover the pooled gap")
    supported_context_count = len(
        {
            (str(row["carrier_id"]), str(row["context_id"]))
            for row in support_rows
            if row["supported"]
        }
    )
    if supported_context_count != 82:
        raise AssertionError("PEC does not support every pooled source context")

    by_carrier = {}
    for carrier_id in ("cand3", "cand4", "cand5"):
        carrier_rows = [row for row in support_rows if row["carrier_id"] == carrier_id]
        by_carrier[carrier_id] = {
            "input_provenances": len(carrier_rows),
            "PEC_supported_provenances": sum(
                1 for row in carrier_rows if row["supported"]
            ),
        }

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "sections": [
                "Sec_4,cand3^(7)",
                "Sec_4,cand4^(7)",
                "Sec_4,cand5^(7)",
            ],
            "new_census": False,
            "success_evaluator_loaded": False,
            "input_projectability_payload_sha256": source[
                "projectability_payload_sha256"
            ],
        },
        "phase_order": [
            "load_pooled_frozen_projectable_but_unsupported_provenances",
            "derive_anonymous_cross_carrier_role_profiles",
            "freeze_common_profile_digest",
            "freeze_future_free_branch_formula",
            "assign_schema_identifier_PEC",
            "evaluate_expanded_family_support",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "input": {
            "name": input_path.name,
            "schema": source["schema"],
            "sha256": _sha256(input_path),
            "content_sha256": source["content_sha256"],
            "projectability_payload_sha256": source[
                "projectability_payload_sha256"
            ],
        },
        "unsupported_provenance_analysis": {
            "row_count": len(profiles),
            "common_profile": common_profile,
            "profiles": profiles,
            "common_profile_payload_sha256": common_profile_digest,
            "variation_audit": {
                "selected_word_histogram": word_histogram,
                "length_histogram": length_histogram,
                "surplus_histogram": surplus_histogram,
                "incoming_pair_role_histogram": incoming_role_histogram,
                "incoming_participation_histogram": participation_histogram,
                "source_role_placement_profile_count": len(
                    source_placement_profiles
                ),
                "target_offset_profile_count": len(target_offset_profiles),
                "interpretation": (
                    "pair-extension/carry is common while ancestry polarity, word, "
                    "length, surplus, and placement anatomy vary"
                ),
            },
        },
        "declaration": {
            "prior_family": PRIOR_FAMILY,
            "schema_id": SCHEMA_ID,
            "schema_name": SCHEMA_NAME,
            "expanded_family": EXPANDED_FAMILY,
            "branch_formula": branch_formula,
            "field_ownership": {
                "C_and_current_distinguished_packet": "typed rank-four source context",
                "C_up_and_exact_entry": "kappa_4^ISE provenance record",
                "packet_identities_and_ancestry_update": "exact replay in kappa_4^ISE",
                "typed_role_transport": "F3-certified handoff in kappa_4^ISE",
            },
            "support_rows": support_rows,
        },
        "summary": {
            "unsupported_projectable_provenances": 82,
            "PEC_supported_provenances": supported_count,
            "expanded_family_supported_contexts": supported_context_count,
            "by_carrier": by_carrier,
            "selected_word_histogram": word_histogram,
            "length_histogram": length_histogram,
            "surplus_histogram": surplus_histogram,
            "incoming_pair_role_histogram": incoming_role_histogram,
            "incoming_participation_histogram": participation_histogram,
            "source_role_placement_profile_count": len(source_placement_profiles),
            "target_offset_profile_count": len(target_offset_profiles),
            "result": "THIRD_SCHEMA_DECLARED_AND_POOLED_SUPPORT_GAP_CLOSED",
        },
        "claim_boundary": {
            "proved": [
                "all 82 exact unsupported provenances share the Pair-Extension Carry role equation",
                "the PEC branch predicate is future-free and provenance-sensitive",
                "the expanded family {OW,FPC,PEC} supports every audited cand3/cand4/cand5 fixed-scope source",
                "fresh-consumption polarity, length, surplus, and placement are not clauses of PEC",
            ],
            "not_proved": [
                "PEC component completion",
                "support cover on every released rank-four section",
                "all-n projectability or support cover",
                "completeness of {OW,FPC,PEC}",
                "identification of PEC with a historical mechanism label",
                "F5 from the enlarged family",
                "equality of the fixed-scope adapter with Lambda_4^complete(C)",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, output: Path, payload: Mapping[str, Any], input_path: Path
) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "common_profile_payload_sha256": payload[
                "unsupported_provenance_analysis"
            ]["common_profile_payload_sha256"],
        },
        "input": {"name": input_path.name, "sha256": _sha256(input_path)},
        "source_closure": {
            "script": {
                "name": Path(__file__).name,
                "sha256": _sha256(Path(__file__).resolve()),
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(input_path=args.input)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(output=args.out, payload=payload, input_path=args.input),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "common_profile_payload_sha256": payload[
                    "unsupported_provenance_analysis"
                ]["common_profile_payload_sha256"],
                **payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
