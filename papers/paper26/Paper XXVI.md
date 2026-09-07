# Pair-Chain Transfer Operators and Random Synchronization
## Diffusive pair absorption, rare-run waiting, and a sharp reset-word envelope

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*This paper (Paper XXVI of the RIME program) develops a stochastic
pair-transfer line for synchronizing automata. It separates deterministic
pair control, global reset control, pairwise random absorption, and global
random synchronization.*

---

## Abstract

**Problem.** Deterministic pair control, global reset control, pairwise random
absorption, and global random synchronization are distinct quantities, and
their asymptotic scales need not agree.

**Approach.** We retain the labelled unordered-pair graph exactly: its integer
adjacency counts the letters that preserve a distinct pair, and normalization
produces a substochastic transfer operator. The fundamental matrix describes
expected absorption, while Perron--Frobenius theory describes the dominant
tail scale.

**Results.** For the standard Černý family, we recover the known uniform-input
worst-pair mean in pair-transfer coordinates,

$$
H_2(C_n)
=n^3-\frac32n^2+\frac{n\bmod2}{2}
$$

and derive the Perron asymptotic

$$
1-\rho(Q_{C_n})=\frac{\pi^2}{8n^3}(1+o(1)).
$$

Thus its worst-pair mean is cubic although its deterministic reset threshold
is quadratic. An extremal advance/reset family gives

$$
rt(R_n)=n-1,
\qquad H_2(R_n)=E[\tau_{\mathrm{sync}}]=2^n-2,
\qquad 1-\rho(Q_{R_n})\sim2^{-n}.
$$

Finally, for an alphabet of size $k$ and reset threshold $r$, we prove the
sharp universal waiting envelope

$$
H_2(A)\le E[\tau_{\mathrm{sync}}]
\le\frac{k^{r+1}-k}{k-1}.
$$

The bound is sharp for every $k\ge2$: a generalized advance/reset family
attains equality. Equality requires two simultaneous extremal features: a
shortest reset word of maximal self-overlap, necessarily a constant-letter
word $a^r$, and a pair that does not absorb before the first occurrence of
that pattern. The comparison separates optimal deterministic control,
pairwise control, and random-word absorption. In particular, polynomial
deterministic synchronization does not imply polynomial stochastic absorption
without additional structural hypotheses.

**Boundary.** Exact Bernoulli-input worst-pair formulas for the Černý family
and the qualitative existence of exponentially slow random synchronization
families are prior results. The paper does not claim a general polynomial
relation between reset threshold and random absorption, a spectral proof of
the deterministic Černý conjecture, or a nontrivial zero theory for the finite
determinant function introduced below. Appendix A supplies the perturbative
control used by the leading Perron result and proves a further second-order
refinement; it is not used by TA-II or TA-III.

**Keywords:** synchronizing automata; pair automaton; transfer operator;
Perron--Frobenius theory; absorbing Markov chains; pattern waiting time;
Černý automata.

## Notation {.unnumbered}

| Symbol | Meaning |
|---|---|
| $A=(Q,\Sigma,\delta)$ | complete deterministic finite automaton |
| $n=|Q|$, $k=|\Sigma|$ | state and alphabet sizes |
| $rt(A)$ | shortest reset-word length |
| $d_2(x,y)$ | shortest word merging the pair $\{x,y\}$ |
| $D_2(A)$ | $\max_{x\ne y}d_2(x,y)$ |
| $\mathcal P_2(Q)$ | unordered distinct pairs of states |
| $\widehat T_A$ | transient pair multigraph adjacency |
| $Q_A=\widehat T_A/k$ | uniform random-letter transient matrix |
| $\tau_p$ | random absorption time from pair $p$ |
| $H_2(A)$ | worst-pair mean $\max_pE[\tau_p]$ |
| $\tau_{\mathrm{sync}}$ | first time all pairs have merged under one common random word |
| $E[\tau_{\mathrm{sync}}]$ | mean global random synchronization time |
| $\rho(Q_A)$ | Perron root of the transient matrix |

---

## Introduction

A deterministic synchronizing automaton admits a word that sends all states
to one state. The classical extremal quantity is the reset threshold
$rt(A)$, the minimum length of such a word. It is an optimal-control
quantity: at each step the controller chooses the next letter
\cite{cerny1964,volkov2008}.

There is a different natural experiment. Draw letters independently and
uniformly from $\Sigma$ and ask how long a given pair takes to merge. This is
not optimal control. It is absorption in a finite substochastic Markov chain.
The two experiments share the same automaton but need not share a complexity
scale.

The exact carrier of the random experiment is the unordered-pair transfer
operator:

$$
\boxed{
A\longmapsto\widehat T_A\longmapsto Q_A
\longmapsto\bigl((I-Q_A)^{-1},\rho(Q_A)\bigr).
}
$$

This representation should be compared with, but not identified with, the
deterministic transformation-semigroup and mass-quotient representations:

$$
\text{one automaton}
\longrightarrow
\begin{cases}
\text{controlled words and rank descent},\\
\text{random letters and pair absorption}.
\end{cases}
$$

The deterministic pair-hitting, marked-kernel, and Schreier viewpoints used
for comparison here were developed in the previous deterministic study
\cite{paper23}. That work studies controlled rank descent, whereas this paper
studies random absorption for a fixed automaton.

The distinction is forced by the examples considered here. The Černý family
has quadratic optimal reset and cubic random absorption. The advance/reset
family has linear optimal reset and exponential random absorption.
Deterministic and stochastic scales are therefore not monotone across
families. The qualitative separation and the exact Černý mean have prior
antecedents; Section 8 states the attribution boundary precisely.

### Contributions

The paper organizes its results into one exact representation and three
theorem groups.

1. The pair-chain transfer operator is exact: it is the integer adjacency of
   a labelled multigraph, not a norm-based coarse graining.
2. **TA-I (diffusive Černý regime).** The known uniform-input worst-pair mean
   is recovered in pair-transfer coordinates, and the PF gap is shown to have
   leading constant $\pi^2/8$ at scale $n^{-3}$ together with a second-order
   refinement.
