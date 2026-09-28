# EMG Feature Demonstration

An educational Python example showing how common time-domain features can be calculated from a **synthetic EMG-like signal**.

## Features

- Mean absolute value (MAV)
- Root mean square (RMS)
- Standard deviation
- Signal length and sampling rate

## Why this matters

Surface EMG is a time-varying physiological signal. Before building a predictive model, a researcher needs a reproducible way to preprocess the signal and describe its properties.

## Important note

The signal is simulated for learning and software demonstration. It is not a clinical measurement and does not represent a real participant.

## Run

```bash
pip install -r requirements.txt
python emg_features.py
```
