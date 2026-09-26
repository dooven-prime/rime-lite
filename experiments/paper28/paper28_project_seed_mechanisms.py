#!/usr/bin/env python3
"""Project the Paper XXVIII ``4+35`` seed into typed mechanism quotients.

The projector consumes released Paper XXVII theorem inputs, reconstructs every
tied endpoint-shortest admissible Type-I/II macro receipt, and retains exact
packet provenance. It does not read a selected completion or a winning label
when constructing the relation or either quotient.

The 39 rank-four contexts are the declared seed. To make exact composition a
real binary relation rather than an empty diagnostic, the projector also
closes their targets under the same future-free macro relation down to rank
one. Seed and low-rank closure receipts remain separately labelled.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mass_maturity_legacy import mass_rank, simplified_deadline
from paper28_mechanism_schema import SCHEMA as RECEIPT_SCHEMA
from paper28_mechanism_schema import (
    audit_composition_matrix,
    audit_unary_matrix,
    exact_receipt_sha256,
    validate_receipt,
)
from section_return_core import (
    CompleteExitOracle,
    LowRankOracle,
    PacketState,
    activated_edge_summary,
    deserialize_packet_state,
    mass_partition,
    packet_mass,
    serialize_packet_state,
    trace_packets,
)

CATALOG_SCHEMA = "paper28-seed-mechanism-catalog-v1"
N6_INPUT_SCHEMA = "single-defect-n6-rank4-activated-entry-exhaustiveness-v1"
N7_INPUT_SCHEMA = "SINGLE_DEFECT_N7_EXTREMAL_CHANNEL_COVER_V1"

HERE = Path(__file__).resolve().parent
LOCAL_N6_INPUT = (
    HERE.parent
    / "paper27"
    / "results"
    / "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_seed_mechanism_catalog_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_project_seed_mechanisms.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "costed_endpoint_diagnostic.py",
    "single_defect_macro_trap.py",
    "mass_maturity_legacy.py",
    "single_defect_transport.py",
    "kernel_mass_potential.py",
    "mass_rank_debt_n6.py",
    "families.py",
    "registry.py",
    "validation/validate_paper28_seed_mechanism_catalog.py",
)

OBSERVABLES = (
    "corridor_count",
    "corridor_lengths",
    "corridor_surpluses",
    "debt_profile",
    "exact_ancestry_update",
    "exact_target_transport_channel",
    "fusion_mass_pattern",
    "fusion_packet_identity",
    "rank_drop_vector",
    "residual_tail_budget",
    "source_packet_identity",
    "source_target_shape",
    "target_in_exact_P_le3",
    "total_surplus",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def write_catalog(path: Path, payload: Mapping[str, Any]) -> None:
    """Write deterministic gzip bytes (including a zero gzip timestamp)."""

    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def read_catalog(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()).decode("ascii"))


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def build_receipt(
    *,
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
        "schema": "paper28-seed-mechanism-catalog-receipt-v1",
        "verification_mode": "LOCAL_REPLAY_WITH_BOUND_RELEASE_INPUTS",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": payload["inputs"],
        "source_closure": closure,
    }


def write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _cycle(n: int) -> tuple[int, ...]:
    return tuple((coordinate + 1) % n for coordinate in range(n))


def _defect_from_string(value: str) -> tuple[int, ...]:
    return tuple(int(character) for character in value)


def _packet_rows(state: PacketState) -> list[dict[str, Any]]:
    return serialize_packet_state(state)


def _context_payload(
    *,
    n: int,
    defect: Sequence[int],
    packets: PacketState,
    distinguished: frozenset[int],
) -> dict[str, Any]:
    body = {
        "ambient_n": int(n),
        "defect": [int(value) for value in defect],
        "packets": _packet_rows(packets),
        "distinguished_packet": sorted(distinguished),
    }
    return {"context_id": f"ctx-{_digest(body)[:24]}", **body}


def _canonical_n7_packets(
    context: Mapping[str, Any],
) -> tuple[PacketState, frozenset[int]]:
    """Give the released role-addressed carrier a canonical atom labelling."""

    role_order = {"F4": 0, "D1": 1, "D2": 2, "s": 3}
    rows = list(context["source_geometry"]["packet_roles"])

    def base_role(row: Mapping[str, Any]) -> str:
        return str(row["role"]).split("@", 1)[0]

    rows.sort(key=lambda row: (role_order[base_role(row)], int(row["coordinate"])))
    packets: PacketState = {}
    next_atom = 0
    distinguished: frozenset[int] | None = None
    for row in rows:
        size = int(row["mass"])
        packet = frozenset(range(next_atom, next_atom + size))
        next_atom += size
        packets[int(row["coordinate"])] = packet
        if base_role(row) == "F4":
            distinguished = packet
    if next_atom != 7 or distinguished is None:
        raise AssertionError("n=7 carrier failed canonical packet reconstruction")
    return packets, distinguished


def _participation_type(
    distinguished: frozenset[int], fusions: Sequence[Mapping[str, Any]]
) -> str:
    flags = [
        any(
            distinguished.issubset(frozenset(int(value) for value in parent))
            for parent in fusion["parent_packets"]
        )
        for fusion in fusions
    ]
    lookup = {
        (True,): "FIRST_ONLY",
        (False,): "NONE",
        (True, True): "BOTH",
        (True, False): "FIRST_ONLY",
        (False, True): "SECOND_ONLY",
        (False, False): "NONE",
    }
    try:
        return lookup[tuple(flags)]
    except KeyError as error:
        raise AssertionError(
            f"unsupported ancestry participation flags: {flags!r}"
        ) from error


def _parent_role(
    packet: frozenset[int],
    *,
    distinguished: frozenset[int],
    first_fresh: frozenset[int] | None,
) -> str:
    if first_fresh is not None and packet == first_fresh:
        suffix = "_WITH_CURRENT_F" if distinguished.issubset(packet) else ""
        return f"FRESH_1{suffix}"
    if packet == distinguished:
        return "CURRENT_F"
    if distinguished.issubset(packet):
        return "CARRIES_CURRENT_F"
    return f"OTHER_M{len(packet)}"


def _fusion_skeleton(
    fusions: Sequence[Mapping[str, Any]], distinguished: frozenset[int]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    first_fresh: frozenset[int] | None = None
    for index, fusion in enumerate(fusions):
        parents = [
            frozenset(int(value) for value in row)
            for row in fusion["parent_packets"]
        ]
        descriptors = sorted(
            (
                len(packet),
                _parent_role(
                    packet,
                    distinguished=distinguished,
                    first_fresh=first_fresh,
                ),
            )
            for packet in parents
        )
        rows.append(
            {
                "parent_masses": [mass for mass, _ in descriptors],
                "parent_roles": [role for _, role in descriptors],
                "result_mass": int(fusion["fresh_size"]),
            }
        )
        if index == 0:
            first_fresh = frozenset(
                int(value) for value in fusion["fresh_packet"]
            )
    return rows


def _fusion_exact(fusion: Mapping[str, Any]) -> dict[str, Any]:
    parents = sorted(
        (
            int(coordinate),
            sorted(int(value) for value in packet),
        )
        for coordinate, packet in zip(
            fusion["boundary_parent_coordinates"],
            fusion["parent_packets"],
            strict=True,
        )
    )
    return {
        "parent_coordinates": [coordinate for coordinate, _ in parents],
        "parents": [packet for _, packet in parents],
        "result": sorted(int(value) for value in fusion["fresh_packet"]),
        "target_coordinate": int(fusion["target_coordinate"]),
    }


def _corridor_boundary(
    state: PacketState,
    word: Sequence[int],
    letters: tuple[tuple[int, ...], ...],
) -> dict[str, Any]:
    return {
        "source": _packet_rows(state),
        "preterminal": _packet_rows(trace_packets(state, word[:-1], letters)),
        "target": _packet_rows(trace_packets(state, word, letters)),
    }


def _debt_profile(surpluses: Sequence[int]) -> list[int]:
    total = 0
    result = [0]
    for surplus in surpluses:
        total += int(surplus)
        result.append(max(0, -total))
    return result


def _target_budget(target: Sequence[int], n: int) -> int:
    reset = (n,) + (0,) * (n - 1)
    return simplified_deadline(reset, n) - simplified_deadline(tuple(target), n)


@dataclass(frozen=True)
class Context:
    n: int
    defect: tuple[int, ...]
    packets: PacketState
    distinguished: frozenset[int]
    origin: str
    seed_surface: str
    is_seed: bool

    @property
    def mass(self) -> tuple[int, ...]:
        return packet_mass(self.packets, self.n)

    @property
    def payload(self) -> dict[str, Any]:
        return _context_payload(
            n=self.n,
            defect=self.defect,
            packets=self.packets,
            distinguished=self.distinguished,
        )

    @property
    def context_id(self) -> str:
        return str(self.payload["context_id"])


def _record_from_edge(
    context: Context,
    edge: Mapping[str, Any],
    *,
    low_rank: LowRankOracle,
) -> tuple[dict[str, Any], Context]:
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

    fresh_packets = [
        frozenset(int(value) for value in fusion["fresh_packet"])
        for fusion in fusions
    ]
    new_distinguished = fresh_packets[-1]
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
        "schema": RECEIPT_SCHEMA,
        "receipt_id": "pending",
        "seed_surface": context.seed_surface,
        "relation_role": "SEED" if context.is_seed else "LOW_RANK_CLOSURE",
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
            "target_in_exact_P_le3": low_rank.is_good(target_mass),
        },
    }
    record["receipt_id"] = f"r-{exact_receipt_sha256(record)[:24]}"
    validate_receipt(record)
    return record, target_context


def _n6_seeds(payload: Mapping[str, Any]) -> list[Context]:
    if payload.get("schema") != N6_INPUT_SCHEMA:
        raise AssertionError("unexpected n=6 Paper XXVII input schema")
    rows = [
        row
        for row in payload["synchronizing_action_rows"]
        if int(
            row["entry_choice_audit"]["section_choice"][
                "local_type_i_descent_count"
            ]
        )
        == 0
    ]
    if len(rows) != 4:
        raise AssertionError(f"n=6 Type-II-only seed drift: {len(rows)}")
    seeds = []
    for row in rows:
        choice = row["entry_choice_audit"]["section_choice"]
        packets = deserialize_packet_state(
            choice["activated_basis"]["checkpoint_packets"]
        )
        distinguished = frozenset(
            int(value)
            for value in choice["activated_basis"]["ancestry"]["fresh_packet"]
        )
        defect_text = str(row["defect"])
        seeds.append(
            Context(
                n=6,
                defect=_defect_from_string(defect_text),
                packets=packets,
                distinguished=distinguished,
                origin=f"n6-defect-{defect_text}",
                seed_surface="N6_TYPE_II_ONLY_SECTION",
                is_seed=True,
            )
        )
    return seeds


def _n7_seeds(payload: Mapping[str, Any]) -> list[Context]:
    if payload.get("schema") != N7_INPUT_SCHEMA:
        raise AssertionError("unexpected n=7 Paper XXVII input schema")
    contexts = list(payload["contexts"])
    if len(contexts) != 35:
        raise AssertionError(f"n=7 extremal carrier seed drift: {len(contexts)}")
    seeds = []
    for row in contexts:
        packets, distinguished = _canonical_n7_packets(row)
        defect = tuple(
            int(value) for value in row["source_geometry"]["defect_map"]
        )
        if packet_mass(packets, 7) != tuple(
            int(value) for value in row["source_mass"]
        ):
            raise AssertionError("n=7 canonical packets miss released source mass")
        seeds.append(
            Context(
                n=7,
                defect=defect,
                packets=packets,
                distinguished=distinguished,
                origin=f"n7-carrier-{int(row['index'])}-{row['defect']}",
                seed_surface="N7_EXTREMAL_35_CARRIER",
                is_seed=True,
            )
        )
    return seeds


def _project_relation(
    seeds: Sequence[Context],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    grouped: dict[tuple[int, tuple[int, ...]], list[Context]] = {}
    for seed in seeds:
        grouped.setdefault((seed.n, seed.defect), []).append(seed)

    seen_contexts: set[str] = set()
    records_by_id: dict[str, dict[str, Any]] = {}
    source_receipts: dict[str, set[str]] = {}
    context_rows: dict[str, dict[str, Any]] = {}

    for action_key in sorted(grouped):
        n, defect = action_key
        queue = deque(grouped[action_key])
        oracle = CompleteExitOracle((_cycle(n), defect), n)
        low_rank = LowRankOracle(oracle)
        while queue:
            context = queue.popleft()
            if context.context_id in seen_contexts:
                continue
            seen_contexts.add(context.context_id)
            context_rows[context.context_id] = context.payload
            if mass_rank(context.mass) <= 1:
                continue
            receipts = source_receipts.setdefault(context.context_id, set())
            for edge in oracle.macro_edges(context.mass):
                record, target_context = _record_from_edge(
                    context, edge, low_rank=low_rank
                )
                receipt_id = str(record["receipt_id"])
                previous = records_by_id.get(receipt_id)
                if previous is not None and previous != record:
                    raise AssertionError("exact receipt digest collision")
                records_by_id[receipt_id] = record
                receipts.add(receipt_id)
                context_rows.setdefault(target_context.context_id, target_context.payload)
                if mass_rank(target_context.mass) > 1:
                    queue.append(target_context)

    records = sorted(records_by_id.values(), key=lambda row: str(row["receipt_id"]))
    compatibility: list[dict[str, str]] = []
    for record in records:
        target_context_id = str(record["exact"]["target_context"]["context_id"])
        for successor_id in sorted(source_receipts.get(target_context_id, ())):
            compatibility.append(
                {
                    "source_receipt_id": str(record["receipt_id"]),
                    "successor_receipt_id": successor_id,
                }
            )
    compatibility.sort(
        key=lambda row: (row["source_receipt_id"], row["successor_receipt_id"])
    )
    context_summary = {
        "context_count": len(context_rows),
        "processed_source_context_count": len(source_receipts),
        "rank_counts": dict(
            sorted(
                (
                    str(rank),
                    count,
                )
                for rank, count in Counter(
                    len(row["packets"]) for row in context_rows.values()
                ).items()
            )
        ),
    }
    return records, compatibility, context_summary


def _classification(
    unary_matrix: Sequence[Mapping[str, Any]],
) -> dict[str, list[str]]:
    rows = {
        (str(row["observable"]), str(row["quotient_level"])): bool(
            row["descends"]
        )
        for row in unary_matrix
    }
    result = {"skeleton": [], "accounting_only": [], "exact_only": []}
    for observable in OBSERVABLES:
        if rows[(observable, "skeleton")]:
            result["skeleton"].append(observable)
        elif rows[(observable, "accounting")]:
            result["accounting_only"].append(observable)
        else:
            result["exact_only"].append(observable)
    return result


def build_payload(n6_input: Path, n7_input: Path) -> dict[str, Any]:
    n6_payload = _load(n6_input)
    n7_payload = _load(n7_input)
    seeds = _n6_seeds(n6_payload) + _n7_seeds(n7_payload)
    if len(seeds) != 39:
        raise AssertionError("4+35 seed count drift")

    records, compatibility_rows, context_summary = _project_relation(seeds)
    compatibility_edges = [
        (row["source_receipt_id"], row["successor_receipt_id"])
        for row in compatibility_rows
    ]
    unary_matrix = audit_unary_matrix(records, OBSERVABLES)
    composition_matrix = audit_composition_matrix(records, compatibility_edges)

    seed_receipts = [row for row in records if row["relation_role"] == "SEED"]
    closure_receipts = [
        row
        for row in records
        if row["relation_role"] == "LOW_RANK_CLOSURE"
    ]
    counts = {
        "seed_contexts": 39,
        "n6_seed_contexts": 4,
        "n7_seed_contexts": 35,
        "exact_receipts": len(records),
        "seed_receipts": len(seed_receipts),
        "low_rank_closure_receipts": len(closure_receipts),
        "compatibility_edges": len(compatibility_rows),
        "type_i_receipts": sum(
            row["skeleton"]["return_type"] == "ONE_CORRIDOR"
            for row in records
        ),
        "type_ii_receipts": sum(
            row["skeleton"]["return_type"] == "TWO_CORRIDOR_REPAYMENT"
            for row in records
        ),
    }
    payload = {
        "schema": CATALOG_SCHEMA,
        "scope": {
            "seed": "4 fixed-n=6 Type-II-only section contexts plus 35 fixed-n=7 extremal carrier contexts",
            "relation": "all tied endpoint-shortest admissible Type-I/II macro receipts from each seed and its strictly descending low-rank closure",
            "choice_forbidden_inputs": [
                "target membership in exact P_1/P_2/P_3",
                "winning or Bellman labels",
                "reset coaccessibility",
                "producer-selected preferred witnesses",
            ],
            "composition": "exact target/source typed-context equality, including outgoing distinguished ancestry",
            "nonclaim": "no all-n mechanism taxonomy, bounded-menu theorem, or Forced FFS conclusion",
        },
        "inputs": {
            "n6_entry_exhaustiveness": {
                "schema": n6_payload["schema"],
                "sha256": _sha256(n6_input),
            },
            "n7_extremal_carrier": {
                "schema": n7_payload["schema"],
                "sha256": _sha256(n7_input),
            },
        },
        "counts": counts,
        "contexts": context_summary,
        "observable_classification": _classification(unary_matrix),
        "unary_observable_audit": unary_matrix,
        "composition_congruence_audit": composition_matrix,
        "compatibility_edges": compatibility_rows,
        "receipts": records,
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def _release_input(relative_name: str) -> Path | None:
    release_root = os.environ.get("RIME_PAPER27_RELEASE_ROOT")
    if not release_root:
        return None
    candidate = (
        Path(release_root)
        / "experiments"
        / "paper27"
        / "results"
        / relative_name
    )
    return candidate if candidate.exists() else None


def _resolve_n6_input(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    released = _release_input(
        "single_defect_n6_rank4_activated_entry_exhaustiveness_v1.json"
    )
    if released is not None:
        return released
    if LOCAL_N6_INPUT.exists():
        return LOCAL_N6_INPUT
    raise SystemExit(
        "n=6 entry input not found; pass --n6-entry-input or set "
        "RIME_PAPER27_RELEASE_ROOT to the Paper XXVII v1 release root"
    )


def _resolve_n7_input(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    local = (
        HERE.parent
        / "paper27"
        / "results"
        / "single_defect_n7_extremal_carrier_input_v1.json"
    )
    if local.exists():
        return local
    released = _release_input("single_defect_n7_extremal_carrier_input_v1.json")
    if released is not None:
        return released
    raise SystemExit(
        "n=7 carrier input not found; pass --n7-carrier-input or set "
        "RIME_PAPER27_RELEASE_ROOT to the Paper XXVII v1 release root"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n6-entry-input", type=Path)
    parser.add_argument("--n7-carrier-input", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    n6_input = _resolve_n6_input(args.n6_entry_input)
    n7_input = _resolve_n7_input(args.n7_carrier_input)
    payload = build_payload(n6_input.resolve(), n7_input.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_catalog(args.output, payload)
    receipt_path = args.receipt or default_receipt_path(args.output)
    write_receipt(receipt_path, build_receipt(output=args.output, payload=payload))
    print(
        json.dumps(
            {
                "output": args.output.as_posix(),
                "receipt": receipt_path.as_posix(),
                **payload["counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
