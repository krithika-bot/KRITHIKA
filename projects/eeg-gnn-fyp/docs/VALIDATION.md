# Software validation record

**Recorded:** 12 October 2026  
**Scope:** software behavior only; this is not evidence of EEG decoding performance.

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

## Real-data status

The PhysioNet EEGMMIDB quick run did not complete in this environment. The first EDF download was interrupted
before a usable dataset was available. No real EEG files were processed, no real-data predictions were generated,
and no scientific result or conclusion is reported here. The dataset files are not included in this repository;
the MNE loader retrieves them from PhysioNet when a full run is performed.

## Re-run the software checks

```bash
pip install -e ".[test]"
python tests/run_tests.py
python scripts/run_deep.py --synthetic --smoke --out /tmp/eeg-gnn-smoke
python scripts/run_baselines.py --synthetic --seeds 0 --out /tmp/eeg-gnn-smoke/classical
python scripts/make_summary.py --results /tmp/eeg-gnn-smoke --synthetic
```

Keep synthetic outputs labelled as pipeline tests. Only update the project’s result status after a real-data run
has completed and its raw predictions, configuration, run metadata, summary, and figures have been reviewed.
