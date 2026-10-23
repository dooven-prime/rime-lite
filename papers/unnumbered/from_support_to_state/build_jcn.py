#!/usr/bin/env python3
"""Build a JCN-sized reader PDF from the local journal manuscript."""

from pathlib import Path
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = ROOT / "output" / "tex" / "from_support_to_state" / "jcn"
PDF = ROOT / "output" / "pdf" / "Chen_A_Path_Is_Not_a_State_JCN_reader.pdf"
SUPPDF = ROOT / "output" / "pdf" / "Chen_A_Path_Is_Not_a_State_JCN_supplement.pdf"
sys.path.insert(0, str(ROOT / "papers" / "tex"))

from _build import compile_pdf, postprocess, run_pandoc  # noqa: E402


def between(source: str, first: str, last: str) -> str:
    if source.count(first) != 1 or source.count(last) != 1:
        raise RuntimeError(f"Expected one occurrence each of {first!r} and {last!r}")
    return source.split(first, 1)[1].split(last, 1)[0].strip()


def separate_results(body: str) -> str:
    cutoffs = {
        "prop:nonnegative-relay-criterion": "This criterion is restricted",
        "lem:fiber-criterion": "For one retained lag",
        "prop:verified-image-escape": "An escape certificate concerns",
        "thm:unit-state-profile-characterization": None,
    }
    seen: set[str] = set()
    pattern = re.compile(
        r"(?P<opening>\\begin\{(?P<kind>proposition|lemma|theorem)\}"
        r"(?:\[[^\n]*\])?\s*\\label\{(?P<label>[^}]+)\}\s*)"
        r"(?P<statement>.*?)\\begin\{proof\}(?P<proof>.*?)"
        r"\\end\{proof\}\s*\\end\{(?P=kind)\}",
        re.S,
    )

    def split(match: re.Match[str]) -> str:
        label = match.group("label")
        if label not in cutoffs:
            raise RuntimeError(f"Unexpected result with proof: {label}")
        seen.add(label)
        proof = match.group("proof")
        trailing = ""
        marker = cutoffs[label]
        if marker:
            if proof.count(marker) != 1:
                raise RuntimeError(f"Missing proof boundary: {label}")
            proof, trailing = proof.split(marker, 1)
            trailing = marker + trailing
        kind = match.group("kind")
        return (
            match.group("opening") + match.group("statement").rstrip()
            + f"\n\\end{{{kind}}}\n\n\\begin{{proof}}"
            + proof.rstrip() + "\n\\end{proof}\n\n" + trailing.strip() + "\n"
        )

    body = pattern.sub(split, body)
    if seen != set(cutoffs):
        raise RuntimeError(f"Proof boundaries changed: {seen}")
    corollary = re.search(r"\\begin\{corollary\}.*?\\end\{corollary\}", body, re.S)
    if corollary is None:
        raise RuntimeError("Missing compact-profile corollary")
    content = corollary.group(0)
    marker = "The sums in this certificate"
    if content.count(marker) != 1:
        raise RuntimeError("Corollary boundary changed")
    statement, trailing = content.split(marker, 1)
    statement = statement.removesuffix(r"\end{corollary}").rstrip()
    body = body[:corollary.start()] + statement + "\n\\end{corollary}\n\n" \
        + marker + trailing.removesuffix(r"\end{corollary}") + body[corollary.end():]
    return body


def merge_figure_captions(body: str) -> str:
    for title in ("Predictive profile multiplicity", "Coordinate-specific profile splitting"):
        figure_start = body.index(r"\begin{figure}")
        while title not in body[figure_start:body.index(r"\end{figure}", figure_start)]:
            figure_start = body.index(r"\begin{figure}", figure_start + 1)
        figure_end = body.index(r"\end{figure}", figure_start) + len(r"\end{figure}")
        label = rf"\caption{{\textbf{{Figure \thefigure.}} {title}}}"
        if body[figure_start:figure_end].count(label) != 1:
            raise RuntimeError(f"Unexpected figure caption: {title}")
        marker = rf"\textbf{{{title}.}} "
        description_start = body.index(marker, figure_end)
        description_end = body.index("\n\n", description_start)
        description = body[description_start + len(marker):description_end].strip()
        alt_start = body.index("Alt text:", description_end)
        if body[description_end:alt_start].strip():
            raise RuntimeError(f"Alt text is not directly below the legend: {title}")
        alt_end = body.index("\n\n", alt_start)
        alt = body[alt_start + len("Alt text:"):alt_end].strip()
        if not alt:
            raise RuntimeError(f"Empty figure alt text: {title}")
        figure = body[figure_start:figure_end].replace(
            label, rf"\caption{{\textbf{{Figure \thefigure.}} {title}. {description}}}"
        ).replace(
            r"\end{figure}",
            rf"\caption*{{\footnotesize\textit{{Alt text:}} {alt}}}" + "\n" + r"\end{figure}",
        )
        body = body[:figure_start] + figure + body[figure_end:description_start] \
            + body[alt_end:]
    return body


