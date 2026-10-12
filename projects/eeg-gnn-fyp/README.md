# Electrode-graph neural networks for cross-subject EEG motor-imagery decoding

Final-year project · Krithika K · B.Sc. Computer Science (AI & ML), VISTAS, Chennai

> **Status: implementation, software checks, and the full eligible-cohort real-data experiment complete.** The
> analysis covers 104 PhysioNet participants, five subject-wise folds, and three seeds. EEGNet reached 70.1% mean
> participant accuracy (95% participant-bootstrap CI 67.9–72.4%); the distance-graph GCN reached 56.9%, 1.2 points
> below the identity control, but that difference did not survive Holm correction (adjusted p = 0.053). See the
> [full-cohort report](docs/FULL_COHORT_REPORT.md) and [evidence index](results/full_cohort/README.md). An earlier
> 20-participant pilot is retained under `results/real_data_pilot/` as exploratory history.
> `summary.md` is generated from raw predictions by `scripts/make_summary.py`; nothing is typed in by hand. See
> [`docs/VALIDATION.md`](docs/VALIDATION.md) for the current validation record and
> [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md) for the full project explanation, dataset provenance,
> code map, tooling, evaluation plan, evidence boundaries, and reproduction instructions.

## Research question

Does giving a neural network the **spatial structure of the EEG electrode array** (a graph over electrodes) improve
decoding of imagined left- vs right-hand movement in **unseen subjects**, compared with (i) classical pipelines,
(ii) a compact non-graph CNN, and (iii) the *same* graph network with a graph that carries no spatial information?

Hypotheses (written before running the experiments; they may be refuted):

* **H1.** A graph network is at least competitive with EEGNet in cross-subject decoding.
* **H2.** A spatially meaningful graph (`distance`) beats the identical network with no graph (`identity`),
  a fully-connected uniform graph (`uniform`) and a degree-matched random graph (`random`).
* **H3 (exploratory).** A data-driven connectivity graph (`corr`) differs from the distance graph.

A null or negative outcome on any of these is a valid, reportable result.

## Data

[PhysioNet EEG Motor Movement/Imagery Dataset](https://physionet.org/content/eegmmidb/1.0.0/) (EEGMMIDB; 109
volunteers, 64 channels, 160 Hz; recorded with BCI2000). We use the three **left- vs right-fist motor-imagery**
runs (4, 8, 12). Data are downloaded through MNE-Python; nothing is redistributed here. Subjects with irregular
annotations (88, 89, 92, 100, 104 — commonly excluded in the literature) are excluded, and the loader additionally
validates sampling rate and trial counts and logs any subject it skips (`meta["skipped"]` in the cache).

## Methods

| Step | What is done | Code |
|---|---|---|
| Preprocessing | 8–30 Hz band-pass (mu + beta), epoch 0–4 s after cue, per-trial DC removal and global RMS scaling (keeps inter-channel power ratios; label-free) | `data.py`, `preprocess.py` |
| Classical baselines | CSP + LDA; log band-power (mu, beta) + logistic regression | `baselines.py` |
| Deep baseline | EEGNet (Lawhern et al., 2018) | `models.py` |
| Graph model | shared per-electrode temporal filter bank → log-power features → 2 graph-convolution layers on a fixed electrode graph → flatten (keeps electrode identity) → linear classifier | `models.py` |
| Graph variants | `identity`, `uniform`, `random`, `distance`, `corr` (and optionally `plv`). **Only the adjacency matrix differs**, so parameter counts are identical (checked in `tests/test_models.py` and logged in `run_info.json`) | `graphs.py` |

## Evaluation protocol (designed to avoid leakage)

* **Subject-wise 5-fold cross-validation**: every test subject is completely unseen — not used for fitting,
  scaling, graph estimation, or early stopping (`evaluate.fold_indices` asserts this).
* Early stopping uses **validation subjects** carved out of the training subjects.
* Data-driven graphs (`corr`, `plv`) are estimated on **training trials only**.
* 3 random seeds (different subject partitions and initialisations).
* Primary metric: **mean per-subject accuracy with 95% bootstrap CI over subjects**; also trial accuracy,
  balanced accuracy, macro-F1, AUC, confusion matrices.
* Paired **Wilcoxon signed-rank** tests on per-subject accuracy, **Holm-corrected** over all reported comparisons.

## Built-in sanity controls

