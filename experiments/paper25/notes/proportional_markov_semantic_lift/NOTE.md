# Proportional Scaling and Semantic Lifts for Finite Markov Diagnostics

## Supplementary Technical Note S1

**WuJun Chen**

Independent Researcher | RIME Program | 2026

*Supplementary Technical Note S1 is owned by Paper XXV. It shares the Paper XXV
release package and has no independent paper number, DOI, or release identity.
Its claim and validation boundary remains separately declared.*

## Abstract

A norm bound on one coordinate block of a stochastic matrix is not, by itself,
a bound on global Markov behavior. This note identifies a preservation contract
under which two important semantics do descend. If one row is varied by
increasing a direct transition probability while scaling its complete
off-target profile proportionally, then the expected hitting time of the target
decreases strictly and the stationary target mass increases strictly. The first
result follows from an entrywise resolvent comparison and rank-one
differentiation; the second uses a regeneration-cycle formula. Both yield
endpoint-evaluable uncertainty intervals. Independent edge variation breaks
the single-parameter lift, $1/P_{ij}$ is neither an upper nor a lower
hitting-time bound in three or more states, and the absolute spectral gap can be
nonmonotone even along the proportional family. These results provide a typed
semantic lift for Paper XXV perturbation certificates without turning
operator-local control into an unconditional stochastic or spectral theorem.

## 1. Scope and Preservation Contract

Let $P(a)$ be a finite irreducible row-stochastic matrix. Fix distinct states
$i,j$, keep every row except row $i$ fixed, and choose a probability profile
$p=(p_k)_{k\ne j}$. The varying row is

$$
P(a)_{ij}=a,
\qquad
P(a)_{ik}=(1-a)p_k \quad (k\ne j).
$$

This proportional-scaling contract is stronger than an interval for the single
entry $P_{ij}$: it specifies how stochasticity is restored across the rest of
the row.

The note studies three outputs:

- expected hitting time $\mathbb E_i[T_j]$;
- stationary target mass $\pi_j$;
- absolute spectral gap $1-\max_{\lambda\ne1}|\lambda|$.

They do not share one preservation theorem.

## 2. Related Work and Attribution Boundary

The hitting-time, regeneration, stationary-distribution, and fundamental-matrix
arguments belong to standard finite Markov-chain theory [1-3]. The specific
interface studied here is the proportional preservation contract: one direct
transition parameter varies while the complete off-target row profile is
scaled with it.

The hitting-time proof uses entrywise resolvent comparison followed by rank-one
differentiation. The stationary-mass proof uses a renewal-reward formula for
returns to a fixed state. Both are finite-dimensional results under explicit
transience or irreducibility hypotheses, not a general operator perturbation
theorem. The absolute-gap example supplies a negative boundary: the positive
hitting-time and stationary-mass lifts cannot be copied to the spectral gap.

Paper XXV supplies the typed coordinate-block perturbation interface. This note
uses that interface only after adding the proportional-scaling contract. A
Hilbert-frame rotation is not treated as a state partition, and a
subset-automaton potential is not identified with a pair-chain resolvent. No
claim of priority, exhaustive literature coverage, or universal stochastic
stability is made.

## 3. Hitting-Time Lift

**Theorem N1 (Proportional hitting-time lift).** Under the hypotheses of
Section 1, assume \(\rho(Q_j(a))<1\) throughout the admitted interval. Then
the expected hitting time \(E_i[T_j]\) is strictly decreasing in the
proportional parameter \(a\).

Delete target state $j$ and write $Q_j(a)$ for the transient submatrix. Let
$R(a)=(I-Q_j(a))^{-1}$. Then

$$
\frac{dR}{da}=-R(a)e_ip^\top R(a),
\qquad
\frac{d}{da}\mathbb E_i[T_j]
=-(e_i^\top R(a)e_i)(p^\top R(a)\mathbf 1)<0.
$$

Thus $\mathbb E_i[T_j]$ is strictly decreasing. A certified interval
$a\in[\ell,u]$ therefore gives

$$
\mathbb E_i[T_j](a)
\in[\mathbb E_i[T_j](u),\mathbb E_i[T_j](\ell)].
$$

