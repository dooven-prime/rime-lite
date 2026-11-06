"""Cross-check the two actual CI replay receipts; record their runner context."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess

import replay as m3
import replay_m4c as m4c
import replay_m4d as m4d
import verify_ci_ancestors as ancestors


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ancestors.REPOSITORY,
                                   text=True, encoding="utf-8").strip()


def collect(directory):
    if os.environ.get("GITHUB_ACTIONS") != "true" or platform.system() != "Linux":
        raise RuntimeError("this collector requires an actual GitHub Actions Linux runner")
    expected_ancestors = ancestors.verify()
    recorded_ancestors = json.loads((directory / "ancestors.json").read_text(encoding="utf-8"))
    if recorded_ancestors != expected_ancestors:
        raise RuntimeError("ancestor receipt mismatch")
    source = os.environ["PROOF_SOURCE_COMMIT"]
    checkout = git("rev-parse", "HEAD")
    git("diff", "--exit-code", source, checkout, "--",
        "experiments/fusion_log_compression", ".github/workflows/fusion-log-lean.yml")
    observations = {}
    receipts = {}
    for label, owner, status in (
            ("m4c", m4c, "PASS_M4C_ARBITRARY_INITIAL_INTERPRETATION"),
            ("m4d", m4d, "PASS_M4D_ABSTRACT_SCHEDULE_CLASSIFICATION")):
        manifest = owner.verify_inputs()
        path = directory / (label + "-replay.json")
        report = json.loads(path.read_text(encoding="utf-8"))
        if report["status"] != status or report["build_completed"] is not True:
            raise RuntimeError(label + " unsuccessful replay")
        if report[label + "_manifest_sha256"] != m3.sha256(owner.MANIFEST):
            raise RuntimeError(label + " manifest mismatch")
        if manifest["lean_commit"] not in report["lean_version"]:
            raise RuntimeError(label + " Lean runtime mismatch")
        if report["mathlib_revision"] != m3.MATHLIB:
            raise RuntimeError(label + " Mathlib receipt mismatch")
        actual_mathlib = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=owner.LEAN / ".lake/packages/mathlib",
            text=True, encoding="utf-8").strip()
        if actual_mathlib != m3.MATHLIB:
            raise RuntimeError(label + " actual Mathlib checkout mismatch")
        axioms = m3.parse_axiom_audit(report["audit_output"], manifest["axiom_targets"])
        if axioms != report["axioms"]:
            raise RuntimeError(label + " axiom receipt mismatch")
        receipts[path.name] = m3.sha256(path)
        observations[label] = {"manifest_sha256": m3.sha256(owner.MANIFEST),
                               "actual_mathlib_revision": actual_mathlib,
                               "axiom_target_count": len(axioms)}
    if json.loads((directory / "m4d-replay.json").read_text())["m4c_manifest_sha256"] != \
            observations["m4c"]["manifest_sha256"]:
        raise RuntimeError("M4-D/C ancestor mismatch")
    receipts["ancestors.json"] = m3.sha256(directory / "ancestors.json")
    context = {"status": "PASS_HOSTED_UBUNTU_M4C_M4D_REPLAY",
               "completed_at_utc": datetime.now(timezone.utc).isoformat(),
               "source_commit": source, "checkout_commit": checkout,
               "runner_platform": platform.platform(),
               "github": {key: os.environ.get(key) for key in (
                   "GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA",
                   "GITHUB_REF", "GITHUB_EVENT_NAME", "RUNNER_OS", "RUNNER_ARCH",
                   "ImageOS", "ImageVersion")},
               "proofs": observations, "receipt_sha256": receipts,
               "dependency_cache_policy": "Official Mathlib compiled cache; external dependencies shared within this runner; GitHub build cache disabled",
               "public_release_tag": None}
    with (directory / "runner-context.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(context, indent=2) + "\n")
    return context


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    print(json.dumps(collect(parser.parse_args().directory)))


if __name__ == "__main__":
    main()
