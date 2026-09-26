#!/usr/bin/env python3
"""Prepare the future-free P28.5a rank-five section-return candidate.

This producer deliberately stops before evaluating `Good_5`. It constructs
the source section, abstract menus, and exact generator-path lift fibers using
only source-local data. It freezes that construction payload and its digest
before loading the independently released rank-four target section.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from mass_maturity_legacy import mass_rank
from paper28_factor_boundary_generators import _factor_receipt
from paper28_mechanism_schema import SCHEMA as MECHANISM_RECEIPT_SCHEMA
from paper28_mechanism_schema import exact_receipt_sha256, validate_receipt
from paper28_project_seed_mechanisms import (
    Context,
    _corridor_boundary,
    _debt_profile,
    _fusion_exact,
    _fusion_skeleton,
    _participation_type,
    _target_budget,
)
from section_return_core import (
    CompleteExitOracle,
    ExitOracle,
    activated_choice_key,
    activated_edge_summary,
    packet_mass,
    push_packets,
)

SCHEMA = "paper28-rank5-section-return-candidate-v1"
RECEIPT_SCHEMA = "paper28-rank5-section-return-candidate-receipt-v1"
LOWER_SECTION_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "results" / "paper28_rank5_section_candidate_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_prepare_rank5_section_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_rank5_section_candidate.py",
)

N = 7
CYCLE = tuple(range(1, N)) + (0,)
P2D_WORD = (0, 0, 1)
PREDECESSOR_WORD = (0,) * (N - 1) + (1,)
FORBIDDEN_CONSTRUCTION_FIELDS = (
    "good_5",
    "lower_section_member",
    "target_in_lower_section",
    "successful_channel",
    "successful_exact_lift",
    "winning",
    "bellman",
    "reset_coaccessibility",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def _read(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _defect_text(defect: Sequence[int]) -> str:
    return "".join(str(int(value)) for value in defect)


def _carrier_actions() -> list[tuple[int, ...]]:
    """Return the action-local 36-row packet-recursion carrier."""

    actions = []
    for images in itertools.permutations(range(1, 6)):
        defect = (0, *images, 0)
        if {4, 5}.issubset({defect[3], defect[4], defect[5]}):
            actions.append(defect)
    actions.sort()
    if len(actions) != 36:
        raise AssertionError("action-local carrier no longer has 36 rows")
    return actions


def _is_predecessor_idempotent(defect: Sequence[int]) -> bool:
    return (
        tuple(int(defect[int(defect[index])]) for index in range(N))
        == tuple(int(value) for value in defect)
        and {index for index, image in enumerate(defect) if int(image) == 0}
        == {0, 6}
    )


def _rank5_source(
    defect: tuple[int, ...],
) -> tuple[Context | None, dict[str, Any]]:
    """Apply the independently declared Sigma_6 rule without target data."""

    letters = (CYCLE, defect)
    singleton_packets = {
        coordinate: frozenset((coordinate,)) for coordinate in range(N)
    }
    kernel_packets = push_packets(singleton_packets, defect)
    kernel_mass = packet_mass(kernel_packets, N)
    if mass_rank(kernel_mass) != 6:
        raise AssertionError("candidate action did not have rank-six kernel image")

    oracle = ExitOracle(letters, N)
    relation = [
        edge
        for edge in oracle.macro_edges(kernel_mass)
        if edge["type"] == "I" and int(edge["rank_target"]) == 5
    ]
    activated = [
        activated_edge_summary(
            edge, kernel_packets, letters, N, include_target_packets=True
        )[0]
        for edge in relation
    ]
    activated.sort(key=activated_choice_key)
    if not activated:
        raise AssertionError("candidate action has no Sigma_6 rank-five entry")

    predecessor = _is_predecessor_idempotent(defect)
    if predecessor:
        if _defect_text(defect) != "0123450":
            raise AssertionError("unexpected predecessor action")
        return None, {
            "defect": _defect_text(defect),
            "excluded": True,
            "exclusion_reason": "SIGMA6_PREDECESSOR_ORIENTED_RETURN",
            "sigma6_selected_word": list(PREDECESSOR_WORD),
        }

    selected_word = tuple(int(value) for value in activated[0]["first_word"])
    matches = [
        edge
        for edge in relation
        if tuple(int(value) for value in edge["first_word"]) == selected_word
    ]
    if selected_word != P2D_WORD or len(matches) != 1:
        raise AssertionError("non-predecessor carrier action lost its p^2 d entry")
    edge = matches[0]
    activated_row, rank5_packets = activated_edge_summary(
        edge, kernel_packets, letters, N, include_target_packets=True
    )
    fresh = frozenset(
        int(value) for value in activated_row["first_fusion"]["fresh_packet"]
    )
    context = Context(
        n=N,
        defect=defect,
        packets=rank5_packets,
        distinguished=fresh,
        origin=f"n7-rank5-candidate-{_defect_text(defect)}",
        seed_surface="N7_RANK5_EXTREMAL_PREDECESSOR_CANDIDATE",
        is_seed=True,
    )
    if tuple(sorted((value for value in context.mass if value), reverse=True)) != (
        2,
        2,
        1,
        1,
        1,
    ):
        raise AssertionError("rank-five candidate partition drift")
    membership = {
        "defect": _defect_text(defect),
        "excluded": False,
        "rooted_action_form": "d=(0,pi(1),...,pi(5),0)",
        "action_local_condition": "{4,5} subset pi({3,4,5})",
        "sigma6_selection_rule": (
            "predecessor-idempotent p^6 d; otherwise endpoint-shortest "
            "activated rank-six-to-five Type-I block"
        ),
        "sigma6_selected_word": list(P2D_WORD),
        "sigma6_fusion_parent_sizes": list(
            activated_row["first_fusion"]["parent_sizes"]
        ),
        "source_partition": [2, 2, 1, 1, 1],
        "normalized_mass_placement": list(context.mass),
        "fresh_packet": sorted(fresh),
        "fresh_coordinate": next(
            coordinate
            for coordinate, packet in context.packets.items()
            if packet == fresh
        ),
        "binary_kernel": [0, 6],
        "context": context.payload,
    }
    return context, membership


def _boundary_key(
    *,
    defect: Sequence[int],
    packets: Mapping[int, frozenset[int]],
    distinguished: frozenset[int],
) -> dict[str, Any]:
    distinguished_coordinates = [
        int(coordinate)
        for coordinate, packet in packets.items()
        if packet == distinguished
    ]
    if len(distinguished_coordinates) != 1:
        raise AssertionError("typed boundary lost its distinguished packet")
    root = distinguished_coordinates[0]
    return {
        "ambient_n": N,
        "defect": [int(value) for value in defect],
        "rank": len(packets),
        "distinguished_coordinate": root,
        "distinguished_mass": len(distinguished),
        "mass_rows": [
            {
                "coordinate": int(coordinate),
                "mass": len(packet),
                "offset_from_distinguished": (int(coordinate) - root) % N,
                "is_distinguished": packet == distinguished,
            }
            for coordinate, packet in sorted(packets.items())
        ],
    }


def _record_from_rank5_edge(
    context: Context,
    edge: Mapping[str, Any],
    *,
    relation_role: str = "RANK5_SECTION_CANDIDATE",
) -> dict[str, Any]:
    """Build a future-free exact receipt without a success observable."""

    letters = (CYCLE, context.defect)
    activated, target_packets = activated_edge_summary(
        dict(edge), context.packets, letters, N, include_target_packets=True
    )
    if edge["type"] != "I" or int(edge["rank_target"]) != 4:
        raise AssertionError("rank-five candidate lift is not one strict corridor")
    fusion = activated["first_fusion"]
    new_distinguished = frozenset(int(value) for value in fusion["fresh_packet"])
    target_context = Context(
        n=N,
        defect=context.defect,
        packets=target_packets,
        distinguished=new_distinguished,
        origin=context.origin,
        seed_surface=context.seed_surface,
        is_seed=False,
    )
    source_partition = sorted(
        (len(packet) for packet in context.packets.values()), reverse=True
    )
    target_partition = sorted(
        (len(packet) for packet in target_packets.values()), reverse=True
    )
    surplus = int(edge["surplus_first"])
    ancestry_update = {
        "incoming_distinguished_packet": sorted(context.distinguished),
        "participation_type": _participation_type(
            context.distinguished, [fusion]
        ),
        "outgoing_distinguished_packet": sorted(new_distinguished),
        "update_rule": "FINAL_STRICT_FUSION_PACKET",
    }
    exact_fusion = _fusion_exact(fusion)
    target_payload = target_context.payload
    record: dict[str, Any] = {
        "schema": MECHANISM_RECEIPT_SCHEMA,
        "receipt_id": "pending",
        "seed_surface": context.seed_surface,
        "relation_role": relation_role,
        "origin": context.origin,
        "skeleton": {
            "ambient_n": N,
            "source_rank": 5,
            "target_rank": 4,
            "source_partition": source_partition,
            "target_partition": target_partition,
            "corridor_count": 1,
            "rank_drop_vector": [1],
            "fusion_chain": _fusion_skeleton([fusion], context.distinguished),
            "ancestry_update_type": ancestry_update["participation_type"],
            "return_type": "ONE_CORRIDOR",
        },
        "accounting": {
            "corridors": [
                {
                    "rank_drop": 1,
                    "delta_m": int(fusion["parent_sizes"][0])
                    * int(fusion["parent_sizes"][1]),
                    "length": int(edge["length_first"]),
                    "surplus": surplus,
                }
            ],
            "debt_profile": _debt_profile([surplus]),
            "residual_tail_budget": _target_budget(edge["target"], N),
        },
        "exact": {
            "source_context_id": context.context_id,
            "source_packet_ids": [
                sorted(packet) for _, packet in sorted(context.packets.items())
            ],
            "words": [[int(value) for value in edge["first_word"]]],
            "corridor_boundaries": [
                _corridor_boundary(context.packets, edge["first_word"], letters)
            ],
            "fusion_packet_identities": [exact_fusion],
            "target_channel": {
                "target_context_id": target_payload["context_id"],
                "target_packets": target_payload["packets"],
                "outgoing_distinguished_packet": sorted(new_distinguished),
                "section_boundary_key": _boundary_key(
                    defect=context.defect,
                    packets=target_packets,
                    distinguished=new_distinguished,
                ),
            },
            "target_endpoint": [int(value) for value in edge["target"]],
            "target_context": target_payload,
            "ancestry_update": ancestry_update,
        },
        "observables": {
            "source_target_shape": {
                "source_rank": 5,
                "target_rank": 4,
                "source_partition": source_partition,
                "target_partition": target_partition,
            },
            "fusion_mass_pattern": [
                sorted(int(value) for value in fusion["parent_sizes"])
            ],
            "rank_drop_vector": [1],
            "corridor_count": 1,
            "corridor_lengths": [int(edge["length_first"])],
            "corridor_surpluses": [surplus],
            "debt_profile": _debt_profile([surplus]),
            "total_surplus": surplus,
            "residual_tail_budget": _target_budget(edge["target"], N),
            "exact_ancestry_update": ancestry_update,
            "source_packet_identity": [
                sorted(packet) for _, packet in sorted(context.packets.items())
            ],
            "fusion_packet_identity": [exact_fusion],
            "exact_target_transport_channel": {
                "target_context_id": target_payload["context_id"],
                "target_packets": target_payload["packets"],
                "outgoing_distinguished_packet": sorted(new_distinguished),
            },
        },
    }
    record["receipt_id"] = f"r5-{exact_receipt_sha256(record)[:24]}"
    validate_receipt(record)
    return record


def _factorization_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    factorization = _factor_receipt(record)
    return {
        "receipt_id": str(factorization["receipt_id"]),
        "source_state_id": str(factorization["source_state_id"]),
        "target_state_id": str(factorization["target_state_id"]),
        "operation_kind_path": list(factorization["operation_kind_path"]),
        "operation_occurrences": factorization["operation_occurrences"],
        "total_length": int(factorization["total_length"]),
        "total_surplus": int(factorization["total_surplus"]),
    }


def _construction_core(construction: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_contexts": construction["source_section"]["contexts"],
        "menu_contexts": construction["menus"]["contexts"],
        "exact_lifts": construction["exact_lifts"]["receipts"],
    }


def _build_source_menu_payload() -> dict[str, Any]:
    source_rows = []
    excluded_rows = []
    records = []
    factorizations = []
    menus = []

    for defect in _carrier_actions():
        context, membership = _rank5_source(defect)
        if membership["excluded"]:
            excluded_rows.append(membership)
            continue
        if context is None:
            raise AssertionError("included source lost its typed context")
        source_rows.append(membership)

        oracle = CompleteExitOracle((CYCLE, defect), N)
        rank4_edges = [
            edge
            for edge in oracle.macro_edges(context.mass)
            if int(edge["rank_target"]) == 4
        ]
        if not rank4_edges:
            raise AssertionError("rank-five candidate has no rank-four local lift")

        source_records = []
        for edge in rank4_edges:
            record = _record_from_rank5_edge(context, edge)
            records.append(record)
            source_records.append(record)
            factorizations.append(_factorization_summary(record))

        channels: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in source_records:
            channels[_digest(record["skeleton"])].append(record)
        channel_rows = []
        for channel_digest, channel_records in sorted(channels.items()):
            representative = channel_records[0]
            accounting: dict[str, list[str]] = defaultdict(list)
            for record in channel_records:
                accounting[_digest(record["accounting"])].append(
                    str(record["receipt_id"])
                )
            channel_rows.append(
                {
                    "channel_id": f"r5m-{channel_digest[:24]}",
                    "interaction_skeleton": representative["skeleton"],
                    "accounting_refinements": [
                        {
                            "accounting_id": f"r5a-{key[:24]}",
                            "accounting": next(
                                row["accounting"]
                                for row in channel_records
                                if _digest(row["accounting"]) == key
                            ),
                            "exact_lift_ids": sorted(receipt_ids),
                        }
                        for key, receipt_ids in sorted(accounting.items())
                    ],
                    "exact_lift_ids": sorted(
                        str(record["receipt_id"]) for record in channel_records
                    ),
                }
            )
        menus.append(
            {
                "source_context_id": context.context_id,
                "menu_size": len(channel_rows),
                "channels": channel_rows,
            }
        )

    if len(source_rows) != 35 or len(excluded_rows) != 1:
        raise AssertionError("rank-five candidate source count drift")
    if excluded_rows[0]["defect"] != "0123450":
        raise AssertionError("wrong source-local predecessor exclusion")

    records.sort(key=lambda row: str(row["receipt_id"]))
    factorizations.sort(key=lambda row: str(row["receipt_id"]))
    menus.sort(key=lambda row: str(row["source_context_id"]))
    source_rows.sort(key=lambda row: str(row["defect"]))

    factor_state_ids = {
        str(operation[side]["state_id"])
        for row in factorizations
        for operation in row["operation_occurrences"]
        for side in ("exact_source", "exact_target")
    }
    receipt_endpoint_ids = {
        str(row["source_state_id"]) for row in factorizations
    } | {str(row["target_state_id"]) for row in factorizations}
    construction = {
        "source_section": {
            "name": "Sec_5,cand^(7)",
            "membership_rule": (
                "rooted local-recursion action {4,5} subset pi({3,4,5}), "
                "followed by the intrinsic Sigma_6 selector; exclude the unique "
                "predecessor idempotent because Sigma_6 uses p^6 d rather than p^2 d"
            ),
            "forbidden_inputs": [
                "rank-four section membership",
                "Good_5",
                "lower-rank success",
                "winning or Bellman labels",
            ],
            "action_local_carrier_count": 36,
            "excluded_sources": excluded_rows,
            "context_count": len(source_rows),
            "contexts": source_rows,
        },
        "menus": {
            "constructor": (
                "all tied endpoint-shortest one-corridor rank-five-to-four "
                "receipts, quotiented only by the future-free interaction skeleton"
            ),
            "forbidden_inputs": list(FORBIDDEN_CONSTRUCTION_FIELDS),
            "context_count": len(menus),
            "channel_count": sum(row["menu_size"] for row in menus),
            "max_menu_size": max(row["menu_size"] for row in menus),
            "contexts": menus,
        },
        "exact_lifts": {
            "definition": (
                "complete source-addressed rank-five-to-four receipts factored "
                "through exact TRANSPORT/RETURN/FUSION operation paths"
            ),
            "receipt_count": len(records),
            "receipts": records,
            "factorizations": factorizations,
        },
        "checkpoint_type_audit": {
            "menu_source_context_count": len(source_rows),
            "exported_recursive_target_count": 0,
            "replay_state_count": len(factor_state_ids),
            "receipt_endpoint_state_count": len(receipt_endpoint_ids),
            "internal_only_state_count": len(
                factor_state_ids - receipt_endpoint_ids
            ),
            "internal_only_exported_as_checkpoint": 0,
        },
    }
    encoded = json.dumps(
        _construction_core(construction),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field.lower() in encoded:
            raise AssertionError(
                f"construction payload contains forbidden field: {field}"
            )
    return construction


def _project_lower_section(path: Path) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("schema") != LOWER_SECTION_SCHEMA:
        raise AssertionError("unexpected Paper XXVII lower-section schema")
    rows = []
    for context in payload["contexts"]:
        geometry = context["source_geometry"]
        f4_coordinate = int(geometry["F4_coordinate"])
        mass_rows = [
            {
                "coordinate": int(row["coordinate"]),
                "mass": int(row["mass"]),
                "offset_from_distinguished": (
                    int(row["coordinate"]) - f4_coordinate
                )
                % N,
                "is_distinguished": str(row["role"]).split("@", 1)[0] == "F4",
            }
            for row in geometry["packet_roles"]
        ]
        mass_rows.sort(key=lambda row: row["coordinate"])
        rows.append(
            {
                "authority": "Paper XXVII released Sec_4,ext^(7)",
                "defect": str(context["defect"]),
                "source_index": int(context["index"]),
                "section_boundary_key": {
                    "ambient_n": N,
                    "defect": [
                        int(value) for value in geometry["defect_map"]
                    ],
                    "rank": 4,
                    "distinguished_coordinate": f4_coordinate,
                    "distinguished_mass": 2,
                    "mass_rows": mass_rows,
                },
            }
        )
    rows.sort(key=lambda row: (row["defect"], row["source_index"]))
    if len(rows) != 35:
        raise AssertionError("released lower section no longer has 35 contexts")
    return {
        "name": "Sec_4,ext^(7)",
        "input_name": path.name,
        "input_schema": payload["schema"],
        "input_sha256": _sha256(path),
        "context_count": len(rows),
        "contexts": rows,
        "section_keys_sha256": _digest(
            [row["section_boundary_key"] for row in rows]
        ),
    }


def build_payload(lower_section_input: Path) -> dict[str, Any]:
    # This call completes before the lower-section file is opened.
    construction = _build_source_menu_payload()
    construction_digest = _digest(construction)

    # The independently certified target authority is projected only after
    # the source/menu/lift payload has been frozen.
    lower_section = _project_lower_section(lower_section_input)
    payload = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "source": "future-free extremal rank-five predecessor candidate",
            "target": "released Paper XXVII Sec_4,ext^(7)",
            "evaluation_status": "NOT_RUN",
            "nonclaim": (
                "this artifact defines source, menu, exact lifts, and lower "
                "section authority but does not evaluate Good_5"
            ),
        },
        "construction_phase_order": [
            "source_section",
            "future_free_menus_and_exact_lifts",
            "construction_payload_digest",
            "independent_lower_section_projection",
            "future_hostile_evaluator_not_run",
        ],
        "construction_payload_sha256": construction_digest,
        "construction": construction,
        "lower_section_target": lower_section,
        "evaluator": {
            "status": "ABSENT_BY_DESIGN",
            "good_predicate_defined_for_later_phase": (
                "Good_5(C,m) iff an exact lift in Lift_5(C,m) has target "
                "in Sec_4,ext^(7)"
            ),
            "evaluated_source_count": 0,
            "evaluated_channel_count": 0,
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, output: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    closure = []
    for relative in SOURCE_CLOSURE:
        path = HERE / relative
        closure.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "sha256": _sha256(path),
            }
        )
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_RELEASE_INPUT",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "construction_payload_sha256": payload[
                "construction_payload_sha256"
            ],
        },
        "inputs": {
            "paper27_lower_section": {
                "name": payload["lower_section_target"]["input_name"],
                "schema": payload["lower_section_target"]["input_schema"],
                "sha256": payload["lower_section_target"]["input_sha256"],
            }
        },
        "source_closure": closure,
    }


def _resolve_lower_section(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    release_root = os.environ.get("RIME_PAPER27_RELEASE_ROOT")
    if release_root:
        path = (
            Path(release_root)
            / "experiments"
            / "paper27"
            / "results"
            / "single_defect_n7_extremal_carrier_input_v1.json"
        )
        if path.exists():
            return path
    local = (
        HERE.parent
        / "paper27"
        / "results"
        / "single_defect_n7_extremal_carrier_input_v1.json"
    )
    if local.exists():
        return local
    raise SystemExit(
        "Paper XXVII lower-section input not found; pass --n7-extremal-input "
        "or set RIME_PAPER27_RELEASE_ROOT"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n7-extremal-input", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    lower_section_input = _resolve_lower_section(args.n7_extremal_input)
    payload = build_payload(lower_section_input)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(output=args.out, payload=payload),
    )
    print(
        json.dumps(
            {
                "artifact": args.out.as_posix(),
                "construction_payload_sha256": payload[
                    "construction_payload_sha256"
                ],
                "exact_lifts": payload["construction"]["exact_lifts"][
                    "receipt_count"
                ],
                "menu_channels": payload["construction"]["menus"][
                    "channel_count"
                ],
                "receipt": receipt_path.as_posix(),
                "source_contexts": payload["construction"]["source_section"][
                    "context_count"
                ],
                "status": "PRE_EVALUATION_OBJECTS_FROZEN",
                "target_contexts": payload["lower_section_target"][
                    "context_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
