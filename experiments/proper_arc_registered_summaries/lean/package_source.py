"""Package the accepted proof closure without introducing a new theorem audit."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import zipfile

from theorem_map import as_json, collect, require, sha256
from cold_replay.verify_result import verify

BASE = Path(__file__).resolve().parent
VERSION = "1.0"
TAG = "proper-arc-lean-companion-v1.0"
SOURCE_BASE = "b2c64443b61ef63879704308b5062ab7df6066c3"
EVIDENCE = Path("cold_replay/results/isolated-windows-v1")
MANIFEST = "source-manifest.v1.json"


def payload_paths(data):
    paths = set(data["frozen_source_sha256"])
    for row in data["milestones"]:
        paths.update((row["manifest"], row["report"]))
    paths.update((".gitignore", ".gitattributes", ".zenodo.json", "LICENSE", "CITATION.cff",
        "README.md", "REPRODUCING.md", "RELEASE.md", "PROOF_PLAN.md", "package_source.py",
        "theorem_map.py", "THEOREM_TO_SOURCE_MAP.md", "theorem-to-source-map.v1.json",
        "map_tests/test_theorem_map.py", "cold_replay/README.md", "cold_replay/RESULT.md"))
    paths.update(folder + "/README.md" for folder in (
        "classification", "chains", "converse", "fibres", "summary", "counting", "refinements"))
    envelope = json.loads((BASE / EVIDENCE / "evidence-manifest.v1.json").read_text("utf-8"))
    paths.update((EVIDENCE / name).as_posix() for name in envelope["evidence_sha256"])
    paths.add((EVIDENCE / "evidence-manifest.v1.json").as_posix())
    paths.update(envelope["harness_source_sha256"])
    for name in paths:
        path = Path(name)
        require(not path.is_absolute() and not path.drive and ".." not in path.parts,
                f"nonlocal payload path: {name}")
        source = BASE / path
        require(source.is_file() and not source.is_symlink(), f"missing or linked payload: {name}")
    return sorted(paths)


def check_inventory(paths):
    actual = set()
    for root, folders, files in os.walk(BASE, followlinks=False):
        folders[:] = [name for name in folders if name not in (".lake", "__pycache__", ".git")]
        for name in folders:
            child = Path(root) / name
            require(not child.is_symlink() and not child.is_junction(), "linked source directory")
        actual.update((Path(root) / name).relative_to(BASE).as_posix() for name in files)
    actual.discard(MANIFEST)
    require(actual == set(paths), f"undeclared or missing package files: {sorted(actual ^ set(paths))}")


def acceptance_manifest(data, paths):
    receipt = BASE / EVIDENCE / "cold-replay.v1.json"
    record = json.loads(receipt.read_text("utf-8"))
    return {
        "schema": "proper_arc_lean_source_package.v1",
        "status": "LOCAL_RELEASE_CANDIDATE",
        "version": VERSION,
        "proposed_tag": TAG,
        "source_base_commit": SOURCE_BASE,
        "published_content_commit": None,
        "published_tag": None,
        "zenodo_doi": None,
        "target_manuscript": data["target_manuscript"],
        "final_acceptance_evidence": {
            "kind": "COMPLETED_ISOLATED_COLD_REPLAY",
            "receipt": receipt.relative_to(BASE).as_posix(),
            "receipt_sha256": sha256(receipt),
            "receipt_status": record["status"],
            "evidence_manifest": (EVIDENCE / "evidence-manifest.v1.json").as_posix(),
            "evidence_manifest_sha256": sha256(BASE / EVIDENCE / "evidence-manifest.v1.json"),
            "source_snapshot_sha256": record["source_snapshot_sha256"],
            "completed_utc": record["finished_utc"],
            "validators_passed": len(record["validators"]),
            "unit_tests_passed": 94,
            "same_host_separate_environment": record["same_host_separate_environment"],
            "dependency_mode": record["dependency_mode"],
            "original_source_delivery": record["source_delivery"],
            "frozen_proof_inputs_unchanged": True,
            "new_kernel_replay_by_packager": False,
        },
        "proof_scope": {
            "unique_frozen_inputs": data["unique_frozen_input_count"],
            "selected_theorem_entries": len(data["theorems"]),
            "report_targets_including_repeats": sum(row["target_count"] for row in data["milestones"]),
            "axiom_queries_including_repeats": sum(row["axiom_query_count"] for row in data["milestones"]),
            "observed_axioms": sorted({a for row in data["milestones"] for a in row["observed_axioms"]}),
            "union_declaration_node_count": data["union_declaration_node_count"],
            "union_declaration_node_scope": data["union_declaration_node_scope"],
            "union_graph_sha256": data["union_graph_sha256"],
            "pending_formalization": data["pending_formalization"],
        },
        "frozen_milestones": [{k: row[k] for k in (
            "id", "manifest", "manifest_sha256", "report", "report_sha256", "validator")}
            for row in data["milestones"]],
        "manifest_self_excluded_from_file_inventory": True,
        "file_inventory": {name: {"sha256": sha256(BASE / name), "bytes": (BASE / name).stat().st_size}
                           for name in paths},
        "excluded": [".lake/", "__pycache__/", ".git/", "downloaded toolchain and dependency archives",
                     "private configuration", "exploratory material"],
    }


def write_identical_or_new(path, content):
    if path.exists():
        require(path.read_bytes() == content, f"refuse to replace different frozen output: {path}")
    else:
        path.write_bytes(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--write-manifest", action="store_true", help="create the initial source manifest")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.is_relative_to(BASE), "archive output must be outside the source directory")
    data = collect(False)
    accepted = verify(BASE / EVIDENCE)
    require(accepted["unit_tests"] == 94 and accepted["validators"] == 9, "final acceptance inventory drift")
    paths = payload_paths(data)
    check_inventory(paths)
    manifest = as_json(acceptance_manifest(data, paths)).encode()
    destination = BASE / MANIFEST
    if args.write_manifest:
        write_identical_or_new(destination, manifest)
    else:
        require(destination.is_file() and destination.read_bytes() == manifest, "source package inventory drift")
    archive = io.BytesIO()
    names = sorted([*paths, MANIFEST])
    with zipfile.ZipFile(archive, "w") as bundle:
        for name in names:
            entry = zipfile.ZipInfo(TAG + "/" + name, date_time=(2026, 11, 4, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, (BASE / name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9)
    raw = archive.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as check:
        require(check.namelist() == [TAG + "/" + name for name in names], "archive inventory drift")
        for name in names:
            require(check.read(TAG + "/" + name) == (BASE / name).read_bytes(), "archive byte mismatch")
    output.mkdir(parents=True, exist_ok=True)
    zip_path = output / (TAG + "-source.zip")
    write_identical_or_new(zip_path, raw)
    write_identical_or_new(output / MANIFEST, manifest)
    checksums = f"{sha256(zip_path)}  {zip_path.name}\n{sha256(output / MANIFEST)}  {MANIFEST}\n"
    write_identical_or_new(output / "SHA256SUMS.txt", checksums.encode("ascii"))
    print(json.dumps({"status": "PREPARED_SOURCE_ARCHIVE", "version": VERSION,
        "payload_files": len(names), "source_archive": str(zip_path), "sha256": sha256(zip_path),
        "bytes": len(raw), "final_acceptance": accepted["status"], "new_kernel_replay": False}))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as error:
        raise SystemExit(f"FAIL: {error}") from error
