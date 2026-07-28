# Paper III computational support

## Current v2 certificate

Run from the repository root:

```text
python experiments/paper3/validation/composition_obstruction.py
python tests/test_transport.py
```

A successful full run writes the review-facing observation artifact
`results/composition_obstruction.observation.json`. To inspect whether that
cached run still matches every explicitly declared source file without
repeating the matrix calculation, run:

```text
python experiments/paper3/validation/composition_obstruction.py --check-result
```

The check returns nonzero when the artifact is malformed, missing, or stale.
Use `--no-write-result` for a full audit that does not update the observation.
The JSON artifact is a cached human/AI observation layer with runtime, Git,
parameter, and source-hash provenance. It is not an independent proof and
does not replace a clean full rerun for release validation.

The certificate first audits the QH sector registration: pairwise operator
commutation, projector validity, completeness, joint invariance,
physical-block diagonality, and the nine-sector dimension census over declared
clustering tolerances. It then distinguishes two-step paths in the direct
support graph from nonzero projected products

```text
Q_i rho(g2) Q_k rho(g1) Q_j.
```

For the five canonical graph-only triples, both adjacent factors are nonzero
and every projected product over the 18 x 18 ordered generator pairs is
machine-zero.

Secondary v2 validators belong under `validation/`. The current regression is
`tests/test_transport.py`; no additional Paper III validator has yet been
promoted.

## Legacy v1 scripts

Scripts under `archive/` were written for the withdrawn T7 morphism
interpretation. They may reproduce frozen first-version graph, Lie, search,
generator-family, NCG, and persistence diagnostics, but they are not evidence
for the v2 Paper III theorem spine until individually migrated to
matrix-composition semantics. In particular, a reported two-step `K` path is a
support-graph path, not a compositional morphism.

Retired principal-log and T7 convenience helpers live in
`archive/spectral_utils.py`; they are intentionally absent from the active
`rime.spectral_utils` API. Archived scripts using relative imports must be
invoked as modules from the repository root, for example
`python -m experiments.paper3.archive.generator_defect_taxonomy`.

The current manuscript cites `validation/composition_obstruction.py` and
`tests/test_transport.py` as executable scientific support artifacts. The
cached JSON observation is a review aid for those artifacts.

Only the `validation/` path is active; historical releases retain their own
source snapshots.
