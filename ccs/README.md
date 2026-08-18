# RIME Computational Companion Archive (CCS v2.1)

**Computational Companion and Status Archive**

*Versioned Reproducibility Data, Computational Observations, Open Problems,
and Historical Records*

[![CCS v2.1 DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21988041.svg)](https://doi.org/10.5281/zenodo.21988041)
[![Historical combined-release DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21108197.svg)](https://doi.org/10.5281/zenodo.21108197)

CCS v2.1 is a versioned, non-paper companion archive. It retains selected
Paper I--III reproducibility pointers, computational observations, open
questions, revision history, and links to executable artifacts. It is
published as a standalone archive, not as a research paper.

The release PDF is a curated long-form archive reconstructed from the
2026-07-26 mother source. A separate concise Executive Guide is preserved for
quick navigation; it does not replace the archive data tables and provenance
appendices.

This archive is optional human-readable research companion material. It is not
a paper, theorem source, semantic authority, or prerequisite for Papers I--III.
Mathematical claims must be cited from the corresponding papers.

Papers I, II, and III are self-contained, independently maintained, and
published as separate Zenodo records. None uses CCS v2.1 as a mathematical
premise, definition source, executable certificate, or scholarly authority.

The current archive release is:

[RIME Computational Companion Archive, version 2.1](https://doi.org/10.5281/zenodo.21988041)

The previous version 2.0 record remains available at
[10.5281/zenodo.21616956](https://doi.org/10.5281/zenodo.21616956).

The immutable first-version record retains its historical title:

[The RIME Trilogy: Spectral, Transport, and Accessibility Structures in Finite Group Representations](https://doi.org/10.5281/zenodo.21108197)

That title describes the old release package, not the current RIME program
architecture. Current Papers I, II, and III are maintained independently.
Revision history is recorded in [`HISTORY.md`](../HISTORY.md).

## Current Scope

The live archive indexes optional companion material around Papers I--III:

- the 228-dimensional Rubik cubie representation;
- the standard 18-generator averaging operator;
- the six registered spectral layers;
- the nine QT/HT joint-spectral sectors;
- the direct transport matrix and noncommutative-support audit;
- numerical policies, figure provenance, and implementation notes;
- computational observations and open promotion questions;
- selected first-version history, explicitly marked historical or withdrawn.

Executable scripts and structured artifacts, not CCS prose, certify finite
computations reported by the papers. Paper-level claim status is controlled by
the corresponding manuscript.

The revised Paper III reconstructs its own nine projectors and 18 generator
matrices and exhaustively audits its projected products via:

```bash
python experiments/paper3/validation/composition_obstruction.py
```

No CCS table, archived detector, commutant claim, or first-version
accessibility interpretation is a premise of that paper.

## Reading Path

| Component | PDF | Source | Role |
|-----------|-----|--------|------|
| Paper I | [paper1_arxiv.pdf](../papers/paper1/paper1_arxiv.pdf) | [Paper I.md](../papers/paper1/Paper%20I.md) | Independent spectral paper |
| Paper II | [paper2_arxiv.pdf](../papers/paper2/paper2_arxiv.pdf) | [Paper II.md](../papers/paper2/Paper%20II.md) | Independent direct-transport paper |
| Paper III | [paper3_arxiv.pdf](../papers/paper3/paper3_arxiv.pdf) | [Paper III.md](../papers/paper3/Paper%20III.md) | Independent graph/operator-composition paper |
| CCS v2.1 | [ccs_arxiv.pdf](ccs_arxiv.pdf) | [canonical_specification.md](canonical_specification.md) | Optional non-paper data, observation, open-question, and history archive |

## Computational Support

The paper-owned producer and source-addressed observation identified above are
the public Paper III reproducibility surface. Cross-document consistency,
claim-contract, and cached-result checks are author-side release controls and
are intentionally excluded from the public CCS interface.

The CCS does not study cube solving, search heuristics, pruning tables,
sticker rendering, or neural solvers. The cube is used as a finite
representation-theoretic testbed. Published release metadata and the file
certificate are recorded in the
[Zenodo metadata snapshot](../docs/archive/dois/21988041.json). The historical
combined DOI is provenance only; CCS v2.1 is published independently at
`10.5281/zenodo.21988041`.
