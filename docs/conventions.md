# Geometric and Move Conventions

This document is the public reference for coordinate systems, face mappings,
cubie orderings, generator encodings, rotation conventions, move encodings, and
parser invariants used by the RIME codebase and the Rubik-facing papers.

Scope note: this is a geometry/API convention document, not a paper-claim
document. It mainly supports the canonical Rubik computation behind Papers
I--III and CCS, and remains relevant for later papers whenever they refer back
to the canonical Rubik representation. For paper boundaries, use
`docs/PAPER_SCOPE.md`; for the full program map, use `docs/PROGRAM_MAP.md`.

Design principle from `CubeGeometry`: the only hardcoded element is
`_AXIS_FACE_MAP`. Corner positions, edge positions, rotation strips, and face
normals are derived from coordinate rules:

```text
corners = vectors with exactly 3 non-zero coordinates in {+/-1}^3
edges   = vectors with exactly 2 non-zero coordinates in {+/-1, 0}^3
```

Canonical ordering is derived from XZ-plane ordering cycles.

---

## 1. Coordinate System

Right-handed Cartesian coordinate system:

```text
+X -> R    axis 0
+Y -> U    axis 1
+Z -> F    axis 2
```

Axis vectors:

```python
AXIS_VEC = np.eye(3)
```

Thus axis `0 = X = [1,0,0]`, axis `1 = Y = [0,1,0]`, and axis
`2 = Z = [0,0,1]`.

---

## 2. Face Ordering

The only hardcoded element:

```python
_AXIS_FACE_MAP = {
    (0, 0): "R", (0, 1): "L",
    (1, 0): "U", (1, 1): "D",
    (2, 0): "F", (2, 1): "B",
}
```

- `axis in {0, 1, 2}`
- `side in {0, 1}`, where `0` is the positive face and `1` is the negative face

Derived `AXIS_FACE`:

```python
AXIS_FACE = [
    ("R", "L"),  # X axis
    ("U", "D"),  # Y axis
    ("F", "B"),  # Z axis
]
```

Canonical face list:

```python
FACES = ["U", "D", "F", "B", "L", "R"]
```

Rotation strips, in counterclockwise order around each axis when viewed from
the positive axis:

```python
AXIS_STRIP = (
    ["U", "F", "D", "B"],  # X
    ["F", "R", "B", "L"],  # Y
    ["U", "L", "D", "R"],  # Z
)
```

---

## 3. Cubie Ordering

### 3.1 Corner Ordering

The 8 corners each have exactly 3 non-zero coordinates in `{+/-1}^3`.
Ordering is U-layer clockwise, then D-layer clockwise, derived from the
XZ-plane cycle `[(+1,+1), (-1,+1), (-1,-1), (+1,-1)]`.

```python
CORNER_POS_SIGNS = [
    (+1, +1, +1),  # 0: URF
    (-1, +1, +1),  # 1: UFL
    (-1, +1, -1),  # 2: ULB
    (+1, +1, -1),  # 3: UBR
    (+1, -1, +1),  # 4: DFR
    (-1, -1, +1),  # 5: DLF
    (-1, -1, -1),  # 6: DBL
    (+1, -1, -1),  # 7: DRB
]
```

Derived partitions:

```python
U_CORNER_POSITIONS = (0, 1, 2, 3)
D_CORNER_POSITIONS = (4, 5, 6, 7)
```

### 3.2 Edge Ordering

The 12 edges each have exactly 2 non-zero coordinates in `{+/-1,0}^3`.
Ordering is U-layer axis, middle diagonal, then D-layer axis.

```python
EDGE_POS_SIGNS = [
    (+1, +1, 0),  # 0:  UR
    (0, +1, +1),  # 1:  UF
    (-1, +1, 0),  # 2:  UL
    (0, +1, -1),  # 3:  UB
    (+1, 0, +1),  # 4:  RF
    (-1, 0, +1),  # 5:  LF
    (-1, 0, -1),  # 6:  LB
    (+1, 0, -1),  # 7:  RB
    (+1, -1, 0),  # 8:  DR
    (0, -1, +1),  # 9:  DF
    (-1, -1, 0),  # 10: DL
    (0, -1, -1),  # 11: DB
]
```

