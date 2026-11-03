# Separate Analytic Layer: Future-Event Count

**Status:** the reduction below is now implemented in the separate
[analytic companion](analysis/README.md), with its own exact-byte milestone
and declaration/axiom audit. It is not part of the finite combinatorial
milestone. The finite proof spine remains read-only input to this layer.

## Algebraic entry point

Write `m=n-2>=1` and `B_m=binom(2m,m)`. The adjacent-binomial identity

\[
\binom{2m}{m-1}=\frac{m}{m+1}B_m
\]

converts the already formalized finite count, viewed in the reals, into

\[
Q_{m+2}^{\mathrm{future}}
=\left(5m+3-\frac1{m+1}\right)B_m-(m+2)(m+1)+1.
\]

Use the additive count theorem before casting from `Nat`, rather than
silently commuting real coercion with truncated natural subtraction.

## Central-binomial input

The pinned Mathlib supplies `Real.Wallis.W_eq_factorial_ratio`,
`Real.Wallis.W_pos` and `Real.Wallis.tendsto_W_nhds_pi_div_two` in
`Mathlib.Analysis.Real.Pi.Wallis`. Its factorial formula gives

\[
W_m=\frac{16^m}{B_m^2(2m+1)},\qquad
\frac{\sqrt m\,B_m}{4^m}
=\sqrt{\frac{m}{(2m+1)W_m}}
\longrightarrow\frac1{\sqrt\pi}.
\]

Thus a Wallis-based proof can supply the central-binomial asymptotic
directly; invoking the pinned Stirling theorem is another possible route.
Either route is an analytic input, not a consequence of finite enumeration.

## Final normalization

Put `D_m=5m+3-1/(m+1)`. For `m>=1`, the exact normalization is

\[
\frac{Q_{m+2}^{\mathrm{future}}}{\sqrt{m+2}\,4^{m+2}}
=\frac1{16}\frac{D_m}{m+2}
  \sqrt{\frac{m+2}{m}}\frac{\sqrt m\,B_m}{4^m}
+\frac{1-(m+2)(m+1)}{\sqrt{m+2}\,4^{m+2}}.
\]

The first three variable factors tend to `5`, `1` and `1/sqrt(pi)`;
the last term tends to zero by polynomial-versus-geometric decay. The pinned
library includes `tendsto_pow_const_div_const_pow_of_one_lt` for that decay.
The resulting analytic target is

\[
Q_n^{\mathrm{future}}\sim
\frac5{16\sqrt\pi}\sqrt n\,4^n.
\]

The finite milestone does not depend on these analytic interfaces. Its
dependency record and hashes remain unchanged while this layer is proved.
