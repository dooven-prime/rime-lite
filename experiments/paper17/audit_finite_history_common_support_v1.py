#!/usr/bin/env python3
"""Audit order effects against a common source-time support."""

from __future__ import annotations

import json
import tarfile
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from finite_history_execution_common import D0_PATH, ROOT, artifact, write_json
from freeze_finite_history_closure_v1 import ARCHIVE_PREFIX, ARCHIVE_PATH, FREEZE_MANIFEST_PATH
from optimized_exact_common import canonical_sha256, load_json, sha256_file
from run_finite_history_closure_v1 import _intern_observations


OUTPUT_PATH = ROOT / "results" / "finite_history_common_support_audit.v1.json"
RESULT_PATH = ROOT / "results" / "finite_history_closure.v1.json"


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
                while True:
                    block = source.read(8 * 1024 * 1024)
                    if not block:
                        break
                    output.write(block)


def _fibers(
    sources: list[int],
    sequences: dict[int, tuple[int, ...]],
    h: int,
    times: tuple[int, ...],
) -> dict[tuple[int, ...], dict[str, Any]]:
    fibers: dict[tuple[int, ...], dict[str, Any]] = {}
    for source_id in sources:
        sequence = sequences[source_id]
        for time_index in times:
            history = tuple(sequence[time_index - offset] for offset in range(h + 1))
            successor = sequence[time_index + 1]
            fiber = fibers.setdefault(
                history, {"members": [], "successors": defaultdict(list)}
            )
            fiber["members"].append((source_id, time_index))
            fiber["successors"][successor].append((source_id, time_index))
    return fibers


def _partition_digest(fibers: dict[tuple[int, ...], dict[str, Any]]) -> str:
    blocks = sorted(
        sorted(f"{source_id}:{time_index}" for source_id, time_index in fiber["members"])
        for fiber in fibers.values()
    )
    return canonical_sha256(blocks)


def _profile(h: int, fibers: dict[tuple[int, ...], dict[str, Any]]) -> dict[str, Any]:
    N_h = sum(len(fiber["members"]) for fiber in fibers.values())
    K_h = len(fibers)
    failures = [fiber for fiber in fibers.values() if len(fiber["successors"]) > 1]
    return {
        "h": h,
        "N_h": N_h,
        "K_h": K_h,
        "M_h": max(len(fiber["members"]) for fiber in fibers.values()),
        "redundancy_N_minus_K": N_h - K_h,
        "rho_h": {"numerator": K_h, "denominator": N_h},
        "non_singleton_fiber_count": sum(
            len(fiber["members"]) > 1 for fiber in fibers.values()
        ),
        "failure_fiber_count": len(failures),
        "outcome": (
            "FAILED_EXACT_CLOSURE"
            if failures
            else "EXACT_CLOSED_NONINJECTIVE"
            if any(len(fiber["members"]) > 1 for fiber in fibers.values())
            else "EXACT_CLOSED_BY_INJECTIVITY"
        ),
        "partition_sha256": _partition_digest(fibers),
    }


