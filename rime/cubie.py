from rime.base import class_property, class_cache, class_status, DATA_DIR
from rime.cube import CubeBase, ActionToken, StickerCube
from dataclasses import dataclass
import numpy as np
from scipy.linalg import block_diag
from collections import deque
import random, math

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

    @property
    def key(self) -> tuple:
        corner_idx = CubeBase.encode_perm(self.corners_perm.tolist())
        edge_idx = CubeBase.encode_perm(self.edges_perm.tolist())
        corner_ori = self.corner_ori_coord
        edge_ori = self.edge_ori_coord
        return corner_idx, edge_idx, corner_ori, edge_ori

    @classmethod
    def from_key(cls, key: tuple) -> "CubieState":
        corners_perm = np.array(CubeBase.decode_perm(key[0], 8), dtype=np.int8)
        edges_perm = np.array(CubeBase.decode_perm(key[1], 12), dtype=np.int8)  # np.int32
        corners_ori = cls.decode_corner_ori(key[2])
        edges_ori = cls.decode_edge_ori(key[3])
        return CubieState(
            corners_perm=corners_perm,
            corners_ori=corners_ori,
            edges_perm=edges_perm,
            edges_ori=edges_ori,
        )

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
        #assert s.is_solvable(), f'from_vector is not solvable:{s}'
        return s

    def to_sticker(self, n: int = 3) -> np.ndarray:
        """
        从 CubieState 生成完整的贴纸状态 (6, n, n) 数组 -> StickerMove
        - 支持任意 n（中心块固定，边角根据 cubie）,目前支持3阶
        某一个 gauge 下的具体代表
        Sticker equality is not guaranteed; cubie equality is the invariant
        """
        base = CubeBase(n=n)
        stickers = base.solved_idx.copy()

        solved_corners = base.get_corners(stickers)  # (8, 3)
        solved_edges = base.get_edges(stickers)  # (12, 2)
        # [[(face_idx, r, c), (face_idx, r, c), (face_idx, r, c)],..
        for i, corners in enumerate(base.corner_coords(n=n)):
            cubie_id = self.corners_perm[i]
            twist = self.corners_ori[i]
            # solved 状态下这个 cubie 的 3 个顺序
            perms = solved_corners[cubie_id]  # (3,)
            # 旋转 twist 次（顺时针）
            actual_perms = np.roll(perms, -twist)  # orientation 负 twist = 逆时针 roll

            # 贴到 3 个面
            for pos, perm in zip(corners, actual_perms):  # [(f, r, c)]:[val]
                stickers[pos] = perm

        for i, edges in enumerate(base.edge_coords(n=n)):  # [[(face_idx, r, c), (face_idx, r, c)],
            cubie_id = self.edges_perm[i]
            flip = self.edges_ori[i]

            perms = solved_edges[cubie_id]  # (12,2)
            actual_perms = np.roll(perms, flip)  # 翻转或不翻 flip 1 swap
            for pos, perm in zip(edges, actual_perms):
                stickers[pos] = perm

        assert np.array_equal(np.sort(stickers.flatten()), base.solved_idx.flatten())
        return stickers  # (6, n, n) 数组 .flatten().astype(np.float32)

    def is_solvable(self) -> bool:
        """
        Σ corner orientation ≡ 0 (mod 3)
        Σ edge_orientation ≡ 0 (mod 2)
        parity(corners_perm) == parity(edges_perm)
        不是任意贴纸顺序都能对应到 CubieState，必须保证这些约束
        两个角互换 parity 翻转
        角朝向改变 parity 不变
        两条 edge 内部翻转 parity 不变
        每个 corner 始终是 3 个不同 face
        每个 edge 始终是 2 个不同 face
        没有 sticker 被"拆散"或"拼错"
        """
        # 1. corner orientation
        if self.corners_ori.sum() % 3 != 0:  # 每行 Z3 求和，判断总约束
            return False

        # 2. edge orientation
        if self.edges_ori.sum() % 2 != 0:
            return False

        # 3. parity
        if self.edge_parity != self.corner_parity:
            return False

        return True

    @class_property('UD_SLICE_EDGES')
    def ud_slice_edges(cls) -> tuple:
        '''piece slice cubies（identity 集合),Cubie ID (4, 5, 6, 7)'''
        solved = cls.solved()
        return tuple(int(solved.edges_perm[pos]) for pos in CubeBase.SLICE_POSITIONS)

    @class_property('NON_SLICE_EDGES')
    def non_slice_edges(cls) -> tuple:
        '''非 slice cubie,Cubie ID [0, 1, 2, 3, 8, 9, 10, 11]'''
        solved = cls.solved()
        return tuple(int(solved.edges_perm[pos]) for pos in CubeBase.NON_SLICE_POSITIONS)

    @class_property('FIXED_SLICE_MEMBERSHIP_BASE')
    def fixed_slice_membership_base(cls) -> np.ndarray:
        """Phase 1.5 固定使用的 slice membership base"""
        base = np.arange(12, dtype=np.int8)  # identity

        for pos, piece in zip(CubeBase.SLICE_POSITIONS, sorted(cls.ud_slice_edges())):
            base[pos] = piece

        for pos, piece in zip(CubeBase.NON_SLICE_POSITIONS, sorted(cls.non_slice_edges())):
            base[pos] = piece

        assert np.array_equal(cls.solved().edges_perm, base)
        return base

    @class_property('SOLVED_UD')
    def solved_ud(cls) -> int:
        ''' UD-slice membership = solved'''
        return cls.encode_ud_slice(cls.solved().edges_perm.tolist())

    @class_property('SOLVED_CORNER_COSET')
    def solved_corner_coset(cls) -> int:  # 69
        return cls.encode_corner_coset(cls.solved().corners_perm.tolist())

    def is_phase1_solved(self) -> bool:
        """世界开始呈现出稳定对象结构（层 / 方向 / 对称)"""
        return (
                np.all(self.corners_ori == 0) and
                np.all(self.edges_ori == 0) and
                self.is_ud_slice_separated()
        )

    def is_ud_slice_separated(self) -> bool:
        """
        所有 UD-slice 边都不在 U/D 层 {4, 5, 6, 7}. slice 边在 中层, 只关心集合，不关心顺序
        引入一个先验区分：中层 vs 非中层
        then: self.ud_slice_coord == self.solved_ud: 69
        """
        return all(
            pos in CubeBase.SLICE_POSITIONS
            for pos, cubie in enumerate(self.edges_perm)
            if cubie in self.ud_slice_edges
        )

    def is_phase2_ready(self) -> bool:
        """Phase-1.5"""
        if not self.is_phase1_solved():
            return False
        return Phase15Coord.project(self).is_solved()

    def is_phase2_solved(self) -> bool:
        """
        Phase-2 goal:
        - corners_perm solved
        - edges_perm solved
        （ori 在 Phase-1 已保证为 0）
        """
        return (
                np.array_equal(self.corners_perm, np.arange(8)) and
                np.array_equal(self.edges_perm, np.arange(12))  # self.solved().edges_perm
        )

    def is_corner_solved(self) -> bool:
        return bool(np.all(self.corners_perm == np.arange(8)))

    @property
    def corner_parity(self):
        return CubeBase.permutation_parity(self.corners_perm)

    @property
    def edge_parity(self):
        return CubeBase.permutation_parity(self.edges_perm)

    @property
    def orientation_distance(self):
        """
        计算 orientation distance corner twist + edge flip
        但主要复杂度来自：permutation
        """
        d_corner = sum(abs(x) for x in self.corners_ori)
        d_edge = sum(abs(x) for x in self.edges_ori)
        return d_corner + d_edge  # *2

    @property
    def corner_ori_coord(self) -> int:
        """Z₃⁷ 8 个角，每个 Z₃ 自由度 = 7, 3^7 - 1 = 2186"""
        coord: int = 0
        for i in range(7):
            coord = coord * 3 + int(self.corners_ori[i])
        return coord

    @class_cache(key=lambda coord: coord)
    @staticmethod
    def decode_corner_ori(coord: int) -> np.ndarray:
        """
        coord ∈ [0, 3^7)
        返回 shape (8,) 的 corners_ori，满足 sum ≡ 0 (mod 3)
        diff = (out_ori - delta) % 3
        """
        ori = np.zeros(8, dtype=np.int8)

        s = 0
        for i in range(6, -1, -1):
            ori[i] = coord % 3
            s += ori[i]
            coord //= 3

        ori[7] = (-s) % 3
        return ori

    @property
    def edge_ori_coord(self) -> int:
        """Z₂¹¹ 12 个 edge，每个 Z₂ 自由度 = 11, 2^11 - 1 = 2047"""
        coord: int = 0
        for i in range(11):
            coord = (coord << 1) | int(self.edges_ori[i])
        return coord

    @class_cache(key=lambda coord: coord)
    @staticmethod
    def decode_edge_ori(coord: int) -> np.ndarray:
        """
        coord ∈ [0, 2^11)
        返回 shape (12,) 的 edges_ori，满足 sum ≡ 0 (mod 2)
        diff = (out_ori ^ delta)
        """
        ori = np.zeros(12, dtype=np.int8)

        s = 0
        for i in range(10, -1, -1):
            ori[i] = coord & 1
            s ^= ori[i]
            coord >>= 1

        ori[11] = s
        return ori

    @classmethod
    def encode_ud_slice(cls, edges_perm: list[int]) -> int:
        """
        从 12 个位置里选 4 个 C(12, 4) = 495
        UD-slice 组合坐标：只记哪些位置被 slice cubie 占据。
        encode_ud_slice 与 comb_to_index 同构，仅位序约定相反：
        (position 11 权重最高) ↔ comb_to_index(bit 0 权重最高)
        因此 bits = [1 if edges_perm[11-i] in ud_slice else 0 for i in range(12)]
        """
        bits = [0] * 12
        for i in range(12):
            if edges_perm[11 - i] in cls.ud_slice_edges():
                bits[i] = 1
        return CubeBase.comb_to_index(bits, n=12, k=4)

    @property
    def ud_slice_coord(self) -> int:
        """
        Phase-1: which 4 positions are occupied by slice edges
        哪些 edge cubie 在 slice positions（4,5,6,7）
        """
        return self.encode_ud_slice(self.edges_perm.tolist())

    @class_cache(key=lambda coord: coord)
    @classmethod
    def decode_ud_slice(cls, coord: int) -> np.ndarray:
        """
        根据 UD-slice 坐标 (0~494) 解码为 edges_perm。
        index_to_comb 与 decode_ud_slice 同构，位序约定相反。
        """
        bits = CubeBase.index_to_comb(coord, n=12, k=4)  # bits[i]=1 ←→ position 11-i 有 slice cubie
        positions = sorted(11 - i for i, b in enumerate(bits) if b)

        # canonical fill, identity is irrelevant
        slice_cubies = list(cls.ud_slice_edges())  # sorted slice cubies，按 solved 中的顺序填入(4, 5, 6, 7)
        non_slice = list(cls.non_slice_edges())
        it_slice = iter(slice_cubies)
        it_non = iter(non_slice)

        perm = np.zeros(12, dtype=np.int8)
        for pos in range(12):
            if pos in positions:
                perm[pos] = next(it_slice)
            else:
                perm[pos] = next(it_non)

        return perm

    @staticmethod
    def encode_perm_coord(edges_perm: list[int], positions: list[int],
                          cubies: list[int] | tuple[int]) -> int:
        """
        从完整的 edges_perm 中，提取指定位置 + 指定 cubie 子集 的相对置换坐标
        相对排列的坐标 (0 ~ len(cubies)! - 1)
        """
        cubie_to_rel = {cubie: i for i, cubie in enumerate(cubies)}  # 固定 cubie id

        # 提取当前状态下，在指定 positions 上出现的 cubie 的相对索引
        rel_indices = [cubie_to_rel[int(edges_perm[pos])] for pos in positions]
        return CubeBase.encode_perm(rel_indices)

    @staticmethod
    def encode_corner_coset(corners_perm: list[int]) -> int:
        # corner_coset（U 层是哪 4 个 corner）
        bits = [0] * 8
        for pos in CubeBase.U_CORNER_POSITIONS:  # 例如 [0,1,2,3]
            piece = int(corners_perm[pos])
            bits[piece] = 1

        return CubeBase.comb_to_index(bits, 8, 4)

    @class_cache(key=lambda corner_coset: corner_coset)
    @staticmethod
    def canonical_corner_coset(corner_coset: int) -> np.ndarray:
        """
        corner_coset ∈ [0, 70)
        canonical corner coset（只放层，不管层内排列） 基准点没对齐
        """
        corners_perm = np.zeros(8, dtype=np.int8)
        bits = CubeBase.index_to_comb(corner_coset, 8, 4)
        u_pieces = [i for i in range(8) if bits[i]]
        d_pieces = [i for i in range(8) if not bits[i]]
        # corner layer-membership 固定顺序（canonical）
        for pos, piece in zip(CubeBase.U_CORNER_POSITIONS, sorted(u_pieces)):
            corners_perm[pos] = piece

        for pos, piece in zip(CubeBase.D_CORNER_POSITIONS, sorted(d_pieces)):
            corners_perm[pos] = piece
        return corners_perm

    # @staticmethod
    # def ud_slice_positions(edges_perm: np.ndarray) -> list[int]:
    #     """
    #     UD slice edges 的当前位置 , 4 条边当前所在的位置
    #     """
    #     ud_slice_pos = []
    #     for target_id in CubieState.ud_slice_edges():  # UD slice 的 4 个目标位置索引
    #         pos = np.where(edges_perm == target_id)[0][0]  # 找到这个 edge id 当前在哪个位置
    #         ud_slice_pos.append(pos)
    #
    #     return sorted(ud_slice_pos)  # canonical: 排序，确保 canonical

    @staticmethod
    def encode_perm_ud_slice(edges_perm: list[int]) -> int:
        """
        UD-slice 内 4 个 edge 的排列,内部排列的 identity 编码->内部顺序
        Phase-1 已保证 membership 正确（即哪些 edge 在 slice 位置已固定），不检查
        返回 [0, 24) 只关心否等于 0（identity）
        encode_perm_coord(...,positions = SLICE_POSITIONS,
        cubies = sorted([edges_perm[p] for p in CubeBase.SLICE_POSITIONS])）
        """
        slice_edges = [edges_perm[pos] for pos in CubeBase.SLICE_POSITIONS]  # slice 中的 4 个位置（固定）
        rank = {piece: i for i, piece in enumerate(sorted(slice_edges))}
        rel_perm = [rank[piece] for piece in slice_edges]  # 构造 slice_perm 对应 canonical 编号
        return CubeBase.encode_perm(rel_perm)  # 0..23

    @class_cache(key=lambda ud_slice: ud_slice)
    @classmethod
    def create_ud_slice_perm(cls, ud_slice: int) -> np.ndarray:
        """
        生成一个 edges_perm，只改变 UD-slice 内部的排列，membership 保持固定（canonical）
        ud_slice_index: 0 ~ 23，表示 slice 内部的相对排列索引
        """
        edges_perm = cls.fixed_slice_membership_base.copy()  # 取一个固定的、正确的 slice membership（Phase 1 已保证的）
        slice_positions = CubeBase.SLICE_POSITIONS
        slice_pieces_sorted = sorted(edges_perm[pos] for pos in slice_positions)  # canonical 顺序

        # membership 固定 + slice 内排列 = i
        rel_perm = CubeBase.decode_perm(ud_slice, 4)  # 解码相对索引
        new_slice_pieces = [slice_pieces_sorted[j] for j in rel_perm]
        for pos, p in zip(slice_positions, new_slice_pieces):
            edges_perm[pos] = p

        return edges_perm


