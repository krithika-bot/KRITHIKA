#!/usr/bin/env python3
"""Run the full EEG Analysis project on checksum-verified PhysioNet EEGMMIDB data."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import platform
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

_MPL_CONFIG = PROJECT_ROOT / "data" / ".matplotlib"
_MPL_CONFIG.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CONFIG))

import mne
import numpy as np
import pandas as pd
import scipy
import sklearn

from eeg_analysis import __version__
from eeg_analysis.data import (
    EXCLUDED_SUBJECTS,
    HIGH_HZ,
    LOW_HZ,
    RUNS,
    audit_dataset_files,
    load_physionet,
)
from eeg_analysis.evaluation import evaluate

LOG = logging.getLogger("eeg_analysis")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=PROJECT_ROOT / "data" / "raw",
                        help="MNE data directory; raw EDFs are not copied into the repository.")
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "results" / "full_cohort",
                        help="Directory for aggregate metrics, figures, and provenance.")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--download-missing", action="store_true",
                        help="Allow MNE to download missing raw EEG files from PhysioNet.")
    return parser.parse_args()


def make_report(
    out_dir: Path,
    dataset_summary: dict,
    dataset_audit: dict,
    summary: pd.DataFrame,
    comparison: dict,
) -> None:
    display = summary.copy()
    numeric_cols = [
        "mean_subject_accuracy", "subject_accuracy_ci95_low", "subject_accuracy_ci95_high",
        "mean_trial_accuracy", "balanced_accuracy", "macro_f1", "roc_auc",
    ]
    for column in numeric_cols:
        display[column] = display[column].map(lambda value: f"{value:.3f}")
    display = display.rename(columns={
        "method": "Method",
        "n_subjects": "Participants",
        "n_folds": "Folds",
        "n_seeds": "Seeds",
        "mean_subject_accuracy": "Mean participant accuracy",
        "subject_accuracy_ci95_low": "95% CI low",
        "subject_accuracy_ci95_high": "95% CI high",
        "mean_trial_accuracy": "Mean trial accuracy",
        "balanced_accuracy": "Balanced accuracy",
        "macro_f1": "Macro F1",
        "roc_auc": "ROC AUC",
    })
    table_frame = display[[
        "Method", "Participants", "Folds", "Seeds", "Mean participant accuracy",
        "95% CI low", "95% CI high", "Mean trial accuracy", "Balanced accuracy", "Macro F1", "ROC AUC",
    ]]
    headers = list(table_frame.columns)
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join("---" for _ in headers) + " |\n"
    for values in table_frame.itertuples(index=False, name=None):
        table += "| " + " | ".join(str(value) for value in values) + " |\n"
    comparison_text = "Paired comparison was not computed."
    if comparison:
        difference = comparison["mean_subject_accuracy_difference"]
        low, high = comparison["difference_ci95_low"], comparison["difference_ci95_high"]
        comparison_text = (
            f"CSP-LDA minus band-power logistic regression mean participant-accuracy difference: "
            f"{difference:.3f} (participant-bootstrap 95% CI {low:.3f} to {high:.3f}); "
            f"exploratory paired Wilcoxon p={comparison['wilcoxon_p_value_exploratory']:.4g}. "
            "This comparison is exploratory and was not preregistered."
        )
    text = f"""# EEG Analysis using AI/ML — Full-cohort results

**Status:** completed reproducible software analysis; research results are exploratory and non-clinical.
**Run date:** {datetime.now(timezone.utc).date().isoformat()} (UTC).

## Research question

How do two classical feature-based baselines compare with a majority-class reference for left-versus-right hand motor-imagery classification when test participants are unseen during training?

## Dataset and scope

The analysis uses {dataset_summary['n_subjects']} participants from the PhysioNet EEG Motor Movement/Imagery Database v1.0.0, runs 4, 8, and 12, 64 EEG channels, and {dataset_summary['n_trials']} task epochs sampled at {dataset_summary['sampling_rate_hz']:.0f} Hz. Runs 4, 8, and 12 contain left-versus-right hand motor imagery. T1 is mapped to left imagery and T2 to right imagery. Five participants were not included in the preselected 104-person cohort; the analysis does not infer why. All {dataset_audit['n_edf_files_verified']} EDF files used in this run were SHA-256 checked against the installed MNE-Python EEGBCI registry (zero mismatches). The raw recordings and per-file manifest are not redistributed here.

Dataset citation: Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset (version 1.0.0).* PhysioNet. https://doi.org/10.13026/C28G6P. The dataset is distributed under the Open Data Commons Attribution License v1.0. The original BCI2000 paper should also be cited when reusing the dataset.

## Methods

Raw EDF files were read with MNE-Python, standardized to common channel names, band-pass filtered from {LOW_HZ:.0f} to {HIGH_HZ:.0f} Hz, and epoched from cue onset through 3.99375 seconds (640 samples). Epochs annotated as bad by MNE were excluded. Each trial was demeaned per channel and scaled by its whole-trial RMS, without using labels or other trials.

