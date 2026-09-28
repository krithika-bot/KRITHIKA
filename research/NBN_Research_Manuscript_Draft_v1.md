# NBN — Research Manuscript Draft v1

**Status:** Conceptual R&D manuscript; not peer-reviewed and not experimentally validated.

## Abstract

The Neuro-Behavior Network (NBN) is a proposed research framework for computational modelling of human state from multimodal physiological and behavioural signals. The framework emphasizes longitudinal analysis, individualized baselines, temporal dynamics, uncertainty estimation and responsible decision support. Candidate modalities include EEG, EMG, cardiovascular, electrodermal and movement signals. The initial research direction is a human-state-aware safety layer for high-risk operators, while the methodology may later be studied in other human-centred applications.

## Research Problem

Human physiological and behavioural signals are noisy, context-dependent and highly individual. Single-sensor or short-window approaches may not adequately represent changing states over time. NBN frames human-state estimation as a multimodal, longitudinal and uncertainty-aware computational problem.

## Research Gap

Relevant literature demonstrates multimodal physiological sensing and computational state estimation, while also identifying challenges involving individual variability, signal quality, missing data and real-world generalization. NBN makes these limitations explicit research variables rather than treating them as implementation details.

## Research Questions

1. Can multimodal physiological and behavioural features provide complementary information for selected human-state variables?
2. Does individualized baseline normalization improve robustness across sessions and participants?
3. Can temporal modelling capture state transitions better than independent-window classification?
4. Can uncertainty estimation and missing-signal handling make model outputs more useful for responsible decision support?

## Proposed Architecture

`Signal acquisition → quality assessment → preprocessing → feature extraction → multimodal fusion → individual baseline → temporal state model → state/risk estimate → uncertainty → decision support → responsible response`

## Experimental Programme

1. Feasibility and signal-quality assessment.
2. Individual-baseline modelling.
3. State modelling using defined experimental protocols.
4. Single-modality versus multimodal comparison.
5. Temporal/state-transition modelling.
6. Robustness tests for artefacts, missing channels and session variation.
7. Prototype research dashboard/decision-support demonstrator.

## Evaluation

Use task-appropriate metrics such as balanced accuracy, precision, recall, F1 and AUROC for classification, and MAE/RMSE for continuous estimation. Evaluate calibration and uncertainty where appropriate. Separate participants across training and testing when measuring generalization to unseen people.

## Safety and Scope

NBN is a research platform, not a diagnostic, treatment or autonomous safety system. Human-state estimates should be treated as probabilistic measurements with uncertainty rather than definitive judgments about a person's mental state, character or fitness. Human-participant studies require appropriate ethics review and informed consent.

## Expected Contribution

The intended contribution is a testable research architecture and methodology for individualized, multimodal and longitudinal human-state modelling. Any claim of improved performance, clinical usefulness or operational safety must be supported by future experiments.

## Future Work

The next step is to select one narrowly measurable state, define an evidence-based protocol, collect ethically approved data, build reproducible preprocessing and modelling pipelines, and evaluate generalization across participants and sessions.
