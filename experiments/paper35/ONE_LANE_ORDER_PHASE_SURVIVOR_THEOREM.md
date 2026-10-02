# One-Lane Order, Phase, and Survivor Theorem

**Status:** paper-owned supplementary proof note for Paper XXXV.

**Evidence role:** digest-bound supplementary proof artifact. The manuscript
owns and proves the theorem. The finite audit in this directory is a bounded
consistency control and is not used to prove the
all-$n$ statements below.

## 1. Scope and inherited lemmas

Fix

$$
n\ge 6,\qquad Q=\mathbb Z/n\mathbb Z,\qquad E=Q\setminus\{0\},
$$

with $p(q)=q+1$, marked collapse
$\varepsilon_1(0)=1$, and an arbitrary branch permutation
$a\in\operatorname{Sym}(E)$. Let $T_0$ be a five-element source-label set and
$\lambda_0:T_0\hookrightarrow E$ a source injection. Write
$\mathcal L_a(\lambda_0)$ for the injections reachable by unbudgeted guarded
returns

$$
\phi_r=\varepsilon_1p^ra.
$$

The proof uses two inherited raw lemmas.

1. **Order-fiber saturation.** If one injection with cyclic lineage order
   $\omega$ is reachable, every injection into $E$ with order $\omega$ is
   reachable.
2. **Exact order reduction.** If $R_a$ is the 24-state cyclic-order relation
   induced by $a$, then the reachable order set is
   $\Omega_a^{\rm reach}=\operatorname{Reach}_{R_a}(\omega_0)$.

No typed transfer, ancestry, authorization, projectability, length budget, or
settlement statement is used.

## 2. Terminal-phase collapse

The label-zero return is $a_\#$ and is globally enabled: a permutation of $E$
maps every injection into $E$ to another injection into $E$. Since $a$ has
finite order, a positive power of the same return realizes $a^{-1}_\#$. Hence

