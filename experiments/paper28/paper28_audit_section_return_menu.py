#!/usr/bin/env python3
"""Audit a future-free section-to-base generator menu on the n=7 seed scope.

Only the 35 released extremal rank-four seed contexts are menu sources.  The
menu is constructed from future-free interaction skeletons, their accounting
refinements, and exact lifted generator paths.  Membership in the exact
low-rank base is evaluated only after the menu payload has been frozen.

Replay-certified operation boundaries are allowed inside exact lifts.  They
are never promoted to recursive checkpoint sources or targets by this audit.
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

from paper28_factor_boundary_generators import _factor_receipt
from paper28_mechanism_schema import quotient_key, validate_receipt

AUDIT_SCHEMA = "paper28-section-return-menu-audit-v1"
RECEIPT_SCHEMA = "paper28-section-return-menu-audit-receipt-v1"
CATALOG_SCHEMA = "paper28-seed-mechanism-catalog-v1"
FACTOR_SCHEMA = "paper28-boundary-generator-factorization-v1"

HERE = Path(__file__).resolve().parent
DEFAULT_CATALOG = HERE / "results" / "paper28_seed_mechanism_catalog_v1.json.gz"
DEFAULT_FACTORIZATION = (
    HERE / "results" / "paper28_boundary_generator_factorization_v1.json.gz"
)
DEFAULT_OUTPUT = HERE / "results" / "paper28_section_return_menu_audit_v1.json.gz"
SOURCE_CLOSURE = (
    "paper28_audit_section_return_menu.py",
    "paper28_factor_boundary_generators.py",
    "paper28_mechanism_schema.py",
    "section_return_core.py",
    "mass_maturity_legacy.py",
    "validation/validate_paper28_section_return_menu.py",
)

FORBIDDEN_MENU_FIELDS = (
    "target_in_exact_P_le3",
    "winning",
    "bellman",
    "reset_coaccessibility",
    "successful_exact_lift",
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


def _load(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.name.endswith(".json.gz"):
        data = gzip.decompress(data)
    return json.loads(data.decode("ascii"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical_bytes(payload)
    if path.name.endswith(".json.gz"):
        path.write_bytes(gzip.compress(encoded, mtime=0))
    else:
        path.write_bytes(encoded)


def default_receipt_path(output: Path) -> Path:
    name = output.name.removesuffix(".json.gz")
    return output.with_name(f"{name}.receipt.json")


def _semantic_id(value: str) -> str:
    if "-" not in value:
        raise AssertionError(f"typed id lacks namespace: {value}")
    return value.split("-", 1)[1]


def _source_context(record: Mapping[str, Any]) -> dict[str, Any]:
    exact = record["exact"]
    target = exact["target_context"]
    body = {
        "ambient_n": int(target["ambient_n"]),
        "defect": [int(value) for value in target["defect"]],
        "packets": exact["corridor_boundaries"][0]["source"],
        "distinguished_packet": [
            int(value)
            for value in exact["ancestry_update"]["incoming_distinguished_packet"]
        ],
    }
    expected = f"ctx-{_digest(body)[:24]}"
    context_id = str(exact["source_context_id"])
    if context_id != expected:
        raise AssertionError("source context id does not match exact typed payload")
    return {"context_id": context_id, **body}


def _accounting_key(record: Mapping[str, Any]) -> str:
    return _digest(
        {"skeleton": record["skeleton"], "accounting": record["accounting"]}
    )


def _factorization_summary(factorization: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "receipt_id": str(factorization["receipt_id"]),
        "source_state_id": str(factorization["source_state_id"]),
        "target_state_id": str(factorization["target_state_id"]),
        "operation_count": len(factorization["operation_occurrences"]),
        "operation_kind_path": list(factorization["operation_kind_path"]),
        "operation_occurrence_ids_sha256": _digest(
            [
                operation["occurrence_id"]
                for operation in factorization["operation_occurrences"]
            ]
        ),
        "total_length": int(factorization["total_length"]),
        "total_surplus": int(factorization["total_surplus"]),
        "historical_features": factorization["historical_features"],
    }


def _build_future_free_menu(
    records: Sequence[Mapping[str, Any]],
    stored_factorizations: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_source: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    local_semantic_ids: set[str] = set()
    receipt_endpoint_semantic_ids: set[str] = set()
    factor_summaries: dict[str, dict[str, Any]] = {}

    for record in records:
        validate_receipt(record)
        receipt_id = str(record["receipt_id"])
        factorization = _factor_receipt(record)
        summary = _factorization_summary(factorization)
        if summary != stored_factorizations.get(receipt_id):
            raise AssertionError(f"factorization artifact drift for {receipt_id}")
        factor_summaries[receipt_id] = summary
        receipt_endpoint_semantic_ids.add(_semantic_id(summary["source_state_id"]))
        receipt_endpoint_semantic_ids.add(_semantic_id(summary["target_state_id"]))
        for operation in factorization["operation_occurrences"]:
            local_semantic_ids.add(
                _semantic_id(str(operation["exact_source"]["state_id"]))
            )
            local_semantic_ids.add(
                _semantic_id(str(operation["exact_target"]["state_id"]))
            )
        by_source[str(record["exact"]["source_context_id"])].append(record)

    context_rows: list[dict[str, Any]] = []
    menu_size_histogram: Counter[int] = Counter()
    total_accounting_refinements = 0
    all_menu_receipt_ids: set[str] = set()

    for source_context_id, source_records in sorted(by_source.items()):
        contexts = [_source_context(record) for record in source_records]
        if any(context != contexts[0] for context in contexts[1:]):
            raise AssertionError("one source id has multiple exact typed contexts")
        if len(contexts[0]["packets"]) != 4:
            raise AssertionError("declared n=7 menu source is not rank four")

        channels: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in source_records:
            channel_id = _digest(record["skeleton"])
            channels[channel_id].append(record)

        channel_rows: list[dict[str, Any]] = []
        for channel_key, channel_records in sorted(channels.items()):
            representative = channel_records[0]
            if any(record["skeleton"] != representative["skeleton"] for record in channel_records):
                raise AssertionError("skeleton channel is not constant")
            accounting_fibers: dict[str, list[str]] = defaultdict(list)
            operation_paths: set[tuple[str, ...]] = set()
            exact_lift_ids: list[str] = []
            for record in channel_records:
                receipt_id = str(record["receipt_id"])
                exact_lift_ids.append(receipt_id)
                all_menu_receipt_ids.add(receipt_id)
                accounting_fibers[_accounting_key(record)].append(receipt_id)
                operation_paths.add(
                    tuple(factor_summaries[receipt_id]["operation_kind_path"])
                )
            accounting_rows = [
                {
                    "accounting_id": f"acct-{key[:24]}",
                    "exact_lift_count": len(receipt_ids),
                    "exact_lift_ids_sha256": _digest(sorted(receipt_ids)),
                }
                for key, receipt_ids in sorted(accounting_fibers.items())
            ]
            total_accounting_refinements += len(accounting_rows)
            channel_rows.append(
                {
                    "channel_id": f"menu-{channel_key[:24]}",
                    "abstract_generator_path_schema": representative["skeleton"],
                    "accounting_refinements": accounting_rows,
                    "operation_path_profile_count": len(operation_paths),
                    "operation_path_profiles_sha256": _digest(
                        sorted(list(path) for path in operation_paths)
                    ),
                    "exact_lift_count": len(exact_lift_ids),
                    "exact_lift_ids": sorted(exact_lift_ids),
                }
            )
        menu_size_histogram[len(channel_rows)] += 1
        context_rows.append(
            {
                "source_context": contexts[0],
                "menu_size": len(channel_rows),
                "channels": channel_rows,
            }
        )

    menu = {
        "construction": {
            "source_scope": "released_n7_extremal_35_section_contexts",
            "channel_key": "future_free_interaction_skeleton",
            "accounting_refinement": "future_free_accounting_relation",
            "exact_lift": "all_tied_endpoint_shortest_admissible_receipts",
            "forbidden_inputs": list(FORBIDDEN_MENU_FIELDS),
        },
        "context_count": len(context_rows),
        "channel_count": sum(row["menu_size"] for row in context_rows),
        "accounting_refinement_count": total_accounting_refinements,
        "exact_lift_count": len(all_menu_receipt_ids),
        "max_menu_size": max(row["menu_size"] for row in context_rows),
        "menu_size_histogram": {
            str(size): count for size, count in sorted(menu_size_histogram.items())
        },
        "contexts": context_rows,
    }
    encoded_menu = json.dumps(
        menu["contexts"], sort_keys=True, separators=(",", ":")
    )
    for forbidden in FORBIDDEN_MENU_FIELDS:
        if forbidden in encoded_menu:
            raise AssertionError(f"future-free menu contains forbidden field: {forbidden}")

    replay_boundary = {
        "replay_certified_local_state_count": len(local_semantic_ids),
        "receipt_endpoint_state_count": len(receipt_endpoint_semantic_ids),
        "internal_only_state_count": len(
            local_semantic_ids - receipt_endpoint_semantic_ids
        ),
        "internal_only_state_ids_sha256": _digest(
            sorted(local_semantic_ids - receipt_endpoint_semantic_ids)
        ),
    }
    return menu, replay_boundary


def _certify_success(
    menu: Mapping[str, Any], records: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    by_id = {str(record["receipt_id"]): record for record in records}
    context_rows: list[dict[str, Any]] = []
    successful_receipt_ids: set[str] = set()
    successful_target_ids: set[str] = set()
    successful_channel_count = 0
    failed_channel_count = 0

    for context in menu["contexts"]:
        channel_rows: list[dict[str, Any]] = []
        for channel in context["channels"]:
            success_ids = sorted(
                receipt_id
                for receipt_id in channel["exact_lift_ids"]
                if bool(by_id[receipt_id]["observables"]["target_in_exact_P_le3"])
            )
            target_ids = sorted(
                {
                    str(by_id[receipt_id]["exact"]["target_context"]["context_id"])
                    for receipt_id in success_ids
                }
            )
            target_ranks = sorted(
                {
                    int(by_id[receipt_id]["skeleton"]["target_rank"])
                    for receipt_id in success_ids
                }
            )
            if any(rank not in (2, 3) for rank in target_ranks):
                raise AssertionError("successful recursive target is outside P<=3 rank")
            successful_receipt_ids.update(success_ids)
            successful_target_ids.update(target_ids)
            if success_ids:
                successful_channel_count += 1
            else:
                failed_channel_count += 1
            channel_rows.append(
                {
                    "channel_id": channel["channel_id"],
                    "has_successful_exact_lift": bool(success_ids),
                    "successful_exact_lift_count": len(success_ids),
                    "successful_exact_lift_ids": success_ids,
                    "certified_target_context_ids": target_ids,
                    "certified_target_ranks": target_ranks,
                }
            )
        successful_channels = sum(
            row["has_successful_exact_lift"] for row in channel_rows
        )
        if successful_channels == 0:
            raise AssertionError("declared section source has no successful menu channel")
        context_rows.append(
            {
                "source_context_id": context["source_context"]["context_id"],
                "menu_size": context["menu_size"],
                "successful_channel_count": successful_channels,
                "channels": channel_rows,
            }
        )

    return {
        "evaluator": "target_in_exact_P_le3",
        "evaluator_used_during_menu_generation": False,
        "all_declared_sources_have_successful_channel": True,
        "successful_channel_count": successful_channel_count,
        "failed_channel_count": failed_channel_count,
        "successful_exact_lift_count": len(successful_receipt_ids),
        "failed_exact_lift_count": int(menu["exact_lift_count"])
        - len(successful_receipt_ids),
        "certified_target_context_count": len(successful_target_ids),
        "contexts": context_rows,
    }


def build_audit(
    catalog_path: Path = DEFAULT_CATALOG,
    factorization_path: Path = DEFAULT_FACTORIZATION,
) -> dict[str, Any]:
    catalog = _load(catalog_path)
    factorization = _load(factorization_path)
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ValueError("unexpected seed catalog schema")
    if factorization.get("schema") != FACTOR_SCHEMA:
        raise ValueError("unexpected generator factorization schema")

    records = [
        record
        for record in catalog["receipts"]
        if record["seed_surface"] == "N7_EXTREMAL_35_CARRIER"
        and record["relation_role"] == "SEED"
    ]
    stored_factorizations = {
        str(row["receipt_id"]): row
        for row in factorization["receipt_factorizations"]
    }
    menu, replay_boundary = _build_future_free_menu(records, stored_factorizations)
    menu_content_sha256 = _digest(menu)
    certification = _certify_success(menu, records)
    if menu_content_sha256 != _digest(menu):
        raise AssertionError("success certification mutated the future-free menu")

    declared_source_ids = {
        str(row["source_context"]["context_id"]) for row in menu["contexts"]
    }
    certified_target_ids = {
        target_id
        for context in certification["contexts"]
        for channel in context["channels"]
        for target_id in channel["certified_target_context_ids"]
    }
    if len(declared_source_ids) != 35:
        raise AssertionError("menu source set is not the declared 35-context section")
    if any(not value.startswith("ctx-") for value in certified_target_ids):
        raise AssertionError("internal generator state promoted to recursive target")

    result: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "inputs": {
            "catalog": {
                "name": catalog_path.name,
                "sha256": _sha256(catalog_path),
                "content_sha256": catalog["content_sha256"],
            },
            "generator_factorization": {
                "name": factorization_path.name,
                "sha256": _sha256(factorization_path),
                "content_sha256": factorization["content_sha256"],
            },
        },
        "scope": {
            "ambient_n": 7,
            "source_rank": 4,
            "declared_section_context_count": len(declared_source_ids),
            "no_new_context_or_exit_enumeration": True,
            "target": "exact_P_le3_base",
        },
        "future_free_menu_content_sha256": menu_content_sha256,
        "future_free_menu": menu,
        "success_certification": certification,
        "internal_boundary_exclusion": {
            **replay_boundary,
            "menu_source_not_in_declared_section_count": 0,
            "recursive_target_not_in_certified_base_count": 0,
            "internal_only_boundary_exported_as_checkpoint_count": 0,
            "menu_sources_are_only_declared_section_contexts": True,
            "recursive_targets_are_only_certified_low_rank_contexts": True,
        },
        "claim_boundary": {
            "proved": (
                "Every declared n=7 extremal rank-four section source has a "
                "future-free finite skeleton menu with an exact lifted path to "
                "the certified P<=3 base."
            ),
            "not_claimed": [
                "every menu channel succeeds",
                "all 15120 inherited section contexts are covered",
                "section-to-section return above rank four",
                "all-rank menu construction",
                "B1 or B2 boundedness",
            ],
        },
    }
    result["content_sha256"] = _digest(result)
    return result


def build_receipt(
    *,
    output: Path,
    payload: Mapping[str, Any],
    catalog_path: Path,
    factorization_path: Path,
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
        "verification_mode": "FULL_RECOMPUTATION_FROM_BOUND_CANONICAL_ARTIFACTS",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
        },
        "inputs": payload["inputs"],
        "source_closure": closure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--factorization", type=Path, default=DEFAULT_FACTORIZATION
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_audit(args.catalog, args.factorization)
    _write(args.output, payload)
    receipt_path = args.receipt or default_receipt_path(args.output)
    receipt = build_receipt(
        output=args.output,
        payload=payload,
        catalog_path=args.catalog,
        factorization_path=args.factorization,
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": args.output.as_posix(),
                "receipt": receipt_path.as_posix(),
                "content_sha256": payload["content_sha256"],
                "menu": {
                    key: payload["future_free_menu"][key]
                    for key in (
                        "context_count",
                        "channel_count",
                        "accounting_refinement_count",
                        "exact_lift_count",
                        "max_menu_size",
                    )
                },
                "certification": {
                    key: payload["success_certification"][key]
                    for key in (
                        "successful_channel_count",
                        "failed_channel_count",
                        "successful_exact_lift_count",
                        "failed_exact_lift_count",
                        "certified_target_context_count",
                    )
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