Without proportional scaling, the off-target entries need not move in
entrywise order. Two exact three-state chains make the failure visible. With
source state $0$, target state $1$, and the same direct probability
$P_{01}=3/20$, define

$$
P_{\rm shortcut}=
\begin{pmatrix}
9/20&3/20&2/5\\
2/5&3/10&3/10\\
1/20&9/10&1/20
\end{pmatrix},
\qquad
P_{\rm trap}=
\begin{pmatrix}
9/20&3/20&2/5\\
2/5&3/10&3/10\\
1/20&1/20&9/10
\end{pmatrix}.
$$

Exact first-step solution gives

$$
\mathbb E_0^{\rm shortcut}[T_1]=\frac{180}{67}
<\frac{20}{3}=\frac1{P[0,1]},
\qquad
\mathbb E_0^{\rm trap}[T_1]=\frac{100}{7}
>\frac{20}{3}.
$$

Thus a single transition entry does not determine the hitting time, and
$1/P_{ij}$ is neither an upper nor a lower bound in three states. The
unconditional first-step inequality

$$
\mathbb E_i[T_j]\ge 2-P_{ij}
$$

is the surviving one-entry statement.

## 4. Stationary-Mass Lift

**Theorem N2 (Proportional stationary-mass lift).** Under the hypotheses of
Section 1 and irreducibility throughout the admitted interval, the stationary
target mass \(\pi_j(a)\) is strictly increasing in \(a\).

Use returns to state $i$ as regeneration times. For the chain stopped on
hitting $i$, define quantities independent of $a$:

$$
\begin{aligned}
t&=\mathbb E_j[T_i],\\
v&=\mathbb E_j[\text{number of visits to }j\text{ before }T_i,
\text{ including time }0],\\
h_k&=\mathbb P_k(T_j<T_i),\\
u_k&=\mathbb E_k[T_{\{i,j\}}].
\end{aligned}
$$

Set $h_i=u_i=0$, and average with $p$:

$$
h=\sum_{k\ne j}p_kh_k,
\qquad
u=\sum_{k\ne j}p_ku_k,
\qquad
c(a)=a+(1-a)h.
$$

One regeneration cycle has expected $j$-occupation and expected length

$$
N(a)=vc(a),
\qquad
D(a)=1+(1-a)u+tc(a).
$$

The renewal-reward formula gives

$$
\pi_j(a)=\frac{N(a)}{D(a)},
\qquad
\frac{d\pi_j}{da}=\frac{v[(1-h)+u]}{D(a)^2}>0.
$$

The derivative is strict because $v>0$, while $u=0$ forces the off-target
profile to be concentrated at $i$ and hence forces $h=0$. Therefore

$$
\pi_j(a)\in[\pi_j(\ell),\pi_j(u)].
$$

This theorem is not obtained from the transient comparison in Section 3; it
uses the stronger regenerative structure of the same proportional family.

## 5. Absolute Spectral-Gap Boundary

**Boundary N3 (Absolute-gap nonmonotonicity).** The proportional-scaling
contract does not imply monotonicity of the absolute spectral gap for general
finite chains with at least three states.

Consider

$$
P(a)=
\begin{pmatrix}
(1-a)/2&a&(1-a)/2\\
0&0&1\\
1/2&1/2&0
\end{pmatrix}.
$$

Its nonstationary eigenvalues are the roots of

$$
4\lambda^2+2(a+1)\lambda+3a-1=0.
$$

Direct evaluation gives gaps approximately

$$
g(0.25)=0.2873,
\qquad g(0.50)=0.5000,
\qquad g(0.75)=0.4410.
$$

The gap is therefore nonmonotone even though the row varies proportionally.
The positive hitting-time and stationary-mass theorems must not be promoted to
a general spectral-stability statement.

## 6. Interface with Paper XXV

For coordinate singleton sectors, a generator-resolved block norm is the
nonnegative transition entry itself. Paper XXV can certify an interval for that
entry, but the preservation contract in Section 1 is an additional hypothesis.
Under it, Sections 3 and 4 turn the block interval into hitting-time and
stationary-mass intervals. Section 5 shows that the same interface does not
control the absolute gap.

