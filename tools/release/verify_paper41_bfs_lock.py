"""Check Paper XLI's inherited BFS source before running its finite replay.

This downstream audit supplements the immutable v1.0 candidate. It checks
byte identity, not the mathematical correctness or independence of the replay.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
TAG = "paper41-v1.0"
TAG_OBJECT = "5a33bc162b32dc2d95d6bad337acf25dc3d298a4"
CONTENT_COMMIT = "24e09d3c6b27e744a0ee88d569e5f5fd6bf2226c"
PREFIX = "experiments/registered_absorption_chains/"
LOCK = PREFIX + "replay-lock.v1.json"
LOCK_SHA256 = "1c12bedb480a031968260200ce53867c00a414bee112ccff0baa09f98462d43e"
FILES = (
    "independent_bfs_check.py",
    "results/independent_bfs_n2_n7.v1.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True
    ).stdout


def validate_lock(lock_bytes: bytes, files: dict[str, bytes]) -> None:
    lock = json.loads(lock_bytes)
    require(lock["schema"] == "rime.registered-absorption-chains.replay-lock.v1",
            "replay-lock schema differs")
    require(lock["status"] == "BOUNDED_COMPUTATIONAL_CONSISTENCY_NOT_PROOF",
            "replay-lock evidence status differs")
    rows = lock["files"]
    require(isinstance(rows, list) and len(rows) == len(FILES),
            "replay-lock file count differs")
    require(all(isinstance(row, dict) and
                set(row) == {"path", "size_bytes", "sha256"} for row in rows),
            "replay-lock file fields differ")
    require([row["path"] for row in rows] == list(FILES),
            "replay-lock file paths/order differ")
    require(set(files) == set(FILES), "audited file set differs")
    for row in rows:
        path = row["path"]
        payload = files[path]
        require(row["size_bytes"] == len(payload), f"replay-lock size differs: {path}")
        require(row["sha256"] == digest(payload), f"replay-lock digest differs: {path}")


def validate_materialization(
    tagged_lock: bytes, tagged_files: dict[str, bytes],
    local_lock: bytes, local_files: dict[str, bytes],
) -> None:
    require(digest(tagged_lock) == LOCK_SHA256, "tagged replay lock differs")
    require(local_lock == tagged_lock, "local replay lock differs from release tag")
    validate_lock(tagged_lock, tagged_files)
    validate_lock(local_lock, local_files)


def audit_repository(root: Path = ROOT) -> None:
    tag_object = git(root, "show-ref", "--verify", "--hash", f"refs/tags/{TAG}").decode().strip()
    require(tag_object == TAG_OBJECT, "Paper XLI tag object differs")
    content_commit = git(root, "rev-parse", f"{TAG_OBJECT}^{{commit}}").decode().strip()
    require(content_commit == CONTENT_COMMIT, "Paper XLI content commit differs")

    tagged_lock = git(root, "show", f"{CONTENT_COMMIT}:{LOCK}")
    local_lock = (root / LOCK).read_bytes()
    tagged_files = {path: git(root, "show", f"{CONTENT_COMMIT}:{PREFIX}{path}")
                    for path in FILES}
    local_files = {path: (root / PREFIX / path).read_bytes() for path in FILES}
    validate_materialization(tagged_lock, tagged_files, local_lock, local_files)


if __name__ == "__main__":
    try:
        audit_repository()
        print("PASS Paper XLI post-release BFS lock: 2 tagged and local files")
    except (KeyError, OSError, TypeError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL Paper XLI post-release BFS lock: {error}") from error
