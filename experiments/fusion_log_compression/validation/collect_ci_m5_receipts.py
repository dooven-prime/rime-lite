"""Bind the actual M5 runner receipt to the existing C/D acceptance record."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess

import replay_m5 as m5
import verify_ci_m5_ancestor as ancestor


def collect(directory):
    if os.environ.get("GITHUB_ACTIONS") != "true" or platform.system() != "Linux":
        raise RuntimeError("M5 hosted collection requires a GitHub Actions Linux runner")
    base_path = directory / "runner-context.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    if base["status"] != "PASS_HOSTED_UBUNTU_M4C_M4D_REPLAY":
        raise RuntimeError("missing successful C/D runner context")
    if base["source_commit"] != os.environ["PROOF_SOURCE_COMMIT"]:
        raise RuntimeError("M5 source/context mismatch")
    expected_ancestor = ancestor.verify()
    old_ancestor = json.loads((directory / "m5-ancestor.json").read_text(encoding="utf-8"))
    if old_ancestor != expected_ancestor:
        raise RuntimeError("M5 ancestor receipt mismatch")
    manifest = m5.verify_inputs()
    report_path = directory / "m5-replay.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report["status"] != "PASS_M5_ACTUAL_JOINT_AND_LITERAL_LOG_FIBRES" or report["build_completed"] is not True:
        raise RuntimeError("M5 replay did not pass")
    if report["m5_manifest_sha256"] != m5.m3.sha256(m5.MANIFEST):
        raise RuntimeError("M5 manifest mismatch")
    if report["m4d_manifest_sha256"] != base["proofs"]["m4d"]["manifest_sha256"]:
        raise RuntimeError("M5/C-D ancestor mismatch")
    if manifest["lean_commit"] not in report["lean_version"] or report["mathlib_revision"] != m5.m3.MATHLIB:
        raise RuntimeError("M5 runtime or Mathlib receipt mismatch")
    mathlib = subprocess.check_output(["git", "rev-parse", "HEAD"],
        cwd=m5.LEAN / ".lake/packages/mathlib", text=True, encoding="utf-8").strip()
    if mathlib != m5.m3.MATHLIB:
        raise RuntimeError("M5 actual Mathlib checkout mismatch")
    axioms = m5.m3.parse_axiom_audit(report["audit_output"], manifest["axiom_targets"])
    if axioms != report["axioms"]:
        raise RuntimeError("M5 axiom receipt mismatch")
    for name, expected in base["receipt_sha256"].items():
        if m5.m3.sha256(directory / name) != expected:
            raise RuntimeError("C/D base receipt changed: " + name)
    names = sorted(set(base["receipt_sha256"]) | {
        "runner-context.json", "m5-ancestor.json", "m5-replay.json"})
    result = {"status": "PASS_HOSTED_UBUNTU_M5_EXACT_ENUMERATION",
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_commit": base["source_commit"], "checkout_commit": base["checkout_commit"],
              "github": base["github"], "runner_platform": base["runner_platform"],
              "m5_manifest_sha256": report["m5_manifest_sha256"],
              "m4d_manifest_sha256": report["m4d_manifest_sha256"],
              "lean_version": report["lean_version"], "actual_mathlib_revision": mathlib,
              "axiom_target_count": len(axioms),
              "observed_axiom_union": sorted({a for row in axioms.values() for a in row}),
              "receipt_sha256": {name: m5.m3.sha256(directory / name) for name in names},
              "dependency_cache_policy": base["dependency_cache_policy"], "public_release_tag": None}
    with (directory / "m5-runner-context.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    print(json.dumps(collect(parser.parse_args().directory)))


if __name__ == "__main__":
    main()
