"""Load and prepare the PhysioNet EEGMMIDB motor-imagery cohort."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from importlib.resources import files
from pathlib import Path
import logging

import numpy as np

LOG = logging.getLogger(__name__)

RUNS = (4, 8, 12)  # left-vs-right fist motor imagery
EXCLUDED_SUBJECTS = (88, 89, 92, 100, 104)
SUBJECTS = tuple(s for s in range(1, 110) if s not in EXCLUDED_SUBJECTS)
SFREQ = 160.0
LOW_HZ = 8.0
HIGH_HZ = 30.0
N_SAMPLES = 640
TMIN = 0.0
TMAX = (N_SAMPLES - 1) / SFREQ


@dataclass
class EEGDataset:
    X: np.ndarray  # trials x channels x samples, float32, per-trial normalized
    y: np.ndarray  # 0 = left-hand imagery (T1); 1 = right-hand imagery (T2)
    subject: np.ndarray
    ch_names: list[str]
    sfreq: float
    skipped: list[dict]

    def summary(self) -> dict:
        unique, counts = np.unique(self.y, return_counts=True)
        return {
            "n_trials": int(len(self.y)),
            "n_subjects": int(np.unique(self.subject).size),
            "n_channels": int(self.X.shape[1]),
            "n_samples_per_trial": int(self.X.shape[2]),
            "sampling_rate_hz": float(self.sfreq),
            "class_counts_left_right": {
                str(int(label)): int(count) for label, count in zip(unique, counts)
            },
            # Keep the saved summary aggregate-only; omission details can contain IDs.
            "n_subjects_skipped": int(len(self.skipped)),
        }


def _normalize_trials(X: np.ndarray) -> np.ndarray:
    """Remove each trial's channel DC offsets and scale by its global RMS."""
    X = X - X.mean(axis=-1, keepdims=True)
    rms = np.sqrt(np.mean(np.square(X), axis=(1, 2), keepdims=True))
    return (X / np.maximum(rms, 1e-8)).astype(np.float32, copy=False)


def audit_dataset_files(data_root: Path, subjects: np.ndarray) -> dict:
    """Verify selected EDF checksums against MNE's packaged EEGBCI checksum registry.

    The returned audit is aggregate-only: no participant IDs, EDF names, or per-file
    hashes are emitted.
    """
    data_root = Path(data_root).expanduser().resolve()
    dataset_dir = data_root / "MNE-eegbci-data" / "files" / "eegmmidb" / "1.0.0"
    registry_path = files("mne").joinpath("data", "eegbci_checksums.txt")
    registry: dict[str, str] = {}
    with registry_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            fields = line.split()
            if len(fields) >= 2:
                registry[fields[0]] = fields[1]

    aggregate = hashlib.sha256()
    n_files = 0
    total_bytes = 0
    problems = []
    for subject in sorted(int(s) for s in np.unique(subjects)):
        for run in RUNS:
            relative = f"S{subject:03d}/S{subject:03d}R{run:02d}.edf"
            path = dataset_dir / relative
            if not path.is_file():
                problems.append("missing")
                continue
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            expected = registry.get(relative)
            if expected is None:
                problems.append("not_in_mne_registry")
            elif actual != expected:
                problems.append("checksum_mismatch")
            aggregate.update(relative.encode("utf-8"))
            aggregate.update(b"\0")
            aggregate.update(actual.encode("ascii"))
            aggregate.update(b"\n")
            n_files += 1
            total_bytes += path.stat().st_size
    if problems:
        raise RuntimeError(
            "Dataset checksum audit failed: " + ", ".join(problems[:10])
        )
    return {
        "n_edf_files_verified": n_files,
        "n_subjects": int(np.unique(subjects).size),
        "runs_per_subject": list(RUNS),
        "total_file_bytes": int(total_bytes),
        "sha256_verified_against": "MNE-Python eegbci_checksums.txt registry",
        "aggregate_file_fingerprint_sha256": aggregate.hexdigest(),
        "checksum_mismatches": 0,
        "missing_files": 0,
        "per_file_manifest_published": False,
    }


