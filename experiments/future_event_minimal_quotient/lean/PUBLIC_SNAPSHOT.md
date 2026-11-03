# Future-Event Quotients: Lean Companion Source Snapshot

This is the versioned Lean 4.33.0 source companion to
[hal-05844771v1](https://hal.science/hal-05844771v1), not a revision of that
preprint. It proves the actual generated-state future-event classification,
the uniform distinguishing bound, the exact quotient count, and the separate
full-summary and asymptotic comparisons. The statements and their source
locations are indexed in [the theorem map](review/THEOREM_TO_SOURCE.md).

The complete source snapshot is tagged `future-event-lean-companion-v1.0`.
Its GitHub tag is the source identity. The source ZIP is now archived at
[Zenodo DOI 10.5281/zenodo.23914476](https://doi.org/10.5281/zenodo.23914476);
the [downstream source anchor](../lean-source-anchor.v1.json) binds the tag,
ZIP digest, deposited file, and record. The `PENDING` text retained in the
tagged snapshot and frozen theorem map records their pre-archive state;
neither HAL identifier identifies these later Lean files.

| Layer | Read-only replay from this directory |
|---|---|
| Finite classification and count | `python -B validate_companion.py` |
| Future-event asymptotic | `python -B analysis/validate_analysis.py` |
| Full-summary observer bridge | `python -B full_summary/validate_bridge.py` |
| Observer-growth comparison | `python -B comparison/validate_comparison.py` |
| Theorem-to-source map | `python -B review/build_theorem_map.py` |

In a full Git checkout, `--check-upstream-git`, `--check-owner-git`, and
`--check-git` additionally compare the mirrors with their historical commits.
The default commands also work from a standalone source archive.

The source archive includes all four frozen manifests and dependency reports,
their bound Lean sources, exact upstream mirrors, toolchain and Lake locks,
axiom audits, negative controls, and the two manuscript reference copies.
It excludes `.lake/` and Python caches. A verifier must obtain the pinned
Mathlib dependencies before replaying the Lean kernel checks.

The phrase "Unnumbered short-article draft" in
[`review/manuscripts/fixed-pair-source.md`](review/manuscripts/fixed-pair-source.md)
is part of the exact historical manuscript at commit `050cf8e`, not a claim
about its present publication status. The reference copy is retained to
check paper anchors without rewriting that published source identity.
