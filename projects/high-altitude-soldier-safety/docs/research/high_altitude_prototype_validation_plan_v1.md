# Himalayan Soldier Safety & Load Monitor — Non-Clinical Prototype Validation Plan

**Prepared:** 18 November 2026  
**Status:** Test protocol proposal only. No tests or results are claimed here. This is for an educational engineering prototype, not medical validation or defence field use.

## 1. Scope to validate first

The full concept currently combines two different products: (A) a body-worn signal/trend monitor and (B) a backpack load-measurement module. Validate them separately. A single student can build one clear demonstrator before attempting an integrated system.

### Recommended first demonstrator

**Signal-quality-aware, offline trend logger:** a wearable or fixture-based sensor module records selected signals, labels low-quality readings as “unreliable,” stores data locally, and gives a generic “re-check / consult qualified staff if concerned” prompt. It must not name a disease or say that the wearer is safe.

### Optional second demonstrator

**Pack load measurement:** a load sensor measures total pack mass on a bench/fixture, with a display or local prompt. Measuring mass does not make the pack lighter or prove ergonomic improvement.

## 2. Engineering questions and measurements

| Test | Question | Method (non-clinical) | Record | Example pass criterion to set before testing |
|---|---|---|---|---|
| Sensor logging | Does the device record and timestamp data without gaps during a fixed bench run? | Run at least 10 repeated sessions of a fixed duration using a signal source/simulator where possible; compare expected and recorded sample count. | Expected/received samples, dropped samples, timestamps, resets, battery state. | At least 99% expected samples logged over the defined bench duration; revise if hardware limits differ. |
| Signal-quality gate | Does the system mark deliberately corrupted/disconnected input as unreliable instead of showing a confident value? | Feed valid reference waveforms and controlled bad inputs (disconnect, motion-artifact simulation, low signal) from a simulator or test fixture. Avoid inducing physiological stress in people. | Correct/incorrect quality flags; time to flag; false-quality flags on clean inputs. | Predefine a target such as ≥95% detection of deliberately invalid test segments and report the test set size. This is an engineering criterion, not clinical sensitivity. |
| Offline prompt | Does the prompt work with Bluetooth/network disabled? | Repeat the planned alert conditions with radios/network disabled; inspect local display/log. | Successes, misses, latency, reboot behavior. | All defined test cases produce the expected local event; report number of runs. |
| False prompts | How often does noise create unnecessary prompts in the bench dataset? | Run clean and disturbed inputs with predeclared conditions; keep a fixed event definition. | False prompts per hour, missed scripted events. | Set an engineering target before the test; do not relabel it “medical accuracy.” |
| Cold resilience (device only) | Does the electronics enclosure remain operational after controlled cold exposure? | Test the device/enclosure in a controlled environment following component ratings; warm/inspect safely. Never expose a person to dangerous cold for this test. | Temperature, duration, boot status, battery sag, condensation, sensor faults. | Complete the declared cold cycle with no reset/data loss, or document failure and redesign. Use a calibrated thermometer. |
| Power | Does the prototype run for the claimed duration? | Fully charge, use a fixed sampling/radio/display setting, log current or battery voltage until shutdown, repeat. | Runtime, current profile, environment, battery model, cutoff. | Report median and range over ≥3 runs; do not claim field endurance from room-temperature bench runs. |
| Wearability/weight | What is the device’s actual mass and physical envelope? | Weigh the assembled device; measure dimensions and note attachment locations. | Mass, dimensions, cable/strap locations, snag/comfort observations. | Report measurements; do not say “lightweight” or “comfortable” without a defined comparison/user feedback. |
| Pack scale calibration | How accurately does the load sensor measure known masses? | Calibrate with known masses across the intended range, include zeroing, repeat increasing/decreasing loads. | Reference mass, displayed mass, absolute/percentage error, hysteresis, drift. | Example target: absolute error ≤ the project-defined tolerance across the declared range; state that tolerance before testing. |
| Pack repeated-load stability | Does the reading stay stable with shifting placement? | Repeat at center and several realistic positions on a stationary pack fixture. | Position, reading, spread, settling time. | Report the distribution; do not generalize to dynamic hiking load until separately tested. |
| Software reproducibility | Can another person reproduce the displayed result from the saved data? | Freeze a code version, run documented steps on a clean environment, compare output to stored expected values. | Commit/version, dependencies, input hash, output, errors. | Same input produces the same rule-based output; if stochastic ML is used, record seeds and variance. |

These are candidate thresholds, not standards. Adjust them to the selected hardware and state the reason before testing. Do not tune criteria after seeing results without clearly labeling the revised protocol.

## 3. Data and AI policy for this prototype

- Start with rule-based quality checks and transparent trend displays. AI is not required to make the prototype technically meaningful.
- Do not train or advertise a model to predict HAPE, HACE, frostbite, hypothermia, organ damage, memory loss, or mental illness without suitable labeled data, clinical supervision, ethics review, and prospective validation.
- Public datasets may not represent cold-exposed Indian soldiers. Record dataset source, license, population, sensor type, labels, missingness, and known domain mismatch.
- Keep participant data out of cloud services by default. Use synthetic signals or simulators for development; if any human data are later involved, obtain appropriate consent and institutional/ethics guidance first.
- Do not collect GPS, unit identity, border location, deployment schedules, tactical movement, or classified/operational information.
- Separate training, validation, and test data by person/session where applicable. Do not put windows from the same recording into both train and test sets; that can inflate performance.

## 4. Safety boundaries

- Do not use this prototype to decide whether someone is fit for duty, safe at altitude, or needs/does not need treatment.
- Do not use a device alert instead of reporting symptoms to qualified medical staff or following official procedures.
- Do not run cold-exposure, hypoxia, breath-holding, exertion, sleep deprivation, or medication experiments on yourself or anyone else.
- Do not test on serving soldiers without formal permission, supervision, and the required ethics/defence approvals. Early evidence can be built on a bench.
- No skin injury/frostbite claims can be made from a surface temperature sensor; local temperature is not tissue diagnosis.

## 5. Minimum result table for an award/demo file

| Metric | Protocol version | Number of runs | Result (fill only after testing) | Failure cases / limitations |
|---|---|---:|---|---|
| Logging completeness |  |  |  |  |
| Invalid-input flag rate on scripted test cases |  |  |  |  |
| False prompts per hour on clean bench input |  |  |  |  |
| Offline prompt success and latency |  |  |  |  |
| Runtime at stated settings |  |  |  |  |
| Device mass and dimensions |  |  |  |  |
| Pack-load measurement error across range |  |  |  |  |
| Cold-device test outcome (device only) |  |  |  |  |

Store raw logs, protocol, calibration details, and device photos together. Keep unsuccessful trials and report them; do not replace raw evidence with a polished video.

