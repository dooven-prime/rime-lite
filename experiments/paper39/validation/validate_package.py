"""Read-only local development closure and bounded consumer replay gate."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
MANIFEST = PACKAGE / "development-manifest.json"
sys.path.insert(0, str(PACKAGE))
from audit_scope import ARTIFACTS
from contract import require

RELEASE_ONLY = {
    "experiments/paper39/release-environment.json",
    "experiments/paper39/release-manifest.json",
    "experiments/paper39/validation/validate_release.py",
    "experiments/paper39/results/paper39_public_package_v1.validation-receipt.json",
}


def child_environment():
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def manifest_data():
    artifacts = []
    for role, relative in ARTIFACTS:
        data = (ROOT / relative).read_bytes()
        artifacts.append({"path": relative, "role": role, "size": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    return {"schema": "rime.paper39.development-manifest.v1", "paper_id": "PAPER39",
            "status": "DRAFT_PAPER_OWNED_CLOSURE", "release_identity_claimed": False,
            "validation_mode": "LOCAL_CLOSURE_VERIFICATION",
            "formalization_claimed": "PARTIAL_IMPLEMENTATION_SPINE",
            "digest_policy": {"algorithm": "sha256", "scope": "exact_file_bytes", "text_eol": "LF"},
            "proof_ownership": "The manuscript owns the all-N theorems; finite replay is supplementary.",
            "excluded_dependencies": ["broader exploratory source tree", "unnumbered historical drafts",
                                      "old B0 certificates", "external UFE implementation", "reader PDF"],
            "artifacts": artifacts}


def snapshot():
    return {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in [*(path for _, path in ARTIFACTS), MANIFEST.relative_to(ROOT).as_posix()]}


def check_manifest():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest == manifest_data(), "development manifest or bound bytes drift; do not auto-repair")
    for _, relative in ARTIFACTS:
        pure = PurePosixPath(relative)
        require(not pure.is_absolute() and ".." not in pure.parts and "\\" not in relative,
                "unsafe closure path")
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT), "closure escapes root")
        text = path.read_bytes().decode("utf-8")
        require("\r" not in text, f"non-LF artifact: {relative}")
    expected = {relative for _, relative in ARTIFACTS if relative.startswith("experiments/paper39/")}
    actual = set()
    for directory, directories, filenames in os.walk(PACKAGE):
        directories[:] = [name for name in directories if name not in {"__pycache__", ".lake", ".git"}]
        for filename in filenames:
            path = Path(directory) / filename
            if path != MANIFEST and path.suffix != ".pyc":
                actual.add(path.relative_to(ROOT).as_posix())
    require(expected <= actual and actual - expected <= RELEASE_ONLY,
            f"package inventory drift: {sorted(actual ^ expected)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="explicitly skip finite replay and tests")
    parser.add_argument("--lean", action="store_true", help="also compile and audit the partial Lean spine")
    args = parser.parse_args()
    if args.static and args.lean:
        parser.error("--static cannot be combined with --lean")
    check_manifest()
    before = snapshot()

    def run(script, *extra):
        subprocess.run([sys.executable, "-B", str(PACKAGE / "validation" / script), *extra],
                       cwd=ROOT, env=child_environment(), check=True)

    run("validate_source.py")
    run("validate_lean_formalization.py")
    if args.static:
        run("validate_consumer.py", "--static")
    else:
        run("test_contract.py")
        run("validate_consumer.py")
    if args.lean:
        run("validate_lean_formalization.py", "--replay")
    check_manifest()
    require(snapshot() == before, "verification mutated its bound closure")
    mode = "finite replay skipped" if args.static else "finite replay included"
    print(f"PASS: Paper XXXIX LOCAL_CLOSURE_VERIFICATION ({mode}); no release identity")


if __name__ == "__main__":
    main()
