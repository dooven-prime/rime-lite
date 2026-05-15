import numpy as np
import random, os
from collections import deque
from rime.base import class_status, timer, DATA_DIR
from rime.cubie import CubieState, CubieMove, CubieBase, CubieExample, N_GENERATORS
from rime.cubieoperator import CubieSpectralOperator
from rime.helpers import dbscan, fidelity, softmax, sigmoid, normalize_p, normalize_z, cosine_distance, \
    von_neumann_entropy
import matplotlib.pyplot as plt


class SlowDynamics(CubieSpectralOperator):
    """
    SlowDynamics: Rubik's Cube Phase-1 子群 228 维 faithful 表示下的慢动力学模型,
    群上的 diffusion map/Koopman operator/spectral representation learning
    核心本质：
    本类基于转移算符 A_micro = (1/|S|) ∑ ρ(s) 的谱分解，提取并利用慢子空间（λ ≥ 2/3，100 维）进行高精度动力学近似与低秩表示。
    离散群在连续嵌入空间中的动力系统建模
    现象终结总结：角块扩散、棱块混沌

    ================================
    核心本质（Core Insight）
    ================================
    这是一个“三层混合系统”：

        离散群结构（Group orbits）
        + 连续低频嵌入（Slow manifold）
        + 快速混合噪声（Fast modes）

    表现为：

        ✔ 远区：近似连续梯度系统
        ✔ 中区：混合态（mixing regime）
        ✔ 近区：退化为群轨道动力学（cycle / symmetry dominated）

    Rubik random walk = two-time-scale system, has a two-phase mixing structure
    | subsystem | mixing scale |
    | --------- | ------------ |
    | edge      | ≈5 moves     |
    | corner    | ≈20 moves    |

    1. 谱分层结构（Markov operator spectral stratification）
       - 精确 5 个有理特征值层：1, 7/9, 2/3, 5/9, 1/3
       - 多重度：24, 44, 32, 96, 32
       - 总维度 228 = 100 (慢) + 128 (快)
       - 快层谱半径 ≈ 5/9，确保 20–23 步内充分衰减 (tmix ≈23.5 for ε=10^{-6})
       - 慢层主导长期动力学，T=100 相对误差 < 6×10^{-7}
       - λ=1−k/m,m=∣S∣/2,representation 只选择其中一部分 k,m = effective generator axis
       - edge subsystem mixing time ≈ 5

    2. 平均对称性 vs 瞬时不对称
       - A_micro 属于 5 维交换半单代数，近似 Bose–Mesner 性质（幂等、正交、完备）
       - 生成元 ρ(s) 跨层混合强烈（逃逸误差 0.42–0.46），但泄漏结构化（奇异值 1 或 √3/2）
       - 慢子空间准不变（quasi-invariant），快层作为“热浴”快速均衡

    3. 低秩 & 有效维度
       - generator span rank ≈ 6–11，慢投影后 ≈ 11，平方膨胀至 ≈20 → 非闭合代数 effective dynamics dimension = 6
       - 有效动力学由 ≈5–6 个宏观时间尺度控制（rank-6 attention operator）
       - 可分解为 axis-driven statistical association algebra（轴向统计关联代数）

    4. 群谐性质
       - 前 8 个模式（λ≈1）误差 = 0.000000 → 精确群谐函数
       - λ=7/9 层准谐（误差 ≈0.17 ± 0.444），λ=2/3 layer satisfies the eigenfunction identity E_s[φ(sx)] = λ φ(x)
        exactly due to Aφ=λφ.Eigenfunction identity holds exactly for averaged operator.
       - 分解为：
        invariant
        discrete symmetry modes
        slow statistical modes
        fast mixing modes

    5. 隐藏几何
       - 慢子空间投影呈四重对称星形/十字结构（非 torus）
       - 中心密集核（低深度/solved），四臂向外扩散（高深度）
       - 反映立方对称残留 + 周期性朝向约束
       - 同一个抽象群或结构，在不同维度下有不同的忠实表示 19 × 4 = 76,19 × 12 = 228
       - 高维高斯外观 + 离散群轨道骨架 + 对称子流形
       观测现象：
        • 平均距离 ≈ 6.1（≈ √2 σ √d）
        • 但分布是“壳层结构”：

            0.0 / ~1.1 / ~3.6 / ~5.4 / ~6.1

        → 来源：group word length 的离散投影
    结论：
        欧式距离在 mixing 后失去判别能力（measure concentration）

    6. 算法意义
       - 慢流形截断安全（快层快速衰减 + 无误差放大）
       - representation-aware heuristic d(x,y) = ||V_slow^T (x-y)|| 准等距（1.0059 ± 0.0871）
       - 可用于 A*/IDA* 搜索、生成慢距离 scramble、低秩模拟
        • slow manifold truncation 是安全的
        • dynamics 是低秩可控的
        • 适合：
            - heuristic search
            - reduced simulation
            - representation learning


    7.  --------------------------------
        动力学三阶段（Three Regimes）
        --------------------------------
        — 量化验证：Exp 20（regime 可分性，N=750）、Exp 21（动力学统计，N≈600）、Exp 22（因果，N=500）、Exp 23（轨迹规划）—

        (1) Far Regime（远区，‖tz‖ ≥ 4.0）
            • radial 主导（radial mean η²=0.939, ANOVA across regimes）
            • potential 强，梯度信号明确
            • move 熵 H=2.81±0.07（接近 H_max=log18≈2.89，全方向探索）
            • 2-cycle rate = 1.5%（极少对称捕获）
            • 类似连续梯度下降

        (2) Mid Regime（中区，1.5 ≤ ‖tz‖ < 4.0）
            • radial 与 tangential 竞争（tangential mean η²=0.885）
            • anisotropy 上升，路径不稳定
            • move 熵 H=2.51±0.09（有效方向缩减）
            • 2-cycle rate = 10.0%（对称开始出现）
            • 距离信号衰减

        (3) Near-Target Regime（近区，‖tz‖ < 1.5）【关键难点】
            • radial → 0，potential → 平坦
            • tangential / rot 主导（rot mean η²=0.660）
            • move 熵 H=2.44±0.01（决策空间严重萎缩）
            • **2-cycle rate = 97.8%**（近确定性 g↔g⁻¹ 振荡）
            • inv-in-top-3 = 100%（逆 move 始终在最优候选）
            • **iso-distance shell**（Exp 23）：18 个 move 的 E_base ~相同
              → 打破 2-cycle 也无法改善距离（2-step MPC 0% 2-cycle，但 ‖tz‖ 不变）

        → 本质：连续优化 → 离散群轨道动力学 的相变
        → 2-cycle 是 near-regime 几何退化的**症状**，不是 stall 的**原因**
        → 所有 move 在近区等价（嵌入空间的退化），不是 per-move myopia 能解释的

        慢流形 = “高斯外观的连续空间 + 强离散群轨道骨架 + 局部对称子流形”的混合动力系统
        远区像连续梯度下降，近区退化为群的对称轨道动力学

    8. 几何-行为因果（Causal Geometry → Behavior）
        — Exp 22（Cohen's d, all p<10⁻⁴）—

        | 几何特征          | d（2-cycle vs non） | 方向                       |
        |-------------------|---------------------|----------------------------|
        | curvature         | **+1.42**           | 高弯曲 → 更多 2-cycle        |
        | anisotropy        | +1.35               | 高各向异性 → 更多 2-cycle     |
        | tangential σ      | +1.38               | 切向波动大 → 更多 2-cycle     |
        | ‖tz‖              | **-1.64**           | 远距离 → 少 2-cycle          |
        | radial (best)     | -1.27               | 强径向 → 少 2-cycle          |

        一致模式：几何”扭曲”区域易陷入 2-cycle，强径向 + 远距离提供保护。

    9. 空间几何层（Level 1）
        • 统计外观：近似高维高斯球
            ○ 平均距离稳定在 6.1~6.2（与 √2σ√d ≈ 6.16 高度吻合）
            ○ 但本质不是连续高斯，而是”离散轨道在连续投影下的统计平滑”
        • 壳层结构（Energy Shells）
            ○ 距离呈现明显分层：0.0 / ~1.1 / ~3.6 / ~5.4 / ~6.1…
            ○ 这是 group word-length quantization 在慢流形上的投影体现

    10. 诊断性而非预测性（Diagnostic, Not Predictive）
        — Exps 14–23 的核心结论 —

        ✔ 慢流形是有效的**诊断工具**：
          · d_slow 在近区与 prune distance 相关（r≈0.5 at d≤5）
          · 壳层结构解释了局部贪心搜索的距离阶梯
          · 三区相变解释了为何搜索在目标附近停转
          · Lie curvature 显示慢投影压制非交换性 ~10–100×

        ✘ 但不能提供**预测性** move 排序：
          · E_geom α-sweep：最优 α=0（任意几何权重严格劣化排序）
          · 二次型 E_geom 放大不一致性而非修复
          · 2-step MPC（Exp 23）：完全消除 2-cycle 但 ‖tz‖ 不变
          · 问题不在 per-move myopia，而在嵌入空间本身缺乏群论信息

        使用方式：
            model = SlowDynamics(A_micro)
            z = model.project(state.to_rho())
            z_t = model.evolve(z, T)
            x_t = model.reconstruct(z_t)
        API（详见 Appendix C）：
            model.project(x) / model.lift(z)    — 228D ↔ 76D 投影
            model.move_scores(z, goal)           — 5-component 几何分解
            model.move_energy(z, goal, prev_dz)  — three-regime 能量
            model.lie_curvature(z)               — 局部群弯曲度
            model.chaos_signature(z)             — 非交换性指纹
            CubieMove.inverse_indices()          — 18-generator 逆索引映射

    ── 谱表（18 / 12 generators）─────────────────────────────────────────
    | λ   | dim | 含义              |  12-gen λ  | dim |
    | 1   | 24 | 守恒 / 合法状态     |  1.0       | 24  |
    | 7/9 | 44 | 真实慢模态         |  5/6       | 36  |
    | 2/3 | 32 | 次慢              |  4/6       | 68  |
    | 5/9 | 96 | 中速混合           |  3/6       | 68  |
    | 1/3 | 32 | 快速衰减           |  2/6       | 24  |
    | —   | —  | —                 |  0.0       | 8   |

    λ = 1 − k/m 的代数有理谱来自 partition integrality [1]，不是数值巧合。
    slow/fast split: λ ≥ 2/3 (100D) vs λ ≤ 5/9 (128D), tmix ≈ log(10⁶)/log(9/5) ≈ 23.
    slow manifold is quasi-invariant: generator leakage 0.42–0.46, T=100 error < 6×10⁻⁷.
    effective dynamics rank ≈ 5–6, controlled by a small commutative semisimple algebra C[A] ≅ C⁵.
    
    λ=1 sector = 24 copies of trivial irrep
    谱 + 跃迁代数
    P7/9​ρ(g)P2/3​=0 不存在直接 transport，两条独立 representation channels
    λ=5/9 确认是 interaction hub
    Tij​(g)=Pi​ρ(g)Pj​
    star-like transport algebra
    同时出现：

    group action algebra
    commutant algebra
    Eλ​=⨁α​mα​Vα​

    λ=1: 中心不动子空间 (Central stationary subspace)
    λ=7/9 和 λ=2/3: 慢动力学扇区 (Slow dynamical sectors) — 两者独立，各自内部表示混合。
    λ=5/9: 混合枢纽 (Mixing hub) — 连接所有扇区的核心。
    λ=1/3: 快扇区 (Fast sector) — 单一表示类型，快速衰减。
    """

    def __init__(self, n: int = N_GENERATORS, threshold: float = 2 / 3, tol=1e-6, eps=1e-6,
                 generators=None, k_slow=-1):
        """
        Parameters:
        - n: generator count
        - threshold: slow subspace threshold (default 2/3)
        - tol: numerical tolerance
        """
        super().__init__(n=n, generators=generators, tol=tol)

        # Algebra dimension via SVD
        rho_gen = [rho for _, rho, *_ in self.rho_moves.values()]
        _, s, _ = np.linalg.svd(np.stack([A.reshape(-1) for A in rho_gen]), full_matrices=False)
        self.dim_algebra = np.sum(s > tol)

        # --- invariants ---
        mask_const = np.abs(self.w - 1.0) < tol  # 提取守恒子空间,最大特征值必然是 1
        self.V_const = self.V[:, mask_const]

        # --- slow modes ---
        self.lambda_slow = self.w[~mask_const].max()  # 7 / 9  (λ₂, 次大特征值)
        mask_slow = (self.w >= threshold - tol) & (~mask_const)
        if not np.any(mask_slow):
            mask_slow = np.abs(self.w - self.lambda_slow) < tol
        self.V_slow = self.V[:, mask_slow]
        self.w_slow = self.w[mask_slow]
        self.dim_slow = len(self.w_slow)  # override parent: exclude const
        self.scale_l2 = np.sqrt(2) * 0.5 * np.sqrt(self.dim_slow)  # 平均距离 参考尺度 6.14 6.162 (2.0 * np.pi),把每个坐标近似看成独立高斯分布
        self.V_keep = np.concatenate([self.V_const, self.V_slow], axis=1)

        # Alias for backward compat
        self.A_micro = self.A

        # Pre-cache slow-space compressed operators 预缓存慢空间表示
        self.rho_slow = {k: (mv, self.V_slow.T @ rho @ self.V_slow)
                         for k, (mv, rho, *_) in self.rho_moves.items()}  # (100,100) 约化矩阵

        slow_moves = list(self.rho_slow.values())
        self.U = np.stack([Ug for _, Ug in slow_moves])  # (n, d, d) Uz = U_tensor @ z
        I = np.eye(self.V_slow.shape[1])
        self.D = self.U - I  # (18, 76, 76) D_ops:Ug - I 代替：Ug @ z - z
        self.L = np.diag(np.log(self.w_slow + 1e-12))

        self.C_pairs = {}  # [Ug, Uh]
        self.commutators = {}  # Uc group commutator（非线性）
        for i, (_, Ug) in enumerate(slow_moves):
            for j in range(i + 1, len(slow_moves)):
                _, Uh = slow_moves[j]
                self.C_pairs[(i, j)] = Ug @ Uh - Uh @ Ug
                self.commutators[(i, j)] = Ug @ Uh @ Ug.conj().T @ Uh.conj().T

        M = np.stack([Ug.reshape(-1) for _, Ug in slow_moves], axis=1)
        _, s, _ = np.linalg.svd(M, full_matrices=False)
        self.dim_algebra_slow = np.sum(s > tol)

        A_block = self.V.T.conj() @ self.A_micro @ self.V
        assert np.isclose(np.trace(self.A_micro), np.trace(A_block), atol=1e-6), "trace conservation failed"

        mask_fast = self.w < threshold
        if np.any(mask_fast):
            proj_keep = self.V_keep @ self.V_keep.T.conj()
            proj_fast = np.eye(self.V.shape[0]) - proj_keep
            A_fast = proj_fast @ self.A_micro @ proj_fast
            eigvals_fast = np.linalg.eigvals(A_fast)
            self.rho_f = min(np.max(np.abs(eigvals_fast)), 1 - 1e-8)
            t_mix = np.log(1 / eps) / (-np.log(self.rho_f))  # 23.5043
            self.Tf = int(np.ceil(t_mix))  # 混合时间步数
            print(f"Fast layer spectral radius: {self.rho_f:.6f}, mixing time (eps=1e-6): steps -> Tf={self.Tf}")

    def mutate(self, rho, length: int = 4, p=None):
        """量子变异（commutator chain，保留结构）"""
        gen = list(self.rho_slow.values())
        indices = np.random.choice(len(gen), size=length, p=p)
        U_chain = np.eye(rho.shape[0], dtype=complex)
        g = CubieMove.identity()
        for i in indices:
            m, U = gen[i]
            U_chain = U @ U_chain  # 左乘
            g = g.compose(m)
        rho2 = U_chain @ rho @ U_chain.conj().T
        return rho2 / (np.trace(rho2) + 1e-12), g

    def exact(self, x, T) -> np.ndarray:
        """xT_exact 真实 T 步 vec= A_micro @ vec"""
        return np.linalg.matrix_power(self.A_micro, T) @ x  # (228,)

    def project(self, x):
        """
        表示层,投影到慢子空间,把原 228 维状态压缩到 100 维慢子空间
        """
        return self.V_slow.T @ x  # 返回 (100,) 慢坐标 z0

    def project_move(self, rho_m):
        """慢空间表示,慢层压缩降维,投影变换,真实作用的投影作为参考
        比直接用 已经投影过的 U 更忠实于群作用的原始几何
        一个近似，无法完全忠实还原真实群作用在慢空间的效应
        project(s.vector)用真实作用后再投影,物理上最忠实
        """
        return self.V_slow.T @ rho_m @ self.V_slow  # (100,100) unitary/约化表示

    @staticmethod
    def relative_transform(z0: np.ndarray, z1: np.ndarray) -> np.ndarray:
        """
        计算慢空间中从 z0 到 z1 的最佳线性相对变换矩阵 M (z1 ≈ M @ z0)
        返回 M (76×76 矩阵),只能是近似，不是群同态
        """
        z0 = np.asarray(z0, dtype=complex).reshape(-1, 1)  # 初始慢空间坐标
        z1 = np.asarray(z1, dtype=complex).reshape(-1, 1)

        # 最小二乘求解 M z0 ≈ z1
        M = z1 @ np.linalg.pinv(z0)  # M = z1 @ z0⁺  (Moore-Penrose 伪逆)
        # z_pred = M @ z0
        # error = np.linalg.norm(z_pred.flatten() - z1)# 重建误差
        return M

    def lift(self, z):
        """xT_approx 从慢坐标还原高维状态：x ≈ V_slow z"""
        return self.V_slow @ z  # (228,) 还原回原空间,高维状态

    def evolve(self, z, T):
        """
        谱动力学层,保持慢模演化正确性,zT 微时间指数预测,在慢子空间做  A_micro^T x(t) = x_corner(t) + x_edge(t)
        """
        return (self.w_slow ** T) * z  # (100,) np.multiply(z, self.w_slow ** T) 在慢空间演化 预测 T 步 指数衰减

    def evolve_continuous(self, z, T):
        return np.diag(np.exp(self.L * T)) * z

    def group_action(self, m: CubieMove, z):
        """群元素 ρ(m) 在慢空间的作用,自动继承群乘法：ρ(gh) = ρ(g) ρ(h)"""
        rho_slow = self.project_move(m.rho())  # (100,100) 约化表示
        return rho_slow @ z  # (100,)

    def apply_move(self, key: tuple, z):
        """group_action key move 缓存"""
        _, rho_s = self.rho_slow[key]
        return rho_s @ z  # (100,)

    @staticmethod
    def l2_distance(z0, z1):
        """
        L2 是 backbone
        几何项只能 modulation
        """
        return np.linalg.norm(z0 - z1)

    @staticmethod
    def shell_level(z0, z1):
        """classify 分层能级结构,谱量子化的相空间，slow space 里存在离散轨道壳层,幅度量子化
        用 L2 距离对 slow manifold 做一个粗粒化分区
        np.sqrt(2) * 0.5 * np.sqrt(self.dim_slow)
        注意：
            • 不是严格能级（非量子化）,壳层（shell index）
            • 是 slow manifold 上的“壳层带（shell bands）”
            • 本质来源：group word length 在连续嵌入中的模糊投影

        Distance clusters correspond to projected group word-length:
        ~0        : solved / near identity
        ~1        : small perturbation
        ~3–4      : intermediate
        ~5–6      : mixing region
        """
        d = SlowDynamics.l2_distance(z0, z1)
        # cos_sim = 1 - cosine_distance(z0, z1)
        if d < 1.0:
            return 0, d
        elif d < 2.0:
            return 1, d
        elif d < 4.0:
            return 2, d
        elif d < 6.0:  # self.scale_l2
            return 3, d
        else:  # 高混沌 2*pi
            return 4, d

    def fast_energy(self, x):
        z_slow = self.project(x)
        x_rec = self.lift(z_slow)
        return np.linalg.norm(x - x_rec)

    def heuristic_with_confidence(self, x, y):
        z_delta = self.project(x - y)
        d = np.linalg.norm(z_delta)
        fast_residual = np.linalg.norm((x - y) - self.lift(z_delta))  # 可信度
        confidence = np.exp(-fast_residual)
        return d, confidence

    def heuristic(self, x, y, norm_l2=True):
        """
        计算 Representation-Aware 距离, spectral_diffusion_distance d(x,y) = || V_slow^T (x-y) ||
        Representation Discovery using Harmonic Analysis 系列明确提出用慢特征向量做 heuristic，忽略快模式，提升搜索效率
        input state.vector
        """
        delta = x - y
        z_delta = self.project(delta)  # (100,)
        if norm_l2:
            return np.linalg.norm(z_delta)  # 慢坐标欧氏距离,谱空间 diffusion distance
        return np.sum(np.abs(z_delta))  # np.sqrt(np.sum((np.abs(z_delta) ** 2)))

    def predict(self, state_vector, T: int = 1, const=False):
        """ diffusion map dynamics
        z = V_slowᵀ x
        z_t = λ^t z
        x ≈ V_slow z
        """
        z0 = self.project(state_vector)  # (100,) 投影到慢子空间
        zT = self.evolve(z0, T)  # 微时间演化
        xT_approx = self.lift(zT)
        if const:
            xT_approx += self.V_const @ (self.V_const.T @ state_vector)  # 保持守恒量，保证角棱 parity / sum 等
        return xT_approx.real  # (228,) 返回近似状态向量,np.real(zT)

    def predict_path(self, state_vector, moves: list[tuple] = None, micro_steps=0):
        """路径预测 慢坐标,混合动力学"""
        z = self.project(state_vector)
        if moves is not None:  # 离散群作用,应用 moves 序列
            for m in moves:
                z = self.apply_move(m, z)  # group_action
        if micro_steps > 0:  # 微时间指数预测,长演化
            z = self.evolve(z, micro_steps)
        return

    def behavior_distance(self, z0, z1, samples=5):
        """
        对同一组操作的响应是否相似，衡量慢子空间的行为区分能力,slow manifold 变成了一个“薄壳”
        ≈ 在一个高维球面上随机分布, 方向驱动的动力系统,距离 ≠ 差异,角度 = 差异
        """
        diffs = []
        for _, U in random.sample(list(self.rho_slow.values()), samples):
            za = U @ z0
            zb = U @ z1
            diffs.append(cosine_distance(za, zb))
            # angle_diff = cosine_distance(z_gh, z_hg)
        return np.mean(diffs)

    def build_slow_algebra_basis(self):
        """slow algebra ≈ span{ρ(g), [ρ(g),ρ(h)]}"""
        mats = [U for _, U in self.rho_slow.values()]
        mats += [C for C in self.C_pairs.values()]

        M = np.stack([A.reshape(-1) for A in mats], axis=1)
        U, s, _ = np.linalg.svd(M, full_matrices=False)

        rank = np.sum(s > self.tol)
        # U[:, :rank] is (d², rank); transpose so each row maps to one matrix
        return U[:, :rank].T.reshape(rank, self.dim_slow, self.dim_slow), s[:rank]

    def structure_constants(self):
        """Compute approximate Lie algebra structure constants"""
        basis, _ = self.build_slow_algebra_basis()
        k = len(basis)

        Cijk = np.zeros((k, k, k), dtype=complex)

        for i in range(k):
            for j in range(k):
                comm = basis[i] @ basis[j] - basis[j] @ basis[i]

                # 投影到基
                for l in range(k):
                    Cijk[i, j, l] = np.tensordot(comm.conj(), basis[l])

        return Cijk

    def curvature_ij(self, i, j, z, lie=True):
        """
        几何不稳定性
        分母过强,[Ug, Uh] 在 slow 空间被削弱,slow manifold 把李代数压平了
        C @ z = Ug @ (Uh @ z) - Uh @ (Ug @ z)
        D[i] @ z = Ug @ z - z
        num = || [Ug, Uh] z || = || C_gh z ||
        den = || (Ug - I) z || + || (Uh - I) z ||
        """
        if not lie:  # holonomy curvature
            Uc = self.commutators[(i, j)] if i < j else self.commutators[(j, i)].conj().T
            dz = Uc @ z - z  # 群交换子作用,几何塌缩
            return np.linalg.norm(dz) / (np.linalg.norm(z) + 1e-8)

        C = self.C_pairs[(i, j)] if i < j else -self.C_pairs[(j, i)]  # 反对称

        num = np.linalg.norm(C @ z)  # 局部线性量“非交换结构矩阵”

        di = self.D[i] @ z
        dj = self.D[j] @ z

        den = np.linalg.norm(di) + np.linalg.norm(dj) + 1e-8
        return num / den

    def lie_curvature(self, z, k: int = 6, sample=True) -> float:
        """单位扰动下产生的非交换程度,规范化曲率,几何性质≈ 群结构常数
        curvature(z) = ||[Ug,Uh]z|| / (||Ug z - z|| + ||Uh z - z||)
        用随机抽样，否则全量统计会完全平滑掉局部信号 0.013
        """
        if sample:
            idx = np.random.choice(len(self.rho_slow), size=(k, 2), replace=False)
            curvs = [self.curvature_ij(i, j, z, True) for i, j in idx]
        else:
            Uz = np.einsum('nij,j->ni', self.U, z)  # (n,d)
            dz = Uz - z
            norm_dz = np.linalg.norm(dz, axis=1)
            idx = np.argsort(norm_dz)[-k:]
            # w = norm_dz[idx]
            # w = w / (np.sum(w) + 1e-8)
            curvs = [self.curvature_ij(i, j, z, True) for a, i in enumerate(idx)
                     for b, j in enumerate(idx) if a < b]

        return np.mean(curvs)  # np.percentile(curvatures, 75)

    def chaos_signature(self, z, samples=6):
        """
        动力扰动,交换子带来的“幅度差”,非交换性的动力学 fingerprint, 通过随机选取两个 move 的交换子作用在 z 上，测量结果的差异来量化非交换性
        测z 所在区域的“动力学弯曲程度”，局部李代数非交换性的离散采样估计||UgUh(z) - UhUg(z)||
        chaos ≈ curvature
        """
        n = len(self.rho_slow)
        sig = []
        for _ in range(samples):
            i, j = random.sample(range(n), 2)
            if i < j:
                C = self.C_pairs[(i, j)]
            else:
                C = -self.C_pairs[(j, i)]
            l2_diff = np.linalg.norm(C @ z)  # chaos 强度: Ug @ (Uh @ z) - Uh @ (Ug @ z)
            sig.append(l2_diff)
        return np.array(sig)  # mean/std

    def move_scores(self, z, target, preference=None, eps=3.0):
        """
        当状态已经很接近目标时，不同 move 对 z 的“推动方向”差异变得非常小,慢距离本身在接近目标时分辨率不足
        接近目标时：mean_target_dist 0.397~0.483
        max_chaos 0.397,max_chaos 0.860
        边界退化,被推到一个混合平衡态,须引入微扰,人为注入不对称性,否则系统会卡在对称点
        align → 近目标 → 自动衰减
        target_dist → 近目标 → 梯度消失
        sin_theta → 成主导（导致绕圈 / 平衡轨道）
        梯度流 + 旋度流 拼特征

        核心原则：
            • target_dist = backbone（唯一稳定信号）
            • radial / tangential = 正交分解
            • near-target 强化 symmetry breaking

        后续归一化（非常关键）
        """
        # 当前 z 的演化 z2 = U @ z
        Uz = np.einsum('nij,j->ni', self.U, z)  # (n,d)
        dz = Uz - z  # (n,d) 动力向量
        tz = target - z
        tz_norm = np.linalg.norm(tz)  # 当前到目标的总距离（标量） np.dot(tz, tz)
        dz_norm = np.linalg.norm(dz, axis=1)  # (n_moves,) chaos 每个 move 的移动长度  np.sum(dz * dz, axis=1)

        # 极坐标动力学分解
        inner = np.real(np.einsum('ni,i->n', dz, tz))  # align dot dE 基础方向投影,朝目标方向的曲率,0.5-1.37
        radial = inner / (tz_norm + 1e-8)  # = ||dz|| cosθ
        cos_theta = inner / (dz_norm * tz_norm + 1e-8)  # cosθ alignment（吸引项） 归一化角度
        sin_theta = np.sqrt(np.maximum(1.0 - cos_theta ** 2, 0.0))  # 旋转强度（切向分量） phase（旋转项）
        tangential = dz_norm * sin_theta  # 适度鼓励旋转探索（避免死绕圈） np.linalg.norm(dz - proj, axis=1)
        if tz_norm < eps:
            radial *= 0.0
            tangential = dz_norm  # 全部当作绕行

        target_dist = np.linalg.norm(Uz - target, axis=1)  # 目标驱动 目标距离 势能吸引 energy
        chaos = dz_norm

        pref = np.zeros_like(chaos)
        if preference is not None:
            pref = np.real(np.einsum('ni,i->n', dz, preference))  # 生态位偏好偏置（打破对称性）对称性破缺

        scores = np.stack([
            target_dist,  # 0: global correctness（越小越好）
            -radial,  # 1: 径向（越大越好）
            tangential,  # 2: 切向（探索/绕）
            chaos,  # 3: 扰动,动量,扩散 0.7-5.4
            pref  # 4: 对称性破缺
        ], axis=1)

        # chaos = dz_norm / self.scale_l2
        # alpha = 1.0 / (1.0 + np.exp(2.5 * (tz_norm - self.scale_l2/2)))
        # energy = (
        #         1.0 * delta_dist  # 局部势差
        #         - 0.8 * cos_theta  # 主驱动 drift
        #         - 0.35 * sin_theta * dz_norm  # 负号 切向扰动强度（鼓励结构探索）
        #         + 0.2 * dz_norm ** 2  # 扩散（探索） diffusion
        #     # + 0.15 * pref_bias  # 打破对称性
        # )  # 加权 np.dot(raw_scores, w)
        return scores

    @class_status("待完善")
    def move_energy(self, z, target, prev_dz=None):
        """
        几何能量函数：势能 + 几何修正（radial / tangential / curvature）
        energy 函数尚未“大一统”——远区引导强，近区被 metric + 对称性压制，2-cycle 仍频繁出现。

        E = <dz, ∇V> + <dz, G(z) dz>
        （Fredholm / 紧算子视角）

        ================================
        1. 动力学分区（Three Regimes）
        ================================

        Far Regime（远区）
            ||tz|| large
            • radial 主导，potential 强
            • move ranking 有意义（≈ L2 正确排序）
            • energy 表现稳定

        Mixing Regime（混合区）
            • radial 与 tangential 竞争
            • anisotropy 上升，curvature 开始起作用
            • 欧式距离区分能力下降（进入 shell overlap）

        Near-Target Regime（近目标区）【核心困难】
            ||tz|| → small
            • radial → 0
            • potential → flat
            • tangential / orbit motion 主导
            • metric 容易压倒 potential
            • move_scores 区分度崩塌
            • 出现大量：
                - 2-cycle（g ↔ g⁻¹）
                - dir==2 对称陷阱
                - orbit / cycle 行为
            引入“破坏细致平衡”的项

        ================================
        2. 群对称性主导现象（Level-3）
        ================================

        • 2-cycle orbit（最稳定吸引子）
            - g ↔ g⁻¹ 振荡
            - move 分布集中在成对操作
            - 原因：投影后 U ≈ U⁻¹（方向信息丢失）
            manifestation:
            - paired move dominance
            - undo/redo loops

        • dir==2 / 180° 对称陷阱
            - radial ↓, tangential ↓, rot ≈ 0
            - energy 在这些方向近似平坦
            - 状态在对称子空间振荡（UD-like subspace）

        • Involution-like behavior
            - 多个 move 在 slow manifold 上近似互逆
            - greedy 策略 → undo / redo 循环

        • 对称子流形（Symmetric Submanifold）
            - 局部近似 Abel（低交换子）
            - 有效自由度降低
            - 非交换结构被投影压平

        ================================
        3. Energy 失效模式（必须牢记）
        ================================

        • Metric 主导问题（最危险）
            - quadratic（radial² + tangential²）过强
            → 压制 potential
            → 系统变成“少动优先”，而不是“朝目标走”

        • 对称性区分失败
            - dir==2 / Z-axis 区域：
                radial / tangential / rot 同时变弱
                所有几何量同时变小
            → energy 无法区分 move

        • 近区退化
            - norm_tz → 0
            → 所有信号衰减
            → energy landscape flatten
            在 near-target：
                radial → 0
                tangential → 弱
                rot → 弱
            → 所有动作分数接近

        ================================
        4. Ground Truth（强约束原则）
        ================================

        ||Uz - target||  （L2 distance）

        全局排序最可靠（backbone）
        在任何 regime 都不完全失效

        原则：
            L2 ranking is ground truth backbone
            geometric terms only modulate, never dominate

        ================================
        5. 关键系统事实（防误判）
        ================================

        • dir==2 / 2-cycle ≠ bug
            → 是群轨道（orbit phenomenon）

        • 接近目标 ≠ 更容易
            → 实际进入 isotropic + symmetry-dominated 区域

        • 当前系统 ≠ 连续优化
            → 本质是：
                continuous embedding + discrete orbit dynamics

        • move 行为：
            → progress + orbit + involution 混合

        ================================
        6. 额外动力学补偿（经验）
        ================================

        • prev_dz（动量项）用于：
            - 打破 2-cycle
            - 提供时间方向（temporal asymmetry）

        • 无 prev_dz 时：
            → 极易进入 orbit / 绕圈

        ================================
        7. 总结
        ================================

        魔方慢流形不是连续优化问题，
        而是：
            “离散群轨道 + 连续嵌入 + 对称性主导”的动力系统

        本函数的作用：
            提供一个“近似排序信号”，而不是精确物理能量

        对称性导致有效自由度降低，流体“冻结”成了具有周期性的结构。
        The system is governed by a global L2 potential, locally guided by geometric derivatives in the far regime, and stabilized by symmetry-breaking trajectory terms in the near-target regime, where continuous dynamics collapse into discrete group orbits.
        """
        Uz = np.einsum('nij,j->ni', self.U, z)  # (n,d)
        dz = Uz - z  # (n,d)
        tz = target - z
        norm_dz = np.linalg.norm(dz, axis=1)  # np.sum(np.abs(dz)**2, axis=1)
        norm_tz = np.linalg.norm(tz)

        # --- 分解 dz ---
        tz_unit = tz / (norm_tz + 1e-8)
        radial = np.real(np.einsum('ni,i->n', np.conj(dz), tz_unit))  # 投影到径向方向
        tangential = np.linalg.norm(dz - np.outer(radial, tz_unit), axis=1)  # 切向分量（垂直于径向）
        #  全局 backbone：L2 距离（E_base）
        E_base = np.linalg.norm(Uz - target, axis=1)  # distance L2 主干，高度势能
        # --- 势驱动 ---
        inner = np.einsum('ni,i->n', np.conj(dz), tz)  # Hermitian 内积 <dz | tz>
        E_potential = -np.real(inner)  # 朝目标移动，只在远区参与 energy 降低,线性泛函，类似 <dz, ∇V>
        # --- rotation ---
        rot = np.abs(np.imag(inner))  # 虚部 旋转（绕 target）

        # --- 几何度规 metric ---
        # best_align = np.argsort(potential)
        # i1, i2 = best_align[0], best_align[1]
        # # curvature = self.curvature_ij(i1, i2, z, lie=True)  # 0~0.12 方向驱动的曲率,路是否稳定,大:增加探索需求,纠结区域打破对称性
        anisotropy = np.mean(tangential) / (np.mean(np.abs(radial)) + 1e-8)  # 策略各向异性 1.7,3.6,6
        curvature = np.log1p(anisotropy)  # 探索相变变量 2.0 * np.tanh(anisotropy / 2.0) [0, 2]
        # curvature = tangential / (radial + 1e-8)

        # E_geom = 0.5 * radial ** 2 +  (1.0 + curvature) * tangential
        # 流体介质本身的阻力 + 涡旋效应 + 局部硬度带来的额外成本
        E_geom = radial + tangential + curvature * rot  # 局部度规修正，鼓励 radial 和 tangential，特别是在高曲率区域（纠结区）增加旋转奖励，促进探索
        # E_geom_norm = (
        #     radial / (norm_tz + 1e-8)
        #     + tangential / (norm_dz + 1e-8)
        #     + curvature * rot / (norm_tz * norm_dz + 1e-8)
        # )
        # quadratic = 0.5 * radial ** 2 + (1.0 + curvature) * tangential ** 2  # 只在纠结区域加强成本,随 z 变化的正定紧自伴算子
        # E_metric = quadratic / (norm_dz ** 2 + 1e-12)

        # --- regime gating ---
        # alpha = 1.0 / (1.0 + np.exp(-3.0 * (norm_tz - 2.0)))
        alpha = np.clip(norm_tz / self.scale_l2, 0.0, 1.0)  # 远区≈1，近区≈0
        # beta = np.clip(1.0 - norm_tz / 2.0, 0.0, 1.0) # 远区=0，近区=1
        # energy = potential + metric
        # 动态 gating（远区几何主导，近区 L2 主导）
        E = (
                E_base  # 主干（不调权重）L2 始终是 backbone
                + (0.25 * alpha + 0.05) * E_geom  # 远区强，近区弱，远区几何权重高
                + 0.15 * alpha * E_potential  # 只在远区提供方向，近区势能拉力
        )

        # + 0.03 * np.clip(E_metric - 1.0, 0.0, None)  # 超过各向同性才惩罚,惩罚项系数很小，避免主导
        # + 0.05 * curvature * (rot + 0.5 * rot ** 2)

        # print(E_target, radial, tangential)
        # 时间箭头 + 对称惩罚 + 惯性阻尼 time arrow vdot(dz, prev_dz)
        E_traj = 0.0
        if prev_dz is not None:  # 鼓励同向，惩罚反向
            # 计算当前候选 move 与上一步 move 的“相似度”（越相似越惩罚）
            cos_traj = np.real(np.einsum('ni,i->n', np.conj(dz), prev_dz)) / (norm_dz * np.linalg.norm(prev_dz) + 1e-8)
            E_traj = 1.0 - cos_traj
            E += 0.25 * E_traj  # 防 2-cycle

        # local_term =  0.3 * norm_dz**2 + 0.3 * tangential**2
        # metric = alpha * metric + (1.0 - alpha) * local_term # 平滑混合

        return E

    # def move_energy(self, z, target, *args):
    #     """
    #     统一的几何能量函数：势能 + 径向成本 + 切向成本
    #     几何能量函数：势能 + 径向成本 + 切向成本
    #     E=⟨dz,G(z)dz⟩+⟨dz,∇V(z)⟩
    #     E = <dz, ∇V> + <dz, G(z) dz> Fredholm / 紧算子
    #     接近目标 → 各向同性
    #     """
    #     Uz = np.einsum('nij,j->ni', self.U, z)  # (n,d)
    #     dz = Uz - z
    #     tz = target - z
    #
    #     norm_dz = np.linalg.norm(dz, axis=1)
    #     norm_tz = np.linalg.norm(tz)
    #
    #     # --- 分解 dz ---
    #     tz_norm = tz / (norm_tz + 1e-8)
    #     radial = np.einsum('ni,i->n', dz, tz_norm)  # 投影到径向方向
    #     tangential = np.linalg.norm(dz - np.outer(radial, tz_norm), axis=1)  # 切向分量（垂直于径向）
    #
    #     # --- 势驱动 ---
    #     potential = -np.einsum('ni,i->n', dz, tz)  # 朝目标移动energy 降低,线性泛函，类似 <dz, ∇V>
    #
    #     # --- 几何度规 metric ---
    #     best_align = np.argsort(potential)
    #     i1, i2 = best_align[0], best_align[1]
    #     curvature = self.curvature_ij(i1, i2, z, lie=True)  # 0~0.12 方向驱动的曲率,路是否稳定,大:增加探索需求
    #     metric = 0.5 * radial ** 2 + (1.0 + curvature) * tangential ** 2  # 只在纠结区域加强成本
    #
    #     # local_term =  0.3 * norm_dz**2 + 0.3 * tangential**2
    #     # alpha = np.clip(norm_tz / np.pi, 0.0, 1.0)
    #     # metric = alpha * metric + (1.0 - alpha) * local_term # 平滑混合
    #
    #     energy = potential + metric
    #     return np.real(energy)

    def move_energy_kg(self, z, target):
        """
        三阶稀疏张量（千亿级三元组） 谱投影 embedding
        (state1, move, state2) 知识图谱嵌入空间
        dz = U @ z - z
        平移 + 旋转
        """
        Uz = np.einsum('nij,j->ni', self.U, z)  # 所有可能的下一状态
        dz = Uz - z

        # TransE-style 平移 + RotatE-style 旋转
        translation_loss = np.linalg.norm(Uz - target, axis=1)  # 平移
        rotation_loss = np.abs(np.imag(np.einsum('ni,i->n', dz, target - z)))  # 旋转分量（虚部）

        energy = (
                1.0 * translation_loss
                + 0.5 * rotation_loss
                + 0.2 * np.linalg.norm(dz, axis=1)  # chaos 捕捉非对称
        )
        return energy

    def bfs_slow(self, z_start, z_goal, max_depth=40):
        """
        在慢子空间上做 BFS，目标是 z_goal
        返回：路径长度、最终慢距离、是否到达
        """
        if z_goal is None:
            goal_state = CubieState.solved()
            z_goal = self.project(goal_state.vector)  # 预计算目标慢坐标

        queue = deque([(z_start.copy(), 0, [])])  # (z, depth, path)
        visited = set()

        while queue:
            z_curr, depth, path = queue.popleft()
            z_tuple = tuple(np.round(z_curr, 6))  # 离散化避免浮点重复
            if z_tuple in visited:
                continue
            visited.add(z_tuple)

            dist = self.l2_distance(z_curr, z_goal)
            if dist < 1e-4 or depth >= max_depth:
                return path, dist, depth

            for k in self.rho_slow.keys():
                if len(path) > 0 and CubieMove.is_redundant(path[-1], k):
                    continue
                z_next = self.apply_move(k, z_curr)
                new_path = path + [k]
                queue.append((z_next, depth + 1, new_path))

        return None, self.l2_distance(z_curr, z_goal), max_depth

    def greedy_search_slow(self, s_start: CubieState, s_goal: CubieState, max_depth=40, tau=0.1, min_dist=1.0):
        """
            两阶段搜索：
            1. 用 energy greedy 快速逼近（dist < 1.0）
            2. 逼近后切换到真实群作用精确搜索
        """
        state = s_start.clone()
        path = []
        z_goal = self.project(s_goal.vector)
        moves = list(self.rho_slow.values())
        prev_dz = None
        for depth in range(max_depth):
            z_curr = self.project(state.vector)
            dist = self.l2_distance(z_curr, z_goal)

            if dist < min_dist:
                return path, dist, depth

            energy = self.move_energy(z_curr, z_goal, prev_dz)
            if random.random() < 0.15:  # 15% 的随机扰动概率不选最优，而是选前3个之一
                top3 = np.argsort(energy)[:3]
                top3_energy = energy[top3]
                logits = -top3_energy / (tau + 1e-8)
                logits -= np.max(logits)
                pi = np.exp(logits)
                pi /= pi.sum()
                best_idx = np.random.choice(top3, p=pi)
            else:  # 选 energy 最小的那个 move（top1）
                best_idx = np.argmin(energy)

            best_move, U = moves[best_idx]
            state = best_move.act(state)
            prev_dz = U @ z_curr - z_curr  # 形状 (dim,)
            path.append(best_idx)

        final_dist = self.l2_distance(self.project(state.vector), z_goal)
        return path, final_dist, max_depth

    def guided_search_slow(self, s_start: CubieState, s_goal: CubieState, max_depth=30, beam_width=3, min_dist=1e-3):
        """
        A* 风格搜索（贪心版 + beam search） 目标是 z_goal
        使用慢坐标距离指导的贪心/束搜索
        - moves: list of ρ(s) (27 个生成元)
        - beam_width: 束宽度（限制探索分支）
        # z_goal = model.project(CubieState.solved().vector)
        # z_start = model.project(initial_state.vector)
        """
        from heapq import heappush, heappop
        from itertools import count

        # 优先队列：(距离, 深度, z_current, path)
        pq = []
        counter = count()
        heappush(pq, (0.0, 0, next(counter), s_start, []))

        visited = {}  # state -> best_depth
        z_goal = self.project(s_goal.vector)
        while pq:
            f, depth, _, state, path = heappop(pq)
            if depth > max_depth:  # 深度限制
                continue
            if state in visited and visited[state] <= depth:
                continue
            visited[state] = depth

            z_curr = self.project(state.vector)
            dist = self.l2_distance(z_curr, z_goal)
            if dist < min_dist:  # 到达目标
                return path, dist, depth

            raw_scores = self.move_scores(z_curr, z_goal, eps=2.0)
            if raw_scores[:, 2].sum() < 1e-6:
                return path, dist, depth

            scores_z = np.zeros_like(raw_scores)
            for i in range(raw_scores.shape[1]):
                scores_z[:, i] = (raw_scores[:, i] - raw_scores[:, i].mean()) / (raw_scores[:, i].std() + 1e-8)

            w = [1.0, 0.4, 0.15, 0.1, 0.0]
            scores = np.dot(scores_z, w)
            # if depth % Tf == 0:
            #     z_curr = self.evolve(z_curr, Tf)  # 模拟快层混合,随机采样几步完整演化
            # 生成后继
            successors = []
            for i, (m, U) in enumerate(self.rho_slow.values()):
                next_state = m.act(state)  # U @ z_curr
                cost = scores[i]  # 主驱动：靠近目标
                successors.append((cost, depth + 1, next(counter), next_state, path + [i]))

            # 按距离排序，取 beam_width 个最好
            successors.sort(key=lambda x: x[0])
            for succ in successors[:beam_width]:
                heappush(pq, succ)

        return None, float('inf'), max_depth  # 未找到

    @staticmethod
    def ida_star_slow(model: 'SlowDynamics', start_state: CubieState, goal_state=None, depth_limit=20):
        """
        IDA* 版本：用慢距离作为界
        """
        if goal_state is None:
            goal_state = CubieState.solved()

        z_goal = model.project(goal_state.vector)
        z_start = model.project(start_state.vector)

        def dfs(z_curr, g, bound, path):
            h = model.l2_distance(z_curr, z_goal)
            # z_next = self.project(next_state.vector)  
            # dz = z_next - z_curr
            # h = np.linalg.norm(z_next - z_goal) / model.scale_l2
            # align = np.dot(dz, z_goal - z_curr).real / (np.linalg.norm(dz) * np.linalg.norm(z_goal - z_curr) + 1e-8)
            # chaos = np.linalg.norm(dz) / model.scale_l2
            f = g + h
            if f > bound:
                return f
            if h < 1e-4:
                return path

            min_next = float('inf')
            for k, move in CubieMove.phase1_moves().items():
                if len(path) > 0 and CubieMove.is_redundant(path[-1], k):
                    continue

                z_next = model.apply_move(k, z_curr)
                res = dfs(z_next, g + 1, bound, path + [k])
                if isinstance(res, list):
                    return res
                min_next = min(min_next, res)

            return min_next

        bound = model.l2_distance(z_start, z_goal)
        while True:
            res = dfs(z_start, 0, bound, [])
            if isinstance(res, list):
                return res, bound
            if res == float('inf'):
                return None, bound
            bound = res


