#!/usr/bin/env python3
"""Replay Paper XVI A1/A2 producers and compare their exact output bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
PACKAGE_ROOT = HERE.parents[1]
REPO_ROOT = HERE.parents[3]
MALE_ROOT = PACKAGE_ROOT / "source"
RECEIPT_PATH = PACKAGE_ROOT / "results" / "a1-a2-exact-replay.v1.receipt.json"

REPLAYS = (
    {
        "id": "A1_EXACT_SIGNED_ROUTE_AUDIT",
        "producer": MALE_ROOT / "followups" / "run_y_known_pm_route_audit.py",
        "registration": MALE_ROOT
        / "followups"
        / "y_known_pm_route_audit.registration-v1.2.json",
        "canonical": MALE_ROOT
        / "followups"
        / "results"
        / "y_known_pm_route_audit.v1.json",
    },
    {
        "id": "A2_NAMED_SECTOR_FOLLOWUP",
        "producer": MALE_ROOT / "followups" / "run_d2_2_named_sector_followup.py",
        "registration": MALE_ROOT
        / "followups"
        / "d2_2_named_sector_followup.registration-v1.1.json",
        "canonical": MALE_ROOT
        / "followups"
        / "results"
        / "d2_2_named_sector_followup.v1.json",
    },
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def run_replay() -> tuple[dict[str, Any], bool]:
    failures: list[str] = []
    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="paper16-exact-replay-") as directory:
        scratch_root = Path(directory)
        for index, spec in enumerate(REPLAYS, start=1):
            producer = spec["producer"]
            registration = spec["registration"]
            canonical = spec["canonical"]
            scratch = scratch_root / f"replay-{index}.json"
            command = [sys.executable, str(producer), "--output", str(scratch)]
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            exists = scratch.is_file()
            byte_equal = exists and scratch.read_bytes() == canonical.read_bytes()
            if completed.returncode != 0:
                failures.append(f"{spec['id']}: producer exited {completed.returncode}")
            if not exists:
                failures.append(f"{spec['id']}: replay output missing")
            elif not byte_equal:
                failures.append(f"{spec['id']}: replay bytes differ from canonical result")
            records.append(
                {
                    "id": spec["id"],
                    "producer": {
                        "path": relative(producer),
                        "sha256": sha256_file(producer),
                    },
                    "registration": {
                        "path": relative(registration),
                        "sha256": sha256_file(registration),
                    },
                    "canonical_result": {
                        "path": relative(canonical),
                        "size": canonical.stat().st_size,
                        "sha256": sha256_file(canonical),
                    },
                    "replay_result": {
                        "exists": exists,
                        "size": scratch.stat().st_size if exists else None,
                        "sha256": sha256_file(scratch) if exists else None,
                    },
                    "exit_code": completed.returncode,
                    "exact_byte_equal": byte_equal,
                }
            )

    closure = [
        {
            "role": "REPLAY_IMPLEMENTATION",
            "path": relative(HERE),
            "sha256": sha256_file(HERE),
        }
    ]
    for record in records:
        closure.extend(
            (
                {"role": "PRODUCER", **record["producer"]},
                {"role": "REGISTRATION", **record["registration"]},
                {"role": "CANONICAL_RESULT", **record["canonical_result"]},
            )
        )
    receipt = {
        "schema": "rime.paper16.a1-a2-exact-producer-replay.v1",
        "status": "PASS" if not failures else "FAIL",
        "validation_mode": "PRODUCER_REPLAY_AND_EXACT_BYTE_COMPARISON",
        "independent_validation": False,
        "producer_replay_performed": True,
        "execution_python": {
            "version": sys.version.split()[0],
            "path": f"<EXECUTION_PYTHON>/{Path(sys.executable).name}",
            "sha256": sha256_file(Path(sys.executable)),
        },
        "replays": records,
        "all_replayed_bytes_equal": bool(records)
        and all(record["exact_byte_equal"] for record in records),
        "ordered_closure": closure,
        "closure_sha256": canonical_sha256(closure),
        "receipt_in_own_closure": False,
        "failures": failures,
        "claim_boundary": (
            "clean scratch producer replay and exact-byte comparison; not independent "
            "scientific validation and not a biological claim"
        ),
    }
    return receipt, not failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt, passed = run_replay()
    if args.write_receipt:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
