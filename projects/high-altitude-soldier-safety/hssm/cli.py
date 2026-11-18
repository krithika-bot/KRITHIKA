"""Run the synthetic/local CSV demonstration without network access."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .monitor import Sample, evaluate_sample


def _optional_float(value: str) -> float | None:
    value = value.strip()
    return None if value == "" else float(value)


def run(input_path: Path, output_path: Path, quality_floor: float = 0.75) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with input_path.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {"timestamp", "signal_quality", "check_in"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        with output_path.open("w", encoding="utf-8") as target:
            for row in reader:
                sample = Sample(
                    timestamp=row["timestamp"],
                    signal_quality=_optional_float(row["signal_quality"]),
                    heart_rate_bpm=_optional_float(row.get("heart_rate_bpm", "")),
                    surface_temp_c=_optional_float(row.get("surface_temp_c", "")),
                    motion_rms_g=_optional_float(row.get("motion_rms_g", "")),
                    check_in=row.get("check_in", "none"),
                )
                target.write(json.dumps(evaluate_sample(sample, quality_floor).to_dict()) + "\n")
                count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Input CSV path")
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL path")
    parser.add_argument(
        "--quality-floor", type=float, default=0.75,
        help="Software-demo quality cutoff in [0,1]; not a medical threshold",
    )
    args = parser.parse_args()
    count = run(args.input, args.output, args.quality_floor)
    print(f"Processed {count} rows into {args.output}. Synthetic/demo output is not medical evidence.")


if __name__ == "__main__":
    main()
