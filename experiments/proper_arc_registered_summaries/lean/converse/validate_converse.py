"""Replay arbitrary-history proper-arc chain classification and the actual bijection."""

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
from classification.validate_classification import closure
from chains.validate_chains import PRESERVED as CONSTRUCTION_INPUTS, PROOFS as CONSTRUCTION_PROOFS

PRESERVED = dict(CONSTRUCTION_INPUTS, **{
    "chains/milestones/chain-construction-v1/manifest.json":
        "5979c315a7a8f534efeb29948cb0f4f8ed151c99a7e06cd6059f3bf58aa9e5fd"})
PROOFS = [HERE / (name + ".lean") for name in (
    "DecoderInsertion", "ActualPartner", "ActualTrace", "ActualChainConverse")]
PREFIX = "ProperArc.Chains."
UPSTREAM = [PREFIX + name for name in (
    "codeEmbeddingActualSelectedChains", "realize_clean_code", "decodeChain_injective")] + [
    "ProperArc.run_originWord", "ProperArc.actualRegistrationOriginsEquivCuts"]
TARGETS = [PREFIX + name for name in ("actual_checkpoint_increases", "actual_partner_is_end_interval",
    "actual_chain_checkpoint_strict", "actual_chain_in_decode_range", "encodeChain_decodeChain",
    "actual_chain_decode_encode", "actual_chain_unique_code", "actualSelectedChainsEquivCode",
    "card_actualSelectedChains", "checkpoint_port_bindings_distinct")] + UPSTREAM
BACKWARD = {TARGETS[i] for i in (0, 1, 2, 3, 5, 6)}
DESTINATION = HERE / "milestones/actual-chain-equivalence-v1"


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
    paths = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(), HERE / "tests/test_converse_audit.py"]
    require(set(HERE.glob("*.lean")) == set(PROOFS) | {HERE / "AxiomAudit.lean"}, "converse source inventory drift")
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def declarations():
    names = [PREFIX + match.group(1) for path in PROOFS
             for match in re.finditer(r"^theorem\s+([\w.]+)", path.read_text("utf-8"), re.MULTILINE)]
    return names + [PREFIX + name for name in ("encodeChain", "ActualChainTrace", "actualSelectedChainsEquivCode")] + UPSTREAM


