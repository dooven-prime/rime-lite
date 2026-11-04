# Proper-Arc Registered Summaries: Lean 4 Companion

Lean sources for the finite classification and enumeration in
[Registered Proper-Arc Chains and Placement Fibers in a Circular Collapse
System, hal-05848115v1](https://hal.science/hal-05848115v1).

For every `n >= 3`, source offset `c : ZMod n`, and `2 <= r < n`, this
companion proves the classification of actual registration origins, actual
selected chains, actual placement fibres and complete generated summaries.
It derives the exact total and the absorption-length and packet-rank counts.
The domain is execution by chronological `p,d` words from the singleton seed.
The positive-complement fibre and the independent `k=0` phase fibre are both
included.

## Source and Version

The prepared version is **1.0**, with proposed tag
`proper-arc-lean-companion-v1.0`. No companion content commit, tag or Zenodo
DOI has yet been assigned by this preparation. This is a separate software
companion, not a revision of the HAL paper.

The [theorem-to-source map](THEOREM_TO_SOURCE_MAP.md) identifies the 17
selected theorem entries, their owning sources, frozen signatures and
transitive dependencies. The manuscript reference is an exact copy from
paper content commit `2a30449b9dc37a36b25b277ebc006515c2addb59`.

| Proved layer | Source directory |
|---|---|
| Explicit origin words and common clean boundary | `ProperArc/`, `interfaces/` |
| Every actual origin has a unique internal cut | `classification/` |
| Ternary decoder and actual clean witnesses | `chains/` |
| Every actual chain has a unique code | `converse/` |
| Actual fixed-origin/code placement fibres | `fibres/` |
| Dependent equivalence for complete actual summaries | `summary/` |
| Exact total, including the shortest complement | `counting/` |
| Absorption-length and packet-rank counts | `refinements/` |

Fixed-pair actual-type specialization and the generating-function/asymptotic
layer are outside this Lean version. The corresponding paper proofs are not
being withdrawn or reclassified.

## Final Acceptance Evidence

The final acceptance evidence is the completed
[isolated cold replay](cold_replay/RESULT.md): all nine owning validators and
94 tests passed with a newly downloaded Lean toolchain, newly acquired
locked dependency sources and a fresh official Mathlib compiled cache.
The 99 frozen inputs and all nine reports are unchanged.

The [source manifest](source-manifest.v1.json) binds that final receipt and
its evidence manifest by SHA-256. Its file inventory also binds the release
documentation and packaging utility. These are packaging records, not an
additional theorem-audit layer. The old freeze records retain their original
status and bytes.

This replay used a separate environment on the same Windows host. The
receipt records its original local source-overlay delivery and machine paths;
those paths are provenance, not runtime dependencies. A subsequent source tag
and archive DOI must be recorded downstream, without rewriting the receipt.

## Reproduce

Start with [REPRODUCING.md](REPRODUCING.md). The frozen recipe uses Lean
4.33.0, Mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`, Python 3.12+
and Windows x86-64. No `.lake/`, installed toolchain or compiled dependency
cache is shipped.

Two quick read-only checks, without a new kernel replay:

```powershell
python -B theorem_map.py
python -B cold_replay/verify_result.py --evidence cold_replay/results/isolated-windows-v1
```

## Reuse and Publication

The 38 generic modules under `upstream/RegisteredAbsorptionChains/` are exact
mirrors from commit `547848ce2305daf54f0e2df049a9d5372ffdcbdc`; their fixed-pair
origin is commit `050cf8ec11e3db263830b46ea95e4062b8e08869`.
[upstream-manifest.json](upstream-manifest.json) identifies every mirror.
The proper-arc proofs do not substitute the old fixed-pair total-count theorem.
`PROOF_PLAN.md` is retained as a work record; the theorem map and owning
manuscript determine coverage.

Code is under the included [MIT license](LICENSE). See
[CITATION.cff](CITATION.cff) for software citation metadata and
[RELEASE.md](RELEASE.md) for the prepared source-commit, tag and Zenodo handoff.