---

## 4. Generator Ordering

The 18 face-turn generators are the outer-layer moves of the 3x3x3 cube:

```text
axis 0 (X):  R  R' R2  L  L' L2
axis 1 (Y):  U  U' U2  D  D' D2
axis 2 (Z):  F  F' F2  B  B' B2
```

Canonical generator list, as used by `CubieMove.prim_moves`:

```text
(0, +1, +1)  (0, +1, -1)  (0, +1, 2)   -> R, R', R2
(0, -1, +1)  (0, -1, -1)  (0, -1, 2)   -> L, L', L2
(1, +1, +1)  (1, +1, -1)  (1, +1, 2)   -> U, U', U2
(1, -1, +1)  (1, -1, -1)  (1, -1, 2)   -> D, D', D2
(2, +1, +1)  (2, +1, -1)  (2, +1, 2)   -> F, F', F2
(2, -1, +1)  (2, -1, -1)  (2, -1, 2)   -> B, B', B2
```

Full generator sets:

```text
QT_all = 12 quarter-turn moves
HT_all = 6 half-turn moves
A_18   = (12 QT_all + 6 HT_all) / 18
```

---

## 5. Rotation Convention

`direction = +1` means clockwise when viewed from outside the cube along the
positive face normal.

- `direction = +1`: clockwise, standard face turn with no prime (`R`, `U`, `F`)
- `direction = -1`: counterclockwise, prime move (`R'`, `U'`, `F'`)
- `direction = 2`: 180-degree half-turn (`R2`, `U2`, `F2`)

This follows the standard Rubik convention: look at the face from outside; a
clockwise twist is `+1`.

---

## 6. Move Encoding

Two encodings coexist in the codebase.

### 6.1 Cubie-Level Encoding

Direct `CubieMove` keys, used in `prim_moves`, spectral operators, and
group-theoretic code:

```text
(axis, side, direction)
```

- `axis in {0, 1, 2}`
- `side in {+1, -1}`
- `direction in {+1, -1, 2}`

### 6.2 Sticker-Level `ActionToken`

`ActionToken` decouples layer from geometry:

```python
@dataclass(frozen=True)
class ActionToken:
    axis: int       # 0, 1, 2
    layer: int      # layer = side * mid; for N=3, +/-1 for outer layers
    direction: int  # +1, -1, 2
```

Conversion between the two:

```python
ActionToken.from_cubie_move(axis, side, direction, n)
token.to_cubie_move(n)
```

For `N=3`, `layer = side * 1`, so `layer=+1` means `side=+1`,
`layer=-1` means `side=-1`, and `layer=0` means a center slice.

### 6.3 Compatibility Table

| Internal | Standard | Internal | Standard |
|----------|----------|----------|----------|
| `(0, +1, +1)` | R | `(0, -1, +1)` | L |
| `(0, +1, -1)` | R' | `(0, -1, -1)` | L' |
| `(0, +1,  2)` | R2 | `(0, -1,  2)` | L2 |
| `(1, +1, +1)` | U | `(1, -1, +1)` | D |
| `(1, +1, -1)` | U' | `(1, -1, -1)` | D' |
| `(1, +1,  2)` | U2 | `(1, -1,  2)` | D2 |
| `(2, +1, +1)` | F | `(2, -1, +1)` | B |
| `(2, +1, -1)` | F' | `(2, -1, -1)` | B' |
| `(2, +1,  2)` | F2 | `(2, -1,  2)` | B2 |

---

## 7. Parser Invariants

### 7.1 Roundtrip

For any valid move string `s`, parsing and stringification recover the original:

```text
ActionToken.transform(s).__str__() == s
```

Examples:

