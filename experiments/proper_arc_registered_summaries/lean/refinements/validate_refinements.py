"""Replay actual-chain absorption-length and actual-placement rank refinements."""

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
from counting.validate_counting import PRESERVED as COUNT_INPUTS

PRESERVED = dict(COUNT_INPUTS, **{
    "counting/milestones/summary-count-v1/manifest.json":
        "6535bd701625f294302f4ecadbb686a1a04cd22e9a6c110fe4d050619aa531ba"})
PROOFS = [HERE/(name+".lean") for name in ("ChainLength", "RankFibre")]
PREFIX = "ProperArc.Chains."
CHAIN_TARGETS = [PREFIX+name for name in ("coloredCheckpointsEquivCodes", "card_codes_by_support",
    "decodeChain_length", "actualChainsLengthEquivCodes", "card_actualSelectedChains_length")]
RANK_TARGETS = [PREFIX+name for name in ("positiveFiberTarget_rank", "rankParamsEquivSlice",
    "actualRankCodePlacementsEquiv", "card_actualRankCodePlacements", "actual_full_carrier_rank",
    "actualFullRankCodePlacementsEquiv", "card_actualFullRankCodePlacements")]
UPSTREAM = [PREFIX+name for name in ("actualSelectedChainsEquivCode", "positivePlacementFibreEquiv",
    "fullPlacementFibreEquiv", "codeSnocEquiv")]
TARGETS = CHAIN_TARGETS+RANK_TARGETS+UPSTREAM
EXTRA = [PREFIX+name for name in ("ColoredCheckpoints", "codeOfColors", "coloredCheckpointsEquivCodes",
    "actualChainsLengthEquivCodes", "ActualRankCodePlacements", "rankIndexSliceEquiv",
    "rankParamsEquivSlice", "actualRankCodePlacementsEquiv", "actualFullRankCodePlacementsEquiv")]
DESTINATION = HERE/"milestones/combinatorial-refinements-v1"


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
    paths = [*PROOFS, HERE/"AxiomAudit.lean", Path(__file__).resolve(), HERE/"tests/test_refinement_audit.py"]
    require(set(HERE.glob("*.lean")) == set(PROOFS)|{HERE/"AxiomAudit.lean"}, "refinement source inventory drift")
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def file_declarations(path):
    return {PREFIX+match.group(1) for match in re.finditer(
        r"^(?:theorem|(?:noncomputable\s+)?def|abbrev)\s+([\w.]+)", path.read_text("utf-8"), re.MULTILINE)}


def declarations():
    return [PREFIX+match.group(1) for path in PROOFS for match in
            re.finditer(r"^theorem\s+([\w.]+)", path.read_text("utf-8"), re.MULTILINE)]+EXTRA+UPSTREAM


