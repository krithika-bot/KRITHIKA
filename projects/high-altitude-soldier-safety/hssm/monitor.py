"""Transparent, non-diagnostic logic for the offline demonstrator.

This module does not infer medical conditions or determine fitness/safety.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Sample:
    timestamp: str
    signal_quality: float | None
    heart_rate_bpm: float | None = None
    surface_temp_c: float | None = None
    motion_rms_g: float | None = None
    check_in: str = "none"


@dataclass(frozen=True)
class Decision:
    timestamp: str
    status: str
    message: str
    signal_quality: float | None
    logged_fields: dict[str, float | None]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_sample(sample: Sample, quality_floor: float = 0.75) -> Decision:
    """Return a generic engineering prompt, never a disease label.

    `quality_floor` is a configurable software-demo parameter, not a medical
    threshold. A low/absent quality score prevents the software from treating
    the supplied measurements as reliable.
    """
    if not 0.0 <= quality_floor <= 1.0:
        raise ValueError("quality_floor must be between 0 and 1")
    if sample.signal_quality is None or not 0.0 <= sample.signal_quality <= 1.0:
        status = "SIGNAL_UNRELIABLE"
        message = "Reading unavailable or invalid; re-check sensor placement and repeat."
    elif sample.signal_quality < quality_floor:
        status = "SIGNAL_UNRELIABLE"
        message = "Signal quality is low; re-check sensor placement and repeat."
    elif sample.check_in.strip().lower() == "concern":
        status = "CHECK_IN_REQUESTED"
        message = "Wearer check-in marked concern; follow the appropriate human support process."
    else:
        status = "TREND_RECORDED"
        message = "Signal passed the configured software quality gate; this is not an all-clear."

    return Decision(
        timestamp=sample.timestamp,
        status=status,
        message=message,
        signal_quality=sample.signal_quality,
        logged_fields={
            "heart_rate_bpm": sample.heart_rate_bpm,
            "surface_temp_c": sample.surface_temp_c,
            "motion_rms_g": sample.motion_rms_g,
        },
    )


def load_kg_from_raw(raw_count: float, zero_count: float, counts_per_kg: float) -> float:
    """Convert a load-cell count into kg using a user calibration.

    This is a conversion helper only. Accuracy depends on a real calibration
    and mechanical setup; this function does not establish either.
    """
    if counts_per_kg <= 0:
        raise ValueError("counts_per_kg must be positive")
    if raw_count < 0 or zero_count < 0:
        raise ValueError("raw_count and zero_count must be non-negative")
    return max(0.0, (raw_count - zero_count) / counts_per_kg)


def load_status(load_kg: float, advisory_limit_kg: float) -> str:
    """Compare load with a user-set study limit; no ergonomics claim is made."""
    if load_kg < 0 or advisory_limit_kg <= 0:
        raise ValueError("load must be non-negative and advisory limit positive")
    return "ABOVE_USER_SET_LIMIT" if load_kg > advisory_limit_kg else "WITHIN_USER_SET_LIMIT"
