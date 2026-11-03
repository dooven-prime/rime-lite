"""Build or check the reader map against four immutable Lean proof milestones."""

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
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE))
from validate_companion import require

REPOSITORY = "https://github.com/dooven-prime/rime-lite"
MAP = HERE / "theorem-map.v1.json"
DOCUMENT = HERE / "THEOREM_TO_SOURCE.md"
LAYERS = [
    ("finite", "milestones/finite-combinatorial-v1/manifest.json",
     "f4f2d444828362f2cb95387a8852f5317bc1057f5be71df2351f9d656369576c",
     "python -B freeze_finite_milestone.py"),
    ("wallis", "analysis/milestones/wallis-ratio-v1/manifest.json",
     "273e87e97bd2f5b779898b1f41c6361efa1debcaeed44fbd5f383f37d3419232",
     "python -B analysis/validate_analysis.py"),
    ("full", "full_summary/milestones/full-summary-v1/manifest.json",
     "1bac05ed4a743dff4ce4f07c32237a38207bd2182e404b56c4de29f0b47899aa",
     "python -B full_summary/validate_bridge.py"),
    ("comparison", "comparison/milestones/observer-growth-v1/manifest.json",
     "5154f2a7d11c7434a7af29c9160965ecc105210b95c33ae118ec4815df9b4fc8",
     "python -B comparison/validate_comparison.py"),
]
PAPERS = {
    "future": {
        "hal_identifier": "hal-05844771v1",
        "commit": "baaded50b61a6a9315a6002ece2dfa9b2c9e16a2",
        "source_path": "papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md",
        "git_blob": "416cb189e690752e3cc8abaa93aae9d945bfbd7c",
        "copy": "manuscripts/future-event-hal-v1.md",
    },
    "fixed_pair": {
        "hal_identifier": "hal-05837829v1",
        "commit": "050cf8ec11e3db263830b46ea95e4062b8e08869",
        "source_path": "papers/unnumbered/circular_coalescence_counts/MANUSCRIPT.md",
        "git_blob": "4947def150b25eb4e2fcc0688c09c82b77907dcf",
        "copy": "manuscripts/fixed-pair-source.md",
    },
}


def row(label, paper, anchor, names, relation="Formalization of the stated result"):
    return {"paper_result": label, "paper": paper, "anchor": anchor,
            "declarations": names.split(), "relation": relation}