Three methods were evaluated: a majority-class DummyClassifier; Welch mu (8–13 Hz) and beta (13–30 Hz) log-power features for each channel followed by standardization and L2 logistic regression; and shrinkage-regularized Common Spatial Patterns followed by shrinkage Linear Discriminant Analysis. Hyperparameters were fixed before the evaluation and were not tuned on test participants.

The test split unit was the participant. For each of three random seeds, all participants were partitioned into five disjoint folds. Each participant was tested exactly once per seed and never appeared in that seed's training data. Primary uncertainty is a 95% percentile bootstrap confidence interval over participant-level accuracies (10,000 resamples). The reported trial metrics average across seeds. No trial-level random split was used.

## Results

{table}

{comparison_text}

The 50% line in the performance plot is a reference for a balanced two-class task, not a guarantee of chance-level performance for every metric. Results describe this dataset and pipeline only; they do not establish performance on a new population, equipment, or clinical task.

![Subject-wise performance](figures/performance.png)

![Confusion matrices](figures/confusion_matrices.png)

## Limitations

- The cohort is the available verified subset (104 of 109 dataset participants); five participant recordings were not present in the local verified cache used for this run.
- The two-class task uses motor-imagery runs only and does not compare motor execution with imagery.
- This is a classical baseline study, not a state-of-the-art decoder; model settings were fixed rather than nested-tuned.
- MNE annotation rejection does not remove every ocular, muscle, or movement artifact. The supplied recordings have no dedicated artifact-removal step in this analysis.
- Multiple runs from a participant are combined; the study estimates generalization to new participants, not to new sessions from known participants.
- The bootstrap interval summarizes participant variability for this cohort and does not account for all uncertainty in dataset selection or preprocessing.
- No diagnosis, treatment, or clinical performance claim is made.

## Reproduction

From this project directory, install `requirements.txt`, then run:

```bash
python scripts/run_analysis.py --data-root data/raw --out results/full_cohort --download-missing
```

When network access is unavailable, provide the existing MNE cache directory and omit `--download-missing`. The saved `run_info.json` records the versions and settings; aggregate result files intentionally omit participant-level prediction rows.
"""
    (out_dir / "analysis_report.md").write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.out.mkdir(parents=True, exist_ok=True)
    LOG.info("Loading PhysioNet EEGMMIDB from %s", args.data_root)
    dataset = load_physionet(args.data_root, allow_download=args.download_missing)
    LOG.info("Dataset: %s", dataset.summary())
    dataset_audit = audit_dataset_files(args.data_root, dataset.subject)
    LOG.info(
        "Verified %d EDF checksums against the MNE registry",
        dataset_audit["n_edf_files_verified"],
    )
    outputs = evaluate(dataset, args.out, seeds=args.seeds, n_folds=args.folds)

    versions = {
        "python": platform.python_version(),
        "mne": mne.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
    }
    run_info = {
        "project_version": __version__,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "PhysioNet EEG Motor Movement/Imagery Database (EEGMMIDB) v1.0.0",
        "dataset_doi": "10.13026/C28G6P",
        "dataset_license": "Open Data Commons Attribution License v1.0",
        "data_source": "https://physionet.org/content/eegmmidb/1.0.0/",
        "raw_edf_committed": False,
        "participant_level_predictions_committed": False,
        "selection": {
            "runs": list(RUNS),
            "run_task": "left-versus-right hand motor imagery",
            "class_mapping": {"T1": "left", "T2": "right"},
            "participants_used": dataset.summary()["n_subjects"],
            "participants_omitted_from_cached_cohort": len(EXCLUDED_SUBJECTS),
            "omission_note": "Five participants were not in the local checksum-verified cache; this run does not infer the reason.",
            "channels": dataset.summary()["n_channels"],
            "sampling_rate_hz": dataset.sfreq,
            "filter_hz": [LOW_HZ, HIGH_HZ],
            "epoch_window_seconds": [0.0, 3.99375],
            "artifact_policy": "Reject MNE bad annotations; no additional automated artifact rejection.",
        },
        "evaluation": {
            "split_unit": "participant",
            "folds_per_seed": args.folds,
            "seeds": args.seeds,
            "preprocessing_fit_on_test_data": False,
            "participant_leakage_check": "asserted disjoint train and test subject groups per fold",
            "confidence_interval": "percentile bootstrap over participant accuracies, 10,000 resamples",
        },
        "models": ["majority", "bandpower_logreg", "csp_lda"],
        "dataset_summary": dataset.summary(),
        "dataset_integrity": dataset_audit,
        "software_versions": versions,
        "aggregate_outputs_only": True,
        "exploratory_comparison": outputs["comparison"],
    }
    (args.out / "run_info.json").write_text(
        json.dumps(run_info, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    provenance_dir = args.out / "provenance"
    provenance_dir.mkdir(parents=True, exist_ok=True)
    (provenance_dir / "dataset_audit.json").write_text(
        json.dumps(dataset_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    make_report(
        args.out, dataset.summary(), dataset_audit, outputs["summary"], outputs["comparison"]
    )
    LOG.info("Wrote aggregate report and results under %s", args.out)


if __name__ == "__main__":
    main()
