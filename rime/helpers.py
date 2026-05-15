import numpy as np
from scipy.linalg import sqrtm, logm, expm
from collections import Counter


def dbscan(X, eps=0.5, min_samples=5):
    n = X.shape[0]
    labels = np.full(n, -1)  # -1 表示噪声
    visited = np.zeros(n, dtype=bool)
    cluster_id = 0

    # 预计算距离矩阵
    dist_matrix = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)

    def region_query(i):
        return np.where(dist_matrix[i] <= eps)[0]

    def expand_cluster(i, neighbors):
        nonlocal cluster_id
        labels[i] = cluster_id

        j = 0
        while j < len(neighbors):
            pt = neighbors[j]

            if not visited[pt]:
                visited[pt] = True
                pt_neighbors = region_query(pt)

                if len(pt_neighbors) >= min_samples:
                    neighbors = np.concatenate([neighbors, pt_neighbors])

            if labels[pt] == -1:
                labels[pt] = cluster_id

            j += 1

    for i in range(n):
        if visited[i]:
            continue

        visited[i] = True
        neighbors = region_query(i)

        if len(neighbors) < min_samples:
            labels[i] = -1  # 噪声
        else:
            expand_cluster(i, neighbors)
            cluster_id += 1

    return labels


def kmeans(X, k, max_iter=100, tol=1e-4, init="kmeans++", seed=42):
    rng = np.random.default_rng(seed)
    n, d = X.shape
    # 1. 初始化中心（随机选k个点）
    if init == "kmeans++":
        centroids = []

        # 1. 随机选第一个中心
        idx = rng.integers(n)
        centroids.append(X[idx])

        for _ in range(1, k):
            # 2. 计算每个点到最近中心的距离平方
            dists = np.min(
                np.linalg.norm(X[:, None, :] - np.array(centroids)[None, :, :], axis=2) ** 2,
                axis=1
            )

            # 3. 按距离加权采样
            probs = dists / np.sum(dists)
            idx = rng.choice(n, p=probs)

            centroids.append(X[idx])

        centroids = np.array(centroids)

    else:  # "random":
        centroids = X[rng.choice(n, k, replace=False)]

    for _ in range(max_iter):
        # 2. 计算距离 (n, k)
        distances = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)

        # 3. 分配标签
        labels = np.argmin(distances, axis=1)

        # 4. 更新中心
        new_centroids = np.array([
            X[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
            for i in range(k)
        ])

        # 5. 收敛判断
        if np.linalg.norm(new_centroids - centroids) < tol:
            break

        centroids = new_centroids

    return centroids, labels


# from sklearn.metrics.pairwise import cosine_similarity
def cosine_similarity(ndarr1, ndarr2):
    ndarr1 = np.atleast_2d(ndarr1)
    ndarr2 = np.atleast_2d(ndarr2)
    denominator = np.outer(np.linalg.norm(ndarr1, axis=1), np.linalg.norm(ndarr2, axis=1))
    dot_product = np.dot(ndarr1, ndarr2.T)  # np.einsum('ik,jk->ij', ndarr1, ndarr2)
    with np.errstate(divide='ignore', invalid='ignore'):
        similarity = np.where(denominator != 0, dot_product / denominator, 0)
    return similarity


# from sklearn.metrics.pairwise import cosine_distances
def cosine_distance(a, b):
    return 1.0 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


# from scipy.special import softmax
def softmax(x):
    if x.ndim == 1:
        e_x = np.exp(x - np.max(x))  # Subtract max for numerical stability
        return e_x / e_x.sum()
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))  # 对每行减去最大值
    return e_x / np.sum(e_x, axis=1, keepdims=True)


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


def normalize_p(x):
    """分位数标准化"""
    x = (x - np.percentile(x, 50)) / (np.percentile(x, 90) - np.percentile(x, 10) + 1e-8)
    return x


def normalize_z(x):
    """Z-score"""
    return (x - x.mean()) / (x.std() + 1e-6)


