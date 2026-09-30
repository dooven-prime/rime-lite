"""
Build pipeline: md → pandoc → tex → postprocess → _arxiv.tex → xelatex → _arxiv.pdf

Usage: python _build.py [--no-pdf] [--output-dir PATH] [paperN|ccs|all|extras|theorems]
"""
import argparse
import subprocess, shutil, os, sys, re, tempfile

from _clean_hrule import clean_hrules

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))  # project root
DEFAULT_OUTPUT_DIR = os.path.join(ROOT, 'output', 'tex')
OUTPUT_DIR = os.path.abspath(
    os.environ.get('RIME_TEX_OUTPUT_DIR', DEFAULT_OUTPUT_DIR)
)

# MiKTeX paths (not always on system PATH)
_MIKTEX_DIRS = [
    'D:/Program Files/MiKTeX/miktex/bin/x64',
    'C:/Program Files/MiKTeX/miktex/bin/x64',
]


def _find_exe(name):
    """Find executable, searching MiKTeX directories if needed."""
    path = shutil.which(name)
    if path:
        return path
    for d in _MIKTEX_DIRS:
        exe = os.path.join(d, name + '.exe')
        if os.path.isfile(exe):
            return exe
    return None


def _tex_env():
    """Return environment dict with MiKTeX on PATH."""
    env = os.environ.copy()
    path = env.get('PATH', '')
    for d in _MIKTEX_DIRS:
        if os.path.isdir(d) and d not in path:
            path = d + ';' + path
    env['PATH'] = path
    return env

