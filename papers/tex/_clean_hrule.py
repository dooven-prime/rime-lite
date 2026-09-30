#!/usr/bin/env python3
"""Normalize markdown horizontal rules for the LaTeX build pipeline.

Pandoc can interpret a bare ``---`` near the start of a markdown document as
YAML front matter.  The RIME markdown convention uses ``***`` as the stable
horizontal-rule marker, so this helper rewrites standalone ``---`` lines to
``***``.

The build pipeline imports :func:`clean_hrules` and applies it in-memory before
calling pandoc.  The CLI is kept for one-off cleanup of source files.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

DEFAULT_SOURCES = [
    ROOT / "ccs" / "canonical_specification.md",
    ROOT / "papers" / "paper1" / "Paper I.md",
    ROOT / "papers" / "paper2" / "Paper II.md",
    ROOT / "papers" / "paper3" / "Paper III.md",
    ROOT / "papers" / "paper4" / "Paper IV.md",
    ROOT / "papers" / "paper5" / "Paper V.md",
    ROOT / "papers" / "paper6" / "Paper VI.md",
    ROOT / "papers" / "paper7" / "Paper VII.md",
]

HRULE_RE = re.compile(r"^---\s*$")


def clean_hrules(text: str) -> tuple[str, int]:
    """Return text with standalone ``---`` rules converted to ``***``.

    The second return value is the number of replacements.
    """
    changed = 0
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        newline = ""
        body = line
        if line.endswith("\r\n"):
            body, newline = line[:-2], "\r\n"
        elif line.endswith("\n"):
            body, newline = line[:-1], "\n"
        if HRULE_RE.match(body.strip()) and "|" not in body:
            out.append("***" + newline)
            changed += 1
        else:
            out.append(line)
    return "".join(out), changed


def clean_file(path: Path, *, check: bool = False) -> int:
    """Clean one file in place, or report needed changes in check mode."""
    text = path.read_text(encoding="utf-8")
    cleaned, changed = clean_hrules(text)
    if changed and not check:
        path.write_text(cleaned, encoding="utf-8")
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files to clean. Defaults to CCS and Papers I--VII.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report files that would change without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = args.paths or DEFAULT_SOURCES
    total = 0
    for path in paths:
        if not path.exists():
            print(f"{path}: missing")
            continue
        changed = clean_file(path, check=args.check)
        total += changed
        status = "would replace" if args.check else "replaced"
        print(f"{path.name}: {status} {changed} horizontal rule(s)")
    if args.check and total:
        return 1
    print("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
