"""
Prepare arXiv submission directories from built *_arxiv.tex files.

Usage:
  python prepare_arxiv.py              # public release documents
  python prepare_arxiv.py paper3       # single document

Output:
  output/arxiv/
    paper1/
      paper1_arxiv.tex
      paper1_arxiv.bbl
      ccs_arxiv.aux, paper1_arxiv.aux, paper2_arxiv.aux, paper3_arxiv.aux
      figures/
      xr_sources/

Each arXiv package is self-contained for the retained xr workflow:
  - figure paths are rewritten from ../../figures/<target>/ to figures/
  - \\externaldocument lines are preserved
  - all built *_arxiv.aux files are copied into the package root
  - companion *_arxiv.tex files are copied into xr_sources/ for traceability
  - no .sty or .cls files are bundled

Why companion TeX files are not placed at package root:
  arXiv may try to infer the main TeX file. Keeping non-root documents under
  xr_sources/ avoids ambiguity while still making the cross-document context
  available in the upload package.
"""

import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))
BUILD_DIR = os.path.abspath(
    os.environ.get("RIME_TEX_OUTPUT_DIR", os.path.join(ROOT, "output", "tex"))
)
FIGURES_DIR = os.path.join(ROOT, "figures")
OUT_DIR = os.path.abspath(
    os.environ.get("RIME_ARXIV_OUTPUT_DIR", os.path.join(ROOT, "output", "arxiv"))
)

TARGETS = {
    "paper1": "paper1_arxiv",
    "paper2": "paper2_arxiv",
    "paper3": "paper3_arxiv",
    "ccs": "ccs_arxiv",
}


def _collect_figures(tex_path):
    """Parse \\includegraphics{...} references and return unique basenames."""
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    figs = []
    for m in re.finditer(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", content):
        basename = os.path.basename(m.group(1))
        if basename not in figs:
            figs.append(basename)
    return figs


def _rewrite_figure_paths(tex_content, name):
    """Rewrite built-tree figure paths to package-local figures/ paths."""
    return re.sub(
        r"(\\includegraphics(?:\[.*?\])?\{)\.\./\.\./figures/" + re.escape(name) + r"/",
        r"\1figures/",
        tex_content,
    )


def _copy_figures(name, tex_src, figs_dir):
    fig_names = _collect_figures(tex_src)
    fig_src_dir = os.path.join(FIGURES_DIR, name)

    copied = 0
    for fn in fig_names:
        src = os.path.join(fig_src_dir, fn)
        dst = os.path.join(figs_dir, fn)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"  WARNING: figure not found: {src}")

    print(f"  figures: {copied}/{len(fig_names)} copied")
    return copied == len(fig_names)


def _copy_xr_aux_files(paper_dir):
    """Copy all built aux files into the package root for \\externaldocument."""
    copied = 0
    for tex_name in TARGETS.values():
        aux_src = os.path.join(BUILD_DIR, f"{tex_name}.aux")
        aux_dst = os.path.join(paper_dir, f"{tex_name}.aux")
        if os.path.exists(aux_src):
            shutil.copy2(aux_src, aux_dst)
            copied += 1
        else:
            print(f"  WARNING: aux not found: {aux_src}")

    print(f"  xr aux: {copied}/{len(TARGETS)} copied")
    return copied == len(TARGETS)


def _copy_xr_sources(paper_dir, main_tex_name):
    """Copy non-root companion TeX files for audit/debugging."""
    xr_src_dir = os.path.join(paper_dir, "xr_sources")
    os.makedirs(xr_src_dir, exist_ok=True)

    copied = 0
    expected = len(TARGETS) - 1
    for tex_name in TARGETS.values():
        if tex_name == main_tex_name:
            continue
        tex_src = os.path.join(BUILD_DIR, f"{tex_name}.tex")
        tex_dst = os.path.join(xr_src_dir, f"{tex_name}.tex")
        if os.path.exists(tex_src):
            shutil.copy2(tex_src, tex_dst)
            copied += 1
        else:
            print(f"  WARNING: companion tex not found: {tex_src}")

    print(f"  xr sources: {copied}/{expected} copied -> xr_sources/")
    return copied == expected


def _fresh_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def prepare(name):
    tex_name = TARGETS[name]
    tex_src = os.path.join(BUILD_DIR, f"{tex_name}.tex")
    bbl_src = os.path.join(BUILD_DIR, f"{tex_name}.bbl")

    if not os.path.exists(tex_src):
        print(f"  .tex not found: {tex_src}")
        print(f"  Run `python build.py {name}` first.")
        return False
    if not os.path.exists(bbl_src):
        print(f"  .bbl not found: {bbl_src}")
        print(f"  Run `python build.py {name}` first.")
        return False

    print(f"\n{'=' * 60}\nPreparing {name}...")

    paper_dir = os.path.join(OUT_DIR, name)
    figs_dir = os.path.join(paper_dir, "figures")
    _fresh_dir(paper_dir)
    os.makedirs(figs_dir, exist_ok=True)

    ok = True
    ok = _copy_figures(name, tex_src, figs_dir) and ok

    with open(tex_src, "r", encoding="utf-8") as f:
        tex_content = f.read()
    tex_content = _rewrite_figure_paths(tex_content, name)

    tex_dst = os.path.join(paper_dir, f"{tex_name}.tex")
    with open(tex_dst, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"  .tex: {tex_dst} ({len(tex_content)} bytes)")

    bbl_dst = os.path.join(paper_dir, f"{tex_name}.bbl")
    shutil.copy2(bbl_src, bbl_dst)
    print(f"  .bbl: {bbl_dst} ({os.path.getsize(bbl_dst)} bytes)")

    ok = _copy_xr_aux_files(paper_dir) and ok
    ok = _copy_xr_sources(paper_dir, tex_name) and ok

    print(f"  -> {paper_dir} ready")
    return ok


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a in TARGETS]
    if not args:
        args = list(TARGETS.keys())

    ok = True
    for name in args:
        if not prepare(name):
            ok = False

    if ok:
        print(f"\nDone: {len(args)} prepared -> {OUT_DIR}/")
    else:
        print("\nSome targets failed; run `python build.py all` first.")
        sys.exit(1)
