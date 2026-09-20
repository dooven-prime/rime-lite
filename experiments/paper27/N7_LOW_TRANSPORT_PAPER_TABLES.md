# N7 Low-Transport Paper Tables

## Purpose

This appendix reorganizes the complete-relation certificate into the three
finite tables used by the paper proof. The rows are typed algebraic solutions,
not selected complete representatives. In particular, the count 129 does not
enter the proof flow.

These are **derived-table equalities**. The bound JSON verifies every displayed
row and count, while the paper obtains Table 1 by solving the typed
back-solving constraints, Table 2 from the explicit modular gates, and Table 3
from the heavy-pair strict-exit equations. The tables are not replacement
premises for those eliminations.

Use the exclusion codes

```text
E  early fusion,
R  prescribed packet-role violation,
N  fixed-endpoint nonminimality,
A  debt or length violation.
```

The Back-Solving equality says that solving the typed constraints leaves
exactly the rows below; every omitted branch is eliminated by `E`, `R`, `N`,
or `A`. The inverse-tree completeness argument below closes that equality,
while the bound artifact remains its regression certificate.

## Empty Post-Tag Cell

The fifth negative parameter cell is separate. Here the post-tag relation is
explicitly the **shallow** relation

\[
 \mathcal X_j^{\rm sh}(C)
 =\{\widehat X:\widehat X\text{ arises from a role-compatible marked }
 C_4\text{ association with }r\in\{0,1\}\}.
\]

No landing test occurs in this definition. The claim to prove is

\[
 \boxed{\mathcal X_3^{\rm sh}(321;h=3,\beta=I)=\varnothing.}
 \tag{Empty-X}
\]

Carrier reconstruction gives

\[
 d=(0,3,2,1,4,5,0),
 \qquad
 (F_4,s,D_1,D_2)=(0,1,2,4),
\]

and the marked moved edge is `3 -> 1`. Put `H=F4+D2` after the first
heavy-comb fusion. For corridor lengths `ell_1,ell_2`, the two surpluses are

\[
 S_1=7-\ell_1,
 \qquad
 S_2=13-\ell_2.
\]

Thus a Type-II heavy comb requires

\[
 \ell_1\ge8,
 \qquad
 \ell_1+\ell_2\le20.                            \tag{EX-A}
\]

The finite back-solving used below is entirely local. Reverse rotation is
unique, and the inverse fibres of the defect are

\[
 d^{-1}(0)=\{0,6\},\quad d^{-1}(1)=\{3\},\quad
 d^{-1}(3)=\{1\},\quad d^{-1}(i)=\{i\} (i=2,4,5).
 \tag{EX-B}
\]

Starting from the prescribed terminal fusion roles, iterate `(EX-B)` through
rank-preserving predecessors. Mark a predecessor exactly when the incoming
mass-two packet occupies coordinate `3`, and retain only marks with at most
one later nonterminal `d`. Endpoint nonminimal branches and branches violating
`(EX-A)` are discarded. This gives the following two exhaustive calculations.

### Empty-X.1: a first-corridor mark cannot be repaid

Solving the first-corridor equations for both choices of incoming mass-two
packet leaves exactly the five marked words below. Digits use `0=p,1=d`; the
bracketed `1` is the marked occurrence. Every surviving row fuses `F4` with
`D2`.

| marked first word | `r` | rank-three endpoint | `ell_1` | minimum possible `ell_2` | total | exclusion |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `000101[1]01000001` | 1 | `0:H,3:D1,5:s` | 15 | 6 | 21 | `A` |
| `1000000[1]0100001` | 1 | `0:H,3:D1,5:s` | 15 | 6 | 21 | `A` |
| `10000010[1]0100001` | 1 | `0:H,2:s,3:D1` | 16 | 6 | 22 | `A` |
| `1000000[1]0000001` | 0 | `0:H,2:D1,3:s` | 15 | 12 | 27 | `A` |
| `000101[1]000001` | 0 | `0:H,1:s,5:D1` | 13 | 8 | 21 | `A` |

