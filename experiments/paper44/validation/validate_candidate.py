#!/usr/bin/env python3
"""Check the first numbered Paper XLIV candidate without claiming publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper44"
MANIFEST = PACKAGE / "release-manifest.json"
LEAN = PACKAGE / "lean"
sys.path.insert(0, str(LEAN))
from freeze_structure_count import source_inventory  # noqa: E402


ARTIFACTS = (
    ("manuscript", "papers/paper44/Paper XLIV.md"),
    ("bibliography", "papers/paper44/references-v1.bib"),
    ("reader-pdf", "papers/paper44/paper44_arxiv.pdf"),
    ("paper-index", "papers/paper44/README.md"),
    ("evidence-index", "experiments/paper44/README.md"),
    ("critical-window-review", "experiments/paper44/review/CRITICAL_WINDOW_REVIEW.md"),
    ("lean-index", "experiments/paper44/lean/README.md"),
    ("lean-milestone-index", "experiments/paper44/lean/FINITE_COMBINATORIAL_MILESTONE.md"),
    ("lean-milestone", "experiments/paper44/lean/milestones/structure-count-v1/manifest.json"),
    ("finite-controls-index", "experiments/paper44/controls/README.md"),
    ("finite-report", "experiments/paper44/controls/results/prefix_observer_spectrum.v1.json"),
    ("finite-core", "experiments/paper44/controls/core.py"),
    ("finite-minimizer", "experiments/paper44/controls/minimum_sufficient_quotient.py"),
    ("finite-spectrum-control", "experiments/paper44/controls/prefix_observer_spectrum_control.py"),
    ("finite-control-tests", "experiments/paper44/controls/test_prefix_label_update.py"),
    ("analytic-control-tests", "experiments/paper44/controls/test_prefix_observer_supercritical.py"),
    ("finite-validator", "experiments/paper44/validation/validate_controls.py"),
    ("lean-audit-validator", "experiments/paper44/validation/validate_lean_audit.py"),
    ("candidate-validator", "experiments/paper44/validation/validate_candidate.py"),
    ("candidate-tests", "experiments/paper44/validation/test_candidate.py"),
    ("candidate-workflow", ".github/workflows/paper44-candidate.yml"),
    ("line-ending-policy", ".gitattributes"),
    ("reader-build-entrypoint", "papers/tex/build.py"),
    ("reader-build-driver", "papers/tex/_build.py"),
    ("reader-build-postprocessor", "papers/tex/_postprocess.py"),
    ("reader-build-hrule-cleaner", "papers/tex/_clean_hrule.py"),
    ("paper41-anchor", "docs/release-anchors/paper41-v1.0.json"),
    ("paper43-anchor", "docs/release-anchors/paper43-v1.0.json"),
)

IDENTITY = {
    "schema": "rime.paper44.first-numbered-candidate.v1",
    "paper_id": "PAPER44",
    "release_version": "1.0",
    "intended_release_tag": "paper44-v1.0",
    "status": "RELEASE_CANDIDATE",
    "release_identity_claimed": False,
    "external_anchor_claimed": False,
    "independent_cold_reproduction_claimed": False,
    "receipt_self_exclusion": True,
}
ANCHORS = (
    (41, "chenPaper41v1", "10.5281/zenodo.24137725"),
    (43, "chenPaper43v1", "10.5281/zenodo.24148747"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def path_for(relative: str) -> Path:
    require(bool(relative) and "\\" not in relative, f"invalid path: {relative}")
    path = Path(relative)
    require(not path.is_absolute() and all(part not in (".", "..") for part in path.parts),
            f"noncanonical path: {relative}")
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT.resolve()), f"path escapes repository: {relative}")
    require(resolved.is_file(), f"missing artifact: {relative}")
    return resolved


def data(relative: str) -> bytes:
    return path_for(relative).read_bytes()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_json(relative: str) -> dict:
    value = json.loads(data(relative))
    require(isinstance(value, dict), f"JSON object required: {relative}")
    return value


def artifact_rows() -> list[dict[str, object]]:
    return [
        {"role": role, "path": path, "sha256": digest(data(path)), "size": len(data(path))}
        for role, path in ARTIFACTS
    ]


def candidate_manifest() -> dict[str, object]:
    return {**IDENTITY, "artifacts": artifact_rows()}


def check_manifest() -> int:
    manifest = json.loads(MANIFEST.read_bytes())
    require(isinstance(manifest, dict), "candidate manifest must be an object")
    require(set(manifest) == set(IDENTITY) | {"artifacts"}, "manifest field set drift")
    for key, expected in IDENTITY.items():
        require(manifest[key] == expected, f"manifest {key} drift")
    rows = manifest["artifacts"]
    require(isinstance(rows, list) and len(rows) == len(ARTIFACTS), "artifact count drift")
    require([(row["role"], row["path"]) for row in rows] == list(ARTIFACTS),
            "artifact role/path drift")
    require(len({row["path"] for row in rows}) == len(rows), "duplicate artifact path")
    for row in rows:
        require(set(row) == {"role", "path", "sha256", "size"}, "artifact field drift")
        payload = data(row["path"])
        require(row["sha256"] == digest(payload), f"artifact digest drift: {row['path']}")
        require(row["size"] == len(payload), f"artifact size drift: {row['path']}")
    return len(rows)


def check_review() -> None:
    review = data("experiments/paper44/review/CRITICAL_WINDOW_REVIEW.md").decode("utf-8")
    for relative in ("papers/paper44/Paper XLIV.md", "papers/paper44/references-v1.bib",
                     "papers/paper44/paper44_arxiv.pdf"):
        pattern = rf"^\| `{re.escape(relative)}` \| `([0-9a-f]{{64}})` \|$"
        match = re.search(pattern, review, re.MULTILINE)
        require(match is not None and match.group(1) == digest(data(relative)),
                f"review binding drift: {relative}")


def check_citations() -> None:
    manuscript = data("papers/paper44/Paper XLIV.md").decode("utf-8")
    bibliography = data("papers/paper44/references-v1.bib").decode("utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,]+),", bibliography))
    cited = set(re.findall(r"(?<!\w)@([A-Za-z][A-Za-z0-9_:-]*)", manuscript))
    require(cited <= keys, f"unresolved citations: {sorted(cited - keys)}")
    require("This paper is Paper XLIV (version 1.0)" in manuscript,
            "numbered reader identity missing")
    require("## 8. Claim Status and Boundary" in manuscript,
            "claim boundary missing")
    require("\\boxed" not in manuscript, "unexpected boxed result")
    positions = [manuscript.find(rf"\tag{{6.{index}}}") for index in range(14, 18)]
    require(all(position >= 0 for position in positions) and positions == sorted(positions),
            "critical-window equation tags missing or out of order")
    require("hal-" not in manuscript.lower(), "historical HAL identity in numbered paper")
    pdf = data("papers/paper44/paper44_arxiv.pdf")
    require(pdf.startswith(b"%PDF-") and b"%%EOF" in pdf[-100:], "invalid reader PDF")

    for number, key, doi in ANCHORS:
        entry = re.search(rf"@\w+\s*\{{\s*{re.escape(key)}\s*,(.*?)^\}}",
                          bibliography, re.MULTILINE | re.DOTALL)
        require(key in cited and entry is not None, f"published input not cited: {key}")
        require(re.search(rf"(?m)^\s*doi\s*=\s*\{{{re.escape(doi)}\}}\s*,?\s*$",
                          entry.group(1)) is not None,
                f"published input DOI mismatch: {key}")
        anchor = read_json(f"docs/release-anchors/paper{number}-v1.0.json")
        require(anchor["paper_id"] == f"PAPER{number}" and
                anchor["publication_status"] == "PUBLISHED" and
                anchor["release_identity_claimed"] is True and
                anchor["external_anchor"]["doi"] == doi,
                f"published input anchor drift: Paper {number}")
        tag = anchor["release_tag"]
        require(tag["name"] == f"paper{number}-v1.0", "input tag name drift")
        for suffix, expected in (("^{tag}", tag["tag_object_sha"]),
                                 ("^{}", tag["target_commit_sha"])):
            actual = subprocess.run(["git", "rev-parse", f"refs/tags/{tag['name']}{suffix}"],
                                    cwd=ROOT, check=True, capture_output=True,
                                    text=True).stdout.strip()
            require(actual == expected, f"published input tag drift: Paper {number}")


def check_lean_source() -> None:
    milestone = read_json("experiments/paper44/lean/milestones/structure-count-v1/manifest.json")
    require(milestone["schema"] == "paper44_structure_count_milestone.v1", "Lean schema drift")
    require(milestone["release_identity_claimed"] is False and
            milestone["independent_cold_reproduction_claimed"] is False and
            milestone["scope"]["analytic_layer_included"] is False,
            "Lean milestone overpromoted")
    require(milestone["scope"]["n_min"] == 3 and milestone["scope"]["depth_min"] == 1,
            "Lean finite domain drift")
    require(data("experiments/paper44/lean/lean-toolchain").strip() ==
            b"leanprover/lean4:v4.33.0", "Lean toolchain drift")
    require(milestone["package_revisions"]["mathlib"] ==
            "db584cd6d46c92f209a44c0f1c829460d327499d", "Mathlib pin drift")
    inventory = source_inventory()
    require(len(inventory) == 102 and inventory == milestone["source_sha256"],
            "Lean source closure drift")
    axioms = milestone["axiom_audit"]
    require(len(axioms) == 86 and all(set(values) <=
            {"propext", "Classical.choice", "Quot.sound"} for values in axioms.values()),
            "Lean axiom inventory drift")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="create an absent candidate manifest")
    args = parser.parse_args()
    try:
        check_review()
        check_citations()
        check_lean_source()
        if args.freeze:
            require(not MANIFEST.exists(), "candidate manifest already exists")
            MANIFEST.write_text(json.dumps(candidate_manifest(), indent=2) + "\n",
                                encoding="utf-8", newline="\n")
        count = check_manifest()
        print(f"PASS Paper XLIV first-numbered candidate: {count} artifacts; "
              "102 Lean inputs; 86 recorded axiom outputs")
        print("Candidate source check only; CI recompiles Lean and replays controls.")
    except (KeyError, OSError, TypeError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL Paper XLIV candidate: {error}") from error


if __name__ == "__main__":
    main()
