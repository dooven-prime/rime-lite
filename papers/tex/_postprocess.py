"""Post-process pandoc TeX into arXiv-ready TeX.

This is the central LaTeX rewrite stage used by ``build.py``.  Keep detailed
Pandoc/LaTeX normalization rules here; helper scripts should either call this
module or perform read-only audits rather than duplicating rewrite logic.
"""
import re, os

ARXIV_PREAMBLE = r"""\documentclass[11pt]{article}

\usepackage[a4paper,margin=1in]{geometry}
\usepackage{iftex}
\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{textcomp}
  \usepackage{pmboxdraw}
  \usepackage{lmodern}
  \usepackage{amsmath,amssymb,amsthm}
\else
  \usepackage{amsmath,amssymb,amsthm}
  \usepackage{unicode-math}
  \usepackage{lmodern}
  \defaultfontfeatures{Scale=MatchLowercase}
  \defaultfontfeatures[\rmfamily]{Ligatures=TeX,Scale=1}
  \IfFontExistsTF{DejaVu Sans Mono}{
    \setmonofont{DejaVu Sans Mono}[Scale=MatchLowercase]
  }{}
\fi
\usepackage{mathtools}
\usepackage{newunicodechar}
\newunicodechar{κ}{$\kappa$}
\newunicodechar{α}{$\alpha$}
\newunicodechar{β}{$\beta$}
\newunicodechar{τ}{$\tau$}
\newunicodechar{ρ}{$\rho$}
\newunicodechar{λ}{$\lambda$}
\newunicodechar{π}{$\pi$}
\newunicodechar{ω}{$\omega$}
\newunicodechar{ε}{$\varepsilon$}
\newunicodechar{σ}{$\sigma$}
\newunicodechar{Δ}{$\Delta$}
\newunicodechar{Σ}{$\Sigma$}
\newunicodechar{₀}{$_{0}$}
\newunicodechar{₁}{$_{1}$}
\newunicodechar{₂}{$_{2}$}
\newunicodechar{₃}{$_{3}$}
\newunicodechar{₄}{$_{4}$}
\newunicodechar{₅}{$_{5}$}
\newunicodechar{₆}{$_{6}$}
\newunicodechar{₇}{$_{7}$}
\newunicodechar{₈}{$_{8}$}
\newunicodechar{₉}{$_{9}$}
\newunicodechar{⁰}{$^{0}$}
\newunicodechar{¹}{$^{1}$}
\newunicodechar{⁴}{$^{4}$}
\newunicodechar{⁵}{$^{5}$}
\newunicodechar{⁶}{$^{6}$}
\newunicodechar{⁷}{$^{7}$}
\newunicodechar{⁸}{$^{8}$}
\newunicodechar{⁹}{$^{9}$}
\newunicodechar{⁻}{$^{-}$}
\newunicodechar{⊕}{$\oplus$}
\newunicodechar{⊋}{$\supsetneq$}
\newunicodechar{≈}{$\approx$}
\usepackage{bm}
\usepackage{graphicx}
\usepackage{float}
\usepackage[section]{placeins}
\usepackage[font=normal,labelfont=bf]{caption}
\captionsetup{labelformat=empty}
\usepackage{hyperref}
\usepackage{xr}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{array}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}

\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}

\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}
\newtheorem{example}[theorem]{Example}

% Prevent orphans/widows: no single line stranded at page top/bottom
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000

\bibliographystyle{plain}
"""

# ── Theorem/Lemma/Corollary/Definition/Remark/Proposition types ──
THM_TYPES = {
    'Theorem', 'Lemma', 'Corollary', 'Definition', 'Remark', 'Proposition', 'Example',
}
THM_TYPES_LOWER = {t.lower() for t in THM_TYPES}

# Figures converted by pandoc are ordinary LaTeX floats.  The default float
# placement omits "here", so figures can drift farther than the surrounding
# prose expects.  Most figures should still float, but a small number of
# locally explanatory figures are pinned because the paragraph depends on them
# immediately.
PINNED_FIGURE_LABELS = {
    # Paper II: first-use mechanism figures.
    'fig:fig1-k-heatmap',
    'fig:fig5-s6-hub-signature',
    'fig:fig2-supp-nc-mechanism',
    # Paper III: local conceptual mechanism figures.
    'fig:fig3-curvature-emergence',
    'fig:fig2-lie-barrier',
    # Paper XIV: keep the admission boundary before its three-case audit.
    'fig:fig6-admission-boundary',
}


