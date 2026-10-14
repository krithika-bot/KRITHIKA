# EEG Analysis using AI/ML — Project Documentation

## 1. Project summary

This project is a reproducible, software-only EEG analysis of left- versus right-hand motor imagery. It uses the PhysioNet EEG Motor Movement/Imagery Database (EEGMMIDB) and compares two classical machine-learning pipelines with a majority-class reference. The evaluation holds out entire participants so the reported task is cross-participant decoding within this dataset.

**Research question:** On the selected EEGMMIDB cohort, how do mu/beta band-power features with logistic regression and Common Spatial Patterns (CSP) with Linear Discriminant Analysis (LDA) compare when test participants are held out from training?

**Project status:** The pipeline, full-cohort analysis, aggregate evidence, checksum audit, report, and reproducibility documentation have been created and run. This is an exploratory baseline study. It is not a clinical validation, medical device, or claim of performance on other populations or equipment.

## 2. Core concept and rationale

EEG trials from different people can vary substantially. A random trial split can place trials from the same person in both training and test data and give an overly optimistic estimate of performance on new participants. This project defines its target explicitly: train on some participants and evaluate on different participants.

The model comparison asks whether a spatial filtering baseline (CSP-LDA) and a channel-wise spectral baseline (mu/beta power with logistic regression) differ under the same participant-wise folds. A majority classifier is included as a simple reference. The project emphasizes traceable data provenance, clear preprocessing, participant-level grouping, uncertainty, and bounded interpretation rather than selecting a model for a headline score.

## 3. Dataset and provenance

