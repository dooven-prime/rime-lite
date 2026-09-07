# Paper XXVI Public Evidence Companion

This directory contains the paper-owned computational companion for
*Pair-Chain Transfer Operators and Random Synchronization*.

## Current Boundary

- The exact pair-chain construction, Černý Perron asymptotic, rare-run
  realization, and reset-word waiting envelope form the new theorem surface.
- The uniform-input Černý mean is a pair-transfer recovery of Gusev's 2014
  Bernoulli-input result, not a new formula.
- Theorem A.1 proves the second-order analytic refinement, with
  `gamma_1=0`, `gamma_2=pi^2/24-3/4`, explicit constants `N3=64`, `c0=4`,
  and remainder bound `|R3| <= 16*n^3*epsilon^3`. The expanded constant
  verification in `u3-proof.md` is supplementary and is not
  a premise of the proof.
- `pair_chain.py` is the standalone finite implementation; the family producer
  writes the two paper-owned JSON reproductions under `results/`.
- Each JSON result distinguishes exact integer/formula fields from bounded
  float64 spectral observations. The declared replay tolerance is `1e-9`.
- The Lean package is a partial formalization of TA-III finite-sum arithmetic
  and its conditional certificate chain. It does not formalize probability
  spaces, pair chains, or TA-I/TA-II spectral claims.
- This paper does not imply Forced-FFS, General FFS, or a deterministic Cerny
  proof.

Run the public-package validator from the repository root:

```text
python experiments/paper26/generate_family_results.py
python experiments/paper26/validation/validate_lean_formalization.py --replay
python experiments/paper26/validation/validate_public_package.py
```

The validators consume explicit paper-owned inventories. They perform local
closure verification and numerical replay; they do not establish independent
mathematical validation or replace the manuscript proofs.
