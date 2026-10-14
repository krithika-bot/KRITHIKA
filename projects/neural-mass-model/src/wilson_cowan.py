"""Minimal deterministic Wilson-Cowan excitatory/inhibitory population model.

The equations follow the time-coarse-grained form in Wilson & Cowan (1972),
Eq. 12. This module intentionally uses only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import exp


@dataclass(frozen=True)
class WilsonCowanParams:
    """Parameters for one local excitatory/inhibitory population pair.

    Couplings, inputs, slopes, and thresholds use the dimensionless model
    convention of the cited paper. Time constants are in milliseconds.
    """

    c1: float = 16.0
    c2: float = 12.0
    c3: float = 15.0
    c4: float = 3.0
    a_e: float = 1.3
    theta_e: float = 4.0
    a_i: float = 2.0
    theta_i: float = 3.7
    r_e: float = 1.0
    r_i: float = 1.0
    tau_e_ms: float = 8.0
    tau_i_ms: float = 8.0
    p: float = 1.25
    q: float = 0.0

    def with_changes(self, **changes: float) -> "WilsonCowanParams":
        """Return a copy with selected parameters changed."""
        return replace(self, **changes)


def sigmoid(x: float) -> float:
    """Numerically stable logistic sigmoid."""
    if x >= 0.0:
        z = exp(-x)
        return 1.0 / (1.0 + z)
    z = exp(x)
    return z / (1.0 + z)


def shifted_logistic(x: float, slope: float, threshold: float) -> float:
    """Logistic response shifted so that its value at zero input is zero."""
    return sigmoid(slope * (x - threshold)) - sigmoid(-slope * threshold)


def maximum_response(slope: float, threshold: float) -> float:
    """Maximum of the shifted response function, used as k_e or k_i."""
    return 1.0 - sigmoid(-slope * threshold)


def derivatives(
    e: float, i: float, params: WilsonCowanParams
) -> tuple[float, float]:
    """Return dE/dt and dI/dt in activity units per millisecond."""
    drive_e = params.c1 * e - params.c2 * i + params.p
    drive_i = params.c3 * e - params.c4 * i + params.q
    response_e = shifted_logistic(drive_e, params.a_e, params.theta_e)
    response_i = shifted_logistic(drive_i, params.a_i, params.theta_i)
    k_e = maximum_response(params.a_e, params.theta_e)
    k_i = maximum_response(params.a_i, params.theta_i)
    de = (-e + (k_e - params.r_e * e) * response_e) / params.tau_e_ms
    di = (-i + (k_i - params.r_i * i) * response_i) / params.tau_i_ms
    return de, di


def rk4_step(
    e: float, i: float, params: WilsonCowanParams, dt_ms: float
) -> tuple[float, float]:
    """Advance one classical fourth-order Runge-Kutta step."""
    k1e, k1i = derivatives(e, i, params)
    k2e, k2i = derivatives(e + 0.5 * dt_ms * k1e, i + 0.5 * dt_ms * k1i, params)
    k3e, k3i = derivatives(e + 0.5 * dt_ms * k2e, i + 0.5 * dt_ms * k2i, params)
    k4e, k4i = derivatives(e + dt_ms * k3e, i + dt_ms * k3i, params)
    next_e = e + dt_ms * (k1e + 2.0 * k2e + 2.0 * k3e + k4e) / 6.0
    next_i = i + dt_ms * (k1i + 2.0 * k2i + 2.0 * k3i + k4i) / 6.0
    return next_e, next_i


def simulate(
    params: WilsonCowanParams,
    duration_ms: float,
    dt_ms: float = 0.1,
    initial_state: tuple[float, float] = (0.02, 0.02),
    record_from_ms: float = 0.0,
    sample_every_ms: float | None = None,
) -> list[tuple[float, float, float]]:
    """Integrate the model and return sampled (time, E, I) rows.

    Integration always uses ``dt_ms``. ``sample_every_ms`` only controls the
    recorded output interval, and must be an integer multiple of the step.
    ``record_from_ms`` lets sweeps retain the asymptotic tail only.
    """
    if duration_ms <= 0.0 or dt_ms <= 0.0:
        raise ValueError("duration_ms and dt_ms must be positive")
    steps = round(duration_ms / dt_ms)
    if abs(steps * dt_ms - duration_ms) > 1e-9:
        raise ValueError("duration_ms must be an integer multiple of dt_ms")
    stride = 1 if sample_every_ms is None else round(sample_every_ms / dt_ms)
    if stride < 1 or abs(stride * dt_ms - (sample_every_ms or dt_ms)) > 1e-9:
        raise ValueError("sample_every_ms must be a positive integer multiple of dt_ms")
    if not 0.0 <= record_from_ms <= duration_ms:
        raise ValueError("record_from_ms must be within the simulated interval")

    e, i = initial_state
    rows: list[tuple[float, float, float]] = []
    if record_from_ms == 0.0:
        rows.append((0.0, e, i))
    for step in range(1, steps + 1):
        e, i = rk4_step(e, i, params, dt_ms)
        time_ms = step * dt_ms
        after_start = time_ms + 1e-12 >= record_from_ms
        if after_start and (step % stride == 0 or step == steps):
            rows.append((time_ms, e, i))
    return rows


def summarize(
    rows: list[tuple[float, float, float]],
    oscillation_amplitude_threshold: float = 0.01,
) -> dict[str, float | int | str]:
    """Summarize a trajectory and estimate frequency for clear limit cycles.

    Frequency is intentionally omitted below the declared E-amplitude
    threshold, avoiding spurious peak estimates from a nearly flat trace.
    """
    if len(rows) < 3:
        raise ValueError("at least three samples are required for a summary")
    times = [row[0] for row in rows]
    es = [row[1] for row in rows]
    ins = [row[2] for row in rows]
    e_min, e_max = min(es), max(es)
    i_min, i_max = min(ins), max(ins)
    e_amplitude = e_max - e_min
    i_amplitude = i_max - i_min
    mean_e = sum(es) / len(es)
    peaks: list[float] = []
    if e_amplitude >= oscillation_amplitude_threshold:
        peak_floor = e_min + 0.2 * e_amplitude
        for index in range(1, len(es) - 1):
            if es[index - 1] < es[index] >= es[index + 1] and es[index] > peak_floor:
                peaks.append(times[index])
    periods = [right - left for left, right in zip(peaks, peaks[1:])]
    period_ms = sum(periods) / len(periods) if len(periods) >= 2 else None
    frequency_hz = 1000.0 / period_ms if period_ms else None
    if e_amplitude < oscillation_amplitude_threshold:
        status = "steady_state"
    elif frequency_hz is not None:
        status = "limit_cycle"
    else:
        status = "unresolved"
    return {
        "mean_e": mean_e,
        "e_min": e_min,
        "e_max": e_max,
        "e_amplitude": e_amplitude,
        "i_min": i_min,
        "i_max": i_max,
        "i_amplitude": i_amplitude,
        "period_ms": period_ms,
        "frequency_hz": frequency_hz,
        "peak_count": len(peaks),
        "status": status,
    }

