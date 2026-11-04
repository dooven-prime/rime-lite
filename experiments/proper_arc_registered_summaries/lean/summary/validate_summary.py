"""Replay Theorem 5.3: actual generated summaries and their dependent parameters."""

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
from converse.validate_converse import PROOFS as CONVERSE_PROOFS
from fibres.validate_fibres import PRESERVED as FIBRE_INPUTS, PROOFS as FIBRE_PROOFS

PRESERVED = dict(FIBRE_INPUTS, **{
    "fibres/milestones/placement-fibre-v1/manifest.json":
        "7d85df042a583508908a028e98499b52e7e8d7507d23d5c70f6e210faa21658d"})
PROOFS = [HERE/(name+".lean") for name in ("SummaryTypes","SummaryEquivalence")]
PREFIX = "ProperArc.Chains."
UPSTREAM = [PREFIX+"codePlacementFibreEquiv",PREFIX+"actual_chain_decode_encode",
            "ProperArc.actual_registered_origin_unique","ProperArc.run_originWord"]
TARGETS = [PREFIX+name for name in ("summaryOriginIndex_spec","summaryCode_spec","decodeSummary_origin",
    "decodeSummary_chain","decodeSummary_placed","decodeSummary_encodeSummary","encodeSummary_decodeSummary",
    "actualRegisteredSummariesEquivParams","actualSummary_unique_params","decodeSummary_same_word","decodeSummary_injective")]+UPSTREAM
EXTRA = [PREFIX+name for name in ("ActualRegisteredSummaries","SummaryParams","summaryOriginIndex",
    "summaryPlacementInFibre","decodeSummary","encodeSummary","actualRegisteredSummariesEquivParams")]
DESTINATION = HERE/"milestones/dependent-summary-v1"


def preserved_inputs(check_git=False):
    for relative,expected in PRESERVED.items():
        path=BASE/relative
        require(sha256(path)==expected,f"preserved manifest drift: {relative}")
        manifest=json.loads(path.read_text("utf-8"))
        for source,sha in manifest["source_sha256"].items():
            require(sha256(BASE/source)==sha,f"preserved source drift: {source}")
        require(sha256(path.parent/"dependency-audit.json")==manifest["report_sha256"],f"preserved report drift: {relative}")
    check_inputs(check_git)


def own_inputs():
    paths=[*PROOFS,HERE/"AxiomAudit.lean",Path(__file__).resolve(),HERE/"tests/test_summary_audit.py"]
    require(set(HERE.glob("*.lean"))==set(PROOFS)|{HERE/"AxiomAudit.lean"},"summary source inventory drift")
    return {path.relative_to(BASE).as_posix():sha256(path) for path in paths}


def declarations():
    return [PREFIX+match.group(1) for path in PROOFS for match in
        re.finditer(r"^theorem\s+([\w.]+)",path.read_text("utf-8"),re.MULTILINE)]+EXTRA+UPSTREAM


