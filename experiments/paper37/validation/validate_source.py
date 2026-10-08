#!/usr/bin/env python3
"""Lint the owning manuscript, bibliography, numbering, and claim boundary."""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/paper37/Paper XXXVII.md"
RESULT_HEADINGS = (
    ("Lemma", "3.1"), ("Lemma", "3.2"), ("Lemma", "3.3"),
    ("Theorem", "4.1"), ("Corollary", "4.2"), ("Proposition", "4.3"),
    ("Corollary", "4.4"), ("Theorem", "5.1"), ("Theorem", "5.2"),
    ("Corollary", "5.3"), ("Proposition", "6.1"),
    ("Theorem", "6.2"), ("Theorem", "6.3"),
)
INTERNAL_DOIS = {
    "paper30": "10.5281/zenodo.23034428",
    "paper31": "10.5281/zenodo.23050809",
    "paper33": "10.5281/zenodo.23056470",
    "paper35": "10.5281/zenodo.23085408",
    "paper36": "10.5281/zenodo.23093673",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def source(path: Path) -> str:
    raw = path.read_bytes()
    require(b"\r" not in raw, f"non-LF source: {path.relative_to(ROOT)}")
    text = raw.decode("utf-8")
    require(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text) is None,
            f"control character: {path.relative_to(ROOT)}")
    return text


def has_damaged_spacing(math: str) -> bool:
    return re.search(r"(?<![\\A-Za-z])(?:qquad|quad)(?=\s|[({])", math) is not None


def validate() -> None:
    manuscript = source(PAPER)
    bibliography = source(ROOT / "papers/paper37/references-v1.bib")
    require(manuscript.startswith(
        "# Lineage Permutation Groups and Complete Ordinary-Lane Survivor Frontiers\n"
        "### Guarded Relocation and Phase-Coset Boundaries\n"
    ), "canonical title drift")
    require("Paper XXXVII | Version 1.0" in manuscript, "version status drift")
    require("C_{\\rm src}" in manuscript, "source-lane notation missing")
    require("right-coset set" in manuscript and "H\\kappa" in manuscript,
            "phase-coset convention missing")
    require("not a quotient group" in manuscript, "coset/group boundary missing")
    require("state-set bijection alone" in manuscript,
            "state-set/transition boundary missing")
    require("exhaustive five-stratum classification" in manuscript
            and "does not assert an" in manuscript, "subgroup packaging boundary missing")
    require("No finite replay database or machine-checked formalization is claimed."
            not in manuscript, "artifact status has not been updated")
    require("bounded consistency controls" in re.sub(r"\s+", " ", manuscript),
            "bounded evidence boundary missing")
    flat = re.sub(r"\s+", " ", manuscript)
    require("partial Lean spine" in flat
            and "guard, confinement, relocation words, and terminal-placement converse remain"
            in flat,
            "partial-formalization coverage boundary missing")
    require("exploratory" not in "\n".join(re.findall(
        r"\]\(([^)]+)\)", manuscript
    )), "manuscript depends on exploratory paths")

    entries = re.findall(r"(?m)^@\w+\{([^,]+),", bibliography)
    cited = set(re.findall(r"(?<!\w)@([A-Za-z0-9_]+)", manuscript))
    require(len(entries) == len(set(entries)), "duplicate bibliography key")
    require(cited == set(entries), "citation slice mismatch")
    for key, doi in INTERNAL_DOIS.items():
        block = re.search(rf"(?ms)^@misc\{{{key},(.*?)(?=^@\w|\Z)", bibliography)
        require(block is not None and doi in block.group(1)
                and "version 1.0, Zenodo" in block.group(1),
                f"published internal identity missing: {key}")
    require("pending" not in bibliography.lower(), "stale internal publication metadata")

    section = 0
    headings = []
    for line in manuscript.splitlines():
        if line.startswith("## ") and ".unnumbered" not in line and line != "## Abstract":
            section += 1
        result = re.match(r"^### (Lemma|Theorem|Corollary|Proposition) (\d+\.\d+)\.", line)
        if result:
            require(int(result[2].split(".")[0]) == section, "theorem/section numbering drift")
            headings.append((result[1], result[2]))
    require(tuple(headings) == RESULT_HEADINGS, "result inventory drift")
    tags = re.findall(r"\\tag\{(\d+\.\d+)\}", manuscript)
    require(len(tags) == len(set(tags)), "duplicate equation tag")
    require(set(re.findall(r"\((\d+\.\d+)\)", manuscript)) <= set(tags),
            "unknown equation reference")
    displays = re.findall(r"(?m)^\$\$$", manuscript)
    require(len(displays) % 2 == 0, "unbalanced display delimiters")
    for math in re.findall(r"(?ms)^\$\$\n(.*?)^\$\$", manuscript):
        require(not has_damaged_spacing(math),
                "damaged TeX spacing command")
    for directory, subdirectories, filenames in os.walk(ROOT / "experiments/paper37"):
        subdirectories[:] = [
            name for name in subdirectories if name not in {"__pycache__", ".lake"}
        ]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = Path(directory) / name
            tree = ast.parse(source(path), filename=str(path))
            require(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
                    f"optimization-sensitive assert: {path.name}")


if __name__ == "__main__":
    validate()
    print("PASS: Paper XXXVII source, bibliography, cross-references, and boundaries")
