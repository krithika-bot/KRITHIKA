"""Leakage-aware subject-wise evaluation and aggregate-only reporting."""
from __future__ import annotations

from pathlib import Path
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

from .models import log_bandpower, make_models, normalized_trial_covariances

LOG = logging.getLogger(__name__)


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
    }


def _bootstrap_mean_ci(values: np.ndarray, *, seed: int, n_boot: int = 10_000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=np.float64)
    draws = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[draws].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def evaluate(dataset, out_dir: Path, *, seeds=(0, 1, 2), n_folds: int = 5) -> dict:
    """Evaluate baselines using repeated, disjoint participant-level test folds.

    The participant IDs are used only in memory for grouping and bootstrap uncertainty.
    Saved CSVs contain fold-level and cohort-level aggregates, never trial predictions or
    participant-level scores.
    """
    X, y, subjects = dataset.X, dataset.y, dataset.subject
    unique_subjects = np.unique(subjects)
    if len(unique_subjects) < n_folds:
        raise ValueError(f"Need at least {n_folds} participants; found {len(unique_subjects)}")
    factories = make_models(dataset.sfreq)

    LOG.info("Computing label-free per-trial features and covariances")
    bandpower_features = log_bandpower(X, dataset.sfreq)
    trial_covariances = normalized_trial_covariances(X)

    seed_outputs: dict[str, list[dict]] = {name: [] for name in factories}
    subject_scores: dict[str, dict[int, list[float]]] = {
        name: {int(s): [] for s in unique_subjects} for name in factories
    }
    fold_rows: list[dict] = []
    confusion_sums = {name: np.zeros((2, 2), dtype=np.int64) for name in factories}

    for seed in seeds:
        ordered_subjects = np.random.default_rng(seed).permutation(unique_subjects)
        folds = np.array_split(ordered_subjects, n_folds)
        test_coverage: list[int] = []
        per_seed_predictions: dict[str, dict[str, list[np.ndarray]]] = {
            name: {"true": [], "pred": [], "prob": []} for name in factories
        }
        for fold_index, test_subjects in enumerate(folds):
            train_mask = ~np.isin(subjects, test_subjects)
            test_mask = np.isin(subjects, test_subjects)
            if np.intersect1d(np.unique(subjects[train_mask]), np.unique(subjects[test_mask])).size:
                raise AssertionError("Participant leakage across train/test split")
            train_idx, test_idx = np.flatnonzero(train_mask), np.flatnonzero(test_mask)
            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]
            subject_test = subjects[test_idx]
            test_coverage.extend(int(s) for s in test_subjects)

            for method, factory in factories.items():
                model = factory()
                if method == "majority":
                    model_X_train = np.zeros((len(train_idx), 1), dtype=np.float32)
                    model_X_test = np.zeros((len(test_idx), 1), dtype=np.float32)
                    model.fit(model_X_train, y_train)
                    prediction = model.predict(model_X_test)
                    probability = model.predict_proba(model_X_test)[:, 1]
                elif method == "bandpower_logreg":
                    model.fit(X_train, y_train, features=bandpower_features[train_idx])
                    prediction = model.predict(X_test, features=bandpower_features[test_idx])
                    probability = model.predict_proba(X_test, features=bandpower_features[test_idx])[:, 1]
                elif method == "csp_lda":
                    model.fit(X_train, y_train, covariances=trial_covariances[train_idx])
                    prediction = model.predict(X_test)
                    probability = model.predict_proba(X_test)[:, 1]
                else:
                    raise ValueError(f"Unsupported evaluation model: {method}")
                for subject in test_subjects:
                    subject_mask = subject_test == subject
                    subject_scores[method][int(subject)].append(
                        float(accuracy_score(y_test[subject_mask], prediction[subject_mask]))
                    )
                per_seed_predictions[method]["true"].append(y_test)
                per_seed_predictions[method]["pred"].append(prediction)
                per_seed_predictions[method]["prob"].append(probability)
                confusion_sums[method] += confusion_matrix(y_test, prediction, labels=[0, 1])
                fold_rows.append({
                    "seed": int(seed),
                    "fold": int(fold_index),
                    "method": method,
                    "n_test_subjects": int(len(test_subjects)),
                    "n_test_trials": int(len(y_test)),
                    **_metrics(y_test, prediction, probability),
                })
                LOG.info(
                    "seed %d fold %d %-18s accuracy=%.3f",
                    seed, fold_index, method, accuracy_score(y_test, prediction),
                )

        if len(test_coverage) != len(unique_subjects) or len(set(test_coverage)) != len(unique_subjects):
            raise AssertionError("Each participant must be tested exactly once per seed")
        for method in factories:
            true = np.concatenate(per_seed_predictions[method]["true"])
            pred = np.concatenate(per_seed_predictions[method]["pred"])
            prob = np.concatenate(per_seed_predictions[method]["prob"])
            seed_outputs[method].append(_metrics(true, pred, prob))

    summary_rows = []
    participant_means: dict[str, np.ndarray] = {}
    for method, runs in seed_outputs.items():
        values = np.array([
            np.mean(subject_scores[method][int(s)]) for s in unique_subjects
        ], dtype=np.float64)
        participant_means[method] = values
        ci_low, ci_high = _bootstrap_mean_ci(values, seed=20261014)
        metrics = pd.DataFrame(runs)
        summary_rows.append({
            "method": method,
            "n_subjects": int(len(unique_subjects)),
            "n_folds": int(n_folds),
            "n_seeds": int(len(seeds)),
            "n_test_trials_per_seed": int(len(y)),
            "mean_subject_accuracy": float(values.mean()),
            "subject_accuracy_ci95_low": ci_low,
            "subject_accuracy_ci95_high": ci_high,
            "mean_trial_accuracy": float(metrics["accuracy"].mean()),
            "trial_accuracy_sd_over_seeds": float(metrics["accuracy"].std(ddof=0)),
            "balanced_accuracy": float(metrics["balanced_accuracy"].mean()),
            "macro_f1": float(metrics["macro_f1"].mean()),
            "roc_auc": float(metrics["roc_auc"].mean()),
        })

    summary = pd.DataFrame(summary_rows)
    out_dir = Path(out_dir)
    figures_dir = out_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "summary.csv", index=False, float_format="%.6f")
    pd.DataFrame(fold_rows).to_csv(out_dir / "fold_metrics.csv", index=False, float_format="%.6f")

    confusion_rows = []
    for method, matrix in confusion_sums.items():
        normalizer = np.maximum(matrix.sum(axis=1, keepdims=True), 1)
        normalized = matrix / normalizer
        for true_label, label_name in enumerate(("left", "right")):
            confusion_rows.append({
                "method": method,
                "true_class": label_name,
                "predicted_left_count": int(matrix[true_label, 0]),
                "predicted_right_count": int(matrix[true_label, 1]),
                "predicted_left_fraction": float(normalized[true_label, 0]),
                "predicted_right_fraction": float(normalized[true_label, 1]),
            })
    pd.DataFrame(confusion_rows).to_csv(
        out_dir / "confusion_matrices.csv", index=False, float_format="%.6f"
    )

    comparison = {}
    if {"csp_lda", "bandpower_logreg"}.issubset(participant_means):
        differences = participant_means["csp_lda"] - participant_means["bandpower_logreg"]
        diff_low, diff_high = _bootstrap_mean_ci(differences, seed=20261015)
        try:
            p_value = float(stats.wilcoxon(differences).pvalue) if np.any(differences) else 1.0
        except ValueError:
            p_value = 1.0
        comparison = {
            "comparison": "csp_lda_minus_bandpower_logreg",
            "n_subjects": int(len(differences)),
            "mean_subject_accuracy_difference": float(differences.mean()),
            "difference_ci95_low": diff_low,
            "difference_ci95_high": diff_high,
            "wilcoxon_p_value_exploratory": p_value,
            "note": "Exploratory paired comparison; not a preregistered hypothesis test.",
        }
        pd.DataFrame([comparison]).to_csv(
            out_dir / "paired_comparison.csv", index=False, float_format="%.6f"
        )

    _plot_results(summary, confusion_sums, figures_dir)
    return {"summary": summary, "comparison": comparison, "fold_metrics": pd.DataFrame(fold_rows)}


