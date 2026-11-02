# Registered Proper-Arc Summaries

**Status:** Deposited to HAL as [hal-05848115v1](https://hal.science/hal-05848115v1).
Public access is pending verification. No DOI, journal submission, or
all-parameter Lean certification is claimed for this snapshot.

## Reader and replication

- [Reader PDF](hal-v1/Chen_Registered_Proper_Arc_Summaries_HAL_preprint.pdf)
  (10 pages), [canonical manuscript](MANUSCRIPT.md), and
  [bibliography](references.bib).
- [Build script](build_hal.py): from the repository root, run
  `python papers/unnumbered/proper_arc_registered_summaries/build_hal.py`.
  It requires Pandoc, pdfLaTeX, and BibTeX, writes intermediates under `output/`,
  and uses a fixed PDF metadata epoch for byte-stable reconstruction.
- [Bounded controls](../../../experiments/proper_arc_registered_summaries/README.md)
  ([versioned GitHub source snapshot](https://github.com/dooven-prime/rime-lite/tree/proper-arc-summaries-source-v1.0/experiments/proper_arc_registered_summaries)):
  run `python -B experiments/proper_arc_registered_summaries/validate_controls.py`
  from the repository root. The validator checks its own source/result
  digests and replays complete generated logs for `n=3..6` and the origin
  words for `n=3..7`.

The main result is a dependent bijection for all *generated* complete
summaries of a fixed proper source arc. Each origin cut, selected-chain
code, and compatible placement parameter is realized by a single continuous
chronological `p,d` execution. The construction and inverse in Theorem 5.3
own this all-parameter claim; the bounded controls are consistency checks.
The controls and their provenance are documented here rather than in the
mathematical reader PDF.
The fixed-pair specialization uses the earlier
[HAL preprint](https://hal.science/hal-05837829v1) without changing it.

| Candidate file | SHA-256 |
|---|---|
| `MANUSCRIPT.md` | `057beff05b4a5fb94f3e857298e23b0f5119b3d33fc1e4e6b4dedeb0c08eda48` |
| `references.bib` | `19a78bc60125f09a2d56698197e3d35016dfd0e0ee42a8bb04d51028bf7d95e5` |
| `build_hal.py` | `8d1da018822811d379c16719f9d88439c739cda39fd9ee4cff89752c3fa42402` |
| `hal-v1/Chen_Registered_Proper_Arc_Summaries_HAL_preprint.pdf` | `ead26aa0842546021e961c2eca3d71211190eb0a97eb8825b12e2cee6cc6d2bf` |
| `experiments/proper_arc_registered_summaries/control-manifest.v1.json` | `4d97871b16f5137858ccd2c5bff49688f02ad4beffa7d4f262cbfbf25afec3de` |

The internal proof review and earlier exploratory directory are not part of
this candidate's public replication closure. A later Lean companion may
formalize the all-parameter construction separately; its absence does not
turn the finite controls into a proof.
