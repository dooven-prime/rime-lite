# Paper XLI: Registered Absorption Chains

This directory is the numbered, version 1.0 reader edition of
*Registered Absorption Chains and Placement Fibers for a Circular Action
with an Adjacent Idempotent*. The manuscript, paper-local bibliography,
and reader PDF are the candidate publication files. No Zenodo DOI or
release tag is claimed yet.

The historical source is
`papers/unnumbered/circular_coalescence_counts/`, associated with the
submitted identifier `hal-05837829v1`. That identifier is retained as
submission history, not asserted to be an accepted HAL record. The
historical manuscript, HAL-targeted PDF, and the existing finite and
Lean companions remain unchanged. The edition/proof mapping and exact
source digests are in `experiments/paper41/evidence-map.v1.json`.

Build this edition from the repository root with:

```text
python -B papers/tex/build.py --output-dir output/tex/paper41 paper41
```

The manuscript proof is the authority for the all-parameter results.
The original finite replay covers `n=2..7`; the later Lean companion
checks the exact generated-summary count and its construction but does
not formalize the asymptotic growth corollary. The inherited companions
are indexed, not republished under a new proof identity.
