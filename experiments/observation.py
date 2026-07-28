"""Versioned cached observations for deterministic experiment scripts.

This module belongs to experiment orchestration, not the public ``rime``
mathematical API. An observation artifact records what one completed run
reported together with
the declared source files, parameters, runtime, and repository provenance.
It is a review aid, not a substitute for rerunning a mathematical certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import argparse
import json
from pathlib import Path
import platform
import subprocess
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "rime.experiment-observation.v1"
ARTIFACT_ROLE = "cached_computational_observation"
AUTHORITY_NOTE = (
    "Cached review aid. It records one completed run and does not "
    "replace the executable certificate or promote its claim status."
)


@dataclass(frozen=True)
class ObservationCheck:
    """Result of structural and declared-source validation."""

    valid: bool
    current: bool
    errors: tuple[str, ...]
    stale_sources: tuple[str, ...]

    @property
    def reusable(self) -> bool:
        """Whether the artifact is valid and matches all declared sources."""
        return self.valid and self.current


def utc_now() -> str:
    """Return a stable UTC timestamp suitable for JSON provenance."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def file_sha256(path: Path) -> str:
    """Hash one file without loading it fully into memory."""
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_source(root: Path, source: Path) -> tuple[Path, str]:
    root = root.resolve()
    resolved = (
        source.resolve() if source.is_absolute() else (root / source).resolve()
    )
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"source is outside repository root: {source}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"declared source does not exist: {relative}")
    return resolved, relative.as_posix()


def build_source_manifest(
    root: Path, sources: Iterable[Path | str]
) -> list[dict[str, str]]:
    """Build a deterministic manifest for explicitly declared source files."""
    entries: dict[str, dict[str, str]] = {}
    for source in sources:
        resolved, relative = _relative_source(root, Path(source))
        entries[relative] = {"path": relative, "sha256": file_sha256(resolved)}
    if not entries:
        raise ValueError("at least one source file must be declared")
    return [entries[path] for path in sorted(entries)]


def source_set_sha256(manifest: Sequence[Mapping[str, str]]) -> str:
    """Hash the ordered path/hash pairs in a declared source manifest."""
    digest = sha256()
    for entry in manifest:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def package_versions(distributions: Iterable[str]) -> dict[str, str]:
    """Return installed distribution versions without importing packages."""
    versions: dict[str, str] = {}
    for distribution in distributions:
        try:
            versions[distribution] = version(distribution)
        except PackageNotFoundError:
            versions[distribution] = "uninstalled-source-tree"
    return versions


def git_provenance(root: Path) -> dict[str, Any]:
    """Return commit identity and tracked-worktree state when Git is available."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--short", "--untracked-files=no"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"commit": "unavailable", "tracked_worktree": "unavailable"}
    return {"commit": commit, "tracked_worktree": "dirty" if status else "clean"}


def write_experiment_observation(
    path: Path,
    *,
    root: Path,
    experiment_id: str,
    paper: str,
    command: Sequence[str],
    sources: Iterable[Path | str],
    parameters: Mapping[str, Any],
    observations: Mapping[str, Any],
    claim_status: str,
    claim_scope: str,
    limitations: Sequence[str],
    started_at_utc: str,
    elapsed_seconds: float,
    distributions: Iterable[str] = (),
) -> dict[str, Any]:
    """Write one successful, source-addressed experiment observation."""
    root = root.resolve()
    manifest = build_source_manifest(root, sources)
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "authority": AUTHORITY_NOTE,
        "experiment": {
            "id": experiment_id,
            "paper": paper,
            "command": list(command),
        },
        "claim": {
            "status": claim_status,
            "scope": claim_scope,
            "limitations": list(limitations),
        },
        "run": {
            "status": "passed",
            "started_at_utc": started_at_utc,
            "elapsed_seconds": round(float(elapsed_seconds), 6),
            "parameters": dict(parameters),
        },
        "provenance": {
            "git": git_provenance(root),
            "runtime": {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "packages": package_versions(distributions),
            },
            "source_scope": "explicitly_declared_files",
            "source_set_sha256": source_set_sha256(manifest),
            "sources": manifest,
        },
        "observations": dict(observations),
    }

    path = path.resolve() if path.is_absolute() else (root / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(record, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return record


def check_experiment_observation(path: Path, *, root: Path) -> ObservationCheck:
    """Validate an artifact and compare every declared source hash."""
    errors: list[str] = []
    stale_sources: list[str] = []
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ObservationCheck(False, False, (f"cannot read artifact: {exc}",), ())

    if not isinstance(record, dict):
        return ObservationCheck(False, False, ("artifact root must be an object",), ())
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {record.get('schema_version')!r}")
    if record.get("artifact_role") != ARTIFACT_ROLE:
        errors.append(f"unexpected artifact_role: {record.get('artifact_role')!r}")
    if not isinstance(record.get("observations"), dict):
        errors.append("observations must be an object")
    if not isinstance(record.get("experiment"), dict):
        errors.append("experiment must be an object")
    if not isinstance(record.get("claim"), dict):
        errors.append("claim must be an object")
    run = record.get("run")
    if not isinstance(run, dict) or run.get("status") != "passed":
        errors.append("run.status must be 'passed'")

    provenance = record.get("provenance")
    manifest = provenance.get("sources") if isinstance(provenance, dict) else None
    if not isinstance(manifest, list) or not manifest:
        errors.append("provenance.sources must be a non-empty array")
        manifest = []

    recorded_entries: list[dict[str, str]] = []
    recorded_paths: set[str] = set()
    root = root.resolve()
    for entry in manifest:
        if not isinstance(entry, dict):
            errors.append("source manifest entries must be objects")
            continue
        relative = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("source entries require string path and sha256")
            continue
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            errors.append(f"source entry has invalid sha256: {relative}")
            continue
        if relative in recorded_paths:
            errors.append(f"duplicate source entry: {relative}")
            continue
        recorded_paths.add(relative)
        recorded_entries.append({"path": relative, "sha256": expected})
        try:
            resolved, normalized = _relative_source(root, Path(relative))
        except (ValueError, FileNotFoundError):
            stale_sources.append(relative)
            continue
        actual = file_sha256(resolved)
        if normalized != relative or actual != expected:
            stale_sources.append(relative)

    if isinstance(provenance, dict) and manifest:
        expected_set_hash = provenance.get("source_set_sha256")
        if expected_set_hash != source_set_sha256(recorded_entries):
            errors.append("source_set_sha256 does not match the recorded manifest")

    valid = not errors
    return ObservationCheck(valid, valid and not stale_sources, tuple(errors), tuple(stale_sources))


def format_observation_check(path: Path, check: ObservationCheck) -> str:
    """Format a concise review-facing status message."""
    if check.reusable:
        return f"CURRENT: {path} matches all declared source hashes"
    lines = [f"NOT CURRENT: {path}"]
    lines.extend(f"  invalid: {message}" for message in check.errors)
    lines.extend(f"  stale source: {source}" for source in check.stale_sources)
    return "\n".join(lines)


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    check = check_experiment_observation(args.artifact, root=args.root)
    print(format_observation_check(args.artifact, check))
    return 0 if check.reusable else 1


if __name__ == "__main__":
    raise SystemExit(_main())