def check_report(output):
    marker = "COMBINATORIAL_REFINEMENTS_JSON\n"
    require(output.count(marker) == 1, "missing or repeated refinement report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_combinatorial_refinements_audit.v1", "unknown refinement report")
    require(report["scope_status"] == "ACTUAL_CHAIN_LENGTH_AND_PLACEMENT_RANK_COUNTS", "refinement scope drift")
    require([row["name"] for row in report["targets"]] == TARGETS, "refinement target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate refinement dependency node")
    required = {
        CHAIN_TARGETS[0]: {PREFIX+"support_codeOfColors", PREFIX+"codeOfColors_readback"},
        CHAIN_TARGETS[1]: {CHAIN_TARGETS[0], "RegisteredAbsorptionChains.card_select"},
        CHAIN_TARGETS[2]: {PREFIX+"decodeChain_keys", PREFIX+"keys_length_support"},
        CHAIN_TARGETS[3]: {PREFIX+"actualSelectedChainsEquivCode", PREFIX+"decodeChain_length"},
        CHAIN_TARGETS[4]: {CHAIN_TARGETS[3], CHAIN_TARGETS[1], PREFIX+"ActualSelectedChains"},
        RANK_TARGETS[0]: {PREFIX+"renamePlacement_rank", PREFIX+"positiveFiberData"},
        RANK_TARGETS[1]: {PREFIX+"rankIndexSliceEquiv"},
        RANK_TARGETS[2]: {PREFIX+"positivePlacementFibreEquiv", RANK_TARGETS[0], RANK_TARGETS[1]},
        RANK_TARGETS[3]: {RANK_TARGETS[2], "RegisteredAbsorptionChains.card_rankFiberParams_paper"},
        RANK_TARGETS[4]: {PREFIX+"fullPlacementFibreEquiv", PREFIX+"placedBlocks_fullCarrier"},
        RANK_TARGETS[5]: {PREFIX+"fullPlacementFibreEquiv", RANK_TARGETS[4]},
        RANK_TARGETS[6]: {RANK_TARGETS[5], "Nat.card_zmod"},
    }
    previous_paths = {
        "chain": "converse/milestones/actual-chain-equivalence-v1/dependency-audit.json",
        "fibre": "fibres/milestones/placement-fibre-v1/dependency-audit.json",
        "code": "counting/milestones/summary-count-v1/dependency-audit.json"}
    previous = {key: {node["name"]: node for node in json.loads((BASE/path).read_text("utf-8"))["nodes"]}
                for key, path in previous_paths.items()}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes, name)
        require(reached == set(target["dependencies"]), f"incomplete refinement closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected refinement axioms")
        require(required.get(name, set()) <= reached, f"missing actual refinement input: {name}")
        require(target["signature"] and set(target["type_constants"]) <= reached, "refinement type metadata drift")
        require(PREFIX+"card_actual_registered_summaries" not in reached and not any(item.startswith(
            ("RegisteredAbsorptionChains.card_actualRegisteredSummaries", "FutureEvent.")) for item in reached),
            "total-count shortcut substituted for independent refinement")
        if name in CHAIN_TARGETS:
            require(not (file_declarations(PROOFS[1]) & reached), "chain refinement depends on new rank branch")
        if name in RANK_TARGETS:
            require(not (file_declarations(PROOFS[0]) & reached), "rank refinement depends on new chain branch")
        if name in UPSTREAM:
            key = "chain" if name == UPSTREAM[0] else "code" if name == UPSTREAM[3] else "fibre"
            old = previous[key]
            inherited = closure(old, name)
            require(reached == inherited and all(nodes[item] == old[item] for item in inherited),
                    f"inherited refinement graph drift: {name}")
    by_name = {target["name"]: target for target in report["targets"]}
    chain = by_name[CHAIN_TARGETS[4]]
    require(PREFIX+"ActualSelectedChains" in chain["type_constants"], "chain count lost actual history type")
    signature = " ".join(chain["signature"].split())
    require(all(token in signature for token in ("2 ≤ r", "r < n", "length = j", "(n - r).choose j * 2 ^ j")),
            "chain-length count interface drift")
    rank = by_name[RANK_TARGETS[3]]
    require(PREFIX+"ActualRankCodePlacements" in rank["type_constants"], "rank count lost actual placement type")
    signature = " ".join(rank["signature"].split())
    require(all(token in signature for token in ("0 <", "outsideCount", "2 ≤ s", "v + 1", "s - 2", "n.choose s")),
            "positive-rank formula or domain drift")
    full = by_name[RANK_TARGETS[6]]
    require(PREFIX+"ActualRankCodePlacements" in full["type_constants"] and all(token in full["signature"]
        for token in ("outsideCount", "= 0", "v 1)", "= n")), "rank-one phase interface drift")
    definitions = report["definitions"]
    for key, fields in (("ActualSelectedChains", ("run", "singletonExecution", "origin", "chain")),
                        ("ActualCodePlacements", ("run", "singletonExecution", "origin", "chain", "placed"))):
        domain = definitions[PREFIX+key]
        require(all(token in domain for token in fields), f"actual refinement domain lost seed history: {key}")
        require(not any(token in domain for token in ("CleanOutside", "Set.range", "FiberParams")),
                f"actual refinement domain restricted to constructed states: {key}")
    rank_domain = definitions[PREFIX+"ActualRankCodePlacements"]
    require(all(token in rank_domain for token in ("ActualCodePlacements", "placedBlocks", ".card = s")),
            "rank filter is not the literal placement packet count")
    require(not any(token in rank_domain for token in ("positiveFiberTarget", "FiberParams", "s - 1")),
            "rank filter was replaced by a parameter index")
    colors = definitions[PREFIX+"ColoredCheckpoints"]
    require(all(token in colors for token in ("Select m j", "Bool")), "checkpoint colors lost independent choices")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "refinement axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE/"AxiomAudit.lean").read_text("utf-8"), re.MULTILINE) == declarations(),
            "refinement source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved refinement axiom: {name}")
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
                f"unfinished refinement proof: {path.name}")
    manifest_path = DESTINATION/"manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "refinement freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "refinement source drift")
        require(manifest["preserved_milestones"] == PRESERVED, "refinement prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION/"dependency-audit.json"), "refinement report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_REFINEMENTS_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    origin = json.loads((BASE/next(iter(PRESERVED))).read_text("utf-8"))
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == origin["lean_executable"], "refinement Lean executable drift")
    print("REPLAY frozen origin library", flush=True)
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.FiberParamInverse"])
    library = BASE/".lake/build/lib/lean"
    layers = (("classification", ORIGIN_PROOFS), ("chains", CHAIN_PROOFS),
              ("converse", CONVERSE_PROOFS), ("fibres", FIBRE_PROOFS),
              ("counting", [BASE/"counting/LastCheckpointCount.lean"]), ("refinements", PROOFS))
    for folder, paths in layers:
        (library/folder).mkdir(parents=True, exist_ok=True)
        print(f"REPLAY {folder}", flush=True)
        for path in paths:
            run_lake(["env", "lean", "-o", str(library/folder/(path.stem+".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library/"AxiomAudit.olean"), str(BASE/"AxiomAudit.lean")])
    print("AUDIT independent chain-length and rank closures", flush=True)
    report = check_report(run_lake(["env", "lean", str(HERE/"AxiomAudit.lean")]))
    require(own_inputs() == before, "refinement sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION/"dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest_path.write_text(as_json({
            "schema": "proper_arc_combinatorial_refinements_milestone.v1",
            "scope_status": "ACTUAL_CHAIN_LENGTH_AND_PLACEMENT_RANK_COUNTS",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "target_manuscript": origin["target_manuscript"], "preserved_milestones": PRESERVED,
            "source_sha256": before, "target_declarations": TARGETS, "axiom_audit": declarations(),
            "independent_branches": {"chain_length": CHAIN_TARGETS, "placement_rank": RANK_TARGETS},
            "report_sha256": sha256(report_path),
            "scope": "Theorem 4.2 actual fixed-origin chains with j records; Theorem 5.2 actual fixed-origin/code rank-s placements for k>0, and independent k=0 rank-one phases",
            "remaining_scope": ["Fixed-pair summary specialization", "Generating functions and asymptotics"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION/"dependency-audit.json").read_text("utf-8")),
                "refinement replay differs from freeze")
    print(json.dumps({"status": "PASS_ACTUAL_COMBINATORIAL_REFINEMENTS", "inputs": len(before),
        "preserved_milestones": len(PRESERVED), "axiom_checks": len(declarations()),
        "targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
