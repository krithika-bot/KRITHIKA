"""Classical baselines under subject-wise cross-validation.

  python scripts/run_baselines.py --config configs/default.yaml --out results/classical
  python scripts/run_baselines.py --synthetic --out results_synthetic/classical      # pipeline test only
  python scripts/run_baselines.py --permute-train-labels ...                         # leakage canary (~50% expected)
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from eegfyp.baselines import BandPowerLogReg, CSPLDA  # noqa: E402
from eegfyp.data import get_dataset  # noqa: E402
from eegfyp.evaluate import fold_indices, make_pred_frame, make_subject_folds, save_predictions  # noqa: E402
from eegfyp.preprocess import normalize_trials  # noqa: E402
from eegfyp.utils import load_config, save_run_info, set_seed  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--out", default="results/classical")
    ap.add_argument("--synthetic", action="store_true", help="use planted-effect synthetic data (pipeline test)")
    ap.add_argument("--n-subjects", type=int, default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--permute-train-labels", action="store_true",
                    help="shuffle TRAINING labels: accuracy must fall to ~50%% (leakage canary)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    cfg = load_config(args.config)
    if args.n_subjects:
        cfg["data"]["n_subjects"] = args.n_subjects
        cfg["synthetic"]["n_subjects"] = args.n_subjects
    seeds = args.seeds if args.seeds else cfg["eval"]["seeds"]
    ds = get_dataset(cfg, synthetic=args.synthetic)
    logging.info("Dataset: %s", ds.summary())
    X = normalize_trials(ds.X)
    suffix = "_permuted" if args.permute_train_labels else ""

    models = {
        "csp_lda": lambda: CSPLDA(n_components=6),
        "bandpower_logreg": lambda: BandPowerLogReg(sfreq=ds.sfreq),
    }
    frames = []
    for seed in seeds:
        set_seed(seed)
        rng = np.random.default_rng(seed)
        folds = make_subject_folds(ds.subject, cfg["eval"]["n_folds"], seed)
        for k, test_subj in enumerate(folds):
            tr, te = fold_indices(ds.subject, test_subj)
            y_tr = ds.y[tr].copy()
            if args.permute_train_labels:
                rng.shuffle(y_tr)
            for name, make in models.items():
                t0 = time.time()
                clf = make().fit(X[tr], y_tr)
                prob = clf.predict_proba(X[te])[:, 1]
                pred = (prob >= 0.5).astype(int)
                frames.append(make_pred_frame(name + suffix, seed, k, te, ds.subject[te], ds.y[te], pred, prob))
                acc = float((pred == ds.y[te]).mean())
                logging.info("seed %d fold %d %-18s acc=%.3f (%.1fs)", seed, k, name + suffix, acc, time.time() - t0)

    preds = pd.concat(frames, ignore_index=True)
    out = Path(args.out)
    save_predictions(preds, out / f"preds{suffix}.csv")
    save_run_info(out, cfg, {"synthetic": args.synthetic, "seeds": seeds, "dataset": ds.summary(),
                             "permute_train_labels": args.permute_train_labels})
    logging.info("Saved %s", out / f"preds{suffix}.csv")


if __name__ == "__main__":
    main()
