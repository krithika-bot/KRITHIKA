# Software validation record

**Recorded:** 12 October 2026  
**Scope:** software behavior, an earlier exploratory pilot, and the completed full eligible-cohort real-data analysis. The full-cohort analysis record below was added 13 October 2026.

See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for the project concept, dataset, toolchain, method details, code map, and evidence boundaries.

## Input provenance

- Source archive: `eeg-gnn-fyp.zip` (SHA-256 `d9d800ee3326eed3883fc9dec73ae51c3de114cf70e1217d9495fb845dcfc027`).
- Colab notebook: `run_on_colab.ipynb` (SHA-256 `565911b425043c5fe3dfd0079a02ebb373e512e8958f378ae45c437021d5191e`).
- The notebook embedded in the ZIP has the same SHA-256 as the separately supplied notebook.

## Environment

Validation ran in an isolated Python 3.12.14 environment with NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6,
scikit-learn 1.9.1, Matplotlib 3.11.2, PyYAML 6.0.3, MNE 1.13.2, PyTorch 2.14.1, and pytest 9.1.1.

## Checks completed

| Check | Outcome | What it establishes |
|---|---|---|
| `python tests/run_tests.py` | 13 passed, 0 failed | Data/cache shapes, fold separation, graph properties, preprocessing, statistical helpers, classical synthetic controls, neural model shapes, equal graph-model parameter counts, and a tiny-batch optimization check. |
| `python scripts/run_deep.py --synthetic --smoke --out <temporary-directory>` | Completed on CPU | The deep-model path ran one small fold on generated test data for EEGNet and three graph variants. The generated data are synthetic; its scores are not research findings. |
| `python scripts/make_summary.py --results <synthetic-run> --synthetic` | Completed | The report and figure-generation path accepts prediction files and stamps the output as synthetic test data. |

The smoke run used 12 synthetic subjects, 480 trials, 64 channels, and 640 time samples at 160 Hz. It ran for two
epochs and one test fold. This is a wiring check, not an estimate of performance on EEG recordings.

## Real-data pilot completed

PhysioNet EEGMMIDB v1.0.0 recordings for participants S001–S020 and runs 4, 8, and 12 were processed. All 60 EDF files passed SHA-256 verification against MNE-Python's bundled checksum registry. The resulting dataset had 900 trials, 64 channels, 640 samples at 160 Hz, and class counts 455 left / 445 right. No participant in this subset was skipped.

The run used five participant-wise folds and seeds 0, 1, and 2. It completed two classical baselines, two training-label-shuffle controls, EEGNet, and five GCN adjacency variants. It ran on CPU with the package versions recorded in each run_info.json. The source revision was 34e42589aa4c0e1c540f9b4e631dc2ecf06265c5.

Key outcome: CSP + LDA reached 55.8% mean participant accuracy (95% bootstrap CI 52.1–59.6%); the distance-graph GCN reached 53.7% (52.1–55.3%). The distance graph did not outperform the identity control after Holm correction (adjusted p = 0.300). No reported comparison remained significant after correction. The label-shuffle controls were near chance. Full results and evidence are in [REAL_DATA_PILOT_REPORT.md](REAL_DATA_PILOT_REPORT.md) and [results/real_data_pilot](../results/real_data_pilot/README.md).

An earlier quick attempt had been interrupted during EDF download. That failure was superseded by the checksum-verified pilot above. Raw EDF recordings and the derived cache are not included in this repository; the manifest and audit retain provenance without redistributing data.

## Full-cohort real-data analysis completed

The full eligible-cohort run processed EEGMMIDB v1.0.0 runs 4, 8, and 12 for 104 participants. All 312 EDF files
passed SHA-256 verification against MNE-Python's checksum registry. The resulting dataset had 4,680 trials (2,360
left-cue and 2,320 right-cue), 64 channels, and 640 samples at 160 Hz. No eligible participant was skipped. Full
provenance is recorded in [the dataset audit](../results/full_cohort/provenance/dataset_audit.json) and
[checksum manifest](../results/full_cohort/provenance/edf_manifest.csv).

The evaluation completed five participant-wise folds for seeds 0, 1, and 2. It produced 90 deep model/fold
predictions (EEGNet plus five graph variants), 30 classical baseline fits, and 30 training-label-shuffle fits.
Completeness review confirmed 4,680 unique held-out trial predictions for every method and seed, all 104 subjects,
all five folds, and 90 matching deep training histories. The repository contains 140,400 held-out prediction rows
across the ten methods and three seeds, plus run metadata, generated summaries, and figures. The local execution used
CPU on macOS 15.6.1 arm64 with Python 3.12.7, MNE 1.13.2, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6,
scikit-learn 1.9.1, PyTorch 2.14.1, and Matplotlib 3.11.2. Exact run settings are saved in each `run_info.json`.

EEGNet had the highest mean participant accuracy, 70.1% (95% participant-bootstrap CI 67.9–72.4%). CSP + LDA
reached 61.9% (59.4–64.4%). The distance-graph GCN reached 56.9% (55.4–58.5%), 1.2 percentage points below
the identity control (58.1%; 95% paired bootstrap interval −2.2 to −0.3 points; Holm-adjusted p = 0.053), which
did not cross the 0.05 threshold after correction. The distance graph also did not significantly differ from the
degree-matched random or training-only correlation graphs after correction. Training-label-shuffle controls were
near chance. These are cross-validation estimates from one dataset and fixed configuration;
they do not establish external generalization, clinical value, or a universal claim about graph learning.

See the [full-cohort report](FULL_COHORT_REPORT.md), [generated summary](../results/full_cohort/summary.md),
[paired comparison table](../results/full_cohort/comparisons.csv), and [evidence index](../results/full_cohort/README.md).
Raw EDF files and the derived cache are excluded from the repository.

## Re-run the software checks

```bash
pip install -e ".[test]"
python tests/run_tests.py
python scripts/run_deep.py --synthetic --smoke --out /tmp/eeg-gnn-smoke
python scripts/run_baselines.py --synthetic --seeds 0 --out /tmp/eeg-gnn-smoke/classical
python scripts/make_summary.py --results /tmp/eeg-gnn-smoke --synthetic
```

Keep synthetic outputs labelled as pipeline tests. For future cohort expansions, update the result status only
after predictions, configuration, run metadata, summary, and figures have been reviewed.
