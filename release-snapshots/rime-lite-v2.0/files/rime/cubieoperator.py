"""Rubik-specific numerical spectral and direct-transport engine.

Legacy module flow (non-normative):
  SpectralStructure (block helper) -> CubieSpectralOperator (numerics)
  -> SlowDynamics (dynamics)

Current ownership:
  Paper I: averaging-operator spectral registration.
  Paper II: QH sectors and direct transport.
  Paper III: projected-composition audits live outside this class.

Registered finite data (module-scoped, not theorem premises):
  6 layers numerically matched to displayed labels 1 - k/9,
  k in {0,1,2,3,4,6}
  9 joint sectors from the commuting QH algebra
  10 transport edges (undirected), S6 is the main hub

Usage:
    cso = CubieSpectralOperator.from_gens_dict(CubieMove.prim_moves())
    P = cso.layer_projector(0.777778)
    sec = cso.center_decomposition()   # 9 sectors
"""

from rime.cubie import CubieMove, N_GENERATORS, TOTAL_DIM, BLOCK_RANGES
from rime.base import setup_utf8_stdout
from rime.helpers import is_in_qsqrt5, is_rational_form
from rime.spectral_utils import block_set
import numpy as np

setup_utf8_stdout()

# ═══════════════════════════════════════════════════════════════════════════════
# Numerical precision constants for the declared registrations
# ═══════════════════════════════════════════════════════════════════════════════
SPECTRAL_DECIMALS = 6  # rounding precision for spectral layer keys (canonical, fixed)
CENTER_CLUSTER_TOL = 1e-8  # center diagonalization clustering tolerance
TOL_KAPPA = 1e-6  # κ zero-threshold: logm numerical noise ~1e-6


