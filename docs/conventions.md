# Geometric & Move Conventions

This document is the single source of truth for all coordinate systems, face mappings, cubie orderings, generator encodings, rotation conventions, move encodings, and parser invariants used throughout the RIME codebase and papers.

**Design principle** (from `CubeGeometry`): The only "hardcoded" element is `_AXIS_FACE_MAP`. Everything else — corner positions, edge positions, rotation strips, face normals — is derived from coordinate rules (corners = exactly 3 non-zero coords in {±1}³, edges = exactly 2 non-zero coords in {±1,0}³) and canonical XZ-plane ordering cycles.

---

## 1. Coordinate System

Right-handed Cartesian coordinate system:

```
+X → R    (axis 0)
+Y → U    (axis 1)
+Z → F    (axis 2)
```

Axis vectors: `AXIS_VEC = np.eye(3)` — axis 0 = X = [1,0,0], axis 1 = Y = [0,1,0], axis 2 = Z = [0,0,1].

---

## 2. Face Ordering

The only hardcoded element:

```python
_AXIS_FACE_MAP = {(0, 0): 'R', (0, 1): 'L',
                  (1, 0): 'U', (1, 1): 'D',
                  (2, 0): 'F', (2, 1): 'B'}
```

- `axis` ∈ {0, 1, 2}
- `side` ∈ {0, 1} — 0 = POS face (+axis normal), 1 = NEG face (-axis normal)

Derived `AXIS_FACE`:

```python
AXIS_FACE = [
    ('R', 'L'),  # X axis (0)
    ('U', 'D'),  # Y axis (1)
    ('F', 'B'),  # Z axis (2)
]
```

Canonical face list: `FACES = ['U', 'D', 'F', 'B', 'L', 'R']`

Rotation strips (CCW ordering of faces around each axis, viewed from +axis):

```python
AXIS_STRIP = (
    ['U', 'F', 'D', 'B'],  # X: from +X, CCW
    ['F', 'R', 'B', 'L'],  # Y: from +Y, CCW
    ['U', 'L', 'D', 'R'],  # Z: from +Z, CCW
)
```

---

## 3. Cubie Ordering

### 3.1 Corner Ordering

8 corners, each has exactly 3 non-zero coordinates in {±1}³. U-layer CW then D-layer CW, derived from XZ-plane cycle `[(+1,+1), (-1,+1), (-1,-1), (+1,-1)]` (clockwise from +Y).

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

Derived partitions: `U_CORNER_POSITIONS` = (0,1,2,3), `D_CORNER_POSITIONS` = (4,5,6,7).

### 3.2 Edge Ordering

12 edges, each has exactly 2 non-zero coordinates in {±1,0}³. U-layer axis → middle diagonal → D-layer axis.

```python
EDGE_POS_SIGNS = [
    (+1, +1, 0),  # 0:  UR    U-layer (y=+1)
    (0, +1, +1),  # 1:  UF
    (-1, +1, 0),  # 2:  UL
    (0, +1, -1),  # 3:  UB
    (+1, 0, +1),  # 4:  RF    middle (y=0)
    (-1, 0, +1),  # 5:  LF
    (-1, 0, -1),  # 6:  LB
    (+1, 0, -1),  # 7:  RB
    (+1, -1, 0),  # 8:  DR    D-layer (y=-1)
    (0, -1, +1),  # 9:  DF
    (-1, -1, 0),  # 10: DL
    (0, -1, -1),  # 11: DB
]
```

---

## 4. Generator Ordering

The 18 face-turn generators are the outer-layer moves of the 3×3×3 cube:

```
axis 0 (X):  R  R' R2  L  L' L2
axis 1 (Y):  U  U' U2  D  D' D2
axis 2 (Z):  F  F' F2  B  B' B2
```

Canonical generator list (`CubieMove.prim_moves`):

```
(0, +1, +1)  (0, +1, -1)  (0, +1, 2)   ← R, R', R2
(0, -1, +1)  (0, -1, -1)  (0, -1, 2)   ← L, L', L2
(1, +1, +1)  (1, +1, -1)  (1, +1, 2)   ← U, U', U2
(1, -1, +1)  (1, -1, -1)  (1, -1, 2)   ← D, D', D2
(2, +1, +1)  (2, +1, -1)  (2, +1, 2)   ← F, F', F2
(2, -1, +1)  (2, -1, -1)  (2, -1, 2)   ← B, B', B2
```

Full generator set: `QT_all` = 12 quarter-turn moves, `HT_all` = 6 half-turn moves, `A_18` = (12 QT_all + 6 HT_all) / 18.

---

## 5. Rotation Convention

**`direction = +1` means clockwise when viewed from outside the cube along the positive face normal.**

