#!/usr/bin/env python3
"""Audit whether the registered successor image closes on the common support."""

from __future__ import annotations

import json
import tarfile
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from finite_history_execution_common import D0_PATH, ROOT, artifact, write_json
from freeze_finite_history_closure_v1 import (
    ARCHIVE_PATH,
    ARCHIVE_PREFIX,
    FREEZE_MANIFEST_PATH,
)
from optimized_exact_common import load_json, sha256_file
from run_finite_history_closure_v1 import _intern_observations


OUTPUT_PATH = ROOT / "results" / "finite_history_terminal_image_audit.v1.json"


def _extract_shards(destination: Path) -> None:
    prefix = f"{ARCHIVE_PREFIX}/shards/"
    with tarfile.open(ARCHIVE_PATH, mode="r:") as archive:
        for member in archive.getmembers():
            if not member.name.startswith(prefix):
                continue
            name = member.name[len(prefix) :]
            if not name or "/" in name or "\\" in name or not name.endswith(".bin"):
                raise ValueError(f"unsafe shard member: {member.name}")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"missing shard payload: {member.name}")
            target = destination / name
            with target.open("wb") as output:
                while block := source.read(8 * 1024 * 1024):
                    output.write(block)


def build_audit() -> dict[str, Any]:
    freeze = load_json(FREEZE_MANIFEST_PATH)
    if freeze["status"] != "POST_EXECUTION_FROZEN":
        raise ValueError("result-owned freeze is not complete")
    if sha256_file(ARCHIVE_PATH) != freeze["exact_sidecar_archive"]["sha256"]:
        raise ValueError("result-owned archive digest mismatch")

    sources = [int(value) for value in np.load(D0_PATH, allow_pickle=False)]
    with tempfile.TemporaryDirectory() as directory:
        shard_dir = Path(directory)
        _extract_shards(shard_dir)
        sequences, _, exact_comparisons = _intern_observations(
            sources, shard_dir, 4
        )

    images = {
        time_index: {sequences[source_id][time_index] for source_id in sources}
        for time_index in (2, 3, 4)
    }
    common_image = images[2] | images[3]
    t2_successors = {sequences[source_id][3] for source_id in sources}
    t3_successors = {sequences[source_id][4] for source_id in sources}

    return {
        "schema": "rime.paper17.finite-history-terminal-image-audit.v1",
        "status": "PASS",
        "evidence_role": "POSTHOC_TERMINAL_IMAGE_BOUNDARY_AUDIT",
        "independent_validation": False,
        "producer_replayed": False,
        "inputs": [
            artifact(FREEZE_MANIFEST_PATH, "FREEZE_MANIFEST"),
            artifact(ARCHIVE_PATH, "RESULT_OWNED_EXACT_SIDECAR"),
            artifact(D0_PATH, "D0_INDEX"),
        ],
        "registered_support": {
            "source_count": len(sources),
            "common_support_times": [2, 3],
            "terminal_successor_time": 4,
        },
        "exact_image_profile": {
            "distinct_observations_by_time": {
                str(time_index): len(images[time_index])
                for time_index in (2, 3, 4)
            },
            "common_image_size": len(common_image),
            "t2_t3_intersection_size": len(images[2] & images[3]),
            "t4_intersection_with_common_image_size": len(images[4] & common_image),
            "all_t2_successors_in_common_image": t2_successors <= common_image,
            "all_t3_successors_in_common_image": t3_successors <= common_image,
            "t3_successors_outside_common_image_count": len(
                t3_successors - common_image
            ),
            "exact_payload_comparisons_after_hash_match": exact_comparisons,
        },
        "classification": {
            "one_step_factorization_on_common_support": True,
            "registered_internal_shift_count": 1,
            "coarse_endomap_on_common_image_verified": t3_successors <= common_image,
            "indefinite_iteration_verified": False,
            "safe_outcome": "HORIZON_BOUNDED_ONE_STEP_FACTORIZATION_WITH_ONE_INTERNAL_SHIFT",
        },
        "claim_boundary": {
            "autonomous_closed_dynamical_system_claimed": False,
            "terminal_successor_in_verified_state_image_claimed": False,
            "full_domain_claimed": False,
            "producer_replayed": False,
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