3. **TA-II (extremal rare-run regime).** An advance/reset family attains the
   exact value $2^n-2$ for both worst-pair and global random synchronization
   means, and its PF gap is asymptotic to $2^{-n}$.
4. **TA-III (sharp reset-word envelope).** For alphabet size $k$ and reset
   threshold $r$, both the worst-pair mean and the global random
   synchronization mean are bounded by $(k^{r+1}-k)/(k-1)$, and this
   envelope is sharp for every $k\ge2$.

### Claim boundary

This paper does not prove a deterministic reset bound from a spectral gap. It
does not identify $D_2(A)$ with $rt(A)$, and it does not infer random
absorption from a deterministic mass potential. It also does not claim the
known exact Černý mean or the qualitative existence of exponential
random-input examples as new results.

The leading Černý spectral argument is part of the main theorem surface.
Appendix A supplies its uniform perturbation and root-window estimates and
then continues to the second-order refinement. The refinement is not needed
for the elementary TA-II/TA-III results.

---

## The exact pair-chain representation

Let

$$
\mathcal P_2(Q)=\{\{x,y\}:x,y\in Q,\ x\ne y\}.
$$

For $p=\{x,y\}$ and $a\in\Sigma$, either $a(p)$ is another distinct pair or
$a(x)=a(y)$ and the pair has merged. Define

$$
\widehat T_A[p,q]
=\#\{a\in\Sigma:a(p)=q\},
$$

and the merge multiplicity

$$
m_A(p)=\#\{a\in\Sigma:a(x)=a(y)\}.
$$

Every row satisfies the exact conservation law

$$
\sum_q\widehat T_A[p,q]+m_A(p)=k.
$$

Consequently

$$
Q_A=\frac1k\widehat T_A
$$

is substochastic. Missing row mass is precisely one-step absorption
probability.

### Proposition 2.1 (exactness)

$\widehat T_A$ is the source-row adjacency matrix of the transient unordered-
pair multigraph, with one edge for every letter that preserves distinctness.
No numerical quotient or norm aggregation enters its definition.

**Proof.** A deterministic letter maps each pair to exactly one image. If the
image is distinct it contributes one to exactly one matrix entry; otherwise it
contributes one to $m_A(p)$. Summing over letters gives the row identity. $\square$

### Proposition 2.2 (synchronization and transience)

For a finite complete deterministic automaton, the following are equivalent:

1. $A$ is synchronizing;
2. every distinct pair is mergeable by some word;
3. every state of the pair chain can reach absorption;
4. $\rho(Q_A)<1$.

**Proof.** A reset word merges every pair, so (1) implies (2). If every pair
is mergeable, repeatedly choose a pair in the current image and append a word
merging it; the image size strictly decreases, proving (2) implies (1).
Statements (2) and (3) are the same reachability assertion in the pair graph.
For a finite substochastic matrix, every state reaches missing row mass if and
only if there is no closed stochastic communicating class, which is
equivalent to spectral radius strictly below one. $\square$

### Proposition 2.3 (fundamental matrix)

Assume $A$ is synchronizing. The expectation vector
$h_p=E_p[\tau]$ is

$$
h=(I-Q_A)^{-1}\mathbf1
=\sum_{j\ge0}Q_A^j\mathbf1.
$$

**Proof.** First-step decomposition gives $h=\mathbf1+Q_Ah$.
Proposition 2.2 makes $I-Q_A$ invertible and the Neumann series convergent.
$\square$

For a single random input stream, couple all initial pairs with the same word
and define the global random synchronization time

$$
\tau_{\mathrm{sync}}=\max_{p\in\mathcal P_2(Q)}\tau_p.
$$

It follows that

$$
H_2(A)=\max_p E_p[\tau]\le E[\tau_{\mathrm{sync}}].
$$

The inequality can be strict because expectation does not commute with the
maximum.

### Proposition 2.4 (PF hitting sandwich)

Suppose $Q_A$ is irreducible and let $v>0$ be a right Perron vector. Then

$$
\frac1{1-\rho(Q_A)}
\le H_2(A)
\le\frac{v_{\max}}{v_{\min}}
\frac1{1-\rho(Q_A)}.
$$

**Proof.** The fundamental matrix $N=(I-Q_A)^{-1}$ is nonnegative and has
spectral radius $(1-\rho)^{-1}$. Its infinity norm is the maximum row sum,
which equals $H_2(A)$, proving the lower bound. Since
$\mathbf1\le v/v_{\min}$,

$$
N\mathbf1\le\frac{Nv}{v_{\min}}
=\frac{v}{v_{\min}(1-\rho)},
$$

which gives the upper bound. $\square$

The eigenvector ratio is essential. Reversibility can make spectral analysis
easier, but does not by itself bound $v_{\max}/v_{\min}$ uniformly.

---

## Four inequivalent synchronization scales

The pair-chain representation makes four scales visible:

$$
D_2(A)=\max_{x\ne y}d_2(x,y),
\qquad rt(A),
\qquad H_2(A),
\qquad E[\tau_{\mathrm{sync}}].
$$

$D_2(A)$ is optimal control for one pair. $rt(A)$ is optimal simultaneous
control of the full state set. $H_2(A)$ is the worst-pair mean under a fixed
random policy, while $E[\tau_{\mathrm{sync}}]$ is the mean time for all pairs
to merge under the same random word.

Every reset word merges every pair, hence

$$
D_2(A)\le rt(A).
$$

The inequality is generally strict. For the Černý family,

$$
D_2(C_n)=\frac{n(n-1)}2,
\qquad rt(C_n)=(n-1)^2.
$$

No corresponding general polynomial comparison with $H_2(A)$ or
$E[\tau_{\mathrm{sync}}]$ exists;
Section 5 gives an exact counterexample.

The two families studied below also reverse the deterministic ordering. For
all sufficiently large $n$,

