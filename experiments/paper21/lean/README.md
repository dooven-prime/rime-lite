# Paper XXI Lean Formalization

This directory is a self-contained, paper-owned Lake project. It pins Lean and
Mathlib and vendors the two imported finite-field route modules needed by the
paper-facing entry point.

## Pinned Environment

- Lean: `4.33.0`
- Lake: `5.0.0`
- Mathlib revision: `db584cd6d46c92f209a44c0f1c829460d327499d`
- Imported semantic modules:
  - `Formalization/UniformModularZeroRoute.lean`
  - `Formalization/UniformModularZeroRouteField.lean`

Build from the repository root:

```text
cd experiments/paper21/lean
lake build Formalization.UniformModularZeroRouteField
lake env lean FiniteFieldRouteProfiles.lean
```

Routine verification should write its receipt outside the tracked evidence
tree:

```text
python experiments/paper21/validation/validate_lean_formalization.py \
  --receipt build/verification/paper21-lean-receipt.json
```

## Formalized Surface

- complete semantic depth-two zero-route classification over every finite
  field with at least three elements;
- exact equality of the semantic zero-route set with the declared 14-route
  classification and the `14 / 45` count;
- the arbitrary-depth Boolean candidate formula
  `B_d = 3^d * Nat.fib (d + 3)`;
- the eight supported depth-three sector shapes and the count
  `27 * 8 = 216`;
- definitions of `v_a`, the labelled pole, and `e_ab`, with the pole equation;
- all eight depth-three nonzero shape criteria as semantic equivalences;
- the all-finite witness theorem for every finite field of cardinality at
  least four;
- exact finite enumeration of the `F2` and `F3` exceptional regimes;
- the general first-seven-shape characteristic split;
- the complete characteristic-aware depth-three count theorem.

## Evidence Boundary

A successful Lean compilation means that the vendored sources elaborate and
their theorems type-check under the pinned Lean/Mathlib environment. It does
not mean that the Python replay certificate proves these Lean theorems or that
the formal statements exhaust every manuscript claim. The arbitrary-depth
prefix-pole classification, generic profile/determinant spectrum,
fixed-field automaton/rationality theorem, and fixed-depth
exceptional-characteristic stabilization theorem are currently outside this
Lean closure. Sampled higher-depth profiles remain computational certificates
only.
