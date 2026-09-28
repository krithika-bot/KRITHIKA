"""Synthetic time-series feature classification demonstration."""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def make_dataset(n_samples=600, seed=11):
    rng = np.random.default_rng(seed)
    rows = []
    labels = []

    for label, frequency in [(0, 6.0), (1, 14.0)]:
        for _ in range(n_samples // 2):
            t = np.linspace(0, 1, 250, endpoint=False)
            signal = np.sin(2 * np.pi * frequency * t)
            signal += 0.35 * rng.normal(size=t.size)

            rows.append([
                np.mean(np.abs(signal)),
                np.sqrt(np.mean(signal**2)),
                np.std(signal),
                np.max(signal) - np.min(signal),
            ])
            labels.append(label)

    return np.asarray(rows), np.asarray(labels)


def main():
    X, y = make_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print(f"Test accuracy on synthetic data: {accuracy_score(y_test, predictions):.3f}")
    print(classification_report(y_test, predictions, zero_division=0))


if __name__ == "__main__":
    main()
