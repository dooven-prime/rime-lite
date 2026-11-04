"""Replay the proper-arc ternary decoder, actual clean witnesses and embedding."""

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
from classification.validate_classification import PRESERVED as ORIGIN_INPUTS, closure

PRESERVED = dict(ORIGIN_INPUTS, **{
    "classification/milestones/origin-classification-v1/manifest.json":
        "cf0bc343a73e7466b870c36843e072472159779373ad3e85964d17e69acea2d0"})
PROOFS = [HERE / (name + ".lean") for name in (
    "Decoder", "SourceTranslation", "DecoderInjective", "CleanRealization", "ActualChains")]
PREFIX = "ProperArc.Chains."
UPSTREAM = ["ProperArc." + name for name in (
    "run_local_unregistered", "run_originWord", "boundary_clean", "actualRegistrationOriginsEquivCuts")]
TARGETS = [PREFIX + name for name in ("decodePrefix_absorbed", "decodeChain_keys", "decodeChain_injective",
    "realize_clean_prefix", "realize_clean_code", "codeEmbeddingActualSelectedChains",
    "codeEmbeddingActualSelectedChains_clean")] + UPSTREAM
DESTINATION = HERE / "milestones/chain-construction-v1"


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
    paths = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(), HERE / "tests/test_chain_audit.py"]
    require(set(HERE.glob("*.lean")) == set(PROOFS) | {HERE / "AxiomAudit.lean"}, "chain source inventory drift")
    return {path.relative_to(BASE).as_posix(): sha256(path) for path in paths}


def declarations():
    names = [PREFIX + match.group(1) for path in PROOFS
             for match in re.finditer(r"^(?:@\[simp\] )?theorem\s+([\w.]+)",
                                     path.read_text("utf-8"), re.MULTILINE)]
    return names + [PREFIX + "codeEmbeddingActualSelectedChains"] + UPSTREAM


