#!/usr/bin/env python3
"""Lint the Paper XXXIII manuscript, citations, and theorem surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper33" / "Paper XXXIII.md"
BIBLIOGRAPHY = ROOT / "papers" / "paper33" / "references-v1.bib"

EXPECTED_CITATIONS = {
    "berlinkovNicaud2020",
    "casasTorres2024",
    "cerny1964",
    "don2016",
    "dubuc1998",
    "eppstein1990",
    "ferensSzykula2026",
    "gonzeJungers2018",
    "paper29",
    "paper30",
    "paper31",
    "paper32",
    "ryzhikovShemyakov2018",
    "volkov2008",
    "volkov2022survey",
    "wolf2020",
}

EXPECTED_DECLARATIONS = {
    ("Proposition", "3.1"),
    ("Corollary", "4.1"),
    ("Theorem", "5.1"),
    ("Corollary", "5.2"),
    ("Definition", "6.1"),
    ("Proposition", "6.2"),
    ("Open Problem", "6.3"),
}

EXPECTED_TAGS = (
    {f"1.{index}" for index in range(1, 7)}
    | {f"2.{index}" for index in range(1, 10)}
    | {f"3.{index}" for index in range(1, 11)}
    | {f"4.{index}" for index in range(1, 5)}
    | {f"5.{index}" for index in range(1, 14)}
    | {f"6.{index}" for index in range(1, 3)}
    | {f"7.{index}" for index in range(1, 4)}
)

REQUIRED_HEADINGS = (
    "## Abstract",
    "## Notation Table {.unnumbered}",
    "## Introduction",
    "### Related Work and Novelty Boundary",
    "## The Inherited Stabilizer System",
    "## Source-Addressed Orbit Descent",
    "## Cyclic Phase Compression",
    "## Capacity-Isolated Order Breaking",
    "## The Remaining Mobility Problem",
    "## Computational Artifacts",
    "## Claim Status and Boundary",
    "## Conclusion",
    "## References {.unnumbered}",
)


def parse_bib_keys(text: str) -> set[str]:
    return set(re.findall(r"(?m)^@[A-Za-z]+\{([^,]+),", text))


def parse_citations(text: str) -> set[str]:
    keys: set[str] = set()
    for block in re.findall(r"\[@([^\]]+)\]", text):
        keys.update(re.findall(r"@([A-Za-z0-9_:-]+)", "@" + block))
    return keys


def parse_declarations(text: str) -> set[tuple[str, str]]:
    declarations = {
        (kind, number)
        for kind, number in re.findall(
            r"(?m)^\*\*(Proposition|Theorem|Corollary|Definition) "
            r"([0-9]+\.[0-9]+)",
            text,
        )
    }
    declarations.update(
        ("Open Problem", number)
        for number in re.findall(r"(?m)^### Open Problem ([0-9]+\.[0-9]+)", text)
    )
    return declarations


def validate_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing source: {path.relative_to(ROOT).as_posix()}")
        return ""
    raw = path.read_bytes()
    if b"\r" in raw:
        errors.append(f"non-LF source: {path.name}")
    if b"\x00" in raw:
        errors.append(f"NUL byte in source: {path.name}")
    for byte in raw:
        if byte < 32 and byte not in (9, 10):
            errors.append(f"control byte {byte} in source: {path.name}")
            break
    return raw.decode("utf-8")


def main() -> int:
    errors: list[str] = []
    paper = validate_text(PAPER, errors)
    bibliography = validate_text(BIBLIOGRAPHY, errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    citations = parse_citations(paper)
    bib_keys = parse_bib_keys(bibliography)
    if citations != EXPECTED_CITATIONS:
        errors.append(
            f"citation set mismatch: missing={sorted(EXPECTED_CITATIONS - citations)}, "
            f"extra={sorted(citations - EXPECTED_CITATIONS)}"
        )
    if bib_keys != EXPECTED_CITATIONS:
        errors.append(
            f"bibliography slice mismatch: missing={sorted(EXPECTED_CITATIONS - bib_keys)}, "
            f"extra={sorted(bib_keys - EXPECTED_CITATIONS)}"
        )

    declarations = parse_declarations(paper)
    if declarations != EXPECTED_DECLARATIONS:
        errors.append(
            f"declaration surface mismatch: missing={sorted(EXPECTED_DECLARATIONS - declarations)}, "
            f"extra={sorted(declarations - EXPECTED_DECLARATIONS)}"
        )

    tags = re.findall(r"\\tag\{([^}]+)\}", paper)
    tag_set = set(tags)
    if len(tags) != len(tag_set):
        errors.append("duplicate equation tag")
    if tag_set != EXPECTED_TAGS:
        errors.append(
            f"equation-tag mismatch: missing={sorted(EXPECTED_TAGS - tag_set)}, "
            f"extra={sorted(tag_set - EXPECTED_TAGS)}"
        )

    cursor = -1
    for heading in REQUIRED_HEADINGS:
        position = paper.find(heading)
        if position < 0:
            errors.append(f"missing heading: {heading}")
        elif position <= cursor:
            errors.append(f"heading out of order: {heading}")
        else:
            cursor = position

    corruption_patterns = {
        "bare qquad": r"(?<!\\)qquad",
        "bare quad": r"(?<![A-Za-z\\])quad(?![A-Za-z])",
        "bare left delimiter": r"(?<!\\)left\(",
        "bare right delimiter": r"(?<!\\)right\)",
    }
    for label, pattern in corruption_patterns.items():
        if re.search(pattern, paper):
            errors.append(f"{label} in manuscript")

    required_phrases = (
        "The concrete state \\(y\\) is essential.",
        "../../figures/paper33/fig1_source_addressed_incidence.png",
        "These calculations are bounded consistency controls.",
        "does not prove that the break set itself fails",
        "The finite controls do not enlarge the theorem domain.",
    )
    for phrase in required_phrases:
        if phrase not in paper:
            errors.append(f"missing claim firewall: {phrase}")

    forbidden_phrases = (
        "complete full-stabilizer classification",
        "proves projectable-origin supply",
        "establishes a reset bound",
    )
    for phrase in forbidden_phrases:
        if phrase in paper:
            errors.append(f"forbidden overclaim: {phrase}")

    paper32_block = re.search(
        r"@misc\{paper32,(.*?)(?=\n\})",
        bibliography,
        flags=re.DOTALL,
    )
    if paper32_block is None:
        errors.append("Paper XXXII bibliography entry missing")
    else:
        block = paper32_block.group(1)
        if "version 1.0, Zenodo" not in block:
            errors.append("Paper XXXII publication metadata mismatch")
        if "doi          = {10.5281/zenodo.23053169}" not in block:
            errors.append("Paper XXXII DOI mismatch")
        if "https://doi.org/10.5281/zenodo.23053169" not in block:
            errors.append("Paper XXXII DOI URL mismatch")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXIII manuscript source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
