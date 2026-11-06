"""Replay the budgeted source-ordered M4 stage and unchanged M3 baseline."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import replay as m3


ROOT = Path(__file__).resolve().parents[1]
M4 = ROOT / "lean_m4"
MANIFEST = ROOT / "m4-development-manifest.v2.json"


def verify_inputs():
    m3.verify_inputs()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["m3_manifest_sha256"] != m3.sha256(ROOT / "proof-manifest.v1.json"):
        raise RuntimeError("M3 baseline manifest drift")
    inventory = {p.relative_to(ROOT).as_posix() for p in M4.rglob("*.lean")
                 if ".lake" not in p.parts}
    inventory.update(manifest["non_lean_inputs"])
    m3.checked_files(ROOT, manifest["files"], inventory)
    for path in inventory:
        if path.endswith(".lean") and re.search(
                r"\b(sorry|admit)\b|^\s*axiom\s", (ROOT / path).read_text(encoding="utf-8"), re.MULTILINE):
            raise RuntimeError("placeholder or new axiom: " + path)
    return manifest


def run(command, environment):
    result = subprocess.run(command, cwd=M4, env=environment, text=True,
                            encoding="utf-8", errors="replace", capture_output=True)
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(output)
    if re.search(r"\bsorryAx\b|declaration uses 'sorry'", output):
        raise RuntimeError("placeholder detected in Lean output")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake")
    parser.add_argument("--cache", action="store_true")
    parser.add_argument("--verify-inputs-only", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.report is not None and args.report.exists():
        raise FileExistsError(args.report)
    manifest = verify_inputs()
    if args.verify_inputs_only:
        print("PASS_M3_AND_M4_INPUTS_ONLY")
        return
    lake = m3.lake_binary(args.lake)
    environment = dict(os.environ)
    environment["PATH"] = str(lake.parent) + os.pathsep + environment.get("PATH", "")
    environment["ELAN_TOOLCHAIN"] = m3.TOOLCHAIN
    lean = lake.with_name("lean.exe" if os.name == "nt" else "lean")
    version = run([str(lean), "--version"], environment).strip()
    if manifest["lean_commit"] not in version or "version 4.33.0," not in version:
        raise RuntimeError("unexpected Lean runtime: " + version)
    if args.cache:
        run([str(lake), "exe", "cache", "get"], environment)
    build = run([str(lake), "build"], environment)
    audit = run([str(lake), "env", "lean", "FusionLogReplay/AxiomAudit.lean"], environment)
    axioms = m3.parse_axiom_audit(audit, manifest["axiom_targets"])
    verify_inputs()
    if "Build completed successfully" not in build:
        raise RuntimeError("missing Lake completion")
    result = {"status": "PASS_M4_BUDGETED_SOURCE_ORDERED_REPLAY",
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "lean_version": version, "m4_manifest_sha256": m3.sha256(MANIFEST),
              "mathlib_revision": manifest["mathlib_revision"],
              "m3_manifest_sha256": manifest["m3_manifest_sha256"],
              "build_completed": True, "axioms": axioms, "audit_output": audit,
              "build_output_sha256": hashlib.sha256(build.encode("utf-8")).hexdigest(),
              "scope": manifest["scope"], "open_obligations": manifest["open_obligations"],
              "publication_identity": None, "independent_cold_replay": False}
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "axiom_targets": len(axioms)}))


if __name__ == "__main__":
    main()
