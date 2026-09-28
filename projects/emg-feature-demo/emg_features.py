"""Time-domain feature extraction from a synthetic EMG-like signal."""

import numpy as np


FS = 1000  # Hz
DURATION = 5  # seconds


def generate_synthetic_emg(fs=FS, duration=DURATION, seed=7):
    rng = np.random.default_rng(seed)
    n = int(fs * duration)
    time = np.arange(n) / fs

    # A simple amplitude-modulated noise process for demonstration.
    envelope = 0.5 + 0.5 * (np.sin(2 * np.pi * 0.5 * time) ** 2)
    signal = envelope * rng.normal(0, 1, size=n)
    return time, signal


def extract_features(signal):
    return {
        "mean_absolute_value": float(np.mean(np.abs(signal))),
        "rms": float(np.sqrt(np.mean(signal**2))),
        "standard_deviation": float(np.std(signal)),
        "peak_to_peak": float(np.ptp(signal)),
    }


def main():
    time, signal = generate_synthetic_emg()
    features = extract_features(signal)

    print(f"Duration: {time[-1]:.3f} s")
    print(f"Sampling rate: {FS} Hz")
    for name, value in features.items():
        print(f"{name}: {value:.4f}")


if __name__ == "__main__":
    main()
