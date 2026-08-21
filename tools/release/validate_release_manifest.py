#!/usr/bin/env python
"""Validate release identity, with optional strict snapshot verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDERS = ("<release_", "OPTIONAL_", "SOURCE_SHA256", "YYYY-MM-DD")
REPOSITORY_MANIFEST_VERSION = "repository-release-byte-manifest-1.0"


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout


def tracked_at(commit: str, relative_path: str) -> bool:
    result = git("cat-file", "-e", f"{commit}:{relative_path}", check=False)
    return result.returncode == 0


def require_file(
    relative_path: str,
    expected_sha256: str,
    commit: str,
    *,
    strict_hash: bool,
) -> bytes:
    assert tracked_at(commit, relative_path), (
        f"release file is not tracked in content commit: {relative_path}"
    )
    content = git_bytes("show", f"{commit}:{relative_path}")
    if strict_hash:
        assert hashlib.sha256(content).hexdigest() == expected_sha256, (
            f"SHA-256 mismatch in content commit: {relative_path}"
        )
    return content


def validate_repository_manifest(manifest: dict) -> None:
    release = manifest["release"]
    commit = release["release_content_commit_sha"]
    assert SHA_RE.fullmatch(commit), "invalid release-content commit SHA"
    git("cat-file", "-e", f"{commit}^{{commit}}")
    assert git("merge-base", "--is-ancestor", commit, "HEAD", check=False).returncode == 0
    tree = git("rev-parse", f"{commit}^{{tree}}").stdout.strip()
    assert tree == release["release_content_tree_oid"], "content tree OID mismatch"

    paths: set[str] = set()
    for artifact in manifest["artifacts"]:
        path = artifact["path"]
        assert path not in paths, f"duplicate release artifact: {path}"
        paths.add(path)
        content = require_file(path, artifact["sha256"], commit, strict_hash=True)
        assert len(content) == artifact["size_bytes"], f"size mismatch: {path}"
        assert artifact["role"], f"missing role: {path}"
        assert artifact["contract_version"], f"missing contract version: {path}"
        assert artifact["evidence_status"], f"missing evidence status: {path}"

    assert manifest["artifact_inventory_scope"] == "selected_release_review_surface"
    assert manifest["full_tree_anchor"] == "release_content_commit_sha"
    print(
        f"PASS {manifest['release']['tag']}: repository byte manifest "
        f"({len(paths)} selected artifacts; full tree commit-anchored)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--strict-snapshot",
        action="store_true",
        help="verify every recorded digest, including nonidentity evidence files",
    )
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    serialized = json.dumps(manifest, sort_keys=True)
    assert not any(token in serialized for token in PLACEHOLDERS), (
        "manifest contains an unresolved template placeholder"
    )
    if manifest.get("schema_version") == REPOSITORY_MANIFEST_VERSION:
        validate_repository_manifest(manifest)
        return
    assert manifest["schema_version"] == "paper-release-manifest-1.1"
    assert manifest["release"]["status"] == "repository_accepted"

    commit = manifest["release"]["release_content_commit_sha"]
    assert SHA_RE.fullmatch(commit), "invalid release-content commit SHA"
    git("cat-file", "-e", f"{commit}^{{commit}}")
    assert git("merge-base", "--is-ancestor", commit, "HEAD", check=False).returncode == 0

    source = manifest["source"]
    require_file(
        source["path"],
        source["checksums"]["sha256"],
        commit,
        strict_hash=args.strict_snapshot,
    )

    pdf = manifest["pdf"]
    pdf_bytes = require_file(
        pdf["path"], pdf["checksums"]["sha256"], commit, strict_hash=True
    )
    assert len(pdf_bytes) == pdf["size_bytes"], "PDF size mismatch"
    assert hashlib.md5(pdf_bytes).hexdigest() == pdf["checksums"]["md5"], (
        "PDF MD5 mismatch"
    )

    metadata = manifest.get("prepared_metadata")
    if metadata is not None:
        metadata_bytes = require_file(
            metadata["path"],
            metadata["sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
        metadata_json = json.loads(metadata_bytes.decode("utf-8"))
        assert metadata_json["metadata"]["version"] == manifest["release"]["version"]

    private_metadata = manifest.get("private_submission_metadata")
    if private_metadata is not None and args.strict_snapshot:
        metadata_path = ROOT / private_metadata["path"]
        assert metadata_path.is_file(), "missing private submission metadata"
        assert digest(metadata_path) == private_metadata["sha256"], (
            "private submission metadata SHA-256 mismatch"
        )
        assert not tracked_at(commit, private_metadata["path"]), (
            "private submission metadata is tracked in the release-content commit"
        )
        metadata_json = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata_json["metadata"]["version"] == manifest["release"]["version"]

    result_paths: set[str] = set()
    for record in manifest["result_records"]:
        assert record["path"] not in result_paths, f"duplicate result: {record['path']}"
        result_paths.add(record["path"])
        require_file(
            record["path"],
            record["sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
        assert record["claim_ids"], f"result has no claim scope: {record['path']}"

    for validator in manifest["validators"]:
        require_file(
            validator["path"],
            validator["sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
        assert validator["exit_code"] == 0 and validator["status"] == "passed"
        assert validator["claim_scope"], f"validator has no claim scope: {validator['id']}"

    for figure in manifest["figures"]:
        require_file(
            figure["path"],
            figure["sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
        require_file(
            figure["renderer_path"],
            figure["renderer_sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
        for source_path in figure["source_record_paths"]:
            assert source_path in result_paths, f"unbound figure source: {source_path}"

    build = manifest["build"]
    if "build_script_path" in build:
        require_file(
            build["build_script_path"],
            build["build_script_sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
    if "bibliography_path" in build:
        require_file(
            build["bibliography_path"],
            build["bibliography_sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
    if "log_path" in build:
        require_file(
            build["log_path"],
            build["log_sha256"],
            commit,
            strict_hash=args.strict_snapshot,
        )
    artifact_path = build.get("artifact_path", pdf["path"])
    require_file(
        artifact_path, pdf["checksums"]["sha256"], commit, strict_hash=True
    )
    assert build["blocking_warning_count"] == 0

    review = manifest["visual_review"]
    assert review["pdf_sha256"] == pdf["checksums"]["sha256"]
    assert review["pages_reviewed"] == "all" and review["status"] == "passed"
    assert manifest["tracking_check"]["all_release_paths_tracked"] is True

    mode = "strict snapshot" if args.strict_snapshot else "release identity"
    print(
        f"PASS {manifest_path.name}: {manifest['paper']} "
        f"v{manifest['release']['version']} ({mode}; "
        f"{len(result_paths)} result records declared)"
    )


if __name__ == "__main__":
    main()
