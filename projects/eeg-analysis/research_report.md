# EEG Analysis using AI/ML: Subject-wise motor-imagery baselines

## Abstract

This project evaluates classical machine-learning baselines for decoding left- versus right-hand motor imagery from public EEG. It uses PhysioNet EEGMMIDB runs 4, 8, and 12, 104 participants, and 4,680 labelled epochs. A majority-class reference is compared with per-channel mu/beta Welch power plus logistic regression and a CSP plus shrinkage-LDA pipeline. Evaluation holds out participants in five folds and repeats the partitioning for three seeds. CSP-LDA achieved a mean participant accuracy of 61.9% (95% participant-bootstrap CI 59.5–64.4%); band-power logistic regression achieved 58.4% (56.6–60.1%); the majority reference achieved 50.4% (50.1–50.8%). These exploratory results do not establish clinical performance or generalization outside this cohort and protocol.

## Research question

How do transparent signal features and spatial filters compare for cross-participant left/right hand motor-imagery decoding on a public EEG dataset?

## Data and provenance

PhysioNet EEG Motor Movement/Imagery Database v1.0.0 (EEGMMIDB), runs 4, 8, and 12. The task uses T1 for left-hand imagery and T2 for right-hand imagery. The selected cohort contains 104 of 109 participants; five were not included in the preselected cohort, and no reason is inferred for their omission. All 312 EDF files used here were SHA-256 checked against the installed MNE-Python EEGBCI checksum registry with zero mismatches. Raw data and per-file participant identifiers are not included in the public evidence package.

## Methods

EDF files were loaded and channel names standardized with MNE-Python. EEG was FIR band-pass filtered from 8 to 30 Hz. Epochs cover cue onset to 3.99375 seconds at 160 Hz (640 samples), with epochs annotated as bad rejected. Every epoch was demeaned channel-wise and scaled by its whole-epoch RMS.

The baseline models are:

1. `DummyClassifier(strategy="prior")` majority-class reference.
2. Welch log-power features in the mu (8–13 Hz) and beta (13–30 Hz) bands for each of 64 channels, followed by training-fold standardization and L2 logistic regression (`C=0.1`).
3. Six regularized Common Spatial Patterns filters with log-variance features, followed by shrinkage Linear Discriminant Analysis.

The 104 participants are split into five disjoint test folds per seed, for seeds 0, 1, and 2. Each participant is tested once per seed and is never used in training for that fold. The 95% interval for mean participant accuracy uses a percentile bootstrap across participants (10,000 resamples). The CSP-LDA versus band-power logistic-regression comparison is paired by participant and exploratory; it was not preregistered.

## Results

| Model | Mean participant accuracy | 95% CI | Balanced accuracy | Macro F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|
| Majority reference | 50.4% | 50.1–50.8% | 50.0% | 33.5% | 49.6% |
| Band-power logistic regression | 58.4% | 56.6–60.1% | 58.4% | 58.4% | 61.8% |
| CSP + shrinkage LDA | 61.9% | 59.5–64.4% | 61.9% | 61.9% | 66.3% |

CSP-LDA was 3.5 percentage points higher than band-power logistic regression in mean participant accuracy (paired 95% bootstrap CI 1.6–5.6 points; exploratory Wilcoxon signed-rank p=0.0021). This is evidence for a difference under this particular cross-subject analysis, not proof of superiority on other datasets.

## Conclusion

Both feature-based methods exceeded the majority reference on this selected cohort. CSP-LDA had higher observed accuracy than band-power logistic regression. The results support the project’s limited methodological question: feature and spatial-filter choices affect baseline performance. They do not establish a robust decoder, causal explanation of EEG activity, or clinical use.

## Limitations

- The analysis uses 104 of the database’s 109 participants; five were outside the selected verified cohort.
- Only motor imagery runs are analyzed; motor execution is not included.
- Bad-annotation rejection is not comprehensive artifact removal. No ICA, EOG regression, or amplitude threshold was used.
- Hyperparameters were fixed rather than tuned in a nested cross-validation design.
- Performance estimates are specific to this dataset, acquisition system, and preprocessing.
- No clinical population or clinical endpoint was studied.

## Reproducibility

See [README.md](README.md), [methods and decisions](docs/METHODS.md), [run metadata](results/full_cohort/run_info.json), [checksum audit](results/full_cohort/provenance/dataset_audit.json), and [aggregate result files](results/full_cohort/).

## References

1. Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset (version 1.0.0).* PhysioNet. https://doi.org/10.13026/C28G6P.
2. Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N., & Wolpaw, J. R. (2004). BCI2000: A General-Purpose Brain-Computer Interface (BCI) System. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034–1043. https://doi.org/10.1109/TBME.2004.827072.
3. Ramoser, H., Müller-Gerking, J., & Pfurtscheller, G. (2000). Optimal spatial filtering of single trial EEG during imagined hand movement. *IEEE Transactions on Rehabilitation Engineering*, 8(4), 441–446. https://doi.org/10.1109/86.895946.
