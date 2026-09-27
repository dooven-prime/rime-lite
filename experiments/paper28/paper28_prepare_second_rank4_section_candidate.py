#!/usr/bin/env python3
"""Freeze P28.5e rank-four menus/lifts before any low-rank evaluation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from mass_maturity_legacy import mass_rank
from paper28_factor_boundary_generators import _factor_receipt
from paper28_mechanism_schema import SCHEMA as MECHANISM_SCHEMA
from paper28_mechanism_schema import exact_receipt_sha256, validate_receipt
from paper28_project_seed_mechanisms import (
    Context,
    _corridor_boundary,
    _cycle,
    _debt_profile,
    _fusion_exact,
    _fusion_skeleton,
    _participation_type,
    _target_budget,
)
from paper28_select_second_rank5_return_candidate import (
    SCHEMA as SELECTION_SCHEMA,
)
from section_return_core import (
    CompleteExitOracle,
    activated_edge_summary,
    deserialize_packet_state,
    mass_partition,
    trace_packets,
)


SCHEMA = "paper28-second-rank4-section-candidate-v1"
RECEIPT_SCHEMA = "paper28-second-rank4-section-candidate-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_second_rank5_return_candidate_selection_v1.json.gz"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_second_rank4_section_candidate_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_prepare_second_rank4_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_second_rank4_section_candidate.py",
)
N = 7
FORBIDDEN_CONSTRUCTION_FIELDS = (
    "target_in_exact_p_le3",
    "good_4",
    "good_5",
    "successful_channel",
    "successful_exact_lift",
    "certified_target",
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


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name.removesuffix('.json.gz')}.receipt.json")


def _write_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _context_from_selection(row: Mapping[str, Any]) -> Context:
    rank4 = row["rank4_context"]
    packets = deserialize_packet_state(rank4["packets"])
    distinguished = frozenset(
        int(value) for value in rank4["activation"]["fresh_packet"]
    )
    defect = tuple(int(value) for value in str(row["defect"]))
    context = Context(
        n=N,
        defect=defect,
        packets=packets,
        distinguished=distinguished,
        origin=f"n7-second-rank4-candidate-{row['index']}-{row['defect']}",
        seed_surface="N7_SECOND_RANK4_CANDIDATE_48",
        is_seed=True,
    )
    if tuple(context.mass) != tuple(int(value) for value in rank4["mass"]):
        raise AssertionError("selection packet state does not reproduce rank-four mass")
    if tuple(mass_partition(context.mass)) != (3, 2, 1, 1):
        raise AssertionError("second rank-four candidate partition drift")
    return context


def _record_from_edge(
    context: Context, edge: Mapping[str, Any]
) -> tuple[dict[str, Any], Context]:
    """Build an exact receipt without instantiating a low-rank evaluator."""

    letters = (_cycle(context.n), context.defect)
    activated, target_packets = activated_edge_summary(
        dict(edge), context.packets, letters, context.n, include_target_packets=True
    )
    fusions = [activated["first_fusion"]]
    if activated["second_fusion"] is not None:
        fusions.append(activated["second_fusion"])

    words = [[int(value) for value in edge["first_word"]]]
    corridor_states = [context.packets]
    if edge["type"] == "II":
        words.append([int(value) for value in edge["second_word"]])
        corridor_states.append(
            trace_packets(context.packets, edge["first_word"], letters)
        )
    boundaries = [
        _corridor_boundary(state, word, letters)
        for state, word in zip(corridor_states, words, strict=True)
    ]

    new_distinguished = frozenset(
        int(value) for value in fusions[-1]["fresh_packet"]
    )
    target_context = Context(
        n=context.n,
        defect=context.defect,
        packets=target_packets,
        distinguished=new_distinguished,
        origin=context.origin,
        seed_surface=context.seed_surface,
        is_seed=False,
    )
    target_payload = target_context.payload

    corridor_rows = []
    for index, fusion in enumerate(fusions):
        parent_sizes = [int(value) for value in fusion["parent_sizes"]]
        corridor_rows.append(
            {
                "rank_drop": 1,
                "delta_m": parent_sizes[0] * parent_sizes[1],
                "length": int(
                    edge["length_first" if index == 0 else "length_second"]
                ),
                "surplus": int(
                    edge["surplus_first" if index == 0 else "surplus_second"]
                ),
            }
        )
    surpluses = [int(row["surplus"]) for row in corridor_rows]
    source_partition = list(mass_partition(context.mass))
    target_mass = tuple(int(value) for value in edge["target"])
    target_partition = list(mass_partition(target_mass))
    exact_fusions = [_fusion_exact(fusion) for fusion in fusions]
    participation = _participation_type(context.distinguished, fusions)
    source_packets = [
        sorted(packet) for _, packet in sorted(context.packets.items())
    ]
    ancestry_update = {
        "incoming_distinguished_packet": sorted(context.distinguished),
        "participation_type": participation,
        "outgoing_distinguished_packet": sorted(new_distinguished),
        "update_rule": "FINAL_STRICT_FUSION_PACKET",
    }
    exact_target_channel = {
        "target_context_id": target_payload["context_id"],
        "target_packets": target_payload["packets"],
        "outgoing_distinguished_packet": sorted(new_distinguished),
    }
    record: dict[str, Any] = {
        "schema": MECHANISM_SCHEMA,
        "receipt_id": "pending",
        "seed_surface": context.seed_surface,
        "relation_role": "RANK4_SECOND_SECTION_CANDIDATE",
        "origin": context.origin,
        "skeleton": {
            "ambient_n": context.n,
            "source_rank": mass_rank(context.mass),
            "target_rank": mass_rank(target_mass),
            "source_partition": source_partition,
            "target_partition": target_partition,
            "corridor_count": len(corridor_rows),
            "rank_drop_vector": [1] * len(corridor_rows),
            "fusion_chain": _fusion_skeleton(fusions, context.distinguished),
            "ancestry_update_type": participation,
            "return_type": (
                "ONE_CORRIDOR"
                if edge["type"] == "I"
                else "TWO_CORRIDOR_REPAYMENT"
            ),
        },
        "accounting": {
            "corridors": corridor_rows,
            "debt_profile": _debt_profile(surpluses),
            "residual_tail_budget": _target_budget(target_mass, context.n),
        },
        "exact": {
            "source_context_id": context.context_id,
            "source_packet_ids": source_packets,
            "words": words,
            "corridor_boundaries": boundaries,
            "fusion_packet_identities": exact_fusions,
            "target_channel": exact_target_channel,
            "target_endpoint": list(target_mass),
            "target_context": target_payload,
            "ancestry_update": ancestry_update,
        },
        "observables": {
            "source_target_shape": {
                "source_rank": mass_rank(context.mass),
                "target_rank": mass_rank(target_mass),
                "source_partition": source_partition,
                "target_partition": target_partition,
            },
            "fusion_mass_pattern": [
                sorted(int(value) for value in fusion["parent_sizes"])
                for fusion in fusions
            ],
            "rank_drop_vector": [1] * len(corridor_rows),
            "corridor_count": len(corridor_rows),
            "corridor_lengths": [int(row["length"]) for row in corridor_rows],
            "corridor_surpluses": surpluses,
            "debt_profile": _debt_profile(surpluses),
            "total_surplus": sum(surpluses),
            "residual_tail_budget": _target_budget(target_mass, context.n),
            "exact_ancestry_update": ancestry_update,
            "source_packet_identity": source_packets,
            "fusion_packet_identity": exact_fusions,
            "exact_target_transport_channel": exact_target_channel,
        },
    }
    record["receipt_id"] = f"r4c2-{exact_receipt_sha256(record)[:24]}"
    validate_receipt(record)
    return record, target_context


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
        "historical_features": factorization["historical_features"],
    }


def _build_menus(
    contexts: Sequence[Context], records: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    by_source: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        by_source[str(record["exact"]["source_context_id"])].append(record)
    expected_sources = {context.context_id for context in contexts}
    if set(by_source) != expected_sources:
        raise AssertionError("exact relation and source carrier domains disagree")

    rows = []
    menu_histogram: Counter[int] = Counter()
    accounting_count = 0
    for context in sorted(contexts, key=lambda item: item.context_id):
        source_records = by_source[context.context_id]
        channels: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in source_records:
            channels[_digest(record["skeleton"])].append(record)
        channel_rows = []
        for key, channel_records in sorted(channels.items()):
            representative = channel_records[0]
            accounting: dict[str, list[str]] = defaultdict(list)
            operation_paths = set()
            for record in channel_records:
                accounting[_digest(record["accounting"])].append(
                    str(record["receipt_id"])
                )
                operation_paths.add(
                    tuple(_factor_receipt(record)["operation_kind_path"])
                )
            accounting_rows = [
                {
                    "accounting_id": f"r4c2a-{digest[:24]}",
                    "accounting": next(
                        record["accounting"]
                        for record in channel_records
                        if _digest(record["accounting"]) == digest
                    ),
                    "exact_lift_ids": sorted(receipt_ids),
                }
                for digest, receipt_ids in sorted(accounting.items())
            ]
            accounting_count += len(accounting_rows)
            channel_rows.append(
                {
                    "channel_id": f"r4c2m-{key[:24]}",
                    "interaction_skeleton": representative["skeleton"],
                    "accounting_refinements": accounting_rows,
                    "operation_kind_paths": [
                        list(path) for path in sorted(operation_paths)
                    ],
                    "exact_lift_ids": sorted(
                        str(record["receipt_id"]) for record in channel_records
                    ),
                }
            )
        menu_histogram[len(channel_rows)] += 1
        rows.append(
            {
                "source_context": context.payload,
                "menu_size": len(channel_rows),
                "channels": channel_rows,
            }
        )
    return {
        "constructor": (
            "complete tied endpoint-shortest Type-I/II macro relation, quotiented "
            "only by the future-free interaction skeleton"
        ),
        "forbidden_inputs": list(FORBIDDEN_CONSTRUCTION_FIELDS),
        "context_count": len(rows),
        "channel_count": sum(row["menu_size"] for row in rows),
        "accounting_refinement_count": accounting_count,
        "exact_lift_count": len(records),
        "max_menu_size": max(row["menu_size"] for row in rows),
        "menu_size_histogram": {
            str(size): count for size, count in sorted(menu_histogram.items())
        },
        "contexts": rows,
    }


def _construction_core(construction: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_context_ids": construction["source_carrier"]["context_ids"],
        "menu_contexts": construction["menus"]["contexts"],
        "exact_receipts": construction["exact_lifts"]["receipts"],
        "factorizations": construction["exact_lifts"]["factorizations"],
    }


def build_payload(selection_path: Path) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected second-candidate selection schema")
    if selection["scope"]["evaluation_status"] != "NOT_RUN":
        raise AssertionError("selection input already contains success evaluation")
    if selection["scope"]["section_authority_status"] != "NOT_GRANTED":
        raise AssertionError("selection input already claims section authority")

    selected_rows = selection["candidate"]["contexts"]
    contexts = [_context_from_selection(row) for row in selected_rows]
    if len(contexts) != 48 or len({context.context_id for context in contexts}) != 48:
        raise AssertionError("second rank-four carrier is not 48 distinct contexts")

    records = []
    factorizations = []
    for context in contexts:
        oracle = CompleteExitOracle((_cycle(N), context.defect), N)
        edges = list(oracle.macro_edges(context.mass))
        if not edges:
            raise AssertionError("rank-four candidate has no macro exits")
        for edge in edges:
            record, _ = _record_from_edge(context, edge)
            records.append(record)
            factorizations.append(_factorization_summary(record))
    records.sort(key=lambda row: str(row["receipt_id"]))
    factorizations.sort(key=lambda row: str(row["receipt_id"]))
    if len({row["receipt_id"] for row in records}) != len(records):
        raise AssertionError("exact receipt ids are not unique")

    menus = _build_menus(contexts, records)
    factor_state_ids = {
        str(operation[side]["state_id"])
        for row in factorizations
        for operation in row["operation_occurrences"]
        for side in ("exact_source", "exact_target")
    }
    endpoint_state_ids = {
        str(row["source_state_id"]) for row in factorizations
    } | {str(row["target_state_id"]) for row in factorizations}
    operation_kinds = sorted(
        {
            str(kind)
            for row in factorizations
            for kind in row["operation_kind_path"]
        }
    )
    if not set(operation_kinds).issubset({"TRANSPORT", "RETURN", "FUSION"}):
        raise AssertionError("second carrier requires an undeclared generator kind")

    construction = {
        "source_carrier": {
            "name": "C_4,cand2^(7)",
            "recursive_authority": "NONE_PRE_EVALUATION",
            "selection_artifact": selection_path.name,
            "selection_artifact_sha256": _sha256(selection_path),
            "selection_content_sha256": selection["content_sha256"],
            "selection_candidate_payload_sha256": selection[
                "candidate_payload_sha256"
            ],
            "context_count": len(contexts),
            "context_ids": sorted(context.context_id for context in contexts),
        },
        "menus": menus,
        "exact_lifts": {
            "definition": (
                "complete source-addressed rank-four macro receipts factored "
                "through exact TRANSPORT/RETURN/FUSION operation paths"
            ),
            "receipt_count": len(records),
            "receipts": records,
            "factorizations": factorizations,
            "operation_kinds": operation_kinds,
        },
        "checkpoint_type_audit": {
            "menu_source_context_count": len(contexts),
            "exported_recursive_target_count": 0,
            "replay_state_count": len(factor_state_ids),
            "receipt_endpoint_state_count": len(endpoint_state_ids),
            "internal_only_state_count": len(factor_state_ids - endpoint_state_ids),
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
        if field in encoded:
            raise AssertionError(f"future-success field leaked into construction: {field}")

    payload = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "source_rank": 4,
            "source": "48-context P28.5d pre-section carrier",
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_GRANTED",
            "nonclaim": (
                "this artifact freezes menus and exact lifts but does not evaluate "
                "Good_4 or certify return to P_<=3"
            ),
        },
        "phase_order": [
            "read_frozen_candidate_selection",
            "reconstruct_typed_rank4_sources",
            "enumerate_complete_future_free_macro_relation",
            "factor_exact_lifts_and_construct_menus",
            "freeze_construction_payload_and_digest",
            "low_rank_evaluator_absent",
        ],
        "input": {
            "name": selection_path.name,
            "schema": selection["schema"],
            "sha256": _sha256(selection_path),
            "content_sha256": selection["content_sha256"],
        },
        "construction": construction,
        "evaluator": {
            "status": "ABSENT_BY_DESIGN",
            "good_predicate_defined_for_later_phase": (
                "Good_4(C,m) iff an exact lift in Lift_4(C,m) has target in "
                "the exact P_<=3^(7) base"
            ),
            "evaluated_source_count": 0,
            "evaluated_channel_count": 0,
        },
    }
    payload["construction_payload_sha256"] = _digest(construction)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, selection_path: Path, output: Path, payload: Mapping[str, Any]
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
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_SELECTION_INPUT",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "construction_payload_sha256": payload["construction_payload_sha256"],
        },
        "input": {
            "name": selection_path.name,
            "schema": payload["input"]["schema"],
            "sha256": payload["input"]["sha256"],
            "content_sha256": payload["input"]["content_sha256"],
        },
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.selection)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            selection_path=args.selection, output=args.out, payload=payload
        ),
    )
    menus = payload["construction"]["menus"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "construction_payload_sha256": payload[
                    "construction_payload_sha256"
                ],
                "source_contexts": menus["context_count"],
                "menu_channels": menus["channel_count"],
                "accounting_refinements": menus["accounting_refinement_count"],
                "exact_lifts": menus["exact_lift_count"],
                "max_menu_size": menus["max_menu_size"],
                "operation_kinds": payload["construction"]["exact_lifts"][
                    "operation_kinds"
                ],
                "good_4_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
