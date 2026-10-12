"""Deep models (EEGNet and graph networks) under subject-wise cross-validation.

  python scripts/run_deep.py --smoke --synthetic        # 1-2 minute wiring check (NOT a result)
  python scripts/run_deep.py --out results/deep         # full experiment (use a GPU, e.g. Colab T4)
  python scripts/run_deep.py --models eegnet gcn --graphs identity distance --seeds 0

Results are appended after every (method, seed, fold); re-run with --resume after a disconnect.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from eegfyp.data import get_dataset  # noqa: E402
from eegfyp.evaluate import (fold_indices, make_pred_frame, make_subject_folds,  # noqa: E402
                             save_predictions, split_train_val_subjects)
from eegfyp.graphs import build_adjacency, normalize_adjacency  # noqa: E402
from eegfyp.preprocess import normalize_trials  # noqa: E402
from eegfyp.utils import load_config, save_run_info, set_seed  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--out", default="results/deep")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="tiny run: 1 seed, 1 fold, 2 epochs, 3 graphs")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--n-subjects", type=int, default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--models", nargs="*", default=["eegnet", "gcn"], choices=["eegnet", "gcn"])
    ap.add_argument("--graphs", nargs="*", default=None, help="adjacency kinds for the GCN")
    ap.add_argument("--epochs", type=int, default=None)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    import torch  # imported late so the other scripts work without torch
    from eegfyp.models import EEGGraphNet, EEGNet, count_params
    from eegfyp.train import fit_predict, get_device

    cfg = load_config(args.config)
    if args.n_subjects:
        cfg["data"]["n_subjects"] = args.n_subjects
        cfg["synthetic"]["n_subjects"] = args.n_subjects
    seeds = args.seeds if args.seeds else cfg["eval"]["seeds"]
    kinds = args.graphs if args.graphs else cfg["graph"]["kinds"]
    n_folds = cfg["eval"]["n_folds"]
    if args.epochs:
        cfg["train"]["epochs"] = args.epochs
    if args.smoke:
        seeds, kinds, cfg["train"]["epochs"] = seeds[:1], [k for k in kinds if k in ("identity", "distance", "corr")], 2
        cfg["synthetic"]["n_subjects"] = min(cfg["synthetic"]["n_subjects"], 12)

    device = get_device()
    logging.info("Device: %s", device)
    ds = get_dataset(cfg, synthetic=args.synthetic)
    logging.info("Dataset: %s", ds.summary())
    X = normalize_trials(ds.X)
    n_ch, n_t = X.shape[1], X.shape[2]
    g = cfg["graph"]

    methods = (["eegnet"] if "eegnet" in args.models else []) + \
              ([f"gcn_{k}" for k in kinds] if "gcn" in args.models else [])
    out = Path(args.out)
    pred_path, hist_path = out / "preds.csv", out / "histories.json"
    frames = [pd.read_csv(pred_path)] if args.resume and pred_path.exists() else []
    done = set()
    if frames:
        done = set(map(tuple, frames[0][["method", "seed", "fold"]].drop_duplicates().values.tolist()))
    histories = json.loads(hist_path.read_text()) if args.resume and hist_path.exists() else {}
    n_params = {}

    for seed in seeds:
        folds = make_subject_folds(ds.subject, n_folds, seed)
        for k, test_subj in enumerate(folds[:1] if args.smoke else folds):
            tr_all, te = fold_indices(ds.subject, test_subj)
            tr_subj, val_subj = split_train_val_subjects(ds.subject[tr_all], cfg["eval"]["val_subject_frac"], seed)
            tr = tr_all[np.isin(ds.subject[tr_all], tr_subj)]
            va = tr_all[np.isin(ds.subject[tr_all], val_subj)]
            for method in methods:
                if (method, seed, k) in done:
                    continue
                set_seed(seed * 1000 + k)
                if method == "eegnet":
                    model = EEGNet(n_ch, n_t, dropout=cfg["train"]["dropout"], **cfg["model"]["eegnet"])
                else:
                    kind = method.split("_", 1)[1]
                    A = build_adjacency(kind, ds.pos, X[tr], k=g["k_neighbors"], sigma=g["sigma"], seed=seed * 100 + k)
                    model = EEGGraphNet(n_ch, normalize_adjacency(A), dropout=cfg["train"]["dropout"],
                                        **cfg["model"]["gcn"])
                n_params[method] = count_params(model)
                t0 = time.time()
                prob, hist, best_epoch = fit_predict(
                    model, X[tr], ds.y[tr], X[va], ds.y[va], X[te], cfg["train"], device, seed * 1000 + k)
                pred = (prob >= 0.5).astype(int)
                frames.append(make_pred_frame(method, seed, k, te, ds.subject[te], ds.y[te], pred, prob))
                histories[f"{method}|{seed}|{k}"] = hist
                acc = float((pred == ds.y[te]).mean())
                logging.info("seed %d fold %d %-14s test_acc=%.3f best_epoch=%d params=%d (%.0fs)",
                             seed, k, method, acc, best_epoch, n_params[method], time.time() - t0)
                save_predictions(pd.concat(frames, ignore_index=True), pred_path)
                hist_path.write_text(json.dumps(histories))
                del model
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    save_run_info(out, cfg, {"synthetic": args.synthetic, "smoke": args.smoke, "seeds": seeds,
                             "methods": methods, "n_params": n_params, "dataset": ds.summary()})
    logging.info("Done. Results in %s", out)


if __name__ == "__main__":
    main()