def check_report(output):
    marker = "CHAIN_CONSTRUCTION_JSON\n"
    require(output.count(marker) == 1, "missing or repeated chain report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "proper_arc_chain_construction_audit.v1", "unknown chain report")
    require(report["scope_status"] == "CONSTRUCTIVE_CHAIN_EMBEDDING", "unproved chain-equivalence promotion")
    require([row["name"] for row in report["targets"]] == TARGETS, "chain target inventory drift")
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate chain dependency node")
    required = {
        TARGETS[0]: {PREFIX + "lastCheckpoint"},
        TARGETS[1]: {PREFIX + "shifted_recordKey", PREFIX + "decodePrefix_keys"},
        TARGETS[2]: {PREFIX + "decodeCanonicalChain_injective", PREFIX + "rename_chain_injective"},
        TARGETS[3]: {"ProperArc.run_originWord", "ProperArc.boundary_clean",
                     "RegisteredAbsorptionChains.CheckpointSourceFrontier.realizeR_checkpoint",
                     "RegisteredAbsorptionChains.CheckpointSourceFrontier.realizeL_checkpoint",
                     "RegisteredAbsorptionChains.run_append"},
        TARGETS[4]: {PREFIX + "realize_clean_prefix", PREFIX + "rename_run", "ProperArc.run_alignment"},
        TARGETS[5]: {PREFIX + "realize_clean_code", PREFIX + "decodeChain_injective", PREFIX + "ActualSelectedChains"},
        TARGETS[6]: {PREFIX + "realize_clean_code"},
    }
    old = json.loads((BASE / "classification/milestones/origin-classification-v1/dependency-audit.json").read_text("utf-8"))
    old_nodes = {row["name"]: row for row in old["nodes"]}
    for target in report["targets"]:
        name = target["name"]
        reached = closure(nodes, name)
        require(reached == set(target["dependencies"]), f"incomplete chain closure: {name}")
        axioms = {item for item in reached if nodes[item]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS, "unexpected chain axioms")
        require(required.get(name, set()) <= reached, f"missing actual chain input: {name}")
        require(target["signature"], f"empty chain signature: {name}")
        require("RegisteredAbsorptionChains.realize_clean_code" not in reached,
                "fixed-pair realization substituted for proper-arc execution")
        if name in UPSTREAM:
            previous = closure(old_nodes, name)
            require(previous == reached and all(nodes[item] == old_nodes[item] for item in previous),
                    f"inherited proof graph drift: {name}")
    for target in report["targets"][4:7]:
        signature = target["signature"]
        require("Code (n - r)" in signature, "proper-arc code length missing")
    definition = report["actual_chains_definition"]
    require(all(token in definition for token in ("run", "singletonExecution", "originRecord", "chain")),
            "actual-chain type lost real seed history or fixed origin")
    require("decode" not in definition, "actual-chain type restricted to decoder range")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declarations(), "chain axiom inventory drift")
    require(re.findall(r"^#print axioms (\S+)$", (HERE / "AxiomAudit.lean").read_text("utf-8"), re.MULTILINE)
            == declarations(), "chain source audit inventory drift")
    for name, axioms in printed:
        require({item.strip() for item in axioms.split(",") if item.strip()} <= ALLOWED_AXIOMS,
                f"unapproved chain axiom: {name}")
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
                lean_code(path.read_text("utf-8")), re.MULTILINE), f"unfinished chain proof: {path.name}")
    manifest_path = DESTINATION / "manifest.json"
    if args.freeze:
        require(not args.source_only and not DESTINATION.exists(), "chain freeze exists or no kernel replay")
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["source_sha256"] == before, "chain source drift")
        require(manifest["preserved_milestones"] == PRESERVED, "chain prerequisite drift")
        require(manifest["report_sha256"] == sha256(DESTINATION / "dependency-audit.json"), "chain report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_CHAIN_CONSTRUCTION_SOURCE_ONLY", "inputs": len(before)}))
        return 0
    origin = json.loads((BASE / next(iter(PRESERVED))).read_text("utf-8"))
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == origin["lean_executable"], "chain Lean executable drift")
    run_lake(["build"])
    run_lake(["build", "RegisteredAbsorptionChains.CodeChainUniqueness"])
    library = BASE / ".lake/build/lib/lean"
    for folder in ("classification", "chains"):
        (library / folder).mkdir(parents=True, exist_ok=True)
    for stem in ("SourceCut", "OriginTrace", "OriginExhaustive"):
        run_lake(["env", "lean", "-o", str(library / "classification" / (stem + ".olean")),
                  str(BASE / "classification" / (stem + ".lean"))])
    for path in PROOFS:
        run_lake(["env", "lean", "-o", str(library / "chains" / (path.stem + ".olean")), str(path)])
    run_lake(["env", "lean", "-o", str(library / "AxiomAudit.olean"), str(BASE / "AxiomAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_inputs() == before, "chain sources changed during replay")
    preserved_inputs(args.check_upstream_git)
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(as_json(report), encoding="utf-8", newline="\n")
        manifest_path.write_text(as_json({
            "schema": "proper_arc_chain_construction_milestone.v1",
            "scope_status": "CONSTRUCTIVE_CHAIN_EMBEDDING",
            "release_identity_claimed": False, "hal_v1_proof_identity_changed": False,
            "lean_executable": version, "mathlib_commit": origin["mathlib_commit"],
            "target_manuscript": origin["target_manuscript"], "preserved_milestones": PRESERVED,
            "source_sha256": before, "target_declarations": TARGETS, "axiom_audit": declarations(),
            "report_sha256": sha256(report_path),
            "scope": "All proper n,c,r and internal cuts: ternary decoder, recoverable keys, injection and actual clean singleton-seed witness per code",
            "remaining_scope": ["Arbitrary actual chains are in the decoder range; fixed-origin chain equivalence",
                "Placement fibers, dependent summary equivalence and counts", "Analytic layer"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies, not fresh-machine cold replay",
        }), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "chain replay differs from freeze")
    print(json.dumps({"status": "PASS_CHAIN_CONSTRUCTION", "inputs": len(before),
        "axiom_checks": len(declarations()), "targets": len(TARGETS), "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