$$
rt(R_n)=n-1<rt(C_n)=(n-1)^2,
\qquad
H_2(R_n)=2^n-2>H_2(C_n).
$$

Thus the family with the shorter deterministic reset threshold can have the
larger random pair-absorption scale. Any bridge between these carriers must
retain information about the distribution and overlap structure of useful
words; deterministic reset complexity alone cannot supply it.

![The Černý and advance/reset families reverse their ordering between
deterministic reset threshold and worst-pair random absorption. The former
has quadratic reset and cubic absorption scales; the latter has linear reset
and exponential absorption scales.](../../figures/paper26/fig1_deterministic_stochastic_separation.png)

---

## The diffusive Černý pair chain

Let $C_n$ have state set $\mathbb Z/n\mathbb Z$ and two letters:

$$
a(x)=x+1\pmod n,
$$

and

$$
b(n-1)=0,
\qquad b(x)=x\quad(x\ne n-1).
$$

The deterministic identity $rt(C_n)=(n-1)^2$ is classical.

### Lemma 4.1 (phase reduction)

Let $H(i,j)=E_{\{i,j\}}[\tau]$ for $0\le i<j\le n-1$, and let
$g(d)=H(0,d)$. While $j<n-1$, the letter $b$ is a self-loop and $a$ moves
both coordinates forward, so first-step decomposition gives

$$
H(i,j)=2+H(i+1,j+1).
$$

Solving this recurrence together with the boundary equations at $j=n-1$
gives the exact phase formula

$$
\boxed{H(i,j)=g(j-i)-2i.}
$$

In particular $H(i,j)\le g(j-i)$, so a worst pair can always be chosen with
left endpoint $0$.

**Proof.** The displayed first-step equation follows from
$H=1+\frac12H+\frac12H\circ a$. At the defect boundary, $a$ sends
$\{i,n-1\}$ to $\{0,i+1\}$ and $b$ sends it to $\{0,i\}$; substituting
$H(i,j)=g(j-i)-2i$ into these boundary equations reduces them exactly to the
recurrence for $g$ below. Uniqueness of the finite absorbing-chain system
proves the formula. $\square$

### Theorem 4.2 (Gusev's uniform-input worst-pair mean, recovered)

For $n\ge3$,

$$
\boxed{
H_2(C_n)
=n^3-\frac32n^2+\frac{n\bmod2}{2}.
}
$$

This is the uniform-input specialization of Gusev's Bernoulli-input
worst-pair formula \cite{gusev2014}. The proof below recovers it directly in
the pair-transfer coordinates used here.

**Proof.** By Lemma 4.1, it remains to compute
$g(d)=E_{\{0,d\}}[\tau]$, $1\le d\le n-1$; no rotation symmetry of the
full pair chain is being assumed. Eliminating the deterministic
interior rotations between visits to the defect gives

$$
g(d)=2(n-1-d)+1
+\frac{g(n-d)+g(n-1-d)}2,
\qquad 1\le d\le n-2,
$$

with

$$
g(n-1)=1+\frac{g(1)}2.
$$

Direct substitution verifies the unique solution

$$
g(d)=2d\bigl(2n(n-1)-(2n-1)d\bigr).
$$

This concave quadratic is maximized at the central integer distance. Evaluating
at that distance gives the displayed parity-sensitive formula. $\square$

### Lemma 4.3 (boundary generating-function collapse)

For $0\le x<x+d\le n-1$, let

$$
F_{x,d}(z)=E_{\{x,x+d\}}[z^\tau],
\qquad G_d(z)=F_{0,d}(z).
$$

If $x<n-1-d$, first-step decomposition gives

$$
F_{x,d}(z)=\frac z2F_{x,d}(z)+\frac z2F_{x+1,d}(z),
$$

and hence, with $c_d(z)=(z/(2-z))^{n-1-d}$,

$$
G_d=\frac z2c_d(G_{n-d}+G_{n-1-d})\quad(1\le d\le n-2),
$$

while

$$
G_{n-1}=\frac z2(G_1+1).
$$

Let $C_n(z)=\operatorname{diag}(c_1(z),\ldots,c_{n-1}(z))$ and define the
symmetric $(n-1)\times(n-1)$ matrix $R_0$ by

$$
R_0[d,n-d]=1\quad(1\le d\le n-1),
$$

and

$$
R_0[d,n-1-d]=1\quad(1\le d\le n-2),
$$

with all other entries zero. Then the boundary system is

$$
\boxed{
\left(I-\frac z2C_n(z)R_0\right)G(z)=\frac z2e_{n-1}.
}
$$

**Proof.** In the interior, $b$ fixes the pair and $a$ advances both
coordinates. Iterating the displayed interior identity reaches the unique
boundary pair containing $n-1$. At that boundary, $a$ gives the
$n-d$ term, $b$ gives the $n-1-d$ term, and for $d=n-1$ the latter transition
is absorption. $\square$

### Lemma 4.4 (exact base spectrum)

Put $\theta=\pi/(2n-1)$. The eigenpairs of $R_0/2$ are

$$
\boxed{
\lambda_k=(-1)^{k+1}\cos(k\theta),
\qquad u_k(d)=\sin(2kd\theta),
\quad 1\le k,d\le n-1.
}
$$

In particular the base Perron eigenvalue and a positive Perron vector are

$$
\rho_0=\cos\theta,
\qquad u_1(d)=\sin(2d\theta)>0.
$$

**Proof.** For $d<n-1$, the two nonzero entries in row $d$ give

$$
(R_0u_k)(d)=u_k(n-d)+u_k(n-1-d)
=2(-1)^{k+1}\cos(k\theta)u_k(d).
$$

The last row gives the same identity using
$u_k(1)=2(-1)^{k+1}\cos(k\theta)u_k(n-1)$. The sine vectors are mutually
orthogonal by the finite sine identity

$$
\sum_{d=1}^{n-1}\sin(2kd\theta)\sin(2\ell d\theta)
=\frac{2n-1}{4}\,\delta_{k\ell}.
$$

