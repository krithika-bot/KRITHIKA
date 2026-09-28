# NEURO STORE

## Research Prototype

NEURO STORE is a non-invasive wearable research prototype exploring longitudinal monitoring of neuromuscular activity and movement.

### Research direction

The current concept combines surface EMG and inertial sensing to explore muscle-activity patterns, movement characteristics, within-person baseline variation, signal quality, preprocessing and longitudinal physiological-signal analysis.

### Proposed data pipeline

`Sensor acquisition → signal quality checks → preprocessing → feature extraction → baseline analysis → modelling → evaluation`

### Current status

**Prototype / R&D stage.** The system is not presented as a diagnostic or treatment device, and no clinical performance claims are made.

### Research questions

1. How reliably can wearable EMG and IMU signals be collected during repeated movement tasks?
2. Which signal features are stable enough to support an individual's baseline?
3. How much do movement and electrode placement affect signal quality?
4. Can longitudinal features support computational modelling of changes in neuromuscular behaviour?

### Next experimental steps

- Finalize hardware and acquisition setup.
- Define repeatable movement protocols.
- Collect pilot data with appropriate consent and safety procedures.
- Quantify signal quality and repeatability.
- Build reproducible preprocessing and feature-extraction code.
- Compare simple statistical baselines before applying more complex ML models.

## Related manuscript

See the **NEURO STORE Research Manuscript Draft v1** in the project documentation.

> This repository documents a research prototype. It does not claim diagnosis, treatment, or clinical validation.