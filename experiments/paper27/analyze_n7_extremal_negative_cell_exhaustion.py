#!/usr/bin/env python3
"""Expose complete shallow relations in the five negative n=7 carrier cells.

The producer does not search new contexts.  It projects the frozen complete C4
macro relation for the five menu-bad directions, retaining the typed post-tag
states and the full rank-three continuation relation needed by Gamma(Y, t).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analyze_n7_extremal_colored_obstructions import CHANNEL_C4
from analyze_n7_extremal_direct_complement import (
    _apply_prefix,
    _corridor_source,
    _role_coordinate,
)
from analyze_n7_extremal_edge_germs import _representative_germs
from analyze_n7_extremal_failure_equations import (
    SCHEMA as FAILURE_SCHEMA,
)
from analyze_n7_extremal_failure_equations import (
    _typed_equation,
)
from analyze_n7_extremal_moved_slot_menu import (
    INPUT_SCHEMA as CHANNEL_SCHEMA,
)
from analyze_n7_extremal_moved_slot_menu import (
    _landing_offset,
    _source_role_state,
)
from mass_maturity_legacy import mass_rank, simplified_deadline
from section_return_core import CompleteExitOracle, ExitOracle, digest_payload

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_NEGATIVE_CELL_EXHAUSTION_V1"
N = 7

EXPECTED_SPECTRA = {
    ((1, 3, 2), 2, 3, "IDENTITY"): ({2, 4, 5}, {2, 4, 5}),
    ((2, 1, 3), 2, 3, "IDENTITY"): ({3, 4, 5}, {4}),
    ((2, 1, 3), 2, 3, "SWAP"): ({4}, set()),
    ((2, 1, 3), 2, 4, "IDENTITY"): ({2, 3, 4, 5}, {3, 5}),
    ((3, 2, 1), 3, 3, "IDENTITY"): (set(), set()),
}

RoleState = dict[int, frozenset[str]]
ROLE_MASS = {"F4": 2, "D1": 2, "D2": 2, "s": 1}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _candidate_semantics(candidate: dict[str, Any] | None) -> str:
    if candidate is None:
        return "null"
    semantic = dict(candidate)
    semantic.pop("candidate_corridor_word", None)
    return _canonical(semantic)


def _serialize_role_state(state: RoleState) -> list[dict[str, Any]]:
    return [
        {"coordinate": int(coordinate), "roles": sorted(packet)}
        for coordinate, packet in sorted(state.items())
    ]


def _kinematic_return_rotations(
    state: RoleState,
    incoming_role: str,
    defect: tuple[int, ...],
) -> list[int]:
    x_f = _role_coordinate(state, "F4")
    y_incoming = _role_coordinate(state, incoming_role)
    result = []
    for exponent in range(N):
        images = [defect[(coordinate + exponent) % N] for coordinate in state]
        if len(set(images)) != len(state):
            continue
        x_image = defect[(x_f + exponent) % N]
        y_image = defect[(y_incoming + exponent) % N]
        if (y_image - x_image) % N in {1, N - 1}:
            result.append(exponent)
    return result


def _role_mass(state: RoleState) -> tuple[int, ...]:
    return tuple(
        sum(ROLE_MASS[role] for role in state.get(coordinate, ()))
        for coordinate in range(N)
    )


def _fusion_parent_roles(
    state: RoleState,
    word: list[int],
    defect: tuple[int, ...],
) -> tuple[frozenset[str], frozenset[str]] | None:
    if not word or word[-1] != 1:
        return None
    boundary = _apply_prefix(state, word[:-1], defect)
    parents = [boundary.get(coordinate) for coordinate in (0, N - 1)]
    if any(parent is None for parent in parents):
        return None
    target = _apply_prefix(boundary, [1], defect)
    if len(target) != len(state) - 1:
        return None
    return parents[0], parents[1]  # type: ignore[return-value]


def _endpoint_minimum_length(
    exits: ExitOracle,
    source: tuple[int, ...],
    target: tuple[int, ...],
) -> int | None:
    return next(
        (
            int(row["length"])
            for row in exits.exits(source)
            if tuple(int(value) for value in row["target"]) == target
        ),
        None,
    )


def _other_double(incoming_role: str) -> str:
    if incoming_role == "D1":
        return "D2"
    if incoming_role == "D2":
        return "D1"
    raise AssertionError("incoming role is not a mass-two packet")


def _matches_parent_roles(
    parents: tuple[frozenset[str], frozenset[str]] | None,
    expected: set[frozenset[str]],
) -> bool:
    return parents is not None and set(parents) == expected


def _adjacent_terminal_rotation(
    state: RoleState,
    incoming_role: str,
) -> int:
    x_f = _role_coordinate(state, "F4")
    y_incoming = _role_coordinate(state, incoming_role)
    difference = (y_incoming - x_f) % N
    if difference == 1:
        return (-y_incoming) % N
    if difference == N - 1:
        return (-x_f) % N
    raise ValueError("active pair is not adjacent")


def _terminal_rotation_after_return(
    state: RoleState,
    incoming_role: str,
    defect: tuple[int, ...],
    return_rotation: int,
) -> tuple[int, RoleState]:
    returned = _apply_prefix(
        state,
        [0] * return_rotation + [1],
        defect,
    )
    try:
        exponent = _adjacent_terminal_rotation(returned, incoming_role)
    except ValueError:
        raise AssertionError("kinematic return did not make the active pair adjacent")
    return exponent, returned


def _typed_accounting_state(
    corridor: int,
    marked_prefix_length: int,
    association: dict[str, Any],
) -> dict[str, int]:
    entering = 0 if corridor == 1 else int(association["surplus_first"])
    return {
        "surplus_entering_corridor": entering,
        "marked_prefix_cost": marked_prefix_length,
        "running_balance_after_tag": entering - marked_prefix_length,
    }


def _x_provenance(
    context: dict[str, Any],
    relation: dict[str, Any],
) -> dict[str, Any]:
    corridor = int(relation["corridor"])
    association = relation["association"]
    marked_prefix_length = int(relation["marked_letter_index"]) + 1
    corridor_word = association["first_word" if corridor == 1 else "second_word"]
    source = _source_role_state(context)
    if corridor == 2:
        defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
        source = _apply_prefix(source, association["first_word"], defect)
    return {
        "marked_prefix_word": [int(value) for value in corridor_word[:marked_prefix_length]],
        "corridor_source_role_state": _serialize_role_state(source),
        "accounting_state": _typed_accounting_state(
            corridor,
            marked_prefix_length,
            association,
        ),
    }


def _candidate_second_continuations(
    intermediate: RoleState,
    incoming_role: str,
    first_surplus: int,
    defect: tuple[int, ...],
    exits: ExitOracle,
) -> list[dict[str, Any]]:
    remaining = _other_double(incoming_role)
    expected = {
        frozenset({"F4", incoming_role}),
        frozenset({remaining}),
    }
    source_mass = _role_mass(intermediate)
    rows = []
    for exit_row in exits.exits(source_mass):
        word = [int(value) for value in exit_row["word"]]
        parents = _fusion_parent_roles(intermediate, word, defect)
        if not _matches_parent_roles(parents, expected):
            continue
        rows.append(
            {
                "word": word,
                "length": int(exit_row["length"]),
                "surplus": int(exit_row["surplus"]),
                "repays_first_debt": int(exit_row["surplus"]) >= -first_surplus,
                "target_mass": [int(value) for value in exit_row["target"]],
                "final_singleton_offset": _role_coordinate(
                    _apply_prefix(intermediate, word, defect),
                    "s",
                ),
            }
        )
    return rows


def _shallow_candidate(
    context: dict[str, Any],
    x: dict[str, Any],
    provenance: dict[str, Any],
    return_rotation: int | None,
    exits: ExitOracle,
) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    post_tag = {
        int(item["coordinate"]): frozenset(str(role) for role in item["roles"])
        for item in x["post_tag_role_state"]
    }
    source = {
        int(item["coordinate"]): frozenset(str(role) for role in item["roles"])
        for item in provenance["corridor_source_role_state"]
    }
    if return_rotation is None:
        terminal_rotation = _adjacent_terminal_rotation(
            post_tag,
            str(x["incoming_role"]),
        )
        suffix = [0] * terminal_rotation + [1]
    else:
        terminal_rotation, _ = _terminal_rotation_after_return(
            post_tag,
            str(x["incoming_role"]),
            defect,
            return_rotation,
        )
        suffix = (
            [0] * return_rotation
            + [1]
            + [0] * terminal_rotation
            + [1]
        )
    word = list(provenance["marked_prefix_word"]) + suffix
    target = _apply_prefix(source, word, defect)
    source_mass = _role_mass(source)
    target_mass = _role_mass(target)
    minimum = _endpoint_minimum_length(exits, source_mass, target_mass)
    normalized = minimum is not None and len(word) == minimum
    incoming = str(x["incoming_role"])
    corridor = int(x["corridor"])
    parents = _fusion_parent_roles(source, word, defect)

    if corridor == 1:
        role_ok = _matches_parent_roles(
            parents,
            {frozenset({"F4"}), frozenset({incoming})},
        )
        first_surplus = (
            simplified_deadline(target_mass, N)
            - simplified_deadline(source_mass, N)
            - len(word)
        )
        continuations = (
            _candidate_second_continuations(
                target,
                incoming,
                first_surplus,
                defect,
                exits,
            )
            if role_ok and mass_rank(target_mass) == 3
            else []
        )
        role_completion_exists = bool(continuations)
        accounting_ok = first_surplus < 0 and any(
            row["repays_first_debt"] for row in continuations
        )
        accounting = {
            "first_surplus": first_surplus,
            "role_compatible_second_corridors": len(continuations),
            "repaying_second_corridors": sum(
                int(row["repays_first_debt"]) for row in continuations
            ),
        }
        landing_offsets = sorted(
            {
                int(row["final_singleton_offset"])
                for row in continuations
                if row["repays_first_debt"]
            }
        )
    else:
        other = _other_double(incoming)
        role_ok = _matches_parent_roles(
            parents,
            {
                frozenset({"F4", other}),
                frozenset({incoming}),
            },
        )
        entering = int(provenance["accounting_state"]["surplus_entering_corridor"])
        corridor_surplus = (
            simplified_deadline(target_mass, N)
            - simplified_deadline(source_mass, N)
            - len(word)
        )
        role_completion_exists = role_ok
        accounting_ok = entering < 0 and entering + corridor_surplus >= 0
        accounting = {
            "first_surplus": entering,
            "second_surplus": corridor_surplus,
            "total_surplus": entering + corridor_surplus,
        }
        continuations = []
        landing_offsets = (
            [_role_coordinate(target, "s")]
            if role_completion_exists and accounting_ok
            else []
        )

    predicted_admitted = role_completion_exists and normalized and accounting_ok
    if not role_completion_exists:
        rejection = "ROLE_COMPLETION"
    elif normalized and accounting_ok:
        rejection = None
    elif not normalized and not accounting_ok:
        rejection = "NORMALIZATION_AND_ACCOUNTING"
    elif not normalized:
        rejection = "NORMALIZATION"
    else:
        rejection = "ACCOUNTING"
    return {
        "kind": "DIRECT" if return_rotation is None else "ONE_RETURN",
        "return_rotation_exponent": return_rotation,
        "terminal_rotation_exponent": terminal_rotation,
        "candidate_corridor_word": word,
        "candidate_corridor_length": len(word),
        "endpoint_minimum_length": minimum,
        "target_mass": list(target_mass),
        "role_completion_exists": role_completion_exists,
        "endpoint_normalized": normalized,
        "accounting_admissible": accounting_ok,
        "accounting": accounting,
        "role_compatible_second_corridors": continuations,
        "admitted_landing_offsets": landing_offsets if normalized else [],
        "predicted_admitted": predicted_admitted,
        "rejection_basis": rejection,
    }


def _typed_rank3_state(
    context: dict[str, Any], representative: dict[str, Any]
) -> tuple[dict[str, Any], RoleState]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    edge = representative["edge"]
    rank3 = _apply_prefix(_source_role_state(context), edge["first_word"], defect)
    if len(rank3) != 3:
        raise AssertionError("first C4 corridor did not produce rank three")
    typed = {
        "role_state": _serialize_role_state(rank3),
        "mass": [int(value) for value in edge["intermediate"]],
        "length_first": int(edge["length_first"]),
        "surplus_first": int(edge["surplus_first"]),
        "debt_required": int(edge["debt_required"]),
        "maximum_length_second_under_debt": 13 - int(edge["debt_required"]),
        "second_fusion_roles": list(representative["second_fusion_roles"]),
    }
    return typed, rank3


def _continuation(
    context: dict[str, Any],
    representative: dict[str, Any],
    rank3: RoleState,
) -> dict[str, Any]:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    edge = representative["edge"]
    target = _apply_prefix(rank3, edge["second_word"], defect)
    if len(target) != 2:
        raise AssertionError("second C4 corridor did not produce rank two")
    final_singleton = _role_coordinate(target, "s")
    if final_singleton != _landing_offset(representative):
        raise AssertionError("continuation singleton landing drift")
    return {
        "word": [int(value) for value in edge["second_word"]],
        "length": int(edge["length_second"]),
        "surplus": int(edge["surplus_second"]),
        "final_singleton_offset": int(final_singleton),
        "target_mass": [int(value) for value in edge["target"]],
        "target_role_state": _serialize_role_state(target),
    }


def _gamma_relation(
    context: dict[str, Any], representatives: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    groups: dict[str, dict[str, Any]] = {}
    representative_to_y: dict[str, str] = {}
    for representative in representatives:
        typed, rank3 = _typed_rank3_state(context, representative)
        key = _canonical(typed)
        y_id = digest_payload(typed)
        continuation = _continuation(context, representative, rank3)
        row = groups.setdefault(
            key,
            {
                "Y_id": y_id,
                "Y": typed,
                "t": int(_role_coordinate(rank3, "s")),
                "continuations": {},
            },
        )
        if row["t"] != _role_coordinate(rank3, "s"):
            raise AssertionError("typed Y acquired two singleton coordinates")
        row["continuations"][_canonical(continuation)] = continuation
        representative_to_y[_canonical(representative)] = key

    result = {}
    for key, row in groups.items():
        continuations = [
            row["continuations"][item] for item in sorted(row["continuations"])
        ]
        result[key] = {
            "Y_id": row["Y_id"],
            "Y": row["Y"],
            "t": row["t"],
            "Gamma_image": sorted(
                {item["final_singleton_offset"] for item in continuations}
            ),
            "continuations": continuations,
        }
    return result, representative_to_y


def _post_tag_state(
    context: dict[str, Any],
    representative: dict[str, Any],
    event: dict[str, Any],
) -> RoleState:
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    edge = representative["edge"]
    word = edge["first_word" if event["corridor"] == 1 else "second_word"]
    source = _corridor_source(context, representative, int(event["corridor"]))
    return _apply_prefix(source, word[: int(event["letter_index"]) + 1], defect)


def _relation_member(
    context: dict[str, Any],
    representative: dict[str, Any],
    event: dict[str, Any],
    y_key: str,
    gamma: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    equation = _typed_equation(context, representative, event)
    edge = representative["edge"]
    post_tag = _post_tag_state(context, representative, event)
    row = {
        "corridor": int(event["corridor"]),
        "depth": int(event["rank_preserving_d_after"]),
        "incoming_role": str(event["incoming_role"]),
        "marked_letter_index": int(event["letter_index"]),
        "post_tag_role_state": _serialize_role_state(post_tag),
        "return_rotation_exponent": equation["return_rotation_exponent"],
        "terminal_rotation_exponent": equation["terminal_rotation_exponent"],
        "active_triple": equation["active_triple"],
        "landing_equation": equation["landing_equation"],
        "association": {
            "first_word": [int(value) for value in edge["first_word"]],
            "second_word": [int(value) for value in edge["second_word"]],
            "length_first": int(edge["length_first"]),
            "length_second": int(edge["length_second"]),
            "surplus_first": int(edge["surplus_first"]),
            "surplus_second": int(edge["surplus_second"]),
            "debt_required": int(edge["debt_required"]),
            "first_fusion_roles": list(representative["first_fusion_roles"]),
            "second_fusion_roles": list(representative["second_fusion_roles"]),
            "target_mass": [int(value) for value in edge["target"]],
            "target_packets": representative["target_packets"],
        },
    }
    if event["corridor"] == 1:
        gamma_row = gamma[y_key]
        row["Y_id"] = gamma_row["Y_id"]
        row["rank3_singleton_coordinate"] = gamma_row["t"]
        row["Gamma_image"] = gamma_row["Gamma_image"]
    return row


def _cell(bad: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    slot = int(bad["j"])
    defect = tuple(int(value) for value in context["source_geometry"]["defect_map"])
    slot_coordinates = {1: 1, 2: 2, 3: int(bad["h"])}
    representatives = list(context["channel_relations"][CHANNEL_C4])
    gamma, representative_to_y = _gamma_relation(context, representatives)
    members: dict[int, dict[str, dict[str, Any]]] = {0: {}, 1: {}}

    for representative in representatives:
        y_key = representative_to_y[_canonical(representative)]
        events = _representative_germs(context, representative, slot_coordinates).get(
            slot, []
        )
        for event in events:
            depth = int(event["rank_preserving_d_after"])
            if depth not in members:
                continue
            relation = _relation_member(context, representative, event, y_key, gamma)
            members[depth][_canonical(relation)] = relation

    direct = [members[0][key] for key in sorted(members[0])]
    returned = [members[1][key] for key in sorted(members[1])]
    direct_spectrum = sorted(
        {row["landing_equation"]["final_singleton_offset"] for row in direct}
    )
    return_spectrum = sorted(
        {row["landing_equation"]["final_singleton_offset"] for row in returned}
    )
    identity = (
        tuple(int(value) for value in bad["alpha"]),
        slot,
        int(bad["h"]),
        str(bad["beta"]),
    )
    expected_direct, expected_return = EXPECTED_SPECTRA[identity]
    if set(direct_spectrum) != expected_direct:
        raise AssertionError(f"direct negative spectrum drift: {identity}")
    if set(return_spectrum) != expected_return:
        raise AssertionError(f"return negative spectrum drift: {identity}")

    referenced_y = {row["Y_id"] for row in direct + returned if row["corridor"] == 1}
    gamma_rows = sorted(
        (row for row in gamma.values() if row["Y_id"] in referenced_y),
        key=lambda row: row["Y_id"],
    )
    x_rows: dict[str, dict[str, Any]] = {}
    provenance_by_x: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    direct_landing_by_x: dict[str, set[int]] = defaultdict(set)
    q_by_x: dict[str, set[int]] = defaultdict(set)
    for row in direct + returned:
        marked_prefix_length = int(row["marked_letter_index"]) + 1
        provenance = _x_provenance(context, row)
        x = {
            "corridor": row["corridor"],
            "incoming_role": row["incoming_role"],
            "marked_prefix_length": marked_prefix_length,
            "accounting_state": provenance["accounting_state"],
            "corridor_source_role_state": provenance[
                "corridor_source_role_state"
            ],
            "post_tag_role_state": row["post_tag_role_state"],
        }
        key = _canonical(x)
        x_rows[key] = {"X_id": digest_payload(x), **x}
        provenance_by_x[key][_canonical(provenance)] = provenance
        if row["depth"] == 0:
            direct_landing_by_x[key].add(
                int(row["landing_equation"]["final_singleton_offset"])
            )
        else:
            q_by_x[key].add(int(row["return_rotation_exponent"]))
    exits = CompleteExitOracle(
        (tuple((coordinate + 1) % N for coordinate in range(N)), defect),
        N,
    )
    post_tag_rows = []
    for key in sorted(x_rows):
        row = x_rows[key]
        provenances = sorted(
            provenance_by_x[key].values(),
            key=_canonical,
        )
        post_tag_state = {
            int(item["coordinate"]): frozenset(str(role) for role in item["roles"])
            for item in row["post_tag_role_state"]
        }
        kinematic = _kinematic_return_rotations(
            post_tag_state,
            str(row["incoming_role"]),
            defect,
        )
        relation_observed = sorted(q_by_x[key])
        gate_audits = [
            [
                _shallow_candidate(
                    context,
                    row,
                    provenance,
                    return_rotation,
                    exits,
                )
                for return_rotation in kinematic
            ]
            for provenance in provenances
        ]
        semantic_gate_audits = {
            tuple(_candidate_semantics(candidate) for candidate in audit)
            for audit in gate_audits
        }
        if len(semantic_gate_audits) != 1:
            raise AssertionError(
                "equivalent marked prefixes induce different one-return gates"
            )
        gate_audit = gate_audits[0]
        for candidate in gate_audit:
            observed = candidate["return_rotation_exponent"] in relation_observed
            candidate["relation_observed"] = observed
            candidate["relation_completeness_gap"] = (
                candidate["predicted_admitted"] != observed
            )
        admitted = sorted(
            int(candidate["return_rotation_exponent"])
            for candidate in gate_audit
            if candidate["predicted_admitted"]
        )
        direct_audits = []
        for provenance in provenances:
            try:
                direct_audits.append(
                    _shallow_candidate(
                        context,
                        row,
                        provenance,
                        None,
                        exits,
                    )
                )
            except ValueError:
                direct_audits.append(None)
        if len({_candidate_semantics(audit) for audit in direct_audits}) != 1:
            raise AssertionError(
                "equivalent marked prefixes induce different direct gates"
            )
        direct_audit = direct_audits[0]
        if direct_audit is not None:
            observed_landings = sorted(direct_landing_by_x[key])
            direct_audit["relation_observed_landing_offsets"] = observed_landings
            direct_audit["relation_completeness_gap"] = (
                sorted(direct_audit["admitted_landing_offsets"])
                != observed_landings
            )
        post_tag_rows.append(
            {
                **row,
                "prefix_provenances": provenances,
                "prefix_transport_is_gate_invariant": True,
                "kinematic_one_return_rotations": kinematic,
                "relation_observed_one_return_rotations": relation_observed,
                "admissible_one_return_rotations": admitted,
                "one_return_gate_audit": gate_audit,
                "direct_gate_audit": direct_audit,
            }
        )

    complete_direct_spectrum = {
        int(offset)
        for row in post_tag_rows
        if row["direct_gate_audit"] is not None
        and row["direct_gate_audit"]["predicted_admitted"]
        for offset in row["direct_gate_audit"]["admitted_landing_offsets"]
    }
    complete_return_spectrum = {
        int(offset)
        for row in post_tag_rows
        for candidate in row["one_return_gate_audit"]
        if candidate["predicted_admitted"]
        for offset in candidate["admitted_landing_offsets"]
    }
    if complete_direct_spectrum != expected_direct:
        raise AssertionError(f"gate-complete direct spectrum drift: {identity}")
    if complete_return_spectrum != expected_return:
        raise AssertionError(f"gate-complete return spectrum drift: {identity}")

    return {
        "defect": bad["defect"],
        "alpha": [int(value) for value in bad["alpha"]],
        "j": slot,
        "h": int(bad["h"]),
        "beta": str(bad["beta"]),
        "directed_low_edge": [int(value) for value in bad["directed_low_edge"]],
        "source_geometry": context["source_geometry"],
        "C4_representative_count": len(representatives),
        "post_tag_states": post_tag_rows,
        "D": direct,
        "R": returned,
        "Gamma": gamma_rows,
        "relation_observed_direct_landing_spectrum": direct_spectrum,
        "direct_landing_spectrum": sorted(complete_direct_spectrum),
        "relation_observed_one_return_landing_spectrum": return_spectrum,
        "one_return_landing_spectrum": sorted(complete_return_spectrum),
        "long_germ": None,
    }


def build_payload(failure_path: Path) -> dict[str, Any]:
    failure = json.loads(failure_path.read_text(encoding="utf-8", newline="\n"))
    if failure.get("schema") != FAILURE_SCHEMA:
        raise AssertionError("unexpected failure-equation schema")
    channel_input = next(
        row for row in failure["inputs"] if row["schema"] == CHANNEL_SCHEMA
    )
    channel_path = ROOT / channel_input["path"]
    if _sha256(channel_path) != channel_input["sha256"]:
        raise AssertionError("failure artifact no longer binds its channel input")
    channel = json.loads(channel_path.read_text(encoding="utf-8", newline="\n"))
    if channel.get("schema") != CHANNEL_SCHEMA:
        raise AssertionError("unexpected extremal channel schema")
    context_by_defect = {row["defect"]: row for row in channel["contexts"]}
    bad_rows = [
        row
        for row in failure["complement"]
        if row["observed_mechanism"] == "BAD_DIRECTION"
    ]
    if len(bad_rows) != 5:
        raise AssertionError("negative-cell scope drift")

    cells = [
        _cell(row, context_by_defect[row["defect"]])
        for row in sorted(
            bad_rows,
            key=lambda item: (
                tuple(item["alpha"]),
                int(item["j"]),
                int(item["h"]),
                str(item["beta"]),
            ),
        )
    ]
    one_return_candidates = [
        candidate
        for row in cells
        for state in row["post_tag_states"]
        for candidate in state["one_return_gate_audit"]
    ]
    direct_candidates = [
        state["direct_gate_audit"]
        for row in cells
        for state in row["post_tag_states"]
        if state["direct_gate_audit"] is not None
    ]
    one_return_profile = Counter(
        candidate["rejection_basis"] or "ADMITTED"
        for candidate in one_return_candidates
    )
    direct_profile = Counter(
        candidate["rejection_basis"] or "ADMITTED"
        for candidate in direct_candidates
    )
    if one_return_profile.get("ROLE_COMPLETION", 0):
        raise AssertionError("one-return audit exposed an untyped role gate")
    if direct_profile.get("ROLE_COMPLETION", 0):
        raise AssertionError("direct audit exposed an untyped role gate")
    relation_completeness_gaps = sum(
        int(candidate["relation_completeness_gap"])
        for candidate in one_return_candidates + direct_candidates
    )
    if relation_completeness_gaps:
        raise AssertionError(
            "complete relation disagrees with normalization/accounting admission"
        )
    counts = {
        "negative_cells": len(cells),
        "complete_C4_representatives": sum(
            row["C4_representative_count"] for row in cells
        ),
        "post_tag_states": sum(len(row["post_tag_states"]) for row in cells),
        "kinematic_one_return_exponents": sum(
            len(state["kinematic_one_return_rotations"])
            for row in cells
            for state in row["post_tag_states"]
        ),
        "relation_observed_one_return_exponents": sum(
            len(state["relation_observed_one_return_rotations"])
            for row in cells
            for state in row["post_tag_states"]
        ),
        "admitted_one_return_exponents": sum(
            len(state["admissible_one_return_rotations"])
            for row in cells
            for state in row["post_tag_states"]
        ),
        "relation_completeness_gaps": relation_completeness_gaps,
        "kinematic_direct_candidates": len(direct_candidates),
        "admitted_direct_candidates": sum(
            int(candidate["predicted_admitted"])
            for candidate in direct_candidates
        ),
        "direct_relation_members": sum(len(row["D"]) for row in cells),
        "one_return_relation_members": sum(len(row["R"]) for row in cells),
        "typed_Gamma_states": sum(len(row["Gamma"]) for row in cells),
        "Gamma_continuations": sum(
            len(gamma["continuations"]) for row in cells for gamma in row["Gamma"]
        ),
    }
    payload = {
        "schema": SCHEMA,
        "n": N,
        "inputs": [
            {
                "path": str(failure_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(failure_path),
                "schema": failure["schema"],
                "projection_digest": failure["projection_digest"],
            },
            {
                "path": str(channel_path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(channel_path),
                "schema": channel["schema"],
                "projection_digest": channel["projection_digest"],
            },
        ],
        "scope": {
            "domain": "the five menu-bad transposition directions only",
            "relation": (
                "the complete tied-shortest endpoint relation plus an independent "
                "normalization/accounting audit of every direct and one-return "
                "candidate on the typed post-tag states"
            ),
            "Gamma": (
                "all admissible second corridors attached to each referenced "
                "typed rank-three state Y before any landing or P2 filter"
            ),
            "forbidden_inputs": [
                "P_2/P_3 membership",
                "completion success labels",
                "W^(2C)",
                "reset coaccessibility",
                "Bellman policy",
            ],
        },
        "counts": counts,
        "one_return_admission_profile": dict(sorted(one_return_profile.items())),
        "direct_admission_profile": dict(sorted(direct_profile.items())),
        "cells": cells,
        "claims": [
            "Only the five universal-negative cells are exhaustively projected.",
            "First-corridor landing is the set-valued composition through Gamma(Y,t).",
            (
                "Role completion adds no third admission gate on this scope: "
                "endpoint normalization and accounting exactly recover the complete "
                "direct and one-return relation."
            ),
            (
                "All tied endpoint-shortest words are retained before packet-role "
                "and landing tests."
            ),
            "All five direct and one-return spectra avoid offset one.",
        ],
        "source_closure": [
            {
                "path": str(path.resolve().relative_to(ROOT).as_posix()),
                "sha256": _sha256(path),
            }
            for path in (
                Path(__file__),
                Path(__file__).with_name("analyze_n7_extremal_failure_equations.py"),
                Path(__file__).with_name("analyze_n7_extremal_direct_complement.py"),
                Path(__file__).with_name("analyze_n7_extremal_colored_obstructions.py"),
                Path(__file__).with_name("analyze_n7_extremal_edge_germs.py"),
                Path(__file__).with_name("analyze_n7_extremal_moved_slot_menu.py"),
                Path(__file__).with_name("section_return_core.py"),
            )
        ],
    }
    payload["projection_digest"] = digest_payload(
        {
            "counts": counts,
            "one_return_admission_profile": payload["one_return_admission_profile"],
            "direct_admission_profile": payload["direct_admission_profile"],
            "cells": cells,
        }
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("failure_equation_artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.failure_equation_artifact)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "counts": payload["counts"],
                "projection_digest": payload["projection_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