def _plot_results(summary: pd.DataFrame, confusion_sums: dict, figures_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = summary["method"].tolist()
    means = summary["mean_subject_accuracy"].to_numpy()
    lows = summary["subject_accuracy_ci95_low"].to_numpy()
    highs = summary["subject_accuracy_ci95_high"].to_numpy()
    positions = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.5, 4.8), layout="constrained")
    ax.bar(positions, means, color=["#8c98a4", "#4b82a8", "#b84e5c"][:len(labels)], width=0.65)
    ax.errorbar(
        positions, means,
        yerr=np.vstack([means - lows, highs - means]),
        fmt="none", ecolor="#20252a", capsize=4, linewidth=1.2,
    )
    ax.axhline(0.5, linestyle="--", color="#6d747c", linewidth=1, label="50% reference")
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Mean participant accuracy (95% bootstrap CI)")
    ax.set_title("Cross-subject left/right motor-imagery decoding")
    ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(figures_dir / "performance.png", dpi=180)
    plt.close(fig)

    methods = [name for name in ("bandpower_logreg", "csp_lda") if name in confusion_sums]
    fig, axes = plt.subplots(1, len(methods), figsize=(4.8 * len(methods), 4.3), layout="constrained")
    if len(methods) == 1:
        axes = [axes]
    for ax, method in zip(axes, methods):
        matrix = confusion_sums[method].astype(float)
        matrix /= np.maximum(matrix.sum(axis=1, keepdims=True), 1)
        image = ax.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
        ax.set_xticks([0, 1], ["left", "right"])
        ax.set_yticks([0, 1], ["left", "right"])
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("True class")
        ax.set_title(method.replace("_", " "))
        for row in range(2):
            for col in range(2):
                ax.text(col, row, f"{matrix[row, col]:.1%}", ha="center", va="center",
                        color="white" if matrix[row, col] > 0.55 else "#20252a")
    fig.colorbar(image, ax=axes, shrink=0.8, label="Row-normalized fraction")
    fig.savefig(figures_dir / "confusion_matrices.png", dpi=180)
    plt.close(fig)
