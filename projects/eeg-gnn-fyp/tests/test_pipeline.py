"""Correctness tests that need only numpy/scipy/sklearn:  python tests/run_tests.py  (or pytest)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from eegfyp import graphs  # noqa: E402
from eegfyp.baselines import CSPLDA, BandPowerLogReg  # noqa: E402
from eegfyp.data import EEGDataset, make_synthetic  # noqa: E402
from eegfyp.evaluate import (bootstrap_ci, fold_indices, holm_correction, make_pred_frame,  # noqa: E402
                             make_subject_folds, paired_wilcoxon, split_train_val_subjects, summarize)
from eegfyp.preprocess import bandpass, normalize_trials  # noqa: E402


def _ds():
    return make_synthetic(n_subjects=10, trials_per_subject=20, n_channels=32, n_times=320, seed=1)


def test_synthetic_shapes_and_balance():
    ds = _ds()
    assert ds.X.shape == (200, 32, 320) and ds.X.dtype == np.float32
    assert np.bincount(ds.y).tolist() == [100, 100]
    assert "C3" in ds.ch_names and "C4" in ds.ch_names


def test_cache_roundtrip():
    ds = _ds()
    with tempfile.TemporaryDirectory() as d:
        ds.save(Path(d) / "x.npz")
        back = EEGDataset.load(Path(d) / "x.npz")
    assert np.array_equal(ds.X, back.X) and ds.ch_names == back.ch_names and back.sfreq == ds.sfreq


def test_subject_folds_are_disjoint_and_cover_everyone():
    ds = _ds()
    folds = make_subject_folds(ds.subject, 5, seed=0)
    allsub = np.concatenate(folds)
    assert sorted(allsub.tolist()) == sorted(np.unique(ds.subject).tolist())
    for f in folds:
        tr, te = fold_indices(ds.subject, f)
        assert not set(ds.subject[tr]) & set(ds.subject[te])
        tr_s, va_s = split_train_val_subjects(ds.subject[tr], 0.15, 0)
        assert not set(tr_s) & set(va_s) and not set(va_s) & set(f)


def test_normalize_trials_keeps_channel_power_ratios():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((4, 6, 200)).astype(np.float32)
    X[:, 0] *= 3.0                                  # channel 0 has 3x amplitude
    Z = normalize_trials(X)
    ratio = Z[:, 0].std(-1) / Z[:, 1].std(-1)
    assert np.allclose(ratio, X[:, 0].std(-1) / X[:, 1].std(-1), rtol=1e-3)
    assert np.allclose(np.sqrt((Z ** 2).mean((1, 2))), 1.0, atol=1e-3)


def test_graphs_are_valid():
    ds = _ds()
    n = ds.X.shape[1]
    X = normalize_trials(ds.X)
    for kind in ["identity", "uniform", "random", "distance", "corr", "plv"]:
        A = graphs.build_adjacency(kind, ds.pos, X[:40], k=4, seed=0)
        assert A.shape == (n, n) and np.allclose(A, A.T) and (A >= 0).all() and np.allclose(np.diag(A), 0)
        H = graphs.normalize_adjacency(A)
        assert np.isfinite(H).all() and np.allclose(H, H.T, atol=1e-6)
    d = graphs.build_adjacency("distance", ds.pos, None, k=4)
    r = graphs.build_adjacency("random", ds.pos, None, k=4, seed=3)
    assert (d > 0).sum() == (r > 0).sum()
    assert np.allclose(np.sort(d[d > 0]), np.sort(r[r > 0]))     # same weights, different wiring
    assert not np.array_equal(d > 0, r > 0)


def _cv_accuracy(ds, make, permute=False, seed=0):
    X = normalize_trials(ds.X)
    rng = np.random.default_rng(seed)
    correct = []
    for f in make_subject_folds(ds.subject, 5, seed):
        tr, te = fold_indices(ds.subject, f)
        y = ds.y[tr].copy()
        if permute:
            rng.shuffle(y)
        clf = make().fit(X[tr], y)
        correct.append(clf.predict(X[te]) == ds.y[te])
    return float(np.concatenate(correct).mean())


def test_csp_detects_planted_effect_across_subjects():
    ds = make_synthetic(n_subjects=20, trials_per_subject=40, n_channels=32, n_times=320, seed=0)
    assert _cv_accuracy(ds, lambda: CSPLDA(6)) > 0.58
    assert _cv_accuracy(ds, lambda: BandPowerLogReg(ds.sfreq)) > 0.58


def test_label_permutation_gives_chance_accuracy():
    """Leakage canary: with shuffled training labels nothing can be learned."""
    ds = make_synthetic(n_subjects=20, trials_per_subject=40, n_channels=32, n_times=320, seed=0)
    accs = [_cv_accuracy(ds, lambda: CSPLDA(6), permute=True, seed=s) for s in range(3)]
    assert 0.42 < float(np.mean(accs)) < 0.58, accs


def test_bootstrap_and_stats():
    v = np.random.default_rng(0).uniform(0.4, 0.8, 30)
    lo, hi = bootstrap_ci(v, 2000)
    assert lo < v.mean() < hi
    adj = holm_correction([0.01, 0.04, 0.03])
    assert np.allclose(adj, [0.03, 0.06, 0.06])
    rows = []
    for m, base in [("a", 0.7), ("b", 0.55)]:
        for s in range(15):
            y = np.tile([0, 1], 10)
            pred = y.copy()
            flip = np.random.default_rng(s).random(20) > base
            pred[flip] = 1 - pred[flip]
            rows.append(make_pred_frame(m, 0, 0, np.arange(20), np.full(20, s), y, pred, pred.astype(float)))
    preds = pd.concat(rows)
    res = paired_wilcoxon(preds, "a", "b")
    assert res["mean_diff"] > 0 and res["p_value"] < 0.05
    assert paired_wilcoxon(preds, "a", "a")["p_value"] == 1.0
    assert set(summarize(preds, 500)["method"]) == {"a", "b"}


def test_bandpass_removes_out_of_band_energy():
    t = np.arange(1600) / 160
    x = (np.sin(2 * np.pi * 2 * t) + np.sin(2 * np.pi * 10 * t))[None, None].astype(np.float32)
    y = bandpass(x, 160, 8, 30)
    spec = np.abs(np.fft.rfft(y[0, 0]))
    f = np.fft.rfftfreq(1600, 1 / 160)
    assert spec[np.argmin(abs(f - 2))] < 0.05 * spec[np.argmin(abs(f - 10))]
