"""Copy only the hash-bound companion closure into a pristine owner worktree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from theorem_map import as_json, collect, require, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.worktree.resolve(strict=True)
    evidence = args.evidence.resolve(strict=True)
    data = collect(True)
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"], text=True)
    require(head == data["target_manuscript"]["source_commit"], "cold worktree is not the fixed manuscript source")
    require(not status, "cold worktree is not pristine before the source overlay")
    target = root/"experiments/proper_arc_registered_summaries/lean"
    require(not target.exists(), "cold companion destination already exists")
    files = dict(data["frozen_source_sha256"])
    for row in data["milestones"]:
        files[row["manifest"]] = row["manifest_sha256"]
        files[row["report"]] = row["report_sha256"]
    for name in ("theorem_map.py", "map_tests/test_theorem_map.py", "THEOREM_TO_SOURCE_MAP.md",
                 "theorem-to-source-map.v1.json", "README.md", "PROOF_PLAN.md",
                 "cold_replay/prepare.py", "cold_replay/run_replay.py"):
        files[name] = sha256(BASE/name)
    for name, expected in sorted(files.items()):
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts and ".lake" not in path.parts,
                f"invalid cold snapshot path: {name}")
        source = BASE/path
        require(not source.is_symlink() and sha256(source) == expected, f"cold source drift: {name}")
        destination = target/path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        require(sha256(destination) == expected, f"cold copy mismatch: {name}")
    require(not (target/".lake").exists(), "copied a warm project build")
    receipt = {
        "schema": "proper_arc_cold_source_snapshot.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(), "worktree": str(root),
        "lean_directory": str(target), "base_commit": head, "pre_overlay_git_status": status,
        "source_delivery": "LOCAL_HASH_BOUND_OVERLAY_NOT_A_PUBLIC_COMPANION_CONTENT_COMMIT",
        "fresh_project_build": True, "local_build_or_package_junction_copied": False,
        "source_sha256": dict(sorted(files.items())), "proof_input_count": data["unique_frozen_input_count"],
        "milestones": data["milestones"], "target_manuscript": data["target_manuscript"],
    }
    output = evidence/"source-snapshot.v1.json"
    require(not output.exists(), "cold source receipt already exists")
    output.write_text(as_json(receipt), encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS_COLD_SOURCE_SNAPSHOT", "files": len(files), "directory": str(target)}))


if __name__ == "__main__":
    raise SystemExit(main())
