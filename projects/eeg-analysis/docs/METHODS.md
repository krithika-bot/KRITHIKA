# Methods and evidence record

## Scope

This project uses EEGMMIDB motor-imagery runs 4, 8, and 12 to distinguish left-hand imagery (T1) from right-hand imagery (T2). The estimand is cross-participant generalization on the selected dataset: test participants are excluded entirely from model fitting.

## Data provenance

EEGMMIDB v1.0.0 is hosted by PhysioNet and contains 64-channel EDF+ recordings at 160 Hz. Its license is Open Data Commons Attribution License v1.0. The local cohort contains 104 participants and all three selected runs per participant (312 EDF files); five participant recordings were absent from the existing checksum-verified cache. The current study does not claim a reason for their absence. No raw recording is copied into this repository.

Dataset citation: Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset (version 1.0.0).* PhysioNet. https://doi.org/10.13026/C28G6P.

Also cite the original system paper: Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N., & Wolpaw, J. R. (2004). BCI2000: A General-Purpose Brain-Computer Interface (BCI) System. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034–1043. https://doi.org/10.1109/TBME.2004.827072.

The spatial-filter baseline follows the Common Spatial Patterns approach for imagined hand movement described by Ramoser, H., Müller-Gerking, J., & Pfurtscheller, G. (2000). *IEEE Transactions on Rehabilitation Engineering*, 8(4), 441–446. https://doi.org/10.1109/86.895946.

## Preprocessing

- Read EDF+ files with MNE-Python and standardize EEG channel names.
- Preserve the 64 EEG channels; assign the standard 10-10 montage where channel names permit.
- Apply a 4th-order MNE FIR band-pass filter at 8–30 Hz to each run before concatenation.
- Extract T1/T2 epochs from 0.0 through 3.99375 seconds at 160 Hz (640 samples).
- Exclude epochs annotated as bad by MNE. No amplitude threshold, ICA, or automated ocular/muscle artifact classifier is applied.
- Convert to microvolts, subtract each channel's epoch mean, and divide the complete epoch by its RMS. This transformation is per trial and does not use class labels or other trials.

## Models

### Majority reference

`DummyClassifier(strategy="prior")`, fit only on the current training participants. It predicts according to the training-set class prior.

### Welch band power + logistic regression

Welch power is averaged over mu (8–13 Hz) and beta (13–30 Hz) bands for each of the 64 channels, then log-transformed. Features are standardized on the training data by a scikit-learn pipeline and passed to L2 logistic regression (`C=0.1`, `max_iter=2000`).

### CSP + LDA

Common Spatial Patterns estimates six spatial filters from trace-normalized class covariance matrices with 1% diagonal regularization. Log normalized variances of the six projected signals are classified with shrinkage Linear Discriminant Analysis. CSP filters are fit separately inside each training fold.

## Evaluation and uncertainty

For seeds 0, 1, and 2, the 104 participant IDs are independently permuted and partitioned into five disjoint test folds. Each participant is tested once per seed. The code asserts disjoint training and test participant groups and asserts complete, non-overlapping test-fold coverage per seed.

Trial-level accuracy, balanced accuracy, macro F1, and ROC AUC are calculated over all held-out trials for each seed, then averaged. Participant accuracy is calculated for every participant and averaged across seeds. A percentile bootstrap over those participant accuracies (10,000 resamples) provides the reported 95% interval for mean participant accuracy. The paired CSP-LDA versus logistic-regression comparison uses the participant-level accuracy differences and a two-sided Wilcoxon signed-rank test; it is explicitly exploratory and not preregistered.

## Evidence and privacy

`run_analysis.py` writes aggregate summary tables, fold-level metrics, confusion matrices, figures, and environment/configuration metadata. It intentionally does not save or publish trial-level predictions, per-participant scores, or participant-specific EDF manifests. Raw public EDF data stay outside Git.

## Interpretation

All findings apply to the specified PhysioNet cohort, motor-imagery runs, preprocessing, and fixed baseline settings. They do not establish clinical utility, causal mechanisms, or generalization to other cohorts or acquisition systems.
