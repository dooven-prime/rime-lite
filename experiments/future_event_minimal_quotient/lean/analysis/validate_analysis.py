"""Independent Wallis-ratio build/audit, consuming the frozen finite milestone."""

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


FROZEN_FINITE = BASE / "milestones/finite-combinatorial-v1/manifest.json"
DESTINATION = HERE / "milestones/wallis-ratio-v1"
PROOFS = [HERE / "WallisAsymptotics.lean", HERE / "FutureCountAsymptotics.lean"]
OWN_INPUTS = [*PROOFS, HERE / "AxiomAudit.lean", Path(__file__).resolve(),
              HERE / "tests/test_analysis_audit.py"]
TARGETS = [
    "FutureEventAnalysis.tendsto_scaled_central_binomial",
    "FutureEventAnalysis.tendsto_normalized_remainder",
    "FutureEventAnalysis.tendsto_futureQuotient_normalized",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def finite_inputs() -> dict:
    manifest = json.loads(FROZEN_FINITE.read_text("utf-8"))
    require(manifest["schema"] == "future_event_finite_milestone.v1", "unknown finite milestone")
    for relative, expected in manifest["source_sha256"].items():
        require(sha256(BASE / relative) == expected, f"frozen finite source drift: {relative}")
    report = FROZEN_FINITE.parent / "dependency-audit.json"
    require(sha256(report) == manifest["report_sha256"], "frozen finite dependency report drift")
    return manifest


def own_hashes() -> dict[str, str]:
    return {p.relative_to(BASE).as_posix(): sha256(p) for p in OWN_INPUTS}


def declaration_names() -> list[str]:
    return ["FutureEventAnalysis." + match.group(1)
            for path in PROOFS
            for match in re.finditer(r"^theorem\s+(\w+)", path.read_text("utf-8"), re.MULTILINE)]


def check_report(output: str) -> dict:
    marker = "ANALYTIC_MILESTONE_JSON\n"
    require(output.count(marker) == 1, "missing or repeated analytic report")
    report = json.loads(output.split(marker, 1)[1].splitlines()[0])
    require(report["schema"] == "future_event_analytic_dependency_audit.v1", "unknown analytic schema")
    require([row["name"] for row in report["targets"]] == TARGETS, "analytic target inventory drift")
    nodes = {row["name"]: row for row in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate dependency node")
    for index, target in enumerate(report["targets"]):
        root = target["name"]
        require(target["signature"], f"empty analytic signature: {root}")
        reached: set[str] = set()
        pending = [root]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            require(name in nodes, f"missing analytic dependency node: {name}")
            reached.add(name)
            pending.extend(nodes[name]["direct_dependencies"])
        require(reached == set(target["dependencies"]), f"incomplete analytic closure: {root}")
        actual_axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(actual_axioms == set(target["axioms"]) and actual_axioms <= ALLOWED_AXIOMS,
                f"unexpected or inconsistent analytic axioms: {root}")
        require(not any(name.startswith("Stirling.") for name in reached), "Stirling input was introduced")
        if index < 2:
            require(not any(name.startswith(("FutureEvent.", "RegisteredAbsorptionChains."))
                            for name in reached), f"pure analytic lemma depends on finite model: {root}")
        elif index == 2:
            required = {*TARGETS[:2], "FutureEventAnalysis.futureCardReal",
                        "FutureEvent.card_futureQuotient_closed",
                        "FutureEvent.card_futureQuotient_additive"}
            require(required <= reached, "actual-count bridge or analytic input is missing")
    central = set(report["targets"][0]["dependencies"])
    require({"Real.Wallis.W_eq_factorial_ratio", "Real.Wallis.tendsto_W_nhds_pi_div_two"} <= central,
            "Wallis inputs are missing")
    printed = re.findall(r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)", output)
    require([name for name, _ in printed] == declaration_names(), "analytic axiom inventory drift")
    audit_source = (HERE / "AxiomAudit.lean").read_text("utf-8")
    require(re.findall(r"^#print axioms (\S+)$", audit_source, re.MULTILINE) == declaration_names(),
            "analytic source axiom inventory drift")
    for name, axioms in printed:
        require({a.strip() for a in axioms.split(",") if a.strip()} <= ALLOWED_AXIOMS,
                f"unapproved axiom: {name}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="create an absent analytic milestone once")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    manifest_path = DESTINATION / "manifest.json"
    finite = finite_inputs()
    before = own_hashes()
    for path in [*PROOFS, HERE / "AxiomAudit.lean"]:
        require(not re.search(r"(?<![.\w])(?:sorry|admit)\b|^\s*axiom\s",
                              lean_code(path.read_text("utf-8")), re.MULTILINE),
                f"unfinished analytic proof or custom axiom: {path.name}")
    if args.freeze:
        require(not args.source_only, "cannot freeze without building and auditing")
        require(not DESTINATION.exists(), "analytic milestone already exists; replay is read-only")
        manifest = None
    else:
        manifest = json.loads(manifest_path.read_text("utf-8"))
        require(manifest["schema"] == "future_event_wallis_ratio_milestone.v1", "unknown analytic milestone")
        require(manifest["source_sha256"] == before, "analytic source byte drift")
        require(manifest["finite_manifest_sha256"] == sha256(FROZEN_FINITE), "finite milestone identity drift")
        require(sha256(DESTINATION / "dependency-audit.json") == manifest["report_sha256"],
                "analytic dependency report drift")
    if args.source_only:
        print(json.dumps({"status": "PASS_ANALYTIC_SOURCE_ONLY", "analytic_inputs": len(before),
                          "frozen_finite_inputs": len(finite["source_sha256"])}))
        return 0
    version = run_lake(["env", "lean", "--version"]).strip()
    require(version == finite["lean_executable"], "frozen Lean executable drift")
    run_lake(["build"])
    output_dir = BASE / ".lake/build/lib/lean/analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in PROOFS:
        output = output_dir / (path.stem + ".olean")
        run_lake(["env", "lean", "-o", str(output), str(path)])
    # The declaration-graph walker is reused from the immutable finite audit.
    run_lake(["env", "lean", "-o", str(BASE / ".lake/build/lib/lean/FutureEvent/MilestoneAudit.olean"),
              str(BASE / "FutureEvent/MilestoneAudit.lean")])
    report = check_report(run_lake(["env", "lean", str(HERE / "AxiomAudit.lean")]))
    require(own_hashes() == before, "analytic inputs changed during replay")
    finite_inputs()
    if args.freeze:
        DESTINATION.mkdir(parents=True)
        report_path = DESTINATION / "dependency-audit.json"
        report_path.write_text(canonical_json(report), encoding="utf-8", newline="\n")
        manifest = {
            "schema": "future_event_wallis_ratio_milestone.v1",
            "identity": "LOCAL_EXACT_BYTE_ANALYTIC_PROOF_MILESTONE",
            "release_identity_claimed": False,
            "hal_v1_proof_identity_changed": False,
            "lean_executable": version,
            "mathlib_commit": finite["mathlib_commit"],
            "finite_manifest": FROZEN_FINITE.relative_to(BASE).as_posix(),
            "finite_manifest_sha256": sha256(FROZEN_FINITE),
            "finite_source_files": len(finite["source_sha256"]),
            "source_sha256": before,
            "target_declarations": TARGETS,
            "axiom_audit": declaration_names(),
            "report_sha256": sha256(report_path),
            "scope": "Wallis central-binomial limit, vanishing normalized remainder, and actual future-quotient ratio limit on cofinal horizons n=m+3",
            "excluded_scope": ["Full-summary asymptotics", "Algorithms or complexity bounds", "Changes to the finite milestone"],
            "replay_boundary": "Local kernel replay with pinned cached dependencies; not a fresh-machine cold replay claim",
        }
        manifest_path.write_text(canonical_json(manifest), encoding="utf-8", newline="\n")
    else:
        require(report == json.loads((DESTINATION / "dependency-audit.json").read_text("utf-8")),
                "analytic dependency replay differs from freeze")
    print(json.dumps({"status": "PASS_WALLIS_RATIO_MILESTONE", "analytic_inputs": len(before),
                      "frozen_finite_inputs": len(finite["source_sha256"]),
                      "axiom_checks": len(declaration_names()), "main_targets": len(TARGETS),
                      "dependency_nodes": len(report["nodes"])}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
