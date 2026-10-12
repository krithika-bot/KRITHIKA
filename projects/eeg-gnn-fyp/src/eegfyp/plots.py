"""Publication-style figures. Every function accepts `banner` to stamp synthetic/pipeline-test output."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import signal, stats  # noqa: E402

from .evaluate import confusion, per_subject_accuracy  # noqa: E402

plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 200, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def _finish(fig, path, banner=None):
    if banner:
        fig.text(0.5, 0.5, banner, fontsize=22, color="red", alpha=0.18, ha="center", va="center", rotation=25)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_method_comparison(summary: pd.DataFrame, path, banner=None, title="Cross-subject accuracy"):
    s = summary.iloc[::-1]
    fig, ax = plt.subplots(figsize=(6, 0.5 * len(s) + 1.4))
    err = np.vstack([s["subject_acc"] - s["ci95_lo"], s["ci95_hi"] - s["subject_acc"]])
    ax.barh(s["method"], s["subject_acc"], xerr=err, color="#4C72B0", capsize=3)
    ax.axvline(0.5, color="k", ls="--", lw=1, label="chance (0.5)")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_xlim(0.4, max(0.8, float(s["ci95_hi"].max()) + 0.05))
    ax.set_xlabel("mean per-subject accuracy (95% bootstrap CI over subjects)")
    ax.set_title(title)
    _finish(fig, path, banner)


def plot_per_subject_scatter(preds: pd.DataFrame, a: str, b: str, path, banner=None):
    sa = per_subject_accuracy(preds[preds["method"] == a])
    sb = per_subject_accuracy(preds[preds["method"] == b])
    common = sa.index.intersection(sb.index)
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.scatter(sb.loc[common], sa.loc[common], s=18, alpha=0.75)
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlim(0.2, 1.0); ax.set_ylim(0.2, 1.0)
    ax.set_xlabel(f"{b}  (per-subject accuracy)")
    ax.set_ylabel(f"{a}  (per-subject accuracy)")
    ax.set_title(f"{a} vs {b}: each dot is one held-out subject", fontsize=8)
    _finish(fig, path, banner)


def plot_confusions(preds: pd.DataFrame, methods: list[str], path, banner=None):
    fig, axes = plt.subplots(1, len(methods), figsize=(2.6 * len(methods), 2.8), squeeze=False)
    for ax, m in zip(axes[0], methods):
        cm = confusion(preds[preds["method"] == m]).astype(float)
        cmn = cm / cm.sum(1, keepdims=True)
        ax.imshow(cmn, vmin=0, vmax=1, cmap="Blues")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cmn[i, j]:.2f}\n(n={int(cm[i, j])})", ha="center", va="center", fontsize=7,
                        color="white" if cmn[i, j] > 0.6 else "black")
        ax.set_xticks([0, 1], ["left", "right"]); ax.set_yticks([0, 1], ["left", "right"])
        ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.set_title(m, fontsize=8)
    _finish(fig, path, banner)


def plot_learning_curves(hist_path, path, banner=None):
    hist = json.loads(Path(hist_path).read_text())
    firsts = {}
    for key, h in hist.items():
        method, seed, fold = key.split("|")
        if seed == min(k.split("|")[1] for k in hist) and fold == "0":
            firsts[method] = h
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
    for method, h in firsts.items():
        ep = [r["epoch"] for r in h]
        axes[0].plot(ep, [r["train_loss"] for r in h], label=method)
        axes[1].plot(ep, [r["val_acc"] for r in h], label=method)
    axes[0].set_title("training loss (first fold)"); axes[1].set_title("validation accuracy (validation subjects)")
    for a in axes:
        a.set_xlabel("epoch")
    axes[1].axhline(0.5, color="k", ls="--", lw=1)
    axes[1].legend(fontsize=6, ncol=2)
    _finish(fig, path, banner)


def plot_electrode_graph(pos, A, ch_names, path, title="", banner=None, label=("C3", "C4", "Cz", "Fz", "Pz")):
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    n = len(pos)
    wmax = A.max() if A.max() > 0 else 1.0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] > 0:
                ax.plot(pos[[i, j], 0], pos[[i, j], 1], color="#4C72B0", alpha=0.15 + 0.6 * A[i, j] / wmax, lw=0.8)
    ax.scatter(pos[:, 0], pos[:, 1], s=14, color="k", zorder=3)
    for i, nm in enumerate(ch_names):
        if nm in label:
            ax.annotate(nm, pos[i, :2], fontsize=7, color="crimson", xytext=(3, 3), textcoords="offset points")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=9)
    _finish(fig, path, banner)


def _mu_power(x, sfreq, lo=8.0, hi=13.0):
    f, p = signal.welch(x, fs=sfreq, nperseg=min(256, x.shape[-1]), axis=-1)
    m = (f >= lo) & (f < hi)
    return p[..., m].mean(axis=-1)


def erd_sanity(ds) -> dict:
    """Is the expected physiology present? Contralateral mu suppression => lateralisation index
    LI = (P_C4 - P_C3) / (P_C4 + P_C3) should be HIGHER for right-hand than left-hand imagery."""
    if "C3" not in ds.ch_names or "C4" not in ds.ch_names:
        return {}
    i3, i4 = ds.ch_names.index("C3"), ds.ch_names.index("C4")
    p3, p4 = _mu_power(ds.X[:, i3], ds.sfreq), _mu_power(ds.X[:, i4], ds.sfreq)
    li = (p4 - p3) / (p4 + p3)
    rows = []
    for s in np.unique(ds.subject):
        m = ds.subject == s
        if (ds.y[m] == 0).any() and (ds.y[m] == 1).any():
            rows.append((s, li[m & (ds.y == 0)].mean(), li[m & (ds.y == 1)].mean()))
    r = np.array(rows)
    d = r[:, 2] - r[:, 1]
    p = float(stats.wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
    return {"n_subjects": int(len(r)), "frac_subjects_expected_direction": float((d > 0).mean()),
            "mean_li_left": float(r[:, 1].mean()), "mean_li_right": float(r[:, 2].mean()),
            "wilcoxon_p": p, "per_subject": r}


def plot_erd_sanity(ds, path, banner=None):
    res = erd_sanity(ds)
    if not res:
        return {}
    r = res["per_subject"]
    fig, ax = plt.subplots(figsize=(3.8, 3.6))
    for _, a, b in r:
        ax.plot([0, 1], [a, b], color="gray", alpha=0.35, lw=0.8)
    ax.plot([0, 1], [r[:, 1].mean(), r[:, 2].mean()], color="crimson", lw=2.5, marker="o")
    ax.set_xticks([0, 1], ["left-hand\nimagery", "right-hand\nimagery"])
    ax.set_ylabel("mu-band lateralisation index\n(P_C4 - P_C3)/(P_C4 + P_C3)")
    ax.set_title(f"Expected ERD pattern: {100 * res['frac_subjects_expected_direction']:.0f}% of subjects, "
                 f"p={res['wilcoxon_p']:.2g}", fontsize=8)
    _finish(fig, path, banner)
    return {k: v for k, v in res.items() if k != "per_subject"}