The fifth column is the shortest strict second exit fusing `H` with `D1`,
over all exact rank-two endpoints. Consequently every row violates
`ell_1+ell_2<=20`; no first-corridor mark defines a member of
`\mathcal X_3^{\rm sh}`.

### Empty-X.2: a second-corridor mark is nonminimal

The same back-solving without a mark gives exactly five first corridors that
can satisfy the repayment bound:

| id | complete first word | rank-three source `Z` | `ell_1` | maximum `ell_2` |
| --- | --- | --- | ---: | ---: |
| `Z1` | `000010001` | `0:H,1:D1,3:s` | 9 | 11 |
| `Z2` | `0000101001` | `0:H,2:s,5:D1` | 10 | 10 |
| `Z3` | `00001011001` | `0:H,1:D1,2:s` | 11 | 9 |
| `Z4` | `00010000001` | `0:H,1:s,4:D1` | 11 | 9 |
| `Z5` | `00010100001` | `0:H,2:s,4:D1` | 11 | 9 |

For a final singleton coordinate `t`, let

\[
 L_{\rm sh}(Z,t)
\]

be the minimum length, within the displayed repayment bound, of a strict
`H+D1` exit containing a shallow marked `3 -> 1` edge. Let
`L_min(Z,t)` be the unrestricted fixed-endpoint minimum. Solving the labelled
pair-exit equations gives all finite shallow values:

| source | `t : L_sh(Z,t) > L_min(Z,t)` |
| --- | --- |
| `Z1` | `1: 9>8`, `2: 9>7`, `3: 9>7`, `5: 10>7` |
| `Z2` | `5: 10>8` |
| `Z3` | `2: 9>8`, `3: 9>7`, `5: 9>7` |
| `Z4` | none |
| `Z5` | none |

Every omitted coordinate has no shallow marked solution within the repayment
bound. Every displayed solution is strictly longer than another word to the
same mass endpoint, so fixed-endpoint normalization rejects it. This proves
`(Empty-X)` before any return or rank-three continuation calculation.

The superscript `sh` is essential. The full tagged relation is not empty:
from `Z1`, the endpoint-shortest word `00[1]01100001` contains the marked edge
and has two later rank-preserving `d` letters (`r=2`). It is outside the
canonical direct/one-return menu and is retained as a hostile control against
the stronger, false untyped claim.

## Table 1: Back-Solving

An accounting triple is `(S_in,k,b)`: surplus entering the marked corridor,
marked-prefix length, and running balance after the tagged occurrence.

The four nonempty carrier inputs, derived from `(CR)+(K)`, are:

| cell | rooted defect | rank-four source | marked edge |
| --- | --- | --- | --- |
| `132/2,(3,I)` | `0132450` | `0:F4,3:D1,4:s,5:D2` | `2 -> 3` |
| `213/2,(3,I)` | `0213450` | `0:F4,1:D1,3:D2,5:s` | `2 -> 1` |
| `213/2,(3,S)` | `0213540` | `0:F4,1:D1,3:D2,4:s` | `2 -> 1` |
| `213/2,(4,I)` | `0214350` | `0:F4,1:D1,4:D2,5:s` | `2 -> 1` |

For a corridor source `Z`, incoming role `R`, and moved slot `j`, a
back-solving solution is a marked prefix `u=u' d` such that:

1. every `d` in `u` is rank-preserving;
2. `R` occupies `lambda(j)` immediately before the final, marked `d` in `u`;
3. the resulting post-tag state admits a direct or one-return suffix of the
   prescribed fusion corridor;
4. the full corridor is shortest for its exact mass endpoint and satisfies
   the two-corridor accounting gate.

For corridor one, `Z` is the displayed rank-four source. For corridor two,
`Z` ranges over the rank-three endpoints of admissible first corridors. The
inverse step is explicit:

\[
 p^{-1}(i)=i-1\pmod 7,
 \qquad
 d^{-1}(0)=\{0,6\},
 \qquad
 d^{-1}(i)=\{\pi^{-1}(i)\}\quad(i\ne0).
 \tag{BT-inverse}
\]

