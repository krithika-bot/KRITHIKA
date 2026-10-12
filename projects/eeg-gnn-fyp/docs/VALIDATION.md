# Software validation record

**Recorded:** 12 October 2026  
**Scope:** software behavior and a completed exploratory real-data pilot. See the pilot report for the limits of the empirical result.

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
