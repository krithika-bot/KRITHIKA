"""Reproducible EEG analysis pipeline using the public PhysioNet EEGBCI dataset.

This script is intentionally conservative: it downloads a small subset, performs
basic preprocessing, extracts band-power features, and trains a baseline model.
It does not claim clinical validity.
"""

from pathlib import Path

import mne
import numpy as np
from mne.datasets import eegbci
from mne.io import concatenate_raws, read_raw_edf
from mne.time_frequency import psd_array_welch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

DATA_DIR = Path("data")
SUBJECTS = [1, 2, 3, 4, 5]
RUNS = [3, 7, 11]  # left-vs-right fist motor-execution runs


def load_subject(subject: int):
    files = eegbci.load_data(subjects=subject, runs=RUNS, path=str(DATA_DIR))
    raws = [read_raw_edf(f, preload=True, verbose=False) for f in files]
    for raw in raws:
        eegbci.standardize(raw)
        raw.set_montage("standard_1005", on_missing="ignore", verbose=False)
    return concatenate_raws(raws)


def extract_bandpower(epochs, bands):
    sfreq = epochs.info["sfreq"]
    data = epochs.get_data(copy=True)
    n_epochs, n_channels, n_times = data.shape
    features = []
    for epoch in data:
        psd, freqs = psd_array_welch(
            epoch, sfreq=sfreq, fmin=4, fmax=30, n_fft=min(256, n_times), verbose=False
        )
        row = []
        for low, high in bands.values():
            mask = (freqs >= low) & (freqs < high)
            row.append(np.log(psd[:, mask].mean(axis=1) + 1e-12).mean())
        features.append(row)
    return np.asarray(features)


def main():
    all_X, all_y, all_groups = [], [], []
    bands = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}

    for subject in SUBJECTS:
        raw = load_subject(subject)
        raw.filter(1.0, 40.0, verbose=False)
        events, event_id = mne.events_from_annotations(raw, verbose=False)

        # For these runs, T1/T2 mark left/right fist movement onset.
        selected = {k: v for k, v in event_id.items() if k in {"T1", "T2"}}
        if not selected:
            continue
        epochs = mne.Epochs(
            raw,
            events,
            event_id=selected,
            tmin=0.0,
            tmax=2.0,
            baseline=None,
            preload=True,
            reject_by_annotation=True,
            verbose=False,
        )
        X = extract_bandpower(epochs, bands)
        y = epochs.events[:, -1]
        all_X.append(X)
        all_y.append(y)
        all_groups.extend([subject] * len(y))

    X = np.vstack(all_X)
    y = np.concatenate(all_y)
    groups = np.asarray(all_groups)

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, random_state=42),
    )
    model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx])

    print(f"Samples: {len(y)}")
    print(f"Train subjects: {sorted(set(groups[train_idx]))}")
    print(f"Test subjects: {sorted(set(groups[test_idx]))}")
    print(f"Accuracy: {accuracy_score(y[test_idx], pred):.3f}")
    print(classification_report(y[test_idx], pred, zero_division=0))


if __name__ == "__main__":
    main()