class QuantumAgent:
    """
      Minimal quantum agent:
    - density state
    - entropy / purity
    """

    def __init__(self, state, model: SlowDynamics):
        z = model.project(state.vector)
        z = z / (np.linalg.norm(z) + 1e-12)

        self.rho = np.outer(z, z.conj())  # density 密度矩阵（Hermitian, trace=1）
        self.energy = self.entropy()
        self.pos = np.random.randn(2) * 5
        self.age = 0

    def purity(self):
        return np.real(np.trace(self.rho @ self.rho))

    def entropy(self):
        """
        von_neumann_entropy S = -Tr(ρ ln ρ)
        """
        w = np.linalg.eigvalsh(self.rho)
        w = w[w > 1e-12]  # np.abs(agent.z)**2
        return -np.sum(w * np.log(w)) if len(w) > 0 else 0.0

    def rho_divergence(self, rho, mode: str = "trace"):
        if mode == "relative":  # 相对纯度差异
            return abs(np.real(np.trace(self.rho @ self.rho)) - np.real(np.trace(rho @ rho)))
        elif mode == "trace":  # 迹距离（Hilbert-Schmidt） 核范数
            return 0.5 * np.linalg.norm(self.rho - rho, ord='nuc')
        elif mode == 'fro':  # Frobenius 范数距离（最常用、最稳定）
            return np.linalg.norm(self.rho - rho, 'fro')

        fid = fidelity(self.rho, rho)
        return np.sqrt(2.0 - 2.0 * fid)  # Bures距离

    def expected_z(self):
        # 主方向（最大特征向量）
        w, V = np.linalg.eigh(self.rho)
        return V[:, np.argmax(w)]

    def species(self):
        """主特征向量签名,物种/基因/信仰"""
        v = self.expected_z()
        return tuple(np.sign(v.real[:6]))  # 简单hash

    def move(self):
        self.pos += 0.3 * np.random.randn(2)


