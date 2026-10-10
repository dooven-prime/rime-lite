#!/usr/bin/env python3
"""Run the frozen MTS-1 producer under fail-closed process-tree caps."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any

import psutil


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
PRODUCER = ROOT / "source_addressed_mechanism_producer_v1.py"
AUTHORITY_SCHEMA = "rime.exploratory.male-cns.mts-source-addressed-execution-authority.v1"
AUTHORITY_VALUE = "MTS1_SOURCE_ADDRESSED_PRODUCER_V1_ONLY"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_relative(value: object, label: str) -> PurePosixPath:
    require(isinstance(value, str) and value != "", f"{label} must be a path")
    require("\\" not in value and ":" not in value, f"{label} is not portable")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"{label} escapes its root")
    return path


def _repo_path(value: object, label: str) -> Path:
    relative = _safe_relative(value, label)
    path = (REPO_ROOT / Path(*relative.parts)).resolve()
    require(path.is_relative_to(REPO_ROOT.resolve()), f"{label} escapes checkout")
    return path


def _verify_artifact(entry: dict[str, Any], role: str) -> Path:
    require(entry.get("role") == role, f"authority role mismatch: {role}")
    path = _repo_path(entry["path"], role)
    require(path.is_file() and path.stat().st_size == entry["bytes"], f"authority artifact size mismatch: {role}")
    require(sha256_file(path) == entry["sha256"], f"authority artifact digest mismatch: {role}")
    return path


def _tree_metrics(process: psutil.Process) -> tuple[Decimal, int]:
    processes = [process]
    try:
        processes.extend(process.children(recursive=True))
    except psutil.Error:
        pass
    cpu_seconds = Decimal(0)
    rss = 0
    for item in processes:
        try:
            times = item.cpu_times()
            cpu_seconds += Decimal(str(times.user)) + Decimal(str(times.system))
            rss += int(item.memory_info().rss)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return cpu_seconds, rss


def _tree_bytes(paths: list[Path]) -> int:
    total = 0
    for root in paths:
        if root.is_file():
            total += root.stat().st_size
        elif root.is_dir():
            for path in root.rglob("*"):
                if path.is_file():
                    total += path.stat().st_size
    return total


def _write_json(path: Path, value: object) -> None:
    require(not path.exists(), f"refusing to replace resource receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def execute(authority_path: Path) -> dict[str, Any]:
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    require(authority.get("schema") == AUTHORITY_SCHEMA, "execution authority schema mismatch")
    require(
        authority.get("status") == "AUTHORIZED"
        and authority.get("execution_authority") == AUTHORITY_VALUE,
        "MTS-1 capped execution is not authorized",
    )
    require(authority.get("scientific_payload_generated") is False, "authority is not pre-execution")
    artifacts = authority["artifacts"]
    contract_path = _verify_artifact(artifacts["RESOURCE_CONTRACT"], "RESOURCE_CONTRACT")
    wrapper_path = _verify_artifact(artifacts["CAPPED_EXECUTION_WRAPPER"], "CAPPED_EXECUTION_WRAPPER")
    require(wrapper_path == Path(__file__).resolve(), "authorized wrapper differs from executing bytes")
    producer_path = _verify_artifact(artifacts["SOURCE_ADDRESSED_PRODUCER"], "SOURCE_ADDRESSED_PRODUCER")
    require(producer_path == PRODUCER.resolve(), "authorized producer path drift")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    require(contract["caps"]["max_source_workers"] == 1, "resource contract does not authorize sequential execution")
    caps = contract["caps"]
    cpu_cap_seconds = Decimal(caps["cpu_core_hours"]) * Decimal(3600)
    wall_cap_seconds = Decimal(caps["monotonic_wall_hours"]) * Decimal(3600)
    rss_cap_bytes = Decimal(caps["process_tree_rss_gib"]) * Decimal(1024**3)
    disk_cap_bytes = Decimal(caps["incremental_result_storage_gib"]) * Decimal(1024**3)
    final_root = _repo_path(authority["result_root"], "result_root")
    require(final_root.is_relative_to((ROOT / "results").resolve()), "result root is not MTS-1-owned")
    staging_root = final_root.with_name(final_root.name + ".staging")
    require(not final_root.exists() and not staging_root.exists(), "result or staging root already exists")
    runtime_root = ROOT / ".runtime-work/capped-execution" / final_root.name
    require(not runtime_root.exists(), "runtime log root already exists")
    runtime_root.mkdir(parents=True)
    stdout_path = runtime_root / "producer.stdout.log"
    stderr_path = runtime_root / "producer.stderr.log"
    start = time.monotonic()
    peak_rss = 0
    peak_disk = 0
    peak_cpu = Decimal(0)
    failure: str | None = None
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(PRODUCER), "--authority", str(authority_path)],
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
        )
        observed = psutil.Process(process.pid)
        while process.poll() is None:
            cpu_seconds, rss = _tree_metrics(observed)
            wall_seconds = Decimal(str(time.monotonic() - start))
            disk_bytes = _tree_bytes([final_root, staging_root])
            peak_cpu = max(peak_cpu, cpu_seconds)
            peak_rss = max(peak_rss, rss)
            peak_disk = max(peak_disk, disk_bytes)
            if cpu_seconds > cpu_cap_seconds:
                failure = "CPU_CORE_HOUR_CAP_EXCEEDED"
            elif wall_seconds > wall_cap_seconds:
                failure = "MONOTONIC_WALL_CAP_EXCEEDED"
            elif Decimal(rss) > rss_cap_bytes:
                failure = "PROCESS_TREE_RSS_CAP_EXCEEDED"
            elif Decimal(disk_bytes) > disk_cap_bytes:
                failure = "INCREMENTAL_STORAGE_CAP_EXCEEDED"
            if failure:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=30)
                break
            time.sleep(5)
        return_code = process.wait()
    wall_seconds = Decimal(str(time.monotonic() - start))
    disk_bytes = _tree_bytes([final_root, staging_root])
    peak_disk = max(peak_disk, disk_bytes)
    if failure is None and wall_seconds > wall_cap_seconds:
        failure = "MONOTONIC_WALL_CAP_EXCEEDED"
    if failure is None and Decimal(disk_bytes) > disk_cap_bytes:
        failure = "INCREMENTAL_STORAGE_CAP_EXCEEDED"
    status = "PASS" if failure is None and return_code == 0 else "UNRESOLVED"
    receipt = {
        "schema": "rime.exploratory.male-cns.mts-capped-execution-receipt.v1",
        "status": status,
        "failure": failure if failure is not None else (None if return_code == 0 else "PRODUCER_FAILED"),
        "producer_return_code": return_code,
        "caps": caps,
        "observed": {
            "cpu_core_hours_peak_sampled": format(peak_cpu / Decimal(3600), "f"),
            "monotonic_wall_hours": format(wall_seconds / Decimal(3600), "f"),
            "process_tree_rss_gib_peak_sampled": format(Decimal(peak_rss) / Decimal(1024**3), "f"),
            "incremental_result_storage_gib_peak_sampled": format(Decimal(peak_disk) / Decimal(1024**3), "f"),
        },
        "surface_policy": {
            "source_dropped": False,
            "cohort_dropped": False,
            "pair_dropped": False,
            "adaptive_smaller_surface_retry": False,
            "max_source_workers": 1,
        },
        "result_promoted": final_root.is_dir(),
        "failed_staging_retained": status == "UNRESOLVED" and staging_root.exists(),
        "runtime_logs_are_package_artifacts": False,
    }
    if status == "PASS":
        require(final_root.is_dir() and not staging_root.exists(), "producer did not atomically promote complete result")
        receipt_path = final_root / "resource-execution-receipt.json"
    else:
        receipt_path = ROOT / "results" / f"{final_root.name}.resource-unresolved.json"
    _write_json(receipt_path, receipt)
    if status != "PASS":
        raise RuntimeError(json.dumps(receipt, sort_keys=True))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.authority.resolve()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
