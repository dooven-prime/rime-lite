# Paper V Experiments

These scripts support the second-edition Paper V object separation:

```text
direct support != projected composition != word support
               != commutator support != full Lie depth
```

| Script | Claim boundary |
|--------|----------------|
| `validation/exact_support_commutator_counterexample.py` | Exact integer-matrix certificate that identical generator-indexed direct support need not determine commutator support or exact Lie depth. |
| `validation/low_order_channel_audit.py` | Numerical S4 census computed first on aggregate-`R1`-zero ordered pairs, with `C_2^X`, `W_2^X`, and `R_2^Lie` audited separately. |
| `validation/s4_r1_r2_depth.py` | Ten-sector projector registration, cutoff-depth census, and augmented Lie-span closure certificate for the declared S4 logarithmic realization. |
| `validation/path_commutator_cancellation.py` | Numerical signed cancellation of two projected product orders in two S4 channels. |
| `validation/complement_explosion.py` | Exact-support scalar model for the centered bracket-emergence proposition. |
| `validation/noncomplement_obstruction_enumeration.py` | Finite support-set enumeration; it does not establish matrix-product survival. |
| `validation/matrix_nondegeneracy.py` | Direct-channel two-step product audit. Its 48 targets already satisfy aggregate `R1=1`, and all 48 are left- and right-rank-protected; it is not an `R1`-zero emergence certificate. |

The serialized value `999` means unreached within the tested cutoff. It must
not be interpreted as exact infinite depth without a separate closure
certificate. The S4 generators use a declared numerical matrix-logarithm
branch and therefore support computational, not exact representation-theoretic,
claims.

The ten S4 sectors come from an explicitly order-dependent Hermitian
compression procedure. The registration operators are not mutually
commuting, so these sectors are not described as joint spectral sectors.

## Presentation

`results/figure_data.json` records the exact same-support example and the
finite S4 low-order census used for display. `figures/paper5/render.py`
verifies the owning validation-script hashes and renders two manuscript
figures. It does not execute the S4 audit or promote its finite census.

Only the `validation/` paths are active; historical releases retain their own
source snapshots.
