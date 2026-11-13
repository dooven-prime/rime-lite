# Representation-Theoretic Companion to Fusion-Log Enumeration

Complete ordered fusion logs admit a boundary-deletion description, while
literal endpoints retain physical placement. This note linearizes their
forgetting maps and decomposes two prefix-observation towers. The set-level
objects and joint realization come from [Paper XLV](../../papers/paper45/Paper%20XLV.md)
and its [M5 Lean companion](../fusion_log_compression/lean_m5/README.md);
the representation-theoretic arguments are given below.

## 1. Actual objects and the central theorem

Fix a legal positively ordered literal start \(P_0\) with \(t\) nonempty,
disjoint named packets on \(n\) sites, where
\[
 n\ge3,\qquad 1\le s\le t\le n,\qquad d=t-s.
\]
Let \(\mathcal L=\mathcal L(P_0,d)\) be its actual complete ordered fusion
logs, \(\mathcal J=\mathcal J(P_0,d)\) its jointly attainable pairs
\((H,P)\) of such a log and an exact literal endpoint, and
\(\mathcal B=\mathrm{Endpoints}(P_0,s)\) the endpoint image. Execution words
and reachability proofs are witnesses, not additional elements of these sets.
The M5 boundary-deletion equivalence identifies
\[
 \mathcal L\simeq X_{t,d},\qquad
 X_{t,d}=\{(b_1,\ldots,b_d): b_i\in\mathbb Z/t, b_i\ne b_k\ (i\ne k)\}.
 \tag{1}
\]
Each entry is an original boundary deleted by one complete ordered fusion
record. The bijection includes both final rank-two parent bindings.

The geometric group used throughout the actual-joint tower is
\[
 G=C_t\times C_n,\qquad
 (r,k)(H,P)=(T_rH,R_kT_rP).
 \tag{2}
\]
Here \(T_r\) cyclically relabels initial **packet tokens** and their unions;
\(R_k\) rotates terminal physical sites. For unequal initial packet sizes,
\(T_r\) need not be an atom permutation. Positive cyclic order and M5's
joint-realization theorem make (2) an action on actual data from the fixed
start. It does not act on a chosen realization word or assert equality of
intermediate placements or word lengths.

On \(\mathbb C[\mathcal J]\), use its orthonormal basis of actual pairs.
For \(0\le j\le d\), let
\[
 \mathcal O_j=\{(P,H_{\le j}):(H,P)\in\mathcal J\},\qquad b_j=|\mathcal O_j|,
\]
and let \(Q_j\) average over each observation fibre. Set
\(\Delta_0=Q_0\) and \(\Delta_j=Q_j-Q_{j-1}\) for \(j\ge1\).

**Theorem 1 (regular history increments).** These operators give an
orthogonal decomposition into \(G\)-submodules,
\[
 \mathbb C[\mathcal J]
   =\mathop{\bigoplus}^{\perp}_{j=0}^{d}\operatorname{im}\Delta_j.
 \tag{3}
\]
For every existing positive depth define \(m_j=b_j/(tn)\). These are
nonnegative integers and
\[
 \begin{aligned}
 \operatorname{im}\Delta_0&\cong\mathbb C[\mathcal B],\\
 \operatorname{im}\Delta_1\oplus\mathbb C[\mathcal B]
   &\cong\mathbb C[G]^{\oplus m_1} &&(d\ge1),\\
 \boxed{\operatorname{im}\Delta_j
   \cong\mathbb C[G]^{\oplus(m_j-m_{j-1})}} &&&(2\le j\le d).
 \end{aligned}
 \tag{4}
\]
The last line is a \(G\)-module isomorphism. The observation maps determine
the increment subspaces, but do not select a canonical basis or splitting
into individual regular copies.

Thus the endpoint base contains any nonuniform geometric spectrum. The
first history layer supplies its complement to a regular module. Every
subsequent history layer consists of whole regular representations, with
zero copies allowed. Sections 3--5 give the proof and the exact multiplicities.

## 2. Two forgetting representations

