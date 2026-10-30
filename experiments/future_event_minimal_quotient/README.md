# Future-Event Minimal Quotient: Bounded Controls

**Status:** versioned bounded-control source for the unnumbered manuscript
`papers/unnumbered/future_event_minimal_quotient/MANUSCRIPT.md`. The
manuscript and reader PDF are separate artifacts. This package establishes
only its declared finite replay, not an all-parameter theorem or Lean proof.

## Fixed domain

- `n=3,4,5`; source atoms and sites are `Z/nZ`, with identity singleton seed.
- Raw alphabet only: `p(q)=q+1 mod n` and `d(1)=0`, fixing other sites.
- The selected source pair is exactly `F={0,1}`. Registration and later
  selected absorptions retain full ordered parent blocks, kernel ports, and
  collision target. Unrelated fusions update the entire placement.
- Every retained state is reached by raw words. The finite graph has no word
  cutoff; the `n` range is the bounded control, not an all-`n` proof.

The state implementation in [model.py](model.py) stores one physical site per
source atom; its nonempty fibers are packets. [audit.py](audit.py) computes
the two exact *finite* right congruences by partition refinement, checks the
manuscript normal-form keys, and replays literal `V` and `W` probe words for
one representative of every candidate class pair. Partition refinement
ensures that this representative check covers the finite classes, not merely
sampled states.

| `n` | Retained states | Future classes | Full classes | Candidate pairs |
|---:|---:|---:|---:|---:|
| 3 | 30 | 10 | 16 | 45 |
| 4 | 176 | 65 | 89 | 2,080 |
| 5 | 920 | 336 | 486 | 56,280 |

The introduction's two `n=5` histories are replayed as actual raw words.
The saved [result](results/future_event_controls.v1.json) contains bounded
counts and probe-method totals, not a certificate for arbitrary `n`.

## Replay

Python 3.11+ and its standard library suffice. From the repository root:

```powershell
python -B experiments/future_event_minimal_quotient/validation/validate.py
python -B -m unittest discover -s experiments/future_event_minimal_quotient/tests -p test_controls.py -v
python -B experiments/future_event_minimal_quotient/produce.py
```

The last command prints a freshly computed JSON record without modifying
files. `produce.py --write` deliberately regenerates the saved record; that
changes a sealed byte if the computation changes and requires a new manifest.

The validator checks the source/result SHA-256 entries in
[control-manifest.v1.json](control-manifest.v1.json), recomputes the report,
replays one stored raw source word per state, and compares every raw edge
against a separately written packet-grouping update. It fails on drift or
disagreement. The producer and validator do not import the larger exploratory
tree. This is a local replay and consistency check, not independent review or
proof of the manuscript's all-`n` classification.

## Ownership boundary

The manuscript owns the all-`n` mathematical claims. The
[HAL registered-chain preprint](https://hal.science/hal-05837829v1) owns the
cited complete-summary count; its later Git snapshot is a different
artifact. This control package owns only its fixed finite replay.
A Lean companion is deferred and will state its own precise theorem coverage
and toolchain version. No unfinished Lean source is included in this closure.
