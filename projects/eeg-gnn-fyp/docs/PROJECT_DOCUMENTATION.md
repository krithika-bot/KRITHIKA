# Full project documentation

**Project:** Electrode-graph neural networks for cross-subject EEG motor-imagery decoding  
**Author:** Krithika K · B.Sc. Computer Science (AI & ML), VISTAS, Chennai  
**Document updated:** 12 October 2026  
**Project stage:** Software implementation and software validation complete; real-data study pending.

> **Evidence boundary.** The code and its software checks have been run. The real PhysioNet EEG files were not successfully downloaded in the validation environment, so this project has no real-data model scores or scientific conclusion yet. Synthetic data are used only to check that the pipeline runs.

## 1. Project summary

This project builds a reproducible Python pipeline to compare classical classifiers, a compact convolutional neural network, and graph neural networks for distinguishing imagined left-fist from right-fist movement in EEG.

The specific question is whether representing the 64 scalp electrodes as a graph helps the model classify trials from people it did not see during training. A graph model is compared with the same model using control graphs, so a performance difference could be tested against the graph structure rather than simply a larger parameter count.

The target is motor-imagery classification for research and learning. It is not a medical device, diagnostic system, or validated brain-computer interface.

## 2. Core concept and research questions

EEG is recorded at multiple electrodes. Those electrodes have physical locations, and activity at different channels can be statistically related. A graph represents each electrode as a node and selected relationships as weighted edges. A graph-convolution layer combines a node's features with features from its connected nodes.

The project asks:

1. Can a graph neural network distinguish left- from right-fist motor-imagery trials for held-out participants?
2. Does a distance-based electrode graph help compared with the same model using no inter-electrode edges?
3. Does that graph compare favourably with EEGNet and classical signal-processing baselines?
4. Do results change when the graph uses uniform, random, or training-data-derived edges?

The hypotheses in the source README are hypotheses to test, not findings:

| Hypothesis | Planned comparison |
|---|---|
| H1 | Graph network versus EEGNet on unseen participants |
| H2 | Distance graph versus identity, uniform, and degree-matched random graph |
| H3 (exploratory) | Training-only correlation graph versus distance graph |

A null or negative result is a valid outcome. A graph built from electrode coordinates or signal correlations is a modelling choice; it should not be presented as proof of anatomical or functional brain connectivity.

## 3. Academic and technical level

**Academic level:** advanced final-year undergraduate project combining machine learning, signal processing, and computational neuroscience.

**Technical scope:** research-software prototype. It includes data acquisition code, preprocessing, classical and neural baselines, graph ablations, subject-level evaluation, tests, and report generation.

**Current maturity:** code paths have been tested, including a synthetic end-to-end smoke run and an automated GitHub Actions run. The planned real-data evaluation has not completed. The project is therefore not yet an empirical comparison of EEG model performance.

## 4. Dataset and data provenance

| Item | Project specification |
|---|---|
| Dataset | PhysioNet EEG Motor Movement/Imagery Dataset, version 1.0.0 (EEGMMIDB) |
| Participants in source dataset | 109 volunteers |
| Recording | 64 EEG channels, EDF+ files, 160 samples/second |
| Selected runs | Runs 4, 8, and 12: imagined left- versus right-fist movement |
| Event mapping in this project | T1 → left fist; T2 → right fist |
| Intended maximum in configuration | 109 participant IDs requested; five IDs (88, 89, 92, 100, 104) are excluded up front, leaving at most 104 candidates before loader checks |
| Data access | MNE-Python downloads recordings from PhysioNet when a run is started |
| Data in this GitHub repository | No raw EEG files; the dataset is not redistributed |

PhysioNet describes the collection as 64-channel EEG recorded at 160 Hz and explains that event-label meaning depends on the run. MNE's EEGBCI documentation maps runs 4, 8, and 12 to left-versus-right motor imagery. The code follows those run-specific labels and checks sampling rate, channel order, and a minimum trial count. It logs any additional participant it skips.

The configured data window is nominally 0–4 seconds after the event, represented by 640 samples at 160 Hz. The loader filters from 8 to 30 Hz before epoching, standardizes EEG channel names, assigns a standard 10–10 montage, and converts the returned signal to microvolts.

The source dataset has its own attribution terms. Cite PhysioNet and follow the dataset's [ODC Attribution License 1.0](https://physionet.org/content/eegmmidb/1.0.0/); do not treat the project repository's MIT code licence as a licence for the dataset.

**Actual data status:** no usable PhysioNet EDF file was processed in the recorded validation run. The attempted download was interrupted. There are no real-data predictions, subject counts, performance estimates, or result figures to report.