They are therefore nonzero and form an eigenbasis, giving the full spectrum.
Positivity identifies $k=1$ as the Perron mode. $\square$

### Lemma 4.5 (Perron pole and pencil root)

Define

$$
S_n(z)=\frac z2C_n(z)^{1/2}R_0C_n(z)^{1/2}.
$$

If $z_*>1$ is the first positive solution of
$\lambda_{\max}(S_n(z))=1$, then

$$
\boxed{z_*=\rho(Q_{C_n})^{-1}.}
$$

**Proof.** The transient pair graph of $C_n$ is irreducible and has a
self-loop, hence $Q_{C_n}$ is primitive. The positive left and right Perron
vectors imply that the Perron pole has nonzero residue in every pair-hitting
generating function, whose common radius is therefore $\rho(Q_{C_n})^{-1}$.
Lemma 4.3 is an exact elimination of those functions. Moreover,
Since $C_n(z)$ is positive diagonal for $1<z<2$, there is an actual
similarity

$$
C_n(z)^{-1/2}\left(\frac z2 C_n(z)R_0\right)C_n(z)^{1/2}
=\frac z2 C_n(z)^{1/2}R_0C_n(z)^{1/2}=S_n(z).
$$

Hence $I-(z/2)C_n(z)R_0$ is similar to $I-S_n(z)$.
For $1<z<2$, the matrix $S_n(z)$ is nonnegative and entrywise increasing;
therefore its Perron eigenvalue is the first eigenvalue to reach one. This
identifies its first positive root with the Perron pole. $\square$

### Theorem 4.6 (Černý PF asymptotic)

Let $\rho_n=\rho(Q_{C_n})$. Then

$$
\boxed{
1-\rho_n=\frac{\pi^2}{8n^3}(1+o(1)).
}
$$

Consequently

$$
\boxed{
(1-\rho_n)H_2(C_n)\longrightarrow\frac{\pi^2}{8}.
}
$$

**Proof.** By Lemmas 4.3 and 4.5, $z_*=1+\varepsilon_*$ is characterized by

$$
\lambda_{\max}(S_n(1+\varepsilon_*))=1,
\qquad \rho_n=z_*^{-1}.
$$

Lemma 4.4 identifies the simple base Perron eigenvalue
$\rho_0=\cos(\pi/(2n-1))$. In its normalized sine eigenbasis, the uniform
perturbation estimate proved in Appendix A gives, for
$\varepsilon=O(n^{-3})$,

$$
\lambda_{\max}(S_n(1+\varepsilon))
=\rho_0+\mu_0\varepsilon+O(n^2\varepsilon^2),
\qquad
\mu_0=\rho_0\left(n-\frac12\right)+O(n^{-3}).
$$

The root-window argument in Appendix A first shows
$\varepsilon_*=O(n^{-3})$, so this estimate may be evaluated at the root.
Writing $\delta=1-\rho_0=\Theta(n^{-2})$ gives

$$
\delta=\mu_0\varepsilon_*+O(n^2\varepsilon_*^2),
\qquad
\varepsilon_*=\frac{\delta}{\mu_0}(1+o(1)).
$$

Since $1-\rho_n=\varepsilon_*/(1+\varepsilon_*)$, it follows that

$$
1-\rho_n
=\frac{1-\rho_0}{\rho_0(n-1/2)}(1+o(1))
=\frac{\pi^2}{8n^3}(1+o(1)).
$$

The product limit follows from Theorem 4.2. $\square$

### Second-order refinement

A sharper analytic refinement is given by Theorem A.1. It identifies the
coefficient $\gamma_2=\pi^2/24-3/4$ for the normalized product
$(1-\rho_n)H_2(C_n)$ and includes the uniform third-order remainder, the parity
bookkeeping, and the root-window argument. The leading controls in Appendix A
are required by Theorem 4.6; the additional second-order conclusion is not
used by TA-II or TA-III.

---

## The rare-run regime

Let $R_n$ have states $\{0,\ldots,n-1\}$, put $z=n-1$, and define

$$
a(i)=\begin{cases}i+1,&i<z,\\z,&i=z,\end{cases}
\qquad
b(i)=\begin{cases}0,&i<z,\\z,&i=z.\end{cases}
$$

### Theorem 5.1 (linear reset, exponential absorption)

For $n\ge2$,

$$
\boxed{
rt(R_n)=n-1,
\qquad H_2(R_n)=E[\tau_{\mathrm{sync}}]=2^n-2.
}
$$

**Proof.** The word $a^{n-1}$ sends every state to $z$, so
$rt(R_n)\le n-1$. The pair $\{0,z\}$ cannot merge before the first coordinate
has advanced $n-1$ times without an intervening $b$, giving the reverse
inequality.

Under random letters, $z$ remains fixed. Starting from $\{0,z\}$, letter $a$
advances the first coordinate and letter $b$ resets it to zero. Absorption is
therefore the waiting time for a run of $n-1$ consecutive $a$'s. The standard
run recurrence gives

$$
E[T_r]=2+2^2+\cdots+2^r=2^{r+1}-2.
$$

With $r=n-1$, this is $2^n-2$. For $i>0$, the pair $\{i,z\}$ starts with
partial progress toward the same run and has expectation
$2^n-2^{i+1}<2^n-2$. A pair not initially containing $z$ either merges at
the next $b$, or enters one of these $z$-pair states after a run of $a$'s;
its first-step recurrence is therefore also bounded by the $\{0,z\}$ value.
The whole automaton also synchronizes exactly at the first run of $n-1$
copies of $a$: state $0$ cannot reach the fixed state $z$ sooner, whereas
such a run sends every state to $z$. Hence the worst-pair and global means
coincide.
$\square$

### Theorem 5.2 (rare-run PF gap)

Let $\rho_n=\rho(Q_{R_n})$. Then

$$
2(1-\rho_n)(2\rho_n)^{n-1}=1
$$

and hence

$$
\boxed{
1-\rho_n
=2^{-n}\bigl(1+O(n2^{-n})\bigr).
}
$$

