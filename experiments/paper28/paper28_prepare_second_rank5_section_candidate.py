#!/usr/bin/env python3
"""Freeze the second P28.5 rank-five menus/lifts before Good_5 evaluation."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from paper28_evaluate_second_rank4_section_return import (
    SCHEMA as LOWER_SECTION_SCHEMA,
)
from paper28_prepare_rank5_section_candidate import (
    CYCLE,
    _boundary_key,
    _factorization_summary,
    _record_from_rank5_edge,
)
from paper28_project_seed_mechanisms import Context
from paper28_select_second_rank5_return_candidate import (
    SCHEMA as SELECTION_SCHEMA,
)
from section_return_core import CompleteExitOracle


SCHEMA = "paper28-second-rank5-section-candidate-v1"
RECEIPT_SCHEMA = "paper28-second-rank5-section-candidate-receipt-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_SELECTION = (
    HERE / "results" / "paper28_second_rank5_return_candidate_selection_v1.json.gz"
)
DEFAULT_LOWER_SECTION = (
    HERE
    / "results"
    / "paper28_second_rank4_section_return_evaluation_v1.json.gz"
)
DEFAULT_OUTPUT = (
    HERE / "results" / "paper28_second_rank5_section_candidate_v1.json.gz"
)
SOURCE_CLOSURE = (
    "paper28_prepare_second_rank5_section_candidate.py",
    "paper28_evaluate_second_rank4_section_return.py",
    "paper28_prepare_rank5_section_candidate.py",
    "paper28_select_second_rank5_return_candidate.py",
    "paper28_project_seed_mechanisms.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_second_rank5_section_candidate.py",
)
N = 7
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


def _packet_map(rows: Sequence[Mapping[str, Any]]) -> dict[int, frozenset[int]]:
    packets = {
        int(row["coordinate"]): frozenset(int(value) for value in row["packet"])
        for row in rows
    }
    atoms = {value for packet in packets.values() for value in packet}
    if atoms != set(range(N)):
        raise AssertionError("typed packet state does not partition the atom set")
    return packets


def _context_from_selection(
    row: Mapping[str, Any],
) -> tuple[Context, dict[str, Any]]:
    defect_text = str(row["defect"])
    defect = tuple(int(value) for value in defect_text)
    if len(defect) != N:
        raise AssertionError("selection row has malformed defect")
    rank5 = row["rank5_context"]
    packets = _packet_map(rank5["packets"])
    distinguished = frozenset(
        int(value) for value in rank5["activation"]["fresh_packet"]
    )
    context = Context(
        n=N,
        defect=defect,
        packets=packets,
        distinguished=distinguished,
        origin=f"n7-rank5-candidate2-{defect_text}",
        seed_surface="N7_RANK5_SECOND_RETURN_CANDIDATE",
        is_seed=True,
    )
    if list(sorted((len(packet) for packet in packets.values()), reverse=True)) != [
        3,
        1,
        1,
        1,
        1,
    ]:
        raise AssertionError("second rank-five source partition drift")
    if list(context.mass) != [int(value) for value in rank5["mass"]]:
        raise AssertionError("selection mass placement and exact packets disagree")
    membership = {
        "defect": defect_text,
        "inherited_context_index": int(row["index"]),
        "membership_authority": (
            "frozen future-free P28.5d 31111__11_TO_3211 carrier selection"
        ),
        "membership_uses_lower_section_success": False,
        "source_partition": [3, 1, 1, 1, 1],
        "normalized_mass_placement": list(context.mass),
        "incoming_distinguished_packet": sorted(distinguished),
        "sigma6": row["sigma6"],
        "selected_sigma5": row["sigma5"],
        "carrier_signature": row["carrier_signature"],
        "context": context.payload,
    }
    return context, membership


def _selected_target_matches(
    *,
    row: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> bool:
    selected_word = [int(value) for value in row["sigma5"]["selected_word"]]
    expected_packets = _packet_map(row["rank4_context"]["packets"])
    expected_distinguished = sorted(
        int(value) for value in row["rank4_context"]["activation"]["fresh_packet"]
    )
    matches = []
    for record in records:
        if record["exact"]["words"] != [selected_word]:
            continue
        actual = record["exact"]["target_context"]
        actual_packets = _packet_map(actual["packets"])
        if actual_packets != expected_packets:
            continue
        if sorted(actual["distinguished_packet"]) != expected_distinguished:
            continue
        matches.append(record)
    return bool(matches)


def _construction_core(construction: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_contexts": construction["source_section"]["contexts"],
        "menu_contexts": construction["menus"]["contexts"],
        "exact_lifts": construction["exact_lifts"]["receipts"],
        "factorizations": construction["exact_lifts"]["factorizations"],
    }


def _build_source_menu_payload(selection_path: Path) -> dict[str, Any]:
    selection = _load(selection_path)
    if selection.get("schema") != SELECTION_SCHEMA:
        raise AssertionError("unexpected P28.5d selection schema")
    candidate = selection["candidate"]
    if candidate["recursive_authority"] != "NONE":
        raise AssertionError("P28.5d selection unexpectedly contains authority")
    if int(candidate["context_count"]) != 48:
        raise AssertionError("second carrier source count drift")
    if _digest(candidate) != selection["candidate_payload_sha256"]:
        raise AssertionError("P28.5d candidate payload digest mismatch")

    source_rows = []
    menu_rows = []
    records = []
    factorizations = []
    for selection_row in candidate["contexts"]:
        context, membership = _context_from_selection(selection_row)
        source_rows.append(membership)
        oracle = CompleteExitOracle((CYCLE, context.defect), N)
        rank4_edges = [
            edge
            for edge in oracle.macro_edges(context.mass)
            if int(edge["rank_target"]) == 4
        ]
        if not rank4_edges:
            raise AssertionError("second rank-five source has no rank-four lift")

        source_records = [
            _record_from_rank5_edge(
                context,
                edge,
                relation_role="RANK5_SECOND_SECTION_CANDIDATE",
            )
            for edge in rank4_edges
        ]
        if not _selected_target_matches(
            row=selection_row,
            records=source_records,
        ):
            raise AssertionError(
                "frozen inherited Sigma_5 receipt is absent from exact lift fiber"
            )
        records.extend(source_records)
        factorizations.extend(
            _factorization_summary(record) for record in source_records
        )

        channels: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in source_records:
            channels[_digest(record["skeleton"])].append(record)
        channel_rows = []
        for channel_digest, channel_records in sorted(channels.items()):
            accounting: dict[str, list[str]] = defaultdict(list)
            for record in channel_records:
                accounting[_digest(record["accounting"])].append(
                    str(record["receipt_id"])
                )
            representative = channel_records[0]
            channel_rows.append(
                {
                    "channel_id": f"r5c2m-{channel_digest[:24]}",
                    "interaction_skeleton": representative["skeleton"],
                    "accounting_refinements": [
                        {
                            "accounting_id": f"r5c2a-{key[:24]}",
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
        menu_rows.append(
            {
                "source_context_id": context.context_id,
                "menu_size": len(channel_rows),
                "channels": channel_rows,
            }
        )

    source_rows.sort(key=lambda row: (row["defect"], row["inherited_context_index"]))
    menu_rows.sort(key=lambda row: str(row["source_context_id"]))
    records.sort(key=lambda row: str(row["receipt_id"]))
    factorizations.sort(key=lambda row: str(row["receipt_id"]))
    if len({row["context"]["context_id"] for row in source_rows}) != 48:
        raise AssertionError("second rank-five exact source ids are not unique")

    factor_state_ids = {
        str(operation[side]["state_id"])
        for row in factorizations
        for operation in row["operation_occurrences"]
        for side in ("exact_source", "exact_target")
    }
    endpoint_state_ids = {
        str(row["source_state_id"]) for row in factorizations
    } | {str(row["target_state_id"]) for row in factorizations}
    construction = {
        "source_section": {
            "name": "Sec_5,cand2^(7)",
            "membership_rule": (
                "membership in the frozen future-free P28.5d "
                "31111__11_TO_3211 carrier, reconstructed from its exact "
                "rank-five packet state without lower-section success"
            ),
            "selection_input": {
                "name": selection_path.name,
                "schema": selection["schema"],
                "sha256": _sha256(selection_path),
                "content_sha256": selection["content_sha256"],
                "candidate_payload_sha256": selection[
                    "candidate_payload_sha256"
                ],
            },
            "forbidden_inputs": [
                "Sec_4,cand2^(7) membership",
                "Good_5",
                "lower-rank success",
                "winning or Bellman labels",
            ],
            "context_count": len(source_rows),
            "contexts": source_rows,
        },
        "menus": {
            "constructor": (
                "all tied endpoint-shortest one-corridor rank-five-to-four "
                "receipts, quotiented only by future-free interaction skeleton"
            ),
            "forbidden_inputs": list(FORBIDDEN_CONSTRUCTION_FIELDS),
            "context_count": len(menu_rows),
            "channel_count": sum(row["menu_size"] for row in menu_rows),
            "max_menu_size": max(row["menu_size"] for row in menu_rows),
            "contexts": menu_rows,
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
            "receipt_endpoint_state_count": len(endpoint_state_ids),
            "internal_only_state_count": len(
                factor_state_ids - endpoint_state_ids
            ),
            "internal_only_exported_as_checkpoint": 0,
        },
    }
    theorem_data = json.dumps(
        _construction_core(construction),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field.lower() in theorem_data:
            raise AssertionError(
                f"construction payload contains forbidden field: {field}"
            )
    return construction


def _project_lower_section(path: Path) -> dict[str, Any]:
    payload = _load(path)
    if payload.get("schema") != LOWER_SECTION_SCHEMA:
        raise AssertionError("unexpected second rank-four authority schema")
    evaluation = payload["evaluation"]
    authority = payload["certified_lower_section"]
    if not evaluation["all_sources_have_good_channel"]:
        raise AssertionError("lower carrier lacks fixed-scope F5 authority")
    if authority["authority_status"] != "GRANTED_BY_FIXED_SCOPE_GOOD4_EVALUATION":
        raise AssertionError("lower carrier authority status drift")
    if int(authority["context_count"]) != 48:
        raise AssertionError("lower carrier context count drift")

    rows = []
    for context in authority["contexts"]:
        packets = _packet_map(context["packets"])
        distinguished = frozenset(
            int(value) for value in context["distinguished_packet"]
        )
        rows.append(
            {
                "authority": "P28.5e fixed-scope Sec_4,cand2^(7)",
                "source_context_id": str(context["context_id"]),
                "section_boundary_key": _boundary_key(
                    defect=context["defect"],
                    packets=packets,
                    distinguished=distinguished,
                ),
            }
        )
    rows.sort(key=lambda row: str(row["source_context_id"]))
    if len({_digest(row["section_boundary_key"]) for row in rows}) != 48:
        raise AssertionError("lower section boundary keys are not unique")
    return {
        "name": "Sec_4,cand2^(7)",
        "input_name": path.name,
        "input_schema": payload["schema"],
        "input_sha256": _sha256(path),
        "input_content_sha256": payload["content_sha256"],
        "context_count": len(rows),
        "contexts": rows,
        "section_keys_sha256": _digest(
            [row["section_boundary_key"] for row in rows]
        ),
    }


def build_payload(
    selection_path: Path,
    lower_section_path: Path,
) -> dict[str, Any]:
    construction = _build_source_menu_payload(selection_path)
    construction_digest = _digest(construction)

    # The newly certified lower authority is opened only after the complete
    # source/menu/lift construction has been frozen and digested.
    lower_section = _project_lower_section(lower_section_path)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": N,
            "source": "future-free second rank-five candidate section",
            "target": "P28.5e Sec_4,cand2^(7)",
            "evaluation_status": "NOT_RUN",
            "nonclaim": (
                "this artifact freezes source, menu, exact lifts, and lower "
                "authority but does not evaluate Good_5"
            ),
        },
        "phase_order": [
            "load_future_free_P28_5d_source_selection",
            "construct_rank5_source_menus_and_exact_lifts",
            "freeze_construction_payload_digest",
            "load_independent_P28_5e_lower_authority",
            "future_Good_5_evaluator_not_run",
        ],
        "construction_payload_sha256": construction_digest,
        "construction": construction,
        "lower_section_target": lower_section,
        "evaluator": {
            "status": "ABSENT_BY_DESIGN",
            "good_predicate_defined_for_later_phase": (
                "Good_5(C,m) iff an exact lift in Lift_5(C,m) admits a "
                "typed handoff to Sec_4,cand2^(7)"
            ),
            "evaluated_source_count": 0,
            "evaluated_channel_count": 0,
        },
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *,
    selection_path: Path,
    lower_section_path: Path,
    output: Path,
    payload: Mapping[str, Any],
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
        "verification_mode": "PRE_EVALUATION_WITH_BOUND_AUTHORITIES",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "construction_payload_sha256": payload[
                "construction_payload_sha256"
            ],
        },
        "inputs": {
            "future_free_source_selection": {
                "name": selection_path.name,
                "sha256": _sha256(selection_path),
            },
            "lower_section_authority": {
                "name": lower_section_path.name,
                "sha256": _sha256(lower_section_path),
            },
        },
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument(
        "--lower-section",
        type=Path,
        default=DEFAULT_LOWER_SECTION,
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.selection, args.lower_section)
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    _write_receipt(
        receipt_path,
        build_receipt(
            selection_path=args.selection,
            lower_section_path=args.lower_section,
            output=args.out,
            payload=payload,
        ),
    )
    construction = payload["construction"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": args.out.as_posix(),
                "artifact_sha256": _sha256(args.out),
                "source_contexts": construction["source_section"][
                    "context_count"
                ],
                "menu_channels": construction["menus"]["channel_count"],
                "max_menu_size": construction["menus"]["max_menu_size"],
                "exact_lifts": construction["exact_lifts"]["receipt_count"],
                "good_5_evaluation": "NOT_RUN",
                "lower_section": payload["lower_section_target"]["name"],
                "section_authority": "NOT_GRANTED_BY_THIS_ARTIFACT",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
