"""Replay the complete proper-arc origin classification and inherited proof closures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from validate_companion import ALLOWED_AXIOMS, as_json, check_inputs, lean_code, require, run_lake, sha256

PRESERVED = {
    "milestones/origin-realization-v1/manifest.json":
        "56769c0fa07686e5431de1f2b667eea8bd46619c979d1fe5d4e308e7c6d00c96",
    "interfaces/milestones/origin-interfaces-v1/manifest.json":
        "c3725a2407c2af450ad9c095abcbca89ba5cad13f1331d008c05e7134a2202f8",
}
PROOFS = [HERE / (name + ".lean") for name in ("SourceCut", "OriginTrace", "OriginExhaustive")]
UPSTREAM_TARGETS = ["ProperArc." + name for name in
                    ("run_local_unregistered", "run_originWord", "boundary_clean")]
TARGETS = ["ProperArc." + name for name in ("extract_first_registration", "sourceOrdered_registration_cut",
    "actual_registered_origin_unique", "actual_registered_origin_unique_nat",
    "actualRegistrationOriginsEquivCuts", "card_actualRegistrationOrigins")] + UPSTREAM_TARGETS
DESTINATION = HERE / "milestones/origin-classification-v1"


def preserved_inputs(check_git=False):
    for relative, expected in PRESERVED.items():
        path = BASE / relative
        require(sha256(path) == expected, f"preserved manifest drift: {relative}")
        manifest = json.loads(path.read_text("utf-8"))
        for source, sha in manifest["source_sha256"].items():
            require(sha256(BASE / source) == sha, f"preserved source drift: {source}")
        require(sha256(path.parent / "dependency-audit.json") == manifest["report_sha256"],
                f"preserved report drift: {relative}")
    check_inputs(check_git)


def own_inputs():
    paths = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(), HERE / "tests/test_classification_audit.py"]
    require(set(HERE.glob("*.lean")) == set(PROOFS) | {HERE / "AxiomAudit.lean"}, "classification source inventory drift")
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def declarations():
    names = ["ProperArc." + match.group(1) for path in PROOFS
             for match in re.finditer(r"^theorem\s+(\w+)", path.read_text("utf-8"), re.MULTILINE)]
    return names + ["ProperArc.actualRegistrationOriginsEquivCuts"] + UPSTREAM_TARGETS


def closure(nodes, root):
    reached = set()
    pending = [root]
    while pending:
        name = pending.pop()
        if name in reached:
            continue
        require(name in nodes, f"missing classification dependency node: {name}")
        reached.add(name)
        pending.extend(nodes[name]["direct_dependencies"])
    return reached


def check_report(output):
    marker = "ORIGIN_CLASSIFICATION_JSON\n"
    require(output.count(marker) == 1, "missing or repeated classification report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_origin_classification_audit.v1", "unknown classification report")
    require([row["name"] for row in report["targets"]] == TARGETS, "classification target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate classification dependency node")
    required = {
        TARGETS[0]: {"ProperArc.new_origin_step", "ProperArc.run_origin_of_some",
                     "RegisteredAbsorptionChains.stepDefect"},
        TARGETS[1]: {"ProperArc.ordered_port_addresses",
                     "RegisteredAbsorptionChains.SourceOrderLift.adjacent_port_fibers"},
        TARGETS[2]: {"ProperArc.actual_first_registration", "ProperArc.sourceOrdered_registration_cut",
                     "RegisteredAbsorptionChains.run_ordered", "RegisteredAbsorptionChains.ReachableExecution"},
        TARGETS[3]: {TARGETS[2], "ProperArc.originRecord_injective"},
        TARGETS[4]: {"ProperArc.ActualRegistrationOrigins", "ProperArc.originCutActual_surjective",
                     "ProperArc.actual_origin_in_cut_range", "ProperArc.run_originWord"},
        TARGETS[5]: {TARGETS[4]},
    }
    old_path = BASE / "interfaces/milestones/origin-interfaces-v1/dependency-audit.json"
    old_nodes = {node["name"]: node for node in json.loads(old_path.read_text("utf-8"))["nodes"]}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes, name)
        require(reached == set(target["dependencies"]), f"incomplete classification closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected classification axioms")
        require(target["signature"], f"empty classification signature: {name}")
        require(required.get(name, set()) <= reached, f"missing actual origin input: {name}")
        require("RegisteredAbsorptionChains.selectedPair" not in reached,
                "origin classification imported the fixed-pair specialization")
        if name in TARGETS[2:4]:
            require("ReachableExecution" in target["signature"], "generated history premise missing")
            require(not any(token in target["signature"] for token in ("CleanOutside", "SourceOrdered")),
                    "arbitrary registered history restricted by an extra admission premise")
        if name in UPSTREAM_TARGETS:
            expected = closure(old_nodes, name)
            require(reached == expected, f"upstream transitive closure differs from freeze: {name}")
            require(all(nodes[item] == old_nodes[item] for item in expected),
                    f"upstream declaration graph differs from freeze: {name}")
    definition = report["actual_origins_definition"]
    require(all(token in definition for token in ("run", "singletonExecution", "some")),
            "actual origin type does not retain a real seed history")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "classification axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"), re.MULTILINE)
            == declarations(), "classification source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved classification axiom: {name}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    preserved_inputs(args.check_upstream_git)
    before = own_inputs()
    for relative in before:
        if relative.endswith(".lean"):
            require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                    lean_code((BASE / relative).read_text("utf-8")), re.MULTILINE), "unfinished classification proof")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "classification freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "classification source drift")
        require(manifest["preserved_milestones"] == PRESERVED, "classification prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"), "classification report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_ORIGIN_CLASSIFICATION_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    version = run_lake(["env", "lean", "--version"]).strip()
    origin = json.loads((BASE / next(iter(PRESERVED))).read_text("utf-8"))
    require(version == origin["lean_executable"], "classification Lean executable drift")
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.FiberReachability"])
    library = BASE / ".lake/build/lib/lean"
    (library / "classification").mkdir(parents=True, exist_ok=True)
    for path in PROOFS:
        run_lake(["env", "lean", "-o", str(library / "classification" / (path.stem + ".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library / "AxiomAudit.olean"), str(BASE / "AxiomAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs() == before, "classification sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest = {
            "schema": "proper_arc_origin_classification_milestone.v1",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "target_manuscript": origin["target_manuscript"],
            "preserved_milestones": PRESERVED, "source_sha256": before,
            "target_declarations": TARGETS, "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "Proposition 3.1: actual first-registration extraction, exhaustive unique origin cut, actual-origin/Fin equivalence and exact origin cardinality",
            "remaining_scope": ["Proper-arc ternary chain decoder and actual chain bijection",
                "Actual placement fibers and dependent summary equivalence", "Total summary count and analytic layer"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }
        manifest_path.write_text(as_json(manifest), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")), "classification replay differs from freeze")
    print(json.dumps({"status": "PASS_ORIGIN_CLASSIFICATION", "inputs": len(before),
        "axiom_checks": len(declarations()), "targets": len(TARGETS),
        "explicit_upstream_closures": len(UPSTREAM_TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
