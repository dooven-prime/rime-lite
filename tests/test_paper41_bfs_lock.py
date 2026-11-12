"""Hostile checks for the downstream Paper XLI BFS source lock."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.release.verify_paper41_bfs_lock import (
    FILES,
    LOCK,
    PREFIX,
    audit_repository,
    validate_lock,
    validate_materialization,
)


def inputs() -> tuple[bytes, dict[str, bytes]]:
    return ((ROOT / LOCK).read_bytes(),
            {path: (ROOT / PREFIX / path).read_bytes() for path in FILES})


def must_reject(
    tagged_lock: bytes, tagged_files: dict[str, bytes],
    local_lock: bytes, local_files: dict[str, bytes], case: str,
) -> None:
    try:
        validate_materialization(tagged_lock, tagged_files, local_lock, local_files)
    except (KeyError, TypeError, ValueError):
        return
    raise AssertionError(f"BFS lock mutation accepted: {case}")


def test_tag_and_local_bytes() -> None:
    audit_repository()


def test_source_drift_with_unchanged_result() -> None:
    lock, files = inputs()
    altered = files.copy()
    altered[FILES[0]] += b"\n# changed implementation\n"
    must_reject(lock, files, lock, altered, "source drift with saved result unchanged")


def test_result_drift() -> None:
    lock, files = inputs()
    altered = files.copy()
    altered[FILES[1]] += b"\n"
    must_reject(lock, files, lock, altered, "saved result drift")


def test_missing_or_duplicate_source_binding() -> None:
    lock, files = inputs()
    record = json.loads(lock)
    record["files"][0] = record["files"][1].copy()
    try:
        validate_lock(json.dumps(record).encode(), files)
    except (KeyError, TypeError, ValueError):
        pass
    else:
        raise AssertionError("duplicate source binding accepted")
    record["files"].pop()
    try:
        validate_lock(json.dumps(record).encode(), files)
    except (KeyError, TypeError, ValueError):
        pass
    else:
        raise AssertionError("missing source binding accepted")


def test_rebound_lock_rejected() -> None:
    lock, files = inputs()
    altered = files.copy()
    altered[FILES[0]] += b"\n# changed implementation\n"
    record = json.loads(lock)
    record["files"][0]["sha256"] = hashlib.sha256(altered[FILES[0]]).hexdigest()
    record["files"][0]["size_bytes"] = len(altered[FILES[0]])
    must_reject(lock, files, json.dumps(record).encode(), altered,
                "source and lock rebound together")


if __name__ == "__main__":
    test_tag_and_local_bytes()
    test_source_drift_with_unchanged_result()
    test_result_drift()
    test_missing_or_duplicate_source_binding()
    test_rebound_lock_rejected()
    print("test_paper41_bfs_lock.py: OK")
