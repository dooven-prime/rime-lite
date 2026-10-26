# Paper XVIII: A Path Is Not a State

**Version 1.0 release content; external DOI pending.** The canonical report source is
[Paper XVIII.md](Paper%20XVIII.md), with [Technical Notes and Reproduction
Details](TECHNICAL_NOTES.md). Accepted reader copies are
[the report PDF](paper18_arxiv.pdf) and
[the technical-notes PDF](paper18_technical_notes.pdf).

This is a report identity, not a claim of new general lumpability theory.
The signed unit-state criterion specializes classical block-row-sum
reasoning. The independent case-study result is the exact 163,439-source
predictive-profile census, including 90,148 somaSide successor classes,
the two-source rational certificate, and the coordinate-separation
analysis. Structural and reached-set comparisons retain the published
ownership of Papers XVI and XVII.

Preparation note: OpenAI Codex assisted with editing, typesetting, code
drafting, and preliminary checks. The author is responsible for the report's
mathematics, data interpretation, and reported results.

The [versioned Paper XVIII evidence index](https://github.com/dooven-prime/rime-lite/blob/paper18-v1.0/experiments/paper18/README.md)
distinguishes the deposited Dataset, the separate compact witness ZIP,
and inherited source packages. Its
[local release validator](../../experiments/paper18/validation/validate_release.py)
checks the exact historical Git commit, local bytes, focused controls, and
compact witness replay. The earlier
[JCN author-submission snapshot](../unnumbered/from_support_to_state/README.md)
is preserved unchanged; Paper XVIII is a shorter RIME report adapted from
it following editorial rejection.

From the repository root, rebuild the PDFs with:

~~~text
python papers/tex/build.py paper18
pandoc papers/paper18/TECHNICAL_NOTES.md --from markdown+tex_math_single_backslash --standalone --pdf-engine=xelatex -V geometry:margin=16mm -V fontsize=10pt -o output/tex/paper18_technical_notes.pdf
~~~

The default build writes generated files under output/tex; the two accepted
reader copies are synchronized into this directory after visual review.
The Git tag fixes the repository release content; the local receipt verifies
that closure. A Zenodo DOI and its downstream post-release anchor remain
separate and are not claimed by these artifacts.
