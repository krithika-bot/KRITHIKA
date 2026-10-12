# Full-cohort evidence index

This directory stores the derived evidence for the EEGMMIDB full eligible-cohort analysis. It does not contain the
raw PhysioNet EDF files or the local preprocessed cache. The final report interprets the aggregate results and limits
of the experiment in [`../../docs/FULL_COHORT_REPORT.md`](../../docs/FULL_COHORT_REPORT.md).

## Dataset provenance

- `provenance/dataset_audit.json` records the dataset version and DOI, participant inclusion/exclusion, preprocessing,
  software versions, device, source revision, and the hashes of the manifest and local cache.
- `provenance/edf_manifest.csv` records each downloaded EDF path, source checksum, and verified SHA-256. The 312 EDF
  files cover runs 4, 8, and 12 for 104 eligible participants; each checksum matched MNE-Python's checksum registry.
- The audit reports 4,680 epochs, 64 EEG channels, 640 samples at 160 Hz, 2,360 left-cue trials, and 2,320 right-cue
  trials. The local cache is intentionally excluded from version control.

## Analysis evidence

- `classical/preds.csv` and `classical/run_info.json`: CSP + LDA and log band-power logistic-regression held-out
  predictions and run settings.
- `classical_permuted/preds_permuted.csv` and `classical_permuted/run_info.json`: training-label-shuffle controls.
- `deep/preds.csv`: per-trial held-out predictions for EEGNet and the graph variants.
- `deep/histories.json`: per-run training histories and selected epochs.
- `summary.csv`, `comparisons.csv`, and `summary.md`: generated aggregate metrics and paired comparisons.
- `figures/`: generated method comparison, confusion matrices, graph illustrations, and exploratory signal sanity
  check. Figures are descriptive and should be read with the report's caveats.

The evaluation is participant-wise five-fold cross-validation with seeds 0, 1, and 2. Each test participant is held
out from fitting and early stopping. Data-driven correlation graphs are estimated using training-fold data only.
The label-shuffle outputs are pipeline canaries, not independent validation. The final report includes 11 paired
comparisons with Holm correction across the full family. The direct distance-versus-correlation graph comparison was
added during final exploratory review to complete H3 coverage; it was not pre-registered.

## Reproduction

From this project directory, download and verify the public EDF recordings, prepare the cache, run the experiments,
and regenerate the report artifacts with:

```bash
python scripts/download_physionet_verified.py
python scripts/make_data_figures.py --n-subjects 104
python scripts/run_baselines.py --n-subjects 104 --seeds 0 1 2 --out results/full_cohort/classical
python scripts/run_baselines.py --n-subjects 104 --seeds 0 1 2 --out results/full_cohort/classical_permuted --permute-train-labels
python scripts/run_deep.py --n-subjects 104 --seeds 0 1 2 --out results/full_cohort/deep --resume
python scripts/make_summary.py --results results/full_cohort
```

The deep run is compute-intensive; a compatible GPU is recommended. For the tested execution details, see the dataset
audit and validation record. Follow [PhysioNet's dataset licence and citation terms](https://physionet.org/content/eegmmidb/1.0.0/).