Back-solving the terminal roles with `(BT-inverse)` and discarding a branch at
its first `E`, `R`, `N`, or `A` violation is a finite inverse recurrence.  More
explicitly, for each cell `b`, corridor `c`, and incoming role `R`, start from
the two prescribed terminal fusion parents.  Reverse rotations uniquely.
Whenever a reversed `d`-edge has image zero, branch over the two preimages
`{0,6}`; every other nonzero coordinate has a unique predecessor.  Stop a
branch when it reaches the marked equation

\[
 R@\lambda(j)\xrightarrow d R@\alpha(j),       \tag{BT-mark}
\]

or at its first `E/R/N/A` violation.  Fixed-endpoint distance and the remaining
debt budget bound the marked-prefix depth.  Subtracting the shortest admissible
post-tag suffix from those bounds gives the channel caps in the next table.

> **Inverse-Tree Termination and Completeness Lemma.** For every declared
> cell/channel, the recurrence above terminates and enumerates every admissible
> marked prefix within its stated depth cap. Reverse rotations are unique;
> under `d^{-1}` a nonzero image has one predecessor and the collision image
> zero has exactly the two predecessors `{0,6}`. Hence each reverse level lists
> the full predecessor set. The fixed-endpoint and remaining-accounting bounds
> give the finite depth cap. Moreover, an `E/R/N/A` exclusion is permanent
> under further reverse extension: an early fusion cannot be undone, a role
> violation contradicts the prescribed labelled trace, a shorter word to the
> fixed endpoint remains shorter, and added prefix length cannot repair an
> exceeded debt/length bound. Induction on reverse depth therefore proves both
> termination and exhaustion; no unlisted admissible leaf exists.

> **Back-Solving Exhaustion Lemma.** The inverse recurrence above has exactly
> the source-addressed surviving leaves displayed below.  Every other inverse
> leaf ends at its first `E`, `R`, `N`, or `A` exclusion.  A repeated word in
> two rows denotes two different labelled corridor sources, not a quotient.

| cell | `c/role` | prefix-depth cap | complete surviving marked-prefix leaves |
| --- | --- | ---: | --- |
| `132/2,(3,I)` | `2/D1` | 3 | `011 -> X1` |
| `132/2,(3,I)` | `1/D2` | 5 | `00001 -> X2` |
| `132/2,(3,I)` | `2/D2` | 6 | `00001 -> X3`; `00001 -> X4`; `000101 -> X5`; `101001 -> X5`; `010101 -> X6` |
| `213/2,(3,I)` | `1/D1` | 2 | `01 -> X8` |
| `213/2,(3,I)` | `2/D2` | 2 | `1 -> X7`; `01 -> X9` |
| `213/2,(3,S)` | `2/D2` | 2 | `01 -> X10` |
| `213/2,(4,I)` | `1/D1` | 4 | `01 -> X13`; `0101 -> X17` |
| `213/2,(4,I)` | `2/D1` | 3 | `1 -> X11`; `1 -> X12`; `01 -> X15`; `101 -> X16` |
| `213/2,(4,I)` | `2/D2` | 2 | `01 -> X14` |

All omitted `c/role` combinations have empty survivor sets under the same
recurrence.  The cellwise checksum is

\[
 (7\to6)+(3\to3)+(1\to1)+(7\to7)=18\to17,     \tag{BT-count}
\]

where only `X5` identifies two leaves.  That identification is legal because
the two prefixes induce the same typed post-tag placement and the same full
normalization/accounting gate semantics.  In contrast, no mass-endpoint
quotient is used here.

Expanding the 17 typed leaves gives the following prefix-solution table. The
prefix set is part of the equality: two prefixes may be identified only when
they induce the same displayed typed state and the same
normalization/accounting semantics.

