#!/usr/bin/env python3
"""Append-only global predicate tally over the frozen MTS-1 pair shards."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from nontrivial_contrast_v1 import (
    PAIR_ROLES,
    PRIMARY_PREDICATE_ORDER,
    TRANSITIONS,
    cohort_specs_from_registry,
    evaluate_pair_predicates,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RESULT_ROOT = HERE / "results" / "mts1-v1"
INVENTORY = RESULT_ROOT / "inventory.json"
REGISTRY = HERE / "results" / "mechanism_cohort_registry.v1.json"
CLASSIFICATION = RESULT_ROOT / "validation" / "mechanism_classification.v1.json"
FREEZE = HERE / "results" / "mts1-v1.freeze-manifest.json"
RESULT = HERE / "results" / "mts1-v1.global-pair-tally.v1.json"
RECEIPT = HERE / "results" / "mts1-v1.global-pair-tally.v1.validation-receipt.json"
DECISIVE = (
    "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL",
    "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(REPO).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def audit() -> dict[str, Any]:
    freeze = load(FREEZE)
    frozen = {entry["path"]: entry for entry in freeze["artifact_closure"]}
    for path in (INVENTORY, CLASSIFICATION):
        actual = binding(path)
        entry = frozen[actual["path"]]
        require(actual["bytes"] == entry["bytes"], f"frozen size mismatch: {path}")
        require(actual["sha256"] == entry["sha256"], f"frozen digest mismatch: {path}")

    inventory = load(INVENTORY)
    registry = load(REGISTRY)
    specs = cohort_specs_from_registry(registry)
    classification = load(CLASSIFICATION)["classification"]
    require(classification["complete_finite_census"] is True, "incomplete frozen census")
    require(classification["record_count"] == 6975, "frozen record count mismatch")
    require(
        classification["primary_predicate_order"] == list(PRIMARY_PREDICATE_ORDER),
        "frozen predicate order mismatch",
    )
    expected_cells = {
        (cell["transition"], cell["transient_cohort_id"], cell["persistent_cohort_id"])
        for cell in classification["comparison_cells"]
    }
    require(len(expected_cells) == 15, "frozen comparison-cell count mismatch")
    covered = {
        role: set() for role in PAIR_ROLES
    }
    for transition, transient_id, persistent_id in expected_cells:
        require(transition in TRANSITIONS, "unknown comparison transition")
        covered["TRANSIENT_OBSTRUCTION"].add(transient_id)
        covered["PERSISTENT_SAFE"].add(persistent_id)

    shards = inventory["pair_shards"]
    require(len(shards) == len(specs) * len(TRANSITIONS), "pair-shard grid incomplete")
    require(
        {(entry["cohort_id"], entry["transition"]) for entry in shards}
        == {(cohort_id, transition) for cohort_id in specs for transition in TRANSITIONS},
        "pair-shard grid has duplicate or missing entries",
    )
    cohort_rows: list[dict[str, Any]] = []
    totals = {
        (transition, role): Counter()
        for transition in TRANSITIONS
        for role in PAIR_ROLES
    }
    for entry in sorted(shards, key=lambda item: (item["transition"], item["cohort_id"])):
        cohort_id = entry["cohort_id"]
        transition = entry["transition"]
        spec = specs[cohort_id]
        require(entry["record_count"] == spec["unordered_pair_count"], "shard count mismatch")
        relative = Path(entry["path"])
        require(relative.parts[:1] == ("pair-records",), "unexpected shard path")
        path = RESULT_ROOT / relative
        actual = binding(path)
        require(actual["bytes"] == entry["bytes"], f"shard size mismatch: {relative}")
        require(actual["sha256"] == entry["sha256"], f"shard digest mismatch: {relative}")
        expected_pairs = {tuple(pair) for pair in spec["unordered_pairs"]}
        observed_pairs: set[tuple[int, int]] = set()
        counts: Counter[str] = Counter()
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                require(record["cohort_id"] == cohort_id, "record cohort mismatch")
                require(record["pair_role"] == spec["pair_role"], "record role mismatch")
                require(record["transition"] == transition, "record transition mismatch")
                pair = (record["source_a"], record["source_b"])
                require(pair in expected_pairs, "unregistered pair")
                require(pair not in observed_pairs, "duplicate pair")
                observed_pairs.add(pair)
                predicates = evaluate_pair_predicates(record)
                counts.update(name for name in PRIMARY_PREDICATE_ORDER if predicates[name])
        require(observed_pairs == expected_pairs, f"incomplete pair membership: {cohort_id}")
        totals[(transition, spec["pair_role"])]["pair_count"] += len(observed_pairs)
        totals[(transition, spec["pair_role"])].update(counts)
        cohort_rows.append({
            "transition": transition,
            "cohort_id": cohort_id,
            "pair_role": spec["pair_role"],
            "initial_sector_label": spec["initial_sector_label"],
            "in_shared_stratum_cells": cohort_id in covered[spec["pair_role"]],
            "pair_count": len(observed_pairs),
            "true_counts": {name: counts[name] for name in PRIMARY_PREDICATE_ORDER},
        })

    global_rows: list[dict[str, Any]] = []
    for transition in TRANSITIONS:
        for role in PAIR_ROLES:
            counts = totals[(transition, role)]
            expected = sum(
                spec["unordered_pair_count"]
                for spec in specs.values()
                if spec["pair_role"] == role
            )
            require(counts["pair_count"] == expected, "global pair count mismatch")
            global_rows.append({
                "transition": transition,
                "pair_role": role,
                "pair_count": expected,
                "true_counts": {name: counts[name] for name in PRIMARY_PREDICATE_ORDER},
            })

    for transition in TRANSITIONS[1:]:
        transient = totals[(transition, "TRANSIENT_OBSTRUCTION")]
        persistent = totals[(transition, "PERSISTENT_SAFE")]
        for predicate in DECISIVE:
            require(transient[predicate] == 570, f"global transient separator fails: {transition}")
            require(persistent[predicate] == 0, f"global persistent separator fails: {transition}")
            require(
                {"transition": transition, "predicate": predicate,
                 "direction": "TRANSIENT_ALL__PERSISTENT_NONE"}
                in classification["exact_separators"],
                "global separator not present in frozen comparison cells",
            )

    return {
        "schema": "rime.paper17.mts1-global-pair-tally.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_EXACT_PAIR_SHARD_REPLAY",
        "independent_validation": False,
        "source_producer_replayed": False,
        "inputs": [binding(path) for path in (FREEZE, INVENTORY, REGISTRY, CLASSIFICATION)],
        "pair_shard_count": len(shards),
        "pair_transition_record_count": sum(row["pair_count"] for row in cohort_rows),
        "primary_predicate_order": list(PRIMARY_PREDICATE_ORDER),
        "cohort_counts": cohort_rows,
        "global_counts": global_rows,
        "global_post_separation_separator": True,
        "boundary": "Finite registered pair universe only; the later separator does not identify the initial trigger.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = audit()
    payload = canonical_bytes(result)
    if args.write_result:
        RESULT.write_bytes(payload)
    else:
        require(RESULT.read_bytes() == payload, "saved global tally differs from exact replay")
    receipt = {
        "schema": "rime.paper17.mts1-global-pair-tally-validation-receipt.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_EXACT_PAIR_SHARD_REPLAY",
        "independent_validation": False,
        "source_producer_replayed": False,
        "result": binding(RESULT),
        "validator": binding(Path(__file__)),
        "verified": {
            "pair_shards": result["pair_shard_count"],
            "pair_transition_records": result["pair_transition_record_count"],
            "global_post_separation_separator": True,
        },
    }
    if args.write_result:
        RECEIPT.write_bytes(canonical_bytes(receipt))
    else:
        require(load(RECEIPT) == receipt, "saved tally receipt differs from exact replay")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
