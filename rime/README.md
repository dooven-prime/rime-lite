# RIME Python API

The package exposes a deliberately small public surface. Numerical routines
compute declared finite objects; they do not promote computational output to a
theorem.

## Stable General API

The names exported by `rime.__all__` are the supported general interface:

- input validation for sector basis matrices and observable families;
- typed direct support `R1`, commutator support `R2`, routed support `C_d`,
  full-word support `W_d`, and their separate cutoff depths;
- typed combined Lie audits through `compute_lie_accessibility_audit`;
- Lie filtration and numerical closure certificates;
- image--kernel incidence diagnostics and rectangular rank protection.
- finite-dimensional unital `*`-algebra closure certificates whose
  semisimplicity basis is the standard theorem, not a Gram determinant.

`UNREACHED_DEPTH = 999` means unreached within the declared cutoff. It never
means exact infinite depth without a separate saturated closure certificate.

## Module-Scoped APIs

- `rime.cube`, `rime.cubie`, and `rime.cubieoperator` are Rubik-specific.
- `rime.spectralstructure` is a Rubik block-reduction and numerical
  registration helper. It is not a general spectral-field predictor.
- `rime.spectral_utils` contains registration and historical compatibility
  helpers in addition to current graph/composition utilities. Joint spectral
  registration and order-dependent Hermitian compression are separate APIs.

## Deprecated Compatibility

Deprecated functions emit `DeprecationWarning`. Important migrations are:

- `FROZEN_DEPTH` -> `UNREACHED_DEPTH`;
- `matrix_nondeg_audit` -> `rank_protection_audit`;
- `accessibility_signature` -> `compute_lie_accessibility_audit`;
- `SpectralStructure.predict_*` -> `registered_*` or
  `structural_spectral_field_status`;
- `verify_galois_stability` -> `register_spectral_field`;
- `verify_partition_integrality` -> `audit_partition_integrality`;
- `build_center_operators` -> `build_sector_registration_operators`;
- `symmetrized_generator_center_ops` ->
  `symmetrized_generator_hermitian_ops`;
- T7 and mixed kappa helpers -> typed graph, routed-product, word, and Lie
  audits with an explicitly declared operator family.

The circular `diophantine_feasibility` facade, the unsupported
arbitrary-family `predict_q3_krawtchouk` facade, and three unused untyped
kappa/transport helpers were removed. None had an active caller.
