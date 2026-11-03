"""Build and audit the separate actual full-summary observer/count bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from validate_companion import ALLOWED_AXIOMS, lean_code, require, run_lake


FINITE = BASE / "milestones/finite-combinatorial-v1/manifest.json"
ANALYTIC = BASE / "analysis/milestones/wallis-ratio-v1/manifest.json"
DESTINATION = HERE / "milestones/full-summary-v1"
PROOFS = [HERE / (name + ".lean") for name in
          ("Observation", "Classification", "NullWitness", "Quotient", "CountBridge")]
TARGETS = ["FullSummary." + name for name in (
    "event_to_summary_prefix_detection", "equivalent_iff_normalForm",
    "fullQuotientEquivSummaries", "card_fullQuotient_closed", "forgetToFuture_surjective")]
EXTRA_DEFINITIONS = ["FullSummary." + name for name in (
    "fullQuotientEquivNormalForms", "registeredStatesEquivActualSummaries",
    "fullQuotientEquivSummaries", "forgetToFuture")]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def frozen_inputs() -> dict:
    finite = json.loads(FINITE.read_text("utf-8"))
    analytic = json.loads(ANALYTIC.read_text("utf-8"))
    for label, manifest in (("finite", finite), ("analytic", analytic)):
        for relative, expected in manifest["source_sha256"].items():
            require(sha256(BASE / relative) == expected, f"{label} frozen source drift: {relative}")
    require(sha256(FINITE.parent / "dependency-audit.json") == finite["report_sha256"], "finite report drift")
    require(sha256(ANALYTIC.parent / "dependency-audit.json") == analytic["report_sha256"], "analytic report drift")
    return finite


def owner_inputs(check_git: bool) -> dict:
    extension = json.loads((HERE / "owner-manifest.json").read_text("utf-8"))
    base = json.loads((BASE / "upstream-manifest.json").read_text("utf-8"))
    require(extension["commit"] == base["commit"], "different execution/count owner versions")
    mirror = HERE / extension["mirror_directory"]
    require({p.name for p in mirror.glob("*.lean")} == set(extension["sha256"]), "owner extension inventory drift")
    require("TotalCountFormula.lean" in extension["sha256"], "missing actual-summary count owner")
    known = set(base["sha256"])
    require({name + ".lean" for name in extension["compile_order"]} == set(extension["sha256"]),
            "owner compile order inventory drift")
    for name in extension["compile_order"]:
        file = name + ".lean"
        path = mirror / file
        require(sha256(path) == extension["sha256"][file], f"owner extension byte drift: {file}")
        for imported in re.findall(r"^import RegisteredAbsorptionChains\.(\w+)$",
                                   path.read_text("utf-8"), re.MULTILINE):
            require(imported + ".lean" in known, f"unbound or out-of-order owner dependency: {imported}")
        known.add(file)
        if check_git:
            ref = f'{extension["commit"]}:{extension["source_directory"]}/{file}'
            original = subprocess.check_output(["git", "-C", str(BASE.parents[2]), "show", ref])
            require(hashlib.sha256(original).hexdigest() == extension["sha256"][file],
                    f"owner commit mismatch: {file}")
    for path in PROOFS:
        for imported in re.findall(r"^import RegisteredAbsorptionChains\.(\w+)$",
                                   path.read_text("utf-8"), re.MULTILINE):
            require(imported + ".lean" in known, f"unbound observer count import: {imported}")
    return extension


def own_inputs(owner: dict) -> dict[str, str]:
    paths = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(),
             HERE / "tests/test_bridge_audit.py", HERE / "owner-manifest.json"]
    paths.extend(HERE / owner["mirror_directory"] / name for name in owner["sha256"])
    return {p.relative_to(BASE).as_posix(): sha256(p) for p in paths}


def declarations() -> list[str]:
    # Match the audit's stable alphabetical file order, not compilation order.
    return ["FullSummary." + m.group(1) for p in sorted(PROOFS)
            for m in re.finditer(r"^theorem\s+(\w+)", p.read_text("utf-8"), re.MULTILINE)] + EXTRA_DEFINITIONS


def check_report(output: str) -> dict:
    marker = "FULL_SUMMARY_JSON\n"
    require(output.count(marker) == 1, "missing or repeated full-summary report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "full_summary_dependency_audit.v1", "unknown full-summary schema")
    require([row["name"] for row in report["targets"]] == TARGETS, "full-summary target inventory drift")
    nodes = {row["name"]: row for row in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate dependency node")
    required = {
        TARGETS[1]: {"FullSummary.Equivalent", "FullSummary.output",
                     "FutureEvent.registerable_pair_separation"},
        TARGETS[2]: {"FullSummary.Equivalent", "FullSummary.output", "FullSummary.spoiledSeed_null",
                     "FullSummary.registeredStatesEquivActualSummaries"},
        TARGETS[3]: {"RegisteredAbsorptionChains.card_actualRegisteredSummaries_closed",
                     "RegisteredAbsorptionChains.actualSummaryFiniteParamsEquiv",
                     "RegisteredAbsorptionChains.actual_registered_origin_unique", TARGETS[2]},
        TARGETS[4]: {"FullSummary.equivalent_implies_future", "FullSummary.forgetToFuture"},
    }
    for row in report["targets"]:
        root = row["name"]
        require(row["signature"], f"empty signature: {root}")
        reached: set[str] = set()
        pending = [root]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            require(name in nodes, f"missing full-summary dependency node: {name}")
            reached.add(name)
            pending.extend(nodes[name]["direct_dependencies"])
        require(reached == set(row["dependencies"]), f"incomplete full-summary closure: {root}")
        axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(axioms == set(row["axioms"]) and axioms <= ALLOWED_AXIOMS,
                f"unexpected or inconsistent full-summary axioms: {root}")
        require(required.get(root, set()) <= reached, f"missing observer/actual-count bridge: {root}")
        require(not any(name.startswith("FutureEventAnalysis.") for name in reached),
                "an analytic result was imported into the finite bridge")
    signature = report["targets"][2]["signature"]
    require("ActualRegisteredSummaries" in signature and "RegisteredNonterminalPlacements" not in signature,
            "registered normal forms omit full summaries or terminal states")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "full-summary axiom audit inventory drift")
    source_audits = re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"), re.MULTILINE)
    require(source_audits == declarations(), "full-summary source audit inventory drift")
    for name, axioms in printed:
        require({a.strip() for a in axioms.split(",") if a.strip()} <= ALLOWED_AXIOMS,
                f"unapproved full-summary axiom: {name}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-owner-git", action="store_true")
    args = parser.parse_args()
    finite = frozen_inputs()
    owner = owner_inputs(args.check_owner_git)
    before = own_inputs(owner)
    for relative in before:
        if relative.endswith(".lean"):
            code = lean_code((BASE / relative).read_text("utf-8"))
            require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s", code, re.MULTILINE),
                    f"unfinished full-summary proof: {relative}")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only, "cannot freeze without a proof build/audit")
        require(not DESTINATION.exists(), "full-summary milestone already exists; use read-only replay")
        manifest = None
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "full-summary source byte drift")
        require(manifest["finite_manifest_sha256"] == sha256(FINITE), "finite milestone identity drift")
        require(manifest["preserved_analytic_manifest_sha256"] == sha256(ANALYTIC), "analytic milestone identity drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"), "full-summary report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_FULL_SUMMARY_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == finite["lean_executable"], "frozen Lean executable drift")
    run_lake(["build"])
    library = BASE / ".lake/build/lib/lean"
    (library / "full_summary").mkdir(parents=True, exist_ok=True)
    for name in owner["compile_order"]:
        run_lake(["env", "lean", "--root=" + str(HERE / "owner"),
                  "-o", str(library / "RegisteredAbsorptionChains" / (name + ".olean")),
                  str(HERE / owner["mirror_directory"] / (name + ".lean"))])
    for path in PROOFS:
        run_lake(["env", "lean", "-o", str(library / "full_summary" / (path.stem + ".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library / "FutureEvent/MilestoneAudit.olean"),
              str(BASE / "FutureEvent/MilestoneAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs(owner) == before, "full-summary inputs changed during replay")
    frozen_inputs()
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest = {
            "schema": "full_summary_bridge_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_FULL_SUMMARY_BRIDGE",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": finite["mathlib_commit"],
            "finite_manifest_sha256": sha256(FINITE),
            "preserved_analytic_manifest_sha256": sha256(ANALYTIC),
            "source_sha256": before, "owner_commit": owner["commit"],
            "target_declarations": TARGETS, "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "Actual all-word Moore full-summary quotient, registered-summary identity bridge, exact fixed-pair count, and canonical projection to the future quotient for n>=3",
            "excluded_scope": ["Full-summary 9/2 asymptotics", "Full/future quotient-ratio asymptotics", "Algorithms and reset bounds"],
            "replay_boundary": "Local kernel replay with pinned dependency caches; not a fresh-machine cold-replay claim",
        }
        manifest_path.write_text(as_json(manifest), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "full-summary dependency replay differs from freeze")
    print(json.dumps({"status": "PASS_FULL_SUMMARY_BRIDGE", "inputs": len(before),
                      "owner_extension_modules": len(owner["compile_order"]),
                      "axiom_checks": len(declarations()), "main_targets": len(TARGETS),
                      "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
