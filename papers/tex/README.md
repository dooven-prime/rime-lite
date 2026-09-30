# Build Pipeline

## Scope and Canonical Sources

The Markdown manuscripts under `papers/paperN/` are canonical paper sources;
`ccs/canonical_specification.md` is the source of the optional CCS v2 archive.
Generated TeX, PDF, log, auxiliary, and BBL files belong under `output/tex/`
and must not be edited by hand. This directory contains only build sources,
shared bibliography inputs, and documentation.

All papers are maintained independently within the RIME program. The build
pipeline does not define theorem dependencies. Current Papers I--III are not a
trilogy, revised Paper III has no CCS premise, and the legacy filename
`trilogy.bib` is only a compatibility path for the shared bibliography.

Papers I--VII are in maintenance mode. Rebuilds may implement errata, build
repairs, certificate repairs, or claim-boundary clarifications; they must not
silently change a frozen operator family, sectorization, branch, cutoff,
theorem spine, or numerical realization.

## Preferred Commands

Run builds from the repository root. For local reader-review builds:

```bash
python papers/tex/build.py paper1 paper2 paper3 paper4 paper5 paper6 paper7
python papers/tex/build.py paper13       # one paper
python papers/tex/build.py extras        # Papers IV--XIII
python papers/tex/build.py paper33       # one post-protocol theorem paper
python papers/tex/build.py --no-pdf      # legacy aggregate, TeX only
```

The build writes generated TeX, PDF, log, auxiliary, and BBL files under
`output/tex/`. After review, synchronize an
accepted reader copy explicitly to `papers/paperN/paperN_arxiv.pdf`; the build
entry point does not perform this copy.

Use `--output-dir PATH` for an isolated review build, or set
`RIME_TEX_OUTPUT_DIR`. The source directory `papers/tex/` must remain free of
generated build products.

The conversion path is:

```bash
Paper N.md -> pandoc -> output/tex/paperN.tex -> _postprocess.py
           -> paperN_arxiv.tex -> xelatex/bibtex -> paperN_arxiv.pdf
```

`build.py` with no target, and `build.py all`, retain the historical combined
order `ccs -> paper1 -> paper3 -> paper2`. This is a compatibility aggregate,
not the current public-release boundary and not a dependency statement. Build
`extras` separately for Papers IV--XIII. Papers XIV and XV remain direct
targets rather than aggregate members so their independently versioned
contracts and draft status are not hidden by the compatibility build.

### Legacy Combined-Release Packaging

`release_arxiv.py`, `prepare_arxiv.py`, and `package_arxiv_zips.py` package
only CCS and Papers I--III for compatibility with the immutable first combined
release. They are not the release mechanism for Papers IV--XIII.

```bash
python papers/tex/release_arxiv.py --check-only
python papers/tex/release_arxiv.py --version v1
python papers/tex/package_arxiv_zips.py --version v2
```

The ZIPs contain package contents at archive root, without an extra top-level
directory. Copied auxiliary files and `xr_sources/` preserve the historical
upload layout only.

## Manuscript Contract

### Reader-Facing Sections

The preferred abstract sequence is:

```text
Problem -> Approach -> Results -> [Computational case study] -> Boundary
```

Use `Computational case study` only when separating a finite registration from
the general result materially improves claim discipline. A symbols-only
section is `Notation`; a section that also declares object and evidence layers
is `Notation and Claim Layers`. Use `Claim Status and Boundary` for the claim
summary and `Related Work and Novelty Boundary` for literature positioning.

Do not add a prose `## References` section to current manuscripts. Citations
produce a formal BibTeX `References` section automatically. The old conversion
from a hand-authored `References` section to `Bibliographic Notes` remains only
for legacy source compatibility.

Executable support is indexed once, in the final
`Appendix X: Computational Artifacts`. Follow the Papers XI--XII convention:
declare the paper-local default directory, assign stable appendix artifact IDs,
and use a three-column `Artifact | Role | Short path` table. Main-text sections
refer to artifact roles or IDs rather than repository paths. Do not add a
separate `Code Availability` section or place command/path tables in the main
text. Give one repository-root execution template after the table, and list
generated `results/` records separately from executable `validation/` scripts.
Use the reader-facing sentence "All listed artifacts are available in the RIME
repository"; neither the table heading nor the repository label should repeat
the current paper number or distinguish public and private repository state.

