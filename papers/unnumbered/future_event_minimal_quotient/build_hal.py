#!/usr/bin/env python3
"""Build the neutral HAL reader PDF from the canonical Markdown source."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "output" / "tex" / "future_event_minimal_quotient" / "hal"
PDF = ROOT / "output" / "pdf" / "Chen_Future_Event_Minimal_Quotients_HAL_preprint.pdf"
STEM = "Chen_Future_Event_Minimal_Quotients_HAL_preprint"
SOURCE_DATE_EPOCH = "1793232000"  # 2026-10-29 UTC, for byte-stable PDF metadata.


def pandoc_latex(source: str, output: Path) -> str:
    result = subprocess.run(
        ["pandoc", "--from", "markdown+tex_math_single_backslash", "--to", "latex",
         "--natbib", "--wrap=none", "--output", str(output)],
        input=source, text=True, capture_output=True, encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return output.read_text(encoding="utf-8")


def body_markdown(source: str) -> str:
    body = "## 1. Introduction\n" + source.split("## 1. Introduction\n", 1)[1]
    body = body.split("## References", 1)[0]
    body = re.sub(r"(?m)^## \d+\. ", "# ", body)
    return body


def run(command: list[str]) -> None:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    result = subprocess.run(
        command, cwd=WORK, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=environment,
    )
    if result.returncode:
        raise RuntimeError(result.stdout[-9000:] + "\n" + result.stderr[-2000:])


def main() -> int:
    for executable in ("pandoc", "pdflatex", "bibtex"):
        if not shutil.which(executable):
            raise RuntimeError(f"missing build dependency: {executable}")
    source = (HERE / "MANUSCRIPT.md").read_text(encoding="utf-8")
    title = source.splitlines()[0].removeprefix("# ")
    abstract_md = source.split("## Abstract\n", 1)[1].split("**Keywords:**", 1)[0].strip()
    keywords = source.split("**Keywords:**", 1)[1].split("## 1. Introduction", 1)[0].strip()
    WORK.mkdir(parents=True, exist_ok=True)
    abstract = pandoc_latex(abstract_md, WORK / "abstract.tex")
    body = pandoc_latex(body_markdown(source), WORK / "body.tex")
    body = re.sub(
        r"(?s)\\\[(.*?)\\\]",
        lambda match: "\\begin{equation}" + match.group(1) + "\\end{equation}"
        if r"\tag" in match.group(1) else match.group(0),
        body,
    )
    body = body.replace(r"\textbf{Proof.}", "\\begin{proof}\n")
    body = body.replace(r"\(\square\)", "\n\\end{proof}")
    body = re.sub(
        r"(?m)^\\textbf\{(Lemma|Proposition|Corollary|Theorem) ",
        lambda match: "\\Needspace{5\\baselineskip}\n\\noindent\\textbf{" + match.group(1) + " ",
        body,
    )
    # Keep each calculation with the sentence introducing it in the PDF.
    for anchor, lines in (
        (r"\tag{7.3}" + "\n" + r"\end{equation}", 10),
        (r"with \(C_3=0\).", 7),
    ):
        if body.count(anchor) != 1:
            raise RuntimeError(f"missing or ambiguous layout anchor: {anchor}")
        body = body.replace(anchor, anchor + f"\n\\Needspace{{{lines}\\baselineskip}}", 1)
    body = body.replace(
        r"\texttt{experiments/future\_event\_minimal\_quotient/}",
        r"\path{experiments/future_event_minimal_quotient/}",
    )
    shutil.copyfile(HERE / "references.bib", WORK / "references.bib")
    front = rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage[a4paper,margin=27mm]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{amsmath,amssymb,amsthm,mathtools}}
\usepackage[round]{{natbib}}
\usepackage{{booktabs,longtable,tabularx,array,enumitem,needspace,xurl,microtype}}
\usepackage[hidelinks]{{hyperref}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\hypersetup{{pdftitle={{{title}}},pdfauthor={{WuJun Chen}}}}
\title{{{title}}}
\author{{WuJun Chen\\Independent Researcher}}
\date{{Preprint, October 2026}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract}
\end{{abstract}}
\noindent\textbf{{Keywords:}} {keywords.replace('; ', ', ')}

"""
    target = WORK / f"{STEM}.tex"
    target.write_text(
        front + body + "\n"
        + r"\bibliographystyle{plainnat}" + "\n"
        + r"\bibliography{references}" + "\n" + r"\end{document}" + "\n",
        encoding="utf-8", newline="\n",
    )
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    run(["bibtex", target.stem])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    log = target.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    if re.search(
        r"undefined references|Citation .* undefined|Reference .* undefined|"
        r"Overfull \\hbox|^!", log, flags=re.MULTILINE,
    ):
        raise RuntimeError(f"unresolved LaTeX diagnostic: {target.with_suffix('.log')}")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(target.with_suffix(".pdf"), PDF)
    print(f"HAL reader PDF: {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
