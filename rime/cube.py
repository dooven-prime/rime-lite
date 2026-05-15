from dataclasses import dataclass
from rime.base import class_property, class_cache, chainable_method, class_status
import numpy as np
import random, math
from collections import deque, defaultdict


class CubeGeometry:
    """Pure class-level geometric/combinatorial data provider for the Rubik's cube.

    Everything is derived from:
      - The face naming convention (_AXIS_FACE_MAP) — the only truly "hardcoded" element
      - Coordinate rules: corners = exactly 3 non-zero coords in {±1}³,
        edges = exactly 2 non-zero coords in {±1,0}³
      - Canonical XZ-plane ordering cycles (clockwise when viewed from +Y)

    All properties use @class_property for lazy caching. No instance state.
    No hardcoded position lists — every constant is derived from geometry.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # Face naming convention — the only "hardcoded" element
    # ═══════════════════════════════════════════════════════════════════════════
    # (axis, side) → face name. side=0 → POS_FACE (+axis normal), side=1 → NEG_FACE (-axis normal)
    _AXIS_FACE_MAP = {(0, 0): 'R', (0, 1): 'L',
                      (1, 0): 'U', (1, 1): 'D',
                      (2, 0): 'F', (2, 1): 'B'}

    # Canonical face order (used for indexing throughout)
    FACES = ['U', 'D', 'F', 'B', 'L', 'R']  # 面标识 上 下 前 后 左 右
    COLORS = ['W', 'Y', 'R', 'O', 'G', 'B']  # Rubiks 0:白色, 1:黄色, 2:红色, 3:橙色, 4:绿色, 5:蓝色

    # ═══════════════════════════════════════════════════════════════════════════
    # Coordinate system constants
    # ═══════════════════════════════════════════════════════════════════════════
    AXIS_VEC = np.eye(3, dtype=int)  # axis 0=X, 1=Y, 2=Z → unit vectors

    # ═══════════════════════════════════════════════════════════════════════════
    # Canonical XZ-plane ordering cycles (clockwise from +Y)
    # ═══════════════════════════════════════════════════════════════════════════
    # For corners (diagonal positions on XZ plane):
    #   (1,1)→(-1,1)→(-1,-1)→(1,-1) viewed clockwise from +Y
    _XZ_CYCLE = [(+1, +1), (-1, +1), (-1, -1), (+1, -1)]
    # For U/D-layer edges (axis-aligned positions on XZ plane):
    #   X+→Z+→X-→Z- clockwise from +Y
    _XZ_AXIS_CYCLE = [(+1, 0), (0, +1), (-1, 0), (0, -1)]

    # ═══════════════════════════════════════════════════════════════════════════
    # Local "up" direction for each face (conventional, for face_basis)
    # ═══════════════════════════════════════════════════════════════════════════
    FACE_UP = {
        'U': -AXIS_VEC[2],  # -Z: [0, 0, -1]
        'D': AXIS_VEC[2],  # +Z: [0, 0, 1]
        'F': AXIS_VEC[1],  # +Y: [0, 1, 0]
        'B': AXIS_VEC[1],  # +Y: [0, 1, 0]
        'R': AXIS_VEC[1],  # +Y: [0, 1, 0]
        'L': AXIS_VEC[1],  # +Y: [0, 1, 0]
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # Rotation strips — canonical CCW ordering of faces around each axis
    # ═══════════════════════════════════════════════════════════════════════════
    AXIS_STRIP = (
        ['U', 'F', 'D', 'B'],  # X: from +X, CCW, reference +Y
        ['F', 'R', 'B', 'L'],  # Y: from +Y, CCW, reference +Z
        ['U', 'L', 'D', 'R'],  # Z: from +Z, CW,  reference +X
    )  # CCW 视角,从 +axis 方向看过去,4 元环路,trip 顺序

    # ═══════════════════════════════════════════════════════════════════════════
    # Face → axis/side mappings
    # ═══════════════════════════════════════════════════════════════════════════

    @class_property('AXIS_FACE')
    def axis_face(cls):
        """AXIS_FACE[axis] = (POS_FACE, NEG_FACE).
        AXIS_FACE = [
        ('R', 'L'),  # X axis (0), X+ → R, X− → L
        ('U', 'D'),  # Y axis (1), Y+ → U, Y− → D
        ('F', 'B'),  # Z axis (2), Z+ → F, Z− → B
        ]  
    # YOLO 正轴方向,物理右手坐标一致, 反轴方向,物理右手坐标一致, 轴顺序 X/Y/Z 也符合常规, 但旋转方向约定为面向外法线的顺时针,与右手坐标系的逆时针相反"""
        return [
            (cls._AXIS_FACE_MAP[(0, 0)], cls._AXIS_FACE_MAP[(0, 1)]),
            (cls._AXIS_FACE_MAP[(1, 0)], cls._AXIS_FACE_MAP[(1, 1)]),
            (cls._AXIS_FACE_MAP[(2, 0)], cls._AXIS_FACE_MAP[(2, 1)]),
        ]

    @class_property('FACE_AXIS')
    def face_axis(cls):
        """face → (axis, side)."""
        return {face: (axis, side)
                for axis, pair in enumerate(cls.AXIS_FACE)
                for side, face in enumerate(pair)}

    @class_property('FACE_DEF_IDX')
    def face_idx(cls):
        """face → index in FACES."""
        return {f: i for i, f in enumerate(cls.FACES)}

    @classmethod
    def face_of(cls, axis: int, side: int) -> str:
        """(axis, side_sign) → face name. side=+1→POS, side=-1→NEG."""
        return cls.AXIS_FACE[axis][0 if side == 1 else 1]

    # ═══════════════════════════════════════════════════════════════════════════
    # Position vectors (derived from coordinate rules + canonical cycles)
    # ═══════════════════════════════════════════════════════════════════════════

    @class_property('CORNER_POS_SIGNS')
    def corner_pos_signs(cls):
        """8 corners in canonical order: U-layer CW then D-layer CW.
        Each corner has exactly 3 non-zero coords in {±1}³.
        CORNER_POS_SIGNS = [
        (+1, +1, +1),  # URF
        (-1, +1, +1),  # UFL
        (-1, +1, -1),  # ULB
        (+1, +1, -1),  # UBR
        (+1, -1, +1),  # DFR
        (-1, -1, +1),  # DLF
        (-1, -1, -1),  # DBL
        (+1, -1, -1),  # DRB
    ]  # 排序逻辑是魔方标准：从U层右前开始，顺时针绕一圈；D层类似（但右手调整）"""
        result = []
        for sx, sz in cls._XZ_CYCLE:
            result.append((sx, +1, sz))
        for sx, sz in cls._XZ_CYCLE:
            result.append((sx, -1, sz))
        return result

    @class_property('EDGE_POS_SIGNS')
    def edge_pos_signs(cls):
        """12 edges in canonical order: U-layer axis → middle diagonal → D-layer axis.
        Each edge has exactly 2 non-zero coords in {±1,0}³.
        EDGE_POS_SIGNS = [
        (+1, +1, 0),  # UR
        (0, +1, +1),  # UF
        (-1, +1, 0),  # UL
        (0, +1, -1),  # UB
        (+1, 0, +1),  # RF
        (-1, 0, +1),  # LF
        (-1, 0, -1),  # LB
        (+1, 0, -1),  # RB
        (+1, -1, 0),  # DR
        (0, -1, +1),  # DF
        (-1, -1, 0),  # DL
        (0, -1, -1),  # DB
        ]  # 排序逻辑：先 U 层四条边（UR UF UL UB），再中层四条边（RF LF LB RB），最后 D 层四条边（DR DF DL DB）"""
        result = []
        for sx, sz in cls._XZ_AXIS_CYCLE:
            result.append((sx, +1, sz))
        for sx, sz in cls._XZ_CYCLE:
            result.append((sx, 0, sz))
        for sx, sz in cls._XZ_AXIS_CYCLE:
            result.append((sx, -1, sz))
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # Derived position partitions
    # ═══════════════════════════════════════════════════════════════════════════

    @class_property('U_CORNER_POSITIONS')
    def u_corner_positions(cls):
        return tuple(i for i, (_, y, _) in enumerate(cls.CORNER_POS_SIGNS) if y == +1)

    @class_property('D_CORNER_POSITIONS')
    def d_corner_positions(cls):
        return tuple(i for i, (_, y, _) in enumerate(cls.CORNER_POS_SIGNS) if y == -1)

    @class_property('SLICE_POSITIONS')
    def slice_positions(cls):
        return tuple(i for i, (_, y, _) in enumerate(cls.EDGE_POS_SIGNS) if y == 0)

    @class_property('NON_SLICE_POSITIONS')
    def non_slice_positions(cls):
        return tuple(i for i, (_, y, _) in enumerate(cls.EDGE_POS_SIGNS) if y != 0)

    @class_property('FB_EDGE_POSITIONS')
    def fb_edge_positions(cls):
        return tuple(i for i, (_, _, sz) in enumerate(cls.EDGE_POS_SIGNS) if sz != 0)

    @class_property('NON_FB_EDGE_POSITIONS')
    def non_fb_edge_positions(cls):
        return tuple(i for i, (_, _, sz) in enumerate(cls.EDGE_POS_SIGNS) if sz == 0)

    @classmethod
    def edge_phase_classification(cls):
        """Return phase-active and phase-trivial edge indices (thin wrapper around class_properties)."""
        return {"phase_active": list(cls.FB_EDGE_POSITIONS),
                "phase_trivial": list(cls.NON_FB_EDGE_POSITIONS)}

    # ═══════════════════════════════════════════════════════════════════════════
    # Face vector properties
    # ═══════════════════════════════════════════════════════════════════════════

    @class_property('FACE_NORMAL')
    def face_normal(cls) -> dict[str, np.ndarray]:
        """face → outward normal vector (length-3 np.array).
        FACE_NORMAL = {
        'R': (1, 0, 0),
        'L': (-1, 0, 0),
        'U': (0, 1, 0),
        'D': (0, -1, 0),
        'F': (0, 0, 1),
        'B': (0, 0, -1),
        }  # 由 face naming convention 和 coordinate rules 推导,不是硬编码"""
        mapping = {}
        for axis, (pos_face, neg_face) in enumerate(cls.AXIS_FACE):
            mapping[pos_face] = cls.AXIS_VEC[axis].copy()
            mapping[neg_face] = -cls.AXIS_VEC[axis].copy()
        return mapping

    @class_property('FACE_DEF')
    def face_def(cls) -> dict[str, tuple]:
        """face → (normal, right, up) basis vectors."""
        mapping = {}
        for face, normal in cls.face_normal.items():
            up = cls.FACE_UP[face].copy()
            right = np.cross(normal, up)  # 面内基向量（右手系）
            mapping[face] = (normal, right, up)
        return mapping

    @classmethod
    def face_basis(cls, face: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Normalised (normal, u_dir, v_dir) basis for a face. u=row, v=col.
        确定局部行列方向,纯几何面内坐标系
        约定：
        - u_dir：面内向上（对应 row）
        - v_dir：面内向右（对应 col 正方向）
        - normal：面外法向
        右手系：normal × u_dir = v_dir"""
        normal = cls.face_normal[face].astype(float)
        u_dir = cls.FACE_UP[face].astype(float)
        u_dir /= np.linalg.norm(u_dir)  # 归一化
        v_dir = np.cross(normal, u_dir)
        v_dir /= np.linalg.norm(v_dir)
        assert np.dot(np.cross(u_dir, v_dir), normal) > 0
        return normal, u_dir, v_dir

    @class_property('FACE_NORMALS')
    def FaceNormals(cls) -> np.ndarray:
        """Face normal vectors as (6, 3) array, indexed by FACES order."""
        return np.array([cls.face_normal[f] for f in cls.FACES], dtype=float)

    # ═══════════════════════════════════════════════════════════════════════════
    # Face-cycle properties (corner / edge face names)
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def get_corner_faces(cls, pos_sign: tuple[int, int, int]) -> tuple[str, str, str]:
        """The 3 face names meeting at a corner, with U/D first, then clockwise."""
        sx, sy, sz = pos_sign
        idx = lambda s: 0 if s > 0 else -1  # 索引：正方向 -> 0, 负方向 -> n-1,每个轴取正方向的面（+1 取正，-1 取反）
        face_x = cls.AXIS_FACE[0][idx(sx)]  # R/L
        face_y = cls.AXIS_FACE[1][idx(sy)]  # U/D
        face_z = cls.AXIS_FACE[2][idx(sz)]  # F/B
        outward_normal = np.array([0, -sy, 0])
        cross = np.cross(outward_normal, np.array([sx, 0, 0]))
        if np.dot(cross, np.array([0, 0, sz])) > 0:
            return face_y, face_x, face_z
        return face_y, face_z, face_x

    @classmethod
    def get_edge_faces(cls, pos_sign: tuple[int, int, int]) -> tuple[str, str]:
        """The 2 face names meeting at an edge, U/D-first then right-hand rule.
        对于一个边块的位置符号 (sx, sy, sz)，其中一个坐标为0，另两个为 ±1
        顺序：先 Y 轴（U/D 优先），然后按右手规则排序剩余两个。
        """
        sx, sy, sz = pos_sign
        assert sx * sy * sz == 0 and sum(1 for s in (sx, sy, sz) if s != 0) == 2
        idx = lambda s: 0 if s > 0 else -1
        face_x = cls.AXIS_FACE[0][idx(sx)]
        face_y = cls.AXIS_FACE[1][idx(sy)]
        face_z = cls.AXIS_FACE[2][idx(sz)]
        if sy != 0:
            return (face_y, face_z) if sz != 0 else (face_y, face_x)
        return face_z, face_x

    @class_property('CORNER_FACE_CYCLE')
    def corner_face_cycle(cls):
        """Corner face-name triples in canonical order.
        确保 solved 时 U/D 在位置 0,第1位永远是 U 或 D（由 Y 生成角块, 
        对应：UFR, URB, UBL, ULF, DLF, DFR, DRB, DBL
         ('U', 'R', 'F'),0: URF
         ('U', 'F', 'L'),1: UFL
         ('U', 'L', 'B'),2: ULB
         ('U', 'B', 'R'),3: UBR
         ('D', 'F', 'R'),4: DFR
         ('D', 'L', 'F'),5: DLF
         ('D', 'B', 'L'),6: DBL
         ('D', 'R', 'B'),7: DRB
        """
        return [cls.get_corner_faces(pos_sign) for pos_sign in cls.CORNER_POS_SIGNS]

    @class_property('EDGE_FACE_CYCLE')
    def edge_face_cycle(cls):
        """Edge face-name pairs in canonical order.
        先 Y 轴（U/D 优先），然后按右手规则排序剩余两个。
         参考色放第一位（e.g., [U, R], [F, R]）
         生成角块, 对应：EDGE_INDEX_ORDER = [
        ('U', 'R'), ('U', 'F'), ('U', 'L'), ('U', 'B'),
        ('F', 'R'), ('F', 'L'), ('B', 'L'), ('B', 'R'),
        ('D', 'R'), ('D', 'F'), ('D', 'L'), ('D', 'B'),
        ]
        """
        return [cls.get_edge_faces(pos_sign) for pos_sign in cls.EDGE_POS_SIGNS]

    # ═══════════════════════════════════════════════════════════════════════════
    # Incidence and adjacency (pure geometry derived from positions + faces)
    # ═══════════════════════════════════════════════════════════════════════════

    @classmethod
    def corner_on_face(cls, corner_idx: int, face: str) -> bool:
        """Whether corner i lies on the given face."""
        sign = cls.CORNER_POS_SIGNS[corner_idx]
        axis, side = cls.face_axis[face]
        expected_sign = 1 if side == 0 else -1
        return sign[axis] == expected_sign

    @classmethod
    def edge_on_face(cls, edge_idx: int, face: str) -> bool:
        """Whether edge i lies on the given face."""
        sign = cls.EDGE_POS_SIGNS[edge_idx]
        axis, side = cls.face_axis[face]
        expected_sign = 1 if side == 0 else -1
        return sign[axis] != 0 and sign[axis] == expected_sign

    @classmethod
    def faces_of_corner(cls, corner_idx: int) -> list[str]:
        """The 3 face names meeting at corner i."""
        return [f for f in cls.FACES if cls.corner_on_face(corner_idx, f)]

    @classmethod
    def faces_of_edge(cls, edge_idx: int) -> list[str]:
        """The 2 face names meeting at edge i."""
        return [f for f in cls.FACES if cls.edge_on_face(edge_idx, f)]

    @classmethod
    def corners_affected_by_face(cls, face: str) -> list[int]:
        """Corner indices lying on a given face (always 4)."""
        return [c for c in range(8) if cls.corner_on_face(c, face)]

    @classmethod
    def edges_affected_by_face(cls, face: str) -> list[int]:
        """Edge indices lying on a given face (always 4)."""
        return [e for e in range(12) if cls.edge_on_face(e, face)]

    @classmethod
    def corner_orientation_axes(cls, corner_idx: int) -> tuple[list[str], list[np.ndarray]]:
        """The 3 face normals at a corner (for orientation computation).

        Used to determine how a face turn affects corner orientation.
        The orientation of a corner cubie is defined relative to which
        face sticker is on which face of the cube."""
        faces = cls.faces_of_corner(corner_idx)
        normals = [cls.face_normal[f].copy() for f in faces]
        return faces, normals

    # ═══════════════════════════════════════════════════════════════════════════
    # Incidence matrices (Bose-Mesner / association scheme data)
    # ══
    @class_property('CORNER_ADJACENCY')
    def build_corner_adjacency(cls):
        """Hamming-distance adjacency for 8 corners (Q₃ hypercube).
        On the 3-cube, corners differ in 1, 2, or 3 coordinate signs.
        This is the adjacency metric of the Q3 hypercube.
        Returns {'A': [A₀..A₃], 'v': [1,3,3,1]} — Bose-Mesner basis for the cp block.
        """
        verts = np.array(cls.CORNER_POS_SIGNS, dtype=int)
        A = []
        for d in range(4):
            Ad = np.zeros((8, 8), dtype=int)
            for i in range(8):
                for j in range(8):
                    if int(np.sum(verts[i] != verts[j])) == d:
                        Ad[i, j] = 1
            A.append(Ad)
        return {"A": A, "v": np.array([1, 3, 3, 1], dtype=int)}

    @class_property('EDGE_FACE_INCIDENCE')
    def build_edge_face_incidence(cls):
        """12×6 edge-face incidence matrix J.

        J[e,f] = 1 iff edge e lies on face f (each row=2 ones, each col=4 ones).
        Returns:
            J: (12, 6) int matrix
            edge_labels: list of 12 edge name strings
            face_labels: list of 6 face name strings (= FACES)
        """
        n_edges = len(cls.EDGE_POS_SIGNS)
        n_faces = len(cls.FACES)
        J = np.zeros((n_edges, n_faces), dtype=int)
        for e in range(n_edges):
            for f_idx, f in enumerate(cls.FACES):
                if cls.edge_on_face(e, f):
                    J[e, f_idx] = 1
        edge_labels = ['-'.join(cls.faces_of_edge(e)) for e in range(n_edges)]
        return {"J": J, "edge_labels": edge_labels, "face_labels": list(cls.FACES)}

    @class_property('CORNER_FACE_INCIDENCE')
    def build_corner_face_incidence(cls):
        """8×6 corner-face incidence matrix C.

        C[c,f] = 1 iff corner c lies on face f (each row=3 ones, each col=4 ones).
        Returns:
            C: (8, 6) int matrix
            corner_labels: list of 8 corner name strings
            face_labels: list of 6 face name strings (= FACES)
        """
        n_corners = len(cls.CORNER_POS_SIGNS)
        n_faces = len(cls.FACES)
        C = np.zeros((n_corners, n_faces), dtype=int)
        for c in range(n_corners):
            for f_idx, f in enumerate(cls.FACES):
                if cls.corner_on_face(c, f):
                    C[c, f_idx] = 1
        corner_labels = ['-'.join(cls.faces_of_corner(c)) for c in range(n_corners)]
        return {"C": C, "corner_labels": corner_labels, "face_labels": list(cls.FACES)}

    @class_property('FACE_ADJACENCY')
    def build_face_adjacency(cls):
        """6×6 face adjacency matrix. Adjacent = share an edge (not opposite).
        Two faces are adjacent if they share an edge.
        Opposite faces (U/D, F/B, R/L) do NOT share an edge.

        Returns:
            adj: (6, 6) bool matrix, adj[i,j] = True if faces i and j share an edge"""
        n_faces = len(cls.FACES)
        adj = np.zeros((n_faces, n_faces), dtype=bool)
        for e in range(len(cls.EDGE_POS_SIGNS)):
            fs = [cls.FACES.index(f) for f in cls.faces_of_edge(e)]
            adj[fs[0], fs[1]] = True
            adj[fs[1], fs[0]] = True
        return adj


# ── Trigger all CubeGeometry @class_property computation ──
# Existing code references cached names (CORNER_POS_SIGNS, EDGE_POS_SIGNS, etc.)
# directly; the descriptor only caches after first access.  Force computation now.
def _trigger_geometry_properties():
    class_property.trigger_properties(CubeGeometry)


_trigger_geometry_properties()


class CubeBase(CubeGeometry):
    '''
    逻辑 → 几何 → 群论 → 可视化,状态系统 World / State Space
    运算必须封闭
    表示不能混层
    不变量是结构给的,不是定义的
    贴纸世界是表示的一种投影，投影不可逆
    魔方是一个噪声极低、结构极硬的实验宇宙

    Inherits all geometric constants from CubeGeometry:
      AXIS_FACE, CORNER_POS_SIGNS, EDGE_POS_SIGNS, FACES, etc.
      — derived from face naming convention + coordinate rules, not hardcoded.

    Coordinate system:
      Right-handed Cartesian system.

    Rotation direction convention:
      A positive rotation `d` is defined as clockwise when viewed
      along the face outward normal (right-hand rule).
    '''

    def __init__(self, n: int = 3):
        """纯几何 / move 定义（无状态）"""
        self.n = n
        self.solved_idx = np.arange(6 * n * n, dtype=np.uint32).reshape(6, n, n)
        self.solved = self.solved(n)
        self.SOLVED_CORNERS_MAP = self.solved_corners_map()
        self.SOLVED_EDGES_MAP = self.solved_edges_map()
        self.SOLVED_CENTERS_MAP = self.solved_centers_map()

    @property
    def mid(self) -> int:
        return self.n // 2

    @property
    def center_layers(self) -> list:
        return self.center_layers_list(self.n)

    @staticmethod
    def idx_to_state(state_idx: np.ndarray) -> np.ndarray:
        """颜色视图"""
        n = state_idx.shape[1]
        return (state_idx // (n * n)).astype(np.uint8)

    @classmethod
    def solved(cls, n: int) -> np.ndarray:
        solved = np.zeros((6, n, n), dtype=np.uint8)
        for f in range(6):
            solved[f, :, :] = f
        return solved

    def is_solved(self, state: np.ndarray) -> bool:
        return bool(np.array_equal(state, self.solved))  # not (state ^ self.solved).any()

    @staticmethod
    def encode(state: np.ndarray) -> bytes:
        return np.ascontiguousarray(state, dtype=np.uint8).tobytes()

    @staticmethod
    def embedding(state_idx: np.ndarray) -> np.ndarray:
        """
        Transformer / GNN 相对坐标 relative[color,u,v]
        返回: (batch, 6*n*n, 3)
        """
        if state_idx.ndim == 3:
            state_idx = state_idx[None]  # 加 batch dim (1, 6, n, n)

        b, f, n, _ = state_idx.shape
        # 颜色归一化
        color = (state_idx // (n * n)).astype(np.float32) / 5.0  # (b, 6, n, n)
        # id = (state_idx % (n * n)).astype(np.float32) / (n * n)

        # 相对坐标网格 ∈ [-1, 1]
        grid = np.linspace(-1.0, 1.0, n)
        u, v = np.meshgrid(grid, grid)  # (n,n) for each face

        uv = np.stack([u, v], axis=-1)[None, None]  # (1,1,n,n,2)
        uv = np.broadcast_to(uv, (b, f, n, n, 2))  # 广播到(b,6,n,n,2)

        emb = np.concatenate([color[..., None], uv], axis=-1)  # (b,6,n,n,3)#,  id[...,None]
        return emb.reshape(b, -1, 3)  # (b, 6*n*n, 3)

    @staticmethod
    def get_data(state: np.ndarray, coords_def: list | tuple) -> tuple:
        '''把 piece 看成一个"颜色集合"，忽略朝向，只关心它是哪个 piece'''
        return tuple(sorted(state[f, r, c].tolist() for f, r, c in coords_def))

    @classmethod
    def get_colors(cls, state: np.ndarray) -> dict:
        """返回原来使用的 face->二维字符串颜色矩阵"""
        n = state.shape[1]
        face_stickers = cls.get_face_stickers(n=n)  # 返回 [(r, c, pos), ...] 按渲染顺序
        idx_color = {i: c for i, c in enumerate(cls.COLORS)}
        result = {}
        for fidx, face in enumerate(cls.FACES):
            # col_mat = np.vectorize(idx_color.get)(state[fidx, :, :])
            # result[face] = col_mat.tolist()  # 转为普通列表[[str,str]]
            mat = np.empty((n, n), dtype='<U1')
            coords = face_stickers[face]
            for (r, c, _), color_idx in zip(coords, state[fidx].flatten()):
                mat[r, c] = idx_color[color_idx]
            result[face] = mat.tolist()

        return result

    @classmethod
    def from_color(cls, cube_color: dict) -> np.ndarray:
        # 传入的 state 是面->二维列表的映射
        color_index = {color: i for i, color in enumerate(cls.COLORS)}
        n = len(cube_color)
        arr = np.zeros((6, n, n), dtype=np.uint8)
        for fidx, face in enumerate(cls.FACES):
            face_mat = cube_color[face]
            arr[fidx, :, :] = np.vectorize(color_index.get)(face_mat)
        return arr

    @classmethod
    def get_corners(cls, state: np.ndarray) -> np.ndarray:
        """
        返回 8 个角块的三颜色编号（按顺序）shape = (8, 3),
        角块位置： (face, row, col) 三元组的 3 个集合
        """
        res = np.empty((8, 3), dtype=state.dtype)
        for i, corner in enumerate(cls.corner_coords(n=state.shape[1])):
            # corner 是 [(face,row,col), ...]
            for j, (f, r, c) in enumerate(corner):
                res[i, j] = state[f, r, c]
        return res

    @classmethod
    def get_edges(cls, state: np.ndarray) -> np.ndarray:
        """返回 12 个角块的2颜色编号（按顺序）shape = (12,2)"""
        res = np.empty((12, 2), dtype=state.dtype)
        for i, edge in enumerate(cls.edge_coords(n=state.shape[1])):
            for j, (f, r, c) in enumerate(edge):
                res[i, j] = state[f, r, c]
        return res

    @classmethod
    def get_centers(cls, state: np.ndarray) -> np.ndarray:
        """Extract center sticker colors from state in canonical order."""
        coords = cls.center_coords(state.shape[1])
        return np.array([state[f, r, c] for f, r, c in coords], dtype=state.dtype)

    @classmethod
    def encode_state(cls, state: np.ndarray) -> np.ndarray:
        """48: 8*3+12*2,物理块不去重"""
        return np.concatenate([cls.get_corners(state).ravel(), cls.get_edges(state).ravel()]).astype(np.uint8)

    def solved_corners_map(self) -> dict:
        """
        角块的 cubie id
        用字典加速 lookup，建立 solved corner 的颜色集合 → index 映射
        忽略朝向，否则同一个块旋转后会被误认为不同块,角块的 twist 信息在贴纸级处理里丢失
        slot 0 为 reference （基准面）
        """
        solved = self.get_corners(self.solved)  # (8, 3) np.sort(, axis=1)
        return {frozenset(c): (pid, c) for pid, c in enumerate(solved)}

    def corner_ids_ori(self, state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        返回每个 corner 对应的 piece id（0~7）, corners_perm (8)
        perm 表示 piece 的重排，当前位置 i 的角块，原来是 solved 的哪一块？ 群作用矩阵里计算 twist
        corner_ori 不是物理量，是约定量，测不准
        """
        corners = self.get_corners(state)
        perm = np.empty(8, dtype=np.int8)
        ori = np.empty(8, dtype=np.int8)
        for i, c in enumerate(corners):
            pid, ref = self.SOLVED_CORNERS_MAP[frozenset(c)]
            perm[i] = pid
            for twist in range(3):
                rolled = np.roll(ref, -twist)
                if np.array_equal(rolled, c):
                    ori[i] = twist
                    break
            else:
                ori_raw = list(c).index(ref[0])  # 原始索引：0/1/2
                ori[i] = (-ori_raw) % 3
                print(f"{pid}:No matching twist found")

        # ori = (ori - ori[0]) % 3  # 全局 orientation gauge fix
        # ori = (3 - ori) % 3/ (- ori) % 3
        ori[-1] = (-ori[:-1].sum()) % 3  # 把 orientation 投影到合法子空间,修正最后一个角方向
        return perm, ori

    def solved_edges_map(self) -> dict:
        """
        标准顺序,依赖 solved_edges 的正确定义（顺序必须匹配参考色先）
        cubie id : ref  0/1
        """
        solved = self.get_edges(self.solved)  # (12, 2)
        edge_map = {}
        for pid in range(12):
            a, b = solved[pid]
            edge_map[(a, b)] = (pid, 0)  # forward 正向映射：标准颜色顺序 → id,ori[i] = 0
            edge_map[(b, a)] = (pid, 1)  # flipped 翻转映射：同一个块,ori[i] = 1
        return edge_map

    def solved_centers_map(self) -> dict:
        """Center identity map: orbit structure + solved-state colors.

        Returns dict:
          flat: np.ndarray — get_centers(self.solved), colors in center_coords order
          orbits: list[list[int]] — flat index groups per orbit (center_coords order)
          pos_to_orbit: list[tuple] — per flat index: (orbit_id, pos_in_orbit)
        """
        coords = self.center_coords(self.n)
        idx_map = {c: i for i, c in enumerate(coords)}
        rings = CubeBase.get_center_rings(self.n)
        orbits = []
        for fidx, face_rings in enumerate(rings):
            for ring in face_rings:
                orbits.append([idx_map[(fidx, r, c)] for r, c, _ in ring])

        centers = self.get_centers(self.solved)
        pos_to_orbit = [None] * len(centers)
        for oid, indices in enumerate(orbits):
            for pos, idx in enumerate(indices):
                pos_to_orbit[idx] = (oid, pos)
        return {'flat': centers, 'orbits': orbits, 'pos_to_orbit': pos_to_orbit}

    def edge_ids_ori(self, state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """ edges_perm  (12) 保留方向,按标准顺序"""
        edges = self.get_edges(state)  # current_edges
        perm = np.empty(12, dtype=np.int8)
        ori = np.empty(12, dtype=np.int8)
        for i, (a, b) in enumerate(edges):
            pid, o = self.SOLVED_EDGES_MAP[(a, b)]
            perm[i] = pid
            ori[i] = o
        ori[-1] = (-ori[:-1].sum()) % 2  # 修正最后一个边方向
        return perm, ori

    def orbit_perm(self, state: np.ndarray) -> list[np.ndarray]:
        """每个 orbit 内 center 贴纸的相对排列 (使用 SOLVED_CENTERS_MAP 中的 orbit 结构)."""
        m = self.SOLVED_CENTERS_MAP
        current = self.get_centers(state).astype(np.int32)

        result: list[np.ndarray] = []
        for oid, indices in enumerate(m['orbits']):
            if len(indices) <= 1:
                continue
            pieces = current[indices]
            order = np.argsort(pieces)
            rel = np.empty_like(order)
            rel[order] = np.arange(len(order))
            result.append(rel)
        return result

    def basic_generators(self) -> list:
        """基础生成元,逻辑层（axis, layer, direction）与几何层解耦，返回 move list,有限邻域 moves（减枝！！）"""
        moves = []
        for axis in range(3):
            for layer in self.center_layers:
                for direction in (-1, 1, 2):  # direction 只用 ±1，2 步可视为两步重复
                    moves.append((axis, layer, direction))
        return moves

    @classmethod
    def act_moves(cls, state: np.ndarray, moves: list | tuple):
        """
        连续作用,replace
        action space, action:群生成元
        (axis, layer, direction)
        s_{t+1} = T(s_t, a_t)
        """
        if not isinstance(moves, list):
            moves = [moves]
        for axis, layer, direction in moves:
            cls.rotate_core(state, axis, layer, direction)

    @staticmethod
    def invert_moves(moves: list[tuple]) -> list[tuple]:
        """move 的逆 将 moves 转成可还原的逆操作序列（反向 + 方向反）"""
        return [(axis, layer, -direction) for (axis, layer, direction) in reversed(moves)]

    @staticmethod
    def is_inverse(path: list[tuple], axis: int, layer: int, direction: int) -> bool:
        """
        is_redundant
        禁止与上一个动作在同一面（axis+layer）上连续转动且总效果为 0 mod 4
        两个动作加起来等价于什么都没做
        """
        # forbid immediate reversal
        if not path:
            return False
        pa, pl, pd = path[-1]
        if axis == pa and layer == pl:
            return (pd + direction) % 4 == 0
        return False

    @staticmethod
    def permutation_parity(perm: np.ndarray | list) -> int:
        """
        Return 0 for even, 1 for odd permutation
        0（偶置换）或 1（奇置换）
        """
        visited = np.zeros(len(perm), dtype=bool)
        parity = 0
        for i in range(len(perm)):
            if visited[i]:
                continue
            cycle_len = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                cycle_len += 1
            if cycle_len > 0:
                parity ^= (cycle_len - 1) & 1  # 奇长循环贡献奇置换 (cycle_len % 2)
        return parity

    @staticmethod
    def encode_perm(perm: list[int]) -> int:
        """
        perm: 长度 n 的排列，值域 0..n-1
        返回 [0, n!-1]
        """
        n = len(perm)
        code = 0
        factor = 1
        for i in range(n - 1, -1, -1):
            cnt = 0
            for j in range(i + 1, n):
                if perm[j] < perm[i]:
                    cnt += 1
            code += cnt * factor
            factor *= (n - i)
        return code

    @class_cache(key=lambda code, n: (code, n))
    @staticmethod
    def decode_perm(code: int, n: int) -> list[int]:
        """
        code: 0 .. n!-1
        返回 perm，值域 0..n-1
        """
        elems = list(range(n))
        perm = [0] * n

        for i in range(n):
            fact = math.factorial(n - 1 - i)
            idx = code // fact
            code %= fact
            perm[i] = elems.pop(idx)
            # perm[i], perm[i + idx] = perm[i + idx], perm[i]

        return perm

    @staticmethod
    def comb_to_index(bits: list[int], n: int, k: int) -> int:
        """
        bits: 长度 n 的 0/1，恰有 k 个 1
        返回 [0, C(n,k))
        """
        idx = 0
        r = k
        for i in range(n):
            if bits[i]:
                idx += math.comb(n - i - 1, r)
                r -= 1
                if r == 0:
                    break
        return idx

    @staticmethod
    def index_to_comb(idx: int, n: int, k: int) -> list[int]:
        """逆字典序的降序解码"""
        bits = [0] * n
        r = k
        for i in range(n):
            if r == 0:
                break
            c = math.comb(n - i - 1, r)
            if idx >= c:
                bits[i] = 1
                idx -= c
                r -= 1
        return bits


    @classmethod
    def get_vars(cls):
        """获取类中的变量名"""
        return [name for name, value in vars(cls).items() if
                not (callable(value) or isinstance(value, (classmethod, staticmethod)))]

    @staticmethod
    def center_layers_list(n: int) -> list:
        mid, c = divmod(n, 2)
        if c == 1:
            return list(range(-mid, mid + 1))  # 奇数阶：中心在 0
        return [i for i in range(-mid, mid + 1) if i != 0]

    @staticmethod
    def layer_index(layer: int, n: int) -> int:
        """数组索引空间"""
        mid, c = divmod(n, 2)
        layer_idx = layer + mid
        if c == 0 and layer >= mid:
            layer_idx -= 1
        return layer_idx

    @staticmethod
    def layer_to_logic(layer: int, n: int) -> float:
        """逻辑/拓扑坐标空间"""
        c = n % 2
        if c == 1:
            return float(layer)
        return layer - 0.5 if layer > 0 else layer + 0.5  # 偶数阶：整数 layer → 半整数坐标

    @staticmethod
    def layer_to_geom(layer: int, n: int) -> float:
        """几何模型空间"""
        return -n / 2 + 0.5 + layer

    @classmethod
    def face_rc_to_xyz(cls, face: str, r: int, c: int, n: int):
        """
        把某个面上的 row/col 映射到世界坐标系 XYZ 返回 [x,y,z]
        把离散拓扑嵌入到连续空间中保持方向一致性
        face 上的 row / col 方向（固定定义）
        约定：
        #   row 方向 = Y×normal,Z
        #   col 方向 = normal×row
         n = 5 [-2, -1, 0, 1, 2]
         n = 4 [-1.5, -0.5, 0.5, 1.5]
        """
        # 面中心
        k = (n - 1) / 2.0
        dr = k - r  # r 向下 → y 减小
        dc = c - k  # c 向右 → x 增大
        normal, right, up = cls.face_def[face]

        # 世界坐标,normal 是面中心，dc*right + dr*up2 扩展到局部坐标
        pos = normal + dc * right + dr * up
        if n % 2 == 1:  # 离散化,保证严格整数
            return np.round(pos).astype(int)
        return np.sign(pos) * np.floor(np.abs(pos) + 0.5).astype(int)  # 原点缺失,parity 成为全局约束

    @staticmethod
    def sticker_pos(normal, u_dir, v_dir, r: int, c: int, n: int) -> np.ndarray:
        """
         返回贴纸中心在世界坐标系中的 (x, y, z), world 连续浮点坐标
         与 face_rc_to_xyz 一致的面内基
         - 立方体中心在原点，坐标范围 [-center, center]
         - r, c: 从 0 到 n-1
         """
        center = (n - 1) / 2.0  # 连续浮点
        face_center = normal * center
        # 局部坐标映射到中心坐标 [-center, center]
        s_v = c - center  # col → right x:j
        s_u = r - center  # row → down y:i
        pos_rel = u_dir * s_u + v_dir * s_v
        return face_center + pos_rel  # float, 保留 ±0.5

    @classmethod
    def pos_to_face_rc(cls, pos: tuple, n: int) -> tuple:
        """lookup 直接查表  xyz → (face, r, c)"""

        best_face = None
        best_dot = -float('inf')

        for f, nvec in cls.face_normal.items():
            dot = np.dot(pos, nvec)
            if dot > best_dot:
                best_dot = dot
                best_face = f

        face = best_face

        normal, u_dir, v_dir = cls.face_basis(face)
        u = np.dot(pos, u_dir)  # projection onto row direction
        v = np.dot(pos, v_dir)  # projection onto col direction

        center = (n - 1) / 2.0
        r = int(round(u + center))  # u_dir → row
        c = int(round(v + center))  # v_dir → col
        if not (0 <= r < n and 0 <= c < n):
            raise ValueError(f"out of face: {face}, r={r}, c={c}")

        return cls.face_idx[face], r, c

    @class_cache(cache_name='_LAYER_CACHE', key=lambda axis, layer, n: (axis, layer, n))
    @classmethod
    def get_layer_stickers(cls, axis: int, layer: int, n: int = 3):
        """
        Returns a list of (fidx, r, c, pos) for stickers in the given layer along the axis.
        Assumes center at origin, layers from -x to x where x = (n-1)/2.
        """
        stickers = defaultdict(list)
        axis_vec = cls.AXIS_VEC[axis].astype(float)
        layer_coord = cls.layer_to_logic(layer, n)
        # R = cls.rot90_matrix(axis, 1)
        for idx, face in enumerate(cls.AXIS_STRIP[axis]):  # 已调整为统一 CCW 顺序
            normal, u_dir, v_dir = cls.face_basis(face)
            # normal_rot = R @ normal
            if abs(np.dot(normal, axis_vec)) > 1e-6:
                continue  # 整个面或不在该 layer
            for r in range(n):
                for c in range(n):
                    xyz = cls.sticker_pos(normal, u_dir, v_dir, r, c, n)  # 中间态
                    # k = int(round(np.dot(xyz, axis_vec)))
                    # xyz_rot= R @ xyz
                    if np.isclose(xyz[axis], layer_coord, atol=1e-6):  # 中心坐标,abs(xyz[axis] - layer) < 1e-6
                        stickers[face].append((r, c, xyz))

        return stickers

    @class_cache(cache_name='_STRIP_CACHE', key=lambda axis, layer, n: (axis, layer, n))
    @classmethod
    def strip_coords_from_axis(cls, axis: int, layer: int, n: int) -> list:
        """
          返回某 axis, face, layer 对应的条带坐标列表，已按中心原点计算
          返回: [(face, r, c), ...]  按 strip 顺序排列
          layer 在"世界坐标系"里定义
          row / col 在"face 局部坐标系"里定义
          strip 级别旋转 ≠ piece 级别置换
          几何排序 ≠ 拓扑顺序
        """
        strips = []
        axis_vec = cls.AXIS_VEC[axis].astype(float)
        face_stickers = cls.get_layer_stickers(axis, layer, n)
        for face, coords in face_stickers.items():
            if not coords:  # face_stickers.get(face, [])
                continue

            fidx = cls.face_idx[face]
            normal, u_dir, v_dir = cls.face_basis(face)
 
            strip_dir = np.cross(axis_vec, normal)
            strip_dir /= np.linalg.norm(strip_dir)  # 该面对应的旋转条带方向或法向量
            # 确定沿哪个方向 (v 或 u)，并计算 align
            align_u = np.dot(strip_dir, u_dir)
            align_v = np.dot(strip_dir, v_dir)
            if abs(align_u) > abs(align_v):
                key_dir = u_dir  # key = lambda x: x[0]  # r
                reverse = align_u < 0  # 如果 align <0,reverse 排序，使顺序沿局部正方向
            else:
                key_dir = v_dir  # key = lambda x: x[1]  # c
                reverse = align_v < 0
            # print('axis', axis, 'face', face, 'u', align_u, 'v', align_v, reverse)
            # coords_sorted = sorted(coords, key=lambda x: np.dot(x[2], strip_dir))
            coords_sorted = sorted(coords, key=lambda x: np.dot(x[2], key_dir), reverse=reverse)  # 世界坐标投影排序
            strip = [(fidx, r, c) for r, c, _ in coords_sorted]
            strips.append(strip)

        return strips


    @classmethod
    def rotate_slice(cls, state: np.ndarray, axis: int, layer: int, shift: int, n: int = None):
        """旋转一层, inplace,当前的 strip 机制：丢失了顺序信息"""
        if shift == 0:
            return
        n = n or state.shape[1]
        # 生成每一条 strip 的坐标列表 (f, r, c)
        strips = cls.strip_coords_from_axis(axis, layer, n)  # 获取每一面条带的坐标序列
        # 读取每条 strip 的值（list of lists）,by strip_coords
        vals = [[state[f, r, c] for (f, r, c) in strip] for strip in strips]
        # 循环环移,正向移位
        vals = vals[-shift:] + vals[:-shift]  # CCW rotation
        # 写回
        for strip, val in zip(strips, vals):
            for (f, r, c), v in zip(strip, val):
                state[f, r, c] = v

    @classmethod
    def rotate_core(cls, state: np.ndarray, axis: int, layer: int, direction: int):
        """
        inplace 版本
        生成元 move(axis, layer, dir), SE(3) 中旋转生成元在立方晶格上的离散表示
          state ∈ Sticker(SO(3))
          axis ∈ {0,1,2} 离散化的旋转轴方向（单位向量）: 'x', 'y', 'z'
          layer ∈ {..., -2, -1, 0, 1, 2, ...} 沿旋转轴法向方向的离散标量坐标
          dir ∈ {+1, -1, 2}  θ ∈ {π/2, -π/2, π} 离散化的旋转角 / 旋量大小
        贴纸态 ≠ CubieState（不可逆）
        """
        d = direction % 4
        if d == 0:
            return  # 旋转 0 次
        n = state.shape[1]
        mid = n // 2

        # 处理最外层面本体旋转，x轴 → R/L, y轴 → U/D ,z轴 → F/B
        if abs(layer) == mid:
            side = 0 if layer > 0 else 1  # layer == +mid → 使用几何正向面,[0]（pos face）
            dd = -d if side == 0 else d  # 方向修正：视角翻转补偿  d if face in ["U", "R", "F"] else -d
            face = cls.AXIS_FACE[axis][side]
            fidx = cls.face_idx[face]
            cls.rotate_inplace(state[fidx], dd)  # 使用的是「观察者正对该面」的顺时针定义
        # 中层处理
        cls.rotate_slice(state, axis, layer, shift=d, n=n)

    @classmethod
    def rotate_state(cls, state: np.ndarray, axis: int, layer: int, direction: int) -> np.ndarray:
        """
        纯函数版本：不修改传入 state，返回新状态 next_state 副本（已经应用旋转）。rotate_state 只存在于贴纸层
        用于 BFS/IDA*/并行扩展时的安全调用。区别实例方法"就地旋转"，完全独立
        """
        arr = state.copy()
        cls.rotate_core(arr, axis, layer, direction)
        return arr  # new_state

    @class_cache(cache_name='_FACE_CACHE', key=lambda n: n)
    @classmethod
    def get_face_stickers(cls, n: int):
        """sticker_pos_from_face,不依赖 axis / layer / strip，返回贴纸中心的 3D 世界坐标"""
        stickers = defaultdict(list)
        for face in cls.FACES:
            normal, u_dir, v_dir = cls.face_basis(face)
            # origin = normal * (n / 2)
            for r in range(n):
                for c in range(n):
                    pos = cls.sticker_pos(normal, u_dir, v_dir, r, c, n)
                    # p = origin + dx * (c - n / 2 + 0.5) + dy * (r - n / 2 + 0.5)
                    stickers[face].append((r, c, pos))  # 抽象网格顺序
        return stickers

    @classmethod
    def get_corner_stickers(cls, n: int) -> list:
        """
        不考虑面环路连续性,几何点本身不应该知道邻接
        """
        stickers = []
        for face in cls.FACES:
            normal, u_dir, v_dir = cls.face_basis(face)
            for r in (0, n - 1):
                for c in (0, n - 1):
                    pos = cls.sticker_pos(normal, u_dir, v_dir, r, c, n)
                    stickers.append((face, r, c, pos))
        return stickers

    @classmethod
    def get_edge_stickers(cls, n: int) -> list[tuple]:
        """
        返回所有 edge 贴纸:
        [(face, r, c, pos), ...]
        不考虑邻接 / 环路 / strip
        """
        stickers = []
        mid, c = divmod(n, 2)
        center = mid if c == 1 else mid - 1
        # 奇数阶选 layer=0（中心中线）,偶数阶选（偏左/下的中线）
        for face in cls.FACES:
            normal, u_dir, v_dir = cls.face_basis(face)
            # 四条边，去掉角
            for r, c in (
                    (0, center),  # 上边
                    (center, n - 1),  # 右边
                    (n - 1, center),  # 下边
                    (center, 0),  # 左边
            ):
                pos = cls.sticker_pos(normal, u_dir, v_dir, r, c, n)
                stickers.append((face, r, c, pos))
        return stickers

    @class_cache(cache_name='_CENTER_CACHE', key=lambda n: n)
    @classmethod
    def get_center_stickers(cls, n: int) -> list[tuple]:
        """
        返回每个面的中心贴纸坐标,6
        """
        mid, c = divmod(n, 2)  # 中心永远是几何中心
        cr = cc = mid if c == 1 else mid - 1  # 奇数取正中，偶数取偏左/上
        stickers = []
        for face in cls.FACES:
            normal, u_dir, v_dir = cls.face_basis(face)
            pos = cls.sticker_pos(normal, u_dir, v_dir, cr, cc, n)
            stickers.append((cls.face_idx[face], cr, cc, pos))  # 通常不需要 pos，直接返回坐标
        return stickers

    @class_cache(cache_name='_CENTER_RINGS_CACHE', key=lambda n: n)
    @classmethod
    def get_center_rings(cls, n: int) -> list[list[list[tuple]]]:
        """
        返回每个 face 的所有中心贴纸坐标（带 pos）
        返回结构: list[face_idx] -> list[rings] -> list[(r, c, pos)]
        - face_idx 0~5 对应 cls.FACES 顺序
        - 最内层 ring 通常是中心单块（n奇数时只有一个元素）
        """
        rings = []
        mid = n // 2
        max_dist = mid - 1
        for face in cls.FACES:
            normal, u_dir, v_dir = cls.face_basis(face)
            face_rings = [[] for _ in range(max_dist + 1)]  # 每个距离一个 ring
            # 遍历内层区域
            for r in range(1, n - 1):
                for c in range(1, n - 1):
                    dist = max(abs(r - mid), abs(c - mid))  # 计算到中心的曼哈顿距离
                    pos = cls.sticker_pos(normal, u_dir, v_dir, r, c, n)
                    face_rings[dist].append((r, c, pos))
            # for ring in face_rings:
            #     ring.sort(key=lambda x: (x[0], x[1]))# 按 row, col 排序
            rings.append(face_rings)
        return rings

    @class_cache(cache_name='CENTERS_CACHE', key=lambda n: n)
    @classmethod
    def center_coords(cls, n: int) -> list[tuple[int, int, int]]:
        """All center sticker coords in canonical order: per face 0..5, per ring innermost→outermost, row-major.

        For N=3: 6 stickers (1 fixed per face). For N=4: 24 (4 per face). For N=5: 54 (9 per face).
        """
        rings = cls.get_center_rings(n)
        coords = []
        for fidx, face_rings in enumerate(rings):
            for ring in face_rings:
                for r, c, _ in ring:
                    coords.append((fidx, r, c))
        return coords

    @class_cache(cache_name='EDGES_CACHE', key=lambda n: n)
    @classmethod
    def edge_coords(cls, n: int) -> list[list[tuple[int, int, int]]]:
        """
        返回固定顺序的 12 条边的贴纸坐标，按标准顺序：
        [[(face_idx, r, c), (face_idx, r, c)],
          ...
        ]
        生成魔方所有 central edges 的贴纸坐标,12组，每条 edge 两个贴纸
        奇：基于 3D 世界坐标 + EDGE_POS_SIGNS 的 edge 定义
        偶：顺序严格对应 EDGE_FACE_CYCLE 的标准顺序（UR, UF, ..., DB）
        """
        stickers = cls.get_edge_stickers(n)
        assert len(stickers) == 24, f"Expected 24 edge pieces, got {len(stickers)}"
        result = [[] for _ in range(len(cls.EDGE_POS_SIGNS))]
        edge_cycle = cls.edge_face_cycle()

        if n % 2 == 1:
            edges = {k: [] for k in cls.EDGE_POS_SIGNS}
            for face, r, c, pos in stickers:
                sign = tuple(np.sign(pos).astype(int).tolist())
                if sign in edges:
                    edges[sign].append((face, r, c))

            for eid, sign in enumerate(cls.EDGE_POS_SIGNS):
                group = edges[sign]
                if len(group) != 2:
                    raise ValueError(f"illegal edge {sign}: {len(group)}")
                face_order = {f: i for i, f in enumerate(edge_cycle[eid])}
                group.sort(key=lambda x: face_order[x[0]])
                result[eid] = [(cls.face_idx[f], r, c) for f, r, c in group]
        else:
            pos_groups = defaultdict(list)
            for face, r, c, pos in stickers:
                key = tuple(np.round(pos, decimals=0).astype(int))
                pos_groups[key].append((face, r, c))

            edge_groups = [g for g in pos_groups.values() if len(g) == 2]
            if len(edge_groups) != 12:
                raise ValueError(f"Expected 12 edge groups, got {len(edge_groups)}")

            face_pair_to_id = {frozenset(pair): idx for idx, pair in enumerate(edge_cycle)}
            for group in edge_groups:
                faces = frozenset(g[0] for g in group)
                eid = face_pair_to_id[faces]
                face_order = {f: i for i, f in enumerate(edge_cycle[eid])}
                group.sort(key=lambda x: face_order[x[0]])
                result[eid] = [(cls.face_idx[f], r, c) for f, r, c in group]

        assert len(result) == 12, f"Expected 12 edges, got {len(result)}"
        return result

    @class_cache(cache_name='CORNERS_CACHE', key=lambda n: n)
    @classmethod
    def corner_coords(cls, n: int) -> list[list]:
        """
        [[(face_idx, r, c), (face_idx, r, c), (face_idx, r, c)],
          ...
        ]
        xyz pos(center)-> corner_id
        8 个角法向量组合: 每个角由三个轴的正负组成,3轴各2方向
        signs = [(sx, sy, sz)
                 for sx in (+1, -1)
                 for sy in (+1, -1)
                 for sz in (+1, -1)]  # list(product([1, -1], repeat=3))
        定义基准：UFR
        corner_ori = 0   如果 U 或 D sticker 在 U/D 面
        corner_ori = 1   顺时针旋转
        corner_ori = 2   逆时针旋转
        """
        stickers = cls.get_corner_stickers(n)
        corners = {k: [] for k in cls.CORNER_POS_SIGNS}  # 8 个角

        for face, r, c, pos in stickers:
            signs = tuple(np.sign(np.round(pos, decimals=5)).astype(int))
            corners[signs].append((face, r, c))

        result = []
        face_cycle = cls.corner_face_cycle()
        for cid, sign in enumerate(cls.CORNER_POS_SIGNS):
            group = corners[sign]
            if len(group) != 3:
                raise ValueError(f"illegal corner {sign}: {len(group)}")

            # Order by pre-computed corner face cycle (CW, U/D-first)
            face_order = {f: i for i, f in enumerate(face_cycle[cid])}
            group.sort(key=lambda x: face_order[x[0]])

            result.append([(cls.face_idx[f], r, c) for f, r, c in group])

        assert len(result) == 8, f"Expected 8 corners, got {len(result)}"
        return result

    @staticmethod
    def rotate_inplace(mat: np.ndarray, direction: int = 1) -> None:
        """
        rotate square matrix mat by direction*90 degrees clockwise.
        dir_sign: integer (positive/negative allowed). direction % 4 gives action:
          0 -> no-op
          1 -> 90 deg CW
          2 -> 180 deg
          3 -> 270 deg CW (or 90 CCW)
        The function mutates mat and returns None.
        和 rotate_coord 的旋转方向是完全一致的，都是顺时针（CW）。
        """
        dir_sign = direction % 4
        if dir_sign == 0:
            return
        elif dir_sign == 1:
            mat[:] = np.flip(mat.T, axis=1)  # 90 CW : transpose + flip LR
        elif dir_sign == 2:
            mat[:] = np.flip(np.flip(mat, axis=0), axis=1)  # 180 : flip LR + flip UD
        elif dir_sign == 3:  # i.e. 270 CW = 90 CCW
            mat[:] = np.flip(mat.T, axis=0)  # 90 CCW : transpose + flip UD
        else:
            raise ValueError(f"Invalid direction:{direction}")

    @staticmethod
    def rotate_coord(coord, axis: int, dir_sign: int = 1):
        """
        直接对一个3D坐标点[x, y, z]应用90度旋转，返回新坐标
        支持 cw (1) 和 ccw (-1) 的坐标旋转 right-hand
        dir_sign = 1 表示CW，dir_sign = -1 表示CCW
        """
        x, y, z = coord
        if axis == 0:  # X (R/L)  around x
            if dir_sign == 1:  # cw
                return [x, z, -y]
            else:  # ccw
                return [x, -z, y]
        elif axis == 1:  # Y (U/D)
            if dir_sign == 1:
                return [-z, y, x]
            else:
                return [z, y, -x]
        elif axis == 2:  # Z (F/B)
            if dir_sign == 1:
                return [y, -x, z]
            else:
                return [-y, x, z]
        raise ValueError("Invalid axis")

    @staticmethod
    def rot90_matrix(axis: int, dir: int) -> np.ndarray:
        """
        生成一个3x3的旋转矩阵,dir = +1 表示逆时针（CCW，从轴正方向看），dir = -1 表示顺时针（CW）
        axis: 0=x, 1=y, 2=z
        k: +1 = CCW, -1 = CW （从轴正方向看 +axis）
        """
        assert dir in (+1, -1)
        if axis == 0:  # X
            return np.array([
                [1, 0, 0],
                [0, 0, -dir],
                [0, dir, 0],
            ])
        if axis == 1:  # Y
            return np.array([
                [0, 0, dir],
                [0, 1, 0],
                [-dir, 0, 0],
            ])
        if axis == 2:  # Z
            return np.array([
                [0, -dir, 0],
                [dir, 0, 0],
                [0, 0, 1],
            ])
        raise ValueError(axis)

    @staticmethod
    def rotation_matrix(angle: tuple | np.ndarray) -> np.ndarray:
        # --- 合成基本旋转矩阵,整体旋转或欧拉角旋转 ---
        ax, ay, az = angle
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(ax), -np.sin(ax)],
            [0, np.sin(ax), np.cos(ax)]
        ])
        Ry = np.array([
            [np.cos(ay), 0, np.sin(ay)],
            [0, 1, 0],
            [-np.sin(ay), 0, np.cos(ay)]
        ])
        Rz = np.array([
            [np.cos(az), -np.sin(az), 0],
            [np.sin(az), np.cos(az), 0],
            [0, 0, 1]
        ])
        if np.abs(np.abs(ay) - np.pi / 2) < 1e-6:
            print(f"Near gimbal lock! ay={ay} near ±90°")
        return Rz @ Ry @ Rx  # 从右向左执行，实际顺序是 X -> Y -> Z

    @class_property('ROTATION_MATRICES')
    def rotation_matrices(cls) -> np.ndarray:
        """
        生成所有：3x3 正交矩阵，直接用于坐标变换,24 个 SO(3) 旋转
        立方体的 24 个旋转矩阵 (SO(3) 部分, det = +1)
        """
        # rot_x_90 = CubeBase.rot90_matrix(0, 1)
        # rot_y_90 = CubeBase.rot90_matrix(1, 1)
        # rot_z_90 = CubeBase.rot90_matrix(2, 1)
        # R = rz @ ry @ rx
        mats = []
        import itertools
        for perm in itertools.permutations(range(3)):
            for signs in itertools.product([-1, 1], repeat=3):
                M = np.zeros((3, 3), dtype=np.int8)
                for i, j in enumerate(perm):
                    M[i, j] = signs[i]
                if abs(np.linalg.det(M) - 1.0) < 1e-8 and np.allclose(M @ M.T, np.eye(3), atol=1e-8):
                    mats.append(M)

        mats.sort(key=lambda M: -int(np.linalg.det(M)))
        return np.array(mats)  # 24 个

    @class_property('SYMMETRY_MATRICES')
    def symmetry_matrices(cls) -> np.ndarray:
        """
        生成完整的 48 个立方体对称矩阵（24 旋转 + 24 镜像）
        每个矩阵 M: 3×3 带符号置换矩阵, det = ±1
        """
        rot_mats = cls.rotation_matrices  # (24, 3, 3)
        mirror = np.diag(np.array([1, 1, -1], dtype=np.int8))
        sym_mats = []
        for R in rot_mats:
            sym_mats.append(R)
            sym_mats.append(mirror @ R)  # 镜像版本
        return np.array(sym_mats)  # shape: (48, 3, 3)

    @classmethod
    def apply_rotation(cls, state: np.ndarray, R: np.ndarray):
        """
        对整个 sticker 数组应用 3x3 旋转矩阵 R（坐标变换）
        - state: (6, n, n) 贴纸数组
        - R: 3x3 旋转矩阵
        返回旋转后的 sticker
        把每个 sticker 的位置 (x,y,z) 应用 R 变换，然后映射回新 face/row/col
        """
        n = state.shape[1]
        new_state = np.zeros_like(state)
        face_stickers = cls.get_face_stickers(n=n)
        for fidx, face in enumerate(cls.FACES):
            for r, c, xyz in face_stickers[face]:
                xyz_rot = R @ xyz
                xyz_rot = tuple(np.round(xyz_rot).astype(int))
                new_f, new_r, new_c = cls.pos_to_face_rc(xyz_rot, n)
                new_state[new_f, new_r, new_c] = state[fidx, r, c]
        return new_state

    @classmethod
    def normalize_align(cls, state: np.ndarray, max_depth: int = 8):
        """
        使用 BFS 遍历 layer=0 旋转，使 U 和 F 面中心对齐
        角块保持不动
        返回：
        - new_state: 对齐后的 state
        - move_list: 初步旋转列表 [(axis, layer, dir), ...]
        """
        n = state.shape[1]
        mid = n // 2

        U = cls.face_idx['U']  # 0
        F = cls.face_idx['F']  # 2

        solved = cls.solved(n=n)
        target_u = solved[U, mid, mid]
        target_f = solved[F, mid, mid]
        if state[U, mid, mid] == target_u and state[F, mid, mid] == target_f:
            return state.copy(), []

        # 只绕 xyz 三个轴做 layer=0 旋转
        moves = [(axis, 0, dir) for axis in [0, 1, 2] for dir in [1, 2, -1]]

        q = deque()
        q.append((state.copy(), []))
        visited = set()
        visited.add(tuple(state.flatten()))

        while q:
            current_state, move_list = q.popleft()
            if len(move_list) > max_depth:
                continue
            # 检查目标 U/F 对齐
            if current_state[U, mid, mid] == target_u and current_state[F, mid, mid] == target_f:
                return current_state, move_list

            # 遍历所有 layer=0 的旋转
            for move in moves:
                new_state = cls.rotate_state(current_state, *move)
                state_key = tuple(new_state.flatten())
                if state_key not in visited:
                    visited.add(state_key)
                    q.append((new_state, move_list + [move]))

        raise ValueError("Cannot align U/F faces")

    @class_property('SYMMETRY_INVERSE_ID')
    def symmetry_inverse_id(cls) -> np.ndarray:
        """symmetry_inverse_id[i] = j 表示第 i 个对称的逆是第 j 个"""
        mats = cls.symmetry_matrices
        inv = np.zeros(48, dtype=np.int8)
        for i, M in enumerate(mats):
            MT = M.T
            for j, N in enumerate(mats):
                if np.array_equal(MT, N):
                    inv[i] = j
                    break
        return inv

    @classmethod
    def apply_symmetry(cls, state: np.ndarray, sym_id: int) -> np.ndarray:
        """将第 sym_id 种对称操作作用于贴纸状态 (6, n, n)"""
        M = cls.symmetry_matrices[sym_id]  # (3, 3)
        n = state.shape[1]
        mid = (n - 1) / 2.0
        new_state = np.zeros_like(state)

        for old_fidx in range(6):
            old_face = cls.FACES[old_fidx]
            normal_old = cls.face_normal[old_face]
            normal_new = M @ normal_old
            # 通过法向量匹配找到新面
            new_fidx = None
            for fidx, face in enumerate(cls.FACES):
                if np.array_equal(normal_new, cls.face_normal[face]):
                    new_fidx = fidx
                    break
            assert new_fidx is not None, f'sym {sym_id}: face {old_face} normal not matched'
            # 计算面内 2D 变换: (dr, dc) -> (dr_new, dc_new)
            # pos_new = M @ pos_old  ⇒  u_new·dr_new + v_new·dc_new = Mu·dr + Mv·dc
            _, u_old, v_old = cls.face_basis(old_face)
            _, u_new, v_new = cls.face_basis(cls.FACES[new_fidx])
            Mu, Mv = M @ u_old, M @ v_old
            a, b = np.dot(Mu, u_new), np.dot(Mv, u_new)  # dr 的 u_new 分量 + dc 的 u_new 分量
            c, d = np.dot(Mu, v_new), np.dot(Mv, v_new)  # dr 的 v_new 分量 + dc 的 v_new 分量
            # 应用变换到每个贴纸
            for r in range(n):
                for col in range(n):
                    dr, dc = r - mid, col - mid
                    r_new = int(round(mid + a * dr + b * dc))
                    c_new = int(round(mid + c * dr + d * dc))
                    if 0 <= r_new < n and 0 <= c_new < n:
                        new_state[new_fidx, r_new, c_new] = state[old_fidx, r, col]
        return new_state


