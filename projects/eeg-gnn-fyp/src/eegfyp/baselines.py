"""Classical baselines, implemented from scratch / with scikit-learn (no deep-learning dependency)."""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .preprocess import log_bandpower


class CSP(BaseEstimator):
    """Common Spatial Patterns (Ramoser et al., 2000) for two classes.

    Filters solve  C0 w = lambda (C0 + C1) w  on trace-normalised, shrinkage-regularised class
    covariances. Features are log normalised variances of the `n_components` extreme filters.
    """

    def __init__(self, n_components: int = 6, reg: float = 1e-2):
        self.n_components = n_components
        self.reg = reg

    @staticmethod
    def _mean_cov(X: np.ndarray) -> np.ndarray:
        covs = np.matmul(X, X.transpose(0, 2, 1))
        covs /= np.trace(covs, axis1=1, axis2=2)[:, None, None]
        return covs.mean(0)

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        c0, c1 = self._mean_cov(X[y == 0]), self._mean_cov(X[y == 1])
        n = c0.shape[0]
        reg_eye = self.reg * np.eye(n) / n
        c0, c1 = (1 - self.reg) * c0 + reg_eye, (1 - self.reg) * c1 + reg_eye
        vals, vecs = eigh(c0, c0 + c1)                      # ascending eigenvalues
        half = self.n_components // 2
        idx = np.r_[np.arange(half), np.arange(n - half, n)]
        self.filters_ = vecs[:, idx].T                       # (n_components, n_channels)
        return self

    def transform(self, X):
        Z = np.matmul(self.filters_[None], np.asarray(X, dtype=np.float64))
        var = Z.var(axis=-1)
        return np.log(var / var.sum(axis=1, keepdims=True))

    def fit_transform(self, X, y):
        return self.fit(X, y).transform(X)


class CSPLDA(BaseEstimator, ClassifierMixin):
    def __init__(self, n_components: int = 6, reg: float = 1e-2):
        self.n_components = n_components
        self.reg = reg

    def fit(self, X, y):
        self.csp_ = CSP(self.n_components, self.reg).fit(X, y)
        self.lda_ = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
        self.lda_.fit(self.csp_.transform(X), y)
        self.classes_ = self.lda_.classes_
        return self

    def predict_proba(self, X):
        return self.lda_.predict_proba(self.csp_.transform(X))

    def predict(self, X):
        return self.lda_.predict(self.csp_.transform(X))


class BandPowerLogReg(BaseEstimator, ClassifierMixin):
    """Log band power (mu, beta) per channel + standardisation + L2 logistic regression."""

    def __init__(self, sfreq: float = 160.0, C: float = 0.1):
        self.sfreq = sfreq
        self.C = C

    def fit(self, X, y):
        F = log_bandpower(X, self.sfreq)
        self.pipe_ = make_pipeline(StandardScaler(), LogisticRegression(C=self.C, max_iter=2000))
        self.pipe_.fit(F, y)
        self.classes_ = self.pipe_.classes_
        return self

    def predict_proba(self, X):
        return self.pipe_.predict_proba(log_bandpower(X, self.sfreq))

    def predict(self, X):
        return self.pipe_.predict(log_bandpower(X, self.sfreq))