class CubieSpectralOperator:
    """Numerical spectral operator for the Rubik representation.

    After construction, _frozen=True — spectral identity is immutable.
    All heavy computations (logm, commutant) are cached.

    Usage:
        cso = CubieSpectralOperator(n=18)
        cso.summary()
        P = cso.projector(0.777778)
        h_ops, labels = cso.build_h_operators()
        field = cso.classify_field()
    """

    def __init__(self, n: int = N_GENERATORS, generators: dict | None = None, tol: float = 1e-6, seed: int = 42):
        self.n = n
        self.tol = tol
        self.seed = seed
        self.rho_moves = generators or self.__class__.rho_moves(n)
        rho_gen = [rho for _, rho, *_ in self.rho_moves.values()]
        self.A = np.array(sum(rho_gen) / len(rho_gen), dtype=np.complex128)  # A = (1/|S|) Σ ρ(s) 平均算子
        assert np.allclose(self.A, self.A.T.conj(), rtol=tol, atol=tol), "A is not Hermitian"
        self.w, self.V = np.linalg.eigh(self.A)  # 谱分解: A = Σ λ_i P_i
        idx = np.argsort(-self.w)  # 降序: λ₁ > λ₂ > ...
        self.w = self.w[idx]
        self.V = self.V[:, idx]
        self._compute_spectral_layers()

        # Lazy init
        self._ss = None
        self._transport_tensor_cache = None

        # All caches are permanent — no invalidation, no force_recompute. — 全永久，不失效
        self._pg_cache = {}  # lam → (projected_gens, d)
        self._cb_cache = {}  # lam → (comm_basis, comm_dim)
        self._full_comm_cache = None  # full 228-dim commutant
        self._lie_gens_cache = None  # A_g = log ρ(g)
        self._frozen = True  # spectral identity is now immutable 谱身份锁定

    # ═══════════════════════════════════════════════════════════════
    # Spectral layer construction
    # ═══════════════════════════════════════════════════════════════

    def _compute_spectral_layers(self) -> None:
        """Cluster eigenvalues by SPECTRAL_DECIMALS → {lam: {dim, projector}}.

        SPECTRAL_DECIMALS is a canonical fixed value, not affected by self.tol.
        """
        w_rounded = np.round(self.w, decimals=SPECTRAL_DECIMALS)
        unique_w = np.unique(w_rounded)
        self.lambda_layers = unique_w
        self._layers = {}
        for lam in unique_w:
            mask = np.abs(self.w - lam) < self.tol
            dim = int(np.sum(mask))
            V_lam = self.V[:, mask]
            P_lam = V_lam @ V_lam.T.conj()  # 谱投影算子
            self._layers[float(lam)] = {'dim': dim, 'projector': P_lam, 'eigenvalue': float(np.mean(self.w[mask]))}

        # 慢/快分裂 — 数值实验用
        self.dim_const = int(np.sum(np.abs(self.w - 1.0) < self.tol))
        self.dim_slow = int(np.sum((self.w >= 2 / 3 - self.tol) & (np.abs(self.w - 1.0) >= self.tol)))
        mask_fast = self.w < 2 / 3 - self.tol
        self.rho_fast = float(np.max(np.abs(self.w[mask_fast]))) if np.any(mask_fast) else 0.0

    # ═══════════════════════════════════════════════════════════════
    # Constructors
    # ═══════════════════════════════════════════════════════════════

    @classmethod
    def rho_moves(cls, n=N_GENERATORS):
        """Filter ρ representation dict by generator count n.

        Supports n: 18 (full), 16, 12 (QT only), 10, 9, 8, 6 (HT only), 4, 3, 2.
        n=21 additionally includes slice moves.
        Returns {move_key: (CubieMove, rho_matrix)}.
        """
        if n > 18:
            all_moves = CubieMove.prim_moves().copy()
            if n == 21:
                all_moves.update(CubieMove.slice_moves())
                return {k: (mv, mv.rho().astype(np.complex128))
                        for k, mv in all_moves.items()}

        # move_key = (axis, side, direction): axis∈{0,1,2}, side∈{±1}, dir∈{-1,1,2}
        f = {18: lambda k: True,
             16: lambda k: not (k[0] == 0 and k[2] == 2),  # 去 axis-0 HT,Sector Shielding
             15: lambda k: k[1] == 1 or k[2] != 2,  # 去3 个负面 HT,Transport Resolution Amplification
             14: lambda k: k[0] != 1 or k[2] == 2,  # 去axis-1 QT,Field Defect Localization
             12: lambda k: k[2] != 2,  # 仅 quarter-turn
             10: lambda k: k[0] == 1 or k[2] == 2,  # axis-1 全 + 所有 HT
             9: lambda k: k[1] == 1,  # 仅 +face (R/U/F)
             8: lambda k: k[0] != 1 and k[2] != 2,  # 去 axis-1 + 去 HT
             6: lambda k: k[2] == 2,  # 仅 half-turn
             4: lambda k: k[0] == 0 and k[2] != 2,  # axis-0 QT only
             3: lambda k: k[0] == 0 and k[1] == 1,  # axis-0 +face QT
             2: lambda k: k[0] == 0 and k[2] == 2}  # axis-0 HT only
        match = f.get(n, lambda k: False)
        return {k: v for k, v in CubieMove.rho_moves.items() if match(k)}

    @classmethod
    def lite(cls) -> "CubieSpectralOperator":
        """Lightweight instance — skips spectral decomposition. For class-method access only."""
        return cls.__new__(cls)

    @classmethod
    def from_generators(cls, generators: dict, tol: float = 1e-6) -> "CubieSpectralOperator":
        """Construct from internal-format rho_moves dict."""
        return cls(n=len(generators), generators=generators, tol=tol)

    @classmethod
    def from_gens_dict(cls, gens_dict: dict, tol: float = 1e-6) -> "CubieSpectralOperator":
        """Construct from {move_key: CubieMove} dict — the most common entry point."""
        generators = {}
        for k, mv in gens_dict.items():
            generators[k] = (mv, mv.rho().astype(np.complex128))
        return cls(n=len(generators), generators=generators, tol=tol)

    # ═══════════════════════════════════════════════════════════════
    # Paper I: A — spectral origin
    # ═══════════════════════════════════════════════════════════════

    # -- Spectral accessors --

    def spectral_layers(self) -> dict[float, dict]:
        """{lam: {dim, projector}} — one layer per distinct eigenvalue."""
        return self._layers

    def projector(self, lam: float) -> np.ndarray:
        """Spectral projector P_λ. Prefer _layers cache (closest-key match).
        """
        closest = min(self._layers.keys(), key=lambda k: abs(k - lam))
        if abs(closest - lam) < self.tol:
            return self._layers[closest]['projector']
        # fallback
        mask = np.abs(self.w - lam) < self.tol
        idx = np.where(mask)[0]
        if len(idx) == 0:
            raise ValueError(f"Eigenvalue {lam} not found")
        return self.V[:, idx] @ self.V[:, idx].T.conj()

    def eigenspace_basis(self, lam: float) -> np.ndarray:
        """Basis of the λ-eigenspace (column vectors)."""
        mask = np.abs(self.w - lam) < self.tol
        return self.V[:, mask]

    @property
    def projectors(self) -> np.ndarray:
        """Ordered list of spectral projectors P_i (one per distinct eigenvalue).
        谱投影算子列表 P_i, 按 λ 降序"""
        return np.array([info['projector'] for _, info in sorted(self._layers.items(), reverse=True)])

    @property
    def layer_dim(self) -> np.ndarray:
        """Array of spectral multiplicities (dimensions) for each eigenvalue layer.
        各层维数数组, 按 λ 降序"""
        return np.array([info['dim'] for _, info in sorted(self._layers.items(), reverse=True)])

    @property
    def layer_keys(self) -> list[float]:
        """Canonical layer eigenvalues, sorted descending.
        Canonical 层特征值, 降序 [1.0, 0.888889, 0.777778, 0.666667, 0.555556, 0.333333]
        """
        return sorted(self._layers, reverse=True)

    def labelled_projectors(self):
        """Return [(lambda, projector), ...] sorted by eigenvalue descending."""
        for lam in sorted(self._layers, reverse=True):
            yield lam, self._layers[lam]['projector']

    def layer_dimension(self, lam: float) -> int:
        """Dimension (multiplicity) of a spectral layer.

        Accepts canonical fractions (7/9, 2/3, etc.) via closest-key matching.
        某层的维数 (重数)
        """
        closest = min(self._layers.keys(), key=lambda k: abs(k - lam))
        if abs(closest - lam) < self.tol:
            return self._layers[closest]['dim']
        raise ValueError(f"Eigenvalue {lam} not found")

    def layer_projector(self, lam: float) -> np.ndarray:
        """Projector for a spectral layer — delegates to cached projector().
        谱层投影算子"""
        return self.projector(lam)

    def closest_layer(self, lam: float) -> float:
        """Return the actual float key in self._layers closest to a canonical eigenvalue.

        Canonical fractions like 7/9 resolve to the stored float key (e.g. 0.777778). 
        返回 _layers 中最接近 lam 的 canonical key 7/9 → 0.777778, 2/3 → 0.666667, etc.
        """
        return min(self._layers.keys(), key=lambda k: abs(k - lam))

    def rho_matrices(self) -> list[np.ndarray]:
        """Dense ρ(g) matrices for all generators, in rho_moves order.

        Abstracts away the internal (CubieMove, rho_matrix, ...) tuple format
        so experiments don't need to unpack it.
        所有生成元的 dense ρ(g) 矩阵, 按 rho_moves 顺序 屏蔽内部 tuple
        """
        return [v[1] for v in self.rho_moves.values()]

    @staticmethod
    def lam_to_k(lam: float) -> int:
        """λ → k where λ = 1 − k/9."""
        return round(9 * (1 - lam))

    @staticmethod
    def k_to_lam(k: int) -> float:
        """k → λ where λ = 1 − k/9."""
        return 1.0 - k / 9.0

    @staticmethod
    def layer_label(lam: float) -> str:
        """λ → human-readable label: 1.0 → V₁, 0.777778 → V(2)"""
        k = round(9 * (1 - lam))
        if abs(lam - 1.0) < 1e-5:
            return 'V₁'
        return f'V({k})'

    @staticmethod
    def block_slice(block_name: str) -> slice:
        """Return slice for block: 'cp'→slice(0,64), 'ep'→slice(64,208), etc."""
        start, end = BLOCK_RANGES[block_name]
        return slice(start, end)

    # -- Slow/fast split (for numerical experiments) --

    def slow_fast_split(self, threshold: float = 2 / 3) -> tuple[np.ndarray, np.ndarray]:
        """Split eigenvalue indices into slow (λ ≥ threshold) and fast masks.
        特征值按 threshold 分慢/快两个 mask"""
        mask_slow = self.w >= threshold - self.tol
        return mask_slow, ~mask_slow

    def slow_projector(self, threshold: float = 2 / 3) -> np.ndarray:
        """Projector onto the slow subspace (eigenvalues ≥ threshold).
        慢子空间 (λ ≥ threshold) 的投影算子"""
        mask_slow, _ = self.slow_fast_split(threshold)
        V_slow = self.V[:, mask_slow]
        return V_slow @ V_slow.T.conj()

    def slow_basis(self, threshold: float = 2 / 3) -> np.ndarray:
        """Basis vectors (columns) spanning the slow subspace.
        慢子空间的基 (列向量)"""
        mask_slow, _ = self.slow_fast_split(threshold)
        return self.V[:, mask_slow]

    # -- h_i operators & spectral field classification --

    def build_h_operators(self) -> tuple[list[np.ndarray], list[str]]:
        """Build symmetric h_i = (rho(g) + rho(g^{-1}))/2.
        对称算子, 全部 12 对"""
        gens_dict = {k: mv for k, (mv, _, _) in self.rho_moves.items()}
        return build_h_operators(gens_dict)

    def classify_field(self) -> str:
        """Classify spectral field: rational, sqrt5, or higher.
        谱域分类: m_eff = n_gen // 2 (偶数时), = n_gen (奇数时).
        """
        m_eff = self.n // 2 if self.n % 2 == 0 else self.n
        return classify_spectral_field(list(self._layers.keys()), m_eff)

    # -- SpectralStructure bridge --

    @property
    def spectral_structure(self) -> "SpectralStructure":
        if self._ss is None:
            from rime.spectralstructure import SpectralStructure
            gen_dict = {k: mv for k, (mv, *_) in self.rho_moves.items()}
            self._ss = SpectralStructure(generators=gen_dict)
        return self._ss

    def validate_with_structure(self, ss: "SpectralStructure | None" = None) -> dict:
        """Compare numerical spectrum against SpectralStructure predictions."""
        if ss is None:
            ss = self.spectral_structure
        return ss.validate_with_numerics(cso=self, tol=self.tol)

    # -- Spectral dynamics (toy) --

    def spectral_evolve(self, x: np.ndarray, T: int) -> np.ndarray:
        """T-step spectral diffusion: x ↦ A^T x = Σ λ_i^T P_i x.
        T 步谱扩散: x ↦ A^T x = Σ λ_i^T P_i x"""
        y = np.zeros_like(x, dtype=complex)
        for lam in self._layers:
            V = self.eigenspace_basis(lam)
            coeff = V.T.conj() @ x
            y += (lam ** T) * (V @ coeff)
        return y

    def random_walk(self, length: int = 10, p: np.ndarray | None = None) -> "CubieMove":
        """Sample a random length-L word from the generator set.
        从生成元集随机采 length 步 word"""
        gen = [m for m, *_ in self.rho_moves.values()]
        if length == 1:
            idx = np.random.choice(len(gen), p=p)
            return gen[idx]
        g = CubieMove.identity()
        indices = np.random.choice(len(gen), size=length, p=p)
        for idx in indices:
            g = g.compose(gen[idx])
        return g

    # ═══════════════════════════════════════════════════════════════
    # Paper II: K_αβ — transport topology & commutant algebra
    # ═══════════════════════════════════════════════════════════════

    # -- Transport tensor & graph --

    def transport_tensor(self, force_recompute: bool = False) -> dict:
        """Full P_i ρ(g) P_j coupling structure across all generator–projector triples.

        Returns nested dict keyed by (lam_i, lam_j):
            T[(lam_i, lam_j)] = {'mean': ..., 'max': ...}
        where mean/max aggregate ‖P_i ρ(g) P_j‖_F over all generators.

        Result is cached after first computation.
        全 P_i ρ(g) P_j 耦合结构
        """
        if self._transport_tensor_cache is not None and not force_recompute:
            return self._transport_tensor_cache
        if self._frozen and force_recompute:
            raise RuntimeError(
                "transport_tensor is frozen after __init__; "
                "force_recompute=True is not allowed for a frozen operator")

        layers = sorted(self._layers, reverse=True)
        T = {}
        for lam_i in layers:
            Pi = self._layers[lam_i]['projector']
            for lam_j in layers:
                Pj = self._layers[lam_j]['projector']
                norms = []
                for _k, (_mv, rho) in self.rho_moves.items():
                    norms.append(float(np.linalg.norm(Pi @ rho @ Pj, 'fro')))
                T[(lam_i, lam_j)] = {'mean': float(np.mean(norms)), 'max': float(np.max(norms))}
        self._transport_tensor_cache = T
        return T

    def transport_between(self, lam_i: float, lam_j: float) -> dict | None:
        """Transport coupling between two spectral sectors, using closest layer matching.
        两谱扇区间的传输耦合, closest-layer match"""
        T = self.transport_tensor()
        ki = self.closest_layer(lam_i)
        kj = self.closest_layer(lam_j)
        return T.get((ki, kj))

    def transport_graph(self, threshold: float | None = None) -> dict:
        """Build the transport graph from the transport tensor.
        Returns dict with nodes, edges, adjacency, is_star, hub, isolated, laplacian.

        从传输张量建图 → {nodes, edges, adjacency, is_star, hub, ...} threshold 默认 tol * 10。
        """
        layers = sorted(self._layers, reverse=True)
        n = len(layers)
        T = self.transport_tensor()
        if threshold is None:
            threshold = self.tol * 10

        # 邻接矩阵
        adj = np.zeros((n, n))
        for i, lam_i in enumerate(layers):
            for j, lam_j in enumerate(layers):
                if i != j:
                    adj[i, j] = T[(lam_i, lam_j)]['max']
        adj[np.abs(adj) < threshold] = 0.0

        # 边列表 (无向, 取 max)
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                w = max(adj[i, j], adj[j, i])
                if w > threshold:
                    edges.append((layers[i], layers[j], float(w)))

        # 度 & hub 检测
        degrees = np.array([np.count_nonzero(adj[i]) + np.count_nonzero(adj[:, i])
                            for i in range(n)])
        isolated = [layers[i] for i in range(n) if degrees[i] == 0]

        non_isolated = [i for i in range(n) if degrees[i] > 0]
        is_star = False
        hub = None
        if len(non_isolated) >= 2:
            hub_candidates = [i for i in non_isolated if degrees[i] >= len(non_isolated) - 1]
            if len(hub_candidates) == 1:
                is_star = True
                hub = layers[hub_candidates[0]]

        # 拉普拉斯
        A_undirected = np.maximum(adj, adj.T)
        D = np.diag(np.sum(A_undirected, axis=1))
        laplacian = D - A_undirected

        return {
            'nodes': layers,
            'edges': edges,
            'adjacency': adj,
            'is_star': is_star,
            'hub': hub,
            'isolated': isolated,
            'laplacian': laplacian,
        }

    def raising_lowering(self, g_key=None) -> dict:
        """Raising/lowering operators for a given generator.

        For adjacent sector pairs (i, i+1) with nonzero transport, define:
            R_k = P_{k+1}·ρ(g)·P_k, L_k = P_{k-1}·ρ(g)·P_k

        升降算子:对相邻 (有传输边) 的扇区对定义, 含闭包关系 [L,R] 和正交性检查
        """
        layers = sorted(self._layers, reverse=True)
        graph = self.transport_graph()
        edges = graph['edges']

        if g_key is None:
            g_key = list(self.rho_moves.keys())[0]
        _mv, rho_g = self.rho_moves[g_key]

        R, L, norms = {}, {}, {}
        for lam_i, lam_j, _w in edges:
            Pi = self._layers[lam_i]['projector']
            Pj = self._layers[lam_j]['projector']
            R[(lam_i, lam_j)] = Pj @ rho_g @ Pi
            L[(lam_j, lam_i)] = Pi @ rho_g @ Pj
            norms[(lam_i, lam_j)] = {
                'R': float(np.linalg.norm(R[(lam_i, lam_j)], 'fro')),
                'L': float(np.linalg.norm(L[(lam_j, lam_i)], 'fro')),
            }

        # 闭包: 7/9 ↔ 5/9 是 canonical 升降对
        closure = {}
        lam_79 = 7 / 9
        lam_59 = 5 / 9
        if lam_79 in self._layers and lam_59 in self._layers:
            R_op = R.get((lam_79, lam_59))
            L_op = L.get((lam_79, lam_59))
            if R_op is not None and L_op is not None:
                closure['R†R'] = float(np.linalg.norm(
                    R_op.T.conj() @ R_op, 'fro'))
                closure['RR†'] = float(np.linalg.norm(
                    R_op @ R_op.T.conj(), 'fro'))
                closure['LR'] = float(np.linalg.norm(L_op @ R_op, 'fro'))
                closure['RL'] = float(np.linalg.norm(R_op @ L_op, 'fro'))
                comm_LR = L_op @ R_op - R_op @ L_op
                closure['‖[L,R]‖'] = float(np.linalg.norm(comm_LR, 'fro'))

        return {
            'generator_key': g_key,
            'pairs': edges,
            'R': R,
            'L': L,
            'norms': norms,
            'closure': closure,
        }

    # -- Per-axis averaged operators (Object 1) --

    def build_per_axis_ops(self) -> tuple[dict, list]:
        """Build per-axis QT and HT averaging operators.

        Primary Object 1: A_S for axis-restricted generator subsets.
        Returns ops dict with QT0-2, HT0-2, QT_all, HT_all, A_18.
        分轴 QT/HT 平均算子
        """
        if hasattr(self, '_per_axis_ops_cache'):
            return self._per_axis_ops_cache, self._per_axis_move_keys

        rhos = [v[1] for v in self.rho_moves.values()]
        move_keys = list(self.rho_moves.keys())
        ops = {}

        ops['A_18'] = sum(rhos) / 18

        # QT = quarter-turn (dir ≠ 2), HT = half-turn (dir = 2)
        d = rhos[0].shape[0]
        qt_idx = [i for i, k in enumerate(move_keys) if k[2] != 2]
        ops['QT_all'] = sum(rhos[i] for i in qt_idx) / len(qt_idx) if qt_idx else np.zeros((d, d))

        ht_idx = [i for i, k in enumerate(move_keys) if k[2] == 2]
        ops['HT_all'] = sum(rhos[i] for i in ht_idx) / len(ht_idx) if ht_idx else np.zeros((d, d))

        for axis in range(3):
            qt_ax = [i for i, k in enumerate(move_keys) if k[0] == axis and k[2] != 2]
            ops[f'QT{axis}'] = sum(rhos[i] for i in qt_ax) / len(qt_ax) if qt_ax else np.zeros((d, d))

        for axis in range(3):
            ht_ax = [i for i, k in enumerate(move_keys) if k[0] == axis and k[2] == 2]
            ops[f'HT{axis}'] = sum(rhos[i] for i in ht_ax) / len(ht_ax) if ht_ax else np.zeros((d, d))

        self._per_axis_ops_cache = ops
        self._per_axis_move_keys = move_keys
        return ops, move_keys

    # Quick-access properties
    @property
    def QT_all(self):
        ops, _ = self.build_per_axis_ops()
        return ops['QT_all']

    @property
    def HT_all(self):
        ops, _ = self.build_per_axis_ops()
        return ops['HT_all']

    @property
    def A_18(self):
        return self.A

    @property
    def QT0(self):
        ops, _ = self.build_per_axis_ops()
        return ops['QT0']

    @property
    def QT1(self):
        ops, _ = self.build_per_axis_ops()
        return ops['QT1']

    @property
    def QT2(self):
        ops, _ = self.build_per_axis_ops()
        return ops['QT2']

    @property
    def HT0(self):
        ops, _ = self.build_per_axis_ops()
        return ops['HT0']

    @property
    def HT1(self):
        ops, _ = self.build_per_axis_ops()
        return ops['HT1']

    @property
    def HT2(self):
        ops, _ = self.build_per_axis_ops()
        return ops['HT2']

    # ═══════════════════════════════════════════════════════════════
    # Commutant algebra — commutant & irrep decomposition
    # ═══════════════════════════════════════════════════════════════

    # -- Shared cache: projected_gens & commutant basis --

    def _projected_gens_for_layer(self, lam: float) -> tuple[list[np.ndarray], int]:
        """Build projected generators G_k = V_λ† ρ(g_k) V_λ within one eigenspace.

        Result is cached — commutant_algebra() and irrep_decomposition()
        share the same projected generators, eliminating duplicate computation.
        G_k — 投影到 λ-特征空间的生成元
        """
        if lam in self._pg_cache:
            return self._pg_cache[lam]
        V = self.eigenspace_basis(lam)
        d = V.shape[1]
        projected_gens = []
        for _k, (_mv, rho) in self.rho_moves.items():
            projected_gens.append(V.T.conj() @ rho @ V)
        self._pg_cache[lam] = (projected_gens, d)
        return projected_gens, d

    def _commutant_for_layer(self, lam: float) -> tuple[list[np.ndarray], int]:
        """Compute (or retrieve from cache) commutant basis and dimension for a layer.

        Single computation shared by commutant_algebra() and irrep_decomposition().
        First call freezes the result — eliminates randomized-method drift between
        independent calls and cuts duplicate SVD/projection work.
        λ-层的交换子基 & 维数 首次调用冻结结果，消除随机方法的漂移
        """
        if lam in self._cb_cache:
            return self._cb_cache[lam]
        projected_gens, d = self._projected_gens_for_layer(lam)
        basis, comm_dim = self._commutant_basis_within_block(projected_gens, d)
        self._cb_cache[lam] = (basis, comm_dim)
        return basis, comm_dim

    # -- Reynolds projection (commutant projection) --

    @staticmethod
    def project_commutant(X: np.ndarray, projected_gens: list[np.ndarray], gen_inv: list[np.ndarray] | None = None,
                          n_iter: int = 30) -> np.ndarray:
        """Project a d×d matrix X onto the commutant via group averaging (Reynolds operator).

        For best convergence, use project_commutant_exact() which uses the
        order-4 exact projector. This method is kept as a faster, lower-precision alternative.
        群平均 (Reynolds operator) 投影到交换子
        X ↦ (1/|G|) Σ_g G^H X G, 迭代 n_iter 次。对大规模 d 用 project_commutant_exact() 更稳
        """
        if gen_inv is None:
            gen_inv = [G.T.conj() for G in projected_gens]
        n = len(projected_gens)
        for _ in range(n_iter):
            X_avg = np.zeros_like(X)
            for G_inv, G in zip(gen_inv, projected_gens):
                X_avg += G_inv @ X @ G
            X = X_avg / n
        return X

    @staticmethod
    def project_commutant_exact(X: np.ndarray, projected_gens: list[np.ndarray], n_iter: int = 10) -> np.ndarray:
        """Project onto commutant using exact per-generator centralizer projectors.

        For generator G of order 4: P_G(X) = 1/4 Σ_{t=0}^3 (G^H)^t X G^t.
        Each per-generator projection maps to ker[G, ·] in one step.
        精确中心化投影: 用 G 的 4 阶性质一步到 ker[G, ·] Rubik 生成元都是 4 阶 → 每步精确投影。
        """
        for _ in range(n_iter):
            for G in projected_gens:
                GH = G.conj().T
                G2 = G @ G
                G2H = GH @ GH
                G3 = G2 @ G
                G3H = G2H @ GH
                X = 0.25 * (X + GH @ X @ G + G2H @ X @ G2 + G3H @ X @ G3)
        return X

    # -- Commutant basis computation --

    def _commutant_basis_within_block(self, projected_gens: list[np.ndarray], d: int) -> tuple[list[np.ndarray], int]:
        """Build orthonormal basis for the commutant within one eigenspace block.

        d ≤ 50: reduce generators to independent set, build full constraint
                matrix, one-shot SVD (stable for clustered singular spectra).
        d > 50: randomized sampling + Reynolds projection.
        块内交换子正交基
        """
        if d <= 50:  # 先生成元独立化
            gen_vecs = np.array([G.ravel() for G in projected_gens])
            _, s_gen, Vh_gen = np.linalg.svd(gen_vecs, full_matrices=False)
            rank = int(np.sum(s_gen > self.tol * s_gen[0]))
            indep_gens = [Vh_gen[i, :].reshape(d, d) for i in range(rank)]

            # 建完整约束矩阵 → 一次 SVD
            # M_k = kron(G_k^T, I) - kron(I, G_k)
            constraints = []
            for G_k in indep_gens:
                M_k = np.kron(G_k.T, np.eye(d)) - np.kron(np.eye(d), G_k)
                constraints.append(M_k)
            C = np.vstack(constraints)
            _, s, Vh = np.linalg.svd(C, full_matrices=False)
            sv_thresh = self.tol * max(1.0, s[0]) * max(C.shape)
            null_mask = s < sv_thresh
            comm_dim = int(np.sum(null_mask))

            # Gram-Schmidt 正交化
            basis_vecs = Vh[-comm_dim:, :] if comm_dim > 0 else Vh[-1:, :] * 0
            basis = []
            gs_tol = self.tol * d * 10
            for i in range(comm_dim):
                B = basis_vecs[i].reshape(d, d)
                for existing in basis:
                    B -= np.tensordot(existing.conj(), B) * existing
                nrm = np.linalg.norm(B, 'fro')
                if nrm > gs_tol:
                    basis.append(B / nrm)
            comm_dim = len(basis)
        else:  # 随机采样 + Reynolds 投影
            gen_inv = [G.T.conj() for G in projected_gens]
            basis, comm_dim = self._commutant_basis_randomized(projected_gens, gen_inv, d)
        return basis, comm_dim

    def _commutant_basis_randomized(self, projected_gens: list[np.ndarray], gen_inv: list[np.ndarray],
                                    d: int, n_samples: int | None = None) -> tuple[list[np.ndarray], int]:
        """Random sampling + Reynolds projection + Gram-Schmidt for d > 50.

        Uses exact order-4 per-generator projectors.
        随机 + Reynolds 投影 + GS 正交化,使用精确 4 阶投影算子
        """
        if n_samples is None:
            n_samples = min(d * 6, 250)
        basis = []
        gs_tol = self.tol * d * 10
        for _ in range(n_samples):
            X = np.random.randn(d, d) + 1j * np.random.randn(d, d)
            X = self.project_commutant_exact(X, projected_gens, n_iter=8)
            for B in basis:
                X -= np.tensordot(B.conj(), X) * B
            nrm = np.linalg.norm(X, 'fro')
            if nrm > gs_tol:
                basis.append(X / nrm)
        return basis, len(basis)

    # -- Commutant algebra analysis --

    def commutant_residual(self, P: np.ndarray) -> dict:
        """‖[P, ρ(g)]‖_F for every generator — measures how far P is from central.
        P 离中心的距离, 每个生成元一个值"""
        residuals = {}
        for k, (_, rho, *_) in self.rho_moves.items():
            residuals[k] = float(np.linalg.norm(P @ rho - rho @ P, 'fro'))
        return residuals

    def commutant_algebra(self) -> dict:
        """Compute the commutant algebra C = {X : [X, ρ(g)] = 0 for all generators g}.

        Uses shared _commutant_for_layer() cache — first caller pays the cost,
        subsequent callers (e.g. irrep_decomposition) get cached results.

        交换子代数  分 λ 层计算 — 共用 cache
        """
        layers = sorted(self._layers, reverse=True)
        comm_blocks = {}
        dim_total = 0

        for lam in layers:
            info = self._layers[lam]
            d = info['dim']
            _basis, comm_dim = self._commutant_for_layer(lam)
            is_pure = (comm_dim == d * d)
            comm_blocks[lam] = {
                'dim': d,
                'commutant_dim': comm_dim,
                'is_pure': is_pure,
                'n_irreps': int(np.round(np.sqrt(comm_dim))) if is_pure else None,
            }
            dim_total += comm_dim

        # 中心幂等元: 与所有生成元对易的投影算子
        central = []
        for lam in layers:
            residuals = self.commutant_residual(self._layers[lam]['projector'])
            max_res = max(residuals.values())
            if max_res < self.tol * 10:
                central.append(lam)

        return {
            'dim_total': dim_total,
            'blocks': comm_blocks,
            'central_idempotents': central,
        }

    # -- Full-space commutant (combinatorial orbit method) --

    def full_commutant_combinatorial(self) -> tuple[list[np.ndarray], int]:
        """Compute commutant basis in the FULL 228-dim space via combinatorial orbits.

        For monomial ρ(g) = D_g Π_g: entries of X are constant on orbits of
        (i,j) → (π_g(i), π_g(j)), up to phase consistency. One orbit = one
        commutant degree of freedom iff phase consistency holds.

        Returns (basis, comm_dim) where comm_dim is the exact total commutant dimension.

        228 维全空间交换子基 — 组合轨道法。

        ρ(g) = D_g Π_g 是单项矩阵: 每个 (i,j) 对落在置换-相位轨道上
        一条轨道 ⇔ 一个交换子自由度 (当相位一致性成立)

        返回 (basis, comm_dim), comm_dim = 610 (CCS canonical).
        """
        if self._full_comm_cache is not None:
            return self._full_comm_cache

        d_full = 228
        # 提取置换和相位 (每列一个非零元)
        perms, phases = [], []
        for _k, (_mv, rho) in self.rho_moves.items():
            rho_dense = rho.toarray() if hasattr(rho, 'toarray') else np.array(rho)
            perm = [0] * d_full
            diag = np.zeros(d_full, dtype=complex)
            for col in range(d_full):
                rows = np.where(np.abs(rho_dense[:, col]) > 0.5)[0]
                if len(rows) == 1:
                    row = rows[0]
                    perm[col] = row
                    diag[row] = rho_dense[row, col]
            perms.append(perm)
            phases.append(diag)

        # BFS 找轨道
        n_pairs = d_full * d_full
        visited = np.zeros(n_pairs, dtype=bool)
        orbits = []

        # 预计算逆置换
        g_inv = [[0] * d_full for _ in perms]
        for g_idx, perm in enumerate(perms):
            for i in range(d_full):
                g_inv[g_idx][perm[i]] = i

        for start in range(n_pairs):
            if visited[start]:
                continue
            orbit = []
            stack = [start]
            visited[start] = True
            while stack:
                pair_idx = stack.pop()
                orbit.append(pair_idx)
                i, j = divmod(pair_idx, d_full)
                for g_idx in range(len(perms)):
                    ni, nj = perms[g_idx][i], perms[g_idx][j]
                    nidx = ni * d_full + nj
                    if not visited[nidx]:
                        visited[nidx] = True
                        stack.append(nidx)
            orbits.append(orbit)

        # 相位一致性检查 → 构造基元素
        basis = []
        for orb in orbits:
            pair_to_phase = {orb[0]: 1.0 + 0j}
            queue = [orb[0]]
            consistent = True
            while queue and consistent:
                pair_idx = queue.pop(0)
                i, j = divmod(pair_idx, d_full)
                val = pair_to_phase[pair_idx]
                for g_idx in range(len(perms)):
                    pi, pj = perms[g_idx][i], perms[g_idx][j]
                    next_idx = pi * d_full + pj
                    if next_idx not in pair_to_phase:
                        d_pi = phases[g_idx][pi]
                        d_pj = phases[g_idx][pj]
                        if abs(d_pj) < 1e-10:
                            consistent = False
                            break
                        pair_to_phase[next_idx] = d_pi * val / d_pj
                        queue.append(next_idx)
                    else:
                        d_pi = phases[g_idx][pi]
                        d_pj = phases[g_idx][pj]
                        expected = d_pi * val / d_pj if abs(d_pj) > 1e-10 else 0
                        if abs(pair_to_phase[next_idx] - expected) > 1e-8:
                            consistent = False
                            break

            if consistent:
                B = np.zeros((d_full, d_full), dtype=complex)
                norm_factor = np.sqrt(len(orb))
                for pair_idx, phase_val in pair_to_phase.items():
                    i, j = divmod(pair_idx, d_full)
                    B[i, j] = phase_val / norm_factor
                basis.append(B)

        self._full_comm_cache = (basis, len(basis))
        return basis, len(basis)

    # -- Center & irrep decomposition (F1-F3) --

    def _commutant_center_lightweight(self, comm_basis: list[np.ndarray], d: int) -> tuple[int, list[tuple]]:
        """Lightweight center detection: diagonalize a random commutant element.

        Returns (center_dim, components) where each component is (comp_dim, multiplicity, d_irrep).
    
        轻型中心检测， 对角化一个随机交换子元素
        """
        r = len(comm_basis)
        if r == 0:
            return 0, []

        tol = self.tol * d * 10
        C_rand = np.zeros((d, d), dtype=complex)  # 随机组合 → 期望可对角化
        for i in range(r):
            C_rand += np.random.randn() * comm_basis[i]
        C_rand = (C_rand + C_rand.T.conj()) / 2

        eigvals, U = np.linalg.eigh(C_rand)
        eigvals_rounded = np.round(eigvals, decimals=max(3, -int(np.log10(tol))))
        unique_eigvals, inverse, counts = np.unique(eigvals_rounded, return_inverse=True, return_counts=True)

        # 第二个随机组合 → 拆分可能合并的分量
        C_rand2 = np.zeros((d, d), dtype=complex)
        for i in range(r):
            C_rand2 += np.random.randn() * comm_basis[i]
        C_rand2 = (C_rand2 + C_rand2.T.conj()) / 2

        final_components = []
        for idx in range(len(unique_eigvals)):
            mask = inverse == idx
            comp_dim = int(np.sum(mask))
            if comp_dim == 0:
                continue
            U_sub = U[:, mask]
            C2_sub = U_sub.T.conj() @ C_rand2 @ U_sub
            w2 = np.linalg.eigvalsh(C2_sub)
            w2_rounded = np.round(w2, decimals=max(3, -int(np.log10(tol))))
            n_sub = len(np.unique(w2_rounded))
            if n_sub > 1:  # 进一步拆分
                eigvals2, U2 = np.linalg.eigh(C2_sub)
                eigvals2_rounded = np.round(eigvals2, decimals=max(3, -int(np.log10(tol))))
                for mu2 in np.unique(eigvals2_rounded):
                    mask2 = np.abs(eigvals2_rounded - mu2) < 1e-8
                    sub_dim = int(np.sum(mask2))
                    if sub_dim == 0:
                        continue
                    final_components.append(sub_dim)
            else:
                final_components.append(comp_dim)

        result = []
        for comp_dim in final_components:
            # 分解为 d_irrep × multiplicity
            m_est = 1
            for m_cand in range(int(np.sqrt(comp_dim)), 0, -1):
                if comp_dim % m_cand == 0:
                    m_est = m_cand
                    break
            d_irrep = comp_dim // m_est
            result.append((comp_dim, m_est, d_irrep))

        return len(final_components), result

    def _center_idempotents(self, comm_basis: list[np.ndarray], d: int) -> tuple:
        """Central primitive idempotents from commutant basis (F1).

        Returns (center_dim, idempotents, isotypic_projectors, isotypic_info).
        中心本原幂等元 from 交换子基 (F1)
        """
        r = len(comm_basis)
        if r == 0:
            return 0, [], [], []
        if r == 1:
            P = np.eye(d, dtype=complex)
            return 1, [P], [P], [(d, 1)]

        # MHM: 可对易性矩阵 → 零空间 = 中心元素
        C_stack = np.array(comm_basis)
        MHM = np.zeros((r, r))
        d2 = d * d
        for j in range(r):
            comms = C_stack @ C_stack[j] - C_stack[j] @ C_stack
            comms_flat = comms.reshape(r, d2)
            MHM += (comms_flat @ comms_flat.conj().T).real

        evals, evecs = np.linalg.eigh(MHM)
        ev_thresh = self.tol * max(1.0, np.max(evals)) * r * d
        null_mask = evals < ev_thresh
        center_dim = int(np.sum(null_mask))
        if center_dim == 0:
            return 0, [], [], []

        center_elems = []
        for idx in range(r):
            if null_mask[idx]:
                Z = sum(evecs[idx, i] * comm_basis[i] for i in range(r))
                center_elems.append((Z + Z.conj().T) / 2)

        if center_dim == 1:
            m_est = int(np.round(np.sqrt(r)))
            if m_est * m_est == r and d % m_est == 0:
                d_irrep, mult = d // m_est, m_est
            else:
                d_irrep, mult = d, 1
            P = np.eye(d, dtype=complex)
            return 1, [P], [P], [(d_irrep, mult)]

        # 两个随机组合 → 同时对角化 → 分解
        C_rand = sum(np.random.randn() * Z for Z in center_elems)
        C_rand = (C_rand + C_rand.conj().T) / 2
        evals_C, U = np.linalg.eigh(C_rand)

        decimals = max(4, -int(np.log10(self.tol)))
        evals_rounded = np.round(evals_C, decimals=decimals)
        unique_evals = np.unique(evals_rounded)

        C_rand2 = sum(np.random.randn() * C for C in comm_basis)
        C_rand2 = (C_rand2 + C_rand2.conj().T) / 2

        idempotents, isotypic_projectors, isotypic_info = [], [], []
        for val in unique_evals:
            mask = np.abs(evals_rounded - val) < 10 ** (-decimals)
            U_sub = U[:, mask]
            comp_dim = U_sub.shape[1]
            if comp_dim == 0:
                continue

            P_iso = U_sub @ U_sub.T.conj()
            isotypic_projectors.append((P_iso + P_iso.conj().T) / 2)

            C2_proj = U_sub.T.conj() @ C_rand2 @ U_sub
            w2 = np.linalg.eigvalsh(C2_proj)
            w2_rounded = np.round(w2, decimals=decimals)
            unique_w2, w2_counts = np.unique(w2_rounded, return_counts=True)
            d_alphas = np.unique(w2_counts)
            d_alpha = d_alphas[np.argmax([np.sum(w2_counts == d) for d in d_alphas])] if len(d_alphas) > 1 else \
                d_alphas[0]
            m_alpha = comp_dim // d_alpha
            isotypic_info.append((d_alpha, m_alpha))

            for w_val in unique_w2:
                w_mask = np.abs(w2_rounded - w_val) < 10 ** (-decimals)
                n_sub = int(np.sum(w_mask))
                if n_sub == 0:
                    continue
                P = (U_sub @ np.eye(comp_dim)[:, w_mask] @ (U_sub @ np.eye(comp_dim)[:, w_mask]).T.conj())
                idempotents.append((P + P.conj().T) / 2)

        return len(isotypic_info), idempotents, isotypic_projectors, isotypic_info

    def irrep_decomposition(self) -> dict:
        """Full Artin-Wedderburn decomposition within each spectral eigenspace.

        Uses shared _commutant_for_layer() cache — commutant_algebra() and
        irrep_decomposition() share the same commutant basis, guaranteeing
        consistent commutant dimensions and eliminating duplicate SVD work.

        Artin-Wedderburn 分解 — 每层内的不可约表示结构

        .. warning::
           **LIMITATION:** This method operates within spectral
           layers of A_18, but A_18 layers are NOT invariant under individual
           ρ(g) ([A_18, ρ(g)] ~ 0.1). Layer-projected generators V†ρ(g)V are
           non-unitary, so isotypic detection within layers reports incorrect
           irrep dimensions (2D/3D instead of true 7/8/11/12).

           For correct irrep decomposition, use full 228D commutant
           (full_commutant_combinatorial) + Center(Comm) idempotents.
           See experiments/exploratory/_exp_lie_saturation_ratio.py for the
           working implementation.
        """
        layers = sorted(self._layers, reverse=True)
        result_blocks = {}
        all_irreps = []

        for lam in layers:
            info = self._layers[lam]
            d = info['dim']

            comm_basis, comm_dim = self._commutant_for_layer(lam)
            center_dim, isotypic_raw = self._commutant_center_lightweight(comm_basis, d)

            isotypic = ([(d_irr, mult) for _, mult, d_irr in isotypic_raw] if isotypic_raw else [])

            if comm_dim == d * d and not isotypic:
                isotypic = [(1, d)]
                center_dim = 1

            for d_irrep, mult in isotypic:
                all_irreps.append((d_irrep, mult, float(lam)))

            if not isotypic and d > 0:
                m_est = int(np.round(np.sqrt(comm_dim)))
                if m_est * m_est == comm_dim:
                    d_irrep = d // m_est if m_est > 0 else d
                else:
                    m_est = 1
                    d_irrep = d
                isotypic = [(d_irrep, m_est)]
                all_irreps.append((d_irrep, m_est, float(lam)))

            result_blocks[lam] = {
                'dim': d,
                'commutant_dim': comm_dim,
                'center_dim': center_dim,
                'isotypic': isotypic,
            }

        irrep_summary = {}
        for d_irrep, m, lam_src in all_irreps:
            key = d_irrep
            if key not in irrep_summary:
                irrep_summary[key] = {'d_irrep': d_irrep, 'total_mult': 0, 'sources': []}
            irrep_summary[key]['total_mult'] += m
            irrep_summary[key]['sources'].append((float(lam_src), m))

        return {
            'blocks': result_blocks,
            'total_isotypic_types': len(all_irreps),
            'irrep_sizes': sorted(irrep_summary.values(), key=lambda x: x['d_irrep'], reverse=True),
            'dim_total': sum(b['commutant_dim'] for b in result_blocks.values()),
        }

    # ═══════════════════════════════════════════════════════════════
    # 9 joint sectors from the commuting QH algebra
    # ═══════════════════════════════════════════════════════════════

    def center_decomposition(self) -> dict:
        """Joint diagonalization of {A_18, QT_all, HT_all} into 9 sectors.

        These are the minimal simultaneous eigenspaces of the registered
        commuting QH algebra, ordered by k and then dimension. No identification
        with the center or the full group commutant is made here.

        Registered commuting QH algebra -> 9 minimal joint sectors
        CCS canonical order (k 升序, dim 升序):
        S1: V₁   dim=20  [cp=8 + ep=12]          — Isolated (deg=0)
        S2: V₈/₉ dim= 2  [eo=2]                   — Connective (deg=2)
        S3: V₇/₉ dim=39  [ep=36 + eo=3]           — Metastable (deg=2)
        S4: V₂/₃ dim=26  [ep=24 + co=2]           — Intermediate (deg=2)
        S5: V₅/₉ dim= 1  [eo=1]                   — Tiny EO leaf (deg=2)
        S6: V₅/₉ dim=39  [ep=36 + eo=3]           — PRIMARY HUB (deg=5)
        S7: V₅/₉ dim=66  [cp+ep+co+eo]            — Secondary hub (deg=3)
        S8: V₁/₃ dim= 8  [cp=8]                   — Pure CP (deg=1)
        S9: V₁/₃ dim=27  [cp=24 + co=3]           — CP+CO (deg=3)
        """
        ops, _ = self.build_per_axis_ops()
        A_18 = ops['A_18']
        A_qt = ops['QT_all']
        A_ht = ops['HT_all']

        # 随机线性组合 → 几乎必然同时对角化
        rng = np.random.RandomState(self.seed)
        M = A_18 + rng.randn() * A_qt + rng.randn() * A_ht
        M = (M + M.conj().T) / 2
        evals, evecs = np.linalg.eigh(M)

        # 按 CENTER_CLUSTER_TOL 聚类
        order = np.argsort(evals)[::-1]
        groups, cur, cv = [], [order[0]], evals[order[0]]
        for idx in range(1, len(order)):
            oi = order[idx]
            if abs(evals[oi] - cv) < CENTER_CLUSTER_TOL:
                cur.append(oi)
            else:
                groups.append(cur)
                cur, cv = [oi], evals[oi]
        groups.append(cur)

        sectors, projectors, sector_bases = [], [], []
        for indices in groups:
            V = evecs[:, indices]
            V_orth, _ = np.linalg.qr(V)        # orthonormal sector basis
            P = V_orth @ V_orth.T.conj()        # projector from orthonormal basis
            dim = int(round(np.trace(P).real))

            # 在每个扇区内取 A_18/A_qt/A_ht 的特征值
            r_18 = P @ A_18 @ P
            ev = np.linalg.eigvalsh(r_18)
            nz = np.abs(ev) > 1e-10
            lam_18 = float(ev[nz][0]) if np.any(nz) else 0.0

            r_qt = P @ A_qt @ P
            ev = np.linalg.eigvalsh(r_qt)
            nz = np.abs(ev) > 1e-10
            lam_QT = float(ev[nz][0]) if np.any(nz) else 0.0

            r_ht = P @ A_ht @ P
            ev = np.linalg.eigvalsh(r_ht)
            nz = np.abs(ev) > 1e-10
            lam_HT = float(ev[nz][0]) if np.any(nz) else 0.0

            sectors.append({'dim': dim, 'lam_18': lam_18, 'lam_QT': lam_QT, 'lam_HT': lam_HT})
            projectors.append(P)
            sector_bases.append(V_orth)

        # CCS canonical order: k = 9*(1-λ) 升序, 同 k 内 dim 升序
        ccs_order = sorted(range(len(sectors)),
                           key=lambda i: (round(9 * (1 - sectors[i]['lam_18'])), sectors[i]['dim']))
        sectors = [sectors[i] for i in ccs_order]
        projectors = [projectors[i] for i in ccs_order]
        sector_bases = [sector_bases[i] for i in ccs_order]

        # MorphoSymm-style change-of-basis: Q = [V_0 | V_1 | ... | V_{s-1}]
        Q = np.hstack(sector_bases) if sector_bases else np.zeros((0, 0), dtype=complex)

        return {
            'sectors': sectors,
            'projectors': projectors,
            'sector_bases': sector_bases,
            'Q': Q,
            'n_sectors': len(sectors),
        }
    
    def decompose_signal(self, vec: np.ndarray) -> list[np.ndarray]:
        """MorphoSymm-style signal decomposition into sector components.

        Transforms vec to isotypic basis via Q†, splits by sector dimension,
        and returns per-sector components in the original basis.

        Args:
            vec: state vector of shape (n,) or (n, k).

        Returns:
            list of per-sector component vectors, each same shape as vec.
            Sum of components = vec (up to numerical error).
        """
        decomp = self.center_decomposition()
        Q = decomp['Q']
        sector_dims = [s['dim'] for s in decomp['sectors']]
        vec = np.asarray(vec, dtype=complex)
        scalar_input = (vec.ndim == 1)
        if scalar_input:
            vec = vec.reshape(-1, 1)

        # Transform to isotypic basis
        vec_iso = Q.conj().T @ vec

        # Split by sector
        components = []
        pos = 0
        for dk in sector_dims:
            comp_iso = np.zeros_like(vec_iso)
            comp_iso[pos:pos + dk] = vec_iso[pos:pos + dk]
            comp_orig = Q @ comp_iso
            components.append(comp_orig)
            pos += dk

        if scalar_input:
            components = [c.ravel() for c in components]
        return components

    def sector_block_support(self, projectors: list[np.ndarray] | None = None) -> list[set[str]]:
        """Return [{block_names}, ...] for each sector projector.

        If projectors is None, uses center_decomposition()['projectors'].
        Detects multi-block membership via Frobenius norm (block_set).
        """
        if projectors is None:
            projectors = self.center_decomposition()['projectors']
        return [block_set(P, BLOCK_RANGES) for P in projectors]

    # ═══════════════════════════════════════════════════════════════
    # Archived first-version kappa diagnostics; not current Paper III support
    # ═══════════════════════════════════════════════════════════════

    def registered_principal_log_generators(self) -> list[np.ndarray]:
        """Register ``log(rho(g))`` using SciPy's principal matrix-log branch.

        This is one declared observable family. It is not interchangeable with
        finite-order logarithms or anti-Hermitian-part registrations. The
        result is cached because the 18 matrix logarithms are expensive.

        Verification: expm(A_g) ≈ ρ(g) to ~1e-15 for all generators.
        """
        if self._lie_gens_cache is not None:
            return self._lie_gens_cache

        from scipy.linalg import logm, expm
        rhos = [v[1] for v in self.rho_moves.values()]
        A_gens = [logm(rho) for rho in rhos]

        max_err = max(np.max(np.abs(expm(Ag) - rho))
                      for Ag, rho in zip(A_gens, rhos))
        if max_err > 1e-10:
            import warnings
            warnings.warn(f"logm fidelity: max|expm(A_g)-rho| = {max_err:.2e}")

        self._lie_gens_cache = A_gens
        return A_gens

    def compute_lie_generators(self) -> list[np.ndarray]:
        """Deprecated alias for ``registered_principal_log_generators``."""
        import warnings
        warnings.warn(
            "compute_lie_generators() is deprecated; use "
            "registered_principal_log_generators() and record the branch",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.registered_principal_log_generators()

    def infinitesimal_transport(self) -> dict:
        """Compute κ_ij = max_g ‖P_i A_g P_j‖_F — infinitesimal transport.

        Continuous analogue of transport_tensor(). Uses logm for Lie generators
        A_g = log(ρ(g)). Pairs with κ_ij > 0 indicate sectors connected in the
        continuous (Lie) dynamics.

        无穷小传输 (κ₀) 连续 Lie 动力学的传输矩阵 κ_ij > 0 ⇔ Lie 可达。
        """
        import warnings
        warnings.warn(
            "infinitesimal_transport() is a legacy principal-log diagnostic; "
            "use typed accessibility APIs with an explicitly declared family",
            DeprecationWarning,
            stacklevel=2,
        )
        A_gens = self.registered_principal_log_generators()
        layers = sorted(self._layers, reverse=True)
        n_layers = len(layers)

        kappa = {}
        kappa_matrix = np.zeros((n_layers, n_layers))

        for i, lam_i in enumerate(layers):
            Pi = self._layers[lam_i]['projector']
            for j, lam_j in enumerate(layers):
                Pj = self._layers[lam_j]['projector']
                norms = [np.linalg.norm(Pi @ A_g @ Pj, 'fro') for A_g in A_gens]
                kappa[(lam_i, lam_j)] = {'mean': float(np.mean(norms)), 'max': float(np.max(norms)), }
                kappa_matrix[i, j] = max(norms)

        return {'kappa': kappa, 'kappa_matrix': kappa_matrix, 'layers': layers}

    def kappa_depth(self, depth: int = 1, max_commutator_samples: int = 200) -> dict:
        """Compute κ_d(i,j) at Lie depth d.

        Primary Object 6: Lie closure accessibility hierarchy.
        depth=0: delegates to infinitesimal_transport() (κ₀)
        depth=1: [A_g, A_h] commutators (κ₁)
        depth=2: [[A_g, A_h], A_k] nested commutators (κ₂)

        κ_d(i,j) — Lie 深度 d 的可达性
        depth=0: κ₀ (梯度)
        depth=1: κ₁ (曲率, commutator)
        depth=2: κ₂ (嵌套 commutator)
        """
        import itertools
        import warnings
        warnings.warn(
            "kappa_depth() is a legacy sampled diagnostic; use "
            "rime.accessibility.compute_lie_depth_matrix() for declared cutoffs",
            DeprecationWarning,
            stacklevel=2,
        )
        layers = sorted(self._layers, reverse=True)
        n_layers = len(layers)

        if depth == 0:
            result = self.infinitesimal_transport()
            lam_labels = ['V1', 'V8/9', 'V7/9', 'V2/3', 'V5/9', 'V1/3'][:n_layers]
            return {'kappa_matrix': result['kappa_matrix'],
                    'layers': result['layers'],
                    'lam_labels': lam_labels}

        A_gens = self.registered_principal_log_generators()
        n_gen = len(A_gens)
        P = [self._layers[lam]['projector'] for lam in layers]

        if depth == 1:
            kappa = np.zeros((n_layers, n_layers))
            for g in range(n_gen):
                for h in range(g + 1, n_gen):
                    comm = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
                    for i in range(n_layers):
                        for j in range(n_layers):
                            nrm = np.linalg.norm(P[i] @ comm @ P[j], 'fro')
                            kappa[i, j] = max(kappa[i, j], nrm)
        elif depth == 2:
            kappa = np.zeros((n_layers, n_layers))
            triples = list(itertools.combinations(range(n_gen), 3))
            if len(triples) > max_commutator_samples:
                rng = np.random.RandomState(self.seed)
                triples = [triples[i] for i in
                           rng.choice(len(triples), max_commutator_samples, replace=False)]
            for g, h, k in triples:
                comm_gh = A_gens[g] @ A_gens[h] - A_gens[h] @ A_gens[g]
                nested = comm_gh @ A_gens[k] - A_gens[k] @ comm_gh
                for i in range(n_layers):
                    for j in range(n_layers):
                        nrm = np.linalg.norm(P[i] @ nested @ P[j], 'fro')
                        kappa[i, j] = max(kappa[i, j], nrm)
        else:
            raise ValueError(f"depth={depth} not supported (use 0, 1, or 2)")

        lam_labels = ['V1', 'V8/9', 'V7/9', 'V2/3', 'V5/9', 'V1/3'][:n_layers]
        return {'kappa_matrix': kappa, 'layers': layers, 'lam_labels': lam_labels}

    # ═══════════════════════════════════════════════════════════════
    # Legacy mixed-family kappa compatibility entry point
    # ═══════════════════════════════════════════════════════════════

    def transport_kappa(self, projectors: list[np.ndarray], compute_kappa1: bool = True) -> tuple:
        """K, κ₀, κ₁ on arbitrary projectors using cached generators + Lie generators.

        This is a legacy compatibility path. It uses cached representation
        matrices and the registered principal-log family; the
        computation itself is delegated to the standalone
        compute_transport_kappa_from_Xs() to avoid duplicating the loop logic.

        Args:
            projectors: list of (n,n) projector matrices (e.g. from center_decomposition).
            compute_kappa1: if True, also compute κ₁ (commutator-based).

        Returns:
            (K, kappa0, kappa1) — three (n_sec, n_sec) arrays.
        """
        import warnings
        warnings.warn(
            "transport_kappa() is a legacy mixed-family diagnostic; compute "
            "direct and Lie supports separately with declared operator families",
            DeprecationWarning,
            stacklevel=2,
        )
        from rime.spectral_utils import compute_transport_kappa_from_Xs
        rhos = [v[1] for v in self.rho_moves.values()]
        Xs = self.registered_principal_log_generators()
        return compute_transport_kappa_from_Xs(rhos, Xs, projectors, compute_kappa1=compute_kappa1)

    # ═══════════════════════════════════════════════════════════════
    # Display
    # ═══════════════════════════════════════════════════════════════

    def summary(self) -> str:
        """One-shot spectral summary — layers, k-values, transport, field."""
        lines = []
        lines.append("=" * 60)
        lines.append(
            f"CubieSpectralOperator  n={self.n}  tol={self.tol}  dim={TOTAL_DIM}  n_layers={len(self._layers)}")
        lines.append(f"  Hermitian: {np.allclose(self.A, self.A.T.conj(), atol=self.tol)}")
        lines.append("=" * 60)

        lines.append("\n  Spectral layers (λ = 1 − k/9):")
        for lam in sorted(self._layers, reverse=True):
            info = self._layers[lam]
            k = round(9 * (1 - lam))
            lines.append(f"    λ={lam:12.8f}  k={k:2d}  dim={info['dim']:4d}")

        lines.append("\n  Slow/fast split:")
        fast_dim = TOTAL_DIM - self.dim_const - self.dim_slow
        lines.append(f"    Const (λ=1):    {self.dim_const:4d}")
        lines.append(f"    Slow  (λ≥2/3):  {self.dim_slow:4d}")
        lines.append(f"    Fast  (λ<2/3):  {fast_dim:4d}")
        rf = self.rho_fast
        lines.append(f"    Fast spectral radius: {rf:.6f}")
        if 0 < rf < 1:
            lines.append(f"    Mixing time (eps=1e-6): {np.log(1e6) / (-np.log(rf)):.1f} steps")

        try:  # 传输图 — transport_tensor 首次调用后缓存
            tg = self.transport_graph()
            lines.append(
                f"\n  Transport: {len(tg['edges'])} edges, hub={'S' + str(round(9 * (1 - tg['hub']))) if tg['hub'] else 'none'}, isolated={len(tg['isolated'])}")
        except Exception:
            pass

        field = self.classify_field()
        lines.append(f"\n  Spectral field: {field}  {spectral_field_label(field)}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"CubieSpectralOperator(n={self.n}, "
                f"n_eigs={len(self.lambda_layers)}, "
                f"slow_dim={self.dim_slow})")


# ═══════════════════════════════════════════════════════════════════
# Module-level utilities (called by class methods above)
# ═══════════════════════════════════════════════════════════════════

def build_h_operators(gens_dict: dict) -> tuple[list[np.ndarray], list[str]]:
    """Build symmetric h_i = (ρ(g) + ρ(g⁻¹))/2 operators from generator dict.

    Returns (h_ops, h_labels) where h_ops are (228,228) arrays.

    对称配对 (axis, ±face, dir) 从 CubieMove dict 自动配对 CW/CCW 和 180° 对面
    """
    from rime.cube import ActionToken
    h_ops, h_labels = [], []

    # CW + CCW 配对: (axis, +1, -1) ↔ (axis, -1, +1)
    for axis in range(3):
        for side in [-1, 1]:
            cw_key = (axis, side, -1)
            ccw_key = (axis, side, 1)
            if cw_key in gens_dict and ccw_key in gens_dict:
                h_ops.append((gens_dict[cw_key].rho() + gens_dict[ccw_key].rho()) / 2)
                at_cw = str(ActionToken.from_cubie_move(*cw_key, n=3))
                at_ccw = str(ActionToken.from_cubie_move(*ccw_key, n=3))
                h_labels.append(f"({at_cw}+{at_ccw})/2")

    # 180° 对面配对: (axis, +1, 2) ↔ (axis, -1, 2)
    for axis in range(3):
        keys_180 = [(axis, side, 2) for side in [-1, 1] if (axis, side, 2) in gens_dict]
        if len(keys_180) == 2:
            h_ops.append((gens_dict[keys_180[0]].rho() + gens_dict[keys_180[1]].rho()) / 2)
            at_a = str(ActionToken.from_cubie_move(*keys_180[0], n=3))
            at_b = str(ActionToken.from_cubie_move(*keys_180[1], n=3))
            h_labels.append(f"({at_a}+{at_b})/2")

    return h_ops, h_labels


def classify_spectral_field(eigs: list[float], m_eff: int) -> str:
    """Classify spectral field as 'rational', 'sqrt5', or 'higher'.
    谱域分类:  m_eff = 有效分母 (= n_gen // 2 偶数时).
    """
    all_rational = all(is_rational_form(lam, m_eff) for lam in eigs)
    if all_rational:
        return 'rational'
    non_rat = [lam for lam in eigs if not is_rational_form(lam, m_eff)]
    if non_rat and all(is_in_qsqrt5(lam)[0] for lam in non_rat):
        return 'sqrt5'
    return 'higher'


def spectral_field_label(set_class: str) -> str:
    """Return LaTeX field notation for a set class.
    域分类 → LaTeX 标记"""
    return {
        'rational': r'$\mathbb{Q}$',
        'sqrt5': r'$\mathbb{Q}(\sqrt{5})$',
        'higher': r'$\mathbb{Q}(\zeta_n)^+$',
    }[set_class]


if __name__ == '__main__':
    pass