def von_neumann_entropy(rho):
    """
    S = -Tr(ρ ln ρ) 冯纽曼熵 在纯态下取值为零,
    rho_b:规划空间的混乱程度，越高说明想象力越丰富、决策越不确定
    """
    w = np.linalg.eigvalsh(rho)
    w = w[w > 1e-12]
    return -np.sum(w * np.log(w)) if len(w) > 0 else 0.0


def kl_divergence(p, q, eps=1e-10):
    """单个 KL(p || q)，带数值稳定"""
    p = np.asarray(p) + eps
    q = np.asarray(q) + eps
    p = p / p.sum()
    q = q / q.sum()
    return np.sum(p * np.log(p / q))


def compute_total_jeffreys(distributions, eps=1e-10):
    """对称 KL 散度： KL(p||q) + KL(q||p) """
    k = len(distributions)
    total = 0.0
    for i in range(k):
        for j in range(i + 1, k):  # 只计算上三角，避免重复
            kl_ij = kl_divergence(distributions[i], distributions[j], eps)
            kl_ji = kl_divergence(distributions[j], distributions[i], eps)
            jd = kl_ij + kl_ji
            total += jd
    return total


def pairwise_kl_matrix(distributions, eps=1e-10):
    """返回 (k, k) 的 KL 距离矩阵"""
    k = len(distributions)
    dists = np.array(distributions) + eps
    dists = dists / dists.sum(axis=1, keepdims=True)

    # log(p/q) = log p - log q
    log_dists = np.log(dists)
    kl_matrix = np.zeros((k, k))

    for i in range(k):
        kl_matrix[i] = np.sum(dists[i][:, None] * (log_dists[i][:, None] - log_dists), axis=0)

    return kl_matrix


def fidelity(rho, sigma, eps=1e-8):
    """
    计算两个密度矩阵的保真度 F(ρ, σ) = [Tr √(√ρ σ √ρ)]²
    重叠程度，越接近1越相似
    """
    # 正则化（防止特征值过小导致 sqrtm 失败）
    rho_reg = rho + eps * np.eye(rho.shape[0])
    sigma_reg = sigma + eps * np.eye(sigma.shape[0])
    sqrt_rho = sqrtm(rho_reg)  # matrix_sqrt(rho)
    middle = sqrt_rho @ sigma_reg @ sqrt_rho.conj().T
    sqrt_middle = sqrtm(middle)
    fid = np.real(np.trace(sqrt_middle)) ** 2
    return np.clip(fid, 0.0, 1.0)


def matrix_log(A, eps=1e-10):
    """Hermitian 矩阵的对数（仅适用于正半定矩阵）"""
    eigvals, eigvecs = np.linalg.eigh(A)
    eigvals = np.maximum(eigvals, eps)  # 避免 log(0)
    log_eigvals = np.log(eigvals)
    return eigvecs @ np.diag(log_eigvals) @ eigvecs.conj().T


def matrix_sqrt(A, tol=1e-10):
    """用特征值分解实现 Hermitian 矩阵的平方根（仅适用于正半定 Hermitian 矩阵）"""
    eigvals, eigvecs = np.linalg.eigh(A)  # 密度矩阵是 Hermitian 的
    # 数值稳定性处理：负的极小特征值置0
    eigvals = np.maximum(eigvals, 0.0)
    sqrt_eigvals = np.sqrt(eigvals)
    return eigvecs @ np.diag(sqrt_eigvals) @ eigvecs.conj().T


def quantum_cross_entropy(rho, sigma, eps=1e-10):
    """适合一个分布相对于另一个分布的预测误差，不对称"""
    sigma_reg = sigma + eps * np.eye(sigma.shape[0], dtype=complex)
    log_sigma = logm(sigma_reg)  # matrix_log
    cross_ent = -np.real(np.trace(rho @ log_sigma))
    return max(cross_ent, 0.0)  # 不对称


