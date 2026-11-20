"""Read-only replay of the selected Paper XLVII reader and Lean closure."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
LEAN = PACKAGE / "lean"
MANIFEST = PACKAGE / "candidate-manifest.v2.json"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
MENUS = [
    ("single_block", "ClosedAudit.lean", "ClosedSignatures.lean", 25),
    ("forest_moment", "RSR2History/ForestGapMomentAudit.lean", "RSR2History/ForestGapMomentSignatures.lean", 57),
    ("forest_relative", "RSR2History/ForestRelativeReplayAudit.lean", "RSR2History/ForestRelativeReplaySignatures.lean", 34),
    ("all_upper", "RSR2History/AllUpperExtremaAudit.lean", "RSR2History/AllUpperExtremaSignatures.lean", 25),
]
LIBRARIES = {"Paper47", "Paper47Closed", "ClosedAudit", "ClosedSignatures", "RSR2History",
             "RSR2", "FusionLogCompression", "FusionLogAllR", "RegisteredAbsorptionChains"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_files(directory):
    for base, dirs, files in os.walk(directory):
        dirs[:] = [name for name in dirs if name not in {".lake", "__pycache__"}]
        for name in files:
            yield Path(base) / name


def inputs():
    paths = [ROOT / name for name in (
        ".github/workflows/paper47-candidate.yml",
        "papers/tex/_build.py",
        "papers/tex/_clean_hrule.py",
        "papers/tex/_postprocess.py",
    )]
    paths += [p for p in (ROOT / "papers/paper47").iterdir() if p.is_file()]
    paths += [PACKAGE / name for name in (".gitattributes", "LICENSE", "README.md", "THEOREM_MAP.md", "SCOPE.md",
                                         "reader-profile.json", "results/reader-build.v1.json")]
    for directory in (PACKAGE / "lean", PACKAGE / "validation", PACKAGE / "provenance"):
        for p in local_files(directory):
            if p.is_file() and (p.suffix in {".lean", ".toml", ".py", ".json"} or p.name == "lean-toolchain"):
                paths.append(p)
    return sorted(set(paths))


def source_index():
    return {p.relative_to(ROOT).as_posix(): {"sha256": digest(p), "size": p.stat().st_size}
            for p in inputs()}


def parse_axioms(output, targets):
    rows = []
    for m in re.finditer(r"'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", output):
        axioms = sorted(a.strip() for a in (m[2] or "").split(",") if a.strip())
        if set(axioms) - ALLOWED:
            raise ValueError(f"unapproved axiom: {m[1]}: {axioms}")
        rows.append({"declaration": m[1], "axioms": axioms})
    if Counter(r["declaration"] for r in rows) != Counter(targets):
        raise ValueError("audit did not resolve exactly the selected target menu")
    return rows


def menus():
    result = []
    for name, audit, signatures, count in MENUS:
        targets = re.findall(r"^#print axioms (\S+)", (LEAN / audit).read_text(), re.M)
        checks = re.findall(r"^#check (\S+)", (LEAN / signatures).read_text(), re.M)
        if targets != checks or len(targets) != count or len(set(targets)) != count:
            raise ValueError(f"target menu mismatch: {name}")
        result.append((name, audit, signatures, targets))
    return result


def check_structure():
    provenance = json.loads((LEAN / "extraction-provenance.json").read_text())
    for row in provenance["proof_sources"]:
        if digest(PACKAGE / row["target"]) != row["sha256"]:
            raise ValueError(f"copied source drift: {row['target']}")
    ancestor = PACKAGE / "provenance/single-block-source-manifest.v1.json"
    if digest(ancestor) != provenance["ancestor_index_sha256"]:
        raise ValueError("ancestor index drift")
    old = json.loads(ancestor.read_text())["sha256"]
    preserved = 0
    for name, expected in old.items():
        if name.startswith("lean_single_block/") and name.endswith(".lean"):
            if digest(LEAN / name.removeprefix("lean_single_block/")) != expected:
                raise ValueError(f"ancestor proof byte drift: {name}")
            preserved += 1
    if preserved != provenance["unchanged_ancestor_lean_sources"]:
        raise ValueError("ancestor proof count differs")
    sources = [p for p in local_files(LEAN) if p.suffix == ".lean"]
    for p in sources:
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            if not line.startswith("import "):
                continue
            for module in line.split("--", 1)[0].split()[1:]:
                prefix = module.split(".")[0]
                if prefix in LIBRARIES:
                    if not (LEAN / (module.replace(".", "/") + ".lean")).is_file():
                        raise ValueError(f"missing local import: {module}")
                elif prefix not in {"Mathlib", "Init", "Lean", "Std"}:
                    raise ValueError(f"external unresolved import: {module}")
    lock = json.loads((LEAN / "lake-manifest.json").read_text())
    if any(p["type"] != "git" for p in lock["packages"]):
        raise ValueError("external local dependency in lock")
    if "path =" in (LEAN / "lakefile.toml").read_text():
        raise ValueError("external local dependency in Lake config")
    text = (ROOT / "papers/paper47/Paper XLVII.md").read_text(encoding="utf-8")
    tags = re.findall(r"\\tag\{([^}]+)\}", text)
    if len(tags) != len(set(tags)) or text.count("**Proof.**") != text.count(r"$\square$"):
        raise ValueError("manuscript equation labels or proof delimiters differ")
    receipt = json.loads((PACKAGE / "results/reader-build.v1.json").read_text())
    for name, expected in receipt["inputs"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"reader input drift: {name}")
    if digest(ROOT / receipt["reader_pdf"]) != receipt["reader_pdf_sha256"]:
        raise ValueError("reader PDF drift")
    groups = menus()
    return {"mirrored_lean_sources": len(provenance["proof_sources"]),
            "local_lean_sources": len(sources), "preserved_ancestor_lean_sources": preserved,
            "audit_occurrences": sum(len(g[3]) for g in groups),
            "unique_audit_declarations": len({d for g in groups for d in g[3]})}


def run(command, cwd=LEAN):
    p = subprocess.run(list(map(str, command)), cwd=cwd, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=3600)
    if p.returncode:
        raise RuntimeError(f"failed command {command}\n{p.stdout[-8000:]}\n{p.stderr[-4000:]}")
    return {"command": list(map(str, command)), "exit_code": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize-manifest", action="store_true")
    parser.add_argument("--verify-inputs-only", action="store_true")
    parser.add_argument("--lean", action="store_true")
    parser.add_argument("--lake", default="lake")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.initialize_manifest and (args.lean or args.verify_inputs_only or args.report):
        parser.error("manifest initialization is separate from replay")
    summary = check_structure()
    actual = source_index()
    if args.initialize_manifest:
        with MANIFEST.open("x", encoding="utf-8") as stream:
            json.dump({"status": "LOCAL_SELECTED_CANDIDATE", "publication_identity": None,
                       "remote_base": "43835de9ac21465412f80e8074fa8576f9a9b65c",
                       "inputs": actual, **summary}, stream, indent=2)
            stream.write("\n")
        print(json.dumps({"indexed_files": len(actual), **summary}, indent=2))
        return
    if actual != json.loads(MANIFEST.read_text())["inputs"]:
        raise ValueError("candidate source byte drift")
    report = {"status": "PASS", "scope": "LOCAL_SELECTED_READER_AND_LEAN_REPLAY",
              "utc": datetime.now(timezone.utc).isoformat(),
              "manifest_sha256": digest(MANIFEST), "publication_identity": None,
              "lean_replayed": False,
              "cache_policy": "pinned installed cache; not a cold independent replay", **summary}
    if not args.verify_inputs_only:
        report["tests"] = run([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                               PACKAGE / "validation", "-p", "test_*.py"], cwd=ROOT)
    if args.lean:
        lake = shutil.which(args.lake)
        if not lake:
            raise ValueError("Lake executable unavailable")
        report["lean_version"] = run([lake, "--no-cache", "env", "lean", "--version"])
        if "version 4.33.0" not in report["lean_version"]["stdout"]:
            raise ValueError("wrong Lean version")
        lock = json.loads((LEAN / "lake-manifest.json").read_text())
        for p in lock["packages"]:
            package = LEAN / ".lake/packages" / p["name"]
            rev = run(["git", "-C", package, "rev-parse", "HEAD"])["stdout"].strip()
            if rev != p["rev"]:
                raise ValueError(f"dependency revision mismatch: {p['name']}")
            run(["git", "-C", package, "diff", "--exit-code", "HEAD", "--",
                 "*.lean", "*.toml", "lean-toolchain"])
        report["dependency_revisions"] = {p["name"]: p["rev"] for p in lock["packages"]}
        report["build"] = run([lake, "--no-cache", "build", "Paper47"])
        report["groups"] = []
        for name, audit, signatures, targets in menus():
            output = run([lake, "--no-cache", "env", "lean", audit])
            report["groups"].append({"name": name, "axiom_audit": parse_axioms(output["stdout"], targets),
                                     "audit_output": output,
                                     "signatures": run([lake, "--no-cache", "env", "lean", signatures])})
        report["lean_replayed"] = True
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"tests", "lean_version", "build", "groups"}}, indent=2))


if __name__ == "__main__":
    main()
