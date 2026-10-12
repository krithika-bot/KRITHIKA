# EEG Graph Neural Network — portfolio text

**Status:** Software implementation complete; exploratory real-data pilot completed on 20 PhysioNet participants.

I implemented and ran a reproducible EEG motor-imagery pipeline comparing classical baselines, EEGNet, and electrode-graph neural networks under participant-wise evaluation. On a checksum-verified 20-participant PhysioNet pilot, CSP + LDA reached 55.8% mean participant accuracy (95% bootstrap CI 52.1–59.6%); the distance-graph GCN reached 53.7%. The graph did not significantly outperform the identity control after correction for multiple comparisons. The report includes raw held-out predictions, dataset checksums, run metadata, training histories, summary tables, figures, and limitations. The result is exploratory and does not establish generalization to the full cohort.

**Evidence:** [Full project documentation](PROJECT_DOCUMENTATION.md) · [Project source](../README.md) · [Software validation record](VALIDATION.md) · [Colab notebook](../notebooks/run_on_colab.ipynb)

**Scope:** One public dataset, healthy volunteers, and left/right motor-imagery classes. The graph represents a modelling choice; it is not evidence of brain connectivity and is not a clinical tool.
