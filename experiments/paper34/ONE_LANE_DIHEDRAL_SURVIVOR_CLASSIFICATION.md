# One-Lane Dihedral Survivor Classification

**Status:** paper-local supporting proof note for Paper XXXIV. This note is not
the release manuscript or a publication identity.

## Setup

Fix $n\ge6$, put $L=n-1$, take $\Delta=1$, and use the one-lane normalized
carrier

$$
 E=\{1,\ldots,n-1\}.
$$

Let $\psi$ be the positive $L$-cycle on $E$, and let

$$
 \operatorname{Aut}(C_L)=\langle\psi,\rho\rangle
$$

be its cycle-graph automorphism group, where $\rho$ is the reflection fixing
$1$:

$$
 \rho(1)=1,
 \qquad
 \rho(q)=n+1-q\quad(2\le q\le n-1).
 \tag{S34.1}
$$

Every $a\in\operatorname{Aut}(C_L)$ has an orientation character

$$
 \chi(a)=
 \begin{cases}
  +1,&a\in\langle\psi\rangle,\\
  -1,&a\in\langle\psi\rangle\rho.
 \end{cases}
 \tag{S34.2}
$$

Fix five source lineage labels $T_0$ with positive cyclic order and a source
injection $\lambda_0:T_0\hookrightarrow E$ preserving that order. For a
branch $a$, let $\mathfrak F_a(\lambda_0)$ be its set of hittable fused source
pairs and let $\mathfrak S_a(\lambda_0;F)$ be its normalized survivor
spectrum. Both objects are defined from complete terminal witnesses, not from
formal terminal placements alone.

For a consecutive source pair $F$, orient the source order as

$$
 (f_0,f_1,r_1,r_2,r_3),
 \qquad
 F=\{f_0,f_1\},
 \tag{S34.3}
$$

and define

$$
 \mathfrak S^+(F)
 =\left\{
 s:R_0\hookrightarrow E\setminus\{1\}:
 2\le s(r_1)<s(r_2)<s(r_3)\le n-1
 \right\},
 \tag{S34.4}
$$

$$
 \mathfrak S^-(F)
 =\left\{
 s:R_0\hookrightarrow E\setminus\{1\}:
 2\le s(r_3)<s(r_2)<s(r_1)\le n-1
 \right\}.
 \tag{S34.5}
$$

## The Classification

**Theorem I1 (one-lane dihedral survivor-spectrum classification).** For
every $a\in\operatorname{Aut}(C_L)$,

$$
 \boxed{
 \mathfrak F_a(\lambda_0)
 =\{\text{the five consecutive pairs in the source cyclic order}\}.}
 \tag{S34.6}
$$

For every such pair $F$,

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)
 =
 \begin{cases}
  \mathfrak S^+(F),&\chi(a)=+1,\\[1mm]
  \mathfrak S^+(F)\mathbin{\sqcup}\mathfrak S^-(F),&\chi(a)=-1.
 \end{cases}}
 \tag{S34.7}
$$

Consequently,

$$
 \boxed{
 |\mathfrak S_a(\lambda_0;F)|
 =
 \begin{cases}
  \binom{n-2}{3},&\chi(a)=+1,\\[1mm]
  2\binom{n-2}{3},&\chi(a)=-1.
 \end{cases}}
 \tag{S34.8}
$$

### Reachable orientation classes

On a guarded five-point support, every identity-branch point map
$\varepsilon_1p^r$ preserves the hole-deleted cyclic order. Hence a branch
step

$$
 \varepsilon_1p^ra
 \tag{S34.9}
$$

preserves lineage orientation when $\chi(a)=+1$ and reverses it when
$\chi(a)=-1$. Starting from $\lambda_0$, the rotation branches therefore
reach only preserving injections, while reflection branches reach only the
union of preserving and reversing injections.

The reverse inclusions use actual guarded paths. The label-zero branch return
is $a_\#$ and is globally enabled. Since $a$ has finite order, one may apply
a positive power of this return to realize $a^{-1}_\#$. Therefore every
identity-branch transition

$$
 x\longmapsto(\varepsilon_1p^r)_\#x
$$

is simulated in the branch-$a$ system by first reaching $a^{-1}_\#x$ through
label-zero returns and then applying the label-$r$ return. The labelled
identity-branch order-fiber theorem thus supplies every preserving injection
for every dihedral branch.

If $\chi(a)=-1$ and $\mu$ is reversing, then $a^{-1}\mu$ is preserving.
Reach $a^{-1}\mu$ by the simulated identity path and apply the globally
enabled label-zero return once. This reaches $\mu$. Hence

$$
 \mathcal L_a(\lambda_0)
 =
 \begin{cases}
  \{\text{preserving injections}\},&\chi(a)=+1,\\
  \{\text{preserving injections}\}\sqcup
  \{\text{reversing injections}\},&\chi(a)=-1.
 \end{cases}
 \tag{S34.10}