```text
ActionToken.transform("U")   -> axis=1, layer=+1, dir=+1 -> "U"
ActionToken.transform("U'")  -> axis=1, layer=+1, dir=-1 -> "U'"
ActionToken.transform("U2")  -> axis=1, layer=+1, dir=2  -> "U2"
```

### 7.2 Parser Grammar

Supported input syntax:

| Input | Meaning |
|-------|---------|
| `U`, `U'`, `U2` | standard face turns |
| `Rw`, `Rw'`, `Rw2` | wide turns with default width 2 |
| `2Rw`, `3Uw'`, `2Rw2` | explicit width prefix |
| `M`, `M'`, `M2`, `E`, `S` | slice moves |

Parsing rules:

1. Trailing `2` means `direction = 2`.
2. Trailing `'` means `direction = -1`.
3. `M`, `E`, and `S` map to axes `0`, `1`, and `2` with `layer = 0`.
4. Otherwise, parse `(\d*)([URFDLB])(w?)` as width, face, and wide flag.
5. Width with `w` means wide turn; width with digit only means that many
   layers from outside.

---

## 8. Action Direction, Composition, and Representation

The codebase has two parallel action conventions serving different purposes.
They are interconvertible via `convert()`.

### 8.1 Right Action: `CubieMove.act`

```python
move.act(s)  # state' = state * move
```

This is the state-transition convention used by search-compatible and
transition-test code.

Effect on state:

```text
cp[i] = s.corners_perm[self.corners_perm[i]]
co[i] = (s.corners_ori[self.corners_perm[i]] + self.corners_ori_delta[i]) % 3
```

Successive application:

```text
act(act(act(s, m1), m2), m3) = s * m1 * m2 * m3
```

### 8.2 Left Action: `CubieMove.act_left`

```python
move.act_left(s)  # state' = move * state
```

This is the geometry/sticker construction convention.

Semidirect product law, in ASCII notation:

```text
(sigma, delta) * (pi, o) = (sigma*pi, o*sigma^{-1} + delta*sigma^{-1})
```

Effect on state:

```text
cp = sigma[s.corners_perm]
co[i] = (s.corners_ori[sigma^{-1}(i)] + delta[sigma^{-1}(i)]) % 3
```

### 8.3 Interconversion

```python
move.convert()
```

The orientation delta flips sign modulo the orientation order; the permutation
is unchanged.

### 8.4 Composition: `compose` and `@`

Right-action composition. `self @ other` means do `self`, then `other`:

```text
(self @ other).act(s) == other.act(self.act(s))
```

### 8.5 Representation `rho(g)`

```python
move.rho()  # rho(g) in GL(228, C), block_diag(Cp, Ep, Co, Eo)
```

`rho` is a left-action matrix:

```text
rho(g) rho(h) = rho(gh)
rho(g^{-1}) = rho(g)^H
rho(g) rho(g)^H = I
```

Vectors are row vectors, so application is right multiplication:

```text
v' = v @ rho(g)
```

Consequence:

```text
v @ rho(g) @ rho(h) = v @ rho(gh)
```

The matrix multiplication order matches group multiplication order, even though
row-vector application is from the right.

Block structure:

```text
228 = 64 + 144 + 8 + 12
```

| Block | Dim | Formula |
|-------|-----|---------|
| Cp | 64 | `kron(perm_mat, I_8)`; permutation only |
| Ep | 144 | `kron(perm_mat, I_12)`; permutation only |
| Co | 8 | permutation matrix with `Z_3` phases |
| Eo | 12 | permutation matrix with `Z_2` phases |

Matrix construction: for a permutation block, `M[perm[i], i] = 1.0`. For
orientation blocks, the entry is replaced by `exp(2*pi*1j*ori_delta/k)`.

Averaging operator:

```text
A = (1/|S|) sum_{s in S} rho(s)
```

The spectral decomposition is over this operator.

### 8.6 State Encoding: `CubieState`