def time_evolution(H, psi0, t_list, hbar=1.0):
    """
    求解时间相关薛定谔方程：iℏ∂ψ/∂t = Hψ
    使用形式解：ψ(t) = exp(-iHt/ℏ) ψ(0)
    """
    psi_t = []
    for t in t_list:
        # 时间演化算符 U(t) = exp(-iHt/ℏ)
        U = expm(-1j * H * t / hbar)
        psi = U @ psi0
        psi_t.append(psi)

    return np.array(psi_t)


def rho_sigreg(rho, num_projections=32, lambda_reg=0.08):
    """
    强制 latent embedding 的随机投影接近各向同性高斯分布，从而防止 collapse（所有表示坍缩到同一个点或极端纯态）
    LeCun SIGReg 适配版：对 rho_b 施加轻量正则，防止过度纯态或过度混沌
    lambda_reg: 正则强度（建议 0.05~0.12）
    """
    dim = rho.shape[0]
    total = 0.0
    for _ in range(num_projections):
        # 随机投影方向（单位向量）
        v = np.random.randn(dim) + 1j * np.random.randn(dim)
        v /= np.linalg.norm(v) + 1e-12

        proj = np.real(np.vdot(v, rho @ v))  # 计算二次型 <v| rho_b |v> （实数）

        # 希望 proj 接近标准正态分布的统计特性（均值0，方差1）
        # 用简单的平方惩罚（接近 LeCun 的 sketched Gaussian 思想）
        # mean_loss = (proj - 1.0 / dim) ** 2
        # var_loss = (proj**2 - 1.0 / dim) ** 2
        total += (proj - 0.5) ** 2 + 0.1 * (proj ** 2 - 1.0) ** 2

    return lambda_reg * (total / num_projections)


def sinkhorn_basic(matrix: np.ndarray, max_iter: int = 300, tol: float = 1e-4, epsilon=1e-8):
    """
    基础Sinkhorn算法：将非负方阵转换为双随机矩阵

    参数:
        matrix: 输入的非负方阵 (n x n)
        max_iter: 最大迭代次数
        tol: 收敛容差（行/列和与1的最大允许偏差）
        epsilon: 小常数，防止除零

    返回:
        P: 双随机矩阵
        n_iter: 实际迭代次数
        err: 最终误差
    """
    A = matrix.copy().astype(np.float64)

    # 确保非负并添加小常数避免除零
    A = np.maximum(A, 0) + epsilon

    for i in range(max_iter):
        # 行归一化
        row_sums = A.sum(axis=1, keepdims=True)
        A /= row_sums

        # 列归一化
        col_sums = A.sum(axis=0, keepdims=True)
        A /= col_sums

        # 检查收敛：计算行和与列和与1的最大偏差
        row_err = np.max(np.abs(A.sum(axis=1) - 1))
        col_err = np.max(np.abs(A.sum(axis=0) - 1))
        err = max(row_err, col_err)

        if err < tol:
            return A, i + 1, err

    print(f"警告：未在 {max_iter} 次迭代内收敛，最终误差: {err:.2e}")
    return A, max_iter, err


def get_probability(data: list | tuple | dict, output_format: str = "probs", sort: bool = False) -> dict:
    """
    统计列表中的元素频率，并支持不同的输出格式。

    :param data: 输入的列表,possibilities
    :param output_format: 输出格式，可选值：
        - "counter": 返回 Counter 统计的字典
        - "probability": 返回归一化的概率字典,normalize
    :param sort: 按值从大到小排序
    :return: 对应格式的统计结果
    """
    ct = data.copy() if isinstance(data, dict) else Counter(data)
    if output_format == "counter":
        if sort:
            ct = sorted(ct.items(), key=lambda x: x[1], reverse=True)
        return dict(ct)

    if output_format in ("probs", "probability"):
        total = sum(ct.values())
        if total == 0:
            return {}
        probs = {key: value / total for key, value in ct.items()}
        if sort:
            return dict(sorted(probs.items(), key=lambda x: x[1], reverse=True))
        return probs

    raise ValueError("Invalid output_format. Choose from  'counter' or 'probability'.")