class QuantumSimulation:
    """
    群结构（严格约束）
    慢流形（低维动力）
    量子概率（密度矩阵）
    统计力学（entropy/purity）
    进化（reproduce/mutate）
    密度矩阵版：连续、可微、必然均匀化（heat death）
    """

    def __init__(self, model: SlowDynamics, n_agents=20):
        self.model = model
        self.moves = [rho_s for _, rho_s in model.rho_slow.values()]
        self.agents = [
            QuantumAgent(CubieBase.generate_cubie(10), model)
            for _ in range(n_agents)
        ]

        self.history = []  # 记录纯度、熵、交换子强度

    def chaos_density(self, rho, samples: int = 20, commutator=True):
        """用交换子 [U, ρ] 量化量子非对易性/相干性
        简化版 C(t) ≈ || UW^t UV UW^{-t} ρ UW^t UV† UW^{-t} - ρ ||
        """
        total = 0
        for _ in range(samples):
            if commutator:
                Uc = random.choice(self.model.commutators.values())  # commutator 链 216
                rho2 = Uc @ rho @ Uc.conj().T
                total += np.linalg.norm(rho2 - rho, 'fro')  # || Uc ρ Uc† - ρ || 非交换性
            else:
                C_gh = random.choice(self.model.C_pairs.values())
                rho_diff = C_gh @ rho @ C_gh.conj().T
                total += np.linalg.norm(rho_diff, 'fro')

        return total / samples

    def evolve_density(self, agent, probs, alpha=0.3):
        """演化 ρ → Σ p_i U_i ρ U_i†"""
        rho_next = np.zeros_like(agent.rho, dtype=complex)
        for U, p in zip(self.moves, probs):  # (76×76) or 二阶结构（commutator algebra）作为动力
            rho_next += p * (U @ agent.rho @ U.conj().T)

        rho_next = (1 - alpha) * agent.rho + alpha * rho_next  # identity 保持结构,避免热寂
        agent.rho = rho_next / np.trace(rho_next)  # 数值稳定（归一化）

    def choose_probs(self, agent):
        """决策 Policy->后续 density / slow space 做策略评估"""
        scores = []
        for U in self.moves:
            rho2 = U @ agent.rho @ U.T
            purity_score = -agent.purity()  # 倾向保持纯度 purity 越纯越好（秩序）
            chaos_score = np.linalg.norm(rho2 - agent.rho, 'fro')  # 倾向保持非对易
            scores.append(purity_score + 0.3 * chaos_score)

        chaos = self.chaos_density(agent.rho)

        T = 0.2 + chaos  # chaos 控制随机性

        scores = np.array(scores)
        # p = np.zeros_like(scores)
        p = np.exp(-np.array(scores) / T)
        p /= p.sum() + 1e-12  # softmax(-np.array(scores) / T) 太平滑 → 导致平均化
        return p  # 会热寂

    @staticmethod
    def predator_prey(a, b):
        #  非对易性 = 捕食能力
        comm = np.linalg.norm(a.rho @ b.rho - b.rho @ a.rho)  # dominance
        if comm > 0.2:  # 非对易性强 → 耦合
            if a.purity() > b.purity():
                b.rho = 0.7 * b.rho + 0.3 * a.rho  # 高非交换 → 吞噬 a 吞 b
            else:
                a.rho = 0.7 * a.rho + 0.3 * b.rho

            a.rho /= np.trace(a.rho)
            b.rho /= np.trace(b.rho)

    def mutate(self, rho):
        """Mutation（结构保留）用 commutator chain 扰动 量子遗传（变异）"""
        # 随机选 2–4 个 U 做链
        U_chain = np.eye(rho.shape[0], dtype=complex)
        for _ in range(random.randint(2, 4)):
            U = random.choice(self.moves)
            U_chain = U @ U_chain  # @ U.conj().T
        rho2 = U_chain @ rho @ U_chain.conj().T
        return rho2 / (np.trace(rho2) + 1e-12)

    def destroy(self, rho):
        noise = np.random.randn(*rho.shape)
        rho2 = rho + 0.1 * (noise @ noise.T)
        tr = np.trace(rho2)
        return rho2 / (tr + 1e-8)

    # def repair(self, rho):
    #     for _ in range(5):
    #         p = choose_probs(...)
    #         rho = self.evolve_density(rho, p)
    #     return rho

    def death(self):
        """死亡：高熵/高年龄/高混沌/低纯度 → 淘汰"""
        self.agents = [
            a for a in self.agents
            if a.purity() > 0.1 and a.energy < 5.0 and a.age < 500
        ]

    def step(self):
        for agent in self.agents:
            p = self.choose_probs(agent)
            self.evolve_density(agent, p)
            agent.energy = agent.entropy()
            agent.age += 1

    def interact(self):
        """量子交互"""
        for i, a in enumerate(self.agents):
            for b in self.agents:
                if a is b: continue
                dist = np.linalg.norm(a.rho - b.rho, 'fro')
                if dist < 0.3:  # 相似 → 同步
                    U = random.choice(self.moves)
                    a.rho = U @ a.rho @ U.conj().T
                    b.rho = U @ b.rho @ U.conj().T

                d = np.linalg.norm(a.pos - b.pos)  # 局部才交互
                if d < 1.5:
                    self.predator_prey(a, b)

    def reproduce(self):
        """没有“遗传差异”，系统会塌缩成单一族群,鼓励多样性"""
        new_agents = []
        for agent in self.agents:
            if agent.purity() > 0.6 and random.random() < 0.1:
                child = QuantumAgent(CubieBase.generate_cubie(3), self.model)
                child.rho = self.mutate(agent.rho)
                child.pos = agent.pos + 0.5 * np.random.randn(2)
                new_agents.append(child)

        self.agents.extend(new_agents)

    def observe(self):
        ps = [a.purity() for a in self.agents]
        es = [a.entropy() for a in self.agents]
        cs = [self.chaos_density(a.rho, samples=10) for a in self.agents]
        species = [a.species() for a in self.agents]
        obs = {
            "purity_mean": np.mean(ps),  # chaos = mean(commutator)
            "entropy_mean": np.mean(es),
            "chaos_mean": np.mean(cs),
            "n_agents": len(self.agents),
            "species": len(set(species)),
        }

        self.history.append(obs)
        return obs

    def evolve(self, steps=100):
        for t in range(steps):
            self.step()
            self.interact()
            self.reproduce()
            self.death()

            obs = self.observe()
            if t % 10 == 0:
                print(
                    f"[{t}] purity={obs['purity_mean']:.3f} "
                    f"entropy={obs['entropy_mean']:.3f} "
                    f"chaos={obs['chaos_mean']:.3f} "
                    f"species={obs['species']} "
                    f"N={obs['n_agents']}"
                )

    def plot(self):
        if not self.history:
            return
        steps = np.arange(len(self.history))
        purity = [h['purity_mean'] for h in self.history]
        entropy = [h['entropy_mean'] for h in self.history]
        comm = [h['chaos_mean'] for h in self.history]
        n = [h['n_agents'] for h in self.history]

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))

        axs[0, 0].plot(steps, purity, 'b-', label='Purity')
        axs[0, 0].set_title('Purity Evolution')
        axs[0, 0].grid(True)

        axs[0, 1].plot(steps, entropy, 'r-', label='von Neumann Entropy')
        axs[0, 1].set_title('Quantum Entropy')
        axs[0, 1].grid(True)

        axs[1, 0].plot(steps, comm, 'g-', label='Commutator Chaos')
        axs[1, 0].set_title('Exchange Chaos')
        axs[1, 0].grid(True)

        axs[1, 1].plot(steps, n, 'm-', label='Population')
        axs[1, 1].set_title('Population Size')
        axs[1, 1].grid(True)

        plt.tight_layout()
        plt.show()

    def plot_world(self):
        plt.figure(figsize=(6, 6))

        for a in self.agents:
            s = a.species()
            color = hash(s) % 10

            plt.scatter(a.pos[0], a.pos[1],
                        c=f"C{color}",
                        s=50 * a.purity(),
                        alpha=0.7)

        plt.title(f"N={len(self.agents)}")
        plt.grid(True, alpha=0.3)
        plt.show()


