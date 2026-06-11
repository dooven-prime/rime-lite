import numpy as np
from scipy.linalg import sqrtm, logm, expm
from collections import Counter


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

def find_qsqrt5_form(lam, tol= 1e-4):
    """Find (a + b√5)/c representation for λ, if one exists.
    Searches small integer ranges. Returns (a, b, c) or None."""
    sqrt5 = np.sqrt(5)
    for c in range(2, 41):
        for a in range(-c, 2 * c + 1):
            for b in [-2, -1, 1, 2]:
                target = (a + b * sqrt5) / c
                if abs(lam - target) < tol:
                    return a, b, c
    return None

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
