# Real-data pilot evidence package

This directory contains the completed exploratory PhysioNet EEGMMIDB pilot: 20 participants, 900 trials, five participant-wise folds, and three seeds. The full method and interpretation are in [REAL_DATA_PILOT_REPORT.md](../../docs/REAL_DATA_PILOT_REPORT.md).

## Key result

CSP + LDA achieved 55.8% mean participant accuracy (95% participant-bootstrap CI 52.1–59.6%). The distance-graph GCN achieved 53.7% (52.1–55.3%); its paired difference from the identity graph control was −1.8 percentage points (Holm-adjusted p = 0.300). No reported comparison remained significant after Holm correction. The pilot does not show that the spatial graph improves cross-participant decoding.

## Files

- summary.csv and comparisons.csv: machine-readable metrics and paired comparisons.
- summary.md: generated summary with method-comparison and confusion-matrix figures.
- classical/, classical_permuted/, deep/: held-out trial predictions and exact run configuration; deep/ also has epoch-level training histories.
- figures/: data-sanity, graph, learning-curve, method-comparison and confusion-matrix images.
- provenance/dataset_audit.json: participant/trial counts, preprocessing, package versions and cache hash.
- provenance/edf_manifest.csv: the 60 EDF filenames and their verified SHA-256 digests.

The raw EDFs and local preprocessed cache are intentionally excluded. The manifest and audit provide provenance without redistributing the dataset. Source dataset: [PhysioNet EEGMMIDB](https://physionet.org/content/eegmmidb/1.0.0/), DOI 10.13026/C28G6P; follow its ODC Attribution License.
