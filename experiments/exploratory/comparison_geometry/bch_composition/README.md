# BCH Composition Signature Candidate

**Research status:** exact finite Heisenberg control plus an exploratory
comparison-coordinate candidate.

**Execution status:** runnable with the repository Python environment.

**Paper evidence:** none. Directory placement does not promote this package
into Paper XII or Paper XIII evidence.

This package freezes one BCH implementation for the rational
three-dimensional, class-two Heisenberg Lie algebra:

```text
[X,Y] = Z,  [X,Z] = [Y,Z] = 0.
```

It computes the finite polynomial

```text
BCH(x_1,...,x_m) = sum_i x_i + 1/2 sum_{i<j} [x_i,x_j]
```

with exact `fractions.Fraction` arithmetic. It is not a generic symbolic BCH
engine and does not call a matrix logarithm. The admitted input generators are
`X` and `Y`; `Z=[X,Y]` is a derived Hall-basis coordinate, not a third input
generator.

## Frozen Interface

The implementation is registered as:

```text
rime.bch.heisenberg3.class2.rational.v1
```

Each signature binds:

- the exact carrier-definition digest;
- the implementation source SHA-256;
- a local structured generator registration;
- product order, Hall basis, coefficient domain, and quotient relation;
- truncation order and replay-derived remainder status;
- the exact ordered input sequence and homogeneous coefficients.

Comparison additionally requires a separate structured generator alignment.
The current evaluator admits only a digest-bound identity bijection on the
frozen carrier; it never infers alignment from equal labels. It replays both
signatures before returning a factual match or mismatch. An unsupported
implementation or missing alignment is `INCOMPARABLE`; a malformed or
tampered registered signature or alignment is rejected rather than converted
into a scientific comparison state.

## BCH Status

The coordinate-local state vocabulary is:

```text
EXACT_MATCH
CERTIFIED_MISMATCH
TRUNCATED_MATCH
UNRESOLVED
INCOMPARABLE
NOT_DECLARED
```

These values do not replace Paper XIII's global `comparison_state`. The
exploratory projection is:

| BCH status | Candidate SOFAUDIT projection |
|---|---|
| `EXACT_MATCH` | `ALIGNED` |
| `CERTIFIED_MISMATCH` | `MISMATCH` |
| `TRUNCATED_MATCH` | `ALIGNED` only for a `through_degree` coordinate; full BCH remains `UNRESOLVED` |
| `UNRESOLVED` | `UNRESOLVED` |
| `INCOMPARABLE` | `INCOMPARABLE` |
| `NOT_DECLARED` | `NOT_DECLARED` |

For the exact Heisenberg control,

```text
BCH(X,Y) = X + Y + 1/2 Z
BCH(Y,X) = X + Y - 1/2 Z
```

so the comparison is `CERTIFIED_MISMATCH` with
`lowest_differing_degree = 2`.

## Run

From the repository root:

```bash
python experiments/exploratory/comparison_geometry/bch_composition/bch_signature.py \
  --out experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.json \
  --markdown experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.md
python experiments/exploratory/comparison_geometry/bch_composition/validate_bch_signature.py \
  experiments/exploratory/comparison_geometry/bch_composition/results/heisenberg_order_control.json
python experiments/exploratory/comparison_geometry/bch_composition/hostile_cases.py
```

See [`PROMOTION_NOTE.md`](PROMOTION_NOTE.md) for the intended Paper XII,
Paper XIII, and `sof-runtime` ownership boundaries.

## Known Nonclaims

- This package is not a SOFRS report, SOFAUDIT artifact, Audit Profile, or
  coordinate-semantics registry entry.
- It does not establish BCH convergence for a non-nilpotent Lie algebra.
- It does not establish equality in a free Lie algebra, arbitrary quotient,
  matrix representation, or logarithm chart.
- A bounded `TRUNCATED_MATCH` does not establish full BCH equality.
- The script is not a runtime evaluator closure; that belongs in
  `sof-runtime` after upstream promotion.