$$
\boxed{a_\#\mathcal L_a(\lambda_0)=\mathcal L_a(\lambda_0).}
\tag{P35.1}
$$

Fix a candidate fused pair $F\subset T_0$, $|F|=2$, and a formal terminal
placement

$$
\mu:T_0\hookrightarrow Q,
\qquad
\mu(F)=\{0,1\}.
$$

For $u\in Q$,

$$
0\notin p^{-u}\mu(T_0)
\iff
u\notin\mu(T_0).
$$

Thus $u$ is a well-typed terminal phase exactly when it is a hole of $\mu$.
For such a hole, put

$$
\lambda_u=a^{-1}p^{-u}\mu:T_0\hookrightarrow E.
$$

By (P35.1),

$$
\lambda_u\in\mathcal L_a
\iff
p^{-u}\mu\in\mathcal L_a.
$$

The rotation $p^{-u}$ and deletion of the empty coordinate $0$ preserve the
oriented cyclic order of the five labels. Order-fiber saturation therefore
gives

$$
\lambda_u\in\mathcal L_a
\iff
\operatorname{ord}_Q(\mu)\in\Omega_a^{\rm reach}.
$$

The right-hand side is independent of $u$. Consequently

$$
\boxed{
\Phi_a(\mu)=
\begin{cases}
Q\setminus\mu(T_0),
&\operatorname{ord}_Q(\mu)\in\Omega_a^{\rm reach},\\[1mm]
\varnothing,
&\operatorname{ord}_Q(\mu)\notin\Omega_a^{\rm reach}.
\end{cases}}
\tag{P35.2}
$$

Every attainable terminal placement therefore has exactly $n-5$ phase
witnesses. These witnesses remain distinct; the theorem does not quotient
them.

The same calculation proves the exact terminal criterion. If
$\operatorname{ord}_Q(\mu)\in\Omega_a^{\rm reach}$, choose any hole $u$ and
use $\lambda_u$; then

$$
p^ua\lambda_u=\mu.
$$

The converse follows by reading the order of an existing witness. Thus

$$
\boxed{
\mu\text{ is attainable}
\iff
\operatorname{ord}_Q(\mu)\in\Omega_a^{\rm reach}.}
\tag{P35.3}
$$

## 3. Eight pattern classes and the order subgroup

Let $G=\operatorname{Sym}(T_0)\cong S_5$, let $\omega_0$ be the source cyclic
order, and let $H=\operatorname{Stab}_G(\omega_0)\cong C_5$. Diagonal
$G$-orbits on cyclic-order pairs are indexed by $H\backslash G/H$. The exact
branch signature $\mathcal P_5(a)$ is the set of double cosets whose orbitals
occur in $R_a$.

Choose one representative $g_D$ from every
$D\in\mathcal P_5(a)$ and define

$$
K_a^{\rm ord}=\langle H,g_D:D\in\mathcal P_5(a)\rangle\le S_5.
$$

This subgroup is independent of the representatives, because replacing
$g_D$ by an element of $Hg_DH$ does not change a subgroup already containing
$H$. An $R_a$-step is multiplication by one of these double cosets. Conversely
every representative step is present in its orbital. Since the generated
semigroup is finite, it is the generated subgroup. Hence, with the fixed
left-coset convention,

$$
\boxed{\Omega_a^{\rm reach}\cong K_a^{\rm ord}/H.}
\tag{P35.4}
$$

Here $K_a^{\rm ord}/H$ is a left-coset space, not a quotient group.

The group $K_a^{\rm ord}$ acts on source-label orders. It is not the physical
return group on carrier coordinates.

Because the eight-pattern signature reconstructs $R_a$ exactly, (P35.2)--
(P35.4) imply

$$
\boxed{
\mathcal P_5(a)=\mathcal P_5(b)
\Longrightarrow
\Omega_a^{\rm reach}=\Omega_b^{\rm reach}
\Longrightarrow
\Phi_a=\Phi_b.}
\tag{P35.5}
$$

Thus a same-pattern, different-phase counterexample cannot occur in the
present scope.

## 4. Complete survivor spectrum

Put $R_0=T_0\setminus F$. Choose a temporary naming
$F=\{f_0,f_1\}$ and write a linear order of the three survivor labels as
$(s_1,s_2,s_3)$. Let $M_a(F)$ contain this order exactly when

$$
[f_0,f_1,s_1,s_2,s_3]
\quad\text{or}\quad
[f_1,f_0,s_1,s_2,s_3]
$$

belongs to $\Omega_a^{\rm reach}$. The union over the two fused-label
orientations makes $M_a(F)$ independent of their temporary naming. Set
$m_a(F)=|M_a(F)|$, so $0\le m_a(F)\le 6$.

For every coordinate set

$$
\{c_1<c_2<c_3\}\subseteq Q\setminus\{0,1\}
$$

and every $(s_1,s_2,s_3)\in M_a(F)$, map $s_i$ to $c_i$. The resulting
survivor injection extends to a formal terminal placement whose cyclic order
is reachable; (P35.2) supplies every one of its holes as an actual phase.
Conversely every actual terminal witness produces exactly one such survivor
order and coordinate set. Therefore

$$
\boxed{
\mathfrak S_a(\lambda_0;F)
\cong
M_a(F)\times\binom{Q\setminus\{0,1\}}{3}.}
\tag{P35.6}
$$

Here $\binom{Q\setminus\{0,1\}}{3}$ denotes the set of three-element subsets
of $Q\setminus\{0,1\}$.

In particular,

$$
\boxed{
|\mathfrak S_a(\lambda_0;F)|
=m_a(F)\binom{n-2}{3}.}
\tag{P35.7}
$$

The pair $F$ is hittable if and only if $m_a(F)>0$. Sending both fused labels
to the collapse image and retaining the survivor injection gives the complete
normalized strict-exit incidence frontier.

Combining (P35.5) with (P35.6) gives the complete invariant statement:

$$
\boxed{
\mathcal P_5(a)=\mathcal P_5(b)
\Longrightarrow
\mathfrak S_a(\lambda_0;F)=\mathfrak S_b(\lambda_0;F)
\quad\text{for every }F.}
\tag{P35.8}
$$

Thus $\mathcal P_5$ is not merely an exact encoding of the 24-state order
relation. For a fixed source cyclic order it is a complete invariant of the
one-lane terminal-incidence frontier.

Complete means that it determines that frontier. No minimality statement is
made, and the converse implication is not claimed.

For orientation-preserving dihedral branches, $m_a(F)=1$ on the five
source-consecutive pairs and vanishes otherwise. For orientation-reversing
branches, the corresponding value is $2$. This recovers the Paper XXXIV
survivor spectra.

## 5. Boundaries

The theorem is one-lane, raw, and unbudgeted. It does not solve multi-lane
same-witness mobility, classify shortest words, construct typed transfer
data, or establish projectability or recursive return.