def check_report(output):
    marker="DEPENDENT_SUMMARY_JSON\n"
    require(output.count(marker)==1,"missing or repeated summary report")
    report=json.loads(output.split(marker,1)[1].splitlines()[0])
    require(report["schema"]=="proper_arc_dependent_summary_audit.v1","unknown summary report")
    require(report["scope_status"]=="ACTUAL_DEPENDENT_SUMMARY_EQUIVALENCE","summary scope drift")
    require([row["name"] for row in report["targets"]]==TARGETS,"summary target inventory drift")
    nodes={node["name"]:node for node in report["nodes"]}
    require(len(nodes)==len(report["nodes"]),"duplicate summary dependency node")
    required={
        TARGETS[0]:{"ProperArc.actual_registered_origin_unique",PREFIX+"ActualRegisteredSummaries"},
        TARGETS[1]:{PREFIX+"actual_chain_decode_encode",PREFIX+"encodeChain"},
        TARGETS[2]:{PREFIX+"decodeSummary","ProperArc.originRecord"},
        TARGETS[3]:{PREFIX+"decodeSummary",PREFIX+"decodeChain"},
        TARGETS[4]:{PREFIX+"decodeSummary",PREFIX+"codePlacementFibreEquiv"},
        TARGETS[5]:{PREFIX+"execution_ext_fields",PREFIX+"summaryOriginIndex_spec",PREFIX+"summaryCode_spec",
                    PREFIX+"encodeSummary_placement_readback"},
        TARGETS[6]:{PREFIX+"decodeSummary_injective",PREFIX+"decodeSummary_encodeSummary"},
        TARGETS[7]:{PREFIX+"ActualRegisteredSummaries",PREFIX+"SummaryParams",PREFIX+"encodeSummary",
                    PREFIX+"decodeSummary",PREFIX+"decodeSummary_encodeSummary",PREFIX+"encodeSummary_decodeSummary"},
        TARGETS[8]:{PREFIX+"decodeSummary_injective",PREFIX+"decodeSummary_encodeSummary"},
        TARGETS[9]:{PREFIX+"decodeSummary",PREFIX+"codePlacementFibreEquiv",PREFIX+"ActualCodePlacements",
                    "RegisteredAbsorptionChains.run","RegisteredAbsorptionChains.singletonExecution"},
        TARGETS[10]:{"ProperArc.originRecord_injective",PREFIX+"decodeChain_injective",PREFIX+"codePlacementFibreEquiv"},
    }
    paths={"fibre":"fibres/milestones/placement-fibre-v1/dependency-audit.json",
           "origin":"classification/milestones/origin-classification-v1/dependency-audit.json"}
    old_nodes={key:{row["name"]:row for row in json.loads((BASE/path).read_text("utf-8"))["nodes"]}
               for key,path in paths.items()}
    forbidden={"RegisteredAbsorptionChains."+name for name in ("actualFixedChainPlacementEquiv",
        "actual_fiber_normal_form","codeEquivReachableSelectedChain","actual_chain_in_decode_range")}
    for target in report["targets"]:
        name=target["name"]
        reached=closure(nodes,name)
        require(reached==set(target["dependencies"]),f"incomplete summary closure: {name}")
        axioms={item for item in reached if nodes[item]["kind"]=="axiom"}
        require(axioms==set(target["axioms"]) and axioms<=ALLOWED_AXIOMS,"unexpected summary axioms")
        require(required.get(name,set())<=reached,f"missing actual summary input: {name}")
        require(not(forbidden&reached),"fixed-pair actual classification substituted for dependent summary proof")
        require(target["signature"],f"empty summary signature: {name}")
        if name in UPSTREAM:
            old=old_nodes["origin" if name=="ProperArc.actual_registered_origin_unique" else "fibre"]
            previous=closure(old,name)
            require(reached==previous and all(nodes[item]==old[item] for item in previous),f"inherited summary graph drift: {name}")
    definitions=report["definitions"]
    domain=definitions[PREFIX+"ActualRegisteredSummaries"]
    require(all(token in domain for token in ("run","singletonExecution","isSome")),"actual-summary domain lost registered seed history")
    require(not any(token in domain for token in ("decodeSummary","SummaryParams","CleanOutside")),"actual-summary domain restricted to constructed states")
    params=definitions[PREFIX+"SummaryParams"]
    require(all(token in params for token in ("Fin","r - 1","Code","n - r","CodeFiberParams")),"dependent parameter family drift")
    require(not any(token in params for token in ("Reachable","run ","ActualRegisteredSummaries","ActualCodePlacements")),
            "summary parameters assume actual reachability")
    decoder=definitions[PREFIX+"decodeSummary"]
    require(all(token in decoder for token in ("codePlacementFibreEquiv","originRecord","decodeChain")),"decoder lost full summary fields")
    encoder=definitions[PREFIX+"encodeSummary"]
    require(all(token in encoder for token in ("summaryOriginIndex","encodeChain","summaryPlacementInFibre","symm")),"encoder lost dependent field recovery")
    signature=report["targets"][9]["signature"]
    require(all(token in signature for token in ("∃ word","run","singletonExecution","origin","chain","placed")),
            "same-word certificate lost a jointly realized summary field")
    signature=report["targets"][7]["signature"]
    require("ActualRegisteredSummaries" in signature and "SummaryParams" in signature and "r < n" in signature,
            "actual dependent-equivalence interface drift")
    printed=re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)",output)
    require([name for name,_ in printed]==declarations(),"summary axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$",(HERE/"AxiomAudit.lean").read_text("utf-8"),re.MULTILINE)==declarations(),
            "summary source audit inventory drift")
    for name,axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()}<=ALLOWED_AXIOMS,f"unapproved summary axiom: {name}")
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze",action="store_true")
    parser.add_argument("--source-only",action="store_true")
    parser.add_argument("--check-upstream-git",action="store_true")
    args=parser.parse_args()
    preserved_inputs(args.check_upstream_git)
    before=own_inputs()
    for path in [*PROOFS,HERE/"AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",lean_code(path.read_text("utf-8")),re.MULTILINE),
                f"unfinished summary proof: {path.name}")
    manifest_path=DESTINATION/"manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(),"summary freeze exists or no kernel replay")
    else:
        manifest=json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"]==before,"summary source drift")
        require(manifest["preserved_milestones"]==PRESERVED,"summary prerequisite drift")
        require(manifest["report_sha256"]==sha256(DESTINATION/"dependency-audit.json"),"summary report drift")
    if args.source_only:
        print(json.dumps({"status":"PASS_DEPENDENT_SUMMARY_SOURCE_ONLY","inputs":len(before)}))
        return 0
    origin=json.loads((BASE/next(iter(PRESERVED))).read_text("utf-8"))
    version=run_lake(["env","lean","--version"]).strip()
    require(version==origin["lean_executable"],"summary Lean executable drift")
    run_lake(["build"])
    run_lake(["build","RegisteredAbsorptionChains.FiberParamInverse"])
    library=BASE/".lake/build/lib/lean"
    for folder in ("classification","chains","converse","fibres","summary"):
        (library/folder).mkdir(parents=True,exist_ok=True)
    for stem in ("SourceCut","OriginTrace","OriginExhaustive"):
        run_lake(["env","lean","-o",str(library/"classification"/(stem+".olean")),str(BASE/"classification"/(stem+".lean"))])
    for folder,paths in (("chains",CHAIN_PROOFS),("converse",CONVERSE_PROOFS),("fibres",FIBRE_PROOFS),("summary",PROOFS)):
        for path in paths:
            run_lake(["env","lean","-o",str(library/folder/(path.stem+".olean")),str(path)])
    run_lake(["env","lean","-o",str(library/"AxiomAudit.olean"),str(BASE/"AxiomAudit.lean")])
    report=check_report(run_lake(["env","lean",str(HERE/"AxiomAudit.lean")]))
    require(own_inputs()==before,"summary sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path=DESTINATION/"dependency-audit.json"
        report_path.write_text(as_json(report),encoding="utf-8",newline="\n")
        manifest_path.write_text(as_json({
            "schema":"proper_arc_dependent_summary_milestone.v1","scope_status":"ACTUAL_DEPENDENT_SUMMARY_EQUIVALENCE",
            "release_identity_claimed":False,"hal_v1_proof_identity_changed":False,
            "lean_executable":version,"mathlib_commit":origin["mathlib_commit"],"target_manuscript":origin["target_manuscript"],
            "preserved_milestones":PRESERVED,"source_sha256":before,"target_declarations":TARGETS,
            "axiom_audit":declarations(),"report_sha256":sha256(report_path),
            "scope":"Theorem 5.3: actual registered singleton-seed summaries equivalent to origin/code/dependent fibre parameters, both round-trips, unique parameters and same-word realization of all literal fields",
            "remaining_scope":["Theorem 6.1 total-summary enumeration","Rank-refined fibre and chain counts",
                "Fixed-pair summary specialization","Generating functions and asymptotics"],
            "replay_boundary":"Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }),encoding="utf-8",newline="\n")
    else:
        require(report==json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8")),"summary replay differs from freeze")
    print(json.dumps({"status":"PASS_ACTUAL_DEPENDENT_SUMMARY_EQUIVALENCE","inputs":len(before),
        "axiom_checks":len(declarations()),"targets":len(TARGETS),"dependency_nodes":len(report["nodes"])}))
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError,OSError,KeyError,ValueError) as exc:
        print(f"FAIL: {exc}",file=sys.stderr)
        raise SystemExit(1) from exc
