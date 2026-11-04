"""Export or read-only check the frozen Proper-arc theorem-to-source map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from validate_companion import ALLOWED_AXIOMS, as_json, check_inputs, require, sha256
from classification.validate_classification import closure

BASE = Path(__file__).resolve().parent
MARKDOWN = BASE/"THEOREM_TO_SOURCE_MAP.md"
INDEX = BASE/"theorem-to-source-map.v1.json"
P = "ProperArc.Chains."
UNION_SCOPE = ("The union graph counts all audited declarations in the nine frozen reports, "
               "not merely the union of the 17 selected theorem closures.")

MILESTONES = [
    ("M1", "Origin construction", "milestones/origin-realization-v1/manifest.json",
     "56769c0fa07686e5431de1f2b667eea8bd46619c979d1fe5d4e308e7c6d00c96", "validate_companion.py"),
    ("M2", "Named origin interfaces", "interfaces/milestones/origin-interfaces-v1/manifest.json",
     "c3725a2407c2af450ad9c095abcbca89ba5cad13f1331d008c05e7134a2202f8", "interfaces/validate_interfaces.py"),
    ("M3", "Exhaustive origin classification", "classification/milestones/origin-classification-v1/manifest.json",
     "cf0bc343a73e7466b870c36843e072472159779373ad3e85964d17e69acea2d0", "classification/validate_classification.py"),
    ("M4", "Actual clean chain construction", "chains/milestones/chain-construction-v1/manifest.json",
     "5979c315a7a8f534efeb29948cb0f4f8ed151c99a7e06cd6059f3bf58aa9e5fd", "chains/validate_chains.py"),
    ("M5", "Actual chain equivalence", "converse/milestones/actual-chain-equivalence-v1/manifest.json",
     "3dac55c745d644ebb80565fdeb749b411f0ca7e18e0a9c35d4d7b1fc2ee3a731", "converse/validate_converse.py"),
    ("M6", "Actual placement fibres", "fibres/milestones/placement-fibre-v1/manifest.json",
     "7d85df042a583508908a028e98499b52e7e8d7507d23d5c70f6e210faa21658d", "fibres/validate_fibres.py"),
    ("M7", "Actual dependent summaries", "summary/milestones/dependent-summary-v1/manifest.json",
     "aef536f33efdd1b114e87f9b96ffdce1ddceec94c9a41d10b572f092a38b95a6", "summary/validate_summary.py"),
    ("M8", "Exact actual-summary count", "counting/milestones/summary-count-v1/manifest.json",
     "6535bd701625f294302f4ecadbb686a1a04cd22e9a6c110fe4d050619aa531ba", "counting/validate_counting.py"),
    ("M9", "Independent combinatorial refinements", "refinements/milestones/combinatorial-refinements-v1/manifest.json",
     "54ac894b75ab88a1eb66058f5bdb6b90d6ced237b3d8c104099777188d1febec", "refinements/validate_refinements.py"),
]

# Mathematical owner, declaration owner and evidence owner are recorded separately.
THEOREMS = [
    ("O1", "Proposition 3.1, constructive direction", "ProperArc.run_originWord", "ProperArc/OriginBoundary.lean", "M1",
     "Each legal internal cut has an explicit actual word, its complete origin and the cut-independent boundary placement."),
    ("O2", "Proposition 3.1, exhaustive direction", "ProperArc.actual_registered_origin_unique", "classification/OriginExhaustive.lean", "M3",
     "Every actual registered history has exactly one legal internal origin cut; no clean-state premise."),
    ("O3", "Proposition 3.1, actual origin equivalence", "ProperArc.actualRegistrationOriginsEquivCuts", "classification/OriginExhaustive.lean", "M3",
     "Actual registration origins are equivalent to Fin (r-1)."),
    ("C1", "Lemma 4.1 / Theorem 4.2, construction", P+"realize_clean_code", "chains/CleanRealization.lean", "M4",
     "Every code at every origin has one actual clean word realizing the full selected records."),
    ("C2", "Theorem 4.2, actual chain equivalence", P+"actualSelectedChainsEquivCode", "converse/ActualChainConverse.lean", "M5",
     "Actual fixed-origin selected chains are equivalent to Code (n-r), including arbitrary nonclean histories."),
    ("C3", "Theorem 4.2, total chain count", P+"card_actualSelectedChains", "converse/ActualChainConverse.lean", "M5",
     "The actual fixed-origin selected-chain set has cardinality 3^(n-r)."),
    ("F1", "Theorem 5.2, positive-complement fibre", P+"positivePlacementFibreEquiv", "fibres/PlacementEquivalence.lean", "M6",
     "Native cut/site parameters and actual fixed-origin/code placements are equivalent for k>0."),
    ("F0", "Theorem 5.2, full-carrier fibre", P+"fullPlacementFibreEquiv", "fibres/PlacementEquivalence.lean", "M6",
     "For k=0 the actual fixed-origin/code placement fibre is independently equivalent to ZMod n."),
    ("F2", "Theorem 5.2, uniform fibre interface", P+"codePlacementFibreEquiv", "fibres/PlacementEquivalence.lean", "M6",
     "CodeFiberParams uses a separate full-carrier branch and is equivalent to actual placements."),
    ("F3", "Theorem 5.2, exact fibre cardinality", P+"card_actualCodePlacements", "fibres/PlacementEquivalence.lean", "M6",
     "The actual fixed-origin/code placement count is n * choose(n+k-2,k), including k=0."),
    ("S1", "Theorem 5.3, dependent equivalence", P+"actualRegisteredSummariesEquivParams", "summary/SummaryEquivalence.lean", "M7",
     "Actual registered summaries are equivalent to the pure dependent origin/code/fibre parameter sum."),
    ("S2", "Theorem 5.3, same-word certificate", P+"decodeSummary_same_word", "summary/SummaryEquivalence.lean", "M7",
     "One actual singleton-seed word jointly realizes the decoded origin, full chain and literal placement."),
    ("N1", "Theorem 6.1 / equation (6.1)", P+"card_actual_registered_summaries", "counting/SummaryCardinality.lean", "M8",
     "The exact binomial total counts ActualRegisteredSummaries c r, not an assumed formal image."),
    ("N2", "Section 6, shortest-complement boundary", P+"card_actual_registered_summaries_short_complement", "counting/SummaryCardinality.lean", "M8",
     "For n>=3 and r=n-1 the actual summary count is (n-2)*n*(n+1)."),
    ("R1", "Theorem 4.2, absorption-length refinement", P+"card_actualSelectedChains_length", "refinements/ChainLength.lean", "M9",
     "Actual fixed-origin chains with j records are counted by choose(n-r,j)*2^j for every natural j."),
    ("R2", "Theorem 5.2 / equation (5.4), rank refinement", P+"card_actualRankCodePlacements", "refinements/RankFibre.lean", "M9",
     "Actual rank-s placements number s*choose(k-1,s-2)*choose(n,s) for k>0 and 2<=s<=k+1."),
    ("R0", "Theorem 5.2, rank-one boundary", P+"card_actualFullRankCodePlacements", "refinements/RankFibre.lean", "M9",
     "The k=0 actual rank-one placement fibre has exactly n phases."),
]

PENDING = [
    {"paper": "Proposition 7.1", "status": "PAPER_PROOF_PRESENT_LEAN_NOT_STARTED",
     "scope": "Identify the actual r=2,c=0 proper-arc summary type with the fixed-pair owner type, then transport its equivalences."},
    {"paper": "Propositions 8.1 and 8.2; Corollary 8.3", "status": "PAPER_PROOF_PRESENT_LEAN_NOT_STARTED",
     "scope": "Fixed-n, diagonal fixed-r and unscaled summary-count generating functions, with their distinct coefficient domains."},
    {"paper": "Theorem 8.4", "status": "PAPER_PROOF_PRESENT_LEAN_NOT_STARTED",
     "scope": "Fixed-r 9/2 growth, leading coefficient and explicit tail/error estimates for the proper-arc count."},
]


def digest(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def audit_graph(report):
    nodes = {node["name"]: node for node in report["nodes"]}
    require(len(nodes) == len(report["nodes"]), "duplicate map dependency node")
    for target in report["targets"]:
        reached = closure(nodes, target["name"])
        require(reached == set(target["dependencies"]), f"incomplete map closure: {target['name']}")
        axioms = {name for name in reached if nodes[name]["kind"] == "axiom"}
        require(axioms == set(target["axioms"]) and axioms <= ALLOWED_AXIOMS,
                f"unapproved map axiom: {target['name']}")
        require(target["signature"], f"missing frozen signature: {target['name']}")
    return nodes


def collect(check_git=False):
    check_inputs(check_git)
    records, owners, graphs, union, inputs = [], {}, {}, {}, {}
    baseline = None
    for mid, label, path, expected, validator in MILESTONES:
        manifest_path = BASE/path
        require(sha256(manifest_path) == expected, f"map manifest drift: {mid}")
        manifest = json.loads(manifest_path.read_text("utf-8"))
        report_path = manifest_path.parent/"dependency-audit.json"
        require(sha256(report_path) == manifest["report_sha256"], f"map report drift: {mid}")
        identity = {key: manifest[key] for key in ("lean_executable", "mathlib_commit")}
        if "target_manuscript" in manifest:
            identity["target_manuscript"] = manifest["target_manuscript"]
        else:
            require(mid == "M2" and manifest["origin_manifest_sha256"] == records[0]["manifest_sha256"],
                    "unbound interface manuscript owner")
            identity["target_manuscript"] = baseline["target_manuscript"]
        if baseline is None:
            baseline = identity
        require(identity == baseline, f"map owner or toolchain drift: {mid}")
        for source, sha in manifest["source_sha256"].items():
            require(source not in inputs or inputs[source] == sha, f"conflicting map source binding: {source}")
            require(sha256(BASE/source) == sha, f"map source drift: {source}")
            inputs[source] = sha
        for parent, sha in manifest.get("preserved_milestones", {}).items():
            require(sha256(BASE/parent) == sha, f"map predecessor drift: {parent}")
        report = json.loads(report_path.read_text("utf-8"))
        nodes = audit_graph(report)
        require([row["name"] for row in report["targets"]] == manifest["target_declarations"],
                f"map target inventory drift: {mid}")
        for name, node in nodes.items():
            require(name not in union or union[name] == node, f"map declaration graph conflict: {name}")
            union[name] = node
        owners[mid], graphs[mid] = manifest, {"report": report, "nodes": nodes}
        records.append({"id": mid, "label": label, "manifest": path, "manifest_sha256": expected,
            "report": report_path.relative_to(BASE).as_posix(), "report_sha256": manifest["report_sha256"],
            "validator": validator, "source_input_count": len(manifest["source_sha256"]),
            "axiom_query_count": len(manifest["axiom_audit"]), "target_count": len(report["targets"]),
            "declaration_node_count": len(nodes),
            "observed_axioms": sorted({name for name, node in nodes.items() if node["kind"] == "axiom"})})
    entries = []
    for tid, paper, name, source, mid, contract in THEOREMS:
        owner, graph = owners[mid], graphs[mid]
        require(source in owner["source_sha256"], f"unbound map source owner: {name}")
        match = re.search(r"^(?:theorem|(?:noncomputable\s+)?def)\s+"+re.escape(name.rsplit(".", 1)[1])+r"\b",
                          (BASE/source).read_text("utf-8"), re.MULTILINE)
        require(match is not None, f"missing owning source declaration: {name}")
        target = next((row for row in graph["report"]["targets"] if row["name"] == name), None)
        require(target is not None, f"declaration is not a frozen map target: {name}")
        reached = closure(graph["nodes"], name)
        entries.append({"id": tid, "paper_statement": paper, "declaration": name,
            "source": source, "source_line": (BASE/source).read_text("utf-8")[:match.start()].count("\n")+1,
            "source_sha256": owner["source_sha256"][source], "owner_milestone": mid,
            "contract": contract, "status": "KERNEL_CHECKED_IN_OWNING_LOCAL_FREEZE",
            "signature": target["signature"], "axioms": target["axioms"],
            "type_constants": target.get("type_constants"),
            "dependencies": sorted(reached), "dependency_node_count": len(reached),
            "closure_graph_sha256": digest([graph["nodes"][item] for item in sorted(reached)])})
    by_id = {entry["id"]: entry for entry in entries}
    for entry in entries:
        mapped = [other["id"] for other in entries if other is not entry and other["declaration"] in entry["dependencies"]]
        entry["mapped_dependencies"] = mapped
        entry["nearest_mapped_dependencies"] = [tid for tid in mapped if not any(
            tid != other and by_id[tid]["declaration"] in by_id[other]["dependencies"] for other in mapped)]
    pins = json.loads((BASE/"upstream-manifest.json").read_text("utf-8"))
    return {"schema": "proper_arc_lean_theorem_to_source.v1",
        "verification_mode": "FROZEN_SOURCE_AND_REPORT_GRAPH_CHECK_NOT_NEW_KERNEL_REPLAY",
        "companion_public_release_identity": None, "hal_v1_proof_identity_changed": False,
        **baseline, "upstream": {key: pins[key] for key in ("upstream_source_commit", "upstream_source_directory",
            "underlying_fixed_pair_commit", "upstream_archive_url", "upstream_archive_file_bytes_verified_here")},
        "allowed_axioms": sorted(ALLOWED_AXIOMS), "milestones": records, "theorems": entries,
        "pending_formalization": PENDING,
        "unique_frozen_input_count": len(inputs), "frozen_source_sha256": dict(sorted(inputs.items())),
        "union_declaration_node_count": len(union),
        "union_declaration_node_scope": UNION_SCOPE,
        "graph_digest_encoding": "UTF-8 compact JSON, sorted object keys, node records sorted by declaration name",
        "union_graph_sha256": digest([union[name] for name in sorted(union)]),
        "map_source_sha256": {name: sha256(BASE/name) for name in ("theorem_map.py", "map_tests/test_theorem_map.py")}}


def render(data):
    paper = data["target_manuscript"]
    rows = ["# Proper-Arc Lean Theorem-To-Source Map", "",
        "This map connects the proper-arc paper's closed finite classification and",
        "enumeration statements to their owning Lean declarations and frozen audit",
        "closures. Mathematical ownership remains with",
        f"[{paper['hal_identifier']}](https://hal.science/{paper['hal_identifier']});",
        "the companion supplies the separate formal proof artifacts below.", "",
        "## Scope And Proof Spine", "",
        "The domain is `c : ZMod n`, `2<=r<n` (hence n>=3), the identity singleton",
        "seed, the fixed proper source arc `arc c r`, and chronological actual `p,d`",
        "words with no length cutoff. Write `m=n-r` and let k be the decoded number",
        "of outside source atoms. Origins and selected chains retain ordered source",
        "parent blocks; placements are literal generated packet placements.", "",
        "$$", r"\boxed{\begin{gathered}", r"\text{Actual origin classification}\\",
        r"\Downarrow\\", r"\text{Actual chain equivalence}\\", r"\Downarrow\\",
        r"\text{Actual placement fibres}\\", r"\Downarrow\\",
        r"\text{Actual summary equivalence}\\", r"\Downarrow\\",
        r"\text{Exact and refined counts}", r"\end{gathered}}", "$$", "",
        "This is the assembly sequence, not an assertion that every preceding",
        "interface is a proof dependency of every later one. In particular, the",
        "fixed-origin chain construction consumes the explicit origin construction;",
        "origin exhaustiveness is separately needed to recover the origin component",
        "of arbitrary actual summaries. The declaration dependencies below are read",
        "from the frozen proof graphs, not inferred from file imports.", "",
        "## Theorem-To-Source Table", "",
        "Each row is kernel-checked in its owning local freeze. The actual-history",
        "types are not replaced by formal decoder images in the counting statements.", "",
        "| ID | Paper statement and closed contract | Owning Lean source | Freeze |",
        "|---|---|---|---|"]
    for item in data["theorems"]:
        rows.append(f"| {item['id']} | {item['paper_statement']}. {item['contract']} | "
                    f"[`{item['declaration']}`]({item['source']}#L{item['source_line']}) | {item['owner_milestone']} |")
    rows += ["", "M2 is a thin named-interface freeze rather than another classification",
        "theorem. M4's clean witnesses are used for construction; the converse",
        "classifications and actual-set equivalences do not assume cleanliness.", "",
        "## Actual Declaration Dependencies", "",
        "A table edge omits intervening helpers but is verified by the complete",
        "transitive declaration closure. Nearest mapped inputs are the transitive",
        "reduction among the selected rows, not the raw direct Lean dependencies.", "",
        "| Target | Nearest mapped inputs | Closure nodes | Actual axiom leaves |",
        "|---|---|---:|---|"]
    for item in data["theorems"]:
        rows.append(f"| {item['id']} | {', '.join(item['nearest_mapped_dependencies']) or '(no other mapped target)'} | "
                    f"{item['dependency_node_count']:,} | {', '.join('`'+a+'`' for a in item['axioms']) or '(none)'} |")
    rows += ["", "A later stage can use the underlying converse/helper interface without",
        "using the earlier packaged equivalence as a declaration. For example, S1",
        "uses `actual_chain_decode_encode` through its summary-code readback, while",
        "the F1 inverse uses `actual_fiber_params`. Their full helper dependencies",
        "remain in the owning reports even when C2 is absent from a mapped-input row.", "",
        "The two M9 refinements are independent of one another and of N1.",
        "R1 restricts the actual chain equivalence by literal record length; R2",
        "restricts the positive fibre equivalence by the literal placement's packet",
        "count. R0 uses the independent full-carrier phase equivalence. The k=0",
        "fibre is not replaced by the empty positive-complement sigma type.", "",
        "Full dependency-name lists and per-theorem closure graph hashes are in",
        "[`theorem-to-source-map.v1.json`](theorem-to-source-map.v1.json). Each",
        "owning report stores every node's kind and direct declaration dependencies.",
        "The graph hashes cover canonical sorted node records; exact Lean source",
        "bytes are separately bound by the source hashes. A graph hash alone is not",
        "a hash of a compiled proof term.", "",
        "## Frozen Versions And Audit Results", "",
        f"- Lean executable: `{data['lean_executable']}`.",
        f"- Mathlib commit: `{data['mathlib_commit']}`.",
        f"- Paper source tag: `{paper['source_tag']}`.",
        f"- Paper content commit: `{paper['source_commit']}`.",
        f"- [Pinned manuscript]({paper['reference_copy']}) SHA-256: `{paper['sha256']}`.",
        f"- Generic `RegisteredAbsorptionChains` source: `{data['upstream']['upstream_source_commit']}`;",
        f"  underlying fixed-pair source: `{data['upstream']['underlying_fixed_pair_commit']}`.",
        "  These are owners of reused interpreter, source-order, placement and pure",
        "  parameter machinery, not substitutes for the proper-arc actual-set proofs.", "",
        "| Freeze | Scope | Bound inputs | Axiom queries | Targets | Graph nodes |",
        "|---|---|---:|---:|---:|---:|"]
    for item in data["milestones"]:
        rows.append(f"| [{item['id']}]({item['manifest']}) | {item['label']} | {item['source_input_count']} | "
                    f"{item['axiom_query_count']} | {item['target_count']} | {item['declaration_node_count']:,} |")
    rows += ["", "| Freeze | Manifest SHA-256 | Dependency report SHA-256 |", "|---|---|---|"]
    for item in data["milestones"]:
        rows.append(f"| {item['id']} | `{item['manifest_sha256']}` | [`{item['report_sha256']}`]({item['report']}) |")
    rows += ["", f"Together these freezes bind {data['unique_frozen_input_count']} distinct input files.",
        f"Their compatible declaration graphs have {data['union_declaration_node_count']:,} distinct nodes.",
        data["union_declaration_node_scope"],
        "Per-freeze query and node counts overlap and must not be added as independent",
        "proof totals. Every recorded target closure was checked for missing nodes",
        "and axiom leaves; only `propext`, `Classical.choice` and `Quot.sound` occur.", "",
        "These are local companion freeze identities. No separate public companion",
        "tag or deposit is assigned by this map, and the paper's HAL v1 proof identity",
        "is unchanged. The upstream archive URL is provenance metadata; downloaded",
        "archive file bytes were not verified here. The recorded kernel replays use",
        "pinned cached dependencies, not a fresh-machine cold replay.", "",
        "## Reproduction", "",
        "From this Lean directory, the following read-only command checks all nine",
        "manifest/report identities, every bound source, all reported target closures",
        "and axiom sets, and the deterministic map outputs:", "",
        "```powershell", "python -B theorem_map.py --check-upstream-git",
        "python -B -m unittest discover -s map_tests -p 'test_*.py' -v", "```", "",
        "It checks frozen evidence; it does not execute the Lean kernel anew. A",
        "standalone source copy can omit `--check-upstream-git`; that option additionally",
        "compares reused inputs and the manuscript with local historical Git objects.", "",
        "For a fresh local kernel replay use the pinned Lean/Mathlib versions and",
        "the owning validator for the desired freeze (no `--freeze` option):", "", "```powershell"]
    for item in data["milestones"]:
        rows.append(f"python -B {item['validator']}")
    rows += ["```", "", "`RIME_LAKE_EXE` may select the pinned `lake.exe`; `lake --no-cache build`",
        "alone retains the original origin target. The later validators compile",
        "their named modules and audit their complete target closures. The bootstrap",
        "entry is [`bootstrap_inputs.py`](bootstrap_inputs.py); the dependency lock",
        "and [`upstream-manifest.json`](upstream-manifest.json) specify the reused",
        "versions. A portable snapshot must include the bound inputs, manifests,",
        "reports and validators, not a machine-specific `.lake/packages` junction.", "",
        "## Separate Later Formalization", "",
        "The pinned paper already contains proofs of the following results. They",
        "are not kernel-verified conclusions of this companion snapshot:", "",
        "| Paper owner | Remaining Lean obligation |", "|---|---|"]
    for item in data["pending_formalization"]:
        rows.append(f"| {item['paper']} | {item['scope']} |")
    rows += ["", "In particular, the exact finite counts are closed here; a Lean proof",
        "of their generating functions or fixed-r 9/2 growth requires a separate",
        "analytic/formal-series layer. Numerically specializing the closed proper-arc",
        "formula at r=2 is not the pending cross-owner actual-type identification.", "",
        "## Frozen Target Signatures", "",
        "These are verbatim signatures from the owning kernel audit reports. The",
        "paper contracts and source links above disambiguate older pretty-printer",
        "outputs that suppress inferred subtype binder types. M9 additionally records",
        "the constants in each target's type to pin its actual-history domain."]
    for item in data["theorems"]:
        rows += ["", f"### {item['id']}: `{item['declaration']}`", "", "```lean", item["signature"], "```"]
    return "\n".join(rows)+"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate only the two map outputs")
    parser.add_argument("--check-upstream-git", action="store_true")
    args = parser.parse_args()
    data = collect(args.check_upstream_git)
    outputs = ((INDEX, as_json(data)), (MARKDOWN, render(data)))
    for path, expected in outputs:
        if args.write:
            path.write_text(expected, encoding="utf-8", newline="\n")
        else:
            require(path.read_bytes() == expected.encode("utf-8"), f"theorem map output drift: {path.name}")
    print(json.dumps({"status": "PASS_FROZEN_THEOREM_TO_SOURCE_MAP", "new_kernel_replay": False,
        "milestones": len(data["milestones"]), "mapped_theorems": len(data["theorems"]),
        "unique_frozen_inputs": data["unique_frozen_input_count"],
        "union_declaration_nodes": data["union_declaration_node_count"]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
