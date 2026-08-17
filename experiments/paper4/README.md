# Paper IV computational support

Paper IV separates all four reader-facing claim layers. Exact theorems are
proved in the manuscript; the scripts below own only the declared certificate
and observation records. Research-program statements have no supporting
artifact role.

## Exact theorem controls

The rectangular family $P_{\mathrm{rect}}(a,b)$ and its sole interior collision at
$b/(a+b)$ are proved symbolically in Proposition 4.2. They do not consume a
Rubik computation or a numerical result artifact. The diagonal negative
control in Proposition 8.1 is likewise an exact theorem-level counterexample:
collision adjacency alone cannot imply transport adjacency or projected
composition.

## Exact explicit arrangement

```text
python experiments/paper4/validation/rubik_collision_quotient.py
```

This script uses exact `Fraction` arithmetic on the independently declared
weighted rational set `P_9`. It verifies the complete 36-pair certificate,
endpoint and interior quotient
classes, pair multiplicities, layer-count drops, all open-chamber branch
orders on `[0,1]`, and the exact weighted quotient at `alpha=2/3`. It does not
prove that `P_9` is the exact Rubik joint spectrum.

## Numerical Rubik registration

```text
python experiments/paper4/validation/rubik_joint_spectrum_registration.py
```

This script reconstructs the complex128 QT/HT operators and reports
Hermiticity, normality, commutation, `A_18` reconstruction, projector
identities, ranks, joint-eigen residuals, raw-to-`P_9` table discrepancies,
`L_infinity` joint-point separation, and coordinate-matched projector stability
across tolerances. The registration is deterministic: it diagonalizes QT,
diagonalizes HT inside each numerical QT cluster, and globally matches the raw
coordinates to `P_9`. It performs no rational reconstruction. A successful run
writes:

```text
results/rubik_joint_spectrum_registration_v2_1.observation.json
```

Check whether the cached observation matches all declared sources without
repeating the matrix construction:

```text
python experiments/paper4/validation/rubik_joint_spectrum_registration.py --check-result
```

The published v2.0 observation at
`results/rubik_joint_spectrum_registration.observation.json` is immutable.
The producer defaults to the distinct v2.1 candidate path above and never
refreshes the v2.0 bytes.

The registration and its JSON snapshot form Computational Certificate 6.1,
not an exact commutation or exact rational-spectrum proof. In particular, a
passing certificate does not discharge the exact R1--R3 assumption checklist
of Corollary 7.1; a new exact source would be required for that promotion.

## Transport comparison

```text
python experiments/paper4/validation/v59_collision_vs_transport.py
```

This Computational Observation compares the exact collision triangle of the
declared arrangement with the direct-support chain in the registered Rubik
clusters. It makes no graph-to-composition or collision-to-transport
implication. The theorem-level nonimplication is supplied separately by the
diagonal negative control in the manuscript.

## Presentation

`results/figure_data.json` is a source-addressed display record for the exact
finite arrangement. `figures/paper4/render.py` reads that record and renders
the three manuscript figures without rerunning either numerical Rubik audit.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