class Environment:
    """
    宇宙接口，迁移世界,切换模型，添加目标，调整权重，世界规则变化，
    环境驱动的认知进化
    """

    def __init__(self, model: SlowDynamics, targets: list = None):
        self.model = model

        # --- 基础 ---
        solved = CubieState.solved()
        self.z_solved = model.project(solved.vector)
        # --- target ---
        self.targets = targets if targets is not None else [self.z_solved]
        self.target_id = 0
        self.targets_weight = [1.0] * len(self.targets)

        # --- move pairs ---
        self.move_pairs = list(model.rho_slow.values())

        # --- 调度 ---
        self.scheduler = None

        self.context = {}

        self.id_counter = 0  # ID计数器

    def add_target(self, z):
        self.targets.append(z)
        self.targets_weight.append(1.0)
        size = len(self.targets)
        self.context["n_targets"] = size
        return size - 1

    def get_target(self, idx: int = 0):
        if 0 <= idx < len(self.targets):
            return self.targets[idx]
        return self.z_solved

    def get_levels(self, z):
        """返回每个目标的距离"""
        return [self.model.shell_level(z, t) for t in self.targets]

    def get_preference(self, z, target_id: int = 0, eta=0.2):
        """ 生态位"""
        # dirs = [t - z for t in self.targets]
        # weights = softmax(-[norm(d) for d in dirs])
        target_dir = self.targets[target_id] - z  # 指向目标的向量
        target_dir /= np.linalg.norm(target_dir) + 1e-8
        noise = np.random.randn(len(z))  # 个体噪声
        noise /= np.linalg.norm(noise) + 1e-8
        pref = (1 - eta) * np.real(target_dir) + eta * noise
        pref /= np.linalg.norm(pref) + 1e-8
        return pref

    def update_context(self, **kwargs):
        """环境上下文更新，可能影响 agent 的感知/决策"""
        self.context.update(kwargs)

    def adjust_weights(self, k: float = 2.0):
        """k>=1,新元素权重是每个旧元素的 k 倍"""
        n = len(self.targets)
        if n == 0:
            return
        if n == 1:
            self.targets_weight = [1.0]
            return
        w_old = 1.0 / (n - 1 + k)
        w_new = k * w_old
        self.targets_weight = [w_old] * (n - 1) + [w_new]

    def set_targets(self):
        """不要重新赋值"""
        if len(self.targets) > 1:
            return
        self.targets[0] = self.z_solved
        self.targets += self.base_targets(type=0)
        self.targets_weight = [1.0] * len(self.targets)

    def base_targets(self, type=0) -> list:
        if type == 1:
            return [self.model.project(s.vector) for s in
                    (CubieExample.twisted(), CubieExample.inversed(), CubieExample.big_cycle(),
                     CubieExample.checkerboard(), CubieExample.superflip())]

        targets = []
        s0 = CubieState.solved()
        for k in [(0, 1, 1), (1, 1, 1), (2, 1, 1)]:
            g = self.model.rho_moves[k][0]
            s1 = g.act(s0)
            z = self.model.project(s1.vector)
            targets.append(z)
        return targets

    def generate_far_target(self, threshold=7.0):
        while True:
            s = CubieBase.generate_cubie(length=15)
            z = self.model.project(s.vector)
            if all(np.linalg.norm(z - z0) > threshold for z0 in self.targets):
                return z

    def generate_diff_target(self, threshold=0.4):
        """正交目标"""
        current_threshold = threshold
        attempt = 0
        while True:
            s = CubieBase.generate_cubie(length=20)
            z = self.model.project(s.vector)
            max_dot = max(abs(np.dot(z, z0)) for z0 in self.targets)
            if max_dot < current_threshold:
                return z
            if attempt % 10 == 0:
                current_threshold += 0.01
            attempt += 1

    @staticmethod
    def generate_target_from_agents(zs):
        """agent.set_target"""
        # zs = np.stack([a.z for a in self.agents])
        center = zs.mean(axis=0)
        idx = np.argmax(np.linalg.norm(zs - center, axis=1))  # 找一个“最远点”
        return zs[idx]


