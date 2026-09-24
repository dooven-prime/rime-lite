#!/usr/bin/env python3
"""Replay the Paper XVI v0.1-v0.2 dynamic-descent artifacts in scratch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
PACKAGE_ROOT = HERE.parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "source"
DEFAULT_RECEIPT = PACKAGE_ROOT / "results" / "dynamic-descent-replay.v1.receipt.json"

COMMANDS = (
    ("digital_fly_v0_1/scripts/run_sd1_operator_admission.py", ()),
    ("digital_fly_v0_1/scripts/run_sd1_dynamics.py", ()),
    ("digital_fly_v0_1/scripts/run_o1_observation_resolution.py", ()),
    ("digital_fly_v0_2/scripts/run_d2_1_markov_closure.py", ()),
    ("digital_fly_v0_2/scripts/run_d2_2_memory_closure.py", ()),
    ("digital_fly_v0_2/scripts/run_d2_3_partition_comparison.py", ()),
)

EXPECTED_OUTPUTS = (
    "digital_fly_v0_1/results/sd1_operator_admission_v0_1.json",
    "digital_fly_v0_1/results/sd1_dynamics_v0_1.json",
    "digital_fly_v0_1/results/o1_observation_resolution_v0_1.json",
    "digital_fly_v0_2/results/d2_1_markov_closure_v0_2.json",
    "digital_fly_v0_2/results/d2_2_memory_closure_v0_2.json",
    "digital_fly_v0_2/results/d2_3_partition_comparison_v0_2.json",
)

CARRIER_FILES = (
    "carrier_v0_edges.npz",
    "carrier_v0_manifest.json",
    "carrier_v0_nodes.parquet",
)

EXPECTED_PACKAGES = {
    "numpy": "2.5.3",
    "pandas": "3.0.5",
    "scipy": "1.18.1",
    "pyarrow": "25.0.1",
    "networkx": "3.6.1",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_runtime() -> dict[str, Any]:
    versions = {name: version(name) for name in EXPECTED_PACKAGES}
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, got {platform.python_version()}")
    mismatches = {
        name: {"expected": expected, "actual": versions.get(name)}
        for name, expected in EXPECTED_PACKAGES.items()
        if versions.get(name) != expected
    }
    if mismatches:
        raise RuntimeError(f"dynamic replay package mismatch: {mismatches}")
    return {
        "python": platform.python_version(),
        "executable": "<EXECUTION_PYTHON>/python.exe",
        "executable_sha256": sha256_file(Path(sys.executable).resolve()),
        "packages": versions,
    }


def materialize(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        shutil.copy2(source, target)
        return "copy"


def replay(scratch_parent: Path | None) -> dict[str, Any]:
    runtime = check_runtime()
    with tempfile.TemporaryDirectory(prefix="paper16-dynamic-", dir=scratch_parent) as temp:
        scratch = Path(temp)
        scratch_source = scratch / "source"
        producer_bindings: list[dict[str, Any]] = []
        for relative, _arguments in COMMANDS:
            origin = SOURCE_ROOT / relative
            target = scratch_source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, target)
            producer_bindings.append({"path": f"source/{relative}", "sha256": sha256_file(origin)})

        carrier_bindings: list[dict[str, Any]] = []
        for name in CARRIER_FILES:
            origin = SOURCE_ROOT / "digital_fly_v0" / "results" / name
            if not origin.is_file():
                raise FileNotFoundError(origin)
            target = scratch_source / "digital_fly_v0" / "results" / name
            mode = materialize(origin, target)
            carrier_bindings.append(
                {
                    "path": f"source/digital_fly_v0/results/{name}",
                    "size": origin.stat().st_size,
                    "sha256": sha256_file(origin),
                    "scratch_materialization": mode,
                }
            )

        for directory in ("digital_fly_v0_1/results", "digital_fly_v0_2/results"):
            (scratch_source / directory).mkdir(parents=True, exist_ok=True)

        command_records: list[dict[str, Any]] = []
        for relative, arguments in COMMANDS:
            command = [sys.executable, str(scratch_source / relative), *arguments]
            completed = subprocess.run(
                command,
                cwd=scratch,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            command_records.append(
                {
                    "script": relative,
                    "arguments": list(arguments),
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
                    "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
                }
            )
            if completed.returncode != 0:
                raise RuntimeError(f"dynamic replay failed: {relative}\n{completed.stderr[-4000:]}")

        output_records: list[dict[str, Any]] = []
        for relative in EXPECTED_OUTPUTS:
            generated = scratch_source / relative
            canonical = SOURCE_ROOT / relative
            if not generated.is_file() or not canonical.is_file():
                raise FileNotFoundError(relative)
            generated_sha = sha256_file(generated)
            canonical_sha = sha256_file(canonical)
            output_records.append(
                {
                    "path": f"source/{relative}",
                    "generated_size": generated.stat().st_size,
                    "canonical_size": canonical.stat().st_size,
                    "generated_sha256": generated_sha,
                    "canonical_sha256": canonical_sha,
                    "exact_bytes_equal": generated.read_bytes() == canonical.read_bytes(),
                }
            )

        all_equal = all(item["exact_bytes_equal"] for item in output_records)
        return {
            "schema": "rime.paper16.dynamic-descent-replay-receipt.v1",
            "status": "PASS" if all_equal else "FAIL",
            "validation_mode": "PRODUCER_REPLAY_AND_EXACT_BYTE_COMPARISON",
            "producer_replay_performed": True,
            "independent_validation": False,
            "canonical_results_modified": False,
            "runtime": runtime,
            "carrier_bindings": carrier_bindings,
            "producer_bindings": producer_bindings,
            "commands": command_records,
            "outputs": output_records,
            "all_replayed_bytes_equal": all_equal,
            "receipt_in_own_closure": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    if args.scratch_root is not None:
        args.scratch_root.mkdir(parents=True, exist_ok=True)
    result = replay(args.scratch_root)
    write_json(args.receipt.resolve(), result)
    print(json.dumps({"status": result["status"], "outputs": result["outputs"]}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
