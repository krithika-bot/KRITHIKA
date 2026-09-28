# EEG Analysis: A Reproducible Computational Pipeline for Motor-Related EEG

**Status:** Research project / manuscript draft — results pending execution.

## Abstract

This project develops a reproducible computational pipeline for analysing publicly available electroencephalography (EEG) recordings associated with motor tasks. The objective is to demonstrate a complete workflow from raw EEG data through preprocessing, feature extraction, and a baseline machine-learning model. The project is designed as a bridge between computer science/AI/ML and computational neuroscience. It does not make clinical or diagnostic claims.

## 1. Background

EEG provides time-varying measurements of electrical activity recorded from the scalp. Computational analysis requires careful handling of signal quality, event timing, preprocessing, feature representation, and evaluation. A machine-learning result can be misleading if subject information leaks between training and testing data, so this project uses subject-level separation for its baseline evaluation.

## 2. Dataset

The project uses the PhysioNet EEG Motor Movement/Imagery Dataset (EEGMMIDB), accessed through MNE-Python. The dataset contains 64-channel EEG recordings from 109 volunteers and includes motor execution and motor imagery tasks. For the first implementation, runs 3, 7, and 11 are used because they correspond to left-versus-right fist motor execution in the documented protocol.

Dataset citation:

Schalk, G. (2009). EEG Motor Movement/Imagery Dataset (version 1.0.0). PhysioNet. https://doi.org/10.13026/C28G6P

Original BCI2000 publication:

Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N., & Wolpaw, J. R. (2004). BCI2000: A General-Purpose Brain-Computer Interface (BCI) System. IEEE Transactions on Biomedical Engineering, 51(6), 1034–1043.

## 3. Research Question

Can a simple, reproducible feature-based machine-learning pipeline distinguish the documented motor-task classes in a held-out-subject evaluation on a public EEG dataset?

## 4. Hypothesis

A baseline model using basic frequency-band EEG features should capture some task-related structure, but performance is expected to depend on preprocessing, feature choice, subject variability, and the evaluation design.

## 5. Computational Pipeline

1. Download selected EEG recordings using MNE-Python.
2. Standardize EEG channel names and montage information.
3. Apply a conservative 1–40 Hz band-pass filter.
4. Extract two-second epochs following task events.
5. Estimate power spectral density with Welch's method.
6. Summarize theta (4–8 Hz), alpha (8–13 Hz), and beta (13–30 Hz) band-power features.
7. Standardize features.
8. Train a logistic-regression baseline.
9. Evaluate on subjects excluded from training.
10. Report metrics only after the script has been executed and independently checked.

## 6. Evaluation

The primary evaluation is subject-grouped train/test separation. This is important because randomly splitting epochs can place highly correlated recordings from the same participant in both sets and produce an overly optimistic estimate of generalization.

Metrics to report after execution:

- Number of samples
- Training subjects
- Test subjects
- Accuracy
- Precision, recall, and F1-score
- Confusion matrix

**No numerical result is reported in this draft until the pipeline is actually run.**

## 7. Limitations

- The initial implementation is a baseline rather than a state-of-the-art decoder.
- Only a small subject subset is used initially for rapid reproducibility.
- Band-power features are intentionally simple.
- EEG preprocessing choices can materially affect results.
- Public motor-task data should not be interpreted as evidence of clinical diagnostic performance.
- Cross-subject generalization is a separate research question from within-subject decoding.

## 8. Future Work

- Expand to more subjects and runs.
- Compare alternative feature representations.
- Add common-spatial-pattern features for motor imagery experiments.
- Compare logistic regression with tree-based and neural models.
- Add nested cross-validation where appropriate.
- Study robustness to preprocessing choices.
- Connect the computational pipeline to the longer-term NBN human-state modelling research direction without conflating this benchmark with NBN validation.

## 9. Reproducibility

The repository contains the Python pipeline and dependency specification. Dataset files are not committed to GitHub; they are fetched through MNE from the public PhysioNet resource. Users must follow the dataset's attribution and license requirements.
