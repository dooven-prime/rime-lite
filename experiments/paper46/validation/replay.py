"""Replay the Paper XLVI development package without refreshing its input lock."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
MANIFEST = PACKAGE / "development-manifest.json"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
PAPER_INPUTS = [
    "Paper XLVI.md", "README.md", "references-v1.bib",
    "paper46_arxiv.pdf",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_paths() -> set[str]:
    paths = {
        path.relative_to(ROOT).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_file()
        and path != MANIFEST
        and not {".lake", "__pycache__", "results"}.intersection(
            path.relative_to(PACKAGE).parts
        )
    }
    paths.update(f"papers/paper46/{name}" for name in PAPER_INPUTS)
    return paths


def verify_inputs() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["status"] != "DEVELOPMENT_CANDIDATE":
        raise ValueError("This replay expects a development candidate, not a release")
    rows = manifest["inputs"]
    expected = [row["path"] for row in rows]
    if len(set(expected)) != len(expected):
        raise ValueError("Duplicate input path")
    actual = candidate_paths()
    if set(expected) != actual:
        raise ValueError(
            f"Input inventory mismatch: missing={sorted(set(expected) - actual)}, "
            f"unbound={sorted(actual - set(expected))}"
        )
    for row in rows:
        path = ROOT / row["path"]
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise ValueError(f"Source byte drift: {row['path']}")
    provenance = json.loads((PACKAGE / "extraction-provenance.json").read_text())
    if len(provenance["files"]) != provenance["copied_file_count"]:
        raise ValueError("Extraction inventory count mismatch")
    for row in provenance["files"]:
        path = PACKAGE / row["path"]
        if not path.resolve().is_relative_to(PACKAGE) or not path.is_file():
            raise ValueError(f"Invalid extraction path: {row['path']}")
        if sha256(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError(f"Extracted source changed: {row['path']}")
    return {"status": "PASS", "input_count": len(rows),
            "manifest_sha256": sha256(MANIFEST)}


def check_axioms(output: str, expected: list[str]) -> dict:
    entries = re.findall(
        r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|"
        r"does not depend on any axioms)", output, re.MULTILINE
    )
    if len(entries) != len(expected):
        raise ValueError(f"Incomplete axiom audit: {len(entries)} != {len(expected)}")
    observed = set()
    matched = set()
    for name, axioms in entries:
        targets = [target for target in expected
                   if name == target or name.endswith("." + target)]
        if len(targets) != 1 or targets[0] in matched:
            raise ValueError(f"Unexpected or duplicate audit target: {name}")
        matched.add(targets[0])
        observed.update(item.strip() for item in axioms.split(",") if item.strip())
    if observed - ALLOWED_AXIOMS:
        raise ValueError(f"Unexpected axioms: {sorted(observed - ALLOWED_AXIOMS)}")
    return {"status": "PASS", "target_count": len(entries),
            "axioms": sorted(observed), "target_names": [name for name, _ in entries]}


def run_command(command: list[str], cwd: Path, receipt: dict) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8",
                            errors="replace", stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=900)
    receipt["commands"].append({"command": command,
                                "cwd": cwd.relative_to(ROOT).as_posix(),
                                "returncode": result.returncode, "output": result.stdout})
    if result.returncode:
        raise ValueError(f"Command failed ({result.returncode}): {command}\n{result.stdout}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", action="store_true")
    parser.add_argument("--lake", default="lake", help="Pinned toolchain Lake executable")
    parser.add_argument("--report", type=Path, help="Write a generated local JSON receipt")
    args = parser.parse_args()
    if args.report:
        destination = args.report.resolve()
        protected = {ROOT / name for name in candidate_paths()} | {MANIFEST}
        if (destination in protected or ".lake" in destination.parts
                or (destination.is_relative_to(PACKAGE)
                    and not destination.is_relative_to(PACKAGE / "results"))):
            parser.error("Report must not overwrite an input or a build artifact")
    receipt = {"schema": "rime.paper46.local-replay.v1",
               "started_at": datetime.now(timezone.utc).isoformat(),
               "evidence_layer": "LOCAL_REPLAY", "commands": [],
               "independent_cold_replay": False, "python_version": sys.version,
               "lean": {"status": "NOT_RUN"}}
    try:
        receipt["inputs"] = verify_inputs()
        run_command([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                     "experiments/paper46/validation", "-p", "test_*.py"], ROOT, receipt)
        run_command([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                     "experiments/paper46", "-p", "test_*.py"], ROOT, receipt)
        if args.lean:
            lean_root = PACKAGE / "lean"
            receipt["local_build_products_present_before"] = (lean_root / ".lake").exists()
            lock = json.loads((lean_root / "lake-manifest.json").read_text())
            if lock["packages"]:
                raise ValueError("Expected core-only Lean dependency closure")
            toolchain = (lean_root / "lean-toolchain").read_text().strip()
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            if toolchain != manifest["lean_toolchain"]:
                raise ValueError("Toolchain differs from the candidate lock")
            version = run_command([args.lake, "env", "lean", "--version"], lean_root, receipt)
            expected_version = toolchain.split(":v", 1)[1]
            if not re.search(r"version " + re.escape(expected_version) + r"(?:,|\s)", version):
                raise ValueError(f"Wrong Lean version: {version.strip()}")
            run_command([args.lake, "--no-cache", "build"], lean_root, receipt)
            source = (lean_root / "RSR2/AxiomAudit.lean").read_text(encoding="utf-8")
            targets = re.findall(r"^#print axioms (\S+)\s*$", source, re.MULTILINE)
            if not targets or len(set(targets)) != len(targets):
                raise ValueError("Empty or duplicate axiom target list")
            if len(targets) != manifest["axiom_audit_target_count"]:
                raise ValueError("Axiom target count differs from the candidate lock")
            output = run_command([args.lake, "env", "lean", "RSR2/AxiomAudit.lean"],
                                 lean_root, receipt)
            receipt["lean"] = {"toolchain": toolchain, "version": version.strip(),
                               **check_axioms(output, targets)}
        # Catch concurrent source changes rather than certifying mixed input bytes.
        if verify_inputs() != receipt["inputs"]:
            raise ValueError("Input identity changed during replay")
        receipt["status"] = "PASS"
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        receipt.update(status="FAIL", error=str(error))
    receipt["completed_at"] = datetime.now(timezone.utc).isoformat()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary = {key: receipt[key] for key in ("status", "evidence_layer", "lean")}
    if "error" in receipt:
        summary["error"] = receipt["error"]
    if "target_names" in summary["lean"]:
        summary["lean"] = {k: v for k, v in summary["lean"].items() if k != "target_names"}
    print(json.dumps(summary, indent=2))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
