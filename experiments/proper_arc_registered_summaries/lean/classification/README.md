# Exhaustive Proper-Arc Origins

This separate layer completes Proposition 3.1 of `hal-05848115v1` for
`n>=3`, arbitrary source start `c : ZMod n`, and `2<=r<n`. It leaves the
constructive origin and named-interface source freezes unchanged.

## Proof Interfaces

| Source | Responsibility |
|---|---|
| `OriginTrace.lean` | From the original actual word, recover its first registration as `pre ++ d :: post`, with the absent predecessor origin, occupied ordered ports, the union F, and the event record that persists through the suffix. |
| `SourceCut.lean` | Shift the degree-one integer source lift to c. The outside atom c+r excludes a cyclic wrap between ports. Every left-parent address is strictly less than every right-parent address. The latter's minimum is the internal cut. |
| `OriginExhaustive.lean` | Supply source order and disjointness from the actual seed prefix, recover the unique cut, and combine this converse with the frozen explicit origin words. |

The reverse theorem is about arbitrary generated registered histories. It
does not assume that outside packets remain singleton, that the origin is
standard, or that a code decoder already exists.

`actual_registered_origin_unique` gives the unique index in `Fin (r-1)`.
The natural-number interface `actual_registered_origin_unique_nat` states
the corresponding bounded cut directly:

\[
\operatorname{ReachableExecution}(F,s)\ \land\ s.\operatorname{origin}\ne\mathrm{none}
\quad\Longrightarrow\quad
\exists!t,\quad 1\le t<r\ \land\ s.\operatorname{origin}=\mathrm{some}(o_t).
\]

Both require `F=arc c r` and `2<=r<n`. Their complete elaborated Lean
signatures are in the dependency report below.

## Actual Origin Parameter Type

`ActualRegistrationOrigins c r` contains a record exactly when some raw
word from the singleton seed records that origin. It is not defined as
the range of the proposed origin decoder.

The equivalence

```lean
actualRegistrationOriginsEquivCuts c r hr :
  ActualRegistrationOrigins c r ≃ Fin (r - 1)
```

is obtained by proving that the explicit map from cuts is injective and
surjective onto that actual-history type. Its reverse map realizes a cut
with the already frozen `originWord`. The semantic readout theorem
`actualRegistrationOriginsEquivCuts_left_card` proves that its cut value
plus one equals the actual origin's left-parent cardinality. Finiteness
and the exact count `r-1` follow from this equivalence.

The equivalence uses classical choice as a mathematical inverse. This
does not replace the explicit word in the constructive direction or claim
an extracted normalization algorithm.

## Replay and Scope

From the parent Lean directory:

```powershell
python -B classification/validate_classification.py
python -B -m unittest discover -s classification/tests -p 'test_*.py' -v
```

`--check-upstream-git` additionally checks the pinned input mirrors against
their historical Git objects. `--source-only` checks bytes, not the kernel.
The default rebuilds the frozen root, the generic owner modules and these
three new proof modules, then reruns the declaration audit.

The [milestone](milestones/origin-classification-v1/manifest.json) records
six new source inputs, 23 axiom checks, nine complete target signatures,
the 8,268-node dependency report and the toolchain. Its manifest SHA-256 is
`cf0bc343a73e7466b870c36843e072472159779373ad3e85964d17e69acea2d0`.
Its [dependency graph](milestones/origin-classification-v1/dependency-audit.json)
includes three explicit inherited targets:

- `ProperArc.run_local_unregistered`;
- `ProperArc.run_originWord`;
- `ProperArc.boundary_clean`.

Their entire transitive node sets and direct dependency edges are compared
against the frozen interface report. The checker also requires actual
first-registration extraction, integer-lift source order, and the explicit
raw witness in the relevant main targets. An added clean-state admission
premise, a formal-range replacement of the actual origin type, or a
nonstandard axiom is rejected.

This closes origin classification only. Ternary-chain decoding and its
actual-history inverse, full placement fibres, dependent summary assembly,
and their total count remain subsequent proof layers. The n=2/full-arc
exception is outside the proper-arc hypotheses. No published manuscript or
earlier frozen proof bytes are rewritten by this companion.
