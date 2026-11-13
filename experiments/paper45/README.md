# Paper XLV evidence index

This index connects the first numbered Paper XLV manuscript to existing
proof owners. It does not reassign or mutate their accepted inputs. The
earlier C1 source tag is an unpublished Git source snapshot, not a HAL
publication or a prior numbered paper. Its byte identity and the detailed
statement map are in [FORMALIZATION_MAP.md](FORMALIZATION_MAP.md).

| Claim in Paper XLV | Proof owner | Scope |
| --- | --- | --- |
| Theorem 4.1 and Corollary 4.3: actual joint realization and quadratic budget | [M4-D](../fusion_log_compression/M4D_THEOREM_MAP.md), [M4-C](../fusion_log_compression/M4C_THEOREM_MAP.md) | All eligible ranks and packet starts under the declared `p,d` action |
| Theorem 5.2 and Proposition 5.3: dependent joint count and literal-endpoint log fibres | [M5](../fusion_log_compression/M5_THEOREM_MAP.md) | Actual log/endpoint objects, including rank one |
| Theorem 6.4, (6.9), Corollary 6.5: all-right minimum, surplus and unique literal word | [All-R](../fusion_log_compression/lean_all_r/README.md) | Specified complete ordered all-right log and literal endpoint, `n >= 3` |
| Section 7 and Corollary 8.1 | [Manuscript](../../papers/paper45/Paper%20XLV.md) | Paper proofs; not separate Lean interfaces |

The M5 layer has its own [Zenodo archive](https://doi.org/10.5281/zenodo.24123627).
That record does not contain the later All-R layer. The All-R source is
included in this numbered-paper candidate but has no separate archive or
independent cold-replay claim here. The finite controls are bounded checks,
not proofs of all-parameter statements.

## Bounded checks

Singleton-start enumeration for $3\le n\le6$ agrees with the joint
complete-log/literal-endpoint counts, including the initial empty log:

| Sites $n$ | Joint objects |
| --- | ---: |
| 3 | 39 |
| 4 | 292 |
| 5 | 2,505 |
| 6 | 24,306 |

The arbitrary-start control checks 65,992 joint objects across 36 layouts
of disjoint two-atom packets and all initial ranks in this size range. It
compares complete event lists, literal endpoints and the $K,M,B(n,t,s)$
budgets. The [saved control results](../fusion_log_compression/controls/results/)
and their [source](../fusion_log_compression/controls/) are inherited,
unchanged bounded evidence for Paper XLV.

## Read-only checks

From `experiments/fusion_log_compression/`:

```text
python -B validation/replay_m4d.py --verify-inputs-only
python -B validation/replay_m5.py --verify-inputs-only
python -B controls/fusion_log_arbitrary_start_control.py --max-n 6
python -B controls/audit_math.py
```

From `experiments/fusion_log_compression/lean_all_r/`, with the pinned Lean
4.33.0 and Mathlib dependencies available:

```text
lake --no-cache build
lake env lean FusionLogAllR/AxiomAudit.lean
```

The detailed [All-R README](../fusion_log_compression/lean_all_r/README.md)
distinguishes a warm build from an independent cold replay. The preserved
M4-D and M5 validators own their separate historical source locks and axiom
inventories. The [candidate gate](validation/validate_candidate.py) binds
the numbered manuscript, bibliography, PDF, evidence index and All-R source
inventory. It does not itself compile Lean or replay finite controls; the
[CI workflow](../../.github/workflows/paper45-candidate.yml) runs those
checks separately. No Paper XLV tag or DOI is claimed by this candidate.
