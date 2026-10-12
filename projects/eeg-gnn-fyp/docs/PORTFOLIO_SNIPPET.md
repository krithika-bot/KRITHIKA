# EEG Graph Neural Network — portfolio text

**Status:** Software implementation and validation complete; real-data experiments pending.

I implemented a reproducible EEG motor-imagery pipeline that compares classical baselines, EEGNet, and electrode-graph neural networks under participant-wise evaluation. The code passes 13 software tests and completes a synthetic smoke check. These checks validate software behavior only; the PhysioNet real-data experiment has not yet completed, so no EEG performance result is claimed.

**Evidence:** [Full project documentation](PROJECT_DOCUMENTATION.md) · [Project source](../README.md) · [Software validation record](VALIDATION.md) · [Colab notebook](../notebooks/run_on_colab.ipynb)

**Scope:** One public dataset, healthy volunteers, and left/right motor-imagery classes. The graph represents a modelling choice; it is not evidence of brain connectivity and is not a clinical tool.