- `direction = +1`: CW — standard face turn with no prime (`R`, `U`, `F`)
- `direction = -1`: CCW — prime move (`R'`, `U'`, `F'`)
- `direction = 2`: 180° half-turn (`R2`, `U2`, `F2`)

This is the standard Rubik's Cube convention: look at the face from the outside, a clockwise twist is `+1`.

---

## 6. Move Encoding

Two encodings coexist in the codebase:

### 6.1 Cubie-level: `(axis, side, direction)`

Direct `CubieMove` keys, used in `prim_moves`, spectral operators, and all group-theoretic code:

- `axis` ∈ {0, 1, 2}
- `side` ∈ {+1, -1} — POS or NEG face
- `direction` ∈ {+1, -1, 2}

### 6.2 Sticker-level: `ActionToken`

Dataclass for sticker simulation, decouples layer from geometry:

```python
@dataclass(frozen=True)
class ActionToken:
    axis: int       # 0, 1, 2
    layer: int      # layer = side * mid (N=3: ±1 for outer, 0 for center)
    direction: int  # +1, -1, 2
```

Conversion between the two:

```python
ActionToken.from_cubie_move(axis, side, direction, n)  # cubie → ActionToken
token.to_cubie_move(n)                                  # ActionToken → cubie key
```

For N=3: `layer = side * 1`, so `layer=+1` ↔ `side=+1`, `layer=-1` ↔ `side=-1`, `layer=0` ↔ `side=0` (center slice `M`/`E`/`S`).

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

```
ActionToken.transform(s).__str__() == s
```

For any valid move string `s`, parse → stringify recovers the original:

```
ActionToken.transform("U")   → axis=1, layer=+1, dir=+1 → __str__() = "U"
ActionToken.transform("U'")  → axis=1, layer=+1, dir=-1 → __str__() = "U'"
ActionToken.transform("U2")  → axis=1, layer=+1, dir=2  → __str__() = "U2"
```

### 7.2 Parser grammar (`ActionToken.transform`)

Supported input syntax:

| Input | Meaning |
|-------|---------|
| `U`, `U'`, `U2` | Standard face turns (all 6 faces) |
| `Rw`, `Rw'`, `Rw2` | Wide turns (default width = 2) |
| `2Rw`, `3Uw'`, `2Rw2` | Explicit width prefix |
| `M`, `M'`, `M2`, `E`, `S` | Slice moves |

Parsing rules:
1. Trailing `2` → direction = 2, strip
2. Trailing `'` → direction = -1, strip
3. `M`/`E`/`S` → axis = 0/1/2, layer = 0
4. Otherwise: extract `(\d*)([URFDLB])(w?)` — width, face, wide flag
5. Width with `w` → wide turn; width with digit only → that many layers from outside

---

## 8. Action Direction (act / ρ / compose)

The codebase has two parallel action conventions serving different purposes. Both are correct — they are interconvertible via `convert()`.

### 8.1 Right action: `CubieMove.act`

```python
move.act(s)  # state' = state ∘ move
```

Used for **search / BFS / IDA* / solver / pruning**. All search logic must use this to stay self-consistent with pruning tables.

Effect on state:

```
cp[i] = s.corners_perm[self.corners_perm[i]]   # new_at_i = old_at_move_i
co[i] = (s.corners_ori[self.corners_perm[i]] + self.corners_ori_delta[i]) % 3
```

Successive application: `act(act(act(s, m1), m2), m3)` = `s ∘ m1 ∘ m2 ∘ m3`.

### 8.2 Left action: `CubieMove.act_left`

```python
move.act_left(s)  # state' = move · state
```

Used for **geometry construction / sticker rotation / debugging**. Semidirect product law:

```
(σ, Δ) · (π, o) = (σ ∘ π,  o ∘ σ⁻¹ + Δ ∘ σ⁻¹)
```

Effect on state:

```
cp = σ[s.corners_perm]                           # new = σ ∘ old
co[i] = (s.corners_ori[σ⁻¹(i)] + Δ[σ⁻¹(i)]) % 3  # pull-back orientation
```

### 8.3 Interconversion

```python
move.convert()  # Δ → -Δ mod k, perm unchanged
```

Bidirectional bridge. The delta (orientation change) flips sign; the permutation is invariant.

### 8.4 Composition: `compose` / `@`

Right-action composition. `self @ other` = `self.compose(other)` = do self then other:

```
(self @ other).act(s) == other.act(self.act(s))
```

Semidirect product formula:

```
(σ₁, Δ₁) @ (σ₂, Δ₂) = (σ₁ ∘ σ₂,  Δ₁ + Δ₂ ∘ σ₁⁻¹)
```

### 8.5 Representation ρ(g)

```python
move.rho()  # ρ(g) ∈ GL(228, ℂ), block_diag(Cp, Ep, Co, Eo)
```

**ρ is a left-action matrix:** ρ(g)ρ(h) = ρ(gh), ρ(g⁻¹) = ρ(g)^H, ρ(g)ρ(g)^H = I.