def _label_slug(name):
    """Generate a LaTeX-safe label slug from a theorem name."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug.strip('-')


def _section_slug(title):
    """Generate a LaTeX-safe label slug from a section title.

    Handles LaTeX math, commands, and Unicode punctuation inside the title.
    """
    # Strip inline math $...$
    title = re.sub(r'\$[^$]*\$', '', title)
    # Strip LaTeX commands with arguments: \\mathrm{...}, \\mathbb{...}, etc.
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
    # Strip remaining bare LaTeX commands
    title = re.sub(r'\\[a-zA-Z]+', '', title)
    # Replace Unicode dashes
    title = title.replace('—', '-').replace('–', '-')
    # Lowercase
    slug = title.lower().strip()
    # Remove everything except a-z, 0-9, whitespace, hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace whitespace runs with a single hyphen
    slug = re.sub(r'\s+', '-', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing hyphens and ensure non-empty
    return slug.strip('-') or 'section'


def _normalize_headings(body):
    """Join multi-line \\section/\\subsection/\\subsubsection into single lines.

    Strips pandoc-generated \\label from headings so downstream code sees
    clean single-line headings.
    """
    lines = body.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'(\\(?:section|subsection|subsubsection)\{)(.*)', line)
        if not m:
            out.append(line)
            i += 1
            continue

        prefix = m.group(1)
        rest = m.group(2)

        # Account for the opening brace in prefix; accumulate until depth = 0
        depth = 1 + rest.count('{') - rest.count('}')
        while depth > 0 and i + 1 < len(lines):
            i += 1
            nxt = lines[i].strip()
            rest += ' ' + nxt
            depth += nxt.count('{') - nxt.count('}')

        # Strip inline trailing \\label{...}
        rest = re.sub(r'\}\\label\{[^}]*\}$', '}', rest)

        # Skip orphan \\label on the next line
        if i + 1 < len(lines) and re.match(r'\s*\\label\{[^}]*\}\s*$', lines[i + 1]):
            i += 1

        out.append(prefix + rest)
        i += 1

    return '\n'.join(out)


def add_section_labels(body):
    """Add \\label{sec:...} after every \\section, \\subsection, \\subsubsection.

    Assumes headings are already single-line (call ``_normalize_headings`` first).
    Handles \\texorpdfstring{...}{...} inside headings by protecting them first.
    """
    # Protect \texorpdfstring{Text}{Math} blocks so [^}]* doesn't stop early
    tex_blocks = {}
    def _save_tex(m):
        token = f'<<<TEX{len(tex_blocks)}>>>'
        tex_blocks[token] = m.group(0)
        return token

    body = re.sub(
        r'\\texorpdfstring\{[^}]*\}\{[^}]*\}',
        _save_tex,
        body,
    )

    def _insert_label(m):
        cmd = m.group(1)
        star = m.group(2) or ''
        title = m.group(3)
        return f'\\{cmd}{star}{{{title}}}\\label{{sec:{_section_slug(title)}}}'

    body = re.sub(
        r'\\(section|subsection|subsubsection)(\*?)\{([^}]*)\}',
        _insert_label,
        body,
    )

    # Restore texorpdfstring blocks
    for token, orig in tex_blocks.items():
        body = body.replace(token, orig)

    return body


def _extract_name(text):
    r"""Extract parenthesized name from text, skipping \(...\) and $...$.
    Returns (name, rest) or (None, text)."""
    s = text.strip()
    if not s.startswith('('):
        return None, text
    depth = 0
    in_math_paren = False   # inside \(...\)
    in_math_dollar = False  # inside $...$
    i = 0
    while i < len(s):
        ch = s[i]
        if not in_math_paren and not in_math_dollar:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    name = s[1:i]
                    after = s[i + 1:]
                    if after.startswith('.'):
                        after = after[1:]
                    return name, after
            elif ch == '\\' and i + 1 < len(s) and s[i + 1] == '(':
                in_math_paren = True
                i += 1
            elif ch == '$':
                in_math_dollar = True
        elif in_math_paren:
            if ch == '\\' and i + 1 < len(s) and s[i + 1] == ')':
                in_math_paren = False
                i += 1
        elif in_math_dollar:
            if ch == '$':
                in_math_dollar = False
        i += 1
    return None, text


def _find_thm_heading(line):
    r"""Parse \subsection{Type N (Name)} or \subsection{Type N}.

    Also handles unnumbered forms:
      \subsection{Type: Name}
      \subsection{The ... Type (Name)}

    Returns (env_type, number, name, label_slug) or None.
    """
    s = line.strip()
    # Numbered: Type N (Name) or Type N
    m = re.match(
        r'\\subsection{('
        r'(?:Theorem|Lemma|Corollary|Definition|Remark|Proposition|Example)'
        r')\s+(\d+(?:\.\d+)*)'
        r'([^}]*)\}',
        s,
    )
    if m:
        raw_type = m.group(1)
        number = m.group(2)
        after_number = m.group(3).strip()
        name, _ = _extract_name(after_number)
        if name is None:
            # Try em-dash format: "Lemma 0 --- Name"
            m_dash = re.match(r'[-–—]{2,3}\s*(.+)', after_number)
            if m_dash:
                name = m_dash.group(1).strip()
            else:
                name = ''
        env = raw_type.lower()
        slug = _label_slug(name) if name else number.replace('.', '-')
        return env, number, name, slug

    # Unnumbered with colon: Type: Name
    m = re.match(
        r'\\subsection{('
        r'(?:Theorem|Lemma|Corollary|Definition|Remark|Proposition|Example)'
        r'):\s+([^}]+)}',
        s,
    )
    if m:
        raw_type = m.group(1)
        name = m.group(2).strip()
        env = raw_type.lower()
        slug = _label_slug(name)
        return env, '', name, slug

    return None


def _find_bold_thm(line):
    """Parse \textbf{Type N (Name).}, \textbf{Type A.1 (Name).},
    \textbf{Type (Name).}, \textbf{Type.} — inline bold format.

    Also handles \textbf{Type A.1} (Name). where the parenthesized name
    falls outside the bold markup.
    """
    s = line.strip()
    if not s.startswith(r'\textbf{'):
        return None
    # Find matching } — handles nested braces (e.g. \mathcal{U})
    depth = 1
    end = 8  # start after \textbf{
    while end < len(s) and depth > 0:
        if s[end] == '{':
            depth += 1
        elif s[end] == '}':
            depth -= 1
        end += 1
    if depth != 0:
        return None
    end -= 1  # position of matching }
    inner = s[8:end]
    after_brace = s[end + 1:]  # text after closing }
    for raw_type in THM_TYPES:
        prefix = raw_type + ' '
        if not inner.startswith(prefix):
            continue
        rest = inner[len(prefix):]

        # Try alphanumeric number first: A.1, C.1, 3.6, etc.
        m_num = re.match(r'([A-Z]?\d+(?:\.\d+)*)', rest)
        number = ''
        after = rest
        if m_num:
            number = m_num.group(1)
            after = rest[m_num.end():]

        name = ''
        m_name, after_rest = _extract_name(after)
        if m_name is not None:
            name = m_name
            after = after_rest
        elif not number:
            if after.strip() == '.':
                pass  # bare type, no name

        # Also try parenthesized name outside braces:
        #   \textbf{Corollary A.1} (All Direct Edges...).
        if not name:
            m_name_out, _ = _extract_name(after_brace)
            if m_name_out is not None:
                name = m_name_out

        # Require at least one of number or name (avoid matching mid-text refs
        # like "\textbf{Theorem} is important" — though those are rare)
        if not number and not name and inner != raw_type + '.':
            continue

        env = raw_type.lower()
        slug = _label_slug(name) if name else (number.replace('.', '-') if number else 'section')
        return env, number, name, slug
    return None


def match_thm(line):
    """Returns (env_type, number, name, label_slug) or None."""
    result = _find_thm_heading(line)
    if result:
        return result
    # Strip leading \] (display math close) so that "\] \textbf{Theorem ...}"
    # on the same line is still recognized.
    s = line.strip()
    if s.startswith(r'\]') and len(s) > 2:
        result = _find_bold_thm(s[2:].strip())
        if result:
            return result
    return _find_bold_thm(line)


def end_here(line):
    """Should a theorem environment end before this line?"""
    s = line.strip()
    if not s:
        return False
    stops = [
        r'\subsection', r'\section', r'\subsubsection',
        r'\begin{center}\rule', r'\begin{longtable}',
        r'\begin{figure}',
        r'\end{enumerate}', r'\end{itemize}', r'\end{quote}',
    ]
    if any(s.startswith(t) for t in stops):
        return True
    # Stop at \textbf{Type...} that starts a new theorem-like block
    if s.startswith(r'\textbf{'):
        for t in THM_TYPES:
            if s.startswith(r'\textbf{' + t):
                return True
    return False


def _convert_heading_math(text):
    """Convert only subscripts, superscripts, and Greek in headings to LaTeX math.
    Symbols like →, ⊕ are left as Unicode — they break hyperref PDF bookmarks.
    """
    subs = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5',
            '₆': '6', '₇': '7', '₈': '8', '₉': '9'}
    sups = {'⁰': '0', '¹': '1', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7',
            '⁸': '8', '⁹': '9', '⁻': '-'}
    greek = {'κ': r'\kappa', 'α': r'\alpha', 'β': r'\beta',
             'τ': r'\tau', 'ρ': r'\rho', 'λ': r'\lambda', 'π': r'\pi',
             'ω': r'\omega', 'ε': r'\varepsilon', 'Δ': r'\Delta',
             'σ': r'\sigma', 'Σ': r'\Sigma'}

    # Greek + subscript combos
    for g_uni, g_latex in greek.items():
        for s_uni, s_num in subs.items():
            text = text.replace(g_uni + s_uni, f'${g_latex}_{s_num}$')

    # Latin letter + subscript
    for s_uni, s_num in subs.items():
        text = re.sub(
            r'(?<!\$)(?<!\\)([A-Za-z])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', text)

    # Digit + subscript
    for s_uni, s_num in subs.items():
        text = re.sub(
            r'(?<!\$)(?<!\\)([0-9])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', text)

    # Latin letter + superscript
    for s_uni, s_num in sups.items():
        text = re.sub(
            r'(?<!\$)(?<!\\)([A-Za-z])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}^{{{n}}}$', text)

    # Standalone Greek (not followed by subscript)
    for g_uni, g_latex in greek.items():
        text = re.sub(
            r'(?<!\\)(?<!\$)' + re.escape(g_uni) + r'(?![\d₀₁₂₃₄₅₆₇₈₉])',
            lambda m, cmd=g_latex: f'${cmd}$', text)

    # $...$ + subscript — fold subscript into preceding math block
    for s_uni, s_num in subs.items():
        text = re.sub(
            r'\$([^$]+)\$' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', text)

    # $...$ + Greek — fold Greek into preceding math block
    for g_uni, g_latex in greek.items():
        text = re.sub(
            r'\$([^$]+)\$' + re.escape(g_uni),
            lambda m, gl=g_latex: f'${m.group(1)}{gl}$', text)

    return text


def protect_blocks(body):
    """Protect verbatim, math, and heading blocks from downstream processing.

    Returns (protected_body, blocks) — blocks is {token: original}.
    Tokens use <<<N>>> numbering for stable restore order.
    """
    blocks = {}

    def _save(m):
        token = f'<<<{len(blocks)}>>>'
        blocks[token] = m.group(0)
        return token

    # 0. Section headings — newunicodechar handles Greek/subscripts at TeX level;
    #    protect from Python-level symbol conversion (→→\rightarrow breaks bookmarks)
    body = re.sub(
        r'\\(section|subsection|subsubsection|paragraph)\*?\{[^}]*\}',
        _save, body,
    )

    # 1. Verbatim blocks
    body = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}',
                  _save, body, flags=re.DOTALL)

    # 2. Display math $$...$$
    body = re.sub(r'\$\$.*?\$\$', _save, body, flags=re.DOTALL)

    # 3. Inline math $...$ (not $$, not \$ escaped)
    body = re.sub(r'(?<!\\)\$(?!\$)[^$]+(?<!\\)\$(?!\$)',
                  _save, body)

    return body, blocks


def restore_blocks(body, blocks):
    """Restore protected blocks from tokens. Restore in reverse order
    (largest token number first) to avoid partial-token collisions."""
    for token in sorted(blocks, key=lambda t: int(t[3:-3]), reverse=True):
        body = body.replace(token, blocks[token])

    # verb_blocks = []
    # def protect_verb(m):
    #     verb_blocks.append(m.group(0))
    #     return f'<<<VB{len(verb_blocks)-1}>>>'
    # body = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}',
    #               protect_verb, body, flags=re.DOTALL)
    return body


def convert_unicode_math(body):
    """Convert Unicode math chars to LaTeX math mode, outside protected blocks."""
    body, blocks = protect_blocks(body)

    # Greek + subscript combos (longest patterns first)
    greek = {'κ': r'\kappa', 'α': r'\alpha', 'β': r'\beta',
             'τ': r'\tau', 'Π': r'\Pi', 'ρ': r'\rho',
             'λ': r'\lambda', 'π': r'\pi',
             'ω': r'\omega', 'ε': r'\varepsilon', 'Δ': r'\Delta',
             'σ': r'\sigma', 'Σ': r'\Sigma'}
    subs = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5',
            '₆':'6','₇':'7','₈':'8','₉':'9'}
    sups = {'⁰':'0','¹':'1','⁴':'4','⁵':'5','⁶':'6','⁷':'7',
            '⁸':'8','⁹':'9','⁻':'-'}

    for g_uni, g_latex in greek.items():
        for s_uni, s_num in subs.items():
            body = body.replace(g_uni + s_uni, f'${g_latex}_{s_num}$')

    # Latin letter + Unicode subscript → $letter_num$
    for s_uni, s_num in subs.items():
        body = re.sub(
            r'(?<!\$)(?<!\\)([A-Za-z])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', body)

    # Digit followed by Unicode subscript → $digit_num$ (e.g., 1₃)
    for s_uni, s_num in subs.items():
        body = re.sub(
            r'(?<!\$)(?<!\\)([0-9])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', body)

    # Latin letter + Unicode superscript → $letter^num$
    for s_uni, s_num in sups.items():
        body = re.sub(
            r'(?<!\$)(?<!\\)([A-Za-z])' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}^{{{n}}}$', body)

    # Catch remaining standalone subscript chars (wrap in math with empty base)
    # These appear after / or other non-letter chars
    for s_uni, s_num in subs.items():
        # / + subscript (e.g., $V_8$/₉) → replace just the subscript
        body = body.replace('/' + s_uni, '/$' + s_num + '$')
        # $...$ + subscript → fold subscript into preceding math block
        body = re.sub(
            r'\$([^$]+)\$' + re.escape(s_uni),
            lambda m, n=s_num: f'${m.group(1)}_{n}$', body)
        # comma/space + subscript
        body = body.replace(', ' + s_uni, ', $' + s_num + '$')

    # Catch remaining standalone superscript chars
    for s_uni, s_num in sups.items():
        body = body.replace(s_uni, f'$^{{{s_num}}}$')

    # Standalone Greek chars (not already inside $...$ or preceded by \)
    for g_uni, g_latex in greek.items():
        body = re.sub(
            r'(?<!\\)(?<!\$)' + re.escape(g_uni) + r'(?![\d₀₁₂₃₄₅₆₇₈₉])',
            lambda m, cmd=g_latex: f'${cmd}$', body)

    # Standalone math symbols
    symbols = {
        '⊕': r'\oplus', '→': r'\rightarrow', '↔': r'\leftrightarrow',
        '∼': r'\sim', '≈': r'\approx', '≥': r'\geq', '⊋': r'\supsetneq',
        '∝': r'\propto', '≠': r'\neq',
        '⊊': r'\subsetneq', '′': r'\prime', '⟨': r'\langle', '⟩': r'\rangle',
        '✓': r'\checkmark', '✗': r'\times',
        '≤': r'\leq', 'ℤ': r'\mathbb{Z}',
        '‖': r'\|', '↓': r'\downarrow', '⇒': r'\Rightarrow',
        '∅': r'\emptyset', '∈': r'\in', '∞': r'\infty',
        '∩': r'\cap', 'ℂ': r'\mathbb{C}',
        '±': r'\pm', '·': r'\cdot',
    }
    for uni_sym, latex_cmd in symbols.items():
        body = body.replace(uni_sym, f'${latex_cmd}$')

    # Simple char replacements (no math mode wrapping needed or simple)
    simple = {'∗': '*', '−': '-', '×': r'$\times$', '≅': r'$\cong$',
              '§': r'\S', 'Ü': r'\"U', 'é': r"\'e", '¹': r'$^{1}$',
              '⁰': r'$^{0}$', '⁴': r'$^{4}$', '⁶': r'$^{6}$',
              '⁸': r'$^{8}$', '⁻': r'$^{-}$',
              '≀': r'$\wr$', 'ᵀ': r'$^{\mathsf{T}}$',
              '°': r'$^\circ$', '²': r'$^{2}$', '³': r'$^{3}$',
              '†': r'$\dagger$',
              }
    for uni_c, repl in simple.items():
        body = body.replace(uni_c, repl)

    body = restore_blocks(body, blocks)
    return body


def _restructure_sections(body, is_ccs=False):
    r"""Make Abstract/Notation Table/References unnumbered, appendices lettered.

    Called BEFORE add_section_labels, so headings look like \section{Name}
    without trailing \label{sec:...}.  We:
      1. Convert \section{Abstract} and \section{Notation Table} to \section*
      2. (CCS only) Convert \section{Part ...} to \section* with
         \refstepcounter{section} to keep theorem [section] counter working
         while suppressing the LaTeX section number that conflicts with
         CCS part identifiers.
      3. Insert \appendix before the first appendix section and strip
         "Appendix X: " / "X.Y " prefixes.
      4. Convert \section{References} to \section*; subsections after it to
         \subsection*.
    """
    # 1. Abstract → unnumbered
    body = re.sub(r'\\section\{Abstract\}', r'\\section*{Abstract}', body)
    # 2. Notation Table → unnumbered
    body = re.sub(r'\\section\{Notation Table\}', r'\\section*{Notation Table}', body)
    # 2b. (CCS only) Part sections → \section* with \refstepcounter.
    # CCS Parts carry their own identifiers (0, 0.5, I, II, III) in the
    # title; LaTeX section numbers (1, 2, 3) would create a conflicting
    # dual-numbering system.  We suppress the LaTeX number but keep the
    # counter stepping so that theorem [section] numbering still works.
    if is_ccs:
        def _make_part_unnumbered(m):
            title = m.group(1)
            return (
                r'\refstepcounter{section}' + '\n'
                + r'\addcontentsline{toc}{section}{' + title + r'}' + '\n'
                + r'\section*{' + title + r'}'
            )
        body = re.sub(
            r'\\section\{(Part\s+[^\}]+)\}',
            _make_part_unnumbered,
            body,
        )
    # 3. Insert \appendix before the first appendix section and strip prefixes.
    # 3a. Remove bold identity lines that duplicate Part/Appendix section headings.
    #     CCS markdown: **Part X --- Title** / **Appendix Y --- Title** followed by
    #     ## Part X --- Title / ## Appendix Y --- Title.  Pandoc → \textbf{...} +
    #     \section{...} with LaTeX boilerplate (\appendix, \refstepcounter, etc.)
    #     between them.  Remove the bold line when a \section/\section* or \appendix
    #     follows within ~500 chars, indicating it's an identity marker, not a
    #     cross-reference or standalone sub-header.
    def _is_identity_marker(m):
        # Only strip standalone bold identity markers, not inline
        # references like "see \textbf{Appendix C ...}".
        # Check if there are letters on the same line before the match.
        line_start = m.string.rfind('\n', 0, m.start())
        if line_start < 0:
            line_start = 0
        else:
            line_start += 1
        same_line_before = m.string[line_start:m.start()]
        if re.search(r'[a-zA-Z]', same_line_before):
            return m.group(0)  # inline reference — keep
        ahead = m.string[m.end():m.end() + 500]
        if re.search(r'\\(?:section\*?\{|appendix\b)', ahead):
            return ''
        return m.group(0)
    body = re.sub(
        r'\\textbf\{(Part\s+\S+|Appendix\s+[A-Z])\s*[^}]*?\}\s*\n*',
        _is_identity_marker,
        body,
    )
    # 3b. Insert \appendix
    first_appendix = re.search(r'\\section\{Appendix\s+[A-Z]', body)
    if first_appendix:
        appendix_preamble = (r'\appendix' + '\n'
                           + r'\renewcommand{\thesection}{Appendix \Alph{section}}' + '\n'
                           + r'\renewcommand{\thesubsection}{\Alph{section}.\arabic{subsection}}')
        if is_ccs:
            # CCS sets secnumdepth=1 globally (suppresses \subsection numbering
            # because CCS subsections carry hardcoded Part-scoped IDs).
            # Re-enable \subsection numbering for appendix subsections (G.1, G.2, …).
            appendix_preamble += '\n' + r'\setcounter{secnumdepth}{2}'
        appendix_preamble += '\n\n'
        body = (body[:first_appendix.start()]
                + appendix_preamble
                + body[first_appendix.start():])
        # Strip "Appendix X: " or "Appendix X --- " prefix from section titles
        body = re.sub(
            r'\\section\{Appendix\s+[A-Z]\s*[:\-–—]+\s*([^}]*?)\}',
            r'\\section{\1}',
            body,
        )
        # Strip "X.Y " number-prefix from subsection titles in appendix zone
        app_pos = body.find(r'\appendix')
        ref_pos = body.find(r'\section{References}')
        if ref_pos < 0:
            ref_pos = body.find(r'\section*{References}')
        zone_end = ref_pos if ref_pos > app_pos else len(body)
        before = body[:app_pos]
        zone = body[app_pos:zone_end]
        after = body[zone_end:]
        # Plain subsections: \subsection{A.1 Name}
        zone = re.sub(
            r'\\subsection\{[A-Z]\.\d+\s+([^}]*?)\}',
            r'\\subsection{\1}',
            zone,
        )
        # \texorpdfstring subsections — strip prefix from both args:
        #   \subsection{\texorpdfstring{A.1 Name}{A.1 Name}}
        zone = re.sub(
            r'\\subsection\{\\texorpdfstring\{[A-Z]\.\d+\s+([^}]*?)\}\{[A-Z]\.\d+\s+([^}]*?)\}\}',
            r'\\subsection{\\texorpdfstring{\1}{\2}}',
            zone,
        )
        body = before + zone + after
    # 4. Legacy prose References -> Bibliographic Notes (unnumbered).
    #    Current manuscripts use a Related Work section; \bibliography{trilogy}
    #    generates the formal References section.
    #    Subsections within also unnumbered.
    ref_match = re.search(r'\\section\{References\}', body)
    if ref_match:
        body = (body[:ref_match.start()]
                + r'\section*{Bibliographic Notes}'
                + body[ref_match.end():])
        # Make subsections after References into \subsection*
        ref_pos = ref_match.start()
        after_refs = body[ref_pos:]
        after_refs = re.sub(
            r'\\subsection\{([^}]*?)\}',
            r'\\subsection*{\1}',
            after_refs,
        )
        body = body[:ref_pos] + after_refs

    return body


def _convert_proof_remark_environments(body):
    r"""Convert \subsection/\subsubsection{Proof/Remark/Example} to theorem environments.

    In the markdown source, Proof/Remark/Example are written as ### or ####
    headings.  Pandoc converts them to \subsubsection or \paragraph; the
    promotion step maps these to \subsection and \subsubsection respectively.
    Both levels are numbered, appear in the TOC, and lack proper theorem
    formatting.

    Heading formats handled:
      Proof.                             → \begin{proof}
      Proof. --- Name                    → \begin{proof}[Name]
      Remark.                            → \begin{remark}
      Remark (Name).                     → \begin{remark}[Name]
      Example. / Example (Name).         → \begin{example}[Name]
    """
    import re as _re

    def _parse_note(suffix):
        """Extract optional note from the heading suffix text.

        suffix examples: '.', '. --- Galois stability', ' (Scope).', ''
        Returns note string or None.
        """
        suffix = suffix.strip()
        if not suffix:
            return None
        # Parenthetical: " (Name)." or " (Name)"
        m = _re.match(r'\s*\(([^)]*)\)\.?$', suffix)
        if m:
            return m.group(1).strip() or None
        # Dash-separated: ". --- Name" or ". --- Name."
        m = _re.match(r'\.\s*---\s*(.*?)\.?$', suffix)
        if m:
            return m.group(1).strip() or None
        return None

    env_map = {'Proof': 'proof', 'Remark': 'remark', 'Example': 'example'}

    for env_name, env_cmd in env_map.items():
        heading_pat = (
            r'\\(?:sub){0,2}section\{'       # \section, \subsection, or \subsubsection
            + _re.escape(env_name) +
            r'([^}]*)\}\\label\{sec:[^}]*\}\s*\n'  # capture suffix, then label
        )
        content_pat = (
            r'(.*?)'                          # content (non-greedy)
            r'(?=\\(?:sub){0,2}section\{|'     # stop at next heading
            r'\\end\{document\})'
        )

        def make_replacer(cmd):
            def replacer(m):
                suffix = m.group(1)
                note = _parse_note(suffix)
                content = m.group(2).strip()
                if note:
                    return f'\\begin{{{cmd}}}[{note}]\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'
                else:
                    return f'\\begin{{{cmd}}}\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'
            return replacer

        body = _re.sub(
            heading_pat + content_pat,
            make_replacer(env_cmd),
            body,
            flags=_re.DOTALL
        )

    return body


def _convert_inline_proof_remark(body):
    r"""Convert inline \textbf{Type.} / \textbf{Type (Name).} / \emph{Proof.}
    to amsthm environments.

    This is a safety-net pass for any theorem-like labels that survived the
    line-by-line theorem-wrapping pass (e.g. unnumbered named theorems,
    alphanumeric corollaries, or inline remarks).
    """
    import re as _re

    env_map = {
        'Theorem': 'theorem', 'Lemma': 'lemma', 'Proposition': 'proposition',
        'Corollary': 'corollary', 'Definition': 'definition',
        'Remark': 'remark', 'Example': 'example',
    }

    _bs = r'\\'
    _structural_cmds = r'textbf|emph|textit|section|subsection|subsubsection|paragraph|begin|end'
    _content_pat = (
        r'([^\n]*)'                              # rest of first line
        r'((?:'                                   # remaining content:
        r'(?!'                                    #   NOT at:
        r'\n\n'                                   #     blank line then
        + _bs + r'(?:' + _structural_cmds + r')'  #     structural command
        r'|'                                      #   OR:
        r'\n' + _bs + r'end\{(?!enumerate|itemize)'  #     \end{env} (non-list) on own line
        r')'                                      #
        r'.)'                                     #   any character (DOTALL)
        r'*)'                                     #
    )

    # ── Italic: \emph{Proof.} / \textit{Proof.} content ──
    italic_pat = (
        _bs + r'(?:emph|textit)\{Proof\.?\}'
        r'\s+'
        + _content_pat
    )
    def _italic_replacer(m):
        first_line = m.group(1)
        rest_lines = m.group(2)
        if rest_lines.startswith('\n'):
            rest_lines = rest_lines[1:]
        content = (first_line + '\n' + rest_lines).rstrip()
        return f'\\begin{{proof}}\n\\noindent\n{content}\n\\end{{proof}}\n\n'

    body = _re.sub(italic_pat, _italic_replacer, body, flags=_re.DOTALL)

    # ── Bold: \textbf{Type...} for all theorem types ──
    for type_name, env_cmd in env_map.items():
        # Pattern: \n\n\textbf{Type...} at paragraph boundary
        bold_pat = (
            r'\n\n'
            + _bs + r'textbf\{' + _re.escape(type_name)
            + r'((?:[^{}]|\{[^{}]*\})*)\}'          # rest inside braces (handles one level of nesting like \mathcal{U})
            + r'\s*'
            + _content_pat
        )

        def _bold_replacer(m, cmd=env_cmd):
            inner = m.group(1)  # rest inside braces after type name
            first_line = m.group(2)
            rest_lines = m.group(3)

            # Extract name from parentheses
            name = ''
            name_m = _re.search(r'\(([^)]+)\)', inner)
            if name_m:
                name = name_m.group(1)

            if rest_lines.startswith('\n'):
                rest_lines = rest_lines[1:]
            content = (first_line + '\n' + rest_lines).rstrip()

            # Extract \label{...} from beginning of content
            label_line = ''
            label_match = _re.match(r'^\s*(\\label\{[^}]*\})\s*', content)
            if label_match:
                label_line = label_match.group(1)
                content = content[label_match.end():].lstrip()

            label_block = f'\n{label_line}' if label_line else ''
            if name:
                return f'\n\n\\begin{{{cmd}}}[{name}]{label_block}\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'
            else:
                return f'\n\n\\begin{{{cmd}}}{label_block}\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'

        body = _re.sub(bold_pat, _bold_replacer, body, flags=_re.DOTALL)

        # Also handle after display math: \] \n\textbf{Type...}
        math_pat = (
            r'(\\\]\s*\n)'
            + _bs + r'textbf\{' + _re.escape(type_name)
            + r'([^}]*)\}'
            + r'\s*'
            + _content_pat
        )
        def _math_replacer(m, cmd=env_cmd):
            prefix = m.group(1)  # \] \n
            inner = m.group(2)
            first_line = m.group(3)
            rest_lines = m.group(4)

            name = ''
            name_m = _re.search(r'\(([^)]+)\)', inner)
            if name_m:
                name = name_m.group(1)

            if rest_lines.startswith('\n'):
                rest_lines = rest_lines[1:]
            content = (first_line + '\n' + rest_lines).rstrip()

            # Extract \label{...} from beginning of content
            label_line = ''
            label_match = _re.match(r'^\s*(\\label\{[^}]*\})\s*', content)
            if label_match:
                label_line = label_match.group(1)
                content = content[label_match.end():].lstrip()

            label_block = f'\n{label_line}' if label_line else ''
            if name:
                return f'{prefix}\\begin{{{cmd}}}[{name}]{label_block}\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'
            else:
                return f'{prefix}\\begin{{{cmd}}}{label_block}\n\\noindent\n{content}\n\\end{{{cmd}}}\n\n'

        body = _re.sub(math_pat, _math_replacer, body, flags=_re.DOTALL)

    return body


def _normalize_theorem_labels(body):
    r"""Normalize all theorem labels to stable 3-letter prefix format.

    - Prefix: theorem→thm, lemma→lem, definition→def, proposition→prop,
      corollary→cor
    - Fix known broken slugs (lemma:1, theorem:t7-----…)
    - Apply canonical slug remappings for permanently stable labels
    - Update all \ref{} cross-references to match.
    """
    prefix_map = {
        'theorem': 'thm', 'lemma': 'lem', 'definition': 'def',
        'proposition': 'prop', 'corollary': 'cor',
    }

    # 1. Rename prefixes in \label{...} and \ref{...}
    for old, new in prefix_map.items():
        body = body.replace(f'\\label{{{old}:', f'\\label{{{new}:')
        body = body.replace(f'\\ref{{{old}:', f'\\ref{{{new}:')

    # 2. Canonical slug remappings — these are the permanent stable labels
    #    that survive heading-text changes and renumbering.
    canonical_slugs = {
        # Paper I
        'thm:spectral-origin': 'thm:spectral-collapse',
        'thm:rationality-from-galois-stable-projector-----conditional': 'thm:field-of-definition',
        # Paper III
        'lem:0': 'lem:pure-sector-obstruction',
        'thm:t7-theorem': 'thm:t7',
        'thm:t7-theorem-c0-c3': 'thm:t7',
    }
    for old_slug, new_slug in canonical_slugs.items():
        body = body.replace(f'\\label{{{old_slug}}}', f'\\label{{{new_slug}}}')
        body = body.replace(f'\\ref{{{old_slug}}}', f'\\ref{{{new_slug}}}')

    # 2b. Safety net: fix double-prefix references (thm:thm: → thm:, etc.)
    # These arise from implicit cross-reference logic when a label already has
    # the short prefix (e.g. \label{thm:block-reduction-of-the-k-set}) and the
    # prefix-stripping list only checks long forms.
    short_pfxs = ['thm', 'lem', 'def', 'prop', 'cor']
    for pfx in short_pfxs:
        body = body.replace(f'\\ref{{{pfx}:{pfx}:', f'\\ref{{{pfx}:')
        body = body.replace(f'\\label{{{pfx}:{pfx}:', f'\\label{{{pfx}:')

    # 3. Fix known broken labels from pandoc unicode corruption
    body = body.replace('\\label{lem:1}', '\\label{lem:lie-support-invariance}')
    body = body.replace('\\ref{lem:1}', '\\ref{lem:lie-support-invariance}')
    # T7: collapse the unicode-garbage slug to a clean one
    body = re.sub(
        r'\\label\{thm:t7-+compositional-accessibility-.*?\}',
        r'\\label{thm:t7}',
        body,
    )
    body = re.sub(
        r'\\ref\{thm:t7-+compositional-accessibility-.*?\}',
        r'\\ref{thm:t7}',
        body,
    )

    return body


def _strip_manual_qed(body):
    r"""Remove any remaining manual QED markers (\blacksquare, \square).

    amsthm's \begin{proof} provides □ automatically; all other theorem
    environments should have no end marker.  This pass strips any
    \blacksquare or \square that may have survived from legacy sources.
    """
    import re as _re

    # Inline math: \(\blacksquare\), \(\square\), $\blacksquare$, $\square$
    body = _re.sub(r'\\\(\\blacksquare\\\)', '', body)
    body = _re.sub(r'\\\(\\square\\\)', '', body)
    body = _re.sub(r'\$\\blacksquare\$', '', body)
    body = _re.sub(r'\$\\square\$', '', body)

    # Display math or standalone
    body = _re.sub(r'\\blacksquare', '', body)
    body = _re.sub(r'\\square(?!\s*\\)', '', body)  # avoid matching \square in math commands

    # Parenthesized variants: (\blacksquare), (\(\blacksquare\)), ($\blacksquare$)
    body = _re.sub(r'\(\\blacksquare\)', '', body)
    body = _re.sub(r'\(\\square\)', '', body)
    body = _re.sub(r'\\\(\\blacksquare\\\)', '', body)
    body = _re.sub(r'\\\(\\square\\\)', '', body)

    # \quad\blacksquare
    body = _re.sub(r'\\quad\\blacksquare', '', body)
    body = _re.sub(r'\\quad\\square', '', body)

    return body


def auto_table_fix(body):
    r"""Auto-adjust table formatting based on cell length and column/row counts.

    Rules (in priority order):
      1. >20 rows → preserve longtable
      2. max cell length < 25 → tabular (no wrapping needed)
      3. 25 ≤ max cell length < 80 → tabularx{\textwidth}, last column = X
      4. max cell length ≥ 80 → tabularx{\textwidth}, all X columns
      5. >8 cols → additionally wrap with \footnotesize + \resizebox
    """
    def _clean_cell(cell):
        """Strip LaTeX markup to approximate visible text length."""
        # Replace math modes with length-proportional placeholder
        # (pure XX loses width info for long math expressions)
        def _math_placeholder(m):
            inner = m.group(1)
            # Strip LaTeX commands within math too, so \mathbb{C} → C
            # and \oplus → (removed).  Keeps braces, digits, letters.
            prev = None
            while prev != inner:
                prev = inner
                inner = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', inner)
                inner = re.sub(r'\\[a-zA-Z]+', '', inner)
            inner = re.sub(r'[\{\}]', '', inner)
            return 'X' * max(2, len(inner))
        cell = re.sub(r'\$([^$]*)\$', _math_placeholder, cell)
        cell = re.sub(r'\\\((.+?)\\\)', _math_placeholder, cell)
        cell = re.sub(r'\\\[(.+?)\\\]', _math_placeholder, cell, flags=re.DOTALL)
        # Iteratively strip commands with brace-balanced args (handles \frac{x}{y})
        prev = None
        while prev != cell:
            prev = cell
            cell = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', cell)
            cell = re.sub(r'\\[a-zA-Z]+', '', cell)
        # Normalize pandoc-escaped characters: \_ → _, \{ → {, etc.
        for ch in '{}_[]#$%&':
            cell = cell.replace('\\' + ch, ch)
        cell = cell.replace(r'\textbackslash', '\\')
        cell = cell.replace('{', '').replace('}', '')
        return cell.strip()

    def _measure_cells(table_body):
        """Measure max text length per column from data rows.

        Pandoc longtable structure:
          \\toprule ... \\midrule \\endhead  ← header
          \\bottomrule \\endlastfoot          ← footer
          <data rows>                         ← what we measure
        """
        # Skip header and footer, keep only data rows
        m = re.search(r'\\endlastfoot\s*\n?', table_body)
        if m:
            body = table_body[m.end():]
        else:
            m = re.search(r'\\endhead\s*\n', table_body)
            body = table_body[m.end():] if m else table_body

        col_max = {}
        for row in body.split(r'\\'):
            cells = row.split('&')
            for i, cell in enumerate(cells):
                clean = _clean_cell(cell)
                if i not in col_max or len(clean) > col_max[i]:
                    col_max[i] = len(clean)
        return col_max

    def _count_cols(spec):
        """Count columns from a column specification (already brace-stripped)."""
        inner = spec.strip()[1:-1]  # strip outer { }
        inner = inner.replace('@{}', '')
        p_cols = len(re.findall(r'>\{[^}]*\}p\{[^{}]*(?:\{[^}]*\}[^{}]*)*\}', inner))
        if p_cols > 0:
            return p_cols
        return len(re.findall(r'[lrc]', inner))

    def _count_data_rows(table_body):
        """Count data rows (after \\endlastfoot in pandoc longtable format)."""
        m = re.search(r'\\endlastfoot\s*\n?', table_body)
        if m:
            body = table_body[m.end():]
        else:
            m = re.search(r'\\endhead\s*\n', table_body)
            body = table_body[m.end():] if m else table_body
        return len(re.findall(r'\\\\', body))

    def _strip_longtable_cmds(text):
        """Remove longtable-specific commands and restructure for tabular.

        Pandoc longtable structure:
          \\toprule ... \\midrule \\endhead  ← header
          \\bottomrule \\endlastfoot          ← footer (last page only)
          <data rows>

        Tabular structure:
          \\toprule ... \\midrule  ← header
          <data rows>
          \\bottomrule             ← moved to end
        """
        parts = re.split(r'\\endhead\s*\n?', text, maxsplit=1)
        header = parts[0] if len(parts) > 0 else ''
        rest = parts[1] if len(parts) > 1 else ''

        parts2 = re.split(r'\\endlastfoot\s*\n?', rest, maxsplit=1)
        footer = parts2[0].strip() if len(parts2) > 0 else ''
        data = parts2[1] if len(parts2) > 1 else ''

        bottom_rule = ''
        m = re.search(r'\\bottomrule[^\n]*', footer)
        if m:
            bottom_rule = m.group(0)

        result = header.rstrip() + '\n' + data.rstrip()
        if bottom_rule:
            result += '\n' + bottom_rule
        return result

    def _extract_braces(text, start):
        """Extract brace-balanced substring starting at position start.
        Returns (substring, end_position)."""
        if start >= len(text) or text[start] != '{':
            return '', start
        depth = 1
        i = start + 1
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        return text[start:i], i

    def _find_tables(text):
        """Locate all \\begin{longtable}...\\end{longtable} blocks.
        Returns list of (full_match, spec, body_content)."""
        tables = []
        pos = 0
        tag = r'\begin{longtable}'
        end_tag = r'\end{longtable}'
        while True:
            idx = text.find(tag, pos)
            if idx == -1:
                break
            brace_start = text.find('{', idx + len(tag))
            if brace_start == -1:
                break
            spec, spec_end = _extract_braces(text, brace_start)
            end_idx = text.find(end_tag, spec_end)
            if end_idx == -1:
                break
            body_content = text[spec_end:end_idx]
            full = text[idx:end_idx + len(end_tag)]
            tables.append((full, spec, body_content))
            pos = end_idx + len(end_tag)
        return tables

    tables = _find_tables(body)
    if not tables:
        return body

    for full, spec, body_content in tables:
        n_cols = _count_cols(spec)
        n_rows = _count_data_rows(body_content)

        if n_rows > 22:
            # Preserve longtable but add centering via \centering
            replacement = r'{\centering' + '\n' + full + '\n' + r'\par}'
            if replacement != full:
                body = body.replace(full, replacement, 1)
            continue

        col_max = _measure_cells(body_content)
        max_len = max(col_max.values()) if col_max else 0

        inner = _strip_longtable_cmds(body_content)

        # Determine format based on cell length
        # For short cells (≤20 chars): tabular with original pandoc p-column spec.
        # Pandoc's p-column fractions are already correct for \textwidth
        # (they sum to ~1.0 of \linewidth - M\tabcolsep), so no adjustment needed.
        # For longer cells: tabularx with proportional column widths.
        if max_len <= 20:
            env_name = 'tabular'
            env_spec = spec
        else:
            env_name = 'tabularx'
            total = sum(col_max.values()) if col_max else 1
            # Compute per-column fractions, then scale so X gets ≥20%
            p_fracs = []
            for i in range(n_cols):
                cl = col_max.get(i, 0)
                if cl == max_len and max_len > 0:
                    p_fracs.append(None)  # X column
                else:
                    # Dynamic minimum: reserve extra width for row labels in
                    # five-column comparison tables.
                    if n_cols <= 4:
                        min_p = 0.125
                    elif n_cols == 5:
                        min_p = 0.11
                    else:
                        min_p = max(0.04, 0.40 / n_cols)
                    frac = max(min_p, min(0.32, cl / total * 1.2))
                    p_fracs.append(frac)
            p_sum = sum(f for f in p_fracs if f is not None)
            # Account for \tabcolsep gaps: each inter-column gap
            # costs ~2\tabcolsep ≈ 12pt ≈ 0.035 of \textwidth.
            # X must get ≥20% of \textwidth AFTER gaps are paid.
            gap_frac = (n_cols - 1) * 0.035
            max_p_sum = max(0.30, 0.75 - gap_frac)
            if p_sum > max_p_sum:
                scale = max_p_sum / p_sum
                for i in range(n_cols):
                    if p_fracs[i] is not None:
                        p_fracs[i] = max(min_p, p_fracs[i] * scale)
            parts = ['@{}']
            for i in range(n_cols):
                if p_fracs[i] is None:
                    parts.append(r'>{\raggedright\arraybackslash}X')
                else:
                    parts.append(r'>{\raggedright\arraybackslash}p{%.2f\textwidth}' % p_fracs[i])
            parts.append('@{}')
            env_spec = '{' + ''.join(parts) + '}'

        # Build table body without centering
        if env_name == 'tabularx':
            inner_replacement = (
                r'\begin{tabularx}{\textwidth}' + env_spec + '\n'
                + inner + '\n'
                + r'\end{tabularx}'
            )
        else:
            inner_replacement = (
                r'\begin{tabular}' + env_spec + '\n'
                + inner + '\n'
                + r'\end{tabular}'
            )

        # Tall tables → footnotesize to fit on one page
        if n_rows > 14:
            inner_replacement = (
                r'{\footnotesize' + '\n'
                + inner_replacement + '\n}'
            )

        # Long-cell tables → \small to reduce line-wrapping churn
        if max_len > 40:
            inner_replacement = (
                r'{\small' + '\n'
                + inner_replacement + '\n}'
            )

        # >8 cols → add resizebox wrapping
        if n_cols > 8:
            inner_replacement = (
                (r'{\footnotesize' + '\n' if n_rows <= 14 else '{')
                + r'\resizebox{\linewidth}{!}{' + '\n'
                + inner_replacement + '\n}}'
            )

        # Wrap with center
        replacement = (
            r'\begin{center}' + '\n'
            + inner_replacement + '\n'
            + r'\end{center}'
        )

        if replacement != full:
            body = body.replace(full, replacement, 1)

    return body


def _extract_braced_text(body, cmd):
    """Extract the text inside \\cmd{...}, handling multi-line content.
    Returns the extracted text (newlines collapsed to spaces) or None."""
    m = re.search(r'\\' + cmd + r'\{', body)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(body) and depth > 0:
        if body[i] == '{':
            depth += 1
        elif body[i] == '}':
            depth -= 1
        i += 1
    return re.sub(r'\s+', ' ', body[start:i-1]).strip()


def _process_figure_captions(body, is_ccs=False):
    """Add bold label to figure captions and suppress LaTeX auto-numbering.

    With ``\\captionsetup{labelformat=empty}``, LaTeX no longer prepends
    "Figure N:" -- the caption text IS the full caption.  We insert
    ``\\textbf{Figure \\thefigure.}`` at the start and strip any existing
    hand-numbered prefix (\\textbf{Figure X:}, \\textbf{Fig. X. ...}, etc.).

    For CCS documents the label prefix is ``CCS Figure C\\thefigure.``.
    """
    label_base = r'CCS Figure C' if is_ccs else r'Figure '

    def _clean_caption(text):
        """Strip old hand-numbered prefix if present."""
        text = text.strip()
        # Case 1: \\textbf{Figure N:} or \\textbf{Figure N. Title.}
        text = re.sub(r'^\\textbf\{Figure\s+\d+[:.]?\s*(?:[^}]*?\.\s*)?\}', '', text)
        # Case 2: \\textbf{Fig. N. Title.}
        text = re.sub(r'^\\textbf\{Fig\.\s+\d+\.\s*[^}]*?\}', '', text)
        # Case 3: \\emph{Figure N: Title}
        text = re.sub(r'^\\emph\{Figure\s+\d+:\s*[^}]*?\}', '', text)
        # Case 4: Plain "Figure N:" or "Figure N: Title" (Paper III style)
        text = re.sub(r'^Figure\s+\d+:\s*(?:\S[^:]*?:)?', '', text)
        # Case 5: "(CCS Fig. CN)" or "(CCS Fig. C12b)" prefix in parens
        text = re.sub(r'^\s*\(CCS Fig\.\s*C[\da-z]+\)\s*', '', text)
        return text.strip()

    def _extract_caption(m):
        """Extract caption content handling nested braces."""
        start = m.end()  # position after \\caption{
        depth = 1
        i = start
        while i < len(body) and depth > 0:
            if body[i] == '{':
                depth += 1
            elif body[i] == '}':
                depth -= 1
            i += 1
        return body[start:i-1]

    # Process each includegraphics + caption pair.
    # Pattern: \includegraphics (optionally braced), then \caption on following line
    # (possibly with \centering in between).
    fig_pat = re.compile(
        r'\{?\\includegraphics\[[^\]]*\]\{[^}]*\}\}?\s*\n(?:\s*\\centering\s*\n)?\s*\\caption\{',
        re.MULTILINE,
    )

    def _replace_match(m):
        fig_line = m.group(0).rstrip()  # includegraphics line + \caption{
        fig_line = fig_line[:fig_line.rfind(r'\caption{')]  # strip \caption{
        # The \caption{ was at end of match; extract braced content
        cap_start = m.end()  # after \caption{
        depth = 1
        i = cap_start
        while i < len(body) and depth > 0:
            if body[i] == '{':
                depth += 1
            elif body[i] == '}':
                depth -= 1
            i += 1
        content = body[cap_start:i-1]

        # Also match and remove any trailing \\label{...} after the caption
        suffix = ''
        remaining = body[i:].lstrip()
        lbl_m = re.match(r'\\label\{[^}]*\}', remaining)
        if lbl_m:
            suffix = '\n' + lbl_m.group(0)
            i += len(lbl_m.group(0))
        else:
            # Auto-generate \\label{fig:STEM} from the figure filename
            fn_matches = re.findall(r'\{([^}]+)\}', fig_line)
            for fn in reversed(fn_matches):
                if re.search(r'\.(png|pdf|jpg)$', fn, re.I):
                    stem = os.path.splitext(os.path.basename(fn))[0]
                    stem = stem.replace('_', '-')
                    suffix = f'\n\\label{{fig:{stem}}}'
                    break

        cleaned = _clean_caption(content)
        if not cleaned:
            cleaned = content  # fallback: keep original if cleaning emptied it

        # For CCS figures, extract fixed C-number from filename:
        #   fig_c0_... → C0, fig_c10_... → C10, fig_c12b_... → C12b
        # Falls back to caption text "(CCS Fig. CN)" → CN.
        # This replaces \\thefigure so PDF labels match source references.
        if is_ccs:
            c_num = None
            fn_m = re.search(r'fig_c([\da-z]+)_', fig_line)
            if fn_m:
                c_num = fn_m.group(1)
            else:
                cap_m = re.search(r'CCS Fig\.\s*C([\da-z]+)', content)
                if cap_m:
                    c_num = cap_m.group(1)
            label = f'{label_base}{c_num}.' if c_num else f'{label_base}\\thefigure.'
        else:
            label = label_base + r'\thefigure.'

        return f'{fig_line}\\caption{{\\textbf{{{label}}} {cleaned}}}{suffix}'

    # We can't use re.sub with a function that scans ahead, so process iteratively
    result = []
    pos = 0
    for m in fig_pat.finditer(body):
        result.append(body[pos:m.start()])
        result.append(_replace_match(m))
        pos = m.end()
        # Find matching } — skip past caption and optional label
        depth = 1
        while pos < len(body) and depth > 0:
            if body[pos] == '{':
                depth += 1
            elif body[pos] == '}':
                depth -= 1
            pos += 1
        # Skip past optional \\label{...}
        remaining = body[pos:].lstrip()
        lbl_m = re.match(r'\\label\{[^}]*\}', remaining)
        if lbl_m:
            pos += len(body[pos:]) - len(remaining) + len(lbl_m.group(0))
    result.append(body[pos:])
    return ''.join(result)


def _apply_figure_placement(body):
    """Apply conservative placement options to pandoc figure floats.

    Most figures should remain floats, but LaTeX's default figure placement can
    omit "here" and drift away from the introducing paragraph.  We use [htbp]
    by default and force only explicitly listed, locally explanatory figures
    with [H].
    """
    fig_pat = re.compile(
        r'\\begin\{figure\}(?:\[[^\]]*\])?.*?\\end\{figure\}',
        re.DOTALL,
    )

    def _replace(m):
        block = m.group(0)
        label_m = re.search(r'\\label\{([^}]+)\}', block)
        label = label_m.group(1) if label_m else ''
        placement = 'H' if label in PINNED_FIGURE_LABELS else 'htbp'
        return re.sub(
            r'\\begin\{figure\}(?:\[[^\]]*\])?',
            rf'\\begin{{figure}}[{placement}]',
            block,
            count=1,
        )

    return fig_pat.sub(_replace, body)


def process(input_path, output_path, title, author='WuJun Chen'):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    di = content.find(r'\begin{document}')
    de = content.find(r'\end{document}')
    if di == -1:
        print(f"ERROR: {input_path}")
        return

    body = content[di + len(r'\begin{document}'):de]

    # ── Extract header info for custom title block (before stripping) ──
    is_ccs = 'ccs' in input_path.lower()
    is_late_sof = any(
        name in input_path.lower()
        for name in ('paper11', 'paper12', 'paper13', 'paper14')
    )
    paper_match = re.search(r'paper(\d+)', os.path.basename(input_path).lower())
    paper_number = int(paper_match.group(1)) if paper_match else None
    is_paper13 = paper_number == 13
    is_paper16 = 'paper16' in input_path.lower()
    is_paper17 = 'paper17' in input_path.lower()
    is_paper22 = 'paper22' in input_path.lower()
    is_paper23 = 'paper23' in input_path.lower()
    is_paper24 = 'paper24' in input_path.lower()
    is_paper25 = 'paper25' in input_path.lower()
    is_paper26 = 'paper26' in input_path.lower()
    is_paper27 = 'paper27' in input_path.lower()
    is_paper29 = 'paper29' in input_path.lower()
    title_block = None
    m_abs = re.search(r'\\subsection\{Abstract\}', body)
    if not is_ccs and m_abs:
        header = body[:m_abs.start()]
        title_block = {
            'title': _extract_braced_text(header, 'section') or title,
            'subtitle': (
                _extract_braced_text(header, 'subsubsection')
                or _extract_braced_text(header, 'subsection')
                or ''
            ),
            'author': 'WuJun Chen',
        }
        # Extract the optional italic program-context block.
        m_italic = re.search(r'\\emph\{', header)
        if m_italic:
            title_block['italic'] = _extract_braced_text(header, 'emph') or ''
    elif is_ccs:
        # CCS: extract title/subtitle/author before stripping
        ccs_title = _extract_braced_text(body, 'section') or title
        ccs_subtitle = _extract_braced_text(body, 'subsubsection') or ''
        title_block = {
            'title': ccs_title,
            'subtitle': ccs_subtitle,
            'author': 'WuJun Chen',
        }

    # Strip pandoc-generated title/author header block
    # Pattern: (blank) \section{title} (blank) \subsubsection{subtitle} (blank)
    #          \textbf{Author}∗ ... \subsection{Abstract}
    # Strategy: find \subsection{Abstract}, delete everything before it.
    # For CCS (no abstract), find the first \begin{center}\rule after the header
    # and delete everything before it.
    if m_abs:
        body = body[m_abs.start():]
    else:
        # CCS-style header: strip up to and including the first center rule
        m_rule = re.search(
            r'\\begin\{center\}\\rule\{0\.5\\linewidth\}\{0\.5pt\}\\end\{center\}',
            body)
        if m_rule:
            body = body[m_rule.end():]

    # Strip leading blank lines
    body = body.lstrip('\n')

    # Replacements
    body = body.replace(r'\pandocbounded{', '{')
    # Pandoc escapes ~ (intended as LaTeX non-breaking space) to \textasciitilde{}
    # in markdown.  Restore it: Theorem~\ref → proper non-breaking space, not tilde glyph.
    body = body.replace(r'\textasciitilde{}', '~')

    # Figure sizing: add width=\textwidth to includegraphics that lack it
    def _add_width(m):
        opts = m.group(1)
        rest = m.group(2)
        if 'width=' in opts:
            return m.group(0)
        return f'\\includegraphics[width=\\textwidth,{opts}]{{{rest}}}'
    body = re.sub(
        r'\\includegraphics\[([^\]]*)\]\{([^}]*)\}',
        _add_width,
        body,
    )

    body = body.replace(
        r'\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}',
        r'\medskip\noindent\hrulefill\medskip'
    )
    # Normalize figure paths to point to repo-root figures/ from output/tex/.
    # Papers (../../figures/X) and CCS (../figures/X) both resolve to
    # ../../figures/X relative to the default build directory.
    # ../figures/ is a substring of ../../figures/ — protect the latter first.
    body = body.replace('../../figures/', '\x00FIG\x00')
    body = body.replace('../figures/', '../../figures/')
    body = body.replace('\x00FIG\x00', '../../figures/')
    # Most legacy figures have a vector PDF companion. Papers XVII and XXVII
    # publish their raster diagrams directly and retain the declared PNG path.
    if not (is_paper17 or is_paper27):
        body = body.replace('.png', '.pdf')
    body = body.replace(r'\tightlist' + '\n', '')
    body = body.replace(r'\printbibliography' + '\n', '')
    # With --natbib, a terminal Markdown ``References {.unnumbered}`` heading
    # becomes an empty placeholder. The real bibliography is appended below.
    body = re.sub(
        r'\n*\\subsection\*?\{References\}(?:\\label\{[^}]+\})*\s*'
        r'(?:\\addcontentsline\{toc\}\{subsection\}\{References\}\s*)?'
        r'(?:\\protect\\phantomsection)?(?:\\label\{refs\})?\s*$',
        '',
        body,
    )

    # ── Process figure captions: strip old labels, add unified bold prefix ──
    body = _process_figure_captions(body, is_ccs=is_ccs)

    # Keep most figures near their introducing text while pinning only the
    # figures whose local paragraphs depend on immediate visual support.
    body = _apply_figure_placement(body)

    # Convert Unicode math chars to LaTeX math mode
    body = convert_unicode_math(body)

    # convert_unicode_math converts § to \S, producing \SII (undefined).
    # Insert {} so LaTeX parses \S{}II correctly, but do not corrupt
    # ordinary commands such as \Sigma.
    body = re.sub(r'\\S(?!igma)', r'\\S{}', body)

    # ── Promote headings so LaTeX section counter starts at 1 ──
    # pandoc maps: # → \section, ## → \subsection, ### → \subsubsection, #### → \paragraph
    # After stripping the title \section, body starts at \subsection → LaTeX would number 0.X
    # Promote largest-first to avoid double-promotion:
    #   \subsection → \section (##), \subsubsection → \subsection (###), \paragraph → \subsubsection (####)
    body = re.sub(r'\\(subsection)\{', r'\\section{', body)
    body = re.sub(r'\\(subsubsection)\{', r'\\subsection{', body)
    body = re.sub(r'\\(paragraph)\{', r'\\subsubsection{', body)

    # ── Normalize multi-line headings for downstream parsing ──
    body = _normalize_headings(body)

    # ── Theorem wrapping + label generation + cross-reference map ──
    lines = body.split('\n')
    out = []
    xref_map = {}  # {(type, number): label_slug}  e.g. {('theorem', '6.2'): 'thm:field-definition'}
    i = 0
    while i < len(lines):
        line = lines[i]
        result = match_thm(line)
        if result:
            env_type, number, name, slug = result

            # ── Peek ahead for explicit \label{type:slug} from markdown ──
            # Explicit labels in markdown override auto-generated slugs, giving
            # the author permanent control over canonical label names.
            label = f'{env_type}:{slug}'

            label_from_markdown = False
            label_on_next_line = False

            if lines[i].strip().startswith(r'\subsection'):
                peek = i + 1
                if peek < len(lines) and lines[peek].strip().startswith(r'\label{sec:'):
                    peek += 1
                if peek < len(lines) and lines[peek].strip().startswith(r'\label{') \
                        and not lines[peek].strip().startswith(r'\label{sec:'):
                    label = lines[peek].strip()[7:-1]
                    label_from_markdown = True
            else:
                # Bold-style: check if \label{...} follows \textbf{...} inline
                s = lines[i].strip()
                end_brace = s.find('}')
                if end_brace >= 0:
                    after_bf = s[end_brace + 1:].lstrip()
                    m_lab = re.match(r'\\label\{([^}]*)\}', after_bf)
                    if m_lab:
                        label = m_lab.group(1)
                        label_from_markdown = True
                # Also peek at next line for standalone \label{...}
                if not label_from_markdown and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    m_lab = re.match(r'\\label\{([^}]*)\}', next_line)
                    if m_lab:
                        label = m_lab.group(1)
                        label_from_markdown = True
                        label_on_next_line = True

            xref_map[(env_type, number)] = label

            # Preserve \] (display math close) if it was on the same line
            if lines[i].strip().startswith(r'\]'):
                out.append(r'\]')
                out.append('')

            # Emit \begin{env}[Name]\label{label}
            if name:
                out.append(r'\begin{' + env_type + r'}[' + name + r']')
            else:
                out.append(r'\begin{' + env_type + r'}')
            out.append(r'\label{' + label + '}')
            out.append(r'\noindent')
            out.append('')

            # Also strip the pandoc-generated \label{...} right after \subsection
            if lines[i].strip().startswith(r'\subsection'):
                i += 1
                # Skip the \label{sec:...} line that pandoc appends
                if i < len(lines) and lines[i].strip().startswith(r'\label{sec:'):
                    i += 1
                # Skip any explicit \label{...} (already consumed above)
                if i < len(lines) and lines[i].strip().startswith(r'\label{') \
                        and not lines[i].strip().startswith(r'\label{sec:'):
                    i += 1
            else:
                # Preserve body text on the same line after \textbf{...}
                s = lines[i].strip()
                end_brace = s.find('}')
                if end_brace >= 0 and end_brace + 1 < len(s):
                    after = s[end_brace + 1:].lstrip()
                    # Strip the parenthesized name if it was already captured
                    if name and after.startswith('(' + name + ')'):
                        after = after[len(name) + 2:]
                        if after.startswith('.'):
                            after = after[1:]
                        after = after.lstrip()
                    # Strip consumed inline \label{...}
                    after = re.sub(r'^\\label\{[^}]*\}\s*', '', after)
                    if after:
                        out.append(after)
                i += 1
                # If label was consumed from next line, strip it from that line
                if label_on_next_line and i < len(lines):
                    nxt = lines[i].strip()
                    rest = re.sub(r'^\\label\{[^}]*\}\s*', '', nxt)
                    if rest:
                        out.append(rest)
                    i += 1

            list_depth = 0
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith(r'\begin{enumerate}') or s.startswith(r'\begin{itemize}'):
                    list_depth += 1
                elif s.startswith(r'\end{enumerate}') or s.startswith(r'\end{itemize}'):
                    list_depth -= 1
                    if list_depth < 0:
                        list_depth = 0
                    if list_depth == 0:
                        out.append(lines[i])
                        i += 1
                        break
                if list_depth == 0 and end_here(lines[i]):
                    break
                if list_depth == 0 and (not lines[i].strip() and i+1 < len(lines) and
                    (end_here(lines[i+1]) or match_thm(lines[i+1]))):
                    break
                out.append(lines[i])
                i += 1
            while out and not out[-1].strip():
                out.pop()
            out.append(r'\end{' + env_type + '}')
            out.append('')
        else:
            # Handle multi-line \textbf{Type...} that spans lines
            s = line.strip()
            if s.startswith(r'\textbf{') and s.count('{') > s.count('}'):
                # Collect lines until braces balance
                depth = s.count('{') - s.count('}')
                j = i + 1
                while j < len(lines) and depth > 0:
                    depth += lines[j].count('{') - lines[j].count('}')
                    j += 1
                if depth == 0:
                    # Join with space to form a single logical line
                    joined = ' '.join(l.rstrip() for l in lines[i:j])
                    result = match_thm(joined)
                    if result:
                        env_type, number, name, slug = result

                        # Peek for inline \label{...} in joined line
                        label = f'{env_type}:{slug}'
                        brace_end = 0
                        d = 0
                        for idx, ch in enumerate(joined):
                            if ch == '{':
                                d += 1
                            elif ch == '}':
                                d -= 1
                                if d == 0:
                                    brace_end = idx
                                    break
                        after = joined[brace_end + 1:].lstrip()
                        if name and after.startswith('(' + name + ')'):
                            after = after[len(name) + 2:]
                            if after.startswith('.'):
                                after = after[1:]
                            after = after.lstrip()
                        m_lab = re.match(r'\\label\{([^}]*)\}', after)
                        if m_lab:
                            label = m_lab.group(1)
                            after = re.sub(r'^\\label\{[^}]*\}\s*', '', after)

                        xref_map[(env_type, number)] = label

                        if name:
                            out.append(r'\begin{' + env_type + r'}[' + name + r']')
                        else:
                            out.append(r'\begin{' + env_type + r'}')
                        out.append(r'\label{' + label + '}')
                        out.append(r'\noindent')
                        out.append('')

                        if after:
                            out.append(after)

                        i = j
                        # Collect body until end_here or next match
                        list_depth = 0
                        while i < len(lines):
                            ls = lines[i].strip()
                            if ls.startswith(r'\begin{enumerate}') or ls.startswith(r'\begin{itemize}'):
                                list_depth += 1
                            elif ls.startswith(r'\end{enumerate}') or ls.startswith(r'\end{itemize}'):
                                list_depth -= 1
                                if list_depth < 0:
                                    list_depth = 0
                                if list_depth == 0:
                                    out.append(lines[i])
                                    i += 1
                                    break
                            if list_depth == 0 and end_here(lines[i]):
                                break
                            if list_depth == 0 and (not lines[i].strip() and i+1 < len(lines) and
                                (end_here(lines[i+1]) or match_thm(lines[i+1]))):
                                break
                            out.append(lines[i])
                            i += 1
                        while out and not out[-1].strip():
                            out.pop()
                        out.append(r'\end{' + env_type + '}')
                        out.append('')
                        continue
            out.append(line)
            i += 1

    body = '\n'.join(out)

    # ── Cross-reference: unnumbered subsections as implicit theorems ──
    # Detect \subsection{N.M Name} and \label{name-slug}, then
    # search body for "Theorem N.M" / "Corollary N.M" and map to label.
    implicit_map = {}  # {N: {'theorem': label, 'corollary': label, ...}}
    for m in re.finditer(
        r'\\subsection\{(\d+(?:\.\d+)*)\s+([^}]*?)\}',
        body,
    ):
        number = m.group(1)
        name = m.group(2)
        slug = _label_slug(name)
        # Search for the pandoc label right after this subsubsection
        after = body[m.end():m.end() + 200]
        label_m = re.search(r'\\label\{([^}]*)\}', after)
        existing_label = label_m.group(1) if label_m else slug
        if number not in implicit_map:
            implicit_map[number] = {}
        implicit_map[number]['_label'] = existing_label
        implicit_map[number]['_name'] = name

    # For each implicit section number, check what types appear in body text
    for number, info in implicit_map.items():
        label_base = info['_label']
        for env_type, display in [('theorem', 'Theorem'),
                                   ('corollary', 'Corollary'),
                                   ('lemma', 'Lemma')]:
            # Check if "Type N" appears in body (not inside {} or after \)
            probe = re.search(
                r'(?<![\\{])' + re.escape(display) + r'\s+' + re.escape(number) + r'(?![-\w])',
                body,
            )
            if probe and (env_type, number) not in xref_map:
                # Strip existing type prefix from label_base to avoid
                # doubling (e.g. theorem: → theorem:theorem:).
                base = label_base
                for pfx in ['theorem:', 'lemma:', 'corollary:', 'definition:',
                            'remark:', 'proposition:', 'example:',
                            'thm:', 'lem:', 'def:', 'prop:', 'cor:']:
                    if base.startswith(pfx):
                        base = base[len(pfx):]
                        break
                label = f'{env_type}:{base}'
                xref_map[(env_type, number)] = label

    # ── Cross-reference replacement ──
    # Replace "Theorem 6.2" → "Theorem~\ref{thm:field-definition}"
    # Skip unnumbered entries (number='') — they have no numeric ref to replace.
    _numbered = {k: v for k, v in xref_map.items() if k[1]}

    for (env_type, number), label in sorted(
        _numbered.items(), key=lambda x: -int(x[0][1].split('.')[0])
    ):
        display = env_type.capitalize()
        pattern = (r'(?<![\\{])' + re.escape(display) +
                   r'\s+' + re.escape(number) + r'(?![-\w])')
        body = re.sub(pattern, f'{display}~\\\\ref{{{label}}}', body)

    # ── Section numbering restructure (before labels, so stripping is clean) ──
    body = _restructure_sections(body, is_ccs=is_ccs)

    # ── Section label generation ──
    body = add_section_labels(body)

    # ── Reference entry formatting: suppress paragraph indent on {[}N{]} entries ──
    body = re.sub(
        r'(?m)^(\s*)(\{\[\}\d+\{\]\})',
        r'\1\\noindent \2',
        body,
    )

    # ── Protect \emph{Proof.} inside table cells from conversion ──
    # Tables can contain literal "\emph{Proof.}" as descriptive text (e.g. Box
    # Conventions table in CCS).  _convert_inline_proof_remark would wrap these
    # in \begin{proof}...\end{proof}, which breaks tabularx/tabular alignment.
    _table_guards = {}
    _tg_counter = [0]

    def _guard_table_proofs(m):
        key = f'__TABLE_PROOF_GUARD_{_tg_counter[0]}__'
        _tg_counter[0] += 1
        _table_guards[key] = m.group(0)
        return key

    body = re.sub(
        r'\\begin\{(?:tabularx|tabular|longtable)\}.*?\\end\{(?:tabularx|tabular|longtable)\}',
        lambda m: re.sub(r'\\emph\{Proof\.?\}', _guard_table_proofs, m.group(0)),
        body,
        flags=re.DOTALL,
    )

    # ── Convert inline \textbf{Remark.} / \emph{Proof.} to amsthm environments ──
    body = _convert_inline_proof_remark(body)

    # ── Restore protected table proofs ──
    for key, value in _table_guards.items():
        body = body.replace(key, value)

    # ── Convert Proof/Remark/Example subsections to theorem environments ──
    body = _convert_proof_remark_environments(body)

    # ── Protect \ref/\cite inside section headings (moving arguments) ──
    # \ref, \cite, and \pageref are fragile commands.  Inside \section{...},
    # \subsection{...}, etc. they break in the .toc/.aux write, creating
    # "Label(s) may have changed" loops that never stabilise across reruns.
    _heading_pat = re.compile(r'(\\(?:section|subsection|subsubsection|paragraph)\*?\{)')
    def _protect_fragile_in_heading(line):
        if not _heading_pat.match(line.lstrip()):
            return line
        line = re.sub(r'(?<!\\)\\ref\{', r'\\protect\\ref{', line)
        line = re.sub(r'(?<!\\)\\cite\{', r'\\protect\\cite{', line)
        line = re.sub(r'(?<!\\)\\pageref\{', r'\\protect\\pageref{', line)
        return line
    body = '\n'.join(_protect_fragile_in_heading(l) for l in body.split('\n'))

    # ── Normalize theorem labels: stable 3-letter prefix + fix broken slugs ──
    body = _normalize_theorem_labels(body)

    # ── Auto table sizing ──
    body = auto_table_fix(body)

    # ── Center \#layers column (narrow terminal column, looks unbalanced raggedright) ──
    # 1. Header cell: \raggedright → \centering in the minipage containing \#layers
    body = body.replace(
        r'\begin{minipage}[b]{\linewidth}\raggedright' + '\n' + r'\#layers',
        r'\begin{minipage}[b]{\linewidth}\centering' + '\n' + r'\#layers',
    )
    # 2. Column spec: in the table containing \#layers, center the last column.
    #    Find \#layers, then work backwards to find and modify the column definition.
    idx = body.find(r'\#layers')
    if idx >= 0:
        # Search backwards for the start of the tabular containing this column
        tabular_start = body.rfind(r'\begin{tabular}', 0, idx)
        if tabular_start >= 0:
            # Find the last column definition before \toprule within this tabular
            toprule = body.find(r'\toprule', tabular_start, idx)
            if toprule >= 0:
                col_spec = body[tabular_start:toprule]
                # Find the last occurrence of >{\raggedright\arraybackslash} in this spec
                last_ragged = col_spec.rfind(r'>{\raggedright\arraybackslash}')
                if last_ragged >= 0:
                    abs_pos = tabular_start + last_ragged
                    body = (body[:abs_pos] +
                            r'>{\centering\arraybackslash}' +
                            body[abs_pos + len(r'>{\raggedright\arraybackslash}'):])

    # ── Abstract: add \noindent before bold label paragraphs ──
    # Between \section*{Abstract} and the next \section, add \noindent
    # before each \textbf{Problem.}, \textbf{Mechanism.}, etc.
    abs_match = re.search(r'\\section\*\{Abstract\}', body)
    if abs_match:
        abs_end = body.find(r'\section', abs_match.end())
        if abs_end < 0:
            abs_end = len(body)
        before = body[:abs_match.end()]
        abstract_zone = body[abs_match.end():abs_end]
        after = body[abs_end:]
        # Add \noindent before bold label paragraphs
        abstract_zone = re.sub(
            r'(\n\n)\\textbf\{(Problem|Approach|Results|Computational case study|Boundary|Implications)\.\}',
            r'\1\\noindent\n\\textbf{\2.}',
            abstract_zone,
        )
        body = before + abstract_zone + after

    # ── Strip manual QED markers (\blacksquare, \square) ──
    # amsthm's \begin{proof} provides □ automatically; all other environments
    # should have no end marker.  This pass removes any legacy manual markers.
    body = _strip_manual_qed(body)

    # ── CCS: allow \texttt content to break at character boundaries ──
    # Long API identifiers (e.g. CubieSpectralOperator().layer_keys) are
    # unbreakable in monospace; \seqsplit inserts \allowbreak between chars.
    if is_ccs or is_late_sof or is_paper17:
        body = re.sub(
            r'\\texttt\{([^}]+)\}',
            r'\\texttt{\\seqsplit{\1}}',
            body,
        )

    preamble = ARXIV_PREAMBLE
    # ── Cross-file references via xr ──
    # Papers that use explicit CCS labels load the CCS aux file. Revised Papers
    # I--VII have no external \ref targets, so loading the aux file would only
    # duplicate bibliography and section labels.
    has_no_ccs_xrefs = any(
        name in input_path.lower()
        for name in ('paper1', 'paper2', 'paper3', 'paper4', 'paper5', 'paper6', 'paper7')
    )
    xr_docs = [] if has_no_ccs_xrefs else ['ccs_arxiv']
    if not is_ccs:
        xr_lines = '\n'.join(
            r'\externaldocument{' + d + '}'
            for d in xr_docs
        )
        preamble += '\n' + xr_lines + '\n'

    if re.search(r'\\(?:citep|citet)\{', body):
        preamble += '\n' + r'\usepackage[numbers,sort&compress]{natbib}' + '\n'

    if is_ccs:
        preamble = preamble.replace(
            r'\newtheorem{theorem}{Theorem}[section]',
            r'\newtheorem{theorem}{Theorem}',
        )
        # Suppress LaTeX subsection numbering; CCS subsections carry their
        # own hardcoded Part-scoped identifiers (1.1, II.3, 0.5.1, etc.).
        preamble = preamble.replace(
            r'\usepackage{hyperref}',
            r'\setcounter{secnumdepth}{1}' + '\n' + r'\usepackage{hyperref}',
        )
        # Zero paragraph indent + light paragraph spacing (CCS only).
        preamble += '\n' + r'\setlength{\parindent}{0pt}' + '\n'
        preamble += r'\setlength{\parskip}{0.4em}' + '\n'
        # Allow \texttt content to break at character boundaries (CCS API tables).
        preamble += r'\usepackage{seqsplit}' + '\n'
        # PDF page headers for navigation (replaces removed markdown prefix).
        preamble += r'\usepackage{fancyhdr}' + '\n'
        preamble += r'\setlength{\headheight}{14pt}' + '\n'
        preamble += r'\pagestyle{fancy}' + '\n'
        preamble += r'\fancyhf{}' + '\n'
        preamble += r'\fancyhead[L]{RIME Computational Companion Archive}' + '\n'
        preamble += r'\fancyhead[R]{\thepage}' + '\n'
        preamble += r'\renewcommand{\headrulewidth}{0.4pt}' + '\n'
    elif is_paper22:
        # Paper XXII freezes a continuous main-result sequence
        # Theorem 1 -> Theorem 2 -> Corollary 3 -> Theorem 4 -> Theorem 5.
        # Auxiliary lemmas and definitions retain section-local numbering.
        preamble = preamble.replace(
            r'\newtheorem{theorem}{Theorem}[section]' + '\n'
            r'\newtheorem{lemma}[theorem]{Lemma}' + '\n'
            r'\newtheorem{proposition}[theorem]{Proposition}' + '\n'
            r'\newtheorem{corollary}[theorem]{Corollary}' + '\n\n'
            r'\theoremstyle{definition}' + '\n'
            r'\newtheorem{definition}[theorem]{Definition}' + '\n\n'
            r'\theoremstyle{remark}' + '\n'
            r'\newtheorem{remark}[theorem]{Remark}' + '\n'
            r'\newtheorem{example}[theorem]{Example}',
            r'\newtheorem{theorem}{Theorem}' + '\n'
            r'\newtheorem{corollary}[theorem]{Corollary}' + '\n'
            r'\newtheorem{lemma}{Lemma}[section]' + '\n'
            r'\newtheorem{proposition}[lemma]{Proposition}' + '\n\n'
            r'\theoremstyle{definition}' + '\n'
            r'\newtheorem{definition}[lemma]{Definition}' + '\n\n'
            r'\theoremstyle{remark}' + '\n'
            r'\newtheorem{remark}[lemma]{Remark}' + '\n'
            r'\newtheorem{example}[lemma]{Example}',
        )
    elif is_late_sof:
        # Long report identifiers, script paths, and the normative JSON schema
        # must remain readable without overflowing the page.
        preamble += r'\usepackage{seqsplit}' + '\n'
        preamble += r'\usepackage{fvextra}' + '\n'
        preamble += (
            r'\DefineVerbatimEnvironment{verbatim}{Verbatim}'
            r'{breaklines=true,breakanywhere=true,fontsize=\small}' + '\n'
        )
    elif is_paper17:
        # Long immutable digests and source-addressed artifact paths are part
        # of the reader-facing evidence surface and must remain breakable.
        preamble += r'\usepackage{seqsplit}' + '\n'
    final = preamble + '\n'
    final += r'\title{' + title + '}\n'
    final += r'\author{' + author + '}\n'
    final += r'\date{2026}' + '\n\n'
    final += (
        r'\hypersetup{pdftitle={' + title + r'},pdfauthor={' + author + r'}}'
        + '\n\n'
    )
    final += r'\begin{document}' + '\n\n'

    # ── Custom title block (papers) or standard maketitle (CCS) ──
    if title_block:
        final += r'\begin{center}' + '\n'
        final += r'{\LARGE\bfseries ' + title_block['title'] + r'\par}' + '\n'
        final += r'\vspace{0.3em}' + '\n'
        if title_block['subtitle']:
            final += r'{\large\itshape ' + title_block['subtitle'] + r'\par}' + '\n'
            final += r'\vspace{0.3em}' + '\n'
        final += r'\vspace{1.2em}' + '\n'
        final += r'{\normalsize ' + title_block['author'] + r'\par}' + '\n'
        final += r'\smallskip' + '\n'
        final += r'{\small Independent Researcher\par}' + '\n'
        final += r'{\small 2026\par}' + '\n'
        final += r'\end{center}' + '\n\n'
        if title_block.get('italic'):
            final += r'\medskip' + '\n'
            final += r'\noindent{\itshape ' + title_block['italic'] + r'}' + '\n'
            final += r'\medskip' + '\n\n'
    else:
        final += r'\maketitle' + '\n\n'

    final += body + '\n\n'
    if re.search(r'\\(?:cite|citep|citet|nocite)\{', body):
        paper_local_bib = None
        if paper_number is not None:
            paper_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                f'paper{paper_number}',
            )
            for filename in ('references-v1.bib', 'references-v1.0.bib'):
                candidate = os.path.join(paper_dir, filename)
                if os.path.isfile(candidate):
                    paper_local_bib = os.path.splitext(candidate)[0]
                    break
        if paper_local_bib:
            bibliography = os.path.relpath(
                paper_local_bib,
                os.path.dirname(os.path.abspath(output_path)),
            ).replace(os.sep, '/')
            final += r'\bibliography{' + bibliography + '}' + '\n\n'
        elif is_paper13:
            final += r'\begingroup\small' + '\n'
            trilogy = os.path.relpath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trilogy'),
                os.path.dirname(os.path.abspath(output_path)),
            ).replace(os.sep, '/')
            final += r'\bibliography{' + trilogy + '}' + '\n'
            final += r'\endgroup' + '\n\n'
        else:
            trilogy = os.path.relpath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trilogy'),
                os.path.dirname(os.path.abspath(output_path)),
            ).replace(os.sep, '/')
            final += r'\bibliography{' + trilogy + '}' + '\n\n'
    final += r'\end{document}' + '\n'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final)
    print(f"  -> {output_path}")


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    base = os.path.abspath(
        os.environ.get(
            'RIME_TEX_OUTPUT_DIR',
            os.path.join(project_root, 'output', 'tex'),
        )
    )
    os.makedirs(base, exist_ok=True)
    for inp, out, title in [
        ('paper1.tex', 'paper1_arxiv.tex',
         'Spectral Sector Decomposition in the Rubik\'s Cube Representation'),
        ('paper2.tex', 'paper2_arxiv.tex',
         'Noncommutative Transport Topology in the Rubik\'s Cube Representation'),
        ('paper3.tex', 'paper3_arxiv.tex',
         'Support-Graph Reachability and Matrix-Composition Obstructions'),
        ('ccs.tex', 'ccs_arxiv.tex',
         'RIME Computational Companion Archive'),
    ]:
        process(f'{base}/{inp}', f'{base}/{out}', title)
    print("Done")
