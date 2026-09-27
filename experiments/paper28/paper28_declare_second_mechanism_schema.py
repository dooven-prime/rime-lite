#!/usr/bin/env python3
"""Declare the second rank-four mechanism schema from a frozen support gap.

The input is the P28.6u-B0 projectability/support-separation artifact.  This
script first extracts and digests the source-local role-transport profile of
all exact projectable-but-unsupported provenances.  Only after that digest is
frozen does it evaluate the new provenance-level branch predicate and attach
the stable schema identifier FPC (Fresh-Pair Carry).

No Good evaluator, lower-target membership, successful receipt, winner, or
historical mechanism label is read.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "paper28-second-mechanism-schema-declaration-v1"
RECEIPT_SCHEMA = "paper28-second-mechanism-schema-declaration-receipt-v1"
INPUT_SCHEMA = "paper28-fixed-scope-projectability-support-separation-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    HERE
    / "results"
    / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_second_mechanism_schema_declaration_v1.json.gz"
)

PRIOR_FAMILY = ["OW"]
SCHEMA_ID = "FPC"
SCHEMA_NAME = "Fresh-Pair Carry"
EXPANDED_FAMILY = ["OW", SCHEMA_ID]
FORBIDDEN_INPUTS = [
    "paper28_second_rank5_section_return_evaluation_v1.json.gz",
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


def _role_profile(row: Mapping[str, Any]) -> dict[str, Any]:
    provenance_row = row["provenance_fiber"][0]
    provenance = provenance_row["kappa_4_ISE"]
    return_certificate = row["return_certificate"]
    context_up = provenance["C_up"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    f2_record = provenance["F_4"]
    fusion = f2_record["terminal_fusion"]
    ancestry = return_certificate["chi_4"]["incoming_transfer_update"]

    ambient_n = int(context_up["ambient_n"])
    up_packets = {_packet(packet["packet"]): packet for packet in pi_up}
    current_packets = {
        _packet(packet["packet"]): packet for packet in pi_current
    }
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    parent_union = tuple(sorted(atom for packet in parents for atom in packet))
    f2 = _packet(f2_record["packet"])
    incoming_heavy = _packet(ancestry["incoming_distinguished_packet"])
    outgoing_distinguished = _packet(
        ancestry["outgoing_distinguished_packet"]
    )
    current_distinguished = _packet(
        return_certificate["chi_4"]["distinguished_packet"]
    )

    expected_current_packets = (set(up_packets) - parent_set) | {f2}
    selected_sigma5 = provenance["sel"]["selected_sigma5"]
    selected_word = [int(value) for value in selected_sigma5["selected_word"]]
    exact_words = provenance["e"]["words"]

    checks = {
        "pi_up_equals_source_packets": pi_up == context_up["packets"],
        "source_partition_is_n_minus_4_1111": _partition(pi_up)
        == [ambient_n - 4, 1, 1, 1, 1],
        "current_partition_is_n_minus_4_211": _partition(pi_current)
        == [ambient_n - 4, 2, 1, 1],
        "incoming_distinguished_is_source_distinguished": incoming_heavy
        == _packet(context_up["distinguished_packet"]),
        "incoming_distinguished_has_mass_n_minus_4": len(incoming_heavy)
        == ambient_n - 4,
        "incoming_distinguished_survives_atomwise": incoming_heavy
        in current_packets,
        "incoming_distinguished_not_fused": incoming_heavy not in parent_set,
        "incoming_participation_is_none": ancestry["participation_type"]
        == "NONE",
        "terminal_parents_are_distinct_source_singletons": len(parent_set) == 2
        and all(parent in up_packets and len(parent) == 1 for parent in parents),
        "terminal_result_is_parent_union": f2 == parent_union,
        "terminal_result_has_mass_two": int(f2_record["mass"]) == len(f2) == 2,
        "terminal_result_is_outgoing_distinguished": f2
        == outgoing_distinguished,
        "terminal_result_is_current_distinguished": f2
        == current_distinguished,
        "current_packet_partition_is_exact_replay": set(current_packets)
        == expected_current_packets,
        "selected_word_is_exact_transfer_word": exact_words == [selected_word],
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
        "handoff_certifies_role_transport": provenance["eta"][
            "target_context_id"
        ]
        == row["context_id"]
        and f2 in current_packets
        and incoming_heavy in current_packets,
    }

    current_boundary = return_certificate["b_4"]
    target_offset_profile = [
        {
            "mass": int(item["mass"]),
            "offset": int(item["offset_from_distinguished"]),
            "distinguished": bool(item["is_distinguished"]),
        }
        for item in current_boundary["mass_rows"]
    ]
    source_placement_profile = [
        {
            "mass": int(packet["mass"]),
            "coordinate": int(packet["coordinate"]),
            "is_incoming_distinguished": _packet(packet["packet"])
            == incoming_heavy,
            "is_terminal_parent": _packet(packet["packet"]) in parent_set,
        }
        for packet in pi_up
    ]

    return {
        "context_id": str(row["context_id"]),
        "return_certificate_id": str(row["return_certificate_id"]),
        "kappa_4_ISE_id": str(provenance_row["kappa_4_ISE_id"]),
        "ambient_n": ambient_n,
        "source_partition": _partition(pi_up),
        "current_partition": _partition(pi_current),
        "incoming_distinguished_mass": len(incoming_heavy),
        "terminal_parent_masses": sorted(len(parent) for parent in parents),
        "terminal_result_mass": len(f2),
        "ancestry_update_rule": str(ancestry["update_rule"]),
        "checks": checks,
        "realization_anatomy": {
            "selected_word": selected_word,
            "length": int(selected_sigma5["total_length"]),
            "surplus": int(selected_sigma5["total_surplus"]),
            "handoff_type": str(provenance["eta"]["type"]),
            "source_placement_profile": source_placement_profile,
            "target_offset_profile": target_offset_profile,
        },
    }


def build_payload(*, input_path: Path) -> dict[str, Any]:
    source = _load(input_path)
    if source.get("schema") != INPUT_SCHEMA:
        raise AssertionError("unexpected projectability/support input schema")
    _verify_content_digest(source)
    if source["summary"]["projectable_but_unsupported_contexts"] != 48:
        raise AssertionError("support-gap domain drift")
    if source["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("input unexpectedly loaded the rank-five evaluator")
    if source["support_audit"]["declared_family"] != PRIOR_FAMILY:
        raise AssertionError("input is not the singleton OW support audit")

    input_support = {
        str(row["context_id"]): row
        for row in source["support_audit"]["rows"]
    }
    source_rows = []
    for row in source["projectability"]["rows"]:
        context_id = str(row["context_id"])
        support = input_support[context_id]
        if not row["projectable"] or not row["provenance_fiber"]:
            continue
        if support["singleton_support_relation_nonempty"]:
            continue
        if len(row["provenance_fiber"]) != 1:
            raise AssertionError("cand2 provenance fiber cardinality drift")
        source_rows.append(row)
    source_rows.sort(key=lambda row: str(row["context_id"]))
    if len(source_rows) != 48:
        raise AssertionError("expected 48 exact unsupported provenances")

    profiles = [_role_profile(row) for row in source_rows]
    failed_checks = [
        {
            "context_id": profile["context_id"],
            "failed": [
                key for key, value in profile["checks"].items() if not value
            ],
        }
        for profile in profiles
        if not all(profile["checks"].values())
    ]
    if failed_checks:
        raise AssertionError(f"role-transport checks failed: {failed_checks[:3]}")

    common_profile = {
        "ambient_n": 7,
        "source_partition": [3, 1, 1, 1, 1],
        "current_partition": [3, 2, 1, 1],
        "incoming_distinguished_role": (
            "mass n-4 packet transported atomwise and not used by the entry fusion"
        ),
        "entry_role": (
            "two distinct source singleton packets are fused by the exact terminal "
            "entry step"
        ),
        "outgoing_distinguished_role": (
            "the exact singleton union is the mass-two entry packet F_ent and "
            "the current distinguished packet"
        ),
        "current_packet_equation": (
            "Pi_C = (Pi_up minus the two singleton parents) union {F_ent}"
        ),
        "handoff_obligation": (
            "the certified handoff preserves F_ent, the inherited mass-(n-4) packet, "
            "and the two remaining singleton packets"
        ),
    }
    common_profile_payload = {
        "common_profile": common_profile,
        "profiles": profiles,
    }
    common_profile_digest = _digest(common_profile_payload)

    word_histogram = _counter(
        [
            _word_key(profile["realization_anatomy"]["selected_word"])
            for profile in profiles
        ]
    )
    source_placement_profiles = {
        _canonical_text(profile["realization_anatomy"]["source_placement_profile"])
        for profile in profiles
    }
    target_offset_profiles = {
        _canonical_text(profile["realization_anatomy"]["target_offset_profile"])
        for profile in profiles
    }

    branch_formula = {
        "provenance_record": "kappa_4^ISE in the complete frozen P_ISE fiber",
        "clauses": [
            "part(mu_C)=(n-4,2,1,1)",
            "part(mu_C_up)=(n-4,1,1,1,1)",
            "the exact selected terminal entry fuses two distinct singleton packets x,y",
            "F_ent:=F_4=x disjoint-union y has mass two and is transported to the current distinguished packet",
            "the incoming distinguished mass-(n-4) packet H is disjoint from x,y and survives atomwise",
            "the exact current packet equation is {H,F_ent,z_1,z_2}",
            "the F3-certified handoff preserves the H,F_ent,z_1,z_2 typed roles",
        ],
        "explicitly_not_read": [
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

    support_rows = []
    for profile in profiles:
        supported = all(profile["checks"].values())
        support_rows.append(
            {
                "context_id": profile["context_id"],
                "return_certificate_id": profile["return_certificate_id"],
                "kappa_4_ISE_id": profile["kappa_4_ISE_id"],
                "schema_id": SCHEMA_ID,
                "supported": supported,
                "support_basis": "exact fresh-pair creation and inherited-heavy carry",
            }
        )
    supported_count = sum(1 for row in support_rows if row["supported"])
    if supported_count != 48:
        raise AssertionError("the declared FPC branch does not cover cand2")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "section": "Sec_4,cand2^(7)",
            "new_census": False,
            "success_evaluator_loaded": False,
            "input_projectability_payload_sha256": source[
                "projectability_payload_sha256"
            ],
        },
        "phase_order": [
            "load_frozen_projectable_but_unsupported_provenances",
            "derive_exact_source_local_role_transport_profiles",
            "freeze_common_profile_digest",
            "freeze_future_free_branch_formula",
            "assign_schema_identifier_FPC",
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
                "source_placement_profile_count": len(source_placement_profiles),
                "target_offset_profile_count": len(target_offset_profiles),
                "distinct_context_count": len(
                    {profile["context_id"] for profile in profiles}
                ),
                "interpretation": (
                    "the role-transport equation is common while word and placement "
                    "anatomy vary"
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
                "C_and_current_packet_partition": "typed rank-four source context",
                "C_up_and_exact_entry": "kappa_4^ISE provenance record",
                "packet_identities_and_ancestry_update": "exact replay in kappa_4^ISE",
                "typed_role_transport": "F3-certified handoff in kappa_4^ISE",
            },
            "support_rows": support_rows,
        },
        "summary": {
            "unsupported_projectable_provenances": 48,
            "FPC_supported_provenances": supported_count,
            "expanded_family_supported_contexts": supported_count,
            "selected_word_histogram": word_histogram,
            "source_placement_profile_count": len(source_placement_profiles),
            "target_offset_profile_count": len(target_offset_profiles),
            "result": "SECOND_SCHEMA_DECLARED_AND_CAND2_SUPPORT_GAP_CLOSED",
        },
        "claim_boundary": {
            "proved": [
                "all 48 exact unsupported cand2 provenances share the Fresh-Pair Carry role equation",
                "the FPC branch predicate is future-free and provenance-sensitive",
                "the expanded family {OW,FPC} supports every cand2 fixed-scope source",
            ],
            "not_proved": [
                "FPC component completion",
                "support cover on another released rank-four section",
                "all-n projectability or support cover",
                "completeness of {OW,FPC}",
                "identification of FPC with a historical mechanism label",
                "F5 from the enlarged family",
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