@dataclass(frozen=True)
class CubieMove:
    """
    perm_map: dict[int, np.ndarray]       # orbit_id -> σ
    ori_delta: dict[int, np.ndarray]      # orbit_id -> Δ (mod k)
    先验形式:群作用、生成元、右作用
    Permutation/Abelian Representation
    排列部分是交错群,方向部分是阿贝尔群
    """
    # permutation: new_pos = perm[old_pos]
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

    def square(self) -> "CubieMove":
        # m ∘ m
        return self.compose(self)

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
            if axis != 1:  # U/D 不变,不 twist,F/R/L/ B：正好 4 个角 ±1 / ±2
                a = (axis + 1) % 3
                b = (axis + 2) % 3
                for i in range(8):
                    if affected_corners[i]:
                        sign_a = np.sign(current_corner_pos[i, a])  # np.sign(corner_positions[i, a])
                        sign_b = np.sign(current_corner_pos[i, b])
                        # sign_axis = np.sign(corner_positions[i, axis])  # U / D 层的左右手系不一致
                        # corner 的朝向变化 = 局部右手系在旋转下的 twist,右手规则 + sign_dir 翻转 ccw 加负号是为了让顺时针90°对应 +2 或 -1
                        twist = (-sign_a * sign_b * sign_dir) % 3
                        corners_ori_delta[i] = (corners_ori_delta[i] + twist) % 3
                        # print(i, sign_a, sign_b, sign_dir, twist, sign_axis,side)

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

        # key = (axis, side, direction)
        # if key in [(0, -1, -1), (0, 1, 1), (2, 1, -1), (2, -1, 1)]:
        if axis != 1 and turns == 1:
            flip = (side == sign_dir) ^ (axis == 2)
            if flip:  # X 轴（R/L）和 Z 轴（F/B）的"朝向约定"不一致
                corners_ori_delta = (-corners_ori_delta) % 3
                # print('key',key,side*sign_dir,'flip')
                # then mv.inverse().is_primitive()

        return cls(
            corners_perm=corners_perm,
            corners_ori_delta=corners_ori_delta,
            edges_perm=edges_perm,
            edges_ori_delta=edges_ori_delta
        )

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
    def from_path(moves: list[tuple[tuple, 'QuotientMove']]) -> list['CubieMove']:
        """QuotientMove Action path"""
        return [m[1].cubie_move for m in moves]

    @classmethod
    def act_moves(cls, state: CubieState, moves: list['CubieMove']) -> tuple['CubieMove', 'CubieState']:
        '''state = M_n ∘ ... ∘ M_2 ∘ M_1 (state)'''
        mv = cls.identity()
        for m in moves:
            # current = m.act(current)
            mv = mv.compose(m)  # 右复合
        return mv, mv.act(state)

    @classmethod
    def apply(cls, state: CubieState, moves: list[tuple] | tuple) -> CubieState:
        '''状态级 API 等价 act_moves'''
        if not isinstance(moves, list):
            moves = [moves]
        for k in moves:
            # print(k, state)
            state = cls.prim_moves[k].act(state)  # cls.from_rotation(*k).act(state)
        return state

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

    @class_property('BASIC_PRIM_MOVES')
    def basic_generators(cls) -> list[tuple]:
        """所有 18 个基本 move（U D R L F B 的 ±90° 和 180°） 6 faces × {1,2,3} """
        moves = []
        for axis in (0, 1, 2):
            for side in (-1, +1):
                for direction in (-1, +1, +2):
                    moves.append((axis, side, direction))
        return moves  # face_id = move_id // 3 {k: i for i, k in enumerate(moves)}

    @class_cache('PRIM_MOVE_EMB', key=lambda move_id, n=3: (move_id, n))
    @classmethod
    def embedding(cls, move_id: int, n: int = 3) -> np.ndarray:
        k = cls.basic_generators[move_id]
        token = ActionToken.from_cubie_move(*k, n=n)
        return token.embedding(n=n)  # total 8 dim

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

    @class_property('INVERSE_INDICES')
    def inverse_indices(cls) -> list[int]:
        """返回 18 个基本 move 的逆元 index 映射: inverse_indices[i] = j ⇔ g_j = g_i⁻¹"""
        prim = cls.prim_moves()
        gen = cls.basic_generators()
        result = [-1] * len(gen)
        for i, k in enumerate(gen):
            inv = prim[k].inverse()
            for j, k2 in enumerate(gen):
                if inv == prim[k2]:
                    result[i] = j
                    break
        return result

    @class_cache('STICKER_MOVES', key=lambda n: n)
    @classmethod
    def sticker_moves(cls, n: int) -> dict[tuple, 'StickerMove']:
        all_moves = cls.prim_moves().copy()
        all_moves.update(cls.slice_moves())
        return {k: StickerMove.phi(n, m) for k, m in all_moves.items()}

    @class_property('PHASE0_MOVES')
    def phase0_moves(cls) -> dict[tuple, 'Phase0Action']:
        return {k: Phase0Action.phi(m) for k, m in cls.prim_moves.items()}

    @class_property('PHASE1_MOVES')
    def phase1_moves(cls) -> dict[tuple, 'Phase1Action']:
        return {k: Phase1Action.lift(p) for k, p in cls.phase0_moves.items()}

    @class_property('PHASE15_MOVES')
    def phase15_moves(cls) -> dict[tuple, 'Phase15Action']:
        """使用 G₁ move，但仅约束目标 coset，不限制 move 集，只限制目标: prim_moves /phase1_moves"""
        return {k: Phase15Action.phi(m) for k, m in cls.prim_moves.items()}

    @class_property('PHASE2_MOVES')
    def phase2_moves(cls) -> dict[tuple, 'Phase2Action']:
        '''⟨ U, D, L², R², F², B² ⟩ 10
        Phase2 的生成元应该在结构上"自洽闭合"
        '''
        moves: dict[tuple, CubieMove] = {}  # 去重
        for (axis, side, direction), m in cls.prim_moves.items():
            # if all(d == 0 for d in m.corners_ori_delta) and all(d == 0 for d in m.edges_ori_delta):
            # if m.inverse().is_primitive() # inverse 本身就应该在 primitive 集里
            if abs(side) != 1:  # 只允许外层
                continue
            if axis == 1:  # U / D 的 ±90°
                moves[(axis, side, direction)] = m
            elif direction == 2:  # X/Z 轴,R/L/F/B，只取 180°
                moves[(axis, side, direction)] = m
                # if direction == 1:  # 只生成一次，避免重复
                #     key = (axis, side, 2)
                #     moves[key] =  m.compose(m)  # 合并了对称的 180°

        return {k: Phase2Action.phi(m) for k, m in moves.items()}

    @property
    def edge_parity_delta(self) -> int:
        # edge permutation parity_effect 奇偶 0 or 1
        return CubeBase.permutation_parity(self.edges_perm)

    @property
    def orientation_distance(self):
        """
        计算 MOVE 的 orientation distance corner twist + edge flip
        但主要复杂度来自：permutation
        """
        d_corner = sum(abs(x) for x in self.corners_ori_delta)
        d_edge = sum(abs(x) for x in self.edges_ori_delta)
        return d_corner + d_edge

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

    @classmethod
    def relative_state(cls, s0: 'CubieState', s1: 'CubieState') -> 'CubieState':
        """
        计算 A 到 B （用相对状态 C = A^{-1} ∘ B) 转换到 solved 相对状态 基于群作用的相对变换
        g = solved ∘ g
        move = solved⁻¹ ∘ g = g
        s1 = s0 ∘ m
        """
        m = cls.build(s0, s1)
        return m.act(CubieState.solved())

    def re_act(self, s1: 'CubieState') -> 'CubieState':
        """还原初始状态 initial s0，s0 = m⁻¹ ∘ s1, s1 = s0 ∘ m"""
        return self.inverse().act(s1)

    @staticmethod
    def build_pruning_table(
            moves: list["QuotientMove"],  # Phase0Action|Phase1Action|Phase2Action
            apply_move: callable,  # (move, coord) -> new_coord
            start_coord: tuple | int = 0,  # solved 状态在该坐标下的编码,
            table_shape: tuple | int = 495,  # ud:495/40320, (3**7, 2**11)
    ) -> np.ndarray:
        """
        Phase 剪枝表构建函数
        |Q| = 3^7 × 2^11 × C(12,4) = 2,217,093,120

        参数:
            moves: List[Phase2Action]，所有允许的移动
            apply_move: callable，函数，签名: (move, current_coord) -> new_coord
                        Phase2 示例: 提取对应 perm_map 的函数
                                    lambda m, idx: m.corner_perm_map[idx]
                                    lambda m, idx: m.edge_perm_map[idx]
                        Phase1 示例:
                                lambda m, (co,eo): (m.corner_ori_map[co], m.edge_ori_map[eo])
                                lambda m, ud: m.ud_slice_map[ud]

            start_coord: int，solved 状态在该坐标下的索引
                (0, 0)
                encode_perm(list(range(8)))  # corner 0~7 顺序编码为 0
                encode_perm([NON_SLICE_EDGES.index(p) for p in NON_SLICE_EDGES]  # edge 相对排列 0~7
            table_shape:
                    表形状，用于 np.ndarray 分配
                     Phase2: 40320 或 495
                     Phase1: (2187, 2048) CO_EO_PRUNE 或 495
        返回:
            dist: np.ndarray(shape=(40320,), dtype=np.int8)，距离表，-1 表示不可达
        """
        dist = np.full(table_shape, -1, dtype=np.int8)
        dist[start_coord] = 0
        queue = deque([start_coord])

        while queue:
            cur = queue.popleft()
            d = dist[cur]

            for m in moves:
                nxt = apply_move(m, cur)  # 关键：使用传入的 map
                if dist[nxt] == -1:
                    dist[nxt] = d + 1
                    queue.append(nxt)

        return dist


@dataclass(frozen=True)
class QuotientMove:
    """
    一个群作用在 quotient 空间上的"元素,在该 Phase 下"有意义"的变化
    知性范畴的"合法作用",只有 符合范畴法则的变化 才是对象变化
    """
    cubie_move: CubieMove  # 仅用于 replay/debug，一个合法代表（保留） replay 得到真实 CubieState

    def act(self, coord):
        raise NotImplementedError

    def replay(self, cubie: CubieState) -> CubieState:
        """使用底层 cubie_move 重放路径，得到完整 CubieState  从 Phase 路径 replay 到真实状态"""
        return self.cubie_move.act(cubie)

    def token(self, n: int) -> ActionToken:
        return self.cubie_move.to_sticker_move(n)


@dataclass(frozen=True)
class Phase0Coord:
    """
    Full Cube State
    G/N ≅ (Z3^7 × Z2^11) quotient 空间
    物理层（不可违背）一个"只含守恒律"的物理世界,所有可达性约束的"物理底线"
    任何经验对象，必须服从这些先天一致性条件
    8! * 3^7 corners × 12! * 2^11 edges ≈ 4.3e19
    """
    corner_ori: int  # 0 .. 3^7 - 1
    edge_ori: int  # 0 .. 2^11 - 1

    @property
    def key(self) -> tuple:
        """CosetID"""
        return self.corner_ori, self.edge_ori

    @classmethod
    def project(cls, s: CubieState) -> 'Phase0Coord':
        """from_cubie,投影到 Phase-1 坐标空间"""
        return cls(
            corner_ori=s.corner_ori_coord,
            edge_ori=s.edge_ori_coord,
        )

    def __hash__(self):
        return hash(self.key)

    def __str__(self) -> str:
        return f"({self.key})"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.corner_ori == other.corner_ori and self.edge_ori == other.edge_ori

    @classmethod
    def solved(cls) -> "Phase0Coord":
        return cls(0, 0)

    def is_solved(self) -> bool:
        return self.corner_ori == 0 and self.edge_ori == 0

    def heuristic(self) -> int:
        '''
        weak heuristic pruning table：CO × EO
        '''
        co_bits = CubieState.decode_corner_ori(self.corner_ori)  # list of 7 ints 0~2
        eo_bits = CubieState.decode_edge_ori(self.edge_ori)  # list of 11 ints 0~1

        corner_h = np.count_nonzero(co_bits)
        edge_h = np.count_nonzero(eo_bits)

        return max(corner_h, edge_h)


@dataclass(frozen=True)
class Phase0Action(QuotientMove):
    """Phase0Action ⊂ End(Phase0Coord) 群作用的投影"""
    corner_ori_map: np.ndarray  # shape (3^7,), permutation of 0..6
    edge_ori_map: np.ndarray  # shape (2^11,), permutation of 0..10
    cubie_move: CubieMove  # 一个合法代表（保留）

    def act(self, c: Phase0Coord) -> Phase0Coord:
        return Phase0Coord(
            corner_ori=int(self.corner_ori_map[c.corner_ori]),
            edge_ori=int(self.edge_ori_map[c.edge_ori])
        )

    @classmethod
    def phi(cls, m: CubieMove) -> "Phase0Action":
        solved = CubieState.solved()
        corner_map = np.zeros(3 ** 7, np.int32)
        # -------- corner ori map --------
        for i in range(3 ** 7):
            s = solved.with_(corners_ori=CubieState.decode_corner_ori(i))
            corner_map[i] = m.act(s).corner_ori_coord  # 必须保证完全遵循群规则
        # -------- edge ori map --------
        edge_map = np.zeros(2 ** 11, np.int32)
        for i in range(2 ** 11):
            s = solved.with_(edges_ori=CubieState.decode_edge_ori(i))
            edge_map[i] = m.act(s).edge_ori_coord

        return cls(
            corner_ori_map=corner_map,
            edge_ori_map=edge_map,
            cubie_move=m
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
                np.array_equal(self.corner_ori_map, other.corner_ori_map)
                and np.array_equal(self.edge_ori_map, other.edge_ori_map)
        )


@dataclass(frozen=True)
class Phase1Coord:
    """
    保证方向正确 + slice 边在中层,可经验对象化
    Orientation & UD membership solved
    -> corners = 8! edges = 12! / 495
    剩下 permutation 自由度:
    8! * 12!/495 ≈ 40320 * 967680 ≈ 3.9e10
    """
    corner_ori: int  # 0 .. 3^7 - 1
    edge_ori: int  # 0 .. 2^11 - 1

    ud_slice: int  # 0..494,来自 m.act(SOLVED) 在组合空间的像,区分工程 Kociemba/群论 quotient

    @classmethod
    def project(cls, s: CubieState) -> 'Phase1Coord':
        """from_cubie,投影到 Phase-1 坐标空间"""
        return cls(
            corner_ori=s.corner_ori_coord,
            edge_ori=s.edge_ori_coord,
            ud_slice=s.ud_slice_coord,
        )

    @classmethod
    def solved(cls) -> "Phase1Coord":
        return cls(corner_ori=0, edge_ori=0, ud_slice=CubieState.solved_ud)  # 69

    def is_solved(self) -> bool:
        '''
        is_phase1_solved: coord.co == 0 and coord.eo == 0
        UD-slice membership = 0  注意：不是 quotient，只是 goal 条件
        Phase-1 只解决"进入 G₁"，不解决"进入 solved coset"
        coord 版不检查 slice separation,slice separation 已经体现在 allowed move set + heuristic 中
        '''
        return self.corner_ori == 0 and self.edge_ori == 0 and self.ud_slice == CubieState.solved_ud

    @property
    def key(self) -> tuple:
        return self.corner_ori, self.edge_ori, self.ud_slice

    @property
    def label(self) -> str:
        co, eo, uds = self.key
        return f"CO{co}|EO{eo}|UD{uds}"

    def __hash__(self):
        return hash(self.key)

    def __str__(self) -> str:
        return f"({self.key})"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.corner_ori == other.corner_ori and self.edge_ori == other.edge_ori and self.ud_slice == other.ud_slice

    def apply(self, m: "Phase1Action") -> "Phase1Coord":
        return m.act(self)


@dataclass(frozen=True)
class Phase1Action(Phase0Action):
    """
    Phase-1 坐标映射：把 CubieMove 投影到 Phase-1 子空间（CO × EO × UD-slice membership）
    满足：π(s ∘ m) = π(s) ∘ φ(m)   （右作用语义）
    φ : CubieMove → Phase1Action 是同态映射
    用于 pruning table 生成和 IDA*/BFS 中的坐标转移
    """
    # UD-slice membership 的组合置换
    # 作用在 C(12,4) 编码空间上,并不存在一个与 EP 无关的、真正的函数
    ud_slice_map: np.ndarray  # shape (495,), permutation of 0..494

    def act(self, c: Phase1Coord) -> Phase1Coord:
        """
        Phase1Action.act 只作为"坐标映射"，不作为群作用,整数置换,只计算 CO, EO, UD 的变化
        此方法仅用于坐标投影，不是 cubie 层面的群作用
        """
        return Phase1Coord(
            corner_ori=int(self.corner_ori_map[c.corner_ori]),  # apply_corner_ori
            edge_ori=int(self.edge_ori_map[c.edge_ori]),  # apply_edge_ori
            ud_slice=int(self.ud_slice_map[c.ud_slice]),  # state.ud_slice_coord
        )

    def compose(self, other: "Phase1Action") -> "Phase1Action":
        """
        坐标映射右作用复合：self ∘ other  先应用 other（右边），再应用 self（左边）
        (self ∘ other).act(c) = self.act(other.act(c))
        """
        return Phase1Action(
            corner_ori_map=self.corner_ori_map[other.corner_ori_map],
            edge_ori_map=self.edge_ori_map[other.edge_ori_map],
            ud_slice_map=self.ud_slice_map[other.ud_slice_map],
            cubie_move=self.cubie_move.compose(other.cubie_move)  # 为了 replay / debug
        )

    @classmethod
    def lift(cls, p0: Phase0Action) -> "Phase1Action":
        m = p0.cubie_move
        solved = CubieState.solved()
        # -------- ud slice map --------
        # 构造一个"只有 slice membership 不同"的状态,只要求"slice 成员正确"， 不要求 slice 内部的排列是对的,依赖 edge permutation 的操作
        slice_map = np.zeros(495, dtype=np.int16)
        for coord in range(495):
            s = solved.with_(edges_perm=CubieState.decode_ud_slice(coord))
            # assert s.ud_slice_coord == coord < 495
            out = m.act(s)
            slice_map[coord] = out.ud_slice_coord

        return cls(
            corner_ori_map=p0.corner_ori_map,
            edge_ori_map=p0.edge_ori_map,
            ud_slice_map=slice_map,
            cubie_move=m
        )

    @classmethod
    def phi(cls, m: CubieMove) -> "Phase1Action":
        """
        从底层 CubieMove 生成 Phase-1 坐标映射
        保证：对于任意 s，φ(m).act(π(s)) == π(m.act(s))
        """
        return cls.lift(Phase0Action.phi(m))