ROWS = [
    row("Lemma 5.3: exact coalescence and strict gap", "future", "**Lemma 5.3",
        "FutureEvent.gapProbe_coalesces_iff_holeMove FutureEvent.probe_coalescence_strict_gap"),
    row("Theorem 1 / (6.1): actual future-equivalence classes", "future", "**Theorem 1",
        "FutureEvent.futureEquivalent_iff_normalForm FutureEvent.futureQuotientEquivNormalForms"),
    row("Theorem 2: distinguishing depth 6n-10", "future", "**Theorem 2",
        "FutureEvent.future_inequivalence_uniform_separation FutureEvent.bounded_traces_iff_futureEquivalent"),
    row("Proposition 3.3: actual placement parameters and counts", "future", "**Proposition 3.3",
        "FutureEvent.registerablePlacementParamsEquiv FutureEvent.registeredPlacementParamsEquiv "
        "FutureEvent.card_actual_registerable_placements FutureEvent.card_actual_registered_placements_closed"),
    row("Equation (7.1): exact future quotient count", "future", r"\tag{7.1}",
        "FutureEvent.card_futureQuotient_closed"),
    row("Equation (7.2): actual future quotient asymptotic", "future", r"\tag{7.2}",
        "FutureEventAnalysis.tendsto_futureQuotient_normalized",
        "Same ratio limit; Lean uses the pinned Wallis input"),
    row("Lemma 6.1 and (6.2): full-summary quotient and count", "future", "**Lemma 6.1",
        "FullSummary.event_to_summary_prefix_detection FullSummary.fullQuotientEquivSummaries "
        "FullSummary.card_fullQuotient_closed"),
    row("Theorem 5.1: inherited actual complete-summary count", "fixed_pair", "**Theorem 5.1",
        "RegisteredAbsorptionChains.card_actualRegisteredSummaries_closed",
        "Inherited from the pinned fixed-pair companion; used in future-paper (7.3)"),
    row("Auxiliary bound for (7.3b); fixed-pair Corollary 5.2", "fixed_pair", "**Corollary 5.2",
        "ObserverComparison.summaryBracket_error",
        "Companion strengthening: signed error bound, not a verbatim HAL-v1 lemma"),
    row("Equations (6.2), (7.3b), preceding (7.4): full growth", "future", r"\tag{7.3b}",
        "ObserverComparison.tendsto_fullQuotient_normalized",
        "Same full-quotient limit; negative-binomial tail replaces singularity analysis"),
    row("Equation (7.4): exponential quotient-size separation", "future", r"\tag{7.4}",
        "ObserverComparison.tendsto_full_div_future_normalized"),
    row("Consequence of (7.4): quotient-size ratio tends to infinity", "future", r"\tag{7.4}",
        "ObserverComparison.tendsto_full_div_future_atTop",
        "Explicit formal corollary; not a separately numbered theorem in HAL v1"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_layers() -> list[dict]:
    layers = []
    for name, relative, expected, command in LAYERS:
        path = BASE / relative
        require(digest(path.read_bytes()) == expected, f"frozen manifest drift: {name}")
        manifest = json.loads(path.read_text("utf-8"))
        for source, sha in manifest["source_sha256"].items():
            require(digest((BASE / source).read_bytes()) == sha, f"frozen source drift: {source}")
        report_path = path.parent / "dependency-audit.json"
        require(digest(report_path.read_bytes()) == manifest["report_sha256"], f"graph drift: {name}")
        report = json.loads(report_path.read_text("utf-8"))
        layers.append({"id": name, "manifest": relative, "manifest_sha256": expected,
                       "report": report_path.relative_to(BASE).as_posix(),
                       "report_sha256": manifest["report_sha256"],
                       "source_count": len(manifest["source_sha256"]),
                       "target_count": len(report["targets"]), "node_count": len(report["nodes"]),
                       "replay": command, "manifest_data": manifest, "report_data": report})
    return layers


def manuscript_data(write: bool, check_git: bool) -> dict:
    papers = {}
    for name, identity in PAPERS.items():
        copy = HERE / identity["copy"]
        if copy.exists():
            data = copy.read_bytes()
        else:
            require(write, f"missing pinned manuscript copy: {copy}")
            data = subprocess.check_output(["git", "-C", str(ROOT), "show",
                f'{identity["commit"]}:{identity["source_path"]}'])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == identity["git_blob"], f"pinned manuscript byte drift: {name}")
        if check_git:
            original = subprocess.check_output(["git", "-C", str(ROOT), "show",
                f'{identity["commit"]}:{identity["source_path"]}'])
            require(original == data, f"manuscript Git mismatch: {name}")
        if write and not copy.exists():
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(data)
        papers[name] = {**identity, "sha256": digest(data), "lines": data.decode("utf-8").splitlines(),
                       "source_url": f'{REPOSITORY}/blob/{identity["commit"]}/{identity["source_path"]}',
                       "hal_url": f'https://hal.science/{identity["hal_identifier"]}'}
    return papers


def declaration_location(name: str, layers: list[dict]) -> dict:
    namespace, short = name.rsplit(".", 1)
    matches = []
    for layer in layers:
        for relative, sha in layer["manifest_data"]["source_sha256"].items():
            if not relative.endswith(".lean"):
                continue
            lines = (BASE / relative).read_text("utf-8").splitlines()
            if not any(line == "namespace " + namespace for line in lines):
                continue
            for line, text in enumerate(lines, 1):
                if re.match(r"^(?:noncomputable )?(?:theorem|def) " + re.escape(short) + r"\b", text):
                    matches.append({"name": name, "source": relative, "line": line,
                                    "sha256": sha, "layer": layer["id"]})
    require(len(matches) == 1, f"missing or ambiguous source for {name}")
    return matches[0]


def make_payload(layers: list[dict], papers: dict) -> dict:
    require(papers["future"]["sha256"] == layers[0]["manifest_data"]["target_manuscript"]["sha256"],
            "manuscript does not match the finite milestone")
    versions = {(layer["manifest_data"]["lean_executable"], layer["manifest_data"]["mathlib_commit"])
                for layer in layers}
    require(len(versions) == 1, "incompatible frozen proof toolchains")
    lean, mathlib = versions.pop()
    rows = []
    for spec in ROWS:
        paper = papers[spec["paper"]]
        anchors = [i for i, text in enumerate(paper["lines"], 1) if text.startswith(spec["anchor"])]
        require(len(anchors) == 1, f"ambiguous manuscript anchor: {spec['paper_result']}")
        rows.append({**spec, "paper_line": anchors[0],
                     "paper_source_url": paper["source_url"] + f"#L{anchors[0]}",
                     "sources": [declaration_location(name, layers) for name in spec["declarations"]]})
    comparison = layers[-1]
    graph = {node["name"]: node for node in comparison["report_data"]["nodes"]}
    targets = []
    for index, target in enumerate(comparison["report_data"]["targets"]):
        matching = [item for item in rows if target["name"] in item["declarations"]]
        require(len(matching) == 1, f"final target mapping missing: {target['name']}")
        reached = set(target["dependencies"])
        require(target["name"] in reached, "target absent from its closure")
        require(all(name in graph and set(graph[name]["direct_dependencies"]) <= reached
                    for name in reached), f"incomplete target graph: {target['name']}")
        targets.append({**declaration_location(target["name"], layers),
            "signature": target["signature"], "axioms": target["axioms"],
            "direct_dependencies": graph[target["name"]]["direct_dependencies"],
            "transitive_dependency_count": len(reached),
            "graph_reference": comparison["report"] + f"#/targets/{index}",
            "paper_result": matching[0]["paper_result"], "relation": matching[0]["relation"]})
    return {"schema": "future_event_theorem_to_source.v1",
        "status": "LOCAL_EXACT_BYTE_REVIEW_MAP",
        "public_companion_identity": {"status": "PENDING", "source_commit": None,
                                      "source_tag": None, "archive_identifier": None},
        "scope": "n>=3; actual singleton-seed p,d histories; selected pair {0,1}; unrestricted common future words",
        "lean_executable": lean, "mathlib_commit": mathlib,
        "papers": {key: {k: v for k, v in paper.items() if k != "lines"} for key, paper in papers.items()},
        "layers": [{k: v for k, v in layer.items() if k not in ("manifest_data", "report_data")}
                   for layer in layers],
        "theorem_map": rows, "final_targets": targets,
        "unmapped_paper_scope": ["The specified-probe graph counts (7.6)-(7.7a) and its gap-distribution limit",
                                "The generating-function identity (7.3a) as a formal power-series theorem"]}


def source_link(source: dict) -> str:
    return f'[{source["name"]}](../{source["source"]}#L{source["line"]})'


def render(payload: dict, map_hash: str) -> str:
    lines = ["# Theorem-to-Source Review Map", "",
        "The declared main proof line is closed: actual behavior, exact parameter",
        "equivalences and counts, full-summary observation, and the two growth laws",
        "with exponential quotient-size separation. This map identifies the owning",
        "paper statements and frozen companion proofs separately.", "",
        "**Domain:** `n>=3`, singleton-seed chronological `p,d` histories, selected",
        "source pair `{0,1}`, complete declared outputs, unrestricted future words.", "",
        "**Identity:** the four proof milestones have exact local source identities.",
        "A publicly retrievable version of this complete companion is still pending;",
        "the HAL paper identifiers below do not identify these later Lean files.", "",
        "## Paper-to-Source Table", "",
        "| Paper statement | Frozen Lean source | Correspondence |", "|---|---|---|"]
    for row in payload["theorem_map"]:
        declarations = "<br>".join(source_link(source) for source in row["sources"])
        lines.append(f'| [{row["paper_result"]}]({row["paper_source_url"]}) | {declarations} | {row["relation"]} |')
    lines += ["", "The fixed-pair count is inherited, including its registered-origin",
        "classification and actual dependent fibre construction. The full-summary",
        "bridge identifies literal executions and seed provenance, not just numbers.", "",
        "## Four Final Target Signatures", "",
        "These are the complete elaborated signatures copied from the frozen Lean",
        "dependency report, not hand-transcribed restatements. `fullCardReal m` is",
        "`Nat.card (FullSummary.FullQuotient (m+3))` cast to reals, and",
        "`futureCardReal m` reads the analogous actual future-event quotient.",
        "The cofinal parameter `n=m+3` covers every legal horizon.", ""]
    for target in payload["final_targets"]:
        lines += ["### " + target["name"].split(".")[-1], "", "```lean", target["signature"], "```", "",
            f'Source: {source_link(target)}; SHA-256 `{target["sha256"]}`.', "",
            f'Paper relation: {target["relation"]}.', "",
            f'Dependency closure: {target["transitive_dependency_count"]:,} declarations; '
            f'axioms: `{", ".join(target["axioms"])}`. The full node list and direct edges are at '
            f'[`{target["graph_reference"]}`](../{target["graph_reference"]}).', ""]
    lines += ["## Frozen Layers", "", "| Layer | Inputs / targets / graph nodes | Manifest | Dependency report |",
              "|---|---|---|---|"]
    for layer in payload["layers"]:
        lines.append(f'| {layer["id"]} | {layer["source_count"]} / {layer["target_count"]} / '
                     f'{layer["node_count"]:,} | [manifest](../{layer["manifest"]})<br>'
                     f'`{layer["manifest_sha256"]}` | [graph](../{layer["report"]})<br>`{layer["report_sha256"]}` |')
    lines += ["", "Input and graph-node counts are per layer; dependency closures overlap and",
        "must not be added as independent proofs. Each graph records declaration types,",
        "proof bodies, direct dependencies, target closures and axiom leaves.", "",
        "The mathematical dependency spine is:", "", "```text",
        "actual p,d execution + source order + same-word probes",
        "  -> all-word future-equivalence classification",
        "  -> pure placement parameters <-> actual reachable placements",
        "  -> exact future count -> Wallis -> future growth",
        "actual Moore output + event-to-summary bridge",
        "  -> full quotient <-> null + registerable placements + actual summaries",
        "  -> pinned fixed-pair exact summary count -> negative-binomial tail",
        "  -> full growth -> full/future ratio limit -> divergence", "```", "",
        "This spine covers the declared classification, count and growth conclusions.",
        "The separate probe-graph enumeration/distribution in (7.6)-(7.7a) and the",
        "formal power-series identity (7.3a) are not claimed as Lean coverage here.", "",
        "## Build and Audit", "",
        f'Lean: `{payload["lean_executable"]}`.', "",
        f'Mathlib: `{payload["mathlib_commit"]}`. The package `lean-toolchain`,',
        "`lakefile.toml` and `lake-manifest.json` fix the toolchain and dependency revisions.", "",
        "From `experiments/future_event_minimal_quotient/lean`, first obtain the pinned",
        "Lean toolchain and Lake dependencies (including the Mathlib cache). Then:", "", "```powershell",
        "lake --no-cache build", "python -B validate_companion.py"]
    lines += [layer["replay"] for layer in payload["layers"]]
    lines += ["python -B review/build_theorem_map.py", "```", "",
        "Each layer's ordinary replay rebuilds and audits; it does not rewrite its",
        "freeze. The comparison replay also rebuilds the bound owner and extension",
        "modules, so stale extension `.olean` files are not accepted as evidence.",
        "`--source-only` on the proof validators checks bytes only. These records",
        "document local kernel replay with cached pinned dependencies, not a completed",
        "fresh-machine cold replay.", "",
        "Run the recorded negative controls and finite-control tests separately:", "", "```powershell",
        "python -B -m unittest discover -s tests -p 'test_*.py' -v",
        "python -B -m unittest discover -s analysis/tests -p 'test_*.py' -v",
        "python -B -m unittest discover -s full_summary/tests -p 'test_*.py' -v",
        "python -B -m unittest discover -s comparison/tests -p 'test_*.py' -v",
        "python -B -m unittest discover -s review/tests -p 'test_*.py' -v", "```", "",
        "The parent Python control package is independently versioned and is not a",
        "premise of these all-parameter Lean proofs.", "",
        "## Manuscript and Public Snapshot Identities", ""]
    for paper in payload["papers"].values():
        lines += [f'- Paper: [{paper["hal_identifier"]}]({paper["hal_url"]}); '
            f'[pinned source]({paper["source_url"]}); [read-only reference copy]({paper["copy"]}). '
            f'Source commit `{paper["commit"]}`; SHA-256 `{paper["sha256"]}`.']
    lines += ["", "The reference copies retain exact historical bytes; they do not replace",
        "the owning manuscripts or claim that HAL deposited the later formalization.", "",
        "The independently obtainable **companion** identity remains `PENDING`.",
        "Before advertising public replay, select and commit this complete companion",
        "closure, fix a source tag/commit, and archive an obtainable source bundle",
        "with its checksum and persistent record identifier. Include all four",
        "manifests, reports, their bound sources, the two read-only manuscript copies,",
        "build locks, attribution/license files, this map and its checker. `.lake/`",
        "build products are not the source identity. A normal source archive must",
        "preserve the recorded bytes, rather than applying checkout newline conversion.", "",
        "Record that retrieval identity in a downstream public-source anchor, outside",
        "the four frozen closures. Verify its commit and archived bytes; do not edit",
        "old manifests to turn their truthful local status into a published claim.", "",
        f'Machine-readable map: [`theorem-map.v1.json`](theorem-map.v1.json), SHA-256 `{map_hash}`.', "",
        "The map checker validates source/report hashes, exact declaration locations,",
        "paper anchors and the four target signatures. It does not re-run the kernel;",
        "the separate proof replay commands above perform that work.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this non-proof review map")
    parser.add_argument("--check-git", action="store_true", help="also compare reference copies to pinned Git blobs")
    args = parser.parse_args()
    layers = load_layers()
    papers = manuscript_data(args.write, args.check_git)
    payload = make_payload(layers, papers)
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    document = render(payload, digest(data)).encode("utf-8")
    if args.write:
        MAP.write_bytes(data)
        DOCUMENT.write_bytes(document)
    else:
        require(MAP.read_bytes() == data, "theorem map drift; inspect before regenerating")
        require(DOCUMENT.read_bytes() == document, "reader table drift; inspect before regenerating")
    print(json.dumps({"status": "PASS_THEOREM_TO_SOURCE_MAP", "proof_layers": len(layers),
                      "paper_rows": len(ROWS), "final_signatures": len(payload["final_targets"]),
                      "kernel_replayed": False, "public_companion_identity": "PENDING"}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
