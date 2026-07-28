# Paper VI Archive

These scripts are historical exploratory support, not active Paper VI theorem
entry points.

Active implementations live under `../validation/`:

- `../validation/tangent_commutator_map.py`
- `../validation/normal_spectral_chart_audit.py`
- `../validation/generator_moduli_space.py`

The shared helper remains at `../phase_utils.py`. Current generated records
belong under `../results/`; repository-level `data/` is internal and is not a
public Paper VI artifact location.

Archived here:

- `bifurcation_analysis.py` - superseded by `generator_moduli_space.py`, which
  now writes `../results/_paper6_bifurcation_log.txt`.
- `commutativity_wall_geometry.py` - superseded by `tangent_commutator_map.py`
  and retained as earlier local-scan evidence.
- `deformation_wall_crossing.py` - verbose first-version Type III/IV
  demonstrations. Those labels are static mechanism provenance, not Paper VI
  wall categories.
- `fragmentation_walls.py` - first-version commuting but generally nonnormal
  SVD paths. Its `9 -> 24...35` sectors and raw-operator `R1` counts are not
  valid v2 normal spectral-chart evidence.
- `wall_crossing_summary.py` - first-version untyped `R1/R2/D` summary. It
  mixes accessibility objects and is not a current theorem-support table.

Moved out:

- `search_type4_*.py` moved to `experiments/paper7/archive/`, because those
  scripts explore whether Type IV incidence appears in represented systems,
  which is now part of the Paper VII completion/incidence boundary line.
