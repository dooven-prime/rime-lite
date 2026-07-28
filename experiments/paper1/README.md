# Paper I computational support

The directory separates current submission-facing certificates from secondary
validation and withdrawn first-version interpretations.

## Current Validation

- `validation/spectral_ladder.py`: registered six-layer spectrum and block census.
- `validation/k_absence.py`: registered absence of the `k=5` layer.
- `validation/block_composition.py`: blockwise spectral support.
- `validation/projector_algebra.py`: numerical orthogonality, idempotence, and completeness
  of the spectral projectors.
- `validation/co_eo_analytic_spectrum.py`: qualified CO/EO block audit.
- `validation/symmetry_breaking.py`: finite broken-face field-candidate control.

The last two scripts are finite controls or qualified block reductions; they
do not establish universal theorems.

## Archive

Scripts under `archive/` preserve calculations tied to withdrawn or unresolved
interpretations. In particular, compression of the ambient commutant to an
`A`-spectral layer is not a group-isotypic decomposition unless that layer is
invariant under the declared group action.

The former top-level Paper I figure atlas is retained here as a historical
renderer. Its unused outputs belong to the CCS historical figure collection
and are not evidence for the active manuscript.