| id | negative cell | `c/role` | complete marked-prefix set | `k` | post-tag labelled placement | accounting | corridor source |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `X1` | `132/2,(3,I)` | `2/D1` | `{011}` | 3 | `0:s,1:D2+F4,3:D1` | `(-3,3,-6)` | `0:D2+F4,2:D1,5:s` |
| `X2` | `132/2,(3,I)` | `1/D2` | `{00001}` | 5 | `0:D1,1:s,3:D2,4:F4` | `(0,5,-5)` | `0:F4,3:D1,4:s,5:D2` |
| `X3` | `132/2,(3,I)` | `2/D2` | `{00001}` | 5 | `0:s,3:D2,4:D1+F4` | `(-2,5,-7)` | `0:D1+F4,2:s,5:D2` |
| `X4` | `132/2,(3,I)` | `2/D2` | `{00001}` | 5 | `1:s,3:D2,4:D1+F4` | `(-3,5,-8)` | `0:D1+F4,4:s,5:D2` |
| `X5` | `132/2,(3,I)` | `2/D2` | `{000101,101001}` | 6 | `0:s,2:D1+F4,3:D2` | `(-2,6,-8)` | `0:D1+F4,2:s,5:D2` |
| `X6` | `132/2,(3,I)` | `2/D2` | `{010101}` | 6 | `2:s,3:D2,4:D1+F4` | `(-2,6,-8)` | `0:D1+F4,2:s,5:D2` |
| `X7` | `213/2,(3,I)` | `2/D2` | `{1}` | 1 | `0:D1+F4,1:D2,4:s` | `(-1,1,-2)` | `0:D1+F4,2:D2,4:s` |
| `X8` | `213/2,(3,I)` | `1/D1` | `{01}` | 2 | `0:s,1:D1,2:F4,4:D2` | `(0,2,-2)` | `0:F4,1:D1,3:D2,5:s` |
| `X9` | `213/2,(3,I)` | `2/D2` | `{01}` | 2 | `0:s,1:D2,2:D1+F4` | `(-1,2,-3)` | `0:D1+F4,1:D2,5:s` |
| `X10` | `213/2,(3,S)` | `2/D2` | `{01}` | 2 | `0:s,1:D2,2:D1+F4` | `(-1,2,-3)` | `0:D1+F4,1:D2,5:s` |
| `X11` | `213/2,(4,I)` | `2/D1` | `{1}` | 1 | `0:D2+F4,1:D1,4:s` | `(-1,1,-2)` | `0:D2+F4,2:D1,3:s` |
| `X12` | `213/2,(4,I)` | `2/D1` | `{1}` | 1 | `0:D2+F4,1:D1,5:s` | `(-2,1,-3)` | `0:D2+F4,2:D1,5:s` |
| `X13` | `213/2,(4,I)` | `1/D1` | `{01}` | 2 | `0:s,1:D1,2:F4,5:D2` | `(0,2,-2)` | `0:F4,1:D1,4:D2,5:s` |
| `X14` | `213/2,(4,I)` | `2/D2` | `{01}` | 2 | `1:D2,2:D1+F4,3:s` | `(-1,2,-3)` | `0:D1+F4,1:D2,3:s` |
| `X15` | `213/2,(4,I)` | `2/D1` | `{01}` | 2 | `0:s,1:D1,2:D2+F4` | `(-3,2,-5)` | `0:D2+F4,1:D1,5:s` |
| `X16` | `213/2,(4,I)` | `2/D1` | `{101}` | 3 | `0:s,1:D1,2:D2+F4` | `(-2,3,-5)` | `0:D2+F4,2:D1,5:s` |
| `X17` | `213/2,(4,I)` | `1/D1` | `{0101}` | 4 | `0:D2,1:D1,2:s,4:F4` | `(0,4,-4)` | `0:F4,1:D1,4:D2,5:s` |

Let

\[
 \mathfrak B_{\ne\varnothing}
 =\{132/2,(3,I);\ 213/2,(3,I);\ 213/2,(3,S);\ 213/2,(4,I)\}.
\]

The theorem-facing equality is the disjoint-union statement

\[
 \bigsqcup_{b\in\mathfrak B_{\ne\varnothing}}
 \operatorname{Sol}_{\rm BT}(b)
 =\{\widehat X_1,\ldots,\widehat X_{17}\}
\]

