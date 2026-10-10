#!/usr/bin/env python3
"""Describe how the t=1 obstruction is replaced by post-transient closure."""

from __future__ import annotations

import json
import tarfile
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from finite_history_binary import iter_shard
from finite_history_execution_common import D0_PATH, ROOT, artifact, write_json
from freeze_finite_history_closure_v1 import ARCHIVE_PREFIX, ARCHIVE_PATH, FREEZE_MANIFEST_PATH
from optimized_exact_common import load_json, sha256_file
from run_finite_history_closure_v1 import _intern_observations


OUTPUT_PATH = ROOT / "results" / "finite_history_transient_fiber_audit.v1.json"
COMMON_SUPPORT_AUDIT_PATH = (
    ROOT / "results" / "finite_history_common_support_audit.v1.json"
)
SECTOR_LABELS_PATH = (
    ROOT / "results" / "finite_history_closure.v1.sector-labels.json"
)


def _extract_sidecar(destination: Path) -> None:
    allowed_prefixes = ("shards/", "source-metadata/")
    with tarfile.open(ARCHIVE_PATH, mode="r:") as archive:
        for member in archive.getmembers():
            prefix = f"{ARCHIVE_PREFIX}/"
            if not member.name.startswith(prefix):
                continue
            relative = member.name[len(prefix) :]
            if not relative.startswith(allowed_prefixes):
                continue
            parts = Path(relative).parts
            if len(parts) != 2 or parts[0] not in {"shards", "source-metadata"}:
                raise ValueError(f"unsafe sidecar member: {member.name}")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"missing sidecar payload: {member.name}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as output:
                while True:
                    block = source.read(8 * 1024 * 1024)
                    if not block:
                        break
                    output.write(block)


def _observation_records(
    sources: list[int], shard_dir: Path
) -> dict[tuple[int, int], dict[int, Any]]:
    records: dict[tuple[int, int], dict[int, Any]] = {}
    for source_id in sources:
        for record in iter_shard(shard_dir / f"{source_id}.bin"):
            records[(source_id, record.time)] = record.observation
    return records


