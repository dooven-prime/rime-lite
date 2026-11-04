"""Replay proper-arc Theorem 6.1 from actual summaries and dependent fibres."""

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
from classification.validate_classification import closure, PROOFS as ORIGIN_PROOFS
from chains.validate_chains import PROOFS as CHAIN_PROOFS
from converse.validate_converse import PROOFS as CONVERSE_PROOFS
from fibres.validate_fibres import PROOFS as FIBRE_PROOFS
from summary.validate_summary import PRESERVED as SUMMARY_INPUTS, PROOFS as SUMMARY_PROOFS

PRESERVED = dict(SUMMARY_INPUTS, **{
    "summary/milestones/dependent-summary-v1/manifest.json":
        "aef536f33efdd1b114e87f9b96ffdce1ddceec94c9a41d10b572f092a38b95a6"})
PROOFS = [HERE/(name+".lean") for name in ("LastCheckpointCount", "SummaryCardinality")]
PREFIX = "ProperArc.Chains."
UPSTREAM = [PREFIX+name for name in ("actualRegisteredSummariesEquivParams",
    "card_actualCodePlacements", "codePlacementFibreEquiv", "outsideCount_eq")]
TARGETS = [PREFIX+name for name in ("card_summary_sigma", "card_codes_by_last_checkpoint",
    "card_code_fibre", "card_code_fibre_full", "card_code_fibre_sum",
    "card_actual_registered_summaries", "card_actual_registered_summaries_short_complement",
    "sum_codes_by_last_checkpoint")]+UPSTREAM
EXTRA = [PREFIX+"codeSnocEquiv"]
DESTINATION = HERE/"milestones/summary-count-v1"


def preserved_inputs(check_git=False):
    for relative, expected in PRESERVED.items():
        path = BASE/relative
        require(sha256(path) == expected, f"preserved manifest drift: {relative}")
        manifest = json.loads(path.read_text("utf-8"))
        for source, sha in manifest["source_sha256"].items():
            require(sha256(BASE/source) == sha, f"preserved source drift: {source}")
        require(sha256(path.parent/"dependency-audit.json") == manifest["report_sha256"],
                f"preserved report drift: {relative}")
    check_inputs(check_git)


def own_inputs():
    paths = [*PROOFS, HERE/"AxiomAudit.lean", Path(__file__).resolve(), HERE/"tests/test_counting_audit.py"]
    require(set(HERE.glob("*.lean")) == set(PROOFS)|{HERE/"AxiomAudit.lean"}, "counting source inventory drift")
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def declarations():
    return [PREFIX+match.group(1) for path in PROOFS for match in
            re.finditer(r"^theorem\s+([\w.]+)", path.read_text("utf-8"), re.MULTILINE)]+EXTRA+UPSTREAM


