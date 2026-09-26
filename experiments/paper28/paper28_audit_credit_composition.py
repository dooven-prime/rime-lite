#!/usr/bin/env python3
"""Audit the Paper XXVIII exact-lift credit composition law.

The audit consumes the canonical ``4+35`` exact-receipt catalog.  It proves
credit identities only along exact typed arrows and exact compatible pairs.
Accounting and interaction-skeleton labels are then tested as edge-label
quotients of the resulting numerical composition data.  No abstract label
pair is declared composable without at least one exact compatible lift.
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

from mass_maturity_legacy import simplified_deadline
from paper28_mechanism_schema import freeze_json, quotient_key, validate_receipt

AUDIT_SCHEMA = "paper28-credit-composition-audit-v1"
RECEIPT_SCHEMA = "paper28-credit-composition-audit-receipt-v1"
CATALOG_SCHEMA = "paper28-seed-mechanism-catalog-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "results" / "paper28_seed_mechanism_catalog_v1.json.gz"
DEFAULT_OUTPUT = HERE / "results" / "paper28_credit_composition_audit_v1.json"
SOURCE_CLOSURE = (
    "paper28_audit_credit_composition.py",
    "paper28_mechanism_schema.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_credit_composition_audit.py",
)

QuotientLevel = Literal["accounting", "skeleton"]

COMPOSITE_OBSERVABLES = (
    "allocation_vector",
    "composite_accounting_summary",
    "composite_debt_profile",
    "gross_credit_vector",
    "length_vector",
    "partition_chain",
    "peak_composite_debt",
    "surplus_vector",
    "tail_budget_vector",
    "total_length",
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


def _mass_from_packet_rows(
    rows: Sequence[Mapping[str, Any]], ambient_n: int
) -> tuple[int, ...]:
    mass = [0] * ambient_n
    for row in rows:
        coordinate = int(row["coordinate"])
        if mass[coordinate] != 0:
            raise AssertionError(f"duplicate packet coordinate: {coordinate}")
        packet_mass = int(row["mass"])
        if packet_mass != len(row["packet"]):
            raise AssertionError("packet mass and packet identity disagree")
        mass[coordinate] = packet_mass
    if sum(mass) != ambient_n:
        raise AssertionError("packet placement does not have ambient mass")
    return tuple(mass)


def _debt_profile(surpluses: Sequence[int]) -> list[int]:
    total = 0
    result = [0]
    for surplus in surpluses:
        total += int(surplus)
        result.append(max(0, -total))
    return result


def _partition(mass: Sequence[int]) -> list[int]:
    return sorted((int(value) for value in mass if value), reverse=True)


def _budget_to_reset(mass: tuple[int, ...]) -> int:
    ambient_n = len(mass)
    reset = (ambient_n,) + (0,) * (ambient_n - 1)
    return simplified_deadline(reset, ambient_n) - simplified_deadline(
        mass, ambient_n
    )


def _receipt_credit(record: Mapping[str, Any]) -> dict[str, Any]:
    validate_receipt(record)
    skeleton = record["skeleton"]
    accounting = record["accounting"]
    exact = record["exact"]
    ambient_n = int(skeleton["ambient_n"])
    boundaries = exact["corridor_boundaries"]
    corridors = accounting["corridors"]

    corridor_rows: list[dict[str, Any]] = []
    previous_target: tuple[int, ...] | None = None
    for index, (boundary, corridor) in enumerate(
        zip(boundaries, corridors, strict=True)
    ):
        source_mass = _mass_from_packet_rows(boundary["source"], ambient_n)
        target_mass = _mass_from_packet_rows(boundary["target"], ambient_n)
        if previous_target is not None and source_mass != previous_target:
            raise AssertionError("corridor boundary mass is not continuous")
        source_tau = simplified_deadline(source_mass, ambient_n)
        target_tau = simplified_deadline(target_mass, ambient_n)
        length = int(corridor["length"])
        surplus = int(corridor["surplus"])
        maturity_gain = target_tau - source_tau
        if maturity_gain != length + surplus:
            raise AssertionError("corridor maturity telescope failed")
        corridor_rows.append(
            {
                "index": index,
                "source_mass": list(source_mass),
                "target_mass": list(target_mass),
                "source_tau": source_tau,
                "target_tau": target_tau,
                "maturity_gain": maturity_gain,
                "length": length,
                "surplus": surplus,
            }
        )
        previous_target = target_mass

    source_mass = tuple(corridor_rows[0]["source_mass"])
    target_mass = tuple(corridor_rows[-1]["target_mass"])
    exact_target = tuple(int(value) for value in exact["target_endpoint"])
    if target_mass != exact_target:
        raise AssertionError("corridor target does not match exact target endpoint")
    if _partition(source_mass) != list(skeleton["source_partition"]):
        raise AssertionError("source partition drift")
    if _partition(target_mass) != list(skeleton["target_partition"]):
        raise AssertionError("target partition drift")

    source_tau = simplified_deadline(source_mass, ambient_n)
    target_tau = simplified_deadline(target_mass, ambient_n)
    total_length = sum(row["length"] for row in corridor_rows)
    surpluses = [row["surplus"] for row in corridor_rows]
    total_surplus = sum(surpluses)
    maturity_gain = target_tau - source_tau
    target_budget = _budget_to_reset(target_mass)
    source_budget = _budget_to_reset(source_mass)
    if maturity_gain != total_length + total_surplus:
        raise AssertionError("receipt maturity telescope failed")
    if int(accounting["residual_tail_budget"]) != target_budget:
        raise AssertionError("stored residual tail budget drift")
    if list(accounting["debt_profile"]) != _debt_profile(surpluses):
        raise AssertionError("stored debt profile drift")
    if source_budget != total_length + total_surplus + target_budget:
        raise AssertionError("receipt credit allocation failed")

    return {
        "receipt_id": str(record["receipt_id"]),
        "ambient_n": ambient_n,
        "source_context_id": str(exact["source_context_id"]),
        "target_context_id": str(exact["target_context"]["context_id"]),
        "source_mass": list(source_mass),
        "target_mass": list(target_mass),
        "source_partition": list(skeleton["source_partition"]),
        "target_partition": list(skeleton["target_partition"]),
        "source_tau": source_tau,
        "target_tau": target_tau,
        "reset_tau": simplified_deadline(
            (ambient_n,) + (0,) * (ambient_n - 1), ambient_n
        ),
        "source_budget": source_budget,
        "target_budget": target_budget,
        "total_length": total_length,
        "total_surplus": total_surplus,
        "maturity_gain": maturity_gain,
        "debt_profile": _debt_profile(surpluses),
        "corridors": corridor_rows,
    }


def _composite_credit(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, Any]:
    if left["target_context_id"] != right["source_context_id"]:
        raise AssertionError("credit composition lacks an exact typed lift")
    if left["ambient_n"] != right["ambient_n"]:
        raise AssertionError("ambient size changes across exact composition")
    if left["target_mass"] != right["source_mass"]:
        raise AssertionError("typed context equality failed to preserve mass")
    if left["target_budget"] != right["source_budget"]:
        raise AssertionError("middle boundary budget mismatch")

    surplus_sequence = [
        int(row["surplus"])
        for row in [*left["corridors"], *right["corridors"]]
    ]
    total_length = int(left["total_length"]) + int(right["total_length"])
    total_surplus = int(left["total_surplus"]) + int(right["total_surplus"])
    gross_first = int(left["maturity_gain"])
    gross_second = int(right["maturity_gain"])
    gross_total = int(right["target_tau"]) - int(left["source_tau"])
    source_budget = int(left["source_budget"])
    middle_budget = int(left["target_budget"])
    target_budget = int(right["target_budget"])

    if gross_total != gross_first + gross_second:
        raise AssertionError("gross maturity credit is not additive")
    if total_surplus != int(left["total_surplus"]) + int(right["total_surplus"]):
        raise AssertionError("surplus is not additive")
    if middle_budget != int(right["total_length"]) + int(
        right["total_surplus"]
    ) + target_budget:
        raise AssertionError("successor credit transfer failed")
    if source_budget != total_length + total_surplus + target_budget:
        raise AssertionError("composite credit allocation failed")

    debt_profile = _debt_profile(surplus_sequence)
    partition_chain = [
        list(left["source_partition"]),
        list(left["target_partition"]),
        list(right["target_partition"]),
    ]
    gross_credit_vector = [gross_first, gross_second, gross_total]
    length_vector = [
        int(left["total_length"]),
        int(right["total_length"]),
        total_length,
    ]
    surplus_vector = [
        int(left["total_surplus"]),
        int(right["total_surplus"]),
        total_surplus,
    ]
    tail_budget_vector = [source_budget, middle_budget, target_budget]
    allocation_vector = [total_length, total_surplus, target_budget]
    summary = {
        "ambient_n": int(left["ambient_n"]),
        "partition_chain": partition_chain,
        "gross_credit_vector": gross_credit_vector,
        "length_vector": length_vector,
        "surplus_vector": surplus_vector,
        "tail_budget_vector": tail_budget_vector,
        "allocation_vector": allocation_vector,
        "composite_debt_profile": debt_profile,
        "peak_composite_debt": max(debt_profile),
        "total_length": total_length,
        "total_surplus": total_surplus,
    }
    return {
        **summary,
        "composite_accounting_summary": summary,
    }


def _edge_label_pair_key(
    left: Mapping[str, Any], right: Mapping[str, Any], level: QuotientLevel
) -> Any:
    return freeze_json(
        {
            "first": quotient_key(left, level),
            "second": quotient_key(right, level),
        }
    )


def _pair_observable_audit(
    edge_rows: Sequence[Mapping[str, Any]], level: QuotientLevel
) -> dict[str, Any]:
    fibers: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for row in edge_rows:
        fibers[row[f"{level}_pair_key"]].append(row)

    observable_rows: list[dict[str, Any]] = []
    for observable in COMPOSITE_OBSERVABLES:
        hostile: list[dict[str, Any]] = []
        for pair_key, rows in sorted(fibers.items(), key=lambda item: _digest(item[0])):
            values: dict[Any, Mapping[str, Any]] = {}
            for row in rows:
                value_key = freeze_json(row["composite"][observable])
                values.setdefault(value_key, row)
            if len(values) <= 1:
                continue
            witnesses = sorted(values.values(), key=lambda row: row["edge_id"])
            hostile.append(
                {
                    "label_pair_sha256": _digest(pair_key),
                    "left_edge_id": witnesses[0]["edge_id"],
                    "right_edge_id": witnesses[1]["edge_id"],
                    "left_value": witnesses[0]["composite"][observable],
                    "right_value": witnesses[1]["composite"][observable],
                }
            )
        observable_rows.append(
            {
                "observable": observable,
                "descends": not hostile,
                "nonconstant_label_pair_count": len(hostile),
                "hostile_examples": hostile[:12],
            }
        )

    lift_counts = [len(rows) for rows in fibers.values()]
    return {
        "quotient_level": level,
        "exact_lift_count": len(edge_rows),
        "lifted_label_pair_count": len(fibers),
        "label_pairs_with_multiple_exact_lifts": sum(
            count > 1 for count in lift_counts
        ),
        "max_exact_lifts_for_one_label_pair": max(lift_counts),
        "exact_lift_count_distribution": {
            str(value): count
            for value, count in sorted(Counter(lift_counts).items())
        },
        "observable_audit": observable_rows,
    }


def _accounting_composition_relation(
    edge_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    fibers: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for row in edge_rows:
        fibers[row["accounting_pair_key"]].append(row)

    relation: list[dict[str, Any]] = []
    for pair_key, rows in sorted(fibers.items(), key=lambda item: _digest(item[0])):
        summaries = {
            freeze_json(row["composite"]["composite_accounting_summary"])
            for row in rows
        }
        if len(summaries) != 1:
            raise AssertionError("accounting label pair has two credit summaries")
        first = min(rows, key=lambda row: row["edge_id"])
        relation.append(
            {
                "accounting_label_pair_sha256": _digest(pair_key),
                "exact_lift_count": len(rows),
                "distinct_middle_context_count": len(
                    {row["middle_context_id"] for row in rows}
                ),
                "composite_accounting_summary": first["composite"][
                    "composite_accounting_summary"
                ],
                "witness_edge_id": first["edge_id"],
            }
        )
    return relation


def _histogram(values: Sequence[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(int(value) for value in values).items())
    }


def _credit_reallocation(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    candidates = [
        row
        for row in rows
        if row["relation_role"] == "SEED"
        and int(row["skeleton"]["ambient_n"]) == 7
        and list(row["skeleton"]["source_partition"]) == [2, 2, 2, 1]
    ]
    channels = {}
    for name, target_partition, length, expected_count in (
        ("heavy_comb_6_1", [6, 1], 20, 1020),
        ("fallback_5_2", [5, 2], 12, 87),
    ):
        matches = [
            row
            for row in candidates
            if list(row["skeleton"]["target_partition"]) == target_partition
            and sum(
                int(corridor["length"])
                for corridor in row["accounting"]["corridors"]
            )
            == length
            and sum(
                int(corridor["surplus"])
                for corridor in row["accounting"]["corridors"]
            )
            == 0
        ]
        if len(matches) != expected_count:
            raise AssertionError(f"credit-reallocation channel drift: {name}")
        target_mass = tuple(int(value) for value in matches[0]["exact"]["target_endpoint"])
        channels[name] = {
            "target_partition": target_partition,
            "zero_surplus_length": length,
            "tail_budget": _budget_to_reset(target_mass),
            "exact_realization_count": len(matches),
            "witness_receipt_id": min(str(row["receipt_id"]) for row in matches),
        }

    source_mass = (2, 2, 2, 1, 0, 0, 0)
    source_budget = _budget_to_reset(source_mass)
    if source_budget != 27:
        raise AssertionError("extremal source budget drift")
    if channels["heavy_comb_6_1"]["zero_surplus_length"] + channels[
        "heavy_comb_6_1"
    ]["tail_budget"] != source_budget:
        raise AssertionError("20+7 credit identity failed")
    if channels["fallback_5_2"]["zero_surplus_length"] + channels[
        "fallback_5_2"
    ]["tail_budget"] != source_budget:
        raise AssertionError("12+15 credit identity failed")
    return {
        "source_partition": [2, 2, 2, 1],
        "source_budget": source_budget,
        "channels": channels,
        "identity": "20 + 7 = 12 + 15 = 27",
    }


def build_audit(catalog: Mapping[str, Any], *, catalog_path: Path) -> dict[str, Any]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ValueError(f"unexpected catalog schema: {catalog.get('schema')!r}")
    records = list(catalog["receipts"])
    by_id: dict[str, Mapping[str, Any]] = {}
    credit_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        validate_receipt(record)
        receipt_id = str(record["receipt_id"])
        if receipt_id in by_id:
            raise AssertionError(f"duplicate receipt id: {receipt_id}")
        by_id[receipt_id] = record
        credit_by_id[receipt_id] = _receipt_credit(record)

    edge_rows: list[dict[str, Any]] = []
    for edge in catalog["compatibility_edges"]:
        left_id = str(edge["source_receipt_id"])
        right_id = str(edge["successor_receipt_id"])
        left = by_id[left_id]
        right = by_id[right_id]
        left_credit = credit_by_id[left_id]
        right_credit = credit_by_id[right_id]
        composite = _composite_credit(left_credit, right_credit)
        edge_rows.append(
            {
                "edge_id": f"{left_id}->{right_id}",
                "left_receipt_id": left_id,
                "right_receipt_id": right_id,
                "middle_context_id": left_credit["target_context_id"],
                "accounting_pair_key": _edge_label_pair_key(
                    left, right, "accounting"
                ),
                "skeleton_pair_key": _edge_label_pair_key(left, right, "skeleton"),
                "composite": composite,
            }
        )
    edge_rows.sort(key=lambda row: row["edge_id"])

    receipt_ledger = [credit_by_id[receipt_id] for receipt_id in sorted(credit_by_id)]
    composition_ledger = [
        {
            "edge_id": row["edge_id"],
            "middle_context_id": row["middle_context_id"],
            "composite": row["composite"],
        }
        for row in edge_rows
    ]
    pair_audits = [
        _pair_observable_audit(edge_rows, level)
        for level in ("accounting", "skeleton")
    ]
    accounting_relation = _accounting_composition_relation(edge_rows)

    unary_surpluses = [row["total_surplus"] for row in receipt_ledger]
    result: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "scope": {
            "construction": "credit projection of the canonical 4+35 exact relation",
            "new_state_census": False,
            "semantic_composition": "exact typed target/source context equality",
            "abstract_composition": "defined only for edge-label pairs with an exact compatible lift",
        },
        "input": {
            "path": catalog_path.relative_to(HERE.parents[1]).as_posix(),
            "sha256": _sha256(catalog_path),
            "content_sha256": catalog["content_sha256"],
            "exact_receipts": len(records),
            "compatibility_edges": len(edge_rows),
        },
        "exact_receipt_credit_theorem": {
            "receipt_count": len(receipt_ledger),
            "all_corridor_telescopes_hold": True,
            "all_receipt_telescopes_hold": True,
            "all_credit_allocations_hold": True,
            "identity": "B(source) = L + S + B(target)",
            "receipt_credit_ledger_sha256": _digest(receipt_ledger),
            "total_surplus_distribution": _histogram(unary_surpluses),
            "total_length_distribution": _histogram(
                [row["total_length"] for row in receipt_ledger]
            ),
        },
        "exact_lift_composition_theorem": {
            "exact_compatible_lift_count": len(edge_rows),
            "all_middle_boundary_budgets_match": True,
            "all_gross_credits_add": True,
            "all_surpluses_add": True,
            "all_composite_allocations_hold": True,
            "identities": [
                "B(middle) = L(second) + S(second) + B(final)",
                "S(composite) = S(first) + S(second)",
                "B(source) = L(total) + S(total) + B(final)",
            ],
            "composition_credit_ledger_sha256": _digest(composition_ledger),
        },
        "edge_label_pair_audits": pair_audits,
        "lifted_accounting_composition_relation": {
            "relation_semantics": "one row per accounting-label pair admitting at least one exact compatible lift",
            "label_pair_count": len(accounting_relation),
            "composite_summary_is_well_defined": True,
            "rows": accounting_relation,
        },
        "extremal_credit_reallocation": _credit_reallocation(records),
        "conclusions": {
            "classification_descent_is_not_semantic_composition_descent": True,
            "accounting_credit_composition_is_well_defined_given_exact_lift": True,
            "accounting_labels_do_not_assert_exact_lift_existence": True,
            "skeleton_labels_preserve_gross_credit_but_not_credit_allocation": True,
            "no_abstract_mechanism_algebra_claimed": True,
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
    payload = build_audit(_read_catalog(catalog_path), catalog_path=catalog_path)
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
                "receipts": payload["exact_receipt_credit_theorem"][
                    "receipt_count"
                ],
                "exact_lifts": payload["exact_lift_composition_theorem"][
                    "exact_compatible_lift_count"
                ],
                "label_pair_audits": [
                    {
                        "level": row["quotient_level"],
                        "lifted_pairs": row["lifted_label_pair_count"],
                        "observable_failures": {
                            observable["observable"]: observable[
                                "nonconstant_label_pair_count"
                            ]
                            for observable in row["observable_audit"]
                            if not observable["descends"]
                        },
                    }
                    for row in payload["edge_label_pair_audits"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
