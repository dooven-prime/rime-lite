"""Replay the all-parameter proper-arc actual placement fibre and exact count."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0,str(BASE))
from validate_companion import ALLOWED_AXIOMS, as_json, check_inputs, lean_code, require, run_lake, sha256
from classification.validate_classification import closure
from chains.validate_chains import PROOFS as CHAIN_PROOFS
from converse.validate_converse import PRESERVED as CHAIN_INPUTS, PROOFS as CONVERSE_PROOFS

PRESERVED = dict(CHAIN_INPUTS, **{
    "converse/milestones/actual-chain-equivalence-v1/manifest.json":
        "3dac55c745d644ebb80565fdeb749b411f0ca7e18e0a9c35d4d7b1fc2ee3a731"})
PROOFS = [HERE/(name+".lean") for name in ("Carrier","NormalForm","Realization","PlacementEquivalence")]
PREFIX = "ProperArc.Chains."
UPSTREAM = [PREFIX+name for name in ("actualSelectedChainsEquivCode","actual_chain_decode_encode","realize_clean_code")]+["ProperArc.run_originWord"]
TARGETS = [PREFIX+name for name in ("outsideCount_eq","actual_code_carrier","actual_fiber_normal_form",
    "fiber_target_reachable","positiveFiberTarget_injective","actual_fiber_params","positivePlacementFibreEquiv",
    "full_carrier_target_reachable","fullPlacementFibreEquiv","codePlacementFibreEquiv","card_actualCodePlacements")]+UPSTREAM
EXTRA = [PREFIX+name for name in ("ActualCodePlacements","CodeFiberParams","positiveFiberData","positiveFiberTarget",
    "positivePlacementFibreEquiv","fullPlacementFibreEquiv","codePlacementFibreEquiv")]
DESTINATION = HERE/"milestones/placement-fibre-v1"


def preserved_inputs(check_git=False):
    for relative, expected in PRESERVED.items():
        path = BASE/relative
        require(sha256(path)==expected,f"preserved manifest drift: {relative}")
        manifest = json.loads(path.read_text("utf-8"))
        for source, sha in manifest["source_sha256"].items():
            require(sha256(BASE/source)==sha,f"preserved source drift: {source}")
        require(sha256(path.parent/"dependency-audit.json")==manifest["report_sha256"],f"preserved report drift: {relative}")
    check_inputs(check_git)


def own_inputs():
    paths = [*PROOFS,HERE/"AxiomAudit.lean",Path(__file__).resolve(),HERE/"tests/test_fibre_audit.py"]
    require(set(HERE.glob("*.lean"))==set(PROOFS)|{HERE/"AxiomAudit.lean"},"fibre source inventory drift")
    return {path.relative_to(BASE).as_posix():sha256(path) for path in paths}


def declarations():
    return [PREFIX+match.group(1) for path in PROOFS for match in
        re.finditer(r"^theorem\s+([\w.]+)",path.read_text("utf-8"),re.MULTILINE)]+EXTRA+UPSTREAM


def check_report(output):
    marker = "PLACEMENT_FIBRE_JSON\n"
    require(output.count(marker)==1,"missing or repeated fibre report")
    report = json.loads(output.split(marker,1)[1].splitlines()[0])
    require(report["schema"]=="proper_arc_placement_fibre_audit.v1","unknown fibre report")
    require(report["scope_status"]=="ACTUAL_FIXED_ORIGIN_CHAIN_PLACEMENT_FIBRE","fibre scope drift")
    require([row["name"] for row in report["targets"]]==TARGETS,"fibre target inventory drift")
    nodes = {node["name"]:node for node in report["nodes"]}
    require(len(nodes)==len(report["nodes"]),"duplicate fibre dependency node")
    required = {
        TARGETS[0]:{PREFIX+"decodePrefix_absorbed"},
        TARGETS[1]:{PREFIX+"actual_chain_trace_run",PREFIX+"canonical_code_carrier",PREFIX+"normalized_run"},
        TARGETS[2]:{PREFIX+"normalized_code_carrier",PREFIX+"ordered_fiber_naming",
                    "RegisteredAbsorptionChains.OrderedOutsideNaming.toCutNamed"},
        TARGETS[3]:{PREFIX+"realize_clean_prefix","RegisteredAbsorptionChains.allCut_realize_target",
                    "RegisteredAbsorptionChains.run_append",PREFIX+"rename_run"},
        TARGETS[4]:{"RegisteredAbsorptionChains.rank_params_target_unique",PREFIX+"renamePlacement_injective"},
        TARGETS[5]:{PREFIX+"actual_fiber_normal_form","RegisteredAbsorptionChains.ValidFiberPlacement.of_toRankParams"},
        TARGETS[6]:{PREFIX+"ActualCodePlacements",PREFIX+"positiveFiberTarget_reachable",PREFIX+"actual_fiber_params"},
        TARGETS[7]:{PREFIX+"realize_clean_code","RegisteredAbsorptionChains.realize_full_carrier_rotation",PREFIX+"decodedCarrier_full"},
        TARGETS[8]:{PREFIX+"actual_code_carrier",PREFIX+"full_carrier_target_reachable","RegisteredAbsorptionChains.sourceOrdered_fullCarrier"},
        TARGETS[9]:{PREFIX+"positivePlacementFibreEquiv",PREFIX+"fullPlacementFibreEquiv"},
        TARGETS[10]:{PREFIX+"codePlacementFibreEquiv","RegisteredAbsorptionChains.card_fiberParams"},
    }
    previous = json.loads((BASE/"converse/milestones/actual-chain-equivalence-v1/dependency-audit.json").read_text("utf-8"))
    old_nodes = {row["name"]:row for row in previous["nodes"]}
    forbidden = {"RegisteredAbsorptionChains."+name for name in ("actualFixedChainPlacementEquiv",
        "actual_fiber_rank_normal_form","actual_fiber_normal_form","actual_code_carrier_at_site",
        "actual_code_canonical_named","actual_code_ordered_outside_naming","code_rank_params_reachable",
        "code_fiber_target_reachable","full_carrier_code_fiber_phases","realize_clean_code")}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes,name)
        require(reached==set(target["dependencies"]),f"incomplete fibre closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"]=="axiom"}
        require(axioms==set(target["axioms"]) and axioms<=ALLOWED_AXIOMS,"unexpected fibre axioms")
        require(required.get(name,set())<=reached,f"missing actual fibre input: {name}")
        require(not (forbidden&reached),"fixed-pair actual fibre theorem substituted for proper-arc proof")
        require(target["signature"],f"empty fibre signature: {name}")
        if name in (TARGETS[1],TARGETS[2],TARGETS[5]):
            require("CleanOutside" not in target["signature"] and
                    "RegisteredAbsorptionChains.CleanOutside" not in reached,"reverse fibre restricted to clean histories")
            require("singletonExecution" in target["signature"] and "run" in target["signature"],"actual fibre history missing")
        if name in UPSTREAM:
            old = closure(old_nodes,name)
            require(reached==old and all(nodes[item]==old_nodes[item] for item in old),f"inherited chain graph drift: {name}")
    definitions = report["definitions"]
    domain = definitions[PREFIX+"ActualCodePlacements"]
    require(all(token in domain for token in ("run","singletonExecution","originRecord","decodeChain","placed")),
            "actual fibre lost same-history origin, chain or placement")
    require("positiveFiberTarget" not in domain and "CodeFiberParams" not in domain,"actual fibre replaced by parameter image")
    params = definitions[PREFIX+"CodeFiberParams"]
    require("ZMod" in params and "FiberParams" in params,"full-carrier parameter branch missing")
    for name in ("CodeFiberParams","positiveFiberData"):
        body = definitions[PREFIX+name]
        require(not any(token in body for token in ("Reachable","singletonExecution","run ")),"parameter type assumes reachability")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)",output)
    require([name for name,_ in printed]==declarations(),"fibre axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$",(HERE/"AxiomAudit.lean").read_text("utf-8"),re.MULTILINE)==declarations(),
            "fibre source audit inventory drift")
    for name,axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()}<=ALLOWED_AXIOMS,f"unapproved fibre axiom: {name}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze",action="store_true")
    parser.add_argument("--source-only",action="store_true")
    parser.add_argument("--check-upstream-git",action="store_true")
    args = parser.parse_args()
    preserved_inputs(args.check_upstream_git)
    before = own_inputs()
    for path in [*PROOFS,HERE/"AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",lean_code(path.read_text("utf-8")),re.MULTILINE),
                f"unfinished fibre proof: {path.name}")
    manifest_path = DESTINATION/"manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(),"fibre freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"]==before,"fibre source drift")
        require(manifest["preserved_milestones"]==PRESERVED,"fibre prerequisite drift")
        require(manifest["report_sha256"]==sha256(DESTINATION/"dependency-audit.json"),"fibre report drift")
    if args.source_only:
        print(json.dumps({"status":"PASS_PLACEMENT_FIBRE_SOURCE_ONLY","inputs":len(before)}))
        return 0
    origin = json.loads((BASE/next(iter(PRESERVED))).read_text("utf-8"))
    version = run_lake(["env","lean","--version"]).strip()
    require(version==origin["lean_executable"],"fibre Lean executable drift")
    run_lake(["build"])
    run_lake(["build","RegisteredAbsorptionChains.FiberParamInverse"])
    library = BASE/".lake/build/lib/lean"
    for folder in ("classification","chains","converse","fibres"):
        (library/folder).mkdir(parents=True,exist_ok=True)
    for stem in ("SourceCut","OriginTrace","OriginExhaustive"):
        run_lake(["env","lean","-o",str(library/"classification"/(stem+".olean")),str(BASE/"classification"/(stem+".lean"))])
    for folder,paths in (("chains",CHAIN_PROOFS),("converse",CONVERSE_PROOFS),("fibres",PROOFS)):
        for path in paths:
            run_lake(["env","lean","-o",str(library/folder/(path.stem+".olean")),str(path)])
    run_lake(["env","lean","-o",str(library/"AxiomAudit.olean"),str(BASE/"AxiomAudit.lean")])
    report = check_report(run_lake(["env","lean",str(HERE/"AxiomAudit.lean")]))
    require(own_inputs()==before,"fibre sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION/"dependency-audit.json"
        report_path.write_text(as_json(report),encoding="utf-8",newline="\n")
        manifest_path.write_text(as_json({
            "schema":"proper_arc_placement_fibre_milestone.v1","scope_status":"ACTUAL_FIXED_ORIGIN_CHAIN_PLACEMENT_FIBRE",
            "release_identity_claimed":False,"hal_v1_proof_identity_changed":False,
            "lean_executable":version,"mathlib_commit":origin["mathlib_commit"],"target_manuscript":origin["target_manuscript"],
            "preserved_milestones":PRESERVED,"source_sha256":before,"target_declarations":TARGETS,
            "axiom_audit":declarations(),"report_sha256":sha256(report_path),
            "scope":"Theorem 5.2 actual fixed-origin/code placement fibre: positive outside parameters, independent full-carrier phases, two-way equivalence and n*choose(n+k-2,k) total count",
            "remaining_scope":["Rank-refined fibre count","Dependent full-summary equivalence and total count",
                "Refined chain count","Generating functions and asymptotics"],
            "replay_boundary":"Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }),encoding="utf-8",newline="\n")
    else:
        require(report==json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8")),"fibre replay differs from freeze")
    print(json.dumps({"status":"PASS_ACTUAL_PLACEMENT_FIBRE","inputs":len(before),
        "axiom_checks":len(declarations()),"targets":len(TARGETS),"dependency_nodes":len(report["nodes"])}))
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError,OSError,KeyError,ValueError) as exc:
        print(f"FAIL: {exc}",file=sys.stderr)
        raise SystemExit(1) from exc