- **Name/version:** PhysioNet EEG Motor Movement/Imagery Database (EEGMMIDB), v1.0.0.
- **Source:** [PhysioNet dataset page](https://physionet.org/content/eegmmidb/1.0.0/).
- **DOI:** [10.13026/C28G6P](https://doi.org/10.13026/C28G6P).
- **License:** Open Data Commons Attribution License v1.0; cite the dataset when reusing it.
- **Recording format:** EDF+, 64 EEG channels, 160 Hz.
- **Selected runs:** 4, 8, and 12, the left/right fist motor-imagery runs. Runs 3, 7, and 11 are movement-execution runs and are not part of this analysis.
- **Labels:** T1 = left-hand imagery; T2 = right-hand imagery.
- **Analyzed cohort:** 104 participants, 4,680 retained epochs, 64 channels, 640 samples per epoch. The analyzed class counts are 2,360 left and 2,320 right epochs.
- **Files used:** 312 EDF files (three selected runs per participant). Every used file was checked by SHA-256 against the checksum registry bundled with the installed MNE-Python version. The audit found zero missing files and zero checksum mismatches.
- **Raw data handling:** EDF files remain in the local MNE cache and are excluded from this repository. The repository contains aggregate results, not trial predictions, participant scores, or a per-recording manifest.

Five participants from the 109-participant database were not part of the locally available verified cohort. The project records the omission without claiming why those recordings were unavailable. The analysis uses all 104 participants that were loaded successfully and passed the file checks.

## 4. Software, tools, and environment

| Tool | Use in this project |
|---|---|
| Python | Pipeline, models, evaluation, report generation |
| MNE-Python | Read EDF+, standardize EEG channels, filtering, annotations, event and epoch handling |
| NumPy | Trial arrays, per-trial normalization, participant grouping |
| SciPy | Welch spectral estimates and exploratory paired statistical comparison |
| pandas | Aggregate tables and CSV evidence |
| scikit-learn | Logistic regression, CSP-related pipeline components, shrinkage LDA, metrics, and majority reference |
| Matplotlib | Aggregate performance and confusion-matrix figures |
| Git | Version control for code and documentation |
| Jupyter-compatible notebook | Optional results walkthrough |

Exact versions for the reported run are recorded in [`run_info.json`](results/full_cohort/run_info.json). The run environment used Python 3.12.14, MNE 1.13.2, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, and scikit-learn 1.9.1.

## 5. End-to-end workflow

1. **Locate data:** use the local MNE EEGBCI cache by default; downloading missing recordings is an explicit CLI option.
2. **Load and check:** load the three selected EDF runs per eligible participant, standardize channel names, confirm the expected 64 channels and 160 Hz sampling, and record exclusions rather than silently skipping them.
3. **Audit source files:** compare each selected EDF SHA-256 digest with MNE-Python's packaged EEGBCI checksum registry. The public audit records aggregate counts and a combined fingerprint, not file names or per-file hashes.
4. **Filter and epoch:** apply an 8–30 Hz FIR band-pass filter, find T1/T2 annotations, and extract cue-onset epochs from 0 to 3.99375 seconds (640 samples at 160 Hz). Reject epochs covered by MNE bad annotations.
5. **Normalize each epoch:** convert to microvolts, subtract each channel's within-epoch mean, and divide by the epoch-wide RMS. This is a label-free per-trial transform.
6. **Compute fixed inputs:** calculate per-channel Welch log-power for mu (8–13 Hz) and beta (13–30 Hz), and compute normalized trial covariance matrices for CSP.
7. **Fit three baselines inside each fold:** a training-fold majority reference; standardized log-band-power features with L2 logistic regression (`C=0.1`); and six regularized CSP components with shrinkage LDA.
8. **Evaluate by participant:** for each of seeds 0, 1, and 2, partition the 104 participants into five disjoint test folds. Assert that train and test participants do not overlap and that every participant appears in one test fold per seed.
9. **Summarize:** calculate trial metrics by seed, mean participant accuracy, a 10,000-resample percentile bootstrap interval across participants, aggregate confusion matrices, and an explicitly exploratory paired comparison.
10. **Write evidence:** save CSV summaries, JSON run/provenance metadata, plots, and a generated Markdown report. The pipeline does not save raw predictions or participant-level score rows.

## 6. Model details

### Majority reference

`DummyClassifier(strategy="prior")`, fitted only on the training participants in each fold. This provides a simple reference reflecting the training class prior.

### Mu/beta band-power logistic regression

Welch power is averaged within the 8–13 Hz mu and 13–30 Hz beta bands for each of the 64 channels, log transformed, standardized using the training fold, and classified with L2 logistic regression (`C=0.1`, `max_iter=2000`).

### CSP with shrinkage LDA

Six CSP filters are fit from training-fold class covariance matrices with trace normalization and 1% diagonal regularization. Log normalized variances of the projected signals are passed to shrinkage LDA. The spatial filters are re-fit independently in each training fold.

## 7. Evaluation design and evidence

The evaluation target is unseen participants drawn from the same public dataset and protocol. For each seed, the 104 participants are partitioned into five disjoint test groups. All trials from a participant remain in that participant's fold. Assertions in the evaluation code check train/test separation and one-time test coverage per seed.

The report includes accuracy, balanced accuracy, macro F1, ROC AUC, confusion matrices, and mean participant accuracy. The confidence intervals are percentile bootstrap intervals over participant mean accuracies (10,000 resamples). The paired CSP-LDA versus logistic-regression test uses participant-level differences and a two-sided Wilcoxon signed-rank test; it is exploratory and was not preregistered.

### Full-cohort result

| Model | Mean participant accuracy | Participant-bootstrap 95% CI | Balanced accuracy | Macro F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|
| Majority reference | 50.4% | 50.1–50.8% | 50.0% | 33.5% | 49.6% |
| Mu/beta band-power + logistic regression | 58.4% | 56.6–60.1% | 58.4% | 58.4% | 61.8% |
| CSP + shrinkage LDA | 61.9% | 59.5–64.4% | 61.9% | 61.9% | 66.3% |

CSP-LDA's mean participant accuracy was 3.5 percentage points above the band-power model in this run (paired bootstrap 95% interval: 1.6 to 5.6 percentage points; exploratory Wilcoxon p = 0.0021). This comparison is specific to this dataset, cohort, preprocessing, and fixed model settings; it does not establish general superiority.

### Evidence files

- [`analysis_report.md`](results/full_cohort/analysis_report.md) — generated run summary.
- [`summary.csv`](results/full_cohort/summary.csv) — aggregate model metrics and confidence intervals.
- [`fold_metrics.csv`](results/full_cohort/fold_metrics.csv) — aggregate metrics per seed, fold, and method.
- [`confusion_matrices.csv`](results/full_cohort/confusion_matrices.csv) — aggregate held-out class counts and fractions.
- [`paired_comparison.csv`](results/full_cohort/paired_comparison.csv) — exploratory paired summary.
- [`run_info.json`](results/full_cohort/run_info.json) — configuration, dataset summary, data integrity summary, and software versions.
- [`dataset_audit.json`](results/full_cohort/provenance/dataset_audit.json) — aggregate-only checksum evidence.
- [`performance.png`](results/full_cohort/figures/performance.png) — participant accuracy and bootstrap intervals.
- [`confusion_matrices.png`](results/full_cohort/figures/confusion_matrices.png) — normalized confusion matrices for the two feature models.

## 8. Code map

```text
projects/eeg-analysis/
├── README.md                         # Quick start and scope
├── PROJECT_DOCUMENTATION.md          # Complete project record
├── research_report.md                # Narrative research report
├── docs/METHODS.md                   # Detailed methods and decision record
├── pyproject.toml                    # Package and CLI metadata
├── requirements.txt                  # Runtime dependencies
├── scripts/run_analysis.py           # Command-line experiment entry point
├── src/eeg_analysis/
│   ├── data.py                       # Dataset loading, preprocessing, checksum audit
│   ├── models.py                     # Fixed features and model factories
│   ├── evaluation.py                 # Subject-wise folds, metrics, aggregate outputs
│   └── cli.py                        # Command-line arguments
├── notebooks/eeg_analysis_results.ipynb # Aggregate-results walkthrough
└── results/full_cohort/              # Reproducibility evidence and plots
```

## 9. Reproduction instructions

From this directory, create an environment and install the declared packages:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

With the dataset already present under `data/raw/MNE-eegbci-data/`, run offline:

```bash
python scripts/run_analysis.py --data-root data/raw --out results/full_cohort
```

To let MNE download missing files from PhysioNet, when network access is available:

```bash
python scripts/run_analysis.py --data-root data/raw --out results/full_cohort --download-missing
```

The data directory is ignored by Git. The current offline analysis used a local cache, so no download is needed to inspect the committed aggregate evidence. Downloading all selected files can take time and requires internet access.

## 10. Limitations and interpretation

- The evaluated cohort contains 104 of 109 database participants; the reason for the five absent recordings is not inferred.
- Only left-versus-right hand motor imagery is studied. This project does not analyze motor execution, rest-state recognition, another dataset, or a clinical population.
- Rejecting MNE bad annotations is not comprehensive artifact removal. No ICA, EOG regression, or automated muscle-artifact detector is used.
- The reported estimates are specific to this cohort, hardware, protocol, preprocessing, and fixed hyperparameters.
- Hyperparameters were not selected in nested cross-validation, and the paired comparison was exploratory rather than preregistered.
- No independent external test cohort, causal interpretation, clinical endpoint, or diagnostic performance claim is provided.
- Classification scores are not evidence of medical usefulness.

## 11. References

1. Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset (version 1.0.0).* PhysioNet. [https://doi.org/10.13026/C28G6P](https://doi.org/10.13026/C28G6P).
2. Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N., & Wolpaw, J. R. (2004). BCI2000: A general-purpose brain-computer interface system. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034–1043. [https://doi.org/10.1109/TBME.2004.827072](https://doi.org/10.1109/TBME.2004.827072).
3. Ramoser, H., Müller-Gerking, J., & Pfurtscheller, G. (2000). Optimal spatial filtering of single trial EEG during imagined hand movement. *IEEE Transactions on Rehabilitation Engineering*, 8(4), 441–446. [https://doi.org/10.1109/86.895946](https://doi.org/10.1109/86.895946).
4. MNE-Python. EEGBCI dataset loader and checksum registry documentation. [https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html).
