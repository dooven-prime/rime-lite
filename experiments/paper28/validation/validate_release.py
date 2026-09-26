"""Validate finite Paper XXVIII roots in a clean, temporary path alias.

Original scripts and receipts keep their historical relative paths. This
paper-owned wrapper copies only manifest-bound bytes into a temporary layout,
runs the original validators there, and issues a downstream local receipt.
It is not an independent mathematical implementation or a publication anchor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "experiments" / "paper28"
MANIFEST = PACKAGE / "dependency-manifest.json"
MIRROR_VALIDATOR = PACKAGE / "validation" / "validate_mirror.py"
RECEIPT = PACKAGE / "validation" / "paper28_release_validation_v1.receipt.json"
EXTRA_VALIDATORS = {
    "paper28_fourth_mechanism_schema_declaration_v1": "validation/validate_paper28_fourth_mechanism_schema.py",
    "paper28_third_mechanism_schema_declaration_v1": "validation/validate_paper28_third_mechanism_schema.py",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes release layout: {relative}")
    return path


def source_relative(reference: str) -> str:
    if reference.startswith("git:"):
        return reference.split(":", 2)[2]
    return reference


def root_validators(manifest: dict) -> list[tuple[str, str]]:
    copied_sources = {item["source"] for item in manifest["files"]}
    result = []
    for stem in manifest["root_artifacts"]:
        receipt = json.loads((PACKAGE / "results" / f"{stem}.receipt.json").read_text(encoding="utf-8"))
        closure = receipt.get("source_closure", [])
        if isinstance(closure, dict):
            closure = list(closure.values())
        candidates = []
        for item in closure:
            ref = item.get("path") or item.get("name")
            old_path = ref if ref.startswith("experiments/") else "experiments/synchronizing_automata/" + ref
            if "/validation/validate_" in old_path:
                candidates.append(old_path)
        if stem in EXTRA_VALIDATORS:
            candidates.append("experiments/synchronizing_automata/" + EXTRA_VALIDATORS[stem])
        if len(candidates) != 1 or candidates[0] not in copied_sources:
            raise ValueError(f"no unique mirrored validator for {stem}: {candidates}")
        result.append((stem, candidates[0]))
    return result


def copy_layout(root: Path, manifest: dict) -> None:
    for item in manifest["files"]:
        target = checked_path(root, item["source"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checked_path(REPO, item["mirror"]), target)
    for item in manifest["upstream_inputs"]:
        target = checked_path(root, source_relative(item["source"]))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checked_path(REPO, item["mirror"]), target)


def run_validators(root: Path, validators: list[tuple[str, str]]) -> list[dict]:
    env = dict(os.environ)
    env["RIME_PAPER27_RELEASE_ROOT"] = str(root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    checks = []
    for stem, relative in validators:
        print(f"CHECK {stem}", flush=True)
        arguments = []
        if stem == "paper28_rank5_section_return_evaluation_v1":
            arguments = [
                "--n7-extremal-input",
                str(checked_path(root, "experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json")),
            ]
        result = subprocess.run(
            [sys.executable, str(checked_path(root, relative)), *arguments],
            cwd=root, env=env, capture_output=True, text=True, timeout=300,
        )
        if result.returncode:
            raise RuntimeError(
                f"{stem} validator failed (exit {result.returncode})\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        checks.append({
            "artifact_stem": stem,
            "validator_source": relative,
            "validator_sha256": sha256(checked_path(root, relative)),
            "input_options": ["--n7-extremal-input=paper27-v1.0"] if arguments else [],
            "status": "PASS",
        })
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true", help="write the downstream paper-owned local validation receipt")
    args = parser.parse_args()

    mirror = subprocess.run(
        [sys.executable, str(MIRROR_VALIDATOR)], cwd=REPO,
        capture_output=True, text=True, check=True,
    )
    print(mirror.stdout.strip(), flush=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validators = root_validators(manifest)
    temp_parent = Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix="paper28-release-") as location:
        scratch = Path(location).resolve()
        if scratch.parent != temp_parent:
            raise ValueError(f"unexpected scratch directory: {scratch}")
        copy_layout(scratch, manifest)
        checks = run_validators(scratch, validators)

    receipt = {
        "schema": "paper28-local-release-validation-receipt-v1",
        "status": "LOCAL_CLOSURE_VERIFICATION",
        "scope": "20 manuscript-level finite result anchors",
        "manifest_sha256": sha256(MANIFEST),
        "validator_sha256": sha256(Path(__file__)),
        "mirror_validator_sha256": sha256(MIRROR_VALIDATOR),
        "upstream_inputs": [
            {"mirror": item["mirror"], "sha256": item["sha256"], "source": item["source"]}
            for item in manifest["upstream_inputs"]
        ],
        "checks": checks,
        "nonclaims": [
            "No original artifact or receipt was rewritten or re-signed.",
            "This is local closure verification, not an independent implementation or publication receipt.",
            "All-n projectable-origin supply and general admission remain open.",
        ],
    }
    contents = json.dumps(receipt, ensure_ascii=True, indent=2) + "\n"
    if args.emit_receipt:
        RECEIPT.write_text(contents, encoding="utf-8", newline="\n")
        print(f"WROTE {RECEIPT}")
    else:
        if not RECEIPT.is_file() or RECEIPT.read_text(encoding="utf-8") != contents:
            raise ValueError("paper-owned validation receipt is missing or stale")
        print("PASS: 20 finite validators and paper-owned local receipt")


if __name__ == "__main__":
    main()