The log-to-survivor map and the actual joint-to-endpoint map have different
domains, actions and kernels. Write
\[
 \begin{aligned}
 \sigma:X_{t,d}&\longrightarrow Y_{t,s},&
 \sigma(b_1,\ldots,b_d)&=(\mathbb Z/t)\setminus\{b_1,\ldots,b_d\},\\
 f_{\rm phys}:\mathcal J&\longrightarrow\mathcal B,&
 f_{\rm phys}(H,P)&=P.
 \end{aligned}
 \tag{5}
\]
The first map is equivariant for abstract \(S_t\) boundary relabelling;
the second is equivariant for (2). For either map \(f\), linearize by
\(F(e_x)=e_{f(x)}\). A normalized section is
\[
 J_f(e_y)=\frac1{|f^{-1}(y)|}\sum_{x\in f^{-1}(y)}e_x.
 \tag{6}
\]
Surjectivity gives \(FJ_f=I\), and equivariance follows because the action
bijects fibres. Hence \(\mathbb C[\mathrm{domain}]=\operatorname{im}J_f
\oplus\ker F\). The kernel is spanned by differences of basis elements in
the same fibre. In particular
\[
 \begin{aligned}
 \chi_{\ker F}&=\chi_{\mathbb C[X_{t,d}]}-\chi_{\mathbb C[Y_{t,s}]},\\
 \chi_{\ker F_{\rm phys}}
   &=\chi_{\mathbb C[\mathcal J]}-\chi_{\mathbb C[\mathcal B]}.
 \end{aligned}
 \tag{7}
\]
The first identity cannot be substituted into the second by treating physical
coordinates as a trivial factor. For \(t=n=4,s=2\), the source-only half-turn
\((2,0)\) gives abstract kernel character \(-2\) but physical kernel
character \(0\). The simultaneous half-turn \((2,2)\) gives physical
kernel character \(-8\).

Every survivor fibre in (5) has \(d!\) elements. M5's actual literal-endpoint
fibres instead have sizes
\[
 |f_{\rm phys}^{-1}(P)|=
 \begin{cases}d!,&s\ge2,\\t!,&s=1.\end{cases}
 \tag{8}
\]
At rank one the final survivor is absent from the physical endpoint. The
abstract map still remembers it, and a second map \(Y_{t,1}\to\{*\}\)
forgets it. The last ordered fusion direction remains in the complete log.
Physical phases are retained by \(f_{\rm phys}\), including at rank one.

The abstract modules are
\[
 \mathbb C[X_{t,d}]\cong\operatorname{Ind}_{S_s}^{S_t}\mathbf1,
 \qquad
 \mathbb C[Y_{t,s}]\cong
   \operatorname{Ind}_{S_s\times S_d}^{S_t}\mathbf1.
 \tag{9}
\]
These identifications follow from the stabilizers of a tuple and a subset.
They describe a transported boundary-label action; a general element of
\(S_t\) is not being asserted to preserve the physical circular geometry.

## 3. The two prefix towers and orthogonal increments

For a finite set \(\Omega\) with nested observation fibres \(B_j(x)\),
define
\[
 A_je_x=\frac1{|B_j(x)|}\sum_{y\in B_j(x)}e_y.
\]
The matrix is self-adjoint. Averaging twice leaves it unchanged, and
refinement gives
\[
 A_jA_k=A_{\min(j,k)}.
 \tag{10}
\]
Indeed averaging a finer-fibre average over a coarse fibre gives its original
coarse average: each finer denominator cancels the number of entries in that
fibre. Conversely a coarse-constant vector is already finer-constant. No
uniform fibre-size assumption is needed. If the last observation is injective,
\(A_d=I\). Expanding products of successive differences now proves
orthogonality and the resolution of identity (3). A group preserving the
observations commutes with all these operators. Normalized fibre-sum bases
identify \(\operatorname{im}A_j\) with the observation permutation module.

The first tower lives on \(\mathbb C[X_{t,d}]\) and remembers only the
first \(j\) deleted boundaries, equivalently the first \(j\) complete
records. Write its projections as \(P_j\), and increments as
\(E_0=P_0\), \(E_j=P_j-P_{j-1}\). Then
\[
 \begin{aligned}
 \dim\operatorname{im}E_0&=1,\\
 \dim\operatorname{im}E_j
   &=\frac{t!}{(t-j)!}-\frac{t!}{(t-j+1)!},&&1\le j\le d.
 \end{aligned}
 \tag{11}
\]
For a partition \(\lambda\vdash t\), let \(f^{\lambda/(q)}\) count
standard skew tableaux after removing a one-row diagram of length \(q\),
with value zero if that diagram is not contained in \(\lambda\). Then
\[
 \begin{aligned}
 [\operatorname{im}E_0:S^\lambda]&=[\lambda=(t)],\\
 [\operatorname{im}E_j:S^\lambda]
   &=f^{\lambda/(t-j)}-f^{\lambda/(t-j+1)},&&1\le j\le d.
 \end{aligned}
 \tag{12}
\]
To see this, the prefix stabilizer is \(S_{t-j}\), so
\(\operatorname{im}P_j\cong\operatorname{Ind}_{S_{t-j}}^{S_t}\mathbf1\).
The classical branching rule and Frobenius reciprocity count its restriction
paths by these skew tableaux. Subtract multiplicities of the preceding
invariant submodule. Orthogonal inclusion proves nonnegativity of the
difference. This is the log-only \(S_t\) tower.

