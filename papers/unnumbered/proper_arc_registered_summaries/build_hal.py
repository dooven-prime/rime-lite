#!/usr/bin/env python3
"""Build the HAL reader PDF from the canonical proper-arc manuscript."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "output" / "tex" / "proper_arc_registered_summaries" / "hal"
PDF = ROOT / "output" / "pdf" / "Chen_Registered_Proper_Arc_Summaries_HAL_preprint.pdf"
STEM = PDF.stem
SOURCE_DATE_EPOCH = "1793577600"  # 2026-11-02 UTC.


def latex(source: str, filename: str) -> str:
    output = WORK / filename
    result = subprocess.run(
        ["pandoc", "--from", "markdown+tex_math_single_backslash", "--to", "latex",
         "--natbib", "--wrap=none", "--output", str(output)],
        input=source, text=True, capture_output=True, encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return output.read_text(encoding="utf-8")


def body_latex(source: str, filename: str) -> str:
    converted = latex(source, filename)
    converted = re.sub(
        r"(?s)\\\[(.*?)\\\]",
        lambda match: "\\begin{equation}" + match.group(1) + "\\end{equation}"
        if r"\tag" in match.group(1) else match.group(0),
        converted,
    )
    converted = converted.replace(r"\textbf{Proof.}", "\\begin{proof}\n")
    converted = converted.replace(r"\(\square\)", "\n\\end{proof}")
    converted = re.sub(
        r"(?m)^\\textbf\{(Lemma|Proposition|Corollary|Theorem) ",
        lambda match: "\\Needspace{5\\baselineskip}\n\\noindent\\textbf{" + match.group(1) + " ",
        converted,
    )
    return converted


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
    main_md = "## 1. Introduction\n" + source.split("## 1. Introduction\n", 1)[1]
    main_md = main_md.split("## References\n", 1)[0]
    main_md = re.sub(r"(?m)^## \d+\. ", "# ", main_md)

    WORK.mkdir(parents=True, exist_ok=True)
    abstract = latex(abstract_md, "abstract.tex")
    body = body_latex(main_md, "body.tex")
    shutil.copyfile(HERE / "references.bib", WORK / "references.bib")

    front = rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage[a4paper,margin=25mm]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage{{amsmath,amssymb,amsthm,mathtools}}
\usepackage[round]{{natbib}}
\usepackage{{booktabs,longtable,tabularx,array,enumitem,needspace,xurl,microtype}}
\usepackage[hidelinks,hypertexnames=false]{{hyperref}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\hypersetup{{pdftitle={{{title}}},pdfauthor={{WuJun Chen}}}}
\title{{{title}}}
\author{{WuJun Chen\\Independent Researcher}}
\date{{Preprint, November 2026}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract}
\end{{abstract}}
\noindent\textbf{{Keywords:}} {keywords.replace('; ', ', ')}

"""
    target = WORK / f"{STEM}.tex"
    target.write_text(
        front + body + "\n\\Needspace{6\\baselineskip}\n"
        + "\\bibliographystyle{plainnat}\n\\bibliography{references}\n"
        + "\\end{document}\n",
        encoding="utf-8", newline="\n",
    )
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    run(["bibtex", target.stem])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", target.name])
    log = target.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    bib_log = target.with_suffix(".blg").read_text(encoding="utf-8", errors="replace")
    if re.search(
        r"undefined references|Citation .* undefined|Reference .* undefined|"
        r"Overfull \\hbox|destination with the same identifier|^!",
        log, flags=re.MULTILINE,
    ) or re.search(r"(?m)^Warning--", bib_log):
        raise RuntimeError(f"unresolved LaTeX diagnostic: {target.with_suffix('.log')}")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(target.with_suffix(".pdf"), PDF)
    print(f"HAL reader PDF: {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
