# Himalayan Soldier Safety & Load Monitor

**Project status:** software demonstrator scaffold; synthetic-data smoke run only. No hardware prototype, soldier/user study, clinical validation, or field trial is claimed.

## What this project currently does

This local Python demo reads a CSV, checks whether a supplied signal-quality value is usable, and records a generic re-check prompt or wearer check-in. It runs offline and stores its output locally. A separate load-cell conversion helper has software checks, but it is not connected to the CSV demo or to a physical load cell. The example CSV is **synthetic**.

The software does not diagnose, predict, prevent, or rule out altitude illness, frostbite, hypothermia, organ injury, memory loss, or mental-health conditions. A single wearable point cannot monitor an entire body. The load module measures/labels load; it does not make a backpack lighter or prove better ergonomics.

## Quick start (Python 3.10+)

From this folder:

```bash
python -m hssm.cli --input data/synthetic_demo.csv --output results/synthetic_demo_output.jsonl
python -m unittest discover -s tests -v
```

The first command writes a reproducible **synthetic software demonstration** to `results/`. Do not present that output as soldier data, clinical accuracy, or proof of field effectiveness.

## Interactive project website

Open [`site/index.html`](site/index.html) for the illustrated project walkthrough, interactive exploded/assembled concept, sensor placement, system architecture, evidence status, prior-art limits, and provisional design envelope. The 3D-style artwork is vector concept art, not a photo of built hardware. Run it locally using the steps in [`site/README.md`](site/README.md).

## Open in Visual Studio Code

Open `himalayan-soldier-safety.code-workspace` in VS Code, or open this folder. Python is standard-library only; no package install is required. VS Code run/debug settings are in `.vscode/`.

## Project contents

- `hssm/monitor.py` — transparent signal-quality and check-in logic; isolated pack-load conversion helper.
- `hssm/cli.py` — offline CSV-to-JSONL runner.
- `data/synthetic_demo.csv` — clearly labelled synthetic demonstration values.
- `tests/` — software behavior checks; these are not health or sensor validation.
- `docs/` — architecture, hardware plan, validation protocol, evidence register, and award narrative draft.
- `evidence/` — empty templates for future real bench evidence. Blank fields must be filled only after the corresponding test is actually run.

## Proposed hardware path (bench prototype first)

See [`docs/hardware_and_system_plan.md`](docs/hardware_and_system_plan.md). Begin with a sensor simulator or bench fixture. Any later human measurements need appropriate consent, supervision, and institutional guidance. No testing on serving personnel is included in this plan.

## Evidence rule

Every project statement must be tagged as one of: **documented source**, **software behavior**, **bench result**, **user feedback**, or **untested hypothesis**. Keep protocol versions, raw logs, dates, and failures. Never invent results or label synthetic data as real.

## Current limitations

- No embedded ESP32 firmware or physical sensor has been connected yet.
- Signal quality is supplied in the CSV; it is not calculated from a real PPG waveform yet.
- HR, surface-temperature proxy, and motion fields are logged as values only; no clinical thresholds or diagnostic interpretation is implemented.
- No machine-learning model is included. ML is not justified until a clearly defined non-clinical prediction task and suitable data exist.
- Cold exposure, battery performance, device comfort, measurement accuracy, and load-cell calibration have not been tested.