This note does not import the exploratory pair-chain transfer operator as a
theorem premise. A subset-automaton potential and a pair-chain resolvent live on
different carriers and in different units; relating them requires a separate
descent or comparison theorem.

## 7. Claim and Evidence Boundary

The claim map uses the historical audit identifiers `A3`, `A4`, and `A5`:
`A3` is the first-step lower bound, `A4` is Theorem N1, and `A5` is Theorem
N2. Boundary N3 is an explicit negative boundary. Random sweeps are bounded
implementation and hostile-boundary audits, not theorem proofs. The n-state
claims use only the hypotheses stated here; they do not upgrade Paper XXV's
two-state portability corollary into a general Markov theorem.

The following files form the paper-owned machine surface:

| Role | Path |
|---|---|
| Claim map | `claim-surface-map.json` |
| Bounded audit | `markov_nstate_lift_v2.json` |
| Note validator | `validate_note.py` |
| Audit validator | `validate_nstate_audit.py` |

The two validators listed above bind the declared note surface. Their checks
are local closure verification, not independent validation, and do not create
a separate release identity.

## Appendix A. Stationary-Mass Local Proof Audit

Fix distinct states $i$ and $j$. Only row $i$ varies under the contract in
Section 1. Assume the finite chain is irreducible for every admitted $a$.

1. **Regeneration cycle.** Start at $i$ and stop at the first return
   $T_i^+=\inf\{t\ge1:X_t=i\}$. Finite-state irreducibility gives a
   finite-mean return time, so renewal-reward applies.
2. **Direct branch.** With probability $a$, the first step is $j$. The expected
   number of visits to $j$ before returning to $i$ is $v$; the expected
   remaining time is $t=\mathbb E_j[T_i]$.
3. **Off-target branch.** With probability $(1-a)p_k$, the first step is
   $k\ne j$. With $h_k=\mathbb P_k(T_j<T_i)$ and
   $u_k=\mathbb E_k[T_{\{i,j\}}]$, the stopped strong Markov property gives
   expected $j$-occupation $h_kv$ and expected time to hit $i$ equal to
   $u_k+h_kt$. For $k=i$, both are zero.
4. **Profile average.** Put $h=\sum_{k\ne j}p_kh_k$ and
   $u=\sum_{k\ne j}p_ku_k$. The expected cycle occupation and length are
   $N(a)=v[a+(1-a)h]$ and $D(a)=1+(1-a)u+t[a+(1-a)h]$.
5. **Stationary ratio.** Renewal-reward gives $\pi_j(a)=N(a)/D(a)$, with
   $D(a)>0$.
6. **Derivative.** Writing $c(a)=a+(1-a)h$, the quotient rule gives

   $$
   \begin{aligned}
   N'D-ND'
   &=v[(1-h)(1+(1-a)u+tc)-c(-u+t(1-h))]\\
   &=v[(1-h)+u],\\
   \frac{d\pi_j}{da}&=\frac{v[(1-h)+u]}{D(a)^2}.
   \end{aligned}
   $$

7. **Strictness.** Since $v\ge1$, $0\le h\le1$, and $u\ge0$, the numerator is
   positive whenever $u>0$. If $u=0$, each state with $p_k>0$ must already lie in
   $\{i,j\}$; because $k\ne j$, the off-target profile is concentrated at $i$,
   so $h=0$ and the numerator is $v>0$.
8. **Endpoint interval.** Strict increase gives
   $\pi_j(a)\in[\pi_j(\ell),\pi_j(u)]$ for $a\in[\ell,u]$.

This local audit checks the algebraic proof under the declared hypotheses. It
does not establish an independent validation basis or promote the bounded
computational sweep to theorem authority.

## References

1. John G. Kemeny and J. Laurie Snell. *Finite Markov Chains*. Van Nostrand,
   1960.
2. J. R. Norris. *Markov Chains*. Cambridge University Press, 1997.
   [DOI](https://doi.org/10.1017/CBO9780511810633).
3. David A. Levin, Yuval Peres, and Elizabeth L. Wilmer. *Markov Chains and
   Mixing Times*, second edition. American Mathematical Society, 2017.
   [DOI](https://doi.org/10.1090/mbk/107).
