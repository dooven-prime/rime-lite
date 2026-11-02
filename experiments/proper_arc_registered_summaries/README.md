# Proper-Arc Registered-Summary Controls

This is the paper-local bounded control package for the unnumbered
proper-arc preprint candidate. It is self-contained and uses only the
Python standard library (Python 3.11 or later). The owning manuscript is
`papers/unnumbered/proper_arc_registered_summaries/MANUSCRIPT.md`.
Repository path:
[RIME Lite / experiments/proper_arc_registered_summaries](https://github.com/dooven-prime/rime-lite/tree/proper-arc-summaries-source-v1.0/experiments/proper_arc_registered_summaries).

Run from the repository root:

```powershell
python -B experiments/proper_arc_registered_summaries/validate_controls.py
```

The entry point reads the manifest and fixed result, verifies SHA-256 for
every bound source/result file, and recomputes the following controls without
writing files:

- All generated full-log states for `n=3..6`, checking every proper source
  arc's origin count, ternary chain set, per-chain placement count, and total.
- The explicit chronological registration word for every proper arc, source
  start, and internal cut for `n=3..7`, checking its final origin record and
  common post-registration placement. The result records a digest of the
  ordered `(c,r,t,word)` list for each `n`.

`core.py` and `general_arc_control.py` are scoped extracts of the earlier
exploratory controls; `origin_control.py` is a focused replay of manuscript
equation (3.3). No script imports the exploratory tree. The only fixed
machine result is `results/proper_arc_controls.v1.json`; its content and
the code bytes are bound in `control-manifest.v1.json`.

The package is a bounded consistency control. The manuscript's all-`n`
origin, chain, fiber, and counting results are proved in the paper, not by
this replay. This local closure is not a release manifest or validation
receipt, and no public deposit identity is claimed.
