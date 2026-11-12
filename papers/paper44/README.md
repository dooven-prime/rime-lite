# Paper XLIV: Prefix-Memory Event Observers

This is an unreleased numbered reader candidate of *Prefix Memory and the
Growth Spectrum of Event Observers*. It has no Paper XLIV DOI, content tag,
publication anchor, or independent cold-replay receipt yet.

The [manuscript](Paper%20XLIV.md), [bibliography](references-v1.bib), and
[reader PDF](paper44_arxiv.pdf) form the candidate reading set. Build it from
the repository root with:

```text
python -B papers/tex/build.py --output-dir output/tex/paper44 paper44
```

This is the first numbered edition of a previously local, unnumbered draft;
the local draft path is not represented as a publicly retrievable historical
commit. Papers [XLI](../paper41/README.md) and [XLIII](../paper43/README.md)
are the published mathematical inputs. The former supplies actual registered
chains and placement fibres; the latter supplies future-event equivalence and
constructive separation. The numbered bibliography cites their Zenodo
editions, and the XLIII theorem reference follows that edition's numbering.

The exact finite quotient and its all-parameter structural equivalences have
a separately versioned [Lean proof milestone](../../experiments/paper44/lean/README.md).
The fixed-depth asymptotics, linear-memory spectrum, supercritical comparison,
and Gaussian critical window are manuscript proofs, not Lean-certified
results. [Bounded controls](../../experiments/paper44/controls/README.md)
check the complete partitions for `n=3..7`; they do not prove the limits.
The numbered [critical-window review](../../experiments/paper44/review/CRITICAL_WINDOW_REVIEW.md)
binds the current manuscript and PDF; the earlier unnumbered C1 review
does not describe the new Theorem 6.5.

The review record is included in the GitHub candidate
[release manifest](../../experiments/paper44/release-manifest.json), not as
a separate Zenodo reader file. A future content tag will identify the PDF
and bibliography while retaining this source-level review. Any later Lean
formalization of the analytic layer requires a separate companion milestone
or an explicitly versioned new paper edition.
