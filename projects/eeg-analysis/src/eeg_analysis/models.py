"""Interpretable classical EEG feature baselines."""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.linalg import eigh
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def log_bandpower(X: np.ndarray, sfreq: float) -> np.ndarray:
    """Welch log power in mu (8–13 Hz) and beta (13–30 Hz), for each EEG channel."""
    frequencies, power = signal.welch(
        X, fs=sfreq, nperseg=min(256, X.shape[-1]), axis=-1
    )
    features = []
    for low, high in ((8.0, 13.0), (13.0, 30.0)):
        mask = (frequencies >= low) & (frequencies < high)
        if not np.any(mask):
            raise ValueError(f"No Welch bins in requested band {low:g}–{high:g} Hz")
        features.append(np.log(power[..., mask].mean(axis=-1) + 1e-12))
    return np.concatenate(features, axis=1)


class BandPowerLogisticRegression:
    """Per-channel mu/beta log-power features followed by standardized L2 logistic regression."""

    def __init__(self, sfreq: float, C: float = 0.1):
        self.sfreq = sfreq
        self.model = make_pipeline(
            StandardScaler(), LogisticRegression(C=C, max_iter=2000, random_state=0)
        )

    def fit(self, X: np.ndarray, y: np.ndarray, *, features: np.ndarray | None = None):
        if features is None:
            features = log_bandpower(X, self.sfreq)
        self.model.fit(features, y)
        return self

    def predict(self, X: np.ndarray, *, features: np.ndarray | None = None) -> np.ndarray:
        if features is None:
            features = log_bandpower(X, self.sfreq)
        return self.model.predict(features)

    def predict_proba(self, X: np.ndarray, *, features: np.ndarray | None = None) -> np.ndarray:
        if features is None:
            features = log_bandpower(X, self.sfreq)
        return self.model.predict_proba(features)


def normalized_trial_covariances(X: np.ndarray) -> np.ndarray:
    """Return trace-normalized channel covariances for each trial.

    This label-free transform can be computed once and sliced by participant fold. CSP's
    class covariance averages and spatial filters are still fit using training trials only.
    """
    covariances = X @ np.swapaxes(X, 1, 2)
    traces = np.trace(covariances, axis1=1, axis2=2)
    covariances /= np.maximum(traces[:, None, None], 1e-12)
    return covariances


class CSPLinearDiscriminant:
    """Shrinkage-regularized Common Spatial Patterns followed by shrinkage LDA."""

    def __init__(self, n_components: int = 6, regularization: float = 0.01):
        self.n_components = n_components
        self.regularization = regularization

    def _features(self, X: np.ndarray) -> np.ndarray:
        projected = self.filters_[None, :, :] @ X
        variances = projected.var(axis=-1)
        return np.log(variances / np.maximum(variances.sum(axis=1, keepdims=True), 1e-12))

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        covariances: np.ndarray | None = None,
    ):
        X64 = np.asarray(X, dtype=np.float64)
        if covariances is None:
            covariances = normalized_trial_covariances(X64)
        covariance_left = covariances[y == 0].mean(axis=0, dtype=np.float64)
        covariance_right = covariances[y == 1].mean(axis=0, dtype=np.float64)
        n_channels = covariance_left.shape[0]
        reg_eye = self.regularization * np.eye(n_channels) / n_channels
        covariance_left = (1 - self.regularization) * covariance_left + reg_eye
        covariance_right = (1 - self.regularization) * covariance_right + reg_eye
        _, vectors = eigh(covariance_left, covariance_left + covariance_right)
        half = self.n_components // 2
        indices = np.r_[np.arange(half), np.arange(n_channels - half, n_channels)]
        self.filters_ = vectors[:, indices].T
        self.model_ = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
        self.model_.fit(self._features(X64), y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model_.predict(self._features(np.asarray(X, dtype=np.float64)))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model_.predict_proba(self._features(np.asarray(X, dtype=np.float64)))


def make_models(sfreq: float) -> dict:
    """Return newly constructed, unfitted model instances."""
    from sklearn.dummy import DummyClassifier

    return {
        "majority": lambda: DummyClassifier(strategy="prior"),
        "bandpower_logreg": lambda: BandPowerLogisticRegression(sfreq=sfreq, C=0.1),
        "csp_lda": lambda: CSPLinearDiscriminant(n_components=6, regularization=0.01),
    }