Public manuscripts state hypotheses, evidence status, reproducibility
requirements, corrections, and open mathematical boundaries directly. Keep
freeze status, migration history, internal archive routing, release workflow,
and author-side planning in repository governance documents rather than paper
prose. Cross-paper citations should describe the neighboring mathematical
object; avoid series-navigation language unless a genuine technical dependency
must be disclosed.

Treat neighboring papers as typed interfaces rather than a linear chain. Every
manuscript remains locally readable and redeclares the object and hypotheses it
uses. A sentence such as "the incidence criterion of \cite{paper7} applies to
the declared factors $A,B$" is acceptable; "Paper VII completes the preceding
accessibility layer" is not. Bibliographic compatibility never substitutes for
a local promotion theorem or computational certificate.

Forward-looking research seeds appear only at the end of the Introduction, in
a Boundary or Promotion Limits section, or in the Conclusion/Research Program.
Do not place future concepts in theorem statements, and do not present a
research program as an established abstract result.

### Versioned Bibliography Identities

A BibTeX key identifies a versioned publication object, not only a paper
number. Within one record, the title, semantic scope, version note, and DOI
must refer to the same immutable object. For Papers IV--VII, keys
`paper4v1`--`paper7v1` identify the historical Zenodo releases, while
`paper4`--`paper7` identify the active v2 manuscripts and remain DOI-free until
those manuscripts receive new version-specific deposits. Never attach a v1 DOI
to an active v2 title or claim boundary.

### Claim Levels

Claim summaries use exactly four evidence levels:

1. `Theorem`
2. `Computational Certificate`
3. `Computational Observation`
4. `Research Program`

Lemma, Proposition, and Corollary are mathematical result types within the
Theorem level. `Computational Proposition` is a result label, not a fifth
claim level; it maps to Computational Certificate only when realization,
dtype, tolerance, registration, branch, rank/closure policy, artifact, and
reproducibility requirements are supplied.

### Rubik Terms

- `Rubik realization`: declared matrices, projectors, operator family, dtype,
  and numerical policy.
- `Rubik registration`: numerical clustering, matching, or identification
  inside that realization.
- `Computational Rubik case study`: paper-level use of the finite registered
  evidence.

These terms are not interchangeable. General theorems should precede the
Rubik case study unless the theorem itself concerns an explicitly declared
finite Rubik object.

### Papers XIII--XIV

The canonical source is `papers/paper13/Paper XIII.md`. A successful build
produces `paper13.tex`, `paper13_arxiv.tex`, and `paper13_arxiv.pdf` under
`output/tex/`; the reader copy is synchronized to
`papers/paper13/paper13_arxiv.pdf` when preparing a review snapshot.

Paper XIII uses the same late-SOF formatting path as Papers XI--XII. Its
machine-readable comparison-object contract is
`schemas/sofaudit/v1.0.schema.json`; Appendix A
summarizes contract semantics and intentionally does not duplicate the full
JSON schema. Validate the canonical contract and all current comparison
artifacts with:

```bash
python experiments/paper13/validate_sofaudit.py
python -m pytest tests/test_paper13_methodology.py -q
```

Regenerate the six main-text and two appendix figures with:

```bash
python experiments/paper13_figures.py
```

Paper XIV is built directly because its action-semantics contract has an
independent release identity and is excluded from the legacy aggregate. Its
semantic-factorization controls use:

```bash
python experiments/paper14/action_workbench.py
python experiments/paper14/validate_sofaction.py
python -m pytest tests/test_sof_action.py -q
```

Paper XV is also a direct build target. Its initial position draft is
theorem-and-interface only: it currently has no figure renderer, computational
census, or released wire schema.

The Paper XIII experiment layout is deliberately small:

```text
experiments/paper13/
├── *.py          # main domain audits, mathematical controls, validators
├── validation/   # secondary stability/discrimination/outlook controls
└── results/      # generated .sofreport, .sofaudit, and tables
```

## Tool Map

| Tool | Role | Writes |
|------|------|--------|
| `build.py` | Canonical local build entry point | generated `.tex`, `_arxiv.tex`, PDF/log artifacts |
| `_build.py` | Legacy-compatible build module used by `build.py` | same as `build.py` when run directly |
| `_postprocess.py` | Pandoc-TeX to arXiv-TeX transformer | output path passed by the build entry point |
| `_clean_hrule.py` | Normalize markdown `---` rules to `***`; imported by `_build.py` | only when run directly without `--check` |
| `_audit_tables.py` | Read-only table-shape diagnostic for generated TeX | none |
| `prepare_arxiv.py` / `release_arxiv.py` / `package_arxiv_zips.py` | Legacy CCS + Papers I--III packaging and validation | `output/arxiv/` package directories and release zips |

