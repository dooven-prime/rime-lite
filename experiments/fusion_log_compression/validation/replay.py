"""Verify pinned inputs, build the Lean package, and replay targeted axiom checks."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
TOOLCHAIN = "leanprover/lean4:v4.33.0"
MATHLIB = "db584cd6d46c92f209a44c0f1c829460d327499d"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
UPSTREAM_COMMIT = "050cf8ec11e3db263830b46ea95e4062b8e08869"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_files(base: Path, expected: dict[str, str], actual: set[str]) -> None:
    if set(expected) != actual:
        raise RuntimeError(f"source inventory mismatch under {base}")
    for relative, digest in expected.items():
        path = (base / relative).resolve()
        if not path.is_relative_to(base.resolve()):
            raise RuntimeError(f"source path escapes its root: {relative}")
        if sha256(path) != digest:
            raise RuntimeError(f"source byte drift: {relative}")


def verify_inputs() -> dict:
    pin = json.loads((ROOT / "upstream-pin.v1.json").read_text(encoding="utf-8"))
    if pin["commit"] != UPSTREAM_COMMIT or pin["source_file_count"] != len(pin["files"]):
        raise RuntimeError("upstream identity or inventory count drift")
    upstream = ROOT / pin["vendored_directory"]
    inventory = {str(p.relative_to(upstream)).replace("\\", "/")
                 for p in upstream.rglob("*.lean")}
    checked_files(upstream, pin["files"], inventory)
    manifest = json.loads((ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    actual = {str(p.relative_to(ROOT)).replace("\\", "/")
              for p in LEAN.rglob("*.lean")
              if ".lake" not in p.parts and "upstream" not in p.relative_to(LEAN).parts}
    actual.update(manifest["non_lean_inputs"])
    checked_files(ROOT, expected, actual)
    if (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip() != TOOLCHAIN:
        raise RuntimeError("toolchain identity drift")
    lock = json.loads((LEAN / "lake-manifest.json").read_text(encoding="utf-8"))
    mathlib = [p for p in lock["packages"] if p["name"] == "mathlib"]
    if len(mathlib) != 1 or mathlib[0]["rev"] != MATHLIB:
        raise RuntimeError("Mathlib lock drift")
    for relative in actual:
        if relative.endswith(".lean"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            if re.search(r"\b(sorry|admit)\b|^\s*axiom\s", source, re.MULTILINE):
                raise RuntimeError(f"placeholder or new axiom declaration: {relative}")
    return manifest


def lake_binary(explicit: str | None) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if not candidate.is_file():
            raise RuntimeError(f"missing Lake binary: {candidate}")
        return candidate
    executable = "lake.exe" if os.name == "nt" else "lake"
    homes = [Path(os.environ["ELAN_HOME"])] if os.environ.get("ELAN_HOME") else []
    homes.append(Path.home() / ".elan")
    slot = TOOLCHAIN.replace("/", "--").replace(":", "---")
    for home in homes:
        candidate = home / "toolchains" / slot / "bin" / executable
        if candidate.is_file():
            return candidate.resolve()
    found = shutil.which("lake")
    if found:
        return Path(found).resolve()
    raise RuntimeError(f"install {TOOLCHAIN} with elan, or pass --lake")


def run(command: list[str], env: dict[str, str]) -> str:
    result = subprocess.run(command, cwd=LEAN, env=env, text=True,
                            encoding="utf-8", errors="replace", capture_output=True)
    output = result.stdout + result.stderr
    if result.returncode:
        sys.stderr.write(output)
        raise RuntimeError(f"command failed ({result.returncode}): {command}")
    if re.search(r"\bsorryAx\b|declaration uses 'sorry'", output):
        raise RuntimeError("placeholder detected in Lean output")
    return output


def parse_axiom_audit(audit: str, targets: list[str]) -> dict[str, list[str]]:
    rows = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", audit)
    rows += [(name, "") for name in
             re.findall(r"'([^']+)' does not depend on any axioms", audit)]
    observations = dict(rows)
    if len(rows) != len(observations) or set(observations) != set(targets):
        raise RuntimeError(f"axiom target mismatch: {sorted(observations)}")
    result = {}
    for theorem, axioms in observations.items():
        names = [name.strip() for name in axioms.split(",") if name.strip()]
        if not set(names) <= ALLOWED_AXIOMS:
            raise RuntimeError(f"unexpected axioms for {theorem}: {sorted(names)}")
        result[theorem] = names
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake", help="explicit Lake binary in the pinned toolchain")
    parser.add_argument("--cache", action="store_true", help="fetch official Mathlib compiled cache")
    parser.add_argument("--verify-inputs-only", action="store_true")
    parser.add_argument("--report", type=Path, help="write a new local replay report; never overwrite")
    args = parser.parse_args()
    if args.report is not None and args.report.exists():
        raise RuntimeError(f"report already exists: {args.report}")
    manifest = verify_inputs()
    if args.verify_inputs_only:
        print("PASS_PINNED_INPUTS_ONLY")
        return 0
    lake = lake_binary(args.lake)
    lean = lake.with_name("lean.exe" if os.name == "nt" else "lean")
    env = dict(os.environ)
    env["PATH"] = str(lake.parent) + os.pathsep + env.get("PATH", "")
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    version = run([str(lean), "--version"], env).strip()
    if "version 4.33.0," not in version or manifest["lean_commit"] not in version:
        raise RuntimeError(f"unexpected Lean runtime: {version}")
    if args.cache:
        run([str(lake), "exe", "cache", "get"], env)
    build = run([str(lake), "build"], env)
    audit = run([str(lake), "env", "lean", "FusionLogCompression/AxiomAudit.lean"], env)
    observations = parse_axiom_audit(audit, manifest["axiom_targets"])
    verify_inputs()
    report = {
        "status": "PASS_LOCAL_M3_REPLAY", "lean_version": version,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "mathlib_revision": MATHLIB, "upstream_pin_sha256": sha256(ROOT / "upstream-pin.v1.json"),
        "proof_manifest_sha256": sha256(ROOT / "proof-manifest.v1.json"),
        "build_completed": "Build completed successfully" in build,
        "axioms": observations,
        "audit_output": audit,
        "replay_scope": "local replay; no independent cold-environment claim",
        "nonclaims": ["M4 complete-log replay", "shortest-word optimum", "full-paper formalization"],
    }
    if not report["build_completed"]:
        raise RuntimeError("missing Lake build completion")
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "axiom_targets": len(observations)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
