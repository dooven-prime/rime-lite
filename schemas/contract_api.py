"""Shared, language-neutral contract validation primitives.

Paper-specific validators own semantic rules. This module owns only the
cross-contract mechanics that must not drift between papers: JSON loading,
JSON Schema validation, digest verification, repository-bounded artifact
resolution, and the reader-facing result/claim status matrix.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


RESULT_CLAIM_STATUS_MATRIX: dict[str, set[str | None]] = {
    "DECLARED": {None, "Research Program"},
    "ESTABLISHED": {"Theorem"},
    "CERTIFIED": {"Computational Certificate"},
    "OBSERVED": {"Computational Observation"},
    "UNREACHED_AT_CUTOFF": {
        "Computational Certificate",
        "Computational Observation",
    },
    "NOT_APPLICABLE": {None},
    "NOT_DECLARED": {None},
}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def schema_errors(payload: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: [str(part) for part in error.path],
    )
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def file_digest(path: str | Path, algorithm: str = "sha256") -> str:
    result = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def resolve_artifact_path(
    uri: str,
    *,
    repository_root: str | Path,
    base_directory: str | Path | None = None,
) -> Path:
    root = Path(repository_root).resolve()
    base = Path(base_directory).resolve() if base_directory is not None else root
    try:
        base.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact base directory escapes repository root") from error
    relative = Path(uri)
    if relative.is_absolute():
        raise ValueError("artifact URI must be repository-relative")
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact URI escapes repository root") from error
    return resolved


def artifact_reference_errors(
    reference: dict[str, Any],
    *,
    label: str,
    repository_root: str | Path,
    base_directory: str | Path | None = None,
    allowed_algorithms: Iterable[str] = ("sha256",),
) -> list[str]:
    try:
        declared = reference["digest"]
        algorithm = declared["algorithm"]
        expected = declared["value"].lower()
    except (KeyError, TypeError, AttributeError):
        return [f"{label}: malformed digest declaration"]
    if algorithm not in set(allowed_algorithms):
        return [f"{label}: unsupported digest algorithm {algorithm!r}"]
    try:
        from schemas.release_snapshot import resolve_release_reference

        path = resolve_release_reference(
            reference,
            repository_root=repository_root,
            base_directory=base_directory,
        )
    except (ImportError, KeyError, TypeError, ValueError):
        try:
            path = resolve_artifact_path(
                reference["uri"],
                repository_root=repository_root,
                base_directory=base_directory,
            )
        except (KeyError, TypeError, ValueError) as error:
            return [f"{label}: {error}"]
    if not path.is_file():
        return [f"{label}: referenced file does not exist"]
    try:
        actual = file_digest(path, algorithm)
    except ValueError:
        return [f"{label}: unsupported digest algorithm {algorithm!r}"]
    return [] if actual == expected else [f"{label}: digest mismatch"]


def result_claim_status_error(
    result_state: str,
    claim_status: str | None,
    *,
    label: str,
) -> str | None:
    allowed = RESULT_CLAIM_STATUS_MATRIX.get(result_state)
    if allowed is None:
        return f"{label}: unknown result state {result_state!r}"
    if claim_status not in allowed:
        return (
            f"{label}: illegal result/claim status pair "
            f"{result_state!r} + {claim_status!r}"
        )
    return None
