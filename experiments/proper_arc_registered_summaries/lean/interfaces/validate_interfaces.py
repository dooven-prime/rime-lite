"""Audit named consumer interfaces without rewriting the origin proof freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from validate_companion import ALLOWED_AXIOMS, check_inputs, lean_code, require, run_lake, sha256, as_json

ORIGIN = BASE / "milestones/origin-realization-v1/manifest.json"
ORIGIN_SHA256 = "56769c0fa07686e5431de1f2b667eea8bd46619c979d1fe5d4e308e7c6d00c96"
DESTINATION = HERE / "milestones/origin-interfaces-v1"
TARGETS = ["ProperArc." + name for name in ("localLetters_fuse_adjacent",
    "originCut_reaches_common_boundary", "originWords_same_boundary", "originWord_clean")]


def preserved_inputs():
    require(sha256(ORIGIN) == ORIGIN_SHA256, "origin manifest identity drift")
    manifest = json.loads(ORIGIN.read_text("utf-8"))
    for path, expected in manifest["source_sha256"].items():
        require(sha256(BASE / path) == expected, f"frozen origin source drift: {path}")
    require(sha256(ORIGIN.parent / "dependency-audit.json") == manifest["report_sha256"], "origin report drift")
    check_inputs()


def own_inputs():
    paths = [HERE / "OriginInterfaces.lean", HERE / "AxiomAudit.lean", Path(__file__).resolve(),
             HERE / "tests/test_interfaces_audit.py"]
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def declarations():
    return ["ProperArc." + name for name in re.findall(r"^theorem (\w+)",
            (HERE / "OriginInterfaces.lean").read_text("utf-8"), re.MULTILINE)]


def check_report(output):
    marker = "ORIGIN_INTERFACES_JSON\n"
    require(output.count(marker) == 1, "missing or repeated interface report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_origin_interfaces_audit.v1", "unknown interface report")
    require([t["name"] for t in report["targets"]] == TARGETS, "interface target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate interface dependency node")
    for index, target in enumerate(report["targets"]):
        root = target["name"]
        reached = set()
        pending = [root]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            require(name in nodes, f"missing interface dependency node: {name}")
            reached.add(name)
            pending.extend(nodes[name]["direct_dependencies"])
        require(reached == set(target["dependencies"]), f"incomplete interface closure: {root}")
        axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected interface axioms")
        require(target["signature"], f"empty interface signature: {root}")
        if index == 0:
            require("ProperArc.run_local_unregistered" in reached, "missing true local fusion input")
            require("RegisteredAbsorptionChains.run_localLetters_safe" not in reached,
                    "fusion interface replaced by empty-port routing")
        else:
            require({"ProperArc.run_originWord", "ProperArc.originWord",
                     "RegisteredAbsorptionChains.run", "RegisteredAbsorptionChains.singletonExecution"} <= reached,
                    "missing explicit actual origin witness")
        require("RegisteredAbsorptionChains.selectedPair" not in reached, "interface specialized to old pair")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "interface axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"), re.MULTILINE)
            == declarations(), "interface source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved interface axiom: {name}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    preserved_inputs()
    before = own_inputs()
    for relative in before:
        if relative.endswith(".lean"):
            require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                lean_code((BASE / relative).read_text("utf-8")), re.MULTILINE), "unfinished interface proof")
    destination = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "interface freeze exists or no kernel replay")
    else:
        manifest = json.loads(destination.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "interface source drift")
        require(manifest["origin_manifest_sha256"] == ORIGIN_SHA256, "interface prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"), "interface report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_ORIGIN_INTERFACES_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    version = run_lake(["env", "lean", "--version"]).strip()
    origin = json.loads(ORIGIN.read_text("utf-8"))
    require(version == origin["lean_executable"], "interface Lean executable drift")
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.CleanChainWitness"])
    library = BASE / ".lake/build/lib/lean"
    (library / "interfaces").mkdir(parents=True, exist_ok=True)
    run_lake(["env", "lean", "-o", str(library / "interfaces/OriginInterfaces.olean"),
              str(HERE / "OriginInterfaces.lean")])
    run_lake(["env", "lean", "-o", str(library / "AxiomAudit.olean"), str(BASE / "AxiomAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs() == before, "interface source changed during replay")
    preserved_inputs()
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest = {
            "schema": "proper_arc_origin_interfaces_milestone.v1",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "origin_manifest_sha256": ORIGIN_SHA256,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "source_sha256": before, "report_sha256": sha256(report_path),
            "target_declarations": TARGETS, "axiom_audit": declarations(),
            "scope": "Derived true-fusion, explicit existence, common-boundary and clean/reachable APIs",
            "converse_origin_classification_proved": False,
        }
        destination.write_text(as_json(manifest), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")), "interface replay drift")
    print(json.dumps({"status": "PASS_ORIGIN_INTERFACES", "inputs": len(before),
                      "axiom_checks": len(declarations()), "targets": len(TARGETS),
                      "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