@dataclass(frozen=True)
class ActionToken:
    axis: int
    layer: int  # layer=side*mid
    direction: int

    @property
    def key(self) -> tuple:
        return self.axis, self.layer, self.direction

    def invert(self) -> 'ActionToken':
        return ActionToken(axis=self.axis, layer=self.layer, direction=-self.direction)

    @classmethod
    def identity(cls) -> "ActionToken":
        return cls(0, 0, 0)

    @classmethod
    def from_path(cls, path: list[tuple] | tuple) -> list['ActionToken']:
        """从三元组快速创建"""
        if not path:
            return [ActionToken.identity()]
        if isinstance(path, tuple):
            return [cls(*path)]
        return [cls(*t) for t in path]

    @class_cache('BASIC_MOVES', key=lambda n=3: n)
    @classmethod
    def basic_generators(cls, n: int = 3) -> list['ActionToken']:
        """基础生成元,逻辑层（axis, layer, direction）与几何层解耦"""
        center_layers = CubeBase.center_layers_list(n)
        moves = []
        for axis in range(3):
            for layer in center_layers:
                for direction in (-1, 1, 2):  # direction 只用 ±1，2 步可视为两步重复
                    moves.append(cls(axis, layer, direction))
        return moves

    @classmethod
    def from_cubie_move(cls, axis: int, side: int, direction: int, n: int) -> 'ActionToken':
        """
        side == 0 表示中心层转动：
        - 奇数阶：layer = 0（物理中心）
        - 偶数阶：layer = -1（约定表示中心 slice）
        """
        mid, c = divmod(n, 2)
        if side == 0:
            layer = 0 if c == 1 else -1
        else:
            layer = side * mid
        return cls(axis=axis, layer=layer, direction=direction)

    def to_cubie_move(self, n: int = 3) -> tuple | None:
        """
        side
        最外层 → ±1
        中心层 → 0（奇数:0, 偶数:-1）
        其他中间层 → None
        """
        mid, c = divmod(n, 2)
        side = None
        if abs(self.layer) == mid:
            side = 1 if self.layer > 0 else -1
        if self.layer == 0 or (c == 0 and self.layer == -1):
            side = 0
        if side is None:
            return None
        dir_norm = self.direction % 4
        if dir_norm == 3:
            dir_norm = -1
        return self.axis, side, dir_norm

    @classmethod
    def transform(cls, move: str, n: int = 3) -> 'ActionToken':
        """
        解析层 Human Move String → transform → sticker simulation（仅用于构表）
        通用 NxN 解析，支持标准记法：
            U, U', U2
            R, L, F, B, D
            Rw, Rw', Rw2, Uw, Fw ...
            2Rw, 3Uw',2Rw2,3U,3Uw',2Fw2  等 |A| = 18
        返回实际执行的 primitive move 列表：[(axis, layer, direction), ...]
        side:
            0 → 正轴面 (layer > 0)
            1 → 负轴面 (layer < 0)
        """
        if not move:
            raise ValueError("Move string cannot be empty")

        mid, c = divmod(n, 2)
        move_tmp = move
        turn_times = 1
        direction = 1
        import re
        # --- 解析方向 ---
        if move_tmp.endswith("2"):
            turn_times = 2
            move_tmp = move_tmp[:-1]

        if move_tmp.endswith("'"):
            direction = -1
            move_tmp = move_tmp[:-1]

        # --- 中心层 M/E/S ---
        m_mid = re.match(r"([MES])$", move_tmp)
        if m_mid:
            mid_face = m_mid.group(1)
            axis = {'M': 0, 'E': 1, 'S': 2}[mid_face]
            layers = [0]
        else:
            # --- 正则解析宽度（前缀数字）---
            m = re.match(r"(\d*)([URFDLB])(w?)$", move_tmp)
            if not m:
                raise ValueError(f"Cannot parse move: {move}")

            width_txt, face, wide_flag = m.groups()
            if face not in CubeGeometry.FACES:
                raise ValueError(f"Unknown face: {face}")

            # 宽度：无数字 → 默认 1；如果有 'w' 则默认 = 2
            if width_txt:
                width = int(width_txt)
                if width < 1 or width > n:
                    raise ValueError(f"Width {width} exceeds cube order {n}")
            else:
                width = 2 if wide_flag else 1

            axis, side = CubeGeometry.face_axis[face]

            if wide_flag or width != 1:  # 宽层：使用宽度数字
                if c == 1 and width == 0:  # 中心层
                    layer_abs = 0
                else:
                    layer_abs = (mid - width + 1) if side == 0 else -(mid - width + 1)
                layers = [layer_abs]
            else:
                layers = [mid if side == 0 else - mid]

        return cls(axis, layers[0], direction * turn_times)

    def embedding(self, n: int = 3) -> np.ndarray:
        """
        动作的几何性质，几何 embedding
        axis:      0,1,2 (X,Y,Z)
        layer:     -mid .. +mid
        direction: -1 (逆90), 2 (180), +1 (顺90)
        n:         魔方阶数

        返回: shape (9,) 或 (7,) 的向量
        """
        dir_norm = self.direction % 4
        if dir_norm == 0:
            raise ValueError(f"Invalid direction:{self.direction}")

        mid = n // 2

        # 1. axis one-hot (3 dim)
        axis_oh = np.zeros(3)
        axis_oh[self.axis] = 1.0

        # 2. depth ∈ [-1, 1], coset 内 vs coset 间作用强度
        depth = self.layer / mid
        # layer_embed = np.array([np.sin(depth * np.pi), np.cos(depth * np.pi)])

        # 3. direction one-hot (3 dim)，更易学习
        dir_idx = dir_norm - 1
        dir_oh = np.zeros(3)
        dir_oh[dir_idx] = 1.0

        # 4. outer-ness: 1=最外层,是否触发 coset 跳变
        is_outer = 1.0 if abs(self.layer) == mid else 0.0
        # distance_to_center = 1.0 - abs(self.layer) / mid

        # 组合
        return np.concatenate([
            axis_oh,  # 3
            [depth],  # 1
            dir_oh,  # 3
            [is_outer]  # 1
        ])  # total 8 dim

    def __add__(self, other) -> list["ActionToken"]:
        """combine_with 列表组合"""
        if isinstance(other, list):
            return [self] + other
        elif isinstance(other, ActionToken):
            return [self, other]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __neg__(self):
        return self.invert()

    def __hash__(self):
        return hash(self.key)

    def __str__(self) -> str:
        """标准魔方记法，与 transform() 互逆:
        外层: U/U'/U2, R/R'/R2, F/F'/F2, D/D'/D2, L/L'/L2, B/B'/B2
        中心层: M/M'/M2, E/E'/E2, S/S'/S2
        宽层: 2Rw/2Rw'/2Rw2 等
        约定：
          - 对于正轴面（layer > 0）: 外侧第1层 =   mid,  第2层 =   mid-1, ...
          - 对于负轴面（layer < 0）: 外侧第1层 =  -mid,  第2层 =  -mid+1, ...
        """
        if self.direction == 0:
            return 'I'  # identity
        dir_norm = self.direction % 4
        pos_face, neg_face = CubeGeometry.axis_face[self.axis]
        # 判断 layer 属于哪个面 (基于 n=3 的约定: mid=1, layer=±1/0)
        # 对于一般 n: |layer| == mid → 外层, layer=0 → 中心层, 其他 → 宽层
        n_est = max(3, abs(self.layer) * 2 + 1)  # 从 |layer| 估算 n
        mid, c = divmod(n_est, 2)
        is_outer = abs(self.layer) == mid
        is_center = (c == 1 and self.layer == 0)
        suffix = '2' if dir_norm == 2 else ("'" if dir_norm == 3 else '')

        if is_outer:
            face = pos_face if self.layer > 0 else neg_face
        elif is_center:  # 中心层（M/E/S）不输出宽度数字
            face = ['M', 'E', 'S'][self.axis]
        else:  # 宽层: |layer| < mid → 从正面算起第 (mid - |layer|) 层 = width
            k = mid - abs(self.layer) + 1
            face = pos_face if self.layer > 0 else neg_face
            return f"{k}{face}w{suffix}"

        return f"{face}{suffix}"

    def __repr__(self) -> str:
        return f"ActionToken({self})"

    @staticmethod
    def invert_moves(moves: list['ActionToken']) -> list['ActionToken']:
        """move 的逆 将 moves 转成可还原的逆操作序列（反向 + 方向反）"""
        return [m.invert() for m in reversed(moves)]


if __name__ == "__main__":
    pass