def normalize_weights(items: list | tuple, weights: dict | list | tuple | float | int) -> list:
    """
    将多种形式的权重输入统一为与 items 对齐的概率列表。

    :param items: 要采样的元素序列
    :param weights: 输入权重，可以是 dict / list / tuple / float / int / None
    :return: 概率（未必归一化，但可直接用于 random.choices / np.random.choice）
    """
    n = len(items)
    # weights 是数字 → 均匀随机
    if isinstance(weights, (float, int)):
        probabilities = [1.0 / n] * n
    elif isinstance(weights, (list, tuple)):
        if len(weights) != n:
            raise ValueError(f"权重长度 {len(weights)} 与元素数 {n} 不匹配")
        probabilities = list(weights)
    elif isinstance(weights, dict):  # 处理缺失的权重
        probabilities = [weights.get(x, 0.0) for x in items]
    else:
        raise TypeError(f"不支持的权重类型: {type(weights)}")

    if any(w < 0 for w in probabilities):
        raise ValueError("权重必须为非负数")
    if sum(probabilities) <= 0:
        raise ValueError("权重总和必须大于 0")
    return probabilities  # weights 相对权重,只需要是正数，相对大小决定了选择概率,会自动归一化


def weierstrass(x, a=0.5, b=21, n_terms=100):
    """
    威尔斯特拉斯函数实现

    参数:
        x: 输入值或数组
        a: 振幅衰减系数 (0 < a < 1)
        b: 频率增长基数 (正奇数)
        n_terms: 级数截断项数
    """
    # 验证参数条件（原始严格条件）
    assert 0 < a < 1, "a必须在(0,1)之间"
    assert b % 2 == 1, "b必须是奇数"
    assert a * b > 1 + 3 * np.pi / 2, "不满足处处不可导条件"

    x = np.atleast_1d(x)
    result = np.zeros_like(x, dtype=float)

    # 计算级数和
    for n in range(n_terms):
        result += a ** n * np.cos(b ** n * np.pi * x)

    return result


def is_rational_form(lam, denom, tol=1e-5):
    """Check if λ ≈ k/denom for some integer k (0 ≤ k ≤ denom).

    Used to detect eigenvalues of the form λ = 1 − k/m
    in face-symmetric generator sets.
    """
    return abs(lam - round(lam * denom) / denom) < tol


# ============================================================
# Spectral field detection utilities
# ============================================================

def is_in_qsqrt5(lam, tol=1e-5):
    """Check if λ ∈ ℚ(√5): λ = (p + q√5)/r for small integers p,q,r with q≠0.

    Returns (True, (p, q, r)) if found, else (False, None).
    Used by the spectral rationality paper to detect ℚ(√5) eigenvalues
    in symmetry-broken generator sets (n=8, n=16).
    """
    sqrt5 = np.sqrt(5)
    for p in range(-20, 21):
        for q in range(-20, 21):
            if q == 0:
                continue
            for r in range(1, 21):
                val = (p + q * sqrt5) / r
                if abs(lam - val) < tol:
                    return True, (p, q, r)
    return False, None


def krawtchouk(k, x, n=3):
    """Krawtchouk polynomial K_k(x; n, q=2).

    K_k(x; n, 2) = sum_{j=0}^k (-1)^j C(x, j) C(n-x, k-j)

    Used in Hamming association schemes (e.g., Q3 hypercube cp block).
    The eigenmatrix of the H(n,2) scheme is P[k,d] = K_k(d; n, 2).
    """
    from math import comb
    total = 0
    for j in range(k + 1):
        total += ((-1) ** j) * comb(x, j) * comb(n - x, k - j)
    return total


