# P28.5i-j: Third Rank-Four Section Return

## Status

The frozen P28.5h carrier has passed the independently staged rank-four
section-to-base test. It now has fixed-scope authority as
`Sec_4,cand3^(7)`.

## Independence audit

Before constructing any menu, the 36 exact typed rank-four contexts were
compared with the 48 contexts of `Sec_4,cand2^(7)`. Their intersection is
empty. This audit did not alter candidate membership and did not read
`Good_4`.

```text
candidate3 contexts        36
Sec_4,cand2 contexts       48
typed intersection          0
```

Thus this is a new lower-section realization, not a replay of already
certified source contexts with a different carrier description.

## Frozen pre-evaluation relation

The future-free P28.5i constructor freezes:

```text
sources                    36
abstract channels         172
accounting refinements   1503
exact lifts              5239
maximum menu size           7
operation vocabulary       TRANSPORT / RETURN / FUSION
```

The exact stored histogram is:

```text
menu size 3 :  2 sources
menu size 4 : 11 sources
menu size 5 : 17 sources
menu size 6 :  5 sources
menu size 7 :  1 source
```

No recursive target is exported by this artifact. Of 13,997 replay states,
13,248 occur only internally, and none receives checkpoint authority.

## Independent Good_4 evaluation

Only after the construction digest was frozen did P28.5j evaluate exact
low-rank success:

```text
successful sources          36 / 36
successful channels        171 / 172
successful exact lifts    4208 / 5239
failed exact lifts         1031
mixed channels               63
certified low-rank targets  624
winner selected            false
```

The single fully failed channel is retained as a quantifier control. The
theorem is `forall C exists m exists x`, not universal success of menu members
or exact realizations.

## Fixed-scope conclusion

For every context in the frozen 36-context carrier there is a future-free
channel with an exact source-addressed lift to `P_<=3^(7)`. This grants the
name `Sec_4,cand3^(7)` only on the declared fixed scope.

The result does not assert maximality, canonicity, coverage of the inherited
15,120-context universe, a uniform menu bound, or an all-rank return theorem.

## Artifacts

- `results/paper28_third_rank4_section_overlap_audit_v1.json`
- `results/paper28_third_rank4_section_candidate_v1.json.gz`
- `results/paper28_third_rank4_section_return_evaluation_v1.json.gz`
- their replay receipts and validators