## 5. End-to-end workflow

    PhysioNet EEG recordings
            ↓
    MNE load, channel standardization, 8–30 Hz filtering
            ↓
    Runs 4/8/12 → T1/T2 events → 640-sample trials
            ↓
    Per-trial DC removal and whole-trial RMS normalization
            ↓
    Five subject-disjoint folds × three random seeds
            ↓
    CSP/LDA · band-power/logistic regression · EEGNet · graph models
            ↓
    Held-out-subject predictions → metrics, uncertainty, comparisons, figures

The synthetic-data option follows the same software paths using generated EEG-like signals with a deliberately planted class effect. It exists for pipeline tests only and cannot establish model performance on PhysioNet.

## 6. Preprocessing and model methods

### Preprocessing

1. Load the three motor-imagery runs for a participant.
2. Apply an 8–30 Hz band-pass filter (mu and beta range).
3. Epoch from the cue onset for 640 samples at 160 Hz, with no baseline subtraction in MNE's epoch constructor.
4. Convert voltage values to microvolts.
5. Remove each channel's within-trial DC mean.
6. Divide the whole trial by its global RMS. This keeps the channels' relative power differences; it does not use labels or statistics from other trials.

### Models and controls

| Method | Implementation | Why it is included |
|---|---|---|
| CSP + LDA | Trace-normalized, regularized Common Spatial Patterns followed by shrinkage LDA | Established signal-processing baseline |
| Log band-power + logistic regression | Welch power in 8–13 Hz and 13–30 Hz, log transformed, standardized, and classified with L2 logistic regression | Interpretable spectral-feature baseline |
| EEGNet | Compact depthwise/separable temporal-spatial CNN | Deep-learning baseline without an explicit electrode graph |
| EEGGraphNet | Shared temporal filter bank per channel → log-power features → two graph-convolution layers → channel-preserving flattening → two-class linear head | Proposed graph model |

The graph model uses trainable shared temporal filters to form one feature vector per electrode. It then applies two graph-convolution layers using the normalized adjacency matrix, followed by a classifier. Flattening retains electrode identity, which matters when left/right motor imagery produces spatially different patterns.

Graph variants used by the default experiment:

| Graph | Construction | Interpretation/control |
|---|---|---|
| Identity | No off-diagonal edges; normalization adds self-loops | No messages pass between electrodes |
| Uniform | Every pair of distinct electrodes has equal weight | Graph is present but carries no spatial information |
| Random | Distance-graph edge count and weight multiset, with randomized pairs | Tests whether arbitrary edges explain an effect |
| Distance | Six nearest electrode neighbours with Gaussian distance weights | Encodes physical proximity |
| Correlation | Top six mean absolute channel correlations from training trials | Data-derived graph; estimated from training data only |
| PLV (optional code path) | Top six phase-locking values from training trials | Optional alternative; not in the default graph list |

For the model ablation, only the adjacency changes across graph variants; the tests check that graph-model parameter counts are equal. The illustrative graph-figure script may estimate a correlation graph from all available data for visualization. The model evaluation path estimates correlation or PLV graphs from that fold's training trials only.

## 7. Evaluation design

The intended primary evaluation is **five-fold participant-wise cross-validation with seeds 0, 1, and 2**. Participants are assigned to held-out folds, and every trial for a test participant stays out of training. A validation set is selected from the remaining training participants for early stopping. The test set is evaluated only after selecting the best validation checkpoint.

This addresses a key EEG evaluation risk: trials from one person can share person-specific patterns. Random trial-level splitting could put trials from the same person in both training and test data and overstate performance. The code's fold helper asserts train/test subject disjointness; the tests check disjointness and fold coverage.

Data-derived graphs use training-fold data. Per-trial normalization uses only that trial. The training loop uses AdamW, a cosine learning-rate schedule, cross-entropy loss, dropout, and early stopping on validation subjects. Default settings are recorded in configs/default.yaml:

| Setting | Default |
|---|---:|
| Outer folds | 5 subject-wise folds |
| Seeds | 0, 1, 2 |
| Validation share | 15% of training participants |
| Graph neighbours | 6 |
| Training epochs / batch size | 40 / 64 |
| Learning rate / weight decay | 0.001 / 0.001 |
| Early-stopping patience / dropout | 10 epochs / 0.5 |
| GCN temporal filters / kernel | 16 / 40 samples |
| GCN hidden width / graph layers | 32 / 2 |

Planned measures are mean per-subject accuracy with a participant-level bootstrap 95% interval, trial accuracy, balanced accuracy, macro-F1, AUC, and confusion matrices. Paired model comparisons use Wilcoxon signed-rank tests on per-subject accuracy with Holm correction across the comparisons in the summary script. These metrics and tests are implemented; no real-data values have been generated.

