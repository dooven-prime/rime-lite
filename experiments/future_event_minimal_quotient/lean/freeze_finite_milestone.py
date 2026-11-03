"""Freeze once, or replay, the finite combinatorial proof milestone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from validate_companion import ALLOWED_AXIOMS, HERE, require, run_lake


DESTINATION = HERE / "milestones" / "finite-combinatorial-v1"
TARGETS = [
    "FutureEvent.registerablePlacementParamsEquiv",
    "FutureEvent.registeredPlacementParamsEquiv",
    "FutureEvent.card_actual_registerable_placements",
    "FutureEvent.card_actual_registered_placements_closed",
    "FutureEvent.card_futureQuotient_closed",
]
PARAMETERS = [
    "FutureEvent.RegisterableParam", "FutureEvent.RegisterableParams",
    "FutureEvent.RegisteredPlacementParam", "FutureEvent.RegisteredPlacementParams",
]
REQUIRED = {
    TARGETS[0]: {"FutureEvent.registerableNativeTarget_reachable",
                 "FutureEvent.registerableNativeTarget_covers_actual",
                 "FutureEvent.registerableNativeTarget_injective"},
    TARGETS[1]: {"FutureEvent.registeredParamTarget_reachable",
                 "FutureEvent.registeredParamTarget_covers_actual",
                 "FutureEvent.registeredParamTarget_injective"},
    TARGETS[4]: {"FutureEvent.futureEquivalent_iff_normalForm",
                 "FutureEvent.futureQuotientEquivNormalForms",
                 TARGETS[0], TARGETS[1]},
}
FORBIDDEN_PARAMETER_DEPENDENCIES = {
    "FutureEvent.PairGenerated", "FutureEvent.PairRegisterable",
    "FutureEvent.RegisteredNonterminal",
    "RegisteredAbsorptionChains.ReachableExecution",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def audit_result(output: str) -> dict:
    marker = "FINITE_MILESTONE_JSON\n"
    require(output.count(marker) == 1, "missing or repeated dependency report")
    payload = output.split(marker, 1)[1].splitlines()[0]
    report = json.loads(payload)
    require(report["schema"] == "future_event_finite_dependency_audit.v1", "unknown dependency schema")
    require([row["name"] for row in report["targets"]] == TARGETS, "target inventory drift")
    require([row["name"] for row in report["parameters"]] == PARAMETERS, "parameter inventory drift")
    nodes = {row["name"]: row for row in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate dependency node")
    for target in report["targets"]:
        name = target["name"]
        require(target["signature"], f"empty signature: {name}")
        require(set(target["axioms"]) <= ALLOWED_AXIOMS, f"unexpected axioms: {name}")
        reached: set[str] = set()
        pending = [name]
        while pending:
            node = pending.pop()
            if node in reached:
                continue
            require(node in nodes, f"missing dependency node: {node}")
            reached.add(node)
            pending.extend(nodes[node]["direct_dependencies"])
        require(reached == set(target["dependencies"]), f"incomplete dependency closure: {name}")
        actual_axioms = {node for node in reached if nodes[node]["kind"] == "axiom"}
        require(actual_axioms == set(target["axioms"]), f"axiom graph disagrees with Lean: {name}")
        require(REQUIRED.get(name, set()) <= reached, f"missing actual construction/classification: {name}")
    for parameter in report["parameters"]:
        require(not FORBIDDEN_PARAMETER_DEPENDENCIES.intersection(parameter["dependencies"]),
                f"reachability hidden in parameter input: {parameter['name']}")
    printed = re.findall(r"'([^']+)' depends on axioms:\s*\[([^]]*)\]", output)
    require([name for name, _ in printed] == TARGETS, "explicit axiom print inventory drift")
    for (name, axioms), target in zip(printed, report["targets"]):
        require({a.strip() for a in axioms.split(",")} == set(target["axioms"]),
                f"explicit axiom print disagrees with dependency report: {name}")
    return report


def proof_inputs() -> dict[str, str]:
    paths = [HERE / "FutureEvent.lean"]
    for folder in ("FutureEvent", "upstream"):
        paths.extend((HERE / folder).rglob("*.lean"))
    paths.extend(HERE / name for name in (
        "lean-toolchain", "lakefile.toml", "lake-manifest.json", "upstream-manifest.json",
        "validate_companion.py", "freeze_finite_milestone.py", "tests/test_source_lint.py"))
    return {p.relative_to(HERE).as_posix(): sha256(p) for p in sorted(paths)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="create an absent milestone; never overwrite")
    args = parser.parse_args()
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not DESTINATION.exists(), "milestone already exists; use read-only replay")
        manifest = None
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        for path, expected in manifest["source_sha256"].items():
            require(sha256(HERE / path) == expected, f"frozen proof byte drift: {path}")
    inputs_before = proof_inputs()
    version = run_lake(["env", "lean", "--version"]).strip()
    development = json.loads((HERE / "formalization-manifest.v1.json").read_text("utf-8"))
    require(development["lean_commit"] in version, "Lean version drift")
    run_lake(["build"])
    report = audit_result(run_lake(["env", "lean", "FutureEvent/MilestoneAudit.lean"]))
    require(proof_inputs() == inputs_before, "proof inputs changed during build/audit")
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(canonical_json(report), encoding="utf-8", newline="\n")
        repository_head = subprocess.check_output(
            ["git", "-C", str(HERE.parents[2]), "rev-parse", "HEAD"], text=True).strip()
        manifest = {
            "schema": "future_event_finite_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_PROOF_MILESTONE",
            "release_identity_claimed": False,
            "repository_head_at_freeze": repository_head,
            "source_is_committed_release": False,
            "lean_executable": version,
            "mathlib_commit": json.loads((HERE / "upstream-manifest.json").read_text("utf-8"))["mathlib_commit"],
            "target_manuscript": development["target_manuscript"],
            "scope": "Actual future-event classification, placement parameter equivalences and closed finite count for n>=3",
            "excluded_scope": ["Full-summary contract and count", "Asymptotics", "Extracted minimization algorithm"],
            "target_declarations": TARGETS,
            "parameter_declarations": PARAMETERS,
            "report_sha256": sha256(report_path),
            "source_sha256": inputs_before,
        }
        manifest_path.write_text(canonical_json(manifest), encoding="utf-8", newline="\n")
    else:
        report_path = DESTINATION / "dependency-audit.json"
        require(sha256(report_path) == manifest["report_sha256"], "frozen dependency report drift")
        require(report == json.loads(report_path.read_text("utf-8")), "dependency replay differs from freeze")
        require(version == manifest["lean_executable"], "frozen Lean executable drift")
    print(json.dumps({
        "status": "PASS_FINITE_COMBINATORIAL_MILESTONE",
        "source_files": len(manifest["source_sha256"]),
        "explicit_targets": len(TARGETS), "parameter_types": len(PARAMETERS),
        "dependency_nodes": len(report["nodes"]),
        "axioms": sorted({a for row in report["targets"] for a in row["axioms"]}),
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
