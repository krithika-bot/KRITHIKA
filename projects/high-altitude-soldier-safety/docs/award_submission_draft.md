# Award Submission Draft — Evidence-First Version

**Status:** editable draft only. It is not submission-ready until the actual prototype stage, measurements, applicant eligibility, and current award-cycle rules are verified.

## Project title

Cold- and Motion-Aware Backpack Load-Share Monitor (proposed, not built)

## Problem being investigated

Indian high-altitude load-carriage equipment and soldier-support research already exist. This project investigates a narrower hardware question: can a removable, offline add-on estimate relative shoulder/hip pack-load share, and can it flag when motion, temperature change, drift, or sensor detachment make that estimate unreliable?

This is a research question, not proof that soldiers currently lack monitoring or that this prototype reduces illness or injury.

## Proposed solution

The proposed Phase-1 hardware would use removable force-sensing links at pack support paths, a frame IMU, a hardware-temperature sensor, and an offline quality gate. A valid out-of-range test result would prompt only “re-check pack fit/load”; an invalid reading would be marked uncertain. This is not built. The current Python demonstrator is separate software operating on synthetic signal-quality values, not this hardware system. No injury, disease, or duty-fitness output is proposed.

## What is built and demonstrated

The student reports owning an ESP32/Arduino board, but it is not connected to a load sensor. The current Python demonstration uses synthetic signal-quality inputs and is separate from the proposed pack hardware.

**Fill after the real build only:**

- Hardware revision / date: `[fill after build]`
- Sensor models and locations: `[fill after build]`
- Software version/commit: `[fill after implementation]`
- Demonstration video and unedited build photos: `[add only genuine media]`
- Bench test protocol and raw result files: `[add after tests]`

## Results

**No physical sensor or human test result is available yet.** The current software test uses synthetic CSV examples and checks only code behavior. Add measured results only after tests are run, including failed runs, number of trials, setup, calibration, and limitations.

## Novelty / differentiation

Novelty is not established, and the project currently makes no novelty claim. Prior art includes shoulder/hip load sensing, backpack alerts, motion-aware pack measurement, and quality-gated load estimation. The R&D question is whether a low-cost, removable two-channel retrofit can give repeatable measurements on a defined pack and add useful evidence compared with simple baselines. Do not state “first,” “unique,” or “patented.” See [`novelty_research_gap_v2.md`](novelty_research_gap_v2.md).

## Impact

Potential impact is a hypothesis. No health outcome, injury prevention, cost saving, soldier acceptance, or operational benefit has been measured.

## Risks and limits

- Not a medical device; not validated to diagnose or predict disease.
- A sensor at one body site cannot monitor an entire body.
- Surface temperature cannot identify frostbite or organ damage.
- A load-share display does not reduce pack mass or prove ergonomic benefit.
- The concept has not been evaluated with soldiers or in high-altitude conditions.