over the four nonempty negative cells, together with `(Empty-X)` for the fifth.
There are 18 marked-prefix solutions because `X5` has two tied provenances,
but exactly 17 typed states. No landing value is used in this elimination.

## Table 2: Return Admission

For each `q in Q^kin(X)`, let `A_q(X)` be the uniquely determined shallow
candidate obtained after terminal-rotation elimination. Define

\[
 \mathsf N(\widehat X,q)=1
 \iff A_q(\widehat X)\text{ has fixed-endpoint minimum length},
\]

and

\[
 \mathsf A(\widehat X,q)=1
 \iff A_q(\widehat X)\text{ satisfies the applicable corridor balance and
 debt bound}.
\]

Rank preservation and the prescribed packet roles are already part of
`Q^kin`. The admitted relation is therefore

\[
 Q(\widehat X)=
 \{q\in Q^{\rm kin}(\widehat X):
   \mathsf N(\widehat X,q)=\mathsf A(\widehat X,q)=1\}.       \tag{Admission}
\]

If the marked prefix has length `k`, a one-return suffix has the forced form

\[
 p^q d\,p^{a_q}d,
 \qquad
 L_q=k+q+a_q+2,                              \tag{RA-word}
\]

where adjacency uniquely determines `a_q`.  A direct suffix has the form
`p^{a_D}d` and length `L_D=k+a_D+1`.  Write `L_*` for the shortest length to
the same exact mass endpoint.  Then

\[
 \mathsf N=1\iff L=L_*.
\]

For a second-corridor candidate, its surplus is `S_2=13-L`; the typed state
supplies `S_in<0`, and

\[
 \mathsf A=1\iff S_{\rm in}+S_2\ge0.          \tag{RA-2}
\]

For a first-corridor candidate, `S_1=7-L<0`.  Its accounting entry below is
`S1; r/m`, where `m` is the number of role-compatible normalized second
corridors and `r` is the number that repay `-S_1`; here

\[
 \mathsf A=1\iff r>0.                          \tag{RA-1}
\]

Mass endpoints are displayed as seven-coordinate strings.  The following is
the complete one-return elimination.  In the accounting column, an expression
`x+y=z` means `S_in+S_2=S_total`; `N`, `A`, and `N+A` in the last column are
the complete rejection bases.