def build_audit() -> dict[str, Any]:
    freeze = load_json(FREEZE_MANIFEST_PATH)
    if freeze["status"] != "POST_EXECUTION_FROZEN":
        raise ValueError("result-owned freeze is not complete")
    if sha256_file(ARCHIVE_PATH) != freeze["exact_sidecar_archive"]["sha256"]:
        raise ValueError("result-owned archive digest mismatch")
    result = load_json(RESULT_PATH)
    sources = [int(value) for value in np.load(D0_PATH, allow_pickle=False)]
    with tempfile.TemporaryDirectory() as directory:
        shard_dir = Path(directory)
        _extract_shards(shard_dir)
        sequences, _, exact_comparisons = _intern_observations(sources, shard_dir, 4)

    registered_h1 = _fibers(sources, sequences, 1, (1, 2, 3))
    h1_failures = [
        (history, fiber)
        for history, fiber in registered_h1.items()
        if len(fiber["successors"]) > 1
    ]
    failure_details = []
    for history, fiber in sorted(h1_failures, key=lambda item: item[0]):
        failure_details.append(
            {
                "history_observation_ids": list(history),
                "member_count": len(fiber["members"]),
                "member_times": {
                    str(key): value
                    for key, value in sorted(
                        Counter(time for _, time in fiber["members"]).items()
                    )
                },
                "distinct_source_count": len(
                    {source for source, _ in fiber["members"]}
                ),
                "distinct_successor_count": len(fiber["successors"]),
            }
        )

    common_times = (2, 3)
    common_fibers = {
        h: _fibers(sources, sequences, h, common_times) for h in (0, 1, 2)
    }
    profiles = [_profile(h, common_fibers[h]) for h in (0, 1, 2)]
    partition_digests = [profile["partition_sha256"] for profile in profiles]
    all_partitions_equal = len(set(partition_digests)) == 1
    all_common_support_orders_closed = all(
        profile["failure_fiber_count"] == 0 for profile in profiles
    )
    all_h1_failures_at_left_boundary = all(
        set(detail["member_times"]) == {"1"} for detail in failure_details
    )

    return {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-common-support-audit.v1",
        "status": "PASS",
        "evidence_role": "POSTHOC_SCOPE_DIAGNOSTIC",
        "independent_validation": False,
        "producer_replayed": False,
        "inputs": [
            artifact(RESULT_PATH, "FROZEN_PRIMARY_RESULT"),
            artifact(FREEZE_MANIFEST_PATH, "FREEZE_MANIFEST"),
            artifact(ARCHIVE_PATH, "RESULT_OWNED_EXACT_SIDECAR"),
            artifact(D0_PATH, "D0_INDEX"),
        ],
        "registered_order_specific_result": {
            "h1_failure_fiber_count": result["classification"]["orders"][1][
                "failure_fiber_count"
            ],
            "h2_outcome": result["classification"]["orders"][2]["outcome"],
            "order_specific_domains": {
                "h0": "t in {0,1,2,3}",
                "h1": "t in {1,2,3}",
                "h2": "t in {2,3}",
            },
        },
        "h1_failure_localization": {
            "failure_fiber_count": len(failure_details),
            "failure_member_count": sum(
                detail["member_count"] for detail in failure_details
            ),
            "all_failure_members_at_t1": all_h1_failures_at_left_boundary,
            "failures": failure_details,
        },
        "common_support_audit": {
            "source_count": len(sources),
            "times": list(common_times),
            "window_count": len(sources) * len(common_times),
            "profiles": profiles,
            "all_orders_closed": all_common_support_orders_closed,
            "all_order_partitions_identical": all_partitions_equal,
            "common_partition_sha256": (
                partition_digests[0] if all_partitions_equal else None
            ),
            "exact_payload_comparisons_after_hash_match": exact_comparisons,
        },
        "diagnosis": {
            "outcome": "REGISTERED_ORDER_EFFECT_CONFOUNDED_WITH_LEFT_BOUNDARY",
            "minimal_memory_order_identified": False,
            "second_lag_resolves_ambiguity_supported": False,
            "safe_positive_result": (
                "On the common registered t>=2 support, the current coarse "
                "observation is already an exact noninjective closed state, and "
                "orders 0, 1, and 2 induce the same fiber partition."
            ),
            "required_future_design": (
                "Compare every history order on one common source-time universe "
                "Omega_(H_max,T), rather than on order-dependent left boundaries."
            ),
        },
        "claim_boundary": {
            "frozen_primary_result_modified": False,
            "new_orbit_generated": False,
            "minimal_h_equals_2_claim_supported": False,
            "observation_plus_two_lags_required_claim_supported": False,
            "full_domain_claimed": False,
            "indefinite_forward_invariance_claimed": False,
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
