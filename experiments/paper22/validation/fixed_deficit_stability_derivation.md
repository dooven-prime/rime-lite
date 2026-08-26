# Fixed-Deficit Stability Theorem

Status: retained auxiliary derivation ledger with an exact rational certificate
through deficit eight. The canonical Paper XXII manuscript owns the current
theorem statements and numbering. Paper XXI v1.0 is a precursor only.

## 1. Rational defect dynamics

Use the primitive integral cusp model

\[
\mathbb P^1(\mathbb Q)
=\{(n,d):\gcd(|n|,|d|)=1,\ d\ge 0\}/\{(n,d)\sim(-n,-d)\},
\qquad \infty=(1,0),
\]

and the labelled matrices

\[
S=\begin{pmatrix}0&-1\\1&0\end{pmatrix},\qquad
R=\begin{pmatrix}0&-1\\1&1\end{pmatrix},\qquad
R^{-1}=\begin{pmatrix}-1&-1\\1&0\end{pmatrix}.
\]

A rational defect state is a finite set `D` of finite rational cusps. For a
label `a` define

\[
\Phi_a(D)=a(D\cup\{\infty\})\setminus\{\infty\}.
\]

This is the exact characteristic-zero form of the finite-field sector-1 defect
recursion. Let `C_k` be the reachable rational states of cardinality `k`, and
write `C_{<=k}` for their union through level `k`.

### Lemma 1 (deficit monotonicity)

Let `pi_a=a^{-1}(infinity)`. Then

\[
|\Phi_a(D)|=|D|+1-\mathbf 1_{\pi_a\in D}.
\]

Hence every transition preserves the deficit or increases it by one.

**Proof.** The set `D union {infinity}` has cardinality `|D|+1`, and `a` is a
bijection. Removing infinity removes one point exactly when its preimage
`pi_a` belonged to `D`. The three poles are finite, so no additional case is
needed. `QED`

### Lemma 2 (anchor and same-level transport)

Every nonempty successor contains `0` or `-1`. If a transition preserves the
deficit and `D_hat=D union {infinity}`, then

\[
\widehat{\Phi_a(D)}=a\widehat D.
\]

**Proof.** The image of infinity is `0` for `S,R` and `-1` for `R^{-1}`; it is
finite and therefore remains in the successor. In a same-level transition the
pole belongs to `D`, so infinity occurs in `a(D)` and is exactly the point
removed and restored by the two hats. `QED`

### Lemma 3 (two-cusp rigidity)

An element of `PSL_2(Z)` fixing two distinct rational cusps pointwise is the
identity. Consequently, for fixed distinct rational cusps `x,y` and fixed
distinct targets `x',y'`, at most one element sends `(x,y)` to `(x',y')`.

**Proof.** If an integral determinant-one matrix has two rational eigenlines,
its two eigenvalues are rational algebraic integers. They are therefore
integers, and their product is one. Both are `1` or both are `-1`; the two
independent eigenlines then force the matrix to be `I` or `-I`, which represent
the same identity in `PSL_2(Z)`. The uniqueness statement follows by composing
two proposed transports. `QED`

### Lemma 4 (finite anchored orbit slice)

For a finite cusp configuration `X`, define

\[
\mathcal N(X)=\{gX:\infty\in gX,\quad
gX\cap\{0,-1\}\ne\varnothing,\quad g\in PSL_2(\mathbb Z)\}.
\]

Then `N(X)` is finite. More precisely, if `|X|=m`, then

\[
|\mathcal N(X)|\le 2m(m-1).
\]

**Proof.** For each normalized image choose a preimage of infinity, a distinct
preimage of one declared anchor `c in {0,-1}`, and the anchor `c`. There are at
most `2m(m-1)` such choices. Lemma 3 permits at most one group element, hence
at most one image, for each choice. `QED`

## 2. Finite low-deficit normalization

### Theorem 5 (finite rational low-deficit state space)

For every nonnegative integer `k`, the reachable set `C_{<=k}` is finite and
is computable by exact breadth-first closure under `Phi_S`, `Phi_R`, and
`Phi_R_inv`, discarding transitions of cardinality greater than `k`.

**Proof.** Induct on `k`. The base `C_0={empty}` is finite. Assume
`C_{<=k-1}` finite. There are only finitely many first-growth seeds of size
`k`, since each is one labelled successor of a state in `C_{<=k-1}`.

