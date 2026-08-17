# Theorem Layer

This file states the reusable theorem layer behind the finite census.  It is
deliberately independent of the Rubik numerical realization.

These local propositions are exploratory theorem candidates derived from
finite-dimensional linear algebra. Directory placement does not amend Paper
VII or promote them into the published SOF contract. Paper VII v2.1 separately
restates and owns only its selected fixed-frame carrier and covariance results;
the n=8, cross-frame, and refinement layer remains package-local. Rubik
hypotheses are discharged only by the separate finite certificates named
below.

## Theorem 1: Carrier-Forced Routed Incidence

Let `H = direct_sum_b H_b` with carrier projectors `C_b`. Let `P_i` be sector
projectors satisfying `[P_i, C_b] = 0` for every `i,b`, and let the operative
matrices preserve the same carrier decomposition:

```text
[X,C_b] = [Y,C_b] = 0 for every b.
```

For

```text
A = P_i X P_k,   B = P_k Y P_j,
```

define carrier supports

```text
S(A) = { b : C_b A C_b != 0 },
S(B) = { b : C_b B C_b != 0 }.
```

If `S(A) intersect S(B) = empty`, then `A B = 0`.

**Proof.** Since `P_i`, `P_k`, `P_j`, `X`, and `Y` commute with every `C_b`,
both `A` and `B` are block diagonal in the carrier decomposition. Therefore

```text
A B = sum_b (C_b A C_b)(C_b B C_b).
```

Every summand vanishes because one factor is zero by disjointness. `QED`.

This theorem is an exact promotion rule. A floating-point profile may invoke
it only after separately certifying exact sector-projector reduction, exact
operative-matrix reduction, and exact carrier support masks. Sector-projector
reduction alone is insufficient: off-diagonal carrier blocks of `X` or `Y`
can make `AB` nonzero even when the displayed diagonal carrier supports are
disjoint.

## Theorem 2: Within-Carrier Image--Kernel Criterion

Under the same sector-projector and operative-matrix carrier-reduction
hypotheses, if the carrier supports overlap, then

```text
A B = 0
iff
for every b, im(C_b B C_b) subset ker(C_b A C_b).
```

**Proof.** Use the direct-sum identity in Theorem 1 and apply the ordinary
image--kernel criterion to each carrier block. `QED`.

This is the exact distinction between a physical-carrier-forced zero and a
within-carrier image--kernel alignment. It does not assert that numerical SVD
residuals establish the hypotheses.

## Theorem 3: Projector-Overlap Alignment

For orthogonal decompositions `{P_i}` and `{R_j}` of the same finite Hilbert
space, define

```text
M_ij = tr(P_i R_j) = ||V_i^* W_j||_F^2.
```

Then every row sum is `tr(P_i)` and every column sum is `tr(R_j)`. If both
decompositions are exact, `M` is a basis-invariant table of all pairwise
overlap masses and their marginals; sector indices do not have cross-frame
meaning without an explicit alignment such as `M`. The overlap table is not
claimed to be a complete invariant or classifier of pairs of decompositions.

**Proof.** Write `P_i = V_i V_i^*` and `R_j = W_j W_j^*`. Cyclicity of trace
gives `tr(P_i R_j) = tr(V_i^* W_j W_j^* V_i)`, which is the displayed squared
Frobenius norm. Summing over `j` and using `sum_j R_j = I` gives the row law;
the column law is symmetric. Conjugating both decompositions by a common
unitary leaves every trace unchanged. `QED`.

## Theorem 4: Rotation-Conjugacy Invariance

Let `U` be a representation-space unitary implementing an orientation-preserving
cube rotation and let `F' = U F U^{-1}`. Transport the sector projectors by
`P'_i = U P_i U^{-1}`. Then every routed product is conjugated:

```text
P'_i X' P'_k P'_k Y' P'_j = U (P_i X P_k P_k Y P_j) U^{-1}.
```

