#!/usr/bin/env python3
"""Audit generated TeX table shapes against the auto-table sizing heuristic.

This is a diagnostic script.  It does not modify files.  Run it after
``build.py --no-pdf`` or a normal build to inspect how pandoc longtables would
be classified by the postprocessor's table-sizing logic.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_BUILD_DIR = Path(
    os.environ.get("RIME_TEX_OUTPUT_DIR", ROOT / "output" / "tex")
).resolve()
DEFAULT_PAPERS = [f"paper{i}" for i in range(1, 8)] + ["ccs"]


def clean_cell(cell: str) -> str:
    """Strip LaTeX markup to approximate visible text length."""

    def _math_placeholder(match: re.Match[str]) -> str:
        inner = match.group(1)
        return "X" * max(2, len(inner) // 3)

    cell = re.sub(r"\$([^$]*)\$", _math_placeholder, cell)
    cell = re.sub(r"\\\((.+?)\\\)", _math_placeholder, cell)
    cell = re.sub(r"\\\[(.+?)\\\]", _math_placeholder, cell, flags=re.DOTALL)
    previous = None
    while previous != cell:
        previous = cell
        cell = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", "", cell)
        cell = re.sub(r"\\[a-zA-Z]+", "", cell)
    return cell.replace("{", "").replace("}", "").strip()


def data_body(body: str) -> str:
    """Return the data-row region of a pandoc longtable body."""
    match = re.search(r"\\endlastfoot\s*\n?", body)
    if match:
        return body[match.end():]
    match = re.search(r"\\endhead\s*\n", body)
    return body[match.end():] if match else body


def measure_cells(body: str) -> dict[int, int]:
    col_max: dict[int, int] = {}
    for row in data_body(body).split(r"\\"):
        if not row.strip():
            continue
        for index, cell in enumerate(row.split("&")):
            length = len(clean_cell(cell))
            col_max[index] = max(col_max.get(index, 0), length)
    return col_max


def count_data_rows(body: str) -> int:
    return len([row for row in data_body(body).split(r"\\") if row.strip()])


def count_cols(spec: str) -> int:
    inner = spec.strip()[1:-1].replace("@{}", "")
    p_cols = len(re.findall(r">\{[^}]*\}p\{[^{}]*(?:\{[^}]*\}[^{}]*)*\}", inner))
    return p_cols if p_cols > 0 else len(re.findall(r"[lrc]", inner))


def extract_braces(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "{":
        return "", start
    depth = 1
    index = start + 1
    while index < len(text) and depth > 0:
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    return text[start:index], index


def find_tables(text: str) -> list[tuple[str, str, str]]:
    tables: list[tuple[str, str, str]] = []
    pos = 0
    begin_tag = r"\begin{longtable}"
    end_tag = r"\end{longtable}"
    while True:
        idx = text.find(begin_tag, pos)
        if idx == -1:
            break
        brace = text.find("{", idx + len(begin_tag))
        if brace == -1:
            break
        spec, spec_end = extract_braces(text, brace)
        end_idx = text.find(end_tag, spec_end)
        if end_idx == -1:
            break
        body = text[spec_end:end_idx]
        full = text[idx:end_idx + len(end_tag)]
        tables.append((full, spec, body))
        pos = end_idx + len(end_tag)
    return tables


def classify_table(n_cols: int, n_rows: int, max_len: int) -> str:
    if n_rows > 22:
        action = "keep-longtable"
    elif max_len <= 20:
        action = "tabular"
    elif max_len < 80:
        action = "tabularx-lastX"
    else:
        action = "tabularx-allX"
    if n_cols > 8:
        action += "+resizebox"
    return action


def audit_paper(name: str, build_dir: Path) -> int:
    path = build_dir / f"{name}.tex"
    if not path.exists():
        print(f"{name}: missing {path.name}")
        return 0
    text = path.read_text(encoding="utf-8")
    tables = find_tables(text)
    print(f"\n{name}: {len(tables)} table(s)")
    for _full, spec, body in tables:
        n_cols = count_cols(spec)
        n_rows = count_data_rows(body)
        max_len = max(measure_cells(body).values(), default=0)
        action = classify_table(n_cols, n_rows, max_len)
        print(f"  {n_cols:2d} cols {n_rows:2d} rows max-len={max_len:3d} -> {action}")
    return len(tables)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "papers",
        nargs="*",
        help="Generated TeX basenames to audit, e.g. paper4 ccs.",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=DEFAULT_BUILD_DIR,
        help="Generated TeX directory (default: repository output/tex).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    papers = args.papers or DEFAULT_PAPERS
    total = sum(audit_paper(name, args.build_dir.resolve()) for name in papers)
    print(f"\nAudited {total} table(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
