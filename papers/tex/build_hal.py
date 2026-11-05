#!/usr/bin/env python3
"""Build an unnumbered HAL reader PDF with the shared layout profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path(__file__).with_name("hal-reader-template.tex")
REQUIRED_CONFIG = {"author", "affiliation", "date", "pdf_name", "source_date_epoch"}
OPTIONAL_CONFIG = {"header_file", "statement_keep_lines"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_config(path: Path) -> dict[str, object]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - (REQUIRED_CONFIG | OPTIONAL_CONFIG):
        raise ValueError("unknown HAL reader configuration fields")
    if REQUIRED_CONFIG - set(config):
        raise ValueError("missing HAL reader configuration fields")
    if any(not isinstance(config[key], str) or not config[key].strip() for key in REQUIRED_CONFIG):
        raise ValueError("required HAL reader configuration values must be nonempty strings")
    if "header_file" in config and (not isinstance(config["header_file"], str)
                                    or not config["header_file"].strip()):
        raise ValueError("header_file must be a nonempty string")
    if "statement_keep_lines" in config:
        keeps = config["statement_keep_lines"]
        if (not isinstance(keeps, dict) or any(
            not isinstance(heading, str) or not heading.strip()
            or not isinstance(lines, int) or isinstance(lines, bool)
            or not 6 <= lines <= 30
            for heading, lines in keeps.items()
        )):
            raise ValueError("statement_keep_lines must map headings to 6..30 lines")
    if not re.fullmatch(r"[1-9][0-9]*", config["source_date_epoch"]):
        raise ValueError("source_date_epoch must be a positive Unix timestamp")
    if Path(config["pdf_name"]).name != config["pdf_name"] or not config["pdf_name"].endswith(".pdf"):
        raise ValueError("pdf_name must be a PDF filename")
    return config


def parse_manuscript(source: str, config: dict[str, object]) -> tuple[str, str, str, str]:
    match = re.fullmatch(
        r"# (?P<title>[^\n]+)\n\n\*\*(?P<author>[^\n]+)\*\*\n\n"
        r"(?P<byline>[^\n]+)\n\n## Abstract\n\n(?P<abstract>.*?)\n\n"
        r"\*\*Keywords:\*\* (?P<keywords>.*?)\n\n(?P<body>## 1\. Introduction.*)",
        source.strip(), flags=re.DOTALL,
    )
    if match is None:
        raise ValueError("manuscript must have a title, byline, abstract, keywords, and Introduction")
    if match["author"] != config["author"]:
        raise ValueError("author differs between manuscript and HAL configuration")
    if match["byline"] != f"{config['affiliation']} | {config['date']}":
        raise ValueError("affiliation/date differs between manuscript and HAL configuration")
    return match["title"], match["abstract"], match["keywords"], match["body"]


def normalize_body(body: str) -> str:
    parts = re.split(r"(?m)^## References\s*$", body)
    if len(parts) != 2 or parts[1].strip():
        raise ValueError("expected one trailing References heading without manual entries")
    body = parts[0].rstrip()
    numbers = [int(value) for value in re.findall(r"(?m)^## (\d+)\. ", body)]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("main section numbers must be consecutive from 1")
    if body.count("**Proof.**") != body.count(r"$\square$"):
        raise ValueError("proof starts and end markers do not match")
    body = re.sub(r"(?m)^## \d+\. (.+)$", r"# \1", body)
    appendices = re.findall(r"(?m)^## Appendix ([A-Z])\. ", body)
    if appendices != [chr(ord("A") + index) for index in range(len(appendices))]:
        raise ValueError("appendix letters must be consecutive from A")

    def appendix_heading(match: re.Match[str]) -> str:
        setup = ("\\appendix\n"
                 "\\renewcommand{\\thesection}{Appendix \\Alph{section}}\n\n"
                 if match[1] == "A" else "")
        return setup + "# " + match[2]

    body = re.sub(r"(?m)^## Appendix ([A-Z])\. (.+)$", appendix_heading, body)
    body = re.sub(
        r"(?m)^### ((?:Lemma|Proposition|Corollary|Theorem|Definition|Remark|Example) [^\n]+)$",
        r"**\1**", body,
    )
    return body


def run(command: list[str], *, cwd: Path, epoch: str) -> str:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = epoch
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=environment)
    if result.returncode:
        raise RuntimeError(result.stdout[-8000:] + "\n" + result.stderr[-2000:])
    return result.stdout + result.stderr


def pandoc_fragment(source: str, path: Path, *, epoch: str) -> str:
    path.write_text(source + "\n", encoding="utf-8", newline="\n")
    result = run(["pandoc", str(path), "--from=markdown+tex_math_single_backslash",
                  "--to=latex", "--natbib", "--wrap=none"], cwd=path.parent, epoch=epoch)
    if "[WARNING]" in result:
        raise RuntimeError(result)
    return result.strip()


def tagged_equations(latex: str) -> str:
    return re.sub(
        r"(?s)\\\[(.*?)\\\]",
        lambda match: "\\begin{equation}" + match[1] + "\\end{equation}"
        if r"\tag" in match[1] else match[0],
        latex,
    )


def keep_statements(latex: str, overrides: dict[str, int]) -> str:
    for heading, lines in overrides.items():
        marker = "\\Needspace{5\\baselineskip}\n\\noindent\\textbf{" + heading + "}"
        if latex.count(marker) != 1:
            raise ValueError(f"missing or ambiguous statement layout anchor: {heading}")
        latex = latex.replace(marker, f"\\Needspace{{{lines}\\baselineskip}}\n"
                              "\\noindent\\textbf{" + heading + "}", 1)
    return latex


def template_fields(template: str, fields: dict[str, str]) -> str:
    for name, value in fields.items():
        marker = f"@@{name}@@"
        if template.count(marker) != 1:
            raise ValueError(f"template marker missing or duplicated: {marker}")
        template = template.replace(marker, value)
    if re.search(r"@@[A-Z_]+@@", template):
        raise ValueError("unfilled HAL reader template marker")
    return template


def build(config_path: Path, output_override: Path | None = None) -> Path:
    config_path = config_path.resolve()
    paper = config_path.parent
    if not paper.is_relative_to(ROOT / "papers" / "unnumbered"):
        raise ValueError("HAL reader configuration must be under papers/unnumbered")
    config = read_config(config_path)
    source = paper / "MANUSCRIPT.md"
    bibliography = paper / "references.bib"
    title, abstract, keywords, body = parse_manuscript(source.read_text(encoding="utf-8"), config)
    work = ROOT / "output" / "tex" / paper.name / "hal"
    work.mkdir(parents=True, exist_ok=True)
    epoch = config["source_date_epoch"]
    abstract_latex = pandoc_fragment(abstract, work / "abstract.md", epoch=epoch)
    keywords_latex = pandoc_fragment(re.sub(r"\s*;\s*", ", ", " ".join(keywords.split())),
                                     work / "keywords.md", epoch=epoch)
    body_latex = tagged_equations(pandoc_fragment(normalize_body(body), work / "body.md", epoch=epoch))
    body_latex = body_latex.replace(r"\textbf{Proof.}", "\\begin{proof}\n")
    body_latex = body_latex.replace(r"\(\square\)", "\n\\end{proof}")
    body_latex = re.sub(
        r"(?m)^\\textbf\{(Lemma|Proposition|Corollary|Theorem|Definition|Remark|Example) ",
        lambda match: "\\par\\smallskip\n\\Needspace{5\\baselineskip}\n"
        "\\noindent\\textbf{" + match[1] + " ",
        body_latex,
    )
    body_latex = keep_statements(body_latex, config.get("statement_keep_lines", {}))
    body_latex = re.sub(
        r"(?m)^\\section\{",
        lambda _: "\\Needspace{7\\baselineskip}\n\\section{",
        body_latex,
    )
    header = ""
    if "header_file" in config:
        header_path = (paper / config["header_file"]).resolve()
        if not header_path.is_relative_to(paper) or not header_path.is_file():
            raise ValueError("header_file must name a file inside the manuscript directory")
        header = header_path.read_text(encoding="utf-8")
    tex = template_fields(TEMPLATE.read_text(encoding="utf-8"), {
        "HEADER_INCLUDES": header,
        "PDF_TITLE": title,
        "PDF_AUTHOR": config["author"],
        "TITLE": title,
        "AUTHOR": config["author"],
        "AFFILIATION": config["affiliation"],
        "DATE": config["date"],
        "ABSTRACT": abstract_latex,
        "KEYWORDS": keywords_latex,
        "BODY": body_latex,
    })
    stem = Path(config["pdf_name"]).stem
    target = work / f"{stem}.tex"
    target.write_text(tex, encoding="utf-8", newline="\n")
    shutil.copyfile(bibliography, work / "references.bib")
    for command in (["xelatex", "-interaction=nonstopmode", "-halt-on-error", target.name],
                    ["bibtex", stem],
                    ["xelatex", "-interaction=nonstopmode", "-halt-on-error", target.name],
                    ["xelatex", "-interaction=nonstopmode", "-halt-on-error", target.name]):
        run(command, cwd=work, epoch=epoch)
    log = target.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    bib_log = target.with_suffix(".blg").read_text(encoding="utf-8", errors="replace")
    overfull = [float(value) for value in re.findall(r"Overfull \\[hv]box \(([\d.]+)pt", log)]
    if (max(overfull, default=0) > 0.5 or "Missing character:" in log
            or re.search(r"(?:Citation|Reference) .+ undefined|There were undefined", log)
            or re.search(r"(?m)^Warning--", bib_log)):
        raise RuntimeError(f"reader layout/citation diagnostics failed; inspect {target.with_suffix('.log')}")
    output = (output_override or paper / "hal-v1" / config["pdf_name"]).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError("HAL reader output must remain inside the repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(target.with_suffix(".pdf"), output)
    preview = ROOT / "output" / "pdf" / config["pdf_name"]
    preview.parent.mkdir(parents=True, exist_ok=True)
    if output != preview:
        shutil.copyfile(output, preview)
    inputs = {"MANUSCRIPT.md": digest(source), "references.bib": digest(bibliography),
              "hal-reader.json": digest(config_path), "papers/tex/build_hal.py": digest(Path(__file__)),
              "papers/tex/hal-reader-template.tex": digest(TEMPLATE)}
    if "header_file" in config:
        inputs[config["header_file"]] = digest(paper / config["header_file"])
    receipt = {"status": "PASS_HAL_READER_BUILD", "stage": "HAL_V1_CANDIDATE",
               "inputs": inputs, "reader_pdf": output.relative_to(ROOT).as_posix(),
               "reader_pdf_sha256": digest(output), "max_overfull_pt": max(overfull, default=0),
               "undefined_citations": False, "missing_characters": False,
               "publication_identity": None}
    result_path = paper / "results" / "reader-build.hal-v1.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", type=Path, help="unnumbered manuscript directory")
    parser.add_argument("--output", type=Path, help="override PDF destination inside the repository")
    args = parser.parse_args()
    print(build(args.paper / "hal-reader.json", args.output))


if __name__ == "__main__":
    main()