| `X` | `c` | `q` | `a_q` | endpoint | `L/L_*` | accounting | `N` | `A` | result |
| --- | ---: | ---: | ---: | --- | ---: | --- | :---: | :---: | --- |
| `X1` | 2 | 0 | 5 | `6000010` | 10/8 | `-3+3=0` | no | yes | `N` |
| `X1` | 2 | 1 | 3 | `6000100` | 9/9 | `-3+4=1` | yes | yes | `in Q` |
| `X1` | 2 | 5 | 6 | `6000100` | 16/9 | `-3-3=-6` | no | no | `N+A` |
| `X2` | 1 | 1 | 2 | `4020010` | 10/10 | `S1=-3; 4/12` | yes | yes | `in Q` |
| `X2` | 1 | 4 | 6 | `4020100` | 17/9 | `S1=-10; 0/8` | no | no | `N+A` |
| `X3` | 2 | 1 | 2 | `6010000` | 10/9 | `-2+3=1` | no | yes | `N` |
| `X3` | 2 | 4 | 6 | `6010000` | 17/9 | `-2-4=-6` | no | no | `N+A` |
| `X3` | 2 | 6 | 4 | `6000100` | 17/11 | `-2-4=-6` | no | no | `N+A` |
| `X4` | 2 | 1 | 2 | `6000010` | 10/10 | `-3+3=0` | yes | yes | `in Q` |
| `X4` | 2 | 4 | 6 | `6000100` | 17/9 | `-3-4=-7` | no | no | `N+A` |
| `X4` | 2 | 6 | 4 | `6000100` | 17/9 | `-3-4=-7` | no | no | `N+A` |
| `X5` | 2 | 0 | 4 | `6000100` | 12/11 | `-2+1=-1` | no | no | `N+A` |
| `X5` | 2 | 2 | 2 | `6000010` | 12/10 | `-2+1=-1` | no | no | `N+A` |
| `X5` | 2 | 5 | 6 | `6000100` | 19/11 | `-2-6=-8` | no | no | `N+A` |
| `X6` | 2 | 1 | 2 | `6000100` | 11/11 | `-2+2=0` | yes | yes | `in Q` |
| `X6` | 2 | 6 | 4 | `6000010` | 18/10 | `-2-5=-7` | no | no | `N+A` |
| `X7` | 2 | 1 | 5 | `6001000` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X7` | 2 | 3 | 3 | `6001000` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X7` | 2 | 4 | 2 | `6000100` | 9/9 | `-1+4=3` | yes | yes | `in Q` |
| `X8` | 1 | 0 | 5 | `4200010` | 9/8 | `S1=-2; 4/9` | no | yes | `N` |
| `X8` | 1 | 2 | 3 | `4002100` | 9/9 | `S1=-2; 0/7` | yes | no | `A` |
| `X8` | 1 | 3 | 2 | `4200010` | 9/8 | `S1=-2; 4/9` | no | yes | `N` |
| `X9` | 2 | 0 | 5 | `6000010` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X9` | 2 | 2 | 3 | `6000100` | 9/7 | `-1+4=3` | no | yes | `N` |
| `X9` | 2 | 3 | 2 | `6000010` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X10` | 2 | 0 | 5 | `6000100` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X10` | 2 | 3 | 2 | `6000100` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X11` | 2 | 1 | 5 | `6000100` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X11` | 2 | 3 | 3 | `6000100` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X12` | 2 | 1 | 5 | `6000010` | 9/9 | `-2+4=2` | yes | yes | `in Q` |
| `X12` | 2 | 3 | 3 | `6000010` | 9/9 | `-2+4=2` | yes | yes | `in Q` |
| `X13` | 1 | 0 | 5 | `4000210` | 9/8 | `S1=-2; 2/6` | no | yes | `N` |
| `X13` | 1 | 2 | 3 | `4001200` | 9/7 | `S1=-2; 7/10` | no | yes | `N` |
| `X14` | 2 | 0 | 5 | `6100000` | 9/7 | `-1+4=3` | no | yes | `N` |
| `X14` | 2 | 2 | 3 | `6010000` | 9/8 | `-1+4=3` | no | yes | `N` |
| `X15` | 2 | 0 | 5 | `6000010` | 9/8 | `-3+4=1` | no | yes | `N` |
| `X15` | 2 | 2 | 3 | `6001000` | 9/7 | `-3+4=1` | no | yes | `N` |
| `X16` | 2 | 0 | 5 | `6000010` | 10/9 | `-2+3=1` | no | yes | `N` |
| `X16` | 2 | 2 | 3 | `6001000` | 10/7 | `-2+3=1` | no | yes | `N` |
| `X17` | 1 | 0 | 4 | `4002010` | 10/10 | `S1=-3; 2/6` | yes | yes | `in Q` |

The direct candidates are exhausted by the same formulas with no return
exponent:

| `X` | `c` | `a_D` | endpoint | `L/L_*` | accounting | `N` | `A` | result |
| --- | ---: | ---: | --- | ---: | --- | :---: | :---: | --- |
| `X2` | 1 | 3 | `4020100` | 9/9 | `S1=-2; 3/8` | yes | yes | direct |
| `X3` | 2 | 3 | `6010000` | 9/9 | `-2+4=2` | yes | yes | direct |
| `X4` | 2 | 3 | `6000100` | 9/9 | `-3+4=1` | yes | yes | direct |
| `X5` | 2 | 4 | `6000100` | 11/11 | `-2+2=0` | yes | yes | direct |
| `X6` | 2 | 3 | `6000010` | 10/10 | `-2+3=1` | yes | yes | direct |
| `X7` | 2 | 6 | `6001000` | 8/8 | `-1+5=4` | yes | yes | direct |
| `X8` | 1 | 5 | `4200010` | 8/8 | `S1=-1; 4/9` | yes | yes | direct |
| `X9` | 2 | 5 | `6000010` | 8/8 | `-1+5=4` | yes | yes | direct |
| `X10` | 2 | 5 | `6000100` | 8/8 | `-1+5=4` | yes | yes | direct |
| `X11` | 2 | 6 | `6000100` | 8/8 | `-1+5=4` | yes | yes | direct |
| `X12` | 2 | 6 | `6001000` | 8/7 | `-2+5=3` | no | yes | `N` |
| `X13` | 1 | 5 | `4000210` | 8/8 | `S1=-1; 4/6` | yes | yes | direct |
| `X14` | 2 | 5 | `6010000` | 8/8 | `-1+5=4` | yes | yes | direct |
| `X15` | 2 | 5 | `6000010` | 8/8 | `-3+5=2` | yes | yes | direct |
| `X16` | 2 | 5 | `6000010` | 9/9 | `-2+4=2` | yes | yes | direct |

Thus the rowwise equality `(Admission)` gives

| id | `Q^kin(X)` | admitted `Q(X)` | direct |
| --- | --- | --- | --- |
| `X1` | `{0,1,5}` | `{1}` | none |
| `X2` | `{1,4}` | `{1}` | admitted |
| `X3` | `{1,4,6}` | empty | admitted |
| `X4` | `{1,4,6}` | `{1}` | admitted |
| `X5` | `{0,2,5}` | empty | admitted |
| `X6` | `{1,6}` | `{1}` | admitted |
| `X7` | `{1,3,4}` | `{4}` | admitted |
| `X8` | `{0,2,3}` | empty | admitted |
| `X9` | `{0,2,3}` | empty | admitted |
| `X10` | `{0,3}` | empty | admitted |
| `X11` | `{1,3}` | empty | admitted |
| `X12` | `{1,3}` | `{1,3}` | rejected by `N` |
| `X13` | `{0,2}` | empty | admitted |
| `X14` | `{0,2}` | empty | admitted |
| `X15` | `{0,2}` | empty | admitted |
| `X16` | `{0,2}` | empty | admitted |
| `X17` | `{0}` | `{0}` | none |

Summing the rows gives

\[
 40=8_{\rm admitted}+21_{N}+1_A+10_{N+A},       \tag{Q-count}
\]

and the direct candidates give

\[
 15=14_{\rm admitted}+1_N.                      \tag{D-count}
\]

No return candidate passes both `N` and `A` while remaining outside `Q(X)`.
No direct candidate passes its declared gate while remaining outside the
direct relation. Thus endpoint normalization and accounting are the complete
admission interface **on this five-cell surface**. This statement is not
promoted to other ranks or ambient sizes.

## Table 3: Heavy-Pair Exits

For a typed rank-three state `Y`, define

\[
 \mathcal E(Y)=\{w:w\text{ is an admissible endpoint-normalized strict
 heavy-pair exit from }Y\},
\]

and

\[
 \Gamma(Y,t)=\{w(t):w\in\mathcal E(Y)\}.        \tag{Gamma-image}
\]

Words use `0=p,1=d` and act left to right.  Completeness is obtained before
the singleton is replayed.  On the finite rank-three mass graph, let
`delta_Y(M)` be the shortest rank-preserving distance from the mass placement
of `Y` to `M`.  Retain a parent edge `M --a--> M'` exactly when