PAPERS = {
    'paper1': {
        'md': f'{ROOT}/papers/paper1/Paper I.md',
        'tex': f'{OUTPUT_DIR}/paper1.tex',
        'arxiv': f'{OUTPUT_DIR}/paper1_arxiv.tex',
        'title': "Spectral Sector Decomposition in the Rubik's Cube Representation",
    },
    'paper2': {
        'md': f'{ROOT}/papers/paper2/Paper II.md',
        'tex': f'{OUTPUT_DIR}/paper2.tex',
        'arxiv': f'{OUTPUT_DIR}/paper2_arxiv.tex',
        'title': "Noncommutative Transport Topology in the Rubik's Cube Representation",
    },
    'paper3': {
        'md': f'{ROOT}/papers/paper3/Paper III.md',
        'tex': f'{OUTPUT_DIR}/paper3.tex',
        'arxiv': f'{OUTPUT_DIR}/paper3_arxiv.tex',
        'title': "Support-Graph Reachability and Matrix-Composition Obstructions",
    },
    'paper4': {
        'md': f'{ROOT}/papers/paper4/Paper IV.md',
        'tex': f'{OUTPUT_DIR}/paper4.tex',
        'arxiv': f'{OUTPUT_DIR}/paper4_arxiv.tex',
        'title': "Collision Geometry of Joint Spectra",
    },
    'paper5': {
        'md': f'{ROOT}/papers/paper5/Paper V.md',
        'tex': f'{OUTPUT_DIR}/paper5.tex',
        'arxiv': f'{OUTPUT_DIR}/paper5_arxiv.tex',
        'title': "Boolean Support Does Not Determine Commutator Accessibility",
    },
    'paper6': {
        'md': f'{ROOT}/papers/paper6/Paper VI.md',
        'tex': f'{OUTPUT_DIR}/paper6.tex',
        'arxiv': f'{OUTPUT_DIR}/paper6_arxiv.tex',
        'title': "Linearized Certificates and Normality-Gated Registrations for Weighted Generator Averages",
    },
    'paper7': {
        'md': f'{ROOT}/papers/paper7/Paper VII.md',
        'tex': f'{OUTPUT_DIR}/paper7.tex',
        'arxiv': f'{OUTPUT_DIR}/paper7_arxiv.tex',
        'title': "Incidence Geometry of Projected Operator Composition",
    },
    'paper8': {
        'md': f'{ROOT}/papers/paper8/Paper VIII.md',
        'tex': f'{OUTPUT_DIR}/paper8.tex',
        'arxiv': f'{OUTPUT_DIR}/paper8_arxiv.tex',
        'title': "Sectorized Observable Framework: A Typed Static Object Language with Exact Marked Finite Realizations",
    },
    'paper9': {
        'md': f'{ROOT}/papers/paper9/Paper IX.md',
        'tex': f'{OUTPUT_DIR}/paper9.tex',
        'arxiv': f'{OUTPUT_DIR}/paper9_arxiv.tex',
        'title': "Observable Dynamics of Sectorized Observable Frameworks: Typed Deformations, Observable Trajectories, and Wall Pullbacks",
    },
    'paper10': {
        'md': f'{ROOT}/papers/paper10/Paper X.md',
        'tex': f'{OUTPUT_DIR}/paper10.tex',
        'arxiv': f'{OUTPUT_DIR}/paper10_arxiv.tex',
        'title': "Capability-Aware Compilation for Sectorized Observable Frameworks: Typed Admission and Cross-Species Registry Evidence",
    },
    'paper11': {
        'md': f'{ROOT}/papers/paper11/Paper XI.md',
        'tex': f'{OUTPUT_DIR}/paper11.tex',
        'arxiv': f'{OUTPUT_DIR}/paper11_arxiv.tex',
        'title': "Typed Wall Morphology for Sectorized Observable Frameworks",
    },
    'paper12': {
        'md': f'{ROOT}/papers/paper12/Paper XII.md',
        'tex': f'{OUTPUT_DIR}/paper12.tex',
        'arxiv': f'{OUTPUT_DIR}/paper12_arxiv.tex',
        'title': "SOF Diagnostic Protocol",
    },
    'paper13': {
        'md': f'{ROOT}/papers/paper13/Paper XIII.md',
        'tex': f'{OUTPUT_DIR}/paper13.tex',
        'arxiv': f'{OUTPUT_DIR}/paper13_arxiv.tex',
        'title': "Typed Alignment and Audit Signatures",
    },
    'paper14': {
        'md': f'{ROOT}/papers/paper14/Paper XIV.md',
        'tex': f'{OUTPUT_DIR}/paper14.tex',
        'arxiv': f'{OUTPUT_DIR}/paper14_arxiv.tex',
        'title': "SOF Action Semantics",
    },
    'paper15': {
        'md': f'{ROOT}/papers/paper15/Paper XV.md',
        'tex': f'{OUTPUT_DIR}/paper15.tex',
        'arxiv': f'{OUTPUT_DIR}/paper15_arxiv.tex',
        'title': "Corrigible Structural Interfaces",
    },
    'paper16': {
        'md': f'{ROOT}/papers/paper16/Paper XVI.md',
        'tex': f'{OUTPUT_DIR}/paper16.tex',
        'arxiv': f'{OUTPUT_DIR}/paper16_arxiv.tex',
        'title': "From Support to State",
    },
    'paper17': {
        'md': f'{ROOT}/papers/paper17/Paper XVII.md',
        'tex': f'{OUTPUT_DIR}/paper17.tex',
        'arxiv': f'{OUTPUT_DIR}/paper17_arxiv.tex',
        'title': "Exact Post-Transient Coarse Factorization in a Reduced Male Drosophila CNS Model",
    },
    'paper20': {
        'md': f'{ROOT}/papers/paper20/Paper XX.md',
        'tex': f'{OUTPUT_DIR}/paper20.tex',
        'arxiv': f'{OUTPUT_DIR}/paper20_arxiv.tex',
        'title': "All-Depth Carrier Accessibility for Routed Composition",
    },
    'paper21': {
        'md': f'{ROOT}/papers/paper21/Paper XXI.md',
        'tex': f'{OUTPUT_DIR}/paper21.tex',
        'arxiv': f'{OUTPUT_DIR}/paper21_arxiv.tex',
        'title': "Uniform Finite-Field Route Profiles",
    },
    'paper22': {
        'md': f'{ROOT}/papers/paper22/Paper XXII.md',
        'tex': f'{OUTPUT_DIR}/paper22.tex',
        'arxiv': f'{OUTPUT_DIR}/paper22_arxiv.tex',
        'title': "Anchored Farey Classification and Catalan-Fibonacci Envelopes for Rational Defect Dynamics",
    },
    'paper23': {
        'md': f'{ROOT}/papers/paper23/Paper XXIII.md',
        'tex': f'{OUTPUT_DIR}/paper23.tex',
        'arxiv': f'{OUTPUT_DIR}/paper23_arxiv.tex',
        'title': "Kernel Corridors and Schreier Waiting in Synchronizing Automata",
    },
    'paper24': {
        'md': f'{ROOT}/papers/paper24/Paper XXIV.md',
        'tex': f'{OUTPUT_DIR}/paper24.tex',
        'arxiv': f'{OUTPUT_DIR}/paper24_arxiv.tex',
        'title': "Finite Typed Context Descent",
    },
    'paper25': {
        'md': f'{ROOT}/papers/paper25/Paper XXV.md',
        'tex': f'{OUTPUT_DIR}/paper25.tex',
        'arxiv': f'{OUTPUT_DIR}/paper25_arxiv.tex',
        'title': "Transformation Laws and Localized Stability of Generator-Resolved Diagnostics",
    },
    'paper26': {
        'md': f'{ROOT}/papers/paper26/Paper XXVI.md',
        'tex': f'{OUTPUT_DIR}/paper26.tex',
        'arxiv': f'{OUTPUT_DIR}/paper26_arxiv.tex',
        'title': "Pair-Chain Transfer Operators and Random Synchronization",
    },
    'paper27': {
        'md': f'{ROOT}/papers/paper27/Paper XXVII.md',
        'tex': f'{OUTPUT_DIR}/paper27.tex',
        'arxiv': f'{OUTPUT_DIR}/paper27_arxiv.tex',
        'title': "Entry Sections and Relation-Valued Descent",
    },
    'paper29': {
        'md': f'{ROOT}/papers/paper29/Paper XXIX.md',
        'tex': f'{OUTPUT_DIR}/paper29.tex',
        'arxiv': f'{OUTPUT_DIR}/paper29_arxiv.tex',
        'title': "Cyclic Lineage Dynamics and Rank-Five First-Exit Frontiers",
    },
    'ccs': {
        'md': f'{ROOT}/ccs/canonical_specification.md',
        'tex': f'{OUTPUT_DIR}/ccs.tex',
        'arxiv': f'{OUTPUT_DIR}/ccs_arxiv.tex',
        'title': "RIME Computational Companion Archive",
    },
}