1. **Label-permutation canary** (`run_baselines.py --permute-train-labels`): accuracy must fall to ≈ 50%.
2. **ERD physiology check** (`make_data_figures.py`): contralateral mu suppression should be visible in C3/C4
   — confirms the data really contain motor-imagery signal.
3. **Graph controls**: `identity`, `uniform`, `random` rule out "any graph helps" and "extra capacity helps".
4. **Unit tests** (`tests/`): fold disjointness, graph validity, planted-effect recovery, equal parameter counts,
   no message passing under the identity graph.

## Reproduce

```bash
pip install -e ".[test]"               # project dependencies plus pytest
python tests/run_tests.py              # all tests must pass first

# quick run (≈ 20 subjects, one seed) — good for a first end-to-end check
python scripts/make_data_figures.py --n-subjects 20
python scripts/run_baselines.py --n-subjects 20 --seeds 0 --out results/classical
python scripts/run_baselines.py --n-subjects 20 --seeds 0 --out results/classical --permute-train-labels
python scripts/run_deep.py      --n-subjects 20 --seeds 0 --out results/deep --resume
python scripts/make_summary.py  --results results

# full experiment (all subjects, 3 seeds; use a GPU — see notebooks/run_on_colab.ipynb)
python scripts/make_data_figures.py
python scripts/run_baselines.py --out results/classical
python scripts/run_baselines.py --out results/classical --permute-train-labels
python scripts/run_deep.py --out results/deep --resume
python scripts/make_summary.py --results results
```

`python scripts/run_deep.py --synthetic --smoke` runs a 1–2 minute wiring check on planted-effect synthetic data.
Synthetic output is **only** for testing the code and is stamped on every figure; never report it.

The completed full-cohort analysis contains checksum-verified recordings from 104 eligible participants (4,680
trials), participant-wise out-of-fold predictions, training histories, run metadata, generated tables, and figures.
EEGNet reached 70.1% mean participant accuracy (95% CI 67.9–72.4%), compared with 61.9% for CSP + LDA. The
distance-graph GCN reached 56.9%, 1.2 percentage points below the identity GCN (58.1%; Holm-adjusted p = 0.053),
which does not cross the 0.05 threshold. These results describe the tested dataset and fixed configuration. See the
[full report](docs/FULL_COHORT_REPORT.md) for the complete table and qualified interpretation, and the
[evidence index](results/full_cohort/README.md) for provenance and reproduction steps. Raw EDF recordings and the
derived cache are not redistributed. The earlier 20-participant pilot remains separately documented in
[`docs/REAL_DATA_PILOT_REPORT.md`](docs/REAL_DATA_PILOT_REPORT.md).

## Repository layout

```
configs/default.yaml     all hyper-parameters
src/eegfyp/              data, preprocess, graphs, baselines, models, train, evaluate, plots
scripts/                 verified PhysioNet download, run_baselines, run_deep, summaries, data figures
tests/                   correctness tests (+ run_tests.py runner)
notebooks/               run_on_colab.ipynb
docs/                    full project and cohort reports, validation record, report template, portfolio snippet
results/                 pilot and full-cohort predictions, provenance, summary tables and figures
```

## Limitations (stated up front)

* Single public dataset, healthy volunteers, 2-class imagery, ~45 trials per subject; no claim of clinical use.
* Cross-subject EEG decoding is hard; modest absolute accuracy is expected and not a bug.
* The `corr` graph is sensitive to volume conduction (nearby electrodes correlate); `plv` is provided as an alternative.
* One architecture family and one hyper-parameter setting; no extensive tuning (to keep comparisons fair).
* Not a medical device and not validated for any diagnostic or therapeutic purpose.

## References

* Goldberger et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. *Circulation* 101(23).
* Schalk, McFarland, Hinterberger, Birbaumer, Wolpaw (2004). BCI2000: a general-purpose brain-computer interface system. *IEEE Trans. Biomed. Eng.* 51(6).
* Ramoser, Müller-Gerking, Pfurtscheller (2000). Optimal spatial filtering of single trial EEG during imagined hand movement. *IEEE Trans. Rehabil. Eng.* 8(4).
* Lawhern et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. *J. Neural Eng.* 15(5).
* Kipf & Welling (2017). Semi-supervised classification with graph convolutional networks. *ICLR*.
* Gramfort et al. (2013). MEG and EEG data analysis with MNE-Python. *Front. Neurosci.* 7.

Code: MIT licence. Dataset: see the PhysioNet page for its licence and citation requirements.