```python
@dataclass(frozen=True)
class CubieState:
    corners_perm: np.ndarray  # (8,), values 0..7
    corners_ori: np.ndarray   # (8,), values 0,1,2
    edges_perm: np.ndarray    # (12,), values 0..11
    edges_ori: np.ndarray     # (12,), values 0,1
```

`corners_perm[i]` records which physical corner cubie occupies position `i`.
Only 7 of 8 corner orientations and 11 of 12 edge orientations are independent:
the last is determined by the total twist and flip constraints.

### 8.7 Generator Set Resolution

Half-turns are separate generator elements with their own `rho` matrices. They
are not computed as `rho(direction=1)^2` inside the canonical 18-generator set.

The full 18-generator set contains 12 quarter-turns and 6 half-turns. This
matters: the spectral decomposition of

```text
A_18 = (12 QT_all + 6 HT_all) / 18
```

is not the same as the spectral decomposition of

```text
A_12 = QT_all / 12
```

### 8.8 Summary

| Context | Convention | Notation |
|---------|------------|----------|
| State transition | right action | `s * m = m.act(s)` |
| Geometry/stickers | left action | `m * s = m.act_left(s)` |
| Move composition | right-action composition | `m1 @ m2` means do `m1`, then `m2` |
| `rho` matrix | left-action matrix, right-applied to row vectors | `v' = v @ rho(g)` |
| Averaging | sum over generator matrices | `A = (1/|S|) sum rho(s)` |

---

## 9. Block Decomposition

The 228-dimensional representation decomposes into four blocks, in
`block_diag(Cp, Ep, Co, Eo)` order:

```python
TOTAL_DIM = 228
BLOCK_DIMS = {"cp": 64, "ep": 144, "co": 8, "eo": 12}

BLOCK_RANGES = {
    "cp": (0, 64),      # corner permutation
    "ep": (64, 208),    # edge permutation
    "co": (208, 216),   # corner orientation
    "eo": (216, 228),   # edge orientation
}
```

| Block | Dim | Formula | Content |
|-------|-----|---------|---------|
| cp | 64 | `8 x 8` | corner permutation |
| ep | 144 | `12 x 12` | edge permutation |
| co | 8 | `8 x 8` | corner orientation with `Z_3` phases |
| eo | 12 | `12 x 12` | edge orientation with `Z_2` phases |

The block order is fixed:

```text
cp -> ep -> co -> eo
```

All `rho` matrices, projectors, and transport tensors follow this layout.
Block projectors are diagonal masks, for example
`P_cp = diag(I_64, 0, 0, 0)`.

---

## 10. Solved State

The identity element of the group:

```python
CubieState.solved() == CubieState(
    corners_perm=[0, 1, 2, 3, 4, 5, 6, 7],
    corners_ori=[0, 0, 0, 0, 0, 0, 0, 0],
    edges_perm=[0, 1, ..., 11],
    edges_ori=[0, 0, ..., 0],
)
```

Corner index `i` is physical cubie `i` at position `i`, in the canonical
corner order. Edge index `j` is physical cubie `j` at position `j`, in the
canonical edge order. All orientations are zero.

The solved state serves as the reference state for transition tests, generated
state audits, and representation construction.

---

## 11. Numerical Tolerances

Default tolerance throughout the spectral framework:

```python
CubieSpectralOperator(tol=1e-6)
```

| Use | tol |
|-----|-----|
| Eigenvalue clustering | `abs(w - lam) < 1e-6` |
| Hermiticity check | `rtol=1e-6, atol=1e-6` |
| Rank determination by SVD | `1e-10` |
| Zero transport (`K=0`) | `1e-10` |
| `K` symmetry verification | `1e-15` |
| Commutant rank | `1e-6` |

`tol=1e-6` is the canonical value; it separates the six distinct `A_18`
eigenvalues cleanly. Tighter tolerances such as `1e-10` and `1e-15` are used
for structural assertions where false positives would corrupt the topology.
