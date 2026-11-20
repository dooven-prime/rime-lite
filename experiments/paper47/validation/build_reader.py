"""Build the Paper XLVII reader with the numbered-paper TeX pipeline."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys


PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "papers/tex"))
import _build as builder
import _clean_hrule
import _postprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numbered_reader_layout(tex, margin_mm):
    original = r"\usepackage[a4paper,margin=1in]{geometry}"
    if tex.count(original) != 1:
        raise ValueError("numbered-paper geometry setting changed")
    return tex.replace(original, rf"\usepackage[a4paper,margin={margin_mm}mm]{{geometry}}")


def main():
    paper = ROOT / "papers/paper47"
    config_path = PACKAGE / "reader-profile.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source = paper / "Paper XLVII.md"
    bib = paper / "references-v1.bib"
    work = ROOT / "output/tex/paper47-reader"
    work.mkdir(parents=True, exist_ok=True)
    os.environ["SOURCE_DATE_EPOCH"] = str(config["source_date_epoch"])

    builder.configure_output_dir(str(work))
    if not builder.discover_paper("paper47"):
        raise ValueError("expected one canonical Paper XLVII manuscript")
    target = builder.PAPERS["paper47"]
    if not builder.run_pandoc(target["md"], target["tex"]):
        raise ValueError("Pandoc conversion failed")
    builder.postprocess(target["tex"], target["arxiv"], target["title"])
    tex_path = Path(target["arxiv"])
    tex = numbered_reader_layout(tex_path.read_text(encoding="utf-8"), config["margin_mm"])
    if (tex.count(r"\begin{proof}") != 24 or tex.count(r"\end{proof}") != 24
            or r"Lemma~\ref{lem:7-1}" not in tex
            or r"Theorem~\ref{thm:7-2}" not in tex
            or r"\section{Displacement-sensitive terminal routing}" not in tex
            or r"\renewcommand{\thetheorem}{\Alph{section}.\arabic{theorem}}" not in tex
            or r"\href{https://github.com/dooven-prime/rime-lite}{RIME Lite repository}" not in tex):
        raise ValueError("proof or hyperlink conversion differs from the manuscript")
    tex_path.write_text(tex, encoding="utf-8", newline="\n")
    if not builder.compile_pdf(str(tex_path)):
        raise ValueError("XeLaTeX or BibTeX build failed")

    log = tex_path.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    blg = tex_path.with_suffix(".blg").read_text(encoding="utf-8", errors="replace")
    overfull = [float(v) for v in re.findall(r"Overfull \\[hv]box \(([\d.]+)pt", log)]
    if (max(overfull, default=0) > 0.5 or "Missing character:" in log
            or re.search(r"(?:Citation|Reference) .+ undefined|There were undefined", log)
            or re.search(r"(?m)^Warning--", blg)):
        raise ValueError(f"reader diagnostics failed: {tex_path.with_suffix('.log')}")

    output = paper / config["pdf_name"]
    shutil.copyfile(tex_path.with_suffix(".pdf"), output)
    inputs = [source, bib, config_path, Path(__file__), Path(builder.__file__),
              Path(_postprocess.__file__), Path(_clean_hrule.__file__)]
    receipt = {
        "status": "LOCAL_READER_BUILD_PASS", "publication_identity": None,
        "inputs": {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
        "reader_pdf": output.relative_to(ROOT).as_posix(), "reader_pdf_sha256": digest(output),
        "max_overfull_pt": max(overfull, default=0),
        "undefined_citations": False, "missing_characters": False,
        "profile": "Numbered-paper TeX pipeline with 22 mm paper-local margins",
    }
    (PACKAGE / "results").mkdir(exist_ok=True)
    (PACKAGE / "results/reader-build.v1.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
