# Paper XLI Publication Evidence Index

This directory maps the numbered Paper XLI edition to its historical
source and existing computational companions. It adds publication
identity and candidate byte closure only; the proof-owner directories
`papers/unnumbered/circular_coalescence_counts/` and
`experiments/registered_absorption_chains/` are unchanged.

| Manuscript claim | Owner and evidence level |
|---|---|
| Lemma 2.2, actual fusion-free placement control | Manuscript proof; inherited Lean actual-word and cyclic-frame theorems |
| Theorem 3.1, complete selected-chain bijection | Manuscript proof; inherited Lean chain-range and clean-code induction |
| Theorem 4.2, fixed-chain placement fibers | Manuscript proof; inherited Lean fiber normal form and actual sufficiency |
| Theorem 5.1, exact total count | Manuscript proof; inherited Lean exact generated-summary count; bounded BFS for `n=2..7` |
| Corollary 5.2, asymptotic growth | Manuscript proof only; not formalized by the inherited Lean companion |

The historical `hal-05837829v1` identifier records a submission, not
an accepted HAL publication. The candidate edition has no DOI, content
tag, or downstream Zenodo anchor. See `evidence-map.v1.json` for
exact historical bytes and `release-manifest.json` for the new edition's
candidate closure. `release-environment.json` records the local reader
build and separates that visual check from the inherited Lean replay.

From the repository root, the existing read-only replays are:

```text
python -O -B experiments/registered_absorption_chains/independent_bfs_check.py --check-result experiments/registered_absorption_chains/results/independent_bfs_n2_n7.v1.json
python -B experiments/registered_absorption_chains/lean/validate_lean_package.py
```

If `lake` is not on `PATH`, set `RIME_LAKE_EXE` to the Lean 4.33.0
executable. The candidate validator checks the pinned source and edition
bytes; `--replay` additionally reruns both inherited controls.
The dedicated GitHub workflow `.github/workflows/paper41-candidate.yml`
checks the same candidate closure and retains its own runner receipt;
the local receipt is not a substitute for that run.
