# Results and interpretation

## Baseline reproduction

With the Figure 11 parameter set and `P=1.25`, the simulated excitatory population has a resolved periodic trajectory. The final 500 ms have an E peak-to-peak amplitude of **0.16710**, an I peak-to-peak amplitude of **0.17273**, mean E of **0.15945**, and a peak-interval frequency estimate of **25.02 Hz** (period **39.97 ms**). The paper's Figure 11 reports a limit cycle for this same parameterization and shows an E period of about 40 ms; this run is qualitatively consistent with that plotted example.

## External drive scan

The drive scan used 0.05 increments and a 10,000 ms run at each point. Oscillation was operationally resolved from the last second when E amplitude was at least 0.01.

| P | E mean | E amplitude | Frequency | Classification |
|---:|---:|---:|---:|---|
| 0.80 | 0.01495 | 0.00000 | — | steady state |
| 1.00 | 0.02825 | 0.00000 | — | steady state |
| 1.10 | 0.12165 | 0.16957 | 13.18 Hz | limit cycle |
| 1.25 | 0.15945 | 0.16710 | 25.02 Hz | limit cycle |
| 1.50 | 0.20273 | 0.13470 | 37.65 Hz | limit cycle |
| 1.75 | 0.23536 | 0.07781 | 48.05 Hz | limit cycle |
| 1.85 | 0.24635 | 0.03672 | 51.90 Hz | limit cycle |
| 1.90 | 0.25069 | 0.00023 | — | steady state |
| 2.00 | 0.25717 | < 0.00001 | — | steady state |
| 2.50 | 0.28871 | < 0.00001 | — | steady state |

Across the resolved-cycle portion of this grid, mean E and estimated frequency increase with P while oscillation amplitude declines toward the high-drive steady state. The first resolved cycle is at `P=1.10`; the last is at `P=1.85`. Because the grid is coarse and the classification uses a fixed amplitude threshold, this brackets the behavior for this simulation protocol; it is not a precise bifurcation estimate.

## Coupling scans

At `P=1.25`, the source baseline (`c2=12`, `c3=15`, `c4=3`) yields E amplitude 0.16710.

- **`c2` scan:** the system is steady at `c2=8`; resolved cycles occur for sampled values `c2=10` through `18`. The peak E amplitude is 0.16710 at the baseline `c2=12`, then falls to 0.13014 at `c2=18`.
- **`c3` scan:** the sampled `c3=8`, `10`, and `12` settings are below the 0.01 amplitude threshold; `c3=15` gives the baseline cycle; `c3=18`, `21`, and `24` are also below threshold in the final window.
- **`c4` scan:** E amplitude declines from 0.19508 at `c4=1` to 0.08874 at `c4=4`; sampled values `c4=5` and `6` converge to a steady state by the stated criterion.

These one-factor scans demonstrate parameter sensitivity in this chosen model. They do not identify unique physiological parameters, map the full parameter space, or prove that the model describes real neural recordings.

## Numerical checks

| RK4 step | E amplitude | Period | Frequency | Frequency difference vs 0.05 ms |
|---:|---:|---:|---:|---:|
| 0.20 ms | 0.1670997 | 39.9636 ms | 25.0227 Hz | 0.0076% |
| 0.10 ms | 0.1670998 | 39.9667 ms | 25.0209 Hz | 0.0000% |
| 0.05 ms | 0.1671002 | 39.9667 ms | 25.0209 Hz | reference |

The same 0.1 ms baseline summary was reproduced exactly in a second deterministic run. These checks support numerical consistency for the reported baseline at the tested step sizes; they do not establish model validity.

## Evidence files

- `results/drive_sweep.csv` and `results/coupling_sweeps.csv` contain every scanned point.
- `results/timestep_sensitivity.csv` contains step-size comparison details.
- `results/baseline_timeseries.csv` contains the 1 ms sampled 2-second baseline trajectory.
- `results/run_info.json` records the source, parameters, run windows, Python version, data status, and reproducibility checks.
- `results/checksums.sha256` records SHA-256 hashes for the generated result files; the JSON also records the analysis script hash.
- `results/figures/` contains the baseline time series, phase plane, drive amplitude/frequency, and separate c2, c3, and c4 coupling charts.

