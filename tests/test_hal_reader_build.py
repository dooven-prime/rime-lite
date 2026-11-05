"""Pure regressions for the shared unnumbered HAL reader profile."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "papers" / "tex"))

from build_hal import (  # noqa: E402
    normalize_body,
    keep_statements,
    parse_manuscript,
    read_config,
    tagged_equations,
    template_fields,
)


CONFIG = {
    "author": "WuJun Chen",
    "affiliation": "Independent Researcher",
    "date": "Preprint, November 2026",
    "pdf_name": "reader.pdf",
    "source_date_epoch": "1793836800",
}
BODY = (
    "## 1. Introduction\n\n### Lemma 1.1. Statement\n\n"
    "**Proof.** Text. $\\square$\n\n"
    "## 2. Result\n\nText.\n\n"
    "## Appendix A. Details\n\nText.\n\n## References\n"
)


def rejects(function, *args) -> None:
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError(f"invalid HAL reader input accepted by {function.__name__}")


def test_source_contract() -> None:
    source = (
        "# Example\n\n**WuJun Chen**\n\n"
        "Independent Researcher | Preprint, November 2026\n\n"
        "## Abstract\n\nA result.\n\n**Keywords:** one; two\n\n" + BODY
    )
    assert parse_manuscript(source, CONFIG) == ("Example", "A result.", "one; two", BODY.strip())
    rejects(parse_manuscript, source.replace("Independent Researcher |", "Other |"), CONFIG)
    rejects(parse_manuscript, source.replace("**WuJun Chen**", "**Other**"), CONFIG)


def test_section_and_proof_contract() -> None:
    normalized = normalize_body(BODY)
    assert "# Introduction" in normalized and "# Result" in normalized
    assert "**Lemma 1.1. Statement**" in normalized
    assert ("\\appendix\n\\renewcommand{\\thesection}{Appendix \\Alph{section}}"
            "\n\n# Details") in normalized
    assert "## References" not in normalized
    rejects(normalize_body, BODY.replace("## 2. Result", "## 3. Result"))
    rejects(normalize_body, BODY.replace("## Appendix A. Details", "## Appendix B. Details"))
    rejects(normalize_body, BODY.replace(r"$\square$", ""))
    rejects(normalize_body, BODY.replace("## References", "## References\n\nManual entry"))


def test_equations_and_template() -> None:
    assert tagged_equations(r"\[x=1\tag{1}\]") == r"\begin{equation}x=1\tag{1}\end{equation}"
    assert tagged_equations(r"\[x=1\]") == r"\[x=1\]"
    assert template_fields("@@TITLE@@", {"TITLE": "Example"}) == "Example"
    rejects(template_fields, "@@TITLE@@ @@TITLE@@", {"TITLE": "Example"})
    statement = r"\Needspace{5\baselineskip}" + "\n" + r"\noindent\textbf{Lemma 1.1. Statement}"
    assert r"\Needspace{9\baselineskip}" in keep_statements(
        statement, {"Lemma 1.1. Statement": 9})
    rejects(keep_statements, statement, {"Lemma 1.2. Missing": 9})


def test_configuration_contract() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "hal-reader.json"
        path.write_text(json.dumps(CONFIG), encoding="utf-8")
        assert read_config(path) == CONFIG
        for key, value in (("pdf_name", "../reader.pdf"),
                           ("source_date_epoch", "yesterday"),
                           ("author", "")):
            changed = {**CONFIG, key: value}
            path.write_text(json.dumps(changed), encoding="utf-8")
            rejects(read_config, path)
        path.write_text(json.dumps({**CONFIG, "statement_keep_lines": {"Lemma 1.1": 0}}), encoding="utf-8")
        rejects(read_config, path)


def test_prior_hal_sources_remain_admissible() -> None:
    legacy_config = {**CONFIG, "date": "2026"}
    for name in ("proper_arc_registered_summaries", "future_event_minimal_quotient"):
        source = (ROOT / "papers" / "unnumbered" / name / "MANUSCRIPT.md").read_text(encoding="utf-8")
        title, abstract, keywords, body = parse_manuscript(source, legacy_config)
        assert title and abstract and keywords
        normalized = normalize_body(body)
        assert "# Introduction" in normalized and "## References" not in normalized


if __name__ == "__main__":
    test_source_contract()
    test_section_and_proof_contract()
    test_equations_and_template()
    test_configuration_contract()
    test_prior_hal_sources_remain_admissible()
    print("PASS shared HAL reader profile")
