"""Data-sanity and graph figures (needs the cached dataset).

  python scripts/make_data_figures.py --out results/figures
Produces: the ERD/lateralisation check (is the expected physiology in the data?) and drawings of the
electrode graphs. The corr graph here is estimated on ALL trials purely for illustration; the
experiments estimate it on training trials only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from eegfyp import plots  # noqa: E402
from eegfyp.data import get_dataset  # noqa: E402
from eegfyp.graphs import build_adjacency  # noqa: E402
from eegfyp.preprocess import normalize_trials  # noqa: E402
from eegfyp.utils import load_config  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--out", default="results/figures")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--n-subjects", type=int, default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.n_subjects:
        cfg["data"]["n_subjects"] = args.n_subjects
        cfg["synthetic"]["n_subjects"] = args.n_subjects
    ds = get_dataset(cfg, synthetic=args.synthetic)
    banner = "SYNTHETIC DATA - PIPELINE TEST" if args.synthetic else None
    out = Path(args.out)
    res = plots.plot_erd_sanity(ds, out / "erd_sanity.png", banner)
    (out / "erd_sanity.json").write_text(json.dumps(res, indent=2))
    print("ERD sanity:", res)
    g = cfg["graph"]
    X = normalize_trials(ds.X)
    for kind in ["distance", "random", "uniform", "corr"]:
        A = build_adjacency(kind, ds.pos, X, k=g["k_neighbors"], sigma=g["sigma"], seed=0)
        plots.plot_electrode_graph(ds.pos, A, ds.ch_names, out / f"graph_{kind}.png", f"{kind} graph", banner)
    print("Figures written to", out)


if __name__ == "__main__":
    main()