def main() -> int:
    source = (HERE / "MANUSCRIPT.md").read_text(encoding="utf-8")
    lines = source.splitlines()
    title = lines[0].removeprefix("# ").strip()
    subtitle = lines[1].removeprefix("### ").strip()
    if not title or not subtitle or len(lines) < 3:
        raise RuntimeError("Expected manuscript title and subtitle")

    BUILD.mkdir(parents=True, exist_ok=True)
    cleaned = re.sub(
        r"^(#{2,4})\s+\d+(?:\.\d+)*\.?\s+",
        r"\1 ",
        source,
        flags=re.MULTILINE,
    ).replace(
        "## Appendix A. Noninjectivity and the Drive-Off Boundary",
        "## Appendix A: Noninjectivity and Drive-Off",
    )
    build_md = BUILD / "manuscript-build.md"
    build_md.write_text(cleaned, encoding="utf-8", newline="\n")
    raw_tex = BUILD / "manuscript-raw.tex"
    converted_tex = BUILD / "manuscript-converted.tex"
    if not run_pandoc(str(build_md), str(raw_tex)):
        return 1
    postprocess(str(raw_tex), str(converted_tex), title)
    converted = converted_tex.read_text(encoding="utf-8")

    abstract = between(converted, r"\section*{Abstract}", r"\textbf{Keywords:}")
    keywords = between(converted, r"\textbf{Keywords:}", r"\section{Introduction}")
    body = r"\section{Introduction}" + "\n" + between(
        converted, r"\section{Introduction}", r"\bibliography{"
    )
    body = separate_results(body)
    body = merge_figure_captions(body)
    table_titles = re.findall(r"\\textbf\{Table (\d+)\.", body)
    if table_titles != [str(n) for n in range(1, 6)]:
        raise RuntimeError(f"Expected five sequential table titles: {table_titles}")
    body = re.sub(
        r"(?=\\textbf\{Table \d+\.)",
        r"\\Needspace{7\\baselineskip}\\noindent ",
        body,
    )
    body = body.replace(r"\section{Funding}", r"\section*{Funding}")
    body = body.replace(r"\section{Acknowledgements}", r"\section*{Acknowledgements}")
    body = body.replace("figures/profile_multiplicity.pdf", "figures/profile_multiplicity.png")
    body = body.replace("figures/coordinate_profile_splits.pdf", "figures/coordinate_profile_splits.png")
    body = body.replace(r"\[", r"\begin{equation}").replace(r"\]", r"\end{equation}")

    figures = BUILD / "figures"
    figures.mkdir(exist_ok=True)
    for name in ("profile_multiplicity.png", "coordinate_profile_splits.png"):
        shutil.copyfile(HERE / "figures" / name, figures / name)
    shutil.copyfile(HERE / "references.bib", BUILD / "references.bib")

    preamble = rf"""\documentclass[11pt]{{article}}
\usepackage[paperwidth=176mm,paperheight=250mm,textwidth=126mm,textheight=195mm,centering]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{microtype}}
\usepackage{{needspace}}
\usepackage{{amsmath,amssymb,amsthm,mathtools}}
\usepackage{{graphicx,float,booktabs,longtable,tabularx,array}}
\usepackage[font=small,labelfont=bf]{{caption}}
\usepackage[section]{{placeins}}
\usepackage[numbers,sort&compress]{{natbib}}
\usepackage[hidelinks]{{hyperref}}
\providecommand{{\doi}}[1]{{\href{{https://doi.org/#1}}{{doi:#1}}}}
\captionsetup{{labelformat=empty}}
\setlength{{\parindent}}{{1.5em}}
\setlength{{\parskip}}{{0pt}}
\emergencystretch=2em
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\theoremstyle{{plain}}
\newtheorem{{theorem}}{{Theorem}}[section]
\newtheorem{{lemma}}[theorem]{{Lemma}}
\newtheorem{{proposition}}[theorem]{{Proposition}}
\newtheorem{{corollary}}[theorem]{{Corollary}}
\theoremstyle{{definition}}
\newtheorem{{definition}}[theorem]{{Definition}}
\theoremstyle{{remark}}
\newtheorem{{remark}}[theorem]{{Remark}}
\newtheorem{{example}}[theorem]{{Example}}
\hypersetup{{pdftitle={{{title}: {subtitle}}},pdfauthor={{WuJun Chen}}}}
\title{{\bfseries {title}\\[0.45em]\large {subtitle}}}
\author{{WuJun Chen\\\small Independent Researcher, Ningbo, China\\
  \small\href{{https://orcid.org/0009-0007-9561-2892}}{{ORCID: 0009-0007-9561-2892}}\\
  \small\texttt{{dooven@outlook.com}}}}
\date{{}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract}
\end{{abstract}}
\noindent\textbf{{Keywords:}} {keywords}
\medskip

"""
    tex = BUILD / "jcn_reader.tex"
    tex.write_text(
        preamble + body + "\n\n\\bibliographystyle{unsrtnat}\n"
        "\\bibliography{references}\n\\end{document}\n",
        encoding="utf-8",
        newline="\n",
    )
    if not compile_pdf(str(tex)):
        return 1

    log = tex.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    bbl = tex.with_suffix(".bbl")
    if not bbl.is_file() or r"\bibitem" not in bbl.read_text(encoding="utf-8"):
        raise RuntimeError("BibTeX did not produce a bibliography")
    if re.search(r"Citation .* undefined|There were undefined citations", log):
        raise RuntimeError("Unresolved citations")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(tex.with_suffix(".pdf"), PDF)
    subprocess.run(
        [
            "pandoc", str(HERE / "SUPPLEMENTARY_INFORMATION.md"),
            "--from=markdown+tex_math_single_backslash",
            "--pdf-engine=xelatex", "--standalone", "-V", "fontsize:11pt",
            "-V", "geometry:paperwidth=176mm", "-V", "geometry:paperheight=250mm",
            "-V", "geometry:textwidth=126mm", "-V", "geometry:textheight=195mm",
            "-V", "geometry:centering", "-o", str(SUPPDF),
        ],
        cwd=HERE,
        check=True,
    )
    print(f"Overfull boxes: {len(re.findall('Overfull', log))}")
    print(f"Reader PDF: {PDF}")
    print(f"Supplement PDF: {SUPPDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
