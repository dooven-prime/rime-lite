# Paper II computational support

## Current Validation

- `validation/symmetry_and_transport_audit.py`: separates the sector-preserving subgroup
  from the full transport action and audits spectral-layer leakage.
- `validation/primitive_sectors.py`: numerical QH joint-sector construction.
- `validation/transport_graph.py`: direct generator-support graph.
- `validation/supp_nc.py`: registered family-level block noncommutativity localizer, using
  the maximum over all three per-axis QT commutator pairs. Its support
  intersection is not a sufficient direct-edge criterion: the canonical
  census has 15 overlap candidates, 9 Type I labelled edges, and 6 nonedges.
- `validation/ep_algebra.py`: registered EP algebra audit.
- `validation/joint_spectral_geometry.py`: numerical QT/HT commutation and
  registered nine-point joint-spectrum audit.
- `validation/collision_geometry.py`: exact affine collision arithmetic for
  the declared registered coordinates.
- `validation/generator_universality.py`: finite generator-family comparison;
  despite its historical filename, it is not a universality theorem.

The collision, joint-spectrum, and generator-family controls retain their
explicitly finite or conditional computational scope.

`figures/paper2/render.py` reads the frozen registered transport census and
resolves its declared sources through the registered release-byte snapshot.
It performs presentation work only and does not rerun the audit.

## Archive

`archive/` contains calculations whose object definitions depend on the
withdrawn assumption that nontrivial `A`-spectral layers are full
`G`-subrepresentations.

The former top-level Paper II figure atlas is retained here as a historical
renderer. Its commutant, isotypic, and mechanism diagrams are not active
Paper II evidence.
