# Paper XXVI Lean v1

This supplementary artifact formalizes the elementary TA-III reset-word
waiting envelope.

The Lean development proves:

- monotonicity of the border waiting sum under inclusion of border lengths;
- the closed geometric value
  `sum_{j=1}^r k^j = (k^(r+1) - k) / (k - 1)` for `k >= 2`;
- the conditional TA-III chain
  `worstPairMean <= globalMean <= (k^(r+1)-k)/(k-1)`;
- arithmetic sharpness via the complete border set.

The exact pattern-waiting identity and the coupling from one reset word to
pairwise/global synchronization are represented by explicit certificate fields.
This v1 does not formalize probability spaces, transfer operators, Perron
asymptotics, or the rare-run automaton construction.

Build from this directory with:

```text
lake build Formalization
lake env lean Formalization.lean
```

The project pins Lean 4.33.0 and Mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`.

## Entry point and target

`Formalization.lean` is the technical entry point and imports
`Formalization/TAIII.lean`.  The Lake library and default build target are
both named `Formalization`; `Paper XXVI` remains the manuscript identity and
is not used as a Lean library name.

## Lean declaration ↔ manuscript theorem surface

| Lean declaration | Role in the manuscript |
| --- | --- |
| `borderSum`, `envelope` | Border waiting sum and universal envelope in Section 6 |
| `border_sum_le_envelope` | Monotonicity of the border sum (Theorem 6.1) |
| `envelope_mul_sub`, `envelope_eq_closed` | Finite geometric-series identity used in Theorem 6.1 |
| `BorderWaitingCertificate`, `certificate_envelope`, `certificate_closed_bound` | Certificate form of the reset-word waiting bound |
| `TAIIIData`, `taIII_global_bound`, `taIII_pair_bound`, `taIII_chain` | Conditional comparison chain in Theorem 6.1 |
| `fullBorderCertificate`, `full_border_attains_envelope` | Complete-border equality witness |
| `taIII_arithmetic_sharp`, `taIII_arithmetic_sharp_closed` | Arithmetic sharpness supporting Proposition 6.2 |

The certificate fields intentionally abstract the pattern-waiting identity and
the common-stream coupling.  Those probabilistic constructions are stated in
the paper but are outside this v1 Lean closure.  In particular, the
autocorrelation/equality characterization in Proposition 6.3 and the TA-I and
TA-II spectral results are not claimed as Lean theorems here.