@dataclass(frozen=True)
class Phase2Coord:
    """处理角块、非 slice 边、slice 内部排列
    Invariants:
    - corner_ori = 0
    - edge_ori = 0
    - UD-slice membership fixed
    - corner parity = edge parity (guaranteed by Phase-1.75)

    Components:
    - corner_perm ∈ A8 (8! / 2)
    - edge_perm ∈ S8 (non-slice edges)
    - ud_slice_perm ∈ S4
    """
    corner_perm: int  # 0 .. 40319 (8! / 2, 去掉整体 parity)
    edge_perm: int  # 0 .. 40319 (8! 只取非-slice edges 8 条)
    ud_slice_perm: int  # 0 .. 23  (4!) 局部自由度,坐标维度

    @classmethod
    def project(cls, s: CubieState) -> "Phase2Coord":
        """
        必须假设 s ∈ G₁ s.is_phase1_solved,Phase-2 只在 G₁ 内搜索
        使用的是 降维后的坐标群
        """
        assert s.is_phase1_solved(), f'phase1 not solved:{s}'

        corner_idx = CubeBase.encode_perm(s.corners_perm.tolist())

        # 非 slice 边：相对排列
        edge_idx = CubieState.encode_perm_coord(s.edges_perm.tolist(),
                                                positions=CubeBase.NON_SLICE_POSITIONS,
                                                cubies=CubieState.non_slice_edges())

        ud_idx = CubieState.encode_perm_coord(s.edges_perm.tolist(),
                                              positions=CubeBase.SLICE_POSITIONS,
                                              cubies=CubieState.ud_slice_edges())

        return cls(corner_idx, edge_idx, ud_idx)

    def is_solved(self) -> bool:
        """角块排列复原.非 slice 边排列复原,slice 边排列复原"""
        return self.corner_perm == 0 and self.edge_perm == 0 and self.ud_slice_perm == 0

    @classmethod
    def solved(cls) -> "Phase2Coord":
        return cls(0, 0, 0)

    @property
    def key(self) -> tuple:
        return self.corner_perm, self.edge_perm, self.ud_slice_perm

    def __hash__(self):
        return hash(self.key)

    def __str__(self) -> str:
        return f"({self.key})"

    def apply(self, m: "Phase2Action") -> "Phase2Coord":
        return m.act(self)

    def heuristic(self) -> int:
        # decode corner/edge/ud-slice permutation
        corners = CubeBase.decode_perm(self.corner_perm, 8)
        edges = CubeBase.decode_perm(self.edge_perm, 8)
        ud_edges = CubeBase.decode_perm(self.ud_slice_perm, 4)

        # 保守估计：统计不在原位的数量
        h_corners = sum(1 for i, c in enumerate(corners) if c != i)
        h_edges = sum(1 for i, e in enumerate(edges) if e != i)
        h_ud = sum(1 for i, u in enumerate(ud_edges) if u != i)

        # Phase2 中最少需要的 move 至少等于最大的错位数
        return max(h_corners, h_edges, h_ud)


@dataclass(frozen=True)
class Phase2Action(QuotientMove):
    corner_perm_map: np.ndarray  # shape (40320,)
    edge_perm_map: np.ndarray  # shape (40320,)
    ud_slice_perm_map: np.ndarray  # shape (24,)

    def act(self, c: Phase2Coord) -> Phase2Coord:
        """DFS 用, m ⋅ s """
        return Phase2Coord(
            corner_perm=int(self.corner_perm_map[c.corner_perm]),
            edge_perm=int(self.edge_perm_map[c.edge_perm]),
            ud_slice_perm=int(self.ud_slice_perm_map[c.ud_slice_perm]),
        )

    def compose(self, other: "Phase2Action") -> "Phase2Action":
        """
        self ∘ other
        """
        return Phase2Action(
            corner_perm_map=self.corner_perm_map[other.corner_perm_map],
            edge_perm_map=self.edge_perm_map[other.edge_perm_map],
            ud_slice_perm_map=self.ud_slice_perm_map[other.ud_slice_perm_map],
            cubie_move=self.cubie_move.compose(other.cubie_move),
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
                np.array_equal(self.corner_perm_map, other.corner_perm_map)
                and np.array_equal(self.edge_perm_map, other.edge_perm_map)
            # and np.array_equal(self.ud_slice_perm_map, other.ud_slice_perm_map)
        )

    @classmethod
    def phi(cls, m: CubieMove) -> "Phase2Action":
        """
        直接从 CubieMove 诱导,坐标转换
        G₂ = ⟨U, D, R², L², F², B²⟩
        """
        solved = CubieState.solved()

        def induce_corner_perm_map() -> np.ndarray:
            """诱导角块置换表 (8! = 40320)"""
            size = math.factorial(8)  # 40320
            perm_map = np.zeros(size, dtype=np.int32)

            for idx in range(size):
                # decode 成 corner permutation
                rel_perm = CubeBase.decode_perm(idx, 8)  # 0~7
                corner_perm = np.array(rel_perm, dtype=np.int8)  # shape (8,) 直接就是 cubie id
                s = solved.with_(corners_perm=corner_perm)
                out = m.act(s)
                perm_map[idx] = CubeBase.encode_perm(out.corners_perm.tolist())  # perm8: shape (8,), values 0..7

            return perm_map

        def induce_edge_perm_map(positions: list[int], cubies: list[int] | tuple[int]) -> np.ndarray:
            """
            诱导边块子置换表（非 slice 8! 或 slice 4!）  8! = 40320
            cubies 编号集合（piece space）NON_SLICE_EDGES/UD_SLICE_EDGES
            """
            n = len(positions)
            size = math.factorial(n)  # 40320/24
            # assert n == len(cubies) and factorial(n) == size
            perm_map = np.zeros(size, dtype=np.int32 if n == 8 else np.int8)
            cubie_to_rel = {cubie: i for i, cubie in enumerate(cubies)}

            for idx in range(size):
                rel_perm = CubeBase.decode_perm(idx, n)  # 0 ~ n-1,0..7/0..3
                actual = [cubies[i] for i in rel_perm]  # perm8/perm4,真实 cubie id,values in cubies
                # 嵌回到 solved 的完整状态
                new_edges_perm = solved.edges_perm.copy()
                for pos, cubie in zip(positions, actual):  # slice 保持 solved 顺序
                    new_edges_perm[pos] = cubie

                out = m.act(solved.with_(edges_perm=new_edges_perm))

                out_rel = [cubie_to_rel[int(out.edges_perm[p])] for p in positions]  # -> 0..7/ 0..3, 长度 8,
                perm_map[idx] = CubeBase.encode_perm(out_rel)

            return perm_map

        # 三个坐标分别调用
        corner_perm_map = induce_corner_perm_map()
        edge_perm_map = induce_edge_perm_map(positions=CubeBase.NON_SLICE_POSITIONS,
                                             cubies=CubieState.non_slice_edges())
        ud_slice_perm_map = induce_edge_perm_map(positions=CubeBase.SLICE_POSITIONS,
                                                 cubies=CubieState.ud_slice_edges())

        return cls(
            corner_perm_map=corner_perm_map,
            edge_perm_map=edge_perm_map,
            ud_slice_perm_map=ud_slice_perm_map,
            cubie_move=m
        )


@dataclass(frozen=True)
class Phase15Coord:
    """
    Phase-1.5 quotient 坐标,对象如何在先天结构中被规定,表达结构,是 稳定结构的纯净子集
    范畴是抽象的，直观是具体的,二者之间，必须有"图式"（Schema）
    在 G / H₁ 的基础上，再 quotient 一个 H₂ ⊂ H₁
    约定：仅在 Phase-1 已满足时调用,投影到 G₂ 可达 coset
    Phase1 已经 quotient 掉 orientation 与 slice membership。
    Phase1.5 再 quotient 掉 slice 内排列与角块内部排列，只保留 coset 与 edge parity
    在不限制 move 集的情况下，仅通过目标约束，把状态推进到 Phase-2 可达子空间
    状态空间大小 4! × 70 × 2 = 560 状态,压缩状态,纯净的因果子空间 → Δpotential
    不可违背的先验法则（群论）,可涌现的经验规律（策略、启发）,看张力、稳定结构和涌现模式

    对称性破缺（Symmetry Breaking）
    魔方世界有极强对称性：面对称/颜色置换/全局旋转等价
    但有效策略一定会破坏对称性。弱锚定:引入一个"reference frame observable",当前 entropy 最小的面 = reference
    具体映射：

    State space
    = G / (Ori × SliceMembership)
    = 纯 coset + parity

    quotient 坐标不是正规子群商，所以不存在真正群同态坐标，同一个坐标可能对应两个真实群轨道。
    整体群要求：corner_parity=edge_parity  slice_parity:internal_permutation_parity

    Move set = 原群生成元（不裁剪）
    Goal = 收缩到 Phase-2 子群
    Prune table = exact distance to target subgroup（admissible）
    Critic / heuristic = potential gradient 的 noisy proxy
    3360 = 7! / 15
    """
    slice_perm: int  # UD-slice 内 4 条 edge 的排列 4! = 24 slice_perm ∈ [0,24) critic label
    corner_coset: int  # U/D 层 corner membership quotient 掉 U-layer + D-layer 内部的排列 8! / (4!·4!) = C(8,4)  ∈ [0,70)
    parity: int  # Z2 守恒 0 / 1,来自真实 edge_parity,edge_parity' = edge_parity XOR Δ(m) / edge_parity XOR corner_parity

    @property
    def index(self) -> int:
        """index=slice∗70∗2+corner∗2+parity 只存索引，丢失一半的连通性"""
        N_CORNER = 70
        return ((self.slice_perm * N_CORNER + self.corner_coset) << 1) | self.parity

    @classmethod
    def from_index(cls, i: int) -> "Phase15Coord":
        N_CORNER = 70
        parity = i & 1
        i >>= 1
        corner_coset = i % N_CORNER
        slice_perm = i // N_CORNER
        return cls(slice_perm=slice_perm, corner_coset=corner_coset, parity=parity)

    @property
    def key(self) -> tuple:
        """
        CosetID
          slice_perm UD-slice 内部 4 条边的排列 返回值: 0..23
        """
        return self.slice_perm, self.corner_coset, self.parity

    def __hash__(self):
        return hash(self.key)

    @classmethod
    def project(cls, s: CubieState) -> "Phase15Coord":
        """ encode 状态空间裁剪  在 Phase-2 中，corner parity 与 edge parity 必须匹配,
        必须通过真实状态回溯（cubie Lift）来维持结构的正确性
        """
        # 1. slice_perm（Phase1 已保证 membership）
        slice_perm = CubieState.encode_perm_ud_slice(s.edges_perm.tolist())  # 0..23
        # 2. corner_coset（U 层是哪 4 个 corner）
        corner_coset = CubieState.encode_corner_coset(s.corners_perm.tolist())
        # 3. edge parity
        edge_parity = s.edge_parity  # 0/1,s.edge_parity ^ s.corner_parity==0

        return cls(
            slice_perm=slice_perm,
            corner_coset=corner_coset,
            parity=edge_parity
        )

    @classmethod
    def solved(cls) -> "Phase15Coord":
        return cls(0, CubieState.solved_corner_coset, 0)  # 69

    def is_solved(self) -> bool:
        return self.slice_perm == 0 and self.corner_coset == CubieState.solved_corner_coset and self.parity == 0

    def embedding(self) -> np.ndarray:
        """群的商空间指示函数,返回神经网络输入向量 95 维 one-hot,
        商群指标表示,为了搜索/压缩设计的,不是为了表示群结构设计的"""
        # 简单 one-hot style embedding
        slice_vec = np.zeros(24, dtype=np.float32)
        slice_vec[self.slice_perm % 24] = 1.0
        corner_vec = np.zeros(70, dtype=np.float32)
        corner_vec[self.corner_coset % 70] = 1.0
        parity_vec = np.array([self.parity], dtype=np.float32)
        return np.concatenate([slice_vec, corner_vec, parity_vec])

    def observables(self) -> np.ndarray:
        """
        任何被 world model 预测的量，必须满足：
        它的变化对可达性是单调相关的。
        """
        # slice misplaced count
        slice_edges = CubeBase.decode_perm(self.slice_perm, 4)
        h_slice = sum(1 for i, p in enumerate(slice_edges) if p != i)

        # corner coset misplaced（canonical）
        corner_perm = CubieState.canonical_corner_coset(self.corner_coset)
        solved = CubieState.canonical_corner_coset(CubieState.solved_corner_coset)
        h_corner = int(np.sum(corner_perm != solved))  # float(self.corner_coset) / 69.0

        parity = float(self.parity)

        return np.array([
            h_slice,  # 0..4
            h_corner,  # 0..8
            parity,
            h_slice + h_corner,
            max(h_slice, h_corner),
        ], dtype=np.float32)  # 5 维

    def heuristic(self) -> float:
        """
        Phase-1.5 ranking critic heuristic(coord) ≈ dist(coord, solved)
        加权版 越小越好
        """
        obs = self.observables()
        h_slice, h_corner, parity = obs[:3]
        return max(h_slice, 0.5 * h_corner, 0.5 * parity)

    def decode(self, start: CubieState = None) -> CubieState:
        """
         canonical representative
         仅用于 φ 构造 不用于搜索 replay,搜索过程中 从不调用 decode 再 project
        """
        if start is None:
            start = CubieState.solved()
        # 1. slice_perm：固定 membership + slice_perm 排列
        # 2. corner_coset（只放层，不管层内排列）
        s = start.with_(edges_perm=CubieState.create_ud_slice_perm(self.slice_perm),
                        corners_perm=CubieState.canonical_corner_coset(self.corner_coset))
        # # parity fix
        # if s.edge_parity != self.parity:
        #     ep = s.edges_perm
        #     # swap two slice edges
        #     ep[4], ep[5] = ep[5], ep[4]
        #     s = s.with_(edges_perm=ep)

        # 3. edge parity,flip
        if s.edge_parity != self.parity:  # decode 出来的状态，其 parity 必须天然一致
            raise AssertionError("Illegal Phase15Coord: parity mismatch")
        assert s.edge_parity ^ s.corner_parity == 0, "Invalid state: parity mismatch"
        assert Phase15Coord.project(s) == self
        return s


@dataclass(frozen=True)
class Phase15Action(QuotientMove):
    """
    Phase-1.5 商空间上的作用投影。

    关键约束：Phase15Coord 的商不是正规子群商，slice_perm 与 corner_coset
    在 90° 外层动作下存在耦合（一个 move 对 corner_coset 的影响依赖于当前
    slice_perm，反之亦然）。因此不存在纯坐标到坐标的群同态映射 act_index()，
    只能通过 act(state) 走真实 CubieState 再 project。

    用法：
        state, coord = phase15_action.act(cubie_state)
        # coord 是 project 后的 Phase15Coord，state 是真实的 CubieState
    """
    cubie_move: CubieMove

    def act(self, s: CubieState) -> tuple[CubieState, Phase15Coord]:
        """真实 CubieMove 作用 → project 回 Phase15Coord"""
        state = self.replay(s)
        coord = Phase15Coord.project(state)
        return state, coord

    @classmethod
    def phi(cls, m: CubieMove) -> "Phase15Action":
        """从 CubieMove 构造 Phase15Action"""
        return cls(cubie_move=m)


