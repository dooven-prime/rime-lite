"""Source-bound replay of the C1-compatible Paper XL/RGT companion."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

LEAN = Path(__file__).resolve().parents[1]
ROOT = LEAN.parents[2]
MANIFEST = LEAN / "companion-manifest.v1.json"
C1 = ROOT / "experiments/fusion_log_compression"
RGT = ROOT / "experiments/rgt_bounded_history_certificates/lean"
TOOLCHAIN = "leanprover/lean4:v4.33.0"
LEAN_COMMIT = "d8b18978322de05a8f3dba51ef03cf5461676c17"
MATHLIB = "db584cd6d46c92f209a44c0f1c829460d327499d"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
SCOPES = ["experiments/paper40/lean", "experiments/rgt_bounded_history_certificates",
          "formal-cases/rgt-bounded-history/v1"]
WORKFLOW = ".github/workflows/paper40-c1-rgt.yml"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def inventory():
    result = {WORKFLOW}
    for prefix in SCOPES:
        for directory, directories, files in os.walk(ROOT / prefix):
            directories[:] = [name for name in directories if name not in {".lake", "__pycache__", "results"}]
            for name in files:
                path = Path(directory) / name
                if path == MANIFEST or path.suffix in {".pyc", ".olean", ".ilean", ".trace"}:
                    continue
                result.add(path.relative_to(ROOT).as_posix())
    return result


def targets(path):
    rows = re.findall(r"^#print axioms (\S+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    if len(rows) != len(set(rows)):
        raise ValueError("duplicate axiom target: " + str(path))
    return rows


def audit(raw, expected):
    rows = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", raw)
    empty = re.findall(r"'([^']+)' does not depend on any axioms", raw)
    names = [name for name, _ in rows] + empty
    if len(names) != len(set(names)) or set(names) != set(expected):
        raise ValueError("axiom audit inventory mismatch")
    result = {name: [a.strip() for a in values.split(",") if a.strip()] for name, values in rows}
    result.update({name: [] for name in empty})
    if any(not set(row) <= ALLOWED for row in result.values()):
        raise ValueError("unexpected axiom")
    return result


def verify_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if set(manifest["files"]) != inventory():
        raise ValueError("companion source inventory mismatch")
    for relative, expected in manifest["files"].items():
        if sha(ROOT / relative) != expected:
            raise ValueError("source byte drift: " + relative)
        if relative.endswith(".lean") and re.search(r"(?<![\w.])(?:sorry|admit|native_decide)\b|^\s*axiom\s",
                (ROOT / relative).read_text(encoding="utf-8"), re.MULTILINE):
            raise ValueError("placeholder, native tactic or new axiom: " + relative)
    if (LEAN / "lean-toolchain").read_text().strip() != TOOLCHAIN:
        raise ValueError("Lean toolchain drift")
    lock = json.loads((LEAN / "lake-manifest.json").read_text())
    if [row["rev"] for row in lock["packages"] if row["name"] == "mathlib"] != [MATHLIB]:
        raise ValueError("Mathlib lock drift")
    for owner in ("paper40", "c1"):
        pin = manifest["owners"][owner]
        ref = "refs/tags/" + pin["tag"]
        if git("rev-parse", ref).decode().strip() != pin["tag_object"] or \
                git("rev-parse", ref + "^{commit}").decode().strip() != pin["commit"]:
            raise ValueError(owner + " source tag drift")
        for relative, expected in pin["files"].items():
            tagged = git("show", ref + ":" + relative)
            if hashlib.sha256(tagged).hexdigest() != expected or sha(ROOT / relative) != expected:
                raise ValueError(owner + " historical/current byte mismatch: " + relative)
    subprocess.run([sys.executable, "-B", str(C1 / "validation/replay_m4c.py"), "--verify-inputs-only"],
                   cwd=C1, check=True, capture_output=True)
    own = targets(LEAN / "AxiomAudit.lean")
    rgt = targets(RGT / "AxiomAudit.lean")
    c1 = targets(C1 / "lean_m4c/FusionLogInterpretation/AxiomAudit.lean")
    if {"paper40": own, "rgt": rgt, "c1": c1} != manifest["axiom_targets"]:
        raise ValueError("declared axiom targets changed")
    return manifest


def execute(command, env, cwd=LEAN):
    process = subprocess.run([str(arg) for arg in command], cwd=cwd, env=env, capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
    raw = process.stdout + process.stderr
    if process.returncode or re.search(r"\bsorryAx\b|Unknown constant|declaration uses 'sorry'", raw):
        raise RuntimeError(raw)
    return raw


def replay(lake, cache=False):
    manifest = verify_inputs()
    env = dict(os.environ)
    env["PATH"] = str(lake.parent) + os.pathsep + env.get("PATH", "")
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    lean = lake.with_name("lean.exe" if os.name == "nt" else "lean")
    version = execute([lean, "--version"], env).strip()
    if LEAN_COMMIT not in version:
        raise ValueError("Lean runtime commit mismatch")
    actual_mathlib = subprocess.check_output(["git", "rev-parse", "HEAD"],
        cwd=LEAN / ".lake/packages/mathlib", text=True).strip()
    if actual_mathlib != MATHLIB:
        raise ValueError("actual Mathlib source mismatch")
    if cache:
        execute([lake, "exe", "cache", "get"], env)
    build = execute([lake, "build"], env)
    if "Build completed successfully" not in build:
        raise ValueError("missing successful Lake completion")
    checks = {}
    for name in ("Checks", "DecisionChecks", "ConsumerBridgeChecks", "CircularObservationChecks",
                 "PrefixObserverChecks", "FixedPrefixGrowthChecks"):
        checks[name] = execute([lake, "env", "lean", name + ".lean"], env)
    checks["rgt-checks"] = execute([lake, "env", "lean", RGT / "Checks.lean"], env)
    checks["rgt-observation-checks"] = execute([lake, "env", "lean", RGT / "ObservationCompressionChecks.lean"], env)
    outputs, axioms = {}, {}
    for owner, path in (("paper40", LEAN / "AxiomAudit.lean"), ("rgt", RGT / "AxiomAudit.lean"),
                        ("c1", C1 / "lean_m4c/FusionLogInterpretation/AxiomAudit.lean")):
        outputs[owner] = execute([lake, "env", "lean", path], env)
        axioms[owner] = audit(outputs[owner], manifest["axiom_targets"][owner])
    signatures = execute([lake, "env", "lean", "Signatures.lean"], env)
    for name in manifest["signature_targets"]:
        if name not in signatures:
            raise ValueError("missing final signature: " + name)
    verify_inputs()
    return {"status": "PASS_C1_PAPERXL_RGT_PROOF_REPLAY", "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "manifest_sha256": sha(MANIFEST), "lean_version": version, "actual_mathlib_revision": actual_mathlib,
            "build_completed": True, "build_output_sha256": hashlib.sha256(build.encode()).hexdigest(),
            "checks": checks, "axioms": axioms, "audit_outputs": outputs, "signatures_output": signatures,
            "independent_cold_replay": False, "runtime_correspondence_proved": False,
            "public_source_tag": None}


def collect(directory):
    if os.environ.get("GITHUB_ACTIONS") != "true" or platform.system() != "Linux":
        raise ValueError("hosted collection requires a GitHub Actions Linux environment")
    proof = json.loads((directory / "proof-replay.json").read_text())
    runtime = json.loads((directory / "consumer-replay.json").read_text())
    if proof["status"] != "PASS_C1_PAPERXL_RGT_PROOF_REPLAY" or not proof["build_completed"]:
        raise ValueError("missing successful proof replay")
    if runtime["status"] != "PASS_FIXED_C1_CONSUMER_CORRESPONDENCE":
        raise ValueError("missing successful finite consumer replay")
    manifest = verify_inputs()
    if proof["manifest_sha256"] != sha(MANIFEST):
        raise ValueError("proof manifest mismatch")
    actual_mathlib = subprocess.check_output(["git", "rev-parse", "HEAD"],
        cwd=LEAN / ".lake/packages/mathlib", text=True).strip()
    if actual_mathlib != MATHLIB or proof["actual_mathlib_revision"] != MATHLIB or LEAN_COMMIT not in proof["lean_version"]:
        raise ValueError("actual toolchain/Mathlib receipt mismatch")
    catalog = json.loads((ROOT / "formal-cases/rgt-bounded-history/v1/cases.json").read_text())
    if runtime["runtime_archive_sha256"] != manifest["owners"]["paper40"]["files"]["experiments/paper40/source/q2-source-v1.zip"]:
        raise ValueError("runtime archive receipt mismatch")
    if [row["id"] for row in runtime["cases"]] != [row["id"] for row in catalog["cases"]]:
        raise ValueError("runtime case inventory mismatch")
    for owner, expected in manifest["axiom_targets"].items():
        if audit(proof["audit_outputs"][owner], expected) != proof["axioms"][owner]:
            raise ValueError("proof axiom receipt mismatch")
    source = os.environ["PROOF_SOURCE_COMMIT"]
    subprocess.run(["git", "diff", "--exit-code", source, "HEAD", "--", *SCOPES, WORKFLOW], cwd=ROOT, check=True)
    result = {"status": "PASS_HOSTED_C1_PAPERXL_RGT_AND_FIXED_CONSUMERS",
              "source_commit": source, "checkout_commit": git("rev-parse", "HEAD").decode().strip(),
              "manifest_sha256": sha(MANIFEST), "owners": manifest["owners"],
              "lean_version": proof["lean_version"], "actual_mathlib_revision": proof["actual_mathlib_revision"],
              "axiom_counts": {owner: len(rows) for owner, rows in proof["axioms"].items()},
              "github": {key: os.environ.get(key) for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
                  "GITHUB_REPOSITORY", "GITHUB_EVENT_NAME", "RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion")},
              "receipt_sha256": {name: sha(directory / name) for name in ("proof-replay.json", "consumer-replay.json")},
              "finite_consumer_query_count": runtime["lean_queries"],
              "runtime_correspondence_proved": False, "public_source_tag": None}
    with (directory / "runner-context.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake", default="lake")
    parser.add_argument("--cache", action="store_true")
    parser.add_argument("--verify-inputs-only", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--collect-ci", type=Path)
    args = parser.parse_args()
    if args.collect_ci:
        print(json.dumps(collect(args.collect_ci)))
        return
    if args.report is not None and args.report.exists():
        raise FileExistsError(args.report)
    if args.verify_inputs_only:
        verify_inputs()
        print("PASS_C1_PAPERXL_RGT_INPUTS_ONLY")
        return
    import shutil
    resolved = shutil.which(args.lake)
    if not resolved:
        raise FileNotFoundError(args.lake)
    result = replay(Path(resolved), args.cache)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "axiom_counts": {k: len(v) for k, v in result["axioms"].items()}}))


if __name__ == "__main__":
    main()