def configure_output_dir(path):
    """Point every generated TeX/PDF artifact at one non-source directory."""
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.abspath(path)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for cfg in PAPERS.values():
        cfg['tex'] = os.path.join(OUTPUT_DIR, os.path.basename(cfg['tex']))
        cfg['arxiv'] = os.path.join(OUTPUT_DIR, os.path.basename(cfg['arxiv']))


def discover_paper(name):
    """Register a canonical ``papers/paperN/Paper *.md`` target on demand."""
    match = re.fullmatch(r'paper\d+', name)
    if not match:
        return False
    paper_dir = os.path.join(ROOT, 'papers', name)
    if not os.path.isdir(paper_dir):
        return False
    candidates = sorted(
        entry for entry in os.listdir(paper_dir)
        if entry.startswith('Paper ') and entry.endswith('.md') and ' - ' not in entry
    )
    if len(candidates) != 1:
        print(
            f"  Cannot discover {name}: expected one canonical Paper *.md, "
            f"found {len(candidates)}"
        )
        return False
    md_path = os.path.join(paper_dir, candidates[0])
    with open(md_path, 'r', encoding='utf-8') as handle:
        first_heading = next(
            (line[2:].strip() for line in handle if line.startswith('# ')),
            name,
        )
    PAPERS[name] = {
        'md': md_path,
        'tex': os.path.join(OUTPUT_DIR, f'{name}.tex'),
        'arxiv': os.path.join(OUTPUT_DIR, f'{name}_arxiv.tex'),
        'title': first_heading,
    }
    return True


configure_output_dir(OUTPUT_DIR)


