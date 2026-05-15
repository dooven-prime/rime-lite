from rime.cubie import CubieMove, N_GENERATORS, TOTAL_DIM
from rime.base import class_cache,setup_utf8_stdout
from rime.helpers import is_in_qsqrt5, is_rational_form
import numpy as np

setup_utf8_stdout()

class CubieSpectralOperator:
    """Numerical spectral operator - the numerical utility layer.

    Architecture:
      SpectralStructure (theory) -> CubieSpectralOperator (numerics) -> SlowDynamics (dynamics)

    Takes a generator set, builds A = (1/|S|) Sum rho(s), diagonalizes it,
    and provides spectral layers, projectors, block structure, and h_i operators.

    Usage:
        cso = CubieSpectralOperator(n=18)
        cso.summary()
        P = cso.projector(0.777778)
        h_ops, labels = cso.build_h_operators()
        field = cso.classify_field()
    """

    def __init__(self, n: int = N_GENERATORS, generators: dict | None = None, tol: float = 1e-6):
        self.n = n
        self.tol = tol
        self.rho_moves = generators or self.__class__.rho_moves(n)
        rho_gen = [rho for _, rho, *_ in self.rho_moves.values()]
        self.A = np.array(sum(rho_gen) / len(rho_gen), dtype=np.complex128)
        assert np.allclose(self.A, self.A.T.conj(), rtol=tol, atol=tol), "A is not Hermitian"
        self.w, self.V = np.linalg.eigh(self.A)  # 对称特征分解
        idx = np.argsort(-self.w)
        self.w = self.w[idx]
        self.V = self.V[:, idx]
        self._compute_spectral_layers()
        self._ss = None  # lazy SpectralStructure
        self._transport_tensor_cache = None  # lazy, computed on first access

    def _compute_spectral_layers(self) -> None:
        """Compute {lam: {dim, projector}} for each distinct eigenvalue."""
        w_rounded = np.round(self.w, decimals=int(-np.log10(max(self.tol, 1e-10))))
        unique_w = np.unique(w_rounded)
        self.lambda_layers = unique_w
        self._layers = {}
        for lam in unique_w:
            mask = np.abs(self.w - lam) < self.tol
            dim = int(np.sum(mask))
            V_lam = self.V[:, mask]
            P_lam = V_lam @ V_lam.T.conj()
            self._layers[float(lam)] = {'dim': dim, 'projector': P_lam, 'eigenvalue': float(np.mean(self.w[mask]))}
        self.dim_const = int(np.sum(np.abs(self.w - 1.0) < self.tol))
        self.dim_slow = int(np.sum((self.w >= 2 / 3 - self.tol) & (np.abs(self.w - 1.0) >= self.tol)))
        mask_fast = self.w < 2 / 3 - self.tol
        self.rho_fast = float(np.max(np.abs(self.w[mask_fast]))) if np.any(mask_fast) else 0.0

    # -- Classmethods --

    @class_cache('PRIM_RHO_MOVES', key=lambda n: n)
    def rho_moves(cls, n=N_GENERATORS):
        """
        根据生成元规模 n 过滤并缓存 rho 表示字典

        支持的 n 值与过滤规则：
        - 18: 所有 face turns (UDFRLB 各 3 种)
        - 16: 排除某些特定组合
        - 12: 标准 face-turn（k[2] != 2）
        - 10: 部分破缺对称性
        - 21：6个特征值，满足 λ = 1 - k/21，9个 h_i，但只有 12/36 对交换
        - ... (其他 n 如 9,8,6,4,3,2)
        Return {move_key: (CubieMove, rho_matrix)} for given n.
        """
        if n > 18:
            all_moves = CubieMove.prim_moves().copy()
            if n == 21:
                all_moves.update(CubieMove.slice_moves())
                return {k: (mv, mv.rho()) for k, mv in all_moves.items()}
        f = {18: lambda k: True,
             16: lambda k: not (k[0] == 0 and k[2] == 2),
             12: lambda k: k[2] != 2,
             10: lambda k: k[0] == 1 or k[2] == 2,
             9: lambda k: k[1] == 1,
             8: lambda k: k[0] != 1 and k[2] != 2,
             6: lambda k: k[2] == 2,
             4: lambda k: k[0] == 0 and k[2] != 2,
             3: lambda k: k[0] == 0 and k[1] == 1,
             2: lambda k: k[0] == 0 and k[2] == 2}
        match = f.get(n, lambda k: False)
        return {k: (mv, mv.rho().astype(np.complex128))
                for k, mv in CubieMove.prim_moves.items() if match(k)}

    @classmethod
    def lite(cls) -> "CubieSpectralOperator":
        """Return lightweight instance without running full eigenspace decomposition.

        Use this when you only need rho_moves() or other classmethods,
        avoiding the expensive __init__ that computes A_micro, eigh, etc.
        Equivalent to the old pattern: CubieSpectralOperator.__new__(CubieSpectralOperator).
        """
        return cls.__new__(cls)

    @classmethod
    def from_generators(cls, generators: dict, tol: float = 1e-6) -> "CubieSpectralOperator":
        """Construct from an explicit rho_moves dict (internal format).

        Args:
            generators: {move_key: (CubieMove, rho_matrix, permutation_matrix)} dict
            tol: numerical tolerance for eigenvalue clustering
        """
        return cls(n=len(generators), generators=generators, tol=tol)

    @classmethod
    def from_gens_dict(cls, gens_dict: dict, tol: float = 1e-6) -> "CubieSpectralOperator":
        """Construct from a plain {move_key: CubieMove} dictionary.

        This is the common pattern in experiment files: filter prim_moves(),
        pass the result here, get a fully initialized spectral operator back.
        Avoids the manual rhos = [...], A = sum(rhos)/n, eigenspaces(A) dance.

        Args:
            gens_dict: {move_key: CubieMove} (e.g. filtered prim_moves())
            tol: numerical tolerance
        Returns:
            CubieSpectralOperator with full spectral decomposition
        """
        generators = {}
        for k, mv in gens_dict.items():
            generators[k] = (mv, mv.rho().astype(np.complex128))
        return cls(n=len(generators), generators=generators, tol=tol)

    def spectral_evolve(self, x: np.ndarray, T: int) -> np.ndarray:
        """T-step spectral diffusion: x ↦ A^T x = Σ λ_i^T P_i x.

        Uses the eigendecomposition of A = Σ λ_i P_i, so
        A^T = Σ λ_i^T P_i (projectors are mutually orthogonal).
        Avoids constructing the full P_i matrices by projecting
        onto each eigenspace basis directly.
        """
        y = np.zeros_like(x, dtype=complex)
        for lam in self._layers:
            V = self.eigenspace_basis(lam)  # (228, k)
            coeff = V.T.conj() @ x  # (k,)
            y += (lam ** T) * (V @ coeff)
        return y

    def random_walk(self, length: int = 10, p: np.ndarray | None = None) -> "CubieMove":
        """Sample a random length-L word from the generator set.

        Args:
            length: number of generator applications (1 = single move)
            p: optional probability distribution over generators

        Returns:
            CubieMove: the composed group element g_L ··· g_1
        """
        gen = [m for m, *_ in self.rho_moves.values()]
        if length == 1:
            idx = np.random.choice(len(gen), p=p)
            return gen[idx]
        g = CubieMove.identity()
        indices = np.random.choice(len(gen), size=length, p=p)
        for idx in indices:
            g = g.compose(gen[idx])
        return g

    # -- Spectral accessors --

    def spectral_layers(self) -> dict[float, dict]:
        """Return {lam: {dim, projector}} for each distinct eigenvalue."""
        return self._layers

    def projector(self, lam: float = 7 / 9) -> np.ndarray:
        """Spectral projector P_λ = Σ_{v∈E_λ} v v† for a single eigenvalue.

        Args:
            lam: eigenvalue (default 7/9 for the slow sector)
        Returns:
            (TOTAL_DIM, TOTAL_DIM) Hermitian projector matrix
        Raises:
            ValueError if λ is not among the distinct eigenvalues.
        """
        mask = np.abs(self.w - lam) < self.tol
        idx = np.where(mask)[0]
        if len(idx) == 0:
            raise ValueError(f"Eigenvalue {lam} not found")
        return self.V[:, idx] @ self.V[:, idx].T.conj()

    def eigenspace_basis(self, lam: float) -> np.ndarray:
        """Eigenvectors spanning the lambda-eigenspace."""
        mask = np.abs(self.w - lam) < self.tol
        return self.V[:, mask]

    # -- h_i operators --

    def build_h_operators(self) -> tuple[list[np.ndarray], list[str]]:
        """Build symmetric h_i = (rho(g) + rho(g^{-1}))/2.
        Returns (h_ops, h_labels).
        """
        gens_dict = {k: mv for k, (mv, _, _) in self.rho_moves.items()}
        return build_h_operators(gens_dict)

    def classify_field(self) -> str:
        """Classify spectral field: rational, sqrt5, or higher."""
        m_eff = self.n // 2 if self.n % 2 == 0 else self.n
        name = f"n={self.n}"
        return classify_spectral_field(list(self._layers.keys()), m_eff, name=name)

    # -- Projector algebra / transport --

    @property
    def projectors(self) -> np.ndarray:
        """Ordered list of spectral projectors P_i (one per distinct eigenvalue)."""
        return np.array([info['projector'] for _, info in sorted(self._layers.items(), reverse=True)])

    @property
    def layer_dim(self) -> np.ndarray:
        """Array of spectral multiplicities (dimensions) for each eigenvalue layer."""
        return np.array([info['dim'] for _, info in sorted(self._layers.items(), reverse=True)])

    def labelled_projectors(self):
        """Return [(lambda, projector), ...] sorted by eigenvalue descending."""
        for lam in sorted(self._layers, reverse=True):
            yield lam, self._layers[lam]['projector']

    def commutant_residual(self, P: np.ndarray) -> dict:
        """‖[P, ρ(g)]‖_F for every generator — measures how far P is from central.

        Returns {move_key: Frobenius_norm_of_commutator}.
        """
        residuals = {}
        for k, (_, rho, *_) in self.rho_moves.items():
            residuals[k] = float(np.linalg.norm(P @ rho - rho @ P, 'fro'))
        return residuals

    def transport_tensor(self, force_recompute: bool = False) -> dict:
        """Full P_i ρ(g) P_j coupling structure across all generator–projector triples.

        Returns a nested dict keyed by (lam_i, lam_j):
            T[(lam_i, lam_j)] = {'mean': ..., 'max': ...}
        where mean/max aggregate ‖P_i ρ(g) P_j‖_F over all generators.

        Result is cached after first computation; use force_recompute=True to refresh.
        Paper II 核心
        """
        if self._transport_tensor_cache is not None and not force_recompute:
            return self._transport_tensor_cache
        layers = sorted(self._layers, reverse=True)
        T = {}
        for lam_i in layers:
            Pi = self._layers[lam_i]['projector']
            for lam_j in layers:
                Pj = self._layers[lam_j]['projector']
                norms = []
                for _k, (_mv, rho, *_details) in self.rho_moves.items():
                    norms.append(float(np.linalg.norm(Pi @ rho @ Pj, 'fro')))
                T[(lam_i, lam_j)] = {'mean': float(np.mean(norms)),
                                     'max': float(np.max(norms))}
        self._transport_tensor_cache = T
        return T

    def transport_between(self, lam_i: float, lam_j: float) -> dict | None:
        """Transport coupling between two spectral sectors, using closest layer matching.

        Unlike direct dict access `T[(lam_i, lam_j)]` which requires exact float keys,
        this uses _closest_layer() to resolve canonical λ values like 7/9 to the
        actual stored key 0.777778.

        Returns dict {'mean': float, 'max': float} or None if no transport data.
        """
        T = self.transport_tensor()
        ki = self._closest_layer(lam_i)
        kj = self._closest_layer(lam_j)
        return T.get((ki, kj))

    def transport_graph(self, threshold: float | None = None) -> dict:
        """Build the transport graph from the transport tensor.

        Nodes are spectral sectors (λ values). Edges connect sectors with nonzero
        cross-transport under any generator. Self-loops excluded.

        Returns dict with:
            nodes: list of λ values
            edges: list of (lam_i, lam_j, max_weight) for nonzero cross-transport
            adjacency: 5×5 numpy array of max transport norms
            is_star: whether hub structure (all non-isolated edges through one node)
            hub: λ of the hub node (if is_star)
            isolated: list of λ values with no cross-transport
            laplacian: graph Laplacian matrix
        """
        layers = sorted(self._layers, reverse=True)
        n = len(layers)
        T = self.transport_tensor()
        if threshold is None:
            threshold = self.tol * 10

        adj = np.zeros((n, n))
        for i, lam_i in enumerate(layers):
            for j, lam_j in enumerate(layers):
                if i != j:
                    adj[i, j] = T[(lam_i, lam_j)]['max']

        # Mask out numerical zeros
        adj[np.abs(adj) < threshold] = 0.0

        # Build edge list
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                w = max(adj[i, j], adj[j, i])
                if w > threshold:
                    edges.append((layers[i], layers[j], float(w)))

        # Degree and isolated nodes
        degrees = np.array([np.count_nonzero(adj[i]) + np.count_nonzero(adj[:, i])
                            for i in range(n)])
        isolated = [layers[i] for i in range(n) if degrees[i] == 0]

        # Star detection: a star has one hub connected to all other non-isolated nodes
        non_isolated = [i for i in range(n) if degrees[i] > 0]
        is_star = False
        hub = None
        if len(non_isolated) >= 2:
            max_deg_idx = max(non_isolated, key=lambda i: degrees[i])
            hub_candidates = [i for i in non_isolated if degrees[i] >= len(non_isolated) - 1]
            if len(hub_candidates) == 1:
                is_star = True
                hub = layers[hub_candidates[0]]

        # Graph Laplacian: L = D - A (undirected, using max of symmetric pair)
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
            R_{k} = P_{k+1} · ρ(g) · P_k   (transport k → k+1)
            L_{k} = P_{k-1} · ρ(g) · P_k   (transport k → k-1)

        If g_key is None, uses the first generator. Returns dict with:
            pairs: list of (lam_from, lam_to, max_weight)
            R: {(lam_from, lam_to): matrix} raising operators
            L: {(lam_from, lam_to): matrix} lowering operators
            norms: {(lam_from, lam_to): {'R': fro_norm, 'L': fro_norm}}
            closure: {'R†R': ..., 'RR†': ..., 'LR': ..., 'RL': ...} algebraic diagnostics
        """
        layers = sorted(self._layers, reverse=True)
        graph = self.transport_graph()
        edges = graph['edges']

        if g_key is None:
            g_key = list(self.rho_moves.keys())[0]
        _mv, rho_g, *_details = self.rho_moves[g_key]

        R = {}
        L = {}
        norms = {}
        for lam_i, lam_j, _w in edges:
            Pi = self._layers[lam_i]['projector']
            Pj = self._layers[lam_j]['projector']
            R[(lam_i, lam_j)] = Pj @ rho_g @ Pi
            L[(lam_j, lam_i)] = Pi @ rho_g @ Pj
            norms[(lam_i, lam_j)] = {
                'R': float(np.linalg.norm(R[(lam_i, lam_j)], 'fro')),
                'L': float(np.linalg.norm(L[(lam_j, lam_i)], 'fro')),
            }

        # Algebraic diagnostics on the 7/9 ↔ 5/9 pair (the only nontrivial transport chain)
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
                closure['LR'] = float(np.linalg.norm(
                    L_op @ R_op, 'fro'))
                closure['RL'] = float(np.linalg.norm(
                    R_op @ L_op, 'fro'))
                # Check if [L, R] ≈ identity on V_{7/9} (sl(2)-like)
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

    # -- Irreducible decomposition (Artin-Wedderburn within each eigenspace) --

    def _projected_gens_for_layer(self, lam: float) -> tuple[list[np.ndarray], int]:
        """Build projected generators G_k = V_λ† ρ(g_k) V_λ within one eigenspace.

        Used by both irrep_decomposition() and commutant_algebra() — avoids
        duplicating the rho_moves iteration loop.

        Args:
            lam: eigenvalue of the target layer
        Returns:
            (projected_gens, d) where projected_gens is list of (d,d) matrices
        """
        V = self.eigenspace_basis(lam)
        d = V.shape[1]
        projected_gens = []
        for _k, (_mv, rho, *_details) in self.rho_moves.items():
            projected_gens.append(V.T.conj() @ rho @ V)
        return projected_gens, d

    @staticmethod
    def project_commutant(X: np.ndarray, projected_gens: list[np.ndarray], gen_inv: list[np.ndarray] | None = None, n_iter: int = 30) -> np.ndarray:
        """Project a d×d matrix X onto the commutant via group averaging.

        Uses Reynolds operator: R(X) = 1/n Σ_k G_k^H X G_k.
        For generators of order m ≤ 4 (Rubik's cube face turns), the exact
        per-generator centralizer projector P_G(X) = 1/m Σ_t (G^H)^t X G^t
        converges in one step per generator.  The alternating projection onto
        the intersection ∩_k ker[G_k, ·] converges much faster than the
        averaged Reynolds operator.

        For best convergence, use project_commutant_exact() which uses the
        order-4 exact projector.  This method (Reynolds averaging) is kept
        as a faster, lower-precision alternative.
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

        For generator G of order 4 (Rubik's cube face turns):
            P_G(X) = 1/4 Σ_{t=0}^3 (G^H)^t X G^t

        Each per-generator projection is EXACT (maps to ker[G, ·] in one step).
        Iterating over all generators converges to ∩_k ker[G_k, ·] = commutant.

        Converges much faster than Reynolds averaging for blocks where the
        averaged operator has small spectral gap.

        Args:
            X: d×d matrix to project
            projected_gens: list of projected generator matrices
            n_iter: number of full passes over all generators (default 10)
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

    def _commutant_basis_within_block(self, projected_gens: list[np.ndarray], d: int) -> tuple[list[np.ndarray], int]:
        """Build orthonormal basis for the commutant within one eigenspace block.

        Args:
            projected_gens: list of d×d matrices G_k = V† ρ(g_k) V
            d: block dimension

        Returns:
            basis: list of d×d orthonormal commutant basis matrices (Frobenius inner product)
            comm_dim: dimension of commutant
        """
        gen_inv = [G.T.conj() for G in projected_gens]

        if d <= 50:
            # Direct SVD approach — exact nullspace
            constraints = []
            for G_k in projected_gens:
                M_k = np.kron(G_k.T, np.eye(d)) - np.kron(np.eye(d), G_k)
                constraints.append(M_k)
            C = np.vstack(constraints)
            _, s, Vh = np.linalg.svd(C, full_matrices=True)
            sv_thresh = self.tol * max(1.0, s[0]) * max(C.shape)
            null_mask = s < sv_thresh
            comm_dim = int(np.sum(null_mask))
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
        else:
            # Large blocks (d > 50): random sampling + Reynolds projection.
            # The Reynolds operator converges to machine precision (verified:
            # commutator norms ~1e-15 for d=106 after 30 iterations).
            # For blocks this large, the exact SVD constraint matrix would need
            # O(n_gens * d^4) memory which is prohibitive.
            basis, comm_dim = self._commutant_basis_randomized(projected_gens, gen_inv, d)

        return basis, comm_dim

    def _commutant_basis_randomized(self, projected_gens: list[np.ndarray], gen_inv: list[np.ndarray], d: int, n_samples: int | None = None) -> tuple[list[np.ndarray], int]:
        """Enhanced random sampling: Reynolds projection + Gram-Schmidt.

        For d > 50 (where exact SVD is blocked by memory), this is the primary method.
        Uses exact per-generator centralizer projectors (order-4 face turns) for
        faster convergence than simple Reynolds averaging.

        Args:
            projected_gens: projected generator matrices
            gen_inv: conjugate transpose of generators
            d: block dimension
            n_samples: number of random samples

        Returns:
            basis: list of d×d orthonormal commutant basis matrices
            comm_dim: number found (lower bound on true commutant dimension)
        """
        if n_samples is None:
            n_samples = min(d * 8, 800) if d > 50 else min(d * 5, 400)
        basis = []
        gs_tol = self.tol * d * 10
        # Use exact projector for large blocks (better convergence)
        _project = (self.project_commutant_exact if d > 50
                    else self.project_commutant)
        for _ in range(n_samples):
            X = np.random.randn(d, d) + 1j * np.random.randn(d, d)
            if d > 50:
                X = _project(X, projected_gens)
            else:
                X = _project(X, projected_gens, gen_inv)
            # Orthogonalize
            for B in basis:
                X -= np.tensordot(B.conj(), X) * B
            nrm = np.linalg.norm(X, 'fro')
            if nrm > gs_tol:
                basis.append(X / nrm)
        return basis, len(basis)

    def _commutant_center_lightweight(self, comm_basis: list[np.ndarray], d: int) -> tuple[int, list[tuple[int, int, int]]]:
        """Lightweight center detection: diagonalize a random commutant element.

        Avoids the O(r²·d²) memory of the full center computation.
        The eigenspaces of a random C ∈ C approximate the isotypic decomposition.

        Returns:
            center_dim: estimated number of distinct isotypic components
            components: list of (comp_dim, multiplicity, d_irrep) for each eigenspace cluster
        """
        r = len(comm_basis)
        if r == 0:
            return 0, []

        tol = self.tol * d * 10

        # Pick a random Hermitian combination of commutant basis
        C_rand = np.zeros((d, d), dtype=complex)
        for i in range(r):
            coeff = np.random.randn()
            C_rand += coeff * comm_basis[i]
        C_rand = (C_rand + C_rand.T.conj()) / 2  # make Hermitian

        # Diagonalize
        eigvals, U = np.linalg.eigh(C_rand)

        # Cluster eigenvalues
        eigvals_rounded = np.round(eigvals, decimals=max(3, -int(np.log10(tol))))
        unique_eigvals, inverse, counts = np.unique(eigvals_rounded, return_inverse=True,
                                                      return_counts=True)

        # Refine: check if a second random commutant element splits any cluster
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

            U_sub = U[:, mask]  # (d, comp_dim)

            # Check if C_rand2 splits this component
            C2_sub = U_sub.T.conj() @ C_rand2 @ U_sub
            w2 = np.linalg.eigvalsh(C2_sub)
            w2_rounded = np.round(w2, decimals=max(3, -int(np.log10(tol))))
            n_sub = len(np.unique(w2_rounded))

            if n_sub > 1:
                # Component splits — decompose via C2_sub eigenspaces
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

        # For each component, estimate multiplicity from restricted commutant
        result = []
        for comp_dim in final_components:
            # For a single isotypic component of dimension comp_dim = m × d_irrep:
            # restricted commutant dimension = m²
            # Without explicit restricted basis, use eigenvalue spacing heuristic:
            # If comp_dim is small, it's likely a single irrep copy (m=1)
            # Otherwise check for perfect square factors
            # Find largest m such that m² divides something related to comp_dim
            m_est = 1
            for m_cand in range(int(np.sqrt(comp_dim)), 0, -1):
                if comp_dim % m_cand == 0:
                    m_est = m_cand
                    break
            d_irrep = comp_dim // m_est
            result.append((comp_dim, m_est, d_irrep))

        center_dim = len(final_components)
        return center_dim, result

    def _full_commutant_combinatorial(self) -> tuple[list[np.ndarray], int]:
        """Compute commutant basis in the FULL 228-dim space via combinatorial orbits.

        For monomial ρ(g) = D_g Π_g (Π_g=perm, D_g=diagonal phases):
          ρ(g) X = X ρ(g)  ⇔  d_i^{(g)} · X_{π_g^{-1}(i), j} = X_{i, π_g(j)} · d_{π_g(j)}^{(g)}

        This implies entries of X are constant on orbits of the simultaneous action
        (i,j) → (π_g(i), π_g(j)), up to phases that must be consistent along each orbit.

        One orbit = one commutant degree of freedom iff phase consistency holds.

        Returns:
            basis: list of 228×228 orthonormal commutant basis matrices
            comm_dim: total commutant dimension in full space
        """
        d_full = 228
        # Extract permutations and phases from ρ(g_k)
        perms = []   # list of permutations (list of length d_full)
        phases = []  # list of diagonal phase vectors
        for _k, (_mv, rho, *_details) in self.rho_moves.items():
            rho_dense = rho.toarray() if hasattr(rho, 'toarray') else np.array(rho)
            perm = [0] * d_full
            diag = np.zeros(d_full, dtype=complex)
            for col in range(d_full):
                rows = np.where(np.abs(rho_dense[:, col]) > 0.5)[0]
                if len(rows) == 1:
                    row = rows[0]
                    perm[col] = row  # π(col) = row, i.e., e_col → e_row
                    diag[row] = rho_dense[row, col]
                # else: column is all zeros (shouldn't happen for unitary)
            perms.append(perm)
            phases.append(diag)

        # Compute orbits of (i, j) under simultaneous action:
        #   (i, j) → (π_k(i), π_k(j)) for all k
        n_pairs = d_full * d_full
        visited = np.zeros(n_pairs, dtype=bool)
        orbit_map = np.full(n_pairs, -1, dtype=int)  # pair_idx → orbit_id
        orbits = []  # list of lists of pair indices
        g_inv = [[0]*d_full for _ in perms]  # inverse perms
        for g_idx, perm in enumerate(perms):
            for i in range(d_full):
                g_inv[g_idx][perm[i]] = i  # π^{-1}

        for start in range(n_pairs):
            if visited[start]:
                continue
            # BFS to find orbit
            orbit = []
            stack = [start]
            visited[start] = True
            while stack:
                pair_idx = stack.pop()
                orbit.append(pair_idx)
                i, j = divmod(pair_idx, d_full)
                for g_idx in range(len(perms)):
                    ni = perms[g_idx][i]     # π(i)
                    nj = perms[g_idx][j]     # π(j)
                    nidx = ni * d_full + nj
                    if not visited[nidx]:
                        visited[nidx] = True
                        stack.append(nidx)
            orbits.append(orbit)

        # Phase consistency check per orbit.
        # Constraint: d_i^{(g)} · X_{π^{-1}(i), j} = X_{i, π(j)} · d_{π(j)}^{(g)}
        # Walk around orbit cycle: product of phase ratios must be 1.
        basis = []
        for orb in orbits:
            # Pick reference pair in orbit, tentatively set X = 1 there
            # Walk BFS to assign consistent phases to all pairs in orbit
            pair_to_phase = {}
            ref_pair = orb[0]
            pair_to_phase[ref_pair] = 1.0 + 0j
            queue = [ref_pair]
            consistent = True
            while queue and consistent:
                pair_idx = queue.pop(0)
                i, j = divmod(pair_idx, d_full)
                val = pair_to_phase[pair_idx]
                for g_idx in range(len(perms)):
                    pi = perms[g_idx][i]     # π(i)
                    pj = perms[g_idx][j]     # π(j)
                    inv_i = g_inv[g_idx][i]   # π^{-1}(i)
                    inv_j = g_inv[g_idx][j]   # π^{-1}(j)
                    # Forward: (i,j) → (π(i), π(j))
                    # Constraint: d_{inv_i} X_{i,j} = X_{π(i), π(j)} d_{pj}
                    # Wait, let me re-derive from the matrix equation.
                    # ρ(g) @ X = X @ ρ(g)
                    # (ρ @ X)[i,j] = Σ_k ρ[i,k] X[k,j]
                    # For monomial ρ with ρ[i,k] nonzero only at k = π^{-1}(i):
                    #   (ρ @ X)[i,j] = d_i^{(g)} · X[π^{-1}(i), j]
                    # (X @ ρ)[i,j] = Σ_k X[i,k] ρ[k,j]
                    # For monomial ρ with ρ[k,j] nonzero only at k = π(j):
                    #   (X @ ρ)[i,j] = X[i, π(j)] · d_{π(j)}^{(g)}
                    # Equality: d_i^{(g)} · X[π^{-1}(i), j] = X[i, π(j)] · d_{π(j)}^{(g)}
                    # Let a = π^{-1}(i), so i = π(a):
                    #   d_{π(a)}^{(g)} · X[a, j] = X[π(a), π(j)] · d_{π(j)}^{(g)}
                    # So: X[π(a), π(j)] = d_{π(a)}^{(g)} · X[a, j] / d_{π(j)}^{(g)}
                    # In terms of (i,j) → (π(i), π(j)):
                    #   X[π(i), π(j)] = d_{π(i)} · X[i,j] / d_{π(j)}
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
                # Build basis matrix: orthonormal sparse matrix on this orbit
                B = np.zeros((d_full, d_full), dtype=complex)
                # Normalize so |B|_F = 1
                norm_factor = np.sqrt(len(orb))
                for pair_idx, phase_val in pair_to_phase.items():
                    i, j = divmod(pair_idx, d_full)
                    B[i, j] = phase_val / norm_factor
                basis.append(B)

        return basis, len(basis)

    def _center_idempotents(self, comm_basis: list[np.ndarray], d: int) -> tuple[int, list[np.ndarray], list[np.ndarray], list[tuple[int, int]]]:
        """Central primitive idempotents from commutant basis (F1).

        Given commutant basis {C_i} of Comm_G(V_λ), finds center ℨ = Z(Comm_G(V_λ))
        via M^H M nullspace (r×r Gram matrix of commutator constraints), then
        extracts primitive idempotents by joint diagonalization.

        Uses C_rand ∈ ℨ (random center element) for isotypic splitting, then
        C_rand2 ∈ Comm (random commutant element) for multiplicity-fibre splitting.

        Returns:
            center_dim: number of isotypic components (= dim ℨ)
            idempotents: per-irrep-copy projectors (fine-grained, for F3)
            isotypic_projectors: one d×d projector per isotypic component
            isotypic_info: [(d_irrep, multiplicity), ...] per isotypic component
        """
        r = len(comm_basis)
        if r == 0:
            return 0, [], [], []
        if r == 1:
            P = np.eye(d, dtype=complex)
            return 1, [P], [P], [(d, 1)]

        # M^H M where M[a,b] = Σ_j Re(trace([C_a, C_j]^H [C_b, C_j]))
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
            d_alpha = d_alphas[np.argmax([np.sum(w2_counts == d) for d in d_alphas])] if len(d_alphas) > 1 else d_alphas[0]
            m_alpha = comp_dim // d_alpha
            isotypic_info.append((d_alpha, m_alpha))

            for w_val in unique_w2:
                w_mask = np.abs(w2_rounded - w_val) < 10 ** (-decimals)
                n_sub = int(np.sum(w_mask))
                if n_sub == 0:
                    continue
                P = (U_sub @ np.eye(comp_dim)[:, w_mask]) @ (U_sub @ np.eye(comp_dim)[:, w_mask]).T.conj()
                idempotents.append((P + P.conj().T) / 2)

        return len(isotypic_info), idempotents, isotypic_projectors, isotypic_info

    def irrep_decomposition(self) -> dict:
        """Full Artin-Wedderburn decomposition within each spectral eigenspace.

        For each eigenspace V_λ:
        1. Build commutant basis C = {X : [X, ρ(g)] = 0 ∀g on V_λ}
        2. Lightweight isotypic decomposition via random commutant element diagonalization
        3. Decompose into isotypic components V_λ = ⊕_α m_α ⊗ V_α
        4. Extract irrep dimensions d_α and multiplicities m_α

        Returns dict with:
            blocks: {lam: {'dim': d, 'commutant_dim': c, 'center_dim': s,
                           'isotypic': [(d_irrep, multiplicity), ...]}}
            total_isotypic_types: total number of distinct isotypic components
            irrep_sizes: sorted list of (d_irrep, multiplicity, λ_source)
            dim_total: sum of per-block commutant dimensions
        """
        layers = sorted(self._layers, reverse=True)
        result_blocks = {}
        all_irreps = []

        for lam in layers:
            info = self._layers[lam]
            d = info['dim']

            # Build projected generators (shared helper)
            projected_gens, _ = self._projected_gens_for_layer(lam)

            # Step 1: Commutant basis
            comm_basis, comm_dim = self._commutant_basis_within_block(projected_gens, d)

            # Step 2-3: Lightweight isotypic decomposition
            center_dim, isotypic_raw = self._commutant_center_lightweight(comm_basis, d)

            # Step 4: Interpret isotypic components
            # Convert 3-tuples (comp_dim, m_est, d_irrep) → 2-tuples (d_irrep, mult)
            isotypic = [(d_irr, mult) for _, mult, d_irr in isotypic_raw] if isotypic_raw else []

            # If comm_dim == d²: generators act as scalars, irrep is trivial on this block
            if comm_dim == d * d and not isotypic:
                isotypic = [(1, d)]  # d copies of 1D trivial rep
                center_dim = 1

            for d_irrep, mult in isotypic:
                all_irreps.append((d_irrep, mult, float(lam)))

            # Fallback
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

        # Aggregate unique irrep types
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

    def commutant_algebra(self) -> dict:
        """Compute the commutant algebra C = {X : [X, ρ(g)] = 0 for all generators g}.

        Since [X, A] = 0, X is block-diagonal in the eigenbasis of A:
            X = diag(X_1, X_2, ..., X_5) where X_i acts on V_{λ_i}.

        Within each eigenspace, X_i must commute with all projected generators
        P_i ρ(g) P_i. We solve this via SVD of the linear constraint system:
            vec(X_i · G_k - G_k · X_i) = 0 for all k.

        Returns dict with:
            dim_total: total projected commutant dimension (Σ dim C_λ)
            blocks: {lam: {'dim': d, 'commutant_dim': c, 'is_pure': bool,
                           'n_irreps': m (meaningful only if is_pure)}}
            central_idempotents: list of λ where P_λ is central
        """
        layers = sorted(self._layers, reverse=True)
        comm_blocks = {}
        dim_total = 0

        for lam in layers:
            info = self._layers[lam]
            d = info['dim']

            projected_gens, _ = self._projected_gens_for_layer(lam)
            _basis, comm_dim = self._commutant_basis_within_block(projected_gens, d)

            is_pure = (comm_dim == d * d)

            comm_blocks[lam] = {
                'dim': d,
                'commutant_dim': comm_dim,
                'is_pure': is_pure,
                'n_irreps': int(np.round(np.sqrt(comm_dim))) if is_pure else None,
            }
            dim_total += comm_dim

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

    # -- Slow/fast classification ------------------------------------------
    # (dim_const, dim_slow, rho_fast are set in _compute_spectral_layers)

    def slow_fast_split(self, threshold: float = 2 / 3) -> tuple[np.ndarray, np.ndarray]:
        """Split eigenvalue indices into slow (λ ≥ threshold) and fast masks.

        Returns:
            (mask_slow, mask_fast): boolean arrays into self.w / self.V columns.
        """
        mask_slow = self.w >= threshold - self.tol
        return mask_slow, ~mask_slow

    def slow_projector(self, threshold: float = 2 / 3) -> np.ndarray:
        """Projector onto the slow subspace (eigenvalues ≥ threshold)."""
        mask_slow, _ = self.slow_fast_split(threshold)
        V_slow = self.V[:, mask_slow]
        return V_slow @ V_slow.T.conj()

    def slow_basis(self, threshold: float = 2 / 3) -> np.ndarray:
        """Basis vectors (columns) spanning the slow subspace."""
        mask_slow, _ = self.slow_fast_split(threshold)
        return self.V[:, mask_slow]

    # -- SpectralStructure integration --

    @property
    def spectral_structure(self) -> "SpectralStructure":
        """Lazy SpectralStructure for theoretical comparison."""
        if self._ss is None:
            from rime.spectralstructure import SpectralStructure
            gen_dict = {k: mv for k, (mv, _, _) in self.rho_moves.items()}
            self._ss = SpectralStructure(generators=gen_dict)
        return self._ss

    def validate_with_structure(self, ss: "SpectralStructure | None" = None) -> dict:
        """Compare numerical spectrum against SpectralStructure predictions."""
        if ss is None:
            ss = self.spectral_structure
        return ss.validate_with_numerics(cso=self, tol=self.tol)

    # -- Lie Algebra --

    def compute_lie_generators(self) -> list[np.ndarray]:
        """Compute A_g = log(ρ(g)) for all generators via scipy.linalg.logm.

        This is the principal matrix logarithm. For permutation matrices,
        log(ρ) is block-structured by cycle decomposition; for general
        representation matrices (including orientation phases), logm
        correctly captures the full Lie algebra embedding.

        Verification: expm(A_g) ≈ ρ(g) to ~1e-15 for all generators.

        Returns:
            A_gens: list of (n, n) complex matrices, in order of self.rho_moves
        """
        from scipy.linalg import logm
        rhos = [v[1] for v in self.rho_moves.values()]
        A_gens = [logm(rho) for rho in rhos]

        # Quick verification on first call
        if not hasattr(self, '_lie_verified'):
            from scipy.linalg import expm
            max_err = max(np.max(np.abs(expm(Ag) - rho))
                         for Ag, rho in zip(A_gens, rhos))
            if max_err > 1e-10:
                import warnings
                warnings.warn(f"logm fidelity: max|expm(A_g)-rho| = {max_err:.2e}")
            self._lie_verified = True

        return A_gens

    def _closest_layer(self, lam: float) -> float:
        """Return the actual float key in self._layers closest to a canonical eigenvalue.

        self._layers stores eigenvalues as rounded floats (e.g., 0.666667 not 2/3),
        so canonical values like 7/9 need to be matched by proximity.
        """
        return min(self._layers.keys(), key=lambda k: abs(k - lam))

    def infinitesimal_transport(self) -> dict:
        """Compute kappa_ij = max_g ||P_i A_g P_j||_F — infinitesimal transport.

        Continuous analogue of transport_tensor(). Uses scipy.linalg.logm to
        compute correct Lie generators A_g = log(rho(g)). Pairs with kappa_ij > 0
        indicate sectors connected in the continuous (Lie) dynamics.

        Returns dict with:
            kappa: dict {(lam_i, lam_j): {'mean': float, 'max': float}}
            kappa_matrix: (n_layers, n_layers) array of max kappa values
            layers: sorted list of lambda values
        """
        A_gens = self.compute_lie_generators()
        layers = sorted(self._layers, reverse=True)
        n_layers = len(layers)

        kappa = {}
        kappa_matrix = np.zeros((n_layers, n_layers))

        for i, lam_i in enumerate(layers):
            Pi = self._layers[lam_i]['projector']
            for j, lam_j in enumerate(layers):
                Pj = self._layers[lam_j]['projector']
                norms = [np.linalg.norm(Pi @ A_g @ Pj, 'fro') for A_g in A_gens]
                kappa[(lam_i, lam_j)] = {'mean': float(np.mean(norms)),
                                          'max': float(np.max(norms))}
                kappa_matrix[i, j] = max(norms)

        return {
            'kappa': kappa,
            'kappa_matrix': kappa_matrix,
            'layers': layers,
        }

    # -- Primary Object 1: Per-Axis Averaging Operators --

    def build_per_axis_ops(self) -> tuple[dict, list]:
        """Build per-axis QT and HT averaging operators.

        Primary Object 1: A_S for axis-restricted generator subsets.
        Uses self.rho_moves key format: (axis, side, direction).

        Returns:
            ops: dict with keys 'QT0','QT1','QT2','HT0','HT1','HT2','QT_all','HT_all','A_18'
            move_keys: list of move key tuples in rho_moves order
        """
        if hasattr(self, '_per_axis_ops_cache'):
            return self._per_axis_ops_cache, self._per_axis_move_keys

        rhos = [v[1] for v in self.rho_moves.values()]
        move_keys = list(self.rho_moves.keys())
        ops = {}

        ops['A_18'] = sum(rhos) / 18

        qt_idx = [i for i, k in enumerate(move_keys) if k[2] != 2]
        ops['QT_all'] = sum(rhos[i] for i in qt_idx) / len(qt_idx)

        ht_idx = [i for i, k in enumerate(move_keys) if k[2] == 2]
        ops['HT_all'] = sum(rhos[i] for i in ht_idx) / len(ht_idx)

        for axis in range(3):
            qt_ax = [i for i, k in enumerate(move_keys) if k[0] == axis and k[2] != 2]
            ops[f'QT{axis}'] = sum(rhos[i] for i in qt_ax) / len(qt_ax)

        for axis in range(3):
            ht_ax = [i for i, k in enumerate(move_keys) if k[0] == axis and k[2] == 2]
            ops[f'HT{axis}'] = sum(rhos[i] for i in ht_ax) / len(ht_ax)

        self._per_axis_ops_cache = ops
        self._per_axis_move_keys = move_keys
        return ops, move_keys

    @property
    def QT_all(self):
        """QT_all = average of all quarter-turn generators (12 of 18)."""
        ops, _ = self.build_per_axis_ops()
        return ops['QT_all']

    @property
    def HT_all(self):
        """HT_all = average of all half-turn generators (6 of 18)."""
        ops, _ = self.build_per_axis_ops()
        return ops['HT_all']

    @property
    def A_18(self):
        """A_18 = full generator average (alias for self.A)."""
        return self.A

    @property
    def QT0(self):
        """QT on axis 0 (R/L faces)."""
        ops, _ = self.build_per_axis_ops()
        return ops['QT0']

    @property
    def QT1(self):
        """QT on axis 1 (U/D faces)."""
        ops, _ = self.build_per_axis_ops()
        return ops['QT1']

    @property
    def QT2(self):
        """QT on axis 2 (F/B faces)."""
        ops, _ = self.build_per_axis_ops()
        return ops['QT2']

    @property
    def HT0(self):
        """HT on axis 0 (R2/L2)."""
        ops, _ = self.build_per_axis_ops()
        return ops['HT0']

    @property
    def HT1(self):
        """HT on axis 1 (U2/D2)."""
        ops, _ = self.build_per_axis_ops()
        return ops['HT1']

    @property
    def HT2(self):
        """HT on axis 2 (F2/B2)."""
        ops, _ = self.build_per_axis_ops()
        return ops['HT2']

    # -- Primary Object 6: Lie Closure Hierarchy --

    def kappa_depth(self, depth: int = 1, max_commutator_samples: int = 200) -> dict:
        """Compute kappa_d(i,j) at Lie depth d.

        Primary Object 6: Lie closure accessibility hierarchy.
        depth=0: individual A_g (use infinitesimal_transport() for full result)
        depth=1: [A_g, A_h] commutators
        depth=2: [[A_g, A_h], A_k] nested commutators

        Args:
            depth: Lie depth (0, 1, or 2)
            max_commutator_samples: max commutator triples to sample at depth=2

        Returns:
            dict with keys: kappa_matrix, layers, lam_labels
        """
        import itertools
        A_gens = self.compute_lie_generators()
        layers = sorted(self._layers, reverse=True)
        n_layers = len(layers)
        n_gen = len(A_gens)
        P = [self._layers[lam]['projector'] for lam in layers]

        if depth == 0:
            kappa = np.zeros((n_layers, n_layers))
            for i in range(n_layers):
                for j in range(n_layers):
                    kappa[i, j] = max(np.linalg.norm(P[i] @ Ag @ P[j], 'fro') for Ag in A_gens)
        elif depth == 1:
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
                rng = np.random.RandomState(42)
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

        lam_labels = ['V1', 'V7/9', 'V2/3', 'V5/9', 'V1/3'][:n_layers]
        return {'kappa_matrix': kappa, 'layers': layers, 'lam_labels': lam_labels}

    # -- Primary Object 4: Primitive Sectors (Center Decomposition) --

    def center_decomposition(self) -> dict:
        """Joint diagonalization of {A_18, QT_all, HT_all} → 9 primitive sectors.

        Primary Object 4: The minimal simultaneous eigenspaces of the
        commutative center of the averaging algebra.

        Returns:
            dict with keys:
                sectors: list of dicts with dim, lam_18, lam_QT, lam_HT, block_composition
                projectors: list of (228,228) projector matrices
                n_sectors: int (9 for 18-gen system)
        """
        ops, _ = self.build_per_axis_ops()
        A_18 = ops['A_18']
        A_qt = ops['QT_all']
        A_ht = ops['HT_all']

        # Since they all commute, a random linear combination gives joint eigenspaces
        rng = np.random.RandomState(42)
        M = A_18 + rng.randn() * A_qt + rng.randn() * A_ht
        M = (M + M.conj().T) / 2
        evals, evecs = np.linalg.eigh(M)

        # Cluster near-degenerate eigenvalues
        order = np.argsort(evals)[::-1]
        groups = []
        cur = [order[0]]
        cv = evals[order[0]]
        for idx in range(1, len(order)):
            oi = order[idx]
            if abs(evals[oi] - cv) < 1e-8:
                cur.append(oi)
            else:
                groups.append(cur)
                cur = [oi]
                cv = evals[oi]
        groups.append(cur)

        sectors = []
        projectors = []
        for indices in groups:
            V = evecs[:, indices]
            P = V @ V.conj().T
            dim = int(round(np.trace(P).real))
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

        return {'sectors': sectors, 'projectors': projectors, 'n_sectors': len(sectors)}

    # -- Display --

    def summary(self) -> str:
        """Print spectral summary with basic statistics."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"CubieSpectralOperator  n={self.n}  tol={self.tol}")
        lines.append(f"  Hermitian: {np.allclose(self.A, self.A.T.conj(), atol=self.tol)}")
        lines.append(f"  Eigenvalues: {len(self.lambda_layers)} distinct")
        lines.append("=" * 60)
        lines.append("\n  Spectral layers:")
        for lam, info in sorted(self._layers.items(), reverse=True):
            lines.append(f"    lambda={lam:12.8f}  dim={info['dim']:3d}")
        lines.append(f"\n  Subspaces:")
        lines.append(f"    Const (lambda=1):   {self.dim_const:3d}")
        lines.append(f"    Slow  (lambda>=2/3): {self.dim_slow:3d}")
        lines.append(f"    Fast  (lambda<2/3):  {TOTAL_DIM - self.dim_const - self.dim_slow:3d}")
        rf = self.rho_fast
        lines.append(f"    Fast spectral radius: {rf:.6f}")
        if rf > 0 and rf < 1:
            lines.append(f"    Mixing time (eps=1e-6): {np.log(1e6) / (-np.log(rf)):.1f}")
        field = self.classify_field()
        lines.append(f"\n  Spectral field: {field}  {spectral_field_label(field)}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"CubieSpectralOperator(n={self.n}, "
                f"n_eigs={len(self.lambda_layers)}, "
                f"slow_dim={self.dim_slow})")


# Shared spectral utilities (used by _exp_*.py test files)
# ============================================================

def eigenspaces(A: np.ndarray, tol: float = 1e-6) -> dict[float, dict]:
    """Eigenspace decomposition: {eigenvalue: {'dim': int, 'projector': ndarray}}.

    Handles both Hermitian (eigh) and non-Hermitian (eig) matrices.
    Returns only real eigenvalues.
    """
    if np.allclose(A, A.T.conj(), atol=1e-10):
        w, V = np.linalg.eigh(A)
    else:
        w_raw, V_raw = np.linalg.eig(A)
        mask = np.abs(np.imag(w_raw)) < 1e-8
        w, V = np.real(w_raw[mask]), V_raw[:, mask]
    w_rounded = np.round(w, 6)
    unique_w = np.unique(w_rounded)
    result = {}
    for lam in unique_w:
        idx = np.where(w_rounded == lam)[0]
        V_lam = V[:, idx]
        P_lam = V_lam @ V_lam.T.conj()
        result[lam] = {'dim': len(idx), 'projector': P_lam}
    return result


def build_A(gens_dict: dict) -> np.ndarray:
    """Build averaging operator A = (1/|S|) Σ_{s∈S} ρ(s)."""
    rhos = [m.rho() for m in gens_dict.values()]
    return sum(rhos) / len(rhos)


def build_h_operators(gens_dict: dict) -> tuple[list[np.ndarray], list[str]]:
    """Build symmetric h_i = (ρ(g) + ρ(g⁻¹))/2 operators from generator dict.

    Returns (h_ops, h_labels) where h_ops are (228,228) arrays.
    """
    from rime.cube import ActionToken
    h_ops, h_labels = [], []
    for axis in range(3):
        for side in [-1, 1]:
            cw_key = (axis, side, -1)
            ccw_key = (axis, side, 1)
            if cw_key in gens_dict and ccw_key in gens_dict:
                h_ops.append((gens_dict[cw_key].rho() + gens_dict[ccw_key].rho()) / 2)
                at_cw = str(ActionToken.from_cubie_move(*cw_key, n=3))
                at_ccw = str(ActionToken.from_cubie_move(*ccw_key, n=3))
                h_labels.append(f"({at_cw}+{at_ccw})/2")
    for axis in range(3):
        keys_180 = [(axis, side, 2) for side in [-1, 1] if (axis, side, 2) in gens_dict]
        if len(keys_180) == 2:
            h_ops.append((gens_dict[keys_180[0]].rho() + gens_dict[keys_180[1]].rho()) / 2)
            at_a = str(ActionToken.from_cubie_move(*keys_180[0], n=3))
            at_b = str(ActionToken.from_cubie_move(*keys_180[1], n=3))
            h_labels.append(f"({at_a}+{at_b})/2")
    return h_ops, h_labels


def classify_spectral_field(eigs: list[float], m_eff: int, name: str | None = None) -> str:
    """Classify spectral field as 'rational', 'sqrt5', or 'higher'.

    Uses theoretical classification: n=8/n=16 → sqrt5, otherwise based on m_eff check.
    """
    all_rational = all(is_rational_form(lam, m_eff) for lam in eigs)
    if all_rational:
        return 'rational'
    if name in ('n=8', 'n=16'):
        return 'sqrt5'
    # Check if all non-rational eigenvalues are in ℚ(√5)
    non_rat = [lam for lam in eigs if not is_rational_form(lam, m_eff)]
    if non_rat and all(is_in_qsqrt5(lam)[0] for lam in non_rat):
        return 'sqrt5'
    return 'higher'


def spectral_field_label(set_class: str) -> str:
    """Return LaTeX field notation for a set class."""
    return {
        'rational': r'$\mathbb{Q}$',
        'sqrt5': r'$\mathbb{Q}(\sqrt{5})$',
        'higher': r'$\mathbb{Q}(\zeta_n)^+$',
    }[set_class]


if __name__ == '__main__':
    pass
