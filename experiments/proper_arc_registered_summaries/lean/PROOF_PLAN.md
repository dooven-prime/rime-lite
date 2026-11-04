# Proper-Arc Formalization Interfaces

The owner is `hal-05848115v1`, source content commit
`2a30449b9dc37a36b25b277ebc006515c2addb59`.
The proof domain is the identity singleton seed, raw chronological `p,d`,
fixed proper source arc `F=U(c,r)`, `2<=r<n`, and unrestricted word length.

The closed proof spine, exact declaration owners, frozen signatures and
evidence versions are consolidated in the independently checked
[theorem-to-source map](THEOREM_TO_SOURCE_MAP.md). The remaining interfaces
below are outside that kernel-checked snapshot.

## Completed Origin Classification

The first frozen layer supplies a continuous actual word for every internal
origin cut, the literal clean boundary, no earlier registration, and distinct
actual origins for distinct cuts. Its source files should remain unchanged
when subsequent modules are introduced.

The separate `classification/OriginExhaustive.lean` layer now proves the
reverse direction for arbitrary actual registered histories. It extracts
the first registration, recovers the unique oriented internal cut, and
establishes `ActualRegistrationOrigins c r equiv Fin(r-1)`, with the cut
readout determined by the actual left parent. Proposition 3.1 is closed;
neither a clean-state premise nor the ternary decoder enters this converse.

## Completed Constructive Ternary Layer

`chains/` now proves the `n-r` checkpoint decoder, cumulative-size/port key
recovery, all-c injectivity, and actual clean singleton-seed witnesses for
every code and every internal origin cut. The source frontier and complete
records are bound to one real execution prefix. Multi-atom outside partner
assembly and the final ordered absorption use the inherited generic
checkpoint constructors. Source translation commutes with the raw updates.

The resulting map is `Code (n-r)` embedded in the actual fixed-origin
selected-chain type. Its frozen construction remains unchanged by the
separate converse layer below.

## Completed Actual-Chain Classification

`converse/ActualChainConverse.lean` proves both encoder/decoder identities,
unique code for any actual registered history, strict chronological
checkpoints, the actual fixed-origin chain equivalence and `3^(n-r)` count.
The encoder is an explicit expression in the actual records. Its converse
uses arbitrary source-ordered execution prefixes and the current recorded
carrier, with no clean-state premise. The final two-packet port alternatives
remain distinct complete records. This closes the chain-bijection and
total-chain-count parts of Theorem 4.2.

## Completed Placement Fibre

The fixed-origin/code placement fibre is now proved in `fibres/`: arbitrary
actual endpoints recover unique native cut/site parameters, and each
parameter has an actual word preserving the specified origin and full
selected chain. The k=0 branch is independently equivalent to `ZMod n`.
The exact fixed-fibre total is `n * (n+k-2).choose k`.

## Completed Dependent Summary Equivalence

`summary/` proves Theorem 5.3 for all proper source arcs. The actual type is
defined by complete registered singleton-seed executions. `SummaryParams`
is the pure dependent origin/code/fibre sum. The explicit maps preserve
the literal origin, full ordered chain and placement, with both inverse
identities and a joint actual-word realization certificate. The owning
origin, chain and fibre proof freezes are unchanged.

## Completed Exact Summary Count

The separate `counting/` layer now transfers the frozen actual equivalence
through finite dependent-sigma cardinalities. It proves the last-checkpoint
multiplicities, weights them by the actual fibre count (including k=0), and
obtains Theorem 6.1 on `ActualRegisteredSummaries c r`. The all-n r=n-1
boundary is `(n-2)*n*(n+1)`. No old fixed-pair total is used.

## Completed Combinatorial Refinements

The separate `refinements/` layer now supplies the two finite subdivisions.
The literal selected-record length is the number of nonzero code positions,
so the actual fixed-origin length-j chain count is `(n-r).choose j * 2^j`.
The literal placement packet count is preserved by the positive fibre
decoder, giving the rank-s actual-fibre count
`s * (k-1).choose (s-2) * n.choose s` for k>0, 2<=s<=k+1.
The k=0 rank-one fibre remains independently equivalent to `ZMod n`.
The two branches do not use each other or the total-summary enumeration.

## Remaining Acceptance Points

1. **Fixed-pair specialization.** Identify the actual summary types at r=2,
   c=0 before comparing the already proved numerical totals.
2. **Separate analytic layer.** Generating functions and fixed-r asymptotics
   consume the exact count, without being prerequisites of the finite geometry.

Each point needs an all-parameter statement and its actual-source interface.
The existing finite control package remains a separate bounded replay.
No new operational field, typed transfer contract, or reset-bound assertion is
part of these acceptance points.
