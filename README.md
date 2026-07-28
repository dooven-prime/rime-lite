# RIME

**Representation-Induced Mechanics and Evolution**

RIME studies spectral, transport, accessibility, and deformation structures in
finite-dimensional represented systems. The Rubik cube is used as a concrete
finite representation laboratory, not as a puzzle-solving problem.

## Public Release

The current public release contains Papers I--XIII. CCS v2 is published
separately as an optional non-paper Computational Companion Archive; the
immutable first combined record retains its historical predecessor.

| Component | Topic | DOI / source |
|-----------|-------|--------------|
| Paper I | block spectral structure and a conditional rationality criterion | <https://doi.org/10.5281/zenodo.21571403> |
| Paper II | sector non-invariance, direct support, and transport channels | <https://doi.org/10.5281/zenodo.21581072> |
| Paper III | support-graph reachability and matrix-composition obstructions | <https://doi.org/10.5281/zenodo.21583070> |
| Paper IV | collision geometry of joint spectra | <https://doi.org/10.5281/zenodo.21620776> |
| Paper V | Boolean support and commutator accessibility | <https://doi.org/10.5281/zenodo.21634007> |
| Paper VI | linearized commutativity geometry, normality gates, and typed spectral registrations | <https://doi.org/10.5281/zenodo.21634256> |
| Paper VII | incidence geometry, rank protection, and composition-promotion limits | <https://doi.org/10.5281/zenodo.21634538> |
| Paper VIII | sectorized observable framework | <https://doi.org/10.5281/zenodo.21287278> |
| Paper IX | observable dynamics of sectorized observable frameworks | <https://doi.org/10.5281/zenodo.21287695> |
| Paper X | universal observable pipeline and SOF registry evidence | <https://doi.org/10.5281/zenodo.21288036> |
| Paper XI | observable classification theory for SOF wall records | <https://doi.org/10.5281/zenodo.21453674> |
| Paper XII | SOF diagnostic protocol and report specification | <https://doi.org/10.5281/zenodo.21387462> |
| Paper XIII | comparison geometry, SOF Report Alignment, and audit signatures | <https://doi.org/10.5281/zenodo.21449512> |
| CCS v2 | optional reproducibility, observation, open-problem, and history archive | <https://doi.org/10.5281/zenodo.21616956> |
| Historical combined Papers I--III + CCS release | immutable first-version archive; current papers are maintained independently | <https://doi.org/10.5281/zenodo.21108197> |

This is the repository's canonical DOI index. It identifies immutable
published records; other public documents link here instead of duplicating the
list. Repository manuscripts and PDFs may contain an explicitly labeled later
revision candidate. In particular, the current Paper XII repository copy is a
post-v1.0 candidate; its published DOI still identifies v1.0, and the SOFRS
v1.0 contract is unchanged.

## Start Here

| If you want to... | Start with |
|-------------------|------------|
| browse the public documentation | [`docs/README.md`](docs/README.md) |
| get the program overview | [`docs/overview.md`](docs/overview.md) |
| understand the paper architecture | [`docs/PROGRAM_MAP.md`](docs/PROGRAM_MAP.md) |
| understand the Rubik-as-laboratory philosophy | [`docs/PROGRAM_PHILOSOPHY.md`](docs/PROGRAM_PHILOSOPHY.md) |
| check paper boundaries | [`docs/PAPER_SCOPE.md`](docs/PAPER_SCOPE.md) |
| inspect canonical Rubik invariants | [`docs/CORE_INVARIANTS.md`](docs/CORE_INVARIANTS.md) |
| check geometry and move conventions | [`docs/conventions.md`](docs/conventions.md) |
| inspect reproducibility scripts | [`experiments/README.md`](experiments/README.md) |
| inspect published SOF data contracts | [`schemas/README.md`](schemas/README.md) |
| inspect optional reproducibility data, observations, open problems, and history | [`ccs/canonical_specification.md`](ccs/canonical_specification.md) |

## Papers

