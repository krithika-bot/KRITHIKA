# Software Validation Record

**Run date:** 18 November 2026  
**Environment:** Python 3.12.10; local macOS workspace.  
**Scope:** software behavior only. No hardware, sensor, human, clinical, or field validation.

## Reproduction commands

```bash
python3 -m unittest discover -s tests -v
python3 -m hssm.cli --input data/synthetic_demo.csv --output results/synthetic_demo_output.jsonl
```

## Recorded outcome

- **8/8 unit tests passed** for software-only behavior: quality gate, missing/out-of-range quality, wearer check-in prompt, load conversion, load-limit comparison, and invalid calibration handling.
- The CLI processed **3 synthetic rows** and wrote `results/synthetic_demo_output.jsonl`.
- Low-quality synthetic row produced `SIGNAL_UNRELIABLE`; check-in row produced `CHECK_IN_REQUESTED`; the good-quality row produced `TREND_RECORDED` with an explicit “not an all-clear” message.

## Interpretation and limits

This verifies only that the software behaved as encoded for these test cases. It does **not** show that a physical sensor detects poor-quality data, that any physiological value is accurate, that an alert is medically meaningful, or that the system benefits soldiers. The demonstration values are synthetic and must not be described as project/user measurements.