def run_pandoc(md_path, tex_path):
    """Convert cleaned md to tex via pandoc."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    cleaned, _ = clean_hrules(content)
    if re.search(r'[/\\]papers[/\\]paper\d+[/\\]', md_path.lower()):
        # Canonical Markdown carries reader-visible section numbers. LaTeX
        # supplies its own numbering, so remove only those heading prefixes in
        # the temporary build source.
        cleaned = re.sub(
            r'^(#{2,4})\s+\d+(?:\.\d+)*\.?\s+',
            r'\1 ',
            cleaned,
            flags=re.MULTILINE,
        )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                     encoding='utf-8', delete=False) as tmp:
        tmp.write(cleaned)
        tmp_path = tmp.name

    try:
        os.makedirs(os.path.dirname(tex_path), exist_ok=True)
        cmd = [
            'pandoc', tmp_path,
            '-o', tex_path,
            '--from', 'markdown+tex_math_single_backslash',
            '--to', 'latex',
            '--standalone',
            '--no-highlight',
        ]
        if re.search(r'\[@', cleaned):
            cmd.append('--natbib')
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  pandoc error:\n{result.stderr}")
            return False
        print(f"  -> {tex_path}")
        return True
    finally:
        os.unlink(tmp_path)


def postprocess(tex_path, arxiv_path, title):
    """Run tex → arxiv_tex post-processing."""
    from _postprocess import process
    process(tex_path, arxiv_path, title)


def compile_pdf(arxiv_path):
    """Compile arxiv tex to PDF with xelatex (4 passes) + bibtex.

    Uses 4 passes instead of the standard 3 because xr cross-document
    references can cause label drift requiring an extra stabilization pass.
    """
    xelatex = _find_exe('xelatex')
    if not xelatex:
        print("  xelatex not found — install MiKTeX or TeX Live")
        return False
    bibtex = _find_exe('bibtex')

    tex_dir = os.path.dirname(arxiv_path)
    tex_name = os.path.basename(arxiv_path)
    base_name = os.path.splitext(tex_name)[0]
    env = _tex_env()

    def _read_log():
        log_path = os.path.join(tex_dir, base_name + '.log')
        if not os.path.exists(log_path):
            return ''
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()

    def _run_xelatex(label):
        cmd = [
            xelatex,
            '-interaction=nonstopmode',
            '-halt-on-error',
            '-output-directory',
            tex_dir,
            tex_name,
        ]
        last_output = ''
        for attempt in range(2):
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    cwd=tex_dir, env=env, encoding='utf-8', errors='replace')
            last_output = result.stdout + '\n' + result.stderr
            log_text = _read_log()
            output_written = 'Output written on' in log_text or 'Output written on' in last_output
            fatal = bool(re.search(r'Fatal error|Emergency stop|^!', log_text, re.M))
            if result.returncode == 0 and output_written and not fatal:
                print(f"  xelatex {label} done")
                return True
            if attempt == 0:
                print(f"  xelatex {label}: retrying after incomplete log")

        log_tail = (_read_log() or last_output)[-2000:]
        print(f"  xelatex {label} FAILED")
        for line in log_tail.strip().split('\n')[-10:]:
            print(f"    {line}")
        return False

    def _final_references_ok():
        log_text = _read_log()
        bad_patterns = [
            r'undefined references',
            r'Reference .* undefined',
            r'Label\(s\) may have changed',
            r'File .* not found',
            r'Unable to load picture',
        ]
        hits = []
        for pattern in bad_patterns:
            if re.search(pattern, log_text):
                hits.append(pattern)
        if hits:
            print("  xelatex final check FAILED:")
            for pattern in hits:
                print(f"    {pattern}")
            return False
        return True

    # Pass 1: generate .aux
    if not _run_xelatex('pass 1'):
        return False

    # Bibtex: resolve citations
    if bibtex:
        aux_path = os.path.join(tex_dir, base_name + '.aux')
        if os.path.exists(aux_path):
            cmd = [bibtex, base_name]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    cwd=tex_dir, env=env, encoding='utf-8', errors='replace')
            if result.returncode == 0:
                print(f"  bibtex done")
            else:
                # Non-fatal: bibtex may fail if no citations
                print(f"  bibtex: no citations or skipped")

    # Pass 2: incorporate .bbl
    if not _run_xelatex('pass 2'):
        return False

    # Pass 3: resolve cross-references
    if not _run_xelatex('pass 3'):
        return False

    # Pass 4: stabilize (xr external-doc labels may need extra pass)
    if not _run_xelatex('pass 4'):
        return False
    if not _final_references_ok():
        return False

    pdf_path = arxiv_path.replace('.tex', '.pdf')
    print(f"  -> {pdf_path}")
    return True


def sync_figures():
    """Legacy helper: copy PDF figures into the generated build tree."""
    src_dir = f'{ROOT}/figures'
    dst_dir = f'{OUTPUT_DIR}/figures'
    os.makedirs(dst_dir, exist_ok=True)

    copied = 0
    for sub in ['ccs', 'paper1', 'paper2', 'paper3']:
        src_sub = f'{src_dir}/{sub}'
        dst_sub = f'{dst_dir}/{sub}'
        if not os.path.isdir(src_sub):
            continue
        os.makedirs(dst_sub, exist_ok=True)
        for fname in os.listdir(src_sub):
            if fname.endswith('.pdf'):
                src_f = f'{src_sub}/{fname}'
                dst_f = f'{dst_sub}/{fname}'
                if not os.path.exists(dst_f) or os.path.getmtime(src_f) > os.path.getmtime(dst_f):
                    shutil.copy2(src_f, dst_f)
                    copied += 1
    if copied:
        print(f"  synced {copied} figure PDF(s)")


def build(name, do_pdf=True):
    cfg = PAPERS[name]
    print(f"\n{'='*60}\nBuilding {name}...")

    # Step 1: md → tex (pandoc)
    print("  [1/3] pandoc...")
    if not run_pandoc(cfg['md'], cfg['tex']):
        return False

    # Step 2: tex → arxiv tex (postprocess)
    print("  [2/3] postprocess...")
    postprocess(cfg['tex'], cfg['arxiv'], cfg['title'])

    # Step 3: arxiv tex → PDF (xelatex)
    if do_pdf:
        print("  [3/3] xelatex...")
        if not compile_pdf(cfg['arxiv']):
            return False
    else:
        print("  [3/3] skipped (--no-pdf)")

    return True


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-pdf', action='store_true')
    parser.add_argument(
        '--output-dir',
        default=OUTPUT_DIR,
        help='Generated artifact directory (default: repository output/tex).',
    )
    parser.add_argument('targets', nargs='*')
    parsed = parser.parse_args(argv)
    configure_output_dir(parsed.output_dir)
    do_pdf = not parsed.no_pdf
    args = parsed.targets
    if not args:
        args = ['all']

    for name in args:
        if name not in PAPERS and name not in ('all', 'extras', 'theorems'):
            if not discover_paper(name):
                parser.error(f'unknown build target: {name}')

    targets = [] if ('all' in args or 'extras' in args or 'theorems' in args) else args
    # ── Build CCS first when building everything so its .aux is available
    #     for cross-file references (xr package) in Papers I-III. ──
    if 'all' in args:
        # Build order: ccs -> paper1 -> paper3 -> paper2
        # paper2 xr-loads paper3, so paper3 .aux must exist first
        targets.extend(['ccs', 'paper1', 'paper3', 'paper2'])

    if 'extras' in args:
        targets.extend([
            'paper4', 'paper5', 'paper6', 'paper7', 'paper8', 'paper9',
            'paper10', 'paper11', 'paper12', 'paper13',
        ])

    if 'theorems' in args:
        targets.extend([
            'paper20', 'paper21', 'paper22', 'paper23', 'paper24', 'paper25',
            'paper26', 'paper27', 'paper28', 'paper29', 'paper30', 'paper31',
            'paper32', 'paper33', 'paper16',
        ])

    for name in list(targets):
        if name not in PAPERS:
            discover_paper(name)

    targets = list(dict.fromkeys(name for name in targets if name in PAPERS))

    # Figures are referenced directly from repo-root figures/ via relative path.
    # No copy step needed — changes to figures/ are picked up automatically.
    # sync_figures()

    for name in targets:
        ok = build(name, do_pdf=do_pdf)
        if not ok:
            print(f"  FAILED: {name}")
            return 1

    print(f"\nDone: {len(targets)} built -> {OUTPUT_DIR}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
