#!/usr/bin/env python3
"""Check the first numbered Paper XLV candidate without claiming publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/paper45"
MANIFEST = PACKAGE / "release-manifest.json"
ALL_R = ROOT / "experiments/fusion_log_compression/lean_all_r"
SOURCE_TAG = "fusion-log-compression-source-v1.0"
SOURCE_PATH = "papers/unnumbered/fusion_log_compression/MANUSCRIPT.md"
SOURCE_SHA256 = "790188c21e075e37cb2f85a837721c5b1f2be4a913d942e228f63ab97db1b6e3"

ARTIFACTS = (
    ("manuscript", "papers/paper45/Paper XLV.md"),
    ("bibliography", "papers/paper45/references-v1.bib"),
    ("reader-pdf", "papers/paper45/paper45_arxiv.pdf"),
    ("paper-index", "papers/paper45/README.md"),
    ("evidence-index", "experiments/paper45/README.md"),
    ("theorem-map", "experiments/paper45/FORMALIZATION_MAP.md"),
    ("candidate-validator", "experiments/paper45/validation/validate_candidate.py"),
    ("all-r-audit-validator", "experiments/paper45/validation/validate_all_r_audit.py"),
    ("candidate-tests", "experiments/paper45/validation/test_candidate.py"),
    ("candidate-workflow", ".github/workflows/paper45-candidate.yml"),
    ("reader-build-entrypoint", "papers/tex/build.py"),
    ("reader-build-driver", "papers/tex/_build.py"),
    ("reader-build-postprocessor", "papers/tex/_postprocess.py"),
    ("reader-build-hrule-cleaner", "papers/tex/_clean_hrule.py"),
    ("paper41-anchor", "docs/release-anchors/paper41-v1.0.json"),
    ("paper42-anchor", "docs/release-anchors/paper42-v1.0.json"),
    ("m5-archive-anchor", "docs/release-anchors/fusion-log-m5-source-v1.0.json"),
    ("m4d-lock", "experiments/fusion_log_compression/m4d-development-manifest.v1.json"),
    ("m5-lock", "experiments/fusion_log_compression/m5-development-manifest.v1.json"),
    ("m4d-validator", "experiments/fusion_log_compression/validation/replay_m4d.py"),
    ("m5-validator", "experiments/fusion_log_compression/validation/replay_m5.py"),
    ("m3-validator", "experiments/fusion_log_compression/validation/replay.py"),
    ("all-r-index", "experiments/fusion_log_compression/lean_all_r/README.md"),
    ("all-r-lakefile", "experiments/fusion_log_compression/lean_all_r/lakefile.toml"),
    ("all-r-lock", "experiments/fusion_log_compression/lean_all_r/lake-manifest.json"),
    ("all-r-toolchain", "experiments/fusion_log_compression/lean_all_r/lean-toolchain"),
    ("finite-controls-index", "experiments/fusion_log_compression/controls/README.md"),
    ("finite-core", "experiments/fusion_log_compression/controls/core.py"),
    ("finite-arbitrary-control", "experiments/fusion_log_compression/controls/fusion_log_arbitrary_start_control.py"),
    ("finite-math-control", "experiments/fusion_log_compression/controls/audit_math.py"),
    ("finite-arbitrary-result", "experiments/fusion_log_compression/controls/results/arbitrary-start.c2.json"),
    ("finite-math-result", "experiments/fusion_log_compression/controls/results/mathematical-controls.c2.json"),
)

IDENTITY = {
    "schema": "rime.paper45.first-numbered-candidate.v1",
    "paper_id": "PAPER45",
    "release_version": "1.0",
    "intended_release_tag": "paper45-v1.0",
    "status": "RELEASE_CANDIDATE",
    "release_identity_claimed": False,
    "external_anchor_claimed": False,
    "independent_cold_reproduction_claimed": False,
}

ANCHORS = (
    (41, "chenAbsorption2026", "10.5281/zenodo.24137725"),
    (42, "chenProperArc2026", "10.5281/zenodo.24138941"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def data(relative: str) -> bytes:
    path = Path(relative)
    require(not path.is_absolute() and all(part not in (".", "..") for part in path.parts),
            f"noncanonical artifact path: {relative}")
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT.resolve()) and resolved.is_file(),
            f"missing or external artifact: {relative}")
    return resolved.read_bytes()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def artifact_paths() -> list[tuple[str, str]]:
    sources = sorted([*ALL_R.glob("*.lean"), *(ALL_R / "FusionLogAllR").rglob("*.lean")])
    require(len(sources) >= 15, "All-R source inventory unexpectedly small")
    rows = list(ARTIFACTS)
    rows.extend(("all-r-source", path.relative_to(ROOT).as_posix()) for path in sources)
    require(len({path for _, path in rows}) == len(rows), "duplicate artifact path")
    return rows


def candidate_manifest() -> dict[str, object]:
    return {
        **IDENTITY,
        "artifacts": [
            {"role": role, "path": path, "sha256": digest(data(path)), "size": len(data(path))}
            for role, path in artifact_paths()
        ],
    }


def check_manifest(manifest: dict[str, object]) -> int:
    require(set(manifest) == set(IDENTITY) | {"artifacts"}, "manifest field drift")
    for key, expected in IDENTITY.items():
        require(manifest[key] == expected, f"manifest {key} drift")
    rows = manifest["artifacts"]
    expected = artifact_paths()
    require(isinstance(rows, list) and
            [(row["role"], row["path"]) for row in rows] == expected,
            "artifact inventory drift")
    for row in rows:
        require(set(row) == {"role", "path", "sha256", "size"}, "artifact field drift")
        payload = data(row["path"])
        require(row["sha256"] == digest(payload) and row["size"] == len(payload),
                f"artifact digest drift: {row['path']}")
    return len(rows)


def check_citations(manuscript: str, bibliography: str) -> None:
    keys = set(re.findall(r"@\w+\s*\{\s*([^,]+),", bibliography))
    cited = set(re.findall(r"(?<!\w)@([A-Za-z][A-Za-z0-9_:-]*)", manuscript))
    require(cited <= keys, f"unresolved citations: {sorted(cited - keys)}")
    require("Paper XLV (version 1.0)" in manuscript, "numbered identity missing")
    titles = re.findall(r"(?m)^\*\*(?:Theorem|Lemma|Proposition|Corollary) "
                        r"\d+\.\d+ \([^)]+\)\.\*\*$", manuscript)
    require(len(titles) == 16 and "**Theorem 4.1 (log and endpoint realization).**" in titles,
            "descriptive statement titles missing")
    require(re.search(r"(?m)^### (?:Theorem|Lemma|Proposition|Corollary)", manuscript)
            is None, "legacy statement heading style")
    require("hal-" not in manuscript.lower() and "hal-" not in bibliography.lower(),
            "unreleased HAL submission cited as a publication")
    require("chenFusionLogSource2026" not in cited, "unpublished C1 draft cited as a paper")
    for number, key, doi in ANCHORS:
        entry = re.search(rf"@\w+\s*\{{\s*{re.escape(key)}\s*,(.*?)^\}}",
                          bibliography, re.MULTILINE | re.DOTALL)
        require(key in cited and entry is not None, f"published input not cited: {key}")
        require(re.search(rf"(?m)^\s*doi\s*=\s*\{{{re.escape(doi)}\}}\s*,?\s*$",
                          entry.group(1)) is not None, f"published input DOI drift: {key}")
        anchor = json.loads(data(f"docs/release-anchors/paper{number}-v1.0.json"))
        require(anchor["paper_id"] == f"PAPER{number}" and
                anchor["publication_status"] == "PUBLISHED" and
                anchor["external_anchor"]["doi"] == doi,
                f"published input anchor drift: Paper {number}")


def check_source_tag() -> None:
    payload = subprocess.run(["git", "show", f"refs/tags/{SOURCE_TAG}:{SOURCE_PATH}"],
                             cwd=ROOT, capture_output=True, check=True).stdout
    require(digest(payload) == SOURCE_SHA256, "retained C1 tag source drift")
    require(digest(data(SOURCE_PATH)) == SOURCE_SHA256, "retained C1 worktree source drift")


def check_inputs() -> None:
    check_source_tag()
    check_citations(data("papers/paper45/Paper XLV.md").decode("utf-8"),
                    data("papers/paper45/references-v1.bib").decode("utf-8"))
    pdf = data("papers/paper45/paper45_arxiv.pdf")
    require(pdf.startswith(b"%PDF-") and b"%%EOF" in pdf[-100:], "invalid reader PDF")
    require(data("experiments/fusion_log_compression/lean_all_r/lean-toolchain").strip() ==
            b"leanprover/lean4:v4.33.0", "Lean toolchain drift")
    audit = data("experiments/fusion_log_compression/lean_all_r/FusionLogAllR/AxiomAudit.lean")
    targets = re.findall(rb"(?m)^#print axioms\s+(\S+)\s*$", audit)
    require(len(targets) == 69 and len(set(targets)) == 69,
            "All-R axiom target inventory drift")
    lock = json.loads(data("experiments/fusion_log_compression/lean_all_r/lake-manifest.json"))
    mathlib = next((item for item in lock["packages"] if item["name"] == "mathlib"), None)
    require(mathlib is not None and mathlib["rev"] ==
            "db584cd6d46c92f209a44c0f1c829460d327499d", "Mathlib pin drift")
    m5_anchor = json.loads(data("docs/release-anchors/fusion-log-m5-source-v1.0.json"))
    require(m5_anchor["status"] == "PUBLISHED_DEPOSIT_BYTES_VERIFIED" and
            m5_anchor["doi"] == "10.5281/zenodo.24123627",
            "M5 archive anchor drift")
    for name in ("replay_m4d.py", "replay_m5.py"):
        subprocess.run(["python", "-O", "-B", name, "--verify-inputs-only"],
                       cwd=ROOT / "experiments/fusion_log_compression/validation",
                       check=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="create an absent manifest")
    args = parser.parse_args()
    try:
        check_inputs()
        if args.freeze:
            require(not MANIFEST.exists(), "candidate manifest already exists")
            MANIFEST.write_text(json.dumps(candidate_manifest(), indent=2) + "\n",
                                encoding="utf-8", newline="\n")
        manifest = json.loads(MANIFEST.read_bytes())
        count = check_manifest(manifest)
        print(f"PASS Paper XLV candidate: {count} bound artifacts; inherited input locks verified")
        print("Source closure only; finite controls and Lean replay are separate checks.")
    except (KeyError, OSError, StopIteration, TypeError, ValueError,
            subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL Paper XLV candidate: {error}") from error


if __name__ == "__main__":
    main()
