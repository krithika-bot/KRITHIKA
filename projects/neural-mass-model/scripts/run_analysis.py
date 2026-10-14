#!/usr/bin/env python3
"""Run the reproducible Wilson-Cowan parameter study and generate evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from wilson_cowan import WilsonCowanParams, simulate, summarize  # noqa: E402


COLORS = ["#167d8d", "#d56a4a", "#6c63a8", "#548c5a"]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write an empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def svg_escape(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def chart_svg(
    title: str,
    x_label: str,
    y_label: str,
    series: list[dict[str, object]],
    *,
    width: int = 900,
    height: int = 500,
    x_bounds: tuple[float, float] | None = None,
    y_bounds: tuple[float, float] | None = None,
    x_ticks: int = 6,
    y_ticks: int = 5,
) -> str:
    """Create a compact standalone SVG line chart without third-party tools."""
    left, right, top, bottom = 88, width - 36, 76, height - 78
    all_x = [float(x) for item in series for x in item["x"]]
    all_y = [float(y) for item in series for y in item["y"]]
    x0, x1 = x_bounds or (min(all_x), max(all_x))
    y0, y1 = y_bounds or (min(0.0, min(all_y)), max(all_y))
    if x1 <= x0:
        x1 = x0 + 1.0
    if y1 <= y0:
        y1 = y0 + 1.0
    y_pad = 0.06 * (y1 - y0) if y_bounds is None else 0.0
    y0 -= y_pad
    y1 += y_pad

    def px(value: float) -> float:
        return left + (value - x0) / (x1 - x0) * (right - left)

    def py(value: float) -> float:
        return bottom - (value - y0) / (y1 - y0) * (bottom - top)

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{svg_escape(title)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2:.1f}" y="34" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#18232d">{svg_escape(title)}</text>',
    ]
    for tick in range(x_ticks + 1):
        value = x0 + (x1 - x0) * tick / x_ticks
        x = px(value)
        pieces.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" stroke="#e8ecef"/>')
        pieces.append(f'<text x="{x:.2f}" y="{bottom + 23}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#53616b">{value:.3g}</text>')
    for tick in range(y_ticks + 1):
        value = y0 + (y1 - y0) * tick / y_ticks
        y = py(value)
        pieces.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#e8ecef"/>')
        pieces.append(f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial,sans-serif" font-size="12" fill="#53616b">{value:.3g}</text>')
    pieces.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#52616b" stroke-width="1.3"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#52616b" stroke-width="1.3"/>',
        f'<text x="{(left + right) / 2:.1f}" y="{height - 20}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="#26343d">{svg_escape(x_label)}</text>',
        f'<text x="23" y="{(top + bottom) / 2:.1f}" text-anchor="middle" transform="rotate(-90 23 {(top + bottom) / 2:.1f})" font-family="Arial,sans-serif" font-size="14" fill="#26343d">{svg_escape(y_label)}</text>',
    ])
    legend_x = left + 8
    for idx, item in enumerate(series):
        coordinates = " ".join(f"{px(float(x)):.2f},{py(float(y)):.2f}" for x, y in zip(item["x"], item["y"]))
        color = str(item.get("color", COLORS[idx % len(COLORS)]))
        pieces.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
        if item.get("markers"):
            for x, y in zip(item["x"], item["y"]):
                pieces.append(f'<circle cx="{px(float(x)):.2f}" cy="{py(float(y)):.2f}" r="3.4" fill="{color}"/>')
        pieces.append(f'<line x1="{legend_x}" y1="{top - 20}" x2="{legend_x + 24}" y2="{top - 20}" stroke="{color}" stroke-width="3"/>')
        pieces.append(f'<text x="{legend_x + 31}" y="{top - 16}" font-family="Arial,sans-serif" font-size="12" fill="#34434d">{svg_escape(item["label"])}</text>')
        legend_x += 42 + len(str(item["label"])) * 7
    pieces.append("</svg>")
    return "\n".join(pieces)


def write_svg(path: Path, *args: object, **kwargs: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chart_svg(*args, **kwargs), encoding="utf-8")


def output_row(parameter: str, value: float, params: WilsonCowanParams,
               duration_ms: float, tail_ms: float, dt_ms: float) -> dict[str, object]:
    trajectory = simulate(
        params, duration_ms, dt_ms,
        record_from_ms=duration_ms - tail_ms,
        sample_every_ms=dt_ms,
    )
    metrics = summarize(trajectory)
    return {
        "parameter": parameter,
        "value": value,
        "p": params.p,
        "mean_e": metrics["mean_e"],
        "e_amplitude": metrics["e_amplitude"],
        "i_amplitude": metrics["i_amplitude"],
        "period_ms": metrics["period_ms"] or "",
        "frequency_hz": metrics["frequency_hz"] or "",
        "peak_count": metrics["peak_count"],
        "status": metrics["status"],
    }


def build_evidence(out: Path) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    figures = out / "figures"
    base = WilsonCowanParams()

    # Baseline time series and phase-plane trace use the source's Figure 11 case.
    baseline_full = simulate(base, 2000.0, 0.1, sample_every_ms=1.0)
    baseline_tail = simulate(base, 2000.0, 0.1, record_from_ms=1500.0, sample_every_ms=0.1)
    baseline_metrics = summarize(baseline_tail)
    write_csv(out / "baseline_timeseries.csv", [
        {"time_ms": time_ms, "E": e, "I": i}
        for time_ms, e, i in baseline_full
    ])
    write_svg(
        figures / "baseline_timeseries.svg",
        "Wilson–Cowan baseline: population activity",
        "Time (ms)", "Activity (dimensionless)",
        [
            {"label": "E: excitatory", "x": [r[0] for r in baseline_full], "y": [r[1] for r in baseline_full], "color": COLORS[0]},
            {"label": "I: inhibitory", "x": [r[0] for r in baseline_full], "y": [r[2] for r in baseline_full], "color": COLORS[1]},
        ], x_bounds=(0.0, 2000.0), y_bounds=(0.0, 0.5),
    )
    write_svg(
        figures / "baseline_phase_plane.svg",
        "Baseline phase-plane trajectory",
        "Excitatory activity E", "Inhibitory activity I",
        [{"label": "trajectory", "x": [r[1] for r in baseline_full], "y": [r[2] for r in baseline_full], "color": COLORS[2]}],
        x_bounds=(0.0, 0.5), y_bounds=(0.0, 0.5),
    )

    # Independent-drive scan. The long run allows near-critical transients to decay.
    drive_rows: list[dict[str, object]] = []
    for index in range(35):
        p_value = round(0.8 + 0.05 * index, 2)
        params = base.with_changes(p=p_value)
        tail = simulate(params, 10000.0, 0.1, record_from_ms=9000.0, sample_every_ms=0.1)
        metrics = summarize(tail)
        drive_rows.append({
            "p": p_value,
            "mean_e": metrics["mean_e"],
            "e_amplitude": metrics["e_amplitude"],
            "i_amplitude": metrics["i_amplitude"],
            "period_ms": metrics["period_ms"] or "",
            "frequency_hz": metrics["frequency_hz"] or "",
            "peak_count": metrics["peak_count"],
            "status": metrics["status"],
        })
    write_csv(out / "drive_sweep.csv", drive_rows)
    drive_x = [float(row["p"]) for row in drive_rows]
    write_svg(
        figures / "drive_amplitude.svg",
        "Excitatory oscillation amplitude across external drive",
        "External drive P", "E peak-to-peak amplitude",
        [{"label": "E amplitude", "x": drive_x, "y": [float(r["e_amplitude"]) for r in drive_rows], "color": COLORS[0], "markers": True}],
        x_bounds=(0.8, 2.5), y_bounds=(0.0, 0.2),
    )
    frequency_points = [row for row in drive_rows if row["frequency_hz"] != ""]
    write_svg(
        figures / "drive_frequency.svg",
        "Oscillation frequency where a limit cycle is resolved",
        "External drive P", "Frequency (Hz)",
        [{"label": "frequency", "x": [float(r["p"]) for r in frequency_points], "y": [float(r["frequency_hz"]) for r in frequency_points], "color": COLORS[1], "markers": True}],
        x_bounds=(0.8, 2.5), y_bounds=(0.0, 60.0),
    )

    # One-at-a-time coupling sensitivity at the published baseline drive.
    coupling_rows: list[dict[str, object]] = []
    coupling_values = {
        "c2": [6, 8, 10, 12, 14, 16, 18],
        "c3": [8, 10, 12, 15, 18, 21, 24],
        "c4": [1, 2, 3, 4, 5, 6],
    }
    for parameter, values in coupling_values.items():
        for value in values:
            params = base.with_changes(**{parameter: float(value)})
            coupling_rows.append(output_row(parameter, float(value), params, 4000.0, 1000.0, 0.1))
    write_csv(out / "coupling_sweeps.csv", coupling_rows)
    for idx, parameter in enumerate(("c2", "c3", "c4")):
        rows = [row for row in coupling_rows if row["parameter"] == parameter]
        values = [float(row["value"]) for row in rows]
        write_svg(
            figures / f"coupling_{parameter}.svg",
            f"E amplitude while varying {parameter}",
            f"{parameter} coupling coefficient", "E peak-to-peak amplitude",
            [{
                "label": f"vary {parameter}",
                "x": values,
                "y": [float(row["e_amplitude"]) for row in rows],
                "color": COLORS[idx],
                "markers": True,
            }],
            x_bounds=(min(values), max(values)), y_bounds=(0.0, 0.35),
        )

    # Timestep sensitivity plus an exact deterministic replay check.
    timestep_rows: list[dict[str, object]] = []
    step_metrics: dict[float, dict[str, float | int | str]] = {}
    for dt_ms in (0.2, 0.1, 0.05):
        trace = simulate(base, 2000.0, dt_ms, record_from_ms=1500.0, sample_every_ms=dt_ms)
        metrics = summarize(trace)
        step_metrics[dt_ms] = metrics
    reference = step_metrics[0.05]
    for dt_ms in (0.2, 0.1, 0.05):
        metrics = step_metrics[dt_ms]
        ref_frequency = float(reference["frequency_hz"])
        ref_amplitude = float(reference["e_amplitude"])
        timestep_rows.append({
            "dt_ms": dt_ms,
            "e_amplitude": metrics["e_amplitude"],
            "period_ms": metrics["period_ms"] or "",
            "frequency_hz": metrics["frequency_hz"] or "",
            "frequency_difference_vs_0.05_pct": abs(float(metrics["frequency_hz"]) - ref_frequency) / ref_frequency * 100.0,
            "amplitude_difference_vs_0.05_pct": abs(float(metrics["e_amplitude"]) - ref_amplitude) / ref_amplitude * 100.0,
        })
    write_csv(out / "timestep_sensitivity.csv", timestep_rows)
    repeat = summarize(simulate(base, 2000.0, 0.1, record_from_ms=1500.0, sample_every_ms=0.1))
    deterministic_replay = (
        repeat["e_amplitude"] == step_metrics[0.1]["e_amplitude"]
        and repeat["frequency_hz"] == step_metrics[0.1]["frequency_hz"]
    )

    latest_cycle = max(
        (row for row in drive_rows if row["status"] == "limit_cycle"),
        key=lambda row: float(row["p"]),
    )
    first_cycle = min(
        (row for row in drive_rows if row["status"] == "limit_cycle"),
        key=lambda row: float(row["p"]),
    )
    metadata = {
        "project": "Neural Mass Model: Wilson-Cowan two-population study",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "implementation": "Python standard library only; classical fourth-order Runge-Kutta (RK4)",
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "dataset": None,
        "data_note": "All output is deterministic simulation from the documented equations; no EEG, human, or clinical data were used.",
        "model_source": "Wilson, H. R., & Cowan, J. D. (1972). Biophysical Journal, 12(1), 1-24. https://doi.org/10.1016/S0006-3495(72)86068-5",
        "baseline_parameters": base.__dict__,
        "baseline_duration_ms": 2000.0,
        "baseline_dt_ms": 0.1,
        "baseline_initial_state": [0.02, 0.02],
        "drive_sweep": {"p_values": [0.8, 2.5, 0.05], "duration_ms": 10000.0, "tail_window_ms": 1000.0, "classification_amplitude_threshold": 0.01},
        "coupling_sweeps": {"parameters": coupling_values, "duration_ms": 4000.0, "tail_window_ms": 1000.0},
        "numerical_checks": {
            "timesteps_ms": [0.2, 0.1, 0.05],
            "reference_timestep_ms": 0.05,
            "deterministic_replay_equal": deterministic_replay,
        },
        "drive_scan_first_resolved_cycle_p": first_cycle["p"],
        "drive_scan_last_resolved_cycle_p": latest_cycle["p"],
        "interpretation_limit": "Qualitative software simulation only; not a fitted model, real EEG result, biological validation, or clinical finding.",
    }
    (out / "run_info.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    checksum_lines = [
        f"{sha256_file(path)}  {path.relative_to(out).as_posix()}"
        for path in sorted(out.rglob("*"))
        if path.is_file() and path.name != "checksums.sha256"
    ]
    (out / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return {
        "baseline": baseline_metrics,
        "first_cycle": first_cycle,
        "last_cycle": latest_cycle,
        "timestep_rows": timestep_rows,
        "coupling_rows": coupling_rows,
        "drive_rows": drive_rows,
        "deterministic_replay": deterministic_replay,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "results", help="directory for CSV, JSON and SVG evidence")
    args = parser.parse_args()
    result = build_evidence(args.out.resolve())
    baseline = result["baseline"]
    print(f"Wrote evidence to {args.out.resolve()}")
    print(f"Baseline: {baseline['frequency_hz']:.3f} Hz, E amplitude {baseline['e_amplitude']:.6f}")
    print(f"Resolved cycles in P scan: {result['first_cycle']['p']} to {result['last_cycle']['p']}")
    print(f"Exact deterministic replay: {result['deterministic_replay']}")
    for row in result["timestep_rows"]:
        print(f"dt={row['dt_ms']:.2f} ms: {row['frequency_hz']:.3f} Hz, amplitude error vs 0.05 ms={row['amplitude_difference_vs_0.05_pct']:.4f}%")


if __name__ == "__main__":
    main()
