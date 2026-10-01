#!/usr/bin/env python3
"""Replay versioned owner evidence before a later paper inherits it."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


SCHEMA = "rime.paper-inheritance-gate.v1"
TAG_PATTERN = re.compile(
    r"^paper(?P<number>[1-9][0-9]*)-v(?P<version>[0-9]+(?:\.[0-9]+){1,2})$"
)
TOP_LEVEL_KEYS = {"schema", "consumer", "status", "sources", "semantic_constraints"}
SOURCE_KEYS = {
    "paper_id",
    "release_tag",
    "validator",
    "arguments",
    "receipt",
    "required_replay",
    "required_stdout",
}
SEMANTIC_CONSTRAINTS = {
    "domain_objects_must_reference_declared_concrete_state_space": True,
    "abstract_witness_only_statement_sufficient": False,
    "forbidden_as_admission_evidence": ["separate_witnesses_do_not_combine"],
}


def repository_root(start: Path | None = None) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def checked_relative_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"invalid repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or any(token in value for token in "*?[]"):
        raise ValueError(f"unsafe repository-relative path: {value}")
    return path.as_posix()


def exact_tag_sha(root: Path, tag: str) -> str:
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--hash", f"refs/tags/{tag}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise ValueError(f"release tag does not exist as an exact tag ref: {tag}")
    return result.stdout.strip()


def anchored_tag_commit(root: Path, paper_id: str, tag: str) -> str:
    anchor_path = root / "docs" / "release-anchors" / f"{tag}.json"
    if not anchor_path.is_file():
        raise ValueError(f"release anchor is missing for {paper_id}: {anchor_path}")
    try:
        anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"release anchor is unreadable for {paper_id}: {error}") from error
    release_tag = anchor.get("release_tag")
    if anchor.get("paper_id") != paper_id or not isinstance(release_tag, dict):
        raise ValueError(f"release anchor identity is invalid for {paper_id}")
    if release_tag.get("name") != tag:
        raise ValueError(f"release anchor tag name mismatch for {paper_id}")

    actual_tag_sha = exact_tag_sha(root, tag)
    actual_commit = subprocess.run(
        ["git", "rev-parse", f"refs/tags/{tag}^{{commit}}"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if release_tag.get("tag_object_sha") != actual_tag_sha:
        raise ValueError(f"release tag object identity mismatch for {paper_id}")
    if release_tag.get("target_commit_sha") != actual_commit:
        raise ValueError(f"release tag target identity mismatch for {paper_id}")
    return actual_commit


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def materialize_commit(root: Path, commit_sha: str, destination: Path) -> None:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", commit_sha],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as stream:
        for member in stream.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe path in release archive: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise ValueError(f"unsupported entry in release archive: {member.name}")
        stream.extractall(destination, filter="data")


def validate_gate(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != TOP_LEVEL_KEYS:
        raise ValueError("inheritance gate has invalid top-level fields")
    if payload.get("schema") != SCHEMA or payload.get("status") != "PRE_INHERITANCE_GATE":
        raise ValueError("inheritance gate schema or status mismatch")
    consumer = payload.get("consumer")
    if not isinstance(consumer, str) or not re.fullmatch(r"PAPER[1-9][0-9]*", consumer):
        raise ValueError("inheritance gate consumer is invalid")
    if payload.get("semantic_constraints") != SEMANTIC_CONSTRAINTS:
        raise ValueError("inheritance gate semantic constraints are not canonical")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("inheritance gate has no owner sources")
    identities: set[tuple[str, str]] = set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
            raise ValueError("inheritance source has invalid fields")
        paper_id = source.get("paper_id")
        tag = source.get("release_tag")
        if not isinstance(tag, str):
            raise ValueError("inheritance source tag is invalid")
        match = TAG_PATTERN.fullmatch(tag)
        if match is None or paper_id != f"PAPER{match.group('number')}":
            raise ValueError("inheritance source identity does not match its tag")
        identity = (paper_id, tag)
        if identity in identities:
            raise ValueError(f"duplicate inheritance source: {paper_id} {tag}")
        identities.add(identity)
        checked_relative_path(source.get("validator"))
        checked_relative_path(source.get("receipt"))
        arguments = source.get("arguments")
        if not isinstance(arguments, list) or not arguments or not all(
            isinstance(value, str) and value for value in arguments
        ):
            raise ValueError(f"invalid validator arguments for {paper_id}")
        replay = source.get("required_replay")
        if not isinstance(replay, dict) or not replay or not all(
            isinstance(key, str) and value is True for key, value in replay.items()
        ):
            raise ValueError(f"invalid required replay truth for {paper_id}")
        markers = source.get("required_stdout")
        if not isinstance(markers, list) or not markers or not all(
            isinstance(value, str) and value for value in markers
        ):
            raise ValueError(f"invalid replay output markers for {paper_id}")
    return payload


def replay_source(repository: Path, source: dict[str, Any], timeout: int) -> None:
    tag = source["release_tag"]
    commit_sha = anchored_tag_commit(repository, source["paper_id"], tag)
    with tempfile.TemporaryDirectory(prefix=f"rime-{tag}-") as directory:
        checkout = Path(directory) / "repository"
        materialize_commit(repository, commit_sha, checkout)
        before = tracked_snapshot(checkout)

        receipt_path = checkout / checked_relative_path(source["receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("replay") != source["required_replay"]:
            raise ValueError(f"{source['paper_id']} receipt replay truth is not canonical")

        validator = checkout / checked_relative_path(source["validator"])
        if not validator.is_file():
            raise ValueError(f"tagged validator is missing: {source['validator']}")
        environment = dict(os.environ)
        environment.pop("PYTHONOPTIMIZE", None)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", str(validator), *source["arguments"]],
            cwd=checkout,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        if completed.returncode:
            raise ValueError(
                f"{source['paper_id']} tagged replay failed with exit "
                f"{completed.returncode}:\n{output.strip()}"
            )
        missing = [marker for marker in source["required_stdout"] if marker not in output]
        if missing:
            raise ValueError(
                f"{source['paper_id']} replay omitted required truth markers: {missing}"
            )
        after = tracked_snapshot(checkout)
        changed = sorted(
            path for path, digest in before.items() if after.get(path) != digest
        )
        if changed:
            raise ValueError(
                f"{source['paper_id']} replay modified tagged source bytes: {changed}"
            )
        print(
            f"PASS {source['paper_id']} inheritance replay: {tag}; "
            f"{len(source['required_stdout'])} truth markers"
        )


def verify_gate(repository: Path, gate_path: Path, timeout: int) -> None:
    payload = validate_gate(json.loads(gate_path.read_text(encoding="utf-8")))
    for source in payload["sources"]:
        replay_source(repository, source, timeout)
    print(
        f"PASS {payload['consumer']} pre-inheritance gate: "
        f"{len(payload['sources'])} versioned owner replays"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate")
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    try:
        root = repository_root(args.repository)
        gate = (root / checked_relative_path(args.gate)).resolve()
        gate.relative_to(root)
        verify_gate(root, gate, args.timeout)
    except (json.JSONDecodeError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, TypeError, ValueError) as error:
        print(f"FAIL inheritance gate: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
