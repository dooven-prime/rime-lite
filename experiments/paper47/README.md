# Paper XLVII: selected reader and Lean companion

This package accompanies **Fusion Elimination and Exact History-Cost
Extrema on Stacked Rings**. It contains only the reader-owned
proof closure and reproducible entry points, not the exploratory programme.

- [Manuscript](../../papers/paper47/Paper%20XLVII.md) and [reader PDF](../../papers/paper47/paper47_arxiv.pdf)
- [Theorem-to-source map](THEOREM_MAP.md)
- [Scope and evidence boundary](SCOPE.md)
- [Selected-input manifest](candidate-manifest.v2.json)
- [Source copy provenance](lean/extraction-provenance.json)
- Local full replay receipt: `results/candidate-local-replay.v2.json`.

## Mathematical closure

For `n >= 3`, the entire actual one-block fibre has amplitude
`5*choose(n,2)+K_n-n+2`, where `K_n` is the attained maximum auxiliary
singleton-extraction cost. Lower fusion elimination and a shared upper
cursor cover all packet masses and legal interleavings. The extremal
structure theorem gives necessary conditions on the original actual log.

Section 8 proves the attained maximum over all all-upper observations equals
the same delayed benchmark. Whole-packet transfers, lower prefusions,
arbitrary ordered root forests and event interleavings are allowed. The
maximum is over the union of terminal ranks, not an equality at every
fixed rank or for every individual partition.

For singleton transfers and fused rank `2 <= r < n`, one actual witness pays
`length+(K_n-kappa_n(z(H)))+structuralDefect+choose(r-1,2)` within the
minimum cost of the same partition plus the delayed benchmark. The defect
combines within-root debt, cross-root debt and the cyclic gap moment.
The terminal route retains its actual moment saving and physical phase.
The whole-packet extension uses an independently attained packed lower
minimum and lower fusion elimination, not a fictitious singleton extraction
order for packets. Any global excess must have at least two terminal blocks
and a lower survivor.

## Reproduce

Required: Python 3.11+ and Git; for Lean, the exact toolchain and locked
dependencies; for PDF rebuilding, Pandoc, XeLaTeX and BibTeX with the fonts
and packages used by the numbered-paper TeX pipeline.

```sh
python -B experiments/paper47/validation/replay.py --verify-inputs-only
python -B -m unittest discover -s experiments/paper47/validation -p 'test_*.py'
cd experiments/paper47/lean
lake exe cache get
lake --no-cache build Paper47
cd ../../..
python -B experiments/paper47/validation/replay.py --lean --report /new/path/replay.json
```

`lake exe cache get` fetches the official compiled dependency cache for the
locked Mathlib sources. Do not run `lake update` or edit the lock. All
project-local libraries are mirrored inside this Lake root. No build reads
the source checkout, exploratory directories or another worktree.
`--lake /path/to/lake` chooses the pinned executable when it is not on PATH.
The report path must not already exist.

Lean is `leanprover/lean4:v4.33.0`; Mathlib is
`db584cd6d46c92f209a44c0f1c829460d327499d`. There are 195 byte-identical
mirrored Lean sources and one new combined import root. All 149 Lean files
in the earlier single-block candidate, including its entry/audit files,
remain byte-identical. The archived ancestor index is provenance only;
the active validator is `validation/replay.py`.

Paper-local `.gitattributes` preserve the exact mirror, bibliography and
ancestor bytes during Git materialization. The included `LICENSE` is an
unchanged copy of the repository license. These are packaging inputs,
not changes to the proof sources.

The audit menus remain separate: 25 one-block, 57 moment-route,
34 joint-forest and 25 all-upper
occurrences. Their union is counted separately in the manifest and replay
receipt; occurrences are not claimed to be distinct declarations. The
validator requires exact menu resolution and permits only `propext`,
`Classical.choice`, `Quot.sound`. Complete printed types are in the replay
receipt, grouped by the owning signature menu.

## Reader and archive

```sh
python -B experiments/paper47/validation/build_reader.py
python -B experiments/paper47/validation/package_candidate.py --output /new/path/paper47-candidate.zip
```

The archive preserves repository-relative paths and includes only manifest
inputs, the manifest and the local replay receipt. It excludes caches,
generated TeX/logs, exploratory notes and unrelated repository content.
`validation/stage_sources.py` records the mechanical extraction process;
it is not needed to reproduce the extracted package.

The [candidate CI workflow](../../.github/workflows/paper47-candidate.yml)
checks the selected bytes and tests, builds the locked Lean companion, and
uploads only a fresh successful runner receipt. It does not use the retained
local receipt as CI evidence.

This is local candidate iteration 2, not a published Paper XLVII version 2.
The earlier one-block/comb candidate and its archive remain unchanged.
The new worktree is based on verified remote commit
`43835de9ac21465412f80e8074fa8576f9a9b65c`. The recorded local build uses
a pinned installed dependency cache and compatible local project artifacts,
rechecked by Lake against the new sources. It is not an independent cold replay,
a GitHub-hosted acceptance or a public release. A candidate branch commit
does not assign a publication identity, tag, upload or submission.
