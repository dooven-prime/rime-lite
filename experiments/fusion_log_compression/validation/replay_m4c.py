"""Replay M4-C arbitrary-initial interpretation above unchanged M4-B inputs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import replay as m3
import replay_m4 as m4b


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean_m4c"
MANIFEST = ROOT / "m4c-development-manifest.v1.json"
M4B_MANIFEST = "69456464ff271024c8ab9e97694d5c8fdf125db3c309aadf98fded7fb07612ed"


def verify_inputs():
    m4b.verify_inputs()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["m4b_manifest_sha256"] != M4B_MANIFEST or m3.sha256(m4b.MANIFEST) != M4B_MANIFEST:
        raise RuntimeError("M4-B manifest drift")
    inventory = {p.relative_to(ROOT).as_posix() for p in LEAN.rglob("*.lean")
                 if ".lake" not in p.parts}
    inventory.update(manifest["non_lean_inputs"])
    m3.checked_files(ROOT, manifest["files"], inventory)
    if (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip() != m3.TOOLCHAIN:
        raise RuntimeError("M4-C toolchain drift")
    lock = json.loads((LEAN / "lake-manifest.json").read_text(encoding="utf-8"))
    revisions = [p["rev"] for p in lock["packages"] if p["name"] == "mathlib"]
    if revisions != [m3.MATHLIB]:
        raise RuntimeError("M4-C Mathlib lock drift")
    for name in inventory:
        if name.endswith(".lean") and re.search(r"\b(sorry|admit)\b|^\s*axiom\s",
                (ROOT / name).read_text(encoding="utf-8"), re.MULTILINE):
            raise RuntimeError("placeholder or new axiom: " + name)
    return manifest


def run(command, environment):
    result = subprocess.run(command, cwd=LEAN, env=environment, text=True,
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
        print("PASS_M1_M4B_AND_M4C_INPUTS_ONLY")
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
    if "Build completed successfully" not in build:
        raise RuntimeError("missing Lake completion")
    audit = run([str(lake), "env", "lean", "FusionLogInterpretation/AxiomAudit.lean"], environment)
    axioms = m3.parse_axiom_audit(audit, manifest["axiom_targets"])
    verify_inputs()
    result = {"status": "PASS_M4C_ARBITRARY_INITIAL_INTERPRETATION",
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "lean_version": version, "mathlib_revision": m3.MATHLIB,
              "m4c_manifest_sha256": m3.sha256(MANIFEST),
              "m4b_manifest_sha256": M4B_MANIFEST,
              "m4b_archive_doi": manifest["m4b_archive_doi"],
              "m4b_archive_sha256": manifest["m4b_archive_sha256"],
              "build_completed": True,
              "build_output_sha256": hashlib.sha256(build.encode("utf-8")).hexdigest(),
              "axioms": axioms, "audit_output": audit, "scope": manifest["scope"],
              "open_obligations": manifest["open_obligations"],
              "publication_identity": None, "independent_cold_replay": False}
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "axiom_targets": len(axioms)}))


if __name__ == "__main__":
    main()
