"""Check the downstream cold-replay evidence closure without invoking Lean."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from theorem_map import collect, require, sha256


def read(path):
    return json.loads(path.read_text("utf-8"))


def verify(evidence):
    envelope = evidence / "evidence-manifest.v1.json"
    if envelope.exists():
        manifest = read(envelope)
        for name, digest in manifest["evidence_sha256"].items():
            path = Path(name)
            require(not path.is_absolute() and ".." not in path.parts, "nonlocal evidence path")
            require(sha256(evidence / path) == digest, f"evidence byte drift: {name}")
        for name, digest in manifest["harness_source_sha256"].items():
            path = Path(name)
            require(not path.is_absolute() and ".." not in path.parts, "nonlocal harness path")
            require(sha256(BASE / path) == digest, f"harness source drift: {name}")
    record = read(evidence / "cold-replay.v1.json")
    require(record["status"] == "PASS_ISOLATED_COLD_REPLAY_WITH_FRESH_OFFICIAL_MATHLIB_CACHE",
            "cold replay has not passed")
    snapshots = [path for path in evidence.glob("source-snapshot.v*.json")
                 if sha256(path) == record["source_snapshot_sha256"]]
    require(len(snapshots) == 1, "missing or ambiguous source snapshot")
    snapshot = read(snapshots[0])
    data = collect(False)
    require(snapshot["target_manuscript"] == data["target_manuscript"], "manuscript identity drift")
    for name, expected in data["frozen_source_sha256"].items():
        require(snapshot["source_sha256"].get(name) == expected, f"frozen snapshot mismatch: {name}")
    successful = {}
    for step in record["steps"]:
        name = Path(step["log"])
        require(name.name == step["log"], "nonlocal replay log")
        require(sha256(evidence / name) == step["log_sha256"], f"replay log drift: {name}")
        if step["exit_code"] == 0:
            successful[step["name"]] = step
    expected_validators = []
    for row in data["milestones"]:
        step = successful.get(row["id"] + "-validator")
        require(step is not None and step["command"][1:] == ["-B", row["validator"]],
                f"missing default owning-validator replay: {row['id']}")
        expected_validators.append({"id": row["id"], "status": "PASS",
            "manifest_sha256": row["manifest_sha256"], "report_sha256": row["report_sha256"],
            "target_count": row["target_count"]})
    require(record["validators"] == expected_validators, "validator/report identity drift")
    tests = 0
    for folder in ("tests", "interfaces/tests", "classification/tests", "chains/tests", "converse/tests",
                   "fibres/tests", "summary/tests", "counting/tests", "refinements/tests", "map_tests"):
        step = successful.get("tests-" + folder.replace("/", "-"))
        require(step is not None, f"missing test suite: {folder}")
        output = (evidence / step["log"]).read_text("utf-8")
        counts = re.findall(r"^Ran (\d+) tests? in", output, re.MULTILINE)
        require(len(counts) == 1 and re.search(r"^OK\s*$", output, re.MULTILINE),
                f"test result not successful: {folder}")
        tests += int(counts[0])
    require("final-theorem-map" in successful, "missing final map check")
    require(record["mapped_theorems"] == len(data["theorems"]), "mapped target drift")
    require(record["union_declaration_nodes"] == data["union_declaration_node_count"], "union size drift")
    require(record["union_graph_sha256"] == data["union_graph_sha256"], "union graph drift")
    require(record["pending_formalization"] == data["pending_formalization"], "formalization boundary drift")
    require(record["lock_sha256"] == sha256(BASE / "lake-manifest.json"), "Lake lock drift")
    lock = read(BASE / "lake-manifest.json")
    expected_packages = [{"name": p["name"], "url": p["url"], "head": p["rev"], "tracked_status": ""}
                         for p in lock["packages"]]
    require(record["packages"] == expected_packages, "dependency identity drift")
    require(record["lean_executable"] == data["lean_executable"], "Lean executable version drift")
    require(record["mathlib_cache_containers"] == ["master", "legacy"], "official cache scope changed")
    transfer = read(evidence / "toolchain-transfer.v1.json")
    require(transfer["sha256"] == record["toolchain"]["archive_sha256"], "toolchain transfer drift")
    require(record["dependency_mode"] == "official-cache" and not record["mathlib_source_rebuilt"],
            "dependency-mode boundary changed")
    require(record["source_delivery"] == snapshot["source_delivery"], "source delivery drift")
    bootstrap = sorted(evidence.glob("mathlib-archive-bootstrap.v*.json"))
    for receipt in bootstrap:
        recovery = read(receipt)
        for step in recovery["commands"]:
            name = Path(step["log"])
            require(name.name == step["log"] and sha256(evidence / name) == step["log_sha256"],
                    "source-bootstrap log drift")
    if bootstrap:
        completed = [read(path) for path in bootstrap if read(path)["status"] ==
                     "PASS_VERIFIED_FRESH_NETWORK_SOURCE_BOOTSTRAP"]
        require(len(completed) == 1, "missing or ambiguous successful source recovery")
        require(completed[0]["blob_content_matches_commit_tree"] and
                not completed[0]["local_object_or_build_cache_reused"], "source-recovery boundary changed")
    return {"status": "PASS_COLD_REPLAY_EVIDENCE_CLOSURE", "kernel_replayed_by_this_check": False,
            "validators": len(expected_validators), "unit_tests": tests,
            "mapped_theorems": record["mapped_theorems"],
            "union_declaration_nodes": record["union_declaration_nodes"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.evidence.resolve(strict=True))))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
