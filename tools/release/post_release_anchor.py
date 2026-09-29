#!/usr/bin/env python
"""Create or validate an additive post-release publication anchor.

The pre-release manifest and receipt remain immutable. This tool resolves
their exact bytes from the declared release tag, verifies deposited Zenodo
files against tagged source bytes, and writes a downstream metadata record.
It never promotes current-HEAD bytes into a historical release identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

SCHEMA = "rime.paper-post-release-anchor.v1"
POLICY = {
    "pre_release_manifest_mutation_allowed": False,
    "pre_release_receipt_mutation_allowed": False,
    "current_head_fallback_allowed": False,
    "owner_change_requires_new_owner_version": True,
    "consumer_change_requires_new_consumer_version_and_repin": True,
    "shared_file_in_place_update_allowed": False,
}
BOUNDARY = [
    "The anchor establishes release-tag, evidence-root, and deposited-file byte identity only.",
    "A DOI anchors only files actually deposited in that record.",
    "Local closure verification is not independent mathematical validation.",
    "Publication anchoring does not establish theorem truth or scientific adequacy.",
    "The anchor is downstream metadata and is not part of the release tag it records.",
]


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_root(start: Path | None = None) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def git_output(root: Path, *args: str, text: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=text,
    )
    return result.stdout


def git_text(root: Path, *args: str) -> str:
    return str(git_output(root, *args, text=True)).strip()


def git_blob(root: Path, tag: str, path: str) -> bytes:
    return bytes(git_output(root, "show", f"refs/tags/{tag}:{path}"))


def tag_ref_sha(root: Path, tag: str) -> str:
    if not isinstance(tag, str) or not tag:
        raise ValueError("release tag name is missing")
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--hash", f"refs/tags/{tag}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"release tag does not exist as an exact tag ref: {tag}")
    return result.stdout.strip()


def git_tag_path_exists(root: Path, tag: str, path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-tree", "-z", "--name-only", f"refs/tags/{tag}", "--", path],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"could not inspect release tag path: {tag}:{path}")
    return bool(result.stdout)


def validated_publication_date(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError("publication_date must be an ISO calendar date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("publication_date must be an ISO calendar date") from exc
    if parsed.isoformat() != value:
        raise ValueError("publication_date must be an ISO calendar date")
    return value


def validate_remote_publication_date(record: dict[str, Any], expected: str) -> None:
    remote = validated_publication_date(
        (record.get("metadata") or {}).get("publication_date")
    )
    if remote != expected:
        raise ValueError("remote Zenodo publication date differs from the stored anchor")


def checked_relative_path(value: str) -> str:
    if "\\" in value:
        raise ValueError(f"path must use repository-relative POSIX syntax: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe repository-relative path: {value}")
    return path.as_posix()


def assignment(value: str, kind: str) -> tuple[str, str]:
    key, separator, path = value.partition("=")
    if not separator or not key or not path:
        raise ValueError(f"{kind} must use NAME=repository/relative/path")
    return key, checked_relative_path(path)


def zenodo_record_id(value: str) -> str:
    candidate = value.rstrip("/").split("/")[-1]
    if candidate.isdigit():
        return candidate
    match = re.fullmatch(r"(?:10\.5281/)?zenodo\.(\d+)", candidate, re.IGNORECASE)
    if match:
        return match.group(1)
    raise ValueError("expected a Zenodo DOI, DOI URL, or numeric record ID")


def fetch_record(doi: str) -> dict[str, Any]:
    record_id = zenodo_record_id(doi)
    url = f"https://zenodo.org/api/records/{record_id}"
    last_error: BaseException | None = None
    for attempt in range(4):
        try:
            with urlopen(url, timeout=60) as response:
                return json.load(response)
        except (URLError, TimeoutError, ConnectionError, OSError) as error:
            last_error = error
            if attempt < 3:
                time.sleep(1 + attempt)
    raise OSError(f"failed to load Zenodo record after four attempts: {url}") from last_error


def remote_digest(url: str) -> tuple[str, int]:
    last_error: BaseException | None = None
    for attempt in range(4):
        try:
            digest = hashlib.sha256()
            size = 0
            with urlopen(url, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            return digest.hexdigest(), size
        except (URLError, TimeoutError, ConnectionError, OSError) as error:
            last_error = error
            if attempt < 3:
                time.sleep(1 + attempt)
    raise OSError(f"failed to download Zenodo file after four attempts: {url}") from last_error


def json_status(data: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    result = {}
    for key in ("schema", "status", "release_identity_claimed", "validation_mode"):
        if key in payload:
            result[key] = payload[key]
    return result


def tag_identity(root: Path, tag: str) -> dict[str, str]:
    ref_sha = tag_ref_sha(root, tag)
    return {
        "name": tag,
        "tag_object_sha": ref_sha,
        "target_commit_sha": git_text(
            root, "rev-parse", f"refs/tags/{tag}^{{commit}}"
        ),
    }


def evidence_rows(
    root: Path, tag: str, declarations: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    rows = []
    for role, path in declarations:
        data = git_blob(root, tag, path)
        row: dict[str, Any] = {
            "role": role,
            "path": path,
            "sha256_at_tag": digest_bytes(data),
            "size_at_tag": len(data),
            "mutation_policy": "IMMUTABLE_TAG_BYTES",
        }
        status = json_status(data)
        if status:
            row["declared_state_at_tag"] = status
        rows.append(row)
    return rows


def supplement_rows(
    root: Path, tag: str, declarations: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    rows = []
    for role, path in declarations:
        local = (root / path).resolve()
        if not local.is_file() or root not in local.parents:
            raise ValueError(f"post-release supplement is missing or unsafe: {path}")
        if git_tag_path_exists(root, tag, path):
            raise ValueError(f"post-release supplement already exists in release tag: {path}")
        rows.append(
            {
                "role": role,
                "path": path,
                "sha256": digest_file(local),
                "size": local.stat().st_size,
                "release_role": "POST_RELEASE_SUPPLEMENT_NOT_IN_RELEASE_TAG",
            }
        )
    return rows


def deposit_rows(
    root: Path,
    tag: str,
    record: dict[str, Any],
    declarations: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    rows = []
    files = record.get("files", [])
    for remote_name, source_path in declarations:
        matches = [item for item in files if item.get("key") == remote_name]
        if len(matches) != 1:
            available = [item.get("key") for item in files]
            raise ValueError(
                f"Zenodo file {remote_name!r} not found exactly once; available={available}"
            )
        source = git_blob(root, tag, source_path)
        source_digest = digest_bytes(source)
        link = matches[0].get("links", {}).get("content") or matches[0]["links"]["self"]
        deposited_digest, deposited_size = remote_digest(link)
        if source_digest != deposited_digest or len(source) != deposited_size:
            raise ValueError(
                f"deposited bytes differ from {tag}:{source_path}: {remote_name}"
            )
        rows.append(
            {
                "remote_name": remote_name,
                "source_path_at_tag": source_path,
                "sha256": source_digest,
                "size": len(source),
            }
        )
    return rows


def write_anchor(args: argparse.Namespace) -> int:
    root = repository_root(args.repository)
    output = (root / checked_relative_path(args.output)).resolve()
    if root not in output.parents:
        raise ValueError(f"output must stay inside the repository: {output}")
    if output.exists() and not args.force:
        raise ValueError(f"anchor already exists; pass --force to replace it: {output}")

    evidence = [assignment(value, "--evidence") for value in args.evidence]
    deposits = [assignment(value, "--deposit") for value in args.deposit]
    supplements = [assignment(value, "--supplement") for value in args.supplement]
    if not evidence:
        raise ValueError("at least one --evidence root is required")
    bound_paths = {path for _, path in evidence + deposits + supplements}
    output_relative = output.relative_to(root).as_posix()
    if output_relative in bound_paths:
        raise ValueError("a post-release anchor may not bind itself")

    record = fetch_record(args.doi)
    canonical_doi = record.get("doi")
    if not canonical_doi:
        raise ValueError("Zenodo record has no DOI")
    record_id = str(record["id"])
    metadata = record.get("metadata", {})
    publication_date = validated_publication_date(metadata.get("publication_date"))
    anchor = {
        "schema": SCHEMA,
        "paper_id": args.paper,
        "release_version": args.version,
        "publication_status": "PUBLISHED",
        "release_identity_claimed": True,
        "anchor_role": "DOWNSTREAM_PUBLICATION_METADATA",
        "release_tag": tag_identity(root, args.tag),
        "pre_release_evidence": evidence_rows(root, args.tag, evidence),
        "post_release_supplements": supplement_rows(root, args.tag, supplements),
        "external_anchor": {
            "provider": "Zenodo",
            "doi": canonical_doi,
            "record_id": record_id,
            "record_url": f"https://zenodo.org/records/{record_id}",
            "publication_date": publication_date,
            "deposited_files": deposit_rows(root, args.tag, record, deposits),
        },
        "versioned_repin_policy": dict(POLICY),
        "authority_boundary": list(BOUNDARY),
        "notes": list(args.note),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(anchor, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        f"WROTE {output_relative}: {args.paper} v{args.version}, "
        f"{len(evidence)} evidence roots, {len(deposits)} deposited files"
    )
    return 0


def validate_anchor(args: argparse.Namespace) -> int:
    root = repository_root(args.repository)
    anchor_path = (root / checked_relative_path(args.anchor)).resolve()
    anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
    expected_keys = {
        "schema",
        "paper_id",
        "release_version",
        "publication_status",
        "release_identity_claimed",
        "anchor_role",
        "release_tag",
        "pre_release_evidence",
        "post_release_supplements",
        "external_anchor",
        "versioned_repin_policy",
        "authority_boundary",
        "notes",
    }
    if set(anchor) != expected_keys:
        raise ValueError(f"unexpected anchor fields: {sorted(set(anchor) ^ expected_keys)}")
    if anchor.get("schema") != SCHEMA:
        raise ValueError(f"unsupported anchor schema: {anchor.get('schema')}")
    if anchor.get("publication_status") != "PUBLISHED":
        raise ValueError("post-release anchor is not PUBLISHED")
    if anchor.get("release_identity_claimed") is not True:
        raise ValueError("post-release anchor does not claim a release identity")
    if anchor.get("anchor_role") != "DOWNSTREAM_PUBLICATION_METADATA":
        raise ValueError("unexpected anchor role")
    if anchor.get("versioned_repin_policy") != POLICY:
        raise ValueError("versioned re-pin policy differs from the frozen policy")
    if anchor.get("authority_boundary") != BOUNDARY:
        raise ValueError("authority boundary differs from the frozen boundary")
    if not isinstance(anchor.get("paper_id"), str) or not anchor["paper_id"]:
        raise ValueError("paper_id is missing")
    if not isinstance(anchor.get("release_version"), str) or not anchor["release_version"]:
        raise ValueError("release_version is missing")
    if not isinstance(anchor.get("notes"), list) or not all(
        isinstance(item, str) for item in anchor["notes"]
    ):
        raise ValueError("notes must be a string array")

    release_tag = anchor["release_tag"]
    actual_tag = tag_identity(root, release_tag["name"])
    if release_tag != actual_tag:
        raise ValueError("release tag identity mismatch")
    anchor_relative = anchor_path.relative_to(root).as_posix()
    if not anchor["pre_release_evidence"]:
        raise ValueError("anchor has no pre-release evidence roots")
    evidence_roles: set[str] = set()
    evidence_paths: set[str] = set()
    for row in anchor["pre_release_evidence"]:
        required = {"role", "path", "sha256_at_tag", "size_at_tag", "mutation_policy"}
        if not required.issubset(row) or set(row) - required - {"declared_state_at_tag"}:
            raise ValueError("invalid pre-release evidence row fields")
        if row["role"] in evidence_roles or row["path"] in evidence_paths:
            raise ValueError("duplicate pre-release evidence role or path")
        evidence_roles.add(row["role"])
        evidence_paths.add(row["path"])
        path = checked_relative_path(row["path"])
        if path == anchor_relative:
            raise ValueError("post-release anchor binds itself")
        data = git_blob(root, release_tag["name"], path)
        if digest_bytes(data) != row["sha256_at_tag"] or len(data) != row["size_at_tag"]:
            raise ValueError(f"tagged evidence mismatch: {path}")
        if row.get("mutation_policy") != "IMMUTABLE_TAG_BYTES":
            raise ValueError(f"invalid mutation policy: {path}")
        status = json_status(data)
        if status:
            if row.get("declared_state_at_tag") != status:
                raise ValueError(f"declared tag state mismatch: {path}")
        elif "declared_state_at_tag" in row:
            raise ValueError(f"unexpected declared tag state: {path}")

    supplement_roles: set[str] = set()
    supplement_paths: set[str] = set()
    for row in anchor["post_release_supplements"]:
        required = {"role", "path", "sha256", "size", "release_role"}
        if set(row) != required:
            raise ValueError("invalid post-release supplement row fields")
        if row["role"] in supplement_roles or row["path"] in supplement_paths:
            raise ValueError("duplicate post-release supplement role or path")
        supplement_roles.add(row["role"])
        supplement_paths.add(row["path"])
        path = checked_relative_path(row["path"])
        if path == anchor_relative:
            raise ValueError("post-release anchor binds itself")
        if git_tag_path_exists(root, release_tag["name"], path):
            raise ValueError(f"post-release supplement already exists in release tag: {path}")
        local = (root / path).resolve()
        if digest_file(local) != row["sha256"] or local.stat().st_size != row["size"]:
            raise ValueError(f"post-release supplement mismatch: {path}")
        if row.get("release_role") != "POST_RELEASE_SUPPLEMENT_NOT_IN_RELEASE_TAG":
            raise ValueError(f"invalid supplement role: {path}")

    external = anchor["external_anchor"]
    external_keys = {
        "provider",
        "doi",
        "record_id",
        "record_url",
        "publication_date",
        "deposited_files",
    }
    if set(external) != external_keys or external.get("provider") != "Zenodo":
        raise ValueError("invalid external anchor fields")
    doi = external["doi"]
    record_id = zenodo_record_id(doi)
    if external["record_id"] != record_id:
        raise ValueError("Zenodo record ID does not match DOI")
    if external["record_url"] != f"https://zenodo.org/records/{record_id}":
        raise ValueError("Zenodo record URL does not match DOI")
    publication_date = validated_publication_date(external["publication_date"])
    if not external["deposited_files"]:
        raise ValueError("anchor has no deposited files")
    record = fetch_record(doi) if args.check_remote else None
    if record is not None:
        if record.get("doi") != doi:
            raise ValueError("remote Zenodo DOI differs from the stored anchor")
        validate_remote_publication_date(record, publication_date)
    remote_names: set[str] = set()
    source_paths: set[str] = set()
    for row in external["deposited_files"]:
        required = {"remote_name", "source_path_at_tag", "sha256", "size"}
        if set(row) != required:
            raise ValueError("invalid deposited-file row fields")
        if row["remote_name"] in remote_names or row["source_path_at_tag"] in source_paths:
            raise ValueError("duplicate remote name or tagged deposit source")
        remote_names.add(row["remote_name"])
        source_paths.add(row["source_path_at_tag"])
        source_path = checked_relative_path(row["source_path_at_tag"])
        source = git_blob(root, release_tag["name"], source_path)
        if digest_bytes(source) != row["sha256"] or len(source) != row["size"]:
            raise ValueError(f"tagged deposit source mismatch: {source_path}")
        if record is not None:
            matches = [item for item in record.get("files", []) if item.get("key") == row["remote_name"]]
            if len(matches) != 1:
                raise ValueError(f"remote deposit is missing: {row['remote_name']}")
            link = matches[0].get("links", {}).get("content") or matches[0]["links"]["self"]
            digest, size = remote_digest(link)
            if digest != row["sha256"] or size != row["size"]:
                raise ValueError(f"remote deposit mismatch: {row['remote_name']}")

    mode = "remote+local" if args.check_remote else "local-tag"
    print(
        f"PASS {anchor['paper_id']} v{anchor['release_version']} post-release anchor "
        f"({mode}; {len(anchor['pre_release_evidence'])} evidence roots; "
        f"{len(anchor['external_anchor']['deposited_files'])} deposited files)"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create an additive post-release anchor")
    create.add_argument("--paper", required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--tag", required=True)
    create.add_argument("--doi", required=True)
    create.add_argument("--evidence", action="append", default=[], metavar="ROLE=PATH")
    create.add_argument("--deposit", action="append", required=True, metavar="REMOTE=PATH")
    create.add_argument("--supplement", action="append", default=[], metavar="ROLE=PATH")
    create.add_argument("--note", action="append", default=[])
    create.add_argument("--output", required=True)
    create.add_argument("--repository", type=Path)
    create.add_argument("--force", action="store_true")
    create.set_defaults(handler=write_anchor)

    validate = subparsers.add_parser("validate", help="validate a post-release anchor")
    validate.add_argument("anchor")
    validate.add_argument("--repository", type=Path)
    validate.add_argument("--check-remote", action="store_true")
    validate.set_defaults(handler=validate_anchor)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL: {error}") from error


if __name__ == "__main__":
    raise SystemExit(main())