class HybridAgent:
    """
    双态系统,用量子态做观测 / 决策，用群作用做真实演化
    多 agent 生态：resource 竞争 + 4 种互动（imitate / predator / reproduce / emulate）。
    Phase 决策（Exploit / Revert / Explore / Natura）驱动行为。
    目标：从离散群 + 慢流形中涌现集体智能、世界模型、记忆与时间箭头。
    | 层级 | 实现             |
    | -- | ------------------ |
    | 微观 | 群作用                |
    | 表示 | slow manifold      |
    | 认知 | density matrix     |
    | 决策 | softmax + chaos    |
    | 资源 | resource field     |
    | 社会 | imitate + predator |
    | 演化 | reproduction       |
    """

    # __slots__ = ('state', 'z', 'rho',  'pos')

    def __init__(self, state: CubieState, env: Environment, mutate_length=0):
        self.env = env
        self.model = env.model
        self.move_pairs = env.move_pairs

        # 粒子态（真实）保持离散
        self.state = state
        self.memory = deque(maxlen=10)
        self.memory.append(state)
        self.gm = CubieMove.identity()

        # 波函数（慢空间）用于几何
        self.z = env.model.project(state.vector)
        self.prev_dz = None

        # 多场耦合系统
        z_hat = self.z / (np.linalg.norm(self.z) + 1e-8)  # 物理状态 z 的模长 = 物理信息（不能丢）,方向 = 认知信息（可以变）
        self.rho = np.outer(z_hat, z_hat.conj())  # 纯态密度矩阵,感知层,不参与真实演化（观测更新），马尔可夫式的当下存在，自在的存在
        if mutate_length > 0:  # 量子遗传（变异）
            self.rho, g = self.model.mutate(self.rho, length=mutate_length)

        self.rho_plan = self.rho.copy()  # future 快层 规划态/工作记忆 planning / imagination（不被观测污染），投向各种可能性，自为的存在
        self.rho_mem = self.rho.copy()  # past 慢层 记忆场,长期记忆锚点,海马体长期记忆库,自我连续性，防止完全虚无化导致崩溃

        self.chaos_val = self.chaos_density(mode='fast')  # z
        self.curvature_val = self.model.lie_curvature(self.z)  # z,路径稳定性
        self.move_entropy_val = 0.0

        self.plan_entropy_val = von_neumann_entropy(self.rho_plan)  # plan_entropy，初始 0
        self.purity_val = 1.0  # plan 规划态纯度
        # 相对指标
        self.fidelity_val = 1.0  # mem/plan 规划↔记忆锚点 相对相似度
        self.consistency_val = 1.0  # a/mem，初始 1 vs 记忆 的连续性
        self.divergence_val = 0.0  # a/plan，初始 0  规划态漂移 vs 信念相对差异

        self.target_id = 0
        self.level, dist = self.model.shell_level(self.z, env.get_target(self.target_id))
        self.energy = dist ** 2

        self.preference = env.get_preference(self.z, self.target_id)  # 生态位偏好向量
        self.alignment = 1.0
        self.energy_delta_cum = 0.0  # 总能量变化绝对值（经典运动量）
        self.entropy_delta_cum = 0.0  # 总熵变化绝对值（持续活跃度）

        self.confidence = 0.0
        # 生态特征
        self.age = 0
        self.resource = 1.0  # 资源（生存能力）
        self.stats = {'phase': -1, 'T': 0.0, 'T_phase': 0.0,
                      'move_id': -1, 'move_probs_mean': 0.0, 'move_probs_std': 0.0,
                      'diversity': 2.0 * np.pi}
        self.pos = np.random.randn(2) * 5  # 空间位置（局部交互）
        self.species_id = tuple(np.sign(self.z.real[:6]))  # 主特征向量签名,物种/基因/信仰/行为结构 cluster

        # self.move_probs = np.zeros(len(self.move_pairs))  # 当前动作概率分布
        self.phase_count = np.zeros(4, dtype=int)  # exploit/rollback/explore/mutate
        self.interact_count = np.zeros(6, dtype=int)
        self.get_energy()
        self.children: list['HybridAgent'] = []  # 子代对象列表
        env.id_counter += 1

    def quantum_evolve(self, k=3, alpha=1 / 3, beta=1 / 9, temperature=1 / 3):
        """保持相干性,量子大脑轻微混合 局部混合 = 有方向的思考
        把 agent 的决策拆成 4 种相位（phase)
        探索-利用-修复-突变 四态系统
        存在先于本质,虚无是自由的条件
        beta 观测强度 β=1 → 现在的（强坍缩）β<1, beta 越高 → 塌缩越彻底（越不可逆）
        """
        self.divergence_val = 0.5 * np.linalg.norm(self.rho_plan - self.rho, ord='nuc')  # 0.4~1.2 规划空间的混乱程度与纯态信念的偏离程度
        beta_eff = beta + 1.0 / 9 * (self.divergence_val - self.fidelity_val)
        self.rho_plan = (1 - beta_eff) * self.rho_plan + beta_eff * self.rho  # 适度拉回当前现实观测
        self.rho_plan /= np.trace(self.rho_plan)
        old_entropy = self.plan_entropy_val
        self.plan_entropy_val = von_neumann_entropy(self.rho_plan)  # 规划空间混乱度0~3 纯 rho_b: 0.05 /0.7 /1.5 /1.2
        self.entropy_delta_cum += abs(self.plan_entropy_val - old_entropy)
        self.purity_val = np.real(np.trace(self.rho_plan @ self.rho_plan))  # 0~1，越纯越好
        self.fidelity_val = fidelity(self.rho_mem, self.rho_plan)  # 0~1,规划空间与当前记忆锚点的相似度,比 divergence 更稳定,但不敏感于纯度变化

        phase, p, idx = self.choose_phase(k=k, temperature=temperature)

        z_new = self.z.copy()
        best_id = -1
        move_cost = 0
        if phase == 0:  # 锁位 资源充足且适合 → 执行规划,试图成为某种固定本质:A Exploit
            best_id = idx[-1]
            g, U_opt = self.move_pairs[best_id]
            z_new = U_opt @ self.z
            rho_next = U_opt @ self.rho @ U_opt.conj().T
            move_cost = max(0.04, 0.21 - 0.07 * self.confidence)  # 范围约 0.03 ~ 0.18
            # exploit 允许“认知跃迁”
        elif phase == 1:  # 资源充足但不适合 →回退rollback:AB Revert
            s_past = random.choice(list(self.memory))  # 回归点原修复，容许人犯错，仅限瞬息间
            g = CubieMove.build(self.state, s_past)
            z_past = self.model.project(s_past.vector)
            z_past /= np.linalg.norm(z_past) + 1e-8
            rho_a = np.outer(z_past, z_past.conj())
            U = self.model.project_move(g.rho())
            z_new = U @ self.z  # z_past
            rho_b = U @ self.rho_plan @ U.conj().T
            rho_next = 0.5 * rho_a + 0.5 * rho_b  # 这功能有点逆天，打破真实与虚妄，虚实结合，现实 + 记忆 量子干涉
            move_cost = max(0.05, 0.32 - 0.08 * self.confidence)
        elif phase == 2:  # 更相信自身信念，采样+ 精细打分，大胆投向可能性（真实性）:B Explore
            raw_scores = self.choose_scores(idx=idx)  # shape (18, 4)
            top_component = raw_scores[idx]  # shape (k, 4)
            top_component = (top_component - top_component.mean(axis=0)) / (top_component.std(axis=0) + 1e-6)
            p_k = p[idx]
            p_k /= p_k.sum()
            w = np.array([0.4, 0.3, 0.2, 0.1])  # chaos,-purity, -divergence, mem_align
            comp_score = np.tanh(np.dot(top_component, w))
            move_scores = 1.0 / 3 * p_k + 2.0 / 3 * comp_score  # + top_p
            # best_id = np.random.choice(idx, p=p_k)
            best_id = idx[np.argmax(move_scores)]
            g, U_opt = self.move_pairs[best_id]
            z_new = U_opt @ self.z
            zt = z_new.copy()
            zt /= np.linalg.norm(zt) + 1e-8
            rho_next = np.outer(zt, zt.conj())  # 纯态更新 U_opt @ self.rho_plan @ U_opt.conj().T
            move_cost = max(0.04, 0.22 - 0.1 * self.confidence)
        else:  # 道法自然,多步演化 np.mean(p[idx]) < 1.0 / len(self.move_pairs) + np.std(p[idx]):
            zt = self.model.evolve(self.z, T=k)  # 先让当前认知在慢流形上演化一段时间，得到一个“预期位置”
            zt /= np.linalg.norm(zt) + 1e-8
            rho_a = np.outer(zt, zt.conj())
            rho_next, g = self.model.mutate(rho_a, length=random.randint(2, k), p=p)  # 探索性变异+random_walk
            U = self.model.project_move(g.rho())
            z_new = U @ self.z
            # move_cost = -0.05 + 0.1 * random.random()

        self.prev_dz = z_new - self.z

        self.phase_count[phase] += 1
        self.stats['phase'] = phase
        self.stats['move_id'] = best_id
        self.stats['move_cost'] = move_cost
        # 从 rho 出发 explore（少量混合） + 保留经典身份
        # S_norm = self.plan_entropy_val / (np.log(self.rho_plan.shape[0]) + 1e-8)
        alpha_eff = alpha + 1.0 / 9 * self.plan_entropy_val  # 用规划熵控制激进程度,混乱时更激进规划
        # alpha_eff = np.clip(alpha_eff, 0.05, 0.5)
        self.rho_plan = (1 - alpha_eff) * self.rho_plan + alpha_eff * rho_next
        self.rho_plan /= np.trace(self.rho_plan)

        # sig_loss = rho_sigreg(rho=self.rho_plan, lambda_reg=0.09)
        # self.rho_plan = self.rho_plan - sig_loss * (self.rho_plan - 0.5 * np.eye(self.rho_plan.shape[0]))

        return g, move_cost

    def quantum_update(self, g: CubieMove, samples: int = 10):
        """从真实 state 更新“认知”,观测坍缩,同步认知"""
        # 身体演化（离散、确定性） O(20) 操作（perm + ori） 严格群结构（真实世界）
        self.state = g.act(self.state)
        self.gm = self.gm.compose(g)
        self.memory.append(self.state)

        self.z = self.model.project(self.state.vector)
        self.chaos_val = self.chaos_density(samples=samples, mode='fast')  # 真实动力学的非交换性表现 'show'/'commutator'
        self.curvature_val = self.model.lie_curvature(self.z, k=6)

        z_hat = self.z / (np.linalg.norm(self.z) + 1e-8)
        self.rho = np.outer(z_hat, z_hat.conj())  # rho_obs

    def quantum_dream(self, step=5, gamma=1 / 3):
        """
        Dream 模式：使用 rho_mem 进行离线想象/模拟
        不改变真实 state，只更新 rho_plan 和 rho_mem
        混乱时更需要重组记忆
        """
        if self.age % step == 0:  # 长期记忆缓慢巩固
            rho_mem_fresh = self.memory_field(limit=10, decay_tau=4.0, symmetry=True)  # 过去+未来的稳定结构
            zt = self.env.targets[self.target_id]
            zt /= np.linalg.norm(zt) + 1e-8
            target_bias = np.outer(zt, zt.conj())  # 生成未来策略的源头
            beta_eff = 1.0 / 9 * (1 - self.alignment)
            rho_mem_fresh = (1 - beta_eff) * rho_mem_fresh + beta_eff * target_bias
            self.rho_mem = (1 - gamma) * self.rho_mem + gamma * rho_mem_fresh
        else:  # 轻微 EMA 更新（吸收当前 rho_a）
            gamma_eff = gamma / step + 1.0 / 9 * von_neumann_entropy(self.rho_mem)  # 混乱时更依赖观测
            self.rho_mem = (1 - gamma_eff) * self.rho_mem + gamma_eff * self.rho  # 当前 belief 用现实修正记忆

        self.rho_mem /= np.trace(self.rho_mem)
        self.consistency_val = np.real(np.trace(self.rho @ self.rho_mem.conj().T))  # 惯性,一致性,包含方向信息 0.22-0.7

        if self.age > 1 and self.plan_entropy_val < 0.3 and self.purity_val > 0.90 and self.divergence_val < 0.2:
            self.interact_count[4] += 1  # Boltzmann brain 状态持续,低熵涨落如何被第二定律摧毁 bb_lifetime
        if self.plan_entropy_val > 2.0 and self.fidelity_val < 0.1 and self.consistency_val < 0.1:  # 认知崩溃检测，强锚定回当前信念,混乱时回忆过去的认知
            self.rho_plan = 5.0 / 9 * self.rho + 1.0 / 3 * self.rho_mem + 1.0 / 9 * self.rho_plan
            self.rho_plan /= np.trace(self.rho_plan)
            print(f"[Crisis Anchor] entropy={self.plan_entropy_val:.3f} fidelity={self.fidelity_val:.3f} "
                  f"div={self.divergence_val:.3f} purity={self.purity_val:.3f}")  # 虚假记忆如何快速被现实修正

    def memory_field(self, limit=5, decay_tau=3.0, symmetry=False):
        """
        支持时间对称的长期记忆场, 从历史得到认知+ 时间衰减权重 + 从当前z反向演化出的虚拟记忆
        海马体式，提供认知锚点
        """
        if not self.memory:
            return self.rho.copy()
        # 取过去几个状态
        past_states = list(self.memory)[-limit:]
        rho_mem = np.zeros_like(self.rho, dtype=complex)
        for i, s in enumerate(reversed(past_states)):
            z_past = self.model.project(s.vector)
            z_past /= np.linalg.norm(z_past) + 1e-8
            weight = np.exp(-i / decay_tau) if decay_tau > 0 else 1.0
            rho_mem += weight * np.outer(z_past, z_past.conj())

        if symmetry:  # 加入预测的“未来”记忆，使其近似时间平移不变:观察 bb_lifetime 是否显著增加
            z_future = self.model.evolve(self.z, T=min(len(past_states), limit // 2))  # 用谱演化预测未来 T 步（对称于过去）
            z_future /= np.linalg.norm(z_future) + 1e-8
            rho_future = np.outer(z_future, z_future.conj())
            rho_mem = 0.5 * rho_mem + 0.5 * rho_future  # 对称融合（过去和未来等权重）

        rho_mem /= np.trace(rho_mem) + 1e-12
        return rho_mem

    def resource_field(self, pos):
        """简单径向 + 多峰资源场（可扩展成真实环境地图）"""
        if pos is None:
            pos = self.pos
        r = np.linalg.norm(pos)
        # 主峰在原点 + 4个随机小峰（模拟资源斑块）
        field = 0.6 * np.exp(-r ** 2 / 25)
        for i in range(4):
            peak = np.array([np.sin(i * 1.7) * 12, np.cos(i * 1.7) * 12])  # centers
            field += 0.15 * np.exp(-np.linalg.norm(pos - peak) ** 2 / 12)
        return field

    def get_energy(self, step=10, momentum=0.2):
        """经典能量（slow distance²）"""
        dists = self.env.get_levels(self.z)
        best_target_id = np.argmin([d for _, d in dists])  # np.argsort(dists)[:k]
        if self.age % step == 0 or self.level == -1 or self.target_id == -1:  # target 不要每步贪心切换
            self.target_id = best_target_id
            eta_eff = 0.2 * (2 - self.consistency_val + self.chaos_val)
            new_pref = self.env.get_preference(self.z, self.target_id, eta=eta_eff)
            self.preference = (1.0 - momentum) * self.preference + momentum * new_pref
            self.preference /= np.linalg.norm(self.preference) + 1e-8

        target_dir = self.env.targets[self.target_id] - self.z
        target_dir /= np.linalg.norm(target_dir) + 1e-8
        self.alignment = np.dot(target_dir.real, self.preference)  # cos θ [-1, 1] 0.3,0.7
        self.level, dist = dists[self.target_id]
        if self.level <= 3.0:  # 靠近目标额外奖励
            reward = 1.0 * (2 * np.pi - dist) / (2 * np.pi)
            if self.level == 0:
                reward += 1.0  # 额外奖励 self.state == CubieState.solved()
                self.interact_count[5] += 1
                print(
                    f"Reached target {self.target_id} at age {self.age} with resource {self.resource:.2f},stats: {self.stats}")
                self.target_id = np.argmax([d for _, d in dists])
            self.resource += reward

        old_energy = self.energy
        self.energy = dist ** 2
        self.energy_delta_cum += abs(self.energy - old_energy)
        self.resource += 0.1 * (1.0 / (1.0 + self.energy))
        return self.energy

    def chaos_density(self, samples=10, mode='fast'):
        """对易性观测量:表示层非对易性/真实动力学扰动"""
        if mode == 'fast':  # slow
            sigs = self.model.chaos_signature(self.z, samples)
            return sigs.mean()

        total = 0.0
        for _ in range(samples):
            (g, Ug), (h, Uh) = random.sample(self.move_pairs, 2)
            if mode == 'quantum':  # rho_diff ≈ C_gh @ rho @ C_gh.conj().T
                rho_gh = Ug @ (Uh @ self.rho @ Uh.conj().T) @ Ug.conj().T
                rho_hg = Uh @ (Ug @ self.rho @ Ug.conj().T) @ Uh.conj().T
                total += np.linalg.norm(rho_gh - rho_hg, 'fro')  # 0.07-0.4
            elif mode == 'show':  # 非交换性在慢空间的表现，完全在慢流形上,非对易性被压平了
                z_gh = Ug @ (Uh @ self.z)  # g 后 h
                z_hg = Uh @ (Ug @ self.z)  # h 后 g
                total += np.linalg.norm(z_gh - z_hg)  # 0.1-0.35 chaos_signature np.linalg.norm(C_gh @ z)
            else:  # Rubik group 本来就是强非交换群,chaos 太强 → 系统发散 or 震荡
                s_gh = (g @ h).act(self.state)  # g.act(h.act(self.state))
                s_hg = (h @ g).act(self.state)
                z_gh = self.model.project(s_gh.vector)
                z_hg = self.model.project(s_hg.vector)
                total += np.linalg.norm(z_gh - z_hg)  # 0.5-3

        if mode == 'quantum' or mode == 'show':
            return total / samples

        z_norm = np.linalg.norm(self.z) + 1e-8
        return (total / samples) / z_norm

    def choose_scores(self, idx=None):
        """
        只对这 k 个动作做精细的 4 维 component score 计算，节省计算量
        倾向：高纯度（秩序）+ 适度混沌（非交换性）
        对指定的 idx（top-k）计算 4 维 component score，其余保持 
        move_scores → p → idx = top-k
        """
        if idx is None:
            idx = range(len(self.move_pairs))

        # rho_next = np.zeros_like(self.rho_plan, dtype=complex)
        scores = np.zeros((len(self.move_pairs), 4), dtype=np.float64)
        for i in idx:
            _, U = self.move_pairs[i]
            sim_rho_real = U @ self.rho @ U.conj().T
            chaos = np.linalg.norm(sim_rho_real - self.rho, 'fro')  # 非对易倾向 0.2-1.3
            purity_gain = np.real(np.trace(sim_rho_real @ sim_rho_real)) - self.purity_val  # 自然系统里不是：变得更纯
            divergence = 0.5 * np.linalg.norm(sim_rho_real - self.rho_plan, ord='nuc') - self.divergence_val  # 与规划态的匹配度
            mem_align = np.linalg.norm(sim_rho_real - self.rho_mem, 'fro')  # 保持轨道连续性 -self.consistency_val
            # sim_rho_plan = U @ self.rho_plan @ U.conj().T
            # plan_consistency = np.real(np.trace(sim_rho_plan @ self.rho_plan))

            scores[i, 0] = chaos  # 探索性
            scores[i, 1] = -purity_gain  # 稳定性,适度混合,纯度太高:探索性丢失
            scores[i, 2] = -divergence  # 规划匹配度 np.real(np.trace(sim_rho @ self.rho_plan))
            scores[i, 3] = -mem_align  # 记忆连续性
            # rho_next += p[i] * sim_rho

        return scores

    def choose_phase(self, k=3, temperature=1 / 9):
        """phase 选择逻辑：整合所有变量，输出 phase,用 4 个 phase 的分数决定行为模式
        焦虑是自由的证明:phase 切换"""
        target = self.env.get_target(self.target_id)
        energy = self.model.move_energy(self.z, target, self.prev_dz)
        fitness = - energy  # 越高越好
        f = normalize_z(fitness)
        p0 = softmax(f)  # softmax 太平滑 → 导致平均,无T
        self.move_entropy_val = -np.sum(p0 * np.log(p0 + 1e-8))
        entropy = self.move_entropy_val / np.log(len(p0))
        scale = np.percentile(np.abs(fitness), 80) + 1e-6
        # scores = np.clip(fitness,-15, 15)  # 限制范围，避免溢出
        T = temperature * (1 + 3.0 * self.curvature_val) + 2.0 * self.chaos_val  # 动作层,越高越随机
        # p = np.exp(-scores / T)  # 量子决策 math.exp(-dE / temperature)
        f = fitness / (T * scale + 1e-8)
        f = f - np.max(f)
        p = np.exp(f)
        p /= p.sum() + 1e-12

        idx = np.argsort(p)[-k:]
        best_id = idx[-1]
        p_max = p[best_id] / p[idx].sum()  # 在候选中的相对优势

        sharpness = np.sum(p ** 2)  # Gini-like ,1/n,1
        suitability = p_max + 2.0 / 3 * sharpness + 1.0 / 3 * (1.0 - entropy)  # 执行阈值
        instability = self.chaos_val * (1 + 2.0 * self.curvature_val) + 1.0 / 3 * entropy
        # print(f"Suitability: {suitability:.3f} /{instability:.3f} (p={p[best_id]:.3f}, purity={self.purity_val:.3f}, plan_entropy={self.plan_entropy_val:.3f},"
        #       f"entropy={entropy:.3f},sharpness={sharpness:.3f},p_max={p_max:.3f}")

        suitability = np.clip(suitability, 0.0, 1.0)
        instability = np.clip(instability, 0.0, 1.0)
        self.confidence = (1.0 - instability + suitability) / 2.0

        phase_scores = np.array([
            suitability + 1.0 / 3 * (1.0 - self.divergence_val + self.fidelity_val + self.purity_val),
            # exploit: 高信心 + 高规划可靠
            (1.0 - suitability) * self.consistency_val * self.resource / np.sqrt(self.age + 1),
            # revert:  低信心 + 规划失效,认知崩了才回退
            instability + self.divergence_val + 1.0 / 9 * self.plan_entropy_val,  # (1.0 - self.consistency_val)
            # explore: 高混乱 + 高曲率
            self.consistency_val * (1.0 - abs(self.purity_val - 0.5) - abs(self.fidelity_val - 0.5)) +
            self.alignment * (1 + 2.0 * self.curvature_val)
            # natura:  中性、保守，结构沉淀阶段，鞅偏差
        ])  # phase_vector

        # conflict_exploit = np.clip((self.plan_entropy_val - 0.8) / 0.8, 0.0, 1.0)
        # conflict_explore = np.clip((0.5 - self.fidelity_val) / 0.5, 0.0, 1.0)

        # phase_scores[0] *= (1.0 - 0.6 * conflict_exploit)
        # phase_scores[0] -= 0.2 * conflict_explore
        # phase_scores[2] *= (1.0 + 0.5 * conflict_explore)
        # phase_scores[2] += 0.3 * conflict_exploit
        ps = normalize_z(phase_scores)
        ps = np.tanh(ps)
        T_phase = temperature * (1 + 1.0 / 3 * self.chaos_val)  # 策略层
        x_scores = ps / (T_phase + 1e-6)
        phase_p = softmax(x_scores)  # 限制范围，避免溢出, 提高数值稳定性

        try:
            phase = np.random.choice(4, p=phase_p)  # 会抖,or last_phase
        except ValueError:
            phase = np.argmax(phase_p) or self.stats['phase']  # 如果概率分布有问题，选择概率最高的阶段
            # if np.any(np.isnan(phase_p)) or np.sum(phase_p) == 0:
            print(
                f"Phase scores: {phase_scores},scores:{fitness} Phase probabilities: {phase_p}, T_phase: {T_phase:.3f}")

            print("energy range:", energy.min(), energy.max())

        self.stats['T'] = T
        self.stats['T_phase'] = T_phase
        self.stats['move_probs_mean'] = p.mean()
        self.stats['move_probs_std'] = p.std()  # 0.05
        self.stats['suitability'] = suitability
        self.stats['instability'] = instability
        # self.stats['move_cv']  = np.real(np.std(energy) / (np.mean(energy) + 1e-8))  #  概率分布集中度

        return int(phase), p, idx

    def step(self, T=1 / 9, L: int = 1, S: int = 10, neighbors=None):
        """核心双态步进：量子决策 → 经典执行 → 大脑更新 量子大脑混合"""
        for _ in range(L):
            # 量子大脑轻微演化 未来模拟,融合同步记忆 k = int(3 + 6 * self.entropy())
            g, move_cost = self.quantum_evolve(k=3, alpha=1 / 3, beta=1 / 9, temperature=T)
            if move_cost > 0:
                self.resource -= move_cost
                # print(f"Agent executes move {self.move_id} with cost {move_cost:.3f} and suitability {p[best_idx]:.3f}")
            # 观测更新
            self.quantum_update(g)

        # 弱坍缩,现实校正
        self.quantum_dream(step=5, gamma=1 / 3)

        self.get_energy(step=S)
        # 资源动态
        self.gather_resource(neighbors)
        self.age += 1

        self.pos += 0.25 * np.random.randn(2)  # 随机扩散
        grad_x = self.resource_field(self.pos + np.array([0.1, 0])) - self.resource_field(self.pos)
        grad_y = self.resource_field(self.pos + np.array([0, 0.1])) - self.resource_field(self.pos)
        self.pos += 0.8 * np.array([grad_x, grad_y])

    def emulate(self, g: CubieMove):
        self.quantum_update(g)  # 同步认知
        self.get_energy()
        self.interact_count[3] += 1

    def imitate(self, other_agent: 'HybridAgent', data: dict = None):
        """
        社会学习：模仿经典状态，量子自动同步,弱者向强者学习
        imitation = phase 同步
        """
        if not other_agent.memory:
            return
        if self.purity_val > other_agent.purity_val:
            return
        relative_strength = self.purity_val * self.fidelity_val - other_agent.purity_val * other_agent.fidelity_val
        if abs(relative_strength) < 0.1:  # 实力相近不学（避免过度模仿导致系统崩溃）
            return

        directed_d = data.get("directed_d", np.dot(other_agent.z - self.z, self.preference).real)  # 沿自身偏好方向投影
        if directed_d < 0.1:  # 方向性判断
            return  # 太近不模仿（防止塌缩,抹平结构）collapse,只有当对方在自己偏好方向上更接近目标时才模仿

        cultural_d = np.linalg.norm(self.rho_plan - other_agent.rho_plan, 'fro')  # 规划认知差异
        if cultural_d > 1.0:  # 规划认知差异过大不模仿（防止认知冲突）
            return
        score = 0.5 * sigmoid(directed_d) + 0.4 * (1 - cultural_d / 2.0) + 0.1 * self.resource
        trigger_prob = np.clip(score, 0.05, 1.0)
        if random.random() > trigger_prob:
            return

        # comm = np.linalg.norm(self.rho_mem @ other_agent.rho_mem - other_agent.rho_mem@ self.rho_mem)
        # if comm < 0.2:
        #     return

        # 模仿对方的规划认知或者参考对方的记忆场
        if self.divergence_val > 0.8 and self.resource > 3:  # 当自己的规划和现实差异过大时，更倾向于参考对方的记忆场（更稳定）
            teacher_rho = other_agent.rho_mem.copy()
            transfer = min(0.5, 0.1 * self.resource)  # 法不轻传
            self.resource -= transfer
            other_agent.resource += transfer
        else:
            teacher_rho = other_agent.rho_plan.copy()

        # 融合对方的规划认知，只学习对自己有用的部分
        mix_ratio = 1 / 9 * min(1.0, directed_d * self.resource * self.plan_entropy_val)
        delta = teacher_rho - self.rho_plan
        align = np.real(np.trace(delta @ np.outer(self.preference, self.preference)))

        self.rho_plan += mix_ratio * align * delta  # 记忆融合，文化吸收
        self.rho_plan /= np.trace(self.rho_plan)  # 暂时不影响 rho_a

        self.interact_count[0] += 1  # 模仿计数

    def predator(self, other_agent: 'HybridAgent', data: dict = None):
        """
        捕食：改变 state 和 资源+ 领地推进
        predator = phase 扰动
        """
        relative_strength = self.purity_val * self.resource - other_agent.purity_val * other_agent.resource
        if abs(relative_strength) < 0.3:  # 实力相近不打（避免过度竞争导致系统崩溃）
            return

        # 强者判定
        if relative_strength > 0:
            predator, prey = self, other_agent
        else:
            predator, prey = other_agent, self
            return  # 单向,只让 stronger 调用 weaker

        pos_d = data.get("pos_d", np.linalg.norm(self.pos - other_agent.pos))
        local_avg = 0.5 * (self.resource + other_agent.resource)
        relative_strength /= (local_avg + 1e-6)
        transfer = max(0, 0.1 * prey.resource * sigmoid(relative_strength))
        predator.resource += 0.95 * transfer
        prey.resource -= transfer

        prob = np.exp(-pos_d ** 2 / 5.0) * self.plan_entropy_val
        # 量子捕食（位置近才触发）
        if random.random() < prob:  # 边界扰动,捕食成功后，弱者可能发生认知变异（逃避/适应）
            g = self.model.random_walk(length=2)
            prey.emulate(g)

        direction = predator.pos - prey.pos
        prey.pos -= 0.3 * direction / (pos_d + 1e-6)

        self.interact_count[1] += 1  # 捕食计数

    def interact_kernel(self, agents, values: list, D=0.03, S=0.08, T=0.2, R=0.1):
        """
        连续场近似：kernel-based PDE update
        统一加权更新，状态转移
        diffusion（模仿） + selection（竞争） + transport（捕食） + entropy（抗塌缩）
        """

        rho_i = self.rho_plan
        x_i = self.z

        # local_diversity = np.mean([np.linalg.norm(self.z - n.z) for n in neighbors])

        diffusion_term = np.zeros_like(rho_i, dtype=complex)
        transport_term = np.zeros_like(x_i)

        entropy = self.plan_entropy_val
        curvature_i = self.curvature_val
        r_i = self.resource
        f_i = self.purity_val * max(1e-6, r_i)
        selection_term = 0.0
        fitness_accum = 0.0
        resource_flow = 0.0
        weight_sum = 1e-8

        for b in agents:
            if b is self:
                continue

            rho_j = b.rho_plan
            x_j = b.z
            # --- 1️⃣ kernel ---
            dist = np.linalg.norm(x_i - x_j)
            if dist > 2 * np.pi:  # 距离过远直接跳过
                continue
            same_species = (self.species_id == b.species_id)
            same_target = (self.target_id == b.target_id)
            species_gate = 0.2 + 0.8 * (1.0 if same_species else 0.0)
            target_gate = 0.5 + 0.5 * (1.0 if same_target else 0.0)

            dir_align = np.dot(x_j - x_i, self.preference).real  # imitate的核心
            # --- kernel ---
            K = np.exp(-dist ** 2 / 2.0)
            K *= species_gate
            K *= target_gate

            learn_gate = sigmoid(dir_align) * (1 - entropy)  # imitate
            cultural_d = np.linalg.norm(rho_i - rho_j, 'fro')
            cultural_gate = np.exp(-cultural_d)

            # --- predator gating（predator_prob）---
            f_j = b.purity_val * max(1e-6, b.resource)
            strength_diff = (f_j - f_i) / (abs(f_i) + abs(f_j) + 1e-6)
            flow_gate = sigmoid(strength_diff)
            pred_gate = flow_gate * np.exp(-dist)
            pred_gate *= (1 + 2.0 * curvature_i)

            # --- 2️⃣ diffusion ---
            diffusion_term += K * learn_gate * cultural_gate * (rho_j - rho_i)  # 模仿

            # === 2️⃣ selection（replicator）===
            selection_term += K * (f_j - f_i)

            # --- resource flux ---
            resource_flow += K * flow_gate * (b.resource - r_i)

            # === 3️⃣ transport（捕食 → 空间推进）===
            direction = (x_j - x_i) / (dist + 1e-6)
            transport_term += K * pred_gate * direction

            # --- 3️⃣ fitness（selection准备） ---
            f_j = b.purity_val * max(0.0, b.resource)
            fitness_accum += K * f_j

            weight_sum += K

        # === diffusion ===
        self.rho_plan += D * diffusion_term / weight_sum  # 0.02~0.05 模仿融合
        # === selection（replicator）===
        self.rho_plan += S * (selection_term / weight_sum) * rho_i  # 0.05~0.1

        # self.z += T * transport_term / weight_sum

        self.resource += R * resource_flow / weight_sum
        self.resource = max(1e-6, self.resource)
        # --- entropy（抗塌缩）---
        H = -np.real(np.trace(rho_i @ np.log(rho_i + 1e-8)))
        entropy_force = 0.02 * (1.0 - H)
        # === anti-collapse normalize ===
        self.rho_plan /= np.trace(self.rho_plan) + 1e-12
        # === mutation（底噪）===
        instability = (1 - entropy) + np.abs(selection_term / weight_sum)

        mutation_prob = sigmoid(instability)
        if random.random() < 0.02 * mutation_prob:
            g = self.model.random_walk(length=1)
            self.emulate(g)
            # teacher = random.choice(list(other_agent.memory))
            # g = CubieMove.build(self.state, teacher)  # 带着求经问道之心
            # U = self.model.project_move(g.rho())
            # teacher_rho = U @ self.rho_plan @ U.conj().T

    def gather_resource(self, neighbors):
        """获取资源：生态位匹配 + 局部空间场"""
        # 1. 慢空间生态位匹配
        gain = max(0.0, float(self.alignment)) * 0.15
        if neighbors:  # 局部竞争
            competition = sum(n.resource for n in neighbors) / len(neighbors)
            gain *= np.exp(-0.3 * competition)

        season = 0.3 * np.sin(2 * np.pi * self.age / 50)  # 季节波动
        gain *= (1.0 + season)
        self.resource += gain
        # 局部资源场（空间结构）
        self.resource += self.resource_field(self.pos)
        # 资源代谢衰减
        self.resource *= 0.97
        # self.resource += 0.05  # baseline inflow

    def reproduce(self, max_length=4):
        """繁殖：只有高纯度 + 低能量时才产生后代"""
        # 经典小变异
        length = random.randint(2, max_length)
        child_state = self.state.clone()
        if random.random() < 0.3:
            g = self.model.random_walk(length=length)
            child_state = g.act(child_state)
        else:  # 直接用交换子矩阵,群结构的“内禀曲率”. 3.7-3.9
            for _ in range(length):
                (g, _), (h, _) = random.sample(self.move_pairs, 2)
                m = g @ h @ g.inverse() @ h.inverse()  # ghg⁻¹h⁻¹
                child_state = m.act(child_state)

        child = HybridAgent(child_state, self.env, mutate_length=length)
        child.species_id = self.species_id  # 遗传物种标签
        child.pos = self.pos + 0.4 * np.random.randn(2)

        child.resource = 0.5 * self.resource
        self.resource *= 0.5
        # 部分记忆继承
        child.memory = deque(list(self.memory)[:6], maxlen=10)
        child.memory.append(child_state)
        self.children.append(child)
        self.interact_count[2] += 1  # 繁殖计数
        return child

    def vector(self):
        "behavior:行为向量,策略签名"
        energy_rate = self.energy_delta_cum / max(1, self.age)
        entropy_rate = self.entropy_delta_cum / max(1, self.age)
        resource_rate = self.resource / max(1, self.age)
        mem_drift = 1.0 - self.consistency_val  # 轨道偏移量
        return np.array([
            # --- 状态 ---
            self.plan_entropy_val,
            self.purity_val,
            self.fidelity_val,
            self.divergence_val,

            self.move_entropy_val,
            self.curvature_val,
            self.chaos_val,
            self.alignment,
            # --- 行为 ---
            energy_rate,  # 运动强度/ 动力学速度
            entropy_rate,  # 认知活跃度/ 探索程度
            mem_drift,  # 轨道稳定性/行为一致性
            resource_rate,
            self.confidence,
            # self.stats['move_probs_mean'],  # 行为模式
            # self.stats['move_probs_std'],
        ])


class HybridSimulation:
    """
    Hybrid 双态人工生命系统（平衡秩序-混沌）
    微观	群作用（Cubie）	真实动力
    中观	slow manifold	结构压缩
    宏观	density / entropy	统计行为
    agent:
        rho → rho_plan
        rho_mem → 调参数
        ↓
    interact_kernel → 局部传播

    simulation:
        agents → rho_collective（全局抽象）

    rho_collective:
        → dream（生成新结构）
        → 弱反馈 → rho_mem

    最终：
        memory → policy → action
    """

    def __init__(self, env: Environment, n_agents=25):
        self.env = env
        self.env.set_targets()

        self.agents = [
            HybridAgent(CubieBase.generate_cubie(length=random.randint(3, 12)), env)
            for _ in range(n_agents)
        ]
        self.rho_collective = None  # 全局共享记忆场,群体共同的“潜意识”
        self.history = []
        self.population_history = []
        self.stats = {'n_agents': len(self.agents), 'n_targets': len(env.targets), 'n_species': 0,
                      'birth_cum': 0, 'death_cum': 0, "resource_mean": 1.0, 'step_time': 0.0, 'P': 0, 'T': 1.0}
        # self.env.context = self.stats  # 环境上下文共享统计数据
        self.move_counter = np.zeros(len(self.env.move_pairs), dtype=int)
        self.record()

    def record(self):
        if not self.agents:
            return
        zs = np.stack([a.z for a in self.agents])
        self.population_history.append(zs)
        self.env.update_context(**self.stats)

    def step(self, T=1 / 9, L=1, S: int = 10, K=300, k_neighbors=10):
        # 1. 所有 agent 演化
        import time
        t0 = time.perf_counter()
        for i, a in enumerate(self.agents):
            neighbors = [b for b in self.agents if a is not b]
            neighbors = random.sample(neighbors, min(k_neighbors, len(neighbors))) if neighbors else None
            a.step(T, L=L, S=S, neighbors=neighbors)

        self.assign_species(eps=0.5, min_samples=3)  # 每步重新分配物种 ID，基于当前的 z 向量聚类

        self.interaction(k_neighbors=k_neighbors)  # 2. 邻居交互（模仿 + 捕食）

        # 3. 繁殖
        self.reproduce(K)

        # 4. 死亡
        self.death(K)

        t1 = time.perf_counter()
        self.stats['step_time'] = t1 - t0

        # 5. 记录
        self.record()

    def behavior_dbscan(self, eps=0.3, min_samples=4, sig_samples=6):
        """DBSCAN 的前提是：存在 density cluster（密度簇）"""
        n = len(self.agents)
        labels = np.full(n, -1)
        visited = np.zeros(n, dtype=bool)
        cluster_id = 0

        # 预计算 signature
        sigs = [self.env.model.chaos_signature(a.z, sig_samples) for a in self.agents]

        def region_query(i):
            return [j for j in range(n) if np.linalg.norm(sigs[i] - sigs[j]) < eps]

        def expand(i, neighbors):
            nonlocal cluster_id
            labels[i] = cluster_id
            k = 0
            while k < len(neighbors):
                j = neighbors[k]
                if not visited[j]:
                    visited[j] = True
                    nj = region_query(j)
                    if len(nj) >= min_samples:
                        neighbors.extend(nj)
                if labels[j] == -1:
                    labels[j] = cluster_id
                k += 1

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            neigh = region_query(i)
            if len(neigh) < min_samples:
                labels[i] = -1
            else:
                expand(i, neigh)
                cluster_id += 1

        return labels

    def assign_species(self, eps=0.5, min_samples=4):
        """
        cluster 不是连续分布,而是离散轨道 ,
        慢流形上的几何已经塌成一层壳，导致 DBSCAN 无法形成 species,direction 有信息:cosine distance
        """

        # from sklearn.cluster import DBSCAN
        # Z = np.stack([a.z.real for a in self.agents])
        # Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-8)
        # dist_matrix = 1 - np.dot(Z, Z.T)
        # # 先按壳层分组
        # levels = np.array([a.level for a in self.agents]) #, a.preference
        # species = dbscan(Z, eps=0.8, min_samples=min_samples)

        # species = self.behavior_dbscan(eps=eps, min_samples=min_samples)
        def phase_signature(agent):
            """基于 phase behavior 分布的 signature,反映行为模式的相似性"""
            total = agent.phase_count.sum()
            return np.array(agent.phase_count) / (total + 1e-8) if total > 0 else np.zeros(4)

        # X = [a.rho_b.flatten().real for a in self.agents]
        # X = np.stack([a.preference for a in agents])
        X = np.stack([np.concatenate([a.vector(), phase_signature(a)]) for a in self.agents])
        # X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
        # X[:, :7] = (X[:, :7] - X[:, :7].mean(0)) / (X[:, :7].std(0) + 1e-8)
        species = dbscan(X, eps=eps, min_samples=min_samples)

        for a, s in zip(self.agents, species):
            a.species_id = s

        self.stats['n_species'] = len(set(s for s in species if s >= 0))
        return species

    def update_collective(self, agents):
        """每一步更新集体大脑"""
        if len(agents) < 2:
            return
        rhos = [a.rho_mem for a in agents]
        weights = []
        for a in agents:
            w = (
                    0.5 * a.fidelity_val +
                    0.3 * (1 - a.plan_entropy_val) +
                    0.2 * a.purity_val
            )
            weights.append(w)

        weights = np.array(weights)
        weights /= weights.sum() + 1e-8

        # 加权平均,收集当前所有 agent 的 rho_mem 贡献
        contrib = sum(w * r for w, r in zip(weights, rhos))
        contrib /= np.trace(contrib) + 1e-12

        # --- 2️⃣ 初始化 ---
        if self.rho_collective is None:
            self.rho_collective = contrib.copy()
            return

        # --- 3️⃣ 动态融合率（关键）---
        avg_entropy = np.mean([a.plan_entropy_val for a in agents])
        diversity = np.mean([
            np.linalg.norm(a.z - b.z)
            for a in agents for b in agents if a is not b
        ])

        alpha = 0.08 + 0.12 * avg_entropy + 0.05 * np.tanh(diversity)

        # --- 4️⃣ EMA 更新,弱融合进集体记忆 ---
        self.rho_collective = (1 - alpha) * self.rho_collective + alpha * contrib

        # --- 5️⃣ anti-collapse（关键！）---
        dim = self.rho_collective.shape[0]
        I = np.eye(dim) / dim

        mix = 0.02 + 0.05 * (1 - avg_entropy)
        self.rho_collective = (1 - mix) * self.rho_collective + mix * I

        # --- 6️⃣ normalize ---
        self.rho_collective /= np.trace(self.rho_collective) + 1e-12

        # --- 7️⃣ 记录 entropy ---
        self.stats['collective_entropy'] = von_neumann_entropy(self.rho_collective)

    def collective_dream(self, steps=3, T=0.9):
        """ 触发集体 dream,越“不稳定的人”越受群体影响"""
        if self.rho_collective is None:
            return None

        rho = self.rho_collective.copy()

        for _ in range(steps):
            # ---  policy:在集体记忆空间进行轻微演化 ---
            f = self.model.move_scores_from_rho(rho)
            p = softmax(f / T)

            idx = np.random.choice(len(p), p=p)
            _, U = self.env.move_pairs[idx]

            rho = U @ rho @ U.conj().T
            rho /= np.trace(rho) + 1e-12

        # 梦境回馈给所有 agent（弱影响）
        for a in self.agents:  # 需要把 agents 传进来或全局持有
            # align = np.real(np.trace(a.rho_plan @ rho))
            strength = 0.05 * (1 - a.fidelity_val)
            a.rho_mem = (1 - strength) * a.rho_mem + strength * rho
            a.rho_mem /= np.trace(a.rho_mem) + 1e-12

        return rho

    def interaction(self, k_neighbors=8, slow_radius=5.0, pos_radius=4.0):
        """
        Top-K 邻居交互,所有 agent 状态更新后再进行邻居交互
        k: 每个 agent 最多交互的邻居数量
        slow_radius: 慢空间语义距离阈值
        pos_radius: 物理位置距离阈值
        """
        if len(self.agents) < 2:
            return

        n_species = self.stats['n_species']
        for a in self.agents:
            candidates = []
            for b in self.agents:
                if a is b:
                    continue
                slow_d = np.linalg.norm(a.z - b.z)
                pos_d = np.linalg.norm(a.pos - b.pos)
                # 只考虑在慢空间或物理空间上接近的
                if slow_d < slow_radius or pos_d < pos_radius:
                    score = -slow_d * 0.6 - pos_d * 0.4  # 综合分数：慢空间距离更重要
                    candidates.append((score, b, slow_d, pos_d))

            # 选 Top-K
            candidates.sort(key=lambda x: x[0], reverse=True)  # 分数越高越优先
            selected = candidates[:k_neighbors]
            neighbors = [b for _, b, *_ in selected]

            if not neighbors:
                continue

            values = [{"slow_d": item[2], "pos_d": item[3]} for item in selected]
            diversity = np.mean([item[2] for item in selected]) if selected else 2.0 * np.pi
            a.stats['diversity'] = diversity
            # 执行交互
            if n_species <= 3:
                # 只负责和给定的邻居列表交互（慢空间模仿 + 量子捕食）
                for b, d in zip(neighbors, values or [{}] * len(neighbors)):
                    if a is b: continue
                    directed_d = np.dot(b.z - a.z, a.preference).real  # 方向性判断
                    d['directed_d'] = directed_d
                    slow_d = d.get("slow_d", np.linalg.norm(a.z - b.z))
                    pos_d = d.get("pos_d", np.linalg.norm(a.pos - b.pos))
                    if a.species_id == b.species_id:  # 同族：学习
                        # 慢空间吸引/排斥
                        interaction_strength = 1.0 - (slow_d / (diversity + 1e-8))
                        if slow_d < 2 * np.pi and random.random() < interaction_strength:
                            a.imitate(b, data=d)
                    elif a.target_id == b.target_id:  # 异族：竞争
                        predator_prob = np.exp(-len(neighbors) / 10.0) * 1 / (1 + n_species)  # species 越少越小,越拥挤越少打
                        if pos_d < 5 and random.random() < predator_prob:
                            a.predator(b, data=d)
                    elif a.level < b.level:
                        pass
            else:
                a.interact_kernel(neighbors, values)

    def reproduce(self, K=300):
        new_agents = []
        N = len(self.agents)
        density = N / K
        fitness = [0.5 * a.resource + 0.4 * a.purity_val + 0.3 * np.tanh(
            a.energy / 30) + 0.2 * a.alignment + 0.1 * np.exp(-((a.age - 50) ** 2) / 3600) for a in self.agents]
        threshold = np.percentile(fitness, 80)
        for a, s in zip(self.agents, fitness):
            birth_prob = (0.05 + 0.1 * s) * np.exp(- density)
            if a.resource > 1.0 and s > threshold and random.random() < birth_prob:
                child = a.reproduce()
                if child:
                    new_agents.append(child)
        self.agents.extend(new_agents)
        born = len(new_agents)
        self.stats["n_agents"] = len(self.agents)
        self.stats['birth_cum'] += born
        return born

    def death(self, K=300):
        N = len(self.agents)
        if N > K:
            resource_mean = self.stats.get("resource_mean", 1.0)
            life_activity_mean = self.stats.get("life_activity_mean", 1.0)
            base_prob = np.clip(0.2 + 0.8 * np.tanh((resource_mean + life_activity_mean) / 5), 0, 1)
            density = N / K  # 高密度惩罚
            survival_prob = base_prob * np.exp(-max(0, density - 1))
            self.agents = [a for a in self.agents
                           if a.purity_val > 0.15 and a.consistency_val > 0.05 and a.divergence_val < 1.0
                           and a.resource > -4.0 and a.energy < 50.0 and a.age < 500
                           and random.random() < survival_prob]
        else:
            self.agents = [a for a in self.agents
                           if a.purity_val > 0.1 and a.consistency_val > 0.05 and a.resource > -5.0 and a.age < 500]
        self.stats["n_agents"] = len(self.agents)
        died = N - self.stats["n_agents"]
        self.stats['death_cum'] += died
        return died

    def observe(self):
        """全部掉到“高能壳层”上了,慢空间的几何结构已经塌成一层壳了,所以只能统计行为特征了"""
        if not self.agents:
            obs = {
                "purity_mean": 0.0,
                "energy_mean": 0.0,
                "chaos_mean": 0.0,
                "n_agents": 0,
            }
            self.history.append(obs)
            return obs

        ps = [a.purity_val for a in self.agents]
        es = [a.energy for a in self.agents]
        cs = [a.chaos_val for a in self.agents]
        rs = [a.resource for a in self.agents]

        ts = [a.stats['T'] for a in self.agents]
        ts2 = [a.stats['T_phase'] for a in self.agents]
        fs = [a.fidelity_val for a in self.agents]
        ds = [a.divergence_val for a in self.agents]

        curvature = [a.curvature_val for a in self.agents]
        confidence = [a.confidence for a in self.agents]
        consistency = [a.consistency_val for a in self.agents]
        entropy = [a.plan_entropy_val for a in self.agents]
        move_entropy = [a.move_entropy_val for a in self.agents]
        entropy_deltas = [a.entropy_delta_cum for a in self.agents]
        energy_deltas = [a.energy_delta_cum / (a.age + 1) for a in self.agents]
        age = [a.age for a in self.agents]

        alignment = [a.alignment for a in self.agents]
        prefs = np.std(np.stack([a.preference for a in self.agents]), axis=0)

        phase_counts = np.sum([a.phase_count for a in self.agents], axis=0)
        phase_ratios = phase_counts / (phase_counts.sum() + 1e-8)
        interact_counts = np.array([a.interact_count / max(1, a.age) for a in self.agents])
        interact_ratios = interact_counts.mean(axis=0)
        hit_counts = [a.interact_count[5] for a in self.agents]

        diversity = [a.stats.get('diversity', 0.0) for a in self.agents]
        move_probs_std = [a.stats.get('move_probs_std', 0.0) for a in self.agents]
        bb_like = [a.purity_val > 0.9 and a.plan_entropy_val < 0.3 for a in self.agents]

        move_ids = [a.stats['move_id'] for a in self.agents if a.stats['move_id'] != -1]
        ids, counts = np.unique(move_ids, return_counts=True)
        self.move_counter[ids] += counts
        obs = {
            "purity_mean": np.mean(ps),
            "fidelity_mean": np.mean(fs),
            "consistency_mean": np.mean(consistency),
            "divergence_mean": np.mean(ds),

            "plan_entropy_mean": np.mean(entropy),
            "move_entropy_mean": np.mean(move_entropy),
            "energy_mean": np.mean(es),
            "chaos_mean": np.mean(cs),  # 0.275
            "curvature_mean": np.mean(curvature),

            "resource_mean": np.mean(rs),
            "age_mean": np.mean(age),  # 23
            "temperature_mean": np.mean(ts),
            "temperature_phase_mean": np.mean(ts2),
            "alignment_mean": np.mean(alignment),
            "confidence_mean": np.mean(confidence),
            'diversity_mean': np.mean(diversity),  # 邻居差异性

            "resource_std": np.std(rs),
            "resource_max": np.max(rs),
            "age_max": np.max(age),
            "energy_std": np.std(es),
            "energy_min": np.min(es),
            "entropy_max": np.max(entropy),
            "curvature_max": np.max(curvature),
            "purity_min": np.min(ps),
            "fidelity_min": np.min(fs),
            'consistency_min': np.min(consistency),
            "divergence_max": np.max(ds),
            'confidence_max': np.max(confidence),
            "temperature_max": np.max(ts),
            "pref_diversity": np.mean(prefs),  # preference 向量多样性

            'exploit_ratio': phase_ratios[0],
            'revert_ratio': phase_ratios[1],
            'explore_ratio': phase_ratios[2],
            'natura_ratio': phase_ratios[3],

            'imitate_avg': interact_ratios[0],
            'predator_avg': interact_ratios[1],
            'reproduce_avg': interact_ratios[2],
            'emulate_avg': interact_ratios[3],
            'hit_count': np.sum(hit_counts),
            'bb_lifetime_avg': interact_ratios[4],  # 0.06~0.314 虚假记忆快速被现实修正
            "bb_fraction": float(np.mean(bb_like)),  # boltzmann_brain
            "bb_count": np.sum(bb_like),

            'move_probs_std_mean': float(np.mean(move_probs_std)),
            'life_activity_mean': np.mean(entropy_deltas),  # 生命长度/活跃度(认知层面的变化)
            'cumulative_energy_delta_mean': np.mean(energy_deltas),
        }
        self.stats["resource_mean"] = obs["resource_mean"]
        self.stats["age_mean"] = obs["age_mean"]
        self.stats["life_activity_mean"] = obs["life_activity_mean"]
        obs.update(self.stats)  # 添加统计
        self.history.append(obs)
        return obs

    def save(self, filename=None):
        import pickle
        if filename is None:
            filename = os.path.join(DATA_DIR, "simulation_data.pkl")
        with open(filename, 'wb') as f:
            pickle.dump(self.history, f)

    def evolve(self, steps=300, max_k=300, print_every=10, base_temp=1.0 / 9.0):
        K = len(self.agents)
        P = 0
        targets = self.env.base_targets(type=1)
        prev_short_osc = 0.0

        for t in range(steps):
            a, b = divmod(t, 10)
            if b == 0 and K < max_k:
                K += 8 * (a + 1)
                self.stats['K'] = K

            T = base_temp
            if t < 3:  # 初期强探索
                T = 4.0 * base_temp
                P = 1
            elif t < self.env.model.Tf:
                T = 3.0 * base_temp
                P = 2
            elif t < 3 * self.env.model.Tf:
                P = 3
            else:  # 周期性温度波动
                short_osc = 2.0 / 3. * np.sin(2 * np.pi * t / 32)
                long_osc = 1.0 / 3 * np.sin(2 * np.pi * t / 100)
                temp_osc = short_osc + long_osc
                T = 2.0 * base_temp * (1.0 + temp_osc * (1.0 + 3 * long_osc))  # 双频扰动 0.25~3
                if (prev_short_osc < 0) and (short_osc >= 0):  # 接近零点/ 接近波峰
                    print(
                        f"[t={t}] 温度峰值扰动！新阶段 Phase {P},T={T:.3f} (short_osc={short_osc:.3f}, long_osc={long_osc:.3f})")
                    P += 1
                prev_short_osc = short_osc

            S = 10
            if self.stats.get('P', 0) != P:
                if P <= 3:
                    new_targets = targets.pop()
                    self.env.add_target(new_targets)
                elif len(self.env.targets) < 30:
                    new_targets = self.env.generate_diff_target()  # 每次温度峰值时生成新目标
                    self.env.add_target(new_targets)  # 添加新目标，增加环境复杂度

                self.stats['P'] = P
                self.stats['n_targets'] = self.env.context['n_targets']
                S = 1

            self.stats['T'] = T

            self.step(T=T, S=S, K=K)
            obs = self.observe()

            if obs["n_agents"] == 0:
                print(f"[t={t}] 种群灭绝！自动重生 10 个新个体...")
                self.agents = [
                    HybridAgent(CubieBase.generate_cubie(length=random.randint(0, 8)), self.env)
                    for _ in range(10)
                ]
                self.record()
                obs = self.observe()

            if t % print_every == 0:
                obs_display = {k: f"{float(v):.3f}" for k, v in obs.items()}
                phases = [a.stats['phase'] for a in self.agents]
                move_ids = [a.stats['move_id'] for a in self.agents if a.stats['move_id'] != -1]
                levels = [a.level for a in self.agents]
                target_ids = [a.target_id for a in self.agents]
                obs_distribution = {
                    "phase": {int(k): int(v) for k, v in zip(*np.unique(phases, return_counts=True)) if k >= 0},
                    "level": {int(k): int(v) for k, v in zip(*np.unique(levels, return_counts=True))},
                    "target": {int(k): int(v) for k, v in zip(*np.unique(target_ids, return_counts=True))},
                    "move": {int(k): int(v) for k, v in zip(*np.unique(move_ids, return_counts=True))}
                }
                print(f"[{t:3d}] obs={obs_display} \ndistribution={obs_distribution}")
                print(self.move_counter)

    def compute_flow(self):
        flows = []
        for a in self.agents:
            z1 = a.z.copy()
            initial_state = a.gm.re_act(a.state)
            z0 = self.env.model.project(initial_state.vector)
            flows.append((z1, z1 - z0))

        return flows

    def plot_flow(self):
        flows = self.compute_flow()

        Z = np.array([f[0].real for f in flows])  # 当前位置
        V = np.array([f[1].real for f in flows])

        R = np.random.randn(Z.shape[1], 2)
        R /= np.linalg.norm(R, axis=0) + 1e-8
        Z2 = Z @ R
        V2 = V @ R

        plt.figure(figsize=(12, 8))
        plt.quiver(Z2[:, 0], Z2[:, 1], V2[:, 0], V2[:, 1],
                   angles='xy', scale_units='xy', scale=1, alpha=0.5)

        plt.title("Population Flow Field,From Birth to Current")
        plt.grid(True, alpha=0.3)
        plt.show()

    def plot_population(self, n_last=60):
        if len(self.population_history) < n_last:
            return
        recent = self.population_history[-n_last:]
        plt.figure(figsize=(12, 8))
        for i, Z in enumerate(recent):
            Z_plot = self.env.model.evolve(Z, T=6)  # diffusion scaling
            # R = np.random.randn(Z_plot.shape[1], 2)
            # Z_plot = Z_plot @ R
            alpha = 0.1 + 0.9 * (i / (n_last - 1))
            plt.scatter(Z_plot[:, 0].real, Z_plot[:, 1].real, s=8, alpha=alpha, c='purple')
        plt.xlabel('Slow PC1')
        plt.ylabel('Slow PC2')
        plt.title('Hybrid Population on Slow Manifold (last 60 gens)')
        plt.grid(True, alpha=0.3)
        plt.show()

    def plot_metrics(self):
        steps = np.arange(len(self.history))
        purity = [h['purity_mean'] for h in self.history]
        energy = [h['energy_mean'] for h in self.history]
        chaos = [h['chaos_mean'] for h in self.history]

        fidelity = [h['fidelity_mean'] for h in self.history]
        plan_entropy = [h['plan_entropy_mean'] for h in self.history]
        consistency = [h['consistency_mean'] for h in self.history]

        divergence = [h['divergence_mean'] for h in self.history]
        resource = [h['resource_mean'] for h in self.history]

        n = [h['n_agents'] for h in self.history]

        fig, axs = plt.subplots(3, 3, figsize=(18, 12))
        axs[0, 0].plot(steps, purity, 'b-', label='Purity')
        axs[0, 1].plot(steps, energy, 'r-', label='Classical Energy')
        axs[0, 2].plot(steps, chaos, 'g-', label='Commutator Chaos')

        axs[1, 0].plot(steps, fidelity, 'c-', label='Fidelity')
        axs[1, 1].plot(steps, plan_entropy, 'brown', label='Plan Entropy')
        axs[1, 2].plot(steps, consistency, 'y-', label='Consistency Mean')

        axs[2, 0].plot(steps, divergence, 'k-', label='Divergence')
        axs[2, 1].plot(steps, resource, 'b-', label='Resource')
        axs[2, 2].plot(steps, n, 'm-', label='Population')
        for ax in axs.flat:
            ax.grid(True, alpha=0.3)
            ax.legend()
        plt.tight_layout()
        plt.show()

    def plot_additional_metrics(self):
        """其他 9 个指标的演化图"""
        steps = np.arange(len(self.history))

        alignment = [h.get('alignment_mean', 0) for h in self.history]
        temperature = [h.get('temperature_mean', 0) for h in self.history]
        diversity = [h.get('diversity_mean', 0) for h in self.history]

        curvature = [h.get('curvature_mean', 0) for h in self.history]
        confidence = [h['confidence_mean'] for h in self.history]
        move_probs_std = [h.get('move_probs_std_mean', 0) for h in self.history]

        bb_fraction = [h.get('bb_fraction', 0) for h in self.history]
        species = [h.get('n_species', 0) for h in self.history]
        pref_diversity = [h.get('pref_diversity', 0) for h in self.history]

        fig, axs = plt.subplots(3, 3, figsize=(18, 12))
        axs[0, 0].plot(steps, alignment, 'm-', label='Alignment')
        axs[0, 1].plot(steps, temperature, 'orange', label='Temperature Mean')
        axs[0, 2].plot(steps, diversity, 'y-', label='Diversity Mean')

        axs[1, 0].plot(steps, curvature, 'purple', label='Curvature')
        axs[1, 1].plot(steps, confidence, 'navy', label='Confidence')
        axs[1, 2].plot(steps, move_probs_std, 'teal', label='Move Probabilities Std')

        axs[2, 0].plot(steps, bb_fraction, 'k-', label='Boltzmann Brain Fraction')
        axs[2, 1].plot(steps, species, 'gold', label='Species Count')
        axs[2, 2].plot(steps, pref_diversity, 'brown', label='Preference Diversity')

        for ax in axs.flat:
            ax.grid(True, alpha=0.3)
            ax.legend()
        plt.suptitle('Additional Metrics Evolution', fontsize=16, y=1.0)
        plt.tight_layout()
        plt.show()

    def plot_extra_metrics(self):
        """绘制额外9个指标的演化图"""
        steps = np.arange(len(self.history))

        resource_std = [h['resource_std'] for h in self.history]
        curvature_max = [h.get('curvature_max', 0) for h in self.history]
        entropy_max = [h.get('entropy_max', 0) for h in self.history]

        life_activity = [h.get('life_activity_mean', 0) for h in self.history]  # entropy_deltas
        cumulative_energy_delta = [h.get('cumulative_energy_delta_mean', 0) for h in self.history]  # energy_deltas
        age = [h.get('age_mean', 0) for h in self.history]

        death = [h.get('death_cum', 0) for h in self.history]
        birth = [h.get('birth_cum', 0) for h in self.history]

        hit_count = [h.get('hit_count', 0) for h in self.history]
        bb_count = [h.get('bb_count', 0) for h in self.history]

        fig, axs = plt.subplots(3, 3, figsize=(18, 12))

        axs[0, 0].plot(steps, curvature_max, 'purple', label='Curvature Max')
        axs[0, 1].plot(steps, entropy_max, 'darkgreen', label='Plan Entropy Max')
        axs[0, 2].plot(steps, resource_std, 'teal', label='Resource Std')

        axs[1, 0].plot(steps, life_activity, 'magenta', label='Life Activity (Entropy Deltas)')
        axs[1, 1].plot(steps, cumulative_energy_delta, 'orange', label='Cumulative Energy Delta')
        axs[1, 2].plot(steps, age, 'cyan', label='Age Mean')

        axs[2, 0].plot(steps, death, 'brown', label='Death Cumulative')
        axs[2, 0].plot(steps, birth, 'navy', label='Birth Cumulative')
        axs[2, 1].plot(steps, hit_count, 'red', label='Hit Target Count')
        axs[2, 2].plot(steps, bb_count, 'darkblue', label='Boltzmann Brain Count')

        for ax in axs.flat:
            ax.grid(True, alpha=0.3)
            ax.legend()
        plt.suptitle('Extra Metrics Evolution (New Variables)', fontsize=16, y=1.0)
        plt.tight_layout()
        plt.show()

    def plot_phase(self):
        """绘制四个 phase 的比例演化图（堆叠面积图）"""

        steps = np.arange(len(self.history))

        exploit = [h.get('exploit_ratio', 0) for h in self.history]
        revert = [h.get('revert_ratio', 0) for h in self.history]
        explore = [h.get('explore_ratio', 0) for h in self.history]
        natura = [h.get('natura_ratio', 0) for h in self.history]

        plt.figure(figsize=(12, 7))

        plt.stackplot(steps,
                      exploit, revert, explore, natura,
                      labels=['Exploit (利用)', 'Revert (回退)',
                              'Explore (探索)', 'Natura (自然/变异)'],
                      colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                      alpha=0.85)

        plt.xlabel('Evolution Steps')
        plt.ylabel('Phase Ratio')
        plt.title('Phase Distribution Over Time (Stacked Area)')
        plt.legend(loc='upper left', frameon=True)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.show()

    def plot_interaction(self, n_last=100):
        """画交互行为平均次数的变化曲线"""

        recent = self.history[-n_last:]
        steps = list(range(len(recent)))

        # 提取各项
        imitate = [h.get('imitate_avg', 0) for h in recent]
        predator = [h.get('predator_avg', 0) for h in recent]
        reproduce = [h.get('reproduce_avg', 0) for h in recent]
        emulate = [h.get('emulate_avg', 0) for h in recent]
        # crisis = [h.get('crisis_avg', 0) for h in recent]
        bb_lifetime = [h.get('bb_lifetime_avg', 0) for h in recent]

        plt.figure(figsize=(12, 8))

        plt.plot(steps, imitate, label='Imitate', linewidth=2.5, color='tab:blue')
        plt.plot(steps, predator, label='Predator', linewidth=2.5, color='tab:red')
        plt.plot(steps, reproduce, label='Reproduce', linewidth=2.5, color='tab:green')
        plt.plot(steps, emulate, label='Emulate', linewidth=2.5, color='tab:orange')
        # plt.plot(steps, crisis, label='Crisis', linewidth=2.5, color='tab:purple')
        plt.plot(steps, bb_lifetime, label='BB Lifetime', linewidth=2.5, color='tab:cyan', linestyle='--')

        plt.title("Average Interaction Counts per Agent over Time")
        plt.xlabel("Steps")
        plt.ylabel("Average Interactions per Step")
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_agent_rho(self, rho_type='rho_plan'):
        """
        找出 age 最大的 Agent，并画出它的 rho 热力图
        rho_type 可选: 'rho', 'rho_plan', 'rho_mem'
        """
        import seaborn as sns
        # 找出 age 最大的 Agent
        oldest_agent = max(self.agents, key=lambda a: a.age)
        # 额外打印一些信息
        print(f"Agent (age={oldest_agent.age})")
        print(f"  Purity (rho_plan): {oldest_agent.purity_val:.4f}")
        print(f"  Fidelity: {oldest_agent.fidelity_val:.4f}")
        print(f"  Divergence: {oldest_agent.divergence_val:.4f}")
        print(f"  Entropy: {oldest_agent.plan_entropy_val:.4f}")

        # 获取对应的 rho
        if rho_type == 'rho_plan':
            rho = oldest_agent.rho_plan
            rho_name = 'rho_plan (规划态)'
        elif rho_type == 'rho_mem':
            rho = oldest_agent.rho_mem
            rho_name = 'rho_mem (长期记忆)'
        else:
            rho = oldest_agent.rho
            rho_name = 'rho'

        # 转为实部矩阵（热力图通常看实部或绝对值）
        rho_real = np.real(rho)
        mask = np.triu(np.ones_like(rho_real, dtype=bool), k=1)
        plt.figure(figsize=(10, 8))
        # sns.heatmap(np.abs(rho), cmap='viridis', annot=False)
        sns.heatmap(rho_real, mask=mask,
                    cmap='RdBu_r',
                    center=0,
                    annot=False,
                    cbar_kws={'label': 'Real Part'})

        plt.title(f"Agent rho Age = {oldest_agent.age} | {rho_name} | Purity = {oldest_agent.purity_val:.4f}")
        plt.xlabel("Dimension Index")
        plt.ylabel("Dimension Index")
        plt.tight_layout()
        plt.show()


def main():
    env = Environment(model=SlowDynamics(n=N_GENERATORS))
    sim = HybridSimulation(env=env, n_agents=30)
    sim.evolve(steps=123, print_every=10, max_k=400)
    sim.plot_population()
    sim.plot_metrics()
    sim.plot_additional_metrics()
    sim.plot_extra_metrics()
    sim.plot_phase()
    sim.plot_interaction()
    sim.plot_agent_rho()
    sim.plot_flow()
    sim.save()


if __name__ == '__main__':
    main()
