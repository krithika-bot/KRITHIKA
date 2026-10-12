"""Evaluation protocol: SUBJECT-wise cross-validation, metrics, bootstrap CIs, paired tests.

Cross-subject protocol: in every fold the test subjects are completely unseen during training
(no trial of a test subject is used for fitting, normalisation statistics, graph estimation or
early stopping). This is the hard, clinically relevant setting and avoids the trial-level leakage
that inflates many published EEG numbers.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score


def make_subject_folds(subjects: np.ndarray, n_folds: int, seed: int) -> list[np.ndarray]:
    """Random partition of the unique subjects into `n_folds` disjoint test sets."""
    uniq = np.unique(subjects)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(uniq)
    return [np.sort(f) for f in np.array_split(perm, n_folds)]


def split_train_val_subjects(train_subjects: np.ndarray, frac: float, seed: int):
    uniq = np.unique(train_subjects)
    rng = np.random.default_rng(seed + 12345)
    perm = rng.permutation(uniq)
    n_val = max(1, int(round(frac * len(uniq))))
    return np.sort(perm[n_val:]), np.sort(perm[:n_val])


def fold_indices(subject: np.ndarray, test_subjects: np.ndarray):
    test_mask = np.isin(subject, test_subjects)
    tr, te = np.where(~test_mask)[0], np.where(test_mask)[0]
    assert not set(np.unique(subject[tr])) & set(np.unique(subject[te])), "subject leakage!"
    return tr, te


def trial_metrics(y_true, y_pred, y_prob) -> dict:
    out = {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
    }
    try:
        out["auc"] = roc_auc_score(y_true, y_prob)
    except ValueError:
        out["auc"] = float("nan")
    return out


def per_subject_accuracy(preds: pd.DataFrame) -> pd.Series:
    """Accuracy per subject (averaged over seeds)."""
    return (preds["y_true"] == preds["y_pred"]).groupby(preds["subject"]).mean()


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 0, alpha: float = 0.05):
    """Percentile bootstrap CI of the mean, resampling SUBJECTS."""
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[idx].mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def summarize(preds: pd.DataFrame, n_boot: int = 10000) -> pd.DataFrame:
    rows = []
    for method, g in preds.groupby("method", sort=False):
        per_seed = pd.DataFrame([
            trial_metrics(s["y_true"].values, s["y_pred"].values, s["y_prob"].values)
            for _, s in g.groupby("seed")
        ])
        subj = per_subject_accuracy(g)
        lo, hi = bootstrap_ci(subj.values, n_boot)
        rows.append({
            "method": method,
            "n_subjects": int(subj.shape[0]),
            "n_seeds": int(g["seed"].nunique()),
            "subject_acc": float(subj.mean()),
            "ci95_lo": lo,
            "ci95_hi": hi,
            "trial_acc": float(per_seed["accuracy"].mean()),
            "trial_acc_sd_over_seeds": float(per_seed["accuracy"].std(ddof=0)),
            "balanced_acc": float(per_seed["balanced_accuracy"].mean()),
            "f1_macro": float(per_seed["f1_macro"].mean()),
            "auc": float(per_seed["auc"].mean()),
        })
    return pd.DataFrame(rows)


def paired_wilcoxon(preds: pd.DataFrame, a: str, b: str) -> dict:
    """Paired Wilcoxon signed-rank test on per-subject accuracy of method `a` vs `b`."""
    sa = per_subject_accuracy(preds[preds["method"] == a])
    sb = per_subject_accuracy(preds[preds["method"] == b])
    common = sa.index.intersection(sb.index)
    diff = sa.loc[common].values - sb.loc[common].values
    try:
        p = float(stats.wilcoxon(diff).pvalue) if np.any(diff != 0) else 1.0
    except ValueError:
        p = 1.0
    lo, hi = bootstrap_ci(diff, 10000)
    return {"a": a, "b": b, "n_subjects": int(len(common)), "mean_diff": float(diff.mean()),
            "diff_ci95_lo": lo, "diff_ci95_hi": hi, "p_value": p}


def holm_correction(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def confusion(preds: pd.DataFrame) -> np.ndarray:
    cm = np.zeros((2, 2), dtype=int)
    for t, p in zip(preds["y_true"], preds["y_pred"]):
        cm[int(t), int(p)] += 1
    return cm


def make_pred_frame(method, seed, fold, trial_idx, subject, y_true, y_pred, y_prob) -> pd.DataFrame:
    return pd.DataFrame({
        "method": method, "seed": seed, "fold": fold, "trial": trial_idx, "subject": subject,
        "y_true": y_true, "y_pred": y_pred, "y_prob": y_prob,
    })


def save_predictions(df: pd.DataFrame, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
