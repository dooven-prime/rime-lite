# P28.2 Exact-Lift Credit Composition

## Status

This note records the first fixed-scope credit calculus for Paper XXVIII. It
projects the canonical `4+35` exact relation and introduces no new automata,
contexts, receipts, or mechanism fields.

The result is conditional on an exact compatible lift. It does not define a
total multiplication on accounting or interaction-skeleton labels.

## 1. Credit on an Exact Typed Arrow

For a typed context `C` with mass state `mu(C)`, define its remaining maturity
budget by

\[
 B(C)=\tau(n)-\tau(\mu(C)),
\]

where `tau(n)` is the maturity of a reset mass. If an exact receipt

\[
 x:C\longrightarrow C'
\]

has total length `L(x)` and total surplus `S(x)`, the corridor telescope gives

\[
 S(x)=\tau(C')-\tau(C)-L(x).
\]

Equivalently,

\[
 \boxed{B(C)=L(x)+S(x)+B(C').}
 \tag{1.1}
\]

The audit verifies (1.1), every individual corridor telescope, every stored
debt profile, and every residual-tail budget on all 11,252 exact receipts.

## 2. Exact-Lift Composition

Let

\[
 x:C_0\to C_1,
 \qquad
 y:C_1\to C_2
\]

be an exact compatible pair. Then

\[
 \begin{aligned}
 B(C_1)&=L(y)+S(y)+B(C_2),\\
 S(y\circ x)&=S(x)+S(y),\\
 B(C_0)&=L(y\circ x)+S(y\circ x)+B(C_2).
 \end{aligned}
 \tag{2.1}
\]

All 13,054 exact compatibility edges satisfy (2.1). The middle budget is
computed independently from the target of `x` and the source of `y`; the two
values agree because compatibility is equality of the exact typed boundary.

The additivity in (2.1) is numerical. Legal composition remains an exact
typed-relation question.

## 3. Lifted Accounting Composition Relation

For accounting labels `a_1,a_2`, declare a composition row only when there is
an exact lift

\[
 x\in q_{\rm acct}^{-1}(a_1),qquad
 y\in q_{\rm acct}^{-1}(a_2),qquad
 \partial^+x=\partial^-y.
\]

On the seed closure this produces 569 lifted accounting-label pairs. For every
such pair, all exact lifts give the same:

- source/middle/target partition chain;
- gross maturity-credit vector;
- first, second, and total length;
- first, second, and total surplus;
- tail-budget vector;
- composite debt profile and peak debt;
- final allocation vector `(L_total,S_total,B_final)`.

Thus the partial relation

\[
 \boxed{
  (a_1,a_2)\ \overset{\exists\text{ exact lift}}{\longmapsto}\
  A_{21}}
 \tag{3.1}
\]

has a well-defined composite accounting summary. It does not assert that every
pair of labels composes, or that every exact representative of `a_1` has a
compatible representative of `a_2`.

Of the 569 label pairs, 507 have more than one exact lift; one pair has 616
exact lifts. The equality in (3.1) is therefore a genuine fiber statement,
not uniqueness of a concrete witness.

## 4. Skeleton Hostile Control

There are 26 skeleton-label pairs admitting an exact lift, and every one has
multiple exact lifts. The skeleton preserves the coarse credit geometry:

| composite observable | skeleton pair fibers where it varies |
| --- | ---: |
| partition chain | 0 |
| gross maturity-credit vector | 0 |
| tail-budget vector | 0 |
| length vector / total length | 23 |
| surplus vector / total surplus | 23 |
| allocation vector / full accounting summary | 23 |
| composite debt profile / peak debt | 15 |

Hence

\[
 \boxed{
  \text{skeleton determines gross credit geometry,}
  \quad
  \text{accounting determines credit allocation}.}
 \tag{4.1}
\]

The largest skeleton-label pair fiber contains 2,675 exact compatible lifts.
This is further evidence that the skeleton is an interaction label, not yet an
algebra with a semantic composition operation.

## 5. Credit Reallocation Family

The extremal `(2,2,2,1)` source has budget 27. The complete seed relation
contains two zero-surplus families:

| channel | exact realizations | prefix length | target tail budget |
| --- | ---: | ---: | ---: |
| heavy-comb target `(6,1)` | 1,020 | 20 | 7 |
| rank-two fallback target `(5,2)` | 87 | 12 | 15 |

Therefore

\[
 \boxed{20+7=12+15=27.}
 \tag{5.1}
\]

The fallback reallocates eight units from prefix transport to the lower-rank
tail. It creates no maturity credit.

## 6. Current Theorem Boundary

The fixed-scope result is:

\[
 \boxed{
  \text{exact compatible lift}
  +\text{ accounting labels}
  \Longrightarrow
  \text{unique composite credit summary}.}
\]

It does not prove:

- that accounting labels decide whether an exact lift exists;
- that the skeleton determines credit allocation;
- a total mechanism-label multiplication;
- an all-rank repayment calculus;
- a future-free recursive return.

These boundaries keep P28.2 compatible with the P28.1 finding that semantic
composition remains exact-relation-valued.

## 7. Reproducibility

Run:

```powershell
python experiments/synchronizing_automata/paper28_audit_credit_composition.py
python experiments/synchronizing_automata/validation/validate_paper28_credit_composition_audit.py
```

The deterministic outputs are:

- `results/paper28_credit_composition_audit_v1.json`;
- `results/paper28_credit_composition_audit_v1.receipt.json`.

The validator reconstructs every receipt and exact-lift identity, freezes the
569/26 lifted-label counts and the skeleton hostile matrix, verifies the
1,020/87 reallocation families, and checks the artifact/input/source-closure
receipt.
