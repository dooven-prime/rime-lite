# RIME

**Representation-Induced Mechanics and Evolution**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21108197.svg)](https://doi.org/10.5281/zenodo.21108197)
[![Paper IV DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21127271.svg)](https://doi.org/10.5281/zenodo.21127271)
[![Paper V DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21152972.svg)](https://doi.org/10.5281/zenodo.21152972)
[![Paper VI DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21154656.svg)](https://doi.org/10.5281/zenodo.21154656)
[![Paper VII DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21193940.svg)](https://doi.org/10.5281/zenodo.21193940)

RIME studies spectral, transport, accessibility, and deformation structures in
finite-dimensional represented systems. The Rubik cube is used as a concrete
finite representation laboratory, not as a puzzle-solving problem.

## Public Release

The current public release contains Papers I--VII plus the Computational
Canonical Specification (CCS).

| Component | Topic | DOI / source |
|-----------|-------|--------------|
| Papers I--III + CCS | spectral, transport, and accessibility structures in the Rubik representation | [10.5281/zenodo.21108197](https://doi.org/10.5281/zenodo.21108197) |
| Paper IV | collision geometry of joint spectra | [10.5281/zenodo.21127271](https://doi.org/10.5281/zenodo.21127271) |
| Paper V | accessibility repair calculus | [10.5281/zenodo.21152972](https://doi.org/10.5281/zenodo.21152972) |
| Paper VI | generator-set deformation and accessibility walls | [10.5281/zenodo.21154656](https://doi.org/10.5281/zenodo.21154656) |
| Paper VII | generic accessibility completion | [10.5281/zenodo.21193940](https://doi.org/10.5281/zenodo.21193940) |

## Start Here

| If you want to... | Start with |
|-------------------|------------|
| get the program overview | [`docs/overview.md`](docs/overview.md) |
| understand the paper architecture | [`docs/PROGRAM_MAP.md`](docs/PROGRAM_MAP.md) |
| read the trilogy overview | [`docs/TRILOGY_OVERVIEW.md`](docs/TRILOGY_OVERVIEW.md) |
| inspect reproducibility scripts | [`experiments/README.md`](experiments/README.md) |
| check canonical computation notes | [`ccs/canonical_specification.md`](ccs/canonical_specification.md) |

## Papers

| Paper | PDF | Source | Main question |
|-------|-----|--------|---------------|
| I | [`paper1_arxiv.pdf`](papers/paper1/paper1_arxiv.pdf) | [`Paper I.md`](papers/paper1/Paper%20I.md) | Why does the averaging operator have a rational six-layer spectrum? |
| II | [`paper2_arxiv.pdf`](papers/paper2/paper2_arxiv.pdf) | [`Paper II.md`](papers/paper2/Paper%20II.md) | Why does the nine-sector transport graph have its observed sparse structure? |
| III | [`paper3_arxiv.pdf`](papers/paper3/paper3_arxiv.pdf) | [`Paper III.md`](papers/paper3/Paper%20III.md) | Why can discrete composition create channels invisible to Lie-generated accessibility? |
| IV | [`paper4_arxiv.pdf`](papers/paper4/paper4_arxiv.pdf) | [`Paper IV.md`](papers/paper4/Paper%20IV.md) | Why are the six spectral layers a collision quotient of a nine-point joint spectrum? |
| V | [`paper5_arxiv.pdf`](papers/paper5/paper5_arxiv.pdf) | [`Paper V.md`](papers/paper5/Paper%20V.md) | What repairs binary support after path-commutator cancellation? |
| VI | [`paper6_arxiv.pdf`](papers/paper6/paper6_arxiv.pdf) | [`Paper VI.md`](papers/paper6/Paper%20VI.md) | How do spectral phases and accessibility data bifurcate under generator variation? |
| VII | [`paper7_arxiv.pdf`](papers/paper7/paper7_arxiv.pdf) | [`Paper VII.md`](papers/paper7/Paper%20VII.md) | Why is accessibility generically stable? |
| CCS | [`ccs_arxiv.pdf`](ccs/ccs_arxiv.pdf) | [`canonical_specification.md`](ccs/canonical_specification.md) | Which numerical objects, figures, stability checks, and claim dependencies are canonical? |

Program arc:

```text
Arithmetic
  -> Transport
  -> Lie/composition separation
  -> Collision geometry
  -> Accessibility repair
  -> Generator-set deformation
  -> Generic completion
```

## Repository Structure

```text
rime-lite/
|-- rime/                 core representation and spectral computation
|-- experiments/          paper support scripts and diagnostics
|-- tests/                invariant checks
|-- papers/               manuscript sources
|-- ccs/                  Computational Canonical Specification source
|-- docs/                 public overview, program map, and research notes
`-- figures/              frozen generated figures used by papers
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
python experiments/paper1/spectral_ladder.py
python experiments/paper2/primitive_sectors.py
python experiments/paper3/t7_detection.py
python experiments/paper4/rubik_collision_quotient.py
python experiments/paper5/matrix_nondegeneracy.py
python experiments/paper6/tangent_commutator_map.py
python experiments/paper7/rank_protected_bridge_audit.py
```

For the full experiment map, see [`experiments/README.md`](experiments/README.md).

## Scope

This is not a cube-solving repository. It does not implement Kociemba's
algorithm, pruning tables, scramble search, sticker rendering, or neural
solvers. The cube is used as a finite representation-theoretic testbed.

## License

Code: MIT License. See [`LICENSE`](LICENSE).

Papers and manuscript sources: Creative Commons Attribution 4.0 International
(CC BY 4.0). See [`LICENSE-PAPERS`](LICENSE-PAPERS).

## Citation

Please cite the individual paper DOI when referring to a specific result. The
foundational trilogy + CCS archive is:

```text
10.5281/zenodo.21108197
```

Post-trilogy DOI records:

```text
Paper IV   10.5281/zenodo.21127271
Paper V    10.5281/zenodo.21152972
Paper VI   10.5281/zenodo.21154656
Paper VII  10.5281/zenodo.21193940
```
