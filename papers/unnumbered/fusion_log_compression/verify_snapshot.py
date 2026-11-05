"""Read-only byte and bounded-replay validation of the HAL source snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[2]
CONTROLS = ROOT / "experiments" / "fusion_log_compression" / "controls"
MANIFEST = PAPER / "source-manifest.v1.json"
TAG_NAME = "fusion-log-compression-source-v1.0"
PDF = "papers/unnumbered/fusion_log_compression/hal-v1/Chen_History_Preserving_Quadratic_Normal_Forms_HAL_preprint.pdf"
FILES = (
    ".gitattributes",
    "papers/tex/README.md",
    "papers/tex/HAL_READER.md",
    "papers/tex/build_hal.py",
    "papers/tex/hal-reader-template.tex",
    "tests/run_all_tests.py",
    "tests/test_hal_reader_build.py",
    "papers/unnumbered/fusion_log_compression/README.md",
    "papers/unnumbered/fusion_log_compression/MANUSCRIPT.md",
    "papers/unnumbered/fusion_log_compression/references.bib",
    "papers/unnumbered/fusion_log_compression/build_hal.py",
    "papers/unnumbered/fusion_log_compression/hal-reader.json",
    "papers/unnumbered/fusion_log_compression/hal-v1/Chen_History_Preserving_Quadratic_Normal_Forms_HAL_preprint.pdf",
    "papers/unnumbered/fusion_log_compression/results/reader-build.hal-v1.json",
    "papers/unnumbered/fusion_log_compression/verify_snapshot.py",
    "experiments/fusion_log_compression/controls/README.md",
    "experiments/fusion_log_compression/controls/core.py",
    "experiments/fusion_log_compression/controls/audit_math.py",
    "experiments/fusion_log_compression/controls/fusion_log_arbitrary_start_control.py",
    "experiments/fusion_log_compression/controls/results/arbitrary-start.c2.json",
    "experiments/fusion_log_compression/controls/results/mathematical-controls.c2.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}")
    return result.stdout


def validate_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(isinstance(manifest, dict) and set(manifest) == {
        "schema", "source_tag_name", "hal_deposit", "evidence_boundary", "sha256"
    }, "invalid source manifest fields")
    require(manifest["schema"] == "rime.fusion-log-hal-source-snapshot.v1", "invalid schema")
    require(manifest["source_tag_name"] == TAG_NAME, "source tag name mismatch")
    require(manifest["hal_deposit"] is None, "tagged source must not claim a later HAL deposit")
    require(manifest["evidence_boundary"] == "PAPER_PROOFS_AND_BOUNDED_CONSISTENCY_CONTROLS",
            "evidence boundary mismatch")
    hashes = manifest["sha256"]
    require(isinstance(hashes, dict) and set(hashes) == set(FILES), "source file set mismatch")
    for name in FILES:
        digest = hashes[name]
        require(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest) is not None,
                f"invalid digest: {name}")
        require(sha256((ROOT / name).read_bytes()) == digest, f"byte mismatch: {name}")

    expected_owned = {name for name in FILES if name.startswith(
        ("papers/unnumbered/fusion_log_compression/", "experiments/fusion_log_compression/controls/")
    )} | {MANIFEST.relative_to(ROOT).as_posix()}
    actual_owned = {
        path.relative_to(ROOT).as_posix()
        for base in (PAPER, CONTROLS)
        for path in base.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    require(actual_owned == expected_owned, f"unexpected owned files: {sorted(actual_owned ^ expected_owned)}")
    return manifest


def validate_reader_receipt(manifest: dict[str, object]) -> None:
    receipt = json.loads((PAPER / "results" / "reader-build.hal-v1.json").read_text(encoding="utf-8"))
    require(receipt["status"] == "PASS_HAL_READER_BUILD"
            and receipt["stage"] == "HAL_V1_CANDIDATE"
            and receipt["publication_identity"] is None,
            "reader receipt overclaims publication")
    require(receipt["reader_pdf"] == PDF, "reader PDF path mismatch")
    require(receipt["reader_pdf_sha256"] == manifest["sha256"][PDF], "reader PDF digest mismatch")
    require(receipt["max_overfull_pt"] == 0
            and receipt["undefined_citations"] is False
            and receipt["missing_characters"] is False,
            "reader diagnostic mismatch")
    inputs = receipt["inputs"]
    require(set(inputs) == {"MANUSCRIPT.md", "references.bib", "hal-reader.json",
                            "papers/tex/build_hal.py", "papers/tex/hal-reader-template.tex"},
            "reader input set mismatch")
    for name, digest in inputs.items():
        full_name = name if name.startswith("papers/tex/") else (PAPER / name).relative_to(ROOT).as_posix()
        require(manifest["sha256"][full_name] == digest, f"reader input digest mismatch: {name}")


def validate_control_results() -> None:
    arbitrary = json.loads((CONTROLS / "results" / "arbitrary-start.c2.json").read_text(encoding="utf-8"))
    mathematical = json.loads((CONTROLS / "results" / "mathematical-controls.c2.json").read_text(encoding="utf-8"))
    for result, status in ((arbitrary, "PASS_BOUNDED_ARBITRARY_START_CONTROL"),
                           (mathematical, "PASS_BOUNDED_MATHEMATICAL_CONTROLS")):
        require(result["status"] == status
                and result["evidence"] == "BOUNDED_CONSISTENCY_ONLY"
                and result["kernel_formalization_claimed"] is False,
                "bounded control status mismatch")
    require(len(arbitrary["cases"]) == 36
            and {case["n"] for case in arbitrary["cases"]} == {3, 4, 5, 6}
            and sum(case["complete_log_endpoint_pairs"] for case in arbitrary["cases"]) == 65992,
            "arbitrary-start domain mismatch")
    require(len(mathematical["cases"]) == 4
            and mathematical["costs"]["valid_triples_checked"] == 88556,
            "mathematical control domain mismatch")


def replay_controls() -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    with tempfile.TemporaryDirectory(prefix="fusion-log-hal-replay-") as folder:
        for script, arguments, saved in (
            ("fusion_log_arbitrary_start_control.py", ["--max-n", "6"], "arbitrary-start.c2.json"),
            ("audit_math.py", [], "mathematical-controls.c2.json"),
        ):
            result = Path(folder) / saved
            command = [sys.executable, "-B", str(CONTROLS / script), *arguments,
                       "--output", str(result)]
            run = subprocess.run(command, cwd=CONTROLS, env=environment,
                                 capture_output=True, text=True)
            require(run.returncode == 0, f"control replay failed: {script}: {run.stderr}")
            require(result.read_bytes() == (CONTROLS / "results" / saved).read_bytes(),
                    f"control result drift: {saved}")


def validate_tag() -> None:
    ref = f"refs/tags/{TAG_NAME}"
    require(git("cat-file", "-t", ref).strip() == b"tag", "source tag must be annotated")
    selected = (MANIFEST.relative_to(ROOT).as_posix(), *FILES)
    for name in selected:
        require(git("show", f"{ref}:{name}") == (ROOT / name).read_bytes(),
                f"tagged bytes differ: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-tag", action="store_true", help="also compare the exact tagged tree")
    args = parser.parse_args()
    manifest = validate_manifest()
    validate_reader_receipt(manifest)
    validate_control_results()
    replay_controls()
    if args.check_tag:
        validate_tag()
    print(f"PASS fusion-log HAL source snapshot: {len(FILES)} bound files, "
          "36 layouts, 65,992 joint objects, 88,556 cost triples"
          + (", annotated tag checked" if args.check_tag else ""))


if __name__ == "__main__":
    main()
