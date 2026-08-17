# Current Results

Claim status is stated per item. None of the finite counts is promoted to a
universal generator-family law.

## Exact Results

1. **Rotation-orbit family index.** The declared axis-balanced family space has 63
   nonempty labelled families and 19 representatives under the 24
   orientation-preserving cube rotations.
2. **Rotation-conjugacy theorem.** A transported sector frame preserves routed
   product norms, ranks, protection classes, carrier mechanisms, and profile
   counts.
3. **Canonical carrier certificate.** Exact joint QT/HT projectors over
   `Q(zeta_3)` recover the nine canonical sector carrier masks. The four
   canonical zero triples have disjoint endpoint carriers, proving exact
   `AB=0` for every generator pair on those triples.
4. **n=8 exact spectrum.** For the `axes02_qt` family, the exact sum `S` over
   `Z[zeta_3]` satisfies

   ```text
   S(S-2I)(S-4I)(S-6I)(S-8I)((S-5I)^2-5I) = 0.
   ```

   Exact Lagrange traces give multiplicities
   `[8,32,31,26,26,84,21]`, summing to 228. Thus the seven endogenous
   projectors are algebraic over `Q(sqrt(5),zeta_3)`.
5. **Alignment/refinement theorem.** Projector-overlap alignment has exact row
   and column mass laws. Refined zero routes imply the aggregated coarse zero;
   the converse fails without a no-cancellation hypothesis.

## Computational Census

| Family / frame | Supported | Protected | Unprotected zero | Zero/all | Zero/unprotected |
|---|---:|---:|---:|---:|---:|
| 18-full / fixed canonical | 2,592 | 0 | 576 | 22.22% | 22.22% |
| axes02_qt / fixed canonical | 1,152 | 0 | 256 | 22.22% | 22.22% |
| axes02_qt / endogenous | 1,664 | 0 | 1,088 | 65.38% | 65.38% |
| drop_axis0_ht / endogenous | 6,816 | 2,896 | 1,920 | 28.17% | 48.98% |

Mechanism split:

```text
axes02_qt fixed:      256 carrier-forced,   0 within-carrier
axes02_qt endogenous: 256 carrier-forced, 832 within-carrier
n=16 endogenous:      832 carrier-forced, 1088 within-carrier
```

All 19 fixed-frame orbit representatives have either no supported skew routes
(pure half-turn families) or a numerically registered 22.22%
carrier-forced-zero rate. The canonical carrier certificate proves the exact
zero status of every registered carrier-forced route. The `2/9` rate remains a
finite numerical census because exact nonvanishing of every remaining
supported route has not been certified.

The 19 endogenous profiles have 16 distinct signatures. They contain zero
rates from 0% to 65.38%, protected-route counts from 0 to 2,896, and both
carrier-forced and within-carrier mechanisms. Equal operator counts can have
different rates: the 8-operator representatives include 0% and 65.38%, while
the 12-operator representatives include 22.22%, 35.82%, and 65.38%.

## Alignment Finding

The axes02_qt seven-sector frame and canonical nine-sector frame are
`overlapping_non_refinement_frames`: projector-overlap mass is complete to
about `3e-14`, but neither frame's sectors are contained in the other. The
65.38% versus 22.22% contrast is therefore a frame-change observation, not a
strict sector-refinement monotonicity result.

## Conjecture Gate

The current evidence supports one bounded statement:

> In the declared 19-orbit axis-balanced family census, every nonempty fixed-frame
> anti-Hermitian numerical support census has the same `2/9`
> carrier-forced-zero rate, and every zero counted in that numerator has an
> exact carrier-disjointness witness.

This is a completed finite census, not a conjecture beyond that family index. A
general theorem would need a combinatorial classification of which canonical
sector legs survive an arbitrary inverse-closed generator subset. Endogenous
profiles must be censused separately and compared only through their explicit
alignment objects.

`results/conjecture_audit.json` records this gate mechanically. It supplies
explicit orbit counterexamples to operator-count determinism, sector-count
determinism, and increasing/decreasing monotonicity proposals.

All exact finite artifacts use the repository evidence level
`Computational Certificate`; `certificate_kind` records the exact or
conditional-exact subtype. Paper VII v2.1 independently states and owns its
selected carrier and transported-frame results. The n=8, cross-frame, and
refinement propositions remain exploratory package results and do not acquire
Paper VII authority from public directory placement.
