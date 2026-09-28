#!/usr/bin/env python3
"""Execute the registered exact finite-history orbit-window classification."""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np
import psutil

from finite_history_binary import iter_shard, read_payload_slice, write_shard
from finite_history_execution_common import (
    ARRAY_NAMES,
    D0_PATH,
    REGISTRATION_PATH,
    ROOT,
    RUNTIME_ROOT,
    artifact,
    load_backend_contract,
    load_scope_contract,
    resource_caps,
    verify_registration,
    write_json,
)
from optimized_exact_common import (
    bit_profile,
    exact_observation,
    process_memory,
    rational_payload_hash,
    runtime_identity,
    sha256_file,
)


_WORKER: dict[str, Any] = {}


def _worker_init(cache_dir_text: str, kernel_dir_text: str) -> None:
    cache_dir = Path(cache_dir_text)
    sys.path.insert(0, kernel_dir_text)
    import optimized_exact_sparse_kernel as kernel

    arrays = {
        name: np.load(cache_dir / f"{name}.npy", mmap_mode="r", allow_pickle=False)
        for name in ARRAY_NAMES
    }
    for name, array in arrays.items():
        if not isinstance(array, np.memmap) or array.flags.writeable:
            raise ValueError(f"worker array is not read-only mmap: {name}")
    labels = json.loads((cache_dir / "sector_labels.json").read_text(encoding="utf-8"))
    _WORKER.update(arrays)
    _WORKER["kernel"] = kernel
    _WORKER["sector_count"] = len(labels)
    _WORKER["alpha"] = gmpy2.mpq(1, 5)
    _WORKER["decay"] = gmpy2.mpq(4, 5)
    _WORKER["zero"] = gmpy2.mpq(0)
    _WORKER["one"] = gmpy2.mpq(1)


def _generate_source(source: int, shard_text: str, metadata_text: str, horizon: int) -> dict[str, Any]:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    shard_path = Path(shard_text)
    metadata_path = Path(metadata_text)
    state = {int(source): gmpy2.mpq(1)}
    observation, observation_metrics = exact_observation(
        state,
        _WORKER["sector_codes"],
        _WORKER["sector_sizes"],
        _WORKER["sector_count"],
    )
    records = [(source, 0, _WORKER["sector_count"], observation)]
    steps: list[dict[str, Any]] = [
        {
            "time": 0,
            "state_support_count": 1,
            "state_payload_sha256_provenance_only": rational_payload_hash(state),
            "observation_payload_sha256_provenance_only": rational_payload_hash(observation),
            **observation_metrics,
            **bit_profile(list(state.values())),
        }
    ]
    for step in range(1, horizon + 1):
        step_started = time.perf_counter()
        state, counts = _WORKER["kernel"].exact_step(
            _WORKER["indptr"],
            _WORKER["indices"],
            _WORKER["numerators"],
            _WORKER["row_abs"],
            state,
            _WORKER["alpha"],
            _WORKER["decay"],
            _WORKER["zero"],
            _WORKER["one"],
        )
        observation, observation_metrics = exact_observation(
            state,
            _WORKER["sector_codes"],
            _WORKER["sector_sizes"],
            _WORKER["sector_count"],
        )
        records.append((source, step, _WORKER["sector_count"], observation))
        steps.append(
            {
                "time": step,
                "exact_step_wall_seconds": time.perf_counter() - step_started,
                "state_support_count": len(state),
                "state_payload_sha256_provenance_only": rational_payload_hash(state),
                "observation_payload_sha256_provenance_only": rational_payload_hash(observation),
                **counts,
                **observation_metrics,
                **bit_profile(list(state.values())),
            }
        )

    shard = write_shard(shard_path, records)
    result = {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-source-shard.v1",
        "status": "COMPLETE",
        "source_id": source,
        "horizon_T": horizon,
        "record_count": horizon + 1,
        "shard": {
            "path": shard_path.name,
            **shard,
        },
        "steps": steps,
        "resources": {
            "worker_process_cpu_seconds": time.process_time() - started_cpu,
            "worker_wall_seconds": time.perf_counter() - started_wall,
            "final_memory": process_memory(),
        },
    }
    write_json(metadata_path, result)
    return result