## 8. Tools and software

| Tool/software | Role |
|---|---|
| Python 3.10+ | Project language; the recorded local validation used Python 3.12.14 |
| MNE-Python | Download/load EEGBCI EDF files, standardize channels, filter, epoch, and attach montage positions |
| NumPy and SciPy | Array processing, signal filters, graph calculations, bootstrap and statistical helpers |
| pandas | Trial-prediction tables and generated summaries |
| scikit-learn | LDA, logistic regression, scaling, and classification metrics |
| PyTorch | EEGNet, graph model, training loop, CPU/GPU selection |
| Matplotlib | Data sanity, graph, comparison, confusion, and learning-curve figures |
| PyYAML | Read the single experiment configuration file |
| pytest | Test dependency; the project runner reports the unit checks |
| Google Colab | Optional hosted notebook route for longer runs; a corrected notebook is included |
| GitHub and GitHub Actions | Public source, version history, portfolio link, and automated software validation |

The dependency minimums are declared in pyproject.toml and requirements.txt. The local recorded environment and exact package versions are listed in [VALIDATION.md](VALIDATION.md). Training automatically uses CUDA when PyTorch reports it is available; otherwise it uses CPU. The verified synthetic smoke run used CPU. No GPU real-data training run is recorded.

## 9. Code map

| Path | Responsibility |
|---|---|
| configs/default.yaml | Dataset choices, filters, graph settings, folds, seeds, and training hyperparameters |
| src/eegfyp/data.py | EEG dataset structure, MNE/PhysioNet loader, cache, synthetic generator |
| src/eegfyp/preprocess.py | Trial normalization, band-pass helper, log band-power |
| src/eegfyp/graphs.py | Distance, identity, uniform, random, correlation, PLV, and normalized adjacency |
| src/eegfyp/baselines.py | CSP, CSP+LDA, and band-power logistic regression |
| src/eegfyp/models.py | EEGNet, per-channel temporal encoder, graph convolution, EEGGraphNet |
| src/eegfyp/train.py | Device selection, AdamW training, validation-based early stopping, predictions |
| src/eegfyp/evaluate.py | Subject folds, leakage assertions, metrics, bootstrap intervals, paired tests, prediction files |
| src/eegfyp/plots.py | ERD checks and plots for graphs, comparisons, confusion matrices, and training history |
| src/eegfyp/utils.py | Configuration loading, random seeds, environment and run metadata |
| scripts/make_data_figures.py | ERD sanity check and graph illustrations |
| scripts/run_baselines.py | Classical baselines and optional train-label permutation canary |
| scripts/run_deep.py | EEGNet and graph-network cross-validation, predictions, histories, resume support |
| scripts/make_summary.py | Summary metrics, paired tests, corrected p-values, and figures from saved predictions |
| tests/ | Synthetic pipeline, preprocessing, graph, fold, statistical, and model checks |
| notebooks/run_on_colab.ipynb | Colab setup and quick/full run instructions; output folders are kept separate |
| docs/VALIDATION.md | Provenance, environment, completed software checks, and real-data status |
| docs/REPORT_TEMPLATE.md | Template for documenting an eventual empirical study |

