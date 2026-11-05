# HAL Reader Build Profile

`papers/tex/build_hal.py` and `hal-reader-template.tex` are the shared build
path for new unnumbered HAL reader manuscripts. They do not replace the
historical build scripts or PDF bytes of already deposited preprints.

Run from the repository root:

```bash
python -B papers/tex/build_hal.py papers/unnumbered/fusion_log_compression
```

The manuscript directory supplies `MANUSCRIPT.md`, `references.bib`, and
`hal-reader.json`. Its configuration fixes the author, affiliation, preprint
date, output filename, and `SOURCE_DATE_EPOCH`. A paper-specific LaTeX header
may be named by the optional `header_file` field; it must remain inside that
manuscript directory. The byline in Markdown must match the configured
author, affiliation, and date. The configuration never supplies theorem text.
An optional `statement_keep_lines` map raises the page-space reservation for
one exactly named result; a missing or duplicated heading fails the build.

The source begins with a level-one title, bold author, byline, `## Abstract`,
and `**Keywords:**`, followed by consecutively numbered `## N. ...` sections.
`### Theorem/Lemma/Proposition/Corollary ...` headings remain explicitly
numbered statement labels, not auto-numbered subsections. Proofs use
`**Proof.**` and a final `$\square$`. Optional `## Appendix A. ...` headings
render with the full "Appendix A" prefix; manuscript equation tags such as
`(A.1)` are retained. A final empty `## References` heading is
replaced by the BibTeX bibliography. These checks fail rather than guessing
when a manuscript changes its source convention.

The fixed reader profile uses A4, 11 pt, 24 mm margins, Latin Modern,
`article` section numbering, a centered title block, a standard abstract
environment, a bold Keywords label, hidden link borders, `plainnat`
author-year references, and XeLaTeX. Pandoc converts Markdown/math to LaTeX;
BibTeX resolves references. Tagged display equations are placed in numbered
equation environments. The build fails on missing characters, unresolved
citations/references, BibTeX warnings, or overfull boxes above 0.5 pt.

Generated TeX and logs stay under `output/tex/<manuscript>/hal/`. A preview
copy is written under `output/pdf/`; the candidate PDF is written to
`<manuscript>/hal-v1/<pdf_name>`. A source/PDF digest receipt is written under
`<manuscript>/results/reader-build.hal-v1.json`. This receipt records a
reader build, not a HAL deposit or publication identity. Visual inspection
of the final PDF remains necessary before freezing or submitting it.