class StickerMove:
    def __init__(self, perm: np.ndarray, cubie_move: CubieMove = None):
        """对 sticker index 的一维置换"""
        self.perm = perm.astype(np.int32)  # 一维贴纸置换
        self.cubie_move: CubieMove = cubie_move or CubieMove.identity()

    @classmethod
    def identity(cls, n: int) -> "StickerMove":
        return cls(perm=np.arange(6 * n * n, dtype=np.int32))

    def act(self, state: np.ndarray) -> np.ndarray:
        """右作用：new[i] = old[perm[i]] new_state[i] = old_state[perm[i]]"""
        flat = state.reshape(-1)  # sticker state/id
        return flat[self.perm].reshape(state.shape)

    def apply(self, s: StickerCube | np.ndarray) -> StickerCube:
        arr = s if isinstance(s, np.ndarray) else s.get_state()
        return StickerCube(state=self.act(arr), n=arr.shape[1])

    def replay(self, cubie: CubieState, n: int = 3) -> tuple[CubieState, np.ndarray]:
        """等价于 act"""
        arr = cubie.to_sticker()  # base.from_cubie(cubie)
        state = self.act(arr)
        cubie = self.cubie_move.act(cubie)  # some move 没映射
        state1 = (state // (n * n)).astype(np.uint8)
        cubie1 = CubieBase(n).to_cubie(state1)  # project from arr
        assert cubie == cubie1
        return cubie, state

    @classmethod
    def act_moves(cls, state: np.ndarray, moves: list['ActionToken']) -> tuple['StickerMove', np.ndarray]:
        '''
        replay_cubie_moves,CubieMove → StickerMove → compose → act
        state' = state ∘ m1 ∘ m2 ∘ ... ∘ mn
        '''
        n = state.shape[1]
        sticker_moves = CubieMove.sticker_moves(n=n)
        sm = cls.identity(n)
        for t in moves:
            k = t.to_cubie_move(n)
            if k is not None and k in sticker_moves:
                m = sticker_moves[k]
            else:
                m = cls.from_rotation(n, t)
            sm = sm.compose(m)
        return sm, sm.act(state)

    @classmethod
    def phi(cls, n: int, m: CubieMove) -> "StickerMove":
        """
         把 CubieMove 转换为 perm 供 StickerMove, CubieMove → StickerMove。
         new_sticker[i] = old_sticker[perm[i]]   （右作用）
        """
        token = m.to_sticker_move(n)
        assert token is not None, 'not prim move,composed!'
        sm = cls.from_rotation(n, token)
        sm.cubie_move = m
        return sm

    @class_cache('ROT_CACHE', key=lambda n, token: (n, token.key))
    @classmethod
    def from_rotation(cls, n: int, token: ActionToken) -> "StickerMove":
        """
        CubieMove ⊂ StickerMove
        perm[i] = j  表示 new_flat[i] = old_flat[j]
        perm[i] = j 表示 i 号贴纸 → j 号位置
        """
        state_idx = np.arange(6 * n * n, dtype=np.int32).reshape(6, n, n)
        CubeBase.rotate_core(state_idx, token.axis, token.layer, token.direction)
        return cls(perm=state_idx.reshape(-1))  # rotated flatten np.argsort

    @property
    def N(self) -> int:
        L = self.perm.shape[0]
        n_float = np.sqrt(L / 6)
        if not n_float.is_integer():
            raise ValueError(f"Length {L} is not divisible by 6 or not a perfect square")
        return int(n_float)

    def center_perm(self) -> np.ndarray:
        """
           返回一维 center_perm：
           index = center sticker 全局编号
           value = 被 move 后送来的 sticker 编号
        """
        n = self.N
        state_idx = self.perm.reshape(6, n, n)
        centers = CubeBase.get_center_rings(n)

        flat = []
        for fidx, rings in enumerate(centers):
            for ring in rings:
                for r, c, _ in ring:
                    flat.append(state_idx[fidx, r, c])
        return np.array(flat, dtype=np.int32)

    def __eq__(self, other):
        if not isinstance(other, StickerMove):
            return NotImplemented
        return np.array_equal(self.perm, other.perm)

    def is_solved(self) -> bool:
        n = self.N
        solved = np.zeros((6, n, n), dtype=np.uint8)
        for f in range(6):
            solved[f, :, :] = f
        return bool(np.array_equal(self.state(), solved))

    def state(self) -> np.ndarray:
        """颜色视图"""
        n = self.N
        state_idx = self.perm.reshape(6, n, n)
        return (state_idx // (n * n)).astype(np.uint8)

    def embedding(self) -> np.ndarray:
        """MLP, n 变化（比如同时训练 3×3，甚至 7×7），网络就很难学到一致的模式 absolute index relative color+uv"""
        n = self.N
        state_idx = self.perm.reshape(6, n, n)
        # (state_idx // (n * n)).astype(float) + (state_idx % (n * n)).astype(float) / (n * n)
        return state_idx.astype(float) / (n * n)

    def inverse(self) -> "StickerMove":
        inv = np.empty_like(self.perm)
        inv[self.perm] = np.arange(len(self.perm))
        return StickerMove(perm=inv, cubie_move=self.cubie_move.inverse())

    def compose(self, other: "StickerMove") -> "StickerMove":
        # self ∘ other,先 other，再 self
        return StickerMove(perm=self.perm[other.perm], cubie_move=self.cubie_move.compose(other.cubie_move))

    @classmethod
    def build(cls, state_idx_t: np.ndarray, state_idx_t1: np.ndarray) -> "StickerMove":
        """从 state0 到 state1 的置换合成 from delta 相对变化"""
        perm0 = state_idx_t.ravel()  # .reshape(-1)
        perm1 = state_idx_t1.ravel()

        # 用 numpy 的索引技巧直接完成置换合成
        inv_idx0 = np.argsort(perm0)  # O(n log n)
        move_perm = inv_idx0[perm1]  # O(n) 向量化索引
        assert np.array_equal(np.sort(move_perm), np.arange(len(perm0)))

        n = state_idx_t.shape[1]
        state0 = (state_idx_t // (n * n)).astype(np.uint8)
        state1 = (state_idx_t1 // (n * n)).astype(np.uint8)
        base = CubieBase(n)
        mv = CubieMove.build(s0=base.to_cubie(state0), s1=base.to_cubie(state1))
        assert mv.edges_ori_delta.sum() % 2 == 0
        assert mv.corners_ori_delta.sum() % 3 == 0
        return cls(perm=move_perm, cubie_move=mv)


class CubieExample:
    @staticmethod
    def twisted():
        """10 + 15"""
        co = np.arange(8, dtype=np.int8) % 3
        co[-1] = (-np.sum(co[:-1])) % 3
        eo = np.arange(12, dtype=np.int8) % 2
        eo[-1] = (-np.sum(eo[:-1])) % 2
        return CubieState.solved().with_(corners_ori=co, edges_ori=eo)

    @staticmethod
    def big_cycle():
        """9 + 11"""
        cp = np.roll(np.arange(8, dtype=np.int8), 4)  # 4-cycle corners
        ep = np.roll(np.arange(12, dtype=np.int8), 6)  # 6-cycle edges
        return CubieState.solved().with_(corners_perm=cp, edges_perm=ep)

    @staticmethod
    def inversed():
        """已知20步的极端置换 extreme reverse 0 + 11"""
        cp = np.arange(8, dtype=np.int8)[::-1]  # 角块完全反序
        ep = np.arange(12, dtype=np.int8)[::-1]
        return CubieState.solved().with_(corners_perm=cp, edges_perm=ep)

    @staticmethod
    def checkerboard():
        """棋盘格，较难 9+13
        [0, 3, 1, 2, 4, 7, 5, 6] [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10]
        """
        cp = np.array([6, 7, 4, 5, 2, 3, 0, 1], dtype=np.int8)
        ep = np.array([6, 7, 4, 5, 2, 3, 0, 1, 10, 11, 8, 9], dtype=np.int8)
        return CubieState.solved().with_(corners_perm=cp, edges_perm=ep)

    @staticmethod
    def superflip():
        eo = np.ones(12, dtype=np.int8)  # 所有边全部翻转,20步理论最优
        return CubieState.solved().with_(edges_ori=eo)

    @staticmethod
    def superflip_plus():
        """Superflip + corners twisted（经典 20步）9+13"""
        co = np.array([1, 1, 1, 0, 0, 0, 0, 0], dtype=np.int8)  # 两个角各扭1
        eo = np.ones(12, dtype=np.int8)  # 所有边翻转
        return CubieState.solved().with_(corners_ori=co, edges_ori=eo)


class CycleLibrary:
    """
    合法群元素的组合模板,构造一个群元素，它在贴纸表示下呈现为 cycle
    """

    @staticmethod
    def verify_cycle(state: np.ndarray, moves: list):
        """
        sticker 3-cycle → 3 或 6 :assert verify_cycle(cube0, cycle) in (3, 6)
        edge 3-cycle → 6（3 条边 × 2 贴纸）
        corner 3-cycle → 9（3 × 3）
        """
        arr = state.copy()
        CubeBase.act_moves(arr, moves)
        diff = np.where(arr != state)
        return len(diff[0])  # np.sum(arr != state)

    @staticmethod
    def sticker_3cycle_base():
        """
        一个已知稳定的贴纸 3-cycle（固定位置）
        支撑很小，parity 合法
        """
        A = [(0, +1, 1)]  # R
        B = [(1, +1, 1)]  # U
        return ActionToken.commutator(A, B)

    @staticmethod
    def edge_3cycle_base():
        """
        3 条边的循环，不翻转方向
        """
        A = [(0, +1, 1)]  # R
        B = [(2, +1, 1)]  # F
        return ActionToken.commutator(A, B)

    @staticmethod
    def corner_3cycle_base():
        """
        3 个角块的循环，不扭转
        """
        A = [(0, +1, 1)]  # R
        B = [(1, +1, 1)]  # U
        C = [(0, +1, -1)]  # R'
        return ActionToken.commutator(A, ActionToken.commutator(B, C))

    @staticmethod
    def sticker_3cycle(position_moves: list):
        base = CycleLibrary.sticker_3cycle_base()
        return ActionToken.at(position_moves, base)

    @staticmethod
    def edge_3cycle(position_moves: list):
        base = CycleLibrary.edge_3cycle_base()
        return ActionToken.at(position_moves, base)

    @staticmethod
    def corner_3cycle(position_moves: list):
        base = CycleLibrary.corner_3cycle_base()
        return ActionToken.at(position_moves, base)


class CubieBase(CubeBase):
    """群论态（搜索）"""
    AXIS_NAME = ('X', 'Y', 'Z')
    SOLVED_STATE = CubieState.solved()

    def __init__(self, n: int = 3):
        super().__init__(n)
        self.CORNER_REF_AXIS = self.build_corner_reference_axis()
        self.EDGE_REF_AXIS = self.build_edge_reference_axis()
        # assert np.all(self.corner_orientation(self.solved) == 0) ,self.corner_orientation(self.solved)

    def to_cubie(self, state: np.ndarray) -> CubieState:
        """
        sticker_to_cubie_state from_stickers
        state = [
          corners_perm (8)       ∈ [0..7]
          corners_ori  (8)       ∈ [0..2]
          edges_perm   (12)      ∈ [0..11]
          edges_ori    (12)      ∈ [0..1]
        ] 最小充分状态
        定义并修正 ori
        """
        assert self.n == state.shape[1]
        edges_perm, edges_ori = self.edge_ids_ori(state)
        corners_perm, corners_ori = self.corner_ids_ori(state)
        # 修正 parity
        corner_parity = self.permutation_parity(corners_perm)
        edge_parity = self.permutation_parity(edges_perm)
        if corner_parity != edge_parity:
            print(f'Fixing odd parity: corner {corner_parity} != edge {edge_parity}')
            non_slice = CubieState.non_slice_edges()
            i, j = non_slice[-2], non_slice[-1]  # 交换最后两条非 slice 边
            edges_perm[i], edges_perm[j] = edges_perm[j], edges_perm[i]
            assert self.permutation_parity(edges_perm) == corner_parity, "Parity fix failed"

        return CubieState(
            corners_perm=corners_perm,
            corners_ori=corners_ori,  # self.corner_orientation(state)
            edges_perm=edges_perm,
            edges_ori=edges_ori,
        )

    def from_cubie(self, cubie: CubieState) -> np.ndarray:
        """
        从 CubieState.to_sticker 生成完整的贴纸状态 (6, n, n) 数组
        - 值是颜色索引 0~5 或颜色字符（根据需要）
        - 支持任意 n（中心块固定，边角根据 cubie）,目前支持3阶
        某一个 gauge 下的具体代表
        Sticker equality is not guaranteed; cubie equality is the invariant
        """
        # 输出数组：6面 × n × n，值是颜色索引 0~5
        n = self.n
        stickers = np.zeros((6, n, n), dtype=np.int8)  # base.solved.copy()
        # 填充中心块（固定颜色）
        center_colors = np.array([0, 1, 2, 3, 4, 5])  # U D F B R L
        for f in range(6):
            stickers[f, n // 2, n // 2] = center_colors[f]

        # solved 状态下每个角块的颜色顺序
        solved_corners = self.get_corners(self.solved)  # (8, 3)

        # solved 边块颜色（12 个位置）
        solved_edges = self.get_edges(self.solved)  # (12, 2)
        # [[(face_idx, r, c), (face_idx, r, c), (face_idx, r, c)],..
        for i, corners in enumerate(self.corner_coords(n=n)):
            cubie_id = cubie.corners_perm[i]
            twist = cubie.corners_ori[i]

            # solved 状态下这个 cubie 的 3 个颜色顺序
            colors = solved_corners[cubie_id]  # (3,)
            # 旋转 twist 次（顺时针）
            actual_colors = np.roll(colors, -twist)  # orientation 负 twist = 逆时针 roll

            # 贴到 3 个面
            for sticker_pos, color in zip(corners, actual_colors):  # [(f, r, c)]:[val]
                stickers[sticker_pos] = color

        for i, edges in enumerate(self.edge_coords(n=n)):  # [[(face_idx, r, c), (face_idx, r, c)],
            cubie_id = cubie.edges_perm[i]
            flip = cubie.edges_ori[i]

            colors = solved_edges[cubie_id]  # (12,2)
            actual_colors = np.roll(colors, flip)  # 翻转或不翻 flip 1 swap: (colors[1], colors[0])
            for sticker_pos, color in zip(edges, actual_colors):
                stickers[sticker_pos] = color

        return stickers

    @class_status('参考方法')
    def build_cubie_move_from_stickers(self, state_arr: np.ndarray, token: ActionToken) -> CubieMove:
        """
        构建 CubieMove：orientation 信息被抹平过,只作为"验证 / 校准工具" 不做 parity 修正,不保证 is_solvable
        不依赖贴纸索引顺序来算 delta，直接从 CubieState 计算。
        - cube: 当前 Cube 对象，需提供 to_cubie() 和 rotate_state()
        - axis, layer, direction: move 定义: (axis, layer, dir)
        """
        s0: CubieState = self.to_cubie(state_arr)  # 原始 CubieState
        rotated_arr = self.rotate_state(state_arr, token.axis, token.layer, token.direction)  # 贴纸级旋转
        s1: CubieState = self.to_cubie(rotated_arr)  # 旋转后状态

        mv = CubieMove.build(s0, s1)  # delta

        assert s1.is_solvable()
        assert mv.edges_ori_delta.sum() % 2 == 0
        assert mv.corners_ori_delta.sum() % 3 == 0, f'{token.axis},{mv.corners_ori_delta}'

        return mv

    @class_status('参考方法')
    def build_cubie_primitive_moves(self) -> dict[tuple, CubieMove]:
        """
        生成所有 primitive move 对应的 CubieMove,手工定义 / 程序生成（基于坐标）
        sticker rotation → CubieState → delta (right action)
        m.act(s) == rotate_state(s)
         | 项目       | corner | edge  |
         | --------- | ------ | ----- |
         | 群         | Z₃     | Z₂    |
         | reference | U/D 色  | F/B 色 |
         | U/D move  | 不变    | 不变   |
         | R/L move  | 变      | 不变   |
         | F/B move  | 变      | 变     |
        """
        prim_moves = {}
        for move in self.basic_generators():
            prim_moves[move] = self.build_cubie_move_from_stickers(self.solved, ActionToken(*move))
        return prim_moves  # self.PRIM_MOVES

    @staticmethod
    def build_group(gens: list[CubieMove], max_depth: int = 10, max_groups: int = 10000) -> dict:
        start = CubieMove.identity()
        queue = deque([start])
        group = {start: 0}

        while queue:
            current = queue.popleft()
            d = group[current]
            if d >= max_depth:
                continue

            for g in gens:
                new = current.compose(g)  # multiply(g)
                if new not in group:
                    group[new] = d + 1
                    queue.append(new)
                    if len(group) >= max_groups:
                        return group
        return group

    @staticmethod
    def build_phase_graph(start: Phase0Coord | Phase1Coord | Phase2Coord,
                          max_depth: int = 2, max_nodes: int = 10000) -> tuple:
        """
        Schreier graph,从群 + 子群 先验构造,理性不是发现世界结构，而是规定世界的可理解形式
        nodes: set[Phase1Coord]
        edges: list[(src, label, dst)]
        I explicitly constructed the Phase-1 Schreier graph of the Rubik's Cube quotient
        and verified generator degeneracies, involutions, and identity actions.
        """
        moves = CubieMove.phase0_moves if isinstance(start, Phase0Coord) \
            else CubieMove.phase1_moves if isinstance(start, Phase1Coord) \
            else CubieMove.phase2_moves
        queue = deque([start])
        nodes = {start: 0}
        # visited = {id(start)}
        edges = []
        while queue and len(nodes) < max_nodes:
            s = queue.popleft()
            d = nodes[s]
            if d >= max_depth:
                continue

            for label, m in moves.items():  # (axis,side,dir)
                s2 = m.act(s)
                edges.append((s, label, s2))
                if s2 not in nodes:
                    nodes[s2] = d + 1
                    queue.append(s2)
                    if len(nodes) >= max_nodes:
                        break

        # n = [(i.key, d) for i, d in nodes.items()]
        # e = [(i.key, j, k.key) for i, j, k in edges]
        return nodes, edges

    @staticmethod
    def build_phase15_graph(start: CubieState, max_depth: int = 2, max_nodes: int = 10000):
        moves = CubieMove.phase15_moves
        solved_idx = Phase15Coord.project(start).index
        queue = deque([(start, solved_idx)])
        nodes = {solved_idx: 0}
        edges = []
        while queue and len(nodes) < max_nodes:
            cubie, cur = queue.popleft()
            d = nodes[cur]
            if d >= max_depth:
                continue

            for label, m in moves.items():  # (axis,side,dir)
                next_cubie, next_coord = m.act(cubie)
                nxt = next_coord.index
                edges.append((cur, label, nxt))
                if nxt not in nodes:
                    nodes[nxt] = d + 1
                    queue.append((next_cubie, nxt))
                    if len(nodes) >= max_nodes:
                        break
        return nodes, edges

    @staticmethod
    def build_phase15_pruning() -> np.ndarray:
        """
        从 solved 出发 BFS 填充 Phase-1.5 pruning table（3360 状态）。
        走真实 CubieState → project，保证全坐标可达。
        """
        N_PHASE15 = 24 * 70 * 2  # `3360`
        PHASE15_MOVES: list[Phase15Action] = list(CubieMove.phase15_moves.values())
        INF = np.int8(127)
        dist = np.full(N_PHASE15, INF, dtype=np.int8)
        start = CubieState.solved()
        solved_idx = Phase15Coord.project(start).index
        dist[solved_idx] = 0
        queue = deque([(start, solved_idx)])
        while queue:
            cubie, cur = queue.popleft()
            d = dist[cur]
            nd = np.int8(d + 1)

            for m in PHASE15_MOVES:
                next_cubie, next_coord = m.act(cubie)
                nxt = next_coord.index
                if dist[nxt] == INF:
                    dist[nxt] = nd
                    queue.append((next_cubie, nxt))

        reachable = int(np.sum(dist < INF))
        print(f"Phase-1.5 pruning: {reachable}/{N_PHASE15} reachable, "
              f"max_dist={np.max(dist[dist < INF])}, "
              f"mean_dist={np.mean(dist[dist < INF]):.4f}")
        return dist

    @classmethod
    @class_status('测试')
    def build_phase_graph_from_max_h(cls, max_depth: int = 3, max_nodes: int = 20000):
        # 1. 先从 solved 跑一次，得到 dist
        if hasattr(cls, 'PHASE15_PRUNE'):
            dist = cls.PHASE15_PRUNE
        else:
            dist = cls.build_phase15_pruning()  # 返回 3360 的 dist

        # 2. 找 h 最大的有效 index
        valid_dist = np.where(dist < 127, dist, -1)
        max_h = np.max(valid_dist)  # 6
        assert max_h == -1, "No reachable states"

        max_idx = int(np.argmax(valid_dist))
        max_coord = Phase15Coord.from_index(max_idx)

        print(f"从 h = {max_h} 的状态出发: {max_coord} (index={max_idx})")

        start = max_coord.decode()
        # 3. 以 max_coord 为起点重新构建 graph
        return cls.build_phase15_graph(
            start=start,
            max_depth=max_depth,
            max_nodes=max_nodes
        )

    @classmethod
    def build_pruning_table(cls):
        # 离线构建器
        # PRIM_MOVES = CubieMove.prim_moves()
        PHASE0_MOVES: list[Phase0Action] = list(CubieMove.phase0_moves.values())
        PHASE1_MOVES: list[Phase1Action] = list(CubieMove.phase1_moves.values())
        PHASE2_MOVES: list[Phase2Action] = list(CubieMove.phase2_moves.values())
        print('build_pruning_table', len(PHASE1_MOVES), len(PHASE2_MOVES))
        import os
        if os.path.exists(os.path.join(DATA_DIR, 'phase1_pruning.npz')):
            data = np.load(os.path.join(DATA_DIR, "phase1_pruning.npz"))
            cls.CO_EO_PRUNE = data["CO_EO"]
            cls.UD_PRUNE = data["UD"]
        else:
            # PHASE0_PRUNE 两维联合（CO × EO），固定 UD-slice = 0,深度 ≤ 7
            cls.CO_EO_PRUNE = CubieMove.build_pruning_table(
                moves=PHASE0_MOVES,  # PHASE1_MOVES
                apply_move=lambda m, c: (m.corner_ori_map[c[0]], m.edge_ori_map[c[1]]),
                start_coord=(0, 0),
                table_shape=(2187, 2048)  # (3**7, 2**11)
            )  # dist((corner_ori, edge_ori)) ≈ 4.5M
            # 最大深度 7
            cls.UD_PRUNE = CubieMove.build_pruning_table(
                moves=PHASE1_MOVES,  # List[Phase1Action]
                apply_move=lambda m, ud: m.ud_slice_map[ud],
                start_coord=CubieState.solved_ud,
                table_shape=495
            )  # dist(ud_slice) C(12,4)=495
            np.savez(
                os.path.join(DATA_DIR, "phase1_pruning.npz"),
                CO_EO=cls.CO_EO_PRUNE,  # (2187, 2048)
                UD=cls.UD_PRUNE  # (495,)
            )

        if os.path.exists(os.path.join(DATA_DIR, 'phase2_pruning.npz')):
            data = np.load(os.path.join(DATA_DIR, "phase2_pruning.npz"))
            cls.CO_PRUNE = data["CO"]
            cls.EDGE_PRUNE = data["EDGE"]
            cls.SLICE_PRUNE = data["SLICE"]
        else:
            # Corner pruning
            cls.CO_PRUNE = CubieMove.build_pruning_table(
                moves=PHASE2_MOVES,
                apply_move=lambda m, idx: m.corner_perm_map[idx],
                start_coord=CubeBase.encode_perm(list(range(8))),
                table_shape=40320  # 8!
            )
            # Non-slice edge pruning
            cls.EDGE_PRUNE = CubieMove.build_pruning_table(
                moves=PHASE2_MOVES,
                apply_move=lambda m, idx: m.edge_perm_map[idx],
                start_coord=CubeBase.encode_perm(list(range(8))),  # 0
                table_shape=40320
            )
            # Slice pruning,进去收益极小，但复杂度翻倍
            cls.SLICE_PRUNE = CubieMove.build_pruning_table(
                moves=PHASE2_MOVES,
                apply_move=lambda m, idx: m.ud_slice_perm_map[idx],
                start_coord=0,
                table_shape=24
            )
            np.savez(
                os.path.join(DATA_DIR, "phase2_pruning.npz"),
                CO=cls.CO_PRUNE,  # 40320
                EDGE=cls.EDGE_PRUNE,  # 40320
                SLICE=cls.SLICE_PRUNE
            )
        if os.path.exists(os.path.join(DATA_DIR, 'phase15_pruning.npy')):
            cls.PHASE15_PRUNE = np.load(os.path.join(DATA_DIR, "phase15_pruning.npy"))
        else:
            cls.PHASE15_PRUNE = cls.build_phase15_pruning()
            np.save(os.path.join(DATA_DIR, "phase15_pruning.npy"), cls.PHASE15_PRUNE)

        # h_15(s) = dist[Phase15Coord.project(s).index]

        print(cls.CO_PRUNE.max())  # 最大深度 ≈ 11  14 /13
        print(cls.EDGE_PRUNE.max())  # ≈ 10~11  10 /8
        print(cls.PHASE15_PRUNE.max())  # /6
        print(np.sum(cls.CO_PRUNE >= 0))  # < 40320 一半以上的状态必然是 -1  40320
        print(cls.CO_EO_PRUNE.shape, cls.CO_PRUNE.shape, cls.EDGE_PRUNE.shape, cls.PHASE15_PRUNE.shape)
        print(cls.CO_EO_PRUNE[:3])
        print(cls.CO_PRUNE[:10], '...', cls.CO_PRUNE[-10:])
        print(cls.EDGE_PRUNE[:10], '...', cls.EDGE_PRUNE[-10:])
        print(cls.PHASE15_PRUNE[:10], '...', cls.PHASE15_PRUNE[-10:])
        print(cls.SLICE_PRUNE)
        print(np.bincount(cls.CO_PRUNE))
        print(np.bincount(cls.EDGE_PRUNE))
        print(np.bincount(cls.PHASE15_PRUNE[cls.PHASE15_PRUNE != 127]))
        """
        [   1   10   67  330  752 1400 2752 4384 6208 7136 8064 6528 2432  256]
        [    1    10    63   352  1623  5890 14345 15772  2264]
        [   1   13  102  515 1447 1183   99]
        """

    @classmethod
    def phase1_search(cls, cubie: CubieState, depth_limit: int = 8) -> list[tuple] | None:
        """
        IDA* 搜索 Phase-1：目标是进入 G₁（EO=0, CO=0, UD-slice 在中层）
        使用右作用 CubieMove.act + Phase1Action.project
        BFS 解决 18 个基本转动,直径 diam(G / G₁) ≈ 7，通常 depth_limit=7 或 8 足够
        12:9~12
        """
        PHASE1_MOVES = CubieMove.phase1_moves()

        def dfs(coord, depth: int, last_move: tuple | None):
            if depth > depth_limit:
                return None

            h = max(cls.CO_EO_PRUNE[coord.corner_ori, coord.edge_ori],
                    cls.UD_PRUNE[coord.ud_slice])  # admissible phase1_heuristic（reference）

            if coord.is_solved():  # EO=0, CO=0, UD-slice=solved, current_state.is_ud_slice_separated()
                print('phase1_search', depth, h, coord.ud_slice)  # 69,current_state.ud_slice_coord
                return []  # 判断 phase1 solved

            for k, m in PHASE1_MOVES.items():
                if CubieMove.is_redundant(last_move, k):
                    continue

                next_coord = m.act(coord)
                # next_state = m.replay(current_state) next_coord = Phase1Coord.project(next_state)
                res = dfs(next_coord, depth + 1, k)  # 递归 moves
                if res is not None:
                    return [(k, m)] + res

            return None

        initial_coord = Phase1Coord.project(cubie)
        return dfs(initial_coord, 0, None)

    @classmethod
    def phase2_search(cls, cubie: CubieState, depth_limit: int = 14) -> list[tuple] | None:
        """
        10～12个基本转动 diam(G₁ / G₂) = 10
        IDDFS 18 limit ≈ 10~11, 12:14-20
        """
        PHASE2_MOVES = CubieMove.phase2_moves()

        def dfs(coord, depth: int, last_move: tuple | None) -> list[tuple] | None:
            if depth > depth_limit:
                return None
            h = max(
                cls.CO_PRUNE[coord.corner_perm],
                cls.EDGE_PRUNE[coord.edge_perm],
                cls.SLICE_PRUNE[coord.ud_slice_perm]
            )

            if coord.is_solved():
                print('phase2_search', depth, h, coord.ud_slice_perm)
                return []

            for k, m in PHASE2_MOVES.items():
                if CubieMove.is_redundant(last_move, k):
                    continue

                next_coord = m.act(coord)
                res = dfs(next_coord, depth + 1, k)
                if res is not None:
                    return [(k, m)] + res

            return None

        initial_coord = Phase2Coord.project(cubie)
        return dfs(initial_coord, 0, None)

    @classmethod
    def phase15_dfs(cls, cubie: CubieState, depth_limit: int = 8) -> list[tuple] | None:
        """
        IDA* 搜索 Phase-1.5
        目标：slice_perm = solved, corner_coset = solved, parity = 0
        move 集：G₁
        """
        PHASE15_MOVES = CubieMove.phase15_moves()

        def dfs(state: CubieState, coord: Phase15Coord, depth: int, last_move: tuple | None):
            h = cls.PHASE15_PRUNE[coord.index]
            if depth + h > depth_limit:
                return None

            if coord.is_solved():
                print('phase15_search', depth, h, coord.index, coord.corner_coset)
                return []

            for k, m in PHASE15_MOVES.items():
                if CubieMove.is_redundant(last_move, k):
                    continue

                next_state, next_coord = m.act(state)
                res = dfs(next_state, next_coord, depth + 1, k)
                if res is not None:
                    return [(k, m)] + res

            return None

        initial_coord = Phase15Coord.project(cubie)
        return dfs(cubie, initial_coord, 0, None)

    @classmethod
    def phase15_search(cls, cubie: CubieState, depth_limit: int = 8) -> list[tuple] | None:
        """
        Phase-1.5 深度受限搜索，不要求 admissible
        先 lift 到一个 canonical CubieState,群作用是真实的
        Phase15Coord 仅用于 pruning / heuristic
        """
        PHASE15_MOVES = CubieMove.phase15_moves()

        def dfs(state: CubieState, coord: Phase15Coord, depth, last_move):
            h = cls.PHASE15_PRUNE[coord.index]
            if depth + h > depth_limit:
                return None

            if state.is_phase1_solved() and coord.is_solved():  # is_phase2_ready
                print('phase15_search', depth, h, coord.index, coord.corner_coset)
                return []  # 0 138 69

            # heuristic 动作排序，不裁决，不影响可达性
            scored = []
            for k, m in PHASE15_MOVES.items():
                if CubieMove.is_redundant(last_move, k):
                    continue

                next_state, next_coord = m.act(state)
                score = next_coord.heuristic()
                scored.append((score, k, m, next_state, next_coord))

            # order_phase15_moves, 先试"看起来对的动作"，只做 ordering
            scored.sort(key=lambda x: x[0])  # 越小越好

            for _, k, m, next_state, next_coord in scored:  # 再 DFS
                res = dfs(next_state, next_coord, depth + 1, k)
                if res is not None:
                    return [(k, m)] + res

            return None

        initial_coord = Phase15Coord.project(cubie)
        return dfs(cubie, initial_coord, 0, None)

    @classmethod
    def solve_phase1(cls, cubie: CubieState,
                     start: int = 6, end: int = 13) -> tuple[list[tuple], CubieMove, CubieState]:
        path1 = None
        d = start  # 9
        while d < end:  # 9/13
            path1 = cls.phase1_search(cubie, d)
            if path1 is not None:
                break
            print('phase1 depth', d)
            d += 1

        assert path1 is not None, f"Phase1 failed to solve: {cubie}"
        mv1, state = CubieMove.act_moves(cubie, [x[1].cubie_move for x in path1])
        return path1, mv1, state

    @classmethod
    def solve_phase2(cls, cubie: CubieState,
                     start: int = 9, end: int = 20) -> tuple[list[tuple], CubieMove, CubieState]:
        path2 = None
        d = start
        while d < end:  # 12,20
            path2 = cls.phase2_search(cubie, d)
            if path2 is not None:
                break
            print('phase2 depth', d)
            d += 1

        mv2, state = CubieMove.act_moves(cubie, [x[1].cubie_move for x in path2])
        return path2, mv2, state

    @classmethod
    def solve_phase15(cls, cubie: CubieState, max_depth: int = 12) -> tuple[list[tuple], CubieMove, CubieState]:
        """投影到 G₂ 可达 coset,优化 Phase-2 的入口分布,非必要,max:126"""
        assert cubie.is_phase1_solved(), "输入必须是 Phase-1 已解决状态"
        path = None
        if max_depth >= 0:
            for d in range(max_depth + 1):
                res = cls.phase15_search(cubie, depth_limit=d)
                if res is not None:
                    path = res
                    break
                print('phase15 depth', d)

        if path is not None:
            mv, state = CubieMove.act_moves(cubie, [x[1].cubie_move for x in path])
            # assert state.is_phase1_solved() 确保 Phase1 方向仍然正确
            # assert state.is_phase2_ready()
            return path, mv, state
        return [], CubieMove.identity(), cubie

    @classmethod
    def solve_kociemba(cls, cubie: CubieState,
                       phase1_start: int = 6, phase1_end: int = 12, phase15_depth=0,
                       phase2_start: int = 9, phase2_end: int = 19) -> tuple[list[tuple], CubieMove]:
        """
        Kociemba 两阶段求解：
            Phase1: 解决 EO + CO + UD-slice separation
            Phase2: 解决剩余 CP + EP（在 G1 内）
            返回：(move_keys 序列, 总复合 move)
            G -Phase-1 -> H -Phase-2 -> {e}
            Gₙ
             ├─ Phase-0：orientation only
             ├─ Phase-1：slice class
             ├─ Phase-1.5：center orbits
             └─ Phase-2：permutation class
        """
        assert cubie.is_solvable(), "Unsolvable cube state"

        path1, mv1, cubie1 = cls.solve_phase1(cubie, phase1_start, phase1_end)
        assert cubie1.is_phase1_solved(), f'Phase1 invalid: len={len(path1)}, ud_slice={cubie1.ud_slice_coord}'
        # assert Phase15Coord.project(state).parity == 0

        path15, mv15, cubie15 = CubieBase.solve_phase15(cubie1, max_depth=phase15_depth)
        if cubie15.is_phase2_ready():
            print("epoch phase 2 ready.")

        path2, mv2, cubie2 = cls.solve_phase2(cubie15, phase2_start, phase2_end)
        assert cubie2.is_phase2_solved(), f'Phase2 invalid: len={len(path2)}, state={cubie2}'

        assert cubie2 == cls.SOLVED_STATE, f'Not fully solved,state:{cubie2}'
        return [a for a, _ in path1 + path15 + path2], mv1.compose(mv15).compose(mv2)

    def solve_sticker(self, state: np.ndarray) -> list[tuple]:
        if not hasattr(self, 'CO_EO_PRUNE'):
            self.build_pruning_table()
        if not hasattr(self, 'SYM_DATA'):
            self.build_symmetry_data()

        n = self.n
        # 遍历 48 种对称，选 phase-1 剪枝距离最小的
        best_sym, best_dist = 0, 999
        for sym_id in range(48):
            s_sym = CubeBase.apply_symmetry(state, sym_id)
            s_fixed = self.SYM_DATA[sym_id]['color_perm'][s_sym]
            c_sym = self.to_cubie(s_fixed)
            coord = Phase1Coord.project(c_sym)
            d = max(self.CO_EO_PRUNE[coord.corner_ori, coord.edge_ori],
                    self.UD_PRUNE[coord.ud_slice])
            if d < best_dist:
                best_dist, best_sym = d, sym_id

        # 对最优对称状态求解
        s_sym = CubeBase.apply_symmetry(state, best_sym)
        s_fixed = self.SYM_DATA[best_sym]['color_perm'][s_sym]
        c_aligned = self.to_cubie(s_fixed)
        moves, mv = self.solve_kociemba(c_aligned)

        # 用预计算的逆 move_map 将对称空间的解映射回原始空间
        inv_map = self.SYM_DATA[best_sym]['inv_move_map']
        moves_orig = [inv_map[t] for t in moves]

        # correction: 解 inv_sym(solved) 的残余 → 同样用 inv_sym 的 inv_move_map 映射
        correction = self._compute_correction(best_sym)
        inv_sym = int(CubeBase.symmetry_inverse_id[best_sym])
        corr_orig = [self.SYM_DATA[inv_sym]['inv_move_map'][t] for t in correction]

        act = [ActionToken.from_cubie_move(*t, n=n).key for t in moves_orig + corr_orig]
        s0 = state.copy()
        self.act_moves(s0, act)
        print(f'sym={best_sym} inv={inv_sym} dist={best_dist} len={len(act)} '
              f'solved={self.is_solved(s0)} corr={len(correction)}')
        return act

    def build_symmetry_data(self):
        """预计算每种对称的 color_perm 和 inv_move_map
        color_perm[c] = σ(c): 将 apply_symmetry 后的贴纸颜色映射回标准中心
        inv_move_map: 对称空间 move key → 原始空间 move key
        """
        solved = CubieState.solved()
        prim = CubieMove.prim_moves  # {(axis, side, dir): CubieMove}

        # 预计算 18 个原始 move 作用于 solved 的 cubie 状态
        move_results = {k: m.act(solved) for k, m in prim.items()}

        self.SYM_DATA = {}
        for sym_id in range(48):
            M = CubeBase.symmetry_matrices[sym_id]

            # color_perm: σ(face_i) = face_j
            color_perm = np.zeros(6, dtype=np.int8)
            for old_fidx in range(6):
                normal_old = CubeBase.face_normal[CubeBase.FACES[old_fidx]]
                normal_new = M @ normal_old
                for fidx, face in enumerate(CubeBase.FACES):
                    if np.array_equal(normal_new, CubeBase.face_normal[face]):
                        color_perm[old_fidx] = fidx
                        break

            # 对每个原始 move: 原始空间 → 对称空间 move
            forward_map = {}
            for key_orig in prim:
                # 原始 move 作用于 solved → 贴纸 → 对称变换 → color_perm → cubie
                c_orig = move_results[key_orig]
                s_sticker = CubeBase.idx_to_state(c_orig.to_sticker())
                s_sym = CubeBase.apply_symmetry(s_sticker, sym_id)
                c_sym = self.to_cubie(color_perm[s_sym])
                # 匹配: 哪个 prim move 产生同样的 cubie 状态？
                for key_sym, c_target in move_results.items():
                    if c_target == c_sym:
                        forward_map[key_orig] = key_sym
                        break

            self.SYM_DATA[sym_id] = {
                'color_perm': color_perm,
                'inv_move_map': {v: k for k, v in forward_map.items()},
                'correction': None,
            }

    def _compute_correction(self, sym_id: int) -> list:
        """计算逆对称的修正序列: 解 σ⁻¹(solved) → solved"""
        if self.SYM_DATA[sym_id]['correction'] is not None:
            return self.SYM_DATA[sym_id]['correction']
        inv_sym = int(CubeBase.symmetry_inverse_id[sym_id])
        solved = self.solved.copy()
        s_inv = CubeBase.apply_symmetry(solved, inv_sym)
        s_fixed = self.SYM_DATA[inv_sym]['color_perm'][s_inv]
        c_residual = self.to_cubie(s_fixed)
        correction = []
        if c_residual != CubieState.solved() and c_residual.is_solvable():
            try:
                correction, _ = CubieBase.solve_kociemba(
                    c_residual, phase1_start=0, phase1_end=8,
                    phase15_depth=-1, phase2_start=0, phase2_end=12)
            except (AssertionError, ValueError):
                pass
        self.SYM_DATA[sym_id]['correction'] = correction
        return correction

    @class_status('参考实现')
    def permutation_parity_ok(self, state):
        corner_coords = self.corner_coords(self.n)
        edge_coords = self.edge_coords(self.n)
        solved_corners = [self.get_data(self.solved, c) for c in corner_coords]
        solved_edges = [self.get_data(self.solved, e) for e in edge_coords]

        def corner_perm(state):
            perm = []
            for c in corner_coords:
                cid = self.get_data(state, c)
                perm.append(solved_corners.index(cid))
            return perm

        def edge_perm(state):
            perm = []
            for e in edge_coords:
                eid = self.get_data(state, e)
                perm.append(solved_edges.index(eid))
            return perm

        return self.permutation_parity(corner_perm(state)) == self.permutation_parity(edge_perm(state))

    @class_status('参考方法')
    def corner_orientation(self, state: np.ndarray) -> np.ndarray:
        """
        返回每个角块的朝向 0,1,2 (Z3),只看 U / D 颜色在哪个贴纸位置（Z₃）,全局状态,cubie 自身坐标系 vs 世界坐标系 的相对关系
        朝向定义：需要旋转几次（沿角块到中心的径向）才能使 U/D 颜色回到"标准位置"（即 cycle[0] 位置）
        每个角块有 3 种姿态,orientation 的定义 必须对所有 move 保持一致,U/D 是魔方的"上下极轴"
        角块的朝向信息,在当前架构(在贴纸级表示)下，corner_orientation 是"冗余状态"，已经被贴纸的空间位置完全决定,当前魔方状态：贴纸级真实旋转
        ---rotate 不会改变它，因为 rotate 已经体现在贴纸位置里了,用于验证或接口兼容传统求解器时才需要。
        """
        U, D = self.face_idx['U'], self.face_idx['D']  # face_to_color 隐含假设：颜色编号 == 面编号 0,1
        corner_pos = self.corner_coords(self.n)
        ori = np.zeros(8, dtype=np.int8)
        for i, corner in enumerate(corner_pos):
            dst_colors = [state[f, r, c] for f, r, c in corner]
            # 找到 U/D 色在角块内部的索引，哪个物理位置（0,1,2）
            ud_idx = next(j for j, c in enumerate(dst_colors) if c in (U, D))  # physical
            cycle = self.corner_face_cycle[i]  # 映射到标准 cycle_faces 中的逻辑位置
            ud_logical_idx = next(j for j, f in enumerate(cycle) if f in ('U', 'D'))  # U/D 始终在索引 0！
            # orientation = 旋转次数使 U/D 色在 cycle[0] 位置(内部参考顺序)
            ori[i] = (ud_idx - ud_logical_idx) % 3  # 注意：方向要正确 —— 通常是顺时针为正 ori[i] = (3 - ud_idx) % 3
        return ori

    @class_status('已废弃')
    def corner_orientation_delta(self, s0: np.ndarray, s1: np.ndarray) -> np.ndarray:
        """
        局部增量,生成元,这个 move 对"被搬到 i 位置的角块"额外施加了多少扭转
        perm 表示 piece 的重排，ori_delta 表示局部坐标系里的 twist / flip
        需要 s0 (原始), s1 (旋转后) 来算 delta
        face_to_color 隐含假设：颜色编号 == 面编号 0,1(这是关键假设）
        """
        U, D = self.face_idx['U'], self.face_idx['D']
        corner_pos = self.corner_coords(self.n)
        corner_perm, corner_ori = self.corner_ids_ori(s1)
        ori_delta = np.zeros(8, dtype=np.int8)
        for i, corner in enumerate(corner_pos):
            dst_colors = [s1[f, r, c] for f, r, c in corner]
            src_pos = np.where(corner_perm == i)[0][0]  # 这个块在 s0 中的位置（通过 perm 反推）
            # orientation delta（Z₃）
            src_colors = [s0[f, r, c] for f, r, c in corner_pos[src_pos]]
            # 找到 U/D 色在角块内部的索引，哪个物理位置（0,1,2）
            dst_ud = next(j for j, c in enumerate(dst_colors) if c in (U, D))
            src_ud = next(j for j, f in enumerate(src_colors) if f in (U, D))
            ori_delta[i] = (dst_ud - src_ud) % 3
        return ori_delta

    @class_status('参考方法')
    def edge_orientation(self, state: np.ndarray) -> np.ndarray:
        """
        稳定子内的剩余自由度
        返回 12 条边块的朝向 0/1，shape = (12,), edge orientation 定义基于：颜色 == 面编号 == 几何语义
        规则：
            orientation = 0 时，优先让 U/D 颜色在 U/D 面上
            赤道边（无 U/D）：orientation = 0 时 F/B 颜色在 F/B 面上
        定义：
          - U/D 色边：在 U/D 面为 0，否则为 1
          - F/B 色边：在 F/B 面为 0，否则为 1
          - color == face_id
          - 标准 Singmaster U/D, F/B 轴定义
        """
        U, D, F, B = self.face_idx['U'], self.face_idx['D'], self.face_idx['F'], self.face_idx['B']
        ori = np.zeros(12, dtype=np.int8)  # edges_ori (12)
        for i, edge_def in enumerate(self.edge_coords(self.n)):
            (f1, r1, c1), (f2, r2, c2) = edge_def
            c1v, c2v = state[f1, r1, c1], state[f2, r2, c2]
            # 找 F 或 B 色 在角块内部的索引，哪个物理位置,edge_flip_index
            if c1v in (U, D):
                ori[i] = 0 if f1 in (U, D) else 1
            elif c2v in (U, D):
                ori[i] = 0 if f2 in (U, D) else 1
            elif c1v in (F, B):  # F/B 色的边（不含 U/D）
                ori[i] = 0 if f1 in (F, B) else 1
            elif c2v in (F, B):
                ori[i] = 0 if f2 in (F, B) else 1
            else:
                ori[i] = 0  # R/L 纯边，默认 0
        return ori  # [0 0 0 0 0 0 0 0 0 0 0 0]

    @class_status('参考方法')
    def build_edge_reference(self):
        """
        ref 被抹掉,投影态不可逆
        为每条 edge 确定 orientation = 0 的 reference sticker
        """
        U = self.face_idx['U']  # 0
        D = self.face_idx['D']  # 1
        F = self.face_idx['F']  # 2
        B = self.face_idx['B']  # 3

        ref = np.empty(12, dtype=np.int8)
        for i, edge in enumerate(self.edge_coords(self.n)):
            (f1, r1, c1), (f2, r2, c2) = edge
            # key = (self.FACES[f1], self.FACES[f2])
            col1 = self.solved[f1, r1, c1]
            col2 = self.solved[f2, r2, c2]

            # 优先选 U/D 颜色
            if col1 in (U, D):
                ref[i] = 0
            elif col2 in (U, D):
                ref[i] = 1
            else:
                ref[i] = 0 if col1 in (F, B) else 1  # 否则选 F/B
        return ref

    @class_status('参考方法')
    def build_corner_reference(self):
        """
        在 solved 状态下，记录每个 corner 的 U/D 色所在轴,corner 只看 U/D 是否在顶部/底部位置
        每个 corner 必须有一个参考循环
        """
        U = self.face_idx['U']
        D = self.face_idx['D']

        def corner_ud_index(colors):
            for i, c in enumerate(colors):
                if c == U or c == D: return i
            raise ValueError("corner missing U/D color")

        ref = np.empty(8, dtype=np.int8)
        for i, corner in enumerate(self.corner_coords(self.n)):
            colors = [self.solved[f, r, c] for f, r, c in corner]
            ref[i] = corner_ud_index(colors)

        return ref  # [0 0 0 0 0 0 0 0]

    def build_corner_reference_axis(self):
        """
        在 solved 状态下，记录每个 corner 的 U/D 色所在轴,corner 只看 U/D 是否在顶部/底部位置
        这个 corner 的"重力轴"是不是 U/D,axis 无方向/无旋向,twist 的等价表示
        corner 的 twist 循环 ≠ 空间轴的排列循环.而是"相对于参考循环顺序的位移",axis 本身没有方向性、也没有旋向。
        """
        U = self.face_idx['U']
        D = self.face_idx['D']

        ref = np.empty(8, dtype=np.int8)
        for i, corner in enumerate(self.corner_coords(self.n)):
            for (f, r, c) in corner:
                cv = self.solved[f, r, c]  # shape (6,n,n)
                if cv in (U, D):
                    axis, _ = self.face_axis[self.FACES[f]]
                    ref[i] = axis
                    break
            else:
                raise RuntimeError(f"Solved corner {i} without U/D color")

        return ref  # [1 1 1 1 1 1 1 1]

    def build_edge_reference_axis(self) -> np.ndarray:
        """
        在 solved 状态下，记录每条 edge 的 UD 颜色所在的轴（0,1,2）
        返回:
            ref: shape (12,) 的数组，每个元素是该 edge 在 solved 状态下 UD 色所在的轴,-1 表示该边在 solved 时没有 U/D 色
        """

        U = self.face_idx['U']
        D = self.face_idx['D']
        ref = np.full(12, -1, dtype=np.int8)

        edge_coords_list = self.edge_coords(self.n)
        for i, piece in enumerate(edge_coords_list):
            for fidx, r, c in piece:
                cv = self.solved[fidx, r, c]  # solved 状态的颜色
                if cv in (U, D):
                    axis, _ = self.face_axis[self.FACES[fidx]]
                    ref[i] = axis
                    break  # 一条边最多一条 U/D 色

        # print("Edges with UD color in solved:", np.sum(ref != -1)) 8
        return ref  # [ 1  1  1  1 -1 -1 -1 -1  1  1  1  1]

    def ud_slice_alignment(self, state: np.ndarray):
        """属于 UD slice 的 edge，目前仍位于 slice 位置) / 4 Coset 关键量"""
        if not hasattr(self, 'UD_SLICE_EDGES'):
            solved_edges_perm, _ = self.edge_ids_ori(self.solved)
            self.UD_SLICE_EDGES = tuple(int(solved_edges_perm[pos]) for pos in self.SLICE_POSITIONS)

        perm, _ = self.edge_ids_ori(state)
        aligned = sum(1 for pos in self.SLICE_POSITIONS if perm[pos] in self.UD_SLICE_EDGES)
        return aligned  # ∈ {0,1,2,3,4}

    def corner_ud_defect(self, state: np.ndarray) -> int:
        """
        轴错位的统计分布,有多少个角块的 U/D 颜色不在 ref 轴
        - corner_ud_alignment = 8 - np.sum(hist) corner_ud_axis_defect
        返回值 ∈ {0,1,...,8}
        """
        if not hasattr(self, 'CORNER_REF_AXIS'):
            self.CORNER_REF_AXIS = self.build_corner_reference_axis()

        corner_coords = self.corner_coords(self.n)
        U = self.face_idx['U']
        D = self.face_idx['D']
        defect = 0
        for i in range(8):
            current_axis = None  # 找到这个角块当前 U/D 颜色所在的轴
            for f, r, c in corner_coords[i]:
                color = state[f, r, c]
                if color in (U, D):
                    current_axis, _ = self.face_axis[self.FACES[f]]
                    break
            # 如果当前轴 ≠ 参考轴 → 算作错位，且错位到了 current_axis
            if current_axis != self.CORNER_REF_AXIS[i]:
                defect += 1
        return defect  # 轴错位分布,轴对齐率:, 8 - np.sum(hist) / 8

    def edge_ud_defect(self, state: np.ndarray) -> int:
        """
        edge_defect_hist
        有多少条本应在 UD 轴的 edge，目前不在 UD 轴
        值域: {0,2,4,6,8}（通常偶数，因为 parity 守恒）
        """
        if not hasattr(self, 'EDGE_REF_AXIS'):
            self.CORNER_REF_AXIS = self.build_edge_reference_axis()

        edge_coords = self.edge_coords(self.n)
        U = self.face_idx['U']
        D = self.face_idx['D']
        defect = 0
        for i in range(12):
            ref_axis = self.EDGE_REF_AXIS[i]
            if ref_axis == -1:
                continue  # 这条边本来就没有 U/D，不统计 defect

            # 找当前状态下这条边的 U/D 颜色所在轴
            current_axis = None
            for fidx, r, c in edge_coords[i]:
                color = state[fidx, r, c]
                if color in (U, D):
                    current_axis, _ = self.face_axis[self.FACES[fidx]]
                    break
            if current_axis is None:
                continue
            if current_axis != ref_axis:
                defect += 1
        # assert defect % 2 == 0
        return defect

    def face_order(self, state: np.ndarray, face: str) -> float:
        """
        衡量一面"像完整中心颜色面"的程度
        center-color stickers on that face) / (n²)
        值域 [0,1]，1 表示整面都是中心颜色
        """
        face_idx = self.face_idx[face]
        center_color = face_idx
        count = np.sum(state[face_idx] == center_color)
        return count / (self.n * self.n)

    def face_entropy(self, state: np.ndarray) -> np.ndarray:
        """
        返回 6 个面的颜色分布熵 熵越小 → 颜色越集中,越接近单色面 heuristic
        计算每个颜色的出现次数,捕捉  Phase-1.5 的"中间态"
        """
        ent = np.zeros(6, dtype=np.float32)
        for f in range(6):
            colors, counts = np.unique(state[f].reshape(-1), return_counts=True)
            p = counts / counts.sum()
            ent[f] = -np.sum(p * np.log(p + 1e-9))
        return ent

    def heuristic_corner_perm(self, state: np.ndarray):
        """角块在 permutation 意义上的缺陷分布 heuristic,轴错位的统计分布"""
        corners_perm, _ = self.corner_ids_ori(state)
        return np.count_nonzero(corners_perm != np.arange(8))

    def observables(self, state: np.ndarray):
        """现象 mid_level_features
        返回一组观测值，用于描述当前魔方状态的关键特征
        连续、相对单调
        在 G/H 上引入一个"连续势能函数"
        o = [
          mean(face_entropy), 面级结构 ,容易被"绕路动作"欺骗 symptom
          std(face_entropy),
          mean(face_order),
          ---symptom_observables

          ud_slice_alignment / 4, scalar ∈ {0..4}
          corner_ud_alignment / 8, scalar, 8 - sum(corner_defect_hist)
          edge_ud_alignment / 8, calar, 8 - sum(edge_defect_hist)
        ]
        """
        #  面熵 - 均值 & 标准差（越小越好）
        ent = self.face_entropy(state)
        mean_face_entropy = np.mean(ent)
        std_face_entropy = np.std(ent)

        # 面秩序 - 均值（越大越好）
        face_orders = [self.face_order(state, f) for f in self.FACES]
        mean_face_order = np.mean(face_orders)

        # UD 中层对齐率 [0,1] ud_slice_alignment
        ud_slice_align = self.ud_slice_alignment(state) / 4.0

        # 角块 UD 轴对齐率 [0,1] corner_ud_alignment
        corner_defect = self.corner_ud_defect(state)
        corner_ud_align = (8 - corner_defect) / 8.0

        # 边块 UD 轴对齐率 [0,1] edge_ud_alignment
        edge_defect = self.edge_ud_defect(state)
        edge_ud_align = (8 - edge_defect) / 8.0

        # 组合成向量
        o = np.array([
            mean_face_entropy,  # 面熵均值（越小越有序）
            std_face_entropy,  # 面熵标准差（面间差异）
            mean_face_order,  # 面秩序均值（越大越好,接近 1.0 越好）
            ud_slice_align,  # UD 中层对齐率
            corner_ud_align,  # 角块 UD 轴对齐率
            edge_ud_align  # 边块 UD 轴对齐率
        ], dtype=np.float32)
        return o

    def causal_observables(self, state: np.ndarray):
        return np.array([
            self.ud_slice_alignment(state),  # 0..4, 越大越好
            8 - self.corner_ud_defect(state),  # 0..8, 越大越好
            8 - self.edge_ud_defect(state),  # 0..8, 越大越好
        ], dtype=np.float32)

    def delta_potential(self, state: np.ndarray, token: ActionToken):
        """
        返回一个标量： Δpotential 因果张力变化 potential_drop
        < 0 : 张力下降（好）
        = 0 : 基本无变化
        > 0 : 张力上升（坏）
        """
        obs_before = self.causal_observables(state)
        next_state = self.rotate_state(state, token.axis, token.layer, token.direction)
        obs_after = self.causal_observables(next_state)

        # 越大越好，所以 potential = -obs
        delta = obs_after - obs_before

        # 分层加权（非常重要）
        w = np.array([
            3.0,  # UD slice 结构最关键
            2.0,  # corner coset
            1.0,  # edge 对齐
        ], dtype=np.float32)

        # 负数 = potential 下降
        return -np.dot(w, delta)

    def critic_progress_label(self, state_t: np.ndarray, state_t1: np.ndarray) -> float:
        """
        计算从 t 到 t+1 的进展 label（稠密 reward）
        经验判断: heuristic、critic、policy
        主要组成部分：
        - Δslice: UD 中层对齐变化（权重最高）
        - Δud: UD 轴对齐总变化（角 + 边）
        - ΔH: 平均面熵下降（负熵增加 = 进步）
        - Δorder: 平均面秩序提升

        label = 1.0 * sign(Δslice) + 0.5 * sign(Δud) + 0.5 * clamp(ΔH_drop, -1,1)
        label ≈ sign(Δ 更接近 Phase-1.5 子群)
        """
        # Δslice UD slice 对齐（0~4）
        slice_t = self.ud_slice_alignment(state_t)
        slice_t1 = self.ud_slice_alignment(state_t1)
        delta_slice = slice_t1 - slice_t  # 正向 = 增加完整性

        # Δud UD 轴对齐（角 + 边，各自 0~1）
        corner_defect_t = self.corner_ud_defect(state_t)
        corner_defect_t1 = self.corner_ud_defect(state_t1)
        corner_align_t = (8 - corner_defect_t) / 8.0
        corner_align_t1 = (8 - corner_defect_t1) / 8.0

        edge_defect_t = self.edge_ud_defect(state_t)
        edge_defect_t1 = self.edge_ud_defect(state_t1)
        edge_align_t = (8 - edge_defect_t) / 8.0
        edge_align_t1 = (8 - edge_defect_t1) / 8.0

        ud_align_t = corner_align_t + edge_align_t
        ud_align_t1 = corner_align_t1 + edge_align_t1
        delta_ud = ud_align_t1 - ud_align_t  # 正向 = 轴对齐提升

        # ΔH  面熵变化（熵下降 = 进步）, 不能压过群论结构
        ent_t = self.face_entropy(state_t)
        ent_t1 = self.face_entropy(state_t1)
        mean_ent_t = np.mean(ent_t)
        mean_ent_t1 = np.mean(ent_t1)
        delta_H = mean_ent_t - mean_ent_t1  # 正向 = 熵降低（有序性增加）

        # 面秩序变化（秩序上升 = 进步）
        # order_t  = np.mean([self.face_order(state_t, f) for f in self.FACES])
        # order_t1 = np.mean([self.face_order(state_t1, f) for f in self.FACES])
        # delta_order = order_t1 - order_t

        # 最终 label
        label = (
                1.0 * np.sign(delta_slice)  # 最重要：中层完整性变化,保证策略学的是 方向场，而不是幅值函数
                + 0.5 * np.sign(delta_ud)  # UD 轴对齐变化
                + 0.5 * np.clip(delta_H, -1.0, 1.0)  # 熵下降幅度（夹到 [-1,1]）,防止极端值
        )
        # dead-move 惩罚
        # if delta_slice == 0 and delta_ud == 0:
        #     label -= 0.1
        return label  # -2.0~2

    def generate_state(self, max_depth: int = 50) -> tuple['StickerMove', np.ndarray]:
        moves = list(self.basic_generators())
        random.shuffle(moves)
        path = [random.choice(moves) for _ in range(max_depth)]
        sm, state = StickerMove.act_moves(self.solved.copy(), ActionToken.from_path(path))
        return sm, state

    @staticmethod
    def generate_moves(length: int = 20, n: int = 3) -> list['ActionToken']:
        moves = ActionToken.basic_generators(n)
        return [random.choice(moves) for _ in range(length)]

    @staticmethod
    def generate_compose_moves(gens: dict[tuple, 'CubieMove'], commutator: bool = False, max_len: int = -1) -> dict:
        """
        返回可用的 compose 序列 |S²| distance ≤ 2 可达状态数
        or commutator(A, B) = A B A⁻¹ B⁻¹,构造局部操作序列，群元素乘法不满足交换律
        描述：局部自由度 group commutator width
        防止非法 orientation
        防止 parity 错误
        防止 edge flip / corner twist
        保证物理可达，筛掉非法状态

        cubie 世界	搜索空间裁剪
        IDA* / Kociemba	必需
        12 generators：134
        21：212
        """
        I = CubieMove.identity()
        products = {}
        for A, g1 in gens.items():
            for B, g2 in gens.items():
                if not (A or B): continue
                if len(products) > max_len > 0: break
                t1 = ActionToken.from_path(A)
                t2 = ActionToken.from_path(B)
                seq = t1 + t2
                m = g1.compose(g2)
                if commutator:
                    m = m @ g1.inverse() @ g2.inverse()
                    seq = ActionToken.commutator(t1, t2)  # commutator 永远不会改变 parity
                if m == I:  # 排除单位元,去 identity
                    continue
                products[m] = seq  # 去重

        # print(len(products))
        solved = CubieState.solved()
        # check_state/is_solvable/is_phase1_solved
        return {tuple(t.key for t in seq): m for m, seq in products.items() if m.act(solved).is_solvable()}

    @staticmethod
    def random_walk(length: int = 50, gen: list = None) -> CubieMove:
        moves = gen or list(CubieMove.prim_moves.values())
        if length == 1:
            return random.choice(moves)
        current = CubieMove.identity()
        for _ in range(length):
            m = random.choice(moves)
            current = current.compose(m)
        return current

    @classmethod
    def cubie_distance(cls, s: CubieState) -> tuple[int, int]:
        """
        自动判断当前状态属于哪个阶段，并返回对应的距离下界（heuristic）
        返回: (phase: int, distance: int)  phase 0=solved, 1=Phase-1, 2=Phase-2, 3=orientation
        """
        if not hasattr(cls, 'CO_EO_PRUNE'):
            cls.build_pruning_table()

        if s == cls.SOLVED_STATE:
            return 0, 0

        # Phase-1: 一次计算 co/eo，避免 is_phase1_solved + project 重复遍历
        co = s.corner_ori_coord
        eo = s.edge_ori_coord
        if co != 0 or eo != 0 or not s.is_ud_slice_separated():
            ud = s.ud_slice_coord
            d1 = max(cls.CO_EO_PRUNE[co, eo], cls.UD_PRUNE[ud])
            return 1, d1

        # Phase-2: Phase-1 已解决，检查 permutation
        if not s.is_phase2_solved():
            coord = Phase2Coord.project(s)
            d2 = max(
                cls.CO_PRUNE[coord.corner_perm],
                cls.EDGE_PRUNE[coord.edge_perm],
                cls.SLICE_PRUNE[coord.ud_slice_perm],
            )
            return 2, d2

        return 3, s.orientation_distance

    @staticmethod
    def generate_cubie(length: int = 50, left: bool = False, check: bool = False) -> CubieState:
        """
        生成一个随机打乱的 CubieState,使用 act_left 模拟物理转动顺序，更符合直观和 sticker 模型
        phase0
        """
        moves = list(CubieMove.prim_moves.items())
        state = CubieState.solved()
        # 连续应用随机 move,random.sample(moves, length)
        last = None
        i = 0
        while i < length:
            k, m = random.choice(moves)
            if check and CubieMove.is_redundant(last, k):
                continue
            state = m.act_left(state) if left else m.act(state)
            last = k
            i += 1

        assert state.is_solvable()
        return state

    @staticmethod
    def generate_cubie_rho(max_depth: int = 27, sigma: float = 1.0) -> np.ndarray:
        """生成若干随机线性组合,可控标准差 combination"""
        moves = list(CubieMove.prim_moves.values())
        coeffs = np.random.normal(loc=0.0, scale=sigma, size=max_depth)  # np.random.randn()
        selected_moves = random.choices(moves, k=max_depth)
        rho_zero = moves[0].rho()
        A = np.zeros_like(rho_zero, dtype=rho_zero.dtype)
        for c, mv in zip(coeffs, selected_moves):
            A += c * mv.rho()
        return A  # (228, 228) # sum(c_i * mv_i.rho() for mv_i, c_i in zip(selected_moves, np.random.randn(len(selected_moves)))

    @classmethod
    def generate_phase1_cubie(cls, max_depth: int = 20) -> CubieState:
        """Phase-1 solved cubie"""
        moves = list(CubieMove.phase1_moves().values())
        state = CubieState.solved()
        depth = np.random.randint(1, max_depth + 1)
        for _ in range(depth):  # max_depth
            m = random.choice(moves)
            state = m.replay(state)

        _, mv, cubie = cls.solve_phase1(state)
        assert cubie.is_phase1_solved()
        return cubie

    @classmethod
    def generate_phase15_cubie(cls, cubie_phase1: CubieState, max_depth: int = 8) -> CubieState:
        """
       从 Phase-1 已解决状态开始，随机打乱中层边（UD slice）生成 Phase-1.5 状态。
       Args:
           cubie_phase1: Phase-1 已解决的 CubieState
           max_depth: 最大随机动作步数
        """
        assert cubie_phase1.is_phase1_solved(), "输入必须是 Phase-1 已解决状态"

        moves = list(CubieMove.phase15_moves().values())
        cubie = cubie_phase1.clone()
        depth = np.random.randint(1, max_depth + 1)
        for _ in range(depth):
            m = np.random.choice(moves)  # p=weights
            cubie = m.replay(cubie)

        # 确保 Phase1 方向仍然正确
        if not cubie.is_phase1_solved():  # "Phase-1 被破坏"
            cubie = cls.solve_phase1(cubie)[2]  # 只取最终 cubie state
        return cubie

    @classmethod
    def generate_phase15_dataset(cls, max_depth: int = 10, num_starting_points: int = 20,
                                 num_samples: int = 5000, as_key: bool = False, start_random: bool = False) -> list:
        ''''
        Phase15Coord 只是 Phase-1.5 子群的投影，信息是丢失的，必须保留 cubie
        随机游走采样，单步转移（single-step transition）
        起点多样性 20
        总转移数 6000-8000
        '''
        PHASE15_MOVES = CubieMove.phase15_moves()
        MOVE_IDX = CubieMove.basic_generators()
        starting_pool = [cls.generate_phase1_cubie(max_depth=20) for _ in range(num_starting_points)]  # 提前生成起点池
        dataset = []
        for _ in range(num_samples):
            cubie_phase1 = np.random.choice(starting_pool).clone()  # 从池子里随机选一个起点
            if start_random:
                cubie_phase15 = cls.generate_phase15_cubie(cubie_phase1, max_depth=8)  # 随机打乱 Phase-1 状态
                cubie = cubie_phase15.clone()
            else:  # 从 phase1_solved 解出发
                cubie = cubie_phase1.clone()
            coord = Phase15Coord.project(cubie)
            # state = coord.embedding() cubie.vector
            # score = coord.heuristic()
            # cid = coord.index
            depth = np.random.randint(1, max_depth + 1)
            for step in range(depth):
                move_id = random.choice(range(len(MOVE_IDX)))  # 18 np.
                m_k = MOVE_IDX[move_id]
                m = PHASE15_MOVES[m_k]
                next_cubie, next_coord = m.act(cubie)
                dataset.append((coord, move_id, next_coord,
                                cubie, next_cubie,
                                cubie_phase1, step,  # cubie_phase15
                                ))  # step 轨迹内部的进度标记,保留起点信息,部分 move 可以偶然修复 next_cubie.is_phase1_solved()
                coord = next_coord
                cubie = next_cubie

        if as_key:
            dataset = [(d[0].key, d[1], d[2].key,
                        d[3].key, d[4].key,
                        d[5].key, d[6]) for d in dataset]

        return dataset

    def get_phase15_M(cls):
        '''
        M(d, θ) = E[Δ parity | distance=d, corner=θ]
        径向过程是主导,角向调制是真实的，但高度可压缩（有效维度 ≈ 4）rank=5 补齐剩余线性自由度
        壳层之间主方向不共享固定基
        角向自由度随 r 连续漂移
        整体维度 ≈ 4~5
        角向高维 + 低秩调制
        '''
        N_SLICE = 24
        N_CORNER = 70
        N_PARITY = 2

        dist = cls.PHASE15_PRUNE
        print(np.bincount(dist))  # [   1   13  102  515 1447 1183   99]
        # 重塑成 (24, 70, 2)
        dist_3d = dist.reshape(N_SLICE, N_CORNER, N_PARITY)
        # 把 127 替换成 NaN，便于热图显示为灰色/白色
        dist_3d = np.where(dist_3d == 127, np.nan, dist_3d)
        data_0 = dist_3d[:, :, 0]  # (24, 70)
        data_1 = dist_3d[:, :, 1]
        p_delta = data_1 - data_0  # ∈ {-1,0,1}
        print(p_delta.shape, p_delta.min(), p_delta.max())

        dist_flat = data_0.flatten()
        new_dist_flat = data_1.flatten()
        delta_flat = p_delta.flatten()
        unique_d = np.unique(dist_flat)
        print(len(delta_flat), np.corrcoef(delta_flat, dist_flat)[0, 1])
        # A = np.vstack([dist_flat, np.ones_like(dist_flat)]).T
        # coef, _, _, _ = np.linalg.lstsq(A, new_dist_flat, rcond=None)
        # residual = new_dist_flat - coef[0] * dist_flat + coef[1]
        # print(np.std(residual),np.unique(residual))

        for d in unique_d:
            mask = dist_flat == d
            vals = delta_flat[mask]
            print(
                f"d={d}  "
                f"-1:{np.mean(vals == -1):.2f}  "  # neg_ratio
                f"0:{np.mean(vals == 0):.2f}  "
                f"+1:{np.mean(vals == 1):.2f}  "  # pos_ratio
                f"std:{np.std(new_dist_flat[mask]):.6f}"
            )

        D = sorted(unique_d)  # 距离层（radial layer）离散值 0-6,D ≈ 7（壳层）
        C = N_CORNER  # C ≤ 70（corner）
        M_raw = np.zeros((len(D), C))  # M_avg
        V_D = [None] * len(D)

        for i, d in enumerate(D):
            mask = dist_3d[:, :, 0] == d  # 选择当前距离层的所有点
            block = np.where(mask, p_delta, np.nan)  # 屏蔽非当前距离层
            M_raw[i] = np.nanmean(block, axis=(0, 1))  # 对 slice/另一个维度平均，得到角向均值

            # valid_cols = ~np.isnan(block).all(axis=0)
            # B = block[:, valid_cols]
            # B = np.nan_to_num(B, nan=0.0)
            B = np.nan_to_num(block, nan=0.0)  # 不删列
            U_d, S_d, Vt_d = np.linalg.svd(B, full_matrices=False)
            V_D[i] = Vt_d
            ratio = S_d ** 2 / np.sum(S_d ** 2)
            rank_d = (S_d > 1e-6).sum()
            print(d, rank_d, ratio[:3])  # 是否存在统一角向子空间

        # for i, d1 in enumerate(D):
        #     for j, d2 in enumerate(D):
        #         # u1 = U_D[d1][:,0]
        #         v1 = V_D[i][0, :]  # U_d[:, :k] 第一角向模态
        #         v2 = V_D[j][0, :]
        #         cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))  # 主模态跨层 cosine,奇异向量是否跨层对齐
        #         print(f"d1={d1}, d2={d2}, cos={cos:.4f}")  # 不是所有壳层共享同一个 θ 而是 θ 随 r 平滑旋转
        #         # 角向主方向随着 r 单调变化
        #
        # Theta = np.stack([V_D[i][0, :] for i in range(len(D))])  # (7, 70)
        # U2, S2, V2 = np.linalg.svd(Theta, full_matrices=False)  # 每层的主角向模态联合 SVD
        # print("Explained ratio across shells:", S2 ** 2 / np.sum(S2 ** 2))  # 不存在统一角向子空间
        #
        # for k in range(4):
        #     vec = V2[k]  # (70,) cubie group 分解
        #     print(np.argsort(np.abs(vec))[-10:])
        #     for delta_val in [-1, 0, 1]:
        #         mask = delta_flat == delta_val
        #         print(f"Mode {k}, delta {delta_val}: mean {vec[mask[:70]].mean():.4f}")
        """
        单个距离层的角向分布本身是高维的,低秩来自层之间的"对齐"或"相关性"
        0.0 1 [1. 0. 0.]
        1.0 4 [0.25 0.25 0.25]
        2.0 22 [0.13662735 0.11186389 0.09163437]
        3.0 24 [0.28860816 0.09246434 0.07245906]
        4.0 24 [0.27545707 0.07417986 0.07312078]
        5.0 24 [0.3933974  0.0643495  0.05869728]
        6.0 18 [0.21496932 0.15570672 0.12163538]
        不存在统一角向子空间，虽然每层是高维的，但层与层之间存在对齐结构。
        Explained ratio across shells: [0.29692753 0.2014328  0.15423826 0.1427982  0.09835902 0.06577302 0.04047117]
        Mode 0, delta -1: mean 0.0801
        Mode 0, delta 0: mean -0.0504
        Mode 0, delta 1: mean -0.1261
        Mode 1, delta -1: mean 0.1116
        Mode 1, delta 0: mean 0.0939
        Mode 1, delta 1: mean 0.0622
        Mode 2, delta -1: mean 0.0156
        Mode 2, delta 0: mean 0.0011
        Mode 2, delta 1: mean 0.0277
        Mode 3, delta -1: mean 0.0024
        Mode 3, delta 0: mean 0.0672
        Mode 3, delta 1: mean -0.0103
        共享"变化方向"
        """
        # valid_cols = ~np.isnan(M_raw).all(axis=0)
        # M = M_raw[:, valid_cols]  # 去掉全 NaN 的 corner
        # print( np.sum(~np.isnan(M)),np.nanstd(M, axis=1))
        # row_std = np.nanstd(M, axis=1, keepdims=True)
        ## M_std = np.nan_to_num((M - np.nanmean(M, axis=1, keepdims=True)) / row_std, nan=0.0)
        # valid_rows = np.ones(M.shape[0], dtype=bool)
        # D_valid = np.array(D)[valid_rows]
        # radial_profile = np.nanmean(M, axis=1)  # (7,)
        # for d, val in zip(D_valid, radial_profile):#径向剖面（每个距离层的平均 p_delta）
        #     print(f"d={d}: p_Δ = {val:.6f}")
        '''
        (d=0.0): p_Δ = 1.000000
        (d=1.0): p_Δ = 1.000000
        (d=2.0): p_Δ = 0.741935
        (d=3.0): p_Δ = 0.614108
        (d=4.0): p_Δ = 0.154286
        (d=5.0): p_Δ = -0.518459
        (d=6.0): p_Δ = -0.918367
        '''

        M_keep = np.full((len(D), C), np.nan)
        for i, d in enumerate(D):
            mask_d = dist_3d[:, :, 0] == d  # (slice, corner)
            for c in range(C):
                values = p_delta[mask_d[:, c], c]  # 取该 d 层该 θ 的值
                if len(values) > 0:
                    M_keep[i, c] = values.mean()
        # 构造矩阵
        M_np = M_keep.copy()  # (7, 70)

        valid_cols = ~np.isnan(M_np).all(axis=0)  # 去掉全nan列
        M_np = M_np[:, valid_cols]  # 未中心化 M_clean
        mask = ~np.isnan(M_np)  # 标记观测值
        print("Observed count:", mask.sum())  # 283

        # 做 SVD 分析
        M_centered = M_np - np.nanmean(M_np, axis=1, keepdims=True)  # 行中心化,去掉每行的均值
        M_clean = np.nan_to_num(M_centered, nan=0.0)  # Phase1.5 是径向主导，角向其实可以填 0 或用平均值, 防止残留 NaN 导致 SVD 崩溃
        U, S, Vt = np.linalg.svd(M_clean, full_matrices=False)
        explained_ratio = S ** 2 / np.sum(S ** 2)  # 角向模态解释方差累积: np.cumsum(explained_ratio)
        print("singular values:", S)
        print("explained ratio:", explained_ratio)
        """
        singular values: [9.18326505e+00 5.01761404e+00 2.22274471e+00 1.67290484e+00
         1.61810289e+00 2.92488830e-16 1.89293979e-17]
        explained ratio: [7.03553697e-01 2.10037827e-01 4.12175510e-02 2.33477743e-02
         2.18431505e-02 7.13709673e-34 2.98934892e-36]
        """
        n_rank = min(5, len(S))
        modes_layers = np.zeros((M_clean.shape[0], n_rank))
        for k in range(n_rank):
            modes_layers[:, k] = U[:, k] * S[k]  # 对每个层的贡献 = U[:, k] * S[k] （奇异值加权）
        return dist_3d, M_np, M_clean, mask

    @staticmethod
    @class_status('实验用')
    def canonicalize_ud_slice(s: 'CubieState') -> 'CubieState':
        """
        Phase-1 → Phase-2
        phase2_start = canonicalize_ud_slice(phase1_state)
        1. 将所有 UD-slice 边放回标准中层位置（SLICE_POSITIONS）
        2. 内部顺序按 solved 顺序排列
        """
        s = s.clone()

        slice_pos = CubeBase.SLICE_POSITIONS
        non_slice_pos = CubeBase.NON_SLICE_POSITIONS
        slice_cubies = s.ud_slice_edges  # (4,5,6,7)

        original_edges = s.edges_perm.copy()

        # 当前 slice cubies
        slice_edges = sorted(e for e in original_edges if e in slice_cubies)  # 按 solved 顺序
        # 非 slice cubies
        non_slice_cubies = [e for e in original_edges if e not in slice_cubies]

        new_edges = np.zeros(12, dtype=np.int8)  # 重写 edges_perm
        for pos, cubie in zip(slice_pos, slice_edges):  # 放 slice
            new_edges[pos] = cubie

        for pos, cubie in zip(non_slice_pos, non_slice_cubies):  # 放非 slice
            new_edges[pos] = cubie

        s.edges_perm[:] = new_edges
        s.corners_ori[:] = 0
        s.edges_ori[:] = 0

        return s


    @classmethod
    @class_status('参考实现')
    def build_rotate_map(cls) -> dict:
        """
         面的邻接关系（6 * 4） (face, type, idx, reverse)
        从 SLICE_MAP 推导 ROTATE_MAP（返回 dict）。
        - SLICE_MAP 的项形如 ('U','row', None, maybe_reverse) 或者 ('F','col', None, maybe_reverse)
          这里的 idx 是 None 占位，实际旋转时要填 layer/index。
        """
        # 哪些面在轴的正/负一侧（约定：layer==0 对应正面）
        # 这里用 +1 表示正面（layer==0），-1 表示反面（layer==n-1）
        FACE_SIGN = {'U': 1, 'F': 1, 'R': 1, 'D': -1, 'B': -1, 'L': -1}

        # 明确定义「当旋转某个 face 时」，每个邻接面沿哪个 index 接触它（这是固定的魔方拓扑）
        # 这些值可直接来源于常用魔方约定
        CONTACT_IDX = {
            'U': {'F': 0, 'R': 0, 'B': 0, 'L': 0},
            'D': {'F': -1, 'L': -1, 'B': -1, 'R': -1},
            'F': {'U': -1, 'R': 0, 'D': 0, 'L': -1},
            'B': {'U': 0, 'L': 0, 'D': -1, 'R': -1},
            'L': {'U': 0, 'F': 0, 'D': 0, 'B': -1},
            'R': {'U': -1, 'B': 0, 'D': -1, 'F': -1},
        }

        SLICE_MAP = {
            'X': [
                ('U', 'col', None, False),
                ('B', 'col', None, True),  # B 需要 reverse !!!
                ('D', 'col', None, False),
                ('F', 'col', None, False),
            ],  # R/L转动：绕 x 轴转动（右/左） 切 col,U → B → D → F
            'Y': [
                ('F', 'row', None, False),
                ('R', 'row', None, False),
                ('B', 'row', None, True),
                ('L', 'row', None, False),
            ],  # U/D转动（上 ↔ 下） 切 row, F → R → B → L
            'Z': [
                ('U', 'row', None, False),
                ('R', 'col', None, False),
                ('D', 'row', None, True),  # col → row（方向变）要 reverse
                ('L', 'col', None, False),
            ]  # F/B转动（前 ↔ 后） 切 row/col,U → R → D → L
        }
        AXIS_FACE_WALK = {
            0: {  # X
                'U': lambda i, layer, n: (i, layer),
                'B': lambda i, layer, n: (n - 1 - i, n - 1 - layer),
                'D': lambda i, layer, n: (n - 1 - i, layer),
                'F': lambda i, layer, n: (i, layer),
            },
            1: {  # Y
                'F': lambda i, layer, n: (i, layer),
                'R': lambda i, layer, n: (i, layer),
                'B': lambda i, layer, n: (n - 1 - i, layer),
                'L': lambda i, layer, n: (n - 1 - i, layer),
            },
            2: {  # Z
                'U': lambda i, layer, n: (layer, i),
                'R': lambda i, layer, n: (i, n - 1 - layer),
                'D': lambda i, layer, n: (n - 1 - layer, n - 1 - i),
                'L': lambda i, layer, n: (n - 1 - i, layer),
            }
        }
        FACE_AXIS = {face: cls.AXIS_NAME[axis] for axis, pair in enumerate(cls.AXIS_FACE)
                     for face in pair}  # 哪个面属于哪个轴
        # 对同一轴，SLICE_MAP[axis] 给出邻接面顺序（环）
        # 对于"正侧面"（FACE_SIGN==1）按 SLICE_MAP 顺序生成
        # 对于"反侧面"（FACE_SIGN==-1）按 (0,3,2,1) 的顺序（这是与面朝向相关的常见置换）
        NEG_ORDER = [0, 3, 2, 1]

        rotate_map = {}
        # 为每个 face 构造 rot list
        for face in cls.FACES:
            axis = FACE_AXIS[face]  # X/Y/Z
            base = SLICE_MAP[axis]  # SLICE_MAP['Y'] = [('F','row',None,rev),...]
            sign = FACE_SIGN[face]

            # build a small lookup from neighbor face -> (type, default_rev from SLICE_MAP)
            # neighbor_info = {entry[0]: (entry[1], entry[3] if len(entry) > 3 else False) for entry in base}

            # choose order of neighbors depending on face sign
            if sign == 1:
                order_idx = [0, 1, 2, 3]
            else:
                order_idx = NEG_ORDER

            seq = []
            for idx in order_idx:
                neighbor_face, neigh_type, _, neigh_rev = base[idx]
                # actual index where neighbor touches this face (0 or -1), from CONTACT_IDX
                contact_i = CONTACT_IDX[face][neighbor_face]
                # reverse flag: combine neighbor's base reverse with any face-contact inversion
                # Using base rev is usually correct; CONTACT_IDX encodes geometric orientation (we used it above)
                rev = neigh_rev
                seq.append((neighbor_face, neigh_type, contact_i, rev))

            rotate_map[face] = seq

        return rotate_map


if __name__ == "__main__":
    # 测试已迁移到 test/test_cubie.py
    cube = CubieBase(n=3)
    cube.build_pruning_table()
