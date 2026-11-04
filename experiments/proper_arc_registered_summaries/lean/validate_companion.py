"""Replay the first all-parameter proper-arc origin-realization milestone."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib

HERE = Path(__file__).resolve().parent
DESTINATION = HERE / "milestones/origin-realization-v1"
PROOFS = [HERE / "ProperArc" / (name + ".lean") for name in
          ("ArcGeometry", "LocalMerge", "OriginAssembly", "OriginBoundary")]
TARGETS = ["ProperArc." + name for name in ("originRecord_injective", "assemble_strict_parent",
          "run_originWord", "originPrefix_no_early_registration")]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def lean_code(source):
    result = list(source)
    i = 0
    while i < len(source):
        start = i
        if source.startswith("/-", i):
            depth = 1
            i += 2
            while i < len(source) and depth:
                if source.startswith("/-", i):
                    depth += 1
                    i += 2
                elif source.startswith("-/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
        elif source.startswith("--", i):
            while i < len(source) and source[i] != "\n":
                i += 1
        elif source[i] == '"':
            i += 1
            while i < len(source):
                if source[i] == "\\":
                    i += 2
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
        else:
            i += 1
            continue
        for k in range(start, min(i, len(source))):
            if result[k] not in "\r\n":
                result[k] = " "
    return "".join(result)


def check_inputs(check_git=False):
    manifest = json.loads((HERE / "upstream-manifest.json").read_text("utf-8"))
    require(manifest["schema"] == "proper_arc_lean_inputs.v1", "unknown input manifest")
    require(sha256(HERE / "lake-manifest.json") == manifest["lock_sha256"], "dependency lock drift")
    require({p.relative_to(HERE).as_posix() for p in (HERE / "upstream").rglob("*.lean")} ==
            set(manifest["sha256"]), "upstream inventory drift")
    for relative, expected in manifest["sha256"].items():
        require(sha256(HERE / relative) == expected, f"upstream byte drift: {relative}")
        if check_git:
            data = subprocess.check_output(["git", "-C", str(HERE.parents[2]), "show",
                f'{manifest["upstream_source_commit"]}:{manifest["upstream_source_directory"]}/{relative}'])
            require(hashlib.sha256(data).hexdigest() == expected, f"upstream Git mismatch: {relative}")
    paper = manifest["target_manuscript"]
    require(sha256(HERE / paper["reference_copy"]) == paper["sha256"], "manuscript byte drift")
    if check_git:
        data = subprocess.check_output(["git", "-C", str(HERE.parents[2]), "show",
                f'{paper["source_commit"]}:{paper["source_path"]}'])
        require(hashlib.sha256(data).hexdigest() == paper["sha256"], "manuscript Git mismatch")
    require((HERE / "lean-toolchain").read_text().strip() == manifest["lean_toolchain"], "Lean pin drift")
    config = tomllib.loads((HERE / "lakefile.toml").read_text("utf-8"))
    lock = json.loads((HERE / "lake-manifest.json").read_text("utf-8"))
    require(config["require"][0]["rev"] == manifest["mathlib_commit"], "Mathlib config drift")
    require(next(p for p in lock["packages"] if p["name"] == "mathlib")["rev"] ==
            manifest["mathlib_commit"], "Mathlib lock drift")
    require(lock["name"] == config["name"] == "proper_arc_registered_summaries", "root package mismatch")
    return manifest


def own_inputs(manifest):
    paths = [*PROOFS, HERE / "ProperArc.lean", HERE / "AxiomAudit.lean", HERE / "bootstrap_inputs.py",
             HERE / "validate_companion.py", HERE / "tests/test_audit.py", HERE / "upstream-manifest.json",
             HERE / "lean-toolchain", HERE / "lakefile.toml", HERE / "lake-manifest.json",
             HERE / manifest["target_manuscript"]["reference_copy"]]
    paths.extend(HERE / path for path in manifest["sha256"])
    require(set((HERE / "ProperArc").glob("*.lean")) == set(PROOFS), "own proof inventory drift")
    return {path.relative_to(HERE).as_posix(): sha256(path) for path in paths}


def declarations():
    return ["ProperArc." + match.group(1) for path in PROOFS
            for match in re.finditer(r"^theorem\s+(\w+)", path.read_text("utf-8"), re.MULTILINE)]


def check_report(output):
    marker = "PROPER_ARC_JSON\n"
    require(output.count(marker) == 1, "missing or repeated origin report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_origin_dependency_audit.v1", "unknown origin report")
    require([row["name"] for row in report["targets"]] == TARGETS, "origin target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate dependency node")
    actual = {"RegisteredAbsorptionChains.run", "RegisteredAbsorptionChains.stepDefect",
              "RegisteredAbsorptionChains.singletonExecution", "ProperArc.originWord",
              "ProperArc.originRecord", "ProperArc.boundaryPlacement", "ProperArc.assemble_strict_parent"}
    for index, target in enumerate(report["targets"]):
        root = target["name"]
        require(target["signature"], f"empty target signature: {root}")
        reached = set()
        pending = [root]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            require(name in nodes, f"missing dependency node: {name}")
            reached.add(name)
            pending.extend(nodes[name]["direct_dependencies"])
        require(reached == set(target["dependencies"]), f"incomplete dependency closure: {root}")
        axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS,
                f"unexpected or inconsistent origin axioms: {root}")
        require(not any(name.startswith(("FutureEvent.", "FullSummary.", "ObserverComparison."))
                        for name in reached), "observer theorem used as proper-arc proof")
        require("RegisteredAbsorptionChains.selectedPair" not in reached,
                "proper-arc theorem specialized to the old selected pair")
        if index == 2:
            require(actual <= reached, "missing actual origin-construction input")
            require("run" in target["signature"] and "originWord" in target["signature"] and
                    "ReachableExecution" not in target["signature"], "origin realization became conditional")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "axiom-audit inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"),
                       re.MULTILINE) == declarations(), "source axiom inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved axiom for {name}")
    return report


def run_lake(arguments):
    lake = os.environ.get("RIME_LAKE_EXE", "lake")
    result = subprocess.run([lake, "--no-cache", *arguments], cwd=HERE, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=1200)
    require(result.returncode == 0, result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    inputs = check_inputs(args.check_upstream_git)
    before = own_inputs(inputs)
    for path in before:
        if path.endswith(".lean"):
            require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                                  lean_code((HERE / path).read_text("utf-8")), re.MULTILINE),
                    f"unfinished proof or custom axiom: {path}")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only, "cannot freeze without kernel replay")
        require(not DESTINATION.exists(), "origin milestone exists; replay is read-only")
    else:
        frozen = json.loads(manifest_path.read_text("utf-8"))
        require(frozen["source_sha256"] == before, "origin milestone source drift")
        require(sha256(DESTINATION / "dependency-audit.json") == frozen["report_sha256"], "origin report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_ORIGIN_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    version = run_lake(["env", "lean", "--version"]).strip()
    require("4.33.0" in version and "d8b18978322de05a8f3dba51ef03cf5461676c17" in version,
            "Lean executable drift")
    run_lake(["build"])
    report = check_report(run_lake(["env", "lean", "AxiomAudit.lean"]))
    require(own_inputs(check_inputs(args.check_upstream_git)) == before, "input bytes changed during replay")
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        frozen = {
            "schema": "proper_arc_origin_realization_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_PARTIAL_PROPER_ARC_COMPANION",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": inputs["mathlib_commit"],
            "target_manuscript": inputs["target_manuscript"],
            "source_sha256": before, "target_declarations": TARGETS,
            "axiom_audit": declarations(), "report_sha256": sha256(report_path),
            "scope": "All legal n,c,r,t: explicit actual origin word, common clean boundary, distinct cut origins and no early registration",
            "remaining_scope": ["Converse origin classification", "Proper-arc actual code bijection",
                "Fixed-chain actual placement fibers", "Dependent summary equivalence and total count",
                "Generating functions and fixed-r asymptotics"],
            "replay_boundary": "Local Lean kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }
        manifest_path.write_text(as_json(frozen), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "origin dependency replay differs from freeze")
    print(json.dumps({"status": "PASS_PROPER_ARC_ORIGIN_MILESTONE", "inputs": len(before),
        "axiom_checks": len(declarations()), "targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
