"""Acquire isolated dependencies, then replay all nine immutable owning validators."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from theorem_map import as_json, collect, require, sha256


def utc():
    return datetime.now(timezone.utc).isoformat()


def verify_snapshot(snapshot):
    require(Path(snapshot["lean_directory"]).resolve() == BASE, "wrong cold snapshot directory")
    for name, expected in snapshot["source_sha256"].items():
        require(sha256(BASE/name) == expected, f"cold source byte drift: {name}")


def package_states(lock, env):
    result = []
    for package in lock["packages"]:
        root = BASE/lock["packagesDir"]/package["name"]
        require(root.is_dir() and not root.is_symlink() and not root.is_junction(),
                f"shared or missing dependency directory: {package['name']}")
        head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, env=env).strip()
        require(head == package["rev"], f"dependency revision drift: {package['name']}")
        require(not (root/".git/objects/info/alternates").exists(), "shared Git object dependency")
        status = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=no"], text=True, env=env)
        require(not status, f"modified dependency sources: {package['name']}")
        result.append({"name": package["name"], "url": package["url"], "head": head, "tracked_status": status})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, help="explicit source-snapshot revision; default is v1")
    parser.add_argument("--dependency-mode", choices=("official-cache", "source"), default="official-cache")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    evidence = args.evidence.resolve(strict=True)
    runtime = args.toolchain.resolve(strict=True)
    archive = args.archive.resolve(strict=True)
    snapshot_path = args.snapshot.resolve(strict=True) if args.snapshot else evidence/"source-snapshot.v1.json"
    snapshot = json.loads(snapshot_path.read_text("utf-8"))
    verify_snapshot(snapshot)
    receipt_path = evidence/"cold-replay.v1.json"
    outer = evidence.parent
    scratch = outer/"isolated-caches"
    lake = runtime/"bin/lake.exe"
    lean = runtime/"bin/lean.exe"
    require(lake.is_file() and lean.is_file(), "fresh toolchain binaries missing")
    lock = json.loads((BASE/"lake-manifest.json").read_text("utf-8"))
    lock_sha = sha256(BASE/"lake-manifest.json")
    toolchain_identity = {"directory": str(runtime), "archive_sha256": sha256(archive),
        "archive_bytes": archive.stat().st_size, "lean_exe_sha256": sha256(lean), "lake_exe_sha256": sha256(lake),
        "archive_url": "https://github.com/leanprover/lean4/releases/download/v4.33.0/lean-4.33.0-windows.zip",
        "publisher_asset_digest_verified": False}
    if args.resume:
        record = json.loads(receipt_path.read_text("utf-8"))
        require(record["toolchain"] == toolchain_identity, "resume toolchain drift")
        require(record["source_snapshot_sha256"] == sha256(snapshot_path), "resume source snapshot drift")
        require(record["dependency_mode"] == args.dependency_mode, "resume dependency mode drift")
        if "error" in record:
            record.setdefault("previous_failures", []).append({"error": record.pop("error"), "updated_utc": record["updated_utc"]})
    else:
        require(not receipt_path.exists() and not scratch.exists() and not (BASE/".lake").exists(),
                "cold start already contains build or download artifacts")
        record = {"schema": "proper_arc_isolated_cold_replay.v1", "status": "RUNNING", "started_utc": utc(),
            "source_snapshot_sha256": sha256(snapshot_path), "source_delivery": snapshot["source_delivery"],
            "toolchain": toolchain_identity, "dependency_mode": args.dependency_mode,
            "initial_project_build_absent": True, "initial_isolated_caches_absent": True,
            "same_host_separate_environment": True, "mathlib_source_rebuilt": args.dependency_mode == "source",
            "lock_sha256": lock_sha, "python": sys.version, "platform": platform.platform(), "steps": []}
    scratch.mkdir(exist_ok=True)
    config = scratch/"gitconfig"
    if not config.exists():
        config.write_text("[core]\n\tautocrlf = false\n\tlongpaths = true\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("LEAN_", "LAKE_", "ELAN_", "MATHLIB_", "GIT_"))}
    env.update({"PATH": str(runtime/"bin")+os.pathsep+os.environ["PATH"], "RIME_LAKE_EXE": str(lake),
        "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1",
        "LAKE_CACHE_DIR": str(scratch/"lake"), "LAKE_ARTIFACT_CACHE": "false",
        "ELAN_HOME": str(scratch/"elan"), "XDG_CACHE_HOME": str(scratch/"xdg"),
        "MATHLIB_CACHE_DIR": str(scratch/"mathlib"), "MATHLIB_NO_CACHE_ON_UPDATE": "1",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(config)})

    def save():
        record["updated_utc"] = utc()
        receipt_path.write_text(as_json(record), encoding="utf-8", newline="\n")

    def run(name, command, timeout=1800):
        previous = next((step for step in reversed(record["steps"]) if step["name"] == name and step["exit_code"] == 0), None)
        if previous is not None:
            require(previous["command"] == command and sha256(evidence/previous["log"]) == previous["log_sha256"],
                    f"resume command/log drift: {name}")
            return (evidence/previous["log"]).read_text("utf-8")
        number = len(record["steps"])+1
        log = evidence/f"{number:02d}-{name}.log"
        require(not log.exists(), "refuse to overwrite a replay log")
        print(f"RUN {name}", flush=True)
        started = time.monotonic()
        with log.open("w", encoding="utf-8", newline="\n") as output:
            try:
                result = subprocess.run(command, cwd=BASE, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = -1
                output.write("\nCOLD_REPLAY_TIMEOUT\n")
        record["steps"].append({"name": name, "command": command, "exit_code": code,
            "seconds": time.monotonic()-started, "log": log.name, "log_sha256": sha256(log)})
        save()
        require(code == 0, f"cold replay step failed: {name}; see {log}")
        print(f"PASS {name}", flush=True)
        return log.read_text("utf-8")

    try:
        record["status"] = "RUNNING"
        save()
        lean_version = run("lean-version", [str(lean), "--version"]).strip()
        data = collect(True)
        require(lean_version == data["lean_executable"], "fresh Lean does not match the frozen version")
        record["lean_executable"] = lean_version
        run("lake-version", [str(lake), "--version"])
        for package in lock["packages"]:
            root = BASE/lock["packagesDir"]/package["name"]
            root.parent.mkdir(parents=True, exist_ok=True)
            name = package["name"]
            run("init-"+name, ["git", "init", str(root)])
            run("origin-"+name, ["git", "-C", str(root), "remote", "add", "origin", package["url"]])
            run("fetch-"+name, ["git", "-C", str(root), "fetch", "--depth", "1", "origin", package["rev"]], timeout=3600)
            run("checkout-"+name, ["git", "-C", str(root), "checkout", "--detach", package["rev"]])
        record["dependency_acquisition"] = "FRESH_NETWORK_SHALLOW_FETCH_AT_EACH_LOCKED_SHA_NO_LOCAL_OBJECT_REUSE"
        run("fetch-locked-dependencies", [str(lake), "--no-cache", "env", "lean", "--version"], timeout=3600)
        require(sha256(BASE/"lake-manifest.json") == lock_sha, "dependency acquisition changed the frozen lock")
        record["packages"] = package_states(lock, env)
        if args.dependency_mode == "official-cache":
            imports = set()
            for name in snapshot["source_sha256"]:
                if name.endswith(".lean"):
                    imports.update(re.findall(r"^import\s+(Mathlib\.[\w.]+)", (BASE/name).read_text("utf-8"), re.MULTILINE))
            record["mathlib_cache_modules"] = sorted(imports)
            record["mathlib_cache_containers"] = ["master", "legacy"]
            run("fresh-official-mathlib-cache", [str(lake), "--no-cache", "exe", "cache", "get",
                "--cache-from=master,legacy", "--repo=leanprover-community/mathlib4", *sorted(imports)], timeout=7200)
        record["packages"] = package_states(lock, env)
        save()
        validators = []
        for row in data["milestones"]:
            run(row["id"]+"-validator", [sys.executable, "-B", row["validator"]], timeout=7200)
            validators.append({"id": row["id"], "status": "PASS", "manifest_sha256": row["manifest_sha256"],
                "report_sha256": row["report_sha256"], "target_count": row["target_count"]})
            record["validators"] = validators
            save()
        for folder in ("tests", "interfaces/tests", "classification/tests", "chains/tests", "converse/tests",
                       "fibres/tests", "summary/tests", "counting/tests", "refinements/tests", "map_tests"):
            run("tests-"+folder.replace("/", "-"), [sys.executable, "-B", "-m", "unittest", "discover",
                "-s", folder, "-p", "test_*.py", "-v"])
        run("final-theorem-map", [sys.executable, "-B", "theorem_map.py", "--check-upstream-git"])
        verify_snapshot(snapshot)
        record["packages"] = package_states(lock, env)
        require(sha256(BASE/"lake-manifest.json") == lock_sha, "final lock drift")
        record["status"] = "PASS_ISOLATED_COLD_REPLAY_WITH_FRESH_OFFICIAL_MATHLIB_CACHE" if args.dependency_mode == "official-cache" else "PASS_ISOLATED_SOURCE_BUILD_COLD_REPLAY"
        record["finished_utc"] = utc()
        record["mapped_theorems"] = len(data["theorems"])
        record["union_declaration_nodes"] = data["union_declaration_node_count"]
        record["union_graph_sha256"] = data["union_graph_sha256"]
        record["pending_formalization"] = data["pending_formalization"]
        save()
        print(json.dumps({"status": record["status"], "validators": len(validators), "receipt": str(receipt_path)}))
    except Exception as error:
        record["status"] = "FAILED"
        record["error"] = str(error)
        save()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