$$

### From formal terminal placements to actual witnesses

For a terminal witness $(\lambda,u)$, write

$$
 \mu=p^ua\lambda.
 \tag{S34.11}
$$

This is the injective pre-collapse terminal placement. A rotation branch
produces only preserving $\mu$. A reflection branch produces both
orientations because its reachable fiber already contains both and the final
application of $a$ reverses orientation.

Conversely, let $\mu:T_0\hookrightarrow Q$ be a formal terminal placement of
one of the allowed orientations with

$$
 \mu(F)=\{0,1\}.
 \tag{S34.12}
$$

The carrier has $n\ge6$ points and $\mu$ occupies only five, so it has a
missing coordinate $h$. Choose $u$ so that $p^{-u}\mu$ omits $0$, and put

$$
 \boxed{\lambda=a^{-1}p^{-u}\mu:T_0\hookrightarrow E.}
 \tag{S34.13}
$$

Rotation preserves orientation. If $\chi(a)=+1$, the allowed $\mu$ is
preserving, so $\lambda$ is preserving and belongs to (S34.10). If
$\chi(a)=-1$, equation (S34.10) contains both orientation classes, so the
orientation reversal introduced by $a^{-1}$ also leaves $\lambda$ in the
reachable fiber. In both cases

$$
 p^ua\lambda=\mu.
 \tag{S34.14}
$$

Thus every formal placement used in the classification is supplied by one
actual section injection and the same terminal exponent. No pair witness is
spliced with a survivor witness from another row.

### Reading the survivor spectra

An unordered pair can occupy the adjacent terminal kernel pair $\{0,1\}$ in
a preserving or reversing placement exactly when it is consecutive in the
source cyclic order. This proves (S34.6).

For a preserving terminal placement, the orientation (S34.3) forces

$$
 f_0\mapsto0,
 \qquad
 f_1\mapsto1,
 \qquad
 2\le r_1<r_2<r_3\le n-1.
 \tag{S34.15}
$$

For a reversing terminal placement it forces

$$
 f_1\mapsto0,
 \qquad
 f_0\mapsto1,
 \qquad
 2\le r_3<r_2<r_1\le n-1.
 \tag{S34.16}
$$

The strict collapse sends both fused lineages to $1$ and fixes the three
survivor coordinates. Equations (S34.15)--(S34.16), together with the actual
witness construction above, prove (S34.7). The two families are disjoint
because the survivor coordinates are distinct. Each is indexed by a
three-subset of $\{2,\ldots,n-1\}$, proving (S34.8).

## Orientation Spectrum and Non-Descent

For a hittable fused pair $F$, define the attained terminal-orientation
spectrum

$$
 \operatorname{OriSpec}_a(F)
 =\{\epsilon\in\{+,-\}:
   \text{some terminal witness for $F$ has pre-collapse placement}
   \\[-1mm]
   \text{$\mu=p^ua\lambda$ of orientation $\epsilon$}\}.
 \tag{S34.17}
$$

Theorem I1 gives

$$
 \boxed{
 \operatorname{OriSpec}_a(F)
 =
 \begin{cases}
  \{+\},&\chi(a)=+1,\\
  \{+,-\},&\chi(a)=-1,
 \end{cases}}
 \tag{S34.18}
$$

and, within this family,

$$
 \boxed{
 \mathfrak S_a(\lambda_0;F)
 =
 \bigsqcup_{\epsilon\in\operatorname{OriSpec}_a(F)}
 \mathfrak S^\epsilon(F).}
 \tag{S34.19}
$$

**Corollary I2 (pair-level non-descent).** Let $a_+$ be any rotation and
$a_-$ any reflection in $\operatorname{Aut}(C_L)$. Then

$$
 \mathfrak F_{a_+}(\lambda_0)
 =\mathfrak F_{a_-}(\lambda_0),
 \tag{S34.20}
$$

and Paper XXXII's one-lane classification gives the same complete Safe-Hit
predicate for the two branches, but

$$
 \boxed{
 \mathfrak S_{a_+}(\lambda_0;F)
 \ne
 \mathfrak S_{a_-}(\lambda_0;F)}
 \tag{S34.21}
$$

for every hittable pair $F$. Thus pair-level reachability forgets the attained
terminal orientation class and does not determine survivor incidence.

Equation (S34.19) is an exact factorization inside the one-lane dihedral
family. It does not claim that $\operatorname{OriSpec}$ is a minimal or
sufficient survivor quotient for arbitrary branches.

## Claim Boundary

The theorem is a raw normalized-incidence statement. It does not establish:

- a complete survivor classification for arbitrary branch permutations;
- a survivor quotient for multiple lanes;
- typed transfer membership or endpoint authority;
- projectability, recursive return, settlement, or a reset bound.

The retained finite audit checks the complete dihedral family for
$6\le n\le9$. Those rows validate the implementation of the definitions;
they are not the proof of the all-$n$ theorem.