\[
 \delta_Y(M)+1=\delta_Y(M'),                    \tag{Exit-DAG}
\]

and retain a strict terminal edge to `Z` exactly at the minimum distance to
that exact endpoint `Z`.  Backtracking this shortest-parent DAG gives every
tied endpoint-shortest exit word.  A terminal parent-role check then selects
the exits fusing the two heavy packet identities.  Finally, the displayed
debt bound discards the overlength exits.  No singleton landing is read in
any of these three operations.

The resulting equalities are below.  An accepted entry is
`word [length,target,t,S2]`; its last two fields are obtained only by passive
replay.  The `over debt` column lists every other endpoint-shortest exit that
fuses the correct heavy pair, as `word [length,target]`.

| id | defect / typed `Y` | debt / max `ell_2` | complete `E(Y)` | correct pair but over debt | all-exit split | `Gamma(Y,t)` |
| --- | --- | --- | --- | --- | --- | --- |
| `Y1` | `0132450`; `0:D2+F4,2:D1,4:s` | `2 / 11` | `0010001 [7,6010000,2,6]`; `010100001 [9,6000100,4,4]`; `0101001001 [10,6000010,5,3]` | `00000010000001 [14,6100000]`; `000000100001001 [15,6001000]`; `000000110000001 [15,6001000]`; `00010101000001 [14,6100000]`; `000101010001001 [15,6001000]` | `24=3+5+16_wrong-pair` | `{2,4,5}` |
| `Y2` | `0132450`; `0:D2+F4,2:D1,5:s` | `3 / 10` | `0010001 [7,6010000,2,6]`; `010001001 [9,6000100,4,4]`; `011010001 [9,6000100,4,4]`; `01000001 [8,6000010,5,5]` | `0001010010001 [13,6100000]`; `00010100101001 [14,6001000]`; `00010101000001 [14,6001000]`; `1000101000001 [13,6100000]`; `10001010001001 [14,6001000]`; `1010010010001 [13,6100000]`; `10100100101001 [14,6001000]`; `10100101000001 [14,6001000]` | `25=4+8+13_wrong-pair` | `{2,4,5}` |
| `Y3` | `0213450`; `0:D1+F4,1:D2,5:s` | `1 / 12` | `00001001 [8,6001000,3,5]`; `0000001 [7,6000100,4,6]`; `00010001 [8,6000010,5,5]`; `01000001 [8,6000010,5,5]` | `000001010100001 [15,6100000]`; `0000101000100001 [16,6010000]`; `100000010100001 [15,6100000]`; `100101010000001 [15,6100000]`; `1001010110100001 [16,6010000]` | `24=4+5+15_wrong-pair` | `{3,4,5}` |
| `Y4` | `0214350`; `0:D1+F4,4:D2,5:s` | `1 / 12` | `011000100001 [12,6010000,2,1]`; `011010000001 [12,6010000,2,1]`; `10100001 [8,6001000,3,5]`; `101010001 [9,6000010,5,4]` | `0110101000001 [13,6100000]`; `0110110101001 [13,6000100]` | `23=4+2+17_wrong-pair` | `{2,3,5}` |
| `Y5` | `0214350`; `0:D1+F4,3:D2,5:s` | `3 / 10` | `0100001 [7,6001000,3,6]`; `01010001 [8,6000010,5,5]` | `001000100001 [12,6010000]`; `001010000001 [12,6010000]`; `0010101000001 [13,6100000]`; `0010110101001 [13,6000100]` | `22=2+4+16_wrong-pair` | `{3,5}` |

Thus each row proves a word-set equality, not merely the existence of enough
witnesses.  Across the five rows the complete rank-three relation contains
17 admitted heavy-pair exits, 24 correct-pair exits rejected only by the debt
bound, and 77 tied endpoint-shortest exits rejected by the terminal packet
roles.  The singleton images in `Gamma` are derived images of the admitted
word sets.

## Derived Negative Spectra

Composing the first-corridor images with `Gamma` and adjoining the local
second-corridor images gives:

| cell | direct spectrum | one-return spectrum |
| --- | --- | --- |
| `132/2,(3,I)` | `{2,4,5}` | `{2,4,5}` |
| `213/2,(3,I)` | `{3,4,5}` | `{4}` |
| `213/2,(3,S)` | `{4}` | empty |
| `213/2,(4,I)` | `{2,3,4,5}` | `{3,5}` |
| `321/3,(3,I)` | empty by `(Empty-X)` | empty by `(Empty-X)` |

No displayed spectrum contains offset one. This final table is a set-image
calculation; all universal work is confined to Back-Solving, Return Admission,
and Heavy-Pair Exit Exhaustion above.
