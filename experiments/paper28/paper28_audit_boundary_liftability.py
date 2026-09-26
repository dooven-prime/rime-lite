#!/usr/bin/env python3
"""Audit boundary factorization and exact liftability for Paper XXVIII.

The input is the canonical ``4+35`` exact-receipt catalog.  This script does
not construct new automaton states or enlarge the receipt relation.  It asks
whether composition failures inside an accounting or interaction-skeleton
fiber are explained by the exact typed boundary, and whether progressively
coarser boundary quotients support a fiber-uniform successor relation.

Mechanism labels are treated as edge labels.  Exact semantic composition is
still defined by equality of the target and source typed contexts.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from paper28_mechanism_schema import freeze_json, quotient_key, validate_receipt

AUDIT_SCHEMA = "paper28-boundary-liftability-audit-v1"
RECEIPT_SCHEMA = "paper28-boundary-liftability-audit-receipt-v1"
CATALOG_SCHEMA = "paper28-seed-mechanism-catalog-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "results" / "paper28_seed_mechanism_catalog_v1.json.gz"
DEFAULT_OUTPUT = HERE / "results" / "paper28_boundary_liftability_audit_v1.json"
BOUNDARY_LEVELS = (
    "action",
    "normalized_mass",
    "ancestry_position",
    "role_typed",
    "exact_typed_context",
)
SOURCE_CLOSURE = (
    "paper28_audit_boundary_liftability.py",
    "paper28_mechanism_schema.py",
    "validation/validate_paper28_boundary_liftability_audit.py",
)

QuotientLevel = Literal["accounting", "skeleton"]


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
    return output.with_name(f"{output.stem}.receipt.json")


def _packet_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                "coordinate": int(row["coordinate"]),
                "mass": int(row["mass"]),
                "packet": sorted(int(atom) for atom in row["packet"]),
            }
            for row in rows
        ),
        key=lambda row: row["coordinate"],
    )


def _canonical_context(context: Mapping[str, Any]) -> dict[str, Any]:
    result = {
        "context_id": str(context["context_id"]),
        "ambient_n": int(context["ambient_n"]),
        "defect": [int(value) for value in context["defect"]],
        "packets": _packet_rows(context["packets"]),
        "distinguished_packet": sorted(
            int(atom) for atom in context["distinguished_packet"]
        ),
    }
    body = {key: value for key, value in result.items() if key != "context_id"}
    expected_id = f"ctx-{_digest(body)[:24]}"
    if result["context_id"] != expected_id:
        raise AssertionError(
            f"context id does not match typed payload: {result['context_id']}"
        )
    return result


def _source_context(record: Mapping[str, Any]) -> dict[str, Any]:
    exact = record["exact"]
    target = exact["target_context"]
    return _canonical_context(
        {
            "context_id": exact["source_context_id"],
            "ambient_n": target["ambient_n"],
            "defect": target["defect"],
            "packets": exact["corridor_boundaries"][0]["source"],
            "distinguished_packet": exact["ancestry_update"][
                "incoming_distinguished_packet"
            ],
        }
    )


def _target_context(record: Mapping[str, Any]) -> dict[str, Any]:
    return _canonical_context(record["exact"]["target_context"])


def _collect_contexts(records: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    contexts: dict[str, dict[str, Any]] = {}
    for record in records:
        for context in (_source_context(record), _target_context(record)):
            context_id = context["context_id"]
            previous = contexts.setdefault(context_id, context)
            if previous != context:
                raise AssertionError(f"context id has two payloads: {context_id}")
    return contexts


def _validate_exact_compatibility(
    records: Sequence[Mapping[str, Any]], edges: Sequence[tuple[str, str]]
) -> None:
    source_receipts: dict[str, list[str]] = defaultdict(list)
    by_id: dict[str, Mapping[str, Any]] = {}
    for record in records:
        receipt_id = str(record["receipt_id"])
        if receipt_id in by_id:
            raise AssertionError(f"duplicate receipt id: {receipt_id}")
        by_id[receipt_id] = record
        source_receipts[str(record["exact"]["source_context_id"])].append(receipt_id)

    expected = {
        (receipt_id, successor_id)
        for receipt_id, record in by_id.items()
        for successor_id in source_receipts.get(
            str(record["exact"]["target_context"]["context_id"]), ()
        )
    }
    observed = set(edges)
    if len(observed) != len(edges):
        raise AssertionError("duplicate exact compatibility edge")
    if observed != expected:
        raise AssertionError("compatibility edges do not equal typed boundary matching")


def _rank(context: Mapping[str, Any]) -> int:
    return len(context["packets"])


def _distinguished_row(context: Mapping[str, Any]) -> Mapping[str, Any]:
    distinguished = tuple(int(atom) for atom in context["distinguished_packet"])
    matches = [
        row
        for row in context["packets"]
        if tuple(int(atom) for atom in row["packet"]) == distinguished
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"distinguished packet is not one exact packet in {context['context_id']}"
        )
    return matches[0]


def boundary_signature(context: Mapping[str, Any], level: str) -> Any:
    """Return one future-free boundary projection in the declared hierarchy."""

    if level not in BOUNDARY_LEVELS:
        raise ValueError(f"unknown boundary level: {level!r}")
    action = {
        "ambient_n": int(context["ambient_n"]),
        "rank": _rank(context),
        "defect": [int(value) for value in context["defect"]],
    }
    if level == "action":
        return freeze_json(action)

    mass_rows = [
        {"coordinate": int(row["coordinate"]), "mass": int(row["mass"])}
        for row in context["packets"]
    ]
    normalized_mass = {"action": action, "mass_rows": mass_rows}
    if level == "normalized_mass":
        return freeze_json(normalized_mass)

    distinguished = _distinguished_row(context)
    ancestry_position = {
        "normalized_mass": normalized_mass,
        "distinguished_coordinate": int(distinguished["coordinate"]),
        "distinguished_mass": int(distinguished["mass"]),
    }
    if level == "ancestry_position":
        return freeze_json(ancestry_position)

    distinguished_packet = tuple(int(atom) for atom in context["distinguished_packet"])
    role_rows = [
        {
            "coordinate": int(row["coordinate"]),
            "mass": int(row["mass"]),
            "role": (
                "CURRENT_F"
                if tuple(int(atom) for atom in row["packet"])
                == distinguished_packet
                else f"OTHER_M{int(row['mass'])}"
            ),
        }
        for row in context["packets"]
    ]
    role_typed = {"action": action, "role_rows": role_rows}
    if level == "role_typed":
        return freeze_json(role_typed)

    return freeze_json(context)


def _successor_maps(
    records: Sequence[Mapping[str, Any]],
    edges: Sequence[tuple[str, str]],
    level: QuotientLevel,
) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    by_id = {str(record["receipt_id"]): record for record in records}
    receipt_successors: dict[str, set[str]] = {
        receipt_id: set() for receipt_id in by_id
    }
    for source_id, successor_id in edges:
        receipt_successors[source_id].add(
            _digest(quotient_key(by_id[successor_id], level))
        )
    frozen_receipt_successors = {
        receipt_id: frozenset(values)
        for receipt_id, values in receipt_successors.items()
    }

    context_successors: dict[str, set[str]] = defaultdict(set)
    for record in records:
        context_successors[str(record["exact"]["source_context_id"])].add(
            _digest(quotient_key(record, level))
        )
    return frozen_receipt_successors, {
        context_id: frozenset(values)
        for context_id, values in context_successors.items()
    }


def _profile_digest(profile: frozenset[str]) -> str:
    return _digest(sorted(profile))


def _uniform_after_boundary(
    receipt_ids: Sequence[str],
    by_id: Mapping[str, Mapping[str, Any]],
    successor_profiles: Mapping[str, frozenset[str]],
    level: str,
) -> bool:
    boundary_fibers: dict[Any, set[frozenset[str]]] = defaultdict(set)
    for receipt_id in receipt_ids:
        target = _target_context(by_id[receipt_id])
        boundary_fibers[boundary_signature(target, level)].add(
            successor_profiles[receipt_id]
        )
    return all(len(profiles) == 1 for profiles in boundary_fibers.values())


def _first_difference(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    for level in BOUNDARY_LEVELS:
        if boundary_signature(left, level) != boundary_signature(right, level):
            return level
    raise AssertionError("different successor profiles share one exact target context")


def _factorization_audit(
    records: Sequence[Mapping[str, Any]],
    edges: Sequence[tuple[str, str]],
    level: QuotientLevel,
) -> dict[str, Any]:
    by_id = {str(record["receipt_id"]): record for record in records}
    successor_profiles, _ = _successor_maps(records, edges, level)
    mechanism_fibers: dict[Any, list[str]] = defaultdict(list)
    for record in records:
        mechanism_fibers[quotient_key(record, level)].append(str(record["receipt_id"]))

    rows: list[dict[str, Any]] = []
    minimal_level_counts: Counter[str] = Counter()
    first_difference_counts: Counter[str] = Counter()
    for mechanism_key, receipt_ids in sorted(
        mechanism_fibers.items(), key=lambda item: _digest(item[0])
    ):
        receipt_ids.sort()
        profile_groups: dict[frozenset[str], list[str]] = defaultdict(list)
        for receipt_id in receipt_ids:
            profile_groups[successor_profiles[receipt_id]].append(receipt_id)
        if len(profile_groups) == 1:
            continue

        minimal_level = next(
            boundary_level
            for boundary_level in BOUNDARY_LEVELS
            if _uniform_after_boundary(
                receipt_ids,
                by_id,
                successor_profiles,
                boundary_level,
            )
        )
        minimal_level_counts[minimal_level] += 1

        ordered_profiles = sorted(
            profile_groups.items(), key=lambda item: _profile_digest(item[0])
        )
        left_id = min(ordered_profiles[0][1])
        right_id = min(ordered_profiles[1][1])
        left_target = _target_context(by_id[left_id])
        right_target = _target_context(by_id[right_id])
        first_difference = _first_difference(left_target, right_target)
        first_difference_counts[first_difference] += 1

        boundary_spectrum = {
            boundary_level: len(
                {
                    boundary_signature(_target_context(by_id[receipt_id]), boundary_level)
                    for receipt_id in receipt_ids
                }
            )
            for boundary_level in BOUNDARY_LEVELS
        }
        rows.append(
            {
                "mechanism_class_sha256": _digest(mechanism_key),
                "receipt_count": len(receipt_ids),
                "successor_profile_count": len(profile_groups),
                "successor_nonemptiness_values": sorted(
                    {bool(profile) for profile in profile_groups}
                ),
                "boundary_spectrum": boundary_spectrum,
                "minimal_uniform_boundary_level": minimal_level,
                "hostile_pair": {
                    "left_receipt_id": left_id,
                    "right_receipt_id": right_id,
                    "left_target_context_id": left_target["context_id"],
                    "right_target_context_id": right_target["context_id"],
                    "left_successor_profile_sha256": _profile_digest(
                        successor_profiles[left_id]
                    ),
                    "right_successor_profile_sha256": _profile_digest(
                        successor_profiles[right_id]
                    ),
                    "first_boundary_difference": first_difference,
                    "boundary_mismatches": {
                        boundary_level: boundary_signature(
                            left_target, boundary_level
                        )
                        != boundary_signature(right_target, boundary_level)
                        for boundary_level in BOUNDARY_LEVELS
                    },
                },
            }
        )

    return {
        "quotient_level": level,
        "mechanism_fiber_count": len(mechanism_fibers),
        "noncongruent_fiber_count": len(rows),
        "minimal_uniform_boundary_level_counts": dict(
            sorted(minimal_level_counts.items())
        ),
        "hostile_pair_first_difference_counts": dict(
            sorted(first_difference_counts.items())
        ),
        "exact_boundary_factorization_holds": True,
        "noncongruent_fibers": rows,
    }


def _context_boundary_audit(
    records: Sequence[Mapping[str, Any]],
    contexts: Mapping[str, Mapping[str, Any]],
    edges: Sequence[tuple[str, str]],
    quotient_level: QuotientLevel,
    boundary_level: str,
) -> dict[str, Any]:
    _, context_successors = _successor_maps(records, edges, quotient_level)
    fibers: dict[Any, list[str]] = defaultdict(list)
    for context_id, context in contexts.items():
        fibers[boundary_signature(context, boundary_level)].append(context_id)

    nonuniform_rows: list[dict[str, Any]] = []
    nonempty_mismatches = 0
    for signature, context_ids in sorted(
        fibers.items(), key=lambda item: _digest(item[0])
    ):
        profiles: dict[frozenset[str], list[str]] = defaultdict(list)
        for context_id in sorted(context_ids):
            profiles[context_successors.get(context_id, frozenset())].append(context_id)
        if len({bool(profile) for profile in profiles}) > 1:
            nonempty_mismatches += 1
        if len(profiles) == 1:
            continue
        ordered = sorted(profiles.items(), key=lambda item: _profile_digest(item[0]))
        nonuniform_rows.append(
            {
                "boundary_class_sha256": _digest(signature),
                "context_count": len(context_ids),
                "successor_profile_count": len(profiles),
                "witness_context_ids": [
                    min(ordered[0][1]),
                    min(ordered[1][1]),
                ],
                "witness_successor_profile_sha256": [
                    _profile_digest(ordered[0][0]),
                    _profile_digest(ordered[1][0]),
                ],
            }
        )

    return {
        "quotient_level": quotient_level,
        "boundary_level": boundary_level,
        "context_count": len(contexts),
        "boundary_fiber_count": len(fibers),
        "nonuniform_fiber_count": len(nonuniform_rows),
        "nonempty_mismatch_fiber_count": nonempty_mismatches,
        "fiber_uniform_liftability": not nonuniform_rows,
        "successor_nonemptiness_descends": nonempty_mismatches == 0,
        "hostile_examples": nonuniform_rows[:12],
    }


def _distribution(values: Sequence[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(int(value) for value in values).items())
    }


def _menu_fiber_audit(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    seed_records = [record for record in records if record["relation_role"] == "SEED"]
    by_context: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in seed_records:
        by_context[str(record["exact"]["source_context_id"])].append(record)

    rows: list[dict[str, Any]] = []
    for context_id, context_records in sorted(by_context.items()):
        skeleton_fibers: dict[Any, int] = Counter(
            quotient_key(record, "skeleton") for record in context_records
        )
        accounting_fibers: dict[Any, int] = Counter(
            quotient_key(record, "accounting") for record in context_records
        )
        rows.append(
            {
                "context_id": context_id,
                "seed_surface": str(context_records[0]["seed_surface"]),
                "origin": str(context_records[0]["origin"]),
                "exact_receipt_count": len(context_records),
                "skeleton_menu_size": len(skeleton_fibers),
                "accounting_menu_size": len(accounting_fibers),
                "skeleton_realization_fiber_sizes": sorted(skeleton_fibers.values()),
                "accounting_realization_fiber_sizes": sorted(accounting_fibers.values()),
            }
        )

    by_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_surface[row["seed_surface"]].append(row)
    summaries = {}
    for surface, surface_rows in sorted(by_surface.items()):
        summaries[surface] = {
            "context_count": len(surface_rows),
            "exact_receipt_count_distribution": _distribution(
                [row["exact_receipt_count"] for row in surface_rows]
            ),
            "skeleton_menu_size_distribution": _distribution(
                [row["skeleton_menu_size"] for row in surface_rows]
            ),
            "accounting_menu_size_distribution": _distribution(
                [row["accounting_menu_size"] for row in surface_rows]
            ),
            "max_exact_receipt_count": max(
                row["exact_receipt_count"] for row in surface_rows
            ),
            "max_skeleton_menu_size": max(
                row["skeleton_menu_size"] for row in surface_rows
            ),
            "max_accounting_menu_size": max(
                row["accounting_menu_size"] for row in surface_rows
            ),
        }

    all_skeleton_fibers = [
        size for row in rows for size in row["skeleton_realization_fiber_sizes"]
    ]
    all_accounting_fibers = [
        size for row in rows for size in row["accounting_realization_fiber_sizes"]
    ]
    return {
        "definition": {
            "abstract_menu": "distinct quotient labels among seed receipts from one exact source context",
            "realization_fiber": "all exact seed receipts with one source context and one abstract label",
            "boundedness_applies_to": "abstract_menu_cardinality",
            "boundedness_does_not_apply_to": "total_exact_realization_cardinality",
        },
        "surface_summaries": summaries,
        "skeleton_realization_fiber_size_distribution": _distribution(
            all_skeleton_fibers
        ),
        "accounting_realization_fiber_size_distribution": _distribution(
            all_accounting_fibers
        ),
        "contexts": rows,
    }


def build_audit(catalog: Mapping[str, Any], *, catalog_path: Path) -> dict[str, Any]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ValueError(f"unexpected catalog schema: {catalog.get('schema')!r}")
    records = list(catalog["receipts"])
    for record in records:
        validate_receipt(record)
    edges = [
        (str(row["source_receipt_id"]), str(row["successor_receipt_id"]))
        for row in catalog["compatibility_edges"]
    ]
    contexts = _collect_contexts(records)
    _validate_exact_compatibility(records, edges)

    factorization = [
        _factorization_audit(records, edges, level)
        for level in ("accounting", "skeleton")
    ]
    boundary_liftability = [
        _context_boundary_audit(
            records,
            contexts,
            edges,
            quotient_level,
            boundary_level,
        )
        for quotient_level in ("accounting", "skeleton")
        for boundary_level in BOUNDARY_LEVELS
    ]

    result: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "scope": {
            "construction": "projection-only audit of the canonical 4+35 catalog",
            "new_state_census": False,
            "composition": "exact target/source typed-context equality",
            "boundary_levels": list(BOUNDARY_LEVELS),
        },
        "input": {
            "path": catalog_path.relative_to(HERE.parents[1]).as_posix(),
            "sha256": _sha256(catalog_path),
            "content_sha256": catalog["content_sha256"],
            "exact_receipts": len(records),
            "compatibility_edges": len(edges),
        },
        "exact_context_count": len(contexts),
        "exact_compatibility_recomputed": True,
        "composition_failure_factorization": factorization,
        "context_boundary_liftability": boundary_liftability,
        "menu_realization_split": _menu_fiber_audit(records),
        "conclusions": {
            "mechanism_labels_are_edge_labels": True,
            "mechanism_quotients_are_not_composition_categories": True,
            "exact_typed_boundary_factors_composition": True,
            "boundedness_object": "abstract mechanism menu",
            "exact_realization_fibers_may_be_large": True,
        },
    }
    result["content_sha256"] = _digest(result)
    return result


def build_receipt(
    output: Path, payload: Mapping[str, Any], *, catalog_path: Path
) -> dict[str, Any]:
    repo_root = HERE.parents[1]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "LOCAL_REPLAY_FROM_BOUND_CANONICAL_CATALOG",
        "artifact": {
            "path": output.relative_to(repo_root).as_posix(),
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "input": {
            "path": catalog_path.relative_to(repo_root).as_posix(),
            "sha256": _sha256(catalog_path),
            "content_sha256": payload["input"]["content_sha256"],
        },
        "source_closure": [
            {
                "path": (HERE / relative).relative_to(repo_root).as_posix(),
                "sha256": _sha256(HERE / relative),
            }
            for relative in SOURCE_CLOSURE
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog_path = args.catalog.resolve()
    output = args.output.resolve()
    receipt_path = (
        args.receipt.resolve() if args.receipt else default_receipt_path(output)
    )
    catalog = _read_catalog(catalog_path)
    payload = build_audit(catalog, catalog_path=catalog_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_bytes(payload))
    receipt = build_receipt(output, payload, catalog_path=catalog_path)
    receipt_path.write_bytes(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True).encode("ascii")
        + b"\n"
    )
    print(
        json.dumps(
            {
                "output": output.as_posix(),
                "receipt": receipt_path.as_posix(),
                "content_sha256": payload["content_sha256"],
                "exact_contexts": payload["exact_context_count"],
                "factorization": [
                    {
                        "level": row["quotient_level"],
                        "noncongruent": row["noncongruent_fiber_count"],
                        "minimal_boundaries": row[
                            "minimal_uniform_boundary_level_counts"
                        ],
                    }
                    for row in payload["composition_failure_factorization"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
