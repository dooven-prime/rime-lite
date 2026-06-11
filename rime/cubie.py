from rime.base import class_property, class_cache, class_status, DATA_DIR
from rime.cube import CubeBase, ActionToken
from dataclasses import dataclass
import numpy as np
from scipy.linalg import block_diag

# ═══════════════════════════════════════════════════════════════════════════════
# Block constants (fixed by representation, independent of generator set)
# ═══════════════════════════════════════════════════════════════════════════════
N_GENERATORS = 18
TOTAL_DIM = 228
BLOCK_DIMS = {"cp": 64, "ep": 144, "co": 8, "eo": 12}

BLOCK_RANGES = {
    "cp": (0, 64),
    "ep": (64, 208),
    "co": (208, 216),
    "eo": (216, 228),
}


@dataclass(frozen=True)
class CubieState:
    """
    G = (S₈ × S₁₂) ⋉ (ℤ₃⁷ × ℤ₂¹¹)
    perm: dict[int, np.ndarray]      # orbit_id -> permutation
    ori: dict[int, np.ndarray]       # orbit_id -> orientation (optional)
    """
    corners_perm: np.ndarray  # (8,)  0..7, ∈ S₈
    corners_ori: np.ndarray  # (8,)  0..2, ∈ ℤ₃
    edges_perm: np.ndarray  # (12,) 0..11, ∈ S₁₂
    edges_ori: np.ndarray  # (12,) 0..1, ∈ ℤ₂

    @classmethod
    def solved(cls) -> "CubieState":
        """
        fully_solved
        - corners_perm (8!)
        - corners_ori  (Z3^7)
        - edges_perm   (12!)
        - edges_ori    (Z2^11)
        符号（permutation）
        几何（orientation）
        群结构（closure / inverse）
        """
        return cls(
            corners_perm=np.arange(8, dtype=np.int8),  # [0,1,...,7]
            corners_ori=np.zeros(8, dtype=np.int8),
            edges_perm=np.arange(12, dtype=np.int8),  # [0,1,...,11]
            edges_ori=np.zeros(12, dtype=np.int8),
        )

    def with_(self, **kwargs) -> "CubieState":
        data = dict(
            corners_perm=self.corners_perm,
            corners_ori=self.corners_ori,
            edges_perm=self.edges_perm,
            edges_ori=self.edges_ori,
        )
        data.update(kwargs)
        return CubieState(**data)

    def clone(self) -> "CubieState":
        return CubieState(
            corners_perm=self.corners_perm,
            corners_ori=self.corners_ori,
            edges_perm=self.edges_perm,
            edges_ori=self.edges_ori,
        )

    def inverse(self) -> "CubieState":
        """inv permutation 反转,orientation 同时修正"""
        cp = np.argsort(self.corners_perm)
        co = (-self.corners_ori[cp]) % 3
        ep = np.argsort(self.edges_perm)
        eo = (-self.edges_ori[ep]) % 2
        return CubieState(
            corners_perm=cp,
            corners_ori=co,
            edges_perm=ep,
            edges_ori=eo
        )

    def __eq__(self, other):
        if not isinstance(other, CubieState):
            return NotImplemented
        return (
                np.array_equal(self.corners_perm, other.corners_perm) and
                np.array_equal(self.corners_ori, other.corners_ori) and
                np.array_equal(self.edges_perm, other.edges_perm) and
                np.array_equal(self.edges_ori, other.edges_ori)
        )

    def __hash__(self):
        return hash(self.state().tobytes())  # dtype=np.uint8

    def state(self) -> np.ndarray:
        """
        40:(12+8)*2,
        perm 是离散标签（0~7, 0~11）ori 是模数空间（Z3 / Z2)
        """
        return np.concatenate([self.corners_perm, self.edges_perm, self.corners_ori, self.edges_ori])

    @property
    def vector(self) -> np.ndarray:
        """
        .to_rho()
        ρ_vec(g) ∈ ℂ^228
        把群元素（状态）映射到一个 228 维表示空间中的向量
        perm_onehot+ ori unitroot/sign
        64 + 144 + 8 + 12 = 228
        返回 ρ(g)·v₀ 的结果（embedding 视角）
        v0 = solved.vector
        v1 = rho_g @ v0
        sizes = [64, 144, 8, 12]
        v_real = np.concatenate([v.real, v.imag], axis=1)
        """
        cp = np.eye(8, dtype=np.float32)[self.corners_perm].flatten()  # 64
        ep = np.eye(12, dtype=np.float32)[self.edges_perm].flatten()  # 144

        omega = np.exp(2j * np.pi / 3)
        co = np.zeros(8, dtype=np.complex64)  # 8
        for i in range(8):
            if self.corners_ori[i] == 0:
                co[i] = 1
            elif self.corners_ori[i] == 1:
                co[i] = omega
            else:
                co[i] = omega ** 2

        vec = np.where(self.edges_ori == 0, 1.0, -1.0)
        eo = vec.astype(np.float32)  # 12
        return np.concatenate([cp, ep, co, eo])  # 228

    @classmethod
    def from_vector(cls, vec: np.ndarray) -> "CubieState":
        """
        从拼接的向量恢复魔方状态数据。
        vec: np.ndarray, 长度为228，由四部分拼接而成：
        """
        vec = np.asarray(vec)
        assert len(vec) == 228, "向量长度必须为228"

        # 分块提取（注意取实部，因为复数部分可能混入虚部）
        cp = vec[:64].reshape(8, 8).real  # (8,8)
        ep = vec[64:208].reshape(12, 12).real  # (12,12)
        co = vec[208:216]  # (8,) 复数
        eo = vec[216:].real  # (12,) 实数

        corners_perm = np.argmax(cp, axis=1).astype(np.int8)  # 每行最大值的索引
        edges_perm = np.argmax(ep, axis=1).astype(np.int8)

        #  角块方向：与三个单位根比较距离
        omega = np.exp(2j * np.pi / 3)
        targets = [1, omega, omega ** 2]
        corners_ori = np.zeros(8, dtype=np.int8)
        for i in range(8):
            dist = [abs(co[i] - t) for t in targets]
            corners_ori[i] = np.argmin(dist)

        # 棱块方向：由实部符号决定（原编码：ori=0 -> 1, ori=1 -> -1）
        # 理论上不会出现恰好为0的情况，若出现可视为1或根据容差处理
        edges_ori = (np.sign(eo) < 0).astype(np.int8)  # 负则为1，正则为0
        s = cls(corners_perm=corners_perm, corners_ori=corners_ori, edges_perm=edges_perm, edges_ori=edges_ori)
        # assert s.is_solvable(), f'from_vector is not solvable:{s}'
        return s

    def is_solvable(self) -> bool:
        """Parity and orientation sum invariants."""
        return (self.corners_ori.sum() % 3 == 0 and
                self.edges_ori.sum() % 2 == 0 and
                CubeBase.permutation_parity(self.corners_perm) ==
                CubeBase.permutation_parity(self.edges_perm))

    def to_sticker(self, n: int = 3) -> np.ndarray:
        stickers = np.arange(6 * n * n, dtype=np.uint32).reshape(6, n, n)

        solved_corners = CubeBase.get_corners(stickers)  # (8, 3)
        solved_edges = CubeBase.get_edges(stickers)  # (12, 2)
        for i, corners in enumerate(CubeBase.corner_coords(n=n)):
            cubie_id = self.corners_perm[i]
            twist = self.corners_ori[i]
            # solved 状态下这个 cubie 的 3 个顺序
            perms = solved_corners[cubie_id]  # (3,)
            # 旋转 twist 次（顺时针）
            actual_perms = np.roll(perms, -twist)  # orientation 负 twist = 逆时针 roll
            for pos, perm in zip(corners, actual_perms):  # [(f, r, c)]:[val]
                stickers[pos] = perm

        for i, edges in enumerate(CubeBase.edge_coords(n=n)):  # [[(face_idx, r, c), (face_idx, r, c)],
            cubie_id = self.edges_perm[i]
            flip = self.edges_ori[i]

            perms = solved_edges[cubie_id]  # (12,2)
            actual_perms = np.roll(perms, flip)  # 翻转或不翻 flip 1 swap
            for pos, perm in zip(edges, actual_perms):
                stickers[pos] = perm

        return stickers  # (6, n, n) 数组 .flatten().astype(np.float32)