But vectors are **row vectors**, so application is right-multiplication:

```
v' = v @ ρ(g)
```

Consequence: `v @ ρ(g) @ ρ(h) = v @ ρ(gh)` — the matrix multiplication order matches the group multiplication order, even though the effective action on the vector is from the right.

Block structure (228 = 64 + 144 + 8 + 12):

| Block | Dim | Formula |
|-------|-----|---------|
| Cp | 64 | kron(perm_mat, I₈) — permutation only |
| Ep | 144 | kron(perm_mat, I₁₂) — permutation only |
| Co | 8 | perm_mat with ω^k phases — permutation + Z₃ twist |
| Eo | 12 | perm_mat with ±1 phases — permutation + Z₂ flip |

Matrix construction: for a permutation block, `M[perm[i], i] = 1.0` (column i has 1 at row perm[i]). For orientation blocks, the 1.0 is replaced by the phase factor `exp(2πi · ori_delta / k)`.

**Averaging operator:** `A = (1/|S|) Σ_{s∈S} ρ(s)` sums over the chosen generator set. The spectral decomposition is over A.

### 8.6 State encoding: `CubieState`

```python
@dataclass(frozen=True)
class CubieState:
    corners_perm: np.ndarray  # (8,), values 0..7 — which cubie at each position
    corners_ori: np.ndarray   # (8,), values 0,1,2 — orientation mod 3
    edges_perm: np.ndarray    # (12,), values 0..11
    edges_ori: np.ndarray     # (12,), values 0,1 — orientation mod 2
```

`corners_perm[i]` = which physical corner cubie occupies position i. Oriented state: only 7 of 8 corner orientations and 11 of 12 edge orientations are independent (the last is determined by the parity constraint — total twist sum ≡ 0 mod 3, total flip sum ≡ 0 mod 2).

### 8.7 Generator set resolution

`direction = 2` (half-turns) are **separate generator elements** with their own ρ matrices. They are NOT computed as ρ(direction=1)². The full 18-generator set includes 12 quarter-turns (QT_all) and 6 half-turns (HT_all), each with an independent ρ matrix. This matters: the spectral decomposition of A_18 = (12·QT_all + 6·HT_all) / 18 is not the same as the spectral decomposition of A_12 = QT_all / 12.

### 8.8 Summary

| Context | Convention | Notation |
|---------|-----------|----------|
| Search / BFS / solver | Right action | `s ∘ m` = `m.act(s)` |
| Geometry / stickers | Left action | `m · s` = `m.act_left(s)` |
| Compose moves | Right-action composition | `m1 @ m2` = do m1 then m2 |
| ρ matrix | Left-action matrix, right-applied to row vectors | `v' = v @ ρ(g)`, `ρ(gh) = ρ(g)ρ(h)` |
| Averaging | Sum over generator ρ matrices | `A = (1/|S|) Σ ρ(s)` |

---

## 9. Block Decomposition

The 228-dimensional representation decomposes into four blocks, laid out in `block_diag(Cp, Ep, Co, Eo)` order:

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
| cp | 64 | 8 × 8 | Corner permutation (8! possible states) |
| ep | 144 | 12 × 12 | Edge permutation (12! possible states) |
| co | 8 | 8 × 8 | Corner orientation (Z₃ phases) |
| eo | 12 | 12 × 12 | Edge orientation (Z₂ phases) |

The block order is fixed: cp → ep → co → eo. All ρ matrices, projectors, and transport tensors follow this layout. Block projectors are diagonal masks: `P_cp = diag(I₆₄, 0, 0, 0)`, etc.

---

## 10. Solved State

The identity element of the group:

```python
CubieState.solved() == CubieState(
    corners_perm=[0, 1, 2, 3, 4, 5, 6, 7],   # identity permutation
    corners_ori=[0, 0, 0, 0, 0, 0, 0, 0],     # all zero twist
    edges_perm=[0, 1, ..., 11],                 # identity permutation
    edges_ori=[0, 0, ..., 0],                   # all zero flip
)
```

Corner index i = physical cubie i at position i, in the canonical corner order (§5). Edge index j = physical cubie j at position j, in the canonical edge order (§6). All orientations are zero (no twist, no flip).

The solved state serves as the reference for: BFS root, pruning table origin, state generation (`act_left` from solved), and the δ-gap vector baseline in spectral control policies.

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
| Rank determination (SVD) | `1e-10` |
| Zero transport (K=0) | `1e-10` |
| κ symmetry verification | `1e-15` |
| Commutant rank | `1e-6` |

`tol=1e-6` is the canonical value — it separates the 6 distinct A_18 eigenvalues cleanly. Tighter tolerances (1e-10, 1e-15) are used for structural assertions (zero transport, symmetry) where false positives would corrupt the topology.