The second tower is the actual endpoint-retaining tower of Section 1. The
joint count and the completion fibres (8) give
\[
 b_j=
 \begin{cases}
 \displaystyle\frac{t!}{s!(d-j)!}\,s\binom ns,&s\ge2,\\[2mm]
 \displaystyle n\frac{t!}{(t-j)!},&s=1,
 \end{cases}
 \qquad0\le j\le d.
 \tag{13}
\]
At visible rank \(s\ge2\), the endpoint exposes the survivor set; a
length-\(j\) prefix leaves \((d-j)!\) orders of its complement. At rank
one the survivor is invisible and the completion count is \((t-j)!\).
Every listed prefix extends to a complete admissible log, and M5 gives its
joint realization with the compatible endpoint. Thus (13) counts actual
observations, not arbitrary products of coordinates.

Consequently \(\dim\operatorname{im}\Delta_0=b_0\) and
\(\dim\operatorname{im}\Delta_j=b_j-b_{j-1}\). Moreover
\[
 \ker F_{\rm phys}
   =\mathop{\bigoplus}^{\perp}_{j=1}^{d}\operatorname{im}\Delta_j,
 \tag{14}
\]
because \(Q_0=J_{f_{\rm phys}}F_{\rm phys}\).

## 4. Endpoint characters and geometric Fourier multiplicities

For representatives \(0\le r<t\), \(0\le k<n\), the actual endpoint
character is
\[
 \chi_0(r,k)=
 \begin{cases}
 s\binom{t/\ell}{s/\ell}\binom{n/\ell}{s/\ell},
   &s\ge2,\quad r/t=k/n,\quad\ell=t/\gcd(t,r)\mid s,\\
 0,&s\ge2\text{ and otherwise},\\
 n[k=0],&s=1.
 \end{cases}
 \tag{15}
\]
At the identity \(\ell=1\). For \(s\ge2\), an endpoint consists of a
survivor set, an occupied-site set and one of their \(s\) positive cyclic
matchings. A fixed endpoint requires invariant sets with the same cyclic
index shift. On survivors the shift is \(sr/t\), and on sites it is
\(sk/n\); equality forces the synchronized fraction in (15). Both sets are
unions of length-\(\ell\) rotation orbits, giving the two binomial choices.
Every cyclic matching is then fixed. At rank one only a site rotation can
move the full packet, proving the last case.

Define
\[
 \psi_{a,b}(r,k)=
   \exp\!\left(2\pi i\left(\frac{ar}{t}+\frac{bk}{n}\right)\right),
 \qquad(a,b)\in\mathbb Z/t\times\mathbb Z/n.
\]
Character inner products applied to (15) give the base multiplicities
\[
 \boxed{\mu^{(0)}_{a,b}=\frac{s}{tn}
   \sum_{\ell\mid\gcd(t,n,s)}
     \binom{t/\ell}{s/\ell}\binom{n/\ell}{s/\ell}\,c_\ell(a+b)}
 \quad(s\ge2),
 \tag{16}
\]
and
\[
 \boxed{\mu^{(0)}_{a,b}=[a=0]}\quad(s=1).
 \tag{17}
\]
Here
\(c_\ell(q)=\sum_{0\le u<\ell,\ \gcd(u,\ell)=1}e^{2\pi iqu/\ell}\)
is the Ramanujan sum. To derive (16), parametrize the nonzero character
terms by \((r,k)=(tu/\ell,nu/\ell)\) with \(\ell\mid\gcd(t,n,s)\)
and \(u\) coprime to \(\ell\). The conjugate Fourier factor sums to
\(c_\ell(-(a+b))=c_\ell(a+b)\). The plus sign reflects the synchronized
positive rotations in (2). At rank one the sum over \(r\) instead selects
\(a=0\), leaving every site frequency once. Integrality and nonnegativity
also follow from these being multiplicities of an actual permutation module.

## 5. Proof of the regular-layer theorem and the double decomposition