In particular,

$$
(1-\rho_n)H_2(R_n)\longrightarrow1.
$$

**Proof.** Ordering transient pairs by whether they contain $z$, the full
matrix is block triangular. The block of pairs not containing $z$ is
nilpotent, while the $z$-pair block is irreducible and carries the Perron
root. This Perron block consists of
$\{0,z\},\ldots,\{n-2,z\}$. With $v_0=1$, its right eigenvector recurrence is

$$
v_{j+1}=2\rho_nv_j-1,
$$

and therefore

$$
v_j=(2\rho_n)^j
-\frac{(2\rho_n)^j-1}{2\rho_n-1}.
$$

The absorbing boundary $v_{n-1}=0$ gives the characteristic equation. Writing
$\varepsilon_n=1-\rho_n$ in that equation gives

$$
\varepsilon_n
=2^{-n}(1-\varepsilon_n)^{-(n-1)}
=2^{-n}\bigl(1+O(n2^{-n})\bigr).
$$

The product limit follows from Theorem 5.1. $\square$

### Corollary 5.3 (no unconditional polynomial bridge)

There is no universal implication from a polynomial reset threshold to either
random-input mean:

$$
rt(A_n)=\operatorname{poly}(n)
\not\Longrightarrow
\left\{
\begin{array}{l}
H_2(A_n)=\operatorname{poly}(n),\\
E[\tau_{\mathrm{sync}}]=\operatorname{poly}(n).
\end{array}
\right.
$$

and no universal polynomial lower bound on $1-\rho(Q_A)$ can follow from a
polynomial reset threshold alone.

---

## A sharp reset-word waiting envelope

For a word $w$ of length $r$, let $B(w)\subseteq\{1,\ldots,r\}$ be its border
lengths, including $r$ itself. For an iid uniform $k$-letter stream, the exact
pattern waiting formula is

$$
E[T_w]=\sum_{j\in B(w)}k^j.
$$

### Theorem 6.1 (universal envelope)

Let $A$ be a synchronizing automaton with at least two states over an alphabet
of size $k\ge2$, and let $rt(A)=r\ge1$. Then

$$
\boxed{
H_2(A)
\le E[\tau_{\mathrm{sync}}]
\le\frac{k^{r+1}-k}{k-1}.
}
$$

**Proof.** Fix a shortest reset word $w$ of length $r$. Whenever $w$ occurs as
a contiguous block in the random stream, every currently surviving pair is
merged by the end of that block. Thus $\tau_p\le T_w$ under the natural
coupling, for every initial pair $p$. The border formula and
$B(w)\subseteq\{1,\ldots,r\}$ give

$$
E[\tau_p]\le E[T_w]
\le k+k^2+\cdots+k^r
=\frac{k^{r+1}-k}{k-1}.
$$

The first inequality was established after Proposition 2.3. The occurrence of
$w$ merges all pairs under the same coupling, so
$\tau_{\mathrm{sync}}\le T_w$ almost surely. Taking expectations gives the
second inequality. $\square$

### Proposition 6.2 (sharpness for every alphabet size)

For every $k\ge2$ and $r\ge1$, there exists a synchronizing automaton with
alphabet size $k$, reset threshold $r$, and

$$
H_2(A)=E[\tau_{\mathrm{sync}}]=\frac{k^{r+1}-k}{k-1}.
$$

**Proof.** Use states $\{0,\ldots,r\}$ with sink $z=r$. Let one letter $a$
advance $i\mapsto i+1$ until $z$, and let each of the other $k-1$ letters
reset every non-sink state to $0$ while fixing $z$. Then $a^r$ is a shortest
reset word. The pair $\{0,z\}$ and the full state set synchronize exactly when
the random stream first contains $r$ consecutive copies of $a$. For success
probability $1/k$, the
classical run-waiting expectation is

$$
E[T_{a^r}]
= k+k^2+\cdots+k^r
=\frac{k^{r+1}-k}{k-1}.
$$

Thus both inequalities in Theorem 6.1 are sharp for every $k\ge2$. $\square$

### Proposition 6.3 (equality mechanism)

Let $A$ have alphabet size $k$ and reset threshold $r$. The pairwise endpoint
$H_2(A)$ equals the upper envelope in Theorem 6.1 if and only if there exist a
letter $a$ and a pair $p$ such that
$a^r$ is a shortest reset word and, under the uniform random input,

$$
\tau_p=T_{a^r}\qquad\text{almost surely}.
$$

Equivalently, the extremal case combines maximal reset-word autocorrelation
with no premature absorption of the extremal pair.

**Proof.** If these conditions hold, $a^r$ has every border length
$1,\ldots,r$, so its waiting time attains the upper bound in Theorem 6.1, and
the pair attains the same expectation. Conversely, suppose equality holds and
choose a pair $p$ attaining $H_2(A)$. For any shortest reset word $w$ of
length $r$, the natural
coupling gives $\tau_p\le T_w$ almost surely. Hence equality of the universal
bound forces equality throughout

$$
E[\tau_p]\le E[T_w]\le\sum_{j=1}^r k^j.
$$

The second equality requires all border lengths $1,\ldots,r$, which forces
$w=a^r$ for some letter $a$. Since $T_w-\tau_p\ge0$ and has expectation zero,
$T_w=\tau_p$ almost surely. $\square$

The envelope is exponential in reset threshold and therefore cannot support
a general polynomial spectral shortcut. The Černý family lies far below this
worst envelope, whereas the generalized rare-run construction saturates it.
This separates diffusive pair transport from pattern-autocorrelation
slowness.

---

## Discussion: determinant encoding

For any finite transfer matrix $T$, one may define

$$
Z_T(s)=\det(I-sT)^{-1}.
$$

This is a rational function. It is analytic near $s=0$ and has automatic
meromorphic continuation to the Riemann sphere. Its finite poles are the
reciprocals of the nonzero eigenvalues of $T$, counted with algebraic
multiplicity. Because its numerator is the constant one, it has no finite
zeros.

Equivalently, the reciprocal polynomial

$$
L_T(s)=\det(I-sT)
$$

has zeros at the reciprocal eigenvalues. This repackages finite spectral data;
it does not by itself create a nontrivial analytic-continuation or critical-
line problem. For the pair chain, the meaningful dominant singularity is
$s=\rho(Q_A)^{-1}$, because it controls absorption asymptotics.

Accordingly, the proof-facing objects are $Q_A$, its resolvent, its Perron
eigenpair, and explicit family geometry. The determinant notation is only a
compact encoding of finite spectral data, not a separate zeta theory.

---

## Related Work and Novelty Boundary

### Deterministic synchronization

The deterministic line asks for one controlled word or one admissible rank-
descent route. Its algebra is existential and min-plus. The pair-chain line
averages all letters under a fixed random policy. Its algebra is linear and
Perron--Frobenius.

The rare-run theorem shows that a bridge cannot depend only on $rt(A)$ or on a
deterministic potential that merely bounds $rt(A)$. A valid future bridge must
add information controlling the distribution of useful words. Plausible
hypotheses include:

- bounded reset-word border complexity or autocorrelation;
- a Doeblin or minorization condition on rank-decreasing events
  \cite{meynTweedie2009};
- reversible pair chains with a controlled Perron eigenvector ratio
  \cite{levinPeresWilmer2017};
- typed per-rank coupling between random pair motion and deterministic
  checkpoint geometry.

None of these is asserted generally here. The current conclusion is a clean
separation of representations:

$$
\boxed{
\text{same automaton, different carriers, different complexity notions}.
}
$$

### Random-input and transfer-operator literature

The pair graph is classical in deterministic synchronization theory, where it
supports pair-merging distances and reset-word arguments
\cite{volkov2008,gonzeEtAl2019,ananichevVolkovZaks2007}. The recent
deterministic treatment \cite{paper23} further retains marked transformation
kernels and Schreier-corridor geometry. The present use is different: every
letter-preserving pair transition is retained with its integer multiplicity and
then normalized to a substochastic matrix. The resulting fundamental matrix
and Perron root belong to the random-input problem, not to the optimal-control
problem.

Gusev derived exact worst-pair mean formulas for the Černý family under
Bernoulli input and showed that the selected central pair is maximal
\cite{gusev2014}. Setting both letter probabilities to $1/2$ yields Theorem
4.2. Gusev's cycle and defect letters are named oppositely to ours, so any
comparison of the nonuniform formulas must swap the associated probability
labels. Theorem 4.2 is therefore a recovery in the present transfer notation,
not a new expectation formula.

The same work also exhibited a fixed automaton family with exponential random
synchronization time under a linearly long prescribed pattern
\cite{gusev2014}. Related studies treat random automaton models and random-input
synchronization under their respective hypotheses
\cite{skvortsovZaks2010,berlinkovNicaud2018,chapuyPerarnau2025}. Accordingly,
TA-II does not claim the qualitative deterministic--stochastic separation as
new. Its contribution is the extremal advance/reset realization with exact
mean $2^n-2$, its Perron-gap asymptotic, and its role in attaining the sharp
universal envelope and equality mechanism of Section 6.

The reset-word envelope uses classical border and overlap formulas for waiting
for one prescribed word \cite{guibasOdlyzko1980,guibasOdlyzko1981Periods,
guibasOdlyzko1981Overlap}. A full pair chain can absorb through many words, so
the single-pattern formula is an upper-bound device rather than a complete
description of its spectrum. Absorbing-chain and quasi-stationary arguments
used here are standard \cite{kemenySnell1961,darrochSeneta1965,seneta1967,
seneta2006}.

The references listed below are the release bibliography. The comparison is
bounded to the cited literature and is not an exhaustive novelty claim.

---

## Claim status and evidence

The paper keeps proof, exact finite calculation, and bounded computation
separate. The following table is the reader-facing claim map.

| Claim | Status | Carrier or source |
|---|---|---|
| Exact pair-chain representation and absorbing-chain equations | Theorem | Sections 2--3 |
| Known uniform-input Černý expectation, recovered | Theorem | Theorem 4.2; Gusev \cite{gusev2014} |
| TA-I leading Perron-gap asymptotic | Theorem | Theorem 4.6 |
| TA-II extremal rare-run formulas and Perron gap | Theorem | Theorems 5.1--5.2 |
| TA-III universal waiting envelope | Theorem | Theorem 6.1 |
| TA-III sharpness and equality mechanism | Theorem / Proposition | Propositions 6.2--6.3 |
| Second-order Černý refinement | Theorem | Theorem A.1 |

The numerical scripts validate exact constructions, reproduce the displayed
finite observations, or cross-check asymptotic formulas. They do not upgrade a
computational observation to a theorem. The public evidence companion is in
`experiments/paper26/`.

## Conclusion and outlook

The unordered-pair transfer operator is an exact stochastic carrier for a
fixed deterministic automaton. It makes four scales explicit: one-pair
control, simultaneous reset, pairwise random absorption, and global random
synchronization. The Černý and rare-run families show that these scales
can separate, while the reset-word envelope identifies the sharp
pattern-waiting obstruction. In particular, the two families reverse their
ordering between deterministic reset threshold and worst-pair random
absorption.

The new results concern the Černý pair-chain Perron asymptotics and
second-order refinement, the exact extremal rare-run realization, and the
sharp reset-word envelope with its equality mechanism. They do not form a
bridge from random spectra to the deterministic Černý conjecture. A
future bridge would need hypotheses controlling useful-word distribution or
the geometry of the Perron eigenvector. The deterministic mass/macrograph
program and the stochastic pair-chain program may share automata, but they do
not share a theorem interface automatically.

The finite determinant function $Z_T(s)=\det(I-sT)^{-1}$ remains useful as a
compact encoding of finite spectral data. Its rationality and meromorphic
continuation are automatic; any deeper zero statement would be a different
problem and is outside the scope of this paper.

## Appendix A: Explicit Černý second-order refinement

The proof below records the exact pencil, selection-rule estimates, uniform
third-order bound, and root expansion needed for the second-order coefficient.
The paper-owned companion contains a supplementary line-by-line verification
of the explicit constants; that record is not a logical premise of the theorem.

**Theorem A.1 (Second-order Černý refinement).**

As $n\to\infty$,

$$
\boxed{
1-\rho_n=\frac{\pi^2}{8n^3}
\left[1+\frac{3}{2n}
+\left(\frac32+\frac{\pi^2}{24}\right)\frac1{n^2}
+o(n^{-2})\right].
}
$$

Consequently,

$$
\boxed{
(1-\rho_n)H_2(C_n)=\frac{\pi^2}{8}
\left[1+\left(\frac{\pi^2}{24}-\frac34\right)\frac1{n^2}
+o(n^{-2})\right].
}
$$

In particular, the relative $n^{-1}$ coefficient vanishes and

$$
\boxed{
\gamma_1=0,
\qquad
\gamma_2=\frac{\pi^2}{24}-\frac34.
}
$$

The proof occupies Sections A.1--A.4.

### Uniform Feshbach estimate

Let $\theta=\pi/(2n-1)$, $\rho_0=\cos\theta$, and write the symmetrized
two-channel pencil in the eigenbasis of the unperturbed operator as
$H(\varepsilon)=a(\varepsilon)\Lambda+b(\varepsilon)\widetilde D$, where

$$
\boxed{
\begin{gathered}
f_m(\varepsilon)=\frac{1+\varepsilon}{2}
\left(\frac{1+\varepsilon}{1-\varepsilon}\right)^m,\\
A=f_{(n-2)/2},\qquad B=f_{(n-1)/2},\qquad
a=A+B,\qquad b=\frac{B-A}{2}.
\end{gathered}
}
$$

For completeness, split the matrix of Lemma 4.3 as $R_0=R_a+R_b$,
where $R_a[d,n-d]=1$ and $R_b[d,n-1-d]=1$ on their respective index
ranges, and put $D=R_b-R_a$. If $U$ is the orthonormal sine eigenbasis from
Lemma 4.4, then

$$
\Lambda=U^T(R_0/2)U=\operatorname{diag}(\lambda_1,\ldots,\lambda_{n-1}),
\qquad \widetilde D=U^TDU.
$$

These definitions give the displayed two-channel pencil exactly. They also
fix the later notation
$g_k=\rho_0-\lambda_k$ and
$v=(\widetilde D_{21},\ldots,\widetilde D_{n-1,1})^T$.

For the audited constants $N_3=64$ and $c_0=4$, and for
$n\ge N_3$ and $0\le\varepsilon\le c_0n^{-3}$, Taylor's theorem gives

$$
\begin{aligned}
a&=1+a_1\varepsilon+a_2\varepsilon^2+r_a,
&|r_a|&\le8n^3\varepsilon^3,\\
b&=b_1\varepsilon+b_2\varepsilon^2+r_b,
&|r_b|&\le8n^2\varepsilon^3,
\end{aligned}
$$

with

$$
a_1=n-\frac12,\qquad a_2=\frac{2n^2-2n-1}{4},
\qquad b_1=\frac14,\qquad b_2=\frac{2n-1}{8}.
$$

The derivative bounds behind these constants are uniform on the whole
window: $f_m\le0.501$, $|L_m'|\le1.001n$, $|L_m''|\le2$, and
$|L_m'''|\le2.01n$, where $L_m=\log f_m$. For the odd channel, writing
$q=((1+\varepsilon)/(1-\varepsilon))^{1/2}$ and $b=A(q-1)/2$ gives
$|b'''|\le48n^2$.

### Lower-block control

The mode gaps satisfy

$$
g_k=\rho_0-\lambda_k,\qquad
g_k\ge4n^{-2}\quad(k\ge2),
$$

using the even/odd parity split of the cosine modes. If $G=\operatorname{diag}
(g_k)_{k\ge2}$ and $v$ is the Perron-row coupling, the selection-rule sums
can be made explicit as follows.

**Lemma A.2 (Perron-row selection rule).** For $2\le k\le n-1$,

$$
\boxed{
\widetilde D_{1k}=(-1)^k\frac{4\sin\theta}{2n-1}
\frac{\sin(k\theta)}
{\cos\theta-(-1)^k\cos(k\theta)}.
}
$$

Moreover, for even $k$,

$$
|\widetilde D_{1k}|\le\frac{8\pi^2}{3(2n-1)k},
\qquad g_k=\cos\theta+\cos(k\theta)\ge\frac12,
$$

whereas for odd $k\ge3$,

$$
|\widetilde D_{1k}|\le\frac{8\pi^2k}{(2n-1)^3},
\qquad
g_k=\cos\theta-\cos(k\theta)
\ge\frac{16k^2\theta^2}{9\pi^2}.
$$

**Proof.** By the finite sine orthogonality identity in Lemma 4.4, the
unnormalized vectors satisfy $\|u_k\|^2=(2n-1)/4$. Evaluating $u_1^TDu_k$
with the finite Dirichlet sine sum gives the boxed identity. For even $k$, factor
$\cos\theta-\cos(k\theta)$ into two sines; for odd $k$, use
$\cos\theta+\cos(k\theta)\ge\cos\theta$. The elementary bounds
$2x/\pi\le\sin x\le x$ on $[0,\pi/2]$ give the two displayed estimates.
Summing the even and odd classes separately, using
$\sum_{k\ge1}k^{-2}=\pi^2/6$, gives

$$
\begin{aligned}
v^TG^{-1}v
&\le \frac{16\pi^6}{27(2n-1)^2}
+\frac{18\pi^4}{(2n-1)^3},\\
v^TG^{-2}v
&\le \frac{1}{(2n-1)^2}
\left(\frac{32\pi^6}{27}+\frac{81\pi^6}{32}\right).
\end{aligned}
$$

In particular, for $n\ge64$,

$$
v^TG^{-1}v\le200n^{-2},\qquad
v^TG^{-2}v\le1000n^{-2}.
$$

Finally, $\|\widetilde D\|=\|D\|\le2$ by orthogonal invariance. $\square$

Relative to the Perron mode, the exact block decomposition is

$$
H(\varepsilon)=
\begin{pmatrix}
a\rho_0+b\widetilde D_{11} & bv^T\\
bv & a\Lambda_\perp+b\widetilde D_\perp
\end{pmatrix}.
$$

For an eigenvalue $\lambda$ in the Perron branch, define the lower Schur block

$$
\boxed{
K(\lambda,\varepsilon)
=\lambda I-\bigl(a\Lambda_\perp+b\widetilde D_\perp\bigr).
}
$$

The diagonal entry obeys $|\widetilde D_{11}|\le3n^{-3}$. Weyl's
inequality and the scalar bounds imply, throughout the same window,

$$
E=(a-1)I+(\lambda-a\rho_0)G^{-1}
-bG^{-1/2}\widetilde D_\perp G^{-1/2},
$$

and hence

$$
\|E\|\le2n\varepsilon+n^2\varepsilon
\le\frac8{n^2}+\frac4n<\frac12,
$$

for the weighted lower-block perturbation
$K(\lambda,\varepsilon)=G^{1/2}(I+E)G^{1/2}$. Thus $K$ is invertible before
the Perron root is specialized, and

$$
\left|v^T(K^{-1}-G^{-1})v\right|\le800\varepsilon.
$$

### Remainder and coefficient assembly

Taking the Schur complement of the displayed block gives the exact identity

$$
\lambda=a\rho_0+b\widetilde D_{11}+b^2v^TK^{-1}v.
$$

Consequently

$$
\lambda=\rho_0+\mu_0\varepsilon+\nu_0\varepsilon^2+R_3(n,\varepsilon),
$$

where

$$
\mu_0=a_1\rho_0+b_1\widetilde D_{11},
\qquad
\nu_0=a_2\rho_0+b_2\widetilde D_{11}+b_1^2v^TG^{-1}v,
$$

and

$$
\boxed{|R_3(n,\varepsilon)|\le16n^3\varepsilon^3.}
$$

The four contributions are bounded respectively by
$8n^3\varepsilon^3$, $24\varepsilon^3/n$, $800\varepsilon^3$, and
$2\varepsilon^3$. The last bound uses

$$
|b-b_1\varepsilon|\le\left(\frac n4+\frac{32}{n}\right)\varepsilon^2,
\qquad |b+b_1\varepsilon|\le\frac{3}{4}\varepsilon.
$$

### Root window and the coefficient

The same estimates give $\mu_0\ge0.95n$ and $\nu_0>0$. Put

$$
\varepsilon_b=\frac{2(1-\rho_0)}{\mu_0}.
$$

Then

$$
\varepsilon_b<4n^{-3},
\qquad
|R_3(n,\varepsilon_b)|<\frac{1-\rho_0}{2}.
$$

Since $\lambda_{\max}(H(\varepsilon_b))>1$ and the original symmetrized
matrix $S_n(z)$ is entrywise nonnegative with every nonzero entry strictly
increasing for $z\in(1,2)$, its Perron eigenvalue is strictly increasing.
Hence its unique root lies in the stated window.
At that root, put $\delta=1-\rho_0$. The expansions used in the coefficient
assembly are

$$
\mu_0=n-\frac12-\frac{\pi^2}{8n}-\frac{\pi^2}{16n^2}+O(n^{-3}),
\qquad
\nu_0=\frac{n^2}{2}+O(n),
$$

and the root equation gives

$$
\varepsilon_*=\frac{\delta}{\mu_0}
-\frac{\nu_0\delta^2}{\mu_0^3}+O(n^{-7}).
$$

Substitution, followed by the elementary expansion of $\rho_0$, yields

$$
1-\rho_n=\frac{\pi^2}{8n^3}
\left[1+\frac{3}{2n}
+\frac{3/2+\pi^2/24}{n^2}+o(n^{-2})\right],
$$

and, using Theorem 4.2,

$$
\boxed{
(1-\rho_n)H_2(C_n)
=\frac{\pi^2}{8}
\left[1+\frac{\pi^2/24-3/4}{n^2}+o(n^{-2})\right].
}
$$

The relative $n^{-2}$ coefficient separates into

$$
\gamma_2^{\mathrm{linear}}=\frac{5\pi^2}{48}-\frac34,
\qquad
\Delta\gamma_2^{\mathrm{curvature}}=-\frac{\pi^2}{16}.
$$

Therefore

$$
\boxed{\gamma_2=\frac{\pi^2}{24}-\frac34.}
$$

The proof is uniform for $n\ge64$, which is sufficient for the asserted
asymptotic expansion. No numerical regression enters the argument. This proves
Theorem A.1. $\square$

---

## Appendix B: Computational Artifacts

All listed artifacts are available in the
[RIME repository](https://github.com/dooven-prime/rime-lite) under
`experiments/paper26/`; short paths below are relative to that directory.

| Artifact | Role | Short path |
|---|---|---|
| implementation | pair transfer, absorption, Perron gap, and reset length | `pair_chain.py` |
| producer | Černý and rare-run finite records | `generate_family_results.py` |
| family records | exact fields and bounded float64 spectral observations | `results/` |
| analytic supplement | explicit constants and root-window verification | `u3-proof.md` |
| partial formalization | TA-III arithmetic and conditional certificate chain | `lean/` |
| claim and closure metadata | attribution, evidence status, and exact release inventory | `claim-surface-map.json`; `release-manifest.json` |
| validation | source digests, finite replay, and Lean closure | `validation/` |

The JSON records reproduce finite instances of the exact family formulas; they
do not prove the asymptotic statements. The explicit U3 document is
supplementary verification for Theorem A.1. A passing package validator
establishes local path, status, hash, and replay closure. It is not independent
mathematical validation and does not replace the manuscript proofs.
