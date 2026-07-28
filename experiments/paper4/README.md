# Paper IV computational support

Paper IV separates three evidence layers.

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
results/rubik_joint_spectrum_registration.observation.json
```

Check whether the cached observation matches all declared sources without
repeating the matrix construction:

```text
python experiments/paper4/validation/rubik_joint_spectrum_registration.py --check-result
```

The registration and its JSON snapshot are computational evidence, not exact
commutation or exact rational-spectrum proofs.

## Transport comparison

```text
python experiments/paper4/validation/v59_collision_vs_transport.py
```

This numerical check compares the exact collision triangle of the declared
arrangement with the direct-support chain in the registered Rubik clusters.
It makes no graph-to-composition or collision-to-transport implication.

## Presentation

`results/figure_data.json` is a source-addressed display record for the exact
finite arrangement. `figures/paper4/render.py` reads that record and renders
the three manuscript figures without rerunning either numerical Rubik audit.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