At every positive depth \(j\), the \(G\) action on \(\mathcal O_j\)
is free. A fixed first complete record determines its first deleted original
boundary, so source rotation must have \(r=0\). A fixed nonempty named
literal endpoint then requires \(k=0\): a site rotation cannot leave the
position of a specified nonempty packet fixed otherwise. This argument
retains the ordered binding when only two packets remain.

Each free orbit is a copy of \(G\). Thus \(m_j=b_j/(tn)\) is an integer
and \(\operatorname{im}Q_j\cong\mathbb C[G]^{\oplus m_j}\) for every
existing positive depth. Orthogonal subtraction gives
\[
 \begin{aligned}
 [\operatorname{im}\Delta_0:\psi_{a,b}]&=\mu^{(0)}_{a,b},\\
 [\operatorname{im}\Delta_1:\psi_{a,b}]&=m_1-\mu^{(0)}_{a,b},\quad d\ge1,\\
 [\operatorname{im}\Delta_j:\psi_{a,b}]&=m_j-m_{j-1},\quad2\le j\le d.
 \end{aligned}
 \tag{18}
\]
The finite abelian group has precisely the \(tn\) characters \(\psi_{a,b}\).
Its commuting finite-order unitary operators are simultaneously diagonalizable,
and each character occurs once in the regular module. Equality of all their
multiplicities therefore proves the \(G\)-module isomorphisms (4), rather
than merely an equality of dimensions. It does not choose regular-copy bases.

For an explicit joint grading, write \(\rho\) for (2) on
\(\mathbb C[\mathcal J]\) and put
\[
 \Pi_{a,b}=\frac1{tn}\sum_{(r,k)\in G}
    \overline{\psi_{a,b}(r,k)}\rho(r,k),\qquad
 \mathcal V_{j,a,b}=\operatorname{im}(\Delta_j\Pi_{a,b}).
\]
Root-of-unity orthogonality makes the \(\Pi_{a,b}\) mutually orthogonal
spectral projections summing to identity. Equivariance makes them commute
with every \(\Delta_j\). Their products give
\[
 \boxed{\mathbb C[\mathcal J]
   =\mathop{\bigoplus}^{\perp}_{j=0}^{d}
      \mathop{\bigoplus}^{\perp}_{a,b}\mathcal V_{j,a,b},}
 \qquad\dim\mathcal V_{j,a,b}\text{ is given by (18)}.
 \tag{19}
\]
This is the combined history-depth and geometric-frequency decomposition.

All boundary cases are included:

- If \(d=0\), only the endpoint base exists and the physical forgetting
  kernel is zero. No positive-depth \(m_j\) is introduced.
- If \(s\ge2,d\ge1\), then \(b_d=b_{d-1}\) and \(\Delta_d=0\).
  The endpoint and first \(d-1\) records determine the last event. For
  \(d=1\) the vanishing layer is the first; it is not an application of
  the depth-two statement to an undefined \(m_0\).
- At rank one, \(m_j=(t-1)!/(t-j)!\). The first increment has multiplicity
  \([a\ne0]\), independent of \(b\). For \(t\ge3\), the last layer
  is regular with multiplicity \((t-1)!/2\); at \(t=2\) it is instead
  the first layer. At \(t=1\) no positive-depth layer exists.

For example, \(t=n=4,s=2\) has base multiplicities 5 at even \(a+b\)
and 4 at odd \(a+b\); \(m_1=m_2=9\). Its increment dimensions are
\(72,72,0\). At \(t=n=4,s=1\), instead, \(m_1,m_2,m_3=1,3,6\), so
the second and third layers are respectively two and three copies of
\(\mathbb C[C_4\times C_4]\). Its increment dimensions are \(4,12,32,48\).

## 6. Relation to behavioral observers

The two towers here retain prefixes of **all complete effective fusion
records**, at a fixed start and terminal rank.
[Paper XLIV](../../papers/paper44/Paper%20XLIV.md) retains origin,
selected-absorption prefixes and future per-letter event behavior. Event
selection from a whole log connects their semantics, but need not commute
with truncation at equal depth. Full and selected prefixes can be incomparable
even at a fixed literal endpoint. These modules do not identify the two
observers or determine Paper XLIV's growth spectrum.

Likewise the action (2) is defined and transported on actual log/endpoint
objects using M5's equivalences. It is not automatically a symmetry of every
raw word, its length, or its intermediate physical trajectory. Representation
kernels are linear information-loss spaces, not behavioral right congruences.
Connecting an observation to raw commands still requires the report, guard
and transition conditions of
[Paper XL](../../papers/paper40/Paper%20XL.md).
