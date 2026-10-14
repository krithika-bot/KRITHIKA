# EEG Analysis using AI/ML

An end-to-end, reproducible analysis of public EEG for left-versus-right hand motor-imagery classification. The project makes the dataset choice, signal processing, participant-level evaluation, model baselines, aggregate results, and limitations inspectable.

> **Research status:** the software pipeline and the reported 104-participant analysis have been run. The results are exploratory and apply only to this public dataset and protocol. This is not a clinical or diagnostic system.

## Project question

How do two classical feature-based EEG baselines compare with a majority-class reference when the test participants are held out from training?

## Dataset

- **Dataset:** PhysioNet EEG Motor Movement/Imagery Database (EEGMMIDB), version 1.0.0
- **Source:** [PhysioNet](https://physionet.org/content/eegmmidb/1.0.0/)
- **Dataset citation:** Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset (version 1.0.0).* PhysioNet. [doi:10.13026/C28G6P](https://doi.org/10.13026/C28G6P)
- **License:** Open Data Commons Attribution License v1.0
- **Task:** left-versus-right hand motor imagery, runs 4, 8, and 12
- **Labels:** T1 = left hand imagery; T2 = right hand imagery
- **Cohort used:** 104 participants, 64 EEG channels, 160 Hz; five participant recordings were absent from the local checksum-verified cache used for this run. The analysis does not infer why those recordings were absent.
- **Raw data:** fetched from PhysioNet through MNE when needed; not included in this repository.

Runs 4, 8, and 12 are motor-imagery runs. They are distinct from runs 3, 7, and 11, which record executed hand movements. The project reports only the imagery task.

## Analysis pipeline

1. Load EDF recordings with MNE-Python and standardize EEG channel names.
2. Band-pass filter from 8 to 30 Hz.
3. Select T1/T2 motor-imagery events and create 640-sample epochs from cue onset.
4. Reject epochs covered by MNE bad annotations; demean each channel and apply whole-trial RMS normalization.
5. Compare three fixed baselines:
   - majority-class reference;
   - per-channel mu (8–13 Hz) and beta (13–30 Hz) Welch log-power with standardized logistic regression;
   - shrinkage-regularized Common Spatial Patterns with shrinkage Linear Discriminant Analysis.
6. Evaluate with five-fold participant-grouped cross-validation for each of three seeds. No participant appears in both training and test sets within a fold.
7. Report accuracy, balanced accuracy, macro F1, ROC AUC, participant-bootstrap confidence intervals, confusion matrices, and an exploratory paired comparison between the two feature models.

Model and preprocessing settings are fixed before evaluation. The comparison is a baseline study; it does not claim state-of-the-art performance.

## Reproduce

Python 3.10 or newer is required. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_analysis.py --data-root data/raw --out results/full_cohort --download-missing
```

If the EEGMMIDB files are already cached locally and network access is unavailable, omit `--download-missing` and point `--data-root` at the directory containing `MNE-eegbci-data/`:

```bash
python scripts/run_analysis.py \
  --data-root /path/to/MNE-cache-root \
  --out results/full_cohort
```

The run is CPU-compatible. A full download requires several hundred megabytes; MNE stores data in the selected raw-data directory. `data/` is ignored by Git.

## Evidence in this repository

- [Full analysis report](results/full_cohort/analysis_report.md)
- [Aggregate metrics](results/full_cohort/summary.csv)
- [Fold-level aggregate metrics](results/full_cohort/fold_metrics.csv)
- [Aggregate confusion matrices](results/full_cohort/confusion_matrices.csv)
- [Exploratory paired comparison](results/full_cohort/paired_comparison.csv)
- [Run settings and software versions](results/full_cohort/run_info.json)
- [Aggregate dataset checksum audit](results/full_cohort/provenance/dataset_audit.json)
- [Performance figure](results/full_cohort/figures/performance.png)
- [Confusion-matrix figure](results/full_cohort/figures/confusion_matrices.png)
- [Methods and decision record](docs/METHODS.md)
- [Complete project documentation](PROJECT_DOCUMENTATION.md)
- [Research report](research_report.md)
- [Results walkthrough notebook](notebooks/eeg_analysis_results.ipynb)

The public evidence package contains aggregate outputs only. It does not include EDF files, trial-level predictions, participant-level scores, or a file-by-file recording manifest.

## Software and tools

Python, MNE-Python, NumPy, SciPy, pandas, scikit-learn, Matplotlib, Git, and Jupyter-compatible notebook tooling. Exact versions used for the reported run are recorded in `results/full_cohort/run_info.json`.

## Limitations

- The selected cohort contains 104 of the dataset's 109 participants. Five were not included in the local checksum-verified cache; no reason is inferred for their absence.
- Only left-versus-right hand motor imagery is studied. This does not evaluate movement execution, rest detection, or transfer to another dataset.
- Annotation-based rejection is not a complete ocular, muscle, or movement-artifact-removal procedure.
- Cross-subject testing estimates performance on unseen people from this dataset; it does not establish performance on new equipment, sites, populations, or clinical tasks.
- No hyperparameter tuning, nested model selection, clinical evaluation, or causal interpretation is claimed.
- Machine-learning performance is not medical evidence.