def check_report(output):
    marker = "SUMMARY_COUNT_JSON\n"
    require(output.count(marker) == 1, "missing or repeated counting report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_summary_count_audit.v1", "unknown counting report")
    require(report["scope_status"] == "ACTUAL_REGISTERED_SUMMARY_COUNT", "counting scope drift")
    require([row["name"] for row in report["targets"]] == TARGETS, "counting target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate counting dependency node")
    required = {
        TARGETS[0]: {PREFIX+"actualRegisteredSummariesEquivParams", PREFIX+"ActualRegisteredSummaries",
                     PREFIX+"SummaryParams", "Nat.card_sigma", PREFIX+"codeFiberParams_finite"},
        TARGETS[1]: {PREFIX+"sum_codes_by_last_checkpoint", PREFIX+"lastCheckpoint"},
        TARGETS[2]: {PREFIX+"codePlacementFibreEquiv", PREFIX+"card_actualCodePlacements", PREFIX+"outsideCount_eq"},
        TARGETS[3]: {PREFIX+"card_code_fibre"},
        TARGETS[4]: {PREFIX+"sum_codes_by_last_checkpoint", PREFIX+"card_code_fibre", PREFIX+"sum_range_shift_Icc"},
        TARGETS[5]: {PREFIX+"card_summary_sigma", PREFIX+"card_code_fibre_sum",
                     PREFIX+"actualRegisteredSummariesEquivParams", PREFIX+"card_actualCodePlacements"},
        TARGETS[6]: {PREFIX+"card_actual_registered_summaries"},
        TARGETS[7]: {PREFIX+"codeSnocEquiv", PREFIX+"lastCheckpoint_snoc", "RegisteredAbsorptionChains.card_code"},
    }
    previous_paths = {
        "summary": "summary/milestones/dependent-summary-v1/dependency-audit.json",
        "fibre": "fibres/milestones/placement-fibre-v1/dependency-audit.json"}
    previous = {key: {node["name"]: node for node in json.loads((BASE/path).read_text("utf-8"))["nodes"]}
                for key, path in previous_paths.items()}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes, name)
        require(reached == set(target["dependencies"]), f"incomplete counting closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected counting axioms")
        require(required.get(name, set()) <= reached, f"missing actual counting input: {name}")
        require(not any(item.startswith(("RegisteredAbsorptionChains.card_actualRegisteredSummaries",
            "RegisteredAbsorptionChains.card_actual_registered_summaries", "FutureEvent.")) for item in reached),
            "fixed-pair total or future-observer count substituted for proper-arc enumeration")
        require(target["signature"], f"empty counting signature: {name}")
        if name in UPSTREAM:
            old = previous["summary" if name == UPSTREAM[0] else "fibre"]
            inherited = closure(old, name)
            require(reached == inherited and all(nodes[item] == old[item] for item in inherited),
                    f"inherited counting graph drift: {name}")
    definitions = report["definitions"]
    domain = definitions[PREFIX+"ActualRegisteredSummaries"]
    require(all(token in domain for token in ("run", "singletonExecution", "isSome")),
            "actual counting domain lost registered seed history")
    require(not any(token in domain for token in ("decodeSummary", "SummaryParams", "CleanOutside")),
            "actual counting domain restricted to constructed states")
    params = definitions[PREFIX+"SummaryParams"]
    require(all(token in params for token in ("Fin", "r - 1", "Code", "n - r", "CodeFiberParams")),
            "dependent counting parameter family drift")
    require(not any(token in params for token in ("Reachable", "run ", "ActualRegisteredSummaries")),
            "counting parameters assume actual reachability")
    branch = definitions[PREFIX+"CodeFiberParams"]
    require(all(token in branch for token in ("outsideCount", "0", "ZMod", "FiberParams")),
            "counting lost independent full-carrier phase branch")
    for index in (0, 5, 6):
        signature = " ".join(report["targets"][index]["signature"].split())
        require(re.search(r"Nat\.card \((?:ProperArc\.Chains\.)?ActualRegisteredSummaries c (?:r|\(n - 1\))\) =", signature),
                "counting interface lost actual summary left side")
    signature = report["targets"][5]["signature"]
    require(all(token in signature for token in ("2 ≤ r", "r < n", "r - 1", "choose", "Icc", "3 ^")),
            "Theorem 6.1 formula or proper-arc domain drift")
    boundary = report["targets"][6]["signature"]
    require(all(token in boundary for token in ("3 ≤ n", "n - 1", "n - 2", "n + 1")),
            "short-complement regression interface drift")
    full = report["targets"][3]["signature"]
    require("lastCheckpoint" in full and "= n" in full, "full-carrier checkpoint endpoint missing")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "counting axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE/"AxiomAudit.lean").read_text("utf-8"), re.MULTILINE) == declarations(),
            "counting source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved counting axiom: {name}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    preserved_inputs(args.check_upstream_git)
    before = own_inputs()
    for path in [*PROOFS, HERE/"AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s", lean_code(path.read_text("utf-8")), re.MULTILINE),
                f"unfinished counting proof: {path.name}")
    manifest_path = DESTINATION/"manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "counting freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "counting source drift")
        require(manifest["preserved_milestones"] == PRESERVED, "counting prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION/"dependency-audit.json"), "counting report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_SUMMARY_COUNT_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    origin = json.loads((BASE/next(iter(PRESERVED))).read_text("utf-8"))
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == origin["lean_executable"], "counting Lean executable drift")
    print("REPLAY frozen origin library", flush=True)
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.FiberParamInverse"])
    library = BASE/".lake/build/lib/lean"
    layers = (("classification", ORIGIN_PROOFS), ("chains", CHAIN_PROOFS),
              ("converse", CONVERSE_PROOFS), ("fibres", FIBRE_PROOFS),
              ("summary", SUMMARY_PROOFS), ("counting", PROOFS))
    for folder, paths in layers:
        (library/folder).mkdir(parents=True, exist_ok=True)
        print(f"REPLAY {folder}", flush=True)
        for path in paths:
            run_lake(["env", "lean", "-o", str(library/folder/(path.stem+".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library/"AxiomAudit.olean"), str(BASE/"AxiomAudit.lean")])
    print("AUDIT Theorem 6.1 and transitive declaration dependencies", flush=True)
    report = check_report(run_lake(["env", "lean", str(HERE/"AxiomAudit.lean")]))
    require(own_inputs() == before, "counting sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION/"dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest_path.write_text(as_json({
            "schema": "proper_arc_summary_count_milestone.v1", "scope_status": "ACTUAL_REGISTERED_SUMMARY_COUNT",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "target_manuscript": origin["target_manuscript"], "preserved_milestones": PRESERVED,
            "source_sha256": before, "target_declarations": TARGETS, "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "Theorem 6.1 on ActualRegisteredSummaries c r for every 2<=r<n, last-checkpoint multiplicities, independent k=0 fibres, and the all-n r=n-1 boundary count",
            "remaining_scope": ["Rank-refined fibre and absorption-length counts", "Fixed-pair summary specialization",
                                "Generating functions and asymptotics"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8")),
                "counting replay differs from freeze")
    print(json.dumps({"status": "PASS_ACTUAL_REGISTERED_SUMMARY_COUNT", "inputs": len(before),
        "preserved_milestones": len(PRESERVED), "axiom_checks": len(declarations()),
        "targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