def geometric_brownian_motion(S0=100, mu=0.05, sigma=0.2, T=1.0, N=1000, seed=None):
    """几何布朗运动（Black-Scholes模型基础）"""
    if seed is not None:
        np.random.seed(seed)

    dt = T / N
    t = np.linspace(0, T, N + 1)

    # 通过标准布朗运动转换
    dW = np.random.normal(0, np.sqrt(dt), N)  # 增量服从 N(0, dt)
    W = np.cumsum(dW)  # 累积和
    W = np.insert(W, 0, 0)  # W(0) = 0
    # S(t) = S0 * exp((mu - 0.5*sigma^2)*t + sigma*W(t))
    S = S0 * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * W)

    return t, S


# ============================================================
# Linear algebra / spectral utilities
# ============================================================


def poly_rank(A, k=6, tol=1e-10):
    """Krylov subspace rank: rank{I, A, A², ..., A^{k-1}} = minimal polynomial degree.

    BUGFIX: np.linalg.matrix_rank default tolerance is unreliable
    for large matrices. Uses SVD + explicit tolerance for numerical stability.

    Args:
        A: (n,n) square matrix
        k: number of Krylov vectors to test
        tol: singular value threshold

    Returns:
        int: rank of the Krylov subspace
    """
    mats = []
    Ak = np.eye(A.shape[0])

    for i in range(k):
        mats.append(Ak.flatten())
        Ak = Ak @ A

    M = np.vstack(mats)
    _, s, _ = np.linalg.svd(M, full_matrices=False)
    return np.sum(s > tol * max(s[0], 1.0))


def construct_projection_operators(U, blocks, tol=1e-12):
    """Construct Hermitian projection operators from basis U and block indices.

    For each block b (list of indices), returns P_b = U[:,b] @ U[:,b]†.
    Numerical corrections ensure idempotence: P[np.abs(P) < tol] = 0.

    Args:
        U: (n,n) basis matrix (e.g., eigenvector matrix)
        blocks: list of index lists defining the blocks
        tol: threshold for numerical zero

    Returns:
        list of (n,n) Hermitian projection matrices
    """
    projections = []
    for b in blocks:
        Ub = U[:, b]  # basis for this block
        P = Ub @ Ub.T.conj()  # projector
        P[np.abs(P) < tol] = 0  # enforce idempotence numerically
        projections.append(P)
    return projections


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import os

    # os.environ["OMP_NUM_THREADS"] = "8"
    # os.environ["MKL_NUM_THREADS"] = "8"
    # Adjust these paths to match your actual Tcl/Tk directories
    os.environ['TCL_LIBRARY'] = r'D:\Program Files\Python\Python313\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'D:\Program Files\Python\Python313\tcl\tk8.6'
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    x = np.linspace(-2, 2, 10000)
    y = weierstrass(x, a=0.5, b=21, n_terms=50)
    # 全局视图
    axes[0].plot(x, y, 'b-', linewidth=0.8)
    axes[0].set_title('Weierstrass Function (Global View)')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('W(x)')
    axes[0].grid(True, alpha=0.3)

    # 局部放大视图（展示自相似性）
    x_zoom = np.linspace(0.5, 0.55, 5000)
    y_zoom = weierstrass(x_zoom, a=0.5, b=21, n_terms=100)
    axes[1].plot(x_zoom, y_zoom, 'r-', linewidth=0.8)
    axes[1].set_title('Zoomed In (0.5 to 0.55)')
    axes[1].set_xlabel('x')
    axes[1].grid(True, alpha=0.3)

    for i in range(5):
        t, S = geometric_brownian_motion(S0=100, mu=0.1, sigma=0.3, T=1.0, seed=i)
        axes[2].plot(t, S, alpha=0.7)
    axes[2].set_title('Geometric Brownian Motion (Stock Price Simulation)')
    axes[2].set_xlabel('t')
    axes[2].set_ylabel('S(t)')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
