"""Resolve the Paper XXIII package independently of the caller's cwd."""

from __future__ import annotations

import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = PACKAGE.parents[1]

if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))


def resolve_repository_reference(value: str | Path) -> Path:
    """Resolve a repository-relative artifact reference without using cwd."""

    path = Path(value)
    return path if path.is_absolute() else REPOSITORY / path


def repository_relative_reference(path: Path) -> str:
    """Return the stable repository-relative spelling of a source artifact."""

    return path.resolve().relative_to(REPOSITORY).as_posix()
