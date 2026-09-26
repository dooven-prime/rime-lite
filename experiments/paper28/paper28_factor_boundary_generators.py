#!/usr/bin/env python3
"""Factor the Paper XXVIII seed relation through typed boundary generators.

The input is the canonical ``4+35`` exact-receipt catalog.  This script does
not enumerate new contexts or exits.  It replays each stored word and factors
it into three exact operation types:

``TRANSPORT``
    one nonempty maximal rotation block ``p^a``;
``RETURN``
    one rank-preserving defect letter ``d``;
``FUSION``
    one strict defect letter ``d`` that performs a binary packet fusion.

An abstract generator row is not a bare operation name.  It is a relation row

    source boundary --(generator, accounting decoration)--> target boundary

with a nonempty exact realization fiber.  The audit verifies soundness of
every displayed row and exact factorization of every stored receipt.  Named
mechanisms such as repayment, heavy comb, and fallback are then reported as
path/accounting predicates; they are not silently promoted to primitive
interaction generators.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from mass_maturity_legacy import simplified_deadline
from paper28_mechanism_schema import validate_receipt
from section_return_core import (
    PacketState,
    deserialize_packet_state,
    packet_mass,
    push_packets,
    serialize_packet_state,
)

AUDIT_SCHEMA = "paper28-boundary-generator-factorization-v1"
RECEIPT_SCHEMA = "paper28-boundary-generator-factorization-receipt-v1"
CATALOG_SCHEMA = "paper28-seed-mechanism-catalog-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "results" / "paper28_seed_mechanism_catalog_v1.json.gz"
DEFAULT_OUTPUT = HERE / "results" / "paper28_boundary_generator_factorization_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_boundary_generator_factorization.py",
)

PRIMITIVE_KINDS = ("FUSION", "RETURN", "TRANSPORT")


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
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def _read_catalog(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()).decode("ascii"))


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _cycle(n: int) -> tuple[int, ...]:
    return tuple((coordinate + 1) % n for coordinate in range(n))


def _rank(state: PacketState) -> int:
    return len(state)


def _partition(state: PacketState) -> list[int]:
    return sorted((len(packet) for packet in state.values()), reverse=True)


def _tau(state: PacketState, n: int) -> int:
    return simplified_deadline(packet_mass(state, n), n)


def _budget(state: PacketState, n: int) -> int:
    reset = (n,) + (0,) * (n - 1)
    return simplified_deadline(reset, n) - _tau(state, n)


def _packet_key(packet: frozenset[int]) -> tuple[int, ...]:
    return tuple(sorted(int(atom) for atom in packet))


def _exact_state(
    *,
    n: int,
    defect: Sequence[int],
    packets: PacketState,
    distinguished: frozenset[int],
) -> dict[str, Any]:
    if distinguished not in packets.values():
        raise AssertionError("distinguished packet is not present in exact state")
    body = {
        "ambient_n": int(n),
        "defect": [int(value) for value in defect],
        "packets": serialize_packet_state(packets),
        "distinguished_packet": sorted(int(atom) for atom in distinguished),
    }
    return {"state_id": f"gx-{_digest(body)[:24]}", **body}


def _boundary(
    *, n: int, defect: Sequence[int], packets: PacketState
) -> dict[str, Any]:
    """Return the future-free ``(action, normalized mass placement)`` base."""

    return {
        "action": {
            "ambient_n": int(n),
            "rank": _rank(packets),
            "defect": [int(value) for value in defect],
        },
        "mass_rows": [
            {"coordinate": int(coordinate), "mass": len(packet)}
            for coordinate, packet in sorted(packets.items())
        ],
    }


def _accounting(
    source: PacketState,
    target: PacketState,
    *,
    n: int,
    length: int,
    incoming_debt: int,
    cumulative_surplus_before: int,
) -> dict[str, Any]:
    source_tau = _tau(source, n)
    target_tau = _tau(target, n)
    maturity_gain = target_tau - source_tau
    surplus = maturity_gain - int(length)
    cumulative_surplus_after = cumulative_surplus_before + surplus
    outgoing_debt = max(0, -cumulative_surplus_after)
    return {
        "length": int(length),
        "maturity_gain": maturity_gain,
        "surplus": surplus,
        "incoming_debt": int(incoming_debt),
        "outgoing_debt": outgoing_debt,
        "source_budget": _budget(source, n),
        "target_budget": _budget(target, n),
    }


def _parent_role(
    packet: frozenset[int], current_distinguished: frozenset[int]
) -> str:
    if packet == current_distinguished:
        return "CURRENT_F"
    if current_distinguished < packet:
        return "CARRIES_CURRENT_F"
    return f"OTHER_M{len(packet)}"


def _fusion_data(
    source: PacketState,
    target: PacketState,
    defect: Sequence[int],
    current_distinguished: frozenset[int],
) -> tuple[dict[str, Any], frozenset[int]]:
    grouped: dict[int, list[tuple[int, frozenset[int]]]] = defaultdict(list)
    for coordinate, packet in source.items():
        grouped[int(defect[coordinate])].append((int(coordinate), packet))
    collisions = [
        (coordinate, rows) for coordinate, rows in grouped.items() if len(rows) > 1
    ]
    if len(collisions) != 1 or len(collisions[0][1]) != 2:
        raise AssertionError("strict generator is not one binary fusion")
    target_coordinate, parent_rows = collisions[0]
    parent_rows.sort(key=lambda row: (len(row[1]), _packet_key(row[1])))
    fresh = frozenset().union(*(packet for _, packet in parent_rows))
    if target.get(target_coordinate) != fresh:
        raise AssertionError("strict generator fresh packet mismatch")
    profiles = [
        {
            "mass": len(packet),
            "role": _parent_role(packet, current_distinguished),
        }
        for _, packet in parent_rows
    ]
    generator = {
        "kind": "FUSION",
        "parents": profiles,
        "result_mass": len(fresh),
    }
    return generator, fresh


def _operation_row(
    *,
    receipt_id: str,
    corridor_index: int,
    operation_index: int,
    segment: Sequence[int],
    generator: Mapping[str, Any],
    accounting: Mapping[str, Any],
    n: int,
    defect: Sequence[int],
    source: PacketState,
    target: PacketState,
    source_distinguished: frozenset[int],
    target_distinguished: frozenset[int],
) -> dict[str, Any]:
    exact_source = _exact_state(
        n=n,
        defect=defect,
        packets=source,
        distinguished=source_distinguished,
    )
    exact_target = _exact_state(
        n=n,
        defect=defect,
        packets=target,
        distinguished=target_distinguished,
    )
    body = {
        "receipt_id": receipt_id,
        "corridor_index": int(corridor_index),
        "operation_index": int(operation_index),
        "word_segment": [int(value) for value in segment],
        "generator": dict(generator),
        "accounting": dict(accounting),
        "source_boundary": _boundary(n=n, defect=defect, packets=source),
        "target_boundary": _boundary(n=n, defect=defect, packets=target),
        "exact_source": exact_source,
        "exact_target": exact_target,
    }
    return {"occurrence_id": f"go-{_digest(body)[:24]}", **body}


def _factor_receipt(record: Mapping[str, Any]) -> dict[str, Any]:
    validate_receipt(record)
    receipt_id = str(record["receipt_id"])
    skeleton = record["skeleton"]
    exact = record["exact"]
    accounting = record["accounting"]
    n = int(skeleton["ambient_n"])
    defect = tuple(int(value) for value in exact["target_context"]["defect"])
    cycle = _cycle(n)
    words = exact["words"]
    boundaries = exact["corridor_boundaries"]
    state = deserialize_packet_state(boundaries[0]["source"])
    distinguished = frozenset(
        int(atom) for atom in exact["ancestry_update"]["incoming_distinguished_packet"]
    )
    source_state = state
    source_distinguished = distinguished
    cumulative_surplus = 0
    operations: list[dict[str, Any]] = []
    corridor_fusion_occurrences: list[dict[str, Any]] = []

    for corridor_index, (word, boundary, stored_corridor) in enumerate(
        zip(words, boundaries, accounting["corridors"], strict=True)
    ):
        expected_source = deserialize_packet_state(boundary["source"])
        expected_target = deserialize_packet_state(boundary["target"])
        if state != expected_source:
            raise AssertionError("corridor source packet state drift")
        corridor_operation_start = len(operations)
        corridor_start_length = sum(
            int(row["accounting"]["length"]) for row in operations
        )
        corridor_start_surplus = cumulative_surplus
        fusion_count = 0
        rotation_run = 0

        for letter_position, letter in enumerate(word):
            letter = int(letter)
            if letter == 0:
                rotation_run += 1
                continue
            if letter != 1:
                raise AssertionError(f"unexpected letter index: {letter}")

            if rotation_run:
                before = state
                after = before
                for _ in range(rotation_run):
                    after = push_packets(after, cycle)
                operation_accounting = _accounting(
                    before,
                    after,
                    n=n,
                    length=rotation_run,
                    incoming_debt=max(0, -cumulative_surplus),
                    cumulative_surplus_before=cumulative_surplus,
                )
                operation = _operation_row(
                    receipt_id=receipt_id,
                    corridor_index=corridor_index,
                    operation_index=len(operations),
                    segment=[0] * rotation_run,
                    generator={"kind": "TRANSPORT"},
                    accounting=operation_accounting,
                    n=n,
                    defect=defect,
                    source=before,
                    target=after,
                    source_distinguished=distinguished,
                    target_distinguished=distinguished,
                )
                operations.append(operation)
                cumulative_surplus += int(operation_accounting["surplus"])
                state = after
                rotation_run = 0

            before = state
            after = push_packets(before, defect)
            rank_drop = _rank(before) - _rank(after)
            previous_distinguished = distinguished
            if rank_drop == 0:
                generator = {"kind": "RETURN"}
            elif rank_drop == 1:
                generator, distinguished = _fusion_data(
                    before, after, defect, distinguished
                )
                fusion_count += 1
            else:
                raise AssertionError("defect generator changes rank by more than one")
            operation_accounting = _accounting(
                before,
                after,
                n=n,
                length=1,
                incoming_debt=max(0, -cumulative_surplus),
                cumulative_surplus_before=cumulative_surplus,
            )
            operation = _operation_row(
                receipt_id=receipt_id,
                corridor_index=corridor_index,
                operation_index=len(operations),
                segment=[1],
                generator=generator,
                accounting=operation_accounting,
                n=n,
                defect=defect,
                source=before,
                target=after,
                source_distinguished=previous_distinguished,
                target_distinguished=distinguished,
            )
            operations.append(operation)
            if rank_drop == 1:
                corridor_fusion_occurrences.append(operation)
                if letter_position != len(word) - 1:
                    raise AssertionError("strict fusion is not corridor-terminal")
            cumulative_surplus += int(operation_accounting["surplus"])
            state = after

        if rotation_run:
            raise AssertionError("corridor ends in a nonterminal rotation block")
        if fusion_count != 1:
            raise AssertionError("corridor does not factor through one terminal fusion")
        if state != expected_target:
            raise AssertionError("factored corridor misses stored packet target")
        corridor_length = sum(
            int(row["accounting"]["length"]) for row in operations
        ) - corridor_start_length
        corridor_surplus = cumulative_surplus - corridor_start_surplus
        if corridor_length != int(stored_corridor["length"]):
            raise AssertionError("factored corridor length mismatch")
        if corridor_surplus != int(stored_corridor["surplus"]):
            raise AssertionError("factored corridor surplus mismatch")
        replayed_word = [
            letter
            for operation in operations[corridor_operation_start:]
            for letter in operation["word_segment"]
        ]
        if replayed_word != [int(letter) for letter in word]:
            raise AssertionError("generator segments do not reconstruct corridor word")

    expected_final = deserialize_packet_state(boundaries[-1]["target"])
    expected_distinguished = frozenset(
        int(atom)
        for atom in exact["ancestry_update"]["outgoing_distinguished_packet"]
    )
    if state != expected_final or distinguished != expected_distinguished:
        raise AssertionError("receipt factorization misses exact target context")
    total_length = sum(int(row["accounting"]["length"]) for row in operations)
    total_surplus = sum(int(row["accounting"]["surplus"]) for row in operations)
    stored_length = sum(int(row["length"]) for row in accounting["corridors"])
    stored_surplus = sum(int(row["surplus"]) for row in accounting["corridors"])
    if (total_length, total_surplus) != (stored_length, stored_surplus):
        raise AssertionError("receipt accounting is not recovered by generators")
    if _budget(source_state, n) != total_length + total_surplus + _budget(state, n):
        raise AssertionError("factored receipt violates credit allocation")
    for left, right in zip(operations, operations[1:], strict=False):
        if left["exact_target"]["state_id"] != right["exact_source"]["state_id"]:
            raise AssertionError("adjacent generators do not share an exact boundary")

    fusion_packets = [
        frozenset(row["exact_target"]["distinguished_packet"])
        for row in corridor_fusion_occurrences
    ]
    heavy_chain = all(
        frozenset(left) < frozenset(right)
        for left, right in zip(fusion_packets, fusion_packets[1:], strict=False)
    )
    corridor_surpluses = [int(row["surplus"]) for row in accounting["corridors"]]
    repayment = (
        len(corridor_surpluses) == 2
        and corridor_surpluses[0] < 0
        and sum(corridor_surpluses) >= 0
    )
    source_partition = list(skeleton["source_partition"])
    target_partition = list(skeleton["target_partition"])
    fallback_52 = source_partition == [2, 2, 2, 1] and target_partition == [5, 2]
    heavy_61 = source_partition == [2, 2, 2, 1] and target_partition == [6, 1]
    historical_features = {
        "one_corridor_completion": len(corridor_surpluses) == 1,
        "two_corridor_repayment": repayment,
        "repeated_fusion_heavy_chain": len(fusion_packets) > 1 and heavy_chain,
        "rank_two_52_fallback": fallback_52,
        "rank_two_61_heavy_target": heavy_61,
        "zero_surplus_rank_two_52_fallback": fallback_52
        and sum(corridor_surpluses) == 0,
        "zero_surplus_rank_two_61_heavy_target": heavy_61
        and sum(corridor_surpluses) == 0,
    }
    return {
        "receipt_id": receipt_id,
        "seed_surface": str(record["seed_surface"]),
        "relation_role": str(record["relation_role"]),
        "source_state_id": _exact_state(
            n=n,
            defect=defect,
            packets=source_state,
            distinguished=source_distinguished,
        )["state_id"],
        "target_state_id": _exact_state(
            n=n,
            defect=defect,
            packets=state,
            distinguished=distinguished,
        )["state_id"],
        "operation_occurrences": operations,
        "operation_kind_path": [row["generator"]["kind"] for row in operations],
        "total_length": total_length,
        "total_surplus": total_surplus,
        "historical_features": historical_features,
    }


def _relation_key(operation: Mapping[str, Any]) -> str:
    return _digest(
        {
            "source_boundary": operation["source_boundary"],
            "generator": operation["generator"],
            "accounting": operation["accounting"],
            "target_boundary": operation["target_boundary"],
        }
    )


def _path_signature(kinds: Sequence[str]) -> str:
    return "-".join(str(kind) for kind in kinds)


def build_audit(catalog_path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    catalog = _read_catalog(catalog_path)
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ValueError(f"unexpected catalog schema: {catalog.get('schema')!r}")
    records = list(catalog["receipts"])

    factorizations: list[dict[str, Any]] = []
    relation_fibers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    operation_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    feature_counts: Counter[str] = Counter()
    exact_states: set[str] = set()
    occurrence_ids: set[str] = set()

    for record in records:
        factorization = _factor_receipt(record)
        factorizations.append(factorization)
        exact_states.add(str(factorization["source_state_id"]))
        exact_states.add(str(factorization["target_state_id"]))
        path_counts[_path_signature(factorization["operation_kind_path"])] += 1
        for name, holds in factorization["historical_features"].items():
            if holds:
                feature_counts[name] += 1
        for operation in factorization["operation_occurrences"]:
            occurrence_id = str(operation["occurrence_id"])
            if occurrence_id in occurrence_ids:
                raise AssertionError(f"duplicate operation occurrence: {occurrence_id}")
            occurrence_ids.add(occurrence_id)
            kind = str(operation["generator"]["kind"])
            operation_counts[kind] += 1
            exact_states.add(str(operation["exact_source"]["state_id"]))
            exact_states.add(str(operation["exact_target"]["state_id"]))
            relation_fibers[_relation_key(operation)].append(operation)

    if set(operation_counts) != set(PRIMITIVE_KINDS):
        raise AssertionError("primitive generator cover changed")

    relation_rows: list[dict[str, Any]] = []
    relation_rows_by_kind: Counter[str] = Counter()
    max_fiber_by_kind: Counter[str] = Counter()
    for relation_id, operations in sorted(relation_fibers.items()):
        representative = operations[0]
        for operation in operations[1:]:
            if _relation_key(operation) != relation_id:
                raise AssertionError("relation fiber is not constant")
        kind = str(representative["generator"]["kind"])
        relation_rows_by_kind[kind] += 1
        max_fiber_by_kind[kind] = max(max_fiber_by_kind[kind], len(operations))
        occurrence_id_list = sorted(str(row["occurrence_id"]) for row in operations)
        relation_rows.append(
            {
                "relation_id": f"gr-{relation_id[:24]}",
                "source_boundary": representative["source_boundary"],
                "generator": representative["generator"],
                "accounting": representative["accounting"],
                "target_boundary": representative["target_boundary"],
                "exact_realization_count": len(operations),
                "exact_realization_ids_sha256": _digest(occurrence_id_list),
                "sample_occurrence_ids": occurrence_id_list[:3],
            }
        )

    boundary_relation_menus: dict[str, set[str]] = defaultdict(set)
    boundary_kind_menus: dict[str, set[str]] = defaultdict(set)
    for row in relation_rows:
        source_boundary_id = _digest(row["source_boundary"])
        boundary_relation_menus[source_boundary_id].add(str(row["relation_id"]))
        boundary_kind_menus[source_boundary_id].add(str(row["generator"]["kind"]))
    menu_size_histogram = Counter(
        len(menu) for menu in boundary_relation_menus.values()
    )

    receipt_summaries = [
        {
            "receipt_id": row["receipt_id"],
            "source_state_id": row["source_state_id"],
            "target_state_id": row["target_state_id"],
            "operation_count": len(row["operation_occurrences"]),
            "operation_kind_path": row["operation_kind_path"],
            "operation_occurrence_ids_sha256": _digest(
                [item["occurrence_id"] for item in row["operation_occurrences"]]
            ),
            "total_length": row["total_length"],
            "total_surplus": row["total_surplus"],
            "historical_features": row["historical_features"],
        }
        for row in factorizations
    ]

    result: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "input": {
            "artifact": catalog_path.name,
            "sha256": _sha256(catalog_path),
            "content_sha256": catalog["content_sha256"],
        },
        "scope": {
            "seed_context_count": int(catalog["counts"]["seed_contexts"]),
            "exact_receipt_count": len(records),
            "no_new_context_or_exit_enumeration": True,
        },
        "boundary_definition": {
            "base": "action_plus_normalized_mass_placement",
            "action_fields": ["ambient_n", "rank", "defect"],
            "local_boundary_certification": (
                "every local boundary is an endpoint of an exactly replayed "
                "typed operation with carried debt state"
            ),
            "section_boundary_relation": (
                "stored receipt source and target contexts form a distinguished "
                "subset of the replay-certified local boundary space"
            ),
            "exact_fiber_retains": [
                "packet_identity",
                "distinguished_packet",
                "receipt_id",
                "corridor_index",
                "operation_index",
                "word_segment",
            ],
        },
        "generator_definition": {
            "primitive_kinds": list(PRIMITIVE_KINDS),
            "relation_shape": "boundary x generator x accounting x boundary",
            "composition_requires_matching_exact_typed_boundary": True,
            "bare_generator_composition_claimed": False,
        },
        "factorization": {
            "receipt_count": len(factorizations),
            "covered_receipt_count": len(factorizations),
            "residual_receipt_count": 0,
            "exact_operation_occurrence_count": len(occurrence_ids),
            "exact_state_count": len(exact_states),
            "operation_occurrence_counts": dict(sorted(operation_counts.items())),
            "operation_path_signature_count": len(path_counts),
            "operation_path_signature_counts_sha256": _digest(
                dict(sorted(path_counts.items()))
            ),
            "largest_operation_path_signature_multiplicity": max(
                path_counts.values()
            ),
            "all_exact_endpoints_replayed": True,
            "all_lengths_recovered": True,
            "all_surpluses_recovered": True,
            "all_words_reconstructed": True,
            "all_adjacent_operations_share_exact_boundary": True,
            "every_corridor_has_one_terminal_fusion": True,
        },
        "generator_relations": {
            "relation_row_count": len(relation_rows),
            "relation_row_counts_by_kind": dict(sorted(relation_rows_by_kind.items())),
            "max_exact_realization_fiber_by_kind": dict(
                sorted(max_fiber_by_kind.items())
            ),
            "every_relation_row_has_exact_lift": all(
                row["exact_realization_count"] > 0 for row in relation_rows
            ),
            "source_boundary_count": len(boundary_relation_menus),
            "max_relation_menu_size": max(
                len(menu) for menu in boundary_relation_menus.values()
            ),
            "max_generator_kind_menu_size": max(
                len(menu) for menu in boundary_kind_menus.values()
            ),
            "relation_menu_size_histogram": {
                str(size): count for size, count in sorted(menu_size_histogram.items())
            },
            "rows": relation_rows,
        },
        "historical_name_reduction": {
            "receipt_feature_counts": dict(sorted(feature_counts.items())),
            "interaction_primitives": list(PRIMITIVE_KINDS),
            "path_or_accounting_predicates": [
                "one_corridor_completion",
                "two_corridor_repayment",
                "repeated_fusion_heavy_chain",
                "rank_two_52_fallback",
                "rank_two_61_heavy_target",
                "zero_surplus_rank_two_52_fallback",
                "zero_surplus_rank_two_61_heavy_target",
            ],
            "realization_refinements_not_promoted_to_primitives": [
                "B2_STEERING",
                "BRIDGE",
                "ORBIT_CLOSURE",
            ],
            "claim_boundary": (
                "The seed relation factors through three typed operation kinds. "
                "No all-rank generator completeness or unique factorization is claimed."
            ),
        },
        "receipt_factorizations": sorted(
            receipt_summaries, key=lambda row: str(row["receipt_id"])
        ),
    }
    result["content_sha256"] = _digest(result)
    return result


def build_receipt(
    *, output: Path, payload: Mapping[str, Any], catalog_path: Path
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
        "verification_mode": "FULL_RECOMPUTATION_FROM_CANONICAL_SEED_CATALOG",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "input": {
            "name": catalog_path.name,
            "sha256": _sha256(catalog_path),
            "content_sha256": payload["input"]["content_sha256"],
        },
        "source_closure": closure,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical_bytes(payload)
    if path.name.endswith(".json.gz"):
        path.write_bytes(gzip.compress(encoded, mtime=0))
    else:
        path.write_bytes(encoded)


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_audit(args.catalog)
    _write_json(args.output, payload)
    receipt_path = args.receipt or default_receipt_path(args.output)
    _write_receipt(
        receipt_path,
        build_receipt(output=args.output, payload=payload, catalog_path=args.catalog),
    )
    print(
        json.dumps(
            {
                "output": args.output.as_posix(),
                "receipt": receipt_path.as_posix(),
                "content_sha256": payload["content_sha256"],
                "factorization": {
                    "receipt_count": payload["factorization"]["receipt_count"],
                    "exact_operation_occurrence_count": payload["factorization"][
                        "exact_operation_occurrence_count"
                    ],
                    "operation_occurrence_counts": payload["factorization"][
                        "operation_occurrence_counts"
                    ],
                    "residual_receipt_count": payload["factorization"][
                        "residual_receipt_count"
                    ],
                },
                "relation_row_count": payload["generator_relations"][
                    "relation_row_count"
                ],
                "historical_features": payload["historical_name_reduction"][
                    "receipt_feature_counts"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