`_postprocess.py` is intentionally the only script that knows the detailed
LaTeX rewrite rules.  Helper scripts should not duplicate those rules unless
they are read-only audits.

Generated TeX, PDFs, logs, package directories, reverse conversions, and
registry diagnostics are not build sources. They remain under `output/` and
must not be moved back into this directory.

## `_postprocess.py` — Processing Passes (in order)

### 1. Header extraction
Extract title and subtitle from the pandoc-generated
`\section{Title}` / `\subsection{Subtitle}` or
`\subsubsection{Subtitle}` block before stripping. CCS
uses standard `\maketitle`; papers use a normalized author/affiliation/year
block and may extract one italic program-context paragraph.

### 2. Body preparation
- Strip pandoc-generated `\section{Title}` / `\textbf{Author}` header (keep from `\subsection{Abstract}` or first center rule)
- Replace `\pandocbounded{` → `{`
- Restore `~` non-breaking spaces: `\textasciitilde{}` → `~` (pandoc escapes tildes in markdown)
- Add `width=\textwidth` to `\includegraphics` that lack it
- Convert `\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}` (pandoc's `***`) → `\medskip\noindent\hrulefill\medskip`
- Normalize figure paths: unify `../figures/` and `../../figures/` → `../../figures/` (sentinel-protected), then `.png` → `.pdf`
- Strip `\tightlist`, `\printbibliography`

### 3. Figure captions (`_process_figure_captions`)
- Strip legacy hand-numbered prefixes (`Figure N:`, `Fig. N.`, `(CCS Fig. CN)`)
- Prepend `\textbf{Figure \thefigure.}` (or `\textbf{CCS Figure C\thefigure.}` for CCS) — the LaTeX counter provides the canonical number
- Auto-generate `\label{fig:STEM}` from the figure filename when no explicit `\label` follows the caption (e.g., `fig1_spectral_collapse.pdf` → `\label{fig:fig1-spectral-collapse}`)
- CCS figures get extra `C` prefix in the label: `CCS Figure C\thefigure.`
- Uses `\captionsetup{labelformat=empty}` so LaTeX suppresses its own "Figure N:" prefix — our bold prefix is the sole label

### 4. Unicode → LaTeX conversion
Convert Unicode math characters to LaTeX commands (protects verbatim + math blocks). Also fixes `\S` → `\S{}` to avoid `\SII` parsing error.

### 5. Heading promotion
Promote all headings one level (`\subsection→\section`, `\subsubsection→\subsection`, `\paragraph→\subsubsection`) so LaTeX section counter starts at 1. Largest-first to avoid double-promotion.

### 6. Heading normalization (`_normalize_headings`)
Join multi-line headings into single lines for downstream regex parsing.

### 7. Theorem wrapping + cross-reference map
Convert `\subsection{Theorem N (Name)}` and `\textbf{Theorem N (Name).}` into `\begin{theorem}[Name]\label{thm:name}`. Builds cross-reference map `{(type, number): label_slug}`. Handles 7 types: Theorem, Lemma, Proposition, Corollary, Definition, Remark, Example. Handles multi-line `\textbf{...}` spanning lines. Strips pandoc-generated `\label{sec:...}` after subsection headings. Marks `\label` explicitly given in markdown as author-controlled canonical labels. Adds `\noindent` after each `\begin{env}`.

Also detects implicit theorem labels from unnumbered `\subsection{N.M Name}` blocks (e.g., CCS) and maps body-text "Theorem N.M" references to the correct label.

### 8. Cross-reference replacement
Replace hardcoded "Theorem N.M" text in body with `Theorem~\ref{thm:...}` using the xref map. Sorted by descending section number to avoid partial matches (6.4 before 6.41).

### 9. Section restructuring (`_restructure_sections`)
- Abstract → `\section*{Abstract}` (unnumbered)
- Notation Table → `\section*{Notation Table}` (unnumbered)
- Legacy hand-authored References -> `\section*{Bibliographic Notes}`
  (unnumbered). Current manuscripts use `Related Work and Novelty Boundary`;
  citations generate the formal BibTeX References section.
- **CCS only**: Part sections → `\section*{Part …}` with `\refstepcounter{section}` + `\addcontentsline{toc}{section}{…}`
- Appendices: insert `\appendix` before first Appendix section, strip "Appendix X —" prefix
- Strip CCS bold identity markers (`**Part X — Title**` / `**Appendix X — Title**`) that precede matching `\section*{Part …}` / `\appendix` — these are markdown navigation aids, not printed headings

### 10. Section labels (`add_section_labels`)
Insert `\label{sec:…}` after every `\section`, `\subsection`, `\subsubsection` (including `*` variants). Protects `\texorpdfstring` in headings.

### 11. Reference entry formatting
Add `\noindent` before `{[}N{]}` reference entries (the pandoc compact enum format).

### 12. Table proof protection
Guard `\emph{Proof.}` inside `tabularx`/`tabular`/`longtable` from being converted to `\begin{proof}`. Prevents literal "Proof." text in table cells from breaking table alignment.

### 13. Inline proof/remark conversion (`_convert_inline_proof_remark`)
Convert remaining `\emph{Proof.}` and `\textbf{Type.}` at paragraph boundaries into `\begin{proof}` / `\begin{remark}` environments. Restore protected table proofs afterward.

### 14. Proof/Remark subsection conversion (`_convert_proof_remark_environments`)
Convert `\subsection{Proof}` / `\subsection{Remark N}` headings into `\begin{proof}` / `\begin{remark}` with their content.

### 15. Theorem label normalization (`_normalize_theorem_labels`)
Fix broken theorem label slugs — ensure stable 3-letter prefix (`thm:`, `lem:`, `prop:`, `cor:`, `def:`, `rem:`, `ex:`), strip doubled prefixes (`theorem:theorem:...`), and deduplicate conflicting labels within the same environment type.

### 16. Auto table sizing (`auto_table_fix`)
Replace pandoc `longtable` with `tabularx` (≤22 rows) or centered `longtable` (>22 rows). Dynamically computes column widths from content length. Short cells (≤20 chars) → `tabular` with original spec; longer cells → `tabularx{\textwidth}` with proportional `p{…}`/`X` columns. Also centers the narrow `\#layers` column (`\raggedright` → `\centering`).

### 17. Abstract formatting
Add `\noindent` before `Problem`, `Approach`, `Results`, optional
`Computational case study`, and `Boundary`. `Implications` remains recognized
only for legacy manuscripts.

### 18. QED stripping (`_strip_manual_qed`)
Remove manual `\blacksquare` / `\square` markers (amsthm `\begin{proof}` provides □ automatically).

### 19. CCS and late-SOF `\seqsplit` wrapping
For CCS and Papers XI--XIV, wrap `\texttt{…}` content with
`\seqsplit{…}` so long API identifiers, schema fields, and script paths break
at character boundaries in table cells. Late-SOF papers also enable
line-breaking verbatim environments.

### 20. Output assembly
- Build preamble with `ARXIV_PREAMBLE`, xr external documents (prefixed to prevent label collisions), and CCS-specific overrides
- Papers: custom `\begin{center}...\end{center}` title block (title, subtitle,
  normalized author, affiliation, year, and optional italic program context)
- CCS: `\maketitle`; papers use the custom title block
- Append `\bibliography{trilogy}` only when the processed body contains
  `\cite{...}` or `\nocite{...}`. The filename is legacy; the generated
  section is the formal References list.
- Append `\end{document}`

## CCS-Specific Differences

| Feature | Papers | CCS |
|---------|-----------------|-----|
| Theorem counter | `[section]` (Theorem 4.3) | Sequential (Theorem 1…13) |
| Subsection numbering | LaTeX auto-numbers | `\setcounter{secnumdepth}{1}` — only CCS identifiers visible |
| Paragraph style | Default (indent, no skip) | `\parindent=0pt`, `\parskip=0.4em` |
| Page headers | None | `\usepackage{fancyhdr}`, `\setlength{\headheight}{14pt}`, `\pagestyle{fancy}` — "Computational Supplement" left, page number right |
| `\texttt` breaking | Default (no breaks) | `\seqsplit` wrapping |
| Part sections | N/A | `\section*` (unnumbered) with `\refstepcounter{section}` |
| Title block | Custom centered | `\maketitle` |
| Figure label | `Figure \thefigure.` | `CCS Figure C\thefigure.` |

## Preamble

All generated papers and CCS share `ARXIV_PREAMBLE`
(`\documentclass[11pt]{article}`, geometry, amsmath, amsthm, amssymb,
hyperref, xr, booktabs, graphicx, caption, etc.).

CCS overrides: theorem counter (sequential), secnumdepth (1), parindent (0pt), parskip (0.4em), seqsplit, fancyhdr with headheight=14pt.

### Cross-file references (`xr`)

The shared preamble retains `xr` support for historical packages, but current
Papers I--VII build without `\externaldocument` declarations. Neighboring
papers are cited bibliographically; their theorem labels and auxiliary files
are not premises of the local manuscript.

Do not add a cross-paper `xr` edge merely to create narrative continuity. If a
future release genuinely requires one, declare it explicitly, prefix imported
labels to prevent collisions, document the build order, and package the exact
target `.aux` file. The legacy CCS + Papers I--III package still copies four
auxiliary files because its immutable upload layout predates this independent
paper policy.

## Theorem Styles

- `\theoremstyle{plain}` — Theorem, Lemma, Proposition, Corollary (bold label, italic body)
- `\theoremstyle{definition}` — Definition (bold label, roman body)
- `\theoremstyle{remark}` — Remark, Example (bold label, roman body)

All 7 types share a single counter sequence.

## Theorem Reference Formatting Convention

Formatting cases, consistent across all papers:

| Context | Weight | LaTeX source |
|---|---|---|
| Theorem / Lemma / Proposition heading | **Bold** | `amsthm` `plain` style (bold label, italic body) |
| Proof heading | **Proof.** bold | `amsthm` `proof` style |
| Remark / Example heading | **Bold** | `amsthm` `remark` style (bold label, roman body) |
| Running-text `Theorem 3.2` reference | Regular | Plain Markdown text -> regular LaTeX text |
| `\ref{thm:...}` number | Regular | Inherits surrounding text weight, never independently bold |

**Rule**: Theorem *statements* are bold (they are headings). Theorem *references* in running text are not bold. This is the standard convention in mathematical publishing and the semantic distinction is intentional — "I am stating a result" vs "I am citing a result."

### Markdown source

- Theorem heading: `### Theorem 3.6 (Name)` or `**Theorem 3.6 (Name).**` → wrapped to `\begin{theorem}[Name]`
- In-text reference: `By Theorem 3.2, we have…` → stays regular weight (pass 8 replaces hardcoded number with `\ref{thm:…}`)
- Self-reference within theorem heading: `**Lemma 1 (Lie-Generated Support Invariance).**` — bold because it's the statement itself

### `_postprocess.py` handling

- Pass 7 (Theorem wrapping): Converts `\subsection{Theorem N}` / `\textbf{Theorem N.}` → `\begin{theorem}` (bold from amsthm)
- Pass 8 (Cross-reference replacement): Replaces hardcoded `Theorem N.M` in body text with `\ref{thm:…}` — does NOT add `\textbf`, preserving regular weight
- Pass 13 (Inline proof/remark): Safety-net for any `\textbf{Type.}` not caught by pass 7; handles `\emph{Proof.}`

## Adding a New Paper

1. Add the Markdown source with title, subtitle, author, optional italic RIME
   program-context paragraph, `***`, and an abstract following the reader-facing
   sequence above.
2. Add a build entry to `_build.py` with `md`, `tex`, `arxiv`, and title paths.
3. Add the paper to an aggregate only if its release status warrants that
   inclusion; every paper must remain directly buildable by name.
4. Use bibliography entries for neighboring papers. Add `xr` only when an
   explicit, versioned cross-document label dependency is unavoidable.
5. Add paper-specific figure, schema, artifact, and validator commands to the
   owning paper or experiment README rather than expanding this file into a
   scientific claim register.

## Final PDF Checklist

Before synchronizing a reader PDF or recording a new frozen hash:

1. Build the named paper with `python build.py paperN`.
2. Check the final log for LaTeX errors, undefined citations/references,
   duplicate labels, overfull boxes, and underfull boxes.
3. Confirm fonts are embedded and visually inspect at least the title/abstract,
   representative theorem/table/figure pages, and the final References pages.
4. Confirm `Related Work and Novelty Boundary`, `Claim Status and Boundary`,
   and the formal `References` section each occur exactly once when applicable.
5. Run the smallest complete scientific validator suite covering the change.
   A prose-only maintenance edit does not require rerunning unrelated long
   experiments.
6. Synchronize the accepted PDF to `papers/paperN/` and record new source/PDF
   hashes in `HISTORY.md`. Never overwrite the adoption baseline in the Papers
   I--VII freeze contract.
