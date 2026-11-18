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

**Fill after the real build only:**

- Hardware revision / date: `[fill after build]`
- Sensor models and locations: `[fill after build]`
- Software version/commit: `[fill after implementation]`
- Demonstration video and unedited build photos: `[add only genuine media]`
- Bench test protocol and raw result files: `[add after tests]`

## Results

**No physical sensor or human test result is available yet.** The current software test uses synthetic CSV examples and checks only code behavior. Add measured results only after tests are run, including failed runs, number of trials, setup, calibration, and limitations.

## Novelty / differentiation

Novelty is not established. Prior art expressly includes shoulder/hip load-balance sensing and feedback, as well as Indian load-carriage and soldier-support technologies. The current hypothesis is a removable, low-mass implementation whose relative load-share output is withheld when its sensors are unreliable under controlled movement and temperature changes. A claim-by-claim prior-art review and comparative bench results are required. Do not state “first,” “unique,” or “patented.” See [`novelty_research_gap_v2.md`](novelty_research_gap_v2.md).

## Impact

Potential impact is a hypothesis. No health outcome, injury prevention, cost saving, soldier acceptance, or operational benefit has been measured.

## Risks and limits

- Not a medical device; not validated to diagnose or predict disease.
- A sensor at one body site cannot monitor an entire body.
- Surface temperature cannot identify frostbite or organ damage.
- A load-share display does not reduce pack mass or prove ergonomic benefit.
- The concept has not been evaluated with soldiers or in high-altitude conditions.