def _validate_completed_source(source: int, shard: Path, metadata: Path, horizon: int) -> dict[str, Any] | None:
    if not shard.is_file() or not metadata.is_file():
        return None
    try:
        recorded = json.loads(metadata.read_text(encoding="utf-8"))
        if recorded["status"] != "COMPLETE" or recorded["source_id"] != source:
            return None
        if recorded["horizon_T"] != horizon or recorded["record_count"] != horizon + 1:
            return None
        if recorded["shard"]["bytes"] != shard.stat().st_size:
            return None
        if recorded["shard"]["sha256"] != sha256_file(shard):
            return None
        records = list(iter_shard(shard))
        if len(records) != horizon + 1:
            return None
        if any(record.source_id != source or record.time != index for index, record in enumerate(records)):
            return None
        return recorded
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        return None


def _directory_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _process_tree_metrics() -> tuple[int, float]:
    root = psutil.Process()
    processes = [root, *root.children(recursive=True)]
    rss = 0
    cpu = 0.0
    for process in processes:
        try:
            rss += int(process.memory_info().rss)
            times = process.cpu_times()
            cpu += float(times.user + times.system)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rss, cpu


def _checkpoint(path: Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def _intern_observations(
    sources: list[int], shard_dir: Path, horizon: int
) -> tuple[dict[int, tuple[int, ...]], list[dict[str, Any]], int]:
    digest_buckets: dict[str, list[int]] = defaultdict(list)
    representatives: list[tuple[Path, int, int]] = []
    inventory: list[dict[str, Any]] = []
    source_sequences: dict[int, tuple[int, ...]] = {}
    exact_payload_comparisons = 0
    for source in sources:
        shard = shard_dir / f"{source}.bin"
        sequence: list[int] = []
        for record in iter_shard(shard):
            digest = hashlib.sha256(record.observation_payload).hexdigest()
            observation_id: int | None = None
            for candidate_id in digest_buckets[digest]:
                exact_payload_comparisons += 1
                candidate_path, offset, length = representatives[candidate_id]
                if length == record.observation_length and read_payload_slice(
                    candidate_path, offset, length
                ) == record.observation_payload:
                    observation_id = candidate_id
                    break
            if observation_id is None:
                observation_id = len(representatives)
                representatives.append(
                    (shard, record.observation_offset, record.observation_length)
                )
                digest_buckets[digest].append(observation_id)
                inventory.append(
                    {
                        "observation_id": observation_id,
                        "sha256_index_only": digest,
                        "representative_source": source,
                        "representative_time": record.time,
                        "payload_bytes": record.observation_length,
                    }
                )
            sequence.append(observation_id)
        if len(sequence) != horizon + 1:
            raise ValueError(f"source {source} has incomplete observation sequence")
        source_sequences[source] = tuple(sequence)
    return source_sequences, inventory, exact_payload_comparisons


def _classify(
    sources: list[int], source_sequences: dict[int, tuple[int, ...]], H: int, T: int
) -> dict[str, Any]:
    orders: list[dict[str, Any]] = []
    for h in range(H + 1):
        fibers: dict[tuple[int, ...], dict[str, Any]] = {}
        shift_checks = 0
        for source in sources:
            sequence = source_sequences[source]
            for t in range(h, T):
                history = tuple(sequence[t - offset] for offset in range(h + 1))
                successor = sequence[t + 1]
                fiber = fibers.setdefault(
                    history,
                    {"count": 0, "sources": set(), "successors": {}, "first": (source, t)},
                )
                fiber["count"] += 1
                fiber["sources"].add(source)
                fiber["successors"].setdefault(successor, (source, t))
                if t < T - 1:
                    shifted = (successor, *history[:-1])
                    expected = tuple(sequence[t + 1 - offset] for offset in range(h + 1))
                    if shifted != expected:
                        raise AssertionError("horizon-bounded history shift mismatch")
                    shift_checks += 1
        failures = [item for item in fibers.items() if len(item[1]["successors"]) > 1]
        N_h = len(sources) * (T - h)
        K_h = len(fibers)
        M_h = max(int(fiber["count"]) for fiber in fibers.values())
        witness = None
        if failures:
            history, fiber = failures[0]
            first_two = list(fiber["successors"].items())[:2]
            witness = {
                "history_observation_ids": list(history),
                "first": {
                    "successor_observation_id": first_two[0][0],
                    "source_id": first_two[0][1][0],
                    "time": first_two[0][1][1],
                },
                "second": {
                    "successor_observation_id": first_two[1][0],
                    "source_id": first_two[1][1][0],
                    "time": first_two[1][1][1],
                },
            }
        if failures:
            outcome = "FAILED_EXACT_CLOSURE"
        elif M_h > 1:
            outcome = "EXACT_CLOSED_NONINJECTIVE"
        else:
            outcome = "EXACT_CLOSED_BY_INJECTIVITY"
        orders.append(
            {
                "h": h,
                "outcome": outcome,
                "N_h": N_h,
                "K_h": K_h,
                "M_h": M_h,
                "redundancy_N_minus_K": N_h - K_h,
                "rho_h": {"numerator": K_h, "denominator": N_h},
                "non_singleton_fiber_count": sum(1 for fiber in fibers.values() if fiber["count"] > 1),
                "maximum_distinct_sources_in_one_fiber": max(len(fiber["sources"]) for fiber in fibers.values()),
                "failure_fiber_count": len(failures),
                "first_failure_witness": witness,
                "horizon_bounded_shift_checks": shift_checks,
            }
        )
    primary = orders[H]["outcome"]
    minimal_closing_order = next(
        (entry["h"] for entry in orders if entry["outcome"] != "FAILED_EXACT_CLOSURE"),
        None,
    )
    return {
        "orders": orders,
        "primary_outcome_at_H": primary,
        "minimal_closing_order_on_registered_domain": minimal_closing_order,
        "minimality_claim_allowed": (
            minimal_closing_order is not None
            and all(
                entry["outcome"] == "FAILED_EXACT_CLOSURE"
                for entry in orders[:minimal_closing_order]
            )
        ),
    }


def _write_unresolved(
    output: Path,
    run_id: str,
    run_root: Path,
    reason: str,
    completed: int,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    result = {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-result.v1",
        "status": "UNRESOLVED",
        "outcome": "UNRESOLVED",
        "run_id": run_id,
        "reason": reason,
        "completed_sources": completed,
        "required_sources": 711,
        "D0_resized": False,
        "run_root": run_root.relative_to(ROOT).as_posix(),
        "resources": metrics,
        "claim_boundary": {
            "closure_classified": False,
            "minimal_order_claimed": False,
            "incomplete_scan_is_negative_evidence": False,
        },
    }
    write_json(output, result)
    write_json(run_root / "UNRESOLVED.json", result)
    return result


def execute(run_id: str, output: Path) -> dict[str, Any]:
    registration = verify_registration()
    _, d0 = load_scope_contract()
    _, cache_dir, kernel_path = load_backend_contract()
    caps = resource_caps()
    expected_run_id = registration["execution"]["run_id"]
    if run_id != expected_run_id:
        raise ValueError(f"run id must equal registered value: {expected_run_id}")
    H = int(registration["scope"]["H"])
    T = int(registration["scope"]["T"])
    sources = [int(value) for value in d0]
    run_root = RUNTIME_ROOT / run_id
    shard_dir = run_root / "shards"
    metadata_dir = run_root / "source-metadata"
    checkpoint_path = run_root / "checkpoint.json"
    shard_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    checkpoint = (
        json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint_path.is_file()
        else {"cumulative_wall_seconds": 0.0, "cumulative_cpu_seconds": 0.0}
    )
    prior_wall = float(checkpoint.get("cumulative_wall_seconds", 0.0))
    prior_cpu = float(checkpoint.get("cumulative_cpu_seconds", 0.0))
    started_wall = time.monotonic()
    _, started_tree_cpu = _process_tree_metrics()
    completed: dict[int, dict[str, Any]] = {}
    pending_sources: list[int] = []
    for source in sources:
        metadata = _validate_completed_source(
            source,
            shard_dir / f"{source}.bin",
            metadata_dir / f"{source}.json",
            T,
        )
        if metadata is None:
            pending_sources.append(source)
        else:
            completed[source] = metadata

    peak_rss = 0
    peak_storage = _directory_bytes(run_root)
    maximum_accounted_cpu = prior_cpu
    last_reported_completed = len(completed)
    pool = multiprocessing.get_context("spawn").Pool(
        processes=int(caps["maximum_workers"]),
        initializer=_worker_init,
        initargs=(str(cache_dir), str(kernel_path.parent)),
    )
    active: dict[int, Any] = {}
    cursor = 0
    failure_reason: str | None = None
    try:
        while cursor < len(pending_sources) or active:
            while cursor < len(pending_sources) and len(active) < int(caps["maximum_workers"]):
                source = pending_sources[cursor]
                cursor += 1
                active[source] = pool.apply_async(
                    _generate_source,
                    (
                        source,
                        str(shard_dir / f"{source}.bin"),
                        str(metadata_dir / f"{source}.json"),
                        T,
                    ),
                )
            time.sleep(min(1.0, float(caps["poll_interval_seconds"])))
            for source, task in list(active.items()):
                if task.ready():
                    try:
                        completed[source] = task.get()
                    except Exception as exc:  # worker traceback is preserved by multiprocessing
                        failure_reason = f"WORKER_FAILURE:{type(exc).__name__}:{exc}"
                        break
                    del active[source]
            rss, tree_cpu = _process_tree_metrics()
            wall = prior_wall + (time.monotonic() - started_wall)
            cpu = prior_cpu + max(0.0, tree_cpu - started_tree_cpu)
            maximum_accounted_cpu = max(maximum_accounted_cpu, cpu)
            storage = _directory_bytes(run_root)
            peak_rss = max(peak_rss, rss)
            peak_storage = max(peak_storage, storage)
            _checkpoint(
                checkpoint_path,
                {
                    "run_id": run_id,
                    "completed_source_count": len(completed),
                    "cumulative_wall_seconds": wall,
                    "cumulative_cpu_seconds": cpu,
                    "peak_process_tree_rss_bytes": peak_rss,
                    "peak_incremental_storage_bytes": peak_storage,
                    "next_pending_cursor": cursor,
                },
            )
            if (
                len(completed) == len(sources)
                or len(completed) >= last_reported_completed + 5
            ):
                print(
                    json.dumps(
                        {
                            "event": "FINITE_HISTORY_PROGRESS",
                            "completed_sources": len(completed),
                            "required_sources": len(sources),
                            "active_workers": len(active),
                            "cumulative_wall_hours": wall / 3600.0,
                            "cumulative_cpu_core_hours_sampled": cpu / 3600.0,
                            "process_tree_rss_gib": rss / 2**30,
                            "incremental_storage_gib": storage / 2**30,
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
                last_reported_completed = len(completed)
            if failure_reason:
                break
            if wall > float(caps["primary_wall_seconds"]):
                failure_reason = "PRIMARY_WALL_CAP_EXCEEDED"
            elif cpu > float(caps["primary_cpu_seconds"]):
                failure_reason = "PRIMARY_CPU_CAP_EXCEEDED"
            elif rss > int(caps["peak_process_tree_rss_bytes"]):
                failure_reason = "PROCESS_TREE_RSS_CAP_EXCEEDED"
            elif storage > int(caps["incremental_run_storage_bytes"]):
                failure_reason = "INCREMENTAL_STORAGE_CAP_EXCEEDED"
            if failure_reason:
                break
        if failure_reason:
            pool.terminate()
        else:
            pool.close()
        pool.join()
    except BaseException:
        pool.terminate()
        pool.join()
        raise

    rss, tree_cpu = _process_tree_metrics()
    wall = prior_wall + (time.monotonic() - started_wall)
    cpu = prior_cpu + max(0.0, tree_cpu - started_tree_cpu)
    cpu = max(cpu, maximum_accounted_cpu)
    storage = _directory_bytes(run_root)
    peak_rss = max(peak_rss, rss)
    peak_storage = max(peak_storage, storage)
    resource_metrics = {
        "cumulative_wall_seconds": wall,
        "cumulative_cpu_seconds_sampled": cpu,
        "peak_process_tree_rss_bytes": peak_rss,
        "peak_incremental_storage_bytes": peak_storage,
        "caps": caps,
    }
    if failure_reason or len(completed) != len(sources):
        return _write_unresolved(
            output,
            run_id,
            run_root,
            failure_reason or "INCOMPLETE_D0",
            len(completed),
            resource_metrics,
        )

    source_sequences, observation_inventory, comparisons = _intern_observations(
        sources, shard_dir, T
    )
    classification = _classify(sources, source_sequences, H, T)
    inventory = {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-sidecar-inventory.v1",
        "run_id": run_id,
        "source_count": len(sources),
        "ordered_sources": sources,
        "shards": [
            {
                "source_id": source,
                "path": f"shards/{source}.bin",
                "bytes": (shard_dir / f"{source}.bin").stat().st_size,
                "sha256": sha256_file(shard_dir / f"{source}.bin"),
                "metadata_path": f"source-metadata/{source}.json",
                "metadata_sha256": sha256_file(metadata_dir / f"{source}.json"),
            }
            for source in sources
        ],
        "observation_inventory": observation_inventory,
        "exact_payload_comparisons_after_hash_match": comparisons,
    }
    inventory_path = run_root / "sidecar-inventory.json"
    write_json(inventory_path, inventory)
    result = {
        "schema": "rime.exploratory.male-cns-dynamic-compression.finite-history-result.v1",
        "status": "COMPLETED",
        "evidence_level": "Computational Certificate",
        "run_id": run_id,
        "scope": {
            "domain": "REGISTERED_REDUCED_D0",
            "source_count": len(sources),
            "H": H,
            "T": T,
            "orders": list(range(H + 1)),
            "D0_resized": False,
        },
        "classification": classification,
        "exact_identity": {
            "hash_role": "INDEX_ONLY",
            "hash_match_followed_by_canonical_payload_comparison": True,
            "exact_payload_comparisons": comparisons,
            "distinct_exact_observations": len(observation_inventory),
        },
        "sidecar_inventory": {
            "path": inventory_path.relative_to(ROOT).as_posix(),
            "bytes": inventory_path.stat().st_size,
            "sha256": sha256_file(inventory_path),
        },
        "registration": artifact(REGISTRATION_PATH, "REGISTRATION"),
        "runtime": runtime_identity(),
        "resources": resource_metrics,
        "claim_boundary": {
            "registered_reduced_domain_only": True,
            "full_domain_claimed": False,
            "finite_H_failure_implies_infinite_memory": False,
            "indefinite_forward_invariance_claimed": False,
            "independent_validation": False,
        },
    }
    write_json(output, result)
    write_json(run_root / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="finite-history-v1")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "finite_history_closure.v1.json",
    )
    args = parser.parse_args()
    result = execute(args.run_id, args.output.resolve())
    print(
        json.dumps(
            {
                "status": result["status"],
                "outcome": (
                    result.get("outcome")
                    or result.get("classification", {}).get("primary_outcome_at_H")
                ),
                "result": str(args.output.resolve()),
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
