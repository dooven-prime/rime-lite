#!/usr/bin/env python3
"""Lint the Paper XXXIV manuscript, citations, and theorem surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper34" / "Paper XXXIV.md"
BIBLIOGRAPHY = ROOT / "papers" / "paper34" / "references-v1.bib"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_lf_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing file: {path.relative_to(ROOT).as_posix()}")
        return ""
    raw = path.read_bytes()
    require(b"\r" not in raw, f"non-LF source: {path.name}", errors)
    require(b"\x00" not in raw, f"NUL byte in source: {path.name}", errors)
    return raw.decode("utf-8")


def citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\[@([^\]]+)\]", text):
        for item in group.split(";"):
            key = item.strip().lstrip("@")
            if key:
                keys.add(key)
    return keys


def bibliography_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", text))


def main() -> int:
    errors: list[str] = []
    paper = read_lf_text(PAPER, errors)
    bibliography = read_lf_text(BIBLIOGRAPHY, errors)

    if not errors:
        require(
            paper.startswith(
                "# Terminal Orientation and Survivor Incidence in Five-Token Return Dynamics\n"
            ),
            "manuscript title drift",
            errors,
        )
        require("**Paper XXXIV | Version 1.0**" in paper, "release identity missing", errors)
        require(
            "This paper (Paper XXXIV of the RIME program)" in paper,
            "numbered positioning statement missing",
            errors,
        )

        required_surfaces = (
            "Proposition 2.1 (normalized strict-exit incidence transport)",
            "Lemma 3.1 (identity-path simulation)",
            "Lemma 3.2 (reachable orientation fiber)",
            "Lemma 3.3 (missing-hole terminal realization)",
            "Theorem 4.1 (one-lane dihedral survivor-spectrum classification)",
            "Corollary 5.1 (orientation-spectrum factorization)",
            "Corollary 5.2 (pair-level non-descent)",
        )
        for surface in required_surfaces:
            require(surface in paper, f"missing theorem surface: {surface}", errors)

        required_firewalls = (
            "The terminal exponent $u$ remains",
            "must come from\nthe same labelled path and the same terminal event",
            "$\\operatorname{OriSpec}$ is minimal or sufficient for arbitrary branches",
            "raw survivor incidence",
            "typed transfer membership",
            "same-witness projectability",
        )
        for firewall in required_firewalls:
            require(firewall in paper, f"missing claim firewall: {firewall}", errors)

        require(
            "DIRECTION_DRAFT" not in paper,
            "research ledger must not be a manuscript dependency",
            errors,
        )
        broader_tree = "experiments/" + "synchronizing_automata"
        require(
            broader_tree not in paper,
            "manuscript depends on broader exploratory tree",
            errors,
        )

        tags = re.findall(r"\\tag\{([^}]+)\}", paper)
        require(len(tags) == len(set(tags)), "duplicate equation tags", errors)
        require(len(tags) >= 30, "unexpectedly small equation surface", errors)

        broken_patterns = (
            r"(?<!\\)qquad",
            r"(?<![\\q])quad(?=\s|\()",
            r"(?<!\\)left\(",
            r"(?<!\\)right\)",
        )
        for pattern in broken_patterns:
            require(
                re.search(pattern, paper) is None,
                f"possible TeX escape corruption: {pattern}",
                errors,
            )

        cited = citation_keys(paper)
        defined = bibliography_keys(bibliography)
        require(cited <= defined, f"undefined citations: {sorted(cited - defined)}", errors)
        require(defined <= cited, f"unused bibliography entries: {sorted(defined - cited)}", errors)

        require(
            "doi          = {10.5281/zenodo.23053169}" in bibliography,
            "Paper XXXII DOI missing",
            errors,
        )
        require(
            "doi          = {10.5281/zenodo.23056470}" in bibliography,
            "Paper XXXIII DOI missing",
            errors,
        )
        for paper_id, doi in (
            ("Paper XXIX", "10.5281/zenodo.23028361"),
            ("Paper XXX", "10.5281/zenodo.23034428"),
            ("Paper XXXI", "10.5281/zenodo.23050809"),
            ("Paper XXXII", "10.5281/zenodo.23053169"),
            ("Paper XXXIII", "10.5281/zenodo.23056470"),
        ):
            require(
                f"note         = {{DOI: \\url{{https://doi.org/{doi}}}}}" in bibliography,
                f"{paper_id} reader-facing DOI missing",
                errors,
            )
        require(
            "Publication identity pending" not in bibliography,
            "stale Paper XXXIII pending-publication metadata",
            errors,
        )
        require(
            "By Paper XXXI's lane-order preservation theorem" in paper,
            "Paper XXXI lane-order dependency is not explicit",
            errors,
        )
        require(
            "A paper-owned Lean formalization machine-checks the data-independent"
            in paper,
            "Lean scope paragraph missing",
            errors,
        )
        require(
            "It is not an independent mathematical validation." in paper,
            "local closure authority boundary missing",
            errors,
        )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Paper XXXIV manuscript source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
