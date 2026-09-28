# Signal Processing Basics

A small, reproducible Python project demonstrating a basic physiological-signal workflow using **synthetic data**.

## Purpose

This project is intentionally educational. It demonstrates how a noisy time-series can be generated, filtered, segmented, and summarized before any machine-learning step.

## Pipeline

Synthetic signal → noise → band-pass filtering → time-domain features → visualization

## Skills demonstrated

- Python
- NumPy
- SciPy
- Matplotlib
- Time-series analysis
- Digital filtering
- Feature extraction
- Reproducible research practice

## Important note

The data in this repository are synthetic. They are **not human EEG/EMG recordings**, and the project makes no clinical claims.

## Run

```bash
pip install -r requirements.txt
python signal_pipeline.py
```

## Next step

Replace the synthetic input with a properly documented public EEG or EMG dataset and add dataset-specific preprocessing and validation.
