"""Data loading.

Real data  : PhysioNet EEG Motor Movement/Imagery Dataset (EEGMMIDB), left- vs right-fist
             MOTOR IMAGERY, runs 4/8/12 (annotation T1 = left fist, T2 = right fist).
Synthetic  : a planted-effect generator used ONLY to test that the pipeline is correct
             (no leakage, shapes, metrics). Synthetic numbers are never results.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)


@dataclass
class EEGDataset:
    X: np.ndarray            # (n_trials, n_channels, n_times) float32, microvolts
    y: np.ndarray            # (n_trials,) int64; 0 = left, 1 = right
    subject: np.ndarray      # (n_trials,) int64 subject id
    ch_names: list
    pos: np.ndarray          # (n_channels, 3) electrode positions
    sfreq: float
    meta: dict = field(default_factory=dict)

    def save(self, path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path, X=self.X, y=self.y, subject=self.subject, pos=self.pos,
            ch_names=np.array(self.ch_names), sfreq=self.sfreq, meta=json.dumps(self.meta, default=str),
        )

    @staticmethod
    def load(path) -> "EEGDataset":
        d = np.load(path, allow_pickle=False)
        return EEGDataset(
            X=d["X"], y=d["y"], subject=d["subject"], ch_names=[str(c) for c in d["ch_names"]],
            pos=d["pos"], sfreq=float(d["sfreq"]), meta=json.loads(str(d["meta"])),
        )

    @property
    def n_trials(self) -> int:
        return int(self.X.shape[0])

    def summary(self) -> str:
        subs = np.unique(self.subject)
        return (f"{self.n_trials} trials | {len(subs)} subjects | {self.X.shape[1]} channels | "
                f"{self.X.shape[2]} samples @ {self.sfreq:g} Hz | class balance {np.bincount(self.y).tolist()}")


# --------------------------------------------------------------------------- real data
def load_physionet_mi(cfg: dict) -> EEGDataset:
    """Download (via MNE) and epoch left/right motor imagery. Requires `mne` and internet."""
    import mne
    from mne.datasets import eegbci

    mne.set_log_level("ERROR")
    d = cfg["data"]
    sfreq = float(d["sfreq"])
    n_times = int(round((d["tmax"] - d["tmin"]) * sfreq))
    excluded = set(d["exclude_subjects"])
    candidates = [s for s in range(1, 110) if s not in excluded][: d["n_subjects"]]

    X_all, y_all, s_all, skipped = [], [], [], []
    ch_names, pos = None, None
    for s in candidates:
        try:
            paths = eegbci.load_data(s, d["runs"], path=d["raw_dir"], update_path=False)
            raws = []
            for p in paths:
                r = mne.io.read_raw_edf(p, preload=True, verbose="ERROR")
                eegbci.standardize(r)                       # fix channel names ("Fc5." -> "FC5")
                r.filter(d["l_freq"], d["h_freq"], fir_design="firwin", verbose="ERROR")
                raws.append(r)
            raw = mne.concatenate_raws(raws)
            if abs(raw.info["sfreq"] - sfreq) > 1e-6:
                raise ValueError(f"unexpected sampling rate {raw.info['sfreq']}")
            raw.set_montage(mne.channels.make_standard_montage("standard_1005"))
            events, _ = mne.events_from_annotations(raw, event_id=dict(T1=2, T2=3), verbose="ERROR")
            epochs = mne.Epochs(
                raw, events, event_id=dict(left=2, right=3), tmin=d["tmin"],
                tmax=d["tmin"] + (n_times - 1) / sfreq, baseline=None, preload=True,
                picks="eeg", verbose="ERROR",
            )
            Xs = epochs.get_data() * 1e6                    # V -> uV
            ys = (epochs.events[:, 2] == 3).astype(np.int64)
            if Xs.shape[2] != n_times or len(ys) < d["min_trials"]:
                raise ValueError(f"bad epochs: shape {Xs.shape}")
            if ch_names is None:
                ch_names = list(epochs.ch_names)
                pos = np.array([epochs.info["chs"][i]["loc"][:3] for i in range(len(ch_names))])
            elif list(epochs.ch_names) != ch_names:
                raise ValueError("channel order differs")
        except Exception as e:  # skip loudly, never silently
            log.warning("Skipping subject %d: %s", s, e)
            skipped.append((s, str(e)))
            continue
        X_all.append(Xs.astype(np.float32))
        y_all.append(ys)
        s_all.append(np.full(len(ys), s, dtype=np.int64))
        log.info("subject %d: %d trials", s, len(ys))

    if not X_all:
        raise RuntimeError("No subjects could be loaded. Check internet access / MNE installation.")
    meta = {"dataset": "physionet_eegmmidb", "runs": d["runs"], "skipped": skipped,
            "l_freq": d["l_freq"], "h_freq": d["h_freq"], "tmin": d["tmin"], "tmax": d["tmax"]}
    return EEGDataset(np.concatenate(X_all), np.concatenate(y_all), np.concatenate(s_all),
                      ch_names, pos, sfreq, meta)


def get_dataset(cfg: dict, synthetic: bool = False, force: bool = False) -> EEGDataset:
    if synthetic:
        return make_synthetic(**cfg.get("synthetic", {}))
    d = cfg["data"]
    key = (f"eegmmidb_runs{'-'.join(map(str, d['runs']))}_{d['l_freq']:g}-{d['h_freq']:g}Hz_"
           f"t{d['tmin']:g}-{d['tmax']:g}_n{d['n_subjects']}.npz")
    cache = Path(d["cache_dir"]) / key
    if cache.exists() and not force:
        log.info("Loading cached dataset %s", cache)
        return EEGDataset.load(cache)
    ds = load_physionet_mi(cfg)
    ds.save(cache)
    return ds


# --------------------------------------------------------------------------- synthetic data
def hemisphere_positions(n: int, radius: float = 0.09) -> np.ndarray:
    """Roughly uniform points on the upper hemisphere (x = left/right, y = front/back, z = up)."""
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - i / n)                       # polar angle in (0, pi/2)
    theta = np.pi * (1 + 5 ** 0.5) * i               # golden-angle spiral
    xyz = np.stack([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)], axis=1)
    return radius * xyz


def make_synthetic(n_subjects=20, trials_per_subject=40, n_channels=64, n_times=640,
                   sfreq=160.0, seed=0) -> EEGDataset:
    """EEG-like data with a PLANTED effect: imagining the left hand suppresses mu/beta power over the
    right motor area and vice versa (event-related desynchronisation), plus 1/f noise, subject gain
    differences and volume-conduction-like spatial mixing. For pipeline testing only."""
    rng = np.random.default_rng(seed)
    pos = hemisphere_positions(n_channels)
    unit = pos / np.linalg.norm(pos, axis=1, keepdims=True)
    dir_left = np.array([-0.6, 0.0, 0.8]); dir_left /= np.linalg.norm(dir_left)
    dir_right = np.array([0.6, 0.0, 0.8]); dir_right /= np.linalg.norm(dir_right)
    ang_l = np.arccos(np.clip(unit @ dir_left, -1, 1))
    ang_r = np.arccos(np.clip(unit @ dir_right, -1, 1))
    w_left = np.exp(-(ang_l ** 2) / (2 * 0.35 ** 2))   # "C3-like" region (left hemisphere)
    w_right = np.exp(-(ang_r ** 2) / (2 * 0.35 ** 2))  # "C4-like" region (right hemisphere)

    d = np.linalg.norm(pos[:, None] - pos[None], axis=-1)
    mix = np.exp(-(d ** 2) / (2 * 0.03 ** 2))
    mix /= mix.sum(1, keepdims=True)

    ch_names = [f"E{i:02d}" for i in range(n_channels)]
    ch_names[int(np.argmax(w_left))] = "C3"
    ch_names[int(np.argmax(w_right))] = "C4"

    t = np.arange(n_times) / sfreq
    freqs = np.fft.rfftfreq(n_times, 1 / sfreq)
    shape = 1.0 / np.sqrt(freqs + 1.0)

    X, y, subj = [], [], []
    for s in range(1, n_subjects + 1):
        gain = rng.lognormal(0, 0.3)
        erd = rng.uniform(0.25, 0.55)
        f_mu, f_beta = rng.uniform(9, 12), rng.uniform(18, 24)
        labels = np.tile([0, 1], trials_per_subject // 2)
        rng.shuffle(labels)
        for lab in labels:
            noise = rng.standard_normal((n_channels, n_times))
            spec = np.fft.rfft(noise, axis=1) * shape
            noise = np.fft.irfft(spec, n=n_times, axis=1)
            noise *= 3.0 / noise.std()
            suppress = w_right if lab == 0 else w_left          # contralateral ERD
            a_mu = 2.5 * (1 - erd * suppress) * rng.uniform(0.8, 1.2)
            a_beta = 1.5 * (1 - 0.5 * erd * suppress) * rng.uniform(0.8, 1.2)
            ph1 = rng.uniform(0, 2 * np.pi, (n_channels, 1))
            ph2 = rng.uniform(0, 2 * np.pi, (n_channels, 1))
            osc = a_mu[:, None] * np.sin(2 * np.pi * f_mu * t + ph1) + \
                a_beta[:, None] * np.sin(2 * np.pi * f_beta * t + ph2)
            X.append((gain * (mix @ (noise + osc))).astype(np.float32))
            y.append(lab)
            subj.append(s)
    meta = {"dataset": "SYNTHETIC (pipeline test only)", "seed": seed}
    return EEGDataset(np.stack(X), np.array(y, dtype=np.int64), np.array(subj, dtype=np.int64),
                      ch_names, pos, float(sfreq), meta)
