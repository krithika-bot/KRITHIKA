# EEG Graph Neural Network — portfolio text

**Status:** Full eligible-cohort experiment completed on PhysioNet EEGMMIDB.

I built and ran a reproducible EEG motor-imagery pipeline on 104 checksum-verified participants, comparing classical
baselines, EEGNet, five electrode-graph variants, and training-label-shuffle controls. Evaluation used five
participant-wise folds and three seeds. EEGNet achieved 70.1% mean participant accuracy (95% bootstrap CI
67.9–72.4%), while CSP + LDA achieved 61.9%. The distance-graph GCN reached 56.9%, 1.2 percentage points below the
identity-graph control; the difference did not survive Holm correction (adjusted p = 0.053). The result does not
demonstrate a benefit from the tested spatial graph and is specific to this dataset and configuration.

**Evidence:** [Full-cohort report](FULL_COHORT_REPORT.md) · [Full project documentation](PROJECT_DOCUMENTATION.md) ·
[Validation record](VALIDATION.md) · [Evidence index, predictions, provenance and figures](../results/full_cohort/README.md) ·
[Project source](../README.md) · [Colab notebook](../notebooks/run_on_colab.ipynb)

**Scope:** One public dataset, healthy volunteers, and left/right fist motor-imagery classes. Electrode graphs encode
a modelling choice; they are not evidence of anatomical connectivity. This is not a clinical or diagnostic tool.