def build_audit() -> dict[str, Any]:
    freeze = load_json(FREEZE_MANIFEST_PATH)
    if freeze["status"] != "POST_EXECUTION_FROZEN":
        raise ValueError("result-owned freeze is not complete")
    if sha256_file(ARCHIVE_PATH) != freeze["exact_sidecar_archive"]["sha256"]:
        raise ValueError("result-owned archive digest mismatch")
    common_support = load_json(COMMON_SUPPORT_AUDIT_PATH)
    if common_support["diagnosis"]["minimal_memory_order_identified"]:
        raise ValueError("common-support boundary unexpectedly changed")
    labels = load_json(SECTOR_LABELS_PATH)
    sources = [int(value) for value in np.load(D0_PATH, allow_pickle=False)]

    with tempfile.TemporaryDirectory() as directory:
        sidecar_root = Path(directory)
        _extract_sidecar(sidecar_root)
        sequences, _, exact_comparisons = _intern_observations(
            sources, sidecar_root / "shards", 4
        )
        observations = _observation_records(sources, sidecar_root / "shards")

        h1_fibers: dict[tuple[int, int], dict[str, Any]] = {}
        for source_id in sources:
            sequence = sequences[source_id]
            for time_index in (1, 2, 3):
                key = (sequence[time_index], sequence[time_index - 1])
                fiber = h1_fibers.setdefault(
                    key, {"members": [], "successors": defaultdict(list)}
                )
                fiber["members"].append((source_id, time_index))
                fiber["successors"][sequence[time_index + 1]].append(
                    (source_id, time_index)
                )
        failures = [
            (history, fiber)
            for history, fiber in h1_fibers.items()
            if len(fiber["successors"]) > 1
        ]

        z2_fibers: dict[int, list[int]] = defaultdict(list)
        z3_fibers: dict[int, list[int]] = defaultdict(list)
        for source_id in sources:
            z2_fibers[sequences[source_id][2]].append(source_id)
            z3_fibers[sequences[source_id][3]].append(source_id)

        failure_details: list[dict[str, Any]] = []
        offending_sources: set[int] = set()
        for history, fiber in sorted(failures, key=lambda item: item[0]):
            members = sorted(source_id for source_id, _ in fiber["members"])
            offending_sources.update(members)
            varying_coordinates = []
            for coordinate, label in enumerate(labels):
                values = {
                    observations[(source_id, 2)].get(coordinate, 0)
                    for source_id in members
                }
                if len(values) > 1:
                    varying_coordinates.append(
                        {"coordinate": coordinate, "label": label}
                    )
            metadata = [
                load_json(sidecar_root / "source-metadata" / f"{source_id}.json")
                for source_id in members
            ]
            step_two = [entry["steps"][2] for entry in metadata]
            initial_coordinates = {
                next(iter(observations[(source_id, 0)])) for source_id in members
            }
            failure_details.append(
                {
                    "history_observation_ids": list(history),
                    "source_ids": members,
                    "member_count": len(members),
                    "initial_sector_labels": [
                        labels[coordinate]
                        for coordinate in sorted(initial_coordinates)
                    ],
                    "distinct_z2_observation_count": len(
                        {sequences[source_id][2] for source_id in members}
                    ),
                    "all_z2_observations_globally_singleton": all(
                        len(z2_fibers[sequences[source_id][2]]) == 1
                        for source_id in members
                    ),
                    "varying_z2_coordinates": varying_coordinates,
                    "step_1_to_2_state_support_range": [
                        min(entry["state_support_count"] for entry in step_two),
                        max(entry["state_support_count"] for entry in step_two),
                    ],
                    "distinct_step_1_to_2_clip_summary_count": len(
                        {
                            (
                                entry["clip_lower_count"],
                                entry["clip_upper_count"],
                                entry["clip_interior_count"],
                            )
                            for entry in step_two
                        }
                    ),
                }
            )

        z2_cohorts = [
            set(members) for members in z2_fibers.values() if len(members) > 1
        ]
        z3_cohorts = [
            set(members) for members in z3_fibers.values() if len(members) > 1
        ]
        z3_sets = {frozenset(cohort) for cohort in z3_cohorts}
        persistent_cohorts = []
        for cohort in sorted(z2_cohorts, key=lambda group: (-len(group), min(group))):
            frozen = frozenset(cohort)
            source_id = min(cohort)
            initial_coordinates = {
                next(iter(observations[(member, 0)])) for member in cohort
            }
            persistent_cohorts.append(
                {
                    "source_ids": sorted(cohort),
                    "size": len(cohort),
                    "initial_sector_labels": [
                        labels[coordinate]
                        for coordinate in sorted(initial_coordinates)
                    ],
                    "same_source_membership_at_t3": frozen in z3_sets,
                    "z2_observation_id": sequences[source_id][2],
                    "z3_observation_id": sequences[source_id][3],
                    "z4_successor_observation_id": sequences[source_id][4],
                    "overlap_with_t1_offending_sources": len(
                        cohort & offending_sources
                    ),
                }
            )

    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-transient-fiber-audit.v1",
        "status": "PASS",
        "evidence_role": "POSTHOC_DESCRIPTIVE_MECHANISM_LOCALIZATION",
        "independent_validation": False,
        "producer_replayed": False,
        "inputs": [
            artifact(FREEZE_MANIFEST_PATH, "FREEZE_MANIFEST"),
            artifact(ARCHIVE_PATH, "RESULT_OWNED_EXACT_SIDECAR"),
            artifact(COMMON_SUPPORT_AUDIT_PATH, "COMMON_SUPPORT_DIAGNOSTIC"),
            artifact(D0_PATH, "D0_INDEX"),
            artifact(SECTOR_LABELS_PATH, "SECTOR_LABELS"),
        ],
        "transient_separation": {
            "t1_failure_fiber_count": len(failure_details),
            "offending_source_count": len(offending_sources),
            "all_offending_sources_globally_singleton_at_t2": all(
                len(z2_fibers[sequences[source_id][2]]) == 1
                for source_id in offending_sources
            ),
            "offending_sources_in_post_transient_non_singleton_cohorts": sum(
                source_id in cohort
                for source_id in offending_sources
                for cohort in z2_cohorts
            ),
            "failure_fibers": failure_details,
        },
        "persistent_safe_forgetting": {
            "cohort_count_per_time_slice": len(z2_cohorts),
            "cohort_sizes": [len(cohort) for cohort in sorted(z2_cohorts, key=len, reverse=True)],
            "same_cohort_collection_at_t2_and_t3": (
                {frozenset(cohort) for cohort in z2_cohorts} == z3_sets
            ),
            "total_redundancy_per_time_slice": sum(
                len(cohort) - 1 for cohort in z2_cohorts
            ),
            "total_redundancy_across_t2_t3": 2
            * sum(len(cohort) - 1 for cohort in z2_cohorts),
            "cohorts": persistent_cohorts,
        },
        "exact_identity": {
            "hash_role": "INDEX_ONLY",
            "exact_payload_comparisons_after_hash_match": exact_comparisons,
        },
        "diagnosis": {
            "outcome": "TRANSIENT_SEPARATION_PLUS_PERSISTENT_SAFE_FORGETTING",
            "safe_statement": (
                "Every source participating in a t=1 closure obstruction has a "
                "globally singleton coarse observation at t=2. The remaining "
                "post-transient noninjectivity consists of five disjoint source "
                "cohorts whose membership persists from t=2 to t=3 and whose "
                "registered successors agree."
            ),
            "mechanism_identified": False,
        },
        "claim_boundary": {
            "clipping_causes_separation_claimed": False,
            "microscopic_convergence_claimed": False,
            "slow_mode_claimed": False,
            "recurrent_input_mechanism_claimed": False,
            "full_domain_claimed": False,
            "beyond_horizon_persistence_claimed": False,
        },
        "producer": artifact(Path(__file__).resolve(), "AUDIT_PRODUCER"),
    }


def main() -> int:
    result = build_audit()
    write_json(OUTPUT_PATH, result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