def load_physionet(data_root: Path, *, allow_download: bool = False) -> EEGDataset:
    """Load eligible cached recordings; optionally let MNE fetch missing recordings.

    Raw EDF files are kept outside the repository. The default offline behavior avoids
    unexpected network calls and uses all eligible, locally cached subjects. Pass
    ``allow_download=True`` to fetch missing EEGMMIDB files from PhysioNet via MNE.
    """
    import mne
    from mne.datasets import eegbci
    from mne.io import concatenate_raws, read_raw_edf

    mne.set_log_level("ERROR")
    data_root = Path(data_root).expanduser().resolve()
    dataset_dir = data_root / "MNE-eegbci-data" / "files" / "eegmmidb" / "1.0.0"
    X_all: list[np.ndarray] = []
    y_all: list[np.ndarray] = []
    subject_all: list[np.ndarray] = []
    skipped: list[dict] = []
    ch_names: list[str] | None = None

    for subject in SUBJECTS:
        expected = [dataset_dir / f"S{subject:03d}" / f"S{subject:03d}R{run:02d}.edf" for run in RUNS]
        if not allow_download and not all(p.is_file() for p in expected):
            skipped.append({"subject": subject, "reason": "required run file is not in the local cache"})
            continue
        try:
            paths = eegbci.load_data(
                subject, RUNS, path=str(data_root), update_path=False, verbose="ERROR"
            )
            raws = []
            for path in paths:
                raw = read_raw_edf(path, preload=True, verbose="ERROR")
                eegbci.standardize(raw)
                raw.filter(LOW_HZ, HIGH_HZ, fir_design="firwin", verbose="ERROR")
                raws.append(raw)
            raw = concatenate_raws(raws, verbose="ERROR")
            if not np.isclose(raw.info["sfreq"], SFREQ):
                raise ValueError(f"expected {SFREQ:g} Hz, got {raw.info['sfreq']:g} Hz")
            raw.set_montage(
                mne.channels.make_standard_montage("standard_1005"),
                on_missing="ignore",
                verbose="ERROR",
            )
            events, _ = mne.events_from_annotations(
                raw, event_id={"T1": 1, "T2": 2}, verbose="ERROR"
            )
            epochs = mne.Epochs(
                raw,
                events,
                event_id={"left": 1, "right": 2},
                tmin=TMIN,
                tmax=TMAX,
                baseline=None,
                preload=True,
                picks="eeg",
                reject_by_annotation=True,
                verbose="ERROR",
            )
            Xi = epochs.get_data(copy=True) * 1e6  # MNE volts -> microvolts
            yi = (epochs.events[:, 2] == 2).astype(np.int64)
            if Xi.shape[1] != 64 or Xi.shape[2] != N_SAMPLES:
                raise ValueError(f"unexpected epoch array shape {Xi.shape}")
            if len(yi) < 30 or set(np.unique(yi)) != {0, 1}:
                raise ValueError(f"insufficient or single-class task epochs: {len(yi)}")
            if ch_names is None:
                ch_names = list(epochs.ch_names)
            elif ch_names != list(epochs.ch_names):
                raise ValueError("EEG channel order changed between participants")
            X_all.append(_normalize_trials(Xi))
            y_all.append(yi)
            subject_all.append(np.full(len(yi), subject, dtype=np.int16))
            LOG.info("Loaded subject %03d: %d trials", subject, len(yi))
        except Exception as exc:  # record omissions with a reason; never silently skip
            skipped.append({"subject": subject, "reason": f"{type(exc).__name__}: {exc}"})
            LOG.warning("Skipping subject %03d: %s", subject, exc)

    if not X_all:
        raise RuntimeError(
            f"No eligible EEGMMIDB subjects found under {data_root}. "
            "Check --data-root or rerun with --download-missing and network access."
        )
    return EEGDataset(
        X=np.concatenate(X_all),
        y=np.concatenate(y_all),
        subject=np.concatenate(subject_all),
        ch_names=ch_names or [],
        sfreq=SFREQ,
        skipped=skipped,
    )
