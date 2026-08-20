"""Exact-byte lookup for explicitly declared historical release snapshots."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any


SNAPSHOT_RELATIVE_ROOT = Path("release-snapshots/rime-lite-v2.0")


def _digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _manifest(repository_root: Path) -> dict[str, Any]:
    path = repository_root / SNAPSHOT_RELATIVE_ROOT / "manifest.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _source_uri(uri: str, *, repository_root: Path, base_directory: Path) -> str:
    relative = Path(uri)
    if relative.is_absolute():
        raise ValueError("artifact URI must be repository-relative")
    resolved = _resolve_uri(relative, repository_root, base_directory)
    try:
        return resolved.relative_to(repository_root).as_posix()
    except ValueError as error:
        raise ValueError("artifact URI escapes repository root") from error


def _resolve_uri(relative: Path, repository_root: Path, base_directory: Path) -> Path:
    """Honor the repository-root URI convention used by the paper contracts."""

    if relative.parts and relative.parts[0] not in {".", ".."}:
        root_candidate = (repository_root / relative).resolve()
        if root_candidate.is_file():
            return root_candidate

    # A historical artifact loaded from the byte snapshot retains relative
    # references written against its materialized repository location. Resolve
    # those references against the corresponding source-tree directory before
    # trying the physical snapshot path.
    snapshot_root = (repository_root / SNAPSHOT_RELATIVE_ROOT).resolve()
    try:
        snapshot_base = base_directory.resolve().relative_to(snapshot_root / "files")
    except ValueError:
        snapshot_base = None
    if snapshot_base is not None:
        materialized_candidate = (
            repository_root / snapshot_base / relative
        ).resolve()
        if materialized_candidate.is_file():
            return materialized_candidate
    return (base_directory / relative).resolve()


def snapshot_path_for_reference(
    reference: dict[str, Any],
    *,
    repository_root: str | Path,
    base_directory: str | Path | None = None,
) -> Path | None:
    root = Path(repository_root).resolve()
    base = Path(base_directory).resolve() if base_directory is not None else root
    uri = reference.get("uri")
    expected = reference.get("digest", {}).get("value")
    if not isinstance(uri, str) or not isinstance(expected, str):
        return None
    try:
        source_uri = _source_uri(uri, repository_root=root, base_directory=base)
    except ValueError:
        return None
    entries = {
        item.get("source_uri"): item
        for item in _manifest(root).get("files", [])
        if isinstance(item, dict)
    }
    entry = entries.get(source_uri)
    if entry is None or entry.get("digest", "").lower() != expected.lower():
        return None
    snapshot_uri = entry.get("snapshot_uri")
    if not isinstance(snapshot_uri, str):
        return None
    snapshot_root = root / SNAPSHOT_RELATIVE_ROOT
    candidate = (snapshot_root / Path(*snapshot_uri.split("/"))).resolve()
    try:
        candidate.relative_to(snapshot_root.resolve())
    except ValueError:
        return None
    if not candidate.is_file() or _digest(candidate) != expected.lower():
        return None
    return candidate


def resolve_release_reference(
    reference: dict[str, Any],
    *,
    repository_root: str | Path,
    base_directory: str | Path | None = None,
) -> Path:
    root = Path(repository_root).resolve()
    base = Path(base_directory).resolve() if base_directory is not None else root
    uri = reference["uri"]
    relative = Path(uri)
    if relative.is_absolute():
        raise ValueError("artifact URI must be repository-relative")
    current = _resolve_uri(relative, root, base)
    try:
        current.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact URI escapes repository root") from error
    expected = reference.get("digest", {}).get("value")
    if current.is_file() and isinstance(expected, str) and _digest(current) == expected.lower():
        return current
    snapshot = snapshot_path_for_reference(
        reference,
        repository_root=root,
        base_directory=base,
    )
    return snapshot if snapshot is not None else current


def canonical_reference_for_path(
    path: str | Path,
    *,
    repository_root: str | Path,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    resolved = Path(path).resolve()
    snapshot_root = (root / SNAPSHOT_RELATIVE_ROOT).resolve()
    try:
        relative = resolved.relative_to(snapshot_root).as_posix()
    except ValueError:
        relative = None
    if relative is not None:
        entries = {
            item.get("snapshot_uri"): item
            for item in _manifest(root).get("files", [])
            if isinstance(item, dict)
        }
        entry = entries.get(relative)
        if entry is not None:
            return {
                "uri": entry["source_uri"],
                "digest": {"algorithm": "sha256", "value": entry["digest"]},
            }
    return {
        "uri": resolved.relative_to(root).as_posix(),
        "digest": {"algorithm": "sha256", "value": _digest(resolved)},
    }
