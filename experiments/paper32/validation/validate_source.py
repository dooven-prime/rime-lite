#!/usr/bin/env python3
"""Lint Paper XXXII source, citations, theorem labels, and cross-references."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper32" / "Paper XXXII.md"
BIBLIOGRAPHY = ROOT / "papers" / "paper32" / "references-v1.bib"

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
    "ryzhikovShemyakov2018",
    "volkov2008",
    "volkov2022survey",
    "wolf2020",
}

EXPECTED_DOIS = {
    "berlinkovNicaud2020": "10.1142/S0129054120420058",
    "casasTorres2024": "10.48550/arXiv.2409.19172",
    "don2016": None,
    "dubuc1998": None,
    "eppstein1990": "10.1137/0219033",
    "ferensSzykula2026": "10.1145/3798283",
    "gonzeJungers2018": "10.1007/978-3-319-98654-8_27",
    "paper29": "10.5281/zenodo.23028361",
    "paper30": "10.5281/zenodo.23034428",
    "paper31": "10.5281/zenodo.23050809",
    "ryzhikovShemyakov2018": "10.3233/FI-2018-1721",
    "volkov2008": "10.1007/978-3-540-88282-4_4",
    "volkov2022survey": "10.4213/rm10005e",
    "wolf2020": "10.4230/LIPIcs.FSTTCS.2020.58",
}

EXPECTED_TITLES = {
    "paper29": "Cyclic Lineage Dynamics and Rank-Five First-Exit Frontiers",
    "paper30": "Universal Return Groups and Punctured Rotations",
    "paper31": "Branch-Normalized Partial Returns in Single-Defect Circular Automata",
    "ferensSzykula2026": "Recognizing Completely Reachable Automata in Quadratic Time",
    "casasTorres2024": "Completely Reachable Almost Group Automata",
}

EXPECTED_INTERNAL_FIELDS = {
    "paper29": {
        "author": "Chen, WuJun",
        "howpublished": "RIME Paper XXIX, version 1.0, Zenodo",
        "year": "2026",
        "month": "sep",
        "url": "https://doi.org/10.5281/zenodo.23028361",
    },
    "paper30": {
        "author": "Chen, WuJun",
        "howpublished": "RIME Paper XXX, version 1.0, Zenodo",
        "year": "2026",
        "month": "sep",
        "url": "https://doi.org/10.5281/zenodo.23034428",
    },
    "paper31": {
        "author": "Chen, WuJun",
        "howpublished": "RIME Paper XXXI, version 1.0, Zenodo",
        "year": "2026",
        "month": "sep",
        "url": "https://doi.org/10.5281/zenodo.23050809",
    },
}

EXPECTED_DECLARATIONS = {
    ("Lemma", "2.1"),
    ("Proposition", "3.1"),
    ("Lemma", "4.1"),
    ("Lemma", "4.2"),
    ("Theorem", "4.3"),
    ("Theorem", "5.1"),
    ("Corollary", "5.2"),
    ("Corollary", "6.1"),
}


def parse_bib_entries(text: str) -> dict[str, dict[str, str]]:
    starts = list(re.finditer(r"(?m)^@([A-Za-z]+)\{([^,]+),\s*$", text))
    entries: dict[str, dict[str, str]] = {}
    for index, match in enumerate(starts):
        start = match.end()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        body = text[start:end]
        fields: dict[str, str] = {"entry_type": match.group(1)}
        for field_match in re.finditer(
            r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*"
            r"(?:\{(.*)\}|([^,\s]+)),?\s*$",
            body,
        ):
            fields[field_match.group(1).lower()] = (
                field_match.group(2)
                if field_match.group(2) is not None
                else field_match.group(3)
            )
        key = match.group(2)
        if key in entries:
            raise RuntimeError(f"duplicate bibliography key: {key}")
        entries[key] = fields
    return entries


def normalize_title(value: str) -> str:
    return value.replace("{{", "").replace("}}", "").replace("{", "").replace("}", "")


def validate() -> list[str]:
    errors: list[str] = []
    paper_bytes = PAPER.read_bytes()
    bib_bytes = BIBLIOGRAPHY.read_bytes()
    if b"\r" in paper_bytes:
        errors.append("manuscript is not LF-only")
    if b"\r" in bib_bytes:
        errors.append("bibliography is not LF-only")
    paper = paper_bytes.decode("utf-8")
    bibliography = bib_bytes.decode("utf-8")

    controls = [
        (index, ord(char))
        for index, char in enumerate(paper)
        if ord(char) < 32 and char not in "\n\t"
    ]
    if controls:
        errors.append(f"manuscript contains control characters: {controls[:3]}")

    for pattern, label in (
        (r"(?<!\\)\bqquad\b", "bare qquad"),
        (r"(?<!\\)\bquad\b", "bare quad"),
        (r"(?<!\\)\bleft(?=[(\[{])", "bare left delimiter"),
        (r"(?<!\\)\bright(?=[)\]}])", "bare right delimiter"),
    ):
        if re.search(pattern, paper):
            errors.append(f"manuscript contains {label}")

    equation_tags = re.findall(r"\\tag\{([0-9]+\.[0-9]+)\}", paper)
    duplicate_tags = sorted(
        tag for tag in set(equation_tags) if equation_tags.count(tag) > 1
    )
    if duplicate_tags:
        errors.append(f"duplicate equation tags: {duplicate_tags}")
    tag_set = set(equation_tags)
    equation_refs = set(re.findall(r"\(([0-9]+\.[0-9]+)\)", paper))
    missing_equations = sorted(equation_refs - tag_set)
    if missing_equations:
        errors.append(f"unresolved equation references: {missing_equations}")

    declaration_pattern = re.compile(
        r"\*\*(Lemma|Theorem|Proposition|Corollary) "
        r"([0-9]+\.[0-9]+) \([^*]+\)\.\*\*"
    )
    declarations = set(declaration_pattern.findall(paper))
    if declarations != EXPECTED_DECLARATIONS:
        errors.append(
            "theorem declaration surface drift: "
            f"expected={sorted(EXPECTED_DECLARATIONS)}, actual={sorted(declarations)}"
        )
    all_numbered_mentions = set(
        re.findall(r"\b(Lemma|Theorem|Proposition|Corollary) ([0-9]+\.[0-9]+)\b", paper)
    )
    unresolved_theorems = sorted(all_numbered_mentions - declarations)
    if unresolved_theorems:
        errors.append(f"unresolved theorem references: {unresolved_theorems}")

    for kind, number in declarations:
        start = paper.find(f"**{kind} {number} ")
        next_declaration = min(
            (
                position
                for other_kind, other_number in declarations
                if (position := paper.find(f"**{other_kind} {other_number} ")) > start
            ),
            default=len(paper),
        )
        next_section = paper.find("\n## ", start + 1)
        boundary = min(
            value for value in (next_declaration, next_section) if value != -1
        )
        if "**Proof." not in paper[start:boundary]:
            errors.append(f"{kind} {number} has no local proof block")

    citations = set(re.findall(r"@([A-Za-z0-9:_-]+)", paper))
    entries = parse_bib_entries(bibliography)
    keys = set(entries)
    if citations != EXPECTED_CITATIONS:
        errors.append(
            f"citation surface drift: expected={sorted(EXPECTED_CITATIONS)}, "
            f"actual={sorted(citations)}"
        )
    if keys != EXPECTED_CITATIONS:
        errors.append(
            f"bibliography slice drift: expected={sorted(EXPECTED_CITATIONS)}, "
            f"actual={sorted(keys)}"
        )

    for key, expected_doi in EXPECTED_DOIS.items():
        actual = entries.get(key, {}).get("doi")
        if actual != expected_doi:
            errors.append(f"DOI mismatch for {key}: expected={expected_doi}, actual={actual}")
    for key, expected_title in EXPECTED_TITLES.items():
        actual = normalize_title(entries.get(key, {}).get("title", ""))
        if actual != expected_title:
            errors.append(
                f"title mismatch for {key}: expected={expected_title!r}, actual={actual!r}"
            )
    for key, expected_fields in EXPECTED_INTERNAL_FIELDS.items():
        for field, expected in expected_fields.items():
            actual = entries.get(key, {}).get(field)
            if actual != expected:
                errors.append(
                    f"metadata mismatch for {key}.{field}: "
                    f"expected={expected!r}, actual={actual!r}"
                )

    required_markers = (
        "Paper XXXII | Version 1.0",
        "Proposition 3.1 (lane-wise dihedral classification)",
        "Theorem 4.3 (single-lane order-fiber transitivity)",
        "Theorem 5.1 (single-lane permutation dichotomy)",
        "Corollary 6.1 (lane-stabilizer Safe-Hit sandwich)",
        "## Computational Artifacts",
        "## Claim Status and Boundary",
        "Bounded arbitrary-permutation control",
        r"a\in\operatorname{Aut}(C_L)",
        r"\operatorname{Stab}(\mathcal C_\Delta)",
        "The finite audits are bounded consistency controls",
        "does not classify the multi-lane regime",
        "raw Safe-Hit",
        "typed transfer membership or projectability",
    )
    for marker in required_markers:
        if marker not in paper:
            errors.append(f"required manuscript marker missing: {marker}")

    forbidden = (
        "experiments/" + "synchronizing_automata",
        "all normalizer multipliers are classified",
        "general defect classification",
        "single-lane affine dichotomy",
    )
    for marker in forbidden:
        if marker in paper:
            errors.append(f"forbidden manuscript promotion: {marker}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL Paper XXXII source audit")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        "PASS Paper XXXII source audit: "
        f"{len(EXPECTED_DECLARATIONS)} declarations, "
        f"{len(EXPECTED_CITATIONS)} citation keys"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
