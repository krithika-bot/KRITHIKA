"""Label-free preprocessing helpers (nothing here looks at labels or other trials)."""
from __future__ import annotations

import numpy as np
from scipy import signal


def normalize_trials(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Remove each channel's DC offset, then divide the whole trial by its global RMS.

    A per-channel z-score would erase exactly the quantity motor imagery changes (band power
    in some channels relative to others), so we only rescale the trial as a whole. This keeps
    inter-channel power ratios (e.g. C3 vs C4), is label-free and uses no other trials.
    """
    X = X - X.mean(axis=-1, keepdims=True)
    rms = np.sqrt((X ** 2).mean(axis=(-2, -1), keepdims=True))
    return (X / (rms + eps)).astype(np.float32)


def bandpass(X: np.ndarray, sfreq: float, low: float, high: float, order: int = 4) -> np.ndarray:
    sos = signal.butter(order, [low, high], btype="bandpass", fs=sfreq, output="sos")
    return signal.sosfiltfilt(sos, X, axis=-1).astype(np.float32)


def log_bandpower(X: np.ndarray, sfreq: float, bands=((8, 13), (13, 30))) -> np.ndarray:
    """Welch log band power per channel -> (n_trials, n_channels * n_bands)."""
    nper = min(256, X.shape[-1])
    f, pxx = signal.welch(X, fs=sfreq, nperseg=nper, axis=-1)
    feats = []
    for lo, hi in bands:
        m = (f >= lo) & (f < hi)
        feats.append(np.log(pxx[..., m].mean(axis=-1) + 1e-12))
    return np.concatenate(feats, axis=1)