def check_report(output):
    marker = "CHAIN_CONVERSE_JSON\n"
    require(output.count(marker) == 1, "missing or repeated converse report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_chain_converse_audit.v1", "unknown converse report")
    require(report["scope_status"] == "ACTUAL_FIXED_ORIGIN_CHAIN_EQUIVALENCE", "converse scope drift")
    require([row["name"] for row in report["targets"]] == TARGETS, "converse target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate converse dependency node")
    required = {
        TARGETS[0]: {"RegisteredAbsorptionChains.actual_selected_partner_strict", "ProperArc.card_arc"},
        TARGETS[1]: {"RegisteredAbsorptionChains.actual_selected_fusion_frontier",
                     "RegisteredAbsorptionChains.checkpoint_step_records", PREFIX + "actual_checkpoint_increases"},
        TARGETS[2]: {PREFIX + "actual_chain_in_decode_range", PREFIX + "keys_strict", PREFIX + "keys_bounds"},
        TARGETS[3]: {PREFIX + "ActualChainTrace", PREFIX + "actual_chain_trace_run",
                     PREFIX + "actual_step_extends_code", PREFIX + "actual_partner_is_end_interval",
                     PREFIX + "rename_run", "RegisteredAbsorptionChains.run_ordered"},
        TARGETS[4]: {PREFIX + "encodeChain", PREFIX + "decodeChain_keys", PREFIX + "keys_mem_iff"},
        TARGETS[5]: {PREFIX + "actual_chain_in_decode_range", PREFIX + "encodeChain_decodeChain"},
        TARGETS[6]: {PREFIX + "actual_chain_decode_encode", PREFIX + "encodeChain_decodeChain"},
        TARGETS[7]: {PREFIX + "ActualSelectedChains", PREFIX + "encodeChain", PREFIX + "codeEmbeddingActualSelectedChains",
                     PREFIX + "actual_chain_decode_encode", PREFIX + "encodeChain_decodeChain"},
        TARGETS[8]: {PREFIX + "actualSelectedChainsEquivCode", "RegisteredAbsorptionChains.card_code"},
    }
    old = json.loads((BASE / "chains/milestones/chain-construction-v1/dependency-audit.json").read_text("utf-8"))
    old_nodes = {row["name"]: row for row in old["nodes"]}
    forbidden_pair = {"RegisteredAbsorptionChains." + name for name in (
        "actual_chain_in_decode_range", "actual_chain_unique_code", "codeEquivReachableSelectedChain",
        "actual_decoded_trace_run", "actual_decoded_trace_run_from", "realize_clean_code")}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes, name)
        require(reached == set(target["dependencies"]), f"incomplete converse closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected converse axioms")
        require(required.get(name, set()) <= reached, f"missing actual converse input: {name}")
        require(not (forbidden_pair & reached), "fixed-pair actual chain theorem substituted for proper-arc proof")
        require(target["signature"], f"empty converse signature: {name}")
        if name in BACKWARD:
            require("CleanOutside" not in target["signature"], "clean premise restricts actual converse")
            require("RegisteredAbsorptionChains.CleanOutside" not in reached and
                    PREFIX + "realize_clean_code" not in reached and PREFIX + "realize_clean_prefix" not in reached,
                    "converse relies on clean forward witnesses")
        if name in UPSTREAM:
            previous = closure(old_nodes, name)
            require(reached == previous and all(nodes[item] == old_nodes[item] for item in previous),
                    f"inherited construction graph drift: {name}")
    for i in (2, 3, 5, 6):
        signature = report["targets"][i]["signature"]
        require("singletonExecution" in signature and "run" in signature and "isSome" in signature,
                "arbitrary actual seed-history premise missing")
    require("Code (n - r)" in report["targets"][7]["signature"] and
            "ActualSelectedChains" in report["targets"][7]["signature"], "actual equivalence endpoint drift")
    definitions = report["definitions"]
    domain = definitions[PREFIX + "ActualSelectedChains"]
    require(all(token in domain for token in ("run", "singletonExecution", "originRecord", "chain"))
            and "decode" not in domain, "actual-chain type is not the full fixed-origin history domain")
    trace = definitions[PREFIX + "ActualChainTrace"]
    require("CleanOutside" not in trace and "RecordedCarrier" in trace, "reverse invariant narrowed to clean histories")
    encoder = definitions[PREFIX + "encodeChain"]
    require(all(token in encoder for token in ("recordKeyAt", "true", "false")), "encoder lost actual-record key reads")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "converse axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"), re.MULTILINE)
            == declarations(), "converse source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved converse axiom: {name}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    preserved_inputs(args.check_upstream_git)
    before = own_inputs()
    for path in [*PROOFS, HERE / "AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                lean_code(path.read_text("utf-8")), re.MULTILINE), f"unfinished converse proof: {path.name}")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "converse freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "converse source drift")
        require(manifest["preserved_milestones"] == PRESERVED, "converse prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"), "converse report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_CHAIN_CONVERSE_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    origin = json.loads((BASE / next(iter(PRESERVED))).read_text("utf-8"))
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == origin["lean_executable"], "converse Lean executable drift")
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.ActualChainRange"])
    library = BASE / ".lake/build/lib/lean"
    for folder in ("classification", "chains", "converse"):
        (library / folder).mkdir(parents=True, exist_ok=True)
    for stem in ("SourceCut", "OriginTrace", "OriginExhaustive"):
        run_lake(["env", "lean", "-o", str(library / "classification" / (stem + ".olean")),
                  str(BASE / "classification" / (stem + ".lean"))])
    for path in CONSTRUCTION_PROOFS:
        run_lake(["env", "lean", "-o", str(library / "chains" / (path.stem + ".olean")), str(path)])
    for path in PROOFS:
        run_lake(["env", "lean", "-o", str(library / "converse" / (path.stem + ".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library / "AxiomAudit.olean"), str(BASE / "AxiomAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs() == before, "converse sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest_path.write_text(as_json({
            "schema": "proper_arc_actual_chain_equivalence_milestone.v1",
            "scope_status": "ACTUAL_FIXED_ORIGIN_CHAIN_EQUIVALENCE",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "target_manuscript": origin["target_manuscript"], "preserved_milestones": PRESERVED,
            "source_sha256": before, "target_declarations": TARGETS, "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "Theorem 4.2 chain bijection and total 3^(n-r): arbitrary actual-history converse, strict checkpoints, explicit record encoder, both round-trips and actual fixed-origin equivalence",
            "remaining_scope": ["Refined count by selected absorption length", "Actual placement fibers",
                "Dependent full-summary equivalence and count", "Analytic layer"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "converse replay differs from freeze")
    print(json.dumps({"status": "PASS_ACTUAL_CHAIN_EQUIVALENCE", "inputs": len(before),
        "axiom_checks": len(declarations()), "targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