The full source is in the [project folder on GitHub](https://github.com/krithika-bot/KRITHIKA/tree/main/projects/eeg-gnn-fyp).

## 10. Evidence and what it establishes

| Evidence | Recorded outcome | What it supports | What it does not support |
|---|---|---|---|
| Automated unit checks | 13 passed, 0 failed | Tested shapes, cache round-trip, subject split invariants, preprocessing, graph validity, planted-effect behavior, label-permutation sanity, statistics, model shapes, equal graph-model parameter counts, and optimization on a tiny batch | Real-data accuracy or superiority |
| Synthetic deep smoke test | Completed on CPU; 12 generated subjects, 480 trials, 64 channels, 640 samples at 160 Hz; one fold and two epochs | The EEGNet and graph-model training, checkpointing, prediction, and output path run end-to-end | EEG decoding performance; all samples are generated |
| Synthetic classical pipeline and label-shuffle control | Completed; shuffled-training-label results behaved as a chance-level canary on generated data | Baseline and leakage-canary code paths run | That real EEG labels contain a decodable effect |
| Synthetic report generation | Completed with synthetic warning in the report | The report and figure pipeline can consume predictions and label test data as synthetic | Scientific significance or real physiology |
| GitHub Actions | Passing software-validation workflow on the uploaded project; workflow reruns for project changes | Reproducible automated checks in the repository | Reproduction of the real-data experiment |
| Input hashes | ZIP SHA-256: d9d800ee3326eed3883fc9dec73ae51c3de114cf70e1217d9495fb845dcfc027; supplied notebook SHA-256: 565911b425043c5fe3dfd0079a02ebb373e512e8958f378ae45c437021d5191e | Identifies the supplied files used to prepare this project package | Integrity or completeness of a future PhysioNet result |

The [GitHub Actions history](https://github.com/krithika-bot/KRITHIKA/actions/workflows/eeg-gnn-project.yml) is the public record for automated software checks. The detailed local validation record is [docs/VALIDATION.md](VALIDATION.md).

### Evidence status

**Proven so far:** the software tests pass; the synthetic pipeline, label-shuffle control, and report generator run; the uploaded project has an automated CI workflow.

**Not proven yet:** real-data model performance, that any graph improves decoding, that the hypotheses are supported, statistical significance on EEG, or physiological ERD on the PhysioNet recordings. The real dataset run must finish before any of those claims are made.

## 11. Reproduction

From the project directory, install the declared dependencies and run the software checks:

    python -m pip install -e ".[test]"
    python tests/run_tests.py
    python scripts/run_deep.py --synthetic --smoke --out /tmp/eeg-gnn-smoke

To run the planned quick real-data study (downloads up to 20 eligible participants):

    python scripts/make_data_figures.py --n-subjects 20
    python scripts/run_baselines.py --n-subjects 20 --seeds 0 --out results/classical
    python scripts/run_baselines.py --n-subjects 20 --seeds 0 --out results/classical --permute-train-labels
    python scripts/run_deep.py --n-subjects 20 --seeds 0 --out results/deep --resume
    python scripts/make_summary.py --results results

The full configuration uses all eligible participants and three seeds. It can require a long download and substantial compute; the Colab notebook includes a resumable route. Do not run the real-data commands under a synthetic-results label.

The scripts create evidence artifacts such as participant and skipped-subject metadata in run_info.json, raw held-out predictions, training histories, summary.csv, comparisons.csv, summary.md, and figures. Review those files before reporting results. Do not commit the raw EDF dataset; keep the project code, configuration, predictions, and metadata sufficient to document the analysis, subject to the dataset's terms and the final project policy.

## 12. Limitations and completion checklist

- One public dataset and a two-class healthy-volunteer task; results would not automatically generalize to patients or other tasks.
- Five common irregular-timing/annotation IDs are excluded, and the loader may skip more participants after validation.
- The model family and hyperparameters are fixed for a controlled comparison; broad hyperparameter search has not been done.
- Correlation can reflect volume conduction and does not by itself establish functional connectivity.
- Synthetic signals contain a planted effect; they are deliberately suitable for checking software and cannot stand in for recorded EEG.
- This work is not clinically validated and must not be used for diagnosis or treatment.

Before calling the empirical study complete:

1. Finish the PhysioNet download and confirm the actual loaded participant/trial counts and any skips.
2. Run the configured baselines, permutation canary, graph models, and summary on real data.
3. Check saved run metadata, raw predictions, figures, and reproducibility from a clean environment.
4. Report the actual subject-wise estimates, uncertainty, comparisons, limitations, and any failed or skipped runs.
5. Update the portfolio and validation record only after those artifacts have been reviewed.

## 13. References

- PhysioNet. [EEG Motor Movement/Imagery Dataset, version 1.0.0](https://physionet.org/content/eegmmidb/1.0.0/). DOI: 10.13026/C28G6P.
- MNE-Python. [EEGBCI loader and run descriptions](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html).
- scikit-learn. [Cross-validation and grouped data](https://scikit-learn.org/stable/modules/cross_validation.html).
- Lawhern et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. *Journal of Neural Engineering*, 15(5). [DOI: 10.1088/1741-2552/aace8c](https://doi.org/10.1088/1741-2552/aace8c).
- Ramoser, Müller-Gerking & Pfurtscheller (2000). Optimal spatial filtering of single trial EEG during imagined hand movement. *IEEE Transactions on Rehabilitation Engineering*, 8(4). [DOI: 10.1109/10.842302](https://doi.org/10.1109/10.842302).
- Kipf & Welling (2017). Semi-Supervised Classification with Graph Convolutional Networks. [ICLR paper](https://arxiv.org/abs/1609.02907).
- Goldberger et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. *Circulation*, 101(23). [DOI: 10.1161/01.CIR.101.23.e215](https://doi.org/10.1161/01.CIR.101.23.e215).

## Portfolio-ready description

Implemented a subject-wise EEG motor-imagery research pipeline comparing classical baselines, EEGNet, and electrode-graph models, with tests for data handling, graph controls, and subject separation. Software checks pass; the planned PhysioNet real-data experiment is still pending, so no EEG performance result is claimed.
