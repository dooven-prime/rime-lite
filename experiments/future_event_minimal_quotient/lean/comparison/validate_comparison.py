"""Read-only replay of observer-growth proofs, preserving three frozen inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from validate_companion import ALLOWED_AXIOMS, lean_code, require, run_lake

PREREQUISITES = [
    BASE / "milestones/finite-combinatorial-v1/manifest.json",
    BASE / "analysis/milestones/wallis-ratio-v1/manifest.json",
    BASE / "full_summary/milestones/full-summary-v1/manifest.json",
]
DESTINATION = HERE / "milestones/observer-growth-v1"
PROOFS = [HERE / (name + ".lean") for name in ("SummarySeries", "ObserverGrowth")]
TARGETS = ["ObserverComparison." + name for name in (
    "summaryBracket_error", "tendsto_fullQuotient_normalized",
    "tendsto_full_div_future_normalized", "tendsto_full_div_future_atTop")]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def preserved_inputs() -> dict[str, str]:
    identities = {}
    for path in PREREQUISITES:
        manifest = json.loads(path.read_text("utf-8"))
        for relative, expected in manifest["source_sha256"].items():
            require(sha256(BASE / relative) == expected, f"preserved source drift: {relative}")
        require(sha256(path.parent / "dependency-audit.json") == manifest["report_sha256"],
                f"preserved report drift: {path}")
        identities[path.relative_to(BASE).as_posix()] = sha256(path)
    return identities


def own_inputs() -> dict[str, str]:
    paths = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(),
             HERE / "tests/test_comparison_audit.py"]
    require({p.name for p in HERE.glob("*.lean")} == {p.name for p in paths if p.suffix == ".lean"},
            "comparison Lean inventory drift")
    return {p.relative_to(BASE).as_posix(): sha256(p) for p in paths}


def declarations() -> list[str]:
    return ["ObserverComparison." + match.group(1) for path in PROOFS
            for match in re.finditer(r"^theorem\s+(\w+)", path.read_text("utf-8"), re.MULTILINE)]


def check_report(output: str) -> dict:
    marker = "OBSERVER_COMPARISON_JSON\n"
    require(output.count(marker) == 1, "missing or repeated comparison report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "observer_comparison_dependency_audit.v1", "unknown comparison schema")
    require([row["name"] for row in report["targets"]] == TARGETS, "comparison target inventory drift")
    nodes = {row["name"]: row for row in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate comparison dependency node")
    full_inputs = {"ObserverComparison.fullCardReal", "FullSummary.FullQuotient",
                   "FullSummary.card_fullQuotient_closed", "FullSummary.fullQuotientEquivSummaries",
                   "RegisteredAbsorptionChains.card_actualRegisteredSummaries_closed",
                   "RegisteredAbsorptionChains.actual_registered_origin_unique",
                   "ObserverComparison.tendsto_summaryBracket_normalized"}
    future_inputs = {"FutureEventAnalysis.futureCardReal", "FutureEvent.FutureQuotient",
                     "FutureEventAnalysis.tendsto_futureQuotient_normalized",
                     "FutureEvent.card_futureQuotient_closed",
                     "Real.Wallis.tendsto_W_nhds_pi_div_two"}
    for index, target in enumerate(report["targets"]):
        root = target["name"]
        require(target["signature"], f"empty comparison signature: {root}")
        reached: set[str] = set()
        pending = [root]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            require(name in nodes, f"missing comparison dependency node: {name}")
            reached.add(name)
            pending.extend(nodes[name]["direct_dependencies"])
        require(reached == set(target["dependencies"]), f"incomplete comparison closure: {root}")
        axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS,
                f"unexpected or inconsistent comparison axioms: {root}")
        if index == 0:
            require(not any(name.startswith(("FullSummary.", "FutureEvent.",
                        "RegisteredAbsorptionChains.", "FutureEventAnalysis.")) for name in reached),
                    "pure series bound depends on a model theorem")
        else:
            require(full_inputs <= reached, f"missing actual full-observer/count input: {root}")
            require("fullCardReal" in target["signature"], f"full count is a proxy: {root}")
        if index >= 2:
            require(future_inputs <= reached, f"missing actual future-observer/Wallis input: {root}")
            require("futureCardReal" in target["signature"], f"future count is a proxy: {root}")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "comparison axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"),
                       re.MULTILINE) == declarations(), "comparison source audit inventory drift")
    for name, axioms in printed:
        require({a.strip() for a in axioms.split(",") if a.strip()} <= ALLOWED_AXIOMS,
                f"unapproved comparison axiom: {name}")
    return report


def compile_inputs() -> str:
    finite = json.loads(PREREQUISITES[0].read_text("utf-8"))
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == finite["lean_executable"], "frozen Lean executable drift")
    run_lake(["build"])
    library = BASE / ".lake/build/lib/lean"
    # Rebuild bound proof inputs, rather than trusting stale extension oleans.
    owner = json.loads((BASE / "full_summary/owner-manifest.json").read_text("utf-8"))
    for name in owner["compile_order"]:
        run_lake(["env", "lean", "--root=" + str(BASE / "full_summary/owner"), "-o",
                  str(library / "RegisteredAbsorptionChains" / (name + ".olean")),
                  str(BASE / "full_summary" / owner["mirror_directory"] / (name + ".lean"))])
    for folder, names in (
        ("full_summary", ("Observation", "Classification", "NullWitness", "Quotient", "CountBridge")),
        ("analysis", ("WallisAsymptotics", "FutureCountAsymptotics")),
        ("comparison", ("SummarySeries", "ObserverGrowth")),
    ):
        (library / folder).mkdir(parents=True, exist_ok=True)
        for name in names:
            run_lake(["env", "lean", "-o", str(library / folder / (name + ".olean")),
                      str(BASE / folder / (name + ".lean"))])
    run_lake(["env", "lean", "-o", str(library / "FutureEvent/MilestoneAudit.olean"),
              str(BASE / "FutureEvent/MilestoneAudit.lean")])
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    preserved = preserved_inputs()
    before = own_inputs()
    for path in [*PROOFS, HERE / "AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                              lean_code(path.read_text("utf-8")), re.MULTILINE),
                f"unfinished comparison proof or custom axiom: {path.name}")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only, "cannot freeze without a kernel replay")
        require(not DESTINATION.exists(), "comparison milestone already exists; replay is read-only")
        manifest = None
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["schema"] == "observer_growth_milestone.v1", "unknown comparison milestone")
        require(manifest["source_sha256"] == before, "comparison source byte drift")
        require(manifest["preserved_milestones"] == preserved, "preserved milestone identity drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"),
                "comparison report byte drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_COMPARISON_SOURCE_ONLY", "inputs": len(before),
                          "preserved_milestones": len(preserved)}))
        return 0
    version = compile_inputs()
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs() == before, "comparison inputs changed during replay")
    require(preserved_inputs() == preserved, "preserved milestones changed during replay")
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        finite = json.loads(PREREQUISITES[0].read_text("utf-8"))
        manifest = {
            "schema": "observer_growth_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_OBSERVER_COMPARISON_MILESTONE",
            "release_identity_claimed": False,
            "hal_v1_proof_identity_changed": False,
            "lean_executable": version,
            "mathlib_commit": finite["mathlib_commit"],
            "preserved_milestones": preserved,
            "source_sha256": before,
            "target_declarations": TARGETS,
            "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "Negative-binomial error bound; actual full-summary 9/2 limit; actual full/future asymptotic ratio and divergence, on n=m+3",
            "excluded_scope": ["Reset-word or generic memory lower bounds", "Changes to frozen finite, Wallis or full-summary bridge sources", "HAL v1 proof identity"],
            "replay_boundary": "Local kernel replay using pinned cached dependencies, not a fresh-machine cold replay",
        }
        manifest_path.write_text(as_json(manifest), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "comparison dependency replay differs from freeze")
    print(json.dumps({"status": "PASS_OBSERVER_GROWTH_MILESTONE", "inputs": len(before),
                      "preserved_milestones": len(preserved), "axiom_checks": len(declarations()),
                      "main_targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