| Paper | PDF | Source | Main question |
|-------|-----|--------|---------------|
| I | [`paper1_arxiv.pdf`](papers/paper1/paper1_arxiv.pdf) | [`Paper I.md`](papers/paper1/Paper%20I.md) | What is the blockwise canonical spectrum, and which conditional arithmetic criteria apply? |
| II | [`paper2_arxiv.pdf`](papers/paper2/paper2_arxiv.pdf) | [`Paper II.md`](papers/paper2/Paper%20II.md) | Why does the nine-sector transport graph have its observed sparse structure? |
| III | [`paper3_arxiv.pdf`](papers/paper3/paper3_arxiv.pdf) | [`Paper III.md`](papers/paper3/Paper%20III.md) | When does a path in the direct support graph represent a nonzero projected matrix composition? |
| IV | [`paper4_arxiv.pdf`](papers/paper4/paper4_arxiv.pdf) | [`Paper IV.md`](papers/paper4/Paper%20IV.md) | How do fixed affine-branch collisions form quotient layers, and when may a numerical realization inherit that quotient? |
| V | [`paper5_arxiv.pdf`](papers/paper5/paper5_arxiv.pdf) | [`Paper V.md`](papers/paper5/Paper%20V.md) | Why does Boolean support fail to determine commutator accessibility? |
| VI | [`paper6_arxiv.pdf`](papers/paper6/paper6_arxiv.pdf) | [`Paper VI.md`](papers/paper6/Paper%20VI.md) | Which linearized directions preserve the constraints, and which samples pass the spectral gates? |
| VII | [`paper7_arxiv.pdf`](papers/paper7/paper7_arxiv.pdf) | [`Paper VII.md`](papers/paper7/Paper%20VII.md) | When do nonzero projected factors compose, and what limits stronger promotions? |
| VIII | [`paper8_arxiv.pdf`](papers/paper8/paper8_arxiv.pdf) | [`Paper VIII.md`](papers/paper8/Paper%20VIII.md) | What is the sectorized observable object? |
| IX | [`paper9_arxiv.pdf`](papers/paper9/paper9_arxiv.pdf) | [`Paper IX.md`](papers/paper9/Paper%20IX.md) | How do SOF observables evolve under deformation? |
| X | [`paper10_arxiv.pdf`](papers/paper10/paper10_arxiv.pdf) | [`Paper X.md`](papers/paper10/Paper%20X.md) | Why do different species share one observable pipeline? |
| XI | [`paper11_arxiv.pdf`](papers/paper11/paper11_arxiv.pdf) | [`Paper XI.md`](papers/paper11/Paper%20XI.md) | Which SOF wall records can be classified, and by what kind of local or global theory? |
| XII | [`paper12_arxiv.pdf`](papers/paper12/paper12_arxiv.pdf) | [`Paper XII.md`](papers/paper12/Paper%20XII.md) | How does SOF produce reusable SOF Reports? |
| XIII | [`paper13_arxiv.pdf`](papers/paper13/paper13_arxiv.pdf) | [`Paper XIII.md`](papers/paper13/Paper%20XIII.md) | How can two SOF Reports be aligned and compared without conflating difference with defect? |
| CCS v2 Archive | [`ccs_arxiv.pdf`](ccs/ccs_arxiv.pdf) | [`canonical_specification.md`](ccs/canonical_specification.md) | Optional Paper I--III reproducibility pointers, computational observations, open problems, and historical records |

Thematic index, not a paper dependency order:

```text
Arithmetic
Transport
Support-graph/matrix-composition separation
Collision geometry
Local support and commutator separation
Linearized commutativity and normality-gated registration
Incidence geometry and promotion limits
SOF object theory
Observable dynamics
Universal observable pipeline
Observable wall classification
SOF diagnostic reporting
SOF Report Alignment and comparison geometry
```

Papers I--VII are independently readable. Their neighboring results connect
through typed inputs and outputs; every receiving paper restates its objects,
hypotheses, and missing promotion conditions.

## Repository Structure

```text
rime-lite/
|-- rime/                 core representation and spectral computation
|-- experiments/          paper support scripts and diagnostics
|-- tests/                invariant checks
|-- papers/               manuscript sources
|-- ccs/                  Computational Companion and Status Archive source
|-- docs/                 public overview, program map, and companion notes
|-- schemas/              published SOFRS, SOFAudit, and Registry contracts
|-- registry/             frozen Paper X SOF Registry release snapshots
`-- figures/              manuscript figures and presentation-only renderers
```

## Reproducibility

Install the package in editable mode:

```bash
pip install -e .
```

Run fast invariant checks:

```bash
python tests/run_all_tests.py
```

Representative support scripts:

```bash
python experiments/paper1/validation/spectral_ladder.py
python experiments/paper2/validation/primitive_sectors.py
python experiments/paper3/validation/composition_obstruction.py
python experiments/paper4/validation/rubik_collision_quotient.py
python experiments/paper5/validation/matrix_nondegeneracy.py
python experiments/paper6/validation/tangent_commutator_map.py
python experiments/paper7/validation/rank_protected_bridge_audit.py
python experiments/paper9/rate_hierarchy.py
python experiments/paper10/registry_evidence.py
python experiments/paper11/validation/wall_record_census_v2.py
python experiments/paper12/validate_protocol_admission.py
python experiments/paper13/validate_sofaudit.py
```

For the full experiment map, see [`experiments/README.md`](experiments/README.md).

## Scope

This is not a cube-solving repository. It does not implement Kociemba's
algorithm, pruning tables, scramble search, sticker rendering, or neural
solvers. The cube is used as a finite representation-theoretic testbed.

## Acknowledgements

Repository maintenance and editorial workflows have used ChatGPT/Codex,
Claude, and Gemini/Continue for bounded assistance with code, document
restructuring, language suggestions, and consistency review. These tools are
not authors or authorities on mathematical claims. All mathematical judgments,
accepted edits, verification choices, releases, and scholarly responsibility
remain with WuJun Chen.

## License

Code: MIT License. See [`LICENSE`](LICENSE).

Papers and manuscript sources: Creative Commons Attribution 4.0 International
(CC BY 4.0). See [`LICENSE-PAPERS`](LICENSE-PAPERS).

## Citation

Please cite the individual paper DOI when referring to a specific result. Use
the [canonical DOI index](#public-release) above to select the immutable record.
Cite CCS v2 only for archive-specific material, and cite the historical
combined record only when referring to that immutable first-version package.
