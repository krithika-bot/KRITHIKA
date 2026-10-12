"""Electrode-graph construction. Every graph returns a symmetric, non-negative adjacency with a
zero diagonal; `normalize_adjacency` adds self loops and applies D^-1/2 (A+I) D^-1/2 (Kipf & Welling).

Graph kinds (used for the ablation):
  identity  - no edges: the GCN degenerates to a per-electrode model (the "no graph" control)
  uniform   - fully connected, equal weights (graph present but carries no spatial information)
  random    - same number of edges and same weights as `distance`, but random electrode pairs
  distance  - Gaussian kernel on 3-D electrode distance, k nearest neighbours
  corr      - mean |Pearson correlation| between channels, estimated on TRAINING trials only
  plv       - mean phase-locking value between channels, estimated on TRAINING trials only
"""
from __future__ import annotations

import numpy as np
from scipy.signal import hilbert


def pairwise_distances(pos: np.ndarray) -> np.ndarray:
    return np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=-1)


def knn_sparsify(W: np.ndarray, k: int) -> np.ndarray:
    """Keep each node's k strongest edges, then symmetrise with max."""
    W = W.copy()
    np.fill_diagonal(W, 0.0)
    keep = np.zeros_like(W, dtype=bool)
    idx = np.argsort(-W, axis=1)[:, :k]
    rows = np.arange(W.shape[0])[:, None]
    keep[rows, idx] = True
    keep = keep | keep.T
    return np.where(keep, W, 0.0)


def distance_adjacency(pos: np.ndarray, k: int = 6, sigma: float | None = None) -> np.ndarray:
    d = pairwise_distances(pos)
    if sigma is None:
        sigma = float(np.median(d[np.triu_indices_from(d, k=1)]))
    W = np.exp(-(d ** 2) / (2 * sigma ** 2))
    return knn_sparsify(W, k)


def uniform_adjacency(n: int) -> np.ndarray:
    A = np.ones((n, n))
    np.fill_diagonal(A, 0.0)
    return A


def identity_adjacency(n: int) -> np.ndarray:
    return np.zeros((n, n))


def random_adjacency(reference: np.ndarray, seed: int = 0) -> np.ndarray:
    """Random graph with the same edge count and edge-weight multiset as `reference`."""
    rng = np.random.default_rng(seed)
    n = reference.shape[0]
    iu = np.triu_indices(n, k=1)
    weights = reference[iu]
    nz = weights[weights > 0]
    pick = rng.choice(len(weights), size=len(nz), replace=False)
    out = np.zeros(len(weights))
    out[pick] = rng.permutation(nz)
    A = np.zeros((n, n))
    A[iu] = out
    return A + A.T


def correlation_adjacency(X: np.ndarray, k: int = 6, chunk: int = 256) -> np.ndarray:
    """Mean absolute channel correlation over trials (X: n_trials, n_channels, n_times)."""
    n, c, t = X.shape
    total = np.zeros((c, c))
    for i in range(0, n, chunk):
        Z = X[i:i + chunk].astype(np.float64)
        Z = Z - Z.mean(-1, keepdims=True)
        Z = Z / (np.linalg.norm(Z, axis=-1, keepdims=True) + 1e-12)
        total += np.abs(np.matmul(Z, Z.transpose(0, 2, 1))).sum(0)
    return knn_sparsify(total / n, k)


def plv_adjacency(X: np.ndarray, k: int = 6, chunk: int = 128) -> np.ndarray:
    """Mean phase-locking value between channels over trials (X should already be band-limited)."""
    n, c, t = X.shape
    total = np.zeros((c, c))
    for i in range(0, n, chunk):
        U = np.exp(1j * np.angle(hilbert(X[i:i + chunk].astype(np.float64), axis=-1)))
        total += np.abs(np.matmul(U, U.conj().transpose(0, 2, 1)) / t).sum(0)
    return knn_sparsify(total / n, k)


def normalize_adjacency(A: np.ndarray) -> np.ndarray:
    A_tilde = A + np.eye(A.shape[0])
    deg = A_tilde.sum(1)
    d_inv_sqrt = 1.0 / np.sqrt(deg)
    return (d_inv_sqrt[:, None] * A_tilde * d_inv_sqrt[None, :]).astype(np.float32)


def build_adjacency(kind: str, pos: np.ndarray, X_train: np.ndarray | None, k: int = 6,
                    sigma: float | None = None, seed: int = 0) -> np.ndarray:
    """Raw (un-normalised) adjacency of the requested kind. Data-driven graphs use X_train only."""
    n = pos.shape[0]
    if kind == "identity":
        return identity_adjacency(n)
    if kind == "uniform":
        return uniform_adjacency(n)
    if kind == "distance":
        return distance_adjacency(pos, k, sigma)
    if kind == "random":
        return random_adjacency(distance_adjacency(pos, k, sigma), seed)
    if kind == "corr":
        assert X_train is not None, "corr graph needs training data"
        return correlation_adjacency(X_train, k)
    if kind == "plv":
        assert X_train is not None, "plv graph needs training data"
        return plv_adjacency(X_train, k)
    raise ValueError(f"unknown graph kind: {kind}")
