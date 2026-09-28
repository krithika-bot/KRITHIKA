"""Basic signal-processing demonstration using synthetic data only."""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt


FS = 250  # Hz
DURATION = 10  # seconds


def bandpass_filter(signal, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)


def main():
    rng = np.random.default_rng(42)
    time = np.arange(0, DURATION, 1 / FS)

    # Synthetic oscillatory component plus Gaussian noise.
    clean = np.sin(2 * np.pi * 10 * time)
    noisy = clean + 0.7 * rng.normal(size=time.size)
    filtered = bandpass_filter(noisy, 5, 30, FS)

    rms = np.sqrt(np.mean(filtered**2))
    mean_abs = np.mean(np.abs(filtered))

    print(f"Samples: {len(time)}")
    print(f"Sampling rate: {FS} Hz")
    print(f"Filtered RMS: {rms:.4f}")
    print(f"Filtered mean absolute value: {mean_abs:.4f}")

    plt.figure(figsize=(10, 5))
    plt.plot(time, noisy, label="Synthetic noisy signal", alpha=0.6)
    plt.plot(time, filtered, label="Band-pass filtered signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (a.u.)")
    plt.title("Basic Physiological-Signal Processing Demonstration")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
