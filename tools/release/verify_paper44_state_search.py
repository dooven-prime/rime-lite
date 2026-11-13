"""Audit a Paper XLIV control dependency omitted from the v1.0 manifest.

This is a post-release source binding, not part of the immutable candidate
closure or a new proof of the asymptotic results.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SUPPLEMENT = "docs/release-anchors/supplements/paper44-state-search-source.v1.json"
SOURCE = "experiments/paper44/controls/shortest_summary_search.py"
EXPECTED = {
    "schema": "rime.paper44.post-release-state-search-source.v1",
    "paper_id": "PAPER44",
    "release_role": "POST_RELEASE_SUPPLEMENT_NOT_IN_RELEASE_TAG",
    "release_tag": {
        "name": "paper44-v1.0",
        "tag_object_sha": "101e065cb1250030bb8d2b32aa9fced1c2645b05",
        "target_commit_sha": "15c1f4f510190a66b23f732b77a8273b85fd62dc",
    },
    "candidate_manifest": {
        "path": "experiments/paper44/release-manifest.json",
        "sha256_at_tag": "53624af64d94f1cb57f336f3ca7302abe69cd875c26b60ad742087207c51d30f",
    },
    "omitted_source": {
        "path": SOURCE,
        "sha256_at_tag": "415fe14f14820d7b27aa540f6e0a3606f19c7ea983c08fc06443a5fcd9fdc215",
        "size_at_tag": 11272,
    },
    "bound_callers": {
        "finite-minimizer": "experiments/paper44/controls/minimum_sufficient_quotient.py",
        "finite-spectrum-control": "experiments/paper44/controls/prefix_observer_spectrum_control.py",
        "finite-core": "experiments/paper44/controls/core.py",
    },
    "boundary": [
        "The state-search source exists in the immutable tag but was omitted from the original candidate artifact inventory.",
        "This downstream source lock checks the tagged bytes and current materialization; it does not retroactively repair the candidate manifest or prove the analytic results.",
    ],
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True).stdout


def tagged(path: str) -> bytes:
    return git("show", f"paper44-v1.0:{path}")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def check_record(record: dict) -> None:
    require(record == EXPECTED, "post-release source lock drift")


def check_source(source: bytes) -> None:
    expected = EXPECTED["omitted_source"]
    require(len(source) == expected["size_at_tag"] and
            sha256(source) == expected["sha256_at_tag"], "state-search source drift")
    tree = ast.parse(source)
    require(any(isinstance(node, ast.Import) and
                any(alias.name == "core" for alias in node.names)
                for node in tree.body), "state-search core import drift")


def check_caller(source: bytes, path: str) -> None:
    tree = ast.parse(source)
    require(any(isinstance(node, ast.Import) and
                any(alias.name == "shortest_summary_search" and alias.asname == "search"
                    for alias in node.names) for node in tree.body),
            f"state-search import drift: {path}")
    called = {node.func.attr for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and isinstance(node.func.value, ast.Name)
              and node.func.value.id == "search"}
    require({"bfs_distances", "successor"} <= called,
            f"state-search calls drift: {path}")


def audit() -> None:
    supplement = json.loads((ROOT / SUPPLEMENT).read_text(encoding="utf-8"))
    check_record(supplement)
    tag = EXPECTED["release_tag"]
    require(git("rev-parse", "refs/tags/paper44-v1.0").decode().strip() ==
            tag["tag_object_sha"], "tag object drift")
    require(git("rev-parse", "paper44-v1.0^{commit}").decode().strip() ==
            tag["target_commit_sha"], "tag target drift")
    try:
        tagged(SUPPLEMENT)
    except subprocess.CalledProcessError:
        pass
    else:
        raise ValueError("post-release supplement is present in the release tag")

    manifest_bytes = tagged(EXPECTED["candidate_manifest"]["path"])
    require(sha256(manifest_bytes) == EXPECTED["candidate_manifest"]["sha256_at_tag"],
            "tagged candidate manifest drift")
    rows = json.loads(manifest_bytes)["artifacts"]
    require(SOURCE not in {row["path"] for row in rows},
            "state-search source was already in candidate inventory")
    by_role = {row["role"]: row for row in rows}
    require(len(by_role) == len(rows), "duplicate candidate artifact role")

    source = tagged(SOURCE)
    check_source(source)
    require((ROOT / SOURCE).read_bytes() == source, "current state-search source differs from tag")
    for role, path in EXPECTED["bound_callers"].items():
        require(by_role.get(role, {}).get("path") == path, f"candidate caller missing: {role}")
        payload = tagged(path)
        require(sha256(payload) == by_role[role]["sha256"] and
                len(payload) == by_role[role]["size"], f"tagged caller drift: {role}")
        require((ROOT / path).read_bytes() == payload, f"current caller differs from tag: {role}")
        if role != "finite-core":
            check_caller(payload, path)
    print("PASS Paper XLIV post-release state-search source lock: tagged and local bytes")


if __name__ == "__main__":
    audit()
