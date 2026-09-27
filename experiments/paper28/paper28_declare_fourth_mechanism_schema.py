#!/usr/bin/env python3
"""Declare the fourth rank-four mechanism from the cand2/ext pooled domain.

The exact domain is the tagged disjoint union of the 48 cand2 provenances
already supporting FPC and the 35 projectable-but-unsupported extremal
provenances from P28.6u-B2.  The script first checks and digests an anonymous
fresh-singleton-pair/carry role equation.  Only after all 83 rows pass is the
identifier GFPC (Generalized Fresh-Pair Carry) assigned.

No component-completion artifact, Good evaluator, lower-target membership,
successful receipt, or winner is read.
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

SCHEMA = "paper28-fourth-mechanism-schema-declaration-v1"
RECEIPT_SCHEMA = "paper28-fourth-mechanism-schema-declaration-receipt-v1"
B0_SCHEMA = "paper28-fixed-scope-projectability-support-separation-v1"
A1_SCHEMA = "paper28-second-mechanism-schema-declaration-v1"
A2_SCHEMA = "paper28-third-mechanism-schema-declaration-v1"
B2_SCHEMA = "paper28-extremal-carrier-support-separation-v1"

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_CAND2_PROJECTABILITY = (
    RESULTS / "paper28_fixed_scope_projectability_support_separation_v1.json.gz"
)
DEFAULT_FPC_DECLARATION = (
    RESULTS / "paper28_second_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_PRIOR_FAMILY = (
    RESULTS / "paper28_third_mechanism_schema_declaration_v1.json.gz"
)
DEFAULT_EXT_SUPPORT = (
    RESULTS / "paper28_extremal_carrier_support_separation_v1.json.gz"
)
DEFAULT_OUTPUT = (
    RESULTS / "paper28_fourth_mechanism_schema_declaration_v1.json.gz"
)

PRIOR_FAMILY = ["OW", "FPC", "PEC"]
SCHEMA_ID = "GFPC"
SCHEMA_NAME = "Generalized Fresh-Pair Carry"
EXPANDED_FAMILY = ["OW", "FPC", "PEC", SCHEMA_ID]
FORBIDDEN_INPUTS = [
    "paper28_second_rank4_section_return_evaluation_v1.json.gz",
    "paper28_section_return_menu_audit_v1.json.gz",
    "paper28_fpc_component_completion_v1.json.gz",
    "paper28_pec_component_completion_v1.json.gz",
    "Good_4",
    "Good_5",
    "LocalReturn",
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
    name = name.removesuffix(".json.gz")
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


def _packet(packet: Sequence[int]) -> tuple[int, ...]:
    return tuple(sorted(int(atom) for atom in packet))


def _partition(packets: Sequence[Mapping[str, Any]]) -> list[int]:
    return sorted((int(row["mass"]) for row in packets), reverse=True)


def _counter(values: Sequence[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _word_key(word: Sequence[int]) -> str:
    return "".join(str(int(letter)) for letter in word)


def _map_packet(packet: tuple[int, ...], eta: Mapping[str, Any]) -> tuple[int, ...]:
    if eta["type"] == "IDENTITY":
        return packet
    if eta["type"] != "ATOM_BIJECTION":
        raise AssertionError(f"unsupported handoff type {eta['type']}")
    atom_map = {
        int(row["actual_atom"]): int(row["theorem_atom"])
        for row in eta["actual_to_theorem_atom_bijection"]
    }
    return tuple(sorted(atom_map[atom] for atom in packet))


def _ancestry(
    *, row: Mapping[str, Any], provenance: Mapping[str, Any]
) -> Mapping[str, Any]:
    if "ancestry_update" in provenance:
        return provenance["ancestry_update"]
    return row["return_certificate"]["chi_4"]["incoming_transfer_update"]


def _role_profile(
    *, pool_tag: str, row: Mapping[str, Any], provenance_row: Mapping[str, Any]
) -> dict[str, Any]:
    provenance = provenance_row["kappa_4_ISE"]
    pi_up = provenance["Pi_up"]
    pi_current = provenance["Pi_C"]
    context_up = provenance["C_up"]
    f_entry = provenance["F_4"]
    fusion = f_entry["terminal_fusion"]
    eta = provenance["eta"]
    ancestry = _ancestry(row=row, provenance=provenance)

    up_packets = {_packet(item["packet"]): item for item in pi_up}
    current_packets = {_packet(item["packet"]): item for item in pi_current}
    actual_target_rows = provenance.get("Pi_target_actual", pi_current)
    actual_target_packets = {
        _packet(item["packet"]): item for item in actual_target_rows
    }
    parents = [_packet(packet) for packet in fusion["parents"]]
    parent_set = set(parents)
    parent_union = tuple(sorted(atom for parent in parents for atom in parent))
    result_actual = _packet(
        f_entry.get("actual_packet", f_entry.get("packet", []))
    )
    result_theorem = _packet(
        f_entry.get("theorem_facing_packet", _map_packet(result_actual, eta))
    )
    mapped_result = _map_packet(result_actual, eta)
    nonparents = set(up_packets) - parent_set
    expected_actual_target = nonparents | {result_actual}
    expected_theorem_target = {
        _map_packet(packet, eta) for packet in expected_actual_target
    }
    incoming = _packet(ancestry["incoming_distinguished_packet"])
    outgoing = _packet(ancestry["outgoing_distinguished_packet"])
    current_distinguished = _packet(
        row["return_certificate"]["chi_4"]["distinguished_packet"]
    )
    selected = provenance["sel"]["selected_sigma5"]
    selected_word = [int(value) for value in selected["selected_word"]]

    carry_rows = [
        {
            "source_packet": list(packet),
            "theorem_packet": list(_map_packet(packet, eta)),
            "mass": len(packet),
            "incoming_distinguished": packet == incoming,
            "actual_target_contains_packet": packet in actual_target_packets,
            "theorem_target_contains_packet": _map_packet(packet, eta)
            in current_packets,
        }
        for packet in sorted(nonparents)
    ]

    checks = {
        "source_has_rank_five": len(pi_up) == 5,
        "current_has_rank_four": len(pi_current) == 4,
        "pi_up_equals_source_packets": pi_up == context_up["packets"],
        "terminal_parents_are_distinct_source_singletons": len(parent_set) == 2
        and all(parent in up_packets and len(parent) == 1 for parent in parents),
        "terminal_result_is_parent_union": result_actual == parent_union,
        "terminal_result_has_mass_two": int(f_entry["mass"])
        == len(result_actual)
        == 2,
        "terminal_result_maps_to_theorem_packet": mapped_result
        == result_theorem,
        "terminal_result_maps_to_current_distinguished": mapped_result
        == current_distinguished,
        "terminal_result_is_outgoing_distinguished_before_handoff": result_actual
        == outgoing,
        "exactly_three_nonparent_source_packets": len(nonparents) == 3,
        "all_three_nonparents_carry_atomwise": all(
            item["actual_target_contains_packet"]
            and item["theorem_target_contains_packet"]
            for item in carry_rows
        ),
        "incoming_distinguished_is_source_distinguished": incoming
        == _packet(context_up["distinguished_packet"]),
        "incoming_distinguished_is_nonparent": incoming in nonparents,
        "incoming_distinguished_carries_atomwise": incoming in actual_target_packets
        and _map_packet(incoming, eta) in current_packets,
        "actual_target_is_exact_packet_replay": set(actual_target_packets)
        == expected_actual_target,
        "theorem_target_is_exact_handoff_image": set(current_packets)
        == expected_theorem_target,
        "selected_word_is_exact_transfer_word": provenance["e"]["words"]
        == [selected_word],
        "selector_is_future_free": not provenance["sel"][
            "membership_uses_lower_section_success"
        ],
    }

    background_masses = sorted((len(packet) for packet in nonparents), reverse=True)
    return {
        "pool_tag": pool_tag,
        "carrier_id": "cand2" if pool_tag == "cand2_fpc" else "ext",
        "context_id": str(row["context_id"]),
        "return_certificate_id": str(row["return_certificate_id"]),
        "kappa_4_ISE_id": str(provenance_row["kappa_4_ISE_id"]),
        "source_partition": _partition(pi_up),
        "current_partition": _partition(pi_current),
        "background_mass_profile": background_masses,
        "incoming_distinguished_mass": len(incoming),
        "terminal_parent_masses": sorted(len(parent) for parent in parents),
        "terminal_result_mass": len(result_actual),
        "handoff_type": str(eta["type"]),
        "checks": checks,
        "role_witness": {
            "parents": [list(packet) for packet in sorted(parent_set)],
            "entry_packet_actual": list(result_actual),
            "entry_packet_theorem": list(result_theorem),
            "incoming_distinguished_packet": list(incoming),
            "nonparent_carry_rows": carry_rows,
        },
        "realization_anatomy": {
            "selected_word": selected_word,
            "length": int(selected["total_length"]),
            "surplus": int(selected["total_surplus"]),
            "incoming_participation_type": str(ancestry["participation_type"]),
            "literal_handoff_identity": eta["type"] == "IDENTITY"
            or bool(eta.get("literal_atom_identity", False)),
        },
    }


def _collect_cand2(
    *, projectability: Mapping[str, Any], fpc: Mapping[str, Any]
) -> list[tuple[str, Mapping[str, Any], Mapping[str, Any]]]:
    support_by_key = {
        (
            str(row["context_id"]),
            str(row["return_certificate_id"]),
            str(row["kappa_4_ISE_id"]),
        ): row
        for row in fpc["declaration"]["support_rows"]
    }
    rows = []
    for row in projectability["projectability"]["rows"]:
        if not row["projectable"]:
            continue
        for provenance_row in row["provenance_fiber"]:
            key = (
                str(row["context_id"]),
                str(row["return_certificate_id"]),
                str(provenance_row["kappa_4_ISE_id"]),
            )
            support = support_by_key.get(key)
            if support is not None and support["supported"]:
                rows.append(("cand2_fpc", row, provenance_row))
    rows.sort(key=lambda item: (str(item[1]["context_id"]), str(item[2]["kappa_4_ISE_id"])))
    if len(rows) != 48:
        raise AssertionError("expected exactly 48 FPC-supported cand2 provenances")
    return rows


def _collect_ext(
    *, ext_support: Mapping[str, Any]
) -> list[tuple[str, Mapping[str, Any], Mapping[str, Any]]]:
    support_by_context = {
        str(row["context_id"]): row for row in ext_support["support_audit"]["rows"]
    }
    rows = []
    for row in ext_support["projectability"]["rows"]:
        support = support_by_context[str(row["context_id"])]
        if not row["projectable"] or not row["provenance_fiber"]:
            continue
        if support["expanded_family_support_relation_nonempty"]:
            continue
        for provenance_row in row["provenance_fiber"]:
            rows.append(("ext_unsupported", row, provenance_row))
    rows.sort(key=lambda item: (str(item[1]["context_id"]), str(item[2]["kappa_4_ISE_id"])))
    if len(rows) != 35:
        raise AssertionError("expected exactly 35 unsupported ext provenances")
    return rows


def build_payload(
    *,
    cand2_projectability_path: Path = DEFAULT_CAND2_PROJECTABILITY,
    fpc_declaration_path: Path = DEFAULT_FPC_DECLARATION,
    prior_family_path: Path = DEFAULT_PRIOR_FAMILY,
    ext_support_path: Path = DEFAULT_EXT_SUPPORT,
) -> dict[str, Any]:
    cand2 = _load(cand2_projectability_path)
    fpc = _load(fpc_declaration_path)
    prior_family = _load(prior_family_path)
    ext = _load(ext_support_path)
    for payload, schema, label in (
        (cand2, B0_SCHEMA, "cand2 projectability"),
        (fpc, A1_SCHEMA, "FPC declaration"),
        (prior_family, A2_SCHEMA, "prior family declaration"),
        (ext, B2_SCHEMA, "ext support separation"),
    ):
        if payload.get("schema") != schema:
            raise AssertionError(f"unexpected {label} schema")
        _verify_content_digest(payload, label)

    if cand2["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("cand2 input loaded a rank-five Good evaluator")
    if fpc["scope"]["success_evaluator_loaded"]:
        raise AssertionError("FPC declaration loaded a success evaluator")
    if prior_family["scope"]["success_evaluator_loaded"]:
        raise AssertionError("prior family declaration loaded a success evaluator")
    if ext["scope"]["rank5_good_evaluator_loaded"]:
        raise AssertionError("ext input loaded a rank-five Good evaluator")
    if prior_family["declaration"]["expanded_family"] != PRIOR_FAMILY:
        raise AssertionError("prior mechanism family drift")
    if ext["support_audit"]["declared_family"] != PRIOR_FAMILY:
        raise AssertionError("ext support audit did not test the prior family")
    if fpc["declaration"]["schema_id"] != "FPC":
        raise AssertionError("FPC declaration identity drift")

    cand2_rows = _collect_cand2(projectability=cand2, fpc=fpc)
    ext_rows = _collect_ext(ext_support=ext)
    tagged_rows = cand2_rows + ext_rows
    if len(tagged_rows) != 83:
        raise AssertionError("pooled provenance domain is not 48 disjoint-union 35")

    # This anonymous payload is complete and frozen before a schema name exists.
    profiles = [
        _role_profile(pool_tag=tag, row=row, provenance_row=provenance)
        for tag, row, provenance in tagged_rows
    ]
    failed_checks = [
        {
            "pool_tag": profile["pool_tag"],
            "context_id": profile["context_id"],
            "kappa_4_ISE_id": profile["kappa_4_ISE_id"],
            "failed": [
                key for key, value in profile["checks"].items() if not value
            ],
        }
        for profile in profiles
        if not all(profile["checks"].values())
    ]
    if failed_checks:
        raise AssertionError(
            f"anonymous fresh-pair/carry checks failed: {failed_checks[:3]}"
        )

    common_profile = {
        "source_rank": 5,
        "current_rank": 4,
        "entry_role": (
            "there exist distinct singleton source packets x,y whose exact "
            "terminal strict fusion is x disjoint-union y=F_ent"
        ),
        "distinguished_role": (
            "F_ent has mass two and its F3-certified handoff image is the "
            "current distinguished packet"
        ),
        "carry_role": (
            "all three remaining source-addressed packets carry atomwise; the "
            "incoming distinguished packet is one of them"
        ),
        "current_packet_equation": (
            "Pi_C=eta((Pi_up minus {x,y}) union {F_ent})"
        ),
    }
    anonymous_profile_payload = {
        "common_profile": common_profile,
        "profiles": profiles,
    }
    anonymous_profile_digest = _digest(anonymous_profile_payload)

    by_pool = {}
    for pool_tag in ("cand2_fpc", "ext_unsupported"):
        pool_profiles = [p for p in profiles if p["pool_tag"] == pool_tag]
        by_pool[pool_tag] = {
            "input_provenances": len(pool_profiles),
            "anonymous_role_equation_passes": sum(
                int(all(p["checks"].values())) for p in pool_profiles
            ),
        }

    background_histogram = _counter(
        [",".join(map(str, p["background_mass_profile"])) for p in profiles]
    )
    source_partition_histogram = _counter(
        [",".join(map(str, p["source_partition"])) for p in profiles]
    )
    current_partition_histogram = _counter(
        [",".join(map(str, p["current_partition"])) for p in profiles]
    )
    incoming_mass_histogram = _counter(
        [str(p["incoming_distinguished_mass"]) for p in profiles]
    )
    handoff_histogram = _counter([p["handoff_type"] for p in profiles])
    word_histogram = _counter(
        [_word_key(p["realization_anatomy"]["selected_word"]) for p in profiles]
    )
    length_histogram = _counter(
        [str(p["realization_anatomy"]["length"]) for p in profiles]
    )
    surplus_histogram = _counter(
        [str(p["realization_anatomy"]["surplus"]) for p in profiles]
    )

    branch_formula = {
        "provenance_record": "kappa_4^ISE in the complete frozen P_ISE fiber",
        "role_quantifier": (
            "there exist distinct x,y in Pi_up; no uniqueness of the role "
            "decomposition is assumed"
        ),
        "clauses": [
            "Pi_up has rank five and Pi_C has rank four",
            "x and y are distinct source-addressed singleton packets",
            "the exact terminal strict entry fuses x,y into F_ent=x disjoint-union y",
            "F_ent has mass two and eta(F_ent)=Dist(chi_4)",
            "all three nonparent source-addressed packets carry atomwise under eta",
            "Dist(chi_up) is a nonparent and carries atomwise",
            "Pi_C=eta((Pi_up minus {x,y}) union {F_ent})",
        ],
        "explicitly_not_read": [
            "background packet masses",
            "incoming distinguished mass",
            "current packet partition",
            "literal identity of the handoff",
            "selected word",
            "corridor length",
            "surplus or debt",
            "cyclic placement or kernel offsets",
            "Good or LocalReturn",
            "lower-section membership",
            "successful endpoint or winner",
            "historical mechanism label",
        ],
    }

    # Naming occurs only after every anonymous row has passed and the payload
    # above has a stable digest.
    support_rows = [
        {
            "pool_tag": profile["pool_tag"],
            "carrier_id": profile["carrier_id"],
            "context_id": profile["context_id"],
            "return_certificate_id": profile["return_certificate_id"],
            "kappa_4_ISE_id": profile["kappa_4_ISE_id"],
            "schema_id": SCHEMA_ID,
            "supported": all(profile["checks"].values()),
            "support_basis": (
                "exact singleton-pair creation of the distinguished mass-two "
                "packet with three-packet atomwise carry"
            ),
        }
        for profile in profiles
    ]
    supported_count = sum(int(row["supported"]) for row in support_rows)
    if supported_count != 83:
        raise AssertionError("GFPC does not cover the frozen pooled domain")

    fpc_ids = {
        str(row["kappa_4_ISE_id"])
        for row in fpc["declaration"]["support_rows"]
        if row["supported"]
    }
    gfpc_cand2_ids = {
        str(row["kappa_4_ISE_id"])
        for row in support_rows
        if row["pool_tag"] == "cand2_fpc" and row["supported"]
    }
    if fpc_ids != gfpc_cand2_ids:
        raise AssertionError("FPC support domain is not contained in GFPC")
    strict_ext_witnesses = [
        row for row in support_rows if row["pool_tag"] == "ext_unsupported"
    ]
    if len(strict_ext_witnesses) != 35:
        raise AssertionError("strict subsumption witness count drift")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "rank": 4,
            "sections": ["Sec_4,cand2^(7)", "Sec_4,ext^(7)"],
            "pooled_domain": (
                "48 cand2 FPC provenances tagged-disjoint-union 35 ext "
                "unsupported provenances"
            ),
            "new_census": False,
            "success_evaluator_loaded": False,
        },
        "phase_order": [
            "load_48_frozen_FPC_supported_cand2_provenances",
            "load_35_frozen_projectable_but_unsupported_ext_provenances",
            "form_tagged_disjoint_union",
            "derive_anonymous_exact_fresh_pair_carry_profiles",
            "freeze_anonymous_profile_digest",
            "freeze_future_free_branch_formula",
            "assign_schema_identifier_GFPC",
            "prove_FPC_branch_domain_subsumption_and_record_strict_ext_witnesses",
        ],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "inputs": {
            "cand2_projectability": _input_record(
                cand2_projectability_path, cand2
            ),
            "fpc_declaration": _input_record(fpc_declaration_path, fpc),
            "prior_family_declaration": _input_record(
                prior_family_path, prior_family
            ),
            "ext_support_separation": _input_record(ext_support_path, ext),
        },
        "anonymous_role_analysis": {
            "row_count": len(profiles),
            "tagged_domain_counts": {
                "cand2_fpc": len(cand2_rows),
                "ext_unsupported": len(ext_rows),
            },
            "common_profile": common_profile,
            "profiles": profiles,
            "anonymous_profile_payload_sha256": anonymous_profile_digest,
            "variation_audit": {
                "source_partition_histogram": source_partition_histogram,
                "current_partition_histogram": current_partition_histogram,
                "background_mass_profile_histogram": background_histogram,
                "incoming_distinguished_mass_histogram": incoming_mass_histogram,
                "handoff_type_histogram": handoff_histogram,
                "selected_word_histogram": word_histogram,
                "length_histogram": length_histogram,
                "surplus_histogram": surplus_histogram,
                "interpretation": (
                    "the exact singleton-pair/carry equation survives changes "
                    "in background masses, partitions, incoming mass, and "
                    "identity versus atom-bijection handoff"
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
                "Pi_up_entry_and_source_distinguished": (
                    "exact replay in kappa_4^ISE"
                ),
                "Pi_C_and_current_distinguished": "typed rank-four source context",
                "atomwise_role_transport": "F3-certified handoff eta",
            },
            "support_rows": support_rows,
        },
        "schema_subsumption": {
            "definition": (
                "g <= h iff RelevantBranch_g^ISE implies "
                "RelevantBranch_h^ISE on every typed provenance"
            ),
            "relation": "FPC <= GFPC",
            "status": "PROVED_BY_CLAUSE_WEAKENING",
            "proof": [
                "FPC supplies rank-five to rank-four exact replay",
                "FPC supplies distinct singleton parents and a mass-two entry packet",
                "FPC maps that entry packet to the current distinguished packet",
                "FPC carries its heavy packet and two singleton spectators atomwise",
                "FPC makes the incoming distinguished heavy packet a carried nonparent",
                "GFPC drops FPC background-mass and partition restrictions",
            ],
            "audited_FPC_rows_contained": len(gfpc_cand2_ids),
            "strictness": {
                "status": "STRICT_ON_DECLARED_FIXED_SCOPE",
                "GFPC_supported_but_FPC_unsupported_ext_witnesses": len(
                    strict_ext_witnesses
                ),
            },
            "completion_inheritance": False,
            "completion_note": (
                "branch-domain inclusion does not extend FPC completion to the "
                "new ext part of GFPC"
            ),
        },
        "reduced_family_view": {
            "candidate": ["OW", "GFPC", "PEC"],
            "status": "NOT_DECLARED_MINIMAL",
            "historical_family_preserved": EXPANDED_FAMILY,
        },
        "summary": {
            "pooled_provenances": len(profiles),
            "GFPC_supported_provenances": supported_count,
            "by_pool": by_pool,
            "source_partition_histogram": source_partition_histogram,
            "current_partition_histogram": current_partition_histogram,
            "background_mass_profile_histogram": background_histogram,
            "incoming_distinguished_mass_histogram": incoming_mass_histogram,
            "handoff_type_histogram": handoff_histogram,
            "FPC_subsumed_rows": len(gfpc_cand2_ids),
            "strict_ext_witnesses": len(strict_ext_witnesses),
            "result": "FOURTH_SCHEMA_DECLARED_WITH_FPC_SUBSUMPTION",
        },
        "claim_boundary": {
            "proved": [
                "all 83 pooled provenances satisfy the anonymous exact fresh-pair/carry role equation",
                "the GFPC branch predicate is future-free and provenance-sensitive",
                "FPC is a strict branch-domain specialization of GFPC on the declared fixed scopes",
                "the expanded family preserves FPC as a historical theorem object",
            ],
            "not_proved": [
                "GFPC component completion on cand2 or ext",
                "inheritance of FPC completion by GFPC",
                "minimality of {OW,GFPC,PEC}",
                "realizability or projectability for arbitrary background masses",
                "all-n projectability, support cover, or GFPC completion",
                "F5 from the enlarged family",
                "equality of a fixed-scope adapter with Lambda_4^complete(C)",
            ],
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    input_paths: Mapping[str, Path],
) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "anonymous_profile_payload_sha256": payload[
                "anonymous_role_analysis"
            ]["anonymous_profile_payload_sha256"],
        },
        "inputs": {
            key: {"name": path.name, "sha256": _sha256(path)}
            for key, path in sorted(input_paths.items())
        },
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
        "--cand2-projectability",
        type=Path,
        default=DEFAULT_CAND2_PROJECTABILITY,
    )
    parser.add_argument(
        "--fpc-declaration", type=Path, default=DEFAULT_FPC_DECLARATION
    )
    parser.add_argument("--prior-family", type=Path, default=DEFAULT_PRIOR_FAMILY)
    parser.add_argument("--ext-support", type=Path, default=DEFAULT_EXT_SUPPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    input_paths = {
        "cand2_projectability": args.cand2_projectability,
        "ext_support": args.ext_support,
        "fpc_declaration": args.fpc_declaration,
        "prior_family": args.prior_family,
    }
    payload = build_payload(
        cand2_projectability_path=args.cand2_projectability,
        fpc_declaration_path=args.fpc_declaration,
        prior_family_path=args.prior_family,
        ext_support_path=args.ext_support,
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(output=args.out, payload=payload, input_paths=input_paths),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "anonymous_profile_payload_sha256": payload[
                    "anonymous_role_analysis"
                ]["anonymous_profile_payload_sha256"],
                **payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