@dataclass(frozen=True)
class CubieMove:
    corners_perm: np.ndarray  # σ_c (8,) / tuple[int, ...]
    edges_perm: np.ndarray  # σ_e (12,)

    # orientation delta (mod)
    corners_ori_delta: np.ndarray  # Δ_c (8,)  int mod 3
    edges_ori_delta: np.ndarray  # Δ_e (12,) int mod 2

    def act(self, s: CubieState) -> CubieState:
        '''
        右作用 (state' = state ∘ move)
        用于pruning/BFS/IDA*/solver/phase判断。所有搜索/优化逻辑必须用此，确保半直积自洽和pruning table匹配。
        Phase-1 / Phase-2  / group logic —— 只允许用 act.用于群论/search逻辑
        act(s, m) = s ∘ m 编码等价, (π, o) ∘ (σ, Δ) ，不做 canonical 修正
        self.corners_perm 已经是"索引搬运表" 完全忽略 pull back
        self.corners_ori_delta 已经在 state 的 reference 下
        连续多次 apply：act(act(act(s, m1), m2), m3) = s ∘ m1 ∘ m2 ∘ m3
        new_ori = (old_ori[perm⁻¹] + Δo) % k
        new_ori = (old_ori ∘ perm + ori_delta) mod 3 （复合顺序：先 old 后 self）
        '''
        # 应用 delta
        cp = s.corners_perm[self.corners_perm]  # new_corners_perm
        ep = s.edges_perm[self.edges_perm]  # new_edges_perm

        co = (s.corners_ori[self.corners_perm] + self.corners_ori_delta) % 3  # new_corners_ori
        eo = (s.edges_ori[self.edges_perm] + self.edges_ori_delta) % 2  # new_edges_ori
        # co = (s.corners_ori + self.corners_ori_delta)[np.argsort(self.corners_perm)] % 3
        # eo = (s.edges_ori + self.edges_ori_delta)[np.argsort(self.edges_perm)] % 2
        return CubieState(cp, co, ep, eo)

    def act_left(self, s: CubieState) -> CubieState:
        """
        左作用 (state' = move ⋅ state),半直积作用律,
        用于几何构造/贴纸旋转/调试/测试。仅限从solved生成state，或与外部模型对齐
        左作用（几何）  apply(m, s) = m ∘ s  = move ∘ state, 用于几何/贴纸
        Apply this CubieMove to a CubieState using semidirect product law.
        This version is topology-safe and orientation-correct.
        |G| ≈ 4.3e19
        G = (Perm × Ori) ⋊ Move
        群作用,严格等价于：
        (σ, Δ) · (π, o) = (σ∘π, o∘σ⁻¹ + Δ∘σ⁻¹)

        new_perm = σ ∘ old_perm
        new_ori[i] = old_ori[σ⁻¹(i)] + Δ[σ⁻¹(i)]
        new_ori[i] = old_ori[ self.perm⁻¹(i) ] + self.ori_delta[ self.perm⁻¹(i) ]
        """
        # ---------- corners ----------
        σc = self.corners_perm
        Δc = self.corners_ori_delta
        σc_inv = np.argsort(σc)

        new_corners_perm = σc[s.corners_perm]
        new_corners_ori = (s.corners_ori[σc_inv] + Δc[σc_inv]) % 3
        # ---------- edges ----------
        σe = self.edges_perm
        Δe = self.edges_ori_delta
        σe_inv = np.argsort(σe)

        new_edges_perm = σe[s.edges_perm]
        new_edges_ori = (s.edges_ori[σe_inv] + Δe[σe_inv]) % 2

        return CubieState(
            corners_perm=new_corners_perm,
            corners_ori=new_corners_ori,
            edges_perm=new_edges_perm,
            edges_ori=new_edges_ori,
        )

    def convert(self) -> "CubieMove":
        """
        桥梁（双向）act_left ↔ act opposite
        坐标系翻转、符号约定改变
        Convert this move (assuming left/right action delta) to right/left action equivalent.
        Δ_left = -Δ_right   (mod k)
        delta = -delta % mod
        """
        return CubieMove(
            corners_perm=self.corners_perm,  # perm 不变，位置关系不变
            corners_ori_delta=(-self.corners_ori_delta) % 3,  # 翻转符号，每个块的扭转方向反过来
            edges_perm=self.edges_perm,
            edges_ori_delta=(-self.edges_ori_delta) % 2,
        )

    def compose(self, other: "CubieMove") -> "CubieMove":
        """
        multiply（半直积乘法）右作用复合：self ∘ other = 先 self 后 other
        (self ∘ other).act(s) == other.act(self.act(s))
        (σ₁, Δ₁) ∘ (σ₂, Δ₂) = (σ₁ ∘ σ₂, Δ₁ + Δ₂ ∘ σ₁⁻¹)
        """

        # ---------- corners ----------
        σ1 = self.corners_perm
        Δ1 = self.corners_ori_delta
        σ2 = other.corners_perm
        Δ2 = other.corners_ori_delta

        corners_perm = σ1[σ2]  # σ1 ∘ σ2
        corners_ori_delta = (Δ1[σ2] + Δ2) % 3

        # ---------- edges ----------
        τ1 = self.edges_perm
        δ1 = self.edges_ori_delta
        τ2 = other.edges_perm
        δ2 = other.edges_ori_delta

        edges_perm = τ1[τ2]
        edges_ori_delta = (δ1[τ2] + δ2) % 2

        return CubieMove(
            corners_perm=corners_perm,
            corners_ori_delta=corners_ori_delta,
            edges_perm=edges_perm,
            edges_ori_delta=edges_ori_delta,
        )

    def inverse(self) -> "CubieMove":
        """
        右作用逆元（半直积）：
        (σ, Δ)⁻¹ = (σ⁻¹, -Δ ∘ σ⁻¹)
        """
        # ---------- corners ----------
        σ = self.corners_perm
        Δ = self.corners_ori_delta
        σ_inv = np.argsort(σ)

        corners_perm = σ_inv
        corners_ori_delta = (-Δ[σ_inv]) % 3

        # ---------- edges ----------
        τ = self.edges_perm
        δ = self.edges_ori_delta
        τ_inv = np.argsort(τ)

        edges_perm = τ_inv
        edges_ori_delta = (-δ[τ_inv]) % 2

        return CubieMove(
            corners_perm=corners_perm,
            corners_ori_delta=corners_ori_delta,
            edges_perm=edges_perm,
            edges_ori_delta=edges_ori_delta,
        )

    @classmethod
    def identity(cls) -> "CubieMove":
        # Identity,基坐标系,什么都没发生
        return cls(
            corners_perm=np.arange(8, dtype=np.int8),
            corners_ori_delta=np.zeros(8, dtype=np.int8),
            edges_perm=np.arange(12, dtype=np.int8),
            edges_ori_delta=np.zeros(12, dtype=np.int8),
        )

    def clone(self):
        return CubieMove(
            corners_perm=self.corners_perm,
            corners_ori_delta=self.corners_ori_delta,
            edges_perm=self.edges_perm,
            edges_ori_delta=self.edges_ori_delta,
        )

    def rho(self) -> np.ndarray:
        """ρ(g) ∈ GL(228, ℂ) — 群表示矩阵（left action）。

        Cp/Ep: kronecker 置换表示 (one-hot perm ⊗ I)。
        Co/Eo: 置换 + 单位根嵌入，ori_delta 作为对角相位。
        ρ(g)ρ(h) = ρ(gh), ρ(g⁻¹) = ρ(g)*, ρ(g)ρ(g)* = I.
        右作用: v @ ρ(g) = ρ(g).T @ v.
        v' = v @ ρ(g)，等价于 ρ(g)^T @ v
        """

        def _perm_mat(perm):
            n = len(perm)
            M = np.zeros((n, n), dtype=np.float32)
            for i in range(n):
                M[perm[i], i] = 1.0
            return M

        Cp = np.kron(_perm_mat(self.corners_perm), np.eye(8, dtype=np.float32))
        Ep = np.kron(_perm_mat(self.edges_perm), np.eye(12, dtype=np.float32))

        omega = np.exp(2j * np.pi / 3)
        Co = np.zeros((8, 8), dtype=np.complex64)
        for i in range(8):
            Co[self.corners_perm[i], i] = omega ** int(self.corners_ori_delta[i])

        Eo = np.zeros((12, 12), dtype=np.float32)
        for i in range(12):
            Eo[self.edges_perm[i], i] = -1.0 if self.edges_ori_delta[i] % 2 else 1.0

        return block_diag(Cp, Ep, Co, Eo)

    @property
    def matrix(self) -> np.ndarray:
        """右作用算子 — 等价于 ρ(g)。历史别名，请直接用 rho()。
        V @ mv.matrix = mv.rho().T @ V
        """
        return self.rho()

    def __eq__(self, other):
        if not isinstance(other, CubieMove):
            return NotImplemented
        return (
                np.array_equal(self.corners_perm, other.corners_perm) and
                np.array_equal(self.edges_perm, other.edges_perm) and
                np.array_equal(self.corners_ori_delta, other.corners_ori_delta) and
                np.array_equal(self.edges_ori_delta, other.edges_ori_delta)
        )

    def __hash__(self):
        return hash((
            self.corners_perm.tobytes(),
            self.corners_ori_delta.tobytes(),
            self.edges_perm.tobytes(),
            self.edges_ori_delta.tobytes(),
        ))

    def __matmul__(self, other) -> "CubieMove":
        """
        通过 @ 运算符实现右作用复合（半直积乘法）。
        R @ U 表示先 R 后 U  (R ∘ U) 通常不可交换
        即：`self @ other` 等价于 `self.compose(other)`，
           先执行 self，再执行 other（右作用）。
           公式：(σ₁, Δ₁) @ (σ₂, Δ₂) = (σ₁ ∘ σ₂, Δ₁ + Δ₂ ∘ σ₁⁻¹)
        """
        if not isinstance(other, CubieMove):
            return NotImplemented
        return self.compose(other)

    def with_(self, **kwargs) -> "CubieMove":
        data = dict(
            corners_perm=self.corners_perm,
            corners_ori_delta=self.corners_ori_delta,
            edges_perm=self.edges_perm,
            edges_ori_delta=self.edges_ori_delta,
        )
        data.update(kwargs)
        return CubieMove(**data)

    @classmethod
    def from_rotation(cls, axis: int, side: int, direction: int) -> 'CubieMove':
        """
        生成的是「右作用 / apply 语义」的 move，理论 move，在 cubie 参考系下定义
        定义在"绝对 reference 坐标系"上的群元素,几何表示
        独立计算 move 的 perm 和 delta（不依赖贴纸，用坐标模拟旋转）
        Build CubieMove from rotation parameters.
        axis: 0 = X (R/L), 1 = Y (U/D), 2 = Z (F/B)
        side: +1 or -1,layer ∈ {+1,-1} side sign，不是层编号
        direction: +1 (90°) or -1 (-90°)
        orientation delta（Z₂） orientation delta（Z₃）
        corner_ori_delta[i] ∈ {0,1,2} new_ori = (old_ori ∘ perm + ori_delta) mod 3
        局部增量,比较"旋转前后"，每个 cubie 去了谁的位置，朝向变了多少,move 对"被搬到 i 位置的角块"额外施加了多少扭转
        """
        assert axis in (0, 1, 2)
        assert side in (-1, 0, 1)

        turns = abs(direction) % 4  # Compute turns direction % 4
        sign_dir = 1 if direction > 0 else -1
        if turns == 0:
            return cls.identity()  # Identity
        # Define corner and edge positions
        corner_positions = np.array(CubeBase.CORNER_POS_SIGNS, dtype=np.int8)
        edge_positions = np.array(CubeBase.EDGE_POS_SIGNS, dtype=np.int8)
        # Current positions for simulation
        current_corner_pos = corner_positions.copy()
        current_edge_pos = edge_positions.copy()
        # Affected masks,affected 集合在 move 内不是常量,必须在 move 开始前就确定
        affected_corners = (corner_positions[:, axis] == side)
        affected_edges = (edge_positions[:, axis] == side)
        # Initialize deltas
        corners_ori_delta = np.zeros(8, dtype=np.int8)
        edges_ori_delta = np.zeros(12, dtype=np.int8)

        for _ in range(turns):
            # Update corner ori deltas if not U/D axis
            if axis != 1:  # U/D 不变,不 twist, 角块朝向以 U/D 为基准
                a = (axis + 1) % 3
                b = (axis + 2) % 3
                for i in range(8):
                    if affected_corners[i]:
                        sign_a = np.sign(current_corner_pos[i, a])
                        sign_b = np.sign(current_corner_pos[i, b])
                        if turns == 1:
                            # single turn: twist depends on axis & face, not direction
                            twist = (sign_a * sign_b * side) % 3 if axis == 0 else (-sign_a * sign_b * side) % 3
                        else:
                            twist = (-sign_a * sign_b * sign_dir) % 3
                        corners_ori_delta[i] = (corners_ori_delta[i] + twist) % 3

            # Update edge ori deltas if F/B axis
            if axis == 2:  # F/B 变,翻转
                for i in range(12):
                    if affected_edges[i]:
                        edges_ori_delta[i] ^= 1  # Z2 翻转,翻转不依赖 sign_dir（90° 和 -90° 都翻一次） = (edges_ori_delta[i] + 1) % 2

            # R/L (axis=0): edges 不变
            # U/D (axis=1): 都不变

            # Update positions with rotation,必须是 right-hand
            for i in range(8):
                if affected_corners[i]:
                    current_corner_pos[i] = CubeBase.rotate_coord(current_corner_pos[i], axis, sign_dir)

            for i in range(12):
                if affected_edges[i]:
                    current_edge_pos[i] = CubeBase.rotate_coord(current_edge_pos[i], axis, sign_dir)

        # 计算 perm（从 current_pos 映射回原始 pos）
        # Compute perms: for each original i, find the dst where original_pos[dst] == current_pos[i]
        corners_perm = np.zeros(8, dtype=np.int8)
        for i in range(8):
            dst = np.where(np.all(corner_positions == current_corner_pos[i], axis=1))[0][0]
            corners_perm[i] = dst

        edges_perm = np.zeros(12, dtype=np.int8)
        for i in range(12):
            dst = np.where(np.all(edge_positions == current_edge_pos[i], axis=1))[0][0]
            edges_perm[i] = dst

        return cls(
            corners_perm=corners_perm,
            corners_ori_delta=corners_ori_delta,
            edges_perm=edges_perm,
            edges_ori_delta=edges_ori_delta
        )

    @class_property('BASIC_PRIM_MOVES')
    def basic_generators(cls) -> list[tuple]:
        """所有 18 个基本 move（U D R L F B 的 ±90° 和 180°） 6 faces × {1,2,3} """
        moves = []
        for axis in (0, 1, 2):
            for side in (-1, +1):
                for direction in (-1, +1, +2):
                    moves.append((axis, side, direction))
        return moves  # face_id = move_id // 3 {k: i for i, k in enumerate(moves)}

    @class_property('PRIM_MOVES')
    def prim_moves(cls) -> dict[tuple, 'CubieMove']:
        """
        CubieMove  ──apply──▶ CubieState
        18 BFS / IDDFS 深度可能 +1
        外层转动，中间层用扩展 moves 生成
        """
        return {k: cls.from_rotation(*k) for k in cls.basic_generators()}  # 生成 CubieMove delta

    @class_property('SLICE_MOVES')
    def slice_moves(cls) -> dict[tuple, 'CubieMove']:
        """
        额外生成 slice move（side=0）：M, E, S 的 ±90°, 180°
        用于扩展搜索或 n>3 魔方
        影响中层 edge，但不作为 prim（冗余）,slice 作为 derived,影响 edge permutation parity (改变一次)
        """
        slice_moves = {}
        for axis in (0, 1, 2):
            # for direction in (-1, +1, +2):
            slice_moves[(axis, 0, 2)] = cls.from_rotation(axis, 0, 2)
        return slice_moves
    
    @class_property('PRIM_RHO_MOVES')
    def rho_moves(cls) -> dict[tuple, tuple['CubieMove', np.ndarray]]:
        """rho representation dict for generator set.
        Return {move_key: (CubieMove, rho_matrix)}.
        """
        return {k: (m, m.rho().astype(np.complex128)) for k, m in cls.prim_moves.items()}

    def to_sticker_move(self, n: int) -> ActionToken | None:
        """
        把 CubieMove 转换为 实际 act 供 StickerMove(生成元在几何空间的表示)。
        从 prim cubie_move 获取
        """
        all_moves = self.prim_moves().copy()
        all_moves.update(self.slice_moves())
        k = next((a for a, m in all_moves.items() if m == self), None)
        if k is None:
            return None
        return ActionToken.from_cubie_move(*k, n=n)

    @staticmethod
    def is_redundant(last, cur) -> bool:
        """is_inverse, 禁止与上一个动作在同一面（axis+layer）上连续转动且总效果为 0 mod 4"""
        if last is None:
            return False
        if isinstance(last, CubieMove):
            return last.compose(cur) == CubieMove.identity()

        axis1, side1, dir1 = last
        axis2, side2, dir2 = cur

        # 同轴同层,连续转，反向,必冗余
        if axis1 == axis2 and side1 == side2:
            return (dir1 + dir2) % 4 == 0

        return False

    def is_primitive(self) -> bool:
        """判断当前 move 是否是 prim_moves 中的基本转动"""
        return any(m is self or m == self for m in self.prim_moves.values())

    @staticmethod
    def build_move_part(perm0, ori0, perm1, ori1, mod: int) -> tuple[np.ndarray, np.ndarray]:
        """
        右作用下求 move delta：s1 = s0 ∘ m, s1 = s0 ∘ m → m = s0⁻¹ ∘ s1
        move_ori[new_pos] = ori1[new_pos] - ori0[old_pos]   (mod)
        """
        n = len(perm0)
        move_perm = np.zeros(n, dtype=np.int8)
        move_ori = np.zeros(n, dtype=np.int8)
        # 逆置换
        inv_perm0 = np.argsort(perm0)  # cubie → pos in s0
        for pos in range(n):
            cubie = perm1[pos]  # pos 在 s1 的 cubie
            old_pos = inv_perm0[cubie]  # 这个 cubie 在 s0 的位置
            move_perm[pos] = old_pos  # m 把 old_pos 的内容搬到 pos
            move_ori[pos] = (ori1[pos] - ori0[old_pos]) % mod  # ori delta = ori1[pos] - ori0[old_pos]
            assert (ori0[old_pos] + move_ori[pos]) % mod == ori1[pos]

        return move_perm, move_ori

    @classmethod
    def build(cls, s0: 'CubieState', s1: 'CubieState') -> "CubieMove":
        """
         buildetween 相对于 s 的局部 delta move g = A.inv().act(B)
         s0 原始 CubieState
         s1 旋转后状态
         s1 = s0 ∘ m   （右作用语义）
         m = s0⁻¹ ∘ s1 m = A⁻¹ ∘ B
         构建 CubieMove：不依赖贴纸索引顺序来算 delta，直接从 CubieState 计算。
         s0 = CubieState.solved()
         CubieMove.build(s0, move.act(s0)) == move
        """
        assert s0.is_solvable() and s1.is_solvable(), f"States must be solvable:{s0}\n{s1}"
        σc, Δc = cls.build_move_part(s0.corners_perm, s0.corners_ori, s1.corners_perm, s1.corners_ori, 3)
        σe, Δe = cls.build_move_part(s0.edges_perm, s0.edges_ori, s1.edges_perm, s1.edges_ori, 2)
        return cls(
            corners_perm=σc,
            corners_ori_delta=Δc,
            edges_perm=σe,
            edges_ori_delta=Δe,
        )
