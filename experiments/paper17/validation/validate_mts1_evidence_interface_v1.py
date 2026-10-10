#!/usr/bin/env python3
"""Check compact MTS-1 tally and deposit bindings without opening the sidecar."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MECHANISM = ROOT / "mechanism"
TALLY = MECHANISM / "results" / "mts1-v1.global-pair-tally.v1.json"
RECEIPT = MECHANISM / "results" / "mts1-v1.global-pair-tally.v1.validation-receipt.json"
ANCHOR = MECHANISM / "results" / "mts1-v1.zenodo-anchor.v1.json"
INVENTORY = MECHANISM / "results" / "mts1-v1" / "inventory.json"
CLASSIFICATION = MECHANISM / "results" / "mts1-v1" / "validation" / "mechanism_classification.v1.json"
DECISIVE = {
    "CLIPPING_MODIFIES_NONZERO_COARSE_RESIDUAL",
    "FATE_DISAGREEMENT_WITH_NONZERO_CLIP_CORRECTION",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> dict:
    tally = load(TALLY)
    receipt = load(RECEIPT)
    anchor = load(ANCHOR)
    inventory = load(INVENTORY)
    classification = load(CLASSIFICATION)["classification"]
    require(tally["status"] == "PASS", "global tally not passed")
    require(tally["pair_shard_count"] == 33, "wrong shard count")
    require(tally["pair_transition_record_count"] == 6975, "wrong record count")
    require(receipt["status"] == "PASS", "global tally receipt not passed")
    require(receipt["result"]["bytes"] == TALLY.stat().st_size, "tally size mismatch")
    require(receipt["result"]["sha256"] == sha256(TALLY), "tally digest mismatch")
    require(receipt["validator"]["sha256"] == sha256(MECHANISM / "audit_global_pair_tally_v1.py"), "tally validator digest mismatch")
    for entry in tally["inputs"]:
        path = ROOT.parents[1] / entry["path"]
        require(path.stat().st_size == entry["bytes"], "input size mismatch")
        require(sha256(path) == entry["sha256"], "input digest mismatch")
    require(tally["primary_predicate_order"] == classification["primary_predicate_order"], "predicate order mismatch")
    require(len(tally["cohort_counts"]) == 33, "cohort row count mismatch")
    require(len(tally["global_counts"]) == 6, "global row count mismatch")
    for global_row in tally["global_counts"]:
        rows = [
            row for row in tally["cohort_counts"]
            if row["transition"] == global_row["transition"]
            and row["pair_role"] == global_row["pair_role"]
        ]
        require(sum(row["pair_count"] for row in rows) == global_row["pair_count"], "global pair sum mismatch")
        for predicate in tally["primary_predicate_order"]:
            require(
                sum(row["true_counts"][predicate] for row in rows)
                == global_row["true_counts"][predicate],
                "global predicate sum mismatch",
            )
    require(
        {(row["transition"], row["cohort_id"]) for row in tally["cohort_counts"]}
        == {(row["transition"], row["cohort_id"]) for row in inventory["pair_shards"]},
        "tally/inventory shard grid mismatch",
    )
    shard_counts = {
        (row["transition"], row["cohort_id"]): row["record_count"]
        for row in inventory["pair_shards"]
    }
    for row in tally["cohort_counts"]:
        require(
            row["pair_count"] == shard_counts[(row["transition"], row["cohort_id"])],
            "tally/inventory cohort count mismatch",
        )
    rows_by_key = {
        (row["transition"], row["pair_role"]): row
        for row in tally["global_counts"]
    }
    for transition in ("2_TO_3", "3_TO_4"):
        transient = rows_by_key[(transition, "TRANSIENT_OBSTRUCTION")]
        persistent = rows_by_key[(transition, "PERSISTENT_SAFE")]
        require(transient["pair_count"] == 570, "transient pair total mismatch")
        require(persistent["pair_count"] == 1755, "persistent pair total mismatch")
        for predicate in DECISIVE:
            require(transient["true_counts"][predicate] == 570, "transient separator mismatch")
            require(persistent["true_counts"][predicate] == 0, "persistent separator mismatch")
            require(
                {"transition": transition, "predicate": predicate,
                 "direction": "TRANSIENT_ALL__PERSISTENT_NONE"}
                in classification["exact_separators"],
                "frozen cell separator mismatch",
            )
    require(anchor["status"] == "PUBLIC_DEPOSIT_VERIFIED", "external anchor status mismatch")
    require(anchor["published_record"]["doi"] == "10.5281/zenodo.23234143", "external DOI mismatch")
    require(anchor["published_record"]["status"] == "published", "deposit not published")
    require(anchor["verification"]["zenodo_file_count"] == len(anchor["files"]) == 17, "deposit file count mismatch")
    require(anchor["exact_sidecar_identity"]["inventory_sha256"] == sha256(INVENTORY), "deposit/inventory mismatch")
    require(anchor["exact_sidecar_identity"]["ordered_artifact_closure_sha256"] == inventory["ordered_artifact_closure_sha256"], "deposit/sidecar closure mismatch")
    require(anchor["verification"]["remote_file_bytes_downloaded_for_sha256"] is False, "remote download overclaim")
    return {
        "schema": "rime.paper17.mts1-evidence-interface-validation.v1",
        "status": "PASS",
        "validation_mode": "LOCAL_COMPACT_BINDING_VERIFICATION",
        "sidecar_pair_shards_replayed": False,
        "independent_validation": False,
        "doi": anchor["published_record"]["doi"],
        "global_pair_counts_bound": True,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
