# Time-Series Machine Learning Demonstration

A small reproducible machine-learning example showing how engineered time-domain features can be passed into a classifier.

## Pipeline

Synthetic time-series → windowing → feature extraction → train/test split → classifier → evaluation

## Skills demonstrated

- Python
- NumPy
- scikit-learn
- Feature engineering
- Classification
- Train/test separation
- Reproducible evaluation

## Important note

This project uses synthetic data only. The labels are artificial demonstration labels, not physiological diagnoses or real human states. The model should not be interpreted as a neuroscience or medical model.

## Run

```bash
pip install -r requirements.txt
python ml_pipeline.py
```

## Research extension

The next scientifically meaningful step would be to repeat the pipeline on an appropriate public EEG/EMG dataset, document preprocessing, define the prediction target from the dataset, and evaluate generalization with subject-aware validation where appropriate.