Consequently Frobenius norms, ranks, protection classes, and their count
profiles are invariant. Carrier-mechanism classes are also invariant provided
the rotation transports the registered carrier projectors by
`U C_b U^{-1} = C_{pi(b)}` for an explicitly declared permutation `pi`. The
exact combinatorial certificate in `results/exact_certificates/` proves the
family orbit relation; representation equivariance and carrier transport are
separate hypotheses that must be discharged by the representation
implementation.

**Proof.** Substitute `P'_i = U P_i U^{-1}`, `X' = U X U^{-1}`, and the
corresponding formulas for the other factors. Adjacent `U^{-1}U` terms cancel,
leaving the displayed conjugate. Unitary conjugation preserves Frobenius norm
and rank, hence also rank-defined protection classes. Under the additional
carrier-transport hypothesis, it permutes the carrier-local factors and their
mechanism labels. `QED`.

## Theorem 5: Refinement Aggregation and Its Converse Boundary

Suppose `{R_{i,alpha}}_alpha` is an orthogonal refinement of every coarse
sector `P_i`, so `P_i = sum_alpha R_{i,alpha}`. Then for any `X,Y`,

```text
P_i X P_k Y P_j
  = sum_{alpha,beta,gamma}
      R_{i,alpha} X R_{k,beta} Y R_{j,gamma}.
```

Therefore, if every refined routed product on the right vanishes, the coarse
routed product vanishes. Conversely, a zero coarse product implies only that
the displayed sum is zero. It does not imply that each refined route is zero,
because cancellation across `beta` or across endpoint components is possible.

**Proof.** Insert the three finite resolutions of the identity inside the
coarse sectors and distribute. The forward implication is immediate. A pair of
nonzero opposite summands gives a counterexample to the converse. `QED`.

This theorem separates a genuine sector refinement from two merely overlapping
frames. The JSON alignment computes containment residuals and labels the frame
relation. An `overlapping_non_refinement_frames` result is outside the theorem's
hypotheses and must not be described as refinement monotonicity.

## Promotion Boundary

For a Rubik JSON profile, the following are diagnostics, not exact proofs:

- `physical_carrier_commutator_residuals` near machine zero;
- SVD ranks and support masks;
- products below the numerical threshold.

An unconditional exact `AB=0` record requires exact projectors (for example
from a verified algebraic matrix model), exact carrier preservation by the
operative matrices, and exact carrier support masks. The
Lagrange records generated by `make_exact_certificates.py` verify the polynomial
interpolation identities over `Q(sqrt(5))`, while explicitly retaining the
exact-spectrum and diagonalizability assumptions needed to identify those
polynomials with the Rubik projectors.

For the `axes02_qt` family, `exact_n8_spectrum.py` discharges these assumptions
directly over `Z[zeta_3]`: it verifies the annihilating polynomial entrywise and
computes positive integer traces of all seven Lagrange idempotents. Thus its
endogenous seven-sector spectral projectors are exact algebraic projectors;
route-level exact zero verification remains a separate certificate obligation.

`exact_canonical_carriers.py` discharges that obligation for the fixed canonical
frame. It constructs all nine joint QT/HT projectors exactly over
`Q(zeta_3)`, verifies their orthogonality, completeness, carrier masks, and
idempotence, verifies carrier preservation by the registered Rubik generators,
and proves the four canonical zero triples by disjoint endpoint carriers. The
resulting certificate proves the exact-zero status of every numerically
registered carrier-forced route in the 19 fixed-frame orbit profiles. It does
not prove exact nonvanishing of all remaining numerical routes and therefore
does not by itself promote the observed `2/9` rate to an exact algebraic rate.

The v2 certificate records a conservative bound before every fixed-width
identity, addition, subtraction, scale, adjoint, matrix multiplication, and
trace operation. It uses Python integers for trace accumulation. Exactness is
therefore conditional on a complete passing arithmetic audit, not on silent
`int64` execution.
