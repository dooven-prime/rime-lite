# A Path Is Not a State

This is the author-original version submitted to the *Journal of Complex
Networks* on 22 October 2026. It is not peer reviewed, accepted, or a new
numbered RIME paper. Papers XVI and XVII retain their separate published
claims and release identities.

## Read the submitted version

| Item | Location |
|---|---|
| Main manuscript PDF | [submitted author PDF](submitted/Chen_A_Path_Is_Not_a_State_JCN_reader.pdf) |
| Supplementary Information PDF | [submitted supplement](submitted/Chen_A_Path_Is_Not_a_State_JCN_supplement.pdf) |
| Manuscript source | [MANUSCRIPT.md](MANUSCRIPT.md), [references.bib](references.bib), [figures/](figures/) |
| Supplement source | [SUPPLEMENTARY_INFORMATION.md](SUPPLEMENTARY_INFORMATION.md) |
| Full predictive-profile Dataset | [Zenodo record](https://doi.org/10.5281/zenodo.23555888) and [Dataset guide](dataset/README.md) |
| Compact two-source certificate | [submitted witness ZIP](witness/malecns_two_source_witness_v1.0.zip) and [witness guide](witness/README.md) |

The PDFs above are the submitted author files, not ScholarOne's line-numbered
review proof. Their SHA-256 digests are:

| File | SHA-256 |
|---|---|
| Main manuscript PDF | `d984962a17e20049c9f4ede0410ed26dd36e04567ccb9476c9efa7d49216da84` |
| Supplement PDF | `12eaf81eb63efcedc15b4e04e7117adc00bb6a9d7c284975f42c619fd8705ea2` |
| Manuscript Markdown | `e3294e12cd60e28bbb18e04db536316bdffb914fcd90ab3f110f63b8373d5629` |
| Supplement Markdown | `2db155a315408716cb29730848a77509e895570005c7cf757625a15df49ccf24` |
| Submitted witness ZIP | `6ff8175d62b893f2f71c357ae51419727edc58aed160365fe8fb86a52feea2c9` |

## Evidence boundary

The [Dataset](dataset/README.md) owns the full-domain census and its large,
byte-pinned carrier. This Git checkout contains only small source, result,
figure, and manifest mirrors; it is **not** a standalone replacement for the
316 MB Zenodo archive. Download that archive to run its complete byte check
or source replay. The compact witness ZIP is separate and can be checked
without the large carrier; source extraction additionally consumes the
Dataset carrier. The Dataset DOI does not identify the witness ZIP: its
submitted bytes are bound by the separate SHA-256 value above, with no
separate witness DOI claimed.

The theorem concerns the declared signed, normalized, clipped update on
eligible unit sources. The census is an exact finite computation on that
carrier, not a claim about biological mechanism, all mixtures, or later-time
closure. [Paper XVI](https://doi.org/10.5281/zenodo.22931881) and
[Paper XVII](https://doi.org/10.5281/zenodo.23275058) own their earlier
structural and reached-set results.

The source can be rebuilt with `python papers/unnumbered/from_support_to_state/build_jcn.py`
using the repository's `papers/tex/` tooling and its documented external
dependencies. A fresh PDF build is a layout check, not a replacement for the
submitted PDF hashes above. Generated TeX and build output belong under
`output/` and are not part of this public source selection.
