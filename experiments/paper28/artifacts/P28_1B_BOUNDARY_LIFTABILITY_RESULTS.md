# P28.1b Boundary and Liftability Factorization

## Status

This note records a projection-only audit of the canonical Paper XXVIII
`4+35` seed catalog. It introduces no new automata, contexts, receipts, or
mechanism fields. The exact relation remains the 11,252-receipt downward
closure constructed by `paper28_project_seed_mechanisms.py`.

The audit asks two questions that must not be conflated:

1. which typed target boundary explains successor heterogeneity inside one
   accounting or interaction-skeleton fiber; and
2. whether quotienting exact contexts by that boundary gives a fiber-uniform
   set of realizable successor mechanism classes.

The second is the stronger liftability question.

## 1. Exact Typed Arrows

An exact receipt is treated as an arrow

\[
 C\xrightarrow[\text{exact realization}]
   {(M_{\rm skel},M_{\rm acct})}C'.
\]

The mechanism data label the edge. Exact semantic composition is

\[
 \operatorname{Comp}(x,y)
 \quad\Longleftrightarrow\quad
 \partial^+x=\partial^-y,
\]

where equality is equality of the complete typed context, including the
outgoing distinguished ancestry packet. Neither mechanism quotient is
therefore assumed to be a quotient category.

The audited target-boundary hierarchy is:

1. action: ambient size, rank, and defect action;
2. normalized mass: action plus packet mass at every coordinate;
3. ancestry position: normalized mass plus the distinguished packet position;
4. role typed: coordinate-wise mass and current-fresh/other role;
5. exact typed context: packet identities and distinguished packet.

All keys are future-free.

## 2. Failure Factorization Inside Mechanism Fibers

The previous composition audit found 103 noncongruent accounting fibers and
9 noncongruent skeleton fibers. Refining only by the target boundary gives:

| mechanism quotient | action boundary sufficient | normalized mass needed | total hostile fibers |
| --- | ---: | ---: | ---: |
| accounting | 15 | 88 | 103 |
| skeleton | 1 | 8 | 9 |

No hostile fiber needs ancestry position, packet identity, or an exact target
channel once the normalized target mass placement is retained. This is a
factorization statement about the declared seed closure, not a new field in
either mechanism key.

For the displayed hostile pairs, the first boundary difference is even
coarser:

| mechanism quotient | first differs at action | first differs at normalized mass |
| --- | ---: | ---: |
| accounting | 90 | 13 |
| skeleton | 6 | 3 |

The distinction matters. Separating one hostile pair is weaker than proving
that all receipts with one boundary have the same successor-class set.

## 3. Context-Level Fiber-Uniform Liftability

There are 537 exact typed contexts in the seed closure. The normalized-mass
projection has 492 fibers. For each boundary fiber, the audit compares the
complete set of outgoing accounting classes and the complete set of outgoing
skeleton classes.

| successor labels | boundary | fibers | nonuniform fibers | nonempty mismatches |
| --- | --- | ---: | ---: | ---: |
| accounting | action | 151 | 67 | 38 |
| accounting | normalized mass | 492 | 0 | 0 |
| skeleton | action | 151 | 49 | 38 |
| skeleton | normalized mass | 492 | 0 | 0 |

Ancestry-position and role-typed boundaries also have 492 fibers on this
scope and add no separation beyond normalized mass. The exact-context baseline
has 537 fibers and is uniform by construction.

Thus the first seed audit supports the fixed-scope liftability statement

\[
 \boxed{
  \text{same action and normalized mass boundary}
  \Longrightarrow
  \text{same realizable successor mechanism classes}.}
\]

This is not promoted to an all-rank theorem. It is the first nontrivial
boundary quotient surviving the stronger successor-set test.

## 4. Abstract Menus and Exact Realization Fibers

For an exact source context `C`, define

\[
 \mathfrak M_r(C)=
 \{m:\mathcal R_r(C;m)\ne\varnothing\},
 \qquad
 \mathcal R_r(C;m)=
 \{B:q(B)=m,\ \partial^-B=C\}.
\]

The seed data sharply separate menu size from exact-receipt count.

| seed surface | contexts | max skeleton menu | max accounting menu | max exact receipts from one context |
| --- | ---: | ---: | ---: | ---: |
| `n=6` Type-II-only section | 4 | 4 | 10 | 22 |
| `n=7` extremal carrier | 35 | 8 | 46 | 380 |

Across the seed contexts, one skeleton realization fiber contains as many as
316 exact receipts; one accounting realization fiber contains as many as 64.
Consequently B0/B1/B2 boundedness is assigned to
`|\mathfrak M_r(C)|`, not to the total size of the exact realization relation.
Exact fibers are required to be relation-defined, locally enumerable, and
liftable; no constant-cardinality claim is made.

## 5. Current Architecture

The seed evidence supports the layered description

\[
 \boxed{
  \text{interaction skeleton layer}
  +\text{ accounting refinement}
  +\text{ exact typed realization fiber}.}
\]

The word `algebra` is deliberately withheld from the skeleton layer. The raw
skeleton quotient does not preserve even successor nonemptiness. What survives
is a small edge-label menu together with a typed boundary and its exact lift
relation.

## 6. Reproducibility

Run:

```powershell
python experiments/synchronizing_automata/paper28_audit_boundary_liftability.py
python experiments/synchronizing_automata/validation/validate_paper28_boundary_liftability_audit.py
```

The deterministic outputs are:

- `results/paper28_boundary_liftability_audit_v1.json`;
- `results/paper28_boundary_liftability_audit_v1.receipt.json`.

The validator rebuilds every boundary fiber and successor-class set from the
bound canonical catalog. It also recomputes every typed context identifier and
all 13,054 compatibility edges directly from exact boundary equality, checks
the 103/9 hostile-fiber totals, and verifies the artifact/input/source-closure
receipt.
