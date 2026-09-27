#!/usr/bin/env python3
"""Freeze the extremal rank-four menu/exact-lift relation without Good_4.

The historical extremal audit stored its future-free menu and the later
membership evaluation in one artifact.  This adapter independently projects
the same complete source-addressed relation from the bound seed catalog,
removes every outcome observable, and freezes a construction digest for C3.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from paper28_audit_section_return_menu import (
    CATALOG_SCHEMA,
    FACTOR_SCHEMA,
    _build_future_free_menu,
)

SCHEMA = "paper28-ext-rank4-section-candidate-v1"
RECEIPT_SCHEMA = "paper28-ext-rank4-section-candidate-receipt-v1"
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DEFAULT_CATALOG = RESULTS / "paper28_seed_mechanism_catalog_v1.json.gz"
DEFAULT_FACTORIZATION = (
    RESULTS / "paper28_boundary_generator_factorization_v1.json.gz"
)
DEFAULT_OUTPUT = RESULTS / "paper28_ext_rank4_section_candidate_v1.json.gz"

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


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(_canonical_bytes(payload), mtime=0))


def default_receipt_path(path: Path) -> Path:
    return path.with_name(
        f"{path.name.removesuffix('.json.gz')}.receipt.json"
    )


def _verify_content_digest(payload: Mapping[str, Any], label: str) -> None:
    candidate = dict(payload)
    stored = str(candidate.pop("content_sha256"))
    if _digest(candidate) != stored:
        raise AssertionError(f"{label} content digest mismatch")


def _input_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": path.name,
        "schema": payload["schema"],
        "sha256": _sha256(path),
        "content_sha256": payload["content_sha256"],
    }


def _strip_outcome_observables(record: Mapping[str, Any]) -> dict[str, Any]:
    """Project only theorem-facing construction fields from a seed receipt."""

    return {
        key: record[key]
        for key in (
            "schema",
            "receipt_id",
            "seed_surface",
            "relation_role",
            "origin",
            "skeleton",
            "accounting",
            "exact",
        )
    }


def build_payload(
    *, catalog_path: Path, factorization_path: Path
) -> dict[str, Any]:
    catalog = _load(catalog_path)
    factorization = _load(factorization_path)
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise AssertionError("unexpected seed catalog schema")
    if factorization.get("schema") != FACTOR_SCHEMA:
        raise AssertionError("unexpected factorization schema")
    _verify_content_digest(catalog, "seed catalog")
    _verify_content_digest(factorization, "factorization")

    source_records = [
        row
        for row in catalog["receipts"]
        if row["seed_surface"] == "N7_EXTREMAL_35_CARRIER"
        and row["relation_role"] == "SEED"
    ]
    stored_factorizations = {
        str(row["receipt_id"]): row
        for row in factorization["receipt_factorizations"]
    }
    menus, replay_boundary = _build_future_free_menu(
        source_records, stored_factorizations
    )
    receipts = sorted(
        (_strip_outcome_observables(row) for row in source_records),
        key=lambda row: str(row["receipt_id"]),
    )
    receipt_ids = {str(row["receipt_id"]) for row in receipts}
    menu_ids = {
        str(receipt_id)
        for context in menus["contexts"]
        for channel in context["channels"]
        for receipt_id in channel["exact_lift_ids"]
    }
    if receipt_ids != menu_ids:
        raise AssertionError("ext menu and projected exact relation disagree")
    if len(receipt_ids) != len(receipts):
        raise AssertionError("ext projected receipt ids are not unique")

    contexts = menus["contexts"]
    construction = {
        "source_carrier": {
            "name": "C_4,ext^(7)",
            "recursive_authority": "NONE_IN_THIS_PRE_EVALUATION_ADAPTER",
            "context_count": len(contexts),
            "context_ids": sorted(
                str(row["source_context"]["context_id"]) for row in contexts
            ),
        },
        "menus": menus,
        "exact_lifts": {
            "definition": (
                "complete source-addressed extremal rank-four seed receipts "
                "with all outcome observables removed"
            ),
            "receipt_count": len(receipts),
            "receipts": receipts,
        },
        "checkpoint_type_audit": {
            "menu_source_context_count": len(contexts),
            "exported_recursive_target_count": 0,
            **replay_boundary,
            "internal_only_exported_as_checkpoint": 0,
        },
    }
    encoded_core = json.dumps(
        {
            "menu_contexts": menus["contexts"],
            "exact_receipts": receipts,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    for field in FORBIDDEN_CONSTRUCTION_FIELDS:
        if field in encoded_core:
            raise AssertionError(
                f"future-success field leaked into ext construction: {field}"
            )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "scope": {
            "ambient_n": 7,
            "source_rank": 4,
            "source": "35-context extremal pre-evaluation adapter",
            "evaluation_status": "NOT_RUN",
            "section_authority_status": "NOT_ASSERTED_BY_THIS_ADAPTER",
            "source_projection": (
                "field-whitelisted projection; catalog observables are never "
                "read into the construction"
            ),
        },
        "phase_order": [
            "load_bound_seed_and_factorization_artifacts",
            "select_extremal_seed_receipts_without_reading_outcomes",
            "construct_future_free_menu",
            "strip_all_observables_from_exact_relation",
            "freeze_construction_payload_and_digest",
            "low_rank_evaluator_absent",
        ],
        "inputs": {
            "catalog": _input_record(catalog_path, catalog),
            "factorization": _input_record(
                factorization_path, factorization
            ),
        },
        "construction": construction,
        "evaluator": {
            "status": "ABSENT_BY_DESIGN",
            "good_predicate_defined_for_later_phase": (
                "Good_4(C,m) iff an exact lift in Lift_4(C,m) has target "
                "in exact P_<=3^(7)"
            ),
            "evaluated_source_count": 0,
            "evaluated_channel_count": 0,
        },
    }
    payload["construction_payload_sha256"] = _digest(construction)
    payload["content_sha256"] = _digest(payload)
    return payload


def build_receipt(
    *, output: Path, payload: Mapping[str, Any], input_paths: list[Path]
) -> dict[str, Any]:
    source_paths = [
        Path(__file__).resolve(),
        HERE / "paper28_audit_section_return_menu.py",
        HERE / "paper28_factor_boundary_generators.py",
        HERE / "paper28_mechanism_schema.py",
        HERE / "validation" / "validate_paper28_ext_rank4_section_candidate.py",
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "verification_mode": "FULL_SUCCESS_FREE_PROJECTION_REPLAY",
        "artifact": {
            "name": output.name,
            "sha256": _sha256(output),
            "content_sha256": payload["content_sha256"],
            "construction_payload_sha256": payload[
                "construction_payload_sha256"
            ],
        },
        "inputs": [
            {"name": path.name, "sha256": _sha256(path)}
            for path in input_paths
        ],
        "source_closure": [
            {
                "name": path.relative_to(HERE).as_posix(),
                "sha256": _sha256(path),
            }
            for path in source_paths
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--factorization", type=Path, default=DEFAULT_FACTORIZATION
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = build_payload(
        catalog_path=args.catalog, factorization_path=args.factorization
    )
    _write(args.out, payload)
    receipt_path = args.receipt or default_receipt_path(args.out)
    receipt = build_receipt(
        output=args.out,
        payload=payload,
        input_paths=[args.catalog, args.factorization],
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="ascii",
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
                "exact_lifts": menus["exact_lift_count"],
                "max_menu_size": menus["max_menu_size"],
                "good_4_evaluation": "NOT_RUN",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
