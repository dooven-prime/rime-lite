#!/usr/bin/env python3
"""Lint the Paper XXXV manuscript, bibliography, and theorem surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper35" / "Paper XXXV.md"
BIBLIOGRAPHY = ROOT / "papers" / "paper35" / "references-v1.bib"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_lf(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing source: {path.relative_to(ROOT).as_posix()}")
        return ""
    raw = path.read_bytes()
    require(b"\r" not in raw, f"non-LF source: {path.name}", errors)
    require(b"\x00" not in raw, f"NUL byte in source: {path.name}", errors)
    return raw.decode("utf-8")


def main() -> int:
    errors: list[str] = []
    paper = read_lf(PAPER, errors)
    bibliography = read_lf(BIBLIOGRAPHY, errors)
    if not errors:
        require(
            paper.startswith(
                "# Cyclic-Order Laws and Complete Survivor Frontiers in One-Lane Five-Token Dynamics\n"
            ),
            "title drift",
            errors,
        )
        require("**Paper XXXV | Version 1.0**" in paper, "version identity missing", errors)
        for heading in (
            "## Abstract",
            "## Notation Table {.unnumbered}",
            "## Introduction",
            "### Related Work and Novelty Boundary",
            "### The lineage-order subgroup",
            "## Terminal-Phase Collapse",
            "## Complete Survivor and Frontier Classification",
            "## Computational Artifacts",
            "## Claim Status and Boundary",
            "## References {.unnumbered}",
        ):
            require(heading in paper, f"missing heading: {heading}", errors)

        paper_flat = " ".join(paper.split())
        for phrase in (
            "does not assert typed transfer membership",
            "does not solve the multi-lane",
            "finite artifacts are consistency controls",
            "not proofs of the all-$n$ theorems",
            "left-coset space, not a quotient group",
            "denotes the set of three-element subsets",
            "Minimality is not asserted, and the converse implication is not claimed",
            "Paper XXXII, Theorem 4.3 supplies",
            "Paper XXXIV, Lemma 3.1",
        ):
            require(phrase in paper_flat, f"claim firewall missing: {phrase}", errors)

        require("\\Phi_a(\\mu)=" in paper, "phase-collapse formula missing", errors)
        require("K_a^{\\rm ord}" in paper, "order subgroup missing", errors)
        require("m_a(F)\\binom{n-2}{3}" in paper, "survivor formula missing", errors)
        for theorem in (
            "**Theorem A (order reduction).**",
            "**Theorem 4.2 (all-hole terminal-phase collapse; Theorem B).**",
            "**Theorem C (complete one-lane survivor frontier).**",
        ):
            require(theorem in paper, f"missing principal theorem: {theorem}", errors)

        require(
            "doi          = {10.5281/zenodo.23072915}" in bibliography,
            "Paper XXXIV DOI missing or stale",
            errors,
        )
        require(
            "Publication identity pending" not in bibliography,
            "stale Paper XXXIV publication status",
            errors,
        )

        tags = re.findall(r"\\tag\{([^}]+)\}", paper)
        require(len(tags) == len(set(tags)), "duplicate equation tag", errors)

        citation_keys: set[str] = set()
        for group in re.findall(r"\[@([^\]]+)\]", paper):
            citation_keys.update(
                token.strip().lstrip("@")
                for token in group.split(";")
                if token.strip()
            )
        bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bibliography, re.MULTILINE))
        require(citation_keys <= bib_keys, f"missing bibliography keys: {sorted(citation_keys - bib_keys)}", errors)
        require(bib_keys <= citation_keys, f"unused bibliography keys: {sorted(bib_keys - citation_keys)}", errors)

        for pattern, label in (
            (r"(?<!\\)qquad", "bare qquad"),
            (r"(?<![\\q])quad", "bare quad"),
            (r"=left\(", "bare left delimiter"),
            (r"(?<!\\)textbf", "bare textbf"),
        ):
            require(re.search(pattern, paper) is None, f"possible TeX escape damage: {label}", errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXV manuscript source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
