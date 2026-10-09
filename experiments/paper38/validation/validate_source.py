#!/usr/bin/env python3
"""Check canonical numbering, citations, TeX source, and scope firewalls."""

import ast
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = (
    ("Theorem", "3.1"), ("Proposition", "3.2"),
    ("Lemma", "4.1"), ("Lemma", "4.2"), ("Lemma", "4.3"),
    ("Theorem", "4.4"), ("Theorem", "5.1"), ("Corollary", "6.1"),
    ("Lemma", "A.1"), ("Proposition", "A.2"),
)
MAIN_SECTIONS = (
    "Introduction",
    "Raw System and Return-Count Convention",
    "Exact Return Layers and Same-Witness Realization",
    "Uniform Finite Return-Budget Realization",
    "An All-g Budget-Frontier Non-Descent Family",
    "Conditional Original-Letter Consequence",
    "Scope and Open Boundaries",
    "Computational Artifacts",
    "Claim Status and Boundary",
    "Conclusion",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_source(path):
    data = path.read_bytes()
    require(b"\r" not in data, f"non-LF source: {path.name}")
    text = data.decode("utf-8")
    require(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text) is None, "control character")
    return text


def validate():
    text = read_source(ROOT / "papers/paper38/Paper XXXVIII.md")
    bib = read_source(ROOT / "papers/paper38/references-v1.bib")
    require(text.startswith("# Exact Return Layers and Budgeted Survivor Frontiers\n"), "title drift")
    require("Paper XXXVIII | Version 1.0" in text, "version status drift")
    flat = re.sub(r"\s+", " ", text)
    for clause in (
        "includes that last occurrence", "one actual witness", "right cosets",
        "not append an internal step to a completed strict exit",
        "not a count separation", "excludes entry cost", "partial Lean algebraic spine",
        "bounded consistency controls", "same terminal permutation",
    ):
        require(clause in flat, f"scope firewall missing: {clause}")
    require("actual, collision-free returns" not in text
            and "single actual guarded injection sequence" not in text, "ambiguous witness wording")
    require("No assertion that every placement can be padded to exactly 24 returns" in flat,
            "cumulative/exact budget boundary missing")
    require("not a complete formalization of the all-$g$ geometric results" in flat
            and "actual label-word realization" in flat, "partial Lean coverage firewall missing")
    require("source-specific realization theorem is invoked here to discharge it" in flat
            and "not an independent original-letter length result" in flat,
            "conditional original-letter realization boundary missing")
    for status in ("Proved conditional corollary", "Proved auxiliary lemma and proposition",
                   "Bounded consistency control", "Partial formalization"):
        require(status in text, f"claim-status distinction missing: {status}")
    require("First exits and budgets are relative to these five lineages" in flat
            and "not asserted to be the complete current image reached from the initial $Q$" in flat,
            "local-source/whole-image boundary missing")
    require("The source assumption is not an entry-supply conclusion" in flat
            and "the full normalized carrier $E$ cannot supply this entrance" in flat,
            "full-lane entry-domain boundary missing")
    entries = re.findall(r"(?m)^@\w+\{([^,]+),", bib)
    citations = set(re.findall(r"(?<!\w)@([A-Za-z0-9_]+)", text))
    require(len(entries) == len(set(entries)) and set(entries) == citations, "bibliography slice mismatch")
    block = re.search(r"(?ms)^@misc\{paper37,(.*?)(?=^@|\Z)", bib)
    require(block is not None and "version 1.0, Zenodo" in block[1]
            and "10.5281/zenodo.23227579" in block[1], "published XXXVII identity missing")
    require("10.15826/umj.2024.2.004" in bib and "pending" not in bib.lower(), "bibliography metadata drift")
    headings = []
    section = 0
    for line in text.splitlines():
        if (line.startswith("## ") and ".unnumbered" not in line
                and line != "## Abstract" and not line.startswith("## Appendix ")):
            section += 1
            require(section <= len(MAIN_SECTIONS)
                    and line == f"## {MAIN_SECTIONS[section - 1]}",
                    "section order drift")
        found = re.match(r"^### (Lemma|Theorem|Corollary|Proposition) ([\dA]+\.\d+)\.", line)
        if found:
            if not found[2].startswith("A."):
                require(int(found[2].split(".")[0]) == section, "result/section mismatch")
            headings.append((found[1], found[2]))
    require(section == len(MAIN_SECTIONS) and tuple(headings) == RESULTS,
            "theorem inventory drift")
    tags = re.findall(r"\\tag\{([\dA]+\.\d+)\}", text)
    require(len(tags) == 34 and len(set(tags)) == 34, "equation inventory drift")
    require(set(re.findall(r"\(([\dA]+\.\d+)\)", text)) <= set(tags), "unknown equation reference")
    require(len(re.findall(r"(?m)^\$\$$", text)) == 68, "display delimiter drift")
    for math in re.findall(r"(?ms)^\$\$\n(.*?)^\$\$", text):
        require(re.search(r"(?<![\\A-Za-z])(?:qquad|quad|left|right)(?=\s|[({])", math) is None,
                "damaged TeX escape")
        require(math.count("{") == math.count("}"), "unbalanced math braces")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        require("exploratory" not in target and "unnumbered" not in target
                and "synchronizing_automata" not in target, "nonpublic manuscript dependency")
    for directory, subdirectories, filenames in os.walk(ROOT / "experiments/paper38"):
        subdirectories[:] = [name for name in subdirectories if name not in {"__pycache__", ".lake"}]
        for filename in filenames:
            if filename.endswith(".py"):
                path = Path(directory) / filename
                tree = ast.parse(read_source(path))
                require(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
                        f"optimization-sensitive assertion: {path.name}")


if __name__ == "__main__":
    validate()
    print("PASS: Paper XXXVIII source, citations, numbering, and scope boundaries")
