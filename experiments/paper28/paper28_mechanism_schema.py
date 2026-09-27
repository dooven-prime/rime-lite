#!/usr/bin/env python3
"""Typed records and quotient audits for the Paper XXVIII mechanism program.

This module does not discover mechanisms.  It defines the canonical interface
used by a future projector from existing source-addressed exact receipts.
Every observable is audited independently; sharing a quotient key is never
treated as proof that an observable descends.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

SCHEMA = "paper28-mechanism-receipt-v1"
QuotientLevel = Literal["accounting", "skeleton"]

SKELETON_FIELDS = (
    "ambient_n",
    "source_rank",
    "target_rank",
    "source_partition",
    "target_partition",
    "corridor_count",
    "rank_drop_vector",
    "fusion_chain",
    "ancestry_update_type",
    "return_type",
)

ACCOUNTING_FIELDS = (
    "corridors",
    "debt_profile",
    "residual_tail_budget",
)

EXACT_FIELDS = (
    "source_context_id",
    "source_packet_ids",
    "words",
    "corridor_boundaries",
    "fusion_packet_identities",
    "target_channel",
    "target_endpoint",
    "target_context",
    "ancestry_update",
)


def freeze_json(value: Any) -> Any:
    """Convert a canonical JSON value into a deterministic hashable value.

    Ordered JSON arrays remain ordered.  A relation-valued observable must
    therefore be sorted by its producer before it enters this module.
    """

    if isinstance(value, Mapping):
        return tuple(
            (str(key), freeze_json(item))
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"non-JSON mechanism value: {type(value).__name__}")


def _require_mapping(record: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = record.get(field)
    if not isinstance(value, Mapping):
        raise ValueError(f"{field!r} must be a mapping")
    return value


def _require_fields(
    record: Mapping[str, Any], fields: Iterable[str], *, where: str
) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise ValueError(f"{where} is missing fields: {', '.join(missing)}")


def validate_receipt(record: Mapping[str, Any]) -> None:
    """Validate the three-level receipt shape without asserting quotient soundness."""

    if record.get("schema") != SCHEMA:
        raise ValueError(f"unexpected mechanism schema: {record.get('schema')!r}")
    receipt_id = record.get("receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id:
        raise ValueError("receipt_id must be a nonempty string")

    skeleton = _require_mapping(record, "skeleton")
    accounting = _require_mapping(record, "accounting")
    exact = _require_mapping(record, "exact")
    _require_mapping(record, "observables")
    _require_fields(skeleton, SKELETON_FIELDS, where="skeleton")
    _require_fields(accounting, ACCOUNTING_FIELDS, where="accounting")
    _require_fields(exact, EXACT_FIELDS, where="exact")

    ambient_n = int(skeleton["ambient_n"])
    source_partition = tuple(int(value) for value in skeleton["source_partition"])
    target_partition = tuple(int(value) for value in skeleton["target_partition"])
    if len(source_partition) != int(skeleton["source_rank"]):
        raise ValueError("source_rank does not match source_partition")
    if len(target_partition) != int(skeleton["target_rank"]):
        raise ValueError("target_rank does not match target_partition")
    if sum(source_partition) != ambient_n or sum(target_partition) != ambient_n:
        raise ValueError("packet partitions do not have ambient mass")

    corridors = accounting["corridors"]
    if not isinstance(corridors, list):
        raise ValueError("accounting.corridors must be a list")
    if len(corridors) != int(skeleton["corridor_count"]):
        raise ValueError("corridor_count does not match accounting.corridors")
    for index, corridor in enumerate(corridors):
        if not isinstance(corridor, Mapping):
            raise ValueError(f"accounting.corridors[{index}] must be a mapping")
        _require_fields(
            corridor,
            ("rank_drop", "delta_m", "length", "surplus"),
            where=f"accounting.corridors[{index}]",
        )
    rank_drops = tuple(int(value) for value in skeleton["rank_drop_vector"])
    corridor_drops = tuple(int(corridor["rank_drop"]) for corridor in corridors)
    if rank_drops != corridor_drops:
        raise ValueError("rank_drop_vector does not match accounting.corridors")
    if sum(rank_drops) != int(skeleton["source_rank"]) - int(
        skeleton["target_rank"]
    ):
        raise ValueError("rank-drop total does not match source and target ranks")

    current_rank = int(skeleton["source_rank"])
    for index, corridor in enumerate(corridors):
        rank_drop = int(corridor["rank_drop"])
        delta_m = int(corridor["delta_m"])
        length = int(corridor["length"])
        expected_surplus = (
            2 * delta_m
            + rank_drop * (2 * current_rank - rank_drop - ambient_n - 1)
            - length
        )
        if int(corridor["surplus"]) != expected_surplus:
            raise ValueError(
                f"accounting.corridors[{index}] violates the surplus identity"
            )
        current_rank -= rank_drop

    debt_profile = accounting["debt_profile"]
    if not isinstance(debt_profile, list) or len(debt_profile) != len(corridors) + 1:
        raise ValueError("debt_profile must record every corridor boundary")

    words = exact["words"]
    boundaries = exact["corridor_boundaries"]
    if not isinstance(words, list) or len(words) != len(corridors):
        raise ValueError("exact.words must record every corridor")
    if not isinstance(boundaries, list) or len(boundaries) != len(corridors):
        raise ValueError("exact.corridor_boundaries must record every corridor")
    for index, (word, corridor) in enumerate(zip(words, corridors, strict=True)):
        if not isinstance(word, list) or len(word) != int(corridor["length"]):
            raise ValueError(
                f"exact.words[{index}] does not match the corridor length"
            )

    source_packets = exact["source_packet_ids"]
    if not isinstance(source_packets, list):
        raise ValueError("exact.source_packet_ids must be a list")
    packet_sizes = tuple(
        sorted((len(packet) for packet in source_packets), reverse=True)
    )
    if packet_sizes != tuple(sorted(source_partition, reverse=True)):
        raise ValueError("source packet identities do not match source_partition")


def quotient_key(record: Mapping[str, Any], level: QuotientLevel) -> Any:
    """Return the proposed quotient key at ``level``.

    This function defines fibers only.  ``audit_observable`` decides whether a
    theorem observable is constant on those fibers.
    """

    validate_receipt(record)
    skeleton = record["skeleton"]
    if level == "skeleton":
        return freeze_json(skeleton)
    if level == "accounting":
        return freeze_json(
            {"skeleton": skeleton, "accounting": record["accounting"]}
        )
    raise ValueError(f"unknown quotient level: {level!r}")


def exact_receipt_key(record: Mapping[str, Any]) -> Any:
    """Return the over-retained exact identity before either quotient."""

    validate_receipt(record)
    return freeze_json(
        {
            "skeleton": record["skeleton"],
            "accounting": record["accounting"],
            "exact": record["exact"],
        }
    )


def exact_receipt_sha256(record: Mapping[str, Any]) -> str:
    """Return a stable digest suitable for a projector-generated receipt id."""

    return _key_sha256(exact_receipt_key(record))


@dataclass(frozen=True)
class HostilePair:
    quotient_level: QuotientLevel
    observable: str
    left_receipt_id: str
    right_receipt_id: str
    left_value: Any
    right_value: Any

    def as_json(self) -> dict[str, Any]:
        return {
            "quotient_level": self.quotient_level,
            "observable": self.observable,
            "left_receipt_id": self.left_receipt_id,
            "right_receipt_id": self.right_receipt_id,
            "left_value": self.left_value,
            "right_value": self.right_value,
        }


@dataclass(frozen=True)
class ObservableAudit:
    quotient_level: QuotientLevel
    observable: str
    receipt_count: int
    fiber_count: int
    nonconstant_fiber_count: int
    hostile_pairs: tuple[HostilePair, ...]

    @property
    def descends(self) -> bool:
        return self.nonconstant_fiber_count == 0

    def as_json(self) -> dict[str, Any]:
        return {
            "audit_kind": "unary_observable_descent",
            "quotient_level": self.quotient_level,
            "observable": self.observable,
            "descends": self.descends,
            "receipt_count": self.receipt_count,
            "fiber_count": self.fiber_count,
            "nonconstant_fiber_count": self.nonconstant_fiber_count,
            "hostile_pairs": [pair.as_json() for pair in self.hostile_pairs],
        }


@dataclass(frozen=True)
class CompositionHostilePair:
    quotient_level: QuotientLevel
    left_source_receipt_id: str
    right_source_receipt_id: str
    missing_from_receipt_id: str
    successor_class_sha256: str
    witness_successor_receipt_id: str

    def as_json(self) -> dict[str, Any]:
        return {
            "quotient_level": self.quotient_level,
            "left_source_receipt_id": self.left_source_receipt_id,
            "right_source_receipt_id": self.right_source_receipt_id,
            "missing_from_receipt_id": self.missing_from_receipt_id,
            "successor_class_sha256": self.successor_class_sha256,
            "witness_successor_receipt_id": self.witness_successor_receipt_id,
        }


@dataclass(frozen=True)
class CompositionAudit:
    quotient_level: QuotientLevel
    receipt_count: int
    compatibility_edge_count: int
    source_fiber_count: int
    noncongruent_fiber_count: int
    nonempty_mismatch_fiber_count: int
    hostile_pairs: tuple[CompositionHostilePair, ...]

    @property
    def successor_classes_descend(self) -> bool:
        return self.noncongruent_fiber_count == 0

    @property
    def nonemptiness_descends(self) -> bool:
        return self.nonempty_mismatch_fiber_count == 0

    def as_json(self) -> dict[str, Any]:
        return {
            "audit_kind": "composition_congruence",
            "quotient_level": self.quotient_level,
            "successor_classes_descend": self.successor_classes_descend,
            "nonemptiness_descends": self.nonemptiness_descends,
            "receipt_count": self.receipt_count,
            "compatibility_edge_count": self.compatibility_edge_count,
            "source_fiber_count": self.source_fiber_count,
            "noncongruent_fiber_count": self.noncongruent_fiber_count,
            "nonempty_mismatch_fiber_count": self.nonempty_mismatch_fiber_count,
            "hostile_pairs": [pair.as_json() for pair in self.hostile_pairs],
        }


def audit_observable(
    records: Iterable[Mapping[str, Any]],
    *,
    level: QuotientLevel,
    observable: str,
) -> ObservableAudit:
    """Test whether one declared observable is constant on every quotient fiber."""

    rows = sorted(records, key=lambda row: str(row.get("receipt_id", "")))
    fibers: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        validate_receipt(row)
        observables = row["observables"]
        if observable not in observables:
            raise ValueError(
                f"receipt {row['receipt_id']!r} lacks observable {observable!r}"
            )
        fibers[quotient_key(row, level)].append(row)

    hostile_pairs: list[HostilePair] = []
    for fiber in fibers.values():
        left = fiber[0]
        left_value = freeze_json(left["observables"][observable])
        for right in fiber[1:]:
            right_value = freeze_json(right["observables"][observable])
            if right_value != left_value:
                hostile_pairs.append(
                    HostilePair(
                        quotient_level=level,
                        observable=observable,
                        left_receipt_id=str(left["receipt_id"]),
                        right_receipt_id=str(right["receipt_id"]),
                        left_value=left["observables"][observable],
                        right_value=right["observables"][observable],
                    )
                )
                break

    return ObservableAudit(
        quotient_level=level,
        observable=observable,
        receipt_count=len(rows),
        fiber_count=len(fibers),
        nonconstant_fiber_count=len(hostile_pairs),
        hostile_pairs=tuple(hostile_pairs),
    )


def audit_unary_matrix(
    records: Iterable[Mapping[str, Any]], observables: Iterable[str]
) -> list[dict[str, Any]]:
    """Return deterministic accounting/skeleton audits for each observable."""

    rows = list(records)
    return [
        audit_observable(rows, level=level, observable=observable).as_json()
        for observable in sorted(set(observables))
        for level in ("accounting", "skeleton")
    ]


def _key_sha256(key: Any) -> str:
    encoded = json.dumps(
        key, ensure_ascii=True, separators=(",", ":"), default=list
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def audit_composition(
    records: Iterable[Mapping[str, Any]],
    compatibility_edges: Iterable[tuple[str, str]],
    *,
    level: QuotientLevel,
) -> CompositionAudit:
    """Audit whether exact compatibility induces a quotient successor relation.

    For every exact receipt ``x``, the audited successor set is
    ``{q(y): Comp(x, y)}``.  Full composition congruence requires this set to
    be constant on each source quotient fiber.  The weaker nonempty result is
    reported separately and is never promoted to full congruence.
    """

    rows = sorted(records, key=lambda row: str(row.get("receipt_id", "")))
    by_id: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        validate_receipt(row)
        receipt_id = str(row["receipt_id"])
        if receipt_id in by_id:
            raise ValueError(f"duplicate receipt_id: {receipt_id!r}")
        by_id[receipt_id] = row

    successors: dict[str, dict[Any, str]] = {receipt_id: {} for receipt_id in by_id}
    normalized_edges = sorted(set(compatibility_edges))
    for source_id, target_id in normalized_edges:
        if source_id not in by_id or target_id not in by_id:
            raise ValueError(
                f"composition edge references unknown receipt: {(source_id, target_id)!r}"
            )
        target_key = quotient_key(by_id[target_id], level)
        successors[source_id].setdefault(target_key, target_id)

    source_fibers: dict[Any, list[str]] = defaultdict(list)
    for receipt_id, row in by_id.items():
        source_fibers[quotient_key(row, level)].append(receipt_id)

    hostile_pairs: list[CompositionHostilePair] = []
    nonempty_mismatch_count = 0
    for source_ids in source_fibers.values():
        reference_id = source_ids[0]
        reference = successors[reference_id]
        nonempty_values = {bool(successors[source_id]) for source_id in source_ids}
        if len(nonempty_values) > 1:
            nonempty_mismatch_count += 1
        for other_id in source_ids[1:]:
            other = successors[other_id]
            if reference.keys() == other.keys():
                continue
            left_only = sorted(
                set(reference).difference(other), key=lambda key: _key_sha256(key)
            )
            if left_only:
                successor_key = left_only[0]
                missing_from = other_id
                witness_id = reference[successor_key]
            else:
                successor_key = sorted(
                    set(other).difference(reference), key=lambda key: _key_sha256(key)
                )[0]
                missing_from = reference_id
                witness_id = other[successor_key]
            hostile_pairs.append(
                CompositionHostilePair(
                    quotient_level=level,
                    left_source_receipt_id=reference_id,
                    right_source_receipt_id=other_id,
                    missing_from_receipt_id=missing_from,
                    successor_class_sha256=_key_sha256(successor_key),
                    witness_successor_receipt_id=witness_id,
                )
            )
            break

    return CompositionAudit(
        quotient_level=level,
        receipt_count=len(rows),
        compatibility_edge_count=len(normalized_edges),
        source_fiber_count=len(source_fibers),
        noncongruent_fiber_count=len(hostile_pairs),
        nonempty_mismatch_fiber_count=nonempty_mismatch_count,
        hostile_pairs=tuple(hostile_pairs),
    )


def audit_composition_matrix(
    records: Iterable[Mapping[str, Any]],
    compatibility_edges: Iterable[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Return deterministic congruence audits at both proposed quotient levels."""

    rows = list(records)
    edges = list(compatibility_edges)
    return [
        audit_composition(rows, edges, level=level).as_json()
        for level in ("accounting", "skeleton")
    ]
