#!/usr/bin/env python3
"""Verify or replay the large MaleCNS v1 artifact closure in a scratch tree."""

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


ROOT = Path(__file__).resolve().parents[1]
CLOSURE_PATH = Path(__file__).with_name("large_artifact_closure.v1.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_closure_document(closure: dict) -> None:
    digest = closure.get("closure_sha256")
    body = {key: value for key, value in closure.items() if key != "closure_sha256"}
    if digest != canonical_digest(body):
        raise ValueError("large-artifact closure digest mismatch")
    requirements = ROOT / closure["runtime"]["requirements_path"]
    if sha256_file(requirements) != closure["runtime"]["requirements_sha256"]:
        raise ValueError("runtime requirements digest mismatch")


def installed_versions() -> dict[str, str]:
    versions = {"python": platform.python_version()}
    for module_name in ("numpy", "pandas", "pyarrow"):
        module = __import__(module_name)
        versions[module_name] = module.__version__
    return versions


def check_file_set(base: Path, entries: list[dict]) -> list[dict]:
    checks: list[dict] = []
    for entry in entries:
        path = base / entry["path"]
        actual_size = path.stat().st_size if path.is_file() else None
        actual_sha = sha256_file(path) if path.is_file() else None
        checks.append(
            {
                "path": entry["path"],
                "exists": path.is_file(),
                "size_matches": actual_size == entry["size"],
                "sha256_matches": actual_sha == entry["sha256"],
            }
        )
    return checks


def link_input(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
    except OSError:
        try:
            target.symlink_to(source)
        except OSError as error:
            raise RuntimeError(
                "external input cannot be hard-linked or symlinked into scratch; "
                "choose --scratch-root on the same volume"
            ) from error


def assert_environment(expected: dict) -> dict[str, str]:
    actual = installed_versions()
    errors: list[str] = []
    if not actual["python"].startswith(expected["python_prefix"]):
        errors.append(
            f"python expected {expected['python_prefix']}.*, found {actual['python']}"
        )
    for name, version in expected["packages"].items():
        if actual.get(name) != version:
            errors.append(f"{name} expected {version}, found {actual.get(name)}")
    if errors:
        raise RuntimeError("replay environment mismatch: " + "; ".join(errors))
    return actual


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def full_replay(
    closure: dict,
    external_input_root: Path,
    scratch_parent: Path,
    keep_scratch: bool,
    materialize_output_root: Path | None,
) -> dict:
    environment = assert_environment(closure["runtime"])
    replay_checks = check_file_set(ROOT, closure["replay_implementation"])
    if not all(
        item["exists"] and item["size_matches"] and item["sha256_matches"]
        for item in replay_checks
    ):
        raise ValueError("replay implementation closure mismatch")
    producer_checks = check_file_set(ROOT, closure["producers"])
    if not all(
        item["exists"] and item["size_matches"] and item["sha256_matches"]
        for item in producer_checks
    ):
        raise ValueError("producer closure mismatch")
    scratch_parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="malecns-replay-", dir=scratch_parent))
    clone = scratch / "male_cns_connectome"
    try:
        for entry in closure["producers"]:
            source = ROOT / entry["path"]
            target = clone / entry["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        for entry in closure["external_inputs"]:
            source = external_input_root / Path(entry["path"]).name
            if not source.is_file():
                raise FileNotFoundError(source)
            if source.stat().st_size != entry["size"] or sha256_file(source) != entry["sha256"]:
                raise ValueError(f"external input digest mismatch: {source.name}")
            link_input(source, clone / entry["path"])

        for command in sorted(closure["commands"], key=lambda item: item["order"]):
            run(
                [
                    sys.executable,
                    str(clone / command["script"]),
                    *command["arguments"],
                ],
                clone,
            )
        checks = check_file_set(clone, closure["outputs"])
        passed = all(
            item["exists"] and item["size_matches"] and item["sha256_matches"]
            for item in checks
        )
        if passed and materialize_output_root is not None:
            for entry in closure["outputs"]:
                source = clone / entry["path"]
                target = materialize_output_root / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        return {
            "status": "PASS" if passed else "FAIL",
            "mode": "CLEAN_CLONE_EXACT_BYTE_REPLAY",
            "closure_sha256": closure["closure_sha256"],
            "environment": environment,
            "outputs": checks,
            "producer_replay_performed": True,
            "historical_result_mutation": False,
            "outputs_materialized_after_verification": materialize_output_root
            is not None,
            "independent_validation": False,
            "scratch_retained": keep_scratch,
        }
    finally:
        if not keep_scratch:
            shutil.rmtree(scratch, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--external-input-root", type=Path, default=ROOT / "data")
    parser.add_argument("--scratch-root", type=Path, default=ROOT / ".replay-work")
    parser.add_argument("--keep-scratch", action="store_true")
    parser.add_argument("--materialize-output-root", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    closure = json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))
    validate_closure_document(closure)
    if args.replay:
        result = full_replay(
            closure,
            args.external_input_root.resolve(),
            args.scratch_root.resolve(),
            args.keep_scratch,
            args.materialize_output_root.resolve()
            if args.materialize_output_root
            else None,
        )
    else:
        input_checks = check_file_set(ROOT, closure["external_inputs"])
        replay_checks = check_file_set(ROOT, closure["replay_implementation"])
        producer_checks = check_file_set(ROOT, closure["producers"])
        output_checks = check_file_set(ROOT, closure["outputs"])
        all_checks = input_checks + replay_checks + producer_checks + output_checks
        passed = all(
            item["exists"] and item["size_matches"] and item["sha256_matches"]
            for item in all_checks
        )
        result = {
            "status": "PASS" if passed else "FAIL",
            "mode": "LOCAL_EXACT_BYTE_CLOSURE_PREFLIGHT",
            "closure_sha256": closure["closure_sha256"],
            "external_inputs": input_checks,
            "replay_implementation": replay_checks,
            "producers": producer_checks,
            "outputs": output_checks,
            "producer_replay_performed": False,
        }

    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
