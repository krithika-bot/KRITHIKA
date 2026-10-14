# Wilson–Cowan Neural Mass Model

A small, reproducible simulation of interacting excitatory and inhibitory neural populations. This project implements the time-coarse-grained Wilson–Cowan equations, reproduces the oscillatory baseline described in Figure 11 of the 1972 paper, and explores how external drive and selected coupling coefficients change the simulated dynamics.

> **Research status:** the deterministic software simulation and parameter study are complete. This is a mathematical model demonstration. It uses no EEG or human data and does not establish biological validity, clinical utility, or a model of any individual brain.

## Project question

How do external excitatory drive and selected excitatory/inhibitory coupling coefficients change activity amplitude, oscillation frequency, and the presence of a resolved limit cycle in the two-population Wilson–Cowan model?

## Model and source

The implementation follows the time-coarse-grained equations in Eq. 12 of Wilson and Cowan (1972):

```text
τE dE/dt = -E + (kE - rE·E) SE(c1·E - c2·I + P)
τI dI/dt = -I + (kI - rI·I) SI(c3·E - c4·I + Q)
```

The response functions are shifted logistic curves, `S(x) = sigmoid(a·(x − θ)) − sigmoid(−a·θ)`, so `S(0) = 0`; `k` is the maximum of the corresponding shifted response. The variables `E` and `I` are dimensionless excitatory and inhibitory population activities. Time is measured in milliseconds.

The baseline uses Figure 11's parameter set: `c1=16`, `c2=12`, `c3=15`, `c4=3`, `aE=1.3`, `θE=4`, `aI=2`, `θI=3.7`, `rE=rI=1`, `τE=τI=8 ms`, `P=1.25`, and `Q=0`.

**Primary source:** Wilson, H. R., & Cowan, J. D. (1972). Excitatory and inhibitory interactions in localized populations of model neurons. *Biophysical Journal, 12*(1), 1–24. [doi:10.1016/S0006-3495(72)86068-5](https://doi.org/10.1016/S0006-3495(72)86068-5) · [Paper PDF](https://isn.ucsd.edu/courses/beng260/reading/Wilson_Cowan_1972.pdf)

## Reproduce

Python 3.10 or newer is sufficient; the implementation uses the Python standard library only.

```bash
python3 scripts/run_analysis.py
```

To write outputs elsewhere:

```bash
python3 scripts/run_analysis.py --out /path/to/output-directory
```

The run produces CSV tables, a JSON provenance/configuration record, and standalone SVG figures under `results/`. All simulations are deterministic from the declared initial state; there is no random seed and no external dataset.

## Evidence package

- [Complete project documentation](PROJECT_DOCUMENTATION.md)
- [Methods and implementation decisions](docs/METHODS.md)
- [Results and interpretation](docs/RESULTS.md)
- [Baseline E/I time series](results/baseline_timeseries.csv)
- [External drive sweep](results/drive_sweep.csv)
- [Coupling sensitivity sweep](results/coupling_sweeps.csv)
- [Timestep sensitivity](results/timestep_sensitivity.csv)
- [Run configuration and provenance](results/run_info.json)
- [SHA-256 checksums for generated outputs](results/checksums.sha256)
- Figures: [baseline time series](results/figures/baseline_timeseries.svg), [phase plane](results/figures/baseline_phase_plane.svg), [drive amplitude](results/figures/drive_amplitude.svg), [drive frequency](results/figures/drive_frequency.svg), and separate [c2](results/figures/coupling_c2.svg), [c3](results/figures/coupling_c3.svg), and [c4](results/figures/coupling_c4.svg) sweeps

## Software and tools

- Python 3.10+ standard library: `dataclasses`, `math`, `csv`, `json`, `argparse`, and `pathlib`
- Classical fourth-order Runge–Kutta (RK4) numerical integration
- CSV for numerical outputs and SVG for dependency-free, inspectable figures
- Git for version control

NumPy, SciPy, Matplotlib, Jupyter, EEG hardware, and an external dataset are not required for this implementation.

## Scope and limitations

- This is a two-variable, spatially local, time-coarse-grained model; it does not represent a whole brain or an individual participant.
- Parameters are the source paper's illustrative Figure 11 settings, not fit to measurements in this project.
- Sweeps vary one parameter at a time and do not establish a complete bifurcation diagram or parameter identifiability.
- Oscillation status is operationally classified from the last 1,000 ms using a declared `E` peak-to-peak threshold of 0.01. The drive grid uses 0.05 increments, so transition values are only bracketed at that resolution.
- Timestep sensitivity is a numerical check for this baseline, not proof of biological accuracy.
- No EEG, animal, human, clinical, or patient data were used. Simulated dynamics are not experimental evidence or a clinical result.

