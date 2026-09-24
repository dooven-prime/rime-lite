#!/usr/bin/env python3
"""Replay the Paper XVI static audits in scratch and compare exact bytes."""

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
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
PACKAGE_ROOT = HERE.parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "source"
PROVENANCE_PATH = PACKAGE_ROOT / "upstream-provenance.v1.json"
DEFAULT_RECEIPT = PACKAGE_ROOT / "results" / "static-audits-replay.v1.receipt.json"

COMMANDS = (
    ("sectorization_field_audit.py", ()),
    ("path_lifting_audit.py", ("--full",)),
    ("path_lifting_audit.py", ("--full", "--sector-field", "somaSide")),
    ("path_lifting_depth3_audit.py", ("--full",)),
    ("path_lifting_depth3_audit.py", ("--full", "--sector-field", "somaSide")),
    ("sectorization_comparison_report.py", ()),
)

EXPECTED_OUTPUTS = (
    "path_lifting_audit_full_v3.json",
    "path_lifting_audit_full_v3_somaSide.json",
    "path_lifting_depth3_audit_full_v1.json",
    "path_lifting_depth3_audit_full_somaSide_v1.json",
    "sectorization_field_audit_v1.json",
    "sectorization_comparison_v1.json",
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


def package_versions() -> dict[str, str]:
    from importlib.metadata import version

    return {name: version(name) for name in EXPECTED_PACKAGES}


def check_runtime() -> dict[str, Any]:
    versions = package_versions()
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Python 3.12 required, got {platform.python_version()}")
    mismatches = {
        name: {"expected": expected, "actual": versions.get(name)}
        for name, expected in EXPECTED_PACKAGES.items()
        if versions.get(name) != expected
    }
    if mismatches:
        raise RuntimeError(f"static replay package mismatch: {mismatches}")
    return {
        "python": platform.python_version(),
        "executable": "<EXECUTION_PYTHON>/python.exe",
        "executable_sha256": sha256_file(Path(sys.executable).resolve()),
        "packages": versions,
    }


def bind_inputs(external_root: Path, scratch_data: Path) -> list[dict[str, Any]]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    scratch_data.mkdir(parents=True, exist_ok=True)
    bindings: list[dict[str, Any]] = []
    for item in provenance["exact_inputs"]:
        name = Path(item["path"]).name
        source = external_root / name
        if not source.is_file():
            raise FileNotFoundError(source)
        actual_size = source.stat().st_size
        actual_sha = sha256_file(source)
        if actual_size != item["size"] or actual_sha != item["sha256"]:
            raise ValueError(f"upstream input mismatch: {name}")
        target = scratch_data / name
        try:
            os.link(source, target)
            materialization = "hardlink"
        except OSError:
            shutil.copy2(source, target)
            materialization = "copy"
        bindings.append(
            {
                "name": name,
                "size": actual_size,
                "sha256": actual_sha,
                "scratch_materialization": materialization,
            }
        )
    return bindings


def replay(external_root: Path, scratch_parent: Path | None) -> dict[str, Any]:
    runtime = check_runtime()
    with tempfile.TemporaryDirectory(prefix="paper16-static-", dir=scratch_parent) as temp:
        scratch = Path(temp)
        source = scratch / "source"
        scripts = source / "scripts"
        results = source / "results"
        scripts.mkdir(parents=True)
        results.mkdir(parents=True)
        producer_bindings: list[dict[str, Any]] = []
        for name in sorted({name for name, _args in COMMANDS}):
            origin = SOURCE_ROOT / "scripts" / name
            target = scripts / name
            shutil.copy2(origin, target)
            producer_bindings.append({"path": f"source/scripts/{name}", "sha256": sha256_file(origin)})
        input_bindings = bind_inputs(external_root, source / "data")

        command_records: list[dict[str, Any]] = []
        for script, arguments in COMMANDS:
            command = [sys.executable, str(scripts / script), *arguments]
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
                    "script": script,
                    "arguments": list(arguments),
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
                    "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
                }
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"static replay failed: {script} {arguments}\n{completed.stderr[-4000:]}"
                )

        output_records: list[dict[str, Any]] = []
        for name in EXPECTED_OUTPUTS:
            generated = results / name
            canonical = SOURCE_ROOT / "results" / name
            if not generated.is_file() or not canonical.is_file():
                raise FileNotFoundError(name)
            generated_sha = sha256_file(generated)
            canonical_sha = sha256_file(canonical)
            output_records.append(
                {
                    "path": f"source/results/{name}",
                    "generated_size": generated.stat().st_size,
                    "canonical_size": canonical.stat().st_size,
                    "generated_sha256": generated_sha,
                    "canonical_sha256": canonical_sha,
                    "exact_bytes_equal": generated.read_bytes() == canonical.read_bytes(),
                }
            )

        all_equal = all(item["exact_bytes_equal"] for item in output_records)
        return {
            "schema": "rime.paper16.static-audits-replay-receipt.v1",
            "status": "PASS" if all_equal else "FAIL",
            "validation_mode": "PRODUCER_REPLAY_AND_EXACT_BYTE_COMPARISON",
            "producer_replay_performed": True,
            "independent_validation": False,
            "canonical_results_modified": False,
            "runtime": runtime,
            "input_bindings": input_bindings,
            "producer_bindings": producer_bindings,
            "commands": command_records,
            "outputs": output_records,
            "all_replayed_bytes_equal": all_equal,
            "receipt_in_own_closure": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-input-root", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    if args.scratch_root is not None:
        args.scratch_root.mkdir(parents=True, exist_ok=True)
    result = replay(args.external_input_root.resolve(), args.scratch_root)
    write_json(args.receipt.resolve(), result)
    print(json.dumps({"status": result["status"], "outputs": result["outputs"]}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