Take any reachable state of size `k` and choose a path to it. By Lemma 1 the
path has a first transition from size at most `k-1` to size `k`; after that
point every transition on the path preserves size. If `X` is the hatted seed,
Lemma 2 says the final hatted state is `gX` for a word `g` in the labelled
modular generators. It contains infinity by construction and contains `0` or
`-1` by the anchor part of Lemma 2. It therefore lies in `N(X)`, which is finite
by Lemma 4. A finite union over the finite seed set proves `C_k` finite.

The exact breadth-first procedure visits every reachable in-range successor.
Finiteness makes the queue terminate, while Lemma 1 proves that a discarded
state can never return to an earlier level. `QED`

This theorem uses two-cusp integral rigidity, not proper discontinuity of the
boundary action. The `PSL_2(Z)` orbit of a rational cusp is not discrete in the
topology needed for a naive boundary-discreteness argument.

## 3. Global determinant registry

For stability through deficit `k`, define the one-step guard frontier

\[
G_k=\{\Phi_a(D):D\in C_{\le k},\ |\Phi_a(D)|=k+1,\ a\in\{S,R,R^{-1}\}\}.
\]

Let `P_k` contain infinity and every cusp occurring in any state in
`C_{<=k} union G_k`. Choose the declared primitive integral vector `u_x` for
each `x in P_k`, and set

\[
M_k^{\mathrm{guard}}
=\max_{x\ne y\in P_k}|\det(u_x,u_y)|.
\]

The frontier is necessary: injectivity inside `C_{<=k}` alone does not exclude
a size-`k+1` rational successor collapsing modulo `p` and re-entering the
finite-field low-deficit graph.

### Theorem 6 (eventual fixed-deficit stability)

For every fixed `k` and every prime

\[
p>\max\{k,M_k^{\mathrm{guard}}\},
\]

reduction modulo `p` gives an isomorphism from the rational transition graph on
`C_{<=k}` to the reachable finite-field defect graph through deficit `k`.
Therefore every fixed-deficit coefficient is eventually constant, with

\[
|C_j(\mathbb F_p)|=|C_j|\qquad(0\le j\le k)
\]

for all primes satisfying the displayed bound.

**Proof.** Distinct cusps in `P_k` have a nonzero integral determinant of
absolute value at most `M_k^guard`. Such a determinant cannot vanish modulo a
prime larger than the bound. Reduction is therefore injective on the entire
registry, including infinity, and each in-range rational state retains its
cardinality. Integral matrix action commutes with reduction, so every rational
edge reduces to the corresponding finite-field edge. Global cusp injectivity
also makes the reduction map injective on states.

For surjectivity, induct along any finite-field path that remains at deficit at
most `k`. The empty state is the reduction of the rational empty state. If the
current state lifts to `D in C_{<=k}`, its next labelled rational successor is
either in `C_{<=k}` or in `G_k`. In the second case registry injectivity
preserves its cardinality `k+1`, contradicting that the finite-field path
remains in range. Thus every in-range finite successor has a rational in-range
lift. This proves graph isomorphism and the coefficient equality. `QED`

The threshold is sufficient, not sharp. Equivalently, one may require `p>k`
and that `p` avoid the finite prime support of all nonzero determinants in the
guard registry.

## 4. Exact certificate through deficit eight

`exact_rational_low_deficit.py` performs the exact integer replay. Through
`k=8` it closes on

```text
|C_k| = 1, 2, 3, 7, 19, 56, 174, 561, 1859.
```

The cumulative state registry contains 320 rational cusps including infinity,
with global maximum determinant `987`. The one-step guard registry contains
448 cusps and has `M_8^guard=1597`. The largest determinant internal to any
single configuration is only `21`; that smaller number is not a valid global
stability threshold.

The `p=23` hostile fixture makes the failure exact. The two distinct states

```text
{0,1,1/2,1/3,2,2/5,3,4}
{0,1,1/2,1/3,2,3,4,5}
```

reduce to the same defect set because `2/5` and `5` collide modulo `23`:

\[
\det((2,5),(5,1))=-23.
\]

Each state is internally injective modulo `23`, yet the exact rational layer
has 1859 states and its reduction has 1723 distinct states, exactly matching
the finite-field breadth-first layer. Hence

\[
\text{configuration-local injectivity}
\not\Rightarrow
\text{global state-registry injectivity}.
\]

This fixture refutes only the local-bound shortcut. It does not refute Theorem
6 and does not claim that `1597` is the least stabilization threshold.
