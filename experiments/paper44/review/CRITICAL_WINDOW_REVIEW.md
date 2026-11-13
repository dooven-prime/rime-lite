# Paper XLIV Critical-Window Proof Review

Status: local numbered-reader review, 2026-11-12. This record is not a
publication receipt or a Lean proof of the analytic results.

## Reviewed Identity

| File | SHA-256 |
| --- | --- |
| `papers/paper44/Paper XLIV.md` | `ae9e674927ed4d8843dcc2aacbda0bbe86af31f4c4548fd4a9e888a55db0c370` |
| `papers/paper44/references-v1.bib` | `4c580d76c3a56cb0597013d2958e35af94099312217fc7d34f01e9134a63e27c` |
| `papers/paper44/paper44_arxiv.pdf` | `db15d29efcfd4a0c24f5dcc28224f39052aeeadef7de5901f3f6a304e4ed9661` |

The earlier unnumbered C1 review bound manuscript hash
`1dda742bb740cb63655c8adebd7d58c3f182c5ba047c520efd07f5ca347bb080`
and reported the critical ratio as open. That assessment belongs to the
earlier local draft, not to this numbered manuscript. The historical source
and review are unchanged.

## Mathematical Checks

For `N=n-2` and `1<=j<=N`, the exact identity (6.17) follows by splitting
proper-carrier labels into short and saturated parts. The complete-summary
convolution (6.6) supplies `H_<j`; deleting the full-carrier placements
subtracts `n U_short`, and the terminal labels restore `U_short`.
For saturated labels, Pascal's identity and (5.5) give the two upper
binomial terms in `V`; deleting the `r=N` terms gives its two subtractions.
The terminal saturated labels contribute `2^j binom(N,j)`.

For bounded `u`, `j=floor(n/3+u sqrt(n))=N/3+u sqrt(N)+O_A(1)`.
With `x=(N-j)/(2N+1)`, one has
`x=1/3-u/(2 sqrt(N))+O_A(1/N)`. Taylor expansion of binary entropy,
`H'(1/3)=log 2`, and a uniform interior Stirling bound yield
`2^j binom(2N+1,N-j)=O_A((9/2)^N/sqrt(N))`; shifting the binomial index
by one has the same bound. The unweighted short and endpoint sums in
(6.17) are `O(3^N)`; their coefficients are at most `n`. Equations
(6.7)--(6.8) give
`s_n=n(9/2)^N(1+O((8/9)^N))`. Thus the registered ratio differs from
`H_<j/s_n` by `O_A(N^-1/2)`.

Under the exact reweighting (6.7), `H_<j/s_n` is
`Pr(K>N-j | K<=N)` for `K~Bin(2N,1/3)`. The conditioning error is
`O((8/9)^N)`. Its standardized cutoff is
`-3u/2+O_A(N^-1/2)`, including the floor. Berry--Esseen supplies the
uniform `O_A(N^-1/2)` Gaussian estimate. Adding the identical
`1+R_n` contribution to numerator and denominator changes the ratio by
at most `(1+R_n)/s_n=O(N^-1/2 (8/9)^N)`. These steps establish the
paper proof of (6.14)--(6.16); the equation tags occur in order before
the auxiliary identity (6.17).

The citation keys `chenPaper41v1` and `chenPaper43v1` resolve to the
published Zenodo editions with DOIs `10.5281/zenodo.24137725` and
`10.5281/zenodo.24148747`. Paper XLIV is a first numbered edition, not
a migration of a HAL deposit.

## Finite and Formal Boundaries

The six local arithmetic/transition tests pass; the `(6.17)` test covers
every depth `1<=j<=n-2` for `3<=n<=62`. The retained minimization table
covers 20 cases at `n=3..7`. Neither finite check proves the Gaussian
limit. The Lean milestone covers the finite quotient through Theorem 3.3,
not Theorem 6.5. Source/toolchain hashes pass its local read-only check;
this review does not claim a new clean-host Lean replay.
