# Core Rubik Calibration Records

This page records the stable Rubik-facing data used for calibration across the
early RIME papers. It is a compact numerical and structural reference, not a
proof source or a substitute for the owning manuscripts.

The records below have different claim levels. Exact statements must be cited
from the paper that proves them; numerical records must retain their declared
realization and tolerance. CCS v2.1 is optional companion material and is not a
premise, definition source, or claim authority for the independent papers.

For the complete program architecture, use [overview.md](overview.md) and
[PROGRAM_MAP.md](PROGRAM_MAP.md). Publication identities are maintained in the
root [Public Release table](../README.md#public-release).

## Claim Levels

| Status | Meaning |
|--------|---------|
| Theorem | Exact statement proved from declared hypotheses in the owning paper |
| Computational Certificate | Reproducible finite computation tied to declared inputs |
| Computational Observation | Bounded numerical pattern without exact or generic promotion |
| Research Program | Open problem, conjectural bridge, or proposed extension |

Passing numerical residual checks does not turn a computational record into an
exact identity. A label such as *canonical* identifies the declared Rubik
realization; it does not imply universality across generator families.

## 1. Declared Realization

The canonical laboratory is the 228-dimensional Rubik's Cube cubie
representation with the standard inverse-closed family of 18 face turns. The
representation preserves four physical blocks:

| Block | Dimension | Meaning |
|-------|----------:|---------|
| `cp` | 64 | corner permutation |
| `ep` | 144 | edge permutation |
| `co` | 8 | corner orientation |
| `eo` | 12 | edge orientation |

Thus every represented move is block diagonal with respect to

```text
cp + ep + co + eo.
```

This block preservation is an exact property of the declared construction.
It is the structural input behind the blockwise spectral union and the
disjoint-endpoint composition obstruction.

Primary implementation checks:

- `tests/test_representation.py`
- `rime/cubie.py`
- `rime/cubieoperator.py`

## 2. Registered Six-Layer Census

For the standard generator family,

```text
A_18 = (1/18) sum_{s in S} rho(s).
```

The complex128 block computation registers six numerical eigenvalue layers
against

```text
lambda = 1 - k/9,  k in {0, 1, 2, 3, 4, 6}.
```

The per-block census is:

| Block | Dimension | Registered `k` values | Multiplicities by increasing `k` | Status |
|-------|----------:|-----------------------|--------------------------------------|--------|
| `cp` | 64 | `{0,4,6}` | `(8,24,32)` | analytic combinatorial reduction |
| `ep` | 144 | `{0,2,3,4}` | `(12,36,24,72)` | analytic combinatorial reduction |
| `co` | 8 | `{3,4,6}` | `(2,3,3)` | symmetry-guided computation; accidental degeneracy remains computational |
| `eo` | 12 | `{1,2,4}` | `(2,3,7)` | numerical-representation observation |

Combining the four blocks gives:

| Registered layer label | Dimension | Physical-block contribution |
|------------------------|----------:|-----------------------------|
| `V_1` | 20 | `cp(8) + ep(12)` |
| `V_8/9` | 2 | `eo(2)` |
| `V_7/9` | 39 | `ep(36) + eo(3)` |
| `V_2/3` | 26 | `ep(24) + co(2)` |
| `V_5/9` | 106 | `cp(24) + ep(72) + co(3) + eo(7)` |
| `V_1/3` | 35 | `cp(32) + co(3)` |

The dimensions sum to 228. The value `k=5` is absent from every registered
block spectrum. The `cp` and `ep` exclusions have exact combinatorial
reductions; the `co` and `eo` exclusions retain their stated computational
status.

The displayed rational values are registered numerical matches. Paper I does
not prove canonical Rubik rationality from partition integrality: the tested
face partition fails the required integer compression-trace hypothesis.

Primary certificates:

- `experiments/paper1/validation/spectral_ladder.py`
- `experiments/paper1/validation/k_absence.py`
- `experiments/paper1/validation/block_composition.py`
- `experiments/paper1/validation/projector_algebra.py`

## 3. Registered QT/HT Sectors

The declared complex128 QT/HT joint-diagonalization and registration policy
produces nine stable numerical clusters. These are registered sectors, not
unconditionally exact minimal joint eigenspaces.

| Sector | Layer label | Rank | Physical-block support | Direct-graph degree |
|--------|-------------|-----:|------------------------|--------------------:|
| S1 | `V_1` | 20 | `cp + ep` | 0 |
| S2 | `V_8/9` | 2 | `eo` | 2 |
| S3 | `V_7/9` | 39 | `ep + eo` | 2 |
| S4 | `V_2/3` | 26 | `ep + co` | 2 |
| S5 | `V_5/9` | 1 | `eo` | 2 |
| S6 | `V_5/9` | 39 | `ep + eo` | 5 |
| S7 | `V_5/9` | 66 | `cp + ep + co + eo` | 3 |
| S8 | `V_1/3` | 8 | `cp` | 1 |
| S9 | `V_1/3` | 27 | `cp + co` | 3 |

The rank sequence sums to 228. The registered cluster census is stable across
the declared clustering tolerances, but machine-zero commutators and
projector residuals do not prove exact QT/HT commutation or exact rational
joint coordinates.

Primary certificates:

- `experiments/paper2/validation/joint_spectral_geometry.py`
- `experiments/paper2/validation/primitive_sectors.py`
- `experiments/paper2/validation/symmetry_and_transport_audit.py`
- `tests/test_sectors.py`

## 4. Registered Direct Transport

For the declared generator family, Paper II uses the aggregate Frobenius
support magnitude

```text
K_ij = max_{g in S} ||Q_i rho(g) Q_j||_F.
```

The registered graph is symmetric to numerical precision and has ten
undirected edges:

```text
S2--S5  S2--S6  S3--S6  S3--S7  S4--S6
S4--S9  S5--S6  S6--S7  S7--S9  S8--S9
```

Its degree sequence is

```text
(0, 2, 2, 2, 2, 5, 3, 1, 3).
```

S1 is isolated and S6 is the unique degree-five hub. Nine already-certified
edges carry the registered Type I label because their endpoints share
thresholded noncommutative block support. S8--S9 carries the Type II label and
is supported by the numerically commuting `cp` block.

The block-level noncommutative-support test is only a localizer:

```text
15 overlap candidates = 9 Type I labelled edges + 6 nonedges.
```

The six false-positive candidates are

```text
S2--S3  S2--S7  S3--S4  S3--S5  S4--S7  S5--S7.
```

Type I and Type II are post-certification labels, not universal transport
mechanisms or sufficient edge criteria. The computed edge-permutation
averaging algebra is registered as

```text
M_2(C)^4 direct-sum M_1(C)^4.
```

Primary certificates:

- `experiments/paper2/validation/transport_graph.py`
- `experiments/paper2/validation/supp_nc.py`
- `experiments/paper2/validation/ep_algebra.py`
- `experiments/paper2/results/direct_transport.json`

## 5. Graph/Composition Separation

A support-graph path

```text
j -> k -> i
```

records nonzero adjacent projected blocks, possibly witnessed by different
generators. It does not guarantee a nonzero routed product

```text
Q_i rho(g_2) Q_k rho(g_1) Q_j.
```

The canonical audit registers five graph-only triples:

| Endpoints | Intermediate | Endpoint physical support |
|-----------|--------------|---------------------------|
| S2--S4 | S6 | `eo` versus `ep + co` |
| S3--S9 | S7 | `ep + eo` versus `cp + co` |
| S4--S5 | S6 | `ep + co` versus `eo` |
| S4--S8 | S9 | `ep + co` versus `cp` |
| S6--S9 | S7 | `ep + eo` versus `cp + co` |

For every triple, all `18^2` ordered projected products are machine-zero at
the declared tolerance. The exact local theorem is the image--kernel
criterion:

```text
AB = 0  if and only if  im(B) is contained in ker(A).
```

In the canonical five cases, disjoint endpoint physical-block support and
block preservation provide the structural obstruction. These records are not
T7 morphisms and do not compare full words with Lie closure.

Primary certificate:

- `experiments/paper3/validation/composition_obstruction.py`
- `experiments/paper3/results/composition_obstruction.observation.json`
- `tests/test_transport.py`

The observation JSON is a source-addressed review cache. It does not replace
the executable certificate.

## 6. Explicit Non-Invariants

The following historical or stronger statements are not part of the current
core record:

- exact canonical rationality inferred from the tested face partition;
- exact QT/HT joint sectors inferred only from complex128 residuals;
- shared noncommutative block support as a sufficient transport criterion;
- support paths treated as nonzero projected compositions;
- T7 morphisms or a strict word-versus-Lie containment theorem;
- layerwise ambient-commutant pieces treated as `G`-isotypic components;
- the historical `51`, `59`, `3D x 11`, or uncertified commutant-dimension
  values treated as canonical invariants;
- a single untyped `R1/R2/D` ladder or a generic accessibility-completion
  theorem.

The averaging-operator spectral decomposition and the ambient
`G`-representation decomposition remain distinct. Nontrivial spectral layers
fail the full-action invariance audit, so compression into a spectral layer
does not automatically define a `G`-subrepresentation.

## 7. Change Audit

Before changing a Rubik-facing implementation or manuscript statement, check
whether the change affects:

- the four physical blocks and total dimension 228;
- the registered six-layer block census and the `k=5` vacancy;
- the nine registered QT/HT sectors and their ranks;
- the ten direct edges and degree sequence;
- the 15 noncommutative-support overlap candidates;
- the five graph-only composition obstructions;
- the numerical qualification of the orientation blocks and QT/HT sectors;
- any withdrawn exactness, commutant, T7, or untyped-completion claim.

Run the owning paper certificates first. The repository-wide regression entry
points are:

```bash
python tests/run_all_tests.py
python tests/run_slow_tests.py
```

Presentation renderers under `figures/` consume registered results; they are
not independent scientific certificates.
